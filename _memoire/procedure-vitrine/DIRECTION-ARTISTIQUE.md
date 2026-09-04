# DIRECTION ARTISTIQUE — le standard « 100 000 € »

> **À lire AVANT d'écrire une seule ligne de CSS, sur CHAQUE vitrine, sans exception.**
>
> Origine : 2026-08-01. Mongazi regarde une vitrine techniquement irréprochable et dit :
> « je vois un site à 100 $ ». Il avait raison. Ce document existe pour que ça n'arrive
> plus jamais.
>
> Référence d'exécution : `clients/10-hillary-m-styl/` (direction « LE FIL »).

---

## 0. La règle

**Une vitrine NEBULA n'est pas finie quand elle marche. Elle est finie quand elle
impressionne.** Le QC vert prouve que rien n'est cassé ; il ne prouve pas que c'est beau.
Ce sont deux critères de sortie, pas un.

Et la réponse à « ça fait cheap » n'est **jamais** « ajouter des animations ».
C'est **trouver l'idée**.

---

## 1. D'abord l'idée, sinon rien ne tient

Avant toute chose, écrire **une phrase** qui dit ce qu'est ce métier, vu de l'intérieur.
Pas ce qu'il vend : ce qu'il *est*.

| Client | La phrase | Ce qu'elle a produit |
|---|---|---|
| HILLARY M. STYL | « Une maison de couture, c'est **un fil** qui va du mètre-ruban au vêtement fini. » | le rideau au fil, la piqûre, le patron à la craie, la coupe aux ciseaux, l'aiguille-curseur |
| Weinkeller by CK | « Une cave, c'est **une descente** au frais, loin du bruit. » | le seuil-éclair, les silhouettes de bouteilles, le coverflow 3D |
| Au Braisé d'Or | « Un braisé, c'est **la braise** avant le plat. » | charbon + ember + verre fumé, ambiance sonore braise |

**Le test :** si la phrase pourrait s'appliquer à un autre client, elle est trop vague.
Recommencer. Une bonne phrase contient un **objet concret du métier** — un fil, une braise,
une descente — parce que c'est de cet objet que sortiront les animations.

Tout ce qui suit découle de la phrase. **Sans elle, on décore ; avec elle, on raconte.**

---

## 2. Les trois choses qui font 80 % de l'écart, et aucune n'est une animation

C'est la partie que tout le monde saute. C'est celle qui compte le plus.

### 2.1 La typographie
Une police de titre **à caractère**, à **très gros corps**. C'est le premier signal de prix.

| Registre | Display | Exemple NEBULA |
|---|---|---|
| Mode, couture, beauté, joaillerie | **Didone** (Bodoni Moda, Playfair) | Hillary M. Styl |
| Artisanat, bois, matière, restaurant | **Garamond / humaniste** (Cormorant) | HH Design |
| Commerce, tech, énergie | **Grotesque à caractère** (Bricolage, Anton) | Miss cakes, Speed |

Règles dures :
- `clamp()` jusqu'à **6 rem** en héros. En dessous de 40 px sur mobile, ça ne fait jamais cher.
- **Ne jamais apparier deux polices du même genre.** Serif + sans, ou une seule famille en plusieurs graisses.
- Un **italique de la display** en accent coloré vaut dix effets. C'est gratuit et ça se remarque.
- Interdits durables : Montserrat, Inter, Roboto, Poppins en display. Ce sont les polices du gratuit.

### 2.2 Le rythme des fonds
**Alterner sombre et clair, section par section.** Sans alternance, tout se vaut et rien ne ressort.

```
héros SOMBRE → ruban ACCENT → section CLAIRE → section PAPIER (clair plus dense)
→ section SOMBRE → section CLAIRE → contact SOMBRE → pied NOIR
```

Et **jamais de noir pur** (`#000`) ni de blanc pur (`#fff`) en fond : une encre
(`#0B0A0C`) et un papier (`#F4F1EC`). Le noir pur est le fond de celui qui n'a pas choisi.

