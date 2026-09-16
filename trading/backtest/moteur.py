# -*- coding: utf-8 -*-
"""
Le simulateur, barre par barre.

Quatre règles font la différence entre une mesure et une publicité. Chacune
rend les résultats PIRES, et c'est exactement pourquoi elles sont là :

  1. AUCUN REGARD VERS LE FUTUR. Le signal se calcule sur la barre qui vient de
     clore ; l'exécution a lieu à l'OUVERTURE de la barre suivante. Entrer au
     cours de clôture de la barre du signal, c'est acheter à un prix qu'on
     n'aurait pas pu obtenir.

  2. HYPOTHÈSE PESSIMISTE INTRA-BARRE. Si une barre contient à la fois le stop
     et l'objectif, on suppose le STOP touché en premier. On ne sait pas dans
     quel ordre le prix est passé : la seule hypothèse honnête est celle qui
     nous défavorise.

  3. LES COÛTS SONT FACTURÉS. Spread des deux côtés, slippage toujours
     défavorable, commission, swap.

  4. LES MÊMES VERROUS QU'EN RÉEL. Le backtest appelle `controle_prealable`,
     exactement comme le live. Sans ça, backtest et production divergent en
     silence, et c'est le compte qui paie la différence.

Un stop est une INSTRUCTION, pas une garantie : si la barre ouvre au-delà du
stop (gap), l'exécution se fait au prix d'ouverture, aussi loin soit-il.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np

from ..noyau import profils
from ..noyau.plan import ACHAT, EtatSysteme, PlanDeTrade, controle_prealable
from ..noyau.risque import SpecsSymbole, deplacement_de_stop_autorise, dimensionner
from ..strategies.base import Barres, ContexteStrategie, Strategie
from .couts import ModeleCouts
from .metriques import Metriques, TradeFerme, calculer

HEURES_PAR_TF = {"M1": 1 / 60, "M5": 5 / 60, "M15": .25, "M30": .5,
                 "H1": 1, "H4": 4, "D1": 24, "W1": 168}


@dataclass
class Position:
    plan: PlanDeTrade
    lots: float
    prix_entree: float
    stop: float
    objectif: float
    ouverte_le: datetime
    barre_entree: int
    risque_prix: float              # R en prix, figé à l'entrée
    cout_entree: float
    stop_deplace: bool = False
    nuits: int = 0

    def resultat_R(self, prix: float) -> float:
        signe = 1 if self.plan.sens == ACHAT else -1
        return signe * (prix - self.prix_entree) / self.risque_prix


@dataclass
class Resultat:
    trades: list[TradeFerme] = field(default_factory=list)
    courbe_equite: list[tuple[datetime, float]] = field(default_factory=list)
    refus: list[tuple[datetime, str]] = field(default_factory=list)
    barres_vues: int = 0
    signaux_proposes: int = 0
    capital_initial: float = 0.0
    metriques: Metriques | None = None
    verrouille: float = 0.0            # poche épargne mise à l'abri (profil BOOST)
    mises_a_l_abri: int = 0

    @property
    def taux_de_refus(self) -> float:
        return len(self.refus) / self.signaux_proposes if self.signaux_proposes else 0.0

    def motifs_de_refus(self) -> dict[str, int]:
        compte: dict[str, int] = {}
        for _, motif in self.refus:
            compte[motif] = compte.get(motif, 0) + 1
        return dict(sorted(compte.items(), key=lambda kv: -kv[1]))


class Moteur:
    def __init__(self, cfg, specs: SpecsSymbole, couts: ModeleCouts,
                 strategie: Strategie, *, journaliser_refus: bool = True,
                 annonce_imminente=None):
        self.cfg = cfg
        self.specs = specs
        self.couts = couts
        self.strategie = strategie
        self.journaliser_refus = journaliser_refus
        # Sans calendrier économique historique, le backtest ne peut pas
        # reproduire le blackout : il le déclare, il ne le simule pas.
        self.annonce_imminente = annonce_imminente or (lambda _t: (False, ""))
        # Le plafond de spread de CET instrument : celui de l'EUR/USD refusait 92,8 % des
        # bougies du NAS100 (spread fixe de 70 points), le backtest mesurait le plafond.
        from ..noyau.instruments import limites_execution
        self.spread_max_points = limites_execution(cfg.execution, specs.nom, specs.point)[0]

    # ------------------------------------------------------------------ #
    def lancer(self, barres: Barres, capital_initial: float,
               *, echauffement: int = 200) -> Resultat:
        self.strategie.preparer(barres)

        res = Resultat(capital_initial=capital_initial)
        etat_profil = profils.initialiser(self.cfg.profil.actif, capital_initial)
        equite = capital_initial
        sommet = capital_initial
        position: Position | None = None

        pertes_consecutives = 0
        derniere_perte: datetime | None = None
        pause_jusqu_a: datetime | None = None
        pnl_jour = pnl_semaine = pnl_mois = 0.0
        jour = semaine = mois = None
        trades_jour = trades_semaine = 0
        arret_total = False

        heures_barre = HEURES_PAR_TF.get(barres.timeframe or "H4", 4)
        n = len(barres)

        for i in range(echauffement, n - 1):
            quand = barres.quand(i)

            # --- bascule des périodes --------------------------------------
            if jour != quand.date():
                jour, pnl_jour, trades_jour = quand.date(), 0.0, 0
            iso = quand.isocalendar()[:2]
            if semaine != iso:
                semaine, pnl_semaine, trades_semaine = iso, 0.0, 0
            if mois != (quand.year, quand.month):
                mois, pnl_mois = (quand.year, quand.month), 0.0

            # --- 1. gérer la position ouverte PENDANT la barre i ------------
            if position is not None:
                ferme = self._gerer(position, barres, i, heures_barre)
                if ferme is not None:
                    trade, prix_sortie = ferme
                    equite += trade.resultat_devise
                    sommet = max(sommet, equite)
                    pnl_jour += trade.resultat_devise
                    pnl_semaine += trade.resultat_devise
                    pnl_mois += trade.resultat_devise
                    if trade.resultat_devise <= 0:
                        pertes_consecutives += 1
                        derniere_perte = trade.sortie_le
                        # Le disjoncteur de série noire doit se RÉARMER.
                        # Sans ça il se verrouille pour toujours : le compteur
                        # ne retombe que sur un gain, et aucun gain n'est
                        # possible tant que les entrées sont bloquées. En
                        # production, ça se voit comme « le bot ne trade plus »
                        # et rien ne dit pourquoi.
                        if pertes_consecutives >= self.cfg.circuits.pertes_consecutives_max:
                            pause_jusqu_a = trade.sortie_le + timedelta(
                                hours=self.cfg.circuits.pause_apres_serie_heures)
                            pertes_consecutives = 0
                            res.refus.append((
                                trade.sortie_le,
                                f"pause {self.cfg.circuits.pause_apres_serie_heures} h "
                                f"après série noire"))
                    else:
                        pertes_consecutives = 0
                    res.trades.append(trade)
                    res.courbe_equite.append((trade.sortie_le, equite))
                    position = None

                    dd = 100 * (sommet - equite) / sommet if sommet else 0.0
                    if dd >= self.cfg.circuits.drawdown_max_total_pct:
                        arret_total = True
                        res.refus.append((trade.sortie_le,
                                          f"ARRÊT TOTAL : drawdown {dd:.1f} %"))

            if arret_total:
                continue

            # --- 2. chercher un signal sur la barre CLOSE i -----------------
            if position is not None:
                continue

            # Mêmes règles que l'agent : la poche épargne sort du capital de travail,
            # le palier fixe le risque du trade.
            profils.mettre_a_l_abri(self.cfg, etat_profil, equite)
            capital = self.cfg.compte.capital_effectif(profils.capital_disponible(equite, etat_profil))
            risque_du_palier, _ = profils.risque_courant(self.cfg, etat_profil, equite)
            ctx = self._contexte(barres, i, quand)
            if ctx is None:
                continue

            plan = self.strategie.signal(ctx)
            if plan is None:
                continue
            res.signaux_proposes += 1

            # Disjoncteurs de période : ils passent AVANT les verrous, parce
            # qu'ils ne discutent pas du trade, ils ferment la boutique.
            frein = self._disjoncteur(capital, pnl_jour, pnl_semaine, pnl_mois)
            if frein:
                if self.journaliser_refus:
                    res.refus.append((quand, frein))
                continue

            en_pause = pause_jusqu_a is not None and quand < pause_jusqu_a
            etat = EtatSysteme(
                en_pause=en_pause,
                motif_pause=(f"série noire, reprise à {pause_jusqu_a:%Y-%m-%d %H:%M}"
                             if en_pause else ""),
                spread_points=self._spread(barres, i),
                spread_habituel_points=self.couts.spread_points,
                spread_max_points=self.spread_max_points,
                atr_courant=ctx.atr,
                pertes_consecutives=pertes_consecutives,
                minutes_depuis_derniere_perte=(
                    (quand - derniere_perte).total_seconds() / 60
                    if derniere_perte else None),
                trades_aujourdhui=trades_jour,
                trades_cette_semaine=trades_semaine,
                drawdown_courant_pct=100 * (sommet - equite) / sommet if sommet else 0.0,
                regime=ctx.regime,
                regimes_favorables=("tendance", "range", "inconnu")
                if self.strategie.regime_favorable(ctx) else ("aucun",),
            )

            # L'heure qui compte pour les verrous est celle de l'ENTRÉE (ouverture
            # de la barre suivante), pas l'ouverture de la barre du signal : en H4
            # l'écart est de quatre heures, assez pour qu'une entrée à 00 h passe
            # le filtre des heures creuses asiatiques en se faisant dater de 20 h.
            entree_le = barres.quand(i + 1)
            verdict = controle_prealable(
                plan, self.cfg, etat, capital=capital, specs=self.specs,
                annonce_imminente=self.annonce_imminente,
                maintenant=entree_le,
                risque_pct_plafond=self.cfg.risque.risque_max_petit_compte_pct,
                risque_pct=risque_du_palier)

            if not verdict.autorise:
                if self.journaliser_refus:
                    for v in verdict.refus:
                        res.refus.append((quand, f"Q{v.numero} {v.question}"))
                continue

            # --- 3. entrer à l'OUVERTURE de la barre i+1 --------------------
            position = self._ouvrir(plan, verdict.dimensionnement.lots,
                                    barres, i + 1)
            trades_jour += 1
            trades_semaine += 1

        # Une position encore ouverte à la fin n'est PAS un gain : on la ferme
        # au dernier prix connu, sinon le backtest s'offre un trade suspendu.
        if position is not None:
            trade = self._fermer(position, barres, n - 1,
                                 barres.cloture[n - 1], "fin de données")
            equite += trade.resultat_devise
            res.trades.append(trade)
            res.courbe_equite.append((trade.sortie_le, equite))

        res.barres_vues = max(0, n - 1 - echauffement)
        res.verrouille, res.mises_a_l_abri = etat_profil.verrouille, etat_profil.mises_a_l_abri
        res.metriques = calculer(res.trades, capital_initial=capital_initial,
                                 courbe_equite=res.courbe_equite)
        return res

    # ------------------------------------------------------------------ #
    def _contexte(self, barres: Barres, i: int, quand: datetime):
        atr = getattr(self.strategie, "_atr", None)
        if atr is None or np.isnan(atr[i]) or atr[i] <= 0:
            return None
        regime = getattr(self.strategie, "regime_a", lambda _i: "inconnu")(i)
        return ContexteStrategie(i=i, barres=barres, atr=float(atr[i]),
                                 regime=regime, maintenant=quand)

    def _spread(self, barres: Barres, i: int) -> float:
        """Le spread de cette barre-là, si le courtier l'a fourni."""
        if barres.spread is not None and not np.isnan(barres.spread[i]):
            return float(barres.spread[i])
        return self.couts.spread_points

    def _disjoncteur(self, capital, pnl_jour, pnl_semaine, pnl_mois) -> str | None:
        c = self.cfg.circuits
        for pnl, seuil, nom in ((pnl_jour, c.perte_max_jour_pct, "jour"),
                                (pnl_semaine, c.perte_max_semaine_pct, "semaine"),
                                (pnl_mois, c.perte_max_mois_pct, "mois")):
            if capital > 0 and pnl < 0 and (100 * abs(pnl) / capital) >= seuil:
                return f"disjoncteur {nom} : -{100 * abs(pnl) / capital:.1f} %"
        return None

    # ------------------------------------------------------------------ #
    def _ouvrir(self, plan: PlanDeTrade, lots: float, barres: Barres,
                i: int) -> Position:
        """Entrée au prix d'OUVERTURE de la barre i, coûts compris."""
        theorique = float(barres.ouverture[i])
        prix = self.couts.prix_entree(sens=plan.sens, prix_theorique=theorique,
                                      specs=self.specs)
        # Le stop et l'objectif gardent leur distance au prix RÉELLEMENT obtenu :
        # le glissement décale la position, il ne change pas le risque voulu.
        signe = 1 if plan.sens == ACHAT else -1
        risque_prix = plan.risque_prix
        return Position(
            plan=plan, lots=lots, prix_entree=prix,
            stop=prix - signe * risque_prix,
            objectif=prix + signe * plan.gain_prix,
            ouverte_le=barres.quand(i), barre_entree=i,
            risque_prix=risque_prix,
            cout_entree=(self.couts.spread_points / 2 + self.couts.slippage_points)
            * lots * self.specs.valeur_point_par_lot
            + self.couts.commission_par_lot_par_sens * lots,
        )

    def _gerer(self, pos: Position, barres: Barres, i: int,
               heures_barre: float) -> tuple[TradeFerme, float] | None:
        """Que devient la position pendant la barre i ?"""
        haut, bas = float(barres.haut[i]), float(barres.bas[i])
        ouverture = float(barres.ouverture[i])
        quand = barres.quand(i)
        long = pos.plan.sens == ACHAT

        # --- Gap : un stop est une instruction, pas une garantie ------------
        if (long and ouverture <= pos.stop) or (not long and ouverture >= pos.stop):
            return (self._fermer(pos, barres, i, ouverture, "stop (gap)"), ouverture)

        touche_stop = bas <= pos.stop if long else haut >= pos.stop
        touche_objectif = haut >= pos.objectif if long else bas <= pos.objectif

        # --- Hypothèse pessimiste : le stop d'abord -------------------------
        if touche_stop:
            return (self._fermer(pos, barres, i, pos.stop, "stop"), pos.stop)
        if touche_objectif:
            return (self._fermer(pos, barres, i, pos.objectif, "objectif"), pos.objectif)

        # --- Suiveur : seulement après 1R encaissé, jamais élargi -----------
        r = self.cfg.risque
        if r.trailing_actif:
            extreme = haut if long else bas
            avance_R = (extreme - pos.prix_entree) / pos.risque_prix if long \
                else (pos.prix_entree - extreme) / pos.risque_prix
            if avance_R >= r.trailing_declenche_a_r:
                atr = getattr(self.strategie, "_atr", None)
                if atr is not None and not np.isnan(atr[i]):
                    marge = r.trailing_atr_multiple * float(atr[i])
                    propose = extreme - marge if long else extreme + marge
                    ok, _ = deplacement_de_stop_autorise(
                        sens=pos.plan.sens, stop_actuel=pos.stop, stop_propose=propose)
                    if ok:
                        pos.stop = propose
                        pos.stop_deplace = True

        # --- Stop temporel --------------------------------------------------
        barres_tenues = i - pos.barre_entree
        limite = self.cfg.discipline.stop_temporel_barres
        if limite and barres_tenues >= limite:
            return (self._fermer(pos, barres, i, float(barres.cloture[i]), "temporel"),
                    float(barres.cloture[i]))

        # --- Fermeture avant le week-end ------------------------------------
        # On regarde la FIN de la barre, pas son ouverture. En H4 la dernière
        # barre du vendredi ouvre à 20 h 00 : comparer son ouverture au seuil de
        # 20 h 30 ne déclenchait JAMAIS la fermeture, et les positions
        # traversaient le week-end que la règle devait leur éviter.
        cal = self.cfg.calendrier
        fin_barre = quand + timedelta(hours=heures_barre)
        if cal.fermer_avant_weekend and quand.weekday() == 4 and (
                fin_barre.time() >= cal.vendredi_tout_fermer
                or fin_barre.date() > quand.date()):
            return (self._fermer(pos, barres, i, float(barres.cloture[i]), "week-end"),
                    float(barres.cloture[i]))

        # --- Portage --------------------------------------------------------
        if heures_barre >= 24 or quand.hour == 0:
            pos.nuits += 1
        return None

    def _fermer(self, pos: Position, barres: Barres, i: int,
                prix_theorique: float, motif: str) -> TradeFerme:
        prix = self.couts.prix_sortie(sens=pos.plan.sens,
                                      prix_theorique=prix_theorique, specs=self.specs)
        signe = 1 if pos.plan.sens == ACHAT else -1
        brut = signe * (prix - pos.prix_entree) * pos.lots \
            / self.specs.point * self.specs.valeur_point_par_lot

        cout_sortie = ((self.couts.spread_points / 2 + self.couts.slippage_points)
                       * pos.lots * self.specs.valeur_point_par_lot
                       + self.couts.commission_par_lot_par_sens * pos.lots)
        portage = self.couts.portage_devise(sens=pos.plan.sens, lots=pos.lots,
                                            nuits=pos.nuits, specs=self.specs)
        cout_total = pos.cout_entree + cout_sortie - min(portage, 0.0)
        net = brut + portage

        risque_devise = pos.risque_prix / self.specs.point * pos.lots \
            * self.specs.valeur_point_par_lot

        return TradeFerme(
            entree_le=pos.ouverte_le, sortie_le=barres.quand(i),
            sens=pos.plan.sens, prix_entree=pos.prix_entree, prix_sortie=prix,
            stop_initial=pos.plan.stop, objectif=pos.objectif, lots=pos.lots,
            resultat_devise=net,
            resultat_R=net / risque_devise if risque_devise else 0.0,
            cout_devise=cout_total, motif_sortie=motif,
            these=pos.plan.these, strategie=pos.plan.strategie,
            contexte=dict(pos.plan.contexte, stop_deplace=pos.stop_deplace,
                          nuits=pos.nuits),
        )
