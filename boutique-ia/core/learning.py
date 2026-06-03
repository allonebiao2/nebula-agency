"""Le CERVEAU D'APPRENTISSAGE — Vendora s'auto-améliore (intelligence collective).

Une fois par semaine, on relit les conversations récentes de TOUTES les boutiques,
on les croise avec les commandes (ventes CONCLUES vs PERDUES), puis un modèle
(Sonnet) en extrait des « leçons de vente » concrètes (accroches qui marchent,
réponses aux objections, moments de bascule). Ces leçons sont RÉINJECTÉES dans le
prompt des agents vendeurs (`brain.build_system_prompt`) → chaque nouvelle boutique
profite de l'expérience de toutes les autres. C'est le moat : + de boutiques →
meilleurs agents → encore + de boutiques.

Stockage : table `bia_lessons` (scope 'global' = collectif, scope 'merchant' = par
boutique). Lecture par `db.client.get_active_lessons()` (caché).

Déclenché par la boucle de fond (1×/semaine) ou manuellement depuis l'admin.
"""
from __future__ import annotations

import logging
from typing import Any

import anthropic

from config import settings

log = logging.getLogger("boutique-ia.learning")

# Fenêtre d'analyse (jours de conversations relus).
DEFAULT_WINDOW_DAYS = 14
# Un client doit avoir envoyé au moins ce nb de messages pour compter comme
# "engagé" (on ignore les contacts d'une seule ligne = bruit).
MIN_CUSTOMER_MSGS = 2
# Plafonds pour maîtriser le coût/temps du modèle.
MAX_CONVOS_GLOBAL = 24       # 12 conclues + 12 perdues max dans le digest global
MAX_CONVOS_MERCHANT = 16
MAX_MSGS_PER_CONVO = 14      # on garde les derniers échanges (le dénouement)
MAX_CHARS_PER_MSG = 200
# Une boutique doit avoir au moins ce nb de conversations engagées pour mériter
# ses propres leçons (sinon elle s'appuie sur le collectif).
MERCHANT_MIN_CONVOS = 8
# Nb max de boutiques analysées individuellement par cycle (coût maîtrisé).
MAX_MERCHANTS_PER_CYCLE = 8

# --- Déclencheur AUTONOME : le cerveau décide lui-même quand apprendre ---
# Garde-fous de cadence
TRIGGER_MIN_HOURS = 18      # jamais relancer avant ce délai (anti-gaspillage)
TRIGGER_MAX_DAYS = 14       # au-delà, on relance dès qu'il y a du nouveau (anti-obsolescence)
# Seuils de volume (matière nouvelle depuis la dernière analyse)
TRIGGER_NEW_MSGS = 40       # nb de messages clients nouveaux qui justifient d'apprendre
TRIGGER_NEW_ORDERS = 5      # ou ce nb de nouvelles ventes
# Urgence : baisse de conversion récente → apprendre tout de suite
URGENT_WINDOW_DAYS = 4
URGENT_MIN_CONVOS = 6       # il faut un minimum de volume pour que le signal soit fiable
URGENT_MAX_WIN_RATE = 0.25  # < 25 % de ventes parmi les clients engagés = problème


