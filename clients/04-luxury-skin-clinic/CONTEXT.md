# CONTEXT — LUXURY CLUB 229 (Ahouangnimon Gloria)

> Dossier client : `clients/04-luxury-skin-clinic/`
> Nom officiel du projet : **LUXURY CLUB 229** (anciennement « Luxury Skin Clinic »,
> qui est désormais le nom de l'une des 3 marques).

## Identité

- **Nom du projet** : LUXURY CLUB 229
- **Cliente** : Ahouangnimon Gloria
- **Secteur** : clinique esthétique de luxe, cosmétiques, bien-être
- **Ville** : Cotonou, Bénin
- **WhatsApp** : +229 0167975626 ⚠️ INTOUCHABLE (`2290167975626`)
- **Spécialiste institut** : Mme Sabrina, esthéticienne diplômée
- **Palette** : Blanc nacré · Or `#C9A84C` · Noir profond `#0a0a0a`

## Structure du projet — hub + 3 marques

| Fichier | Rôle | Design |
|---|---|---|
| `index.html` | Hub LUXURY CLUB 229 (+ bouton flottant **Biographie Mme Sabrina** → modal) | Noir & or, luxe |
| `ina-luxury.html` | Catalogue cosmétiques & capillaires | Noir & or |
| `luxury-skin-clinic.html` | Soins & prestations en institut | Blanc clinique + or + menthe |
| `cozy.html` | Hygiène intime & bien-être | Rose poudré + or + blanc |

## Architecture des 3 marques (brief v2 — 2026-05-18)

### INA Luxury — catalogue, navigation + routines préétablies
Catégorie → Sous-catégorie → Produits, **OU** Catégorie → Routine préétablie (clés en main).
Panier multi-produits. Le filtre par préoccupation a été remplacé par **4 routines Visage**
(Hydra · Acné · Éclat/Pigmentation · Boosters) et **2 routines Corps** (Luxury · Skin),
toutes structurées en tiers **Luxury (médicale) en haut + Skin (semi-médicale) en dessous**.
- **Visage** : Gel Nettoyants · Sérums · Crèmes · Masques
- **Corps** : Beauty Bar · Crème corps · Gommage · Huile corps
- **Capillaires** : Shampoing · Après-shampoing · Masque · Sérum · Huile / Beurre
- **Enfant (0-16 ans)** : Gel Lavant · Crème · Crème Lavante
- **39 produits** : 29 fiches complètes (desc, actifs, résultats, INCI, avertissements)
  + 10 nouveaux produits en fiches à compléter (prix « à définir » ou description
  « à venir »). Inclut **INA Luxury Body Butter Baiser Nocturne** (7 000 F / 100ml)
  migré depuis Cozy le 2026-05-24 (l'étiquette officielle est INA LUXURY BODY BUTTER).
- **Corps** entièrement peuplé : Beauty Bar 3 · Crème corps 2 · Gommage 1 · Huile corps 2.
- **Photos produits réelles** en base64 : 34 produits illustrés (Huile Éclat Suprême
  ré-ajoutée le 2026-05-24) ; 2 Beauty Bars (Kojic, Milk) sans photo encore (placeholder
  dégradé en attendant). Toutes les images normalisées en **600×800 (3:4), fond blanc,
  JPEG q78** — même canvas, produits centrés, échelle visuelle homogène dans la grille.

### Luxury Skin Clinic — 11 soins & prestations
Design clinique distinct. Soins groupés Visage / Corps / Capillaires / Soin complet.
- Consultation Peau gratuite + Suivi · Soin Oxygène · Soin Glass Skin · Luxury Peel ·
  Gommage Luxury · Luxury Massage · Diagnostic Capillaire · Hair Spa ·
  Soin Activateur de Pousse · Soin Complet VIP.
- Règlement clinique obligatoire (modal « J'AI COMPRIS ✓ ») avant toute réservation.
- Alerte RDV 24h sur chaque soin · acompte 5 000 F · badges « Réalisé par Mme Sabrina ».
- 1 questionnaire intégré (Consultation Peau gratuite) → envoi WhatsApp.
- **Diagnostic Capillaire** (5 000 F, payant) : description brève + bouton
  « Remplir le formulaire » → redirection WhatsApp avec message adapté
  (paiement-via-WhatsApp tant que FedaPay n'est pas branché). Le questionnaire
  capillaire complet (`HAIR_FORM`) reste dans le code, réactivable dès l'intégration
  paiement.

### Cozy — 6 produits
Design rose poudré sensuel. Filtres par catégorie (Intime / Corps / Bien-être).
Panier multi-produits. Avertissement spécifique sur la Maca Cream (résultats progressifs).
7 produits complets — dont **Le Boost Fermeté** (Booster Drink Sublimes, 15 000 F / 150g),
**Baume Pailleté Nuit Scintillante** (9 000 F), tous deux validés le 2026-05-24, et
**Body Butter Baiser Nocturne** (7 000 F / 100ml) — initialement migré vers INA Luxury
le 2026-05-24, **ré-intégré dans Cozy le 2026-05-26** sur décision Gloria (le produit
appartient à la marque Cozy, l'étiquette « INA LUXURY BODY BUTTER » sur le pot est un
ancien packaging).
Photos produits réelles intégrées en base64 (6/6), normalisées au même canvas que
INA Luxury (**600×800, 3:4, fond blanc, JPEG q78**).

## Fonctionnalités transverses

- **Panier multi-produits** sur INA Luxury et Cozy (persistant via localStorage,
  total auto, commande groupée WhatsApp).
- **Préoccupations** affichées en badges sur chaque carte (cliquables pour filtrer sur INA Luxury).
- **Guidance** : encarts « consultation gratuite », « contacter Mme Sabrina », badges Bestseller.
- **Gestion de stock** : code prêt (badges « Plus que X » / « Rupture ») — tout en stock pour l'instant.
- **Audio** : ambiance douce générée via Web Audio API (règle NEBULA zéro CDN externe).
- Écran d'accueil animé par marque (texte d'accueil typé) · curseur personnalisé · hub :
  3 cards sur la même ligne en mobile, son cristal + zoom à l'entrée.

## Détail des contenus

- Liste complète produits / soins / prix : voir `assets/docs/gloria-infos.md`.
- Données sources : tableaux `PRODUCTS` / `SERVICES` dans chaque fichier HTML.

## Contraintes

- **Budget** : 100 000 FCFA setup + 10 000 FCFA/mois.
- **Hébergement** : Netlify (`index.html` = page d'accueil) — `https://luxuryskinclinic.netlify.app/`.
- **Technique** : HTML pur, CSS inline, JS vanilla, zéro framework, zéro CDN externe.
- **Images** : fichiers JPG/PNG externes dans `assets/images/` (lazy-loadés
  sur les templates produits) — **plus de base64 dans les pages** depuis le
  2026-05-25 (gain cumulé −78 % de poids HTML). Les chemins restent 100 %
  relatifs/Netlify, conformes à la règle « zéro CDN externe ».
- WhatsApp de Gloria : ne jamais modifier sans confirmation.

## État d'avancement

- [x] Brief v2 reçu et intégré
- [x] index.html — hub Luxury Club 229
- [x] ina-luxury.html — 35 produits, nav 4 niveaux, panier
- [x] luxury-skin-clinic.html — 11 soins, design clinique, règlement, formulaires
- [x] cozy.html — 8 produits, design rose, panier
- [x] Logos intégrés : INA Luxury (logo CSS), Cozy, Luxury Skin Clinic, Luxury Club 229 (hub)
- [x] Photos produits réelles en `assets/images/` (INA Luxury 35/35 · Cozy 6/6),
  lazy-loadées
- [x] Audit complet vitrine + correctifs UX (validation ville livraison,
  null-checks, confirm vider panier, méta sociales complètes) — 2026-05-25
- [x] Métadonnées sociales (og:title/description/image/url + twitter:card +
  canonical) sur les 4 pages — 2026-05-25
- [x] 4 images Open Graph générées (1200×630, charte respectée, < 50 KB
  chacune) dans `assets/images/og-*.jpg` — 2026-05-25
- [x] Allègement HTML (extraction base64 → fichiers + lazy loading) :
  2547 KB → 548 KB cumulé sur les 4 pages (−78 %) — 2026-05-25
- [x] Lien Instagram réel intégré sur les 4 pages (`@luxuryclub229`, cross-marque)
- [ ] Lien TikTok réel à confirmer (actuellement `@inaluxury`)
- [ ] Validation des 4 contenus rédigés par défaut (voir ci-dessous)
- [ ] Compléter les 10 fiches « nouveaux produits » restantes (prix, description, INCI) —
  inclut les 3 produits cités dans les briefs routines (Crème Pré-Nettoyante,
  Rose Solution Micellaire, Concentré Fruité)
- [ ] Photos des 2 Beauty Bars (Kojic, Milk)
- [ ] Responsive testé sur appareils réels
- [ ] Livré

## À valider / remplacer avant livraison

- **Contenus rédigés par défaut** (le brief renvoyait à « le document » non fourni) :
  règlement clinique, questionnaire Consultation Peau, questionnaire Diagnostic
  Capillaire, 8 étapes du Soin Glass Skin. → à valider avec Gloria.
- Réseaux sociaux (Instagram / TikTok).
- **Nouveaux produits à compléter** (prix/desc « à définir ») — Rose Purifiant Sérum
  (visage/sérums, gamme Skin, ajout 2026-05-26) · Crème Pré-Nettoyante (visage/crèmes,
  Luxury) · Rose Solution Micellaire (visage/gel-nettoyants, Skin) · les 6 produits
  capillaires INA Luxury en rupture · Kojic & Milk Beauty Bars (corps, sans photo).
- ✅ **Concentré Fruité** complété le 2026-05-26 : 15 000 F · 100 ml · catégorie
  corrigée `huile-corps` → `gommage` · description complète Acide Lactique 5% +
  Willow Bark · photo intégrée (`assets/images/ina-luxury/corps/gommage/concentre-fruite.jpg`).
- Image `CONSULTATION PEAU` classée dans `assets/images/clinic/` — non intégrée :
  les fiches soin de la clinique ont désormais une bannière visuelle SVG (voir ci-dessous),
  mais pas d'emplacement photo réelle. Décision à prendre si on veut y mettre des photos.

## Visuels des soins (Luxury Skin Clinic)

Chaque fiche soin a une bannière illustrée : 4 visuels line-art dorés générés en SVG
(Visage · Corps · Capillaires · Soin complet/VIP), inline dans `luxury-skin-clinic.html`.
100 % libre de droit, zéro CDN, zéro fichier externe. Modifiables directement dans le
code (objet `SVC_ART`). Voie B (vraies photos via `_inbox/`) reste possible plus tard.

## Décisions importantes

- 2026-05-16 — Projet structuré en hub + 3 marques (4 pages HTML).
- 2026-05-17 — Architecture des sous-catégories des 3 marques confirmée et intégrée.
- 2026-05-18 — Brief v2 : projet renommé **LUXURY CLUB 229** ; « Luxury Skin Clinic »
  devient le nom de la marque institut.
- 2026-05-18 — INA Luxury passe à 4 catégories (ajout Enfant 0-16 ans) et 24 produits réels.
- 2026-05-18 — Ajout d'un système de panier multi-produits (INA Luxury + Cozy).
- 2026-05-18 — Luxury Skin Clinic : design clinique distinct (blanc dominant), règlement
  obligatoire avant réservation, questionnaires intégrés.
- 2026-05-18 — Musique : ambiance Web Audio API retenue (le jazz nécessiterait un MP3
  externe, contraire à la règle « zéro CDN »).
- 2026-05-18 — Contenus non fournis (« le document ») rédigés en versions pro par défaut,
  marqués « à valider ».
- 2026-05-18 — Capillaires : sous-catégories fixées à 5 (Shampoing · Après-shampoing ·
  Masque · Sérum · Huile / Beurre). Dossier assets `huile` renommé `huile-beurre`.
- 2026-05-18 — Dispatch des 45 images de `_inbox` : 41 photos produits + 3 logos
  intégrés en base64 (compressées ~640px, JPEG/PNG optimisés), 1 image classée.
  INA Luxury passe à 33 produits, Cozy à 8. Logo INA Luxury fait en CSS (texte noir
  sur blanc, serif espacé) ; logos Cozy / Clinic / Hub en images base64.
- 2026-05-18 — v3 vague 1 : module audio unifié `LCAudio` (Web Audio API, effets +
  musique jazz douce, déblocage au 1er clic) sur les 4 pages ; barre réseaux sociaux
  fixe (WhatsApp/Instagram/TikTok) ; textes d'accueil courts (36 ms/lettre).
  WhatsApp `2290167975626` conservé.
- 2026-05-18 — v3 vague 2 : fiches produits enrichies (résultats visibles, 2 accordéons
  En savoir plus / Ingrédients, actifs INCI surlignés) ; panneau catalogue 3 marques
  avec compteurs ; animations (hover 3D, ripple doré, rebond panier, pulse WhatsApp) ;
  polish clinique ; audit mobile (swipe catalogue). v3 complète sur les 4 pages.
- 2026-05-19 — Correction d'architecture par Gloria : Busserole Beauty Bar déplacée
  de Visage/Nettoyants vers Corps/Beauty Bar ; ajout de Kojic Beauty Bar et Milk
  Beauty Bar (Corps/Beauty Bar) ; Crème au Lait de Chèvre et Beurre Clarté déplacées
  vers Corps/Crème corps ; Huile à la Rose confirmée en Corps/Huile corps. INA Luxury
  passe à 35 produits, toutes les sous-catégories Corps sont peuplées. Prix de
  « Rose Hydra Crème » fixé à 7 000 FCFA. Cozy : Huile Éclat Suprême déjà en Corps
  (pas de rayon « huile » distinct dans Cozy) — inchangé.
- 2026-05-19 — Corrections critiques : splash screen sur les 4 pages (logo Luxury
  Group + bouton « Entrer dans l'univers » → déblocage audio mobile garanti par un
  geste explicite, flag `sessionStorage`) ; emblèmes du hub en texte stylisé CSS
  (les dossiers `assets/images/logo/<marque>/` sont vides) ; volume musique plus
  présent sur mobile que desktop ; accordéons « En savoir plus » garantis sans
  clipping (max-height:none une fois ouverts) ; préoccupations plafonnées à 2-3
  badges + « +X autres » cliquable. Qualité images : hints CSS ajoutés — les
  originaux ayant été compressés le 18/05 (640px), la résolution native n'est pas
  récupérable sans re-fourniture des photos dans `_inbox/`.
- 2026-05-19 — Capillaires : prix fixés (Shampoing · Après-Shampoing · Sérum
  Hydratant = 8 000 F · Masque K10 = 10 000 F · Sérum Anagen = 20 000 F · Huile
  Soin 2-en-1 = 9 000 F). Les 6 produits capillaires sont en **rupture de stock**
  (badge rouge « Rupture de stock », bouton « M'avertir du retour » via WhatsApp).
  Hub : ancienne barre réseaux statique supprimée, seule la barre animée
  `lc-social` est conservée.
- 2026-05-19 — Audit conversion : panier enrichi (vignette photo, boutons
  quantité tactiles, « Vider le panier », zone de livraison dans le message
  WhatsApp) ; questionnaires clinique refondus en parcours **multi-étapes**
  (barre de progression, validation inline, sauvegarde `localStorage`). La
  réduction du nombre de questions reste une décision de contenu pour Gloria.
- 2026-05-24 — Brief Gloria : remplacement du **filtre par préoccupation** par
  **« Routine préétablie »** sur INA Luxury. 4 routines Visage (Hydra · Acné ·
  Éclat/Pigmentation · Boosters) et 2 routines Corps (Luxury · Skin). Chaque
  routine est structurée en tiers : Luxury (gamme médicale) en haut, Skin
  (gamme semi-médicale, plus abordable) en dessous. La routine Éclat/Pigmentation
  est exceptionnellement à 3 tiers (Luxury Pigment + Luxury Éclat + Skin).
  Les Boosters ne sont pas tier-divisés : un seul bloc (nettoyants & masques)
  destiné aux clients ayant suivi une routine de base ~3 mois. Les badges de
  préoccupations restent affichés sur les fiches produit (informationnels) mais
  ne déclenchent plus de filtrage. Ajout de 2 nouveaux produits placeholder cités
  dans le brief : **Crème Pré-Nettoyante** (Visage/Crèmes, Luxury) et
  **Rose Solution Micellaire** (Visage/Gel Nettoyants, Skin) — fiches « à compléter ».
- 2026-05-25 — **Audit complet + correctifs + allègement** (5 sessions, 7 commits).
  Domaine Netlify confirmé : `luxuryskinclinic.netlify.app`.
  - **4 bugs UX/conversion corrigés** : validation ville si livraison
    (cozy + ina-luxury), null-checks sur `#helpWa`/`#finalWa`, confirmation
    avant « Vider le panier », méta sociales URL-free.
  - **Métadonnées sociales complètes** sur les 4 pages : og:title /
    description / type / site_name / locale / url / image / image:width /
    image:height / image:alt + twitter:card / title / description / image +
    `<link rel=canonical>`. Permet aperçu visuel des liens partagés sur
    WhatsApp/Facebook/Instagram.
  - **4 images OG générées** via pipeline HTML → PNG (Edge headless) → JPG
    qualité 88 (System.Drawing PowerShell). Toutes < 50 KB, charte respectée
    pixel-perfect (Cormorant Garamond + or dégradé / rose poudré selon page).
    Sources HTML versionnées dans `assets/og-source/` pour régénération future.
  - **Allègement HTML** (extraction base64 → fichiers + `loading="lazy"`) :
    stratégie hash-first (SHA-256 binaire) puis slug-first puis extract.
    Total : 2547 KB → 548 KB sur les 4 pages (−78 %), chargement 3G estimé
    27 s → 6 s. Aucune perte de qualité (les disk JPGs en `assets/images/`
    étaient déjà les versions canoniques, on les utilise enfin).
  - **Cleanup** : `huile-eclat-supreme.jpg` déplacé de `cozy/corps/` vers
    `ina-luxury/corps/huile-corps/` (cross-référence à l'origine d'une
    migration produit). Body Butter Baiser Nocturne extrait du base64 vers
    `ina-luxury/corps/creme-corps/body-butter-baiser-nocturne.jpg`.
  - **Scripts versionnés** dans `/scripts/` (og-audit, og-allegement,
    og-smoke) — réutilisables pour les vitrines des autres clients.
- 2026-05-26 — **4 ajustements demandés par Gloria** sur la vitrine.
  - **Disponibilité Mme Sabrina** restreinte à mercredi/samedi « pour le
    moment » : bandeau RDV haut de page, ligne RDV sous chaque fiche soin
    (9 soins), point 1 du règlement clinique, et messages WhatsApp
    (VIP + standard) adaptés. Récap modal aussi (« Mercredi ou samedi — à
    confirmer avec la clinique »). 5 occurrences groupées, prêtes à élargir
    le jour où Sabrina aura plus de jours dispos.
  - **Confirmation de réservation enrichie** : après validation d'une
    *prestation*, le modal de remerciement affiche une carte adresse luxe
    doré (Akpakpa Suru Lere — Von en face poissonnerie Saint-Paul, 2ᵉ rue
    à droite, 1ʳᵉ maison à étage carrelée marron, 1ᵉʳ étage porte à gauche)
    avec 2 CTA dorés : `tel:+22967975626` (Appeler · 67 97 56 26) et
    Google Maps (recherche « Luxury Skin Clinic Cotonou »). Affichage
    conditionnel via `opts.thanks={text,address}` sur `lcConfirmOrder` —
    pas affichée pour les questionnaires diagnostic (à distance).
    Constantes centralisées : `LC_BOOK_THANKS` (texte typewriter) + bloc
    HTML statique de la carte (1 endroit à éditer).
  - **INA Luxury — Routines simplifiées** (Gloria : « le français là est
    déjà compliqué pour eux ») : intro raccourcie selon ses mots exacts —
    « Deux gammes disponibles : Luxury (gamme médicale) et Skin (gamme
    semi-médicale). La différence se situe au niveau de la concentration
    des actifs. Choisissez selon vos besoins et votre budget. ».
    Sous-titres des tiers Skin allégés (« plus abordable » retiré, 4 occ.).
    Adapté pour Visage et Corps.
  - **Correction Routine Acné — tier Skin** : remplacement de Serum Azelaic
    + Reti Rose Crème par **Rose Purifiant Sérum + Acné Control Crème**
    (correction d'erreur Gloria). Rose Purifiant Sérum ajouté comme nouveau
    produit Visage/Sérums marqué `todo:1, isnew:1` — prix, taille, photo,
    description complète à valider (placeholder pro fourni en attendant).
  - **Instagram unifié** : 7 occurrences (4 barres flottantes + 3 modales
    de remerciement) basculées de `@inaluxury` vers le compte cross-marque
    `@luxuryclub229`. Aria-labels mis à jour. TikTok inchangé.
- 2026-05-26 (4e vague) — **Pédagogie commande & instructions photos**.
  - **Consultation Peau gratuite** : ajout d'une ligne pédagogique dans le
    récap de confirmation du questionnaire. Pour le formulaire Peau :
    « 📸 Photos requises — Veuillez joindre des photos nettes des différentes
    faces de votre visage **après avoir envoyé votre questionnaire**, pour
    une meilleure analyse de Mme Sabrina. » (variante hair pour le Diagnostic
    Capillaire conservée plus courte). `luxury-skin-clinic.html` ligne ~1322.
  - **Commande produits — bloc « Personnalisation de votre routine »** :
    après clic sur « Commander sur WhatsApp » dans le panier Cozy ou INA Luxury,
    le modal de confirmation affiche désormais un encart pédagogique (texte
    fourni par Gloria) + checkbox **« J'ai lu et compris, je valide ma
    commande »**. Le bouton « Valider ma commande → » est désactivé tant que
    la case n'est pas cochée. Pattern réutilisable via le nouveau paramètre
    `opts.acknowledge={text}` sur `lcConfirmOrder` — autres flux WhatsApp
    (Demande de prix, Alerte stock) restent inchangés. Charte : rose poudré
    pour Cozy, doré-cream pour INA Luxury.
- 2026-05-26 (3e vague) — **Simplifications Gloria** :
  - **Routine Savons supprimée** d'INA Luxury Corps : Gloria ne veut que 2 packs
    (Body Pack Luxury + Body Pack Skin). L'entrée `key:'savons'` retirée de
    `ROUTINES.corps`. Les 3 Beauty Bars (Kojic, Busserole, Milk) restent
    accessibles via Corps → Beauty Bar (catalogue normal). Intro routine corps
    reformulée : « Trois packs corps … » → « Deux packs corps disponibles … ».
  - **Option « Retrait sur place » supprimée** du panier (Cozy + INA Luxury) :
    seule la livraison est désormais proposée. Suppression du bloc HTML
    « Mode de réception », du helper JS `getRecv()`, du listener `syncDelivVisibility`,
    et des branches conditionnelles `(recv==='livraison')?...:...` dans les
    messages WhatsApp et le récap modal. Le bloc adresse de livraison est
    désormais toujours affiché et tous ses champs sont obligatoires. CSS orphan
    `.cart-recv*` et `.recv-pill*` également nettoyés (charte conservée pour
    `.cart-recv-lbl` qui reste utilisé par les autres labels du panier).
  - **Signature « Vitrine signée NEBULA Agency » retirée** des 4 pieds de page
    (Gloria : « pas trop professionnel »). Le `<div class="foot-sig">` supprimé
    sur `index.html`, `cozy.html`, `ina-luxury.html` et `luxury-skin-clinic.html`.
    Le `foot-meta` (Marque · Cotonou · Bénin) est conservé.
- 2026-05-26 (suite) — **Réorganisation catalogue corps + Concentré Fruité complété**.
  - **Body Butter Baiser Nocturne ré-intégré dans Cozy** : décision inverse du
    2026-05-24 (Gloria : « le produit appartient à Cozy, pas à INA Luxury »).
    Retiré de `ina-luxury.html` (PRODUCTS + IMG map). Ajouté dans `cozy.html`
    (`cat:'selfcare'`, 7 000 F / 100ml, fiche complète conservée). Image déplacée
    `ina-luxury/corps/creme-corps/body-butter-baiser-nocturne.jpg` →
    `cozy/corps/body-butter-baiser-nocturne.jpg`. Ancienne image obsolète
    `cozy/corps/creme-corps-parfumee.jpg` supprimée. Cohérence : hub `index.html`
    et clinique `luxury-skin-clinic.html` mis à jour
    (« Crème Corps Night Kiss » → « Body Butter Baiser Nocturne » dans le panneau
    Cozy SELFCARE).
  - **Concentré Fruité enrichi et reclassé** : sous-catégorie corrigée
    `huile-corps` → `gommage` (placement réel selon Gloria). Fiche complète
    fournie par Gloria : 15 000 F / 100 ml, description Acide Lactique 5% +
    Willow Bark Extract, résultats par phase (2-4 sem · 6-8 sem · 2-3 mois),
    conseils d'utilisation 1×/semaine, INCI complète. Photo PNG depuis
    `_inbox/` traitée via `scripts/og-defringe.ps1` → 600×800 JPEG q78
    (17 KB) dans `assets/images/ina-luxury/corps/gommage/`. PNG source
    archivé dans `_inbox/_processed/`. Le produit reste dans la routine
    Body Pack Luxury (`items:['Beurre Clarté','Huile Éclat Suprême','Concentré Fruité']`).

## Paiement en ligne — FedaPay (en préparation)

Objectif : permettre le paiement direct (Mobile Money / carte) sur les vitrines,
en complément de la commande WhatsApp.

- **Statut** : en attente de la vérification du compte FedaPay de Mongazi.
- **Architecture retenue** (conforme `CLAUDE.md`) :
  vitrine → webhook n8n (envoi du panier + montant) → n8n crée la transaction
  FedaPay avec la clé secrète `sk_live_*` (serveur uniquement) → renvoie l'URL de
  paiement FedaPay → la vitrine redirige le client vers la page sécurisée FedaPay.
- La clé secrète ne touche jamais le HTML ; pas de SDK CDN dans la vitrine.
- **À faire dès la vérification du compte** :
  1. Créer un sous-compte FedaPay pour Gloria (dashboard FedaPay).
  2. Construire le workflow n8n (création transaction → retour URL → webhook
     de confirmation de paiement → notification WhatsApp).
  3. Ajouter le bouton « Payer en ligne » dans le panier d'INA Luxury & Cozy
     (à côté de « Commander sur WhatsApp »).
  4. Tester un paiement réel de bout en bout avant mise en ligne.

## Évolutions demandées (à planifier)

- **Audit friction complet** (demandé le 2026-05-18, partiellement traité
  le 2026-05-25) : tunnel panier → WhatsApp validé et fluidifié, modal
  règlement obligatoire en place. Les 2 questionnaires clinique restent
  à auditer en profondeur (refonte multi-étapes déjà faite le 2026-05-19).
- Tester en prod sur mobile réel après le redeploy Netlify
  (https://luxuryskinclinic.netlify.app/).
- Valider les aperçus de partage social via
  https://developers.facebook.com/tools/debug/ (Scrape Again obligatoire).

## Liens

- Pages : `index.html`, `ina-luxury.html`, `luxury-skin-clinic.html`, `cozy.html`
- Assets : `assets/` · Infos client : `assets/docs/gloria-infos.md`
- **URL en ligne** : https://luxuryskinclinic.netlify.app/

## Performance (mesurée 2026-05-25)

| Page | Poids HTML | Chargement 3G estimé |
|---|---|---|
| index.html | 57 KB | < 1 s |
| luxury-skin-clinic.html | 152 KB | ~2 s |
| cozy.html | 108 KB | ~1 s |
| ina-luxury.html | 230 KB | ~2 s |

Images en lazy-loading : l'utilisateur ne télécharge que ce qu'il voit. Le
cache HTTP Netlify rend les re-visites quasi-instantanées.
