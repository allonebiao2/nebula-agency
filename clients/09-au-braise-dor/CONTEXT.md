# AU BRAISÉ D'OR — client 09

> ## 🔥 EN LIGNE : **https://au-braise-dor.pages.dev**
> **⚠️ LE SITE N'EST PLUS `index.html`.** Depuis le 2026-08-12 l'adresse du
> client sert le projet **Next.js de `experience/`** : **le héros des 14 sauces**
> (2026-08-26, voir plus bas), puis les 52 plats commandables en dessous.
> `index.html` reste dans le dépôt : un retour arrière est un déploiement.
> ⚠️ **Mais `index.html` reste LA VÉRITÉ DES DONNÉES** : son tableau `CATS` et
> sa table `PHOTO` sont lus par `node _outils/_extraire_carte.js`, qui écrit
> `experience/data/carte.ts`. On n'édite jamais `carte.ts` à la main.
>
> **Publier :**
> ```bash
> cd clients/09-au-braise-dor/experience
> npm run build
> cp -r ../assets/docs out/     # l'affiche A4 et ses QR gardent leur adresse
> npx wrangler pages deploy out --project-name au-braise-dor --branch main
> ```
> ⚠️ **L'alias Cloudflare a du retard** : un fichier peut répondre 404 huit
> secondes après le déploiement et 200 quinze secondes plus tard.
>
> **Pile technique demandée par Mongazi** (j'avais recommandé le natif, il a
> maintenu, c'est son choix) : Next.js 14 · TypeScript · Tailwind · GSAP +
> ScrollTrigger + CustomEase · Swiper · Lenis. **179 kB de JS** au premier
> chargement.
>
> **Détail complet :**
> `_memoire/conversations/2026-08-12-braise-experience-next.md`

## ⚠️ LES SEPT PIÈGES DE CE PROJET, tous trouvés à la mesure

1. **Les 48 photos en `background-image` se téléchargeaient d'un coup** :
   4,3 Mo avant même d'arriver au menu. Un navigateur ne sait pas différer un
   fond CSS. → `<img loading="lazy">`.
2. **`gsap.from()` laisse l'élément invisible si on l'interrompt.** Le bouton
   « Commander sur WhatsApp » était à `visibility: hidden` : la carte
   s'affichait complète, sauf le seul bouton qui rapporte de l'argent.
   → `fromTo()` + `clearProps`, partout, sans exception.
3. **Une scène en `fixed` ne se décolle jamais** et reste en travers du
   contenu suivant. → `sticky` dans un parent de N × 100vh.
4. **On n'empile pas des boîtes à la main sur téléphone** : un pourcentage de
   hauteur ne sait rien de la hauteur en pixels du texte. → conteneur en
   `display: contents` sur grand écran, **colonne flex** sur téléphone.
   ⚠️ Et en `width: auto` une boîte dont les enfants sont tous absolus est
   mesurée à **zéro de large** : l'assiette disparaissait.
5. **Un conteneur plein écran avale les clics** des boutons posés avant lui.
   Le bouton du héros s'illuminait au survol et ne faisait rien.
   → `pointer-events-none`.
6. **LENIS TIENT LE DÉFILEMENT DE LA PAGE.** Tout `scrollIntoView` lancé à côté
   se fait interrompre : le saut vers une catégorie s'arrêtait à **7 382 px**
   de sa cible, sans erreur en console. → `components/aller.ts`.
7. **Une vidéo de référence se MESURE image par image** avant d'écrire
   l'animation, elle ne se résume pas de mémoire. Les assiettes **roulent sur
   un arc** (haut droite → bas gauche, presque un quart de tour), elles ne
   montent pas tout droit.

## Ce qui est en ligne

**L'expérience** : 4 plats signature, défilement **automatique** (5,5 s) avec
cinq garde-fous, titre en deux lignes qui se dédouble, carte de verre, prix qui
compte de 0, carrousel Swiper à item surélevé, tiroir des 8 univers ouvert
depuis le héros.
**La carte** : 48 plats **toujours tous affichés** (le filtre cachait 38
plats), chips en ancres avec scroll-spy, fiche taille + accompagnement +
quantité, panier, mode, message WhatsApp rédigé.
**Le pied** : les deux numéros, l'email, le WiFi, les horaires, le traiteur, la
place des fêtes, **RC RB/COT/24 A 102350 · IFU 0202501441177**.

⛔ **NI NOTE, NI CHEF, NI « LIKES » INVENTÉS.** La vidéo de référence en
affichait ; ce restaurant existe. Le carré coloré porte **le prix**, qui est
vrai. Les champs `chef` et `avis` attendent dans `data/dishes.ts` et
s'afficheront tout seuls le jour où le restaurant les donnera.

## Les outils

| Fichier | Ce qu'il fait |
|---|---|
| `_outils/_extraire_carte.js` | relit `index.html` et régénère `experience/data/carte.ts` (8 catégories, 48 plats). **La carte ne se retape jamais à la main** |
| `_outils/_carte_claire.py` | passe la carte et le pied dans la langue du héros |
| `_outils/_catalogue_vente.py` | ancres + scroll-spy + tiroir des catégories |

⚠️ Les trois **s'arrêtent net si un motif a disparu**, pour ne jamais repeindre
à moitié.

## ✅ LA CARTE DES SAUCES, ET TROIS VRAIES PHOTOS — 2026-08-19 (nuit, 2)

La maison envoie **sa feuille de menu des sauces** (`_partage/2026-08-19-menu-sauces.jpeg`)
et **trois photos de plats**. Mongazi : « ce sont de vraies images de plats
béninois que j'ai améliorées avec l'IA, donc on peut les utiliser ».
**La règle du 2026-08-01 ne s'y applique pas** : ce ne sont pas des images
générées. Les originaux restent dans `_partage/`, la vérification reste possible.

### ⚠️ LE PRIX EST UNE FOURCHETTE, PAS DEUX TAILLES
Mongazi : « le prix varie en fonction des éléments entre parenthèses ; en
fonction de ce que le client veut dans les parenthèses, le prix augmente. »
**J'avais d'abord lu « 1 500-3 000 » comme Normal/Grand.** C'était faux, et le
panier aurait annoncé un total que la maison n'aurait pas tenu.

Nouveau modèle dans les données : **`pMax`** (borne haute) et **`garn`** (ce
qu'on peut mettre dedans). Plus **`tailles`**, pour les deux formats du yassa au
poulet, qui ne s'appellent pas « Normal / Grand » mais « Quart / Demi-poulet ».

Dans la page : la carte affiche **« 1 500 à 3 500 F »**, la fiche propose
**« Ce que vous voulez dedans »** (cases à cocher), et **le total du panier est
lui-même une fourchette**. ⛔ **On n'annonce aucun prix par ingrédient** : la
maison n'a donné qu'une fourchette, un chiffre en face de chaque case serait
inventé. Le message WhatsApp porte les choix, la fourchette, et la phrase
« merci de me le confirmer ».

### ⚠️ LA RÈGLE DE PRIX, PRÉCISÉE PAR MONGAZI (nuit, 3)
> « Un client qui veut commander une sauce doit, après avoir choisi la sauce,
> choisir un accompagnement. Les plats varient de 1 500 à 3 000 F en fonction
> des éléments qu'ils veulent à l'intérieur — entre parenthèses. **Quand on met
> tout dedans, c'est le prix le plus cher.** »

Cette dernière phrase change tout : **deux cas sur trois deviennent EXACTS.**

| Ce que le client choisit | Prix affiché | Au panier |
|---|---|---|
| **rien dedans** | **1 500 F** exact | 1 500 F |
| une partie | **1 500 à 3 500 F** | fourchette, la maison confirme |
| **tout dedans** | **3 500 F** exact | 3 500 F |

⛔ **On n'interpole pas entre les deux.** La maison n'a jamais donné le prix
d'un ingrédient pris séparément : deux bornes connues ne font pas un barème.
Le cas « une partie » reste donc une fourchette assumée, et le message WhatsApp
demande la confirmation.

✅ **L'accompagnement est OBLIGATOIRE.** Le bouton reste bloqué sur
« Choisissez un accompagnement » tant qu'il n'y en a pas — une commande sans
accompagnement arrive incomplète en cuisine, et c'est le restaurant qui doit
rappeler le client. Vaut pour les sauces **et les grillades**, les deux
catégories qui proposent des accompagnements. Deux contrôles le vérifient :
bloqué sans, débloqué avec.

### La catégorie passe de 4 à 14 sauces
Les 10 de la feuille (gombo, krinkrin, feuille, arachide, graine, tomate, tête
de mouton, pieds de bœuf, yassa, yassa au poulet) rejoignent les 4 de l'ancien
menu. Les **accompagnements sont remplacés** par la liste de la feuille (15,
de telibo à toubani).

### Le héros : QUE des sauces
Mongazi, en regardant le héros en ligne : « je veux qu'ici ce soient les sauces
qui soient mises en avant, **que les sauces** ». Le poulet bicyclette, le
tilapia et le chawarma JOQ **sortent du héros**. Ils restent à la carte et se
commandent comme avant : ce n'est pas un retrait de plat, c'est un choix de
vitrine — un restaurant béninois montre ses sauces.

⚠️ **Trois, et pas plus** : ce sont les seules sauces dont la maison a envoyé
la photo, et le héros vit de l'image (une ardoise en plein écran ne vend rien).
Moyo Chigan et Sauce poisson frais ont bien un détourage, mais fait à partir
d'une image **générée** de juillet : les mettre là, c'est ouvrir le site sur de
l'IA. Elles y entreront le jour où la maison les photographie.

### Le héros : trois vraies photos en tête
Sauce gombo, Sauce krinkrin, Sauce feuille, puis poulet, tilapia, chawarma.
⚠️ **L'appariement photo ↔ sauce est vérifié, pas deviné** : la feuille porte
trois vignettes imprimées et **la forme de l'assiette concorde** (gombo
octogonale, krinkrin octogonale sur ardoise, feuille hexagonale).

### Les détourages de la maison : `python _outils/_damier.py`
Mongazi renvoie les trois plats **déjà détourés**, mais les fichiers arrivent en
**RGB sans canal alpha** : le damier gris de son éditeur est **peint dans les
pixels**. Il faut donc redétourer, en traitant le damier comme un fond.

⛔ **Quatre tours perdus à vouloir le faire « proprement »** : apprendre les deux
gris sur les coins, remplir depuis les bords, ponter les pixels de transition,
rembourrer pour que l'érosion ne mange pas l'anneau du bord, reconstruire la
grille pour ne retirer que ce qui coïncide avec elle. Échec de fond : **sur le
gombo les deux gris du damier sont 77 et 124, et le bord noir de l'assiette a
des reflets dans cette plage.** Aucun seuil de luminance ne les sépare.
✅ **rembg sort les trois d'un coup, sans une bavure** : un modèle de saillance
ne se demande pas de quelle couleur est le fond, il voit une assiette.
⚠️ Et ici **`isnet` gagne**, alors que birefnet gagnait sur les mêmes plats
photographiés sur fond noir : **le fond change, le gagnant change.**

⚠️ **Piège d'archivage** : j'avais copié dans `_partage/` *mon masque raté* au
lieu des fichiers de Mongazi, et rembg a donc travaillé sur une image déjà
abîmée — assiette perdue. **Ce qu'on archive doit être la source reçue, jamais
un intermédiaire.**

### Le détourage : `python _outils/_photos_sauces.py`
Deux formes par photo : **carré opaque** pour la carte, **détouré RGBA** pour le
héros. Le carré n'est pas un recadrage aveugle — il se centre sur l'assiette
grâce au masque, un recadrage centré coupait le bord sur deux des trois photos.
⚠️ **MODÈLE : `birefnet-general` ICI, `isnet` POUR LES BOLS.** Planche
comparative : sur ces photos — **assiettes noires sur fond noir** — isnet garde
une tache de vapeur pleine au-dessus du krinkrin, une encoche dans l'assiette de
la feuille et un bout d'ardoise ; birefnet découpe la masse du plat proprement.
Sur les bols de `_detoure_plats.py`, c'est **exactement l'inverse**.
→ **Refaire la planche à chaque nouveau lot, ne pas présumer.**

## ✅ LE HÉROS PASSE AUX SAUCES — 2026-08-19 (nuit)

> Mongazi : « c'est un restaurant béninois, donc les plats de la catégorie
> sauce doivent être mis en avant plus que les autres ; dans la héros section
> ce sont ces plats-là qui défileront automatiquement. Les autres aussi bien
> sûr, mais ces plats-là en principal. »

**Le héros passe de 4 à 6 plats, les deux sauces en tête** : Moyo Chigan et
Sauce poisson frais, puis Poulet bicyclette, Tilapia braisé, Pizza Paysanne,
Chawarma JOQ.

### Pourquoi CES deux sauces et pas les quatre
Le menu papier range les sauces en **deux sections** : « Monyo » (les locales)
et « Sauces Européennes ». **Béchamel et Sauce Crème sont les européennes** :
les mettre en avant pour dire « c'est un restaurant béninois » dirait le
contraire de l'argument. Elles restent à la carte, pas au héros.
⚠️ Et leur détourage est raté (voir ci-dessous), ce qui tranche la question.

### Le détourage : `python _outils/_detoure_plats.py`
Le héros pose l'assiette sur un fond crème, donc **toutes les images de
`public/plats/` sont en RGBA**, contrairement à celles de `public/carte/`.
Les sauces n'en avaient pas : elles ont été détourées depuis leur image carrée.
- **Modèle `isnet-general-use`**, choisi sur planche comparative : `u2net` perd
  le bol et ne garde que la viande, `birefnet-general` déchiquette le bol.
  isnet garde le bol entier **et la vapeur**, qui fait tout le charme.
- ⛔ **Ce qui ne marche pas** : sur Béchamel et Crème, isnet garde un bout de
  l'ardoise sous le bol. L'ouverture morphologique qui devait l'enlever **mord
  dans le bol** et laisse une encoche — pire que le mal. Ne pas refaire l'essai.
- La **teinte du prix est relevée sur la photo** (méthode Hillary) : Moyo
  `#B25324` (5,05:1 avec le blanc), Poisson frais `#8A3520` — les deux sauces
  partagent leur dominante tomate, il fallait les distinguer sans mentir.

### ⏳ Ce qui manque pour aller au bout
**Gombo, krinkrin et sauce feuille — les plus béninoises de toutes — n'ont
aucune photo sur le disque.** Les images envoyées par Mongazi sont arrivées
dans la conversation, pas comme fichiers. Le jour où elles atterrissent dans
`_partage/`, elles prennent la tête du héros.
⚠️ **Et il faudra d'abord savoir d'où elles viennent** : fond noir, vapeur,
lumière de studio — elles ont l'allure des 48 images générées de juillet. Si
elles sont générées, la règle du 2026-08-01 les refuse, et ce serait la
première fois qu'on en ajoute une **après** la règle.

## ✅ CORRECTIONS DE LA PROPRIÉTAIRE — 2026-08-19 (soir) · **52 → 42 plats**

Note manuscrite « Correction pour Au Braisé d'Or », photographiée et transmise
par Mongazi. **Les prix en place sont validés** (« la propriétaire n'est pas
contre »). Elle demande des retraits et une catégorie de plus.

### 13 plats retirés
| Catégorie | Retiré | Reste |
|---|---|---|
| **Pizza** | napolitaine · oriental · margherita · pili chaud · à la crème · **pêcheur** | 4 sur 10 |
| **Grillades** | **le lapin seul** · viande de caille — ✅ **le mouton frit reste, même prix** (Mongazi, 19/08 au soir) | 5 sur 6 |
| **Chawarma** | rien (elle l'écrit) | 3 |
| **Hamburger** | crispy poulet · nugget pomme au four | 7 sur 9 |
| **Cocktails** | « on supprime tout sauf les jus de fruit » → mojito, piña colada, JOQ Viagra | 3 sur 6 |

Salades, sauces et petit-déjeuner : rien à changer.

### Une catégorie ajoutée : **Desserts** (yaourt, glace)
⚠️ Le « cocktail » qu'elle listait **en a été sorti le soir même** (Mongazi) :
il faisait doublon avec les 3 cocktails de fruits à 2 500 F, dans deux onglets
et à deux prix.
⏳ **Aucun prix donné.** Mongazi les demandera plus tard : on garde
« Prix sur demande », c'est assumé, pas un oubli. Les trois portent **« Prix sur demande »** et
leur fiche envoie la question sur WhatsApp au lieu d'ajouter au panier.
Convention posée dans les données : **`p:0` = prix pas encore donné**. On
n'invente pas un prix, et on ne cache pas une catégorie qu'elle veut vendre.
⚠️ Un article à 0 ne doit jamais entrer au panier : le total mentirait et le
message WhatsApp partirait avec un « 0 F ». Un contrôle vérifie qu'aucun
« 0 F » n'apparaît nulle part.

### ⚠️ Ce que le retrait a cassé, et qu'il fallait réparer
1. **La pizza pêcheur était un des 4 plats signature du héros.** Un héros ne
   peut pas mettre en avant un plat qu'on ne peut plus commander : le visiteur
   arrive, s'enthousiasme, et ne le trouve nulle part. → **paysanne**, seule
   pizza restante à deux tailles, donc au même rôle sur la carte.
   ⚠️ Elle réutilise l'image générée de l'ancienne pizza, qui ne représente
   aucun plat réel : à revoir avec la décision sur les 48 photos.
2. **Deux notes de catégorie devenaient fausses.** Les hamburgers disaient
   « sauf végétarien, crispy, nugget » alors que crispy et nugget sont partis ;
   les cocktails annonçaient « avec ou sans alcool » alors qu'il n'y a plus
   d'alcool. Réécrites. **Retirer un plat ne suffit pas : il faut relire ce que
   la page dit encore de lui.**
3. Les trois cocktails restants répétaient « Sans alcool. » en fin de
   description, ce que la note de catégorie dit désormais une fois pour toutes.

### ⏳ Les trois questions qui restent (détail en bas de `MENU.md`)
1. **Prix du yaourt et de la glace** — ⏳ Mongazi les demandera plus tard, les
   deux desserts restent en « Prix sur demande » en attendant.
2. **Aileron** : le prix corrigé au surligneur sur le papier.
3. **Le n° WhatsApp.**

✅ **Deux tranchées par Mongazi le soir même** : le mouton frit reste au même
prix (seul le lapin part) — ⚠️ **on avait retiré la ligne entière et donc
supprimé un plat que la maison vend toujours** — et le « cocktail » sort des
desserts.

✅ **Deux questions de la passe précédente sont mortes d'elles-mêmes** : les
2ᵉˢ tailles de la napolitaine et de l'oriental, et le prix de la pêcheur — les
trois pizzas sont retirées.

**QC : 64 contrôles verts**, dont un par plat retiré (il ne doit réapparaître
ni par une régénération ni par un retour en arrière mal ciblé).

## ✅ PASSE CATALOGUE DU 2026-08-19 — la carte relue contre le menu papier

**On est remonté aux 5 photos du menu** (`_partage/photo_*_2026-07-17_*.jpg`),
recadrées et agrandies, plutôt qu'au `MENU.md` qui en était le résumé. Trois
choses en sont sorties.

### 1. Le catalogue ne contenait pas tout le menu — **48 → 52 plats**
Le petit-déjeuner du papier compte **10 lignes**, le site n'en montrait que
**6**. Manquaient : **café chaud serré (500 F)**, **Lipton citron (500 F)**,
**œuf sur plat (1 000 F)** et **café au lait écrémé (1 000 F)**. Quatre choses
que la maison vend, tous les matins, et qu'on ne lui proposait pas.
Ajoutées dans `index.html` (la vérité), carte régénérée par
`node _outils/_extraire_carte.js`.

### 2. Le prix était **illisible sur les 52 cartes**
La pastille de prix n'avait **aucune couleur de texte** : elle héritait de
`--encre` (`#1d1a17`) et posait de l'encre noire sur un fond noir à 65 %.
Contraste mesuré sur les pixels rendus : **1,1:1**. Le minimum lisible est
4,5:1. Autrement dit le seul chiffre que le client cherche n'était pas là.
→ texte en `#f6efe6`, pastille à 70 %, **mesuré entre 13,9:1 et 18:1**, et un
contrôle le garde désormais.

### 3. Un plat sans photo a maintenant une place : **l'ardoise**
⛔ Ni cadre vide, ni « photo à venir » : le premier dit que le site est en
travaux, le second que la maison n'est pas prête. Un restaurant, lui, **écrit à
l'ardoise** ce qu'il n'a pas photographié. La tuile porte le nom du plat, un
filet de braise, et rien d'autre. C'est aussi **le mécanisme qui servira le
jour où les 48 photos IA sortiront** (voir la question ouverte plus bas).

### Ce que la photo a tranché, et ce qu'elle n'a pas tranché
La colonne des 2ᵉˢ tailles est coupée au bord de la photo, mais **le premier
chiffre se lit** en recadrant :

- **confirmés** : à la crème 6 000 · pili chaud 5 000 · paysanne 6 000 ·
  **pêcheur 6 000** (le `MENU.md` le donnait « à confirmer » : il est bon)
- **absents du site alors qu'ils existent** : **napolitaine** et **oriental**
  ont une grande taille, prix coupé, commençant par 5. ⏳
- **pas de 2ᵉ taille** (colonne vide) : épinards, quatre saisons, fruit de mer,
  margherita — le site a raison
- ⚠️ **Aileron : la ligne est corrigée à la main au surligneur** sur le menu
  papier, et c'est illisible sur la photo. Le site affiche 3 000. ⏳

Les quatre questions à poser à la maison sont dans `MENU.md`, en bas.

### Le QC, enfin écrit : `python _outils/_qc.py`
**30 contrôles** (après `npm run build`) : le compte des plats **lu dans les
données** et jamais recopié, les ardoises lisibles, 0 image cassée, 0
`/carte/undefined.webp`, 0 débordement en 390 et 1440, la fiche qui s'ouvre sur
un plat sans photo, et **la lisibilité du prix mesurée par catégorie**.
⚠️ Trois pièges d'instrument sont documentés en tête du fichier : serveur de
test multi-tâches, les **deux** dialogues de la page, et surtout — le décile le
plus clair ne mesure pas un texte qui couvre un dixième de sa boîte, il mesure
son anticrénelage (il annonçait **2,15:1 sur une pastille parfaitement nette**).

### ⛔ LA QUESTION OUVERTE, QUI APPARTIENT À MONGAZI
**Les 48 photos de plats sont des images générées** (z_image, 2026-07-20).
Depuis le 2026-08-01 le cerveau dit : « INTERDIT ABSOLU : une photo produit
générée par IA présentée comme le catalogue du client. » Angy Art a été purgée
le 2026-08-08, Hillary affiche « Photo sur WhatsApp ». **Au Braisé d'Or est le
dernier site où la règle n'est pas appliquée.** Rien n'a été touché ici sans
décision : l'ardoise est prête, la bascule est de retirer `img` des entrées de
`PHOTO` dans `index.html` et de régénérer.

## 🔥 LE HÉROS DES 14 SAUCES (2026-08-26)

*Détail : `_memoire/conversations/2026-08-26-braise-heros-sauces.md`.*

Trois demandes de Mongazi : **toutes** les sauces au héros, **beaucoup plus
vite**, et **on commande depuis là**.

### ⛔ Le défilement était le moteur, et c'est ce qui bloquait tout
La scène était une piste de **N × 100vh** parcourue par le défilement
(ScrollTrigger « scrub » + aimant). À 4 plats : 400vh. **À 14 sauces :
1 400vh**, quatorze écrans avant la carte. Et une cadence rapide aurait fait
**défiler la page toute seule** à toute vitesse.
→ **La scène tient sur UN écran**, l'index est piloté par un tween sur un
nombre. Le mouvement des assiettes (diagonale + rotation + échelle, réglé image
par image sur la vidéo de référence) **n'a pas bougé d'un pixel** : c'est son
moteur qui a changé, pas son dessin.
✅ La crainte du 21/08 (« reboucler ferait REMONTER la page ») **n'existe
plus** : la boucle est franche, sans le tour de respiration.
✅ On tourne **par le chemin le plus court sur l'anneau** : de la 14e à la 1re,
on avance d'un cran.
⚠️ **Lenis reste** : `aller.ts` passe par `window.__lenis` pour sauter aux
catégories (sans lui, un `scrollIntoView` s'arrête en chemin).

### ⚠️ La pause au survol qui aurait tué le carrousel
`onPointerEnter` sur la scène : **la scène fait tout l'écran**, la souris est
toujours dessus, le carrousel ne serait **jamais reparti** sur un ordinateur.
On ne s'arrête que sur la carte de verre et sur la bande des miniatures.

### `DISHES` est lu dans la carte, plus écrit à la main
Quatre sauces étaient recopiées avec leur prix : deux vérités pour le même
plat. `DISHES` = la catégorie **Sauces** de `carte.ts`. Ajouter une sauce à la
carte la fait entrer au héros toute seule, et **le QC la réclame**.
Sans photo → **ardoise ronde** avec le **filet à la couleur de la sauce**
(huit ardoises identiques ressemblent à une panne, huit couleurs à une
collection).
⚠️ **Béchamel et Crème n'auront jamais de découpe** : `_detoure_plats.py` le
documente depuis le 19/08.

### L'optimisation, mesurée
Les 14 découpes pèsent **plus de 2 Mo** : fenêtre glissante d'images (**4 au
premier écran**, le QC refuse au-delà de 5), et au-delà de la fenêtre une
assiette est **rangée une fois** au lieu d'être repositionnée à chaque image.

### Commander depuis le héros : un pont, pas un second moteur
⛔ Recoder « ajouter au panier » dans le héros = un **deuxième moteur de
commande** avec sa propre idée du prix et de l'accompagnement.
✅ `data/commande.ts` : le héros **demande**, la carte **ouvre sa fiche**. Une
fonction, un nom de plat. Fiche du menu, garnitures, **accompagnement
obligatoire**, fourchette, panier, message : un seul de chaque.
⚠️ **La barre du panier recouvrait la scène** (barre du bas + carrousel).
`body.a-panier` remonte la scène, et un contrôle **mesure le chevauchement**.

### La glace se vend à la boule — le modèle ne savait pas
`p` / `p2` / `pMax` ne portaient que **deux** tailles, et la fiche tenait la
taille dans un **booléen**. Le 3e palier de la glace disparaissait : la maison
encaissait 1 500 F au lieu de 2 500. → **`paliers: [libellé, prix][]`**, un
barème à N crans, et la fiche ne connaît plus qu'un **index**.
⚠️ **Le balisage a maintenant QUATRE façons d'avoir un prix** : `pMax` →
`AggregateOffer` · `p2` → 2 offres · `paliers` → N offres · `p: 0` → aucune.

### ⛔ QUATRE DÉFAUTS QUE LE QC VERT NE VOYAIT PAS
Trouvés **sur les captures**, pas par un contrôle. `_outils/_vues_heros.py`
photographie les 14 sauces en 390 et 1440 : les regarder est la seule façon.

1. **`clearProps: "all"` VIDE l'attribut `style`** (il ne retire pas « ce que
   GSAP a posé »). → **le bouton de commande était INVISIBLE** : fond
   transparent, texte crème, sur verre clair, **1,1:1**. ⚠️ Défaut **antérieur
   à cette session** : l'ancien bouton vert avait le même sort **en ligne**.
   Et le corps du titre, calculé par sauce, était effacé : la **2e ligne
   ressortait plus petite que la 1re**. → `clearProps:
   "opacity,visibility,transform"`, et les couleurs fixes dans une **classe**.
2. **L'ardoise ronde sortait de sa boîte de 100 px** en 390 px : `inset-0` fixe
   déjà les deux dimensions, donc **`aspect-ratio` est ignoré**, et la boîte
   n'est carrée que sur grand écran. → conteneur mesuré + `min(100cqw,100cqh)`.
3. **La pile de points se posait sur le texte** sur téléphone (colonne pleine
   largeur) → masquée sous 768 px.
4. **Les deux flèches du carrousel étaient posées SUR des miniatures** :
   `overflow: visible` + 14 slides qui débordent. → `overflow-x: clip` (garder
   la verticale, sinon l'ombre de la miniature active est rognée).

### Deux défauts trouvés en chemin
⛔ La carte de verre listait les accompagnements des **grillades** sous des
**sauces**. Elle les **lit** maintenant dans la carte.
⛔ **LE SITE A DEUX NUMÉROS WHATSAPP** : `index.html` = `2290156057157`,
`experience/data/dishes.ts` (**le fichier servi**) = `22956057157` — **le `01`
a sauté**. Rien n'a été touché (règle : jamais un lien WhatsApp sans
confirmation). À trancher.

## ⏳ Ce qui reste

- ✅ **FAIT le 2026-08-26 : les quatorze sauces ont leur photo.** Plus une
  seule ardoise, ni dans les sauces ni ailleurs — **les 52 plats du menu ont
  la leur**. Détail : `_memoire/conversations/2026-08-26-braise-les-sauces.md`.
  ⚠️ Au passage, une photo portait le nom d'un autre plat depuis le 19/08 :
  celle dite « sauce graine » était **la sauce arachide** (crémeuse et beige
  quand la graine est rouge d'huile de palme, et servie dans un **bol rond à
  bord cuivré** quand tout le reste est dans l'assiette octogonale noire).
  Réattribuée, sources renommées avec.
- **La vraie photo de la salle.** Le fond est un mur neutre, pas leur
  restaurant. ⚠️ La vidéo `hero.mp4` montre **le gril**, pas la salle.
- **Confirmer le numéro WhatsApp** : `01 56 05 71 57` est câblé, l'enseigne
  affiche `43 99 29 29`.
- Les **vrais avis** et le **nom du chef**.
- L'adresse exacte et la carte, le vrai logo, les réseaux.
- ⏳ **La version « braise »** (vidéo du gril en fond, scène sombre) est dans
  l'historique en **32062e3** : la reprendre est un `git revert`, pas une
  reconstruction. Elle a prouvé qu'inverser toute la scène ne demande de
  réécrire que **cinq jetons de couleur**.

---

## Identité
- Client : **Au Braisé d'Or**
- Secteur : Restaurant (braisé / grillades)
- Livrable : **Catalogue digital** (menu commandable) — 1er catalogue-resto NEBULA
- Marché : Cotonou, Bénin (à confirmer)
- Statut : **LIVE https://au-braise-dor.pages.dev** (Cloudflare Pages, projet `au-braise-dor`, déployé 2026-07-20)

## Décisions
- Architecture : **CATALOGUE DIGITAL** (grille de plats + prix + commande WhatsApp pré-remplie) — validé par Mongazi 2026-07-17
- Direction visuelle : à valider (reco : **braise premium** noir profond + or/braise + bois)
- Périmètre services : à préciser (sur place / à emporter / livraison)

## À DEMANDER au client (WhatsApp, en parallèle du build)
- [ ] **n° WhatsApp Business** (commandes) — à CONFIRMER avant câblage
- [ ] **Menu réel** : plats + prix, par catégorie
- [ ] **Photos** plats + lieu (5-10)
- [ ] **Logo** (si existe)
- [ ] **Adresse exacte** + quartier/ville (Google Maps)
- [ ] **Horaires** d'ouverture
- [ ] **Réseaux** (Instagram / Facebook)
- [ ] Positionnement/ambiance (premium vs populaire)

## ✅ GÉNÉRATION HIGGSFIELD EXÉCUTÉE (2026-07-19, vagues A/B/C)
- **MCP débloqué** : le vrai serveur MCP Higgsfield est connecté (`/mcp` → « Connected »), génération OK via `mcp__higgsfield__*` (le CLI/skills restent bloqués). Détail : [[reference_higgsfield]].
- **Vague A — 7 images (nano_banana_pro, ~14 cr)** : 6 plats photoréalistes (Tilapia braisé, Poulet bicyclette, Pizza feu de bois, Chawarma, Salade JOQ, Cocktail Piña Colada) + 1 image héro (mains gantées noires retournant poisson/brochettes sur flammes, 16:9 2k). Optimisées WebP ≤1100px (43-130 Ko) dans `assets/images/`. Câblées dans la **galerie « La braise en spectacle »** (bento 6 colonnes PC qui tessellise, cartes 2 col tablette / 1 col mobile — bug cascade CSS corrigé : media queries APRÈS les règles de base). Sous-titre honnête « Visuels d'illustration, bientôt remplacés par les photos de la maison ».
- **Vague B — vidéo héro (Kling 3.0 Turbo, 7,5 cr)** : les flammes bougent, mains gantées retournent le poisson, étincelles. 5 s (durée courte optimisée vente, demande Mongazi). Compressée ffmpeg (imageio-ffmpeg) : `hero.mp4` boucle 1,07 Mo + `hero-scrub.mp4` keyframes denses 2,3 Mo. **Câblage** : scroll-scrub sur PC (les images AVANCENT au défilement) + **poster Ken-Burns sur mobile (aucun téléchargement vidéo = data light)** + `prefers-reduced-motion` = poster statique.
- **Vague C — univers braise (1 texture z_image 0,15 cr + CSS/JS gratuit)** : lit de braises `coals.webp` en filigrane sous la **barre d'onglets** ; **halo de braise qui suit le curseur** (PC) ; **boutons chauffés** (balayage d'ember au survol + respiration d'ember sur le CTA or) ; **cadres chauffés** (liseré d'ember sur les cartes plats au survol) ; **onglet actif** = braise vivante qui palpite. Tout respecte `prefers-reduced-motion`.
- **Crédits** : ~21,5 utilisés (test 2 + 7 images ~12 + héro 2k + vidéo 7,5 + texture 0,15), **~76,5 restants** sur les 100 (budget ~50 respecté).
- **QA Playwright** : PC (héro vidéo scrub, galerie bento, onglets braise, halo curseur) + mobile/tablette (poster Ken-Burns, galerie 1/2 col) → 0 erreur console, tout 200. **PAS déployé** (attente accord Mongazi).
- ⚠️ Bump `?v=` de app.css/app.js **inexistants ici** : CSS/JS sont **inline dans index.html** (pas de fichiers externes) → recharge simple.

## ✅ REFONTE + 48 PHOTOS DE PLATS + DÉPLOIEMENT (2026-07-20)
Retours Mongazi après la session Higgsfield → refonte (skill `ui-ux-pro-max` invoqué) :
- **Vidéo héro** : le scroll-scrub « décomposition image par image » a été tenté (scène épinglée 210vh + `requestVideoFrameCallback`) mais **ne passait pas au défilement** chez Mongazi → **abandonné**. Remis en **vidéo d'intro douce qui démarre TOUTE SEULE** à l'entrée (`hero.mp4` boucle muette, autoplay, pause hors-écran via IntersectionObserver, `prefers-reduced-motion` = poster). `hero-scrub.mp4` n'est plus référencé.
- **Photos DANS les cartes** (plus de galerie séparée) : chaque plat a un **cadre image** en haut de sa carte + **prix en pastille verre** ; **carte entière cliquable → fiche de commande qui montre la photo en grand**. La section galerie « La braise en spectacle » a été **supprimée** (markup + CSS).
- **FAB WhatsApp** flottant brillant (bas-droite, anneau pulsant) **retiré** (il restait « Commander » header + héros + fiche).
- **Glassmorphism « verre fumé braise »** : tokens verre (highlight or, hairline), backdrop-filter sur barre d'onglets / feuilles / pastilles de prix, feuille de commande frostée.
- **48 plats = 48 vraies photos générées** (fini les placeholders) : map JS `PHOTO` (nom du plat en minuscules → slug WebP). Chaque fiche de commande affiche aussi la photo.

### Modèle image choisi = **z_image** (pas nano_banana_pro)
- A/B testé **nano_banana_pro (2 cr) vs Recraft V4.1 (1,25 cr) vs z_image (0,15 cr)** sur poulet/pizza/cocktail/burger, **images téléchargées et regardées**. Verdict : **z_image = photoréaliste, 2048², rendu au moins aussi bon** que les autres pour des plats sur ardoise sombre → retenu (nano à 2 cr aurait coûté 84 cr pour 42, hors budget).
- **42 nouvelles images z_image** (1:1) style « braise premium » (charbon + ember + halo doré + fumée), + 4 réutilisées des tests A/B (poulet chair, napolitaine, mojito, cheeseburger). Prompt commun = sujet + « Dark moody charcoal background, warm ember glow, golden rim light, wisps of smoke, appetizing, professional restaurant menu photography, no text/watermark/hands/cutlery ».
- Pipeline : `scratchpad/fetch_dishes.py` télécharge le `_min.webp` de chaque job (via `show_generations`) → réencode **WebP 900px q80** (~72 Ko/pièce, **3 Mo les 42**) dans `assets/images/<slug>.webp`. Slugs = `g-*` grillades, `p-*` pizzas, `c-*` chawarmas, `b-*` burgers, `s-*` salades, `sc-*` sauces, `pd-*` petit-déj, `k-*` cocktails.
- ⚠️ **z_image sujet au rate-limit (429)** si trop d'appels en parallèle → générer par lots de ~6-11.
- **Coût total session** : ~10,2 crédits (dont ~4 en tests A/B). **Solde 66,15 / 100.**
- **QC** : 48/48 plats mappés, 48/48 fichiers présents, 0 lien mort, JS parse OK, tous assets 200 en local ET en prod.
- **Déploiement** : `wrangler pages deploy` d'un dist propre (index.html + assets/images + `assets/videos/hero.mp4` seul ; `assets/raw/` 30 Mo et `hero-scrub.mp4` exclus). 53 fichiers, 5,4 Mo. Projet Cloudflare **`au-braise-dor`** créé + **LIVE https://au-braise-dor.pages.dev** (vérifié 200).

## PLAN GÉNÉRATION HIGGSFIELD (validé — HISTORIQUE, désormais exécuté ci-dessus)
- **Accès** : MCP Higgsfield ajouté à Claude Code (`https://mcp.higgsfield.ai/mcp`, scope user, authentifié via /mcp le 2026-07-19). ⚠️ Le CLI/skills sont BLOQUÉS sur le plan trial (`only_mcp_usage_on_trial_is_available`) → **générer uniquement via les outils MCP** (voir [[reference_higgsfield]]). Budget validé Mongazi = **~50 crédits / 100**, rendu **photoréaliste**.
- **1. Vidéo héro « qui avance au défilement »** : plan cinématique **grillade qui flambe + mains du cuisinier en GANTS NOIRS** qui retourne poisson/brochettes, braises, fumée → image (Nano Banana Pro 16:9 2k, ~2cr) puis animée en vidéo (Kling 3.0 Turbo, ~7,5cr). Câblage = scroll-scrub PC + repli boucle/Ken-Burns mobile.
- **2. Section « ultra puissante »** qui pousse à commander (feu + accroche haute énergie + CTA magnétique).
- **3. 6 visuels de plats photoréalistes** (Tilapia braisé, Poulet bicyclette, Pizza, Chawarma, Salade JOQ, Cocktail) — Nano Banana Pro ~2cr each (~12cr) — marqués « à remplacer » par vraies photos.
- **4. Textures UI boutons** (braise/charbon, or, flamme) via Soul Cinematic 0,12cr — quasi gratuit.
- Après génération : download → optimiser (WebP/JPEG) → câbler dans index.html → QA → rapport (pas de deploy sans accord).

## À FAIRE AUSSI (déjà demandé par Mongazi, en attente de génération/photos)
- Panier + options (taille/accompagnement/qté) + mode Sur place/Emporter/Livraison + message WhatsApp structuré = **DÉJÀ construit** dans index.html (moteur de commande V1).
- Barre de catégories sticky **corrigée** (overflow clip + scroll-spy).
- Ambiance sonore (feu de fond + survol/clic + son commander + boot façon Nintendo DS) = **déjà en place**.

## À REMPLACER / RESTE (placeholders posés pendant le build)
- Photos plats = **48 visuels IA générés** (à remplacer un jour par les vraies photos de la maison si souhaité, mais déjà propres et vendeurs).
- Photo **du lieu** (bloc « La maison » a encore un placeholder) · adresse exacte + carte Google Maps · horaires (badge ouvert/fermé) · logo officiel · réseaux IG/FB · 2ᵉ prix pizzas/grillades · vrais avis · **confirmer n° WhatsApp** (01 56 05 71 57 câblé, vs 43 99 29 29 enseigne).
- ✅ **Affiche A4 + 2 QR** produite (2026-07-20) : `assets/docs/Affiche_Au_Braise_dOr_A4.pdf` (print) + `.jpg` (partage WhatsApp). Design braise (héro flammes + trio tilapia/pizza/mojito), **QR site + QR WhatsApp décodés/vérifiés** (pyzbar). Générateur = `_outils/_build_affiche.py` (Python PIL + qrcode, sans navigateur).
- Reconfirmer direction couleur (braise sombre vs enseigne bleu/blanc/or).

## Infos enseigne (reçues 2026-07-17)
- Nom complet : **Restaurant Au Braisé d'Or**
- Slogan : **« De Paris à Cotonou »**
- Cuisine : **Africaine · Européenne · Américaine** (explique le menu très large)
- Services additionnels : **Service traiteur** + **Place des fêtes** (événementiel)
- Contact : **(+229) 43 99 29 29** (à CONFIRMER = numéro WhatsApp ?) · **aubraisedor@gmail.com** · WiFi 24h/24
- Légal (pied de page / mentions) : RC **RB/COT/24 A 102350** · IFU **0202501441177**
- ⚠️ Couleurs de l'ENSEIGNE = **bleu + blanc + jaune/or** (le menu papier, lui, était orange). Direction actuelle du site = **braise sombre** (choix Mongazi) → à reconfirmer vu l'enseigne.

## Journal
- 2026-07-17 — Création du dossier. Mongazi introduit la cliente (nom seul), puis précise : elle veut un **catalogue digital**. Architecture verrouillée = catalogue.
- 2026-07-17 (13h) — Menu reçu (5 photos → `MENU.md`) + enseigne. Choix validés : catalogue · **braise premium sombre** · son braise. **V1 construite** (`index.html` : dark braise, 3D glass, son braise, tout le menu rendu, commande WhatsApp par plat). Puis enseigne reçue (bleu/blanc/or + slogan + traiteur/place des fêtes + contacts) → questions de recadrage. QA V1 : rendu premium OK, à corriger = kicker hero qui clippe en mobile étroit.
- 2026-07-19 — **Génération Higgsfield exécutée (MCP débloqué)** : héro vidéo braise (scroll-scrub PC / Ken-Burns mobile), galerie de 6 plats + ambiance (bento responsive, bug cascade CSS corrigé), univers braise sur boutons/cadres/curseur/onglets (+ texture lit de braises). QA Playwright PC+mobile OK, 0 erreur. Sources IA lourdes dans `assets/raw/` (gitignoré) ; livrables WebP/MP4 dans `assets/images` + `assets/videos`. **Non déployé** (attente accord).
- 2026-07-20 (3) — **Son remplacé** : le client détestait le son synthétique (Web Audio braise/grésillement). **Retiré tout le moteur Web Audio** (ambiance + bruitages survol/clic/boot) → remplacé par une **boucle mp3 « feu de bois »** (`assets/audio/fire-loop.mp3`, source `_partage/Fat Es BBQ 1 minute of relaxing fire sound..mp3`) qui **démarre au 1er contact** (pointerdown/touchstart/keydown, façon NEBULA Agency) avec fondu ; le bouton haut-parleur du header (#sound) coupe/relance, état en `localStorage`. Redéployé. ✅ testé Playwright (fire-loop.mp3 joué au 1er clic).
- 2026-07-20 (2) — **Polish post-mise en ligne** : (1) **crépitement/ronflement de fond retiré** (`startAmbient` no-op, on garde les retours survol/clic) ; (2) **menu 2 plats par ligne + cartes compactes sur mobile** (`.menu .grid → 1fr 1fr`, description masquée mobile — reste dans la fiche) pour parcourir vite ; (3) **toutes les mentions de brouillon retirées du site public** (« à valider / à confirmer / à préciser / aperçu / exemple / dev-tag ») → carte Maps placeholder remplacée par **vrai lien Google Maps** (recherche par nom+ville), adresse/horaires nettoyés, tags d'avis retirés, watermark « Aperçu NEBULA » supprimé. Nouvelle règle en mémoire : [[feedback_no-placeholder-on-deploy]]. Redéployé + vérifié live.
- 2026-07-20 — **Refonte (skill ui-ux-pro-max) + 48 photos de plats + 1ER DÉPLOIEMENT** (détail section « REFONTE… » ci-dessus). Scroll-scrub héro abandonné (ne passait pas) → intro douce autoplay ; galerie fusionnée dans les cartes (photo + prix + clic→fiche) ; FAB WhatsApp retiré ; verre fumé ; **z_image** retenu après A/B (0,15 cr) pour générer **42 photos** (+4 réutilisées) = 48 plats photographiés. Solde crédits 66,15/100. **LIVE https://au-braise-dor.pages.dev.** Reste : affiche A4+QR, photo du lieu, n° WhatsApp, adresse/Maps, horaires, logo, réseaux, avis.

## 2026-08-19 · les corrections de la propriétaire sont EN LIGNE

Les modifications arrivées par la session téléphone (13 plats retirés, la carte
des sauces, les héros détourés, les deux prix exacts) ont été **construites,
contrôlées et publiées** depuis le PC de Cotonou.

- déploiement : `https://cfc82be6.au-braise-dor.pages.dev` → https://au-braise-dor.pages.dev
- vérifié **dans le corps de la page servie**, pas sur un code 200 :
  « Monyo » 0 fois · gombo 9 · krinkrin 5 · 52 plats · Napolitaine / Mojito /
  Crispy poulet / JOQ Viagra absents · « Mouton frit » toujours là (2 fois)
- les 3 photos de sauces répondent 200 en `image/webp`, l'affiche A4 aussi
- un fichier absent répond bien **404** (et non 200, cf. la panne PISTE)

### ⚠️ Le contrôle qualité ne démarrait pas sur ce PC

`_outils/_qc.py` a été écrit sur la machine du nuage. Trois défauts d'instrument,
corrigés ici, aucun ne venait du site :

1. il **codait en dur** `/opt/pw-browsers/chromium-1194/...` : ce chemin n'existe
   que sur la machine du nuage. Il n'est plus imposé que s'il existe.
2. il lisait `#cat-petitdej` après un **délai fixe de 1,5 s** : sur un poste
   chargé la rubrique n'était pas encore montée et tout s'arrêtait sur un `null`.
   Il **attend** l'élément.
3. la console Windows écrit en **cp1252** : un « ≥ » dans un libellé faisait
   planter la suite **après** l'avoir réussie. Sortie forcée en UTF-8.

**78 contrôles verts, 0 rouge** (mobile 390 + bureau 1440 + lisibilité des prix).

## 2026-08-20 · Les photos générées par IA sont gardées

**Décision de Mongazi : « les photos IA de Braisé d'Or on les garde, oublie
ça ».** Les 48 photos de plats (z_image, 20/07, antérieures à la règle du
2026-08-01) restent en ligne. Le sujet est **clos** : il sort du reste-à-faire.

⚠️ Ce n'est pas une exception à la règle, c'est un héritage assumé. Aucun
**nouveau** visuel généré n'entre dans ce catalogue ni dans un autre.

### Reste à obtenir de la maison

- le prix du **yaourt** et de la **glace** (affichés « Prix sur demande »)
- la correction manuscrite au surligneur sur **l'aileron**
- **confirmer le n° WhatsApp** : 0156057157 câblé, contre 43 99 29 29 sur l'enseigne
- la **vraie photo de la salle**, les vrais avis, l'adresse, le logo

⚠️ `next@14.2.15` porte une vulnérabilité connue signalée par npm.

## 2026-08-20 · ce qui ne se voyait pas : partage, robots, données structurées

La vitrine avait tout ce qui se regarde et **rien de ce qui ne se voit pas**.
Trois manques, tous invisibles depuis le site, tous corrigés sans rien demander
à la maison.

### 1 · Aucune image de partage

Le lien envoyé sur WhatsApp n'était qu'une **ligne de texte grise**. Au Bénin
tout circule par WhatsApp : c'est le défaut le plus cher qu'une vitrine puisse
avoir. `python _outils/_og.py` fabrique `og.jpg` (1200x630, 93 Ko, **JPEG** —
l'aperçu WhatsApp ne lit pas toujours le WebP) : la braise, le nom, et **une
vraie photo de la maison**, la sauce gombo détourée. Aucun texte inventé.

⚠️ **L'instrument mesurait le texte au lieu du fond.** Le contraste du titre
tombait à 1,1:1 parce que les pixels les plus clairs de la zone étaient **les
lettres elles-mêmes**. On relève le fond **avant** d'écrire dessus : 10,8:1.

### 2 · Ni robots.txt, ni sitemap.xml

Écrits. Les robots des IA (GPTBot, ClaudeBot, PerplexityBot) sont explicitement
autorisés : ils citent la maison.

### 3 · Aucune donnée structurée

Un prix réel ne s'affichait dans aucun résultat Google. La page porte
maintenant un `Restaurant` complet, **lu dans `CARTE`, jamais recopié** :
`hasMenu` avec ses 9 rubriques et ses 52 plats, les vrais numéros, l'e-mail.

⛔ **Ce qu'on n'a PAS déclaré** : aucune note ni avis (personne n'en a donné),
aucune adresse de rue (la maison ne l'a jamais donnée : la ville et le pays
suffisent, une adresse inventée est pire que pas d'adresse), aucun horaire
(« ouvert tous les jours » n'est pas un horaire).

⚠️ **UN PLAT A TROIS FAÇONS D'AVOIR UN PRIX**, et les confondre ment :
`pMax` est une **fourchette** (les sauces, selon ce qu'on met dedans) →
`AggregateOffer` ; `p2` est une **deuxième taille** → deux offres ; `p: 0` veut
dire **prix pas encore donné** → aucune offre. Le premier jet ne lisait que
`p` et annonçait « jusqu'à **5 000 F** » alors que la carte monte à **6 000 F**.

### Le contrôle

`python _outils/_qc_partage.py` = **35 contrôles, sans aucun navigateur** (il
lit le fichier servi). Il compare le balisage à la carte plat par plat, refuse
une offre à 0 F, vérifie que les 9 fourchettes portent leur borne haute et que
les 13 plats retirés ne reviennent pas par le balisage.

⚠️ Il a fallu deux corrections d'instrument : une expression régulière « du nom
jusqu'au prix » attrapait le prix du plat **suivant** quand un plat tient sur
plusieurs lignes (les sauces), et `toLocaleString("fr-FR")` sépare les milliers
par une **espace fine insécable** (U+202F) qu'aucune comparaison de texte ne
voit venir.

⚠️ **La suite Playwright (76 contrôles) n'a PAS tourné** : les navigateurs ont
été supprimés le même jour pour libérer le disque. Les changements sont
entièrement dans l'en-tête du document, sans effet sur la mise en page. Pour la
relancer : `npx playwright install chromium` (267 Mo).

---

## LA SCÈNE NE MEURT PLUS AU DERNIER PLAT (2026-08-21)

Mongazi : « il faut que les éléments défilent tout seuls ». Tout était déjà
automatique ici — sauf que `if (iRef.current >= N - 1) return;` arrêtait la
rotation **définitivement** au quatrième plat. Au bout de 22 s, la scène était
morte et le site avait l'air en panne.

**La crainte d'origine était juste, la conclusion trop large.** ⚠️ `aller()`
fait défiler **LA PAGE** : revenir au premier plat la fait **remonter**, en
travers de quelqu'un qui descend vers le menu. Mais ce cas est **déjà couvert
deux fois** — rien ne bouge quand la scène n'est pas à l'écran (garde-fou 2),
et un geste repousse tout de 12 s (garde-fou 5). Ne restait que le visiteur
**immobile, qui regarde** : pour lui, une scène figée n'est pas une protection.

Elle reboucle donc, ⚠️ **avec un tour de plus sur le dernier plat** avant de
remonter : une boucle qui se referme sans respirer ressemble à un bug.
Mesuré sur l'export statique : **0 → 1 → 2 → 3 → 0** en 30 s, sans y toucher.
Build 182 kB, QC **76 verts, 0 rouges**.

---

## ⛔ SIX PHOTOS LIVRÉES, AFFICHÉES NULLE PART (2026-08-27)

*Détail complet : `_memoire/conversations/2026-08-27-braise-deux-machines.md`.*

Les six découpes de sauce (arachide, tomate, tête de mouton, pieds de bœuf,
yassa, yassa au poulet) étaient dans `main` depuis la veille : fichiers
propres, pesés, poussés, en 200. **Et le héros posait quand même son ardoise
sur les six**, en plein premier écran.

Parce que le héros ne lit pas le dossier `/plats`, il lit le `DECO` de
`dishes.ts` :

```ts
img: d?.img,     // d = DECO[nom]  →  absent = ardoise
```

et **aucun des sept commits qui ont posé les images n'a touché `dishes.ts`**.

⚠️ **RIEN NE POUVAIT LE SIGNALER.** Le contrôle « 0 image cassée » ne voit que
les images **demandées**. Une image qu'on ne réclame jamais ne peut pas être
cassée : elle est parfaite et invisible. **Un fichier livré n'est pas un
fichier affiché.**

**Posé le 27/08** : les six `img:` du `DECO` · les six correspondances de la
page de repli `index.html` · les images de carte manquantes dans
`assets/images/` (elle en réclamait déjà trois qui n'existaient pas).

**Nouveau contrôle** : *aucune découpe inutilisée dans `/plats`*. Il lit les
**deux** côtés dans les fichiers, sans recopier aucune liste : le jour où une
sauce arrive, il la réclame tout seul.

### Le héros, après

| | avant | après |
|---|---|---|
| plats illustrés | 46 / 52 | **52 / 52** |
| sauces montrées au héros | 6 | **12** |
| ardoises rondes au héros | 8 | **2** |

Les deux qui restent sont **Béchamel** et **Crème** : elles n'auront **jamais**
de découpe (plat noir sur fond noir, noté depuis le 19/08). Leur ardoise ronde
au filet de la couleur de la sauce est le rendu définitif, pas un pis-aller.

### ⚠️ ET LE MÊME TRAVAIL A ÉTÉ FAIT DEUX FOIS

Le PC de Cotonou avait, non commité, une chaîne complète pour ces six sauces
(deux outils, images, correctif du QC) — pendant que `origin/main` portait déjà
le même travail, poussé depuis le téléphone en 7 commits (`fb93ec7` →
`aeba870`), à partir des **mêmes photos sources au bit près**.

La version de `main` est gardée : elle est plus mûre (rembg/isnet contre une
reconstruction d'alpha depuis le damier — **approche déjà mesurée et rejetée**
dans `_damier.py` : *« les deux gris du damier sont 77 et 124, et le bord noir
de l'assiette a des reflets dans cette plage »*), et son correctif du QC sépare
l'**ardoise** de l'**accompagnement obligatoire** au lieu de laisser les deux
accrochés au même clic. Le commit local `70e3d8b` est **écarté**, pas perdu.

⚠️ **Le garder aurait posé un piège** : `_poser_sauces.py` aurait réécrit en
silence les cadrages que `_photos_sauces.py` gèle exprès, photo par photo.

**Cause racine, corrigée dans `scripts/rapatrier.py`** : le script de début de
session **excluait `origin/main`** de son inventaire et ne surveillait que les
branches `claude/…`. Une session du téléphone pousse **directement dans
`main`** : il répondait « ✅ Rien ne traîne » avec sept commits de retard.

### ⏳ VU EN REGARDANT LES 12 DÉCOUPES : LA VAPEUR DE `sc-moyo` ET `sc-poisson`

Les douze découpes ont été posées côte à côte sur le crème du site
(`#ede9e3`) et regardées. Onze sont propres : assiette entière, aucun halo,
aucun escalier dans le bord. **Deux ne le sont pas.**

Sur **`sc-moyo`** et **`sc-poisson`**, le **panache de vapeur** est sorti du
masque en **forme pleine, gris foncé et opaque** : au-dessus du plat flotte
une silhouette qui ressemble à une **anse ou un crochet**, pas à de la vapeur.
Sur fond blanc ça passe ; sur le crème du héros, c'est une tache.

⚠️ **Ce n'est pas un défaut du 27/08** : ces deux découpes sont en ligne depuis
le 26/08, elles n'ont pas été retouchées aujourd'hui. Personne ne l'avait vu
parce qu'on regarde les images **une par une** — c'est en les mettant **toutes
les douze ensemble** que les deux intruses sautent aux yeux.

**Le remède est déjà écrit dans `_damier.py`** : c'est la « rustine
anti-vapeur », dont la note dit qu'elle ne servait plus sur la krinkrin
(9 lignes étroites, largeur croissante = le coin de l'octogone). Sur ces deux
plats-là, il y a bien un panache. ⚠️ **Refaire la planche comparative des
modèles pour ces deux photos** avant de choisir : `isnet` gagne sur damier,
`birefnet` sur fond noir, et **le fond change le gagnant**.
