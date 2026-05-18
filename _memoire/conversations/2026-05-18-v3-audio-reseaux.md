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

## 4. Reste à faire (vague 2)
- Correction 4 — descriptions produits enrichies + 2 accordéons (En savoir plus / Ingrédients)
- Correction 5 — panneau catalogue latéral complet (architecture 3 marques)
- Correction 6 — animations maximales (hover 3D, ripple, fly-to-cart, etc.)
- Correction 7 — Luxury Skin Clinic style clinique renforcé
- Correction 8 — audit mobile (3 cards hub, tap 44px, swipe)
