#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de devis NEBULA — source -> page autonome.

    cd _documents/nebula-agency/vente && python3 _build_devis.py

On édite `_generateur_devis_src.html`, JAMAIS `generateur-devis.html`.
Ce script y injecte les trois polices maison en base64 et rend :

    generateur-devis.html        page autonome, à ouvrir depuis n'importe où
    _artefact_devis.html         même contenu sans l'enveloppe <html>/<head>,
                                 pour la publication en artefact claude.ai

⚠️ Les polices sont embarquées : la page doit marcher hors réseau, dans la
   boutique, sur un téléphone en 3G. Aucune ressource externe, jamais.
"""

import base64
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent
SRC = ICI / "_generateur_devis_src.html"
OUT = ICI / "generateur-devis.html"
ARTEFACT = ICI / "_artefact_devis.html"
FONTS = ICI / "assets" / "fonts"

# nom de famille CSS -> (fichier, plage de graisses)
POLICES = [
    ("Syne", "syne.woff2", "600 800"),
    ("Inter", "inter.woff2", "400 700"),
    ("JetBrains Mono", "jetbrains-mono.woff2", "500"),
]


def face(famille, fichier, graisses):
    chemin = FONTS / fichier
    if not chemin.exists():
        sys.exit(f"⛔ police absente : {chemin}")
    b64 = base64.b64encode(chemin.read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
        "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}"
        % (famille, graisses, b64)
    )


def construire():
    src = SRC.read_text(encoding="utf-8")
    if "/*@FONTS@*/" not in src:
        sys.exit("⛔ marqueur /*@FONTS@*/ absent de la source")

    corps = src.replace("/*@FONTS@*/", "\n".join(face(*p) for p in POLICES))

    # 1 · l'artefact : le corps tel quel, l'enveloppe est ajoutée à la publication
    ARTEFACT.write_text(corps, encoding="utf-8")

    # 2 · la page autonome : <title> et <style> remontent dans un vrai <head>,
    #     le balisage et le script restent dans <body>.
    m_titre = re.search(r"<title>.*?</title>", corps, re.S)
    m_style = re.search(r"<style>.*?</style>", corps, re.S)
    if not m_titre or not m_style:
        sys.exit("⛔ <title> ou <style> introuvable dans la source")

    titre, style = m_titre.group(0), m_style.group(0)
    reste = corps.replace(titre, "", 1).replace(style, "", 1).strip()

    page = "\n".join([
        "<!DOCTYPE html>",
        '<html lang="fr">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
        '<meta name="robots" content="noindex,nofollow">',
        titre,
        '<meta name="description" content="Transforme la demande d\'un client, '
        'écrite ou dictée, en devis chiffré sur la grille officielle NEBULA.">',
        '<meta name="theme-color" content="#070A14">',
        style,
        "</head>",
        "<body>",
        reste,
        "</body>",
        "</html>",
        "",
    ])

    OUT.write_text(page, encoding="utf-8")

    for f in (OUT, ARTEFACT):
        print(f"✓ {f.name} — {f.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    construire()
