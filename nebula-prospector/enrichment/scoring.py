"""Scoring Claude — qualifie le fit prospect / NEBULA Agency."""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from config import settings

log = logging.getLogger(__name__)

SCORING_PROMPT = """Tu es NOVA, l'agent commercial autonome de NEBULA Agency, basée à Cotonou (Bénin).

NEBULA Agency crée des **vitrines digitales premium** pour entrepreneurs d'Afrique de l'Ouest francophone (Bénin, Togo, Côte d'Ivoire, Sénégal, Burkina Faso). Offre :
- Vitrine + QR code + WhatsApp + paiement Mobile Money — 150 000 FCFA setup
- Catalogue digital — 50 000 FCFA setup
- Fiche Google Maps — 20 000 FCFA
- QR Code Google Review — 30 000 FCFA
- Délai livraison : 5 à 7 jours

**Cible idéale** : artisans, instituts de beauté, salons, boutiques, restaurants, photographes, jeunes marques, créateurs locaux qui n'ont PAS encore de présence web pro (ou en ont une vraiment basique).

**Pas la cible** : grandes entreprises déjà très digitalisées, multinationales, banques, services publics.

Voici un prospect potentiel :
- **Nom** : {name}
- **Secteur** : {sector}
- **Ville** : {city}, {country}
- **Site web actuel** : {website}
- **Email trouvé** : {email}
- **Réseaux sociaux** : {socials}

Voici un extrait du contenu de leur site web (homepage) :
---
{site_content}
---

Donne un **score de 1 à 10** sur le fit avec NEBULA Agency :
- **10** = prospect parfait (entrepreneur local sans web pro, secteur cible exact)
- **7-9** = très bon fit (à contacter en priorité)
- **4-6** = fit moyen (peut-être déjà bien équipé, ou trop gros, ou secteur tangent)
- **1-3** = pas pertinent (grande entreprise, secteur incompatible, pas en Afrique de l'Ouest)

**Réponds en JSON STRICT uniquement** (pas de markdown, pas de texte avant/après) :
{{"score": <entier 1-10>, "reason": "<une phrase courte expliquant la note>"}}"""


def _build_socials_line(prospect: dict[str, Any]) -> str:
    parts = []
    if prospect.get("facebook_url"):
        parts.append(f"FB: {prospect['facebook_url']}")
    if prospect.get("instagram_url"):
        parts.append(f"IG: {prospect['instagram_url']}")
    if prospect.get("linkedin_url"):
        parts.append(f"LI: {prospect['linkedin_url']}")
    return " · ".join(parts) if parts else "(aucun)"


def _strip_code_fence(text: str) -> str:
    """Retire les ```json ... ``` éventuels."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1] if "```" in t[3:] else t[3:]
        if t.lower().startswith("json"):
            t = t[4:]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def score_prospect(prospect: dict[str, Any], site_content: str = "") -> dict[str, Any]:
    """Demande à Claude de scorer le fit NEBULA.

    Retourne `{"score": int 0-10, "reason": str}`.
    Score 0 = erreur (pas un vrai score, signal d'échec).
    """
    if not settings.anthropic_api_key:
        return {"score": 0, "reason": "ANTHROPIC_API_KEY manquante"}

    client = Anthropic(api_key=settings.anthropic_api_key)
    prompt = SCORING_PROMPT.format(
        name=prospect.get("name") or "?",
        sector=prospect.get("sector") or prospect.get("sector_normalized") or "?",
        city=prospect.get("city") or "?",
        country=prospect.get("country") or "?",
        website=prospect.get("website") or "(aucun)",
        email=prospect.get("email") or "(non trouvé)",
        socials=_build_socials_line(prospect),
        site_content=site_content[:2500] if site_content else "(site non accessible ou aucun site)",
    )

    try:
        resp = client.messages.create(
            model=settings.claude_model_fast,
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = resp.content[0].text if resp.content else ""
    except Exception as e:
        log.exception(f"Claude scoring API failed: {e}")
        return {"score": 0, "reason": f"Claude API error: {e}"}

    cleaned = _strip_code_fence(raw_text)
    try:
        data = json.loads(cleaned)
        score = int(data.get("score", 0))
        reason = (data.get("reason") or "").strip()
        score = max(1, min(10, score)) if score > 0 else 0
        return {"score": score, "reason": reason or "(pas de raison fournie)"}
    except Exception as e:
        log.warning(f"Claude scoring JSON parse failed: {cleaned[:200]!r}")
        return {"score": 0, "reason": f"parse error ({e}): {cleaned[:120]}"}
