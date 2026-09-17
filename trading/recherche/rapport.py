# -*- coding: utf-8 -*-
"""
Écrit `trading/RECHERCHE-STRATEGIES.md` en RELISANT les résultats (registre + JSON).

    python -m trading.recherche.rapport

Aucun chiffre n'est recopié à la main : relancer ce script après toute nouvelle vague.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import banc
from .lancer import DOSSIER, _registre
from .million import croissance_necessaire, projeter

SORTIE = Path(__file__).resolve().parents[1] / "RECHERCHE-STRATEGIES.md"
NOMS = {
    "rsi2_connors": "RSI(2) de Connors", "bb_rsi_scalp": "Bollinger + RSI(7) scalping",
    "ibs_baisses": "IBS / 3 barres en baisse", "ema_stoch_pullback": "EMA 200 + Stochastique",
    "range_seance": "Range de séance (Asie→Londres, ouverture US)", "temoin_hasard": "Témoin : entrée au hasard",
    "video_mamba": "Vidéo MambaFx (zone M5 + cassure M1)", "video_hugo": "Vidéo Hugo FX (CRT H1 + swing M15)",
    "sniper_auteur": "Vidéo Sniper Entry (balayage M15 + clôture M1), telle quelle",
    "sniper_auteur_annonces": "Vidéo Sniper Entry + filtre des annonces",
    "sniper_auteur_annonces_sortie": "Vidéo Sniper Entry + sortie avant annonce",
    "sniper_auteur_imbalance": "Vidéo Sniper Entry + imbalance exigé",
    "sniper_auteur_5R": "Vidéo Sniper Entry, objectif 5 R", "sniper_auteur_2R": "Vidéo Sniper Entry, objectif 2 R",
    "sniper_auteur_niveau_oppose": "Vidéo Sniper Entry, objectif au niveau opposé",
    "sniper_auteur_dernier_creux_m1": "Vidéo Sniper Entry + cassure du dernier creux M1",
    "sniper_auteur_stop_saute": "Vidéo Sniper Entry, stop trop court sauté",
    "sniper_meilleures_heures": "Vidéo Sniper Entry, meilleures heures (contrôle)",
    "sniper_variantes": "Vidéo Sniper Entry, variantes (walk-forward)",
    "figures_ete": "Figure : épaule-tête-épaule", "figures_ete_inverse": "Figure : ETE inversé",
    "figures_biseau_ascendant": "Figure : biseau ascendant", "figures_biseau_descendant": "Figure : biseau descendant",
}
SNIPER = DOSSIER / "sniper"


def motifs_figures(cle: str) -> dict:
    """Motifs de sortie d'un test de figure chartiste, relus dans `figures/resultats.json`."""
    try:
        d = json.loads((DOSSIER / "figures" / "resultats.json").read_text(encoding="utf-8"))
        return d[cle]["mesures"].get("motifs", {})
    except (FileNotFoundError, KeyError):
        return {}


def motifs_sniper(cle: str) -> dict:
    """Motifs de sortie d'un test « Sniper Entry », relus dans ses propres JSON."""
    base = "NAS100" if "NAS100" in cle else "EURUSD"
    try:
        if cle.startswith("sniper_heures_controle_"):
            d = json.loads((SNIPER / f"heures_{base}.json").read_text(encoding="utf-8"))
            return (d.get("controle_heures_choisies") or {}).get("motifs", {})
        if cle.startswith("sniper_variantes_"):
            d = json.loads((SNIPER / f"variantes_{base}.json").read_text(encoding="utf-8"))
            return (d.get("hors_echantillon") or {}).get("motifs", {})
        nom = cle[len("sniper_"):].rsplit("_", 1)[0]
        d = json.loads((SNIPER / f"auteur_{base}.json").read_text(encoding="utf-8"))
        return d["versions"][nom]["mesures"].get("motifs", {})
    except (FileNotFoundError, KeyError):
        return {}


def pct(x):
    return f"{100 * x:.1f} %".replace(".", ",")


def r(x):
    return f"{x:+.3f}".replace(".", ",")


def fr(x, fmt):
    return format(x, fmt).replace(".", ",")


