# -*- coding: utf-8 -*-
"""
Lancer une vague de recherche sur EUR/USD et NAS100, et tenir le registre des tests.

    python -m trading.recherche.lancer --tour 1                 # toutes les candidates
    python -m trading.recherche.lancer --tour 2 --seulement ema_stoch_pullback
    python -m trading.recherche.lancer --resume                 # tableau + correction de Holm

⚠️ CHAQUE test lancé entre dans le registre, qu'il plaise ou non. La correction de
Holm porte sur le registre ENTIER : essayer plus de choses rend chaque réussite
moins crédible, et c'est exactement ce que la correction mesure.
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from . import banc, candidates

INSTRUMENTS = ("EURUSD", "NAS100")      # Mongazi, 2026-09-17 : rien d'autre
DOSSIER = Path(__file__).resolve().parents[1] / "rapports" / "recherche"
REGISTRE = DOSSIER / "registre.json"


def _registre() -> list[dict]:
    return json.loads(REGISTRE.read_text(encoding="utf-8")) if REGISTRE.exists() else []


def lancer(tour: int, seulement: set[str] | None, liste=None) -> None:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    liste = liste or (candidates.CANDIDATES + [candidates.TEMOIN])
    registre = _registre()
    for tf in ("M5", "M15", "H1"):
        for base in INSTRUMENTS:
            serie = None
            for cand in liste:
                if tf not in cand.unites or base not in cand.instruments:
                    continue
                if seulement and cand.nom not in seulement:
                    continue
                if serie is None:
                    try:
                        serie = banc.charger(base, tf)
                    except FileNotFoundError as exc:
                        print(f"  {exc}")
                        break
                t0 = time.time()
                res = banc.walk_forward(serie, cand)
                cle = f"t{tour}_{cand.nom}_{base}_{tf}"
                (DOSSIER / f"{cle}.json").write_text(json.dumps(
                    {"tour": tour, "candidate": cand.nom, "libelle": cand.libelle, "source": cand.source,
                     "grille": cand.grille, **asdict(res)}, ensure_ascii=False, default=str), encoding="utf-8")
                h = res.hors_echantillon
                registre = [r for r in registre if r["cle"] != cle]
                registre.append({"cle": cle, "tour": tour, "candidate": cand.nom, "base": base, "tf": tf,
                                 "temoin": cand.nom == "temoin_hasard", "combinaisons": res.combinaisons,
                                 **{k: h.get(k) for k in ("trades", "taux_reussite", "esperance_R",
                                                          "profit_factor", "p_valeur", "drawdown_max_pct",
                                                          "R_par_mois", "trades_par_mois", "debut", "fin")}})
                REGISTRE.write_text(json.dumps(registre, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  {cand.nom:20s} {base} {tf:3s} {h.get('trades', 0):5d} trades  "
                      + (f"{100 * h['taux_reussite']:5.1f} %  {h['esperance_R']:+.3f} R  "
                         f"PF {h['profit_factor']:.2f}  p={h['p_valeur']:.3f}" if h.get("trades") else "—")
                      + f"  ({time.time() - t0:.0f} s)", flush=True)
            del serie
            gc.collect()


def resume() -> list[dict]:
    registre = _registre()
    candidats = [r for r in registre if not r["temoin"] and r.get("trades")]
    rejets = banc.holm([r["p_valeur"] for r in candidats])
    for r, ok in zip(candidats, rejets):
        r["survit_holm"] = ok
    print(f"\n  REGISTRE : {len(candidats)} tests comptés (témoins exclus), correction de Holm à 5 %\n")
    print(f"  {'test':42s} {'trades':>6s} {'réussite':>9s} {'esp. R':>8s} {'PF':>5s} {'R/mois':>7s} "
          f"{'DD 1 %':>7s} {'p':>6s}  Holm")
    for r in sorted(registre, key=lambda x: -(x.get("esperance_R") or -9)):
        if not r.get("trades"):
            continue
        print(f"  {r['cle']:42s} {r['trades']:6d} {100 * r['taux_reussite']:8.1f}% {r['esperance_R']:+8.3f} "
              f"{r['profit_factor']:5.2f} {r['R_par_mois']:+7.2f} {r['drawdown_max_pct']:6.1f}% "
              f"{r['p_valeur']:6.3f}  {'OUI' if r.get('survit_holm') else ('témoin' if r['temoin'] else 'non')}")
    return registre


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tour", type=int, default=1)
    ap.add_argument("--seulement", nargs="*")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    if not a.resume:
        lancer(a.tour, set(a.seulement) if a.seulement else None)
    resume()
    return 0


if __name__ == "__main__":
    sys.exit(main())
