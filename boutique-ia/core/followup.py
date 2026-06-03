"""RELANCES AUTONOMES — l'agent recontacte de lui-même les clients qui allaient être
perdus, pour récupérer des ventes. Deux cas :

1. **Client silencieux** : il s'est montré intéressé (a discuté d'un produit) puis n'a
   plus répondu après le dernier message de l'agent. → relance dans la fenêtre 6-22h.
2. **Panier abandonné** : une commande a été confirmée (`bia_orders` statut `pending`)
   mais le paiement n'est pas arrivé. → relance pour finaliser.

Le message est rédigé par le vendeur IA (Haiku) avec la fiche de la boutique + les
leçons apprises (cerveau d'apprentissage) → ton juste, légère urgence honnête.

GARDE-FOUS (modèle de gouvernance Mongazi : autonome dans ses limites) :
- OFF par défaut (`bia_settings.followups_enabled`) — Mongazi autorise via le cockpit.
- Fenêtre 6-22h (reste dans la fenêtre WhatsApp de 24h → messages libres autorisés).
- 1 relance max par client / 3 jours (cooldown), respect des opt-out (STOP).
- Boutique active uniquement, plafonds/jour (global + par boutique).
- Uniquement les vrais clients WhatsApp (pas les essais/démo).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger("boutique-ia.followup")

WINDOW_DAYS = 2          # fenêtre d'observation (silencieux + paniers)
MIN_HOURS = 6            # on attend au moins ça avant de relancer
MAX_HOURS = 22           # ... et pas au-delà (fenêtre WhatsApp de 24h)
COOLDOWN_DAYS = 3        # 1 relance max par client / boutique sur cette période
GLOBAL_DAILY_CAP = 200   # sécurité globale
MERCHANT_DAILY_CAP = 40  # sécurité par boutique


def _age_hours(iso: Any) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600


def _is_real_customer(customer: str | None) -> bool:
    """Vrai client WhatsApp (pas un essai/démo/test depuis le simulateur web)."""
    return bool(customer) and str(customer).strip().lower().startswith("whatsapp:")


def run_followups() -> dict[str, Any]:
    """Une vague de relances autonomes. Retourne des stats (sent/silent/cart)."""
    from config import settings
    from core import brain
    from db.client import (
        count_followups_since,
        count_followups_today,
        followed_up_recently,
        get_active_lessons,
        get_merchant,
        get_setting_bool,
        is_opted_out,
        list_pending_orders,
        list_products,
        load_history,
        recent_messages,
        recent_orders,
        save_message,
        subscription_active,
        _today_start_iso,
    )
    from core import learning
    from notify import notify_followups_summary, send_customer_whatsapp

    stats = {"enabled": False, "sent": 0, "silent": 0, "cart": 0,
             "skipped": False, "reason": ""}

    # Gating : capacité autorisée par Mongazi (OFF par défaut).
    if not get_setting_bool("followups_enabled", False):
        return stats
    stats["enabled"] = True
    # Envoi sortant = Twilio requis.
    if not (settings.twilio_account_sid and settings.twilio_auth_token
            and settings.vendora_whatsapp_number):
        stats["skipped"] = True
        stats["reason"] = "Twilio non configuré (envoi sortant impossible)."
        return stats
    if count_followups_today() >= GLOBAL_DAILY_CAP:
        stats["skipped"] = True
        stats["reason"] = "Plafond global du jour atteint."
        return stats

    merchants: dict[str, dict] = {}
    products_cache: dict[str, list] = {}
    lessons_cache: dict[str, str] = {}
    today_iso = _today_start_iso()

    def _merchant(mid: str) -> dict | None:
        if mid not in merchants:
            merchants[mid] = get_merchant(mid) or {}
        return merchants[mid]

    def _eligible(mid: str, customer: str) -> bool:
        if not _is_real_customer(customer) or is_opted_out(customer):
            return False
        m = _merchant(mid)
        if not m or not subscription_active(m):
            return False
        if followed_up_recently(mid, customer, COOLDOWN_DAYS):
            return False
        if count_followups_since(today_iso, mid) >= MERCHANT_DAILY_CAP:
            return False
        return True

    def _send(mid: str, customer: str, kind: str, hours: int | None,
              order: dict | None = None) -> bool:
        m = _merchant(mid)
        if mid not in products_cache:
            products_cache[mid] = list_products(mid)
        if mid not in lessons_cache:
            try:
                lessons_cache[mid] = get_active_lessons(mid)
            except Exception:  # noqa: BLE001
                lessons_cache[mid] = ""
        history = load_history(mid, customer, limit=brain.HISTORY_LIMIT)
        if not history:
            return False
        try:
            msg = brain.followup_message(m, products_cache[mid], history,
                                         lessons=lessons_cache[mid], kind=kind, hours=hours)
        except Exception:  # noqa: BLE001
            log.warning("génération relance échouée (%s)", mid, exc_info=True)
            return False
        if not msg or not msg.strip():
            return False
        if not send_customer_whatsapp(customer, msg):
            return False
        # Trace + on garde le message dans l'historique (conversation cohérente).
        from db.client import record_followup
        record_followup(mid, customer, kind, msg, order_id=(order or {}).get("id"))
        try:
            save_message(mid, customer, "assistant", msg)
        except Exception:  # noqa: BLE001
            pass
        return True

    # ---- 1) Clients SILENCIEUX (devis sans réponse) ----
    try:
        convos = learning._build_conversations(
            recent_messages(WINDOW_DAYS), recent_orders(WINDOW_DAYS))
        for c in convos:
            if stats["sent"] >= GLOBAL_DAILY_CAP:
                break
            if c["won"]:
                continue  # déjà acheté
            msgs = c["msgs"]
            if not msgs or msgs[-1].get("role") != "assistant":
                continue  # l'agent doit avoir parlé en dernier (client muet ensuite)
            age = _age_hours(msgs[-1].get("created_at"))
            if age is None or age < MIN_HOURS or age > MAX_HOURS:
                continue
            mid, customer = c["merchant_id"], c["customer"]
            if not _eligible(mid, customer):
                continue
            if _send(mid, customer, "silent", int(age)):
                stats["sent"] += 1
                stats["silent"] += 1
    except Exception:  # noqa: BLE001
        log.warning("relances silencieux", exc_info=True)

    # ---- 2) Paniers ABANDONNÉS (commande non payée) ----
    try:
        for o in list_pending_orders(WINDOW_DAYS):
            if stats["sent"] >= GLOBAL_DAILY_CAP:
                break
            customer = o.get("customer_whatsapp")
            mid = o.get("merchant_id")
            if not mid or not customer:
                continue
            age = _age_hours(o.get("created_at"))
            if age is None or age < MIN_HOURS or age > MAX_HOURS:
                continue
            if not _eligible(mid, customer):
                continue
            if _send(mid, customer, "cart", int(age), order=o):
                stats["sent"] += 1
                stats["cart"] += 1
    except Exception:  # noqa: BLE001
        log.warning("relances paniers", exc_info=True)

    if stats["sent"] > 0:
        try:
            notify_followups_summary(stats)
        except Exception:  # noqa: BLE001
            pass
    log.info("relances : %d envoyées (%d silencieux, %d paniers)",
             stats["sent"], stats["silent"], stats["cart"])
    return stats
