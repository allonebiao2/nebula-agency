# -*- coding: utf-8 -*-
"""
L'historique long, lu dans le terminal MT5 du courtier.

    python -m trading.noyau.donnees_mt5                 # H4, D1 et H1
    python -m trading.noyau.donnees_mt5 H4              # une seule unité
    python -m trading.noyau.donnees_mt5 H4 D1 --base NAS100   # « US Tech 100 » chez Deriv

Mesuré le 2026-09-16 chez Deriv-Demo : **25 000 barres H4 depuis le
2011-02-24**, contre un an par l'API publique. C'est ce qui rend un
walk-forward possible (~500 trades au lieu de ~35).

Trois choses à savoir, toutes mesurées :

  · LE TERMINAL TÉLÉCHARGE À LA MINUTE, une année par minute en remontant, et
    ~22 Mo par année. La première demande peut donc durer plusieurs minutes et
    échouer en « Call failed » si on demande plus de barres qu'il n'en a encore :
    on demande par PLAGE de dates, jamais par nombre.
  · LES HEURES SONT CELLES DU SERVEUR. On enregistre le décalage mesuré à
    l'export : un historique sans son fuseau fait entrer au mauvais moment.
  · LE CHAMP `spread` D'UNE BOUGIE N'EST PAS LE SPREAD PAYÉ : c'est souvent le
    plus petit de la barre. Le coût facturé vient de la mesure sur ticks.

Ces prix sont ceux de CE courtier. C'est voulu : on backteste sur les prix de
celui chez qui on tradera. Un edge mesuré ici se re-mesure ailleurs avant d'être
annoncé comme portable.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    import MetaTrader5 as mt5
except ImportError:                                            # pragma: no cover
    mt5 = None

from ..strategies.base import Barres
from .chemins import dossier_donnees

# Dans le dépôt : trading/donnees. Installé : le dossier de l'utilisateur, jamais
# le dossier du programme (en lecture seule).
CACHE = dossier_donnees()
DEBUT_HISTOIRE = datetime(2005, 1, 1, tzinfo=timezone.utc)   # ~20 ans ; chaque année de plus coûte ~22 Mo de disque au terminal

TIMEFRAMES_MT5 = {
    "M1": "TIMEFRAME_M1", "M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15",
    "M30": "TIMEFRAME_M30", "H1": "TIMEFRAME_H1", "H4": "TIMEFRAME_H4",
    "D1": "TIMEFRAME_D1", "W1": "TIMEFRAME_W1",
}


def constante_tf(timeframe: str) -> int:
    if mt5 is None:
        raise RuntimeError("Le paquet MetaTrader5 n'est pas installé.")
    try:
        return getattr(mt5, TIMEFRAMES_MT5[timeframe])
    except KeyError as exc:
        raise ValueError(f"Unité de temps inconnue : {timeframe}") from exc


def chemin_cache(base: str, timeframe: str) -> Path:
    return CACHE / f"{base.upper()}_{timeframe}_mt5.npz"


# --------------------------------------------------------------------------- #
#  Lecture dans le terminal (session déjà ouverte)
# --------------------------------------------------------------------------- #

def lire_plage(symbole: str, timeframe: str, debut: datetime | None = None,
               fin: datetime | None = None, *, bavard: bool = False) -> Barres:
    """Toutes les barres disponibles entre deux dates. Session MT5 requise.

    ⚠️ Mesuré : une seule demande de 2005 à aujourd'hui échoue en
    `(-1, 'Terminal: Call failed')`, la même par ANNÉE passe (0,0 s pour une
    année déjà téléchargée, ~70 s pour une année que le terminal doit aller
    chercher). On lit donc année par année, en remontant, et on s'arrête à la
    première année vide.
    """
    debut = debut or DEBUT_HISTOIRE
    fin = fin or datetime.now(timezone.utc)
    tf = constante_tf(timeframe)
    morceaux = []
    for an in range(fin.year, debut.year - 1, -1):
        a = max(debut, datetime(an, 1, 1, tzinfo=timezone.utc))
        b = min(fin, datetime(an + 1, 1, 1, tzinfo=timezone.utc))
        rates = mt5.copy_rates_range(symbole, tf, a, b)
        n = 0 if rates is None else len(rates)
        if bavard:
            print(f"    {timeframe} {an} : {n} barres", flush=True)
        if n == 0:
            break
        morceaux.append(rates)
    # ⚠️ MESURÉ le 2026-09-17 : le terminal ne rend que les barres du réglage « Max. barres
    # dans le graphique » (100 000 par défaut). Une année qui DÉPASSE cette limite rend 0 barre,
    # même si sa fin est dedans : en M5, la lecture par année s'arrêtait à 2026 et perdait
    # 47 000 barres chargées. Les N dernières barres se lisent d'un bloc et complètent.
    # Mesuré aussi : demander EXACTEMENT la limite rend None ; 99 000 passe.
    info = mt5.terminal_info()
    # Réglé sur « Unlimited », le terminal annonce 100 000 000 : on ne demande jamais plus
    # d'un million de barres d'un bloc (60 octets chacune), la lecture par année fait le reste.
    plafond = min(int(getattr(info, "maxbars", 100_000) or 100_000), 1_000_000)
    for combien in (plafond - 1_000, plafond // 2):
        derniere = mt5.copy_rates_from_pos(symbole, tf, 0, combien)
        if derniere is not None and len(derniere):
            morceaux.insert(0, derniere)
            break
    if not morceaux:
        code, message = mt5.last_error()
        raise RuntimeError(f"{symbole} {timeframe} : aucune barre ({code}, {message}). "
                           f"Le terminal télécharge peut-être encore l'historique.")
    tout = np.concatenate(morceaux[::-1])
    # Les bornes d'année se touchent : une barre peut apparaître deux fois.
    # np.unique rend les indices dans l'ORDRE DES TEMPS : c'est l'ordre chronologique, même
    # quand les morceaux ne se suivent pas (le bloc des dernières barres chevauche les années).
    _, uniques = np.unique(tout["time"], return_index=True)
    tout = tout[uniques]
    # ⛔ MESURÉ le 2026-09-17 : en « Unlimited », le bloc des dernières barres EUR/USD M15 et H1
    # remontait à 1971, UNE bougie par jour à 22 h, à 0,54 (historique reconstitué d'avant l'euro) :
    # 156 000 bougies factices dans un fichier intraday. On ne garde que la plage demandée.
    garde = (tout["time"] >= int(debut.timestamp())) & (tout["time"] < int(fin.timestamp()) + 86_400)
    return Barres.depuis_mt5(tout[garde], symbole=symbole, timeframe=timeframe)


def dernieres_barres(symbole: str, timeframe: str, combien: int = 600,
                     *, inclure_en_cours: bool = False) -> Barres:
    """Les N dernières barres. Par défaut SANS la barre en cours de formation :
    une décision prise sur une barre non close regarde un prix qui va encore
    changer, et ce n'est pas ce que le backtest a mesuré."""
    depart = 0 if inclure_en_cours else 1
    rates = mt5.copy_rates_from_pos(symbole, constante_tf(timeframe), depart, combien)
    if rates is None or len(rates) == 0:
        code, message = mt5.last_error()
        raise RuntimeError(f"{symbole} {timeframe} : aucune barre ({code}, {message})")
    return Barres.depuis_mt5(rates, symbole=symbole, timeframe=timeframe)


