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


def notify_subscription_reminder(merchant: dict, days: int, price: int) -> None:
    """Relance avant l'échéance de l'abonnement."""
    notify_mongazi(
        "⏳ <b>Abonnement à renouveler</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"⏰ Expire dans <b>{days} jour(s)</b>\n"
        f"💰 {price:,} F/mois".replace(",", " ") +
        f"\n🆔 <code>{merchant.get('id')}</code>"
    )
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"Bonjour 👋 Votre abonnement Vendora ({merchant.get('business_name','votre boutique')}) "
        f"expire dans {days} jour(s). Pensez à renouveler pour que votre agent continue à vendre. Merci !"
    )


def _trial_value_line(stats: dict | None) -> str:
    """Phrase de preuve de valeur de l'essai (vide si rien à montrer)."""
    s = stats or {}
    convos = int(s.get("conversations") or 0)
    orders = int(s.get("orders") or 0)
    rev = s.get("revenue") or 0
    if not (convos or orders):
        return ""
    bits = []
    if convos:
        bits.append(f"{convos} client(s) servi(s)")
    if orders:
        bits.append(f"{orders} commande(s)" + (f" ({_fmt_fcfa(rev)})" if rev else ""))
    return " · ".join(bits)


def notify_trial_reminder(merchant: dict, days: int, price: int, stats: dict | None = None) -> None:
    """Rappel J-1 avant la fin de l'essai gratuit (avec preuve de valeur)."""
    val = _trial_value_line(stats)
    notify_mongazi(
        "⏳ <b>Essai gratuit bientôt terminé</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"⏰ Fin dans <b>{days} jour(s)</b>\n"
        + (f"📈 Pendant l'essai : {val}\n" if val else "")
        + f"💰 Activation {price:,} F/mois".replace(",", " ")
        + f"\n🆔 <code>{merchant.get('id')}</code>"
    )
    extra = f" Pendant l'essai, votre agent a déjà {val}." if val else ""
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"Bonjour 👋 Votre essai gratuit Vendora ({merchant.get('business_name','votre boutique')}) "
        f"se termine dans {days} jour(s).{extra} Activez pour ne pas perdre votre agent — merci !"
    )


def notify_trial_ended(merchant: dict, stats: dict | None = None) -> None:
    """Fin de l'essai gratuit → boutique suspendue (données conservées) + preuve de valeur."""
    val = _trial_value_line(stats)
    notify_mongazi(
        "🎁 <b>Essai gratuit terminé — boutique en pause</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        + (f"📈 Bilan de l'essai : {val}\n" if val else "")
        + "➡️ Relance-le pour le convertir (ses données sont conservées).\n"
        + f"🆔 <code>{merchant.get('id')}</code>"
    )
    extra = f" Pendant l'essai, votre agent a {val}." if val else ""
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"Votre essai gratuit Vendora ({merchant.get('business_name','votre boutique')}) est terminé.{extra} "
        f"Votre agent et toutes vos données sont gardés — activez en 1 paiement pour reprendre là où vous en étiez."
    )


def notify_winback(merchant: dict) -> None:
    """Reconquête d'une boutique en pause (essai fini / abo expiré) — données conservées."""
    name = merchant.get("business_name", "votre boutique")
    raison = "votre essai" if merchant.get("is_trial") else "votre abonnement"
    notify_mongazi(
        "💌 <b>Win-back — boutique à reconquérir</b>\n\n"
        f"🏪 {name}\n"
        f"⏸️ En pause ({raison} terminé) — relance envoyée.\n"
        f"🆔 <code>{merchant.get('id')}</code>"
    )
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"Bonjour 👋 Votre agent Vendora ({name}) est en pause, mais "
        f"<b>toutes vos données et conversations sont gardées</b>. Réactivez en 1 paiement "
        f"pour reprendre exactement où vous en étiez — vos clients vous attendent 🙂".replace("<b>", "").replace("</b>", "")
    )


