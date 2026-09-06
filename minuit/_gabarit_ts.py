# -*- coding: utf-8 -*-
"""MINUIT · recopier le gabarit de la lettre dans un module TypeScript.

⚠️ FICHIER GENERE, jamais edite a la main :

    python minuit/_gabarit_ts.py

POURQUOI IL EXISTE
    Une fonction de bord ne lit pas un fichier a cote d'elle : ce qui n'est pas
    dans le paquet deploye n'existe pas chez Deno. Le gabarit doit donc voyager
    avec le code. Le recopier a la main ferait deux lettres differentes le jour
    ou l'une des deux change ; ici, `_qc_caisse.mjs` compare les deux et refuse
    la moindre difference.

⚠️ On ecrit une chaine JSON, pas un litteral a l'echappement bricole : le
    gabarit contient des apostrophes, des accents graves, des dollars et des
    barres obliques inverses, et chacun casserait un litteral choisi a la main.
"""
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
LETTRE = ICI / "lettre.html"
CIBLE = ICI / "supabase" / "functions" / "_shared" / "gabarit.ts"

ENTETE = """/*
  MINUIT · le gabarit de la lettre, tel quel.

  ⛔ FICHIER GENERE. Ne pas l'editer : `python minuit/_gabarit_ts.py` le
  reecrit depuis `minuit/lettre.html`, qui est la source. Un controle compare
  les deux et refuse la moindre difference.
*/

export const GABARIT = """


def main():
    html = LETTRE.read_text(encoding="utf-8")
    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    CIBLE.write_text(ENTETE + json.dumps(html, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  %s : %d octets de gabarit" % (CIBLE.name, len(html)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
