"""Boutique IA — serveur FastAPI (ÉTAGE 1 : inscription self-service).

Lancer en local :
    cd boutique-ia
    uvicorn web.server:app --reload --port 8010
Puis ouvrir http://localhost:8010/
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from config import settings

log = logging.getLogger("boutique-ia.server")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=settings.product_name, description=settings.product_tagline)


def _ctx(request: Request, **extra) -> dict:
    base = {
        "product_name": settings.product_name,
        "tagline": settings.product_tagline,
        "price": settings.saas_price_fcfa,
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
    return templates.TemplateResponse(
        request, "activation.html", _ctx(request, merchant=merchant, merchant_id=merchant_id)
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
