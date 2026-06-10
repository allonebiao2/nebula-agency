"""Client Supabase + helpers boutiques/produits (étage 1)."""
from __future__ import annotations

import json
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
    if not result.data:
        return None
    m = result.data[0]
    m["payment_accounts"] = _payment_accounts(m.get("id"))
    return m


def get_merchant(merchant_id: str) -> dict[str, Any] | None:
    db = get_db()
    result = (
        db.table("bia_merchants").select("*").eq("id", merchant_id).limit(1).execute()
    )
    if not result.data:
        return None
    m = result.data[0]
    m["payment_accounts"] = _payment_accounts(m.get("id"))
    return m


def _payment_accounts(merchant_id) -> list[dict[str, Any]]:
    """Comptes Mobile Money additionnels d'une boutique (réseau + numéro + nom).

    Stockés dans `bia_settings` (clé `pay_accounts_{id}`) → aucune migration. L'agent
    s'en sert pour donner au client le compte de SON réseau (évite les frais inter-réseaux).
    """
    try:
        raw = get_setting(f"pay_accounts_{merchant_id}")
        if raw:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, list):
                return [a for a in data if isinstance(a, dict) and a.get("number")]
    except Exception:  # noqa: BLE001
        pass
    return []


def save_payment_accounts(merchant_id: str, accounts: list) -> list[dict[str, Any]]:
    """Valide + enregistre la liste de comptes (max 8). Renvoie la liste nettoyée."""
    clean: list[dict[str, Any]] = []
    for a in (accounts or [])[:8]:
        if not isinstance(a, dict):
            continue
        num = str(a.get("number") or "").strip()
        if not num:
            continue
        clean.append({"network": str(a.get("network") or "").strip()[:40],
                      "number": num[:40],
                      "name": str(a.get("name") or "").strip()[:80]})
    set_setting(f"pay_accounts_{merchant_id}", json.dumps(clean))
    return clean


# Mots vides ignorés quand un client écrit une phrase au lieu du seul nom.
_NAME_STOPWORDS = {
    "bonjour", "bonsoir", "salut", "coucou", "hello", "hi", "slt", "cc",
    "la", "le", "les", "boutique", "magasin", "chez", "pour", "avec",
    "je", "jai", "cherche", "veux", "voudrais", "aimerais", "svp", "stp",
    "merci", "est", "cest", "ce", "the", "shop", "store", "de", "du", "des",
    "un", "une", "et", "ou", "vendora", "infos", "info", "information",
}


