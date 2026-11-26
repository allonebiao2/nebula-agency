# -*- coding: utf-8 -*-
"""_ina_retirer_2611.py · les produits qu'INA Luxury ne vend plus (liste de Mme Sabrina, 26/11).

Ce que le script retire ou recalcule, en LISANT la page :
  · les 22 produits (PRODUCTS), leurs photos (IMG) et leurs détourages (manifeste + fichiers) ;
  · les routines préétablies : un produit retiré sort de sa routine, un palier vide disparaît, une routine vide aussi ;
  · les sous-catégories devenues vides (SUBCATS) ;
  · les descriptions de famille qui nommaient une rubrique disparue ;
  · le bloc INA du menu du hub et de la clinique, RÉGÉNÉRÉ depuis les données (il était recopié, et en retard).
Refuse d'écrire si un nom de la liste ne correspond à aucun produit. Idempotent.
"""
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cozy_vers_ina import objets  # le même découpeur d'objets (il saute chaînes et commentaires)

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

RETIRER = [
    # visage
    "Nettoyant Oxygène", "Nettoyant aux Plantes", "Eau Micellaire Apaisante", "Huile Démaquillante", "Sérum Oxygène",
    "Sérum Glass Skin", "Serum Azelaic", "Rose Purifiant Sérum", "Crème Oxygène", "Reti Rose Crème",
    "Glass Skin Boost Crème", "Glass Skin Crème", "Oxygène Masque", "Glass Skin Gel",
    # corps
    "Busserole Beauty Bar", "Clarté Black Soap",
    # capillaires
    "Shampoing Sensicare", "Après-Shampoing Sensicare", "Masque Fortifiant K10", "Huile Soin 2-en-1",
    # enfant
    "Gel Lavant Aloe",
    # soin lèvres
    "Lactic Lip Scrub",
]
# les descriptions de famille qui citaient une rubrique désormais vide
DESCRIPTIONS = [
    ("desc:'Nettoyants, sérums, crèmes et masques pour le visage.'", "desc:'Nettoyants, démaquillants, sérums et crèmes pour le visage.'"),
    ("desc:'Shampoings, après-shampoings, masques, sérums, huiles et beurres cheveux.'", "desc:'Sérums pour le cuir chevelu et les cheveux.'"),
    ("desc:'Rituel lèvres couture — exfoliant, baume réparateur et gloss biomimétique.'", "desc:'Rituel lèvres couture — baume réparateur, gloss biomimétique et coffret.'"),
]


def nom_de(o):
    m = re.search(r"""\bn:(['"])((?:(?!\1)[^\\]|\\.)*)\1""", o)
    return m.group(2).replace("\\'", "'") if m else None


def litteral(s, debut):
    """Le texte d'un littéral JS `const X=…;` (objet ou tableau), en respectant chaînes et commentaires."""
    i = s.index(debut) + len(debut)
    ouvrant = s[i]
    fermant = {"{": "}", "[": "]"}[ouvrant]
    prof, k, q = 0, i, None
    while k < len(s):
        c = s[k]
        if q:
            if c == "\\":
                k += 2
                continue
            if c == q:
                q = None
        elif c == "/" and s[k + 1:k + 2] == "/":
            k = s.index("\n", k)
            continue
        elif c in "'\"`":
            q = c
        elif c == ouvrant:
            prof += 1
        elif c == fermant:
            prof -= 1
            if prof == 0:
                return i, k + 1
        k += 1
    raise SystemExit("littéral non fermé : " + debut)


