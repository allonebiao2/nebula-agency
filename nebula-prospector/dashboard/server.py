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
        _scheduler.start()
        import logging
        logging.getLogger("nova.scheduler").info(
            "[scheduler] APScheduler démarré : "
            "sourcing 3h UTC (4h Cotonou) + briefing 7h UTC (8h Cotonou)"
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
    """Force un cycle d'enrichissement seul (sans sourcing)."""
    if not _check_admin_token(request):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        from main import run_enrichment_pipeline
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        limit = body.get("limit", 25) if isinstance(body, dict) else 25
        stats = run_enrichment_pipeline(limit=limit, only_with_website=True)
        return {"ok": True, "stats": stats}
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
