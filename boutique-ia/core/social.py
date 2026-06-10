"""Vendora Social — moteur de contenu (module dans Vendora, futur « Postora »).

Génère des idées de posts ANCRÉES sur le catalogue (« du social qui vend »), avec :
- du COPYWRITING qui vend (accroche, bénéfice, urgence honnête, CTA fort) ;
- une ADAPTATION PAR RÉSEAU : une variante NATIVE optimisée pour chaque réseau
  (Facebook, Instagram…) plutôt que le même texte partout.

Brique sûre : on rédige, le commerçant valide/copie. La PUBLICATION auto via API
officielle + la génération d'IMAGES (core/social_image) sont des briques à part.

Coût maîtrisé : généré À LA DEMANDE (clic), jamais en autonomie.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date, timedelta
from typing import Any

import anthropic

from config import settings
from core import model_config

log = logging.getLogger("boutique-ia.social")

_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Réseaux du MVP + leur style natif (l'IA adapte le post à chacun).
_NETWORKS: dict[str, str] = {
    "Facebook": ("3 à 5 lignes, ton chaleureux et communautaire, on peut contextualiser/raconter, "
                 "numéro ou invitation à écrire OK, 2 à 4 hashtags max."),
    "Instagram": ("2 à 3 lignes percutantes, accroche forte dès la 1ère ligne, 1 à 3 emojis, "
                  "pensé pour le visuel, 8 à 15 hashtags ciblés."),
}

_COPY_RULES = (
    "RÈGLES DE COPYWRITING (style qui VEND, applique-les) :\n"
    "- 1ère ligne = ACCROCHE qui stoppe le scroll (question, bénéfice choc, curiosité).\n"
    "- Parle BÉNÉFICE pour le client, pas seulement caractéristiques.\n"
    "- Crée le désir + une urgence HONNÊTE (stock limité, pièce unique, promo du jour) UNIQUEMENT si c'est vrai.\n"
    "- Preuve sociale légère si crédible (« nos clientes adorent… »).\n"
    "- Termine TOUJOURS par un CTA clair : « Écris-nous en privé pour commander », « Réserve le tien »…\n"
    "- Jamais de produit/prix hors catalogue."
)


def _catalogue_brief(products: list[dict], limit: int = 12) -> str:
    lines = []
    for p in (products or [])[:limit]:
        if p.get("available") is False:
            continue
        name = (p.get("name") or "").strip()
        if not name:
            continue
        price = p.get("price")
        price_txt = f" — {int(float(price)):,} F".replace(",", " ") if price not in (None, "") else ""
        lines.append(f"- {name}{price_txt}")
    return "\n".join(lines) or "(catalogue vide)"


def _clean_hashtags(h) -> str:
    if isinstance(h, list):
        return " ".join(str(x).strip() for x in h if str(x).strip())
    return str(h or "").strip()


def _parse_posts(text: str) -> list[dict[str, Any]]:
    """Extrait le tableau JSON de posts (robuste) → posts avec variantes par réseau."""
    if not text:
        return []
    m = re.search(r"\[.*\]", text, re.S)
    raw = m.group(0) if m else text
    try:
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        return []
    out: list[dict[str, Any]] = []
    for i, item in enumerate(data if isinstance(data, list) else []):
        if not isinstance(item, dict):
            continue
        reseaux = []
        for net in _NETWORKS:
            v = item.get(net.lower()) or item.get(net)
            if isinstance(v, dict) and (v.get("legende") or v.get("caption")):
                reseaux.append({"reseau": net,
                                "legende": str(v.get("legende") or v.get("caption")).strip(),
                                "hashtags": _clean_hashtags(v.get("hashtags"))})
        # Repli : pas de variantes → on réutilise une légende à plat pour tous les réseaux.
        if not reseaux:
            flat = str(item.get("legende") or item.get("caption") or "").strip()
            if not flat:
                continue
            reseaux = [{"reseau": net, "legende": flat,
                        "hashtags": _clean_hashtags(item.get("hashtags"))} for net in _NETWORKS]
        out.append({
            "jour": str(item.get("jour") or item.get("day") or _JOURS[i % 7]).strip(),
            "type": str(item.get("type") or "post").strip(),
            "idee_visuelle": str(item.get("idee_visuelle") or item.get("visuel") or "").strip(),
            "reseaux": reseaux,
        })
    return out


def generate_posts(merchant: dict, products: list[dict], n: int = 5,
                   lessons: str | None = None) -> list[dict[str, Any]]:
    """Génère `n` posts (copy qui vend + variante NATIVE par réseau). [] si KO.

    `lessons` : leçons de vente apprises (cerveau d'apprentissage) → le contenu
    s'améliore avec l'expérience collective (auto-amélioration).
    """
    settings.require("anthropic_api_key")
    name = merchant.get("business_name") or "la boutique"
    sector = merchant.get("sector") or ""
    tone = merchant.get("ai_tone") or "chaleureux et professionnel"
    city = merchant.get("city") or ""
    desc = merchant.get("description") or ""
    catalogue = _catalogue_brief(products)
    nets_doc = "\n".join(f"- {net} : {style}" for net, style in _NETWORKS.items())

    system_text = (
        f"Tu es un social media manager + copywriter d'élite pour « {name} »"
        f"{f' ({sector})' if sector else ''}{f', à {city}' if city else ''}.\n"
        f"Description : {desc or '(non fournie)'}\n"
        f"Ton de marque : {tone}. Clientèle : Afrique de l'Ouest.\n\n"
        f"{_COPY_RULES}\n\n"
        "ADAPTATION PAR RÉSEAU — ne mets PAS le même texte partout, écris une variante "
        f"NATIVE pour chaque réseau selon son style :\n{nets_doc}\n\n"
        f"Catalogue (ancre-toi dessus, jamais d'invention) :\n{catalogue}"
        + (f"\n\n# Leçons de vente apprises (applique-les)\n{lessons.strip()}"
           if lessons and lessons.strip() else "")
    )
    consigne = (
        f"Génère exactement {n} idées de posts variées (produit phare, promo, conseil, "
        "preuve sociale, nouveauté…). Pour CHAQUE post, écris une variante Facebook ET une "
        "variante Instagram. Réponds UNIQUEMENT par un tableau JSON, sans texte autour, au format : "
        '[{"jour":"Lundi","type":"produit","idee_visuelle":"quoi montrer en photo",'
        '"facebook":{"legende":"...","hashtags":"#x #y"},'
        '"instagram":{"legende":"...","hashtags":"#x #y #z"}}]'
    )
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=model_config.model_for("writer"), max_tokens=model_config.tokens_for("writer", 2800),
            system=[{"type": "text", "text": system_text,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": consigne}],
        )
        text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        return _parse_posts(text)[:n]
    except Exception:  # noqa: BLE001
        log.warning("génération posts social KO", exc_info=True)
        return []


def _spread_dates(per_week: int, weeks: int, count: int) -> list:
    """Répartit `count` posts sur la période : `per_week` par semaine, jours espacés (dès demain)."""
    base = date.today() + timedelta(days=1)
    out = []
    for i in range(count):
        wk, slot = i // per_week, i % per_week
        out.append(base + timedelta(days=wk * 7 + round(slot * 7 / per_week)))
    return out


def generate_calendar(merchant: dict, products: list[dict],
                      per_week: int = 3, weeks: int = 2,
                      lessons: str | None = None) -> list[dict[str, Any]]:
    """Planifie un calendrier de posts (texte par réseau) sur la période choisie par le client.

    `per_week` (1-7) × `weeks` (1-4), plafonné à 12 posts (coût maîtrisé). Chaque post
    reçoit une DATE de publication prévue. La publication auto à ces dates = Phase 3 (Meta).
    """
    per_week = max(1, min(7, int(per_week or 3)))
    weeks = max(1, min(4, int(weeks or 2)))
    n = min(12, per_week * weeks)
    posts = generate_posts(merchant, products, n=n, lessons=lessons)
    dates = _spread_dates(per_week, weeks, len(posts))
    for i, p in enumerate(posts):
        if i < len(dates):
            d = dates[i]
            p["date"] = d.strftime("%d/%m")
            p["jour"] = _JOURS[d.weekday()]
    return posts
