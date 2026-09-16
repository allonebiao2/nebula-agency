# -*- coding: utf-8 -*-
"""
Mesurer un système. Honnêtement.

La métrique la plus importante n'est ni le gain total, ni le taux de réussite :
c'est **la taille de l'échantillon**. Juger un système sur 10 trades est
l'erreur fatale la plus courante, et elle est facile à démontrer :

    un système à 40 % de réussite produit 6 pertes d'affilée environ
    une fois tous les 60 trades.

Ce n'est pas une panne, c'est la respiration normale du système. À l'inverse,
20 trades gagnants d'affilée ne prouvent rien non plus. D'où l'intervalle de
confiance sur le taux de réussite : il dit ce que les données autorisent à
croire, et rien de plus.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TradeFerme:
    """Un trade terminé, avec tout ce qu'il faut pour l'analyser ET pour apprendre."""
    entree_le: datetime
    sortie_le: datetime
    sens: str
    prix_entree: float
    prix_sortie: float
    stop_initial: float
    objectif: float
    lots: float
    resultat_devise: float          # net, coûts déduits
    resultat_R: float               # en multiples du risque initial
    cout_devise: float              # spread + slippage + commission + swap
    motif_sortie: str               # "stop" | "objectif" | "temporel" | "weekend" | "suiveur"
    these: str = ""
    strategie: str = ""
    contexte: dict = field(default_factory=dict)

    @property
    def gagnant(self) -> bool:
        return self.resultat_devise > 0

    @property
    def duree_heures(self) -> float:
        return (self.sortie_le - self.entree_le).total_seconds() / 3600


def _wilson(succes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalle de confiance à 95 % sur une proportion (Wilson).

    Choisi plutôt que l'intervalle normal parce qu'il reste correct sur les
    petits échantillons — exactement le cas où l'on est tenté de conclure trop
    vite.
    """
    if total == 0:
        return (0.0, 1.0)
    p = succes / total
    d = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / d
    demi = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return (max(0.0, centre - demi), min(1.0, centre + demi))


@dataclass(frozen=True)
class Metriques:
    trades: int
    gagnants: int
    taux_reussite: float
    taux_reussite_ic95: tuple[float, float]
    esperance_R: float
    esperance_devise: float
    profit_factor: float
    gain_moyen_R: float
    perte_moyenne_R: float
    resultat_net: float
    resultat_brut: float
    couts_totaux: float
    couts_pct_du_brut: float
    drawdown_max_pct: float
    drawdown_max_duree_jours: float
    serie_perdante_max: int
    serie_gagnante_max: int
    sharpe_annualise: float
    sortino_annualise: float
    mar: float
    duree_moyenne_h: float
    trades_par_mois: float
    capital_initial: float
    capital_final: float

    # --- Le verdict d'échantillon ------------------------------------------
    @property
    def echantillon_suffisant(self) -> bool:
        """100 trades : le seuil sous lequel un taux de réussite ne dit rien."""
        return self.trades >= 100

    @property
    def esperance_credible(self) -> bool:
        """L'espérance est-elle distinguable de zéro ?

        On exige que la borne basse de l'intervalle sur le taux de réussite
        reste au-dessus du seuil d'équilibre imposé par le ratio gain/perte.
        Sinon, le résultat est compatible avec un système qui ne gagne rien.
        """
        if self.trades < 30 or self.perte_moyenne_R == 0:
            return False
        ratio = abs(self.gain_moyen_R / self.perte_moyenne_R)
        seuil_equilibre = 1 / (1 + ratio)
        return self.taux_reussite_ic95[0] > seuil_equilibre


