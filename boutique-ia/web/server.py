"""Boutique IA — serveur FastAPI (ÉTAGE 1 : inscription self-service).

Lancer en local :
    cd boutique-ia
    uvicorn web.server:app --reload --port 8010
Puis ouvrir http://localhost:8010/
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import string
import time
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import (
    PLAN_CORE_FEATURES,
    PLAN_EXTRA_FEATURES,
    PLAN_LABELS,
    PLAN_PRICES,
    daily_orders_for_plan,
    normalize_plan,
    price_for_plan,
    prospection_daily_for_plan,
    settings,
)


def _plans_overview(current_plan: str) -> list[dict]:
    """Les 3 forfaits avec leurs fonctionnalités réelles, pour le back-office."""
    out = []
    for key in ("demarrage", "business", "empire"):
        feats = [{"label": f, "live": True} for f in PLAN_CORE_FEATURES]
        feats += [{"label": lbl, "live": live} for lbl, live in PLAN_EXTRA_FEATURES.get(key, [])]
        out.append({
            "key": key,
            "label": PLAN_LABELS[key],
            "price": PLAN_PRICES[key],
            "current": key == current_plan,
            "features": feats,
        })
    return out


def _gen_code(n: int = 6) -> str:
    """Code court unique-ish pour router les messages WhatsApp vers la bonne boutique."""
    return "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def _wa_link(code: str) -> str:
    """Lien wa.me partageable par la boutique (numéro Vendora partagé + code)."""
    number = re.sub(r"\D", "", settings.vendora_whatsapp_number or "")
    if not number or not code:
        return ""
    text = quote(f"Bonjour ! (vendora:{code})")
    return f"https://wa.me/{number}?text={text}"

log = logging.getLogger("boutique-ia.server")


# ---------------------------------------------------------------------------
# Authentification back-office commerçant (code d'accès + session cookie signé)
# ---------------------------------------------------------------------------
SESSION_COOKIE = "bo_session"
SESSION_DAYS = 30


def _sess_secret() -> str:
    return settings.session_secret or settings.admin_token or "vendora-dev-secret"


def _hash_pin(pin: str, merchant_id: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), merchant_id.encode(), 120_000).hex()


def _make_session(merchant_id: str) -> str:
    exp = int(time.time()) + SESSION_DAYS * 86400
    payload = f"{merchant_id}.{exp}"
    sig = hmac.new(_sess_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def _session_ok(request: Request, merchant_id: str) -> bool:
    token = request.cookies.get(SESSION_COOKIE, "")
    try:
        mid, exp, sig = token.rsplit(".", 2)
    except ValueError:
        return False
    payload = f"{mid}.{exp}"
    good = hmac.new(_sess_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(good, sig):
        return False
    return mid == merchant_id and int(exp) > time.time()


def _need_session(request: Request, merchant_id: str):
    """Retourne une réponse 401 si la session est absente/invalide, sinon None."""
    if not _session_ok(request, merchant_id):
        return JSONResponse({"ok": False, "error": "Session requise.", "auth": True}, status_code=401)
    return None


def _order_recorder(merchant: dict, customer_whatsapp: str | None):
    """Construit le callback que le cerveau appelle quand une vente se conclut."""
    from db.client import create_order
    from notify import notify_new_order

    def _on_order(data: dict) -> None:
        articles = data.get("articles") or []
        items = [
            {
                "produit": (a.get("produit") or "").strip(),
                "quantite": a.get("quantite") or 1,
                "prix_unitaire": a.get("prix_unitaire"),
            }
            for a in articles
            if (a.get("produit") or "").strip()
        ]
        pay = (data.get("paiement") or "").strip().lower()
        payment_method = "livraison" if "livr" in pay else ("mobile_money" if pay else None)
        order = create_order(
            merchant_id=merchant["id"],
            customer_whatsapp=customer_whatsapp,
            items=items,
            total=data.get("total"),
            delivery_mode=(data.get("mode_livraison") or "").strip() or None,
            delivery_address=(data.get("adresse") or "").strip() or None,
            customer_name=(data.get("nom_client") or "").strip() or None,
            payment_method=payment_method,
        )
        try:
            notify_new_order(merchant, order, items)
        except Exception:  # noqa: BLE001
            log.warning("alerte commande échouée", exc_info=True)

    return _on_order


def _escalation_notifier(merchant: dict, customer: str | None):
    """Callback appelé quand l'agent escalade un client vers le/la propriétaire."""
    from notify import notify_hot_lead

    def _on_escalate(data: dict) -> None:
        try:
            notify_hot_lead(
                merchant, customer,
                raison=(data.get("raison") or "À rappeler").strip(),
                resume=(data.get("resume") or "").strip(),
                nom_client=(data.get("nom_client") or "").strip() or None,
            )
        except Exception:  # noqa: BLE001
            log.warning("alerte lead chaud échouée", exc_info=True)

    return _on_escalate


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=settings.product_name, description=settings.product_tagline)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _ctx(request: Request, **extra) -> dict:
    base = {
        "product_name": settings.product_name,
        "tagline": settings.product_tagline,
        "price": settings.saas_price_fcfa,
        "free_trial_messages": settings.free_trial_messages,
        "saas_momo_number": settings.saas_momo_number,
        "saas_momo_name": settings.saas_momo_name,
        "saas_momo_network": settings.saas_momo_network,
    }
    base.update(extra)
    return base


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def onboarding(request: Request):
    """Page publique : la fiche d'inscription du commerçant."""
    return templates.TemplateResponse(request, "onboarding.html", _ctx(request))


