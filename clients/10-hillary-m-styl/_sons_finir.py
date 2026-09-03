# -*- coding: utf-8 -*-
"""Vérifie, coupe et allège les six sons d'atelier.

Trois contrôles obligatoires sur tout son généré (leçon du 2026-08-10) :
  1. sont-ils VRAIMENT différents ? (MD5 + profil spectral)
  2. l'attaque est-elle nette ? (pas de silence en tête)
  3. les niveaux sont-ils alignés ?

⚠️ Ici ce sont des sons PONCTUELS, pas des ambiances : on coupe le silence
avant et après, sinon un déclenchement rapide laisse un blanc audible, et
on paie du poids pour du vide.
"""
import io
import os
import subprocess
import wave

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ICI = os.path.dirname(os.path.abspath(__file__))
BRUT = os.path.join(ICI, "_sources", "sons_bruts")
SONS = os.path.join(ICI, "assets", "sons")
TMP = os.path.join(ICI, "_sources", "_tmp_son")

NOMS = ["ouvrir", "fiche", "mesure", "etape", "couper", "envoyer"]

# ⚠️ Le seuil est RELATIF au pic du son, pas absolu. Avec un seuil absolu,
# le souffle qui précède l'attaque était pris pour le début : « etape » et
# « fiche » démarraient à 70 % et 60 % de leur durée, donc le son arrivait
# un tiers de seconde après le clic. Mesuré le 2026-08-11.
PART = 0.14            # on commence quand le signal atteint 14 % du pic
QUEUE = 0.03           # ... et on finit quand il retombe sous 3 %
CREUX = 0.09           # 90 ms de calme = l'evenement est fini
CIBLE = 0.72           # pic vise, soit environ -3 dBFS

# ⚠️ DUREE MINIMALE. Le MP3 encode par trames et ajoute un delai en tete
# d'environ 30 ms : un extrait de 70 ms se retrouve presque entierement
# mange, et le fichier sort MUET tout en pesant 900 octets. Quatre sons
# sur six sont sortis silencieux avant qu'on le mesure (2026-08-11).
# On prolonge donc la QUEUE, jamais le debut : la latence au clic doit
# rester nulle.
MINI = 0.30


def lire(p):
    os.makedirs(TMP, exist_ok=True)
    w = os.path.join(TMP, "x.wav")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error",
                    "-i", p, "-ac", "1", "-ar", "44100", w], check=True)
    with wave.open(w, "rb") as h:
        n, sr = h.getnframes(), h.getframerate()
        d = h.readframes(n)
    ech = [int.from_bytes(d[i:i + 2], "little", signed=True) / 32768.0
           for i in range(0, len(d), 2)]
    return ech, sr


def bornes(ech, sr):
    """Ou commence et finit L'EVENEMENT PRINCIPAL.

    ⚠️ On ne coupe PAS au premier bruit : les fichiers generes contiennent
    souvent un blip discret, puis un silence, puis le vrai son. En coupant
    au premier bruit, « fiche » demarrait encore a 50 % de sa duree.
    On part donc du PIC et on remonte tant que le signal reste vivant,
    en tolerant les micro-creux (une machine a coudre fait plusieurs points).
    """
    n = len(ech)
    if not n:
        return 0, 0
    abso = [abs(x) for x in ech]
    pic = max(abso)
    if pic <= 0:
        return 0, n

    ipic = abso.index(pic)
    sd, sf = pic * PART, pic * QUEUE
    creux = int(sr * CREUX)

    # en arriere depuis le pic
    deb, vide = ipic, 0
    for i in range(ipic, -1, -1):
        if abso[i] > sd:
            deb, vide = i, 0
        else:
            vide += 1
            if vide > creux:
                break
    deb = max(0, deb - int(sr * 0.006))   # 6 ms d'elan avant l'attaque

    # en avant depuis le pic
    fin, vide = ipic, 0
    for i in range(ipic, n):
        if abso[i] > sf:
            fin, vide = i, 0
        else:
            vide += 1
            if vide > creux:
                break
    fin = min(n, fin + int(sr * 0.04))
    return deb, fin


