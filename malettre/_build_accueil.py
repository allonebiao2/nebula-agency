# -*- coding: utf-8 -*-
"""MA LETTRE À… · fabrique la page d'accueil et les lettres d'exemple.

    python malettre/_build_accueil.py

⛔ `index.html` et `exemples/*.html` sont GÉNÉRÉS. On édite
`_accueil_src.html`, `exemples.json`, ou le catalogue de `creer.html`.

POURQUOI UN BUILD
    Un prix vit à quatre endroits (leçon Angy Art) : la page d'accueil ne doit
    en écrire AUCUN à la main. Les paliers, la plume, les occasions et les
    questions sont LUS dans `creer.html`, qui est déjà comparé au barème du
    serveur par `_qc_caisse.mjs`. Et une liste fixe s'écrit dans la page, pas
    en JavaScript (leçon du CLS) : les cartes, le casier et les timbres sont
    du HTML dès le premier octet.

⛔ LES EXEMPLES SONT DE VRAIES LETTRES, bâties avec le vrai gabarit par
`_injecter.poser()`, le seul endroit qui écrit des données dans une lettre.
Leurs personnes sont inventées, et la lettre le dit elle-même (« Exemple · »).
"""
import html
import json
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from _injecter import poser, serialiser  # noqa: E402

SOURCE = ICI / "_accueil_src.html"
SORTIE = ICI / "index.html"
CREER = ICI / "creer.html"
EXEMPLES = ICI / "exemples.json"
DOSSIER_EX = ICI / "exemples"
LIEN = "https://malettre.nebula-agency.online"
NB = chr(0xA0)  # espace insécable

e = lambda t: html.escape(str(t), quote=True)


def fmt(n):
    if n == 0:
        return "Offert"
    # Espaces INSÉCABLES : « 10 000 F » ne doit jamais se couper (vu en 390).
    return re.sub(r"\B(?=(\d{3})+(?!\d))", NB, str(n)) + NB + "F"


# ── Le catalogue, lu dans creer.html ─────────────────────────────────────
def bloc(src, nom, ouvre="[", ferme="];"):
    m = re.search(r"var %s = \%s(.*?)\n\%s" % (nom, ouvre, ferme[0]), src, re.S)
    if not m:
        sys.exit("⛔ %s introuvable dans creer.html" % nom)
    return m.group(1)


def champ(ligne, cle):
    m = re.search(r'\b%s:"((?:[^"\\]|\\.)*)"' % cle, ligne)
    return m.group(1) if m else None


def catalogue():
    src = CREER.read_text(encoding="utf-8")
    paliers = []
    for m in re.finditer(r'\{id:"([a-z]+)",\s*nom:"([^"]+)",\s*desc:"([^"]+)",\s*prix:(\d+),\s*pied:(true|false),\s*photos:(\d+)\}',
                         bloc(src, "PALIERS")):
        paliers.append({"id": m.group(1), "nom": m.group(2), "desc": m.group(3),
                        "prix": int(m.group(4)), "pied": m.group(5) == "true", "photos": int(m.group(6))})
    plume = re.search(r"var PLUME = \{prix:(\d+)\};", src)
    familles = [{"id": m.group(1), "nom": m.group(2)}
                for m in re.finditer(r'\{id:"([a-z]+)",\s*nom:"([^"]+)"\}', bloc(src, "FAMILLES"))]
    occasions = []
    for ligne in bloc(src, "OCCASIONS").split("\n"):
        if '{id:"' in ligne:
            occasions.append({"id": champ(ligne, "id"), "fam": champ(ligne, "fam"),
                              "nom": champ(ligne, "nom"), "note": champ(ligne, "note")})
    questions = {}
    for m in re.finditer(r'^\s*"([a-z-]+)":\s*\{q:"([^"]+)".*?choix:\[(.*?)\]\}', bloc(src, "QUESTIONS", "{", "};"), re.M):
        questions[m.group(1)] = {"q": m.group(2), "choix": re.findall(r'"([^"]+)"', m.group(3))}
    for nom, liste in (("PALIERS", paliers), ("FAMILLES", familles), ("OCCASIONS", occasions), ("QUESTIONS", questions)):
        if not liste:
            sys.exit("⛔ %s lu vide : la forme de creer.html a changé" % nom)
    if not plume:
        sys.exit("⛔ PLUME introuvable dans creer.html")
    return paliers, int(plume.group(1)), familles, occasions, questions