@app.get("/activation/{merchant_id}", response_class=HTMLResponse)
async def activation(request: Request, merchant_id: str):
    """Écran 'payez par Mobile Money pour activer'."""
    from db.client import get_merchant
    merchant = None
    try:
        merchant = get_merchant(merchant_id)
    except Exception as e:  # noqa: BLE001
        log.warning("activation: lecture merchant impossible: %s", e)
    price = price_for_plan(merchant.get("plan")) if merchant else settings.saas_price_fcfa
    return templates.TemplateResponse(
        request, "activation.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id, price=price),
    )


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.post("/api/merchants")
async def create_merchant_endpoint(request: Request):
    """Reçoit la fiche d'inscription, crée la boutique + ses produits."""
    from db.client import add_products, create_merchant
    from notify import notify_new_merchant

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)

    business_name = (body.get("business_name") or "").strip()
    whatsapp_business = (body.get("whatsapp_business") or "").strip()
    if not business_name or not whatsapp_business:
        return JSONResponse(
            {"ok": False, "error": "Nom de la boutique et WhatsApp obligatoires."},
            status_code=400,
        )

    merchant_payload = {
        "business_name": business_name,
        "code": _gen_code(),
        "plan": normalize_plan(body.get("plan")),
        "sector": (body.get("sector") or "").strip() or None,
        "description": (body.get("description") or "").strip() or None,
        "city": (body.get("city") or "").strip() or None,
        "country": (body.get("country") or "BJ").strip() or "BJ",
        "whatsapp_business": whatsapp_business,
        "owner_whatsapp": (body.get("owner_whatsapp") or "").strip() or None,
        "owner_email": (body.get("owner_email") or "").strip() or None,
        "momo_number": (body.get("momo_number") or "").strip() or None,
        "momo_name": (body.get("momo_name") or "").strip() or None,
        "momo_network": (body.get("momo_network") or "").strip() or None,
        "delivery_zones": (body.get("delivery_zones") or "").strip() or None,
        "delivery_fee_info": (body.get("delivery_fee_info") or "").strip() or None,
        "ai_tone": (body.get("ai_tone") or "").strip() or "chaleureux et professionnel",
        "languages": (body.get("languages") or "").strip() or "français",
        "business_hours": (body.get("business_hours") or "").strip() or None,
        "policies": (body.get("policies") or "").strip() or None,
        "extra_info": (body.get("extra_info") or "").strip() or None,
    }

    try:
        merchant = create_merchant(merchant_payload)
        merchant_id = merchant.get("id")
        products = body.get("products") or []
        count = add_products(merchant_id, products) if merchant_id else 0
    except Exception as e:  # noqa: BLE001
        log.exception("création boutique échouée")
        return JSONResponse(
            {"ok": False, "error": f"Erreur enregistrement : {e}"}, status_code=500
        )

    # Alerte Mongazi (best-effort, ne bloque jamais l'inscription)
    try:
        notify_new_merchant(merchant, count)
    except Exception:  # noqa: BLE001
        pass

    return {"ok": True, "merchant_id": merchant_id, "products": count}


@app.post("/api/merchants/{merchant_id}/payment")
async def submit_payment(request: Request, merchant_id: str):
    """Le commerçant déclare avoir payé l'abonnement (référence MoMo)."""
    from db.client import get_merchant, set_merchant_payment_ref
    from notify import notify_payment_submitted

    try:
        body = await request.json()
    except Exception:
        body = {}
    ref = (body.get("ref") or "").strip()
    if not ref:
        return JSONResponse(
            {"ok": False, "error": "Référence de paiement requise."}, status_code=400
        )
    try:
        set_merchant_payment_ref(merchant_id, ref)
        merchant = get_merchant(merchant_id)
        notify_payment_submitted(merchant or {"id": merchant_id}, ref)
    except Exception as e:  # noqa: BLE001
        log.exception("soumission paiement échouée")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"ok": True, "product": settings.product_name}


# ---------------------------------------------------------------------------
# ÉTAGE 4 — Réponses entrantes : désinscription + webhook Resend (bounces/plaintes)
# ---------------------------------------------------------------------------

@app.get("/unsub/{token}", response_class=HTMLResponse)
async def unsubscribe(token: str):
    """Lien de désinscription des emails de prospection (signé)."""
    from core.prospecting import verify_unsub_token
    from db.client import add_optout
    email = verify_unsub_token(token)
    page = ("<body style='font-family:system-ui,sans-serif;background:#0a0a0c;color:#ededf0;"
            "text-align:center;padding:64px 24px'>")
    if not email:
        return HTMLResponse(page + "<h2>Lien invalide</h2><p>Ce lien de désinscription n'est pas valide.</p></body>",
                            status_code=400)
    try:
        add_optout(email, "email", "unsubscribe")
    except Exception:  # noqa: BLE001
        log.warning("optout enregistrement échoué", exc_info=True)
    return HTMLResponse(
        page + "<h2 style='color:#10b981'>Désinscription confirmée ✓</h2>"
        f"<p><b>{escape(email)}</b> ne recevra plus nos emails.<br>Merci, et désolé pour le dérangement.</p></body>"
    )


@app.post("/api/webhooks/resend")
async def resend_webhook(request: Request):
    """Reçoit les événements Resend : bounce / plainte spam → blacklist l'email."""
    from db.client import blacklist_prospect_email
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False}, status_code=400)
    etype = (body.get("type") or "").lower()
    data = body.get("data") or {}
    to = data.get("to") or data.get("email") or data.get("recipient")
    if isinstance(to, list):
        to = to[0] if to else None
    if to and ("bounce" in etype or "complain" in etype):
        reason = "complaint" if "complain" in etype else "bounce"
        try:
            blacklist_prospect_email(to, reason)
            log.info("Resend %s → blacklist %s", etype, to)
        except Exception:  # noqa: BLE001
            log.warning("blacklist échoué", exc_info=True)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/auth")
