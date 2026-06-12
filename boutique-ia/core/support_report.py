"""Vendora Support — rapport + détection des problèmes récurrents (lot 7).

Analyse les échanges support récents d'un client + ses tickets escaladés, et produit
un rapport COURT et actionnable pour le patron : volume, thèmes récurrents, plaintes,
et — le plus important — les **corrections suggérées** (quoi ajouter à la FAQ, clarifier,
ou corriger) pour que les mêmes problèmes ne reviennent plus.

Grounded : se base UNIQUEMENT sur les données fournies. Ne lève jamais.
"""
from __future__ import annotations

import logging

import anthropic

from config import settings
from core import model_config, usage

log = logging.getLogger("boutique-ia.support_report")

_SYS = """Tu es l'analyste support de Vendora. À partir des QUESTIONS récentes des
utilisateurs d'un business et des tickets escaladés, tu produis un rapport COURT, clair
et actionnable pour le patron (non technique). Structure :

1) Vue d'ensemble — volume et thèmes principaux, en 2-3 lignes.
2) Questions / sujets RÉCURRENTS — les plus fréquents (regroupe les similaires).
3) Plaintes ou points de friction éventuels.
4) CORRECTIONS SUGGÉRÉES (la partie la plus importante) — dis concrètement au patron
   quoi AJOUTER à sa FAQ, quoi CLARIFIER, ou quoi CORRIGER dans son produit/service
   pour que ces problèmes ne reviennent plus.
5) RÉSUMÉ DES PRINCIPAUX VISITEURS — à partir de la liste fournie, dis en quelques
   lignes qui est venu et ce que chacun voulait (regroupe les cas similaires).

Règles : n'invente RIEN (uniquement à partir des données fournies). Pas de markdown
lourd (pas de #, pas de **), des tirets simples. Ton direct, bienveillant et utile."""


def generate_report(merchant: dict) -> str:
    """Génère le rapport support (texte) pour un client. Ne lève jamais."""
    from db.client import list_support_tickets, recent_messages
    try:
        msgs = recent_messages(7, merchant_id=merchant["id"], limit=2000)
    except Exception:  # noqa: BLE001
        msgs = []
    questions = [(m.get("content") or "").strip() for m in msgs
                 if m.get("role") == "customer" and (m.get("content") or "").strip()]
    try:
        tickets = list_support_tickets(merchant["id"], None, 100)
    except Exception:  # noqa: BLE001
        tickets = []

    if len(questions) < 2 and not tickets:
        return ("Pas encore assez d'échanges cette semaine pour un rapport utile. "
                "Reviens quand ton agent aura discuté avec plus d'utilisateurs 🙂")

    q_block = "\n".join("- " + q[:220] for q in questions[:150]) or "(aucune)"
    t_block = "\n".join("- " + (t.get("summary") or "")[:180] for t in tickets[:50]) or "(aucun)"
    by_visitor: dict[str, list[str]] = {}
    for mrow in msgs:
        if mrow.get("role") != "customer":
            continue
        c = (mrow.get("content") or "").strip()
        if c:
            by_visitor.setdefault(mrow.get("customer_whatsapp") or "?", []).append(c)
    vis_block = "\n".join("- " + who + " : " + (" | ".join(qs))[:300]
                         for who, qs in list(by_visitor.items())[:25]) or "(aucun)"
    name = merchant.get("business_name") or "le business"
    user = (f"Business : {name}\n"
            f"Questions reçues (7 derniers jours) : {len(questions)}\n"
            f"Tickets escaladés : {len(tickets)}\n"
            f"Visiteurs distincts : {len(by_visitor)}\n\n"
            f"QUESTIONS DES UTILISATEURS :\n{q_block}\n\n"
            f"TICKETS ESCALADÉS :\n{t_block}\n\n"
            f"VISITEURS & CE QU'ILS ONT DEMANDÉ :\n{vis_block}")
    try:
        settings.require("anthropic_api_key")
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        model = model_config.model_for("writer")
        resp = client.messages.create(
            model=model, max_tokens=model_config.tokens_for("writer", 900),
            system=_SYS, messages=[{"role": "user", "content": user}],
        )
        usage.track("support_report", model, resp, merchant.get("id"))  # F3 — mesure coût
        txt = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
        return txt or "Rapport indisponible pour l'instant."
    except Exception:  # noqa: BLE001
        log.exception("rapport support échoué")
        return "Le rapport n'a pas pu être généré pour l'instant — réessaie dans un moment 🙏"
