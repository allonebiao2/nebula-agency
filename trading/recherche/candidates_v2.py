# -*- coding: utf-8 -*-
"""
Les familles de SCALPING de la vague 2 : sept mécanismes, chacun avec sa raison d'exister.

    python -m trading.recherche.lancer_v2 --tour 6

Chaque famille répond à « pourquoi le prix irait-il 2 fois plus loin dans un sens que dans l'autre,
maintenant ? ». Une famille sans réponse à cette question n'est pas une stratégie, c'est un dessin.
Toutes ferment leur position **le jour même** (`intraday.fin_de_journee`), entrent à l'ouverture de
la barre suivante et paient le spread de la minute.

⚠️ Les grilles de réglages sont écrites ici, AVANT le premier résultat, et chaque combinaison compte
comme un test au registre.
"""
from __future__ import annotations

import numpy as np

from .banc import Candidate, Ordres, Serie, Signaux
from .caracteristiques import _cumul_par_jour, _valeur_veille
from .etiquettes import atr
from .intraday import fin_de_journee, jour_ny, minutes_et_jours

TOUTES = ("M1", "M5", "M15")


def _base(serie: Serie):
    minute, jsem = minutes_et_jours(serie.temps)
    return minute, jsem, fin_de_journee(serie.base, serie.temps, minute=minute, jour=jsem)


def _vide(serie: Serie, stop: np.ndarray, **kw) -> Signaux:
    return Signaux(sens=np.zeros(len(serie), np.int8), stop_dist=stop, **kw)


def _signaux(serie: Serie, sens: np.ndarray, stop: np.ndarray, fs: np.ndarray, *,
             max_minutes: int = 240, rr: float = 2.0) -> Signaux:
    minute, jsem = minutes_et_jours(serie.temps)
    from .intraday import masque_entree
    sens = np.where(masque_entree(serie.base, serie.temps, minute=minute, jour=jsem), sens, 0)
    return Signaux(sens=sens.astype(np.int8), stop_dist=stop, rr=rr,
                   max_barres=max(1, int(max_minutes / serie.minutes)), fin_seance=fs)


# --------------------------------------------------------------------------- #
#  1. Ouverture de séance : la première impulsion, et son contraire
# --------------------------------------------------------------------------- #

def ouverture_seance(serie: Serie, *, mode: str = "suivre", fenetre_min: int = 30,
                     stop_atr: float = 2.0, delai_min: int = 0) -> Signaux:
    """Le marché ouvre, une amplitude se forme, puis on la suit (cassure) ou on la contredit (retour).

    Le mécanisme : à l'ouverture d'une séance, les ordres accumulés pendant la fermeture arrivent
    d'un coup. Soit ils poussent le prix dans une direction (cassure), soit ils l'exagèrent et le
    prix revient (retour). Les deux existent, à des moments différents : c'est ce qu'on mesure.
    """
    minute, jsem, fs = _base(serie)
    a = atr(serie, 14)
    ouverture = {"EURUSD": 2 * 60, "NAS100": 9 * 60 + 30}[serie.base]   # Francfort · cash New York
    jour = jour_ny(serie.temps)
    dans_fenetre = (minute >= ouverture) & (minute < ouverture + fenetre_min) & (jsem < 5)
    haut_f = np.where(dans_fenetre, serie.haut, -np.inf)
    bas_f = np.where(dans_fenetre, serie.bas, np.inf)
    haut_ouv = _cumul_par_jour(haut_f, jour, "max")
    bas_ouv = _cumul_par_jour(bas_f, jour, "min")
    apres = minute >= ouverture + fenetre_min + delai_min
    pret = apres & np.isfinite(haut_ouv) & np.isfinite(bas_ouv) & (haut_ouv > bas_ouv)
    casse_haut = pret & (serie.cloture > haut_ouv)
    casse_bas = pret & (serie.cloture < bas_ouv)
    if mode == "suivre":
        sens = np.where(casse_haut, 1, np.where(casse_bas, -1, 0))
    else:                                        # retour : on contredit la cassure
        sens = np.where(casse_haut, -1, np.where(casse_bas, 1, 0))
    # Un seul signal par jour et par sens : la cassure, pas chaque barre qui suit.
    premier = np.concatenate(([True], (sens[1:] != 0) & (sens[:-1] == 0)))
    sens = np.where(premier, sens, 0)
    return _signaux(serie, sens, stop_atr * a, fs)


