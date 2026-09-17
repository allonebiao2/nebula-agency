# -*- coding: utf-8 -*-
"""
Les figures chartistes, rendues mécaniques : épaule-tête-épaule (ETE), ETE inversé, biseau ascendant,
biseau descendant. Avec ou sans divergence RSI (14) et confirmation EMA 50.

Demande de Mongazi (2026-09-17) : « et si on ajoute le RSI et la moyenne mobile 50 EMA ? backtestons ».
Référence des statistiques publiques : Bulkowski (thepatternsite.com), sur des actions, sortie au
meilleur prix, sans stop ni coûts. Ici : stop, objectif 2 R, coûts Deriv, entrée à l'ouverture suivante.

TOUT EST FIXÉ AVANT LE PREMIER RÉSULTAT (écrit ici pour qu'on le conteste, jamais retouché après) :

Pivots
  · Sommet/creux = extrême de 7 bougies (3 de chaque côté), confirmé 3 bougies après.
  · Séquence ALTERNÉE : deux sommets de suite, on garde le plus haut ; deux creux, le plus bas.

Épaule-tête-épaule (sommet ; l'inversé est le miroir)
  · Pivots L0 (creux) · P1 épaule gauche · T1 creux · P2 tête · T2 creux ; l'épaule droite RS est le plus
    haut atteint depuis T2 (pas besoin d'attendre sa confirmation : la cassure arrive souvent avant).
  · Tête au-dessus des deux épaules. Hauteur H = tête - ligne de cou (droite T1-T2) >= 2 ATR(14).
  · Chaque épaule dépasse la ligne de cou d'au moins 0,3 H ; écart de hauteur entre épaules <= 0,5 H.
  · Ligne de cou pas trop penchée : |T2 - T1| <= 0,5 H. Tendance préalable : L0 sous T1 et T2.
  · Symétrie de temps : la plus longue moitié <= 2,5 fois la plus courte. Largeur 12 à 150 bougies.
  · Signal : PREMIÈRE clôture sous la ligne de cou prolongée, aucune clôture dessous avant, dans une
    largeur de figure après l'épaule droite, sans jamais repasser au-dessus de la tête.
  · Stop « proche » = au-dessus de l'épaule droite ; « loin » = au-dessus de la tête ; + 0,1 ATR.
  · Divergence RSI : RSI(14) à la tête < RSI(14) à l'épaule gauche. EMA 50 : clôture de cassure sous l'EMA 50.

Biseau ascendant (baissier ; le descendant est le miroir)
  · Les 5 derniers pivots alternés (3 sommets + 2 creux, ou 2 + 3) : sommets de plus en plus hauts, creux
    de plus en plus hauts. Ligne haute = premier et dernier sommet ; ligne basse = premier et dernier creux.
  · Les deux lignes montent ET convergent : pente basse > pente haute > 0 ; largeur au dernier pivot
    <= 0,7 fois la largeur au premier ; largeur de départ >= 2 ATR(14). Le pivot du milieu touche sa
    ligne à 0,2 largeur près. Durée 12 à 150 bougies.
  · Signal : PREMIÈRE clôture sous la ligne basse, avant la pointe, aucune clôture hors du biseau avant,
    dans une durée de biseau après le dernier pivot.
  · Stop « proche » = plus haut des 4 dernières bougies (cassure comprise) ; « loin » = plus haut de tout
    le biseau ; + 0,1 ATR. ⚠️ Premier jet : « proche » = plus haut depuis le dernier sommet. Vu sur les
    planches : dans un biseau ascendant le dernier sommet EST le plus haut, les deux stops tombaient au
    même prix et chaque test aurait été compté deux fois. Corrigé avant tout tableau de résultats.
  · Divergence RSI : RSI au dernier sommet < RSI au premier sommet. EMA 50 : cassure sous l'EMA 50.

Objectif : 2 R (règle maison, et le critère de Mongazi). Sortie par le temps : 120 bougies en H1, 60 en
H4, 40 en D1 (une à deux semaines, deux mois en D1).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..strategies.indicateurs import atr, ema, rsi
from .banc import Serie, Signaux

FIGURES = ("ete", "ete_inverse", "biseau_ascendant", "biseau_descendant")
FILTRES = ("aucun", "rsi", "ema50", "rsi_ema50")
STOPS = ("proche", "loin")
MAX_BARRES = {"M15": 240, "M30": 200, "H1": 120, "H4": 60, "D1": 40}
K = 3
LARGEUR_MIN, LARGEUR_MAX = 12, 150


@dataclass
class Evenement:
    """Une figure qui casse, telle qu'on la voit à la clôture de la bougie `b`."""
    figure: str
    b: int
    sens: int
    stop_proche: float
    stop_loin: float
    rsi_ok: bool
    ema_ok: bool
    pivots: list = field(default_factory=list)       # [(indice, prix)] pour les planches
    lignes: list = field(default_factory=list)       # [((i0, p0), (i1, p1))]


