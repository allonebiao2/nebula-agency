# -*- coding: utf-8 -*-
"""
Dimensionnement de position.

« Position sizing calculé avant l'entrée : nombre de lots dérivé du stop-loss,
pas de l'instinct. »

Ce module ne connaît rien à la stratégie. Il répond à une seule question :
étant donné un capital, un risque autorisé en %, et une distance de stop en
points, combien de lots ?

Trois détails valent de l'argent et sont souvent ratés :

  1. ON ARRONDIT VERS LE BAS, jamais vers le haut. Arrondir 0,037 lot à
     0,04 dépasse le risque autorisé — de peu, à chaque trade, dans le même
     sens. C'est une fuite lente et systématique.

  2. SI LE LOT MINIMUM RISQUE PLUS QUE L'AUTORISÉ, ON REFUSE LE TRADE.
     C'est le vrai test de viabilité d'un petit compte, et personne ne le fait :
     on préfère « juste cette fois » et le compte meurt en trois semaines.

  3. LA VALEUR DU POINT SE LIT CHEZ LE COURTIER, jamais en dur. Elle dépend du
     contrat, de la devise du compte et du symbole exact.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SpecsSymbole:
    """Ce que le courtier dit du symbole. Lu via MT5, jamais supposé."""
    nom: str
    point: float             # plus petit incrément de prix (0.00001 sur EURUSD 5 chiffres)
    digits: int
    volume_min: float        # plus petit lot négociable (souvent 0.01)
    volume_max: float
    volume_step: float       # granularité du lot
    valeur_tick: float       # valeur d'un tick pour 1 lot, dans la devise du compte
    taille_tick: float       # taille d'un tick en prix
    taille_contrat: float
    stops_level_points: int = 0   # distance minimale imposée entre le prix et le stop

    @property
    def valeur_point_par_lot(self) -> float:
        """Combien vaut 1 point de mouvement, pour 1 lot, dans la devise du compte."""
        if self.taille_tick <= 0:
            raise ValueError(f"{self.nom} : taille_tick invalide ({self.taille_tick})")
        return self.valeur_tick * (self.point / self.taille_tick)

    @property
    def pip(self) -> float:
        """Un pip = 10 points sur un symbole à 3 ou 5 décimales, sinon 1 point."""
        return self.point * (10 if self.digits in (3, 5) else 1)


@dataclass(frozen=True)
class Dimensionnement:
    lots: float
    risque_devise: float
    risque_pct: float
    points_de_risque: float
    valeur_point_par_lot: float
    autorise: bool
    raison: str = ""
    note: str = ""               # ex. « lot minimum, risque relevé à 1,4 % »
    capital_requis: float = 0.0  # si refusé faute de capital : ce qu'il faudrait

    @property
    def petit_compte(self) -> bool:
        """Vrai si le trade n'a été possible qu'en relevant le risque vers le plafond."""
        return bool(self.note)

    def __str__(self) -> str:
        if not self.autorise:
            return f"REFUSÉ — {self.raison}"
        return (f"{self.lots:g} lot(s)  ·  risque {self.risque_devise:.2f} "
                f"({self.risque_pct:.2f} %)  ·  stop {self.points_de_risque:.0f} points"
                + (f"  ·  {self.note}" if self.note else ""))


def _arrondir_vers_le_bas(valeur: float, pas: float) -> float:
    """Arrondit au pas inférieur. Jamais au supérieur : voir l'en-tête, détail 1."""
    if pas <= 0:
        return valeur
    # On repasse par les entiers pour éviter que 0.1 + 0.2 ne fasse des siennes.
    decimales = max(0, -math.floor(math.log10(pas)) + 2)
    crans = math.floor(round(valeur / pas, 6))
    return round(crans * pas, decimales)


def dimensionner(
    *,
    capital: float,
    risque_pct: float,
    points_de_risque: float,
    specs: SpecsSymbole,
    lots_total_max: float,
    lots_deja_ouverts: float = 0.0,
    perte_max_par_position_pct: float | None = None,
    risque_pct_plafond: float | None = None,
) -> Dimensionnement:
    """Combien de lots, pour risquer exactement `risque_pct` % et pas un cent de plus.

    Renvoie toujours un Dimensionnement : s'il n'est pas `autorise`, la raison
    est écrite en clair et destinée au journal.

    LA POLITIQUE DU PETIT COMPTE (`risque_pct_plafond`). Quand le lot minimum
    risque plus que `risque_pct` mais pas plus que le plafond, on prend le lot
    minimum et on le DIT (champ `note`). Au-delà du plafond, on refuse CE trade
    seulement : le bot attend un signal dont le stop tient dans le capital. Il
    ne plante pas, il ne dépasse pas, il ne « se rattrape » pas.
    """
    vide = dict(lots=0.0, risque_devise=0.0, risque_pct=0.0,
                points_de_risque=points_de_risque,
                valeur_point_par_lot=0.0, autorise=False)

    if capital <= 0:
        return Dimensionnement(**vide, raison="capital nul ou négatif")
    if points_de_risque <= 0:
        return Dimensionnement(
            **vide, raison="distance de stop nulle : une position sans invalidation "
                           "n'a pas d'espérance définie")

    if specs.stops_level_points and points_de_risque < specs.stops_level_points:
        return Dimensionnement(
            **vide,
            raison=(f"stop à {points_de_risque:.0f} points alors que le courtier en impose "
                    f"{specs.stops_level_points} au minimum : l'ordre serait rejeté"))

    vpl = specs.valeur_point_par_lot
    if vpl <= 0:
        return Dimensionnement(**vide, raison=f"valeur du point illisible pour {specs.nom}")

    risque_vise = capital * risque_pct / 100.0
    lots_bruts = risque_vise / (points_de_risque * vpl)
    lots = _arrondir_vers_le_bas(lots_bruts, specs.volume_step)

    # --- Le compte est-il assez gros pour ce stop ? -------------------------
    note = ""
    if lots < specs.volume_min:
        risque_au_min = specs.volume_min * points_de_risque * vpl
        pct_au_min = 100 * risque_au_min / capital
        plafond = max(risque_pct, risque_pct_plafond or risque_pct)
        if pct_au_min <= plafond + 1e-9:
            lots = specs.volume_min
            note = (f"petit compte : lot minimum, risque relevé à {pct_au_min:.2f} % "
                    f"(plafond {plafond:g} %)")
        else:
            capital_requis = risque_au_min * 100 / plafond
            return Dimensionnement(
                **{**vide, "valeur_point_par_lot": vpl},
                capital_requis=capital_requis,
                raison=(
                    f"capital insuffisant pour CE stop : le lot minimum "
                    f"({specs.volume_min:g}) risquerait {risque_au_min:.2f} = "
                    f"{pct_au_min:.2f} % du capital, au-delà du plafond de {plafond:g} %.\n"
                    f"    Il faudrait ~{capital_requis:.0f} pour ce stop de "
                    f"{points_de_risque:.0f} points. Le bot attend un signal au stop plus "
                    f"court, ou un compte cent (lot 100 fois plus petit).\n"
                    f"    On ne contourne pas : dépasser « juste cette fois » est la façon "
                    f"n°1 dont un petit compte meurt."))

    # --- Plafonds d'exposition ---------------------------------------------
    place_restante = lots_total_max - lots_deja_ouverts
    if place_restante < specs.volume_min:
        return Dimensionnement(
            **{**vide, "valeur_point_par_lot": vpl},
            raison=(f"plafond d'exposition atteint : {lots_deja_ouverts:g} lot(s) déjà "
                    f"ouverts sur un maximum de {lots_total_max:g}"))
    if lots > place_restante:
        lots = _arrondir_vers_le_bas(place_restante, specs.volume_step)

    lots = min(lots, specs.volume_max)

    risque_reel = lots * points_de_risque * vpl
    pct_reel = 100 * risque_reel / capital

    # --- Filet contre un bug de calcul --------------------------------------
    if perte_max_par_position_pct is not None and pct_reel > perte_max_par_position_pct:
        return Dimensionnement(
            **{**vide, "valeur_point_par_lot": vpl},
            raison=(f"taille calculée à {lots:g} lot(s) = {pct_reel:.2f} % du capital, "
                    f"au-delà du filet de sécurité ({perte_max_par_position_pct} %). "
                    f"Anomalie de calcul : l'ordre est bloqué."))

    return Dimensionnement(
        lots=lots,
        risque_devise=risque_reel,
        risque_pct=pct_reel,
        points_de_risque=points_de_risque,
        valeur_point_par_lot=vpl,
        autorise=True,
        note=note,
    )


# =============================================================================
#  L'invariant du stop
# =============================================================================

def deplacement_de_stop_autorise(*, sens: str, stop_actuel: float,
                                 stop_propose: float) -> tuple[bool, str]:
    """Un stop ne se déplace QUE dans la direction du profit.

    « Ne jamais déplacer son stop » est une formule fausse : c'est « ne jamais
    l'ÉLARGIR ». Le resserrer est le mécanisme même du suiveur.

    Cette fonction est appelée pour TOUTE modification de stop, y compris celles
    que le bot se propose à lui-même. Un module qui tenterait d'élargir se ferait
    refuser comme n'importe qui.
    """
    if sens == "achat":
        # En achat, le stop est sous le prix : le resserrer, c'est le MONTER.
        if stop_propose < stop_actuel:
            return False, (f"élargissement refusé : stop {stop_actuel} -> {stop_propose} "
                           f"en achat éloigne l'invalidation et augmente le risque.")
    elif sens == "vente":
        if stop_propose > stop_actuel:
            return False, (f"élargissement refusé : stop {stop_actuel} -> {stop_propose} "
                           f"en vente éloigne l'invalidation et augmente le risque.")
    else:
        return False, f"sens inconnu : {sens!r}"
    return True, ""


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Spécifications typiques d'un EURUSD 5 décimales, compte en USD.
    # Elles seront LUES chez Deriv dès la première connexion.
    eurusd = SpecsSymbole(
        nom="EURUSD", point=0.00001, digits=5,
        volume_min=0.01, volume_max=100.0, volume_step=0.01,
        valeur_tick=1.0, taille_tick=0.00001, taille_contrat=100_000,
    )
    print(f"EURUSD : 1 point = {eurusd.valeur_point_par_lot} USD par lot · "
          f"1 pip = {eurusd.pip}\n")

    stop_points = 700          # 70 pips, ordre de grandeur d'un 2xATR en H4
    print(f"Stop de {stop_points} points (70 pips), risque 1 % :\n")
    for capital in (50, 100, 500, 1_000, 5_000, 20_000):
        d = dimensionner(capital=capital, risque_pct=1.0,
                         points_de_risque=stop_points, specs=eurusd,
                         lots_total_max=0.50, perte_max_par_position_pct=3.0)
        etat = "OK " if d.autorise else "NON"
        tete = d.raison.split("\n")[0] if not d.autorise else str(d)
        print(f"  [{etat}] capital {capital:>6} USD  ->  {tete}")

    print("\nInvariant du stop (achat ouvert à 1.0850, stop à 1.0780) :")
    for propose, quoi in ((1.0800, "resserré vers le profit"),
                          (1.0750, "élargi « en espérant que ça revienne »")):
        ok, raison = deplacement_de_stop_autorise(
            sens="achat", stop_actuel=1.0780, stop_propose=propose)
        print(f"  {propose}  ({quoi})")
        print(f"     -> {'ACCEPTÉ' if ok else 'REFUSÉ'}{'' if ok else '  ' + raison}")
