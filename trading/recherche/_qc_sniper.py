# -*- coding: utf-8 -*-
"""
La simulation « Sniper Entry » ment-elle ? Preuves sur bougies fabriquées, puis sur les vraies.

    python -m trading.recherche._qc_sniper

Appelé par `_qc_banc.controles`, donc par `python -m trading.outils.qc`.
Chaque verrou a son TÉMOIN : un verrou resté fermé pour toujours passerait sinon avec les honneurs.
"""
from __future__ import annotations

import dataclasses
import sys
from datetime import datetime

import numpy as np


def _simuler_fabrique(o, h, l, c, *, sens=-1, clo=1.1000, ext=1.1010, validite=4, rr=3.0, bloque=None,
                      mode_annonces=0, stops_level=20.0, elargir=True):
    from trading.recherche import sniper
    n = len(c)
    m15_de = np.arange(n, dtype=np.int64) // 15
    fin_m15 = (np.arange(n) % 15) == 14
    n15 = n // 15 + 1
    sens15 = np.zeros(n15, np.int8)
    rc, rx = np.zeros(n15), np.zeros(n15)
    sens15[1], rc[1], rx[1] = sens, clo, ext                 # balayage à la clôture de la M15 n° 1 (M1 29)
    zeros_b = np.zeros(n, np.bool_)
    return sniper._simuler(o, h, l, c, m15_de, fin_m15, np.full(n, 3.0), 1e-5, 1.0, stops_level, 1.0,
                           sens15, rc, rx, validite, rr, 1.5, elargir, False, np.full(n, np.nan), np.full(n, np.nan),
                           zeros_b if bloque is None else bloque, zeros_b, mode_annonces, zeros_b,
                           np.zeros(n), 0.0, 0.0, np.zeros(n15), np.zeros(n15), 12, 0, n - 1)


def _bougies(n=120, prix=1.1005, ecart=0.00005):
    o = np.full(n, prix)
    return o.copy(), o + ecart, o - ecart, o.copy()