# ── Les morceaux de page ─────────────────────────────────────────────────
def texte_feuille():
    lignes = "".join('<div class="l%s" style="--i:%d"></div>' % (" court" if i in (3, 7) else "", i) for i in range(8))
    return ('<div class="texte"><div class="a">Ma lettre à <b>Afi</b>,</div>%s'
            '<div class="sig">Kofi</div></div>' % lignes)


def jour_mois(ouvre):
    MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
            "septembre", "octobre", "novembre", "décembre"]
    a, m, j = ouvre[:10].split("-")
    return "%d %s" % (int(j), MOIS[int(m) - 1])


def cartes(exemples):
    out = []
    for x in exemples:
        verrou = ('<span class="verrou">S\'ouvre le %s<br>à minuit</span>' % e(jour_mois(x["ouvre"]))) if x["ouvre"] else ""
        out.append(
            '<button class="carte" type="button" data-id="%s" data-titre="%s" aria-label="%s">'
            '<span class="occ">%s</span><span class="cachet-c" aria-hidden="true">%s</span>%s'
            '<span class="a1">Ma lettre à</span><span class="a2">%s</span><span class="de">de %s · %s</span></button>'
            % (e(x["id"]), e("%s à %s" % (x["de"], x["pour"])),
               e("Ouvrir l'exemple : Ma lettre à %s, de %s (%s)" % (x["pour"], x["de"], x["occasionNom"])),
               e(x["occasionNom"]), e(x["de"][:1].upper()), verrou, e(x["pour"]), e(x["de"]), e(x["ville"])))
    return "".join(out)


def fiche_et_lettre(x, questions):
    """La fiche de l'exemple, avec TOUS les choix de chaque question, et ce
    que la plume en a écrit."""
    f = ['<p class="t">La fiche de %s</p>' % e(x["de"])]
    for rep in x["fiche"]["reponses"]:
        q, r = rep["q"], rep["r"]
        cand = [v for v in questions.values() if v["q"] == q and all(c in v["choix"] for c in r)]
        choix = cand[0]["choix"] if cand else r
        f.append('<p class="q">%s</p><div class="puces">%s</div>' % (e(q), "".join(
            '<span class="puce"%s>%s</span>' % (' data-choisie' if c in r else "", e(c)) for c in choix)))
    if x["fiche"]["souvenir"]:
        f.append('<p class="libre"><b>Un souvenir que vous seuls connaissez</b>%s</p>' % e(x["fiche"]["souvenir"]))
    if x["fiche"]["consignes"]:
        f.append('<p class="libre"><b>Comment il la veut</b>%s</p>' % e(x["fiche"]["consignes"]))
    l = ['<p class="o">%s · exemple</p>' % e(x["occasionNom"]), '<h3>%s</h3>' % e(x["titre"])]
    l += ['<p>%s</p>' % e(p) for p in x["lettre"]]
    l += ['<p class="fo">%s</p>' % e(x["formule"]), '<p class="f">%s</p>' % e(x["de"])]
    return "".join(f), "".join(l)


def casier(familles, occasions):
    out = []
    for fam in familles:
        occ = [o for o in occasions if o["fam"] == fam["id"]]
        if not occ:
            continue
        out.append('<h3 class="fam-t" data-rv>%s</h3><div class="casier">' % e(fam["nom"]))
        for o in occ:
            out.append('<a class="case" href="creer.html?occasion=%s"><span class="ev"><b>%s</b><span>%s</span></span>'
                       '<span class="bord">Écrire</span></a>' % (e(o["id"]), e(o["nom"]), e(o["note"])))
        out.append("</div>")
    return "".join(out)


