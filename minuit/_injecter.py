# -*- coding: utf-8 -*-
"""MINUIT · poser les donnees d'une lettre dans le gabarit.

⛔ LA REGLE QUI JUSTIFIE CE FICHIER

Les donnees d'une lettre sont ecrites par un acheteur, et elles atterrissent
DANS un bloc <script>. Un acheteur qui ecrit « </script> » dans son mot ferme
le bloc, et la page entiere meurt : plus de titre, plus de lettre, plus de
seuil. Ce n'est pas theorique, c'est ce qu'a trouve le controle du 2026-09-02.

json.dumps ne protege PAS de ca : « </script> » est une chaine JSON
parfaitement valide. Le navigateur, lui, cherche la balise fermante AVANT de
lire le JSON.

Cette fonction est donc le SEUL endroit ou l'on ecrit des donnees dans le
gabarit. Le constructeur, le serveur et les outils l'utilisent tous. Ne jamais
refaire un json.dumps a la main ailleurs.
"""
import json
import pathlib

ICI = pathlib.Path(__file__).resolve().parent
GABARIT = ICI / "lettre.html"

DEBUT = "/*MINUIT_DONNEES*/"
FIN = "/*FIN_MINUIT_DONNEES*/"


def serialiser(donnees):
    """JSON sur pour un bloc <script> HTML.

    Les trois sequences a neutraliser, et pourquoi :
      </   ferme la balise script, meme dans une chaine ;
      <!-- ouvre un commentaire HTML hérité, qui avale la suite ;
      U+2028 / U+2029 sont des fins de ligne pour JavaScript, pas pour JSON.
    """
    s = json.dumps(donnees, ensure_ascii=False)
    s = s.replace("</", "<\\/")
    s = s.replace("<!--", "<\\!--")
    s = s.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return s


def poser(donnees, gabarit=None):
    """Rend le HTML complet d'UNE lettre, prete a etre servie ou stockee."""
    t = (gabarit or GABARIT).read_text(encoding="utf-8")
    a = t.index(DEBUT)
    b = t.index(FIN) + len(FIN)
    return t[:a] + serialiser(donnees) + t[b:]


if __name__ == "__main__":
    # Une preuve, pas une promesse.
    piege = {"lettre": ["fin </script><script>window.__pwn=1</script>"],
             "titre": "<!-- caché -->", "pour": "Zara", "de": "R",
             "occasion": "", "code": "", "photos": [], "depuis": "", "pied": True}
    s = serialiser(piege)
    assert "</script>" not in s, "la balise fermante passe encore"
    assert "<!--" not in s, "le commentaire HTML passe encore"
    assert json.loads(s.replace("<\\/", "</").replace("<\\!--", "<!--"))["pour"] == "Zara"
    print("  serialiser() : la balise fermante et le commentaire sont neutralises")
