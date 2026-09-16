# -*- coding: utf-8 -*-
"""
Adaptateur courtier : tout ce qui varie d'un MT5 à l'autre se LIT ici.

Le bot doit tourner chez n'importe quel courtier MT5 — c'est une exigence
produit, pas un confort. Douze choses changent d'un courtier à l'autre, et
chacune casse un bot qui les suppose :

   1. le nom du symbole      EURUSD / EURUSD.a / EURUSDm / EURUSDc / EURUSD_raw
   2. le fuseau du serveur   GMT, GMT+2, GMT+3, heure d'été gérée autrement
   3. les décimales          4 ou 5 -> la valeur d'un point change d'un facteur 10
   4. la taille du contrat   100 000, ou 1 000 sur un compte cent -> facteur 100
   5. le lot minimum et le pas
   6. le mode de remplissage FOK / IOC / RETURN
   7. le stops level         distance minimale imposée entre le prix et le stop
   8. couverture ou compensation (hedging / netting)
   9. la devise du compte
  10. commission ou spread inclus
  11. les swaps, et les comptes sans swap
  12. les heures de séance et le rollover

    python trading/noyau/courtier.py        # imprime le profil du courtier

RÈGLE : aucune de ces valeurs n'est écrite en dur, nulle part. Si une valeur ne
peut pas être lue, on s'arrête et on le dit — on ne devine pas.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

try:
    import MetaTrader5 as mt5
except ImportError:                                            # pragma: no cover
    mt5 = None

from .instruments import ALIAS, candidats_symbole  # noqa: F401  (réexportés)
from .risque import SpecsSymbole

# Drapeaux de symbole MQL5, absents du paquet Python (voir mode_remplissage).
_SYMBOL_FILLING_FOK = 1
_SYMBOL_FILLING_IOC = 2


class CourtierIndisponible(Exception):
    """Impossible de parler au terminal, ou le terminal ne sait pas répondre."""


# Variantes de nommage rencontrées chez les courtiers MT5. L'ordre n'a pas
# d'importance : on cherche, on mesure, et on tranche sur le spread.
_SUFFIXES = ("", ".a", ".b", ".c", ".e", ".i", ".m", ".p", ".pro", ".raw", ".ecn",
             ".stp", ".std", ".sb", "m", "c", "i", "e", "z", "_raw", "_ecn", "-5",
             ".cash", ".spot", "..", "#", "+")


@dataclass(frozen=True)
class ProfilCourtier:
    """La carte d'identité du courtier, mesurée et non supposée."""
    societe: str
    serveur: str
    login: int
    devise: str
    levier: int
    solde: float
    equite: float
    demo: bool
    couverture: bool              # True = hedging, False = netting
    trading_autorise: bool
    algo_autorise: bool
    decalage_serveur_h: float | None   # heure serveur - UTC, MESURÉE
    terminal: str = ""
    build: int = 0

    def __str__(self) -> str:
        dec = (f"UTC{self.decalage_serveur_h:+g}" if self.decalage_serveur_h is not None
               else "non mesuré (marché fermé ?)")
        return (f"{self.societe} · {self.serveur} · compte {self.login} "
                f"({'DÉMO' if self.demo else 'RÉEL'}) · {self.devise} · levier 1:{self.levier} "
                f"· {'couverture' if self.couverture else 'compensation'} · serveur {dec}")


@dataclass(frozen=True)
class CoutsSymbole:
    """Ce que le courtier prend réellement. Mesuré, pas annoncé."""
    spread_courant_points: float
    spread_median_points: float | None
    spread_max_observe_points: float | None
    swap_long: float
    swap_short: float
    swap_mode: int
    commission_annoncee: float | None = None   # MT5 ne l'expose pas toujours

    @property
    def spread_fiable(self) -> float:
        """Le spread à retenir pour le backtest : le médian si on l'a, sinon l'instantané."""
        return self.spread_median_points if self.spread_median_points else self.spread_courant_points


