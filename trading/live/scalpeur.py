# -*- coding: utf-8 -*-
"""
L'agent de scalping : il pose des ordres LIMITES en M1, tout seul, et ferme avant la nuit.

    python -m trading.live.scalpeur --observer          # il décide et journalise, il n'envoie RIEN
    python -m trading.live.scalpeur --marche NAS100     # il trade (démo uniquement, voir le videur)

Pourquoi un agent à part, et pas une stratégie de plus dans `live/agent.py` : celui-ci travaille en
**H4 au marché**, une décision par barre. Celui-là travaille **à la minute, en ordres limites**, avec
un modèle à charger, des ordres à annuler et une clôture forcée le soir. Mélanger les deux aurait
fragilisé l'agent qui tourne déjà.

Ce qu'il fait, à chaque minute close :
  1. **fin de journée ?** → annuler les ordres en attente, fermer la position, ne plus rien ouvrir ;
  2. **une position ouverte ?** → ne rien faire (une seule à la fois, comme le backtest) ;
  3. **un ordre en attente trop vieux ?** (plus de 60 min) → l'annuler ;
  4. sinon : calculer les caractéristiques de la dernière barre CLOSE, demander sa probabilité au
     modèle, et si elle dépasse le seuil, poser un ordre limite à 0,5 R sous le prix (au-dessus en
     vente), stop à 2 × ATR(14), objectif à 2 R.

⚠️ **Le risque n'est pas décidé ici** : il vient de `noyau/profils.risque_courant` (l'échelle 6-4-3)
et la taille de `noyau/risque.dimensionner`. Même code que le backtest — c'est la seule façon que la
mesure et le compte disent la même chose.
⛔ **Le videur du fichier de configuration s'applique** : mode réel interdit tant que la porte démo
n'est pas franchie.
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np

from ..noyau import profils
from ..noyau.config import charger
from ..noyau.courtier import Courtier
from ..noyau.donnees_mt5 import dernieres_barres, specs_et_couts
from ..noyau.risque import dimensionner
from ..recherche import banc, caracteristiques, modele as mod_modele
from ..recherche.candidat import REGLAGES
from ..recherche.etiquettes import atr
from ..recherche.intraday import fenetres, minutes_et_jours
from .execution import Executeur
from .journal import Journal

BARRES_CONTEXTE = 6000          # ~4 jours de M1 : assez pour l'EMA, l'ATR et les extrêmes de la veille
MAGIC = 770018                  # le numéro de cet agent chez le courtier, distinct de l'agent H4


@dataclass
class Decision:
    agir: bool
    motif: str
    sens: int = 0
    proba: float = float("nan")
    limite: float = 0.0
    stop: float = 0.0
    objectif: float = 0.0
    risque_prix: float = 0.0


def serie_depuis_barres(barres, base: str, point: float, cout_points: float) -> banc.Serie:
    """Une `Serie` du banc, construite depuis les barres du courtier.

    ⚠️ C'est volontairement le MÊME objet que le backtest : les caractéristiques sont alors calculées
    par le même code, sur la même forme de données. Une deuxième implémentation « pour le direct »
    finirait par diverger, et personne ne le verrait avant la première perte inexpliquée.
    """
    n = len(barres.cloture)
    jours = barres.temps.astype("datetime64[D]")
    nouveau = np.concatenate(([False], jours[1:] != jours[:-1]))
    jeudi = (jours.astype("int64") + 3) % 7 == 3
    poids = np.where(nouveau, np.where(jeudi, 3.0, 1.0), 0.0)
    return banc.Serie(base=base, tf="M1", temps=barres.temps, ouverture=barres.ouverture,
                      haut=barres.haut, bas=barres.bas, cloture=barres.cloture, point=point,
                      cout_sens_pts=cout_points, swap_long_pts=0.0, swap_court_pts=0.0,
                      nuits_cumul=np.cumsum(poids), stop_min_prix=0.0, source="direct",
                      volume=barres.volume if getattr(barres, "volume", None) is not None else None)


def decider(serie: banc.Serie, modele, fiche: dict) -> Decision:
    """La décision pour la DERNIÈRE barre close. Aucune barre future n'existe ici, par construction."""
    minute, jour = minutes_et_jours(serie.temps)
    debut, fin_entree, cloture = fenetres(serie.base)
    i = len(serie) - 1
    if jour[i] >= 5 or not (debut <= minute[i] <= fin_entree):
        return Decision(False, f"hors fenêtre d'entrée (minute {minute[i]} New York)")
    a = atr(serie, 14)
    if not np.isfinite(a[i]) or a[i] <= 0:
        return Decision(False, "ATR indisponible")
    import pandas as pd
    p = max(1, int(REGLAGES["tendance"] / 1))
    ema = pd.Series(serie.cloture).ewm(span=p, adjust=False, min_periods=p).mean().to_numpy()
    if not np.isfinite(ema[i]):
        return Decision(False, "EMA indisponible")
    sens = 1 if serie.cloture[i] > ema[i] else -1
    X = caracteristiques.construire(serie)
    ligne = {nom: valeurs[i] for nom, valeurs in X.items()}
    try:
        proba = mod_modele.probabilite(modele, fiche, ligne)
    except ValueError as exc:
        return Decision(False, f"modèle incompatible : {exc}")
    if not np.isfinite(proba):
        return Decision(False, "caractéristiques incomplètes sur cette barre", proba=proba)
    if proba < fiche["seuil"]:
        return Decision(False, f"probabilité {proba:.3f} sous le seuil {fiche['seuil']:.3f}",
                        sens=sens, proba=proba)
    d = REGLAGES["stop_atr"] * a[i]
    limite = serie.cloture[i] - sens * REGLAGES["retrait"] * d
    return Decision(True, f"probabilité {proba:.3f} ≥ seuil {fiche['seuil']:.3f}", sens=sens,
                    proba=proba, limite=limite, stop=limite - sens * d,
                    objectif=limite + sens * 2.0 * d, risque_prix=d)


