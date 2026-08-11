# -*- coding: utf-8 -*-
"""Moissonne des photos RÉELLES du Bénin sur Wikimedia Commons.

Pourquoi Commons et pas une banque d'images : c'est la seule source où la
**licence et le lieu sont vérifiables fichier par fichier**. Ailleurs, la
moitié des images étiquetées « Bénin » sont ghanéennes ou togolaises, et une
licence « libre » annoncée sur un site n'est pas une licence vérifiée.

⛔ On ne garde QUE les licences réellement libres (CC0, CC BY, CC BY-SA,
   domaine public). Tout le reste est écarté, sans exception.
⚠️ Le script propose, il ne choisit pas : les candidats sont téléchargés dans
   `_sources/candidats/`, on monte une planche, et ON REGARDE. Un titre
   n'est pas une preuve.

    python _moisson.py            moissonne les candidats
    python _moisson.py --planche  monte les planches à regarder
"""
import io
import json
import os
import sys
import urllib.parse
import urllib.request

# la console Windows est en cp1252 : un seul caractere turc suffit a faire
# tomber tout le rapport au milieu du moissonnage. Lecon du 2026-08-05.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(ICI, "_sources", "candidats")
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "NEBULA-Agency/1.0 (allonebiao@gmail.com) python-urllib"}

# licences acceptées, en minuscules et sans espaces
LIBRES = ("cc0", "publicdomain", "ccby2.0", "ccby3.0", "ccby4.0",
          "ccbysa2.0", "ccbysa2.5", "ccbysa3.0", "ccbysa4.0",
          "ccbysa1.0", "ccby2.5", "ccby1.0", "publicdomainmark",
          "attribution", "ccbysa")

# station -> requêtes. Plusieurs formulations : le fonds est bilingue.
LIEUX = {
    "porte": ["Porte du Non-Retour Ouidah", "Door of No Return Ouidah",
              "Monument Ouidah plage"],
    "ouidah": ["Temple des pythons Ouidah", "Ouidah python temple",
               "Foret sacree Kpasse Ouidah", "Fort portugais Ouidah"],
    "cotonou": ["Dantokpa", "Marche Dantokpa Cotonou", "Cotonou market",
                "Place de l'Amazone Cotonou"],
    "ganvie": ["Ganvie", "Ganvie lake village", "Lac Nokoue village"],
    "abomey": ["Royal Palaces of Abomey", "Bas-relief Abomey",
               "Musee historique Abomey"],
    "koutammakou": ["Tata Somba", "Koutammakou", "Batammariba house",
                    "Tata Somba Benin"],
    "pendjari": ["Pendjari National Park", "Parc national de la Pendjari",
                 "Pendjari elephant"],
    "fleuve": ["Niger River Malanville", "Malanville Benin",
               "Fleuve Niger Benin"],
}


def api(params):
    params["format"] = "json"
    u = API + "?" + urllib.parse.urlencode(params)
    r = urllib.request.Request(u, headers=UA)
    return json.loads(urllib.request.urlopen(r, timeout=120).read().decode("utf-8"))


def chercher(q, n=14):
    d = api({"action": "query", "list": "search", "srsearch": q,
             "srnamespace": "6", "srlimit": str(n)})
    return [s["title"] for s in d.get("query", {}).get("search", [])]


def infos(titres):
    """Licence, dimensions, auteur et URL, par paquets de 40."""
    out = {}
    for i in range(0, len(titres), 40):
        lot = titres[i:i + 40]
        d = api({"action": "query", "titles": "|".join(lot),
                 "prop": "imageinfo",
                 "iiprop": "url|size|extmetadata|mime"})
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            em = ii.get("extmetadata", {})

            def v(k):
                return (em.get(k) or {}).get("value", "")

            out[p["title"]] = {
                "url": ii.get("url", ""),
                "w": ii.get("width", 0), "h": ii.get("height", 0),
                "mime": ii.get("mime", ""),
                "licence": v("LicenseShortName"),
                "cle": v("License").replace(" ", "").lower(),
                "auteur": v("Artist"), "credit": v("Credit"),
                "desc": v("ImageDescription")[:200],
            }
    return out


def libre(inf):
    c = (inf["cle"] or "").replace("-", "").replace(" ", "").lower()
    l = (inf["licence"] or "").replace("-", "").replace(" ", "").lower()
    return any(k in c or k in l for k in LIBRES)


