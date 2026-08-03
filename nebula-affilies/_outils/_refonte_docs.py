# -*- coding: utf-8 -*-
"""
Remplace les trois mécanismes qui fabriquaient la zone Documents.

CE QU'IL Y AVAIT (et pourquoi ça n'allait pas)
  1. `_SEED_DOCS` + `seed_content()` : 5 notes écrites en dur dans le code,
     insérées si la table est vide.
  2. `refresh_seeded_docs()` : réécrivait ces mêmes 5 notes à CHAQUE démarrage.
  3. `seed_docs()` : recopiait 2 PDF du dépôt vers `UP_DIR`, le disque de Render.
     Ce disque s'efface à chaque déploiement : les deux PDF étaient donc
     référencés en base mais introuvables. On clique, il ne se passe rien.

  Résultat pour le partenaire : 7 entrées, dont 2 mortes, et aucun rapport avec
  les documents réellement écrits pour la force de vente.

CE QU'ON MET
  Un seul mécanisme, `publier_documents()`, qui pose les 9 documents que tout
  partenaire doit avoir — les vrais PDF, ceux du dossier de vente — **dans la
  base, en base64**, comme les photos. Ils survivent donc au déploiement.

  Il est idempotent (il compare une version et ne réécrit que si elle change),
  il retire ce qu'il a lui-même posé et qui ne fait plus partie de la liste, et
  il **ne touche jamais** à un document ajouté à la main depuis le cockpit.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_refonte_docs.py
"""
import io, sys

CIBLE = r"C:/Users/USER/nebula-agency/nebula-affilies/server.py"

NOUVEAU = '''
# ---------------------------------------------------------------------------
# La bibliothèque de documents des partenaires.
#
# Rangée DANS LA BASE, en base64, et non sur le disque : le disque de Render
# s'efface à chaque déploiement, et c'est précisément pour cela que les anciens
# PDF étaient référencés en base mais ne s'ouvraient plus.
#
# Pour publier une nouvelle version d'un document : remplacer le fichier dans
# assets/docs-partenaires/ et changer sa VERSION ci-dessous.
# ---------------------------------------------------------------------------
DOCS_PARTENAIRES = [
    ("02-MANUEL-DU-PARTENAIRE.pdf", "2026-08-03", "Le manuel du partenaire", "Formation",
     "Ton métier de A à Z : trouver des commerçants, présenter, relancer, être payé. À lire en premier."),
    ("09-CONTRAT-PARTENAIRE.pdf", "2026-08-03", "Ton contrat de partenaire", "Juridique",
     "À imprimer, signer, scanner et renvoyer. Il dit ce que NEBULA te doit et ce que tu dois à NEBULA."),
    ("03-GUIDE-CATALOGUE.pdf", "2026-08-03", "Vendre le Catalogue (50 000 F)", "Produits",
     "Ton offre d'entrée, celle qui se vend le plus facilement. Commence toujours par elle."),
    ("04-GUIDE-VITRINE.pdf", "2026-08-03", "Vendre la Vitrine (150 000 F)", "Produits",
     "La deuxième marche. Elle se vend presque seule à un client déjà content de son catalogue."),
    ("05-GUIDE-OUTIL-METIER.pdf", "2026-08-03", "Vendre l'Outil sur mesure", "Produits",
     "Pour les commerces qui ont un vrai besoin de gestion. De 55 000 à 500 000 F."),
    ("06-ARSENAL-SCRIPTS.pdf", "2026-08-03", "Tous les messages prêts à envoyer", "Vente",
     "Premier contact, relance, réponse aux objections. À copier, coller, envoyer."),
    ("12-GUIDE-DES-APPELS.pdf", "2026-08-03", "Au téléphone", "Vente",
     "Au téléphone on ne vend jamais : on décroche le rendez-vous. Voilà comment."),
    ("08-DIAGNOSTIC-DIGITAL.pdf", "2026-08-03", "La visite chez le commerçant", "Vente",
     "Les questions à poser chez le client pour repérer ce dont il a vraiment besoin."),
    ("01b-ANNONCE-PUBLIQUE.pdf", "2026-08-03", "L'annonce à partager", "Marketing",
     "Le texte à publier pour recruter quelqu'un dans ton équipe."),
]

# Les 7 entrées de l'ancienne bibliothèque, retirées une bonne fois (elles
# n'existent plus nulle part ailleurs, y compris chez les partenaires).
DOCS_RETIRES = [
    "Guide de démarrage du partenaire",
    "Catalogue Digital + QR — ton arme d'entrée",
    "Vitrine Digitale + QR — après ta 1re vente livrée",
    "Répondre aux objections",
    "Tes commissions expliquées",
    "Brochure du Programme Partenaires (PDF premium)",
    "Kit NEBULA — l'essentiel du partenaire (PDF)",
]


def publier_documents():
    """Pose les documents des partenaires en base. Idempotent.

    Ne touche jamais aux documents ajoutés à la main depuis le cockpit : seuls
    ceux marqués `url = 'nebula:socle'` appartiennent à cette fonction.
    """
    now = time.time()
    attendus = {}
    for fkey, version, title, cat, desc in DOCS_PARTENAIRES:
        src = HERE / "assets" / "docs-partenaires" / fkey
        if not src.exists():
            print("publier_documents: fichier absent,", fkey)
            continue
        attendus[title] = (src, version, cat, desc)

    try:
        with db() as c:
            # 1. l'ancienne bibliothèque s'en va
            for t in DOCS_RETIRES:
                c.execute("DELETE FROM documents WHERE title=?", (t,))

            # 2. ce que cette fonction avait posé et qui n'est plus au programme
            for r in c.execute("SELECT id, title FROM documents WHERE url=?", ("nebula:socle",)).fetchall():
                if r["title"] not in attendus:
                    c.execute("DELETE FROM documents WHERE id=?", (r["id"],))

            # 3. les documents du jour
            for title, (src, version, cat, desc) in attendus.items():
                marque = version                      # la version tient lieu d'empreinte
                row = c.execute("SELECT id, filename FROM documents WHERE title=?", (title,)).fetchone()
                if row and row["filename"] == marque:
                    continue                          # déjà à jour, on ne relit pas le fichier
                data = src.read_bytes()
                corps = "data:application/pdf;base64," + base64.b64encode(data).decode("ascii")
                if row:
                    c.execute("UPDATE documents SET category=?,description=?,kind='pdf',body=?,"
                              "url=?,filename=?,size=?,updated=? WHERE id=?",
                              (cat, desc, corps, "nebula:socle", marque, len(data), now, row["id"]))
                else:
                    c.execute("INSERT INTO documents(title,category,description,kind,body,url,filename,size,updated,created) "
                              "VALUES(?,?,?,'pdf',?,?,?,?,?,?)",
                              (title, cat, desc, corps, "nebula:socle", marque, len(data), now, now))
    except Exception as e:
        print("publier_documents:", e)

'''


