"""Weekly self-improvement loop — NOVA s'auto-améliore chaque dimanche soir.

Étapes :
1. Récupère les 7 derniers jours d'événements :
   - Emails envoyés (conversations out)
   - Réponses reçues (conversations in avec detected_intent)
   - Prospects scorés (par tier)
   - Erreurs / tool_calls failed
2. Calcule des stats : taux de réponse, taux conversion, intents distribution,
   templates qui marchent, ceux qui ne marchent pas.
3. Envoie tout ça à Claude Opus 4.7 avec une demande : "Que peux-tu apprendre
   de cette semaine ? Quelles règles tu te donnes pour la prochaine ?"
4. Claude produit un JSON :
   - learnings: list de phrases courtes
   - new_skills: list de skills à créer (key, title, content)
   - mission_update: bool + new content si refonte nécessaire
   - summary: 1 paragraphe pour Mongazi
5. Le code applique les actions (create_document, update_mission)
6. Notifie Mongazi sur Telegram avec le summary
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from anthropic import Anthropic

from config import settings
from core.tool_calls import tool_call
from db.client import get_db

log = logging.getLogger(__name__)


def _gather_week_stats() -> dict[str, Any]:
    """Agrège les stats de la dernière semaine."""
    db = get_db()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    # Emails envoyés cette semaine
    sent = (db.table("conversations").select("id", count="exact", head=True)
            .eq("direction", "out").eq("channel", "email").gte("sent_at", since)
            .execute().count or 0)

    # Réponses reçues
    received = (db.table("conversations").select("id, detected_intent, sentiment")
                .eq("direction", "in").gte("created_at", since).execute().data or [])

    # Distribution des intents
    intents: dict[str, int] = {}
    for r in received:
        i = r.get("detected_intent") or "unknown"
        intents[i] = intents.get(i, 0) + 1

    # Prospects scorés cette semaine
    prospects = (db.table("prospects").select("tier")
                 .gte("updated_at", since).not_.is_("tier", "null")
                 .execute().data or [])
    tiers: dict[str, int] = {"hot": 0, "warm": 0, "cold": 0, "rejected": 0}
    for p in prospects:
        t = p.get("tier")
        if t in tiers:
            tiers[t] += 1

    # Tool calls failed (signal qualité)
    failed_calls = (db.table("tool_calls").select("tool_name, output_summary")
                    .eq("status", "failed").gte("created_at", since)
                    .limit(20).execute().data or [])

    # Conversations qui ont mené à ready_to_pay (succès)
    won = (db.table("conversations").select("subject, body, summary")
           .eq("direction", "in").eq("detected_intent", "ready_to_pay")
           .gte("created_at", since).limit(10).execute().data or [])

    # Conversations not_interested (échec)
    lost = (db.table("conversations").select("subject, body, summary")
            .eq("direction", "in").eq("detected_intent", "not_interested")
            .gte("created_at", since).limit(10).execute().data or [])

    return {
        "period": "7 derniers jours",
        "sent": sent,
        "received_total": len(received),
        "intents_distribution": intents,
        "prospects_scored": tiers,
        "failed_tool_calls": len(failed_calls),
        "failed_samples": failed_calls[:5],
        "won_conversations": won,
        "lost_conversations": lost,
        "reply_rate_percent": round(len(received) / max(sent, 1) * 100, 1),
        "conversion_rate_percent": round(intents.get("ready_to_pay", 0) / max(sent, 1) * 100, 1),
    }


def _get_current_mission() -> str:
    try:
        from core.mission import get_active_mission
        return get_active_mission()
    except Exception:
        return ""


def _get_existing_skills() -> list[dict[str, Any]]:
    try:
        from core.documents import search_documents
        return search_documents(tag="skill", limit=30)
    except Exception:
        return []


LEARNER_PROMPT = """Tu es NOVA, agent commercial autonome de NEBULA Agency. Chaque dimanche soir, tu fais ton introspection hebdomadaire pour t'améliorer.

## Ta mission actuelle
{current_mission}

## Tes skills déjà appris ({n_skills})
{skills_summary}

## Tes statistiques de la semaine
{stats}

## Échantillons de conversations
### Prospects qui ont voulu acheter (ready_to_pay)
{won}

### Prospects qui ont dit non
{lost}

---

**Analyse honnêtement** ce qui a marché et ce qui n'a pas marché cette semaine. Identifie des **patterns concrets** (pas de banalités).

**Pour la semaine prochaine, propose** :
1. **3 à 5 apprentissages** courts (1 phrase chacun) — ce que tu retiens
2. **1 à 3 nouveaux skills** à créer dans ta mémoire long terme (avec key/title/content détaillé)
3. **Mise à jour de la mission ?** Seulement si vraiment nécessaire (pivot stratégique, nouvelle directive critique)
4. **1 summary** pour Mongazi (3-4 phrases max) : ce qui s'est passé + ce que tu vas changer