def variante_de(e) -> str:
    if e["cle"].startswith("figures_"):
        filtre, stop = e["cle"][len(e["candidate"]) + 1:].rsplit("_", 3)[:2]
        noms = {"aucun": "sans filtre", "rsi": "divergence RSI", "ema50": "EMA 50", "rsi_ema50": "RSI + EMA 50"}
        return f" ({noms[filtre]}, stop {stop})"
    return (" (auteur)" if e["cle"].endswith("_auteur") else " (auteur + point mort)" if e["cle"].endswith("_auteur_be")
            else " (adaptée, hors échantillon)" if e["cle"].endswith("_adaptee") else "")


def ligne(e):
    nom = NOMS.get(e["candidate"], e["candidate"])
    variante = variante_de(e)
    pf ="infini" if e["profit_factor"] == float("inf") else fr(e["profit_factor"], ".2f")
    return (f"| {nom}{variante} | {e['base']} {e['tf']} | {e['trades']} | {pct(e['taux_reussite'])} | "
            f"{r(e['esperance_R'])} | {pf} | {fr(e['R_par_mois'], '+.2f')} | "
            f"{fr(e['drawdown_max_pct'], '.1f')} % | {fr(e['p_valeur'], '.3f')} | "
            f"{'OUI' if e.get('survit_holm') else ('témoin' if e['temoin'] else 'non')} |")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    registre = [e for e in _registre() if e.get("trades")]
    comptes = [e for e in registre if not e["temoin"]]
    for e, ok in zip(comptes, banc.holm([e["p_valeur"] for e in comptes])):
        e["survit_holm"] = ok
    survivants = [e for e in comptes if e.get("survit_holm")]
    fiables = [e for e in comptes if e["trades"] >= 200]
    meilleur_taux = max((e for e in comptes if e["trades"] >= 100), key=lambda e: e["taux_reussite"])

    L = []
    L.append("# NEBULA Trader · recherche de stratégies scalping et intraday (EUR/USD, NAS100)\n")
    if survivants:
        L.append(f"## Verdict : OUI, {len(survivants)} test(s) sur {len(comptes)} résistent à la correction statistique.\n")
    else:
        L.append(f"## Verdict : NON, pas avec nos données. Aucun des {len(comptes)} tests ne montre une "
                 f"rentabilité qu'on puisse distinguer de la chance après correction statistique.\n")
    L.append("*Généré par `python -m trading.recherche.rapport` à partir des résultats bruts. "
             "Coûts réels Deriv (spread médian mesuré sur ticks, 1 point de glissement par sens, swap), "
             "entrée à l'ouverture suivante, stop avant objectif dans une même bougie, objectif ≥ 2 R, "
             "stop jamais plus court que le minimum du courtier.*\n")

    # --- L'objectif de Mongazi : R:R d'au moins 1:2 ET plus de 50 % de réussite ------------
    def motifs_de(e):
        if e["cle"].startswith("sniper_"):
            return motifs_sniper(e["cle"])
        if e["cle"].startswith("figures_"):
            return motifs_figures(e["cle"])
        if e["cle"].startswith("videos_"):
            base_cle, variante = e["cle"].rsplit("_", 1)
            if variante == "be":
                base_cle, variante = e["cle"][:-len("_auteur_be")], "auteur_be"
            chemin = DOSSIER / f"{base_cle}.json"
            if not chemin.exists():
                return {}
            d = json.loads(chemin.read_text(encoding="utf-8"))
            bloc = (d.get("adaptee") or {}).get("hors_echantillon") if variante == "adaptee" else d.get(variante)
            return (bloc or {}).get("motifs", {})
        chemin = DOSSIER / f"{e['cle']}.json"
        if not chemin.exists():
            return {}
        return (json.loads(chemin.read_text(encoding="utf-8")).get("hors_echantillon") or {}).get("motifs", {})

    for e in comptes:
        m = motifs_de(e)
        e["part_objectif"] = m.get("objectif", 0) / e["trades"] if e["trades"] else 0.0
    L.append("## 0. Ton objectif : R:R d'au moins 1:2 ET plus de 50 % de réussite\n")
    vises = [e for e in comptes if e["trades"] >= 100 and e["taux_reussite"] > 0.5 and e["esperance_R"] > 0]
    stricts = [e for e in comptes if e["trades"] >= 100 and e["part_objectif"] > 0.5]
    L.append(f"- Tests avec **plus de 50 % de trades gagnants, au moins 100 trades et une espérance positive** : "
             f"**{len(vises)}** sur {len(comptes)}.")
    L.append(f"- Tests où **plus de la moitié des trades atteignent vraiment leur objectif d'au moins 2 R** : "
             f"**{len(stricts)}** sur {len(comptes)}.")
    L.append("- ⚠️ « Gagnant » compte tout trade fini au-dessus de zéro, y compris une petite sortie par le temps ou en "
             "fin de séance. C'est pour ça que les deux lignes diffèrent : seule la seconde dit « j'ai pris mes 2 R ».")
    L.append("- **Le calcul qui borne l'ambition** : à 1:2, gagner 2 R une fois sur deux rapporte **+0,5 R par trade** "
             "avant coûts. La meilleure espérance mesurée ici sur au moins 100 trades est de "
             f"**{r(max((e['esperance_R'] for e in comptes if e['trades'] >= 100), default=0.0))} R**.\n")
    meilleurs = sorted((e for e in comptes if e["trades"] >= 100), key=lambda e: -e["taux_reussite"])[:8]
    L.append("Les plus hauts taux de réussite sur au moins 100 trades :\n")
    L.append("| Stratégie | Marché | Trades | Gagnants | Objectif ≥ 2 R atteint | Espérance (R) |\n|---|---|---|---|---|---|")
    for e in meilleurs:
        variante = " (auteur)" if e["cle"].endswith("_auteur") else (" (auteur + point mort)" if e["cle"].endswith("_auteur_be") else "")
        L.append(f"| {NOMS.get(e['candidate'], e['candidate'])}{variante} | {e['base']} {e['tf']} | {e['trades']} | "
                 f"{pct(e['taux_reussite'])} | {pct(e['part_objectif'])} | {r(e['esperance_R'])} |")
    L.append("")

    L.append("## Les données utilisées\n")
    L.append("| Instrument | M1 | M5 | M15 | H1 |\n|---|---|---|---|---|")
    for base in ("EURUSD", "NAS100"):
        cellules = []
        for tf in ("M1", "M5", "M15", "H1"):
            try:
                s = banc.charger(base, tf)
                cellules.append(f"{str(s.temps[0])[:7]} → {str(s.temps[-1])[:7]} ({len(s):,} bougies)".replace(",", " "))
            except FileNotFoundError:
                cellules.append("absent")
        L.append(f"| {base} | " + " | ".join(cellules) + " |")
    L.append("\nMT5 réglé sur « Max. barres = Unlimited » par Mongazi le 2026-09-17 : **7,7 ans de M1 et 14,7 ans de "
             "M5 sur EUR/USD**. Le M1 est borné à 2019 (8 Go de mémoire vive). Le NAS100 ne remonte qu'à janvier 2024 "
             "chez Deriv, quelle que soit l'unité de temps.\n")

    entete = ("| Stratégie | Marché | Trades | Réussite | Espérance (R) | PF | R/mois | Drawdown à 1 % | p | Correction |\n"
              "|---|---|---|---|---|---|---|---|---|---|")
    L.append("## 1. Les 5 stratégies publiées « à haut taux de réussite » (walk-forward, hors échantillon)\n")
    L.append(entete)
    for e in sorted((e for e in registre if e["cle"].startswith("t1_")), key=lambda e: -e["esperance_R"]):
        L.append(ligne(e))

    L.append("\n## 2. Les vidéos\n")
    L.append("« auteur » = les règles telles que la vidéo les enseigne, sans rien optimiser. « adaptée » = une petite "
             "grille de réglages jugée hors échantillon.\n")
    L.append(entete)
    for e in sorted((e for e in registre if e["cle"].startswith("videos_")), key=lambda e: -e["esperance_R"]):
        L.append(ligne(e))

    L.append("\n### La troisième vidéo : « Sniper Entry » (balayage M15, clôture M1)\n")
    L.append("Testée à part, en M1 avec simulation bid/ask minute par minute, historique des annonces Forex Factory et "
             "compte de 10 000 $ : **détail complet dans `trading/RECHERCHE-SNIPER.md`**.\n")
    L.append(entete)
    for e in sorted((e for e in registre if e["cle"].startswith("sniper_")), key=lambda e: -e["esperance_R"]):
        L.append(ligne(e))

    L.append("\n### Les vidéos, version auteur, année par année\n")
    for fichier in sorted(DOSSIER.glob("videos_video_*.json")):
        d = json.loads(fichier.read_text(encoding="utf-8"))
        a = d.get("auteur") or {}
        if a.get("trades", 0) < 30 or not a.get("par_annee"):
            continue
        L.append(f"**{NOMS.get(d['candidate'])} · {d['base']} {d['tf']}** ({d['periode']}, {a['trades']} trades, "
                 f"{pct(a['taux_reussite'])}, {r(a['esperance_R'])} R par trade)\n")
        L.append("| Année | Trades | Réussite | Somme des R |\n|---|---|---|---|")
        for annee, v in a["par_annee"].items():
            L.append(f"| {annee} | {v['trades']} | {pct(v['taux_reussite'])} | {fr(v['somme_R'], '+.1f')} |")
        L.append("")

    figs = [e for e in registre if e["cle"].startswith("figures_")]
    if figs:
        L.append("\n## 2 bis. Les figures chartistes (ETE, ETE inversé, biseaux, avec ou sans RSI et EMA 50)\n")
        L.append(f"{len(figs)} versions avec au moins un trade, en H1, H4 et D1, objectif 2 R : **détail complet dans "
                 "`trading/RECHERCHE-FIGURES.md`**. Les 10 meilleures par p, sur au moins 30 trades :\n")
        L.append(entete)
        for e in sorted((e for e in figs if e["trades"] >= 30), key=lambda e: e["p_valeur"])[:10]:
            L.append(ligne(e))

    L.append("\n## 3. Le taux de réussite\n")
    L.append(f"- Le plus haut sur au moins 100 trades : **{pct(meilleur_taux['taux_reussite'])}**, "
             f"{NOMS.get(meilleur_taux['candidate'])} sur {meilleur_taux['base']} {meilleur_taux['tf']} "
             f"({meilleur_taux['trades']} trades, espérance {r(meilleur_taux['esperance_R'])} R).")
    petits = [e for e in comptes if e["trades"] < 100]
    if any(e["taux_reussite"] >= 0.8 and e["trades"] >= 100 for e in comptes):
        L.append("- **Au moins un test dépasse 80 % sur 100 trades ou plus** : voir les tableaux.")
    elif petits:
        haut = max(petits, key=lambda e: e["taux_reussite"])
        bas_ic, haut_ic = banc._wilson(round(haut["taux_reussite"] * haut["trades"]), haut["trades"])
        L.append(f"- **Aucun 80 % sur 100 trades ou plus.** Le plus haut taux affiché, {pct(haut['taux_reussite'])} "
                 f"({NOMS.get(haut['candidate'])}, {haut['base']} {haut['tf']}), porte sur **{haut['trades']} trades** : "
                 f"l'intervalle de confiance va de {pct(bas_ic)} à {pct(haut_ic)}.")
    L.append("- À 1:2, le point mort est à **33,3 %** de réussite. Un taux de réussite élevé sans objectif d'au moins "
             "2 R ne dit rien de la rentabilité.\n")

    L.append("## 4. PRO et BOOST : les stratégies retenues\n")
    if not survivants:
        L.append("**Aucune.** Retenir deux stratégies par profil sur ces chiffres, ce serait choisir au hasard parmi "
                 "des résultats qu'on ne peut pas distinguer de zéro. Les pistes qui méritent plus de données :\n")
        pistes = [e for e in comptes if e["esperance_R"] > 0 and e["trades"] >= 14]
        for e in sorted(pistes, key=lambda e: e["p_valeur"])[:4]:
            L.append(f"- **{NOMS.get(e['candidate'])}** · {e['base']} {e['tf']}"
                     f"{variante_de(e)} : {e['trades']} trades, "
                     f"{pct(e['taux_reussite'])}, {r(e['esperance_R'])} R, p = {fr(e['p_valeur'], '.2f')}.")
        L.append("")

    L.append("## 5. Le million de dollars\n")
    L.append("Rendement **mensuel** composé à tenir chaque mois, sans une seule mauvaise année :\n")
    L.append("| Capital de départ | en 3 ans | en 5 ans | en 10 ans | en 20 ans |\n|---|---|---|---|---|")
    for c in (1_000, 10_000, 100_000):
        g = croissance_necessaire(c)
        L.append(f"| {c:,} $ | ".replace(",", " ") + " | ".join(f"{g[a]:.1f} %".replace(".", ",") for a in ("3", "5", "10", "20")) + " |")
    L.append("")
    # les tests Sniper ont leur propre projection à 10 000 $ (RECHERCHE-SNIPER.md) et d'autres fichiers
    candidats_projection = [e for e in comptes if e["esperance_R"] > 0 and e["trades"] >= 100
                            and not e["cle"].startswith("sniper_")]
    for e in sorted(candidats_projection, key=lambda e: e["p_valeur"])[:2]:
        chemin = DOSSIER / (e["cle"].rsplit("_", 1)[0] + ".json" if e["cle"].startswith("videos_") else e["cle"] + ".json")
        d = json.loads(chemin.read_text(encoding="utf-8"))
        R = d.get("trades_R") or (d.get("adaptee") or {}).get("trades_R") or d.get("trades_R_auteur")
        L.append(f"**Si {NOMS.get(e['candidate'])} ({e['base']} {e['tf']}, {r(e['esperance_R'])} R, "
                 f"{fr(e['trades_par_mois'], '.1f')} trades par mois) gardait son espérance mesurée**, ce qui n'est pas prouvé :\n")
        L.append("| Capital | Risque par trade | P(1 M $ en 10 ans) | Délai médian si atteint | P(perdre 50 % en chemin) |\n|---|---|---|---|---|")
        for capital in (1_000, 10_000):
            for risque in (1.0, 3.0, 10.0):
                p = projeter(R, trades_par_mois=e["trades_par_mois"], capital=capital, risque_pct=risque)
                if not p["valide"]:
                    continue
                delai = "jamais" if p["mois_median_si_atteint"] is None else f"{fr(p['mois_median_si_atteint'] / 12, '.1f')} ans"
                L.append(f"| {capital:,} $ | {risque:.0f} % | {pct(p['p_million'])} | {delai} | {pct(p['p_perdre_moitie'])} |".replace(",", " ", 1))
        L.append("")

    L.append("## 6. Conseils\n")
    L.append("1. **Ne rien passer en réel.** Aucun résultat ne distingue un avantage de la chance.")
    L.append("2. **Ne pas croire un résultat court** : un échantillon de quelques mois ou de quelques dizaines de "
             "trades dit presque toujours n'importe quoi. Pour le vérifier : `python -m trading.recherche.videos_lancer` "
             "puis `python -m trading.recherche.rapport`.")
    L.append("3. **Garder la règle 1:2 en PRO et en BOOST** (appliquée le 2026-09-17, le videur refuse désormais 1:1,5).")
    L.append("4. **Se méfier des preuves des vidéos** : captures de gains, replays choisis, abonnements et prop firms "
             "vendus dans la même vidéo. Aucune des trois ne publie une série de trades.")
    L.append("5. **Le million** exige un avantage réel ET du temps. Monter le risque ne remplace pas l'avantage : "
             "à espérance nulle, un risque plus grand ruine seulement plus vite.\n")

    L.append("## 7. Ce qui n'est pas modélisé, et pourquoi c'est écrit\n")
    L.append("- Passage au point mort et ajouts de positions (Hugo FX) : une seule position par instrument, règle maison.")
    L.append("- Lignes de tendance de MambaFx : remplacées par la structure (plus haut plus haut, plus bas plus haut, cassure).")
    L.append("- PD arrays et FVG de Hugo FX : remplacés par un retour sous 50 % (ou 62 %) de l'impulsion M15.")
    L.append("- Transposition H1 des vidéos : sortie temporelle calibrée pour le M1, trop courte pour une structure journalière.\n")

    L.append("## Sources\n")
    for s in ("StockCharts ChartSchool, RSI(2) : https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2",
              "MQL5, Larry Connors RSI2 intraday : https://www.mql5.com/en/articles/17636",
              "learn-forextrading, 5 min scalping Bollinger + RSI : https://www.learn-forextrading.org/2017/06/5-min-scalping-bollinger-bands-and-rsi.html",
              "Alvarez Quant Trading, IBS : https://alvarezquanttrading.com/blog/internal-bar-strength-for-mean-reversion/",
              "ForexCracked, 200 EMA + Stochastic : https://www.forexcracked.com/education/forex-200-ema-and-stochastic-indicator-scalping-strategy/",
              "London breakout, backtests GitHub : https://github.com/adrian-baehler/london-breakout",
              "Vidéo MambaFx « The Only 1-Minute Scalping Strategy You'll EVER NEED » (fichier fourni)",
              "Vidéo Hugo FX « J'ai trouvé la MEILLEURE Stratégie de Scalping M1 pour 2026 ! » (fichier fourni)",
              "Vidéo Mulham Trading « My Secret 1 Minute Scalping Strategy (Sniper Entry) » (fichier fourni)",
              "Calendrier économique Forex Factory, pages hebdomadaires 2019-2026 : https://www.forexfactory.com/calendar"):
        L.append(f"- {s}")
    SORTIE.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
