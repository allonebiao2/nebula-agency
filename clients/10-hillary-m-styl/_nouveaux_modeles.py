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
    dict(cle="organza", id="h10", nom="Robe de ville organza",
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


# ⚠️ BIREFNET, PAS ISNET. Le 2026-08-20, la robe à jupon d'organza a tranché :
#    `isnet-general-use` rendait le train blanc EN GRIS SALE sur la face, et
#    l'EFFAÇAIT ENTIÈREMENT sur le dos — il ne restait qu'un disque rouge
#    flottant. Les tissus translucides (organza, tulle, mousseline) sont
#    exactement ce que ce modèle ne sait pas voir. `birefnet-general` les garde
#    intacts. Il est plus lent (~45 s par photo contre ~10 s) et pèse 890 Mo :
#    c'est le prix d'une pièce qui ressemble à ce qu'Hillary a cousu.
MODELE = "birefnet-general"
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
            seaux[int(h * 360) // 12].append((r, g, b, s))
    if not seaux:
        return "#6b3065"
    # ⚠️ PAS LA COULEUR LA PLUS ÉTENDUE : LA PLUS VIVE PARMI LES GRANDES.
    #    Le 2026-08-20, la robe verte et jaune est ressortie en BRUN `#9e6033`.
    #    Ce n'était pas une erreur de calcul : bras et jambes nus couvraient
    #    23 % de la photo contre 17 % pour le tissu, et la PEAU gagnait. Le
    #    héros aurait peint son fond couleur peau sous une robe verte.
    #    Un vêtement est presque toujours plus saturé qu'une peau : on garde
    #    les teintes qui occupent au moins 15 % de la pièce, et parmi elles on
    #    prend la plus vive. Vérifié sur les huit pièces : la verte redevient
    #    verte, l'ensemble en jean gagne son vrai rouge, et les six autres ne
    #    bougent pas ou à peine.
    total = sum(len(v) for v in seaux.values())
    grandes = [k for k, v in seaux.items() if len(v) >= 0.15 * total] or list(seaux)
    p = seaux[max(grandes, key=lambda k: sum(x[3] for x in seaux[k]) / len(seaux[k]))]
    r = sum(x[0] for x in p) / len(p)
    g = sum(x[1] for x in p) / len(p)
    b = sum(x[2] for x in p) / len(p)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    v = min(0.68, max(0.42, v))
    s = min(0.85, max(0.42, s))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def detourer_un(src, dest, haut):
    """Détoure UNE photo et l'écrit. Appelé dans un processus à part.

    ⚠️ POURQUOI UN PROCESSUS PAR PHOTO. Le 2026-08-20, `birefnet-general`
    enchaînait la première image sans broncher puis se faisait TUER sur la
    deuxième (code 137), sur une machine où 15 Go étaient libres. Ce n'est
    pas la machine : onnxruntime ne rend pas ce qu'il a pris entre deux
    inférences, et le pic finit par dépasser. Un processus par photo borne
    la casse et rend la mémoire à chaque fois. On paie le rechargement du
    modèle (~10 s) : c'est le prix d'une chaîne qui va au bout."""
    from rembg import new_session, remove
    from PIL import Image
    ouvrir_heic()
    session = new_session(MODELE)
    with open(src, "rb") as fh:
        im = Image.open(io.BytesIO(remove(fh.read(), session=session))).convert("RGBA")
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    haut = min(haut, im.height)
    r = haut / float(im.height)
    im = im.resize((max(1, int(round(im.width * r))), haut), Image.LANCZOS)
    im.save(dest, "WEBP", quality=94, alpha_quality=100, method=6, exact=True)


def poser_images(prets):
    """Détoure et pose. Même hauteur, même encodage que `_detourer.py`.
    On ne réencode jamais une image déjà posée."""
    import subprocess
    faits = []
    for m in prets:
        for rang, f in enumerate(photos(m)[:2]):
            suffixe = "" if rang == 0 else "-dos"
            dest = os.path.join(IMG, f"piece-{m['cle']}{suffixe}.webp")
            if os.path.exists(dest):
                print(f"     {os.path.basename(dest)} déjà posée", flush=True)
                continue
            src = os.path.join(dossier(m), f)
            haut = 950 if rang == 0 else 760
            r = subprocess.run([sys.executable, os.path.abspath(__file__),
                                "--une", src, dest, str(haut)],
                               capture_output=True, text=True)
            if r.returncode or not os.path.exists(dest):
                sys.exit(f"\n⛔ {m['nom']} ({f}) : le détourage a échoué"
                         f" (code {r.returncode})\n{(r.stderr or '')[-400:]}\n")
            print(f"     {os.path.basename(dest)} — "
                  f"{os.path.getsize(dest)//1024} Ko", flush=True)
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


def court(t, n=56):
    """La légende du carrousel. On coupe sur un MOT, pas au milieu d'un :
    « jupe longu » s'affiche en grand sous la pièce."""
    t = t.strip()
    if len(t) <= n:
        return t.rstrip(" .,;:")
    c = t[:n + 1]
    c = c[:c.rfind(" ")] if " " in c else c[:n]
    return c.rstrip(" .,;:")


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
    d = mot.find('{id:"%s"' % m["id"])
    if d < 0:
        return mot, False
    f = mot.index("},", d) + 2
    bloc = mot[d:f]

    if ('img:"%s"' % img) in bloc and (not img2 or ('img2:"%s"' % img2) in bloc):
        return mot, False

    ligne = 'img:"%s"' % img + (', img2:"%s"' % img2 if img2 else "")
    if "img:" in bloc:                       # une photo était déjà là : on remplace
        neuf_bloc = re.sub(r'img:"[^"]*"(,\s*img2:"[^"]*")?', ligne.replace("\\", "\\\\"),
                           bloc, count=1)
    else:
        # on insère juste avant la ligne des prix, là où `img` vit sur les
        # autres fiches — pour que les 20 fiches se lisent de la même façon
        neuf_bloc, n = re.subn(r"\n(\s*)prix:",
                               "\n\\g<1>" + ligne.replace("\\", "\\\\") + ",\n\\g<1>prix:",
                               bloc, count=1)
        if not n:
            sys.exit("⛔ %s : ligne « prix: » introuvable, injection annulée" % m["nom"])

    # `photoWa:true` a fait son temps : la photo est là.
    neuf_bloc = re.sub(r",?\s*photoWa:true", "", neuf_bloc, count=1)
    return mot[:d] + neuf_bloc + mot[f:], True


def verifier_js(source, chemin):
    """⛔ ON N'ÉCRIT JAMAIS UN JAVASCRIPT QU'ON N'A PAS FAIT RELIRE.

    Cet outil réécrit `motion.js` et `garde-moteur.js` par découpe de texte.
    Le 2026-08-20, deux bourdes de suite : une virgule posée après un
    commentaire (« */, ») et, pire, tout l'en-tête du fichier effacé. Dans les
    deux cas le site entier devenait muet, et rien ne le disait avant le QC.
    On passe la sortie à `node --check` AVANT de l'écrire, et on refuse."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8",
                                     newline="\n", delete=False) as fh:
        fh.write(source)
        tmp = fh.name
    try:
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    except FileNotFoundError:
        os.unlink(tmp)
        print("     ⚠️ node absent : le JavaScript n'a pas pu être relu.")
        return
    os.unlink(tmp)
    if r.returncode:
        sys.exit(f"\n⛔ {os.path.basename(chemin)} serait invalide, RIEN n'a été"
                 f" écrit :\n{(r.stderr or '').strip()[:400]}\n")


def poser_heros(mtn, faits, coul):
    """Réécrit la QUEUE du héros — les pièces que cet outil y a mises — dans
    l'ORDRE qui évite deux nappes voisines de même teinte.

    ⛔ ON NE TOUCHE À AUCUNE ENTRÉE D'ORIGINE. Les sept diapositives qui
       étaient là avant (les quatre `hero-*` et les trois pièces du 10/08)
       gardent leur place, leur texte et leur ponctuation, mot pour mot.
       Seules les pièces de `MODELES` sont déplaçables : ce sont les nôtres.

    ⚠️ POURQUOI LA QUEUE ENTIÈRE, ET PAS SEULEMENT LE NOUVEAU LOT. Le
       2026-08-20, les deux premières pièces reçues étaient rouges toutes les
       deux (2° et 4° de teinte) : aucun ordre ne pouvait les séparer, elles
       se suivaient forcément. Si l'on n'ordonnait que le lot du jour, ce
       voisinage resterait figé POUR TOUJOURS, même quand une pièce violette
       arriverait. En rejouant toute la queue à chaque vague, le défaut se
       répare tout seul dès qu'une teinte différente entre.

    ⚠️ Le héros TOURNE : la dernière diapositive précède la première. La
       jonction du bout compte autant que les autres."""
    d = mtn.index("var HERO = [")
    f = mtn.index("  ];", d)
    bloc = mtn[d:f]

    # une entrée = « { f:'…', … }, » ; on les sépare sur l'accolade ouvrante
    morceaux = re.split(r"\n(?=    \{ f:)", bloc)
    tete, entrees = morceaux[0], morceaux[1:]
    notres = {"piece-%s.webp" % m["cle"] for m in MODELES}

    fixes, mobiles = [], []
    for e in entrees:
        nom = re.search(r"f:'([^']+)'", e)
        (mobiles if (nom and nom.group(1) in notres) else fixes).append(e)

    # les pièces déjà posées par nous + celles du jour, sans doublon
    deja = {re.search(r"f:'([^']+)'", e).group(1) for e in mobiles}
    par_cle = {m["cle"]: m for m in MODELES}
    a_placer = [par_cle[c] for c in
                [re.search(r"piece-(.+)\.webp", n).group(1) for n in sorted(deja)]
                if c in par_cle and ("piece-" + c) in coul]
    for m in faits:
        img = f"piece-{m['cle']}.webp"
        if img in deja:
            continue
        if os.path.exists(os.path.join(IMG, img)) and ("piece-" + m["cle"]) in coul:
            a_placer.append(m)
    if not a_placer:
        return mtn

    t = lambda m: teinte_deg(coul["piece-" + m["cle"]])
    def virgule(e):
        """⚠️ La virgule se pose APRÈS l'accolade fermante, jamais à la fin du
        morceau. Le bloc `hero-4` traîne un commentaire de dix lignes derrière
        lui : y coller une virgule donne « */, » et casse tout le fichier —
        donc tout le site. Vu le 2026-08-20."""
        i = e.rfind("}")
        if i < 0 or e[i + 1:].lstrip().startswith(","):
            return e
        return e[:i + 1] + "," + e[i + 1:]

    def coul_de(e):
        return teinte_deg(re.search(r"c:'(#[0-9a-fA-F]{6})'", e).group(1))

    # la queue s'accroche à la dernière fixe, et la boucle la ramène à la première
    avant_h = coul_de(fixes[-1]) if fixes else None
    apres_h = coul_de(fixes[0]) if fixes else None

    reste, suite, prec = list(a_placer), [], avant_h
    while reste:
        if prec is None:
            choix = reste[0]
        else:
            loin = [m for m in reste if ecart(t(m), prec) >= ECART_MIN]
            choix = loin[0] if loin else max(reste, key=lambda m: ecart(t(m), prec))
        reste.remove(choix)
        suite.append(choix)
        prec = t(choix)

    def chaine(sq):
        h = ([avant_h] if avant_h is not None else []) + [t(m) for m in sq] \
            + ([apres_h] if apres_h is not None else [])
        return [ecart(h[i], h[i + 1]) for i in range(len(h) - 1)]

    if len(suite) > 1 and any(e < ECART_MIN for e in chaine(suite)):
        meilleur, score = suite, min(chaine(suite))
        for i in range(len(suite)):
            for j in range(i + 1, len(suite)):
                e = suite[:]
                e[i], e[j] = e[j], e[i]
                if min(chaine(e)) > score:
                    meilleur, score = e, min(chaine(e))
        suite = meilleur

    mauvais = [f"{a['nom']} -> {b['nom']}" for a, b, e in
               zip(suite, suite[1:], chaine(suite)[1 if avant_h is not None else 0:])
               if e < ECART_MIN]
    if mauvais:
        print("     ⚠️ nappes voisines au héros, aucun ordre ne les sépare :")
        for x in mauvais:
            print(f"        {x}")
        print("        (ça se réglera tout seul dès qu'une autre teinte entrera)")

    lignes = []
    for m in suite:
        # « Fait main · 2 semaines » quand c'est fait main, comme l'ensemble
        # JOSY qui est au héros depuis le premier jour. Sinon « Sur-mesure ».
        mat = ("Fait main" if m["tag"] == "Fait main" else "Sur-mesure") + " · 2 semaines"
        lignes.append("    { f:%s, c:%s, col:%s, mat:%s,\n      t:%s, d:%s },"
                      % (jsq(f"piece-{m['cle']}.webp"), jsq(coul["piece-" + m["cle"]]),
                         jsq(m["tag"] or "Sur-mesure"), jsq(mat), js(m["nom"]), js(m["ds"])))
    lignes[-1] = lignes[-1].rstrip(",")

    print(f"     héros : {len(suite)} pièce(s) à nous, dans cet ordre — "
          + " · ".join(m["nom"] for m in suite))
    corps = "\n".join([tete] + [virgule(e) for e in fixes] + lignes)
    # ⛔ `mtn[:d]` EST LE FICHIER : la bannière, `(function () {`, le
    #    `'use strict'` et vingt lignes de documentation. Une première
    #    version renvoyait `corps + mtn[f:]` et rayait tout ça d'un coup :
    #    le fichier ne se fermait plus, le site entier devenait muet.
    #    Le tableau du héros n'est pas le fichier, il est DEDANS.
    return mtn[:d] + corps + "\n" + mtn[f:]


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
    verifier_js(mtn, MOTION)
    io.open(MOTION, "w", encoding="utf-8", newline="\n").write(mtn)
    verifier_js(mot, MOTEUR)
    io.open(MOTEUR, "w", encoding="utf-8", newline="\n").write(mot)
    io.open(COULEURS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(coul, ensure_ascii=False, indent=1) + "\n")
    print(f"\n  {ajouts} pièce(s) ajoutée(s) au catalogue.")
    print("  Carrousel et héros : toutes les pièces qui ont une photo.")
    print("  ⚠️ Regarder le résultat AVANT de déployer : une photo mal détourée")
    print("     se voit au héros, jamais dans un contrôle.")
    print("  Ensuite : python _v4/_assembler.py && python _build.py && python _qc.py")


def main():
    # mode interne : une photo, un processus (voir `detourer_un`)
    if len(sys.argv) == 5 and sys.argv[1] == "--une":
        detourer_un(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        return 0

    """⚠️ LA RÈGLE A CHANGÉ LE 2026-08-18, ET C'EST VOULU.

    Avant, le script refusait de poser tant qu'une seule photo manquait :
    « un catalogue à moitié rempli est pire qu'un catalogue qui attend ».
    C'était juste quand les onze pièces n'étaient nulle part. Elles sont
    maintenant AU CATALOGUE, en ligne, avec « Photo sur WhatsApp ». Le calcul
    s'est inversé : chaque photo posée est un gain net, et celles qui manquent
    encore gardent une mention honnête et actionnable. Attendre la dernière,
    c'est laisser dix pièces sans image pour une onzième.

    Ce qui n'a PAS changé : on n'invente rien pour combler un trou."""
    # ⚠️ ON VÉRIFIE CE QUI EST GRATUIT AVANT DE LANCER CE QUI EST CHER.
    #    Le 2026-08-20, une restructuration avait effacé sept fonctions au
    #    passage. Le script a détouré DOUZE photos pendant dix minutes, puis
    #    est mort sur `NameError: fiche_existante` à la seconde d'après — au
    #    moment précis où il allait enfin écrire quelque chose. Le coût d'une
    #    bourde ne doit pas dépendre de l'endroit où elle explose.
    absents = [n for n in ("js", "jsq", "court", "teinte_deg", "ecart",
                           "fiche_existante", "poser_heros", "injecter",
                           "verifier_js", "detourer_un")
               if n not in globals()]
    if absents:
        sys.exit("⛔ fonctions manquantes, rien n'a été lancé : "
                 + ", ".join(absents) + "\n")

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
