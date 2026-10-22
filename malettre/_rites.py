# -*- coding: utf-8 -*-
"""MA LETTRE À… · construire les ouvertures (« rites ») : pour le constructeur ET pour le serveur.

    python malettre/_rites.py

Lit `rites/carte.json` (les ouvertures, et celles de chaque occasion), `rites/moteur.js`, `atelier.js`, `ecriture.js`,
`branchement.js` et chaque mécanique `rites/<mecanique>.js` (minifiée une fois pour tous ses thèmes), les emblèmes des
occasions (`creer.html`, leur seule source), réduit les matières de Blender (`rites/matieres/*.png`, 256 px) en WebP de 128 px, minifie le code
par esbuild (celui du studio vidéo, déjà sur le disque), puis écrit :

    malettre/rites.js                                  lu par le constructeur (aperçu de la lettre)
    malettre/supabase/functions/_shared/rites.ts       lu par le serveur (la lettre livrée)

Les deux portent les MÊMES chaînes (un contrôle de la caisse les compare) et la même fonction `poserRite(html, id,
cire, occasion)`, qui remplace `/*MALETTRE_RITE*/null/*FIN_MALETTRE_RITE*/` par l'ouverture de l'occasion. ⛔ Le rite vient
d'ici, jamais du navigateur : un identifiant inconnu donne « cachet ».

⚠️ Le code est posé DANS un <script> : il ne doit contenir ni « </script », ni « <!-- », ni U+2028/2029 (la
construction refuse). ⚠️ On remplace par une FONCTION, jamais par une chaîne : un `$$` minifié deviendrait `$`.
"""
import base64
import io
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ICI = pathlib.Path(__file__).resolve().parent
RITES = ICI / "rites"
ESBUILD = ICI.parent / "_studio-video" / "node_modules" / "esbuild"
SORTIE_JS = ICI / "rites.js"
SORTIE_TS = ICI / "supabase" / "functions" / "_shared" / "rites.ts"
PLAFOND_RITE = 24_000      # octets minifiés d'un rite seul
PLAFOND_COMMUN = 52_000    # le moteur « cinéma », l'atelier, l'écriture, le branchement (~43 Ko, ~14 Ko compressés à l'envoi)
INTERDITS = ["</script", "<!--", " ", " "]


def minifier(code, comme_expression=False):
    """esbuild, par Node : `transform` (pas de paquet, pas de renommage des noms globaux)."""
    script = (
        "const e=require(%s);let s='';process.stdin.on('data',d=>s+=d);"
        "process.stdin.on('end',()=>{const r=e.transformSync(s,{minify:true,target:'es2017',charset:'utf8',legalComments:'none'});"
        "process.stdout.write(r.code)});" % json.dumps(str(ESBUILD))
    )
    # ⚠️ Une expression seule est du code mort pour un minifieur : il l'efface. On l'affecte, puis on retire l'affectation.
    src = ("var __RITE__=" + code.strip().rstrip(";") + ";") if comme_expression else code
    r = subprocess.run(["node", "-e", script], input=src.encode("utf-8"), capture_output=True, check=True)
    out = r.stdout.decode("utf-8").strip().rstrip(";")
    if comme_expression:
        if not out.startswith("var __RITE__="):
            sys.exit("⛔ le rite minifié ne commence pas par son affectation : " + out[:60])
        out = out[len("var __RITE__="):]
    for x in INTERDITS:
        if x in out:
            sys.exit("⛔ le code minifié contient %r : il casserait la lettre" % x)
    return out


def matcap(nom):
    im = Image.open(RITES / "matieres" / (nom + ".png")).convert("RGBA").resize((128, 128), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "WEBP", quality=86, method=6)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode("ascii")


def emblemes():
    """Les emblèmes des occasions : `creer.html` est leur seule source (la vitrine les lit là aussi)."""
    src = (ICI / "creer.html").read_text(encoding="utf-8")
    bloc = re.search(r"var EMBLEMES = \{(.*?)\n\};", src, re.S)
    if not bloc:
        sys.exit("⛔ EMBLEMES introuvable dans creer.html")
    e = dict(re.findall(r'^\s*([a-z]+):"([^"]+)"', bloc.group(1), re.M))
    for k, v in e.items():
        if not re.fullmatch(r"[MmLlHhVvCcSsQqTtAaZz0-9 .,\-]+", v):
            sys.exit("⛔ l'emblème « %s » porte un caractère inattendu" % k)
    return e


