"""Abonnements NEBULA Agency (vitrines / catalogues digitaux) — facturation
trimestrielle + RAPPELS d'échéance automatiques.

Distinct des forfaits Vendora (bia_merchants) : ici ce sont les clients « site web »
de l'agence (vitrine 15 000 F / 3 mois, catalogue digital 5 000 F / 3 mois).

Rappels : J-7 puis le jour J. Canaux : Telegram (Mongazi) + Email (Mongazi + client,
Resend) toujours ; WhatsApp au client = best-effort (nécessite un template Meta approuvé
pour un message hors fenêtre 24h — sinon l'envoi échoue silencieusement, l'email prend le relais).

Appelé par la boucle de fond (`run_nebula_reminders`). Les drapeaux notif_*_sent évitent
tout doublon : on n'envoie qu'UNE fois par étape et par cycle (remis à zéro au paiement).
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

log = logging.getLogger("boutique-ia.nebula_subs")

OFFER_LABELS = {"vitrine": "Vitrine", "catalogue": "Catalogue digital"}
OFFER_AMOUNTS = {"vitrine": 15000, "catalogue": 5000}
PRE_DAYS = 7  # rappel J-7


# --- Données -------------------------------------------------------------

def _db():
    from db.client import get_db
    return get_db()


def create_sub(client_name: str, offer: str, amount: float | None,
               client_whatsapp: str | None, client_email: str | None,
               next_due: str, period_months: int = 3) -> dict[str, Any]:
    offer = (offer or "vitrine").strip().lower()
    if offer not in OFFER_AMOUNTS:
        offer = "vitrine"
    if amount in (None, "", 0):
        amount = OFFER_AMOUNTS[offer]
    row = {"client_name": (client_name or "").strip(), "offer": offer,
           "amount": float(amount), "client_whatsapp": (client_whatsapp or "").strip() or None,
           "client_email": (client_email or "").strip() or None,
           "next_due": next_due, "period_months": int(period_months or 3),
           "status": "active", "notif_pre_sent": False, "notif_due_sent": False}
    res = _db().table("nebula_abonnements").insert(row).execute()
    return res.data[0] if res.data else {}


def list_subs(status: str | None = "active") -> list[dict[str, Any]]:
    try:
        q = _db().table("nebula_abonnements").select("*")
        if status:
            q = q.eq("status", status)
        return q.order("next_due", desc=False).limit(500).execute().data or []
    except Exception:  # noqa: BLE001
        return []


def mark_paid(sub_id: str) -> dict[str, Any]:
    """Encaissé : repousse l'échéance de `period_months` et réarme les rappels."""
    try:
        rows = (_db().table("nebula_abonnements").select("*").eq("id", sub_id)
                .limit(1).execute().data or [])
        if not rows:
            return {}
        sub = rows[0]
        base = _parse_date(sub.get("next_due")) or date.today()
        # On part de l'échéance (ou d'aujourd'hui si en retard) + N mois.
        start = max(base, date.today())
        nxt = _add_months(start, int(sub.get("period_months") or 3))
        res = (_db().table("nebula_abonnements")
               .update({"next_due": nxt.isoformat(),
                        "notif_pre_sent": False, "notif_due_sent": False})
               .eq("id", sub_id).execute())
        return res.data[0] if res.data else {}
    except Exception:  # noqa: BLE001
        log.warning("mark_paid échoué", exc_info=True)
        return {}


def set_status(sub_id: str, status: str) -> bool:
    try:
        _db().table("nebula_abonnements").update({"status": status}).eq("id", sub_id).execute()
        return True
    except Exception:  # noqa: BLE001
        return False


# --- Dates ----------------------------------------------------------------

def _parse_date(v: Any) -> date | None:
    try:
        return datetime.fromisoformat(str(v)[:10]).date()
    except (ValueError, TypeError):
        return None


def _add_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    # Dernier jour du mois cible si le jour n'existe pas (ex: 31).
    import calendar
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)


def _fmt_fcfa(v: Any) -> str:
    try:
        return f"{int(float(v)):,}".replace(",", " ") + " F"
    except (TypeError, ValueError):
        return str(v)


# --- Rappels ---------------------------------------------------------------

