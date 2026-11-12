"""LE MONDE · une image vers un modèle 3D texturé (.glb), GRATUITEMENT.

    python monde/_outils/en_3d.py image.png --sortie modele.glb [--resolution 512|1024] [--faces 120000]

Passe par la démo publique de TRELLIS.2 (Microsoft) sur Hugging Face :
code ET poids sous licence MIT (vérifié le 2026-11-12 sur l'API de Hugging Face).
Choisie par Mongazi le 2026-11-12 (« voie gratuite »).

⚠️ On parle à la démo par HTTP, sans bibliothèque : ce jour-là, PyPI et GitHub ne
répondaient pas depuis la connexion de Cotonou (Hugging Face, si). Protocole Gradio 6
« sse_v3 » : envoyer le fichier, rejoindre la file avec un identifiant de session,
lire le flux jusqu'à « process_completed ». Le même identifiant garde l'état entre
« image_to_3d » et « extract_glb ».
⚠️ Quota gratuit de carte graphique : sans compte, il est court. Avec un jeton
Hugging Face gratuit (variable HF_TOKEN, ou secrets/huggingface.env), il est plus long.
⛔ Règle NEBULA : un modèle généré d'une pièce du catalogue est VALIDÉ par la cliente
avant d'être exposé, et sa fiche garde la vraie photo.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import random
import re
import string
import sys
import time
import urllib.request
import uuid
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
ESPACE = "https://microsoft-trellis-2.hf.space"
API = ESPACE + "/gradio_api"


def jeton() -> str | None:
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    f = RACINE_DEPOT / "secrets" / "huggingface.env"
    if f.exists():
        m = re.search(r"^HF_TOKEN=(.+)$", f.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return None


def entetes(extra=None):
    h = {"User-Agent": "NEBULA-Monde/0.1"}
    t = jeton()
    if t:
        h["Authorization"] = "Bearer " + t
    if extra:
        h.update(extra)
    return h


def envoyer_fichier(chemin: Path) -> dict:
    limite = "----nebula" + uuid.uuid4().hex
    corps = (f"--{limite}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{chemin.name}\"\r\n"
             f"Content-Type: {mimetypes.guess_type(chemin.name)[0] or 'application/octet-stream'}\r\n\r\n").encode()
    corps += chemin.read_bytes() + f"\r\n--{limite}--\r\n".encode()
    req = urllib.request.Request(API + "/upload", data=corps, headers=entetes({"Content-Type": f"multipart/form-data; boundary={limite}"}))
    chemins = json.load(urllib.request.urlopen(req, timeout=120))
    return {"path": chemins[0], "url": None, "orig_name": chemin.name, "size": chemin.stat().st_size,
            "mime_type": mimetypes.guess_type(chemin.name)[0], "meta": {"_type": "gradio.FileData"}}


def appeler(fn_index: int, donnees: list, session: str, delai=900) -> list:
    corps = json.dumps({"data": donnees, "event_data": None, "fn_index": fn_index, "trigger_id": None, "session_hash": session}).encode()
    req = urllib.request.Request(API + "/queue/join", data=corps, headers=entetes({"Content-Type": "application/json"}))
    evt = json.load(urllib.request.urlopen(req, timeout=60))["event_id"]
    flux = urllib.request.urlopen(urllib.request.Request(API + f"/queue/data?session_hash={session}", headers=entetes()), timeout=delai)
    debut = time.time()
    for brut in flux:
        ligne = brut.decode("utf-8", "replace").strip()
        if not ligne.startswith("data:"):
            continue
        m = json.loads(ligne[5:])
        if m.get("event_id") not in (None, evt):
            continue
        t = m.get("msg")
        if t == "estimation":
            print(f"   file d'attente : rang {m.get('rank')}, ≈ {m.get('rank_eta') or 0:.0f} s", flush=True)
        elif t == "process_starts":
            print("   la carte graphique travaille…", flush=True)
        elif t == "process_completed":
            if not m.get("success"):
                raise SystemExit(f"⛔ échec de la démo : {json.dumps(m.get('output'), ensure_ascii=False)[:400]}")
            print(f"   fait en {time.time() - debut:.0f} s", flush=True)
            return m["output"]["data"]
    raise SystemExit("⛔ le flux s'est fermé sans résultat")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--sortie", type=Path, required=True)
    ap.add_argument("--resolution", default="512", choices=["512", "1024", "1536"])
    ap.add_argument("--faces", type=int, default=120000, help="nombre de faces visé (léger pour la 3G)")
    ap.add_argument("--texture", type=int, default=1024)
    ap.add_argument("--graine", type=int, default=0)
    ap.add_argument("--detourer-ici", action="store_true",
                    help="détourer sur le PC (rembg) : 2 calculs Hugging Face au lieu de 3, le quota gratuit compte les calculs")
    a = ap.parse_args()
    session = "".join(random.choices(string.ascii_lowercase + string.digits, k=11))
    print(f"→ TRELLIS.2 · {a.image.name} · session {session} · {'avec' if jeton() else 'sans'} jeton Hugging Face")
    if a.detourer_ici:
        from rembg import new_session, remove
        from PIL import Image
        detoure = a.image.with_name(a.image.stem + "-detoure.png")
        remove(Image.open(a.image).convert("RGB"), session=new_session("isnet-general-use")).save(detoure)
        print(f"1/3 · détouré sur le PC : {detoure.name}")
        img = envoyer_fichier(detoure)
        appeler(2, [], session)                                     # start_session (sans carte graphique)
        pre = img
    else:
        img = envoyer_fichier(a.image)
        appeler(2, [], session)                                     # start_session
        print("1/3 · détourage")
        pre = appeler(4, [img], session)[0]                          # preprocess_image
    print("2/3 · image vers 3D")
    appeler(7, [pre, a.graine, a.resolution, 7.5, 0.7, 12, 5.0, 7.5, 0.5, 12, 3.0, 1.0, 0.0, 12, 3.0], session)
    print("3/3 · export .glb")
    sortie = appeler(9, [None, a.faces, a.texture], session)        # extract_glb (l'état reste côté serveur)
    fichier = sortie[1] if isinstance(sortie[1], dict) else sortie[0]
    url = fichier.get("url") or (API + "/file=" + fichier["path"])
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=entetes()), timeout=300) as r:
        a.sortie.write_bytes(r.read())
    print(f"✅ {a.sortie} · {a.sortie.stat().st_size / 1e6:.1f} Mo")


if __name__ == "__main__":
    main()
