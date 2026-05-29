"""Émetteur d'événements pour le flux de conscience de NOVA.

Chaque action significative de NOVA émet un event dans la table agent_events.
Le dashboard s'abonne à cette table via Supabase Realtime et affiche les
events en direct, avec animations.

Usage:
    from core.events import emit_thought, emit_action, emit_discovery, set_state

    set_state(status="sourcing", current_activity="Je scanne Cotonou...")
    emit_thought("Je vais chercher les salons de beauté sans site web.")
    emit_discovery("Salon Élégance", prospect_id=uuid, city="Cotonou")
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from db.client import get_db

logger = logging.getLogger(__name__)

AGENT_STATE_ID = "00000000-0000-0000-0000-000000000001"


# ---------------------------------------------------------------------------
# Emit events
# ---------------------------------------------------------------------------
def _emit(
    event_type: str,
    title: str,
    *,
    description: str | None = None,
    emoji: str = "✨",
    severity: str = "info",
    prospect_id: str | UUID | None = None,
    conversation_id: str | UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload = {
        "event_type": event_type,
        "title": title[:200],
        "description": description,
        "emoji": emoji,
        "severity": severity,
        "prospect_id": str(prospect_id) if prospect_id else None,
        "conversation_id": str(conversation_id) if conversation_id else None,
        "metadata": metadata or {},
    }
    try:
        get_db().table("agent_events").insert(payload).execute()
    except Exception as e:
        # Un fail d'event ne doit JAMAIS faire planter l'agent
        logger.warning("emit event failed (%s): %s", event_type, e)


def emit_thought(title: str, description: str | None = None) -> None:
    """Pensée interne de NOVA (réflexion, décision)."""
    _emit("thought", title, description=description, emoji="💭")


def emit_action(title: str, description: str | None = None, target: str | None = None) -> None:
    """Action en cours (sourcing, scraping, etc.)."""
    _emit("action", title, description=description, emoji="⚙️",
          metadata={"target": target} if target else None)


def emit_discovery(
    name: str,
    *,
    prospect_id: str | UUID | None = None,
    city: str | None = None,
    sector: str | None = None,
    no_website: bool = False,
) -> None:
    """Nouveau prospect découvert."""
    extras: list[str] = []
    if city: extras.append(city)
    if sector: extras.append(sector)
    if no_website: extras.append("⚠️ pas de site")
    desc = " · ".join(extras) if extras else None
    _emit("discovery", f"Nouveau prospect : {name}",
          description=desc, emoji="🔭", severity="success",
          prospect_id=prospect_id,
          metadata={"city": city, "sector": sector, "no_website": no_website})


def emit_enrichment(prospect_name: str, what: str, *, prospect_id: str | UUID | None = None) -> None:
    """Un prospect a été enrichi (email trouvé, scoring, etc.)."""
    _emit("enrichment", f"{prospect_name} · {what}", emoji="🧬",
          prospect_id=prospect_id)


def emit_email_sent(prospect_name: str, subject: str,
                    *, prospect_id: str | UUID | None = None,
                    conversation_id: str | UUID | None = None) -> None:
    _emit("email_sent", f"Email envoyé à {prospect_name}",
          description=f"Objet : {subject}", emoji="✉️",
          prospect_id=prospect_id, conversation_id=conversation_id)


def emit_reply_received(prospect_name: str, summary: str,
                        *, prospect_id: str | UUID | None = None,
                        conversation_id: str | UUID | None = None) -> None:
    _emit("reply_received", f"{prospect_name} a répondu",
          description=summary, emoji="📩", severity="success",
          prospect_id=prospect_id, conversation_id=conversation_id)


def emit_intent_detected(prospect_name: str, intent: str,
                         *, prospect_id: str | UUID | None = None) -> None:
    severity = "celebration" if intent == "ready_to_pay" else "info"
    emoji = "👑" if intent == "ready_to_pay" else "🎯"
    _emit("intent_detected", f"{prospect_name} · intent : {intent}",
          emoji=emoji, severity=severity, prospect_id=prospect_id)


def emit_alert_sent(target: str, channel: str = "telegram") -> None:
    _emit("alert_sent", f"Alerte envoyée à Mongazi : {target}",
          description=f"Canal : {channel}", emoji="🚨", severity="celebration")


def emit_error(title: str, description: str | None = None) -> None:
    _emit("error", title, description=description, emoji="⚠️", severity="error")


def emit_learning(title: str, description: str | None = None) -> None:
    """Auto-amélioration : nouveau prompt généré."""
    _emit("learning", title, description=description, emoji="🧠", severity="success")


# ---------------------------------------------------------------------------
# State management (singleton)
# ---------------------------------------------------------------------------
def set_state(
    *,
    status: str | None = None,
    mood: str | None = None,
    current_activity: str | None = None,
    current_target: str | None = None,
    bump_heartbeat: bool = True,
    **counters: int,
) -> None:
    """Met à jour l'état courant de NOVA.

    counters: prospects_found_today / emails_sent_today / replies_today /
              alerts_sent_today  → incrémentés si fournis
    """
    db = get_db()
    update: dict[str, Any] = {}
    if status:           update["status"] = status
    if mood:             update["mood"] = mood
    if current_activity: update["current_activity"] = current_activity
    if current_target is not None: update["current_target"] = current_target
    if bump_heartbeat:   update["last_heartbeat"] = "now()"

    if update:
        try:
            db.table("agent_state").update(update).eq("id", AGENT_STATE_ID).execute()
        except Exception as e:
            logger.warning("set_state failed : %s", e)

    # Compteurs : on lit puis on incrémente (atomic via RPC serait mieux mais ok pour l'instant)
    if counters:
        try:
            current = (db.table("agent_state").select("*")
                       .eq("id", AGENT_STATE_ID).single().execute().data)
            patch = {k: (current.get(k, 0) or 0) + v for k, v in counters.items()}
            db.table("agent_state").update(patch).eq("id", AGENT_STATE_ID).execute()
        except Exception as e:
            logger.warning("counters update failed : %s", e)


def heartbeat() -> None:
    """À appeler régulièrement pour signaler que NOVA est vivante."""
    set_state(bump_heartbeat=True)


def reset_daily_counters() -> None:
    db = get_db()
    db.table("agent_state").update({
        "prospects_found_today": 0,
        "emails_sent_today": 0,
        "replies_today": 0,
        "alerts_sent_today": 0,
    }).eq("id", AGENT_STATE_ID).execute()
