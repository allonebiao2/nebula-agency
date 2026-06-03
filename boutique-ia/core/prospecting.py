"""Moteur de PROSPECTION autonome (étage 5) — partagé.

Réutilise l'approche NOVA :
  - sourcing gratuit via OpenStreetMap (Overpass) : entreprises locales par
    catégorie + ville (on ne garde que celles qui ont un EMAIL public) ;
  - rédaction de l'email par Claude (Opus, qualité max) ;
  - envoi via Gmail SMTP (compte NOVA réutilisé), avec garde-fous.

Deux modes :
  - 'client'      : une boutique prospecte des clients/partenaires pros.
  - 'recrutement' : Vendora (admin) recrute de nouvelles boutiques.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import anthropic
import httpx

from config import settings

log = logging.getLogger("boutique-ia.prospecting")


# --- Désinscription (lien signé par email) -----------------------------------
def _unsub_secret() -> str:
    return settings.session_secret or settings.admin_token or "vendora-unsub"


def unsub_token(email: str) -> str:
    payload = base64.urlsafe_b64encode((email or "").strip().lower().encode()).decode().rstrip("=")
    sig = hmac.new(_unsub_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}.{sig}"


def verify_unsub_token(token: str) -> str | None:
    """Retourne l'email si le token est valide, sinon None."""
    try:
        payload, sig = token.rsplit(".", 1)
    except ValueError:
        return None
    good = hmac.new(_unsub_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(good, sig):
        return None
    pad = "=" * (-len(payload) % 4)
    try:
        return base64.urlsafe_b64decode(payload + pad).decode().lower()
    except Exception:  # noqa: BLE001
        return None


def _unsub_footer(email: str) -> str:
    url = settings.public_base_url.rstrip("/") + "/unsub/" + unsub_token(email)
    return f"Pour ne plus recevoir nos emails, cliquez ici : {url}"

# --- Sourcing OSM (repris de NOVA, découplé) ---------------------------------
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
USER_AGENT = "Vendora-Prospector/1.0 (+https://vendora-agent.up.railway.app)"

CATEGORIES = {
    "beauty":     {"label": "Beauté · cosmétique · coiffure", "filter": '[shop~"^(beauty|hairdresser|cosmetics|perfumery)$"]'},
    "fashion":    {"label": "Mode · vêtements · chaussures · bijoux", "filter": '[shop~"^(clothes|shoes|jewelry|watches|bag|fashion_accessories)$"]'},
    "restaurant": {"label": "Restauration · bars · cafés", "filter": '[amenity~"^(restaurant|cafe|bar|fast_food)$"]'},
    "health":     {"label": "Santé · pharmacies · cliniques", "filter": '[amenity~"^(pharmacy|clinic|doctors|dentist)$"]'},
    "hospitality":{"label": "Hôtels · maisons d'hôtes", "filter": '[tourism~"^(hotel|guest_house|hostel)$"]'},
    "office":     {"label": "Bureaux professionnels", "filter": '[office]'},
    "retail":     {"label": "Boutiques générales", "filter": '[shop~"^(supermarket|electronics|optician|gift|florist|furniture)$"]'},
    "events":     {"label": "Événementiel · photographie", "filter": '[craft~"^(photographer|event)$"]'},
}
CITY_TO_COUNTRY = {
    "cotonou": "BJ", "porto-novo": "BJ", "parakou": "BJ", "abomey-calavi": "BJ", "calavi": "BJ",
    "lomé": "TG", "lome": "TG", "abidjan": "CI", "dakar": "SN", "ouagadougou": "BF",
}


def _overpass(query: str) -> dict[str, Any]:
    last = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            r = httpx.post(endpoint, data={"data": query},
                           headers={"User-Agent": USER_AGENT}, timeout=120.0)
            if r.status_code == 429:
                time.sleep(4); continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            log.warning("Overpass endpoint KO (%s): %s", endpoint, e)
    if last:
        raise last
    raise RuntimeError("Overpass indisponible")


def source_osm(city: str, category: str, *, with_email_only: bool = True,
               limit: int = 60) -> list[dict[str, Any]]:
    """Cherche des entreprises (catégorie + ville). Garde celles avec email."""
    cat = CATEGORIES.get(category)
    if not cat:
        raise ValueError(f"Catégorie inconnue : {category}")
    country = CITY_TO_COUNTRY.get(city.strip().lower())
    query = (f'[out:json][timeout:90];area["name"~"^{city}$",i]->.a;'
             f'(nwr{cat["filter"]}(area.a););out center tags;')
    elements = _overpass(query).get("elements", [])
    out = []
    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("name:fr")
        email = tags.get("email") or tags.get("contact:email")
        if not name:
            continue
        if with_email_only and not email:
            continue
        out.append({
            "name": name[:200],
            "email": email,
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "city": city,
            "country": country,
            "sector": category,
            "source_external_id": f"{el.get('type')}/{el.get('id')}",
        })
        if len(out) >= limit:
            break
    return out


# --- Rédaction de l'email (Claude Opus) --------------------------------------
_OPT_OUT = "Pour ne plus recevoir de message, répondez STOP."


def generate_outreach(mode: str, ctx: dict[str, Any]) -> dict[str, str]:
    """Rédige un modèle d'email (subject + body avec le marqueur [NOM]).

    mode 'client'      : ctx = fiche boutique (vend ses produits à un pro).
    mode 'recrutement' : ctx = pitch Vendora (vend l'abonnement à une boutique).
    """
    if mode == "recrutement":
        guide = (
            "Tu écris au nom de NEBULA Agency (Cotonou). Tu proposes VENDORA : un agent "
            "vendeur doté d'intelligence artificielle qui répond et vend aux clients sur "
            "WhatsApp 24h/24, à la place du commerçant. Inscription simple en ligne, "
            "paiement Mobile Money. Invite à découvrir via "
            "https://vendora-agent.up.railway.app . Signe « — Mongazi · NEBULA Agency »."
        )
        about = "NEBULA Agency — Vendora, l'agent vendeur WhatsApp."
    else:
        name = ctx.get("business_name") or "notre boutique"
        sector = ctx.get("sector") or ""
        desc = ctx.get("description") or ""
        city = ctx.get("city") or ""
        guide = (
            f"Tu écris au nom de la boutique « {name} »{f' ({sector})' if sector else ''}"
            f"{f', à {city}' if city else ''}. Tu proposes ses produits/services à un "
            f"professionnel (revente, cadeaux d'entreprise, partenariat). Reste concret et "
            f"local. Termine par une question simple pour ouvrir la discussion."
        )
        about = f"{name} — {desc}"

    system = (
        "Tu rédiges un cold email B2B en français pour l'Afrique de l'Ouest. Style direct, "
        "chaleureux, court (5 phrases max), tutoiement, AUCUN jargon, 1 emoji maximum, "
        "jamais de formule qui sonne IA. Le destinataire doit pouvoir répondre en 1 phrase.\n"
        + guide +
        "\nUtilise le marqueur [NOM] là où le nom de l'entreprise destinataire doit apparaître.\n"
        'Réponds en JSON STRICT, rien d\'autre : {"subject":"...","body":"..."} '
        "(objet < 55 caractères ; body avec sauts de ligne \\n, signé)."
    )
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=settings.writer_model, max_tokens=700,
        system=system,
        messages=[{"role": "user", "content": f"Contexte : {about}. Rédige l'email."}],
    )
    raw = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[4:].strip() if raw.lower().startswith("json") else raw
    import json
    try:
        data = json.loads(raw)
        subject = (data.get("subject") or "").strip()[:120]
        body = (data.get("body") or "").strip()
    except Exception:  # noqa: BLE001
        subject, body = "", ""
    if not subject or not body:
        # Repli minimal si le modèle dévie
        subject = subject or "Une proposition pour [NOM]"
        body = body or f"Bonjour [NOM],\n\n{about}\n\nÇa vous intéresse ?\n\n— Mongazi · NEBULA Agency"
    # NB : le lien de désinscription (unique par destinataire) est ajouté à l'envoi.
    return {"subject": subject, "body": body}