def notify_subscription_expired(merchant: dict) -> None:
    """Abonnement expiré → boutique suspendue."""
    notify_mongazi(
        "🛑 <b>Abonnement expiré — boutique suspendue</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"➡️ L'agent ne vend plus jusqu'au renouvellement.\n"
        f"🆔 <code>{merchant.get('id')}</code>"
    )
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"Votre abonnement Vendora ({merchant.get('business_name','votre boutique')}) a expiré. "
        f"Votre agent est en pause. Renouvelez pour le réactiver — merci !"
    )


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


def notify_appointment(merchant: dict, appt: dict) -> None:
    """Prévient le commerçant d'une nouvelle demande de rendez-vous."""
    who = appt.get("customer_name") or appt.get("customer_whatsapp") or "—"
    service = (appt.get("service") or "").strip()
    when = (appt.get("requested_time") or "—").strip()
    note = (appt.get("note") or "").strip()
    text = (
        "📅 <b>Nouvelle demande de rendez-vous !</b>\n\n"
        f"🏪 {merchant.get('business_name','?')}\n"
        f"👤 {who}\n"
        f"🗓️ {when}\n"
        + (f"💼 {service}\n" if service else "")
        + (f"📝 {note}\n" if note else "")
        + "\nÀ confirmer avec le client 🙏"
    )
    notify_mongazi(text)
    plain = (
        f"📅 Demande de RDV — {merchant.get('business_name','votre boutique')}\n"
        f"Client : {who}\nQuand : {when}"
        + (f"\nPrestation : {service}" if service else "")
        + (f"\nNote : {note}" if note else "")
    )
    _whatsapp_owner(merchant.get("owner_whatsapp"), merchant.get("country"), plain)


def notify_weekly_digest(merchant: dict, stats: dict) -> None:
    """Résumé hebdo au commerçant : preuve de valeur (anti-résiliation).

    « Ton agent a parlé à X clients cette semaine et conclu Y ventes. »
    """
    name = merchant.get("business_name", "votre boutique")
    convos = int(stats.get("conversations") or 0)
    won = int(stats.get("won") or 0)
    revenue = stats.get("revenue") or 0

    notify_mongazi(
        "📊 <b>Bilan hebdo Vendora</b>\n\n"
        f"🏪 {name}\n"
        f"💬 {convos} client(s) servis par l'agent\n"
        f"🛒 {won} vente(s) conclue(s)\n"
        f"💰 {_fmt_fcfa(revenue)} générés\n"
        f"🆔 <code>{merchant.get('id')}</code>"
    )
    ventes = f"conclu {won} vente(s)" if won else "engagé plusieurs clients"
    rev = f" pour {_fmt_fcfa(revenue)}" if won and revenue else ""
    _whatsapp_owner(
        merchant.get("owner_whatsapp"), merchant.get("country"),
        f"📊 Bilan de la semaine — {name}\n\n"
        f"Votre agent Vendora a parlé à {convos} client(s) et {ventes}{rev}. "
        f"Il travaille pour vous 24h/24 👌"
    )


def notify_learning_summary(result: dict) -> None:
    """Résumé à Mongazi après un cycle d'auto-amélioration (cerveau d'apprentissage)."""
    if result.get("skipped"):
        notify_mongazi(
            "🧠 <b>Cerveau d'apprentissage</b>\n\n"
            f"Analyse passée : {result.get('reason', 'pas assez de données.')}"
        )
        return
    reason = (result.get("trigger_reason") or "").strip()
    reason_line = f"⚡ Déclenché : {reason}\n" if reason else ""
    notify_mongazi(
        "🧠 <b>Vendora a appris de ses conversations</b>\n\n"
        f"{reason_line}"
        f"💬 {result.get('conversations', 0)} conversation(s) analysées "
        f"({result.get('won', 0)} conclues / {result.get('lost', 0)} perdues)\n"
        f"📚 Leçons collectives : <b>{'mises à jour' if result.get('global_updated') else 'inchangées'}</b>\n"
        f"🏪 Boutiques améliorées individuellement : <b>{result.get('merchants_analyzed', 0)}</b>\n"
        f"🤖 Modèle : {result.get('model', '—')}\n\n"
        "Les agents vendeurs appliquent désormais ces leçons."
    )


