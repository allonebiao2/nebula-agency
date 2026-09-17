# -*- coding: utf-8 -*-
"""
L'historique des annonces économiques, pour qu'un backtest sache quand l'agent en direct se serait abstenu.

    python -m trading.recherche.annonces --telecharger 2019-01-01 2026-09-20
    python -m trading.recherche.annonces --verifier

Source : les pages hebdomadaires du calendrier Forex Factory, la même maison que le flux
`ff_calendar_thisweek.json` que lit l'agent (`noyau/calendrier.py`). Chaque page embarque ses
événements en JSON avec un `dateline` : un horodatage Unix, donc AUCUN fuseau à deviner.

⛔ 2026-09-17 : le jeu de données « Forex Factory 2007-2025 » de Hugging Face a été écarté. Ses heures
sont écrites avec un décalage (+03:30), mais 40 à 50 % des annonces majeures USD/EUR y sont à 00:00 :
l'heure est PERDUE (le NFP de 2019 à 2025 y est noté à minuit). Une fenêtre « 30 min avant l'annonce »
posée sur minuit aurait bloqué la nuit et laissé passer le NFP.

Politesse : une page toutes les 2,5 s, cache par semaine sur le disque (`trading/donnees/annonces/ff/`),
arrêt net au premier refus. Une semaine en cours n'est jamais mise en cache (elle est incomplète).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from ..noyau.chemins import dossier_donnees

URL = "https://www.forexfactory.com/calendar?week={}"
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
MOIS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
# Mêmes devises que l'agent : un EUR/USD bouge sur les deux, le NAS100 sur le dollar.
DEVISES = {"EURUSD": ("USD", "EUR"), "NAS100": ("USD",)}


def dossier() -> Path:
    d = dossier_donnees() / "annonces" / "ff"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _dimanche(j: date) -> date:
    return j - timedelta(days=(j.weekday() + 1) % 7)


def _cle_semaine(dim: date) -> str:
    return f"{MOIS[dim.month - 1]}{dim.day}.{dim.year}"


def extraire(html: str) -> list[dict]:
    """Les événements de la page, réduits à ce qui sert. Lève ValueError si la page n'en porte pas."""
    i = html.find("window.calendarComponentStates[1]")
    j = html.find("days: ", i)
    if i < 0 or j < 0:
        raise ValueError("page sans calendrier (refus, défi anti-robot ou format changé)")
    jours, _ = json.JSONDecoder().raw_decode(html[j + len("days: "):])
    sortie = []
    for jour in jours:
        for e in jour["events"]:
            sortie.append({"t": int(e["dateline"]), "devise": e.get("currency", ""),
                           "impact": e.get("impactName", ""), "nom": e.get("name", ""),
                           "heure": e.get("timeLabel", ""),
                           # La SURPRISE : ce qui bouge un marché n'est pas l'annonce, c'est l'écart
                           # au consensus. `actualBetterWorse` vaut +1 (meilleur que prévu pour la
                           # devise), -1 (pire) ou 0 ; `actual`/`forecast` gardent le chiffre brut.
                           "reel": e.get("actual", ""), "prevu": e.get("forecast", ""),
                           "precedent": e.get("previous", ""),
                           "mieux_pire": int(e.get("actualBetterWorse") or 0)})
    return sortie


def _nombre(texte: str) -> float:
    """« 0,4 % », « -12,3K », « 1.05M » → un nombre. NaN si ce n'est pas chiffré (certaines annonces
    ne publient qu'un texte : on ne devine pas)."""
    if not texte:
        return float("nan")
    t = texte.strip().replace(",", "").replace("%", "").replace("$", "").replace("€", "")
    facteur = 1.0
    if t and t[-1] in "KMBT":
        facteur = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}[t[-1]]
        t = t[:-1]
    try:
        return float(t) * facteur
    except ValueError:
        return float("nan")


