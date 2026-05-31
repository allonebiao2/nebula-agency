"""Dashboard FastAPI — sert l'interface temps réel NOVA.

Lancer en dev :
    uvicorn dashboard.server:app --reload --port 8001

Lancer en prod (sur VPS) :
    uvicorn dashboard.server:app --host 0.0.0.0 --port 8001 --workers 2
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from core import persona
from db.client import (
    count_prospects_by_status,
    get_db,
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title=f"{persona.NAME} · Dashboard",
    description=persona.SHORT_BIO,
    version=persona.VERSION,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ---------------------------------------------------------------------------
# Scheduler (cron sourcing quotidien)
# ---------------------------------------------------------------------------
# En production, NOVA lance le sourcing automatiquement à 3h UTC chaque jour.
# En dev, le scheduler ne se lance pas pour éviter les sourcings indésirables.

_scheduler = None

def _run_daily_pipeline():
    """Job quotidien : sourcing OSM → enrichissement (emails + scoring Claude)."""
    import logging
    log = logging.getLogger("nova.scheduler")

    # 1. Sourcing
    log.info("[scheduler] daily — début sourcing")
    try:
        from main import run_sourcing_pipeline
        run_sourcing_pipeline()
        log.info("[scheduler] daily — sourcing OK")
    except Exception as e:
        log.exception(f"[scheduler] sourcing échoué : {e}")
        try:
            from alerts.telegram_bot import notify_error
            notify_error(f"Sourcing quotidien échoué : {e}")
        except Exception:
            pass
        return  # pas la peine d'enrichir si le sourcing a planté

    # 2. Enrichissement (limité à 25/jour pour ne pas brûler de tokens Claude)
    log.info("[scheduler] daily — début enrichissement")
    try:
        from main import run_enrichment_pipeline
        stats = run_enrichment_pipeline(limit=25, only_with_website=True)
        log.info(
            f"[scheduler] daily — enrichissement OK : "
            f"{stats['processed']} traités · {stats['with_email']} emails · "
            f"hot={stats.get('hot',0)} warm={stats.get('warm',0)} "
            f"cold={stats.get('cold',0)} rejected={stats.get('rejected',0)}"
        )
    except Exception as e:
        log.exception(f"[scheduler] enrichissement échoué : {e}")
        try:
            from alerts.telegram_bot import notify_error
            notify_error(f"Enrichissement quotidien échoué : {e}")
        except Exception:
            pass

    # 3. Outreach (envoi cold emails aux HOT non encore contactés, max 15/jour)
    log.info("[scheduler] daily — début outreach")
    try:
        from messaging.outreach import run_outreach
        out = run_outreach()
        log.info(
            f"[scheduler] daily — outreach OK : envoyés={out['sent']} "
            f"skipped={out['skipped']} erreurs={out['errors']} (quota={out['quota']})"
        )
    except Exception as e:
        log.exception(f"[scheduler] outreach échoué : {e}")
        try:
            from alerts.telegram_bot import notify_error
            notify_error(f"Outreach quotidien échoué : {e}")
        except Exception:
            pass


def _run_morning_briefing():
    """Job 7h UTC (= 8h Cotonou) : envoie le rapport matinal sur Telegram."""
    import logging
    log = logging.getLogger("nova.scheduler")
    log.info("[scheduler] morning briefing")
    try:
        from alerts.morning_briefing import send_morning_briefing
        ok = send_morning_briefing()
        log.info(f"[scheduler] morning briefing {'OK' if ok else 'FAILED'}")
    except Exception as e:
        log.exception(f"[scheduler] morning briefing erreur : {e}")


def _drain_task_queue():
    """Worker loop : consomme la queue tasks (CEO ↔ Workers)."""
    import logging
    log = logging.getLogger("nova.scheduler")
    try:
        from core.tasks import drain_queue
        stats = drain_queue(max_tasks=10)  # max 10 tâches par tick (toutes les 10 min)
        if stats["processed"] > 0:
            log.info(f"[scheduler] tasks drained : {stats}")
    except Exception as e:
        log.exception(f"[scheduler] task drain erreur : {e}")


def _poll_inbox_imap():
    """Job IMAP : récupère les nouvelles réponses prospects et les classifie."""
    import logging
    log = logging.getLogger("nova.scheduler")
    try:
        from inbox.imap_poller import poll_inbox
        stats = poll_inbox(max_messages=30)
        if stats.get("fetched", 0) > 0 or stats.get("error"):
            log.info(f"[scheduler] inbox poll : {stats}")
    except Exception as e:
        log.exception(f"[scheduler] inbox poll erreur : {e}")


def _run_weekly_learning():
    """Job dimanche 22h UTC : NOVA s'auto-améliore en réfléchissant à sa semaine."""
    import logging
    log = logging.getLogger("nova.scheduler")
    log.info("[scheduler] weekly learning start")
    try:
        from learning.weekly_learner import run_weekly_learning
        result = run_weekly_learning()
        log.info(f"[scheduler] weekly learning done: applied={result.get('applied')}")
    except Exception as e:
        log.exception(f"[scheduler] weekly learning erreur : {e}")


