"""AUTO-EXPÉRIMENTATION — le « machine learning » réaliste de Vendora.

L'agent ne suit pas une stratégie de vente figée : il en teste plusieurs en parallèle
(champion vs challenger), mesure laquelle CONCLUT le plus de ventes, et GARDE la
gagnante. C'est un test A/B continu (bandit) = de l'optimisation par renforcement,
peu coûteuse et incopiable (chaque boutique nourrit l'apprentissage collectif).

Mécanique :
- Chaque « variante » = un bloc de TACTIQUES de vente injecté dans le prompt du vendeur
  (`variant_text`). Le champion par défaut a un texte vide (= comportement de base).
- Assignation STABLE par client (même client → même variante) pour pouvoir attribuer
  le résultat (vente conclue ou non).
- Évaluation périodique (dans le cycle d'apprentissage) : conversion par variante →
  promotion automatique de la gagnante quand l'écart est net + assez de données.
- Une nouvelle challenger est générée (par le modèle) pour continuer à progresser.

Gouvernance : OFF par défaut (`bia_settings.experiments_enabled`) — Mongazi autorise
via le cockpit. Interne/réversible (ça ne change que la FAÇON de vendre de l'agent).
"""
from __future__ import annotations

import json
import logging
import random
import time as _time
from typing import Any

import anthropic

from config import settings

log = logging.getLogger("boutique-ia.experiment")

MIN_SAMPLE_PROMOTE = 12   # conversations attribuées mini pour promouvoir un gagnant
MIN_SAMPLE_LOSER = 6      # le perdant doit aussi avoir un minimum de données
MARGIN = 0.15            # écart de conversion (15 pts) pour déclarer un gagnant
SPAWN_AT = 24            # si 1 seule variante active et ≥ ça d'échantillon → nouvelle challenger

_CACHE: dict[str, tuple[float, Any]] = {}
_TTL = 300.0


def _active_variants() -> list[dict]:
    hit = _CACHE.get("active")
    if hit and (_time.time() - hit[0]) < _TTL:
        return hit[1]
    from db.client import list_experiments
    try:
        v = list_experiments("active")
    except Exception:  # noqa: BLE001
        v = []
    _CACHE["active"] = (_time.time(), v)
    return v


def _clear_cache() -> None:
    _CACHE.clear()


def pick_variant_text(merchant_id: str, customer: str) -> str:
    """Variante de stratégie à injecter pour ce client (stable). '' si pas d'expérience."""
    from db.client import get_setting_bool
    if not get_setting_bool("experiments_enabled", False):
        return ""
    variants = _active_variants()
    if not variants:
        return ""
    if len(variants) == 1:
        return variants[0].get("variant_text") or ""
    # Plusieurs variantes actives → assignation stable par client.
    from db.client import get_assignment, set_assignment
    active_ids = {v["id"] for v in variants}
    try:
        vid = get_assignment(merchant_id, customer)
    except Exception:  # noqa: BLE001
        vid = None
    if vid not in active_ids:
        vid = random.choice(variants)["id"]  # répartition ~équitable pour mesurer
        try:
            set_assignment(merchant_id, customer, vid)
        except Exception:  # noqa: BLE001
            pass
    return next((v.get("variant_text") or "" for v in variants if v["id"] == vid), "")


_GEN_SYSTEM = (
    "Tu conçois une VARIANTE de stratégie de vente à TESTER pour un agent vendeur sur "
    "WhatsApp (commerce, Afrique de l'Ouest francophone, Mobile Money). Le but : trouver "
    "ce qui fait CONCLURE le plus de ventes. Propose UN angle clair et distinct (ex : "
    "urgence/rareté honnête, réassurance & confiance, bénéfices & montée en gamme, preuve "
    "sociale, rapidité de conclusion). Donne des TACTIQUES concrètes, applicables sur "
    "WhatsApp, sans jargon.\n\n"
    'Réponds en JSON STRICT : {"name":"...","hypothesis":"...","tactics":"- ...\\n- ..."} '
    "— name court (< 40 car.), hypothesis = ce que tu paries (1 phrase), tactics = 3 à 5 "
    "puces « - » d'une ligne, à l'impératif, en français."
)


def generate_challenger(lessons: str = "") -> dict | None:
    """Le modèle invente une variante de stratégie à tester (challenger)."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    ctx = ("\n\nLeçons déjà connues (propose un angle qui les COMPLÈTE ou les pousse plus "
           "loin, pas une simple répétition) :\n" + lessons) if lessons else ""
    try:
        resp = client.messages.create(
            model=settings.writer_model, max_tokens=500, system=_GEN_SYSTEM,
            messages=[{"role": "user", "content": "Propose une variante de stratégie à tester." + ctx}],
        )
        raw = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw[4:].strip() if raw.lower().startswith("json") else raw
        data = json.loads(raw)
        tactics = (data.get("tactics") or "").strip()
        name = (data.get("name") or "Variante").strip()[:60]
        if not tactics:
            return None
        return {"name": name, "hypothesis": (data.get("hypothesis") or "").strip(),
                "variant_text": tactics}
    except Exception:  # noqa: BLE001
        log.warning("génération challenger échouée", exc_info=True)
        return None


def seed_experiments() -> bool:
    """Si aucune expérience active : crée le champion (base) + une 1re challenger."""
    from db.client import create_experiment, get_latest_lessons, list_experiments
    if list_experiments("active"):
        return False
    create_experiment("Approche standard", "Comportement de base (référence du test).", "", "active")
    lessons = (get_latest_lessons("global") or {}).get("lessons") or ""
    ch = generate_challenger(lessons)
    if ch:
        create_experiment(ch["name"], ch["hypothesis"], ch["variant_text"], "active")
    _clear_cache()
    return True


def evaluate_experiments() -> dict[str, Any]:
    """Mesure la conversion par variante, promeut la gagnante, retire les perdantes."""
    from db.client import (
        list_assignments,
        list_experiments,
        recent_messages,
        recent_orders,
        set_experiment_status,
        update_experiment_counters,
    )
    from core import learning

    variants = list_experiments("active")
    result: dict[str, Any] = {"variants": [], "promoted": None}
    if not variants:
        return result

    assign = {(a["merchant_id"], a["customer"]): a["variant_id"] for a in list_assignments()}
    convos = learning._build_conversations(recent_messages(21), recent_orders(21))
    tally = {v["id"]: {"total": 0, "won": 0} for v in variants}
    for c in convos:
        vid = assign.get((c["merchant_id"], c["customer"]))
        if vid in tally:
            tally[vid]["total"] += 1
            if c["won"]:
                tally[vid]["won"] += 1

    stats = []
    for v in variants:
        t = tally[v["id"]]
        update_experiment_counters(v["id"], t["total"], t["won"])
        conv = (t["won"] / t["total"]) if t["total"] else 0.0
        stats.append({"id": v["id"], "name": v.get("name"), "total": t["total"],
                      "won": t["won"], "conv": conv, "variant_text": v.get("variant_text")})
    result["variants"] = stats

    # Promotion : il faut ≥2 variantes, un leader assez testé, et un écart net.
    if len(stats) >= 2:
        ranked = sorted(stats, key=lambda s: s["conv"], reverse=True)
        leader, runner = ranked[0], ranked[1]
        if (leader["total"] >= MIN_SAMPLE_PROMOTE and runner["total"] >= MIN_SAMPLE_LOSER
                and (leader["conv"] - runner["conv"]) >= MARGIN):
            for s in stats:
                if s["id"] != leader["id"]:
                    set_experiment_status(s["id"], "retired")
            result["promoted"] = leader["name"]
            _clear_cache()
    return result


def run_experiment_cycle() -> dict[str, Any]:
    """Cycle complet : amorce si besoin, évalue, promeut, relance une challenger. """
    from db.client import get_latest_lessons, get_setting_bool, list_experiments, create_experiment
    from notify import notify_experiment_update

    out: dict[str, Any] = {"enabled": False, "seeded": False, "promoted": None, "spawned": None}
    if not get_setting_bool("experiments_enabled", False):
        return out
    out["enabled"] = True
    out["seeded"] = seed_experiments()
    ev = evaluate_experiments()
    out["promoted"] = ev.get("promoted")
    out["variants"] = ev.get("variants", [])

    # S'il ne reste qu'une variante (un champion établi) et qu'elle a assez tourné,
    # on lance une nouvelle challenger pour continuer à progresser.
    active = list_experiments("active")
    if len(active) == 1 and (active[0].get("total") or 0) >= SPAWN_AT:
        lessons = (get_latest_lessons("global") or {}).get("lessons") or ""
        ch = generate_challenger(lessons)
        if ch:
            create_experiment(ch["name"], ch["hypothesis"], ch["variant_text"], "active")
            out["spawned"] = ch["name"]
            _clear_cache()

    if out["promoted"] or out["spawned"] or out["seeded"]:
        try:
            notify_experiment_update(out)
        except Exception:  # noqa: BLE001
            pass
    return out
