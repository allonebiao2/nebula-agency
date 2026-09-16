# -*- coding: utf-8 -*-
"""
L'exécution : le seul module qui parle d'argent au courtier.

Les règles qui ne se négocient pas, toutes vérifiées ICI et pas en amont :

  1. PAS D'ORDRE SANS STOP DÉPOSÉ CHEZ LE COURTIER. L'ordre part avec son SL et
     son TP. Après l'ouverture, on RELIT la position : si le courtier l'a
     ouverte sans stop, on la ferme immédiatement et on crie.
  2. LE MODE DÉCIDE, PAS LA BONNE VOLONTÉ.
       observation  aucun ordre, jamais ; l'agent dit ce qu'il aurait fait
       demo         ordres seulement si le COMPTE est un compte démo
       reel         ordres seulement si le compte est réel, le mode réel
                    choisi dans la configuration, un plafond de capital défini
                    et une licence valide
     Un compte réel branché pendant que le mode est « demo » : refus. C'est
     l'erreur qu'on fait un soir en changeant de compte dans le terminal.
  3. LE STOP NE S'ÉLARGIT JAMAIS, même demandé par l'agent lui-même.
  4. LE BOT NE TOUCHE QUE SES POSITIONS (magic number). Les trades manuels de
     l'utilisateur lui sont invisibles.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    import MetaTrader5 as mt5
except ImportError:                                            # pragma: no cover
    mt5 = None

from ..noyau.plan import ACHAT
from ..noyau.risque import deplacement_de_stop_autorise

MODES = ("observation", "demo", "reel")
A_REESSAYER = {10004, 10020, 10021}          # requote, prix changé, prix hors cotation


class ExecutionRefusee(Exception):
    pass


@dataclass
class ResultatOrdre:
    ok: bool
    ticket: int | None = None
    prix: float | None = None
    sl: float | None = None
    tp: float | None = None
    retcode: int | None = None
    message: str = ""
    prix_demande: float | None = None
    glissement_points: float | None = None   # positif = défavorable


def autorisation(mode: str, *, compte_demo: bool, mode_config: str,
                 capital_max_engage: float, licence_valide: bool,
                 profil_boost: bool = False, porte_boost_franchie: bool = False,
                 porte_demo_franchie: bool = False) -> tuple[bool, str]:
    """Le mode permet-il d'envoyer un ordre sur CE compte ? Raison en clair.

    BOOST en RÉEL : exige la porte de la phase 5 du cahier des charges (60 jours de
    PRO rentable). En démo, BOOST est libre : c'est là qu'on l'essaie.
    """
    if mode not in MODES:
        return False, f"mode inconnu : {mode}"
    if mode == "observation":
        return False, "mode observation : l'agent analyse et journalise, il n'envoie rien"
    if mode == "demo":
        if not compte_demo:
            return False, ("le terminal est branché sur un compte RÉEL alors que le mode est "
                           "« démo » : aucun ordre ne part")
        return True, ""
    # reel
    if compte_demo:
        return False, "mode réel demandé, mais le compte branché est un compte démo"
    if mode_config != "reel":
        return False, "mode réel non activé dans la configuration ([compte] mode = \"reel\")"
    if capital_max_engage <= 0:
        return False, "aucun plafond de capital défini : le mode réel reste bloqué"
    if not licence_valide:
        return False, "licence absente ou expirée : le mode réel est réservé aux licences"
    if not porte_demo_franchie:
        return False, ("porte démo non franchie : 30 jours, 30 trades, 100 % d'ordres avec stop et "
                       "glissement conforme sur compte démo d'abord (page Évolution)")
    if profil_boost and not porte_boost_franchie:
        return False, ("profil BOOST en réel refusé : il faut d'abord 60 jours de PRO rentable "
                       "(phase 5 du cahier des charges). En démo, BOOST est libre.")
    return True, ""


def marche_ferme(*, achat: bool, trade_mode: int | None, cotation_s: float | None,
                 reference_s: float | None, age_max_s: float = 600) -> str:
    """Pourquoi on ne peut PAS ouvrir sur cet instrument maintenant ; vide si on peut.

    À l'échelle H4, aucune bougie du NAS100 n'est absente chez Deriv (mesuré sur 4 250
    barres) : la coupure quotidienne d'une heure tombe DANS la bougie de 20 h. Ce qui
    ferme vraiment l'indice, ce sont les jours fériés américains et les clôtures
    anticipées (4 vendredis sur 49 sans bougie de 20 h). Un ordre envoyé là revient
    rejeté, et trois rejets en une heure mettent TOUT l'agent en pause, EUR/USD compris.

    `trade_mode` : SYMBOL_TRADE_MODE du courtier (0 désactivé, 1 achats seuls, 2 ventes
    seules, 3 clôture seule, 4 complet). La fraîcheur de la cotation se compare à la
    cotation la plus FRAÎCHE des instruments suivis, pas à l'horloge : un décalage
    horaire du serveur mal mesuré ne fabrique ainsi ni fausse fermeture ni fausse ouverture.
    """
    if trade_mode is not None:
        if trade_mode in (0, 3):
            return "instrument fermé aux ouvertures chez le courtier (clôture seule ou désactivé)"
        if trade_mode == 1 and not achat:
            return "le courtier n'autorise que les achats sur cet instrument"
        if trade_mode == 2 and achat:
            return "le courtier n'autorise que les ventes sur cet instrument"
    if not cotation_s:
        return "aucune cotation reçue : marché fermé"
    if reference_s and reference_s - cotation_s > age_max_s:
        return (f"dernière cotation {int((reference_s - cotation_s) / 60)} min plus ancienne que les "
                f"autres marchés : séance fermée (jour férié, clôture anticipée)")
    return ""


class Executeur:
    def __init__(self, symbole: str, magic: int, *, deviation_points: int = 10,
                 tentatives: int = 3, mode_remplissage: int | None = None):
        self.symbole = symbole
        self.magic = magic
        self.deviation = deviation_points
        self.tentatives = max(1, tentatives)
        self.remplissage = mode_remplissage

    # ------------------------------------------------------------------ #
    def positions(self) -> list:
        ps = mt5.positions_get(symbol=self.symbole) or ()
        return [p for p in ps if p.magic == self.magic]

    def _remplissage(self) -> int:
        if self.remplissage is not None:
            return self.remplissage
        from ..noyau.courtier import _SYMBOL_FILLING_FOK, _SYMBOL_FILLING_IOC
        info = mt5.symbol_info(self.symbole)
        if info and info.filling_mode & _SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        if info and info.filling_mode & _SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        return mt5.ORDER_FILLING_RETURN

    # ------------------------------------------------------------------ #
    def ouvrir(self, plan, lots: float, *, specs, commentaire: str = "nebula") -> ResultatOrdre:
        """Ouvre au marché, stop et objectif posés chez le courtier dès l'ouverture.

        Le stop et l'objectif gardent la DISTANCE du plan, ancrée au prix
        réellement obtenu : c'est exactement ce que mesure le backtest.
        """
        achat = plan.sens == ACHAT
        derniere = None
        for _ in range(self.tentatives):
            tick = mt5.symbol_info_tick(self.symbole)
            if tick is None:
                return ResultatOrdre(False, message="aucun prix : marché fermé ?")
            prix = tick.ask if achat else tick.bid
            signe = 1 if achat else -1
            sl = round(prix - signe * plan.risque_prix, specs.digits)
            tp = round(prix + signe * plan.gain_prix, specs.digits)

            mini = (specs.stops_level_points or 0) * specs.point
            if abs(prix - sl) < mini or abs(tp - prix) < mini:
                return ResultatOrdre(False, message=(
                    f"stop ou objectif plus proche que le minimum du courtier "
                    f"({specs.stops_level_points} points)"))

            requete = {
                "action": mt5.TRADE_ACTION_DEAL, "symbol": self.symbole,
                "volume": float(lots),
                "type": mt5.ORDER_TYPE_BUY if achat else mt5.ORDER_TYPE_SELL,
                "price": prix, "sl": sl, "tp": tp, "deviation": self.deviation,
                "magic": self.magic, "comment": commentaire[:31],
                "type_time": mt5.ORDER_TIME_GTC, "type_filling": self._remplissage(),
            }
            r = mt5.order_send(requete)
            if r is None:
                code, msg = mt5.last_error()
                return ResultatOrdre(False, message=f"order_send a échoué ({code}, {msg})")
            derniere = r
            if r.retcode == mt5.TRADE_RETCODE_DONE:
                ticket = self._ticket_position(r)
                verif = self._verifier_stop(ticket)
                if not verif.ok:
                    return verif
                obtenu = r.price or prix
                # Le glissement mesuré ordre par ordre : c'est ce que la porte démo compare
                # au modèle de coûts du backtest.
                glisse = (obtenu - prix) / specs.point * (1 if achat else -1)
                return ResultatOrdre(True, ticket=ticket, prix=obtenu, sl=sl, tp=tp,
                                     retcode=r.retcode, message=r.comment,
                                     prix_demande=prix, glissement_points=round(glisse, 1))
            if r.retcode not in A_REESSAYER:
                break
        return ResultatOrdre(False, retcode=derniere.retcode if derniere else None,
                             message=(f"refusé par le courtier : {derniere.retcode} "
                                      f"{derniere.comment}") if derniere else "aucune réponse")

    def _ticket_position(self, r) -> int | None:
        for p in self.positions():
            if p.ticket == r.order or p.identifier == r.order:
                return p.ticket
        ps = sorted(self.positions(), key=lambda p: p.time_msc)
        return ps[-1].ticket if ps else r.order

    def _verifier_stop(self, ticket: int | None) -> ResultatOrdre:
        """Règle 1 : une position sans stop chez le courtier ne survit pas."""
        p = next((x for x in self.positions() if x.ticket == ticket), None)
        if p is None:
            return ResultatOrdre(True, ticket=ticket)
        if not p.sl:
            self.fermer(p, motif="sans stop côté serveur")
            return ResultatOrdre(False, ticket=ticket, message=(
                "⛔ le courtier a ouvert la position SANS stop : elle a été fermée "
                "immédiatement"))
        return ResultatOrdre(True, ticket=ticket, sl=p.sl, tp=p.tp)

    # ------------------------------------------------------------------ #
    def modifier_stop(self, position, nouveau_sl: float, *, digits: int) -> ResultatOrdre:
        sens = "achat" if position.type == mt5.POSITION_TYPE_BUY else "vente"
        ok, raison = deplacement_de_stop_autorise(
            sens=sens, stop_actuel=position.sl, stop_propose=nouveau_sl)
        if not ok:
            return ResultatOrdre(False, ticket=position.ticket, message=raison)
        r = mt5.order_send({
            "action": mt5.TRADE_ACTION_SLTP, "symbol": self.symbole,
            "position": position.ticket, "sl": round(nouveau_sl, digits), "tp": position.tp,
            "magic": self.magic,
        })
        if r is None or r.retcode not in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_NO_CHANGES):
            return ResultatOrdre(False, ticket=position.ticket,
                                 retcode=getattr(r, "retcode", None),
                                 message=getattr(r, "comment", "") or str(mt5.last_error()))
        return ResultatOrdre(True, ticket=position.ticket, sl=nouveau_sl)

    def poser_stop(self, position, sl: float, *, digits: int) -> ResultatOrdre:
        """Pose un stop sur une position qui n'en a AUCUN. Ce n'est pas un élargissement :
        l'invariant ne s'applique qu'entre deux stops. Utilisé par le chien de garde."""
        if position.sl:
            return ResultatOrdre(False, ticket=position.ticket, message="la position a déjà un stop")
        r = mt5.order_send({
            "action": mt5.TRADE_ACTION_SLTP, "symbol": self.symbole,
            "position": position.ticket, "sl": round(sl, digits), "tp": position.tp,
            "magic": self.magic,
        })
        if r is None or r.retcode != mt5.TRADE_RETCODE_DONE:
            return ResultatOrdre(False, ticket=position.ticket, retcode=getattr(r, "retcode", None),
                                 message=getattr(r, "comment", "") or str(mt5.last_error()))
        return ResultatOrdre(True, ticket=position.ticket, sl=sl)

    def fermer(self, position, *, motif: str = "") -> ResultatOrdre:
        tick = mt5.symbol_info_tick(self.symbole)
        if tick is None:
            return ResultatOrdre(False, ticket=position.ticket, message="aucun prix")
        achat = position.type == mt5.POSITION_TYPE_BUY
        derniere = None
        for _ in range(self.tentatives):
            r = mt5.order_send({
                "action": mt5.TRADE_ACTION_DEAL, "symbol": self.symbole,
                "volume": position.volume, "position": position.ticket,
                "type": mt5.ORDER_TYPE_SELL if achat else mt5.ORDER_TYPE_BUY,
                "price": tick.bid if achat else tick.ask, "deviation": self.deviation,
                "magic": self.magic, "comment": f"nebula {motif}"[:31],
                "type_time": mt5.ORDER_TIME_GTC, "type_filling": self._remplissage(),
            })
            derniere = r
            if r is not None and r.retcode == mt5.TRADE_RETCODE_DONE:
                return ResultatOrdre(True, ticket=position.ticket, prix=r.price,
                                     retcode=r.retcode, message=motif)
            if r is None or r.retcode not in A_REESSAYER:
                break
            tick = mt5.symbol_info_tick(self.symbole)
        return ResultatOrdre(False, ticket=position.ticket,
                             retcode=getattr(derniere, "retcode", None),
                             message=getattr(derniere, "comment", "") or str(mt5.last_error()))

    # ------------------------------------------------------------------ #
    def bilan_position_fermee(self, ticket: int) -> dict | None:
        """Résultat réel d'une position fermée, lu dans l'historique du courtier."""
        deals = mt5.history_deals_get(position=ticket)
        if not deals:
            return None
        sorties = [d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT]
        if not sorties:
            return None
        net = sum(d.profit + d.commission + d.swap + getattr(d, "fee", 0.0) for d in deals)
        derniere = max(sorties, key=lambda d: d.time_msc)
        motif = {mt5.DEAL_REASON_SL: "stop", mt5.DEAL_REASON_TP: "objectif",
                 mt5.DEAL_REASON_SO: "appel de marge", mt5.DEAL_REASON_EXPERT: "agent",
                 mt5.DEAL_REASON_CLIENT: "manuel"}.get(derniere.reason, f"raison {derniere.reason}")
        if derniere.comment.startswith("nebula "):
            motif = derniere.comment.removeprefix("nebula ")
        return {"prix": derniere.price, "resultat": net, "motif": motif,
                "ferme_le": derniere.time}
