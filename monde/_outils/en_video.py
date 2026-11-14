"""LE MONDE · une image vers une vidéo (image → vidéo), GRATUITEMENT, par Wan 2.2 sur Hugging Face (ZeroGPU).

    python monde/_outils/en_video.py depart.jpg --sortie video.mp4 --consigne "she talks warmly…" [--duree 5]
    python monde/_outils/en_video.py depart.jpg --fin depart.jpg --sortie boucle.mp4 --consigne "…"   # boucle parfaite

Mongazi (2026-11-14) : « fais ce que tu as à faire » (Hillary est d'accord), sans rien acheter : WaveSpeed et
Higgsfield sont à zéro. Wan 2.2 (Alibaba) : code ET poids sous licence Apache 2.0, comme l'accélérateur
« Lightning » de lightx2v (vérifié le 2026-11-14 sur l'API de Hugging Face : `Wan-AI/Wan2.2-I2V-A14B`,
`lightx2v/Wan2.2-Lightning`, `license:apache-2.0`).

Deux démos publiques, mêmes réglages :
- sans `--fin` : `zerogpu-aoti/wan2-2-fp8da-aoti-faster` (une image de départ, 5 s au plus, 16 i/s, 832 px au plus) ;
- avec `--fin` : `multimodalart/wan-2-2-first-last-frame` (première ET dernière image : donner deux fois la même
  image fait une BOUCLE qui se rejoue sans saut, 5,1 s au plus).

⚠️ Le quota gratuit de carte graphique est court (quelques minutes par jour avec un compte gratuit, moins sans) :
une vidéo de 5 s en consomme environ une minute. Choisir ce qu'on génère. `--sans-jeton` : le quota anonyme, compté
à part. Même protocole que `en_3d.py` (Gradio « sse_v3 », par HTTP, sans bibliothèque).
⛔ Aucun visage d'une personne réelle sans son accord (Hillary : `_partage/…/hillary/ACCORD.md`).
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
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
ESPACES = {
    "depart": "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space",
    "boucle": "https://multimodalart-wan-2-2-first-last-frame.hf.space",
}
NEGATIF = ("色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, "
           "多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走")


def jeton() -> str | None:
    if os.environ.get("NEBULA_SANS_JETON"):
        return None
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


def envoyer_fichier(api: str, chemin: Path) -> dict:
    limite = "----nebula" + uuid.uuid4().hex
    corps = (f"--{limite}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{chemin.name}\"\r\n"
             f"Content-Type: {mimetypes.guess_type(chemin.name)[0] or 'application/octet-stream'}\r\n\r\n").encode()
    corps += chemin.read_bytes() + f"\r\n--{limite}--\r\n".encode()
    req = urllib.request.Request(api + "/upload", data=corps, headers=entetes({"Content-Type": f"multipart/form-data; boundary={limite}"}))
    chemins = json.load(urllib.request.urlopen(req, timeout=180))
    return {"path": chemins[0], "url": None, "orig_name": chemin.name, "size": chemin.stat().st_size,
            "mime_type": mimetypes.guess_type(chemin.name)[0], "meta": {"_type": "gradio.FileData"}}


def appeler(api: str, fn_index: int, donnees: list, session: str, delai=1200) -> list:
    corps = json.dumps({"data": donnees, "event_data": None, "fn_index": fn_index, "trigger_id": None, "session_hash": session}).encode()
    req = urllib.request.Request(api + "/queue/join", data=corps, headers=entetes({"Content-Type": "application/json"}))
    evt = json.load(urllib.request.urlopen(req, timeout=90))["event_id"]
    flux = urllib.request.urlopen(urllib.request.Request(api + f"/queue/data?session_hash={session}", headers=entetes()), timeout=delai)
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
                # le message dit le plus souvent le quota : « You have exceeded your GPU quota (… requested vs. … left) »
                print(f"⛔ échec de la démo : {json.dumps(m.get('output'), ensure_ascii=False)[:600]}", flush=True)
                raise SystemExit(3)
            print(f"   fait en {time.time() - debut:.0f} s", flush=True)
            return m["output"]["data"]
    print("⛔ le flux s'est fermé sans résultat", flush=True)
    raise SystemExit(4)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--sortie", type=Path, required=True)
    ap.add_argument("--consigne", required=True)
    ap.add_argument("--fin", type=Path, default=None, help="la dernière image (la même que la première = une boucle)")
    ap.add_argument("--duree", type=float, default=5.0)
    ap.add_argument("--etapes", type=int, default=None, help="pas de calcul (6 sans --fin, 8 avec)")
    ap.add_argument("--graine", type=int, default=42)
    ap.add_argument("--sans-jeton", action="store_true")
    a = ap.parse_args()
    if a.sans_jeton:
        os.environ["NEBULA_SANS_JETON"] = "1"
    mode = "boucle" if a.fin else "depart"
    api = ESPACES[mode] + "/gradio_api"
    session = "".join(random.choices(string.ascii_lowercase + string.digits, k=11))
    print(f"→ Wan 2.2 ({mode}) · {a.image.name} · {a.duree:g} s · graine {a.graine} · {'avec' if jeton() else 'sans'} jeton Hugging Face", flush=True)
    try:
        img = envoyer_fichier(api, a.image)
        if mode == "boucle":
            fin = img if a.fin.resolve() == a.image.resolve() else envoyer_fichier(api, a.fin)
            donnees = [img, fin, a.consigne, NEGATIF, min(a.duree, 5.1), a.etapes or 8, 1.0, 1.0, a.graine, False]
        else:
            donnees = [img, a.consigne, a.etapes or 6, NEGATIF, min(a.duree, 5.0), 1, 1, a.graine, False]
        sortie = appeler(api, 0, donnees, session)
    except urllib.error.HTTPError as e:
        print(f"⛔ HTTP {e.code} : {e.read().decode('utf-8', 'replace')[:400]}", flush=True)
        raise SystemExit(5)
    v = sortie[0]
    fichier = v.get("video", v) if isinstance(v, dict) else v
    url = fichier.get("url") or (api + "/file=" + fichier["path"])
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=entetes()), timeout=300) as r:
        a.sortie.write_bytes(r.read())
    print(f"✅ {a.sortie} · {a.sortie.stat().st_size / 1e6:.2f} Mo · graine {sortie[1] if len(sortie) > 1 else a.graine}", flush=True)


if __name__ == "__main__":
    main()