def main():
    h = io.open(CIBLE, encoding="utf-8").read()
    if "def publier_documents()" in h:
        print("  Déjà fait.")
        return 0
    L = h.split("\n")

    # 1. la liste de notes en dur
    deb = next(i for i, l in enumerate(L) if l.startswith("# Documents de démarrage du back-office partenaires."))
    fin = next(i for i, l in enumerate(L) if i > deb and l.rstrip() == "]")
    print(f"  - _SEED_DOCS (5 notes en dur)          : {fin - deb + 1} lignes")
    L = L[:deb] + L[fin + 1:]

    # 2. refresh_seeded_docs + seed_docs, jusqu'à `def seed():`
    deb = next(i for i, l in enumerate(L) if l.startswith("def refresh_seeded_docs()"))
    # Ne remonter que sur les lignes vides qui la précèdent, rien d'autre :
    # une marche arrière « tant que c'est indenté » avale la fonction du dessus.
    while deb > 0 and L[deb - 1].strip() == "":
        deb -= 1
    fin = next(i for i, l in enumerate(L) if i > deb and l.startswith("def seed():"))
    print(f"  - refresh_seeded_docs + seed_docs       : {fin - deb} lignes")
    L = L[:deb] + NOUVEAU.split("\n") + L[fin:]

    h = "\n".join(L)

    # 3. les appels au démarrage
    for vieux, neuf in (
        ("refresh_seeded_docs()   # corrige les documents de démarrage déjà en base (idempotent)\nseed_docs()",
         "publier_documents()     # les 9 documents des partenaires, en base (idempotent)"),
    ):
        assert vieux in h, "appels de démarrage introuvables"
        h = h.replace(vieux, neuf, 1)

    # 4. la branche « documents » de seed_content()
    vieux = '''        if not c.execute("SELECT COUNT(*) n FROM documents").fetchone()["n"]:
            docs = _SEED_DOCS
            for t, cat, desc, body in docs:
                c.execute("INSERT INTO documents(title,category,description,kind,body,updated,created) VALUES(?,?,?,'note',?,?,?)",
                          (t, cat, desc, body, now, now))
'''
    assert vieux in h, "branche documents de seed_content introuvable"
    h = h.replace(vieux, "", 1)

    reste = h.count("_SEED_DOCS") + h.count("refresh_seeded_docs") + h.count("seed_docs")
    assert reste == 0, f"il reste {reste} référence(s) à l'ancien mécanisme"

    import ast
    ast.parse(h)
    io.open(CIBLE, "w", encoding="utf-8", newline="").write(h)
    print("  ✓ un seul mécanisme : publier_documents(), 9 PDF rangés en base")
    return 0


if __name__ == "__main__":
    sys.exit(main())
