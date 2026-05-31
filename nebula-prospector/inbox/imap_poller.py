"""IMAP poller — récupère les nouvelles réponses des prospects.

Connexion IMAP générique (Gmail, Outlook, OVH, etc.). Pour Gmail il faut
un App Password (https://myaccount.google.com/apppasswords).

Stratégie :
1. Connecte au serveur IMAP (TLS)
2. Cherche les emails UNSEEN dans INBOX
3. Pour chaque mail :
   - Extrait headers + body texte
   - Essaie de matcher avec un prospect par email expéditeur
   - Si match : insère dans `conversations` (direction='in') et lance classifier intent
   - Marque le mail comme SEEN
4. Best-effort : si IMAP indisponible, log mais ne crashe pas
"""
from __future__ import annotations

import email
import imaplib
import logging
import re
from email.header import decode_header
from email.message import Message
from typing import Any

from config import settings
from db.client import get_db

log = logging.getLogger(__name__)


def _decode_str(s: str | bytes | None) -> str:
    """Décode un header email (RFC 2047)."""
    if s is None:
        return ""
    if isinstance(s, bytes):
        try:
            return s.decode("utf-8", errors="replace")
        except Exception:
            return s.decode("latin-1", errors="replace")
    parts = decode_header(s)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="replace"))
            except Exception:
                out.append(part.decode("latin-1", errors="replace"))
        else:
            out.append(part)
    return "".join(out)


def _extract_text_body(msg: Message) -> str:
    """Extrait le corps text/plain (fallback text/html nettoyé)."""
    if msg.is_multipart():
        # Cherche text/plain d'abord
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    continue
        # Fallback HTML
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    html = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                    # Strip HTML tags
                    return re.sub(r"<[^>]+>", " ", html)
                except Exception:
                    continue
    else:
        try:
            return msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="replace"
            )
        except Exception:
            return str(msg.get_payload())
    return ""


def _extract_from_email(from_header: str) -> str:
    """Extrait juste l'email depuis 'Nom <email@x.com>'."""
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1).strip().lower()
    return from_header.strip().lower()


def _find_prospect_by_email(email_addr: str) -> dict[str, Any] | None:
    """Cherche un prospect ayant cet email."""
    db = get_db()
    r = (
        db.table("prospects")
        .select("*")
        .eq("email", email_addr)
        .limit(1)
        .execute()
    )
    return (r.data or [None])[0]


def _store_inbound_conversation(
    prospect_id: str,
    *,
    subject: str,
    body: str,
    message_id: str | None,
    in_reply_to: str | None,
    from_addr: str,
) -> dict[str, Any]:
    """Insère une conversation inbound dans Supabase."""
    db = get_db()
    payload = {
        "prospect_id": prospect_id,
        "direction": "in",
        "channel": "email",
        "subject": subject[:300],
        "body": body[:10000],  # cap
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "provider_id": from_addr,
    }
    r = db.table("conversations").insert(payload).execute()
    return (r.data or [{}])[0]


def poll_inbox(max_messages: int = 30) -> dict[str, int]:
    """Poll l'IMAP inbox une fois. Retourne stats.

    Variables d'env requises :
      IMAP_HOST  (ex: imap.gmail.com)
      IMAP_PORT  (default 993)
      IMAP_USER  (email complet)
      IMAP_PASSWORD  (App Password pour Gmail)
    """
    if not (settings.imap_host and settings.imap_user and settings.imap_password):
        return {"connected": 0, "fetched": 0, "matched": 0, "stored": 0,
                "error": "IMAP not configured"}

    stats = {"connected": 0, "fetched": 0, "matched": 0, "stored": 0, "error": None}

    try:
        mail = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port or 993)
        mail.login(settings.imap_user, settings.imap_password)
        stats["connected"] = 1
    except Exception as e:
        log.exception(f"IMAP connect failed: {e}")
        stats["error"] = f"connect: {str(e)[:200]}"
        return stats

    try:
        mail.select("INBOX")
        # UNSEEN messages
        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            stats["error"] = f"search failed: {status}"
            return stats

        msg_ids = (data[0].decode() if data and data[0] else "").split()
        for msg_id in msg_ids[:max_messages]:
            stats["fetched"] += 1
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK" or not msg_data:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                from_h = _decode_str(msg.get("From", ""))
                from_addr = _extract_from_email(from_h)
                subject = _decode_str(msg.get("Subject", ""))
                message_id = msg.get("Message-ID", "").strip()
                in_reply_to = msg.get("In-Reply-To", "").strip()
                body = _extract_text_body(msg)

                # Match prospect
                prospect = _find_prospect_by_email(from_addr)
                if not prospect:
                    log.info(f"Email from unknown sender: {from_addr} — skipped")
                    # On le marque tout de même comme lu pour ne pas le retraiter
                    mail.store(msg_id, "+FLAGS", "\\Seen")
                    continue

                stats["matched"] += 1
                conv = _store_inbound_conversation(
                    prospect_id=prospect["id"],
                    subject=subject,
                    body=body,
                    message_id=message_id,
                    in_reply_to=in_reply_to,
                    from_addr=from_addr,
                )
                stats["stored"] += 1

                # Marque comme lu
                mail.store(msg_id, "+FLAGS", "\\Seen")

                # Lance classifier intent (async via task queue ou synchrone selon volume)
                try:
                    from inbox.intent_classifier import classify_reply
                    classify_reply(
                        prospect_id=prospect["id"],
                        conversation_id=conv.get("id"),
                        body=body,
                        subject=subject,
                        prospect=prospect,
                    )
                except Exception as e:
                    log.warning(f"classify_reply failed: {e}")

            except Exception as e:
                log.exception(f"Process message {msg_id} failed: {e}")
                continue

        mail.close()
        mail.logout()
        return stats
    except Exception as e:
        log.exception(f"IMAP poll failed: {e}")
        stats["error"] = f"poll: {str(e)[:200]}"
        try:
            mail.logout()
        except Exception:
            pass
        return stats
