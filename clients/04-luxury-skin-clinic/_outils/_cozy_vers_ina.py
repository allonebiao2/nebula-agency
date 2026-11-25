"""Cozy entre dans INA Luxury (demande de la cliente, 26/11).

Les 7 produits de Cozy rejoignent INA dans une sixième famille, « Intime & bien-être », avec les trois catégories
de Cozy sous leurs libellés exacts (Hygiène intime, Selfcare, Produits raffermissants). Rien n'est recopié à la
main : les objets sont LUS dans cozy.html puis traduits dans la langue d'INA.

  cat:'intime'            ->  f:'intime-bien-etre', s:'intime'
  c:['Peau sèche', ...]   ->  c:['peau-seche', ...]   (clés de CONCERNS, ajoutées si elles manquent)
  important:"..."         ->  warn:"Important : ..."  (INA l'affiche déjà avec la même icône)
  variant:'Fraise Sucrée' ->  gardé ; INA apprend à l'afficher sous le nom
  tint:'...'              ->  retiré (INA prend la teinte de la famille quand une photo manque ; les 7 en ont une)

Idempotent : si la famille est déjà là, le script vérifie et ne réécrit rien.
Usage : python _outils/_cozy_vers_ina.py          (écrit)
        python _outils/_cozy_vers_ina.py --voir   (montre sans écrire)
"""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
COZY = ICI / "cozy.html"
INA = ICI / "ina-luxury.html"
FAM = "intime-bien-etre"
BS = chr(92)

# libellé de Cozy -> clé de CONCERNS d'INA (les deux premières existent déjà chez INA, mot pour mot)
CLES = {
    "Peau sèche": "peau-seche", "Manque d'éclat": "eclat-corps",
    "Fermeté buste": "fermete-buste", "Galbe des courbes": "galbe-courbes", "Fermeté": "fermete",
    "Tonicité": "tonicite", "Self-care": "self-care", "Mains sèches": "mains-seches",
    "Mains rugueuses": "mains-rugueuses", "Parfum sensuel": "parfum-sensuel", "Peau terne": "peau-terne",
}
SOUS = {"intime": "Hygiène intime", "selfcare": "Selfcare", "raffermissant": "Produits raffermissants"}
EMO = {"intime": "🌸", "selfcare": "🕯️", "raffermissant": "💎"}


def objets(blk):
    """Découpe les objets de premier niveau d'un tableau JS, en sautant les chaînes."""
    depth, start, out, k, q = 0, None, [], 0, None
    while k < len(blk):
        ch = blk[k]
        if q:
            if ch == BS:
                k += 2
                continue
            if ch == q:
                q = None
        elif ch == "/" and blk[k + 1:k + 2] == "/":
            # un commentaire de ligne peut porter une apostrophe : on le saute en entier
            fin = blk.find("\n", k)
            k = len(blk) if fin < 0 else fin
            continue
        elif ch in "'\"`":
            q = ch
        elif ch == "{":
            if depth == 0:
                start = k
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(blk[start:k + 1])
        k += 1
    return out


def tableau(s, nom):
    i = s.index(f"const {nom}=[")
    j = s.index("\n];", i)
    return i, j


def noms(objs):
    # un nom s'écrit entre '…' ou entre "…" (quand il porte une apostrophe : « Crème Douceur d'Aloe »)
    return [re.search(r"""\bn:(['"])((?:(?!\1)[^\\]|\\.)*)\1""", o).group(2).replace(BS + "'", "'") for o in objs]


def traduire(o):
    cat = re.search(r"\bcat:'([^']+)'", o).group(1)
    if cat not in SOUS:
        raise SystemExit(f"catégorie Cozy inconnue : {cat}")
    o = o.replace(f"cat:'{cat}'", f"f:'{FAM}',s:'{cat}'", 1)
    o = re.sub(r",?\s*tint:'[^']*'", "", o, count=1)

    def cles(m):
        libs = re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))
        libs = [l.replace(BS + "'", "'") for l in libs]
        manque = [l for l in libs if l not in CLES]
        if manque:
            raise SystemExit(f"besoin sans clé : {manque}")
        return "c:[" + ",".join(f"'{CLES[l]}'" for l in libs) + "]"

    o = re.sub(r"\bc:\[([^\]]*)\]", cles, o, count=1)
    o = re.sub(r'\bimportant:"', 'warn:"Important : ', o, count=1)
    if not o.startswith("{f:"):
        # INA écrit f et s en tête de chaque objet ; on garde la même forme
        o = "{" + o[1:].lstrip()
    return cat, o


