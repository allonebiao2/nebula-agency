# -*- coding: utf-8 -*-
"""
Contrôle de la base PostgreSQL du bureau des partenaires.

Lit DATABASE_URL depuis secrets/supabase.env (ignoré par git), se connecte,
et vérifie que le schéma est complet et utilisable. N'écrit rien de définitif :
le test d'écriture crée une ligne puis l'annule.

    python nebula-affilies/_verif_pg.py
"""
import io, os, sys, time
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency")
ENVF = RACINE / "secrets" / "supabase.env"

TABLES = ["affiliates", "leads", "history", "notifs", "brain_msgs", "agency_chats",
          "recruits", "candidatures", "commissions", "subscriptions", "documents",
          "publications", "messages", "chat_reads", "app_settings", "link_events"]


def dsn():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"].strip()
    if not ENVF.exists():
        print(f"⛔ fichier introuvable : {ENVF}")
        print("   Y mettre une ligne : DATABASE_URL=postgresql://...")
        sys.exit(2)
    for ligne in io.open(ENVF, encoding="utf-8"):
        ligne = ligne.strip()
        if ligne.startswith("DATABASE_URL="):
            return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    print("⛔ pas de ligne DATABASE_URL dans le fichier")
    sys.exit(2)


def main():
    import psycopg
    from psycopg.rows import dict_row

    d = dsn()
    hote = d.split("@")[-1].split("/")[0] if "@" in d else "?"
    print(f"  connexion → {hote}")

    try:
        conn = psycopg.connect(d, row_factory=dict_row, connect_timeout=20)
    except Exception as e:
        print(f"⛔ connexion impossible : {type(e).__name__} : {str(e)[:220]}")
        print("   Vérifier : le mot de passe, et que c'est bien l'URI « Transaction pooler » (port 6543).")
        sys.exit(1)

    ok = True
    with conn:
        cur = conn.cursor()

        # 1. le schéma existe-t-il ?
        cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name='naff'")
        if not cur.fetchone():
            print("⛔ le schéma « naff » n'existe pas : le fichier schema_pg.sql n'a pas été exécuté.")
            sys.exit(1)
        print("  ✓ schéma « naff » présent")

        # 2. les 16 tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='naff' ORDER BY 1")
        vues = [r["table_name"] for r in cur.fetchall()]
        manquantes = [t for t in TABLES if t not in vues]
        print(f"  {'✓' if not manquantes else '⛔'} tables : {len(vues)} trouvées sur {len(TABLES)} attendues")
        if manquantes:
            print("     manquantes :", ", ".join(manquantes)); ok = False
        for extra in [t for t in vues if t not in TABLES]:
            print("     (en plus :", extra + ")")

        # 3. le piège des dates : REAL arrondirait les horodatages
        cur.execute("""SELECT table_name, column_name, data_type FROM information_schema.columns
                       WHERE table_schema='naff' AND data_type='real'""")
        reels = cur.fetchall()
        if reels:
            print(f"  ⛔ {len(reels)} colonne(s) en REAL (4 octets) : les dates seraient arrondies")
            for r in reels[:6]: print(f"     {r['table_name']}.{r['column_name']}")
            ok = False
        else:
            print("  ✓ aucune colonne en REAL : les horodatages sont en double precision")

        # 4. l'identité auto sur les tables à id
        cur.execute("""SELECT table_name FROM information_schema.columns
                       WHERE table_schema='naff' AND column_name='id' AND is_identity='YES'""")
        idents = {r["table_name"] for r in cur.fetchall()}
        attendu = {t for t in TABLES if t not in ("chat_reads", "app_settings")}
        print(f"  {'✓' if attendu <= idents else '⛔'} identité automatique sur {len(idents)} tables")
        if not attendu <= idents:
            print("     sans identité :", ", ".join(sorted(attendu - idents))); ok = False

        # 5. écriture réelle, puis annulation
        cur.execute("SET search_path TO naff, public")
        try:
            cur.execute("INSERT INTO affiliates(code,nom,pin,created) VALUES(%s,%s,%s,%s) RETURNING id",
                        ("__TEST__", "controle", "x", time.time()))
            rid = cur.fetchone()["id"]
            cur.execute("SELECT created FROM affiliates WHERE id=%s", (rid,))
            t = cur.fetchone()["created"]
            precis = abs(t - time.time()) < 5
            print(f"  {'✓' if precis else '⛔'} écriture + relecture (id={rid}), horodatage {'exact' if precis else 'DÉCALÉ'}")
            ok = ok and precis
        except Exception as e:
            print(f"  ⛔ écriture impossible : {type(e).__name__} : {str(e)[:200]}"); ok = False
        finally:
            conn.rollback()   # rien n'est conservé

        cur.execute("SELECT count(*) n FROM naff.affiliates")
        print(f"  · partenaires actuellement en base : {cur.fetchone()['n']}")

    print("\n" + ("  TOUT EST VERT. La base est prête pour Render." if ok else "  DES POINTS À CORRIGER (voir ci-dessus)."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
