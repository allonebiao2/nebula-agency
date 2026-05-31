"""Mémoire long terme de NOVA (inspiré NanoCorp `create_document` / `read_document`).

Au lieu de stocker dans le prompt, NOVA stocke ses connaissances dans une
table `nova_documents` qu'elle peut consulter à la demande. Économise des
tokens et permet une mémoire persistante illimitée.

Patterns d'usage :
- Référence statique : catalog-nebula, ideal-customer, clients-existants (seedés)
- Apprentissage : NOVA crée/met à jour quand elle observe quelque chose
  (ex : "secteur:restaurant → taux de réponse 25%, à prioriser")
- Templates : versions de templates email qui marchent

Usage :
    from core.documents import create_document, read_document, search_documents, update_document
    doc = read_document("catalog-nebula")
    create_document("learn-2026-05-31", title="Apprentissage du jour", content="...", tags=["learning"])
    matches = search_documents(tag="reference")
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from db.client import get_db

log = logging.getLogger(__name__)


def create_document(
    key: str,
    title: str,
    content: str,
    *,
    tags: list[str] | None = None,
    created_by: str = "nova",
    upsert: bool = False,
) -> dict[str, Any]:
    """Crée un document. `key` doit être unique (slug).

    Si `upsert=True` et que la key existe déjà → met à jour le contenu.
    """
    if not key or " " in key:
        raise ValueError("`key` doit être un slug sans espace")
    if not content or len(content.strip()) < 10:
        raise ValueError("Document trop court (min 10 caractères)")

    db = get_db()
    payload = {
        "key": key,
        "title": title[:200],
        "content": content.strip(),
        "tags": tags or [],
        "created_by": created_by,
    }
    if upsert:
        r = db.table("nova_documents").upsert(payload, on_conflict="key").execute()
    else:
        r = db.table("nova_documents").insert(payload).execute()
    return (r.data or [{}])[0]


def read_document(key: str, *, track_access: bool = True) -> dict[str, Any] | None:
    """Lit un document par sa clé. Track les accès pour stats."""
    db = get_db()
    r = (
        db.table("nova_documents")
        .select("*")
        .eq("key", key)
        .limit(1)
        .execute()
    )
    doc = (r.data or [None])[0]
    if doc and track_access:
        try:
            db.table("nova_documents").update({
                "access_count": (doc.get("access_count") or 0) + 1,
                "last_accessed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", doc["id"]).execute()
        except Exception as e:
            log.debug(f"access tracking failed: {e}")
    return doc


def update_document(
    key: str,
    *,
    content: str | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any] | None:
    """Met à jour un document existant. Champs non fournis = inchangés."""
    db = get_db()
    update: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if content is not None:
        update["content"] = content.strip()
    if title is not None:
        update["title"] = title[:200]
    if tags is not None:
        update["tags"] = tags
    if len(update) == 1:  # juste updated_at
        return None
    r = db.table("nova_documents").update(update).eq("key", key).execute()
    return (r.data or [None])[0]


def delete_document(key: str) -> bool:
    """Supprime un document. Retourne True si quelque chose a été supprimé."""
    db = get_db()
    r = db.table("nova_documents").delete().eq("key", key).execute()
    return bool(r.data)


def search_documents(
    *,
    tag: str | None = None,
    tags_any: list[str] | None = None,
    text_contains: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Recherche des documents. Filtres : tag exact, tags_any (OR), full-text."""
    db = get_db()
    q = db.table("nova_documents").select("*").order("updated_at", desc=True).limit(limit)
    if tag:
        q = q.contains("tags", [tag])
    if tags_any:
        q = q.overlaps("tags", tags_any)
    if text_contains:
        q = q.ilike("content", f"%{text_contains}%")
    r = q.execute()
    return r.data or []


def list_documents(limit: int = 50) -> list[dict[str, Any]]:
    """Liste tous les documents (titre + key + tags, sans le contenu)."""
    db = get_db()
    r = (
        db.table("nova_documents")
        .select("key, title, tags, created_by, updated_at, access_count")
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []
