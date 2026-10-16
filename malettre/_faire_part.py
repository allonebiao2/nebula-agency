# -*- coding: utf-8 -*-
"""MA LETTRE À… · fabrique un FAIRE-PART DE MARIAGE à partir de la fiche du couple.

    python malettre/_faire_part.py                                    # les deux exemples (FR, EN)
    python malettre/_faire_part.py malettre/faire-part/_couples/kossi-afiwa.json   # un vrai couple
    python malettre/_faire_part.py FICHE --sortie CHEMIN              # (les contrôles) écrire ailleurs

LE FAIRE-PART SUR DEMANDE (décision de Mongazi, 2026-10-16) : NEBULA le fait
pour le couple, 25 000 F payés hors de la caisse (`faire-part/offre.json`).
Le couple raconte, on remplit sa fiche, ce script fabrique la page, `_dist.py`
la publie à une adresse impossible à deviner :
    https://malettre.nebula-agency.online/f/<jeton>

⛔ LES FICHES DES VRAIS COUPLES NE VONT JAMAIS DANS GIT. Le dépôt est PUBLIC :
noms, date, lieux et numéro WhatsApp d'un couple n'ont rien à y faire, et
publier le jeton y publierait l'adresse. Elles vivent dans
`faire-part/_couples/` (ignoré par git), avec leurs pages dans
`faire-part/_couples/sortie/`. Seule l'EMPREINTE du jeton (sha256) est notée
dans `faire-part/publies.txt` : `_dist.py` refuse de construire si une page
publiée manque sur ce disque, sinon un déploiement fait d'ailleurs l'effacerait
du site (un déploiement Pages est un instantané complet).

⛔ Tout passe par `_injecter.serialiser` (le seul endroit qui neutralise
`</script>` et U+2028) ; le gabarit n'écrit jamais du HTML avec les données.
"""
import base64
import datetime
import hashlib
import io
import json
import pathlib
import re
import secrets
import sys
import urllib.parse

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from _injecter import serialiser  # noqa: E402

DOSSIER = ICI / "faire-part"
GABARIT = DOSSIER / "gabarit.html"
COUPLES = DOSSIER / "_couples"
SORTIE = COUPLES / "sortie"
PUBLIES = DOSSIER / "publies.txt"
SITE = "https://malettre.nebula-agency.online"
EXEMPLES = [(DOSSIER / "exemple.json", DOSSIER / "exemple.html"),
            (DOSSIER / "exemple.en.json", DOSSIER / "exemple-en.html")]
DEBUT, FIN = "/*FP_DONNEES*/", "/*FIN_FP_DONNEES*/"

CIRES = ("or", "bordeaux", "nuit", "sapin", "rose")
PLUIES = ("petales", "confettis", "etoiles", "aucune")
# Le même motif que le gabarit : un lien de carte est Google Maps, en https, ou rien.
CARTE = re.compile(r"^https://(www\.google\.[a-z.]+/maps|maps\.google\.[a-z.]+|maps\.app\.goo\.gl|goo\.gl/maps)\b")
ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"   # sans l, o, 0, 1 : lisible dans un message
MAX_PHOTOS, MAX_OCTETS = 12, 3_500_000


def jeton():
    """16 caractères tirés au hasard (≈ 80 bits) : l'adresse ne se devine pas."""
    return "".join(secrets.choice(ALPHABET) for _ in range(16))


def empreinte(j):
    return hashlib.sha256(j.encode("utf-8")).hexdigest()


def date_ok(s):
    try:
        return datetime.date.fromisoformat(str(s))
    except ValueError:
        return None