def controles(verifier) -> None:
    from trading.recherche import annonces, compte, sniper

    # --- 1. une vente est stoppée par l'ASK, pas par le bid ------------------
    o, h, l, c = _bougies()
    c[31] = 1.0995                                          # clôture M1 sous le rectangle
    o[32] = 1.0995
    l[31] = l[32] = 1.0994
    t = _simuler_fabrique(o, h, l, c)
    entree = 1.0995 - 1e-5
    stop = 1.1010 + 1.5 * 3e-5
    d = stop - entree
    h2 = h.copy()
    h2[40] = stop - 2e-5                                     # bid 2 points sous le stop, ask 1 point au-dessus
    t_ask = _simuler_fabrique(o, h2, l, c)
    h3 = h.copy()
    h3[40] = stop - 4e-5                                     # ask 1 point sous le stop
    t_temoin = _simuler_fabrique(o, h3, l, c)
    verifier(len(t_ask[0]) == 1 and t_ask[0][0] == 32 and t_ask[4][0] == sniper.STOP and t_ask[1][0] == 40
             and abs(t_ask[3][0] - (-(d + 1e-5) / d)) < 1e-9,
             "sniper : entrée à l'ouverture qui suit la clôture M1, vente stoppée quand l'ASK touche le stop",
             str((t_ask[0], t_ask[1], t_ask[3], t_ask[4])))
    verifier(len(t_temoin[0]) == 1 and t_temoin[1][0] != 40,
             "TÉMOIN : ask sous le stop, la vente reste ouverte")
    verifier(len(t[0]) == 1 and abs(t[6][0] - stop) < 1e-12 and abs(t[7][0] - (entree - 3 * d)) < 1e-12,
             "sniper : stop = extrême + 1,5 spread, objectif = 3 R depuis l'entrée réelle (glissement compris)")

    # --- 2. stop et objectif dans la même bougie : le stop d'abord ----------
    h4, l4 = h.copy(), l.copy()
    h4[40], l4[40] = stop + 1e-4, entree - 4 * d
    t_meme = _simuler_fabrique(o, h4, l4, c)
    l5 = l.copy()
    l5[40] = entree - 3 * d - 4e-5                          # l'ask passe l'objectif
    t_obj = _simuler_fabrique(o, h, l5, c)
    verifier(len(t_meme[0]) == 1 and t_meme[4][0] == sniper.STOP, "sniper : stop et objectif dans la même bougie, le stop d'abord")
    verifier(len(t_obj[0]) == 1 and t_obj[4][0] == sniper.OBJECTIF and abs(t_obj[3][0] - 3.0) < 1e-9,
             "TÉMOIN : l'objectif seul rapporte exactement +3 R", str((t_obj[3], t_obj[4])))

    # --- 3. clôture M15 au-delà du sommet = rectangle invalidé ------------------
    o6, h6, l6, c6 = _bougies()
    c6[44], h6[44] = 1.1012, 1.1013                          # la M15 n° 2 clôture au-dessus du sommet
    c6[50], o6[51] = 1.0995, 1.0995
    t_inv = _simuler_fabrique(o6, h6, l6, c6)
    o7, h7, l7, c7 = _bougies()
    h7[44] = 1.1013                                          # une MÈCHE au-dessus, clôture dessous : encore valide
    c7[50], o7[51] = 1.0995, 1.0995
    t_meche = _simuler_fabrique(o7, h7, l7, c7)
    verifier(len(t_inv[0]) == 0, "sniper : une clôture M15 au-dessus du sommet invalide le rectangle")
    verifier(len(t_meche[0]) == 1 and t_meche[0][0] == 51 and abs(t_meche[6][0] - (1.1013 + 4.5e-5)) < 1e-12,
             "TÉMOIN : une mèche au-dessus sans clôture garde le setup, et le stop suit le nouvel extrême",
             str((t_meche[0], t_meche[6])))

    # --- 4. validité : 1 bougie M15 ------------------------------------------
    o8, h8, l8, c8 = _bougies()
    c8[50], o8[51] = 1.0995, 1.0995                          # déclenchement dans la M15 n° 3
    verifier(len(_simuler_fabrique(o8, h8, l8, c8, validite=1)[0]) == 0
             and len(_simuler_fabrique(o8, h8, l8, c8, validite=2)[0]) == 1,
             "sniper : le rectangle expire après N bougies M15 (témoin : à N+1 il déclenche)")

    # --- 5. annonces : entrée bloquée, et fenêtre -30/+15 min ----------------
    bloque = np.zeros(120, np.bool_)
    bloque[32] = True
    t_bl = _simuler_fabrique(o, h, l, c, bloque=bloque, mode_annonces=1)
    verifier(len(t_bl[0]) == 0 or t_bl[0][0] != 32, "sniper : pas d'entrée dans la fenêtre d'une annonce (mode 1)")
    verifier(len(_simuler_fabrique(o, h, l, c, bloque=bloque, mode_annonces=0)[0]) == 1,
             "TÉMOIN : sans filtre, la même entrée est prise")
    temps = (np.datetime64("2026-01-09T11:50") + np.arange(60) * np.timedelta64(1, "m")).astype("datetime64[s]")
    ann = np.array(["2026-01-09T12:30:00"], dtype="datetime64[s]")
    b = annonces.fenetre_bloquee(temps, ann, avant_min=30, apres_min=15)
    minute = lambda hm: int((np.datetime64(f"2026-01-09T{hm}") - np.datetime64("2026-01-09T11:50")) / np.timedelta64(1, "m"))  # noqa: E731
    verifier(b[minute("11:59")] and b[minute("12:45")] and not b[minute("11:58")] and not b[minute("12:46")],
             "annonces : bougies bloquées de 30 min avant à 15 min après (bornes exactes)",
             str([bool(b[minute(x)]) for x in ("11:58", "11:59", "12:45", "12:46")]))

    # --- 6. stop plus court que le minimum du courtier ------------------------
    t_saute = _simuler_fabrique(o, h, l, c, stops_level=500.0, elargir=False)
    t_elargi = _simuler_fabrique(o, h, l, c, stops_level=500.0, elargir=True)
    verifier(len(t_saute[0]) == 0 and len(t_elargi[0]) == 1 and t_elargi[11][0]
             and abs(t_elargi[9][0] - (500e-5 + 3e-5)) < 1e-12,
             "sniper : stop sous le minimum du courtier, élargi à stops level + spread (ou trade sauté)")

    # --- 7. compte de 10 000 $ : tailles réelles ------------------------------
    from trading.noyau.risque import SpecsSymbole
    eu = SpecsSymbole(nom="EURUSD", point=1e-5, digits=5, volume_min=0.01, volume_max=20, volume_step=0.01,
                      valeur_tick=1.0, taille_tick=1e-5, taille_contrat=100000, stops_level_points=20)
    tr = [compte.TradeCompte("EURUSD", datetime(2025, 3, 4, 9, 0), datetime(2025, 3, 4, 9, 30), -1, 2.0, 25.0, 1.10)]
    video = compte.simuler_compte(tr, {"EURUSD": eu}, risque_pct=1.0, regles="video").resume()
    tr2 = [dataclasses.replace(tr[0])]
    pro = compte.simuler_compte(tr2, {"EURUSD": eu}, risque_pct=1.0, regles="pro").resume()
    verifier(abs(video["benefice_usd"] - 200.0) < 1e-6 and abs(video["lots_moyens"] - 4.0) < 1e-9,
             "compte : 1 % de 10 000 $ sur 25 points = 4 lots, +2 R = +200 $", str(video.get("benefice_usd")))
    verifier(pro["lots_moyens"] < 0.3 and pro["benefice_usd"] < 20,
             "compte NEBULA PRO : levier ×3 plafonne la taille du même trade (témoin : la vidéo prend 4 lots)",
             str((pro.get("lots_moyens"), pro.get("benefice_usd"))))
    serie = compte.series_perdantes(np.array([-1.0] * 6 + [3.0] * 94))
    verifier(serie["plus_longue_observee"] == 6 and serie["p_6_pertes_sur_100_sequence_reelle"] == 1.0,
             "compte : série de 6 pertes comptée sur la vraie séquence")

    # --- 8. les vraies bougies : référence, futur, exemples de la vidéo ---------
    from trading.recherche import banc
    try:
        s = banc.charger("EURUSD", "M1")
    except FileNotFoundError:
        verifier(True, "sniper : données M1 absentes, contrôles sur vraies bougies sautés")
        return
    garde = (s.temps >= np.datetime64("2025-08-01")) & (s.temps < np.datetime64("2025-11-10"))
    s = dataclasses.replace(s, temps=s.temps[garde], ouverture=s.ouverture[garde], haut=s.haut[garde],
                            bas=s.bas[garde], cloture=s.cloture[garde], nuits_cumul=s.nuits_cumul[garde])
    prep = sniper.preparer(s, spread_constant=3.0)
    for fvg in (False, True):
        r = sniper.Reglages(fvg=fvg)
        rapide = sniper.balayages(prep, r)
        lente = sniper.balayages_reference(prep, r)
        verifier(np.array_equal(rapide[0], lente[0]) and np.allclose(rapide[1], lente[1]) and np.allclose(rapide[2], lente[2])
                 and (rapide[0] != 0).sum() > 10,
                 f"sniper : balayages compilés = version Python, setup pour setup (imbalance exigé={fvg}, témoin : il y en a)",
                 f"{int((rapide[0] != 0).sum())} contre {int((lente[0] != 0).sum())}")
    r = sniper.Reglages()
    trades = sniper.simuler(prep, r)
    coupe = int(len(s) * 0.6)
    futur = dataclasses.replace(s, ouverture=s.ouverture.copy(), haut=s.haut.copy(), bas=s.bas.copy(), cloture=s.cloture.copy())
    for tab in (futur.ouverture, futur.haut, futur.bas, futur.cloture):
        tab[coupe + 1:] = tab[coupe + 1:][::-1] * 1.013
    futur.haut[coupe + 1:], futur.bas[coupe + 1:] = (np.maximum(futur.haut[coupe + 1:], futur.bas[coupe + 1:]),
                                                     np.minimum(futur.haut[coupe + 1:], futur.bas[coupe + 1:]))
    t_futur = sniper.simuler(sniper.preparer(futur, spread_constant=3.0), r)
    avant = trades.sortie < coupe
    avant_f = t_futur.sortie < coupe
    verifier(avant.sum() > 20 and np.array_equal(trades.entree[avant], t_futur.entree[avant_f])
             and np.allclose(trades.R[avant], t_futur.R[avant_f]),
             "sniper : changer le futur ne change aucun trade clos avant la coupure (aucun regard vers le futur)",
             f"{int(avant.sum())} contre {int(avant_f.sum())}")
    # Le test ci-dessus n'attrape qu'un regard vers le futur qui TRAVERSE sa coupure. Celui-ci coupe les
    # données à la minute même de chaque entrée (la bougie d'entrée réduite à son ouverture, seule chose
    # connue quand l'ordre part) : la décision doit exister à l'identique, sans rien voir après elle.
    rng = np.random.default_rng(3)
    echantillon = rng.choice(len(trades), size=min(25, len(trades)), replace=False)
    ecarts = []
    for q in echantillon:
        e = int(trades.entree[q])
        # ⚠️ Un trade n'est ENREGISTRÉ qu'à sa sortie : on ajoute 6 minutes plates au prix d'ouverture pour
        # qu'il se clôture (1er jet du test : rouge sur le code sain pour cette seule raison).
        plat = np.full(6, s.ouverture[e])
        prix = lambda tab: np.concatenate((tab[:e], [s.ouverture[e]], plat))  # noqa: E731
        temps = np.concatenate((s.temps[:e + 1], s.temps[e] + np.arange(1, 7) * np.timedelta64(60, "s")))
        coupee = dataclasses.replace(s, temps=temps, ouverture=prix(s.ouverture), haut=prix(s.haut), bas=prix(s.bas),
                                     cloture=prix(s.cloture),
                                     nuits_cumul=np.concatenate((s.nuits_cumul[:e + 1], np.full(6, s.nuits_cumul[e]))))
        tc = sniper.simuler(sniper.preparer(coupee, spread_constant=3.0), r)
        k = np.where(tc.entree == e)[0]
        if not (len(k) and abs(tc.prix_entree[k[0]] - trades.prix_entree[q]) < 1e-12
                and abs(tc.stop[k[0]] - trades.stop[q]) < 1e-12 and abs(tc.cible[k[0]] - trades.cible[q]) < 1e-12):
            ecarts.append(str(s.temps[e])[:16])
    verifier(not ecarts and len(echantillon) >= 20,
             "sniper : 25 entrées réelles se reproduisent à l'identique avec des données coupées à la minute d'entrée",
             ", ".join(ecarts[:5]))
    d15 = prep.m15.debut
    trouves = []
    for t_ in ("2025-10-31T01:15", "2025-10-31T06:15", "2025-10-31T15:45"):
        j = int(np.searchsorted(d15, np.datetime64(t_)))
        k = np.where(trades.balayage_m15 == j)[0]
        trouves.append(bool(len(k)) and trades.motif[k[0]] == sniper.OBJECTIF)
    verifier(all(trouves), "sniper : les exemples 1, 2 et 3 de la vidéo sont détectés et gagnent, comme à l'écran", str(trouves))


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
