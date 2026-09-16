# -*- coding: utf-8 -*-
"""
Historique de prix par l'API publique de Deriv. Aucun jeton requis.

Découvert le 2026-09-16 : `ticks_history` répond **sans authentification**.
C'est ce qui a débloqué tout le projet alors que le pont MT5 refusait de
s'ouvrir. On peut donc mesurer un edge sur de vraies données avant même
d'avoir un compte utilisable.

    python trading/noyau/donnees_deriv.py EURUSD H4 6000

⚠️ Ce sont les prix de DERIV, pas une vérité universelle : chaque courtier a
son flux, ses mèches et ses spreads. C'est exactement ce qu'on veut — on
backteste sur les prix du courtier chez qui on tradera. Mais un edge mesuré ici
doit être re-mesuré chez un autre courtier avant d'être vendu comme portable.

⚠️ Les bougies de l'API n'ont NI volume NI spread : le spread doit venir de
`Courtier.couts()` (mesuré dans le terminal), pas d'ici.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    from websocket import create_connection
except ImportError:                                            # pragma: no cover
    create_connection = None

from ..strategies.base import Barres

URL = "wss://ws.derivws.com/websockets/v3?app_id={app}"
CACHE = Path(__file__).resolve().parent.parent / "donnees"

# Granularités acceptées par Deriv, en secondes.
GRANULARITE = {"M1": 60, "M2": 120, "M3": 180, "M5": 300, "M10": 600,
               "M15": 900, "M30": 1800, "H1": 3600, "H2": 7200,
               "H4": 14400, "H8": 28800, "D1": 86400}

MAX_PAR_APPEL = 5000        # plafond imposé par l'API


class DonneesIndisponibles(Exception):
    pass


def _symbole_deriv(paire: str) -> str:
    """EURUSD -> frxEURUSD. Le préfixe `frx` désigne le change chez Deriv."""
    p = paire.upper().replace("/", "").replace("_", "")
    return p if p.startswith("FRX") else f"frx{p}"


def telecharger(paire: str = "EURUSD", timeframe: str = "H4",
                barres_voulues: int = 6000, *, app_id: str = "1089",
                bavard: bool = True) -> Barres:
    """Télécharge en remontant le temps, page par page.

    L'API plafonne à 5 000 bougies par appel. Pour aller plus loin on redemande
    en fixant `end` juste avant la plus ancienne bougie déjà reçue.
    """
    if create_connection is None:
        raise DonneesIndisponibles(
            "Le paquet websocket-client est absent (pip install websocket-client).")
    if timeframe not in GRANULARITE:
        raise DonneesIndisponibles(
            f"Timeframe {timeframe!r} inconnu chez Deriv. Valeurs : "
            f"{', '.join(GRANULARITE)}")

    symbole = _symbole_deriv(paire)
    granularite = GRANULARITE[timeframe]
    ws = create_connection(URL.format(app=app_id), timeout=40)
    bougies: list[dict] = []
    fin: int | str = "latest"

    try:
        while len(bougies) < barres_voulues:
            reste = min(MAX_PAR_APPEL, barres_voulues - len(bougies))
            ws.send(json.dumps({
                "ticks_history": symbole, "style": "candles",
                "granularity": granularite, "count": reste,
                "end": fin, "adjust_start_time": 1,
            }))

            reponse = None
            for _ in range(60):
                r = json.loads(ws.recv())
                if r.get("msg_type") == "candles" or "error" in r:
                    reponse = r
                    break
            if reponse is None:
                raise DonneesIndisponibles("Aucune réponse de l'API après 60 messages.")
            if "error" in reponse:
                raise DonneesIndisponibles(
                    f"Deriv refuse : {reponse['error'].get('code')} — "
                    f"{reponse['error'].get('message')}")

            lot = reponse.get("candles", [])
            if not lot:
                if bavard:
                    print(f"  l'historique s'arrête ici ({len(bougies)} bougies)")
                break

            bougies = lot + bougies
            fin = lot[0]["epoch"] - 1           # on recule d'une seconde
            if bavard:
                depuis = datetime.fromtimestamp(lot[0]["epoch"], timezone.utc)
                print(f"  {len(bougies):>6} bougies · remonté jusqu'au "
                      f"{depuis:%Y-%m-%d}")
            if len(lot) < reste:
                break
            time.sleep(0.4)                     # on ne martèle pas l'API
    finally:
        ws.close()

    if not bougies:
        raise DonneesIndisponibles(f"Aucune donnée pour {symbole} en {timeframe}.")

    # Doublons possibles aux jointures des pages : on garde une bougie par date.
    vues: dict[int, dict] = {}
    for b in bougies:
        vues[int(b["epoch"])] = b
    ordonnees = [vues[k] for k in sorted(vues)]

    return Barres(
        temps=np.array([int(b["epoch"]) for b in ordonnees], dtype="datetime64[s]"),
        ouverture=np.array([float(b["open"]) for b in ordonnees]),
        haut=np.array([float(b["high"]) for b in ordonnees]),
        bas=np.array([float(b["low"]) for b in ordonnees]),
        cloture=np.array([float(b["close"]) for b in ordonnees]),
        spread=None,          # l'API n'en donne pas : il vient du terminal
        symbole=paire.upper(), timeframe=timeframe,
    )


# --- Cache local ---------------------------------------------------------- #

def _chemin_cache(paire: str, timeframe: str) -> Path:
    return CACHE / f"{paire.upper()}_{timeframe}.npz"


def enregistrer(barres: Barres) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = _chemin_cache(barres.symbole, barres.timeframe)
    np.savez_compressed(
        p, temps=barres.temps.astype("int64"), ouverture=barres.ouverture,
        haut=barres.haut, bas=barres.bas, cloture=barres.cloture,
        symbole=barres.symbole, timeframe=barres.timeframe)
    return p


def lire_cache(paire: str = "EURUSD", timeframe: str = "H4") -> Barres | None:
    p = _chemin_cache(paire, timeframe)
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=False)
    return Barres(
        temps=d["temps"].astype("datetime64[s]"), ouverture=d["ouverture"],
        haut=d["haut"], bas=d["bas"], cloture=d["cloture"],
        symbole=str(d["symbole"]), timeframe=str(d["timeframe"]))


def charger(paire: str = "EURUSD", timeframe: str = "H4",
            barres_voulues: int = 6000, *, forcer: bool = False,
            bavard: bool = True) -> Barres:
    """Le cache d'abord, le réseau ensuite. `forcer=True` retélécharge."""
    if not forcer:
        b = lire_cache(paire, timeframe)
        if b is not None and len(b) >= barres_voulues * 0.9:
            if bavard:
                print(f"  cache : {len(b)} barres, du {b.quand(0):%Y-%m-%d} "
                      f"au {b.quand(len(b) - 1):%Y-%m-%d}")
            return b
    b = telecharger(paire, timeframe, barres_voulues, bavard=bavard)
    enregistrer(b)
    return b


