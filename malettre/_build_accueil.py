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
import random
import re
import sys
import urllib.parse

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from _injecter import poser, serialiser  # noqa: E402
import _traduire  # noqa: E402

SOURCE = ICI / "_accueil_src.html"
SITE = "https://malettre.nebula-agency.online"
NB = chr(0xA0)  # espace insécable
# Le faire-part de mariage, sur demande : la SEULE source de son prix.
OFFRE_FP = ICI / "faire-part" / "offre.json"
LLMS = ICI / "llms.txt"

LANGUES = {
    "fr": {
        "creer": ICI / "creer.html", "exemples": ICI / "exemples.json",
        "sortie": ICI / "index.html", "dossier": ICI / "exemples", "lien": SITE,
        "titre": "%s à %s",
        "offert": "Offert", "ma": "Ma lettre à", "verrou": "S'ouvre le %s<br>à minuit",
        "ouvrir": "Ouvrir l'exemple : Ma lettre à %s, de %s (%s)", "de": "de %s · %s",
        "fiche": "La fiche de %s", "souvenir": "Un souvenir que vous seuls connaissez",
        "consignes": "Comment il la veut", "exemple": "%s · exemple", "ecrire": "Écrire", "fam_n": "%d occasions",
        "plume": "La plume", "musique": "Musique", "credit_son": "Musique : %s, sur Pixabay.",
        "plume_ds": "Elle écrit avec toi, une fois ta commande réglée.",
        "occ": "Exemple · ",
        "mois": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                 "septembre", "octobre", "novembre", "décembre"],
        "hab_des": "dès %s (%s)", "habille": "+ l'habillage au choix",
        "hab_l": {"cire": "La cire", "papier": "Le papier", "pluie": "À l'ouverture"},
        # ⛔ « un an » et « sans notre signature » sont VÉRIFIÉS sur chaque offre
        # payante avant d'être écrits (voir faq_prix) : la phrase ne peut pas mentir.
        "an": "un an", "et": " et ",
        "faq_prix": "%s coûte %s : %s. Les autres offres la gardent un an, sans notre signature, avec "
                    "l'habillage au choix : %s. La plume ajoute %s, réglés avec ta lettre.",
        "fp_msg": "Bonjour, nous nous marions et nous voudrions un faire-part Ma lettre à…",
        # ⚠️ Clés NEUTRES : elles vivent dans le script de la page anglaise, où le
        # contrôle des langues prenait « avant » et « dans » pour du français oublié.
        "bientot": {"a": "Prochaine grande date : ", "j0": "c'est aujourd'hui", "j1": "c'est demain",
                    "jn": "dans %d jours", "go": "Écris-la maintenant, elle attendra."},
        "llms": {"resume": "Une lettre digitale scellée qui ne s'ouvre qu'à l'heure choisie, sur le téléphone de la "
                           "personne qui la reçoit. On l'écrit soi-même, ou la plume (une aide à l'écriture) l'écrit "
                           "avec nous ; on envoie le lien ; à l'heure dite, la personne brise le cachet et lit. Un "
                           "service de NEBULA Agency, à Cotonou (Bénin).",
                 "offres": "Les offres", "plume": "La plume : +%s, seulement si on envoie la version qu'elle a écrite",
                 "fp": "Faire-part de mariage, sur demande : %s, fait sur mesure par l'équipe de NEBULA",
                 "faq": "Questions fréquentes", "pages": "Pages", "accueil": "Accueil",
                 "creer": "Écrire une lettre", "wa": "Demander un faire-part (WhatsApp)",
                 "fp_ex": "Un faire-part d'exemple", "fp_page": "/faire-part/exemple"},
    },
    "en": {
        "creer": ICI / "en" / "creer.html", "exemples": ICI / "exemples.en.json",
        "sortie": ICI / "en" / "index.html", "dossier": ICI / "en" / "exemples", "lien": SITE + "/en/",
        "titre": "%s to %s",
        "offert": "Free", "ma": "My letter to", "verrou": "Opens on %s<br>at midnight",
        "ouvrir": "Open the example: My letter to %s, from %s (%s)", "de": "from %s · %s",
        "fiche": "%s's form", "souvenir": "A memory only you two know",
        "consignes": "How he wants it", "exemple": "%s · example", "ecrire": "Write", "fam_n": "%d occasions",
        "plume": "The Quill", "musique": "Music", "credit_son": "Music: %s, on Pixabay.",
        "plume_ds": "It writes with you, once your order is paid.",
        "occ": "Example · ",
        "mois": ["January", "February", "March", "April", "May", "June", "July", "August",
                 "September", "October", "November", "December"],
        "hab_des": "from %s (%s)", "habille": "+ your choice of finish",
        "hab_l": {"cire": "The wax", "papier": "The paper", "pluie": "When it opens"},
        "an": "year", "et": " and ",
        "faq_prix": "%s costs %s: %s. The other offers keep it for a year, without our signature, with your "
                    "choice of finish: %s. The Quill adds %s, paid with your letter.",
        "fp_msg": "Hello, we are getting married and we would like a Ma lettre à… wedding invitation.",
        "bientot": {"a": "Next big date: ", "j0": "it's today", "j1": "it's tomorrow",
                    "jn": "in %d days", "go": "Write it now, it will wait."},
        "llms": {"resume": "A sealed digital letter that only opens at the chosen time, on the phone of the person "
                           "who receives it. You write it yourself, or the Quill (a writing aid) writes it with you; "
                           "you send the link; at the set time, they break the seal and read. A service by NEBULA "
                           "Agency, in Cotonou (Benin).",
                 "offres": "Offers", "plume": "The Quill: +%s, only if you send the version it wrote",
                 "fp": "Wedding invitation, on request: %s, made to measure by the NEBULA team",
                 "faq": "Frequently asked questions", "pages": "Pages", "accueil": "Home",
                 "creer": "Write a letter", "wa": "Ask for a wedding invitation (WhatsApp)",
                 "fp_ex": "An example wedding invitation", "fp_page": "/faire-part/exemple-en"},
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
    for m in re.finditer(r'\{id:"([a-z]+)",\s*nom:"([^"]+)",\s*desc:"([^"]+)",\s*prix:(\d+),\s*pied:(true|false),\s*photos:(\d+)'
                         r'(?:,\s*habillage:(true|false))?(?:,\s*code:(true|false))?\}', bloc(src, "PALIERS")):
        paliers.append({"id": m.group(1), "nom": m.group(2), "desc": m.group(3),
                        "prix": int(m.group(4)), "pied": m.group(5) == "true", "photos": int(m.group(6)),
                        "habillage": m.group(7) == "true", "code": m.group(8) == "true"})
    plume = re.search(r"var PLUME = \{prix:(\d+)\};", src)
    familles = [{"id": m.group(1), "nom": m.group(2)}
                for m in re.finditer(r'\{id:"([a-z]+)",\s*nom:"([^"]+)"\}', bloc(src, "FAMILLES"))]
    occasions = []
    for ligne in bloc(src, "OCCASIONS").split("\n"):
        if '{id:"' in ligne:
            occasions.append({"id": champ(ligne, "id"), "fam": champ(ligne, "fam"),
                              "nom": champ(ligne, "nom"), "note": champ(ligne, "note"),
                              "jour": champ(ligne, "jour")})
    questions = {}
    for m in re.finditer(r'^\s*"([a-z-]+)":\s*\{q:"([^"]+)".*?choix:\[(.*?)\]\}', bloc(src, "QUESTIONS", "{", "};"), re.M):
        questions[m.group(1)] = {"q": m.group(2), "choix": re.findall(r'"([^"]+)"', m.group(3))}
    for nom, liste in (("PALIERS", paliers), ("FAMILLES", familles), ("OCCASIONS", occasions), ("QUESTIONS", questions)):
        if not liste:
            sys.exit("⛔ %s lu vide : la forme de %s a changé" % (nom, creer.name))
    if not plume:
        sys.exit("⛔ PLUME introuvable dans %s" % creer.name)
    return paliers, int(plume.group(1)), familles, occasions, questions


def habillage(creer):
    """Les listes de l'habillage, LUES dans le constructeur (la même langue que
    la page). La première valeur de chaque liste est celle d'une lettre nue."""
    src = creer.read_text(encoding="utf-8")
    m = re.search(r"var HABILLAGE = \{(.*?)\n\};", src, re.S)
    if not m:
        sys.exit("⛔ HABILLAGE introuvable dans %s" % creer.name)
    hab = {}
    for cle, corps in re.findall(r"(cire|sceau|papier|pluie):\s*\[(.*?)\]", m.group(1), re.S):
        hab[cle] = [{"id": a, "nom": b, "c": c or None}
                    for a, b, c in re.findall(r'\{id:"([a-z]+)",\s*nom:"([^"]+)"(?:,\s*c:"(#[0-9a-f]{6})")?\}', corps)]
    for cle in ("cire", "sceau", "papier", "pluie"):
        if not hab.get(cle):
            sys.exit("⛔ HABILLAGE.%s lu vide dans %s" % (cle, creer.name))
    for cle in ("cire", "papier"):
        if any(not o["c"] for o in hab[cle]):
            sys.exit("⛔ une %s sans couleur dans %s" % (cle, creer.name))
    if any(o["id"] not in ICONES for o in hab["pluie"]):
        sys.exit("⛔ une pluie sans icône : ajouter son dessin à ICONES")
    return hab


def tons_de_cire():
    """Les trois tons de chaque cire, LUS dans le gabarit de la lettre : la carte
    d'un exemple porte la même cire que sa lettre, sans quatrième copie."""
    src = (ICI / "lettre.html").read_text(encoding="utf-8")
    tons = {m.group(1): (m.group(2), m.group(3), m.group(4)) for m in re.finditer(
        r"\.cire-([a-z]+)\{--cire:(#[0-9a-f]{6});--cire-clair:(#[0-9a-f]{6});--cire-fonce:(#[0-9a-f]{6})", src)}
    if len(tons) < 4:
        sys.exit("⛔ les tons de cire sont introuvables dans lettre.html")
    return tons


def offre_fp():
    o = json.loads(OFFRE_FP.read_text(encoding="utf-8"))
    if not isinstance(o.get("prix"), int) or o["prix"] <= 0 or not re.fullmatch(r"\d{11,15}", str(o.get("whatsapp", ""))):
        sys.exit("⛔ faire-part/offre.json : un prix entier et un numéro international sont exigés")
    return o


# ── Les morceaux de page ─────────────────────────────────────────────────
def texte_feuille(T):
    lignes = "".join('<div class="l%s" style="--i:%d"></div>' % (" court" if i in (3, 7) else "", i) for i in range(8))
    return ('<div class="texte"><div class="a">%s <b>Afi</b>,</div>%s'
            '<div class="sig">Kofi</div></div>' % (T["ma"], lignes))


def jour_mois(ouvre, T):
    a, m, j = ouvre[:10].split("-")
    return "%d %s" % (int(j), T["mois"][int(m) - 1])


def cartes(exemples, T, tons):
    out = []
    for x in exemples:
        verrou = ('<span class="verrou">%s</span>' % (T["verrou"] % e(jour_mois(x["ouvre"], T)))) if x["ouvre"] else ""
        cire = (x.get("habillage") or {}).get("cire")
        ton = (' style="--cc:%s;--cc-c:%s;--cc-f:%s"' % tons[cire]) if cire in tons else ""
        out.append(
            '<button class="carte" type="button" data-id="%s" data-titre="%s" aria-label="%s"%s>'
            '<span class="occ">%s</span><span class="cachet-c" aria-hidden="true">%s</span>%s'
            '<span class="a1">%s</span><span class="a2">%s</span><span class="de">%s</span></button>'
            % (e(x["id"]), e(T["titre"] % (x["de"], x["pour"])),
               e(T["ouvrir"] % (x["pour"], x["de"], x["occasionNom"])), ton,
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


def emblemes(creer):
    """Les emblèmes des occasions, LUS dans creer.html (seule source) : {id: tracé SVG}."""
    src = creer.read_text(encoding="utf-8")
    em = dict(re.findall(r'^\s*([a-z]+):"([^"]+)"', bloc(src, "EMBLEMES", "{", "};"), re.M))
    if not em:
        sys.exit("⛔ EMBLEMES lu vide : la forme de %s a changé" % creer.name)
    return em


def bruits(creer):
    """Le module de bruitages, LU dans creer.html entre ses deux marqueurs (une seule copie à tenir)."""
    src = creer.read_text(encoding="utf-8")
    a, z = "/*__BRUITS__*/", "/*__FIN_BRUITS__*/"
    if a not in src or z not in src:
        sys.exit("⛔ le module de bruitages est introuvable dans %s" % creer.name)
    code = src[src.index(a) + len(a):src.index(z)]
    # sans ses commentaires : ils sont pour le code, pas pour le visiteur (et 1,5 Ko de moins)
    return re.sub(r"/\*.*?\*/", "", code, flags=re.S).strip()


def cachet_occasion(o, em):
    """Le cachet de cire d'une occasion : son emblème gravé, ou son initiale."""
    if o["id"] in em:
        # le trait (couleur, épaisseur, bouts ronds) est dans le CSS : 27 fois moins d'octets
        return '<i class="sceau-o" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="%s"/></svg></i>' % e(em[o["id"]])
    return '<i class="sceau-o" aria-hidden="true">%s</i>' % e(o["nom"][:1])


def casier(familles, occasions, T, em):
    """Une étagère par famille ; chaque case porte une lettre à son cachet. Au téléphone,
    l'étagère se fait glisser (la page n'est plus un mur de 27 cases)."""
    out = []
    for fam in familles:
        occ = [o for o in occasions if o["fam"] == fam["id"]]
        if not occ:
            continue
        out.append('<h3 class="fam-t" data-rv>%s<span class="fam-n">%s</span></h3><div class="casier" data-fam="%s">'
                   % (e(fam["nom"]), e(T["fam_n"] % len(occ)), e(fam["id"])))
        for o in occ:
            out.append('<a class="case" href="creer.html?occasion=%s"><span class="ev"><span class="ev-in">%s<b>%s</b>'
                       '<span class="nt">%s</span></span></span><span class="bord">%s</span></a>'
                       % (e(o["id"]), cachet_occasion(o, em), e(o["nom"]), e(o["note"]), e(T["ecrire"])))
        out.append("</div>")
    return "".join(out)


# ── La nuit des lettres : une enveloppe par occasion RÉELLE du constructeur ──
# Les heures sont des exemples d'heure choisie, pas des ventes : aucun chiffre.
HEURES = ["00:00", "06:30", "08:00", "12:00", "18:45", "21:00", "23:59", "07:15", "19:30", "05:45"]


def vol(occasions, tons):
    """Chaque enveloppe à sa place : x, y en % du cadre, z en px, r en degrés.
    Une graine FIXE : la page est la même à chaque build. Le couloir central
    reste libre (la caméra y passe, et la tienne y arrive)."""
    rnd = random.Random(20261021)
    cires = [tons[k] for k in sorted(tons)]
    out = []
    for i, o in enumerate(occasions):
        while True:
            x, y = rnd.uniform(-44, 44), rnd.uniform(-38, 38)
            if abs(x) > 15 or abs(y) > 17:
                break
        z = -700 - i * 250 - rnd.uniform(0, 120)
        c = cires[i % len(cires)]
        out.append('<div class="nl-ev" data-x="%.1f" data-y="%.1f" data-z="%d" data-r="%.1f" '
                   'style="--cc:%s;--cc-c:%s;--cc-f:%s"><s>%s</s><b>%s</b></div>'
                   % (x, y, z, rnd.uniform(-14, 14), c[0], c[1], c[2], HEURES[i % len(HEURES)], e(o["nom"])))
    return "".join(out)


# ── Les fonds d'ambiance : seulement si l'image est sur le disque ─────────
FONDS = ["heros", "plume", "nuit", "faire-part", "seuil", "promesses", "fin"]
# Ce qui VIT dans chaque image (demande de Mongazi : « animé comme une vidéo ») :
# la flamme, la pluie, l'eau, la fumée, le cachet, la lumière du jour.
VIVANT = {"heros": '<s class="lueur"></s>', "plume": '<s class="lueur"></s>', "nuit": '<s class="miroir"></s>',
          "seuil": '<s class="pluie"></s><s class="pluie p2"></s>',
          "promesses": '<s class="fumee"></s><s class="fumee f2"></s>',
          "faire-part": '<s class="soleil"></s>', "fin": '<s class="cire-lueur"></s>'}


def fonds(langue):
    """Le marqueur de chaque zone devient un emplacement, ou rien. L'adresse
    des images se pose sur `.fond.pret` : rien n'est téléchargé avant l'approche."""
    rac = "" if langue == "fr" else "../"
    blocs, regles = {}, []
    for z in FONDS:
        l, p = ICI / "fonds" / ("%s-l.webp" % z), ICI / "fonds" / ("%s-p.webp" % z)
        if l.exists() and p.exists():
            # ⚠️ Même le héros attend : le JS l'allume quand le rideau se lève
            # (sinon le premier écran passait de 282 à 341 Ko, au-dessus des 320).
            blocs[z] = '<div class="fond" data-fond="%s" aria-hidden="true"><i><b></b>%s</i></div>' % (z, VIVANT.get(z, ""))
            regles.append('.fond.pret[data-fond="%s"]{--fond-l:url("%sfonds/%s-l.webp");--fond-p:url("%sfonds/%s-p.webp")}'
                          % (z, rac, z, rac, z))
        else:
            blocs[z] = ""
    return blocs, "\n".join(regles)


def credit_son(T):
    """Le crédit de la musique, au pied (Pixabay ne l'exige pas, on le donne)."""
    f = ICI / "son" / "credit.txt"
    if not (ICI / "son" / "musique.mp3").exists() or not f.exists():
        return ""
    return '<p class="credit-son">%s</p>' % e(T["credit_son"] % f.read_text(encoding="utf-8").strip())


def son(langue, T):
    """Le bouton de la musique, seulement si `son/musique.mp3` existe."""
    if not (ICI / "son" / "musique.mp3").exists():
        return ""
    rac = "" if langue == "fr" else "../"
    return ('<button class="son" id="son" type="button" aria-pressed="false" aria-label="%s" data-src="%sson/musique.mp3">'
            '<span class="ondes" aria-hidden="true"><i></i><i></i><i></i></span></button>' % (e(T["musique"]), rac))


TAMPON = ('<svg class="tampon" viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="33"/>'
          '<circle cx="40" cy="40" r="25"/><path d="M4 46 Q22 38 40 46 T76 46"/><path d="M4 54 Q22 46 40 54 T76 54"/></svg>')


def timbres(paliers, plume, T):
    out = []
    for i, p in enumerate(paliers):
        hb = ('<span class="hb">%s</span>' % e(T["habille"])) if p["habillage"] else ""
        out.append('<div class="timbre" data-rv style="--d:%.2fs">%s<span class="nm">%s</span><span class="vl">%s</span>'
                   '<span class="ds">%s</span>%s</div>' % (i * .1, TAMPON, e(p["nom"]), e(fmt(p["prix"], T)), e(p["desc"]), hb))
    out.append('<div class="timbre plume-t" data-rv style="--d:%.2fs">%s<span class="nm">%s</span><span class="vl">+%s</span>'
               '<span class="ds">%s</span></div>'
               % (len(paliers) * .1, TAMPON, e(T["plume"]), e(fmt(plume, T)), e(T["plume_ds"])))
    return "".join(out)


# ── « Ouvre-la toi-même » : les pastilles qui rhabillent la vraie lettre ──
# Les dessins de la pluie (pas de couleur à montrer : une forme).
ICONES = {
    "aucune": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="7.5" fill="none" stroke="currentColor"'
              ' stroke-width="1.6"/><path d="M7 17 17 7" stroke="currentColor" stroke-width="1.6"/></svg>',
    "petales": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c3.2 3.2 3.2 7.4 0 10.6-3.2-3.2-3.2-7.4 0-10.6z" '
               'fill="#e9a3b6"/><path d="M4 13.5c4.3-1.2 7.6.8 8.8 5.1-4.3 1.2-7.6-.8-8.8-5.1z" fill="#c76a85"/></svg>',
    "confettis": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="4" height="7" rx="1" fill="#c9a227" '
                 'transform="rotate(-20 6 7.5)"/><rect x="12" y="3" width="4" height="7" rx="1" fill="#e06a76" transform="rotate(25 14 6.5)"/>'
                 '<rect x="14" y="13" width="4" height="7" rx="1" fill="#6fb592" transform="rotate(-35 16 16.5)"/>'
                 '<rect x="5" y="13" width="4" height="7" rx="1" fill="#e8c56c" transform="rotate(15 7 16.5)"/></svg>',
    "etoiles": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4l-5.3 3 1.2-6-4.5-4.1 '
               '6-.7z" fill="#d9b24a"/></svg>',
}


def pastilles(hab, T):
    """Trois rangées (cire, papier, pluie), des boutons radio dont la zone de
    toucher fait 44 px. Le sceau reste au constructeur : quatre rangées ne
    tenaient plus sous le téléphone, en 390."""
    out = []
    for cle in ("cire", "papier", "pluie"):
        out.append('<div class="hb-g" role="radiogroup" aria-labelledby="hb-l-%s"><span class="hb-l" id="hb-l-%s">%s</span>'
                   % (cle, cle, e(T["hab_l"][cle])))
        for i, o in enumerate(hab[cle]):
            if cle == "pluie":
                cls, rond = "pt icone", '<span class="rond">%s</span>' % ICONES[o["id"]]
            else:
                cls = "pt pap" if cle == "papier" else "pt"
                rond = '<span class="rond" style="--c:%s"></span>' % e(o["c"])
            out.append('<label class="%s" title="%s"><input type="radio" name="hb-%s" value="%s" aria-label="%s"%s>%s</label>'
                       % (cls, e(o["nom"]), cle, e(o["id"]), e(o["nom"]), " checked" if i == 0 else "", rond))
        out.append("</div>")
    return "".join(out)


def milliers(n):
    return re.sub(r"\B(?=(\d{3})+(?!\d))", NB, str(n))


def faq_prix(paliers, plume, T):
    """La réponse « combien ça coûte », ÉCRITE depuis le catalogue. Elle affirme
    que les offres payantes durent un an, sans signature, avec l'habillage :
    c'est vérifié ici sur chacune, sinon rien n'est écrit."""
    # ⛔ Zéro gratuité depuis le 2026-10-22 : la première offre (La Carte) est payante et porte la signature.
    entree, payants = paliers[0], paliers[1:]
    if entree["prix"] <= 0 or not entree["pied"] or not payants:
        sys.exit("⛔ la première offre n'est plus La Carte payante et signée : réécrire la réponse du prix")
    faux = [p["nom"] for p in payants if p["pied"] or not p["habillage"] or T["an"] not in p["desc"].lower()]
    if faux:
        sys.exit("⛔ la réponse du prix mentirait pour %s : réécrire T['faq_prix']" % ", ".join(faux))
    liste = ["%s (%s)" % (p["nom"], fmt(p["prix"], T)) for p in payants]
    liste = ", ".join(liste[:-1]) + T["et"] + liste[-1] if len(liste) > 1 else liste[0]
    desc = entree["desc"][:1].lower() + entree["desc"][1:]
    return e(T["faq_prix"] % (entree["nom"], fmt(entree["prix"], T), desc, liste, fmt(plume, T)))


def plat_html(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()


# ── La typographie du texte VISIBLE (2026-10-21, « pas une once d'IA ») ──
# L'apostrophe droite et le « ? » qui peut tomber seul en début de ligne sont la
# marque d'une page faite à la machine. On ne touche QUE le texte entre les balises :
# jamais un script, un style, un commentaire ni un attribut (le dictionnaire anglais
# et le JavaScript lisent la source telle qu'elle est écrite).
# Espace INSÉCABLE devant ; : ! ? et dans les guillemets. Pas l'espace fine (U+202F) :
# Commissioner et le Caslon ne la dessinent pas, elle tombait à presque rien (« occasion: »).
FINE = " "


def typo_texte(t, langue):
    # l'apostrophe, écrite telle quelle OU échappée par html.escape (« l&#x27;habillage »)
    t = re.sub(r"(?<=[^\W\d_])(?:'|&#x27;|&#39;)(?=[^\W\d_])", "’", t)
    if langue == "fr":
        t = re.sub(r"[  ]([;:!?])", FINE + r"\1", t)
        t = re.sub(r"«[  ]", "«" + FINE, t)
        t = re.sub(r"[  ]»", FINE + "»", t)
    return t


def alleger(s):
    """La page livrée sans les commentaires (2026-10-21) : ils pesaient 23 Ko sur 178 (13 %) et le
    premier écran dépassait ses 320 Ko. Ils restent dans la source, qui seule se lit. On retire : les
    commentaires du CSS, ceux du HTML (hors scripts et styles), et dans les scripts les blocs /* … */
    qui commencent une ligne (jamais un // : une adresse en contient)."""
    s = re.sub(r"<style\b.*?</style>", lambda m: re.sub(r"/\*.*?\*/", "", m.group(0), flags=re.S), s, flags=re.S)
    morceaux = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", s, flags=re.S)
    s = "".join(m if i % 2 else re.sub(r"<!--(?!\[).*?-->", "", m, flags=re.S) for i, m in enumerate(morceaux))
    return re.sub(r"<script>.*?</script>",
                  lambda m: re.sub(r"(?m)^[ \t]*/\*.*?\*/[ \t]*\n", "", m.group(0), flags=re.S), s, flags=re.S)


def typographie(s, langue):
    morceaux = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]+>)", s, flags=re.S)
    return "".join(m if i % 2 else typo_texte(m, langue) for i, m in enumerate(morceaux))


def questions_page(s):
    """Les questions et réponses VISIBLES de la page, dans l'ordre."""
    qs = re.findall(r'<details class="q"[^>]*><summary>(.*?)</summary><div class="r">(.*?)</div></details>', s, re.S)
    if len(qs) < 6:
        sys.exit("⛔ la FAQ compte %d questions (6 au moins)" % len(qs))
    return [(plat_html(q), plat_html(r)) for q, r in qs]


def faq_ld(qs, langue):
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": langue,
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in qs]}
    return '<script type="application/ld+json">%s</script>' % serialiser(ld)


