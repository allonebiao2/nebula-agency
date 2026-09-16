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
        "risque 5 %": {"risque_position.risque_par_trade_pct": 5.0},
        "martingale autorisée": {"coupe_circuits.interdit_martingale": False},
        "grille autorisée": {"coupe_circuits.interdit_grille": False},
        "stop élargissable": {"discipline.stop_jamais_elargi": False},
        "sans stop côté serveur": {"execution.stops_cote_serveur_obligatoire": False},
        "apprentissage en direct": {"apprentissage.apprentissage_en_ligne": True},
        "escalier des disjoncteurs inversé": {"coupe_circuits.perte_max_jour_pct": 8.0},
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
    r = reglages.modifier({"risque_position.risque_par_trade_pct": 0.5}, journal=j)
    verifier(r["ok"] and reglages.config_effective().risque.risque_par_trade_pct == 0.5,
             "TÉMOIN : baisser le risque à 0,5 % est appliqué")
    verifier(j.historique_reglages()[0]["apres"] == "0.5", "le changement est journalisé")
    r = reglages.modifier({"risque_position.risque_par_trade_pct": 5})
    verifier(not r["ok"] and reglages.config_effective().risque.risque_par_trade_pct == 0.5,
             "risque 5 % refusé et rien n'est enregistré")
    r = reglages.modifier({"coupe_circuits.interdit_martingale": False})
    verifier(not r["ok"], "une protection verrouillée n'est pas modifiable")
    r = reglages.modifier({"coupe_circuits.perte_max_jour_pct": 8})
    verifier(not r["ok"] and "escalier" in " ".join(r["erreurs"]), "le videur tranche aussi les surcharges")
    r = reglages.modifier({"coupe_circuits.perte_max_jour_pct": 4}, drawdown_pct=6.0)
    verifier(r["ok"] and r["alertes"], "relever un risque en drawdown déclenche une alerte")
    reglages.reinitialiser()
    verifier(reglages.config_effective().risque.risque_par_trade_pct == 1.0, "retour aux valeurs du fichier")


def qc_execution():
    from trading.live.execution import autorisation
    section("MODES D'EXÉCUTION")
    base = dict(mode_config="reel", capital_max_engage=200, licence_valide=True)
    verifier(not autorisation("observation", compte_demo=True, **base)[0], "observation : aucun ordre")
    verifier(autorisation("demo", compte_demo=True, **base)[0], "TÉMOIN : démo sur compte démo autorisée")
    verifier(not autorisation("demo", compte_demo=False, **base)[0], "démo branchée sur un compte réel : refus")
    verifier(autorisation("reel", compte_demo=False, **base)[0], "TÉMOIN : réel complet autorisé")
    verifier(not autorisation("reel", compte_demo=False, **{**base, "licence_valide": False})[0],
             "réel sans licence : refus")
    verifier(not autorisation("reel", compte_demo=False, **{**base, "capital_max_engage": 0})[0],
             "réel sans plafond de capital : refus")
    verifier(not autorisation("reel", compte_demo=True, **base)[0], "réel sur un compte démo : refus")


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
    res = a._modifier({"risque_position.risque_par_trade_pct": 1.8}, "test")
    verifier(res["proposition"] and not res["appliques"], "relever le risque passe par une proposition")
    res = a._modifier({"risque_position.risque_par_trade_pct": 0.5}, "test")
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
    for f in (qc_config, qc_dimensionnement, qc_capital, qc_licence, qc_reglages, qc_execution,
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