async def merchant_auth(request: Request, merchant_id: str):
    """Crée (mode 'set') ou vérifie (mode 'login') le code d'accès → pose la session."""
    from db.client import get_merchant, set_merchant_pin
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    pin = (body.get("pin") or "").strip()
    mode = (body.get("mode") or "login").strip()
    if not (pin.isdigit() and 4 <= len(pin) <= 8):
        return JSONResponse({"ok": False, "error": "Le code doit faire 4 à 8 chiffres."}, status_code=400)
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    h = _hash_pin(pin, merchant_id)
    if mode == "set":
        if merchant.get("access_pin"):
            return JSONResponse({"ok": False, "error": "Un code existe déjà — connectez-vous."}, status_code=400)
        set_merchant_pin(merchant_id, h)
    else:
        existing = merchant.get("access_pin") or ""
        if not existing or not hmac.compare_digest(existing, h):
            return JSONResponse({"ok": False, "error": "Code incorrect."}, status_code=401)
    resp = JSONResponse({"ok": True})
    resp.set_cookie(SESSION_COOKIE, _make_session(merchant_id),
                    max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax", path="/")
    return resp


# ---------------------------------------------------------------------------
# Back-office commerçant — gérer sa fiche et ses produits soi-même
# (lien privé /boutique/{merchant_id} ; l'agent lit les changements en direct)
# ---------------------------------------------------------------------------

@app.get("/boutique/{merchant_id}", response_class=HTMLResponse)
async def boutique_backoffice(request: Request, merchant_id: str):
    from db.client import (
        count_manager_orders_today,
        get_merchant,
        list_orders,
        list_products,
        list_recent_conversations,
        order_stats,
    )
    from core.prospecting import CATEGORIES
    from db.client import (
        count_prospection_sent_today,
        list_campaigns,
    )

    # --- Garde d'accès : si pas de session valide → écran de code ---
    try:
        _m = get_merchant(merchant_id)
    except Exception:  # noqa: BLE001
        _m = None
    if _m and not _session_ok(request, merchant_id):
        return templates.TemplateResponse(
            request, "boutique_gate.html",
            _ctx(request, merchant_id=merchant_id,
                 business_name=_m.get("business_name") or "Ma boutique",
                 has_pin=bool(_m.get("access_pin")),
                 accent=(_m.get("brand_color") or "#10b981")),
        )

    merchant, products = None, []
    stats = {"count": 0, "revenue": 0}
    recent_orders, conversations, plans, campaigns = [], [], [], []
    plan, plan_label = "demarrage", "Démarrage"
    daily_limit, used_today = 5, 0
    prospect_daily, prospect_used = 0, 0
    try:
        merchant = get_merchant(merchant_id)
        if merchant:
            products = list_products(merchant_id)
            stats = order_stats(merchant_id)
            recent_orders = list_orders(merchant_id, limit=8)
            conversations = list_recent_conversations(merchant_id, limit=8)
            plan = normalize_plan(merchant.get("plan"))
            plan_label = PLAN_LABELS[plan]
            daily_limit = daily_orders_for_plan(plan)
            used_today = count_manager_orders_today(merchant_id)
            plans = _plans_overview(plan)
            prospect_daily = prospection_daily_for_plan(plan)
            prospect_used = count_prospection_sent_today("merchant", merchant_id)
            campaigns = list_campaigns("merchant", merchant_id, limit=6)
    except Exception as e:  # noqa: BLE001
        log.warning("back-office: lecture impossible: %s", e)
    wa_link = _wa_link(merchant.get("code")) if merchant else ""
    remaining = -1 if daily_limit < 0 else max(0, daily_limit - used_today)
    accent = (merchant.get("brand_color") if merchant else None) or "#10b981"
    cats = [{"key": k, "label": v["label"]} for k, v in CATEGORIES.items()]
    return templates.TemplateResponse(
        request, "boutique.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id,
             products=products, wa_link=wa_link, stats=stats,
             recent_orders=recent_orders, conversations=conversations,
             plan=plan, plan_label=plan_label, plans=plans, accent=accent,
             daily_limit=daily_limit, used_today=used_today, remaining=remaining,
             categories=cats, campaigns=campaigns,
             prospect_daily=prospect_daily, prospect_used=prospect_used,
             prospect_remaining=max(0, prospect_daily - prospect_used)),
    )


# ---------------------------------------------------------------------------
# ÉTAGE 4 — Tableau de bord admin (Mongazi) : toutes les boutiques, paiements, ventes
# ---------------------------------------------------------------------------

