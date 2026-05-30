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