def _pivots_confirmes(h: np.ndarray, l: np.ndarray, k: int = K):
    """Pour chaque bougie b, les changements de la séquence alternée confirmés à sa clôture.
    Renvoie une liste d'états : etats[b] = tuple (type, indice, prix) des pivots connus à la clôture de b,
    mais seulement aux bougies où la séquence change (sinon None), pour économiser la mémoire."""
    n = len(h)
    seq: list[tuple[str, int, float]] = []
    changes = [None] * n
    for b in range(2 * k, n):
        p = b - k
        g_h, d_h = h[p - k:p].max(), h[p + 1:p + k + 1].max()
        g_l, d_l = l[p - k:p].min(), l[p + 1:p + k + 1].min()
        nouveaux = []
        if h[p] > g_h and h[p] >= d_h:
            nouveaux.append(("H", p, float(h[p])))
        if l[p] < g_l and l[p] <= d_l:
            nouveaux.append(("L", p, float(l[p])))
        if len(nouveaux) == 2 and seq and seq[-1][0] == "H":
            nouveaux.reverse()                          # bougie qui fait les deux : l'opposé d'abord
        change = False
        for piv in nouveaux:
            if seq and seq[-1][0] == piv[0]:
                plus_extreme = piv[2] > seq[-1][2] if piv[0] == "H" else piv[2] < seq[-1][2]
                if plus_extreme:
                    seq[-1] = piv
                    change = True
            else:
                seq.append(piv)
                change = True
        if change:
            changes[b] = tuple(seq[-8:])
    return changes


def _ligne(i0, p0, i1, p1):
    pente = (p1 - p0) / (i1 - i0)
    return lambda i: p0 + pente * (i - i0), pente


def detecter(serie: Serie, figure: str) -> list[Evenement]:
    h, l, c = serie.haut, serie.bas, serie.cloture
    n = len(c)
    a = atr(h, l, c, 14)
    r = rsi(c, 14)
    m50 = ema(c, 50)
    changes = _pivots_confirmes(h, l)
    vus: set = set()
    evenements: list[Evenement] = []
    signal_pris = np.zeros(n, dtype=bool)
    for cree, seq in enumerate(changes):
        if seq is None or len(seq) < 5:
            continue
        ev = None
        if figure in ("ete", "ete_inverse"):
            ev = _ete(seq, cree, figure, h, l, c, a, r, m50, vus)
        else:
            ev = _biseau(seq, cree, figure, h, l, c, a, r, m50, vus)
        if ev is not None and not signal_pris[ev.b]:
            signal_pris[ev.b] = True
            evenements.append(ev)
    evenements.sort(key=lambda e: e.b)
    return evenements


