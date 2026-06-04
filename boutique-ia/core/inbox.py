"""Boîte email entrante — l'agent LIT et RÉPOND aux réponses de prospection RECRUTEMENT.

Seules les réponses au recrutement reviennent dans NOTRE boîte (`GMAIL_USER`, qui est
le reply-to des emails de recrutement). Les réponses des clients d'une boutique partent
vers l'email du commerçant (`owner_email`), donc hors de notre portée — on ne les gère
pas ici (c'est volontaire et correct).

Pipeline (`run_inbox`) : IMAP UNSEEN → parse → match prospect (recrutement) → STOP→opt-out,
sinon l'agent rédige une réponse pour convertir en boutique Vendora → envoi via Resend →
trace dans `bia_inbox`. Le message IMAP est marqué \\Seen pour ne pas le retraiter.

Garde-fous : ne répond QU'AUX prospects qu'on a réellement contactés (jamais aux
inconnus/newsletters), respecte l'opt-out, plafond/jour, 1 réponse/prospect/cooldown,
ignore nos propres adresses et les expéditeurs automatiques. DORMANT tant que
`GMAIL_USER`/`GMAIL_APP_PASSWORD` absents ; OFF par défaut (`inbox_enabled`).
"""
from __future__ import annotations

import email
import imaplib
import logging
import re
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header
from email.utils import parseaddr
from typing import Any

from config import settings

log = logging.getLogger("boutique-ia.inbox")

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

# Plafonds (garde-fous d'envoi sortant)
DAILY_REPLY_CAP = 60          # réponses/jour max (sécurité, aligné sur la prospection)
REPLY_COOLDOWN_HOURS = 12     # pas plus d'1 réponse au même prospect par 12h (anti-boucle)
FETCH_LIMIT = 25             # messages traités par passage

_STOP_WORDS = {"stop", "stopp", "unsubscribe", "désabonner", "desabonner",
               "désinscription", "desinscription", "arret", "arrêt", "arreter",
               "arrêter", "ne plus me contacter", "ne plus recevoir"}
# Expéditeurs à ignorer (automates) : on ne répond jamais à ça.
_AUTO_SENDERS = ("no-reply", "noreply", "no_reply", "mailer-daemon", "postmaster",
                 "donotreply", "do-not-reply", "notifications@", "bounce")


def configured() -> bool:
    return bool(settings.gmail_user and settings.gmail_app_password)


