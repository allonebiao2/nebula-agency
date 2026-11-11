# -*- coding: utf-8 -*-
"""NEBULA REC · enregistreur d'écran, l'interface. Lancer : pythonw nebula_rec.pyw

Tout le travail vidéo est dans moteur.py. Ici : la fenêtre, les raccourcis clavier, la récupération
d'un enregistrement interrompu. Aucune dépendance hors Python et ffmpeg.
"""

import ctypes
import datetime as dt
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from ctypes import wintypes
from tkinter import filedialog, messagebox, ttk

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import moteur  # noqa: E402
from icone import fabriquer_icone  # noqa: E402

NOM = "NEBULA REC"
DONNEES = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), NOM)
TRAVAIL = os.path.join(DONNEES, "en-cours")
REGLAGES = os.path.join(DONNEES, "reglages.json")
ICONE = os.path.join(DONNEES, "nebula-rec.ico")

C = dict(fond="#111114", carte="#1c1c22", survol="#26262e", ligne="#2c2c34", texte="#f2efe8",
         doux="#9b978f", rouge="#ff3b3b", rouge2="#e23131", vert="#3ecf8e", ambre="#f5b544")
POLICE = "Segoe UI"
NOMS_ENCODEURS = {"h264_nvenc": "carte NVIDIA", "h264_qsv": "puce Intel Quick Sync", "h264_amf": "carte AMD",
                  "h264_mf": "Windows Media Foundation", "libx264": "processeur"}
QUALITES = {"ecran": "taille de l'écran", "1080p": "1080p", "4k": "4K"}

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
kernel32.CreateMutexW.restype = wintypes.HANDLE


# ───────────────────────────── petits outils ─────────────────────────────

def lire_reglages():
    try:
        with open(REGLAGES, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ecrire_reglages(reglages):
    os.makedirs(DONNEES, exist_ok=True)
    tmp = REGLAGES + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reglages, f, ensure_ascii=False, indent=1)
    os.replace(tmp, REGLAGES)


def dossier_videos():
    """Le dossier Vidéos de Windows (il peut avoir été déplacé, dans OneDrive par exemple)."""
    try:
        class GUID(ctypes.Structure):
            _fields_ = [("a", ctypes.c_ulong), ("b", ctypes.c_ushort), ("c", ctypes.c_ushort),
                        ("d", ctypes.c_ubyte * 8)]
        g = GUID(0x18989B1D, 0x99B5, 0x455B, (ctypes.c_ubyte * 8)(0x84, 0x1C, 0xAB, 0x7C, 0x74, 0xE4, 0xDD, 0xFC))
        p = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(p)) == 0:
            chemin = p.value
            ctypes.windll.ole32.CoTaskMemFree(p)
            return os.path.join(chemin, NOM)
    except Exception:  # noqa: BLE001
        pass
    return os.path.join(os.path.expanduser("~"), "Videos", NOM)


def deja_ouvert():
    """Une seule fenêtre à la fois : sinon les raccourcis clavier se disputent."""
    global _VERROU
    _VERROU = kernel32.CreateMutexW(None, False, "Local\\NEBULA_REC_une_seule_fois")
    if kernel32.GetLastError() == 183:
        h = user32.FindWindowW(None, NOM)
        if h:
            user32.ShowWindow(h, 9)
            user32.SetForegroundWindow(h)
        return True
    return False


def eclaircir(couleur, k=0.12):
    r, g, b = (int(couleur[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(v + (255 - v) * k) for v in (r, g, b))


class Raccourcis(threading.Thread):
    """Ctrl + Alt + R (démarrer / arrêter) et Ctrl + Alt + P (pause), partout dans Windows."""

    def __init__(self, file):
        super().__init__(daemon=True)
        self.file, self.ok = file, None

    def run(self):
        mods = 0x0001 | 0x0002 | 0x4000  # Alt + Ctrl, sans répétition quand on garde la touche
        r = user32.RegisterHotKey(None, 1, mods, ord("R"))
        p = user32.RegisterHotKey(None, 2, mods, ord("P"))
        self.ok = bool(r and p)
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == 0x0312:  # WM_HOTKEY
                self.file.put("basculer" if msg.wParam == 1 else "pause")


def bouton(parent, texte, rappel, fond=None, encre=None, taille=10):
    fond = fond or C["carte"]
    b = tk.Label(parent, text=texte, font=(POLICE, taille, "bold"), bg=fond, fg=encre or C["texte"],
                 padx=16, pady=9, cursor="hand2")
    b.bind("<Button-1>", lambda _e: rappel())
    b.bind("<Enter>", lambda _e: b.configure(bg=eclaircir(b.cget("bg"), 0.10)))
    b.bind("<Leave>", lambda _e: b.configure(bg=b.fond))
    b.fond = fond
    return b


class Choix(tk.Frame):
    """Boutons côte à côte, un seul allumé."""

    def __init__(self, parent, variable, options, rappel=None):
        super().__init__(parent, bg=C["fond"])
        self.var, self.rappel, self.boutons = variable, rappel, {}
        self.remplir(options)

    def remplir(self, options):
        for b in self.boutons.values():
            b.destroy()
        self.boutons = {}
        for i, (valeur, texte) in enumerate(options):
            b = tk.Label(self, text=texte, font=(POLICE, 10, "bold"), padx=14, pady=7, cursor="hand2")
            b.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0))
            b.bind("<Button-1>", lambda _e, v=valeur: self.choisir(v))
            self.boutons[valeur] = b
        self.peindre()

    def choisir(self, valeur):
        self.var.set(valeur)
        self.peindre()
        if self.rappel:
            self.rappel()

    def peindre(self):
        for valeur, b in self.boutons.items():
            actif = str(self.var.get()) == str(valeur)
            b.configure(bg=C["texte"] if actif else C["carte"], fg=C["fond"] if actif else C["texte"])