@app.on_event("startup")
async def _start_scheduler():
    global _scheduler
    if settings.env != "production":
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        _scheduler = BackgroundScheduler(timezone="UTC")
        _scheduler.add_job(
            _run_daily_pipeline,
            "cron",
            hour=3,
            minute=0,
            id="daily_pipeline",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        _scheduler.add_job(
            _run_morning_briefing,
            "cron",
            hour=7,  # 7h UTC = 8h Cotonou (UTC+1)
            minute=0,
            id="morning_briefing",
            replace_existing=True,
            misfire_grace_time=1800,
        )
        _scheduler.add_job(
            _drain_task_queue,
            "interval",
            minutes=10,
            id="task_queue_drain",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        _scheduler.add_job(
            _poll_inbox_imap,
            "interval",
            minutes=5,
            id="inbox_imap_poll",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        _scheduler.add_job(
            _run_weekly_learning,
            "cron",
            day_of_week="sun",
            hour=22,  # 22h UTC = 23h Cotonou dimanche soir
            minute=0,
            id="weekly_learning",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        _scheduler.start()
        import logging
        logging.getLogger("nova.scheduler").info(
            "[scheduler] APScheduler démarré : sourcing 3h UTC + briefing 7h UTC + "
            "task queue 10min + IMAP poll 5min"
        )
    except Exception as e:
        import logging
        logging.getLogger("nova.scheduler").exception(
            f"[scheduler] échec démarrage : {e}"
        )


@app.on_event("shutdown")
async def _stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Endpoints admin (déclenchent les jobs à la demande, protégés par token)
# ---------------------------------------------------------------------------

def _check_admin_token(request: Request) -> bool:
    import os
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected:
        return False  # pas de token configuré = endpoints désactivés
    provided = request.headers.get("X-Admin-Token") or request.query_params.get("token", "")
    return provided == expected


@app.post("/api/admin/run/morning-briefing")
async def admin_run_morning_briefing(request: Request):
    """Force l'envoi du briefing matinal sur Telegram."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from alerts.morning_briefing import send_morning_briefing
        ok = send_morning_briefing()
        return {"ok": ok}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/admin/run/sourcing")
async def admin_run_sourcing(request: Request):
    """Force un cycle sourcing + enrichissement + outreach (peut prendre 5-10 min)."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    import threading
    threading.Thread(target=_run_daily_pipeline, daemon=True).start()
    return {"ok": True, "message": "Pipeline lancé en arrière-plan"}


@app.post("/api/admin/run/outreach")
async def admin_run_outreach(request: Request):
    """Force un cycle d'outreach (cold emails) — utile pour tester."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from messaging.outreach import run_outreach
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        max_send = body.get("max_send") if isinstance(body, dict) else None
        stats = run_outreach(max_send=max_send)
        return {"ok": True, "stats": stats}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/admin/run/enrich")
async def admin_run_enrich(request: Request):
    """Force un cycle d'enrichissement (en arrière-plan pour éviter timeout HTTP)."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        if not isinstance(body, dict):
            body = {}
        limit = int(body.get("limit", 25))
        only_with_website = bool(body.get("only_with_website", True))
        background = bool(body.get("background", True))  # default async pour éviter timeout

        if not background:
            from main import run_enrichment_pipeline
            stats = run_enrichment_pipeline(limit=limit, only_with_website=only_with_website)
            return {"ok": True, "stats": stats}

        # Mode background : lance en thread, retour immédiat
        import threading
        def _run():
            try:
                from main import run_enrichment_pipeline
                import logging
                log = logging.getLogger("nova.admin")
                log.info(f"[admin] enrich bg start (limit={limit}, only_with_website={only_with_website})")
                s = run_enrichment_pipeline(limit=limit, only_with_website=only_with_website)
                log.info(f"[admin] enrich bg done : {s}")
            except Exception as e:
                import logging
                logging.getLogger("nova.admin").exception(f"[admin] enrich bg failed: {e}")

        threading.Thread(target=_run, daemon=True).start()
        return {"ok": True, "message": f"Enrichissement lancé en background (limit={limit})"}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# NOVA v2 brain layer — Mission, Documents, Tasks
# ---------------------------------------------------------------------------

@app.get("/api/admin/mission")
async def admin_get_mission(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from core.mission import get_active_mission_full, get_mission_history
    return {"ok": True, "active": get_active_mission_full(), "history": get_mission_history(10)}


@app.post("/api/admin/mission")
async def admin_update_mission(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from core.mission import update_mission
        body = await request.json()
        record = update_mission(
            new_content=body["content"],
            reason=body.get("reason", "via admin endpoint"),
            edited_by=body.get("edited_by", "mongazi"),
        )
        return {"ok": True, "mission": record}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.get("/api/admin/documents")
async def admin_list_documents(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from core.documents import list_documents
    return {"ok": True, "documents": list_documents(100)}


@app.get("/api/admin/documents/{key}")
async def admin_read_document(key: str, request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from core.documents import read_document
    doc = read_document(key)
    if not doc:
        return JSONResponse({"ok": False, "error": "not found"}, status_code=404)
    return {"ok": True, "document": doc}


@app.post("/api/admin/documents")
async def admin_create_document(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from core.documents import create_document
        body = await request.json()
        doc = create_document(
            key=body["key"],
            title=body.get("title", body["key"]),
            content=body["content"],
            tags=body.get("tags", []),
            created_by=body.get("created_by", "mongazi"),
            upsert=bool(body.get("upsert", False)),
        )
        return {"ok": True, "document": doc}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.get("/api/admin/tasks")
async def admin_list_tasks(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from core.tasks import list_tasks, list_handlers
    status = request.query_params.get("status")
    type_ = request.query_params.get("type")
    return {
        "ok": True,
        "handlers": list_handlers(),
        "tasks": list_tasks(status=status, type_=type_, limit=100),
    }


@app.post("/api/admin/tasks")
async def admin_create_task(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from core.tasks import create_task
        body = await request.json()
        t = create_task(
            task_type=body["type"],
            payload=body.get("payload", {}),
            priority=int(body.get("priority", 5)),
            reason=body.get("reason"),
            created_by=body.get("created_by", "mongazi"),
        )
        return {"ok": True, "task": t}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.post("/api/admin/tasks/drain")
async def admin_drain_tasks(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from core.tasks import drain_queue
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        max_tasks = body.get("max_tasks", 20) if isinstance(body, dict) else 20
        stats = drain_queue(max_tasks=max_tasks)
        return {"ok": True, "stats": stats}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/admin/tool-stats")
async def admin_tool_stats(request: Request):
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from core.tool_calls import get_tool_stats
    hours = int(request.query_params.get("hours", "24"))
    return {"ok": True, "window_hours": hours, "stats": get_tool_stats(window_hours=hours)}


# ---------------------------------------------------------------------------
# Chat Telegram bidirectionnel
# ---------------------------------------------------------------------------

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Reçoit les messages Telegram entrants. Sécurisé via X-Telegram-Bot-Api-Secret-Token."""
    import os
    expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    provided = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if expected_secret and provided != expected_secret:
        return JSONResponse({"ok": False, "error": "invalid secret"}, status_code=403)

    try:
        update = await request.json()
        from alerts.telegram_chat import handle_incoming_message
        result = handle_incoming_message(update)
        return {"ok": True, **result}
    except Exception as e:
        import logging
        logging.getLogger("nova.telegram").exception(f"webhook error: {e}")
        # Toujours retourner 200 à Telegram pour éviter retries indéfinis
        return {"ok": False, "error": str(e)[:200]}


@app.post("/api/admin/telegram/setup-webhook")
async def admin_setup_webhook(request: Request):
    """Configure le webhook Telegram pour pointer vers notre endpoint."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    import os
    from alerts.telegram_chat import setup_webhook
    public_url = "https://nebula-agency-production.up.railway.app/api/telegram/webhook"
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    if not secret:
        return JSONResponse({"ok": False, "error": "TELEGRAM_WEBHOOK_SECRET env var missing"}, status_code=500)
    result = setup_webhook(public_url, secret_token=secret)
    return {"ok": result.get("ok", False), "telegram_response": result}


@app.get("/api/admin/telegram/webhook-info")
async def admin_webhook_info(request: Request):
    """Vérifie l'état actuel du webhook Telegram."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    from alerts.telegram_chat import get_webhook_info
    return get_webhook_info()


# ---------------------------------------------------------------------------
# V4 — Inbox IMAP (lecture réponses prospects)
# ---------------------------------------------------------------------------

@app.post("/api/admin/run/weekly-learning")
async def admin_run_weekly_learning(request: Request):
    """Force le cycle d'apprentissage hebdo immédiat (sans attendre dimanche)."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        import threading
        def _run():
            try:
                from learning.weekly_learner import run_weekly_learning
                run_weekly_learning()
            except Exception as e:
                import logging
                logging.getLogger("nova.admin").exception(f"weekly_learning failed: {e}")
        threading.Thread(target=_run, daemon=True).start()
        return {"ok": True, "message": "Cycle apprentissage hebdo lancé en background (~30-60s)"}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/admin/run/imap-poll")
async def admin_run_imap_poll(request: Request):
    """Force un poll IMAP immédiat — utile pour tester sans attendre 5 min."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from inbox.imap_poller import poll_inbox
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        max_msg = int(body.get("max_messages", 30)) if isinstance(body, dict) else 30
        stats = poll_inbox(max_messages=max_msg)
        return {"ok": True, "stats": stats}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Resend — vérification domaine
# ---------------------------------------------------------------------------

@app.post("/api/admin/resend/verify-domain")
async def admin_resend_verify_domain(request: Request):
    """Demande à Resend de vérifier les DNS records du domaine. Utile après ajout des records."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        import os
        api_key = os.environ.get("RESEND_API_KEY", "")
        if not api_key:
            return JSONResponse({"ok": False, "error": "RESEND_API_KEY missing"}, status_code=500)
        import httpx
        r = httpx.get(
            "https://api.resend.com/domains",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )
        return {"ok": True, "status": r.status_code, "data": r.json()}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Starlette >= 0.28 requiert (request, name, context) au lieu de (name, context)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "agent_name": persona.NAME,
            "tagline": persona.TAGLINE,
            "bio": persona.SHORT_BIO,
            "version": persona.VERSION,
            "supabase_url": settings.supabase_url,
            "supabase_anon_key": settings.supabase_anon_key,
        },
    )


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.get("/api/state")
async def state():
    db = get_db()
    row = (db.table("agent_state").select("*")
           .eq("id", "00000000-0000-0000-0000-000000000001")
           .single().execute().data)
    return JSONResponse(row or {})


def _safe_count(table_name: str) -> int:
    """Count exact d'une table, retourne 0 si table absente ou erreur."""
    try:
        r = get_db().table(table_name).select("*", count="exact", head=True).execute()
        return r.count or 0
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("count %s failed: %s", table_name, e)
        return 0


@app.get("/api/stats")
async def stats():
    try:
        counts = count_prospects_by_status()
    except Exception:
        counts = {}
    return JSONResponse({
        "pipeline": counts,
        "totals": {
            "events": _safe_count("agent_events"),
            "alerts": _safe_count("alerts"),
            "conversations": _safe_count("conversations"),
            "prospects": sum(counts.values()),
        },
    })


@app.get("/api/recent-events")
async def recent_events(limit: int = 100):
    """Fallback si Supabase Realtime ne marche pas côté browser."""
    db = get_db()
    rows = (db.table("agent_events").select("*")
            .order("created_at", desc=True).limit(limit).execute().data) or []
    return JSONResponse(rows)


@app.get("/api/pipeline")
async def pipeline():
    db = get_db()
    rows = (db.table("prospects").select(
        "id,name,city,sector_normalized,score,status,has_website,email,updated_at"
    ).order("score", desc=True).limit(200).execute().data) or []
    # Groupé par statut pour le kanban
    grouped: dict[str, list] = {}
    for r in rows:
        grouped.setdefault(r["status"], []).append(r)
    return JSONResponse(grouped)


@app.get("/api/recent-conversations")
async def recent_conversations(limit: int = 20):
    db = get_db()
    rows = (db.table("conversations").select("*")
            .order("sent_at", desc=True).limit(limit).execute().data) or []
    return JSONResponse(rows)


@app.get("/api/recent-tool-calls")
async def recent_tool_calls(limit: int = 30):
    """Derniers appels de tools NOVA (claude.score, query_supabase, resend.send, etc.)."""
    db = get_db()
    rows = (db.table("tool_calls").select("*")
            .order("created_at", desc=True).limit(min(limit, 200)).execute().data) or []
    return JSONResponse(rows)


@app.get("/api/recent-tasks")
async def recent_tasks(limit: int = 20):
    """Dernières tâches de la queue (pending / running / done / failed)."""
    db = get_db()
    rows = (db.table("tasks").select(
        "id,type,status,priority,reason,attempts,max_attempts,created_at,started_at,finished_at"
    ).order("created_at", desc=True).limit(min(limit, 100)).execute().data) or []
    return JSONResponse(rows)


@app.get("/api/persona")
async def persona_info():
    return JSONResponse({
        "name": persona.NAME,
        "tagline": persona.TAGLINE,
        "version": persona.VERSION,
        "bio": persona.SHORT_BIO,
        "moods": {k: {"label": m.label, "emoji": m.emoji, "color": m.color,
                      "description": m.description}
                  for k, m in persona.MOODS.items()},
    })


@app.get("/api/health")
async def health():
    try:
        get_db().table("agent_state").select("id").limit(1).execute()
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=503)