def is_stop(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    # STOP isolé OU phrases de désinscription explicites
    if t in _STOP_WORDS:
        return True
    first = t.splitlines()[0][:60] if t.splitlines() else t[:60]
    if first.strip() in _STOP_WORDS:
        return True
    return any(w in t for w in ("ne plus me contacter", "ne plus recevoir",
                                "me désinscrire", "me desinscrire"))


def _is_auto_sender(addr: str) -> bool:
    a = (addr or "").strip().lower()
    if not a:
        return True
    if settings.gmail_user and a == settings.gmail_user.strip().lower():
        return True  # nos propres envois
    return any(tok in a for tok in _AUTO_SENDERS)


def _decode(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:  # noqa: BLE001
        return value


def _extract_text(msg: email.message.Message) -> str:
    """Corps en texte brut (préfère text/plain, nettoie la partie citée si possible)."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if ctype == "text/plain" and "attachment" not in disp:
                body = _payload_text(part)
                if body:
                    break
        if not body:  # repli : premier text/html dégrossi
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = re.sub(r"<[^>]+>", " ", _payload_text(part))
                    break
    else:
        body = _payload_text(msg)
    return _strip_quoted(body).strip()


def _payload_text(part: email.message.Message) -> str:
    try:
        raw = part.get_payload(decode=True)
        if raw is None:
            return ""
        charset = part.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace")
    except Exception:  # noqa: BLE001
        return ""


def _strip_quoted(text: str) -> str:
    """Enlève la partie citée (réponse précédente) pour ne garder que le nouveau message."""
    lines = []
    for ln in (text or "").splitlines():
        s = ln.strip()
        # Marqueurs classiques de citation Gmail/Outlook
        if s.startswith(">"):
            continue
        # Attribution Gmail/Outlook : « Le … , X a écrit : » / « On … X wrote : »
        # (tolérant aux accents : « a écrit » ou « a ecrit »).
        if re.search(r"\ba\s+[ée]crit\s*:?\s*$", s, re.I):
            break
        if re.search(r"\bwrote\s*:?\s*$", s, re.I):
            break
        if re.match(r"^-{2,}\s*(message d'origine|original message)", s, re.I):
            break
        if s.startswith("De :") or s.startswith("From:"):
            break
        lines.append(ln)
    cleaned = "\n".join(lines).strip()
    return cleaned or (text or "").strip()


def parse_email_bytes(raw: bytes) -> dict[str, Any]:
    """Parse un email brut (RFC822) en {from_email, from_name, subject, body, message_id}.

    Fonction PURE (testable hors IMAP).
    """
    msg = email.message_from_bytes(raw)
    name, addr = parseaddr(msg.get("From", ""))
    # Adresse destinataire d'origine (avant le forward catch-all) : sert à router
    # la réponse vers la bonne boutique. On regarde To, puis les en-têtes de forward.
    to_raw = (msg.get("To") or msg.get("Delivered-To") or msg.get("X-Forwarded-To")
              or msg.get("X-Original-To") or "")
    _, to_addr = parseaddr(to_raw)
    return {
        "from_email": (addr or "").strip().lower(),
        "from_name": _decode(name).strip(),
        "to_email": (to_addr or "").strip().lower(),
        "subject": _decode(msg.get("Subject")),
        "body": _extract_text(msg),
        "message_id": (msg.get("Message-ID") or "").strip(),
    }


def fetch_unseen(limit: int = FETCH_LIMIT) -> list[dict[str, Any]]:
    """Récupère les emails NON LUS de la boîte et les marque \\Seen. [] si KO/dormant."""
    if not configured():
        return []
    out: list[dict[str, Any]] = []
    try:
        srv = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        srv.login(settings.gmail_user, settings.gmail_app_password)
        srv.select("INBOX")
        typ, data = srv.search(None, "UNSEEN")
        if typ == "OK":
            ids = (data[0] or b"").split()
            for num in ids[:limit]:
                typ, msgdata = srv.fetch(num, "(RFC822)")
                if typ != "OK" or not msgdata or not msgdata[0]:
                    continue
                parsed = parse_email_bytes(msgdata[0][1])
                out.append(parsed)
                srv.store(num, "+FLAGS", "\\Seen")  # ne pas retraiter
        srv.logout()
    except Exception as e:  # noqa: BLE001
        log.warning("IMAP fetch KO: %s", e)
    return out


def _route_merchant(to_email: str):
    """Si l'email était adressé à l'alias d'une boutique (code@domaine), retourne la
    boutique. Sinon None (= flux recrutement)."""
    to = (to_email or "").strip().lower()
    if "@" not in to:
        return None
    local = to.split("@", 1)[0]
    if not local or local in ("contact", "hello", "info", "admin",
                              "no-reply", "noreply", "bounce", "send"):
        return None
    try:
        from db.client import get_merchant_by_code
        return get_merchant_by_code(local)
    except Exception:  # noqa: BLE001
        return None


def _reply_subject(subject: str | None, default: str) -> str:
    s = (subject or default).strip()
    if not s.lower().startswith("re"):
        s = "Re: " + s
    return s[:120]


def run_inbox() -> dict[str, Any]:
    """Lit la boîte et répond aux prospects (recrutement + boutiques). OFF par défaut.

    Routing : si l'email visait l'alias d'une boutique → flux boutique (mode supervisé
    = brouillon à valider, ou auto = envoi direct) ; sinon → flux recrutement (l'agent
    répond pour convertir en boutique). Garde-fous : ne répond qu'aux prospects connus,
    STOP/opt-out respecté, plafond/jour, cooldown. Retourne un résumé.
    """
    from db.client import get_setting_bool, inbox_message_seen

    summary = {"checked": 0, "replied": 0, "drafts": 0, "optouts": 0, "skipped": 0}
    if not get_setting_bool("inbox_enabled", False):
        return summary
    if not (configured() and settings.resend_api_key):
        return summary  # besoin de lire (IMAP) ET d'envoyer (Resend)

    boutique_on = get_setting_bool("boutique_inbox_enabled", False)
    today_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
    cooldown_iso = (datetime.now(timezone.utc) - timedelta(hours=REPLY_COOLDOWN_HOURS)).isoformat()

    for m in fetch_unseen():
        summary["checked"] += 1
        from_email = m.get("from_email") or ""
        body = m.get("body") or ""
        mid = m.get("message_id") or ""

        if _is_auto_sender(from_email):
            summary["skipped"] += 1; continue
        if mid and inbox_message_seen(mid):
            summary["skipped"] += 1; continue  # déjà traité (dédup)

        merchant = _route_merchant(m.get("to_email")) if boutique_on else None
        if merchant:
            from core.capabilities import has_capability
            if not has_capability(merchant, "email_pro"):
                summary["skipped"] += 1; continue  # forfait sans module email pro

        if merchant:
            _handle_boutique(merchant, m, from_email, body, mid, summary,
                             today_start, cooldown_iso)
        else:
            _handle_recruitment(m, from_email, body, mid, summary,
                                today_start, cooldown_iso)

    return summary


def _handle_recruitment(m, from_email, body, mid, summary, today_start, cooldown_iso) -> None:
    from db.client import (add_optout, count_inbox_out_since, find_recruitment_prospect,
                           inbox_out_recently, is_opted_out, list_inbox_thread, record_inbox)
    from core.prospecting import compose_recruitment_reply, send_email, _unsub_footer

    prospect = find_recruitment_prospect(from_email)
    if not prospect:
        summary["skipped"] += 1; return   # inconnu → on ne répond pas (sécurité)
    try:
        record_inbox(from_email, "in", m.get("subject"), body, mid)
    except Exception:  # noqa: BLE001
        log.warning("record_inbox(in) KO", exc_info=True)
    if is_stop(body) or is_opted_out(from_email):
        try:
            add_optout(from_email, "email", "stop-reply")
        except Exception:  # noqa: BLE001
            pass
        summary["optouts"] += 1; return
    if count_inbox_out_since(today_start) >= DAILY_REPLY_CAP:
        summary["skipped"] += 1; return
    if inbox_out_recently(from_email, cooldown_iso):
        summary["skipped"] += 1; return
    try:
        thread = list_inbox_thread(from_email)
        reply = compose_recruitment_reply(thread, prospect)
        subject = _reply_subject(m.get("subject"), "Votre vendeur WhatsApp Vendora")
        full = reply + "\n\n" + _unsub_footer(from_email)
        res = send_email(from_email, subject, full,
                         reply_to=settings.email_reply_to or settings.gmail_user,
                         from_name="Mongazi · NEBULA Agency")
        if res.get("ok"):
            record_inbox(from_email, "out", subject, reply)
            summary["replied"] += 1
        else:
            summary["skipped"] += 1
            log.warning("recruitment reply non envoyé: %s", res.get("error"))
    except Exception:  # noqa: BLE001
        summary["skipped"] += 1
        log.warning("recruitment reply KO", exc_info=True)


def _handle_boutique(merchant, m, from_email, body, mid, summary, today_start, cooldown_iso) -> None:
    """Réponse pour une boutique : auto = envoi ; review = brouillon à valider."""
    from core import brain
    from db.client import (add_optout, find_merchant_prospect, get_active_lessons,
                           inbox_out_recently, is_opted_out, list_inbox_thread,
                           list_products, record_inbox)
    from core.prospecting import merchant_email_alias, send_email, _unsub_footer

    mid_merchant = merchant["id"]
    prospect = find_merchant_prospect(mid_merchant, from_email)
    if not prospect:
        summary["skipped"] += 1; return
    try:
        record_inbox(from_email, "in", m.get("subject"), body, mid, merchant_id=mid_merchant)
    except Exception:  # noqa: BLE001
        log.warning("record_inbox(in) boutique KO", exc_info=True)
    if is_stop(body) or is_opted_out(from_email):
        try:
            add_optout(from_email, "email", "stop-reply")
        except Exception:  # noqa: BLE001
            pass
        summary["optouts"] += 1; return
    if inbox_out_recently(from_email, cooldown_iso):
        summary["skipped"] += 1; return
    try:
        products = list_products(mid_merchant)
        try:
            lessons = get_active_lessons(mid_merchant)
        except Exception:  # noqa: BLE001
            lessons = ""
        thread = list_inbox_thread(from_email, merchant_id=mid_merchant)
        reply = brain.email_reply(merchant, products, thread, lessons=lessons)
        subject = _reply_subject(m.get("subject"), f"Votre message à {merchant.get('business_name') or 'la boutique'}")
        mode = (merchant.get("inbox_mode") or "review").strip().lower()
        if mode == "auto":
            full = reply + "\n\n" + _unsub_footer(from_email)
            alias = merchant_email_alias(merchant)
            res = send_email(from_email, subject, full, reply_to=alias,
                             from_name=merchant.get("business_name") or "Boutique",
                             from_address=alias)
            if res.get("ok"):
                record_inbox(from_email, "out", subject, reply, merchant_id=mid_merchant)
                summary["replied"] += 1
            else:
                summary["skipped"] += 1
                log.warning("boutique reply non envoyé: %s", res.get("error"))
        else:
            # Mode supervisé : on enregistre un BROUILLON, on n'envoie pas.
            record_inbox(from_email, "out", subject, reply,
                         merchant_id=mid_merchant, status="draft")
            summary["drafts"] += 1
    except Exception:  # noqa: BLE001
        summary["skipped"] += 1
        log.warning("boutique reply KO", exc_info=True)
