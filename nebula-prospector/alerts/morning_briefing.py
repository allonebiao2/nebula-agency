"""Rapport quotidien NOVA — envoyé chaque matin à 8h Cotonou (= 7h UTC).

Format inspiré du brief Mongazi (NOVA v2.0) : signaux, hot leads,
top prospect du jour, tendances.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from db.client import get_db
from alerts.telegram_bot import send_message, _log_alert, _esc

log = logging.getLogger(__name__)

# Cotonou = UTC+1 (pas de DST)
COTONOU_TZ = timezone(timedelta(hours=1))
DAYS_FR = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]


def _fr_date_long(dt: datetime) -> str:
    """31/05/2026 LUNDI"""
    return f"{dt.strftime('%d/%m/%Y')} {DAYS_FR[dt.weekday()]}"


def _query_24h_stats() -> dict[str, Any]:
    """Agrège les stats des dernières 24h depuis Supabase."""
    db = get_db()
    since_iso = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    # Nouveaux prospects ces 24h
    new_24h_resp = (
        db.table("prospects")
        .select("id", count="exact", head=True)
        .gte("created_at", since_iso)
        .execute()
    )
    new_24h = new_24h_resp.count or 0

    # Distribution par tier sur les 24h
    tier_counts: dict[str, int] = {"hot": 0, "warm": 0, "cold": 0, "rejected": 0}
    enriched_resp = (
        db.table("prospects")
        .select("tier")
        .gte("updated_at", since_iso)
        .not_.is_("tier", "null")
        .execute()
    )
    for row in (enriched_resp.data or []):
        t = row.get("tier")
        if t in tier_counts:
            tier_counts[t] += 1

    # Totaux globaux
    total_resp = db.table("prospects").select("id", count="exact", head=True).execute()
    total = total_resp.count or 0
    hot_active_resp = (
        db.table("prospects")
        .select("id", count="exact", head=True)
        .eq("tier", "hot")
        .neq("status", "contacted")
        .execute()
    )
    hot_active = hot_active_resp.count or 0
    warm_active_resp = (
        db.table("prospects")
        .select("id", count="exact", head=True)
        .eq("tier", "warm")
        .neq("status", "contacted")
        .execute()
    )
    warm_active = warm_active_resp.count or 0

    # Top prospect HOT du jour (le plus haut score parmi les hot des 24h)
    top_hot_resp = (
        db.table("prospects")
        .select("name, sector, city, country, score, recommended_service, status_reason, website, email")
        .eq("tier", "hot")
        .gte("updated_at", since_iso)
        .order("score", desc=True)
        .limit(1)
        .execute()
    )
    top_hot = (top_hot_resp.data or [None])[0]

    return {
        "new_24h": new_24h,
        "tier_counts_24h": tier_counts,
        "total": total,
        "hot_active": hot_active,
        "warm_active": warm_active,
        "top_hot": top_hot,
    }


def _build_message(stats: dict[str, Any]) -> str:
    """Compose le message Telegram en HTML."""
    now_cotonou = datetime.now(COTONOU_TZ)
    head = _fr_date_long(now_cotonou)
    t = stats["tier_counts_24h"]

    parts = [
        f"⚡ <b>NOVA — {head}</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
        f"👁 Nouveaux prospects : <b>{stats['new_24h']}</b> (24h)",
        f"🔥 Chauds : <b>{t['hot']}</b>",
        f"☕ Tièdes : <b>{t['warm']}</b>",
        f"🧊 Froids : <b>{t['cold']}</b>",
        f"❌ Rejetés : <b>{t['rejected']}</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
    ]

    top = stats.get("top_hot")
    if top:
        svc = top.get("recommended_service") or "—"
        site = top.get("website") or ""
        email = top.get("email") or "(email à trouver)"
        parts += [
            "🎯 <b>TOP PROSPECT DU JOUR</b>",
            f"<b>{_esc(top.get('name') or '?')}</b>",
            f"{_esc(top.get('sector') or '?')} · {_esc(top.get('city') or '?')}, {_esc(top.get('country') or '?')}",
            f"Score <b>{top.get('score', 0)}/10</b> · Service à pitcher : <b>{_esc(svc)}</b>",
            f"📧 {_esc(email)}",
        ]
        if site:
            parts.append(f"🌐 {_esc(site)}")
        if top.get("status_reason"):
            parts.append(f"💡 <i>{_esc(top['status_reason'])}</i>")
        parts.append("━━━━━━━━━━━━━━━━━━━━━")
    else:
        parts += [
            "<i>Aucun prospect HOT détecté ces 24h.</i>",
            "━━━━━━━━━━━━━━━━━━━━━",
        ]

    parts += [
        f"📊 Total BDD : <b>{stats['total']}</b> prospects",
        f"🎯 HOT actifs : <b>{stats['hot_active']}</b> · WARM : <b>{stats['warm_active']}</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
        "<i>NOVA 🤖 — NEBULA Agency</i>",
    ]
    return "\n".join(parts)


def send_morning_briefing() -> bool:
    """Compose et envoie le rapport quotidien sur Telegram."""
    try:
        stats = _query_24h_stats()
    except Exception as e:
        log.exception(f"morning_briefing query failed: {e}")
        return False
    text = _build_message(stats)
    r = send_message(text, silent=False)
    _log_alert(
        "morning_briefing",
        {"new_24h": stats["new_24h"], "tier_counts": stats["tier_counts_24h"]},
        r.get("result", {}).get("message_id") if r else None,
    )
    return r is not None
