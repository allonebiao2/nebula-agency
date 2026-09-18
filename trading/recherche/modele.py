# -*- coding: utf-8 -*-
"""
Le modèle du filtre, entraîné puis **posé sur le disque** pour que l'agent s'en serve en direct.

    python -m trading.recherche.modele --marche NAS100 --entrainer
    python -m trading.recherche.modele --marche NAS100 --etat

Un modèle qui ne vit que dans un notebook ne trade pas. Celui-ci est écrit dans `trading/modeles/`
avec **tout ce qu'il faut pour être rejoué à l'identique** : la liste ordonnée des caractéristiques,
le seuil de probabilité, la période d'apprentissage, et l'empreinte des réglages de la stratégie.

⚠️ **L'ordre des caractéristiques fait partie du modèle.** Si l'agent les range autrement que
l'entraînement, le modèle lit « volume » là où il attend « heure » et ne dit plus rien de juste —
sans erreur, sans alerte. Le nom des colonnes est donc enregistré, et l'agent refuse de servir si la
liste ne correspond pas.

⚠️ **Le seuil n'est pas un réglage esthétique** : c'est lui qui décide de la sélectivité (garder 5 %
des occasions, c'est environ un trade par jour). Il est calibré sur les probabilités du passé, pas
choisi à la main.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from ..noyau.chemins import dossier_donnees
from .candidat import REGLAGES

DOSSIER_MODELES = dossier_donnees().parent / "modeles"


def chemin(marche: str) -> Path:
    return DOSSIER_MODELES / f"filtre_{marche.upper()}.joblib"


def chemin_fiche(marche: str) -> Path:
    return DOSSIER_MODELES / f"filtre_{marche.upper()}.json"


def entrainer(marche: str = "NAS100", part: float = 0.05, source: str = "duka") -> dict:
    """Apprendre sur TOUT l'historique disponible, puis écrire le modèle et sa fiche."""
    import joblib
    from sklearn.ensemble import HistGradientBoostingClassifier
    from . import banc, meta_candidat as mc
    serie = banc.charger(marche, "M1", source=source)
    d = mc.trades_et_caracteristiques(serie)
    if d is None:
        raise SystemExit(f"{marche} : aucun trade")
    X, i, y, ok = d["X"], d["i_signal"], d["objectif"], d["ok"]
    modele = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                            min_samples_leaf=100, l2_regularization=1.0,
                                            early_stopping=True, validation_fraction=0.15,
                                            random_state=5)
    modele.fit(X[i[ok]], y[ok].astype(np.int8))
    proba = modele.predict_proba(X[i[ok]])[:, 1]
    seuil = float(np.quantile(proba, 1 - part))
    DOSSIER_MODELES.mkdir(parents=True, exist_ok=True)
    joblib.dump(modele, chemin(marche))
    fiche = {
        "marche": marche.upper(), "source": source, "part_gardee": part, "seuil": round(seuil, 6),
        "caracteristiques": d["noms"], "reglages_strategie": REGLAGES,
        "trades_appris": int(ok.sum()),
        "periode": [str(serie.temps[0])[:10], str(serie.temps[-1])[:10]],
        "taux_objectif_appris": round(float(y[ok].mean()), 4),
        "taux_objectif_au_seuil": round(float(y[ok][proba >= seuil].mean()), 4),
        "entraine_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": ("Le taux au seuil est mesuré SUR L'APPRENTISSAGE : il est optimiste. La mesure "
                 "honnête est celle du walk-forward (`long_backtest.py`) et, à terme, de la démo."),
    }
    chemin_fiche(marche).write_text(json.dumps(fiche, ensure_ascii=False, indent=1), encoding="utf-8")
    return fiche


def charger(marche: str = "NAS100"):
    """(modèle, fiche) ou (None, None) si rien n'est entraîné."""
    import joblib
    if not chemin(marche).exists() or not chemin_fiche(marche).exists():
        return None, None
    fiche = json.loads(chemin_fiche(marche).read_text(encoding="utf-8"))
    return joblib.load(chemin(marche)), fiche


def probabilite(modele, fiche: dict, X_une_ligne: dict) -> float:
    """La probabilité pour UNE barre, avec la garantie que les colonnes sont dans le bon ordre."""
    noms = fiche["caracteristiques"]
    manquantes = [n for n in noms if n not in X_une_ligne]
    if manquantes:
        raise ValueError(f"caractéristiques manquantes pour le modèle : {manquantes[:5]}")
    ligne = np.array([[float(X_une_ligne[n]) for n in noms]], dtype=np.float32)
    if not np.isfinite(ligne).all():
        return float("nan")
    return float(modele.predict_proba(ligne)[0, 1])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--part", type=float, default=0.05)
    ap.add_argument("--source", default="duka")
    ap.add_argument("--entrainer", action="store_true")
    ap.add_argument("--etat", action="store_true")
    a = ap.parse_args()
    if a.entrainer:
        f = entrainer(a.marche, a.part, a.source)
        print(f"  modèle écrit : {chemin(a.marche)}")
        print(f"    appris sur {f['trades_appris']} trades ({f['periode'][0]} → {f['periode'][1]}), "
              f"{len(f['caracteristiques'])} caractéristiques")
        print(f"    seuil {f['seuil']:.4f} pour garder {100 * f['part_gardee']:.0f} % des occasions")
        print(f"    taux de 2 R au seuil, SUR L'APPRENTISSAGE (optimiste) : "
              f"{100 * f['taux_objectif_au_seuil']:.1f} %")
    if a.etat or not a.entrainer:
        m, f = charger(a.marche)
        if m is None:
            print(f"  aucun modèle pour {a.marche} : lancer --entrainer")
        else:
            print(f"  {a.marche} : modèle du {f['entraine_le'][:16]}, seuil {f['seuil']:.4f}, "
                  f"{f['trades_appris']} trades appris, {len(f['caracteristiques'])} caractéristiques")
    return 0


if __name__ == "__main__":
    sys.exit(main())
