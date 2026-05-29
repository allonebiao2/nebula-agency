"""Client Supabase singleton + helpers prospects."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from config import settings


@lru_cache
def get_db() -> Client:
    """Retourne le client Supabase (singleton)."""
    settings.require("supabase_url", "supabase_service_role_key")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# ---------------------------------------------------------------------------
# Helpers prospects
# ---------------------------------------------------------------------------

def upsert_prospect(payload: dict[str, Any]) -> dict[str, Any]:
    """Insert ou update sur (source, source_external_id)."""
    db = get_db()
    result = (
        db.table("prospects")
        .upsert(payload, on_conflict="source,source_external_id")
        .execute()
    )
    return result.data[0] if result.data else {}


def get_prospect_by_external(source: str, external_id: str) -> dict[str, Any] | None:
    db = get_db()
    result = (
        db.table("prospects")
        .select("*")
        .eq("source", source)
        .eq("source_external_id", external_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_prospects(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    db = get_db()
    q = db.table("prospects").select("*").order("score", desc=True).limit(limit)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


def count_prospects_by_status() -> dict[str, int]:
    db = get_db()
    rows = db.table("prospects").select("status").execute().data or []
    counts: dict[str, int] = {}
    for row in rows:
        s = row["status"]
        counts[s] = counts.get(s, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Helpers sourcing_runs
# ---------------------------------------------------------------------------

def start_sourcing_run(source: str, query: str | None = None, location: str | None = None) -> str:
    db = get_db()
    result = db.table("sourcing_runs").insert({
        "source": source,
        "query": query,
        "location": location,
        "status": "running",
    }).execute()
    return result.data[0]["id"]


def finish_sourcing_run(
    run_id: str,
    *,
    results_count: int = 0,
    inserted_count: int = 0,
    updated_count: int = 0,
    skipped_count: int = 0,
    status: str = "success",
    error_message: str | None = None,
) -> None:
    db = get_db()
    db.table("sourcing_runs").update({
        "results_count": results_count,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "status": status,
        "error_message": error_message,
        "finished_at": "now()",
    }).eq("id", run_id).execute()
