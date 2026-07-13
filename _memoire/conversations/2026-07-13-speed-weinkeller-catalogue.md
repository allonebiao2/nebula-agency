# 2026-07-13 — Weinkeller by CK : catalogue enrichi (+28 bouteilles, onglets Cognacs & Apéritifs)

Client #07 — SPEED SHOPPING × WEINKELLER BY CK.
Live : https://speed-weinkeller.pages.dev/weinkeller · `?v=20260713a`
Skills invoqués (demande Mongazi) : `ui-ux-pro-max`, `frontend-design`, `impeccable`.

## Demande
Ck a déposé de **nouvelles bouteilles dans diverses catégories** → les ajouter toutes au catalogue
Weinkeller. + **Remplacer l'image du Clase Azul Reposado** par la nouvelle « corrigé »
(`assets/images/gallery/Catégorie TEQUILA/Clase Azul Reposado Prix _ 250.000 FCFA corrigé.PNG`).

## Ce qui a été fait

### 1. Clase Azul Reposado — image remplacée
- L'ancienne image était coupée + un damier collé en fond. La « corrigé » = bouteille entière.
- `_detour_clase.py` : rembg isnet-general-use, 1100 px, webp q90 → écrase
  `assets/images/cave/clase-azul-reposado.webp` (damier retiré, QC mi-clair/mi-sombre OK).

### 2. 28 nouvelles bouteilles détourées
- `_build_newcave.py` : même pipeline que `_build_whisky.py` (rembg isnet 1100 px → webp),
  planche QC `_newcave_qc.png`. **28/28 détourées** proprement (contrôle : pas de halo).
- Sources dans `assets/images/gallery/catégorie {GIN,RHUM,VODKA,PASTIS,MARTINI,Le WHISKY}`.

### 3. Injection idempotente dans le catalogue
- `_apply_cave.py` : remplace **uniquement** le contenu de `<div class="bottles">` (matching par
  profondeur de `<div>`), **préserve** le drawer `#caveNav` et les cartes existantes verbatim
  (les sous-filtres `data-sub` champagne/tequila sont conservés).
- Reclasse les 6 cognacs (ex-`data-cat="whisky" data-sub="cognac"`) → `data-cat="cognac"`
  (+ badge « Cognac »). Les single malts (`data-sub="scotch"`) → `whisky` à plat.
- Ordonne par `CAT_ORDER` puis prix décroissant. Bump `?v=20260702b`→`?v=20260713a`.
- **Piège évité** : une 1ʳᵉ version régénérait toute la SÉLECTION avec `.wein-filter` et
  **supprimait `data-sub`** → cassait le drawer. Corrigé en ne touchant QUE `.bottles`.

### 4. Alignement de la navigation (TAX `app.js`)
La nav du tiroir (`#caveNav`) est pilotée par le tableau `TAX`. Modifié pour que les `data-cat`
des cartes matchent, sinon Cognacs/Apéritifs ne s'affichent pas :
- **Whiskys** : remis à plat (`subs: []`, label « Whiskys »).
- **+ Cognacs** : nouvel onglet dédié (`cat: "cognac"`).
- **+ Apéritifs & liqueurs** : nouvel onglet (`cat: "aperitif"`) — Ricard reclassé ici.
- **− Pastis** : onglet retiré (Ricard est désormais en Apéritifs).
- Champagnes/Tequila conservent leurs sous-filtres.
- Onglets finaux : Vins · Champagnes · Whiskys · Cognacs · Tequila · Rhum · Gin · Vodka · Apéritifs & liqueurs.

### 5. Catalogue final = 60 fiches
Champagnes 13 · Whiskys 15 · Cognacs 6 · Tequila 8 · Rhum 6 · Gin 4 · Vodka 1 · Apéritifs & liqueurs 7.
Seul **Vins** reste « bientôt » (0 produit → état vide « commande spéciale »).

Détail des 28 ajouts :
- **Whiskys +11** : Chivas Regal 18, Glenfiddich VAT 01, The San-In, Akashi Sherry Cask, Haig Club,
  Jack Daniel's, Aberlour 10, The Deveron 10, Glen Turner 12, Knockando 18, Hwayo.
- **Rhum +5** : Bologne Réserve Spéciale, Ti'Ced Ananas Victoria, Kraken Black Spiced, Hédone, Rivière du Mât.
- **Apéritifs +7** : Baileys Original, Baileys Salted Caramel, Ricard, Martini Rosso, Jägermeister 1 L / 70 cl / 35 cl.
- **Gin +4** : Dry Gin XII, Hendrick's, June by G'Vine, Whitley Neill.
- **Vodka +1** : Cîroc.

**Sans prix (« Prix sur demande »)** ⏳ à fournir par Ck : Whitley Neill, Hédone, Rivière du Mât,
Glen Turner 12, Knockando 18, Hwayo.

## QC (puppeteer HS toute la session → vérif statique + prod)
- `app.js` syntaxe OK (`node --check`), TAX = 9 cats alignées sur les `data-cat`.
- 60 fiches `.bottle real`, **0 image cassée** (chaque `src=cave/*.webp` existe), 0 doublon de carte
  (`grande-dame-2015.webp` réutilisée une fois = hero coverflow, normal).
- Badges Cognac = 6, plus aucun `data-sub` whisky résiduel.
- Prod vérifiée après deploy : `/weinkeller` → 200, sert `?v=20260713a`, 6 cognacs + 7 apéritifs
  dans le HTML, TAX live contient `cognac`+`aperitif`, images neuves 200.

## Déploiement
- `_dist` construit **sélectivement** : HTML + `app.*` + `images/{cave,hero,logos,og,favicon,qr}`.
  **Exclus** : `gallery/` (66 Mo sources), `Wenkeller/` (29 Mo sources), `docs/`, `_*.py`, QC,
  `affiche.html`, `_diag.html`, `CONTEXT.md`. → `_dist` = **5,9 Mo**.
- `npx wrangler@latest pages deploy _dist --project-name=speed-weinkeller --branch=main` → OK.
- Commit `3cb6027` (36 fichiers), poussé sur GitHub.

## Leçons
- **Découverte** : le dossier `assets/images/Wenkeller/` (29 Mo) EST une réserve de sources brutes
  (comme `gallery/`), non référencée par le site → à exclure du `_dist` au même titre que `gallery/`.
  Toujours grep les 3 HTML + `app.*` pour savoir ce qui est réellement servi avant de bâtir `_dist`.
- **TAX ↔ data-cat** : sur ce socle, ajouter une catégorie de produits impose de mettre à jour le
  tableau `TAX` de `app.js` (sinon la catégorie n'apparaît pas dans le drawer).
- Détourage IA + injection = 3 scripts réutilisables et **idempotents** (clé = slug), UTF-8 garanti
  (jamais PowerShell Get-Content/WriteAllText). Cf. `_build_whisky.py` / `_apply_whisky.py`.

## Reste
- [ ] Prix des 6 bouteilles « Prix sur demande » (Ck).
- [ ] Catégorie **Vins** (rouges/blancs — seule encore « bientôt »).
- [ ] Logo Weinkeller définitif · adresses Maps exactes · email/domaine Speed.
