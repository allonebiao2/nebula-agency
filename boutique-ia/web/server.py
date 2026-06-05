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
from collections import deque
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


def _appointment_recorder(merchant: dict, customer: str | None):
    """Callback appelé quand l'agent enregistre une demande de rendez-vous."""
    from db.client import create_appointment
    from notify import notify_appointment

    def _on_appointment(data: dict) -> None:
        appt = create_appointment(
            merchant["id"], customer,
            service=(data.get("service") or "").strip() or None,
            requested_time=(data.get("date_souhaitee") or "").strip() or None,
            customer_name=(data.get("nom_client") or "").strip() or None,
            note=" · ".join(x for x in [(data.get("telephone") or "").strip(),
                                        (data.get("note") or "").strip()] if x) or None,
        )
        try:
            notify_appointment(merchant, appt)
        except Exception:  # noqa: BLE001
            log.warning("alerte rendez-vous échouée", exc_info=True)

    return _on_appointment


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
    cur_plan = normalize_plan(merchant.get("plan")) if merchant else "demarrage"
    price = price_for_plan(cur_plan)
    plans = [{"key": k, "label": PLAN_LABELS[k], "price": v} for k, v in PLAN_PRICES.items()]
    return templates.TemplateResponse(
        request, "activation.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id, price=price,
             plans=plans, current_plan=cur_plan),
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

    # Defaults intelligents : l'agent démarre déjà équipé selon le métier + le
    # forfait (jamais de page blanche). Le commerçant ajuste ensuite librement.
    from core.capabilities import default_capabilities_for, serialize_caps
    _cat = (body.get("category") or body.get("sector") or "").strip().lower()
    merchant_payload["enabled_capabilities"] = serialize_caps(
        default_capabilities_for(_cat, merchant_payload["plan"]))

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

    # Essai gratuit 3 jours (bouton « Tester gratuitement » → offre Démarrage) :
    # la boutique devient active mais non payante, suspendue auto à J+3.
    trial = bool(body.get("trial")) and merchant_id
    if trial:
        try:
            from db.client import start_trial
            merchant = start_trial(merchant_id, days=3) or merchant
        except Exception:  # noqa: BLE001
            log.warning("démarrage essai échoué", exc_info=True)

    # Alerte Mongazi (best-effort, ne bloque jamais l'inscription)
    try:
        notify_new_merchant(merchant, count)
    except Exception:  # noqa: BLE001
        pass

    return {"ok": True, "merchant_id": merchant_id, "products": count, "trial": bool(trial)}


