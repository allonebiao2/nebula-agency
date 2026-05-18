# Session — Luxury Club 229 v3, vague 1 (cliente 04 · Gloria)

## Date : 18 Mai 2026
## Sujet : Corrections v3 — audio, réseaux sociaux, textes d'accueil

---

## 1. Contexte

Brief « Mission critique v3 » de Mongazi : 8 corrections sur les 4 pages.
Vague 1 traitée ici = les 3 priorités concrètes (audio, réseaux, textes).

## 2. Fait dans cette vague

### Correction 1 — Audio (PRIORITÉ MAX)
- Module unifié `LCAudio` (Web Audio API, zéro dépendance) injecté sur les 4 pages.
- Effets : brandClick, hover, addCart, menuOpen/Close, filter, whatsapp, chordOk, tap.
- Musique d'ambiance jazz douce continue (~12% gain, lowpass 950Hz, fondu 4s).
- Déblocage de l'AudioContext au premier geste (click/touch/keydown).
- Câblage par **délégation d'événements** → aucun listener à modifier page par page.
- Ancien code audio neutralisé : bouton `#audio-btn` masqué en CSS (code inerte).
- Bouton mute/unmute animé (égaliseur) en bas à droite.

### Correction 2 — Réseaux sociaux
- Barre fixe `lc-social` (bas, centrée, z-index 500) sur les 4 pages :
  WhatsApp + Instagram + TikTok, visibles sans scroll.
- Pulse doré continu, tooltip au survol, son au clic.
- Liens réels : IG `instagram.com/inaluxury`, TikTok `tiktok.com/@inaluxury`.
- WhatsApp : `2290167975626` CONSERVÉ (le format `22967975626` du brief était
  l'ancien format 8 chiffres, abandonné depuis 2023 — confirmé avec Mongazi).

### Correction 3 — Textes d'accueil
- Réécrits courts (2 lignes), écriture lettre par lettre à 36 ms.
- Hub, INA Luxury, Clinic, Cozy : nouveaux textes chauds et directifs.

## 3. Fichiers touchés
`index.html`, `ina-luxury.html`, `cozy.html`, `luxury-skin-clinic.html`.

## 4. Vague 2 — faite

### Correction 4 — Fiches produits enrichies
- Résultats clés visibles sur la carte (3 max).
- Deux accordéons distincts : « En savoir plus » et « Ingrédients ».
- Actifs clés surlignés en or dans la liste INCI.
- Bug corrigé : carte Cozy « todo » sans `data-add` (crash évité).

### Correction 5 — Panneau catalogue 3 marques
- Accordéon catalogue d'INA Luxury enrichi : compteurs de produits par
  catégorie/sous-catégorie + sections « Luxury Skin Clinic » et « Cozy »
  (liens sortants accordéon vers les autres pages).

### Correction 6 — Animations
- Hover cartes : élévation + ombre + liseré or/rose, zoom image.
- Effet ripple doré au clic sur les cartes (toutes les pages).
- Rebond du compteur panier à chaque ajout.
- Pulse vert continu sur les CTA WhatsApp.

### Correction 7 — Luxury Skin Clinic
- Design clinique déjà conforme (blanc + or, badge Sabrina, protocoles, RDV).
- Polish : pulse « timer » sur l'alerte RDV 24h, hover sur les boutons.

### Correction 8 — Mobile
- 3 cards hub sur même ligne : déjà OK (`flex-wrap:nowrap`).
- Réseaux/mute : 44px (zone tap conforme).
- Swipe vers la gauche pour fermer le catalogue ajouté.

## 5. Méthode
Travail en vagues testées (syntaxe JS validée à chaque étape). Audio testable :
le son se débloque au 1er clic, la musique démarre, le bouton mute (bas droite) la coupe.
