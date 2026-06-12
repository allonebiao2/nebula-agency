"""SUPPORT CLIENT IN-APP — l'IA Vendora aide le COMMERÇANT (client de Vendora).

Différent du vendeur (parle aux clients du commerçant), du manager (exécute les
ordres) et de l'assistant (rapports/agenda). Ici, Vendora répond aux questions et
soucis du commerçant SUR la plateforme (onglet Support de son back-office) :
« comment ça marche », « mon agent ne répond pas », facturation, « où est mon
lien », etc. Quand c'est un VRAI problème (bug, panne, réclamation, remboursement,
insatisfaction, hors de sa portée), l'IA RASSURE le commerçant ET prévient Mongazi.

Auto-amélioration : chaque problème est enregistré (bia_support kind='problem') et
les problèmes RÉCENTS sont réinjectés ici pour que le support s'améliore et évite
que les mêmes soucis se répètent. Mongazi peut reprendre la main à tout moment.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

import anthropic

from config import settings
from core import model_config, usage

log = logging.getLogger("boutique-ia.support")

MAX_TOOL_TURNS = 3
WAT = timezone(timedelta(hours=1))

# Outil d'escalade : prévenir NEBULA d'un vrai problème + le tracer dans le cerveau.
PROBLEM_TOOL = {
    "name": "signaler_probleme",
    "description": (
        "Signale un VRAI problème à l'équipe NEBULA (Mongazi) et l'enregistre. À appeler "
        "quand le commerçant rencontre un bug/une panne, fait une réclamation, est mécontent, "
        "demande un remboursement, ou pose une demande que tu ne peux pas résoudre seul. "
        "Après l'appel, RASSURE le commerçant : l'équipe est prévenue et revient vers lui. "
        "N'abuse pas : seulement pour les vrais soucis, pas pour une simple question."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "categorie": {"type": "string", "description": "bug / panne / facturation / réclamation / remboursement / autre"},
            "resume": {"type": "string", "description": "Le problème en 1 phrase claire."},
        },
        "required": ["resume"],
    },
}

# Connaissances Vendora injectées (factuel, à jour) — le support s'appuie dessus.
_VENDORA_FACTS = """# Ce qu'est Vendora (pour bien aider)
- Vendora = un agent vendeur doté d'IA qui répond aux clients de la boutique sur WhatsApp 24h/24 et prend les commandes.
- Le commerçant partage SON lien WhatsApp / SON QR code (dans l'onglet « Votre agent WhatsApp ») ; ses clients écrivent, l'agent vend.
- Back-office (onglets) : Votre agent WhatsApp (lien + QR), Piloter mon agent (donner des ordres en langage simple : « ajoute un sac à 15000 », « mets X en rupture »), Assistant (rapports/agenda perso), Notifications, Validation des paiements (confirmer/rejeter les paiements Mobile Money des clients), Produits, Capacités (« composez votre vendeur » : activer photos, paiement à la livraison, marchandage, relances, rendez-vous, réseaux… selon le forfait), Infos, Livraison, Style, Coach, Réseaux, Forfait.
- Forfaits (abonnement mensuel) : Démarrage 5 000 F, Business 15 000 F, Empire 40 000 F. Essai gratuit 3 jours possible. Paiement par Mobile Money au numéro de NEBULA, validé par l'équipe ; l'agent vend tant que l'abonnement est actif.
- Conversations clients incluses par mois selon le forfait (rechargeables en crédits) ; le vendeur ne s'arrête jamais en cours de route.
- Accès au back-office : lien privé personnel + code d'accès secret (créé à la 1re visite).

# Mode SUPPORT (en plus de la vente — à connaître et à proposer)
- En plus de VENDRE, l'agent Vendora peut faire du SUPPORT CLIENT. Le commerçant le choisit à l'inscription ou dans l'onglet « Mode Support » du back-office.
- En mode support, l'agent répond aux QUESTIONS des utilisateurs 24h/24, UNIQUEMENT à partir d'une base de connaissances (FAQ collée + import de PDF + lecture automatique du site web), sur WhatsApp ET via un bouton de chat « Discuter avec nous » à coller sur le site du client.
- Quand il ne sait pas, ou face à une plainte, il n'invente jamais : il escalade (crée un ticket + prévient le patron avec le problème et le contact).
- Un rapport résume les questions récurrentes, propose les corrections à faire, et résume les visiteurs venus.
- Forfaits : le support de BASE (WhatsApp + FAQ + escalade) est inclus dans TOUS les forfaits ; le widget site, l'import PDF, la lecture de site et le rapport sont réservés aux forfaits Business et Empire.
- Idéal pour : les SaaS, sites, services, formateurs, écoles, organisateurs d'événements — tous ceux qui reçoivent beaucoup de questions.

# Dépannages fréquents (guide le commerçant pas à pas, gentiment)
- « Mon agent ne répond pas » → vérifier : la boutique est-elle active (abonnement payé / essai en cours) ? le client a-t-il bien ouvert LE lien/QR de la boutique ? le numéro WhatsApp où les clients écrivent est-il renseigné (onglet « Votre agent WhatsApp ») ?
- « Comment ajouter/modifier un produit » → onglet « Piloter mon agent », écrire en langage simple ; ou l'onglet Produits.
- « Où est mon lien / mon QR » → onglet « Votre agent WhatsApp » (bouton Copier / Télécharger le QR).
- « Comment encaisser » → le client paie en Mobile Money sur le numéro du commerçant et envoie la preuve ; le commerçant confirme dans l'onglet Validation.
- Facturation / changer de forfait / recharger des conversations → expliquer simplement ; si ça bloque ou demande une action de l'équipe, signaler le problème."""


def _system(merchant: dict, known_issues: str = "") -> str:
    name = merchant.get("business_name") or "la boutique"
    plan = merchant.get("plan") or "—"
    status = merchant.get("status") or "—"
    issues_block = ""
    if known_issues.strip():
        issues_block = (
            "\n\n# Problèmes déjà signalés récemment (sois PROACTIF, évite qu'ils se répètent)\n"
            + known_issues.strip()
        )
    return f"""Tu es le SUPPORT CLIENT de Vendora. Tu aides « {name} » (un commerçant qui utilise
Vendora) à se servir de la plateforme et à résoudre ses soucis. Tu réponds DANS l'espace du
commerçant (onglet Support). Forfait : {plan}. Statut boutique : {status}.

Ton rôle :
- Réponds avec EMPATHIE, clarté et patience. Rassure toujours. Le commerçant n'est pas technique.
- Aide concrètement : explique étape par étape, dis exactement sur quel onglet aller.
- Pour un VRAI problème (bug, panne, réclamation, mécontentement, remboursement, ou tout ce que
  tu ne peux pas résoudre seul) : appelle l'outil « signaler_probleme » pour prévenir l'équipe
  NEBULA, PUIS rassure le commerçant (« c'est noté, l'équipe est prévenue et revient vers vous »).
- Ne promets jamais ce dont tu n'es pas sûr (délais, remboursements). Reste honnête. Si tu ne sais
  pas, dis-le et signale le problème plutôt que d'inventer.
- Messages clairs et chaleureux, sans jargon. Pas de markdown lourd.

{_VENDORA_FACTS}{issues_block}"""


def support_reply(merchant: dict, question: str, history: list[dict] | None = None,
                  known_issues: str = "",
                  on_problem: Callable[[dict], None] | None = None) -> str:
    """Réponse du support IA au commerçant. `on_problem` : callback d'escalade."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system = [
        {"type": "text", "text": _system(merchant, known_issues),
         "cache_control": {"type": "ephemeral"}},
        # F1 — date volatile dans un 2e bloc NON caché (préserve le cache du 1er).
        {"type": "text",
         "text": f"Date du jour (Bénin) : {datetime.now(WAT):%d/%m/%Y %Hh%M}."},
    ]
    model = model_config.model_for("manager")
    messages: list[dict] = []
    for h in (history or [])[-10:]:
        role = "assistant" if h.get("role") in ("ai", "owner", "assistant") else "user"
        content = (h.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": (question or "").strip() or "Bonjour"})

    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model,
            max_tokens=model_config.tokens_for("manager", 600),
            system=system, messages=messages, tools=[PROBLEM_TOOL],
        )
        usage.track("support", model, resp, merchant.get("id"))  # F3 — mesure coût
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            text = "\n".join(b.text for b in resp.content
                             if getattr(b, "type", None) == "text").strip()
            return text or "Je suis là pour vous aider 🙂 Dites-moi tout."
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            if tu.name == "signaler_probleme" and on_problem:
                try:
                    on_problem(dict(tu.input or {}))
                except Exception:  # noqa: BLE001
                    log.exception("escalade support échouée")
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": ("Problème transmis à l'équipe NEBULA et enregistré. "
                                        "Rassure le commerçant : l'équipe est prévenue et revient "
                                        "vers lui rapidement.")})
        messages.append({"role": "user", "content": results})

    resp = client.messages.create(
        model=model,
        max_tokens=model_config.tokens_for("manager", 400),
        system=system, messages=messages,
    )
    usage.track("support", model, resp, merchant.get("id"))  # F3 — mesure coût
    text = "\n".join(b.text for b in resp.content
                     if getattr(b, "type", None) == "text").strip()
    return text or "Je suis là pour vous aider 🙂 Dites-moi tout."


def format_known_issues(problems: list[dict]) -> str:
    """Met en forme les problèmes récents pour le prompt (cerveau anti-répétition)."""
    lines = []
    for p in problems:
        c = (p.get("content") or "").strip().replace("\n", " ")
        if c:
            lines.append(f"- {c[:160]}")
    return "\n".join(lines)