# ── Les lettres d'exemple : le vrai gabarit ──────────────────────────────
def exemples_html(exemples, T, langue, hab):
    T["dossier"].mkdir(parents=True, exist_ok=True)
    faits = []
    for x in exemples:
        d = {"occasion": T["occ"] + x["occasionNom"], "pour": x["pour"], "de": x["de"],
             "titre": x["titre"], "code": "", "lettre": x["lettre"], "photos": [],
             "depuis": "", "ouvre": x["ouvre"], "formule": x["formule"], "pied": True, "lien": T["lien"]}
        if langue != "fr":
            d["langue"] = langue
        # L'habillage de l'exemple : chaque valeur doit exister dans SA liste,
        # sinon le gabarit retomberait en silence sur la première.
        h = x.get("habillage")
        if h:
            for cle, v in h.items():
                if v not in [o["id"] for o in hab.get(cle, [])]:
                    sys.exit("⛔ exemple %s : %s=%r n'existe pas dans HABILLAGE" % (x["id"], cle, v))
            d["habillage"] = h
        if x.get("gratter"):
            d["gratter"] = x["gratter"]
        (T["dossier"] / ("%s.html" % x["id"])).write_text(poser(d), encoding="utf-8")
        faits.append(x["id"])
    return faits


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><radialGradient id="c" cx=".34" cy=".3" r=".75">'
           '<stop offset="0" stop-color="#b2434e"/><stop offset=".62" stop-color="#8c2f39"/><stop offset="1" stop-color="#6d1f27"/>'
           '</radialGradient></defs><circle cx="32" cy="32" r="29" fill="url(#c)"/>'
           '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#f0d6cf">M</text></svg>')
