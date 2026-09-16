# -*- coding: utf-8 -*-
"""
Les réglages qu'on peut changer depuis l'interface, et comment on les change.

`config.toml` reste la référence documentée : on n'y écrit jamais depuis
l'application (un fichier commenté réécrit par un programme perd ses
commentaires, c'est-à-dire ses raisons). Les changements vivent dans
`reglages.json`, dans le dossier de données de l'utilisateur, et sont
superposés au fichier au chargement.

Trois règles :
  1. TOUT CHANGEMENT REPASSE PAR LE VIDEUR (`config.charger`). Si le résultat
     est dangereux, rien n'est enregistré et la raison est renvoyée en clair.
  2. CERTAINS RÉGLAGES N'EXISTENT PAS DANS L'INTERFACE : les interdits
     (martingale, grille, moyenne à la baisse), le stop côté serveur, le stop
     jamais élargi, l'apprentissage en direct. On ne propose pas un
     interrupteur qu'on refuserait d'actionner.
  3. CHAQUE CHANGEMENT EST JOURNALISÉ, avec son sens : relever le risque en
     plein drawdown est le geste n°2 qui tue un bot rentable, on le signale.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .chemins import fichier
from .config import Config, ConfigDangereuse, charger

# sens = "risque" : augmenter la valeur augmente le risque
#        "prudence" : augmenter la valeur rend le bot plus prudent
#        None : neutre
SCHEMA: list[dict] = [
    # Piloté par la commande « mode » de l'interface, jamais par le formulaire :
    # le passage en réel se décide d'un geste explicite, pas d'un menu déroulant.
    dict(cle="compte.mode", groupe="Compte", type="choix", choix=["demo", "reel"], sens="risque",
         cache=True, libelle="Mode du compte"),
    # --- Profils (le choix du profil actif a son propre écran) -------------
    dict(cle="profils.actif", groupe="Profil", type="choix", choix=["pro", "boost"], sens="risque",
         cache=True, libelle="Profil actif"),
    dict(cle="profil_pro.risque_par_trade_pct", groupe="Profil PRO", type="nombre",
         min=0.1, max=2.0, pas=0.1, unite="%", sens="risque", libelle="Risque par trade",
         aide="Plafond du code : 2 %. À 1 %, dix pertes d'affilée coûtent 10 %."),
    dict(cle="profil_pro.ratio_rr_minimum", groupe="Profil PRO", type="nombre",
         min=1.0, max=3.0, pas=0.1, unite="", sens="prudence", libelle="Ratio gain/risque minimum"),
    dict(cle="profil_pro.exposition_totale_max_pct", groupe="Profil PRO", type="nombre",
         min=1, max=10, pas=0.5, unite="%", sens="risque", libelle="Exposition totale"),
    dict(cle="profil_pro.perte_max_jour_pct", groupe="Profil PRO", type="nombre",
         min=1, max=10, pas=0.5, unite="%", sens="risque", libelle="Perte max du jour"),
    dict(cle="profil_pro.trades_max_par_jour", groupe="Profil PRO", type="entier",
         min=1, max=10, pas=1, unite="", sens="risque", libelle="Trades par jour"),
    dict(cle="profil_pro.levier_effectif_max", groupe="Profil PRO", type="nombre",
         min=1, max=30, pas=0.5, unite="×", sens="risque", libelle="Levier effectif maximum",
         aide="Taille engagée / capital. Au-delà, la taille est réduite, le trade n'est pas refusé."),
    dict(cle="profil_boost.risque_par_trade_pct", groupe="Profil BOOST", type="nombre",
         min=0.5, max=10.0, pas=0.5, unite="%", sens="risque", libelle="Risque par trade",
         aide="Plafond du code : 10 %. Les probabilités de perte se lisent dans l'écran du profil."),
    dict(cle="profil_boost.ratio_rr_minimum", groupe="Profil BOOST", type="nombre",
         min=1.0, max=3.0, pas=0.1, unite="", sens="prudence", libelle="Ratio gain/risque minimum"),
    dict(cle="profil_boost.perte_max_jour_pct", groupe="Profil BOOST", type="nombre",
         min=1, max=35, pas=0.5, unite="%", sens="risque", libelle="Perte max du jour",
         aide="Relevée automatiquement à 1,5 × le risque : une seule perte ne ferme pas la journée."),
    dict(cle="profil_boost.trades_max_par_jour", groupe="Profil BOOST", type="entier",
         min=1, max=20, pas=1, unite="", sens="risque", libelle="Trades par jour"),
    dict(cle="profil_boost.levier_effectif_max", groupe="Profil BOOST", type="nombre",
         min=1, max=30, pas=0.5, unite="×", sens="risque", libelle="Levier effectif maximum"),
    dict(cle="profil_boost.paliers_actifs", groupe="Profil BOOST", type="bool", sens="prudence",
         libelle="Paliers anti-martingale",
         aide="À chaque doublement du capital, le risque descend d'un cran. Jamais il ne remonte."),
    dict(cle="profil_boost.poche_declencheur_pct", groupe="Profil BOOST", type="nombre",
         min=0, max=500, pas=5, unite="%", sens=None, libelle="Poche épargne : à partir de",
         aide="Gain depuis la dernière mise à l'abri qui déclenche le verrouillage. 0 = désactivée."),
    dict(cle="profil_boost.poche_part_pct", groupe="Profil BOOST", type="nombre",
         min=0, max=100, pas=5, unite="%", sens="prudence", libelle="Poche épargne : part du gain",
         aide="Part du gain qui sort du capital de travail et n'est plus jamais risquée."),
    # --- Capital & risque par trade ---------------------------------------
    dict(cle="compte.capital_max_engage", groupe="Capital", type="nombre", min=0, max=10_000_000,
         pas=10, unite="$", sens="risque",
         libelle="Capital engagé au maximum",
         aide="Le bot dimensionne sur le plus petit entre ce montant et le solde. 0 = le solde entier "
              "(le mode réel exige un plafond)."),
    dict(cle="risque_position.risque_max_petit_compte_pct", groupe="Risque par trade", type="nombre",
         min=0.1, max=2.0, pas=0.1, unite="%", sens="risque",
         libelle="Plafond petit compte",
         aide="Jusqu'où le lot minimum peut relever le risque quand le capital est petit. "
              "Égal au risque par trade = refus strict."),
    dict(cle="risque_position.stop_loss_atr_multiple", groupe="Risque par trade", type="nombre",
         min=1.0, max=4.0, pas=0.25, unite="× ATR", sens=None,
         libelle="Distance du stop",
         aide="Le stop suit la volatilité. Plus court = plus de trades possibles sur petit capital, "
              "mais touché plus souvent par le bruit."),
    dict(cle="risque_position.take_profit_r_multiple", groupe="Risque par trade", type="nombre",
         min=1.0, max=5.0, pas=0.25, unite="R", sens=None,
         libelle="Objectif", aide="En multiples du risque. À 2 R, l'équilibre est à 33 % de réussite."),
    dict(cle="risque_position.trailing_actif", groupe="Risque par trade", type="bool", sens=None,
         libelle="Stop suiveur", aide="Resserre le stop après un gain de 1 R. Il ne l'élargit jamais."),
    dict(cle="risque_position.trailing_declenche_a_r", groupe="Risque par trade", type="nombre",
         min=0.5, max=3.0, pas=0.25, unite="R", sens=None, libelle="Suiveur à partir de"),
    dict(cle="risque_position.perte_max_par_position_pct", groupe="Risque par trade", type="nombre",
         min=1.0, max=5.0, pas=0.5, unite="%", sens="risque",
         libelle="Filet anti-bug", aide="Au-delà, l'ordre est bloqué comme une anomalie de calcul."),

    # --- Disjoncteurs -------------------------------------------------------
    dict(cle="coupe_circuits.perte_max_semaine_pct", groupe="Disjoncteurs", type="nombre",
         min=2, max=15, pas=0.5, unite="%", sens="risque", libelle="Perte max de la semaine"),
    dict(cle="coupe_circuits.perte_max_mois_pct", groupe="Disjoncteurs", type="nombre",
         min=3, max=25, pas=1, unite="%", sens="risque", libelle="Perte max du mois"),
    dict(cle="coupe_circuits.drawdown_max_total_pct", groupe="Disjoncteurs", type="nombre",
         min=5, max=35, pas=1, unite="%", sens="risque", libelle="Arrêt total",
         aide="Calibré au Monte Carlo de la stratégie active (au-delà de deux ans de variance "
              "normale), tant qu'on ne le fixe pas soi-même. Redémarrage manuel."),
    dict(cle="coupe_circuits.pertes_consecutives_max", groupe="Disjoncteurs", type="entier",
         min=3, max=15, pas=1, unite="pertes", sens="risque", libelle="Série noire"),
    dict(cle="coupe_circuits.pause_apres_serie_heures", groupe="Disjoncteurs", type="entier",
         min=1, max=168, pas=1, unite="h", sens="prudence", libelle="Pause après série noire"),

    # --- Exposition & discipline -------------------------------------------
    dict(cle="exposition.positions_simultanees_max", groupe="Discipline", type="entier",
         min=1, max=3, pas=1, unite="", sens="risque", libelle="Positions simultanées"),
    dict(cle="exposition.lots_total_max", groupe="Discipline", type="nombre",
         min=0.01, max=20, pas=0.01, unite="lots", sens="risque", libelle="Lots au total"),
    dict(cle="discipline.trades_max_par_semaine", groupe="Discipline", type="entier",
         min=1, max=30, pas=1, unite="", sens="risque", libelle="Trades par semaine"),
    dict(cle="discipline.refroidissement_apres_perte_minutes", groupe="Discipline", type="entier",
         min=0, max=1440, pas=15, unite="min", sens="prudence", libelle="Attente après une perte",
         aide="Anti-revenge : le geste qui sépare une mauvaise journée d'un mauvais mois."),
    dict(cle="discipline.stop_temporel_barres", groupe="Discipline", type="entier",
         min=0, max=200, pas=1, unite="barres", sens=None, libelle="Stop temporel",
         aide="Ferme un trade qui n'a rien fait après N barres. 0 = désactivé."),

    # --- Filtres de marché --------------------------------------------------
    dict(cle="execution.spread_max_points", groupe="Filtres de marché", type="entier",
         min=1, max=100, pas=1, unite="points", sens="risque", libelle="Spread maximum"),
    dict(cle="execution.slippage_max_points", groupe="Filtres de marché", type="entier",
         min=1, max=50, pas=1, unite="points", sens="risque", libelle="Glissement maximum"),
    dict(cle="calendrier.blackout_news_actif", groupe="Filtres de marché", type="bool",
         sens="prudence", libelle="Pause autour des annonces",
         aide="Ne pas entrer autour des annonces à fort impact (NFP, CPI, FOMC, BCE)."),
    dict(cle="calendrier.blackout_avant_minutes", groupe="Filtres de marché", type="entier",
         min=0, max=240, pas=5, unite="min", sens="prudence", libelle="Avant l'annonce"),
    dict(cle="calendrier.blackout_apres_minutes", groupe="Filtres de marché", type="entier",
         min=0, max=240, pas=5, unite="min", sens="prudence", libelle="Après l'annonce"),
    dict(cle="calendrier.eviter_asie_creuse", groupe="Filtres de marché", type="bool",
         sens="prudence", libelle="Éviter les heures creuses d'Asie"),
    dict(cle="calendrier.eviter_rollover", groupe="Filtres de marché", type="bool",
         sens="prudence", libelle="Éviter le rollover"),
    dict(cle="calendrier.fermer_avant_weekend", groupe="Filtres de marché", type="bool",
         sens="prudence", libelle="Tout fermer avant le week-end",
         aide="Un gap du week-end saute par-dessus les stops. Coupe aussi les tendances : "
              "voir le walk-forward."),
    dict(cle="calendrier.vendredi_derniere_entree", groupe="Filtres de marché", type="heure",
         sens=None, libelle="Dernière entrée du vendredi"),
    dict(cle="calendrier.vendredi_tout_fermer", groupe="Filtres de marché", type="heure",
         sens=None, libelle="Fermeture du vendredi"),
    dict(cle="calendrier.eviter_ouverture_dimanche", groupe="Filtres de marché", type="bool",
         sens="prudence", libelle="Éviter l'ouverture du dimanche"),

    # --- Marché -------------------------------------------------------------
    dict(cle="marche.timeframe", groupe="Marché", type="choix", choix=["H1", "H4", "D1"],
         sens=None, libelle="Unité de décision",
         aide="Le coût pèse 0,02 R en H4 contre 0,19 R en M5 : en dessous de H1, les frais "
              "mangent l'espérance."),
]

# Ce qui ne figure PAS dans le schéma, et pourquoi. L'interface l'affiche.
VERROUILLES = {
    "coupe_circuits.interdit_martingale":
        ("Pas de martingale", "doubler après une perte vide un compte en une seule série"),
    "coupe_circuits.interdit_moyenner_a_la_baisse":
        ("Pas de moyenne à la baisse", "renforcer une position perdante, c'est augmenter le risque quand la thèse tombe"),
    "coupe_circuits.interdit_grille":
        ("Pas de grille", "une grille gagne petit pendant des mois et rend tout en une séance"),
    "discipline.stop_jamais_elargi":
        ("Stop jamais élargi", "un stop ne bouge que dans le sens du profit"),
    "execution.stops_cote_serveur_obligatoire":
        ("Stop déposé chez le courtier", "une coupure de courant ne laisse jamais une position nue"),
    "apprentissage.apprentissage_en_ligne":
        ("Pas d'apprentissage en direct", "un modèle qui se réajuste après chaque perte court après le bruit"),
}

PAR_CLE = {s["cle"]: s for s in SCHEMA}

AGENT_DEFAUT = {
    "strategies_actives": ["cassure_donchian"],
    "intervalle_cycle_s": 20,
    "mode": "observation",          # observation | demo | reel
}


# --------------------------------------------------------------------------- #

def _lire() -> dict:
    p = fichier("reglages.json")
    if not p.exists():
        return {"config": {}, "agent": dict(AGENT_DEFAUT)}
    d = json.loads(p.read_text(encoding="utf-8"))
    d.setdefault("config", {})
    d["agent"] = {**AGENT_DEFAUT, **d.get("agent", {})}
    return d


def _ecrire(d: dict) -> None:
    fichier("reglages.json").write_text(json.dumps(d, indent=2, ensure_ascii=False),
                                        encoding="utf-8")


def surcharges() -> dict:
    return _lire()["config"]


def agent() -> dict:
    return _lire()["agent"]


def calibrage_actif(s: dict | None = None) -> dict:
    """Le seuil d'arrêt total calibré au Monte Carlo pour la stratégie et le risque actifs.

    Seuil = p99 du drawdown sur deux ans × 1,2, borné au plafond du code. S'il est
    plafonné, la variance normale de la stratégie à ce risque dépasse ce que le code
    tolère : l'arrêt total sera touché par du bruit, et on le dit.
    """
    from ..backtest import montecarlo
    from .chemins import dossier_rapports
    s = surcharges() if s is None else s
    try:
        cfg0 = charger(surcharges=s)
    except ConfigDangereuse:
        return {"valide": False, "raison": "configuration refusée"}
    actives = agent().get("strategies_actives") or []
    if not actives:
        return {"valide": False, "raison": "aucune stratégie active"}
    d = montecarlo.rapport_actif(dossier_rapports(), actives[0], cfg0.marche.timeframe,
                                 not cfg0.calendrier.fermer_avant_weekend)
    if not d:
        return {"valide": False, "raison": "aucun walk-forward pour la stratégie active"}
    cle_cache = (actives[0], d.get("variante"), d.get("calcule_le"), cfg0.risque.risque_par_trade_pct)
    if cle_cache not in _CALIBRAGES:
        R = montecarlo.rendements_en_R(d)
        par_an = (d.get("metriques") or {}).get("trades_par_mois", 2.3) * 12
        c = montecarlo.seuil_arret_calibre(R, risque_pct=cfg0.risque.risque_par_trade_pct,
                                           trades_par_an=par_an)
        c.update(strategie=actives[0], profil=cfg0.profil.actif)
        _CALIBRAGES[cle_cache] = c
    return dict(_CALIBRAGES[cle_cache])


_CALIBRAGES: dict = {}


def config_effective() -> Config:
    s = surcharges()
    if "coupe_circuits.drawdown_max_total_pct" not in s:
        c = calibrage_actif(s)
        if c.get("valide"):
            s = {**s, "coupe_circuits.drawdown_max_total_pct": c["seuil_pct"]}
    return charger(surcharges=s)


def _brut(s: dict | None = None) -> dict:
    """Le fichier de configuration avec les surcharges, AVANT application du profil.
    C'est là que vivent les réglages des profils, qui n'ont pas de section propre dans
    la configuration effective."""
    import tomllib
    from .config import RACINE
    with open(RACINE / "config.toml", "rb") as f:
        d = tomllib.load(f)
    for cle, v in (surcharges() if s is None else s).items():
        section, _, nom = cle.partition(".")
        if section in d and nom in d[section]:
            d[section][nom] = v
    return d


def valeur_actuelle(cfg: Config, cle: str):
    section, _, nom = cle.partition(".")
    if section == "profils" or section.startswith("profil_"):
        return _brut()[section][nom]
    objet = {"compte": cfg.compte, "marche": cfg.marche, "risque_position": cfg.risque,
             "coupe_circuits": cfg.circuits, "exposition": cfg.exposition,
             "discipline": cfg.discipline, "execution": cfg.execution,
             "calendrier": cfg.calendrier, "apprentissage": cfg.apprentissage}[section]
    v = getattr(objet, nom)
    return v.strftime("%H:%M") if hasattr(v, "strftime") else v


def decrire() -> dict:
    """Le schéma + les valeurs effectives, pour l'interface."""
    cfg = config_effective()
    s = surcharges()
    return {
        "reglages": [{**e, "valeur": valeur_actuelle(cfg, e["cle"]), "modifie": e["cle"] in s}
                     for e in SCHEMA],
        "verrouilles": [{"cle": k, "libelle": l, "raison": r} for k, (l, r) in VERROUILLES.items()],
        "agent": agent(),
    }


