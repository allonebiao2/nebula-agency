# -*- coding: utf-8 -*-
"""
Le banc de recherche : trier beaucoup de stratégies vite, sans se mentir.

Le moteur officiel (`backtest/moteur.py`) coûte environ 60 µs par barre : une grille
de réglages en M5 y prendrait des heures. Le banc sert à TRIER. Les finalistes
repassent ensuite par le moteur, avec tous les verrous du cahier : ce sont ses
chiffres qui font foi.

Ce que le banc ne se permet pas, et que les backtests publics se permettent :
  · entrer au prix de clôture de la barre du signal (on entre à l'OUVERTURE suivante) ;
  · ignorer le spread (on paie le spread MÉDIAN mesuré sur ticks, pas le champ
    `spread` d'une bougie, qui n'est pas le spread payé) et le glissement ;
  · décider que l'objectif a été touché avant le stop dans une même barre (le stop
    d'abord, toujours) ;
  · sortir sur un signal qui réaliserait moins de 2 R (Mongazi, 2026-09-17 : R:R
    d'au moins 1:2). On ne sort QUE par le stop, l'objectif, ou le temps.
  · oublier le portage d'une nuit (le swap du NAS100 pèse lourd).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

import numpy as np
from numba import njit

from ..noyau.donnees_mt5 import lire_cache, specs_et_couts

STOP, OBJECTIF, TEMPS, GAP, SEANCE, FIN, POINT_MORT = 0, 1, 2, 3, 4, 5, 6
MOTIFS = ("stop", "objectif", "temporel", "stop (gap)", "fin de séance", "fin de données", "point mort",
          "avant annonce")
MINUTES_TF = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H2": 120, "H4": 240, "D1": 1440}


@dataclass
class Serie:
    """Une série de bougies et ce qu'elle coûte à trader chez CE courtier."""
    base: str
    tf: str
    temps: np.ndarray            # datetime64[s], heure serveur
    ouverture: np.ndarray
    haut: np.ndarray
    bas: np.ndarray
    cloture: np.ndarray
    point: float
    cout_sens_pts: float         # demi-spread + glissement, payé à l'entrée ET à la sortie
    swap_long_pts: float         # par lot et par nuit, en points
    swap_court_pts: float
    nuits_cumul: np.ndarray      # nuits de portage facturées cumulées (triple le mercredi)
    # Distance de stop minimale, en PRIX : le « stops level » du courtier, et jamais moins de
    # deux allers-retours de coûts. ⛔ 2026-09-17 : sans ce plancher, un stop posé plus près que
    # le spread donnait un risque quasi nul, et un trade valait +8 879 358 R.
    stop_min_prix: float = 0.0
    # Coût d'UN sens, en PRIX, barre par barre. En scalping le coût décide de tout : un stop de
    # 2 pips paie son spread en entier, et le spread de 17:01 New York vaut 30 fois celui de midi.
    # None = le coût scalaire `cout_sens_pts` pour toutes les barres (ancien comportement).
    cout_bar_prix: np.ndarray | None = None
    source: str = "mt5"
    volume: np.ndarray | None = None       # volume de ticks : un flux d'ordres pauvre, mais un flux

    def __len__(self) -> int:
        return len(self.cloture)

    @property
    def minutes(self) -> int:
        return MINUTES_TF[self.tf]

    def couts_prix(self) -> np.ndarray:
        if self.cout_bar_prix is None:
            return np.full(len(self.cloture), self.cout_sens_pts * self.point, dtype=np.float64)
        return self.cout_bar_prix.astype(np.float64, copy=False)

    def tranche(self, debut: str | None = None, fin: str | None = None) -> "Serie":
        """Les barres de [debut, fin[ (dates ISO), tout le reste recalculé. Sert au partage
        découverte / scellé : une tranche ne doit pas garder les cumuls de la série entière."""
        m = np.ones(len(self.cloture), dtype=bool)
        if debut:
            m &= self.temps >= np.datetime64(debut)
        if fin:
            m &= self.temps < np.datetime64(fin)
        nuits = self.nuits_cumul[m]
        return Serie(self.base, self.tf, self.temps[m], self.ouverture[m], self.haut[m], self.bas[m],
                     self.cloture[m], self.point, self.cout_sens_pts, self.swap_long_pts,
                     self.swap_court_pts, nuits - (nuits[0] if len(nuits) else 0.0), self.stop_min_prix,
                     None if self.cout_bar_prix is None else self.cout_bar_prix[m], self.source,
                     None if self.volume is None else self.volume[m])


