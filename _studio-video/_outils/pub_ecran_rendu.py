# -*- coding: utf-8 -*-
"""Rend la pub écran NEBULA dans les deux formats, l'un après l'autre, à UN onglet, sans rien perdre si Chrome tombe.

    python _outils/pub_ecran_rendu.py               le son, puis le 16:9, puis le 9:16
    python _outils/pub_ecran_rendu.py 169           le 16:9 seulement (le son est refait s'il manque)
    python _outils/pub_ecran_rendu.py tiktok        le 9:16 seulement

1. LE SON, une seule fois (il est le même pour les deux formats) : Remotion le rend sans photographier aucune image,
   puis on le mesure ; si une crête dépasse -1 dBTP (les bruitages s'ajoutent à la voix sans limiteur), un limiteur
   doux la ramène, sans toucher au reste.
2. L'IMAGE, par morceaux de 300 images (`rendu_morceaux.mjs`, un onglet) : chaque morceau ouvre un navigateur neuf, un
   morceau fini est gardé, relancer reprend là où ça s'était arrêté. Le son de l'étape 1 est posé tel quel.
3. Les fichiers finaux : `out/NEBULA-Pub-Ecran-16x9.mp4` et `out/NEBULA-Pub-Ecran-TikTok.mp4`, vérifiés (durée,
   pistes, niveau), en copie plafonnée à 8 Mb/s pour le téléphone et CAP ; le rendu brut reste en `-master.mp4`.
   (`python _outils/pub_ecran_rendu.py envoi` refait seulement ces copies.)
4. `python _outils/pub_ecran_rendu.py facebook` : la version Facebook, `out/NEBULA-Pub-Ecran-Facebook.mp4`, l'image de
   la version TikTok copiée telle quelle et un son SANS la musique (voix et bruitages), vérifié en synchro.

⚠️ Un seul travail lourd à la fois (8 Go) : rien d'autre pendant ce rendu, aucun navigateur de test ouvert.
⚠️ Après un changement de la vidéo, effacer `out/morceaux/<composition>/` : sinon les anciens morceaux sont repris.
   (Le son, lui, est refait à chaque fois ; `--garder-son` le reprend.)
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ICI = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or str(ICI / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe")
SON_BRUT = ICI / "out/pub-ecran-son-brut.wav"
SON = ICI / "out/pub-ecran-son.wav"
FORMATS = {
    "169": ("PubEcranNebula169", ICI / "out/NEBULA-Pub-Ecran-16x9.mp4"),
    "tiktok": ("PubEcranNebulaTikTok", ICI / "out/NEBULA-Pub-Ecran-TikTok.mp4"),
}


def mesurer(fichier):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-i", str(fichier), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else float("nan")), (float(p[-1]) if p else float("nan"))


def son():
    # le son est refait à chaque rendu (un son gardé d'un rendu d'avant serait celui d'une autre version) ;
    # `--garder-son` le reprend tel quel, quand on sait que rien n'a changé
    if SON.exists() and "--garder-son" in sys.argv:
        print(f"le son est repris : {SON.relative_to(ICI)}")
        return
    print("le son (sans image)…", flush=True)
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "PubEcranNebula169", str(SON_BRUT), "--codec=wav",
                    "--concurrency=1"], cwd=ICI, check=True, shell=True)
    lufs, crete = mesurer(SON_BRUT)
    print(f"  mélange : {lufs:.1f} LUFS, crête vraie {crete:.1f} dBTP")
    # le master : un gain simple (le mélange garde ses proportions) pour que l'ensemble tienne -16 LUFS, puis un
    # limiteur doux à -1,5 dBTP qui ne mord que sur les rares crêtes (les bruitages s'ajoutent à la voix)
    gain = -16.0 - lufs
    subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y", "-i", str(SON_BRUT), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=2:release=60:level=false", "-ar", "48000",
                    "-c:a", "pcm_s16le", str(SON)], check=True, capture_output=True)
    lufs, crete = mesurer(SON)
    print(f"  master : gain {gain:+.1f} dB → {lufs:.1f} LUFS, crête vraie {crete:.1f} dBTP")


def master_de(final):
    return final.with_name(final.stem + "-master.mp4")


def image(cle):
    """Le rendu brut va DIRECTEMENT dans `-master.mp4` (il remplace l'ancien) : la copie à envoyer est faite ensuite
    depuis lui. ⚠️ Le 21/11, la première version gardait un ancien master et aurait réencodé l'ANCIENNE vidéo."""
    ident, final = FORMATS[cle]
    master = master_de(final)
    print("", flush=True)
    print(f"{ident} → {master.name}", flush=True)
    subprocess.run(["node", "_outils/rendu_morceaux.mjs", ident, "300", "1", str(SON.relative_to(ICI))], cwd=ICI, check=True)
    os.replace(ICI / "out" / f"{ident}.mp4", master)
    sonde = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                            "-of", "json", str(master)], capture_output=True, text=True)
    d = json.loads(sonde.stdout)
    pistes = ", ".join(f"{s['codec_type']} {s.get('width', '')}x{s.get('height', '')}".replace(" x", "") for s in d["streams"])
    lufs, crete = mesurer(master)
    print(f"  {master.relative_to(ICI)} : {float(d['format']['duration']):.2f} s · {pistes} · {lufs:.1f} LUFS, crête {crete:.1f} dBTP")