def main():
    voir = "--voir" in sys.argv
    cz = COZY.read_text(encoding="utf-8")
    ina = INA.read_text(encoding="utf-8")
    ci, cj = tableau(cz, "PRODUCTS")
    cozy_objs = objets(cz[ci + len("const PRODUCTS=["):cj])
    cozy_noms = noms(cozy_objs)
    ii, ij = tableau(ina, "PRODUCTS")
    ina_avant = noms(objets(ina[ii + len("const PRODUCTS=["):ij]))
    print(f"Cozy : {len(cozy_noms)} produits · INA : {len(ina_avant)} produits")

    if f"key:'{FAM}'" in ina:
        absents = [n for n in cozy_noms if ina_avant.count(n) != 1]
        print("déjà fait :", "les 7 sont là, une fois chacun" if not absents else f"PROBLÈME, absents ou en double : {absents}")
        sys.exit(1 if absents else 0)

    doublons = [n for n in cozy_noms if n in ina_avant]
    if doublons:
        raise SystemExit(f"déjà dans INA, je ne double pas : {doublons}")

    # 1. les produits, à la fin du tableau d'INA
    trad = [traduire(o) for o in cozy_objs]
    bloc = "\n  // ===== INTIME & BIEN-ÊTRE (l'ancien univers Cozy, rejoint INA le 26/11) =====\n"
    bloc += "".join(f"  {o},\n" for _, o in trad)
    avant_fin = ina[:ij].rstrip()
    if not avant_fin.endswith(","):
        avant_fin += ","
    ina = avant_fin + bloc.rstrip(",\n") + "\n" + ina[ij:]

    # 2. la famille et ses trois catégories
    fam = ("  {key:'intime-bien-etre',img:'cozy-intime',label:'Intime & bien-être',"
           "desc:'Hygiène intime, selfcare et produits raffermissants.',\n"
           "   tint:'linear-gradient(155deg,#2a1c20,#3a2830 55%,#1a1014)'},\n")
    a = ina.index("const FAMILIES=[")
    b = ina.index("\n];", a)
    ina = ina[:b] + "\n" + fam.rstrip("\n") + ina[b:]
    sub = "  'intime-bien-etre':[\n" + "".join(f"    {{key:'{k}',label:'{v}'}},\n" for k, v in SOUS.items()) + "  ],\n"
    a = ina.index("const SUBCATS={")
    b = ina.index("\n};", a)
    ina = ina[:b] + "\n" + sub.rstrip("\n") + ina[b:]

    # 3. les besoins qui manquent à CONCERNS
    a = ina.index("const CONCERNS={")
    b = ina.index("\n};", a)
    existants = set(re.findall(r"'?([a-z-]+)'?:", ina[a:b]))
    neufs = {k: l for l, k in CLES.items() if k not in existants}
    if neufs:
        ligne = "  " + ",".join(f"'{k}':\"{l}\"" for k, l in neufs.items()) + ","
        ina = ina[:b] + "\n" + ligne + ina[b:]

    # 4. les photos (mêmes fichiers que Cozy) et les emojis des catégories
    imgs = re.search(r"const IMG=(\{.*?\});", cz).group(1)
    paires = re.findall(r'"([^"]+)":\s*"([^"]+)"', imgs)
    a = ina.index("const IMG={")
    b = ina.index("\n};", a)
    lignes = "".join(f',\n  "{n}":"{p}"' for n, p in paires if n in cozy_noms)
    ina = ina[:b] + lignes + ina[b:]
    a = ina.index("const EMO_BY_SUB={")
    b = ina.index("\n};", a)
    ina = ina[:b] + "\n  " + "".join(f"'{k}':'{v}'," for k, v in EMO.items()) + ina[b:]

    # 5. la variante (« Fraise Sucrée ») s'affiche sous le nom, comme chez Cozy
    ancre = "      <h3>${p.n}</h3>\n"
    if ancre not in ina:
        raise SystemExit("gabarit de carte INA introuvable")
    ina = ina.replace(ancre, ancre + "      ${p.variant?`<div class=\"card-variant\">${p.variant}</div>`:''}\n", 1)
    css = ".card-variants{display:flex;"
    ina = ina.replace(css, ".card-variant{font-size:.78rem;font-style:italic;color:#c9a84c;margin:2px 0 6px;}\n" + css, 1)

    # contrôle : chaque produit de Cozy est dans INA, une fois
    ii, ij = tableau(ina, "PRODUCTS")
    apres = noms(objets(ina[ii + len("const PRODUCTS=["):ij]))
    absents = [n for n in cozy_noms if apres.count(n) != 1]
    perdus = [n for n in ina_avant if n not in apres]
    print(f"INA après : {len(apres)} produits (attendu {len(ina_avant) + len(cozy_noms)})")
    if absents or perdus or len(apres) != len(ina_avant) + len(cozy_noms):
        raise SystemExit(f"ARRÊT, rien n'est écrit · absents {absents} · perdus {perdus}")
    for cat, o in trad:
        print(f"  {SOUS[cat]:24} {re.search(r'\bn:.([^\x27]+)', o).group(1)}")
    if voir:
        print("(--voir : rien n'est écrit)")
        return
    INA.write_text(ina, encoding="utf-8")
    print("ina-luxury.html écrit.")


if __name__ == "__main__":
    main()
