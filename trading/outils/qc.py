# -*- coding: utf-8 -*-
"""
Contrôle qualité de NEBULA Trader. À passer VERT avant toute livraison.

    python -m trading.outils.qc

Aucun terminal MT5, aucun réseau, aucun compte : tout tourne dans un dossier de
données temporaire, avec un agent factice. Ce qui est contrôlé, c'est ce qui
protège l'argent : les refus du videur, le dimensionnement sur petit capital,
le compte cent, les modes d'exécution, la licence, le serveur local, et le fait
que l'agent ne devienne jamais plus risqué sur une phrase mal comprise.

⚠️ Chaque verrou a son TÉMOIN : on prouve qu'il laisse passer ce qui doit
passer avant de prouver qu'il refuse. Un verrou fermé pour toujours passerait
sinon tous les contrôles de refus avec les honneurs.
"""
from __future__ import annotations

import dataclasses
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TEMP = Path(tempfile.mkdtemp(prefix="nebula-qc-"))
os.environ["NEBULA_TRADER_DONNEES"] = str(TEMP)
for cle in [k for k in os.environ if k.startswith("MT5_")]:
    os.environ.pop(cle)
os.environ.pop("ANTHROPIC_API_KEY", None)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parents[2]
RESULTATS: list[tuple[bool, str]] = []


def verifier(condition, libelle: str, detail: str = "") -> None:
    RESULTATS.append((bool(condition), libelle))
    print(f"  {'✓' if condition else '✗'} {libelle}" + (f"  ({detail})" if detail and not condition else ""))


def section(titre: str) -> None:
    print(f"\n{titre}")