def node_eval(js_litteral, transformation):
    """Évalue un littéral JS pur (aucun appel) dans Node, applique `transformation` (JS), rend du JSON."""
    code = "const X=(%s);\nconst R=(%s)(X);\nprocess.stdout.write(JSON.stringify(R));" % (js_litteral, transformation)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(code)
    r = subprocess.run(["node", f.name], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit("node : " + r.stderr[:400])
    return json.loads(r.stdout)


def main():
    p = ICI / "ina-luxury.html"
    s = p.read_text(encoding="utf-8")

    # 1. les produits
    i, j = litteral(s, "const PRODUCTS=")
    bloc = s[i:j]
    objs = objets(bloc[1:-1])
    noms = [nom_de(o) for o in objs]
    absents = [n for n in RETIRER if n not in noms]
    deja = [n for n in RETIRER if n in absents]
    if absents and len(absents) != len(RETIRER):
        # une partie seulement est introuvable : une faute de nom, on n'écrit rien
        a_faire = [n for n in absents]
        print("⚠ introuvables (déjà retirés ou mal nommés) :", a_faire)
    retires = 0
    for o in objs:
        if nom_de(o) in RETIRER:
            k = bloc.index(o)
            fin = k + len(o)
            while fin < len(bloc) and bloc[fin] in ", \t":
                fin += 1
            if fin < len(bloc) and bloc[fin] == "\n":
                fin += 1
            debut = bloc.rfind("\n", 0, k) + 1
            if bloc[debut:k].strip() == "":
                k = debut
            bloc = bloc[:k] + bloc[fin:]
            retires += 1
    s = s[:i] + bloc + s[j:]
    restants = [nom_de(o) for o in objets(bloc[1:-1])]
    print(f"produits : {len(noms)} → {len(restants)} ({retires} retirés)")
    if any(n in restants for n in RETIRER):
        raise SystemExit("un produit à retirer est encore là")

    # 2. les photos
    i, j = litteral(s, "const IMG=")
    img = json.loads(s[i:j])
    img2 = {k: v for k, v in img.items() if k not in RETIRER}
    s = s[:i] + "{\n" + ",\n".join(f'  "{k}":"{v}"' for k, v in img2.items()) + "\n}" + s[j:]
    print(f"photos : {len(img)} → {len(img2)}")

    # 3. les routines
    retirer_js = json.dumps(RETIRER, ensure_ascii=False)
    i, j = litteral(s, "const ROUTINES=")
    avant = s[i:j]
    rout = node_eval(avant, """X => { const R = %s, out = {};
      for (const [fam, liste] of Object.entries(X)) {
        out[fam] = liste.map(r => ({...r, tiers: r.tiers.map(t => ({...t, items: t.items.filter(n => !R.includes(n))}))
                                                   .filter(t => t.items.length)}))
                        .filter(r => r.tiers.length);
      } return out; }""" % retirer_js)
    s = s[:i] + json.dumps(rout, ensure_ascii=False, indent=1) + s[j:]
    for fam, liste in rout.items():
        print(f"routines {fam} : " + ", ".join(f"{r['label']} ({sum(len(t['items']) for t in r['tiers'])})" for r in liste))

    # 4. les sous-catégories vides
    pleines = {}
    for o in objets(s[litteral(s, "const PRODUCTS=")[0] + 1:litteral(s, "const PRODUCTS=")[1] - 1]):
        f = re.search(r"\bf:'([^']+)'", o).group(1)
        sc = re.search(r"\bs:'([^']+)'", o).group(1)
        pleines.setdefault(f, set()).add(sc)
    i, j = litteral(s, "const SUBCATS=")
    sub = node_eval(s[i:j], "X => X")
    vides = [f"{f}/{x['key']}" for f, l in sub.items() for x in l if x["key"] not in pleines.get(f, set())]
    sub2 = {f: [x for x in l if x["key"] in pleines.get(f, set())] for f, l in sub.items()}
    s = s[:i] + json.dumps(sub2, ensure_ascii=False, indent=1) + s[j:]
    print("sous-catégories vidées :", vides or "aucune")

    # 5. les descriptions de famille
    for a, b in DESCRIPTIONS:
        if a in s:
            s = s.replace(a, b, 1)
    p.write_text(s, encoding="utf-8")

    # 6. le bloc INA du menu du hub et de la clinique, régénéré depuis les données
    i, j = litteral(s, "const FAMILIES=")
    fams = node_eval(s[i:j], "X => X.map(f => ({key: f.key, label: f.label}))")
    lignes = []
    for f in fams:
        subs = [x["label"] for x in sub2.get(f["key"], [])]
        if f["key"] in pleines and subs:
            lignes.append("    {n:%s,subs:%s}" % (json.dumps(f["label"], ensure_ascii=False), json.dumps(subs, ensure_ascii=False)))
    nouveau = "  {b:'INA LUXURY',href:'ina-luxury.html',cats:[\n" + ",\n".join(lignes) + "\n  ]},"
    for nom in ("index.html", "luxury-skin-clinic.html"):
        q = ICI / nom
        t = q.read_text(encoding="utf-8")
        a = t.index("  {b:'INA LUXURY',href:'ina-luxury.html',cats:[")
        b = t.index("  ]},", a) + len("  ]},")
        t = t[:a] + nouveau + t[b:]
        q.write_text(t, encoding="utf-8")
        print(f"{nom} : menu INA régénéré ({len(lignes)} familles)")

    # 7. les détourages des produits retirés
    man_p = ICI / "assets" / "images" / "ina-luxury" / "_detoures" / "detoures.json"
    if man_p.exists():
        man = json.loads(man_p.read_text(encoding="utf-8"))
        for n in RETIRER:
            chemin = man.pop(n, None)
            if chemin and (ICI / chemin).exists():
                (ICI / chemin).unlink()
        man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"détourages : {len(man)} restants")

    # 8. ce qui nomme encore un produit retiré, ailleurs dans le site
    for nom in ("index.html", "luxury-skin-clinic.html", "ina-luxury.html", "harmonisation-faciale.html"):
        t = (ICI / nom).read_text(encoding="utf-8")
        reste = [n for n in RETIRER if n in t]
        if reste:
            print(f"  ⚠ {nom} nomme encore : {reste}")


if __name__ == "__main__":
    main()
