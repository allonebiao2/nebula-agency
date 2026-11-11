# -*- coding: utf-8 -*-
"""NEBULA REC · le moteur : capture l'écran avec ffmpeg, sans interface.

Le principe, le même que les enregistreurs du commerce (sans leur code) :
- l'image vient de Windows.Graphics.Capture, par le filtre `gfxcapture` de ffmpeg : c'est Windows qui y
  dessine le curseur. ⚠️ Le filtre `ddagrab` (Duplication du bureau) dessinait CHAQUE curseur dans un carré
  blanc (main, texte, flèche : planche du 2026-11-11) ; il ne sert plus qu'en secours sur un vieux Windows ;
- elle est codée en H.264 par la puce vidéo (NVIDIA, Intel Quick Sync, AMD), sinon par le processeur ;
- le son vient de DirectShow : « Mixage stéréo » pour le son du PC, le micro pour la voix ;
- on enregistre TOUJOURS à la taille réelle de l'écran, en morceaux .mkv, lisibles même après une coupure
  de courant (un .mp4 interrompu est illisible) ;
- à l'arrêt, les morceaux sont recollés en .mp4, puis agrandis en 1080p ou en 4K si on l'a demandé.

Pourquoi agrandir APRÈS : mesuré le 2026-11-11 sur le PC de Cotonou (Intel HD 5500), la 4K agrandie en
direct ne tient que 24 images/s sur 30, donc la vidéo saccade. Agrandie après coup, elle ne perd rien.
"""

import ctypes
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import threading
import time
from ctypes import wintypes

SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# Taille demandée → boîte où la vidéo doit tenir (en paysage ; retournée pour un écran en portrait).
BOITES = {"ecran": None, "1080p": (1920, 1080), "4k": (3840, 2160)}
LIBELLES = {"ecran": "", "1080p": " (1080p)", "4k": " (4K)"}

# Le son du PC passe par un périphérique d'enregistrement « bouclé » sur les haut-parleurs.
NOMS_SON_PC = ("mixage stéréo", "mixage stereo", "stereo mix", "what u hear", "wave out", "loopback",
               "ce que vous entendez")

ORDRE_ENCODEURS = ("h264_nvenc", "h264_qsv", "h264_amf", "h264_mf", "libx264")
SOURCES = ("gfxcapture", "ddagrab")


# ───────────────────────────── outils ─────────────────────────────

def discret():
    """Lancer ffmpeg sans le curseur « démarrage » (flèche + sablier) : sinon il apparaît au début de la vidéo."""
    si = subprocess.STARTUPINFO()
    si.dwFlags |= 0x80  # STARTF_FORCEOFFFEEDBACK
    return si

