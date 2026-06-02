"""Client Supabase + helpers boutiques/produits (étage 1)."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from config import settings


@lru_cache
def get_db() -> Client:
    settings.require("supabase_url", "supabase_service_role_key")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# ---------------------------------------------------------------------------
# Boutiques (merchants)
# ---------------------------------------------------------------------------

def create_merchant(payload: dict[str, Any]) -> dict[str, Any]:
    """Crée une boutique en statut pending_payment. Retourne la ligne créée."""
    db = get_db()
    result = db.table("bia_merchants").insert(payload).execute()
    return result.data[0] if result.data else {}


def get_merchant_by_code(code: str) -> dict[str, Any] | None:
    """Retrouve une boutique par son code court (routing WhatsApp)."""
    db = get_db()
    result = (
        db.table("bia_merchants").select("*").eq("code", code).limit(1).execute()
    )
    return result.data[0] if result.data else None


def get_merchant(merchant_id: str) -> dict[str, Any] | None:
    db = get_db()
    result = (
        db.table("bia_merchants").select("*").eq("id", merchant_id).limit(1).execute()
    )
    return result.data[0] if result.data else None


def set_merchant_payment_ref(merchant_id: str, ref: str) -> dict[str, Any]:
    """Le commerçant a soumis sa référence MoMo → en attente de validation."""
    db = get_db()
    result = (
        db.table("bia_merchants")
        .update({"activation_ref": ref, "status": "paid_pending_validation"})
        .eq("id", merchant_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def add_products(merchant_id: str, products: list[dict[str, Any]]) -> int:
    """Insère les produits d'une boutique. Retourne le nombre inséré."""
    rows = []
    for p in products:
        name = (p.get("name") or "").strip()
        if not name:
            continue
        rows.append({
            "merchant_id": merchant_id,
            "name": name,
            "price": p.get("price"),
            "description": (p.get("description") or "").strip() or None,
            "photo_url": (p.get("photo_url") or "").strip() or None,
        })
    if not rows:
        return 0
    db = get_db()
    result = db.table("bia_products").insert(rows).execute()
    return len(result.data or [])


def list_products(merchant_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return (
        db.table("bia_products").select("*").eq("merchant_id", merchant_id).execute().data
        or []
    )


def get_latest_merchant() -> dict[str, Any] | None:
    """Dernière boutique inscrite — pratique pour les tests sur le sandbox WhatsApp."""
    db = get_db()
    result = (
        db.table("bia_merchants").select("*").order("created_at", desc=True).limit(1).execute()
    )
    return result.data[0] if result.data else None


# ---------------------------------------------------------------------------
# Mémoire des conversations (bia_messages)
# ---------------------------------------------------------------------------

def save_message(merchant_id: str, customer: str, role: str, content: str) -> None:
    """role = 'customer' ou 'assistant'."""
    db = get_db()
    db.table("bia_messages").insert({
        "merchant_id": merchant_id,
        "customer_whatsapp": customer,
        "role": role,
        "content": content,
    }).execute()


def count_customer_messages(merchant_id: str, customer: str) -> int:
    """Nombre de messages envoyés par le client (pour la limite d'essai gratuit)."""
    db = get_db()
    r = (
        db.table("bia_messages")
        .select("id", count="exact", head=True)
        .eq("merchant_id", merchant_id)
        .eq("customer_whatsapp", customer)
        .eq("role", "customer")
        .execute()
    )
    return r.count or 0


def upsert_wa_session(customer: str, merchant_id: str) -> None:
    """Mémorise quelle boutique ce client WhatsApp est en train de contacter."""
    db = get_db()
    db.table("bia_wa_sessions").upsert(
        {"customer_whatsapp": customer, "merchant_id": merchant_id, "updated_at": "now()"},
        on_conflict="customer_whatsapp",
    ).execute()


def get_wa_session_merchant_id(customer: str) -> str | None:
    db = get_db()
    result = (
        db.table("bia_wa_sessions").select("merchant_id")
        .eq("customer_whatsapp", customer).limit(1).execute()
    )
    return result.data[0]["merchant_id"] if result.data else None


# ---------------------------------------------------------------------------
# Commandes (bia_orders) — étage 3
# ---------------------------------------------------------------------------

def create_order(
    merchant_id: str,
    customer_whatsapp: str | None,
    items: list[dict[str, Any]],
    total: Any,
    delivery_mode: str | None = None,
    delivery_address: str | None = None,
    customer_name: str | None = None,
    status: str = "pending",
) -> dict[str, Any]:
    """Enregistre une commande conclue par le vendeur IA. Retourne la ligne créée."""
    db = get_db()
    result = (
        db.table("bia_orders")
        .insert({
            "merchant_id": merchant_id,
            "customer_whatsapp": customer_whatsapp,
            "customer_name": customer_name,
            "items": items,
            "total": total,
            "delivery_mode": delivery_mode,
            "delivery_address": delivery_address,
            "status": status,
        })
        .execute()
    )
    return result.data[0] if result.data else {}


def list_orders(merchant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Commandes d'une boutique, de la plus récente à la plus ancienne (admin étage 4)."""
    db = get_db()
    return (
        db.table("bia_orders")
        .select("*")
        .eq("merchant_id", merchant_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
        or []
    )


def load_history(merchant_id: str, customer: str, limit: int = 20) -> list[dict[str, Any]]:
    """Derniers messages d'une conversation, du plus ancien au plus récent."""
    db = get_db()
    rows = (
        db.table("bia_messages")
        .select("role, content, created_at")
        .eq("merchant_id", merchant_id)
        .eq("customer_whatsapp", customer)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
        or []
    )
    return list(reversed(rows))
