# -*- coding: utf-8 -*-
"""
Le calendrier économique : quand NE PAS entrer.

Source : le flux hebdomadaire public de Forex Factory
(`nfs.faireconomy.media/ff_calendar_thisweek.json`), vérifié le 2026-09-16 :
105 événements, dont le FOMC du jour. Aucune clé, aucun compte.

Trois règles :
  · ON NE L'INTERROGE PAS À CHAQUE CYCLE. Le flux change quelques fois par
    semaine et il limite les appels : cache de 6 heures sur le disque.
  · NE PAS SAVOIR N'EST PAS SAVOIR QU'IL N'Y A RIEN. Flux indisponible et cache
    trop vieux (plus de 7 jours) : le verrou s'abstient, donc refuse.
  · LES HEURES DU FLUX SONT EN HEURE DE NEW YORK avec leur décalage écrit
    (`-04:00`) ; les verrous raisonnent en heure du SERVEUR du courtier. On
    passe tout par UTC, et on ne suppose aucun fuseau.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .chemins import fichier

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
CACHE_H = 6
TROP_VIEUX_J = 7


@dataclass(frozen=True)
class Annonce:
    quand_utc: datetime
    devise: str
    titre: str
    impact: str


class Calendrier:
    def __init__(self, devises=("USD", "EUR"), *, avant_min: int = 30, apres_min: int = 15,
                 decalage_serveur_h: float = 0.0, impacts=("High",)):
        self.devises = set(devises)
        self.avant = timedelta(minutes=avant_min)
        self.apres = timedelta(minutes=apres_min)
        self.decalage = timedelta(hours=decalage_serveur_h or 0.0)
        self.impacts = set(impacts)
        self._annonces: list[Annonce] = []
        self._charge_le = 0.0
        self.erreur = ""
        self.url = URL

    # ------------------------------------------------------------------ #
    def _lire_disque(self) -> tuple[list, float] | None:
        p = fichier("calendrier.json")
        if not p.exists():
            return None
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            return d["evenements"], float(d["telecharge_le"])
        except Exception:                                  # noqa: BLE001
            return None

    def rafraichir(self, *, forcer: bool = False) -> None:
        disque = self._lire_disque()
        if disque and not forcer and time.time() - disque[1] < CACHE_H * 3600:
            brut, quand = disque
        else:
            try:
                req = urllib.request.Request(self.url, headers={"User-Agent": "NEBULA-Trader/1.0"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    brut = json.loads(r.read().decode("utf-8"))
                quand = time.time()
                fichier("calendrier.json").write_text(
                    json.dumps({"telecharge_le": quand, "evenements": brut}, ensure_ascii=False),
                    encoding="utf-8")
                self.erreur = ""
            except Exception as exc:                       # noqa: BLE001
                self.erreur = f"flux indisponible ({exc.__class__.__name__})"
                if not disque:
                    self._annonces, self._charge_le = [], 0.0
                    return
                brut, quand = disque
        self._charge_le = quand
        self._annonces = []
        for e in brut:
            try:
                q = datetime.fromisoformat(e["date"]).astimezone(timezone.utc)
            except Exception:                              # noqa: BLE001
                continue
            self._annonces.append(Annonce(q, e.get("country", ""), e.get("title", ""),
                                          e.get("impact", "")))

    @property
    def disponible(self) -> bool:
        return bool(self._charge_le) and time.time() - self._charge_le < TROP_VIEUX_J * 86400

    def a_venir(self, maintenant_utc: datetime | None = None, heures: int = 48) -> list[Annonce]:
        maintenant_utc = maintenant_utc or datetime.now(timezone.utc)
        fin = maintenant_utc + timedelta(hours=heures)
        return sorted((a for a in self._annonces
                       if a.devise in self.devises and a.impact in self.impacts
                       and maintenant_utc - self.apres <= a.quand_utc <= fin),
                      key=lambda a: a.quand_utc)

    # ------------------------------------------------------------------ #
    def __call__(self, maintenant_serveur: datetime) -> tuple[bool, str]:
        """La signature attendue par le verrou Q5. Reçoit l'heure du SERVEUR."""
        if time.time() - self._charge_le > CACHE_H * 3600:
            self.rafraichir()
        if not self.disponible:
            raise CalendrierIndisponible(self.erreur or "calendrier jamais chargé")
        if maintenant_serveur.tzinfo is None:
            utc = (maintenant_serveur - self.decalage).replace(tzinfo=timezone.utc)
        else:
            utc = maintenant_serveur.astimezone(timezone.utc)
        for a in self._annonces:
            if a.devise not in self.devises or a.impact not in self.impacts:
                continue
            if a.quand_utc - self.avant <= utc <= a.quand_utc + self.apres:
                return True, (f"{a.devise} « {a.titre} » à {a.quand_utc:%H:%M} UTC "
                              f"(fenêtre -{self.avant.seconds // 60}/+{self.apres.seconds // 60} min)")
        return False, ""


class CalendrierIndisponible(Exception):
    pass


def verrou_annonces(calendrier: Calendrier):
    """Adapte le calendrier au verrou : une indisponibilité devient un REFUS."""
    def _annonce(maintenant):
        try:
            return calendrier(maintenant)
        except CalendrierIndisponible as exc:
            return True, f"calendrier indisponible ({exc}) : on s'abstient"
    return _annonce