def trouver(nom):
    """Chemin de ffmpeg ou ffprobe : le PATH, puis les emplacements d'installation habituels."""
    chemin = shutil.which(nom)
    if chemin:
        return chemin
    for base in (os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
                 r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"):
        candidat = os.path.join(base, nom + ".exe")
        if os.path.exists(candidat):
            return candidat
    return None


def lancer(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, timeout=timeout, creationflags=SANS_FENETRE,
                          startupinfo=discret())


def decoder(octets):
    try:
        return octets.decode("utf-8")
    except UnicodeDecodeError:
        return octets.decode("cp1252", "replace")


def pair(n):
    return max(2, int(round(n / 2.0)) * 2)


def taille_cible(largeur, hauteur, cle):
    """Taille finale : celle de l'écran, ou la boîte 1080p / 4K en gardant les proportions."""
    boite = BOITES.get(cle)
    if not boite:
        # Même règle que la capture (crop=trunc(iw/2)*2) : on retire le pixel impair, on n'en ajoute pas.
        return int(largeur) // 2 * 2, int(hauteur) // 2 * 2
    bl, bh = boite if largeur >= hauteur else (boite[1], boite[0])
    # Un écran de portable (1366 x 768) n'est pas exactement en 16/9 : à 1 % près, on prend la boîte.
    if abs((largeur / hauteur) / (bl / bh) - 1) < 0.01:
        return bl, bh
    k = min(bl / largeur, bh / hauteur)
    return pair(largeur * k), pair(hauteur * k)


def fmt_duree(s):
    s = int(round(s))
    h, reste = divmod(s, 3600)
    m, s = divmod(reste, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def fmt_taille(octets):
    if octets >= 1024 ** 3:
        return f"{octets / 1024 ** 3:.2f} Go".replace(".", ",")
    return f"{octets / 1024 ** 2:.1f} Mo".replace(".", ",")


# ───────────────────────────── l'écran ─────────────────────────────

def rendre_net():
    """Pixels réels (sinon Windows ment sur la taille quand l'affichage est agrandi à 125 %)."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:  # noqa: BLE001
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:  # noqa: BLE001
            pass


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]


def ecrans():
    """[(largeur, hauteur, principal)] de chaque écran branché, en pixels réels."""
    trouves = []
    user32 = ctypes.windll.user32
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HMONITOR, wintypes.HDC,
                               ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)

    def rappel(hmon, _hdc, _rect, _lp):
        info = _MONITORINFO()
        info.cbSize = ctypes.sizeof(info)
        user32.GetMonitorInfoW(hmon, ctypes.byref(info))
        r = info.rcMonitor
        trouves.append((r.right - r.left, r.bottom - r.top, bool(info.dwFlags & 1)))
        return 1

    user32.EnumDisplayMonitors(None, None, proto(rappel), 0)
    return trouves or [(1920, 1080, True)]


# ───────────────────────────── le son ─────────────────────────────

def peripheriques_audio(ffmpeg):
    """(son_du_pc, micros) : noms DirectShow. son_du_pc vaut None si « Mixage stéréo » est absent."""
    try:
        r = lancer([ffmpeg, "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"], timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None, []
    noms = re.findall(r'"([^"]+)" \(audio\)', decoder(r.stderr))
    son_pc = next((n for n in noms if any(m in n.lower() for m in NOMS_SON_PC)), None)
    micros = [n for n in noms if n != son_pc]
    # Les vrais micros d'abord, les micros virtuels (changeurs de voix…) ensuite.
    micros.sort(key=lambda n: ("virtual" in n.lower() or "virtuel" in n.lower(), "micro" not in n.lower()))
    return son_pc, micros


# ───────────────────────────── le codage ─────────────────────────────

def options_encodeur(nom, q=23):
    """Réglages par encodeur. q : plus bas = plus beau et plus lourd."""
    return {
        "h264_nvenc": ["-preset", "p4", "-rc", "vbr", "-cq", str(q), "-b:v", "0"],
        "h264_qsv": ["-preset", "veryfast", "-global_quality", str(q)],
        "h264_amf": ["-quality", "speed", "-rc", "cqp", "-qp_i", str(q), "-qp_p", str(q + 2)],
        "h264_mf": ["-hw_encoding", "1", "-b:v", "12M" if q < 23 else "8M"],
        "libx264": ["-preset", "ultrafast" if q >= 23 else "veryfast", "-crf", str(q)],
    }[nom]


def tester_encodeur(ffmpeg, nom):
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=320x180:r=30",
           "-frames:v", "8", "-vf", "format=nv12", "-c:v", nom, *options_encodeur(nom), "-f", "null", "-"]
    try:
        return lancer(cmd, timeout=90).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def choisir_encodeur(ffmpeg):
    """Le premier encodeur qui marche vraiment sur cette machine (une carte absente échoue ici)."""
    for nom in ORDRE_ENCODEURS:
        if tester_encodeur(ffmpeg, nom):
            return nom
    return "libx264"


# ───────────────────────────── la capture ─────────────────────────────

def source_video(source, ecran, ips):
    """L'image de l'écran, en mémoire, cadence fixe, dimensions paires, prête pour l'encodeur (nv12)."""
    if source == "gfxcapture":
        src = f"gfxcapture=monitor_idx={ecran}:capture_cursor=1:max_framerate={ips}"
    else:
        src = f"ddagrab=output_idx={ecran}:framerate={ips}:draw_mouse=1"
    # fps= : Windows n'envoie une image que quand l'écran change ; on répète la dernière pour une cadence fixe.
    return f"{src},hwdownload,format=bgra,fps={ips},crop=trunc(iw/2)*2:trunc(ih/2)*2,format=nv12"


def tester_source(ffmpeg, source):
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-filter_complex", source_video(source, 0, 10),
           "-frames:v", "2", "-f", "null", "-"]
    try:
        return lancer(cmd, timeout=90).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def choisir_source(ffmpeg):
    """gfxcapture (Windows 10 1903 et plus), sinon ddagrab."""
    return next((s for s in SOURCES if tester_source(ffmpeg, s)), "ddagrab")


def commande_capture(ffmpeg, sortie, ips, encodeur, ecran=0, son_pc=None, micro=None, source="gfxcapture"):
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1",
           "-stats_period", "0.25", "-y"]
    sons = [n for n in (son_pc, micro) if n]
    for nom in sons:
        # Tampon de 50 ms : par défaut DirectShow garde 500 ms, et le son arrive en retard sur l'image.
        cmd += ["-f", "dshow", "-audio_buffer_size", "50", "-thread_queue_size", "4096", "-i", f"audio={nom}"]
    graphe = source_video(source, ecran, ips) + "[v]"
    if len(sons) == 2:
        graphe += ";[0:a][1:a]amix=inputs=2:duration=longest:normalize=0,aresample=async=1000[a]"
    elif sons:
        graphe += ";[0:a]aresample=async=1000[a]"
    cmd += ["-filter_complex", graphe, "-map", "[v]"]
    if sons:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
    cmd += ["-c:v", encodeur, *options_encodeur(encodeur), "-g", str(int(ips) * 2)]
    # Un bloc .mkv par seconde, écrit tout de suite : si le PC s'éteint, on perd au plus une seconde
    # (par défaut ffmpeg garde 5 secondes en mémoire, et un arrêt brutal laissait un fichier vide).
    cmd += ["-cluster_time_limit", "1000", "-flush_packets", "1", sortie]
    return cmd


