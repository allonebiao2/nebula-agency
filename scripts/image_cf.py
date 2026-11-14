# -*- coding: utf-8 -*-
"""
Images générées par Cloudflare Workers AI (quota gratuit chaque jour, rien ne tourne sur le PC).

    python scripts/image_cf.py "une phrase" --sortie image.jpg
    python scripts/image_cf.py "une phrase" --modele flux-2-dev --largeur 1024 --hauteur 1536 --sortie affiche.jpg
    python scripts/image_cf.py --modeles          # la liste des modèles d'images du compte

La clé vit dans secrets/cloudflare.env (CLOUDFLARE_AI_TOKEN, droit « Workers AI » seul), jamais dans le dépôt.
⛔ Règle NEBULA : une image générée ne devient JAMAIS le catalogue d'un client (ambiance, matière, lieu : oui).
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RACINE = Path(__file__).resolve().parent.parent
RAPIDES = {"flux-1-schnell": "@cf/black-forest-labs/flux-1-schnell", "flux-2-dev": "@cf/black-forest-labs/flux-2-dev",
           "flux-2-klein-9b": "@cf/black-forest-labs/flux-2-klein-9b", "flux-2-klein-4b": "@cf/black-forest-labs/flux-2-klein-4b",
           "lucid-origin": "@cf/leonardo/lucid-origin", "phoenix": "@cf/leonardo/phoenix-1.0",
           "sdxl": "@cf/stabilityai/stable-diffusion-xl-base-1.0", "sdxl-lightning": "@cf/bytedance/stable-diffusion-xl-lightning",
           "dreamshaper": "@cf/lykon/dreamshaper-8-lcm"}


def cles() -> tuple[str, str]:
    env = dict(re.findall(r"^([A-Z_]+)=(.+)$", (RACINE / "secrets" / "cloudflare.env").read_text(encoding="utf-8"), re.M))
    if "CLOUDFLARE_AI_TOKEN" not in env:
        raise SystemExit("CLOUDFLARE_AI_TOKEN absent de secrets/cloudflare.env (un jeton au modèle « Workers AI »)")
    return env["CLOUDFLARE_ACCOUNT_ID"].strip(), env["CLOUDFLARE_AI_TOKEN"].strip()


def _envoyer(url: str, tok: str, corps: bytes, type_: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, data=corps, headers={"Authorization": f"Bearer {tok}", "Content-Type": type_})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()


def _multipart(champs: dict) -> tuple[bytes, str]:
    b = uuid.uuid4().hex
    corps = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in champs.items())
    return corps + f"--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def generer(prompt: str, modele: str = "flux-1-schnell", largeur: int = 1024, hauteur: int = 1024, etapes: int | None = None) -> bytes:
    """Rend les octets de l'image. Les modèles n'acceptent pas tous la même forme : JSON d'abord, formulaire sinon
    (FLUX.2) ; la réponse est soit l'image brute, soit du JSON qui la porte en base64."""
    acc, tok = cles()
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{RAPIDES.get(modele, modele)}"
    champs = {"prompt": prompt}
    if modele != "flux-1-schnell":   # ⚠️ depuis le 2026-11-14, FLUX.1 schnell refuse width/height (erreur 5006) : il rend 1024 × 1024
        champs.update(width=largeur, height=hauteur)
    if etapes:
        champs["steps" if "flux" in modele else "num_steps"] = etapes
    code, typ, corps = _envoyer(url, tok, json.dumps(champs).encode(), "application/json")
    if code != 200 and b"multipart" in corps.lower():
        code, typ, corps = _envoyer(url, tok, *_multipart(champs))
    if code != 200:
        raise SystemExit(f"Workers AI {code} : {corps[:300]!r}")
    if typ.startswith("image/"):
        return corps
    d = json.loads(corps)
    img = (d.get("result") or {}).get("image") if isinstance(d.get("result"), dict) else None
    if not img:
        raise SystemExit(f"réponse sans image : {str(d)[:300]}")
    return base64.b64decode(img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("--modele", default="flux-1-schnell", help=" · ".join(RAPIDES))
    ap.add_argument("--largeur", type=int, default=1024)
    ap.add_argument("--hauteur", type=int, default=1024)
    ap.add_argument("--etapes", type=int)
    ap.add_argument("--sortie", default="image.jpg")
    ap.add_argument("--modeles", action="store_true")
    a = ap.parse_args()
    if a.modeles:
        acc, tok = cles()
        req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/models/search?task=Text-to-Image&per_page=50",
                                     headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            for m in json.loads(r.read())["result"]:
                print(m["name"])
        return
    if not a.prompt:
        ap.error("donne une phrase")
    t = time.time()
    img = generer(a.prompt, a.modele, a.largeur, a.hauteur, a.etapes)
    Path(a.sortie).write_bytes(img)
    print(f"{a.sortie} · {len(img) // 1024} Ko · {a.modele} · {time.time() - t:.1f} s")


if __name__ == "__main__":
    main()
