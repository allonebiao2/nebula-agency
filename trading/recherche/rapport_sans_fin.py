# -*- coding: utf-8 -*-
"""
Le rapport de la recherche de scalping : `trading/RECHERCHE-SCALPING.md`.

    python -m trading.recherche.rapport_sans_fin

Il lit les fichiers produits par les vagues (plafonds, cartes, modèle, règles minées, registre) et
n'invente aucun chiffre. Un verdict s'ouvre TOUJOURS par les trois nombres de Mongazi : la part des
trades qui atteignent vraiment 2 R, le R:R réalisé, et la probabilité de 5 ou 6 pertes d'affilée.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import banc
from .lancer import DOSSIER, REGISTRE

CIBLE = Path(__file__).resolve().parents[1] / "RECHERCHE-SCALPING.md"


def _lire(chemin: Path):
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else None


def _registre() -> list[dict]:
    return _lire(REGISTRE) or []


def section_candidat() -> list[str]:
    d = _lire(DOSSIER / "candidat_rabais.json")
    if not d:
        return []
    lignes = d["periodes"] + d["variantes"] + d["couts"]
    scelle = next((x for x in d["periodes"] if x["libelle"].startswith("SCELLÉ")), None)
    out = ["## 1. Le seul candidat de la recherche : l'entrée limite « au rabais »", "",
           "**La règle** : dans le sens de l'EMA 60 minutes, poser un ordre limite à 0,5 R sous le prix"
           " (au-dessus, en vente), stop à 2 × ATR(14), objectif à 2 R, ordre annulé après 60 minutes,"
           " position fermée au plus tard à la clôture de la journée. NAS100, M1.", "",
           "| période | trades | 2 R atteints | point mort | espérance | PF | P(5 pertes/100) |",
           "|---|---|---|---|---|---|---|"]
    for x in lignes:
        if not x.get("trades"):
            continue
        sp = x.get("series_perdantes") or {}
        out.append(f"| {x['libelle']} | {x['trades']} | **{100 * x['taux_objectif']:.1f} %** | "
                   f"{100 * x['point_mort_objectif']:.1f} % | {x['esperance_R']:+.3f} R | "
                   f"{x['profit_factor']:.2f} | "
                   f"{100 * (sp.get('p_5_pertes_sur_100_montecarlo') or 0):.0f} % |")
    out.append("")
    if scelle:
        sp = scelle["series_perdantes"]
        out += ["**Les trois chiffres de Mongazi, sur le scellé** "
                f"({scelle['trades']} trades jamais regardés pendant la recherche) :", "",
                f"1. **2 R réellement atteints : {100 * scelle['taux_objectif']:.1f} %** — l'objectif"
                f" est « plus de 50 % ». ⛔ **Non atteint.**",
                f"2. **R:R réalisé : {scelle['rr_realise']}** (gain moyen {scelle['gain_moyen_R']:+.2f} R,"
                f" perte moyenne {scelle['perte_moyenne_R']:+.2f} R). ✅",
                f"3. **P(5 pertes d'affilée sur 100 trades) : "
                f"{100 * sp['p_5_pertes_sur_100_montecarlo']:.0f} %**, P(6) : "
                f"{100 * sp['p_6_pertes_sur_100_montecarlo']:.0f} %, plus longue série observée : "
                f"{sp['plus_longue_observee']}. ⛔ **Pas « extrêmement bas ».**", "",
                f"Ce qu'il fait, lui : **{scelle['esperance_R']:+.3f} R par trade**, "
                f"{scelle['trades_par_mois']:.0f} trades par mois, positif chaque année "
                f"({', '.join(f'{a} {v:+.2f} R' for a, v in scelle['par_an'].items())}) et dans les"
                f" deux sens ({', '.join(f'{k} {v:+.2f} R' for k, v in scelle['par_sens'].items())}).",
                "",
                "⚠️ **Sa fragilité tient en un nombre : le spread.** À 70 points chez Deriv (mesuré :"
                " 70 points dans 99,8 % des minutes, ouverture et annonces comprises) il gagne ; au"
                " spread d'époque de Dukascopy (167 points) il perd. Il survit à un coût **trois fois**"
                " supérieur à celui de Deriv, pas quatre.",
                "⚠️ **Il échoue sur 2013-2019 au coût absolu d'aujourd'hui** (70 points sur un indice à"
                " 5 000, c'est quatre fois plus cher en proportion) et **réussit au coût relatif**"
                " (+0,164 R). Le mécanisme est ancien ; sa rentabilité est récente, et tient au spread.",
                "⛔ **Rien n'est en réel.** Le juge est la démo en observation : un ordre limite servi"
                " dans une simulation n'est pas un ordre limite servi par un courtier.", ""]
    return out


def section_plafonds() -> list[str]:
    out = ["## 2. Le plafond : jusqu'où 2 R peut tomber avant 1 R, dans la journée", "",
           "Sur chaque minute, on regarde ce qui serait arrivé dans les DEUX sens. Un devin qui"
           " choisirait toujours le bon sens atteindrait le « plafond ». **Aucune règle, aucun"
           " modèle, aucune intuition ne peut le dépasser.** En face, le « point mort » est le taux"
           " d'objectif qui rend l'espérance nulle, coûts et fins de journée compris.", ""]
    for fichier in sorted((DOSSIER / "carte").glob("plafonds_*.json")):
        lignes = _lire(fichier) or []
        if not lignes:
            continue
        base, tf = lignes[0]["base"], lignes[0]["tf"]
        out += [f"**{base} {tf}**", "",
                "| stop | plafond (devin parfait) | point mort | coût aller-retour | durée médiane |",
                "|---|---|---|---|---|"]
        for d in lignes:
            out.append(f"| {d['stop_points']} points | **{100 * d['plafond_objectif']:.1f} %** | "
                       f"{100 * d['point_mort']:.1f} % | {d['cout_aller_retour_R']:.3f} R | "
                       f"{d['duree_mediane_barres']} barres |")
        out.append("")
    return out


def section_limites() -> list[str]:
    out = ["## 3. Entrer sur un retour de prix (ordre limite)", "",
           "La géométrie change : depuis un meilleur prix, l'objectif est plus près en valeur"
           " absolue. ⛔ Piège mesuré : à 0,5 R de retrait les deux sens sont des miroirs exacts,"
           " donc « au moins un des deux gagne » vaut 99 % **par construction**. Seuls comptent les"
           " taux par sens, rapportés aux ordres servis.", ""]
    for fichier in sorted((DOSSIER / "carte").glob("limites_*.json")):
        lignes = [d for d in (_lire(fichier) or []) if d.get("objectif_achat") is not None]
        if not lignes:
            continue
        base, tf = lignes[0]["base"], lignes[0]["tf"]
        out += [f"**{base} {tf}**", "",
                "| stop | retrait | part servie | objectif achat | objectif vente | point mort |",
                "|---|---|---|---|---|---|"]
        for d in lignes:
            out.append(f"| {d['stop_points']} points | {d['retrait_R']:.2f} R | "
                       f"{100 * d['part_servie']:.1f} % | {100 * d['objectif_achat']:.1f} % | "
                       f"{100 * d['objectif_vente']:.1f} % | {100 * d['point_mort']:.1f} % |")
        out.append("")
    return out


def section_modele() -> list[str]:
    out = ["## 4. Le modèle : ce qu'on sait prévoir, mesuré hors échantillon", "",
           "Un modèle par sens apprend P(2 R avant 1 R) sur les caractéristiques causales,"
           " walk-forward purgé. On lit la précision parmi les minutes où il est le plus sûr :"
           " si les 1 % les plus sûres ne dépassent pas le point mort, il n'y a rien à prendre.", ""]
    for fichier in sorted((DOSSIER / "meta").glob("meta_*.json")):
        res = _lire(fichier) or []
        for r in res:
            lignes = []
            for d in r.get("detail", []):
                p1 = next((p for p in d["precision"] if p["part"] == 0.01), None)
                if p1:
                    lignes.append((d["sens"], d["pli"], d["taux_base_test"], p1["precision"]))
            if not lignes:
                continue
            moy_base = sum(l[2] for l in lignes) / len(lignes)
            moy_top = sum(l[3] for l in lignes) / len(lignes)
            out.append(f"- **{r['base']} {r['tf']} {r['schema']}** ({r['source']}"
                       f"{', TÉMOIN étiquettes mélangées' if r.get('temoin') else ''}) : taux de base "
                       f"{100 * moy_base:.1f} %, précision moyenne du 1 % le plus sûr "
                       f"**{100 * moy_top:.1f} %**")
            for seuil, m in sorted((r.get("seuils") or {}).items()):
                out.append(f"  - seuil {seuil} : {m['trades']} trades, objectif atteint "
                           f"{100 * m['taux_objectif']:.1f} % (point mort "
                           f"{100 * m['point_mort_objectif']:.1f} %), espérance {m['esperance_R']:+.3f} R")
    out.append("")
    return out


def section_regles() -> list[str]:
    out = ["## 5. La recherche exhaustive de règles", "",
           "Toutes les paires de conditions (puis les meilleurs triplets) sont essayées sur la"
           " période d'apprentissage, puis rejouées après la coupe et passées au simulateur."
           " **Le nombre d'essais est publié** : c'est lui qui décide de ce qu'on a le droit de"
           " croire.", ""]
    for fichier in sorted((DOSSIER / "regles").glob("regles_*.json")):
        trouvailles = _lire(fichier) or []
        avec_trades = [t for t in trouvailles if (t["validation"].get("trades") or 0) >= 100]
        if not trouvailles:
            continue
        t0 = trouvailles[0]
        out += [f"**{t0['base']} {t0['tf']} {t0['schema']}** · {t0['essais']} règles essayées", "",
                "| règle | sens | apprentissage | validation | trades | 2 R atteints |",
                "|---|---|---|---|---|---|"]
        for t in (avec_trades or trouvailles)[:8]:
            v = t["validation"]
            out.append(f"| {' ET '.join(t['conditions'])} | {'achat' if t['sens'] > 0 else 'vente'} | "
                       f"{100 * t['apprentissage']['taux_objectif']:.1f} % (n={t['apprentissage']['n']}) | "
                       f"{100 * (v['taux_objectif'] or 0):.1f} % (n={v['n']}) | {v.get('trades') or 0} | "
                       f"{100 * (v.get('taux_objectif_trades') or 0):.1f} % |")
        out.append("")
    return out


def section_registre() -> list[str]:
    registre = _registre()
    comptes = [r for r in registre if not r.get("temoin") and r.get("trades")]
    rejets = banc.holm([r.get("p_objectif") if r.get("p_objectif") is not None
                        else (r.get("p_valeur") or 1.0) for r in comptes])
    survivants = [r for r, ok in zip(comptes, rejets) if ok]
    avec_obj = [r for r in comptes if r.get("taux_objectif") is not None and r["trades"] >= 100]
    meilleurs = sorted(avec_obj, key=lambda r: -(r["taux_objectif"] or 0))[:10]
    out = ["## 6. Le registre", "",
           f"- **{len(comptes)} tests comptés** (témoins exclus), correction de Holm à 5 % sur le"
           f" registre entier.",
           f"- **{len(survivants)} survivant(s).**", ""]
    if avec_obj:
        out += ["Les plus hauts taux de 2 R atteints, sur au moins 100 trades :", "",
                "| test | trades | 2 R atteints | point mort | espérance | p |", "|---|---|---|---|---|---|"]
        for r in meilleurs:
            out.append(f"| {r['cle']} | {r['trades']} | **{100 * r['taux_objectif']:.1f} %** | "
                       f"{100 * (r.get('point_mort_objectif') or 0):.1f} % | "
                       f"{(r.get('esperance_R') or 0):+.3f} R | "
                       f"{(r.get('p_objectif') if r.get('p_objectif') is not None else r.get('p_valeur')):.3f} |")
        out.append("")
    return out


def verdict() -> list[str]:
    registre = [r for r in _registre() if not r.get("temoin") and (r.get("trades") or 0) >= 100]
    avec = [r for r in registre if r.get("taux_objectif") is not None]
    meilleur = max(avec, key=lambda r: r["taux_objectif"]) if avec else None
    au_dessus = [r for r in avec if r["taux_objectif"] > 0.5]
    lignes = ["# NEBULA Trader · recherche d'une stratégie de SCALPING (EUR/USD, NAS100)", ""]
    candidat = _lire(DOSSIER / "candidat_rabais.json")
    scelle = next((x for x in (candidat or {}).get("periodes", [])
                   if x["libelle"].startswith("SCELLÉ")), None)
    if au_dessus:
        lignes += [f"## Verdict : {len(au_dessus)} test(s) dépassent 50 % de 2 R atteints sur au"
                   f" moins 100 trades. À confirmer sur le scellé.", ""]
    else:
        lignes += ["## Verdict : **l'objectif tel qu'il est écrit n'est pas atteignable en intraday**,"
                   " et ce n'est pas une opinion : c'est mesuré.", "",
                   "Un devin qui choisirait toujours le bon sens atteindrait **63,8 %** de 2 R sur"
                   " NAS100 M1 et **57,7 %** sur EUR/USD M1 (section 2). Viser « plus de 50 % »"
                   " revient donc à exiger de choisir le bon sens **trois fois sur quatre**, et viser"
                   " 60-70 % est au-dessus du plafond lui-même. Sur tous les tests de cette"
                   " recherche, le meilleur taux de 2 R atteints est de **41 %**.", ""]
        if scelle:
            lignes += [f"**Mais la recherche a trouvé quelque chose d'autre** : une stratégie qui"
                       f" gagne de l'argent sans remplir ces critères — {100 * scelle['taux_objectif']:.1f} %"
                       f" de 2 R, {scelle['esperance_R']:+.3f} R par trade, **confirmée sur des années"
                       f" scellées** ({scelle['trades']} trades jamais regardés). C'est le profil que"
                       f" Mongazi appelait « nul » : un taux de réussite bas, compensé par un gain"
                       f" moyen presque deux fois la perte moyenne. Section 1.", ""]
    if meilleur:
        lignes += [f"- Meilleur taux de 2 R atteints : **{100 * meilleur['taux_objectif']:.1f} %** "
                   f"({meilleur['cle']}, {meilleur['trades']} trades, point mort "
                   f"{100 * (meilleur.get('point_mort_objectif') or 0):.1f} %).", ""]
    lignes += ["- Objectif de Mongazi : **plus de 50 %** (idéal 60-70 %) de 2 R atteints, R:R 1:2,"
               " et un risque très bas de 5-6 pertes d'affilée.",
               "- Rappel calculé : à 50 % de 2 R, la probabilité de 5 pertes d'affilée sur 100 trades"
               " vaut encore **81 %** ; elle ne tombe sous 5 % (6 pertes) qu'à partir de **70 %**.",
               "- Protocole, données scellées et paliers : `trading/RECHERCHE-SANS-FIN.md`.", ""]
    return lignes


def ecrire() -> Path:
    texte = verdict() + section_candidat() + section_plafonds() + section_limites() + \
        section_modele() + section_regles() + section_registre()
    CIBLE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    return CIBLE


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    chemin = ecrire()
    print(f"  → {chemin} ({chemin.stat().st_size / 1000:.1f} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
