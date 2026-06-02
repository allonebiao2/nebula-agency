"""Le CERVEAU — transforme la fiche d'une boutique en vendeur IA WhatsApp.

Pour une boutique donnée, on construit un "system prompt" à partir de sa fiche
(produits, prix, ton, livraison, paiement) puis Claude répond aux clients comme
le ferait un excellent vendeur de cette boutique.

Testable sans WhatsApp via web/server.py : POST /api/chat.
"""
from __future__ import annotations

import logging

import anthropic

from config import settings

log = logging.getLogger("boutique-ia.brain")

# Combien de messages d'historique on garde en mémoire par conversation
HISTORY_LIMIT = 20


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
- Donne ensuite les instructions de paiement Mobile Money.
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


def reply(merchant: dict, products: list[dict], history: list[dict]) -> str:
    """Génère la réponse du vendeur IA. `history` doit finir par le message client."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_text = build_system_prompt(merchant, products)
    messages = _to_anthropic_messages(history)
    if not messages:
        # Pas de message client exploitable → réponse d'accueil par défaut
        messages = [{"role": "user", "content": "Bonjour"}]

    resp = client.messages.create(
        model=settings.claude_model,
        max_tokens=400,  # réponses WhatsApp courtes → tokens économisés
        system=[{
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},  # cache la fiche (réutilisée à chaque tour)
        }],
        messages=messages,
    )
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip() or "…"