TAMPON = ('<svg class="tampon" viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="33"/>'
          '<circle cx="40" cy="40" r="25"/><path d="M4 46 Q22 38 40 46 T76 46"/><path d="M4 54 Q22 46 40 54 T76 54"/></svg>')


def timbres(paliers, plume):
    out = []
    for i, p in enumerate(paliers):
        out.append('<div class="timbre" data-rv style="--d:%.2fs">%s<span class="nm">%s</span><span class="vl">%s</span>'
                   '<span class="ds">%s</span></div>' % (i * .1, TAMPON, e(p["nom"]), e(fmt(p["prix"])), e(p["desc"])))
    out.append('<div class="timbre plume-t" data-rv style="--d:%.2fs">%s<span class="nm">La plume</span><span class="vl">+%s</span>'
               '<span class="ds">Elle écrit avec toi. Gratuite à essayer, comptée seulement si tu l\'envoies.</span></div>'
               % (len(paliers) * .1, TAMPON, e(fmt(plume))))
    return "".join(out)


# ── Les lettres d'exemple : le vrai gabarit ──────────────────────────────
def exemples_html(exemples):
    DOSSIER_EX.mkdir(exist_ok=True)
    faits = []
    for x in exemples:
        d = {"occasion": "Exemple · " + x["occasionNom"], "pour": x["pour"], "de": x["de"],
             "titre": x["titre"], "code": "", "lettre": x["lettre"], "photos": [],
             "depuis": "", "ouvre": x["ouvre"], "formule": x["formule"], "pied": True, "lien": LIEN}
        (DOSSIER_EX / ("%s.html" % x["id"])).write_text(poser(d), encoding="utf-8")
        faits.append(x["id"])
    return faits


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><radialGradient id="c" cx=".34" cy=".3" r=".75">'
           '<stop offset="0" stop-color="#b2434e"/><stop offset=".62" stop-color="#8c2f39"/><stop offset="1" stop-color="#6d1f27"/>'
           '</radialGradient></defs><circle cx="32" cy="32" r="29" fill="url(#c)"/>'
           '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#f0d6cf">M</text></svg>')


def main():
    paliers, plume, familles, occasions, questions = catalogue()
    doc = json.loads(EXEMPLES.read_text(encoding="utf-8"))
    exemples = doc["exemples"]
    demo = next(x for x in exemples if x["id"] == "afi")
    fiche, lettre = fiche_et_lettre(demo, questions)

    s = SOURCE.read_text(encoding="utf-8")
    remplacer = {
        "<!--__PLUME_PRIX__-->": e(fmt(plume)),
        "<!--__TEXTE__-->": texte_feuille(),
        "<!--__EXEMPLES__-->": cartes(exemples),
        "<!--__FICHE__-->": fiche,
        "<!--__LETTRE_PLUME__-->": lettre,
        "<!--__CASIER__-->": casier(familles, occasions),
        "<!--__PRIX__-->": timbres(paliers, plume),
    }
    for k, v in remplacer.items():
        if k not in s:
            sys.exit("⛔ marqueur absent de la source : %s" % k)
        s = s.replace(k, v)
    a, b = "/*__DONNEES__*/", "/*__FIN_DONNEES__*/"
    i, j = s.index(a), s.index(b) + len(b)
    donnees = {"plume": plume, "paliers": [p["id"] for p in paliers], "exemples": [x["id"] for x in exemples]}
    s = s[:i] + serialiser(donnees) + s[j:]
    if "<!--__" in s:
        sys.exit("⛔ un marqueur n'a pas été remplacé")
    SORTIE.write_text(s, encoding="utf-8")
    faits = exemples_html(exemples)
    (ICI / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    print("index.html : %d octets · %d occasions · %d paliers · plume %s · exemples : %s"
          % (len(s.encode("utf-8")), len(occasions), len(paliers), fmt(plume), ", ".join(faits)))


if __name__ == "__main__":
    main()
