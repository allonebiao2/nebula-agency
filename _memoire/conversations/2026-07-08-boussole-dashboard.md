# 2026-07-08 — Boussole : tableau de bord bento multi-périodes

## Contexte
Reprise de Boussole (outil de gestion financière du commerçant, 3 enveloppes, FCFA). Mongazi a fourni 3 maquettes de dashboards dans `_partage/` (template dashboard ambre « salle de contrôle », dashboard design violet néon « Solo Leveling », HR Dashboard violet dense) et demandé, via `/ui-ux-pro-max` (effort max) : « inspire-toi, copie et adapte, améliore drastiquement le tableau de bord ».

## Décisions (réponses aux 4 questions)
- **Ambiance** : garder l'**ambre/orange sur charbon** (déjà validé le 08/07), pousser le glow/densité/jauges (image 1, la plus « finance »).
- **Pièce maîtresse** : grande **courbe incandescente CA + Bénéfice**.
- **Panneaux ajoutés** : classement produits · objectif du mois (XP) · donut 3 enveloppes · filtres par période — **+ demande explicite** : voir l'évolution sur **toutes les granularités** (heure/jour/semaine/mois/année), **comparaison**, chiffres en couleurs, et d'autres donuts.
- **Densité** : dense sur PC, épuré sur mobile.

## Livré (`?v=20260708b`)
- **Moteur multi-périodes** (`store.js`) : `periodInfo(gran, offset)` (jour=24 h · semaine=7 j · mois=jours · année=12 mois) + `serieDashboard()` (buckets + totaux + **comparaison période précédente** + enveloppes) + `topProduitsPeriode()` (classement + sparkline par produit) + objectif (`getObjectif`/`setObjectif`, stocké dans `profil.objectif_benefice`). **Charges fixes réparties au prorata** des jours (`chargesProrataEntre`), sans compter le futur → bénéfice cohérent à toutes les échelles.
- **Graphes** (`charts.js`) : `chartHero` (aire ambre CA + ligne émeraude Bénéfice, points/labels lumineux), `chartDonut` (multi-segments, glow, centre géré en HTML), `sparklineRaw` (valeurs brutes) ; `chartBeneficeMensuel` accepte `{showValues}` (barres allégées quand >12 buckets).
- **UI** (`ui.js`) : `viewAccueilHTML(period)` refait en **bento** — barre de période (chips Jour/Semaine/Mois/Année + nav ‹ ›), hero CA+Bénéfice, 5 KPIs colorés à delta+sparkline, objectif XP (anneau + flamme), 2 donuts légendés (« Où va ton argent » + « Ventes par produit »), classement produits, barres bénéfice, 3 anneaux, conseil. Helpers `deltaBadge`, `kpiHTML`, `periodBarHTML`. Icônes `trophy`+`flame` ajoutées.
- **Câblage** (`app.js`) : état `period` persisté (`boussole:period`, gran seulement, offset remis à 0), actions `set-gran`/`period-prev`/`period-next`/`edit-objectif`/`save-objectif`, `refreshDash()` (rafraîchit sans reset du scroll), modale objectif.
- **CSS** (`app.css`) : bloc « tableau de bord » (grille bento 12 colonnes ≥1080, 2 col ≥640, 1 col mobile ; chips, KPIs, donuts+légende, objectif, classement, 3 anneaux). Cartes = réutilisation de `.panel`.

## QC
- `node --check` OK sur les 6 modules.
- Boot Chrome headless réel (données seedées « Chez Ada » : 4 produits, 2 charges, ~200 ventes sur 78 j) : **10 cartes, 9 graphes, 2 donuts, 5 KPIs, 0 icône manquante, 0 erreur, 0 débordement horizontal** sur les 4 granularités ; captures **sombre + clair × mobile 430 + PC 1280** validées visuellement (rend exactement l'esprit des maquettes).
- Vraie appli via `_demo.html` (seed → `index.html`) : dashboard rendu, câblage OK.

## Points ouverts
- **Comparaison** : compare le mois EN COURS (partiel) au mois PRÉCÉDENT COMPLET → « -73 % » alarmant en début de mois. À rendre équitable (mois-à-date vs mêmes jours du mois précédent) — proposé, en attente d'accord.
- Reste (inchangé) : brancher Supabase, déployer Cloudflare Pages, nom définitif, icônes PNG.

## Git
- `_perso/` (GENÈSE, sensible) ajouté au `.gitignore` (n'était PAS ignoré → risque d'exposition évité). `boussole/_*.html` (démo/QC) et `clients/*/_diag.html` ignorés aussi.
- Commit + push « tout » demandé par Mongazi (Boussole + livrables clients + site agence + _partage + fitora + studio).
