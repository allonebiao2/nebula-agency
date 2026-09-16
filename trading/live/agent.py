# -*- coding: utf-8 -*-
"""
L'agent : la boucle qui regarde, décide, agit et raconte.

Un cycle toutes les ~20 secondes, dans son propre fil :

  1. COMMANDES   ce que l'utilisateur a demandé (pause, urgence, mode…)
  2. CONNEXION   le terminal répond-il ? sinon on le dit et on réessaie
  3. COMPTE      solde, équité, drawdown : un point d'équité par minute
  4. POSITIONS   celles qui se sont fermées chez le courtier sont soldées
                 dans le journal ; les ouvertes sont gérées (suiveur,
                 stop temporel, week-end)
  5. DISJONCTEURS jour, semaine, mois, arrêt total
  6. BOUGIE      à chaque bougie CLOSE, chaque stratégie active propose ;
                 les 8 verrous disposent ; le mode décide si un ordre part

Tout ce que fait l'agent passe par le journal : c'est ce que l'interface
montre, et c'est ce dont il apprendra.

⚠️ MetaTrader5 n'est pas fait pour être appelé depuis plusieurs fils. SEUL CE
FIL lui parle. Le serveur web ne lit qu'un instantané, et dépose ses ordres
dans une file que la boucle traite au cycle suivant.
"""
from __future__ import annotations

import json
import queue
import threading
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np

try:
    import MetaTrader5 as mt5
except ImportError:                                            # pragma: no cover
    mt5 = None

from ..noyau import capital as capital_mod
from ..noyau import profils, reglages
from ..noyau.calendrier import Calendrier, verrou_annonces
from ..noyau.chemins import dossier_rapports, fichier
from ..noyau.plan import ACHAT, EtatSysteme, controle_prealable
from ..strategies import catalogue
from ..strategies.base import ContexteStrategie
from ..strategies.indicateurs import atr as calc_atr
from ..apprentissage import analyse as analyse_mod
from ..apprentissage import porte as porte_mod
from ..apprentissage import sante as sante_mod
from ..backtest import montecarlo
from .execution import Executeur, autorisation
from .journal import Journal

HEURES_TF = {"M15": .25, "M30": .5, "H1": 1, "H4": 4, "D1": 24}


@dataclass
class MarcheLive:
    """Un instrument tradé : son nom chez CE courtier, ses spécifications, son exécuteur."""
    base: str                 # EURUSD, NAS100
    nom: str                  # EURUSD, « US Tech 100 »
    specs: object
    executeur: Executeur


@dataclass
class Commande:
    action: str
    valeur: object = None
    auteur: str = "interface"


def parametres_du_walkforward(nom: str, timeframe: str, garder_weekend: bool,
                              symbole: str = "EURUSD") -> tuple[dict, str]:
    """Les réglages choisis par la DERNIÈRE fenêtre du walk-forward.

    C'est la définition même du walk-forward en production : on trade l'année
    qui vient avec ce que les quatre années précédentes ont choisi.
    """
    variante = "sans_weekend" if garder_weekend else "reference"
    candidats = sorted(dossier_rapports().glob(f"walkforward_{nom}_{symbole.upper()}_{timeframe}*.json"))
    choisi = None
    for p in candidats:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            continue
        if d.get("variante", "reference") == variante or choisi is None:
            choisi = (d, p.name)
            if d.get("variante", "reference") == variante:
                break
    if not choisi:
        return {}, "réglages par défaut (aucun walk-forward)"
    fen = [f for f in choisi[0].get("fenetres", []) if f.get("parametres")]
    if not fen:
        return {}, "réglages par défaut (walk-forward vide)"
    return fen[-1]["parametres"], f"walk-forward {choisi[1]}, fenêtre {fen[-1]['debut_test'][:4]}"


