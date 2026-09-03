"""La MÉMOIRE — une conversation par numéro, et les trois états qui l'entourent.

Trois choses vivent ici, et aucune n'est décorative :

1. L'HISTORIQUE, par numéro. Sans lui l'agent redemande son nom à chaque
   message et le client s'en va.

2. LA FENÊTRE DE 24 HEURES. Meta laisse répondre librement pendant 24 h après le
   dernier message du client ; passé ce délai, seul un modèle pré-approuvé peut
   partir. Ce n'est pas une politesse, c'est la règle qui fait bannir un numéro
   quand on l'ignore. L'agent doit donc SAVOIR s'il a le droit de parler.

3. LA MAIN HUMAINE. Quand quelqu'un de la maison reprend la conversation,
   l'agent se tait — jusqu'à ce qu'on le relance. Un agent qui répond par-dessus
   son patron est pire que pas d'agent du tout.

Stockage : SQLite, un fichier. Pas de serveur, pas de dépendance : ça tourne sur
le petit hébergement d'un client de Cotonou comme sur un Render.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

FENETRE_SERVICE = timedelta(hours=24)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    maison    TEXT NOT NULL,
    numero    TEXT NOT NULL,
    role      TEXT NOT NULL,          -- 'user' | 'assistant'
    contenu   TEXT NOT NULL,          -- texte, ou JSON pour les blocs d'outil
    entrant   INTEGER NOT NULL,       -- 1 si le message vient du client
    quand     TEXT NOT NULL           -- ISO 8601 UTC
);
CREATE INDEX IF NOT EXISTS idx_fil ON messages (maison, numero, id);

-- ⚠️ Meta REJOUE un webhook qu'il croit non livré. Sans cette table, un accusé
-- de réception perdu fait répondre deux fois au même message — et facturer deux
-- fois. On garde l'identifiant du fournisseur, qui est unique par message.
CREATE TABLE IF NOT EXISTS vus (
    identifiant TEXT PRIMARY KEY,
    quand       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fils (
    maison        TEXT NOT NULL,
    numero        TEXT NOT NULL,
    nom           TEXT DEFAULT '',
    main_humaine  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (maison, numero)
);
"""


def maintenant() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Tour:
    role: str
    contenu: str
    entrant: bool
    quand: datetime