@dataclass
class Courtier:
    """Une session MT5. Ouvre, mesure, et referme proprement."""
    chemin_terminal: str | None = None
    login: int | None = None
    motdepasse: str | None = None
    serveur: str | None = None
    _ouvert: bool = field(default=False, init=False, repr=False)

    @classmethod
    def depuis_profil(cls, profil: str = "defaut") -> "Courtier":
        """Construit une session à partir de `secrets/mt5.env`.

        C'est la voie normale : un bot qui doit tourner chez n'importe quel
        courtier nomme son compte et son serveur au lieu d'espérer que le
        terminal ait mémorisé les bons.
        """
        from .identifiants import charger
        ids = charger(profil)
        return cls(chemin_terminal=ids.terminal, login=ids.login,
                   motdepasse=ids.motdepasse, serveur=ids.serveur)

    # --- Cycle de vie -------------------------------------------------------
    def __enter__(self) -> "Courtier":
        self.connecter()
        return self

    def __exit__(self, *_) -> None:
        self.fermer()

    def connecter(self) -> ProfilCourtier:
        if mt5 is None:
            raise CourtierIndisponible(
                "Le paquet MetaTrader5 n'est pas installé (pip install MetaTrader5). "
                "Il n'existe que pour Windows.")

        kwargs = {}
        if self.chemin_terminal:
            kwargs["path"] = self.chemin_terminal
        if self.login:
            kwargs.update(login=int(self.login), password=self.motdepasse,
                          server=self.serveur)

        if not mt5.initialize(timeout=120_000, **kwargs):
            code, message = mt5.last_error()
            # Deuxième chance : attacher d'abord, se connecter ensuite. Certains
            # terminaux refusent l'authentification pendant le démarrage mais
            # l'acceptent une fois la session établie.
            rattrape = False
            if self.login and mt5.initialize(timeout=120_000,
                                             **({"path": self.chemin_terminal}
                                                if self.chemin_terminal else {})):
                rattrape = mt5.login(int(self.login), password=self.motdepasse,
                                     server=self.serveur)
                if not rattrape:
                    code, message = mt5.last_error()
                    mt5.shutdown()
            if not rattrape:
                raise CourtierIndisponible(
                    _expliquer_erreur(code, message, self.chemin_terminal))

        self._ouvert = True
        if mt5.account_info() is None:
            self.fermer()
            raise CourtierIndisponible(
                "Terminal ouvert, mais aucun compte connecté.\n"
                "  Ouvre MT5, connecte-toi une fois (Fichier > Se connecter à un compte),\n"
                "  coche « Enregistrer les données du compte », puis relance.")
        return self.profil()

    def fermer(self) -> None:
        if self._ouvert and mt5 is not None:
            mt5.shutdown()
            self._ouvert = False

    # --- Identité -----------------------------------------------------------
    def profil(self) -> ProfilCourtier:
        a, t = mt5.account_info(), mt5.terminal_info()
        if a is None:
            raise CourtierIndisponible("account_info() indisponible.")
        return ProfilCourtier(
            societe=a.company, serveur=a.server, login=a.login, devise=a.currency,
            levier=a.leverage, solde=a.balance, equite=a.equity,
            demo=(a.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO),
            couverture=(a.margin_mode == mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING),
            # Le COMPTE dit s'il accepte des ordres et s'il accepte ceux d'un
            # robot ; le TERMINAL dit si le bouton « Trading Algo » est enfoncé
            # et si l'API n'est pas coupée. Il faut les trois pour trader.
            trading_autorise=bool(a.trade_allowed),
            algo_autorise=(bool(a.trade_expert) and bool(t.trade_allowed)
                           and not t.tradeapi_disabled) if t else False,
            decalage_serveur_h=self.decalage_serveur(),
            terminal=t.name if t else "", build=t.build if t else 0,
        )

    # --- Le piège n°2 : le fuseau du serveur -------------------------------
    def decalage_serveur(self, symbole: str | None = None) -> float | None:
        """Mesure « heure du serveur moins UTC », en heures.

        Aucun courtier ne publie cette valeur de façon fiable, et elle change
        avec l'heure d'été — chez certains, pas chez d'autres. On la MESURE en
        comparant l'horodatage du dernier tick (exprimé en heure serveur) à
        l'heure UTC réelle.

        Renvoie None si le marché est fermé : dans ce cas le dernier tick date,
        et la mesure serait fausse. Mieux vaut ne rien savoir que croire savoir.
        """
        symbole = symbole or self.trouver_symbole("EURUSD", silencieux=True)
        if not symbole:
            return None
        tick = mt5.symbol_info_tick(symbole)
        if not tick or not tick.time:
            return None

        maintenant_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        heure_serveur = datetime.fromtimestamp(tick.time, tz=timezone.utc).replace(tzinfo=None)
        ecart_h = (heure_serveur - maintenant_utc).total_seconds() / 3600.0

        # Un tick vieux de plus de 5 minutes = marché fermé, mesure non fiable.
        if abs(ecart_h - round(ecart_h * 2) / 2) > 0.1:
            return None
        return round(ecart_h * 2) / 2      # les fuseaux vont par demi-heures

    # --- Le piège n°1 : le nom du symbole ----------------------------------
    def trouver_symbole(self, base: str = "EURUSD", *, silencieux: bool = False) -> str | None:
        """Retrouve le vrai nom du symbole chez CE courtier.

        S'il existe plusieurs variantes (compte standard et compte raw exposés
        dans le même terminal), on garde celle au spread le plus serré — c'est
        celle qui coûte le moins cher à trader.
        """
        tous = mt5.symbols_get()
        if not tous:
            if not silencieux:
                raise CourtierIndisponible("Le terminal ne renvoie aucun symbole.")
            return None

        noms = {s.name for s in tous}
        base_u = base.upper()

        candidats = candidats_symbole(base, noms)
        if not candidats:
            candidats = [n for n in noms
                         if n.upper().startswith(base_u) and len(n) <= len(base) + 6]
        if not candidats:
            # Dernier recours : les deux devises, dans l'ordre, quelque part.
            a, b = base_u[:3], base_u[3:6]
            candidats = [n for n in noms
                         if a in n.upper() and b in n.upper()
                         and n.upper().index(a) < n.upper().index(b)]
        if not candidats:
            if not silencieux:
                raise CourtierIndisponible(
                    f"Aucun symbole ressemblant à {base} chez ce courtier.\n"
                    f"  Vérifie l'Observation du marché (Ctrl+M) et affiche tous les symboles.")
            return None

        # On départage au spread réel, une fois les candidats rendus visibles.
        meilleur, meilleur_spread = None, float("inf")
        for nom in candidats:
            info = mt5.symbol_info(nom)
            if info is None:
                continue
            if not info.visible:
                mt5.symbol_select(nom, True)
                info = mt5.symbol_info(nom)
            if info is None or not info.point:
                continue
            spread = info.spread if info.spread else (info.ask - info.bid) / info.point
            if 0 < spread < meilleur_spread:
                meilleur, meilleur_spread = nom, spread
        return meilleur or candidats[0]

    # --- Les spécifications du contrat -------------------------------------
    def specs(self, symbole: str) -> SpecsSymbole:
        info = mt5.symbol_info(symbole)
        if info is None:
            raise CourtierIndisponible(f"Symbole inconnu : {symbole}")
        if not info.visible:
            mt5.symbol_select(symbole, True)
            info = mt5.symbol_info(symbole)

        manquants = [n for n, v in (("point", info.point),
                                    ("trade_tick_value", info.trade_tick_value),
                                    ("trade_tick_size", info.trade_tick_size),
                                    ("volume_min", info.volume_min)) if not v]
        if manquants:
            raise CourtierIndisponible(
                f"{symbole} : le courtier ne renseigne pas {', '.join(manquants)}.\n"
                f"  Sans ces valeurs le dimensionnement serait une supposition. On s'arrête.")

        return SpecsSymbole(
            nom=info.name, point=info.point, digits=info.digits,
            volume_min=info.volume_min, volume_max=info.volume_max,
            volume_step=info.volume_step,
            valeur_tick=info.trade_tick_value, taille_tick=info.trade_tick_size,
            taille_contrat=info.trade_contract_size,
            stops_level_points=info.trade_stops_level,
        )

    # --- Les coûts réels ----------------------------------------------------
    def couts(self, symbole: str, *, echantillon_barres: int = 500) -> CoutsSymbole:
        """Le spread MÉDIAN, pas celui de la vitrine.

        Un courtier annonce « à partir de 0,1 pip ». Ce qui compte est ce qu'on
        paie en moyenne, et le pire qu'on ait vu. Le backtest facture le médian.
        """
        info = mt5.symbol_info(symbole)
        if info is None:
            raise CourtierIndisponible(f"Symbole inconnu : {symbole}")

        courant = info.spread if info.spread else (info.ask - info.bid) / info.point
        median = maxi = None
        barres = mt5.copy_rates_from_pos(symbole, mt5.TIMEFRAME_M1, 0, echantillon_barres)
        if barres is not None and len(barres) and "spread" in barres.dtype.names:
            releves = [int(b["spread"]) for b in barres if b["spread"] > 0]
            if releves:
                median, maxi = statistics.median(releves), max(releves)

        return CoutsSymbole(
            spread_courant_points=float(courant),
            spread_median_points=float(median) if median is not None else None,
            spread_max_observe_points=float(maxi) if maxi is not None else None,
            swap_long=info.swap_long, swap_short=info.swap_short,
            swap_mode=info.swap_mode,
        )

    # --- Le piège n°6 : le mode de remplissage -----------------------------
    def mode_remplissage(self, symbole: str) -> int:
        """Le mode que CE courtier accepte pour CE symbole.

        Envoyer un ordre avec un mode non supporté le fait rejeter avec un code
        obscur (10030, « Unsupported filling mode »). C'est le bug de
        portabilité le plus fréquent, et il ne se voit qu'en production.
        """
        info = mt5.symbol_info(symbole)
        if info is None:
            raise CourtierIndisponible(f"Symbole inconnu : {symbole}")
        # `filling_mode` est un champ de BITS (SYMBOL_FILLING_FOK = 1,
        # SYMBOL_FILLING_IOC = 2 en MQL5). Le paquet Python n'exporte pas ces
        # deux constantes, seulement les ORDER_FILLING_*, qui valent 0, 1, 2
        # et ne sont PAS des drapeaux : les confondre ferait tester le mauvais bit.
        drapeaux = info.filling_mode
        if drapeaux & _SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        if drapeaux & _SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        return mt5.ORDER_FILLING_RETURN

    def diagnostic(self, symbole_base: str = "EURUSD") -> str:
        """Le rapport à lire avant d'armer quoi que ce soit chez un nouveau courtier."""
        p = self.profil()
        sym = self.trouver_symbole(symbole_base)
        if not sym:
            return f"{p}\n\n  Aucun symbole {symbole_base} trouvé."
        s, c = self.specs(sym), self.couts(sym)
        remplissage = {mt5.ORDER_FILLING_FOK: "FOK", mt5.ORDER_FILLING_IOC: "IOC",
                       mt5.ORDER_FILLING_RETURN: "RETURN"}[self.mode_remplissage(sym)]
        dec = (f"UTC{p.decalage_serveur_h:+g}" if p.decalage_serveur_h is not None
               else "NON MESURÉ — marché fermé, à refaire en séance")

        stop_70_pips = 70 * (10 if s.digits in (3, 5) else 1)
        risque_min = s.volume_min * stop_70_pips * s.valeur_point_par_lot
        capital_1pct = risque_min * 100

        return "\n".join([
            "=" * 70,
            "  PROFIL DU COURTIER",
            "=" * 70,
            f"  Société            {p.societe}",
            f"  Serveur            {p.serveur}   ({'DÉMO' if p.demo else 'RÉEL'})",
            f"  Compte             {p.login} · {p.devise} · levier 1:{p.levier}",
            f"  Solde / équité     {p.solde:.2f} / {p.equite:.2f} {p.devise}",
            f"  Mode de position   {'couverture (hedging)' if p.couverture else 'compensation (netting)'}",
            f"  Décalage serveur   {dec}",
            f"  Trading autorisé   {'oui' if p.trading_autorise else 'NON'}"
            f"   ·  Algo : {'oui' if p.algo_autorise else 'NON — à activer dans MT5'}",
            "",
            f"  SYMBOLE            {sym}"
            + (f"   (demandé : {symbole_base})" if sym != symbole_base else ""),
            f"  Décimales          {s.digits}   ·  point = {s.point}  ·  pip = {s.pip}",
            f"  Taille contrat     {s.taille_contrat:,.0f}".replace(",", " "),
            f"  Lots               min {s.volume_min:g} · pas {s.volume_step:g} · max {s.volume_max:g}",
            f"  Valeur du point    {s.valeur_point_par_lot:.5f} {p.devise} par lot",
            f"  Stops level        {s.stops_level_points} points"
            + ("  (aucune contrainte)" if not s.stops_level_points else ""),
            f"  Remplissage        {remplissage}",
            "",
            f"  Spread courant     {c.spread_courant_points:.0f} points",
            f"  Spread médian      "
            + (f"{c.spread_median_points:.0f} points   <- c'est CE chiffre que le backtest facture"
               if c.spread_median_points is not None else "non mesurable (historique M1 absent)"),
            f"  Spread max observé "
            + (f"{c.spread_max_observe_points:.0f} points" if c.spread_max_observe_points
               is not None else "—"),
            f"  Swaps              long {c.swap_long:g} · short {c.swap_short:g}",
            "",
            "  VIABILITÉ DU CAPITAL  (stop de 70 pips, ordre de grandeur H4)",
            f"    Le lot minimum risque {risque_min:.2f} {p.devise}",
            f"    -> capital nécessaire pour tenir 1 % : ~{capital_1pct:.0f} {p.devise}",
            f"    -> à 2 % (plafond du code)          : ~{capital_1pct / 2:.0f} {p.devise}",
            "=" * 70,
        ])


# Les noms d'un même instrument d'un courtier à l'autre. Mesuré le 2026-09-16 :
# chez Deriv, le Nasdaq 100 s'appelle « US Tech 100 » (famille Stock Indices).
def _expliquer_erreur(code: int, message: str, chemin: str | None) -> str:
    aides = {
        -6: ("Le terminal refuse l'autorisation : aucun compte enregistré.\n"
             "  1. Ouvre MetaTrader 5\n"
             "  2. Fichier > Se connecter à un compte de trading\n"
             "  3. Coche « Enregistrer les données du compte »\n"
             "  4. Laisse le terminal ouvert, puis relance ceci."),
        -10: "Le terminal est introuvable au chemin indiqué.",
        -2: "Paramètres d'initialisation invalides.",
    }
    detail = aides.get(code, message)
    return (f"Connexion au terminal impossible (code {code}).\n  {detail}"
            + (f"\n  Chemin essayé : {chemin}" if chemin else ""))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    chemin = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        with Courtier(chemin_terminal=chemin) as c:
            print(c.diagnostic("EURUSD"))
    except CourtierIndisponible as e:
        print("\n⛔ COURTIER INDISPONIBLE\n")
        print(f"  {e}\n")
        sys.exit(1)
