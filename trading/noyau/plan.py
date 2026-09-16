# -*- coding: utf-8 -*-
"""
Le plan de trade, et les verrous qui le contrôlent.

    « Une position sans plan écrit, c'est un pari, pas un trade. »

Chez un humain, ce principe se trahit un soir de fatigue. Ici il est structurel :
une stratégie ne renvoie pas « acheter ». Elle renvoie un PlanDeTrade complet,
ou rien. Un plan sans thèse, sans invalidation technique ou sans objectif ne
peut pas se construire — l'objet lève une exception.

Ensuite viennent les VERROUS : les six questions à se poser avant chaque
position, traduites en contrôles exécutés avant tout ordre. Pas de réponse, pas
d'ordre. Deux verrous de la maison s'y ajoutent (discipline et état du marché),
qui ne figuraient pas dans la liste d'origine et que l'expérience impose.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Callable

from .risque import Dimensionnement, SpecsSymbole

ACHAT, VENTE = "achat", "vente"

# Un plan doit dire quelque chose. Ces mots trahissent un gabarit non rempli.
_THESES_VIDES = {"", "-", "n/a", "na", "todo", "test", "signal", "trade",
                 "acheter", "vendre", "?", "rien"}


class PlanInvalide(Exception):
    """Le plan ne tient pas debout géométriquement. Il n'existe pas."""


# =============================================================================
#  Le plan
# =============================================================================

@dataclass(frozen=True)
class PlanDeTrade:
    """Tout ce qu'il faut savoir AVANT d'entrer. Rien ne s'ajoute après coup."""

    symbole: str
    sens: str                   # "achat" | "vente"
    entree: float
    stop: float                 # l'invalidation technique
    objectif: float
    these: str                  # la phrase qu'on pourrait expliquer à quelqu'un
    atr: float                  # volatilité au moment de la décision
    horodatage: datetime
    strategie: str = "inconnue"
    # Tout ce qui servira d'entrée au modèle, et de mémoire au journal.
    contexte: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sens not in (ACHAT, VENTE):
            raise PlanInvalide(f"sens {self.sens!r} : attendu {ACHAT!r} ou {VENTE!r}")

        for nom, val in (("entree", self.entree), ("stop", self.stop),
                         ("objectif", self.objectif)):
            if val is None or val <= 0:
                raise PlanInvalide(f"{nom} manquant ou invalide ({val!r})")

        if self.atr is None or self.atr <= 0:
            raise PlanInvalide("atr manquant : sans mesure de volatilité, le stop ne peut "
                               "pas être technique")

        these = (self.these or "").strip()
        if these.lower() in _THESES_VIDES or len(these) < 15:
            raise PlanInvalide(
                "thèse absente ou creuse. Il faut une phrase qu'on pourrait expliquer à "
                "quelqu'un — c'est elle qui, relue dans six mois, dira pourquoi ce trade "
                "a été pris.")
        if len(these) > 200:
            raise PlanInvalide(f"thèse de {len(these)} caractères : au-delà de 200, ce n'est "
                               f"plus une thèse, c'est un récit.")

        # Géométrie : le stop est du mauvais côté = la position est déjà perdue
        # au moment où elle s'ouvre. C'est une inversion de signe, pas une
        # opinion de marché, et elle doit être impossible.
        if self.sens == ACHAT:
            if self.stop >= self.entree:
                raise PlanInvalide(f"achat : stop ({self.stop}) au-dessus ou à l'entrée "
                                   f"({self.entree})")
            if self.objectif <= self.entree:
                raise PlanInvalide(f"achat : objectif ({self.objectif}) sous ou à l'entrée "
                                   f"({self.entree})")
        else:
            if self.stop <= self.entree:
                raise PlanInvalide(f"vente : stop ({self.stop}) sous ou à l'entrée "
                                   f"({self.entree})")
            if self.objectif >= self.entree:
                raise PlanInvalide(f"vente : objectif ({self.objectif}) au-dessus ou à "
                                   f"l'entrée ({self.entree})")

    # --- Géométrie ----------------------------------------------------------
    @property
    def signe(self) -> int:
        return 1 if self.sens == ACHAT else -1

    @property
    def risque_prix(self) -> float:
        return abs(self.entree - self.stop)

    @property
    def gain_prix(self) -> float:
        return abs(self.objectif - self.entree)

    @property
    def ratio_rr(self) -> float:
        return self.gain_prix / self.risque_prix if self.risque_prix else 0.0

    def risque_points(self, specs: SpecsSymbole) -> float:
        return self.risque_prix / specs.point

    def __str__(self) -> str:
        return (f"{self.sens.upper()} {self.symbole} @ {self.entree} · "
                f"stop {self.stop} · cible {self.objectif} · "
                f"R:R {self.ratio_rr:.2f} · « {self.these} »")


