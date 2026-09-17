# -*- coding: utf-8 -*-
"""
La détection des figures chartistes ment-elle ? Figures fabriquées à la main, puis vraies bougies.

    python -m trading.recherche._qc_figures

Appelé par `_qc_banc.controles`, donc par `python -m trading.outils.qc`.
"""
from __future__ import annotations

import dataclasses
import sys

import numpy as np


def _serie(points: list[tuple[int, float]], n: int, *, eps: float = 0.0005, base: str = "EURUSD", tf: str = "H4"):
    """Bougies qui suivent une ligne brisée : ouverture = clôture précédente, mèches de `eps`."""
    from trading.recherche import banc
    idx = np.arange(n)
    x, y = zip(*points)
    prix = np.interp(idx, x, y)
    o = np.concatenate(([prix[0]], prix[:-1]))
    h = np.maximum(o, prix) + eps
    l = np.minimum(o, prix) - eps
    temps = (np.datetime64("2020-01-06T00:00") + idx * np.timedelta64(4, "h")).astype("datetime64[s]")
    return banc.Serie(base, tf, temps, o, h, l, prix.copy(), point=1e-5, cout_sens_pts=2.5, swap_long_pts=0.0,
                      swap_court_pts=0.0, nuits_cumul=np.zeros(n), stop_min_prix=0.0002)


