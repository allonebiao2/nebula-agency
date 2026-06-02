"""Boutique IA — serveur FastAPI (ÉTAGE 1 : inscription self-service).

Lancer en local :
    cd boutique-ia
    uvicorn web.server:app --reload --port 8010
Puis ouvrir http://localhost:8010/
"""
from __future__ import annotations

import logging
import re
import secrets
import string
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import normalize_plan, price_for_plan, settings


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
        order = create_order(
            merchant_id=merchant["id"],
            customer_whatsapp=customer_whatsapp,
            items=items,
            total=data.get("total"),
            delivery_mode=(data.get("mode_livraison") or "").strip() or None,
            delivery_address=(data.get("adresse") or "").strip() or None,
            customer_name=(data.get("nom_client") or "").strip() or None,
        )
        try:
            notify_new_order(merchant, order, items)
        except Exception:  # noqa: BLE001
            log.warning("alerte commande échouée", exc_info=True)

    return _on_order

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
# ÉTAGE 2b — WhatsApp réel (webhook Twilio, réponse TwiML)
# ---------------------------------------------------------------------------

def _twiml(message: str) -> Response:
    """Réponse TwiML : Twilio enverra ce message au client. Pas besoin de clé API."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(message)}</Message></Response>"
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

    # 2. Nettoyer le marqueur de routing du message
    clean = re.sub(r"\(?\s*vendora:[A-Za-z0-9]+\s*\)?", "", body, flags=re.I).strip() or "Bonjour"

    # 3. Faire répondre l'agent vendeur
    try:
        save_message(merchant["id"], from_, "customer", clean)
        history = load_history(merchant["id"], from_, limit=brain.HISTORY_LIMIT)
        products = list_products(merchant["id"])
        answer = brain.reply(
            merchant, products, history, on_order=_order_recorder(merchant, from_)
        )
        save_message(merchant["id"], from_, "assistant", answer)
    except Exception as e:  # noqa: BLE001
        log.exception("whatsapp reply échoué")
        return _twiml("Un instant, je vérifie avec la boutique et je reviens vers vous 🙏")

    return _twiml(answer)


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
        answer = brain.reply(merchant, products, history, on_order=on_order)
        save_message(merchant_id, customer, "assistant", answer)

        remaining = None
        if preview and merchant.get("status") != "active":
            remaining = max(0, limit - count_customer_messages(merchant_id, customer))
    except Exception as e:  # noqa: BLE001
        log.exception("chat échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)

    return {"ok": True, "reply": answer, "remaining": remaining, "trial_over": False}
