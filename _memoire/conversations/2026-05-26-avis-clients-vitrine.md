# Luxury Club 229 — Système d'avis clients + bio en section

## Date : 2026-05-26 (session 2)

## Contexte

Gloria veut optimiser sa vitrine pour favoriser l'interaction client et
renforcer la crédibilité. Trois demandes claires :

1. **Réorganisation visuelle** : déplacer « univers » et « biographie »
   vers le haut, libérer le bas pour une nouvelle section interactive.
   La biographie reste telle quelle (pas de photos en plus).
2. **Espace avis clients** intitulé « Cliquez ici pour laisser vos avis » :
   - Nom/prénom + commentaire
   - Notation étoiles, idéalement sous chaque produit spécifique
   - Affichage des témoignages existants (Gloria les enregistre elle-même)
3. **Transparence** : pas de rendu « fake » tout-positif. Authenticité
   totale, avis partiels et constructifs bienvenus.

## Travail effectué (3 vagues, 3 commits)

### Vague 1 — `index.html` réorganisé (commit `695a20a`)
- Bio sortie du modal flottant, placée en section visible juste sous les
  3 univers
- Page hub désormais scrollable : top fold = logo + welcome + 3 univers,
  scroll → bio → (espace pour avis) → footer
- Suppression du bouton FAB « Biographie · Mme Sabrina » et du modal
  (devenu redondant)
- IntersectionObserver pour fade-in de la bio + de la section avis
  au scroll

### Vague 2 — Section Avis clients (commit `7347b4b`)
- HTML : titre demandé exact + intro de transparence + synthèse moyenne
  + filtres par catégorie + liste des avis + formulaire complet
- Formulaire : nom, catégorie (INA / Skin Clinic / Cozy / Autre),
  précision optionnelle, étoiles cliquables (radiogroup accessible),
  texte 600 caractères avec compteur
- Validation cliente avec messages d'erreur par champ
- **Soumission via WhatsApp** : ouvre `wa.me/2290167975626` avec
  message pré-rempli (nom, cible, étoiles, commentaire). Gloria
  reçoit, vérifie, ajoute l'avis approuvé au tableau `REVIEWS` du
  HTML manuellement.
- Toast de confirmation après envoi + reset du formulaire
- Tableau `REVIEWS` vide initialement, format commenté pour Gloria

### Vague 3 — Étoiles produits `ina-luxury.html` (commit `07fd92c`)
- Widget mini sous chaque carte produit : moyenne + nombre d'avis
  (si données présentes) OU « Soyez la 1ʳᵉ personne à donner un avis »
- Bouton WhatsApp pré-rempli avec le nom du produit
- Tableau `REVIEWS_INA` mapping produit→avis, peuplé progressivement
  par Gloria

## Choix d'architecture clé

**Pas de backend** pour les avis. La modération passe par WhatsApp
(canal déjà utilisé par Gloria) et les avis approuvés vivent dans des
tableaux JS commentés dans le HTML.

**Avantages** :
- Coût zéro (pas de Supabase, pas de n8n dédié, pas de Cloud)
- Modération native : Gloria décide ce qui sort
- Authenticité préservée : pas de soumission spam, pas de fake reviews
- Workflow déjà connu de Gloria (WhatsApp)

**Trade-off accepté** : Gloria doit ajouter manuellement les avis
validés dans `REVIEWS` / `REVIEWS_INA`. Pas grave tant que le volume
reste artisanal (10-30 avis / mois). Si ça scale, on migrera vers
Supabase ou un static-site CMS.

## Apprentissages techniques

- **IntersectionObserver pour reveal au scroll** : pattern compact
  (`rootMargin:'0px 0px -10% 0px', threshold:.05`) avec fallback
  immédiat si pas supporté. Idéal pour une bio + section avis qui
  apparaissent en glissant quand l'utilisateur descend.
- **Sortir du modal** : on peut conserver les classes CSS internes
  (`.bio-eyebrow`, `.bio-name`, `.bio-flourish`, etc.) en supprimant
  juste le wrapper `.bio-modal`/`.bio-card`. Économie de réécriture.
- **Étoiles input accessibles** : 5 `<button>` avec
  `role="radio"` + `aria-checked` + label SVG `★`. Hover state propage
  via JS (`btns.forEach toggle hover class`).
- **Génération de message WhatsApp** : `encodeURIComponent(msg)` sur
  un template avec `\n` natifs (pas `<br>`), `wa.me/<numéro>?text=`.
  WhatsApp respecte les sauts de ligne et formate gras avec `*texte*`.

## À demander à Gloria

- 3-4 avis authentiques pour amorcer (pas obligé tous positifs)
- Validation du wording de transparence (« Nous publions tous les
  retours authentiques — positifs comme constructifs »)
- Comment recevoir les avis : sur le numéro `67975626` actuel ou
  un canal dédié ?
