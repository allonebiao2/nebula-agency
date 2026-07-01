# 2026-07-02 — Speed × Weinkeller by CK : catégorie Whiskys + Rhum (vraies bouteilles)

> Client #07 · `clients/07-speed-weinkeller-ck/` · LIVE https://speed-weinkeller.pages.dev
> Suite de la VAGUE 2026-07-01 (voir `2026-07-01-speed-weinkeller-evolutions.md`).

## Demande de Mongazi
« J'ai envoyé les images des produits de la catégorie whisky dans le dossier `gallery`, ajoute-les
à la page et mets-la à jour au max de tes capacités, sans erreur et sans erreur de détourage. »

## Contenu réel reçu (dossier `assets/images/gallery/Les whisky_`)
11 bouteilles envoyées par Ck (nom + prix dans les noms de fichiers), en réalité 3 familles :
- **4 single malts (Scotch)** : Lagavulin Distillers Edition (90 000), Lagavulin 16 ans (71 000),
  Aberlour 14 ans (60 000), BenRiach 10 ans (53 000).
- **6 cognacs** : Hennessy VSOP (70cl 90 000 / 1L 120 000), Hennessy VS (70cl 50 000 / 1L 60 000),
  Martell VS 1L (65 000), Martell VSOP 1L (60 000), Rémy Martin VSOP (60 000), Camus VS 1L (60 000).
- **1 rhum** : Eminente Reserva (Cuba, 70cl, 65 000) — rangé par erreur dans le dossier « whisky ».

## Ce qui a été fait
1. **Détourage IA** (`_build_whisky.py`) — même pipeline que les champagnes/tequilas
   (`_build_bottles_ai.py`) : **rembg isnet-general-use**, hauteur 1100 px, webp q90 → `assets/images/cave/*.webp`.
   Planche de contrôle générée (fond mi-clair / mi-sombre) → vérifié **0 halo, 0 liseré, rien de coupé**
   (y compris flacon transparent Eminente + bouteille noire Rémy Martin).
2. **Injection idempotente** (`_apply_whisky.py`, UTF-8, marqueurs `<!-- WHISKY+RHUM ... -->`) :
   10 cartes catégorie `whisky` (badges Whisky/Cognac, `data-sub` scotch/cognac) + 1 carte `rhum` (Eminente).
   WhatsApp pré-rempli par bouteille.
3. **app.js** : sous-filtres ajoutés à la catégorie whisky → `subs: [["scotch","Single Malt"],["cognac","Cognacs"]]`,
   label « Whiskys & Cognacs ». Le système est data-driven : `isReal()` bascule « bientôt » → compteur dès qu'une
   carte réelle existe. Rhum activé pareil (1 bouteille).
4. **3e carte « Nos caves »** (Whiskies & cognacs, `data-jump="whisky"`) ; passage `cellars-2` → `cellars` (3 colonnes).
5. **Notice** « en stock » MAJ : Champagnes, Whiskys, Cognacs, Tequilas & Rhum (Vins/Gin/Pastis/Vodka = bientôt).
6. **Cache-bust** `?v=20260701m` → `?v=20260701n` sur les 3 pages (index/speed/weinkeller).

## QC (fenêtre navigateur fraîche, Playwright)
32 bouteilles · Whiskys **10** (Single Malt 4 / Cognacs 6) · Rhum **1** · **0 erreur console · 0 requête 404** ·
filtres + sous-filtres + recherche OK · WhatsApp décodé correct. Déployé Cloudflare Pages
(`_dist` propre, `wrangler pages deploy`), **vérifié 200 en prod** + images webp 200.

## Décisions / à valider
- **Eminente Reserva** = classé en **Rhum** (c'est un rhum, pas un whisky). Mongazi préfère aussi Rhum
  → **laissé en Rhum en attendant la réponse de Ck** (2026-07-02). Bascule éventuelle : `data-cat="rhum"`
  → `data-cat="whisky"` + `data-sub="rhum"` sur la carte Eminente.
- **Martell VS (65 000) > VSOP (60 000)** (inhabituel) → **confirmé par Mongazi : garder tel quel**.
- Volumes des 4 single malts affichés en région (Islay/Speyside) sans contenance (70 CL standard non inventé).

## Leçon réutilisable
- **rembg (isnet-general-use)** = méthode de détourage canonique pour les bouteilles Weinkeller
  (bouteilles sombres/ambrées/verre sur fond clair) → bords propres sans halo. Toujours faire une
  **planche de contrôle fond clair + fond sombre** pour valider avant livraison.
- Ne **jamais** relancer `_apply_weinkeller.py` (obsolète, reconstruit l'archi 2026-06-26) : éditer le
  weinkeller.html courant via script Python UTF-8 dédié + marqueurs idempotents.

## Fichiers touchés
`weinkeller.html`, `index.html`, `speed.html`, `assets/app.js`, `assets/images/cave/*.webp` (×11 nouveaux),
`_build_whisky.py`, `_apply_whisky.py`, `CONTEXT.md`. Commits : `16ff457` (livraison) + celui-ci (mémoire).
