"""Notifications Telegram pour Mongazi.

NOVA utilise ce module pour pinger Mongazi quand :
- 👑 Un prospect est PRÊT À PAYER (alerte immédiate)
- 🔥 Un lead chaud répond avec intérêt
- 📊 Rapport quotidien (chaque soir)
- 📈 Bilan hebdomadaire (chaque dimanche)
- ⚠️ Erreur critique (NOVA bloquée)

Toutes les alertes sont aussi loggées dans la table `alerts` Supabase
pour traçabilité.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from db.client import get_db

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


# ---------------------------------------------------------------------------
# Bas niveau : envoi brut
# ---------------------------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def _post(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings.require("telegram_bot_token", "telegram_chat_id_mongazi")
    url = TELEGRAM_API.format(token=settings.telegram_bot_token, method=method)
    resp = httpx.post(url, json=payload, timeout=15.0)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram error: {data}")
    return data


def send_message(
    text: str,
    *,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    silent: bool = False,
) -> dict[str, Any] | None:
    """Envoie un message brut sur Telegram à Mongazi."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id_mongazi:
        logger.warning("Telegram pas configuré, message ignoré")
        return None
    try:
        return _post("sendMessage", {
            "chat_id": settings.telegram_chat_id_mongazi,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": silent,
        })
    except Exception as e:
        logger.error("Telegram send_message failed: %s", e)
        return None


def _log_alert(alert_type: str, payload: dict[str, Any], message_id: str | None) -> None:
    try:
        get_db().table("alerts").insert({
            "type": alert_type,
            "channel": "telegram",
            "payload": payload,
            "delivered": message_id is not None,
            "provider_message_id": message_id,
            "sent_at": "now()" if message_id else None,
        }).execute()
    except Exception as e:
        logger.warning("alert log failed: %s", e)


# ---------------------------------------------------------------------------
# Haut niveau : notifications typées
# ---------------------------------------------------------------------------
def notify_bootup() -> bool:
    """Message de test : NOVA est en ligne."""
    text = (
        "🌌 <b>NOVA en ligne.</b>\n\n"
        "Je suis prête à travailler pour toi, Mongazi.\n"
        f"<i>Version {settings.claude_model_fast}</i>\n\n"
        "Je te contacterai quand :\n"
        "• Un prospect veut signer ✨\n"
        "• Un lead chaud répond 🔥\n"
        "• Le bilan du jour est prêt 📊\n"
        "• Une chose critique arrive ⚠️"
    )
    r = send_message(text)
    _log_alert("ready_to_pay", {"test": True}, r.get("result", {}).get("message_id") if r else None)
    return r is not None


def notify_ready_to_pay(
    prospect_name: str,
    *,
    prospect_id: str | None = None,
    summary: str | None = None,
    suggested_quote: str | None = None,
    last_message: str | None = None,
) -> bool:
    """🚨 ALERTE MAX : un prospect est prêt à signer."""
    parts = [
        f"👑 <b>PROSPECT PRÊT À PAYER</b>",
        f"",
        f"<b>{_esc(prospect_name)}</b>",
    ]
    if summary:
        parts += ["", f"<i>{_esc(summary)}</i>"]
    if last_message:
        parts += ["", f"<b>Dernier message :</b>", f"<blockquote>{_esc(last_message)}</blockquote>"]
    if suggested_quote:
        parts += ["", f"<b>Devis suggéré :</b> {_esc(suggested_quote)}"]
    parts += ["", "👉 <b>Action requise : prends la main maintenant.</b>"]

    text = "\n".join(parts)
    r = send_message(text, silent=False)
    _log_alert("ready_to_pay", {
        "prospect_id": prospect_id,
        "prospect_name": prospect_name,
        "summary": summary,
    }, r.get("result", {}).get("message_id") if r else None)
    return r is not None


def notify_hot_lead(
    prospect_name: str,
    *,
    prospect_id: str | None = None,
    snippet: str | None = None,
) -> bool:
    """🔥 Lead chaud : a répondu positivement."""
    default_snippet = "A répondu avec intérêt à mon email."
    body = _esc(snippet) if snippet else default_snippet
    text = f"🔥 <b>Lead chaud :</b> {_esc(prospect_name)}\n\n{body}"
    r = send_message(text)
    _log_alert("hot_lead", {"prospect_id": prospect_id, "prospect_name": prospect_name},
               r.get("result", {}).get("message_id") if r else None)
    return r is not None


def notify_daily_report(
    *,
    prospects_found: int = 0,
    emails_sent: int = 0,
    replies: int = 0,
    hot_leads: int = 0,
    ready_to_pay: int = 0,
) -> bool:
    """📊 Rapport quotidien envoyé chaque soir."""
    text = (
        "📊 <b>Bilan du jour</b>\n\n"
        f"🔭 Prospects trouvés : <b>{prospects_found}</b>\n"
        f"✉️ Emails envoyés : <b>{emails_sent}</b>\n"
        f"📩 Réponses reçues : <b>{replies}</b>\n"
        f"🔥 Leads chauds : <b>{hot_leads}</b>\n"
        f"👑 Prêts à payer : <b>{ready_to_pay}</b>\n\n"
        f"<i>Je continue demain. Bonne nuit Mongazi 🌌</i>"
    )
    r = send_message(text, silent=True)
    _log_alert("weekly_report" if False else "sourcing_report",
               {"prospects": prospects_found, "emails": emails_sent, "replies": replies},
               r.get("result", {}).get("message_id") if r else None)
    return r is not None


def notify_weekly_report(
    *,
    week_stats: dict[str, Any] | None = None,
    learning_summary: str | None = None,
) -> bool:
    """📈 Bilan hebdomadaire avec auto-amélioration."""
    stats = week_stats or {}
    text_parts = [
        "📈 <b>Bilan de la semaine</b>",
        "",
        f"🔭 Prospects trouvés : <b>{stats.get('prospects', 0)}</b>",
        f"✉️ Emails envoyés : <b>{stats.get('emails', 0)}</b>",
        f"📩 Taux de réponse : <b>{stats.get('reply_rate', 0):.1%}</b>",
        f"👑 Prêts à signer : <b>{stats.get('ready', 0)}</b>",
        f"💼 Conversions estimées : <b>{stats.get('conversions', 0)}</b>",
    ]
    if learning_summary:
        text_parts += ["", "🧠 <b>Mon apprentissage cette semaine :</b>",
                       f"<i>{_esc(learning_summary)}</i>"]
    text_parts += ["", "<i>Je m'améliore. La semaine prochaine sera meilleure.</i>"]

    r = send_message("\n".join(text_parts), silent=True)
    _log_alert("weekly_report", stats, r.get("result", {}).get("message_id") if r else None)
    return r is not None


def notify_error(title: str, description: str | None = None) -> bool:
    """⚠️ Erreur critique : NOVA est bloquée."""
    text = f"⚠️ <b>Problème NOVA</b>\n\n<b>{_esc(title)}</b>"
    if description:
        text += f"\n\n<code>{_esc(description[:500])}</code>"
    text += "\n\n<i>J'ai besoin de toi pour débloquer la situation.</i>"
    r = send_message(text)
    _log_alert("error", {"title": title, "description": description},
               r.get("result", {}).get("message_id") if r else None)
    return r is not None


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------
def _esc(s: str | None) -> str:
    """Escape HTML pour Telegram parse_mode=HTML."""
    if not s:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))
