"""Mission auto-éditable de NOVA (inspiré NanoCorp `update_mission`).

NOVA peut elle-même réécrire son prompt système pour s'adapter à ce qu'elle
apprend. Chaque modification est versionnée — on garde l'historique complet.
Une seule version est active à la fois (contrainte unique partielle SQL).

Usage :
    from core.mission import get_active_mission, update_mission
    text = get_active_mission()
    update_mission(new_text, reason="Acné Control n'est plus vendu, à retirer du pitch", edited_by="nova")
"""
from __future__ import annotations

import logging
from typing import Any

from db.client import get_db

log = logging.getLogger(__name__)

# Cache léger pour éviter de query la BDD à chaque appel
_cached_mission: dict[str, Any] | None = None
_cache_ts: float = 0
_CACHE_TTL_SECONDS = 60


def _fetch_active() -> dict[str, Any] | None:
    db = get_db()
    r = (
        db.table("nova_mission")
        .select("*")
        .eq("active", True)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    return (r.data or [None])[0]


def get_active_mission(force_refresh: bool = False) -> str:
    """Retourne le contenu de la mission active. Cache 60s."""
    global _cached_mission, _cache_ts
    import time
    if not force_refresh and _cached_mission and (time.time() - _cache_ts) < _CACHE_TTL_SECONDS:
        return _cached_mission.get("content", "")
    m = _fetch_active()
    if m:
        _cached_mission = m
        _cache_ts = time.time()
        return m.get("content", "")
    return ""


def get_active_mission_full() -> dict[str, Any] | None:
    """Retourne le dict complet de la mission active (version, content, edited_by, etc.)."""
    return _fetch_active()


def update_mission(
    new_content: str,
    *,
    reason: str,
    edited_by: str = "nova",
) -> dict[str, Any]:
    """Crée une nouvelle version de la mission et la désactive l'ancienne.

    Atomique : on désactive d'abord, puis on insère la nouvelle version active.
    Retourne le nouveau record.
    """
    global _cached_mission, _cache_ts
    if not new_content or len(new_content.strip()) < 50:
        raise ValueError("Mission trop courte (min 50 caractères)")
    if edited_by not in ("nova", "mongazi", "system"):
        raise ValueError(f"edited_by invalide : {edited_by}")

    db = get_db()
    # Récupère la version actuelle
    current = _fetch_active()
    next_version = (current["version"] + 1) if current else 1

    # Désactive l'ancienne (pour respecter la contrainte unique partielle)
    if current:
        db.table("nova_mission").update({"active": False}).eq("id", current["id"]).execute()

    # Insère la nouvelle, active
    insert = (
        db.table("nova_mission")
        .insert({
            "version": next_version,
            "content": new_content.strip(),
            "reason_for_change": reason[:500],
            "edited_by": edited_by,
            "active": True,
        })
        .execute()
    )
    new_record = (insert.data or [{}])[0]

    # Invalide le cache
    _cached_mission = None
    _cache_ts = 0

    # Event dashboard
    try:
        from core.events import emit_thought
        emit_thought(
            f"Mission mise à jour (v{next_version}, par {edited_by})",
            description=reason[:200],
        )
    except Exception:
        pass

    log.info(f"Mission updated: v{next_version} by {edited_by} — {reason[:100]}")
    return new_record


def get_mission_history(limit: int = 20) -> list[dict[str, Any]]:
    """Retourne les N dernières versions de la mission (pour audit)."""
    db = get_db()
    r = (
        db.table("nova_mission")
        .select("*")
        .order("version", desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []
