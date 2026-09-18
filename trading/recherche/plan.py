# -*- coding: utf-8 -*-
"""
Le plan de Mongazi : **échelle de risque pilotée par le drawdown, et intérêts composés.**

    python -m trading.recherche.plan                    # sur les vrais trades de la stratégie
    python -m trading.recherche.plan --capital 500 --montecarlo

La règle, telle qu'elle est dessinée :
  · on risque **6 %** tant que le capital est à son sommet (les blocs verts) ;
  · dès qu'on passe sous le sommet, on descend à **4 %** (les blocs orange), puis à **3 %** si ça
    continue ; **on remonte à 6 % dès qu'un nouveau sommet est touché** ;
  · le capital risqué est un pourcentage du capital **du moment** : c'est là que les intérêts
    composés agissent.

Pourquoi l'échelle protège, en une ligne d'arithmétique (la 2ᵉ planche) : six pertes d'affilée à 6 %
coûtent 36 %, six de plus à 4 % amènent à 60 %, six de plus à 3 % à 78 %. **Dix-huit pertes
consécutives ne ruinent pas** — alors qu'à 6 % constant elles coûteraient 100 % du capital de départ.

⚠️ Ce fichier mesure le plan sur la **vraie séquence de trades** de notre stratégie (l'ordre exact,
les vrais gains et les vraies pertes), puis au Monte Carlo. Il ne recopie aucun chiffre d'une
planche : un tableau qui suppose 8 R par mois **tous les mois** n'est pas une prévision, c'est une
multiplication.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

import numpy as np

from .lancer import DOSSIER

SORTIE = DOSSIER / "plan"


@dataclass
class Echelle:
    """L'échelle de risque. `declencheur` : 'drawdown' (planche 1 et 3) ou 'pertes' (planche 2)."""
    risques_pct: tuple[float, ...] = (6.0, 4.0, 3.0)
    declencheur: str = "drawdown"
    seuils_drawdown: tuple[float, ...] = (0.10, 0.25)     # on descend d'un cran à -10 %, puis -25 %
    pertes_consecutives: tuple[int, ...] = (6, 12)        # ou : après 6 pertes d'affilée, puis 12
    arret_total_pct: float = 0.80                          # capital perdu à partir duquel on arrête
    nom: str = "6-4-3"

    def niveau(self, drawdown: float, pertes: int) -> int:
        seuils = self.seuils_drawdown if self.declencheur == "drawdown" else self.pertes_consecutives
        valeur = drawdown if self.declencheur == "drawdown" else pertes
        n = 0
        for s in seuils:
            if valeur >= s:
                n += 1
        return min(n, len(self.risques_pct) - 1)

    def risque(self, drawdown: float, pertes: int) -> float:
        """Le risque à appliquer. En mode « drawdown », **c'est le code de l'agent qui décide**
        (`noyau/profils.risque_du_drawdown`) : une règle qui n'existerait qu'ici ferait diverger la
        mesure et le compte. Le mode « pertes » n'existe que pour la comparaison."""
        if self.declencheur == "drawdown":
            from ..noyau.profils import risque_du_drawdown
            paliers = tuple(zip((0.0,) + tuple(self.seuils_drawdown), self.risques_pct))
            return risque_du_drawdown(paliers, self.risques_pct[0], drawdown)[0]
        return self.risques_pct[self.niveau(drawdown, pertes)]


@dataclass
class Resultat:
    capital_final: float
    multiple: float
    drawdown_max_pct: float
    trades: int
    ruine: bool
    equity: np.ndarray = field(repr=False)
    risques: np.ndarray = field(repr=False)
    niveaux_temps: dict = field(default_factory=dict)


