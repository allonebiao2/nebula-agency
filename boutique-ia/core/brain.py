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
from core import capabilities, model_config

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
            "total": {"type": "number", "description": "Total à payer en F CFA (négocié si négociation), livraison comprise."},
            "mode_livraison": {"type": "string", "enum": ["livraison", "retrait"]},
            "adresse": {"type": "string", "description": "Adresse de livraison (si livraison)."},
            "paiement": {"type": "string", "enum": ["mobile_money", "à_la_livraison"],
                          "description": "Comment le client paie : Mobile Money (avance) ou à la livraison."},
            "nom_client": {"type": "string", "description": "Nom du client s'il est connu."},
        },
        "required": ["articles", "total", "mode_livraison"],
    },
}

# Outil d'escalade : prévenir le/la propriétaire quand un humain est nécessaire
# (lead chaud, négociation, réclamation, demande spéciale).
ESCALATE_TOOL = {
    "name": "alerter_le_patron",
    "description": (
        "Prévient immédiatement le/la propriétaire de la boutique qu'un client a besoin "
        "de son attention humaine. À appeler quand : le client est TRÈS intéressé mais "
        "hésite/veut négocier, fait une réclamation, demande quelque chose hors catalogue "
        "ou hors de tes capacités, ou demande explicitement à parler au responsable. "
        "Après l'appel, rassure le client en lui disant que la boutique va le recontacter. "
        "N'en abuse pas : seulement quand c'est vraiment utile."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "raison": {"type": "string", "description": "Type : lead chaud, négociation, réclamation, demande spéciale…"},
            "resume": {"type": "string", "description": "Résumé en 1 phrase de ce que veut le client."},
            "nom_client": {"type": "string", "description": "Nom du client si connu."},
        },
        "required": ["raison", "resume"],
    },
}

# Outil photo : envoyer la photo d'un/des produit(s) au client (WhatsApp).
SHOW_TOOL = {
    "name": "montrer_produit",
    "description": (
        "Envoie la PHOTO d'un ou plusieurs produits au client. À appeler quand le client "
        "demande à voir un produit (« montre-moi », « tu as une photo ? », « ça ressemble à quoi ? ») "
        "ET que le produit a une photo disponible (indiqué par [photo] dans le catalogue). "
        "Donne les noms EXACTS des produits. Continue ta réponse normalement après."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "produits": {"type": "array", "items": {"type": "string"},
                          "description": "Noms exacts des produits dont envoyer la photo."},
        },
        "required": ["produits"],
    },
}


# Outil rendez-vous : enregistrer une demande de RDV (capacité « rdv », Business+).
RDV_TOOL = {
    "name": "enregistrer_rendezvous",
    "description": (
        "Enregistre une demande de RENDEZ-VOUS et prévient le/la propriétaire. À appeler "
        "quand le client veut prendre rendez-vous (consultation, prestation, visite) ET "
        "qu'il a indiqué ce qu'il souhaite + un moment qui lui convient (jour + heure). "
        "Propose toujours un créneau DANS les disponibilités de la boutique. Appelle l'outil "
        "une seule fois, puis confirme au client que la boutique va valider le créneau."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "service": {"type": "string", "description": "Prestation / motif du rendez-vous."},
            "date_souhaitee": {"type": "string", "description": "Jour + heure souhaités (ex : samedi 14h)."},
            "nom_client": {"type": "string", "description": "Nom du client s'il est connu."},
            "telephone": {"type": "string", "description": "Téléphone/contact si donné."},
            "note": {"type": "string", "description": "Précision utile (lieu, à distance, remarque)."},
        },
        "required": ["date_souhaitee"],
    },
}