### 2.3 Le vide
Un héros qui remplit l'écran fait pauvre. Un héros qui **respire** fait cher.
Marges généreuses, `padding` de section ≥ 90 px, une seule idée par écran.

**Si la moitié droite est vide en grand écran, ce n'est pas un défaut** — c'est une place.
On y met un dessin au trait, une photo, un objet. Voir §4.

---

## 3. Une animation signature DIFFÉRENTE par section

C'est déjà la règle NEBULA (Miss cakes, Djambar, Grain d'Esthétique). Le standard ajoute
une contrainte : **chaque animation doit sortir de la phrase du §1.**

Une animation qui pourrait être copiée-collée chez un autre client est une animation ratée.

### Le gabarit qui marche

| Moment | Rôle | Exemple « LE FIL » |
|---|---|---|
| **Ouverture** | on entre quelque part | le fil descend, le monogramme paraît, deux pans de tissu s'écartent |
| **Héros** | l'objet du métier apparaît | titre à la craie ligne par ligne, **croquis qui se dessine**, mètre-ruban gradué |
| **Section 1** | le geste du métier | **la piqûre** : un point de couture se coud d'un bloc à l'autre au défilement |
| **Catalogue** | la matière | **le patron à la craie** : contour pointillé tracé autour de chaque carte, en cascade |
| **Méthode** | le temps qui passe | **le fil qui relie** les étapes, la perle avance avec le défilement |
| **À propos** | la confidence | **le drapé** : le texte se dévoile par plis, les chiffres se comptent |
| **Contact** | l'acte final | **la coupe** : la ligne traverse, les ciseaux la suivent, le titre se révèle |
| **Modale / tunnel** | le carnet de l'artisan | la feuille se lève, les champs se posent un à un, la date se **tamponne** |

### Le détail permanent
Ces quatre-là ne coûtent presque rien et changent tout :
1. **Un grain** (SVG `feTurbulence` en data-URI, opacité 4-5 %, `mix-blend-mode`)
2. **Une barre de progression** fine dans la couleur d'accent
3. **Un curseur métier** sur ordinateur (aiguille, lame, verre…), aimanté par les boutons
4. **Un ruban défilant** avec les mots du métier

### Les techniques, sans aucune bibliothèque
- révélations : **un seul** `IntersectionObserver`, classe `.vu`, délai par `--d`
- scroll-driven : **une seule** boucle `requestAnimationFrame`, `scrollY` lu une fois
- tracés : `stroke-dasharray` / `stroke-dashoffset` sur SVG (croquis, patron, piqûre)
- révélations de texte : `clip-path: inset()` ou masque `overflow:hidden` + `translateY`
- compteurs : `requestAnimationFrame` + `1 - (1-k)³`

---

## 4. Les images : ce qu'on a le droit de faire, et ce qu'on n'a pas le droit

**INTERDIT ABSOLU : générer par IA une photo de produit qu'on présente comme le catalogue
du client.** Une cliente qui commande sur la photo d'une robe que l'atelier ne fabrique
pas, c'est la maison qui paie à la livraison. Cette règle ne souffre aucune exception,
même « juste pour la démo », même « on remplacera après ».