class Agent:
    def __init__(self, journal: Journal | None = None, *, profil: str = "defaut",
                 licence_valide=lambda: False):
        self.journal = journal or Journal()
        self.profil = profil
        self.licence_valide = licence_valide
        self._commandes: "queue.Queue[Commande]" = queue.Queue()
        self._reveil = threading.Event()
        self._stop = threading.Event()
        self._fil: threading.Thread | None = None
        self._verrou = threading.Lock()

        self.courtier = None
        self.symbole = None
        self.specs = None
        self.executeur: Executeur | None = None
        self.marches: dict[str, MarcheLive] = {}
        self.type_compte = None
        self.calendrier: Calendrier | None = None
        self.connecte = False
        self.message_connexion = "pas encore connecté"
        self._derniere_barre: dict[str, datetime] = {}
        self._dernier_point = 0.0
        self._prochaine_tentative = 0.0
        self.pause_motif = ""
        self.arret_total = False
        self.decalage_h = 0.0
        self.etat_profil: profils.EtatProfil | None = self._lire_etat_profil()
        self.risque_du_palier: tuple[float, str] = (0.0, "")
        self.sante: dict[str, dict] = {}
        self.portes: dict = {}
        self._portes_le = 0.0
        self._alertes_emises: set[str] = set()
        self._deconnecte_depuis: float | None = None
        self._positions_connues = 0
        self.cycles = 0
        self._instantane: dict = {"etat": "démarrage"}

    # ------------------------------------------------------------------ #
    #  Cycle de vie
    # ------------------------------------------------------------------ #
    def demarrer(self) -> None:
        if self._fil and self._fil.is_alive():
            return
        self._stop.clear()
        self._fil = threading.Thread(target=self._boucle, name="agent", daemon=True)
        self._fil.start()
        self.journal.evenement("agent", f"agent démarré en mode {reglages.agent()['mode']}")

    def arreter(self) -> None:
        self._stop.set()
        self._reveil.set()
        if self._fil:
            self._fil.join(timeout=10)
        if mt5 is not None and self.connecte:
            mt5.shutdown()
        self.connecte = False

    def commander(self, action: str, valeur=None, auteur: str = "interface") -> None:
        self._commandes.put(Commande(action, valeur, auteur))
        self._reveil.set()

    @staticmethod
    def _lire_etat_profil() -> profils.EtatProfil | None:
        p = fichier("profil_etat.json")
        try:
            return profils.EtatProfil.depuis_json(p.read_text(encoding="utf-8")) if p.exists() else None
        except Exception:                                     # noqa: BLE001
            return None

    def _ecrire_etat_profil(self) -> None:
        if self.etat_profil:
            fichier("profil_etat.json").write_text(self.etat_profil.en_json(), encoding="utf-8")

    def _suivre_profil(self, cfg, compte) -> None:
        """Point de départ des paliers et poche épargne, remis à zéro à chaque changement
        de profil ; et mise à l'abri des gains quand le seuil est franchi."""
        if self.etat_profil is None or self.etat_profil.profil != cfg.profil.actif:
            ancien = self.etat_profil.profil if self.etat_profil else None
            self.etat_profil = profils.initialiser(cfg.profil.actif, compte.equity)
            self._ecrire_etat_profil()
            depart = f"{compte.equity:,.2f}".replace(",", " ")
            self.journal.evenement(
                "profil", f"profil {cfg.profil.actif.upper()} actif"
                          + (f" (était {ancien.upper()})" if ancien else "")
                          + f" : point de départ des paliers {depart}",
                niveau="alerte" if cfg.profil.boost else "info")
        part = profils.mettre_a_l_abri(cfg, self.etat_profil, compte.equity)
        if part > 0:
            self._ecrire_etat_profil()
            texte = f"{part:,.2f} mis à l'abri (total {self.etat_profil.verrouille:,.2f})"
            self.journal.evenement("poche", texte.replace(",", " ")
                                   + " : ces gains ne seront plus jamais risqués")
        self.risque_du_palier = profils.risque_courant(cfg, self.etat_profil, compte.equity)

    # ------------------------------------------------------------------ #
    #  Santé, portes, chien de garde, rapport hebdomadaire
    # ------------------------------------------------------------------ #
    def _alerte_unique(self, cle: str, message: str, niveau: str = "critique") -> None:
        if cle not in self._alertes_emises:
            self._alertes_emises.add(cle)
            self.journal.evenement("chien de garde", message, niveau=niveau)

    def _evaluer_sante(self, cfg, ag) -> None:
        """CUSUM de chaque stratégie active contre son walk-forward ; portes toutes les minutes."""
        bases = list(self.marches) or list(cfg.marche.liste)
        for base in bases:
            nom_courtier = self.marches[base].nom if base in self.marches else base
            for nom in ag["strategies_actives"]:
                cle = f"{nom} · {base}"
                d = montecarlo.rapport_actif(dossier_rapports(), nom, cfg.marche.timeframe,
                                             not cfg.calendrier.fermer_avant_weekend, symbole=base)
                reference = montecarlo.rendements_en_R(d) if d else []
                reprise = (ag.get("reprises_sante") or {}).get(cle)
                live = [t["resultat_R"] for t in reversed(self.journal.trades(2000, ouverts=False))
                        if t.get("strategie") == nom and t.get("mode") in ("demo", "reel")
                        and (t.get("symbole") or "EURUSD") in (base, nom_courtier)
                        and (not reprise or (t.get("ferme_le") or "") > reprise)]
                diag = sante_mod.diagnostiquer(live, reference, cle=f"{cle}:{d.get('calcule_le') if d else ''}")
                ancien = self.sante.get(cle, {}).get("statut")
                self.sante[cle] = diag
                if diag["statut"] != ancien and ancien is not None and diag["statut"] in ("pause", "surveillance"):
                    self.journal.evenement("santé", f"{cle} : {diag['statut'].upper()} · {diag['message']}",
                                           niveau="critique" if diag["statut"] == "pause" else "alerte")
        if time.time() - self._portes_le > 60:
            principale = next(iter(self.sante.values()), {})
            self.portes = {"demo": porte_mod.porte_demo(self.journal, sante=principale),
                           "boost_reel": porte_mod.porte_boost_reel(self.journal, sante=principale)}
            self._portes_le = time.time()

    def _chien_de_garde(self, cfg, compte, positions) -> None:
        """Ce qui doit arrêter les entrées sans attendre un humain."""
        maintenant = datetime.now(timezone.utc)
        # 1. ordres rejetés en série : le courtier refuse, on n'insiste pas
        heure = (maintenant - timedelta(hours=1)).isoformat()
        rejets = [o for o in self.journal.ordres(50)
                  if o["action"] == "ouvrir" and o["ts"] >= heure and o.get("retcode") not in (10009, None)]
        if len(rejets) >= 3 and not self.pause_motif:
            self.pause_motif = f"chien de garde : {len(rejets)} ordres rejetés en une heure"
            self.journal.evenement("chien de garde", self.pause_motif + " ; plus aucune entrée",
                                   niveau="critique")
        # 2. position sans stop chez le courtier : on en pose un, sinon on ferme
        for p in positions:
            if p.sl:
                continue
            trade = self.journal.trade_par_ticket(p.ticket) or {}
            stop = trade.get("stop_initial")
            m = self._marche_de(p) if self.marches else None
            execu = m.executeur if m else self.executeur
            chiffres = m.specs.digits if m else self.specs.digits
            r = execu.poser_stop(p, stop, digits=chiffres) if stop else None
            if r is not None and r.ok:
                self.journal.evenement("chien de garde", f"position {p.ticket} trouvée SANS stop : "
                                                         f"stop posé à {stop}", niveau="critique")
            else:
                f = execu.fermer(p, motif="sans stop")
                self.journal.evenement("chien de garde", f"position {p.ticket} SANS stop et stop impossible "
                                                         f"à poser : fermeture {'faite' if f.ok else 'REFUSÉE'}",
                                       niveau="critique")
        # 3. chute brutale de l'équité
        seuil = max(3.0, 2 * cfg.risque.risque_par_trade_pct)
        points = self.journal.courbe(depuis_jours=1, points_max=5000)
        recents = [q for q in points if q["ts"] >= heure]
        if recents:
            haut = max(q["equite"] for q in recents)
            chute = 100 * (haut - compte.equity) / haut if haut else 0.0
            if chute >= seuil and not self.pause_motif:
                self.pause_motif = f"chien de garde : équité −{chute:.1f} % en une heure (seuil {seuil:g} %)"
                self.journal.evenement("chien de garde", self.pause_motif, niveau="critique")

    def _garde_deconnexion(self) -> None:
        if self._deconnecte_depuis is None:
            self._deconnecte_depuis = time.time()
            return
        if self._positions_connues and time.time() - self._deconnecte_depuis > 600:
            self._alerte_unique(
                f"deconnexion-{int(self._deconnecte_depuis)}",
                f"terminal muet depuis {int((time.time() - self._deconnecte_depuis) / 60)} min avec "
                f"{self._positions_connues} position(s) ouverte(s) : l'agent ne peut plus agir, "
                f"seuls les stops déposés chez le courtier protègent le compte")

    def _rapport_hebdomadaire(self) -> None:
        semaine = datetime.now(timezone.utc).strftime("%G-S%V")
        marque = fichier("dernier_rapport_hebdo.txt")
        if marque.exists() and marque.read_text(encoding="utf-8").strip() == semaine:
            return
        rapport = analyse_mod.analyser(self.journal, depuis_jours=7)
        dossier = fichier("rapports_hebdo")
        dossier.mkdir(exist_ok=True)
        (dossier / f"{semaine}.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
        marque.write_text(semaine, encoding="utf-8")
        self.journal.evenement("analyse hebdo", f"rapport {semaine} : " + " ".join(rapport["constats"][:2]))

    def instantane(self) -> dict:
        with self._verrou:
            return dict(self._instantane)

    def _boucle(self) -> None:
        while not self._stop.is_set():
            debut = time.time()
            try:
                self.cycle()
            except Exception as exc:                          # noqa: BLE001
                self.journal.evenement("erreur", f"cycle interrompu : {exc}", niveau="alerte",
                                       donnees={"trace": traceback.format_exc()[-2000:]})
            self.cycles += 1
            attente = max(2.0, reglages.agent()["intervalle_cycle_s"] - (time.time() - debut))
            self._reveil.wait(attente)
            self._reveil.clear()

    # ------------------------------------------------------------------ #
    #  Le cycle
    # ------------------------------------------------------------------ #
    def cycle(self) -> None:
        cfg = reglages.config_effective()
        ag = reglages.agent()
        self._traiter_commandes(cfg)

        if not self._assurer_connexion(cfg):
            self._garde_deconnexion()
            self._publier(cfg, ag, None, [])
            return
        self._deconnecte_depuis = None

        compte = mt5.account_info()
        if compte is None:
            self.connecte = False
            self.message_connexion = "le terminal ne renvoie plus le compte"
            self._publier(cfg, ag, None, [])
            return

        maintenant_serveur = self._heure_serveur()
        positions = self._toutes_positions()
        self._solder_positions_fermees(positions)
        positions = self._toutes_positions()

        if time.time() - self._dernier_point >= 60:
            self.journal.point_equite(compte.balance, compte.equity, compte.margin_free)
            self._dernier_point = time.time()

        self._suivre_profil(cfg, compte)
        capital = capital_mod.capital_de_travail(
            profils.capital_disponible(compte.balance, self.etat_profil),
            cfg.compte.capital_max_engage, self.type_compte)
        risque = self._etat_du_risque(cfg, capital)

        if risque["drawdown_pct"] >= cfg.circuits.drawdown_max_total_pct and not self.arret_total:
            self.arret_total = True
            self.journal.evenement("disjoncteur",
                                   f"ARRÊT TOTAL : drawdown {risque['drawdown_pct']:.1f} % "
                                   f"(seuil {cfg.circuits.drawdown_max_total_pct} %). "
                                   f"Redémarrage manuel requis.", niveau="critique")

        self._evaluer_sante(cfg, ag)
        self._chien_de_garde(cfg, compte, positions)
        self._rapport_hebdomadaire()
        self._positions_connues = len(positions)

        mode = ag["mode"]
        peut_trader, raison_mode = autorisation(
            mode, compte_demo=compte.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO,
            mode_config=cfg.compte.mode, capital_max_engage=cfg.compte.capital_max_engage,
            licence_valide=self.licence_valide(),
            profil_boost=cfg.profil.boost,
            porte_boost_franchie=self.portes.get("boost_reel", {}).get("franchie", False),
            porte_demo_franchie=self.portes.get("demo", {}).get("franchie", False))

        self._gerer_positions(cfg, positions, maintenant_serveur, peut_trader)

        for marche in self.marches.values():
            for nom in ag["strategies_actives"]:
                if nom in catalogue.STRATEGIES:
                    self._analyser(nom, marche, cfg, compte, capital, risque, positions,
                                   maintenant_serveur, mode, peut_trader, raison_mode)

        self._publier(cfg, ag, compte, self._toutes_positions(), risque=risque,
                      capital=capital, raison_mode=raison_mode, peut_trader=peut_trader)

    # ------------------------------------------------------------------ #
    def _assurer_connexion(self, cfg) -> bool:
        if self.connecte and mt5.terminal_info() is not None:
            return True
        if time.time() < self._prochaine_tentative:
            return False
        from ..noyau.courtier import Courtier, CourtierIndisponible
        from ..noyau.identifiants import IdentifiantsManquants
        try:
            self.courtier = Courtier.depuis_profil(self.profil)
            profil = self.courtier.connecter()
            self.marches = {}
            for base in cfg.marche.liste:
                nom = self.courtier.trouver_symbole(base, silencieux=True)
                if not nom:
                    self.journal.evenement("connexion", f"{base} introuvable chez ce courtier : "
                                                        f"instrument ignoré", niveau="alerte")
                    continue
                self.marches[base] = MarcheLive(
                    base=base, nom=nom, specs=self.courtier.specs(nom),
                    executeur=Executeur(nom, cfg.compte.magic_number,
                                        deviation_points=cfg.execution.slippage_max_points,
                                        tentatives=cfg.execution.tentatives_max))
            if not self.marches:
                raise RuntimeError("aucun des instruments configurés n'existe chez ce courtier")
            principal = next(iter(self.marches.values()))
            self.symbole, self.specs, self.executeur = principal.nom, principal.specs, principal.executeur
            self.type_compte = capital_mod.detecter(profil.devise, profil.serveur, self.symbole)
            self.decalage_h = profil.decalage_serveur_h or 0.0
            self.calendrier = Calendrier(
                avant_min=cfg.calendrier.blackout_avant_minutes,
                apres_min=cfg.calendrier.blackout_apres_minutes,
                decalage_serveur_h=profil.decalage_serveur_h or 0.0)
            self.calendrier.rafraichir()
            self.connecte = True
            self.message_connexion = (f"connecté à {profil.serveur} · compte {profil.login} "
                                      f"{'DÉMO' if profil.demo else 'RÉEL'}")
            self.journal.evenement("connexion", self.message_connexion,
                                   donnees={"symboles": {b: m.nom for b, m in self.marches.items()},
                                            "type_compte": self.type_compte.libelle(),
                                            "algo_autorise": profil.algo_autorise})
            if not profil.algo_autorise:
                self.journal.evenement(
                    "connexion", "Trading algorithmique NON autorisé dans le terminal (bouton "
                                 "« Trading Algo » ou case API Python) : aucun ordre ne passera.",
                    niveau="alerte")
            return True
        except (CourtierIndisponible, IdentifiantsManquants, Exception) as exc:  # noqa: BLE001
            self.connecte = False
            self.message_connexion = str(exc).split("\n")[0][:300]
            self._prochaine_tentative = time.time() + 60
            self.journal.evenement("connexion", f"connexion impossible : {self.message_connexion}",
                                   niveau="alerte")
            return False

    def _toutes_positions(self) -> list:
        return [q for m in self.marches.values() for q in m.executeur.positions()]

    def _marche_de(self, position) -> MarcheLive:
        for m in self.marches.values():
            if m.nom == position.symbol:
                return m
        return next(iter(self.marches.values()))

    def _heure_serveur(self) -> datetime:
        tick = mt5.symbol_info_tick(self.symbole)
        if tick and tick.time:
            t = datetime.fromtimestamp(tick.time, tz=timezone.utc).replace(tzinfo=None)
            if abs((datetime.now(timezone.utc).replace(tzinfo=None) - t).total_seconds()) < 3600 * 14:
                return t
        return datetime.now(timezone.utc).replace(tzinfo=None)

    # ------------------------------------------------------------------ #
    #  Commandes
    # ------------------------------------------------------------------ #
    def _traiter_commandes(self, cfg) -> None:
        while True:
            try:
                c = self._commandes.get_nowait()
            except queue.Empty:
                return
            try:
                self._executer_commande(c, cfg)
            except Exception as exc:                          # noqa: BLE001
                self.journal.evenement("commande", f"« {c.action} » a échoué : {exc}",
                                       niveau="alerte")

    def _executer_commande(self, c: Commande, cfg) -> None:
        if c.action == "pause":
            self.pause_motif = str(c.valeur or "pause demandée")
            self.journal.evenement("commande", f"pause ({self.pause_motif}) par {c.auteur}")
        elif c.action == "reprendre":
            self.pause_motif = ""
            self.journal.evenement("commande", f"reprise par {c.auteur}")
        elif c.action == "urgence":
            self.pause_motif = "arrêt d'urgence"
            fermees = 0
            if self.connecte and self.marches:
                for p in self._toutes_positions():
                    r = self._marche_de(p).executeur.fermer(p, motif="urgence")
                    self.journal.ordre(action="fermer", ticket=p.ticket, lots=p.volume,
                                       prix=r.prix, retcode=r.retcode, commentaire=r.message,
                                       mode=reglages.agent()["mode"])
                    fermees += r.ok
            self.journal.evenement("commande", f"ARRÊT D'URGENCE par {c.auteur} : {fermees} "
                                               f"position(s) fermée(s), agent en pause",
                                   niveau="critique")
        elif c.action == "mode":
            ancien = reglages.agent()["mode"]
            reglages.modifier_agent({"mode": c.valeur})
            self.journal.evenement("commande", f"mode {ancien} -> {c.valeur} par {c.auteur}",
                                   niveau="alerte" if c.valeur == "reel" else "info")
        elif c.action == "strategies":
            reglages.modifier_agent({"strategies_actives": list(c.valeur)})
            self.journal.evenement("commande", f"stratégies actives : {', '.join(c.valeur) or 'aucune'}")
        elif c.action == "relancer_apres_arret":
            self.arret_total = False
            self.journal.remettre_sommet()
            self.journal.evenement("commande", f"arrêt total levé par {c.auteur} : le drawdown "
                                               f"repart du niveau actuel", niveau="alerte")
        elif c.action == "analyser":
            self._derniere_barre.clear()
            self.journal.evenement("commande", "nouvelle analyse de la dernière bougie demandée")
        elif c.action == "reprendre_strategie":
            reprises = dict(reglages.agent().get("reprises_sante") or {})
            reprises[str(c.valeur)] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            reglages.modifier_agent({"reprises_sante": reprises})
            self.sante.pop(str(c.valeur), None)
            self.journal.evenement("santé", f"{c.valeur} reprise manuellement par {c.auteur} : le CUSUM "
                                            f"repart de zéro", niveau="alerte")
        elif c.action == "reconnecter":
            if mt5 is not None:
                mt5.shutdown()
            self.connecte = False
            self._prochaine_tentative = 0
        else:
            raise ValueError(f"commande inconnue : {c.action}")

    # ------------------------------------------------------------------ #
    #  Positions
    # ------------------------------------------------------------------ #
    def _solder_positions_fermees(self, positions) -> None:
        ouvertes = {p.ticket for p in positions}
        for t in self.journal.trades(limite=50, ouverts=True):
            if t["ticket"] in ouvertes:
                continue
            bilan = self.executeur.bilan_position_fermee(t["ticket"])
            if bilan is None:
                continue
            ferme_le = datetime.fromtimestamp(bilan["ferme_le"], tz=timezone.utc).isoformat()
            self.journal.fermer_trade(ticket=t["ticket"], prix=bilan["prix"],
                                      resultat=bilan["resultat"], motif=bilan["motif"],
                                      ferme_le=ferme_le)
            signe = "+" if bilan["resultat"] > 0 else ""
            self.journal.evenement(
                "trade", f"position {t['ticket']} fermée ({bilan['motif']}) : "
                         f"{signe}{bilan['resultat']:.2f}",
                niveau="info" if bilan["resultat"] > 0 else "alerte")

    def _gerer_positions(self, cfg, positions, maintenant_serveur, peut_trader) -> None:
        if not positions or not peut_trader:
            return
        tf = cfg.marche.timeframe
        heures = HEURES_TF.get(tf, 4)
        barres_par_symbole: dict = {}
        cal = cfg.calendrier
        for p in positions:
            m = self._marche_de(p)
            achat = p.type == mt5.POSITION_TYPE_BUY
            # --- week-end -------------------------------------------------
            if cal.fermer_avant_weekend and maintenant_serveur.weekday() == 4 \
                    and maintenant_serveur.time() >= cal.vendredi_tout_fermer:
                self._fermer(p, "week-end")
                continue
            # --- stop temporel ------------------------------------------
            ouverte = datetime.fromtimestamp(p.time, tz=timezone.utc).replace(tzinfo=None)
            barres_tenues = (maintenant_serveur - ouverte).total_seconds() / 3600 / heures
            if cfg.discipline.stop_temporel_barres and \
                    barres_tenues >= cfg.discipline.stop_temporel_barres:
                self._fermer(p, "temporel")
                continue
            # --- suiveur : après 1 R, jamais élargi ---------------------
            if not cfg.risque.trailing_actif:
                continue
            trade = self.journal.trade_par_ticket(p.ticket)
            if not trade or not trade.get("stop_initial"):
                continue
            risque_prix = abs(trade["prix_entree"] - trade["stop_initial"])
            if risque_prix <= 0:
                continue
            avance = (p.price_current - p.price_open) / risque_prix * (1 if achat else -1)
            if avance < cfg.risque.trailing_declenche_a_r:
                continue
            if m.nom not in barres_par_symbole:
                from ..noyau.donnees_mt5 import dernieres_barres
                barres_par_symbole[m.nom] = dernieres_barres(m.nom, tf, 100)
            barres = barres_par_symbole[m.nom]
            a = calc_atr(barres.haut, barres.bas, barres.cloture, cfg.risque.atr_periode)[-1]
            if np.isnan(a):
                continue
            marge = cfg.risque.trailing_atr_multiple * float(a)
            propose = p.price_current - marge if achat else p.price_current + marge
            meilleur = (propose > p.sl) if achat else (p.sl == 0 or propose < p.sl)
            if meilleur:
                r = m.executeur.modifier_stop(p, propose, digits=m.specs.digits)
                if r.ok:
                    self.journal.evenement("suiveur", f"{m.base} : stop de {p.ticket} resserré à "
                                                      f"{propose:.{m.specs.digits}f}")

    def _fermer(self, p, motif: str) -> None:
        r = self._marche_de(p).executeur.fermer(p, motif=motif)
        self.journal.ordre(action="fermer", ticket=p.ticket, lots=p.volume, prix=r.prix,
                           retcode=r.retcode, commentaire=f"{motif} · {r.message}",
                           mode=reglages.agent()["mode"])
        self.journal.evenement("trade", f"position {p.ticket} : fermeture « {motif} » "
                                        f"{'faite' if r.ok else 'REFUSÉE : ' + r.message}",
                               niveau="info" if r.ok else "alerte")

    # ------------------------------------------------------------------ #
    #  Risque
    # ------------------------------------------------------------------ #
    def _etat_du_risque(self, cfg, capital: float) -> dict:
        maintenant = datetime.now(timezone.utc)
        debut_jour = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)
        debut_semaine = debut_jour - timedelta(days=debut_jour.weekday())
        debut_mois = debut_jour.replace(day=1)
        def pnl(depuis):
            return sum(t["resultat_devise"] or 0 for t in self.journal.fermes_depuis(depuis))
        dernier = self.journal.dernier_point()
        serie, derniere_perte = self.journal.serie_perdante()
        minutes = None
        if derniere_perte:
            minutes = (maintenant - datetime.fromisoformat(derniere_perte)).total_seconds() / 60
        ouverts = self.journal.trades(limite=20, ouverts=True)
        exposition = sum((t["risque_devise"] or 0) for t in ouverts)
        return {
            "pnl_jour": pnl(debut_jour), "pnl_semaine": pnl(debut_semaine),
            "pnl_mois": pnl(debut_mois),
            "pnl_jour_pct": 100 * pnl(debut_jour) / capital if capital else 0.0,
            "pnl_semaine_pct": 100 * pnl(debut_semaine) / capital if capital else 0.0,
            "pnl_mois_pct": 100 * pnl(debut_mois) / capital if capital else 0.0,
            "drawdown_pct": dernier["drawdown_pct"] if dernier else 0.0,
            "pertes_consecutives": serie, "minutes_depuis_perte": minutes,
            "trades_jour": self.journal.ouverts_depuis(debut_jour),
            "trades_semaine": self.journal.ouverts_depuis(debut_semaine),
            "exposition_pct": 100 * exposition / capital if capital else 0.0,
        }

    def _disjoncteur(self, cfg, risque) -> str:
        c = cfg.circuits
        for cle, seuil, nom in (("pnl_jour_pct", c.perte_max_jour_pct, "jour"),
                                ("pnl_semaine_pct", c.perte_max_semaine_pct, "semaine"),
                                ("pnl_mois_pct", c.perte_max_mois_pct, "mois")):
            if risque[cle] <= -seuil:
                return f"disjoncteur {nom} : {risque[cle]:.1f} % (seuil -{seuil} %)"
        return ""

    # ------------------------------------------------------------------ #
    #  Analyse d'une bougie close
    # ------------------------------------------------------------------ #
    def _analyser(self, nom, marche: MarcheLive, cfg, compte, capital, risque, positions,
                  maintenant_serveur, mode, peut_trader, raison_mode) -> None:
        from ..noyau.donnees_mt5 import dernieres_barres
        tf = cfg.marche.timeframe
        barres = dernieres_barres(marche.nom, tf, 700)
        i = len(barres) - 1
        barre_close = barres.quand(i)
        cle = f"{nom} · {marche.base}"
        if self._derniere_barre.get(cle) == barre_close:
            return
        self._derniere_barre[cle] = barre_close

        params, origine = parametres_du_walkforward(nom, tf, not cfg.calendrier.fermer_avant_weekend,
                                                    marche.base)
        strategie = catalogue.STRATEGIES[nom](**params)
        strategie.preparer(barres)
        atr_i = float(strategie._atr[i]) if not np.isnan(strategie._atr[i]) else 0.0
        regime = strategie.regime_a(i) if hasattr(strategie, "regime_a") else "inconnu"
        ctx = ContexteStrategie(i=i, barres=barres, atr=atr_i, regime=regime,
                                maintenant=maintenant_serveur)
        plan = strategie.signal(ctx) if atr_i > 0 else None

        if plan is None:
            self.journal.evenement(
                "analyse", f"{cle} · bougie {tf} de {barre_close:%d/%m %H:%M} close à "
                           f"{barres.cloture[i]:.{marche.specs.digits}f} : pas de signal (régime {regime})",
                donnees={"strategie": nom, "regime": regime, "atr": atr_i, "origine": origine})
            return

        motif_blocage = ""
        diag = self.sante.get(cle, {})
        memes = [q for q in positions if q.symbol == marche.nom]
        if diag.get("statut") == "pause":
            motif_blocage = f"stratégie en pause de santé (CUSUM) : {diag.get('message', '')}"
        elif self.arret_total:
            motif_blocage = "arrêt total en cours (redémarrage manuel requis)"
        elif self.pause_motif:
            motif_blocage = f"agent en pause : {self.pause_motif}"
        elif memes:
            motif_blocage = f"une position déjà ouverte sur {marche.base} (une par instrument)"
        elif len(positions) >= cfg.exposition.positions_simultanees_max:
            motif_blocage = (f"{len(positions)} position(s) déjà ouverte(s), plafond "
                             f"{cfg.exposition.positions_simultanees_max}")
        else:
            motif_blocage = self._disjoncteur(cfg, risque)

        tick = mt5.symbol_info_tick(marche.nom)
        spread = (tick.ask - tick.bid) / marche.specs.point if tick else 0.0
        from ..noyau.donnees_mt5 import charger_profil
        prof = charger_profil(marche.base) or {}
        etat = EtatSysteme(
            spread_points=spread,
            spread_habituel_points=prof.get("spread_median_points") or 0.0,
            atr_courant=atr_i,
            pertes_consecutives=risque["pertes_consecutives"],
            minutes_depuis_derniere_perte=risque["minutes_depuis_perte"],
            trades_aujourdhui=risque["trades_jour"],
            trades_cette_semaine=risque["trades_semaine"],
            lots_deja_ouverts=sum(q.volume for q in memes),
            exposition_courante_pct=risque["exposition_pct"],
            drawdown_courant_pct=risque["drawdown_pct"],
            regime=regime,
            regimes_favorables=(regime,) if strategie.regime_favorable(ctx) else ("aucun",),
            en_pause=bool(motif_blocage), motif_pause=motif_blocage,
        )
        annonces = verrou_annonces(self.calendrier) if self.calendrier else None
        risque_du_palier, _note_palier = self.risque_du_palier
        verdict = controle_prealable(
            plan, cfg, etat, capital=capital, specs=marche.specs,
            annonce_imminente=annonces, maintenant=maintenant_serveur,
            risque_pct_plafond=cfg.risque.risque_max_petit_compte_pct,
            risque_pct=risque_du_palier or None,
            prix=(tick.ask if plan.sens == ACHAT else tick.bid) if tick else None)
        profil = cfg.profil.actif

        if not verdict.autorise:
            motif = " · ".join(f"Q{v.numero} {v.detail.splitlines()[0]}" for v in verdict.refus)
            self.journal.decision(verdict_obj=verdict, verdict="refuse", motif=motif, mode=mode,
                                  barre=barre_close, profil=profil, risque_choisi=risque_du_palier)
            self.journal.evenement("decision", f"{cle} proposait {plan.sens.upper()} : REFUSÉ "
                                               f"({len(verdict.refus)} verrou(s))",
                                   niveau="info", donnees={"motif": motif})
            return

        # Le backtest entre à l'OUVERTURE de la bougie suivante. Un signal
        # découvert tard (démarrage, reconnexion) n'est plus le même trade :
        # le prix a bougé, la mesure ne le couvre pas.
        fin_bougie = barre_close + timedelta(hours=HEURES_TF.get(tf, 4))
        retard_min = (maintenant_serveur - fin_bougie).total_seconds() / 60
        if peut_trader and retard_min > 45:
            peut_trader = False
            raison_mode = (f"signal de la bougie close il y a {retard_min:.0f} min : entrée trop "
                           f"tardive par rapport à ce que mesure le backtest")

        if not peut_trader:
            self.journal.decision(verdict_obj=verdict, verdict="observe", motif=raison_mode,
                                  mode=mode, barre=barre_close, profil=profil,
                                  risque_choisi=risque_du_palier)
            self.journal.evenement("decision", f"{cle} : {plan.sens.upper()} autorisé par les "
                                               f"8 verrous, NON envoyé ({raison_mode})")
            return

        dim = verdict.dimensionnement
        r = marche.executeur.ouvrir(plan, dim.lots, specs=marche.specs,
                                    commentaire=f"nebula {nom[:12]}")
        self.journal.ordre(action="ouvrir", ticket=r.ticket, sens=plan.sens, lots=dim.lots,
                           prix=r.prix, sl=r.sl, tp=r.tp, retcode=r.retcode,
                           commentaire=r.message, mode=mode, prix_demande=r.prix_demande,
                           glissement_points=r.glissement_points)
        if r.ok:
            self.journal.decision(verdict_obj=verdict, verdict="pris", mode=mode,
                                  barre=barre_close, profil=profil, risque_choisi=risque_du_palier)
            self.journal.ouvrir_trade(ticket=r.ticket, plan=plan, lots=dim.lots, prix=r.prix,
                                      risque_devise=dim.risque_devise, mode=mode, profil=profil)
            self.journal.evenement("trade", f"{marche.base} {plan.sens.upper()} {dim.lots:g} lot à {r.prix} · "
                                            f"stop {r.sl} · objectif {r.tp} · risque "
                                            f"{dim.risque_pct:.2f} %", niveau="info")
        else:
            self.journal.decision(verdict_obj=verdict, verdict="echec", motif=r.message,
                                  mode=mode, barre=barre_close, profil=profil,
                                  risque_choisi=risque_du_palier)
            self.journal.evenement("trade", f"ordre refusé par le courtier : {r.message}",
                                   niveau="alerte")

    # ------------------------------------------------------------------ #
    #  Instantané pour l'interface
    # ------------------------------------------------------------------ #
    def _publier(self, cfg, ag, compte, positions, *, risque=None, capital=None,
                 raison_mode="", peut_trader=False) -> None:
        tf = cfg.marche.timeframe
        heures = HEURES_TF.get(tf, 4)
        derniere = max(self._derniere_barre.values()) if self._derniere_barre else None
        prochaine = (derniere + timedelta(hours=2 * heures)) if derniere else None
        tc = self.type_compte
        pos = []
        for p in positions:
            trade = self.journal.trade_par_ticket(p.ticket) or {}
            risque_prix = abs((trade.get("prix_entree") or p.price_open)
                              - (trade.get("stop_initial") or p.sl or p.price_open))
            achat = p.type == mt5.POSITION_TYPE_BUY
            r_courant = ((p.price_current - p.price_open) / risque_prix * (1 if achat else -1)
                         if risque_prix else None)
            pos.append({"ticket": p.ticket, "sens": "achat" if achat else "vente", "symbole": p.symbol,
                        "lots": p.volume, "prix_entree": p.price_open,
                        "prix_actuel": p.price_current, "sl": p.sl, "tp": p.tp,
                        "profit": p.profit + p.swap, "R": r_courant,
                        "ouverte_le": datetime.fromtimestamp(p.time, tz=timezone.utc).isoformat(),
                        "strategie": trade.get("strategie"), "these": trade.get("these")})
        prochaines = []
        if self.calendrier:
            prochaines = [{"quand": a.quand_utc.isoformat(), "devise": a.devise,
                           "titre": a.titre} for a in self.calendrier.a_venir(heures=72)[:8]]
        instant = {
            "maj": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "cycles": self.cycles,
            "connexion": {"ok": self.connecte, "message": self.message_connexion,
                          "symbole": self.symbole,
                          "marches": {b: m.nom for b, m in self.marches.items()}},
            "mode": ag["mode"], "peut_trader": peut_trader, "raison_mode": raison_mode,
            "pause": self.pause_motif, "arret_total": self.arret_total,
            "strategies_actives": ag["strategies_actives"],
            "timeframe": tf, "derniere_bougie": derniere.isoformat() if derniere else None,
            "prochaine_bougie": prochaine.isoformat() if prochaine else None,
            "prochaine_bougie_utc": ((prochaine - timedelta(hours=self.decalage_h)).isoformat() + "Z")
            if prochaine else None,
            "positions": pos, "calendrier": prochaines,
            "sante": {k: {x: y for x, y in v.items() if x != "trajet"} for k, v in self.sante.items()},
            "portes": self.portes,
            "calendrier_ok": bool(self.calendrier and self.calendrier.disponible),
        }
        ep = self.etat_profil
        instant["profil"] = {
            "actif": cfg.profil.actif, "risque_choisi": cfg.risque.risque_par_trade_pct,
            "risque_courant": self.risque_du_palier[0] or cfg.risque.risque_par_trade_pct,
            "note_palier": self.risque_du_palier[1], "plafond_code": cfg.profil.plafond_risque_pct,
            "levier_max": cfg.profil.levier_effectif_max, "paliers": list(cfg.profil.paliers),
            "paliers_actifs": cfg.profil.paliers_actifs,
            "poche": {"declencheur_pct": cfg.profil.poche_declencheur_pct,
                      "part_pct": cfg.profil.poche_part_pct,
                      "verrouille": ep.verrouille if ep else 0.0,
                      "verrouille_reel": (tc.en_reel(ep.verrouille) if (ep and tc) else 0.0),
                      "mises_a_l_abri": ep.mises_a_l_abri if ep else 0},
            "capital_depart": ep.capital_depart if ep else None,
            "porte_boost_franchie": bool(self.portes.get("boost_reel", {}).get("franchie", False)),
        }
        if compte is not None and tc is not None:
            instant["compte"] = {
                "login": compte.login, "serveur": compte.server, "societe": compte.company,
                "devise": compte.currency, "demo": compte.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO,
                "solde": compte.balance, "equite": compte.equity, "marge_libre": compte.margin_free,
                "levier": compte.leverage, "type_compte": tc.libelle(), "cent": tc.cent,
                "solde_reel": tc.en_reel(compte.balance), "devise_reelle": tc.devise_reelle,
                "capital_travail": capital, "capital_travail_reel": tc.en_reel(capital or 0),
            }
        if risque is not None:
            c = cfg.circuits
            instant["risque"] = {
                **risque,
                "limites": {
                    "risque_par_trade_pct": cfg.risque.risque_par_trade_pct,
                    "risque_max_petit_compte_pct": cfg.risque.risque_max_petit_compte_pct,
                    "perte_max_jour_pct": c.perte_max_jour_pct,
                    "perte_max_semaine_pct": c.perte_max_semaine_pct,
                    "perte_max_mois_pct": c.perte_max_mois_pct,
                    "drawdown_max_total_pct": c.drawdown_max_total_pct,
                    "pertes_consecutives_max": c.pertes_consecutives_max,
                    "trades_max_par_jour": cfg.discipline.trades_max_par_jour,
                    "trades_max_par_semaine": cfg.discipline.trades_max_par_semaine,
                    "exposition_totale_max_pct": cfg.exposition.exposition_totale_max_pct,
                },
                "disjoncteur": self._disjoncteur(cfg, risque),
            }
        with self._verrou:
            self._instantane = instant
