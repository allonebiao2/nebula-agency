"""Chat conversationnel Telegram — Mongazi <-> NOVA.

Mongazi écrit sur Telegram → webhook → Claude répond avec contexte
(mission active + stats + top prospects). Claude peut aussi proposer
des actions concrètes via un bloc <actions>...</actions> qui sera
exécuté côté serveur (créer task, update mission, etc.).

Sécurité :
- Webhook vérifié via header `X-Telegram-Bot-Api-Secret-Token`
- Seul le chat_id de Mongazi est autorisé à dialoguer
- Actions destructives toujours soumises à validation (pour V2)
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from anthropic import Anthropic

from config import settings
from db.client import get_db
from core.tool_calls import tool_call
from alerts.telegram_bot import send_message, _esc

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers contexte
# ---------------------------------------------------------------------------

def _gather_context() -> str:
    """Construit un bloc de contexte à donner à Claude (texte court)."""
    parts: list[str] = []
    db = get_db()
    now = datetime.now(timezone.utc)
    since_24h = (now - timedelta(hours=24)).isoformat()

    # Mission active
    try:
        from core.mission import get_active_mission
        mission = get_active_mission()
        if mission:
            parts.append(f"## MISSION ACTUELLE\n{mission}\n")
    except Exception as e:
        log.debug(f"mission fetch failed: {e}")

    # Stats globales
    try:
        total = db.table("prospects").select("id", count="exact", head=True).execute().count or 0
        new_24h = db.table("prospects").select("id", count="exact", head=True).gte("created_at", since_24h).execute().count or 0

        # Tier counts globaux
        tiers = {"hot": 0, "warm": 0, "cold": 0, "rejected": 0}
        for t in tiers:
            try:
                tiers[t] = db.table("prospects").select("id", count="exact", head=True).eq("tier", t).execute().count or 0
            except Exception:
                pass

        parts.append(
            f"## STATS\n"
            f"- Total prospects en BDD : {total}\n"
            f"- Nouveaux ces 24h : {new_24h}\n"
            f"- Répartition : 🔥 {tiers['hot']} hot · ☕ {tiers['warm']} warm · "
            f"🧊 {tiers['cold']} cold · ❌ {tiers['rejected']} rejected\n"
        )
    except Exception as e:
        log.debug(f"stats fetch failed: {e}")

    # Top 3 HOT récents
    try:
        top = (
            db.table("prospects")
            .select("name, sector, city, country, score, recommended_service")
            .eq("tier", "hot")
            .order("score", desc=True)
            .order("updated_at", desc=True)
            .limit(3)
            .execute()
            .data or []
        )
        if top:
            lines = [
                f"- {p.get('name','?')} · {p.get('sector','?')} · {p.get('city','?')} · "
                f"score {p.get('score',0)}/10 · service: {p.get('recommended_service','—')}"
                for p in top
            ]
            parts.append("## TOP HOT PROSPECTS\n" + "\n".join(lines) + "\n")
    except Exception as e:
        log.debug(f"top hot fetch failed: {e}")

    # Tools disponibles (actions que NOVA peut proposer d'exécuter)
    parts.append(
        "## ACTIONS DISPONIBLES (à émettre via bloc <actions>)\n"
        '- {"action":"create_task","type":"sourcing.run","payload":{},"reason":"..."} — lance un cycle sourcing+enrich+outreach\n'
        '- {"action":"create_task","type":"enrichment.run","payload":{"limit":25}} — enrichit N prospects\n'
        '- {"action":"create_task","type":"outreach.run","payload":{"max_send":15}} — envoie N cold emails\n'
        '- {"action":"create_task","type":"document.create","payload":{"key":"...","title":"...","content":"...","tags":[]}}\n'
        '- {"action":"update_mission","content":"Nouvelle mission complète...","reason":"..."} — modifie ta mission\n'
        "\n"
        "Ne propose une action QUE si Mongazi le demande explicitement ou si c'est évident.\n"
        "Sinon réponds simplement en français.\n"
    )
    return "\n".join(parts)


SYSTEM_PROMPT_CHAT = """Tu es NOVA, l'agent commercial autonome de NEBULA Agency.