def appliquer(R: np.ndarray, *, capital: float = 500.0, echelle: Echelle | None = None,
              risque_fixe: float | None = None, plafond_perte_R: float = -3.0) -> Resultat:
    """Dérouler la vraie séquence de trades avec l'échelle et les intérêts composés.

    `risque_fixe` : pour comparer avec un risque constant (c'est le témoin du plan).
    `plafond_perte_R` : une perte ne dépasse jamais ce multiple du risque (un gap peut faire pire
    qu'un stop ; sans borne, un seul trade pourrait dépasser 100 % du capital risqué).
    """
    echelle = echelle or Echelle()
    equity = np.empty(len(R) + 1)
    equity[0] = capital
    risques = np.empty(len(R))
    sommet = capital
    pertes = 0
    temps_par_niveau = {i: 0 for i in range(len(echelle.risques_pct))}
    ruine = False
    for k, r in enumerate(R):
        c = equity[k]
        if ruine or c <= capital * (1 - echelle.arret_total_pct):
            ruine = True
            equity[k + 1:] = c
            risques[k:] = 0.0
            break
        drawdown = 1.0 - c / sommet
        niveau = 0 if risque_fixe is not None else echelle.niveau(drawdown, pertes)
        risque = risque_fixe if risque_fixe is not None else echelle.risque(drawdown, pertes)
        risques[k] = risque
        temps_par_niveau[niveau] = temps_par_niveau.get(niveau, 0) + 1
        gain = max(float(r), plafond_perte_R) * (risque / 100.0) * c
        equity[k + 1] = max(c + gain, 0.0)
        sommet = max(sommet, equity[k + 1])
        pertes = 0 if r > 0 else pertes + 1
    pics = np.maximum.accumulate(equity)
    dd = float((1.0 - equity / pics).max() * 100)
    return Resultat(capital_final=float(equity[-1]), multiple=float(equity[-1] / capital),
                    drawdown_max_pct=dd, trades=int(len(R)), ruine=ruine, equity=equity,
                    risques=risques, niveaux_temps=temps_par_niveau)


def monte_carlo(R: np.ndarray, *, capital: float = 500.0, echelle: Echelle | None = None,
                risque_fixe: float | None = None, horizon: int = 250, tirages: int = 5000,
                facteur_avantage: float = 1.0, graine: int = 11) -> dict:
    """Rejouer le plan sur des séquences tirées au hasard dans la distribution observée.

    `facteur_avantage` : 1 = l'avantage mesuré, 0,5 = il tombe de moitié, 0 = plus d'avantage du
    tout. **C'est la question qui compte** : un plan de risque ne se juge pas sur le cas où tout va
    bien, il se juge sur le cas où l'avantage s'use.
    """
    rng = np.random.default_rng(graine)
    Rb = R - (1 - facteur_avantage) * R.mean()
    finals, dds, ruines = np.empty(tirages), np.empty(tirages), 0
    for i in range(tirages):
        serie = rng.choice(Rb, size=horizon, replace=True)
        res = appliquer(serie, capital=capital, echelle=echelle, risque_fixe=risque_fixe)
        finals[i] = res.capital_final
        dds[i] = res.drawdown_max_pct
        ruines += res.ruine
    return {"horizon_trades": horizon, "tirages": tirages, "facteur_avantage": facteur_avantage,
            "capital_median": float(np.median(finals)),
            "capital_p10": float(np.quantile(finals, 0.10)),
            "capital_p90": float(np.quantile(finals, 0.90)),
            "multiple_median": float(np.median(finals) / capital),
            "drawdown_median_pct": float(np.median(dds)),
            "drawdown_p90_pct": float(np.quantile(dds, 0.90)),
            "p_ruine": ruines / tirages,
            "p_perdre_moitie": float((finals < capital * 0.5).mean()),
            "p_doubler": float((finals > capital * 2).mean())}