def _admin_ok(token: str | None) -> bool:
    expected = settings.admin_token
    return bool(expected) and token == expected


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, token: str = ""):
    from db.client import (
        all_orders_brief,
        all_products_brief,
        days_left,
        list_all_merchants,
    )
    if not settings.admin_token:
        return HTMLResponse(
            "<body style='font-family:sans-serif;background:#0a0a0c;color:#eee;padding:40px'>"
            "<h2>Admin non configuré</h2><p>Définis la variable <code>ADMIN_TOKEN</code> "
            "(Railway + .env), puis ouvre <code>/admin?token=TON_TOKEN</code>.</p></body>",
            status_code=503,
        )
    if not _admin_ok(token):
        return HTMLResponse(
            "<body style='font-family:sans-serif;background:#0a0a0c;color:#eee;padding:40px'>"
            "<h2>Accès refusé</h2><p>Ajoute <code>?token=TON_TOKEN</code> à l'URL.</p></body>",
            status_code=401,
        )

    merchants = list_all_merchants()
    orders = all_orders_brief()
    products = all_products_brief()

    # Agrégations en mémoire (peu de boutiques au départ)
    orders_by_m: dict[str, dict] = {}
    for o in orders:
        mid = o.get("merchant_id")
        agg = orders_by_m.setdefault(mid, {"count": 0, "revenue": 0.0})
        agg["count"] += 1
        try:
            agg["revenue"] += float(o.get("total") or 0)
        except (TypeError, ValueError):
            pass
    prod_by_m: dict[str, int] = {}
    for p in products:
        prod_by_m[p.get("merchant_id")] = prod_by_m.get(p.get("merchant_id"), 0) + 1

    rows, mrr, total_sales = [], 0, 0.0
    counts = {"active": 0, "paid_pending_validation": 0, "pending_payment": 0, "suspended": 0}
    for m in merchants:
        mid = m.get("id")
        st = m.get("status") or "pending_payment"
        counts[st] = counts.get(st, 0) + 1
        oc = orders_by_m.get(mid, {"count": 0, "revenue": 0.0})
        total_sales += oc["revenue"]
        price = price_for_plan(m.get("plan"))
        if st == "active":
            mrr += price
        rows.append({
            "m": m,
            "plan_label": PLAN_LABELS[normalize_plan(m.get("plan"))],
            "price": price,
            "products": prod_by_m.get(mid, 0),
            "orders": oc["count"],
            "revenue": oc["revenue"],
            "status": st,
            "dleft": days_left(m),
        })

    pending = [r for r in rows if r["status"] == "paid_pending_validation"]
    glob = {
        "merchants": len(merchants),
        "active": counts.get("active", 0),
        "pending": counts.get("paid_pending_validation", 0),
        "orders": len(orders),
        "sales": total_sales,
        "mrr": mrr,
    }
    from core.prospecting import CATEGORIES
    from db.client import (
        count_prospection_sent_today,
        get_setting_bool,
        get_setting_int,
        list_campaigns,
    )
    cats = [{"key": k, "label": v["label"]} for k, v in CATEGORIES.items()]
    campaigns = list_campaigns("admin", None, limit=8)
    prospect_used = count_prospection_sent_today("admin", None)
    total_recruited = sum((c.get("sent") or 0) for c in list_campaigns("admin", None, limit=200))
    auto_enabled = get_setting_bool("auto_prospection_enabled", settings.auto_prospection_enabled)
    auto_daily = get_setting_int("auto_prospection_daily", settings.auto_prospection_daily)
    return templates.TemplateResponse(
        request, "admin.html",
        _ctx(request, token=token, rows=rows, pending=pending, glob=glob,
             categories=cats, campaigns=campaigns,
             prospect_used=prospect_used, prospect_daily=settings.prospection_admin_daily,
             auto_enabled=auto_enabled, auto_daily=auto_daily,
             total_recruited=total_recruited),
    )


@app.post("/api/admin/merchants/{merchant_id}/activate")
async def admin_activate(request: Request, merchant_id: str):
    from db.client import activate_merchant
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        m = activate_merchant(merchant_id)
    except Exception as e:  # noqa: BLE001
        log.exception("admin activate échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": bool(m), "merchant": m}


@app.post("/api/admin/merchants/{merchant_id}/status")
async def admin_set_status(request: Request, merchant_id: str):
    from db.client import set_merchant_status
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    status = (body.get("status") or "").strip()
    if status not in {"active", "suspended", "pending_payment", "paid_pending_validation"}:
        return JSONResponse({"ok": False, "error": "Statut invalide."}, status_code=400)
    try:
        m = set_merchant_status(merchant_id, status)
    except Exception as e:  # noqa: BLE001
        log.exception("admin set_status échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": bool(m), "merchant": m}


@app.post("/api/admin/merchants/{merchant_id}/reset-pin")
async def admin_reset_pin(request: Request, merchant_id: str):
    """Réinitialise le code d'accès d'une boutique (le commerçant en recrée un)."""
    from db.client import set_merchant_pin
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        set_merchant_pin(merchant_id, None)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/prospection/launch")
async def merchant_prospection_launch(request: Request, merchant_id: str, bg: BackgroundTasks):
    """Le commerçant lance une campagne de prospection (clients/partenaires pros)."""
    from core import prospecting
    from db.client import (
        count_prospection_sent_today,
        create_campaign,
        get_merchant,
    )
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    category = (body.get("category") or "").strip()
    city = (body.get("city") or "").strip()
    if category not in prospecting.CATEGORIES or not city:
        return JSONResponse({"ok": False, "error": "Catégorie ou ville invalide."}, status_code=400)

    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    plan = normalize_plan(merchant.get("plan"))
    daily = prospection_daily_for_plan(plan)
    if daily <= 0:
        return {"ok": True, "locked": True,
                "message": "La prospection est incluse à partir du forfait Business. "
                           "Passez à un forfait supérieur pour l'activer 🚀"}
    if count_prospection_sent_today("merchant", merchant_id) >= daily:
        return {"ok": True, "limit_reached": True,
                "message": f"Limite de {daily} emails de prospection atteinte aujourd'hui."}

    camp = create_campaign({
        "owner_type": "merchant", "merchant_id": merchant_id, "mode": "client",
        "title": f"{prospecting.CATEGORIES[category]['label']} · {city}",
        "category": category, "city": city, "status": "sourcing",
    })
    bg.add_task(prospecting.run_full_campaign, camp["id"], "client", category, city,
                daily, "merchant", merchant_id)
    return {"ok": True, "campaign_id": camp.get("id"),
            "message": "Campagne lancée — recherche des prospects en cours…"}