# --------------------------------------------------------------------------- #
#  Cache
# --------------------------------------------------------------------------- #

def enregistrer(barres: Barres, base: str, meta: dict) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = chemin_cache(base, barres.timeframe)
    np.savez_compressed(
        p, temps=barres.temps.astype("int64"), ouverture=barres.ouverture,
        haut=barres.haut, bas=barres.bas, cloture=barres.cloture,
        volume=barres.volume if barres.volume is not None else np.array([]),
        spread=barres.spread if barres.spread is not None else np.array([]),
        symbole=barres.symbole, timeframe=barres.timeframe,
        meta=json.dumps(meta, ensure_ascii=False))
    return p


def lire_cache(base: str = "EURUSD", timeframe: str = "H4") -> Barres | None:
    p = chemin_cache(base, timeframe)
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=False)
    volume = d["volume"] if d["volume"].size else None
    spread = d["spread"] if d["spread"].size else None
    return Barres(
        temps=d["temps"].astype("datetime64[s]"), ouverture=d["ouverture"],
        haut=d["haut"], bas=d["bas"], cloture=d["cloture"],
        volume=volume, spread=spread,
        symbole=str(d["symbole"]), timeframe=str(d["timeframe"]))


def meta_cache(base: str = "EURUSD", timeframe: str = "H4") -> dict:
    p = chemin_cache(base, timeframe)
    if not p.exists():
        return {}
    return json.loads(str(np.load(p, allow_pickle=False)["meta"]))