def personalize(template: str, prospect: dict[str, Any]) -> str:
    name = prospect.get("name") or "votre équipe"
    return template.replace("[NOM]", name).replace("{nom}", name)


# --- Envoi email ------------------------------------------------------------
# Resend (API HTTP, port 443) = backend par défaut, fonctionne sur Railway.
# Gmail SMTP (port 465) gardé en repli LOCAL uniquement (bloqué par Railway).
def _send_resend(to: str, subject: str, body: str, reply_to: str | None,
                 from_name: str) -> dict[str, Any]:
    if not settings.resend_api_key:
        return {"ok": False, "error": "RESEND_API_KEY manquante"}
    payload = {
        "from": f"{from_name or settings.email_from_name} <{settings.email_from_address}>",
        "to": [to],
        "subject": subject,
        "text": body,
    }
    rt = reply_to or settings.email_reply_to
    if rt:
        payload["reply_to"] = rt
    try:
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}",
                     "Content-Type": "application/json"},
            json=payload, timeout=20.0,
        )
        if r.status_code in (200, 201):
            return {"ok": True, "error": None}
        return {"ok": False, "error": f"resend {r.status_code}: {r.text[:160]}"}
    except Exception as e:  # noqa: BLE001
        log.warning("Resend send KO: %s", e)
        return {"ok": False, "error": str(e)[:200]}


def _send_gmail_smtp(to: str, subject: str, body: str, reply_to: str | None,
                     from_name: str) -> dict[str, Any]:
    if not (settings.gmail_user and settings.gmail_app_password):
        return {"ok": False, "error": "Gmail non configuré"}
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{settings.gmail_user}>"
    msg["To"] = to
    msg["Subject"] = subject
    rt = reply_to or settings.email_reply_to
    if rt:
        msg["Reply-To"] = rt
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as srv:
            srv.login(settings.gmail_user, settings.gmail_app_password)
            srv.send_message(msg)
        return {"ok": True, "error": None}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:200]}


