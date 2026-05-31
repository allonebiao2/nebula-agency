"""Scoring Claude — qualifie le fit prospect / NEBULA Agency.

Barème explicite (10 points max) :
+3  besoin explicite détecté (recherche site, vente en ligne, visibilité)
+2  business actif (posts récents, site basique, signes de vie commerciale)
+2  secteur prioritaire NEBULA (beauté, mode, restauration, photo, artisanat, jeune marque)
+2  contact direct disponible (email, téléphone, ou réseau social actif)
+1  localisation Afrique de l'Ouest francophone (BJ, TG, CI, SN, BF)
-2  déjà un site web professionnel et complet
-3  concurrent (agence digitale, webdesign, marketing) ou grand groupe

Segmentation :
hot       (8-10) → contact prioritaire dans la journée
warm      (5-7)  → contact dans la semaine
cold      (1-4)  → liste d'attente / pas encore mûr
rejected  (0)    → pas pertinent (concurrent, grand groupe, hors cible)

Service NEBULA recommandé (en fonction du profil) :
- vitrine        : pas de site, business prêt à vendre en ligne
- catalogue      : vend des produits, beaucoup de SKUs
- qr_menu        : restaurant, bar, salon
- fiche_maps     : commerce physique sans présence Google
- qr_review      : business établi avec besoin de réputation
- auto_whatsapp  : volume de demandes WA important
"""
from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic

from config import settings
from core.tool_calls import tool_call

log = logging.getLogger(__name__)

VALID_SERVICES = {
    "vitrine", "catalogue", "qr_menu", "fiche_maps",
    "qr_review", "auto_whatsapp",
}
VALID_TIERS = {"hot", "warm", "cold", "rejected"}

SCORING_PROMPT = """Tu es NOVA, agent commercial autonome de NEBULA Agency (Cotonou, Bénin).

**Catalogue NEBULA** :
- `vitrine` — Vitrine digitale + QR + Mobile Money — 150 000 FCFA setup (idéal : pas de site, business prêt à vendre)
- `catalogue` — Catalogue digital + QR — 50 000 FCFA setup (idéal : beaucoup de produits à exposer)
- `qr_menu` — QR Code menu — sur devis (idéal : restaurants, bars, salons)
- `fiche_maps` — Fiche Google Maps — 20 000 FCFA (idéal : commerce physique sans présence Google)
- `qr_review` — QR Code Google Review — 30 000 FCFA (idéal : business établi qui veut plus d'avis)
- `auto_whatsapp` — Automatisation WhatsApp — sur devis (idéal : business avec gros volume de demandes WA)

**Cible géographique** : Bénin, Togo, Côte d'Ivoire, Sénégal, Burkina Faso.

**Cible idéale** : artisans, instituts beauté, salons, boutiques, restaurants, photographes, jeunes marques, créateurs locaux sans présence web pro.

**À éviter** : grandes entreprises digitalisées, multinationales, banques, services publics, autres agences digitales (concurrents).

---

**Prospect à évaluer** :
- Nom : {name}
- Secteur : {sector}
- Localisation : {city}, {country}
- Site web : {website}
- Email : {email}
- Réseaux : {socials}

**Contenu du site (extrait)** :
{site_content}

---

**Barème (max 10)** :
- +3 si besoin explicite détecté (texte parle de site, vente en ligne, visibilité)
- +2 si business actif (signes de vie commerciale, nouveautés)
- +2 si secteur prioritaire NEBULA (beauté/mode/resto/photo/artisanat/jeune marque)
- +2 si contact direct disponible (email OU réseaux actifs)
- +1 si localisation Afrique de l'Ouest francophone
- -2 si déjà un site web pro et complet
- -3 si concurrent (agence/webdesign/marketing) ou grand groupe → score = 0 et tier = `rejected`

**Tier** :
- 8-10 → `hot` (à contacter en priorité)
- 5-7 → `warm` (à contacter cette semaine)
- 1-4 → `cold` (pas mûr, plus tard)
- 0   → `rejected` (concurrent, pas la cible)

**Service à pitcher** : choisis UN service dans la liste ci-dessus, celui qui correspond le mieux au prospect. Si rien ne convient → `null`.

**Réponds en JSON STRICT** (pas de markdown, pas de texte avant/après) :
{{
  "score": <entier 0-10>,
  "tier": "hot" | "warm" | "cold" | "rejected",
  "recommended_service": "vitrine" | "catalogue" | "qr_menu" | "fiche_maps" | "qr_review" | "auto_whatsapp" | null,
  "breakdown": {{
    "needs_signal": <-3..3>,
    "active_business": <0..2>,
    "priority_sector": <0..2>,
    "direct_contact": <0..2>,
    "location": <0..1>,
    "has_pro_site": <-2..0>,
    "is_competitor": <-3..0>
  }},
  "reason": "<une phrase courte expliquant le score et le service recommandé>"
}}"""


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


def _coerce_tier(score: int, raw_tier: Any) -> str:
    """Vérifie/déduit le tier à partir du score si besoin."""
    if isinstance(raw_tier, str) and raw_tier in VALID_TIERS:
        return raw_tier
    if score == 0:
        return "rejected"
    if score >= 8:
        return "hot"
    if score >= 5:
        return "warm"
    return "cold"


def _coerce_service(raw: Any) -> str | None:
    if isinstance(raw, str) and raw in VALID_SERVICES:
        return raw
    return None


@tool_call("claude.score", per_hour=120, per_day=1000, raise_on_limit=False)
def score_prospect(prospect: dict[str, Any], site_content: str = "") -> dict[str, Any]:
    """Demande à Claude de scorer le fit NEBULA.

    Retourne un dict :
        {
            "score": int 0-10,
            "tier": "hot" | "warm" | "cold" | "rejected",
            "recommended_service": str | None,
            "breakdown": dict,
            "reason": str,
            "error": str | None  # présent uniquement si parsing failed
        }
    """
    if not settings.anthropic_api_key:
        return {
            "score": 0, "tier": "rejected",
            "recommended_service": None, "breakdown": {},
            "reason": "ANTHROPIC_API_KEY manquante", "error": "config",
        }

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
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = resp.content[0].text if resp.content else ""
    except Exception as e:
        log.exception(f"Claude scoring API failed: {e}")
        return {
            "score": 0, "tier": "rejected",
            "recommended_service": None, "breakdown": {},
            "reason": f"Claude API error: {e}", "error": "api",
        }

    cleaned = _strip_code_fence(raw_text)
    try:
        data = json.loads(cleaned)
        score = int(data.get("score", 0))
        score = max(0, min(10, score))
        tier = _coerce_tier(score, data.get("tier"))
        return {
            "score": score,
            "tier": tier,
            "recommended_service": _coerce_service(data.get("recommended_service")),
            "breakdown": data.get("breakdown") or {},
            "reason": (data.get("reason") or "").strip() or "(pas de raison fournie)",
            "error": None,
        }
    except Exception as e:
        log.warning(f"Claude scoring JSON parse failed: {cleaned[:200]!r}")
        return {
            "score": 0, "tier": "rejected",
            "recommended_service": None, "breakdown": {},
            "reason": f"parse error: {cleaned[:120]}",
            "error": f"parse: {e}",
        }