def charger(base: str, tf: str, *, multiplicateur_couts: float = 1.0, source: str = "mt5",
            cout: str = "deriv") -> Serie:
    """`source` : 'mt5' (Deriv) ou 'duka' (Dukascopy, l'historique que Deriv n'a pas).
    `cout` : 'deriv' = le profil du courtier chez qui on tradera, minute par minute (défaut) ·
    'epoque' = le spread réellement observé à la date de la barre (Dukascopy seulement) ·
    'max' = le plus cher des deux, pour savoir si un avantage survit au pire des deux mondes."""
    ecart_epoque = None
    if source == "duka":
        from . import dukascopy
        lu = dukascopy.lire_cache(base, tf)
        if lu is None:
            raise FileNotFoundError(f"{base} {tf} Dukascopy absent : "
                                    f"python -m trading.recherche.dukascopy --base {base}")
        tab, _meta = lu
        from ..strategies.base import Barres
        b = Barres(temps=tab["temps"], ouverture=tab["ouverture"], haut=tab["haut"], bas=tab["bas"],
                   cloture=tab["cloture"], volume=tab.get("volume"), spread=None,
                   symbole=base.upper(), timeframe=tf)
        ecart_epoque = tab.get("spread_points")
        if ecart_epoque is None and "ecart_prix" in tab:
            ecart_epoque = tab["ecart_prix"]
    else:
        b = lire_cache(base, tf)
    if b is None:
        raise FileNotFoundError(f"{base} {tf} absent : python -m trading.noyau.donnees_mt5 {tf} --base {base}")
    specs, couts = specs_et_couts(base)
    cout_median = (couts.spread_points / 2 + couts.slippage_points) * multiplicateur_couts
    cout_bar = _couts_par_barre(base, b.temps, specs.point, couts, multiplicateur_couts,
                                ecart_epoque, cout, b.cloture)
    jours = b.temps.astype("datetime64[D]")
    nouveau = np.concatenate(([False], jours[1:] != jours[:-1]))
    # MT5 facture trois nuits au roulement du mercredi soir : la première barre du jeudi.
    jeudi = (jours.astype("int64") + 3) % 7 == 3          # 1970-01-01 était un jeudi
    poids = np.where(nouveau, np.where(jeudi, 3.0, 1.0), 0.0)
    return Serie(base=base.upper(), tf=tf, temps=b.temps, ouverture=b.ouverture, haut=b.haut,
                 bas=b.bas, cloture=b.cloture, point=specs.point, cout_sens_pts=cout_median,
                 swap_long_pts=couts.swap_long_points, swap_court_pts=couts.swap_short_points,
                 nuits_cumul=np.cumsum(poids),
                 stop_min_prix=max(float(specs.stops_level_points or 0), 4 * cout_median) * specs.point,
                 cout_bar_prix=cout_bar, source=source,
                 volume=None if b.volume is None or not len(b.volume) else np.asarray(b.volume, float))


def _couts_par_barre(base: str, temps: np.ndarray, point: float, couts, multiplicateur: float,
                     ecart_epoque: np.ndarray | None, mode: str,
                     prix: np.ndarray | None = None) -> np.ndarray | None:
    """Coût d'un sens, en PRIX, pour chaque barre : demi-spread de la minute + glissement.

    ⚠️ Mode `relatif` : le spread d'un indice est coté en points, mais **un point ne vaut pas la même
    chose selon le niveau de l'indice**. Les 70 points de Deriv sur un NAS100 à 24 000 valent quatre
    fois plus sur le NAS100 de 2015, qui était à 5 000. Appliquer le spread d'aujourd'hui à un passé
    lointain condamne toute stratégie, et l'inverse la sauve : le mode `relatif` met le coût en
    proportion du prix, calibré sur le prix de référence du courtier.
    """
    gliss = couts.slippage_points * point
    deriv = None
    try:
        from .spread_horaire import spread_par_barre
        deriv = spread_par_barre(base, temps) * point / 2.0 + gliss
    except Exception:                                  # profil pas encore mesuré : coût scalaire
        deriv = None
    epoque = None
    if ecart_epoque is not None:
        e = np.asarray(ecart_epoque, float) / 2.0 + gliss
        # Une minute sans cotation ask (rare) n'a pas de spread d'époque : on lui donne le coût Deriv,
        # ou la médiane des minutes voisines, jamais zéro.
        manque = ~np.isfinite(e)
        if manque.any():
            secours = deriv if deriv is not None else np.full(len(e), np.nanmedian(e))
            e = np.where(manque, secours, e)
        epoque = e
    if mode == "epoque" and epoque is not None:
        choisi = epoque
    elif mode == "max" and epoque is not None:
        choisi = epoque if deriv is None else np.maximum(deriv, epoque)
    elif mode == "relatif" and deriv is not None and prix is not None:
        from ..noyau.donnees_mt5 import charger_profil
        reference = float((charger_profil(base) or {}).get("prix_reference") or 0.0)
        choisi = deriv * (np.asarray(prix, float) / reference) if reference > 0 else deriv
    else:
        choisi = deriv
    return None if choisi is None else (choisi * multiplicateur).astype(np.float64)


