# -*- coding: utf-8 -*-
"""
Walk-forward : la seule validation acceptée.

Le principe tient en une phrase : **on choisit les réglages sur un passé, on
les juge sur l'avenir qui suit, et on n'a pas le droit de revenir en arrière.**

    ┌──── apprentissage (4 ans) ────┐┌─ test (1 an) ─┐
                     ┌──── apprentissage (4 ans) ────┐┌─ test (1 an) ─┐
                                      ...

Seuls les résultats des fenêtres de TEST comptent. Mis bout à bout, ils forment
ce qu'aurait vécu quelqu'un qui aurait appliqué la méthode en temps réel, sans
connaître le futur. Les chiffres d'apprentissage ne sont affichés que pour
mesurer l'écart : un système qui brille en apprentissage et s'effondre en test
a mémorisé le passé, il n'a rien compris.

Trois règles, qui rendent tous le résultat PIRE :
  1. Le critère de choix est le SQN (espérance / dispersion × √n) et non le
     gain : un réglage qui a gagné gros sur 12 trades chanceux perd face à un
     réglage modeste mais régulier sur 60.
  2. Un réglage qui n'a pas produit `min_trades_is` trades en apprentissage
     n'est pas éligible, quel que soit son résultat.
  3. Le capital de chaque fenêtre de test est celui qu'a laissé la précédente :
     les pertes se reportent, rien ne repart à zéro.
"""
from __future__ import annotations

import itertools
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import numpy as np

from .metriques import Metriques, TradeFerme, calculer
from .moteur import Moteur


@dataclass
class Fenetre:
    debut_apprentissage: datetime
    debut_test: datetime
    fin_test: datetime
    parametres: dict
    sqn_apprentissage: float
    trades_apprentissage: int
    esperance_R_apprentissage: float
    trades_test: int = 0
    esperance_R_test: float = 0.0
    resultat_test: float = 0.0
    capital_debut: float = 0.0
    capital_fin: float = 0.0
    eligibles: int = 0


@dataclass
class RapportWalkForward:
    fenetres: list[Fenetre]
    trades: list[TradeFerme]
    courbe_equite: list[tuple[datetime, float]]
    metriques: Metriques
    capital_initial: float
    refus: dict[str, int] = field(default_factory=dict)

    @property
    def efficacite(self) -> float:
        """Espérance en test / espérance en apprentissage.

        Proche de 1 : ce que la méthode apprend se retrouve dans l'avenir.
        Proche de 0 ou négatif : elle a mémorisé du bruit.
        """
        app = [f.esperance_R_apprentissage for f in self.fenetres if f.trades_apprentissage]
        tst = [f.esperance_R_test for f in self.fenetres if f.trades_test]
        if not app or not tst:
            return 0.0
        m_app = statistics.fmean(app)
        return statistics.fmean(tst) / m_app if m_app > 0 else 0.0

    def stabilite_parametres(self) -> dict[str, dict]:
        """Combien de fois chaque valeur a été choisie. Un réglage qui change à
        chaque fenêtre est un réglage que les données ne savent pas trancher."""
        compte: dict[str, dict] = {}
        for f in self.fenetres:
            for k, v in f.parametres.items():
                compte.setdefault(k, {})
                compte[k][v] = compte[k].get(v, 0) + 1
        return compte

    def en_dict(self) -> dict:
        m = self.metriques
        return {
            "capital_initial": self.capital_initial,
            "efficacite": self.efficacite,
            "fenetres": [
                {**{k: (v.isoformat() if isinstance(v, datetime) else v)
                    for k, v in f.__dict__.items()}}
                for f in self.fenetres
            ],
            "metriques": {k: (list(v) if isinstance(v, tuple) else v)
                          for k, v in m.__dict__.items()},
            "credible": m.esperance_credible,
            "echantillon_suffisant": m.echantillon_suffisant,
            "courbe_equite": [(t.isoformat(), round(e, 2)) for t, e in self.courbe_equite],
            "trades_R": [round(t.resultat_R, 4) for t in self.trades],
            "stabilite": {k: {str(a): b for a, b in d.items()}
                          for k, d in self.stabilite_parametres().items()},
            "refus": self.refus,
        }


def sqn(trades: list[TradeFerme]) -> float:
    """System Quality Number : espérance / écart-type × √min(n, 100)."""
    r = [t.resultat_R for t in trades]
    if len(r) < 2:
        return float("-inf")
    ecart = statistics.stdev(r)
    if ecart <= 0:
        return float("-inf")
    return statistics.fmean(r) / ecart * math.sqrt(min(len(r), 100))


def _indice(barres, quand: datetime) -> int:
    return int(np.searchsorted(barres.temps, np.datetime64(quand, "s")))


