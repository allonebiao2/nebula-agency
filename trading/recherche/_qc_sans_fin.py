# -*- coding: utf-8 -*-
"""
Les contrôles de la recherche sans fin.

    python -m trading.recherche._qc_sans_fin

Ce qu'ils protègent, dans l'ordre d'importance :
  1. **L'étiquette dit la même chose que le simulateur.** Toute la vague 1 repose là-dessus.
  2. **Aucun trade ne passe la nuit.** C'est la règle de Mongazi, et elle doit tenir dans les DEUX
     noyaux (marché et ordre limite), pas seulement dans celui qu'on a écrit en dernier.
  3. **Le scellé refuse de s'ouvrir deux fois.** Sinon ce n'est plus un scellé, c'est un réglage.
  4. **Une fuite du futur injectée doit virer au rouge.** Un contrôle qu'on n'a jamais vu échouer ne
     prouve rien : chaque contrôle ci-dessous est prouvé sur une faute fabriquée exprès.
"""
from __future__ import annotations

import sys

import numpy as np

from . import banc, caracteristiques, etiquettes, intraday
from .banc import OBJECTIF, SEANCE

VERTS, ROUGES = 0, 0


def verifier(condition: bool, libelle: str) -> None:
    global VERTS, ROUGES
    if condition:
        VERTS += 1
        print(f"  ✓ {libelle}")
    else:
        ROUGES += 1
        print(f"  ✗ {libelle}")


def _serie(n: int = 6000, base: str = "EURUSD", graine: int = 3) -> banc.Serie:
    """Une série M1 fabriquée, avec des minutes vraies (donc de vraies séances New York)."""
    rng = np.random.default_rng(graine)
    temps = (np.datetime64("2024-03-04T00:00:00") + np.arange(n) * np.timedelta64(1, "m")).astype("datetime64[s]")
    pas = rng.normal(0, 0.0004, n).cumsum()
    clo = 1.09 + pas
    ouv = np.concatenate(([clo[0]], clo[:-1]))
    haut = np.maximum(ouv, clo) + np.abs(rng.normal(0, 0.0002, n))
    bas = np.minimum(ouv, clo) - np.abs(rng.normal(0, 0.0002, n))
    return banc.Serie(base, "M1", temps, ouv, haut, bas, clo, point=1e-5, cout_sens_pts=2.5,
                      swap_long_pts=0.0, swap_court_pts=0.0, nuits_cumul=np.zeros(n),
                      stop_min_prix=20 * 1e-5)


def qc_etiquette_egale_simulateur() -> None:
    """L'étiquette d'une barre = le trade que le banc aurait fait, au R près."""
    s = _serie()
    stop = etiquettes.stops_points(s, 60)
    permis = intraday.masque_entree(s.base, s.temps)
    e = etiquettes.etiqueter(s, stop_dist=stop, sens=+1, permis=permis)
    # Des signaux ÉPARS : le banc n'autorise qu'une position à la fois, donc on espace les entrées.
    epars = np.zeros(len(s), bool)
    candidats = np.flatnonzero(permis & e.valides())
    choisis = candidats[::400]
    epars[choisis] = True
    sig = banc.Signaux(sens=np.where(epars, 1, 0).astype(np.int8), stop_dist=stop, rr=2.0,
                       max_barres=1440, fin_seance=intraday.fin_de_journee(s.base, s.temps))
    t = banc.simuler(s, sig)
    # Le banc peut sauter un signal si le précédent trade dure encore : on compare les communs.
    attendus = {int(i): float(e.R[i]) for i in choisis}
    ecarts = [abs(attendus[int(t.entree[k] - 1)] - float(t.R[k])) for k in range(len(t))
              if int(t.entree[k] - 1) in attendus]
    verifier(len(ecarts) >= 5 and max(ecarts) < 1e-9,
             f"étiquette = simulateur au R près ({len(ecarts)} trades comparés)")
    # TÉMOIN : une étiquette calculée avec un coût faux doit, elle, différer.
    chere = banc.Serie(**{**s.__dict__, "cout_sens_pts": 25.0, "cout_bar_prix": None})
    e2 = etiquettes.etiqueter(chere, stop_dist=stop, sens=+1, permis=permis)
    verifier(any(abs(float(e2.R[i]) - attendus[int(i)]) > 1e-6 for i in choisis),
             "TÉMOIN : un coût dix fois plus cher change bien les étiquettes")


