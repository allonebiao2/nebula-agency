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
import os, re, sqlite3, contextlib, threading, contextvars
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


# ---------------------------------------------------------------------------
# Une seule connexion par requête, et pas une par appel de fonction.
#
# Mesuré le 2026-08-03 : ouvrir une connexion vers Supabase coûte **1,3 s**
# (7 s la première, poignée de main TLS comprise). Sur SQLite c'était de l'ordre
# de la microseconde, donc le code appelait `db()` librement, y compris dans des
# fonctions imbriquées.
#
# Conséquence après la migration : `/api/admin/affiliates` ouvrait 1 connexion
# pour la liste, puis 2 par partenaire (statistiques + gains). Neuf connexions
# pour 4 partenaires, soit ~12 s — et ça grandit avec le réseau. La page
# attendait sans jamais rien afficher : l'écran noir.
#
# Le remède, en deux temps :
#   1. `ouvrir()` devient RÉENTRANT : un `with` imbriqué réutilise la connexion
#      déjà ouverte au lieu d'en créer une.
#   2. `requete()` tient une connexion pour TOUTE la durée d'une requête HTTP.
#      Sans cela, la réentrance ne suffit pas : le code fait souvent
#      `with db(): lire la liste`, PUIS boucle en dehors du bloc, donc la
#      connexion est déjà refermée. Ce motif se répète à douze endroits ; les
#      corriger un par un serait long et risqué. Une connexion par requête les
#      répare tous, sans toucher à un seul appel.
#
# On utilise un ContextVar et non un thread-local : Starlette exécute les
# fonctions synchrones dans un fil séparé, mais il RECOPIE le contexte, donc la
# connexion suit la requête jusque dans ce fil.
# ---------------------------------------------------------------------------
_porteur = contextvars.ContextVar("naff_conn", default=None)
_local = threading.local()   # repli hors requête HTTP (démarrage, scripts, cron)


@contextlib.contextmanager
def requete(chemin_sqlite: Path):
    """Une seule connexion pour toute la requête, ouverte à la première lecture.

    Si la requête ne touche jamais la base (fichier statique, page publique),
    aucune connexion n'est ouverte : on ne paie que ce qu'on utilise.
    """
    porteur = {"conn": None, "brut": None}
    jeton = _porteur.set(porteur)
    try:
        yield
        c = porteur["conn"]
        if c is not None:
            c.commit()
    except Exception:
        c = porteur["conn"]
        if c is not None:
            try:
                c.rollback()
            except Exception:
                pass
        raise
    finally:
        _porteur.reset(jeton)
        c = porteur["conn"]
        if c is not None:
            try:
                c.close()
            except Exception:
                pass


def _ouvrir_brut(chemin_sqlite: Path):
    """Ouvre une connexion neuve, SQLite ou PostgreSQL selon la configuration."""
    if not IS_PG:
        c = sqlite3.connect(chemin_sqlite, timeout=30)
        c.row_factory = sqlite3.Row
        return c
    import psycopg
    from psycopg.rows import dict_row
    brut = psycopg.connect(DSN, row_factory=dict_row, connect_timeout=15)
    # ⚠️ INDISPENSABLE avec le pooler de Supabase (port 6543, mode transaction).
    # psycopg3 « prépare » automatiquement une requête après 5 exécutions, pour
    # aller plus vite. Mais le pooler multiplexe les connexions : la requête
    # préparée sur un serveur n'existe pas sur le suivant, et on obtient
    #     DuplicatePreparedStatement: prepared statement "_pg3_0" already exists
    # Le bug n'apparaît qu'au-delà de 5 exécutions de la MÊME requête sur une
    # connexion : il est donc resté invisible tant qu'on ouvrait une connexion
    # par appel, et il est sorti dès qu'on a commencé à les réutiliser.
    brut.prepare_threshold = None
    conn = _ConnexionPG(brut)
    # search_path : toutes les tables vivent dans « naff », donc aucune requête
    # du serveur n'a besoin d'être préfixée.
    brut.cursor().execute(f"SET search_path TO {SCHEMA}, public")
    return conn


@contextlib.contextmanager
def ouvrir(chemin_sqlite: Path):
    """Le même contrat que l'ancien `db()` : on entre, on écrit, ça commit.

    Réentrant, et adossé à la connexion de la requête quand il y en a une.
    """
    # 1. une requête HTTP est en cours : on lui emprunte sa connexion
    porteur = _porteur.get()
    if porteur is not None:
        if porteur["conn"] is None:
            porteur["conn"] = _ouvrir_brut(chemin_sqlite)
        yield porteur["conn"]      # ni commit ni close ici : `requete()` s'en charge
        return

    # 2. déjà dans une transaction sur ce fil : on prête la connexion en cours
    interne = getattr(_local, "conn", None)
    if interne is not None:
        _local.profondeur += 1
        try:
            yield interne
        finally:
            _local.profondeur -= 1
        return

    if not IS_PG:
        c = sqlite3.connect(chemin_sqlite, timeout=30)
        c.row_factory = sqlite3.Row
        _local.conn, _local.profondeur = c, 1
        try:
            yield c
            c.commit()
        finally:
            _local.conn, _local.profondeur = None, 0
            c.close()
        return

    import psycopg
    from psycopg.rows import dict_row

    brut = psycopg.connect(DSN, row_factory=dict_row, connect_timeout=15)
    brut.prepare_threshold = None     # cf. l'explication dans _ouvrir_brut
    conn = _ConnexionPG(brut)
    _local.conn, _local.profondeur = conn, 1
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
        _local.conn, _local.profondeur = None, 0
        conn.close()


def etat() -> str:
    if not IS_PG:
        return "SQLite (fichier local)"
    hote = DSN.split("@")[-1].split("/")[0] if "@" in DSN else "?"
    return f"PostgreSQL {hote} · schéma {SCHEMA}"