@dataclass
class Signaux:
    """Ce qu'une stratégie propose à la clôture de chaque barre i (entrée à i+1)."""
    sens: np.ndarray                     # +1 achat, -1 vente, 0 rien
    stop_dist: np.ndarray                # distance du stop en PRIX, mesurée au signal
    rr: float = 2.0                      # objectif = rr × stop (jamais sous 2 : cahier)
    max_barres: int = 36                 # stop temporel, en barres (règle maison : 36)
    fin_seance: np.ndarray | None = None  # True = sortir à la clôture de cette barre
    be_R: float = 0.0                    # 0 = jamais ; sinon stop ramené à l'entrée (coûts couverts) après be_R de gain


@njit(cache=True)
def _simuler(ouv, haut, bas, clo, sens, stop_dist, rr, max_barres, fin_seance, a_fin_seance,
             couts, swap_l_prix, swap_c_prix, nuits, i_debut, i_fin, stop_min, be_R):
    n = len(clo)
    cap = i_fin - i_debut + 1
    e_i = np.empty(cap, np.int64)
    s_i = np.empty(cap, np.int64)
    sens_o = np.empty(cap, np.int8)
    r_o = np.empty(cap, np.float64)
    motif_o = np.empty(cap, np.int8)
    k = 0
    libre_des = i_debut
    fin = min(i_fin, n - 2)
    for i in range(i_debut, fin + 1):
        if i < libre_des or sens[i] == 0:
            continue
        d = stop_dist[i]
        if not (d >= stop_min and d > 0.0):
            continue
        e = i + 1
        s = 1.0 if sens[i] > 0 else -1.0
        cout_prix = couts[e]                    # le spread de LA minute d'entrée
        entree = ouv[e] + s * cout_prix
        stop = entree - s * d
        cible = entree + s * rr * d
        sortie = -1.0
        motif = FIN
        deplace = False
        j = e
        derniere = min(n - 1, e + max_barres)
        while j <= derniere:
            if j > e:
                if (s > 0 and ouv[j] <= stop) or (s < 0 and ouv[j] >= stop):
                    sortie, motif = ouv[j], (POINT_MORT if deplace else GAP)
                    break
            touche_stop = bas[j] <= stop if s > 0 else haut[j] >= stop
            if touche_stop:
                sortie, motif = stop, (POINT_MORT if deplace else STOP)
                break
            touche_cible = haut[j] >= cible if s > 0 else bas[j] <= cible
            if touche_cible:
                sortie, motif = cible, OBJECTIF
                break
            # Point mort : actif à partir de la barre SUIVANTE (l'ordre dans la barre est inconnu).
            if be_R > 0.0 and not deplace and ((s > 0 and haut[j] >= entree + be_R * d)
                                               or (s < 0 and bas[j] <= entree - be_R * d)):
                stop = entree + s * couts[j]
                deplace = True
            if a_fin_seance and fin_seance[j]:
                sortie, motif = clo[j], SEANCE
                break
            if j - e >= max_barres:
                sortie, motif = clo[j], TEMPS
                break
            j += 1
        if sortie < 0.0:
            j = n - 1
            sortie, motif = clo[j], FIN
        net = s * ((sortie - s * couts[j]) - entree)
        portage = (nuits[j] - nuits[e]) * (swap_l_prix if s > 0 else swap_c_prix)
        e_i[k] = e
        s_i[k] = j
        sens_o[k] = 1 if s > 0 else -1
        r_o[k] = (net + portage) / d
        motif_o[k] = motif
        k += 1
        libre_des = j
    return e_i[:k], s_i[:k], sens_o[:k], r_o[:k], motif_o[:k]


