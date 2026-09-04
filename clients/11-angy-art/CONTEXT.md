# Client 11 — ANGY ART

**Angélique AVOCEVOU** · artiste plasticienne · Cotonou, Bénin
Commande reçue le **2026-08-05** via le formulaire nebula-agency.online.

| | |
|---|---|
| Marque | **Angy Art** — accroche officielle : **« Inspiré d'en haut, enraciné ici. »** |
| WhatsApp | **+229 01 52 00 64 90** — ⚠️ **à tester une fois** (voir § 4) |
| E-mail | angyavocevou@gmail.com |
| Instagram | [@angy_art_creatif](https://instagram.com/angy_art_creatif) |
| TikTok | [@angy_art_](https://tiktok.com/@angy_art_) |
| Service vendu | Vitrine Digitale + QR Code — 150 000 F installation + 20 000 F / 6 mois |
| Objectif | Portfolio / galerie — montrer son travail |
| Délai | Pas pressé, elle prépare |
| Style demandé | Luxe & élégant · immersif · épuré · émotionnel |
| Couleurs imposées | aucune (choix NEBULA) |
| Options | boutons WhatsApp · galerie photos · musique d'ambiance · section avis |
| En ligne | https://angy-art.pages.dev (Cloudflare Pages, projet `angy-art`) |

## 0. ⚡ LA FLUIDITÉ (2026-08-26) — lire avant de toucher au CSS

*Détail complet : `_memoire/conversations/2026-08-26-angy-art-fluidite.md`.*

Le site était **vert à 150 contrôles** et tournait à **quinze images par
seconde** sur un processeur ralenti ×6, avec une tâche de **1 557 ms** pendant
laquelle la page ne répondait plus. Un QC vert dit que rien n'est cassé ; il ne
dit pas que ça glisse.

**Après :** 60 images/s, **0 à 1 tâche longue**, et sur téléphone un
95e centile à **16,8 ms**.

### ⛔ NE PAS REMETTRE LE GRAIN PLEIN ÉCRAN
`body::after` en `position:fixed` + `mix-blend-mode:overlay` coûtait **un tiers
à trois quarts du budget d'une image**, sur toute la page, tout le temps — et
valait **0,90/255** à l'œil (deux morceaux agrandis 3× sont indiscernables).
⚠️ **Ce n'est pas l'image de bruit qui coûte, c'est le mélange** : retirer
`background-image` ne change rien, passer à `mix-blend-mode:normal` rapporte
autant que tout supprimer. ⚠️ **Aucun remède de compositing ne le sauve**
(`will-change`, `translateZ(0)`, `contain:strict`, `isolation` : quatre
essais, trois mesures chacun, tous inchangés). La matière vit toujours dans
`--lin`, posé sur les photos de scène, en `absolute` dans leur section.

### Les trois autres corrections
- **On lit tout, PUIS on écrit tout** dans les deux balayages du défilement.
  `classList.add()` au milieu d'une boucle de `getBoundingClientRect()` force
  un recalcul de mise en page **par élément** : jusqu'à cent dans une seule
  image, au moment précis où le visiteur commence à défiler.
- **`marque.png` : 199 Ko pour un rendu de 57 × 44 px**, demandé en deuxième
  position à 2 298 ms sur une 3G. → **`marque.webp`, 9,7 Ko**, pour les pages.
  ⚠️ `marque.png` **reste** : l'affiche A4, l'OG et les favicons s'en servent.
- **La barre du haut était à 92 %** et on lisait le texte au travers. Une bande
  de bord a le droit de recouvrir, **si elle est vraiment opaque**.

### Les instruments, gardés dans le dossier
| | |
|---|---|
| `_fluidite.py` | la page se chronomètre elle-même, processeur ralenti |
| `_attribuer.py` | éteint un mécanisme à la fois pour lui attribuer son coût |
| `_audit.py` | **22 contrôles** sur ce que `_qc.py` ne regarde pas |

⚠️ **Cinq de mes propres sondes ont menti avant de dire vrai** : mesurer le
poids sur `localhost` (le seuil de `loading="lazy"` grandit avec la vitesse de
la connexion — j'ai failli réécrire le carrousel pour un défaut inexistant),
`*{mix-blend-mode}` qui n'atteint pas les pseudo-éléments, un bouton de modale
mal visé qui rendait deux contrôles vides, la règle des 44 px appliquée à un
lien dans une phrase, et une barre jugée translucide alors que c'était la
police qui finissait de charger. **Avant d'annoncer un défaut : « et si c'était
ma mesure ? »**

## 1. Ce qu'elle fait, dans ses mots

Œuvres contemporaines qui célèbrent l'identité, la mémoire et le patrimoine africain.
Croisée de l'art, de la matière et du design : peinture, reliefs, matériaux mêlés.
Inspirations : cultures africaines, scarifications traditionnelles, symboles ancestraux,
masques, textiles, et les **histoires personnelles de ses collectionneurs**.

Cinq axes d'activité, repris tels quels sur le site :

1. Œuvres originales pour particuliers et collectionneurs
2. Tableaux personnalisés racontant une histoire / immortalisant un moment de vie
3. Œuvres décoratives haut de gamme : résidences, hôtels, restaurants, espaces pro
4. Expositions et projets artistiques
5. Ateliers créatifs (transmission du savoir-faire)

Cibles visées : collectionneurs, décorateurs, architectes, entreprises, passionnés d'art.

## 2. Direction artistique retenue

**Esthétique « Selva Toscana »**, imposée par Mongazi le 2026-08-05 : éditorial
noir `#0a0a0a` / crème `#f3efe6`, **Playfair Display + Public Sans**, italiques dorés,
curseur suiveur, défilement lourd, carrousel en coverflow.
**L'or du site est SON or**, `#bd9f64`, relevé au pixel sur son logo (7,8:1 sur noir).
⚠️ Sur le crème il ne donne que 2,2:1 : les italiques et les liens sur fond clair
utilisent `#7e6d3a` (4,4:1). L'or `#c9b99a` du brief initial était pire encore (1,68:1). Tout le détail, et la liste de ce qui a
été écarté du brief avec les motifs, dans **`DESIGN.md`** (à lire avant tout CSS).

Une première direction « L'ENTAILLE » (indigo, Young Serif) avait été construite le matin
même puis remplacée. Sa phrase fondatrice survit et porte encore les scènes :
*une œuvre d'Angy, c'est une entaille dans la matière.*

## 3. Fichiers

```
index.html            la page (source directe, aucun build : zéro image base64)
assets/app.css        tout le style        ⚠️ bumper ?v= à chaque modif
assets/app.js         tout le comportement ⚠️ bumper ?v= à chaque modif
                      ↳ le tableau SITUATIONS est EN HAUT du fichier
assets/images/scenes/      les 9 photos d'atelier posées dans les sections
assets/images/situations/  les 6 mises en situation du carrousel
assets/images/        favicon / logos / og / qr
_sources/photos/      les 15 photos d'origine, archivées en WebP qualité 95
                      ⚠️ `clients/*/_sources/` est GITIGNORÉ : ce dossier n'existe
                      que sur la machine où les photos ont été reçues. Sans lui,
                      `_photos.py` ne peut pas tourner (les sorties, elles, sont
                      bien dans le dépôt).
_photos.py            fabrique les images du site depuis _sources/photos
                      `python _photos.py --voir` détaille chaque sortie
affiche.html          l'affiche A4 imprimable → assets/docs/Affiche_Angy_Art_A4.pdf
_qc.py                la suite de contrôle : 82 contrôles, verte avant tout déploiement
                      `python _qc.py --voir` produit aussi les captures par section
_build_assets.py      favicon + OG + QR (ré-exécutable, chaque QR est RELU par décodage)
                      `python _build_assets.py --og` refait la seule carte de partage,
                      sans avoir besoin du logo source
404.html _headers robots.txt sitemap.xml
_qc_captures/         les captures (jamais déployées)
_dist/                ce qui part sur Cloudflare (généré)
```

### La navigation reprend celle de la référence (Selva Toscana)

Le 2026-08-08, Mongazi envoie une capture vidéo du site **Selva Toscana**, la
référence qu'il avait imposée en août, et demande que « chaque défilement,
navigation, déplacement » soit pareil. Comparaison faite image par image
(38 s de vidéo, relues dans un navigateur) : **le site avait déjà** le
défilement lissé inertiel, le curseur suiveur en médaillon, le carrousel
coverflow, le rythme sombre/clair, les titres didone géants à mot italique, la
révélation mot à mot et la modale de fin. **Deux choses manquaient**, elles ont
été posées :

1. **Le rideau d'ouverture** : panneau crème plein écran, glyphe + « Angy · Art »,
   un filet doré qui se tire, un compteur qui monte de 00 à 100 en 1 s, puis le
   panneau se retire vers le haut et le héros ouvre dans la foulée.
2. **Le volet de section** : chaque section est couverte par un volet de la
   couleur OPPOSÉE (noir sur une section crème, crème sur une section noire),
   qui se retire vers le haut quand elle entre. Le volet est donc invisible
   contre la section précédente : la suivante a l'air de glisser par-dessus.
   ⚠️ Le `scaleY` porte sur un **pseudo-élément**, jamais sur la section :
   une transformation sur un ancêtre casserait la barre fixe et le curseur.

⚠️ **Le compte du rideau tourne au minuteur, pas sur `requestAnimationFrame`.**
Et ⚠️ **pour mesurer une animation d'ouverture, ne jamais se fier à des
`wait_for_timeout` empilés autour de captures d'écran** : une capture coûte des
centaines de millisecondes et décale toutes les mesures. Deux diagnostics
successifs ont conclu à tort que le rideau ne durait pas 1 s. La vérité s'obtient
en faisant mesurer la PAGE elle-même, ou avec un chargement par instant observé.

⚠️ Le QC attend **3 400 ms** après le chargement pour cette raison : mesurer
avant, c'est mesurer le rideau et non la page.

### ⚠️ Toute image DOIT porter `?v=` — sinon le visiteur voit l'ancienne un an

Le 2026-08-08, Mongazi voyait encore **l'ancienne image générée** dans le héros
alors que le serveur envoyait déjà la vraie photo. Vérifié : le fichier servi
était **identique au disque, MD5 pour MD5**. Ce n'était donc ni le déploiement,
ni Cloudflare, ni un cache empoisonné : c'était **son propre navigateur**, qui
gardait `hero.webp` parce que le nom n'avait pas changé et que l'en-tête dit
`immutable, max-age=31536000`.

Toutes les URL d'images portent désormais `?v=` (même cran que `app.css` et
`app.js`), y compris `og:image` et les chemins construits par `app.js`
(constante `VER` en haut du fichier). **À bumper dès qu'une image change de
contenu sans changer de nom.** Un contrôle le vérifie : « toute image porte sa
marque de version ».

### ⚠️ Les anciennes images restent en cache, et on ne peut pas les purger

Après le passage aux vraies photos, les 4 anciennes images générées répondaient
encore **200** à leur URL. Vérification faite : `cf-cache-status: HIT`,
`max-age=31536000, immutable`. C'est le **cache de bordure**, pas le déploiement,
et la preuve tient en une ligne : la même URL sur l'alias du déploiement
(`https://<hash>.angy-art.pages.dev/...`) renvoie bien **404**.

Sur un domaine `*.pages.dev`, **il n'y a pas de purge** : ce n'est pas une zone du
compte, `scripts/purger.py` ne peut rien. Ces copies vivront jusqu'à un an. Sans
conséquence ici (plus rien ne les référence), mais à savoir : **un fichier retiré
d'un site NEBULA ne disparaît pas d'Internet le jour où on le retire.** La seule
vraie protection est celle déjà posée sur PISTE : une marque de déploiement dans
le nom des fichiers compilés.

### Pour publier une modification
```bash
python _qc.py --voir     # doit finir « Tout est vert », puis REGARDER les captures
# bumper ?v= dans index.html si app.css ou app.js a changé, reconstruire _dist, puis :
npx wrangler pages deploy clients/11-angy-art/_dist --project-name=angy-art --branch=main
```

## 4. ⚠️ À CONFIRMER / À REMPLACER (ce que seule la cliente possède)

| # | Quoi | Où ça se pose | État |
|---|---|---|---|
| 1 | **Numéro WhatsApp** | les `href="https://wa.me/…"` de `index.html` (écrits en dur pour marcher sans JS) | ⚠️ câblé sur `2290152006490` (la forme donnée au formulaire). **Envoyer un message de test.** Si le lien n'ouvre pas la bonne conversation, essayer `22952006490` — au Bénin les deux formes vivent, et les gens donnent souvent la mauvaise sans le savoir. |
| 2 | **Photos des œuvres, détourées** | un tableau `OEUVRES` à créer dans `assets/app.js`, à côté de `SITUATIONS` | ⏳ **C'est ce qui manque encore.** Le carrousel montre aujourd'hui 6 **mises en situation** (ses vrais masques dans des intérieurs de présentation), et le dit. Ce qu'il n'a pas : la pièce seule, sur fond neutre, avec **son vrai titre, sa technique et ses dimensions**. Mongazi a annoncé ces photos-là pour plus tard. ⛔ Quand elles arrivent, elles vont dans un tableau **séparé** : une œuvre au catalogue et une mise en situation ne se mélangent pas. Les 5 règles de prise de vue sont dans `PROMPTS-IMAGES.md` § 3. |
| 3 | **Logo** | `_sources/logo-transparent.png` → `_build_assets.py` | ✅ **REÇU le 2026-08-05.** Le glyphe (axe vertical, deux barres, deux points) est détouré et posé dans la nav, le pied, la modale, le favicon, l'OG et l'affiche. Son accroche « Inspiré d'en haut, enraciné ici. » remplace celle qu'on avait écrite. |
| 4 | **Photos d'atelier / portrait** | héros, « La démarche », les 4 temps, « La citation », « Pour un lieu », « La visite » | ✅ **REÇUES ET POSÉES le 2026-08-08.** 7 photos réelles d'Angélique au travail. **Plus une seule image générée sur le site.** Détail au § 6. |
| 5 | **Vrais témoignages** | section « La citation » | ⏳ la section affiche une phrase **d'Angélique**, signée d'elle. Le jour où un vrai client écrit : remplacer la citation et l'attribution. ⛔ Jamais un faux critique, jamais un faux magazine. |
| 6 | **Adresse / atelier** | pied de page + « L'atelier » | ⏳ « Cotonou » seul pour l'instant. Pas de carte tant que l'adresse n'est pas donnée : un mauvais repère est pire que pas de repère. |
| 7 | **Musique** | FAB son | ✅ ambiance de salle **synthétisée** (Web Audio, aucun fichier, aucun droit à payer). Remplaçable par une piste dont elle détient les droits. |
| 8 | **Prix / fourchettes** | nulle part | ⏳ aucun prix affiché, volontairement : en art, le prix se dit dans la conversation, et un prix ferme la porte aux commandes d'hôtel. À rediscuter avec elle. |
| 9 | **Domaine** | — | ⏳ `angy-art.pages.dev` pour l'instant. `angyart.com` ou équivalent = étape séparée. |

## 5. Décisions prises (et pourquoi)

- **Page unique, scroll long.** Elle a demandé une navigation immersive ; un hub
  multi-pages casse le fil d'une visite de galerie.
- **Aucun prix sur le site.** Une œuvre unique ne se tarife pas en vitrine ; afficher un
  prix ferme la porte aux commandes d'hôtel, qui sont le meilleur budget.
- **Le portfolio ne ment pas.** Plutôt que des visuels inventés, le carrousel montre les
  matières de l'atelier et propose l'envoi du portfolio complet sur WhatsApp. C'est honnête,
  et ça convertit mieux qu'une grille floue.
- **La citation est signée d'Angélique**, pas d'un critique inventé. Zéro faux témoignage.
- **Pas de carte** tant que l'adresse exacte n'est pas connue.
- **Aucune bibliothèque JavaScript**, malgré un brief qui demandait Next.js, GSAP, Lenis et
  Swiper : tout est réécrit en natif. Motif : règle NEBULA et réalité 4G à Cotonou.
  Le rendu demandé est là ; le poids ne l'est pas.
- **La modale ne promet pas de créneau.** Trois questions, puis WhatsApp avec la demande
  déjà rédigée. Il n'y a pas d'agenda derrière : annoncer une disponibilité qu'on ne tient
  pas coûte le client.

## 6. Les images du site — TOUTES RÉELLES depuis le 2026-08-08

**Les 13 images générées par IA ont été supprimées** (8 fausses œuvres + 5 scènes
d'ambiance), avec `_gen_images.py` et `_pose_images.py`. Les prompts restent tracés dans
`PROMPTS-IMAGES.md`, et l'historique git garde le reste. Coût enterré : 2,80 $.

Mongazi a envoyé **15 photos** le 2026-08-08, en précisant : « ce ne sont pas ses
produits, ce sont des images pour rendre son activité plus authentique ». Deux familles,
et elles ne se traitent pas pareil.

### a. Les 7 photos d'atelier — 100 % réelles, aucune retouche

Angélique au travail, à Cotonou. Ce sont elles qui portent l'authenticité du site.

| Fichier produit | Ce qu'on y voit | Où |
|---|---|---|
| `scenes/matiere.webp` | détail du relief, sans personne (recadré dans la photo « dehors ») | 04 La citation |
| `scenes/demarche.webp` | penchée sur sa table, fleurs bleues, pinceau fin | 01 La démarche |
| `scenes/temps-1.webp` | l'enduit blanc sur une forme encore nue | 02 · La forme |
| `scenes/temps-2.webp` | elle mélange l'orange, palette dans un cadre doré | 02 · La couleur |
| `scenes/temps-3.webp` | la ligne blanche au pinceau sur le terracotta | 02 · Le trait |
| `scenes/temps-4.webp` | assise sur un tabouret devant une toile de plus de 2 m | 02 · L'échelle |

### b bis. Le héros porte UNE ŒUVRE, pas l'artiste

Mongazi a tranché le 2026-08-08 : « utilise une des images des œuvres
d'Angélique, ça doit être spectaculaire ». Le héros montre donc **le duo
terracotta sur socles dorés** (`scenes/hero.webp`, recadré depuis `situ-duo`,
plus serré que la carte `situ-1` du carrousel).

⚠️ **Le choix ne tient pas au goût.** Cinq cadrages serrés ont été regardés côte
à côte : terracotta seul, duo, perles, relief réel, jaune. Quatre posent leur
masque sur **un mur beige pâle**, qui devient un rectangle lumineux au milieu
d'une page noire. Le duo est le seul sur **fond sombre** : le noyer se fond dans
la page, les visages flottent, et **les socles dorés reprennent son or
`#bd9f64`**. C'est cette règle qu'il faut garder si l'image change un jour :
sur cette page, un fond clair tue l'effet.

La photo d'elle qui peint dehors n'est pas perdue : elle nourrit toujours
`matiere.webp` (le détail de relief de la citation), et les sept photos
d'atelier tiennent les sections 01 et 02.

### b. Les 6 mises en situation + le lieu — ses vrais masques, décors montés

⚠️ **Les MASQUES sont bien les siens. Les INTÉRIEURS sont des rendus.** La preuve est
dans les photos elles-mêmes : le terracotta à spirale de `situ-1` est **exactement** celui
qu'elle peint sur `temps-3`, et le jaune/orange de `situ-2` est celui de `demarche`.

Donc le site les annonce pour ce qu'elles sont. Le mot **« MISE EN SITUATION »** est le
cartel de chaque carte, il est répété dans la vue en grand, dans le texte alternatif lu
par les lecteurs d'écran, et la description de la section le dit en toutes lettres.
⛔ **Aucun prix, aucune dimension, aucun titre d'œuvre inventé** : `t` décrit ce qu'on
voit (« Le bleu outremer »), il ne nomme pas une pièce. Seule Angélique peut la nommer.

Une seule retouche, sur `situ-3` : le dos d'un livre du décor portait **« PICASO »**.
C'est une faute du décor, pas de l'œuvre : elle est noyée dans un flou dégradé, comme une
profondeur de champ. ⚠️ Un flou posé sur un rectangle net **se voit** (on distingue les
quatre arêtes) : le masque est dégradé sur 55 px et déborde sur du mur uni.

`lieu.webp` (le masque monumental dans un restaurant) sert l'axe le plus commercial de son
activité : équiper un hôtel, un restaurant, un hall.

### c. La carte de partage

`assets/images/og/og.jpg` porte désormais **une vraie photo d'atelier** sur sa moitié
droite, fondue vers le noir pour que le texte de gauche reste lisible. C'est cette
vignette que voient les gens quand le lien circule sur WhatsApp, et c'est là que se joue
la première impression au Bénin. `python _build_assets.py --og` la refait seule.

⚠️ **EN JPEG DEPUIS LE 2026-08-26, ET C'EST UNE RÈGLE DE LA MAISON.** Elle était en
PNG : **566 Ko** pour une carte de texte et une photo. En JPEG à 84, la même image pèse
**96 Ko** — 83 % de moins, sans différence visible, et sans le risque qu'un lecteur de
lien abandonne un téléchargement trop long. C'est le défaut le plus cher d'un site,
parce qu'il est **invisible depuis le site**.

## 7. Journal

- **2026-08-05** — Réception de la commande. Direction « L'ENTAILLE » construite le matin
  (indigo, Young Serif), puis **remplacée en cours de session** par l'esthétique
  « Selva Toscana » demandée par Mongazi (noir, crème, Playfair). Site construit,
  **66 contrôles verts**, captures regardées section par section en 390 et 1440 px
  (quatre tours de correction), affiche A4 + 2 QR décodés, **déployé et vérifié en ligne**
  sur https://angy-art.pages.dev.

  **Second temps, le même jour** : le vrai logo arrive (glyphe or + accroche
  « Inspiré d'en haut, enraciné ici. »). Il remplace le monogramme provisoire partout,
  **son or `#bd9f64` devient l'or du site**, et son accroche remplace celle qu'on avait
  écrite. Puis 13 visuels générés et posés (voir § 6), affiche refaite avec le vrai logo
  et la vraie photo, **67 contrôles verts**, redéployé.

  Défauts trouvés **en regardant**, que le contrôle automatique ne voyait pas :
  matières trop sombres (des trous noirs), titres qui passaient sous la barre fixe,
  textes traversés par les cadres du mur, « ÉCRIRE SUR WHATSAPP » affiché deux fois,
  monogramme à une seule barre (il se lisait « A Λ »), trou de 8 cm au milieu de
  l'affiche. Le seul défaut attrapé par le contrôle, et le plus grave, était invisible
  à l'œil : **les textes d'une section sautée restaient cachés pour toujours.**
  Le monogramme provisoire n'avait qu'une barre sur deux A : il se lisait « A Λ ».
  Il a disparu avec l'arrivée du vrai logo.

- **2026-08-08 — LES VRAIES PHOTOS. Le site ne contient plus une seule image générée.**

  Mongazi envoie 15 photos, en précisant que ce ne sont pas les produits d'Angélique
  mais de quoi rendre son activité authentique. Les 13 visuels IA sont **supprimés**
  (§ 6), et avec eux les 8 fausses œuvres du carrousel, qui étaient le point faible
  du site depuis sa mise en ligne.

  Nouvelle architecture, **7 sections** au lieu de 6 :

  1. héros, elle peint dehors · 2. La démarche · **3. La main, en quatre temps**
  (nouvelle : l'enduit, le pigment, le trait, l'échelle) · 4. Dans un lieu
  (ex-portfolio, six mises en situation) · 5. La citation, sur un détail de relief ·
  **6. Pour un lieu** (nouvelle : hôtels, restaurants, halls) · 7. La visite.
  L'ancien plein écran « L'ATELIER » disparaît : les quatre temps disent la même
  chose, en vrai. L'ancre `#atelier` du menu pointe désormais sur eux.

  **La signature du héros vient de son propre geste** : la photo se révèle d'abord
  sans couleur, comme la forme enduite de blanc, puis le pigment monte. Deux calques
  du même fichier, donc un seul téléchargement, et **seule l'opacité s'anime** : une
  transition de `filter` sur une image de cette taille aurait fait tressauter
  l'entrée du héros sur un téléphone.

  Défauts trouvés **en regardant, puis mesurés**, qu'aucun contrôle ne voyait :

  - ⛔ **Cliquer une entrée du menu posait l'étiquette de section à 6 px sous la
    barre fixe** (mesuré à 390 px). Le défilement est écrit à la main, donc
    `scroll-margin-top` n'était **pas** appliqué : il faut le lire et le retrancher.
    Défaut **antérieur** à cette session, il touchait aussi `#demarche` et
    `#portfolio`. Corrigé : 6 px → 90 px.
  - ⛔ **Le texte de « Pour un lieu » se posait sur un masque orange vif.** C'est la
    photo la plus claire du site et le voile standard tombe à 20 % en son milieu.
    ⚠️ **Le contrôle de contraste ne pouvait pas le voir** : il lit la couleur de
    fond *calculée*, qui est transparente au-dessus d'une photo.
  - ⛔ À 768 px, « DÉCOUVRIR L'ATELIER » **barrait** « PIÈCES · UNIQUES ».
  - Le flou posé sur le livre « PICASO » laissait voir ses **quatre arêtes**.

  Trois familles de contrôles ajoutées, pour que rien de tout ça ne revienne :
  **l'arrivée par le menu**, **le chevauchement des boîtes**, et surtout le
  **contraste mesuré sur les pixels réellement rendus** (on masque le texte, on
  photographie la zone, on prend le décile le plus clair du fond).

  ⚠️ Deux pièges rencontrés en écrivant ces contrôles, notés pour la prochaine fois :
  `page.screenshot(clip=…)` et `bounding_box()` **ne parlent pas dans le même
  repère** (page contre viewport) ; et une boîte lue **avant** que le défilement
  doux se soit posé est périmée de plusieurs centaines de pixels. Les deux
  faisaient mesurer une zone qui n'avait rien à voir.

---

## LES CRÉATIONS PERSONNALISÉES (2026-08-21)

Brief d'Angélique reçu par Mongazi : *« Une œuvre qui raconte votre histoire. »*
Une section nouvelle (`#personnalise`, crème, entre « Pour un lieu » et la
citation) et les **15 questions en trois temps**.

### La distinction Collections / Créations personnalisées

⚠️ **Le brief l'exige en toutes lettres.** Elle a ses deux blocs, et elle est
dite : une **collection** existe déjà, avec ses dimensions et sa technique — on
la regarde, on en choisit une. Une **création personnalisée** n'existe pas
encore : elle naît de l'histoire du client. **Aucun prix affiché** : c'est une
œuvre sur commande, pas un produit décoratif.

### Sa signature : l'entaille qui se creuse

« Une œuvre d'Angy, c'est une entaille dans la matière. » Ici c'est l'histoire
du visiteur qu'on entaille. **Deux traits sur le même chemin** : l'arête claire
remonte d'un pixel, le creux sombre descend d'un pixel, et le creux se trace
**160 ms après** l'arête — la main appuie, puis la matière cède. Un seul trait
n'aurait été qu'un soulignement.

### Le formulaire — ce qu'il fait, et ce qu'il ne peut pas faire

Trois temps (VOTRE HISTOIRE · VOTRE VISION · VOTRE PROJET), comme le tableau du
brief. Deux champs n'apparaissent que si on en a besoin (type « Autre »,
dimensions).

⚠️ **IL NE « SOUMET » RIEN, ET C'EST VOLONTAIRE.** Le site est statique : pas de
serveur, pas de base, pas de boîte mail. Il **rédige** le brief et ouvre la
conversation WhatsApp avec le texte déjà écrit. Un bouton qui ferait semblant
d'envoyer serait le pire des défauts : le client croirait sa demande partie.

⚠️ **La question 11 (téléversement) devient une phrase.** On ne peut pas recevoir
un fichier sans serveur. Plutôt qu'un bouton « Parcourir » qui n'enverrait rien,
on dit au client de joindre ses photos dans la conversation — au Bénin c'est de
toute façon le geste naturel — et le message le rappelle à Angélique.

⚠️ **Le nom et la date sont dans le message.** Le brief demande de pouvoir
identifier une demande par le nom du client et sa date : sans base, c'est le
message lui-même qui les porte.

⏳ **Ce qui reste hors de portée du statique** (§8 du brief) : notification
automatique, stockage sécurisé des pièces jointes, historique des demandes.
Cela demande n8n + un stockage — hors périmètre d'une vitrine.

### ⛔ Trois défauts vus sur les captures, pas dans le code

1. **`.pill--plein` est crème sur noir** : posé sur une section claire il
   devient **crème sur crème**, donc invisible. Le site n'avait **aucun bouton
   pour un fond crème** — les sections claires n'avaient que des liens
   soulignés. → `.pill--encre`, 15,2:1.
2. **`hidden` ne cachait rien** : `.ch` et `.etp` sont en `display:grid`,
   `.pill` en `display:inline-flex`, et un `display` déclaré écrase le
   `display:none` de la feuille par défaut. Le champ « Précisez » s'affichait
   sans raison, **les trois étapes étaient empilées d'un coup**, et le bouton
   d'envoi débordait. → sélecteurs d'attribut, sans `!important`.
3. **Les champs débordaient à 390 px** : un enfant de grille a
   `min-width:auto`, pas zéro. La piste s'élargit jusqu'à la largeur
   **intrinsèque** de son contenu, et un long texte d'invite dans un
   `textarea` poussait les champs dehors. `width:100%` n'y peut rien.

Au passage : la largeur d'une modale se déclare sur `[open]` — un `max-width`
seul ne sert à rien quand une `width` est fixée ailleurs.

### Contrôles : 106 → 121, tous verts

15 neufs, qui parcourent le formulaire comme une visiteuse. Et **deux qui
mentaient** :
- « la demande part sur WhatsApp » ouvrait **vraiment** `wa.me` : il testait la
  connexion, pas le message, et rendait rouge un site parfait hors ligne. On
  intercepte `window.open` et on lit l'URL.
- « deux familles chargées » a besoin de Google Fonts : hors ligne il accusait
  le site. Il se saute maintenant **en le disant**. Les deux contrôles qui
  lisent la police *demandée* restent stricts.

### ⏳ À trancher par Mongazi

1. Le brief écrit **« ANGYART »** ; tout le site écrit **« Angy Art »**. J'ai
   gardé l'orthographe du site. Si elle préfère l'autre, c'est un passage
   partout (nav, pied, JSON-LD, affiche, OG).
2. Le **bouton du son** d'Angy est en `position:fixed` en bas à droite, comme
   l'était celui d'Hillary avant le 2026-08-21 : il peut recouvrir du texte.
   Le détecteur écrit pour Hillary s'applique tel quel si on veut vérifier.

---

## SES SIX ŒUVRES ENTRENT AU SITE (2026-08-21)

C'était le manque le plus ancien : *« reste : photos des œuvres seules, dans un
tableau `OEUVRES` SÉPARÉ de `SITUATIONS` »*. Angélique a envoyé six pièces avec
titres, techniques, palettes, dimensions, prix et ses propres textes.

| œuvre | dimensions | prix |
|---|---|---|
| Bonheur éternel | 1 m 20 × 80 cm | **prix sur demande** |
| L'Équilibre des Âmes | 75 × 65 cm | 250 000 F |
| Alliance Solaire | 75 × 65 cm | 250 000 F |
| Âmes Sœurs | 30 cm | 120 000 F |
| Force Silencieuse | 30 cm | 110 000 F |
| Aura | 30 cm | 100 000 F |

⚠️ **Rien n'est inventé** : tout vient d'elle, mot pour mot.

### ⚠️ Trois d'entre elles étaient DÉJÀ sur le site, anonymes

`situ-1`, `situ-2` et `situ-3` du carrousel **sont** Âmes Sœurs, Aura et Force
Silencieuse. Elles y figuraient comme décor, sans nom ni prix, avec des légendes
purement descriptives faute de mieux (« Deux visages, terre et blanc »). Elles
ont maintenant leur identité. Le carrousel garde son rôle d'ambiance.

### ⚠️ Ses textes sont écrits EN DUR dans la page

Pas dans le script. Ce qui fait la valeur de ce site — ses descriptions, les
dimensions, les prix — doit rester lisible **sans JavaScript** et visible pour
les moteurs de recherche. Six fiches **`VisualArtwork`** rejoignent le graphe
JSON-LD, avec leur `Offer` pour les cinq qui ont un prix.

### ⚠️ « MISE EN SITUATION » sur trois photos

Les masques sont bien d'Angélique ; les **niches de marbre, les livres et les
vases** qui les entourent sont des rendus. Même règle que le carrousel, posée le
2026-08-08 — et un contrôle vérifie qu'elle tient.

### Sa signature : le cartel qui s'écrit

Dans une exposition, l'étiquette se lit ligne après ligne. Technique, palette,
dimensions, prix : les quatre se posent l'une après l'autre, comme une main qui
écrit. Le geste du lieu, pas une décoration.

⚠️ **Une boîte commune, mais la vraie proportion.** Recadrer en carré alignerait
les cartes et **mentirait sur la pièce** : une œuvre d'1 m 20 sur 80 cm est
haute, et ça doit se voir. Toutes ont la même boîte — les titres s'alignent, on
compare — et l'œuvre s'y pose en `contain`.

**663 Ko** pour les six images, toutes en chargement différé.
**Contrôles : 121 → 129, tous verts.**

### ⏳ Ce qui reste

- Les **autres œuvres** : elle en a sûrement plus que six.
- Le **statut** de chaque pièce (vendue / disponible) : sans ça, une œuvre
  vendue reste affichée à son prix.
- ⏳ Toujours en attente : l'adresse de l'atelier, de vrais avis, et **tester le
  numéro WhatsApp**.

---

## 2026-08-21 — SON VOCABULAIRE, SA COLLECTION, ET LE MOTEUR DE DÉFILEMENT

Elle a envoyé un récapitulatif de sa vision. On y prend **ses mots**, pas les
nôtres.

### Le menu suit sa structure

`L'ARTISTE · LA COLLECTION · SUR MESURE · LE JOURNAL · CONTACT`

Les étiquettes des sections s'alignent dessus : `01 L'ARTISTE`,
`02 LE JOURNAL`, `04 LA COLLECTION`, `06 CRÉATIONS SUR MESURE`. La démarche,
l'atelier et les créations personnalisées n'ont pas changé de contenu : elles
ont changé de nom, parce que c'est le sien.

⚠️ L'entrée `ACCUEIL` de son récapitulatif n'est pas ajoutée au menu : le logo
en haut à gauche ramène déjà en haut, et un menu de six entrées se casse à
390 px. Le rôle est tenu, le libellé ne l'est pas — **à lui dire**.

### Le héros mène aux œuvres

`DÉCOUVRIR LES ŒUVRES` → `#oeuvres`, au lieu de `DÉCOUVRIR L'ATELIER`. On
découvre d'abord ce qu'elle vend. Et un **second appel en bas de page** mène au
sur-mesure : on découvre, puis on agit. Les deux boutons qu'elle demande.

### La collection ÉNERGIES

La section porte le **nom de la collection avant son titre** : on sait dans
quoi on entre avant de voir les pièces. Le titre est sa phrase telle quelle :
*« Donner une forme à ce qui ne se voit pas. »*

⏳ **Deux choses manquent, marquées en commentaire dans le HTML :**

1. **Son texte d'introduction de collection.** Le nôtre est *provisoire* et
   n'assemble que les mots de son récapitulatif (forces invisibles, lumière,
   liens, résilience, puissance intérieure, rayonnement, visages sculptés,
   couleurs vibrantes, esthétique africaine, symboles chargés de sens). Une
   ligne à remplacer le jour où elle envoie le sien.
2. ⚠️ **Elle annonce CINQ œuvres dans ÉNERGIES. Elle en a envoyé SIX.**
   Laquelle n'en fait pas partie ? À trancher avant la mise en ligne.

### ⚠️ LE DÉFILEMENT LISSÉ ÉCRASAIT TOUT LE MONDE

Le moteur maison (`app.js`, l'équivalent de Lenis) ne relisait sa cible que
**lorsqu'il était à l'arrêt** :

```js
window.addEventListener('scroll', function () {
  if (!anime) { cible = window.scrollY; courant = window.scrollY; }   /* ⛔ */
});
```

Pendant qu'il glissait, il écrasait tout déplacement venu d'ailleurs : la
**recherche du navigateur**, un **lecteur d'écran**, la touche **Fin**, le
passage au clavier sur un bouton hors écran. Le saut était annulé sans un mot.

C'est le piège déjà documenté sur **Au Braisé d'Or** (Lenis interrompait tout
`scrollIntoView`, saut arrêté à 7 382 px de sa cible). Retrouvé ici parce que
le QC échouait **uniquement en mode captures** : les captures laissent le
moteur en pleine course.

⚠️ **On ne peut pas adopter tout écart.** Une image perdue laisse la page **sur
le chemin** du moteur, et l'adopter arrêterait le glissement net au milieu —
une régression bien plus visible que le défaut réparé. Alors on regarde **où** :

```js
var bas = Math.min(courant, cible) - 12, haut = Math.max(courant, cible) + 12;
if (y < bas || y > haut) { cible = borne(y); courant = y; }
```

Entre `courant` et `cible`, c'est nous. Ailleurs, c'est quelqu'un d'autre, et
c'est lui qui a raison.

**Mesuré** : sans le correctif, un saut à 200 px est ramené à **5 992 px** ;
avec, la page reste à 200.

### Quatre mesures qui mentaient parce qu'elles recopiaient

| Ce qui était recopié | Ce que ça a coûté |
|---|---|
| trois ancres de menu, dont `#portfolio` | le menu a changé → `null.click()`, le contrôle **plantait** au lieu de tester |
| les étiquettes `LA DÉMARCHE` / `L'ATELIER` / `DANS UN LIEU` | le contrôle a **accusé le site** d'avoir perdu des textes qu'il avait seulement renommés |
| huit sélecteurs de sections dans `SECTIONS` | les **deux sections neuves n'ont jamais été photographiées**, et personne ne l'a vu |
| l'attente de 500 ms avant de mesurer un contraste | l'élément n'était pas à l'écran, et le contrôle criait au **défaut de contraste** |

Les trois premiers lisent la page maintenant. Le quatrième est devenu
`placer()` : on se place, **puis on vérifie qu'on y est**, et on recommence —
et si on n'y arrive pas, on le dit **avec le chiffre**.

Ce qui reste écrit en dur dans le contrôle sans JS, ce sont **ses phrases à
elle** (`ANGY`, `par sa main`, `La forme`, `Le trait`, `Retrouvons-nous`,
`ÉNERGIES`, `Votre histoire`) : celles-là ne doivent jamais disparaître, quel
que soit le vocabulaire du menu.

### Le contrôle du moteur a un témoin

« Le défilement lissé laisse passer les autres » prouve **d'abord que ça
glisse** (3 000 → 4 352 px après un coup de molette), puis saute ailleurs. Sans
le témoin, un moteur mort passerait le contrôle les doigts dans le nez : une
page qui ne glisse pas ne ramène évidemment rien. Même leçon que le contrôle de
pause de Hillary, le 2026-08-18.

⚠️ Contexte **PC uniquement** : le moteur n'existe que sur pointeur fin
(`(hover:hover) and (pointer:fine)`).

**129 → 146 contrôles, tous verts.** *(Déployé le 2026-09-02, voir la fin du document.)*

### Les six questions tranchées, faute de réponse

> Mongazi : « fais appliquer ce qui est meilleur pour le moment, si elle veut
> des modifications plus tard, elle observera et me dira. »

| Question | Ce qui est appliqué | Pourquoi |
|---|---|---|
| `ACCUEIL` dans le menu | **ajouté**, en première entrée | il est dans sa liste, et il tient : **mesuré** avant de le poser — 31 px de marge à 1024 px, 101 à 309 px au-delà, et 7 entrées dans le tiroir du téléphone (dernier lien à 686 px sur 844) |
| Quelles **cinq** œuvres dans ÉNERGIES | **les six restent, aucun nombre n'est annoncé** | en cacher une serait une **perte sèche**, et se tromper de laquelle serait pire. Le jour où elle dit laquelle est à part, c'est un attribut à poser, pas une refonte |
| Son texte d'introduction | **le nôtre tient sa place**, sans être annoncé comme provisoire | il n'invente rien : il n'assemble que les mots de son récapitulatif, et le titre au-dessus est sa phrase telle quelle. Remplaçable en une ligne |
| Statut vendue / disponible | **aucun statut inventé** + une phrase : « Chaque pièce est unique : un mot suffit pour savoir si elle est encore disponible. » | une œuvre vendue affichée à son prix ferait écrire quelqu'un **pour rien** ; annoncer « disponible » sur les six serait une affirmation qu'on ne peut pas tenir. Cette phrase est vraie dans les deux cas, et elle tombe **avant la grille** |
| « ANGYART » ou « Angy Art » | **Angy Art**, en deux mots | c'est ce que portent déjà le logo, la barre, le pied, l'image de partage, le JSON-LD et l'affiche. La cohérence vaut mieux qu'un tirage au sort |
| Texte de la page L'ARTISTE | **son texte de démarche existant** | il parle d'elle et de sa main. Rien à inventer en attendant le sien |

⚠️ Le libellé du sur-mesure reste **court** dans la barre (« SUR MESURE ») : sa
formule complète, « CRÉATIONS SUR MESURE », déborderait à 1024 px, et elle se
lit déjà deux fois plus bas — sur la section et sur le bouton de fin de page.

### ⚠️ Un contrôle qui ne prouvait rien

Une entrée « ACCUEIL » **testée depuis le haut de la page** passerait même si le
lien était mort : arriver à 0 en partant de 0 n'est pas une preuve. On part donc
du **bas** pour celle-là (mesuré : 12 082 → 0 px), et du haut pour les autres.
Même famille que le témoin du 2026-08-18.

**149 contrôles verts.**

## ✅ Publié le 2026-09-02, depuis le PC de Cotonou

Tout ce qui dormait dans `main` est en ligne : les quatre corrections
d'Angélique, le bouton du héros devenu **sommaire**, et la vague fluidité.

```bash
python clients/11-angy-art/_dist.py
wrangler pages deploy clients/11-angy-art/_dist --project-name=angy-art --branch=main
```

⚠️ **`wrangler` global, pas `npx`** : le paquet a été supprimé avec les
`node_modules` et le cache npm a été vidé. Le jeton vient de
`secrets/cloudflare.env`, ignoré par git : **une session en conteneur ne peut
pas publier**, c'est le PC qui le fait.

**Ce qui a été vérifié après coup**, et pas seulement le code de retour :

- `_dist` reconstruit : **37 fichiers, 4,67 Mo**, aucune trace des anciennes
  images générées ;
- **150 contrôles verts** avant l'envoi ;
- `index.html`, `app.js` et `app.css` servis **identiques au disque en MD5** ;
- **34 fichiers sur 37 répondent 200**, et les 3 autres sont corrects :
  `_headers` en **404** (c'est un fichier de configuration, il ne doit pas
  être public), `index.html` et `404.html` en **308** vers leurs adresses
  propres ;
- un fichier absent répond bien **404** ;
- le corps servi porte `ACCUEIL`, `L'ARTISTE`, `SUR MESURE`, `ÉNERGIES`, les
  titres d'œuvres et les trois cartels **MISE EN SITUATION**.

⚠️ **Un `git push` ne déploie rien.** Le travail était dans `main` depuis le
2026-08-21 et le site servait encore l'état d'avant.

### ⏳ Ce qui reste, au 2026-09-02

- Ce qu'elle pourra corriger **en observant** : la cinquième/sixième œuvre
  d'ÉNERGIES, son texte d'introduction, le statut de chaque pièce.
- Toujours : l'adresse de l'atelier, de vrais avis, **tester le numéro
  WhatsApp**, et les **photos des œuvres seules** (fond neutre).

## ✅ 2026-08-22 · SES SIX ŒUVRES SONT EN LIGNE

Le travail de la session téléphone (les six œuvres nommées et chiffrées, son
vocabulaire, la collection ÉNERGIES, le second appel, les créations
personnalisées) était **dans `main` sans être publié** : les six images
répondaient **404** et la page servie faisait 20 953 octets contre 59 976
aujourd'hui. La session en conteneur n'avait pas les jetons Cloudflare
(`secrets/` est ignoré par git) : c'est le PC de Cotonou qui publie.

Vérifié en ligne : les **six fichiers** répondent 200 (`alliance-solaire`,
`ames-soeurs`, `aura`, `bonheur-eternel`, `equilibre-des-ames`,
`force-silencieuse`), les prix s'affichent (100 000 / 200 000 / 350 000 /
500 000 FCFA), et `app.js` servi est **identique octet pour octet** au disque.

⚠️ Version bumpée à **`?v=20260822a`** (27 endroits) : `app.js` a changé, et nos
fichiers portent `immutable` pour un an.

### ⚠️ Deux pannes de contrôle, un vrai défaut de site

**1 · Le serveur de test était mono-tâche.** `Page.goto: Timeout` sur
`127.0.0.1:8611`, et rien ne démarrait. Le navigateur garde ses connexions
ouvertes : l'une bloquait les autres. Passé en `ThreadingTCPServer`, comme chez
Hillary le 2026-08-17. **Ce n'était pas le site.**

**2 · Le contrôle pariait sur 1 700 ms.** Il attend maintenant que la page
**se pose** (immobile trois relevés d'affilée, 6 s au plus).

**3 · Et un VRAI défaut, celui-là :** « accueil » ramenait bien en haut sur
téléphone et sur tablette, mais laissait la page à **284 px** (puis 467 px à
l'essai suivant) **sur ordinateur**, là où le défilement maison remplace le
natif. Sa boucle avançait **d'un cran fixe par image** :

```js
courant += (cible - courant) * 0.095;   // dépend de la cadence
```

Sur une machine à 30 images par seconde, le même geste dure **deux fois plus
longtemps** que sur une à 60. Le glissement n'était pas cassé, il n'était pas
fini. Corrigé en interpolant **au temps** :

```js
var k = 1 - Math.pow(1 - 0.095, dt / 16.7);
```

⚠️ **C'est le téléphone bas de gamme de Cotonou qui payait la différence**, et
aucun contrôle ne l'aurait vu : sur mobile, le moteur maison ne tourne même pas.

**150 contrôles verts, 0 en échec.**


---

## 2026-08-27 — Le bouton « Découvrir les œuvres » est retiré

Demandé par Angélique. Il avait été ajouté le 21/08 sur son propre
récapitulatif (« un bouton pour Découvrir les œuvres menant directement à la
collection ») : elle change d'avis en le voyant, c'est son droit et c'est
exactement à ça que sert une mise en ligne.

Retiré **partout**, pas seulement du balisage : les quatre règles CSS qui le
portaient (position absolue sur grand écran, retour dans le flux sous 768 px,
révélation à l'ouverture du héros, exception « mouvement réduit ») sont parties
avec lui. Il ne reste **aucune trace** de `.hero-pill` dans le projet.

⚠️ **Et les deux paires du contrôle de chevauchement qui le nommaient.** Elles
ne plantaient pas — le contrôle rend `None` et annonce « absent à cette
taille » — mais **un contrôle qui décrit un élément disparu ne protège plus
rien et fait croire qu'il veille.** Remplacées par une paire qui, elle, n'était
pas testée : `.hero-mx li` contre `.cadre`.

**Arithmétique vérifiée plutôt que supposée** : 149 → 146. Six contrôles
partis (deux paires × trois largeurs), trois gagnés (une paire × trois
largeurs). La baisse s'explique entièrement.

Regardé à 390, 768 et 1440 : aucun trou. Le bouton était en position absolue,
sa disparition ne déplace rien ; la ligne des métriques garde ses 42 à 48 px
de marge basse.

⚠️ La collection reste atteignable depuis le haut par l'entrée **LA
COLLECTION** du menu. Rien n'est isolé.

---

## 2026-08-27 (2) — Les quatre corrections d'Angélique, et le sommaire du héros

⚠️ **Correction de la correction précédente** : elle ne voulait pas *supprimer*
le bouton « Découvrir les œuvres », elle voulait le **transformer**. Elle
regarde le site **sur téléphone**, et là le menu burger ne lui suffit pas :
elle veut voir d'un coup d'œil ce que le site contient, et y accéder
directement.

### Le sommaire

Six entrées à la place du bouton unique : L'ARTISTE · **DÉCOUVRIR LES ŒUVRES**
· LE JOURNAL · DANS UN LIEU · CRÉATIONS SUR MESURE · CONTACT. Le libellé de la
deuxième est **sa formule à elle**, elle l'a nommée telle quelle.

⚠️ **Dans le flux, pas en position absolue** comme l'ancien bouton : celui-ci se
posait *sur* la ligne des métriques dès que le héros passait sur une colonne
(« DÉCOUVRIR L'ATELIER » barrait « PIÈCES · UNIQUES » à 768 px, corrigé le
2026-08-08). Le héros est une colonne flex, le sommaire y prend sa place.

⛔ **Et le bouton du son se posait dessus.** Mesuré : **11 × 34 px** de
recouvrement sur « DÉCOUVRIR LES ŒUVRES », **à 390 px et nulle part ailleurs**
— c'est-à-dire pile la pastille qu'elle a nommée, pile la largeur où elle
regarde. La colonne de droite lui est réservée, et un contrôle le vérifie aux
trois largeurs.

### L'ordre et les noms

`01 L'ARTISTE · 02 COLLECTION ÉNERGIES · 03 LE JOURNAL · 04 DANS UN LIEU ·
05 CRÉATIONS SUR MESURE`. La collection passe **avant** le journal, et « Dans
un lieu » — la mise en situation, qu'elle ne trouve pas claire — passe après.
Le menu suit l'ordre de la page.

La numérotation allait `01, 02, 03, 04, 06` : la suite était **déjà trouée**.

⚠️ **L'ordre a été changé en découpant le fichier en tranches qui se touchent**,
pas en recollant des morceaux choisis : **longueur identique au caractère près**
avant et après. Une première version extrayait les sections et les recollait ;
les commentaires d'en-tête restaient dehors, et le garde-fou de longueur a
refusé d'écrire.

### ⚠️ La typographie : mesurer avant d'appliquer

Elle dit : « le texte qui suit immédiatement les titres de section est plus
grand que les titres eux-mêmes ». Pris au pied de la lettre, ça vise les `h2`
— **et c'était faux** : ils font déjà 80 px contre 14 à 19 px pour les
paragraphes, cinq fois plus.

**Mesuré, le vrai coupable est ailleurs** : l'**étiquette** de section faisait
10,5 px et la phrase en dessous 80 px. **Sept fois et demie.** Et c'était le
**seul endroit du site** où la suite dépassait son titre — les six étiquettes,
nulle part ailleurs.

Le nom prend donc la taille d'affichage (`clamp(1.45rem, 3.4vw, 2.9rem)`), la
phrase devient une entrée en matière, et la citation descend aussi (elle
passait devant son étiquette de 1,6 px).

⚠️ **Deux finitions vues sur les captures, pas dans les contrôles** : le filet
`.lab b` restait orphelin à droite du nom quand celui-ci se replie à 390 px (il
prend toute la largeur et devient un soulignement), et le titre de la section
des œuvres se collait à son étiquette — elle n'avait pas de marge propre,
contrairement à `.demarche`, `.temps` et `.folio`.

⚠️ **La requête média du filet était placée AVANT la règle qu'elle corrige** :
à spécificité égale la dernière gagne, elle ne servait à rien. Déplacée après.

**146 → 149 contrôles verts.** Regardé à 390, 768 et 1440.

### ✅ Tranché

« Collection Énergie » (singulier, dans la note) contre **ÉNERGIES** (pluriel,
son récapitulatif du 21/08, ce qui est en ligne, et ce qui colle au contenu :
« les forces invisibles : la lumière, les liens, la résilience… »). Mongazi :
**« non ça va »** — le pluriel reste.

---

## 2026-09-04 — UN SEUL BOUTON « DÉCOUVRIR », ET IL NE QUITTE PLUS L'ÉCRAN

**Mongazi** : « je veux que tous ces points se voient quand on clique sur un seul
bouton, découvrir, et qui reste visible partout sur la page, surtout sur mobile ».

Le sommaire du 2026-08-27 faisait son travail **au bas du héros, et nulle part
ailleurs**. Passée la première section, il ne restait que le burger : exactement ce
dont Angélique se plaignait. **Ce n'est pas la liste qui manquait, c'est sa présence.**

### Un seul contrôle, deux places, jamais deux à l'écran

- **héros** : pastille crème « DÉCOUVRIR », **dans le flux**, à la place du sommaire ;
- **barre** : la même en pilule, à **toutes les largeurs**, elle remplace le burger ;
- celle de la barre **s'efface tant que celle du héros est à l'écran**
  (`IntersectionObserver`, seuil 0) et prend le relais dès qu'elle en sort.
  ⚠️ **Par défaut elle est VISIBLE** : si l'observateur meurt, il reste un bouton,
  jamais zéro.

Mesuré : à **390 px** le bouton du héros est **sous la ligne de flottaison** à
l'arrivée, donc c'est celui de la barre qu'on voit tout de suite ; à 768 et 1440 c'est
l'inverse. Dans les deux cas, **un et un seul**.

### Le panneau porte SON sommaire, entier

ACCUEIL · L'ARTISTE · **DÉCOUVRIR LES ŒUVRES** · LE JOURNAL · **DANS UN LIEU** ·
**CRÉATIONS SUR MESURE** · CONTACT · ÉCRIRE SUR WHATSAPP.

⚠️ **Les deux listes ont fusionné.** La barre portait des libellés **raccourcis**
(« LA COLLECTION », « SUR MESURE ») parce qu'elle débordait à 1024 px avec les vrais,
et « DANS UN LIEU » n'y était pas. Dans un panneau la contrainte de largeur tombe :
ses formules complètes reviennent.

### ⚠️ Pourquoi la barre et pas une pastille flottante

Une pastille flottante serait plus près du pouce, et elle est **interdite** : un
instrument flottant ne recouvre jamais du texte. Ce site l'a payé le **2026-08-27**
(le bouton du son sur « DÉCOUVRIR LES ŒUVRES », 11 × 34 px, à 390 px seulement). La
barre du haut est **la seule chose de ce site qui ait le droit de passer devant une
phrase**, parce qu'elle est **vraiment opaque** (vérifié par `_audit.py`).

### ⛔ Trois défauts vus SUR LES CAPTURES, le QC étant vert

Trouvés dans `_vues/dec-*.png` (nouveau `python _vue_decouvrir.py` : héros, panneau
ouvert, barre en cours de page, en 390 et 1440).

1. ⛔ **Le panneau recouvrait le bouton qui venait de l'ouvrir** — plus aucune croix
   à l'écran. Le panneau est un **enfant de la barre** : son `z-index` se compte **à
   l'intérieur** de la barre. → `position:relative;z-index:2` sur le bouton.
   ⚠️ Même famille que la leçon Hillary du 2026-08-21 : « il change de parent, pas de
   style ».
2. ⛔ **« DEMANDER UNE VISITE » coupé en deux** par le bord du panneau (« DEM… ») :
   elle se retire tant que le panneau est ouvert.
3. ⚠️ **Cadre de focus sur le premier lien au simple toucher** : le focus va
   maintenant **sur le panneau** (`tabindex="-1"`), qui n'a pas à désigner une entrée.

### Ce qui a été tenu

- **Sans JS** : le bouton **se retire** (il n'ouvrirait rien), le panneau redevient la
  **rangée de liens** repliée sur plusieurs lignes, et **la barre cesse de flotter**
  (`position:static`) — son fond n'arrive qu'au défilement, par le script.
- **Au clavier** : le reste de la page devient **inerte**, Échap referme, **le focus
  revient sur le bouton qui a ouvert**.
- **Le voile** est en `pointer-events:none` fermé, dans le même état que son opacité
  (chez Hillary il avalait les clics 350 ms après sa fermeture).
- **Panneau centré par marges automatiques, pas `justify-content:center`** : quand ça
  déborde, une marge automatique retombe à zéro, là où `center` **coupe le début** et
  le rend inatteignable.

### Contrôles : 150 → 188 (et `_audit.py` toujours 22 verts)

Trente aux trois largeurs, plus trois sans JavaScript. ⚠️ **« toujours un » et
« jamais deux » sont deux contrôles distincts** : le premier seul laisserait passer
deux boutons ensemble, le second seul une page qui n'en a plus aucun. Et **« se voit »
se mesure** : les 8 entrées sont comptées en boîtes réellement dans la fenêtre, et un
panneau qu'il faudrait faire défiler est refusé.

⚠️ **Le contrôle du couloir du son visait `.hero-plan a`**, qui n'existe plus : il vise
`.hero-dec`.

### En ligne

`?v=20260904a` (feuille et script seulement, les images n'ont pas changé). Vérifié
avec un vrai `User-Agent` : `app.css` et `app.js` **identiques au disque en MD5**,
`index.html` porte les deux boutons, **aucune trace de `hero-plan`**, 404 sur un
fichier absent.

---

## 2026-09-04, second temps — la barre redevient visible, le bouton flottant s'ajoute

**Mongazi, après avoir vu la version du matin :** « il y avait directement tout qui
était visible, remets ça ».

### Ce qui était faux

Le bouton unique avait **remplacé** les liens de la barre. La demande d'Angélique
(« voir d'un coup d'œil ce que le site contient ») venait de son usage **téléphone**,
et la réponse l'avait appliquée **à toutes les largeurs**. Sur ordinateur, où la place
ne manque pas, on avait retiré une navigation qu'on VOIT pour une navigation qu'on
OUVRE : un geste de plus pour tout le monde, pour un problème de petit écran.

⚠️ **Une contrainte de téléphone ne se généralise pas à l'ordinateur.**

### Ce qui est en place

- la barre retrouve ses **6 entrées + WhatsApp**, le **burger reste sur téléphone** ;
- le **sommaire du héros revient** (6 entrées, dans le flux) ;
- le **bouton flottant s'AJOUTE au lieu de remplacer** : il ouvre le même panneau, à
  toutes les largeurs. **Trois portes, trois habitudes, un seul mécanisme** — ouvrir
  l'une referme l'autre, et chacune gèle ce qui n'est pas elle ;
- ⚠️ **les deux instruments flottants partagent UN couloir réservé, pas deux** ;
- **sans JS** le bouton flottant se retire, la barre cesse de flotter.

### ⛔ Un recouvrement se CALCULE, il ne s'échantillonne pas

Premier jet : défiler par paliers de 400 px et comparer les boîtes. Trois cibles
trouvées, réservées, **contrôle vert — et il en restait une** : « ÉQUIPER UN LIEU »,
**54 px de recouvrement à 390 px**. Sa fenêtre de croisement fait **102 px** : un pas
de 400 la manque **quatre fois sur cinq**.

**Un contrôle qui dépend de l'endroit où l'on regarde n'est pas un contrôle.**

Le bouton est **fixe**, la cible **défile** : on résout l'intervalle de défilement où
les deux se croisent. Exact, instantané, sans faire bouger la page. ⚠️ On écarte ce
qui ne défile pas (un ancêtre `fixed` ne passera jamais sous le bouton).

### ⚠️ Le `?v=` n'avait pas été bumpé

Feuille et script changés de 307 et 107 lignes, marque restée `20260904a` — **déjà
servie le matin avec l'ancien contenu**, et nos assets portent `immutable` un an.
Tous ceux qui avaient ouvert le site dans la matinée, **Mongazi le premier**, seraient
restés sur l'ancienne version. → `?v=20260904b`. Défaut du 2026-08-08 à l'identique :
**le cache du navigateur ne se voit pas depuis le serveur, et le QC ne le dit pas.**

### Contrôles : 188 → 209
