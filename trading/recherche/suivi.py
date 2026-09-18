# -*- coding: utf-8 -*-
"""
Le carnet : **chaque trade noté, comparé à ce que le backtest promettait, et ce qu'on en apprend.**

    python -m trading.recherche.suivi                 # écrit trading/SUIVI.md
    python -m trading.recherche.suivi --reference     # recalcule la référence du backtest

Mongazi, 2026-09-18 : « je veux que tu notes au fur et à mesure chaque trade perte gain, tu analyses
et tu améliores au fur et à mesure ».

Le journal SQLite de l'agent (`live/journal.py`, table `trades`) enregistre déjà chaque ouverture et
chaque fermeture. Ce fichier ne réinvente rien : il le **lit**, en tire une ligne par trade, et pose
à côté **ce que le backtest annonçait**. Un écart entre les deux est l'information la plus précieuse
de tout le projet, parce que c'est la seule qui ne vienne pas de nos propres hypothèses.

**Ce qu'on surveille, dans cet ordre** :
  1. **le taux de remplissage des ordres limites** — c'est la seule hypothèse du backtest qu'un
     courtier peut démentir, et elle est au cœur de la stratégie ;
  2. **le spread réellement payé** contre les 70 points du profil ;
  3. le **taux de 2 R atteints**, comparé à son intervalle de confiance ;
  4. la **série perdante en cours** et le palier de risque qui en découle.
⚠️ Un écart ne se corrige pas le jour même : on note, on accumule, et on ne change une règle qu'avec
assez de trades pour que le changement ne soit pas du bruit. Toute modification repart au registre.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .lancer import DOSSIER

CIBLE = Path(__file__).resolve().parents[1] / "SUIVI.md"
REFERENCE = DOSSIER / "plan" / "reference_backtest.json"
ECHELLE = ((0.0, 6.0), (0.0001, 4.0), (0.20, 3.0))


def reference_backtest(marche: str = "NAS100", part: float = 0.05) -> dict:
    """Ce que le backtest promet, chiffre par chiffre. C'est la barre à laquelle le direct se compare."""
    from . import banc
    from .compte_plan import trades_du_plan
    trades = trades_du_plan(marche, part)
    R = np.array([t.R for t in trades])
    objectif = R > 1.5                      # un trade qui a pris ses 2 R (net de coûts)
    duree = [(t.sortie - t.entree).total_seconds() / 60 for t in trades]
    jours = len({t.entree.date() for t in trades})
    ref = {"marche": marche, "part": part, "trades": len(R),
           "taux_objectif": round(float(objectif.mean()), 4),
           "esperance_R": round(float(R.mean()), 4),
           "ecart_type_R": round(float(R.std()), 4),
           "gain_moyen_R": round(float(R[R > 0].mean()), 3),
           "perte_moyenne_R": round(float(R[R <= 0].mean()), 3),
           "trades_par_jour": round(len(R) / max(jours, 1), 2),
           "duree_mediane_min": round(float(np.median(duree)), 1),
           "ic95_taux_objectif": [round(x, 4) for x in banc._wilson(int(objectif.sum()), len(R))],
           "calcule_le": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE.write_text(json.dumps(ref, ensure_ascii=False), encoding="utf-8")
    return ref


def trades_en_direct() -> list[dict]:
    """Les trades fermés du journal de l'agent, les plus récents en dernier."""
    from ..live.journal import Journal
    j = Journal()
    lignes = j._lire("SELECT * FROM trades WHERE ferme_le IS NOT NULL ORDER BY ferme_le")
    return lignes


def _palier(drawdown: float) -> float:
    niveau = ECHELLE[0][1]
    for seuil, risque in ECHELLE:
        if drawdown >= seuil - 1e-12:
            niveau = risque
    return niveau


def analyser(trades: list[dict], ref: dict) -> dict:
    """Les chiffres du direct, et leur écart à la référence."""
    if not trades:
        return {"trades": 0}
    R = np.array([t.get("resultat_R") or 0.0 for t in trades], float)
    gains = R > 0
    objectif = R > 1.5
    serie, pire = 0, 0
    for g in gains:
        serie = 0 if g else serie + 1
        pire = max(pire, serie)
    equite = np.cumsum([t.get("resultat_devise") or 0.0 for t in trades])
    sommets = np.maximum.accumulate(np.concatenate(([0.0], equite)))[1:]
    drawdown = float((sommets[-1] - equite[-1]) / sommets[-1]) if sommets[-1] > 0 else 0.0
    ic = ref.get("ic95_taux_objectif") or [0, 1]
    taux = float(objectif.mean())
    return {"trades": len(R), "taux_objectif": round(taux, 4),
            "taux_reussite": round(float(gains.mean()), 4),
            "esperance_R": round(float(R.mean()), 4),
            "somme_R": round(float(R.sum()), 2),
            "resultat_devise": round(float(equite[-1]), 2),
            "serie_perdante_max": int(pire),
            "serie_perdante_en_cours": int(serie),
            "drawdown_courant_pct": round(100 * drawdown, 2),
            "palier_risque_pct": _palier(drawdown),
            "dans_l_intervalle": bool(ic[0] <= taux <= ic[1]) if len(R) >= 30 else None,
            "ecart_esperance_R": round(float(R.mean()) - (ref.get("esperance_R") or 0), 4)}


def ecrire(marche: str = "NAS100") -> Path:
    ref = json.loads(REFERENCE.read_text(encoding="utf-8")) if REFERENCE.exists() else {}
    try:
        trades = trades_en_direct()
    except Exception as exc:                                   # journal absent ou illisible
        trades = []
        print(f"  (journal indisponible : {exc})")
    d = analyser(trades, ref)
    lignes = ["# NEBULA Trader · carnet de suivi", "",
              f"*Régénéré le {datetime.now().strftime('%Y-%m-%d %H:%M')}. Une ligne par trade, et"
              f" l'écart à ce que le backtest promettait.*", ""]
    if ref:
        lignes += ["## Ce que le backtest promet", "",
                   f"- **{100 * ref['taux_objectif']:.1f} %** des trades atteignent 2 R "
                   f"(intervalle de confiance {100 * ref['ic95_taux_objectif'][0]:.1f} – "
                   f"{100 * ref['ic95_taux_objectif'][1]:.1f} %, sur {ref['trades']} trades)",
                   f"- **{ref['esperance_R']:+.3f} R** par trade, écart-type {ref['ecart_type_R']:.2f} R",
                   f"- gain moyen **{ref['gain_moyen_R']:+.2f} R**, perte moyenne "
                   f"**{ref['perte_moyenne_R']:+.2f} R**",
                   f"- **{ref['trades_par_jour']:.1f} trades par jour**, durée médiane "
                   f"{ref['duree_mediane_min']:.0f} minutes", ""]
    lignes += ["## Le direct", ""]
    if not d.get("trades"):
        lignes += ["**Aucun trade fermé pour l'instant.** Le carnet se remplira tout seul dès que"
                   " l'agent tournera : chaque ouverture et chaque fermeture passent déjà par le"
                   " journal (`trading/donnees/journal.db`).", "",
                   "⏳ Ce qu'il faut pour commencer : lancer l'agent en observation sur le démo"
                   " `6305888` avec le profil du plan (échelle 6-4-3).", ""]
    else:
        lignes += [f"- **{d['trades']} trades fermés** · {100 * d['taux_objectif']:.1f} % ont atteint"
                   f" 2 R · espérance **{d['esperance_R']:+.3f} R** · total "
                   f"**{d['somme_R']:+.1f} R** ({d['resultat_devise']:+.2f} $)",
                   f"- série perdante : **{d['serie_perdante_max']}** au pire, "
                   f"**{d['serie_perdante_en_cours']}** en cours",
                   f"- drawdown courant **{d['drawdown_courant_pct']:.1f} %** → palier de risque "
                   f"**{d['palier_risque_pct']:g} %**",
                   f"- écart à la référence : **{d['ecart_esperance_R']:+.3f} R** par trade"
                   + ("" if d["dans_l_intervalle"] is None else
                      (" · dans l'intervalle de confiance du backtest ✅" if d["dans_l_intervalle"]
                       else " · **hors de l'intervalle du backtest** ⚠️")), ""]
        lignes += ["## Les trades", "",
                   "| # | fermé le | sens | lots | R | résultat | motif |", "|---|---|---|---|---|---|---|"]
        for k, t in enumerate(trades[-60:], start=max(1, len(trades) - 59)):
            lignes.append(f"| {k} | {str(t.get('ferme_le'))[:16]} | {t.get('sens')} | "
                          f"{t.get('lots')} | {(t.get('resultat_R') or 0):+.2f} | "
                          f"{(t.get('resultat_devise') or 0):+.2f} $ | {t.get('motif') or ''} |")
        lignes.append("")
    lignes += ["## Ce qu'on surveille, dans cet ordre", "",
               "1. **Le taux de remplissage des ordres limites.** C'est la seule hypothèse du"
               " backtest qu'un courtier peut démentir, et toute la stratégie repose dessus.",
               "2. **Le spread réellement payé**, contre les 70 points mesurés chez Deriv.",
               "3. **Le taux de 2 R atteints**, comparé à l'intervalle de confiance ci-dessus.",
               "4. **La série perdante en cours**, qui décide du palier de risque.", "",
               "⚠️ Un écart ne se corrige pas le jour même. On note, on accumule, et on ne change"
               " une règle qu'avec assez de trades pour que le changement ne soit pas du bruit."
               " Toute modification repasse par le registre et se juge en avant.", ""]
    CIBLE.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return CIBLE


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--part", type=float, default=0.05)
    ap.add_argument("--reference", action="store_true", help="recalculer la référence du backtest")
    a = ap.parse_args()
    if a.reference or not REFERENCE.exists():
        ref = reference_backtest(a.marche, a.part)
        print(f"  référence : {ref['trades']} trades, {100 * ref['taux_objectif']:.1f} % de 2 R, "
              f"{ref['esperance_R']:+.3f} R, {ref['trades_par_jour']:.1f} trades/jour")
    chemin = ecrire(a.marche)
    print(f"  → {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