def _ete(seq, cree, figure, h, l, c, a, r, m50, vus):
    haut = figure == "ete"                  # sommet : tête = SOMMET le plus haut, cassure vers le bas
    t_tete, t_creux = ("H", "L") if haut else ("L", "H")
    # T2 = le dernier pivot du type « creux de la figure », au plus un pivot après lui
    pos = len(seq) - 1 if seq[-1][0] == t_creux else len(seq) - 2
    if pos < 4:
        return None
    L0, P1, T1, P2, T2 = seq[pos - 4:pos + 1]
    if (L0[0], P1[0], T1[0], P2[0], T2[0]) != (t_creux, t_tete, t_creux, t_tete, t_creux):
        return None
    cle = (figure, P2[1])
    if cle in vus:
        return None
    s = 1 if haut else -1                   # s = +1 : les « hauts » sont des sommets
    if not (s * (P2[2] - P1[2]) > 0):
        return None
    cou, _ = _ligne(T1[1], T1[2], T2[1], T2[2])
    H = s * (P2[2] - cou(P2[1]))
    if not (np.isfinite(a[P2[1]]) and H >= 2 * a[P2[1]]):
        return None
    if abs(T2[2] - T1[2]) > 0.5 * H or not (s * (min(T1[2], T2[2]) if haut else max(T1[2], T2[2])) > s * L0[2]):
        return None
    epaule_g = s * (P1[2] - cou(P1[1]))
    if epaule_g < 0.3 * H:
        return None
    n = len(c)
    largeur_gauche = P2[1] - P1[1]
    extremes = h if haut else l
    extreme_rs, i_rs = -np.inf * s, -1
    for b in range(T2[1] + 1, n):
        # épaule droite = extrême atteint depuis T2 (dans le sens des sommets), suivi bougie après bougie
        if s * (extremes[b] - extreme_rs) > 0:
            extreme_rs, i_rs = float(extremes[b]), b
        if s * (extreme_rs - P2[2]) >= 0:
            vus.add(cle)
            return None                     # la tête est dépassée : plus d'ETE
        if b - T2[1] > 2 * (T2[1] - P1[1]) + 10:
            vus.add(cle)
            return None                     # figure périmée
        franchi = (c[b] < cou(b)) if haut else (c[b] > cou(b))
        if not franchi:
            continue
        if b <= cree:
            # ⚠️ La ligne de cou a été franchie PENDANT la confirmation du dernier pivot : à la clôture de
            # cette bougie la figure n'était pas encore connue. Entrer maintenant, ce serait entrer en retard.
            vus.add(cle)
            return None
        # première clôture au-delà de la ligne de cou : on juge la figure maintenant, avec ce qu'on sait
        vus.add(cle)
        epaule_d = s * (extreme_rs - cou(i_rs))
        largeur = i_rs - P1[1]
        d1, d2 = largeur_gauche, i_rs - P2[1]
        if (i_rs >= b or epaule_d < 0.3 * H or abs(epaule_g - epaule_d) > 0.5 * H
                or not (LARGEUR_MIN <= largeur <= LARGEUR_MAX) or min(d1, d2) <= 0
                or max(d1, d2) > 2.5 * min(d1, d2) or b - i_rs > largeur):
            return None
        tampon = 0.1 * a[b]
        return Evenement(figure, b, -s, extreme_rs + s * tampon, P2[2] + s * tampon,
                         rsi_ok=bool(s * (r[P2[1]] - r[P1[1]]) < 0) if np.isfinite(r[P1[1]]) else False,
                         ema_ok=bool(s * (c[b] - m50[b]) < 0) if np.isfinite(m50[b]) else False,
                         pivots=[(L0[1], L0[2]), (P1[1], P1[2]), (T1[1], T1[2]), (P2[1], P2[2]), (T2[1], T2[2]), (i_rs, extreme_rs)],
                         lignes=[((T1[1], T1[2]), (b, cou(b)))])
    return None


