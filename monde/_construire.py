"""LE MONDE · construire un lieu à partir de ses sources.

    python monde/_construire.py              # prépare le lieu pour le serveur local
    python monde/_construire.py --dist       # + assemble monde/_dist/ pour la mise en ligne

⛔ RÈGLE FONDATRICE (héritée de LE STANDARD) : le catalogue n'est JAMAIS recopié.
Il est LU, à chaque construction, dans la source de la vitrine d'Hillary, par le
lecteur de littéraux de LE STANDARD, qui n'exécute aucun code. Hillary change un
prix sur son site : le salon change à la construction suivante.

Ce que ce script écrit (tout est GÉNÉRÉ, rien n'est à éditer à la main) :
  lieux/hillary-m-styl/donnees.js     le catalogue, les pays, les délais, les mesures, le numéro
  lieux/hillary-m-styl/img/           les photos des pièces et le logo, copiées de la vitrine
  lieux/hillary-m-styl/polices/       ses trois polices, copiées de la vitrine
"""
from __future__ import annotations

import io
import json
import re
import shutil
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(RACINE / "whatsapp-agent"))
from lecteurs.js_litteral import lire_declaration  # noqa: E402

CLIENT = RACINE / "clients" / "10-hillary-m-styl"
SOURCE = CLIENT / "_vitrine_src.html"           # la source assemblée, celle que lit LE STANDARD
LIEU = ICI / "lieux" / "hillary-m-styl"


def lire_vitrine() -> dict:
    src = SOURCE.read_text(encoding="utf-8")
    d = {}
    for nom in ("PIECES", "PAYS", "DELAIS", "MESURES", "ATELIER", "TAILLES"):
        d[nom] = lire_declaration(src, nom)
    m = re.search(r'var\s+WHATSAPP\s*=\s*"(\d{8,15})"', src)
    if not m:
        raise SystemExit("⛔ numéro WhatsApp introuvable dans la vitrine : on n'en invente pas")
    d["WHATSAPP"] = m.group(1)
    m = re.search(r'var\s+AIDE\s*=\s*"([^"]*)"', src)
    d["AIDE"] = m.group(1) if m else ""
    if not d["PIECES"]:
        raise SystemExit("⛔ PIECES lu vide")
    return d


def preparer_images(pieces: list) -> None:
    dst = LIEU / "img"
    dst.mkdir(parents=True, exist_ok=True)
    src = CLIENT / "assets" / "images"
    noms = {"logo.png", "logo.webp"}
    for p in pieces:
        for cle in ("img", "img2"):
            if p.get(cle):
                noms.add(p[cle])
    manquantes = []
    for n in sorted(noms):
        f = src / n
        if not f.exists():
            manquantes.append(n)
            continue
        cible = dst / n
        if not cible.exists() or cible.stat().st_mtime < f.stat().st_mtime:
            shutil.copy2(f, cible)
    if manquantes:
        raise SystemExit(f"⛔ photos absentes de la vitrine : {manquantes}")


def preparer_polices() -> None:
    dst = LIEU / "polices"
    dst.mkdir(parents=True, exist_ok=True)
    for f in (CLIENT / "assets" / "fonts").glob("*.woff2"):
        shutil.copy2(f, dst / f.name)


def lire_faits() -> dict:
    """Ce que Mongazi tient à jour à la main (TikTok, événements, quartier).
    Une valeur vide = la fonction reste cachée dans le salon. Rien n'est inventé."""
    f = LIEU / "faits.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def ecrire_donnees(v: dict, faits: dict) -> Path:
    pieces = []
    for p in v["PIECES"]:
        q = {k: p.get(k) for k in ("id", "cat", "nom", "type", "typeLibre", "tag", "img", "img2",
                                   "prix", "jmin", "jmax", "expPrix", "expMin", "expMax",
                                   "eur", "usd", "eurExp", "usdExp", "ds") if p.get(k) is not None}
        pieces.append(q)
    donnees = {
        "source": "clients/10-hillary-m-styl/_vitrine_src.html (lu par monde/_construire.py)",
        "whatsapp": v["WHATSAPP"],
        "atelier": v["ATELIER"],
        "pays": v["PAYS"],
        "delais": v["DELAIS"],
        "mesures": v["MESURES"],
        "tailles": v["TAILLES"],
        "aide_mesures": v["AIDE"],
        "pieces": pieces,
        "faits": faits,
    }
    js = ("/* ⛔ FICHIER GÉNÉRÉ par monde/_construire.py : ne pas éditer.\n"
          "   Le catalogue est LU dans la vitrine d'Hillary, jamais recopié. */\n"
          "export const DONNEES = " + json.dumps(donnees, ensure_ascii=False, indent=1) + ";\n")
    cible = LIEU / "donnees.js"
    io.open(cible, "w", encoding="utf-8", newline="\n").write(js)
    return cible


def assembler_dist() -> Path:
    dist = ICI / "_dist"
    if dist.exists():
        shutil.rmtree(dist)
    shutil.copytree(ICI / "socle", dist / "socle")
    exclus = shutil.ignore_patterns("_*", "*.md")
    shutil.copytree(LIEU, dist / "lieux" / "hillary-m-styl", ignore=exclus)
    for f in ("_worker.js", "_headers", "index.html", "404.html"):
        if (ICI / "publier" / f).exists():
            shutil.copy2(ICI / "publier" / f, dist / f)
    return dist


def main() -> None:
    v = lire_vitrine()
    preparer_images(v["PIECES"])
    preparer_polices()
    faits = lire_faits()
    cible = ecrire_donnees(v, faits)
    print(f"✅ {len(v['PIECES'])} pièces, {len(v['PAYS'])} pays, {len(v['MESURES'])} jeux de mesures "
          f"lus dans la vitrine · numéro {v['WHATSAPP']} · {cible.relative_to(RACINE)}")
    if "--dist" in sys.argv:
        d = assembler_dist()
        poids = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        print(f"✅ {d.relative_to(RACINE)} assemblé · {poids/1e6:.1f} Mo")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
