# CONTEXT — SPEED SHOPPING × WEINKELLER BY CK (client #07)

> Fiche reçue le **2026-06-26** via formulaire `nebula-agency.online` + brief stratégique vocal.
> Contact intermédiaire : **Ck**. Marché : Bénin (Cotonou / Porto-Novo) + France (Paris).
> Statut : **EN LIGNE** ✅ **https://speed-weinkeller.pages.dev** (Cloudflare Pages, déployé le 2026-06-26 via nebula-site `?v=20260626b`).
> Exigence #1 de Mongazi : **site TOTALEMENT différent** de tout l'existant (Djambar, Miss cakes…) — aucune ressemblance. → tenue par le concept **hub à 2 mondes opposés + seuil-éclair**.
> Affiche A4 + 2 QR : `assets/docs/Affiche_BY_CK_A4.pdf`.

## La maison « BY CK » — DEUX mondes
Un seul propriétaire (CK), **deux marques** que la cliente décrit comme « deux mondes carrément
différents ». D'où l'architecture **hub à 2 mondes** reliés par un **seuil-éclair** (idée de la
cliente : page d'accueil façon « présentation de match de foot », séparation centrale par un
éclair / zigzag, un bouton pour entrer de chaque côté).

### 1. SPEED SHOPPING (+ sous-marque « Speed Delivery »)
- **Promesse** : « Vos achats en France, livrés chez vous au Bénin. » · « La France à portée de main. »
- **Service** : personal shopping / achat-pour-autrui France→Bénin + envoi de colis **2 sens**
  (Speed Delivery : France→Bénin ET Bénin→France).
- **Villes** : Cotonou (Bénin) · Paris (France).
- **Couleurs** : bleu nuit + bleu ciel + blanc (univers clair, énergique, « vitesse »).
- **On achète sur** : Zara, Amazon, Sephora, Nike, Cdiscount, Zalando… « et bien plus ».
- **6 catégories** : Vêtements & chaussures · Articles pour enfants · Cosmétiques & parfums ·
  Téléphones & électronique · Articles de maison · Produits alimentaires.
- **Commander en 3 étapes** : 1) Envoyez le lien de vos articles / votre panier · 2) On vous envoie
  le total + nos frais de service (clair, sans surprise) · 3) Après paiement, on achète et on expédie.
- **Délai** : ~3 à 5 jours (selon expédition aérienne). **Paiement** : Mobile Money (MoMo), 100 % sécurisé.
- **Atouts** : tous poids acceptés · colis assurés jusqu'à livraison · suivi personnalisé · service client.
- **Contacts (depuis les AFFICHES officielles, donc fiables)** :
  - WhatsApp **Bénin** : **+229 0197 1584 84** → `wa.me/2290197158484`
  - WhatsApp **France** : **+33 7 61 66 68 87** → `wa.me/33761666887`
  - Email : contact@speedshopping.com *(à confirmer le domaine exact)*
  - Réseaux : @speedshopping229 (Facebook · Instagram · TikTok)

### 2. WEINKELLER BY CK  (« cave à vin » en allemand · jeu de mots « Vine Killer »)
- **Univers** : cave à vins, champagnes & spiritueux — **masculin, premium**, **noir / rouge / or** (+ blanc/doré/jaune).
- **Ville** : Porto-Novo.
- **Catalogue boissons** : la cliente FOURNIRA les **noms exacts + prix** de chaque boisson (à venir).
  Elle suggérait de prendre les visuels bouteilles sur Google → **REFUSÉ** (droits d'auteur + règle
  « jamais de stock déguisé en produit réel »). On met des **silhouettes SVG or « à valider »** en
  attendant les vraies photos + la vraie liste.
- **Aucun visuel ni logo Weinkeller fourni** → wordmark + emblème SVG « à valider » créés par nos soins.

## Demandes spécifiques de la cliente (brief)
1. **Accueil double-identité** (match/éclair, bouton chaque côté). ✅ pris en compte (splash).
2. **Facturiers séparés** par marque → c'est un **outil de gestion/facturation distinct**, PAS la
   vitrine. Noté comme livrable **séparé/futur** (la vitrine ne facture pas).
3. **Inventaire boissons Weinkeller** : structure catalogue prête, en attente liste réelle.
4. **Logistique** : elle attend un paiement (« le truc du bois » = hébergement/domaine) avant lancement
   officiel ; ajoutera d'autres idées au fil de l'eau.

## Architecture du site (hub multi-pages, socle partagé)
- `index.html` — **seuil-éclair** double-identité (gateway vers les 2 mondes) + monogramme CK.
- `speed.html` — monde **Speed Shopping** (clair, kinetic) : hero vol France→Bénin, concept, 6 catégories,
  3 étapes, atouts, FAQ (JSON-LD), contact (2 WhatsApp + réseaux + Maps Cotonou).
- `weinkeller.html` — monde **Weinkeller by CK** (sombre, cave) : hero spotlight, la maison, sélection
  par catégories + bouteilles placeholder « à valider », commander WhatsApp, contact + Maps Porto-Novo.
- Socle : `assets/app.css` + `assets/app.js` (scopé `.w-speed` / `.w-wein`). Images **relatives**.

## Direction visuelle (anti-ressemblance)
- **Splash** : diagonale scindée par un **éclair SVG animé**, 2 ambiances opposées, expansion au survol.
- **Speed** : *Archivo / Archivo Expanded*, bleu électrique, lignes de vitesse, arc de vol pointillé + avion,
  compositions diagonales asymétriques. Thème **clair**.
- **Weinkeller** : *Cinzel* (capitales gravées, étiquette de spiritueux) + *Spectral* (corps), noir/oxblood/or,
  spots, poussière d'or, silhouettes de bouteilles. Thème **sombre**.
