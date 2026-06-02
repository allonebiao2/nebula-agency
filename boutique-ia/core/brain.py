"""Le CERVEAU — transforme la fiche d'une boutique en vendeur IA WhatsApp.

Pour une boutique donnée, on construit un "system prompt" à partir de sa fiche
(produits, prix, ton, livraison, paiement) puis Claude répond aux clients comme
le ferait un excellent vendeur de cette boutique.

Testable sans WhatsApp via web/server.py : POST /api/chat.
"""
from __future__ import annotations

import logging
from typing import Callable

import anthropic

from config import settings

log = logging.getLogger("boutique-ia.brain")

# Combien de messages d'historique on garde en mémoire par conversation
HISTORY_LIMIT = 20

# Garde-fou anti-boucle : nb max d'allers-retours outil dans un même tour
MAX_TOOL_TURNS = 4

# Outil que le vendeur IA appelle quand une vente se conclut (étage 3)
ORDER_TOOL = {
    "name": "enregistrer_commande",
    "description": (
        "Enregistre une commande FERME dans le système de la boutique et prévient "
        "immédiatement le/la propriétaire. À appeler UNIQUEMENT quand le client a "
        "confirmé ce qu'il veut acheter : le(s) produit(s), la quantité, et le mode de "
        "réception (livraison ou retrait, plus l'adresse si livraison). Appelle cet "
        "outil AVANT de donner les instructions de paiement, et une SEULE fois par "
        "commande. N'invente jamais une commande que le client n'a pas confirmée."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "articles": {
                "type": "array",
                "description": "Les articles commandés.",
                "items": {
                    "type": "object",
                    "properties": {
                        "produit": {"type": "string", "description": "Nom exact du produit du catalogue."},
                        "quantite": {"type": "integer", "description": "Quantité commandée."},
                        "prix_unitaire": {"type": "number", "description": "Prix unitaire en F CFA."},
                    },
                    "required": ["produit", "quantite"],
                },
            },
            "total": {"type": "number", "description": "Total à payer en F CFA, livraison comprise."},
            "mode_livraison": {"type": "string", "enum": ["livraison", "retrait"]},
            "adresse": {"type": "string", "description": "Adresse de livraison (si livraison)."},
            "nom_client": {"type": "string", "description": "Nom du client s'il est connu."},
        },
        "required": ["articles", "total", "mode_livraison"],
    },
}


def _format_price(value) -> str:
    if value is None:
        return "prix sur demande"
    try:
        n = int(float(value))
        return f"{n:,}".replace(",", " ") + " F CFA"
    except (TypeError, ValueError):
        return str(value)