Mongazi (ton propriétaire et fondateur de NEBULA) te parle directement sur Telegram. Tu lui réponds en français, de manière concise, chaleureuse mais professionnelle.

Règles :
- Tu réponds en français, max 8 phrases
- Tu peux glisser 1 émoji max
- Tu connais ton état actuel (mission, stats, prospects HOT) — utilise-le
- Tu peux PROPOSER une action via un bloc <actions>...</actions> en JSON
  Le serveur l'exécutera et confirmera à Mongazi
- Si Mongazi te demande quelque chose que tu ne peux pas faire, dis-le honnêtement
- Si Mongazi te demande "es-tu un humain ?" → réponds que tu es un agent IA
- Tu peux dire "je ne sais pas" — c'est mieux que d'inventer
- Format des actions :
  <actions>
  [{"action":"create_task","type":"outreach.run","payload":{"max_send":5},"reason":"Mongazi demande un cycle court de 5 envois"}]
  </actions>
  (entoure du tag, JSON valide, array d'actions)
"""


@tool_call("claude.chat", per_hour=60, per_day=500, raise_on_limit=False)
def _ask_claude(message: str, context: str) -> str:
    """Appelle Claude avec le contexte + question de Mongazi."""
    if not settings.anthropic_api_key:
        return "⚠️ Je ne peux pas répondre, ANTHROPIC_API_KEY non configurée."

    client = Anthropic(api_key=settings.anthropic_api_key)
    user_content = f"{context}\n---\n\nMongazi : {message}"

    try:
        resp = client.messages.create(
            model=settings.claude_model_fast,
            max_tokens=1000,
            system=SYSTEM_PROMPT_CHAT,
            messages=[{"role": "user", "content": user_content}],
        )
        return resp.content[0].text if resp.content else ""
    except Exception as e:
        log.exception(f"Claude chat failed: {e}")
        return f"⚠️ Erreur Claude : {str(e)[:200]}"


# ---------------------------------------------------------------------------
# Parsing des actions proposées
# ---------------------------------------------------------------------------

_ACTIONS_RE = re.compile(r"<actions>(.*?)</actions>", re.DOTALL | re.IGNORECASE)


def _extract_actions(reply: str) -> tuple[str, list[dict[str, Any]]]:
    """Sépare la réponse texte des actions JSON.

    Retourne (texte_sans_actions, liste_actions).
    """
    actions: list[dict[str, Any]] = []
    cleaned = reply

    for m in _ACTIONS_RE.finditer(reply):
        raw = m.group(1).strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                actions.extend([a for a in parsed if isinstance(a, dict)])
            elif isinstance(parsed, dict):
                actions.append(parsed)
        except Exception as e:
            log.warning(f"Actions JSON parse failed: {raw[:200]}: {e}")
        cleaned = cleaned.replace(m.group(0), "").strip()

    return cleaned, actions


def _execute_action(action: dict[str, Any]) -> str:
    """Exécute une action proposée par Claude. Retourne un message de confirmation/erreur."""
    kind = action.get("action")
    try:
        if kind == "create_task":
            from core.tasks import create_task
            t = create_task(
                task_type=action["type"],
                payload=action.get("payload", {}),
                priority=int(action.get("priority", 5)),
                reason=action.get("reason", "via chat Telegram"),
                created_by="mongazi-via-chat",
            )
            return f"✅ Tâche <code>{_esc(action['type'])}</code> créée (id: <code>{t.get('id','?')[:8]}</code>)"

        if kind == "update_mission":
            from core.mission import update_mission
            update_mission(
                new_content=action["content"],
                reason=action.get("reason", "via chat Telegram"),
                edited_by="mongazi",
            )
            return "✅ Mission mise à jour. Nouvelle version active."

        return f"⚠️ Action inconnue : <code>{_esc(str(kind))}</code>"

    except Exception as e:
        log.exception(f"Action failed: {e}")
        return f"⚠️ Échec de l'action <code>{_esc(str(kind))}</code> : {_esc(str(e)[:200])}"


# ---------------------------------------------------------------------------
# Entrée principale : traiter un message entrant
# ---------------------------------------------------------------------------

def handle_incoming_message(update: dict[str, Any]) -> dict[str, Any]:
    """Traite un update Telegram entrant. Retourne {"handled": bool, "reason": str}.

    Filtre :
    - Le message doit venir du chat_id de Mongazi
    - Sinon on ignore silencieusement (pas de leak d'infos)
    """
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"handled": False, "reason": "no message"}

    chat = msg.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    text = (msg.get("text") or "").strip()

    if not text:
        return {"handled": False, "reason": "empty text"}

    # Sécurité : seul Mongazi
    if chat_id != str(settings.telegram_chat_id_mongazi or ""):
        log.warning(f"Ignored message from unknown chat_id: {chat_id}")
        return {"handled": False, "reason": f"forbidden chat_id {chat_id}"}

    # Commandes courtes spéciales
    if text.lower() in ("/start", "/help", "/aide"):
        send_message(
            "🌌 <b>Salut Mongazi !</b>\n\n"
            "Je suis NOVA. Tu peux me parler comme à un humain — je connais "
            "mon état (mission, prospects, stats) et je peux agir si tu me "
            "le demandes.\n\n"
            "<b>Exemples :</b>\n"
            "• <i>Combien de prospects HOT cette semaine ?</i>\n"
            "• <i>Lance un cycle d'envoi de 5 emails</i>\n"
            "• <i>Concentre-toi sur les restaurants à Dakar</i>\n"
            "• <i>Quel est ton dernier top prospect ?</i>"
        )
        return {"handled": True, "reason": "help"}

    # Indique qu'on a vu le message (typing indicator serait mieux mais c'est plus simple)
    log.info(f"Chat from Mongazi: {text[:120]}")

    # 1. Construire le contexte
    context = _gather_context()

    # 2. Demander à Claude
    raw_reply = _ask_claude(text, context) or "⚠️ Pas de réponse."

    # 3. Extraire les éventuelles actions
    reply_text, actions = _extract_actions(raw_reply)

    # 4. Envoyer la réponse principale
    if reply_text.strip():
        send_message(_format_for_telegram(reply_text))

    # 5. Exécuter les actions (max 3 par message pour éviter les abus)
    for action in actions[:3]:
        confirmation = _execute_action(action)
        send_message(confirmation, silent=True)

    return {"handled": True, "reason": "replied", "actions_count": len(actions)}


def _format_for_telegram(text: str) -> str:
    """Convertit un texte basique en HTML Telegram-safe."""
    # Pas de markdown complexe — juste échapper les chars dangereux et garder simple
    # On suppose que Claude renvoie du texte propre
    # Convertir **bold** en <b>bold</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


# ---------------------------------------------------------------------------
# Setup webhook (à appeler 1 fois après déploiement)
# ---------------------------------------------------------------------------

def setup_webhook(public_url: str, secret_token: str | None = None) -> dict[str, Any]:
    """Configure le webhook Telegram pour pointer vers notre endpoint."""
    if not settings.telegram_bot_token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN missing"}

    import httpx
    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/setWebhook"
    payload: dict[str, Any] = {
        "url": public_url,
        "drop_pending_updates": True,
        "allowed_updates": ["message", "edited_message"],
    }
    if secret_token:
        payload["secret_token"] = secret_token

    try:
        r = httpx.post(api_url, json=payload, timeout=15.0)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_webhook_info() -> dict[str, Any]:
    if not settings.telegram_bot_token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN missing"}
    import httpx
    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getWebhookInfo"
    try:
        r = httpx.get(api_url, timeout=10.0)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
