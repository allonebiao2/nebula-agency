"""L'agent de GESTION — le commerçant pilote sa boutique en langage naturel.

Depuis le back-office, le propriétaire donne des « ordres » (« ajoute le collier
à 7000 », « mets les boucles en rupture », « change le ton pour plus formel ») et
cet agent les exécute réellement via des outils (mêmes helpers que le back-office).

Distinct du vendeur (core/brain.py) qui, lui, parle aux clients.
"""
from __future__ import annotations

import logging

import anthropic

from config import settings
from core import model_config
from db.client import (
    add_products,
    delete_product,
    list_products,
    update_merchant,
    update_product,
)

log = logging.getLogger("boutique-ia.manager")

MAX_TOOL_TURNS = 6

TOOLS = [
    {
        "name": "ajouter_produit",
        "description": "Ajoute un produit ou service au catalogue de la boutique.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nom": {"type": "string"},
                "prix": {"type": "number", "description": "Prix en F CFA. Omettre si « sur demande »."},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["produit", "service"]},
                "duree": {"type": "string", "description": "Durée si c'est un service (ex: 1h30)."},
                "options": {"type": "string", "description": "Variantes : tailles, couleurs, formules…"},
            },
            "required": ["nom"],
        },
    },
    {
        "name": "modifier_produit",
        "description": ("Modifie un produit existant (prix, nom, description, type, durée, options, "
                        "disponibilité). Utilise le product_id exact fourni dans le catalogue."),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "nouveau_nom": {"type": "string"},
                "prix": {"type": "number"},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["produit", "service"]},
                "duree": {"type": "string"},
                "options": {"type": "string"},
                "disponible": {"type": "boolean", "description": "false = en rupture."},
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "supprimer_produit",
        "description": "Supprime définitivement un produit. Utilise le product_id exact du catalogue.",
        "input_schema": {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        },
    },
    {
        "name": "modifier_boutique",
        "description": ("Modifie la fiche de la boutique. Ne renseigne que les champs à changer."),
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "sector": {"type": "string"},
                "city": {"type": "string"},
                "business_hours": {"type": "string"},
                "delivery_zones": {"type": "string"},
                "delivery_fee_info": {"type": "string"},
                "momo_number": {"type": "string"},
                "momo_name": {"type": "string"},
                "momo_network": {"type": "string"},
                "ai_tone": {"type": "string", "description": "Ton du vendeur (ex: plus formel)."},
                "languages": {"type": "string"},
                "policies": {"type": "string", "description": "Règles : acompte, retours, garanties."},
                "extra_info": {"type": "string"},
                "cod_enabled": {"type": "boolean", "description": "Activer le paiement à la livraison."},
                "negotiation_enabled": {"type": "boolean", "description": "Autoriser la négociation des prix."},
                "negotiation_rule": {"type": "string", "description": "Limite de négociation (ex: jusqu'à 10%, -500F dès 2 articles)."},
            },
        },
    },
]


def _catalogue(products: list[dict]) -> str:
    if not products:
        return "(catalogue vide)"
    lines = []
    for p in products:
        price = p.get("price")
        price_s = f"{int(price)} F" if price is not None else "sur demande"
        dispo = "" if p.get("available") is not False else " [EN RUPTURE]"
        lines.append(f"- product_id={p.get('id')} | {p.get('name')} | {price_s}{dispo}")
    return "\n".join(lines)


def _system(merchant: dict, products: list[dict]) -> str:
    return f"""Tu es l'assistant de GESTION de la boutique « {merchant.get('business_name','')} ».
Le PROPRIÉTAIRE te donne des ordres pour gérer sa boutique. Exécute-les avec les outils,
puis confirme en 1-2 phrases courtes et claires, en français.

Catalogue actuel (utilise le product_id EXACT pour modifier/supprimer) :
{_catalogue(products)}

Règles :
- Fais exactement ce qui est demandé, rien de plus.
- Pour « en rupture » → modifier_produit avec disponible=false. Pour « de nouveau dispo » → disponible=true.
- Si un ordre est ambigu (ex: plusieurs produits possibles), demande une précision au lieu de deviner.
- Si l'ordre ne concerne pas la gestion de la boutique, explique poliment ce que tu peux faire.
- Ne touche jamais au forfait, au prix de l'abonnement, ni au statut de paiement.
"""


def _exec_tool(merchant_id: str, name: str, args: dict) -> tuple[str, str | None]:
    """Exécute un outil. Retourne (message_pour_le_modele, resume_action_humain)."""
    try:
        if name == "ajouter_produit":
            n = add_products(merchant_id, [{
                "name": args.get("nom"),
                "price": args.get("prix"),
                "description": args.get("description"),
                "kind": args.get("type"),
                "duration": args.get("duree"),
                "options": args.get("options"),
            }])
            if n:
                return "OK, produit ajouté.", f"Ajouté : {args.get('nom')}"
            return "Échec : nom manquant.", None
        if name == "modifier_produit":
            fields = {}
            if args.get("nouveau_nom"):
                fields["name"] = args["nouveau_nom"]
            if "prix" in args:
                fields["price"] = args["prix"]
            if "description" in args:
                fields["description"] = args["description"]
            if "type" in args:
                fields["kind"] = args["type"]
            if "duree" in args:
                fields["duration"] = args["duree"]
            if "options" in args:
                fields["options"] = args["options"]
            if "disponible" in args:
                fields["available"] = args["disponible"]
            p = update_product(args.get("product_id", ""), merchant_id, fields)
            if p:
                return "OK, produit modifié.", f"Modifié : {p.get('name')}"
            return "Produit introuvable.", None
        if name == "supprimer_produit":
            ok = delete_product(args.get("product_id", ""), merchant_id)
            return ("OK, produit supprimé." if ok else "Produit introuvable.",
                    "Produit supprimé" if ok else None)
        if name == "modifier_boutique":
            m = update_merchant(merchant_id, args)
            if m:
                champs = ", ".join(args.keys())
                return "OK, fiche mise à jour.", f"Fiche mise à jour ({champs})"
            return "Aucun champ valide.", None
    except Exception as e:  # noqa: BLE001
        log.exception("exécution ordre échouée")
        return f"Erreur technique : {e}", None
    return "Outil inconnu.", None


def run_order(merchant: dict, order_text: str) -> dict:
    """Exécute un ordre du commerçant. Retourne {reply, actions:[...]}."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    merchant_id = merchant["id"]

    products = list_products(merchant_id)
    system = [{"type": "text", "text": _system(merchant, products),
               "cache_control": {"type": "ephemeral"}}]
    messages = [{"role": "user", "content": order_text}]
    actions: list[str] = []

    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model_config.model_for("manager"), max_tokens=model_config.tokens_for("manager", 500),
            system=system, messages=messages, tools=TOOLS,
        )
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
            return {"reply": text or "C'est fait.", "actions": actions}

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            note, human = _exec_tool(merchant_id, tu.name, dict(tu.input or {}))
            if human:
                actions.append(human)
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": note})
        messages.append({"role": "user", "content": results})

    # Dernier tour sans outil pour conclure proprement.
    resp = client.messages.create(
        model=model_config.model_for("manager"), max_tokens=model_config.tokens_for("manager", 400), system=system, messages=messages,
    )
    text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
    return {"reply": text or "C'est fait.", "actions": actions}
