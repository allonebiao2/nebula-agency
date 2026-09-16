# -*- coding: utf-8 -*-
"""
poids_claude_md.py — CLAUDE.md tient-il encore dans la limite de Claude Code ?

    python scripts/poids_claude_md.py            # le total et les 12 blocs les plus lourds
    python scripts/poids_claude_md.py --tous     # tous les blocs

`CLAUDE.md` est chargé EN ENTIER au début de chaque session. Au-delà de
150 000 caractères, Claude Code affiche « CLAUDE.md is over the 150.0k-char
limit » : chaque session démarre avec ~40 000 tokens de moins pour travailler.

⛔ 2026-09-16 : 151 181 caractères. Trois lignes du tableau des clients (Angy
   Art, Hillary, Au Braisé d'Or) en pesaient 73 819 à elles seules : chaque
   vague y avait ajouté son récit. Elles ont été recopiées intégralement dans
   leur CONTEXT.md, et le tableau n'en garde qu'un résumé (~2 000 caractères).

LA RÈGLE (CLAUDE.md, « RÈGLE AUTOMATIQUE — MÉMOIRE ET DISPATCH ») : au-delà
de 140 000, on transfère les blocs les plus lourds SANS DEMANDER.
  1. recopier le bloc intégralement dans le CONTEXT.md du client (ou du produit) ;
  2. vérifier que chaque morceau d'origine s'y retrouve ;
  3. seulement ensuite, le remplacer par un résumé qui renvoie au CONTEXT.md.

Sortie 0 sous le seuil d'alerte, 1 au-dessus.
"""
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LIMITE = 150_000
ALERTE = 140_000
LIGNE_CLIENT_MAX = 3_000


def nb(n):
    """17 623 et pas 17,623 : on formate le NOMBRE, jamais la phrase (qui a ses propres virgules)."""
    return f"{n:,}".replace(",", " ")


FICHIER = pathlib.Path(__file__).resolve().parent.parent / "CLAUDE.md"


def blocs(texte):
    """Chaque ligne du tableau des clients compte seule, chaque section compte sans elles."""
    sortie = []
    for section in re.split(r"\n(?=#{2,3} )", texte):
        titre = section.split("\n", 1)[0].strip()
        reste = []
        for ligne in section.split("\n"):
            m = re.match(r"\| (\d\d) \| ([^|]+) \|", ligne)
            if m:
                sortie.append((len(ligne), f"client {m.group(1)} · {m.group(2).strip()}"))
            else:
                reste.append(ligne)
        sortie.append((len("\n".join(reste)), titre[:70]))
    return sorted(sortie, reverse=True)


def main():
    texte = FICHIER.read_text(encoding="utf-8").replace("\r\n", "\n")
    total = len(texte)
    etat = "⛔ AU-DESSUS DE LA LIMITE" if total > LIMITE else (
        "⚠️ au-dessus du seuil d'alerte" if total > ALERTE else "✅ sous le seuil d'alerte")
    print(f"CLAUDE.md : {nb(total)} caractères · limite {nb(LIMITE)} · alerte {nb(ALERTE)} · {etat}")
    print(f"marge avant l'alerte : {nb(ALERTE - total)}")
    print()

    liste = blocs(texte)
    for poids, nom in (liste if "--tous" in sys.argv else liste[:12]):
        drapeau = "  ⚠️ ligne client trop longue" if nom.startswith("client") and poids > LIGNE_CLIENT_MAX else ""
        print(f"{nb(poids):>8}  {nom}{drapeau}")

    return 1 if total > ALERTE else 0


if __name__ == "__main__":
    sys.exit(main())
