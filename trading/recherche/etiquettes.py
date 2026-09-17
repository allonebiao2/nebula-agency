# -*- coding: utf-8 -*-
"""
L'étiquette qui répond à la question de Mongazi, barre par barre : **2 R avant 1 R, oui ou non ?**

    from .etiquettes import etiqueter, stops_atr
    e = etiqueter(serie, stop_dist=stops_atr(serie, 2.0), sens=+1)
    e.taux_objectif()        # la part des minutes où l'objectif de 2 R serait tombé avant le stop

Une stratégie, c'est un choix de minutes. Avant de chercher des règles, on mesure ce qu'il y a à
gagner : si aucune minute de la journée ne dépasse le point mort, aucune règle bâtie dessus ne le
dépassera non plus. C'est la mesure la moins chère de toute la recherche, et la plus dure à tromper.

Trois règles, les mêmes que le banc, et c'est volontaire :
  · entrée à l'OUVERTURE de la barre suivante, jamais à la clôture du signal ;
  · dans une même barre, **le stop d'abord** (on ne suppose jamais que l'objectif est tombé avant) ;
  · coût du spread de LA minute d'entrée et de LA minute de sortie, plancher de stop du courtier.
Et une règle en plus, celle de cette recherche : **la journée se ferme** (`intraday.fin_de_journee`).

⚠️ Un contrôle (`_qc_sans_fin.py`) rejoue un jeu de signaux épars dans `banc.simuler` et exige le
même R au trade près. Une étiquette qui diverge du simulateur ne mesure pas ce qu'on croit.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numba import njit

from .banc import FIN, GAP, OBJECTIF, SEANCE, STOP, TEMPS, Serie
from .intraday import fin_de_journee, masque_entree


# --------------------------------------------------------------------------- #
#  Distances de stop
# --------------------------------------------------------------------------- #

@njit(cache=True)
def _atr_rma(haut, bas, clo, periode):
    n = len(clo)
    out = np.full(n, np.nan)
    if n <= periode:
        return out
    somme = 0.0
    for i in range(1, periode + 1):
        tr = max(haut[i] - bas[i], abs(haut[i] - clo[i - 1]), abs(bas[i] - clo[i - 1]))
        somme += tr
    out[periode] = somme / periode
    a = 1.0 / periode
    for i in range(periode + 1, n):
        tr = max(haut[i] - bas[i], abs(haut[i] - clo[i - 1]), abs(bas[i] - clo[i - 1]))
        out[i] = out[i - 1] + a * (tr - out[i - 1])
    return out


def atr(serie: Serie, periode: int = 14) -> np.ndarray:
    """ATR de Wilder, comme MT5. Aucune valeur ne dépend d'une barre future."""
    return _atr_rma(serie.haut, serie.bas, serie.cloture, periode)


def stops_atr(serie: Serie, k: float, periode: int = 14) -> np.ndarray:
    """Stop = k × ATR(periode), mesuré à la barre du signal."""
    return k * atr(serie, periode)


def stops_points(serie: Serie, points: float) -> np.ndarray:
    """Stop fixe, en points du courtier : utile pour lire le coût en R directement."""
    return np.full(len(serie), points * serie.point)


SCHEMAS = {                      # nom -> (fabrique, ce que ça teste)
    "atr14x1": (lambda s: stops_atr(s, 1.0, 14), "stop très court : coût maximal en R"),
    "atr14x2": (lambda s: stops_atr(s, 2.0, 14), "scalping serré"),
    "atr14x4": (lambda s: stops_atr(s, 4.0, 14), "scalping large"),
    "atr60x2": (lambda s: stops_atr(s, 2.0, 60), "volatilité de l'heure écoulée"),
    "atr60x4": (lambda s: stops_atr(s, 4.0, 60), "intraday ample"),
}


# --------------------------------------------------------------------------- #
#  Étiquetage
# --------------------------------------------------------------------------- #