class Memoire:
    def __init__(self, fichier: Path | str = "whatsapp-agent.db"):
        self.fichier = Path(fichier)
        self.fichier.parent.mkdir(parents=True, exist_ok=True)
        self.cx = sqlite3.connect(self.fichier, check_same_thread=False)
        self.cx.row_factory = sqlite3.Row
        self.cx.executescript(_SCHEMA)
        self.cx.commit()

    def fermer(self) -> None:
        self.cx.close()

    # --- écriture ------------------------------------------------------
    def noter(self, maison: str, numero: str, role: str, contenu,
              entrant: bool, quand: datetime | None = None) -> None:
        """Ajoute un tour au fil. `contenu` peut être du texte ou des blocs d'outil."""
        brut = contenu if isinstance(contenu, str) else json.dumps(contenu, ensure_ascii=False)
        self.cx.execute(
            "INSERT INTO messages (maison, numero, role, contenu, entrant, quand)"
            " VALUES (?,?,?,?,?,?)",
            (maison, numero, role, brut, 1 if entrant else 0,
             (quand or maintenant()).isoformat()),
        )
        self.cx.execute(
            "INSERT OR IGNORE INTO fils (maison, numero) VALUES (?,?)", (maison, numero))
        self.cx.commit()

    # --- lecture -------------------------------------------------------
    def historique(self, maison: str, numero: str, limite: int = 20) -> list[dict]:
        """Les derniers tours, au format attendu par l'API Messages.

        ⚠️ On rend les tours DANS L'ORDRE. On les tire les plus récents d'abord
        pour ne lire que ce qu'il faut, puis on les remet à l'endroit : servir
        une conversation à l'envers, c'est servir une autre conversation.
        """
        lignes = self.cx.execute(
            "SELECT role, contenu FROM messages WHERE maison=? AND numero=?"
            " ORDER BY id DESC LIMIT ?", (maison, numero, limite)).fetchall()
        tours = []
        for l in reversed(lignes):
            contenu = l["contenu"]
            if contenu.startswith("[") or contenu.startswith("{"):
                try:
                    contenu = json.loads(contenu)
                except json.JSONDecodeError:
                    pass
            tours.append({"role": l["role"], "content": contenu})
        # Une conversation envoyée au modèle ne peut pas commencer par l'agent.
        while tours and tours[0]["role"] != "user":
            tours.pop(0)
        return tours

    def dernier_entrant(self, maison: str, numero: str) -> datetime | None:
        ligne = self.cx.execute(
            "SELECT quand FROM messages WHERE maison=? AND numero=? AND entrant=1"
            " ORDER BY id DESC LIMIT 1", (maison, numero)).fetchone()
        return datetime.fromisoformat(ligne["quand"]) if ligne else None

    def fenetre_ouverte(self, maison: str, numero: str,
                        quand: datetime | None = None) -> bool:
        """A-t-on encore le droit de répondre librement à ce numéro ?"""
        dernier = self.dernier_entrant(maison, numero)
        if dernier is None:
            return False
        return (quand or maintenant()) - dernier < FENETRE_SERVICE

    def messages_du_client(self, maison: str, numero: str, heures: int = 24) -> int:
        """Combien de messages ce numéro a envoyés récemment (garde-fou anti-abus)."""
        depuis = (maintenant() - timedelta(hours=heures)).isoformat()
        return self.cx.execute(
            "SELECT COUNT(*) n FROM messages WHERE maison=? AND numero=? AND entrant=1"
            " AND quand > ?", (maison, numero, depuis)).fetchone()["n"]

    # --- ne pas traiter deux fois le même message ------------------------
    def deja_vu(self, identifiant: str) -> bool:
        """Vrai si ce message a déjà été traité. Le marque au passage.

        ⚠️ L'insertion et la question sont le MÊME geste : les poser en deux temps
        laisserait deux webhooks simultanés passer tous les deux.
        """
        if not identifiant:
            return False  # un message sans identifiant ne peut pas être dédoublonné
        curseur = self.cx.execute(
            "INSERT OR IGNORE INTO vus (identifiant, quand) VALUES (?,?)",
            (identifiant, maintenant().isoformat()))
        self.cx.commit()
        return curseur.rowcount == 0

    # --- la main humaine -----------------------------------------------
    def main_humaine(self, maison: str, numero: str) -> bool:
        ligne = self.cx.execute(
            "SELECT main_humaine FROM fils WHERE maison=? AND numero=?",
            (maison, numero)).fetchone()
        return bool(ligne and ligne["main_humaine"])

    def passer_la_main(self, maison: str, numero: str) -> None:
        """Quelqu'un de la maison prend le relais : l'agent se tait."""
        self.cx.execute(
            "INSERT INTO fils (maison, numero, main_humaine) VALUES (?,?,1)"
            " ON CONFLICT(maison, numero) DO UPDATE SET main_humaine=1",
            (maison, numero))
        self.cx.commit()

    def reprendre(self, maison: str, numero: str) -> None:
        self.cx.execute(
            "INSERT INTO fils (maison, numero, main_humaine) VALUES (?,?,0)"
            " ON CONFLICT(maison, numero) DO UPDATE SET main_humaine=0",
            (maison, numero))
        self.cx.commit()

    def nommer(self, maison: str, numero: str, nom: str) -> None:
        self.cx.execute(
            "INSERT INTO fils (maison, numero, nom) VALUES (?,?,?)"
            " ON CONFLICT(maison, numero) DO UPDATE SET nom=excluded.nom",
            (maison, numero, nom))
        self.cx.commit()

    def nom(self, maison: str, numero: str) -> str:
        ligne = self.cx.execute(
            "SELECT nom FROM fils WHERE maison=? AND numero=?", (maison, numero)).fetchone()
        return (ligne["nom"] if ligne else "") or ""