# ───────────────────────────── l'application ─────────────────────────────

class Appli:
    def __init__(self, racine):
        self.r = racine
        self.reg = lire_reglages()
        self.file = queue.Queue()
        self.ffmpeg, self.ffprobe = moteur.trouver("ffmpeg"), moteur.trouver("ffprobe")
        meme_ffmpeg = self.reg.get("ffmpeg") == self.ffmpeg
        self.encodeur = self.reg.get("encodeur") if meme_ffmpeg else None
        self.source = self.reg.get("source") if meme_ffmpeg else None
        self.son_pc, self.micros = None, []
        self.liste_ecrans = moteur.ecrans()
        self.etat = "preparation"
        self.enr = None
        self.quand, self.cle = None, "ecran"
        self.progres, self.message_fin, self.resultat = 0.0, "", None
        self.annuler_finition = False
        self.fermer_apres = False
        self.note = ""
        self.base_details = ""
        self.demarrer_des_que_pret = False
        self.exclu = False
        self.clignote = 0

        self.v_qualite = tk.StringVar(value=self.reg.get("qualite", "ecran"))
        self.v_ips = tk.StringVar(value=str(self.reg.get("ips", 30)))
        self.v_son_pc = tk.BooleanVar(value=self.reg.get("son_pc", True))
        self.v_micro = tk.BooleanVar(value=self.reg.get("micro", False))
        self.v_micro_nom = tk.StringVar(value=self.reg.get("micro_nom", ""))
        self.v_ecran = tk.StringVar(value=str(self.reg.get("ecran", 0)))
        if int(self.v_ecran.get()) >= len(self.liste_ecrans):
            self.v_ecran.set("0")
        self.dossier = self.reg.get("dossier") or dossier_videos()

        self.raccourcis = Raccourcis(self.file)
        self.raccourcis.start()
        self.construire()
        racine.protocol("WM_DELETE_WINDOW", self.fermer)
        racine.after(250, self.apres_affichage)
        threading.Thread(target=self.preparer, daemon=True).start()
        self.boucle()

    # — construction —
    def construire(self):
        r = self.r
        r.title(NOM)
        r.configure(bg=C["fond"])
        r.resizable(False, False)
        style = ttk.Style(r)
        style.theme_use("clam")
        style.configure("Rec.Horizontal.TProgressbar", troughcolor=C["carte"], background=C["rouge"],
                        bordercolor=C["carte"], lightcolor=C["rouge"], darkcolor=C["rouge"], thickness=10)
        style.configure("TCombobox", fieldbackground=C["carte"], background=C["carte"], foreground=C["texte"],
                        arrowcolor=C["texte"], bordercolor=C["ligne"], lightcolor=C["carte"], darkcolor=C["carte"])
        style.map("TCombobox", fieldbackground=[("readonly", C["carte"])], foreground=[("readonly", C["texte"])],
                  selectbackground=[("readonly", C["carte"])], selectforeground=[("readonly", C["texte"])])
        r.option_add("*TCombobox*Listbox.background", C["carte"])
        r.option_add("*TCombobox*Listbox.foreground", C["texte"])
        r.option_add("*TCombobox*Listbox.selectBackground", C["survol"])

        corps = tk.Frame(r, bg=C["fond"], padx=24, pady=20)
        corps.pack(fill="both", expand=True)
        tete = tk.Frame(corps, bg=C["fond"])
        tete.pack(fill="x")
        logo = tk.Canvas(tete, width=30, height=30, bg=C["fond"], highlightthickness=0)
        logo.create_oval(3, 3, 27, 27, outline=C["texte"], width=2)
        logo.create_oval(9, 9, 21, 21, fill=C["rouge"], outline="")
        logo.pack(side="left", padx=(0, 10))
        tk.Label(tete, text=NOM, font=(POLICE, 15, "bold"), bg=C["fond"], fg=C["texte"]).pack(side="left")
        self.l_etat = tk.Label(corps, text="Préparation…", font=(POLICE, 9), bg=C["fond"], fg=C["doux"],
                               anchor="w", justify="left")
        self.l_etat.pack(fill="x", pady=(4, 14))

        self.zone = tk.Frame(corps, bg=C["fond"])
        self.zone.pack(fill="both", expand=True)
        self.p_reglages = self.panneau_reglages(self.zone)
        self.p_enr = self.panneau_enregistrement(self.zone)
        self.p_fin = self.panneau_finition(self.zone)
        self.p_pret = self.panneau_resultat(self.zone)
        self.montrer(self.p_reglages)
        self.maj_indices()
        if os.path.exists(ICONE) or self.fabriquer_icone():
            try:
                r.iconbitmap(ICONE)
            except tk.TclError:
                pass

    def fabriquer_icone(self):
        try:
            os.makedirs(DONNEES, exist_ok=True)
            fabriquer_icone(ICONE)
            return True
        except OSError:
            return False

    def titre(self, parent, texte):
        tk.Label(parent, text=texte, font=(POLICE, 8, "bold"), bg=C["fond"], fg=C["doux"]).pack(
            anchor="w", pady=(12, 6))

    def indice(self, parent):
        l = tk.Label(parent, text="", font=(POLICE, 9), bg=C["fond"], fg=C["doux"], wraplength=340,
                     justify="left", anchor="w")
        l.pack(fill="x", pady=(6, 0))
        return l

    def panneau_reglages(self, parent):
        p = tk.Frame(parent, bg=C["fond"])
        self.titre(p, "QUALITÉ DE LA VIDÉO")
        self.c_qualite = Choix(p, self.v_qualite, self.options_qualite(), self.maj_indices)
        self.c_qualite.pack(anchor="w")
        self.i_qualite = self.indice(p)

        self.titre(p, "IMAGES PAR SECONDE")
        Choix(p, self.v_ips, [("30", "30"), ("60", "60")], self.maj_indices).pack(anchor="w")
        self.i_ips = self.indice(p)

        if len(self.liste_ecrans) > 1:
            self.titre(p, "ÉCRAN")
            Choix(p, self.v_ecran, [(str(i), f"Écran {i + 1}") for i in range(len(self.liste_ecrans))],
                  self.maj_indices).pack(anchor="w")

        self.titre(p, "SON")
        opts = dict(bg=C["fond"], fg=C["texte"], selectcolor=C["carte"], activebackground=C["fond"],
                    activeforeground=C["texte"], font=(POLICE, 10), bd=0, highlightthickness=0, cursor="hand2")
        self.k_son_pc = tk.Checkbutton(p, text="Son du PC", variable=self.v_son_pc, command=self.maj_indices, **opts)
        self.k_son_pc.pack(anchor="w")
        ligne = tk.Frame(p, bg=C["fond"])
        ligne.pack(anchor="w", fill="x", pady=(4, 0))
        tk.Checkbutton(ligne, text="Micro", variable=self.v_micro, command=self.maj_indices, **opts).pack(side="left")
        self.cb_micro = ttk.Combobox(ligne, textvariable=self.v_micro_nom, state="readonly", width=34,
                                     font=(POLICE, 9))
        self.cb_micro.pack(side="left", padx=(8, 0))
        self.i_son = self.indice(p)

        self.titre(p, "DOSSIER")
        ligne = tk.Frame(p, bg=C["fond"])
        ligne.pack(fill="x")
        self.l_dossier = tk.Label(ligne, text="", font=(POLICE, 9), bg=C["fond"], fg=C["texte"], anchor="w")
        self.l_dossier.pack(side="left", fill="x", expand=True)
        bouton(ligne, "Ouvrir", self.ouvrir_dossier, taille=9).pack(side="right")
        bouton(ligne, "Changer", self.changer_dossier, taille=9).pack(side="right", padx=(0, 6))

        self.b_rec = tk.Frame(p, bg=C["rouge"], cursor="hand2")
        self.b_rec.pack(fill="x", pady=(22, 0))
        dedans = tk.Frame(self.b_rec, bg=C["rouge"], pady=12)
        dedans.pack()
        rond = tk.Canvas(dedans, width=22, height=22, bg=C["rouge"], highlightthickness=0)
        rond.create_oval(2, 2, 20, 20, fill=C["texte"], outline="")
        rond.pack(side="left", padx=(0, 10))
        self.l_rec = tk.Label(dedans, text="Enregistrer", font=(POLICE, 13, "bold"), bg=C["rouge"], fg=C["texte"])
        self.l_rec.pack(side="left")
        for w in (self.b_rec, dedans, rond, self.l_rec):
            w.bind("<Button-1>", lambda _e: self.basculer())
            w.bind("<Enter>", lambda _e: self.peindre_rec(C["rouge2"]))
            w.bind("<Leave>", lambda _e: self.peindre_rec(C["rouge"]))
        self._rec_widgets = (self.b_rec, dedans, rond, self.l_rec)
        self.l_raccourci = tk.Label(p, text="ou Ctrl + Alt + R, de n'importe où", font=(POLICE, 9),
                                    bg=C["fond"], fg=C["doux"])
        self.l_raccourci.pack(pady=(8, 0))
        self.maj_dossier()
        return p

    def peindre_rec(self, couleur):
        for w in self._rec_widgets:
            w.configure(bg=couleur)

    def panneau_enregistrement(self, parent):
        p = tk.Frame(parent, bg=C["fond"])
        ligne = tk.Frame(p, bg=C["fond"])
        ligne.pack(anchor="w", pady=(10, 0))
        self.point = tk.Canvas(ligne, width=14, height=14, bg=C["fond"], highlightthickness=0)
        self.point_id = self.point.create_oval(2, 2, 12, 12, fill=C["rouge"], outline="")
        self.point.pack(side="left", padx=(0, 8))
        self.l_mode = tk.Label(ligne, text="DÉMARRAGE…", font=(POLICE, 9, "bold"), bg=C["fond"], fg=C["texte"])
        self.l_mode.pack(side="left")
        self.l_chrono = tk.Label(p, text="00:00", font=(POLICE, 40, "bold"), bg=C["fond"], fg=C["texte"])
        self.l_chrono.pack(anchor="w", pady=(4, 0))
        self.l_details = tk.Label(p, text="", font=(POLICE, 10), bg=C["fond"], fg=C["doux"])
        self.l_details.pack(anchor="w")
        ligne = tk.Frame(p, bg=C["fond"])
        ligne.pack(fill="x", pady=(20, 0))
        self.b_pause = bouton(ligne, "Pause", self.pause_reprendre)
        self.b_pause.pack(side="left")
        bouton(ligne, "Arrêter et garder", self.basculer, fond=C["rouge"]).pack(side="left", padx=(8, 0))
        tk.Label(p, text="Ctrl + Alt + P : pause     Ctrl + Alt + R : arrêter", font=(POLICE, 9),
                 bg=C["fond"], fg=C["doux"]).pack(anchor="w", pady=(12, 0))
        self.l_exclu = tk.Label(p, text="", font=(POLICE, 9), bg=C["fond"], fg=C["doux"], wraplength=340,
                                justify="left")
        self.l_exclu.pack(anchor="w", pady=(4, 0))
        return p

    def panneau_finition(self, parent):
        p = tk.Frame(parent, bg=C["fond"])
        self.l_fin = tk.Label(p, text="", font=(POLICE, 13, "bold"), bg=C["fond"], fg=C["texte"], wraplength=340,
                              justify="left")
        self.l_fin.pack(anchor="w", pady=(16, 10))
        self.barre = ttk.Progressbar(p, style="Rec.Horizontal.TProgressbar", maximum=1000, length=340)
        self.barre.pack(anchor="w")
        self.l_pct = tk.Label(p, text="", font=(POLICE, 10), bg=C["fond"], fg=C["doux"])
        self.l_pct.pack(anchor="w", pady=(6, 0))
        self.b_annuler = bouton(p, "Annuler et garder la taille de l'écran", self.annuler, taille=9)
        self.b_annuler.pack(anchor="w", pady=(18, 0))
        return p

    def panneau_resultat(self, parent):
        p = tk.Frame(parent, bg=C["fond"])
        self.l_res_titre = tk.Label(p, text="", font=(POLICE, 14, "bold"), bg=C["fond"], fg=C["vert"])
        self.l_res_titre.pack(anchor="w", pady=(10, 4))
        self.l_res_nom = tk.Label(p, text="", font=(POLICE, 10, "bold"), bg=C["fond"], fg=C["texte"],
                                  wraplength=340, justify="left")
        self.l_res_nom.pack(anchor="w")
        self.l_res_details = tk.Label(p, text="", font=(POLICE, 10), bg=C["fond"], fg=C["doux"], wraplength=340,
                                      justify="left")
        self.l_res_details.pack(anchor="w", pady=(2, 0))
        self.l_res_note = tk.Label(p, text="", font=(POLICE, 9), bg=C["fond"], fg=C["ambre"], wraplength=340,
                                   justify="left")
        self.l_res_note.pack(anchor="w", pady=(8, 0))
        ligne = tk.Frame(p, bg=C["fond"])
        ligne.pack(fill="x", pady=(18, 0))
        self.b_voir = bouton(ligne, "Ouvrir la vidéo", self.ouvrir_video, fond=C["texte"], encre=C["fond"])
        self.b_voir.pack(side="left", padx=(0, 8))
        self.b_voir_dossier = bouton(ligne, "Voir dans le dossier", self.montrer_fichier)
        self.b_voir_dossier.pack(side="left")
        bouton(p, "Nouvel enregistrement", self.nouveau, taille=9).pack(anchor="w", pady=(10, 0))
        return p

    def montrer(self, panneau):
        for p in (self.p_reglages, self.p_enr, self.p_fin, self.p_pret):
            p.pack_forget()
        panneau.pack(fill="both", expand=True)

    # — indications —
    def ecran_choisi(self):
        return self.liste_ecrans[int(self.v_ecran.get())]

    def options_qualite(self):
        l, h, _ = self.ecran_choisi()
        return [("ecran", f"Écran · {l} x {h}"), ("1080p", "1080p"), ("4k", "4K")]

    def maj_indices(self):
        l, h, _ = self.ecran_choisi()
        if hasattr(self, "c_qualite"):
            self.c_qualite.remplir(self.options_qualite())
        cle = self.v_qualite.get()
        cl, ch = moteur.taille_cible(l, h, cle)
        if (cl, ch) == (l, h):
            texte = f"La vidéo fera {l} x {h}, exactement ce que montre l'écran."
        elif cl * ch > l * h:
            texte = (f"Ton écran fait {l} x {h} : la vidéo est enregistrée à cette taille, puis agrandie en "
                     f"{cl} x {ch} à l'arrêt. Plus grande, pas plus détaillée : un écran ne contient pas plus "
                     f"que ce qu'il affiche.")
        else:
            texte = f"La vidéo est enregistrée en {l} x {h}, puis réduite en {cl} x {ch} à l'arrêt."
        self.i_qualite.configure(text=texte)
        self.i_ips.configure(text="60 demande beaucoup à ce PC. Si la vidéo saccade, reviens à 30."
                             if self.v_ips.get() == "60" else "")
        if self.etat == "preparation":
            son = "Recherche du son du PC et des micros…"
        elif not self.son_pc:
            son = ("Son du PC indisponible : active « Mixage stéréo » dans Paramètres du son → Panneau de "
                   "configuration Son → Enregistrement.")
        else:
            son = "Le son du PC est celui des haut-parleurs du PC, pas celui d'un casque Bluetooth."
        if self.v_micro.get() and not self.micros:
            son += " Aucun micro trouvé."
        self.i_son.configure(text=son)

    def maj_dossier(self):
        texte = self.dossier
        if len(texte) > 46:
            texte = "…" + texte[-45:]
        self.l_dossier.configure(text=texte)

    # — démarrage —
    def preparer(self):
        if not self.ffmpeg or not self.ffprobe:
            self.file.put("sans_ffmpeg")
            return
        self.son_pc, self.micros = moteur.peripheriques_audio(self.ffmpeg)
        if not self.source:
            self.source = moteur.choisir_source(self.ffmpeg)
        if not self.encodeur:
            self.encodeur = moteur.choisir_encodeur(self.ffmpeg)
        self.file.put("pret")

    def quand_pret(self):
        self.etat = "pret"
        self.reg.update(encodeur=self.encodeur, source=self.source, ffmpeg=self.ffmpeg)
        ecrire_reglages(self.reg)
        if not self.son_pc:
            self.v_son_pc.set(False)
            self.k_son_pc.configure(state="disabled")
        self.cb_micro.configure(values=self.micros)
        if self.v_micro_nom.get() not in self.micros:
            self.v_micro_nom.set(self.micros[0] if self.micros else "")
        if not self.micros:
            self.v_micro.set(False)
        etat = f"Prêt · codage par la {NOMS_ENCODEURS.get(self.encodeur, self.encodeur)}"
        if self.encodeur == "libx264":
            etat = "Prêt · codage par le processeur (aucune puce vidéo trouvée, ce sera plus lourd)"
        if self.source != "gfxcapture":
            etat += "\nWindows trop ancien pour la capture récente : le curseur peut avoir un cadre blanc."
        if self.raccourcis.ok is False:
            self.l_raccourci.configure(text="Raccourci Ctrl + Alt + R déjà pris par une autre appli")
        self.l_etat.configure(text=etat)
        self.maj_indices()
        if self.demarrer_des_que_pret:
            self.demarrer_des_que_pret = False
            self.l_rec.configure(text="Enregistrer")
            self.demarrer()

    def apres_affichage(self):
        self.r.update_idletasks()
        try:
            # NEBULA_REC_VISIBLE=1 : seulement pour photographier la fenêtre pendant les contrôles.
            if not os.environ.get("NEBULA_REC_VISIBLE"):
                hwnd = user32.GetAncestor(self.r.winfo_id(), 2)
                self.exclu = bool(user32.SetWindowDisplayAffinity(hwnd, 0x11))  # WDA_EXCLUDEFROMCAPTURE
        except Exception:  # noqa: BLE001
            self.exclu = False
        if os.environ.get("NEBULA_REC_VISIBLE"):
            self.exclu = True  # garder la fenêtre ouverte (pas rangée) pour qu'on la voie
            self.r.attributes("-topmost", True)
        self.l_exclu.configure(text="Cette fenêtre n'apparaît pas dans la vidéo." if self.exclu else
                               "La fenêtre se range dans la barre des tâches pendant l'enregistrement.")
        perdus = moteur.sessions_interrompues(TRAVAIL)
        if perdus and self.etat in ("preparation", "pret"):
            rep = messagebox.askyesnocancel(
                NOM, f"{len(perdus)} enregistrement(s) interrompu(s) retrouvé(s) (le PC ou le logiciel s'est "
                     f"arrêté pendant qu'il tournait).\n\nOui : le récupérer dans ton dossier.\nNon : le supprimer."
                     f"\nAnnuler : décider plus tard.", parent=self.r)
            if rep is True:
                threading.Thread(target=self.recuperer, args=(perdus,), daemon=True).start()
            elif rep is False:
                for d in perdus:
                    shutil.rmtree(d, ignore_errors=True)

    def recuperer(self, dossiers):
        retrouves = []
        for d in dossiers:
            try:
                with open(os.path.join(d, "session.json"), encoding="utf-8") as f:
                    quand = dt.datetime.fromisoformat(json.load(f)["debut"])
            except (OSError, ValueError, KeyError):
                quand = dt.datetime.fromtimestamp(os.path.getmtime(d))
            morceaux = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".mkv"))
            try:
                os.makedirs(self.dossier, exist_ok=True)
                sortie = moteur.nom_libre(self.dossier, moteur.nom_de_base(quand) + " (récupéré)")
                moteur.recoller(self.ffmpeg, morceaux, sortie)
                shutil.rmtree(d, ignore_errors=True)
                retrouves.append(sortie)
            except Exception:  # noqa: BLE001
                pass
        self.file.put(("recupere", retrouves))

    # — enregistrer —
    def basculer(self):
        if self.etat == "pret":
            self.demarrer()
        elif self.etat in ("enregistre", "pause"):
            self.arreter()
        elif self.etat == "preparation" and self.ffmpeg:
            # Appui pendant la préparation : on ne l'ignore pas, on démarre dès que tout est prêt.
            self.demarrer_des_que_pret = not self.demarrer_des_que_pret
            self.l_rec.configure(text="Démarre dès que prêt…" if self.demarrer_des_que_pret else "Enregistrer")

    def demarrer(self):
        try:
            os.makedirs(self.dossier, exist_ok=True)
            libre = shutil.disk_usage(self.dossier).free
        except OSError as e:
            messagebox.showerror(NOM, f"Le dossier n'est pas accessible :\n{e}", parent=self.r)
            return
        if libre < 1024 ** 3 and not messagebox.askyesno(
                NOM, f"Il ne reste que {moteur.fmt_taille(libre)} sur le disque. Enregistrer quand même ?",
                parent=self.r):
            return
        self.reg.update(qualite=self.v_qualite.get(), ips=int(self.v_ips.get()), son_pc=self.v_son_pc.get(),
                        micro=self.v_micro.get(), micro_nom=self.v_micro_nom.get(), ecran=int(self.v_ecran.get()),
                        dossier=self.dossier)
        ecrire_reglages(self.reg)
        self.quand, self.cle = dt.datetime.now(), self.v_qualite.get()
        son_pc = self.son_pc if self.v_son_pc.get() else None
        micro = self.v_micro_nom.get() if self.v_micro.get() and self.v_micro_nom.get() in self.micros else None
        travail = os.path.join(TRAVAIL, self.quand.strftime("%Y%m%d-%H%M%S"))
        self.enr = moteur.Enregistrement(self.ffmpeg, travail, int(self.v_ips.get()), self.encodeur,
                                         int(self.v_ecran.get()), son_pc, micro, self.source)
        self.enr.demarrer()
        self.etat = "enregistre"
        l, h, _ = self.ecran_choisi()
        sons = [n for n, v in (("son du PC", son_pc), ("micro", micro)) if v]
        self.base_details = f"{l} x {h} · {self.v_ips.get()} i/s · " + (" + ".join(sons) if sons else "sans son")
        self.l_mode.configure(text="DÉMARRAGE…", fg=C["texte"])
        self.b_pause.configure(text="Pause")
        self.montrer(self.p_enr)
        if not self.exclu:
            self.r.iconify()

    def pause_reprendre(self):
        if self.etat == "enregistre" and self.enr.demarre:
            self.enr.pause()
            self.etat = "pause"
            self.l_mode.configure(text="EN PAUSE", fg=C["ambre"])
            self.b_pause.configure(text="Reprendre")
        elif self.etat == "pause":
            self.enr.reprendre()
            self.etat = "enregistre"
            self.l_mode.configure(text="REPRISE…", fg=C["texte"])
            self.b_pause.configure(text="Pause")

    def arreter(self, note=""):
        self.etat = "finition"
        self.progres, self.annuler_finition, self.note = 0.0, False, note
        self.message_fin = "Fermeture du fichier…"
        self.b_annuler.pack_forget()
        self.montrer(self.p_fin)
        self.r.deiconify()
        threading.Thread(target=self.finaliser, daemon=True).start()

    def finaliser(self):
        enr = self.enr
        try:
            morceaux = enr.arreter()
            if not morceaux:
                raise RuntimeError("Aucune image n'a été enregistrée.\n" + enr.erreur())
            self.message_fin = "Recollage de la vidéo…"
            natif = os.path.join(enr.dossier, "assemble.mp4")
            moteur.recoller(self.ffmpeg, morceaux, natif)
            l, h, duree, images, _son = moteur.sonder(self.ffprobe, natif)
            cl, ch = moteur.taille_cible(l, h, self.cle)
            os.makedirs(self.dossier, exist_ok=True)
            source, cle = natif, self.cle
            if (cl, ch) != (l, h):
                self.message_fin = f"Finition en {QUALITES[self.cle]} ({cl} x {ch})"
                self.file.put("annulable")
                agrandi = os.path.join(enr.dossier, "final.mp4")
                try:
                    fini = moteur.agrandir(self.ffmpeg, natif, agrandi, cl, ch, self.encodeur, duree,
                                           progres=self.avancer, annule=lambda: self.annuler_finition)
                except Exception:  # noqa: BLE001 (la vidéo à la taille de l'écran est sauve, on la garde)
                    fini = False
                    self.note = (self.note + " " if self.note else "") + "La finition a échoué."
                if fini:
                    source = agrandi
                else:
                    cle = "ecran"
            final = moteur.nom_libre(self.dossier, moteur.nom_de_base(self.quand, cle))
            shutil.move(source, final)
            L, H, duree_f, _i, son = moteur.sonder(self.ffprobe, final)
            ips_moy = images / duree if duree > 0 else 0
            shutil.rmtree(enr.dossier, ignore_errors=True)
            self.resultat = dict(chemin=final, l=L, h=H, duree=duree_f, taille=os.path.getsize(final), son=son,
                                 ips=enr.ips, ips_moy=ips_moy, annule=cle != self.cle)
        except Exception as e:  # noqa: BLE001
            self.resultat = dict(erreur=str(e), dossier=enr.dossier)
            if not enr.images():
                # Au prochain lancement, on reteste la capture et la puce vidéo.
                self.reg.pop("encodeur", None)
                self.reg.pop("source", None)
                ecrire_reglages(self.reg)
        self.file.put("fini")

    def avancer(self, part):
        self.progres = part

    def annuler(self):
        self.annuler_finition = True
        self.message_fin = "Annulation…"

    def afficher_resultat(self):
        res = self.resultat or {}
        self.etat = "pret" if self.encodeur else "preparation"
        if "erreur" in res:
            self.l_res_titre.configure(text="L'enregistrement a échoué", fg=C["rouge"])
            self.l_res_nom.configure(text=res["erreur"][-400:])
            self.l_res_details.configure(text=f"Les morceaux éventuels sont gardés ici : {res['dossier']}")
            self.l_res_note.configure(text="Essaie sans le son (un micro pris par une autre appli bloque tout), "
                                           "ou redémarre le logiciel.")
            self.b_voir.pack_forget()
        else:
            self.b_voir.pack(side="left", padx=(0, 8), before=self.b_voir_dossier)
            self.l_res_titre.configure(text="Vidéo prête", fg=C["vert"])
            self.l_res_nom.configure(text=os.path.basename(res["chemin"]))
            self.l_res_details.configure(text=f"{res['l']} x {res['h']} · {res['ips']} i/s · "
                                              f"{moteur.fmt_duree(res['duree'])} · {moteur.fmt_taille(res['taille'])}"
                                              + ("" if res["son"] else " · sans son"))
            notes = [self.note] if self.note else []
            if res["annule"]:
                notes.append("Finition annulée : la vidéo est gardée à la taille de l'écran.")
            if res["ips_moy"] and res["ips_moy"] < 0.9 * res["ips"]:
                notes.append(f"Le PC a suivi à {res['ips_moy']:.0f} images/s en moyenne au lieu de {res['ips']}. "
                             f"Choisis 30, ou ferme des applis, pour une vidéo plus régulière.")
            self.l_res_note.configure(text="\n".join(notes))
        self.montrer(self.p_pret)
        self.r.deiconify()
        self.r.lift()
        if self.fermer_apres:
            self.r.destroy()

    def nouveau(self):
        self.montrer(self.p_reglages)

    # — fichiers —
    def ouvrir_video(self):
        if self.resultat and "chemin" in self.resultat:
            os.startfile(self.resultat["chemin"])

    def montrer_fichier(self):
        if self.resultat and "chemin" in self.resultat:
            subprocess.Popen(f'explorer /select,"{self.resultat["chemin"]}"')
        else:
            self.ouvrir_dossier()

    def ouvrir_dossier(self):
        os.makedirs(self.dossier, exist_ok=True)
        os.startfile(self.dossier)

    def changer_dossier(self):
        choix = filedialog.askdirectory(parent=self.r, initialdir=self.dossier, title="Où ranger les vidéos ?")
        if choix:
            self.dossier = os.path.normpath(choix)
            self.reg["dossier"] = self.dossier
            ecrire_reglages(self.reg)
            self.maj_dossier()

    # — la boucle —
    def boucle(self):
        try:
            while True:
                evt = self.file.get_nowait()
                if evt == "pret":
                    self.quand_pret()
                elif evt == "sans_ffmpeg":
                    self.l_etat.configure(text="ffmpeg introuvable. Installe-le : winget install Gyan.FFmpeg",
                                          fg=C["rouge"])
                elif evt == "basculer":
                    self.basculer()
                elif evt == "pause":
                    self.pause_reprendre()
                elif evt == "annulable":
                    self.b_annuler.pack(anchor="w", pady=(18, 0))
                elif evt == "fini":
                    self.afficher_resultat()
                elif isinstance(evt, tuple) and evt[0] == "recupere" and evt[1]:
                    messagebox.showinfo(NOM, "Récupéré dans ton dossier :\n" +
                                        "\n".join(os.path.basename(c) for c in evt[1]), parent=self.r)
        except queue.Empty:
            pass

        if self.etat in ("enregistre", "pause") and self.enr:
            if self.etat == "enregistre" and self.enr.mort_seul():
                self.arreter(note="L'enregistrement s'est arrêté tout seul (écran verrouillé, son débranché ?). "
                                  "Ce qui a été filmé est gardé.")
            else:
                if self.etat == "enregistre" and self.enr.demarre:
                    self.l_mode.configure(text="ENREGISTREMENT", fg=C["texte"])
                self.l_chrono.configure(text=moteur.fmt_duree(self.enr.duree()))
                self.l_details.configure(text=f"{self.base_details} · {moteur.fmt_taille(self.enr.taille())}")
                self.clignote = (self.clignote + 1) % 6
                allume = self.etat == "pause" or self.clignote < 3
                self.point.itemconfigure(self.point_id, fill=(C["ambre"] if self.etat == "pause" else C["rouge"])
                                         if allume else C["fond"])
        elif self.etat == "finition":
            self.l_fin.configure(text=self.message_fin)
            if self.message_fin.startswith("Finition"):
                self.barre.configure(value=int(self.progres * 1000))
                self.l_pct.configure(text=f"{self.progres * 100:.0f} %")
            else:
                self.barre.configure(value=0)
                self.l_pct.configure(text="")
        self.r.after(200, self.boucle)

    def fermer(self):
        if self.etat in ("enregistre", "pause"):
            if messagebox.askyesno(NOM, "Un enregistrement est en cours. L'arrêter et garder la vidéo ?",
                                   parent=self.r):
                self.fermer_apres = True
                self.arreter()
            return
        if self.etat == "finition":
            messagebox.showinfo(NOM, "La vidéo est en train d'être terminée, patiente quelques instants.",
                                parent=self.r)
            return
        self.r.destroy()


def main():
    moteur.rendre_net()
    if deja_ouvert():
        return
    racine = tk.Tk()
    Appli(racine)
    racine.mainloop()


if __name__ == "__main__":
    main()
