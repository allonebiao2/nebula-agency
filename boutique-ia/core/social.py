"""Vendora Social — moteur de contenu (Phase 2, brique 1).

Génère des idées de posts réseaux sociaux ANCRÉES sur le catalogue de la boutique
(« du social qui vend »), + un mini calendrier. Brique SÛRE : aucune publication
automatique ici (pas de dépendance Meta) — on rédige, le commerçant valide/copie.
La publication via API officielle viendra en Phase 3 (compte connecté + App Review).

Coût maîtrisé : généré À LA DEMANDE (clic), jamais en autonomie.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic

from config import settings

log = logging.getLogger("boutique-ia.social")

_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


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


def _parse_posts(text: str) -> list[dict[str, Any]]:
    """Extrait le tableau JSON de posts de la réponse du modèle (robuste)."""
    if not text:
        return []
    # Tente de récupérer le 1er bloc [...] JSON.
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
        legende = (item.get("legende") or item.get("caption") or "").strip()
        if not legende:
            continue
        hashtags = item.get("hashtags") or ""
        if isinstance(hashtags, list):
            hashtags = " ".join(str(h).strip() for h in hashtags if str(h).strip())
        out.append({
            "jour": (str(item.get("jour") or item.get("day") or _JOURS[i % 7])).strip(),
            "type": (str(item.get("type") or "post")).strip(),
            "legende": legende,
            "hashtags": str(hashtags).strip(),
            "idee_visuelle": (str(item.get("idee_visuelle") or item.get("visuel") or "")).strip(),
        })
    return out


def generate_posts(merchant: dict, products: list[dict], n: int = 5) -> list[dict[str, Any]]:
    """Génère `n` idées de posts (légende + hashtags + idée visuelle) pour la boutique.

    Contenu orienté VENTE, ancré sur le catalogue. Retourne [] si génération KO.
    """
    settings.require("anthropic_api_key")
    name = merchant.get("business_name") or "la boutique"
    sector = merchant.get("sector") or ""
    tone = merchant.get("ai_tone") or "chaleureux et professionnel"
    city = merchant.get("city") or ""
    desc = merchant.get("description") or ""
    catalogue = _catalogue_brief(products)

    system_text = (
        f"Tu es un social media manager expert pour « {name} »"
        f"{f' ({sector})' if sector else ''}{f', à {city}' if city else ''}.\n"
        f"Description : {desc or '(non fournie)'}\n\n"
        "Ton rôle : créer des idées de posts pour Facebook/Instagram qui font VENDRE — "
        "ancrés sur les vrais produits ci-dessous, jamais génériques. Style adapté au ton "
        f"« {tone} », adapté à une clientèle d'Afrique de l'Ouest. Chaque post doit donner "
        "envie d'écrire en privé pour commander.\n\n"
        f"Catalogue :\n{catalogue}"
    )
    consigne = (
        f"Génère exactement {n} idées de posts variées (produit phare, promo, conseil, "
        "preuve sociale, nouveauté…). Réponds UNIQUEMENT par un tableau JSON, sans texte "
        "autour, au format : "
        '[{"jour":"Lundi","type":"produit","legende":"texte du post (2-4 lignes, 1-2 emojis, '
        'appel à écrire en privé)","hashtags":"#x #y","idee_visuelle":"quoi montrer en photo"}]'
    )
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.writer_model, max_tokens=1500,
            system=[{"type": "text", "text": system_text,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": consigne}],
        )
        text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        return _parse_posts(text)[:n]
    except Exception:  # noqa: BLE001
        log.warning("génération posts social KO", exc_info=True)
        return []