def notify_experiment_update(out: dict) -> None:
    """Annonce une avancée de l'auto-expérimentation (promotion / nouvelle variante)."""
    parts = []
    if out.get("seeded"):
        parts.append("🧪 Première expérience de vente lancée (champion vs challenger).")
    if out.get("promoted"):
        parts.append(f"🏆 Variante gagnante adoptée : <b>{out['promoted']}</b> "
                     "(elle conclut le plus de ventes — gardée par défaut).")
    if out.get("spawned"):
        parts.append(f"🔬 Nouvelle variante mise à l'épreuve : <b>{out['spawned']}</b>.")
    if not parts:
        return
    notify_mongazi("🧬 <b>Auto-amélioration des ventes</b>\n\n" + "\n\n".join(parts))


def notify_ceo_review(result: dict) -> None:
    """Le directeur autonome présente ses décisions à Mongazi (Telegram)."""
    recos = result.get("recommendations") or []
    if not recos:
        notify_mongazi(
            "🧭 <b>Revue du directeur Vendora</b>\n\n"
            "Pas de recommandation cette fois (données insuffisantes ou rien d'urgent). "
            "Je continue d'observer."
        )
        return
    lines = []
    for i, r in enumerate(recos[:5], 1):
        tag = "💰" if r.get("financier") else ("🤖" if r.get("categorie") == "modele" else "•")
        lines.append(f"{i}. {tag} <b>{r.get('titre','?')}</b>\n   {r.get('recommandation','')}")
    notify_mongazi(
        "🧭 <b>Le directeur Vendora a réfléchi — décisions à valider</b>\n\n"
        f"MRR {int(result.get('mrr',0)):,} F".replace(",", " ") +
        f" · {result.get('merchants',0)} boutiques · conversion ventes {result.get('sales_conversion_pct',0)} %\n\n"
        + "\n\n".join(lines) +
        "\n\n➡️ Ouvre le cockpit (panneau « Décisions du directeur ») pour valider ✓ ou rejeter ✗."
    )


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


def send_customer_whatsapp(customer_whatsapp: str | None, text: str) -> bool:
    """Envoie un message WhatsApp à un CLIENT via Twilio (relances autonomes).

    `customer_whatsapp` est au format Twilio « whatsapp:+229... » (tel que stocké).
    ⚠️ WhatsApp n'autorise les messages libres que dans la fenêtre de 24h après le
    dernier message du client (sinon il faut un template approuvé — WhatsApp prod).
    Les relances visent justement cette fenêtre. Retourne True si l'envoi part.
    """
    sid = settings.twilio_account_sid
    token = settings.twilio_auth_token
    from_number = settings.vendora_whatsapp_number
    if not (sid and token and from_number and customer_whatsapp):
        return False
    to = customer_whatsapp.strip()
    if not to.startswith("whatsapp:"):
        e164 = _to_e164(to, "BJ")
        if not e164:
            return False
        to = f"whatsapp:{e164}"
    from_e164 = "+" + re.sub(r"\D", "", from_number)
    try:
        r = httpx.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data={"From": f"whatsapp:{from_e164}", "To": to, "Body": text},
            auth=(sid, token),
            timeout=10.0,
        )
        return r.status_code in (200, 201)
    except Exception as e:  # noqa: BLE001
        log.warning("[notify] WhatsApp client échoué : %s", e)
        return False


def notify_followups_summary(stats: dict) -> None:
    """Résumé Telegram après une vague de relances (seulement si quelque chose est parti)."""
    sent = int(stats.get("sent") or 0)
    if sent <= 0:
        return
    notify_mongazi(
        "📲 <b>Relances automatiques</b>\n\n"
        f"L'agent a recontacté <b>{sent}</b> client(s) de lui-même "
        f"(💬 {stats.get('silent', 0)} silencieux · 🛒 {stats.get('cart', 0)} paniers).\n"
        "Objectif : récupérer des ventes qui allaient être perdues."
    )


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
