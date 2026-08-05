# Client 11 — ANGY ART

**Angélique AVOCEVOU** · artiste plasticienne · Cotonou, Bénin
Commande reçue le **2026-08-05** via le formulaire nebula-agency.online.

| | |
|---|---|
| Marque | **Angy Art** |
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
⚠️ **L'or `#c9b99a` du brief est illisible sur le crème (1,68:1)** : les italiques et les
liens sur fond clair utilisent `#7e6d3a` (4,4:1). Tout le détail, et la liste de ce qui a
été écarté du brief avec les motifs, dans **`DESIGN.md`** (à lire avant tout CSS).

Une première direction « L'ENTAILLE » (indigo, Young Serif) avait été construite le matin
même puis remplacée. Sa phrase fondatrice survit et porte encore les scènes :
*une œuvre d'Angy, c'est une entaille dans la matière.*

## 3. Fichiers

```
index.html            la page (source directe, aucun build : zéro image base64)
assets/app.css        tout le style        ⚠️ bumper ?v= à chaque modif
assets/app.js         tout le comportement ⚠️ bumper ?v= à chaque modif
                      ↳ les tableaux OEUVRES et MATIERES sont EN HAUT du fichier
assets/images/        favicon / og / qr / gallery  (gallery vide, en attente)
affiche.html          l'affiche A4 imprimable → assets/docs/Affiche_Angy_Art_A4.pdf
_qc.py                la suite de contrôle : 66 contrôles, verte avant tout déploiement
                      `python _qc.py --voir` produit aussi les captures par section
_build_assets.py      favicon + OG + QR (ré-exécutable, chaque QR est RELU par décodage)
404.html _headers robots.txt sitemap.xml
_qc_captures/         les captures (jamais déployées)
_dist/                ce qui part sur Cloudflare (généré)
```

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
| 2 | **Photos des œuvres** | tableau `OEUVRES` en haut de `assets/app.js` + `assets/images/gallery/` | ⛔ aucune. Le carrousel présente en attendant **les matières de l'atelier** (toile, pigment, relief, textile, lumière), qui sont vraies. Une ligne ajoutée dans `OEUVRES` remplace les matières par les œuvres : cartel, compteur et vue en grand suivent tout seuls. **Aucune image IA, aucun titre inventé** : règle absolue. |
| 3 | **Logo** | `assets/images/favicon.svg` + `_build_assets.py` (favicon, OG) | ⏳ annoncé sur WhatsApp. En attendant, monogramme typographique `A·A` gravé, remplaçable sans refonte. |
| 4 | **Photos d'atelier / portrait** | héros, « La démarche », « L'atelier », « La visite » | ⏳ **quatre emplacements** attendent une vraie photo. Chacun est un `.scene` : y poser une `<img class="scene-p">` suffit, la matière dessous disparaît. |
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

## 6. Journal

- **2026-08-05** — Réception de la commande. Direction « L'ENTAILLE » construite le matin
  (indigo, Young Serif), puis **remplacée en cours de session** par l'esthétique
  « Selva Toscana » demandée par Mongazi (noir, crème, Playfair). Site construit,
  **66 contrôles verts**, captures regardées section par section en 390 et 1440 px
  (quatre tours de correction), affiche A4 + 2 QR décodés, **déployé et vérifié en ligne**
  sur https://angy-art.pages.dev.

  Défauts trouvés **en regardant**, que le contrôle automatique ne voyait pas :
  matières trop sombres (des trous noirs), titres qui passaient sous la barre fixe,
  textes traversés par les cadres du mur, « ÉCRIRE SUR WHATSAPP » affiché deux fois,
  monogramme à une seule barre (il se lisait « A Λ »), trou de 8 cm au milieu de
  l'affiche. Le seul défaut attrapé par le contrôle, et le plus grave, était invisible
  à l'œil : **les textes d'une section sautée restaient cachés pour toujours.**
