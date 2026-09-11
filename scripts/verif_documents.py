# -*- coding: utf-8 -*-
"""
verif_documents.py — ce que les partenaires téléchargent VRAIMENT.

    python scripts/verif_documents.py

Le bureau des partenaires range ses PDF dans la base (`naff.documents`, en
base64). `publier_documents()` ne les y pose qu'au DÉMARRAGE du service, et
seulement si leur date a changé dans `DOCS_PARTENAIRES` (server.py).

⛔ 2026-09-11 : trois sessions avaient bumpé des dates, aucune n'avait
   redéployé Render. La base portait encore les dix PDF du 3 août, et le
   contrat servi aux partenaires était l'ancien. Le code disait l'intention,
   la base disait la vérité. Ce script lit la base.

Pour chaque document attendu : la version en base est-elle celle du code, et
les octets en base sont-ils ceux du fichier du dépôt ? Une version à jour avec
des octets différents arrive quand seule l'étiquette du PDF a changé (le TEXTE
se compare à part, voir `_memoire/apprentissages/2026-09-11-prouver-une-publication.md`).
Une version en retard n'est jamais normale.

Sortie 0 si toutes les versions concordent, 1 sinon.
"""
import ast
import base64
import hashlib
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVEUR = os.path.join(RACINE, "nebula-affilies", "server.py")
DOCS = os.path.join(RACINE, "nebula-affilies", "assets", "docs-partenaires")
SECRETS = os.path.join(RACINE, "secrets", "supabase.env")
RENDER = "https://api.render.com/v1/services/srv-d9nni7e7bikc73c9oksg/deploys"


def attendus():
    """Lit DOCS_PARTENAIRES dans server.py sans l'exécuter."""
    code = open(SERVEUR, encoding="utf-8").read()
    debut = code.index("DOCS_PARTENAIRES = [")
    fin = code.index("\n]\n", debut) + 2
    liste = ast.literal_eval(code[debut:fin].split("=", 1)[1].strip())
    return {titre: (fichier, version) for fichier, version, titre, _cat, _desc in liste}


def url_base():
    for ligne in open(SECRETS, encoding="utf-8"):
        m = re.match(r"\s*DATABASE_URL\s*=\s*(.*)", ligne)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    sys.exit("⛔ DATABASE_URL absent de secrets/supabase.env")


def main():
    # ⚠️ console Windows en cp1252 : sans ça, le premier ✅ fait planter le script
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        import psycopg
    except ImportError:
        sys.exit("⛔ il manque psycopg : pip install \"psycopg[binary]\"")

    voulu = attendus()
    # ⚠️ prepare_threshold=None : obligatoire avec le pooler Supabase (port 6543)
    with psycopg.connect(url_base(), prepare_threshold=None) as cx:
        lignes = cx.execute(
            "select title, filename, body from naff.documents where url = 'nebula:socle'"
        ).fetchall()
    en_base = {titre: (version, corps) for titre, version, corps in lignes}

    retard = 0
    for titre, (fichier, version) in voulu.items():
        if titre not in en_base:
            retard += 1
            print(u"  ⛔ %-38s ABSENT de la base" % titre[:38])
            continue
        v, corps = en_base[titre]
        disque = open(os.path.join(DOCS, fichier), "rb").read()
        octets = base64.b64decode(corps.split(",", 1)[1]) if corps and "," in corps else b""
        meme = hashlib.md5(octets).digest() == hashlib.md5(disque).digest()
        if v != version:
            retard += 1
            print(u"  ⛔ %-38s base %s, code %s" % (titre[:38], v, version))
        elif meme:
            print(u"  ✅ %-38s %s  identique au dépôt" % (titre[:38], v))
        else:
            print(u"  ✅ %-38s %s  ⚠️ octets ≠ dépôt : bumper si le TEXTE a changé"
                  % (titre[:38], v))
    for titre in sorted(set(en_base) - set(voulu)):
        print(u"  ⚠️  %-38s en base mais plus au programme" % titre[:38])

    print()
    if retard:
        print(u"  ⛔ %d document(s) en retard sur le code. Redéployer Render :" % retard)
        print(u"     POST %s   (clé : secrets/render.env)" % RENDER)
        sys.exit(1)
    print(u"  ✅ les %d documents servis aux partenaires sont ceux du code." % len(voulu))


if __name__ == "__main__":
    main()
