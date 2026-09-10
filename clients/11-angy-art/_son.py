# -*- coding: utf-8 -*-
"""
ANGY ART — l'ambiance musicale du site : elle s'encode ici, et elle se MESURE ici.

Le morceau reçu de Mongazi (jazz lofi, « iced coffee », Tama's Little Music Shop)
pèse 2,16 Mo. Tel quel, il pèserait plus lourd que tout le reste du site réuni sur
la 3G de Cotonou. Ce script fabrique le fichier qui part en ligne — et surtout il
mesure ce qu'il vient de fabriquer : personne ici ne peut ÉCOUTER le résultat,
donc tout ce qui se juge d'ordinaire à l'oreille doit se lire en chiffres.

    python _son.py             # encode, puis mesure
    python _son.py --mesurer   # mesure seulement, n'écrit rien

⚠️ IDEMPOTENT : on repart TOUJOURS de `_sources/musique-source.mp3`. Ré-encoder
   un MP3 déjà encodé le dégrade un peu plus à chaque passage, et c'est le genre
   de perte que personne n'entend venir.

⚠️ LA SOURCE N'EST PAS VERSIONNÉE (`clients/*/_sources/` est ignoré, et le dépôt
   est public). Si elle disparaît, elle se redemande à Mongazi : le fichier
   encodé ne peut pas la remplacer.

LE « TAMISÉ » EST CUIT DANS LE FICHIER, pas joué par le navigateur. C'est ce qui
permet de garder un `<audio>` nu — donc de rester audible sur un iPhone en mode
silencieux, où Web Audio est muet (leçon du 2026-05-25) :

  · `lowpass=3200` feutre les cymbales et le souffle. ⛔ PAS 950 Hz : la leçon
    Luxury Club dit qu'une coupure basse rend la musique INAUDIBLE sur un
    haut-parleur de téléphone, qui ne reproduit pas les graves où tout le
    contenu s'est alors réfugié.
    ⚠️ N'EMPILE PAS LES LOWPASS. Mesuré ici : un seul filtre à 3200 Hz creuse
    l'aigu de 2,0 dB, trois filtres de 2,3 dB. La source est du lofi — elle n'a
    presque rien au-dessus de 4 kHz, et un filtre ne retire pas ce qui n'est pas
    là. LE TAMISÉ VIENT DU NIVEAU (-17 LUFS et le volume de lecture), le filtre
    ne fait que retirer le souffle.
  · `highpass=80` retire des infra-graves que personne n'entend et qui coûtent
    des bits à chaque seconde.
  · `loudnorm I=-11` aligne la SONIE PERÇUE, pas le pic.
    ⛔ **UNE PREMIÈRE VERSION VISAIT -17, ET MONGAZI N'ENTENDAIT « QU'UN BRUIT
    TOUT BAS ».** L'erreur : atténuer DEUX FOIS, dans le fichier puis au volume
    de lecture. Mesuré : -17,4 LUFS x 0,34 = **-26,8 LUFS entendus**, quand le
    site de l'agence — la référence qu'il donne — sort à **-18,0** (son fichier
    est BRUT, à -8,9, et n'est atténué que par le volume).
    ⚠️ **LE TAMISÉ SE FAIT AU VOLUME DE LECTURE, PAS DANS LE FICHIER** : le
    volume se règle en une ligne et s'entend tout de suite ; un fichier trop
    bas se ré-encode et ne se rattrape jamais vraiment.
    -11 laisse de la marge de crête sans rien perdre de la présence.
  · mono, 32 kHz, 48 kb/s : le format de la maison (`benin-mon-pays/_sons_finir.py`).
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import wave

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ICI, "_sources", "musique-source.mp3")
SORTIE = os.path.join(ICI, "assets", "sons", "ambiance.mp3")

LOWPASS = 3600      # Hz — le feutrage, léger
HIGHPASS = 80       # Hz — les infra-graves
LUFS = -11          # la sonie visée
DEBIT = "48k"
ECHANT = "32000"
CROISE = 2.0        # s — le fondu croisé qui referme la boucle

# Le raccord de boucle est propre sous cet écart (règle maison, wavespeed-audio).
SEUIL_RACCORD = 0.35
POIDS_MAX = 1024 * 1024      # la cible du README maison : moins de 1 Mo


def ffmpeg():
    """Le binaire. ⚠️ `apt-get install ffmpeg` échoue dans le conteneur (index
    apt périmé, 404 sur libva/mesa) : c'est `pip install imageio-ffmpeg` qui
    fournit un binaire statique complet."""
    for essai in ("ffmpeg", "/usr/local/bin/ffmpeg"):
        try:
            subprocess.run([essai, "-version"], capture_output=True, check=True)
            return essai
        except Exception:
            pass
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("  ffmpeg introuvable : pip install imageio-ffmpeg")


FF = None


def lancer(args):
    return subprocess.run([FF, "-hide_banner", "-nostdin"] + args,
                          capture_output=True, text=True, errors="replace")


# ── les mesures ──────────────────────────────────────────────────────────────

def entete_mp3(chemin):
    """Durée, débit et canaux LUS DANS LES TRAMES, sans faire confiance au tag.
    Un tag ID3 peut annoncer n'importe quoi ; les trames, elles, sont le son."""
    d = open(chemin, "rb").read()
    i = 0
    tag = 0
    if d[:3] == b"ID3":
        tag = (d[6] & 0x7F) << 21 | (d[7] & 0x7F) << 14 | (d[8] & 0x7F) << 7 | (d[9] & 0x7F)
        i = 10 + tag
    BR = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    SR = [44100, 48000, 32000]
    n = 0
    duree = 0.0
    canaux = "?"
    while i < len(d) - 4:
        if d[i] == 0xFF and (d[i + 1] & 0xE0) == 0xE0:
            ver, lay = (d[i + 1] >> 3) & 3, (d[i + 1] >> 1) & 3
            bi, si, pad = (d[i + 2] >> 4) & 0xF, (d[i + 2] >> 2) & 3, (d[i + 2] >> 1) & 1
            if ver == 3 and lay == 1 and bi not in (0, 15) and si != 3:
                if not n:
                    canaux = "mono" if ((d[i + 3] >> 6) & 3) == 3 else "stéréo"
                duree += 1152.0 / SR[si]
                n += 1
                i += int(144 * BR[bi] * 1000 / SR[si]) + pad
                continue
        i += 1
    audio = len(d) - (10 + tag if tag else 0)
    return {
        "octets": len(d), "tag": tag, "duree": duree, "canaux": canaux,
        "debit": (audio * 8 / duree / 1000) if duree else 0,
    }