def build_system_prompt(merchant: dict, products: list[dict]) -> str:
    """Construit la personnalité + les connaissances du vendeur IA."""
    name = merchant.get("business_name") or "la boutique"
    sector = merchant.get("sector") or ""
    desc = merchant.get("description") or ""
    tone = merchant.get("ai_tone") or "chaleureux et professionnel"
    languages = merchant.get("languages") or "français"
    hours = merchant.get("business_hours") or ""
    policies = merchant.get("policies") or ""
    extra = merchant.get("extra_info") or ""
    city = merchant.get("city") or ""
    delivery_zones = merchant.get("delivery_zones") or ""
    delivery_fee = merchant.get("delivery_fee_info") or ""

    momo_number = merchant.get("momo_number") or ""
    momo_name = merchant.get("momo_name") or ""
    momo_network = merchant.get("momo_network") or ""

    # Catalogue produits
    if products:
        lines = []
        for p in products:
            if p.get("available") is False:
                continue
            line = f"- {p.get('name')} : {_format_price(p.get('price'))}"
            if p.get("description"):
                line += f" — {p['description']}"
            lines.append(line)
        catalogue = "\n".join(lines) if lines else "(aucun produit disponible pour le moment)"
    else:
        catalogue = "(catalogue vide pour le moment)"

    # Instructions de paiement Mobile Money (manuel)
    if momo_number:
        paiement = (
            f"Quand un client veut payer, donne-lui ces instructions Mobile Money :\n"
            f"  • Envoyer le montant au numéro {momo_network} : {momo_number} ({momo_name})\n"
            f"  • Puis t'envoyer la CAPTURE ou la référence du SMS de confirmation\n"
            f"Après réception de la preuve, remercie le client et dis-lui que la boutique "
            f"valide et prépare sa commande."
        )
    else:
        paiement = (
            "Si un client veut payer, demande-lui de patienter : la boutique le contactera "
            "pour le paiement (le numéro Mobile Money n'est pas encore configuré)."
        )

    return f"""Tu es le vendeur de la boutique « {name} »{f' ({sector})' if sector else ''}.
Tu réponds aux clients sur WhatsApp à la place du/de la propriétaire.

# Ta boutique
{desc or "(pas de description fournie)"}
{f"Ville : {city}" if city else ""}
{f"Horaires : {hours}" if hours else ""}

# Ton catalogue (NE JAMAIS inventer de produit ni de prix hors de cette liste)
{catalogue}

# Livraison
{f"Zones livrées : {delivery_zones}" if delivery_zones else "Demande au client où il se trouve."}
{f"Frais : {delivery_fee}" if delivery_fee else ""}

# Paiement
{paiement}

# Règles de la boutique
{policies or "(aucune règle particulière)"}

# Infos utiles
{extra or "(rien de plus)"}

# Style de réponse (TRÈS IMPORTANT)
- Ton : {tone}. Langue : {languages}.
- Tu écris sur WhatsApp : messages TRÈS COURTS, 2 à 4 lignes maximum, naturels et directs.
- N'utilise AUCUN markdown : jamais de **, jamais de #, jamais de longues listes à puces.
  Pour souligner un mot tu peux l'entourer d'UN seul astérisque, style WhatsApp (ex: *3 500 F*), avec parcimonie.
- Maximum 1 ou 2 emojis par message.
- Ne réénumère pas tout le catalogue à chaque message : montre seulement ce qui est pertinent.
- Chaque mot compte : va droit au but.

# Ce que tu fais
- Salue, comprends le besoin, propose le bon produit avec son prix.
- Commande : confirme produit + quantité, livraison ou retrait, puis l'adresse si livraison.
- Calcule le total (produits + livraison) et annonce-le avant le paiement.
- Dès que le client a CONFIRMÉ sa commande (produit + quantité + livraison/retrait + adresse si livraison),
  appelle l'outil « enregistrer_commande » pour la transmettre au propriétaire. Fais-le une seule fois,
  puis donne les instructions de paiement dans ta réponse au client.
- N'enregistre jamais une commande que le client n'a pas clairement confirmée.
- Jamais de produit ou prix hors catalogue. Si on te le demande, dis que tu vérifies avec la boutique.
- Cas délicat (réclamation, demande spéciale) → propose de transmettre au/à la propriétaire.
- Si tu ne sais pas, dis-le simplement. Ne mens jamais.

# Tes talents de vendeur (applique-les avec finesse, jamais lourdement)
- VENDS, ne te contente pas de répondre : ton objectif est de conclure la vente, en douceur.
- Parle BÉNÉFICES, pas seulement caractéristiques (« sublime votre tenue », « cadeau qui marque »).
- Propose intelligemment un produit complémentaire ou une quantité supérieure (upsell/cross-sell), quand c'est pertinent.
- Rassure et lève les objections (prix, livraison, confiance) avec des arguments simples et honnêtes.
- Crée une envie ou une légère urgence UNIQUEMENT si c'est vrai (ex : pièce unique faite main). Ne mens jamais sur le stock.
- Utilise une preuve sociale légère si c'est crédible (« nos clientes adorent ce modèle »).
- Termine TOUJOURS par une question ou une proposition claire qui fait avancer vers l'achat (CTA).
- Reste respectueux : si le client hésite, accompagne-le, ne le harcèle pas.
"""


