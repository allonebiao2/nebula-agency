# -*- coding: utf-8 -*-
"""
La vague 4 : essayer des MILLIONS de règles, et n'en croire aucune sans correction.

    python -m trading.recherche.regles --base NAS100 --tf M1 --schema pts1200
    python -m trading.recherche.regles --base EURUSD --tf M1 --schema pts50 --profondeur 3

Chaque caractéristique est découpée en tranches ; chaque tranche devient une condition ; on essaie
toutes les paires (puis les meilleurs triplets). Pour chaque règle on compte, sur la période
d'apprentissage, combien de barres la vérifient et combien atteignent 2 R avant 1 R.

Pourquoi cette force brute est légitime ici, et pourquoi elle ne l'est pas ailleurs :
  · l'avantage cherché est ÉNORME (50 % de 2 R contre ~34 % au point mort). Sur 300 trades, z = 6,1 :
    il survivrait à une correction de Bonferroni sur un million de règles (z ≈ 5,9) ;
  · toute règle essayée est comptée. Le p publié est **multiplié par le nombre de règles essayées**,
    et la ligne entre au registre avec ce nombre. Une recherche qui cache son nombre d'essais ne
    prouve rien ;
  · rien n'est retenu sur la seule période d'apprentissage : la meilleure règle est rejouée sur la
    période de validation, puis dans `banc.simuler` (une position à la fois, coûts de la minute).

Technique : les conditions sont des bitsets (`np.packbits`), les intersections des `&` et les
comptages des `np.bitwise_count`. 26 000 paires se comptent en une seconde sur 1,7 million de barres.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import numpy as np

from . import banc, caracteristiques, etiquettes, scelle
from .intraday import fin_de_journee
from .lancer import DOSSIER, enregistrer_test

SORTIE = DOSSIER / "regles"
QUANTILES = (0.1, 0.25, 0.5, 0.75, 0.9)


def conditions(X: dict[str, np.ndarray], masque: np.ndarray) -> tuple[list[str], np.ndarray]:
    """Chaque caractéristique donne des conditions « au-dessus » et « en dessous » de ses quantiles.

    Deux formes suffisent et se composent : « x > seuil » et « x <= seuil ». Une tranche fermée est
    l'intersection des deux, donc elle apparaît toute seule dans les paires.
    """
    noms, colonnes = [], []
    for nom in sorted(X):
        v = X[nom][masque]
        fini = np.isfinite(v)
        if fini.sum() < 1000:
            continue
        uniques = np.unique(v[fini])
        seuils = uniques if len(uniques) <= 6 else np.unique(np.quantile(v[fini], QUANTILES))
        for s in seuils:
            haut = fini & (v > s)
            if 0.01 < haut.mean() < 0.99:
                noms.append(f"{nom}>{s:.6g}")
                colonnes.append(haut)
                noms.append(f"{nom}<={s:.6g}")
                colonnes.append(fini & ~haut)
    return noms, np.packbits(np.array(colonnes, dtype=bool), axis=1)


def _compte(bits: np.ndarray) -> np.ndarray:
    return np.bitwise_count(bits).sum(axis=-1)


def z_binomial(k: np.ndarray, n: np.ndarray, p0: float) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return (k / n - p0) / np.sqrt(p0 * (1 - p0) / np.maximum(n, 1))


def chercher(base: str, tf: str, schema: str, *, profondeur: int = 2, minimum: int = 500,
             garder: int = 40, part_apprentissage: float = 0.7) -> list[dict]:
    """Les meilleures règles d'apprentissage, rejouées en validation puis dans le simulateur."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    trouvailles = []
    for serie in scelle.series_decouverte(base, tf):
        X = caracteristiques.construire(serie)
        deux = etiquettes.deux_sens(serie, schema)
        n = len(serie)
        coupe = int(n * part_apprentissage)
        for sens, e in deux.items():
            valide = e.valides()
            app = valide & (np.arange(n) < coupe)
            if app.sum() < 20_000:
                continue
            p0 = banc.point_mort_objectif(e.R[app], e.objectif()[app])
            noms, bits = conditions(X, app)
            obj = np.packbits(e.objectif()[app])
            t0 = time.time()
            essais = 0
            meilleures: list[tuple[float, int, int, int, int]] = []       # (z, i, j, k, n)
            for i in range(len(noms)):
                inter = bits[i] & bits[i + 1:]
                if not len(inter):
                    continue
                n_ij = _compte(inter)
                k_ij = _compte(inter & obj)
                z = z_binomial(k_ij, n_ij, p0)
                z = np.where(n_ij >= minimum, z, -np.inf)
                essais += len(noms) - i - 1
                for j in np.argsort(z)[-3:]:
                    if np.isfinite(z[j]):
                        meilleures.append((float(z[j]), i, i + 1 + int(j), int(k_ij[j]), int(n_ij[j])))
            meilleures.sort(key=lambda x: -x[0])
            meilleures = meilleures[:garder]
            print(f"  {base} {tf} {schema} sens {sens:+d} · {serie.source} : {essais} paires en "
                  f"{time.time() - t0:.0f} s · point mort {100 * p0:.1f} %", flush=True)
            for z, i, j, k, n_ij in meilleures[:garder]:
                trouvailles.append(evaluer(serie, e, schema, sens, [noms[i], noms[j]],
                                           coupe, p0, essais, z, k, n_ij, X))
            if profondeur >= 3 and meilleures:
                trouvailles += _triplets(serie, e, schema, sens, noms, bits, obj, app, coupe, p0,
                                         meilleures, minimum, garder, essais, X)
        del X, deux
    trouvailles = [t for t in trouvailles if t]
    trouvailles.sort(key=lambda t: -(t["validation"]["taux_objectif"] or 0))
    fichier = SORTIE / f"regles_{base}_{tf}_{schema}.json"
    fichier.write_text(json.dumps(trouvailles, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  → {fichier}")
    return trouvailles


def _triplets(serie, e, schema, sens, noms, bits, obj, app, coupe, p0, meilleures, minimum, garder,
              essais_paires, X) -> list[dict]:
    """Les meilleures paires, croisées avec toutes les conditions : la profondeur 3 sans explosion."""
    sorties = []
    essais = essais_paires
    t0 = time.time()
    trouves: list[tuple[float, tuple[int, int, int], int, int]] = []
    for z, i, j, _k, _n in meilleures[:20]:
        base_bits = bits[i] & bits[j]
        inter = base_bits & bits
        n_ijk = _compte(inter)
        k_ijk = _compte(inter & obj)
        zz = z_binomial(k_ijk, n_ijk, p0)
        zz = np.where(n_ijk >= minimum, zz, -np.inf)
        zz[i] = zz[j] = -np.inf
        essais += len(noms)
        for m in np.argsort(zz)[-3:]:
            if np.isfinite(zz[m]):
                trouves.append((float(zz[m]), (i, j, int(m)), int(k_ijk[m]), int(n_ijk[m])))
    trouves.sort(key=lambda x: -x[0])
    print(f"    triplets : {essais - essais_paires} essais en {time.time() - t0:.0f} s", flush=True)
    for z, (i, j, m), k, n_ijk in trouves[:garder]:
        sorties.append(evaluer(serie, e, schema, sens, [noms[i], noms[j], noms[m]],
                               coupe, p0, essais, z, k, n_ijk, X))
    return sorties


def evaluer(serie, e, schema, sens, libelle, coupe, p0, essais, z, k, n_app, X) -> dict | None:
    """Rejouer la règle après la coupe, puis dans le simulateur. C'est là qu'elle meurt d'habitude."""
    from scipy.stats import binom
    validation = rejouer(serie, e, libelle, coupe, X)
    if validation is None:
        return None
    p_brut = float(binom.sf(k - 1, n_app, p0))
    return {"base": serie.base, "tf": serie.tf, "schema": schema, "sens": int(sens),
            "flux": serie.source, "conditions": libelle, "essais": int(essais),
            "apprentissage": {"n": int(n_app), "taux_objectif": round(k / n_app, 4),
                              "point_mort": round(p0, 4), "z": round(float(z), 2),
                              "p": p_brut, "p_corrige": min(1.0, p_brut * max(essais, 1))},
            "validation": validation}


def _masque_conditions(X: dict[str, np.ndarray], libelle: list[str]) -> np.ndarray:
    """Reconstruire une règle depuis son libellé (« ret_5min>0.42 », « heure_ny<=9 »)."""
    m = None
    for c in libelle:
        if ">" in c and "<=" not in c:
            nom, seuil = c.split(">")
            v = X[nom] > float(seuil)
        else:
            nom, seuil = c.split("<=")
            v = X[nom] <= float(seuil)
        v &= np.isfinite(X[nom])
        m = v if m is None else (m & v)
    return m


def rejouer(serie, e, libelle: list[str], depuis: int, X: dict | None = None) -> dict | None:
    """La règle, appliquée après la coupe : taux d'objectif hors apprentissage, puis vrais trades."""
    X = X if X is not None else caracteristiques.construire(serie)
    m = _masque_conditions(X, libelle) & e.valides()
    m &= np.arange(len(serie)) >= depuis
    n = int(m.sum())
    if n < 100:
        return {"n": n, "taux_objectif": None}
    taux = float(e.objectif()[m].mean())
    sens = np.where(m, e.sens, 0).astype(np.int8)
    sig = banc.Signaux(sens=sens, stop_dist=etiquettes.distances(serie, e.schema), rr=2.0,
                       max_barres=int(24 * 60 / serie.minutes),
                       fin_seance=fin_de_journee(serie.base, serie.temps))
    t = banc.simuler(serie, sig)
    mesure = banc.mesurer(serie, t, series=len(t) <= 20000) if len(t) else {"trades": 0}
    return {"n": n, "taux_objectif": round(taux, 4),
            "trades": mesure.get("trades", 0),
            "taux_objectif_trades": mesure.get("taux_objectif"),
            "point_mort": mesure.get("point_mort_objectif"),
            "esperance_R": mesure.get("esperance_R"), "p_objectif": mesure.get("p_objectif")}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="NAS100")
    p.add_argument("--tf", default="M1")
    p.add_argument("--schema", default="pts1200")
    p.add_argument("--profondeur", type=int, default=2)
    p.add_argument("--minimum", type=int, default=500)
    a = p.parse_args()
    trouvailles = chercher(a.base, a.tf, a.schema, profondeur=a.profondeur, minimum=a.minimum)
    for t in trouvailles[:12]:
        v = t["validation"]
        print(f"    {' ET '.join(t['conditions']):70s} sens {t['sens']:+d} | apprentissage "
              f"{100 * t['apprentissage']['taux_objectif']:.1f} % (n={t['apprentissage']['n']}) | "
              f"validation {100 * (v['taux_objectif'] or 0):.1f} % (n={v['n']}) | "
              f"trades {v.get('trades')} à {100 * (v.get('taux_objectif_trades') or 0):.1f} %")
    if trouvailles:
        meilleure = trouvailles[0]
        v = meilleure["validation"]
        enregistrer_test(f"regles_{a.base}_{a.tf}_{a.schema}_p{a.profondeur}", {
            "tour": 7, "candidate": f"regles_{a.schema}", "base": a.base, "tf": a.tf, "temoin": False,
            "combinaisons": meilleure["apprentissage"] and meilleure["essais"],
            "vague": "4 · règles minées", "trades": v.get("trades"),
            "taux_objectif": v.get("taux_objectif_trades"),
            "point_mort_objectif": v.get("point_mort"), "p_objectif": v.get("p_objectif"),
            "esperance_R": v.get("esperance_R"), "taux_reussite": None, "profit_factor": None,
            "p_valeur": None, "conditions": meilleure["conditions"]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