@dataclass
class Trades:
    entree: np.ndarray
    sortie: np.ndarray
    sens: np.ndarray
    R: np.ndarray
    motif: np.ndarray

    def __len__(self) -> int:
        return len(self.R)

    def selection(self, masque: np.ndarray) -> "Trades":
        return Trades(self.entree[masque], self.sortie[masque], self.sens[masque],
                      self.R[masque], self.motif[masque])

    @staticmethod
    def concat(liste: list["Trades"]) -> "Trades":
        if not liste:
            vide = np.array([], dtype=np.int64)
            return Trades(vide, vide, np.array([], np.int8), np.array([], float), np.array([], np.int8))
        return Trades(*(np.concatenate([getattr(t, c) for t in liste])
                        for c in ("entree", "sortie", "sens", "R", "motif")))


def simuler(serie: Serie, sig: Signaux, i_debut: int = 0, i_fin: int | None = None) -> Trades:
    """Les trades dont le SIGNAL tombe dans [i_debut, i_fin]."""
    i_fin = len(serie) - 1 if i_fin is None else i_fin
    if sig.rr < 2.0 - 1e-9:
        raise ValueError(f"rr = {sig.rr} : le cahier exige un objectif d'au moins 2 R")
    fs = sig.fin_seance if sig.fin_seance is not None else np.zeros(len(serie), dtype=np.bool_)
    sortie = _simuler(serie.ouverture, serie.haut, serie.bas, serie.cloture,
                      sig.sens.astype(np.int8), sig.stop_dist.astype(np.float64), float(sig.rr),
                      int(sig.max_barres), fs.astype(np.bool_), sig.fin_seance is not None,
                      serie.couts_prix(), serie.swap_long_pts * serie.point,
                      serie.swap_court_pts * serie.point, serie.nuits_cumul, int(i_debut), int(i_fin),
                      float(serie.stop_min_prix), float(sig.be_R))
    return Trades(*sortie)


# --------------------------------------------------------------------------- #
#  Mesures
# --------------------------------------------------------------------------- #

def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    marge = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - marge, centre + marge


def p_valeur_unilaterale(R: np.ndarray) -> float:
    """P(espérance <= 0) sous l'hypothèse nulle, test t approché par la loi normale."""
    n = len(R)
    if n < 2:
        return 1.0
    ecart = float(np.std(R, ddof=1))
    if ecart == 0:
        return 0.0 if R.mean() > 0 else 1.0
    t = float(R.mean()) / (ecart / math.sqrt(n))
    return 0.5 * math.erfc(t / math.sqrt(2))


def point_mort_objectif(R: np.ndarray, objectif: np.ndarray, rr: float = 2.0) -> float:
    """Le taux d'objectifs atteints qui rend l'espérance nulle, coûts compris.

    Le point mort théorique à 1:2 est 33,3 %. Il ne vaut que si une perte coûte exactement 1 R et un
    gain rapporte exactement 2 R. En vrai, le stop est franchi par un gap, une sortie par le temps
    rend −0,4 R, et le coût s'ajoute : le vrai point mort se lit dans les trades, pas dans la théorie.
    """
    n = len(R)
    if n == 0:
        return rr / (rr + 1.0)
    gain = float(R[objectif].mean()) if objectif.any() else rr
    perte = float(R[~objectif].mean()) if (~objectif).any() else -1.0
    if gain - perte <= 0:
        return 1.0
    return float(min(1.0, max(0.0, -perte / (gain - perte))))


def p_binomial(k: int, n: int, p0: float) -> float:
    """P(au moins k succès sur n) sous H0 : la proportion vaut p0. C'est le test du CRITÈRE de
    Mongazi (« plus de la moitié des trades atteignent 2 R »), pas celui de l'espérance."""
    if n == 0:
        return 1.0
    p0 = min(max(p0, 1e-9), 1 - 1e-9)
    try:
        from scipy.stats import binom
        return float(binom.sf(k - 1, n, p0))
    except Exception:                                   # pragma: no cover
        z = (k / n - p0) / math.sqrt(p0 * (1 - p0) / n)
        return 0.5 * math.erfc(z / math.sqrt(2))


