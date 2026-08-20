#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HILLARY M. STYL — les ONZE modèles reçus les 2026-08-16 et 17, prêts à entrer.

    python _nouveaux_modeles.py           dit ce qui manque, ne touche à rien
    python _nouveaux_modeles.py --poser   détoure, pose les images, injecte

POURQUOI CE FICHIER EXISTE
Hillary a envoyé onze modèles avec leurs prix, leurs délais et leur type de
mesures. **Tout est ici, sauf les photos** : elles ont été montrées dans une
conversation, elles ne sont jamais devenues des fichiers sur le disque. Ce
script garde les données au chaud pour que leur arrivée ne coûte qu'une
commande, et il REFUSE de travailler tant qu'une photo manque.

⛔ IL N'INVENTE RIEN. Pas de photo générée, pas de prix déduit, pas de nom
   fabriqué autrement que le descriptif provisoire validé par Mongazi.

COMMENT ON S'EN SERT
1. Les photos arrivent dans `_partage/`.
2. On les range, une par dossier : `_sources/modele-<clé>/…`
   · UNE photo  → la pièce a une seule vue ;
   · DEUX photos → face et dos. Nommer le dos `dos.jpg` (ou `2-dos.jpg`) suffit
     à fixer l'ordre ; sans ça, c'est l'ordre alphabétique qui tranche.
     La carte du catalogue et le carrousel les feront alors DÉFILER TOUT SEULS,
     l'une après l'autre, pendant qu'on les regarde.