@app.post("/api/admin/prospection/launch")
async def admin_prospection_launch(request: Request, bg: BackgroundTasks):
    """Vendora (admin) lance une campagne de recrutement de nouvelles boutiques."""
    from core import prospecting
    from db.client import count_prospection_sent_today, create_campaign
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    category = (body.get("category") or "").strip()
    city = (body.get("city") or "").strip()
    if category not in prospecting.CATEGORIES or not city:
        return JSONResponse({"ok": False, "error": "Catégorie ou ville invalide."}, status_code=400)
    daily = settings.prospection_admin_daily
    if count_prospection_sent_today("admin", None) >= daily:
        return {"ok": True, "limit_reached": True,
                "message": f"Limite admin de {daily} emails atteinte aujourd'hui."}
    camp = create_campaign({
        "owner_type": "admin", "merchant_id": None, "mode": "recrutement",
        "title": f"Recrutement · {prospecting.CATEGORIES[category]['label']} · {city}",
        "category": category, "city": city, "status": "sourcing",
    })
    bg.add_task(prospecting.run_full_campaign, camp["id"], "recrutement", category, city,
                daily, "admin", None)
    return {"ok": True, "campaign_id": camp.get("id"),
            "message": "Campagne de recrutement lancée…"}


# ---------------------------------------------------------------------------
# Recrutement AUTONOME — Vendora se trouve des clients tout seul (pilote auto)
# ---------------------------------------------------------------------------
# Cibles tournantes (catégorie, ville) pour ne pas épuiser une seule zone.
AUTO_TARGETS = [
    ("restaurant", "Cotonou"), ("fashion", "Cotonou"), ("beauty", "Cotonou"),
    ("retail", "Cotonou"), ("hospitality", "Cotonou"), ("health", "Cotonou"),
    ("restaurant", "Porto-Novo"), ("fashion", "Calavi"),
    ("restaurant", "Lomé"), ("fashion", "Lomé"), ("beauty", "Lomé"),
    ("restaurant", "Abidjan"), ("fashion", "Abidjan"), ("beauty", "Abidjan"),
    ("restaurant", "Dakar"), ("fashion", "Dakar"),
    ("restaurant", "Ouagadougou"), ("fashion", "Ouagadougou"),
]


def _next_auto_target() -> tuple[str, str]:
    from datetime import datetime, timezone
    idx = datetime.now(timezone.utc).timetuple().tm_yday % len(AUTO_TARGETS)
    return AUTO_TARGETS[idx]


def _auto_ran_today() -> bool:
    from datetime import datetime, timezone
    from db.client import list_campaigns
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for c in list_campaigns("admin", None, limit=12):
        if (c.get("title") or "").startswith("Auto ·") and (c.get("created_at") or "").startswith(today):
            return True
    return False


def _run_auto_cycle() -> dict:
    """Lance UN cycle de recrutement automatique (sourcing→rédaction→envoi) + résumé."""
    from core import prospecting
    from db.client import create_campaign, get_campaign, get_setting_int
    from notify import notify_mongazi
    cat, city = _next_auto_target()
    label = prospecting.CATEGORIES.get(cat, {}).get("label", cat)
    daily = get_setting_int("auto_prospection_daily", settings.auto_prospection_daily)
    camp = create_campaign({
        "owner_type": "admin", "merchant_id": None, "mode": "recrutement",
        "title": f"Auto · {label} · {city}", "category": cat, "city": city, "status": "sourcing",
    })
    prospecting.run_full_campaign(camp["id"], "recrutement", cat, city,
                                  daily, "admin", None)
    final = get_campaign(camp["id"]) or {}
    try:
        notify_mongazi(
            "🤖 <b>Vendora s'est recruté des clients</b>\n\n"
            f"🎯 {label} · {city}\n"
            f"📨 {final.get('sent', 0)} boutiques contactées "
            f"({final.get('found', 0)} trouvées)"
        )
    except Exception:  # noqa: BLE001
        pass
    return {"sent": final.get("sent", 0), "found": final.get("found", 0),
            "target": f"{label} · {city}"}


@app.post("/api/admin/recruit-settings")
async def admin_recruit_settings(request: Request):
    """Pilote du recrutement automatique : ON/OFF + volume/jour (en direct, sans redeploy)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("auto_prospection_enabled", "true" if body.get("enabled") else "false")
    if "daily" in body:
        try:
            d = max(1, min(80, int(body.get("daily"))))
            set_setting("auto_prospection_daily", d)
        except (TypeError, ValueError):
            pass
    return {"ok": True}


@app.post("/api/admin/prospection/auto")
async def admin_prospection_auto(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement un cycle de recrutement auto (test, ou cron externe)."""
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(_run_auto_cycle)
    return {"ok": True, "message": "Cycle de recrutement automatique lancé."}


def run_billing_cycle() -> dict:
    """Cycle d'abonnement : suspend les expirés + relance ceux qui arrivent à échéance."""
    from db.client import days_left, list_all_merchants, mark_reminder_sent, set_merchant_status
    from notify import notify_subscription_expired, notify_subscription_reminder
    suspended = reminded = 0
    for m in list_all_merchants():
        if m.get("status") != "active" or not m.get("period_end"):
            continue
        d = days_left(m)
        if d is None:
            continue
        if d <= 0:
            set_merchant_status(m["id"], "suspended")
            try:
                notify_subscription_expired(m)
            except Exception:  # noqa: BLE001
                pass
            suspended += 1
        elif d <= settings.reminder_days and m.get("reminder_sent_for") != m.get("period_end"):
            mark_reminder_sent(m["id"], m.get("period_end"))
            try:
                notify_subscription_reminder(m, d, price_for_plan(m.get("plan")))
            except Exception:  # noqa: BLE001
                pass
            reminded += 1
    return {"suspended": suspended, "reminded": reminded}


