"""WhatsApp PRODUCTION — Meta Cloud API (Pilier 2).

Permet à Vendora de recevoir et envoyer des messages WhatsApp via l'API officielle
de Meta (gratuit jusqu'à 1000 conversations de service/mois, sans Twilio ni CB).

Dormant tant que `whatsapp_token` + `whatsapp_phone_number_id` ne sont pas configurés
→ le webhook Meta répond mais n'agit pas, et le sandbox Twilio reste l'I/O par défaut.

Couvre : vérification du webhook (GET), parsing des messages entrants (texte + vocal),
envoi texte, envoi image (photo produit), et récupération d'un média vocal (2 appels
Graph : id → url → octets) pour la transcription.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings

log = logging.getLogger("boutique-ia.whatsapp_meta")


def configured() -> bool:
    return bool(settings.whatsapp_token and settings.whatsapp_phone_number_id)


def _graph(path: str) -> str:
    return f"https://graph.facebook.com/{settings.whatsapp_graph_version}/{path}"


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.whatsapp_token}",
            "Content-Type": "application/json"}


def verify_webhook(mode: str | None, token: str | None, challenge: str | None) -> str | None:
    """Vérification d'abonnement du webhook Meta (GET). Retourne le challenge si OK."""
    if mode == "subscribe" and token and token == settings.whatsapp_verify_token:
        return challenge
    return None


def _to_digits(to: str) -> str:
    import re
    return re.sub(r"\D", "", to or "")


def send_text(to: str, text: str) -> bool:
    """Envoie un message texte au client (wa_id = chiffres, sans + ni 'whatsapp:')."""
    if not (configured() and to and text):
        return False
    payload = {"messaging_product": "whatsapp", "recipient_type": "individual",
               "to": _to_digits(to), "type": "text",
               "text": {"preview_url": False, "body": text[:4096]}}
    try:
        r = httpx.post(_graph(f"{settings.whatsapp_phone_number_id}/messages"),
                       headers=_headers(), json=payload, timeout=15.0)
        if r.status_code not in (200, 201):
            log.warning("Meta send_text %s: %s", r.status_code, r.text[:200])
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("Meta send_text KO: %s", e)
        return False


def send_image(to: str, link: str, caption: str | None = None) -> bool:
    """Envoie une image (photo produit) via une URL publique."""
    if not (configured() and to and link):
        return False
    img: dict[str, Any] = {"link": link}
    if caption:
        img["caption"] = caption[:1024]
    payload = {"messaging_product": "whatsapp", "to": _to_digits(to),
               "type": "image", "image": img}
    try:
        r = httpx.post(_graph(f"{settings.whatsapp_phone_number_id}/messages"),
                       headers=_headers(), json=payload, timeout=15.0)
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("Meta send_image KO: %s", e)
        return False


def fetch_media(media_id: str) -> tuple[bytes, str] | None:
    """Récupère un média (vocal) : id → url → octets. Retourne (octets, content_type)."""
    if not (configured() and media_id):
        return None
    try:
        meta = httpx.get(_graph(media_id), headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
                         timeout=15.0)
        meta.raise_for_status()
        url = meta.json().get("url")
        if not url:
            return None
        # Le téléchargement du binaire exige aussi le Bearer.
        dl = httpx.get(url, headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
                       follow_redirects=True, timeout=30.0)
        dl.raise_for_status()
        ctype = dl.headers.get("content-type", "audio/ogg")
        return dl.content, ctype
    except Exception as e:  # noqa: BLE001
        log.warning("Meta fetch_media KO: %s", e)
        return None


def parse_incoming(payload: dict) -> list[dict[str, Any]]:
    """Extrait les messages clients d'un webhook Meta. Ignore les statuts de livraison."""
    out: list[dict[str, Any]] = []
    try:
        for entry in payload.get("entry", []) or []:
            for change in entry.get("changes", []) or []:
                value = change.get("value", {}) or {}
                for msg in value.get("messages", []) or []:
                    mtype = msg.get("type")
                    item: dict[str, Any] = {"from": msg.get("from"), "type": mtype,
                                            "text": "", "audio_id": None, "audio_ctype": None,
                                            "image_id": None, "image_ctype": None}
                    if mtype == "text":
                        item["text"] = (msg.get("text") or {}).get("body", "")
                    elif mtype == "audio":
                        au = msg.get("audio") or {}
                        item["audio_id"] = au.get("id")
                        item["audio_ctype"] = au.get("mime_type") or "audio/ogg"
                    elif mtype == "image":
                        im = msg.get("image") or {}
                        item["image_id"] = im.get("id")
                        item["image_ctype"] = im.get("mime_type") or "image/jpeg"
                        item["text"] = im.get("caption") or ""
                    elif mtype in ("button", "interactive"):
                        # Réponses à des boutons/templates → on prend le texte si présent
                        item["text"] = ((msg.get("button") or {}).get("text")
                                        or (((msg.get("interactive") or {}).get("button_reply") or {}).get("title"))
                                        or "")
                    out.append(item)
    except Exception:  # noqa: BLE001
        log.warning("parse webhook Meta KO", exc_info=True)
    return out