def charger_historique(base: str = "EURUSD", timeframe: str = "H4") -> Barres:
    """L'historique le plus long dont on dispose : MT5 d'abord, Deriv ensuite."""
    b = lire_cache(base, timeframe)
    if b is not None:
        return b
    from .donnees_deriv import lire_cache as lire_deriv
    b = lire_deriv(base, timeframe)
    if b is None:
        raise FileNotFoundError(
            f"Aucun historique {base} {timeframe}. Lancer : "
            f"python -m trading.noyau.donnees_mt5 {timeframe}")
    return b


# --------------------------------------------------------------------------- #
#  Export complet
# --------------------------------------------------------------------------- #

def chemin_profil(base: str) -> Path:
    return CACHE / f"{base.upper()}_courtier_mt5.json"


def mesurer_profil(c, symbole: str, *, jours_ticks: int = 1) -> dict:
    """Spécifications et coûts RÉELS, mesurés dans une session ouverte.

    Le spread facturé est la MÉDIANE DES TICKS (mesurée le 2026-09-16 sur
    149 485 ticks : 3 points), pas le champ `spread` des bougies.
    """
    from datetime import timedelta
    specs = c.specs(symbole)
    info = mt5.symbol_info(symbole)
    fin = datetime.now(timezone.utc)
    ticks = mt5.copy_ticks_range(symbole, fin - timedelta(days=jours_ticks), fin,
                                 mt5.COPY_TICKS_INFO)
    mediane = p90 = None
    if ticks is not None and len(ticks):
        ecarts = np.sort(np.round((ticks["ask"] - ticks["bid"]) / specs.point))
        mediane = float(ecarts[len(ecarts) // 2])
        p90 = float(ecarts[int(len(ecarts) * 0.9)])
    p = c.profil()
    compte = mt5.account_info()
    return {
        "mesure_le": fin.isoformat(timespec="seconds"),
        "courtier": p.societe, "serveur": p.serveur, "devise": p.devise,
        "demo": p.demo, "couverture": p.couverture, "levier": p.levier,
        "decalage_serveur_h": p.decalage_serveur_h,
        "symbole": symbole,
        "specs": {k: getattr(specs, k) for k in (
            "nom", "point", "digits", "volume_min", "volume_max", "volume_step",
            "valeur_tick", "taille_tick", "taille_contrat", "stops_level_points")},
        "spread_median_points": mediane, "spread_p90_points": p90,
        "ticks_mesures": 0 if ticks is None else int(len(ticks)),
        # swap_mode 1 = en points. Tout autre mode est noté et non facturé en
        # points, pour ne pas facturer un chiffre dans la mauvaise unité.
        "swap_mode": int(info.swap_mode),
        "prix_reference": float(mt5.symbol_info_tick(symbole).bid or 0.0),
        "swap_long": float(info.swap_long), "swap_short": float(info.swap_short),
        "mode_remplissage": int(c.mode_remplissage(symbole)),
        "limite_compte": {"limit_orders": int(compte.limit_orders) if compte else 0},
    }


def charger_profil(base: str = "EURUSD") -> dict | None:
    p = chemin_profil(base)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def specs_et_couts(base: str = "EURUSD", *, slippage_points: float = 1.0):
    """SpecsSymbole et ModeleCouts reconstruits depuis la dernière mesure.

    Le glissement n'est pas mesurable sans exécution réelle : 1 point par sens,
    toujours défavorable, jusqu'à ce que le journal des ordres en donne un vrai.
    """
    from ..backtest.couts import ModeleCouts
    from .risque import SpecsSymbole
    prof = charger_profil(base)
    if not prof:
        return None, None
    specs = SpecsSymbole(**prof["specs"])
    mode = prof.get("swap_mode")
    prix = prof.get("prix_reference") or 0.0
    if mode == 1:                                  # en points par lot et par nuit
        swap_l, swap_c = prof["swap_long"], prof["swap_short"]
    elif mode in (5, 6) and prix > 0:
        # En TAUX ANNUEL (%) : c'est le cas des indices chez Deriv (US Tech 100, mode 5).
        # Ramené en points par lot et par nuit au prix de référence mesuré. Ignorer ce
        # swap sous-estimait le portage d'une position tenue plusieurs jours.
        par_nuit = lambda taux: prix * taux / 100 / 360 / specs.point   # noqa: E731
        swap_l, swap_c = par_nuit(prof["swap_long"]), par_nuit(prof["swap_short"])
    else:
        swap_l = swap_c = 0.0
    couts = ModeleCouts(
        spread_points=prof.get("spread_median_points") or 3.0,
        spread_points_max=prof.get("spread_p90_points"),
        slippage_points=slippage_points,
        swap_long_points=swap_l,
        swap_short_points=swap_c,
    )
    return specs, couts


def exporter(timeframes=("H4", "D1", "H1"), base: str = "EURUSD",
             profil: str = "defaut", *, bavard: bool = True, depuis: int | None = None) -> dict[str, Path]:
    """Ouvre une session, lit tout l'historique disponible (ou depuis l'année `depuis`), l'écrit en cache.

    ⚠️ En M1, 20 ans font ~7 millions de barres : trop pour 8 Go de mémoire vive. `--depuis`
    borne la profondeur."""
    from .courtier import Courtier
    from .donnees_deriv import controler

    sorties: dict[str, Path] = {}
    with Courtier.depuis_profil(profil) as c:
        symbole = c.trouver_symbole(base)
        profil_c = c.profil()
        CACHE.mkdir(parents=True, exist_ok=True)
        mesure = mesurer_profil(c, symbole)
        chemin_profil(base).write_text(json.dumps(mesure, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
        if bavard:
            print(f"Profil du courtier -> {chemin_profil(base)}")
            print(f"  spread médian {mesure['spread_median_points']} pts "
                  f"(p90 {mesure['spread_p90_points']}) sur {mesure['ticks_mesures']} ticks · "
                  f"swap_mode {mesure['swap_mode']}")
        for tf in timeframes:
            b = lire_plage(symbole, tf, debut=datetime(depuis, 1, 1, tzinfo=timezone.utc) if depuis else None,
                           bavard=bavard)
            meta = {
                "source": "mt5", "courtier": profil_c.societe,
                "serveur": profil_c.serveur, "symbole_courtier": symbole,
                "decalage_serveur_h": profil_c.decalage_serveur_h,
                "exporte_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "barres": len(b),
                "debut": f"{b.quand(0):%Y-%m-%d %H:%M}",
                "fin": f"{b.quand(len(b) - 1):%Y-%m-%d %H:%M}",
            }
            sorties[tf] = enregistrer(b, base, meta)
            if bavard:
                print(f"\n{base} {tf} ({symbole} chez {profil_c.serveur})")
                print(controler(b))
                print(f"  -> {sorties[tf]}")
    return sorties


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    demandes = tuple(a for a in sys.argv[1:] if a in TIMEFRAMES_MT5) or ("H4", "D1", "H1")
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "EURUSD"
    depuis = int(sys.argv[sys.argv.index("--depuis") + 1]) if "--depuis" in sys.argv else None
    exporter(demandes, base=base, depuis=depuis)
