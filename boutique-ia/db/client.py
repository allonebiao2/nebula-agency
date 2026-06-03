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
    "brand_color", "cod_enabled", "negotiation_enabled", "negotiation_rule",
    "auto_prospect_enabled", "auto_prospect_category", "auto_prospect_city",
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


def set_merchant_pin(merchant_id: str, pin_hash: str | None) -> dict[str, Any]:
    """Définit (ou réinitialise si None) le code d'accès du back-office."""
    db = get_db()
    result = (
        db.table("bia_merchants").update({"access_pin": pin_hash})
        .eq("id", merchant_id).execute()
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


def upload_product_photo(merchant_id: str, product_id: str, data: bytes,
                         content_type: str = "image/jpeg", ext: str = "jpg") -> str:
    """Upload une photo produit sur Supabase Storage (bucket public) + maj photo_url."""
    import time
    db = get_db()
    path = f"{merchant_id}/{product_id}.{ext}"
    opts = {"content-type": content_type or "image/jpeg", "upsert": "true"}
    try:
        db.storage.from_("bia-products").upload(path, data, opts)
    except Exception:  # noqa: BLE001 — déjà présent → on remplace
        db.storage.from_("bia-products").update(path, data, opts)
    url = db.storage.from_("bia-products").get_public_url(path).split("?")[0]
    url = f"{url}?v={int(time.time())}"  # cache-bust
    update_product(product_id, merchant_id, {"photo_url": url})
    return url


def list_products(merchant_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return (
        db.table("bia_products").select("*").eq("merchant_id", merchant_id).execute().data
        or []
    )


# ---------------------------------------------------------------------------
# Réglages dynamiques (bia_settings) — pilotables depuis l'admin, sans redéploiement
# ---------------------------------------------------------------------------

def get_setting(key: str, default: Any = None) -> Any:
    try:
        r = get_db().table("bia_settings").select("value").eq("key", key).limit(1).execute()
        return r.data[0]["value"] if r.data else default
    except Exception:  # noqa: BLE001
        return default


def set_setting(key: str, value: Any) -> None:
    get_db().table("bia_settings").upsert(
        {"key": key, "value": str(value), "updated_at": "now()"}, on_conflict="key"
    ).execute()


def get_setting_bool(key: str, default: bool) -> bool:
    v = get_setting(key)
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on", "oui")


def get_setting_int(key: str, default: int) -> int:
    try:
        return int(get_setting(key, default))
    except (TypeError, ValueError):
        return default


def list_all_merchants() -> list[dict[str, Any]]:
    """Toutes les boutiques, de la plus récente à la plus ancienne (admin étage 4)."""
    db = get_db()
    return (
        db.table("bia_merchants").select("*").order("created_at", desc=True).execute().data
        or []
    )


def _parse_dt(s: Any):
    from datetime import datetime
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def activate_merchant(merchant_id: str, days: int | None = None) -> dict[str, Any]:
    """Valide un paiement : active la boutique + prolonge l'abonnement de N jours.

    Renouvellement : on ajoute les jours à la date d'échéance en cours si elle
    est encore future, sinon à partir d'aujourd'hui.
    """
    from datetime import datetime, timedelta, timezone

    from config import settings
    days = days or settings.subscription_days
    now = datetime.now(timezone.utc)
    m = get_merchant(merchant_id) or {}
    cur_end = _parse_dt(m.get("period_end"))
    base = cur_end if (cur_end and cur_end > now) else now
    fields: dict[str, Any] = {
        "status": "active",
        "period_end": (base + timedelta(days=days)).isoformat(),
        "last_payment_at": now.isoformat(),
        "reminder_sent_for": None,
    }
    if not m.get("activated_at"):
        fields["activated_at"] = now.isoformat()
    db = get_db()
    result = db.table("bia_merchants").update(fields).eq("id", merchant_id).execute()
    return result.data[0] if result.data else {}


def subscription_active(merchant: dict[str, Any] | None) -> bool:
    """L'abonnement est-il valide MAINTENANT ? (statut active + échéance non dépassée)"""
    m = merchant or {}
    if m.get("status") != "active":
        return False
    end = _parse_dt(m.get("period_end"))
    if end is None:
        return True  # actif sans échéance (legacy) → toléré
    from datetime import datetime, timezone
    return end >= datetime.now(timezone.utc)


def days_left(merchant: dict[str, Any] | None) -> int | None:
    """Jours restants d'abonnement (None si pas d'échéance, négatif si expiré)."""
    end = _parse_dt((merchant or {}).get("period_end"))
    if end is None:
        return None
    from datetime import datetime, timezone
    secs = (end - datetime.now(timezone.utc)).total_seconds()
    import math
    return math.ceil(secs / 86400)  # >0 = jours restants, <=0 = expiré


def mark_reminder_sent(merchant_id: str, period_end: Any) -> None:
    """Mémorise qu'une relance a été envoyée pour cette échéance (anti-doublon)."""
    get_db().table("bia_merchants").update(
        {"reminder_sent_for": str(period_end)}
    ).eq("id", merchant_id).execute()


def set_merchant_status(merchant_id: str, status: str) -> dict[str, Any]:
    """Change le statut d'une boutique (ex: suspended / active / pending_payment)."""
    db = get_db()
    result = (
        db.table("bia_merchants").update({"status": status}).eq("id", merchant_id).execute()
    )
    return result.data[0] if result.data else {}


def all_orders_brief() -> list[dict[str, Any]]:
    """Toutes les commandes (champs légers) pour agrégation admin."""
    db = get_db()
    return (
        db.table("bia_orders").select("merchant_id, total, status, created_at").execute().data
        or []
    )


def all_products_brief() -> list[dict[str, Any]]:
    """Tous les produits (id + merchant) pour comptage admin."""
    db = get_db()
    return db.table("bia_products").select("id, merchant_id").execute().data or []


# ---------------------------------------------------------------------------
# Prospection (bia_campaigns / bia_prospects) — étage 5
# ---------------------------------------------------------------------------

def create_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    db = get_db()
    r = db.table("bia_campaigns").insert(payload).execute()
    return r.data[0] if r.data else {}


def update_campaign(campaign_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    db = get_db()
    r = db.table("bia_campaigns").update(fields).eq("id", campaign_id).execute()
    return r.data[0] if r.data else {}


def get_campaign(campaign_id: str) -> dict[str, Any] | None:
    db = get_db()
    r = db.table("bia_campaigns").select("*").eq("id", campaign_id).limit(1).execute()
    return r.data[0] if r.data else None


def list_campaigns(owner_type: str, merchant_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    db = get_db()
    q = db.table("bia_campaigns").select("*").eq("owner_type", owner_type)
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.order("created_at", desc=True).limit(limit).execute().data or []


def add_prospects(campaign_id: str, merchant_id: str | None, owner_type: str,
                  prospects: list[dict[str, Any]]) -> int:
    """Insère les prospects d'une campagne. Dédup sur l'email DANS la campagne."""
    seen, rows = set(), []
    for p in prospects:
        email = (p.get("email") or "").strip().lower()
        if not email or email in seen:
            continue
        seen.add(email)
        rows.append({
            "campaign_id": campaign_id, "merchant_id": merchant_id, "owner_type": owner_type,
            "name": p.get("name"), "sector": p.get("sector"), "city": p.get("city"),
            "country": p.get("country"), "website": p.get("website"),
            "email": email, "phone": p.get("phone"),
            "source_external_id": p.get("source_external_id"), "status": "new",
        })
    if not rows:
        return 0
    return len(get_db().table("bia_prospects").insert(rows).execute().data or [])


def list_prospects(campaign_id: str, limit: int = 200) -> list[dict[str, Any]]:
    db = get_db()
    return (
        db.table("bia_prospects").select("*").eq("campaign_id", campaign_id)
        .order("created_at").limit(limit).execute().data or []
    )


def mark_prospect(prospect_id: str, status: str, error: str | None = None,
                  sent_at: str | None = None) -> None:
    fields: dict[str, Any] = {"status": status}
    if error is not None:
        fields["error"] = error[:300]
    if sent_at is not None:
        fields["sent_at"] = sent_at
    get_db().table("bia_prospects").update(fields).eq("id", prospect_id).execute()


def _today_start_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")


def count_prospection_sent_today(owner_type: str, merchant_id: str | None = None) -> int:
    db = get_db()
    q = (db.table("bia_prospects").select("id", count="exact", head=True)
         .eq("status", "sent").gte("sent_at", _today_start_iso()).eq("owner_type", owner_type))
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().count or 0


def count_prospection_sent_today_global() -> int:
    """Tous les envois du jour (sécurité plafond Gmail)."""
    db = get_db()
    r = (db.table("bia_prospects").select("id", count="exact", head=True)
         .eq("status", "sent").gte("sent_at", _today_start_iso()).execute())
    return r.count or 0


def email_already_contacted(owner_type: str, merchant_id: str | None, email: str) -> bool:
    """Cet email a-t-il déjà été contacté (ou blacklisté) par ce propriétaire ?"""
    db = get_db()
    q = (db.table("bia_prospects").select("id", count="exact", head=True)
         .eq("owner_type", owner_type).eq("email", (email or "").strip().lower())
         .in_("status", ["sent", "blacklisted"]))
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return (q.execute().count or 0) > 0


# ---------------------------------------------------------------------------
# Opt-out / désinscription (bia_optouts) — étage 4 (réponses entrantes)
# ---------------------------------------------------------------------------

def add_optout(contact: str, channel: str, reason: str = "manual") -> None:
    contact = (contact or "").strip().lower()
    if not contact:
        return
    get_db().table("bia_optouts").upsert(
        {"contact": contact, "channel": channel, "reason": reason},
        on_conflict="contact",
    ).execute()


def is_opted_out(contact: str) -> bool:
    contact = (contact or "").strip().lower()
    if not contact:
        return False
    r = (
        get_db().table("bia_optouts").select("contact", count="exact", head=True)
        .eq("contact", contact).execute()
    )
    return (r.count or 0) > 0


def blacklist_prospect_email(email: str, reason: str = "bounce") -> int:
    """Marque tous les prospects ayant cet email comme blacklistés (+ opt-out)."""
    email = (email or "").strip().lower()
    if not email:
        return 0
    add_optout(email, "email", reason)
    r = (
        get_db().table("bia_prospects").update({"status": "blacklisted", "error": reason})
        .eq("email", email).execute()
    )
    return len(r.data or [])


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
    payment_method: str | None = None,
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
            "payment_method": payment_method,
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


# ---------------------------------------------------------------------------
# Cerveau d'apprentissage (auto-amélioration) — bia_lessons
# ---------------------------------------------------------------------------

def _window_iso(days: int) -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def recent_messages(days: int, merchant_id: str | None = None,
                    limit: int = 4000) -> list[dict[str, Any]]:
    """Messages des N derniers jours (toutes boutiques ou une seule), du + ancien au + récent."""
    db = get_db()
    q = (
        db.table("bia_messages")
        .select("merchant_id, customer_whatsapp, role, content, created_at")
        .gte("created_at", _window_iso(days))
    )
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    rows = q.order("created_at", desc=False).limit(limit).execute().data or []
    return rows


def recent_orders(days: int, merchant_id: str | None = None) -> list[dict[str, Any]]:
    """Commandes des N derniers jours (pour croiser conversations conclues vs perdues)."""
    db = get_db()
    q = (
        db.table("bia_orders")
        .select("merchant_id, customer_whatsapp, total, status, created_at")
        .gte("created_at", _window_iso(days))
    )
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().data or []


def save_lessons(scope: str, merchant_id: str | None, lessons: str,
                 stats: dict[str, Any] | None = None, model: str | None = None) -> dict[str, Any]:
    """Enregistre une nouvelle synthèse de leçons (on garde l'historique, on lit la + récente)."""
    db = get_db()
    row = {
        "scope": scope,
        "merchant_id": merchant_id,
        "lessons": lessons,
        "stats": stats or {},
        "model": model,
    }
    r = db.table("bia_lessons").insert(row).execute()
    _LESSON_CACHE.clear()
    return r.data[0] if r.data else {}


def get_latest_lessons(scope: str = "global",
                       merchant_id: str | None = None) -> dict[str, Any] | None:
    """Dernière synthèse de leçons pour un scope donné."""
    db = get_db()
    q = db.table("bia_lessons").select("*").eq("scope", scope)
    if scope == "merchant" and merchant_id:
        q = q.eq("merchant_id", merchant_id)
    r = q.order("created_at", desc=True).limit(1).execute()
    return r.data[0] if r.data else None


# Petit cache mémoire (le webhook WhatsApp lit les leçons à CHAQUE message ;
# on évite une requête DB à chaque fois). TTL court — les leçons changent ~1×/semaine.
_LESSON_CACHE: dict[str, tuple[float, str]] = {}
_LESSON_TTL = 600.0  # secondes


def get_active_lessons(merchant_id: str | None = None) -> str:
    """Texte des leçons à injecter dans le prompt du vendeur (global + boutique). Caché."""
    import time as _time
    key = merchant_id or "_global"
    hit = _LESSON_CACHE.get(key)
    if hit and (_time.time() - hit[0]) < _LESSON_TTL:
        return hit[1]
    parts: list[str] = []
    try:
        g = get_latest_lessons("global")
        if g and (g.get("lessons") or "").strip():
            parts.append(g["lessons"].strip())
    except Exception:  # noqa: BLE001
        pass
    if merchant_id:
        try:
            m = get_latest_lessons("merchant", merchant_id)
            if m and (m.get("lessons") or "").strip():
                parts.append("Spécifique à ta boutique :\n" + m["lessons"].strip())
        except Exception:  # noqa: BLE001
            pass
    text = "\n\n".join(parts)
    _LESSON_CACHE[key] = (_time.time(), text)
    return text
