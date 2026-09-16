# -*- coding: utf-8 -*-
"""
Le journal : la mémoire de l'agent, et son jeu de données d'entraînement.

Ce n'est pas de la comptabilité. Chaque décision est gardée avec son contexte
complet AU MOMENT où elle a été prise, y compris les signaux REFUSÉS : un
trade qu'on n'a pas pris est une donnée aussi précieuse qu'un trade perdu. Sans
ce journal, « s'améliorer tout seul » serait un mot creux.

C'est aussi ce que l'interface raconte : ce que l'agent a vu, ce qu'il a
décidé, pourquoi, et ce que ça a donné.

SQLite, un fichier, aucune installation. Une connexion par appel : l'agent et
le serveur web tournent dans des fils différents, et SQLite n'aime pas qu'une
connexion change de fil.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..noyau.chemins import fichier

SCHEMA = """
CREATE TABLE IF NOT EXISTS evenements (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, niveau TEXT NOT NULL,
    type TEXT NOT NULL, message TEXT NOT NULL, donnees TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, barre TEXT, strategie TEXT, sens TEXT,
    entree REAL, stop REAL, objectif REAL, these TEXT, verdict TEXT NOT NULL,
    motif TEXT, verrous TEXT, lots REAL, risque_pct REAL, risque_devise REAL,
    note TEXT, mode TEXT, contexte TEXT
);
CREATE TABLE IF NOT EXISTS ordres (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, action TEXT NOT NULL, ticket INTEGER,
    sens TEXT, lots REAL, prix REAL, sl REAL, tp REAL, retcode INTEGER,
    commentaire TEXT, mode TEXT
);
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY, ticket INTEGER UNIQUE, strategie TEXT, sens TEXT, lots REAL,
    ouvert_le TEXT, prix_entree REAL, stop_initial REAL, objectif REAL,
    risque_devise REAL, ferme_le TEXT, prix_sortie REAL, resultat_devise REAL,
    resultat_R REAL, motif TEXT, these TEXT, contexte TEXT, mode TEXT
);
CREATE TABLE IF NOT EXISTS equite (
    ts TEXT PRIMARY KEY, solde REAL, equite REAL, marge_libre REAL,
    sommet REAL, drawdown_pct REAL
);
CREATE TABLE IF NOT EXISTS reglages_historique (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, cle TEXT, avant TEXT, apres TEXT, auteur TEXT
);
CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, role TEXT NOT NULL, contenu TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_decisions_ts ON decisions(ts);
CREATE INDEX IF NOT EXISTS idx_evenements_ts ON evenements(ts);
CREATE INDEX IF NOT EXISTS idx_trades_ferme ON trades(ferme_le);
"""


def maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Journal:
    def __init__(self, chemin: Path | None = None):
        self.chemin = Path(chemin) if chemin else fichier("journal.db")
        self._verrou = threading.Lock()
        with self._cx() as cx:
            cx.executescript(SCHEMA)

    @contextmanager
    def _cx(self):
        cx = sqlite3.connect(self.chemin, timeout=10)
        cx.row_factory = sqlite3.Row
        try:
            yield cx
            cx.commit()
        finally:
            cx.close()

    def _ecrire(self, sql: str, params: tuple) -> int:
        with self._verrou, self._cx() as cx:
            return cx.execute(sql, params).lastrowid

    def _lire(self, sql: str, params: tuple = ()) -> list[dict]:
        with self._cx() as cx:
            return [dict(r) for r in cx.execute(sql, params).fetchall()]

    # ------------------------------------------------------------------ #
    #  Écritures
    # ------------------------------------------------------------------ #
    def evenement(self, type_: str, message: str, *, niveau: str = "info",
                  donnees: dict | None = None) -> int:
        return self._ecrire(
            "INSERT INTO evenements (ts, niveau, type, message, donnees) VALUES (?,?,?,?,?)",
            (maintenant(), niveau, type_, message,
             json.dumps(donnees, ensure_ascii=False, default=str) if donnees else None))

    def decision(self, *, verdict_obj=None, plan=None, verdict: str, motif: str = "",
                 mode: str, barre: datetime | None = None) -> int:
        plan = plan or (verdict_obj.plan if verdict_obj else None)
        dim = verdict_obj.dimensionnement if verdict_obj else None
        verrous = ([{"n": v.numero, "question": v.question, "passe": v.passe,
                     "detail": v.detail, "maison": v.maison} for v in verdict_obj.verrous]
                   if verdict_obj else [])
        return self._ecrire(
            """INSERT INTO decisions (ts, barre, strategie, sens, entree, stop, objectif, these,
               verdict, motif, verrous, lots, risque_pct, risque_devise, note, mode, contexte)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (maintenant(), barre.isoformat() if barre else None,
             plan.strategie if plan else None, plan.sens if plan else None,
             plan.entree if plan else None, plan.stop if plan else None,
             plan.objectif if plan else None, plan.these if plan else None,
             verdict, motif, json.dumps(verrous, ensure_ascii=False),
             dim.lots if dim and dim.autorise else None,
             dim.risque_pct if dim and dim.autorise else None,
             dim.risque_devise if dim and dim.autorise else None,
             dim.note if dim else None, mode,
             json.dumps(plan.contexte, ensure_ascii=False, default=str) if plan else None))

    def ordre(self, *, action: str, ticket=None, sens=None, lots=None, prix=None, sl=None,
              tp=None, retcode=None, commentaire="", mode="") -> int:
        return self._ecrire(
            """INSERT INTO ordres (ts, action, ticket, sens, lots, prix, sl, tp, retcode,
               commentaire, mode) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (maintenant(), action, ticket, sens, lots, prix, sl, tp, retcode, commentaire, mode))

    def ouvrir_trade(self, *, ticket: int, plan, lots: float, prix: float,
                     risque_devise: float, mode: str) -> None:
        self._ecrire(
            """INSERT OR IGNORE INTO trades (ticket, strategie, sens, lots, ouvert_le,
               prix_entree, stop_initial, objectif, risque_devise, these, contexte, mode)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ticket, plan.strategie, plan.sens, lots, maintenant(), prix, plan.stop,
             plan.objectif, risque_devise, plan.these,
             json.dumps(plan.contexte, ensure_ascii=False, default=str), mode))

    def fermer_trade(self, *, ticket: int, prix: float, resultat: float, motif: str,
                     ferme_le: str | None = None) -> None:
        t = self._lire("SELECT risque_devise FROM trades WHERE ticket=?", (ticket,))
        risque = t[0]["risque_devise"] if t else None
        self._ecrire(
            """UPDATE trades SET ferme_le=?, prix_sortie=?, resultat_devise=?, resultat_R=?,
               motif=? WHERE ticket=?""",
            (ferme_le or maintenant(), prix, resultat,
             resultat / risque if risque else None, motif, ticket))

    def point_equite(self, solde: float, equite: float, marge_libre: float) -> dict:
        precedent = self._lire("SELECT MAX(sommet) AS s FROM equite")
        sommet = max(equite, (precedent[0]["s"] or 0.0) if precedent else 0.0)
        dd = 100 * (sommet - equite) / sommet if sommet else 0.0
        self._ecrire("INSERT OR REPLACE INTO equite VALUES (?,?,?,?,?,?)",
                     (maintenant(), solde, equite, marge_libre, sommet, dd))
        return {"sommet": sommet, "drawdown_pct": dd}

    def reglage(self, cle: str, avant, apres, auteur: str) -> None:
        self._ecrire("INSERT INTO reglages_historique (ts, cle, avant, apres, auteur) "
                     "VALUES (?,?,?,?,?)", (maintenant(), cle, str(avant), str(apres), auteur))

    def message(self, role: str, contenu: str) -> None:
        self._ecrire("INSERT INTO conversation (ts, role, contenu) VALUES (?,?,?)",
                     (maintenant(), role, contenu))

    def remettre_sommet(self) -> None:
        """Après un arrêt total, le redémarrage manuel repart du niveau actuel."""
        with self._verrou, self._cx() as cx:
            cx.execute("UPDATE equite SET sommet = equite")

    # ------------------------------------------------------------------ #
    #  Lectures
    # ------------------------------------------------------------------ #
    def evenements(self, limite: int = 100) -> list[dict]:
        return self._lire("SELECT * FROM evenements ORDER BY id DESC LIMIT ?", (limite,))

    def decisions(self, limite: int = 100) -> list[dict]:
        lignes = self._lire("SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limite,))
        for l in lignes:
            l["verrous"] = json.loads(l["verrous"] or "[]")
            l["contexte"] = json.loads(l["contexte"] or "{}")
        return lignes

    def trades(self, limite: int = 200, *, ouverts: bool | None = None) -> list[dict]:
        cond = "" if ouverts is None else ("WHERE ferme_le IS NULL" if ouverts
                                           else "WHERE ferme_le IS NOT NULL")
        return self._lire(f"SELECT * FROM trades {cond} ORDER BY id DESC LIMIT ?", (limite,))

    def trade_par_ticket(self, ticket: int) -> dict | None:
        r = self._lire("SELECT * FROM trades WHERE ticket=?", (ticket,))
        return r[0] if r else None

    def ordres(self, limite: int = 100) -> list[dict]:
        return self._lire("SELECT * FROM ordres ORDER BY id DESC LIMIT ?", (limite,))

    def courbe(self, depuis_jours: int = 90, points_max: int = 600) -> list[dict]:
        depuis = (datetime.now(timezone.utc) - timedelta(days=depuis_jours)).isoformat()
        lignes = self._lire("SELECT ts, equite, solde, drawdown_pct FROM equite WHERE ts >= ? "
                            "ORDER BY ts", (depuis,))
        if len(lignes) > points_max:
            pas = len(lignes) / points_max
            lignes = [lignes[int(i * pas)] for i in range(points_max)] + [lignes[-1]]
        return lignes

    def dernier_point(self) -> dict | None:
        r = self._lire("SELECT * FROM equite ORDER BY ts DESC LIMIT 1")
        return r[0] if r else None

    def historique_reglages(self, limite: int = 100) -> list[dict]:
        return self._lire("SELECT * FROM reglages_historique ORDER BY id DESC LIMIT ?", (limite,))

    def conversation(self, limite: int = 60) -> list[dict]:
        return list(reversed(self._lire(
            "SELECT * FROM conversation ORDER BY id DESC LIMIT ?", (limite,))))

    # --- Statistiques qui nourrissent les verrous -------------------------
    def fermes_depuis(self, depuis: datetime) -> list[dict]:
        return self._lire("SELECT * FROM trades WHERE ferme_le >= ? ORDER BY ferme_le",
                          (depuis.isoformat(),))

    def ouverts_depuis(self, depuis: datetime) -> int:
        r = self._lire("SELECT COUNT(*) AS n FROM trades WHERE ouvert_le >= ?",
                       (depuis.isoformat(),))
        return r[0]["n"]

    def serie_perdante(self) -> tuple[int, str | None]:
        """Pertes consécutives depuis le dernier gain, et date de la dernière perte."""
        fermes = self._lire("SELECT resultat_devise, ferme_le FROM trades "
                            "WHERE ferme_le IS NOT NULL ORDER BY ferme_le DESC LIMIT 50")
        n, derniere = 0, None
        for t in fermes:
            if (t["resultat_devise"] or 0) <= 0:
                n += 1
                derniere = derniere or t["ferme_le"]
            else:
                break
        return n, derniere

    def statistiques(self) -> dict:
        fermes = self._lire("SELECT resultat_devise, resultat_R FROM trades "
                            "WHERE ferme_le IS NOT NULL")
        n = len(fermes)
        gains = [t for t in fermes if (t["resultat_devise"] or 0) > 0]
        somme_g = sum(t["resultat_devise"] for t in gains)
        somme_p = abs(sum(t["resultat_devise"] or 0 for t in fermes if t not in gains))
        r = [t["resultat_R"] for t in fermes if t["resultat_R"] is not None]
        return {
            "trades": n, "gagnants": len(gains),
            "taux_reussite": len(gains) / n if n else None,
            "resultat_net": sum(t["resultat_devise"] or 0 for t in fermes),
            "profit_factor": somme_g / somme_p if somme_p else None,
            "esperance_R": sum(r) / len(r) if r else None,
            "decisions": self._lire("SELECT COUNT(*) AS n FROM decisions")[0]["n"],
            "refus": self._lire("SELECT COUNT(*) AS n FROM decisions WHERE verdict='refuse'")[0]["n"],
        }
