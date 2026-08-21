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

`assets/images/og/og.png` porte désormais **une vraie photo d'atelier** sur sa moitié
droite, fondue vers le noir pour que le texte de gauche reste lisible. C'est cette
vignette que voient les gens quand le lien circule sur WhatsApp, et c'est là que se joue
la première impression au Bénin. `python _build_assets.py --og` la refait seule.

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
