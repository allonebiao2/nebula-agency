# -*- coding: utf-8 -*-
"""
Un compte de 10 000 $ qui prend les trades d'une stratégie, avec de VRAIES tailles de position.

Deux jeux de règles, toujours côte à côte :
  · « vidéo »       : ce que fait l'auteur. Risque fixe par trade, limites du courtier seulement
                      (lot min/max/pas, 1:1000). Aucun plafond de levier, aucun frein.
  · « NEBULA PRO »  : les verrous de l'agent (`config.toml`, profil actif) : levier effectif ×3,
                      0,50 lot au plus, 3 trades/jour et 8/semaine, 4 h d'attente après une perte,
                      -3 %/jour, -6 %/semaine, -10 %/mois, pause de 24 h après 6 pertes d'affilée,
                      arrêt total à -20 % du sommet, pas d'entrée en Asie creuse ni au rollover.

Le résultat d'un trade en dollars = R × le risque RÉELLEMENT engagé (lots arrondis vers le bas,
plafonds appliqués). R est déjà net de spread, glissement et swap : on ne recompte rien.
Taille calculée sur le capital RÉALISÉ au moment de l'entrée (les positions ouvertes sur l'autre
instrument ne comptent pas tant qu'elles ne sont pas fermées).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd

from ..noyau.risque import SpecsSymbole, dimensionner


@dataclass
class TradeCompte:
    base: str
    entree: datetime
    sortie: datetime
    sens: int
    R: float
    points_risque: float
    prix: float
    lots: float = 0.0
    risque_usd: float = 0.0
    pnl_usd: float = 0.0
    capital_avant: float = 0.0
    capital_apres: float = 0.0
    refuse: str = ""
    risque_pct_applique: float = 0.0    # le palier de l'échelle au moment de l'entrée
    drawdown_avant: float = 0.0         # à quelle distance du sommet on était


@dataclass
class ResultatCompte:
    regles: str
    risque_pct: float
    capital_initial: float
    trades: list = field(default_factory=list)          # pris ET refusés
    arret_total: str = ""

    @property
    def pris(self) -> list:
        return [t for t in self.trades if not t.refuse]

    def resume(self) -> dict:
        pris = sorted(self.pris, key=lambda t: t.sortie)      # le capital bouge à la SORTIE
        cap0 = self.capital_initial
        if not pris:
            return {"regles": self.regles, "risque_pct": self.risque_pct, "trades": 0,
                    "refuses": len(self.trades), "capital_final": cap0}
        pnl = np.array([t.pnl_usd for t in pris])
        R = np.array([t.R for t in pris])
        equite = cap0 + np.cumsum(pnl)
        sommets = np.maximum.accumulate(np.concatenate(([cap0], equite)))[1:]
        dd_usd = sommets - equite
        dd_pct = dd_usd / sommets * 100
        gagn = pnl > 0
        serie, pire = 0, 0
        for g in gagn:
            serie = 0 if g else serie + 1
            pire = max(pire, serie)
        debut, fin = pris[0].entree, pris[-1].sortie
        annees = max((fin - debut).days / 365.25, 1 / 12)
        final = float(equite[-1])
        df = pd.DataFrame({"mois": [t.sortie.strftime("%Y-%m") for t in pris], "pnl": pnl,
                           "annee": [t.sortie.year for t in pris]})
        par_mois = df.groupby("mois")["pnl"].sum()
        cap_mois = cap0 + par_mois.cumsum()
        rendement_mois = par_mois / (cap_mois - par_mois) * 100
        par_annee = df.groupby("annee")["pnl"].sum()
        cap_annee = cap0 + par_annee.cumsum()
        motifs_refus: dict[str, int] = {}
        for t in self.trades:
            if t.refuse:
                cle = t.refuse.split(" :")[0]
                motifs_refus[cle] = motifs_refus.get(cle, 0) + 1
        return {
            "regles": self.regles, "risque_pct": self.risque_pct, "capital_initial": cap0,
            "capital_final": round(final, 2), "benefice_usd": round(final - cap0, 2),
            "rendement_pct": round((final / cap0 - 1) * 100, 2),
            "rendement_annuel_pct": round(((max(final, 0.01) / cap0) ** (1 / annees) - 1) * 100, 2),
            "debut": debut.isoformat(timespec="minutes"), "fin": fin.isoformat(timespec="minutes"),
            "annees": round(annees, 2),
            "trades": len(pris), "refuses": len(self.trades) - len(pris), "motifs_refus": motifs_refus,
            "trades_par_mois": round(len(pris) / (annees * 12), 1),
            "taux_reussite": round(float(gagn.mean()), 4),
            "gain_moyen_usd": round(float(pnl[gagn].mean()), 2) if gagn.any() else 0.0,
            "perte_moyenne_usd": round(float(pnl[~gagn].mean()), 2) if (~gagn).any() else 0.0,
            "plus_gros_gain_usd": round(float(pnl.max()), 2), "plus_grosse_perte_usd": round(float(pnl.min()), 2),
            "profit_factor": round(float(pnl[gagn].sum() / -pnl[~gagn].sum()), 3) if (~gagn).any() and pnl[~gagn].sum() < 0 else None,
            "drawdown_max_pct": round(float(dd_pct.max()), 2), "drawdown_max_usd": round(float(dd_usd.max()), 2),
            "capital_min_usd": round(float(min(cap0, equite.min())), 2),
            "serie_perdante_max": int(pire),
            "risque_moyen_usd": round(float(np.mean([t.risque_usd for t in pris])), 2),
            "risque_moyen_pct": round(float(np.mean([t.risque_usd / t.capital_avant * 100 for t in pris])), 3),
            "lots_moyens": round(float(np.mean([t.lots for t in pris])), 3),
            "mois_positifs_pct": round(float((par_mois > 0).mean() * 100), 1), "mois": int(len(par_mois)),
            "meilleur_mois_pct": round(float(rendement_mois.max()), 2), "pire_mois_pct": round(float(rendement_mois.min()), 2),
            "par_annee": {str(a): {"pnl_usd": round(float(p), 2),
                                   "rendement_pct": round(float(p / (cap_annee[a] - p) * 100), 2),
                                   "capital_fin": round(float(cap_annee[a]), 2)}
                          for a, p in par_annee.items()},
            "par_mois_pct": {m: round(float(v), 2) for m, v in rendement_mois.items()},
            "courbe": [[t.sortie.isoformat(timespec="minutes"), round(t.capital_apres, 2)] for t in pris],
            "arret_total": self.arret_total,
        }


def _dans(t: time, debut: time, fin: time) -> bool:
    return debut <= t <= fin if debut <= fin else (t >= debut or t <= fin)


def _config_echelle(cfg, risque_pct: float, echelle: tuple[tuple[float, float], ...]):
    """Une configuration minimale pour `profils.risque_courant` : le risque plein et l'échelle.

    On ne fabrique pas une deuxième logique de décision : on donne au code de l'agent ce dont il a
    besoin, et c'est lui qui décide. C'est la seule façon que la mesure et le compte disent pareil.
    """
    from dataclasses import replace
    from ..noyau.config import Profil, charger
    base = cfg or charger()
    profil = replace(base.profil, paliers_drawdown=tuple((float(s), float(r)) for s, r in echelle),
                     paliers_actifs=False, paliers=()) if isinstance(base.profil, Profil) else base.profil
    risque = replace(base.risque, risque_par_trade_pct=risque_pct)
    return replace(base, profil=profil, risque=risque)


def simuler_compte(trades: list[TradeCompte], specs: dict[str, SpecsSymbole], *, capital: float = 10_000.0,
                   risque_pct: float = 1.0, regles: str = "video", cfg=None,
                   echelle_drawdown: tuple[tuple[float, float], ...] | None = None) -> ResultatCompte:
    """`trades` : tous instruments mélangés, dans n'importe quel ordre (triés ici par entrée).

    `echelle_drawdown` : l'échelle du plan de Mongazi ((seuil, risque %), …). Le risque du trade est
    alors décidé par `noyau/profils.risque_courant`, **le même code que l'agent en direct**, à partir
    du capital réalisé et de son sommet. Sans échelle, le risque reste fixe : rien ne change pour les
    appelants existants.
    """
    from ..noyau import profils
    pro = regles == "pro"
    if pro and cfg is None:
        from ..noyau.config import charger
        cfg = charger()
    etat = profils.initialiser("plan", capital) if echelle_drawdown else None
    cfg_echelle = _config_echelle(cfg, risque_pct, echelle_drawdown) if echelle_drawdown else None
    res = ResultatCompte("NEBULA PRO" if pro else "vidéo", risque_pct, capital)
    realise = capital
    sommet = capital
    ouverts: list[TradeCompte] = []
    jour_cle = semaine_cle = mois_cle = None
    pnl_jour = pnl_sem = pnl_mois = 0.0
    cap_jour = cap_sem = cap_mois = capital
    n_jour = n_sem = 0
    derniere_perte: datetime | None = None
    pertes_affilee = 0
    pause_jusqu_a: datetime | None = None
    arrete = False

    def realiser(jusqu_a: datetime):
        nonlocal realise, sommet, pnl_jour, pnl_sem, pnl_mois, derniere_perte, pertes_affilee, pause_jusqu_a, arrete
        for t in sorted([t for t in ouverts if t.sortie <= jusqu_a], key=lambda x: x.sortie):
            ouverts.remove(t)
            realise += t.pnl_usd
            t.capital_apres = realise
            pnl_jour += t.pnl_usd
            pnl_sem += t.pnl_usd
            pnl_mois += t.pnl_usd
            sommet = max(sommet, realise)
            profils.maj_sommet(etat, realise)       # le « TOP » de l'échelle par drawdown
            if t.pnl_usd < 0:
                derniere_perte = t.sortie
                pertes_affilee += 1
                if pro and pertes_affilee >= cfg.circuits.pertes_consecutives_max:
                    pause_jusqu_a = t.sortie + timedelta(hours=cfg.circuits.pause_apres_serie_heures)
                    pertes_affilee = 0
            else:
                pertes_affilee = 0
            if pro and not arrete and (sommet - realise) / sommet * 100 >= cfg.circuits.drawdown_max_total_pct:
                arrete = True
                res.arret_total = (f"arrêt total le {t.sortie:%Y-%m-%d} : -{(sommet - realise) / sommet * 100:.1f} % ".replace(".", ",")
                                   + f"depuis le sommet de {sommet:,.0f} $".replace(",", " "))

    for t in sorted(trades, key=lambda x: x.entree):
        realiser(t.entree)
        res.trades.append(t)
        # compteurs de période (heure serveur = UTC)
        j, s, m = t.entree.date(), t.entree.isocalendar()[:2], (t.entree.year, t.entree.month)
        if j != jour_cle:
            jour_cle, pnl_jour, cap_jour, n_jour = j, 0.0, realise, 0
        if s != semaine_cle:
            semaine_cle, pnl_sem, cap_sem, n_sem = s, 0.0, realise, 0
        if m != mois_cle:
            mois_cle, pnl_mois, cap_mois = m, 0.0, realise
        if realise <= 0:
            t.refuse = "compte vide"
            continue
        if pro:
            h = t.entree.time()
            c = cfg.calendrier
            motif = ""
            if arrete:
                motif = "arrêt total"
            elif pause_jusqu_a and t.entree < pause_jusqu_a:
                motif = "pause après série perdante"
            elif c.eviter_asie_creuse and _dans(h, c.asie_debut, c.asie_fin):
                motif = "Asie creuse"
            elif c.eviter_rollover and _dans(h, c.rollover_debut, c.rollover_fin):
                motif = "rollover"
            elif n_jour >= cfg.discipline.trades_max_par_jour:
                motif = "3 trades par jour"
            elif n_sem >= cfg.discipline.trades_max_par_semaine:
                motif = "8 trades par semaine"
            elif derniere_perte and (t.entree - derniere_perte) < timedelta(minutes=cfg.discipline.refroidissement_apres_perte_minutes):
                motif = "attente après une perte"
            elif -pnl_jour / cap_jour * 100 >= cfg.circuits.perte_max_jour_pct:
                motif = "perte max du jour"
            elif -pnl_sem / cap_sem * 100 >= cfg.circuits.perte_max_semaine_pct:
                motif = "perte max de la semaine"
            elif -pnl_mois / cap_mois * 100 >= cfg.circuits.perte_max_mois_pct:
                motif = "perte max du mois"
            elif len(ouverts) >= cfg.exposition.positions_simultanees_max:
                motif = "positions simultanées"
            if motif:
                t.refuse = motif
                continue
        risque_trade = risque_pct
        if echelle_drawdown:
            risque_trade, _motif = profils.risque_courant(cfg_echelle, etat, realise)
            t.drawdown_avant = profils.drawdown_courant(etat, realise)
        t.risque_pct_applique = risque_trade
        d = dimensionner(capital=realise, risque_pct=risque_trade, points_de_risque=t.points_risque,
                         specs=specs[t.base],
                         lots_total_max=(cfg.exposition.lots_total_max if pro else specs[t.base].volume_max * 10),
                         lots_deja_ouverts=sum(o.lots for o in ouverts) if pro else 0.0,   # « tous ordres confondus »
                         prix=t.prix, levier_max=cfg.profil.levier_effectif_max if pro else None)
        if not d.autorise:
            t.refuse = "taille : " + d.raison.split("\n")[0]
            continue
        t.lots = d.lots
        t.risque_usd = d.risque_devise
        t.pnl_usd = t.R * d.risque_devise
        t.capital_avant = realise
        ouverts.append(t)
        n_jour += 1
        n_sem += 1
    realiser(datetime.max)
    return res


def depuis_sniper(base: str, serie, tr) -> list[TradeCompte]:
    temps = pd.DatetimeIndex(serie.temps)
    return [TradeCompte(base=base, entree=temps[tr.entree[k]].to_pydatetime(),
                        sortie=(temps[tr.sortie[k]] + pd.Timedelta(minutes=1)).to_pydatetime(),
                        sens=int(tr.sens[k]), R=float(tr.R[k]),
                        points_risque=float(tr.risque_prix[k] / serie.point), prix=float(tr.prix_entree[k]))
            for k in range(len(tr))]


def series_perdantes(R: np.ndarray, *, longueurs=(5, 6), fenetre: int = 100, tirages: int = 20_000,
                     graine: int = 7) -> dict:
    """Probabilité d'au moins une série de N pertes d'affilée dans 100 trades.
    Trois lectures : la vraie séquence (fenêtres glissantes de 100 trades), le Monte Carlo
    (trades tirés au hasard avec remise dans la distribution observée), et la plus longue observée."""
    perte = R <= 0
    sortie = {"trades": int(len(R)), "taux_pertes": round(float(perte.mean()), 4) if len(R) else None}
    serie, pire = 0, 0
    for p in perte:
        serie = serie + 1 if p else 0
        pire = max(pire, serie)
    sortie["plus_longue_observee"] = int(pire)
    rng = np.random.default_rng(graine)
    tirs = rng.random((tirages, fenetre)) < (perte.mean() if len(R) else 0)
    for n in longueurs:
        def a_une_serie(ligne):
            c = 0
            for x in ligne:
                c = c + 1 if x else 0
                if c >= n:
                    return True
            return False
        # Monte Carlo vectorisé : convolution des pertes consécutives
        noyau = np.ones(n, dtype=int)
        mc = float(np.mean([np.convolve(l_.astype(int), noyau, "valid").max() >= n for l_ in tirs]))
        reelles = None
        if len(R) >= fenetre:
            fen = [a_une_serie(perte[i:i + fenetre]) for i in range(0, len(R) - fenetre + 1)]
            reelles = round(float(np.mean(fen)), 4)
        sortie[f"p_{n}_pertes_sur_{fenetre}_montecarlo"] = round(mc, 4)
        sortie[f"p_{n}_pertes_sur_{fenetre}_sequence_reelle"] = reelles
    return sortie
