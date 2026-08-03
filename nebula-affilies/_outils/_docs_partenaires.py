# -*- coding: utf-8 -*-
"""
Remet à plat la bibliothèque de documents des partenaires.

CE QUI NE VA PAS AUJOURD'HUI
  · 7 entrées mélangées : 5 notes écrites à la main et 2 PDF dont les fichiers
    ont **déjà disparu** avec le disque de Render. On clique, il ne se passe rien.
  · Aucun rapport avec les documents réellement écrits depuis (manuel, guides
    par service, arsenal de scripts, guide des appels, contrat).

CE QU'ON MET À LA PLACE
  Les 9 documents que **tout partenaire doit avoir**, en PDF, téléchargeables et
  imprimables. Le contrat en fait partie : il doit pouvoir être imprimé, signé,
  scanné et renvoyé.

  Volontairement EXCLUS, ce sont des documents internes :
    · 00-SOCLE-COMMERCIAL (les décisions et les marges de NEBULA)
    · 01-AVIS-DE-RECRUTEMENT (le dossier interne de sélection)

COMMENT ILS SONT STOCKÉS
  **Dans la base, en base64**, comme les photos depuis ce matin. Le disque de
  Render s'efface à chaque déploiement : c'est exactement pour ça que les deux
  PDF actuels ne s'ouvrent plus.

    python nebula-affilies/_outils/_docs_partenaires.py            # montre
    python nebula-affilies/_outils/_docs_partenaires.py --ecrire   # remplace
"""
import base64, io, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency")
VERSION = "2026-08-03"   # doit rester identique a celle de DOCS_PARTENAIRES dans server.py
PDF = RACINE / "_documents/nebula-agency/vente/pdf"

# (fichier, titre affiché, catégorie, description — dite comme un partenaire la dirait)
DOCS = [
    ("02-MANUEL-DU-PARTENAIRE.pdf", "Le manuel du partenaire", "Formation",
     "Ton métier de A à Z : trouver des commerçants, présenter, relancer, être payé. À lire en premier."),
    ("09-CONTRAT-PARTENAIRE.pdf", "Ton contrat de partenaire", "Juridique",
     "À imprimer, signer, scanner et renvoyer. Il dit ce que NEBULA te doit et ce que tu dois à NEBULA."),
    ("03-GUIDE-CATALOGUE.pdf", "Vendre le Catalogue (50 000 F)", "Produits",
     "Ton offre d'entrée, celle qui se vend le plus facilement. Commence toujours par elle."),
    ("04-GUIDE-VITRINE.pdf", "Vendre la Vitrine (150 000 F)", "Produits",
     "La deuxième marche. Elle se vend presque seule à un client déjà content de son catalogue."),
    ("05-GUIDE-OUTIL-METIER.pdf", "Vendre l'Outil sur mesure", "Produits",
     "Pour les commerces qui ont un vrai besoin de gestion. De 55 000 à 500 000 F."),
    ("06-ARSENAL-SCRIPTS.pdf", "Tous les messages prêts à envoyer", "Vente",
     "Premier contact, relance, réponse aux objections. À copier, coller, envoyer."),
    ("12-GUIDE-DES-APPELS.pdf", "Au téléphone", "Vente",
     "Au téléphone on ne vend jamais : on décroche le rendez-vous. Voilà comment."),
    ("08-DIAGNOSTIC-DIGITAL.pdf", "La visite chez le commerçant", "Vente",
     "Les questions à poser chez le client pour repérer ce dont il a vraiment besoin."),
    ("01b-ANNONCE-PUBLIQUE.pdf", "L'annonce à partager", "Marketing",
     "Le texte à publier pour recruter quelqu'un dans ton équipe."),
]


def main():
    ecrire = "--ecrire" in sys.argv
    env = RACINE / "secrets/supabase.env"
    dsn = next((l.split("=", 1)[1].strip() for l in io.open(env, encoding="utf-8")
                if l.startswith("DATABASE_URL=")), None)
    if not dsn:
        print("  DATABASE_URL introuvable"); return 1

    lignes, total = [], 0
    for f, titre, cat, desc in DOCS:
        p = PDF / f
        if not p.exists():
            print(f"  MANQUE : {f}"); return 1
        data = p.read_bytes()
        total += len(data)
        lignes.append((titre, cat, desc, "data:application/pdf;base64," + base64.b64encode(data).decode("ascii"), len(data)))
        print(f"  {titre:38} {len(data)//1024:>4} Ko  ({f})")
    print(f"  ---\n  {len(lignes)} documents, {total//1024} Ko, soit {int(total*1.34)//1024} Ko une fois en base")

    if not ecrire:
        print("\n  Rien n'a été modifié. Pour remplacer la bibliothèque :")
        print("      python nebula-affilies/_outils/_docs_partenaires.py --ecrire")
        return 0

    import psycopg
    from psycopg.rows import dict_row
    import time
    with psycopg.connect(dsn, row_factory=dict_row) as c:
        c.execute("SET search_path TO naff, public")
        anciens = c.execute("select count(*) n from documents").fetchone()["n"]
        c.execute("DELETE FROM documents")
        # Exactement ce que pose `publier_documents()` au demarrage du serveur :
        # url = 'nebula:socle' (ce qui appartient au socle), filename = la version.
        # Ainsi, au prochain redemarrage, le serveur voit que c'est deja a jour
        # et ne rejoue rien.
        for titre, cat, desc, b64, taille in lignes:
            c.execute("""INSERT INTO documents(title,category,description,kind,body,url,filename,size,updated,created)
                         VALUES(%s,%s,%s,'pdf',%s,'nebula:socle',%s,%s,%s,%s)""",
                      (titre, cat, desc, b64, VERSION, taille, time.time(), time.time()))
        c.commit()
        n = c.execute("select count(*) n from documents").fetchone()["n"]
    print(f"\n  {anciens} ancien(s) document(s) supprimé(s), {n} en place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