# --------------------------------------------------------------------------- #
#  2. Balayage d'un niveau, puis rejet
# --------------------------------------------------------------------------- #

def balayage_niveau(serie: Serie, *, niveau: str = "veille", stop_atr: float = 1.5,
                    confirmation: int = 1) -> Signaux:
    """Le prix dépasse un niveau connu de tous, puis referme de l'autre côté : les stops ont été pris.

    Le mécanisme est réel et documenté par tous les carnets d'ordres : sous un plus bas de la veille
    dorment des stops de vente ; une fois pris, le carburant est consommé et le prix revient.
    """
    minute, jsem, fs = _base(serie)
    a = atr(serie, 14)
    jour = jour_ny(serie.temps)
    if niveau == "veille":
        haut = _valeur_veille(serie.haut, jour, "max")
        bas = _valeur_veille(serie.bas, jour, "min")
    else:                                          # extrêmes de la journée en cours, avant la barre
        haut = np.concatenate(([np.nan], _cumul_par_jour(serie.haut, jour, "max")[:-1]))
        bas = np.concatenate(([np.nan], _cumul_par_jour(serie.bas, jour, "min")[:-1]))
    balaye_haut = (serie.haut > haut) & (serie.cloture < haut)
    balaye_bas = (serie.bas < bas) & (serie.cloture > bas)
    if confirmation > 1:                            # exiger N barres de suite du bon côté
        for k in range(1, confirmation):
            balaye_haut &= np.concatenate((np.zeros(k, bool), (serie.cloture < haut)[:-k]))
            balaye_bas &= np.concatenate((np.zeros(k, bool), (serie.cloture > bas)[:-k]))
    sens = np.where(balaye_haut, -1, np.where(balaye_bas, 1, 0))
    return _signaux(serie, sens, stop_atr * a, fs)


# --------------------------------------------------------------------------- #
#  3. Compression puis expansion
# --------------------------------------------------------------------------- #

def compression(serie: Serie, *, barres: int = 30, seuil: float = 0.5, stop_atr: float = 1.5) -> Signaux:
    """Une amplitude anormalement petite précède souvent une grande : on entre à la sortie de la boîte.

    Le mécanisme : la volatilité est persistante, donc une compression se paie plus tard. Le pari
    n'est pas sur le sens mais sur l'AMPLITUDE ; le sens vient de la sortie de la boîte.
    """
    minute, jsem, fs = _base(serie)
    import pandas as pd
    a = atr(serie, 14)
    h = pd.Series(serie.haut).rolling(barres).max().to_numpy()
    b = pd.Series(serie.bas).rolling(barres).min().to_numpy()
    etendue = h - b
    reference = pd.Series(etendue).rolling(20 * barres, min_periods=barres).median().to_numpy()
    serre = etendue < seuil * reference
    hier_serre = np.concatenate(([False], serre[:-1]))
    casse_haut = hier_serre & (serie.cloture > np.concatenate(([np.nan], h[:-1])))
    casse_bas = hier_serre & (serie.cloture < np.concatenate(([np.nan], b[:-1])))
    sens = np.where(casse_haut, 1, np.where(casse_bas, -1, 0))
    return _signaux(serie, sens, stop_atr * a, fs)


# --------------------------------------------------------------------------- #
#  4. Excès de séance : le mouvement trop rapide
# --------------------------------------------------------------------------- #

def exces(serie: Serie, *, minutes: int = 15, seuil_atr: float = 3.0, mode: str = "retour",
          stop_atr: float = 1.5) -> Signaux:
    """Un mouvement de plusieurs ATR en quelques minutes : liquidation, pas information.

    Le mécanisme du retour : une liquidation forcée (appel de marge, stop en cascade) déplace le prix
    au-delà de ce que l'information justifie. Le mode « suivre » teste l'hypothèse inverse, celle de
    l'information vraie. On ne décide pas d'avance laquelle est bonne : on mesure.
    """
    minute, jsem, fs = _base(serie)
    a = atr(serie, 14)
    p = max(1, int(minutes / serie.minutes))
    prec = np.concatenate((np.full(p, np.nan), serie.cloture[:-p]))
    with np.errstate(invalid="ignore"):
        bouge = (serie.cloture - prec) / a
    monte, descend = bouge > seuil_atr, bouge < -seuil_atr
    sens = (np.where(monte, -1, np.where(descend, 1, 0)) if mode == "retour"
            else np.where(monte, 1, np.where(descend, -1, 0)))
    premier = np.concatenate(([True], (sens[1:] != 0) & (sens[:-1] == 0)))
    return _signaux(serie, np.where(premier, sens, 0), stop_atr * a, fs)


