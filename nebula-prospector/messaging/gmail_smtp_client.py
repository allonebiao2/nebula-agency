"""Backend SMTP Gmail — alternative à Resend en attendant validation domaine.

Utilise les credentials IMAP_USER + IMAP_PASSWORD (App Password Gmail)
pour envoyer via smtp.gmail.com:465 (SSL). Limites Gmail :
- ~100 emails/jour (compte standard)
- ~500 emails/jour (compte payant Workspace)

Avantage : pas besoin de validation domaine. L'expéditeur est l'email
Gmail réel (allonebiao2@gmail.com), donc super crédible.
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from config import settings
from core.tool_calls import tool_call

log = logging.getLogger(__name__)


@tool_call("gmail.send", per_hour=20, per_day=100, raise_on_limit=False)
def send_email_gmail(
    to: str,
    subject: str,
    body_text: str,
    *,
    reply_to: str | None = None,
    body_html: str | None = None,
    from_name: str = "Mongazi · NEBULA Agency",
) -> dict[str, Any]:
    """Envoie un email via Gmail SMTP. Retourne {ok, id, error}."""
    if not (settings.imap_user and settings.imap_password):
        return {"ok": False, "id": None, "error": "IMAP_USER ou IMAP_PASSWORD manquant"}

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{settings.imap_user}>"
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to or settings.email_reply_to:
        msg["Reply-To"] = reply_to or settings.email_reply_to
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as srv:
            srv.login(settings.imap_user, settings.imap_password)
            srv.send_message(msg)
        return {"ok": True, "id": f"gmail-{to[:20]}", "error": None}
    except smtplib.SMTPAuthenticationError as e:
        log.error(f"Gmail SMTP auth failed: {e}")
        return {"ok": False, "id": None, "error": f"AUTH FAILED: {str(e)[:200]}"}
    except Exception as e:
        log.exception(f"Gmail SMTP send failed: {e}")
        return {"ok": False, "id": None, "error": str(e)[:200]}