def qc_aucune_nuit() -> None:
    """Aucun trade, dans aucun des deux noyaux, ne survit à la clôture de sa journée."""
    s = _serie(n=20000)
    stop = etiquettes.stops_points(s, 300)          # assez large pour que le temps décide
    fs = intraday.fin_de_journee(s.base, s.temps)
    jour = intraday.jour_ny(s.temps)
    sens = np.zeros(len(s), np.int8)
    sens[np.flatnonzero(intraday.masque_entree(s.base, s.temps))[::120]] = 1
    t = banc.simuler(s, banc.Signaux(sens=sens, stop_dist=stop, rr=2.0, max_barres=1440, fin_seance=fs))
    meme_jour = all(jour[t.entree[k]] == jour[t.sortie[k]] for k in range(len(t)))
    verifier(len(t) > 20 and meme_jour, f"marché : les {len(t)} trades se ferment le jour même")

    i = np.flatnonzero(intraday.masque_entree(s.base, s.temps))[::120]
    d = stop[i]
    o = banc.Ordres(pose=i.astype(np.int64), sens=np.ones(len(i), np.int8),
                    limite=s.cloture[i] - 0.25 * d, stop=s.cloture[i] - 1.25 * d,
                    cible=s.cloture[i] + 1.75 * d, expire=(i + 30).astype(np.int64),
                    max_barres=1440, fin_seance=fs)
    t2 = banc.simuler(s, o)
    verifier(len(t2) > 5 and all(jour[t2.entree[k]] == jour[t2.sortie[k]] for k in range(len(t2))),
             f"ordres limites : les {len(t2)} trades se ferment le jour même")
    # TÉMOIN : sans le masque de fin de journée, et avec de quoi durer, des trades traversent la nuit.
    large = etiquettes.stops_points(s, 2000)
    t3 = banc.simuler(s, banc.Signaux(sens=sens, stop_dist=large, rr=2.0, max_barres=5000))
    verifier(any(jour[t3.entree[k]] != jour[t3.sortie[k]] for k in range(len(t3))),
             "TÉMOIN : sans la règle, des trades passent bien la nuit")


def qc_fuite_du_futur() -> None:
    """Une caractéristique qui regarde une barre future doit se voir : on en fabrique une."""
    s = _serie(n=8000)
    X = caracteristiques.construire(s)
    futur = np.concatenate((s.cloture[1:], [s.cloture[-1]])) - s.cloture
    suspectes = []
    for nom, v in X.items():
        fini = np.isfinite(v) & np.isfinite(futur)
        if fini.sum() < 500:
            continue
        c = abs(float(np.corrcoef(v[fini], futur[fini])[0, 1]))
        if c > 0.2:
            suspectes.append((nom, round(c, 3)))
    verifier(not suspectes, f"aucune caractéristique ne corrèle au rendement de la barre suivante "
                            f"({'rien' if not suspectes else suspectes})")
    triche = np.corrcoef(futur[:-1], futur[:-1])[0, 1]
    verifier(abs(triche) > 0.9, "TÉMOIN : la sonde repère bien une corrélation parfaite au futur")


