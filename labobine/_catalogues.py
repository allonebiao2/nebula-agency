"""LA BOBINE · les catalogues des maisons, lus à la source, pour en faire des vidéos.

    python labobine/_catalogues.py        (écrit labobine/catalogues/, ignoré par git, publié par _dist.py)

Rien n'est recopié à la main :
- les articles et leurs prix viennent des lecteurs de LE STANDARD (whatsapp-agent/lecteurs/), qui lisent le
  fichier que le site de la maison sert déjà ; la maison change un prix, on republie, la vidéo suit ;
- les photos sont celles que ce même fichier nomme (champ `img`), réduites pour la vidéo ;
- les couleurs viennent de la feuille de style de la maison ;
- le numéro WhatsApp vient de la fiche de la maison dans LE STANDARD, et reste VIDE quand elle est vide.

Chaque catalogue s'ouvre par un lien non listé : https://labobine.pages.dev/#catalogue/<maison>.
"""
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(RACINE / "whatsapp-agent"))

from agent import maison as fiches  # noqa: E402
from agent.service import charger_catalogue  # noqa: E402
from agent.catalogue import formater_fcfa  # noqa: E402

SORTIE = ICI / "catalogues"
COTE_MAX = 1280

# le lien de la maison dans LA BOBINE → sa fiche du STANDARD, le dossier de ses photos, sa feuille de style
MAISONS = {
    "hillary-m-styl": {
        "fiche": "hillary.yaml",
        "photos": "clients/10-hillary-m-styl/assets/images",
        "css": "clients/10-hillary-m-styl/_v4/style-page.css",
        "couleurs": {"accent": "--rose", "fond": "--encre"},
    },
    "au-braise-dor": {
        "fiche": "braise-dor.yaml",
        "photos": "clients/09-au-braise-dor/experience/public",
        "css": "clients/09-au-braise-dor/experience/app/globals.css",
        "couleurs": {"accent": "--wash", "fond": "--encre"},
    },
}


def texte_propre(s: str) -> str:
    """Les espaces insécables fines (U+202F) n'existent pas dans toutes les polices : on garde l'insécable simple."""
    return s.replace(" ", " ")


def prix_court(prix) -> str:
    """Ce qui tient sur une étiquette de prix, sans jamais mentir : le prix exact, ou le plus bas précédé de « dès »."""
    if not prix.connu:
        return "Prix sur demande"
    if prix.mode == "simple":
        return texte_propre(formater_fcfa(prix.bas))
    return "dès " + texte_propre(formater_fcfa(prix.bas))


def numero_affiche(brut: str) -> str:
    """« 22951374793 » → « +229 51 37 47 93 ». On présente les chiffres de la fiche, on n'en change aucun."""
    chiffres = re.sub(r"\D", "", brut or "")
    if not chiffres:
        return ""
    if chiffres.startswith("229"):
        reste = chiffres[3:]
        return "+229 " + " ".join(reste[i:i + 2] for i in range(0, len(reste), 2))
    return "+" + chiffres


def couleurs(css: Path, noms: dict) -> dict:
    texte = css.read_text(encoding="utf-8")
    res = {}
    for role, var in noms.items():
        m = re.search(re.escape(var) + r"\s*:\s*(#[0-9a-fA-F]{6})\b", texte)
        if not m:
            raise SystemExit(f"{css} : la variable {var} est introuvable")
        res[role] = m.group(1).lower()
    return res


def photo(source: Path, cible: Path) -> bool:
    """Réduit la photo pour la vidéo (WebP). Rend True si elle est détourée (fond transparent)."""
    im = Image.open(source)
    im.load()
    detoure = False
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        detoure = im.getchannel("A").getextrema()[0] < 250
    else:
        im = im.convert("RGB")
    r = min(1.0, COTE_MAX / max(im.size))
    if r < 1:
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    im.save(cible, "WEBP", quality=84, method=5)
    return detoure


def construire(slug: str, conf: dict) -> dict:
    fiche = fiches.charger(RACINE / "whatsapp-agent" / "maisons" / conf["fiche"])
    cat = charger_catalogue(fiche, RACINE)
    dossier = SORTIE / slug
    (dossier / "photos").mkdir(parents=True, exist_ok=True)
    racine_photos = RACINE / conf["photos"]
    articles = []
    sans_photo = 0
    for categorie in cat.categories:
        for a in categorie.articles:
            entree = {"nom": a.nom, "categorie": categorie.label, "prix": texte_propre(a.prix.texte()), "prixCourt": prix_court(a.prix),
                      "photo": None, "detoure": False}
            if a.photo:
                src = racine_photos / a.photo.lstrip("/")
                if not src.exists():
                    raise SystemExit(f"{slug} : la photo « {a.photo} » de « {a.nom} » est introuvable ({src})")
                nom = f"{len(articles) + 1:02d}.webp"
                entree["detoure"] = photo(src, dossier / "photos" / nom)
                entree["photo"] = f"photos/{nom}"
            else:
                sans_photo += 1
            articles.append(entree)
    donnees = {
        "maison": fiche.nom,
        "slug": slug,
        "lu": date.today().isoformat(),
        "source": cat.source,
        "contact": numero_affiche(fiche.numero_whatsapp),
        "couleurs": couleurs(RACINE / conf["css"], conf["couleurs"]),
        "categories": [c.label for c in cat.categories if c.articles],
        "articles": articles,
    }
    (dossier / "catalogue.json").write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")
    poids = sum(f.stat().st_size for f in dossier.rglob("*") if f.is_file())
    print(f"  {fiche.nom} : {len(articles)} articles ({sans_photo} sans photo), contact {'« ' + donnees['contact'] + ' »' if donnees['contact'] else 'vide (fiche vide)'}, {poids // 1024} Ko")
    return donnees


def main():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    print("Catalogues de LA BOBINE, lus à la source :")
    for slug, conf in MAISONS.items():
        construire(slug, conf)


if __name__ == "__main__":
    main()
