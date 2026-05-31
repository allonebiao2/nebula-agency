"""Classifier d'intent — Claude lit une réponse prospect et décide quoi faire.

5 intents possibles :
- ready_to_pay : "OK je prends", "envoie-moi le devis", "je veux acheter" → notify Mongazi IMMÉDIAT
- interested  : "ça m'intéresse mais...", questions concrètes → générer une réponse Claude
- question    : juste une question d'info → générer une réponse courte
- not_interested : "pas intéressé", "trop cher", "pas le moment" → archiver
- unsubscribe : "ne plus me contacter", "STOP" → blacklist immédiat

Conséquences automatiques selon intent.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from config import settings
from core.tool_calls import tool_call
from db.client import get_db

log = logging.getLogger(__name__)


VALID_INTENTS = {"ready_to_pay", "interested", "question", "not_interested", "unsubscribe"}

CLASSIFIER_PROMPT = """Tu es NOVA, agent commercial de NEBULA Agency. Tu reçois la réponse email d'un prospect que tu avais contacté avec un cold email pour lui vendre une vitrine digitale / catalogue / fiche Google Maps.

Voici le prospect :
- Nom : {name}
- Secteur : {sector}
- Ville : {city}
- Score : {score}/10 · Tier : {tier}
- Service que NOVA avait pitché : {recommended_service}

Voici sa réponse (extrait) :
---
Sujet : {subject}

{body}
---

Classe l'intent du prospect en UNE seule catégorie :

- **ready_to_pay** — il veut acheter MAINTENANT (mots clés : "je prends", "j'achète", "envoie devis", "comment payer", "OK je signe", "validé")
- **interested** — intéressé mais a besoin de plus d'info / questions / hésitations à lever (mots : "ça m'intéresse mais...", "combien si...", "vous faites aussi...", "j'aimerais voir")
- **question** — juste une question simple sans engagement (mots : "est-ce que...", "comment ça marche", "qui êtes-vous")
- **not_interested** — pas la bonne période, trop cher, pas adapté (mots : "merci mais non", "pas en ce moment", "trop cher", "pas mon besoin")
- **unsubscribe** — demande à ne plus être contacté (mots : "STOP", "ne plus me contacter", "désabonnement", "retirez-moi")

**Détecte aussi le sentiment** : positive | neutral | negative

**Et un résumé** : 1 phrase max qui capture l'essentiel de la réponse.

