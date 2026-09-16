# -*- coding: utf-8 -*-
"""
Chargement et VALIDATION de config.toml.

Ce module n'est pas un lecteur de fichier : c'est un videur. Il refuse de
laisser démarrer un système mal réglé, parce qu'un mauvais réglage du risque ne
se voit pas — il se paie trois mois plus tard, d'un coup.

    python trading/noyau/config.py        # affiche la posture de risque

Toute valeur refusée lève ConfigDangereuse avec la raison, en français.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Plafonds écrits DANS LE CODE, que le fichier de configuration ne peut pas
# desserrer. Ce sont les limites qu'un trader expérimenté ne franchit pas, et
# les mettre ici plutôt que dans le TOML est délibéré : on ne doit pas pouvoir
# les relever un soir de frustration en éditant un fichier texte.
# -----------------------------------------------------------------------------
PLAFOND_RISQUE_PAR_TRADE = 2.0    # % de l'équité. Au-delà, la ruine devient probable.
PLAFOND_DRAWDOWN_TOTAL = 35.0     # % . Au-delà, il faut +54 % pour revenir à zéro.
PLANCHER_ECHANTILLON = 100        # trades. En dessous, « apprendre » = inventer.

TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"}


class ConfigDangereuse(Exception):
    """Le réglage demandé peut détruire le compte. On ne démarre pas."""


# =============================================================================
#  Sections
# =============================================================================

@dataclass(frozen=True)
class Compte:
    capital_max_engage: float
    devise: str
    mode: str
    courtier: str
    serveur: str
    terminal: str
    magic_number: int

    @property
    def est_reel(self) -> bool:
        return self.mode == "reel"

    def capital_effectif(self, solde_reel: float) -> float:
        """Le capital de travail : le plus PETIT des deux.

        C'est le cœur du plafond. Le bot ne voit jamais l'argent qui dort à
        côté : si le compte porte 5 000 $ et que le plafond est à 200 $, toutes
        les tailles de position sont calculées sur 200 $.
        """
        if self.capital_max_engage <= 0:
            return solde_reel
        return min(self.capital_max_engage, solde_reel)


@dataclass(frozen=True)
class RisquePosition:
    risque_par_trade_pct: float
    risque_par_trade_pct_max: float
    stop_loss_atr_multiple: float
    atr_periode: int
    take_profit_r_multiple: float
    ratio_rr_minimum: float
    trailing_actif: bool
    trailing_declenche_a_r: float
    trailing_atr_multiple: float
    perte_max_par_position_pct: float
    # Politique du petit compte : jusqu'où le lot minimum peut relever le
    # risque d'un trade quand le capital ne permet pas mieux. Égal à
    # risque_par_trade_pct = politique désactivée (refus strict).
    risque_max_petit_compte_pct: float = 2.0


@dataclass(frozen=True)
class CoupeCircuits:
    perte_max_jour_pct: float
    perte_max_semaine_pct: float
    perte_max_mois_pct: float
    drawdown_max_total_pct: float
    pertes_consecutives_max: int
    pause_apres_serie_heures: int
    interdit_martingale: bool
    interdit_moyenner_a_la_baisse: bool
    interdit_grille: bool


@dataclass(frozen=True)
class Exposition:
    positions_simultanees_max: int
    lots_total_max: float
    exposition_totale_max_pct: float


@dataclass(frozen=True)
class Discipline:
    refroidissement_apres_perte_minutes: int
    trades_max_par_jour: int
    trades_max_par_semaine: int
    stop_temporel_barres: int
    stop_jamais_elargi: bool
    alerter_si_risque_releve_en_drawdown: bool


@dataclass(frozen=True)
class Execution:
    spread_max_points: int
    slippage_max_points: int
    stops_cote_serveur_obligatoire: bool
    tentatives_max: int


@dataclass(frozen=True)
class Calendrier:
    eviter_rollover: bool
    rollover_debut: time
    rollover_fin: time
    eviter_asie_creuse: bool
    asie_debut: time
    asie_fin: time
    fermer_avant_weekend: bool
    vendredi_derniere_entree: time
    vendredi_tout_fermer: time
    eviter_ouverture_dimanche: bool
    blackout_news_actif: bool
    blackout_avant_minutes: int
    blackout_apres_minutes: int


@dataclass(frozen=True)
class Apprentissage:
    apprentissage_en_ligne: bool
    reentrainement_jours: int
    echantillon_min_trades: int
    amelioration_min_requise_pct: float
    validation: str
    role: str
    modele: str


@dataclass(frozen=True)
class Marche:
    symbole: str
    timeframe: str
    timeframe_filtre: str


@dataclass(frozen=True)
class Config:
    compte: Compte
    marche: Marche
    risque: RisquePosition
    circuits: CoupeCircuits
    exposition: Exposition
    discipline: Discipline
    execution: Execution
    calendrier: Calendrier
    apprentissage: Apprentissage
    surveillance: dict
    journal: dict
    chemin: Path = field(default_factory=lambda: RACINE / "config.toml")


# =============================================================================
#  Chargement
# =============================================================================

def _heure(texte: str, champ: str) -> time:
    try:
        h, m = texte.split(":")
        return time(int(h), int(m))
    except Exception as exc:  # noqa: BLE001
        raise ConfigDangereuse(
            f"[calendrier] {champ} = {texte!r} n'est pas une heure valide "
            f"(format attendu \"HH:MM\")."
        ) from exc


def charger(chemin: Path | str | None = None, *, surcharges: dict | None = None) -> Config:
    """Lit config.toml, le valide, et refuse tout réglage dangereux.

    `surcharges` = {"section.cle": valeur} : les réglages changés depuis
    l'interface. Ils passent par le MÊME videur que le fichier : une surcharge
    ne desserre rien que le fichier n'aurait pas pu desserrer.
    """
    chemin = Path(chemin) if chemin else RACINE / "config.toml"
    if not chemin.exists():
        raise ConfigDangereuse(f"Configuration introuvable : {chemin}")

    with open(chemin, "rb") as f:
        d = tomllib.load(f)

    for cle_complete, valeur in (surcharges or {}).items():
        section, _, cle = cle_complete.partition(".")
        if section not in d or cle not in d[section]:
            raise ConfigDangereuse(f"Réglage inconnu : {cle_complete}")
        d[section][cle] = valeur

    cal = d["calendrier"]
    cfg = Config(
        compte=Compte(**d["compte"]),
        marche=Marche(**d["marche"]),
        risque=RisquePosition(**d["risque_position"]),
        circuits=CoupeCircuits(**d["coupe_circuits"]),
        exposition=Exposition(**d["exposition"]),
        discipline=Discipline(**d["discipline"]),
        execution=Execution(**d["execution"]),
        calendrier=Calendrier(
            eviter_rollover=cal["eviter_rollover"],
            rollover_debut=_heure(cal["rollover_debut"], "rollover_debut"),
            rollover_fin=_heure(cal["rollover_fin"], "rollover_fin"),
            eviter_asie_creuse=cal["eviter_asie_creuse"],
            asie_debut=_heure(cal["asie_debut"], "asie_debut"),
            asie_fin=_heure(cal["asie_fin"], "asie_fin"),
            fermer_avant_weekend=cal["fermer_avant_weekend"],
            vendredi_derniere_entree=_heure(cal["vendredi_derniere_entree"], "vendredi_derniere_entree"),
            vendredi_tout_fermer=_heure(cal["vendredi_tout_fermer"], "vendredi_tout_fermer"),
            eviter_ouverture_dimanche=cal["eviter_ouverture_dimanche"],
            blackout_news_actif=cal["blackout_news_actif"],
            blackout_avant_minutes=cal["blackout_avant_minutes"],
            blackout_apres_minutes=cal["blackout_apres_minutes"],
        ),
        apprentissage=Apprentissage(**d["apprentissage"]),
        surveillance=d["surveillance"],
        journal=d["journal"],
        chemin=chemin,
    )
    _valider(cfg)
    return cfg


# =============================================================================
#  Le videur
# =============================================================================

def _valider(c: Config) -> None:
    fautes: list[str] = []

    # --- Compte -------------------------------------------------------------
    if c.compte.mode not in ("demo", "reel"):
        fautes.append(f"[compte] mode = {c.compte.mode!r} : attendu \"demo\" ou \"reel\".")

    if c.compte.est_reel and c.compte.capital_max_engage <= 0:
        fautes.append(
            "[compte] Passage en RÉEL demandé alors que capital_max_engage = 0.\n"
            "        Tant que ce plafond n'est pas choisi délibérément, le bot\n"
            "        dimensionnerait ses positions sur la totalité du compte."
        )

    if c.compte.magic_number <= 0:
        fautes.append("[compte] magic_number doit être un entier positif : c'est ce qui "
                      "sépare les ordres du bot de tes trades manuels.")

    # --- Marché -------------------------------------------------------------
    for champ, val in (("timeframe", c.marche.timeframe),
                       ("timeframe_filtre", c.marche.timeframe_filtre)):
        if val not in TIMEFRAMES:
            fautes.append(f"[marche] {champ} = {val!r} inconnu. Valeurs : {sorted(TIMEFRAMES)}")

    # --- Risque par position ------------------------------------------------
    r = c.risque
    if r.risque_par_trade_pct <= 0:
        fautes.append("[risque_position] risque_par_trade_pct doit être > 0.")

    if r.risque_par_trade_pct > r.risque_par_trade_pct_max:
        fautes.append(
            f"[risque_position] risque_par_trade_pct ({r.risque_par_trade_pct} %) dépasse "
            f"son propre plafond risque_par_trade_pct_max ({r.risque_par_trade_pct_max} %)."
        )

    if r.risque_par_trade_pct > PLAFOND_RISQUE_PAR_TRADE:
        fautes.append(
            f"[risque_position] risque_par_trade_pct = {r.risque_par_trade_pct} % dépasse le\n"
            f"        plafond écrit dans le code ({PLAFOND_RISQUE_PAR_TRADE} %).\n"
            f"        À ce niveau, une série de 10 pertes consécutives (qui arrive environ\n"
            f"        une fois par an) coûte {r.risque_par_trade_pct * 10:.0f} % du compte.\n"
            f"        Ce plafond n'est pas desserrable depuis le fichier, volontairement."
        )

    if r.take_profit_r_multiple < 1.0:
        fautes.append(
            f"[risque_position] take_profit_r_multiple = {r.take_profit_r_multiple} : viser moins\n"
            f"        que le montant risqué exige un taux de réussite > "
            f"{100 / (1 + r.take_profit_r_multiple):.0f} % rien que pour rentrer dans ses frais."
        )

    if r.stop_loss_atr_multiple <= 0:
        fautes.append("[risque_position] stop_loss_atr_multiple doit être > 0 : un système "
                      "sans stop n'a pas d'espérance définie, il a une date de décès.")

    if r.atr_periode < 2:
        fautes.append("[risque_position] atr_periode doit être >= 2.")

    if r.risque_max_petit_compte_pct < r.risque_par_trade_pct:
        fautes.append(
            f"[risque_position] risque_max_petit_compte_pct ({r.risque_max_petit_compte_pct} %) "
            f"est sous le risque nominal ({r.risque_par_trade_pct} %) : pour désactiver la "
            f"politique du petit compte, écrire la même valeur que le risque nominal.")
    if r.risque_max_petit_compte_pct > PLAFOND_RISQUE_PAR_TRADE:
        fautes.append(
            f"[risque_position] risque_max_petit_compte_pct = {r.risque_max_petit_compte_pct} % "
            f"dépasse le plafond écrit dans le code ({PLAFOND_RISQUE_PAR_TRADE} %).\n"
            f"        Un petit compte n'a pas le droit de risquer plus qu'un gros : il a "
            f"moins de marge pour encaisser une série noire, pas plus.")
    if r.perte_max_par_position_pct < r.risque_max_petit_compte_pct:
        fautes.append(
            f"[risque_position] perte_max_par_position_pct ({r.perte_max_par_position_pct} %) "
            f"est sous risque_max_petit_compte_pct ({r.risque_max_petit_compte_pct} %) : le "
            f"filet refuserait les trades que la politique du petit compte autorise.")

    if r.perte_max_par_position_pct < r.risque_par_trade_pct:
        fautes.append(
            f"[risque_position] perte_max_par_position_pct ({r.perte_max_par_position_pct} %) est\n"
            f"        inférieur au risque nominal par trade ({r.risque_par_trade_pct} %) :\n"
            f"        le filet de sécurité refuserait tous les ordres normaux."
        )

    # --- Coupe-circuits -----------------------------------------------------
    cc = c.circuits
    paliers = [
        ("perte_max_jour_pct", cc.perte_max_jour_pct),
        ("perte_max_semaine_pct", cc.perte_max_semaine_pct),
        ("perte_max_mois_pct", cc.perte_max_mois_pct),
        ("drawdown_max_total_pct", cc.drawdown_max_total_pct),
    ]
    for (n1, v1), (n2, v2) in zip(paliers, paliers[1:]):
        if v1 > v2:
            fautes.append(
                f"[coupe_circuits] {n1} ({v1} %) > {n2} ({v2} %) : l'escalier des disjoncteurs\n"
                f"        est inversé, le palier large se déclencherait avant le palier serré."
            )

    if cc.perte_max_jour_pct <= 0:
        fautes.append("[coupe_circuits] perte_max_jour_pct doit être > 0.")

    if cc.drawdown_max_total_pct > PLAFOND_DRAWDOWN_TOTAL:
        besoin = 100 * cc.drawdown_max_total_pct / (100 - cc.drawdown_max_total_pct)
        fautes.append(
            f"[coupe_circuits] drawdown_max_total_pct = {cc.drawdown_max_total_pct} % dépasse le\n"
            f"        plafond du code ({PLAFOND_DRAWDOWN_TOTAL} %). Après une telle perte il faut\n"
            f"        gagner +{besoin:.0f} % pour seulement revenir au point de départ."
        )

    if cc.perte_max_jour_pct < c.risque.risque_par_trade_pct:
        fautes.append(
            f"[coupe_circuits] perte_max_jour_pct ({cc.perte_max_jour_pct} %) est inférieur au\n"
            f"        risque d'un seul trade ({c.risque.risque_par_trade_pct} %) : la première\n"
            f"        position perdante fermerait la journée."
        )

    if cc.pertes_consecutives_max < 3:
        fautes.append(
            f"[coupe_circuits] pertes_consecutives_max = {cc.pertes_consecutives_max} : trop bas.\n"
            f"        Une série de 3 pertes est banale pour un système à 40 % de réussite\n"
            f"        (probabilité ≈ 22 %). Le bot passerait sa vie en pause."
        )

    # Les trois interdits ne se négocient pas.
    for champ, actif, explication in (
        ("interdit_martingale", cc.interdit_martingale,
         "doubler la mise après une perte transforme une série normale en compte vidé"),
        ("interdit_moyenner_a_la_baisse", cc.interdit_moyenner_a_la_baisse,
         "renforcer une position perdante, c'est augmenter le risque exactement quand "
         "la thèse se révèle fausse"),
        ("interdit_grille", cc.interdit_grille,
         "une grille gagne petit pendant des mois puis rend tout en une séance"),
    ):
        if not actif:
            fautes.append(
                f"[coupe_circuits] {champ} = false : refusé.\n"
                f"        Raison : {explication}.\n"
                f"        Ce comportement n'est pas implémenté dans le moteur."
            )

    if r.ratio_rr_minimum < 1.0:
        seuil = 100 / (1 + r.ratio_rr_minimum)
        fautes.append(
            f"[risque_position] ratio_rr_minimum = {r.ratio_rr_minimum} : viser moins que\n"
            f"        ce qu'on risque exige {seuil:.0f} % de réussite rien que pour l'équilibre,\n"
            f"        et il ne reste alors aucune marge pour payer le spread."
        )

    if r.take_profit_r_multiple < r.ratio_rr_minimum:
        fautes.append(
            f"[risque_position] take_profit_r_multiple ({r.take_profit_r_multiple}) est sous le\n"
            f"        plancher ratio_rr_minimum ({r.ratio_rr_minimum}) : la stratégie viserait\n"
            f"        systématiquement moins que ce que le contrôle préalable accepte."
        )

    # --- Exposition ---------------------------------------------------------
    if c.exposition.positions_simultanees_max < 1:
        fautes.append("[exposition] positions_simultanees_max doit être >= 1.")
    if c.exposition.lots_total_max <= 0:
        fautes.append("[exposition] lots_total_max doit être > 0.")

    if c.exposition.exposition_totale_max_pct < c.risque.risque_par_trade_pct:
        fautes.append(
            f"[exposition] exposition_totale_max_pct ({c.exposition.exposition_totale_max_pct} %)\n"
            f"        est inférieur au risque d'un seul trade "
            f"({c.risque.risque_par_trade_pct} %) : aucune position ne pourrait s'ouvrir."
        )
    if c.exposition.exposition_totale_max_pct > 10.0:
        fautes.append(
            f"[exposition] exposition_totale_max_pct = {c.exposition.exposition_totale_max_pct} % :\n"
            f"        au-delà de 10 %, une seule séance défavorable suffit à creuser un trou\n"
            f"        dont la remontée prend des mois. Le repère du métier est 5 à 6 %."
        )

    # --- Discipline ---------------------------------------------------------
    di = c.discipline
    if not di.stop_jamais_elargi:
        fautes.append(
            "[discipline] stop_jamais_elargi = false : refusé.\n"
            "        C'est l'invariant qui empêche « j'espère que ça revienne ». Un stop se\n"
            "        déplace uniquement dans la direction du profit — l'élargir revient à\n"
            "        augmenter le risque au moment précis où la thèse se révèle fausse."
        )
    if di.trades_max_par_jour < 1:
        fautes.append("[discipline] trades_max_par_jour doit être >= 1.")
    if di.trades_max_par_semaine < di.trades_max_par_jour:
        fautes.append(
            f"[discipline] trades_max_par_semaine ({di.trades_max_par_semaine}) < "
            f"trades_max_par_jour ({di.trades_max_par_jour}) : le plafond hebdomadaire\n"
            f"        serait atteint avant le plafond journalier."
        )
    if di.refroidissement_apres_perte_minutes < 0:
        fautes.append("[discipline] refroidissement_apres_perte_minutes ne peut pas être négatif.")
    if di.stop_temporel_barres < 0:
        fautes.append("[discipline] stop_temporel_barres ne peut pas être négatif (0 = désactivé).")

    # --- Exécution ----------------------------------------------------------
    if not c.execution.stops_cote_serveur_obligatoire:
        fautes.append(
            "[execution] stops_cote_serveur_obligatoire = false : refusé.\n"
            "        Le bot tourne sur un PC à Cotonou. Sans stop déposé chez le courtier,\n"
            "        une coupure de courant laisse une position ouverte sans surveillance."
        )
    if c.execution.spread_max_points <= 0:
        fautes.append("[execution] spread_max_points doit être > 0 : sans filtre de spread, "
                      "le bot entrera au rollover et paiera dix fois le prix normal.")
    if c.execution.tentatives_max < 1:
        fautes.append("[execution] tentatives_max doit être >= 1.")

    # --- Calendrier ---------------------------------------------------------
    if c.calendrier.fermer_avant_weekend:
        if c.calendrier.vendredi_derniere_entree >= c.calendrier.vendredi_tout_fermer:
            fautes.append(
                "[calendrier] vendredi_derniere_entree doit précéder vendredi_tout_fermer, "
                "sinon le bot ouvrirait une position juste avant de tout liquider."
            )

    # --- Apprentissage ------------------------------------------------------
    a = c.apprentissage
    if a.apprentissage_en_ligne:
        fautes.append(
            "[apprentissage] apprentissage_en_ligne = true : refusé.\n"
            "        Un modèle qui se réajuste après chaque perte court après le bruit\n"
            "        (rapport signal/bruit du forex ≈ 5 %) et finit par miser gros sur sa\n"
            "        dernière idée. Le réentraînement se fait hors ligne, validé en\n"
            "        walk-forward, et promu seulement s'il bat le champion."
        )

    if a.echantillon_min_trades < PLANCHER_ECHANTILLON:
        fautes.append(
            f"[apprentissage] echantillon_min_trades = {a.echantillon_min_trades} < "
            f"{PLANCHER_ECHANTILLON}.\n"
            f"        Sous ce seuil, un modèle n'apprend pas : il mémorise du hasard."
        )

    if a.validation != "walk_forward":
        fautes.append(
            f"[apprentissage] validation = {a.validation!r} : seul \"walk_forward\" est accepté.\n"
            f"        Une validation croisée ordinaire laisse fuiter le futur dans le passé\n"
            f"        sur des séries temporelles, et produit des résultats flatteurs et faux."
        )

    if a.role not in ("meta_labeling", "direction"):
        fautes.append(f"[apprentissage] role = {a.role!r} inconnu.")

    if a.modele not in ("gradient_boosting", "reseau_profond", "logistique"):
        fautes.append(f"[apprentissage] modele = {a.modele!r} inconnu.")

    if a.amelioration_min_requise_pct <= 0:
        fautes.append(
            "[apprentissage] amelioration_min_requise_pct doit être > 0 : sans marge exigée,\n"
            "        un challenger qui n'est que du bruit finirait par passer par hasard."
        )

    if fautes:
        raise ConfigDangereuse(
            "Configuration refusée. "
            f"{len(fautes)} problème(s) :\n\n" + "\n\n".join(f"  {i}. {f}" for i, f in enumerate(fautes, 1))
        )


# =============================================================================
#  Lecture humaine
# =============================================================================

def resume(c: Config) -> str:
    """La posture de risque en clair, pour la relire avant d'armer le bot."""
    cap = c.compte.capital_max_engage
    cap_txt = f"{cap:,.2f} {c.compte.devise}".replace(",", " ") if cap > 0 else "NON DÉFINI (réel bloqué)"
    perte_trade = cap * c.risque.risque_par_trade_pct / 100 if cap > 0 else 0
    perte_jour = cap * c.circuits.perte_max_jour_pct / 100 if cap > 0 else 0
    perte_totale = cap * c.circuits.drawdown_max_total_pct / 100 if cap > 0 else 0

    lignes = [
        "=" * 68,
        f"  POSTURE DE RISQUE  ·  {c.marche.symbole}  ·  mode {c.compte.mode.upper()}",
        "=" * 68,
        f"  Courtier              {c.compte.courtier}  ({c.compte.serveur or 'serveur non renseigné'})",
        f"  Capital engagé max    {cap_txt}",
        f"  Unité de décision     {c.marche.timeframe}   (filtre {c.marche.timeframe_filtre})",
        "",
        "  PAR TRADE",
        f"    Risque              {c.risque.risque_par_trade_pct} %"
        + (f"   =  {perte_trade:,.2f} {c.compte.devise}".replace(",", " ") if cap > 0 else ""),
        f"    Stop                {c.risque.stop_loss_atr_multiple} x ATR({c.risque.atr_periode})",
        f"    Objectif            {c.risque.take_profit_r_multiple} R",
        f"    Suiveur             " + (f"à partir de {c.risque.trailing_declenche_a_r} R"
                                       if c.risque.trailing_actif else "désactivé"),
        "",
        "  DISJONCTEURS",
        f"    Jour                -{c.circuits.perte_max_jour_pct} %"
        + (f"   =  {perte_jour:,.2f} {c.compte.devise}".replace(",", " ") if cap > 0 else ""),
        f"    Semaine             -{c.circuits.perte_max_semaine_pct} %",
        f"    Mois                -{c.circuits.perte_max_mois_pct} %",
        f"    ARRÊT TOTAL         -{c.circuits.drawdown_max_total_pct} %"
        + (f"   =  {perte_totale:,.2f} {c.compte.devise}".replace(",", " ") if cap > 0 else "")
        + "   (redémarrage manuel)",
        f"    Série noire         {c.circuits.pertes_consecutives_max} pertes -> pause "
        f"{c.circuits.pause_apres_serie_heures} h",
        "",
        "  DISCIPLINE",
        f"    Ratio R:R minimum   {c.risque.ratio_rr_minimum}   "
        f"(équilibre à {100 / (1 + c.risque.ratio_rr_minimum):.0f} % de réussite)",
        f"    Trades max          {c.discipline.trades_max_par_jour}/jour · "
        f"{c.discipline.trades_max_par_semaine}/semaine",
        f"    Après une perte     attente {c.discipline.refroidissement_apres_perte_minutes} min "
        f"(anti-revenge)",
        f"    Stop temporel       " + (f"{c.discipline.stop_temporel_barres} barres"
                                       if c.discipline.stop_temporel_barres else "désactivé"),
        f"    Stop élargi         INTERDIT (il ne bouge que vers le profit)",
        f"    Exposition totale   {c.exposition.exposition_totale_max_pct} % max",
        "",
        "  FILTRES",
        f"    Spread max          {c.execution.spread_max_points} points",
        f"    Stops côté serveur  {'OUI' if c.execution.stops_cote_serveur_obligatoire else 'NON'}",
        f"    Rollover évité      {'oui' if c.calendrier.eviter_rollover else 'non'}"
        f"   ({c.calendrier.rollover_debut:%H:%M}-{c.calendrier.rollover_fin:%H:%M})",
        f"    Week-end            {'tout fermé à ' + format(c.calendrier.vendredi_tout_fermer, '%H:%M')
                                   if c.calendrier.fermer_avant_weekend else 'positions conservées'}",
        f"    Blackout news       {'±' + str(c.calendrier.blackout_avant_minutes) + ' min'
                                   if c.calendrier.blackout_news_actif else 'désactivé'}",
        "",
        "  APPRENTISSAGE",
        f"    Rôle du modèle      {c.apprentissage.role}  ({c.apprentissage.modele})",
        f"    En direct           {'OUI (DANGER)' if c.apprentissage.apprentissage_en_ligne else 'non — hors ligne uniquement'}",
        f"    Réentraînement      tous les {c.apprentissage.reentrainement_jours} jours, "
        f"min {c.apprentissage.echantillon_min_trades} trades",
        f"    Promotion           +{c.apprentissage.amelioration_min_requise_pct} % exigés "
        f"en {c.apprentissage.validation}",
        "",
        "  INTERDITS ABSOLUS     martingale · moyenner à la baisse · grille",
        "=" * 68,
    ]
    return "\n".join(lignes)


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        cfg = charger()
    except ConfigDangereuse as e:
        print("\n⛔ DÉMARRAGE REFUSÉ\n")
        print(e)
        sys.exit(1)
    print(resume(cfg))
    if not cfg.compte.est_reel:
        print("\n  Mode démo : aucun argent réel n'est engagé.")
    if cfg.compte.capital_max_engage <= 0:
        print("  ⚠ capital_max_engage = 0 -> le passage en réel est bloqué tant qu'il "
              "n'est pas\n    choisi délibérément dans config.toml.")