def main():
    carte = json.loads((RITES / "carte.json").read_text(encoding="utf-8"))
    ouvertures, occasions = carte["ouvertures"], carte["occasions"]
    if "cachet" not in ouvertures:
        sys.exit("⛔ « cachet » doit exister : c'est l'ouverture de toute occasion qui n'a pas la sienne")
    for occ, liste in occasions.items():
        for i in liste:
            if i not in ouvertures:
                sys.exit("⛔ l'occasion « %s » propose « %s », qui n'existe pas" % (occ, i))
    commun = minifier("\n".join((RITES / f).read_text(encoding="utf-8") for f in ("moteur.js", "atelier.js", "ecriture.js", "branchement.js")))
    if len(commun.encode("utf-8")) > PLAFOND_COMMUN:
        sys.exit("⛔ le moteur pèse %d octets (plafond %d)" % (len(commun.encode()), PLAFOND_COMMUN))
    # une mécanique est minifiée UNE fois, quel que soit le nombre de ses thèmes
    mecaniques, besoin = {}, set()
    for i, o in ouvertures.items():
        m = o["mecanique"]
        if m not in mecaniques:
            code = minifier((RITES / (m + ".js")).read_text(encoding="utf-8"), comme_expression=True)
            if len(code.encode("utf-8")) > PLAFOND_RITE:
                sys.exit("⛔ %s pèse %d octets (plafond %d)" % (m, len(code.encode()), PLAFOND_RITE))
            mecaniques[m] = code
            print("mécanique %-9s %6d octets" % (m, len(code.encode())))
        besoin.update(x for x in o["matieres"] if x != "cire")
    texte_carte = json.dumps(carte, ensure_ascii=False)
    for y in INTERDITS:
        if y in texte_carte:
            sys.exit("⛔ la carte contient %r : elle casserait la lettre" % y)
    cires = ["bordeaux", "or", "nuit", "sapin", "rose"]
    noms = sorted(besoin) + ["cire-" + c for c in cires]
    matcaps = {n: matcap(n) for n in noms}
    poids = sum(len(v) for v in matcaps.values())
    print("commun %6d octets · matières %d (%d octets en base64) · %d ouvertures · %d occasions" % (
        len(commun.encode()), len(matcaps), poids, len(ouvertures), len(occasions)))

    donnees = {
        "commun": commun, "mecaniques": mecaniques, "matcaps": matcaps, "emblemes": emblemes(), "occasions": occasions,
        "ouvertures": {i: {"nom": o["nom"], "mecanique": o["mecanique"], "theme": o.get("theme", {}), "matieres": o["matieres"],
                           "grande": bool(o.get("grande"))} for i, o in ouvertures.items()},
    }
    corps = json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))

    # La fonction qui pose un rite, écrite UNE fois et recopiée telle quelle des deux côtés. ⛔ L'ouverture est déjà
    # choisie et vérifiée par l'appelant (le serveur la valide contre l'occasion) ; inconnue, c'est « cachet ».
    poser = """function poserRite(html, id, cire, occasion) {
  var D = RITES_DONNEES, R = D.ouvertures[id] ? id : "cachet", r = D.ouvertures[R], m = {}, theme = {}, k;
  var c = ["bordeaux", "or", "nuit", "sapin", "rose"].indexOf(cire) >= 0 ? cire : "bordeaux";
  r.matieres.forEach(function (n) { var x = n === "cire" ? "cire-" + c : n; m[x] = D.matcaps[x]; });
  for (k in r.theme) theme[k] = r.theme[k];
  theme.ouverture = R;
  if (D.emblemes[occasion]) theme.embleme = D.emblemes[occasion];
  var code = "(function(){var MATIERES=" + JSON.stringify(m) + ";var THEME=" + JSON.stringify(theme) + ";" + D.commun + ";return Branchement(" + D.mecaniques[r.mecanique] + ")})()";
  var a = "/*MALETTRE_RITE*/null/*FIN_MALETTRE_RITE*/", i = html.indexOf(a);
  if (i < 0) return html;
  return html.slice(0, i) + "/*MALETTRE_RITE*/" + code + "/*FIN_MALETTRE_RITE*/" + html.slice(i + a.length);
}"""
    SORTIE_JS.write_text(
        "/* MA LETTRE À… · les ouvertures, pour le constructeur. ⛔ FICHIER GÉNÉRÉ : python malettre/_rites.py */\n"
        "var RITES_DONNEES = " + corps + ";\n" + poser + "\n", encoding="utf-8")
    SORTIE_TS.write_text(
        "/* MA LETTRE À… · les ouvertures, pour le serveur. ⛔ FICHIER GÉNÉRÉ : python malettre/_rites.py */\n"
        "// deno-lint-ignore-file\n"
        "export const RITES_DONNEES: { commun: string; mecaniques: Record<string, string>; matcaps: Record<string, string>; "
        "emblemes: Record<string, string>; occasions: Record<string, string[]>; "
        "ouvertures: Record<string, { nom: { fr: string; en: string }; mecanique: string; theme: Record<string, unknown>; matieres: string[]; grande: boolean }> } = "
        + corps + ";\n"
        "export " + poser.replace("function poserRite(html, id, cire, occasion)", "function poserRite(html: string, id: string, cire: string, occasion: string): string")
        .replace("m = {}, theme = {}, k;", "m: Record<string, string> = {}, theme: Record<string, unknown> = {}, k: string;")
        .replace("function (n) {", "function (n: string) {") + "\n", encoding="utf-8")
    print("✓ %s (%d Ko) · %s" % (SORTIE_JS.relative_to(ICI.parent), SORTIE_JS.stat().st_size // 1024, SORTIE_TS.relative_to(ICI.parent)))


if __name__ == "__main__":
    main()