**AUTORISÉ :** ambiance, matière, texture, arrière-plan, éditorial — ce qui ne prétend pas
être un article vendable (précédents : Miss cakes, Au Braisé d'Or).

**Ce qu'on fait quand il n'y a pas de photos** — et c'est presque toujours le cas :
1. Un **dessin au trait animé** de l'objet du métier (croquis de robe, bouteille, meuble),
   en SVG qui se trace. Coût : 2 Ko. Effet : maximal. C'est ce qui remplit le vide du héros.
2. Des cartes avec un **visuel de substitution élégant** marqué « photo à venir » —
   jamais un carré gris, jamais un vide.
3. Le héros est **construit pour recevoir une vraie photo** le jour où elle arrive.

Et on le dit au client : **les vraies photos sont le dernier palier**, celui qu'on ne peut
pas franchir à sa place.

---

## 5. Regarder, pas seulement tester

**Le QC automatique protège la logique. Il ne protège pas le goût.**

Sur la vitrine Hillary, six défauts sont passés au travers de 53 contrôles verts et de
plusieurs relectures du code. Ils ont tous été trouvés **en regardant les captures, écran
par écran** :

| Défaut | Pourquoi le code ne le montrait pas |
|---|---|
| La « coupe » du titre cassait à deux lignes | le procédé supposait une hauteur de bloc connue |
| Le survol restait collé après un appui | `:hover` n'existe pas au clavier ni au test |
| « 45 000 F » se coupait en deux | dépend de la largeur réelle de la carte |
| L'anneau du curseur traînait en 0,0 | état initial jamais joué en test |
| L'icône du mètre-ruban était illisible | 30 px, ça ne se lit pas dans le DOM |
| Le croquis débordait de l'écran | rapport largeur/hauteur × viewport |

**Procédure obligatoire avant de dire « fini » :**
1. Capture de **chaque section**, en **390 px** et en **1440 px**
2. Les **regarder une par une** et écrire ce qui cloche
3. Corriger, recapturer, recommencer
4. Le QC vert ne remplace jamais cette étape

⚠️ **Émulation obligatoire** (Playwright `is_mobile=True`). Une capture headless sans
émulation ignore le `meta viewport`, rend à 800 px et fait croire à des débordements qui
n'existent pas.

### 5 bis. Photographier une MODALE : deux façons évidentes, deux images fausses

*(leçon Hillary du 2026-09-04 — vaut pour toute modale, tout tiroir, tout panneau)*

- ⛔ **`full_page=True`** photographie tout le document. Une modale est un
  `position:fixed` posé au-dessus d'un catalogue qui peut faire **28 000 px** : elle y est
  un timbre-poste.
- ⛔ **La capture de l'élément** (`.sheet`, `.modale`…) a l'air d'être la bonne réponse, et
  c'est pire. Une barre ou un pied `position:sticky` **se repeint au bord de la fenêtre**
  et recouvre tout ce qui suit. Sur les deux premières planches, les blocs que je venais
  précisément vérifier **étaient absents de l'image, sans le moindre signal**.
- ✅ **Une fenêtre assez haute pour que toute la modale y tienne** (390 × 2600,
  1440 × 2000) et une capture de fenêtre ordinaire. La **largeur** reste réelle : c'est
  elle qui fait la mise en page, et le débordement horizontal reste mesuré par le QC aux
  vraies hauteurs.

⚠️ **Photographier chaque ÉTAT, pas seulement l'état plein** : formulaire vide, un seul
champ rempli, bouton grisé. C'est dans l'état intermédiaire que se cachait le vrai défaut
du jour — un bouton désactivé qui ne disait pas pourquoi.

### 5 ter. L'angle mort : le contraste DANS une modale

Les contrôles de contraste lisent `background-color` **sur l'élément qui porte le texte**.
Dans une modale, cet élément est presque toujours transparent : la couleur vient d'un
ancêtre. Ils lisent `rgba(0,0,0,0)` et **ne mesurent rien**.

→ **Remonter jusqu'au premier ancêtre dont le fond est vraiment opaque**, puis choisir le
seuil sur la taille réelle lue dans `getComputedStyle` (3,0 au-delà de 24 px ou 18,66 px
en gras, 4,5 sinon).

⛔ **La couleur de marque sert au TRAIT, jamais à la LETTRE.** Chez Hillary, le rose
`--rose` a été posé sur du texte **quatre fois** (étiquette du carrousel, badge, bouton
WhatsApp, puce de recopie à 3,91:1). Prévoir dès la palette **deux valeurs** : la vive pour
les contours et les aplats, une foncée pour tout ce qui se lit.

⚠️ Ça ne vaut **pas** pour un texte posé sur une photo : là, on masque le texte, on
photographie, et on prend le décile le plus clair (leçon Angy Art du 2026-08-08).

---

## 6. Le luxe ne s'achète pas en images par seconde

Trois garde-fous, non négociables, qui sont eux aussi des contrôles automatiques :

1. **`prefers-reduced-motion`** respecté : tout s'arrête pour qui en a besoin.
2. **Sur téléphone**, on fige ce qui coûte : grain non animé (la texture reste, le repaint
   disparaît), une nappe floutée en moins, blur réduit.
3. **Aucune animation infinie sous un `backdrop-filter`** (leçon Boussole 2026-07-21) et
   **jamais de `transform` sur un écran contenant un `position:fixed`** (leçon FAB 2026-07-25).

Et toujours : **aucune bibliothèque**. Tout ce qui précède tient en CSS + ~150 lignes de JS.

---

## 7. Source, construction, livrable

Dès qu'une image en base64 entre dans un fichier (donc : toujours, sur une vitrine
mono-fichier), on sépare :

