# -*- coding: utf-8 -*-
"""
L'historique M1 que Deriv n'a pas, chez Dukascopy (gratuit, sans compte, sans carte).

    python -m trading.recherche.dukascopy --base NAS100 --de 2013 --a 2023
    python -m trading.recherche.dukascopy --base EURUSD --de 2003 --a 2011
    python -m trading.recherche.dukascopy --sonder            # où commence chaque instrument

Pourquoi : chez Deriv, le NAS100 ne remonte qu'au 2024-01-22 et l'EUR/USD M1 qu'à 2019. Une recherche
de scalping qui se juge sur deux ans et demi ne se juge pas. Et surtout, **il faut des années que la
recherche n'a jamais vues** : c'est le rôle du scellé (`scelle.py`).

Sondé le 2026-09-17, une journée à la fois : le M1 commence le **2003-05-04** pour `eurusd` et en
**janvier 2013** pour `usatechidxusd` (2012 rend zéro barre).

Trois précautions, toutes payées ailleurs dans ce dépôt :
  · **bid ET ask.** Le spread d'époque est mesuré, pas supposé : appliquer le spread Deriv de 2026 à
    l'EUR/USD de 2004 (où il valait plusieurs pips) rendrait rentable ce qui ne l'était pas.
  · **Les bougies plates sont exclues** (`-fl` absent) : une minute sans transaction n'est pas une
    minute de marché, et elle fabriquerait de faux balayages de stop.
  · **Tout est en UTC** (`-utc 0`), comme le serveur Deriv (décalage mesuré : 0 h). Un flux décalé
    d'une heure déplacerait toutes les séances.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import numpy as np

from ..noyau.chemins import dossier_donnees

SYMBOLES = {"EURUSD": "eurusd", "NAS100": "usatechidxusd"}
# Sondé le 2026-09-17 (une journée par appel) : premier jour qui rend des barres M1.
DEBUT_M1 = {"EURUSD": date(2003, 5, 5), "NAS100": date(2013, 1, 7)}
DOSSIER = dossier_donnees() / "duka"
COLONNES = ("temps", "ouverture", "haut", "bas", "cloture", "volume", "spread_points")


def chemin_cache(base: str, tf: str = "M1") -> Path:
    return dossier_donnees() / f"{base.upper()}_{tf}_duka.npz"


def _npx() -> str:
    for nom in ("npx.cmd", "npx"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    raise RuntimeError("npx introuvable : Node.js est nécessaire pour dukascopy-node.")


def _appeler(instrument: str, debut: date, fin: date, prix: str, dossier: Path, tf: str) -> Path | None:
    """Un appel à dukascopy-node. Rend le CSV produit, ou None si la plage est vide."""
    avant = {p.name for p in dossier.glob("*.csv")}
    cmd = [_npx(), "-y", "dukascopy-node@latest", "-i", instrument, "-from", debut.isoformat(),
           "-to", fin.isoformat(), "-t", tf.lower(), "-p", prix, "-utc", "0", "-v", "-f", "csv",
           # ⚠️ Mesuré : `-re` (réessayer les réponses vides) fait ÉCHOUER le mois entier, parce que
           # les heures de week-end et de fermeture sont légitimement vides. `-fr` garde la main.
           "-dir", str(dossier), "-bs", "40", "-bp", "200", "-r", "3", "-rp", "1500", "-fr", "-s"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"dukascopy-node {instrument} {debut}→{fin} {prix} : {r.stderr.strip()[:400]}")
    nouveaux = [p for p in dossier.glob("*.csv") if p.name not in avant]
    return nouveaux[0] if nouveaux else None


def _lire(csv: Path | None):
    import pandas as pd
    if csv is None or csv.stat().st_size == 0:
        return None
    d = pd.read_csv(csv)
    if d.empty:
        return None
    return d


def telecharger_mois(base: str, an: int, mois: int, tf: str = "M1") -> dict | None:
    """Un mois de barres, bid et ask alignés sur l'horodatage. None si le marché n'a rien donné."""
    import pandas as pd
    instrument = SYMBOLES[base.upper()]
    debut = date(an, mois, 1)
    fin = date(an + (mois == 12), mois % 12 + 1, 1)
    with tempfile.TemporaryDirectory(prefix="duka_") as tmp:
        dossier = Path(tmp)
        bid = _lire(_appeler(instrument, debut, fin, "bid", dossier, tf))
        ask = _lire(_appeler(instrument, debut, fin, "ask", dossier, tf))
    if bid is None:
        return None
    if ask is None:                                  # pas d'ask : le spread sera celui de Deriv
        ask = bid.assign(open=np.nan, close=np.nan)
    j = bid.merge(ask[["timestamp", "open", "close"]], on="timestamp", how="left",
                  suffixes=("", "_ask"))
    ecart = ((j["open_ask"] - j["open"]) + (j["close_ask"] - j["close"])) / 2.0
    return {"temps": (j["timestamp"].to_numpy() // 1000).astype(np.int64),
            "ouverture": j["open"].to_numpy(float), "haut": j["high"].to_numpy(float),
            "bas": j["low"].to_numpy(float), "cloture": j["close"].to_numpy(float),
            "volume": j["volume"].to_numpy(np.float32),
            "ecart_prix": np.clip(ecart.to_numpy(float), 0.0, None)}


def telecharger_annee(base: str, an: int, tf: str = "M1", *, refaire: bool = False) -> Path | None:
    """Une année, rangée en `donnees/duka/BASE_TF_ANNEE.npz`. Reprise possible : une année déjà
    rangée n'est pas retéléchargée."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    cible = DOSSIER / f"{base.upper()}_{tf}_{an}.npz"
    if cible.exists() and not refaire:
        return cible
    morceaux = []
    for mois in range(1, 13):
        if date(an, mois, 1) > date.today():
            break
        m = telecharger_mois(base, an, mois, tf)
        if m:
            morceaux.append(m)
        print(f"    {base} {an}-{mois:02d} : {0 if not m else len(m['temps']):6d} barres", flush=True)
    if not morceaux:
        return None
    d = {c: np.concatenate([m[c] for m in morceaux]) for c in morceaux[0]}
    ordre = np.argsort(d["temps"], kind="stable")
    _, uniques = np.unique(d["temps"][ordre], return_index=True)
    d = {c: v[ordre][uniques] for c, v in d.items()}
    np.savez_compressed(cible, **d)
    return cible


