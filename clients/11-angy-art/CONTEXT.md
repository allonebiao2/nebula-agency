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
| `scenes/hero.webp` | de profil, dehors, elle trace les motifs blancs d'un grand masque | héros |
| `scenes/demarche.webp` | penchée sur sa table, fleurs bleues, pinceau fin | 01 La démarche |
| `scenes/temps-1.webp` | l'enduit blanc sur une forme encore nue | 02 · La forme |
| `scenes/temps-2.webp` | elle mélange l'orange, palette dans un cadre doré | 02 · La couleur |
| `scenes/temps-3.webp` | la ligne blanche au pinceau sur le terracotta | 02 · Le trait |
| `scenes/temps-4.webp` | assise sur un tabouret devant une toile de plus de 2 m | 02 · L'échelle |
| `scenes/matiere.webp` | détail du relief, sans personne (recadré dans le héros) | 04 La citation |

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