def _decaler_mois(d: datetime, mois: int) -> datetime:
    total = d.year * 12 + (d.month - 1) + mois
    return d.replace(year=total // 12, month=total % 12 + 1, day=1)


def walk_forward(
    barres,
    fabrique: Callable[..., object],
    espace: dict[str, list],
    *,
    cfg,
    specs,
    couts,
    capital: float,
    annees_apprentissage: int = 4,
    annees_test: int = 1,
    mois_apprentissage: int | None = None,
    mois_test: int | None = None,
    echauffement: int = 300,
    min_trades_is: int = 25,
    rappel: Callable[[str], None] | None = None,
) -> RapportWalkForward:
    """Déroule le walk-forward complet et renvoie les seuls résultats de test.

    Les fenêtres se comptent en mois (`mois_apprentissage`, `mois_test`) quand
    l'historique est court : le NAS100 de Deriv ne remonte qu'à janvier 2024.
    """
    m_app = mois_apprentissage or 12 * annees_apprentissage
    m_test = mois_test or 12 * annees_test
    dire = rappel or (lambda _m: None)
    cles = list(espace)
    combinaisons = [dict(zip(cles, vals)) for vals in itertools.product(*espace.values())] \
        or [{}]

    premier = barres.quand(min(echauffement, len(barres) - 1))
    dernier = barres.quand(len(barres) - 1)

    fenetres: list[Fenetre] = []
    tous_trades: list[TradeFerme] = []
    courbe: list[tuple[datetime, float]] = []
    refus: dict[str, int] = {}
    equite = capital

    # Premier mois PLEIN après l'échauffement (une année pleine pour les longues histoires).
    debut_app = (datetime(premier.year + 1, 1, 1) if m_app >= 24
                 else _decaler_mois(datetime(premier.year, premier.month, 1), 1))
    while True:
        debut_test = _decaler_mois(debut_app, m_app)
        fin_test = _decaler_mois(debut_test, m_test)
        if debut_test >= dernier:
            break
        fin_test = min(fin_test, dernier)

        i_app = _indice(barres, debut_app)
        i_test = _indice(barres, debut_test)
        i_fin = min(_indice(barres, fin_test), len(barres))

        # --- 1. choisir les réglages sur l'apprentissage -------------------
        meilleur, meilleur_score, meilleur_trades, eligibles = None, float("-inf"), [], 0
        tranche_app = barres.tronquer(max(0, i_app - echauffement), i_test)
        for params in combinaisons:
            moteur = Moteur(cfg, specs, couts, fabrique(**params), journaliser_refus=False)
            res = moteur.lancer(tranche_app, capital,
                                echauffement=min(echauffement, i_app))
            if len(res.trades) < min_trades_is:
                continue
            eligibles += 1
            score = sqn(res.trades)
            if score > meilleur_score:
                meilleur, meilleur_score, meilleur_trades = params, score, res.trades

        if meilleur is None:
            dire(f"  {debut_test:%Y} : aucun réglage n'a produit {min_trades_is} trades "
                 f"en apprentissage -> fenêtre non tradée")
            fenetres.append(Fenetre(debut_app, debut_test, fin_test, {}, 0.0, 0, 0.0,
                                    capital_debut=equite, capital_fin=equite))
            debut_app = _decaler_mois(debut_app, m_test)
            continue

        # --- 2. l'appliquer à l'année suivante, jamais vue -------------------
        tranche_test = barres.tronquer(max(0, i_test - echauffement), i_fin)
        moteur = Moteur(cfg, specs, couts, fabrique(**meilleur))
        res = moteur.lancer(tranche_test, equite, echauffement=min(echauffement, i_test))
        for motif, n in res.motifs_de_refus().items():
            refus[motif] = refus.get(motif, 0) + n

        f = Fenetre(
            debut_apprentissage=debut_app, debut_test=debut_test, fin_test=fin_test,
            parametres=meilleur, sqn_apprentissage=meilleur_score,
            trades_apprentissage=len(meilleur_trades),
            esperance_R_apprentissage=statistics.fmean(t.resultat_R for t in meilleur_trades),
            trades_test=len(res.trades),
            esperance_R_test=(statistics.fmean(t.resultat_R for t in res.trades)
                              if res.trades else 0.0),
            resultat_test=sum(t.resultat_devise for t in res.trades),
            capital_debut=equite, eligibles=eligibles,
        )
        tous_trades.extend(res.trades)
        courbe.extend(res.courbe_equite)
        equite += f.resultat_test
        f.capital_fin = equite
        fenetres.append(f)
        dire(f"  {debut_test:%Y} : {meilleur} · appr. {len(meilleur_trades)} trades "
             f"{f.esperance_R_apprentissage:+.2f} R · TEST {f.trades_test} trades "
             f"{f.esperance_R_test:+.2f} R · capital {equite:,.0f}".replace(",", " "))

        debut_app = _decaler_mois(debut_app, m_test)

    m = calculer(tous_trades, capital_initial=capital, courbe_equite=courbe or None)
    return RapportWalkForward(fenetres=fenetres, trades=tous_trades, courbe_equite=courbe,
                              metriques=m, capital_initial=capital,
                              refus=dict(sorted(refus.items(), key=lambda kv: -kv[1])))