def verifier(f, chemin):
    """Toutes les fautes d'un coup, ou une fiche propre. Rien n'est deviné."""
    fautes = []
    exige = lambda cond, msg: cond or fautes.append(msg)
    texte = lambda cle, maxi, requis=True: (
        exige(isinstance(f.get(cle), str) and (0 < len(f[cle].strip()) <= maxi), "%s : texte de 1 à %d caractères" % (cle, maxi))
        if requis or f.get(cle) not in (None, "") else True)

    exige(f.get("langue") in ("fr", "en"), "langue : fr ou en")
    noms = f.get("noms")
    exige(isinstance(noms, list) and len(noms) == 2 and all(isinstance(n, str) and 0 < len(n.strip()) <= 30 for n in noms),
          "noms : deux prénoms de 1 à 30 caractères")
    jour = date_ok(f.get("date"))
    exige(jour is not None, "date : AAAA-MM-JJ")
    exige(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(f.get("heure", ""))), "heure : HH:MM")
    exige(re.fullmatch(r"[+-](0\d|1[0-4]):(00|30|45)", str(f.get("fuseau", ""))), "fuseau : +01:00 (Bénin), +00:00 (Togo, Côte d'Ivoire)")
    texte("ville", 60)
    texte("familles", 120, False)
    texte("phrase", 60, False)
    texte("tenue", 300, False)
    texte("mot", 600, False)
    teintes = f.get("teintes") or []
    exige(isinstance(teintes, list) and len(teintes) <= 6 and all(re.fullmatch(r"#[0-9a-fA-F]{6}", str(c)) for c in teintes),
          "teintes : au plus 6 couleurs #RRGGBB")
    prog = f.get("programme")
    exige(isinstance(prog, list) and 1 <= len(prog) <= 8, "programme : de 1 à 8 moments")
    for i, p in enumerate(prog if isinstance(prog, list) else []):
        exige(isinstance(p, dict) and re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(p.get("heure", ""))), "programme[%d].heure : HH:MM" % i)
        exige(isinstance(p, dict) and isinstance(p.get("quoi"), str) and 0 < len(p["quoi"].strip()) <= 60, "programme[%d].quoi : 1 à 60 caractères" % i)
        exige(isinstance(p, dict) and isinstance(p.get("lieu"), str) and 0 < len(p["lieu"].strip()) <= 120, "programme[%d].lieu : 1 à 120 caractères" % i)
        exige(not isinstance(p, dict) or not p.get("carte") or CARTE.match(str(p["carte"])), "programme[%d].carte : un lien Google Maps en https" % i)
    exige(f.get("cire", "or") in CIRES, "cire : " + ", ".join(CIRES))
    exige(f.get("pluie", "petales") in PLUIES, "pluie : " + ", ".join(PLUIES))
    if f.get("exemple"):
        exige(not f.get("whatsapp"), "un exemple n'a pas de numéro : ses réponses ne partent nulle part")
    else:
        # Le numéro DES MARIÉS, au format international, sans + ni espace :
        # 229 + les 10 chiffres béninois (le 01 GARDÉ), 228 + 8 au Togo, 225 + 10 en Côte d'Ivoire.
        exige(re.fullmatch(r"\d{10,15}", str(f.get("whatsapp", ""))), "whatsapp : le numéro des mariés, indicatif compris, chiffres seuls")
    if f.get("repondre_avant"):
        rav = date_ok(f["repondre_avant"])
        exige(rav is not None and (jour is None or rav <= jour), "repondre_avant : AAAA-MM-JJ, avant le jour J")
    photos = f.get("photos") or []
    exige(isinstance(photos, list) and len(photos) <= MAX_PHOTOS, "photos : au plus %d" % MAX_PHOTOS)
    for p in photos if isinstance(photos, list) else []:
        exige((chemin.parent / str(p)).is_file(), "photo introuvable : %s" % p)
    if jour and jour < datetime.date.today():
        fautes.append("date : le %s est passé" % jour.isoformat())
    if fautes:
        sys.exit("⛔ %s : %d faute(s), rien n'est écrit :\n  %s" % (chemin.name, len(fautes), "\n  ".join(fautes)))