def _biseau(seq, cree, figure, h, l, c, a, r, m50, vus):
    montant = figure == "biseau_ascendant"          # baissier : cassure vers le bas
    cinq = seq[-5:]
    cle = (figure, cinq[0][1])
    if cle in vus:
        return None
    hauts = [p for p in cinq if p[0] == "H"]
    bas = [p for p in cinq if p[0] == "L"]
    if len(hauts) < 2 or len(bas) < 2:
        return None
    signe = 1 if montant else -1
    if not all(signe * (x[2] - y[2]) > 0 for y, x in zip(hauts, hauts[1:])):
        return None
    if not all(signe * (x[2] - y[2]) > 0 for y, x in zip(bas, bas[1:])):
        return None
    haute, pente_h = _ligne(hauts[0][1], hauts[0][2], hauts[-1][1], hauts[-1][2])
    basse, pente_b = _ligne(bas[0][1], bas[0][2], bas[-1][1], bas[-1][2])
    if montant:
        if not (pente_b > pente_h > 0):
            return None
    else:
        if not (pente_h < pente_b < 0):
            return None
    t0, t1 = cinq[0][1], cinq[-1][1]
    w0, w1 = haute(t0) - basse(t0), haute(t1) - basse(t1)
    if not (w0 > 0 and w1 > 0 and w1 <= 0.7 * w0 and np.isfinite(a[t1]) and w0 >= 2 * a[t1]):
        return None
    if not (LARGEUR_MIN <= t1 - t0 <= LARGEUR_MAX):
        return None
    for groupe, ligne_ in ((hauts, haute), (bas, basse)):
        for p in groupe[1:-1]:
            if abs(p[2] - ligne_(p[1])) > 0.2 * (haute(p[1]) - basse(p[1])):
                return None
    n = len(c)
    duree = t1 - t0
    for b in range(t1 + 1, n):
        if b - t1 > duree:
            vus.add(cle)
            return None
        if haute(b) <= basse(b):
            vus.add(cle)
            return None                                    # pointe atteinte sans cassure
        dehors_haut, dehors_bas = c[b] > haute(b), c[b] < basse(b)
        attendu = dehors_bas if montant else dehors_haut
        contraire = dehors_haut if montant else dehors_bas
        if contraire:
            vus.add(cle)
            return None                                    # sorti du mauvais côté
        if not attendu:
            continue
        vus.add(cle)
        if b <= cree:
            return None                                    # cassée avant que le biseau soit connu
        tampon = 0.1 * a[b]
        if montant:
            proche = float(h[b - 3:b + 1].max()) + tampon
            loin = float(h[t0:b + 1].max()) + tampon
            rsi_ok = bool(r[hauts[-1][1]] < r[hauts[0][1]]) if np.isfinite(r[hauts[0][1]]) else False
            ema_ok = bool(c[b] < m50[b]) if np.isfinite(m50[b]) else False
            sens = -1
        else:
            proche = float(l[b - 3:b + 1].min()) - tampon
            loin = float(l[t0:b + 1].min()) - tampon
            rsi_ok = bool(r[bas[-1][1]] > r[bas[0][1]]) if np.isfinite(r[bas[0][1]]) else False
            ema_ok = bool(c[b] > m50[b]) if np.isfinite(m50[b]) else False
            sens = 1
        return Evenement(figure, b, sens, proche, loin, rsi_ok, ema_ok,
                         pivots=[(p[1], p[2]) for p in cinq],
                         lignes=[((t0, haute(t0)), (b, haute(b))), ((t0, basse(t0)), (b, basse(b)))])
    return None


def signaux(serie: Serie, evenements: list[Evenement], *, filtre: str = "aucun", stop: str = "proche",
            rr: float = 2.0) -> Signaux:
    n = len(serie)
    sens = np.zeros(n, np.int8)
    dist = np.zeros(n)
    for e in evenements:
        if filtre in ("rsi", "rsi_ema50") and not e.rsi_ok:
            continue
        if filtre in ("ema50", "rsi_ema50") and not e.ema_ok:
            continue
        niveau = e.stop_proche if stop == "proche" else e.stop_loin
        d = e.sens * (serie.cloture[e.b] - niveau)
        if d > 0:
            sens[e.b], dist[e.b] = e.sens, d
    return Signaux(sens, dist, rr=rr, max_barres=MAX_BARRES[serie.tf])
