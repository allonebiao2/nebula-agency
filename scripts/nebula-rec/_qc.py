# -*- coding: utf-8 -*-
"""Contrôles de NEBULA REC.

    python scripts/nebula-rec/_qc.py          # sans rien filmer (quelques secondes)
    python scripts/nebula-rec/_qc.py --reel   # + de vraies captures de l'écran (2 à 4 minutes sur ce PC)

⚠️ Sur le PC de Cotonou : une seule tâche lourde à la fois (voir la mémoire « Disque du PC »).
"""

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import moteur  # noqa: E402
from icone import fabriquer_icone  # noqa: E402

VERTS, ROUGES = [], []


def ok(condition, libelle, detail=""):
    (VERTS if condition else ROUGES).append(libelle)
    print(("  ✅ " if condition else "  ❌ ") + libelle + (f"  ({detail})" if detail else ""), flush=True)
    return condition


def flux(ffprobe, chemin):
    r = moteur.lancer([ffprobe, "-v", "error", "-show_entries", "stream=codec_type,codec_name,duration,width,height",
                       "-of", "json", chemin], timeout=120)
    return json.loads(moteur.decoder(r.stdout) or "{}").get("streams", [])


def sans_rien_filmer():
    print("Sans rien filmer")
    t = moteur.taille_cible
    ok(t(1366, 768, "4k") == (3840, 2160), "1366 x 768 en 4K donne 3840 x 2160", t(1366, 768, "4k"))
    ok(t(1366, 768, "1080p") == (1920, 1080), "1366 x 768 en 1080p donne 1920 x 1080")
    ok(t(1920, 1080, "ecran") == (1920, 1080), "taille de l'écran inchangée")
    ok(t(1365, 767, "ecran") == (1364, 766), "pixel impair retiré comme à la capture", t(1365, 767, "ecran"))
    ok(t(1920, 1200, "4k") == (3456, 2160), "écran 16/10 en 4K garde ses proportions", t(1920, 1200, "4k"))
    ok(t(1080, 1920, "4k") == (2160, 3840), "écran en portrait en 4K", t(1080, 1920, "4k"))
    ok(t(3840, 2160, "1080p") == (1920, 1080), "écran 4K réduit en 1080p")

    cmd = moteur.commande_capture("ffmpeg", "x.mkv", 30, "h264_qsv", 0, "Mixage stéréo (Realtek)", "Micro (Realtek)")
    texte = " ".join(cmd)
    ok("gfxcapture=monitor_idx=0:capture_cursor=1" in texte, "capture par Windows.Graphics.Capture (curseur juste)")
    ok("fps=30" in texte, "cadence fixe même quand l'écran ne bouge pas")
    ok("ddagrab=output_idx=1" in " ".join(moteur.commande_capture("ffmpeg", "x.mkv", 30, "h264_qsv", 1,
                                                                    source="ddagrab")), "secours ddagrab")
    ok("-cluster_time_limit" in cmd and "-flush_packets" in cmd, "écrit sur le disque chaque seconde")
    ok("amix=inputs=2" in texte and "audio=Mixage stéréo (Realtek)" in cmd, "son du PC et micro mélangés")
    ok("-audio_buffer_size" in cmd, "tampon du son réduit (sinon le son arrive en retard)")
    cmd = moteur.commande_capture("ffmpeg", "x.mkv", 60, "libx264")
    ok("[a]" not in " ".join(cmd) and "-c:a" not in cmd, "sans son : aucune piste son")
    ok(cmd[cmd.index("-g") + 1] == "120", "une image clé toutes les deux secondes")
    for nom in moteur.ORDRE_ENCODEURS:
        ok(bool(moteur.options_encodeur(nom)) and bool(moteur.options_encodeur(nom, 20)), f"réglages de {nom}")

    exemple = ('[in#0] "HP HD Webcam" (video)\n[in#0] "Microphone (2- Realtek High Definition Audio)" (audio)\n'
               '[in#0] "Microphone (Voice Changer Virtual Audio Device (WDM))" (audio)\n'
               '[in#0] "Mixage stéréo (2- Realtek High Definition Audio)" (audio)\n')
    import re
    noms = re.findall(r'"([^"]+)" \(audio\)', exemple)
    son_pc = next((n for n in noms if any(m in n.lower() for m in moteur.NOMS_SON_PC)), None)
    ok(son_pc and son_pc.startswith("Mixage stéréo"), "« Mixage stéréo » reconnu comme son du PC")

    d = tempfile.mkdtemp(prefix="nebula-rec-qc-")
    try:
        ico = fabriquer_icone(os.path.join(d, "i.ico"))
        with open(ico, "rb") as f:
            tete = f.read(6)
        ok(struct.unpack("<HHH", tete) == (0, 1, 6), "icône : six tailles", os.path.getsize(ico))
        open(os.path.join(d, "Écran.mp4"), "w").close()
        ok(os.path.basename(moteur.nom_libre(d, "Écran")) == "Écran (2).mp4", "jamais d'écrasement d'une vidéo")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ok(moteur.fmt_duree(3725) == "1:02:05" and moteur.fmt_duree(65) == "01:05", "chrono lisible")
    ok(moteur.fmt_taille(5 * 1024 ** 2) == "5,0 Mo", "tailles à la française")
    ok(moteur.nom_de_base(cle="4k").endswith("(4K)"), "le nom dit la qualité")