def spectre(ech):
    """Signature grossiere : energie haute frequence par tiers."""
    out = []
    t = max(1, len(ech) // 3)
    for b in range(3):
        seg = ech[b * t:(b + 1) * t]
        if len(seg) < 2:
            out.append(0)
            continue
        hf = sum(abs(seg[i] - seg[i - 1]) for i in range(1, len(seg))) / (len(seg) - 1)
        out.append(round(hf * 1000))
    return out


if __name__ == "__main__":
    os.makedirs(SONS, exist_ok=True)
    print("%-10s %8s %8s %7s %7s  %s"
          % ("SON", "BRUT", "FINAL", "DUREE", "PIC", "SPECTRE"))
    print("-" * 68)

    profils, total = {}, 0
    for nom in NOMS:
        src = os.path.join(BRUT, nom + ".mp3")
        if not os.path.exists(src):
            print("%-10s absent" % nom)
            continue
        ech, sr = lire(src)
        d, f = bornes(ech, sr)
        util = ech[d:f]
        pic = max(abs(x) for x in util) if util else 0

        # on allonge par la FIN si c'est trop court pour le MP3
        if (f - d) / float(sr) < MINI:
            f = min(len(ech), d + int(sr * MINI))
        duree = max(MINI, (f - d) / float(sr))

        # ⚠️ ON COUPE SUR LES ECHANTILLONS, EN PYTHON, jamais avec `-ss`.
        # Place apres `-i`, la coupe laisse le graphe de filtres sur la
        # timeline du fichier ENTIER : `afade=t=out:st=0.27` eteignait le
        # son a 270 ms du debut du source alors que le coup de ciseaux
        # etait a 680 ms, et trois sons sur six sortaient parfaitement
        # muets avec un poids normal. Place AVANT `-i`, la coupe tombe sur
        # la trame MP3 la plus proche, donc a quelques dizaines de
        # millisecondes pres, et l'attaque se decale.
        # Sur les echantillons, il n'y a plus aucune approximation.
        gain = CIBLE / pic if pic > 0 else 1.0
        nf = int(sr * duree)
        bloc = list(util) + [0.0] * max(0, nf - len(util))
        bloc = bloc[:nf]

        fade = max(0.005, min(0.03, duree * 0.12))
        nfade = int(sr * fade)
        for i in range(nfade):
            k = len(bloc) - nfade + i
            if 0 <= k < len(bloc):
                bloc[k] *= (1.0 - i / float(nfade))

        os.makedirs(TMP, exist_ok=True)
        w = os.path.join(TMP, "coupe.wav")
        with wave.open(w, "wb") as h:
            h.setnchannels(1)
            h.setsampwidth(2)
            h.setframerate(sr)
            h.writeframes(b"".join(
                int(max(-1.0, min(1.0, v * gain)) * 32767).to_bytes(
                    2, "little", signed=True) for v in bloc))

        dst = os.path.join(SONS, nom + ".mp3")
        subprocess.run([
            FF, "-y", "-hide_banner", "-loglevel", "error", "-i", w,
            "-ac", "1", "-ar", "32000", "-b:a", "48k", dst], check=True)

        t = os.path.getsize(dst)
        total += t
        profils[nom] = spectre(util)
        print("%-10s %7d o %7d o %6.2fs %6.2f  %s"
              % (nom, os.path.getsize(src), t, duree, pic, profils[nom]))

    print("\ntotal : %d sons, %.1f Ko" % (len(profils), total / 1024.0))

    # sont-ils vraiment differents ? deux sons identiques = un lot rate
    print("\nsons trop proches deux a deux :")
    n = list(profils)
    souci = 0
    for i in range(len(n)):
        for j in range(i + 1, len(n)):
            a, b = profils[n[i]], profils[n[j]]
            base = max(1, sum(a) / 3.0)
            ec = sum(abs(x - y) for x, y in zip(a, b)) / 3.0
            if ec / base < 0.05:
                souci += 1
                print("  ! %s et %s (%.1f %%)" % (n[i], n[j], ec / base * 100))
    print("  aucun" if not souci else "")