- Galeries/sélections en **dispositions différentes** des sites précédents (pas la mosaïque bento de Djambar).

## FAIT le 2026-06-26 (2e passe — vraies images + 3D)
- ✅ **WhatsApp Weinkeller CONFIRMÉ par Mongazi** = même n° que la maison (+229 0197 1584 84) ; caveat retiré du site.
- ✅ **Champagnes RÉELS intégrés** : 8 bouteilles (Ruinart ×3, Moët ×2, Veuve Clicquot, Lanson, Nicolas Feuillatte),
  photos client **détourées** fond blanc→transparent (`_build_bottles.py`) → `assets/images/cave/*.webp`, **noms + prix réels**.
- ✅ **3D + animations** (demande Mongazi) : **coverflow 3D** des champagnes au hero (perspective, reflets, halo or,
  auto-rotation, drag/flèches/points, fiche live nom+prix+Commander) + **cartes photo profondeur 3D** dans la sélection
  (tilt parallax translateZ + reflet) + **poussière d'or** (canvas). PE : sans JS, coverflow = simple rangée scrollable.

## FAIT le 2026-07-02 (héros photo cave + animation « boissons »)
- ✅ **Nouveau héros Weinkeller** : vraie photo de cave (fournie par Mongazi via `_partage/weinkeller HERO.PNG`),
  optimisée → `assets/images/hero/weinkeller-hero.webp` (113 Ko) + `weinkeller-hero-mobile.webp` (52 Ko) via `_build_hero.py`.
  Câblée en fond du héros (`<picture>` desktop/mobile, fetchpriority high).
- ✅ **Animation adaptée au vin/boissons** (GPU, `prefers-reduced-motion` OK) : Ken Burns cinématique (poussée lente
  vers le verre), **effervescence dorée** (14 bulles qui montent, façon champagne), lueur ambrée qui « respire » sur
  le verre, scrim + ombres de texte pour la lisibilité, lueur dorée pulsée sur « by CK ». `?v=20260702a`.
- QC navigateur desktop + mobile : image chargée (mobile = webp 52 Ko via srcset), 0 erreur console, 0 requête 404,
  texte parfaitement lisible. Déployé Cloudflare Pages + vérifié 200 en prod.

## FAIT le 2026-07-01 (catégorie Whiskys + Rhum — vraies bouteilles)
- ✅ **Catégorie « Whiskys » ACTIVÉE** (`?v=20260701n`) : **10 bouteilles réelles** envoyées par Ck (dossier
  `assets/images/gallery/Les whisky_`), détourées fond clair→transparent en **IA rembg** (`_build_whisky.py`,
  isnet-general-use, 1100 px, webp) → `assets/images/cave/*.webp`. Sous-filtres : **Single Malt (4)** =
  Lagavulin Distillers/16 ans, Aberlour 14, BenRiach 10 · **Cognacs (6)** = Hennessy VSOP/VS, Martell VS/VSOP,
  Rémy Martin VSOP, Camus VS. Noms + prix réels, WhatsApp pré-rempli par bouteille.
- ✅ **Catégorie « Rhum » ACTIVÉE** : **Eminente Reserva** (rhum ambré, Cuba, 70 CL, 65 000 F) — 1 bouteille.
  (Eminente était rangé dans le dossier « whisky » du client ; classé en Rhum car c'est un rhum.
  Mongazi préfère aussi Rhum — ⏳ **en Rhum pour l'instant, en attente de la réponse de Ck** (2026-07-02).
  Si Ck veut le voir sous Whiskys : changer `data-cat="rhum"` → `data-cat="whisky"` + `data-sub="rhum"` sur la carte Eminente.)
- ✅ 3e carte « Nos caves » = **Whiskies & cognacs** ; notice « en stock » mise à jour (Champagnes, Whiskys,
  Cognacs, Tequilas & Rhum). Injection idempotente via `_apply_whisky.py` (UTF-8).
- ✅ QC navigateur (Playwright) : 32 bouteilles, 0 erreur console, 0 requête 404, filtres/sous-filtres OK,
  détourage sans halo (fond clair ET sombre). Déployé + vérifié 200 en prod.
- ✅ Martell **VS 65 000 F > VSOP 60 000 F** : **confirmé par Mongazi 2026-07-02, garder tel quel** (« laisse comme c'est »).
- ⏳ **Eminente Reserva** : classé en Rhum, **en attente réponse de Ck** (cf. section 2026-07-01).
- ⏳ Volumes des 4 single malts (affichés « Islay/Speyside » sans contenance ; 70 CL standard non inventé) — à confirmer si utile.

## À CONFIRMER / À REMPLACER (reste)
- [ ] Email / domaine exact (contact@speedshopping.com ?).
- [ ] **Autres caves Weinkeller** : **vins rouges/blancs, gin, pastis, vodka** (noms + prix + photos).
  ✅ Faits : champagnes (8→13), tequilas (8), **whiskies+cognacs (10), rhum (1) — 2026-07-01**.
  Reste = catégories encore « bientôt ».
- [ ] **Logo Weinkeller** définitif (on a créé un wordmark/emblème « à valider »).
- [ ] **Adresses exactes** Cotonou (Speed) + Porto-Novo (Weinkeller) pour Google Maps précis.
- [ ] Photos lifestyle Speed (optionnel — le monde Speed est volontairement graphique/illustré).
- [ ] **Facturiers** séparés (outil de gestion) = chiffrage/livrable distinct.

## Tarif
Vitrine + QR : 150 000 F (setup) + 15 000 F / 6 mois (hébergement). Option : Google Maps.
