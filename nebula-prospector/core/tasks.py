"""Queue de tâches séquentielles — CEO planifie, Workers exécutent.

Inspiré NanoCorp `create_task / update_task / list_tasks`. Le CEO (Claude)
crée des tâches via function calling. Un worker loop (dans le scheduler ou
en endpoint admin) les consomme et appelle le handler approprié.

Types de tâches supportés :
- sourcing.run                — lance un cycle de sourcing (peut filtrer pays)
- enrichment.run              — enrichit N prospects pending
- enrichment.score_one        — re-score un prospect spécifique (force=True)
- outreach.run                — envoie cold emails à N prospects HOT
- outreach.send_one           — envoie un email à un prospect précis
- document.create             — crée un document (NOVA apprend)
- document.update             — met à jour un document existant
- mission.update              — met à jour la mission active
- maintenance.archive_cold    — archive les prospects cold de plus de N jours

Statuts : pending → running → done | failed | cancelled
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable

from db.client import get_db

log = logging.getLogger(__name__)


# Registre des handlers : type → fonction
_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}


def register_handler(task_type: str):
    """Décorateur pour enregistrer un handler de tâche."""
    def deco(fn: Callable):
        _HANDLERS[task_type] = fn
        return fn
    return deco


def list_handlers() -> list[str]:
    return sorted(_HANDLERS.keys())


# ---------------------------------------------------------------------------
# Création / lecture
# ---------------------------------------------------------------------------

def create_task(
    task_type: str,
    payload: dict[str, Any] | None = None,
    *,
    priority: int = 5,
    reason: str | None = None,
    created_by: str = "nova",
    scheduled_for: datetime | None = None,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Crée une tâche pending dans la queue.

    Args:
        task_type: type (doit matcher un handler enregistré pour être consommé)
        payload: arguments pour le handler
        priority: 1 (basse) à 10 (urgent). Default 5.
        reason: pourquoi cette tâche (pour audit)
    """
    db = get_db()
    insert = {
        "type": task_type,
        "payload": payload or {},
        "priority": max(1, min(10, priority)),
        "reason": (reason or "")[:500],
        "created_by": created_by,
        "max_attempts": max_attempts,
    }
    if scheduled_for:
        insert["scheduled_for"] = scheduled_for.isoformat()
    r = db.table("tasks").insert(insert).execute()
    task = (r.data or [{}])[0]
    log.info(f"task created: {task_type} (id={task.get('id')}, prio={priority})")
    return task


def get_task(task_id: str) -> dict[str, Any] | None:
    db = get_db()
    r = db.table("tasks").select("*").eq("id", task_id).limit(1).execute()
    return (r.data or [None])[0]


