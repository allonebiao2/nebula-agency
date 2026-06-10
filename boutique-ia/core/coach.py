"""Coach commercial — le « directeur commercial » de CHAQUE boutique.

À partir des vraies données de la boutique (ventes, conversations, conversion,
top produits, invendus), l'agent donne des conseils CONCRETS et chiffrés pour
vendre plus. Réutilise l'esprit du cerveau CEO (core/strategist) mais au niveau
d'UNE boutique, côté commerçant (rétention + valeur perçue = anti-résiliation).

Coût maîtrisé : généré À LA DEMANDE (clic), jamais en autonomie.
"""
from __future__ import annotations

import logging

import anthropic

from config import settings
from core import model_config

log = logging.getLogger("boutique-ia.coach")


def _snapshot(merchant: dict) -> dict:
    """Photo chiffrée de la boutique (défensif : valeurs par défaut si données absentes)."""
    from db.client import get_db, list_orders, list_products, order_stats
    mid = merchant.get("id")
    snap = {"ventes": 0, "ca": 0, "conversations": 0, "conversion": 0.0,
            "nb_produits": 0, "top": [], "dead": [],
            "cod": bool(merchant.get("cod_enabled")), "nego": bool(merchant.get("negotiation_enabled"))}
    try:
        st = order_stats(mid) or {}
        snap["ventes"] = st.get("count", 0) or 0
        snap["ca"] = st.get("revenue", 0) or 0
    except Exception:  # noqa: BLE001
        pass
    products = []
    try:
        products = list_products(mid) or []
        snap["nb_produits"] = len(products)
    except Exception:  # noqa: BLE001
        pass
    # Top ventes + invendus (à partir des articles des commandes).
    try:
        sold: dict[str, int] = {}
        for o in (list_orders(mid, limit=200) or []):
            for it in (o.get("items") or []):
                name = (it.get("produit") or "").strip()
                if name:
                    sold[name] = sold.get(name, 0) + int(it.get("quantite") or 1)
        snap["top"] = sorted(sold.items(), key=lambda kv: kv[1], reverse=True)[:3]
        snap["dead"] = [p.get("name") for p in products
                        if p.get("name") and p.get("name") not in sold and p.get("available") is not False][:5]
    except Exception:  # noqa: BLE001
        pass
    # Conversations = clients distincts ayant écrit.
    try:
        r = get_db().table("bia_messages").select("customer_whatsapp").eq("merchant_id", mid).execute()
        snap["conversations"] = len({(row.get("customer_whatsapp") or "")
                                     for row in (r.data or []) if row.get("customer_whatsapp")})
    except Exception:  # noqa: BLE001
        pass
    if snap["conversations"]:
        snap["conversion"] = round(100 * snap["ventes"] / snap["conversations"], 1)
    return snap


def _fmt_top(top: list) -> str:
    return ", ".join(f"{n} (×{q})" for n, q in top) or "aucune vente enregistrée pour l'instant"


def generate_coaching(merchant: dict, lessons: str | None = None) -> dict:
    """Conseil de la semaine pour la boutique : {snapshot, advice}. advice='' si KO.

    `lessons` : leçons de vente apprises (auto-amélioration) → le coaching profite
    de l'expérience collective.
    """
    settings.require("anthropic_api_key")
    snap = _snapshot(merchant)
    name = merchant.get("business_name") or "la boutique"
    sector = merchant.get("sector") or ""

    system = (
        f"Tu es le DIRECTEUR COMMERCIAL de la boutique « {name} »"
        f"{f' ({sector})' if sector else ''}, en Afrique de l'Ouest. "
        "Tu analyses ses chiffres et tu donnes des conseils CONCRETS, chiffrés et actionnables "
        "pour vendre PLUS cette semaine. Pas de généralités, pas de blabla. Ton direct, motivant, "
        "vouvoiement chaleureux. Tu ne proposes que des actions réalistes pour un petit commerçant."
    )
    data = (
        "Chiffres de la boutique :\n"
        f"- Ventes : {snap['ventes']} · Chiffre d'affaires : {int(snap['ca']):,} F\n".replace(",", " ") +
        f"- Clients ayant écrit : {snap['conversations']} · Taux de conversion : {snap['conversion']} %\n"
        f"- Produits au catalogue : {snap['nb_produits']}\n"
        f"- Meilleures ventes : {_fmt_top(snap['top'])}\n"
        f"- Jamais vendus : {', '.join(snap['dead']) or '—'}\n"
        f"- Paiement à la livraison : {'activé' if snap['cod'] else 'désactivé'} · "
        f"Négociation : {'activée' if snap['nego'] else 'désactivée'}"
    )
    # Intelligence collective : repère anonymisé du secteur (vide si trop peu de pairs).
    try:
        from core import collective
        bench = collective.benchmark_for(merchant)
        if bench:
            data += "\n- " + bench
    except Exception:  # noqa: BLE001
        pass
    consigne = (
        "Donne 3 à 5 conseils NUMÉROTÉS, chacun = UNE action concrète à faire CETTE SEMAINE "
        "(quel produit pousser, quel prix ou promo, quoi réapprovisionner ou retirer du catalogue, "
        "à quelles heures être actif, relancer qui, activer le paiement à la livraison ou la "
        "négociation si pertinent). 1 à 2 phrases max par conseil, chiffré quand possible. "
        "Termine par UNE phrase d'encouragement. N'invente aucun chiffre non fourni. "
        "Si un repère secteur est fourni, situe la boutique par rapport (mieux/moins bien) et "
        "conseille en conséquence."
    )
    if lessons and lessons.strip():
        data += "\n\n# Leçons de vente apprises (appuie-toi dessus)\n" + lessons.strip()
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=model_config.model_for("writer"), max_tokens=model_config.tokens_for("writer", 750),
            system=[{"type": "text", "text": system}],
            messages=[{"role": "user", "content": data + "\n\n" + consigne}],
        )
        advice = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
    except Exception:  # noqa: BLE001
        log.warning("génération coaching KO", exc_info=True)
        advice = ""
    return {"snapshot": snap, "advice": advice}