SOURCE = "gfxcapture"


def filmer(ffmpeg, d, nom, secondes, encodeur, son_pc=None, micro=None, ips=30, pause=0.0):
    enr = moteur.Enregistrement(ffmpeg, os.path.join(d, nom), ips, encodeur, 0, son_pc, micro, SOURCE)
    enr.demarrer()
    t0 = time.monotonic()
    while not enr.demarre and time.monotonic() - t0 < 60 and not enr.mort_seul():
        time.sleep(0.2)
    time.sleep(secondes)
    if pause:
        enr.pause()
        time.sleep(pause)
        enr.reprendre()
        t0 = time.monotonic()
        while not enr.demarre and time.monotonic() - t0 < 60 and not enr.mort_seul():
            time.sleep(0.2)
        time.sleep(secondes)
    return enr


def avec_de_vraies_captures():
    print("\nDe vraies captures de l'écran")
    moteur.rendre_net()
    ffmpeg, ffprobe = moteur.trouver("ffmpeg"), moteur.trouver("ffprobe")
    if not ok(bool(ffmpeg and ffprobe), "ffmpeg et ffprobe trouvés", ffmpeg):
        return
    l_ecran, h_ecran, _ = next((e for e in moteur.ecrans() if e[2]), moteur.ecrans()[0])
    global SOURCE
    SOURCE = moteur.choisir_source(ffmpeg)
    ok(SOURCE == "gfxcapture", "capture Windows.Graphics.Capture disponible", SOURCE)
    t0 = time.monotonic()
    enc = moteur.choisir_encodeur(ffmpeg)
    ok(enc != "libx264", f"encodeur matériel choisi : {enc}", f"{time.monotonic() - t0:.0f} s")
    son_pc, micros = moteur.peripheriques_audio(ffmpeg)
    print(f"     son du PC : {son_pc} · micros : {micros}")

    d = tempfile.mkdtemp(prefix="nebula-rec-qc-")
    try:
        # 1. Sans son
        enr = filmer(ffmpeg, d, "a", 4, enc)
        morceaux = enr.arreter()
        ok(len(morceaux) == 1, "un morceau .mkv écrit", enr.erreur())
        if morceaux:
            sortie = moteur.recoller(ffmpeg, morceaux, os.path.join(d, "a.mp4"))
            l, h, duree, images, son = moteur.sonder(ffprobe, sortie)
            ok((l, h) == (l_ecran // 2 * 2, h_ecran // 2 * 2), "taille réelle de l'écran", f"{l} x {h}")
            ok(3.0 <= duree <= 6.0, "durée cohérente", f"{duree:.1f} s")
            ok(images >= 0.85 * 30 * duree, "images régulières", f"{images} images, {images / max(duree, .1):.1f} i/s")
            ok(not son, "pas de piste son demandée, pas de piste son")
            # 5. Finition 1080p
            t1 = time.monotonic()
            vu = []
            fini = moteur.agrandir(ffmpeg, sortie, os.path.join(d, "a1080.mp4"), 1920, 1080, enc, duree,
                                   progres=vu.append)
            l2, h2, d2, _i, _s = moteur.sonder(ffprobe, os.path.join(d, "a1080.mp4"))
            ok(fini and (l2, h2) == (1920, 1080), "finition 1080p", f"{time.monotonic() - t1:.0f} s")
            ok(vu and max(vu) > 0.5, "la barre de progression avance", f"{max(vu or [0]):.2f}")
            ok(abs(d2 - duree) < 0.3, "même durée après finition", f"{d2:.2f} contre {duree:.2f}")
            # Annulation de la finition
            fini = moteur.agrandir(ffmpeg, sortie, os.path.join(d, "annule.mp4"), 3840, 2160, enc, duree,
                                   annule=lambda: True)
            ok(fini is False and not os.path.exists(os.path.join(d, "annule.mp4")), "finition annulable")

        # 2. Avec le son du PC et le micro
        if son_pc or micros:
            enr = filmer(ffmpeg, d, "b", 4, enc, son_pc, micros[0] if micros else None)
            morceaux = enr.arreter()
            if ok(bool(morceaux), "capture avec le son", enr.erreur()):
                sortie = moteur.recoller(ffmpeg, morceaux, os.path.join(d, "b.mp4"))
                s = {f["codec_type"]: f for f in flux(ffprobe, sortie)}
                ok("audio" in s and s["audio"].get("codec_name") == "aac", "piste son AAC présente")
                if "audio" in s and "video" in s:
                    ecart = abs(float(s["audio"]["duration"]) - float(s["video"]["duration"]))
                    ok(ecart < 0.5, "son et image de même durée", f"écart {ecart:.2f} s")

        # 3. Pause puis reprise
        enr = filmer(ffmpeg, d, "c", 2.5, enc, pause=2.0)
        morceaux = enr.arreter()
        ok(len(morceaux) == 2, "deux morceaux après une pause", len(morceaux))
        if len(morceaux) == 2:
            sortie = moteur.recoller(ffmpeg, morceaux, os.path.join(d, "c.mp4"))
            _l, _h, duree, _i, _s = moteur.sonder(ffprobe, sortie)
            # Chaque morceau ajoute ~1 s (démarrage + arrêt de ffmpeg) ; avec la pause de 2 s on dépasserait 9 s.
            ok(4.5 <= duree <= 8.0, "la pause n'est pas dans la vidéo", f"{duree:.1f} s pour 2 x 2,5 s filmées")
            ok(abs(enr.duree() - duree) < 1.0, "le chrono dit la vérité", f"{enr.duree():.1f} contre {duree:.1f}")

        # 4. Coupure brutale (PC qui s'éteint, logiciel tué) : le .mkv reste lisible
        enr = filmer(ffmpeg, d, "d", 3, enc)
        enr.proc.kill()
        enr.proc.wait()
        ok(enr.mort_seul(), "une coupure est reconnue comme telle")
        perdus = moteur.sessions_interrompues(d)
        ok(os.path.join(d, "d") in perdus, "la session coupée est retrouvée au redémarrage")
        try:
            sortie = moteur.recoller(ffmpeg, moteur.morceaux_valides(enr.morceaux), os.path.join(d, "d.mp4"))
            _l, _h, duree, _i, _s = moteur.sonder(ffprobe, sortie)
            ok(duree > 1.5, "la vidéo coupée est récupérée", f"{duree:.1f} s")
        except RuntimeError as e:
            ok(False, "la vidéo coupée est récupérée", str(e)[:120])

        # 6. La fenêtre de NEBULA REC n'apparaît pas dans la vidéo
        fenetre_invisible(ffmpeg, d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def fenetre_invisible(ffmpeg, d):
    import ctypes
    import tkinter as tk
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]

    def pixel_au_centre(exclure):
        r = tk.Tk()
        r.overrideredirect(True)
        r.geometry("300x300+80+80")
        r.configure(bg="#ff00ff")
        r.attributes("-topmost", True)
        r.update()
        hwnd = user32.GetAncestor(r.winfo_id(), 2)
        aff = bool(user32.SetWindowDisplayAffinity(hwnd, 0x11 if exclure else 0))
        r.update()
        time.sleep(0.6)
        img = os.path.join(d, "p.rgb")
        moteur.lancer([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-filter_complex",
                       moteur.source_video(SOURCE, 0, 10).replace(",format=nv12", "") + ",crop=1:1:230:230,format=rgb24",
                       "-frames:v", "3", "-f", "rawvideo", img], timeout=120)
        r.destroy()
        with open(img, "rb") as f:
            octets = f.read()
        return aff, tuple(octets[-3:]) if len(octets) >= 3 else None

    _aff, temoin = pixel_au_centre(False)
    ok(temoin == (255, 0, 255), "témoin : une fenêtre normale est bien filmée", temoin)
    aff, cache = pixel_au_centre(True)
    ok(aff and cache is not None and cache != (255, 0, 255), "la fenêtre de NEBULA REC n'est pas filmée", cache)


if __name__ == "__main__":
    sans_rien_filmer()
    if "--reel" in sys.argv:
        avec_de_vraies_captures()
    print(f"\n{len(VERTS)} verts, {len(ROUGES)} rouges")
    sys.exit(1 if ROUGES else 0)