def qc_etiquette_ne_regarde_pas_apres() -> None:
    """Changer le futur lointain ne doit pas changer une étiquette déjà résolue."""
    s = _serie(n=5000)
    stop = etiquettes.stops_points(s, 60)
    e1 = etiquettes.etiqueter(s, stop_dist=stop, sens=+1)
    # La coupe doit tomber PENDANT un trade, sinon le témoin n'a rien à montrer : on la pose juste
    # après une entrée valide dont la durée déborde.
    fin_trade = np.arange(len(s)) + 1 + e1.duree
    candidats = np.flatnonzero(e1.valides() & (e1.duree > 3))
    coupe = int(fin_trade[candidats[len(candidats) // 2]]) - 1
    s2 = banc.Serie(**{**s.__dict__})
    s2.cloture = s.cloture.copy(); s2.haut = s.haut.copy(); s2.bas = s.bas.copy(); s2.ouverture = s.ouverture.copy()
    s2.cloture[coupe:] += 0.02
    s2.haut[coupe:] += 0.02
    s2.bas[coupe:] += 0.02
    s2.ouverture[coupe:] += 0.02
    e2 = etiquettes.etiqueter(s2, stop_dist=stop, sens=+1)
    fini_avant = np.flatnonzero(e1.valides() & (np.arange(len(s)) + 1 + e1.duree < coupe))
    identiques = np.allclose(np.nan_to_num(e1.R[fini_avant]), np.nan_to_num(e2.R[fini_avant]))
    verifier(len(fini_avant) > 100 and identiques,
             f"un futur modifié ne change aucune étiquette déjà résolue ({len(fini_avant)} barres)")
    tardives = np.flatnonzero(e1.valides() & (np.arange(len(s)) + 1 + e1.duree >= coupe))
    verifier(len(tardives) > 0 and not np.allclose(np.nan_to_num(e1.R[tardives]),
                                                   np.nan_to_num(e2.R[tardives])),
             "TÉMOIN : les étiquettes qui débordent après la coupe changent, elles")


def qc_point_mort() -> None:
    """Le point mort mesuré doit valoir 1/3 quand les trades sont propres, et monter avec le coût."""
    R = np.array([2.0] * 100 + [-1.0] * 200)
    obj = np.array([True] * 100 + [False] * 200)
    verifier(abs(banc.point_mort_objectif(R, obj) - 1 / 3) < 1e-9,
             "point mort = 33,3 % quand un gain vaut 2 R et une perte 1 R")
    R2 = np.array([1.9] * 100 + [-1.1] * 200)
    verifier(banc.point_mort_objectif(R2, obj) > 1 / 3,
             "TÉMOIN : avec des coûts, le point mort monte au-dessus de 33,3 %")
    verifier(banc.p_binomial(50, 100, 1 / 3) < 1e-3 and banc.p_binomial(33, 100, 1 / 3) > 0.4,
             "test binomial : 50 objectifs sur 100 est improbable au point mort, 33 ne l'est pas")


def qc_scelle() -> None:
    """Le scellé s'ouvre une fois, et le dit."""
    from . import scelle
    verifier(set(scelle.PERIODES) == {"EURUSD", "NAS100"}, "le scellé couvre les deux instruments")
    debut, fin = scelle.PERIODES["NAS100"]
    verifier(debut == "2020-01-01" and fin == "2024-01-01",
             "NAS100 : 2020-2023 scellés (Deriv commence en 2024)")
    d2, f2 = scelle.PERIODES["EURUSD"]
    verifier(d2 < "2012-01-01" and f2 == "2012-01-01",
             "EUR/USD : avant 2012 scellé (Deriv commence en 2012 en M5-M15)")
    vues = scelle._journal()
    doublons = [o["candidate"] for o in vues if sum(
        1 for x in vues if x["candidate"] == o["candidate"] and x["base"] == o["base"]
        and x["tf"] == o["tf"]) > 1]
    verifier(not doublons, f"aucune candidate n'a ouvert deux fois le même scellé ({len(vues)} ouvertures)")


def qc_dukascopy() -> None:
    """Les données d'époque : mêmes minutes, même horloge, pas de doublon, pas de barre plate."""
    from . import dukascopy
    for base in ("NAS100", "EURUSD"):
        lu = dukascopy.lire_cache(base, "M1")
        if lu is None:
            print(f"  · {base} Dukascopy pas encore téléchargé, contrôles sautés")
            continue
        tab, meta = lu
        t = tab["temps"]
        verifier(bool(np.all(np.diff(t.astype("int64")) > 0)),
                 f"{base} Dukascopy : horodatages strictement croissants ({len(t)} barres)")
        ok_prix = np.all(tab["haut"] >= tab["bas"]) and np.all(tab["haut"] >= tab["ouverture"]) \
            and np.all(tab["bas"] <= tab["cloture"])
        verifier(bool(ok_prix), f"{base} Dukascopy : hauts et bas cohérents avec ouverture et clôture")
        # L'écart d'époque doit exister et être positif : c'est lui qui rend le coût honnête.
        if "ecart_prix" in tab:
            e = tab["ecart_prix"]
            verifier(bool(np.nanmedian(e) > 0), f"{base} Dukascopy : spread d'époque mesuré "
                                                f"(médiane {np.nanmedian(e):.5g} en prix)")


def qc_echelle_drawdown() -> None:
    """L'échelle 6-4-3 du plan de Mongazi : plein tarif au sommet, moins en dessous, et retour."""
    from ..noyau import profils
    from ..noyau.config import ConfigDangereuse, charger
    cfg = charger(surcharges={"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 6.0})
    verifier(cfg.profil.paliers_drawdown == ((0.0, 6.0), (0.0001, 4.0), (0.2, 3.0)),
             f"l'échelle est lue depuis la configuration : {cfg.profil.paliers_drawdown}")
    etat = profils.initialiser("boost", 500.0)
    lu = []
    for equite in (500, 600, 590, 480, 420, 700):
        profils.maj_sommet(etat, equite)
        lu.append(round(profils.risque_courant(cfg, etat, equite)[0], 2))
    verifier(lu == [6.0, 6.0, 4.0, 3.0, 3.0, 6.0],
             f"6 % au sommet · 4 % sous le sommet · 3 % à -20 % · 6 % au nouveau sommet ({lu})")
    # TÉMOIN : sans mise à jour du sommet, l'échelle mesure le drawdown depuis le CAPITAL DE DÉPART
    # et pas depuis le sommet atteint. Après 500 → 600 → 480, elle lit -4 % au lieu de -20 % : elle
    # laisse donc 4 % de risque là où le plan en veut 3. C'est la panne silencieuse à attraper.
    fige = profils.initialiser("boost", 500.0)
    sans_maj = [round(profils.risque_courant(cfg, fige, e)[0], 2) for e in (600, 480)]
    verifier(sans_maj == [6.0, 4.0] and lu[3] == 3.0,
             f"TÉMOIN : sommet jamais mis à jour → 4 % là où le plan veut 3 % ({sans_maj} contre {lu[3]})")
    try:
        charger(surcharges={"profils.actif": "boost",
                            "profil_boost.paliers_drawdown": [[0.0, 3.0], [0.2, 6.0]]})
        verifier(False, "une échelle qui REMONTE le risque (martingale) doit être refusée")
    except ConfigDangereuse:
        verifier(True, "une échelle qui remonte le risque quand ça va mal est refusée (martingale)")
    verifier(profils.risque_courant(charger(), profils.initialiser("pro", 100.0), 50.0)[0]
             == charger().risque.risque_par_trade_pct,
             "TÉMOIN : sans échelle configurée, le risque reste celui du profil")


def qc_compte_suit_echelle() -> None:
    """Le simulateur de compte applique bien l'échelle, et ne change rien quand elle est absente."""
    from datetime import datetime, timedelta
    from ..noyau.risque import SpecsSymbole
    from .compte import TradeCompte, simuler_compte
    specs = SpecsSymbole(nom="NAS100", point=0.01, digits=2, volume_min=0.1, volume_max=100,
                         volume_step=0.1, valeur_tick=0.01, taille_tick=0.01, taille_contrat=1.0,
                         stops_level_points=150)
    t0 = datetime(2024, 1, 2, 10, 0)
    suite = [2.0, -1.0, -1.0, -1.0, -1.0, 2.0, 2.0]      # un sommet, une descente, une remontée
    def trades():
        return [TradeCompte(base="NAS100", entree=t0 + timedelta(hours=2 * k),
                            sortie=t0 + timedelta(hours=2 * k + 1), sens=1, R=r,
                            points_risque=1500, prix=20000.0) for k, r in enumerate(suite)]
    # ⚠️ Capital volontairement PETIT : à 50 000 $ le lot maximum du courtier plafonne les deux
    # plans au même endroit et ils rendent le même capital final — le témoin ne montrerait rien.
    echelle = ((0.0, 6.0), (0.0001, 4.0), (0.20, 3.0))
    avec = simuler_compte(trades(), {"NAS100": specs}, capital=5_000.0, risque_pct=6.0,
                          echelle_drawdown=echelle)
    risques = [round(t.risque_pct_applique, 2) for t in avec.pris]
    verifier(risques[0] == 6.0 and 4.0 in risques and min(risques) <= 4.0,
             f"le compte applique l'échelle trade par trade ({risques})")
    verifier(max(risques) <= 6.0, "le risque ne dépasse jamais le plein tarif")
    verifier(risques[-1] >= risques[-2], "le risque remonte quand le capital remonte")
    sans = simuler_compte(trades(), {"NAS100": specs}, capital=5_000.0, risque_pct=6.0)
    verifier(all(abs(t.risque_pct_applique - 6.0) < 1e-9 for t in sans.pris),
             "TÉMOIN : sans échelle, le risque reste fixe (aucune régression pour les autres appels)")
    verifier(sans.resume()["capital_final"] != avec.resume()["capital_final"],
             "TÉMOIN : les deux plans ne donnent pas le même capital final")


def qc_surprises() -> None:
    """Le signe des surprises doit être équilibré. Forex Factory code « pire » par 2, pas par -1 :
    lu tel quel, toutes les mauvaises surprises devenaient des bonnes, en double."""
    from . import annonces
    try:
        ts, signe, ampleur = annonces.surprises("EURUSD")
    except FileNotFoundError:
        print("  · annonces pas en cache, contrôles sautés")
        return
    verifier(len(ts) > 500, f"surprises chiffrées disponibles ({len(ts)})")
    mieux, pire = int((signe > 0).sum()), int((signe < 0).sum())
    verifier(mieux > 0 and pire > 0 and 0.5 < mieux / max(pire, 1) < 2.0,
             f"signe équilibré : {mieux} mieux que prévu, {pire} pire")
    verifier(set(np.unique(signe)) <= {-1.0, 0.0, 1.0}, "le signe ne vaut que -1, 0 ou +1")
    verifier(float(np.median(ampleur)) > 0 and float(np.max(ampleur)) <= 10.0,
             "l'ampleur relative est positive et bornée")
    verifier(abs(annonces._nombre("143K") - 143000) < 1e-6 and abs(annonces._nombre("0.4%") - 0.4) < 1e-9
             and np.isnan(annonces._nombre("")),
             "lecture des chiffres : « 143K » = 143 000, « 0,4 % » = 0,4, vide = inconnu")


def qc_masques_seance() -> None:
    """Les fenêtres sont en heure de New York, et la clôture forcée tombe avant le moment cher."""
    s = _serie(n=4000)
    minute, jour = intraday.minutes_et_jours(s.temps)
    entree = intraday.masque_entree("EURUSD", s.temps, minute=minute, jour=jour)
    fin = intraday.fin_de_journee("EURUSD", s.temps, minute=minute, jour=jour)
    verifier(not (entree & fin).any(), "aucune barre n'est à la fois ouverte à l'entrée et en clôture forcée")
    verifier(minute[entree].max() <= intraday.fenetres("EURUSD")[1],
             "la dernière entrée tombe avant la borne de la fenêtre")
    verifier(intraday.fenetres("EURUSD")[2] < 17 * 60,
             "EUR/USD : la clôture forcée précède le rollover de 17:00 New York")
    verifier(intraday.fenetres("NAS100")[2] < 16 * 60,
             "NAS100 : la clôture forcée précède la clôture cash de 16:00 New York")
    verifier(not fin[minute == 12 * 60].any(), "midi à New York n'est jamais une clôture forcée")


def qc_sortie_seance_compte_comme_echec() -> None:
    """Une sortie de fin de journée n'est PAS un objectif atteint : c'est tout l'enjeu du critère."""
    s = _serie(n=3000)
    stop = etiquettes.stops_points(s, 400)
    e = etiquettes.etiqueter(s, stop_dist=stop, sens=+1)
    v = e.valides()
    verifier((e.motif[v] == SEANCE).any(), "des trades se ferment bien par fin de journée")
    verifier(not (e.objectif() & (e.motif == SEANCE)).any(),
             "une sortie de fin de journée n'est jamais comptée comme objectif atteint")
    verifier(float((e.motif[v] == OBJECTIF).mean()) == e.taux_objectif(),
             "le taux d'objectif compte exactement les sorties par objectif")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n  QC · recherche sans fin\n")
    for f in (qc_etiquette_egale_simulateur, qc_aucune_nuit, qc_fuite_du_futur,
              qc_etiquette_ne_regarde_pas_apres, qc_point_mort, qc_scelle, qc_masques_seance,
              qc_sortie_seance_compte_comme_echec, qc_dukascopy, qc_surprises,
              qc_echelle_drawdown, qc_compte_suit_echelle):
        f()
    print(f"\n  {VERTS} verts · {ROUGES} rouges\n")
    return 0 if ROUGES == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