3. `python _nouveaux_modeles.py --poser`   (pose ce qui est prêt, pas plus)
4. `python _v4/_assembler.py && python _build.py && python _qc.py`
"""
import io, json, os, re, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "_sources")
IMG = os.path.join(ICI, "assets", "images")
MOTEUR = os.path.join(ICI, "_v4", "garde-moteur.js")
MOTION = os.path.join(ICI, "_v4", "motion.js")
COULEURS = os.path.join(ICI, "_v4", "_couleurs.json")

# ⚠️ LES DONNÉES SONT CELLES QU'ELLE A DONNÉES, MOT POUR MOT.
#    Prix normal, prix express TOTAL, délais, type de mesures. Les euros et
#    les dollars sont les siens : on ne les recalcule jamais.
#    Les noms sont provisoires : Mongazi a tranché le 2026-08-16, « on garde,
#    elle corrigera ce qui ne lui va pas ».
#    `indice` sert à reconnaître la photo au moment de la ranger.
MODELES = [
    dict(cle="organza", id="h10", nom="Robe Organza",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="robe_ovale", tag="Cérémonie",
         indice="robe rouge à motifs blancs, col en organza blanc froncé, jupon d'organza — fond JAUNE, deux vues : face et dos (la face est arrivée le 17/08)",
         ds="Manches ballon détachées des épaules, col en organza froncé, découpe à la taille, dos lacé au ruban et jupon d'organza sous un wax rouge."),
    dict(cle="noeud", id="h11", nom="Ensemble Nœud",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="haut_pantalon", tag="",
         indice="haut dos nu à col, noué dans le dos, et pantalon large rouge — face et dos",
         ds="Haut dos nu à col, noué dans le dos, et pantalon large avec un pan de wax rouge et blanc."),
    dict(cle="lacee", id="h12", nom="Robe Lacée",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="robe_ovale", tag="",
         indice="robe wax violet à éventails bleu et blanc, sur mannequin, dos lacé — face et dos",
         ds="Épaules dénudées à fines bretelles, manches ballon, basque à la taille, dos lacé au ruban."),
    dict(cle="coeurs", id="h13", nom="Tailleur Cœurs",
         prix=50000, expPrix=65000, eur=75, usd=90, eurExp=99, usdExp=115,
         type="haut_pantalon", tag="Fait main",
         indice="tailleur bordeaux à cœurs blancs, veste cintrée et pantalon large, sur mannequin",
         ds="Veste cintrée à revers et épaules structurées, pantalon large assorti, wax bordeaux à cœurs."),
    dict(cle="jean", id="h14", nom="Ensemble Jean",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="haut_jupe", tag="",
         indice="haut court et jupe à volants montée sur un empiècement en JEAN — deux mannequins",
         ds="Haut court épaules dénudées à manches ballon, jupe longue à volants montée sur un empiècement en jean."),
    dict(cle="sirene", id="h15", nom="Robe Sirène",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="robe_droite", tag="Cérémonie",
         indice="fourreau violet à volants bleu roi, traîne, foulard assorti — ⛔ prendre la vue de PROFIL, celle de face porte un cœur collé",
         ds="Fourreau en wax violet, volants bleu roi en bordure et le long de la fente, traîne et foulard assorti."),
    dict(cle="emeraude", id="h16", nom="Robe Émeraude",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="haut_jupe", tag="",
         indice="robe courte verte et jaune à manches longues, fond blanc",
         ds="Coupe courte ajustée, manches longues, grands motifs verts et jaunes cernés de noir."),
    dict(cle="orange-uni", id="h17", nom="Ensemble Orange",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="haut_pantalon", tag="",
         indice="tissu UNI orange, bustier froncé à lien au cou, découpes à la taille (⚠️ le sac beige n'est pas la pièce)",
         ds="Bustier froncé à lien au cou, découpes sur les côtés, bas long et très ample en tissu uni."),
    dict(cle="soleil", id="h18", nom="Robe Soleil",
         prix=25000, expPrix=35000, eur=37, usd=45, eurExp=52, usdExp=63,
         type="robe_ovale", tag="Cérémonie",
         indice="robe longue bazin tie-dye ROUGE ET OR, épaules drapées à pompons, sur mannequin",
         ds="Épaules drapées à cordons et pompons, ceinture drapée, jupe très ample en bazin teint rouge et or."),
    dict(cle="ete", id="h19", nom="Robe d'été",
         prix=35000, expPrix=45000, eur=52, usd=63, eurExp=67, usdExp=81,
         type="robe_ovale", tag="Plage",
         indice="DEUX mannequins, haut court noué au cou + jupe longue : bazin tie-dye brun et jaune à médaillons roses, et tie-dye orange et bleu — DEUX vues nettes reçues le 18/08 (face et dos, dos nu noué à la nuque) — ne PAS reprendre la capture d'écran du 17",
         ds="Haut court noué au cou et jupe longue très ample, en bazin teint. La pièce d'été, qui va de la plage au déjeuner."),
    dict(cle="volants", id="h20", nom="Ensemble Volants",
         prix=40000, expPrix=55000, eur=60, usd=72, eurExp=82, usdExp=100,
         type="haut_pantalon", tag="",
         indice="haut court noué devant à MANCHES A TROIS VOLANTS, bazin tie-dye rouge et blanc, + pantalon tres evase en JEAN a empiecements rouges — face et dos, un seul mannequin",
         ds="Haut court noué devant, manches à trois volants étagés, et pantalon très évasé en jean à empiècements de bazin teint."),
]

# ⚠️ IL N'Y A PLUS DE LISTE DE TROIS ÉLUES. Mongazi, le 2026-08-18 :
#    « dans la hero tu n'y mets en plus que les nouvelles, dans le style de
#    ceux déjà présents, histoire que ça reste cohérent. » Toute pièce qui a
#    sa photo entre donc au héros, écrite comme ses voisines, et c'est
#    `poser_heros()` qui choisit l'ORDRE pour que deux nappes de même teinte
#    ne se suivent jamais.

JMIN = JMAX = 14          # deux semaines fermes, pour les dix
EXPMIN, EXPMAX = 2, 4     # « 2 à 4 jours », pour les dix


BONS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif")
_DITS = set()


def ouvrir_heic():
    """Les photos d'un iPhone arrivent en HEIC. Sans ce greffon, Pillow ne
    sait pas les lire et le détourage s'arrête sur une exception. Absent, on
    continue : les JPEG et les PNG marchent quand même."""
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass


def dossier(m):
    return os.path.join(SRC, "modele-" + m["cle"])


def photos(m):
    """Les photos d'un modèle, LA FACE D'ABORD.

    Hillary envoie certaines pièces en double : une vue de face, une de dos.
    L'ordre compte — la face va au catalogue, au carrousel et au héros, le dos
    ne sert qu'à la seconde vue. On le décide dans cet ordre :

      1. un nom qui le dit  (`dos`, `arriere`, `back`) part au second rang ;
      2. sinon, l'ordre alphabétique, en documentant que `1-…` / `2-…` marche.

    ⚠️ Trois photos ou plus : on garde les deux premières et on le DIT.
       Choisir en silence, c'est laisser une vue sur le disque sans que
       personne ne sache qu'elle a été écartée."""
    d = dossier(m)
    if not os.path.isdir(d):
        return []
    # ⚠️ Le HEIC des iPhone est accepté (voir `ouvrir_heic()`). Il ne l'était
    #    pas, et un `.heic` déposé dans le dossier était ignoré EN SILENCE :
    #    le script annonçait « en attente de photo » alors que la photo était
    #    là, sous les yeux, dans le bon dossier.
    tout = [f for f in sorted(os.listdir(d)) if not f.startswith(".")]
    l = [f for f in tout if f.lower().endswith(BONS)]
    for f in tout:
        c = os.path.join(os.path.basename(d), f)
        if f not in l and c not in _DITS:      # `photos()` est appelée plusieurs
            _DITS.add(c)                       # fois : on ne le dit qu'une
            print(f"     ⚠️ ignoré (format non géré) : {c}")

    def est_dos(f):
        return re.search(r"(dos|arriere|arrière|back)", f, re.I) is not None

    face = [f for f in l if not est_dos(f)]
    dos = [f for f in l if est_dos(f)]
    return (face + dos) if face else l


