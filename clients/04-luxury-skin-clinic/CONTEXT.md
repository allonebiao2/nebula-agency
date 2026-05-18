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
- **33 produits** : 24 fiches complètes (desc, actifs, résultats, INCI, avertissements)
  + 9 nouveaux produits (7 Capillaires, 1 Huile corps, 1 Crème visage) en fiches
  à compléter (prix « à définir », description « à venir », badge « À compléter »).
- **Photos produits réelles** intégrées en base64 (33/33).
- Sous-catégories encore sans produit : Corps (Beauty Bar, Crème corps) →
  état « Bientôt disponible ».

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
- [x] ina-luxury.html — 24 produits, nav 4 niveaux, panier
- [x] luxury-skin-clinic.html — 11 soins, design clinique, règlement, formulaires
- [x] cozy.html — 8 produits, design rose, panier
- [x] Logos intégrés : INA Luxury (logo CSS), Cozy, Luxury Skin Clinic, Luxury Club 229 (hub)
- [x] Photos produits réelles en base64 (INA Luxury 33/33 · Cozy 8/8)
- [ ] Liens Instagram / TikTok réels
- [ ] Validation des 4 contenus rédigés par défaut (voir ci-dessous)
- [ ] Compléter les 11 fiches « nouveaux produits » (prix, description, INCI)
- [ ] Responsive testé sur appareils réels
- [ ] Livré

## À valider / remplacer avant livraison

- **Contenus rédigés par défaut** (le brief renvoyait à « le document » non fourni) :
  règlement clinique, questionnaire Consultation Peau, questionnaire Diagnostic
  Capillaire, 8 étapes du Soin Glass Skin. → à valider avec Gloria.
- Prix manquant : « Rose Hydra Crème » affichée « Prix sur demande ».
- Réseaux sociaux (Instagram / TikTok).
- **11 nouveaux produits à compléter** (image OK, prix/desc « à définir ») :
  - INA Luxury — Capillaires : Shampoing Sensicare · Après-Shampoing Sensicare ·
    Masque Fortifiant K10 · Sérum Anagen · Sérum Hydratant · Beurre Clarté · Huile Soin 2-en-1
  - INA Luxury — Corps : Huile à la Rose · Visage : Crème au Lait de Chèvre
  - Cozy : Baume Pailleté (Nuit Scintillante) · Le Boost Fermeté
- Image `CONSULTATION PEAU` classée dans `assets/images/clinic/` — non intégrée :
  les fiches soin de la clinique n'ont pas d'emplacement photo (décision design à prendre).

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
  WhatsApp `2290167975626` conservé. Vague 2 à venir : descriptions enrichies,
  panneau catalogue latéral, animations, style clinique, audit mobile.

## Liens

- Pages : `index.html`, `ina-luxury.html`, `luxury-skin-clinic.html`, `cozy.html`
- Assets : `assets/` · Infos client : `assets/docs/gloria-infos.md`
- URL en ligne : —