@njit(cache=True)
def _etiqueter(ouv, haut, bas, clo, sens, stop_dist, rr, max_barres, fin_seance, couts,
               swap_l_prix, swap_c_prix, nuits, stop_min, permis):
    """Copie fidèle de `banc._simuler`, SANS la règle « une position à la fois » : chaque barre
    permise est étiquetée pour elle-même."""
    n = len(clo)
    R = np.full(n, np.nan)
    motif = np.full(n, np.int8(-1))
    duree = np.zeros(n, np.int32)
    for i in range(n - 1):
        if not permis[i]:
            continue
        d = stop_dist[i]
        if not (d >= stop_min and d > 0.0):
            continue
        e = i + 1
        s = 1.0 if sens > 0 else -1.0
        cout_prix = couts[e]
        entree = ouv[e] + s * cout_prix
        stop = entree - s * d
        cible = entree + s * rr * d
        sortie = -1.0
        m = FIN
        j = e
        derniere = min(n - 1, e + max_barres)
        while j <= derniere:
            if j > e:
                if (s > 0 and ouv[j] <= stop) or (s < 0 and ouv[j] >= stop):
                    sortie, m = ouv[j], GAP
                    break
            touche_stop = bas[j] <= stop if s > 0 else haut[j] >= stop
            if touche_stop:
                sortie, m = stop, STOP
                break
            touche_cible = haut[j] >= cible if s > 0 else bas[j] <= cible
            if touche_cible:
                sortie, m = cible, OBJECTIF
                break
            if fin_seance[j]:
                sortie, m = clo[j], SEANCE
                break
            if j - e >= max_barres:
                sortie, m = clo[j], TEMPS
                break
            j += 1
        if sortie < 0.0:
            continue                     # les données s'arrêtent : on n'étiquette pas un trade ouvert
        net = s * ((sortie - s * couts[j]) - entree)
        portage = (nuits[j] - nuits[e]) * (swap_l_prix if s > 0 else swap_c_prix)
        R[i] = (net + portage) / d
        motif[i] = m
        duree[i] = j - e
    return R, motif, duree


@njit(cache=True)
def _etiqueter_limite(ouv, haut, bas, clo, sens, retrait, stop_dist, rr, expiration, max_barres,
                      fin_seance, couts, stop_min, permis):
    """Comme `_etiqueter`, mais l'entrée est un ORDRE LIMITE posé `retrait` plus loin que le prix.

    C'est la méthode « au rabais » des scalpers : on n'achète pas au marché, on attend que le prix
    revienne. La géométrie en est changée — le stop et l'objectif partent d'un meilleur prix — et
    c'est justement ce qu'on veut mesurer. L'ordre non servi avant `expiration` est annulé, et un
    objectif touché avant le remplissage annule l'ordre (hypothèse pessimiste : on n'a pas été servi).
    """
    n = len(clo)
    R = np.full(n, np.nan)
    motif = np.full(n, np.int8(-1))
    duree = np.zeros(n, np.int32)
    for i in range(n - 1):
        if not permis[i]:
            continue
        d = stop_dist[i]
        if not (d >= stop_min and d > 0.0):
            continue
        s = 1.0 if sens > 0 else -1.0
        lim = clo[i] - s * retrait[i]
        st = lim - s * d
        ci = lim + s * rr * d
        rempli = -1
        prix = 0.0
        j = i + 1
        while j <= min(i + expiration, n - 1):
            if (s > 0 and haut[j] >= ci) or (s < 0 and bas[j] <= ci):
                break
            if fin_seance[j]:
                break
            if (s > 0 and bas[j] <= lim) or (s < 0 and haut[j] >= lim):
                rempli = j
                prix = min(lim, ouv[j]) if s > 0 else max(lim, ouv[j])
                break
            j += 1
        if rempli < 0:
            continue
        entree = prix + s * couts[rempli]
        sortie = -1.0
        m = FIN
        j = rempli
        derniere = min(n - 1, rempli + max_barres)
        while j <= derniere:
            if j > rempli and ((s > 0 and ouv[j] <= st) or (s < 0 and ouv[j] >= st)):
                sortie, m = ouv[j], GAP
                break
            if (s > 0 and bas[j] <= st) or (s < 0 and haut[j] >= st):
                sortie, m = st, STOP
                break
            if j > rempli and ((s > 0 and haut[j] >= ci) or (s < 0 and bas[j] <= ci)):
                sortie, m = ci, OBJECTIF
                break
            if fin_seance[j]:
                sortie, m = clo[j], SEANCE
                break
            if j - rempli >= max_barres:
                sortie, m = clo[j], TEMPS
                break
            j += 1
        if sortie < 0.0:
            continue
        R[i] = s * ((sortie - s * couts[j]) - entree) / d
        motif[i] = m
        duree[i] = j - i
    return R, motif, duree


