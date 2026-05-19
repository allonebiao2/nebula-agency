# Audit conversion — Luxury Club 229

## Date : 2026-05-19
## Contexte
Pas de flux d'inscription sur le site (vitrines catalogue). Audit des vrais
parcours de conversion avec les principes signup/form-CRO.

## FLUX A — Panier → WhatsApp (INA Luxury & Cozy)
Sain dans l'ensemble (panier persistant, total auto, message structuré).
Corrections :
- Vignette photo produit dans le panier (au lieu de l'initiale).
- Boutons quantité agrandis (cible tactile mobile).
- Bouton « Vider le panier ».
- Ligne « zone de livraison » dans le message WhatsApp.

## FLUX B — Questionnaires clinique (friction majeure)
Consultation Peau = 25 champs / 10 sections en une seule modale → abandon.
Corrections :
- Parcours **multi-étapes** (1 section / écran) + barre de progression.
- Validation **inline** (plus d'`alert()`), radios requis vérifiés.
- Sauvegarde des réponses en `localStorage`.
- Note : réduire le NOMBRE de questions est une décision de contenu (Gloria) —
  le multi-étapes rend le formulaire supportable sans rien supprimer.

## FLUX C — Modal règlement
Règlement obligatoire à chaque réservation → afficher 1×/session (`sessionStorage`).

## Suite
Toutes les corrections structurelles/UX appliquées le 2026-05-19
(voir journal du jour). La réduction du nombre de questions reste à valider
avec Gloria.
