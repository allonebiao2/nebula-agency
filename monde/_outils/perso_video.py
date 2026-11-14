"""LE MONDE · une vidéo de personnage → un personnage-vidéo du salon (détouré, stable, en boucle, lisible partout).

    python monde/_outils/perso_video.py <source.mp4> <sortie sans extension> [--debut 0] [--fin 7.6]
           [--hauteur 960] [--boucle allerretour|directe] [--modele isnet-general-use]

    ex. python monde/_outils/perso_video.py "_partage/immersive  store 3D/personnages/afi/videos/afi-parler.mp4" \\
            monde/lieux/hillary-m-styl/personnages/afi/video-parler --fin 7.6

Mongazi (2026-11-14) : « comment faire pour que ce soit ultra réaliste ? », « pour les visages, comment se
rapprocher le maximum possible ? ». Ses vidéos sont photoréalistes, c'est le passage en 3D qui les détruisait :
en conversation, le salon montre la vidéo elle-même (`socle/perso-video.js`).

Ce que fait l'outil, dans l'ordre :
1. les images du passage choisi, à la hauteur voulue ;
2. le détourage de chaque image (rembg) ;
3. le détourage LISSÉ dans le temps (médiane sur 3 images) : un bord qui scintille trahit le montage ;
4. le gris du fond retiré des bords (la couleur vraie retrouvée sous le mélange avec le fond) ;
5. le cadre STABILISÉ : la taille de la personne (tête → pieds) et la place de ses pieds tenues constantes (les
   générateurs zooment doucement : 2 % en 7 s sur `afi-parler`) ;
6. la boucle : aller-retour (une vidéo dont la fin ne rejoint pas le début), ou directe (première = dernière image) ;
7. l'encodage : couleur à GAUCHE, opacité à DROITE, dans une seule vidéo H.264 (le seul format à transparence
   que lisent aussi les iPhone ; le WebM transparent n'y passe pas) + `<sortie>.json` (cadre, pieds, tête).

⚠️ Ce PC a peu de mémoire : les images passent par le disque, jamais toutes en mémoire.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def detourer_fond_uni(rgb: np.ndarray, s0: float = 12.0, s1: float = 40.0) -> np.ndarray:
    """Le détourage d'un sujet devant un FOND UNI (studio), par la couleur : rapide (quelques centièmes de seconde par
    image, contre ~6 s au réseau de neurones) et PLUS FIN (les mèches, le flou de mouvement d'une main gardent leur
    transparence vraie). Le fond est une surface lisse ajustée sur ce qui est sûrement du fond (les studios ont un
    léger dégradé) ; est « fond » ce qui lui ressemble ET touche le bord de l'image, plus les trous fermés assez
    grands (entre un bras et le corps). Les petits éclats clairs DANS le sujet (bijoux, dents) restent opaques.
    ⚠️ Réservé aux vidéos sans sol visible (un buste) : un sol et son ombre de contact ne sont pas un fond uni."""
    import cv2
    a = rgb.astype(np.float32); H, W = a.shape[:2]
    bord = np.concatenate([a[:8].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    med = np.median(bord, axis=0)
    d0 = np.sqrt(((a - med) ** 2).sum(axis=2))
    n, lab = cv2.connectedComponents((d0 < 30).astype(np.uint8), connectivity=4)
    b = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); b = b[b != 0]
    sur = np.isin(lab, b)
    # la surface du fond : un polynôme du 2e degré par canal, ajusté sur le fond sûr (un pixel sur 3)
    ys, xs = np.nonzero(sur[::3, ::3]); ys = ys * 3; xs = xs * 3
    if len(ys) < 200:
        return np.full((H, W), 255, np.uint8)
    base = lambda x, y: np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], axis=-1)
    X = base(xs / W * 2 - 1.0, ys / H * 2 - 1.0).astype(np.float32)
    coef, *_ = np.linalg.lstsq(X, a[ys, xs], rcond=None)
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
    fond = base(gx / W * 2 - 1.0, gy / H * 2 - 1.0) @ coef
    d = np.sqrt(((a - fond) ** 2).sum(axis=2))
    n, lab, stats, _ = cv2.connectedComponentsWithStats((d < s1).astype(np.uint8), connectivity=4)
    b = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); b = b[b != 0]
    region = np.isin(lab, b)
    # les trous fermés : assez grands, et vraiment couleur de fond
    for k in range(1, n):
        if k in b or stats[k, cv2.CC_STAT_AREA] < 40: continue   # plus petit : un bijou, une dent (ils restent opaques)
        m = lab == k
        if float(d[m].mean()) < s0 + 4: region |= m
    alpha = np.where(region, np.clip((d - s0) / (s1 - s0), 0.0, 1.0), 1.0).astype(np.float32)
    # un voile faible LOIN du sujet (un coin plus sombre du studio) n'est pas le sujet : on ne garde la demi-transparence
    # qu'à moins de 18 px d'une partie pleine (le flou de mouvement d'une main, le bord d'une mèche)
    plein = cv2.dilate((alpha > 0.6).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (37, 37)))
    alpha = np.where(plein > 0, alpha, 0.0).astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.6)
    return (alpha * 255).astype(np.uint8)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("source"); ap.add_argument("sortie")
    ap.add_argument("--debut", type=float, default=0.0); ap.add_argument("--fin", type=float, default=None)
    ap.add_argument("--hauteur", type=int, default=960)
    ap.add_argument("--boucle", choices=["allerretour", "directe"], default="allerretour")
    ap.add_argument("--modele", default="isnet-general-use")
    ap.add_argument("--qualite", type=int, default=24, help="CRF H.264 (plus bas = plus lourd)")
    ap.add_argument("--garder", action="store_true", help="garder le dossier de travail (pour regarder)")
    ap.add_argument("--calme", type=float, default=None, help="garder seulement le passage de N secondes où le VISAGE bouge le moins (« écouter » tiré d'une vidéo « parler »)")
    ap.add_argument("--pas", type=int, default=1, help="détourer une image sur N et interpoler les autres (2 = deux fois plus vite ; réservé aux vidéos CALMES : sur un geste rapide, le bord d'une main dédoublerait)")
    ap.add_argument("--plage", default=None, help="garder seulement ce passage, choisi À L'ŒIL : « 4.8-7.4 » (secondes dans le passage extrait). Quand --calme se trompe (Maman : son passage le plus calme contient un geste des mains)")
    ap.add_argument("--vitesse", type=float, default=None, help="vitesse de lecture dans le salon (ex. 0.85 : un peu ralenti)")
    ap.add_argument("--fond-uni", action="store_true", help="détourer par la couleur du fond (studio uni, sans sol visible : un buste) : des centaines de fois plus rapide et plus fin que le réseau de neurones")
    ap.add_argument("--buste", type=float, default=None, help="vidéo en BUSTE (le bas du corps est coupé par le cadre, ex. Hillary derrière son comptoir) : la hauteur RÉELLE du cadre, en mètres. Pas de stabilisation ; le plan est ancré sur le sommet de la tête")
    ap.add_argument("--tete-m", type=float, default=None, help="avec --buste : la hauteur réelle du sommet de la tête (sa taille), en mètres")
    ap.add_argument("--fondu-bas", type=float, default=0.08, help="avec --buste : le bas de l'image se fond sur cette fraction de sa hauteur")
    ap.add_argument("--reprendre", default=None, help="un dossier de travail déjà détouré (gardé par --garder ou laissé par une coupure) : on repart de ses masques")
    a = ap.parse_args()

    src, sortie = Path(a.source), Path(a.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    travail = Path(a.reprendre) if a.reprendre else Path(tempfile.mkdtemp(prefix="perso_video_"))
    for d in ("img", "masque", "fini"): (travail / d).mkdir(exist_ok=True)
    for f in list((travail / "masque").glob("l_*.png")) + list((travail / "fini").glob("*.png")): f.unlink()
    deja = a.reprendre and len(list((travail / "img").glob("i_*.png"))) == len(list((travail / "masque").glob("i_*.png"))) > 0
    if a.reprendre: a.garder = True   # on ne détruit pas un travail qu'on reprend
    try:
        # 1 · les images
        duree = ["-t", str(a.fin - a.debut)] if a.fin else []
        if not deja:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.debut), "-i", str(src), *duree,
                            "-vf", f"scale=-2:{a.hauteur}:flags=lanczos", str(travail / "img" / "i_%04d.png")], check=True)
        sonde = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                           "-of", "json", str(src)], capture_output=True, text=True, check=True).stdout)
        num, den = sonde["streams"][0]["r_frame_rate"].split("/"); ips = float(num) / float(den)
        images = sorted((travail / "img").glob("i_*.png"))
        print(f"{len(images)} images à {ips:g} i/s")

        if a.plage:
            d_, f_ = (float(x) for x in a.plage.split("-")); i0, i1 = int(round(d_ * ips)), int(round(f_ * ips))
            images = images[i0:i1]; a.fin = round(a.debut + f_, 3); a.debut = round(a.debut + d_, 3)
            print(f"passage choisi : images {i0}-{i1 - 1} ({d_:g} s à {f_:g} s)")

        # 1 bis · le passage le plus calme (--calme) : là où le visage bouge le moins d'une image à l'autre. On ne
        # détoure qu'une image pour savoir où est la tête (le haut de la personne), puis on mesure le mouvement brut.
        if a.calme:
            n = max(8, int(round(a.calme * ips)))
            m0 = travail / "masque" / images[0].name
            if not m0.exists():
                from rembg import new_session, remove
                remove(Image.open(images[0]).convert("RGB"), session=new_session(a.modele), only_mask=True).save(m0)
            al = np.asarray(Image.open(m0), dtype=np.uint8); ys, xs = np.where(al > 128)
            haut, bas = ys.min(), ys.max(); h = bas - haut
            y0, y1 = haut, haut + int(h * 0.16)
            x0, x1 = int(np.percentile(xs[ys < y1], 2)), int(np.percentile(xs[ys < y1], 98))
            # le VISAGE (elle ne parle pas) ET le CORPS entier (ses mains ne font pas de grands gestes) : une personne qui
            # écoute ne lève pas les bras. ⚠️ Le visage seul choisissait, chez Maman, un passage où ses mains montent.
            bx0, bx1 = max(0, int(xs.min()) - 40), min(al.shape[1], int(xs.max()) + 40)
            gris = [np.asarray(Image.open(f).convert("L"), dtype=np.float32) for f in images]
            mouv = np.array([0.0] + [float(np.abs(gris[i][y0:y1, x0:x1] - gris[i - 1][y0:y1, x0:x1]).mean())
                                     + 2.0 * float(np.abs(gris[i][haut:bas, bx0:bx1] - gris[i - 1][haut:bas, bx0:bx1]).mean()) for i in range(1, len(gris))])
            cumul = np.concatenate([[0.0], np.cumsum(mouv)])
            debut = int(np.argmin([cumul[i + n] - cumul[i + 1] for i in range(0, len(images) - n + 1)]))
            print(f"passage calme : images {debut}-{debut + n - 1} ({debut / ips:.2f} s à {(debut + n - 1) / ips:.2f} s), "
                  f"mouvement moyen {mouv[debut + 1:debut + n].mean():.2f} contre {mouv[1:].mean():.2f} sur toute la vidéo")
            images = images[debut:debut + n]
            a.debut, a.fin = round(a.debut + debut / ips, 3), round(a.debut + (debut + n) / ips, 3)
            del gris

        # 2 · le détourage (sauté si on reprend un travail déjà détouré)
        deja = deja or all((travail / "masque" / f.name).exists() for f in images)
        if a.fond_uni and not deja:
            for k, f in enumerate(images):
                Image.fromarray(detourer_fond_uni(np.asarray(Image.open(f).convert("RGB")))).save(travail / "masque" / f.name)
            print(f"  détourage par la couleur du fond : {len(images)} images", flush=True)
        elif not deja:
            from rembg import new_session, remove
            session = new_session(a.modele)
            cles = [k for k in range(len(images)) if k % a.pas == 0 or k == len(images) - 1]
            for n_, k in enumerate(cles):
                f = images[k]
                if (travail / "masque" / f.name).exists(): continue
                m = remove(Image.open(f).convert("RGB"), session=session, only_mask=True)
                m.save(travail / "masque" / f.name)
                if n_ % 20 == 0: print(f"  détourage {n_ + 1}/{len(cles)}", flush=True)
            del session
            # les images entre deux clés : le masque interpolé (mélange des deux voisins détourés)
            for i in range(len(cles) - 1):
                k0, k1 = cles[i], cles[i + 1]
                if k1 - k0 < 2: continue
                m0 = np.asarray(Image.open(travail / "masque" / images[k0].name), dtype=np.float32)
                m1 = np.asarray(Image.open(travail / "masque" / images[k1].name), dtype=np.float32)
                for k in range(k0 + 1, k1):
                    w = (k - k0) / (k1 - k0)
                    Image.fromarray(((1 - w) * m0 + w * m1).astype(np.uint8)).save(travail / "masque" / images[k].name)
        else:
            print("détourage repris :", travail)

        # 3 · lissé dans le temps, 5 · mesures du cadre (tête, pieds, centre) sur le masque lissé
        cadres = []
        noms = [f.name for f in images]
        lire = lambda n: np.asarray(Image.open(travail / "masque" / n), dtype=np.uint8)
        for k, n in enumerate(noms):
            if a.fond_uni:
                al = lire(n)
            else:
                pile = [lire(noms[j]) for j in (max(0, k - 1), k, min(len(noms) - 1, k + 1))]
                al = np.median(np.stack(pile), axis=0).astype(np.uint8)
            Image.fromarray(al).save(travail / "masque" / ("l_" + n))
            ys, xs = np.where(al > 128)
            cadres.append((ys.min(), ys.max(), float(np.median(xs[ys > ys.max() - 12]))) if len(ys) else None)
        valides = [c for c in cadres if c]
        if not valides: sys.exit("aucune personne trouvée dans la vidéo")
        # la taille de référence : celle de la première image ; on lisse les mesures (fenêtre de 9 images)
        haut = np.array([c[0] if c else valides[0][0] for c in cadres], dtype=float)
        bas = np.array([c[1] if c else valides[0][1] for c in cadres], dtype=float)
        cx = np.array([c[2] if c else valides[0][2] for c in cadres], dtype=float)
        lisse = lambda v: np.convolve(np.pad(v, 4, mode="edge"), np.ones(9) / 9, mode="valid")
        haut, bas, cx = lisse(haut), lisse(bas), lisse(cx)
        H0, B0, X0 = haut[0], bas[0], cx[0]

        # 4 · couleur vraie sous le mélange avec le fond, puis 5 · stabilisation, puis côte à côte
        W = Image.open(images[0]).size[0]
        H = a.hauteur
        for k, f in enumerate(images):
            rgb = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32)
            al = np.asarray(Image.open(travail / "masque" / ("l_" + f.name)), dtype=np.float32) / 255.0
            fond = np.median(np.concatenate([rgb[:12].reshape(-1, 3), rgb[:, :12].reshape(-1, 3), rgb[:, -12:].reshape(-1, 3)]), axis=0)
            a3 = al[..., None]
            vrai = np.where(a3 > 0.02, (rgb - (1 - a3) * fond) / np.maximum(a3, 0.05), rgb)
            vrai = np.clip(vrai, 0, 255)
            # échelle et décalage qui ramènent la tête et les pieds à leur place de la première image
            s = (B0 - H0) / max(1.0, bas[k] - haut[k])
            ty, tx = B0 - bas[k] * s, X0 - cx[k] * s
            if a.buste: s, ty, tx = 1.0, 0.0, 0.0   # le « bas » d'un buste est le bord du cadre : rien à stabiliser dessus
            def placer(img, mode):
                im = Image.fromarray(img)
                return im.transform((W, H), Image.AFFINE, (1 / s, 0, -tx / s, 0, 1 / s, -ty / s), resample=mode)
            couleur = placer(vrai.astype(np.uint8), Image.BICUBIC)
            opac = placer((al * 255).astype(np.uint8), Image.BILINEAR)
            # la couleur hors de la personne : neutre (elle ne sert à rien, et du gris uni se compresse mieux)
            c = np.asarray(couleur, dtype=np.uint8).copy(); o = np.asarray(opac)
            c[o < 3] = 0
            planche = Image.new("RGB", (W * 2, H))
            planche.paste(Image.fromarray(c), (0, 0)); planche.paste(Image.merge("RGB", (opac, opac, opac)), (W, 0))
            planche.save(travail / "fini" / f"f_{k:04d}.png")
        n = len(images)

        # 6 · la boucle
        if a.boucle == "allerretour":
            for j, k in enumerate(range(n - 2, 0, -1)):
                shutil.copy(travail / "fini" / f"f_{k:04d}.png", travail / "fini" / f"f_{n + j:04d}.png")
        total = len(list((travail / "fini").glob("f_*.png")))

        # 7 · l'encodage
        mp4 = sortie.with_suffix(".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{ips:g}", "-i", str(travail / "fini" / "f_%04d.png"),
                        "-c:v", "libx264", "-preset", "slow", "-crf", str(a.qualite), "-pix_fmt", "yuv420p",
                        "-profile:v", "high", "-level", "4.0", "-movflags", "+faststart", "-an", str(mp4)], check=True)
        meta = {
            "source": src.name, "debut": a.debut, "fin": a.fin, "boucle": a.boucle, "images": total, "ips": ips,
            **({"vitesse": a.vitesse} if a.vitesse else {}), **({"calme": a.calme} if a.calme else {}), **({"plage": a.plage} if a.plage else {}),
            "largeur": W, "hauteur": H,
            # en fraction de la hauteur de l'image, depuis le HAUT : où sont le sommet de la tête et la plante des pieds
            "tete": round(H0 / H, 4), "pieds": round(B0 / H, 4), "centre": round(X0 / W, 4),
            "poids_ko": round(mp4.stat().st_size / 1024),
            # un buste : la hauteur réelle du cadre, la hauteur de son bord bas au-dessus du sol (ancrée sur la tête), le fondu du bas
            **({"hauteur_m": a.buste, "bas_m": round((a.tete_m or 1.68) - (1 - H0 / H) * a.buste, 3), "fondu_bas": a.fondu_bas} if a.buste else {}),
        }
        sortie.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(meta, ensure_ascii=False))
        if a.garder: print("travail :", travail)
    finally:
        if not a.garder: shutil.rmtree(travail, ignore_errors=True)


if __name__ == "__main__":
    main()
