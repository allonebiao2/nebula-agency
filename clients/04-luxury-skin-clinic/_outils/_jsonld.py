# -*- coding: utf-8 -*-
"""
_jsonld.py — le balisage de la clinique, LU dans la page.

    python _outils/_jsonld.py

⚠️ LES SOINS NE SONT PAS RECOPIES, ILS SONT LUS dans le tableau `SERVICES` de
   `luxury-skin-clinic.html`. Un prix recopié est une deuxième vérité : le jour
   où Gloria change un tarif, le balisage mentirait sans que rien ne le dise.
   C'est la règle de la maison (Hillary, Au Braisé d'Or).

⛔ ON NE PROMET QUE CE QUE LA PAGE MONTRE. Pas de note, pas d'avis, pas
   d'adresse de rue : Gloria n'a jamais donné l'adresse exacte, et une adresse
   inventée dans un balisage local est pire qu'une adresse absente.

Le script est idempotent : il remplace le bloc précédent.
"""
import io, json, os, re, sys

# La console Windows est en cp1252 : sans ca, l'outil MEURT en affichant son
# propre rapport, apres avoir fait son travail (vu le 2026-09-05).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(RACINE, "luxury-skin-clinic.html")

# les horaires que Gloria a donnés le 2026-09-05
JOURS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
OUVRE, FERME = "10:00", "17:00"


def lire_questions(src):
    """Releve les questions VISIBLES de la section #questions.

    ⛔ UN `FAQPage` NE SE RECOPIE PAS. Un balisage qui declare des questions
       que la page n'affiche pas est un balisage qui ment — defaut trouve chez
       Hillary le 2026-08-16, ou le `FAQPage` existait sans une seule question
       a l'ecran. Ici, si la question disparait de la page, elle disparait du
       balisage le jour meme.
    """
    i = src.find('<section id="questions">')
    j = src.find("</section>", i)
    if i < 0 or j < 0:
        return []
    bloc = src[i:j]
    qs = []
    for m in re.finditer(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", bloc, re.S):
        q = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        r = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if q and r:
            qs.append((q, r))
    return qs


def lire_soins(src):
    """Relève le nom, le prix et la famille de chaque soin du tableau SERVICES."""
    i = src.find("const SERVICES=[")
    j = src.find("\n];", i)
    if i < 0 or j < 0:
        sys.exit("SERVICES introuvable")
    bloc = src[i:j]
    soins = []
    for m in re.finditer(r"\{g:'([^']+)',n:'([^']+)'.*?p:(\d+),", bloc):
        soins.append({"famille": m.group(1), "nom": m.group(2).replace("\\'", "'"),
                      "prix": int(m.group(3))})
    return soins


def main():
    src = io.open(P, encoding="utf-8").read()
    soins = lire_soins(src)
    if len(soins) < 5:
        sys.exit("seulement %d soins relevés : le format a bougé" % len(soins))

    prix = sorted(s["prix"] for s in soins if s["prix"] > 0)
    fiche = {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": "Luxury Skin Clinic, Luxury Club 229",
        "url": "https://luxuryclub229.com/luxury-skin-clinic",
        "image": "https://luxuryclub229.com/assets/images/og-luxury-skin-clinic.jpg",
        "description": "Luxury Skin Clinic : clinique esthétique à Cotonou, soins du visage, "
                       "du corps et capillaires, réalisés par Mme Sabrina, esthéticienne diplômée.",
        "telephone": "+2290167975626",
        "priceRange": "%s - %s FCFA" % ("{:,}".format(prix[0]).replace(",", " "),
                                        "{:,}".format(prix[-1]).replace(",", " ")),
        "currenciesAccepted": "XOF",
        "address": {"@type": "PostalAddress", "addressLocality": "Cotonou", "addressCountry": "BJ"},
        "areaServed": "Cotonou, Bénin",
        "sameAs": ["https://www.instagram.com/luxuryclub229"],
        # les horaires : la page les annonce en toutes lettres, le balisage les dit aussi
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["https://schema.org/" + j for j in JOURS],
            "opens": OUVRE, "closes": FERME,
        }],
        "employee": {"@type": "Person", "name": "Mme Sabrina",
                     "jobTitle": "Esthéticienne diplômée"},
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Soins Luxury Skin Clinic",
            "itemListElement": [{
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "name": s["nom"],
                                "serviceType": {"visage": "Soin du visage", "corps": "Soin du corps",
                                                "capillaires": "Soin capillaire",
                                                "complet": "Soin complet"}.get(s["famille"], "Soin"),
                                "provider": {"@type": "HealthAndBeautyBusiness",
                                             "name": "Luxury Skin Clinic"}},
                "price": s["prix"], "priceCurrency": "XOF",
                "availability": "https://schema.org/InStock",
            } for s in soins],
        },
    }

    questions = lire_questions(src)
    if len(questions) < 4:
        sys.exit("seulement %d questions relevees : la FAQ visible a bouge" % len(questions))

    graphe = [fiche, {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": r},
        } for q, r in questions],
    }]

    bloc = ('<script type="application/ld+json">'
            + json.dumps(graphe if len(graphe) > 1 else fiche,
                          ensure_ascii=False, separators=(",", ":"))
            + "</script>")
    neuf, n = re.subn(r'<script type="application/ld\+json">.*?</script>', bloc, src, count=1, flags=re.S)
    if n != 1:
        sys.exit("bloc JSON-LD introuvable")

    # ⚠️ un balisage qui casse la page est pire qu'un balisage absent
    json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', neuf, re.S).group(1))
    io.open(P, "w", encoding="utf-8", newline="\n").write(neuf)
    print("  balisage refait : %d soins lus, prix de %s à %s FCFA"
          % (len(soins), prix[0], prix[-1]))
    print("  horaires : lundi→samedi %s-%s" % (OUVRE, FERME))
    print("  %d questions LUES dans la FAQ visible de la page" % len(questions))
    for s in soins:
        print("     %-34s %7d F" % (s["nom"], s["prix"]))


if __name__ == "__main__":
    main()