def mesurer(serie: Serie, t: Trades, *, risque_pct: float = 1.0, series: bool = True) -> dict:
    n = len(t)
    if n == 0:
        return {"trades": 0}
    R = t.R
    gagnants = int((R > 0).sum())
    pos, neg = R[R > 0].sum(), -R[R <= 0].sum()
    equite = np.cumprod(1.0 + np.maximum(R * risque_pct / 100.0, -0.999))
    sommets = np.maximum.accumulate(np.concatenate(([1.0], equite)))[1:]
    duree_jours = max(1.0, (serie.temps[t.sortie[-1]] - serie.temps[t.entree[0]]).astype("timedelta64[s]")
                      .astype(float) / 86400)
    # LE chiffre de Mongazi : un trade « gagnant » peut être une sortie par le temps à +0,1 R.
    # Seul l'objectif dit « j'ai pris mes 2 R ».
    atteint = t.motif == OBJECTIF
    k_obj = int(atteint.sum())
    p0 = point_mort_objectif(R, atteint)
    mesures_series = {}
    if series:
        from .compte import series_perdantes
        mesures_series = series_perdantes(R, fenetre=100) if n <= 20_000 else \
            series_perdantes(R[-20_000:], fenetre=100)
    return {
        "trades": n,
        "taux_reussite": gagnants / n,
        "taux_reussite_ic95": _wilson(gagnants, n),
        "taux_objectif": k_obj / n,
        "taux_objectif_ic95": _wilson(k_obj, n),
        "point_mort_objectif": round(p0, 4),
        "p_objectif": p_binomial(k_obj, n, p0),
        "series_perdantes": mesures_series,
        "esperance_R": float(R.mean()),
        "profit_factor": float(pos / neg) if neg > 0 else float("inf"),
        "gain_moyen_R": float(R[R > 0].mean()) if gagnants else 0.0,
        "perte_moyenne_R": float(R[R <= 0].mean()) if gagnants < n else 0.0,
        "p_valeur": p_valeur_unilaterale(R),
        "drawdown_max_pct": float((1.0 - equite / sommets).max() * 100),
        "resultat_pct": float((equite[-1] - 1.0) * 100),
        "R_par_mois": float(R.sum() / (duree_jours / 30.44)),
        "trades_par_mois": float(n / (duree_jours / 30.44)),
        "motifs": {MOTIFS[m]: int((t.motif == m).sum()) for m in range(len(MOTIFS)) if (t.motif == m).any()},
        "debut": str(serie.temps[t.entree[0]])[:16], "fin": str(serie.temps[t.sortie[-1]])[:16],
    }


# --------------------------------------------------------------------------- #
#  Walk-forward et période de contrôle
# --------------------------------------------------------------------------- #

@dataclass
class Candidate:
    nom: str
    libelle: str
    source: str
    fabrique: object                     # (serie, **params) -> Signaux
    grille: dict[str, list]
    unites: tuple[str, ...]
    instruments: tuple[str, ...] = ("EURUSD", "NAS100")
    note: str = ""

    def combinaisons(self) -> list[dict]:
        cles = list(self.grille)
        return [dict(zip(cles, v)) for v in itertools.product(*(self.grille[c] for c in cles))]


@dataclass
class Resultat:
    candidate: str
    base: str
    tf: str
    combinaisons: int
    fenetres: list = field(default_factory=list)
    hors_echantillon: dict = field(default_factory=dict)
    trades_R: list = field(default_factory=list)
    derniers_reglages: dict = field(default_factory=dict)


def _score(R: np.ndarray, min_trades: int) -> float:
    """Critère de choix en apprentissage : l'espérance pondérée par la taille (t de Student)."""
    if len(R) < min_trades:
        return -math.inf
    ecart = float(np.std(R, ddof=1)) or 1e-9
    return float(R.mean()) / ecart * math.sqrt(len(R))


def bornes(serie: Serie, part_developpement: float = 0.8, n_tests: int = 6, ratio: int = 4):
    """Indices : développement = les 80 % anciens, contrôle = les 20 % récents.
    Fenêtre de test T = développement / (ratio + n_tests), apprentissage = ratio × T."""
    n = len(serie)
    fin_dev = int(n * part_developpement)
    T = fin_dev // (ratio + n_tests)
    return fin_dev, T


