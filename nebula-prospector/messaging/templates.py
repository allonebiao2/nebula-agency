"""Génération de cold emails personnalisés via Claude.

Structure 5 lignes (brief NOVA v2.0) :
  Ligne 1 : Accroche personnalisée (prénom + nom du business)
  Ligne 2 : Leur problème exact (extrait du site / signal détecté)
  Ligne 3 : La solution NEBULA en 1 phrase
  Ligne 4 : Preuve sociale (cas similaire)
  Ligne 5 : CTA ultra simple (répondez OUI / une question)

L'objectif : que le destinataire puisse répondre en 1 phrase.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from config import settings
from core.tool_calls import tool_call

log = logging.getLogger(__name__)


# Pitch NEBULA selon le service recommandé
SERVICE_PITCH = {
    "vitrine": {
        "name": "vitrine digitale + QR code + paiement Mobile Money",
        "price": "150 000 FCFA",
        "delay": "5 à 7 jours",
        "proof": "On a livré ça à Grain d'Esthétique (Cotonou) — leur institut reçoit maintenant des réservations 24h/24.",
    },
    "catalogue": {
        "name": "catalogue digital interactif + QR code",
        "price": "50 000 FCFA",
        "delay": "5 à 7 jours",
        "proof": "INA Luxury (Cotonou) gère ses 37 produits via notre catalogue — chaque client commande directement sur WhatsApp.",
    },
    "qr_menu": {
        "name": "QR Code menu digital",
        "price": "à partir de 30 000 FCFA",
        "delay": "5 à 7 jours",
        "proof": "Plusieurs restaurants/bars du Bénin utilisent nos QR menus pour leurs clients.",
    },
    "fiche_maps": {
        "name": "fiche Google Maps professionnelle",
        "price": "20 000 FCFA",
        "delay": "5 à 7 jours",
        "proof": "Les commerces avec une fiche Google bien faite voient leurs visites doubler en 1 mois.",
    },
    "qr_review": {
        "name": "QR Code Google Review",
        "price": "30 000 FCFA",
        "delay": "2 à 3 jours",
        "proof": "Vos clients scannent → laissent un avis Google en 30 secondes — votre réputation décolle.",
    },
    "auto_whatsapp": {
        "name": "automatisation WhatsApp (réponses auto, commandes, suivi)",
        "price": "sur devis",
        "delay": "1 à 2 semaines",
        "proof": "Un business avec 100 demandes/jour gagne ~3h/jour avec notre automatisation.",
    },
}


SYSTEM_PROMPT = """Tu es NOVA, agent commercial autonome de NEBULA Agency (Cotonou, Bénin).

Ton style :
- Direct, chaleureux, court (max 6 phrases)
- Tutoiement par défaut (entrepreneurs locaux d'Afrique de l'Ouest)
- JAMAIS de jargon commercial pompeux ("synergie", "leverage", "transformer votre business")
- JAMAIS de phrase qui sonne IA ("J'espère que ce message vous trouve bien")
- Tu peux glisser **1 émoji max** (pas plus)
- Tu signes : "— Mongazi · NEBULA Agency"

Tu DOIS suivre la structure 5 lignes :
1. **Accroche** (prénom OU nom du business + détail spécifique vu sur leur site/réseaux)
2. **Problème** détecté chez eux (concret, pas "vous voulez plus de clients")
3. **Solution NEBULA** en une phrase
4. **Preuve sociale** (cas similaire)
5. **CTA simple** : oriente vers la vitrine NEBULA `https://nebula-agency.online` OU une question courte ("Dis-moi OUI je t'envoie un exemple")

Quand le prospect manifeste de l'intérêt, le closing DOIT passer par la vitrine NEBULA (où il choisit son forfait et passe commande) OU par le WhatsApp NEBULA (+229 96 74 07 32). Tu ne closes JAMAIS toi-même."""


