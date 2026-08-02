# -*- coding: utf-8 -*-
"""
Branche server.py sur dbx.py (SQLite en local, PostgreSQL si DATABASE_URL).
Idempotent, UTF-8 strict. Ne touche à aucune des 219 requêtes.
"""
import io, sys

SRC = r"C:/Users/USER/nebula-agency/nebula-affilies/server.py"

ANCIEN_DB = '''@contextlib.contextmanager
def db():
    c = sqlite3.connect(DBF, timeout=30)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()

def init_db():
    with db() as c:
        c.execute("PRAGMA journal_mode=WAL")     # lecteurs + 1 écrivain concurrents'''

NOUVEAU_DB = '''@contextlib.contextmanager
def db():
    """SQLite en local, PostgreSQL (Supabase) si DATABASE_URL est posée.
    La traduction vit dans dbx.py : les requêtes du serveur ne changent pas."""
    with dbx.ouvrir(DBF) as c:
        yield c

def init_db():
    # Sur PostgreSQL, le schéma est posé UNE FOIS par schema_pg.sql (Supabase).
    # On ne crée donc rien au démarrage : pas de DDL SQLite à traduire à chaud.
    if dbx.IS_PG:
        return
    with db() as c:
        c.execute("PRAGMA journal_mode=WAL")     # lecteurs + 1 écrivain concurrents'''

ANCIEN_MIG = '''def migrate():
    with db() as c:
        for col, ddl in [("pseudo", "TEXT DEFAULT \'\'"), ("parrain_id", "INTEGER DEFAULT 0"), ("photo", "TEXT DEFAULT \'\'"),'''

NOUVEAU_MIG = '''def migrate():
    # Idem : sur PostgreSQL les colonnes sont déjà toutes dans schema_pg.sql.
    # Et surtout, le try/except de ce bloc est un piège en Postgres : un ALTER
    # qui échoue empoisonne toute la transaction, les suivants échouent aussi.
    if dbx.IS_PG:
        return
    with db() as c:
        for col, ddl in [("pseudo", "TEXT DEFAULT \'\'"), ("parrain_id", "INTEGER DEFAULT 0"), ("photo", "TEXT DEFAULT \'\'"),'''


def main():
    h = io.open(SRC, encoding="utf-8").read()
    avant = h

    if "import dbx" not in h:
        cible = "# ----------------------------------------------------------------------------\n# Base de données"
        assert h.count(cible) == 1, "ancre d'import introuvable"
        h = h.replace(cible, "import dbx\n\n" + cible, 1)
        print("  ✓ import dbx")

    for ancien, nouveau, nom in ((ANCIEN_DB, NOUVEAU_DB, "db() + init_db()"),
                                 (ANCIEN_MIG, NOUVEAU_MIG, "migrate()")):
        if nouveau.split("\n")[2] in h and "dbx.IS_PG" in h:
            pass
        if ancien in h:
            h = h.replace(ancien, nouveau, 1)
            print(f"  ✓ {nom}")
        elif "dbx.IS_PG" not in h:
            print(f"  ⚠️  motif introuvable : {nom}")
            return 1

    if h == avant:
        print("Aucun changement : déjà branché.")
        return 0

    io.open(SRC, "w", encoding="utf-8", newline="").write(h)

    assert "dbx.ouvrir(DBF)" in h, "db() n'a pas été rebranché"
    assert h.count("if dbx.IS_PG:") == 2, "les deux gardes ne sont pas posées"
    print("  ✓ contrôles passés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
