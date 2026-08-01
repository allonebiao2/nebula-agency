# CONVENTIONS NEBULA — standards non négociables

> Règles que le skill doit honorer systématiquement. Sources : `CLAUDE.md`, mémoire/feedback, exécution Djambar Team.

## Architecture & fichiers
- **Socle partagé** `assets/app.css` + `assets/app.js` (≠ pages auto-contenues lourdes). Ajouter un pôle = dupliquer 1 page légère.
- **Cache-bust** `?v=AAAAMMJJx` sur app.css/app.js → **bumper à chaque modif** du socle (sinon cache périmé : « tout cassé sur PC, OK mobile »).
- **Images** : chemins **relatifs** (`assets/images/…`) pour un **hub multi-pages déployé** (plus léger, cacheable, lazy-load).
  - Nuance vs règle « base64 » : le **base64** reste la règle pour les **vitrines mono-fichier**. Multi-pages = relatif assumé.
  - **Jamais** d'images en CDN Google Drive.
- Dossiers client : `clients/NN-slug/` avec `assets/{images,videos,docs}` + `CONTEXT.md`.

## Direction artistique — le standard « 100 000 € » *(2026-08-01, non négociable)*
> Manuel complet : **`_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`**, à lire
> AVANT d'écrire une ligne de CSS, sur chaque vitrine.

- **Une vitrine n'est pas finie quand elle marche, elle est finie quand elle impressionne.**
  QC vert et beauté sont **deux** critères de sortie, pas un.
- **La phrase d'abord** : ce qu'est le métier vu de l'intérieur, en une ligne, avec un objet
  concret (le fil, la braise). Toutes les animations en sortent. Sans phrase, on décore.
- **Une animation signature DIFFÉRENTE par section, tirée du métier.** Une animation
  transposable telle quelle chez un autre client est à refaire.
- **Les trois choses qui font 80 % de l'écart, et aucune n'est une animation** : la typo
  display à caractère et à gros corps (didone/garamond/grotesque selon le registre, jamais
  Montserrat/Inter/Roboto/Poppins), le **rythme alterné sombre/clair** des fonds, et le
  **vide** qu'on ose laisser. Jamais de `#000` ni de `#fff` en fond : une encre, un papier.
- **INTERDIT ABSOLU : une photo produit générée par IA présentée comme le catalogue du
  client.** Aucune exception, même « pour la démo ». Ambiance et texture : autorisées.
  Sans photos → dessin au trait animé (SVG qui se trace) + cartes « photo à venir ».
- **Perf** : `prefers-reduced-motion` ; sur téléphone on fige le grain et on retire une
  nappe floutée ; **aucune animation infinie sous un `backdrop-filter`** ; **jamais de
  `transform` sur un écran contenant un `position:fixed`**. Aucune bibliothèque.
- **Source / construction / livrable** : on édite `_vitrine_src.html`, `_build.py` génère
  `vitrine.html` — **jamais édité à la main**. Gabarits : `procedure-vitrine/templates/`.
- **Regarder les captures section par section** en 390 et 1440 avant de dire « fini ».

## Visuel / UX
- **Typo** : display **selon le registre du métier** (didone Bodoni pour la mode, Cormorant
  pour la matière/l'artisanat, grotesque à caractère pour le commerce) + body sans
  distinctive. Éviter Montserrat/Inter/Roboto/Poppins « sur-utilisés ». Voir DIRECTION-ARTISTIQUE §2.1.
- **Palette** : respecter la **couleur imposée** par le client ; accents métier (or/argent pour bijoux).
- **0 emoji en icône** → **SVG** (cohérents, viewBox 24, stroke uniforme).
- **Accessibilité** : contraste ≥ 4.5:1, focus visibles, `aria-label` sur icônes/boutons, labels de formulaire, alt descriptifs.
- **Tactile** : cibles ≥ 44×44 px, `cursor:pointer`, hover sans décalage de layout.
- **Animations** : 150–300 ms, `transform`/`opacity`, respecter **`prefers-reduced-motion`**.
- **Mobile-first** : tester 375/390/768/1024/1440 ; **0 débordement horizontal** (mesuré).
- **Pas de cadence « IA »** : limiter les em-dashes « — » dans le texte courant (préférer `·`, virgules, deux-points) — le hook impeccable le signale.

## Contenu
- **Contenu manquant** → version **pro par défaut « à valider »**, jamais un placeholder vide.
- **Avis** : exemples **explicitement marqués** « à valider » ; ne pas faire passer de faux avis pour réels.
- **Watermarks** des photos client = son branding → **conservés**.

## WhatsApp / contact
- Liens `https://wa.me/<numéro>` **pré-remplis par contexte** (message adapté à la page/produit).
- **Confirmer le numéro** avec le client **avant** câblage (règle absolue). Ne jamais changer un lien WhatsApp sans confirmation.
- **FAB WhatsApp** + **FAB audio** flottants ; **Google Maps + itinéraire texte** + bouton « ouvrir dans Maps ».

## Audio
- **Baseline mobile** systématique : déblocage iOS (silent buffer) + **DynamicsCompressor** + **gain mobile boosté**, fondu sans clic, **OFF par défaut**, pause si onglet caché. Remplaçable par une piste client `<audio data-ambiance>`.

## Livraison / process
- **Montrer les changements avant commit** ; **stage sélectif** ; **ne pas pousser sans validation** (sauf routine explicitement autorisée).
- **Déploiement = étape par étape** (surtout DNS/domaine custom → souvent action client).
- **Visualisation** = envoyer un **lien localhost / live**, pas des captures (les captures = pour ma QA).
- **Avertir des risques** plateforme/technique **avant** d'agir, proposer la voie conforme.
- **Vérifier avant d'affirmer** (prix, règles plateformes) : tester/sourcer.
- **Réponses courtes** : direct, prochaine étape, sans remplissage.

## Sécurité
- Secrets uniquement dans `secrets/*.env` (gitignorés), **jamais** affichés ni commités. Clé secrète paiement **jamais** côté client.

- **2026-06-25 — RÈGLE D'OR (Mongazi) : CHAQUE SITE TOTALEMENT UNIQUE.** Deux sites NEBULA ne doivent
  **jamais se ressembler**, dans leur **entièreté** — pas seulement la couleur. Varier délibérément à chaque
  nouveau client : **disposition de la galerie / des images** (jamais la même grille ; ici Djambar = mosaïque
  bento à tailles variées, ailleurs masonry, colonnes, carrousel, plein-écran…), **tailles d'images non
  uniformes**, structure et ORDRE des sections, type de héros, grilles (asymétrie), système de motion,
  rythme typographique. Le socle partagé sert de moteur technique, **pas** de gabarit visuel : on le
  ré-agence et on change la présentation. Avant de livrer, se demander : « si je mets ce site à côté du
  précédent, se ressemblent-ils ? » Si oui → retravailler la composition jusqu'à ce que non.