```
_vitrine_src.html   ← LA SOURCE, c'est elle qu'on édite (marqueurs __LOGO_B64__)
_build.py           ← injecte les images → écrit le livrable
_qc.py              ← la suite de contrôle, doit être verte avant tout déploiement
vitrine.html        ← LE LIVRABLE, généré, JAMAIS édité à la main
```

Gabarits prêts à copier : `_memoire/procedure-vitrine/templates/`.

Sans ça : un HTML illisible où le code utile est noyé dans 75 Ko de base64, et l'invitation
à dupliquer le logo — c'est ce qui avait fait un fichier de 681 Ko sur la première version.

### 7 bis. Une chaîne en deux temps se lance en deux temps

Quand un site gagne un assembleur (Hillary : `_v4/_assembler.py` recompose la source à
partir de morceaux, **puis** `_build.py` en tire le livrable), **le script de déploiement
doit partir de la source la plus amont**.

⛔ Celui d'Hillary ne lançait que le build. Modifier un morceau puis déployer publiait un
livrable bâti sur une source **périmée** : QC vert, déploiement réussi, changement absent
du site — **sans un mot**. Le défaut était noté dans la documentation depuis le 2026-08-16
et n'avait jamais été refermé : **un défaut écrit dans une phrase n'est pas un défaut
corrigé.**

### 7 ter. Le `?v=` et le `_headers` vont ensemble

- **Avec** un `_headers` qui pose `immutable` sur `/assets/*` : les fichiers sont mis en
  cache **un an**, donc **toute modification d'un asset exige de bumper son `?v=`**. Oublier
  le bump laisse le client sur l'ancienne version, et ça **ne se voit ni depuis le serveur,
  ni dans un QC, ni dans une comparaison MD5 de la page servie** (Angy Art, 08/08 et 04/09).
- **Sans `_headers`** : Cloudflare Pages sert `max-age=0, must-revalidate` sur tout. Aucun
  risque de cache périmé, mais **aucun cache non plus** — chaque visite revalide toutes les
  images, sur la 3G de Cotonou. Et **aucun en-tête de sécurité**.

⚠️ **Mesuré le 2026-09-04 : 10 sites du parc sur 15 n'ont pas de `_headers`.** Voir
`_memoire/RESTE-A-FAIRE.md`.

---

## 8. La question finale, avant de livrer

Trois questions dans cet ordre. Tant qu'une réponse est non, ce n'est pas fini.

1. **« Quelle est la phrase ? »** Si je ne peux pas la dire en une ligne, il n'y a pas de
   direction artistique — il y a de la décoration.
2. **« Est-ce que chaque animation vient du métier ? »** Si une seule pourrait être
   copiée-collée chez un autre client, elle est à refaire.
3. **« Si je mets ce site à côté du précédent, se ressemblent-ils ? »**
   *(règle d'or Mongazi du 2026-06-25)* Si oui → retravailler jusqu'à ce que non.

Et la seule qui compte vraiment, celle de Mongazi :

> **« Est-ce que le client est abasourdi ? »**

---

*NEBULA Agency · Cotonou · Standard applicable à toutes les vitrines à partir du 2026-08-01.*