def trades_strategie(marche: str = "NAS100", part: float = 0.05):
    """La vraie séquence de trades de la stratégie retenue, dans l'ordre du temps."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from . import banc, meta_candidat as mc
    if marche.upper() == "NAS100":
        s_app = banc.charger("NAS100", "M1", source="duka").tranche("2013-01-01", "2020-01-01")
        s_test = banc.charger("NAS100", "M1", source="duka").tranche("2020-01-01", "2024-01-01")
    else:
        s_app = banc.charger("EURUSD", "M1")
        s_test = banc.charger("EURUSD", "M1", source="duka").tranche("2003-05-05", "2012-01-01")
    a = mc.trades_et_caracteristiques(s_app)
    b = mc.trades_et_caracteristiques(s_test)
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=31,
                                       min_samples_leaf=100, l2_regularization=1.0,
                                       early_stopping=True, validation_fraction=0.15, random_state=5)
    m.fit(a["X"][a["i_signal"][a["ok"]]], a["objectif"][a["ok"]].astype(np.int8))
    p = m.predict_proba(b["X"][b["i_signal"][b["ok"]]])[:, 1]
    garde = p >= np.quantile(p, 1 - part)
    R = b["trades"].R[b["ok"]][garde]
    temps = s_test.temps[b["trades"].entree[b["ok"]]][garde]
    return R, temps


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--capital", type=float, default=500.0)
    ap.add_argument("--marche", default="NAS100")
    ap.add_argument("--part", type=float, default=0.05)
    ap.add_argument("--montecarlo", action="store_true")
    a = ap.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    R, temps = trades_strategie(a.marche, a.part)
    mois = (temps[-1] - temps[0]).astype("timedelta64[s]").astype(float) / (86400 * 30.44)
    print(f"\n  {a.marche} · {len(R)} trades sur {mois:.0f} mois · espérance {R.mean():+.3f} R · "
          f"{len(R) / mois:.1f} trades/mois · **{R.sum() / mois:.1f} R par mois**")
    print(f"  (la planche suppose 8 R par mois ; ici la mesure en donne {R.sum() / mois:.1f})\n")

    variantes = [("échelle 6-4-3 sur le drawdown", Echelle(declencheur="drawdown"), None),
                 ("échelle 6-4-3 sur les pertes d'affilée", Echelle(declencheur="pertes"), None),
                 ("risque fixe 6 % (témoin)", None, 6.0),
                 ("risque fixe 2 %", None, 2.0),
                 ("risque fixe 1 %", None, 1.0)]
    lignes = []
    print(f"  {'plan':42s} {'capital final':>16s} {'multiple':>12s} {'pire recul':>11s}")
    for nom, ech, fixe in variantes:
        res = appliquer(R, capital=a.capital, echelle=ech, risque_fixe=fixe)
        lignes.append({"plan": nom, "capital_final": res.capital_final, "multiple": res.multiple,
                       "drawdown_max_pct": res.drawdown_max_pct, "ruine": res.ruine})
        print(f"  {nom:42s} {res.capital_final:16,.0f} $ {res.multiple:11,.1f}x "
              f"{res.drawdown_max_pct:10.1f} %".replace(",", " "))

    if a.montecarlo:
        print(f"\n  MONTE CARLO · 250 trades (environ 8 mois), capital {a.capital:.0f} $\n")
        print(f"  {'plan':30s} {'avantage':>9s} {'capital médian':>16s} {'pire recul médian':>18s} "
              f"{'P(perdre la moitié)':>20s} {'P(ruine)':>9s}")
        mc_lignes = []
        for nom, ech, fixe in variantes[:1] + variantes[2:4]:
            for facteur in (1.0, 0.5, 0.0):
                d = monte_carlo(R, capital=a.capital, echelle=ech, risque_fixe=fixe,
                                facteur_avantage=facteur)
                mc_lignes.append({"plan": nom, **d})
                print(f"  {nom[:30]:30s} {facteur:8.0%} {d['capital_median']:16,.0f} $ "
                      f"{d['drawdown_median_pct']:17.1f} % {100 * d['p_perdre_moitie']:19.1f} % "
                      f"{100 * d['p_ruine']:8.1f} %".replace(",", " "))
        lignes.append({"montecarlo": mc_lignes})
    (SORTIE / f"plan_{a.marche}.json").write_text(json.dumps(lignes, ensure_ascii=False, default=str),
                                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