def etat():
    prets, manquants = [], []
    for m in MODELES:
        (prets if photos(m) else manquants).append(m)
    return prets, manquants


def dire():
    prets, manquants = etat()
    print(f"\n  {len(prets)} modèle(s) prêt(s), {len(manquants)} en attente de photo.\n")
    for m in manquants:
        os.makedirs(dossier(m), exist_ok=True)   # pour qu'il se voie dans l'explorateur
        print(f"  ⛔ {m['nom']:<18} {m['prix']:>6} F   {dossier(m)[len(ICI)+1:]}/")
        print(f"     à reconnaître : {m['indice']}")
    for m in prets:
        ph = photos(m)
        vue = "face + dos ↔ elle switchera toute seule" if len(ph) >= 2 else "face seule"
        trop = f"  ⚠️ {len(ph) - 2} photo(s) écartée(s)" if len(ph) > 2 else ""
        print(f"  ✅ {m['nom']:<18} {m['prix']:>6} F   {vue}{trop}")
    if manquants:
        print("\n  Rien n'a été modifié. Déposez les photos dans les dossiers"
              "\n  ci-dessus, puis relancez avec --poser.\n")
    return prets, manquants


def teinte(chemin):
    """La teinte dominante du tissu, comme pour les pièces déjà en ligne.
    ⚠️ Seuil de saturation à 0,22 : à 0,35 les tissus sourds (le sauge de la
    robe verte) étaient écartés et deux pièces tombaient sur la même nappe."""
    import colorsys
    from collections import defaultdict
    from PIL import Image
    im = Image.open(chemin).convert("RGBA")
    im = im.resize((max(1, im.width // 3), max(1, im.height // 3)), Image.LANCZOS)
    px = im.load()
    seaux = defaultdict(list)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 220:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s < 0.22 or v < 0.18 or v > 0.92:
                continue
            seaux[int(h * 360) // 12].append((r, g, b))
    if not seaux:
        return "#6b3065"
    p = seaux[max(seaux, key=lambda k: len(seaux[k]))]
    r = sum(x[0] for x in p) / len(p)
    g = sum(x[1] for x in p) / len(p)
    b = sum(x[2] for x in p) / len(p)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    v = min(0.68, max(0.42, v))
    s = min(0.85, max(0.42, s))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def poser_images(prets):
    """Détoure et pose, exactement comme `_detourer.py` : même hauteur, même
    encodage. On ne réencode jamais une image déjà posée."""
    from rembg import new_session, remove
    from PIL import Image
    ouvrir_heic()
    session = new_session("isnet-general-use")
    faits = []
    for m in prets:
        for rang, f in enumerate(photos(m)[:2]):
            suffixe = "" if rang == 0 else "-dos"
            dest = os.path.join(IMG, f"piece-{m['cle']}{suffixe}.webp")
            if os.path.exists(dest):
                print(f"     {os.path.basename(dest)} déjà posée")
                continue
            with open(os.path.join(dossier(m), f), "rb") as fh:
                im = Image.open(io.BytesIO(remove(fh.read(), session=session))).convert("RGBA")
            bb = im.getbbox()
            if bb:
                im = im.crop(bb)
            haut = min(950 if rang == 0 else 760, im.height)
            r = haut / float(im.height)
            im = im.resize((max(1, int(round(im.width * r))), haut), Image.LANCZOS)
            im.save(dest, "WEBP", quality=94, alpha_quality=100, method=6, exact=True)
            print(f"     {os.path.basename(dest)} — {os.path.getsize(dest)//1024} Ko")
        faits.append(m)
    return faits


def js(v):
    """Une chaîne écrite dans du JavaScript, échappée pour de bon.
    ⚠️ Les anciennes lignes étaient bâties en `'%s'` : la première apostrophe
    dans un nom ou une description cassait tout le fichier, donc tout le site.
    Aucune des pièces d'aujourd'hui n'en porte — ce n'est pas une raison."""
    return json.dumps(v, ensure_ascii=False)


def jsq(v):
    """La même chose, mais EN GARDANT LE STYLE DU FICHIER : les entrées du
    héros et du carrousel écrivent leurs noms de fichier et leurs étiquettes
    entre apostrophes (`f:'hero-1.webp'`) et leurs textes entre guillemets
    (`t:"L'ensemble Mira"`). Une pièce ajoutée doit se lire comme ses voisines,
    sinon le tableau devient un patchwork au fil des vagues.
    Dès qu'une valeur porte une apostrophe, on repasse aux guillemets : la
    cohérence ne vaut pas un fichier cassé."""
    return "'" + v + "'" if ("'" not in v and "\\" not in v) else json.dumps(v, ensure_ascii=False)


def teinte_deg(c):
    """La teinte d'un « #rrggbb », en degrés sur le cercle des couleurs."""
    import colorsys
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360


def ecart(a, b):
    """La distance entre deux teintes (0 à 180)."""
    d = abs(a - b) % 360
    return min(d, 360 - d)


ECART_MIN = 28   # en dessous, deux nappes se confondent


def court(t, n=56):
    """La légende du carrousel. On coupe sur un MOT, pas au milieu d'un :
    « jupe longu » s'affiche en grand sous la pièce."""
    t = t.strip()
    if len(t) <= n:
        return t.rstrip(" .,;:")
    c = t[:n + 1]
    c = c[:c.rfind(" ")] if " " in c else c[:n]
    return c.rstrip(" .,;:")


def fiche_existante(mot, m, img, img2):
    """⛔ LE DÉFAUT QUE CE BLOC RÉPARE. Les onze fiches sont ENTRÉES AU
    CATALOGUE LE 2026-08-18, sans photo, avec `photoWa:true` (« Photo sur
    WhatsApp »). L'ancien `injecter()` voyait `id:"h10"` déjà présent, écrivait
    « déjà au catalogue » et passait. Les photos auraient été détourées, posées
    dans `assets/images/`… et jamais raccrochées à une fiche. Le site n'aurait
    pas bougé d'un pixel, et rien ne l'aurait signalé.

    Ici on ACCROCHE la photo à la fiche qui existe : on pose `img` (et `img2`
    s'il y a un dos) et on retire `photoWa:true`, qui devient un mensonge dès
    que la photo est là. Idempotent : une fiche déjà pourvue n'est pas touchée.
    Renvoie (source, True) si quelque chose a changé."""
    d = mot.find(f'{{id:"{m["id"]}"')
    if d < 0:
        return mot, False
    f = mot.index("},", d) + 2
    bloc = mot[d:f]

    if f'img:"{img}"' in bloc and (not img2 or f'img2:"{img2}"' in bloc):
        return mot, False

    ligne = f'img:"{img}"' + (f', img2:"{img2}"' if img2 else "")
    if "img:" in bloc:                       # une photo était déjà là : on remplace
        neuf_bloc = re.sub(r'img:"[^"]*"(,\s*img2:"[^"]*")?', ligne, bloc, count=1)
    else:
        # on insère juste avant la ligne des prix, là où `img` vit sur les
        # autres fiches — pour que les 20 fiches se lisent de la même façon
        neuf_bloc, n = re.subn(r"\n(\s*)prix:", "\n\\g<1>" + ligne.replace("\\", "\\\\") + ",\n\\g<1>prix:",
                               bloc, count=1)
        if not n:
            sys.exit(f"⛔ {m['nom']} : ligne « prix: » introuvable, injection annulée")

    # `photoWa:true` a fait son temps : la photo est là.
    neuf_bloc = re.sub(r",?\s*photoWa:true", "", neuf_bloc, count=1)
    return mot[:d] + neuf_bloc + mot[f:], True


def poser_heros(mtn, faits, coul):
    """Ajoute les nouvelles pièces au HÉROS, à la suite de celles qui y sont,
    et dans l'ORDRE qui évite deux nappes voisines de même teinte.

    ⛔ ON NE TOUCHE À AUCUNE ENTRÉE DÉJÀ PRÉSENTE. Elles gardent leur place,
       leur formulation et leur ponctuation. On ajoute à la suite, dans leur
       style : `f` `c` `col` `mat` entre apostrophes, `t` et `d` entre
       guillemets, une pièce par bloc de deux lignes.

    ⚠️ LA RÈGLE DES NAPPES VIENT DU 2026-08-17. La robe à tulle avait été
       écartée du héros parce que « son violet doublait celui de la robe de
       cérémonie violette, et deux nappes identiques qui se suivent ne se
       voient pas » : le héros peint le fond avec la teinte de la pièce, donc
       deux teintes voisines à la suite, c'est une transition qui n'existe
       pas. On garde la règle — mais on ne perd plus la pièce : au lieu de
       l'exclure, on la DÉPLACE.

    ⚠️ Le héros TOURNE en boucle : la dernière diapositive précède la
       première. La jonction du bout compte autant que les autres."""
    d = mtn.index("var HERO = [")
    f = mtn.index("  ];", d)
    bloc = mtn[d:f]
    deja = re.findall(r"c:'(#[0-9a-fA-F]{6})'", bloc)
    presentes = set(re.findall(r"f:'([^']+)'", bloc))

    reste = [m for m in faits
             if os.path.exists(os.path.join(IMG, f"piece-{m['cle']}.webp"))
             and f"piece-{m['cle']}.webp" not in presentes
             and ("piece-" + m["cle"]) in coul]
    if not reste:
        return mtn

    t = lambda m: teinte_deg(coul["piece-" + m["cle"]])

    # on enchaîne à partir de la dernière teinte déjà en place
    suite, prec = [], teinte_deg(deja[-1]) if deja else None
    while reste:
        if prec is None:
            choix = reste[0]
        else:
            loin = [m for m in reste if ecart(t(m), prec) >= ECART_MIN]
            # à défaut, celle qui s'en éloigne le plus : on ne bloque jamais
            choix = loin[0] if loin else max(reste, key=lambda m: ecart(t(m), prec))
        reste.remove(choix)
        suite.append(choix)
        prec = t(choix)

    # la boucle se referme : si la dernière double la première du héros, on
    # cherche une permutation qui règle la jonction sans en casser une autre
    if deja and len(suite) > 1:
        avant, apres = teinte_deg(deja[-1]), teinte_deg(deja[0])

        def chaine_ok(sq):
            h = [avant] + [t(m) for m in sq] + [apres]
            return all(ecart(h[i], h[i + 1]) >= ECART_MIN for i in range(len(h) - 1))

        if not chaine_ok(suite):
            for i in range(len(suite)):
                for j in range(i + 1, len(suite)):
                    e = suite[:]
                    e[i], e[j] = e[j], e[i]
                    if chaine_ok(e):
                        suite = e
                        break
                else:
                    continue
                break
            else:
                print("     ⚠️ deux nappes voisines se ressemblent au héros :"
                      " regarder l'enchaînement avant de déployer.")

    lignes = []
    for m in suite:
        # « Fait main · 2 semaines » quand c'est fait main, comme l'ensemble
        # JOSY qui est au héros depuis le premier jour. Sinon « Sur-mesure ».
        mat = ("Fait main" if m["tag"] == "Fait main" else "Sur-mesure") + " · 2 semaines"
        lignes.append("    { f:%s, c:%s, col:%s, mat:%s,\n      t:%s, d:%s }"
                      % (jsq(f"piece-{m['cle']}.webp"), jsq(coul["piece-" + m["cle"]]),
                         jsq(m["tag"] or "Sur-mesure"), jsq(mat), js(m["nom"]), js(m["ds"])))

    print(f"     héros : +{len(suite)} pièce(s) — "
          + " · ".join(m["nom"] for m in suite))
    return (mtn[:f].rstrip().rstrip(",") + ",\n" + ",\n".join(lignes) + "\n" + mtn[f:])


def injecter(faits):
    """Accroche la photo à chaque pièce : au catalogue, au carrousel et, pour
    les meilleures, au héros. Idempotent de bout en bout — on peut relancer."""
    mot = io.open(MOTEUR, encoding="utf-8").read()
    mtn = io.open(MOTION, encoding="utf-8").read()
    coul = json.load(io.open(COULEURS, encoding="utf-8"))
    ajouts = 0

    for m in faits:
        img = f"piece-{m['cle']}.webp"
        img2 = f"piece-{m['cle']}-dos.webp"
        a_dos = os.path.exists(os.path.join(IMG, img2))
        if not os.path.exists(os.path.join(IMG, img)):
            print(f"     ⛔ {m['nom']} : {img} absente, fiche laissée telle quelle")
            continue

        if f'id:"{m["id"]}"' in mot:
            mot, change = fiche_existante(mot, m, img, img2 if a_dos else None)
            print(f"     {m['nom']} : "
                  + (("photo posée" + (" + dos" if a_dos else "")) if change
                     else "déjà pourvue, rien à faire"))
            if change:
                coul["piece-" + m["cle"]] = teinte(os.path.join(IMG, img))
                ajouts += 1
            continue

        fiche = (
            f'\n  {{id:"{m["id"]}", cat:"sm", nom:"{m["nom"]}", type:"{m["type"]}", tag:"{m["tag"]}",\n'
            f'   img:"{img}"' + (f', img2:"{img2}"' if a_dos else "") + ",\n"
            f'   prix:{m["prix"]}, jmin:{JMIN}, jmax:{JMAX}, expPrix:{m["expPrix"]}, '
            f'expMin:{EXPMIN}, expMax:{EXPMAX},\n'
            f'   eur:{m["eur"]}, usd:{m["usd"]}, eurExp:{m["eurExp"]}, usdExp:{m["usdExp"]},\n'
            f'   ds:"{m["ds"]}"}},'
        )
        # on insère juste avant la « Création libre », qui doit rester la dernière
        ancre = '  /* Une CRÉATION LIBRE'
        if ancre not in mot:
            sys.exit("⛔ ancre du catalogue introuvable : injection annulée")
        mot = mot.replace(ancre, fiche.lstrip("\n") + "\n\n" + ancre, 1)

        coul["piece-" + m["cle"]] = teinte(os.path.join(IMG, img))
        ajouts += 1

    # ── LE CARROUSEL PREND TOUTES LES PIÈCES ──────────────────────
    for m in faits:
        img = f"piece-{m['cle']}.webp"
        img2 = f"piece-{m['cle']}-dos.webp"
        a_dos = os.path.exists(os.path.join(IMG, img2))
        if not os.path.exists(os.path.join(IMG, img)) or img in mtn:
            continue
        fin_coll = mtn.index("  ];", mtn.index("var COLLECTIONS = ["))
        # `f2` = la vue de dos : c'est elle qui fait respirer la carte active
        ligne = ("    { f:%s,%s l:%s, t:%s, s:%s }"
                 % (jsq(img), (" f2:%s," % jsq(img2)) if a_dos else "",
                    jsq(m["tag"] or "Sur-mesure"), js(m["nom"]), jsq(court(m["ds"]))))
        mtn = (mtn[:fin_coll].rstrip().rstrip(",") + ",\n" + ligne + "\n"
               + mtn[fin_coll:])

    # ── ET LE HÉROS AUSSI ─────────────────────────────────────────
    mtn = poser_heros(mtn, faits, coul)

    # ⛔ `motion.js` n'était JAMAIS réécrit : le carrousel et le héros étaient
    #    calculés ligne par ligne, puis jetés à la sortie de la fonction. Une
    #    pièce serait entrée au catalogue et nulle part ailleurs.
    io.open(MOTION, "w", encoding="utf-8", newline="\n").write(mtn)
    io.open(MOTEUR, "w", encoding="utf-8", newline="\n").write(mot)
    io.open(COULEURS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(coul, ensure_ascii=False, indent=1) + "\n")
    print(f"\n  {ajouts} pièce(s) ajoutée(s) au catalogue.")
    print("  Carrousel et héros : toutes les pièces qui ont une photo.")
    print("  ⚠️ Regarder le résultat AVANT de déployer : une photo mal détourée")
    print("     se voit au héros, jamais dans un contrôle.")
    print("  Ensuite : python _v4/_assembler.py && python _build.py && python _qc.py")


def main():
    """⚠️ LA RÈGLE A CHANGÉ LE 2026-08-18, ET C'EST VOULU.

    Avant, le script refusait de poser tant qu'une seule photo manquait :
    « un catalogue à moitié rempli est pire qu'un catalogue qui attend ».
    C'était juste quand les onze pièces n'étaient nulle part. Elles sont
    maintenant AU CATALOGUE, en ligne, avec « Photo sur WhatsApp ». Le calcul
    s'est inversé : chaque photo posée est un gain net, et celles qui manquent
    encore gardent une mention honnête et actionnable. Attendre la dernière,
    c'est laisser dix pièces sans image pour une onzième.

    Ce qui n'a PAS changé : on n'invente rien pour combler un trou."""
    prets, manquants = dire()
    if "--poser" not in sys.argv:
        return 0
    if not prets:
        print("  Aucune photo à poser.\n")
        return 1
    print("\n  Détourage et pose…")
    injecter(poser_images(prets))
    if manquants:
        print(f"\n  ⏳ {len(manquants)} pièce(s) attendent encore leur photo et"
              "\n     gardent « Photo sur WhatsApp ». Relancer à leur arrivée.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