def _send_client_email(sub: dict, due: date, when: str) -> None:
    email = sub.get("client_email")
    if not email:
        return
    offer = OFFER_LABELS.get(sub.get("offer"), "abonnement")
    montant = _fmt_fcfa(sub.get("amount"))
    if when == "pre":
        subject = f"Votre {offer} NEBULA — renouvellement le {due:%d/%m/%Y}"
        body = (f"Bonjour {sub.get('client_name') or ''},\n\n"
                f"Votre abonnement {offer} arrive à échéance le {due:%d/%m/%Y} "
                f"(montant : {montant}, tous les 3 mois).\n"
                "Merci de procéder au renouvellement pour que votre site reste en ligne sans interruption.\n\n"
                "Un grand merci pour votre confiance.\n— NEBULA Agency")
    else:
        subject = f"Votre {offer} NEBULA — échéance aujourd'hui"
        body = (f"Bonjour {sub.get('client_name') or ''},\n\n"
                f"Votre abonnement {offer} ({montant} / 3 mois) arrive à échéance aujourd'hui "
                f"({due:%d/%m/%Y}).\nMerci de régler pour maintenir votre site en ligne.\n\n"
                "Merci de votre confiance.\n— NEBULA Agency")
    try:
        from core.prospecting import send_email
        send_email(email, subject, body)
    except Exception:  # noqa: BLE001
        log.warning("email client échéance échoué", exc_info=True)


def _send_client_whatsapp(sub: dict, due: date, when: str) -> None:
    """Best-effort : nécessite un template Meta approuvé (message hors fenêtre 24h).
    Si l'envoi échoue, l'email a déjà pris le relais — on n'alerte pas."""
    num = sub.get("client_whatsapp")
    if not num:
        return
    offer = OFFER_LABELS.get(sub.get("offer"), "abonnement")
    montant = _fmt_fcfa(sub.get("amount"))
    quand = (f"le {due:%d/%m/%Y}" if when == "pre" else "aujourd'hui")
    msg = (f"Bonjour 🙏 Votre {offer} NEBULA arrive à échéance {quand} "
           f"({montant} / 3 mois). Merci de renouveler pour rester en ligne sans coupure.")
    try:
        from core import whatsapp_meta
        whatsapp_meta.send_text(num, msg)  # échoue sans template → silencieux (email pris le relais)
    except Exception:  # noqa: BLE001
        pass


def _notify_mongazi(sub: dict, due: date, when: str) -> None:
    from notify import notify_mongazi
    offer = OFFER_LABELS.get(sub.get("offer"), "abonnement")
    montant = _fmt_fcfa(sub.get("amount"))
    titre = ("⏰ <b>Échéance dans 7 jours</b>" if when == "pre"
             else "🔔 <b>Échéance AUJOURD'HUI</b>")
    notify_mongazi(
        f"{titre} — abonnement NEBULA\n\n"
        f"👤 {sub.get('client_name') or '—'}\n"
        f"🌐 {offer}\n"
        f"💰 {montant} (tous les 3 mois)\n"
        f"📅 {due:%d/%m/%Y}\n"
        + (f"📞 {sub.get('client_whatsapp')}\n" if sub.get("client_whatsapp") else "")
        + (f"✉️ {sub.get('client_email')}\n" if sub.get("client_email") else "")
        + "\nPensez à encaisser puis marquez « Payé » dans le cockpit."
    )


def run_nebula_reminders() -> dict[str, int]:
    """Parcourt les abonnements actifs et envoie les rappels d'échéance (J-7 + jour J).
    Idempotent : drapeaux notif_pre_sent / notif_due_sent (1 envoi par étape/cycle)."""
    today = date.today()
    sent = {"pre": 0, "due": 0}
    for sub in list_subs("active"):
        due = _parse_date(sub.get("next_due"))
        if not due:
            continue
        delta = (due - today).days
        # Jour J (ou en retard) : rappel d'échéance, une fois.
        if delta <= 0 and not sub.get("notif_due_sent"):
            _notify_mongazi(sub, due, "due")
            _send_client_email(sub, due, "due")
            _send_client_whatsapp(sub, due, "due")
            _mark_sent(sub["id"], "due")
            sent["due"] += 1
        # J-7 (fenêtre 0<delta<=7) : pré-rappel, une fois.
        elif 0 < delta <= PRE_DAYS and not sub.get("notif_pre_sent"):
            _notify_mongazi(sub, due, "pre")
            _send_client_email(sub, due, "pre")
            _send_client_whatsapp(sub, due, "pre")
            _mark_sent(sub["id"], "pre")
            sent["pre"] += 1
    if sent["pre"] or sent["due"]:
        log.info("nebula reminders: %s", sent)
    return sent


def _mark_sent(sub_id: str, stage: str) -> None:
    field = "notif_due_sent" if stage == "due" else "notif_pre_sent"
    try:
        _db().table("nebula_abonnements").update({field: True}).eq("id", sub_id).execute()
    except Exception:  # noqa: BLE001
        log.warning("maj drapeau rappel échoué", exc_info=True)
