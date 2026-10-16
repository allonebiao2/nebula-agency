"""Les faits de Grain d'Esthétique, LUS dans sa vitrine, pour la pub de 35 s.

Rien n'est recopié à la main : un prix, une heure ou un numéro retapé dans la vidéo
serait une deuxième vérité, et le jour où la vitrine change, c'est la cliente qui
trouve porte close (règle de l'affiche de l'institut, 2026-09-02).

Source : clients/01-grain-esthetique/grain-esthetique-LIVE.html (le fichier publié).
Sortie : src/grain35/faits.ts

    python _outils/grain35_faits.py
"""
import html as H
import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SOURCE = ICI.parent / "clients/01-grain-esthetique/grain-esthetique-LIVE.html"
SORTIE = ICI / "src/grain35/faits.ts"
JOURS = {"Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mer", "Thursday": "Jeu",
         "Friday": "Ven", "Saturday": "Sam", "Sunday": "Dim"}


def texte(s):
    return H.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# Les soins montrés à l'écran, par leur NOM sur la vitrine. ⚠️ Pas « le moins cher
# de la section » : celui du visage est un remplissage de faux cils (7 000 F), celui
# des ongles un vernis « à l'unité » (2 000 F). « Soins du visage dès 7 000 F » serait
# faux. Un nom absent fait échouer l'outil : jamais de prix inventé à la place.
SOINS = {
    "visage": "Soin visage mini Sothys",
    "corps": "Massage du corps manuel",
    "mainsPieds": "Beauté mains + pieds (forfait)",
}


def prix_de(t, nom):
    """Le prix écrit à côté du nom du soin (le nom tel quel, ou avec « & » échappé)."""
    for forme in (nom, H.escape(nom, quote=False)):
        m = re.search(r'class="soin-name">' + re.escape(forme) + r'</div>.*?class="soin-price">([^<]+)<', t, re.S)
        if m:
            return texte(m.group(1))
    raise SystemExit(f"⛔ soin introuvable sur la vitrine : {nom}")


def section(t, ident, fin):
    i = t.find(f'id="{ident}"')
    j = t.find(fin, i + 10) if fin else len(t)
    assert i > 0, ident
    return t[i:j]


def main():
    t = SOURCE.read_text(encoding="utf-8")
    t = re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,", t)
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', t, re.S).group(1))
    tel = ld["telephone"]  # +2290197085576
    nat = tel.replace("+229", "")
    tel_lisible = " ".join(nat[i:i + 2] for i in range(0, len(nat), 2))
    h = ld["openingHoursSpecification"][0]
    jours = [JOURS[j] for j in h["dayOfWeek"]]
    horaires = f"{jours[0]}–{jours[-1]} · {h['opens'].replace(':00', 'h')}–{h['closes'].replace(':00', 'h')}"

    wa = re.search(r'class="hero-cta" href="(https://wa\.me/[^"]+)"', t).group(1)
    assert nat.lstrip("0") in wa.replace("229", "", 1) or nat in wa, "le lien WhatsApp ne porte pas le numéro du JSON-LD"
    maisons = re.findall(r'class="maison-badge">([^<]+)<', t)
    stats = [(texte(v), texte(l)) for v, l in
             re.findall(r'class="stat-val">(.*?)</div><div class="stat-lab">(.*?)</div>', t)]
    vision = texte(re.search(r'class="apropos-text">(.*?)</div>', t, re.S).group(1))
    devise = re.search(r"la beauté est un art de vivre", vision).group(0)

    avances = section(t, "avances", 'id="hommes"')
    cartes = re.findall(r'class="avance-name">([^<]+)<.*?class="avance-desc">(.*?)</div>'
                        r'.*?class="avance-price">([^<]+)<', avances, re.S)
    hyalu = next(c for c in cartes if "Hyaluropen" in c[0])
    titre_hommes = texte(re.search(r'class="hommes-title">(.*?)</div>', t, re.S).group(1))

    faits = {
        "nom": ld["name"],
        "quartier": ld["address"]["streetAddress"].replace("-", " "),
        "ville": ld["address"]["addressLocality"],
        "telephone": tel_lisible,
        "whatsapp": wa,
        "horaires": horaires,
        "surRendezVous": "Sur rendez-vous uniquement" if "Sur rendez-vous uniquement" in t else None,
        "maisons": maisons,
        "stats": [{"valeur": v, "libelle": l} for v, l in stats],
        "devise": devise[0].upper() + devise[1:] + ".",
        "fondatrice": re.search(r"Fondé à Cotonou par ([A-ZÉ][\w-]+ [A-ZÉ][\w-]+)", vision).group(1),
        "soins": {cle: {"nom": nom, "prix": prix_de(t, nom)} for cle, nom in SOINS.items()},
        "hyaluropen": {
            "nom": texte(hyalu[0]).replace(" — ", " · "),
            "details": [texte(x) for x in re.split(r"<br\s*/?>", hyalu[1])],
            "prix": texte(hyalu[2]),
        },
        "espaceHommes": titre_hommes,
        "site": ld["url"].replace("https://", "").rstrip("/"),
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        "/**\n * Les faits de Grain d'Esthétique, LUS dans sa vitrine par _outils/grain35_faits.py.\n"
        " * Ne pas éditer à la main : la vitrine change, on relance l'outil.\n */\n"
        f"export const FAITS = {json.dumps(faits, ensure_ascii=False, indent='\t')} as const;\n",
        encoding="utf-8")
    print(json.dumps(faits, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
