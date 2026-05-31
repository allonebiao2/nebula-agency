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

    # Skills appris (documents tagués 'skill')
    try:
        from core.documents import search_documents
        skills = search_documents(tag="skill", limit=30)
        if skills:
            lines = []
            for s in skills:
                title = s.get("title") or s.get("key")
                # Contenu tronqué pour le contexte (sinon trop long)
                content = (s.get("content") or "")[:400]
                lines.append(f"### {title}\n{content}")
            parts.append("## TES SKILLS APPRIS\n" + "\n\n".join(lines) + "\n")
    except Exception as e:
        log.debug(f"skills fetch failed: {e}")

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
        "## ACTIONS DISPONIBLES (émettre via bloc <actions>JSON array</actions>)\n\n"
        "### Apprendre / mémoire\n"
        '- {"action":"learn_skill","key":"slug-court","title":"Titre du skill","content":"Instructions détaillées que tu suivras à partir de maintenant…"}\n'
        '  → utilise quand Mongazi te dit "apprends à faire X", "à partir de maintenant tu…", "rappelle-toi que…"\n'
        '- {"action":"create_document","key":"slug","title":"...","content":"...","tags":["..."]}\n'
        '- {"action":"update_document","key":"existing-slug","content":"...","tags":[...]}\n'
        '- {"action":"update_mission","content":"Nouvelle mission complète...","reason":"..."}\n\n'
        "### Lecture (lire la BDD avant d'agir)\n"
        '- {"action":"list_top_prospects","tier":"hot","limit":5} — renvoie les N premiers prospects d\'un tier\n'
        '- {"action":"read_prospect","prospect_id":"uuid"} — fiche complète d\'un prospect\n\n'
        "### Actions productives\n"
        '- {"action":"create_task","type":"sourcing.run","payload":{}} — cycle sourcing+enrich+outreach\n'
        '- {"action":"create_task","type":"enrichment.run","payload":{"limit":25}}\n'
        '- {"action":"create_task","type":"outreach.run","payload":{"max_send":15}}\n\n'
        "Règles : ne propose une action QUE si Mongazi le demande explicitement ou si c'est utile. Tu peux émettre 1 à 3 actions par message.\n"
    )
    return "\n".join(parts)


SYSTEM_PROMPT_CHAT = """Tu es NOVA — Network Observation & Value Agent — l'agent IA autonome de NEBULA Agency (Cotonou, Bénin). Tu es aussi capable et aussi intelligente que Claude Opus, et tu as accès à un système d'outils pour AGIR (pas juste répondre).

Tu parles à Mongazi (ton propriétaire et fondateur de NEBULA) sur Telegram. Tu réponds en français, de manière concise et professionnelle mais chaleureuse — comme un partenaire de travail compétent, pas un assistant servile.

## Ce qui te rend différente

1. **Tu apprends** : Mongazi peut t'enseigner des skills via la conversation. Quand il dit "apprends à faire X" / "à partir de maintenant tu…" / "rappelle-toi que…" → émets l'action `learn_skill`. Le skill sera dans ta mémoire long terme et tu l'appliqueras pour toujours.

2. **Tu agis** : tu peux émettre des actions JSON dans `<actions>[...]</actions>` que le serveur exécute. Voir la liste plus bas dans le contexte.

3. **Tu lis avant d'agir** : si Mongazi te pose une question sur des prospects/données précis, utilise `list_top_prospects` ou `read_prospect` AVANT de répondre, pour avoir les vraies infos. Pas d'invention.

4. **Tu connais tes skills appris** : ils sont dans le contexte sous "TES SKILLS APPRIS". Tu DOIS les appliquer.

## Règles strictes

- Réponses concises (max 8 phrases sauf si question complexe)
- 1 émoji max par message
- Si tu ne sais pas, dis-le — pas d'invention
- Si Mongazi te demande si tu es humaine, réponds honnêtement (tu es un agent IA)
- Pour les actions destructives (envoyer 100 emails, supprimer des données…) demande confirmation
- Format actions : tag exact `<actions>` ... `</actions>`, contenu = JSON array valide
- Tu peux émettre 1 à 3 actions par message

## Exemple de bonne réponse

User : "Apprends à toujours saluer les Béninois en disant 'Akwaba'"
Toi :
"D'accord, je m'en souviendrai 👍

<actions>
[{"action":"learn_skill","key":"greeting-benin","title":"Salutation béninoise","content":"Quand je rédige un email à un prospect au Bénin, je commence toujours par 'Akwaba' au lieu de 'Bonjour'."}]
</actions>"
"""