# =============================================================================
#  L'état du système — l'« émotion » d'une machine
# =============================================================================

@dataclass
class EtatSysteme:
    """L'équivalent machine de « quelle est mon émotion actuelle ? ».

    Un trader qui se sent mal passe son tour. Un bot n'a pas d'humeur, mais il a
    une dérive d'état — et elle se mesure.
    """
    spread_points: float = 0.0
    spread_habituel_points: float = 0.0
    atr_courant: float = 0.0
    atr_plage_connue: tuple[float, float] | None = None   # plage vue à l'entraînement
    pertes_consecutives: int = 0
    minutes_depuis_derniere_perte: float | None = None
    trades_aujourdhui: int = 0
    trades_cette_semaine: int = 0
    lots_deja_ouverts: float = 0.0
    exposition_courante_pct: float = 0.0
    drawdown_courant_pct: float = 0.0
    confiance_modele: float | None = None      # 0..1, None si pas de modèle
    regime: str | None = None
    regimes_favorables: tuple[str, ...] = ()
    en_pause: bool = False
    motif_pause: str = ""


# =============================================================================
#  Les verrous
# =============================================================================

@dataclass(frozen=True)
class Verrou:
    numero: int
    question: str
    passe: bool
    detail: str
    maison: bool = False        # True = ajouté par la maison, hors des 6 questions


@dataclass(frozen=True)
class Verdict:
    plan: PlanDeTrade | None
    verrous: list[Verrou]
    dimensionnement: Dimensionnement | None = None

    @property
    def autorise(self) -> bool:
        return bool(self.verrous) and all(v.passe for v in self.verrous)

    @property
    def refus(self) -> list[Verrou]:
        return [v for v in self.verrous if not v.passe]

    def rapport(self) -> str:
        lignes = []
        if self.plan:
            lignes += [str(self.plan), ""]
        for v in self.verrous:
            marque = "OK " if v.passe else "NON"
            etiquette = "maison" if v.maison else f"Q{v.numero}"
            lignes.append(f"  [{marque}] {etiquette:<7} {v.question}")
            if v.detail:
                lignes.append(f"            {v.detail}")
        verdict = "ORDRE AUTORISÉ" if self.autorise else f"ORDRE BLOQUÉ ({len(self.refus)} verrou(x))"
        lignes += ["", f"  ==> {verdict}"]
        return "\n".join(lignes)