def send_email(to: str, subject: str, body: str, *, reply_to: str | None = None,
               from_name: str = "Mongazi · NEBULA Agency") -> dict[str, Any]:
    """Envoie via Resend (défaut). Repli Gmail SMTP si pas de clé Resend (local)."""
    if settings.resend_api_key:
        return _send_resend(to, subject, body, reply_to, from_name)
    return _send_gmail_smtp(to, subject, body, reply_to, from_name)


# --- Orchestration : envoi d'une campagne (tâche de fond, avec garde-fous) ----
SEND_DELAY_S = 6  # délai court entre 2 envois (anti-spam)


def execute_campaign(campaign_id: str, plan_daily: int, *,
                     reply_to: str | None = None, from_name: str = "Mongazi · NEBULA Agency") -> None:
    """Envoie les emails d'une campagne en respectant les quotas (plan + Gmail global)."""
    from datetime import datetime, timezone

    from db.client import (
        count_prospection_sent_today,
        count_prospection_sent_today_global,
        email_already_contacted,
        get_campaign,
        is_opted_out,
        list_prospects,
        mark_prospect,
        update_campaign,
    )

    camp = get_campaign(campaign_id)
    if not camp:
        return
    owner_type = camp.get("owner_type") or "merchant"
    merchant_id = camp.get("merchant_id")
    subject_tpl = camp.get("subject") or ""
    body_tpl = camp.get("body") or ""
    update_campaign(campaign_id, {"status": "sending"})

    sent = failed = 0
    try:
        for p in list_prospects(campaign_id):
            if p.get("status") != "new":
                continue
            # Quotas (revérifiés à chaque tour : sûr même en parallèle)
            used_plan = count_prospection_sent_today(owner_type, merchant_id)
            if plan_daily >= 0 and used_plan >= plan_daily:
                break
            if count_prospection_sent_today_global() >= settings.gmail_daily_cap:
                break
            email = (p.get("email") or "").strip()
            if not email:
                mark_prospect(p["id"], "skipped", "pas d'email"); continue
            if is_opted_out(email):
                mark_prospect(p["id"], "skipped", "désinscrit"); continue
            if email_already_contacted(owner_type, merchant_id, email):
                mark_prospect(p["id"], "skipped", "déjà contacté"); continue

            body = personalize(body_tpl, p) + "\n\n" + _unsub_footer(email)
            res = send_email(
                email, personalize(subject_tpl, p), body,
                reply_to=reply_to, from_name=from_name,
            )
            if res.get("ok"):
                mark_prospect(p["id"], "sent",
                              sent_at=datetime.now(timezone.utc).isoformat())
                sent += 1
            else:
                mark_prospect(p["id"], "failed", res.get("error"))
                failed += 1
            time.sleep(SEND_DELAY_S)

        remaining_new = sum(1 for p in list_prospects(campaign_id) if p.get("status") == "new")
        status = "ready" if remaining_new else "done"  # 'ready' = reste à envoyer demain
        update_campaign(campaign_id, {"status": status, "sent": sent, "failed": failed})
    except Exception as e:  # noqa: BLE001
        log.exception("execute_campaign KO")
        update_campaign(campaign_id, {"status": "failed", "sent": sent, "failed": failed})


def run_full_campaign(campaign_id: str, mode: str, category: str, city: str,
                      plan_daily: int, owner_type: str, merchant_id: str | None) -> None:
    """Tâche de fond complète : sourcing OSM → rédaction (Opus) → envoi (garde-fous)."""
    from db.client import add_prospects, get_merchant, update_campaign

    reply_to = None
    from_name = "Mongazi · NEBULA Agency"
    try:
        # 1. Contexte email
        if mode == "client" and merchant_id:
            m = get_merchant(merchant_id) or {}
            ctx = m
            reply_to = m.get("owner_email") or settings.email_reply_to or None
            from_name = m.get("business_name") or from_name
        else:
            ctx = {}
            reply_to = settings.email_reply_to or None

        # 2. Sourcing
        prospects = source_osm(city, category)
        n = add_prospects(campaign_id, merchant_id, owner_type, prospects)
        # 3. Rédaction du modèle d'email
        tpl = generate_outreach(mode, ctx)
        update_campaign(campaign_id, {
            "found": len(prospects), "emailable": n,
            "subject": tpl["subject"], "body": tpl["body"], "status": "ready",
        })
        # 4. Envoi
        execute_campaign(campaign_id, plan_daily, reply_to=reply_to, from_name=from_name)
    except Exception as e:  # noqa: BLE001
        log.exception("run_full_campaign KO")
        update_campaign(campaign_id, {"status": "failed"})