def controles(verifier) -> None:
    from trading.recherche import banc, figures

    # --- 1. un ETE dessiné à la main est reconnu, avec les bons stops -----------------
    ete = [(0, 1.03), (10, 0.95), (25, 1.05), (35, 1.00), (50, 1.12), (60, 1.00), (72, 1.05), (85, 0.97), (130, 0.90)]
    s = _serie(ete, 130)
    ev = figures.detecter(s, "ete")
    verifier(len(ev) == 1 and ev[0].sens == -1 and 75 <= ev[0].b <= 82
             and abs(ev[0].stop_proche - (1.05 + 0.0005 + 0.1 * _atr(s, ev[0].b))) < 1e-9
             and abs(ev[0].stop_loin - (1.12 + 0.0005 + 0.1 * _atr(s, ev[0].b))) < 1e-9,
             "figures : un ETE dessiné est reconnu à la cassure de la ligne de cou, stop épaule droite / tête",
             str([(e.b, e.sens, e.stop_proche, e.stop_loin) for e in ev]))
    sans_cassure = [(0, 1.03), (10, 0.95), (25, 1.05), (35, 1.00), (50, 1.12), (60, 1.00), (72, 1.05), (130, 1.03)]
    verifier(len(figures.detecter(_serie(sans_cassure, 130), "ete")) == 0,
             "TÉMOIN : même figure sans cassure de la ligne de cou, aucun signal")
    epaule_trop_haute = [(0, 1.03), (10, 0.95), (25, 1.05), (35, 1.00), (50, 1.12), (60, 1.00), (72, 1.15), (85, 0.97), (130, 0.90)]
    verifier(len(figures.detecter(_serie(epaule_trop_haute, 130), "ete")) == 0,
             "TÉMOIN : épaule droite au-dessus de la tête, ce n'est plus un ETE")
    miroir = [(i, 2.0 - p) for i, p in ete]
    ev_inv = figures.detecter(_serie(miroir, 130), "ete_inverse")
    verifier(len(ev_inv) == 1 and ev_inv[0].sens == 1 and len(figures.detecter(_serie(miroir, 130), "ete")) == 0,
             "figures : l'ETE inversé (miroir) est reconnu en achat, et n'est pas pris pour un ETE")

    # --- 2. biseau ascendant : convergent oui, canal parallèle non -------------------
    biseau = [(0, 1.03), (10, 1.00), (20, 1.10), (32, 1.04), (44, 1.12), (56, 1.08), (62, 1.105), (80, 1.02), (120, 1.00)]
    ev_b = figures.detecter(_serie(biseau, 120), "biseau_ascendant")
    verifier(len(ev_b) == 1 and ev_b[0].sens == -1 and 62 < ev_b[0].b <= 68,
             "figures : un biseau ascendant dessiné est reconnu à la cassure de sa ligne basse",
             str([(e.b, e.sens) for e in ev_b]))
    canal = [(0, 1.03), (10, 1.00), (20, 1.10), (32, 1.018), (44, 1.12), (56, 1.038), (62, 1.07), (80, 0.98), (120, 0.97)]
    verifier(len(figures.detecter(_serie(canal, 120), "biseau_ascendant")) == 0,
             "TÉMOIN : un canal parallèle montant n'est pas un biseau")
    # Cassure 2 bougies après le dernier creux, AVANT sa confirmation (3 bougies) : à la clôture de la cassure
    # le biseau n'était pas connu. Un signal daté de cette bougie lirait le futur.
    trop_tot = [(0, 1.03), (10, 1.00), (20, 1.10), (32, 1.04), (44, 1.12), (56, 1.08), (57, 1.09), (58, 1.082),
                (61, 1.0845), (70, 1.05), (120, 1.00)]
    ev_tot = figures.detecter(_serie(trop_tot, 120, eps=0.0001), "biseau_ascendant")
    verifier(all(e.b > 59 for e in ev_tot),
             "figures : une cassure pendant la confirmation du dernier pivot ne donne jamais de signal daté d'avant lui",
             str([e.b for e in ev_tot]))
    miroir_b = [(i, 2.0 - p) for i, p in biseau]
    ev_bd = figures.detecter(_serie(miroir_b, 120), "biseau_descendant")
    verifier(len(ev_bd) == 1 and ev_bd[0].sens == 1, "figures : le biseau descendant (miroir) est reconnu en achat")

    # --- 3. filtres et distance de stop ------------------------------------------------
    e0 = dataclasses.replace(ev[0], rsi_ok=False, ema_ok=True)
    sig_aucun = figures.signaux(s, [e0], filtre="aucun", stop="proche")
    sig_rsi = figures.signaux(s, [e0], filtre="rsi", stop="proche")
    sig_ema = figures.signaux(s, [e0], filtre="ema50", stop="loin")
    verifier(sig_aucun.sens[e0.b] == -1 and sig_rsi.sens[e0.b] == 0 and sig_ema.sens[e0.b] == -1
             and abs(sig_ema.stop_dist[e0.b] - (e0.stop_loin - s.cloture[e0.b])) < 1e-12 and sig_aucun.rr == 2.0,
             "figures : le filtre RSI écarte une figure sans divergence (témoin : sans filtre et avec EMA 50 elle passe)")

    # --- 4. vraies bougies : le futur ne change aucun signal passé ---------------------
    try:
        vraie = banc.charger("EURUSD", "H1")
    except FileNotFoundError:
        verifier(True, "figures : données H1 absentes, contrôle sur vraies bougies sauté")
        return
    g = (vraie.temps >= np.datetime64("2016-01-01")) & (vraie.temps < np.datetime64("2019-01-01"))
    vraie = dataclasses.replace(vraie, temps=vraie.temps[g], ouverture=vraie.ouverture[g], haut=vraie.haut[g],
                                bas=vraie.bas[g], cloture=vraie.cloture[g], nuits_cumul=vraie.nuits_cumul[g])
    # Les pivots connus à la clôture d'une bougie ne doivent pas changer quand les données s'arrêtent à cette
    # bougie. (Le contrôle « futur » plus bas ne voit qu'une fuite qui traverse SA coupure : une bougie de trop
    # lue à droite d'un pivot lui échappait, prouvé en l'injectant le 2026-09-17.)
    court = dataclasses.replace(vraie, temps=vraie.temps[:3000], haut=vraie.haut[:3000], bas=vraie.bas[:3000])

    def dernier_etat(etats, b):
        while b >= 0 and etats[b] is None:
            b -= 1
        return etats[b] if b >= 0 else None
    etats = figures._pivots_confirmes(court.haut, court.bas)
    # ⚠️ Tirer parmi TOUTES les bougies, pas seulement celles où l'état change : une fuite qui SUPPRIME un
    # pivot (le futur le dément) ne laisse aucun changement à tirer. Premier jet aveugle, prouvé le 2026-09-17.
    tirage = np.random.default_rng(9).choice(np.arange(30, len(court.haut)), size=300, replace=False)
    differentes = [int(b) for b in tirage
                   if dernier_etat(figures._pivots_confirmes(court.haut[:b + 1], court.bas[:b + 1]), b) != dernier_etat(etats, b)]
    verifier(not differentes and len(tirage) >= 300,
             "figures : les pivots connus à chaque bougie sont les mêmes quand les données s'arrêtent à cette bougie",
             str(differentes[:5]))
    coupe = int(len(vraie) * 0.6)
    futur = dataclasses.replace(vraie, ouverture=vraie.ouverture.copy(), haut=vraie.haut.copy(), bas=vraie.bas.copy(),
                                cloture=vraie.cloture.copy())
    for tab in (futur.ouverture, futur.haut, futur.bas, futur.cloture):
        tab[coupe + 1:] = tab[coupe + 1:][::-1] * 1.02
    futur.haut[coupe + 1:], futur.bas[coupe + 1:] = (np.maximum(futur.haut[coupe + 1:], futur.bas[coupe + 1:]),
                                                     np.minimum(futur.haut[coupe + 1:], futur.bas[coupe + 1:]))
    fautives, total = [], 0
    for f in figures.FIGURES:
        a = [(e.b, e.sens, round(e.stop_proche, 8), round(e.stop_loin, 8), e.rsi_ok, e.ema_ok)
             for e in figures.detecter(vraie, f) if e.b <= coupe]
        b = [(e.b, e.sens, round(e.stop_proche, 8), round(e.stop_loin, 8), e.rsi_ok, e.ema_ok)
             for e in figures.detecter(futur, f) if e.b <= coupe]
        total += len(a)
        if a != b:
            fautives.append(f)
    verifier(not fautives and total > 20,
             "figures : changer le futur ne change aucune figure détectée avant la coupure (témoin : il y en a)",
             f"{', '.join(fautives)} · {total} figures")


def _atr(serie, b):
    from trading.strategies.indicateurs import atr
    return float(atr(serie.haut, serie.bas, serie.cloture, 14)[b])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    resultats = []

    def verifier(condition, libelle, detail=""):
        resultats.append(bool(condition))
        print(f"  {'✓' if condition else '✗'} {libelle}" + (f"  ({detail})" if detail and not condition else ""))
    controles(verifier)
    print(f"\n  {sum(resultats)} verts · {len(resultats) - sum(resultats)} rouges")
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