USER_PROMPT_TEMPLATE = """Voici un prospect à contacter par email :

- Nom du business : {name}
- Secteur : {sector}
- Ville : {city}, {country}
- Site web : {website}
- Email : {email}
- Réseaux : {socials}
- Score NEBULA : {score}/10 ({tier})
- Service que je veux pitcher : **{service_name}** ({service_price}, livré en {service_delay})
- Preuve sociale à utiliser : {service_proof}

Extrait de leur site (analyse ce contenu pour personnaliser) :
---
{site_content}
---

**Génère un cold email en français suivant la structure 5 lignes**.

Objet : court (max 50 caractères), spécifique, sans clickbait, sans "Re:", sans "URGENT".

**Réponds en JSON STRICT** (aucun texte avant/après, pas de markdown) :
{{
  "subject": "<objet du mail>",
  "body": "<corps du mail en français, séparé par \\n\\n entre paragraphes, signé '— Mongazi · NEBULA Agency'>",
  "personalization_notes": "<une phrase qui explique ce que tu as personnalisé>"
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


def _build_socials_line(prospect: dict[str, Any]) -> str:
    parts = []
    if prospect.get("facebook_url"):
        parts.append(f"FB: {prospect['facebook_url']}")
    if prospect.get("instagram_url"):
        parts.append(f"IG: {prospect['instagram_url']}")
    if prospect.get("linkedin_url"):
        parts.append(f"LI: {prospect['linkedin_url']}")
    return " · ".join(parts) if parts else "(aucun)"


@tool_call("claude.email", per_hour=30, per_day=200, raise_on_limit=False)
def generate_cold_email(
    prospect: dict[str, Any],
    site_content: str = "",
    service: str | None = None,
) -> dict[str, Any]:
    """Génère un cold email personnalisé pour un prospect.

    Retourne : {"subject": str, "body": str, "personalization_notes": str, "service": str, "error": str | None}
    """
    if not settings.anthropic_api_key:
        return {"subject": "", "body": "", "service": service or "",
                "personalization_notes": "", "error": "ANTHROPIC_API_KEY manquante"}

    svc_key = service or prospect.get("recommended_service") or "vitrine"
    if svc_key not in SERVICE_PITCH:
        svc_key = "vitrine"
    svc_info = SERVICE_PITCH[svc_key]

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=prospect.get("name") or "?",
        sector=prospect.get("sector") or prospect.get("sector_normalized") or "?",
        city=prospect.get("city") or "?",
        country=prospect.get("country") or "?",
        website=prospect.get("website") or "(aucun)",
        email=prospect.get("email") or "(à trouver)",
        socials=_build_socials_line(prospect),
        score=prospect.get("score", 0),
        tier=prospect.get("tier", "—"),
        service_name=svc_info["name"],
        service_price=svc_info["price"],
        service_delay=svc_info["delay"],
        service_proof=svc_info["proof"],
        site_content=site_content[:2000] if site_content else "(aucun contenu disponible — base-toi sur le secteur)",
    )

    # Injecte les skills appris (taggés 'skill') dans le system prompt
    system_with_skills = SYSTEM_PROMPT
    try:
        from core.documents import search_documents
        skills = search_documents(tag="skill", limit=20)
        if skills:
            skill_block = "\n\n## TES SKILLS APPRIS (à appliquer dans cet email)\n"
            for s in skills:
                title = s.get("title") or s.get("key")
                content = (s.get("content") or "")[:500]
                skill_block += f"\n### {title}\n{content}\n"
            system_with_skills = SYSTEM_PROMPT + skill_block
    except Exception as e:
        log.debug(f"skills injection failed: {e}")

    client = Anthropic(api_key=settings.anthropic_api_key)
    try:
        resp = client.messages.create(
            model=settings.claude_model_fast,
            max_tokens=800,
            system=system_with_skills,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = resp.content[0].text if resp.content else ""
    except Exception as e:
        log.exception(f"Claude email generation failed: {e}")
        return {"subject": "", "body": "", "service": svc_key,
                "personalization_notes": "", "error": f"Claude API error: {e}"}

    cleaned = _strip_code_fence(raw_text)
    try:
        data = json.loads(cleaned)
        subject = (data.get("subject") or "").strip()[:120]
        body = (data.get("body") or "").strip()
        notes = (data.get("personalization_notes") or "").strip()
        if not subject or not body:
            return {"subject": "", "body": "", "service": svc_key,
                    "personalization_notes": "", "error": "empty subject/body"}
        return {"subject": subject, "body": body, "service": svc_key,
                "personalization_notes": notes, "error": None}
    except Exception as e:
        log.warning(f"Email JSON parse failed: {cleaned[:200]!r}")
        return {"subject": "", "body": "", "service": svc_key,
                "personalization_notes": "", "error": f"parse error: {e}"}