@app.post("/api/merchants/{merchant_id}/payment")
async def submit_payment(request: Request, merchant_id: str):
    """Le commerçant déclare avoir payé l'abonnement (référence MoMo + offre choisie)."""
    from db.client import get_merchant, set_merchant_payment_ref, set_merchant_plan
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
        # L'offre est choisie à l'activation (essai = indépendant de l'offre).
        plan = (body.get("plan") or "").strip().lower()
        if plan in PLAN_PRICES:
            set_merchant_plan(merchant_id, plan, immediate=True)
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
    # Réponses email à valider (mode supervisé) + état de la boîte boutique
    from db.client import get_setting_bool, list_pending_drafts
    inbox = {"on": False, "mode": "review", "drafts": []}
    if merchant:
        try:
            inbox = {
                "on": get_setting_bool("boutique_inbox_enabled", False),
                "mode": (merchant.get("inbox_mode") or "review"),
                "drafts": list_pending_drafts(merchant_id),
            }
        except Exception:  # noqa: BLE001
            log.warning("back-office: lecture brouillons KO", exc_info=True)
    wa_link = _wa_link(merchant.get("code")) if merchant else ""
    remaining = -1 if daily_limit < 0 else max(0, daily_limit - used_today)
    accent = (merchant.get("brand_color") if merchant else None) or "#10b981"
    cats = [{"key": k, "label": v["label"]} for k, v in CATEGORIES.items()]
    from core.capabilities import capabilities_context, has_capability
    caps_ctx = capabilities_context(merchant) if merchant else None
    # Guide de démarrage : rend le back-office explicite dès l'arrivée (étapes + état).
    guide = None
    if merchant:
        is_active = merchant.get("status") == "active" and not merchant.get("is_trial")
        steps = [
            {"title": "Ajoutez vos produits ou services",
             "desc": "Pour que votre agent ait quelque chose à vendre à vos clients.",
             "done": bool(products), "target": "produits", "cta": "Ajouter"},
            {"title": "Composez votre vendeur",
             "desc": "Choisissez ce que votre agent sait faire : photos, paiement à la livraison, rendez-vous…",
             "done": bool(merchant.get("enabled_capabilities")), "target": "capacites", "cta": "Configurer"},
            {"title": "Réglez paiement & livraison",
             "desc": "Votre numéro Mobile Money et vos zones de livraison, pour qu'il puisse conclure les ventes.",
             "done": bool(merchant.get("momo_number")), "target": "livraison", "cta": "Renseigner"},
            {"title": "Testez votre agent",
             "desc": "Discutez avec lui comme si vous étiez un client, pour voir comment il répond.",
             "done": None, "href": f"/essai/{merchant_id}", "cta": "Tester"},
            {"title": "Partagez votre lien WhatsApp",
             "desc": "Envoyez ce lien à vos clients : ils tombent directement sur votre vendeur.",
             "done": None, "target": "partager", "cta": "Voir mon lien"},
        ]
        if not is_active:
            steps.append({"title": "Activez votre abonnement",
                          "desc": "Pour que votre agent travaille pour vous 24h/24, en vrai.",
                          "done": False, "href": f"/activation/{merchant_id}", "cta": "Activer"})
        tracked = [s for s in steps if s["done"] is not None]
        guide = {"steps": steps, "done": sum(1 for s in tracked if s["done"]),
                 "total": len(tracked), "all_done": all(s["done"] for s in tracked)}
    trial = None
    if merchant and merchant.get("is_trial"):
        from db.client import days_left as _days_left_bo
        trial = {"days_left": max(0, _days_left_bo(merchant) or 0)}
    rdv_on = bool(merchant) and has_capability(merchant, "rdv")
    appointments = []
    if rdv_on:
        try:
            from db.client import list_appointments
            appointments = list_appointments(merchant_id, limit=20)
        except Exception:  # noqa: BLE001
            log.warning("back-office: lecture RDV KO", exc_info=True)
    return templates.TemplateResponse(
        request, "boutique.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id,
             products=products, wa_link=wa_link, stats=stats,
             recent_orders=recent_orders, conversations=conversations,
             plan=plan, plan_label=plan_label, plans=plans, accent=accent,
             daily_limit=daily_limit, used_today=used_today, remaining=remaining,
             categories=cats, campaigns=campaigns, inbox=inbox, caps=caps_ctx,
             guide=guide, trial=trial, rdv_on=rdv_on, appointments=appointments,
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

    rows, mrr, total_sales, trials = [], 0, 0.0, 0
    counts = {"active": 0, "paid_pending_validation": 0, "pending_payment": 0, "suspended": 0}
    for m in merchants:
        mid = m.get("id")
        st = m.get("status") or "pending_payment"
        counts[st] = counts.get(st, 0) + 1
        oc = orders_by_m.get(mid, {"count": 0, "revenue": 0.0})
        total_sales += oc["revenue"]
        price = price_for_plan(m.get("plan"))
        if st == "active" and not m.get("is_trial"):
            mrr += price        # un essai est actif mais NON payant → exclu du MRR
        if m.get("is_trial"):
            trials += 1
        pplan = (m.get("pending_plan") or "").strip()
        rows.append({
            "m": m,
            "plan_key": normalize_plan(m.get("plan")),
            "plan_label": PLAN_LABELS[normalize_plan(m.get("plan"))],
            "pending_plan": pplan or None,
            "pending_label": PLAN_LABELS.get(normalize_plan(pplan)) if pplan else None,
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
        "trials": trials,
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

    # Relances autonomes (clients silencieux + paniers abandonnés)
    from db.client import count_followups_since, count_followups_today, get_setting
    twilio_ready = bool(settings.twilio_account_sid and settings.twilio_auth_token
                        and settings.vendora_whatsapp_number)
    followups = {
        "enabled": get_setting_bool("followups_enabled", False),
        "today": count_followups_today() if twilio_ready else 0,
        "total": count_followups_since("2000-01-01T00:00:00+00:00") if twilio_ready else 0,
        "twilio_ready": twilio_ready,
    }

    # Boîte email entrante (recrutement → l'agent convertit ; boutiques → supervisé/auto)
    from datetime import datetime, timezone
    from core.inbox import configured as _inbox_configured
    from db.client import count_inbox_out_since, count_pending_drafts
    inbox_ready = _inbox_configured() and bool(settings.resend_api_key)
    _today0 = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
    inbox = {
        "enabled": get_setting_bool("inbox_enabled", False),
        "boutique_enabled": get_setting_bool("boutique_inbox_enabled", False),
        "ready": inbox_ready,
        "today": count_inbox_out_since(_today0) if inbox_ready else 0,
        "total": count_inbox_out_since("2000-01-01T00:00:00+00:00") if inbox_ready else 0,
        "drafts": count_pending_drafts() if inbox_ready else 0,
    }

    # Cerveau d'apprentissage (auto-amélioration)
    from db.client import get_latest_lessons
    learn_enabled = get_setting_bool("learning_enabled", False)
    learn_last = get_setting("learning_last_run")
    latest = get_latest_lessons("global") or {}
    lstats = latest.get("stats") or {}
    learn = {
        "enabled": learn_enabled,
        "last_run": learn_last,
        "last_trigger": get_setting("learning_last_trigger"),
        "lessons": latest.get("lessons") or "",
        "lessons_at": latest.get("created_at"),
        "convos": lstats.get("conversations", 0),
        "won": lstats.get("won", 0),
        "lost": lstats.get("lost", 0),
    }
    # Cerveau CEO (directeur autonome) — décisions à valider
    from db.client import list_decisions, list_experiments
    ceo = {
        "enabled": get_setting_bool("ceo_enabled", False),
        "last_run": get_setting("ceo_last_run"),
        "decisions": list_decisions("proposed", limit=12),
    }
    # Auto-expérimentation des ventes (A/B)
    exp_active = list_experiments("active", limit=10)
    for v in exp_active:
        t = v.get("total") or 0
        v["conv_pct"] = round(100 * (v.get("won") or 0) / t, 1) if t else 0.0
    experiments = {
        "enabled": get_setting_bool("experiments_enabled", False),
        "variants": exp_active,
        "recent_winners": list_experiments("retired", limit=4),
    }
    # Canaux entrants — Messenger + Instagram (Meta). Liens Page/compte → boutique.
    from core import messenger_meta, whatsapp_meta
    from db.client import list_settings_prefix
    code_by_id = {m.get("id"): m.get("code") for m in merchants}
    links = []
    for s in list_settings_prefix("page_merchant_"):
        pid = (s.get("key") or "").replace("page_merchant_", "", 1)
        val = (s.get("value") or "").strip()
        if pid and val:
            links.append({"page_id": pid, "code": val})
    channels = {
        "messenger_ready": messenger_meta.configured(),
        "whatsapp_ready": whatsapp_meta.configured(),
        "links": links,
        "codes": sorted(c for c in code_by_id.values() if c),
        "c2dm_enabled": get_setting_bool("c2dm_enabled", False),
        "c2dm_public_reply": get_setting_bool("c2dm_public_reply", True),
        "c2dm_keyword": get_setting("c2dm_keyword") or "",
    }
    return templates.TemplateResponse(
        request, "admin.html",
        _ctx(request, token=token, rows=rows, pending=pending, glob=glob,
             categories=cats, campaigns=campaigns,
             prospect_used=prospect_used, prospect_daily=settings.prospection_admin_daily,
             auto_enabled=auto_enabled, auto_daily=auto_daily,
             total_recruited=total_recruited, learn=learn, followups=followups,
             ceo=ceo, experiments=experiments, channels=channels, inbox=inbox),
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


@app.post("/api/admin/merchants/{merchant_id}/plan")
async def admin_set_plan(request: Request, merchant_id: str):
    """Change le forfait d'une boutique. apply='now' (immédiat) ou 'renewal' (au renouvellement).

    Recommandé : downgrade → 'renewal' (garde le forfait payé jusqu'à l'échéance) ;
    upgrade → 'now' (le client paie la différence). Mongazi décide (financier).
    """
    from db.client import get_merchant, set_merchant_plan
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    plan = (body.get("plan") or "").strip().lower()
    if plan not in PLAN_PRICES:
        return JSONResponse({"ok": False, "error": "Forfait invalide."}, status_code=400)
    immediate = (body.get("apply") or "renewal") == "now"
    try:
        cur = get_merchant(merchant_id) or {}
        cur_plan = normalize_plan(cur.get("plan"))
        # Garde-fou : un downgrade ne s'applique jamais « maintenant » (le client a payé
        # son forfait en cours) — on le force au renouvellement, même si on demande 'now'.
        if immediate and PLAN_PRICES[plan] < PLAN_PRICES[cur_plan]:
            immediate = False
        m = set_merchant_plan(merchant_id, plan, immediate)
    except Exception as e:  # noqa: BLE001
        log.exception("admin set_plan échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": bool(m), "merchant": m, "applied_now": immediate}


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


@app.post("/api/admin/learning/run")
async def admin_learning_run(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement un cycle d'auto-amélioration (cerveau d'apprentissage)."""
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    # send_digests=False par défaut sur un lancement manuel (test sans spammer les patrons).
    send = bool(body.get("send_digests"))
    bg.add_task(run_learning_job, send, "Lancement manuel depuis le cockpit")
    return {"ok": True, "message": "Analyse lancée — résumé sur Telegram dans un instant."}


@app.post("/api/admin/learning/settings")
async def admin_learning_settings(request: Request):
    """Active / met en pause le cerveau d'apprentissage (sans redéploiement)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("learning_enabled", "true" if body.get("enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/followups/settings")
async def admin_followups_settings(request: Request):
    """Autorise / met en pause les relances autonomes (OFF par défaut)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("followups_enabled", "true" if body.get("enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/followups/run")
async def admin_followups_run(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement une vague de relances (test)."""
    from core.followup import run_followups
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(run_followups)
    return {"ok": True, "message": "Relances lancées — résumé sur Telegram si des envois partent."}


@app.post("/api/admin/inbox/settings")
async def admin_inbox_settings(request: Request):
    """Autorise / met en pause les réponses email entrantes (OFF par défaut)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("inbox_enabled", "true" if body.get("enabled") else "false")
    if "boutique_enabled" in body:
        set_setting("boutique_inbox_enabled", "true" if body.get("boutique_enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/inbox/run")
async def admin_inbox_run(request: Request, bg: BackgroundTasks):
    """Lit la boîte et répond aux prospects maintenant (test). Garde-fous appliqués."""
    from core.inbox import run_inbox
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(run_inbox)
    return {"ok": True, "message": "Boîte email vérifiée — l'agent répond aux prospects connus."}


CEO_INTERVAL_DAYS = 7  # revue stratégique : 1×/semaine


def _ceo_due() -> bool:
    """La revue du directeur doit-elle tourner ? (hebdo ; ON par défaut car il ne fait que proposer)."""
    from datetime import datetime, timezone

    from db.client import get_setting, get_setting_bool
    # OFF par défaut : la revue tourne sur Opus (coûteuse) — pas d'auto-dépense sans
    # vrais clients. Mongazi lance la revue à la main pour tester.
    if not get_setting_bool("ceo_enabled", False):
        return False
    last = get_setting("ceo_last_run")
    if not last:
        return True
    try:
        prev = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True
    return (datetime.now(timezone.utc) - prev).total_seconds() >= CEO_INTERVAL_DAYS * 86400


def run_ceo_job() -> dict:
    """Revue du directeur autonome + mémorise la date (cerveau CEO)."""
    from datetime import datetime, timezone

    from core import strategist
    from db.client import set_setting
    res = strategist.run_ceo_review()
    set_setting("ceo_last_run", datetime.now(timezone.utc).isoformat())
    return res


@app.post("/api/admin/ceo/run")
async def admin_ceo_run(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement une revue du directeur autonome."""
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(run_ceo_job)
    return {"ok": True, "message": "Le directeur analyse le business — décisions sur Telegram + cockpit."}


@app.post("/api/admin/ceo/settings")
async def admin_ceo_settings(request: Request):
    """Active / met en pause la revue autonome hebdomadaire du directeur."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("ceo_enabled", "true" if body.get("enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/experiments/settings")
async def admin_experiments_settings(request: Request):
    """Autorise / met en pause l'auto-expérimentation des ventes (OFF par défaut)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("experiments_enabled", "true" if body.get("enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/messenger/link")
async def admin_messenger_link(request: Request):
    """Associe une Page Facebook / compte Instagram à une boutique (par son code).

    body : {page_id, code}. Si `code` est vide → on supprime l'association (valeur vide).
    Permet aux visiteurs Messenger/IG d'atteindre la bonne boutique sans taper de code.
    """
    from db.client import get_merchant_by_code, set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    page_id = str(body.get("page_id") or "").strip()
    code = str(body.get("code") or "").strip().lower()
    if not page_id:
        return JSONResponse({"ok": False, "error": "page_id requis."}, status_code=400)
    if code and not get_merchant_by_code(code):
        return JSONResponse({"ok": False, "error": f"Aucune boutique au code « {code} »."},
                            status_code=404)
    set_setting(f"page_merchant_{page_id}", code)
    return {"ok": True, "page_id": page_id, "code": code}


@app.post("/api/admin/c2dm/settings")
async def admin_c2dm_settings(request: Request):
    """Comment-to-DM : activer/désactiver, mot-clé déclencheur, réponse publique.

    body : {enabled?, public_reply?, keyword?}. OFF par défaut (acquisition sociale
    conforme : l'agent ne répond QU'aux commentaires, jamais de cold DM).
    """
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("c2dm_enabled", "true" if body.get("enabled") else "false")
    if "public_reply" in body:
        set_setting("c2dm_public_reply", "true" if body.get("public_reply") else "false")
    if "keyword" in body:
        set_setting("c2dm_keyword", str(body.get("keyword") or "").strip())
    return {"ok": True}


@app.post("/api/admin/experiments/run")
async def admin_experiments_run(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement un cycle d'expérimentation (amorce / évalue / promeut)."""
    from core.experiment import run_experiment_cycle
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(run_experiment_cycle)
    return {"ok": True, "message": "Cycle d'expérimentation lancé."}


@app.post("/api/admin/ceo/decision/{decision_id}")
async def admin_ceo_decision(request: Request, decision_id: str):
    """Mongazi valide ✓ ou rejette ✗ une recommandation du directeur.

    Si la décision validée porte une action sûre (niveau:auto, non financière),
    l'agent l'APPLIQUE tout seul dans la foulée (#2 de l'autonomie).
    """
    from core.strategist import execute_decision
    from db.client import get_decision, set_decision_status
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    status = body.get("status")
    if status not in ("approved", "rejected", "done"):
        return JSONResponse({"ok": False, "error": "Statut invalide."}, status_code=400)

    applied_msg = ""
    if status == "approved":
        dec = get_decision(decision_id) or {}
        applied, applied_msg = execute_decision(dec)
        # Appliquée tout seul → on marque 'done' (et on le dit à Mongazi).
        set_decision_status(decision_id, "done" if applied else "approved")
        if applied:
            try:
                from notify import notify_mongazi
                notify_mongazi(f"⚙️ <b>Décision appliquée automatiquement</b>\n\n"
                               f"« {dec.get('title','?')} » → {applied_msg}")
            except Exception:  # noqa: BLE001
                pass
        return {"ok": True, "applied": applied, "applied_message": applied_msg}

    d = set_decision_status(decision_id, status)
    return {"ok": bool(d), "decision": d}


def run_billing_cycle() -> dict:
    """Cycle d'abonnement + essais : suspend les expirés/essais finis + relance à l'échéance.

    Pour un ESSAI (`is_trial`) : rappel à J-1 (pas à J-3) et, à la fin, suspension +
    « preuve de valeur » (ce que l'agent a fait pendant l'essai). Jamais de suppression.
    """
    from db.client import (days_left, list_all_merchants, mark_reminder_sent,
                           set_merchant_status, trial_stats)
    from notify import (notify_subscription_expired, notify_subscription_reminder,
                        notify_trial_ended, notify_trial_reminder)
    suspended = reminded = 0
    for m in list_all_merchants():
        if m.get("status") != "active" or not m.get("period_end"):
            continue
        d = days_left(m)
        if d is None:
            continue
        is_trial = bool(m.get("is_trial"))
        if d <= 0:
            set_merchant_status(m["id"], "suspended")
            try:
                if is_trial:
                    notify_trial_ended(m, trial_stats(m["id"]))
                else:
                    notify_subscription_expired(m)
            except Exception:  # noqa: BLE001
                pass
            suspended += 1
        else:
            # Essai : on relance à J-1. Abonnement payant : à ≤ reminder_days.
            window = 1 if is_trial else settings.reminder_days
            if d <= window and m.get("reminder_sent_for") != m.get("period_end"):
                mark_reminder_sent(m["id"], m.get("period_end"))
                try:
                    if is_trial:
                        notify_trial_reminder(m, d, price_for_plan(m.get("plan")), trial_stats(m["id"]))
                    else:
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
    from core.capabilities import has_capability
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    launched = 0
    for m in list_all_merchants():
        if not m.get("auto_prospect_enabled") or not subscription_active(m):
            continue
        if not has_capability(m, "prospection"):  # capacité du forfait
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


def _learning_decision() -> tuple[bool, str]:
    """Le cerveau décide LUI-MÊME s'il doit apprendre maintenant (+ pourquoi)."""
    from core import learning
    from db.client import get_setting, get_setting_bool
    # OFF par défaut : pas de dépense de tokens en autonomie tant qu'il n'y a pas de
    # vrais clients. Mongazi active quand il veut (ou lance une analyse à la main).
    if not get_setting_bool("learning_enabled", False):
        return False, ""
    last = get_setting("learning_last_run")
    return learning.should_learn(last)


def run_learning_job(send_digests: bool = True, trigger_reason: str | None = None) -> dict:
    """Cycle d'auto-amélioration : apprend des conversations + résumés (Mongazi + commerçants)."""
    from datetime import datetime, timezone

    from core import learning
    from db.client import set_setting, subscription_active
    from notify import notify_learning_summary, notify_weekly_digest

    result = learning.run_learning_cycle()
    result["trigger_reason"] = trigger_reason or ""
    set_setting("learning_last_run", datetime.now(timezone.utc).isoformat())
    if trigger_reason:
        set_setting("learning_last_trigger", trigger_reason)
    try:
        notify_learning_summary(result)
    except Exception:  # noqa: BLE001
        log.warning("notify learning summary", exc_info=True)

    # Auto-expérimentation : amorce/évalue/promeut les variantes de vente (le « ML »).
    try:
        from core.experiment import run_experiment_cycle
        run_experiment_cycle()
    except Exception:  # noqa: BLE001
        log.warning("experiment cycle", exc_info=True)

    # Bonus : résumé hebdo à chaque commerçant actif ayant eu de l'activité (preuve de valeur).
    if send_digests and not result.get("skipped"):
        try:
            stats = learning.merchant_week_stats(days=7)
            for mid, s in stats.items():
                m = s.get("merchant") or {}
                if not subscription_active(m) or s.get("conversations", 0) < 1:
                    continue
                try:
                    notify_weekly_digest(m, s)
                except Exception:  # noqa: BLE001
                    log.warning("digest hebdo boutique %s", mid, exc_info=True)
        except Exception:  # noqa: BLE001
            log.warning("digests hebdo", exc_info=True)
    return result


async def _auto_prospection_loop():
    """Boucle de fond : facturation (toujours) + recrutement/jour si ACTIVÉ + apprentissage hebdo."""
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
        try:
            # Cerveau d'apprentissage : il décide LUI-MÊME quand apprendre
            # (volume de nouvelles conversations OU baisse de conversion), avec
            # garde-fous de cadence (18h mini / 14j maxi).
            due, why = await asyncio.to_thread(_learning_decision)
            if due:
                log.info("learning: déclenchement auto — %s", why)
                await asyncio.to_thread(run_learning_job, True, why)
        except Exception:  # noqa: BLE001
            log.warning("learning loop", exc_info=True)
        try:
            # Relances autonomes (clients silencieux + paniers abandonnés).
            # OFF par défaut ; gating + garde-fous gérés dans run_followups.
            from core.followup import run_followups
            await asyncio.to_thread(run_followups)
        except Exception:  # noqa: BLE001
            log.warning("followups loop", exc_info=True)
        try:
            # Boîte email entrante : l'agent répond aux réponses de recrutement.
            # OFF par défaut ; gating + garde-fous gérés dans run_inbox.
            from core.inbox import run_inbox
            await asyncio.to_thread(run_inbox)
        except Exception:  # noqa: BLE001
            log.warning("inbox loop", exc_info=True)
        try:
            # Cerveau CEO : revue stratégique autonome 1×/semaine (il PROPOSE, Mongazi valide).
            if await asyncio.to_thread(_ceo_due):
                log.info("ceo: revue hebdomadaire autonome")
                await asyncio.to_thread(run_ceo_job)
        except Exception:  # noqa: BLE001
            log.warning("ceo loop", exc_info=True)
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


@app.post("/api/merchants/{merchant_id}/capabilities")
async def merchant_capabilities(request: Request, merchant_id: str):
    """« Composez votre vendeur » : enregistre les capacités choisies.

    body : {ids:[...]}. La grille (palier + nombre selon forfait) est appliquée
    CÔTÉ SERVEUR — on ne fait jamais confiance au navigateur. Retourne le set
    réellement actif (socle + modules retenus).
    """
    from core.capabilities import (effective_capabilities, sanitize_selection,
                                    serialize_caps)
    from db.client import get_merchant, set_merchant_capabilities
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    try:
        body = await request.json()
    except Exception:
        body = {}
    ids = body.get("ids")
    if not isinstance(ids, list):
        return JSONResponse({"ok": False, "error": "Liste de capacités attendue."},
                            status_code=400)
    kept = sanitize_selection(merchant.get("plan"), ids)
    try:
        set_merchant_capabilities(merchant_id, serialize_caps(kept))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    merchant["enabled_capabilities"] = serialize_caps(kept)
    return {"ok": True, "active": sorted(effective_capabilities(merchant)), "modules": kept}


@app.post("/api/merchants/{merchant_id}/inbox/mode")
async def merchant_inbox_mode(request: Request, merchant_id: str):
    """Le commerçant choisit comment l'agent gère ses réponses email :
    'review' (il valide chaque réponse) ou 'auto' (l'agent envoie directement)."""
    from db.client import set_merchant_inbox_mode
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    mode = "auto" if str(body.get("mode")).strip().lower() == "auto" else "review"
    try:
        set_merchant_inbox_mode(merchant_id, mode)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "mode": mode}


@app.post("/api/merchants/{merchant_id}/inbox/draft/{row_id}")
async def merchant_inbox_draft(request: Request, merchant_id: str, row_id: str):
    """Valide (envoie), modifie+envoie, ou rejette un brouillon de réponse.

    body : {action:'send'|'reject', body?:'texte modifié'}.
    """
    from db.client import (get_inbox_row, get_merchant, record_inbox,
                           set_inbox_row)
    from core.prospecting import merchant_email_alias, send_email, _unsub_footer
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    action = str(body.get("action") or "send").strip().lower()
    row = get_inbox_row(row_id)
    if not row or row.get("merchant_id") != merchant_id or row.get("status") != "draft":
        return JSONResponse({"ok": False, "error": "Brouillon introuvable."}, status_code=404)

    if action == "reject":
        set_inbox_row(row_id, {"status": "rejected"})
        return {"ok": True, "action": "reject"}

    # Envoi : texte éventuellement modifié par le commerçant
    text = (body.get("body") or row.get("body") or "").strip()
    to_email = row.get("prospect_email") or ""
    merchant = get_merchant(merchant_id) or {}
    alias = merchant_email_alias(merchant)
    subject = row.get("subject") or "Votre message"
    full = text + "\n\n" + _unsub_footer(to_email)
    res = send_email(to_email, subject, full, reply_to=alias,
                     from_name=merchant.get("business_name") or "Boutique",
                     from_address=alias)
    if not res.get("ok"):
        return JSONResponse({"ok": False, "error": res.get("error") or "Envoi impossible."},
                            status_code=502)
    # Le brouillon devient la réponse envoyée
    set_inbox_row(row_id, {"status": "sent", "body": text})
    return {"ok": True, "action": "send"}


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

# ---------------------------------------------------------------------------
# Logique d'agent PARTAGÉE entre les transports WhatsApp (Twilio sandbox + Meta prod)
# ---------------------------------------------------------------------------

def _agent_handle(customer: str, body_text: str, has_audio: bool = False,
                  transcribe_fn=None) -> dict:
    """Traite un message client entrant → {status, text, media}. Indépendant du canal.

    Identification boutique (code vendora: ou session), garde suspension/expiration,
    vocal, opt-out, réponse du vendeur IA (leçons + variante A/B), photos.
    `transcribe_fn` : callable ()→str|None, appelé seulement si has_audio ET après
    identification de la boutique (on ne transcrit pas pour rien).
    """
    from core import brain
    from db.client import (
        add_optout,
        days_left as _days_left,
        get_active_lessons,
        get_merchant,
        get_merchant_by_code,
        get_wa_session_merchant_id,
        list_products,
        load_history,
        save_message,
        upsert_wa_session,
    )

    body = (body_text or "").strip()

    merchant = None
    m = re.search(r"vendora:([A-Za-z0-9]+)", body, re.I)
    if m:
        merchant = get_merchant_by_code(m.group(1).lower())
        if merchant:
            try:
                upsert_wa_session(customer, merchant["id"])
            except Exception:
                log.warning("wa session upsert échoué", exc_info=True)
    if not merchant and customer:
        try:
            mid = get_wa_session_merchant_id(customer)
            if mid:
                merchant = get_merchant(mid)
        except Exception:
            log.warning("wa session lookup échoué", exc_info=True)

    if not merchant:
        return {"status": "greeting", "media": [], "text":
                "Bonjour 🌟 Pour discuter avec une boutique, ouvrez son lien Vendora "
                "(ou demandez-lui de vous l'envoyer). À très vite !"}

    _exp = _days_left(merchant)
    if merchant.get("status") == "suspended" or (_exp is not None and _exp <= 0):
        return {"status": "unavailable", "media": [], "text":
                "Cette boutique est momentanément indisponible. Merci de réessayer plus tard 🙏"}

    from core.capabilities import has_capability
    if has_audio and not has_capability(merchant, "vocal"):
        # Forfait sans le module « notes vocales » → on invite à écrire (pas de transcription).
        return {"status": "no_vocal", "media": [], "text":
                "Je préfère que vous m'écriviez votre demande en quelques mots 🙏 "
                "Je vous réponds tout de suite !"}
    if has_audio and transcribe_fn:
        spoken = None
        try:
            spoken = transcribe_fn()
        except Exception:  # noqa: BLE001
            log.warning("transcription échouée", exc_info=True)
        if not spoken:
            return {"status": "audio_fail", "media": [], "text":
                    "Je n'ai pas réussi à écouter votre vocal 🙏 Pouvez-vous l'écrire en quelques mots ?"}
        clean = spoken
    else:
        clean = re.sub(r"\(?\s*vendora:[A-Za-z0-9]+\s*\)?", "", body, flags=re.I).strip() or "Bonjour"

    if clean.strip().lower() in {"stop", "stopp", "unsubscribe", "désabonner",
                                 "desabonner", "arret", "arrêt", "arreter", "arrêter"}:
        try:
            add_optout(customer, "whatsapp", "stop")
        except Exception:  # noqa: BLE001
            log.warning("optout WhatsApp échoué", exc_info=True)
        return {"status": "optout", "media": [], "text":
                "C'est noté ✅ Vous ne recevrez plus de messages. Écrivez-nous quand vous voulez revenir 🙏"}

    save_message(merchant["id"], customer, "customer", clean)
    history = load_history(merchant["id"], customer, limit=brain.HISTORY_LIMIT)
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

    try:
        lessons = get_active_lessons(merchant["id"])
    except Exception:  # noqa: BLE001
        lessons = ""
    try:
        from core.experiment import pick_variant_text
        vtext = pick_variant_text(merchant["id"], customer)
        if vtext:
            lessons = (lessons + "\n\n" + vtext) if lessons else vtext
    except Exception:  # noqa: BLE001
        pass

    answer = brain.reply(
        merchant, products, history,
        on_order=_order_recorder(merchant, customer),
        on_escalate=_escalation_notifier(merchant, customer),
        on_show=_on_show,
        on_appointment=_appointment_recorder(merchant, customer),
        lessons=lessons,
    )
    save_message(merchant["id"], customer, "assistant", answer)
    return {"status": "reply", "text": answer, "media": media_urls}


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
    """Reçoit un message WhatsApp via Twilio (sandbox) et répond avec l'agent (TwiML)."""
    try:
        form = await request.form()
    except Exception:
        return _twiml("Désolé, message illisible. Réessayez 🙏")

    from_ = (form.get("From") or "").strip()      # ex : "whatsapp:+22997..."
    body = (form.get("Body") or "").strip()
    try:
        num_media = int(form.get("NumMedia") or "0")
    except (TypeError, ValueError):
        num_media = 0
    ctype0 = (form.get("MediaContentType0") or "")
    media_url0 = form.get("MediaUrl0")
    has_audio = num_media > 0 and ctype0.startswith("audio") and bool(media_url0)
    transcribe_fn = None
    if has_audio:
        from core.transcribe import transcribe_audio
        transcribe_fn = lambda: transcribe_audio(media_url0, ctype0)  # noqa: E731

    try:
        res = _agent_handle(from_, body, has_audio=has_audio, transcribe_fn=transcribe_fn)
    except Exception:  # noqa: BLE001
        log.exception("whatsapp (twilio) reply échoué")
        return _twiml("Un instant, je vérifie avec la boutique et je reviens vers vous 🙏")
    return _twiml(res["text"], res.get("media"))


# ---------------------------------------------------------------------------
# Pilier 2 — WhatsApp PRODUCTION (Meta Cloud API). Dormant tant que non configuré.
# ---------------------------------------------------------------------------

@app.get("/api/whatsapp/meta")
async def whatsapp_meta_verify(request: Request):
    """Vérification d'abonnement du webhook Meta (renvoie le hub.challenge si OK)."""
    from core import whatsapp_meta
    qp = request.query_params
    challenge = whatsapp_meta.verify_webhook(
        qp.get("hub.mode"), qp.get("hub.verify_token"), qp.get("hub.challenge"))
    if challenge is not None:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


def _process_meta_message(msg: dict) -> None:
    """Traite UN message Meta (en tâche de fond) : agent → envoi de la réponse."""
    from core import whatsapp_meta
    wa_id = (msg.get("from") or "").strip()
    if not wa_id:
        return
    customer = f"whatsapp:+{whatsapp_meta._to_digits(wa_id)}"
    has_audio = msg.get("type") == "audio" and bool(msg.get("audio_id"))
    transcribe_fn = None
    if has_audio:
        from core.transcribe import transcribe_bytes
        aid, actype = msg.get("audio_id"), msg.get("audio_ctype")

        def transcribe_fn():  # noqa: E306
            got = whatsapp_meta.fetch_media(aid)
            return transcribe_bytes(got[0], got[1]) if got else None

    try:
        res = _agent_handle(customer, msg.get("text") or "", has_audio=has_audio,
                            transcribe_fn=transcribe_fn)
    except Exception:  # noqa: BLE001
        log.exception("whatsapp (meta) reply échoué")
        whatsapp_meta.send_text(wa_id, "Un instant, je reviens vers vous 🙏")
        return
    whatsapp_meta.send_text(wa_id, res["text"])
    for url in (res.get("media") or []):
        whatsapp_meta.send_image(wa_id, url)


@app.post("/api/whatsapp/meta")
async def whatsapp_meta_webhook(request: Request, bg: BackgroundTasks):
    """Reçoit les messages WhatsApp via Meta Cloud API. Répond 200 vite, traite en fond."""
    from core import whatsapp_meta
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored"}
    for msg in whatsapp_meta.parse_incoming(payload):
        bg.add_task(_process_meta_message, msg)
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Inbound Messenger + Instagram Direct (Meta Messenger Platform). Dormant tant
# que le PAGE token n'est pas configuré. Réutilise _agent_handle (canal-agnostique).
# ---------------------------------------------------------------------------

@app.get("/api/messenger/meta")
async def messenger_meta_verify(request: Request):
    """Vérification d'abonnement du webhook Messenger/Instagram (hub.challenge)."""
    from core import messenger_meta
    qp = request.query_params
    challenge = messenger_meta.verify_webhook(
        qp.get("hub.mode"), qp.get("hub.verify_token"), qp.get("hub.challenge"))
    if challenge is not None:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


def _process_messenger_message(msg: dict) -> None:
    """Traite UN message Messenger/Instagram (tâche de fond) : agent → réponse."""
    from core import messenger_meta
    sender = (msg.get("from") or "").strip()
    if not sender:
        return
    platform = msg.get("platform") or "messenger"
    customer = f"{platform}:{sender}"  # distinct des clients WhatsApp (whatsapp:+…)

    # Résolution Page/compte IG → boutique : un visiteur Messenger/IG dit juste
    # « Bonjour » (pas de code vendora:). On mappe l'ID de la Page à un code boutique
    # via bia_settings (clé page_merchant_{page_id}) et on pré-amorce la session.
    page_id = (msg.get("page_id") or "").strip()
    if page_id:
        try:
            from db.client import (get_merchant_by_code, get_setting,
                                   get_wa_session_merchant_id, upsert_wa_session)
            if not get_wa_session_merchant_id(customer):
                code = get_setting(f"page_merchant_{page_id}")
                if code:
                    mer = get_merchant_by_code(str(code).strip().lower())
                    if mer:
                        upsert_wa_session(customer, mer["id"])
        except Exception:  # noqa: BLE001
            log.warning("messenger page→boutique mapping échoué", exc_info=True)

    # Garde capacité : la boutique doit avoir le module « multi-canal » (Messenger/IG).
    # Si la boutique est connue mais hors forfait, l'agent ne répond pas sur ce canal.
    try:
        from core.capabilities import has_capability
        from db.client import get_merchant, get_wa_session_merchant_id
        _mid = get_wa_session_merchant_id(customer)
        if _mid:
            _m = get_merchant(_mid)
            if _m and not has_capability(_m, "multicanal"):
                return
    except Exception:  # noqa: BLE001
        log.warning("messenger multicanal gate échoué", exc_info=True)

    has_audio = msg.get("type") == "audio" and bool(msg.get("audio_url"))
    transcribe_fn = None
    if has_audio:
        from core.transcribe import transcribe_bytes
        aurl, actype = msg.get("audio_url"), msg.get("audio_ctype")

        def transcribe_fn():  # noqa: E306
            got = messenger_meta.fetch_media(aurl)
            return transcribe_bytes(got[0], got[1]) if got else None

    try:
        res = _agent_handle(customer, msg.get("text") or "", has_audio=has_audio,
                            transcribe_fn=transcribe_fn)
    except Exception:  # noqa: BLE001
        log.exception("messenger reply échoué")
        messenger_meta.send_text(sender, "Un instant, je reviens vers vous 🙏")
        return
    messenger_meta.send_text(sender, res["text"])
    for url in (res.get("media") or []):
        messenger_meta.send_image(sender, url)


# --- Comment-to-DM : acquisition sociale CONFORME (Meta « Private Replies ») ----
# Quand quelqu'un commente une publication d'une boutique, l'agent lui répond en
# privé (DM opt-in : le commentaire = son consentement). Cold DM = interdit Meta,
# on ne le fait JAMAIS. OFF par défaut (toggle cockpit). Opener templaté = ZÉRO
# appel modèle ; le cerveau ne s'allume que si le client répond dans le DM.

_c2dm_seen: set[str] = set()        # dédup des commentaires déjà traités (webhooks Meta rejouent)
_c2dm_order: deque[str] = deque()   # ordre FIFO pour borner la mémoire à 1000


def _c2dm_is_new(comment_id: str) -> bool:
    """True si ce commentaire n'a pas encore été traité. Borne mémoire à 1000.

    Backstop : Meta refuse de toute façon une 2e réponse privée au même commentaire.
    """
    if comment_id in _c2dm_seen:
        return False
    _c2dm_seen.add(comment_id)
    _c2dm_order.append(comment_id)
    if len(_c2dm_order) > 1000:
        _c2dm_seen.discard(_c2dm_order.popleft())
    return True


def _process_comment(c: dict) -> None:
    """Traite UN commentaire (tâche de fond) : réponse privée (DM) + ack public."""
    from core import messenger_meta
    from db.client import (days_left, get_merchant_by_code, get_setting,
                           get_setting_bool, upsert_wa_session)
    if not messenger_meta.configured():
        return
    if not get_setting_bool("c2dm_enabled", False):
        return  # OFF par défaut
    comment_id = (c.get("comment_id") or "").strip()
    page_id = (c.get("page_id") or "").strip()
    if not (comment_id and page_id):
        return
    if not _c2dm_is_new(comment_id):
        return
    # On n'agit QUE sur les Pages associées à une boutique connue (jamais d'inconnu).
    code = get_setting(f"page_merchant_{page_id}")
    if not code:
        return
    merchant = get_merchant_by_code(str(code).strip().lower())
    if not merchant:
        return
    from core.capabilities import has_capability
    if not has_capability(merchant, "comment_to_dm"):
        return  # acquisition sociale = capacité du forfait (Empire)
    exp = days_left(merchant)
    if merchant.get("status") == "suspended" or (exp is not None and exp <= 0):
        return  # boutique suspendue/expirée → pas de DM
    # Filtre mot-clé optionnel : ne répondre qu'aux commentaires pertinents.
    kw = (get_setting("c2dm_keyword") or "").strip().lower()
    if kw and kw not in (c.get("text") or "").lower():
        return
    platform = c.get("platform") or "messenger"
    # Pré-amorce la session DM → la réponse du client tombera sur la bonne boutique.
    from_id = (c.get("from_id") or "").strip()
    if from_id:
        try:
            upsert_wa_session(f"{platform}:{from_id}", merchant["id"])
        except Exception:  # noqa: BLE001
            log.warning("c2dm pré-amorçage session KO", exc_info=True)
    name = merchant.get("business_name") or "notre boutique"
    opener = (f"Bonjour 🌟 Merci pour votre commentaire ! Ici {name}. Je vous "
              f"réponds en privé : dites-moi ce qui vous intéresse et je vous "
              f"renseigne tout de suite (prix, disponibilité, livraison) 😊")
    if not messenger_meta.send_private_reply(page_id, comment_id, opener):
        return
    if get_setting_bool("c2dm_public_reply", True):
        messenger_meta.reply_public_comment(
            comment_id, "Je vous réponds en message privé 📩", platform)


@app.post("/api/messenger/meta")
async def messenger_meta_webhook(request: Request, bg: BackgroundTasks):
    """Reçoit les messages Messenger + Instagram Direct. Répond 200 vite, traite en fond."""
    from core import messenger_meta
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored"}
    for msg in messenger_meta.parse_incoming(payload):
        bg.add_task(_process_messenger_message, msg)
    for c in messenger_meta.parse_comments(payload):
        bg.add_task(_process_comment, c)
    return {"status": "ok"}


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
    # Essai 3 jours : jours restants + preuve de valeur (à afficher dans la page).
    trial = None
    if merchant and merchant.get("is_trial"):
        from db.client import days_left, trial_stats
        trial = {"days_left": max(0, days_left(merchant) or 0), "stats": trial_stats(merchant_id)}
    return templates.TemplateResponse(
        request, "essai.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id, price=price,
             plan_label=plan_label, wa_link=wa_link, trial=trial),
    )


@app.post("/api/chat")
async def chat(request: Request):
    """Reçoit un message client, fait répondre le vendeur IA, persiste la conversation."""
    from core import brain
    from db.client import (
        count_customer_messages,
        get_active_lessons,
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
        try:
            lessons = get_active_lessons(merchant_id)
        except Exception:  # noqa: BLE001
            lessons = ""
        if not preview:  # pas d'A/B sur l'essai gratuit (ne pollue pas les stats de conversion)
            try:
                from core.experiment import pick_variant_text
                vtext = pick_variant_text(merchant_id, customer)
                if vtext:
                    lessons = (lessons + "\n\n" + vtext) if lessons else vtext
            except Exception:  # noqa: BLE001
                pass
        answer = brain.reply(merchant, products, history, on_order=on_order,
                             on_escalate=on_escalate, lessons=lessons)
        save_message(merchant_id, customer, "assistant", answer)

        remaining = None
        if preview and merchant.get("status") != "active":
            remaining = max(0, limit - count_customer_messages(merchant_id, customer))
    except Exception as e:  # noqa: BLE001
        log.exception("chat échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)

    return {"ok": True, "reply": answer, "remaining": remaining, "trial_over": False}
