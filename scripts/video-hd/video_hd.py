#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIDÉO HD : monter une vidéo en 4K et en 60 images par seconde, avec l'IA, gratuitement.

    python video_hd.py ma_video.mp4                  4K, 60 images/s, vidéo filmée
    python video_hd.py ma_video.mp4 --ips 30         4K, 30 images/s
    python video_hd.py ma_video.mp4 --style anime    pour un dessin animé
    python video_hd.py ma_video.mp4 --essai 10       seulement les 10 premières secondes

Deux IA libres, téléchargées depuis GitHub au premier lancement :
  · agrandir   : Real-ESRGAN (Xintao Wang et al., licence BSD-3-Clause)
                 https://github.com/xinntao/Real-ESRGAN
  · fluidifier : RIFE 4.25 (Zhewei Huang, hzwer/Practical-RIFE, licence MIT),
                 architecture et poids tels que publiés par HolyWu/vs-rife (licence MIT)
                 https://github.com/HolyWu/vs-rife

Le son d'origine est gardé. Le travail se fait image par image, sans rien entasser sur le
disque : la vidéo est lue, agrandie, fluidifiée et réencodée au fil de l'eau.

Fait pour Google Colab (carte graphique NVIDIA prêtée gratuitement), voir Video_HD.ipynb.
Marche aussi sur un PC sans carte graphique, mais beaucoup plus lentement.
"""

import argparse
import json
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from fractions import Fraction

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

ESRGAN = "https://github.com/xinntao/Real-ESRGAN/releases/download/"
URL_RIFE = "https://github.com/HolyWu/vs-rife/releases/download/model/flownet_v4.25.pkl"

# Boîte (grand côté, petit côté) : une vidéo verticale de téléphone devient 2160 x 3840.
BOITES = {"4k": (3840, 2160), "1440p": (2560, 1440), "1080p": (1920, 1080)}
LIBELLES = {"4k": "4K", "1440p": "1440p", "1080p": "1080p"}

CADENCES_USUELLES = [
    Fraction(24000, 1001), Fraction(24), Fraction(25), Fraction(30000, 1001), Fraction(30),
    Fraction(48), Fraction(50), Fraction(60000, 1001), Fraction(60), Fraction(90),
    Fraction(100), Fraction(120),
]

# Au-delà de cet écart moyen de luminosité entre deux images, c'est un changement de plan :
# on ne fabrique pas d'image entre les deux (elle mélangerait deux scènes).
SEUIL_COUPURE = 0.10

# HDR (iPhone, HLG ou PQ) vers couleurs normales, sinon l'image sort terne et délavée.
TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


class _JamaisLevee(Exception):
    pass


# « mémoire de la carte graphique pleine » ; sur un PC sans carte, cette erreur n'existe pas
ERREUR_MEMOIRE = getattr(torch.cuda, "OutOfMemoryError", _JamaisLevee)


# --------------------------------------------------------------------------------------------
# Real-ESRGAN : les deux architectures, recopiées de basicsr (BSD-3) pour ne pas dépendre
# d'un paquet qui casse avec les versions récentes de torchvision.
# --------------------------------------------------------------------------------------------

class SRVGGNetCompact(nn.Module):
    """Le petit modèle rapide : realesr-general-x4v3 (filmé) et realesr-animevideov3 (animé)."""

    def __init__(self, num_feat=64, num_conv=16, upscale=4):
        super().__init__()
        self.upscale = upscale
        self.body = nn.ModuleList()
        self.body.append(nn.Conv2d(3, num_feat, 3, 1, 1))
        self.body.append(nn.PReLU(num_parameters=num_feat))
        for _ in range(num_conv):
            self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
            self.body.append(nn.PReLU(num_parameters=num_feat))
        self.body.append(nn.Conv2d(num_feat, 3 * upscale * upscale, 3, 1, 1))
        self.upsampler = nn.PixelShuffle(upscale)

    def forward(self, x):
        out = x
        for couche in self.body:
            out = couche(out)
        out = self.upsampler(out)
        return out + F.interpolate(x, scale_factor=self.upscale, mode="nearest")


class ResidualDenseBlock(nn.Module):
    def __init__(self, num_feat=64, num_grow_ch=32):
        super().__init__()
        self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, num_feat, num_grow_ch=32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    """Le gros modèle, plus fin et beaucoup plus lent : RealESRGAN_x4plus et _x2plus."""

    def __init__(self, scale=4, num_feat=64, num_block=23, num_grow_ch=32):
        super().__init__()
        self.scale = scale
        num_in_ch = 3 * (4 if scale == 2 else 1)
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(num_feat, num_grow_ch) for _ in range(num_block)])
        self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_feat, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        feat = F.pixel_unshuffle(x, 2) if self.scale == 2 else x
        feat = self.conv_first(feat)
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


# nom du fichier de poids, dossier de publication, fabrique, facteur d'agrandissement
MODELES_SR = {
    "reel": ("realesr-general-x4v3.pth", "v0.2.5.0", lambda: SRVGGNetCompact(64, 32, 4), 4),
    "anime": ("realesr-animevideov3.pth", "v0.2.5.0", lambda: SRVGGNetCompact(64, 16, 4), 4),
    "max4": ("RealESRGAN_x4plus.pth", "v0.1.0", lambda: RRDBNet(4), 4),
    "max2": ("RealESRGAN_x2plus.pth", "v0.2.1", lambda: RRDBNet(2), 2),
}
NOMS_SR = {
    "reel": "Real-ESRGAN, vidéo filmée",
    "anime": "Real-ESRGAN, dessin animé",
    "max4": "Real-ESRGAN x4plus, finesse maximale",
    "max2": "Real-ESRGAN x2plus, finesse maximale",
}


# --------------------------------------------------------------------------------------------
# RIFE 4.25 : architecture reprise telle quelle de HolyWu/vs-rife (MIT), qui la tient de
# hzwer/Practical-RIFE (MIT). Les poids publiés par vs-rife correspondent à ce code-là.
# --------------------------------------------------------------------------------------------

def _warp(entree, flot, flot_div, grille):
    dtype = entree.dtype
    entree = entree.to(torch.float)
    flot = flot.to(torch.float)
    flot = torch.cat([flot[:, 0:1] / flot_div[0], flot[:, 1:2] / flot_div[1]], 1)
    g = (grille + flot).permute(0, 2, 3, 1)
    return F.grid_sample(input=entree, grid=g, mode="bilinear", padding_mode="border",
                         align_corners=True).to(dtype)


def _conv(in_planes, out_planes, kernel_size=3, stride=1, padding=1, dilation=1):
    return nn.Sequential(
        nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride,
                  padding=padding, dilation=dilation, bias=True),
        nn.LeakyReLU(0.2, True),
    )


class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn0 = nn.Conv2d(3, 16, 3, 2, 1)
        self.cnn1 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn2 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn3 = nn.ConvTranspose2d(16, 4, 4, 2, 1)
        self.relu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        x = x.clamp(0.0, 1.0)
        x = self.relu(self.cnn0(x))
        x = self.relu(self.cnn1(x))
        x = self.relu(self.cnn2(x))
        return self.cnn3(x)


class ResConv(nn.Module):
    def __init__(self, c, dilation=1):
        super().__init__()
        self.conv = nn.Conv2d(c, c, 3, 1, dilation, dilation=dilation, groups=1)
        self.beta = nn.Parameter(torch.ones((1, c, 1, 1)), requires_grad=True)
        self.relu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        return self.relu(self.conv(x) * self.beta + x)


class IFBlock(nn.Module):
    def __init__(self, in_planes, c=64):
        super().__init__()
        self.conv0 = nn.Sequential(_conv(in_planes, c // 2, 3, 2, 1), _conv(c // 2, c, 3, 2, 1))
        self.convblock = nn.Sequential(*[ResConv(c) for _ in range(8)])
        self.lastconv = nn.Sequential(nn.ConvTranspose2d(c, 4 * 13, 4, 2, 1), nn.PixelShuffle(2))

    def forward(self, x, flow=None, scale=1):
        x = F.interpolate(x, scale_factor=1.0 / scale, mode="bilinear")
        if flow is not None:
            flow = F.interpolate(flow, scale_factor=1.0 / scale, mode="bilinear") / scale
            x = torch.cat((x, flow), 1)
        feat = self.convblock(self.conv0(x))
        tmp = F.interpolate(self.lastconv(feat), scale_factor=scale, mode="bilinear")
        return tmp[:, :4] * scale, tmp[:, 4:5], tmp[:, 5:]


class IFNet(nn.Module):
    def __init__(self, scale=1.0):
        super().__init__()
        self.block0 = IFBlock(7 + 8, c=192)
        self.block1 = IFBlock(8 + 4 + 8 + 8, c=128)
        self.block2 = IFBlock(8 + 4 + 8 + 8, c=96)
        self.block3 = IFBlock(8 + 4 + 8 + 8, c=64)
        self.block4 = IFBlock(8 + 4 + 8 + 8, c=32)
        self.encode = Head()
        self.scale_list = [16 / scale, 8 / scale, 4 / scale, 2 / scale, 1 / scale]

    def forward(self, img0, img1, timestep, flot_div, grille, f0, f1):
        img0 = img0.clamp(0.0, 1.0)
        img1 = img1.clamp(0.0, 1.0)
        warped0, warped1 = img0, img1
        flow = mask = feat = None
        blocs = [self.block0, self.block1, self.block2, self.block3, self.block4]
        for i, bloc in enumerate(blocs):
            if flow is None:
                flow, mask, feat = bloc(torch.cat((img0, img1, f0, f1, timestep), 1), None,
                                        scale=self.scale_list[i])
            else:
                wf0 = _warp(f0, flow[:, :2], flot_div, grille)
                wf1 = _warp(f1, flow[:, 2:4], flot_div, grille)
                fd, mask, feat = bloc(torch.cat((warped0, warped1, wf0, wf1, timestep, mask, feat), 1),
                                      flow, scale=self.scale_list[i])
                flow = flow + fd
            warped0 = _warp(img0, flow[:, :2], flot_div, grille)
            warped1 = _warp(img1, flow[:, 2:4], flot_div, grille)
        mask = torch.sigmoid(mask)
        return warped0 * mask + warped1 * (1 - mask)


# --------------------------------------------------------------------------------------------
# Les deux IA, prêtes à l'emploi
# --------------------------------------------------------------------------------------------

def telecharger(url, dossier, nom):
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom)
    if os.path.isfile(chemin) and os.path.getsize(chemin) > 1_000_000:
        return chemin
    print(f"  téléchargement de {nom}…", flush=True)
    partiel = chemin + ".part"
    requete = urllib.request.Request(url, headers={"User-Agent": "video-hd"})
    with urllib.request.urlopen(requete, timeout=180) as r, open(partiel, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    os.replace(partiel, chemin)
    return chemin


def charger_poids(dossier, nom, version):
    poids = torch.load(telecharger(ESRGAN + version + "/" + nom, dossier, nom),
                       map_location="cpu", weights_only=True)
    if "params_ema" in poids:
        return poids["params_ema"]
    return poids.get("params", poids)


class Agrandisseur:
    def __init__(self, cle, appareil, dtype, dossier, tuile=0, debruitage=0.5):
        nom, version, fabrique, facteur = MODELES_SR[cle]
        modele = fabrique()
        poids = charger_poids(dossier, nom, version)
        if cle == "reel" and debruitage < 1:
            # Comme l'outil officiel (--denoise_strength, 0,5 par défaut) : on mélange le modèle
            # avec sa version « faible débruitage », sinon il efface le grain et les textures fines.
            faible = charger_poids(dossier, "realesr-general-wdn-x4v3.pth", "v0.2.5.0")
            poids = {k: debruitage * v + (1 - debruitage) * faible[k] for k, v in poids.items()}
        modele.load_state_dict(poids, strict=True)
        self.modele = modele.eval().to(appareil, dtype)
        self.facteur = facteur
        self.tuile = tuile
        self.cuda = appareil.type == "cuda"

    def _par_tuiles(self, x):
        f, t, marge = self.facteur, self.tuile, 16
        _, c, h, w = x.shape
        sortie = x.new_zeros((1, c, h * f, w * f))
        for y0 in range(0, h, t):
            for x0 in range(0, w, t):
                y1, x1 = min(y0 + t, h), min(x0 + t, w)
                ya, xa = max(y0 - marge, 0), max(x0 - marge, 0)
                yb, xb = min(y1 + marge, h), min(x1 + marge, w)
                morceau = self.modele(x[:, :, ya:yb, xa:xb])
                sortie[:, :, y0 * f:y1 * f, x0 * f:x1 * f] = morceau[
                    :, :, (y0 - ya) * f:(y1 - ya) * f, (x0 - xa) * f:(x1 - xa) * f]
        return sortie

    def __call__(self, x):
        h, w = x.shape[2:]
        # x2plus travaille sur des blocs de 2 x 2 pixels : il lui faut des côtés pairs
        bas, droite = (h % 2, w % 2) if self.facteur == 2 else (0, 0)
        if bas or droite:
            x = F.pad(x, (0, droite, 0, bas), mode="replicate")
        while True:
            try:
                y = self._par_tuiles(x) if self.tuile else self.modele(x)
                break
            except ERREUR_MEMOIRE:
                if self.tuile and self.tuile <= 128:
                    raise
                self.tuile = 512 if not self.tuile else self.tuile // 2
                torch.cuda.empty_cache()
                print(f"\n  mémoire de la carte pleine : je découpe chaque image en tuiles de "
                      f"{self.tuile} px", flush=True)
        return y[:, :, :h * self.facteur, :w * self.facteur]


class Interpolateur:
    def __init__(self, appareil, dtype, dossier, hauteur, largeur):
        # RIFE conseille de calculer le mouvement à mi-résolution au-delà du 1440p
        echelle = 0.5 if max(hauteur, largeur) > 2560 else 1.0
        modele = IFNet(echelle)
        poids = torch.load(telecharger(URL_RIFE, dossier, "flownet_v4.25.pkl"),
                           map_location="cpu", weights_only=True)
        poids = {k.replace("module.", ""): v for k, v in poids.items() if "module." in k}
        manque, _ = modele.load_state_dict(poids, strict=False)
        if manque:
            raise SystemExit(f"Poids RIFE incomplets ({len(manque)} manquants, ex. {manque[0]})")
        self.modele = modele.eval().to(appareil, dtype)
        multiple = max(64, int(64 / echelle))
        self.h, self.w = hauteur, largeur
        self.ph = math.ceil(hauteur / multiple) * multiple
        self.pw = math.ceil(largeur / multiple) * multiple
        self.bourrage = (0, self.pw - largeur, 0, self.ph - hauteur)
        self.flot_div = torch.tensor([(self.pw - 1.0) / 2.0, (self.ph - 1.0) / 2.0],
                                     dtype=torch.float, device=appareil)
        horiz = torch.linspace(-1.0, 1.0, self.pw, dtype=torch.float, device=appareil)
        horiz = horiz.view(1, 1, 1, self.pw).expand(-1, -1, self.ph, -1)
        vert = torch.linspace(-1.0, 1.0, self.ph, dtype=torch.float, device=appareil)
        vert = vert.view(1, 1, self.ph, 1).expand(-1, -1, -1, self.pw)
        self.grille = torch.cat([horiz, vert], 1)
        self.pas = torch.empty((1, 1, self.ph, self.pw), dtype=dtype, device=appareil)

    def preparer(self, img):
        if any(self.bourrage):
            img = F.pad(img, self.bourrage)
        return img, self.modele.encode(img)

    def __call__(self, a, b, t):
        self.pas.fill_(t)
        sortie = self.modele(a[0], b[0], self.pas, self.flot_div, self.grille, a[1], b[1])
        return sortie[:, :, :self.h, :self.w]


# --------------------------------------------------------------------------------------------
# Lire la vidéo
# --------------------------------------------------------------------------------------------

def arrondir_cadence(ips):
    proche = min(CADENCES_USUELLES, key=lambda c: abs(float(c) - float(ips)))
    if abs(float(proche) - float(ips)) / float(ips) < 0.015:
        return proche
    return ips.limit_denominator(1001)


def sonder(chemin):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", chemin],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"Impossible de lire la vidéo : {r.stderr.strip()}")
    d = json.loads(r.stdout)
    flux = d.get("streams", [])
    video = next((s for s in flux if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    if video is None:
        raise SystemExit("Ce fichier ne contient pas d'image vidéo.")
    largeur, hauteur = int(video["width"]), int(video["height"])
    rotation = 0
    candidats = [video.get("tags", {}).get("rotate")]
    candidats += [sd.get("rotation") for sd in video.get("side_data_list") or []]
    for valeur in candidats:
        try:
            if valeur is not None:
                rotation = int(float(valeur))
        except ValueError:
            pass
    if abs(rotation) % 180 == 90:  # vidéo de téléphone tenue debout
        largeur, hauteur = hauteur, largeur
    ips = None
    for cle in ("avg_frame_rate", "r_frame_rate"):
        try:
            f = Fraction(video.get(cle, "0/1"))
            if 1 <= f <= 500:
                ips = f
                break
        except (ZeroDivisionError, ValueError):
            pass
    duree = 0.0
    for valeur in (video.get("duration"), d.get("format", {}).get("duration")):
        try:
            if valeur and float(valeur) > 0:
                duree = float(valeur)
                break
        except ValueError:
            pass
    return {
        "index": int(video["index"]),
        "largeur": largeur,
        "hauteur": hauteur,
        "ips": arrondir_cadence(ips or Fraction(30)),
        "duree": duree,
        "audio": any(s.get("codec_type") == "audio" for s in flux),
        "hdr": video.get("color_transfer", "") in ("arib-std-b67", "smpte2084"),
    }


def filtre_disponible(nom):
    r = subprocess.run([FFMPEG, "-hide_banner", "-filters"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return re.search(rf"\s{nom}\s", r.stdout) is not None


def choisir_encodeur(qualite):
    nvenc = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", str(qualite),
             "-b:v", "0", "-profile:v", "high"]
    essai = subprocess.run([FFMPEG, "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.2",
                            *nvenc, "-f", "null", "-"], capture_output=True)
    if essai.returncode == 0:
        return "carte graphique (NVENC, H.264)", nvenc
    return "processeur (x264)", ["-c:v", "libx264", "-preset", "faster",
                                 "-crf", str(max(qualite - 2, 0))]


def taille_cible(largeur, hauteur, cle):
    if cle == "garder":
        return largeur, hauteur, 1.0
    if cle in BOITES:
        grand, petit = BOITES[cle]
    else:
        grand, petit = sorted(map(int, cle.lower().split("x")), reverse=True)
    if largeur >= hauteur:
        s = min(grand / largeur, petit / hauteur)
    else:
        s = min(petit / largeur, grand / hauteur)
    return round(largeur * s / 2) * 2, round(hauteur * s / 2) * 2, s


# --------------------------------------------------------------------------------------------
# Affichage
# --------------------------------------------------------------------------------------------

def fmt_ips(f):
    return str(f.numerator) if f.denominator == 1 else f"{float(f):.2f}".replace(".", ",")


def fmt_duree(secondes):
    if secondes < 10:
        return f"{max(0.0, secondes):.1f}".replace(".", ",").replace(",0", "") + " s"
    secondes = int(round(secondes))
    if secondes < 60:
        return f"{secondes} s"
    if secondes < 3600:
        return f"{secondes // 60} min {secondes % 60:02d} s"
    return f"{secondes // 3600} h {secondes % 3600 // 60:02d} min"


# --------------------------------------------------------------------------------------------
# Le travail
# --------------------------------------------------------------------------------------------

def analyser(argv):
    p = argparse.ArgumentParser(prog="video_hd",
                                description="Monter une vidéo en 4K et en 60 images par seconde, avec l'IA.")
    p.add_argument("entree", help="la vidéo à améliorer")
    p.add_argument("--taille", default="4k", help="4k (défaut), 1440p, 1080p, garder, ou une boîte LxH")
    p.add_argument("--ips", default="60", help="images par seconde : 60 (défaut), 30, 50, 25, 24, ou garder")
    p.add_argument("--style", default="reel", choices=["reel", "anime", "max"],
                   help="reel = vidéo filmée (défaut, rapide), anime = dessin animé, "
                        "max = vidéo filmée en finesse maximale (beaucoup plus lent)")
    p.add_argument("--essai", type=float, default=0,
                   help="ne traiter que les N premières secondes (0 = toute la vidéo)")
    p.add_argument("--debruitage", type=float, default=0.5,
                   help="vidéo filmée seulement : 0 = garde le grain, 1 = lisse tout (défaut 0,5)")
    p.add_argument("--qualite", type=int, default=20,
                   help="18 = plus beau et plus lourd, 24 = plus léger (défaut 20)")
    p.add_argument("--sortie", default="", help="fichier de sortie (défaut : dans --dossier)")
    p.add_argument("--dossier", default="", help="dossier de sortie (défaut : celui de la vidéo)")
    p.add_argument("--modeles", default=os.path.join(os.path.expanduser("~"), ".cache", "video_hd"),
                   help="où ranger les poids des IA")
    p.add_argument("--tuile", type=int, default=0, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    a.debruitage = min(1.0, max(0.0, a.debruitage))
    a.taille = a.taille.lower()
    if a.taille not in BOITES and a.taille != "garder" and not re.fullmatch(r"\d+x\d+", a.taille):
        p.error("--taille : 4k, 1440p, 1080p, garder, ou LxH")
    if a.ips.lower() != "garder":
        try:
            if Fraction(a.ips.replace(",", ".")) <= 0:
                raise ValueError
        except (ValueError, ZeroDivisionError):
            p.error("--ips : un nombre d'images par seconde, ou garder")
    return a


def principal(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    a = analyser(argv)
    if not os.path.isfile(a.entree):
        raise SystemExit(f"Fichier introuvable : {a.entree}")

    info = sonder(a.entree)
    w, h, ips_src = info["largeur"], info["hauteur"], info["ips"]

    W, H, s = taille_cible(w, h, a.taille)
    agrandir = s > 1.05
    if not agrandir:
        W, H = w - w % 2, h - h % 2

    if a.ips.lower() == "garder":
        ips_out = ips_src
    else:
        ips_out = arrondir_cadence(Fraction(a.ips.replace(",", ".")))
    interpoler = ips_out > ips_src * Fraction(101, 100)
    pas_source = ips_src / ips_out  # images source parcourues pour chaque image produite

    duree = info["duree"]
    if a.essai:
        duree = min(duree, a.essai) if duree else a.essai
    n_src = max(1, round(duree * float(ips_src))) if duree else 0
    n_out = math.ceil(n_src / pas_source) if n_src else 0

    appareil = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if appareil.type == "cuda" else torch.float32
    if appareil.type == "cuda":
        torch.backends.cudnn.benchmark = True
        calcul = f"carte graphique {torch.cuda.get_device_name(0)}"
    else:
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        calcul = "processeur (sans carte graphique : ce sera lent)"

    cle_sr = None
    if agrandir:
        cle_sr = a.style if a.style in ("reel", "anime") else ("max2" if s <= 2 else "max4")

    base = os.path.splitext(os.path.basename(a.entree))[0]
    libelle = LIBELLES.get(a.taille, f"{W}x{H}") if agrandir else "taille-origine"
    nom_sortie = f"{base}_{libelle}_{fmt_ips(ips_out)}ips{'_essai' if a.essai else ''}.mp4"
    sortie = a.sortie or os.path.join(a.dossier or os.path.dirname(os.path.abspath(a.entree)), nom_sortie)
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)

    nom_enc, args_enc = choisir_encodeur(a.qualite)
    filtres = []
    if info["hdr"]:
        if filtre_disponible("zscale"):
            filtres.append(TONEMAP)
        else:
            print("  ⚠️ Vidéo HDR (iPhone ?) : les couleurs risquent de sortir ternes.")
    filtres.append(f"fps={ips_src.numerator}/{ips_src.denominator}")

    print()
    print(f"  Vidéo       : {os.path.basename(a.entree)} ({w} x {h}, {fmt_ips(ips_src)} images/s, "
          f"{fmt_duree(info['duree'])}, son : {'oui' if info['audio'] else 'non'}"
          f"{', HDR' if info['hdr'] else ''})")
    if a.essai:
        print(f"  Essai       : seulement le début, {fmt_duree(duree)}")
    print(f"  Résultat    : {W} x {H}, {fmt_ips(ips_out)} images/s")
    if agrandir:
        detail = f"{NOMS_SR[cle_sr]}, x{s:.2f}".replace(".", ",")
        if cle_sr == "reel":
            detail += f", débruitage {a.debruitage * 100:.0f} %"
        print(f"  Agrandir    : {detail}")
    else:
        print("  Agrandir    : non, déjà à la taille")
    print(f"  Fluidifier  : {f'RIFE 4.25, {fmt_ips(ips_src)} → {fmt_ips(ips_out)} images/s' if interpoler else 'non'}")
    print(f"  Calcul      : {calcul}")
    print(f"  Encodage    : {nom_enc}")
    print(f"  Fichier     : {sortie}")
    print(flush=True)

    agrandisseur = Agrandisseur(cle_sr, appareil, dtype, a.modeles, a.tuile, a.debruitage) if agrandir else None
    interpolateur = Interpolateur(appareil, dtype, a.modeles, H, W) if interpoler else None

    journal_dec = tempfile.TemporaryFile()
    journal_enc = tempfile.TemporaryFile()

    cmd_dec = [FFMPEG, "-v", "error", "-nostdin"]
    if a.essai:
        cmd_dec += ["-t", str(a.essai)]
    cmd_dec += ["-i", a.entree, "-map", f"0:{info['index']}", "-vf", ",".join(filtres),
                "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]

    cmd_enc = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", f"{ips_out.numerator}/{ips_out.denominator}", "-i", "-"]
    if info["audio"]:
        if a.essai:
            cmd_enc += ["-t", str(a.essai)]
        cmd_enc += ["-i", a.entree]
    cmd_enc += ["-map", "0:v:0"]
    if info["audio"]:
        cmd_enc += ["-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k"]
    # Les couleurs BT.709 sont écrites dans le flux H.264 lui-même : les options -color_* seules
    # ne sont pas reprises par toutes les versions de ffmpeg (vérifié : ffmpeg 9 les ignore ici).
    cmd_enc += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", *args_enc,
                "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
                "-movflags", "+faststart", "-shortest", sortie]

    dec = subprocess.Popen(cmd_dec, stdout=subprocess.PIPE, stderr=journal_dec)
    enc = subprocess.Popen(cmd_enc, stdin=subprocess.PIPE, stderr=journal_enc)

    file_entree = queue.Queue(maxsize=6)
    file_sortie = queue.Queue(maxsize=6)
    incidents = []

    def lire():
        octets = w * h * 3
        try:
            while True:
                tampon = bytearray(octets)
                vue, lu = memoryview(tampon), 0
                while lu < octets:
                    n = dec.stdout.readinto(vue[lu:])
                    if not n:
                        break
                    lu += n
                if lu < octets:
                    break
                file_entree.put(np.frombuffer(tampon, dtype=np.uint8).reshape(h, w, 3))
        except Exception as e:  # noqa: BLE001
            incidents.append(f"lecture : {e}")
        finally:
            file_entree.put(None)

    def ecrire():
        while True:
            img = file_sortie.get()
            if img is None:
                break
            if incidents:
                continue  # on vide la file pour ne bloquer personne
            try:
                enc.stdin.write(img.data)
            except (BrokenPipeError, OSError) as e:
                incidents.append(f"encodage : {e}")
        try:
            enc.stdin.close()
        except OSError:
            pass

    lecteur = threading.Thread(target=lire, daemon=True)
    ecrivain = threading.Thread(target=ecrire, daemon=True)
    lecteur.start()
    ecrivain.start()

    class Image:
        __slots__ = ("t", "prep", "mini")

        def __init__(self, t):
            self.t, self.prep, self.mini = t, None, None

    def vers_tenseur(img):
        x = torch.from_numpy(img).to(appareil, non_blocking=True)
        return x.permute(2, 0, 1).unsqueeze(0).to(dtype).div_(255)

    def traiter(img):
        x = vers_tenseur(img)
        if agrandisseur is None:
            return x[:, :, :H, :W]
        y = agrandisseur(x)
        if tuple(y.shape[2:]) != (H, W):
            y = F.interpolate(y.float(), size=(H, W), mode="bicubic", antialias=True).clamp_(0, 1).to(dtype)
        return y

    def miniature(im):
        if im.mini is None:
            im.mini = F.interpolate(im.t.float().mean(1, keepdim=True), size=(36, 64), mode="area")
        return im.mini

    debut = time.time()
    etat = {"produites": 0, "affiche": 0.0}

    def sortir(t):
        if incidents:
            raise RuntimeError(incidents[0])
        img = t.clamp(0, 1).mul(255).round().to(torch.uint8)[0].permute(1, 2, 0).contiguous().cpu().numpy()
        file_sortie.put(img)
        etat["produites"] += 1
        maintenant = time.time()
        if maintenant - etat["affiche"] >= 2:
            etat["affiche"] = maintenant
            ecoule = maintenant - debut
            vitesse = etat["produites"] / ecoule if ecoule > 0 else 0
            ligne = f"  {etat['produites']}"
            if n_out:
                pc = min(100, 100 * etat["produites"] / n_out)
                reste = (n_out - etat["produites"]) / vitesse if vitesse > 0 else 0
                ligne += (f" / {n_out} images ({pc:.0f} %) · {vitesse:.1f} images/s · "
                          f"reste ≈ {fmt_duree(reste)}").replace(".", ",")
            else:
                ligne += f" images · {vitesse:.1f} images/s".replace(".", ",")
            print("\r" + ligne.ljust(96), end="", flush=True)

    @torch.inference_mode()
    def boucle():
        k = 0          # index de la prochaine image produite
        j = -1         # index de l'image source qu'on vient de lire
        prec = None
        while True:
            img = file_entree.get()
            if img is None:  # « is », pas « == » : numpy comparerait pixel par pixel
                break
            j += 1
            cour = Image(traiter(img))
            if prec is not None:
                coupure = None
                # toutes les images produites qui tombent entre prec (j - 1) et cour (j)
                while k * pas_source < j:
                    t = k * pas_source - (j - 1)
                    if t == 0:
                        sortir(prec.t)
                    elif not interpoler:
                        sortir(prec.t if t < Fraction(1, 2) else cour.t)
                    else:
                        if coupure is None:
                            coupure = (miniature(prec) - miniature(cour)).abs().mean().item() > SEUIL_COUPURE
                        if coupure:
                            sortir(prec.t if t < Fraction(1, 2) else cour.t)
                        else:
                            if prec.prep is None:
                                prec.prep = interpolateur.preparer(prec.t)
                            if cour.prep is None:
                                cour.prep = interpolateur.preparer(cour.t)
                            sortir(interpolateur(prec.prep, cour.prep, float(t)))
                    k += 1
            prec = cour
        if prec is not None:  # la fin : la dernière image tient jusqu'au bout
            while k * pas_source < j + 1:
                sortir(prec.t)
                k += 1
        return j + 1

    try:
        lues = boucle()
    except BaseException:
        dec.kill()
        enc.kill()
        # le lecteur peut attendre une place dans la file : on la vide pour qu'il s'arrête
        def vider():
            while file_entree.get() is not None:
                pass

        threading.Thread(target=vider, daemon=True).start()
        raise
    finally:
        file_sortie.put(None)
        ecrivain.join()

    enc.wait()
    dec.wait()
    print()
    for proc, journal, quoi in ((dec, journal_dec, "la lecture"), (enc, journal_enc, "l'encodage")):
        if proc.returncode != 0 or incidents:
            journal.seek(0)
            detail = journal.read().decode("utf-8", "replace").strip()
            if proc.returncode != 0:
                raise SystemExit(f"Échec de {quoi} (code {proc.returncode}) :\n{detail[-2000:]}")
    if incidents:
        raise SystemExit("Échec : " + incidents[0])
    if lues == 0:
        raise SystemExit("Aucune image lue dans la vidéo.")

    ecoule = time.time() - debut
    taille_mo = os.path.getsize(sortie) / 1e6
    print(f"  ✅ Terminé en {fmt_duree(ecoule)} : {lues} images lues, {etat['produites']} produites.")
    mo = f"{taille_mo:.1f}".replace(".", ",")
    print(f"  {sortie} ({mo} Mo)")
    return sortie


if __name__ == "__main__":
    principal()