# --------------------------------------------------------------------------- #
#  5. Entrée au rabais : ordre limite sur retour de prix
# --------------------------------------------------------------------------- #

def rabais(serie: Serie, *, tendance: int = 60, retrait: float = 0.25, stop_atr: float = 1.5,
           expiration_min: int = 30, remplissage: float = 0.0) -> Ordres:
    """On ne poursuit pas le prix : on pose un ordre LIMITE plus bas (ou plus haut) et on attend.

    La géométrie change vraiment : depuis un meilleur prix, l'objectif de 2 R est plus près en valeur
    absolue. Mesuré le 2026-09-17 sur NAS100 M1 : à 0,25 R de retrait, le taux d'objectif passe
    légèrement au-dessus du point mort — la seule piste de la vague 1 qui ne soit pas plate.
    ⚠️ Et le piège mesuré le même jour : ne JAMAIS juger deux ordres limites miroirs par « au moins
    un des deux gagne ». À 0,5 R de retrait ils sont exactement opposés, donc l'un gagne toujours :
    99 % de « plafond » qui ne veut rien dire.
    """
    import pandas as pd
    minute, jsem, fs = _base(serie)
    from .intraday import masque_entree
    a = atr(serie, 14)
    p = max(1, int(tendance / serie.minutes))
    ema = pd.Series(serie.cloture).ewm(span=p, adjust=False, min_periods=p).mean().to_numpy()
    d = stop_atr * a
    permis = masque_entree(serie.base, serie.temps, minute=minute, jour=jsem) & np.isfinite(d) & np.isfinite(ema)
    sens = np.where(permis & (serie.cloture > ema), 1, np.where(permis & (serie.cloture < ema), -1, 0))
    i = np.flatnonzero(sens != 0)
    s = sens[i].astype(np.int8)
    limite = serie.cloture[i] - s * retrait * d[i]
    expire = i + max(1, int(expiration_min / serie.minutes))
    return Ordres(pose=i.astype(np.int64), sens=s, limite=limite, stop=limite - s * d[i],
                  cible=limite + s * 2.0 * d[i], expire=expire.astype(np.int64),
                  max_barres=max(1, int(240 / serie.minutes)), fin_seance=fs,
                  k_remplissage=remplissage)


# --------------------------------------------------------------------------- #
#  6. Suite de bougies dans le même sens
# --------------------------------------------------------------------------- #

def suite(serie: Serie, *, longueur: int = 4, mode: str = "retour", stop_atr: float = 1.5) -> Signaux:
    """N bougies du même côté : épuisement (retour) ou élan (suivre) ?

    C'est la forme la plus simple d'une question qui décide de tout en scalping : le très court terme
    revient-il sur lui-même, ou continue-t-il ? La réponse n'est pas la même selon l'instrument et
    l'heure, et elle est mesurable.
    """
    minute, jsem, fs = _base(serie)
    a = atr(serie, 14)
    signe = np.sign(serie.cloture - serie.ouverture)
    meme = np.ones(len(serie), bool)
    for k in range(1, longueur):
        meme &= np.concatenate((np.zeros(k, bool), (signe[k:] == signe[:-k])))
    monte = meme & (signe > 0)
    descend = meme & (signe < 0)
    sens = (np.where(monte, -1, np.where(descend, 1, 0)) if mode == "retour"
            else np.where(monte, 1, np.where(descend, -1, 0)))
    premier = np.concatenate(([True], (sens[1:] != 0) & (sens[:-1] == 0)))
    return _signaux(serie, np.where(premier, sens, 0), stop_atr * a, fs)


# --------------------------------------------------------------------------- #
#  7. Heure + volatilité : le créneau où le mouvement paie le spread
# --------------------------------------------------------------------------- #