def should_learn(last_run_iso: str | None) -> tuple[bool, str]:
    """Le cerveau doit-il apprendre MAINTENANT ? Décision intelligente et peu coûteuse.

    Combine : volume de nouvelles conversations, urgence (chute de conversion),
    et garde-fous de cadence (mini 18h, maxi 14j). Retourne (oui/non, raison lisible).
    La raison est affichée à Mongazi (Telegram + cockpit) pour qu'il voie POURQUOI
    le cerveau a décidé d'apprendre.
    """
    from datetime import datetime, timezone

    from db.client import count_messages_since, count_orders_since, recent_messages, recent_orders

    if not last_run_iso:
        return True, "première analyse"
    try:
        prev = datetime.fromisoformat(str(last_run_iso).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True, "horodatage illisible — analyse de remise à niveau"

    elapsed_h = (datetime.now(timezone.utc) - prev).total_seconds() / 3600
    if elapsed_h < TRIGGER_MIN_HOURS:
        return False, ""  # garde-fou : trop tôt depuis la dernière fois

    new_msgs = count_messages_since(last_run_iso, role="customer")
    if new_msgs == 0:
        return False, ""  # rien de nouveau à apprendre
    new_orders = count_orders_since(last_run_iso)
    elapsed_days = elapsed_h / 24

    # 1) Garde-fou haut : ça fait longtemps et il y a du nouveau → on rafraîchit.
    if elapsed_days >= TRIGGER_MAX_DAYS:
        return True, f"analyse périodique ({new_msgs} nouveaux messages en {int(elapsed_days)}j)"

    # 2) Volume : assez de matière nouvelle pour apprendre quelque chose d'utile.
    if new_msgs >= TRIGGER_NEW_MSGS or new_orders >= TRIGGER_NEW_ORDERS:
        return True, f"assez de nouvelles conversations ({new_msgs} messages, {new_orders} ventes)"

    # 3) Urgence : la conversion récente chute → on apprend tout de suite pour corriger.
    try:
        convos = _build_conversations(
            recent_messages(URGENT_WINDOW_DAYS), recent_orders(URGENT_WINDOW_DAYS))
        engaged = len(convos)
        won = sum(1 for c in convos if c["won"])
        if engaged >= URGENT_MIN_CONVOS and (won / engaged) < URGENT_MAX_WIN_RATE:
            return True, (f"baisse de conversion détectée ({won}/{engaged} ventes "
                          f"sur {URGENT_WINDOW_DAYS}j) — apprentissage prioritaire")
    except Exception:  # noqa: BLE001
        log.warning("should_learn: contrôle d'urgence échoué", exc_info=True)

    return False, ""  # pas encore le bon moment


def _norm_phone(s: Any) -> str:
    import re
    return re.sub(r"\D", "", str(s or ""))


def _build_conversations(messages: list[dict], orders: list[dict]) -> list[dict]:
    """Reconstitue les conversations (boutique+client) et les classe conclue/perdue.

    Retourne une liste de dicts : {merchant_id, customer, msgs:[...], won:bool,
    revenue:float}. Seules les conversations « engagées » (>= MIN_CUSTOMER_MSGS
    messages client) sont conservées.
    """
    # Index des ventes : (merchant_id, téléphone normalisé) -> revenu cumulé
    won_revenue: dict[tuple[str, str], float] = {}
    for o in orders:
        key = (o.get("merchant_id"), _norm_phone(o.get("customer_whatsapp")))
        if not key[0] or not key[1]:
            continue
        try:
            won_revenue[key] = won_revenue.get(key, 0.0) + float(o.get("total") or 0)
        except (TypeError, ValueError):
            won_revenue.setdefault(key, 0.0)

    grouped: dict[tuple[str, str], list[dict]] = {}
    for m in messages:
        cust = m.get("customer_whatsapp")
        mid = m.get("merchant_id")
        if not mid or not cust:
            continue
        grouped.setdefault((mid, cust), []).append(m)

    convos = []
    for (mid, cust), msgs in grouped.items():
        n_customer = sum(1 for x in msgs if x.get("role") == "customer")
        if n_customer < MIN_CUSTOMER_MSGS:
            continue
        key = (mid, _norm_phone(cust))
        won = key in won_revenue
        convos.append({
            "merchant_id": mid,
            "customer": cust,
            "msgs": msgs,
            "won": won,
            "revenue": won_revenue.get(key, 0.0),
        })
    return convos


def _render_convo(convo: dict, label: str) -> str:
    """Rend une conversation en texte compact pour le digest envoyé au modèle."""
    msgs = convo["msgs"][-MAX_MSGS_PER_CONVO:]
    lines = [f"[{label}]"]
    for m in msgs:
        who = "Client" if m.get("role") == "customer" else "Vendeur"
        content = (m.get("content") or "").strip().replace("\n", " ")
        if len(content) > MAX_CHARS_PER_MSG:
            content = content[:MAX_CHARS_PER_MSG] + "…"
        if content:
            lines.append(f"{who}: {content}")
    return "\n".join(lines)


def _digest(convos: list[dict], cap: int, sector_by_merchant: dict[str, str] | None = None) -> str:
    """Construit le digest : un échantillon équilibré conclues/perdues."""
    won = [c for c in convos if c["won"]]
    lost = [c for c in convos if not c["won"]]
    half = max(1, cap // 2)
    sample = won[:half] + lost[: cap - len(won[:half])]
    blocks = []
    for c in sample:
        sector = ""
        if sector_by_merchant:
            s = sector_by_merchant.get(c["merchant_id"])
            sector = f" · {s}" if s else ""
        label = ("VENTE CONCLUE" if c["won"] else "VENTE PERDUE") + sector
        blocks.append(_render_convo(c, label))
    return "\n\n".join(blocks)


_SYSTEM_GLOBAL = (
    "Tu es analyste senior de la vente conversationnelle (commerce WhatsApp, "
    "Afrique de l'Ouest francophone). On te donne de VRAIES conversations entre "
    "des agents vendeurs et leurs clients, étiquetées VENTE CONCLUE ou VENTE PERDUE. "
    "Ta mission : en tirer des LEÇONS DE VENTE actionnables qui aideront les agents "
    "à conclure davantage.\n\n"
    "Compare ce qui marche (conclues) et ce qui échoue (perdues) : accroches, "
    "réponses aux objections (prix, confiance, livraison), moments de bascule, "
    "rythme, façon de proposer le paiement, relances. Sois concret et spécifique au "
    "terrain (Mobile Money, paiement à la livraison, marchandage, WhatsApp).\n\n"
    "Réponds en FRANÇAIS, UNIQUEMENT par 5 à 8 puces, une ligne chacune, commençant "
    "par « - », à l'impératif, sans titre ni intro ni conclusion. Chaque puce = une "
    "règle directement applicable par un vendeur (pas de généralités creuses). "
    "Pas de markdown autre que le tiret."
)

_SYSTEM_MERCHANT = (
    "Tu es analyste de la vente conversationnelle. On te donne les conversations "
    "d'UNE boutique précise ({name}{sector}), étiquetées VENTE CONCLUE / VENTE PERDUE. "
    "Tire 4 à 6 leçons SPÉCIFIQUES à cette boutique (ses produits, ses objections "
    "récurrentes, ce qui fait conclure ICI). Réponds en FRANÇAIS, uniquement par des "
    "puces « - » d'une ligne, à l'impératif, sans titre ni intro."
)


def _extract_lessons(system: str, digest: str) -> str:
    """Appel modèle → texte des leçons (puces). Vide si échec/insuffisant."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=settings.writer_model,
        max_tokens=900,
        system=system,
        messages=[{
            "role": "user",
            "content": "Voici les conversations à analyser :\n\n" + digest,
        }],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
    # On ne garde que les lignes-puces, par sécurité.
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip().startswith("-")]
    return "\n".join(lines).strip() or text[:1500]


def run_learning_cycle(days: int = DEFAULT_WINDOW_DAYS) -> dict[str, Any]:
    """Un cycle complet d'auto-amélioration. Retourne un résumé (stats)."""
    from db.client import (
        list_all_merchants,
        recent_messages,
        recent_orders,
        save_lessons,
    )

    messages = recent_messages(days)
    orders = recent_orders(days)
    convos = _build_conversations(messages, orders)

    merchants = {m["id"]: m for m in list_all_merchants()}
    sector_by_merchant = {
        mid: (m.get("sector") or "") for mid, m in merchants.items()
    }

    won = sum(1 for c in convos if c["won"])
    lost = len(convos) - won
    revenue = sum(c["revenue"] for c in convos if c["won"])

    result: dict[str, Any] = {
        "window_days": days,
        "conversations": len(convos),
        "won": won,
        "lost": lost,
        "revenue": revenue,
        "model": settings.writer_model,
        "global_updated": False,
        "merchants_analyzed": 0,
        "skipped": False,
    }

    # Pas assez de matière → on ne fabrique pas de leçons bidon.
    if len(convos) < 3:
        result["skipped"] = True
        result["reason"] = "Pas assez de conversations engagées pour apprendre."
        log.info("learning: skip (%d conversations)", len(convos))
        return result

    # 1) Leçons GLOBALES (intelligence collective)
    try:
        digest = _digest(convos, MAX_CONVOS_GLOBAL, sector_by_merchant)
        lessons = _extract_lessons(_SYSTEM_GLOBAL, digest)
        if lessons:
            save_lessons("global", None, lessons,
                         stats={"conversations": len(convos), "won": won,
                                "lost": lost, "revenue": revenue}, model=settings.writer_model)
            result["global_updated"] = True
            result["global_lessons"] = lessons
    except Exception:  # noqa: BLE001
        log.exception("learning: extraction globale échouée")

    # 2) Leçons PAR BOUTIQUE (pour celles qui ont assez de volume)
    by_merchant: dict[str, list[dict]] = {}
    for c in convos:
        by_merchant.setdefault(c["merchant_id"], []).append(c)
    # Les boutiques les plus actives d'abord (coût maîtrisé).
    ranked = sorted(by_merchant.items(), key=lambda kv: len(kv[1]), reverse=True)
    for mid, mconvos in ranked[:MAX_MERCHANTS_PER_CYCLE]:
        if len(mconvos) < MERCHANT_MIN_CONVOS:
            continue
        m = merchants.get(mid) or {}
        name = m.get("business_name") or "cette boutique"
        sector = m.get("sector")
        sys = _SYSTEM_MERCHANT.format(name=name, sector=f", {sector}" if sector else "")
        try:
            digest = _digest(mconvos, MAX_CONVOS_MERCHANT)
            lessons = _extract_lessons(sys, digest)
            if lessons:
                mw = sum(1 for c in mconvos if c["won"])
                save_lessons("merchant", mid, lessons,
                             stats={"conversations": len(mconvos), "won": mw,
                                    "lost": len(mconvos) - mw}, model=settings.writer_model)
                result["merchants_analyzed"] += 1
        except Exception:  # noqa: BLE001
            log.warning("learning: extraction boutique %s échouée", mid, exc_info=True)

    log.info("learning: %d convos (%d conclues / %d perdues), global=%s, boutiques=%d",
             len(convos), won, lost, result["global_updated"], result["merchants_analyzed"])
    return result


def merchant_week_stats(days: int = 7) -> dict[str, dict[str, Any]]:
    """Stats par boutique sur N jours (pour le résumé hebdo aux commerçants).

    Retourne {merchant_id: {business_name, conversations, won, lost, revenue}}.
    """
    from db.client import list_all_merchants, recent_messages, recent_orders

    messages = recent_messages(days)
    orders = recent_orders(days)
    convos = _build_conversations(messages, orders)
    merchants = {m["id"]: m for m in list_all_merchants()}

    out: dict[str, dict[str, Any]] = {}
    for c in convos:
        mid = c["merchant_id"]
        s = out.setdefault(mid, {
            "business_name": (merchants.get(mid) or {}).get("business_name") or "votre boutique",
            "merchant": merchants.get(mid) or {},
            "conversations": 0, "won": 0, "lost": 0, "revenue": 0.0,
        })
        s["conversations"] += 1
        if c["won"]:
            s["won"] += 1
            s["revenue"] += c["revenue"]
        else:
            s["lost"] += 1
    return out