def nettoyer(s):
    import re
    return re.sub(r"<[^>]+>", "", s or "").strip()


def moissonner():
    os.makedirs(CAND, exist_ok=True)
    fiche = {}
    for lieu, requetes in LIEUX.items():
        d = os.path.join(CAND, lieu)
        os.makedirs(d, exist_ok=True)
        titres = []
        for q in requetes:
            try:
                titres += chercher(q)
            except Exception as e:
                print("  recherche KO :", q, e)
        titres = list(dict.fromkeys(titres))
        inf = infos(titres) if titres else {}

        gardes = []
        for t, i in inf.items():
            if not i["url"] or "image" not in i["mime"]:
                continue
            if i["w"] < 900 or i["h"] < 900:      # trop petit pour du plein écran
                continue
            if not libre(i):
                continue
            gardes.append((t, i))

        # les portraits d'abord : le site est en plein écran vertical
        gardes.sort(key=lambda x: (x[1]["w"] / float(x[1]["h"] or 1),
                                   -x[1]["w"] * x[1]["h"]))
        gardes = gardes[:10]

        print("\n%-13s %d trouves, %d libres et assez grands"
              % (lieu, len(inf), len(gardes)))
        fiche[lieu] = []
        for n, (t, i) in enumerate(gardes):
            # l'URL porte des parametres apres le ? : on coupe AVANT
            # d'extraire l'extension, sinon le fichier s'appelle
            # "00.org&utm_campaign=imageinfo".
            propre = i["url"].split("?")[0]
            ext = os.path.splitext(propre)[1].lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            dest = os.path.join(d, "%02d%s" % (n, ext.lower()))
            if not os.path.exists(dest):
                try:
                    b = urllib.request.urlopen(
                        urllib.request.Request(i["url"], headers=UA),
                        timeout=180).read()
                    io.open(dest, "wb").write(b)
                except Exception as e:
                    print("   telechargement KO :", t[:50], e)
                    continue
            fiche[lieu].append({
                "fichier": os.path.basename(dest),
                "titre": t, "licence": i["licence"],
                "auteur": nettoyer(i["auteur"])[:110],
                "w": i["w"], "h": i["h"],
                "page": "https://commons.wikimedia.org/wiki/" +
                        urllib.parse.quote(t.replace(" ", "_")),
            })
            print("   %-9s %4dx%-4d %-16s %s"
                  % (os.path.basename(dest), i["w"], i["h"],
                     i["licence"][:16], t[5:60]))

    io.open(os.path.join(CAND, "fiche.json"), "w", encoding="utf-8").write(
        json.dumps(fiche, ensure_ascii=False, indent=1))
    print("\nfiche.json ecrite. Etape suivante : --planche, puis REGARDER.")


def planches():
    from PIL import Image, ImageDraw
    fiche = json.loads(io.open(os.path.join(CAND, "fiche.json"),
                               encoding="utf-8").read())
    for lieu, items in fiche.items():
        if not items:
            continue
        L, H, B = 260, 300, 20
        cols = min(5, len(items))
        lignes = (len(items) + cols - 1) // cols
        s = Image.new("RGB", (cols * L, lignes * (H + B)), (24, 24, 24))
        dr = ImageDraw.Draw(s)
        for n, it in enumerate(items):
            p = os.path.join(CAND, lieu, it["fichier"])
            if not os.path.exists(p):
                continue
            try:
                im = Image.open(p).convert("RGB")
            except Exception:
                continue
            r = min(L / im.width, H / im.height)
            im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))),
                           Image.LANCZOS)
            x = (n % cols) * L + (L - im.width) // 2
            y = (n // cols) * (H + B) + B
            s.paste(im, (x, y))
            dr.text(((n % cols) * L + 5, (n // cols) * (H + B) + 4),
                    "%s  %dx%d" % (it["fichier"], it["w"], it["h"]),
                    fill=(255, 200, 90))
        out = r"C:/Users/USER/.claude/jobs/bc7778e0/tmp/cand_%s.png" % lieu
        s.save(out)
        print(out, s.size, len(items), "candidats")


if __name__ == "__main__":
    if "--planche" in sys.argv:
        planches()
    else:
        moissonner()
