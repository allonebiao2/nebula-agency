"""Wrapper Resend pour l'envoi d'emails."""
from __future__ import annotations

import logging
from typing import Any

import resend

from config import settings

log = logging.getLogger(__name__)


def _ensure_configured() -> bool:
    if not settings.resend_api_key:
        log.warning("RESEND_API_KEY manquante, envoi ignoré")
        return False
    resend.api_key = settings.resend_api_key
    return True


def _default_from() -> str:
    """Adresse expéditeur par défaut.

    En l'absence de domaine perso validé, Resend permet d'envoyer depuis
    `onboarding@resend.dev` (sandbox) — mais uniquement vers les emails
    vérifiés sur le compte. En production, mieux vaut valider un domaine
    perso et utiliser ${EMAIL_FROM_ADDRESS}.
    """
    addr = settings.email_from_address or "onboarding@resend.dev"
    name = settings.email_from_name or "Mongazi · NEBULA Agency"
    return f"{name} <{addr}>"


def send_email(
    to: str,
    subject: str,
    body_text: str,
    *,
    reply_to: str | None = None,
    body_html: str | None = None,
) -> dict[str, Any]:
    """Envoie un email via Resend. Retourne {"ok": bool, "id": str | None, "error": str | None}."""
    if not _ensure_configured():
        return {"ok": False, "id": None, "error": "RESEND_API_KEY missing"}

    payload: dict[str, Any] = {
        "from": _default_from(),
        "to": [to],
        "subject": subject,
        "text": body_text,
    }
    if body_html:
        payload["html"] = body_html
    if reply_to or settings.email_reply_to:
        payload["reply_to"] = reply_to or settings.email_reply_to

    try:
        resp = resend.Emails.send(payload)
        msg_id = resp.get("id") if isinstance(resp, dict) else getattr(resp, "id", None)
        return {"ok": True, "id": msg_id, "error": None}
    except Exception as e:
        log.exception(f"Resend send failed for {to}: {e}")
        return {"ok": False, "id": None, "error": str(e)}
