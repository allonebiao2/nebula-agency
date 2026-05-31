"""Rate limits et audit des outils utilisés par NOVA (inspiré NanoCorp).

Tous les appels d'outils sensibles (Claude API, Resend, OSM, etc.) passent par
le décorateur `@tool_call("name", per_hour=N, per_day=M)`. Le décorateur :
- vérifie qu'on n'a pas dépassé les quotas horaires/journaliers
- log l'appel dans la table `tool_calls` (status ok / failed / rate_limited)
- mesure le temps d'exécution
- relève une exception `RateLimited` si bloqué

Usage :
    from core.tool_calls import tool_call

    @tool_call("claude.score", per_hour=120, per_day=1000)
    def score_prospect(prospect, site_content):
        ...
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable

from db.client import get_db

log = logging.getLogger(__name__)


class RateLimited(Exception):
    """Levée quand un outil dépasse son quota."""

    def __init__(self, tool_name: str, scope: str, used: int, limit: int):
        self.tool_name = tool_name
        self.scope = scope  # 'hour' | 'day'
        self.used = used
        self.limit = limit
        super().__init__(
            f"Rate limit pour {tool_name} : {used}/{limit} sur la dernière {scope}"
        )


# ---------------------------------------------------------------------------
# Comptage
# ---------------------------------------------------------------------------

def count_calls(tool_name: str, *, window_hours: int = 1) -> int:
    """Compte les appels OK du tool sur la fenêtre passée."""
    db = get_db()
    since = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    r = (
        db.table("tool_calls")
        .select("id", count="exact", head=True)
        .eq("tool_name", tool_name)
        .eq("status", "ok")
        .gte("created_at", since)
        .execute()
    )
    return r.count or 0


def log_call(
    tool_name: str,
    *,
    status: str = "ok",
    input_summary: str | None = None,
    output_summary: str | None = None,
    duration_ms: int | None = None,
    caller: str = "nova",
) -> None:
    """Insère un log dans tool_calls. Best-effort (silencieux si échec BDD)."""
    try:
        get_db().table("tool_calls").insert({
            "tool_name": tool_name,
            "caller": caller,
            "input_summary": (input_summary or "")[:500],
            "output_summary": (output_summary or "")[:500],
            "status": status,
            "duration_ms": duration_ms,
        }).execute()
    except Exception as e:
        log.warning(f"tool_calls log failed: {e}")


# ---------------------------------------------------------------------------
# Décorateur
# ---------------------------------------------------------------------------

def tool_call(
    name: str,
    *,
    per_hour: int | None = None,
    per_day: int | None = None,
    raise_on_limit: bool = True,
    log_input: bool = True,
    log_output: bool = True,
) -> Callable:
    """Décorateur pour wrapper un outil avec rate-limit + audit.

    Args:
        name: identifiant unique du tool (ex: "claude.score", "resend.send")
        per_hour: limite par heure (None = pas de limite)
        per_day: limite par jour
        raise_on_limit: si True, lève RateLimited. Sinon retourne None et log.
        log_input: si True, sérialise le 1er arg dans input_summary
        log_output: si True, sérialise le résultat dans output_summary
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Check quotas
            if per_hour is not None:
                used = count_calls(name, window_hours=1)
                if used >= per_hour:
                    log_call(name, status="rate_limited",
                             input_summary=f"hourly limit {used}/{per_hour}")
                    if raise_on_limit:
                        raise RateLimited(name, "heure", used, per_hour)
                    return None
            if per_day is not None:
                used = count_calls(name, window_hours=24)
                if used >= per_day:
                    log_call(name, status="rate_limited",
                             input_summary=f"daily limit {used}/{per_day}")
                    if raise_on_limit:
                        raise RateLimited(name, "jour", used, per_day)
                    return None

            # Exécution
            t0 = time.time()
            in_summary = ""
            if log_input and args:
                in_summary = str(args[0])[:300] if args else ""
            try:
                result = fn(*args, **kwargs)
                duration = int((time.time() - t0) * 1000)
                out_summary = ""
                if log_output and result is not None:
                    out_summary = str(result)[:300]
                log_call(name, status="ok",
                         input_summary=in_summary, output_summary=out_summary,
                         duration_ms=duration)
                return result
            except Exception as e:
                duration = int((time.time() - t0) * 1000)
                log_call(name, status="failed",
                         input_summary=in_summary,
                         output_summary=f"ERROR: {str(e)[:200]}",
                         duration_ms=duration)
                raise

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_tool_stats(window_hours: int = 24) -> dict[str, dict[str, int]]:
    """Retourne {tool_name: {ok, failed, rate_limited, total}} sur la fenêtre."""
    db = get_db()
    since = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    r = (
        db.table("tool_calls")
        .select("tool_name, status")
        .gte("created_at", since)
        .execute()
    )
    out: dict[str, dict[str, int]] = {}
    for row in (r.data or []):
        t = row["tool_name"]
        s = row["status"]
        if t not in out:
            out[t] = {"ok": 0, "failed": 0, "rate_limited": 0, "total": 0}
        out[t][s] = out[t].get(s, 0) + 1
        out[t]["total"] += 1
    return out