def creneau_volatil(serie: Serie, *, debut_h: int = 9, duree_h: int = 2, seuil_vol: float = 1.2,
                    mode: str = "suivre", stop_atr: float = 1.5) -> Signaux:
    """Une heure précise, et seulement quand la volatilité y est au-dessus de son ordinaire.

    Le mécanisme : le coût est fixe, le mouvement ne l'est pas. Les minutes qui paient sont celles où
    l'amplitude dépasse nettement le spread. On n'invente pas un signal : on prend la direction de la
    dernière impulsion, et on ne la prend qu'au bon moment.
    """
    minute, jsem, fs = _base(serie)
    a14, a60 = atr(serie, 14), atr(serie, 60)
    with np.errstate(invalid="ignore", divide="ignore"):
        vol = a14 / a60
    p = max(1, int(15 / serie.minutes))
    prec = np.concatenate((np.full(p, np.nan), serie.cloture[:-p]))
    impulsion = np.sign(serie.cloture - prec)
    dans = (minute >= debut_h * 60) & (minute < (debut_h + duree_h) * 60) & (vol >= seuil_vol)
    sens = np.where(dans, impulsion if mode == "suivre" else -impulsion, 0)
    premier = np.concatenate(([True], (sens[1:] != 0) & (sens[:-1] == 0)))
    return _signaux(serie, np.where(premier, sens, 0), stop_atr * a14, fs)


CANDIDATES = [
    Candidate("ouverture_seance", "Ouverture de séance (cassure ou retour)", "vague 2 · mécanisme",
              ouverture_seance,
              {"mode": ["suivre", "retour"], "fenetre_min": [15, 30, 60], "stop_atr": [1.5, 3.0],
               "delai_min": [0]}, TOUTES),
    Candidate("balayage_niveau", "Balayage d'un niveau puis rejet", "vague 2 · mécanisme",
              balayage_niveau,
              {"niveau": ["veille", "jour"], "stop_atr": [1.0, 2.0], "confirmation": [1, 2]}, TOUTES),
    Candidate("compression", "Compression puis expansion", "vague 2 · mécanisme", compression,
              {"barres": [20, 60], "seuil": [0.4, 0.6], "stop_atr": [1.0, 2.0]}, TOUTES),
    Candidate("exces", "Excès de séance (retour ou suite)", "vague 2 · mécanisme", exces,
              {"minutes": [5, 15, 30], "seuil_atr": [2.0, 3.5], "mode": ["retour", "suivre"],
               "stop_atr": [1.0, 2.0]}, TOUTES),
    Candidate("suite", "Suite de bougies (épuisement ou élan)", "vague 2 · mécanisme", suite,
              {"longueur": [3, 4, 5], "mode": ["retour", "suivre"], "stop_atr": [1.0, 2.0]}, TOUTES),
    Candidate("creneau_volatil", "Créneau horaire volatil", "vague 2 · mécanisme", creneau_volatil,
              {"debut_h": [3, 9, 13], "duree_h": [2], "seuil_vol": [1.0, 1.3],
               "mode": ["suivre", "retour"], "stop_atr": [1.0, 2.0]}, TOUTES),
    Candidate("rabais", "Entrée limite au rabais, dans le sens de la tendance", "vague 2 · mécanisme",
              rabais, {"tendance": [60, 240], "retrait": [0.25, 0.5], "stop_atr": [1.0, 2.0],
                       "expiration_min": [15, 60]}, TOUTES),
    # LE MÊME, avec l'hypothèse de remplissage réaliste : le prix doit TRAVERSER la limite d'un
    # spread complet, parce qu'un achat s'exécute au prix acheteur. L'écart entre les deux lignes
    # mesure exactement ce que l'hypothèse optimiste fabriquait.
    Candidate("rabais_reel", "Entrée limite, remplissage réaliste (traverse d'un spread)",
              "vague 2 · mécanisme", rabais,
              {"tendance": [60, 240], "retrait": [0.25, 0.5], "stop_atr": [1.0, 2.0],
               "expiration_min": [15, 60], "remplissage": [2.0]}, TOUTES),
    Candidate("rabais_prudent", "Entrée limite, remplissage prudent (traverse d'un spread et demi)",
              "vague 2 · mécanisme", rabais,
              {"tendance": [60, 240], "retrait": [0.25, 0.5], "stop_atr": [1.0, 2.0],
               "expiration_min": [15, 60], "remplissage": [3.0]}, TOUTES),
]
