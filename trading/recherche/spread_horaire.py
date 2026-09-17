# -*- coding: utf-8 -*-
"""
Le spread RÉEL minute par minute de la journée, mesuré sur les ticks du courtier.

    python -m trading.recherche.spread_horaire --jours 28
    python -m trading.recherche.spread_horaire --sonder        # jusqu'où remonte l'historique de ticks

Pourquoi : le profil du courtier donne UNE médiane (3 points sur l'EUR/USD). Pour du scalping M1 elle
ment deux fois : le spread s'écarte au rollover et à l'ouverture du dimanche, justement les minutes
où un balayage de liquidité « en début d'Asie » se produit. Et un stop de 2 pips paie son spread
en entier : le coût EN R dépend de la minute.

Méthode : pour chaque jour, médiane des ticks de chaque minute (chaque minute compte UNE fois : une
minute agitée n'a pas plus de poids qu'une minute calme), puis médiane et p90
de ces valeurs sur tous les jours, pour chaque minute de la journée en heure de NEW YORK (le rollover
est à 17:00 New York toute l'année : 21:00 UTC l'été, 22:00 l'hiver). Le dimanche a son propre profil.

⛔ Deriv ne sert AUCUN tick passé (sondé le 2026-09-17 : 0 tick rendu pour la veille comme pour 2019) :
le profil utilisé vient donc de `--bougies` (forme tirée du champ `spread` des M1 2025-2026, niveau
recalé sur la médiane des ticks du jour). Mesuré ainsi : EUR/USD 3 points toute la journée, 35 points
de médiane entre 17:00 et 18:00 New York et jusqu'à 100 à 17:01 ; NAS100 70 points fixes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

from ..noyau.chemins import fichier


def chemin(base: str):
    return fichier(f"{base.upper()}_spread_minute.json")


def mesurer(base: str, jours: int = 28) -> dict:
    import MetaTrader5 as mt5
    from ..noyau.courtier import Courtier
    par_jour: dict[int, list[np.ndarray]] = {}          # jour de semaine -> [spreads par minute (1440)]
    with Courtier.depuis_profil("defaut") as c:
        symbole = c.trouver_symbole(base)
        point = c.specs(symbole).point
        fin = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        n_ticks = 0
        for d in range(jours, 0, -1):
            debut = fin - timedelta(days=d)
            t = mt5.copy_ticks_range(symbole, debut, debut + timedelta(days=1), mt5.COPY_TICKS_INFO)
            if t is None or len(t) < 1000:
                continue
            n_ticks += len(t)
            minute, _ = minute_ny(t["time"].astype("datetime64[s]"))   # clé New York, comme le profil lu
            ecart = np.round((t["ask"] - t["bid"]) / point)
            prof = np.full(1440, np.nan)
            ordre = np.argsort(minute, kind="stable")              # une journée UTC chevauche deux jours New York
            minute, ecart = minute[ordre], ecart[ordre]
            bornes = np.searchsorted(minute, np.arange(1441))
            for m in range(1440):
                if bornes[m + 1] > bornes[m]:
                    prof[m] = np.median(ecart[bornes[m]:bornes[m + 1]])
            par_jour.setdefault(debut.weekday(), []).append(prof)
    semaine = np.vstack([p for j, lst in par_jour.items() if j < 5 for p in lst])
    dimanche = np.vstack(par_jour[6]) if 6 in par_jour else np.full((1, 1440), np.nan)
    with np.errstate(all="ignore"):
        def resume(m):
            return (np.nanmedian(m, axis=0), np.nanpercentile(m, 90, axis=0))
        s50, s90 = resume(semaine)
        d50, d90 = resume(dimanche)
    global_median = float(np.nanmedian(semaine))
    def propre(v):
        return [None if np.isnan(x) else round(float(x), 1) for x in v]
    return {"base": base.upper(), "symbole": symbole, "mesure_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "jours": jours, "ticks": int(n_ticks), "jours_semaine": int(len(semaine)), "dimanches": int(len(par_jour.get(6, []))),
            "unite": "points", "heure": "UTC (heure serveur)", "median_global": global_median,
            "semaine_p50": propre(s50), "semaine_p90": propre(s90), "dimanche_p50": propre(d50), "dimanche_p90": propre(d90)}


def depuis_bougies(base: str, *, depuis: str = "2025-01-01") -> dict:
    """Le profil quand les ticks passés ne sont pas servis (Deriv, vérifié le 2026-09-17 : 0 tick
    rendu pour n'importe quel jour passé, même la veille). La FORME minute par minute vient du champ
    `spread` des bougies M1 récentes ; le NIVEAU est recalé sur la médiane mesurée sur ticks (profil
    du courtier). ⚠️ Le champ `spread` d'une bougie n'est pas le spread payé (il vaut 2 là où les
    ticks disent 3) : il ne sert qu'à dire QUAND le spread s'écarte, pas de combien en absolu.
    ⚠️ Avant 2025 le champ est inutilisable (50 partout en 2019, 0 en 2022) : on n'en lit rien."""
    from ..noyau.donnees_mt5 import charger_profil, lire_cache
    b = lire_cache(base, "M1")
    prof = charger_profil(base) or {}
    garde = b.temps >= np.datetime64(depuis)
    sp = b.spread[garde].astype(float)
    minute, jour = minute_ny(b.temps[garde])
    brut_med = float(np.median(sp[jour < 5]))
    tick_med = float(prof.get("spread_median_points") or brut_med)
    echelle = tick_med / brut_med if brut_med > 0 else 1.0
    import pandas as pd
    def profil(masque, q):
        serie = pd.Series(sp[masque]).groupby(minute[masque]).quantile(q)
        v = np.full(1440, np.nan)
        v[serie.index.to_numpy()] = serie.to_numpy() * echelle
        return v
    semaine, dimanche = jour < 5, jour == 6
    def propre(v):
        return [None if np.isnan(x) else round(float(x), 1) for x in v]
    return {"base": base.upper(), "source": f"champ spread des bougies M1 depuis {depuis}, recalé sur la médiane des ticks",
            "mesure_le": datetime.now(timezone.utc).isoformat(timespec="seconds"), "bougies": int(garde.sum()),
            "echelle": round(echelle, 4), "median_ticks": tick_med, "median_bougies": brut_med,
            "unite": "points", "heure": "New York (le rollover est à 17:00 New York toute l'année)", "median_global": tick_med,
            "semaine_p50": propre(profil(semaine, 0.5)), "semaine_p90": propre(profil(semaine, 0.9)),
            "dimanche_p50": propre(profil(dimanche, 0.5)), "dimanche_p90": propre(profil(dimanche, 0.9))}


def profil_minute(base: str, *, quantile: str = "p50") -> tuple[np.ndarray, np.ndarray]:
    """(semaine, dimanche) : spread en POINTS pour chaque minute UTC. Minute sans mesure = médiane globale."""
    d = json.loads(chemin(base).read_text(encoding="utf-8"))
    def remplir(v):
        a = np.array([np.nan if x is None else x for x in v], dtype=float)
        return np.where(np.isnan(a), d["median_global"], a)
    return remplir(d[f"semaine_{quantile}"]), remplir(d[f"dimanche_{quantile}"])


def minute_ny(temps_utc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(minute du jour, jour de semaine lundi=0) en heure de New York. ⚠️ Pas en UTC : le rollover
    est à 17:00 New York, soit 21:00 UTC l'été et 22:00 UTC l'hiver. Un profil en UTC le rate l'hiver."""
    import pandas as pd
    idx = pd.DatetimeIndex(temps_utc).tz_localize("UTC").tz_convert("America/New_York")
    return (idx.hour * 60 + idx.minute).to_numpy().astype(np.int64), idx.dayofweek.to_numpy().astype(np.int64)


def spread_par_barre(base: str, temps: np.ndarray, *, quantile: str = "p50") -> np.ndarray:
    """Le spread (points) attendu à l'ouverture de chaque barre, selon sa minute et son jour (New York)."""
    semaine, dimanche = profil_minute(base, quantile=quantile)
    minute, jour = minute_ny(temps)
    return np.where(jour == 6, dimanche[minute], semaine[minute])


def sonder(base: str) -> None:
    import MetaTrader5 as mt5
    from ..noyau.courtier import Courtier
    with Courtier.depuis_profil("defaut") as c:
        symbole = c.trouver_symbole(base)
        for a in ("2019-06-04", "2021-06-02", "2023-06-06", "2024-06-04", "2025-06-03", "2026-06-02"):
            d = datetime.fromisoformat(a).replace(hour=13, tzinfo=timezone.utc)
            t = mt5.copy_ticks_range(symbole, d, d + timedelta(minutes=10), mt5.COPY_TICKS_INFO)
            print(f"  {base} {a} 13:00-13:10 UTC : {0 if t is None else len(t)} ticks")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--jours", type=int, default=28)
    p.add_argument("--sonder", action="store_true")
    p.add_argument("--bougies", action="store_true", help="profil tiré des bougies (ticks passés non servis)")
    p.add_argument("--base", nargs="*", default=["EURUSD", "NAS100"])
    a = p.parse_args()
    for base in a.base:
        if a.sonder:
            sonder(base)
            continue
        d = depuis_bougies(base) if a.bougies else mesurer(base, a.jours)
        chemin(base).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        s50 = np.array([np.nan if x is None else x for x in d["semaine_p50"]])
        par_h = np.nanmedian(s50.reshape(24, 60), axis=1)
        print(f"{base} : {d.get('source', 'ticks')} · médiane {d['median_global']} points")
        print("  médiane par heure New York : " + " ".join(f"{h:02d}h={v:g}" for h, v in enumerate(par_h)))
        pire = np.argsort(np.nan_to_num(s50, nan=-1))[-5:][::-1]
        print("  minutes les plus chères : " + ", ".join(f"{m // 60:02d}:{m % 60:02d}={s50[m]:g}" for m in pire))
    return 0


if __name__ == "__main__":
    sys.exit(main())
