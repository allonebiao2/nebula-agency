# -*- coding: utf-8 -*-
"""
Accès base : SQLite en local, PostgreSQL (Supabase) en production.

Le serveur continue d'écrire du SQLite (`?` en paramètre, `cur.lastrowid`,
`row["colonne"]`). Ce module traduit à la volée quand `DATABASE_URL` est posée,
pour que les 219 requêtes de server.py restent inchangées.

Pourquoi une couche plutôt qu'une réécriture : 219 requêtes réécrites à la main,
sur une base qui porte des commissions et des paiements, c'est 219 occasions de
casser quelque chose en silence. La couche est petite, testable, et réversible :
sans `DATABASE_URL`, on retombe exactement sur le comportement d'avant.

Ce qui est traduit :
  · `?`               → `%s`
  · `cur.lastrowid`   → `... RETURNING id` puis lecture de la valeur
  · `sqlite3.Row`     → dictionnaire (même accès `row["colonne"]`)
  · le schéma `naff`  → posé par `search_path`, donc aucune requête n'est préfixée

Ce qui n'a PAS besoin d'être traduit, vérifié requête par requête :
  · aucun `INSERT OR ...`, aucun `executescript`, aucun `executemany`
  · aucune fonction de date SQLite (les `strftime` du code sont du Python)
  · `ON CONFLICT ... DO UPDATE SET x=excluded.x` est déjà de la syntaxe Postgres
  · un seul `%` dans tout le SQL, et il est dans un paramètre, pas dans le texte
"""
import os, re, sqlite3, contextlib
from pathlib import Path

DSN = (os.getenv("DATABASE_URL") or "").strip()
IS_PG = bool(DSN)
SCHEMA = os.getenv("NAFF_PG_SCHEMA", "naff")

# Les deux seules tables sans colonne `id` : on ne leur ajoute jamais RETURNING id.
_SANS_ID = {"chat_reads", "app_settings"}
_RX_INSERT = re.compile(r"^\s*INSERT\s+INTO\s+([A-Za-z_][A-Za-z0-9_]*)", re.I)


def _traduire(sql: str) -> str:
    """`?` → `%s`. Sûr ici : le SQL du serveur ne contient aucun `%` littéral."""
    return sql.replace("?", "%s")


def _table_insert(sql: str):
    m = _RX_INSERT.match(sql)
    return m.group(1).lower() if m else None


class _Curseur:
    """Ce que `c.execute(...)` renvoie : de quoi lire, et un `lastrowid`."""

    def __init__(self, cur, lastrowid=None):
        self._cur = cur
        self.lastrowid = lastrowid

    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()

    def __iter__(self):
        return iter(self._cur)

    @property
    def rowcount(self):
        return self._cur.rowcount


class _ConnexionPG:
    """Présente une connexion psycopg avec les manières de sqlite3."""

    def __init__(self, conn):
        self._c = conn

    def execute(self, sql, params=()):
        sql_pg = _traduire(sql)
        table = _table_insert(sql_pg)
        veut_id = (
            table is not None
            and table not in _SANS_ID
            and " RETURNING " not in sql_pg.upper()
            and " ON CONFLICT" not in sql_pg.upper()
        )
        if veut_id:
            sql_pg = sql_pg.rstrip().rstrip(";") + " RETURNING id"

        cur = self._c.cursor()
        cur.execute(sql_pg, tuple(params) if params else None)

        dernier = None
        if veut_id:
            try:
                ligne = cur.fetchone()
                if ligne is not None:
                    dernier = ligne["id"] if isinstance(ligne, dict) else ligne[0]
            except Exception:
                pass
        return _Curseur(cur, dernier)

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()

    def close(self):
        self._c.close()


@contextlib.contextmanager
def ouvrir(chemin_sqlite: Path):
    """Le même contrat que l'ancien `db()` : on entre, on écrit, ça commit."""
    if not IS_PG:
        c = sqlite3.connect(chemin_sqlite, timeout=30)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()
        return

    import psycopg
    from psycopg.rows import dict_row

    brut = psycopg.connect(DSN, row_factory=dict_row, connect_timeout=15)
    conn = _ConnexionPG(brut)
    try:
        # search_path : toutes les tables vivent dans « naff », donc aucune
        # requête du serveur n'a besoin d'être préfixée.
        brut.cursor().execute(f"SET search_path TO {SCHEMA}, public")
        yield conn
        conn.commit()
    except Exception:
        try:
            conn.rollback()   # sans ça, la transaction reste empoisonnée
        except Exception:
            pass
        raise
    finally:
        conn.close()


def etat() -> str:
    if not IS_PG:
        return "SQLite (fichier local)"
    hote = DSN.split("@")[-1].split("/")[0] if "@" in DSN else "?"
    return f"PostgreSQL {hote} · schéma {SCHEMA}"