def _convertir(entree: dict, valeur):
    t = entree["type"]
    if t == "bool":
        if isinstance(valeur, str):
            return valeur.lower() in ("1", "true", "oui", "on")
        return bool(valeur)
    if t in ("nombre", "entier"):
        v = float(str(valeur).replace(",", "."))
        if t == "entier":
            v = int(round(v))
        if v < entree["min"] or v > entree["max"]:
            raise ValueError(f"{entree['libelle']} : {v:g} hors de [{entree['min']:g} ; "
                             f"{entree['max']:g}]")
        return v
    if t == "heure":
        if not re.fullmatch(r"\d{1,2}:\d{2}", str(valeur)):
            raise ValueError(f"{entree['libelle']} : heure attendue au format HH:MM")
        return str(valeur)
    if t == "choix":
        if valeur not in entree["choix"]:
            raise ValueError(f"{entree['libelle']} : valeur possible {entree['choix']}")
        return valeur
    raise ValueError(f"type inconnu {t}")


def modifier(changements: dict, *, auteur: str = "interface", drawdown_pct: float = 0.0,
             journal=None) -> dict:
    """Applique des changements {cle: valeur}. Tout ou rien.

    Renvoie {"ok": bool, "erreurs": [...], "changes": [...], "alertes": [...]}.
    """
    d = _lire()
    cfg_avant = config_effective()
    nouvelles = dict(d["config"])
    erreurs, changes, alertes = [], [], []

    for cle, valeur in changements.items():
        if cle in VERROUILLES:
            erreurs.append(f"{VERROUILLES[cle][0]} : non modifiable, {VERROUILLES[cle][1]}.")
            continue
        entree = PAR_CLE.get(cle)
        if not entree:
            erreurs.append(f"Réglage inconnu : {cle}")
            continue
        try:
            v = _convertir(entree, valeur)
        except (ValueError, TypeError) as exc:
            erreurs.append(str(exc))
            continue
        avant = valeur_actuelle(cfg_avant, cle)
        if v == avant:
            continue
        nouvelles[cle] = v
        hausse = isinstance(v, (int, float)) and not isinstance(v, bool) and v > avant
        sens = entree.get("sens")
        if cle == "profils.actif":
            hausse = v == "boost"
        plus_risque = (sens == "risque" and hausse) or (sens == "prudence" and not hausse
                                                        and entree["type"] != "bool") \
            or (sens == "prudence" and entree["type"] == "bool" and v is False)
        changes.append({"cle": cle, "libelle": entree["libelle"], "avant": avant, "apres": v,
                        "plus_risque": bool(plus_risque)})
        if plus_risque and drawdown_pct >= 3:
            alertes.append(f"{entree['libelle']} relevé alors que le compte est en drawdown de "
                           f"{drawdown_pct:.1f} % : c'est le geste qui transforme une mauvaise "
                           f"passe en compte vidé.")

    if erreurs:
        return {"ok": False, "erreurs": erreurs, "changes": [], "alertes": []}
    if not changes:
        return {"ok": True, "erreurs": [], "changes": [], "alertes": []}

    try:
        charger(surcharges=nouvelles)
    except ConfigDangereuse as exc:
        return {"ok": False, "erreurs": [str(exc)], "changes": [], "alertes": []}

    d["config"] = nouvelles
    _ecrire(d)
    if journal is not None:
        for c in changes:
            journal.reglage(c["cle"], c["avant"], c["apres"], auteur)
    return {"ok": True, "erreurs": [], "changes": changes, "alertes": alertes}


def reinitialiser(cle: str | None = None, *, journal=None, auteur="interface") -> None:
    d = _lire()
    cfg_avant = config_effective()
    cles = [cle] if cle else list(d["config"])
    for k in cles:
        if k in d["config"]:
            avant = valeur_actuelle(cfg_avant, k)
            d["config"].pop(k)
            if journal is not None:
                journal.reglage(k, avant, "(valeur du fichier)", auteur)
    _ecrire(d)


def modifier_agent(changements: dict) -> dict:
    d = _lire()
    for k, v in changements.items():
        if k not in AGENT_DEFAUT:
            raise ValueError(f"Réglage d'agent inconnu : {k}")
        d["agent"][k] = v
    _ecrire(d)
    return d["agent"]


def horodatage() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