def run_merchant_auto_prospection() -> int:
    """Chaque boutique avec le pilote auto activé prospecte ses clients (1×/jour)."""
    from datetime import datetime, timezone

    from core import prospecting
    from db.client import (
        count_prospection_sent_today,
        create_campaign,
        list_all_merchants,
        list_campaigns,
        subscription_active,
    )
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    launched = 0
    for m in list_all_merchants():
        if not m.get("auto_prospect_enabled") or not subscription_active(m):
            continue
        plan = normalize_plan(m.get("plan"))
        daily = prospection_daily_for_plan(plan)
        if daily <= 0:
            continue
        cat = (m.get("auto_prospect_category") or "").strip()
        city = (m.get("auto_prospect_city") or m.get("city") or "").strip()
        if cat not in prospecting.CATEGORIES or not city:
            continue
        mid = m["id"]
        if count_prospection_sent_today("merchant", mid) >= daily:
            continue
        # Déjà prospecté aujourd'hui ?
        if any((c.get("created_at") or "").startswith(today)
               for c in list_campaigns("merchant", mid, limit=5)):
            continue
        camp = create_campaign({
            "owner_type": "merchant", "merchant_id": mid, "mode": "client",
            "title": f"Auto · {prospecting.CATEGORIES[cat]['label']} · {city}",
            "category": cat, "city": city, "status": "sourcing",
        })
        try:
            prospecting.run_full_campaign(camp["id"], "client", cat, city, daily, "merchant", mid)
            launched += 1
        except Exception:  # noqa: BLE001
            log.warning("auto-prospection commerçant KO (%s)", mid, exc_info=True)
    return launched


async def _auto_prospection_loop():
    """Boucle de fond : facturation (toujours) + recrutement/jour si ACTIVÉ."""
    import asyncio
    from datetime import datetime, timezone

    from db.client import get_setting_bool
    await asyncio.sleep(20)  # laisse le serveur démarrer tranquillement
    while True:
        try:
            await asyncio.to_thread(run_billing_cycle)  # cycle d'abonnement, à chaque tick
        except Exception:  # noqa: BLE001
            log.warning("billing cycle", exc_info=True)
        try:
            # NB : appels Supabase = bloquants → toujours via to_thread pour ne pas
            # geler l'event loop (sinon toutes les requêtes HTTP se figent).
            enabled = await asyncio.to_thread(
                get_setting_bool, "auto_prospection_enabled", settings.auto_prospection_enabled)
            if enabled and datetime.now(timezone.utc).hour >= settings.auto_prospection_hour:
                ran = await asyncio.to_thread(_auto_ran_today)
                if not ran:
                    await asyncio.to_thread(_run_auto_cycle)
        except Exception:  # noqa: BLE001
            log.warning("auto-prospection loop", exc_info=True)
        try:
            # Pilote auto des COMMERÇANTS (chaque boutique éligible prospecte 1×/jour)
            if datetime.now(timezone.utc).hour >= settings.auto_prospection_hour:
                await asyncio.to_thread(run_merchant_auto_prospection)
        except Exception:  # noqa: BLE001
            log.warning("auto-prospection merchants loop", exc_info=True)
        await asyncio.sleep(1800)  # vérifie toutes les 30 min


@app.on_event("startup")
async def _start_auto_prospection():
    # On démarre TOUJOURS la boucle : l'activation se pilote en direct depuis l'admin
    # (réglage en base), sans redéploiement.
    import asyncio
    asyncio.create_task(_auto_prospection_loop())