def calculer(trades: list[TradeFerme], *, capital_initial: float,
             courbe_equite: list[tuple[datetime, float]] | None = None) -> Metriques:
    """Toutes les métriques, à partir des trades fermés."""
    n = len(trades)
    if n == 0:
        return Metriques(0, 0, 0.0, (0.0, 1.0), 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0,
                         0.0, 0.0, capital_initial, capital_initial)

    gains = [t for t in trades if t.gagnant]
    pertes = [t for t in trades if not t.gagnant]
    g, p = len(gains), len(pertes)

    somme_gains = sum(t.resultat_devise for t in gains)
    somme_pertes = abs(sum(t.resultat_devise for t in pertes))
    net = somme_gains - somme_pertes
    couts = sum(t.cout_devise for t in trades)
    brut = net + couts

    # --- Courbe d'équité et drawdown ---------------------------------------
    if courbe_equite is None:
        equite, courbe_equite = capital_initial, []
        for t in sorted(trades, key=lambda x: x.sortie_le):
            equite += t.resultat_devise
            courbe_equite.append((t.sortie_le, equite))

    sommet, dd_max, dd_debut, dd_duree = capital_initial, 0.0, None, 0.0
    for quand, eq in courbe_equite:
        if eq > sommet:
            sommet, dd_debut = eq, None
        else:
            if dd_debut is None:
                dd_debut = quand
            creux = 100 * (sommet - eq) / sommet if sommet else 0.0
            if creux > dd_max:
                dd_max = creux
            if dd_debut:
                dd_duree = max(dd_duree, (quand - dd_debut).total_seconds() / 86400)

    # --- Séries -------------------------------------------------------------
    serie_p = serie_g = max_p = max_g = 0
    for t in sorted(trades, key=lambda x: x.sortie_le):
        if t.gagnant:
            serie_g, serie_p = serie_g + 1, 0
        else:
            serie_p, serie_g = serie_p + 1, 0
        max_g, max_p = max(max_g, serie_g), max(max_p, serie_p)

    # --- Sharpe / Sortino ---------------------------------------------------
    rendements = [t.resultat_devise / capital_initial for t in trades]
    debut = min(t.entree_le for t in trades)
    fin = max(t.sortie_le for t in trades)
    annees = max((fin - debut).days / 365.25, 1 / 365.25)
    par_an = n / annees

    sharpe = sortino = 0.0
    if n > 1:
        moy = statistics.fmean(rendements)
        ecart = statistics.stdev(rendements)
        if ecart > 0:
            sharpe = moy / ecart * math.sqrt(par_an)
        negatifs = [r for r in rendements if r < 0]
        if len(negatifs) > 1:
            ecart_bas = statistics.stdev(negatifs)
            if ecart_bas > 0:
                sortino = moy / ecart_bas * math.sqrt(par_an)

    capital_final = capital_initial + net
    rendement_annuel = ((capital_final / capital_initial) ** (1 / annees) - 1) * 100 \
        if capital_initial > 0 and capital_final > 0 else 0.0

    return Metriques(
        trades=n, gagnants=g,
        taux_reussite=g / n,
        taux_reussite_ic95=_wilson(g, n),
        esperance_R=statistics.fmean(t.resultat_R for t in trades),
        esperance_devise=net / n,
        profit_factor=(somme_gains / somme_pertes) if somme_pertes else float("inf"),
        gain_moyen_R=statistics.fmean([t.resultat_R for t in gains]) if g else 0.0,
        perte_moyenne_R=statistics.fmean([t.resultat_R for t in pertes]) if p else 0.0,
        resultat_net=net, resultat_brut=brut, couts_totaux=couts,
        couts_pct_du_brut=(100 * couts / abs(brut)) if brut else 0.0,
        drawdown_max_pct=dd_max, drawdown_max_duree_jours=dd_duree,
        serie_perdante_max=max_p, serie_gagnante_max=max_g,
        sharpe_annualise=sharpe, sortino_annualise=sortino,
        mar=(rendement_annuel / dd_max) if dd_max > 0 else 0.0,
        duree_moyenne_h=statistics.fmean(t.duree_heures for t in trades),
        trades_par_mois=par_an / 12,
        capital_initial=capital_initial, capital_final=capital_final,
    )


