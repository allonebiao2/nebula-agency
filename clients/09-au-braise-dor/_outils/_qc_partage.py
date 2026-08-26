# -*- coding: utf-8 -*-
"""
CONTRÔLE DU PARTAGE ET DES DONNÉES STRUCTURÉES — Au Braisé d'Or.

    python _outils/_qc_partage.py

Ce contrôle ne demande AUCUN navigateur : il lit le fichier réellement servi et
valide le balisage contre les données de la carte.

⚠️ Un balisage n'est pas une déclaration d'intention : il ne doit annoncer que
   ce que la page pratique. On compare donc au TypeScript, plat par plat.
"""
import io, json, os, re, sys

for _f in (sys.stdout, sys.stderr):
    try: _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(ICI, "..", "experience", "out"))
DATA = os.path.normpath(os.path.join(ICI, "..", "experience", "data", "carte.ts"))

ok, ko = [], []


def dire(bon, txt):
    (ok if bon else ko).append(txt)
    print(("  vert  " if bon else "  ROUGE ") + txt)


def main():
    html = io.open(os.path.join(OUT, "index.html"), encoding="utf-8").read()

    # 1 · l'aperçu WhatsApp
    for prop, attendu in [("og:image", "og.jpg"), ("og:title", "Braisé"),
                          ("og:description", "braise"), ("og:url", "au-braise-dor"),
                          ("og:type", "website"), ("og:locale", "fr_FR"),
                          ("twitter:card", "summary_large_image")]:
        m = re.search(r'(?:property|name)="%s"\s+content="([^"]*)"' % re.escape(prop), html)
        dire(bool(m) and attendu.lower() in m.group(1).lower(),
             "%-16s → %s" % (prop, (m.group(1)[:58] if m else "ABSENT")))

    dire('rel="canonical"' in html, "adresse canonique déclarée")

    # 2 · l'image existe vraiment, en JPEG, et pèse un poids d'aperçu
    p = os.path.join(OUT, "og.jpg")
    dire(os.path.exists(p), "og.jpg présent dans le dossier publié")
    if os.path.exists(p):
        tete = io.open(p, "rb").read(3)
        dire(tete == b"\xff\xd8\xff", "og.jpg est un VRAI JPEG (pas un WebP renommé)")
        dire(os.path.getsize(p) < 300 * 1024,
             "og.jpg pèse %.0f Ko" % (os.path.getsize(p) / 1024))

    for f in ("robots.txt", "sitemap.xml", "404.html", "favicon.ico"):
        dire(os.path.exists(os.path.join(OUT, f)), "%s publié" % f)

    # 3 · les données structurées
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    dire(bool(m), "un bloc de données structurées est présent")
    if not m:
        return 1
    d = json.loads(m.group(1))
    dire(d.get("@type") == "Restaurant", "type déclaré : %s" % d.get("@type"))
    dire(bool(d.get("telephone")), "téléphone : %s" % d.get("telephone"))
    dire("streetAddress" not in json.dumps(d),
         "⛔ aucune adresse de rue inventée (la maison ne l'a pas donnée)")
    dire("aggregateRating" not in json.dumps(d) and "review" not in json.dumps(d).lower(),
         "⛔ aucune note ni avis inventés")

    # 4 · le balisage contre la carte, plat par plat
    ts = io.open(DATA, encoding="utf-8").read()

    def plats_ts():
        """Chaque plat de la carte, avec ses TROIS prix possibles.

        ⚠️ On lit l'objet entier en comptant les accolades. Une expression
        régulière « du n jusqu'au p » attrapait le prix du plat SUIVANT dès
        qu'un plat était écrit sur plusieurs lignes (les sauces le sont)."""
        out = []
        for m in re.finditer(r'\{ n: "([^"]*)"', ts):
            i, n = m.start(), 1
            j = i + 1
            while j < len(ts) and n:
                n += (ts[j] == "{") - (ts[j] == "}")
                j += 1
            corps = ts[i:j]
            val = lambda cle: int(re.search(r"\b%s: (\d+)" % cle, corps).group(1)) \
                if re.search(r"\b%s: (\d+)" % cle, corps) else 0
            # ⚠️ QUATRIÈME FAÇON D'AVOIR UN PRIX (2026-08-26) : un BARÈME à N
            #    crans. La glace se vend à la boule, 1 000 / 1 500 / 2 500 F.
            #    Sans cette lecture, le contrôle accusait le balisage d'annoncer
            #    des prix « absents de la carte » alors qu'ils y sont — et pire,
            #    il n'aurait rien dit si un cran avait vraiment disparu.
            mp = re.search(r"paliers: \[(.*?)\]\]", corps)
            pal = [int(x) for x in re.findall(r",\s*(\d+)\]", mp.group(1) + "]")] if mp else []
            out.append((m.group(1), val("p"), val("p2"), val("pMax"), pal))
        return out

    carte_ts = plats_ts()
    noms_ts = [x[0] for x in carte_ts]
    prix_ts = [x[1] for x in carte_ts]
    hauts = [max([x[1], x[2], x[3]] + x[4]) for x in carte_ts]

    items = [i for s in d["hasMenu"]["hasMenuSection"] for i in s["hasMenuItem"]]
    dire(len(items) == len(noms_ts),
         "%d plats balisés, %d dans la carte" % (len(items), len(noms_ts)))
    dire(len(d["hasMenu"]["hasMenuSection"]) == ts.count("\n    id: "),
         "%d rubriques balisées" % len(d["hasMenu"]["hasMenuSection"]))

    def liste_offres(i):
        o = i.get("offers")
        return [] if o is None else (o if isinstance(o, list) else [o])

    def montants(o):
        """Un prix, ou les deux bornes d'une fourchette."""
        if o.get("@type") == "AggregateOffer":
            return [int(o["lowPrice"]), int(o["highPrice"])]
        return [int(o["price"])]

    offres = [i for i in items if liste_offres(i)]
    zero = [i["name"] for i in offres
            for o in liste_offres(i) for v in montants(o) if v <= 0]
    dire(not zero, "⛔ aucune offre à 0 F%s" % ("" if not zero else " → %s" % zero))

    # ⚠️ Le premier jet ne lisait que `p` : le balisage annonçait « jusqu'à
    #    5 000 F » alors que les sauces montent à 6 000 F « tout dedans ».
    # ⚠️ `toLocaleString("fr-FR")` sépare les milliers avec une espace fine
    #    INSÉCABLE (U+202F). On relit les nombres, on ne compare pas du texte.
    annonce = [int(x) for x in re.findall(r"\d+", re.sub(r"\s", "", d["priceRange"]))]
    vrai = [min(p for p in prix_ts if p > 0), max(hauts)]
    dire(annonce == vrai, "fourchette annoncée %s F, la carte va de %d à %d F"
         % (" à ".join(str(x) for x in annonce), vrai[0], vrai[1]))

    fourchettes = [(n, hm) for n, p, p2, hm, pal in carte_ts if hm]
    balisees = {i["name"]: liste_offres(i) for i in items}
    manquantes = [n for n, hm in fourchettes
                  if not any(o.get("@type") == "AggregateOffer" and int(o["highPrice"]) == hm
                             for o in balisees.get(n, []))]
    dire(not manquantes,
         "les %d sauces à fourchette portent leur borne haute%s"
         % (len(fourchettes), "" if not manquantes else " → %s" % manquantes[:3]))

    deux = [(n, p2) for n, p, p2, hm, pal in carte_ts if p2]
    ratees = [n for n, p2 in deux
              if not any(int(o.get("price", 0)) == p2 for o in balisees.get(n, []))]
    dire(not ratees, "les %d plats à deux tailles ont leurs deux prix%s"
         % (len(deux), "" if not ratees else " → %s" % ratees[:3]))

    # ⚠️ UN BARÈME PORTE TOUS SES CRANS, PAS SEULEMENT LE PREMIER. La glace se
    #    vend 1 000 / 1 500 / 2 500 F : n'en baliser qu'un, c'est annoncer à
    #    Google un prix que la maison ne pratique que dans un cas sur trois.
    barem = [(n, pal) for n, p, p2, hm, pal in carte_ts if pal]
    perdus = [n for n, pal in barem
              if {int(o.get("price", 0)) for o in balisees.get(n, [])} != set(pal)]
    dire(not perdus, "les %d plats à barème portent leurs %s crans%s"
         % (len(barem), "/".join(str(len(p)) for _, p in barem) or "0",
            "" if not perdus else " → %s" % perdus[:3]))

    sans = sorted(n for n, p in zip(noms_ts, prix_ts) if p == 0)
    sans_bal = sorted(i["name"] for i in items if "offers" not in i)
    dire(sans == sans_bal,
         "les %d plats « prix sur demande » n'ont pas d'offre : %s" % (len(sans), sans_bal))

    # ⚠️ Un plat peut porter UN prix, DEUX tailles ou UNE fourchette : on
    #    compare les ENSEMBLES de montants, pas un prix contre un prix.
    attendu = {n: {v for v in [p, p2, hm] + pal if v > 0}
               for n, p, p2, hm, pal in carte_ts}
    faux = [i["name"] for i in offres
            if {v for o in liste_offres(i) for v in montants(o)}
               != attendu.get(i["name"], set())]
    dire(not faux, "chaque montant balisé est celui de la carte%s"
         % ("" if not faux else " → %s" % faux[:3]))

    dire(all(o["priceCurrency"] == "XOF" for i in offres for o in liste_offres(i)),
         "toutes les offres sont en XOF")
    # 5 · les plats retirés ne reviennent pas par le balisage
    for r in ("Napolitaine", "Mojito", "Crispy poulet", "JOQ Viagra", "Pêcheur"):
        dire(r not in json.dumps(d, ensure_ascii=False),
             "« %s » n'est pas dans le balisage non plus" % r)

    poids = len(m.group(1).encode("utf-8")) / 1024
    dire(poids < 40, "le balisage pèse %.1f Ko" % poids)

    print("\n%d verts, %d rouges" % (len(ok), len(ko)))
    return 1 if ko else 0


if __name__ == "__main__":
    raise SystemExit(main())
