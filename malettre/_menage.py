# -*- coding: utf-8 -*-
"""MA LETTRE À… · le ménage des lettres expirées, chaque nuit (2026-10-21).

    python malettre/_menage.py            (DATABASE_URL dans l'environnement)

Appelé par `.github/workflows/malettre-menage.yml`, à 03 h 30 UTC. Il appelle
`public.malettre_menage()` (`supabase/lettres.sql`) : une lettre dont la durée
en ligne est passée perd ses données (le mot, les photos), la ligne reste pour
que son adresse réponde « Cette lettre a expiré » et pas « n'existe pas ».

⛔ Rien d'autre : il ne lit aucune lettre, n'écrit à personne, ne supprime aucune
ligne. Tant que la caisse n'est pas branchée (la fonction n'existe pas encore
dans la base), il le dit et sort sans erreur : un ménage qui échoue chaque nuit
avant le lancement finirait par ne plus être regardé.
"""
import os
import sys


def main() -> int:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        print("Aucune base donnée (secret MALETTRE_DATABASE_URL ou PISTE_DATABASE_URL). Rien à faire.")
        return 0
    import psycopg
    # ⚠️ prepare_threshold=None : obligatoire avec le pooler Supabase (port 6543).
    with psycopg.connect(url, prepare_threshold=None, autocommit=True, connect_timeout=30) as c:
        existe = c.execute("select to_regprocedure('public.malettre_menage()') is not null").fetchone()[0]
        if not existe:
            print("La caisse n'est pas encore branchée (malettre_menage absente) : rien à faire.")
            return 0
        n = c.execute("select public.malettre_menage()").fetchone()[0]
        print(f"Ménage : {n} lettre(s) expirée(s) vidée(s) de leurs données.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
