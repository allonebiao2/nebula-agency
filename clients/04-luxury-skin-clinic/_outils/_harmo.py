# -*- coding: utf-8 -*-
"""_harmo.py · la page Harmonisation faciale tirée de SES données (26/11).

La seule source des techniques et des tarifs est le bloc JSON `harmo-donnees` de harmonisation-faciale.html
(les textes et les prix de ses trois flyers, mot pour mot). Ce script en tire, sans rien recopier à la main :
  · le tableau visible des techniques (entre <!--HARMO-DEBUT--> et <!--HARMO-FIN-->), lisible sans JavaScript ;
  · le balisage JSON-LD (à la place de <!--JSONLD-HARMO--> ou du bloc qu'il a déjà posé).
À relancer après tout changement de tarif :  python _outils/_harmo.py
Il refuse d'écrire si un tarif manque ou si une fourchette est aplatie.
"""
import html
import io
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PAGE = ICI / "harmonisation-faciale.html"
URL = "https://luxuryclub229.com/harmonisation-faciale"

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass


def fcfa(n):
    return f"{n:,}".replace(",", " ") + " FCFA"


def prix(z):
    if "pMin" in z:
        return f"{z['pMin']:,}".replace(",", " ") + " à " + fcfa(z["pMax"])
    return fcfa(z["p"]) + (" la séance" if "forfait" in z else "")


def forfait(z):
    """Le forfait (Mésothérapie amincissante, 26/11) : sa propre case, jamais confondue avec la séance."""
    f = z.get("forfait")
    return f"Forfait {f['seances']} séances : {fcfa(f['p'])}" if f else ""


def lire(s):
    m = re.search(r'<script id="harmo-donnees" type="application/json">(.*?)</script>', s, re.S)
    if not m:
        raise SystemExit("bloc harmo-donnees introuvable")
    d = json.loads(m.group(1))
    for t in d:
        for z in t["zones"]:
            if "p" not in z and not ("pMin" in z and "pMax" in z):
                raise SystemExit(f"tarif manquant : {t['nom']} · {z['nom']}")
            if "pMin" in z and z["pMin"] >= z["pMax"]:
                raise SystemExit(f"fourchette fausse : {t['nom']} · {z['nom']}")
    return d


def tableau(d):
    e = html.escape
    out = []
    for i, t in enumerate(d):
        lignes = []
        for j, z in enumerate(t["zones"]):
            det = f"<small>{e(z['detail'])}</small>" if z.get("detail") else ""
            ff = z.get("forfait")
            fo = (f"<small>{e(forfait(z))} <s>{e(fcfa(ff['avant']))}</s></small>" if ff and ff.get("avant")
                  else (f"<small>{e(forfait(z))}</small>" if ff else ""))
            lignes.append(
                f'        <tr><th scope="row">{e(z["nom"])}{det}</th><td>{e(prix(z))}{fo}'
                f'<button type="button" data-consult data-t="{i}" data-z="{j}">Demander</button></td></tr>')
        note = f'\n      <p class="note">{e(t["note"])}</p>' if t.get("note") else ""
        out.append(f'''    <article class="tech" id="{e(t["id"])}">
      <img src="{e(t["flyer"])}" alt="{e(t["nom"])} : les zones du visage et leurs tarifs, sur le visuel de Luxury Skin Clinic" width="900" height="1600" loading="lazy" decoding="async">
      <div>
        <div class="famille">{e(t.get("famille", "Harmonisation faciale"))}</div>
        <h3>{e(t["nom"])}</h3>
        <p>{e(t["texte"])}</p>
        <table class="tarifs">
          <caption class="sr-only">{e(t["nom"])} : zones et tarifs</caption>
          <tbody>
{chr(10).join(lignes)}
          </tbody>
        </table>{note}
      </div>
    </article>''')
    return "\n".join(out)


def jsonld(d):
    cat = []
    for t in d:
        offres = []
        for z in t["zones"]:
            o = {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{t['nom']} · {z['nom']}"},
                 "priceCurrency": "XOF"}
            if z.get("detail"):
                o["itemOffered"]["description"] = z["detail"]
            if "pMin" in z:
                o["priceSpecification"] = {"@type": "PriceSpecification", "minPrice": z["pMin"], "maxPrice": z["pMax"], "priceCurrency": "XOF"}
            else:
                o["price"] = z["p"]
            offres.append(o)
            if z.get("forfait"):
                offres.append({"@type": "Offer", "priceCurrency": "XOF", "price": z["forfait"]["p"],
                               "itemOffered": {"@type": "Service", "name": f"{t['nom']} · {z['nom']} · forfait {z['forfait']['seances']} séances"}})
        cat.append({"@type": "OfferCatalog", "name": t["nom"], "description": t["texte"], "itemListElement": offres})
    tous = [z.get("p", z.get("pMin")) for t in d for z in t["zones"]] + [z["pMax"] for t in d for z in t["zones"] if "pMax" in z]
    doc = {
        "@context": "https://schema.org", "@type": "HealthAndBeautyBusiness",
        "name": "Luxury Skin Clinic · Harmonisation faciale", "url": URL,
        "image": "https://luxuryclub229.com/assets/images/og-harmonisation.jpg",
        "telephone": "+2290167975626",
        "address": {"@type": "PostalAddress", "addressLocality": "Cotonou", "addressCountry": "BJ"},
        "sameAs": ["https://www.instagram.com/luxuryclub229"],
        "priceRange": f"{fcfa(min(tous)).replace(' FCFA', '')} - {fcfa(max(tous))}",
        "parentOrganization": {"@type": "Organization", "name": "Luxury Club 229", "url": "https://luxuryclub229.com/"},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Harmonisation faciale", "itemListElement": cat},
    }
    return '<script type="application/ld+json" id="jsonld-harmo">' + json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "</script>"


def main():
    s = PAGE.read_text(encoding="utf-8")
    d = lire(s)
    a, b = "<!--HARMO-DEBUT-->", "<!--HARMO-FIN-->"
    if a not in s or b not in s:
        raise SystemExit("marqueurs du tableau introuvables")
    s = s[:s.index(a) + len(a)] + "\n" + tableau(d) + "\n" + s[s.index(b):]
    bloc = jsonld(d)
    if '<script type="application/ld+json" id="jsonld-harmo">' in s:
        s = re.sub(r'<script type="application/ld\+json" id="jsonld-harmo">.*?</script>', lambda m: bloc, s, count=1, flags=re.S)
    else:
        s = s.replace("<!--JSONLD-HARMO-->", bloc, 1)
    PAGE.write_text(s, encoding="utf-8")
    n = sum(len(t["zones"]) for t in d)
    print(f"{len(d)} techniques, {n} tarifs : tableau et JSON-LD écrits.")
    for t in d:
        print(f"  {t['nom']:20} " + " · ".join(f"{z['nom']} {prix(z)}" for z in t["zones"]))


if __name__ == "__main__":
    main()
