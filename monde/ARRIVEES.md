# LE MONDE · les assets reçus de Mongazi, et leur analyse

> Le registre de ce qui arrive (images, vidéos, modèles), **où c'est rangé** et **ce qu'on en a vu**.
> Une entrée par arrivée, la plus récente en haut. Tout vit dans `_partage\immersive  store 3D\`
> (deux espaces), **exclu de git en entier depuis le 2026-11-13** : planches de SES robes, son logo,
> FBX Mixamo, visage d'Hillary ; le dépôt est public.

---

## 2026-11-13 · 24 fichiers déposés en vrac dans `hillary\`, rangés le jour même

Mongazi : « j'ai tout mis dans hillary donc dispatch correctement et observes analyses en
profondeur ». Puis : « pour le salon j'ai pas encore fini de générer les plans, et lors des
créations j'arrivais pas à avoir de la constance entre les images » ; « les personnages aussi j'ai
pas encore terminé de créer tous les plans ». ⏸️ **Consigne : ne rien intégrer**, il envoie la
suite (« attends, ne fais rien, je t'enverrai les assets pour que tu intègres »).

Toutes les images font **1536 × 2752** (9:16, la sortie 2K de Nano Banana Pro), toutes les vidéos
**7,93 s, 720 × 1280, 24 i/s, sans son** (image → vidéo). Les noms d'origine (chiffres, passés par une
messagerie) sont dans la table ci-dessous ; **rien n'a été supprimé**, seulement déplacé.

### Le rangement

| Nom d'origine | Rangé sous | Ce que c'est |
|---|---|---|
| `466250186_…jpg` | `personnages/afi/afi-face-29ans.jpg` | Afi, pose A, 29 ans |
| `407134447_…mp4` | `personnages/afi/videos/afi-parler.mp4` | elle parle, gestes à hauteur de poitrine |
| `558361728_…mp4` | `personnages/afi/videos/afi-marcher.mp4` | quelques pas, puis l'arrêt |
| `651593715_…jpg` | `personnages/senami/senami-face-21ans.jpg` | Sènami, pose A, 21 ans |
| `197977779_…mp4` | `personnages/senami/videos/senami-ecouter.mp4` | mains jointes, hoche la tête |
| `168609538_…mp4` | `personnages/senami/videos/senami-parler.mp4` | elle parle, mains ouvertes |
| `11525817_…mp4` | `personnages/senami/videos/senami-marcher.mp4` | elle avance vers la caméra |
| `143374558_…mp4` | `personnages/senami/videos/senami-tourner.mp4` | de la pose A au profil, puis retour |
| `538373366_…jpg` | `personnages/maman/maman-face-47ans.jpg` | Maman Sènami, pose A, 47 ans |
| `851586202_…mp4` | `personnages/maman/videos/maman-parler.mp4` | elle parle, mains ouvertes |
| `427414809_…mp4` | `personnages/maman/videos/maman-marcher.mp4` | baisse les bras, avance de quelques pas |
| `101560209_…mp4` | `personnages/maman/videos/maman-tourner.mp4` | trois quarts, profil, retour |
| `HILLARY.jpg` | `hillary/hillary-corps-face.jpg` | Hillary, pose A, robe noire |
| `224183643_…jpg` | `robes/robe-h1-planche.jpg` | planche 4 vues, Robe de cérémonie (h1) |
| `690854262_…jpg` | `robes/robe-h2-planche.jpg` | planche 4 vues, L'ensemble Mira (h2) |
| `428580821_…jpg` | `robes/robe-inconnue-planche.jpg` | planche 4 vues, **pièce introuvable dans son catalogue** |
| `293650112_…jpg` | `salon/salon-plan-iso.jpg` | plan isométrique + une vue intérieure |
| `693060296_…jpg` | `salon/salon-vue-coupole-ronde.jpg` | coupole ronde, podium carré, vitrine au fond |
| `159102932_…jpg` | `salon/salon-vue-comptoir-arche.jpg` | grand anneau lumineux, comptoir sous une arche, spots |
| `650137189_…jpg` | `salon/salon-vue-trois-podiums.jpg` | double anneau, 3 robes magenta, **autre logo** |
| `386537844_…jpg` | `salon/salon-vue-banc-affiches.jpg` | banc de velours magenta, affiches de défilé |
| `743668242_…jpg` | `salon/salon-vue-vitrine-wax.jpg` | mannequins en wax devant la vitrine, comptoir blanc et bois |
| `45429968_…jpg` | `salon/salon-vue-allee.jpg` | allée vers le comptoir en arche, reflets au sol |
| `914544393_…jpg` | `salon/salon-vue-trois-angles.jpg` | trois vues empilées du même coin |

### Les personnages

- **Afi (29 ans)** : conforme à la consigne mot pour mot (manteau crème ouvert, haut et pantalon
  noirs, ballerines, afro, créoles). **Nettement meilleure que l'image du modèle en place**
  (`personnages/afi-face.png`, 800 px, rendu de jeu) : photographique, afro vrai, mains naturelles,
  proportions justes. **À refaire en 3D quand il le dira.** Les 12 animations « sans peau » sont sur
  le squelette standard de Mixamo : elles devraient se rejouer sur la nouvelle Afi, seule `attendre`
  (avec la peau) est à refaire (⚠️ à vérifier le jour venu, les longueurs d'os changent).
- **Sènami (21 ans)** : l'âge tient (une jeune adulte, plus l'adolescente du 12). Pose A propre.
  ⚠️ **Les tresses tombent devant les épaules** : en 3D depuis une seule image, elles se collent au
  buste, et bougent avec lui.
- **Maman Sènami (47 ans)** : l'âge tient à peu près (45-55, sans cheveux gris ni rides profondes).
  ⚠️ **Le boubou forme une aile entre le bras et le corps** : au squelette, le tissu s'étire dès que
  le bras bouge. Il faudra des animations aux bras proches du corps, ou un tissu séparé.
- **Hillary** : image photographique (pas un rendu de jeu), robe noire à manches longues et ourlet
  asymétrique, ballerines nude, locks longues avec des bagues, créoles. ⚠️ **Les locks couvrent les
  épaules et le haut du buste** (la consigne B1 demandait les cheveux dégagés) : même défaut que
  Sènami, en plus marqué. Fond lavande, pas gris (sans gêne pour le détourage).
  ⛔ **Il manque** : les **six expressions de son visage en 3D** dont Mongazi a parlé (pas dans le
  dossier). ✅ **Accord** : Mongazi, 2026-11-13 : « elle m'a accordé son accord donc vas-y » (une trace écrite lui
  est demandée dans `hillary\`). La ressemblance, seul Mongazi peut la confirmer.

### Les vidéos

Toutes conformes aux règles de capture : caméra fixe, corps entier du début à la fin, fond gris, un
seul personnage. Rangées par action. **Manquent encore**, d'après `personnages/CONSIGNES.md` :
`attendre`, `saluer`, `regarder-robe` et l'action propre à chacune (Afi : l'étiquette et le
téléphone ; Sènami : le TikTok ; Maman : toucher le wax) ; Afi n'a pas `ecouter`.
⚠️ **Ce qu'on en fait n'est toujours pas tranché** (capture de mouvement depuis une vidéo : outil à
trouver, gratuit et à licence commerciale). **Découverte utile** : `senami-tourner` et
`maman-tourner` montrent les personnages **de profil et de trois quarts** : de quoi faire une 3D à
plusieurs vues (le dos n'est plus inventé).

### Les robes (comparées à ses vraies photos, `lieux/hillary-m-styl/img/`)

- **h1, Robe de cérémonie** : **très fidèle** (tie-dye bleu à gauche, rouge à droite, bretelles à
  volants, bustier à pointe, volants de satin bleu roi et bordeaux). ⛔ **Un défaut** : le mannequin
  porte **les bijoux de la photo** (manchette dorée en haut du bras, bracelets aux poignets).
  ✅ **Corrigé par moi le jour même** (Mongazi : « intègre ») : bijoux effacés au pixel (OpenCV, l'or et ses
  creux, sans toucher au tie-dye) → `robes/robe-h1-planche-sans-bijoux.jpg` ; vue de face seule →
  `robes/robe-h1-face.jpg` (et `robe-h2-face.jpg`, pour que la 3D n'hérite pas du dos inventé de h2).
  Consigne C, si on préfère la refaire au générateur :
  `Keep everything identical, except: remove all jewelry from the mannequin, no gold cuff on the upper arm and no bracelets on the wrists. The mannequin wears nothing but the dress.`
- **h2, L'ensemble Mira** : **fidèle de face** (manches ballon jaunes, bonnets en wax brun, corset
  à baleines rayées de bleu, jupe à volants étagés jaune, bleu, brun). ⚠️ **Le dos est inventé** (dos
  nu, lien à la nuque, fermeture éclair visible), alors que sa photo ne montre pas le dos ; et la jupe
  s'arrête aux chevilles, celle de la photo touche le sol. **Hillary doit dire si son dos est ouvert.**
  Sinon : `Keep everything identical, except: the back must not invent anything, no open back, no halter strap, no visible zipper, a simple closed back in the same fabrics as the front; the skirt reaches the floor and covers the feet, with the same fullness as in the original photo.`
- **`robe-inconnue`** : bustier sans bretelles en wax brun et olive, taille basse en biais, longue
  jupe froncée bordeaux. ⛔ **Elle n'est dans aucune des 18 pièces du catalogue.** Une pièce
  absente de son catalogue ne va pas au salon (`PROMPTS-ROBES-3D.md`, règle 1). 🙋 Mongazi : est-ce une
  création d'Hillary qui n'est pas sur le site (photo reçue sur WhatsApp), ou une image ratée ?

### Le salon : pourquoi les images ne se ressemblent pas, et ce qu'elles ont en commun

**Ce qui change d'une image à l'autre** : la forme du plafond (coupole ronde, ovale, double anneau,
vague), **le logo** (le vrai, au mannequin magenta, sur sept images ; un « H.M.S » à empattements qui
n'est pas le sien sur `trois-podiums`), le comptoir (arrondi bois et or, droit, blanc), le nombre de
mannequins (2 à 5), la place de la vitrine et de la cabine. **La raison** : le générateur ne garde
aucune mémoire d'une image à l'autre. Décrire les ingrédients ne fixe pas le plan, et chaque image
réinvente la pièce.

**L'ADN commun aux huit** (ce qui fait « sa » boutique, à garder) : sol crème **très brillant qui
reflète tout**, plafond clair à **gorge lumineuse dorée sur une courbe** et spots encastrés, podiums
ronds blancs, mannequins blancs, étagères de bois clair pleines de wax pliés, logo magenta
rétroéclairé, comptoir bois et laiton, velours magenta (rideau de cabine, banc), plantes
tropicales, grandes baies vitrées sur une rue de jour. C'est **l'étalon de `REALISME.md`** (podiums
crème, sol qui reflète, spots, ligne lumineuse sur une courbe), en plus complet.

**Trois écarts avec le salon 3D actuel, à trancher par Mongazi** :
1. 🙋 **La lumière** : ses huit images sont **claires, de jour, crème et blanches**, l'inverse du
   « tamisé et ultra stylé » demandé le 2026-11-12 (murs expresso, plafond brun nuit). Le salon suit
   l'heure réelle de Cotonou : **proposition, le jour comme ses images, le soir tamisé.**
2. Le plan isométrique annonce **14 m × 14 m × 10 m** : les cotes sont inventées par le générateur
   (10 m sous plafond est impossible, le dessin montre environ 3,5 m). Le salon garde
   `plan.json` (16 × 12 × 4,2 m) tant que Mongazi ne dit pas autre chose.
3. Il apporte ce que le salon n'a pas : **une cabine d'essayage** à rideau magenta, **des portants
   dorés**, **un écran vertical** (le TikTok d'Hillary), **un banc de velours**, une vitrine en angle.

⛔ **Les robes portées par les mannequins de ces vues ne sont PAS les siennes** (des fourreaux
magenta génériques, des wax inventés). Ces vues servent de **référence d'ambiance et de plan** ;
elles ne se montrent jamais à un visiteur comme son catalogue. Les podiums du salon portent SES
pièces (planches ci-dessus, puis 3D).

**La méthode pour ne plus courir après la constance** : on n'a pas besoin que les images se
ressemblent entre elles, **la 3D est la constance**. Il suffit d'**une** image de référence pour le
plan (`salon-plan-iso`) et d'**une** pour la lumière (`salon-vue-comptoir-arche`) ; je construis la
pièce en 3D, et chaque « vue » devient une caméra dans la même pièce. Pour des images fixes (affiche,
teaser), le chemin sûr est **le rendu 3D → photo** : je fais une capture du salon 3D depuis l'angle
voulu, et Nano Banana Pro la rend photographique **sans toucher à la géométrie** (consigne à écrire le
jour venu). À défaut, toujours joindre la même image maîtresse et changer une seule chose par demande.

### Ce qui attend

- 🙋 Mongazi : finir les plans (salon et personnages) · les six expressions du visage d'Hillary ·
  son accord écrit · la pièce de `robe-inconnue` · les consignes C de h1 et h2 · **jour clair et nuit
  tamisée, oui ou non**.
- 🤖 Moi, quand il dira « intègre » : Afi refaite en 3D (nouvelle image), Sènami et Maman en 3D, le
  plan du salon revu d'après `salon-plan-iso` (cabine, portants, écran, banc), la lumière de jour.