def _to_anthropic_messages(history: list[dict]) -> list[dict]:
    """Convertit l'historique (role customer/assistant) en messages Anthropic."""
    msgs = []
    for h in history:
        role = "user" if h.get("role") == "customer" else "assistant"
        content = (h.get("content") or "").strip()
        if content:
            msgs.append({"role": role, "content": content})
    # L'API exige de commencer par un message "user" : on retire les assistants en tête
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    return msgs


def _text_of(resp) -> str:
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip()


def _fallback_after_order(merchant: dict) -> str:
    """Message de secours si l'agent enregistre la commande sans rien écrire au client."""
    momo_number = merchant.get("momo_number") or ""
    momo_name = merchant.get("momo_name") or ""
    momo_network = merchant.get("momo_network") or ""
    if momo_number:
        who = f" ({momo_name})" if momo_name else ""
        net = f"{momo_network} " if momo_network else ""
        return (
            "C'est noté, votre commande est enregistrée ✅\n"
            f"Pour payer, envoyez le montant au {net}{momo_number}{who}, "
            "puis envoyez-moi la capture ou la référence du SMS. Merci 🙏"
        )
    return (
        "C'est noté, votre commande est enregistrée ✅ "
        "La boutique vous contacte tout de suite pour le paiement. Merci 🙏"
    )


def reply(
    merchant: dict,
    products: list[dict],
    history: list[dict],
    on_order: Callable[[dict], None] | None = None,
) -> str:
    """Génère la réponse du vendeur IA. `history` doit finir par le message client.

    `on_order` : callback appelé avec les détails quand l'agent conclut une vente
    (enregistrement commande + alerte commerçant). Si None (mode démo/essai),
    l'agent confirme quand même au client mais rien n'est persisté.
    """
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_text = build_system_prompt(merchant, products)
    messages = _to_anthropic_messages(history)
    if not messages:
        # Pas de message client exploitable → réponse d'accueil par défaut
        messages = [{"role": "user", "content": "Bonjour"}]

    system = [{
        "type": "text",
        "text": system_text,
        "cache_control": {"type": "ephemeral"},  # cache la fiche (réutilisée à chaque tour)
    }]

    did_tool = False
    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=settings.claude_model,
            max_tokens=500,  # réponses WhatsApp courtes → tokens économisés
            system=system,
            messages=messages,
            tools=[ORDER_TOOL],
        )

        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            text = _text_of(resp)
            if text or not did_tool:
                return text or "…"
            # Une commande a été traitée mais l'agent n'a pas écrit au client :
            # on sort pour forcer un dernier message (confirmation + paiement).
            # `messages` se termine déjà sur le tool_result → prompt valide.
            break

        # L'agent veut enregistrer une (ou des) commande(s).
        did_tool = True
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            note = ("Commande enregistrée et propriétaire prévenu. Confirme maintenant "
                    "au client en 2-3 lignes WhatsApp et donne les instructions de "
                    "paiement Mobile Money.")
            if tu.name == "enregistrer_commande":
                if on_order:
                    try:
                        on_order(dict(tu.input or {}))
                    except Exception:  # noqa: BLE001
                        log.exception("enregistrement commande échoué")
                        note = ("Impossible d'enregistrer pour l'instant — continue "
                                "normalement et donne les instructions de paiement.")
                else:
                    note = ("Commande notée (mode démo, non enregistrée). Confirme au "
                            "client et donne les instructions de paiement Mobile Money.")
            else:
                note = "Outil inconnu, ignore-le."
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": note})
        messages.append({"role": "user", "content": results})

    # Sécurité : on a épuisé les tours d'outil → demande un dernier message texte.
    resp = client.messages.create(
        model=settings.claude_model,
        max_tokens=500,
        system=system,
        messages=messages,
    )
    # Si l'agent reste muet après avoir enregistré la commande, on confirme nous-mêmes.
    return _text_of(resp) or (_fallback_after_order(merchant) if did_tool else "…")
