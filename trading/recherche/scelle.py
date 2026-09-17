# -*- coding: utf-8 -*-
"""
Le scellé : les années que la recherche n'a JAMAIS vues, et qui ne s'ouvrent qu'une fois.

    python -m trading.recherche.scelle --etat
    python -m trading.recherche.scelle --ouvrir ma_candidate --base NAS100 --tf M1 --raison "..."

Pourquoi ce fichier existe : on cherche « jusqu'à trouver ». À force d'essayer, on finit toujours par
trouver un backtest flatteur né du hasard. La seule parade est un jeu de données que le chercheur n'a
pas pu regarder pendant qu'il cherchait, ouvert une seule fois, avec des réglages déjà figés.

Ce qui est scellé (vérifié le 2026-09-17 : Deriv ne possède pas ces années) :
  · **EUR/USD 2003-05 → 2011-12** (Dukascopy). Deriv commence en 2012 en M5-M15 et en 2019 en M1.
  · **NAS100 2020-01 → 2023-12** (Dukascopy), krach de 2020 et baisse de 2022 compris.
    Deriv commence le 2024-01-22.

⚠️ Une ouverture s'inscrit dans `rapports/recherche/scelle.json` avec sa date et sa raison. Une
candidate déjà ouverte ne se rouvre pas : rouvrir, c'est re-régler sur le scellé, et alors il n'est
plus scellé.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from . import banc
from .lancer import DOSSIER

JOURNAL = DOSSIER / "scelle.json"

# base -> (début inclus, fin exclue) en dates ISO
PERIODES = {
    "EURUSD": ("2003-05-05", "2012-01-01"),
    "NAS100": ("2020-01-01", "2024-01-01"),
}

# base -> [(source, début, fin)] : là où la recherche a le droit de chercher
DECOUVERTE = {
    "EURUSD": [("mt5", None, None)],
    # Le NAS100 a trois morceaux de découverte : Dukascopy avant le scellé, Dukascopy APRÈS le
    # scellé (la même période que Deriv, chez un autre fournisseur : c'est ce qui permet de savoir
    # si un avantage est celui du marché ou celui d'un flux), et Deriv.
    "NAS100": [("duka", "2013-01-01", "2020-01-01"), ("duka", "2024-01-01", None),
               ("mt5", None, None)],
}


def _journal() -> list[dict]:
    return json.loads(JOURNAL.read_text(encoding="utf-8")) if JOURNAL.exists() else []


def deja_ouvert(candidate: str) -> list[dict]:
    return [o for o in _journal() if o["candidate"] == candidate]


def series_decouverte(base: str, tf: str, **kw) -> list[banc.Serie]:
    """Les morceaux sur lesquels on a le droit de chercher. Plusieurs quand l'historique vient de
    deux flux (NAS100 : Dukascopy jusqu'en 2019, Deriv depuis 2024)."""
    sorties = []
    for source, debut, fin in DECOUVERTE[base.upper()]:
        try:
            s = banc.charger(base, tf, source=source, **kw)
        except FileNotFoundError:
            continue
        s = s.tranche(debut, fin)
        if len(s) > 1000:
            sorties.append(s)
    if not sorties:
        raise FileNotFoundError(f"aucune donnée de découverte pour {base} {tf}")
    return sorties


def ouvrir(base: str, tf: str, candidate: str, *, raison: str = "", cout: str = "deriv") -> banc.Serie:
    """LE geste qui ne se fait qu'une fois par candidate."""
    base = base.upper()
    if base not in PERIODES:
        raise ValueError(f"{base} n'a pas de période scellée")
    vues = [o for o in deja_ouvert(candidate) if o["base"] == base and o["tf"] == tf]
    if vues:
        raise PermissionError(
            f"« {candidate} » a déjà ouvert le scellé {base} {tf} le {vues[0]['date']}. "
            f"Une deuxième ouverture n'est plus une confirmation : c'est un réglage.")
    debut, fin = PERIODES[base]
    serie = banc.charger(base, tf, source="duka", cout=cout).tranche(debut, fin)
    DOSSIER.mkdir(parents=True, exist_ok=True)
    journal = _journal()
    journal.append({"candidate": candidate, "base": base, "tf": tf, "periode": [debut, fin],
                    "barres": len(serie), "cout": cout, "raison": raison,
                    "date": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    JOURNAL.write_text(json.dumps(journal, ensure_ascii=False, indent=1), encoding="utf-8")
    return serie


def etat() -> None:
    print("\n  SCELLÉ\n")
    for base, (debut, fin) in PERIODES.items():
        try:
            s = banc.charger(base, "M1", source="duka")
            dispo = f"{len(s.tranche(debut, fin)):>9d} barres M1 prêtes"
        except FileNotFoundError:
            dispo = "pas encore téléchargé"
        print(f"  {base:8s} {debut} → {fin}   {dispo}")
    ouvertures = _journal()
    print(f"\n  {len(ouvertures)} ouverture(s)")
    for o in ouvertures:
        print(f"    {o['date'][:10]}  {o['candidate']:28s} {o['base']} {o['tf']}  {o['raison'][:60]}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--etat", action="store_true")
    p.add_argument("--ouvrir")
    p.add_argument("--base", default="NAS100")
    p.add_argument("--tf", default="M1")
    p.add_argument("--raison", default="")
    a = p.parse_args()
    if a.ouvrir:
        s = ouvrir(a.base, a.tf, a.ouvrir, raison=a.raison)
        print(f"  scellé ouvert : {a.base} {a.tf}, {len(s)} barres, {s.temps[0]} → {s.temps[-1]}")
    etat()
    return 0


if __name__ == "__main__":
    sys.exit(main())
