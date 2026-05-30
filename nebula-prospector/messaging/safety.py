"""Safety / anti-ban pour l'envoi de cold emails.

Règles :
- Max 15 envois nouveaux / jour (le brief disait 15)
- Cooldown 5 jours minimum entre 2 contacts d'un même prospect
- Blacklist auto si l'email bounce ou que le prospect demande à ne plus être contacté
- Rate-limit court entre 2 envois successifs (30s)
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone

from db.client import get_db

log = logging.getLogger(__name__)

DAILY_LIMIT = 15
COOLDOWN_DAYS = 5
MIN_DELAY_BETWEEN_SENDS_S = 30  # rate-limit court


# ---------------------------------------------------------------------------
# Quotas
# ---------------------------------------------------------------------------

def count_emails_sent_today() -> int:
    """Compte les emails outbound envoyés depuis minuit UTC."""
    db = get_db()
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    r = (
        db.table("conversations")
        .select("id", count="exact", head=True)
        .eq("direction", "out")
        .eq("channel", "email")
        .gte("sent_at", today_start)
        .execute()
    )
    return r.count or 0


def remaining_quota_today() -> int:
    """Combien d'emails NOVA peut encore envoyer aujourd'hui."""
    return max(0, DAILY_LIMIT - count_emails_sent_today())


# ---------------------------------------------------------------------------
# Cooldown par prospect
# ---------------------------------------------------------------------------

def can_contact_prospect(prospect_id: str) -> tuple[bool, str | None]:
    """Vérifie si on peut contacter ce prospect maintenant.

    Retourne (allowed, reason_if_blocked).
    """
    db = get_db()
    cutoff_iso = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS)).isoformat()
    r = (
        db.table("conversations")
        .select("sent_at")
        .eq("prospect_id", prospect_id)
        .eq("direction", "out")
        .gte("sent_at", cutoff_iso)
        .limit(1)
        .execute()
    )
    if r.data:
        last = r.data[0].get("sent_at", "?")
        return False, f"cooldown — déjà contacté le {last}"
    return True, None


def is_blacklisted(prospect_id: str) -> bool:
    """Un prospect est blacklisté si son status est 'blacklisted' ou 'unsubscribed'."""
    db = get_db()
    r = (
        db.table("prospects")
        .select("status")
        .eq("id", prospect_id)
        .limit(1)
        .execute()
    )
    if not r.data:
        return False
    return (r.data[0].get("status") or "") in ("blacklisted", "unsubscribed", "bounced")


def blacklist_prospect(prospect_id: str, reason: str = "manual") -> None:
    """Marque un prospect comme à ne plus jamais contacter."""
    db = get_db()
    db.table("prospects").update({
        "status": "blacklisted",
        "status_reason": f"blacklisted: {reason}"[:500],
    }).eq("id", prospect_id).execute()


# ---------------------------------------------------------------------------
# Rate-limit entre 2 envois
# ---------------------------------------------------------------------------

_last_send_ts: float = 0.0


def wait_between_sends() -> None:
    """Bloque jusqu'à ce que le délai min entre 2 envois soit respecté."""
    global _last_send_ts
    elapsed = time.time() - _last_send_ts
    if elapsed < MIN_DELAY_BETWEEN_SENDS_S:
        sleep_for = MIN_DELAY_BETWEEN_SENDS_S - elapsed
        log.info(f"safety: sleep {sleep_for:.1f}s avant prochain envoi")
        time.sleep(sleep_for)
    _last_send_ts = time.time()