# =========================================================================== #
def qc_config():
    from trading.noyau.config import ConfigDangereuse, charger
    section("VIDEUR")
    cfg = charger()
    verifier(cfg.risque.risque_par_trade_pct == 1.0, "TÉMOIN : la configuration livrée se charge")
    dangers = {
        "risque 5 % en PRO": {"profil_pro.risque_par_trade_pct": 5.0},
        "risque 11 % en BOOST": {"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 11.0},
        "levier effectif x50": {"profils.actif": "boost", "profil_boost.levier_effectif_max": 50.0},
        "paliers qui remontent (martingale)": {"profils.actif": "boost", "profil_boost.paliers": [1.0, 3.0]},
        "profil inconnu": {"profils.actif": "casino"},
        "martingale autorisée": {"coupe_circuits.interdit_martingale": False},
        "grille autorisée": {"coupe_circuits.interdit_grille": False},
        "stop élargissable": {"discipline.stop_jamais_elargi": False},
        "sans stop côté serveur": {"execution.stops_cote_serveur_obligatoire": False},
        "apprentissage en direct": {"apprentissage.apprentissage_en_ligne": True},
        "escalier des disjoncteurs inversé": {"profil_pro.perte_max_jour_pct": 8.0},
        "drawdown total 40 %": {"coupe_circuits.drawdown_max_total_pct": 40.0},
        "petit compte à 3 %": {"risque_position.risque_max_petit_compte_pct": 3.0},
        "réel sans plafond de capital": {"compte.mode": "reel"},
    }
    for nom, s in dangers.items():
        try:
            charger(surcharges=s)
            verifier(False, f"refuse : {nom}")
        except ConfigDangereuse:
            verifier(True, f"refuse : {nom}")
    b = charger(surcharges={"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 10.0})
    c = b.circuits
    verifier(b.risque.risque_par_trade_pct == 10.0
             and c.perte_max_jour_pct <= c.perte_max_semaine_pct <= c.perte_max_mois_pct <= c.drawdown_max_total_pct <= 35
             and c.perte_max_jour_pct >= 10.0,
             "TÉMOIN : BOOST 10 % accepté, disjoncteurs recalculés en escalier cohérent",
             f"{c.perte_max_jour_pct}/{c.perte_max_semaine_pct}/{c.perte_max_mois_pct}/{c.drawdown_max_total_pct}")
    try:
        charger(surcharges={"compte.mode": "reel", "compte.capital_max_engage": 200.0})
        verifier(True, "TÉMOIN : réel accepté avec un plafond de capital")
    except ConfigDangereuse as e:
        verifier(False, "TÉMOIN : réel accepté avec un plafond de capital", str(e)[:120])


def qc_dimensionnement():
    from trading.noyau.risque import SpecsSymbole, deplacement_de_stop_autorise, dimensionner
    section("DIMENSIONNEMENT ET PETIT CAPITAL")
    eurusd = SpecsSymbole(nom="EURUSD", point=1e-5, digits=5, volume_min=0.01, volume_max=20,
                          volume_step=0.01, valeur_tick=1.0, taille_tick=1e-5,
                          taille_contrat=100000, stops_level_points=20)
    d = dimensionner(capital=10000, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                     lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
    verifier(d.autorise and d.risque_pct <= 1.0 and not d.note,
             "TÉMOIN : 10 000 $ trade à 1 % exact, sans note", str(d))
    d = dimensionner(capital=500, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                     lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
    verifier(d.autorise and d.lots == 0.01 and 1.0 < d.risque_pct <= 2.0 and d.note,
             "500 $ : lot minimum accepté sous le plafond, et c'est écrit", str(d))
    d = dimensionner(capital=500, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                     lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=1.0)
    verifier(not d.autorise, "500 $ en refus strict (plafond = risque) : refusé")
    d = dimensionner(capital=100, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                     lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
    verifier(not d.autorise and d.capital_requis > 100,
             "100 $ standard : refusé, capital requis annoncé", f"{d.capital_requis:.0f}")
    d = dimensionner(capital=1000 * 1.0 * 1 * 1, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                     lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
    cent = dimensionner(capital=10 * 100, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                        lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
    verifier(cent.autorise and cent.risque_pct <= 1.0,
             "10 $ sur compte cent (1 000 USC) : trade à 1 % exact", str(cent))
    for capital in (50, 250, 700, 5000):
        dd = dimensionner(capital=capital, risque_pct=1.0, points_de_risque=527, specs=eurusd,
                          lots_total_max=0.5, perte_max_par_position_pct=3.0, risque_pct_plafond=2.0)
        if dd.autorise and dd.risque_pct > 2.0 + 1e-9:
            verifier(False, f"jamais au-dessus du plafond ({capital} $)", str(dd))
            break
    else:
        verifier(True, "jamais au-dessus du plafond de 2 %, quel que soit le capital")
    ok, _ = deplacement_de_stop_autorise(sens="achat", stop_actuel=1.08, stop_propose=1.081)
    ko, _ = deplacement_de_stop_autorise(sens="achat", stop_actuel=1.08, stop_propose=1.079)
    verifier(ok and not ko, "stop : resserré accepté (témoin), élargi refusé")


def qc_capital():
    from trading.noyau.capital import capital_de_travail, detecter
    section("TYPE DE COMPTE")
    usc, usd = detecter("USC"), detecter("USD", "Deriv-Demo")
    verifier(usc.cent and usc.facteur == 100 and usc.devise_reelle == "USD", "USC reconnu comme compte cent")
    verifier(not usd.cent, "TÉMOIN : USD reste un compte standard")
    verifier(capital_de_travail(1_000_000, 50, usc) == 5000,
             "plafond de 50 $ converti en 5 000 USC sur compte cent")
    verifier(capital_de_travail(10_000, 0, usd) == 10_000, "plafond 0 = solde entier")


def qc_licence():
    from trading.noyau.licence import signer, verifier as verifier_licence
    section("LICENCE")
    cle_privee = RACINE / "secrets" / "nebula-trader-licence.pem"
    if not cle_privee.exists():
        verifier(True, "clé privée absente sur cette machine : émission non testée")
        return
    k = signer({"nom": "QC", "email": "qc@x", "edition": "pro", "expire": "2099-01-01", "id": "qc"},
               cle_privee.read_bytes())
    verifier(verifier_licence(k).valide, "TÉMOIN : une clé émise est valide")
    corps = k.split(".")
    falsifiee = f"{corps[0]}.{corps[1][:-3]}AAA.{corps[2]}"
    verifier(not verifier_licence(falsifiee).valide, "clé modifiée : signature refusée")
    k2 = signer({"nom": "QC", "expire": "2020-01-01", "id": "qc2"}, cle_privee.read_bytes())
    verifier(not verifier_licence(k2).valide, "clé expirée refusée")
    verifier(not verifier_licence("").valide, "pas de clé : évaluation")


def qc_reglages():
    from trading.live.journal import Journal
    from trading.noyau import reglages
    section("RÉGLAGES DEPUIS L'INTERFACE")
    j = Journal(TEMP / "qc_reglages.db")
    r = reglages.modifier({"profil_pro.risque_par_trade_pct": 0.5}, journal=j)
    verifier(r["ok"] and reglages.config_effective().risque.risque_par_trade_pct == 0.5,
             "TÉMOIN : baisser le risque à 0,5 % est appliqué")
    verifier(j.historique_reglages()[0]["apres"] == "0.5", "le changement est journalisé")
    r = reglages.modifier({"profil_pro.risque_par_trade_pct": 5})
    verifier(not r["ok"] and reglages.config_effective().risque.risque_par_trade_pct == 0.5,
             "risque 5 % refusé et rien n'est enregistré")
    r = reglages.modifier({"coupe_circuits.interdit_martingale": False})
    verifier(not r["ok"], "une protection verrouillée n'est pas modifiable")
    r = reglages.modifier({"profil_pro.perte_max_jour_pct": 8})
    verifier(not r["ok"] and "escalier" in " ".join(r["erreurs"]), "le videur tranche aussi les surcharges")
    r = reglages.modifier({"profil_pro.perte_max_jour_pct": 4}, drawdown_pct=6.0)
    verifier(r["ok"] and r["alertes"], "relever un risque en drawdown déclenche une alerte")
    reglages.reinitialiser()
    verifier(reglages.config_effective().risque.risque_par_trade_pct == 1.0, "retour aux valeurs du fichier")


def qc_profils():
    import numpy as np
    from trading.noyau import profils
    from trading.noyau.config import charger
    from trading.noyau.risque import SpecsSymbole, dimensionner
    section("PROFILS PRO / BOOST")
    pro = charger()
    b10 = charger(surcharges={"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 10.0})
    b3 = charger(surcharges={"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 3.0})
    e = profils.initialiser("boost", 1000)
    verifier(profils.risque_courant(b10, e, 1000)[0] == 10.0, "TÉMOIN : au départ, BOOST risque ce qui a été choisi")
    r2, note = profils.risque_courant(b10, e, 2100)
    verifier(r2 == 5.0 and note, "capital ×2 : le risque descend d'un palier (10 → 5 %) et le dit", str((r2, note)))
    verifier(profils.risque_courant(b10, e, 16500)[0] == 1.5,
             "capital ×16 : quatre paliers plus bas (10 → 5 → 3 → 2 → 1,5 %)")
    verifier(profils.risque_courant(b10, e, 600)[0] == 10.0,
             "capital sous le départ : le risque ne REMONTE jamais au-dessus du choix")
    verifier(profils.echelle(3.0, b3.profil.paliers) == [3.0, 2.0, 1.5, 1.0],
             "à 3 %, l'échelle ne contient que des paliers inférieurs")
    ep = profils.initialiser("pro", 1000)
    verifier(profils.risque_courant(pro, ep, 5000)[0] == pro.risque.risque_par_trade_pct,
             "TÉMOIN : en PRO, aucun palier ne s'applique")
    poche = profils.initialiser("boost", 1000)
    verifier(profils.mettre_a_l_abri(b10, poche, 1400) == 0, "TÉMOIN : à +40 %, rien n'est mis à l'abri")
    part = profils.mettre_a_l_abri(b10, poche, 1500)
    verifier(abs(part - 125) < 1e-6 and profils.capital_disponible(1500, poche) == 1375,
             "à +50 %, 25 % du gain sort du capital de travail (125 sur 500)", str(part))
    verifier(profils.mettre_a_l_abri(b10, poche, 1500) == 0, "la même poche n'est pas prise deux fois")
    verifier(profils.mettre_a_l_abri(pro, profils.initialiser("pro", 1000), 5000) == 0,
             "TÉMOIN : en PRO, pas de poche")

    eurusd = SpecsSymbole(nom="EURUSD", point=1e-5, digits=5, volume_min=0.01, volume_max=20,
                          volume_step=0.01, valeur_tick=1.0, taille_tick=1e-5, taille_contrat=100000)
    libre = dimensionner(capital=10000, risque_pct=10.0, points_de_risque=527, specs=eurusd,
                         lots_total_max=20, perte_max_par_position_pct=15.0, prix=1.16, levier_max=30.0)
    borne = dimensionner(capital=10000, risque_pct=10.0, points_de_risque=527, specs=eurusd,
                         lots_total_max=20, perte_max_par_position_pct=15.0, prix=1.16, levier_max=5.0)
    verifier(libre.autorise and libre.levier > 5 and "levier" not in libre.note,
             "TÉMOIN : à 10 % et plafond x30, taille pleine", f"x{libre.levier:.1f}")
    verifier(borne.autorise and borne.levier <= 5.0 + 1e-9 and borne.lots < libre.lots and "levier" in borne.note,
             "plafond x5 : taille réduite (risque plus bas), jamais au-dessus du plafond", f"x{borne.levier:.1f}")
    # 500 $ : le capital suffit pour le lot minimum, seul le levier peut refuser.
    refus = dimensionner(capital=500, risque_pct=10.0, points_de_risque=527, specs=eurusd,
                         lots_total_max=20, perte_max_par_position_pct=15.0, prix=1.16, levier_max=1.0)
    verifier(not refus.autorise and "levier" in refus.raison, "même le lot minimum au-delà du levier : refus")

    from trading.backtest.couts import ModeleCouts
    from trading.backtest.moteur import Moteur
    from trading.outils.essai_moteur import barres_synthetiques
    from trading.strategies.cassure_donchian import CassureDonchian
    import dataclasses as dc
    b5 = charger(surcharges={"profils.actif": "boost", "profil_boost.risque_par_trade_pct": 5.0})
    b5 = dc.replace(b5, calendrier=dc.replace(b5.calendrier, fermer_avant_weekend=False))
    res = Moteur(b5, eurusd, ModeleCouts(spread_points=15, slippage_points=5), CassureDonchian()) \
        .lancer(barres_synthetiques(6000), 10000)
    verifier(len(res.trades) > 5, "TÉMOIN : le moteur trade en BOOST", str(len(res.trades)))
    pires = [t.resultat_R for t in res.trades]
    verifier(min(pires) > -1.6, "en BOOST, aucune perte au-delà du stop (hors gap et coûts)", f"{min(pires):.2f} R")


def qc_montecarlo():
    import numpy as np
    from trading.backtest import montecarlo
    section("MONTE CARLO")
    rng = np.random.default_rng(3)
    R = np.where(rng.random(400) < 0.4, 2.0, -1.0)          # 40 % à +2 R : espérance +0,2 R
    a = montecarlo.simuler(R, risque_pct=2, n_trades=60)
    b = montecarlo.simuler(R, risque_pct=2, n_trades=60)
    verifier(a == b, "même graine, même résultat (reproductible)")
    probs = [montecarlo.simuler(R, risque_pct=r, n_trades=60)["p_drawdown"]["20"] for r in (1, 3, 10)]
    verifier(probs[0] <= probs[1] <= probs[2] and probs[2] > probs[0],
             "TÉMOIN d'instrument : plus de risque, plus de chances de perdre 20 % (monotone)", str(probs))
    c1 = montecarlo.seuil_arret_calibre(R, risque_pct=1, trades_par_an=28)
    c10 = montecarlo.seuil_arret_calibre(R, risque_pct=10, trades_par_an=28)
    verifier(c1["valide"] and c1["seuil_pct"] >= c1["p99"] and not c1["plafonne"],
             "arrêt calibré à 1 % : au-delà du p99, non plafonné", str(c1.get("seuil_pct")))
    verifier(c10["seuil_pct"] == 35.0 and c10["plafonne"], "à 10 % : plafonné à 35 % et signalé")
    verifier(not montecarlo.simuler(R[:5], risque_pct=1, n_trades=30)["valide"],
             "moins de 10 trades : le Monte Carlo refuse de conclure")
    rapport = {"capital_initial": 10000, "courbe_equite": [["t1", 10100.0], ["t2", 10049.5]]}
    rr = montecarlo.rendements_en_R(rapport)
    verifier(np.allclose(rr, [1.0, -0.5]), "R retrouvés depuis une courbe d'équité (anciens rapports)", str(rr))


def qc_surveillance():
    import sqlite3
    import numpy as np
    from trading.apprentissage import analyse, porte, sante
    from trading.live.journal import Journal
    section("AUTO-SURVEILLANCE, PORTES, CHIEN DE GARDE")
    rng = np.random.default_rng(9)
    ref = np.where(rng.random(400) < 0.4, 2.0, -1.0)
    verifier(sante.diagnostiquer([], ref, cle="qc")["statut"] == "saine", "aucun trade réel : stratégie saine")
    fausses = sum(sante.diagnostiquer(ref[rng.integers(0, 400, 100)], ref, cle="qc")["statut"] == "pause"
                  for _ in range(100))
    verifier(fausses <= 10, "TÉMOIN : une stratégie conforme à sa mesure n'est presque jamais mise en pause",
             f"{fausses}/100")
    morte = ref[rng.integers(0, 400, 80)] - 1.0
    verifier(sante.diagnostiquer(morte, ref, cle="qc")["statut"] == "pause",
             "un avantage effondré (−1 R) est mis en pause")
    verifier(sante.diagnostiquer([0.5], ref[:10], cle="qc2")["statut"] == "inconnu",
             "sans référence walk-forward suffisante : statut inconnu, pas de verdict")

    j = Journal(TEMP / "qc_surveillance.db")
    vide = analyse.analyser(j)
    verifier(vide["global"]["trades"] == 0 and "Aucun trade" in vide["constats"][0],
             "auto-analyse sur un journal vide : le dit, ne conclut rien")
    verifier(not porte.porte_demo(j)["franchie"], "porte démo fermée sans historique")
    verifier(not porte.porte_boost_reel(j)["franchie"], "porte BOOST réel fermée sans PRO réel")

    cx = sqlite3.connect(j.chemin)
    from datetime import datetime, timedelta, timezone
    debut = datetime.now(timezone.utc) - timedelta(days=40)
    for k in range(32):
        ouvert = (debut + timedelta(days=k)).isoformat()
        ferme = (debut + timedelta(days=k, hours=8)).isoformat()
        gain = k % 5 < 2
        cx.execute("INSERT INTO trades (ticket, strategie, sens, lots, ouvert_le, prix_entree, stop_initial, "
                   "objectif, risque_devise, ferme_le, prix_sortie, resultat_devise, resultat_R, motif, contexte, "
                   "mode, symbole, profil) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (1000 + k, "cassure_donchian", "achat", 0.1, ouvert, 1.1, 1.095, 1.11, 50, ferme,
                    1.11 if gain else 1.095, 100 if gain else -50, 2.0 if gain else -1.0,
                    "objectif" if gain else "stop", '{"efficacite": 0.4}', "demo", "EURUSD", "pro"))
        cx.execute("INSERT INTO ordres (ts, action, ticket, sens, lots, prix, sl, tp, retcode, mode, "
                   "prix_demande, glissement_points) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                   (ouvert, "ouvrir", 1000 + k, "achat", 0.1, 1.1, 1.095, 1.11, 10009, "demo", 1.1, 0.5))
    cx.commit()
    ok = porte.porte_demo(j, sante={"statut": "saine"})
    verifier(ok["franchie"], "TÉMOIN : 40 jours, 32 trades, stops posés, glissement 0,5 pt : porte démo franchie",
             str([c for c in ok["criteres"] if not c["ok"]]))
    verifier(not porte.porte_demo(j, sante={"statut": "pause"})["franchie"],
             "stratégie en pause de santé : porte démo refermée")
    cx.execute("INSERT INTO ordres (ts, action, ticket, retcode, mode, sl) VALUES (?,?,?,?,?,?)",
               (datetime.now(timezone.utc).isoformat(), "ouvrir", 9999, 10009, "demo", 0))
    cx.commit()
    verifier(not porte.porte_demo(j, sante={"statut": "saine"})["franchie"],
             "un seul ordre parti sans stop : porte démo refermée")
    cx.close()
    a = analyse.analyser(j)
    verifier(a["par_regime"]["tendance"]["trades"] == 32 and a["par_regime"]["tendance"]["concluant"],
             "analyse par régime avec effectif, concluante à partir de 20 trades")
    verifier(all(not v["concluant"] for v in a["par_jour"].values()),
             "tranches par jour de moins de 20 trades marquées non concluantes")

    from trading.live.agent import Agent
    from trading.noyau.config import charger

    class ExecFactice:
        def __init__(self):
            self.poses, self.fermees = [], []

        def poser_stop(self, pos, sl, digits):
            from trading.live.execution import ResultatOrdre
            self.poses.append((pos.ticket, sl))
            return ResultatOrdre(True, ticket=pos.ticket, sl=sl)

        def fermer(self, pos, motif=""):
            from trading.live.execution import ResultatOrdre
            self.fermees.append(pos.ticket)
            return ResultatOrdre(True, ticket=pos.ticket)

    class Pos:
        def __init__(self, ticket, sl):
            self.ticket, self.sl, self.tp = ticket, sl, 0.0

    class Compte:
        equity = 10000.0

    cfg = charger()
    jg = Journal(TEMP / "qc_garde.db")
    ag = Agent(jg)
    # L'instantané publié à chaque cycle : ce chemin n'était exercé par aucun contrôle,
    # et un attribut renommé l'a fait planter en direct (vu dans le journal, QC vert).
    from trading.noyau import reglages as _r
    try:
        ag._publier(cfg, _r.agent(), None, [])
        inst = ag.instantane()
        verifier("profil" in inst and "portes" in inst and "sante" in inst,
                 "l'instantané de l'agent se publie sans compte connecté")
    except Exception as exc:                                          # noqa: BLE001
        verifier(False, "l'instantané de l'agent se publie sans compte connecté", repr(exc))
    ag.executeur, ag.specs = ExecFactice(), type("S", (), {"digits": 5})()
    for _ in range(2):
        jg.ordre(action="ouvrir", retcode=10019, mode="demo")
    ag._chien_de_garde(cfg, Compte(), [])
    verifier(not ag.pause_motif, "TÉMOIN : deux ordres rejetés ne mettent pas en pause")
    jg.ordre(action="ouvrir", retcode=10019, mode="demo")
    ag._chien_de_garde(cfg, Compte(), [])
    verifier("rejet" in ag.pause_motif, "trois ordres rejetés en une heure : plus aucune entrée", ag.pause_motif)
    ag.pause_motif = ""
    ag._chien_de_garde(cfg, Compte(), [Pos(7, 1.09)])
    verifier(not ag.executeur.poses, "TÉMOIN : une position avec stop n'est pas touchée")
    ag._chien_de_garde(cfg, Compte(), [Pos(8, 0.0)])
    verifier(ag.executeur.fermees == [8], "position sans stop et sans stop connu : fermée")
    # Journal NEUF : l'ancien porte encore les 3 rejets, qui mettraient en pause
    # avant la règle mesurée ici (un contrôle hérite de l'état du précédent).
    jc = Journal(TEMP / "qc_garde_equite.db")
    ag = Agent(jc)
    ag.executeur, ag.specs = ExecFactice(), type("S", (), {"digits": 5})()
    jc.point_equite(10000, 10000, 10000)

    class CompteChute:
        equity = 9500.0

    ag._chien_de_garde(cfg, Compte(), [])
    verifier(not ag.pause_motif, "TÉMOIN : équité stable, pas de pause")
    ag._chien_de_garde(cfg, CompteChute(), [])
    verifier("équité" in ag.pause_motif, "équité −5 % en une heure : pause", ag.pause_motif)


def qc_execution():
    from trading.live.execution import autorisation
    section("MODES D'EXÉCUTION")
    base = dict(mode_config="reel", capital_max_engage=200, licence_valide=True, porte_demo_franchie=True)
    verifier(not autorisation("observation", compte_demo=True, **base)[0], "observation : aucun ordre")
    verifier(autorisation("demo", compte_demo=True, **base)[0], "TÉMOIN : démo sur compte démo autorisée")
    verifier(not autorisation("demo", compte_demo=False, **base)[0], "démo branchée sur un compte réel : refus")
    verifier(autorisation("reel", compte_demo=False, **base)[0], "TÉMOIN : réel complet autorisé")
    verifier(not autorisation("reel", compte_demo=False, **{**base, "licence_valide": False})[0],
             "réel sans licence : refus")
    verifier(not autorisation("reel", compte_demo=False, **{**base, "porte_demo_franchie": False})[0],
             "réel sans porte démo franchie : refus")
    verifier(not autorisation("reel", compte_demo=False, **{**base, "capital_max_engage": 0})[0],
             "réel sans plafond de capital : refus")
    verifier(not autorisation("reel", compte_demo=True, **base)[0], "réel sur un compte démo : refus")
    verifier(not autorisation("reel", compte_demo=False, profil_boost=True, **base)[0],
             "BOOST en réel sans 60 jours de PRO rentable : refus")
    verifier(autorisation("reel", compte_demo=False, profil_boost=True, porte_boost_franchie=True, **base)[0],
             "TÉMOIN : BOOST en réel, porte franchie : autorisé")
    verifier(autorisation("demo", compte_demo=True, profil_boost=True, **base)[0],
             "BOOST en démo : libre")


def qc_journal():
    from trading.live.journal import Journal
    from trading.noyau.plan import ACHAT, PlanDeTrade
    section("JOURNAL")
    j = Journal(TEMP / "qc_journal.db")
    plan = PlanDeTrade(symbole="EURUSD", sens=ACHAT, entree=1.1, stop=1.095, objectif=1.11,
                       these="Cassure du couloir de vingt barres dans le sens de la tendance.",
                       atr=0.0025, horodatage=datetime.now(), strategie="qc")
    j.ouvrir_trade(ticket=1, plan=plan, lots=0.1, prix=1.1, risque_devise=50.0, mode="demo")
    j.fermer_trade(ticket=1, prix=1.095, resultat=-50.0, motif="stop")
    j.ouvrir_trade(ticket=2, plan=plan, lots=0.1, prix=1.1, risque_devise=50.0, mode="demo")
    j.fermer_trade(ticket=2, prix=1.095, resultat=-49.0, motif="stop")
    t = j.trade_par_ticket(1)
    verifier(abs(t["resultat_R"] + 1.0) < 1e-9, "résultat en R calculé depuis le risque d'entrée")
    verifier(j.serie_perdante()[0] == 2, "série perdante comptée")
    j.ouvrir_trade(ticket=3, plan=plan, lots=0.1, prix=1.1, risque_devise=50.0, mode="demo")
    j.fermer_trade(ticket=3, prix=1.11, resultat=100.0, motif="objectif")
    verifier(j.serie_perdante()[0] == 0, "TÉMOIN : un gain remet la série à zéro")
    s = j.statistiques()
    verifier(s["trades"] == 3 and s["gagnants"] == 1, "statistiques cohérentes", str(s))
    p1 = j.point_equite(1000, 1000, 1000)
    import time as _t
    _t.sleep(1.1)                       # la clé de la table est la seconde
    p2 = j.point_equite(900, 900, 900)
    verifier(p1["drawdown_pct"] == 0, "TÉMOIN : au sommet, drawdown nul")
    verifier(abs(p2["drawdown_pct"] - 10) < 1e-6, "drawdown mesuré depuis le sommet",
             str(p2["drawdown_pct"]))


class AgentFactice:
    def __init__(self):
        self.commandes = []

    def instantane(self):
        return {"connexion": {"ok": True, "message": "connecté (factice)"}, "mode": "observation",
                "positions": [], "pause": "", "prochaine_bougie": "2026-09-16T16:00:00",
                "risque": {"pnl_jour_pct": -0.5, "drawdown_pct": 1.2, "pertes_consecutives": 1,
                           "limites": {"risque_par_trade_pct": 1.0, "risque_max_petit_compte_pct": 2.0,
                                       "perte_max_jour_pct": 3.0, "drawdown_max_total_pct": 20.0}},
                "compte": {"solde": 1000.0, "devise": "USD"}}

    def commander(self, action, valeur=None, auteur="?"):
        self.commandes.append((action, valeur))


def qc_conversation():
    from trading.interface.chat import Assistant
    from trading.live.journal import Journal
    section("CONVERSATION (sans clé API)")
    agent = AgentFactice()
    a = Assistant(agent, Journal(TEMP / "qc_chat.db"))
    a.parler("c'est quoi mon stop ?")
    verifier(not any(c[0] == "pause" for c in agent.commandes), "« mon stop » ne met PAS en pause")
    a.parler("mets-toi en pause")
    verifier(any(c[0] == "pause" for c in agent.commandes), "TÉMOIN : « mets-toi en pause » met en pause")
    r = a.parler("arrêt d'urgence, ferme tout")
    verifier(not any(c[0] == "urgence" for c in agent.commandes) and r["propositions"],
             "l'urgence devient une PROPOSITION, rien ne se ferme sur une phrase")
    pid = r["propositions"][0]["id"]
    a.repondre_proposition(pid, True)
    verifier(any(c[0] == "urgence" for c in agent.commandes), "confirmée, l'urgence est exécutée")
    res = a._modifier({"profil_pro.risque_par_trade_pct": 1.8}, "test")
    verifier(res["proposition"] and not res["appliques"], "relever le risque passe par une proposition")
    res = a._modifier({"profil_pro.risque_par_trade_pct": 0.5}, "test")
    verifier(res["appliques"] and res["appliques"]["ok"], "TÉMOIN : baisser le risque s'applique seul")
    from trading.noyau import reglages
    reglages.reinitialiser()
    r = a.parler("quel est mon risque ?")
    verifier("1,0 %" in r["reponse"] and "." not in r["reponse"].split("%")[0][-4:],
             "chiffres au format français", r["reponse"][:80])


def qc_serveur():
    from fastapi.testclient import TestClient
    from trading.interface.chat import Assistant
    from trading.interface.serveur import creer_app
    from trading.live.journal import Journal
    section("SERVEUR LOCAL")
    agent, journal = AgentFactice(), Journal(TEMP / "qc_serveur.db")
    app = creer_app(agent, journal, Assistant(agent, journal), port=8765)
    c = TestClient(app, base_url="http://127.0.0.1:8765")
    page = c.get("/")
    verifier(page.status_code == 200 and 'name="jeton"' in page.text, "TÉMOIN : la page se sert avec son jeton")
    jeton = page.text.split('name="jeton" content="')[1].split('"')[0]
    H = {"X-Jeton": jeton}
    verifier(TestClient(app, base_url="http://evil.example").get("/api/etat").status_code == 403,
             "hôte étranger refusé (DNS rebinding)")
    verifier(c.post("/api/commande", json={"action": "pause"}).status_code == 403,
             "action sans jeton refusée")
    verifier(c.post("/api/commande", json={"action": "pause"}, headers=H).status_code == 200,
             "TÉMOIN : action avec jeton acceptée")
    verifier(c.get("/api/etat").json()["connexion"]["ok"], "état lisible")
    r = c.post("/api/reglages", json={"changements": {"risque_position.risque_par_trade_pct": 5}}, headers=H).json()
    verifier(not r["ok"], "réglage dangereux refusé par l'API")
    verifier(c.post("/api/commande", json={"action": "urgence"}, headers=H).status_code == 400,
             "urgence non confirmée refusée")
    r = c.post("/api/commande", json={"action": "mode", "valeur": "reel", "confirme": True}, headers=H).json()
    verifier(r.get("ok") is False and "licence" in r.get("erreur", ""), "mode réel sans licence refusé")
    verifier(c.post("/api/commande", json={"action": "mode", "valeur": "demo"}, headers=H).status_code == 400,
             "passage en démo non confirmé refusé")
    rep = c.get("/api/reglages").json()
    verifier(not any(x.get("cache") for x in rep["reglages"]), "le mode du compte n'est pas un champ de formulaire")
    verifier(c.get("/statique/app.js").status_code == 200, "script de l'interface servi")
    verifier(c.post("/api/profil", json={"actif": "boost", "risque": 8}, headers=H).status_code == 400,
             "BOOST non confirmé refusé")
    r = c.post("/api/profil", json={"actif": "boost", "risque": 8, "confirme": True}, headers=H).json()
    prof = c.get("/api/profil").json()
    verifier(r.get("ok") and prof["actif"] == "boost" and prof["effectif"]["risque_pct"] == 8.0,
             "TÉMOIN : BOOST confirmé à 8 % appliqué", str(prof.get("effectif")))
    mc = c.get("/api/montecarlo?risque=8").json()
    verifier(mc.get("valide") and 0 <= mc["p_drawdown"]["50"] <= 1, "probabilités de perte servies au curseur",
             str(mc.get("raison", "")))
    ev = c.get("/api/evolution").json()
    verifier({"total", "semaine", "sante", "portes", "trades"} <= set(ev), "page Évolution servie")
    verifier(c.post("/api/commande", json={"action": "reprendre_strategie", "valeur": "cassure_donchian"},
                    headers=H).status_code == 400, "reprise d'une stratégie en pause : confirmation exigée")
    r = c.post("/api/profil", json={"actif": "pro"}, headers=H).json()
    verifier(r.get("ok") and c.get("/api/profil").json()["actif"] == "pro", "retour en PRO sans confirmation")
    verifier(c.get("/api/etat").headers.get("x-frame-options") == "SAMEORIGIN",
             "interface non encadrable par un site tiers")


def qc_calendrier():
    from trading.noyau.calendrier import Calendrier, verrou_annonces
    section("CALENDRIER ÉCONOMIQUE")
    q = datetime(2026, 9, 16, 18, 0, tzinfo=timezone.utc)
    (TEMP / "calendrier.json").write_text(json.dumps({"telecharge_le": __import__("time").time(), "evenements": [
        {"title": "FOMC Statement", "country": "USD", "date": "2026-09-16T14:00:00-04:00", "impact": "High"},
        {"title": "Petit indice", "country": "USD", "date": "2026-09-16T10:00:00-04:00", "impact": "Low"},
    ]}), encoding="utf-8")
    cal = Calendrier(avant_min=30, apres_min=15, decalage_serveur_h=3)
    cal.rafraichir()
    bloque, quoi = cal((q + timedelta(hours=3) - timedelta(minutes=10)).replace(tzinfo=None))
    verifier(bloque and "FOMC" in quoi, "10 min avant le FOMC (serveur UTC+3) : blackout")
    libre, _ = cal((q + timedelta(hours=3) + timedelta(hours=2)).replace(tzinfo=None))
    verifier(not libre, "TÉMOIN : deux heures après, marché libre")
    petit, _ = cal(datetime(2026, 9, 16, 17, 0))
    verifier(not petit, "un indice à faible impact ne bloque rien")
    # Flux injoignable (port local fermé, aucun appel vers l'extérieur) et aucun
    # cache : le verrou doit REFUSER. Ne pas savoir n'est pas savoir qu'il n'y a rien.
    (TEMP / "calendrier.json").unlink()
    vide = Calendrier()
    vide.url = "http://127.0.0.1:9/injoignable.json"
    bloque, quoi = verrou_annonces(vide)(datetime(2026, 9, 16, 12, 0))
    verifier(bloque and "indisponible" in quoi, "calendrier indisponible : on s'abstient", quoi)


def qc_moteur():
    from trading.backtest.couts import ModeleCouts
    from trading.backtest.moteur import Moteur
    from trading.noyau.config import charger
    from trading.noyau.risque import SpecsSymbole
    from trading.outils.essai_moteur import barres_synthetiques
    from trading.strategies.cassure_donchian import CassureDonchian
    section("MOTEUR DE BACKTEST")
    cfg = charger()
    specs = SpecsSymbole(nom="EURUSD", point=1e-5, digits=5, volume_min=0.01, volume_max=100,
                         volume_step=0.01, valeur_tick=1.0, taille_tick=1e-5, taille_contrat=100000)
    # Les barres synthétiques déclarent 15 points de spread : facturer 3 ferait
    # juger le marché « anormal » (5 fois son spread habituel) et tout refuser.
    couts = ModeleCouts(spread_points=15, slippage_points=5)
    b = barres_synthetiques(6000)
    avec = dataclasses.replace(cfg, calendrier=dataclasses.replace(cfg.calendrier, fermer_avant_weekend=True))
    sans = dataclasses.replace(cfg, calendrier=dataclasses.replace(cfg.calendrier, fermer_avant_weekend=False))
    r1 = Moteur(avec, specs, couts, CassureDonchian()).lancer(b, 10000)
    r2 = Moteur(sans, specs, couts, CassureDonchian()).lancer(b, 10000)
    verifier(len(r1.trades) > 10, "TÉMOIN : le moteur trade sur données synthétiques", str(len(r1.trades)))
    verifier(any(t.motif_sortie == "week-end" for t in r1.trades),
             "fermeture du vendredi effective en H4 (elle ne se déclenchait jamais)")
    verifier(not any(t.motif_sortie == "week-end" for t in r2.trades), "désactivée, elle ne ferme rien")
    asie = sum(1 for t in r1.trades if t.entree_le.hour < 6)
    verifier(asie == 0, "aucune entrée pendant les heures creuses d'Asie (heure d'entrée réelle)", str(asie))


def qc_interface():
    section("INTERFACE")
    js = RACINE / "trading" / "interface" / "statique" / "app.js"
    node = shutil.which("node")
    if node:
        r = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
        verifier(r.returncode == 0, "app.js syntaxiquement valide", r.stderr[:200])
    texte = js.read_text(encoding="utf-8")
    verifier("const lignes = esc(texte).split" in texte,
             "la réponse de l'agent est échappée AVANT la mise en forme")
    verifier("t.textContent = texte" in texte, "les notifications s'écrivent en texte, jamais en HTML")
    css = (RACINE / "trading" / "interface" / "statique" / "app.css").read_text(encoding="utf-8")
    verifier("[hidden] { display: none !important; }" in css, "l'attribut hidden l'emporte sur les display")
    verifier("prefers-reduced-motion" in css, "mouvement réduit respecté")


def main() -> int:
    print("=" * 64)
    print("  QC NEBULA TRADER")
    print("=" * 64)
    for f in (qc_config, qc_dimensionnement, qc_capital, qc_licence, qc_reglages, qc_profils,
              qc_montecarlo, qc_surveillance, qc_execution,
              qc_journal, qc_conversation, qc_serveur, qc_calendrier, qc_moteur, qc_interface):
        try:
            f()
        except Exception as exc:                                  # noqa: BLE001
            import traceback
            verifier(False, f"{f.__name__} a planté", f"{exc.__class__.__name__}: {exc}")
            traceback.print_exc()
    ok = sum(1 for r in RESULTATS if r[0])
    ko = [lib for good, lib in RESULTATS if not good]
    print("\n" + "=" * 64)
    print(f"  {ok} verts · {len(ko)} rouges")
    for lib in ko:
        print(f"    ✗ {lib}")
    print("=" * 64)
    shutil.rmtree(TEMP, ignore_errors=True)
    return 0 if not ko else 1


if __name__ == "__main__":
    sys.exit(main())
