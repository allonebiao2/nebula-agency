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
| `index.html` | Hub LUXURY CLUB 229 | Noir & or, luxe |
| `ina-luxury.html` | Catalogue cosmétiques & capillaires | Noir & or |
| `luxury-skin-clinic.html` | Soins & prestations en institut | Blanc clinique + or + menthe |
| `cozy.html` | Hygiène intime & bien-être | Rose poudré + or + blanc |

## Architecture des 3 marques (brief v2 — 2026-05-18)

### INA Luxury — catalogue, navigation 4 niveaux
Catégorie → Sous-catégorie → Préoccupation → Produits. Panier multi-produits.
- **Visage** : Gel Nettoyants · Sérums · Crèmes · Masques
- **Corps** : Beauty Bar · Crème corps · Gommage · Huile corps
- **Capillaires** : Shampoing · Après-shampoing · Masque · Sérum · Huile / Beurre
- **Enfant (0-16 ans)** : Gel Lavant · Crème Hydratante · Crème Apaisante · Crème Lavante
- **35 produits** : 24 fiches complètes (desc, actifs, résultats, INCI, avertissements)
  + 11 nouveaux produits en fiches à compléter (prix « à définir », description
  « à venir », badge « À compléter »).
- **Corps** entièrement peuplé : Beauty Bar 3 · Crème corps 2 · Gommage 1 · Huile corps 1.
- **Photos produits réelles** en base64 : 33 produits illustrés ; 2 Beauty Bars
  (Kojic, Milk) en attente de photo (placeholder dégradé en attendant).

### Luxury Skin Clinic — 11 soins & prestations
Design clinique distinct. Soins groupés Visage / Corps / Capillaires / Soin complet.
- Consultation Peau gratuite + Suivi · Soin Oxygène · Soin Glass Skin · Luxury Peel ·
  Gommage Luxury · Luxury Massage · Diagnostic Capillaire · Hair Spa ·
  Soin Activateur de Pousse · Soin Complet VIP.
- Règlement clinique obligatoire (modal « J'AI COMPRIS ✓ ») avant toute réservation.
- Alerte RDV 24h sur chaque soin · acompte 5 000 F · badges « Réalisé par Mme Sabrina ».
- 2 questionnaires intégrés (Consultation Peau, Diagnostic Capillaire) → envoi WhatsApp.

### Cozy — 8 produits
Design rose poudré sensuel. Filtres par catégorie (Intime / Corps / Bien-être).
Panier multi-produits. Avertissement spécifique sur la Maca Cream (résultats progressifs).
6 produits complets + 2 nouveaux (Baume Pailleté, Le Boost Fermeté) en fiches à compléter.
Photos produits réelles intégrées en base64 (8/8).

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
- **Hébergement** : Netlify (`index.html` = page d'accueil).
- **Technique** : HTML pur, CSS inline, JS vanilla, zéro framework, zéro CDN externe.
- **Images** : base64 — actuellement placeholders dégradés élégants.
- WhatsApp de Gloria : ne jamais modifier sans confirmation.

## État d'avancement

- [x] Brief v2 reçu et intégré
- [x] index.html — hub Luxury Club 229
- [x] ina-luxury.html — 35 produits, nav 4 niveaux, panier
- [x] luxury-skin-clinic.html — 11 soins, design clinique, règlement, formulaires
- [x] cozy.html — 8 produits, design rose, panier
- [x] Logos intégrés : INA Luxury (logo CSS), Cozy, Luxury Skin Clinic, Luxury Club 229 (hub)
- [x] Photos produits réelles en base64 (INA Luxury 33/33 · Cozy 8/8)
- [ ] Liens Instagram / TikTok réels
- [ ] Validation des 4 contenus rédigés par défaut (voir ci-dessous)
- [ ] Compléter les 13 fiches « nouveaux produits » (prix, description, INCI)
- [ ] Photos des 2 Beauty Bars (Kojic, Milk)
- [ ] Responsive testé sur appareils réels
- [ ] Livré

## À valider / remplacer avant livraison

- **Contenus rédigés par défaut** (le brief renvoyait à « le document » non fourni) :
  règlement clinique, questionnaire Consultation Peau, questionnaire Diagnostic
  Capillaire, 8 étapes du Soin Glass Skin. → à valider avec Gloria.
- Réseaux sociaux (Instagram / TikTok).
- **13 nouveaux produits à compléter** (prix/desc « à définir ») :
  - INA Luxury — Capillaires : Shampoing Sensicare · Après-Shampoing Sensicare ·
    Masque Fortifiant K10 · Sérum Anagen · Sérum Hydratant · Huile Soin 2-en-1
  - INA Luxury — Corps : Kojic Beauty Bar\* · Milk Beauty Bar\* · Crème au Lait de
    Chèvre · Beurre Clarté · Huile à la Rose
  - Cozy : Baume Pailleté (Nuit Scintillante) · Le Boost Fermeté
  - \* = sans photo (placeholder en attendant).
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

- **Audit friction complet** (demandé le 2026-05-18, à faire plus tard) :
  tunnel panier → WhatsApp + 2 questionnaires clinique + modal règlement
  obligatoire avant réservation.

## Liens

- Pages : `index.html`, `ina-luxury.html`, `luxury-skin-clinic.html`, `cozy.html`
- Assets : `assets/` · Infos client : `assets/docs/gloria-infos.md`
- URL en ligne : —