def envoi(cle):
    """Le fichier qu'on envoie : le rendu de Remotion pèse 37 à 78 Mb/s (le grain de l'image coûte cher), trop lourd
    pour un téléphone et pour le coffre de CAP (50 Mo par fichier). On écrit, depuis le `-master.mp4`, une copie
    plafonnée à 8 Mb/s (TikTok réencode de toute façon vers 2 à 4 Mb/s)."""
    _, final = FORMATS[cle]
    master = master_de(final)
    if not master.exists():
        print(f"  pas de master pour {final.name}")
        return
    subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y", "-i", str(master), "-c:v", "libx264", "-preset", "slow",
                    "-crf", "19", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-c:a", "copy", "-movflags", "+faststart", str(final)], check=True, capture_output=True)
    print(f"  à envoyer : {final.relative_to(ICI)} ({final.stat().st_size / 1e6:.0f} Mo ; master {master.stat().st_size / 1e6:.0f} Mo)")


SON_FB_BRUT = ICI / "out/pub-ecran-son-sans-musique-brut.wav"
SON_FB = ICI / "out/pub-ecran-son-sans-musique.wav"
FACEBOOK = ICI / "out/NEBULA-Pub-Ecran-Facebook.mp4"


def piste(fichier, debut, duree):
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", str(debut), "-t", str(duree), "-i", str(fichier), "-vn", "-ac", "1",
                        "-ar", "48000", "-f", "f32le", "-"], capture_output=True, check=True)
    import numpy as np
    return np.frombuffer(r.stdout, dtype=np.float32)


def decalage_ms(a, b, debut, duree=2.0):
    """Le décalage entre deux pistes sur un passage de voix (corrélation croisée, ±150 ms) : 0 = synchrones."""
    import numpy as np
    x, y = piste(a, debut, duree), piste(b, debut, duree)
    n = min(len(x), len(y))
    x, y = x[:n] - x[:n].mean(), y[:n] - y[:n].mean()
    lim = int(0.15 * 48000)
    c = np.correlate(x, np.pad(y, lim), mode="valid")
    return (np.argmax(c) - lim) / 48.0


def facebook():
    """La version Facebook (Mongazi publie à 17 h sur TikTok, puis sur Facebook) : la vidéo TikTok finale, son image
    COPIÉE telle quelle, et un son refait SANS la musique (voix et bruitages seuls), ramené à -16 LUFS. Pourquoi : le
    Content ID de la musique n'est pas vérifié, et Facebook peut couper tout le son d'une vidéo dont la musique est
    déposée. Les props passent par un fichier (`--props=<json>`) : en ligne de commande Windows, les guillemets d'un
    JSON se perdent."""
    source = FORMATS["tiktok"][1]
    props = ICI / "out/pub-ecran-props-facebook.json"
    props.write_text('{"musique": false}', encoding="utf-8")
    print("le son sans musique (sans image)…", flush=True)
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "PubEcranNebula169", str(SON_FB_BRUT), "--codec=wav",
                    "--concurrency=1", f"--props={props}"], cwd=ICI, check=True, shell=True)
    lufs, crete = mesurer(SON_FB_BRUT)
    gain = -16.0 - lufs
    subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y", "-i", str(SON_FB_BRUT), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=2:release=60:level=false", "-ar", "48000",
                    "-c:a", "pcm_s16le", str(SON_FB)], check=True, capture_output=True)
    lufs, crete = mesurer(SON_FB)
    print(f"  sans musique : gain {gain:+.1f} dB → {lufs:.1f} LUFS, crête vraie {crete:.1f} dBTP")
    subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y", "-i", str(source), "-i", str(SON_FB), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(FACEBOOK)],
                   check=True, capture_output=True)
    lufs, crete = mesurer(FACEBOOK)
    print(f"  {FACEBOOK.relative_to(ICI)} : {FACEBOOK.stat().st_size / 1e6:.0f} Mo · {lufs:.1f} LUFS, crête {crete:.1f} dBTP")
    for t in (8.6, 30.0):
        print(f"  synchro avec la version TikTok à {t:.1f} s : {decalage_ms(source, FACEBOOK, t):+.1f} ms")


if __name__ == "__main__":
    voulu = [a for a in sys.argv[1:] if not a.startswith("--")] or ["169", "tiktok"]
    if voulu == ["envoi"]:
        for cle in FORMATS:
            envoi(cle)
        sys.exit(0)
    if voulu == ["facebook"]:
        facebook()
        sys.exit(0)
    son()
    for cle in ("169", "tiktok"):
        if cle in voulu:
            image(cle)
            envoi(cle)
