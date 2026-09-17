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


def enregistrer_test(cle: str, ligne: dict) -> None:
    """Inscrire UN test au registre, d'où qu'il vienne (candidates, modèle, règles minées).

    ⚠️ C'est la règle qui rend la recherche honnête : essayer plus de choses doit rendre chaque
    réussite moins crédible. Un test qui n'entre pas au registre est un test qu'on s'est caché.
    """
    DOSSIER.mkdir(parents=True, exist_ok=True)
    registre = [r for r in _registre() if r["cle"] != cle]
    registre.append({"cle": cle, **ligne})
    REGISTRE.write_text(json.dumps(registre, ensure_ascii=False, indent=1), encoding="utf-8")


def lancer(tour: int, seulement: set[str] | None, liste=None,
           unites=("M1", "M5", "M15", "M30", "H1", "H4")) -> None:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    liste = liste or (candidates.CANDIDATES + [candidates.TEMOIN])
    registre = _registre()
    for tf in unites:
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
    # Le critère de Mongazi porte sur le taux de 2 R atteints : quand il est mesuré, c'est lui qu'on
    # corrige. Les tests plus anciens n'ont que l'espérance : on garde leur p, pour que la
    # multiplicité reste comptée sur le registre ENTIER.
    rejets = banc.holm([r.get("p_objectif") if r.get("p_objectif") is not None else r["p_valeur"]
                        for r in candidats])
    for r, ok in zip(candidats, rejets):
        r["survit_holm"] = ok
    print(f"\n  REGISTRE : {len(candidats)} tests comptés (témoins exclus), correction de Holm à 5 %\n")
    print(f"  {'test':46s} {'trades':>6s} {'gagnants':>9s} {'2 R':>7s} {'pt mort':>8s} {'esp. R':>8s} "
          f"{'PF':>5s} {'p':>6s}  Holm")

    def nombre(x, gabarit="8.3f", defaut="       —"):
        return format(x, gabarit) if isinstance(x, (int, float)) else defaut

    for r in sorted(registre, key=lambda x: -(x.get("esperance_R") or -9)):
        if not r.get("trades"):
            continue
        obj = r.get("taux_objectif")
        pm = r.get("point_mort_objectif")
        print(f"  {r['cle'][:46]:46s} {r['trades']:6d} "
              f"{nombre(100 * (r.get('taux_reussite') or 0), '8.1f')}% "
              f"{nombre(100 * obj, '6.1f') if obj is not None else '     —'}% "
              f"{nombre(100 * pm, '7.1f') if pm is not None else '      —'}% "
              f"{nombre(r.get('esperance_R'))} {nombre(r.get('profit_factor'), '5.2f', '    —')} "
              f"{nombre(r.get('p_valeur'), '6.3f', '     —')}  "
              f"{'OUI' if r.get('survit_holm') else ('témoin' if r['temoin'] else 'non')}")
    return registre


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tour", type=int, default=1)
    ap.add_argument("--seulement", nargs="*")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--unites", nargs="*", default=["M1", "M5", "M15", "M30", "H1", "H4"])
    a = ap.parse_args()
    if not a.resume:
        lancer(a.tour, set(a.seulement) if a.seulement else None, unites=tuple(a.unites))
    resume()
    return 0


if __name__ == "__main__":
    sys.exit(main())