def surprises(base: str, *, impacts=("high",)) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(instants, signe de la surprise pour la DEVISE, ampleur relative) des annonces chiffrées.

    Le signe vient de Forex Factory (`actualBetterWorse`), qui sait si « plus bas » est meilleur
    (le chômage, par exemple). L'ampleur est |réel - prévu| / |prévu|, bornée : elle sépare la
    surprise de routine de celle qui déplace un marché. ⚠️ Pour le NAS100 on ne garde que l'USD,
    et le signe reste « bon pour le dollar », pas « bon pour l'indice » : c'est au modèle d'apprendre
    le rapport entre les deux, pas à nous de le décréter.
    """
    devises = set(DEVISES[base.upper()])
    t, signe, ampleur = [], [], []
    for f in sorted(dossier().glob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if e["devise"] not in devises or e["impact"] not in impacts:
                continue
            if e.get("heure", "").lower() == "all day" or not e.get("reel"):
                continue
            reel, prevu = _nombre(e.get("reel", "")), _nombre(e.get("prevu", ""))
            if not np.isfinite(reel) or not np.isfinite(prevu):
                continue
            t.append(int(e["t"]))
            signe.append(float(e.get("mieux_pire", 0)))
            denom = max(abs(prevu), 1e-9)
            ampleur.append(min(abs(reel - prevu) / denom, 10.0))
    if not t:
        vide = np.array([], dtype="datetime64[s]")
        return vide, np.array([]), np.array([])
    ordre = np.argsort(t, kind="stable")
    return (np.array(t, dtype="int64")[ordre].astype("datetime64[s]"),
            np.array(signe)[ordre], np.array(ampleur)[ordre])


def telecharger(debut: date, fin: date, *, pause_s: float = 2.5, rafraichir: bool = False) -> int:
    """`rafraichir` : reprendre les semaines déjà en cache. Sert quand on enrichit ce qu'on extrait
    (le 2026-09-17 : le réel, le prévu et le signe de la surprise, absents des premières collectes)."""
    d = dossier()
    aujourd_hui = datetime.now(timezone.utc).date()
    dim = _dimanche(debut)
    n = 0
    while dim <= fin:
        cible = d / f"{dim.isoformat()}.json"
        en_cours = dim + timedelta(days=7) > aujourd_hui
        manquant = not cible.exists()
        if not manquant and rafraichir:
            try:
                manquant = "mieux_pire" not in (json.loads(cible.read_text(encoding="utf-8")) or [{}])[0]
            except (json.JSONDecodeError, IndexError, KeyError):
                manquant = True
        if manquant or en_cours:
            req = urllib.request.Request(URL.format(_cle_semaine(dim)), headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                evenements = extraire(r.read().decode("utf-8", errors="replace"))
            if not en_cours:
                cible.write_text(json.dumps(evenements, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            n += 1
            print(f"  {dim} : {len(evenements)} événements", flush=True)
            time.sleep(pause_s)
        dim += timedelta(days=7)
    return n


def charger(base: str, *, impacts=("high",)) -> tuple[np.ndarray, list[str], tuple[str, str]]:
    """Instants (datetime64[s], UTC, triés) des annonces qui comptent pour `base`, leurs noms, et la
    période couverte par le cache. Les événements « All Day » (jours fériés) n'ont pas d'heure : exclus.
    ⚠️ Hors de la période couverte, l'absence d'annonce ne veut rien dire : l'appelant doit la lire."""
    devises = set(DEVISES[base.upper()])
    fichiers = sorted(dossier().glob("*.json"))
    if not fichiers:
        raise FileNotFoundError("aucune semaine en cache : python -m trading.recherche.annonces --telecharger ...")
    temps, noms = [], []
    for f in fichiers:
        for e in json.loads(f.read_text(encoding="utf-8")):
            if e["devise"] in devises and e["impact"] in impacts and e["heure"].lower() != "all day":
                temps.append(e["t"])
                noms.append(f"{e['devise']} {e['nom']}")
    ordre = np.argsort(temps, kind="stable")
    t = np.array(temps, dtype="int64")[ordre].astype("datetime64[s]")
    couverture = (fichiers[0].stem, (date.fromisoformat(fichiers[-1].stem) + timedelta(days=7)).isoformat())
    return t, [noms[k] for k in ordre], couverture


def fenetre_bloquee(temps_barres: np.ndarray, annonces: np.ndarray, *, avant_min: int = 30,
                    apres_min: int = 15, minutes_barre: int = 1) -> np.ndarray:
    """True pour chaque barre dont l'OUVERTURE ou la CLÔTURE tombe dans [annonce - avant, annonce + après].
    C'est la règle de `noyau/calendrier.py`, appliquée à l'instant où l'ordre partirait."""
    if len(annonces) == 0:
        return np.zeros(len(temps_barres), dtype=bool)
    debut = temps_barres.astype("datetime64[s]")
    bloque = np.zeros(len(debut), dtype=bool)
    for decalage in (0, minutes_barre * 60):
        t = debut + np.timedelta64(decalage, "s")
        k = np.searchsorted(annonces, t, side="left")          # première annonce >= t
        suivante = annonces[np.minimum(k, len(annonces) - 1)]
        precedente = annonces[np.maximum(k - 1, 0)]
        proche_avant = (k < len(annonces)) & ((suivante - t) <= np.timedelta64(avant_min * 60, "s"))
        proche_apres = (k > 0) & ((t - precedente) <= np.timedelta64(apres_min * 60, "s"))
        bloque |= proche_avant | proche_apres
    return bloque


def prochaine_annonce(temps_barres: np.ndarray, annonces: np.ndarray) -> np.ndarray:
    """Pour chaque barre, l'instant (datetime64[s]) de la prochaine annonce strictement après son ouverture."""
    k = np.searchsorted(annonces, temps_barres.astype("datetime64[s]"), side="right")
    loin = np.datetime64("2100-01-01T00:00:00")
    return np.where(k < len(annonces), annonces[np.minimum(k, len(annonces) - 1)], loin)


def verifier() -> int:
    """Les heures que tout le monde connaît : NFP et IPC à 08:30 New York, FOMC à 14:00 New York."""
    import pandas as pd
    t, noms, couv = charger("EURUSD")
    df = pd.DataFrame({"t": pd.to_datetime(t).tz_localize("UTC"), "nom": noms})
    df["ny"] = df.t.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
    print(f"couverture {couv[0]} -> {couv[1]} · {len(df)} annonces fortes USD/EUR")
    ok = True
    for nom, attendu in (("USD Non-Farm Employment Change", "08:30"), ("USD CPI m/m", "08:30"),
                         ("USD Federal Funds Rate", "14:00")):
        s = df[df.nom == nom]
        part = float((s.ny == attendu).mean()) if len(s) else 0.0
        print(f"  {nom:36s} {len(s):3d} fois · {100 * part:5.1f} % à {attendu} New York · {s.ny.value_counts().head(3).to_dict()}")
        ok &= len(s) > 0 and part >= 0.9
    return 0 if ok else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--telecharger", nargs=2, metavar=("DEBUT", "FIN"))
    p.add_argument("--rafraichir", action="store_true", help="reprendre les semaines déjà en cache")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.telecharger:
        n = telecharger(date.fromisoformat(a.telecharger[0]), date.fromisoformat(a.telecharger[1]),
                        rafraichir=a.rafraichir)
        print(f"{n} semaines téléchargées")
    if a.verifier:
        return verifier()
    return 0


if __name__ == "__main__":
    sys.exit(main())