def assembler(base: str, de: int, a: int, tf: str = "M1") -> Path:
    """Les années rangées deviennent un seul fichier, au format lu par `banc.charger(source='duka')`."""
    parts = []
    for an in range(de, a + 1):
        p = DOSSIER / f"{base.upper()}_{tf}_{an}.npz"
        if p.exists():
            parts.append(np.load(p, allow_pickle=False))
    if not parts:
        raise FileNotFoundError(f"aucune année rangée pour {base} {tf} ({de}-{a})")
    d = {c: np.concatenate([p[c] for p in parts]) for c in parts[0].files}
    _, uniques = np.unique(d["temps"], return_index=True)
    d = {c: v[uniques] for c, v in d.items()}
    cible = chemin_cache(base, tf)
    # ⚠️ Écriture ATOMIQUE : un lecteur qui ouvre un .npz à moitié écrit reçoit « File is not a zip
    # file » (mesuré le 2026-09-17, pendant que l'assemblage tournait en fond). On écrit à côté,
    # puis on remplace d'un coup.
    # (le nom doit finir par .npz, sinon numpy en rajoute un)
    provisoire = cible.with_name(cible.stem + ".tmp.npz")
    meta = {"source": "dukascopy", "instrument": SYMBOLES[base.upper()], "annees": [de, a],
            "barres": int(len(d["temps"])), "heure": "UTC",
            "debut": str(d["temps"][0].astype("datetime64[s]")), "fin": str(d["temps"][-1].astype("datetime64[s]")),
            "ecart_prix": "spread d'époque mesuré (ask - bid), en PRIX"}
    np.savez_compressed(provisoire, meta=json.dumps(meta, ensure_ascii=False), **d)
    provisoire.replace(cible)
    print(f"  {base} {tf} : {meta['barres']} barres, {meta['debut']} → {meta['fin']}, "
          f"{cible.stat().st_size / 1e6:.1f} Mo", flush=True)
    return cible


