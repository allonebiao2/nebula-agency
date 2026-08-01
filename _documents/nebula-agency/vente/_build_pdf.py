#!/usr/bin/env python3
"""
Convertit les documents de vente Markdown en PDF à la charte cosmique NEBULA.

Chaîne : Markdown -> HTML stylé -> Chrome headless -> PDF.
Même principe que l'atelier utilisé pour le Playbook Boussole.

Usage :  python3 _documents/nebula-agency/vente/_build_pdf.py
Sortie :  _documents/nebula-agency/vente/pdf/*.pdf

Contraintes respectées : lisible sur téléphone (police généreuse, contrastes francs),
aucune dépendance externe dans le PDF, pas de fichier lourd.
"""
import os, re, subprocess, sys, tempfile
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "pdf")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Documents destinés aux partenaires (le socle 00 et l'avis 01 restent internes,
# mais on les génère aussi : ils servent à Mongazi).
# La date de couverture suit le fichier source : un PDF ne doit jamais
# annoncer une version plus ancienne que le texte qu'il contient.
VERSION = ""

# Documents PUBLICS : diffusables librement. La couverture ne doit surtout pas
# porter la mention « confidentiel » — un candidat qui la lit n'ose plus la partager.
PUBLICS = {"01b-ANNONCE-PUBLIQUE.md"}
CONF_PUBLIC = ("Annonce publique &middot; NEBULA Agency vous autorise à la partager "
               "librement, en entier, sans modification.")

DOCS = [
    ("00-SOCLE-COMMERCIAL.md",      "Socle commercial NEBULA"),
    ("01-AVIS-DE-RECRUTEMENT.md",   "Avis de recrutement"),
    ("01b-ANNONCE-PUBLIQUE.md",     "Annonce de recrutement"),
    ("02-MANUEL-DU-PARTENAIRE.md",  "Manuel du Partenaire"),
    ("03-GUIDE-CATALOGUE.md",       "Guide de vente · Catalogue Digital"),
    ("04-GUIDE-VITRINE.md",         "Guide de vente · Vitrine Digitale"),
    ("05-GUIDE-OUTIL-METIER.md",    "Guide de vente · Outil sur mesure"),
    ("06-ARSENAL-SCRIPTS.md",       "Arsenal du Partenaire · Scripts"),
    ("08-DIAGNOSTIC-DIGITAL.md",    "Le Diagnostic Digital"),
    ("09-CONTRAT-PARTENAIRE.md",    "Contrat de Partenaire"),
]

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm; }
*{box-sizing:border-box}
body{
  font-family:"DejaVu Sans","Liberation Sans",Arial,sans-serif;
  font-size:11.2pt; line-height:1.55; color:#12151F; margin:0;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.cover{
  height:250mm; display:flex; flex-direction:column; justify-content:center;
  background:linear-gradient(150deg,#0B0F1E 0%,#141033 55%,#0A1B2E 100%);
  color:#EAEEF9; padding:24mm 18mm; page-break-after:always; border-radius:2mm;
}
.cover .kicker{font-size:9.5pt;letter-spacing:.30em;text-transform:uppercase;
  color:#8E9CC4;margin-bottom:9mm}
.cover h1{font-size:30pt;line-height:1.12;margin:0 0 7mm;font-weight:800;letter-spacing:-.5pt;
  color:#EAEEF9 !important; border:0 !important; padding:0 !important}
.cover .rule{width:34mm;height:2.6pt;background:linear-gradient(90deg,#4A7DFF,#9B5CFF,#3FD8E6);
  border-radius:2pt;margin:0 0 7mm}
.cover .meta{font-size:10.5pt;color:#9AA6C4;line-height:1.85}
.cover .conf{margin-top:12mm;font-size:9pt;color:#7F8CB0;border-top:.6pt solid #2A3350;padding-top:5mm}

h1{font-size:19pt;font-weight:800;margin:11mm 0 4mm;color:#0F1224;
   border-bottom:2.2pt solid #9B5CFF;padding-bottom:2.5mm;page-break-after:avoid}
h2{font-size:14.5pt;font-weight:750;margin:8mm 0 3mm;color:#231A52;page-break-after:avoid}
h3{font-size:12.2pt;font-weight:700;margin:6mm 0 2.5mm;color:#2B2160;page-break-after:avoid}
h4{font-size:11.2pt;font-weight:700;margin:5mm 0 2mm;color:#333}
p{margin:0 0 3.2mm}
ul,ol{margin:0 0 3.6mm;padding-left:6.5mm}
li{margin-bottom:1.5mm}
strong{color:#14112E}
a{color:#3D3A8C;text-decoration:none}
hr{border:0;border-top:.6pt solid #D7DCEA;margin:7mm 0}

blockquote{
  margin:4mm 0; padding:3.4mm 5mm; border-left:2.8pt solid #F6A63C;
  background:#FFF8EC; border-radius:0 2mm 2mm 0; page-break-inside:avoid;
}
blockquote p{margin:0 0 1.6mm}
blockquote p:last-child{margin:0}

table{width:100%;border-collapse:collapse;margin:4mm 0;font-size:9.9pt;page-break-inside:avoid}
th{background:#1B1740;color:#fff;text-align:left;padding:2.4mm 3mm;font-weight:650;font-size:9.6pt}
td{padding:2.2mm 3mm;border-bottom:.5pt solid #E2E6F0;vertical-align:top}
tbody tr:nth-child(even){background:#F7F8FC}

code{background:#F0F1F7;padding:.5mm 1.4mm;border-radius:1mm;font-size:9.6pt;
  font-family:"DejaVu Sans Mono","Liberation Mono",monospace}
pre{background:#12142B;color:#E6EAF7;padding:4mm 5mm;border-radius:2.5mm;overflow:hidden;
  font-size:9.3pt;line-height:1.5;page-break-inside:avoid;margin:3.5mm 0}
pre code{background:none;color:inherit;padding:0;font-size:9.3pt}

.foot{margin-top:9mm;padding-top:3.5mm;border-top:.6pt solid #D7DCEA;
  font-size:8.6pt;color:#77809B;text-align:center}
"""


def build(md_name, title):
    global VERSION
    src = os.path.join(ROOT, md_name)
    if not os.path.exists(src):
        print("  absent :", md_name)
        return None
    import datetime
    VERSION = datetime.date.fromtimestamp(os.path.getmtime(src)).isoformat()
    with open(src, encoding="utf-8") as fh:
        text = fh.read()

    # Retirer le bloc d'en-tête interne (titre + citation de cadrage) : la couverture le remplace.
    body_md = re.sub(r"^#\s+.*?(?=\n---\n)", "", text, count=1, flags=re.S).lstrip("\n-")

    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )

    conf = (CONF_PUBLIC if md_name in PUBLICS else
            "Document confidentiel &middot; réservé aux partenaires actifs de NEBULA "
            "Agency. Ne pas diffuser hors de l'équipe.")

    page = (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{CSS}</style></head><body>"
        "<div class='cover'>"
        "<div class='kicker'>NEBULA Agency &middot; Cotonou</div>"
        "<div class='rule'></div>"
        f"<h1>{title}</h1>"
        f"<div class='meta'>Programme Partenaires<br>Version {VERSION}</div>"
        f"<div class='conf'>{conf}</div>"
        "</div>"
        f"{html_body}"
        "<div class='foot'>NEBULA Agency &middot; Cotonou, Bénin &middot; "
        "www.nebula-agency.online</div>"
        "</body></html>"
    )

    os.makedirs(OUT, exist_ok=True)
    pdf = os.path.join(OUT, md_name.replace(".md", ".pdf"))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(page)
        tmp = fh.name

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + tmp],
        check=True, capture_output=True, timeout=120,
    )
    os.unlink(tmp)
    return pdf


if __name__ == "__main__":
    print("Génération des PDF NEBULA\n")
    total = 0
    for name, title in DOCS:
        out = build(name, title)
        if out:
            ko = os.path.getsize(out) // 1024
            total += ko
            print(f"  {os.path.basename(out):32s} {ko:5d} Ko")
    print(f"\n  {total} Ko au total  ->  {OUT}")
