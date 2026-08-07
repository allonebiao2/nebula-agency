#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — assemble la V4 dans `_vitrine_src.html`.

    python _v4/_assembler.py

Le fichier source est reconstruit à partir de six morceaux :

  1. la tête            — écrite ici (SEO, polices)
  2. style-page.css     — la V4, réécrite
  3. garde-css-modale   ⛔ REPRIS TEL QUEL de la V3
  4. garde-css-toucher  ⛔ REPRIS TEL QUEL de la V3
  5. markup.html        — la V4, réécrite
  6. garde-modale.html  ⛔ REPRIS TEL QUEL de la V3
  7. garde-moteur.js    ⛔ REPRIS TEL QUEL — le moteur de commande
  8. motion.js          — la V4, réécrite

⛔ Les quatre morceaux « garde » ne sont JAMAIS régénérés. Le moteur de
   commande (mesures par type de vêtement, date de disponibilité, message
   WhatsApp) est la seule partie du site qui rapporte : la refonte ne le
   touche pas. Si la V4 casse le moteur, elle est refusée.

Une sauvegarde de l'ancien source est écrite dans `_v4/_avant-v4.html`.
"""
import io, os, sys, re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SRC = os.path.join(RACINE, "_vitrine_src.html")

def lire(n):
    return io.open(os.path.join(ICI, n), encoding="utf-8").read().rstrip("\n")

TETE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>HILLARY M. STYL — Maison de couture · pagne, prêt-à-porter &amp; sur-mesure</title>
<meta name="description" content="HILLARY M. STYL, maison de couture à Cotonou. Pagne, wax et tous tissus. Prêt-à-porter par tailles et sur-mesure aux mesures exactes. Commande en ligne, retrait ou expédition, délai express en 1 à 3 jours.">
<meta name="theme-color" content="#0c0c0c">
<meta name="author" content="Hillary M. Styl">
<link rel="canonical" href="https://hillary-m-styl.pages.dev/">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="HILLARY M. STYL">
<meta property="og:title" content="HILLARY M. STYL — Maison de couture">
<meta property="og:url" content="https://hillary-m-styl.pages.dev/">
<meta property="og:description" content="Pagne, prêt-à-porter et sur-mesure. Donnez vos mesures, connaissez le jour exact où votre tenue sera prête.">
<link rel="icon" href="data:image/png;base64,__FAVICON_B64__">
<!-- ⚠️ LA PREMIERE PIECE DOIT PARTIR AVANT LE RESTE.
     Les mannequins du heros sont poses par le script : le navigateur ne peut
     donc pas les decouvrir en lisant le HTML, et la premiere photo n'etait
     demandee qu'une fois tout le reste charge. Mesure sur une 4G a 1,6 Mb/s :
     elle apparaissait a la NEUVIEME seconde, sur une page deja affichee, avec
     son chiffre geant et ses textes mais sans vetement. Ca ne ressemble pas a
     un site qui charge, ca ressemble a un site casse. -->
<link rel="preload" as="image" href="assets/images/hero-1.webp" fetchpriority="high">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;0,6..96,700;1,6..96,400;1,6..96,500&family=Archivo:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>"""

MILIEU = """</style>
</head>
<body>"""

