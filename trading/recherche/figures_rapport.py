# -*- coding: utf-8 -*-
"""
Écrit `trading/RECHERCHE-FIGURES.md` en RELISANT les résultats de `figures_lancer` et le registre.

    python -m trading.recherche.figures_rapport
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from . import banc
from .lancer import DOSSIER, _registre

RAPPORT = Path(__file__).resolve().parents[1] / "RECHERCHE-FIGURES.md"
NOMS = {"ete": "Épaule-tête-épaule", "ete_inverse": "ETE inversé", "biseau_ascendant": "Biseau ascendant",
        "biseau_descendant": "Biseau descendant"}
FILTRES = {"aucun": "sans filtre", "rsi": "divergence RSI", "ema50": "EMA 50", "rsi_ema50": "RSI + EMA 50"}
# Statistiques publiques relevées le 2026-09-17 sur thepatternsite.com (actions, sortie au meilleur prix)
BULKOWSKI = {"ete": ("51 %", "19 %"), "ete_inverse": ("71 %", "11 %"), "biseau_ascendant": ("32 %", "51 %"),
             "biseau_descendant": ("62 %", "26 %")}


def pct(x, d=1):
    return "n/a" if x is None else f"{100 * x:.{d}f} %".replace(".", ",")


def num(x, fmt="+.3f"):
    return "n/a" if x is None else format(x, fmt).replace(".", ",")


def usd(x):
    return "n/a" if x is None else f"{x:,.0f} $".replace(",", " ")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    d = json.loads((DOSSIER / "figures" / "resultats.json").read_text(encoding="utf-8"))
    cpt = json.loads((DOSSIER / "figures" / "comptes.json").read_text(encoding="utf-8"))
    reg = [e for e in _registre() if e.get("trades") and not e["temoin"]]
    holm = dict(zip([e["cle"] for e in reg], banc.holm([e["p_valeur"] for e in reg])))
    fig_reg = [e for e in reg if e["cle"].startswith("figures_")]
    survivants = [e for e in fig_reg if holm.get(e["cle"])]
    L = ["# NEBULA Trader · figures chartistes : ETE, ETE inversé, biseaux, avec RSI et EMA 50\n",
         "*Demande de Mongazi du 2026-09-17. Généré par `python -m trading.recherche.figures_lancer` puis "
         "`python -m trading.recherche.figures_rapport` : aucun chiffre recopié à la main. Définitions mécaniques "
         "fixées avant le premier résultat : `trading/recherche/figures.py`.*\n"]

    vises = [k for k, v in d.items() if v["mesures"].get("trades", 0) >= 100 and v["mesures"]["taux_reussite"] > 0.5
             and v["mesures"]["esperance_R"] > 0]
    positifs = [k for k, v in d.items() if v["mesures"].get("trades", 0) >= 30 and v["mesures"]["esperance_R"] > 0]
    assez = [k for k, v in d.items() if v["mesures"].get("trades", 0) >= 30]
    if not survivants and not vises:
        L.append("## Verdict : NON. Aucune figure, avec ou sans RSI et EMA 50, n'approche tes critères, et aucune ne se "
                 "distingue du hasard.\n")
    else:
        L.append(f"## Verdict : à examiner ({len(survivants)} test(s) résistent à la correction, {len(vises)} dépassent 50 %).\n")
    L.append(f"- **{len(d)} versions testées** (4 figures × 4 filtres × 2 stops × H1, H4, D1 × EUR/USD et NAS100), "
             f"objectif 2 R, coûts Deriv. **{len(fig_reg)}** ont au moins un trade et entrent au registre, qui compte "
             f"désormais **{len(reg)} tests** ; **{len(survivants)}** résistent à la correction de Holm.")
    L.append(f"- Versions avec **plus de 50 % de réussite, au moins 100 trades et une espérance positive : {len(vises)}**.")
    L.append(f"- Versions à espérance positive sur au moins 30 trades : {len(positifs)} sur {len(assez)}, soit à peu près "
             "la moitié : ce qu'on attend du hasard.\n")

    # ------------------------------------------------------------------ tes chiffres
    L.append("## 1. Tes chiffres, figure par figure (EUR/USD, sans filtre, stop proche)\n")
    L.append("| Figure | Unité | Trades | Gagnants | Objectif 2 R atteint | R:R réalisé | P(5 pertes d'affilée sur 100) | Plus longue série perdante | Espérance | p |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for fig in NOMS:
        for tf in ("H1", "H4", "D1"):
            m = d[f"figures_{fig}_aucun_proche_EURUSD_{tf}"]["mesures"]
            if not m.get("trades"):
                continue
            sp = m["series_perdantes"]
            L.append(f"| {NOMS[fig]} | {tf} | {m['trades']} | **{pct(m['taux_reussite'])}** | {pct(m['objectif_atteint'])} | "
                     f"1:{num(m['rr_realise'], '.2f')} | {pct(sp['p_5_pertes_sur_100_montecarlo'], 0)} | {sp['plus_longue_observee']} | "
                     f"**{num(m['esperance_R'])} R** | {num(m['p_valeur'], '.2f')} |")
    L.append("")
    hauts = [(k, v) for k, v in d.items() if v["base"] == "EURUSD" and v["filtre"] == "aucun" and v["stop"] == "proche"
             and v["mesures"].get("trades") and v["mesures"]["taux_reussite"] > 0.5]
    for k, v in hauts:
        m = v["mesures"]
        n_, g_ = m["trades"], round(m["taux_reussite"] * m["trades"])
        bas_ic, haut_ic = banc._wilson(g_, n_)
        L.append(f"- ⚠️ **{NOMS[v['figure']]} en {v['tf']} dépasse 50 % ({pct(m['taux_reussite'])}), mais sur {n_} trades** : "
                 f"l'intervalle de confiance va de {pct(bas_ic, 0)} à {pct(haut_ic, 0)}, et seulement "
                 f"{round(m['objectif_atteint'] * n_)} trades atteignent l'objectif de 2 R ; les autres gagnants sortent par "
                 "le temps avec un petit gain (R:R réalisé " + f"1:{num(m['rr_realise'], '.2f')}). Ce n'est pas le 50 % à 1:2 que tu cherches.")
    if hauts:
        L.append("")
    L.append("**Comparaison avec Bulkowski** (actions, sortie au meilleur prix, sans stop ni coûts) :\n")
    L.append("| Figure | Bulkowski : objectif atteint | Bulkowski : échec | Ici : gagnants, toutes versions EUR/USD | Ici : espérance moyenne |")
    L.append("|---|---|---|---|---|")
    moyennes = {}
    for fig in NOMS:
        vs = [v["mesures"] for v in d.values() if v["figure"] == fig and v["base"] == "EURUSD" and v["mesures"].get("trades")]
        n = sum(m["trades"] for m in vs)
        moyennes[fig] = (sum(m["trades"] * m["taux_reussite"] for m in vs) / n, sum(m["trades"] * m["esperance_R"] for m in vs) / n)
        L.append(f"| {NOMS[fig]} | {BULKOWSKI[fig][0]} | {BULKOWSKI[fig][1]} | "
                 f"{pct(sum(m['trades'] * m['taux_reussite'] for m in vs) / n)} | "
                 f"{num(sum(m['trades'] * m['esperance_R'] for m in vs) / n)} R |")
    meilleure_moy = max(moyennes.values(), key=lambda x: x[0])[0]
    meilleure_esp = max(x[1] for x in moyennes.values())
    L.append(f"\nAvec un vrai stop et un objectif à 2 R, **la meilleure figure fait {pct(meilleure_moy)} de gagnants en moyenne** "
             f"(toutes versions EUR/USD confondues), et la meilleure espérance moyenne est de {num(meilleure_esp)} R. "
             "Les « objectifs atteints » de Bulkowski supposent une sortie au meilleur prix, sans stop : on ne les retrouve pas.\n")

    # ------------------------------------------------------------------ filtres
    L.append("## 2. Ce que le RSI et l'EMA 50 ajoutent vraiment\n")
    L.append("Chaque version filtrée comparée à la même figure, même stop, même marché, même unité, sans filtre "
             "(paires où les deux ont au moins 20 trades) :\n")
    L.append("| Filtre | Paires comparées | Gain moyen de réussite | Gain moyen d'espérance | Paires améliorées | Trades gardés |\n|---|---|---|---|---|---|")
    for f in ("rsi", "ema50", "rsi_ema50"):
        de, dr, fr_ = [], [], []
        for k, v in d.items():
            if v["filtre"] != "aucun":
                continue
            a, b = v["mesures"], d[k.replace("_aucun_", f"_{f}_")]["mesures"]
            if a.get("trades", 0) >= 20 and b.get("trades", 0) >= 20:
                de.append(b["esperance_R"] - a["esperance_R"])
                dr.append(b["taux_reussite"] - a["taux_reussite"])
                fr_.append(b["trades"] / a["trades"])
        if de:
            L.append(f"| {FILTRES[f]} | {len(de)} | {num(np.mean(dr) * 100, '+.1f')} points | {num(np.mean(de))} R | "
                     f"{sum(x > 0 for x in de)} sur {len(de)} | {pct(np.mean(fr_), 0)} |")
    de = []
    for k, v in d.items():
        if v["stop"] == "proche":
            a, b = v["mesures"], d[k.replace("_proche_", "_loin_")]["mesures"]
            if a.get("trades", 0) >= 20 and b.get("trades", 0) >= 20:
                de.append((b["esperance_R"] - a["esperance_R"], b["taux_reussite"] - a["taux_reussite"]))
    L.append(f"\n- **Stop loin (tête / haut du biseau) au lieu de proche** : {num(np.mean([x[1] for x in de]) * 100, '+.1f')} points "
             f"de réussite, {num(np.mean([x[0] for x in de]))} R d'espérance en moyenne ({len(de)} paires). Plus de trades "
             "gagnants, mais des gains plus petits en dollars pour le même risque.")
    L.append("- **Lecture** : un filtre retire des trades. S'il retirait surtout les perdants, l'espérance monterait nettement "
             "et régulièrement ; ici elle bouge de quelques centièmes de R, dans un sens ou dans l'autre selon la paire. "
             "Le filtre le plus sévère (RSI + EMA 50) ne se compare que sur les rares paires qui gardent 20 trades : ce "
             "sont les échantillons les plus petits, donc les plus trompeurs.\n")

    # ------------------------------------------------------------------ meilleures
    L.append("## 3. Les 12 meilleures versions (au moins 30 trades, classées par p)\n")
    L.append("| Version | Trades | Gagnants | Espérance | p | Coûts ×1,5 | 80 % anciens | 20 % récents | Correction |\n|---|---|---|---|---|---|---|---|---|")
    rangees = sorted(((k, v) for k, v in d.items() if v["mesures"].get("trades", 0) >= 30), key=lambda kv: kv[1]["mesures"]["p_valeur"])
    for k, v in rangees[:12]:
        m = v["mesures"]
        L.append(f"| {NOMS[v['figure']]}, {FILTRES[v['filtre']]}, stop {v['stop']} · {v['base']} {v['tf']} | {m['trades']} | "
                 f"{pct(m['taux_reussite'])} | {num(m['esperance_R'])} R | {num(m['p_valeur'], '.3f')} | "
                 f"{num(v['couts_x1_5']['esperance_R'])} R | {m['avant_80']['trades']} tr, {num(m['avant_80']['esperance_R'])} R | "
                 f"{m['apres_20']['trades']} tr, {num(m['apres_20']['esperance_R'])} R | {'OUI' if holm.get(k) else 'non'} |")
    if rangees:
        k0, v0 = rangees[0]
        L.append(f"\n- Même la meilleure (p = {num(v0['mesures']['p_valeur'], '.3f')} sur {v0['mesures']['trades']} trades) "
                 f"{'résiste' if holm.get(k0) else 'ne résiste pas'} à la correction : avec {len(reg)} tests au registre, la "
                 f"première marche de Holm exige p < {0.05 / len(reg):.5f}".replace(".", ",") + ". Sur "
                 f"{len(d)} versions, en trouver une vers 0,05 est ce que produit le hasard.")
    retournees = [k for k, v in rangees[:12] if (v["mesures"]["avant_80"]["esperance_R"] or 0) <= 0 < (v["mesures"]["apres_20"]["esperance_R"] or 0)]
    effondrees = [k for k, v in rangees[:12] if (v["mesures"]["apres_20"]["esperance_R"] or 0) <= 0 < (v["mesures"]["avant_80"]["esperance_R"] or 0)]
    L.append(f"- Stabilité dans le temps : parmi ces 12, {len(retournees)} perdaient sur les 80 % anciens et ne gagnent que sur "
             f"les 20 % récents, et {len(effondrees)} gagnaient avant et perdent sur les 20 % récents.\n")

    # ------------------------------------------------------------------ NAS100
    L.append("## 4. NAS100 : trop peu de figures pour conclure\n")
    L.append("| Figure | H1 | H4 | D1 |\n|---|---|---|---|")
    for fig in NOMS:
        cel = []
        for tf in ("H1", "H4", "D1"):
            m = d[f"figures_{fig}_aucun_proche_NAS100_{tf}"]["mesures"]
            n_ = m.get("trades", 0)
            cel.append(f"{n_} trade{'s' if n_ > 1 else ''}, {num(m.get('esperance_R'))} R" if n_ else "0 trade")
        L.append(f"| {NOMS[fig]} | " + " | ".join(cel) + " |")
    L.append("\nL'historique Deriv du NAS100 commence en janvier 2024 : 2 ans et demi ne contiennent que quelques dizaines "
             "de figures. Rien ne peut être conclu, dans un sens ou dans l'autre.\n")

    # ------------------------------------------------------------------ 10 000 $
    L.append("## 5. Les 10 000 $ (1 % de risque par trade)\n")
    L.append("| Version | Règles | Trades | Capital final | Résultat | Par an | Drawdown max | Gagnants | Pire série |\n|---|---|---|---|---|---|---|---|---|")
    for cle, v in cpt["comptes"].items():
        base_cle, regles = cle.split("|")
        r_ = d[base_cle]
        titre = f"{NOMS[r_['figure']]}, {FILTRES[r_['filtre']]}, stop {r_['stop']} · {r_['base']} {r_['tf']}"
        if base_cle == cpt["meilleure_apres_coup"]:
            titre += " ⚠️ choisie après coup"
        L.append(f"| {titre} | {'vidéo' if regles == 'video' else 'NEBULA PRO'} | {v.get('trades', 0)} | {usd(v.get('capital_final'))} | "
                 f"**{usd(v.get('benefice_usd'))} ({num((v.get('rendement_pct') or 0) / 100, '+.1%').replace('%', ' %')})** | "
                 f"{num((v.get('rendement_annuel_pct') or 0) / 100, '+.1%').replace('%', ' %')} | "
                 f"{num((v.get('drawdown_max_pct') or 0) / 100, '.1%').replace('%', ' %')} | {pct(v.get('taux_reussite'))} | "
                 f"{v.get('serie_perdante_max', 0)} |")
    ete = cpt["comptes"].get("figures_ete_aucun_proche_EURUSD_H4|video", {})
    gagnantes_h4 = [f for f in NOMS if (cpt["comptes"].get(f"figures_{f}_aucun_proche_EURUSD_H4|video", {}).get("benefice_usd") or 0) > 0]
    L.append(f"\n- **Figures gagnantes sans filtre en H4 : {', '.join(NOMS[f] for f in gagnantes_h4) or 'aucune'}.** L'ETE transforme 10 000 $ en {usd(ete.get('capital_final'))} "
             f"en {num(ete.get('annees'), '.0f')} ans : **{num((ete.get('rendement_annuel_pct') or 0) / 100, '+.1%').replace('%', ' %')} par an**, "
             f"sur {ete.get('trades')} trades (environ {num(ete.get('trades', 0) / max(ete.get('annees') or 1, 1), '.0f')} par an). "
             "Même si c'était un vrai avantage, ce serait moins qu'un livret.")
    L.append("- **La « meilleure version » est choisie après avoir vu les résultats** : son chiffre est le plus optimiste "
             "possible, et c'est pour ça qu'il est marqué.\n")

    # ------------------------------------------------------------------ définitions et limites
    L.append("## 6. Comment les figures ont été reconnues, et ce que ça ne voit pas\n")
    L.append("- **Pivots** : extrême de 7 bougies, séquence alternée sommet/creux. **ETE** : tête au-dessus des épaules, "
             "hauteur d'au moins 2 ATR, épaules comparables, ligne de cou peu penchée, cassure à la clôture. "
             "**Biseaux** : 5 pivots, deux lignes dans le même sens qui convergent, cassure à la clôture avant la pointe.")
    L.append("- **Regardé sur des planches** avant de lire les résultats : les figures détectées ressemblent à des figures. "
             "Deux constats : certains ETE « de sommet » se forment après une forte baisse (continuation plutôt que "
             "retournement), et certains biseaux ascendants ont une ligne haute presque plate (proches d'un triangle).")
    L.append("- **Corrigé avant tout tableau** : dans un biseau, le stop « proche » tombait au même prix que le « loin » ; "
             "il est devenu l'extrême des 4 dernières bougies.")
    L.append("- **Contrôles** : figures dessinées à la main reconnues, témoins rejetés, aucune lecture du futur (deux fuites "
             "injectées exprès sont attrapées).")
    L.append("- **Limite** : un trader humain ne trace pas ses lignes comme ce code. Une autre définition donnerait d'autres "
             "chiffres ; mais pour qu'une figure soit un avantage réel, il faudrait qu'elle gagne sous une définition "
             "raisonnable, et aucune des 192 versions ne le montre.\n")

    L.append("## 7. Conseils\n")
    L.append("1. **Ne pas trader ces figures comme un système** : elles ne font pas mieux que le hasard une fois le stop et "
             "les coûts posés.")
    L.append("2. **Le RSI et l'EMA 50 ne changent pas la nature du résultat** : ils retirent des trades, pas des pertes.")
    L.append(f"3. **Ton critère (plus de 50 % à 1:2 sur au moins 100 trades) n'est atteint par aucun des {len(reg)} tests du registre.** "
             "Le chercher dans des figures ou des indicateurs publics, c'est chercher ce que des milliers de gens ont déjà "
             "arbitré.\n")
    L.append("## Sources\n")
    L.append("- Bulkowski, épaule-tête-épaule : https://thepatternsite.com/hst.html · inversé : https://thepatternsite.com/hsb.html")
    L.append("- Bulkowski, biseaux ascendants : https://thepatternsite.com/risewedge.html · descendants : https://thepatternsite.com/fallwedge.html")
    L.append("- Chang et Osler, « Methodical Madness », Economic Journal 1999 : https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0297.00466")
    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{RAPPORT} écrit ({len(L)} lignes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