**Réponds en JSON STRICT** (aucun markdown, aucun texte avant/après) :
{{
  "learnings": ["phrase 1", "phrase 2", ...],
  "new_skills": [
    {{"key": "skill-slug-court", "title": "Titre lisible", "content": "Instructions détaillées multi-lignes que tu suivras dorénavant. Sois précise, donne des exemples."}}
  ],
  "mission_update_needed": false,
  "mission_new_content": null,
  "summary_for_mongazi": "Cette semaine j'ai... Ce qui marche : ... Ce qui ne marche pas : ... La semaine prochaine je vais changer X et Y."
}}"""


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1] if "```" in t[3:] else t[3:]
        if t.lower().startswith("json"):
            t = t[4:]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


@tool_call("claude.weekly_learn", per_hour=10, per_day=10, raise_on_limit=False)
def _ask_claude_to_reflect(stats: dict, mission: str, skills: list[dict]) -> dict[str, Any]:
    if not settings.anthropic_api_key:
        return {"error": "ANTHROPIC_API_KEY missing"}

    client = Anthropic(api_key=settings.anthropic_api_key)
    skills_summary = "\n".join(
        f"- {s.get('key')}: {(s.get('title') or '')}" for s in skills
    ) or "(aucun)"

    won_text = "\n".join(
        f"- {(c.get('summary') or c.get('subject') or '')[:200]}"
        for c in stats.get("won_conversations", [])
    ) or "(aucune cette semaine)"

    lost_text = "\n".join(
        f"- {(c.get('summary') or c.get('subject') or '')[:200]}"
        for c in stats.get("lost_conversations", [])
    ) or "(aucune cette semaine)"

    prompt = LEARNER_PROMPT.format(
        current_mission=mission[:2000],
        n_skills=len(skills),
        skills_summary=skills_summary,
        stats=json.dumps(
            {k: v for k, v in stats.items() if k not in ("won_conversations", "lost_conversations", "failed_samples")},
            indent=2, ensure_ascii=False,
        ),
        won=won_text,
        lost=lost_text,
    )

    model = settings.claude_model_deep or settings.claude_model_fast
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text if resp.content else ""
        cleaned = _strip_code_fence(raw)
        return json.loads(cleaned)
    except Exception as e:
        log.exception(f"weekly reflection failed: {e}")
        return {"error": str(e)[:300]}


def _apply_learnings(reflection: dict[str, Any]) -> dict[str, int]:
    """Applique les actions issues de la réflexion : crée docs, update mission."""
    applied = {"docs_created": 0, "skills_created": 0, "mission_updated": 0}

    # 1. Document principal des learnings de la semaine
    try:
        from core.documents import create_document
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        learnings_md = "\n".join(f"- {l}" for l in reflection.get("learnings", []))
        create_document(
            key=f"weekly-learnings-{timestamp}",
            title=f"Apprentissages hebdo — {timestamp}",
            content=(
                f"## Résumé\n\n{reflection.get('summary_for_mongazi', '')}\n\n"
                f"## Learnings\n\n{learnings_md or '(aucun)'}"
            ),
            tags=["learning", "weekly", timestamp[:7]],
            created_by="nova-weekly-learner",
            upsert=True,
        )
        applied["docs_created"] = 1
    except Exception as e:
        log.warning(f"weekly doc creation failed: {e}")

    # 2. Nouveaux skills
    try:
        from core.documents import create_document
        for sk in reflection.get("new_skills", []):
            try:
                key = sk["key"]
                if not key.startswith("skill-"):
                    key = f"skill-{key}"
                create_document(
                    key=key,
                    title=sk.get("title", key),
                    content=sk["content"],
                    tags=["skill", "auto-learned"],
                    created_by="nova-weekly-learner",
                    upsert=True,
                )
                applied["skills_created"] += 1
            except Exception as e:
                log.warning(f"skill creation failed for {sk.get('key')}: {e}")
    except Exception as e:
        log.warning(f"skills loop failed: {e}")

    # 3. Mission update si proposée
    if reflection.get("mission_update_needed") and reflection.get("mission_new_content"):
        try:
            from core.mission import update_mission
            update_mission(
                new_content=reflection["mission_new_content"],
                reason="Auto-amélioration hebdo NOVA",
                edited_by="nova",
            )
            applied["mission_updated"] = 1
        except Exception as e:
            log.warning(f"mission update failed: {e}")

    return applied


def run_weekly_learning() -> dict[str, Any]:
    """Lance le cycle d'auto-amélioration hebdo. Retourne un dict avec tout le contexte."""
    log.info("[weekly-learner] début")
    stats = _gather_week_stats()
    mission = _get_current_mission()
    skills = _get_existing_skills()

    reflection = _ask_claude_to_reflect(stats, mission, skills)
    if "error" in reflection:
        log.warning(f"reflection failed: {reflection['error']}")
        return {"ok": False, "error": reflection["error"], "stats": stats}

    applied = _apply_learnings(reflection)

    # Notifier Mongazi sur Telegram
    try:
        from alerts.telegram_bot import send_message, _esc
        summary = reflection.get("summary_for_mongazi", "(pas de résumé)")
        text = (
            f"🧠 <b>Apprentissage hebdo NOVA</b>\n\n"
            f"📊 <b>Cette semaine :</b>\n"
            f"   • {stats['sent']} emails envoyés\n"
            f"   • {stats['received_total']} réponses reçues "
            f"(taux: {stats['reply_rate_percent']}%)\n"
            f"   • {stats['intents_distribution'].get('ready_to_pay', 0)} ready_to_pay\n"
            f"   • {stats['prospects_scored'].get('hot', 0)} hot · "
            f"{stats['prospects_scored'].get('warm', 0)} warm scorés\n\n"
            f"📝 <b>Résumé NOVA :</b>\n<i>{_esc(summary)}</i>\n\n"
            f"✅ <b>Actions appliquées :</b>\n"
            f"   • {applied['docs_created']} doc learnings créé\n"
            f"   • {applied['skills_created']} nouveaux skills créés\n"
            f"   • Mission {'mise à jour' if applied['mission_updated'] else 'inchangée'}\n\n"
            f"<i>Je continue à apprendre.</i> 🌌"
        )
        send_message(text)
    except Exception as e:
        log.warning(f"weekly notif failed: {e}")

    log.info(f"[weekly-learner] OK — {applied}")
    return {"ok": True, "stats": stats, "reflection": reflection, "applied": applied}
