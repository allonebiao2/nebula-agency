"""Alertes Telegram vers Mongazi (réutilise le bot NOVA).

Si le bot n'est pas configuré, les notifications sont simplement ignorées
(elles n'empêchent jamais une inscription d'aboutir).
"""
from __future__ import annotations

import logging
import re

import httpx

from config import settings

log = logging.getLogger("boutique-ia.notify")


def notify_mongazi(text: str) -> bool:
    """Envoie un message Telegram à Mongazi. Best-effort, ne lève jamais."""
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id_mongazi
    if not token or not chat_id:
        log.info("[notify] Telegram non configuré — message ignoré : %s", text[:80])
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10.0,
        )
        return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        log.warning("[notify] échec envoi Telegram : %s", e)
        return False


def notify_new_merchant(merchant: dict, products_count: int) -> None:
    """Alerte à chaque nouvelle inscription de boutique."""
    notify_mongazi(
        "🆕 <b>Nouvelle inscription Boutique IA</b>\n\n"
        f"🏪 <b>{merchant.get('business_name','?')}</b> ({merchant.get('sector','?')})\n"
        f"📍 {merchant.get('city','?')}\n"
        f"📱 WhatsApp clients : {merchant.get('whatsapp_business','?')}\n"
        f"👤 Patron : {merchant.get('owner_whatsapp') or '—'}\n"
        f"📦 {products_count} produit(s)\n"
        f"💳 MoMo encaissement : {merchant.get('momo_number') or '—'} ({merchant.get('momo_network') or '—'})\n\n"
        f"⏳ Statut : <b>en attente de paiement</b>\n"
        f"🆔 <code>{merchant.get('id')}</code>"
    )


def notify_payment_submitted(merchant: dict, ref: str) -> None:
    """Alerte quand un commerçant déclare avoir payé l'abonnement."""
    notify_mongazi(
        "💰 <b>Paiement abonnement déclaré</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"🧾 Référence MoMo : <code>{ref}</code>\n\n"
        f"➡️ À vérifier puis activer.\n"
        f"🆔 <code>{merchant.get('id')}</code>"
    )


# ---------------------------------------------------------------------------
# Étage 3 — alerte nouvelle commande (vers le commerçant)
# ---------------------------------------------------------------------------

def _fmt_fcfa(value) -> str:
    if value is None:
        return "—"
    try:
        return f"{int(float(value)):,}".replace(",", " ") + " F"
    except (TypeError, ValueError):
        return str(value)


def _fmt_items(items: list[dict]) -> str:
    lines = []
    for it in items or []:
        qty = it.get("quantite") or 1
        name = it.get("produit") or "?"
        pu = it.get("prix_unitaire")
        suffix = f" ({_fmt_fcfa(pu)})" if pu else ""
        lines.append(f"• {qty} × {name}{suffix}")
    return "\n".join(lines) or "• (article non précisé)"


def notify_new_order(merchant: dict, order: dict, items: list[dict]) -> None:
    """Prévient le commerçant qu'une commande vient d'être conclue par le vendeur IA.

    Canal sûr maintenant : Telegram vers Mongazi (qui relaie / supervise).
    Canal direct si Twilio configuré : WhatsApp vers le numéro perso du patron.
    """
    client = order.get("customer_name") or order.get("customer_whatsapp") or "—"
    addr = order.get("delivery_address")
    deliv = order.get("delivery_mode") or "—"
    deliv_line = f"🚚 {deliv}" + (f" → {addr}" if addr else "")
    pm = order.get("payment_method")
    pay_line = ""
    if pm == "livraison":
        pay_line = "\n💵 Paiement : <b>à la livraison</b> (encaisser à la remise)"
    elif pm == "mobile_money":
        pay_line = "\n💳 Paiement : Mobile Money (avance)"

    notify_mongazi(
        "🛒 <b>Nouvelle commande !</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"👤 Client : {client}\n\n"
        f"{_fmt_items(items)}\n\n"
        f"💰 Total : <b>{_fmt_fcfa(order.get('total'))}</b>\n"
        f"{deliv_line}{pay_line}\n"
        f"🆔 <code>{order.get('id')}</code>"
    )

    # Best-effort : WhatsApp direct au patron (dormant tant que Twilio non configuré)
    plain = (
        f"🛒 Nouvelle commande sur {merchant.get('business_name','votre boutique')} !\n\n"
        f"Client : {client}\n"
        + "\n".join(
            f"- {(it.get('quantite') or 1)} x {it.get('produit') or '?'}" for it in (items or [])
        )
        + f"\n\nTotal : {_fmt_fcfa(order.get('total'))}\n{deliv}"
        + (f" : {addr}" if addr else "")
    )
    _whatsapp_owner(merchant.get("owner_whatsapp"), merchant.get("country"), plain)


def notify_hot_lead(merchant: dict, customer: str | None, raison: str,
                    resume: str, nom_client: str | None = None) -> None:
    """Prévient le commerçant qu'un client a besoin d'attention (lead chaud / réclamation)."""
    who = nom_client or customer or "—"
    text = (
        "🔥 <b>Client à rappeler !</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"👤 {who}\n"
        f"📌 {raison}\n"
        f"💬 {resume}"
    )
    notify_mongazi(text)
    plain = (
        f"🔥 Client à rappeler — {merchant.get('business_name','votre boutique')}\n"
        f"Client : {who}\n{raison} : {resume}"
    )
    _whatsapp_owner(merchant.get("owner_whatsapp"), merchant.get("country"), plain)


def _to_e164(number: str | None, country: str | None) -> str | None:
    """Normalisation best-effort d'un numéro local en format international (+...)."""
    if not number:
        return None
    digits = re.sub(r"\D", "", number)
    if not digits:
        return None
    if number.strip().startswith("+"):
        return "+" + digits
    if digits.startswith("00"):
        return "+" + digits[2:]
    if digits.startswith("229"):
        return "+" + digits
    # Bénin par défaut (numéros locaux 8 ou 10 chiffres)
    if (country or "BJ").upper() == "BJ" and len(digits) in (8, 10):
        return "+229" + digits
    if len(digits) >= 11:
        return "+" + digits
    return None


def _whatsapp_owner(owner_number: str | None, country: str | None, text: str) -> None:
    """Envoie un WhatsApp au patron via l'API Twilio, si les identifiants existent."""
    sid = settings.twilio_account_sid
    token = settings.twilio_auth_token
    from_number = settings.vendora_whatsapp_number
    to = _to_e164(owner_number, country)
    if not (sid and token and from_number and to):
        return
    from_e164 = "+" + re.sub(r"\D", "", from_number)
    try:
        httpx.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data={
                "From": f"whatsapp:{from_e164}",
                "To": f"whatsapp:{to}",
                "Body": text,
            },
            auth=(sid, token),
            timeout=10.0,
        )
    except Exception as e:  # noqa: BLE001
        log.warning("[notify] WhatsApp patron échoué : %s", e)
