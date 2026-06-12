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

from fastapi import BackgroundTasks, FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
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


def _wa_short_link(code: str) -> str:
    """Lien COURT et propre à partager (redirige vers le vrai lien wa.me).
    Ex: https://vendora-agent.up.railway.app/go/3cdfd1 — pas de `vendora:` visible."""
    if not code:
        return ""
    base = (settings.public_base_url or "").rstrip("/")
    return f"{base}/go/{code}"


def _qr_data_uri(text: str) -> str:
    """QR code (PNG base64) d'un lien — affichable/imprimable dans le back-office.
    Le client le met sur sa boutique/ses réseaux ; ses clients scannent → WhatsApp."""
    if not text:
        return ""
    try:
        import base64
        import io

        import qrcode
        buf = io.BytesIO()
        qrcode.make(text).save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:  # noqa: BLE001
        logging.getLogger("boutique-ia.server").warning("génération QR échouée", exc_info=True)
        return ""

log = logging.getLogger("boutique-ia.server")

_AG_JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_AG_MOIS = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.",
            "août", "sept.", "oct.", "nov.", "déc."]


def _build_agenda(merchant: dict, appointments: list) -> dict:
    """Assemble la vue Agenda : demandes à planifier + RDV groupés par jour (14 j)."""
    from datetime import datetime, timedelta, timezone
    wat = timezone(timedelta(hours=1))
    today = datetime.now(wat).date()

    def _p(s):
        try:
            dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
            return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(wat)
        except Exception:  # noqa: BLE001
            return None

    weekdays = {int(x) for x in (merchant.get("rdv_weekdays") or "").split(",")
                if x.strip().isdigit()}
    off_dates = {d.strip() for d in (merchant.get("rdv_off_dates") or "").split(",") if d.strip()}

    by_day: dict[str, list] = {}
    pending: list = []
    for a in appointments:
        if a.get("status") == "cancelled":
            continue
        dt = _p(a.get("scheduled_at")) if a.get("scheduled_at") else None
        if dt:
            row = dict(a)
            row["_time"] = dt.strftime("%Hh%M")
            by_day.setdefault(dt.date().isoformat(), []).append((dt, row))
        elif a.get("status") == "pending":
            pending.append(a)

    days = []
    for i in range(14):
        d = today + timedelta(days=i)
        diso = d.isoformat()
        is_off = (diso in off_dates) or (bool(weekdays) and (d.weekday() + 1) not in weekdays)
        items = [r for _dt, r in sorted(by_day.get(diso, []), key=lambda t: t[0])]
        if not items and is_off:
            continue  # jour fermé et vide → on n'encombre pas
        days.append({"label": f"{_AG_JOURS[d.weekday()]} {d.day} {_AG_MOIS[d.month]}",
                     "iso": diso, "today": i == 0, "is_off": is_off, "items": items})
    return {"days": days, "pending": pending,
            "weekdays": sorted(weekdays), "off_dates": sorted(off_dates)}


def _wat_iso(date_s: str | None, time_s: str | None) -> str | None:
    """Construit un timestamptz ISO en heure du Bénin depuis 'YYYY-MM-DD' + 'HH:MM'."""
    from datetime import datetime, timedelta, timezone
    try:
        d = datetime.strptime((date_s or "").strip(), "%Y-%m-%d")
        parts = ((time_s or "09:00").strip() + ":00").split(":")
        dt = d.replace(hour=int(parts[0]), minute=int(parts[1]),
                       tzinfo=timezone(timedelta(hours=1)))
        return dt.isoformat()
    except Exception:  # noqa: BLE001
        return None


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


def _payment_recorder(merchant: dict, customer: str | None):
    """Callback : le client annonce un paiement → on attache la preuve à sa dernière
    commande (passe en 'à valider') et on prévient le/la propriétaire."""
    from db.client import attach_payment_to_latest_pending
    from notify import notify_payment_to_validate

    def _on_payment(data: dict) -> None:
        order = attach_payment_to_latest_pending(
            merchant["id"], customer,
            ref=(data.get("transaction_id") or "").strip() or None,
            network=(data.get("reseau") or "").strip() or None,
        )
        try:
            notify_payment_to_validate(merchant, order or {}, data)
        except Exception:  # noqa: BLE001
            log.warning("alerte paiement à valider échouée", exc_info=True)

    return _on_payment


def _escalation_notifier(merchant: dict, customer: str | None):
    """Callback appelé quand l'agent escalade un client vers le/la propriétaire."""
    from db.client import add_notification
    from notify import notify_hot_lead

    def _on_escalate(data: dict) -> None:
        raison = (data.get("raison") or "À rappeler").strip()
        resume = (data.get("resume") or "").strip()
        nom = (data.get("nom_client") or "").strip() or None
        try:
            notify_hot_lead(merchant, customer, raison=raison, resume=resume, nom_client=nom)
        except Exception:  # noqa: BLE001
            log.warning("alerte lead chaud échouée", exc_info=True)
        # On la stocke aussi pour l'onglet Notifications (en plus de Telegram/WhatsApp).
        try:
            add_notification(merchant["id"], "hot_lead",
                             title=f"{nom or 'Client'} — {raison}", body=resume,
                             customer=customer)
        except Exception:  # noqa: BLE001
            log.warning("notification lead chaud non enregistrée", exc_info=True)

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