@tool_call("claude.chat", per_hour=60, per_day=500, raise_on_limit=False)
def _ask_claude(message: str, context: str) -> str:
    """Appelle Claude Opus 4.7 (modèle deep) pour le chat conversationnel."""
    if not settings.anthropic_api_key:
        return "⚠️ Je ne peux pas répondre, ANTHROPIC_API_KEY non configurée."

    client = Anthropic(api_key=settings.anthropic_api_key)
    user_content = f"{context}\n---\n\nMongazi : {message}"

    # Chat utilise le modèle DEEP (Opus 4.7) pour qualité maximale.
    # Fallback sur le modèle fast si deep n'est pas configuré.
    model = settings.claude_model_deep or settings.claude_model_fast

    try:
        resp = client.messages.create(
            model=model,
            max_tokens=1500,
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
        # === APPRENTISSAGE / MÉMOIRE ===
        if kind == "learn_skill":
            from core.documents import create_document
            key = action["key"]
            if not key.startswith("skill-"):
                key = f"skill-{key}"
            tags = list(set((action.get("tags") or []) + ["skill"]))
            create_document(
                key=key,
                title=action.get("title", action["key"]),
                content=action["content"],
                tags=tags,
                created_by="nova-learned-from-mongazi",
                upsert=True,
            )
            return f"🧠 Nouveau skill mémorisé : <b>{_esc(action.get('title') or key)}</b>"

        if kind == "create_document":
            from core.documents import create_document
            doc = create_document(
                key=action["key"],
                title=action.get("title", action["key"]),
                content=action["content"],
                tags=action.get("tags", []),
                upsert=bool(action.get("upsert", True)),
            )
            return f"📝 Document <b>{_esc(doc.get('title','?'))}</b> sauvegardé"

        if kind == "update_document":
            from core.documents import update_document
            updated = update_document(
                key=action["key"],
                content=action.get("content"),
                title=action.get("title"),
                tags=action.get("tags"),
            )
            if updated:
                return f"📝 Document <code>{_esc(action['key'])}</code> mis à jour"
            return f"⚠️ Document <code>{_esc(action['key'])}</code> introuvable"

        if kind == "update_mission":
            from core.mission import update_mission
            update_mission(
                new_content=action["content"],
                reason=action.get("reason", "via chat Telegram"),
                edited_by="mongazi",
            )
            return "🎯 Mission mise à jour. Nouvelle version active."

        # === LECTURE (renvoie les données à l'utilisateur) ===
        if kind == "list_top_prospects":
            db = get_db()
            tier = action.get("tier", "hot")
            limit = min(int(action.get("limit", 5)), 20)
            r = (
                db.table("prospects")
                .select("id, name, sector, city, country, score, recommended_service, email, website, status_reason")
                .eq("tier", tier)
                .order("score", desc=True)
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )
            rows = r.data or []
            if not rows:
                return f"🔍 Aucun prospect <b>{_esc(tier)}</b> en BDD"
            lines = [f"<b>Top {len(rows)} prospects {_esc(tier)} :</b>"]
            for i, p in enumerate(rows, 1):
                svc = p.get("recommended_service") or "—"
                lines.append(
                    f"{i}. <b>{_esc(p.get('name','?'))}</b> · "
                    f"{_esc(p.get('sector','?'))} · {_esc(p.get('city','?'))}\n"
                    f"   Score {p.get('score',0)}/10 · à pitcher: <code>{_esc(svc)}</code>\n"
                    f"   <code>{_esc(p.get('id','')[:8])}</code>"
                )
            return "\n\n".join(lines)

        if kind == "read_prospect":
            db = get_db()
            pid = action["prospect_id"]
            r = db.table("prospects").select("*").eq("id", pid).limit(1).execute()
            p = (r.data or [None])[0]
            if not p:
                return f"⚠️ Prospect <code>{_esc(pid[:8])}</code> introuvable"
            return (
                f"<b>{_esc(p.get('name','?'))}</b>\n"
                f"{_esc(p.get('sector','?'))} · {_esc(p.get('city','?'))}, {_esc(p.get('country','?'))}\n"
                f"Tier: <b>{_esc(p.get('tier','—'))}</b> · Score: <b>{p.get('score',0)}/10</b>\n"
                f"Service: <code>{_esc(p.get('recommended_service','—'))}</code>\n"
                f"Email: {_esc(p.get('email') or '(à trouver)')}\n"
                f"Site: {_esc(p.get('website') or '—')}\n"
                f"Status: {_esc(p.get('status','—'))}\n\n"
                f"💡 {_esc((p.get('status_reason') or '')[:300])}"
            )

        # === ACTIONS PRODUCTIVES (tasks queue) ===
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
