# CONVENTIONS NEBULA — standards non négociables

> Règles que le skill doit honorer systématiquement. Sources : `CLAUDE.md`, mémoire/feedback, exécution Djambar Team.

## Architecture & fichiers
- **Socle partagé** `assets/app.css` + `assets/app.js` (≠ pages auto-contenues lourdes). Ajouter un pôle = dupliquer 1 page légère.
- **Cache-bust** `?v=AAAAMMJJx` sur app.css/app.js → **bumper à chaque modif** du socle (sinon cache périmé : « tout cassé sur PC, OK mobile »).
- **Images** : chemins **relatifs** (`assets/images/…`) pour un **hub multi-pages déployé** (plus léger, cacheable, lazy-load).
  - Nuance vs règle « base64 » : le **base64** reste la règle pour les **vitrines mono-fichier**. Multi-pages = relatif assumé.
  - **Jamais** d'images en CDN Google Drive.
- Dossiers client : `clients/NN-slug/` avec `assets/{images,videos,docs}` + `CONTEXT.md`.

## Visuel / UX
- **Typo** : display **Cormorant** (serif) + body **sans distinctive** (Jost ; éviter Montserrat/Inter/Roboto « sur-utilisés »).
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
