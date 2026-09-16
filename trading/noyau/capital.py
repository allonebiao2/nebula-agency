# -*- coding: utf-8 -*-
"""
Trader avec n'importe quel capital, sans jamais dépasser le risque.

Le problème, mesuré : sur un compte STANDARD, le lot minimum (0,01) d'EUR/USD
vaut 1 $ par pip. Un stop H4 de 70 pips risque donc 7 $ au minimum. À 1 %, il
faut 700 $ ; en dessous, un robot honnête refuse tout, et un robot malhonnête
dépasse en silence.

Trois réponses, appliquées automatiquement, dans cet ordre :

  1. LE COMPTE CENT. Le solde est tenu en cents (USC, EUC) et le lot est 100
     fois plus petit en valeur. Rien à coder pour le dimensionnement : le solde
     et la valeur du point sont dans la même unité, le calcul reste exact. Il
     faut seulement CONVERTIR pour l'affichage et pour `capital_max_engage`,
     écrit en vraie monnaie. Avec 10 $ (1 000 USC), 0,01 lot sur 70 pips
     risque 7 USC = 0,7 %.
  2. LE LOT MINIMUM TOLÉRÉ JUSQU'AU PLAFOND (`risque_max_petit_compte_pct`,
     2 % au plus, plafond écrit dans le code). Chaque trade concerné le dit.
  3. L'ATTENTE. Au-delà, CE trade est refusé et le bot attend un signal dont
     le stop tient dans le capital. Les stops suivent la volatilité : dans un
     marché calme, ils rétrécissent, et les signaux redeviennent accessibles.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEVISES_CENT = {"USC": "USD", "EUC": "EUR", "GBC": "GBP", "USX": "USD", "CENT": "USD"}


@dataclass(frozen=True)
class TypeCompte:
    devise_compte: str        # telle que le courtier l'écrit (USC)
    devise_reelle: str        # USD
    facteur: float            # unités du compte par unité réelle (100 pour un compte cent)

    @property
    def cent(self) -> bool:
        return self.facteur != 1.0

    def en_reel(self, montant_compte: float) -> float:
        return montant_compte / self.facteur

    def en_compte(self, montant_reel: float) -> float:
        return montant_reel * self.facteur

    def libelle(self) -> str:
        return (f"compte cent ({self.devise_compte}, 1 {self.devise_reelle} = "
                f"{self.facteur:g} {self.devise_compte})" if self.cent
                else f"compte standard ({self.devise_compte})")


def detecter(devise: str, serveur: str = "", symbole: str = "") -> TypeCompte:
    """Reconnaît un compte cent à sa devise, puis à son serveur ou son symbole."""
    d = (devise or "").upper()
    if d in DEVISES_CENT:
        return TypeCompte(d, DEVISES_CENT[d], 100.0)
    indices = f"{serveur} {symbole}".lower()
    if "cent" in indices:
        return TypeCompte(d, d, 100.0)
    return TypeCompte(d or "USD", d or "USD", 1.0)


def capital_de_travail(solde_compte: float, capital_max_engage_reel: float,
                       type_compte: TypeCompte) -> float:
    """Le capital sur lequel on dimensionne, dans l'UNITÉ DU COMPTE.

    `capital_max_engage` est écrit par l'utilisateur en vraie monnaie : sur un
    compte cent il faut le multiplier, sinon un plafond de 50 $ deviendrait un
    plafond de 50 cents et bloquerait tout.
    """
    if capital_max_engage_reel <= 0:
        return solde_compte
    return min(solde_compte, type_compte.en_compte(capital_max_engage_reel))


def viabilite(*, points_de_stop: np.ndarray, valeur_point_lot_min: float,
              capitaux: list[float], risque_pct: float, plafond_pct: float,
              facteur: float = 1.0) -> list[dict]:
    """Pour chaque capital (en vraie monnaie) : quelle part des signaux passe ?

    `points_de_stop` = la distribution RÉELLE des stops (2×ATR mesurés sur
    l'historique). `valeur_point_lot_min` = ce que rapporte 1 point au lot
    minimum, dans l'unité du compte.
    """
    stops = np.asarray(points_de_stop, dtype=float)
    stops = stops[np.isfinite(stops) & (stops > 0)]
    lignes = []
    for cap in capitaux:
        cap_compte = cap * facteur
        risque_min = stops * valeur_point_lot_min
        pct = 100 * risque_min / cap_compte
        exact = float(np.mean(pct <= risque_pct)) if len(stops) else 0.0
        tolere = float(np.mean(pct <= plafond_pct)) if len(stops) else 0.0
        lignes.append({
            "capital": cap, "a_1pct": exact, "au_plafond": tolere,
            "stop_median_points": float(np.median(stops)) if len(stops) else 0.0,
            "risque_median_pct": float(np.median(pct)) if len(stops) else 0.0,
        })
    return lignes