def lire_cache(base: str, tf: str = "M1"):
    """(dict de tableaux, meta) ou None."""
    p = chemin_cache(base, tf)
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=False)
    tableaux = {c: d[c] for c in d.files if c != "meta"}
    tableaux["temps"] = tableaux["temps"].astype("datetime64[s]")
    return tableaux, json.loads(str(d["meta"]))


def verifier_alignement(base: str = "EURUSD", an: int = 2024, mois: int = 6) -> dict:
    """Les deux flux racontent-ils la MÊME minute ?

    On télécharge un mois que les deux possèdent et on corrèle les rendements minute à minute, puis
    aux décalages de ±1 et ±60 minutes. Un flux décalé d'une heure donnerait une corrélation forte
    au mauvais décalage : toutes les séances seraient fausses et rien ne le dirait.
    Mesuré le 2026-09-17 (EUR/USD, juin 2024) : **0,985 au décalage nul**, 0,02 à ±1 minute, 0,01 à
    ±60, écart de prix médian 1 point. Les deux flux sont en UTC, comme le serveur Deriv.
    """
    from .banc import charger
    m = telecharger_mois(base, an, mois)
    if m is None:
        return {"erreur": "aucune barre Dukascopy sur ce mois"}
    s = charger(base, "M1")
    communs, i_d, i_m = np.intersect1d(m["temps"].astype("datetime64[s]"), s.temps,
                                       return_indices=True)
    if len(communs) < 1000:
        return {"erreur": f"trop peu de minutes communes ({len(communs)})"}
    rd, rm = np.diff(m["cloture"][i_d]), np.diff(s.cloture[i_m])
    sortie = {"base": base, "mois": f"{an}-{mois:02d}", "minutes_communes": int(len(communs)),
              "ecart_prix_median_points": round(float(np.median(np.abs(
                  m["cloture"][i_d] - s.cloture[i_m])) / s.point), 2)}
    for dec in (-60, -1, 0, 1, 60):
        sortie[f"correlation_{dec:+d}min"] = round(float(np.corrcoef(rd, np.roll(rm, dec))[0, 1]), 4)
    return sortie


def sonder(base: str, annees=range(2003, 2025)) -> None:
    """La première année qui rend des barres, une journée par appel (rapide et poli)."""
    instrument = SYMBOLES[base.upper()]
    with tempfile.TemporaryDirectory(prefix="duka_") as tmp:
        for an in annees:
            j = date(an, 1, 8)
            d = _lire(_appeler(instrument, j, date(an, 1, 9), "bid", Path(tmp), "M1"))
            n = 0 if d is None else len(d)
            print(f"  {base} {an}-01-08 : {n} barres M1", flush=True)
            if n:
                return


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="NAS100")
    p.add_argument("--de", type=int)
    p.add_argument("--a", type=int, default=date.today().year)
    p.add_argument("--tf", default="M1")
    p.add_argument("--sonder", action="store_true")
    p.add_argument("--refaire", action="store_true")
    a = p.parse_args()
    base = a.base.upper()
    if a.sonder:
        for b in SYMBOLES:
            sonder(b)
        return 0
    de = a.de or DEBUT_M1[base].year
    for an in range(de, a.a + 1):
        print(f"  {base} {an}", flush=True)
        telecharger_annee(base, an, a.tf, refaire=a.refaire)
    assembler(base, de, a.a, a.tf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
