# -*- coding: utf-8 -*-
"""MA LETTRE À… · fabrique la page d'accueil et les lettres d'exemple, dans les
deux langues.

    python malettre/_build_accueil.py

⛔ `index.html`, `exemples/*.html` et tout `en/` sont GÉNÉRÉS. On édite
`_accueil_src.html`, `exemples.json` / `exemples.en.json`, le catalogue de
`creer.html`, ou le dictionnaire `i18n/en.txt`.

POURQUOI UN BUILD
    Un prix vit à quatre endroits (leçon Angy Art) : la page d'accueil ne doit
    en écrire AUCUN à la main. Les paliers, la plume, les occasions et les
    questions sont LUS dans `creer.html` (ou `en/creer.html`), qui est déjà
    comparé au barème du serveur par `_qc_caisse.mjs`. Et une liste fixe
    s'écrit dans la page, pas en JavaScript (leçon du CLS) : les cartes, le
    casier et les timbres sont du HTML dès le premier octet.

LES DEUX LANGUES (2026-10-16)
    Le français est la source. Le build lance d'abord `_traduire.py` (les pages
    anglaises du constructeur et du paiement), puis traduit la SOURCE de
    l'accueil avec le même dictionnaire, et la remplit avec le catalogue
    anglais et les exemples anglais.

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
import _traduire  # noqa: E402

SOURCE = ICI / "_accueil_src.html"
SITE = "https://malettre.nebula-agency.online"
NB = chr(0xA0)  # espace insécable

LANGUES = {
    "fr": {
        "creer": ICI / "creer.html", "exemples": ICI / "exemples.json",
        "sortie": ICI / "index.html", "dossier": ICI / "exemples", "lien": SITE,
        "titre": "%s à %s",
        "offert": "Offert", "ma": "Ma lettre à", "verrou": "S'ouvre le %s<br>à minuit",
        "ouvrir": "Ouvrir l'exemple : Ma lettre à %s, de %s (%s)", "de": "de %s · %s",
        "fiche": "La fiche de %s", "souvenir": "Un souvenir que vous seuls connaissez",
        "consignes": "Comment il la veut", "exemple": "%s · exemple", "ecrire": "Écrire",
        "plume": "La plume",
        "plume_ds": "Elle écrit avec toi. Gratuite à essayer, comptée seulement si tu l'envoies.",
        "occ": "Exemple · ",
        "mois": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                 "septembre", "octobre", "novembre", "décembre"],
    },
    "en": {
        "creer": ICI / "en" / "creer.html", "exemples": ICI / "exemples.en.json",
        "sortie": ICI / "en" / "index.html", "dossier": ICI / "en" / "exemples", "lien": SITE + "/en/",
        "titre": "%s to %s",
        "offert": "Free", "ma": "My letter to", "verrou": "Opens on %s<br>at midnight",
        "ouvrir": "Open the example: My letter to %s, from %s (%s)", "de": "from %s · %s",
        "fiche": "%s's form", "souvenir": "A memory only you two know",
        "consignes": "How he wants it", "exemple": "%s · example", "ecrire": "Write",
        "plume": "The Quill",
        "plume_ds": "It writes with you. Free to try, counted only if you send it.",
        "occ": "Example · ",
        "mois": ["January", "February", "March", "April", "May", "June", "July", "August",
                 "September", "October", "November", "December"],
    },
}

e = lambda t: html.escape(str(t), quote=True)


def fmt(n, T):
    if n == 0:
        return T["offert"]
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


def catalogue(creer):
    src = creer.read_text(encoding="utf-8")
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
            sys.exit("⛔ %s lu vide : la forme de %s a changé" % (nom, creer.name))
    if not plume:
        sys.exit("⛔ PLUME introuvable dans %s" % creer.name)
    return paliers, int(plume.group(1)), familles, occasions, questions


# ── Les morceaux de page ─────────────────────────────────────────────────
def texte_feuille(T):
    lignes = "".join('<div class="l%s" style="--i:%d"></div>' % (" court" if i in (3, 7) else "", i) for i in range(8))
    return ('<div class="texte"><div class="a">%s <b>Afi</b>,</div>%s'
            '<div class="sig">Kofi</div></div>' % (T["ma"], lignes))


def jour_mois(ouvre, T):
    a, m, j = ouvre[:10].split("-")
    return "%d %s" % (int(j), T["mois"][int(m) - 1])


def cartes(exemples, T):
    out = []
    for x in exemples:
        verrou = ('<span class="verrou">%s</span>' % (T["verrou"] % e(jour_mois(x["ouvre"], T)))) if x["ouvre"] else ""
        out.append(
            '<button class="carte" type="button" data-id="%s" data-titre="%s" aria-label="%s">'
            '<span class="occ">%s</span><span class="cachet-c" aria-hidden="true">%s</span>%s'
            '<span class="a1">%s</span><span class="a2">%s</span><span class="de">%s</span></button>'
            % (e(x["id"]), e(T["titre"] % (x["de"], x["pour"])),
               e(T["ouvrir"] % (x["pour"], x["de"], x["occasionNom"])),
               e(x["occasionNom"]), e(x["de"][:1].upper()), verrou, e(T["ma"]), e(x["pour"]),
               e(T["de"] % (x["de"], x["ville"]))))
    return "".join(out)


def fiche_et_lettre(x, questions, T):
    """La fiche de l'exemple, avec TOUS les choix de chaque question, et ce
    que la plume en a écrit."""
    f = ['<p class="t">%s</p>' % e(T["fiche"] % x["de"])]
    for rep in x["fiche"]["reponses"]:
        q, r = rep["q"], rep["r"]
        cand = [v for v in questions.values() if v["q"] == q and all(c in v["choix"] for c in r)]
        choix = cand[0]["choix"] if cand else r
        f.append('<p class="q">%s</p><div class="puces">%s</div>' % (e(q), "".join(
            '<span class="puce"%s>%s</span>' % (' data-choisie' if c in r else "", e(c)) for c in choix)))
    if x["fiche"]["souvenir"]:
        f.append('<p class="libre"><b>%s</b>%s</p>' % (e(T["souvenir"]), e(x["fiche"]["souvenir"])))
    if x["fiche"]["consignes"]:
        f.append('<p class="libre"><b>%s</b>%s</p>' % (e(T["consignes"]), e(x["fiche"]["consignes"])))
    l = ['<p class="o">%s</p>' % e(T["exemple"] % x["occasionNom"]), '<h3>%s</h3>' % e(x["titre"])]
    l += ['<p>%s</p>' % e(p) for p in x["lettre"]]
    l += ['<p class="fo">%s</p>' % e(x["formule"]), '<p class="f">%s</p>' % e(x["de"])]
    return "".join(f), "".join(l)


def casier(familles, occasions, T):
    out = []
    for fam in familles:
        occ = [o for o in occasions if o["fam"] == fam["id"]]
        if not occ:
            continue
        out.append('<h3 class="fam-t" data-rv>%s</h3><div class="casier">' % e(fam["nom"]))
        for o in occ:
            out.append('<a class="case" href="creer.html?occasion=%s"><span class="ev"><b>%s</b><span>%s</span></span>'
                       '<span class="bord">%s</span></a>' % (e(o["id"]), e(o["nom"]), e(o["note"]), e(T["ecrire"])))
        out.append("</div>")
    return "".join(out)


TAMPON = ('<svg class="tampon" viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="33"/>'
          '<circle cx="40" cy="40" r="25"/><path d="M4 46 Q22 38 40 46 T76 46"/><path d="M4 54 Q22 46 40 54 T76 54"/></svg>')


def timbres(paliers, plume, T):
    out = []
    for i, p in enumerate(paliers):
        out.append('<div class="timbre" data-rv style="--d:%.2fs">%s<span class="nm">%s</span><span class="vl">%s</span>'
                   '<span class="ds">%s</span></div>' % (i * .1, TAMPON, e(p["nom"]), e(fmt(p["prix"], T)), e(p["desc"])))
    out.append('<div class="timbre plume-t" data-rv style="--d:%.2fs">%s<span class="nm">%s</span><span class="vl">+%s</span>'
               '<span class="ds">%s</span></div>'
               % (len(paliers) * .1, TAMPON, e(T["plume"]), e(fmt(plume, T)), e(T["plume_ds"])))
    return "".join(out)


# ── Les lettres d'exemple : le vrai gabarit ──────────────────────────────
def exemples_html(exemples, T, langue):
    T["dossier"].mkdir(parents=True, exist_ok=True)
    faits = []
    for x in exemples:
        d = {"occasion": T["occ"] + x["occasionNom"], "pour": x["pour"], "de": x["de"],
             "titre": x["titre"], "code": "", "lettre": x["lettre"], "photos": [],
             "depuis": "", "ouvre": x["ouvre"], "formule": x["formule"], "pied": True, "lien": T["lien"]}
        if langue != "fr":
            d["langue"] = langue
        (T["dossier"] / ("%s.html" % x["id"])).write_text(poser(d), encoding="utf-8")
        faits.append(x["id"])
    return faits


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><radialGradient id="c" cx=".34" cy=".3" r=".75">'
           '<stop offset="0" stop-color="#b2434e"/><stop offset=".62" stop-color="#8c2f39"/><stop offset="1" stop-color="#6d1f27"/>'
           '</radialGradient></defs><circle cx="32" cy="32" r="29" fill="url(#c)"/>'
           '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#f0d6cf">M</text></svg>')


def construire(langue, dico):
    T = LANGUES[langue]
    paliers, plume, familles, occasions, questions = catalogue(T["creer"])
    doc = json.loads(T["exemples"].read_text(encoding="utf-8"))
    exemples = doc["exemples"]
    demo = next(x for x in exemples if x["id"] == "afi")
    fiche, lettre = fiche_et_lettre(demo, questions, T)

    s = SOURCE.read_text(encoding="utf-8")
    if langue != "fr":
        s = _traduire.traduire(s, dico["_accueil_src.html"], "_accueil_src.html")
    remplacer = {
        "<!--__PLUME_PRIX__-->": e(fmt(plume, T)),
        "<!--__TEXTE__-->": texte_feuille(T),
        "<!--__EXEMPLES__-->": cartes(exemples, T),
        "<!--__FICHE__-->": fiche,
        "<!--__LETTRE_PLUME__-->": lettre,
        "<!--__CASIER__-->": casier(familles, occasions, T),
        "<!--__PRIX__-->": timbres(paliers, plume, T),
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
    T["sortie"].parent.mkdir(exist_ok=True)
    T["sortie"].write_text(s, encoding="utf-8")
    faits = exemples_html(exemples, T, langue)
    print("%s : %d octets · %d occasions · %d paliers · plume %s · exemples : %s"
          % (T["sortie"].relative_to(ICI), len(s.encode("utf-8")), len(occasions), len(paliers),
             fmt(plume, T), ", ".join(faits)))


def main():
    _traduire.main()   # les pages anglaises d'abord : l'accueil anglais lit en/creer.html
    dico = _traduire.lire_dico()
    construire("fr", dico)
    construire("en", dico)
    (ICI / "favicon.svg").write_text(FAVICON, encoding="utf-8")


if __name__ == "__main__":
    main()