def walk_forward(serie: Serie, cand: Candidate, *, min_trades: int = 20, n_tests: int = 6,
                 ratio: int = 4, part_developpement: float = 0.8) -> Resultat:
    fin_dev, T = bornes(serie, part_developpement, n_tests, ratio)
    combos = cand.combinaisons()
    # Un signal M1 de 7 ans pèse ~25 Mo : on simule puis on jette, on ne garde que les trades.
    tous = [simuler(serie, cand.fabrique(serie, **c), 0, fin_dev - 1) for c in combos]
    res = Resultat(cand.nom, serie.base, serie.tf, len(combos))
    hors = []
    for w in range(n_tests):
        a0, t0 = w * T, (w + ratio) * T
        t1 = t0 + T if w < n_tests - 1 else fin_dev
        meilleur, score = None, -math.inf
        for c, tr in zip(combos, tous):
            m = (tr.entree - 1 >= a0) & (tr.entree - 1 < t0) & (tr.sortie < t0)
            sc = _score(tr.R[m], min_trades)
            if sc > score:
                meilleur, score = c, sc
        if meilleur is None:
            res.fenetres.append({"debut_test": str(serie.temps[t0])[:10], "reglages": None, "trades": 0})
            continue
        tr = tous[combos.index(meilleur)]
        m = (tr.entree - 1 >= t0) & (tr.entree - 1 < t1)
        sel = tr.selection(m)
        hors.append(sel)
        res.fenetres.append({"debut_test": str(serie.temps[t0])[:10], "fin_test": str(serie.temps[t1 - 1])[:10],
                             "reglages": meilleur, "score_apprentissage": round(score, 3),
                             "trades": len(sel), "esperance_R": float(sel.R.mean()) if len(sel) else None})
        res.derniers_reglages = meilleur
    t = Trades.concat(hors)
    res.hors_echantillon = mesurer(serie, t)
    res.trades_R = [round(float(x), 4) for x in t.R]
    return res


def controle(serie: Serie, cand: Candidate, *, min_trades: int = 20, ratio: int = 4, n_tests: int = 6,
             part_developpement: float = 0.8) -> dict:
    """LA période de contrôle : réglages choisis sur la dernière fenêtre d'apprentissage du
    développement, appliqués aux 20 % les plus récents, jamais vus. À n'ouvrir qu'une fois."""
    fin_dev, T = bornes(serie, part_developpement, n_tests, ratio)
    debut_app = fin_dev - ratio * T
    meilleur, score = None, -math.inf
    for c in cand.combinaisons():
        tr = simuler(serie, cand.fabrique(serie, **c), debut_app, fin_dev - 1)
        m = tr.sortie < fin_dev
        sc = _score(tr.R[m], min_trades)
        if sc > score:
            meilleur, score = c, sc
    if meilleur is None:
        return {"reglages": None, "trades": 0}
    tr = simuler(serie, cand.fabrique(serie, **meilleur), fin_dev, len(serie) - 2)
    return {"reglages": meilleur, **mesurer(serie, tr), "trades_R": [round(float(x), 4) for x in tr.R]}


def holm(p_valeurs: list[float], alpha: float = 0.05) -> list[bool]:
    """Holm-Bonferroni : quelles hypothèses « espérance > 0 » survivent à la multiplicité."""
    ordre = sorted(range(len(p_valeurs)), key=lambda i: p_valeurs[i])
    m, rejet = len(p_valeurs), [False] * len(p_valeurs)
    for rang, i in enumerate(ordre):
        if p_valeurs[i] <= alpha / (m - rang):
            rejet[i] = True
        else:
            break
    return rejet


# --------------------------------------------------------------------------- #
#  Ordres LIMITES (entrée sur retour de prix : méthode « discount » de Hugo FX)
# --------------------------------------------------------------------------- #

@dataclass
class Ordres:
    """Des ordres limites posés à l'indice `pose` (la barre dont la CLÔTURE les autorise)."""
    pose: np.ndarray          # int64 : actifs à partir de la barre pose + 1
    sens: np.ndarray          # int8
    limite: np.ndarray        # prix d'entrée voulu
    stop: np.ndarray
    cible: np.ndarray
    expire: np.ndarray        # int64 : dernière barre où l'ordre peut être rempli
    max_barres: int = 240     # après remplissage
    be_R: float = 0.0          # point mort après be_R de gain (0 = jamais)
    # Règle du scalping (2026-09-17) : la journée se ferme. Un ordre non servi est annulé, une
    # position ouverte est soldée à la clôture de la barre. Sans ça, un ordre limite passe la nuit.
    fin_seance: np.ndarray | None = None
    # ⛔ LE PIÈGE DES ORDRES LIMITES. Nos bougies sont des prix VENDEUR (bid). Un achat s'exécute au
    # prix ACHETEUR (ask = bid + spread) : l'ordre n'est donc servi que si le bid descend un spread
    # PLUS BAS que la limite. « Le bas de la bougie a touché ma limite, donc je suis servi » fait
    # entrer sur les creux les plus courts — exactement ceux qui rebondissent — et fabrique un
    # avantage qui n'existe pas. `k_remplissage` exige que le prix traverse de k × coût :
    # 0 = touche (optimiste), 2 = un spread complet (réaliste), 3 = prudent.
    k_remplissage: float = 0.0
    # Amélioration de prix : quand la barre OUVRE au-delà de la limite, un ordre au repos est servi
    # à l'ouverture, donc mieux que sa limite. C'est vrai en marché réel, mais ça fait aussi entrer
    # un backtest sur des ouvertures bruitées : `ameliorer=False` sert à mesurer ce que ça rapporte.
    ameliorer: bool = True


