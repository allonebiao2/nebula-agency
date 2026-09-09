# -*- coding: utf-8 -*-
"""
_outils_llms.py — le `llms.txt` d'Angy Art, LU dans la page.

    python _outils_llms.py

Un assistant qui arrive sans contexte doit savoir en dix lignes qui est
Angelique, ce qu'elle fait, et ou trouver le reste. C'est ce fichier.

⛔ AUCUN PRIX. Angelique les a retires du site le 2026-09-05 : les remettre
   ici serait les reafficher par une autre porte, celle que personne ne
   regarde. Les titres, les techniques et les dimensions viennent de la page.

⚠️ LU, PAS RECOPIE. Le jour ou elle change un texte, on relance la commande.
"""
import html, io, os, re, sys, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RACINE = os.path.dirname(os.path.abspath(__file__))
DOMAINE = "https://angy-art.pages.dev"


def main():
    src = io.open(os.path.join(RACINE, "index.html"), encoding="utf-8").read()

    # les six oeuvres : titre + cartel, tels qu'ils sont affiches
    oeuvres = []
    for m in re.finditer(r'<h3 class="oeu-t">(.*?)</h3>\s*<dl class="oeu-c">(.*?)</dl>', src, re.S):
        titre = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        cartel = {}
        for dt, dd in re.findall(r"<dt>(.*?)</dt><dd[^>]*>(.*?)</dd>", m.group(2), re.S):
            cartel[html.unescape(re.sub(r"<[^>]+>", "", dt)).strip()] = html.unescape(re.sub(r"<[^>]+>", "", dd)).strip()
        oeuvres.append((titre, cartel))

    # la FAQ deja balisee sur la page
    q = [(html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", a))).strip(),
          html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", b))).strip())
         for a, b in re.findall(r'"name":\s*"([^"]+)"[^}]*?"text":\s*"([^"]+)"', src)]

    if len(oeuvres) < 3:
        sys.exit("seulement %d oeuvres relevees : le format a bouge" % len(oeuvres))

    jour = datetime.date.today().isoformat()
    l = ["# Angy Art — Angélique Avocevou", "",
         "> Artiste plasticienne béninoise, à Cotonou. Œuvres contemporaines en",
         "> relief sur l'identité, la mémoire et le patrimoine africain :",
         "> scarifications, symboles, masques, textiles.", "",
         "« Inspiré d'en haut, enraciné ici. »", "",
         "Les pièces sont faites main à Cotonou, en composition sculpturale et",
         "peinture. Chaque pièce est unique. Le contact et les demandes passent",
         "par WhatsApp (+229 01 52 00 64 90).", "",
         "## La collection ÉNERGIES", ""]
    for titre, c in oeuvres:
        l.append("### " + titre)
        for cle in ("TECHNIQUE", "PALETTE", "DIMENSIONS"):
            if c.get(cle):
                l.append("- %s : %s" % (cle.capitalize(), c[cle]))
        l.append("")
    l += ["Le prix de chaque œuvre est communiqué sur demande, par WhatsApp.",
          "Le site n'affiche aucun prix.", "",
          "## Ce qu'on peut demander", "",
          "- une œuvre de la collection ;",
          "- une **création sur mesure**, à partir d'une histoire, d'un format ou d'un lieu ;",
          "- l'**équipement d'un lieu** (hôtel, restaurant, bureau) ;",
          "- une visite de l'atelier à Cotonou.", ""]
    if q:
        l += ["## Questions fréquentes", ""]
        for a, b in q:
            l += ["### " + a, "", b, ""]
    l += ["## Ce que ce site ne dit pas", "",
          "Aucun prix affiché, aucun avis client, aucune note. Trois photographies",
          "de la collection sont des **mises en situation** : les masques sont bien",
          "d'Angélique, les intérieurs qui les entourent sont des rendus, et le",
          "site le dit sur chacune.", "",
          "- [Le site](%s/)" % DOMAINE,
          "- [Plan du site](%s/sitemap.xml)" % DOMAINE, "",
          "Dernière mise à jour : %s." % jour, ""]

    io.open(os.path.join(RACINE, "llms.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(l))
    print("  llms.txt : %d œuvres lues, %d questions reprises de la page" % (len(oeuvres), len(q)))
    print("  ⛔ aucun prix : Angélique les a retirés le 2026-09-05.")


if __name__ == "__main__":
    main()