def find_merchant_by_name(text: str, limit: int = 4) -> list[dict[str, Any]]:
    """Filet de routage WhatsApp : retrouve la/les boutique(s) ACTIVE(s) dont le nom
    correspond au texte du client, quand il n'y a NI code `vendora:` NI session
    (client qui a écrit au numéro brut sans passer par le lien). Insensible à la
    casse et aux accents. Retourne 0 (rien), 1 (match sûr → on route direct) ou
    plusieurs (ambigu → on demande de préciser)."""
    import re
    import unicodedata

    def norm(s: str) -> str:
        s = (s or "").lower().strip()
        s = "".join(c for c in unicodedata.normalize("NFD", s)
                    if unicodedata.category(c) != "Mn")
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    nt = norm(text)
    if len(nt) < 3:
        return []
    nt_tokens = {t for t in nt.split() if t not in _NAME_STOPWORDS and len(t) > 1}
    if not nt_tokens:
        return []  # ex. juste « Bonjour » → on n'a aucun indice de boutique

    try:
        db = get_db()
        rows = (db.table("bia_merchants")
                .select("id,business_name,code,status")
                .eq("status", "active").limit(400).execute().data or [])
    except Exception:
        return []

    scored: list[tuple[int, dict[str, Any]]] = []
    for m in rows:
        nn = norm(m.get("business_name") or "")
        if len(nn) < 2:
            continue
        nn_tokens = {t for t in nn.split() if len(t) > 1}
        if nt == nn:
            score = 100
        elif nn in nt:                       # le nom complet apparaît dans la phrase
            score = 80
        elif len(nt) >= 4 and nt in nn:      # le client a tapé un bout du nom
            score = 60
        else:
            common = nt_tokens & nn_tokens
            score = (30 + 10 * len(common)
                     if common and len(common) >= max(1, len(nn_tokens) // 2) else 0)
        if score:
            scored.append((score, {"id": m["id"],
                                   "business_name": m.get("business_name"),
                                   "code": m.get("code")}))

    if not scored:
        return []
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][0]
    # Un match domine nettement les autres → routage sûr, on ne renvoie que lui.
    if top >= 60 and (len(scored) == 1 or scored[1][0] <= top - 30):
        return [scored[0][1]]
    return [d for _, d in scored[:limit]]


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
    "rdv_days", "rdv_hours", "rdv_note",
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


def create_appointment(merchant_id: str, customer_whatsapp: str | None, *,
                       service: str | None = None, requested_time: str | None = None,
                       customer_name: str | None = None,
                       note: str | None = None) -> dict[str, Any]:
    """Enregistre une demande de rendez-vous (statut pending)."""
    db = get_db()
    row = {"merchant_id": merchant_id, "customer_whatsapp": customer_whatsapp,
           "service": service, "requested_time": requested_time,
           "customer_name": customer_name, "note": note, "status": "pending"}
    result = db.table("bia_appointments").insert(row).execute()
    return result.data[0] if result.data else {}


def list_appointments(merchant_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """Derniers rendez-vous d'une boutique (plus récents d'abord)."""
    db = get_db()
    result = (
        db.table("bia_appointments").select("*").eq("merchant_id", merchant_id)
        .order("created_at", desc=True).limit(limit).execute()
    )
    return result.data or []


def save_coaching(merchant_id: str, advice: str, snapshot: dict[str, Any]) -> None:
    """Enregistre le dernier conseil du coach commercial (+ snapshot chiffré)."""
    import json as _json
    get_db().table("bia_coaching").insert(
        {"merchant_id": merchant_id, "advice": advice,
         "snapshot": _json.dumps(snapshot, ensure_ascii=False)}
    ).execute()


def get_latest_coaching(merchant_id: str) -> dict[str, Any] | None:
    """Dernier conseil du coach pour une boutique (None si aucun)."""
    import json as _json
    try:
        r = (get_db().table("bia_coaching").select("advice,snapshot,created_at")
             .eq("merchant_id", merchant_id).order("created_at", desc=True).limit(1).execute())
        if r.data:
            row = r.data[0]
            snap = {}
            try:
                snap = _json.loads(row.get("snapshot") or "{}")
            except Exception:  # noqa: BLE001
                snap = {}
            return {"advice": row.get("advice") or "", "snapshot": snap,
                    "created_at": row.get("created_at")}
    except Exception:  # noqa: BLE001
        pass
    return None


def save_social_posts(merchant_id: str, posts: list[dict[str, Any]]) -> None:
    """Enregistre un lot de brouillons de posts réseaux sociaux (Vendora Social)."""
    import json as _json
    get_db().table("bia_social_posts").insert(
        {"merchant_id": merchant_id, "posts": _json.dumps(posts, ensure_ascii=False)}
    ).execute()


def get_latest_social_posts(merchant_id: str) -> list[dict[str, Any]]:
    """Dernier lot de posts générés pour une boutique ([] si aucun)."""
    import json as _json
    try:
        r = (get_db().table("bia_social_posts").select("posts")
             .eq("merchant_id", merchant_id).order("created_at", desc=True)
             .limit(1).execute())
        if r.data and r.data[0].get("posts"):
            data = _json.loads(r.data[0]["posts"])
            return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        pass
    return []


def set_merchant_capabilities(merchant_id: str, caps_csv: str) -> dict[str, Any]:
    """Enregistre les capacités choisies (« Composez votre vendeur »).

    `caps_csv` = ids modules/premium séparés par virgule, DÉJÀ filtrés/plafonnés
    selon le forfait par l'appelant (core/capabilities). Le socle reste implicite.
    """
    db = get_db()
    result = (
        db.table("bia_merchants").update({"enabled_capabilities": caps_csv})
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


def upload_social_image(merchant_id: str, data: bytes) -> str:
    """Upload une image de post réseau social (PNG) sur Supabase Storage → URL publique."""
    import time
    db = get_db()
    path = f"{merchant_id}/social/{int(time.time() * 1000)}.png"
    opts = {"content-type": "image/png", "upsert": "true"}
    try:
        db.storage.from_("bia-products").upload(path, data, opts)
    except Exception:  # noqa: BLE001
        db.storage.from_("bia-products").update(path, data, opts)
    return db.storage.from_("bia-products").get_public_url(path).split("?")[0]


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


def list_settings_prefix(prefix: str) -> list[dict[str, Any]]:
    """Réglages dont la clé commence par `prefix` (ex: 'page_merchant_'). [] si KO."""
    try:
        r = (get_db().table("bia_settings").select("key,value")
             .like("key", f"{prefix}%").execute())
        return r.data or []
    except Exception:  # noqa: BLE001
        return []


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
        "is_trial": False,   # un paiement met fin à l'essai (devient payante)
        "period_end": (base + timedelta(days=days)).isoformat(),
        "last_payment_at": now.isoformat(),
        "reminder_sent_for": None,
    }
    if not m.get("activated_at"):
        fields["activated_at"] = now.isoformat()
    # Forfait flexible : un changement programmé (ex. downgrade) s'applique AU
    # renouvellement — le client a profité de son forfait payé jusqu'ici.
    pending = (m.get("pending_plan") or "").strip()
    if pending and pending != (m.get("plan") or ""):
        fields["plan"] = pending
        fields["pending_plan"] = None
    db = get_db()
    result = db.table("bia_merchants").update(fields).eq("id", merchant_id).execute()
    return result.data[0] if result.data else {}


def start_trial(merchant_id: str, days: int = 3) -> dict[str, Any]:
    """Démarre un essai gratuit : la boutique devient active mais NON payante.

    `is_trial=True` + `period_end = maintenant + days`. À l'échéance, le cycle de
    facturation la suspend automatiquement (données conservées, jamais supprimées).
    """
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    fields = {
        "status": "active",
        "is_trial": True,
        "period_end": (now + timedelta(days=days)).isoformat(),
        "reminder_sent_for": None,
    }
    m = get_merchant(merchant_id) or {}
    if not m.get("activated_at"):
        fields["activated_at"] = now.isoformat()
    db = get_db()
    result = db.table("bia_merchants").update(fields).eq("id", merchant_id).execute()
    return result.data[0] if result.data else {}


def trial_stats(merchant_id: str) -> dict[str, Any]:
    """Preuve de valeur de l'essai : {conversations, orders, revenue}."""
    stats = {"conversations": 0, "orders": 0, "revenue": 0}
    try:
        st = order_stats(merchant_id) or {}
        stats["orders"] = st.get("count", 0) or 0
        stats["revenue"] = st.get("revenue", 0) or 0
    except Exception:  # noqa: BLE001
        pass
    try:
        db = get_db()
        r = (db.table("bia_messages").select("customer_whatsapp")
             .eq("merchant_id", merchant_id).execute())
        stats["conversations"] = len({(row.get("customer_whatsapp") or "")
                                      for row in (r.data or []) if row.get("customer_whatsapp")})
    except Exception:  # noqa: BLE001
        pass
    return stats


def set_merchant_plan(merchant_id: str, plan: str, immediate: bool) -> dict[str, Any]:
    """Change le forfait d'une boutique.

    immediate=True  → applique TOUT DE SUITE (ex. upgrade payé).
    immediate=False → programme le changement au PROCHAIN renouvellement (downgrade) :
                      la boutique garde son forfait actuel jusqu'à l'échéance.
    """
    from config import normalize_plan
    plan = normalize_plan(plan)
    db = get_db()
    if immediate:
        fields = {"plan": plan, "pending_plan": None}
    else:
        m = get_merchant(merchant_id) or {}
        # Si on reprogramme le même forfait que l'actuel → on annule juste tout pending.
        fields = {"pending_plan": None if plan == normalize_plan(m.get("plan")) else plan}
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


def list_suspended_for_winback(limit: int = 50) -> list[dict[str, Any]]:
    """Boutiques suspendues jamais relancées en win-back (winback_at vide)."""
    db = get_db()
    r = (db.table("bia_merchants").select("*").eq("status", "suspended")
         .is_("winback_at", "null").limit(limit).execute())
    return r.data or []


def mark_winback(merchant_id: str) -> None:
    """Marque qu'un message de win-back a été envoyé (anti-spam)."""
    get_db().table("bia_merchants").update({"winback_at": "now()"}).eq("id", merchant_id).execute()


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


# ---------------------------------------------------------------------------
# Boîte email entrante (bia_inbox) — réponses de prospection RECRUTEMENT
# ---------------------------------------------------------------------------

def find_recruitment_prospect(email: str) -> dict[str, Any] | None:
    """Le prospect (recrutement) qu'on a contacté à cet email, s'il existe. None sinon.

    Sécurité : l'agent ne répond QU'AUX gens qu'on a réellement contactés (pas aux
    inconnus / newsletters / spam qui atterriraient dans la boîte).
    """
    email = (email or "").strip().lower()
    if not email:
        return None
    r = (get_db().table("bia_prospects").select("*")
         .eq("owner_type", "admin").eq("email", email)
         .order("created_at", desc=True).limit(1).execute())
    return r.data[0] if r.data else None


def find_merchant_prospect(merchant_id: str, email: str) -> dict[str, Any] | None:
    """Le prospect d'une BOUTIQUE à cet email (owner_type='merchant'). None sinon."""
    email = (email or "").strip().lower()
    if not (merchant_id and email):
        return None
    r = (get_db().table("bia_prospects").select("*")
         .eq("owner_type", "merchant").eq("merchant_id", merchant_id).eq("email", email)
         .order("created_at", desc=True).limit(1).execute())
    return r.data[0] if r.data else None


def inbox_message_seen(message_id: str) -> bool:
    """Ce Message-ID entrant a-t-il déjà été traité ? (dédup IMAP)."""
    mid = (message_id or "").strip()
    if not mid:
        return False
    r = (get_db().table("bia_inbox").select("id", count="exact", head=True)
         .eq("message_id", mid).execute())
    return (r.count or 0) > 0


def record_inbox(prospect_email: str, direction: str, subject: str | None,
                 body: str | None, message_id: str | None = None,
                 merchant_id: str | None = None, status: str = "sent") -> str | None:
    """Trace un email entrant ('in') ou une réponse ('out'). Retourne l'id de la ligne.

    `merchant_id` None = recrutement (admin) ; sinon = réponse pour une boutique.
    `status` 'draft' = brouillon en attente de validation du commerçant.
    """
    r = get_db().table("bia_inbox").insert({
        "prospect_email": (prospect_email or "").strip().lower(),
        "merchant_id": merchant_id,
        "direction": direction,
        "status": status,
        "subject": (subject or "")[:300],
        "body": (body or "")[:8000],
        "message_id": (message_id or None),
    }).execute()
    return (r.data[0]["id"] if r.data else None)


def list_inbox_thread(prospect_email: str, merchant_id: str | None = None,
                      limit: int = 20) -> list[dict[str, Any]]:
    """Le fil d'échanges avec ce prospect (du plus ancien au récent).

    merchant_id None = fil de recrutement ; sinon = fil de la boutique. On exclut les
    brouillons rejetés du contexte.
    """
    email = (prospect_email or "").strip().lower()
    if not email:
        return []
    q = (get_db().table("bia_inbox").select("direction,subject,body,status,created_at")
         .eq("prospect_email", email).neq("status", "rejected"))
    q = q.eq("merchant_id", merchant_id) if merchant_id else q.is_("merchant_id", "null")
    r = q.order("created_at", desc=True).limit(limit).execute()
    return list(reversed(r.data or []))


def list_pending_drafts(merchant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Brouillons de réponse en attente de validation pour cette boutique."""
    r = (get_db().table("bia_inbox").select("*")
         .eq("merchant_id", merchant_id).eq("direction", "out").eq("status", "draft")
         .order("created_at", desc=True).limit(limit).execute())
    return r.data or []


def get_inbox_row(row_id: str) -> dict[str, Any] | None:
    r = get_db().table("bia_inbox").select("*").eq("id", row_id).limit(1).execute()
    return r.data[0] if r.data else None


def set_inbox_row(row_id: str, fields: dict[str, Any]) -> None:
    get_db().table("bia_inbox").update(fields).eq("id", row_id).execute()


def count_pending_drafts(merchant_id: str | None = None) -> int:
    """Nombre de brouillons à valider (toutes boutiques si merchant_id None)."""
    q = (get_db().table("bia_inbox").select("id", count="exact", head=True)
         .eq("direction", "out").eq("status", "draft"))
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().count or 0


def set_merchant_inbox_mode(merchant_id: str, mode: str) -> None:
    """Mode de réponse email d'une boutique : 'review' (supervisé) ou 'auto'."""
    mode = "auto" if str(mode).strip().lower() == "auto" else "review"
    get_db().table("bia_merchants").update({"inbox_mode": mode}).eq("id", merchant_id).execute()


def count_inbox_out_since(iso_ts: str) -> int:
    """Nombre de réponses envoyées par l'agent depuis `iso_ts` (plafond/jour)."""
    r = (get_db().table("bia_inbox").select("id", count="exact", head=True)
         .eq("direction", "out").gte("created_at", iso_ts).execute())
    return r.count or 0


def inbox_out_recently(prospect_email: str, since_iso: str) -> bool:
    """L'agent a-t-il déjà répondu à ce prospect depuis `since_iso` ? (anti-boucle)."""
    email = (prospect_email or "").strip().lower()
    if not email:
        return False
    r = (get_db().table("bia_inbox").select("id", count="exact", head=True)
         .eq("prospect_email", email).eq("direction", "out")
         .gte("created_at", since_iso).execute())
    return (r.count or 0) > 0


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


def count_messages_since(iso: str, role: str | None = None,
                         merchant_id: str | None = None) -> int:
    """Nb de messages depuis un horodatage (décision d'apprentissage — requête légère)."""
    db = get_db()
    q = db.table("bia_messages").select("id", count="exact", head=True).gte("created_at", iso)
    if role:
        q = q.eq("role", role)
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().count or 0


def count_orders_since(iso: str, merchant_id: str | None = None) -> int:
    """Nb de commandes depuis un horodatage (décision d'apprentissage — requête légère)."""
    db = get_db()
    q = db.table("bia_orders").select("id", count="exact", head=True).gte("created_at", iso)
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().count or 0


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


def record_followup(merchant_id: str, customer: str, kind: str,
                    message: str, order_id: str | None = None) -> None:
    """Trace une relance envoyée (anti-doublon + reporting)."""
    get_db().table("bia_followups").insert({
        "merchant_id": merchant_id, "customer_whatsapp": customer, "kind": kind,
        "message": message, "order_id": order_id,
    }).execute()


def followed_up_recently(merchant_id: str, customer: str, days: int = 3) -> bool:
    """Ce client a-t-il déjà été relancé récemment (par cette boutique) ? (cooldown)."""
    r = (
        get_db().table("bia_followups").select("id", count="exact", head=True)
        .eq("merchant_id", merchant_id).eq("customer_whatsapp", customer)
        .gte("sent_at", _window_iso(days)).execute()
    )
    return (r.count or 0) > 0


def count_followups_since(iso: str, merchant_id: str | None = None) -> int:
    """Nb de relances envoyées depuis un horodatage (plafond/jour)."""
    db = get_db()
    q = db.table("bia_followups").select("id", count="exact", head=True).gte("sent_at", iso)
    if merchant_id:
        q = q.eq("merchant_id", merchant_id)
    return q.execute().count or 0


def list_pending_orders(days: int) -> list[dict[str, Any]]:
    """Commandes en attente de paiement sur N jours (paniers à relancer)."""
    return (
        get_db().table("bia_orders").select("*")
        .eq("status", "pending").gte("created_at", _window_iso(days))
        .order("created_at", desc=True).execute().data or []
    )


def count_followups_today(merchant_id: str | None = None) -> int:
    return count_followups_since(_today_start_iso(), merchant_id)


# ---------------------------------------------------------------------------
# Cerveau CEO (autonomie stratégique) — bia_decisions
# ---------------------------------------------------------------------------

def save_decisions(decisions: list[dict[str, Any]]) -> int:
    """Enregistre les recommandations proposées par le directeur autonome."""
    rows = []
    for d in decisions or []:
        title = (d.get("title") or d.get("titre") or "").strip()
        if not title:
            continue
        action = (d.get("action") or "").strip().lower() or None
        rows.append({
            "category": (d.get("category") or d.get("categorie") or "autre")[:40],
            "title": title[:200],
            "finding": (d.get("finding") or d.get("constat") or "").strip() or None,
            "recommendation": (d.get("recommendation") or d.get("recommandation") or "").strip() or None,
            "impact": (d.get("impact") or d.get("impact_estime") or "").strip() or None,
            "level": "auto" if (d.get("level") or d.get("niveau")) == "auto" else "validation",
            "financial": bool(d.get("financial") or d.get("financier")),
            "action": action,
            "action_params": d.get("action_params") or {},
            "status": "proposed",
        })
    if not rows:
        return 0
    return len(get_db().table("bia_decisions").insert(rows).execute().data or [])


def list_decisions(status: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    db = get_db()
    q = db.table("bia_decisions").select("*")
    if status:
        q = q.eq("status", status)
    return q.order("created_at", desc=True).limit(limit).execute().data or []


def get_decision(decision_id: str) -> dict[str, Any] | None:
    r = get_db().table("bia_decisions").select("*").eq("id", decision_id).limit(1).execute()
    return r.data[0] if r.data else None


def set_decision_status(decision_id: str, status: str) -> dict[str, Any]:
    from datetime import datetime, timezone
    fields: dict[str, Any] = {"status": status}
    if status in ("approved", "rejected", "done"):
        fields["decided_at"] = datetime.now(timezone.utc).isoformat()
    r = get_db().table("bia_decisions").update(fields).eq("id", decision_id).execute()
    return r.data[0] if r.data else {}


def count_decisions(status: str | None = None) -> int:
    db = get_db()
    q = db.table("bia_decisions").select("id", count="exact", head=True)
    if status:
        q = q.eq("status", status)
    return q.execute().count or 0


# ---------------------------------------------------------------------------
# Auto-expérimentation (le « ML » de Vendora) — bia_experiments / assignments
# ---------------------------------------------------------------------------

def create_experiment(name: str, hypothesis: str, variant_text: str,
                      status: str = "active") -> dict[str, Any]:
    r = get_db().table("bia_experiments").insert({
        "name": name, "hypothesis": hypothesis,
        "variant_text": variant_text or "", "status": status,
    }).execute()
    return r.data[0] if r.data else {}


def list_experiments(status: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    db = get_db()
    q = db.table("bia_experiments").select("*")
    if status:
        q = q.eq("status", status)
    return q.order("created_at", desc=True).limit(limit).execute().data or []


def set_experiment_status(experiment_id: str, status: str) -> None:
    get_db().table("bia_experiments").update({"status": status}).eq("id", experiment_id).execute()


def update_experiment_counters(experiment_id: str, total: int, won: int) -> None:
    get_db().table("bia_experiments").update(
        {"total": total, "won": won}).eq("id", experiment_id).execute()


def get_assignment(merchant_id: str, customer: str) -> str | None:
    r = (get_db().table("bia_experiment_assignments").select("variant_id")
         .eq("merchant_id", merchant_id).eq("customer", customer).limit(1).execute())
    return r.data[0]["variant_id"] if r.data else None


def set_assignment(merchant_id: str, customer: str, variant_id: str) -> None:
    get_db().table("bia_experiment_assignments").upsert(
        {"merchant_id": merchant_id, "customer": customer, "variant_id": variant_id},
        on_conflict="merchant_id,customer",
    ).execute()


def list_assignments() -> list[dict[str, Any]]:
    return (get_db().table("bia_experiment_assignments")
            .select("merchant_id, customer, variant_id").execute().data or [])


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