@njit(cache=True)
def _simuler_ordres(ouv, haut, bas, clo, pose, sens, limite, stop, cible, expire, max_barres,
                    couts, swap_l_prix, swap_c_prix, nuits, stop_min, be_R, fin_seance, a_fin_seance,
                    k_remplissage, ameliorer):
    n = len(clo)
    m = len(pose)
    e_i = np.empty(m, np.int64)
    s_i = np.empty(m, np.int64)
    sens_o = np.empty(m, np.int8)
    r_o = np.empty(m, np.float64)
    motif_o = np.empty(m, np.int8)
    k = 0
    libre_des = 0
    for o in range(m):
        debut = pose[o] + 1
        if debut < libre_des or debut >= n:
            continue
        s = 1.0 if sens[o] > 0 else -1.0
        lim, st, ci = limite[o], stop[o], cible[o]
        d = s * (lim - st)                       # le risque PRÉVU : c'est lui qui définit 1 R
        if not (d >= stop_min and d > 0.0) or not (s * (ci - lim) > 0.0):
            continue
        rempli = -1
        prix = 0.0
        j = debut
        while j <= min(expire[o], n - 1):
            # La cible atteinte avant le remplissage annule l'ordre (hypothèse pessimiste :
            # si la barre touche les deux, on suppose qu'on n'a pas été servi).
            if (s > 0 and haut[j] >= ci) or (s < 0 and bas[j] <= ci):
                break
            if a_fin_seance and fin_seance[j]:          # la journée se ferme : l'ordre est annulé
                break
            seuil = lim - s * k_remplissage * couts[j]   # il faut TRAVERSER, pas effleurer
            if (s > 0 and bas[j] <= seuil) or (s < 0 and haut[j] >= seuil):
                rempli = j
                if ameliorer:
                    prix = min(lim, ouv[j]) if s > 0 else max(lim, ouv[j])
                else:
                    prix = lim
                break
            j += 1
        if rempli < 0:
            continue
        cout_prix = couts[rempli]
        entree = prix + s * cout_prix
        sortie = -1.0
        motif = FIN
        deplace = False
        j = rempli
        derniere = min(n - 1, rempli + max_barres)
        while j <= derniere:
            if j > rempli and ((s > 0 and ouv[j] <= st) or (s < 0 and ouv[j] >= st)):
                sortie, motif = ouv[j], (POINT_MORT if deplace else GAP)
                break
            if (s > 0 and bas[j] <= st) or (s < 0 and haut[j] >= st):
                sortie, motif = st, (POINT_MORT if deplace else STOP)
                break
            if j > rempli and ((s > 0 and haut[j] >= ci) or (s < 0 and bas[j] <= ci)):
                sortie, motif = ci, OBJECTIF
                break
            if be_R > 0.0 and not deplace and j > rempli and ((s > 0 and haut[j] >= entree + be_R * d)
                                                               or (s < 0 and bas[j] <= entree - be_R * d)):
                st = entree + s * couts[j]
                deplace = True
            if a_fin_seance and fin_seance[j]:
                sortie, motif = clo[j], SEANCE
                break
            if j - rempli >= max_barres:
                sortie, motif = clo[j], TEMPS
                break
            j += 1
        if sortie < 0.0:
            j = n - 1
            sortie, motif = clo[j], FIN
        net = s * ((sortie - s * couts[j]) - entree)
        portage = (nuits[j] - nuits[rempli]) * (swap_l_prix if s > 0 else swap_c_prix)
        e_i[k] = rempli
        s_i[k] = j
        sens_o[k] = 1 if s > 0 else -1
        r_o[k] = (net + portage) / d
        motif_o[k] = motif
        k += 1
        libre_des = j
    return e_i[:k], s_i[:k], sens_o[:k], r_o[:k], motif_o[:k]


