"""Vendora Support — moteur de l'agent de SUPPORT client (2e pilier de Vendora).

Distinct du VENDEUR (`core/brain.py`, qui vend aux clients d'une boutique) : ici l'agent
répond aux UTILISATEURS d'un business (SaaS, vitrine, service) à partir de SA base de
connaissances, sur WhatsApp et sur son site (widget).

3 règles (cf. _specs/vendora-support-v1.md) :
1. GROUNDED — répond uniquement depuis la base de connaissances ; n'invente jamais.
2. ESCALADE-SI-DOUTE — hors base / plainte / problème non résolu → rassure + outil
   `escalader` (prévient le responsable avec le problème précis + le contact).
3. (La boucle d'amélioration — détection des récurrents + rapport — est gérée à part,
   par un job d'analyse, pas ici.)

Inerte tant qu'aucun client n'a `agent_role='support'` : ce module n'est appelé que par
le routage support (à brancher au lot 4). Aucun impact sur le Vendora actuel.
"""
from __future__ import annotations

import logging

import anthropic

from config import settings
from core import model_config, usage

log = logging.getLogger("boutique-ia.support_agent")

MAX_TOOL_TURNS = 3

ESCALATE_TOOL = {
    "name": "escalader",
    "description": (
        "Prévient le/la responsable du business qu'un utilisateur a besoin d'un humain. "
        "À appeler quand : la réponse n'est PAS dans la base de connaissances ; l'utilisateur "
        "est mécontent ou fait une réclamation ; il rencontre un problème que tu ne peux pas "
        "résoudre ; ou il redemande la même chose malgré ton explication. Après l'appel, "
        "rassure l'utilisateur (l'équipe revient vers lui très vite). N'invente JAMAIS une "
        "réponse pour éviter d'escalader."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "probleme": {"type": "string", "description": "Le problème précis de l'utilisateur, en 1 phrase."},
            "contact": {"type": "string", "description": "Contact de l'utilisateur (numéro / email) si connu."},
            "gravite": {"type": "string", "enum": ["info", "normal", "urgent"],
                         "description": "Gravité ressentie de la demande."},
        },
        "required": ["probleme"],
    },
}


def build_support_prompt(merchant: dict, kb_text: str = "", kb_instructions: str = "",
                         kb_docs: str = "") -> str:
    """Construit le system prompt du support à partir de la base de connaissances du client."""
    name = merchant.get("business_name") or "ce service"
    tone = (merchant.get("ai_tone") or "clair, patient et chaleureux").strip()
    languages = merchant.get("languages") or "français"
    kb = (kb_text or "").strip() or "(base de connaissances vide — escalade toute question de fond)"
    docs = (kb_docs or "").strip()
    consignes = (kb_instructions or "").strip()
    docs_block = f"\n\n# Documents fournis par le responsable\n{docs}" if docs else ""
    consignes_block = (f"\n\n# Consignes du responsable (à respecter strictement)\n{consignes}"
                       if consignes else "")
    return f"""Tu es l'agent de SUPPORT de « {name} ». Tu réponds à SES utilisateurs (ses clients),
sur WhatsApp et sur son site. Tu n'es PAS un vendeur : tu aides, tu expliques, tu dépannes,
tu rassures.

# Règle absolue (grounded)
Tu réponds UNIQUEMENT à partir de la base de connaissances ci-dessous. Tu n'inventes JAMAIS
une information, un prix, une procédure, un délai ou une promesse. Si l'info n'y est pas, tu
ne la devines pas.

# Quand tu ne sais pas (TRÈS important)
Si la réponse n'est pas dans la base, OU si l'utilisateur est mécontent / fait une réclamation /
rencontre un problème que tu ne peux pas résoudre / redemande la même chose malgré ton
explication : n'invente pas. Rassure-le (« je vérifie ça avec l'équipe et on revient vers toi
très vite 🙏 ») et appelle l'outil « escalader » avec le problème précis et son contact s'il est
connu. Mieux vaut escalader que se tromper — c'est ce qui protège la réputation du business.

# Style
Ton : {tone}. Réponds dans la langue de l'utilisateur ({languages} ; langues locales si besoin
et que tu es sûr, sinon français). Messages clairs et courts, sans jargon, sans markdown lourd.
Patient, pédagogue et rassurant, toujours.

# Base de connaissances de {name}
{kb}{docs_block}{consignes_block}"""


def _text_of(resp) -> str:
    return "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()


def reply(merchant: dict, question: str, history: list[dict] | None = None,
          kb_text: str = "", kb_instructions: str = "", kb_docs: str = "",
          on_escalate=None) -> str:
    """Réponse de l'agent de support à un utilisateur. `on_escalate(dict)` = callback
    appelé quand l'agent escalade (créer ticket + notifier le responsable). Ne lève pas."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system = [{"type": "text",
               "text": build_support_prompt(merchant, kb_text, kb_instructions, kb_docs),
               "cache_control": {"type": "ephemeral"}}]  # base cachée → coût quasi nul en répété
    messages: list[dict] = []
    for h in (history or [])[-12:]:
        role = "assistant" if h.get("role") in ("assistant", "ai") else "user"
        c = (h.get("content") or "").strip()
        if c:
            messages.append({"role": role, "content": c})
    messages.append({"role": "user", "content": (question or "").strip() or "Bonjour"})

    model = model_config.model_for("manager")
    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model, max_tokens=model_config.tokens_for("manager", 600),
            system=system, messages=messages, tools=[ESCALATE_TOOL],
        )
        usage.track("support_agent", model, resp, merchant.get("id"))  # F3 — mesure coût
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            return _text_of(resp) or "Je suis là pour t'aider 🙂"
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            if tu.name == "escalader" and on_escalate:
                try:
                    on_escalate(dict(tu.input or {}))
                except Exception:  # noqa: BLE001
                    log.exception("escalade support échouée")
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": ("Le responsable est prévenu avec le problème. Rassure "
                                        "l'utilisateur : l'équipe revient vers lui très vite. "
                                        "Reste utile en attendant.")})
        messages.append({"role": "user", "content": results})

    resp = client.messages.create(
        model=model, max_tokens=model_config.tokens_for("manager", 400),
        system=system, messages=messages,
    )
    usage.track("support_agent", model, resp, merchant.get("id"))
    return _text_of(resp) or "Je suis là pour t'aider 🙂"
