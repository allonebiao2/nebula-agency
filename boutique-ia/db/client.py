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


# Champs de la fiche que le commerçant peut modifier lui-même (back-office).
# On EXCLUT volontairement : id, code, plan, status, activation_ref (facturation/sécurité).
EDITABLE_MERCHANT_FIELDS = {
    "business_name", "sector", "description", "city", "country",
    "whatsapp_business", "owner_whatsapp", "owner_email",
    "momo_number", "momo_name", "momo_network",
    "delivery_zones", "delivery_fee_info",
    "ai_tone", "languages", "business_hours", "policies", "extra_info",
    "brand_color",
}
EDITABLE_PRODUCT_FIELDS = {"name", "price", "description", "photo_url", "available",
                          "kind", "duration", "options"}


def update_merchant(merchant_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Met à jour la fiche d'une boutique (champs autorisés uniquement)."""
    clean = {k: v for k, v in fields.items() if k in EDITABLE_MERCHANT_FIELDS}
    if not clean:
        return get_merchant(merchant_id) or {}
    db = get_db()
    result = (
        db.table("bia_merchants").update(clean).eq("id", merchant_id).execute()
    )
    return result.data[0] if result.data else {}


def update_product(product_id: str, merchant_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Met à jour un produit (scopé à sa boutique pour la sécurité)."""
    clean = {k: v for k, v in fields.items() if k in EDITABLE_PRODUCT_FIELDS}
    if not clean:
        return {}
    db = get_db()
    result = (
        db.table("bia_products").update(clean)
        .eq("id", product_id).eq("merchant_id", merchant_id).execute()
    )
    return result.data[0] if result.data else {}


def delete_product(product_id: str, merchant_id: str) -> bool:
    """Supprime un produit (scopé à sa boutique)."""
    db = get_db()
    result = (
        db.table("bia_products").delete()
        .eq("id", product_id).eq("merchant_id", merchant_id).execute()
    )
    return bool(result.data)


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
            "kind": (p.get("kind") or "").strip() or None,
            "duration": (p.get("duration") or "").strip() or None,
            "options": (p.get("options") or "").strip() or None,
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


def count_manager_orders_today(merchant_id: str) -> int:
    """Nb d'ordres donnés aujourd'hui (UTC) — pour le quota journalier du forfait."""
    from datetime import datetime, timezone
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
    r = (
        get_db().table("bia_manager_commands")
        .select("id", count="exact", head=True)
        .eq("merchant_id", merchant_id)
        .gte("created_at", start)
        .execute()
    )
    return r.count or 0


def log_manager_order(merchant_id: str, command: str, reply: str) -> None:
    get_db().table("bia_manager_commands").insert({
        "merchant_id": merchant_id, "command": command, "reply": reply,
    }).execute()


def order_stats(merchant_id: str) -> dict[str, Any]:
    """Nb de commandes + total des ventes (pour le tableau de bord)."""
    rows = (
        get_db().table("bia_orders").select("total")
        .eq("merchant_id", merchant_id).execute().data or []
    )
    total = 0.0
    for r in rows:
        try:
            total += float(r.get("total") or 0)
        except (TypeError, ValueError):
            pass
    return {"count": len(rows), "revenue": total}


def list_recent_conversations(merchant_id: str, limit: int = 8) -> list[dict[str, Any]]:
    """Dernières conversations clients : 1 ligne par client (dernier message + nb)."""
    rows = (
        get_db().table("bia_messages")
        .select("customer_whatsapp, role, content, created_at")
        .eq("merchant_id", merchant_id)
        .order("created_at", desc=True)
        .limit(400)
        .execute()
        .data
        or []
    )
    convos: dict[str, dict[str, Any]] = {}
    for r in rows:
        cust = r.get("customer_whatsapp") or "?"
        c = convos.setdefault(cust, {"customer": cust, "count": 0, "last": None, "last_at": None})
        c["count"] += 1
        if c["last"] is None:  # rows déjà triées du + récent au + ancien
            c["last"] = r.get("content")
            c["last_role"] = r.get("role")
            c["last_at"] = r.get("created_at")
    return list(convos.values())[:limit]


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
