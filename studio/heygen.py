# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — moteur vidéo PREMIUM optionnel (HeyGen, avatar parlant).

OFF par défaut : la vidéo quotidienne utilise le moteur kinetic (gratuit, illimité).
Activer avec STUDIO_VIDEO=heygen — consomme des crédits HeyGen (300 dispo).
Clé : HEYGEN_API_KEY (secrets/heygen.env).

⚠️ Non testé "en vrai" pour ne pas consommer de crédits sans accord. Le flux suit
la doc HeyGen v2 (generate) + polling v1 (status). À valider sur un 1er essai.
"""
import os, time, pathlib

API = "https://api.heygen.com"

def _key():
    k = os.environ.get("HEYGEN_API_KEY")
    if not k:
        raise RuntimeError("HEYGEN_API_KEY introuvable.")
    return k

def _pick_voice(cli, key):
    r = cli.get(f"{API}/v2/voices", headers={"X-Api-Key": key})
    voices = (r.json().get("data") or {}).get("voices", [])
    fr = [v for v in voices if str(v.get("language", "")).lower().startswith(("fr", "french"))]
    pool = fr or voices
    return pool[0]["voice_id"] if pool else None

def _pick_avatar(cli, key):
    r = cli.get(f"{API}/v2/avatars", headers={"X-Api-Key": key})
    data = r.json().get("data") or {}
    avs = data.get("avatars", []) or []
    return avs[0]["avatar_id"] if avs else None

def render(concept, out_dir):
    import httpx
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    key = _key()
    script = concept.get("script") or concept.get("hook") or ""
    with httpx.Client(timeout=120) as cli:
        voice_id = os.environ.get("HEYGEN_VOICE_ID") or _pick_voice(cli, key)
        avatar_id = os.environ.get("HEYGEN_AVATAR_ID") or _pick_avatar(cli, key)
        if not voice_id or not avatar_id:
            raise RuntimeError("Voix/avatar HeyGen indisponibles.")
        body = {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": avatar_id, "avatar_style": "normal"},
                "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
            }],
            "dimension": {"width": 720, "height": 1280},
        }
        r = cli.post(f"{API}/v2/video/generate",
                     headers={"X-Api-Key": key, "Content-Type": "application/json"}, json=body)
        r.raise_for_status()
        vid = (r.json().get("data") or {}).get("video_id")
        if not vid:
            raise RuntimeError(f"Pas de video_id : {r.text}")
        url = None
        for _ in range(60):                         # ~5 min max
            time.sleep(5)
            s = cli.get(f"{API}/v1/video_status.get", headers={"X-Api-Key": key},
                        params={"video_id": vid}).json()
            d = s.get("data") or {}
            if d.get("status") == "completed":
                url = d.get("video_url"); break
            if d.get("status") == "failed":
                raise RuntimeError(f"HeyGen a échoué : {d.get('error')}")
        if not url:
            raise RuntimeError("HeyGen : délai dépassé.")
        mp4 = out_dir / "video.mp4"
        with cli.stream("GET", url) as resp:
            with open(mp4, "wb") as fh:
                for ch in resp.iter_bytes():
                    fh.write(ch)
    return {"video": str(mp4), "mp4": str(mp4), "webm": None, "poster": None}