**Réponds en JSON STRICT** (pas de markdown, pas de texte avant/après) :
{{
  "intent": "ready_to_pay|interested|question|not_interested|unsubscribe",
  "sentiment": "positive|neutral|negative",
  "summary": "Une phrase qui résume la réponse"
}}"""


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1] if "```" in t[3:] else t[3:]
        if t.lower().startswith("json"):
            t = t[4:]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


@tool_call("claude.classify_intent", per_hour=60, per_day=500, raise_on_limit=False)
def _classify_with_claude(body: str, subject: str, prospect: dict[str, Any]) -> dict[str, Any]:
    """Demande à Claude de classifier."""
    if not settings.anthropic_api_key:
        return {"intent": "interested", "sentiment": "neutral",
                "summary": "(API key missing, fallback)"}

    client = Anthropic(api_key=settings.anthropic_api_key)
    prompt = CLASSIFIER_PROMPT.format(
        name=prospect.get("name", "?"),
        sector=prospect.get("sector", "?"),
        city=prospect.get("city", "?"),
        score=prospect.get("score", 0),
        tier=prospect.get("tier", "?"),
        recommended_service=prospect.get("recommended_service", "?"),
        subject=subject[:200],
        body=body[:2000],
    )

    try:
        resp = client.messages.create(
            model=settings.claude_model_fast,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text if resp.content else ""
        cleaned = _strip_code_fence(raw)
        data = json.loads(cleaned)
        intent = data.get("intent", "interested")
        if intent not in VALID_INTENTS:
            intent = "interested"
        sentiment = data.get("sentiment", "neutral")
        if sentiment not in {"positive", "neutral", "negative"}:
            sentiment = "neutral"
        return {
            "intent": intent,
            "sentiment": sentiment,
            "summary": (data.get("summary") or "")[:300],
        }
    except Exception as e:
        log.exception(f"Classify failed: {e}")
        return {"intent": "interested", "sentiment": "neutral",
                "summary": f"(classify error: {str(e)[:100]})"}


def classify_reply(
    *,
    prospect_id: str,
    conversation_id: str | None,
    body: str,
    subject: str,
    prospect: dict[str, Any],
) -> dict[str, Any]:
    """Classifie une réponse + déclenche les actions automatiques selon l'intent."""
    result = _classify_with_claude(body, subject, prospect)
    intent = result["intent"]
    sentiment = result["sentiment"]
    summary = result["summary"]

    # 1. Update la conversation avec l'intent détecté
    db = get_db()
    if conversation_id:
        try:
            db.table("conversations").update({
                "detected_intent": intent,
                "sentiment": sentiment,
                "summary": summary,
            }).eq("id", conversation_id).execute()
        except Exception as e:
            log.warning(f"conversation update failed: {e}")

    # 2. Actions automatiques selon intent
    if intent == "unsubscribe":
        # Blacklist immédiat
        try:
            db.table("prospects").update({
                "status": "unsubscribed",
                "status_reason": "désabonnement demandé via réponse email",
            }).eq("id", prospect_id).execute()
        except Exception as e:
            log.warning(f"unsubscribe failed: {e}")

    elif intent == "ready_to_pay":
        # Notif Telegram immédiate
        try:
            from alerts.telegram_bot import send_message, _esc
            text = (
                f"👑 <b>PROSPECT PRÊT À PAYER</b>\n\n"
                f"<b>{_esc(prospect.get('name', '?'))}</b>\n"
                f"{_esc(prospect.get('sector', '?'))} · {_esc(prospect.get('city', '?'))}\n"
                f"📧 {_esc(prospect.get('email', '?'))}\n"
                f"📱 {_esc(prospect.get('phone') or '—')}\n\n"
                f"💬 Sentiment: <b>{_esc(sentiment)}</b>\n"
                f"📝 {_esc(summary)}\n\n"
                f"🎯 Service à pitcher : <code>{_esc(prospect.get('recommended_service') or '—')}</code>\n\n"
                f"<i>Réponds-lui sur WhatsApp +229 96 74 07 32 ou par email directement.</i>"
            )
            send_message(text)
        except Exception as e:
            log.warning(f"ready_to_pay notify failed: {e}")
        # Update status
        try:
            db.table("prospects").update({
                "status": "ready_to_pay",
                "status_reason": f"intent ready_to_pay détecté: {summary[:200]}",
            }).eq("id", prospect_id).execute()
        except Exception as e:
            log.warning(f"status update failed: {e}")

    elif intent == "not_interested":
        # Archiver
        try:
            db.table("prospects").update({
                "status": "lost",
                "status_reason": f"not_interested: {summary[:200]}",
            }).eq("id", prospect_id).execute()
        except Exception as e:
            log.warning(f"not_interested failed: {e}")

    elif intent in ("interested", "question"):
        # Le prospect attend une réponse — on update son statut et on notifie Mongazi
        # (la réponse auto via Claude pourra être ajoutée plus tard)
        try:
            db.table("prospects").update({
                "status": "replied",
                "status_reason": f"intent {intent}: {summary[:200]}",
            }).eq("id", prospect_id).execute()
        except Exception as e:
            log.warning(f"replied update failed: {e}")

        # Notif Telegram pour Mongazi
        try:
            from alerts.telegram_bot import send_message, _esc
            text = (
                f"💬 <b>Réponse prospect</b> ({_esc(intent)}, {_esc(sentiment)})\n\n"
                f"<b>{_esc(prospect.get('name', '?'))}</b> · "
                f"{_esc(prospect.get('city', '?'))}\n"
                f"📧 {_esc(prospect.get('email', '?'))}\n\n"
                f"📝 {_esc(summary)}\n\n"
                f"<i>Réponds depuis Gmail ou demande-moi de générer une réponse.</i>"
            )
            send_message(text, silent=True)
        except Exception as e:
            log.warning(f"reply notify failed: {e}")

    # Event dashboard
    try:
        from core.events import emit_thought
        emit_thought(
            f"Réponse {prospect.get('name', '?')} → {intent}",
            description=summary,
        )
    except Exception:
        pass

    return {
        "intent": intent,
        "sentiment": sentiment,
        "summary": summary,
    }