def controle_prealable(
    plan: PlanDeTrade,
    cfg,
    etat: EtatSysteme,
    *,
    capital: float,
    specs: SpecsSymbole,
    dimensionnement: Dimensionnement | None = None,
    annonce_imminente: Callable[[datetime], tuple[bool, str]] | None = None,
    maintenant: datetime | None = None,
) -> Verdict:
    """Les six questions, plus deux verrous de la maison. Tout doit passer."""
    from .risque import dimensionner

    maintenant = maintenant or plan.horodatage
    v: list[Verrou] = []

    # --- Q1 : quelle est ma thèse ? -----------------------------------------
    # Le constructeur du plan l'a déjà imposée. Ici on la journalise : ce verrou
    # ne peut échouer que si un plan a été fabriqué en contournant la classe.
    v.append(Verrou(1, "Quelle est ma thèse ?", True, f"« {plan.these} »"))

    # --- Q2 : où est mon invalidation technique ? ---------------------------
    attendu = cfg.risque.stop_loss_atr_multiple * plan.atr
    rapport = plan.risque_prix / attendu if attendu else 0.0
    if rapport < 0.5:
        v.append(Verrou(2, "Où est mon invalidation technique ?", False,
                        f"stop à {rapport:.0%} du 2xATR attendu : trop serré, il sera "
                        f"touché par le bruit ordinaire du marché."))
    elif rapport > 2.0:
        v.append(Verrou(2, "Où est mon invalidation technique ?", False,
                        f"stop à {rapport:.0%} du 2xATR attendu : trop large, la taille de "
                        f"position s'effondre et le R:R devient irréaliste."))
    else:
        v.append(Verrou(2, "Où est mon invalidation technique ?", True,
                        f"{plan.risque_points(specs):.0f} points, soit "
                        f"{plan.risque_prix / plan.atr:.2f} x ATR — dérivé de la volatilité, "
                        f"pas d'un montant rond."))

    # --- Q3 : combien je risque, en devise et en % ? ------------------------
    if dimensionnement is None:
        dimensionnement = dimensionner(
            capital=capital,
            risque_pct=cfg.risque.risque_par_trade_pct,
            points_de_risque=plan.risque_points(specs),
            specs=specs,
            lots_total_max=cfg.exposition.lots_total_max,
            lots_deja_ouverts=etat.lots_deja_ouverts,
            perte_max_par_position_pct=cfg.risque.perte_max_par_position_pct,
        )
    if not dimensionnement.autorise:
        v.append(Verrou(3, "Combien je risque, en devise et en % ?", False,
                        dimensionnement.raison))
    else:
        total = etat.exposition_courante_pct + dimensionnement.risque_pct
        if total > cfg.exposition.exposition_totale_max_pct:
            v.append(Verrou(3, "Combien je risque, en devise et en % ?", False,
                            f"ce trade porterait l'exposition totale à {total:.2f} %, "
                            f"au-delà du plafond de "
                            f"{cfg.exposition.exposition_totale_max_pct} %."))
        else:
            v.append(Verrou(3, "Combien je risque, en devise et en % ?", True,
                            f"{dimensionnement.risque_devise:.2f} {cfg.compte.devise} = "
                            f"{dimensionnement.risque_pct:.2f} % "
                            f"({dimensionnement.lots:g} lot)"))

    # --- Q4 : quel est mon ratio R:R ? --------------------------------------
    mini = cfg.risque.ratio_rr_minimum
    if plan.ratio_rr < mini:
        seuil = 100 / (1 + plan.ratio_rr)
        v.append(Verrou(4, "Quel est mon ratio R:R ?", False,
                        f"{plan.ratio_rr:.2f} < {mini} : il faudrait {seuil:.0f} % de "
                        f"réussite rien que pour l'équilibre, coûts non comptés."))
    else:
        seuil = 100 / (1 + plan.ratio_rr)
        v.append(Verrou(4, "Quel est mon ratio R:R ?", True,
                        f"{plan.ratio_rr:.2f} — équilibre atteint dès {seuil:.0f} % de réussite."))

    # --- Q5 : une annonce est-elle imminente ? ------------------------------
    if not cfg.calendrier.blackout_news_actif:
        v.append(Verrou(5, "Une annonce économique est-elle imminente ?", True,
                        "filtre désactivé dans la configuration."))
    elif annonce_imminente is None:
        v.append(Verrou(5, "Une annonce économique est-elle imminente ?", False,
                        "calendrier économique indisponible. Le blackout étant exigé, on "
                        "s'abstient : ne pas savoir n'est pas la même chose que savoir "
                        "qu'il n'y a rien."))
    else:
        imminente, quoi = annonce_imminente(maintenant)
        if imminente:
            v.append(Verrou(5, "Une annonce économique est-elle imminente ?", False,
                            f"{quoi} — le spread s'écarte et un gap peut sauter le stop."))
        else:
            v.append(Verrou(5, "Une annonce économique est-elle imminente ?", True,
                            "aucune annonce à fort impact dans la fenêtre."))

    # --- Q6 : quelle est mon émotion ? -> l'état du système -----------------
    soucis: list[str] = []
    if etat.en_pause:
        soucis.append(f"système en pause ({etat.motif_pause or 'motif non précisé'})")
    if etat.pertes_consecutives >= cfg.circuits.pertes_consecutives_max:
        soucis.append(f"{etat.pertes_consecutives} pertes consécutives "
                      f"(seuil {cfg.circuits.pertes_consecutives_max})")
    if etat.drawdown_courant_pct >= cfg.circuits.drawdown_max_total_pct:
        soucis.append(f"drawdown {etat.drawdown_courant_pct:.1f} % : arrêt total atteint")
    if etat.atr_plage_connue and etat.atr_courant:
        bas, haut = etat.atr_plage_connue
        if not (bas <= etat.atr_courant <= haut):
            soucis.append(f"volatilité {etat.atr_courant:.5f} hors de la plage vue à "
                          f"l'entraînement [{bas:.5f} ; {haut:.5f}]")
    if etat.regimes_favorables and etat.regime not in etat.regimes_favorables:
        soucis.append(f"régime « {etat.regime} » hors des régimes où la stratégie gagne "
                      f"{etat.regimes_favorables}")
    if etat.confiance_modele is not None and etat.confiance_modele < 0.5:
        soucis.append(f"confiance du modèle à {etat.confiance_modele:.0%}")

    v.append(Verrou(6, "Quel est l'état du système ? (l'« émotion » d'une machine)",
                    not soucis,
                    " · ".join(soucis) if soucis
                    else "série, volatilité, régime et confiance dans leurs plages."))

    # --- Maison 1 : discipline ---------------------------------------------
    d = cfg.discipline
    ecarts: list[str] = []
    if etat.trades_aujourdhui >= d.trades_max_par_jour:
        ecarts.append(f"{etat.trades_aujourdhui} trades aujourd'hui "
                      f"(plafond {d.trades_max_par_jour})")
    if etat.trades_cette_semaine >= d.trades_max_par_semaine:
        ecarts.append(f"{etat.trades_cette_semaine} trades cette semaine "
                      f"(plafond {d.trades_max_par_semaine})")
    if (etat.minutes_depuis_derniere_perte is not None
            and etat.minutes_depuis_derniere_perte < d.refroidissement_apres_perte_minutes):
        reste = d.refroidissement_apres_perte_minutes - etat.minutes_depuis_derniere_perte
        ecarts.append(f"refroidissement anti-revenge : encore {reste:.0f} min")
    v.append(Verrou(7, "La discipline est-elle tenue ?", not ecarts,
                    " · ".join(ecarts) if ecarts
                    else f"{etat.trades_aujourdhui}/{d.trades_max_par_jour} aujourd'hui, "
                         f"{etat.trades_cette_semaine}/{d.trades_max_par_semaine} cette semaine.",
                    maison=True))

    # --- Maison 2 : le marché est-il négociable maintenant ? ----------------
    conditions: list[str] = []
    if etat.spread_points > cfg.execution.spread_max_points:
        conditions.append(f"spread {etat.spread_points:.0f} points > "
                          f"{cfg.execution.spread_max_points} autorisés")
    elif etat.spread_habituel_points and etat.spread_points > 3 * etat.spread_habituel_points:
        conditions.append(f"spread {etat.spread_points:.0f} points = "
                          f"{etat.spread_points / etat.spread_habituel_points:.1f}x son niveau "
                          f"habituel : le marché n'est pas normal")
    if _dans_fenetre(maintenant.time(), cfg.calendrier.rollover_debut,
                     cfg.calendrier.rollover_fin) and cfg.calendrier.eviter_rollover:
        conditions.append("fenêtre de rollover : le spread y explose")
    if cfg.calendrier.eviter_asie_creuse and _dans_fenetre(
            maintenant.time(), cfg.calendrier.asie_debut, cfg.calendrier.asie_fin):
        conditions.append("heures creuses asiatiques : liquidité trop faible")
    if cfg.calendrier.fermer_avant_weekend and maintenant.weekday() == 4 \
            and maintenant.time() >= cfg.calendrier.vendredi_derniere_entree:
        conditions.append("vendredi après la dernière entrée : le gap du week-end "
                          "peut sauter le stop")
    if cfg.calendrier.eviter_ouverture_dimanche and maintenant.weekday() == 6:
        conditions.append("ouverture du dimanche : spreads larges, pas de volume")

    v.append(Verrou(8, "Le marché est-il négociable maintenant ?", not conditions,
                    " · ".join(conditions) if conditions
                    else f"spread {etat.spread_points:.0f} points, hors fenêtres interdites.",
                    maison=True))

    return Verdict(plan=plan, verrous=v, dimensionnement=dimensionnement)


def _dans_fenetre(t: time, debut: time, fin: time) -> bool:
    """Vrai si t est dans [debut, fin], y compris si la fenêtre passe minuit."""
    if debut <= fin:
        return debut <= t <= fin
    return t >= debut or t <= fin
