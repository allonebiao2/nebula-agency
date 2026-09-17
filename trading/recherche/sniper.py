# -*- coding: utf-8 -*-
"""
« My Secret 1 Minute Scalping Strategy (Sniper Entry) » (Mulham Trading / Edge Skool), rendue mécanique.

Vidéo envoyée par Mongazi le 2026-09-17 (transcription locale, hors dépôt :
`trading/rapports/recherche/videos/video_en_sniper_entry.txt`). Fiche de la méthode :
`trading/recherche/METHODE-SNIPER.md`.

LA MÉTHODE (chaque règle et le moment de la vidéo qui la donne)
  [09:25] « Attraper les balayages de liquidité M15 à haute probabilité avec le graphique M1. »
  [03:10] Direction : EMA 200 (entourée à l'écran). [04:39] Au-dessus = achats, en dessous = ventes,
          [04:57] avec une structure valide, pas un prix qui zigzague autour de la moyenne.
  [06:16] Continuation seulement : en baisse on vise les SOMMETS, en hausse les CREUX.
  [09:45] Étape 1 : marquer un sommet/creux M15 dans le sens de la tendance (de préférence dans un
          imbalance, et partie d'une structure propre).
  [10:20] Étape 2 : attendre une CLÔTURE sous le sommet (au-dessus du creux) : le rejet par la mèche.
  [22:15] [25:27] La bougie qui prend le sommet doit être HAUSSIÈRE (et baissière pour un creux) :
          clôturée dans le sens du trade, « le mouvement est déjà parti », pas de trade.
  [10:45] Étape 3 : tracer le rectangle et regarder l'ouverture de la bougie M15 suivante.
  [11:16] [14:39] Rectangle = de la CLÔTURE de cette bougie à son extrême (la mèche).
  [15:06] Entrée : une bougie M1 CLÔTURE hors du rectangle. [20:33] Valide tant qu'aucune clôture
          ne « déplace » au-delà du sommet, même si une mèche le reprend.
  [15:56] [23:20] Stop « légèrement au-dessus du sommet, à cause du spread ».
  [01:18] Objectif : au moins 3:1 ; [16:06] [23:31] ou le prochain niveau clé.
  [12:36] [13:12] [20:10] Asie (début), Londres, New York et un peu après ; pas après New York.

CE QUE L'IMAGE A TRANCHÉ (planches regardées le 2026-09-17)
  · Graphique « Euro / U.S. Dollar · 15 · Tickmill », heure de NEW YORK. Les quatre exemples se
    retrouvent AU DIXIÈME DE PIP dans les bougies Deriv (serveur en UTC) :
      31/10/2025 01:15 UTC  vente, plus haut 1,15775, clôture 1,15766  (Asie)
      31/10/2025 06:15 UTC  vente, plus haut 1,15734                   (Londres)
      31/10/2025 15:45 UTC  vente, plus haut 1,15430, clôture 1,15409  (New York + 1 h 45)
      04/11/2025 07:30 UTC  vente, plus haut 1,15336, clôture 1,15309  (Londres)
  · Le sommet balayé peut être un sommet de TROIS bougies formé juste avant (exemple 1), ou des
    sommets égaux (exemple 4) : pivot à 1 bougie de chaque côté, « >= » à droite.
  · Boîtes de séance de son indicateur, en heure de New York : Asie 20:00-00:00, Londres
    02:00-05:00, New York 07:00-10:00. Il prend encore l'exemple 3, clôturé à 12:00.
  · Stops de 1,6 à 4 pips. ⚠️ Deriv impose 2 pips entre le prix et le stop : le stop de l'exemple 1
    ne pouvait pas être posé chez Deriv.

TRADUCTIONS MÉCANIQUES D'UN GESTE DISCRÉTIONNAIRE (écrites pour qu'on les conteste)
  · « Structure valide » = la dernière cassure de structure MAJEURE va dans le sens du trade (pivots
    M15 de 12 bougies de chaque côté, ≈ 3 h, l'équivalent de pivots H1 à 3 bougies), ET les 8
    dernières clôtures M15 (2 h) sont du bon côté de l'EMA 200.
    ⚠️ Réglage choisi sur les EXEMPLES de la vidéo, avant tout résultat : avec des pivots de 5
    bougies, un simple repli (là où se produit le balayage) inverse la structure et AUCUN des 4
    exemples ne passe ; à 12, les exemples 1, 2 et 3 passent. L'exemple 4 ne passe pas pour une
    autre raison : chez Deriv la bougie clôture à 1,15309, 0,3 pip AU-DESSUS des sommets égaux
    (1,15306) ; chez Tickmill elle clôturait à 1,15311 et ses sommets ne sont pas lisibles.
  · « Sommet » = pivot M15 de 3 bougies, jamais dépassé depuis, de moins de 24 h.
  · Si la bougie dépasse plusieurs sommets, le niveau est le plus haut d'entre eux.
  · « Légèrement au-dessus » = extrême depuis la bougie de balayage + 1,5 spread de la minute.
  · Validité : 4 bougies M15 après le balayage (il attend plusieurs bougies dans ses exemples).
  · Sortie forcée à 16:55 New York (le marché ferme à 17:00, le spread y explose).
  · Objectif fixe en R (3 R = son minimum) ; variante « niveau opposé » : le creux M15 le plus proche
    au-delà de 3 R.

SIMULATION (plus dure que TradingView, exprès)
  · Les bougies MT5 sont en BID. Un achat entre à l'ASK et sort au BID ; une vente entre au BID et
    son stop se déclenche quand l'ASK le touche. Spread = celui de la MINUTE (profil mesuré sur les
    ticks, `spread_horaire.py`), glissement défavorable à l'entrée, au stop et en sortie forcée.
  · Entrée à l'ouverture de la bougie M1 qui suit la clôture déclencheuse.
  · Stop avant objectif dans une même bougie. Stop plus court que le minimum du courtier (stops
    level + spread) : élargi à ce minimum (variante : trade sauté).
  · Une position à la fois par instrument ; un balayage pendant un trade est ignoré.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd
from numba import njit

from ..strategies.indicateurs import ema
from . import annonces as mod_annonces
from .banc import Agregat, Serie, Trades, agreger

STOP, OBJECTIF, TEMPS, GAP, SEANCE, FIN, POINT_MORT, ANNONCE = 0, 1, 2, 3, 4, 5, 6, 7

# Séances de l'auteur (heure de New York), sur l'heure de CLÔTURE de la bougie de balayage,
# en minutes depuis minuit. Bornes incluses. 00:00 = fin de la boîte Asie.
SEANCES_AUTEUR = ((20 * 60 + 15, 24 * 60), (0, 0), (2 * 60 + 15, 5 * 60), (7 * 60 + 15, 12 * 60))
FIN_FORCEE_NY = (16 * 60 + 55, 17 * 60)


@dataclass(frozen=True)
class Reglages:
    ema: int = 200
    pivot_niveau: int = 1              # sommets/creux balayés : 1 bougie de chaque côté
    pivot_structure: int = 12          # cassures de structure : 12 bougies M15 de chaque côté (≈ 3 h)
    anti_zigzag: int = 8               # clôtures M15 consécutives du bon côté de l'EMA (0 = sans)
    age_max: int = 96                  # âge maximal d'un niveau, en bougies M15
    fvg: bool = False                  # niveau dans un imbalance non rempli EXIGÉ
    validite: int = 4                  # bougies M15 pendant lesquelles on attend la clôture M1
    dernier_creux_m1: bool = False     # la clôture M1 doit aussi passer le dernier creux M1
    rr: float = 3.0                    # > 0 : objectif fixe ; < 0 : niveau opposé, plancher |rr|
    seances: str = "auteur"            # "auteur" · "toutes" · "heures"
    heures_ny: tuple = ()              # pour "heures" : heures NY (0-23) de la clôture du balayage
    annonces: int = 0                  # 0 sans filtre · 1 entrées bloquées · 2 bloquées + sortie avant
    avant_min: int = 30                # fenêtre de l'agent en direct (noyau/calendrier.py)
    apres_min: int = 15
    sortie_avant_min: int = 5          # mode 2 : on sort à la clôture de la bougie qui précède
    stop_trop_court: str = "elargir"   # "elargir" au minimum du courtier, ou "sauter"
    tampon_spreads: float = 1.5
    couts: float = 1.0                 # multiplicateur du spread ET du glissement


# --------------------------------------------------------------------------- #
#  Préparation (une fois par série) : ce qui ne dépend pas des réglages
# --------------------------------------------------------------------------- #

@dataclass
class Preparation:
    serie: Serie
    m15: Agregat
    m15_de: np.ndarray               # indice M15 de chaque bougie M1
    fin_m15: np.ndarray              # la bougie M1 est la dernière de sa bougie M15
    ny15_minute: np.ndarray          # minute NY de la CLÔTURE de chaque bougie M15
    ny15_heure: np.ndarray
    ny15_jour: np.ndarray            # lundi = 0
    fin_forcee: np.ndarray           # M1 : clôture dans [16:55, 17:00) New York
    spread_pts: np.ndarray           # M1 : spread de la minute, en points
    glissement_pts: float
    stops_level_pts: float
    annonces: np.ndarray             # datetime64[s] UTC
    couverture_annonces: tuple
    creux_m1: np.ndarray = field(default=None)    # dernier creux M1 confirmé (pivot 1), NaN sinon
    sommet_m1: np.ndarray = field(default=None)
    _ema: dict = field(default_factory=dict)
    _masques_annonces: dict = field(default_factory=dict)

    def ema15(self, periode: int) -> np.ndarray:
        if periode not in self._ema:
            self._ema[periode] = ema(self.m15.cloture, periode)
        return self._ema[periode]

    def masques_annonces(self, avant: int, apres: int, sortie_avant: int):
        cle = (avant, apres, sortie_avant)
        if cle not in self._masques_annonces:
            t = self.serie.temps
            bloque = mod_annonces.fenetre_bloquee(t, self.annonces, avant_min=avant, apres_min=apres)
            prochaine = mod_annonces.prochaine_annonce(t, self.annonces)
            fin_barre = t.astype("datetime64[s]") + np.timedelta64(60, "s")
            sortir = (prochaine - fin_barre) <= np.timedelta64(sortie_avant * 60, "s")
            self._masques_annonces[cle] = (bloque, sortir)
        return self._masques_annonces[cle]


def _minutes_ny(temps_utc: np.ndarray):
    idx = pd.DatetimeIndex(temps_utc).tz_localize("UTC").tz_convert("America/New_York")
    return (idx.hour * 60 + idx.minute).to_numpy(), idx.hour.to_numpy(), idx.dayofweek.to_numpy()


@njit(cache=True)
def _pivots_m1(haut, bas):
    n = len(haut)
    creux = np.full(n, np.nan)
    sommet = np.full(n, np.nan)
    dc = np.nan
    ds = np.nan
    for i in range(n):
        # pivot en p = i - 1, confirmé par la bougie i (connue à sa clôture)
        p = i - 1
        if p >= 1:
            if bas[p] < bas[p - 1] and bas[p] <= bas[i]:
                dc = bas[p]
            if haut[p] > haut[p - 1] and haut[p] >= haut[i]:
                ds = haut[p]
        creux[i] = dc
        sommet[i] = ds
    return creux, sommet


def preparer(serie: Serie, *, spread_constant: float | None = None) -> Preparation:
    """`spread_constant` (points) remplace le profil minute par minute (contrôles, ou profil absent)."""
    from . import spread_horaire
    from ..noyau.donnees_mt5 import specs_et_couts
    assert serie.tf == "M1", "la méthode entre en M1"
    m15 = agreger(serie, "M15")
    debut15 = serie.temps.astype("datetime64[m]").astype("int64") // 15
    m15_de = np.searchsorted(m15.debut.astype("datetime64[m]").astype("int64") // 15, debut15)
    fin_m15 = np.ones(len(serie), dtype=bool)
    fin_m15[:-1] = m15_de[1:] != m15_de[:-1]
    minute15, heure15, jour15 = _minutes_ny(m15.debut + np.timedelta64(15 * 60, "s"))
    minute1, _, _ = _minutes_ny(serie.temps + np.timedelta64(60, "s"))
    fin_forcee = (minute1 >= FIN_FORCEE_NY[0]) & (minute1 < FIN_FORCEE_NY[1])
    specs, couts = specs_et_couts(serie.base)
    median = couts.spread_points if couts else 3.0
    if spread_constant is not None:
        spread = np.full(len(serie), float(spread_constant))
    else:
        try:
            spread = spread_horaire.spread_par_barre(serie.base, serie.temps)
        except FileNotFoundError:
            spread = np.full(len(serie), float(median))
    try:
        ann, _, couverture = mod_annonces.charger(serie.base)
    except FileNotFoundError:
        ann, couverture = np.array([], dtype="datetime64[s]"), ("", "")
    creux, sommet = _pivots_m1(serie.haut, serie.bas)
    return Preparation(serie=serie, m15=m15, m15_de=m15_de.astype(np.int64), fin_m15=fin_m15,
                       ny15_minute=minute15, ny15_heure=heure15, ny15_jour=jour15, fin_forcee=fin_forcee,
                       spread_pts=spread.astype(np.float64),
                       glissement_pts=max(1.0, 0.15 * float(spread_constant if spread_constant is not None else median)),
                       stops_level_pts=float(specs.stops_level_points if specs else 0),
                       annonces=ann, couverture_annonces=couverture, creux_m1=creux, sommet_m1=sommet)


def seances_permises(prep: Preparation, r: Reglages) -> np.ndarray:
    m, h, j = prep.ny15_minute, prep.ny15_heure, prep.ny15_jour
    if r.seances == "toutes":
        ok = np.ones(len(m), dtype=bool)
    elif r.seances == "auteur":
        ok = np.zeros(len(m), dtype=bool)
        for a, b in SEANCES_AUTEUR:
            ok |= (m >= a) & (m <= b)
    elif r.seances == "heures":
        ok = np.isin(h, np.array(r.heures_ny, dtype=np.int64))
    else:
        raise ValueError(r.seances)
    # jamais dans la dernière heure avant la fermeture de 17:00 New York
    return ok & ~((m >= 16 * 60) & (m < 17 * 60))


# --------------------------------------------------------------------------- #
#  Étapes 1 et 2 : le balayage M15 (compilé)
# --------------------------------------------------------------------------- #

@njit(cache=True)
def _balayages(o, h, l, c, moyenne, permis, k_niv, k_str, anti_zigzag, age_max, fvg_exige):
    n = len(c)
    sens = np.zeros(n, np.int8)
    rect_cloture = np.zeros(n)
    rect_extreme = np.zeros(n)
    niveau = np.zeros(n)
    dans_fvg = np.zeros(n, np.bool_)
    cap = n + 1
    sh_i = np.empty(cap, np.int64)
    sh_v = np.empty(cap)
    sh_vivant = np.zeros(cap, np.bool_)
    nsh = 0
    sl_i = np.empty(cap, np.int64)
    sl_v = np.empty(cap)
    sl_vivant = np.zeros(cap, np.bool_)
    nsl = 0
    debut_sh = 0
    debut_sl = 0
    tendance = 0
    str_haut = np.nan
    str_bas = np.nan
    for j in range(n):
        # (a) cassure de structure à la clôture de j, pivots de structure confirmés jusqu'à j-1
        if not np.isnan(str_haut) and c[j] > str_haut:
            tendance = 1
            str_haut = np.nan
        if not np.isnan(str_bas) and c[j] < str_bas:
            tendance = -1
            str_bas = np.nan
        # (b) balayage : niveaux confirmés jusqu'à j-1, jamais dépassés avant j
        if permis[j] and not np.isnan(moyenne[j]):
            while debut_sh < nsh and j - sh_i[debut_sh] > age_max:
                debut_sh += 1
            while debut_sl < nsl and j - sl_i[debut_sl] > age_max:
                debut_sl += 1
            # vente : sommet pris par une bougie HAUSSIÈRE qui clôture sous le niveau
            if c[j] > o[j] and c[j] < moyenne[j] and tendance == -1:
                ok_cote = True
                for m in range(anti_zigzag):
                    if j - m < 0 or np.isnan(moyenne[j - m]) or c[j - m] >= moyenne[j - m]:
                        ok_cote = False
                        break
                if ok_cote:
                    lv = -1.0
                    li = -1
                    for q in range(debut_sh, nsh):
                        if sh_vivant[q] and sh_v[q] < h[j] and sh_v[q] > lv:
                            lv = sh_v[q]
                            li = sh_i[q]
                    if li >= 0 and c[j] < lv:
                        fvg_ok = False
                        # imbalance baissier formé AVANT le sommet, où le sommet est entré, pas rempli avant j
                        maxi = -1e300
                        for q in range(j - 1, max(li - 48, 2) - 1, -1):
                            if q < j - 1 and h[q + 1] > maxi:
                                maxi = h[q + 1]
                            if q < li and l[q - 2] > h[q] and h[q] <= lv and maxi < l[q - 2]:
                                fvg_ok = True
                                break
                        if fvg_ok or not fvg_exige:
                            sens[j] = -1
                            rect_cloture[j] = c[j]
                            rect_extreme[j] = h[j]
                            niveau[j] = lv
                            dans_fvg[j] = fvg_ok
            # achat : creux pris par une bougie BAISSIÈRE qui clôture au-dessus du niveau
            if sens[j] == 0 and c[j] < o[j] and c[j] > moyenne[j] and tendance == 1:
                ok_cote = True
                for m in range(anti_zigzag):
                    if j - m < 0 or np.isnan(moyenne[j - m]) or c[j - m] <= moyenne[j - m]:
                        ok_cote = False
                        break
                if ok_cote:
                    lv = 1e300
                    li = -1
                    for q in range(debut_sl, nsl):
                        if sl_vivant[q] and sl_v[q] > l[j] and sl_v[q] < lv:
                            lv = sl_v[q]
                            li = sl_i[q]
                    if li >= 0 and c[j] > lv:
                        fvg_ok = False
                        mini = 1e300
                        for q in range(j - 1, max(li - 48, 2) - 1, -1):
                            if q < j - 1 and l[q + 1] < mini:
                                mini = l[q + 1]
                            if q < li and h[q - 2] < l[q] and l[q] >= lv and mini > h[q - 2]:
                                fvg_ok = True
                                break
                        if fvg_ok or not fvg_exige:
                            sens[j] = 1
                            rect_cloture[j] = c[j]
                            rect_extreme[j] = l[j]
                            niveau[j] = lv
                            dans_fvg[j] = fvg_ok
        # (c) les niveaux dépassés par j sont pris, qu'il y ait eu setup ou non
        for q in range(debut_sh, nsh):
            if sh_vivant[q] and h[j] > sh_v[q]:
                sh_vivant[q] = False
        for q in range(debut_sl, nsl):
            if sl_vivant[q] and l[j] < sl_v[q]:
                sl_vivant[q] = False
        # (d) pivots confirmés par la clôture de j
        p = j - k_niv
        if p - k_niv >= 0:
            est_s = True
            est_c = True
            for m in range(1, k_niv + 1):
                if not (h[p] > h[p - m] and h[p] >= h[p + m]):
                    est_s = False
                if not (l[p] < l[p - m] and l[p] <= l[p + m]):
                    est_c = False
            if est_s:
                sh_i[nsh] = p
                sh_v[nsh] = h[p]
                sh_vivant[nsh] = True
                nsh += 1
            if est_c:
                sl_i[nsl] = p
                sl_v[nsl] = l[p]
                sl_vivant[nsl] = True
                nsl += 1
        p = j - k_str
        if p - k_str >= 0:
            est_s = True
            est_c = True
            for m in range(1, k_str + 1):
                if not (h[p] > h[p - m] and h[p] >= h[p + m]):
                    est_s = False
                if not (l[p] < l[p - m] and l[p] <= l[p + m]):
                    est_c = False
            if est_s:
                str_haut = h[p]
            if est_c:
                str_bas = l[p]
    return sens, rect_cloture, rect_extreme, niveau, dans_fvg


def balayages(prep: Preparation, r: Reglages):
    m = prep.m15
    return _balayages(m.ouverture, m.haut, m.bas, m.cloture, prep.ema15(r.ema), seances_permises(prep, r),
                      r.pivot_niveau, r.pivot_structure, r.anti_zigzag, r.age_max, r.fvg)


# --------------------------------------------------------------------------- #
#  Étape 3 : le rectangle, la clôture M1, le trade (compilé)
# --------------------------------------------------------------------------- #

@njit(cache=True)
def _cible_structure(entree, d, s, plancher, j15, h15, l15, k_str):
    """Le pivot de structure opposé le plus proche au-delà de `plancher` R, jamais dépassé depuis."""
    meilleur = np.nan
    extreme = 1e300 if s < 0 else -1e300
    for p in range(j15, max(j15 - 192, k_str) - 1, -1):
        if p + k_str <= j15:
            if s < 0:
                est = True
                for m in range(1, k_str + 1):
                    if not (l15[p] < l15[p - m] and l15[p] <= l15[p + m]):
                        est = False
                if est and l15[p] < extreme and l15[p] <= entree - plancher * d:
                    if np.isnan(meilleur) or l15[p] > meilleur:
                        meilleur = l15[p]
            else:
                est = True
                for m in range(1, k_str + 1):
                    if not (h15[p] > h15[p - m] and h15[p] >= h15[p + m]):
                        est = False
                if est and h15[p] > extreme and h15[p] >= entree + plancher * d:
                    if np.isnan(meilleur) or h15[p] < meilleur:
                        meilleur = h15[p]
        # « jamais dépassé depuis » : le niveau doit rester au-delà des extrêmes postérieurs
        if s < 0:
            if l15[p] < extreme:
                extreme = l15[p]
        else:
            if h15[p] > extreme:
                extreme = h15[p]
    return meilleur


@njit(cache=True)
def _simuler(o, h, l, c, m15_de, fin_m15, spread_pts, point, gliss_pts, stops_level_pts, couts,
             sens15, rect_cloture, rect_extreme, validite, rr, tampon, elargir, dernier_extreme_m1,
             creux_m1, sommet_m1, bloque, sortir_annonce, mode_annonces, fin_forcee, nuits, swap_l, swap_c,
             h15, l15, k_str, i_debut, i_fin):
    n = len(c)
    cap = n // 10 + 16
    e_o = np.empty(cap, np.int64)
    s_o = np.empty(cap, np.int64)
    sens_o = np.empty(cap, np.int8)
    r_o = np.empty(cap)
    motif_o = np.empty(cap, np.int8)
    entree_o = np.empty(cap)
    stop_o = np.empty(cap)
    cible_o = np.empty(cap)
    sortie_o = np.empty(cap)
    d_o = np.empty(cap)
    j15_o = np.empty(cap, np.int64)
    elargi_o = np.zeros(cap, np.bool_)
    k = 0
    etat = 0                      # 0 à plat · 1 rectangle en attente · 2 en position
    p_sens = 0
    p_clo = 0.0
    p_ext = 0.0
    p_extreme_vu = 0.0
    p_j15 = 0
    t_sens = 0.0
    t_e = 0
    t_entree = 0.0
    t_stop = 0.0
    t_cible = 0.0
    t_d = 0.0
    t_elargi = False
    fin = min(i_fin, n - 2)
    for i in range(i_debut, fin + 1):
        # ---------------- gestion de la position ----------------
        if etat == 2:
            sp = spread_pts[i] * couts * point
            gl = gliss_pts * couts * point
            sortie = -1.0
            motif = FIN
            if t_sens < 0:
                if i > t_e and o[i] + sp >= t_stop:
                    sortie = o[i] + sp + gl
                    motif = GAP
                elif h[i] + sp >= t_stop:
                    sortie = t_stop + gl
                    motif = STOP
                elif l[i] + sp <= t_cible:
                    sortie = t_cible
                    motif = OBJECTIF
                elif mode_annonces == 2 and sortir_annonce[i]:
                    sortie = c[i] + sp + gl
                    motif = ANNONCE
                elif fin_forcee[i]:
                    sortie = c[i] + sp + gl
                    motif = TEMPS
                elif i == n - 2:
                    sortie = c[i] + sp + gl
                    motif = FIN
            else:
                if i > t_e and o[i] <= t_stop:
                    sortie = o[i] - gl
                    motif = GAP
                elif l[i] <= t_stop:
                    sortie = t_stop - gl
                    motif = STOP
                elif h[i] >= t_cible:
                    sortie = t_cible
                    motif = OBJECTIF
                elif mode_annonces == 2 and sortir_annonce[i]:
                    sortie = c[i] - gl
                    motif = ANNONCE
                elif fin_forcee[i]:
                    sortie = c[i] - gl
                    motif = TEMPS
                elif i == n - 2:
                    sortie = c[i] - gl
                    motif = FIN
            if sortie >= 0.0:
                net = t_sens * (sortie - t_entree)
                portage = (nuits[i] - nuits[t_e]) * (swap_l if t_sens > 0 else swap_c)
                if k >= cap:
                    break
                e_o[k] = t_e
                s_o[k] = i
                sens_o[k] = 1 if t_sens > 0 else -1
                r_o[k] = (net + portage) / t_d
                motif_o[k] = motif
                entree_o[k] = t_entree
                stop_o[k] = t_stop
                cible_o[k] = t_cible
                sortie_o[k] = sortie
                d_o[k] = t_d
                j15_o[k] = p_j15
                elargi_o[k] = t_elargi
                k += 1
                etat = 0
        # ---------------- rectangle en attente : la bougie M1 décide ----------------
        elif etat == 1:
            if p_sens < 0:
                if h[i] > p_extreme_vu:
                    p_extreme_vu = h[i]
            else:
                if l[i] < p_extreme_vu:
                    p_extreme_vu = l[i]
            declenche = (c[i] < p_clo) if p_sens < 0 else (c[i] > p_clo)
            if declenche and dernier_extreme_m1:
                if p_sens < 0:
                    declenche = (not np.isnan(creux_m1[i])) and c[i] < creux_m1[i]
                else:
                    declenche = (not np.isnan(sommet_m1[i])) and c[i] > sommet_m1[i]
            e = i + 1
            if declenche and not (mode_annonces >= 1 and bloque[e]) and not fin_forcee[e]:
                sp = spread_pts[e] * couts * point
                gl = gliss_pts * couts * point
                mini = stops_level_pts * point + sp
                ok = True
                t_elargi = False
                if p_sens < 0:
                    t_entree = o[e] - gl
                    t_stop = p_extreme_vu + tampon * sp
                    if t_stop - t_entree < mini:
                        if elargir:
                            t_stop = t_entree + mini
                            t_elargi = True
                        else:
                            ok = False
                    t_d = t_stop - t_entree
                else:
                    t_entree = o[e] + sp + gl
                    t_stop = p_extreme_vu - tampon * sp
                    if t_entree - t_stop < mini:
                        if elargir:
                            t_stop = t_entree - mini
                            t_elargi = True
                        else:
                            ok = False
                    t_d = t_entree - t_stop
                if ok and t_d > 0.0:
                    t_sens = -1.0 if p_sens < 0 else 1.0
                    t_e = e
                    if rr > 0.0:
                        t_cible = t_entree + t_sens * rr * t_d
                    else:
                        # seules les bougies M15 CLOSES : celle de i n'est close que si i la termine
                        j_ferme = m15_de[i] if fin_m15[i] else m15_de[i] - 1
                        niv = _cible_structure(t_entree, t_d, t_sens, -rr, j_ferme, h15, l15, k_str)
                        t_cible = niv if not np.isnan(niv) else t_entree + t_sens * (-rr) * t_d
                    etat = 2
                else:
                    etat = 0
            elif fin_m15[i]:
                j15 = m15_de[i]
                if (p_sens < 0 and c[i] > p_ext) or (p_sens > 0 and c[i] < p_ext):
                    etat = 0                                  # la M15 a déplacé : invalidé
                elif j15 >= p_j15 + validite:
                    etat = 0                                  # expiré
        # ---------------- nouveau balayage à la clôture M15 ----------------
        if etat != 2 and fin_m15[i]:
            j15 = m15_de[i]
            if sens15[j15] != 0:
                etat = 1
                p_sens = sens15[j15]
                p_clo = rect_cloture[j15]
                p_ext = rect_extreme[j15]
                p_extreme_vu = p_ext
                p_j15 = j15
    return (e_o[:k], s_o[:k], sens_o[:k], r_o[:k], motif_o[:k], entree_o[:k], stop_o[:k], cible_o[:k],
            sortie_o[:k], d_o[:k], j15_o[:k], elargi_o[:k])


@dataclass
class TradesSniper(Trades):
    prix_entree: np.ndarray = None
    stop: np.ndarray = None
    cible: np.ndarray = None
    prix_sortie: np.ndarray = None
    risque_prix: np.ndarray = None
    balayage_m15: np.ndarray = None
    stop_elargi: np.ndarray = None


def simuler(prep: Preparation, r: Reglages, i_debut: int = 0, i_fin: int | None = None,
            balayage=None) -> TradesSniper:
    s = prep.serie
    i_fin = len(s) - 1 if i_fin is None else i_fin
    sens15, rc, rx, _, _ = balayage if balayage is not None else balayages(prep, r)
    bloque, sortir = prep.masques_annonces(r.avant_min, r.apres_min, r.sortie_avant_min) if r.annonces \
        else (np.zeros(len(s), bool), np.zeros(len(s), bool))
    out = _simuler(s.ouverture, s.haut, s.bas, s.cloture, prep.m15_de, prep.fin_m15, prep.spread_pts, s.point,
                   prep.glissement_pts, prep.stops_level_pts, float(r.couts), sens15, rc, rx, int(r.validite),
                   float(r.rr), float(r.tampon_spreads), r.stop_trop_court == "elargir", bool(r.dernier_creux_m1),
                   prep.creux_m1, prep.sommet_m1, bloque, sortir, int(r.annonces), prep.fin_forcee,
                   s.nuits_cumul, s.swap_long_pts * s.point, s.swap_court_pts * s.point,
                   prep.m15.haut, prep.m15.bas, int(r.pivot_structure), int(i_debut), int(i_fin))
    return TradesSniper(*out[:5], *out[5:])


class Sniper:
    """Ce que `banc.walk_forward` et `banc.controle` attendent d'une fabrique : un objet que
    `banc.simuler(serie, objet, i_debut, i_fin)` sait rejouer (voir `simuler_banc`)."""
    _cache: dict = {}

    def __init__(self, serie: Serie, **reglages):
        cle = id(serie)
        if cle not in Sniper._cache:
            Sniper._cache.clear()                      # une série à la fois en mémoire
            Sniper._cache[cle] = preparer(serie)
        self.prep = Sniper._cache[cle]
        self.reglages = Reglages(**reglages)

    def simuler_banc(self, serie: Serie, i_debut: int, i_fin: int) -> Trades:
        return simuler(self.prep, self.reglages, i_debut, i_fin)


def fabrique(serie: Serie, **reglages) -> Sniper:
    return Sniper(serie, **reglages)


# --------------------------------------------------------------------------- #
#  Version Python de référence (contrôles : mêmes setups, mêmes trades)
# --------------------------------------------------------------------------- #

def balayages_reference(prep: Preparation, r: Reglages):
    m = prep.m15
    o, h, l, c = m.ouverture, m.haut, m.bas, m.cloture
    moyenne = prep.ema15(r.ema)
    permis = seances_permises(prep, r)
    n = len(c)
    sens = np.zeros(n, np.int8)
    rc, rx = np.zeros(n), np.zeros(n)
    sommets, creux = [], []                      # [indice, valeur, vivant]
    tendance, str_haut, str_bas = 0, None, None
    k, ks = r.pivot_niveau, r.pivot_structure
    for j in range(n):
        if str_haut is not None and c[j] > str_haut:
            tendance, str_haut = 1, None
        if str_bas is not None and c[j] < str_bas:
            tendance, str_bas = -1, None
        if permis[j] and not np.isnan(moyenne[j]):
            recents_s = [x for x in sommets if x[2] and j - x[0] <= r.age_max]
            recents_c = [x for x in creux if x[2] and j - x[0] <= r.age_max]
            cote_bas = all(j - m_ >= 0 and not np.isnan(moyenne[j - m_]) and c[j - m_] < moyenne[j - m_]
                           for m_ in range(r.anti_zigzag))
            cote_haut = all(j - m_ >= 0 and not np.isnan(moyenne[j - m_]) and c[j - m_] > moyenne[j - m_]
                            for m_ in range(r.anti_zigzag))
            pris = [x for x in recents_s if x[1] < h[j]]
            if c[j] > o[j] and c[j] < moyenne[j] and tendance == -1 and cote_bas and pris:
                niv = max(pris, key=lambda x: (x[1], -x[0]))      # à valeur égale, le plus ancien (comme numba)
                if c[j] < niv[1]:
                    fvg = any(l[q - 2] > h[q] and h[q] <= niv[1] and h[q + 1:j].max(initial=-1e300) < l[q - 2]
                              for q in range(max(niv[0] - 48, 2), niv[0]))
                    if fvg or not r.fvg:
                        sens[j], rc[j], rx[j] = -1, c[j], h[j]
            pris = [x for x in recents_c if x[1] > l[j]]
            if sens[j] == 0 and c[j] < o[j] and c[j] > moyenne[j] and tendance == 1 and cote_haut and pris:
                niv = min(pris, key=lambda x: (x[1], x[0]))       # à valeur égale, le plus ancien (comme numba)
                if c[j] > niv[1]:
                    fvg = any(h[q - 2] < l[q] and l[q] >= niv[1] and l[q + 1:j].min(initial=1e300) > h[q - 2]
                              for q in range(max(niv[0] - 48, 2), niv[0]))
                    if fvg or not r.fvg:
                        sens[j], rc[j], rx[j] = 1, c[j], l[j]
        for x in sommets:
            if x[2] and h[j] > x[1]:
                x[2] = False
        for x in creux:
            if x[2] and l[j] < x[1]:
                x[2] = False
        p = j - k
        if p - k >= 0:
            if all(h[p] > h[p - m_] and h[p] >= h[p + m_] for m_ in range(1, k + 1)):
                sommets.append([p, h[p], True])
            if all(l[p] < l[p - m_] and l[p] <= l[p + m_] for m_ in range(1, k + 1)):
                creux.append([p, l[p], True])
        p = j - ks
        if p - ks >= 0:
            if all(h[p] > h[p - m_] and h[p] >= h[p + m_] for m_ in range(1, ks + 1)):
                str_haut = h[p]
            if all(l[p] < l[p - m_] and l[p] <= l[p + m_] for m_ in range(1, ks + 1)):
                str_bas = l[p]
    return sens, rc, rx


def regles_changees(r: Reglages, **modifs) -> Reglages:
    return replace(r, **modifs)