def photo_donnee(chemin):
    """Une photo devient une DONNÉE (data:), jamais un lien : réduite à 1 200 px."""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(chemin)).convert("RGB")
    im.thumbnail((1200, 1200))
    tampon = io.BytesIO()
    im.save(tampon, "JPEG", quality=78, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(tampon.getvalue()).decode("ascii")


def carte(p, ville):
    if p.get("carte"):
        return p["carte"]
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote("%s, %s" % (p["lieu"], ville))


def fabriquer(chemin, sortie=None):
    chemin = pathlib.Path(chemin).resolve()
    f = json.loads(chemin.read_text(encoding="utf-8"))
    verifier(f, chemin)
    photos = [photo_donnee(chemin.parent / p) for p in f.get("photos") or []]
    if sum(len(p) for p in photos) > MAX_OCTETS:
        sys.exit("⛔ les photos pèsent plus de %.1f Mo une fois embarquées : en retirer" % (MAX_OCTETS / 1e6))
    d = {
        "langue": f["langue"], "exemple": bool(f.get("exemple")), "noms": [n.strip() for n in f["noms"]],
        "familles": f.get("familles", ""), "phrase": f.get("phrase", ""),
        "date": f["date"], "heure": f["heure"], "fuseau": f["fuseau"], "ville": f["ville"],
        "programme": [{"heure": p["heure"], "quoi": p["quoi"], "lieu": p["lieu"], "carte": carte(p, f["ville"])}
                      for p in f["programme"]],
        "tenue": f.get("tenue", ""), "teintes": f.get("teintes") or [], "mot": f.get("mot", ""),
        "photos": photos, "whatsapp": str(f.get("whatsapp", "")), "repondre_avant": f.get("repondre_avant", ""),
        "cire": f.get("cire", "or"), "pluie": f.get("pluie", "petales"),
        "lien": SITE + ("/en/" if f["langue"] == "en" else "/"),
    }
    g = GABARIT.read_text(encoding="utf-8")
    a, b = g.index(DEBUT), g.index(FIN) + len(FIN)
    # Les marqueurs restent (des commentaires JavaScript) : le contrôle relit les
    # données d'une page publiée, et une page se refabrique sur elle-même.
    page = g[:a] + DEBUT + serialiser(d) + FIN + g[b:]
    if not f.get("exemple") and sortie is None:
        # La première fabrication tire le jeton et l'écrit DANS la fiche : la
        # page garde son adresse à chaque nouvelle version.
        if not re.fullmatch(r"[%s]{16}" % ALPHABET, str(f.get("jeton", ""))):
            f["jeton"] = jeton()
            chemin.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        sortie = SORTIE / ("%s.html" % f["jeton"])
        noter(f["jeton"])
    sortie = pathlib.Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(page, encoding="utf-8")
    poids = len(page.encode("utf-8"))
    print("%s : %d Ko, %d moment(s), %d photo(s)" % (sortie.name, poids // 1024, len(d["programme"]), len(photos)))
    if not f.get("exemple") and "jeton" in f and sortie.parent == SORTIE:
        print("  adresse (après publication) : %s/f/%s" % (SITE, f["jeton"]))
    return sortie


def noter(j):
    """L'empreinte du jeton, jamais le jeton : le dépôt est public."""
    lignes = PUBLIES.read_text(encoding="utf-8").splitlines() if PUBLIES.exists() else []
    if empreinte(j) not in lignes:
        PUBLIES.write_text("\n".join(lignes + [empreinte(j)]) + "\n", encoding="utf-8", newline="\n")


def main():
    args = sys.argv[1:]
    if not args:
        for fiche, page in EXEMPLES:
            fabriquer(fiche, page)
        return
    sortie = None
    if "--sortie" in args:
        i = args.index("--sortie")
        sortie = args[i + 1]
        args = args[:i] + args[i + 2:]
    for fiche in args:
        fabriquer(fiche, sortie)


if __name__ == "__main__":
    main()
