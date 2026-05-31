"""Tools de NOVA — function calling Anthropic.

NOVA dispose de ces outils via l'API tools d'Anthropic. Claude peut les
appeler en multi-turn pour exécuter des actions concrètes : lire la
BDD, fetch un site, créer un document, envoyer une notif, etc.

Garde-fous légaux (cf skill autonomous-ceo-builder) :
- SQL exécuté en READ-ONLY uniquement (SELECT). Pas de DELETE/UPDATE/DROP
- URL fetch limité aux sites publics, respect robots.txt
- Envoi email passe par les rate limits existants
- Actions destructives notifiées à Mongazi
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from db.client import get_db

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DÉFINITIONS — schémas Anthropic des tools
# ---------------------------------------------------------------------------

TOOLS_SCHEMA: list[dict[str, Any]] = [
    {
        "name": "query_supabase",
        "description": (
            "Exécute une requête SQL SELECT en lecture seule sur la BDD Supabase. "
            "Utilise pour répondre à toute question chiffrée ou demande de liste. "
            "INTERDIT : DELETE / UPDATE / INSERT / DROP / ALTER — Claude refusera. "
            "Tables disponibles : prospects, conversations, alerts, sourcing_runs, "
            "agent_events, agent_state, nova_mission, nova_documents, tool_calls, tasks."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "Requête SQL SELECT à exécuter"},
                "limit": {"type": "integer", "description": "Limite max de rows retournées (default 20, max 100)", "default": 20}
            },
            "required": ["sql"]
        }
    },
    {
        "name": "fetch_url",
        "description": (
            "Récupère le contenu textuel d'une URL publique (homepage, /contact, /about). "
            "Utile pour analyser un prospect avant de lui écrire. Limité aux sites publics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL complète"},
                "max_chars": {"type": "integer", "description": "Longueur max retournée (default 2500)", "default": 2500}
            },
            "required": ["url"]
        }
    },
    {
        "name": "list_top_prospects",
        "description": "Liste les N premiers prospects d'un tier donné, triés par score décroissant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tier": {"type": "string", "enum": ["hot", "warm", "cold", "rejected"]},
                "limit": {"type": "integer", "default": 5},
                "city": {"type": "string", "description": "Filtre optionnel par ville"},
                "country": {"type": "string", "description": "Filtre optionnel par code pays (BJ, TG, etc.)"}
            },
            "required": ["tier"]
        }
    },
    {
        "name": "read_prospect",
        "description": "Récupère la fiche complète d'un prospect par son UUID.",
        "input_schema": {
            "type": "object",
            "properties": {"prospect_id": {"type": "string"}},
            "required": ["prospect_id"]
        }
    },
    {
        "name": "learn_skill",
        "description": (
            "Mémorise une nouvelle compétence/instruction que NOVA appliquera désormais. "
            "Utilise quand Mongazi dit 'apprends à...', 'à partir de maintenant...', "
            "'rappelle-toi que...'. Le skill est dans la mémoire long terme."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Slug court (sera préfixé 'skill-')"},
                "title": {"type": "string", "description": "Titre lisible"},
                "content": {"type": "string", "description": "Instructions détaillées"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []}
            },
            "required": ["key", "title", "content"]
        }
    },
    {
        "name": "create_document",
        "description": "Sauvegarde une information dans la mémoire long terme (non-skill).",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                "upsert": {"type": "boolean", "default": True}
            },
            "required": ["key", "title", "content"]
        }
    },
    {
        "name": "search_documents",
        "description": "Recherche dans la mémoire long terme par tag ou texte.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Filtre par tag exact"},
                "text_contains": {"type": "string", "description": "Filtre sur contenu (LIKE %x%)"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "update_mission",
        "description": (
            "Modifie la mission active de NOVA (versionnée). Toujours expliquer pourquoi. "
            "Utilise seulement quand Mongazi le demande explicitement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Nouvelle mission complète"},
                "reason": {"type": "string", "description": "Pourquoi ce changement"}
            },
            "required": ["content", "reason"]
        }
    },
    {
        "name": "create_task",
        "description": (
            "Crée une tâche dans la queue séquentielle. Sera exécutée par le worker loop. "
            "Types valides : sourcing.run, enrichment.run, outreach.run, document.create, "
            "document.update, mission.update, maintenance.archive_cold."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "payload": {"type": "object", "default": {}},
                "priority": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                "reason": {"type": "string"}
            },
            "required": ["type"]
        }
    },
    {
        "name": "notify_mongazi",
        "description": "Envoie un message Telegram supplémentaire à Mongazi (utile pour rapports longs / pièces jointes texte).",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Texte HTML (b, i, code, br supportés)"}
            },
            "required": ["message"]
        }
    },
    {
        "name": "generate_email_preview",
        "description": "Génère un cold email perso pour un prospect (sans envoyer) — utile pour tester avant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_id": {"type": "string"},
                "service_override": {"type": "string", "description": "Force un service (vitrine/catalogue/qr_menu/fiche_maps/qr_review/auto_whatsapp)"}
            },
            "required": ["prospect_id"]
        }
    },
]


# ---------------------------------------------------------------------------
# IMPLÉMENTATIONS
# ---------------------------------------------------------------------------

_FORBIDDEN_SQL = re.compile(
    r"\b(DELETE|UPDATE|INSERT|DROP|ALTER|TRUNCATE|GRANT|REVOKE|CREATE)\b",
    re.IGNORECASE,
)


def _exec_query_supabase(sql: str, limit: int = 20) -> dict[str, Any]:
    """Exécute un SELECT via la RPC Supabase execute_readonly_select."""
    if _FORBIDDEN_SQL.search(sql):
        return {"error": "Mutation SQL interdite (DELETE/UPDATE/INSERT/DROP/ALTER/CREATE)."}
    if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
        return {"error": "Seules les requêtes SELECT/WITH sont autorisées."}

    limit = max(1, min(limit, 100))
    try:
        db = get_db()
        result = db.rpc("execute_readonly_select", {"q": sql, "max_rows": limit}).execute()
        rows = result.data or []
        # rows peut être directement une liste ou une str JSON selon la version de supabase-py
        if isinstance(rows, str):
            import json as _json
            try:
                rows = _json.loads(rows)
            except Exception:
                pass
        if not isinstance(rows, list):
            rows = []
        return {"rows": rows, "count": len(rows)}
    except Exception as e:
        return {"error": f"SQL error: {str(e)[:300]}"}


def _exec_fetch_url(url: str, max_chars: int = 2500) -> dict[str, Any]:
    """Fetch une URL publique et retourne le texte nettoyé."""
    try:
        from enrichment.website_scraper import get_site_summary
        text = get_site_summary(url, max_chars=max_chars)
        if not text:
            return {"error": "Pas de contenu récupéré"}
        return {"url": url, "content": text}
    except Exception as e:
        return {"error": str(e)[:200]}


def _exec_list_top_prospects(tier: str, limit: int = 5, city: str | None = None, country: str | None = None) -> dict[str, Any]:
    db = get_db()
    q = (
        db.table("prospects")
        .select("id, name, sector, city, country, score, recommended_service, email, website, status")
        .eq("tier", tier)
        .order("score", desc=True)
        .order("updated_at", desc=True)
        .limit(max(1, min(limit, 20)))
    )
    if city:
        q = q.eq("city", city)
    if country:
        q = q.eq("country", country.upper())
    r = q.execute()
    return {"prospects": r.data or [], "count": len(r.data or [])}


def _exec_read_prospect(prospect_id: str) -> dict[str, Any]:
    db = get_db()
    r = db.table("prospects").select("*").eq("id", prospect_id).limit(1).execute()
    p = (r.data or [None])[0]
    if not p:
        return {"error": "prospect not found"}
    return {"prospect": p}


def _exec_learn_skill(key: str, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
    from core.documents import create_document
    if not key.startswith("skill-"):
        key = f"skill-{key}"
    final_tags = list(set((tags or []) + ["skill"]))
    doc = create_document(
        key=key,
        title=title,
        content=content,
        tags=final_tags,
        created_by="nova-learned-from-mongazi",
        upsert=True,
    )
    return {"ok": True, "skill_key": doc.get("key"), "title": doc.get("title")}


def _exec_create_document(key: str, title: str, content: str, tags: list[str] | None = None, upsert: bool = True) -> dict[str, Any]:
    from core.documents import create_document
    doc = create_document(key=key, title=title, content=content, tags=tags or [], upsert=upsert)
    return {"ok": True, "key": doc.get("key")}


def _exec_search_documents(tag: str | None = None, text_contains: str | None = None, limit: int = 10) -> dict[str, Any]:
    from core.documents import search_documents
    docs = search_documents(tag=tag, text_contains=text_contains, limit=limit)
    return {"documents": docs, "count": len(docs)}


def _exec_update_mission(content: str, reason: str) -> dict[str, Any]:
    from core.mission import update_mission
    rec = update_mission(new_content=content, reason=reason, edited_by="nova-via-chat")
    return {"ok": True, "version": rec.get("version")}


def _exec_create_task(type_: str, payload: dict | None = None, priority: int = 5, reason: str | None = None) -> dict[str, Any]:
    from core.tasks import create_task, list_handlers
    if type_ not in list_handlers():
        return {"error": f"type inconnu : {type_}. Disponibles : {list_handlers()}"}
    t = create_task(
        task_type=type_,
        payload=payload or {},
        priority=priority,
        reason=reason,
        created_by="nova-via-chat",
    )
    return {"ok": True, "task_id": t.get("id")}


def _exec_notify_mongazi(message: str) -> dict[str, Any]:
    from alerts.telegram_bot import send_message
    r = send_message(message, silent=True)
    return {"ok": r is not None}


def _exec_generate_email_preview(prospect_id: str, service_override: str | None = None) -> dict[str, Any]:
    from messaging.templates import generate_cold_email
    from enrichment.website_scraper import get_site_summary
    p = _exec_read_prospect(prospect_id).get("prospect")
    if not p:
        return {"error": "prospect not found"}
    site_content = get_site_summary(p.get("website") or "") if p.get("website") else ""
    result = generate_cold_email(p, site_content, service=service_override)
    return result


# ---------------------------------------------------------------------------
# DISPATCHER
# ---------------------------------------------------------------------------

_DISPATCH = {
    "query_supabase": lambda i: _exec_query_supabase(i.get("sql", ""), i.get("limit", 20)),
    "fetch_url": lambda i: _exec_fetch_url(i.get("url", ""), i.get("max_chars", 2500)),
    "list_top_prospects": lambda i: _exec_list_top_prospects(
        i.get("tier"), i.get("limit", 5), i.get("city"), i.get("country")
    ),
    "read_prospect": lambda i: _exec_read_prospect(i.get("prospect_id", "")),
    "learn_skill": lambda i: _exec_learn_skill(
        i.get("key", ""), i.get("title", ""), i.get("content", ""), i.get("tags", [])
    ),
    "create_document": lambda i: _exec_create_document(
        i.get("key", ""), i.get("title", ""), i.get("content", ""), i.get("tags", []), i.get("upsert", True)
    ),
    "search_documents": lambda i: _exec_search_documents(
        i.get("tag"), i.get("text_contains"), i.get("limit", 10)
    ),
    "update_mission": lambda i: _exec_update_mission(i.get("content", ""), i.get("reason", "")),
    "create_task": lambda i: _exec_create_task(
        i.get("type", ""), i.get("payload", {}), i.get("priority", 5), i.get("reason")
    ),
    "notify_mongazi": lambda i: _exec_notify_mongazi(i.get("message", "")),
    "generate_email_preview": lambda i: _exec_generate_email_preview(
        i.get("prospect_id", ""), i.get("service_override")
    ),
}


def execute_tool(name: str, input_: dict[str, Any]) -> dict[str, Any]:
    """Dispatcher principal. Retourne un dict sérialisable JSON."""
    handler = _DISPATCH.get(name)
    if not handler:
        return {"error": f"unknown tool: {name}"}
    try:
        log.info(f"[nova-tool] {name}({str(input_)[:120]})")
        return handler(input_)
    except Exception as e:
        log.exception(f"[nova-tool] {name} failed: {e}")
        return {"error": str(e)[:300]}
