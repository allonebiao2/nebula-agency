# Journal — 2026-06-20 — Correctif « contenu qui clignote et disparaît »

## Symptôme rapporté par Mongazi
Dans le back-office NEBULA Affiliés, plusieurs « fenêtres » (vues) affichaient
le texte/contenu une fraction de seconde puis il disparaissait :
- côté **Documents**
- **Contenu à publier**
- **Validation des nouvelles recrues** (admin — il fallait valider Cephora très vite)
Sur mobile ET sur PC.

## Cause racine
Dans `partenaire.html` et `admin.html`, `switchView()` appelle la fonction de
rendu **puis** `reveal()` immédiatement :
```
({ renderDocs, renderPubli, renderRecrues… }[id])();  // async (await api…)
reveal();                                              // s'exécute AVANT que le contenu existe
```
Les fonctions de rendu sont `async` (elles `await api(...)` avant de poser le
`innerHTML`). Donc `reveal()` tournait **avant** que les cartes `.rv` n'existent.
Comme `.rv` démarre à `opacity:0` et n'apparaît que lorsque l'IntersectionObserver
ajoute `.in`, le contenu fraîchement chargé n'était **jamais révélé** (invisible).
Au retour sur un onglet, le `reveal()` prématuré révélait l'**ancien** contenu une
fraction de seconde, aussitôt remplacé par le rendu frais → **le clignotement**.
Le polling (`pollSignals`) re-rendait la vue active toutes les 12 s sans `reveal()`
ensuite → la vue redevenait blanche.

De plus, le reveal au scroll laissait les cartes **sous la ligne de flottaison**
invisibles tant qu'on ne scrollait pas — inadapté à un back-office.

## Correctif (fichier partagé `static/app.js`)
Moteur de réveil **automatique et robuste** :
1. `MutationObserver` sur `document.body` : tout `.rv` ajouté au DOM (rendu
   synchrone, async, polling, modale) est pris en charge, peu importe **quand**.
2. Contenu d'une **vue applicative** (`.rv` dans `.view`) → révélé **immédiatement**
   (jamais conditionné au scroll). L'entrée animée de la vue (`roomIn`) garde l'effet premium.
3. **Filet de sécurité** : si l'observer ne déclenche pas, on force `.in`.
   → Le contenu ne peut **jamais** rester invisible.
4. Pages publiques (hub, devenir, lead…) : reveal au scroll **préservé** + filet.

Un seul fichier corrigé (`app.js`) → les deux back-offices guéris d'un coup.
Cache-busting `?v=20260619d` → `?v=20260620a` sur toutes les pages.

## Vérification
Tests headless **Playwright** (Chromium) écrits et exécutés sur **PC (1280px)**
ET **mobile (390px)**, pour le partenaire (DEMO) et l'admin :
- Toutes les vues (docs, publi, classement, gains, clients, reseau, recrues,
  leads, paiements, aff) : **100 % des cartes `.rv` révélées, opacité 1.00**.
- Test du clignotement (aller-retour home→docs→home→docs, dash→recrues→dash→recrues) :
  contenu **visible et stable**. ✅ TOUT VISIBLE — CORRIGÉ.

## Fichiers touchés
- `nebula-affilies/static/app.js` (moteur de réveil)
- `nebula-affilies/{partenaire,admin,hub,devenir,lead,index,rejoindre,console}.html` (cache-bust)

## Reste à faire
- Déployer en prod (Railway : Dockerfile racine + bouton Deploy, ou `railway redeploy`).