# ⚠️ Depuis le 2026-10-21, LA MARQUE est le cachet aux trois points (`_logo.py`) :
# l'onglet et le cachet de la barre la reprennent. L'ancien « M » ne sert que si
# le logo n'a pas été dessiné.
MARQUE = ICI / "logo" / "favicon.svg"


def favicon():
    return MARQUE.read_text(encoding="utf-8") if MARQUE.exists() else FAVICON


def cachet_mini():
    """Le cachet de la barre : la marque en image de fond, dans la page (aucune requête)."""
    if not MARQUE.exists():
        return ""
    return '.marque .cachet-mini{background:url("data:image/svg+xml,%s") center/contain no-repeat}' % \
        urllib.parse.quote(MARQUE.read_text(encoding="utf-8"), safe=" =:/,.-")   # « # » et « " » encodés


def construire(langue, dico, tons, fp):
    T = LANGUES[langue]
    paliers, plume, familles, occasions, questions = catalogue(T["creer"])
    hab = habillage(T["creer"])
    doc = json.loads(T["exemples"].read_text(encoding="utf-8"))
    exemples = doc["exemples"]
    demo = next(x for x in exemples if x["id"] == "afi")
    fiche, lettre = fiche_et_lettre(demo, questions, T)
    vetue = next((p for p in paliers if p["habillage"]), None)
    if not vetue:
        sys.exit("⛔ aucune offre ne porte l'habillage : la vitrine le vendrait pour rien")
    wa_fp = "https://wa.me/%s?text=%s" % (fp["whatsapp"], urllib.parse.quote(T["fp_msg"], safe=""))

    s = SOURCE.read_text(encoding="utf-8")
    if langue != "fr":
        s = _traduire.traduire(s, dico["_accueil_src.html"], "_accueil_src.html")
    remplacer = {
        "<!--__PLUME_PRIX__-->": e(fmt(plume, T)),
        "<!--__ENTREE_PRIX__-->": e(fmt(paliers[0]["prix"], T)),
        "<!--__TEXTE__-->": texte_feuille(T),
        "<!--__EXEMPLES__-->": cartes(exemples, T, tons),
        "<!--__FICHE__-->": fiche,
        "<!--__LETTRE_PLUME__-->": lettre,
        "<!--__CASIER__-->": casier(familles, occasions, T, emblemes(T["creer"])),
        "/*__BRUITS__*/": bruits(T["creer"]),
        "<!--__PRIX__-->": timbres(paliers, plume, T),
        "<!--__PASTILLES__-->": pastilles(hab, T),
        "<!--__HAB_DES__-->": e(T["hab_des"] % (vetue["nom"], fmt(vetue["prix"], T))),
        "<!--__FAQ_PRIX__-->": faq_prix(paliers, plume, T),
        "<!--__FP_PRIX__-->": e(fmt(fp["prix"], T)),
        "<!--__FP_WA__-->": e(wa_fp),
        "<!--__VOL__-->": vol(occasions, tons),
        "<!--__SON__-->": son(langue, T),
        "<!--__SON_CREDIT__-->": credit_son(T),
    }
    # Avec le bouton son, la barre se resserre au téléphone (la marque garde son cachet).
    if son(langue, T):
        if '<header class="barre">' not in s:
            sys.exit('⛔ <header class="barre"> introuvable : la barre ne pourrait pas se resserrer')
        s = s.replace('<header class="barre">', '<header class="barre a-son">', 1)
    blocs, regles = fonds(langue)
    for z, bloc_ in blocs.items():
        remplacer["<!--__FOND:%s__-->" % z] = bloc_
    remplacer["/*__FONDS__*/"] = regles + "\n" + cachet_mini()
    for k, v in remplacer.items():
        if k not in s:
            sys.exit("⛔ marqueur absent de la source : %s" % k)
        s = s.replace(k, v)
    # La typographie du texte visible, AVANT de lire la FAQ : le FAQPage dit
    # alors exactement ce que la page affiche.
    s = typographie(s, langue)
    # Le FAQPage est LU dans les questions visibles, une fois les prix posés.
    qs = questions_page(s)
    if "<!--__FAQ_LD__-->" not in s:
        sys.exit("⛔ marqueur absent de la source : <!--__FAQ_LD__-->")
    s = s.replace("<!--__FAQ_LD__-->", faq_ld(qs, langue))
    a, b = "/*__DONNEES__*/", "/*__FIN_DONNEES__*/"
    i, j = s.index(a), s.index(b) + len(b)
    dates = [{"id": o["id"], "nom": o["nom"], "jour": o["jour"]} for o in occasions if o["jour"]]
    if not dates:
        sys.exit("⛔ aucune occasion datée : la prochaine grande date n'aurait rien à dire")
    bientot = {k: (typo_texte(v, langue) if isinstance(v, str) else v) for k, v in T["bientot"].items()}
    bientot["dates"] = dates
    donnees = {"plume": plume, "paliers": [p["id"] for p in paliers], "exemples": [x["id"] for x in exemples],
               "bientot": bientot}
    s = s[:i] + serialiser(donnees) + s[j:]
    if "<!--__" in s:
        sys.exit("⛔ un marqueur n'a pas été remplacé")
    s = alleger(s)
    T["sortie"].parent.mkdir(exist_ok=True)
    T["sortie"].write_text(s, encoding="utf-8")
    faits = exemples_html(exemples, T, langue, hab)
    print("%s : %d octets · %d occasions · %d paliers · plume %s · %d questions · exemples : %s"
          % (T["sortie"].relative_to(ICI), len(s.encode("utf-8")), len(occasions), len(paliers),
             fmt(plume, T), len(qs), ", ".join(faits)))
    return {"paliers": paliers, "plume": plume, "qs": qs, "wa_fp": wa_fp}


