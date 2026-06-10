"""Import express du catalogue — colle une liste en texte libre → produits structurés.

Accélère le « on configure pour toi » (montage de démo ultra-rapide). L'IA lit un
texte libre (ex : « Collier perle 7500, Boucles dorées 3500 ») et en extrait des
produits {name, price, description, kind}. Généré À LA DEMANDE (clic).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic

from config import settings
from core import model_config

log = logging.getLogger("boutique-ia.catalog_import")


def _to_price(v: Any) -> Any:
    if v in (None, "", "null"):
        return None
    if isinstance(v, (int, float)):
        return int(v)
    digits = re.sub(r"[^\d]", "", str(v))  # « 7 500 F » / « 7.500 » → 7500
    return int(digits) if digits else None


def _parse(text: str, limit: int) -> list[dict[str, Any]]:
    m = re.search(r"\[.*\]", text, re.S)
    raw = m.group(0) if m else text
    try:
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        return []
    out = []
    for item in (data if isinstance(data, list) else []):
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or item.get("nom") or "").strip()
        if not name:
            continue
        kind = (item.get("kind") or item.get("type") or "produit").strip().lower()
        kind = "service" if kind.startswith("serv") else "produit"
        out.append({
            "name": name[:120],
            "price": _to_price(item.get("price") if "price" in item else item.get("prix")),
            "description": (item.get("description") or "").strip()[:300] or None,
            "kind": kind,
        })
        if len(out) >= limit:
            break
    return out


def parse_products(text: str, limit: int = 40) -> list[dict[str, Any]]:
    """Extrait une liste de produits d'un texte libre. [] si KO/vide."""
    text = (text or "").strip()
    if not text:
        return []
    settings.require("anthropic_api_key")
    system = (
        "Tu extrais des produits/services d'un texte libre de commerçant (Afrique de l'Ouest). "
        "Pour chacun : name (nom court), price (NOMBRE en F CFA, sans symbole, ou null si absent), "
        "description (courte si présente, sinon vide), kind ('produit' ou 'service'). "
        "N'invente RIEN : pas de produit non mentionné, pas de prix inventé."
    )
    consigne = (
        "Texte du commerçant :\n---\n" + text[:4000] + "\n---\n"
        "Réponds UNIQUEMENT par un tableau JSON, sans texte autour : "
        '[{"name":"...","price":7500,"description":"...","kind":"produit"}]'
    )
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=model_config.model_for("manager"), max_tokens=model_config.tokens_for("manager", 2000),
            system=[{"type": "text", "text": system}],
            messages=[{"role": "user", "content": consigne}],
        )
        out = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        return _parse(out, limit)
    except Exception:  # noqa: BLE001
        log.warning("import catalogue KO", exc_info=True)
        return []