class Enregistrement:
    """Une session : un ou plusieurs morceaux (un par reprise après pause), dans un dossier de travail."""

    def __init__(self, ffmpeg, dossier_travail, ips, encodeur, ecran=0, son_pc=None, micro=None,
                 source="gfxcapture"):
        self.ffmpeg, self.dossier, self.source = ffmpeg, dossier_travail, source
        self.ips, self.encodeur, self.ecran = int(ips), encodeur, ecran
        self.son_pc, self.micro = son_pc, micro
        self.morceaux, self.images_morceaux = [], []
        self.proc = None
        self.debut = None          # instant de la première image du morceau en cours
        self.cumul = 0.0           # secondes des morceaux terminés
        self.octets_avant = 0      # taille des morceaux terminés
        self.octets = 0            # taille du morceau en cours
        self.arret_voulu = False
        os.makedirs(self.dossier, exist_ok=True)
        self.journal = os.path.join(self.dossier, "journal.txt")
        with open(os.path.join(self.dossier, "session.json"), "w", encoding="utf-8") as f:
            json.dump({"ips": self.ips, "debut": dt.datetime.now().isoformat(timespec="seconds")}, f)

    # — états —
    @property
    def en_cours(self):
        return self.proc is not None and self.proc.poll() is None

    @property
    def demarre(self):
        return self.debut is not None

    def duree(self):
        return self.cumul + (time.monotonic() - self.debut if self.debut and self.en_cours else 0.0)

    def taille(self):
        return self.octets_avant + self.octets

    def images(self):
        return sum(self.images_morceaux)

    # — commandes —
    def demarrer(self):
        chemin = os.path.join(self.dossier, f"morceau-{len(self.morceaux) + 1:03d}.mkv")
        cmd = commande_capture(self.ffmpeg, chemin, self.ips, self.encodeur, self.ecran, self.son_pc, self.micro,
                               self.source)
        self._journal = open(self.journal, "ab")
        self._journal.write(f"\n=== {dt.datetime.now():%H:%M:%S} {os.path.basename(chemin)}\n".encode())
        self._journal.flush()
        self.arret_voulu, self.debut, self.octets = False, None, 0
        self.morceaux.append(chemin)
        self.images_morceaux.append(0)
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._journal,
                                     creationflags=SANS_FENETRE, startupinfo=discret())
        threading.Thread(target=self._lire_progres, args=(self.proc, len(self.morceaux) - 1), daemon=True).start()

    def _lire_progres(self, proc, i):
        for ligne in proc.stdout:
            cle, _, val = decoder(ligne).strip().partition("=")
            if cle == "frame" and val.isdigit():
                self.images_morceaux[i] = int(val)
                # « is proc » : une ligne en retard d'un morceau fini ne doit pas relancer le chrono.
                if int(val) > 0 and self.debut is None and self.proc is proc and not self.arret_voulu:
                    self.debut = time.monotonic()
            elif cle == "total_size" and val.isdigit() and self.proc is proc:
                self.octets = int(val)

    def _couper(self):
        """Arrêt propre : « q » à ffmpeg, qui ferme le fichier. Tué seulement s'il ne répond plus."""
        p = self.proc
        if p is None:
            return
        self.arret_voulu = True
        if p.poll() is None:
            try:
                p.stdin.write(b"q")
                p.stdin.flush()
                p.stdin.close()
            except OSError:
                pass
            try:
                p.wait(timeout=20)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        if self.debut is not None:
            self.cumul += time.monotonic() - self.debut
        self.debut = None
        if os.path.exists(self.morceaux[-1]):
            self.octets_avant += os.path.getsize(self.morceaux[-1])
        self.octets = 0
        self.proc = None
        try:
            self._journal.close()
        except Exception:  # noqa: BLE001
            pass

    def pause(self):
        self._couper()

    def reprendre(self):
        self.demarrer()

    def arreter(self):
        self._couper()
        return morceaux_valides(self.morceaux)

    def mort_seul(self):
        """Vrai si ffmpeg s'est arrêté sans qu'on le lui demande (écran verrouillé, son débranché…)."""
        return self.proc is not None and self.proc.poll() is not None and not self.arret_voulu

    def erreur(self):
        return fin_du_journal(self.journal)


