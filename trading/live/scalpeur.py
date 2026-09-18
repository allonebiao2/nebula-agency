# -*- coding: utf-8 -*-
"""
L'agent LE REFLUX : il pose des ordres LIMITES en M1, tout seul, et ferme avant la nuit.

    python -m trading.live.scalpeur --marche NAS100                 # observe : il décide, n'envoie RIEN
    python -m trading.live.scalpeur --marche NAS100 --ordres        # envoie ses ordres (compte démo)
    python -m trading.live.scalpeur --marche EURUSD --ordres --capital-fictif 10

**Un seul code décide, ici comme dans le test d'un an** : `live/moteur_scalp.py` (quels ordres
attendent, lequel est armé pour la minute qui vient) et `recherche/rejeu.py` s'en servent tous les
deux. Chaque minute close :
  1. fin de journée → annuler l'ordre posé chez le courtier, fermer la position, vider l'attente ;
  2. une position ouverte → rien de neuf (stop et objectif sont chez le courtier) ;
  3. sinon : ranger les ordres candidats (`Attente.nettoyer`), ajouter celui de la barre, demander
     au filtre sa probabilité **sur la barre qui vient de se fermer** ; s'il dit oui, **un seul**
     ordre est armé chez le courtier pour la minute suivante, sinon il est RETIRÉ.
Et à chaque passage (toutes les quelques secondes), il réconcilie avec le courtier : un ordre servi
devient un trade noté, un trade fermé reçoit son résultat, sa fiche et une ligne au carnet.

⛔ **Rien ne part sans `execution.autorisation`** : en mode « demo » de la configuration, aucun ordre
sur un compte RÉEL ; en mode « reel », la porte démo, le plafond de capital et la licence. C'est ce
qui manquait à la première version de ce fichier (2026-09-18) : avec son drapeau, elle aurait
tradé n'importe quel compte branché.
⚠️ **20 000 minutes de contexte, pas 6 000** : mesuré par `recherche/_qc_parite.py`, une fenêtre de
6 000 minutes donne des caractéristiques qui s'écartent de 3,7 % de celles de l'apprentissage.
⚠️ **Le coût minute par minute est celui du backtest** (`banc._couts_par_barre`) : deux des 38
caractéristiques (`spread_points`, `cout_R_atr14x2`) en dépendent.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from ..noyau import profils
from ..noyau.config import charger
from ..noyau.courtier import Courtier
from ..noyau.donnees_mt5 import dernieres_barres, specs_et_couts
from ..noyau.risque import dimensionner
from ..recherche import banc, candidates_v2
from ..recherche import modele as mod_modele
from ..recherche.candidat import REGLAGES
from ..recherche.caracteristiques import ECHAUFFEMENT, construire_aux_barres
from ..recherche.compte import _config_echelle
from ..recherche.intraday import minutes_et_jours
from ..recherche.lancer import DOSSIER
from . import moteur_scalp as ms
from .execution import Executeur, autorisation
from .journal import Journal

BARRES_CONTEXTE = ECHAUFFEMENT + 1_500      # l'échauffement mesuré + de quoi reconstruire l'attente
MAGIC = 770018                  # le numéro de cet agent chez le courtier, distinct de l'agent H4
ECHELLE = ((0.0, 6.0), (0.0001, 4.0), (0.20, 3.0))
NOTES = DOSSIER / "direct"


@dataclass
class Arme:
    ordre: ms.OrdreVirtuel
    ticket: int | None
    lots: float
    proba: float
    seuil: float
    barre: str
    caracteristiques: dict
    risque_pct: float
    drawdown: float
    risque_usd: float
    levier: float


def serie_directe(barres, base: str, specs, couts) -> banc.Serie:
    """La `Serie` du banc, construite depuis les barres du courtier, AVEC le coût minute par minute du
    backtest. C'est volontairement le même objet : les caractéristiques sont alors calculées par le
    même code, sur la même forme de données."""
    cout_median = couts.spread_points / 2 + couts.slippage_points
    cout_bar = banc._couts_par_barre(base, barres.temps, specs.point, couts, 1.0, None, "deriv",
                                     barres.cloture)
    jours = barres.temps.astype("datetime64[D]")
    nouveau = np.concatenate(([False], jours[1:] != jours[:-1]))
    jeudi = (jours.astype("int64") + 3) % 7 == 3
    poids = np.where(nouveau, np.where(jeudi, 3.0, 1.0), 0.0)
    vol = getattr(barres, "volume", None)
    return banc.Serie(base=base, tf="M1", temps=barres.temps, ouverture=barres.ouverture,
                      haut=barres.haut, bas=barres.bas, cloture=barres.cloture, point=specs.point,
                      cout_sens_pts=cout_median, swap_long_pts=0.0, swap_court_pts=0.0,
                      nuits_cumul=np.cumsum(poids),
                      stop_min_prix=max(float(specs.stops_level_points or 0), 4 * cout_median) * specs.point,
                      cout_bar_prix=cout_bar, source="direct",
                      volume=None if vol is None or not len(vol) else np.asarray(vol, float))


class Scalpeur:
    def __init__(self, marche: str = "NAS100", envoyer: bool = False, profil: str = "defaut",
                 capital_fictif: float | None = None, levier_max: float | None = 30.0):
        self.marche = marche.upper()
        self.envoyer = envoyer
        self.profil_courtier = profil
        self.levier_max = levier_max
        self.journal = Journal()
        self.modele, self.fiche = mod_modele.charger(self.marche)
        if self.modele is None:
            raise SystemExit(f"aucun modèle pour {self.marche} : "
                             f"python -m trading.recherche.modele --marche {self.marche} --entrainer")
        self.cfg_plan = _config_echelle(None, ECHELLE[0][1], ECHELLE)
        self.capital_fictif = capital_fictif
        self.etat_profil = None
        self.derniere_barre = None
        self.attente = ms.Attente()
        self.arme: Arme | None = None
        self.en_position: dict | None = None
        self.decalage_pose = 0            # indice de barre → numéro absolu (les fenêtres glissent)
        NOTES.mkdir(parents=True, exist_ok=True)
        self.fichier_notes = NOTES / f"{self.marche}.jsonl"
        self.fichier_compteurs = NOTES / f"{self.marche}_compteurs.json"
        self.compteurs = (json.loads(self.fichier_compteurs.read_text(encoding="utf-8"))
                          if self.fichier_compteurs.exists() else
                          {"ordres_armes": 0, "remplis": 0, "retires_par_le_filtre": 0,
                           "refus_taille": 0, "equite_fictive": capital_fictif})
        if capital_fictif and not self.compteurs.get("equite_fictive"):
            self.compteurs["equite_fictive"] = capital_fictif

    # ------------------------------------------------------------------ #
    def _sauver_compteurs(self) -> None:
        self.fichier_compteurs.write_text(json.dumps(self.compteurs, ensure_ascii=False), encoding="utf-8")

    def _equite(self, compte) -> float:
        """Le capital qui dimensionne : le compte, ou un compte FICTIF de N $ nourri par les
        résultats réels de l'agent (pour essayer le plan de 10 $ sur un compte démo de 10 000 $)."""
        if self.capital_fictif:
            return float(self.compteurs["equite_fictive"])
        return float(compte.equity)

    def _mode(self) -> tuple[bool, str]:
        """Ce fichier n'envoie un ordre que si `autorisation` le permet, sur CE compte, maintenant."""
        if not self.envoyer:
            return False, "observation : l'agent décide et journalise, il n'envoie rien"
        cfg = charger()
        p = self.courtier.profil()
        return autorisation(cfg.compte.mode, compte_demo=p.demo, mode_config=cfg.compte.mode,
                            capital_max_engage=cfg.compte.capital_max_engage, licence_valide=False,
                            porte_demo_franchie=False)

    # ------------------------------------------------------------------ #
    def _retirer_ordre(self, executeur, motif: str) -> None:
        for o in executeur.ordres_en_attente():
            r = executeur.annuler(o.ticket)
            self.journal.evenement("scalpeur", f"ordre {o.ticket} retiré : {motif} "
                                               f"({'ok' if r.ok else r.message})")
        self.arme = None

    def _reconcilier(self, executeur, specs) -> None:
        """Ce que le courtier a fait depuis le dernier passage : un ordre servi, un trade fermé."""
        positions = executeur.positions()
        if positions and self.en_position is None:
            p = positions[0]
            a = self.arme
            self.en_position = {
                "ticket": p.ticket, "marche": self.marche, "sens": 1 if p.type == 0 else -1,
                "rempli_a": datetime.fromtimestamp(p.time, timezone.utc).isoformat(timespec="minutes"),
                "prix_rempli": p.price_open, "stop": p.sl, "cible": p.tp, "lots": p.volume,
                "limite": a.ordre.limite if a else None,
                "glissement_points": (round((p.price_open - a.ordre.limite) / specs.point
                                            * (1 if p.type == 0 else -1), 1) if a else None),
                "proba": a.proba if a else None, "seuil": a.seuil if a else None,
                "arme_a": a.barre if a else None, "risque_pct_palier": a.risque_pct if a else None,
                "drawdown_avant_pct": round(100 * a.drawdown, 2) if a else None,
                "risque_usd": a.risque_usd if a else None, "levier": a.levier if a else None,
                "caracteristiques": a.caracteristiques if a else {}}
            self.compteurs["remplis"] += 1
            self._sauver_compteurs()
            self.journal.ordre(action="rempli", ticket=p.ticket, sens="achat" if p.type == 0 else "vente",
                               lots=p.volume, prix=p.price_open, sl=p.sl, tp=p.tp, retcode=0,
                               commentaire="LE REFLUX", mode="demo")
            self._ecrire_trade_ouvert(p, a)
            self.attente.vider()
            for o in executeur.ordres_en_attente():           # une seule position à la fois
                executeur.annuler(o.ticket)
            self.arme = None
        elif not positions and self.en_position is not None:
            t = self.en_position
            bilan = executeur.bilan_position_fermee(t["ticket"])
            if bilan is None:
                return                                        # l'historique n'est pas encore là
            risque = t.get("risque_usd") or abs(t["prix_rempli"] - t["stop"]) / specs.point \
                * specs.valeur_point_par_lot * t["lots"]
            R = bilan["resultat"] / risque if risque else 0.0
            t.update({"sortie_a": datetime.fromtimestamp(bilan["ferme_le"], timezone.utc)
                      .isoformat(timespec="minutes"), "prix_sortie": bilan["prix"],
                      "motif": bilan["motif"], "pnl_usd": round(bilan["resultat"], 4), "R": round(R, 4)})
            if self.capital_fictif:
                # Le compte fictif prend le résultat EN R, au risque qu'il aurait engagé lui-même.
                self.compteurs["equite_fictive"] = round(
                    float(self.compteurs["equite_fictive"]) * (1 + R * (t.get("risque_pct_palier") or 0) / 100), 4)
                t["equite_fictive_apres"] = self.compteurs["equite_fictive"]
            self.journal.fermer_trade(ticket=t["ticket"], prix=bilan["prix"], resultat=bilan["resultat"],
                                      motif=bilan["motif"])
            with open(self.fichier_notes, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(t, ensure_ascii=False, default=str) + "\n")
            self._sauver_compteurs()
            self.en_position = None
            try:
                from ..recherche import suivi
                suivi.ecrire(self.marche)
            except Exception as exc:                                     # noqa: BLE001
                self.journal.evenement("scalpeur", f"carnet non régénéré : {exc}", niveau="alerte")

    def _ecrire_trade_ouvert(self, p, a: Arme | None) -> None:
        class _Plan:                                         # la forme qu'attend `Journal.ouvrir_trade`
            strategie = "LE REFLUX"
            sens = "achat" if p.type == 0 else "vente"
            stop, objectif = p.sl, p.tp
            these = (f"filtre {a.proba:.3f} ≥ {a.seuil:.3f}, ordre posé {a.ordre.pose} "
                     f"à {a.ordre.limite}" if a else "ordre retrouvé chez le courtier")
            contexte = {"proba": a.proba if a else None}
            symbole = self.symbole
        self.journal.ouvrir_trade(ticket=p.ticket, plan=_Plan, lots=p.volume, prix=p.price_open,
                                  risque_devise=a.risque_usd if a else 0.0,
                                  mode="demo" if self.envoyer else "observation", profil="plan 6-4-3")

    # ------------------------------------------------------------------ #
    def cycle(self, executeur, specs, couts) -> dict:
        import MetaTrader5 as mt5
        if self.envoyer:
            self._reconcilier(executeur, specs)
        barres = dernieres_barres(self.symbole, "M1", BARRES_CONTEXTE)
        derniere = barres.temps[-1]
        if self.derniere_barre is not None and derniere <= self.derniere_barre:
            return {}
        premiere_fois = self.derniere_barre is None
        self.derniere_barre = derniere
        serie = serie_directe(barres, self.marche, specs, couts)
        n = len(serie)
        j = n - 1
        ordres = candidates_v2.rabais(serie, **REGLAGES)
        idx = ms.index_des_ordres(ordres, n)
        sens = ms.sens_par_barre(ordres, n)
        # Les indices de barre glissent avec la fenêtre : on repère un ordre par l'heure de sa barre.
        base_abs = int(serie.temps[0].astype("datetime64[m]").astype("int64"))
        compte = mt5.account_info()
        if compte is None:
            return {"etat": "compte illisible"}
        equite = self._equite(compte)
        if self.etat_profil is None:
            self.etat_profil = profils.initialiser("plan", equite)
        profils.maj_sommet(self.etat_profil, equite)

        def absolu(o: ms.OrdreVirtuel) -> ms.OrdreVirtuel:
            d = base_abs
            return ms.OrdreVirtuel(o.pose + d, o.sens, o.limite, o.stop, o.cible, o.expire + d)

        j_abs = j + base_abs
        if premiere_fois:
            # Reconstruire l'attente des 60 dernières minutes, comme si l'agent avait tourné.
            for k in range(max(0, j - 61), j):
                if ordres.fin_seance[k]:
                    self.attente.vider()
                    continue
                self.attente.nettoyer(k + base_abs, serie.haut[k], serie.bas[k], int(sens[k]))
                o = ms.ordre_de_la_barre(ordres, idx, k, serie.stop_min_prix)
                if o is not None:
                    self.attente.poser(absolu(o))

        if ordres.fin_seance[j]:
            self.attente.vider()
            if self.envoyer:
                self._retirer_ordre(executeur, "fin de journée")
                for p in executeur.positions():
                    r = executeur.fermer(p, motif="fin de journée")
                    self.journal.evenement("scalpeur", f"fin de journée : position {p.ticket} fermée "
                                                       f"({'ok' if r.ok else r.message})")
            return {"etat": "journée fermée"}
        if self.en_position is not None:
            return {"etat": "position ouverte", "ticket": self.en_position["ticket"]}

        self.attente.nettoyer(j_abs, serie.haut[j], serie.bas[j], int(sens[j]))
        o = ms.ordre_de_la_barre(ordres, idx, j, serie.stop_min_prix)
        if o is not None:
            self.attente.poser(absolu(o))
        meilleur = self.attente.meilleur()
        X, noms = construire_aux_barres(serie, np.array([j]))
        if noms != self.fiche["caracteristiques"]:
            raise RuntimeError("les caractéristiques calculées ne sont pas celles du modèle")
        proba = (float(self.modele.predict_proba(X)[0, 1]) if np.isfinite(X).all() else float("nan"))
        seuil = float(self.fiche["seuil"])
        if meilleur is None or not ms.arme(proba, seuil):
            if self.arme is not None and self.envoyer:
                self._retirer_ordre(executeur, f"le filtre ne dit plus oui (p={proba:.3f})")
                self.compteurs["retires_par_le_filtre"] += 1
                self._sauver_compteurs()
            self.arme = None
            motif = "aucun ordre en attente" if meilleur is None else f"p={proba:.3f} < {seuil:.3f}"
            return {"etat": "rien d'armé", "motif": motif, "attente": len(self.attente.ordres)}

        risque_pct, _ = profils.risque_courant(self.cfg_plan, self.etat_profil, equite)
        dd = profils.drawdown_courant(self.etat_profil, equite)
        taille = dimensionner(capital=equite, risque_pct=risque_pct,
                              points_de_risque=meilleur.risque / specs.point, specs=specs,
                              lots_total_max=specs.volume_max * 10, prix=meilleur.limite,
                              levier_max=self.levier_max)
        if not taille.autorise:
            self.compteurs["refus_taille"] += 1
            self._sauver_compteurs()
            if self.envoyer:
                self._retirer_ordre(executeur, "taille refusée")
            return {"etat": "taille refusée", "motif": taille.raison.splitlines()[0]}

        carac = {nm: (None if not np.isfinite(v) else round(float(v), 5)) for nm, v in zip(noms, X[0])}
        nouvel = Arme(meilleur, None, taille.lots, round(proba, 4), round(seuil, 4),
                      str(serie.temps[j])[:16], carac, risque_pct, dd, round(taille.risque_devise, 4),
                      round(taille.levier, 1))
        peut, raison = self._mode()
        if not peut:
            self.arme = nouvel
            self.journal.decision(verdict="observation", motif=f"armé : p={proba:.3f}",
                                  sens="achat" if meilleur.sens > 0 else "vente", entree=meilleur.limite,
                                  stop=meilleur.stop, objectif=meilleur.cible, lots=taille.lots,
                                  risque_pct=risque_pct, risque_devise=taille.risque_devise,
                                  mode="observation", note=raison)
            return {"etat": "armé (non envoyé)", "raison": raison, "proba": round(proba, 3),
                    "limite": meilleur.limite, "lots": taille.lots}

        # Déjà posé, identique ? On le laisse. Sinon on remplace.
        if (self.arme and self.arme.ticket and self.arme.ordre.pose == meilleur.pose
                and abs(self.arme.lots - taille.lots) < 1e-9
                and any(x.ticket == self.arme.ticket for x in executeur.ordres_en_attente())):
            self.arme.proba, self.arme.barre, self.arme.caracteristiques = nouvel.proba, nouvel.barre, carac
            return {"etat": "ordre maintenu", "ticket": self.arme.ticket, "proba": round(proba, 3)}
        self._retirer_ordre(executeur, "remplacé par un meilleur ordre")
        expire = datetime.now(timezone.utc) + timedelta(minutes=max(1, meilleur.expire - j_abs))
        tick = mt5.symbol_info_tick(self.symbole)
        achat = meilleur.sens > 0
        marche_deja_passe = tick is not None and ((achat and tick.ask <= meilleur.limite)
                                                  or (not achat and tick.bid >= meilleur.limite))
        if marche_deja_passe:
            # Le prix est déjà au-delà de la limite : un ordre au repos serait servi tout de suite, au
            # prix du marché. Le rejeu fait pareil (servi à l'ouverture, mieux que la limite).
            r = executeur.ouvrir_niveaux(achat=achat, lots=taille.lots, stop=meilleur.stop,
                                         objectif=meilleur.cible, specs=specs, commentaire="nebula-reflux")
        else:
            r = executeur.poser_limite(achat=achat, lots=taille.lots, limite=meilleur.limite,
                                       stop=meilleur.stop, objectif=meilleur.cible, specs=specs,
                                       expire_le=expire, commentaire="nebula-reflux")
        self.journal.ordre(action="marche" if marche_deja_passe else "limite", ticket=r.ticket,
                           sens="achat" if achat else "vente", lots=taille.lots, prix=meilleur.limite,
                           sl=meilleur.stop, tp=meilleur.cible, retcode=r.retcode,
                           commentaire=r.message, mode="demo")
        if r.ok:
            nouvel.ticket = r.ticket
            self.arme = nouvel
            self.compteurs["ordres_armes"] += 1
            self._sauver_compteurs()
            if marche_deja_passe:
                self._reconcilier(executeur, specs)
        return {"etat": ("entré au marché" if marche_deja_passe else "ordre posé") if r.ok
                else f"refusé : {r.message}", "ticket": r.ticket, "proba": round(proba, 3),
                "lots": taille.lots, "risque_pct": risque_pct}

    # ------------------------------------------------------------------ #
    def tourner(self, secondes: float = 5.0, tours: int | None = None) -> None:
        with Courtier.depuis_profil(self.profil_courtier) as courtier:
            self.courtier = courtier
            self.symbole = courtier.trouver_symbole(self.marche)
            specs = courtier.specs(self.symbole)
            _, couts = specs_et_couts(self.marche)
            executeur = Executeur(self.symbole, MAGIC)
            peut, raison = self._mode()
            p = courtier.profil()
            self.journal.evenement("scalpeur", f"LE REFLUX démarre sur {self.symbole} · compte {p.login} "
                                               f"({'DÉMO' if p.demo else 'RÉEL'}) · modèle du "
                                               f"{self.fiche['entraine_le'][:16]} · seuil {self.fiche['seuil']:.3f}"
                                               f" · {'ORDRES' if peut else 'OBSERVATION'}")
            print(f"  LE REFLUX · {self.symbole} · compte {p.login} ({'DÉMO' if p.demo else 'RÉEL'}) · "
                  f"{'ordres envoyés' if peut else raison}", flush=True)
            if self.envoyer and not peut:
                print(f"  ⛔ {raison}", flush=True)
            n = 0
            while tours is None or n < tours:
                try:
                    etat = self.cycle(executeur, specs, couts)
                    if etat:
                        print(f"  {datetime.now():%H:%M:%S} · {etat}", flush=True)
                except Exception as exc:                                   # noqa: BLE001
                    self.journal.evenement("erreur", f"scalpeur : {exc}", niveau="alerte")
                    print(f"  erreur : {exc}", flush=True)
                n += 1
                if tours is None or n < tours:
                    time.sleep(secondes)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--ordres", action="store_true",
                    help="envoyer les ordres (seulement si `execution.autorisation` le permet)")
    ap.add_argument("--capital-fictif", type=float, help="dimensionner comme un compte de N $")
    ap.add_argument("--levier", type=float, default=30.0, help="plafond de levier effectif (0 = aucun)")
    ap.add_argument("--tours", type=int, help="nombre de passages (par défaut : sans fin)")
    ap.add_argument("--secondes", type=float, default=5.0)
    a = ap.parse_args()
    Scalpeur(a.marche, envoyer=a.ordres, capital_fictif=a.capital_fictif,
             levier_max=a.levier or None).tourner(a.secondes, a.tours)
    return 0


if __name__ == "__main__":
    sys.exit(main())