def controler(barres: Barres) -> str:
    """Un historique troué fabrique des résultats faux sans lever d'erreur."""
    n = len(barres)
    heures = {"M1": 1 / 60, "M5": 5 / 60, "M15": .25, "M30": .5, "H1": 1,
              "H4": 4, "D1": 24}.get(barres.timeframe, 4)
    trous = barres.trous(ecart_max_heures=heures * 2.5)

    incoherentes = int(np.sum((barres.haut < barres.bas)
                              | (barres.haut < barres.ouverture)
                              | (barres.haut < barres.cloture)
                              | (barres.bas > barres.ouverture)
                              | (barres.bas > barres.cloture)))
    plates = int(np.sum(barres.haut == barres.bas))

    lignes = [
        f"  Barres            {n}",
        f"  Période           {barres.quand(0):%Y-%m-%d} -> "
        f"{barres.quand(n - 1):%Y-%m-%d}",
        f"  Prix              {barres.cloture.min():.5f} à {barres.cloture.max():.5f}",
        f"  Bougies incohérentes  {incoherentes}"
        + ("   ⛔ à ne pas utiliser" if incoherentes else "   ✓"),
        f"  Bougies plates        {plates}"
        + ("   (marché fermé / illiquide)" if plates else ""),
        f"  Trous (hors week-end) {len(trous)}",
    ]
    for a, b, h in trous[:5]:
        lignes.append(f"      {a:%Y-%m-%d %H:%M} -> {b:%Y-%m-%d %H:%M}  ({h:.0f} h)")
    if len(trous) > 5:
        lignes.append(f"      ... et {len(trous) - 5} autres")
    return "\n".join(lignes)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    paire = sys.argv[1] if len(sys.argv) > 1 else "EURUSD"
    tf = sys.argv[2] if len(sys.argv) > 2 else "H4"
    combien = int(sys.argv[3]) if len(sys.argv) > 3 else 6000

    print(f"Téléchargement {paire} {tf} ({combien} barres) depuis l'API publique Deriv…")
    b = charger(paire, tf, combien, forcer="--forcer" in sys.argv)
    print()
    print("CONTRÔLE DE L'HISTORIQUE")
    print(controler(b))
    print(f"\n  Cache : {_chemin_cache(paire, tf)}")