def rapport(m: Metriques, titre: str = "RÉSULTATS") -> str:
    """Le compte rendu, avec le verdict d'échantillon en premier.

    L'ordre est délibéré : on ne lit pas un taux de réussite avant de savoir
    s'il veut dire quelque chose.
    """
    bas, haut = m.taux_reussite_ic95
    sep = "=" * 68

    if m.trades == 0:
        return f"{sep}\n  {titre}\n{sep}\n  Aucun trade. Le système n'a jamais tiré.\n{sep}"

    if not m.echantillon_suffisant:
        verdict = (f"⚠  {m.trades} trades : ÉCHANTILLON INSUFFISANT.\n"
                   f"     En dessous de 100, rien ici ne permet de conclure.\n"
                   f"     Le taux de réussite réel est quelque part entre "
                   f"{bas:.0%} et {haut:.0%}.")
    elif not m.esperance_credible:
        verdict = (f"⚠  {m.trades} trades, mais l'espérance N'EST PAS distinguable de zéro.\n"
                   f"     Le taux de réussite tient entre {bas:.0%} et {haut:.0%} : cette\n"
                   f"     fourchette contient le seuil d'équilibre. Compatible avec « ça ne\n"
                   f"     gagne rien ».")
    else:
        verdict = (f"✓  {m.trades} trades, espérance positive et distinguable de zéro\n"
                   f"     (taux de réussite entre {bas:.0%} et {haut:.0%}).")

    return "\n".join([
        sep, f"  {titre}", sep,
        "  ÉCHANTILLON",
        "  " + verdict.replace("\n", "\n  "),
        "",
        "  ESPÉRANCE",
        f"    Par trade           {m.esperance_R:+.3f} R   "
        f"({m.esperance_devise:+.2f} par trade)",
        f"    Taux de réussite    {m.taux_reussite:.1%}   "
        f"[{bas:.1%} – {haut:.1%}] à 95 %",
        f"    Gain moyen          {m.gain_moyen_R:+.2f} R",
        f"    Perte moyenne       {m.perte_moyenne_R:+.2f} R",
        f"    Profit factor       {m.profit_factor:.2f}"
        + ("   (< 1 : le système perd)" if m.profit_factor < 1 else ""),
        "",
        "  ARGENT",
        f"    Capital             {m.capital_initial:,.2f}  ->  {m.capital_final:,.2f}".replace(",", " "),
        f"    Résultat net        {m.resultat_net:+,.2f}".replace(",", " "),
        f"    Résultat brut       {m.resultat_brut:+,.2f}".replace(",", " "),
        f"    COÛTS PAYÉS         {m.couts_totaux:,.2f}".replace(",", " ")
        + f"   =  {m.couts_pct_du_brut:.1f} % du brut"
        + ("   ⚠ les coûts mangent le système" if m.couts_pct_du_brut > 40 else ""),
        "",
        "  RISQUE",
        f"    Drawdown max        {m.drawdown_max_pct:.2f} %"
        + (f"   pendant {m.drawdown_max_duree_jours:.0f} jours"
           if m.drawdown_max_duree_jours else ""),
        f"    Série perdante max  {m.serie_perdante_max} trades   "
        f"(à vivre : c'est normal, pas une panne)",
        f"    Série gagnante max  {m.serie_gagnante_max} trades",
        f"    Sharpe annualisé    {m.sharpe_annualise:.2f}"
        + ("   (< 0,5 : trop faible pour risquer de l'argent)"
           if m.sharpe_annualise < 0.5 else ""),
        f"    Sortino annualisé   {m.sortino_annualise:.2f}",
        f"    MAR                 {m.mar:.2f}   (rendement annuel / drawdown max)",
        "",
        "  RYTHME",
        f"    Trades par mois     {m.trades_par_mois:.1f}",
        f"    Durée moyenne       {m.duree_moyenne_h:.1f} h",
        sep,
    ])