def llms_bloc(langue, info, fp, niveau):
    """Un fichier qu'un agent lit sans rendre la page : tout y est TIRÉ de la
    page et du catalogue, aucun prix écrit à la main."""
    T, X = LANGUES[langue], LANGUES[langue]["llms"]
    h = "#" * niveau
    sep = " : " if langue == "fr" else ": "
    lignes = ["%s %s" % (h, X["offres"]), ""]
    for p in info["paliers"]:
        lignes.append("- %s%s%s F. %s" % (p["nom"], sep, milliers(p["prix"]).replace(NB, " "), p["desc"]))
    lignes.append("- " + X["plume"] % fmt(info["plume"], T).replace(NB, " "))
    lignes.append("- " + X["fp"] % fmt(fp["prix"], T).replace(NB, " "))
    lignes += ["", "%s %s" % (h, X["faq"]), ""]
    for q, r in info["qs"]:
        lignes += ["%s# %s" % (h, q), "", r.replace(NB, " "), ""]
    lignes += ["%s %s" % (h, X["pages"]), "",
               "- [%s](%s)" % (X["accueil"], T["lien"]),
               "- [%s](%s)" % (X["creer"], T["lien"].rstrip("/") + "/creer.html"),
               "- [%s](%s)" % (X["wa"], info["wa_fp"]),
               "- [%s](%s)" % (X["fp_ex"], SITE + X["fp_page"]), ""]
    return lignes


def ecrire_llms(infos, fp):
    fr, en = LANGUES["fr"]["llms"], LANGUES["en"]["llms"]
    lignes = ["# Ma lettre à…", "", "> " + fr["resume"], "", "> " + en["resume"], ""]
    lignes += llms_bloc("fr", infos["fr"], fp, 2)
    lignes += ["## In English", ""] + llms_bloc("en", infos["en"], fp, 3)
    LLMS.write_text("\n".join(lignes), encoding="utf-8", newline="\n")
    print("llms.txt : %d lignes, %d questions par langue" % (len(lignes), len(infos["fr"]["qs"])))


def main():
    _traduire.main()   # les pages anglaises d'abord : l'accueil anglais lit en/creer.html
    dico = _traduire.lire_dico()
    tons, fp = tons_de_cire(), offre_fp()
    infos = {"fr": construire("fr", dico, tons, fp), "en": construire("en", dico, tons, fp)}
    ecrire_llms(infos, fp)
    (ICI / "favicon.svg").write_text(favicon(), encoding="utf-8")


if __name__ == "__main__":
    main()