# Outil paiement : le client annonce avoir payé (Mobile Money) → preuve à valider.
PAYMENT_TOOL = {
    "name": "enregistrer_paiement",
    "description": (
        "Enregistre que le client DIT avoir PAYÉ par Mobile Money et transmet la preuve "
        "au/à la propriétaire pour validation. À appeler quand le client confirme avoir "
        "envoyé l'argent ET donne une référence : l'ID/numéro de transaction du SMS MoMo "
        "(et son réseau si possible : MTN, Moov, Celtis…). Appelle-le UNE seule fois, puis "
        "remercie le client et dis-lui que la boutique vérifie et confirme. N'invente JAMAIS "
        "une référence : si le client n'en donne pas, demande-la-lui gentiment."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "transaction_id": {"type": "string", "description": "Référence/ID de la transaction MoMo donnée par le client."},
            "reseau": {"type": "string", "description": "Réseau Mobile Money (MTN, Moov, Celtis, Wave…) si connu."},
            "montant": {"type": "number", "description": "Montant payé en F CFA si précisé."},
        },
        "required": ["transaction_id"],
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


def build_system_prompt(merchant: dict, products: list[dict],
                        lessons: str | None = None,
                        caps: set[str] | None = None) -> str:
    """Construit la personnalité + les connaissances du vendeur IA.

    `lessons` : leçons de vente apprises automatiquement (cerveau d'apprentissage,
    cf. core/learning.py) — réinjectées pour que l'agent s'améliore avec l'expérience
    collective de toutes les boutiques.
    `caps` : capacités actives de la boutique (cf. core/capabilities). Si None, on
    les calcule depuis la fiche. Pilote COD, marchandage, photos, RDV.
    """
    if caps is None:
        caps = capabilities.effective_capabilities(merchant)
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

    cod_enabled = "cod" in caps
    negociation_on = "negociation" in caps
    photos_on = "photos" in caps
    rdv_on = "rdv" in caps
    negociation_rule = (merchant.get("negotiation_rule") or "").strip()

    # Fiche enrichie : identité, positionnement, arguments → l'agent connaît le business.
    def _f(key: str) -> str:
        return (merchant.get(key) or "").strip()

    _identite = [
        ("Depuis", _f("founded")),
        ("Positionnement / gamme", _f("price_range")),
        ("Présence", _f("presence")),
        ("Ce qui rend la boutique unique", _f("unique_selling")),
        ("Produits phares / best-sellers", _f("bestsellers")),
        ("Promo / offre du moment", _f("promotions")),
        ("Clientèle cible", _f("target_audience")),
        ("Occasions d'achat", _f("occasions")),
        ("Paiements acceptés", _f("payment_methods")),
        ("Réseaux sociaux", _f("socials")),
    ]
    _vente = [
        ("Arguments à mettre en avant", _f("selling_points")),
        ("Réassurance / garanties", _f("guarantees")),
        ("Objections fréquentes & comment y répondre", _f("objections")),
    ]
    _id_lines = "\n".join(f"- {k} : {v}" for k, v in _identite if v)
    _vente_lines = "\n".join(f"- {k} : {v}" for k, v in _vente if v)
    _avoid = _f("avoid_topics")
    identite_block = (f"\n\n# Identité & positionnement de la boutique\n{_id_lines}"
                      if _id_lines else "")
    vente_block = ""
    if _vente_lines or _avoid:
        vente_block = "\n\n# Pour bien vendre cette boutique (applique-le avec finesse)\n"
        if _vente_lines:
            vente_block += _vente_lines + "\n"
        if _avoid:
            vente_block += f"- À NE JAMAIS dire ni promettre : {_avoid}\n"

    # Catalogue produits
    if products:
        lines = []
        for p in products:
            if p.get("available") is False:
                continue
            kind = (p.get("kind") or "").strip()
            prefix = "Service" if kind == "service" else None
            label = f"{prefix} — " if prefix else ""
            line = f"- {label}{p.get('name')} : {_format_price(p.get('price'))}"
            if p.get("duration"):
                line += f" ({p['duration']})"
            if p.get("description"):
                line += f" — {p['description']}"
            if p.get("options"):
                line += f" [options : {p['options']}]"
            if photos_on and p.get("photo_url"):
                line += " [photo]"
            lines.append(line)
        catalogue = "\n".join(lines) if lines else "(aucun produit disponible pour le moment)"
    else:
        catalogue = "(catalogue vide pour le moment)"

    # Instructions de paiement Mobile Money (manuel) — un ou PLUSIEURS comptes (par réseau)
    pay_accounts: list[dict] = []
    if momo_number:
        pay_accounts.append({"network": momo_network, "number": momo_number, "name": momo_name})
    for a in (merchant.get("payment_accounts") or []):
        if a.get("number"):
            pay_accounts.append({"network": a.get("network") or "", "number": a.get("number"),
                                 "name": a.get("name") or ""})

    def _acct_line(a: dict) -> str:
        who = f" ({a['name']})" if a.get("name") else ""
        return f"  • {a.get('network') or 'Mobile Money'} : {a['number']}{who}\n"

    if pay_accounts:
        if len(pay_accounts) == 1:
            intro = "Quand un client veut payer, donne-lui ces instructions Mobile Money :\n"
        else:
            intro = ("Quand un client veut payer, demande-lui D'ABORD son réseau Mobile Money, puis "
                     "donne UNIQUEMENT le compte de SON réseau (s'il n'y est pas, propose le plus pratique) :\n")
        paiement = (
            intro
            + "".join(_acct_line(a) for a in pay_accounts)
            + "  • Puis t'envoyer la CAPTURE ou la référence du SMS de confirmation\n"
            "Après réception de la preuve, remercie le client et dis-lui que la boutique "
            "valide et prépare sa commande."
        )
    else:
        paiement = (
            "Si un client veut payer, demande-lui de patienter : la boutique le contactera "
            "pour le paiement (le numéro Mobile Money n'est pas encore configuré)."
        )

    if cod_enabled:
        paiement += (
            "\n\nPAIEMENT À LA LIVRAISON disponible ✅ : le client peut payer EN RECEVANT sa "
            "commande. Mets bien cette option en avant pour rassurer les hésitants (ils ne "
            "paient qu'à la réception). Dans ce cas, pas de preuve de paiement à l'avance : "
            "confirme juste la commande + l'adresse. Demande au client s'il préfère payer "
            "maintenant (Mobile Money) ou à la livraison."
        )

    if negociation_on:
        negociation = (
            "Tu peux NÉGOCIER le prix TOI-MÊME, mais STRICTEMENT dans cette limite fixée par la "
            f"boutique : « {negociation_rule or 'une petite remise raisonnable'} ». "
            "Ne descends JAMAIS en dessous de cette limite. Négocie avec le sourire, comme un "
            "bon vendeur au marché ; ne lâche une remise que si le client hésite vraiment, et "
            "annonce clairement le prix final convenu avant d'enregistrer la commande. "
            "N'alerte PAS le/la propriétaire juste pour négocier : gère-le toi-même. "
            "N'alerte que si le client EXIGE un prix SOUS ta limite."
        )
    else:
        negociation = (
            "Tu ne baisses PAS les prix. Si le client marchande, reste chaleureux et justifie "
            "la valeur (qualité, service, livraison) avec le sourire, sans céder sur le prix."
        )

    # Rendez-vous (capacité « rdv ») — l'agent propose et enregistre des RDV.
    rdv_block = ""
    if rdv_on:
        days = (merchant.get("rdv_days") or "").strip()
        hrs = (merchant.get("rdv_hours") or "").strip()
        rnote = (merchant.get("rdv_note") or "").strip()
        dispo = []
        if days:
            dispo.append(f"jours : {days}")
        if hrs:
            dispo.append(f"horaires : {hrs}")
        if rnote:
            dispo.append(rnote)
        dispo_txt = (" — ".join(dispo) if dispo
                     else "demande au client ses disponibilités et propose un créneau adapté")
        rdv_block = (
            "\n\n# Rendez-vous\n"
            f"Tu peux PRENDRE DES RENDEZ-VOUS pour la boutique. Disponibilités : {dispo_txt}.\n"
            "Propose un créneau DANS ces disponibilités (jamais en dehors). Quand le client "
            "choisit un jour + une heure, appelle l'outil « enregistrer_rendezvous » UNE seule "
            "fois, puis confirme-lui chaleureusement que la boutique valide le créneau et le "
            "recontacte pour confirmer."
        )

    # Leçons de vente apprises (cerveau d'apprentissage) — réinjectées si présentes.
    lessons_block = ""
    if lessons and lessons.strip():
        lessons_block = (
            "\n\n# Leçons de vente apprises (tirées de vraies conversations — applique-les)\n"
            + lessons.strip()
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

# Prix & négociation
{negociation}{rdv_block}

# Règles de la boutique
{policies or "(aucune règle particulière)"}

# Infos utiles
{extra or "(rien de plus)"}{identite_block}{vente_block}

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
- Tu REÇOIS toujours le message du client. Ne dis JAMAIS que tu ne reçois pas / n'as pas reçu / ne vois pas son message — ce serait faux et ça casse la confiance. Si un message est vague, très court ou peu clair, NE prétends pas à un souci technique : relance avec le sourire par une question utile qui fait avancer la vente (ex : « Vous cherchez plutôt un collier ou des boucles ? » ou propose un produit phare).

# Tes talents de vendeur (applique-les avec finesse, jamais lourdement)
- VENDS, ne te contente pas de répondre : ton objectif est de conclure la vente, en douceur.
- Parle BÉNÉFICES, pas seulement caractéristiques (« sublime votre tenue », « cadeau qui marque »).
- Propose intelligemment un produit complémentaire ou une quantité supérieure (upsell/cross-sell), quand c'est pertinent.
- Rassure et lève les objections (prix, livraison, confiance) avec des arguments simples et honnêtes.
- Crée une envie ou une légère urgence UNIQUEMENT si c'est vrai (ex : pièce unique faite main). Ne mens jamais sur le stock.
- Utilise une preuve sociale légère si c'est crédible (« nos clientes adorent ce modèle »).
- Termine TOUJOURS par une question ou une proposition claire qui fait avancer vers l'achat (CTA).
- Reste respectueux : si le client hésite, accompagne-le, ne le harcèle pas.
- REMERCIE toujours, chaleureusement et sincèrement, dès qu'une commande, un rendez-vous ou un paiement est conclu : nomme le client si tu connais son nom, valorise son choix et rassure-le sur la suite (ex : « Merci infiniment pour votre confiance 🙏 on prépare ça et on revient vers vous très vite ! »). Un client remercié et bien traité revient et parle de la boutique autour de lui.{lessons_block}
"""


def followup_message(merchant: dict, products: list[dict], history: list[dict],
                     lessons: str | None = None, kind: str = "silent",
                     hours: int | None = None) -> str:
    """Rédige UN message de relance (le client n'a pas répondu / n'a pas payé).

    Utilise la fiche de la boutique + les leçons apprises pour relancer dans le bon
    ton, avec une légère urgence honnête. Un seul message court, sans outil.
    `kind` : 'silent' (devis sans réponse) | 'cart' (commande non payée).
    """
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_text = build_system_prompt(merchant, products, lessons=lessons)
    messages = _to_anthropic_messages(history) or [{"role": "user", "content": "Bonjour"}]

    delai = f" (cela fait environ {hours}h)" if hours else ""
    if kind == "cart":
        consigne = (
            f"INSTRUCTION INTERNE (ne pas mentionner ceci au client) : le client a confirmé "
            f"sa commande mais n'a pas encore réglé{delai}. Écris UN SEUL message WhatsApp court "
            "et chaleureux pour l'aider à finaliser le paiement, rappelle brièvement ce qui est "
            "réservé pour lui, rassure (paiement simple, ou à la livraison si dispo), et propose "
            "de l'accompagner. Légère urgence honnête, jamais de pression. 2-3 lignes."
        )
    else:
        consigne = (
            f"INSTRUCTION INTERNE (ne pas mentionner ceci au client) : le client s'est montré "
            f"intéressé puis n'a plus répondu{delai}. Écris UN SEUL message WhatsApp court et "
            "naturel pour relancer la conversation, lever sa dernière hésitation et l'inviter à "
            "avancer vers l'achat. Reprends le fil de l'échange (le produit dont il parlait). "
            "Légère urgence honnête si c'est vrai (ex: pièce qui part vite). 2-3 lignes, 1 emoji max."
        )
    # On termine sur un tour "user" → le modèle produit le message de relance (assistant).
    messages = messages + [{"role": "user", "content": consigne}]

    system = [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]
    resp = client.messages.create(
        model=model_config.model_for("vendeur"),
        max_tokens=model_config.tokens_for("vendeur", 300), system=system, messages=messages,
    )
    return _text_of(resp)


def email_reply(merchant: dict, products: list[dict], thread: list[dict],
                lessons: str | None = None) -> str:
    """Rédige la réponse EMAIL d'une boutique à un prospect qui a répondu.

    `thread` = fil [{direction:'in'|'out', body}] du plus ancien au récent. L'agent
    vend les produits/services de la boutique, répond à la question/objection, et
    pousse vers l'achat/la commande. Texte email (un peu plus posé que WhatsApp),
    signé du nom de la boutique. Retourne le corps en texte brut.
    """
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_text = build_system_prompt(merchant, products, lessons=lessons)
    msgs = []
    for m in thread:
        role = "user" if m.get("direction") == "in" else "assistant"
        body = (m.get("body") or "").strip()
        if body:
            msgs.append({"role": role, "content": body})
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    if not msgs:
        msgs = [{"role": "user", "content": "Bonjour, j'ai vu votre message."}]

    name = merchant.get("business_name") or "la boutique"
    consigne = (
        "INSTRUCTION INTERNE (ne pas mentionner ceci) : tu réponds par EMAIL à ce "
        "prospect professionnel. Réponds précisément à sa question/objection, mets en "
        "avant ce qui l'intéresse dans notre offre, et propose une étape concrète "
        "(commande, devis, rendez-vous). Ton chaleureux et professionnel, 4-6 phrases, "
        f"sans jargon. Termine par une signature simple « — {name} ». Écris UNIQUEMENT "
        "le corps de l'email (pas d'objet)."
    )
    msgs = msgs + [{"role": "user", "content": consigne}]
    system = [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]
    resp = client.messages.create(
        model=model_config.model_for("vendeur"),
        max_tokens=model_config.tokens_for("vendeur", 500), system=system, messages=msgs,
    )
    return _text_of(resp) or f"Merci pour votre message ! Dites-nous comment nous pouvons vous aider. — {name}"


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
    on_escalate: Callable[[dict], None] | None = None,
    on_show: Callable[[dict], str] | None = None,
    on_appointment: Callable[[dict], None] | None = None,
    on_payment: Callable[[dict], None] | None = None,
    lessons: str | None = None,
) -> str:
    """Génère la réponse du vendeur IA. `history` doit finir par le message client.

    `on_order` : callback quand l'agent conclut une vente (enregistre + alerte).
    `on_escalate` : callback quand l'agent juge qu'un humain est nécessaire
    (lead chaud, négociation, réclamation) → alerte le commerçant.
    `lessons` : leçons de vente apprises (cerveau d'apprentissage) à réinjecter.
    """
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    caps = capabilities.effective_capabilities(merchant)
    system_text = build_system_prompt(merchant, products, lessons=lessons, caps=caps)
    messages = _to_anthropic_messages(history)
    if not messages:
        # Pas de message client exploitable → réponse d'accueil par défaut
        messages = [{"role": "user", "content": "Bonjour"}]

    system = [{
        "type": "text",
        "text": system_text,
        "cache_control": {"type": "ephemeral"},  # cache la fiche (réutilisée à chaque tour)
    }]

    # Outils selon les capacités de la boutique (photo/RDV offerts seulement si activés).
    tools = [ORDER_TOOL, ESCALATE_TOOL, PAYMENT_TOOL]
    if "photos" in caps:
        tools.append(SHOW_TOOL)
    if "rdv" in caps:
        tools.append(RDV_TOOL)

    did_tool = False
    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model_config.model_for("vendeur"),
            max_tokens=model_config.tokens_for("vendeur", 500),  # WhatsApp court · ajusté par l'effort
            system=system,
            messages=messages,
            tools=tools,
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
                    "au client en 2-3 lignes WhatsApp : s'il paie en Mobile Money, donne "
                    "les instructions ; s'il paie à la livraison, confirme simplement que "
                    "la commande est prise et sera livrée.")
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
            elif tu.name == "alerter_le_patron":
                if on_escalate:
                    try:
                        on_escalate(dict(tu.input or {}))
                    except Exception:  # noqa: BLE001
                        log.exception("escalade échouée")
                note = ("Le/la propriétaire est prévenu(e). Rassure le client : la boutique "
                        "va le recontacter très vite. Reste utile en attendant.")
            elif tu.name == "enregistrer_paiement":
                if on_payment:
                    try:
                        on_payment(dict(tu.input or {}))
                        note = ("Paiement signalé et propriétaire prévenu pour validation. "
                                "Remercie le client, confirme que tu as bien noté sa référence, "
                                "et dis que la boutique vérifie puis confirme la commande très vite.")
                    except Exception:  # noqa: BLE001
                        log.exception("enregistrement paiement échoué")
                        note = ("Impossible d'enregistrer le paiement maintenant — remercie le "
                                "client et dis que la boutique vérifie manuellement.")
                else:
                    note = ("Paiement noté (mode démo, non enregistré). Remercie le client et "
                            "dis que la boutique valide puis confirme la commande.")
            elif tu.name == "montrer_produit":
                if on_show:
                    try:
                        note = on_show(dict(tu.input or {}))
                    except Exception:  # noqa: BLE001
                        log.exception("envoi photo échoué")
                        note = "Photo indisponible pour l'instant — décris le produit au client."
                else:
                    note = ("Photo non envoyable ici (mode démo). Sur WhatsApp elle serait "
                            "envoyée ; décris le produit au client.")
            elif tu.name == "enregistrer_rendezvous":
                if on_appointment:
                    try:
                        on_appointment(dict(tu.input or {}))
                        note = ("Rendez-vous enregistré et propriétaire prévenu. Confirme au "
                                "client en 2-3 lignes : le créneau souhaité est bien noté, la "
                                "boutique valide et le recontacte pour confirmer. Reste chaleureux.")
                    except Exception:  # noqa: BLE001
                        log.exception("enregistrement RDV échoué")
                        note = ("Impossible d'enregistrer le RDV pour l'instant — propose au "
                                "client de réessayer ou transmets sa demande au/à la propriétaire.")
                else:
                    note = ("RDV noté (mode démo, non enregistré). Confirme au client que la "
                            "boutique validera le créneau et le recontactera.")
            else:
                note = "Outil inconnu, ignore-le."
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": note})
        messages.append({"role": "user", "content": results})

    # Sécurité : on a épuisé les tours d'outil → demande un dernier message texte.
    resp = client.messages.create(
        model=model_config.model_for("vendeur"),
        max_tokens=model_config.tokens_for("vendeur", 500),
        system=system,
        messages=messages,
    )
    # Si l'agent reste muet après avoir enregistré la commande, on confirme nous-mêmes.
    return _text_of(resp) or (_fallback_after_order(merchant) if did_tool else "…")