JSON_LD = """
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"ClothingStore","@id":"https://hillary-m-styl.pages.dev/#maison","name":"HILLARY M. STYL","description":"Maison de couture à Cotonou : pagne, wax et tous tissus, prêt-à-porter par tailles et sur-mesure aux mesures exactes.","url":"https://hillary-m-styl.pages.dev/","telephone":"+22951374793","address":{"@type":"PostalAddress","addressLocality":"Cotonou","addressCountry":"BJ"},"areaServed":["BJ","TG","CI","NG"],"currenciesAccepted":"XOF","paymentAccepted":"Mobile Money"},
 {"@type":"WebSite","@id":"https://hillary-m-styl.pages.dev/#site","url":"https://hillary-m-styl.pages.dev/","name":"HILLARY M. STYL","inLanguage":"fr-FR","publisher":{"@id":"https://hillary-m-styl.pages.dev/#maison"}},
 {"@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":"Faites-vous du sur-mesure ?","acceptedAnswer":{"@type":"Answer","text":"Oui. Les mesures demandées dépendent du type de vêtement, pas du genre : une robe coupée à la taille en demande 9, une robe droite 15, un pantalon 6, une chemise 8. Une mesure que vous ne savez pas prendre se prend ensemble."}},
  {"@type":"Question","name":"En combien de temps ma tenue est-elle prête ?","acceptedAnswer":{"@type":"Answer","text":"De 7 à 14 jours en confection normale, de 1 à 3 jours en express. La date exacte de disponibilité s'affiche avant que vous ne validiez, acheminement compris."}},
  {"@type":"Question","name":"Comment se fait le règlement ?","acceptedAnswer":{"@type":"Answer","text":"Par Mobile Money uniquement. Aucun paiement ne se fait sur le site : la commande part sur WhatsApp et le règlement se convient directement."}},
  {"@type":"Question","name":"Travaillez-vous le pagne et le wax ?","acceptedAnswer":{"@type":"Answer","text":"Oui, comme tous les autres tissus. La maison fait le pagne, le wax, le bazin et la dentelle, en prêt-à-porter comme en sur-mesure."}}]}
]}
</script>"""

FIN = """
</body>
</html>"""


def main():
    # ⚠️ la sauvegarde ne se prend QU'UNE FOIS. Au deuxième passage, l'ancien
    #    source est déjà la V4 : l'écraser détruit la V3, seul endroit où lire
    #    le comportement d'origine. C'est arrivé le 2026-08-06, et il a fallu
    #    la récupérer par `git show HEAD:...`.
    if os.path.exists(SRC) and not os.path.exists(os.path.join(ICI, "_avant-v4.html")):
        io.open(os.path.join(ICI, "_avant-v4.html"), "w", encoding="utf-8", newline="\n") \
          .write(io.open(SRC, encoding="utf-8").read())
        print("  sauvegarde de l'ancien source -> _v4/_avant-v4.html")

    out = "\n".join([
        TETE,
        lire("style-page.css"),
        "",
        lire("garde-css-modale.css"),
        "",
        lire("garde-css-toucher.css"),
        MILIEU,
        "",
        lire("markup.html"),
        "",
        lire("garde-modale.html"),
        JSON_LD,
        "",
        "<script>",
        lire("garde-moteur.js"),
        "",
        lire("motion.js"),
        "</script>",
        FIN.lstrip("\n"),
    ])

    # --- contrôles avant écriture : le moteur doit être intact -------
    exiges = ["#adr", "#altMail", "#an", "#btWa", "#btX", "#catalogue", "#f_pays",
              "#f_type", "#grille", "#helloTxt", "#hor", "#mail", "#ov", "#shBd",
              "#shFt", "#shSub", "#shTitre", "#waBas"]
    manquants = [i for i in exiges
                 if ('id="' + i[1:] + '"') not in out]
    if manquants:
        raise SystemExit("⛔ identifiants absents du balisage : " + ", ".join(manquants))
    for m in ("var WHATSAPP", "MESURES", "function carte(", "data-onglet",
              '<div class="ov" id="ov"', "__LOGO_B64__", "__FAVICON_B64__"):
        if m not in out:
            raise SystemExit("⛔ morceau manquant : " + m)
    if out.count("<script>") != 1 or out.count("</script>") != 2:
        raise SystemExit("⛔ balises script mal comptées")

    io.open(SRC, "w", encoding="utf-8", newline="\n").write(out)
    print(f"  _vitrine_src.html reconstruit : {len(out)} caracteres, {out.count(chr(10))+1} lignes")
    print("  les 18 identifiants du moteur sont presents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