def simuler_ordres(serie: Serie, o: Ordres, i_debut: int = 0, i_fin: int | None = None) -> Trades:
    i_fin = len(serie) - 1 if i_fin is None else i_fin
    # Cahier (Mongazi, 2026-09-17) : l'objectif prévu vaut au moins 2 fois le risque prévu.
    with np.errstate(divide="ignore", invalid="ignore"):
        rr = (o.sens * (o.cible - o.limite)) / (o.sens * (o.limite - o.stop))
    garde = (o.pose >= i_debut) & (o.pose <= i_fin) & (rr >= 2.0 - 1e-9)
    ordre = np.argsort(o.pose[garde], kind="stable")
    sortie = _simuler_ordres(serie.ouverture, serie.haut, serie.bas, serie.cloture,
                             o.pose[garde][ordre].astype(np.int64), o.sens[garde][ordre].astype(np.int8),
                             o.limite[garde][ordre].astype(float), o.stop[garde][ordre].astype(float),
                             o.cible[garde][ordre].astype(float), o.expire[garde][ordre].astype(np.int64),
                             int(o.max_barres), serie.couts_prix(),
                             serie.swap_long_pts * serie.point, serie.swap_court_pts * serie.point,
                             serie.nuits_cumul, float(serie.stop_min_prix), float(o.be_R),
                             (o.fin_seance if o.fin_seance is not None
                              else np.zeros(len(serie), dtype=np.bool_)).astype(np.bool_),
                             o.fin_seance is not None, float(o.k_remplissage), bool(o.ameliorer))
    return Trades(*sortie)


_simuler_signaux = simuler


def simuler(serie: Serie, sig, i_debut: int = 0, i_fin: int | None = None) -> Trades:  # noqa: F811
    """Signaux (entrée au marché) ou Ordres (entrée limite), même sortie, mêmes coûts.
    Un objet qui sait se rejouer lui-même (`simuler_banc`, ex. `sniper.Sniper`, bid/ask minute par
    minute) passe par sa propre simulation : walk-forward, contrôle et registre restent les mêmes."""
    if hasattr(sig, "simuler_banc"):
        return sig.simuler_banc(serie, i_debut, len(serie) - 1 if i_fin is None else i_fin)
    if isinstance(sig, Ordres):
        return simuler_ordres(serie, sig, i_debut, i_fin)
    return _simuler_signaux(serie, sig, i_debut, i_fin)


# --------------------------------------------------------------------------- #
#  Plusieurs unités de temps tirées d'UNE série (alignement garanti)
# --------------------------------------------------------------------------- #

@dataclass
class Agregat:
    tf: str
    debut: np.ndarray          # datetime64[s] ouverture de la barre agrégée
    ouverture: np.ndarray
    haut: np.ndarray
    bas: np.ndarray
    cloture: np.ndarray
    fermee_a: np.ndarray       # pour chaque barre de BASE : indice de la dernière barre agrégée CLOSE


def agreger(serie: Serie, tf: str) -> Agregat:
    """Barres `tf` reconstruites depuis la série de base, et pour chaque barre de base
    l'indice de la dernière barre `tf` déjà CLOSE à la clôture de la barre de base
    (jamais celle en cours : c'est là que se cache le regard vers le futur)."""
    import pandas as pd
    minutes = MINUTES_TF[tf]
    df = pd.DataFrame({"o": serie.ouverture, "h": serie.haut, "b": serie.bas, "c": serie.cloture},
                      index=pd.DatetimeIndex(serie.temps))
    r = df.resample(f"{minutes}min", label="left", closed="left").agg(
        {"o": "first", "h": "max", "b": "min", "c": "last"}).dropna()
    debut = r.index.to_numpy().astype("datetime64[s]")
    fin_agregat = debut + np.timedelta64(minutes * 60, "s")
    fin_base = serie.temps + np.timedelta64(serie.minutes * 60, "s")
    fermee_a = np.searchsorted(fin_agregat, fin_base, side="right") - 1
    return Agregat(tf, debut, r["o"].to_numpy(), r["h"].to_numpy(), r["b"].to_numpy(), r["c"].to_numpy(),
                   fermee_a.astype(np.int64))
