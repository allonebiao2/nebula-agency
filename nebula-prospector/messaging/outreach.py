"""Orchestration du cold outreach : prospects HOT → email perso → envoi.

Pipeline :
1. Sélectionne les prospects tier='hot', status='enriched', avec email valide
2. Pour chaque prospect, dans la limite du quota journalier :
   - Récupère contenu site (pour personnaliser)
   - Génère l'email via Claude (templates.py)
   - Respecte safety (cooldown, rate-limit, blacklist)
   - Envoie via Resend
   - Log la conversation outbound dans Supabase
   - Met à jour le prospect (status='contacted', last_contacted_at)
   - Émet un event dashboard
   - Ping Telegram si succès
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from db.client import get_db
from messaging.resend_client import send_email
from messaging.safety import (
    can_contact_prospect,
    is_blacklisted,
    remaining_quota_today,
    wait_between_sends,
)
from messaging.templates import generate_cold_email

log = logging.getLogger(__name__)


def _get_site_content(website: str | None) -> str:
    if not website:
        return ""
    try:
        from enrichment.website_scraper import get_site_summary
        return get_site_summary(website, max_chars=2000)
    except Exception as e:
        log.debug(f"site summary failed: {e}")
        return ""


def _log_conversation(
    prospect_id: str,
    subject: str,
    body: str,
    provider_id: str | None,
    sent_ok: bool,
) -> None:
    """Insère la conversation outbound dans Supabase."""
    db = get_db()
    payload = {
        "prospect_id": prospect_id,
        "direction": "out",
        "channel": "email",
        "subject": subject,
        "body": body,
        "provider_id": provider_id,
        "sent_at": datetime.now(timezone.utc).isoformat() if sent_ok else None,
    }
    try:
        db.table("conversations").insert(payload).execute()
    except Exception as e:
        log.warning(f"failed to log conversation: {e}")


def _mark_contacted(prospect_id: str) -> None:
    db = get_db()
    db.table("prospects").update({
        "status": "contacted",
        "last_contacted_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", prospect_id).execute()


def _select_prospects_for_outreach(limit: int, tiers: list[str] | None = None) -> list[dict[str, Any]]:
    """Sélectionne les prospects à contacter : tier dans (hot, warm par défaut), status=enriched,
    email présent. Tri par score décroissant.
    """
    if tiers is None:
        tiers = ["hot", "warm"]
    db = get_db()
    r = (
        db.table("prospects")
        .select("*")
        .in_("tier", tiers)
        .eq("status", "enriched")
        .not_.is_("email", "null")
        .order("score", desc=True)
        .limit(limit * 2)  # marge pour les prospects en cooldown
        .execute()
    )
    return r.data or []


def run_outreach(max_send: int | None = None, tiers: list[str] | None = None) -> dict[str, int]:
    """Lance un cycle d'outreach. Retourne stats.

    Args:
        max_send: override le quota (sinon = remaining_quota_today())
        tiers: liste de tiers ciblés (default ['hot', 'warm']). Permet de cibler
               aussi les cold si on veut. Trié par score décroissant donc les
               meilleurs warm passent avant des cold moyens.
    """
    quota = max_send if max_send is not None else remaining_quota_today()
    if quota <= 0:
        log.info("outreach: quota journalier épuisé")
        return {"sent": 0, "skipped": 0, "errors": 0, "quota": 0}

    candidates = _select_prospects_for_outreach(quota, tiers=tiers)
    if not candidates:
        log.info(f"outreach: aucun prospect prêt (tiers={tiers or ['hot','warm']})")
        return {"sent": 0, "skipped": 0, "errors": 0, "quota": quota}

    sent = 0
    skipped = 0
    errors = 0

    for p in candidates:
        if sent >= quota:
            break

        pid = p["id"]
        email = p.get("email")
        if not email:
            skipped += 1
            continue

        if is_blacklisted(pid):
            log.info(f"outreach: skip {p.get('name')} (blacklisted)")
            skipped += 1
            continue

        allowed, reason = can_contact_prospect(pid)
        if not allowed:
            log.info(f"outreach: skip {p.get('name')} ({reason})")
            skipped += 1
            continue

        # 1. Générer l'email
        site_content = _get_site_content(p.get("website"))
        gen = generate_cold_email(p, site_content)
        if gen.get("error"):
            log.warning(f"outreach: generation failed for {p.get('name')}: {gen['error']}")
            errors += 1
            continue

        # 2. Envoyer via Resend (avec rate-limit entre envois)
        wait_between_sends()
        result = send_email(
            to=email,
            subject=gen["subject"],
            body_text=gen["body"],
        )

        # 3. Log conversation
        _log_conversation(
            prospect_id=pid,
            subject=gen["subject"],
            body=gen["body"],
            provider_id=result.get("id"),
            sent_ok=result["ok"],
        )

        if result["ok"]:
            sent += 1
            _mark_contacted(pid)
            # Event dashboard
            try:
                from core.events import emit_thought
                emit_thought(
                    f"Email envoyé : {p.get('name')}",
                    description=f"Service: {gen.get('service')} · Objet: {gen.get('subject', '')[:60]}",
                )
            except Exception:
                pass
        else:
            errors += 1
            log.warning(f"outreach: send failed for {p.get('name')}: {result.get('error')}")

    return {"sent": sent, "skipped": skipped, "errors": errors, "quota": quota}
