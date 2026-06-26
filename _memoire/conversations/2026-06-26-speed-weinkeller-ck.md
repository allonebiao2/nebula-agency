# Session 2026-06-26 — Vitrine #07 : SPEED SHOPPING × WEINKELLER BY CK

## Contexte
Fiche `nebula-agency.online` de **Ck** pour la maison **« BY CK »** = **deux marques** que la cliente
décrit comme « deux mondes carrément différents » : **Speed Shopping** (achat-pour-autrui France→Bénin
+ colis 2 sens) et **Weinkeller by CK** (cave à vins/champagnes/spiritueux, Porto-Novo).
Exigence forte de Mongazi : **site TOTALEMENT différent** de tout l'existant (aucune ressemblance).
Brief cliente : accueil **double-identité façon « match de foot »**, séparation centrale par un **éclair**,
un bouton pour entrer de chaque côté ; **facturiers séparés** (= outil de gestion, pas la vitrine) ;
inventaire boissons Weinkeller à venir (noms+prix fournis plus tard).

## Ce qui a été fait (run nebula-site complet, PHASE 0→9)
- **Analyse `_partage/`** : 6 affiches = **toutes Speed Shopping** (services, FAQ, catégories, 2 n° WhatsApp,
  sous-marque « Speed Delivery »). **Aucun visuel Weinkeller** fourni (décrit seulement). Logo Speed récupéré.
- **Concept retenu = hub à 2 mondes opposés + seuil-éclair** (3 pages, socle partagé scopé `.w-speed`/`.w-wein`) :
  - `index.html` — **splash** : diagonale scindée par un **éclair SVG animé**, gauche Speed (bleu électrique,
    logo, ENTRER) / droite Weinkeller (noir/rouge/or, emblème, ENTRER), **sceau CK** central, expansion au survol.
  - `speed.html` — monde clair/kinetic (**Anton**), hero **vol France→Bénin animé** (arc + avion offset-path),
    concept (2 services), 6 catégories asymétriques, bande marques, 3 étapes, atouts, avis-exemples, **FAQ+JSON-LD**,
    contact (2 WhatsApp + réseaux + Maps Cotonou), barre CTA mobile + FABs.
  - `weinkeller.html` — monde sombre/cave (**Cinzel + Spectral**), hero spotlight + **silhouettes bouteilles SVG**,
    la maison, 6 caves, **sélection filtrable** (bouteilles placeholder « à valider », commander WhatsApp, lightbox),
    notice « catalogue en cours », commander (cadence cave sans numéros), Maps Porto-Novo.
- **Assets** (`_build_assets.py`) : logo Speed **détouré cercle** + favicons + apple-touch + **3 OG** (maison/speed/wein).
  **3 QR** (segno) → /speed, /weinkeller, / (maison).
- **Affiche A4 + 2 QR** (`affiche.html` → `assets/docs/Affiche_BY_CK_A4.pdf`, 1 page, header split + 2 colonnes).
- **QA réelle** : 0 débordement horizontal mesuré (iframe-diag, 360/390/768/1366, off=0 partout) ; captures Edge.
- **Déploiement Cloudflare Pages** : **https://speed-weinkeller.pages.dev** (200 splash + /speed + /weinkeller, assets 200).

## Décisions / tranches autonomes
- Numéros WhatsApp = ceux des **affiches** (fiables, répétés 6×) : Bénin `+229 0197158484`, France `+33761666887`.
  Le n° du formulaire `0167975626` (= celui de Gloria #04) considéré douteux → **à confirmer**.
- **Refus** de scraper des photos bouteilles sur Google (droits + règle anti-stock) → **silhouettes SVG or « à valider »**.
- **Facturiers** = livrable séparé (outil de gestion), pas la vitrine.

## Reste (À REMPLACER / confirmer)
- Liste boissons Weinkeller (noms + prix) + vraies photos · logo Weinkeller définitif · n° WhatsApp propre Weinkeller ?
- Email/domaine exact · adresses Maps exactes (Cotonou/Porto-Novo) · photos lifestyle Speed (option).
- Domaine custom (DNS) = étape séparée à valider avec la cliente · vrais avis.

## Pièges QA rencontrés (→ EVOLUTION)
- `--headless=new` **bloque** sur le splash (animation CSS infinie + virtual-time) → screenshots en `--headless` classique + `timeout`.
- `--disable-javascript` **ignoré** par cette build Edge (la barre CTA injectée JS apparaissait) → pour révéler le contenu
  `.reveal` en headless, utiliser **`--force-prefers-reduced-motion`** (mon CSS révèle alors tout).
- `min-height:92vh` sur un hero **gonfle** dans les captures à fenêtre haute (vh = hauteur fenêtre) → cap `min(88vh,820px)`.
- iframe-diag : la chaîne `onload`+setTimeout **stagne** sous virtual-time (fonts externes) → créer tous les iframes
  d'emblée puis **mesurer après un délai fixe** (pas de dépendance onload).
- `--print-to-pdf` exige un **chemin Windows absolu** (un chemin relatif ne s'écrit pas).