@app.post("/api/merchants/{merchant_id}/order")
async def merchant_order_endpoint(request: Request, merchant_id: str):
    """Le commerçant donne un ordre à son agent (langage naturel). Quota/jour selon forfait."""
    from core import manager
    from db.client import (
        count_manager_orders_today,
        get_merchant,
        log_manager_order,
    )
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    order_text = (body.get("message") or "").strip()
    if not order_text:
        return JSONResponse({"ok": False, "error": "Ordre vide."}, status_code=400)

    try:
        merchant = get_merchant(merchant_id)
        if not merchant:
            return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)

        plan = normalize_plan(merchant.get("plan"))
        limit = daily_orders_for_plan(plan)
        if limit >= 0:
            used = count_manager_orders_today(merchant_id)
            if used >= limit:
                return {
                    "ok": True, "limit_reached": True, "remaining": 0,
                    "reply": (f"Vous avez atteint votre limite de {limit} ordres aujourd'hui "
                              f"(forfait {PLAN_LABELS[plan]}). Passez à un forfait supérieur "
                              f"pour piloter votre agent sans limite 🚀"),
                    "actions": [],
                }

        result = manager.run_order(merchant, order_text)
        log_manager_order(merchant_id, order_text, result.get("reply", ""))

        remaining = -1
        if limit >= 0:
            remaining = max(0, limit - count_manager_orders_today(merchant_id))
    except Exception as e:  # noqa: BLE001
        log.exception("ordre commerçant échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)

    return {
        "ok": True, "limit_reached": False, "remaining": remaining,
        "reply": result.get("reply", ""), "actions": result.get("actions", []),
    }


@app.post("/api/merchants/{merchant_id}/update")
async def update_merchant_endpoint(request: Request, merchant_id: str):
    """Le commerçant modifie sa fiche (infos boutique, livraison, MoMo, ton…)."""
    from db.client import update_merchant
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    # Normalise : "" → None pour les champs vides
    fields = {k: (v.strip() or None if isinstance(v, str) else v) for k, v in body.items()}
    if not (fields.get("business_name") if "business_name" in fields else True):
        return JSONResponse({"ok": False, "error": "Le nom de la boutique est obligatoire."}, status_code=400)
    try:
        merchant = update_merchant(merchant_id, fields)
    except Exception as e:  # noqa: BLE001
        log.exception("update merchant échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    return {"ok": True, "merchant": merchant}


@app.post("/api/merchants/{merchant_id}/products")
async def add_product_endpoint(request: Request, merchant_id: str):
    """Ajoute un produit/service à la boutique."""
    from db.client import add_products
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse({"ok": False, "error": "Le nom du produit est obligatoire."}, status_code=400)
    try:
        count = add_products(merchant_id, [body])
    except Exception as e:  # noqa: BLE001
        log.exception("ajout produit échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    return {"ok": True, "added": count}


@app.post("/api/merchants/{merchant_id}/products/{product_id}")
async def update_product_endpoint(request: Request, merchant_id: str, product_id: str):
    """Modifie un produit (nom, prix, description, disponibilité)."""
    from db.client import update_product
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    fields = dict(body)
    if "name" in fields:
        fields["name"] = (fields.get("name") or "").strip()
        if not fields["name"]:
            return JSONResponse({"ok": False, "error": "Le nom du produit est obligatoire."}, status_code=400)
    try:
        product = update_product(product_id, merchant_id, fields)
    except Exception as e:  # noqa: BLE001
        log.exception("update produit échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    if not product:
        return JSONResponse({"ok": False, "error": "Produit introuvable."}, status_code=404)
    return {"ok": True, "product": product}


@app.post("/api/merchants/{merchant_id}/products/{product_id}/photo")
async def upload_photo_endpoint(request: Request, merchant_id: str, product_id: str):
    """Upload une photo pour un produit (Supabase Storage)."""
    from db.client import upload_product_photo
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        form = await request.form()
    except Exception:
        return JSONResponse({"ok": False, "error": "Formulaire invalide"}, status_code=400)
    file = form.get("photo")
    if file is None or not hasattr(file, "read"):
        return JSONResponse({"ok": False, "error": "Aucune image."}, status_code=400)
    data = await file.read()
    if not data:
        return JSONResponse({"ok": False, "error": "Image vide."}, status_code=400)
    if len(data) > 6_000_000:
        return JSONResponse({"ok": False, "error": "Image trop lourde (max 6 Mo)."}, status_code=400)
    ctype = (getattr(file, "content_type", "") or "image/jpeg")
    if not ctype.startswith("image/"):
        return JSONResponse({"ok": False, "error": "Le fichier doit être une image."}, status_code=400)
    ext = ctype.split("/")[-1].split(";")[0].lower() or "jpg"
    if ext == "jpeg":
        ext = "jpg"
    try:
        url = upload_product_photo(merchant_id, product_id, data, ctype, ext)
    except Exception as e:  # noqa: BLE001
        log.exception("upload photo échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "url": url}


@app.delete("/api/merchants/{merchant_id}/products/{product_id}")
async def delete_product_endpoint(request: Request, merchant_id: str, product_id: str):
    """Supprime un produit de la boutique."""
    from db.client import delete_product
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        ok = delete_product(product_id, merchant_id)
    except Exception as e:  # noqa: BLE001
        log.exception("suppression produit échouée")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    return {"ok": ok}


# ---------------------------------------------------------------------------
# ÉTAGE 2b — WhatsApp réel (webhook Twilio, réponse TwiML)
# ---------------------------------------------------------------------------

def _twiml(message: str, media: list[str] | None = None) -> Response:
    """Réponse TwiML : Twilio enverra ce message (+ photos) au client."""
    body = f"<Body>{escape(message)}</Body>"
    medias = "".join(f"<Media>{escape(u)}</Media>" for u in (media or []) if u)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{body}{medias}</Message></Response>"
    )
    return Response(content=xml, media_type="application/xml")


@app.post("/api/whatsapp/twilio")
async def whatsapp_twilio(request: Request):
    """Reçoit un message WhatsApp (via Twilio), identifie la boutique, répond avec l'agent.

    Un seul numéro Vendora sert toutes les boutiques. Le routing se fait via un
    code (vendora:XXXX) présent dans le lien wa.me que chaque boutique partage,
    puis mémorisé pour la suite de la conversation.
    """
    from core import brain
    from db.client import (
        get_merchant,
        get_merchant_by_code,
        get_wa_session_merchant_id,
        list_products,
        load_history,
        save_message,
        upsert_wa_session,
    )

    try:
        form = await request.form()
    except Exception:
        return _twiml("Désolé, message illisible. Réessayez 🙏")

    from_ = (form.get("From") or "").strip()      # ex : "whatsapp:+22997..."
    body = (form.get("Body") or "").strip()

    # 1. Identifier la boutique
    merchant = None
    m = re.search(r"vendora:([A-Za-z0-9]+)", body, re.I)
    if m:
        merchant = get_merchant_by_code(m.group(1).lower())
        if merchant:
            try:
                upsert_wa_session(from_, merchant["id"])
            except Exception:
                log.warning("wa session upsert échoué", exc_info=True)
    if not merchant and from_:
        try:
            mid = get_wa_session_merchant_id(from_)
            if mid:
                merchant = get_merchant(mid)
        except Exception:
            log.warning("wa session lookup échoué", exc_info=True)

    if not merchant:
        return _twiml(
            "Bonjour 🌟 Pour discuter avec une boutique, ouvrez son lien Vendora "
            "(ou demandez-lui de vous l'envoyer). À très vite !"
        )

    # Boutique suspendue OU abonnement expiré → l'agent ne vend plus.
    from db.client import days_left as _days_left
    _exp = _days_left(merchant)
    if merchant.get("status") == "suspended" or (_exp is not None and _exp <= 0):
        return _twiml(
            "Cette boutique est momentanément indisponible. Merci de réessayer plus tard 🙏"
        )

    # 2a. Message VOCAL ? → transcription (booster). Le client peut parler au lieu d'écrire.
    try:
        num_media = int(form.get("NumMedia") or "0")
    except (TypeError, ValueError):
        num_media = 0
    ctype0 = (form.get("MediaContentType0") or "")
    if num_media > 0 and ctype0.startswith("audio") and form.get("MediaUrl0"):
        from core.transcribe import transcribe_audio
        spoken = transcribe_audio(form.get("MediaUrl0"), ctype0)
        if spoken:
            clean = spoken
        else:
            return _twiml("Je n'ai pas réussi à écouter votre vocal 🙏 "
                          "Pouvez-vous l'écrire en quelques mots ?")
    else:
        # 2b. Nettoyer le marqueur de routing du message texte
        clean = re.sub(r"\(?\s*vendora:[A-Za-z0-9]+\s*\)?", "", body, flags=re.I).strip() or "Bonjour"

    # Opt-out WhatsApp : le client écrit STOP / désabonner
    if clean.strip().lower() in {"stop", "stopp", "unsubscribe", "désabonner",
                                 "desabonner", "arret", "arrêt", "arreter", "arrêter"}:
        try:
            from db.client import add_optout
            add_optout(from_, "whatsapp", "stop")
        except Exception:  # noqa: BLE001
            log.warning("optout WhatsApp échoué", exc_info=True)
        return _twiml("C'est noté ✅ Vous ne recevrez plus de messages. "
                      "Écrivez-nous quand vous voulez revenir 🙏")

    # 3. Faire répondre l'agent vendeur
    try:
        save_message(merchant["id"], from_, "customer", clean)
        history = load_history(merchant["id"], from_, limit=brain.HISTORY_LIMIT)
        products = list_products(merchant["id"])

        media_urls: list[str] = []
        def _on_show(data: dict) -> str:
            names = data.get("produits") or []
            n_before = len(media_urls)
            for raw in names:
                nl = (raw or "").strip().lower()
                if not nl:
                    continue
                for p in products:
                    if p.get("photo_url") and nl in (p.get("name") or "").lower():
                        if p["photo_url"] not in media_urls:
                            media_urls.append(p["photo_url"])
                        break
            return ("Photo(s) envoyée(s) au client." if len(media_urls) > n_before
                    else "Aucune photo disponible pour ce produit — décris-le.")

        answer = brain.reply(
            merchant, products, history,
            on_order=_order_recorder(merchant, from_),
            on_escalate=_escalation_notifier(merchant, from_),
            on_show=_on_show,
        )
        save_message(merchant["id"], from_, "assistant", answer)
    except Exception as e:  # noqa: BLE001
        log.exception("whatsapp reply échoué")
        return _twiml("Un instant, je vérifie avec la boutique et je reviens vers vous 🙏")

    return _twiml(answer, media_urls)


# ---------------------------------------------------------------------------
# ÉTAGE 2 — Le cerveau IA (testable dans le navigateur, sans WhatsApp)
# ---------------------------------------------------------------------------

@app.get("/demo/{merchant_id}", response_class=HTMLResponse)
async def demo_chat(request: Request, merchant_id: str):
    """Simulateur de chat : parle à ton vendeur IA comme un client."""
    from db.client import get_merchant
    merchant = None
    try:
        merchant = get_merchant(merchant_id)
    except Exception as e:  # noqa: BLE001
        log.warning("demo: lecture merchant impossible: %s", e)
    return templates.TemplateResponse(
        request, "demo.html", _ctx(request, merchant=merchant, merchant_id=merchant_id)
    )


@app.get("/essai/{merchant_id}", response_class=HTMLResponse)
async def essai(request: Request, merchant_id: str):
    """Page d'essai après inscription : teste ton vendeur IA (messages limités) puis active."""
    from db.client import get_merchant
    merchant = None
    try:
        merchant = get_merchant(merchant_id)
    except Exception as e:  # noqa: BLE001
        log.warning("essai: lecture merchant impossible: %s", e)
    price = price_for_plan(merchant.get("plan")) if merchant else settings.saas_price_fcfa
    plan_label = (merchant.get("plan") or "demarrage").capitalize() if merchant else ""
    wa_link = _wa_link(merchant.get("code")) if merchant else ""
    return templates.TemplateResponse(
        request, "essai.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id, price=price,
             plan_label=plan_label, wa_link=wa_link),
    )


@app.post("/api/chat")
async def chat(request: Request):
    """Reçoit un message client, fait répondre le vendeur IA, persiste la conversation."""
    from core import brain
    from db.client import (
        count_customer_messages,
        get_merchant,
        list_products,
        load_history,
        save_message,
    )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)

    merchant_id = (body.get("merchant_id") or "").strip()
    customer = (body.get("customer_id") or "demo-web").strip()
    message = (body.get("message") or "").strip()
    preview = bool(body.get("preview"))  # essai gratuit depuis la page de vente
    if not merchant_id or not message:
        return JSONResponse(
            {"ok": False, "error": "merchant_id et message requis."}, status_code=400
        )

    try:
        merchant = get_merchant(merchant_id)
        if not merchant:
            return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)

        # Essai gratuit : on limite le nombre de messages tant que la boutique
        # n'est pas activée (active = abonnement payé → messages illimités).
        limit = settings.free_trial_messages
        if preview and merchant.get("status") != "active":
            already = count_customer_messages(merchant_id, customer)
            if already >= limit:
                return {
                    "ok": True,
                    "reply": "",
                    "trial_over": True,
                    "remaining": 0,
                }

        products = list_products(merchant_id)
        save_message(merchant_id, customer, "customer", message)
        history = load_history(merchant_id, customer, limit=brain.HISTORY_LIMIT)
        # Essai gratuit (preview) → on ne persiste pas de commande (données de test).
        # Simulateur /demo et vrais clients → commande enregistrée + patron prévenu.
        on_order = None if preview else _order_recorder(merchant, customer)
        on_escalate = None if preview else _escalation_notifier(merchant, customer)
        answer = brain.reply(merchant, products, history, on_order=on_order, on_escalate=on_escalate)
        save_message(merchant_id, customer, "assistant", answer)

        remaining = None
        if preview and merchant.get("status") != "active":
            remaining = max(0, limit - count_customer_messages(merchant_id, customer))
    except Exception as e:  # noqa: BLE001
        log.exception("chat échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)

    return {"ok": True, "reply": answer, "remaining": remaining, "trial_over": False}
