# -*- coding: utf-8 -*-
"""MA LETTRE À… · construire les ouvertures (« rites ») : pour le constructeur ET pour le serveur.

    python malettre/_rites.py

Lit `rites/carte.json` (la seule liste des ouvertures), `rites/moteur.js`, `atelier.js`, `branchement.js` et
`rites/<id>.js`, réduit les matières de Blender (`rites/matieres/*.png`, 256 px) en WebP de 128 px, minifie le code
par esbuild (celui du studio vidéo, déjà sur le disque), puis écrit :

    malettre/rites.js                                  lu par le constructeur (aperçu de la lettre)
    malettre/supabase/functions/_shared/rites.ts       lu par le serveur (la lettre livrée)

Les deux portent les MÊMES chaînes (un contrôle de la caisse les compare) et la même fonction `poserRite(html, id,
cire)`, qui remplace `/*MALETTRE_RITE*/null/*FIN_MALETTRE_RITE*/` par l'ouverture de l'occasion. ⛔ Le rite vient
d'ici, jamais du navigateur : un identifiant inconnu donne « cachet ».

⚠️ Le code est posé DANS un <script> : il ne doit contenir ni « </script », ni « <!-- », ni U+2028/2029 (la
construction refuse). ⚠️ On remplace par une FONCTION, jamais par une chaîne : un `$$` minifié deviendrait `$`.
"""
import base64
import io
import json
import pathlib
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
PLAFOND_COMMUN = 32_000    # le moteur, l'atelier, le branchement (environ 9 Ko une fois compressé à l'envoi)
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


def main():
    carte = json.loads((RITES / "carte.json").read_text(encoding="utf-8"))
    ids = [k for k in carte if not k.startswith("_")]
    if "cachet" not in ids:
        sys.exit("⛔ « cachet » doit exister : c'est l'ouverture de toute occasion qui n'a pas la sienne")
    commun = minifier("\n".join((RITES / f).read_text(encoding="utf-8") for f in ("moteur.js", "atelier.js", "branchement.js")))
    if len(commun.encode("utf-8")) > PLAFOND_COMMUN:
        sys.exit("⛔ le moteur pèse %d octets (plafond %d)" % (len(commun.encode()), PLAFOND_COMMUN))
    rites, besoin = {}, set()
    for i in ids:
        src = (RITES / (i + ".js")).read_text(encoding="utf-8")
        code = minifier(src, comme_expression=True)
        if len(code.encode("utf-8")) > PLAFOND_RITE:
            sys.exit("⛔ %s pèse %d octets (plafond %d)" % (i, len(code.encode()), PLAFOND_RITE))
        mats = carte[i]["matieres"]
        rites[i] = {"code": code, "matieres": mats, "nom": carte[i]["nom"], "occasions": carte[i].get("occasions", [])}
        besoin.update(m for m in mats if m != "cire")
        print("rite %-10s %6d octets · matières %s" % (i, len(code.encode()), ", ".join(mats)))
    cires = ["bordeaux", "or", "nuit", "sapin", "rose"]
    noms = sorted(besoin) + ["cire-" + c for c in cires]
    matcaps = {n: matcap(n) for n in noms}
    poids = sum(len(v) for v in matcaps.values())
    print("commun %6d octets · matières %d (%d octets en base64)" % (len(commun.encode()), len(matcaps), poids))
    occasion = {}
    for i in ids:
        for o in rites[i]["occasions"]:
            occasion[o] = i

    donnees = {"commun": commun, "rites": rites, "matcaps": matcaps, "occasion": occasion}
    corps = json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))

    # La fonction qui pose un rite, écrite UNE fois et recopiée telle quelle des deux côtés.
    poser = """function poserRite(html, id, cire) {
  var R = RITES_DONNEES.rites[id] ? id : "cachet", r = RITES_DONNEES.rites[R], m = {};
  var c = ["bordeaux", "or", "nuit", "sapin", "rose"].indexOf(cire) >= 0 ? cire : "bordeaux";
  r.matieres.forEach(function (n) { var k = n === "cire" ? "cire-" + c : n; m[k] = RITES_DONNEES.matcaps[k]; });
  var code = "(function(){var MATIERES=" + JSON.stringify(m) + ";" + RITES_DONNEES.commun + ";return Branchement(" + r.code + ")})()";
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
        "export const RITES_DONNEES: { commun: string; rites: Record<string, { code: string; matieres: string[]; nom: { fr: string; en: string }; occasions: string[] }>; "
        "matcaps: Record<string, string>; occasion: Record<string, string> } = " + corps + ";\n"
        "export " + poser.replace("function poserRite(html, id, cire)", "function poserRite(html: string, id: string, cire: string): string")
        .replace("var R = ", "var R: string = ").replace("m = {};", "m: Record<string, string> = {};")
        .replace("function (n) {", "function (n: string) {") + "\n", encoding="utf-8")
    print("✓ %s (%d Ko) · %s" % (SORTIE_JS.relative_to(ICI.parent), SORTIE_JS.stat().st_size // 1024, SORTIE_TS.relative_to(ICI.parent)))


if __name__ == "__main__":
    main()
