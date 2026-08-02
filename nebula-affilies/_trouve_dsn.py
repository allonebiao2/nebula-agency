# -*- coding: utf-8 -*-
"""
Reconstruit la chaîne de connexion Supabase à partir du seul mot de passe.

Tout est connu sauf deux choses : la région du pooler, et le mot de passe.
Le mot de passe vient de secrets/supabase.env, la région est trouvée en
essayant les régions Supabase une par une jusqu'à ce que l'une réponde.

Écrit ensuite DATABASE_URL dans le même fichier, pour que la suite de la
chaîne (contrôle, Render) n'ait plus à s'en occuper.
"""
import io, sys
from pathlib import Path

REF = "xukduhqqfzogisoimhyo"          # référence du projet Supabase (publique)
ENVF = Path(r"C:/Users/USER/nebula-agency/secrets/supabase.env")

# Les régions Supabase les plus probables d'abord (projet créé depuis l'Afrique
# de l'Ouest : l'Europe est le choix par défaut le plus fréquent).
REGIONS = ["eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-2",
           "us-east-1", "us-east-2", "us-west-1", "us-west-2",
           "ap-southeast-1", "ap-southeast-2", "ap-south-1", "ap-northeast-1",
           "ca-central-1", "sa-east-1"]


def lire_env():
    if not ENVF.exists():
        print(f"⛔ fichier introuvable : {ENVF}"); sys.exit(2)
    vals = {}
    for ligne in io.open(ENVF, encoding="utf-8"):
        ligne = ligne.strip()
        if ligne.startswith("#") or "=" not in ligne:
            continue
        k, v = ligne.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def dsn_pour(region, mdp):
    return (f"postgresql://postgres.{REF}:{mdp}"
            f"@aws-0-{region}.pooler.supabase.com:6543/postgres")


def main():
    vals = lire_env()

    if vals.get("DATABASE_URL") and "REGION" not in vals["DATABASE_URL"] \
       and "colle-ici" not in vals["DATABASE_URL"]:
        print("  DATABASE_URL déjà renseignée, rien à reconstruire.")
        return 0

    mdp = vals.get("DB_PASSWORD", "")
    if not mdp or "colle-ici" in mdp:
        print("⛔ Le mot de passe n'est pas encore dans secrets/supabase.env.")
        print("   Remplacer la ligne DB_PASSWORD=colle-ici-ton-mot-de-passe")
        sys.exit(2)

    import psycopg
    print(f"  mot de passe lu ({len(mdp)} caractères). Recherche de la région…")

    trouvee = None
    for r in REGIONS:
        d = dsn_pour(r, mdp)
        try:
            with psycopg.connect(d, connect_timeout=8) as c:
                c.execute("SELECT 1")
            trouvee = r
            print(f"  ✓ région trouvée : {r}")
            break
        except Exception as e:
            msg = str(e).lower()
            if "password authentication failed" in msg:
                # bonne région, mauvais mot de passe : inutile de continuer
                print(f"  ⛔ région {r} : le serveur répond, mais le mot de passe est refusé.")
                print("     Le reste de la chaîne est bon : c'est le mot de passe qu'il faut revoir.")
                sys.exit(1)
            print(f"    {r} : non ({type(e).__name__})")

    if not trouvee:
        print("⛔ aucune région n'a répondu. Vérifier le mot de passe, ou récupérer la")
        print("   chaîne complète via le bouton « Connect » du tableau de bord Supabase.")
        sys.exit(1)

    d = dsn_pour(trouvee, mdp)
    contenu = io.open(ENVF, encoding="utf-8").read()
    if "DATABASE_URL=" in contenu:
        lignes = [l for l in contenu.splitlines()
                  if not (l.strip().startswith("DATABASE_URL=") and "REGION" not in l)]
        contenu = "\n".join(lignes)
    contenu = contenu.rstrip() + f"\n\nDATABASE_URL={d}\n"
    io.open(ENVF, "w", encoding="utf-8", newline="").write(contenu)

    print(f"  ✓ DATABASE_URL écrite dans {ENVF.name}")
    print(f"    hôte : aws-0-{trouvee}.pooler.supabase.com:6543")
    return 0


if __name__ == "__main__":
    sys.exit(main())