class Scalpeur:
    def __init__(self, marche: str = "NAS100", observer: bool = True, profil: str = "defaut"):
        self.marche = marche.upper()
        self.observer = observer
        self.profil_courtier = profil
        self.journal = Journal()
        self.modele, self.fiche = mod_modele.charger(self.marche)
        if self.modele is None:
            raise SystemExit(f"aucun modèle pour {self.marche} : "
                             f"python -m trading.recherche.modele --marche {self.marche} --entrainer")
        self.etat_profil = None
        self.derniere_barre = None
        self.poses: dict[int, datetime] = {}

    # ------------------------------------------------------------------ #
    def _fermer_la_journee(self, executeur, specs, positions) -> None:
        for o in executeur.ordres_en_attente():
            r = executeur.annuler(o.ticket)
            self.journal.evenement("scalpeur", f"fin de journée : ordre {o.ticket} annulé "
                                               f"({'ok' if r.ok else r.message})")
        for p in positions:
            r = executeur.fermer(p, motif="clôture de la journée")
            self.journal.evenement("scalpeur", f"fin de journée : position {p.ticket} fermée "
                                               f"({'ok' if r.ok else r.message})")

    def cycle(self, courtier, executeur, specs, cout_points: float) -> dict:
        import MetaTrader5 as mt5
        barres = dernieres_barres(self.symbole, "M1", BARRES_CONTEXTE)
        derniere = barres.temps[-1]
        if self.derniere_barre is not None and derniere <= self.derniere_barre:
            return {"attente": "pas de nouvelle barre close"}
        self.derniere_barre = derniere
        serie = serie_depuis_barres(barres, self.marche, specs.point, cout_points)
        minute, jour = minutes_et_jours(serie.temps)
        _, _, cloture = fenetres(self.marche)
        positions = executeur.positions()
        compte = mt5.account_info()
        if compte is None:
            return {"etat": "compte illisible"}
        if self.etat_profil is None:
            self.etat_profil = profils.initialiser("plan", compte.equity)
        profils.maj_sommet(self.etat_profil, compte.equity)

        if minute[-1] >= cloture or jour[-1] >= 5:
            self._fermer_la_journee(executeur, specs, positions)
            return {"etat": "journée fermée", "minute_ny": int(minute[-1])}

        # Les ordres trop vieux s'annulent : le backtest les fait expirer après 60 minutes.
        for o in executeur.ordres_en_attente():
            pose = self.poses.get(o.ticket)
            age = (datetime.now(timezone.utc) - pose).total_seconds() / 60 if pose else None
            if age is not None and age > REGLAGES["expiration_min"]:
                executeur.annuler(o.ticket)
                self.poses.pop(o.ticket, None)
                self.journal.evenement("scalpeur", f"ordre {o.ticket} expiré après {age:.0f} minutes")

        if positions:
            return {"etat": "position ouverte", "positions": len(positions)}
        if executeur.ordres_en_attente():
            return {"etat": "ordre en attente"}

        d = decider(serie, self.modele, self.fiche)
        cfg = charger()
        risque_pct, note = profils.risque_courant(cfg, self.etat_profil, compte.equity)
        if not d.agir:
            self.journal.decision(verdict="refus", motif=d.motif, sens="achat" if d.sens > 0 else "vente",
                                  mode="observation" if self.observer else "reel",
                                  note=f"p={d.proba:.3f}" if np.isfinite(d.proba) else "")
            return {"etat": "pas de signal", "motif": d.motif, "proba": d.proba,
                    "risque_pct": risque_pct}

        taille = dimensionner(capital=profils.capital_disponible(compte.balance, self.etat_profil),
                              risque_pct=risque_pct, points_de_risque=d.risque_prix / specs.point,
                              specs=specs, lots_total_max=specs.volume_max,
                              lots_deja_ouverts=0.0, prix=d.limite,
                              levier_max=cfg.profil.levier_effectif_max)
        if not taille.autorise:
            self.journal.decision(verdict="refus", motif=f"taille : {taille.raison.splitlines()[0]}",
                                  mode="observation" if self.observer else "reel")
            return {"etat": "taille refusée", "motif": taille.raison.splitlines()[0]}

        if self.observer:
            self.journal.decision(verdict="observation", motif=d.motif,
                                  sens="achat" if d.sens > 0 else "vente", entree=d.limite,
                                  stop=d.stop, objectif=d.objectif, lots=taille.lots,
                                  risque_pct=risque_pct, risque_devise=taille.risque_devise,
                                  mode="observation", note=f"p={d.proba:.3f} · {note}")
            return {"etat": "ordre SIMULÉ (observation)", "sens": d.sens, "proba": d.proba,
                    "limite": d.limite, "lots": taille.lots, "risque_pct": risque_pct}

        r = executeur.poser_limite(achat=d.sens > 0, lots=taille.lots, limite=d.limite, stop=d.stop,
                                   objectif=d.objectif, specs=specs,
                                   expire_le=datetime.now(timezone.utc)
                                   + timedelta(minutes=REGLAGES["expiration_min"]),
                                   commentaire="nebula-scalp")
        self.journal.ordre(action="limite", ticket=r.ticket, sens="achat" if d.sens > 0 else "vente",
                           lots=taille.lots, prix=d.limite, sl=d.stop, tp=d.objectif,
                           retcode=r.retcode, commentaire=r.message, mode="reel")
        if r.ok:
            self.poses[r.ticket] = datetime.now(timezone.utc)
        return {"etat": "ordre posé" if r.ok else f"refusé : {r.message}", "ticket": r.ticket,
                "sens": d.sens, "proba": d.proba, "lots": taille.lots, "risque_pct": risque_pct}

    # ------------------------------------------------------------------ #
    def tourner(self, secondes: float = 20.0, tours: int | None = None) -> None:
        with Courtier.depuis_profil(self.profil_courtier) as courtier:
            self.symbole = courtier.trouver_symbole(self.marche)
            specs = courtier.specs(self.symbole)
            _, couts = specs_et_couts(self.marche)
            cout_points = (couts.spread_points / 2 + couts.slippage_points) if couts else 3.0
            executeur = Executeur(self.symbole, MAGIC)
            self.journal.evenement("scalpeur", f"démarrage sur {self.symbole} · modèle du "
                                               f"{self.fiche['entraine_le'][:16]} · seuil "
                                               f"{self.fiche['seuil']:.3f} · "
                                               f"{'OBSERVATION' if self.observer else 'RÉEL'}")
            n = 0
            while tours is None or n < tours:
                try:
                    etat = self.cycle(courtier, executeur, specs, cout_points)
                    if etat.get("etat"):
                        print(f"  {datetime.now():%H:%M:%S} · {etat}", flush=True)
                except Exception as exc:                                   # noqa: BLE001
                    self.journal.evenement("erreur", f"scalpeur : {exc}", niveau="alerte")
                    print(f"  erreur : {exc}", flush=True)
                n += 1
                if tours is None or n < tours:
                    time.sleep(secondes)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--reel", action="store_true",
                    help="envoyer les ordres pour de vrai (sinon : observation seule)")
    ap.add_argument("--tours", type=int, help="nombre de cycles (par défaut : sans fin)")
    ap.add_argument("--secondes", type=float, default=20.0)
    a = ap.parse_args()
    # ⛔ Observation par défaut : pour envoyer un ordre il faut le demander explicitement.
    Scalpeur(a.marche, observer=not a.reel).tourner(a.secondes, a.tours)
    return 0


if __name__ == "__main__":
    sys.exit(main())
