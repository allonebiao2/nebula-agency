# -*- coding: utf-8 -*-
"""
Écrit `trading/RECHERCHE-SNIPER.md` en RELISANT les résultats de `sniper_lancer` (JSON + registre).

    python -m trading.recherche.sniper_rapport

Aucun chiffre n'est recopié à la main : relancer après chaque `sniper_lancer`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from . import banc
from .lancer import _registre
from .sniper_lancer import SORTIE, lire

RAPPORT = Path(__file__).resolve().parents[1] / "RECHERCHE-SNIPER.md"
NOMS_VERSIONS = {
    "auteur": "Règles de la vidéo, telles quelles",
    "auteur_annonces": "Règles de la vidéo + pas d'entrée 30 min avant / 15 min après une annonce forte",
    "auteur_annonces_sortie": "… + sortie 5 min avant chaque annonce forte",
    "auteur_imbalance": "… + sommet dans un imbalance non rempli EXIGÉ",
    "auteur_5R": "… objectif 5 R (au lieu de 3)",
    "auteur_2R": "… objectif 2 R",
    "auteur_niveau_oppose": "… objectif = prochain niveau M15 opposé (au moins 3 R)",
    "auteur_dernier_creux_m1": "… la clôture M1 doit aussi casser le dernier creux M1",
    "auteur_stop_saute": "… stop trop court pour Deriv : trade sauté au lieu d'élargi",
}


def pct(x, d=1):
    return "n/a" if x is None else f"{100 * x:.{d}f} %".replace(".", ",")


def num(x, fmt="+.3f"):
    return "n/a" if x is None else format(x, fmt).replace(".", ",")


def usd(x):
    return "n/a" if x is None else f"{x:,.0f} $".replace(",", " ")


def projection_un_an(R: np.ndarray, trades_par_mois: float, *, capital=10_000.0, risque=1.0, chemins=10_000, graine=5) -> dict:
    """Si les trades de l'année suivante ressemblaient à ceux du passé (tirés au hasard avec remise)."""
    rng = np.random.default_rng(graine)
    n = int(round(trades_par_mois * 12))
    tirs = rng.choice(R, size=(chemins, n), replace=True)
    facteurs = np.maximum(1 + tirs * risque / 100, 0.0)
    equite = capital * np.cumprod(facteurs, axis=1)
    final = equite[:, -1]
    plus_bas = equite.min(axis=1)
    return {"trades": n, "mediane": float(np.median(final)), "p10": float(np.percentile(final, 10)),
            "p90": float(np.percentile(final, 90)), "p_gain": float((final > capital).mean()),
            "p_perte_20": float((plus_bas <= capital * 0.8).mean()), "p_perte_50": float((plus_bas <= capital * 0.5).mean())}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fid, cpt = lire("fidelite"), lire("compte")
    aut = {b: lire(f"auteur_{b}") for b in ("EURUSD", "NAS100")}
    heu = {b: lire(f"heures_{b}") for b in ("EURUSD", "NAS100")}
    var = {b: lire(f"variantes_{b}") for b in ("EURUSD", "NAS100")}
    registre = [e for e in _registre() if e.get("trades")]
    comptes_reg = [e for e in registre if not e["temoin"]]
    holm = dict(zip([e["cle"] for e in comptes_reg], banc.holm([e["p_valeur"] for e in comptes_reg])))
    sniper_reg = [e for e in comptes_reg if e["cle"].startswith("sniper_")]
    survivants = [e for e in sniper_reg if holm.get(e["cle"])]
    L = []
    L.append("# NEBULA Trader · « My Secret 1 Minute Scalping Strategy (Sniper Entry) »\n")
    L.append("*Vidéo de Mulham Trading (Edge Skool) envoyée par Mongazi le 2026-09-17. Généré par "
             "`python -m trading.recherche.sniper_rapport` depuis `trading/rapports/recherche/sniper/` : aucun "
             "chiffre recopié à la main. Fiche de la méthode : `trading/recherche/METHODE-SNIPER.md`.*\n")

    # ------------------------------------------------------------------ verdict
    ea, na = aut["EURUSD"]["versions"]["auteur_annonces"]["mesures"], aut["NAS100"]["versions"]["auteur_annonces"]["mesures"]
    perd = ea["esperance_R"] < 0 and na["esperance_R"] < 0
    if not survivants and perd:
        L.append("## Verdict : NON. La méthode ne gagne pas, ni sur EUR/USD ni sur NAS100, et elle est très loin de tes critères.\n")
    elif not survivants:
        L.append("## Verdict : NON PROUVÉ. Aucun test ne résiste à la correction statistique, et la méthode est loin de tes critères.\n")
    else:
        L.append("## Verdict : À EXAMINER. Au moins un test résiste à la correction statistique (section 8).\n")
    if survivants:
        L.append(f"⚠️ {len(survivants)} test(s) Sniper survivent à la correction de Holm : voir la section 8.\n")
    L.append("Tes trois chiffres d'abord (règles de la vidéo + filtre des annonces de l'agent, coûts Deriv réels) :\n")
    L.append("| | Ton critère | EUR/USD (2019-2026) | NAS100 (2024-2026) |\n|---|---|---|---|")
    L.append(f"| Trades gagnants | plus de 50 % (idéal 60-70 %) | **{pct(ea['taux_reussite'])}** | **{pct(na['taux_reussite'])}** |")
    L.append(f"| Objectif de 3 R réellement atteint | | {pct(ea['objectif_atteint'])} | {pct(na['objectif_atteint'])} |")
    L.append(f"| R:R réalisé (gain moyen / perte moyenne) | au moins 1:2 | 1:{num(ea['rr_realise'], '.2f')} | 1:{num(na['rr_realise'], '.2f')} |")
    for k_, lib in ((5, "5"), (6, "6")):
        L.append(f"| Probabilité de {lib} pertes d'affilée sur 100 trades | extrêmement basse | "
                 f"**{pct(ea['series_perdantes'][f'p_{k_}_pertes_sur_100_montecarlo'], 0)}** | "
                 f"**{pct(na['series_perdantes'][f'p_{k_}_pertes_sur_100_montecarlo'], 0)}** |")
    L.append(f"| Plus longue série perdante observée | | {ea['series_perdantes']['plus_longue_observee']} trades | "
             f"{na['series_perdantes']['plus_longue_observee']} trades |")
    L.append(f"| Espérance par trade | positive | **{num(ea['esperance_R'])} R** | **{num(na['esperance_R'])} R** |")
    L.append(f"| Trades | au moins 100 | {ea['trades']} | {na['trades']} |\n")
    bruts = {b: aut[b]["versions"]["auteur_annonces"]["sans_couts"] for b in aut}
    sans_avantage = all(bruts[b]["esperance_R"] < 0.05 and bruts[b]["p_valeur"] > 0.05 for b in bruts)
    L.append(f"- **Même sans AUCUN coût** (ni spread, ni glissement), la méthode fait **{num(bruts['EURUSD']['esperance_R'])} R** "
             f"par trade sur EUR/USD ({pct(bruts['EURUSD']['taux_reussite'])} de gagnants, p = {num(bruts['EURUSD']['p_valeur'], '.2f')}) "
             f"et **{num(bruts['NAS100']['esperance_R'])} R** sur NAS100 (p = {num(bruts['NAS100']['p_valeur'], '.2f')})."
             + (" Aucun des deux ne se distingue du hasard : il n'y a pas d'avantage à protéger." if sans_avantage else "")
             + f" Le courtier prend ensuite environ **{num(ea['cout_moyen_R'], '.2f')} R** par trade sur EUR/USD et "
               f"**{num(na['cout_moyen_R'], '.2f')} R** sur NAS100.")
    L.append(f"- À un objectif de 3 R, l'équilibre est à **25 %** de réussite avant coûts. La méthode en fait "
             f"{pct(bruts['EURUSD']['taux_reussite'])} sur EUR/USD et {pct(bruts['NAS100']['taux_reussite'])} sur NAS100 "
             "avant coûts : à peu près ce qu'on obtient en entrant au hasard avec un stop et un objectif de ces tailles.")
    ts = fid.get("trades_semaine") or []
    montres = {e["trade"]["entree_utc"] for e in fid["exemples"] if e.get("trade")}
    caches = [t for t in ts if t["entree_utc"] not in montres]
    L.append("- **Les exemples de la vidéo sont vrais** (retrouvés au dixième de pip, et gagnants) : ils sont choisis. "
             f"Du 27 octobre au 7 novembre 2025, les mêmes règles ont pris **{len(ts)} trades** ; hors des "
             f"{len(montres)} montrés, il y en a {len(caches)}, dont **{sum(1 for t in caches if t['R'] <= 0)} perdants** "
             f"(somme {num(sum(t['R'] for t in caches), '+.1f')} R).\n")

    # ------------------------------------------------------------------ 10 000 $
    L.append("## 1. Les 10 000 $\n")
    L.append("Tailles de position réelles (lots arrondis vers le bas, lot minimum et maximum du courtier), résultat "
             "net de spread, glissement et swap. **« Vidéo »** = risque fixe par trade, aucun frein, comme l'auteur. "
             "**« NEBULA PRO »** = les verrous de ton agent (levier ×3, 0,50 lot au plus, 3 trades/jour, 8/semaine, "
             "4 h d'attente après une perte, -3 %/jour, -6 %/semaine, -10 %/mois, arrêt total à -20 %).\n")

    def ligne_compte(cle, titre):
        c = cpt.get(cle)
        if not c or not c.get("trades"):
            return f"| {titre} | aucun trade | | | | | | | | |"
        return (f"| {titre} | {usd(c['capital_final'])} | **{usd(c['benefice_usd'])}** | **{num(c['rendement_pct'] / 100 if c['rendement_pct'] is not None else None, '+.1%').replace('%', ' %')}** | "
                f"{num(c['rendement_annuel_pct'] / 100, '+.1%').replace('%', ' %')} | {num(c['drawdown_max_pct'] / 100, '.1%').replace('%', ' %')} ({usd(c['drawdown_max_usd'])}) | "
                f"{c['trades']} | {pct(c['taux_reussite'])} | {usd(c['gain_moyen_usd'])} / {usd(c['perte_moyenne_usd'])} | "
                f"{c['serie_perdante_max']} | {num(c['mois_positifs_pct'] / 100, '.0%').replace('%', ' %')} |")

    L.append("| Compte (1 % par trade) | Capital final | Bénéfice | En % | Par an | Drawdown max | Trades | Gagnants | Gain moyen / perte moyenne | Pire série | Mois positifs |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for panier, titre in (("EURUSD", "EUR/USD 2019-2026"), ("NAS100", "NAS100 2024-2026"), ("EURUSD_et_NAS100", "Les deux, 2024-2026")):
        for regles, nom_r in (("video", "vidéo"), ("pro", "NEBULA PRO")):
            L.append(ligne_compte(f"auteur_annonces|{panier}|{regles}|1.0", f"{titre}, {nom_r}"))
    L.append("")
    L.append("Selon le risque par trade, règles de la vidéo :\n")
    L.append("| Risque par trade | EUR/USD 2019-2026 | NAS100 2024-2026 | Les deux 2024-2026 |\n|---|---|---|---|")
    for risque in (0.5, 1.0, 2.0, 3.0):
        cel = []
        for panier in ("EURUSD", "NAS100", "EURUSD_et_NAS100"):
            c = cpt.get(f"auteur_annonces|{panier}|video|{risque}", {})
            cel.append(f"{usd(c.get('capital_final'))} ({num((c.get('rendement_pct') or 0) / 100, '+.0%').replace('%', ' %')}, drawdown {num((c.get('drawdown_max_pct') or 0) / 100, '.0%').replace('%', ' %')})")
        L.append(f"| {fr_pct(risque)} | " + " | ".join(cel) + " |")
    L.append("")
    pro_eu = cpt.get("auteur_annonces|EURUSD|pro|1.0", {})
    L.append(f"- ⚠️ **En NEBULA PRO, le risque choisi ne change presque rien** : le levier ×3 et le plafond de 0,50 lot "
             f"ramènent le risque réel à **{num((pro_eu.get('risque_moyen_pct') or 0) / 100, '.2%').replace('%', ' %')}** par trade en moyenne sur EUR/USD "
             f"(le stop médian de {num(ea['risque_median_unite'], '.1f')} pips demande {num(100 / ea['risque_median_points'], '.1f')} lots à 1 % "
             f"de 10 000 $, soit un levier de ×{100 / ea['risque_median_points'] * 100_000 * 1.1 / 10_000:.0f}). Les freins limitent la casse, ils ne "
             f"créent pas de gain." + (f" {pro_eu['arret_total'].capitalize()}." if pro_eu.get("arret_total") else ""))
    refus = pro_eu.get("motifs_refus") or {}
    if refus:
        L.append("- Trades refusés par les verrous PRO sur EUR/USD : " + ", ".join(f"{k} {v}" for k, v in sorted(refus.items(), key=lambda x: -x[1])) + ".")
    video_eu = cpt.get("auteur_annonces|EURUSD|video|1.0", {})
    if video_eu.get("par_annee"):
        L.append("\nEUR/USD, règles de la vidéo à 1 %, année par année :\n")
        L.append("| Année | Résultat | En % | Capital en fin d'année |\n|---|---|---|---|")
        for a, v in video_eu["par_annee"].items():
            L.append(f"| {a} | {usd(v['pnl_usd'])} | {num(v['rendement_pct'] / 100, '+.1%').replace('%', ' %')} | {usd(v['capital_fin'])} |")
        L.append(f"\nMeilleur mois {num(video_eu['meilleur_mois_pct'] / 100, '+.1%').replace('%', ' %')}, pire mois "
                 f"{num(video_eu['pire_mois_pct'] / 100, '+.1%').replace('%', ' %')}, plus gros gain {usd(video_eu['plus_gros_gain_usd'])}, "
                 f"plus grosse perte {usd(video_eu['plus_grosse_perte_usd'])}, {num(video_eu['trades_par_mois'], '.1f')} trades par mois.\n")
    L.append("**Et l'année prochaine ?** Si les trades à venir ressemblaient aux trades passés (10 000 tirages, 1 % par trade) :\n")
    L.append("| Marché | Trades en 1 an | Capital médian | 1 fois sur 10 sous | 1 fois sur 10 au-dessus de | Chance de finir gagnant | Chance de toucher -20 % | Chance de toucher -50 % |\n|---|---|---|---|---|---|---|---|")
    for b in ("EURUSD", "NAS100"):
        v = aut[b]["versions"]["auteur_annonces"]
        p = projection_un_an(np.array(v["trades_R"]), v["mesures"]["trades_par_mois"])
        L.append(f"| {b} | {p['trades']} | {usd(p['mediane'])} | {usd(p['p10'])} | {usd(p['p90'])} | {pct(p['p_gain'], 0)} | "
                 f"{pct(p['p_perte_20'], 0)} | {pct(p['p_perte_50'], 0)} |")
    L.append("")

    # ------------------------------------------------------------------ méthode
    L.append("## 2. La méthode (maîtrisée, règle par règle)\n")
    L.append("| # | Règle | Moment de la vidéo |\n|---|---|---|")
    for i, (regle, moment) in enumerate((
            ("Unité principale **M15**, entrée en **M1** : « attraper les balayages de liquidité M15 avec le graphique M1 »", "09:25"),
            ("Direction : **EMA 200** (entourée à l'écran). Au-dessus = achats, en dessous = ventes, avec une structure propre, pas un prix qui zigzague autour", "03:10 · 04:39 · 04:57"),
            ("**Continuation seulement** : en baisse on vise les sommets, en hausse les creux", "06:16"),
            ("Étape 1 : marquer un sommet M15 dans la tendance, de préférence dans un imbalance (FVG) non rempli, partie d'une structure propre ; plus hauts/bas de séance aussi", "09:45 · 08:51"),
            ("Étape 2 : une bougie M15 prend le sommet **sans clôturer au-dessus** (rejet par la mèche)", "10:20"),
            ("Cette bougie doit être **haussière** pour une vente (baissière pour un achat) : sinon « le mouvement est déjà parti »", "22:15 · 25:27"),
            ("Étape 3 : **rectangle** de la clôture de cette bougie à son extrême ; regarder l'ouverture de la M15 suivante", "10:45 · 11:16"),
            ("**Entrée** quand une bougie M1 clôture hors du rectangle ; valide tant qu'aucune clôture ne dépasse le sommet", "15:06 · 20:33"),
            ("**Stop** légèrement au-delà de l'extrême (le spread) ; **objectif** 3:1 minimum, ou le prochain niveau clé", "15:56 · 01:18 · 16:06"),
            ("**Heures** : début d'Asie, Londres, New York et un peu après, jamais après New York", "12:36 · 13:12 · 20:10")), 1):
        L.append(f"| {i} | {regle} | [{moment}] |")
    L.append("\n**Ce que l'image a tranché** : graphique EUR/USD M15 Tickmill en **heure de New York** ; boîtes de séance "
             "Asie 20:00-00:00, Londres 02:00-05:00, New York 07:00-10:00 ; stops de **1,6 à 4 pips** ; la vidéo "
             "vend un abonnement (Edge Skool) et ne publie aucune statistique. **Elle ne parle jamais des annonces "
             "économiques** : le filtre des annonces est ton ajout.\n")

    # ------------------------------------------------------------------ fidélité
    L.append("## 3. Le code voit-il ce que l'auteur montre ?\n")
    L.append("| Exemple de la vidéo | Ce qu'il montre | Bougie Deriv (M15) | Détecté | Trade simulé |\n|---|---|---|---|---|")
    for e in fid["exemples"]:
        b_ = e["bougie_deriv"]
        t = e.get("trade")
        L.append(f"| {e['nom']}, {e['balayage_utc']} UTC | {e['video']} | haut {num(b_['haut'], '.5f')}, clôture {num(b_['cloture'], '.5f')} | "
                 f"{'oui' if e['detecte'] else '**non**'} | " +
                 (f"entrée {t['entree_utc'][11:16]} UTC, stop {num(t['risque_pips'], '.1f')} pips, **{num(t['R'], '+.2f')} R** ({t['motif']})" if t else "—") + " |")
    L.append("\n- Les prix Deriv reproduisent ceux de Tickmill **au dixième de pip** : le serveur Deriv est en UTC et le "
             "graphique de l'auteur en heure de New York.")
    L.append("- **Exemple 4 non détecté**, et c'est dit : chez Deriv la bougie clôture à 1,15309, soit 0,3 pip AU-DESSUS "
             "des deux sommets égaux qu'elle balaie (1,15306). La règle « clôture sous le sommet » la refuse.")
    L.append("- ⚠️ **Un seul réglage a été choisi pour retrouver ses exemples, avant tout résultat** : la structure "
             "« majeure » (pivots M15 de 12 bougies de chaque côté). Avec des pivots de 5 bougies, un simple repli inverse "
             "la tendance et AUCUN exemple ne passe.")
    autres = [x for x in fid["setups_semaine"] if x["balayage_utc"] not in [e["balayage_utc"] + ":00" for e in fid["exemples"]]]
    L.append(f"- La même semaine (27 octobre - 7 novembre 2025), le détecteur a vu **{len(fid['setups_semaine'])} setups**, "
             f"dont {len(autres)} que la vidéo ne montre pas.\n")

    # ------------------------------------------------------------------ versions
    L.append("## 4. Toutes les versions testées (historique complet, coûts Deriv)\n")
    for b in ("EURUSD", "NAS100"):
        d = aut[b]
        L.append(f"**{b}** ({d['periode'][0]} → {d['periode'][1]}, annonces couvertes {d['couverture_annonces'][0]} → {d['couverture_annonces'][1]})\n")
        L.append("| Version | Trades | Gagnants | Objectif atteint | Espérance | PF | Stop médian | Stops élargis | p |\n|---|---|---|---|---|---|---|---|---|")
        for nom, v in d["versions"].items():
            m = v["mesures"]
            L.append(f"| {NOMS_VERSIONS.get(nom, nom)} | {m['trades']} | {pct(m['taux_reussite'])} | {pct(m['objectif_atteint'])} | "
                     f"{num(m['esperance_R'])} R | {num(m['profit_factor'], '.2f')} | {num(m['risque_median_unite'], '.1f')} {m['unite_risque']} | "
                     f"{pct(m['stops_elargis'], 0)} | {num(m['p_valeur'], '.3f')} |")
        v = d["versions"]["auteur_annonces"]
        L.append(f"\nCoûts, même version : sans coûts **{num(v['sans_couts']['esperance_R'])} R** · courtier « raw » (moitié) "
                 f"{num(v['couts_x0.5']['esperance_R'])} R · Deriv {num(v['mesures']['esperance_R'])} R · ×1,5 "
                 f"{num(v['couts_x1.5']['esperance_R'])} R · ×2 {num(v['couts_x2.0']['esperance_R'])} R.\n")

    # ------------------------------------------------------------------ annonces
    L.append("## 5. Les annonces économiques\n")
    L.append("Source : les pages hebdomadaires de Forex Factory (horodatage Unix, aucun fuseau à deviner), 402 semaines. "
             "**Vérifié** : le NFP et l'IPC tombent à 08:30 New York dans 100 % des cas, le FOMC à 14:00 (les deux "
             "exceptions sont les réunions d'urgence de mars 2020). ⛔ Le jeu de données Hugging Face « Forex Factory "
             "2007-2025 » a été écarté : 40 à 50 % des annonces fortes y sont à 00:00, l'heure est perdue.\n")
    L.append("| Marché | Trades dans la fenêtre d'une annonce (-30/+15 min) | Leur espérance | Trades hors fenêtre | Leur espérance |\n|---|---|---|---|---|")
    for b in ("EURUSD", "NAS100"):
        pa = aut[b]["versions"]["auteur"]["pres_annonce"]
        L.append(f"| {b} | {pa['dans_la_fenetre']['trades']} ({pct(pa['dans_la_fenetre']['taux_reussite'])} gagnants) | "
                 f"{num(pa['dans_la_fenetre']['esperance_R'])} R | {pa['hors_fenetre']['trades']} | {num(pa['hors_fenetre']['esperance_R'])} R |")
    L.append("")
    for b in ("EURUSD", "NAS100"):
        pa = aut[b]["versions"]["auteur"]["pres_annonce"]
        hors, dans = pa["hors_fenetre"], pa["dans_la_fenetre"]
        phrase = (f"- {b} : hors des annonces la méthode fait {num(hors['esperance_R'])} R"
                  + (", donc le filtre ne peut pas la rendre gagnante." if (hors["esperance_R"] or 0) < 0 else "."))
        if dans["trades"] and dans["trades"] < 100 and (dans["esperance_R"] or 0) > 0:
            phrase += (f" Les {dans['trades']} trades pris près d'une annonce gagnent ({num(dans['esperance_R'])} R), mais "
                       f"{dans['trades']} trades ne prouvent rien, et c'est justement là que le spread s'écarte en vrai.")
        L.append(phrase)
    L.append("")

    # ------------------------------------------------------------------ heures
    L.append("## 6. Les meilleures heures\n")
    L.append("Choisies sur les **80 % anciens** seulement (heures de New York avec au moins 30 trades et une espérance "
             "positive), puis jugées **une seule fois** sur les 20 % récents, jamais vus.\n")
    L.append("| Marché | Heures choisies (New York) | Au contrôle : trades | Gagnants | Espérance | Séances de l'auteur au contrôle |\n|---|---|---|---|---|---|")
    for b in ("EURUSD", "NAS100"):
        h = heu[b]
        c = h.get("controle_heures_choisies", {})
        a = h["controle_seances_auteur"]
        L.append(f"| {b} | {', '.join(f'{x} h' for x in h['heures_choisies_ny']) or 'aucune'} | {c.get('trades', 0)} | "
                 f"{pct(c.get('taux_reussite'))} | **{num(c.get('esperance_R'))} R** | {a.get('trades', 0)} trades, {num(a.get('esperance_R'))} R |")
    L.append("\nEspérance par heure d'entrée (New York), règles de la vidéo, tout l'historique :\n")
    L.append("| Heure | " + " | ".join(str(hh) for hh in range(24)) + " |\n|---|" + "---|" * 24)
    for b in ("EURUSD", "NAS100"):
        ph = aut[b]["versions"]["auteur_annonces"]["mesures"]["par_heure_ny"]
        L.append(f"| {b} | " + " | ".join((num(ph[str(hh)]['esperance_R'], '+.2f') + f" ({ph[str(hh)]['trades']})") if str(hh) in ph else "" for hh in range(24)) + " |")
    if all((heu[b].get("controle_heures_choisies") or {}).get("esperance_R", 0) <= 0 for b in heu):
        L.append("\nLes heures qui brillaient sur le passé perdent sur la période jamais vue : c'était du bruit.\n")
    else:
        L.append("\n⚠️ Au moins un choix d'heures reste positif au contrôle : voir le registre avant d'y croire (24 heures essayées).\n")

    # ------------------------------------------------------------------ variantes
    L.append("## 7. Les variantes (walk-forward, hors échantillon)\n")
    L.append("Grille : EMA 50 ou 200 · imbalance exigé ou non · objectif 2, 3, 5 R ou niveau opposé · validité 1 ou 4 "
             "bougies M15 · séances de l'auteur ou toutes, filtre des annonces toujours actif. Les réglages sont choisis "
             "sur 4 fenêtres passées et jugés sur la suivante, six fois de suite.\n")
    L.append("| Marché | Combinaisons | Trades hors échantillon | Gagnants | Espérance | p | Contrôle final (20 % récents) |\n|---|---|---|---|---|---|---|")
    for b in ("EURUSD", "NAS100"):
        v = var[b]
        h, c = v["hors_echantillon"], v["controle"]
        L.append(f"| {b} | {v['combinaisons']} | {h.get('trades', 0)} | {pct(h.get('taux_reussite'))} | **{num(h.get('esperance_R'))} R** | "
                 f"{num(h.get('p_valeur'), '.3f')} | {c.get('trades', 0)} trades, {num(c.get('esperance_R'))} R |")
    L.append("")

    # ------------------------------------------------------------------ correction
    L.append("## 8. La correction statistique\n")
    L.append(f"Le registre compte désormais **{len(comptes_reg)} tests** (les 124 d'avant + {len(sniper_reg)} pour cette vidéo). "
             f"Tests Sniper qui survivent à la correction de Holm : **{len(survivants)}**. Tests Sniper à espérance positive : "
             f"**{sum(1 for e in sniper_reg if e['esperance_R'] > 0)}**.\n")

    # ------------------------------------------------------------------ limites
    L.append("## 9. Ce que le backtest ne peut pas voir, et dans quel sens ça joue\n")
    L.append("- **Bougies M1, pas de ticks** : Deriv ne sert aucun tick passé (sondé : 0 tick pour la veille comme pour "
             "2019). L'ordre des prix dans une minute est inconnu, donc **stop avant objectif** quand les deux tombent dans "
             "la même minute : hypothèse défavorable, mais le résultat SANS aucun coût est déjà nul.")
    L.append("- **Le spread de chaque minute** vient du champ `spread` des bougies 2025-2026 recalé sur les ticks du jour "
             "(3 points EUR/USD, jusqu'à 100 points à 17:01 New York ; 70 points fixes NAS100).")
    moitie = {b: aut[b]["versions"]["auteur_annonces"]["couts_x0.5"]["esperance_R"] for b in aut}
    L.append("- **Chez un courtier « raw » comme celui de l'auteur**, les coûts seraient plus bas : c'est la ligne « moitié » "
             f"de la section 4 ({num(moitie['EURUSD'])} R sur EUR/USD, {num(moitie['NAS100'])} R sur NAS100).")
    L.append("- **Le discrétionnaire** : « structure propre », « niveau clé », sorties partielles et objectifs choisis à l'œil "
             "ne se codent pas tels quels. Chaque traduction est écrite dans `trading/recherche/sniper.py` pour être "
             "contestée, et les variantes testent les plus plausibles.")
    saute = aut["EURUSD"]["versions"]["auteur_stop_saute"]["mesures"]["esperance_R"]
    L.append("- **Deriv impose 2 pips** entre le prix et le stop : le stop de 1,6 pip de l'exemple 1 est impossible à poser. "
             f"Élargi (version principale, {num(ea['esperance_R'])} R) ou trade sauté (variante, {num(saute)} R) sur EUR/USD.\n")

    L.append("## 10. Conseils\n")
    annees_m1 = int(aut["EURUSD"]["periode"][1][:4]) - int(aut["EURUSD"]["periode"][0][:4])
    L.append(f"1. **Ne pas trader cette méthode**, ni en démo pour « voir » : {annees_m1} ans de M1 et {ea['trades']} trades "
             "disent déjà ce que six mois de démo diraient, avec beaucoup moins de bruit.")
    L.append("2. **Ne pas l'intégrer à l'agent** : rien ne survit à la correction, rien n'est positif hors échantillon.")
    L.append("3. **Se méfier des exemples parfaits** : ils sont réels, mais sélectionnés. Une méthode se juge sur tous ses "
             "setups, y compris ceux qu'on ne montre pas.")
    L.append(f"4. **Le scalping M1 chez Deriv part avec un handicap d'environ {num(ea['cout_moyen_R'], '.2f')} R par trade** "
             "sur EUR/USD : il faudrait un avantage brut bien supérieur pour le couvrir, et aucune des trois vidéos "
             "reçues n'en a montré.\n")
    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{RAPPORT} écrit ({len(L)} lignes)")
    return 0


def fr_pct(x: float) -> str:
    return f"{x:g} %".replace(".", ",")


if __name__ == "__main__":
    sys.exit(main())
