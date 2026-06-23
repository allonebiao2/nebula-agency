# Miss cakes — CONTEXT

## Client
- **Marque** : Miss cakes
- **Patronne** : Samelia FAGBOHOUN
- **Activité** : Pâtisserie artisanale **en ligne** (gâteaux sur commande)
- **Ville** : Cotonou, Bénin
- **Secteur** : Restaurant / Alimentation (pâtisserie / dessert)
- **WhatsApp (à CONFIRMER)** : saisi `22967748955` (ancien format 8 chiffres) → forme migrée 10 chiffres câblée = **`2290167748955`** (préfixe `01` post-migration Bénin 2024). **À valider avant impression de l'affiche** (règle absolue : ne pas changer un lien WhatsApp sans confirmation).
- **Service commandé** : Vitrine Digitale + QR Code — 150 000 F setup + 15 000 F / 6 mois (hébergement). Aucune option supplémentaire cochée.
- **Couleurs imposées** : Rose poudré + marron (chocolat).
- **Logo** : annoncé « envoyé sur WhatsApp » → **pas encore reçu** → marque provisoire générée (badge cupcake crème sur dégradé rose→chocolat).
- **Délai** : « le plus vite possible ».

## Analyse (PHASE 0)
- Besoin réel = **vitrine gourmande + carte de créations commandables sur WhatsApp** (hybride **Vitrine + Catalogue**), une seule marque (≠ hub multi-pôles type Djambar).
- Pâtisserie « en ligne » → pas de boutique physique connue : axe **commande WhatsApp + livraison Cotonou**.
- Cible : occasions (anniversaires, mariages, baptêmes, baby showers, fêtes), cadeaux gourmands.

## Design (PHASE 1)
- `ui-ux-pro-max` (bleu/Inter) **écrasé** par la palette imposée : **crème dominante + rose poudré + chocolat + filets caramel-or**.
- Typo : **Cormorant** (display) + **Jost** (texte). Direction : **pâtisserie chic & gourmande, éditoriale** ; motion fluide tempéré 4G (pas de canvas lourd : hero clair + sparkles SVG + grille douce).

## Architecture (PHASE 2 — tranchée par défaut, brief non ambigu)
**Page unique élégante** `index.html` à ancres :
Hero → Barre de confiance → La maison (signature + credo) → Nos créations (6 cartes commandables) → Galerie filtrable + lightbox → Bandeau éditorial → Avis (exemples) → **Commander (formulaire → WhatsApp)** → Contact & livraison (carte Cotonou + horaires) → CTA → Footer. FAB WhatsApp + FAB audio.

## Réalisé (build nebula-site, 2026-06-23)
- **Socle** `assets/app.css` + `assets/app.js` (cache-bust `?v=20260623b`) : nav sticky + burger, lien actif au scroll, reveal, galerie masonry + filtres + lightbox, **formulaire commande → message WhatsApp pré-rempli** (sans backend), audio baseline mobile (OFF par défaut), motion (View Transitions, scroll-driven, tilt desktop), ergonomie mobile (inputs 16px, cibles 44px, safe-area, `overflow-x:hidden`).
- **6 cartes « créations »** commandables (anniversaire, wedding/pièce montée, cupcakes, layer/naked, number/letter, gourmandises) → chacune ouvre WhatsApp pré-rempli avec le nom.
- **Galerie** : 12 tuiles d'aperçu (placeholders SVG gradient par catégorie, marquées « à remplacer ») filtrables + lightbox. **Visibles sans JS** (PE corrigé sur `.gitem`).
- **SEO** : JSON-LD `Bakery`, meta description, OG (image générée), favicon/apple-touch.
- **Assets générés** (`_build_assets.py`, Pillow/segno) : marque provisoire `logos/mark.png` (badge cupcake), favicons, `og/og.jpg` 1200×630, `qr/qr-whatsapp.png`.
- **Affiche A4** `affiche.html` → `assets/docs/Affiche_Miss_cakes_A4.pdf` (logo, slogan, 3 visuels, QR WhatsApp « Commander », tél, chips, réseaux, crédit NEBULA).
- **Infra** : `robots.txt`, `sitemap.xml`, `_headers` (sécurité + cache immutable `/assets/*`), `404.html` de marque.

## QA (PHASE 6) — OK
- **0 débordement horizontal** mesuré (360/390/414/768/1024/1280, scrollWidth=clientWidth).
- Tous les assets **200** en local. Visuel desktop + mobile validé (captures Edge headless).
- **Formulaire testé** (harnais) : génère `https://wa.me/2290167748955?text=…` avec message structuré (nom, numéro, quartier, occasion, type, parts, parfums, message). `URLOK=true`.
- Hook **impeccable** : `em-dash-overuse` corrigé (· / : ) ; `single-font` = **faux positif** (Cormorant + Jost dans le CSS partagé, le hook ne scanne qu'un fichier).

## Mise en ligne (PHASE 8)
- Cloudflare Pages, projet **`miss-cakes`** → **https://miss-cakes.pages.dev** (à vérifier 200 en prod).

## À REMPLACER (placeholders pro « à valider »)
- **Logo** → badge cupcake provisoire (remplacer par le vrai logo dès réception WhatsApp ; régénérer favicons/OG/affiche via `_build_assets.py`).
- **Photos** → tuiles d'aperçu SVG (basculer les `.gitem .ph` en `<img>` quand les vraies photos arrivent ; pipeline prêt).
- **Avis** → 3 exemples marqués « à valider » (remplacer par de vrais retours).
- **Numéro WhatsApp** → confirmer `2290167748955` (surtout avant d'imprimer l'affiche).
- **Réseaux sociaux** → Instagram / Facebook (emplacements présents, liens « # » à remplir).
- **Adresse / zone** → carte centrée sur Cotonou (générique) ; préciser quartier de retrait + frais de livraison si besoin.
- **Horaires** → valeurs par défaut (Lun-Ven 8h-20h, Sam 9h-20h, Dim sur RDV) à confirmer.

## À demander sur WhatsApp (en parallèle)
- [ ] Logo (idéalement fond transparent, 2 versions)
- [ ] Photos de réalisations par type (anniversaire, wedding, cupcakes, gourmandises)
- [ ] Confirmer le **numéro WhatsApp**
- [ ] Avis clients réels + horaires
- [ ] Réseaux (Instagram / TikTok / Facebook)
- [ ] Parfums / spécialités à mettre en avant ; fourchette de parts/prix

## Statut
- Créé le 2026-06-23. Build run-to-completion (skill nebula-site) terminé + déployé.
- Domaine custom éventuel = étape ultérieure (DNS) à la demande de Mongazi.
