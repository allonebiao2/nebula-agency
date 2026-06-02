"""Alertes Telegram vers Mongazi (réutilise le bot NOVA).

Si le bot n'est pas configuré, les notifications sont simplement ignorées
(elles n'empêchent jamais une inscription d'aboutir).
"""
from __future__ import annotations

import logging

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