@app.get("/confidentialite", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Politique de confidentialité + conditions d'utilisation (publique)."""
    return templates.TemplateResponse(request, "confidentialite.html", _ctx(request))


@app.get("/go/{code}")
async def wa_redirect(code: str):
    """Lien court partageable → redirige vers le vrai lien wa.me (avec le code de
    routage). Permet de partager `…/go/CODE` au lieu du long lien wa.me + vendora:."""
    target = _wa_link((code or "").strip().lower())
    return RedirectResponse(target or "/", status_code=302)


# ---------------------------------------------------------------------------
# Vendora Support — widget de chat à embarquer sur le site du client (lot 6)
# Une ligne <script src=".../widget.js?code=CODE"> → bouton lumineux + chat.
# ---------------------------------------------------------------------------
_WIDGET_JS = r'''
(function(){
  if(window.__vendoraSupport) return; window.__vendoraSupport=1;
  var C=window.VENDORA_CFG||{}; var color=C.color||'#10b981';
  var name=C.name||'nous'; var api=(C.api||'').replace(/\/+$/,''); var code=C.code||'';
  if(!code) return;
  var hist=[];
  var css=document.createElement('style'); css.textContent=
    '.vsb-btn{position:fixed;right:20px;bottom:20px;z-index:2147483000;display:flex;align-items:center;gap:9px;background:'+color+';color:#fff;border:none;border-radius:40px;padding:13px 18px;font:600 14px system-ui,sans-serif;cursor:pointer;box-shadow:0 8px 26px '+color+'66;animation:vsbp 2.2s infinite}'
   +'@keyframes vsbp{0%{box-shadow:0 8px 26px '+color+'66,0 0 0 0 '+color+'66}70%{box-shadow:0 8px 26px '+color+'66,0 0 0 16px '+color+'00}100%{box-shadow:0 8px 26px '+color+'66,0 0 0 0 '+color+'00}}'
   +'.vsb-btn svg{width:20px;height:20px}'
   +'.vsb-panel{position:fixed;right:20px;bottom:86px;z-index:2147483000;width:360px;max-width:calc(100vw - 32px);height:520px;max-height:calc(100vh - 120px);background:#fff;border-radius:18px;box-shadow:0 18px 60px rgba(0,0,0,.28);display:none;flex-direction:column;overflow:hidden;font:14px system-ui,sans-serif}'
   +'.vsb-panel.vopen{display:flex}'
   +'.vsb-h{background:'+color+';color:#fff;padding:15px 18px;font-weight:700;display:flex;justify-content:space-between;align-items:center}'
   +'.vsb-h small{display:block;font-weight:400;opacity:.85;font-size:11.5px;margin-top:2px}'
   +'.vsb-x{cursor:pointer;font-size:22px;line-height:1;background:none;border:none;color:#fff}'
   +'.vsb-m{flex:1;overflow-y:auto;padding:16px;background:#f6f7f9;display:flex;flex-direction:column;gap:9px}'
   +'.vsb-b{max-width:82%;padding:9px 12px;border-radius:14px;line-height:1.45;white-space:pre-wrap;word-wrap:break-word}'
   +'.vsb-b.u{align-self:flex-end;background:'+color+';color:#fff;border-bottom-right-radius:4px}'
   +'.vsb-b.a{align-self:flex-start;background:#fff;color:#1a1a1a;border:1px solid #e6e8ec;border-bottom-left-radius:4px}'
   +'.vsb-f{display:flex;gap:8px;padding:10px;border-top:1px solid #eee;background:#fff}'
   +'.vsb-f input{flex:1;border:1px solid #dfe2e7;border-radius:22px;padding:10px 14px;font:14px system-ui;outline:none}'
   +'.vsb-f button{background:'+color+';color:#fff;border:none;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:15px}'
   +'.vsb-c{text-align:center;font-size:10px;color:#9aa1ab;padding:5px}';
  document.head.appendChild(css);
  var btn=document.createElement('button'); btn.className='vsb-btn';
  btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg><span>Discuter avec nous</span>';
  document.body.appendChild(btn);
  var p=document.createElement('div'); p.className='vsb-panel';
  p.innerHTML='<div class="vsb-h"><div>'+name+'<small>On vous repond tout de suite</small></div><button class="vsb-x">&times;</button></div><div class="vsb-m"></div><div class="vsb-f"><input placeholder="Votre message..."><button>&#10148;</button></div><div class="vsb-c">Propulse par Vendora</div>';
  document.body.appendChild(p);
  var m=p.querySelector('.vsb-m'), inp=p.querySelector('input'), snd=p.querySelector('.vsb-f button');
  function add(r,t){var d=document.createElement('div');d.className='vsb-b '+(r==='u'?'u':'a');d.textContent=t;m.appendChild(d);m.scrollTop=m.scrollHeight;return d;}
  function op(){p.classList.add('vopen');if(!hist.length)add('a','Bonjour ! Comment puis-je vous aider ?');inp.focus();}
  btn.onclick=function(){p.classList.contains('vopen')?p.classList.remove('vopen'):op();};
  p.querySelector('.vsb-x').onclick=function(){p.classList.remove('vopen');};
  function go(){var t=inp.value.trim();if(!t)return;inp.value='';add('u',t);hist.push({role:'customer',content:t});var ty=add('a','...');
    fetch(api+'/api/support/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:code,message:t,history:hist})})
    .then(function(r){return r.json();}).then(function(d){ty.textContent=d.reply||'Desole, reessayez.';hist.push({role:'assistant',content:ty.textContent});})
    .catch(function(){ty.textContent='Connexion impossible, reessayez.';});}
  snd.onclick=go; inp.addEventListener('keydown',function(e){if(e.key==='Enter')go();});
})();
'''


@app.get("/widget.js")
async def support_widget_js(code: str = ""):
    """Sert le widget de chat support à embarquer sur le site du client."""
    import json as _json
    from db.client import get_merchant_by_code
    m = get_merchant_by_code((code or "").strip().lower()) if code else None
    cfg = _json.dumps({
        "name": (m.get("business_name") if m else "") or "nous",
        "color": (m.get("brand_color") if m else "") or "#10b981",
        "api": (getattr(settings, "public_base_url", None) or "").rstrip("/"),
        "code": (code or "").strip().lower(),
    })
    js = "window.VENDORA_CFG=" + cfg + ";\n" + _WIDGET_JS
    return Response(content=js, media_type="application/javascript",
                    headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=300"})


@app.options("/api/support/chat")
async def support_chat_preflight():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })


@app.post("/api/support/chat")
async def support_chat(request: Request):
    """Endpoint du widget : l'agent support répond aux visiteurs du site du client."""
    from core import support_agent
    from db.client import create_support_ticket, get_merchant_by_code, knowledge_text_for
    cors = {"Access-Control-Allow-Origin": "*"}
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001
        return JSONResponse({"error": "bad_json"}, status_code=400, headers=cors)
    code = (body.get("code") or "").strip().lower()
    msg = (body.get("message") or "").strip()
    merchant = get_merchant_by_code(code) if code else None
    if not merchant:
        return JSONResponse({"error": "unknown"}, status_code=404, headers=cors)
    if (merchant.get("agent_role") or "vendeur") != "support":
        return JSONResponse({"reply": "Le support en ligne n'est pas activé."}, headers=cors)
    hist = [{"role": ("assistant" if h.get("role") == "assistant" else "customer"),
             "content": (h.get("content") or "")} for h in (body.get("history") or [])[-12:]
            if h.get("content")]
    contact = (body.get("contact") or "(visiteur site web)")

    def _on_escalate(d: dict) -> None:
        try:
            create_support_ticket(merchant["id"], user_contact=contact, channel="widget",
                                  summary=d.get("probleme"), severity=d.get("gravite"))
        except Exception:  # noqa: BLE001
            pass
        try:
            _escalation_notifier(merchant, contact)(
                {"raison": "Support (site web)", "resume": d.get("probleme") or "", "nom_client": ""})
        except Exception:  # noqa: BLE001
            pass

    try:
        kb_docs = knowledge_text_for(merchant["id"])
    except Exception:  # noqa: BLE001
        kb_docs = ""
    try:
        ans = support_agent.reply(merchant, msg, history=hist,
                                  kb_text=merchant.get("kb_text") or "",
                                  kb_instructions=merchant.get("kb_instructions") or "",
                                  kb_docs=kb_docs, on_escalate=_on_escalate)
    except Exception:  # noqa: BLE001
        log.exception("support widget chat échoué")
        ans = "Désolé, petit souci technique — réessayez dans un instant 🙏"
    return JSONResponse({"reply": ans}, headers=cors)


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
        created = add_products(merchant_id, products) if merchant_id else []
        count = len(created)
        product_ids = [r.get("id") for r in created]
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

    # On ouvre une session pour la boutique tout juste créée : ça permet d'uploader
    # ses photos produits dans la foulée (et le commerçant arrive déjà connecté).
    resp = JSONResponse({"ok": True, "merchant_id": merchant_id, "products": count,
                         "product_ids": product_ids, "trial": bool(trial)})
    if merchant_id:
        resp.set_cookie(SESSION_COOKIE, _make_session(merchant_id),
                        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax", path="/")
    return resp


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

    merchant, products, gallery = None, [], {}
    stats = {"count": 0, "revenue": 0}
    recent_orders, conversations, plans, campaigns = [], [], [], []
    plan, plan_label = "demarrage", "Démarrage"
    daily_limit, used_today = 5, 0
    prospect_daily, prospect_used = 0, 0
    try:
        merchant = get_merchant(merchant_id)
        if merchant:
            products = list_products(merchant_id)
            from db.client import product_images_map as _pim
            gallery = _pim(merchant_id)
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
    wa_link = _wa_short_link(merchant.get("code")) if merchant else ""
    remaining = -1 if daily_limit < 0 else max(0, daily_limit - used_today)
    accent = (merchant.get("brand_color") if merchant else None) or "#10b981"
    cats = [{"key": k, "label": v["label"]} for k, v in CATEGORIES.items()]
    from core.capabilities import BY_ID, capabilities_context, has_capability
    caps_ctx = capabilities_context(merchant) if merchant else None
    prospection_soon = bool(BY_ID.get("prospection", {}).get("soon"))
    # Guide de démarrage : rend le back-office explicite dès l'arrivée (étapes + état).
    guide = None
    if merchant:
        is_active = merchant.get("status") == "active" and not merchant.get("is_trial")
        steps = [
            {"title": "Indiquez votre numéro WhatsApp",
             "desc": "Le numéro où vos clients vous écrivent. Votre agent y répondra pour vous, jour et nuit.",
             "done": bool(merchant.get("whatsapp_business")), "target": "whatsapp", "cta": "Indiquer"},
            {"title": "Ajoutez vos produits ou services",
             "desc": "Donnez à votre agent de quoi vendre : nom, prix, photo. Astuce : « Import express » colle toute votre liste d'un coup.",
             "done": bool(products), "target": "produits", "cta": "Ajouter"},
            {"title": "Composez votre vendeur",
             "desc": "Cochez ce qu'il sait faire : photos, paiement à la livraison, rendez-vous, notes vocales…",
             "done": bool(merchant.get("enabled_capabilities")), "target": "capacites", "cta": "Configurer"},
            {"title": "Réglez paiement & livraison",
             "desc": "Votre numéro Mobile Money et vos zones de livraison, pour qu'il conclue les ventes tout seul.",
             "done": bool(merchant.get("momo_number")), "target": "livraison", "cta": "Renseigner"},
            {"title": "Testez votre agent",
             "desc": "Discutez avec lui comme un vrai client. Vous verrez : il vend déjà.",
             "done": None, "href": f"/essai/{merchant_id}", "cta": "Tester"},
            {"title": "Partagez votre lien WhatsApp",
             "desc": "Collez-le dans votre bio Instagram, votre statut WhatsApp, vos flyers. Vos clients arrivent direct sur votre vendeur.",
             "done": None, "target": "whatsapp", "cta": "Voir mon lien"},
        ]
        if not is_active:
            steps.append({"title": "Activez votre abonnement",
                          "desc": "Pour que votre agent travaille 24h/24, en vrai, sans interruption.",
                          "done": False, "href": f"/activation/{merchant_id}", "cta": "Activer"})
        tracked = [s for s in steps if s["done"] is not None]
        # Étape « à faire maintenant » : la 1re non terminée (parmi celles à état trackable).
        _cur = next((s for s in steps if s["done"] is False), None)
        for s in steps:
            s["current"] = (s is _cur)
        guide = {"steps": steps, "done": sum(1 for s in tracked if s["done"]),
                 "total": len(tracked), "all_done": all(s["done"] for s in tracked)}
    # Bannière essai : seulement pendant l'essai RÉEL (active + jours restants > 0).
    # Bannière « en pause » : pour toute boutique suspendue (essai fini OU abo expiré).
    trial = None
    suspended = bool(merchant and merchant.get("status") == "suspended")
    if merchant and merchant.get("is_trial") and merchant.get("status") == "active":
        from db.client import days_left as _days_left_bo
        _dl = _days_left_bo(merchant)
        if _dl is not None and _dl > 0:
            trial = {"days_left": _dl}
    rdv_on = bool(merchant) and has_capability(merchant, "rdv")
    appointments, agenda = [], None
    if rdv_on:
        try:
            from db.client import list_appointments
            appointments = list_appointments(merchant_id, limit=200)
            agenda = _build_agenda(merchant, appointments)
        except Exception:  # noqa: BLE001
            log.warning("back-office: lecture RDV KO", exc_info=True)
    social_on = bool(merchant) and has_capability(merchant, "social")
    social_images_on = bool(merchant) and has_capability(merchant, "social_images")
    social_posts = []
    if social_on:
        try:
            from db.client import get_latest_social_posts
            social_posts = get_latest_social_posts(merchant_id)
        except Exception:  # noqa: BLE001
            log.warning("back-office: lecture social KO", exc_info=True)
    social_publish_ready = False
    if social_on:
        try:
            from core import messenger_meta
            social_publish_ready = messenger_meta.configured() and bool(_merchant_facebook_page(merchant))
        except Exception:  # noqa: BLE001
            social_publish_ready = False
    coach_on = bool(merchant) and has_capability(merchant, "coach")
    coaching = None
    if coach_on:
        try:
            from db.client import get_latest_coaching
            coaching = get_latest_coaching(merchant_id)
        except Exception:  # noqa: BLE001
            log.warning("back-office: lecture coaching KO", exc_info=True)
    # Metering : conversations clients ce mois (soft cap — informatif + nudge).
    usage = None
    if merchant:
        try:
            from config import CREDIT_PACKS
            from db.client import conversation_usage
            usage = conversation_usage(merchant)
            usage["packs"] = CREDIT_PACKS
        except Exception:  # noqa: BLE001
            log.warning("back-office: usage KO", exc_info=True)
    # Validation des paiements + Notifications (alertes dans le back-office).
    to_validate, notif = [], None
    if merchant:
        try:
            from db.client import (
                days_left as _dleft,
                list_notifications,
                list_orders_to_validate,
            )
            to_validate = list_orders_to_validate(merchant_id, limit=50)
            pay_count = sum(1 for o in to_validate if o.get("status") == "paid_pending_validation")
            pend_orders = sum(1 for o in to_validate if o.get("status") == "pending")
            pend_appts = [a for a in (appointments or []) if a.get("status") == "pending"]
            hot_leads = [h for h in list_notifications(merchant_id, "unread", limit=20)
                         if h.get("type") == "hot_lead"]
            for h in hot_leads:  # lien « Rappeler » si c'est un numéro WhatsApp
                cust = h.get("customer") or ""
                digits = re.sub(r"\D", "", cust)
                h["call"] = f"https://wa.me/{digits}" if cust.startswith("whatsapp:") and digits else None
            from datetime import datetime, timedelta, timezone
            from db.client import birthdays_today, low_stock as _low
            low = _low(merchant_id)
            mmdd = datetime.now(timezone(timedelta(hours=1))).strftime("%m-%d")
            bdays = birthdays_today(merchant_id, mmdd)
            notif = {
                "pay_count": pay_count,
                "pending_orders": pend_orders,
                "appts": len(pend_appts),
                "appointments": pend_appts[:10],
                "hot_leads": hot_leads,
                "hot_count": len(hot_leads),
                "low_stock": low,
                "low_count": len(low),
                "birthdays": bdays,
                "bday_count": len(bdays),
                "days_left": _dleft(merchant),
                "suspended": suspended,
                "total": pay_count + len(pend_appts) + len(hot_leads) + len(low) + len(bdays),
            }
        except Exception:  # noqa: BLE001
            log.warning("back-office: validation/notif KO", exc_info=True)
    # QR du lien WhatsApp (à imprimer/partager) + lien du back-office (à enregistrer).
    wa_qr = _qr_data_uri(wa_link)
    backoffice_link = str(request.base_url).rstrip("/") + f"/boutique/{merchant_id}"
    # Support in-app : fil d'aide + indication si l'équipe NEBULA gère manuellement.
    support_thread, support_human = [], False
    if merchant:
        try:
            from db.client import get_setting_bool as _gsb, list_support_thread
            support_thread = list_support_thread(merchant_id, limit=40)
            support_human = _gsb(f"support_human_{merchant_id}", False)
        except Exception:  # noqa: BLE001
            log.warning("back-office: support KO", exc_info=True)
    # Mini-outils : caisse (jour/mois/total), ardoise (dettes), documents, fidélité.
    cashbox, ardoise, documents, top_clients = None, None, [], []
    catalogue_link = ""
    if merchant:
        try:
            from datetime import datetime, timedelta, timezone
            from db.client import (cash_summary, debts_total, list_cash, list_debts,
                                   list_documents, top_customers)
            wat = timezone(timedelta(hours=1))
            now = datetime.now(wat)
            today_iso = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat()
            month_iso = (now - timedelta(days=30)).astimezone(timezone.utc).isoformat()
            cashbox = {"today": cash_summary(merchant_id, today_iso),
                       "month": cash_summary(merchant_id, month_iso),
                       "all": cash_summary(merchant_id, None),
                       "entries": list_cash(merchant_id, 12)}
            ardoise = {"total": debts_total(merchant_id),
                       "debts": list_debts(merchant_id, "open", 50)}
            documents = list_documents(merchant_id, 20)
            top_clients = top_customers(merchant_id, 12)
            if merchant.get("code"):
                catalogue_link = str(request.base_url).rstrip("/") + f"/catalogue/{merchant.get('code')}"
        except Exception:  # noqa: BLE001
            log.warning("back-office: mini-outils KO", exc_info=True)
    support_role = (merchant.get("agent_role") or "vendeur") == "support"
    try:
        from db.client import list_support_tickets
        support_tickets = list_support_tickets(merchant_id, "open", 30) if support_role else []
    except Exception:  # noqa: BLE001
        support_tickets = []
    try:
        from db.client import list_knowledge
        kb_docs_list = list_knowledge(merchant_id) if support_role else []
    except Exception:  # noqa: BLE001
        kb_docs_list = []
    public_base = (getattr(settings, "public_base_url", None) or str(request.base_url)).rstrip("/")
    return templates.TemplateResponse(
        request, "boutique.html",
        _ctx(request, merchant=merchant, merchant_id=merchant_id,
             products=products, gallery=gallery, wa_link=wa_link, stats=stats,
             recent_orders=recent_orders, conversations=conversations,
             plan=plan, plan_label=plan_label, plans=plans, accent=accent,
             daily_limit=daily_limit, used_today=used_today, remaining=remaining,
             categories=cats, campaigns=campaigns, inbox=inbox, caps=caps_ctx,
             guide=guide, trial=trial, suspended=suspended, rdv_on=rdv_on, appointments=appointments, agenda=agenda,
             social_on=social_on, social_images_on=social_images_on, social_posts=social_posts,
             social_publish_ready=social_publish_ready,
             coach_on=coach_on, coaching=coaching, usage=usage,
             to_validate=to_validate, notif=notif,
             wa_qr=wa_qr, backoffice_link=backoffice_link,
             support_thread=support_thread, support_human=support_human,
             cashbox=cashbox, ardoise=ardoise, documents=documents,
             top_clients=top_clients, catalogue_link=catalogue_link,
             prospect_daily=prospect_daily, prospect_used=prospect_used, prospection_soon=prospection_soon,
             prospect_remaining=max(0, prospect_daily - prospect_used),
             support_role=support_role, support_tickets=support_tickets,
             kb_docs_list=kb_docs_list, public_base=public_base),
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
        conversation_usage,
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
        try:
            usage = conversation_usage(m)
        except Exception:  # noqa: BLE001
            usage = None
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
            "usage": usage,
            "credits": int(m.get("conv_credits") or 0),
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
        "winback_enabled": get_setting_bool("winback_enabled", False),
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
    # Support in-app : fils d'aide des commerçants (Mongazi répond / reprend la main).
    from db.client import list_support_thread, support_threads_overview
    mname = {m.get("id"): m for m in merchants}
    support_threads = []
    for t in support_threads_overview():
        m = mname.get(t["merchant_id"])
        if not m:
            continue
        support_threads.append({
            "merchant_id": t["merchant_id"],
            "name": m.get("business_name") or "—",
            "last": t.get("last"), "last_role": t.get("last_role"),
            "open": get_setting_bool(f"support_open_{t['merchant_id']}", False),
            "human": get_setting_bool(f"support_human_{t['merchant_id']}", False),
            "thread": list_support_thread(t["merchant_id"], 12),
        })
    support_threads.sort(key=lambda x: 0 if x["open"] else 1)
    support_open_count = sum(1 for x in support_threads if x["open"])

    from core import model_config
    from db.client import usage_summary
    costs = usage_summary(30)  # F3 — coût IA réel des 30 derniers jours
    return templates.TemplateResponse(
        request, "admin.html",
        _ctx(request, token=token, rows=rows, pending=pending, glob=glob,
             model_cfg=model_config.current_config(), costs=costs,
             categories=cats, campaigns=campaigns,
             prospect_used=prospect_used, prospect_daily=settings.prospection_admin_daily,
             auto_enabled=auto_enabled, auto_daily=auto_daily,
             total_recruited=total_recruited, learn=learn, followups=followups,
             ceo=ceo, experiments=experiments, channels=channels, inbox=inbox,
             support_threads=support_threads, support_open_count=support_open_count),
    )


@app.post("/api/admin/merchants/{merchant_id}/activate")
async def admin_activate(request: Request, merchant_id: str):
    from db.client import activate_merchant
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        m = activate_merchant(merchant_id)
        if m:
            try:
                from notify import notify_activated
                notify_activated(m)
            except Exception:  # noqa: BLE001
                log.warning("notif activation commerçant échouée", exc_info=True)
    except Exception as e:  # noqa: BLE001
        log.exception("admin activate échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": bool(m), "merchant": m}


@app.post("/api/admin/assistant")
async def admin_assistant_endpoint(request: Request):
    """L'assistant FONDATEUR (copilote business de Mongazi) dans le cockpit."""
    from core import assistant
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    question = (body.get("message") or "").strip()
    if not question:
        return JSONResponse({"ok": False, "error": "Question vide."}, status_code=400)
    history = body.get("history") if isinstance(body.get("history"), list) else None
    try:
        answer = assistant.admin_reply(question, history=history)
    except Exception as e:  # noqa: BLE001
        log.exception("assistant fondateur échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    return {"ok": True, "reply": answer}


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


@app.post("/api/admin/merchants/{merchant_id}/credits")
async def admin_add_credits(request: Request, merchant_id: str):
    """Crédite des conversations à une boutique (après une recharge MoMo reçue).

    Encaissement MoMo manuel (comme l'activation) : Mongazi valide → on ajoute les
    crédits. `pack` (id de config.CREDIT_PACKS) OU `conversations` (nombre direct,
    peut être négatif pour corriger). Action ADMIN — Mongazi pilote le financier.
    """
    from config import CREDIT_PACKS_BY_ID
    from db.client import add_conversation_credits
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    n = 0
    pack = (body.get("pack") or "").strip()
    if pack and pack in CREDIT_PACKS_BY_ID:
        n = CREDIT_PACKS_BY_ID[pack]["conversations"]
    else:
        try:
            n = int(body.get("conversations") or 0)
        except (TypeError, ValueError):
            n = 0
    if not n:
        return JSONResponse({"ok": False, "error": "Indiquez un pack ou un nombre de conversations."},
                            status_code=400)
    m = add_conversation_credits(merchant_id, n)
    if not m:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    return {"ok": True, "credits": int(m.get("conv_credits") or 0), "added": n}


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


@app.post("/api/admin/models")
async def admin_models(request: Request):
    """Modèle + effort par tâche (vendeur / manager / rédaction / créatif-CEO) — en direct, sans redeploy."""
    from core import model_config
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001
        body = {}
    cfg = model_config.save_config(body or {})
    return {"ok": True, "config": cfg}


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


@app.post("/api/admin/winback/settings")
async def admin_winback_settings(request: Request):
    """Autorise / met en pause le win-back des boutiques suspendues (OFF par défaut)."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    if "enabled" in body:
        set_setting("winback_enabled", "true" if body.get("enabled") else "false")
    return {"ok": True}


@app.post("/api/admin/winback/run")
async def admin_winback_run(request: Request, bg: BackgroundTasks):
    """Déclenche manuellement une vague de win-back (test)."""
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    bg.add_task(run_winback)
    return {"ok": True, "message": "Win-back lancé — résumé sur Telegram si des relances partent."}


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


def run_winback() -> dict:
    """Win-back : relance les boutiques en pause (1 fois) pour les reconquérir.

    OFF par défaut (`winback_enabled`). Message templaté (zéro token), 1 seul par
    boutique (anti-spam via winback_at). Données toujours conservées.
    """
    from db.client import get_setting_bool, list_suspended_for_winback, mark_winback
    from notify import notify_winback
    stats = {"enabled": False, "sent": 0}
    if not get_setting_bool("winback_enabled", False):
        return stats
    stats["enabled"] = True
    for m in list_suspended_for_winback():
        try:
            notify_winback(m)
            mark_winback(m["id"])
            stats["sent"] += 1
        except Exception:  # noqa: BLE001
            log.warning("winback %s échoué", m.get("id"), exc_info=True)
    return stats


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
            # Win-back des boutiques en pause (OFF par défaut, 1 relance/boutique).
            await asyncio.to_thread(run_winback)
        except Exception:  # noqa: BLE001
            log.warning("winback loop", exc_info=True)
        try:
            # Rappels d'agenda de l'assistant perso → poussés au patron UNIQUEMENT
            # dans la fenêtre WhatsApp 24h (gratuit/conforme). Garde-fous internes.
            from core.assistant import run_assistant_reminders
            await asyncio.to_thread(run_assistant_reminders)
        except Exception:  # noqa: BLE001
            log.warning("assistant reminders loop", exc_info=True)
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


@app.post("/api/merchants/{merchant_id}/assistant")
async def merchant_assistant_endpoint(request: Request, merchant_id: str):
    """L'assistant personnel du commerçant (questions, rapports, copilote IA).

    Lecture seule, SANS quota (ce ne sont pas des ordres de gestion). La session
    back-office authentifie déjà la patronne (verrou n°1 satisfait).
    """
    from core import assistant
    from db.client import get_merchant
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    question = (body.get("message") or "").strip()
    if not question:
        return JSONResponse({"ok": False, "error": "Question vide."}, status_code=400)
    try:
        merchant = get_merchant(merchant_id)
        if not merchant:
            return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
        answer = assistant.converse(merchant, question, channel="backoffice")
    except Exception as e:  # noqa: BLE001
        log.exception("assistant commerçant échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    return {"ok": True, "reply": answer}


@app.post("/api/merchants/{merchant_id}/orders/{order_id}/validate")
async def merchant_validate_order_endpoint(request: Request, merchant_id: str, order_id: str):
    """Le commerçant CONFIRME (vert) ou REJETTE (rouge) un paiement client.

    Confirm → commande 'confirmed' + on prévient le client. Reject → retour 'pending'
    (le paiement n'est pas validé, la vente reste ouverte) + on invite le client à
    renvoyer sa référence. Le vendeur n'est jamais perdu.
    """
    from db.client import get_merchant, set_order_status
    from notify import notify_customer_payment_result
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    action = (body.get("action") or "").strip().lower()
    if action not in ("confirm", "reject"):
        return JSONResponse({"ok": False, "error": "Action invalide."}, status_code=400)
    confirmed = action == "confirm"
    try:
        merchant = get_merchant(merchant_id)
        if not merchant:
            return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
        order = set_order_status(order_id, merchant_id, "confirmed" if confirmed else "pending")
        if not order:
            return JSONResponse({"ok": False, "error": "Commande introuvable."}, status_code=404)
        try:
            notify_customer_payment_result(order.get("customer_whatsapp"),
                                           merchant.get("business_name") or "la boutique", confirmed)
        except Exception:  # noqa: BLE001
            log.warning("notif client paiement échouée", exc_info=True)
    except Exception as e:  # noqa: BLE001
        log.exception("validation commande échouée")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "status": order.get("status")}


@app.post("/api/merchants/{merchant_id}/notifications/{notif_id}/done")
async def merchant_notification_done(request: Request, merchant_id: str, notif_id: str):
    """Marque une notification (ex. lead chaud) comme traitée → elle disparaît du feed."""
    from db.client import set_notification_status
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    row = set_notification_status(notif_id, merchant_id, "done")
    if not row:
        return JSONResponse({"ok": False, "error": "Notification introuvable."}, status_code=404)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/support")
async def merchant_support_endpoint(request: Request, merchant_id: str):
    """Support in-app : le commerçant écrit, l'IA Vendora répond (ou ack si Mongazi gère)."""
    from core import support
    from db.client import (
        add_support_message,
        get_merchant,
        get_setting_bool,
        list_support_thread,
        recent_support_problems,
        set_setting,
    )
    from notify import notify_mongazi, notify_support_problem
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    message = (body.get("message") or "").strip()
    if not message:
        return JSONResponse({"ok": False, "error": "Message vide."}, status_code=400)
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)

    add_support_message(merchant_id, "merchant", message)

    # Mode « Mongazi gère » : pas de réponse IA, on l'alerte + accusé de réception.
    if get_setting_bool(f"support_human_{merchant_id}", False):
        set_setting(f"support_open_{merchant_id}", "1")
        try:
            notify_mongazi(f"💬 <b>Message support</b> (vous gérez) — "
                           f"{merchant.get('business_name','?')} :\n{message[:400]}")
        except Exception:  # noqa: BLE001
            log.warning("notif message support échouée", exc_info=True)
        return {"ok": True, "reply": "Votre message est bien reçu 🙏 L'équipe NEBULA vous "
                                     "répond au plus vite.", "by": "owner"}

    history = list_support_thread(merchant_id, limit=20)
    known = support.format_known_issues(recent_support_problems(limit=8))

    def on_problem(data: dict) -> None:
        cat = (data.get("categorie") or "autre").strip()
        resume = (data.get("resume") or message).strip()
        add_support_message(merchant_id, "ai", f"[{cat}] {resume}", kind="problem")
        set_setting(f"support_open_{merchant_id}", "1")
        try:
            notify_support_problem(merchant, cat, resume)
        except Exception:  # noqa: BLE001
            log.warning("alerte problème support échouée", exc_info=True)

    try:
        reply = support.support_reply(merchant, message, history=history[:-1],
                                      known_issues=known, on_problem=on_problem)
    except Exception as e:  # noqa: BLE001
        log.exception("support IA échoué")
        return JSONResponse({"ok": False, "error": str(e)[:300]}, status_code=500)
    add_support_message(merchant_id, "ai", reply)
    return {"ok": True, "reply": reply, "by": "ai"}


@app.post("/api/admin/support/{merchant_id}/reply")
async def admin_support_reply(request: Request, merchant_id: str):
    """Mongazi répond lui-même à un commerçant (apparaît dans son onglet Support)."""
    from db.client import add_support_message, set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    message = (body.get("message") or "").strip()
    if not message:
        return JSONResponse({"ok": False, "error": "Message vide."}, status_code=400)
    add_support_message(merchant_id, "owner", message)
    set_setting(f"support_open_{merchant_id}", "0")  # traité
    return {"ok": True}


@app.post("/api/admin/support/{merchant_id}/mode")
async def admin_support_mode(request: Request, merchant_id: str):
    """Bascule « je gère » (IA OFF) / « rendre à l'IA » pour un commerçant."""
    from db.client import set_setting
    if not _admin_ok(request.headers.get("x-admin-token")):
        return JSONResponse({"ok": False, "error": "Non autorisé."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    human = bool(body.get("human"))
    set_setting(f"support_human_{merchant_id}", "1" if human else "0")
    set_setting(f"support_open_{merchant_id}", "1" if human else "0")
    return {"ok": True, "human": human}


@app.get("/doc/{doc_id}", response_class=HTMLResponse)
async def public_document(request: Request, doc_id: str):
    """Page publique imprimable d'un document (facture / pro forma / devis)."""
    from datetime import datetime
    from db.client import get_document, get_merchant
    doc = get_document(doc_id)
    if not doc:
        return HTMLResponse("<body style='font-family:sans-serif;padding:40px'>"
                            "Document introuvable.</body>", status_code=404)
    merchant = get_merchant(doc.get("merchant_id")) or {}
    label = {"facture": "FACTURE", "proforma": "PRO FORMA",
             "devis": "DEVIS", "recu": "REÇU"}.get(doc.get("doc_type"), "DOCUMENT")
    try:
        date_fr = datetime.fromisoformat(
            str(doc.get("created_at")).replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except Exception:  # noqa: BLE001
        date_fr = ""
    return templates.TemplateResponse(request, "doc.html",
                                      {"doc": doc, "merchant": merchant,
                                       "label": label, "date_fr": date_fr})


@app.get("/catalogue/{code}", response_class=HTMLResponse)
async def public_catalogue(request: Request, code: str):
    """Catalogue public d'une boutique (liste de prix partageable + bouton commander)."""
    from db.client import get_merchant_by_code, list_products
    merchant = get_merchant_by_code((code or "").strip().lower())
    if not merchant:
        return HTMLResponse("<body style='font-family:sans-serif;padding:40px'>"
                            "Catalogue introuvable.</body>", status_code=404)
    products = [p for p in list_products(merchant["id"]) if p.get("available") is not False]
    return templates.TemplateResponse(request, "catalogue.html",
                                      {"merchant": merchant, "products": products,
                                       "wa_link": _wa_short_link(merchant.get("code"))})


@app.post("/api/merchants/{merchant_id}/cash")
async def merchant_cash_endpoint(request: Request, merchant_id: str):
    """Ajout rapide d'une recette/dépense en caisse depuis le back-office."""
    from db.client import add_cash_entry
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    try:
        montant = float(body.get("montant") or 0)
    except (TypeError, ValueError):
        montant = 0
    if montant <= 0:
        return JSONResponse({"ok": False, "error": "Montant invalide."}, status_code=400)
    add_cash_entry(merchant_id, body.get("sens") or "in", montant, body.get("libelle"))
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/debt")
async def merchant_debt_add(request: Request, merchant_id: str):
    """Ajout rapide d'une dette client (ardoise) depuis le back-office."""
    from db.client import add_debt
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    client = (body.get("client") or "").strip()
    try:
        montant = float(body.get("montant") or 0)
    except (TypeError, ValueError):
        montant = 0
    if not client or montant <= 0:
        return JSONResponse({"ok": False, "error": "Client et montant requis."}, status_code=400)
    add_debt(merchant_id, client, montant, body.get("motif"), body.get("contact"))
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/debt/{debt_id}/paid")
async def merchant_debt_paid(request: Request, merchant_id: str, debt_id: str):
    """Marque une dette comme payée (soldée)."""
    from db.client import set_debt_paid
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    row = set_debt_paid(debt_id, merchant_id)
    if not row:
        return JSONResponse({"ok": False, "error": "Dette introuvable."}, status_code=404)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/appointments")
async def merchant_appointment_create(request: Request, merchant_id: str):
    """Ajoute un RDV planifié manuellement depuis l'agenda."""
    from db.client import create_appointment
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    iso = _wat_iso(body.get("date"), body.get("time"))
    if not iso:
        return JSONResponse({"ok": False, "error": "Date et heure requises."}, status_code=400)
    create_appointment(
        merchant_id, None,
        service=(body.get("service") or "").strip() or None,
        customer_name=(body.get("customer_name") or "").strip() or None,
        note=(body.get("note") or "").strip() or None,
        scheduled_at=iso, status="confirmed",
    )
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/appointments/{appt_id}")
async def merchant_appointment_update(request: Request, merchant_id: str, appt_id: str):
    """Planifie (date+heure), confirme ou annule un RDV."""
    from db.client import update_appointment
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    action = (body.get("action") or "").strip()
    if action == "cancel":
        fields = {"status": "cancelled"}
    elif action == "confirm":
        fields = {"status": "confirmed"}
    elif action == "schedule":
        iso = _wat_iso(body.get("date"), body.get("time"))
        if not iso:
            return JSONResponse({"ok": False, "error": "Date et heure requises."}, status_code=400)
        fields = {"scheduled_at": iso, "status": "confirmed"}
    else:
        return JSONResponse({"ok": False, "error": "Action invalide."}, status_code=400)
    row = update_appointment(appt_id, merchant_id, fields)
    if not row:
        return JSONResponse({"ok": False, "error": "Rendez-vous introuvable."}, status_code=404)
    return {"ok": True}


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


@app.post("/api/merchants/{merchant_id}/payment-accounts")
async def merchant_payment_accounts(request: Request, merchant_id: str):
    """Comptes Mobile Money additionnels (réseau + numéro + nom). L'agent donne le bon selon le réseau du client."""
    from db.client import save_payment_accounts
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": "JSON invalide"}, status_code=400)
    accounts = save_payment_accounts(merchant_id, body.get("accounts") or [])
    return {"ok": True, "accounts": accounts}


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


@app.post("/api/merchants/{merchant_id}/social/generate")
async def merchant_social_generate(request: Request, merchant_id: str):
    """Vendora Social : génère un lot de posts réseaux sociaux (à la demande).

    Garde-fous : session valide + capacité « social » du forfait. Génération via
    le writer model, ancrée sur le catalogue. Les posts sont des BROUILLONS (le
    commerçant valide/copie ; pas de publication automatique en V1).
    """
    from core import social
    from core.capabilities import has_capability
    from db.client import get_merchant, list_products, save_social_posts
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    if not has_capability(merchant, "social"):
        return JSONResponse({"ok": False, "error": "Module « Réseaux sociaux » non inclus dans votre forfait."},
                            status_code=403)
    try:
        body = await request.json()
    except Exception:
        body = {}
    per_week = body.get("per_week", 3)
    weeks = body.get("weeks", 2)
    try:
        from db.client import get_active_lessons
        try:
            lessons = get_active_lessons(merchant_id)
        except Exception:  # noqa: BLE001
            lessons = ""
        products = list_products(merchant_id)
        posts = social.generate_calendar(merchant, products, per_week=per_week, weeks=weeks, lessons=lessons)
        if not posts:
            return JSONResponse({"ok": False, "error": "Génération impossible pour l'instant, réessayez."},
                                status_code=502)
        save_social_posts(merchant_id, posts)
    except Exception as e:  # noqa: BLE001
        log.exception("génération social échouée")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "posts": posts}


@app.post("/api/merchants/{merchant_id}/coach/generate")
async def merchant_coach_generate(request: Request, merchant_id: str):
    """Coach commercial : génère le conseil de la semaine à partir des chiffres réels.

    Session + capacité « coach » requises. À la demande (coût maîtrisé).
    """
    from core import coach
    from core.capabilities import has_capability
    from db.client import get_merchant, save_coaching
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    if not has_capability(merchant, "coach"):
        return JSONResponse({"ok": False, "error": "Module « Coach commercial » non inclus."}, status_code=403)
    try:
        from db.client import get_active_lessons
        try:
            lessons = get_active_lessons(merchant_id)
        except Exception:  # noqa: BLE001
            lessons = ""
        res = coach.generate_coaching(merchant, lessons=lessons)
        if not res.get("advice"):
            return JSONResponse({"ok": False, "error": "Conseil indisponible, réessayez."}, status_code=502)
        save_coaching(merchant_id, res["advice"], res.get("snapshot") or {})
    except Exception as e:  # noqa: BLE001
        log.exception("génération coaching échouée")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "advice": res["advice"], "snapshot": res.get("snapshot") or {}}


def _merchant_facebook_page(merchant: dict) -> str | None:
    """Retrouve l'ID de la Page Facebook liée à la boutique (mapping page_merchant_)."""
    code = (merchant.get("code") or "").strip().lower()
    if not code:
        return None
    try:
        from db.client import list_settings_prefix
        for s in list_settings_prefix("page_merchant_"):
            if (s.get("value") or "").strip().lower() == code:
                return (s.get("key") or "").replace("page_merchant_", "", 1) or None
    except Exception:  # noqa: BLE001
        log.warning("lookup page Facebook KO", exc_info=True)
    return None


@app.post("/api/merchants/{merchant_id}/social/publish")
async def merchant_social_publish(request: Request, merchant_id: str):
    """Publie un post planifié sur la Page Facebook liée (1 clic). Session + capacité.

    ⚠️ La publication 100% AUTOMATIQUE (sans clic, multi-clients) nécessite l'App
    Review Meta — ici c'est manuel + sur la page liée (marche dès qu'un token Page est posé).
    """
    from core import messenger_meta
    from core.capabilities import has_capability
    from db.client import get_latest_social_posts, get_merchant
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    if not has_capability(merchant, "social"):
        return JSONResponse({"ok": False, "error": "Module « Réseaux sociaux » non inclus."}, status_code=403)
    if not messenger_meta.configured():
        return JSONResponse({"ok": False, "error": "Publication Meta pas encore activée (jeton Page manquant)."}, status_code=503)
    page_id = _merchant_facebook_page(merchant)
    if not page_id:
        return JSONResponse({"ok": False, "error": "Aucune Page Facebook liée à votre boutique."}, status_code=400)
    try:
        body = await request.json()
    except Exception:
        body = {}
    posts = get_latest_social_posts(merchant_id)
    try:
        idx = int(body.get("index"))
        post = posts[idx]
    except Exception:
        return JSONResponse({"ok": False, "error": "Post introuvable."}, status_code=400)
    reseaux = post.get("reseaux") or []
    fb = next((r for r in reseaux if r.get("reseau") == "Facebook"), reseaux[0] if reseaux else {})
    text = (fb.get("legende") or "").strip()
    if fb.get("hashtags"):
        text += "\n\n" + fb["hashtags"]
    if not text:
        return JSONResponse({"ok": False, "error": "Post vide."}, status_code=400)
    if not messenger_meta.publish_facebook(page_id, text):
        return JSONResponse({"ok": False, "error": "Échec de la publication Facebook."}, status_code=502)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/social/image")
async def merchant_social_image(request: Request, merchant_id: str):
    """Vendora Social : génère une IMAGE de post brandée pour un produit (template, gratuit).

    body : {product_id, headline?}. Compose photo produit + accroche + prix + marque,
    upload sur le stockage, renvoie l'URL. Session + capacité « social » requises.
    """
    import httpx
    from core import social_image
    from core.capabilities import has_capability
    from db.client import get_merchant, list_products, upload_social_image
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    merchant = get_merchant(merchant_id)
    if not merchant:
        return JSONResponse({"ok": False, "error": "Boutique introuvable."}, status_code=404)
    if not has_capability(merchant, "social_images"):
        return JSONResponse({"ok": False, "error": "Images de marque : réservées au forfait Empire."}, status_code=403)
    try:
        body = await request.json()
    except Exception:
        body = {}
    pid = str(body.get("product_id") or "").strip()
    product = next((p for p in list_products(merchant_id) if str(p.get("id")) == pid), None)
    if not product:
        return JSONResponse({"ok": False, "error": "Choisissez un produit."}, status_code=400)
    headline = (body.get("headline") or product.get("name") or "").strip()
    price = product.get("price")
    price_text = (f"{int(float(price)):,} F".replace(",", " ")) if price not in (None, "") else None
    img_bytes = None
    if product.get("photo_url"):
        try:
            img_bytes = httpx.get(product["photo_url"], follow_redirects=True, timeout=20).content
        except Exception:  # noqa: BLE001
            img_bytes = None
    try:
        png = social_image.render_post_image(merchant, headline, price_text, img_bytes)
        url = upload_social_image(merchant_id, png)
    except Exception as e:  # noqa: BLE001
        log.exception("génération image social échouée")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "url": url}


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
        count = len(add_products(merchant_id, [body]))
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
    """Ajoute une image à la GALERIE d'un produit (plusieurs possibles ; la 1re = couverture)."""
    from db.client import add_product_image
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
        url = add_product_image(merchant_id, product_id, data, ctype, ext)
    except Exception as e:  # noqa: BLE001
        log.exception("upload image échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "url": url}


@app.post("/api/merchants/{merchant_id}/support/pdf")
async def upload_support_pdf(request: Request, merchant_id: str):
    """Importe un PDF dans la base de connaissances de l'agent support (texte extrait)."""
    from db.client import add_knowledge
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        form = await request.form()
    except Exception:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": "Formulaire invalide"}, status_code=400)
    file = form.get("pdf")
    if file is None or not hasattr(file, "read"):
        return JSONResponse({"ok": False, "error": "Aucun fichier."}, status_code=400)
    data = await file.read()
    if not data:
        return JSONResponse({"ok": False, "error": "Fichier vide."}, status_code=400)
    if len(data) > 12_000_000:
        return JSONResponse({"ok": False, "error": "PDF trop lourd (max 12 Mo)."}, status_code=400)
    name = (getattr(file, "filename", "") or "document.pdf")[:120]
    try:
        import io
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(data))
        text = "\n".join((pg.extract_text() or "") for pg in reader.pages).strip()
    except Exception:  # noqa: BLE001
        log.exception("extraction PDF échouée")
        return JSONResponse({"ok": False, "error": "Impossible de lire ce PDF."}, status_code=400)
    if not text:
        return JSONResponse({"ok": False, "error": "Aucun texte lisible (PDF scanné en image ?)."},
                            status_code=400)
    add_knowledge(merchant_id, content=text[:60000], title=name, kind="pdf")
    return {"ok": True, "title": name, "chars": len(text)}


@app.post("/api/merchants/{merchant_id}/support/knowledge/{knowledge_id}/delete")
async def delete_support_knowledge(request: Request, merchant_id: str, knowledge_id: str):
    """Supprime un document de la base de connaissances."""
    from db.client import delete_knowledge
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    return {"ok": delete_knowledge(knowledge_id, merchant_id)}


@app.post("/api/merchants/{merchant_id}/support/report")
async def support_report_endpoint(request: Request, merchant_id: str):
    """Génère le rapport support (volume, récurrents, corrections suggérées)."""
    from core import support_report
    from db.client import get_merchant
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    m = get_merchant(merchant_id)
    if not m:
        return JSONResponse({"ok": False, "error": "Boutique introuvable"}, status_code=404)
    return {"ok": True, "report": support_report.generate_report(m)}


@app.post("/api/merchants/{merchant_id}/products/{product_id}/images/{image_id}/delete")
async def delete_product_image_endpoint(request: Request, merchant_id: str,
                                        product_id: str, image_id: str):
    """Supprime une image de la galerie d'un produit."""
    from db.client import delete_product_image
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    ok = delete_product_image(image_id, merchant_id)
    if not ok:
        return JSONResponse({"ok": False, "error": "Image introuvable."}, status_code=404)
    return {"ok": True}


@app.post("/api/merchants/{merchant_id}/products/import")
async def import_products_endpoint(request: Request, merchant_id: str):
    """Import express : colle une liste en texte libre → l'IA structure + ajoute les produits."""
    from core import catalog_import
    from db.client import add_products
    auth = _need_session(request, merchant_id)
    if auth:
        return auth
    try:
        body = await request.json()
    except Exception:
        body = {}
    text = (body.get("text") or "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "Collez votre liste de produits."}, status_code=400)
    try:
        parsed = catalog_import.parse_products(text)
        if not parsed:
            return JSONResponse({"ok": False, "error": "Aucun produit reconnu. Réessayez en listant un produit par ligne."},
                                status_code=502)
        count = len(add_products(merchant_id, parsed))
    except Exception as e:  # noqa: BLE001
        log.exception("import produits échoué")
        return JSONResponse({"ok": False, "error": str(e)[:200]}, status_code=500)
    return {"ok": True, "count": count}


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
                  transcribe_fn=None, image_fn=None) -> dict:
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
        # Filet de sécurité : ni code vendora: ni session (le client a écrit au
        # numéro brut sans passer par le lien). On tente de reconnaître la boutique
        # à son NOM ; sinon on demande gentiment lequel (aucune écriture en base
        # tant qu'on n'a pas identifié la boutique).
        try:
            from db.client import find_merchant_by_name
            cand = find_merchant_by_name(body)
        except Exception:
            cand = []
            log.warning("recherche boutique par nom échouée", exc_info=True)
        if len(cand) == 1:
            merchant = get_merchant(cand[0]["id"])
            if merchant and customer:
                try:
                    upsert_wa_session(customer, merchant["id"])
                except Exception:
                    log.warning("wa session upsert (nom) échoué", exc_info=True)
        elif len(cand) > 1:
            noms = ", ".join(c["business_name"] for c in cand if c.get("business_name"))
            return {"status": "disambiguate", "media": [], "text":
                    "Il y a plusieurs boutiques 🙏 Vous cherchez laquelle : "
                    f"{noms} ? Écrivez son nom exact (ou ouvrez son lien)."}
        if not merchant:
            return {"status": "greeting", "media": [], "text":
                    "Bonjour 🌟 Vous cherchez quelle boutique ? Écrivez-moi son nom "
                    "et je vous mets en relation. (Le plus simple : ouvrir son lien WhatsApp.)"}

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

    # ── Verrou n°1 : la PATRONNE écrit (numéro en liste blanche) → mode ASSISTANT.
    # Son copilote IA (rapports + intelligence générale), JAMAIS le vendeur. On ne
    # persiste pas ces messages dans les conversations clients (pas de pollution
    # des analytics ni de l'apprentissage). Une cliente ne passe jamais ici.
    try:
        from core import assistant
        if assistant.is_owner(merchant, customer):
            imgs = None
            if image_fn:
                try:
                    got = image_fn()  # (octets, content_type) ou None
                    if got and got[0]:
                        import base64 as _b64
                        imgs = [{"media_type": got[1] or "image/jpeg",
                                 "data": _b64.b64encode(got[0]).decode()}]
                except Exception:  # noqa: BLE001
                    imgs = None
            ans = assistant.converse(merchant, clean, channel="whatsapp", images=imgs)
            return {"status": "assistant", "media": [], "text": ans}
    except Exception:  # noqa: BLE001
        log.exception("assistant propriétaire échoué — repli vendeur")

    # ── Agent SUPPORT (2e pilier) : si la boutique est en mode support, l'agent
    # répond aux UTILISATEURS depuis SA base de connaissances (pas le vendeur).
    if (merchant.get("agent_role") or "vendeur") == "support":
        from core import support_agent
        from db.client import create_support_ticket, knowledge_text_for
        save_message(merchant["id"], customer, "customer", clean)
        s_hist = load_history(merchant["id"], customer, limit=12)
        try:
            kb_docs = knowledge_text_for(merchant["id"])
        except Exception:  # noqa: BLE001
            kb_docs = ""

        def _on_escalate(d: dict) -> None:
            try:
                create_support_ticket(merchant["id"], user_contact=customer,
                                      channel="whatsapp", summary=d.get("probleme"),
                                      severity=d.get("gravite"))
            except Exception:  # noqa: BLE001
                log.warning("ticket support non créé", exc_info=True)
            try:
                _escalation_notifier(merchant, customer)(
                    {"raison": "Support — escalade", "resume": d.get("probleme") or "",
                     "nom_client": ""})
            except Exception:  # noqa: BLE001
                log.warning("notif support échouée", exc_info=True)

        s_ans = support_agent.reply(
            merchant, clean, history=s_hist,
            kb_text=merchant.get("kb_text") or "",
            kb_instructions=merchant.get("kb_instructions") or "",
            kb_docs=kb_docs, on_escalate=_on_escalate)
        save_message(merchant["id"], customer, "assistant", s_ans)
        return {"status": "support", "media": [], "text": s_ans}

    save_message(merchant["id"], customer, "customer", clean)
    history = load_history(merchant["id"], customer, limit=brain.HISTORY_LIMIT)
    products = list_products(merchant["id"])
    try:
        from db.client import product_images_map
        _gallery = product_images_map(merchant["id"])
    except Exception:  # noqa: BLE001
        _gallery = {}

    media_urls: list[str] = []

    def _on_show(data: dict) -> str:
        names = data.get("produits") or []
        n_before = len(media_urls)
        for raw in names:
            nl = (raw or "").strip().lower()
            if not nl:
                continue
            for p in products:
                if nl not in (p.get("name") or "").lower():
                    continue
                # Toute la galerie du produit (ou la couverture), max 4 par produit.
                urls = [x["url"] for x in _gallery.get(p.get("id"), [])] or (
                    [p["photo_url"]] if p.get("photo_url") else [])
                for u in urls[:4]:
                    if u and u not in media_urls:
                        media_urls.append(u)
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
        on_payment=_payment_recorder(merchant, customer),
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

    image_fn = None
    if num_media > 0 and ctype0.startswith("image") and media_url0:
        def image_fn():  # noqa: E306
            try:
                auth = ((settings.twilio_account_sid, settings.twilio_auth_token)
                        if settings.twilio_account_sid else None)
                r = httpx.get(media_url0, auth=auth, follow_redirects=True, timeout=20)
                return (r.content, ctype0) if r.status_code == 200 else None
            except Exception:  # noqa: BLE001
                return None

    try:
        res = _agent_handle(from_, body, has_audio=has_audio, transcribe_fn=transcribe_fn,
                            image_fn=image_fn)
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

    image_fn = None
    if msg.get("type") == "image" and msg.get("image_id"):
        iid, ict = msg.get("image_id"), msg.get("image_ctype")

        def image_fn():  # noqa: E306
            got = whatsapp_meta.fetch_media(iid)
            return (got[0], ict or got[1]) if got else None

    try:
        res = _agent_handle(customer, msg.get("text") or "", has_audio=has_audio,
                            transcribe_fn=transcribe_fn, image_fn=image_fn)
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
    wa_link = _wa_short_link(merchant.get("code")) if merchant else ""
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


@app.post("/api/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    """Transcrit une note vocale (simulateur web) en texte via Groq Whisper.

    GRATUIT (Groq). Le front renvoie ensuite ce texte à /api/chat → donc le vocal
    COMPTE dans la limite d'essai (pas d'abus). Garde-fous tokens/coût : taille
    max + transcription tronquée (un vocal qui s'éternise ne fait pas exploser
    les tokens de la réponse)."""
    if not settings.groq_api_key:
        return JSONResponse({"ok": False, "error": "Vocal indisponible pour le moment."},
                            status_code=503)
    try:
        audio = await file.read()
    except Exception:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": "Audio illisible."}, status_code=400)
    if not audio:
        return JSONResponse({"ok": False, "error": "Audio vide."}, status_code=400)
    if len(audio) > 6_000_000:  # ~6 Mo : un vocal de 30-60 s pèse bien moins
        return JSONResponse({"ok": False, "error": "Vocal trop long."}, status_code=413)
    from core import transcribe as _t
    text = _t.transcribe_bytes(audio, file.content_type)
    if not text:
        return JSONResponse({"ok": False, "error": "Je n'ai pas réussi à écouter le vocal."},
                            status_code=502)
    return {"ok": True, "text": text.strip()[:500]}  # garde-fou tokens
