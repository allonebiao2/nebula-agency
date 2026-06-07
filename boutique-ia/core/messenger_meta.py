"""Inbound Messenger + Instagram Direct — Meta Messenger Platform.

Permet à Vendora de RECEVOIR et RÉPONDRE sur Facebook Messenger et Instagram
Direct, en réutilisant la même logique d'agent que WhatsApp (canal-agnostique :
voir `web/server._agent_handle`).

Dormant tant que `messenger_page_token` n'est pas configuré → le webhook répond
mais n'agit pas. Un seul PAGE token couvre Messenger ET Instagram (l'IG pro est
rattaché à la Page Facebook).

⚠️ Diffère de l'API WhatsApp Cloud (`whatsapp_meta.py`) :
- événements sous `entry[].messaging[]` (pas `entry[].changes[].value.messages[]`) ;
- l'expéditeur est un PSID (Messenger) ou IGSID (Instagram), pas un numéro ;
- envoi via `POST /me/messages?access_token=PAGE_TOKEN`, format `{recipient, message}` ;
- les pièces jointes (vocal) ont une URL CDN directe (pas de 2e appel Graph) ;
- les ÉCHOS (`message.is_echo`) de nos propres envois reviennent → on les ignore.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings

log = logging.getLogger("boutique-ia.messenger_meta")


def configured() -> bool:
    return bool(settings.messenger_page_token)


def _graph(path: str) -> str:
    return f"https://graph.facebook.com/{settings.whatsapp_graph_version}/{path}"


def verify_webhook(mode: str | None, token: str | None, challenge: str | None) -> str | None:
    """Vérification d'abonnement du webhook (GET). Retourne le challenge si OK.

    Le jeton de vérif Messenger retombe sur celui de WhatsApp si non défini, pour
    pouvoir réutiliser le même secret côté dashboard Meta.
    """
    expected = settings.messenger_verify_token or settings.whatsapp_verify_token
    if mode == "subscribe" and token and expected and token == expected:
        return challenge
    return None


def _send(recipient_id: str, message: dict) -> bool:
    if not (configured() and recipient_id and message):
        return False
    payload = {"recipient": {"id": str(recipient_id)},
               "messaging_type": "RESPONSE", "message": message}
    try:
        r = httpx.post(_graph("me/messages"),
                       params={"access_token": settings.messenger_page_token},
                       json=payload, timeout=15.0)
        if r.status_code not in (200, 201):
            log.warning("Messenger send %s: %s", r.status_code, r.text[:200])
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("Messenger send KO: %s", e)
        return False


def send_text(recipient_id: str, text: str) -> bool:
    """Envoie un message texte (limite Messenger : 2000 caractères)."""
    if not text:
        return False
    return _send(recipient_id, {"text": text[:1900]})


def send_image(recipient_id: str, link: str, caption: str | None = None) -> bool:
    """Envoie une image (photo produit) via une URL publique.

    Messenger ne met pas de légende sur l'image → on envoie d'abord la légende en
    texte si fournie, puis l'image.
    """
    if not link:
        return False
    if caption:
        send_text(recipient_id, caption)
    return _send(recipient_id, {"attachment": {"type": "image",
                "payload": {"url": link, "is_reusable": False}}})


def fetch_media(url: str) -> tuple[bytes, str] | None:
    """Télécharge une pièce jointe (vocal). URL CDN directe → un seul GET, sans token."""
    if not (configured() and url):
        return None
    try:
        dl = httpx.get(url, follow_redirects=True, timeout=30.0)
        dl.raise_for_status()
        return dl.content, dl.headers.get("content-type", "audio/mp4")
    except Exception as e:  # noqa: BLE001
        log.warning("Messenger fetch_media KO: %s", e)
        return None


def parse_incoming(payload: dict) -> list[dict[str, Any]]:
    """Extrait les messages clients d'un webhook Messenger/Instagram.

    Ignore les échos de nos envois (`is_echo`), les accusés de lecture/livraison
    et les réactions. Gère : texte, pièce jointe audio (vocal), et clic de bouton
    (postback). Renvoie une liste d'items {from, platform, type, text, audio_url,
    audio_ctype} — même forme que `whatsapp_meta.parse_incoming`.
    """
    platform = "instagram" if payload.get("object") == "instagram" else "messenger"
    out: list[dict[str, Any]] = []
    try:
        for entry in payload.get("entry", []) or []:
            # `entry.id` = ID de la Page (Messenger) ou du compte IG → mappé à une boutique
            page_id = entry.get("id")
            for ev in entry.get("messaging", []) or []:
                sender = (ev.get("sender") or {}).get("id")
                if not sender:
                    continue
                item: dict[str, Any] = {"from": sender, "platform": platform,
                                        "page_id": page_id, "type": "text", "text": "",
                                        "audio_url": None, "audio_ctype": None}
                msg = ev.get("message")
                if msg:
                    if msg.get("is_echo"):
                        continue
                    audio_url = None
                    for att in (msg.get("attachments") or []):
                        if att.get("type") == "audio":
                            audio_url = (att.get("payload") or {}).get("url")
                            if audio_url:
                                break
                    if audio_url:
                        item["type"] = "audio"
                        item["audio_url"] = audio_url
                        item["audio_ctype"] = "audio/mp4"
                    else:
                        item["text"] = msg.get("text") or ""
                        if not item["text"]:
                            continue  # image/sticker sans texte → ignoré
                elif ev.get("postback"):
                    pb = ev.get("postback") or {}
                    item["text"] = pb.get("title") or pb.get("payload") or ""
                    if not item["text"]:
                        continue
                else:
                    continue  # delivery / read / reaction → ignoré
                out.append(item)
    except Exception:  # noqa: BLE001
        log.warning("parse webhook Messenger KO", exc_info=True)
    return out


# ---------------------------------------------------------------------------
# COMMENT-TO-DM — acquisition sociale CONFORME (Meta « Private Replies »)
#
# Quand quelqu'un COMMENTE une publication de la Page/du compte IG d'une boutique,
# on a le droit de lui envoyer UNE réponse privée (DM). Le commentaire = son
# consentement. C'est le seul canal d'acquisition sociale autorisé par Meta : le
# cold DM (écrire le premier à un inconnu) est interdit ET techniquement bloqué
# (fenêtre 24h). Une fois le DM ouvert, la conversation retombe sur l'agent normal.
#
# Webhook : les commentaires arrivent sous `entry[].changes[]` (≠ `messaging[]`) :
# - Facebook Page   → field "feed",     value.item == "comment", verb == "add" ;
# - Instagram       → field "comments", value.id == id du commentaire.
# ---------------------------------------------------------------------------


def parse_comments(payload: dict) -> list[dict[str, Any]]:
    """Extrait les nouveaux commentaires (FB feed + IG comments) d'un webhook.

    Ignore : nos propres commentaires (auteur == la Page/compte), les
    modifications/suppressions (verb != add), les événements non-commentaire
    (réactions, posts, partages). Renvoie {comment_id, page_id, platform,
    from_id, from_name, text, post_id}.
    """
    platform = "instagram" if payload.get("object") == "instagram" else "messenger"
    out: list[dict[str, Any]] = []
    try:
        for entry in payload.get("entry", []) or []:
            page_id = str(entry.get("id") or "")
            for ch in entry.get("changes", []) or []:
                field = ch.get("field")
                val = ch.get("value") or {}
                frm = val.get("from") or {}
                from_id = str(frm.get("id") or "")
                # On n'agit jamais sur nos propres commentaires (évite les boucles
                # avec la réponse publique qu'on poste).
                if from_id and from_id == page_id:
                    continue
                if field == "feed":  # Facebook Page
                    if val.get("item") != "comment" or val.get("verb") != "add":
                        continue
                    comment_id = str(val.get("comment_id") or "")
                    post_id = str(val.get("post_id") or "")
                    text = val.get("message") or ""
                    from_name = frm.get("name") or ""
                elif field == "comments":  # Instagram
                    comment_id = str(val.get("id") or "")
                    post_id = str((val.get("media") or {}).get("id") or "")
                    text = val.get("text") or ""
                    from_name = frm.get("username") or ""
                else:
                    continue
                if not comment_id:
                    continue
                out.append({"comment_id": comment_id, "page_id": page_id,
                            "platform": platform, "from_id": from_id,
                            "from_name": from_name, "text": text, "post_id": post_id})
    except Exception:  # noqa: BLE001
        log.warning("parse commentaires Messenger/IG KO", exc_info=True)
    return out


def send_private_reply(page_id: str, comment_id: str, text: str) -> bool:
    """Réponse PRIVÉE (DM) à l'auteur d'un commentaire — Meta « Private Replies ».

    Une seule par commentaire est autorisée : Meta refuse la 2e (backstop). On
    cible le commentaire (`recipient.comment_id`), pas un PSID. Marche pour
    Messenger ET Instagram via `POST /{page_id}/messages` + Page token.
    """
    if not (configured() and page_id and comment_id and text):
        return False
    payload = {"recipient": {"comment_id": str(comment_id)},
               "message": {"text": text[:1900]}}
    try:
        r = httpx.post(_graph(f"{page_id}/messages"),
                       params={"access_token": settings.messenger_page_token},
                       json=payload, timeout=15.0)
        if r.status_code not in (200, 201):
            log.warning("private reply %s: %s", r.status_code, r.text[:200])
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("private reply KO: %s", e)
        return False


def publish_facebook(page_id: str, message: str, image_url: str | None = None) -> bool:
    """Publie un post sur une Page Facebook (texte, ou photo+légende). Page token.

    ⚠️ Pour publier sur la page d'un VRAI client à l'échelle, l'app doit avoir
    `pages_manage_posts` approuvé (App Review). Marche sur nos propres pages en mode dev.
    """
    if not (configured() and page_id and message):
        return False
    if image_url:
        path, payload = f"{page_id}/photos", {"url": image_url, "caption": message[:1900]}
    else:
        path, payload = f"{page_id}/feed", {"message": message[:1900]}
    try:
        r = httpx.post(_graph(path),
                       params={"access_token": settings.messenger_page_token},
                       json=payload, timeout=20.0)
        if r.status_code not in (200, 201):
            log.warning("publish FB %s: %s", r.status_code, r.text[:200])
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("publish FB KO: %s", e)
        return False


def publish_instagram(ig_user_id: str, caption: str, image_url: str) -> bool:
    """Publie sur Instagram (2 étapes : créer le média, puis publier). Image requise."""
    if not (configured() and ig_user_id and image_url):
        return False
    try:
        c = httpx.post(_graph(f"{ig_user_id}/media"),
                       params={"access_token": settings.messenger_page_token},
                       json={"image_url": image_url, "caption": (caption or "")[:1900]}, timeout=20.0)
        if c.status_code not in (200, 201):
            log.warning("IG media %s: %s", c.status_code, c.text[:200]); return False
        creation_id = (c.json() or {}).get("id")
        if not creation_id:
            return False
        p = httpx.post(_graph(f"{ig_user_id}/media_publish"),
                       params={"access_token": settings.messenger_page_token},
                       json={"creation_id": creation_id}, timeout=20.0)
        return p.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("publish IG KO: %s", e)
        return False


def reply_public_comment(comment_id: str, text: str, platform: str = "messenger") -> bool:
    """Réponse PUBLIQUE sous le commentaire (« Je vous réponds en privé 📩 »).

    Endpoints différents : Facebook → `/{comment_id}/comments`, Instagram →
    `/{comment_id}/replies`. Optionnel (toggle cockpit) ; échoue en silence.
    """
    if not (configured() and comment_id and text):
        return False
    path = f"{comment_id}/replies" if platform == "instagram" else f"{comment_id}/comments"
    try:
        r = httpx.post(_graph(path),
                       params={"access_token": settings.messenger_page_token},
                       json={"message": text[:1900]}, timeout=15.0)
        if r.status_code not in (200, 201):
            log.warning("public reply %s: %s", r.status_code, r.text[:200])
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("public reply KO: %s", e)
        return False