def fin_du_journal(chemin, lignes=4):
    try:
        with open(chemin, "rb") as f:
            texte = decoder(f.read()[-4000:])
    except OSError:
        return ""
    utiles = [l.strip() for l in texte.splitlines() if l.strip() and not l.startswith("===")]
    return "\n".join(utiles[-lignes:])


def morceaux_valides(morceaux):
    return [m for m in morceaux if os.path.exists(m) and os.path.getsize(m) > 2048]


# ───────────────────────────── l'assemblage ─────────────────────────────

def sonder(ffprobe, chemin):
    """(largeur, hauteur, durée, images, a_du_son) d'une vidéo."""
    r = lancer([ffprobe, "-v", "error", "-show_entries",
                "stream=codec_type,width,height,nb_frames:format=duration", "-of", "json", chemin], timeout=120)
    infos = json.loads(decoder(r.stdout) or "{}")
    video = next((s for s in infos.get("streams", []) if s.get("codec_type") == "video"), {})
    son = any(s.get("codec_type") == "audio" for s in infos.get("streams", []))
    duree = float(infos.get("format", {}).get("duration") or 0)
    nb = video.get("nb_frames")
    return int(video.get("width") or 0), int(video.get("height") or 0), duree, int(nb) if str(nb).isdigit() else 0, son


def nom_libre(dossier, base, ext=".mp4"):
    chemin = os.path.join(dossier, base + ext)
    n = 2
    while os.path.exists(chemin):
        chemin = os.path.join(dossier, f"{base} ({n}){ext}")
        n += 1
    return chemin


def nom_de_base(quand=None, cle="ecran"):
    quand = quand or dt.datetime.now()
    return f"Écran {quand:%Y-%m-%d} à {quand:%Hh%M}{LIBELLES.get(cle, '')}"


def recoller(ffmpeg, morceaux, sortie):
    """Morceaux .mkv → un seul .mp4, sans recoder (quelques secondes)."""
    morceaux = morceaux_valides(morceaux)
    if not morceaux:
        raise RuntimeError("Aucune image n'a été enregistrée.")
    if len(morceaux) == 1:
        entree = ["-i", morceaux[0]]
    else:
        liste = os.path.join(os.path.dirname(morceaux[0]), "liste.txt")
        with open(liste, "w", encoding="utf-8") as f:
            for m in morceaux:
                f.write("file '" + m.replace("\\", "/").replace("'", "'\\''") + "'\n")
        entree = ["-f", "concat", "-safe", "0", "-i", liste]
    r = lancer([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *entree, "-c", "copy",
                "-movflags", "+faststart", sortie], timeout=3600)
    if r.returncode != 0 or not os.path.exists(sortie):
        raise RuntimeError("Recollage impossible : " + decoder(r.stderr)[-300:])
    return sortie


def agrandir(ffmpeg, entree, sortie, largeur, hauteur, encodeur, duree, progres=None, annule=None):
    """Recode la vidéo à la taille finale (lanczos : le plus net pour du texte d'écran). Faux si annulé."""
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1", "-y", "-i", entree,
           "-map", "0:v:0", "-map", "0:a?", "-vf", f"scale={largeur}:{hauteur}:flags=lanczos,format=nv12",
           "-c:v", encodeur, *options_encodeur(encodeur, 20), "-c:a", "copy", "-movflags", "+faststart", sortie]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=SANS_FENETRE,
                         startupinfo=discret())
    erreurs = []
    threading.Thread(target=lambda: erreurs.append(p.stderr.read()), daemon=True).start()
    for ligne in p.stdout:
        cle, _, val = decoder(ligne).strip().partition("=")
        if cle == "out_time_us" and val.lstrip("-").isdigit() and progres and duree > 0:
            progres(max(0.0, min(1.0, int(val) / 1e6 / duree)))
        if annule and annule():
            p.kill()
            p.wait()
            if os.path.exists(sortie):
                os.remove(sortie)
            return False
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("Finition impossible : " + decoder(b"".join(e or b"" for e in erreurs))[-300:])
    return True


def sessions_interrompues(racine):
    """Dossiers de travail laissés par une coupure (le logiciel ou le PC s'est arrêté pendant l'enregistrement)."""
    if not os.path.isdir(racine):
        return []
    trouves = []
    for nom in sorted(os.listdir(racine)):
        d = os.path.join(racine, nom)
        if os.path.isdir(d) and morceaux_valides([os.path.join(d, f) for f in os.listdir(d) if f.endswith(".mkv")]):
            trouves.append(d)
    return trouves
