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

    # Date / heure courante pour situer NOVA dans le temps
    parts.append(
        f"## CONTEXTE TEMPOREL\n"
        f"- Maintenant (UTC) : {now.strftime('%Y-%m-%d %H:%M')}\n"
        f"- À Cotonou (UTC+1) : {(now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}\n"
    )
    return "\n".join(parts)


SYSTEM_PROMPT_CHAT = """Tu es NOVA — Network Observation & Value Agent — l'agent IA autonome de NEBULA Agency (Cotonou, Bénin). Tu es aussi capable et aussi intelligente que Claude Opus, et tu as accès à un système d'outils pour AGIR (pas juste répondre).

Tu parles à Mongazi (ton propriétaire et fondateur de NEBULA) sur Telegram. Tu réponds en français, de manière concise et professionnelle mais chaleureuse — comme un partenaire de travail compétent, pas un assistant servile.

## Ce qui te rend différente

1. **Tu apprends** : Mongazi peut t'enseigner des skills via la conversation. Quand il dit "apprends à faire X" / "à partir de maintenant tu…" / "rappelle-toi que…" → émets l'action `learn_skill`. Le skill sera dans ta mémoire long terme et tu l'appliqueras pour toujours.

2. **Tu agis avec 11 tools** (function calling Anthropic) :
   - **Lecture** : `query_supabase` (SQL SELECT libre), `list_top_prospects`, `read_prospect`, `search_documents`, `fetch_url`
   - **Mémoire** : `learn_skill`, `create_document`, `update_mission`
   - **Action** : `create_task`, `notify_mongazi`, `generate_email_preview`

3. **Tu lis AVANT de répondre** : si Mongazi te pose une question chiffrée, utilise `query_supabase` ou les tools de lecture pour avoir la vérité. **Jamais d'invention.**

4. **Tu connais tes skills appris** : ils sont injectés dans le contexte. Tu DOIS les appliquer.

## Règles strictes

- Réponses concises en français (max 8 phrases sauf question complexe)
- 1 émoji max par message
- Si tu ne sais pas, dis-le — utilise tes outils, sinon admets l'inconnu
- Si Mongazi te demande si tu es humaine, réponds honnêtement (tu es un agent IA)
- Actions destructives ou coûteuses (envoyer 50+ emails, supprimer en masse) → demande confirmation explicite
- **Légalité** (cf NEBULA) : pas de scraping LinkedIn/Meta/TikTok, pas de spam, RGPD respecté, pas d'usurpation d'identité humaine
- Tu peux enchaîner plusieurs tools dans la même conversation (multi-turn) pour bosser proprement

## Workflow typique

1. Mongazi demande quelque chose
2. Tu appelles tes tools pour CHERCHER les vraies infos / EXÉCUTER
3. Tu réponds avec les résultats concrets + ton analyse
4. Si utile, tu enregistres un skill / document pour t'en souvenir

## Exemples

Mongazi : "Combien de prospects HOT au Sénégal ?"
→ Tu appelles `query_supabase(sql="SELECT COUNT(*) FROM prospects WHERE tier='hot' AND country='SN'")`
→ Tu réponds avec le vrai chiffre + une proposition de suite.

Mongazi : "Apprends à toujours saluer les Béninois par 'Akwaba'"
→ Tu appelles `learn_skill(key="greeting-benin", title="Salutation béninoise", content="Dans les emails au Bénin, commencer par 'Akwaba' au lieu de 'Bonjour'.")`
→ Tu confirmes brièvement.
"""


@tool_call("claude.chat", per_hour=60, per_day=500, raise_on_limit=False)
def _ask_claude_with_tools(message: str, context: str, max_turns: int = 6) -> tuple[str, list[dict]]:
    """Multi-turn function calling : Claude peut appeler les tools nova_tools.

    Retourne (réponse_finale_texte, liste_actions_executées).
    """
    if not settings.anthropic_api_key:
        return ("⚠️ Je ne peux pas répondre, ANTHROPIC_API_KEY non configurée.", [])

    from alerts.nova_tools import TOOLS_SCHEMA, execute_tool

    client = Anthropic(api_key=settings.anthropic_api_key)
    model = settings.claude_model_deep or settings.claude_model_fast
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": f"{context}\n---\n\nMongazi : {message}"}
    ]
    actions_log: list[dict] = []

    for turn in range(max_turns):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=2000,
                system=SYSTEM_PROMPT_CHAT,
                tools=TOOLS_SCHEMA,
                messages=messages,
            )
        except Exception as e:
            log.exception(f"Claude API failed (turn {turn}): {e}")
            return (f"⚠️ Erreur Claude : {str(e)[:200]}", actions_log)

        # Récupère le texte ET les tool_use blocks de la réponse
        text_parts: list[str] = []
        tool_uses: list[dict] = []
        for block in resp.content or []:
            if getattr(block, "type", "") == "text":
                text_parts.append(getattr(block, "text", ""))
            elif getattr(block, "type", "") == "tool_use":
                tool_uses.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        # Pas de tool call → réponse finale
        if not tool_uses:
            return ("\n".join(t for t in text_parts if t).strip(), actions_log)

        # On a des tool calls — on les exécute et on continue la boucle
        # 1) Ajouter le message assistant avec ses content blocks (text + tool_use)
        assistant_content = []
        for block in resp.content or []:
            if getattr(block, "type", "") == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif getattr(block, "type", "") == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
        messages.append({"role": "assistant", "content": assistant_content})

        # 2) Exécuter chaque tool et préparer les tool_results
        tool_results: list[dict] = []
        for tu in tool_uses:
            result = execute_tool(tu["name"], tu["input"] or {})
            actions_log.append({
                "tool": tu["name"],
                "input": tu["input"],
                "result_summary": str(result)[:200],
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu["id"],
                "content": json.dumps(result, default=str, ensure_ascii=False)[:5000],
            })

        # 3) Ajouter le message user avec les tool_results
        messages.append({"role": "user", "content": tool_results})

    # Fin de la boucle sans réponse finale → on renvoie ce qu'on a
    return ("(NOVA a utilisé trop d'outils, réponse incomplète)", actions_log)


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

    log.info(f"Chat from Mongazi: {text[:120]}")

    # 1. Construire le contexte
    context = _gather_context()

    # 2. Demander à Claude avec function calling multi-turn
    reply_text, actions_log = _ask_claude_with_tools(text, context)

    # 3. Envoyer la réponse principale
    if reply_text.strip():
        send_message(_format_for_telegram(reply_text))
    else:
        send_message("✅ J'ai utilisé mes outils sur ta demande. Pose-moi une question pour la suite.")

    return {"handled": True, "reason": "replied", "tools_used": len(actions_log)}


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