@dataclass
class Etiquettes:
    base: str
    tf: str
    sens: int
    schema: str
    R: np.ndarray                 # NaN = barre non étiquetée (hors fenêtre, stop trop court, fin des données)
    motif: np.ndarray             # -1 = non étiquetée
    duree: np.ndarray             # en barres
    temps: np.ndarray

    def valides(self) -> np.ndarray:
        return self.motif >= 0

    def objectif(self) -> np.ndarray:
        return self.motif == OBJECTIF

    def taux_objectif(self) -> float:
        v = self.valides()
        return float(self.objectif()[v].mean()) if v.any() else float("nan")

    def esperance(self) -> float:
        v = self.valides()
        return float(self.R[v].mean()) if v.any() else float("nan")

    def resume(self) -> dict:
        v = self.valides()
        n = int(v.sum())
        if not n:
            return {"barres": 0}
        R = self.R[v]
        return {"barres": n, "taux_objectif": round(self.taux_objectif(), 4),
                "esperance_R": round(float(R.mean()), 4),
                "duree_mediane_barres": int(np.median(self.duree[v])),
                "part_fin_journee": round(float((self.motif[v] == SEANCE).mean()), 4),
                "part_stop": round(float((self.motif[v] == STOP).mean()), 4)}


def etiqueter(serie: Serie, *, stop_dist: np.ndarray, sens: int, rr: float = 2.0,
              permis: np.ndarray | None = None, max_barres: int | None = None,
              schema: str = "") -> Etiquettes:
    """Étiquette chaque barre permise : que serait-il arrivé en entrant à la barre suivante ?"""
    from .intraday import minutes_et_jours
    minute, jour = minutes_et_jours(serie.temps)      # un seul calcul de fuseau pour les deux masques
    if permis is None:
        permis = masque_entree(serie.base, serie.temps, minute=minute, jour=jour)
    fs = fin_de_journee(serie.base, serie.temps, minute=minute, jour=jour)
    if max_barres is None:                     # borne haute : une journée entière de barres
        max_barres = int(24 * 60 / serie.minutes)
    R, motif, duree = _etiqueter(
        serie.ouverture, serie.haut, serie.bas, serie.cloture, int(sens),
        np.asarray(stop_dist, np.float64), float(rr), int(max_barres), fs.astype(np.bool_),
        serie.couts_prix(), serie.swap_long_pts * serie.point, serie.swap_court_pts * serie.point,
        serie.nuits_cumul, float(serie.stop_min_prix), permis.astype(np.bool_))
    return Etiquettes(serie.base, serie.tf, int(sens), schema, R, motif, duree, serie.temps)


def distances(serie: Serie, schema: str) -> np.ndarray:
    """Le schéma de stop, par son nom. `pts1200` = 1 200 points fixes (la forme la plus lisible :
    le coût en R se lit directement), sinon un des `SCHEMAS` en ATR."""
    if schema.startswith("pts"):
        return stops_points(serie, float(schema[3:]))
    return SCHEMAS[schema][0](serie)


def etiqueter_limite(serie: Serie, *, stop_dist: np.ndarray, retrait: np.ndarray, sens: int,
                     rr: float = 2.0, expiration: int = 30, permis: np.ndarray | None = None,
                     max_barres: int | None = None, schema: str = "") -> Etiquettes:
    """L'étiquette d'une entrée LIMITE : et si on avait attendu un meilleur prix ?"""
    from .intraday import minutes_et_jours
    minute, jour = minutes_et_jours(serie.temps)
    if permis is None:
        permis = masque_entree(serie.base, serie.temps, minute=minute, jour=jour)
    fs = fin_de_journee(serie.base, serie.temps, minute=minute, jour=jour)
    if max_barres is None:
        max_barres = int(24 * 60 / serie.minutes)
    R, motif, duree = _etiqueter_limite(
        serie.ouverture, serie.haut, serie.bas, serie.cloture, int(sens),
        np.asarray(retrait, np.float64), np.asarray(stop_dist, np.float64), float(rr),
        int(expiration), int(max_barres), fs.astype(np.bool_), serie.couts_prix(),
        float(serie.stop_min_prix), permis.astype(np.bool_))
    return Etiquettes(serie.base, serie.tf, int(sens), schema, R, motif, duree, serie.temps)


def deux_sens(serie: Serie, schema: str = "atr14x2", **kw) -> dict[int, Etiquettes]:
    """Achat et vente sur le même schéma de stop : les deux moitiés de la même question."""
    stop = distances(serie, schema)
    return {s: etiqueter(serie, stop_dist=stop, sens=s, schema=schema, **kw) for s in (1, -1)}
