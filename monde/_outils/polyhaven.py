"""LE MONDE · télécharger les matières, éclairages et objets de Poly Haven (CC0).

    python monde/_outils/polyhaven.py

Poly Haven (polyhaven.com) : matières photographiées, éclairages HDR et objets scannés,
tous en CC0 (domaine public, usage commercial permis, sans attribution exigée ; on crédite
quand même). C'est ce qui sépare un décor « maquette » (couleurs unies) d'un décor qui a
l'air réel. Mongazi, 2026-11-12 : « le graphisme et la qualité doivent ressembler à Call of
Duty Korea, GTA 6… c'est un des objectifs principaux ».

Tout est ALLÉGÉ pour le téléphone : textures en 1K, converties en WebP (qualité 80), et la
liste ci-dessous est courte exprès. ⚠️ Chaque Mo compte en 3G.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ICI = Path(__file__).resolve().parents[1]
DEST = ICI / "socle" / "ressources" / "polyhaven"
API = "https://api.polyhaven.com"
UA = {"User-Agent": "NEBULA-Monde/0.1"}

MATIERES = {            # nom Poly Haven : cartes voulues
    "marble_01": ["Diffuse", "nor_gl", "Rough"],
    "painted_plaster_wall": ["Diffuse", "nor_gl", "Rough"],
    "oak_veneer_01": ["Diffuse", "nor_gl", "Rough"],
    "velour_velvet": ["Diffuse", "nor_gl", "Rough"],
}
ECLAIRAGES = ["photo_studio_loft_hall"]
OBJETS = ["potted_plant_01", "potted_plant_04", "modern_arm_chair_01", "coffee_table_round_01",
          "ceramic_vase_01", "brass_vase_01", "decorative_book_set_01", "modern_ceiling_lamp_01"]


def lire_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))


def lire(url) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()


def en_webp(octets: bytes, cible: Path, cote=1024):
    im = Image.open(io.BytesIO(octets))
    im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
    if max(im.size) > cote:
        im.thumbnail((cote, cote))
    im.save(cible, "WEBP", quality=80, method=5)


def matieres():
    for nom, cartes in MATIERES.items():
        d = DEST / nom; d.mkdir(parents=True, exist_ok=True)
        f = lire_json(f"{API}/files/{nom}")
        for c in cartes:
            entree = f.get(c) or f.get(c.lower())
            if not entree:
                print(f"   ⚠️ {nom} : pas de carte {c}"); continue
            src = (entree.get("1k") or entree.get("2k"))["jpg"]["url"]
            cible = d / f"{c.lower()}.webp"
            if not cible.exists():
                en_webp(lire(src), cible)
        print(f"✅ matière {nom}")


def eclairages():
    for nom in ECLAIRAGES:
        d = DEST / nom; d.mkdir(parents=True, exist_ok=True)
        f = lire_json(f"{API}/files/{nom}")
        src = f["hdri"]["1k"]["hdr"]["url"]
        cible = d / "eclairage_1k.hdr"
        if not cible.exists():
            cible.write_bytes(lire(src))
        print(f"✅ éclairage {nom} · {cible.stat().st_size / 1e6:.1f} Mo")


def objets():
    for nom in OBJETS:
        d = DEST / nom; d.mkdir(parents=True, exist_ok=True)
        f = lire_json(f"{API}/files/{nom}")
        if "gltf" not in f or "1k" not in f["gltf"]:
            print(f"   ⚠️ {nom} : pas de glTF en 1K, ignoré"); continue
        g = f["gltf"]["1k"]["gltf"]
        (d / f"{nom}.gltf").write_bytes(lire(g["url"]))
        for chemin, info in g.get("include", {}).items():
            cible = d / chemin; cible.parent.mkdir(parents=True, exist_ok=True)
            if not cible.exists():
                cible.write_bytes(lire(info["url"]))
        alleger(d / f"{nom}.gltf")
        poids = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
        print(f"✅ objet {nom} · {poids / 1e6:.1f} Mo")


def alleger(gltf: Path, cote=1024):
    """les textures d'un objet en WebP (le glTF pointe dessus) : un objet de 6 Mo tombe à ~1 Mo"""
    d = json.loads(gltf.read_text(encoding="utf-8"))
    for im in d.get("images", []):
        uri = im.get("uri", "")
        if not uri or uri.endswith(".webp"):
            continue
        src = gltf.parent / uri
        if not src.exists():
            continue
        cible = src.with_suffix(".webp")
        en_webp(src.read_bytes(), cible, cote)
        src.unlink()
        im["uri"] = str(Path(uri).with_suffix(".webp")).replace("\\", "/")
        im.pop("mimeType", None)
    gltf.write_text(json.dumps(d), encoding="utf-8")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "LICENCE.md").write_text("Tout ce dossier vient de Poly Haven (polyhaven.com), sous licence CC0 "
                                     "(domaine public, usage commercial permis). Merci à Poly Haven et à ses auteurs.\n", encoding="utf-8")
    matieres(); eclairages(); objets()
    total = sum(p.stat().st_size for p in DEST.rglob("*") if p.is_file())
    print(f"\nTotal : {total / 1e6:.1f} Mo dans {DEST}")