def sonie(chemin):
    """La sonie perçue en LUFS (EBU R128), par la passe d'analyse de loudnorm."""
    r = lancer(["-i", chemin, "-af", "loudnorm=I=%d:TP=-2:LRA=11:print_format=json" % LUFS,
                "-f", "null", "-"])
    m = re.findall(r"\{[^{}]*input_i[^{}]*\}", r.stderr, re.S)
    if not m:
        return None
    try:
        return float(json.loads(m[-1])["input_i"])
    except Exception:
        return None


def pcm(chemin):
    """Décode en PCM 16 bits mono pour mesurer le signal lui-même."""
    tmp = tempfile.mktemp(suffix=".wav")
    lancer(["-y", "-i", chemin, "-ac", "1", "-ar", "32000", "-f", "wav", tmp])
    with wave.open(tmp, "rb") as w:
        n, sr = w.getnframes(), w.getframerate()
        brut = w.readframes(n)
    os.unlink(tmp)
    return struct.unpack("<%dh" % (len(brut) // 2), brut), sr


def rms(ech):
    if not ech:
        return 0.0
    return (sum(float(v) * v for v in ech) / len(ech)) ** 0.5


def raccord(chemin):
    """LA BOUCLE SE RECOLLE-T-ELLE ? Règle de la maison : on compare l'énergie
    des 40 PREMIÈRES millisecondes à celle des 40 DERNIÈRES. Sous 35 % d'écart,
    le raccord ne s'entend pas. C'est le seul contrôle qui dise si une boucle de
    deux minutes claquera toutes les deux minutes."""
    ech, sr = pcm(chemin)
    n = int(sr * 0.040)
    a, b = rms(ech[:n]), rms(ech[-n:])
    if max(a, b) == 0:
        return {"debut": a, "fin": b, "ecart": 0.0}
    return {"debut": a, "fin": b, "ecart": abs(a - b) / max(a, b)}


def bornes(chemin):
    """OÙ COMMENCE ET OÙ FINIT LA MUSIQUE — pas le fichier.

    ⚠️ Un morceau de vlog porte presque toujours un silence de tête et un FONDU
       DE SORTIE. Ici : 77 ms de silence, puis un fondu qui commence à 116 s et
       descend à -42 dB. Mis en boucle tel quel, le site s'éteindrait pendant
       quatre secondes puis repartirait d'un coup, toutes les deux minutes.

    ⚠️ CE DÉFAUT NE SE VOIT PAS DANS LE DÉBIT. Un premier examen comparait la
       taille des trames MP3 (leur complexité) et concluait « aucun fondu » : la
       complexité reste haute quand le niveau s'effondre. On mesure le NIVEAU.

    Le seuil est RELATIF à la médiane du morceau, pas absolu : un morceau plus
    doux ne doit pas être rogné jusqu'à l'os."""
    ech, sr = pcm(chemin)
    pas = int(sr * 0.25)
    prof = [rms(ech[i:i + pas]) for i in range(0, len(ech) - pas, pas)]
    if not prof:
        return 0.0, len(ech) / float(sr)
    seuil = sorted(prof)[len(prof) // 2] * 0.45          # -7 dB sous la médiane
    d = next((i for i, v in enumerate(prof) if v > seuil), 0)
    f = len(prof) - next((i for i, v in enumerate(reversed(prof)) if v > seuil), 0)
    return d * pas / float(sr), f * pas / float(sr)


def bandes(chemin):
    """L'énergie par bande de fréquence. C'est ce qui prouve que le feutrage a
    retiré le brillant SANS vider le médium où vit le piano — la différence
    entre « tamisé » et « étouffé », qui ne se voit pas dans un poids de fichier.

    ⚠️ LA COMPARAISON SE FAIT À NIVEAU ÉGAL. Un premier jet comparait les dB
       bruts : la normalisation baisse tout de 9 dB, donc toutes les bandes
       chutaient d'autant et la mesure disait « le grave aussi a été filtré ».
       Elle mesurait la normalisation, pas le filtre. On retranche la sonie de
       chaque fichier avant de comparer."""
    out = {}
    for centre in (100, 200, 400, 800, 1600, 3200, 6400):
        r = lancer(["-i", chemin, "-af",
                    "bandpass=f=%d:width_type=o:w=1,volumedetect" % centre,
                    "-f", "null", "-"])
        m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
        out[centre] = float(m.group(1)) if m else None
    return out


# ── l'encodage ───────────────────────────────────────────────────────────────

def encoder():
    """LA BOUCLE EST UNE PROPRIÉTÉ DU FICHIER, pas une acrobatie du navigateur.

    On rogne le silence et le fondu de sortie, puis on referme le morceau sur
    lui-même par un fondu croisé : les deux dernières secondes viennent se poser
    sur les deux premières. Le fichier peut alors tourner en `loop` natif sans
    qu'on entende jamais la couture, et le JavaScript de la page reste une
    balise `<audio loop>` — rien à maintenir.

    ⚠️ `amix` DIVISE par le nombre d'entrées : sans `normalize=0`, le passage
       croisé sortirait 6 dB sous le reste, ce qui s'entend comme un creux.
    ⚠️ Les fondus sont en `qsin` (quart de sinus), pas linéaires : deux rampes
       linéaires qui se croisent laissent un trou de 3 dB au milieu, parce que
       c'est la PUISSANCE qui s'additionne, pas l'amplitude."""
    if not os.path.exists(SOURCE):
        raise SystemExit("  source absente : %s\n  (elle n'est pas versionnée, "
                         "il faut la redemander à Mongazi)" % SOURCE)
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)

    d, f = bornes(SOURCE)
    utile = f - d
    if utile < 3 * CROISE:
        raise SystemExit("  le morceau utile est trop court (%.1f s)" % utile)
    corps = utile - CROISE          # ce que dure le fichier final
    print("  musique utile : %.2f s -> %.2f s  (silence de tête %.0f ms, "
          "fondu de sortie rogné %.1f s)"
          % (d, f, d * 1000, _duree_source() - f))

    graphe = (
        "[0:a]atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS,"
        "highpass=f=%d,lowpass=f=%d[u];"
        "[u]asplit=2[a][b];"
        "[a]atrim=0:%.4f,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=%.3f:curve=qsin[c];"
        "[b]atrim=%.4f,asetpts=PTS-STARTPTS,afade=t=out:st=0:d=%.3f:curve=qsin,"
        "adelay=0|0[q];"
        "[c][q]amix=inputs=2:duration=first:normalize=0[m];"
        "[m]loudnorm=I=%d:TP=-2:LRA=11[out]"
        % (d, f, HIGHPASS, LOWPASS, corps, CROISE, corps, CROISE, LUFS)
    )
    r = lancer(["-y", "-i", SOURCE, "-filter_complex", graphe, "-map", "[out]",
                "-ac", "1", "-ar", ECHANT, "-b:a", DEBIT,
                "-map_metadata", "-1", SORTIE])
    if r.returncode != 0 or not os.path.exists(SORTIE):
        raise SystemExit("  l'encodage a échoué :\n" + r.stderr[-1800:])
    print("  encodé -> assets/sons/ambiance.mp3  (%.2f s, fondu croisé %.1f s)"
          % (corps, CROISE))


def _duree_source():
    return entete_mp3(SOURCE)["duree"]


def mesurer():
    if not os.path.exists(SORTIE):
        raise SystemExit("  rien à mesurer : lance `python _son.py` d'abord.")

    src = entete_mp3(SOURCE) if os.path.exists(SOURCE) else None
    fin = entete_mp3(SORTIE)

    print("\n== Le fichier")
    if src:
        print("  source  : %.1f s · %s · %.0f kb/s · %d Ko"
              % (src["duree"], src["canaux"], src["debit"], src["octets"] // 1024))
    print("  en ligne: %.1f s · %s · %.0f kb/s · %d Ko"
          % (fin["duree"], fin["canaux"], fin["debit"], fin["octets"] // 1024))
    if src:
        print("  gain    : %d Ko en moins (%.0f %%)"
              % ((src["octets"] - fin["octets"]) // 1024,
                 100.0 * (src["octets"] - fin["octets"]) / src["octets"]))
    print("  %s cible du README maison : moins de 1 Mo"
          % ("[ok]" if fin["octets"] < POIDS_MAX else "[KO]"))
    if src:
        perdu = src["duree"] - fin["duree"]
        print("  rogné   : %.1f s (le silence de tête, le fondu de sortie, "
              "et les %.1f s du fondu croisé)" % (perdu, CROISE))
        print("  %s on n'a pas mangé de musique (moins de 10 s retirées)"
              % ("[ok]" if perdu < 10 else "[KO]"))

    print("\n== La sonie perçue")
    if src:
        s = sonie(SOURCE)
        print("  source   : %s LUFS" % ("%.1f" % s if s is not None else "?"))
    f = sonie(SORTIE)
    print("  en ligne : %s LUFS (visé %d)" % ("%.1f" % f if f is not None else "?", LUFS))
    if f is not None:
        ok = abs(f - LUFS) <= 1.5
        print("  %s la normalisation a tenu" % ("[ok]" if ok else "[KO]"))

    print("\n== Le raccord de boucle  (40 ms de début contre 40 ms de fin)")
    r = raccord(SORTIE)
    print("  début %.0f · fin %.0f · écart %.1f %%"
          % (r["debut"], r["fin"], 100 * r["ecart"]))
    if r["ecart"] < SEUIL_RACCORD:
        print("  [ok] sous %.0f %% : la boucle se recolle sans qu'on l'entende"
              % (100 * SEUIL_RACCORD))
    else:
        print("  [KO] au-dessus de %.0f %% : il faudra deux éléments en fondu croisé"
              % (100 * SEUIL_RACCORD))

    print("\n== Le feutrage, bande par bande  (dB, À NIVEAU ÉGAL)")
    bs, bf = (bandes(SOURCE) if src else {}), bandes(SORTIE)
    ss, sf = (sonie(SOURCE) if src else None), sonie(SORTIE)
    print("  %-8s %10s %10s %10s" % ("Hz", "source", "en ligne", "écart"))
    ecarts = {}
    for c in sorted(bf):
        a, b = bs.get(c), bf[c]
        if a is None or b is None or ss is None or sf is None:
            d = "?"
        else:
            # on retranche la sonie de chaque fichier : sinon on mesure la
            # normalisation (-9 dB sur TOUT) au lieu du filtre
            ecarts[c] = (b - sf) - (a - ss)
            d = "%+.1f" % ecarts[c]
        print("  %-8d %10s %10s %10s"
              % (c, "%.1f" % a if a is not None else "?",
                 "%.1f" % b if b is not None else "?", d))
    if 6400 in ecarts and 1600 in ecarts:
        print("  le filtre a retire %.1f dB de brillant"
              % (ecarts[1600] - ecarts[6400]))
    # CE QUI COMPTE EST LA PROPRIETE DU FICHIER LIVRE, PAS L'ACTION DU FILTRE.
    # Le 2026-09-10, le morceau WETHU a fait rougir ce controle en etant DEJA
    # sombre : dans la SOURCE son 6400 Hz est 10,8 dB sous le medium, donc le
    # filtre n'avait presque rien a retirer et son action mesurait 0,4 dB.
    # « Un filtre ne retire pas ce qui n'est pas la » est ecrit plus haut dans
    # ce fichier. Un controle qui exige une ACTION punit une source deja
    # feutree, et laisse passer une source criarde a peine adoucie : les deux
    # erreurs a la fois. On mesure donc ce que la visiteuse entendra.
    if 6400 in bf and 1600 in bf:
        recul = bf[1600] - bf[6400]
        print("  dans le fichier livre, le brillant est %.1f dB sous le medium"
              % recul)
        print("  %s le fichier est feutre" % ("[ok]" if recul > 6.0 else
              "[KO] trop brillant pour une ambiance de fond :"))


if __name__ == "__main__":
    FF = ffmpeg()
    if "--mesurer" not in sys.argv:
        encoder()
    mesurer()
