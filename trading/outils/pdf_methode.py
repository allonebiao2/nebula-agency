# -*- coding: utf-8 -*-
"""
Le document de la méthode, en PDF.

    python -m trading.outils.pdf_methode

Chaîne : Markdown → HTML stylé → Chrome (Playwright) → PDF. La même que les documents de vente de
l'agence (`_documents/nebula-agency/vente/_build_pdf.py`), avec la charte du produit : fond clair
pour l'impression, or NEBULA pour les titres, tableaux lisibles.

⚠️ **Aucune police téléchargée, aucune image distante** : un PDF doit s'ouvrir partout, y compris
hors ligne, y compris dans cinq ans.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SOURCES = {
    "METHODE-LE-REFLUX.md": "NEBULA · LE REFLUX — la méthode",
    "PLAN-DE-RISQUE.md": "NEBULA · LE REFLUX — le plan de risque",
    "BACKTEST-LONG.md": "NEBULA · LE REFLUX — les tests sur 36 ans",
}
SORTIE = RACINE / "documents"

STYLE = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: #15171c;
       font-size: 10.5pt; line-height: 1.55; margin: 0; }
h1 { font-size: 27pt; letter-spacing: -.5px; margin: 0 0 2mm; color: #0d0f14; }
h1 + p { color: #6b7280; font-size: 11pt; margin-top: 0; }
h2 { font-size: 14pt; margin: 9mm 0 2mm; padding-bottom: 1.5mm; color: #0d0f14;
     border-bottom: 2px solid #c9a227; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 5mm 0 1.5mm; color: #1f2430; page-break-after: avoid; }
p, li { margin: 0 0 2.2mm; }
strong { color: #0d0f14; }
blockquote { margin: 3mm 0; padding: 3mm 5mm; border-left: 3px solid #c9a227;
             background: #faf7ee; font-size: 11pt; }
blockquote p { margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 4mm; font-size: 9.5pt;
        page-break-inside: avoid; }
th { background: #14161c; color: #f3efe6; text-align: left; padding: 2mm 2.5mm; font-weight: 600; }
td { border-bottom: 1px solid #e3e5ea; padding: 1.8mm 2.5mm; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
hr { border: 0; border-top: 1px solid #e3e5ea; margin: 6mm 0; }
code { background: #f2f3f5; padding: .5mm 1.2mm; border-radius: 2px; font-size: 9pt; }
pre { background: #14161c; color: #e9e6df; padding: 3mm 4mm; border-radius: 3px; font-size: 8.5pt;
      overflow-x: hidden; white-space: pre-wrap; }
pre code { background: none; color: inherit; }
em { color: #6b7280; }
.bandeau { background: #14161c; color: #f3efe6; padding: 6mm 7mm; margin: 0 0 7mm;
           border-radius: 3px; }
.bandeau h1 { color: #f3efe6; }
.bandeau p { color: #c9a227; margin: 1mm 0 0; font-size: 10.5pt; }
"""


def en_html(markdown_texte: str, titre: str) -> str:
    import markdown as md
    corps = md.markdown(markdown_texte, extensions=["tables", "sane_lists"])
    # Le premier titre et sa ligne de sous-titre deviennent le bandeau de couverture.
    m = re.search(r"<h1>(.*?)</h1>\s*(?:<h2>(.*?)</h2>)?", corps, re.S)
    bandeau = ""
    if m:
        bandeau = (f'<div class="bandeau"><h1>{m.group(1)}</h1>'
                   f'<p>{m.group(2) or ""}</p></div>')
        corps = corps[m.end():]
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f"<title>{titre}</title><style>{STYLE}</style></head><body>{bandeau}{corps}</body></html>")


def construire(nom: str, titre: str) -> Path:
    from playwright.sync_api import sync_playwright
    source = RACINE / nom
    html = en_html(source.read_text(encoding="utf-8"), titre)
    SORTIE.mkdir(parents=True, exist_ok=True)
    provisoire = SORTIE / (source.stem + ".html")
    provisoire.write_text(html, encoding="utf-8")
    cible = SORTIE / (source.stem + ".pdf")
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page()
        page.goto(provisoire.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(cible), format="A4", print_background=True,
                 display_header_footer=True,
                 header_template='<div style="font-size:7pt;color:#9aa0a6;width:100%;'
                                 'padding:0 14mm;text-align:right;">NEBULA · LE REFLUX</div>',
                 footer_template='<div style="font-size:7pt;color:#9aa0a6;width:100%;'
                                 'padding:0 14mm;display:flex;justify-content:space-between;">'
                                 '<span>NEBULA Agency · document interne</span>'
                                 '<span class="pageNumber"></span>/<span class="totalPages"></span></div>',
                 margin={"top": "18mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
        nav.close()
    provisoire.unlink(missing_ok=True)
    return cible


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for nom, titre in SORTIES_A_FAIRE:
        if not (RACINE / nom).exists():
            print(f"  {nom} : absent, ignoré")
            continue
        cible = construire(nom, titre)
        print(f"  {cible}  ({cible.stat().st_size / 1000:.0f} Ko)")
    return 0


SORTIES_A_FAIRE = list(SOURCES.items())

if __name__ == "__main__":
    sys.exit(main())