def list_tasks(
    *,
    status: str | None = None,
    type_: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    db = get_db()
    q = db.table("tasks").select("*").order("created_at", desc=True).limit(limit)
    if status:
        q = q.eq("status", status)
    if type_:
        q = q.eq("type", type_)
    return q.execute().data or []


def cancel_task(task_id: str, reason: str = "manual cancel") -> bool:
    db = get_db()
    r = (
        db.table("tasks")
        .update({"status": "cancelled", "error": reason[:500],
                 "finished_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", task_id)
        .eq("status", "pending")
        .execute()
    )
    return bool(r.data)


# ---------------------------------------------------------------------------
# Worker loop
# ---------------------------------------------------------------------------

def _pop_next_pending() -> dict[str, Any] | None:
    """Récupère la prochaine tâche pending (la plus prioritaire et la plus ancienne)."""
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    # On query l'ordre voulu, mais le claim doit être atomique → on tente un update
    # sur la 1ère pending qu'on trouve. Si update échoue (race), on retry.
    candidates = (
        db.table("tasks")
        .select("id")
        .eq("status", "pending")
        .lte("scheduled_for", now_iso)
        .order("priority", desc=True)
        .order("scheduled_for", desc=False)
        .limit(5)
        .execute()
        .data or []
    )
    for c in candidates:
        # Claim atomique : update only if still pending
        upd = (
            db.table("tasks")
            .update({
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "attempts": (c.get("attempts") or 0) + 1,
            })
            .eq("id", c["id"])
            .eq("status", "pending")
            .execute()
        )
        if upd.data:
            return upd.data[0]
    return None


def _finalize(
    task_id: str,
    *,
    status: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    db = get_db()
    db.table("tasks").update({
        "status": status,
        "result": result,
        "error": (error or "")[:1000] if error else None,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", task_id).execute()


def process_one_task() -> dict[str, Any] | None:
    """Récupère et exécute UNE tâche pending. Retourne le record final ou None si vide."""
    task = _pop_next_pending()
    if not task:
        return None

    task_type = task.get("type", "")
    task_id = task["id"]
    handler = _HANDLERS.get(task_type)

    if not handler:
        _finalize(task_id, status="failed",
                  error=f"Pas de handler enregistré pour type={task_type}")
        log.warning(f"task {task_id} ({task_type}): no handler")
        return get_task(task_id)

    try:
        result = handler(task.get("payload") or {})
        if not isinstance(result, dict):
            result = {"value": result}
        _finalize(task_id, status="done", result=result)
        log.info(f"task {task_id} ({task_type}) done")
        # Event dashboard
        try:
            from core.events import emit_thought
            emit_thought(f"Tâche {task_type} terminée",
                         description=str(result)[:200])
        except Exception:
            pass
    except Exception as e:
        attempts = task.get("attempts", 1)
        max_attempts = task.get("max_attempts", 3)
        if attempts >= max_attempts:
            _finalize(task_id, status="failed", error=str(e))
            log.exception(f"task {task_id} ({task_type}) failed after {attempts} attempts: {e}")
        else:
            # Retry : repasser en pending
            db = get_db()
            db.table("tasks").update({
                "status": "pending",
                "error": str(e)[:1000],
            }).eq("id", task_id).execute()
            log.warning(f"task {task_id} ({task_type}) retrying ({attempts}/{max_attempts}): {e}")

    return get_task(task_id)


def drain_queue(max_tasks: int = 50) -> dict[str, int]:
    """Consomme jusqu'à `max_tasks` de la queue. Retourne stats."""
    stats = {"processed": 0, "done": 0, "failed": 0, "no_handler": 0}
    for _ in range(max_tasks):
        result = process_one_task()
        if result is None:
            break
        stats["processed"] += 1
        if result["status"] == "done":
            stats["done"] += 1
        elif result["status"] == "failed":
            stats["failed"] += 1
            if "Pas de handler" in (result.get("error") or ""):
                stats["no_handler"] += 1
    return stats


# ---------------------------------------------------------------------------
# Handlers de base (auto-enregistrés au démarrage)
# ---------------------------------------------------------------------------

@register_handler("sourcing.run")
def _h_sourcing(payload: dict[str, Any]) -> dict[str, Any]:
    from main import run_sourcing_pipeline
    country = payload.get("country")
    run_sourcing_pipeline(country=country)
    return {"ok": True}


@register_handler("enrichment.run")
def _h_enrichment(payload: dict[str, Any]) -> dict[str, Any]:
    from main import run_enrichment_pipeline
    limit = int(payload.get("limit") or 25)
    only_with_website = bool(payload.get("only_with_website", True))
    return run_enrichment_pipeline(limit=limit, only_with_website=only_with_website)


@register_handler("outreach.run")
def _h_outreach(payload: dict[str, Any]) -> dict[str, Any]:
    from messaging.outreach import run_outreach
    max_send = payload.get("max_send")
    tiers = payload.get("tiers")  # ex: ["hot","warm","cold"], default None = [hot, warm]
    return run_outreach(max_send=max_send, tiers=tiers)


@register_handler("document.create")
def _h_doc_create(payload: dict[str, Any]) -> dict[str, Any]:
    from core.documents import create_document
    return create_document(
        key=payload["key"],
        title=payload.get("title", payload["key"]),
        content=payload["content"],
        tags=payload.get("tags", []),
        created_by=payload.get("created_by", "nova"),
        upsert=payload.get("upsert", False),
    )


@register_handler("document.update")
def _h_doc_update(payload: dict[str, Any]) -> dict[str, Any]:
    from core.documents import update_document
    result = update_document(
        key=payload["key"],
        content=payload.get("content"),
        title=payload.get("title"),
        tags=payload.get("tags"),
    )
    return result or {"ok": False, "error": "no fields to update"}


@register_handler("mission.update")
def _h_mission_update(payload: dict[str, Any]) -> dict[str, Any]:
    from core.mission import update_mission
    return update_mission(
        new_content=payload["content"],
        reason=payload.get("reason", "task-triggered"),
        edited_by=payload.get("edited_by", "nova"),
    )


@register_handler("maintenance.archive_cold")
def _h_archive_cold(payload: dict[str, Any]) -> dict[str, Any]:
    """Archive les prospects cold non touchés depuis N jours."""
    from datetime import datetime, timedelta, timezone
    days = int(payload.get("days") or 30)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    db = get_db()
    r = (
        db.table("prospects")
        .update({"status": "archived"})
        .eq("tier", "cold")
        .lte("updated_at", cutoff)
        .neq("status", "archived")
        .execute()
    )
    return {"archived": len(r.data or [])}
