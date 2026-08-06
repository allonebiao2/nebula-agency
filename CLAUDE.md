# NEBULA Agency — Cerveau Principal

## Identité
- Agence : NEBULA Agency
- Fondateur : Mongazi, Cotonou Bénin
- Marché : Afrique de l'Ouest francophone
- Mission : **digitalisation sectorielle** — concevoir le **logiciel métier** de chaque secteur (SaaS vertical), en plus des vitrines digitales et de l'automatisation IA
- Positionnement : **studio de solutions verticales / éditeur de logiciels métier** (*vertical SaaS*), pas une simple agence de sites. Slogan : « Un outil pensé pour VOTRE secteur, pas un site générique. » Preuves : Digital HSE (industrie/HSE), Vendora (commerce), vitrines par métier. Méthode = *product factory* (socle réutilisable décliné par secteur, cf. skill `nebula-site`). Détail en mémoire : `project_positionnement-vertical`.
- Autres marques : AXIO IA (éducation IA), KARABA Finance

## Stack technique
- Vitrines : HTML pur, CSS inline, images base64
- Automatisation : n8n self-hosted (Hostinger VPS 72.61.103.56)
- IA : Claude Anthropic, Gemini, Groq llama-3.3-70b
- Images/vidéos générées : **WaveSpeed** (961 modèles, un seul solde, à l'image).
  Le meilleur : `google/nano-banana-pro/text-to-image`, **0,14 $**. Clé dans
  `secrets/wavespeed.env`. Mode d'emploi et pièges :
  `_memoire/apprentissages/2026-08-05-wavespeed-nano-banana-pro.md`.
  ⛔ **Une image générée ne devient jamais le catalogue d'un client** : ambiance,
  matière et lieu sont autorisés, une pièce présentée comme vendable ne l'est pas.
- WhatsApp : Twilio
- Base de données : Supabase
- Hébergement vitrines : Netlify
- Versioning : GitHub (allonebiao2)

## Règles absolues
- Images toujours en base64, jamais Google Drive CDN
- Ne jamais modifier les liens WhatsApp sans confirmation
- Toujours montrer les changements avant commit
- Jamais pusher sans validation de Mongazi
- Chaque client a son dossier dans /clients/
- Assets organisés en images/ videos/ docs/
- Clés API et secrets : uniquement dans `.env` local, jamais commités
- Clé secrète FedaPay (`sk_live_*`) : JAMAIS dans le HTML ni côté client

## FedaPay — Paiement Mobile Money
- Provider de paiement pour les vitrines clients (Mobile Money, cartes)
- Clés API stockées dans `.env` local (voir `.env.example` pour la structure)
  - `FEDAPAY_PUBLIC_KEY` (pk_live_*) : utilisable côté client / HTML
  - `FEDAPAY_SECRET_KEY` (sk_live_*) : uniquement côté serveur (n8n, backend)
- Intégration dans vitrines : utiliser UNIQUEMENT la clé publique
- Sous-comptes clients : créer via "+ Ajouter un compte" dans le dashboard FedaPay
- Notifications paiement : WhatsApp + MyFeda (app) + Email natif FedaPay
- Voir `_memoire/stack.md` pour la doc complète du stack technique

## Journal automatique
À chaque fin de session Claude Code :
1. Créer ou mettre à jour _memoire/journal/[date]-journal.md
2. Lister toutes les modifications faites
3. Lister les fichiers touchés
4. Commit automatiquement ce journal

## Éléments d'une vitrine NEBULA
### Sections standard
- Hero (titre + accroche + CTA WhatsApp)
- Services/Produits (grille avec photos)
- Galerie (photos + vidéos)
- Témoignages clients
- Contact (WhatsApp + localisation)

### Assets nécessaires par vitrine
- Logo (base64 PNG)
- Photos produits/services (base64)
- Vidéo présentation (lien YouTube/MP4)
- Palette couleurs (primaire, secondaire, fond)
- Numéro WhatsApp Business
- Textes (accroche, description services)

### Checklist avant livraison
- Images en base64 ✓
- Liens WhatsApp testés ✓
- Mobile responsive ✓
- Vitesse chargement ok ✓
- Textes validés par client ✓

## Clients actifs
| # | Client | Business | Statut | WhatsApp |
|---|---|---|---|---|
| 01 | Jocelyne (mère de Mongazi) | **Grain d'Esthétique** — institut de beauté · Cotonou Haie-Vive · Sothys/Sultane de Saba | **MIGRÉ Cloudflare Pages** (projet `grain-esthetique`) + **domaine `graindesthetique.com`** (Hostinger→Cloudflare, SSL en activation 2026-07-02) · **passe premium 2026-07-02** : promo Fête des Pères expirée retirée, emojis→SVG, SEO/OG/JSON-LD, a11y (nav boutons), CTA « Prendre rendez-vous » + FAB WhatsApp, **1 animation signature par section** (Éclosion/Radiance/Respiration/Glisse/Vernis/Élévation/Assurance) · ⚠️ n° WhatsApp `2290197085576` INCHANGÉ (91 liens) · ancien Netlify obsolète à débrancher | 0197085576 |
| 02 | Cédène | Little Sun Pearls - bijoux | En attente photos | - |
| 03 | Abakar | WECS - montage vidéo | En cours | - |
| 04 | Gloria | Luxury Skin Clinic - cosmétique (hub 4 pages) | Structure créée | 0167975626 |
| 05 | Saeir Thiam | **Djambar Team** (⚠️ JAMAIS « groupe » — redondant avec « team » ; dire « la maison » / « les pôles ») — pôle **Saeir Thiam Bijouterie** (or/argent/sur-mesure) + comm./événementiel à venir · Cotonou (Agla Gbodjètin) · hub multi-pages évolutif | **LIVE https://djambarteam.com** (domaine final, Cloudflare Pages) · finition complète 23/06 (motion, hero nuit vidéo, formulaire devis→WhatsApp, conversion, ergonomie mobile) · 24/06 « groupe » retiré partout (→ « la maison »/« Cotonou ») · 24/06 **V18** : 11 animations signatures par section (bijouterie) + pôles différenciés (Comm = studio/égaliseur, Événementiel = scène/projecteurs) · **V19 conversion** (FAQ+FAQPage, process 3 étapes, garantie, barre CTA mobile+tel:) · **V20 héros média** (accueil still chaîne d'or Ken-Burns + bijouterie vidéo joaillerie 376 Ko) `?v=20260625b` · reste : **vrais avis + photos sans watermark + fiche Google Business** | 0197967671 |
| 06 | Samelia FAGBOHOUN | **Miss cakes** — pâtisserie artisanale en ligne (gâteaux sur commande) · Cotonou · page unique vitrine + catalogue commandable | **LIVE https://miss-cakes.pages.dev** (Cloudflare Pages, skill `nebula-site`) · motion spectaculaire (drips glaçage, CTA AA raspberry) + **une animation signature DIFFÉRENTE par section `?v=20260624c`** (hero parallax, engagements ligne dorée, La maison clip+unfold, créations en perspective, galerie scatter, éditorial Ken-Burns, avis slide+étoiles, commander poussière de sucre, contact tampons, CTA confettis) + **boutons Liquid Glass** (verre raspberry/vert/givré, AA) + **police texte Bricolage Grotesque** (ex-Jost/Hanken jugés « trop basiques » ; grotesque à caractère) `?v=20260624f` + **VRAIES images câblées** : hero = **vidéo cinemagraph** (cake) + 3 fonds photo (éditorial/CTA/La maison, Nano Banana Pro) · rose poudré + chocolat + crème · formulaire commande→WhatsApp · affiche A4+QR · reste : vrai logo + photos galerie + vrais avis + **confirmer n° WhatsApp** | 2290167748955 (à confirmer) |
| 07 | Ck | **SPEED SHOPPING × WEINKELLER BY CK** — maison « BY CK » à **2 marques/mondes opposés** (la cliente : « deux mondes carrément différents ») · **Speed Shopping** = achat-pour-autrui France→Bénin + colis 2 sens (Cotonou/Paris, bleu) · **Weinkeller by CK** = cave vins/champagnes/spiritueux (Porto-Novo, noir/rouge/or) | **LIVE https://speed-weinkeller.pages.dev** (Cloudflare Pages, skill `nebula-site`, `?v=20260626b`) · concept **hub à 2 mondes + seuil-éclair** (accueil splash façon « match » : éclair central, 1 bouton/côté, sceau CK) — exigence Mongazi « totalement différent » tenue · **Speed** clair/kinetic (Anton, vol France→Bénin animé, 6 catégories, 3 étapes, FAQ+JSON-LD) · **Weinkeller** sombre/cave (Cinzel+Spectral, silhouettes bouteilles SVG, sélection filtrable placeholder « à valider ») · logo Speed détouré, OG×3, affiche A4+2 QR · **n° : Bénin +229 0197158484 (confirmé Mongazi, MÊME pour les 2 marques) + France +33761666887** · **2e passe 2026-06-26 `?v=20260626c`** : **8 CHAMPAGNES RÉELS** (Ruinart/Moët/Veuve Clicquot/Lanson/Nicolas Feuillatte, photos client détourées fond→transparent `_build_bottles.py`, noms+prix) + **3D/animations** = **coverflow 3D** champagnes au hero (perspective, reflets, halo, auto+drag+fiche live) + cartes photo profondeur 3D + poussière d'or · reste : **autres caves Weinkeller (rouges/spiritueux… noms+prix+photos)** · logo Weinkeller défin. · adresses Maps exactes · **facturiers séparés = outil distinct** · **VAGUE 2026-07-01 (`?v=20260701m`, détail `_memoire/conversations/2026-07-01-speed-weinkeller-evolutions.md`)** : Weinkeller = **vrai logo blason** (loader/nav/favicon/OG) + **3 fiches services animées** (Commande spéciale import FR/DE→BJ · Événementiel · Bar à domicile, animations distinctes) + **bannière provenance FR+DE dans le héros** & **carrousel champagnes en bas** + **8 catégories** (Vins/Champagnes/Whiskys/Tequila/Rhum/Gin/Pastis/Vodka, 6 « bientôt »→état vide commande spéciale) + **architecture = drawer DROIT global** ouvert par **bouton brillant à gauche (auto-masqué quand « Parcourir » visible)** + **recherche de boissons** + **pop-up coffrets à chaque visite** (exit-intent+animation) · Speed = refonte 4 services+N.B.+carrousel bas + **typo compacte mobile** + nav sans « Commander » + barre mobile « Appeler » seul · commun = **bruitage de touché** + perf(golddust idle)+révélations distinctes/zone + cibles ≥44 + retrait « à valider/à confirmer » + **bloc légal en pied** (confidentialité/conditions-usage/mentions par marque) + **affiche A4+QR** régénérée (`assets/docs/Affiche_BY_CK_A4.pdf`) · ⚠️ bumps/sync **via Node/Python UTF-8** (jamais PowerShell Get-Content/WriteAllText = mojibake) · **VAGUE 2026-07-02 (`?v=20260701n`, détail `_memoire/conversations/2026-07-02-speed-weinkeller-whiskys.md`)** : catégorie **Whiskys ACTIVÉE** (10 = 4 single malts Lagavulin/Aberlour/BenRiach + 6 cognacs Hennessy/Martell/Rémy/Camus · sous-filtres **Single Malt/Cognacs**) + **Rhum** (Eminente Reserva) — vraies bouteilles Ck **détourées IA rembg** (`_build_whisky.py` isnet 1100px + `_apply_whisky.py` inject idempotente UTF-8) · 3e carte « Nos caves » Whiskies&cognacs · notice en-stock MAJ · QC Playwright (32 bouteilles, 0 err/0 404, détourage sans halo) déployé+vérifié 200 · **Eminente laissé en Rhum ⏳ att. réponse Ck** · **Martell VS(65k)>VSOP(60k) confirmé garder** (Mongazi) · **VAGUE 2026-07-13 (`?v=20260713a`, détail `_memoire/conversations/2026-07-13-speed-weinkeller-catalogue.md`)** : catalogue **60 fiches** (+28 bouteilles détourées rembg) · **2 nouveaux onglets = Cognacs + Apéritifs & liqueurs** (Cognacs sortis des Whiskys→onglet dédié, Whiskys à plat, Ricard→Apéritifs, **Pastis retiré**) · répartition Champagnes 13/Whiskys 15/Cognacs 6/Tequila 8/Rhum 6/Gin 4/Vodka 1/Apéritifs 7, seul **Vins** reste « bientôt » · **Clase Azul Reposado image corrigée** (re-détour) · 6 sans prix « Prix sur demande » ⏳ att. Ck · `_build_newcave.py`+`_apply_cave.py` idempotents UTF-8, `_dist` allégé 5,9 Mo (sources `gallery`/`Wenkeller` exclues) · déployé Cloudflare + vérifié 200 | +229 0197158484 (les 2 marques, confirmé) |
| 08 | HH Design | **HH DESIGN** — **maison d'ébénisterie / mobilier bois noble** à Cotonou (⚠️ PAS immobilier : erreur de 1er brief corrigée le 2026-07-04 via les planches de marque `_partage/inspiration 1..8.JPG`) · meubles bois massif faits main (étagères, bibliothèques, tables de chevet, tables basses, consoles) · bois mindi/acajou, finitions roasted coffee/naturelle/pearl brushed · « L'élégance du bois » / « Créé pour durer, pensé pour vous » | **LIVE https://hh-design.pages.dev** — **REFONTE TOTALE v2 2026-07-04** (crème sable + bois + or vieilli + espresso, **Cormorant Garamond + Archivo**) : hero bois brut Ken-Burns · manifeste espresso 3 piliers · **collection filtrable des VRAIES pièces** (Ayula/Leon/Cancun/Tabasco/Natura/Console) en cartes « spécimen » → **fiche modale** (specs + WhatsApp pré-rempli « commander/sur-mesure ») · bande ambiance · **matières & finitions** (4 échantillons bois) · sur-mesure 4 étapes · contact form→WhatsApp · **vraies photos extraites des planches** (WebP ~250 Ko) · affiche A4 + 2 QR (site+WhatsApp) refaites · QC impeccable+node+captures OK · ⚠️ v1 immobilière (blanc/or/noir Marcellus) OBSOLÈTE · reste : **confirmer n° WhatsApp** + vrai logo + handle IG + adresse Maps + prix | **+229 01 62 68 67 68** (⚠️ à confirmer · issu des planches HH · remplace l'ancien 0167975626) |
| 09 | Au Braisé d'Or | **Au Braisé d'Or** — restaurant **braisé / grillades au feu de bois** à Cotonou (« De Paris à Cotonou » · cuisine africaine/européenne/américaine) · **catalogue digital** = menu commandable (1er catalogue-resto NEBULA) · + traiteur & place des fêtes | **LIVE https://au-braise-dor.pages.dev** (Cloudflare Pages `au-braise-dor`, déployé 2026-07-20) · direction **braise premium sombre** (charbon + ember + or + **verre fumé/glassmorphism**) · **48 plats = 48 photos IA DANS les cartes** (générées **z_image 0,15 cr** après A/B vs nano/Recraft — regardées et jugées meilleures ; WebP 900px ~72 Ko ; photo + prix en pastille verre + **clic carte → fiche commande avec photo**) · galerie séparée supprimée · **moteur de commande** (panier + taille/accompagnement/qté + sur place/emporter/livraison → WhatsApp structuré, déjà en place) · **vidéo héro = intro douce autoplay** `hero.mp4` (scroll-scrub « décomposition » tenté puis **abandonné** car ne défilait pas) · FAB WhatsApp brillant retiré · ambiance sonore braise · légal RC RB/COT/24 A 102350 · IFU 0202501441177 · ⚠️ CSS/JS **inline** (pas de `?v=`) · reste : **affiche A4+QR (PHASE 7, pas encore faite)**, confirmer n° WhatsApp, photo du lieu, adresse/Maps, horaires, logo, réseaux, vrais avis · détail complet `clients/09-au-braise-dor/CONTEXT.md` | 0156057157 (à confirmer, vs 43 99 29 29 enseigne) |
| 10 | Hillary | **HILLARY M. STYL** — maison de couture (monogramme H.M.S) · prêt-à-porter par tailles **+ sur-mesure** · magenta `#E6007E` + noir, Archivo + Manrope | **EN LIGNE : https://hillary-m-styl.pages.dev** ✅ **la V3 « LE FIL » EST en ligne ET sur `main`** (vérifié le 2026-08-06 : `vitrine.html` et la page servie sont identiques octet pour octet, empreinte `3d769e1c`) · vitrine + moteur de commande livrée 2026-07-31, refaite en V2 le même jour · ⚠️ **on édite `_vitrine_src.html`, jamais `vitrine.html`** (généré par `python3 _build.py`, 177 Ko ; QC = `python3 _qc.py`, **71 contrôles**) · **🚀 DÉPLOIEMENT depuis `main` : `clients/10-hillary-m-styl/DEPLOIEMENT.md`** ; `python3 _predeploy.py` vérifie tout et refuse un déploiement douteux · ⛔ **la branche `claude/github-repo-context-nisd2r` est PÉRIMÉE : la fusionner supprimerait 30 790 lignes de `main`** (tout PISTE, `purger.py`, `rapatrier.py`) · **V2 = les mesures dépendent du TYPE DE VÊTEMENT, pas du genre** : robe coupée à la taille **9**, robe droite **15**, robe ovale **11 ⚠️ à valider par l'atelier**, pantalon **6**, chemise/haut **8** (champs regroupés haut/longueurs/manches ; une mesure vide part en « à prendre ensemble », la moitié suffit pour avancer ; pièce « Création libre » = le client choisit le vêtement) · **prix ET délai sur chaque carte**, catalogue 2 colonnes mobile · **express 1 à 3 jours** / normal 7-14 · **date précise de disponibilité affichée** dès les options validées, calculée sur la **borne haute** du délai + acheminement du pays (promettre la borne basse fabrique un client déçu) · **WhatsApp OU email** (un des deux suffit) · **Mobile Money seul moyen de règlement**, aucun paiement sur le site · À propos · double notification expliquée · message d'aide mesures mot pour mot · QC : 0 débordement 390/768/1440 page+modale, 0 erreur JS, cibles ≥44px, 0 image externe · ⚠️ **8 informations à confirmer avant mise en ligne** (bloc « ZONE À COMPLÉTER » en haut du script, §6 du CONTEXT.md) frais+acheminement par pays, **mesures robe ovale jamais fournies** · paiement Momo réel = FedaPay + notifications auto = n8n/Twilio, hors périmètre du statique · **V3 « LE FIL » 2026-08-01** = direction artistique complète, moteur inchangé : **Bodoni Moda** (didone mode) + Archivo + Manrope, fond encre `#0B0A0C` / papier `#F4F1EC` / magenta, rythme sombre-clair alterné · **une animation signature par section, toutes tirées du métier** (rideau d'ouverture au fil · héros titre-craie + **croquis de robe qui se dessine** + mètre-ruban gradué · 01 la piqûre · 02 le patron à la craie · 03 le fil qui relie · 04 le drapé + chiffres comptés · 05 la coupe aux ciseaux · modale = carnet + date tamponnée) · permanent : grain, fil de progression, **aiguille-curseur aimantée**, ruban défilant · ⚠️ **pas de photos IA pour le catalogue** (promesse fausse) — héros prêt à recevoir une vraie photo · perf : `prefers-reduced-motion`, grain figé + 1 nappe retirée sur mobile, **contrôle auto « aucune animation infinie sous backdrop-filter »** · **🚀 V4 « LA COUPE » CONSTRUITE ET EN LIGNE le 2026-08-06** (spec `BRIEF-V4.md`, fusion de 3 références) : loader qui se fend · **héros slider éditorial** avec **numéro géant DERRIÈRE la silhouette** et le nom qui la chevauche (⚠️ ne marche QUE sur fond blanc uni) · **4 badges flottants** · coverflow des collections · **lookbook à compteur fixe + mosaïque en parallaxe** · processus qui se remplit · **74 contrôles verts**, moteur de commande INTACT · ⛔ **ZÉRO bibliothèque** là où le brief demandait Next.js/GSAP/ScrollTrigger/SplitText/Lenis/Swiper · ✅ pagne tranché : « elle fait tout, la maison mère » → le wax est une **matière et une collection, pas l'identité** ; **magenta = sa signature** ; « Collection Kente » abandonné (ghanéen) · ⚠️ **chaque accent wax n'est lisible que sur UN seul fond** (ocre 2,2:1 sur papier ⛔, indigo 1,26:1 et vert 1,77:1 sur noir ⛔) · ⚠️ **on édite `_v4/*` puis `python _v4/_assembler.py`**, jamais `_vitrine_src.html` à la main ; les 4 morceaux `garde-*` (modale, toucher, **moteur**) ne sont JAMAIS régénérés · 📸 **`IMAGES-A-FOURNIR.md`** = ce qu'il faut d'Hillary, niveau par niveau (⭐ carrousel 6-8 d'abord, puis héros 4 **fond blanc uni impératif**, lookbook 6-12, atelier 3, vidéos) · ⚠️ le catalogue reste **12 pièces d'EXEMPLE** : une cliente peut commander une « Robe Amazone » qui n'existe pas, c'est le point le plus urgent | **+229 51 37 47 93** ✅ posé et EN LIGNE (`wa.me/22951374793`, donné 2026-08-01 · ⚠️ tester une fois : le dépôt a 2 formats, sinon `2290151374793`) |
| 11 | Angélique AVOCEVOU | **ANGY ART** — **artiste plasticienne** · Cotonou · œuvres contemporaines en relief sur l'identité, la mémoire et le patrimoine africain (scarifications, symboles, masques, textiles) · portfolio + moteur de demande | **LIVE https://angy-art.pages.dev** (Cloudflare Pages `angy-art`, déployé 2026-08-05) · direction **éditoriale noir `#0a0a0a` / crème `#f3efe6`** demandée par Mongazi (réf. « Selva Toscana ») : **Playfair Display + Public Sans**, italiques dorés, curseur suiveur, défilement lourd, **carrousel coverflow**, modale de demande → WhatsApp rédigé · ✅ **VRAI LOGO POSÉ** (glyphe or détouré : nav, pied, modale, favicon, OG, affiche) + son accroche officielle **« Inspiré d'en haut, enraciné ici. »** · **l'or du site est SON or `#bd9f64`** (relevé sur le logo, 7,8:1 sur noir) ; ⚠️ sur le crème il tombe à 2,2:1 → `#7e6d3a` pour tout ce qui est sur clair · **ZÉRO bibliothèque** là où le brief demandait Next.js/GSAP/Lenis/Swiper, tout réécrit en natif · **13 visuels générés** (WaveSpeed / Nano Banana Pro, 2,80 $) = 5 scènes + **8 œuvres de PRÉFIGURATION** ⚠️ titre et technique seulement, **aucun prix ni dimension**, elles partent à l'arrivée des vraies photos (message de prise de vue prêt dans `PROMPTS-IMAGES.md`) · citation signée **d'Angélique**, jamais d'un critique inventé · **67 contrôles** (`python _qc.py --voir`) · affiche A4 + 2 QR décodés · reste : **photos réelles des œuvres**, adresse, vrais avis, **confirmer le n° WhatsApp** · détail `clients/11-angy-art/CONTEXT.md` + `DESIGN.md` | **+229 01 52 00 64 90** (⚠️ à tester une fois : 8 et 10 chiffres coexistent) |

## Produits internes NEBULA (édités par l'agence, pas des vitrines client)

### Boussole — gestion financière du commerçant  *(SaaS vertical n°1)*
- **Ce que c'est** : l'outil qui dit au commerçant ce qu'il **gagne vraiment**. Il encaisse, Boussole calcule (coût de revient, marge, **3 enveloppes** : relance production / charges / bénéfice net) et **lui parle** (avis honnêtes, leçons d'argent, alertes).
- **Cible** : tout commerçant d'Afrique de l'Ouest (nourriture, produits importés, services…). Devise FCFA. Doit rester utilisable **« par un enfant de 5 ans »**.
- **Où c'est** :
  - **prod** `boussole/` → https://boussole-19d.pages.dev (Cloudflare Pages, projet `boussole`)
  - **proto en cours** `boussole/_proto/app.html` + `connexion.html` → preview branche `proto` : https://proto.boussole-19d.pages.dev/_proto/connexion
  - ⚠️ **Tout le développement se fait sur le PROTO** ; l'app prod n'est PAS encore migrée (intégration finale = vague à venir).
- **Direction artistique** : « **ORANGE & NUIT** » depuis le 2026-08-02 — orange signature `#ff8a1e` sur noir chaud `#0a0a0c`, **deux thèmes** (sombre et clair `data-theme="light"`), cartes très arrondies, aplats pleins, boutons pilule. Police Bricolage Grotesque. Toutes les couleurs passent par des **jetons** (`--acc`, `--good`, `--fg` en composantes RVB) : c'est ce qui rend le thème clair possible, dans le CSS **et** dans les couleurs générées par le JavaScript. *(Avant : « verre de nuit » or ambre + émeraude. Le skin Spider-Verse avait été essayé puis retiré le 2026-07-21.)*
- **Publication** : `python boussole/_outils/_build_dist.py` puis `wrangler pages deploy boussole/_dist --project-name boussole --branch main`. ⚠️ `sw.js` (**kill-switch** du service worker) et `_headers` vivent dans `boussole/_deploy/` — ils n'étaient nulle part dans le dépôt avant le 2026-08-02, et un redéploiement les aurait effacés.
- **Charte de couleur des actions** : **or = action primaire** (Enregistrer, valider) · **rouge = destructif uniquement** (Supprimer) · vert = encaisser. Ne jamais mettre un bouton de validation en rouge.
- **Stack** : HTML/CSS/JS pur (aucun build), **Web Audio** synthétisé (aucun fichier son), **Supabase** (auth + table `boussole_proto_etat` en jsonb + RLS — voir `boussole/_proto/etat.sql`), stockage local `sm:state`, PWA offline-first côté prod.
- **Règles Boussole** :
  - **Jamais de données de démo imposées** : l'onboarding propose « mes vraies données » (zéro) ou « explorer la démo » (`SM.meta.demo`).
  - **Toute suppression doit être annulable** (toast « Annuler »).
  - **Aucune animation infinie sous un `backdrop-filter`** (leçon latence 2026-07-21) et **jamais de `transform` sur un écran contenant un `position:fixed`** (leçon FAB 2026-07-25).
  - Édits du fichier via **scripts Python/Node UTF-8**, `node --check` du module inline, puis **suite QC Playwright** avant tout déploiement.
- **QC** : suites cumulatives `qc_v4` → `qc_v9` (données/métier, coffre+coûts, transitions, accueil, salutations+sons, sweep UI mobile+PC). **Toutes doivent être vertes** avant déploiement.
- **Reste à faire** : Agenda · comparateur de 2 périodes · vague 2 des transitions (Bilan-ECG, Stats-constellation, Carnet, Factures, Équipe, Réglages) · exécuter `etat.sql` dans Supabase pour activer la synchro · migration proto → app live.
- Détail complet : `boussole/README.md` + `_memoire/conversations/2026-07-25-boussole-*.md`

### PISTE — vendre des prospects d'entreprise  *(SaaS vertical n°2)*
- **Ce que c'est** : le client dit qui il cherche, PISTE lui livre un **carnet
  de prospects réels**, avec le message déjà écrit pour chacun. Pas un fichier :
  un carnet de travail qu'on ouvre au téléphone, où on appuie, et la
  conversation WhatsApp démarre.
- **En ligne** : https://piste.nebula-agency.online · cockpit `#/cockpit` ·
  carnet client `#/carnet/<jeton>` · reçu `#/recu/<jeton>`
- **Qui achète** : celui qui vend AUX commerçants (grossiste, assureur,
  fournisseur, banque, agence). ⚠️ **Pas les partenaires NEBULA.**
- **Le barème** : **100 F la fiche, 250 F maximum tout compris.** Quatre
  suppléments qui valent exactement 150 F réunis (numéro testé +60 · pas de
  site +40 · dirigeant +30 · message écrit +20). Minimum 10 fiches,
  exclusivité 90 jours, livraison 24 h, **MTN MoMo seul**.
- **Le vivier** : 7 817 fiches (Bénin, Togo, Côte d'Ivoire), 18 métiers. Le
  moteur tourne **chaque nuit sur GitHub Actions**, gratuitement.
- **⚠️ La marchandise n'est JAMAIS dans le dépôt** : `allonebiao2/nebula-agency`
  est PUBLIC. Le dépôt garde les outils, Supabase (schéma `piste`) garde les
  données. Les numéros d'aperçu sont **coupés à la source**, pas masqués à
  l'affichage.
- **Les outils** (sur le PC, jamais dans le site) :
  `python piste/_moteur.py --voir|--collecter` · `python piste/_carnet.py …
  --ecrire` · `python piste/_carnet.py --relances` · `python piste/_stock.py`
- **Le contrôle** : `_qc.js` + `_qc_generateur.js` + `_qc_carnet.mjs`, tous
  verts avant déploiement. ⚠️ Ils LISENT le stock et les libellés dans les
  données : ne jamais y recopier un chiffre ou un nom de métier.
- **Source de vérité : `piste/PRODUCT.md`**, 88 décisions.

## Infrastructure — où tourne quoi (2026-08-02)

| Ce qui tourne | Où | Notes |
|---|---|---|
| Les 12 vitrines et outils | **Cloudflare Pages** | un déploiement est un **instantané complet** : ce qui manque sur le disque disparaît du site |
| **Bureau des partenaires** | **Render** (`srv-d9nni7e7bikc73c9oksg`) + **Supabase** (schéma `naff`) | Railway a fait disparaître l'app le 2026-08-01, données de prod perdues |
| Le domaine des partenaires | relais Cloudflare Pages `nebula-partenaires` | change d'origine sans toucher au DNS |

⚠️ **Railway est abandonné** (exige une carte). ⚠️ **Le VPS Hostinger `72.61.103.56`
n'appartient plus à Mongazi** (certificat au nom de `api-preprod.normly.fr`) : ne jamais y
toucher. ⚠️ **L'auto-déploiement Render ne marche pas** (dépôt branché par URL publique) :
`POST /v1/services/{id}/deploys`. Clés dans `secrets/` : `render.env`, `supabase.env`,
`nebula-affilies.env` (miroir des variables du service), `cloudflare.env`.

**Les robots des IA sont autorisés** sur les 4 domaines depuis le 2026-08-02. Cloudflare les
bloque **par défaut** ; le réglage `ai_bots_protection` n'existe nulle part dans le tableau de
bord, il faut `PUT /zones/{zone}/bot_management` avec un jeton portant `Zone · Bot Management`.
À vérifier sur **chaque nouveau domaine**.

## 🟢 OÙ ATTERRIT LE TRAVAIL — règle absolue, toutes machines

**Tout finit dans `main`, sur `github.com/allonebiao2/nebula-agency`. Il n'y a pas d'autre
endroit.** Que la session tourne dans le terminal de Cotonou, sur le téléphone de Mongazi ou
sur claude.ai/code, le travail n'existe que lorsqu'il est **dans `main`**.

⚠️ **Claude Code sur téléphone et sur le web travaille sur une branche `claude/…`.**
Cette branche **n'arrive jamais dans `main` toute seule**. Le 2026-08-02, neuf branches
s'étaient accumulées, dont une qui portait **toute la refonte des commissions** : sans un
coup d'œil au hasard, personne ne l'aurait su.

### Ce que fait CHAQUE session avant de se terminer

1. `git fetch origin && git merge origin/main` — **récupérer `main` AVANT de fusionner vers
   lui.** `main` bouge pendant qu'on travaille, c'est le piège n° 1 de ce dépôt.
2. `git diff --stat origin/main..HEAD` — rien d'étranger au chantier ?
3. **Fusionner dans `main` et pousser.** Si la session ne peut pas (sandbox), elle **le dit
   explicitement** à Mongazi, avec le nom de sa branche.
4. **Dispatcher la mémoire**, comme d'habitude : `_memoire/conversations/[date]-[sujet].md`,
   le journal, le `CONTEXT.md` du client, `_memoire/lecons.md` si on a appris quelque chose,
   et cette page si une règle change. Voir « RÈGLE AUTOMATIQUE — MÉMOIRE ET DISPATCH ».
5. **Redéployer** ce qui est concerné (voir « Infrastructure »). Un `git push` ne déploie
   **rien** tout seul, ni sur Cloudflare Pages ni sur Render.

### Au DÉBUT de chaque session, en une commande

```bash
python scripts/rapatrier.py
```

Il liste ce qui traîne sur les autres branches, dit si la fusion passerait sans conflit, et
signale celles qui touchent du sensible (contrat, socle commercial, `server.py`,
`_worker.js`, `secrets/`, ce fichier). Avec `--fusionner`, il rapatrie.

⚠️ **Ne jamais fusionner en bloc sans regarder.** Certaines vieilles branches ressusciteraient
des fichiers obsolètes : celle de mai 2026 renommerait le site en `v7`, une autre rajouterait
une configuration Fly.io abandonnée. Le script montre, l'humain tranche.

## Bureau des partenaires — la bibliothèque de documents (2026-08-03)

**Les 10 PDF que tout partenaire doit avoir sont rangés DANS LA BASE, en base64**,
jamais sur le disque : celui de Render s'efface à chaque déploiement, et c'est ce
qui avait tué les deux anciens PDF (référencés en base, fichiers disparus).

Pour en publier un nouveau, ou une nouvelle version : poser le fichier dans
`nebula-affilies/assets/docs-partenaires/` et **changer sa version** dans
`DOCS_PARTENAIRES` (`server.py`). Sans changement de version, `publier_documents()`
ne rejoue rien. Il ne touche jamais un document ajouté à la main depuis le cockpit
(marqueur `url = 'nebula:socle'`).

⚠️ **`00-SOCLE-COMMERCIAL` et `01-AVIS-DE-RECRUTEMENT` restent INTERNES** : ils ne
vont jamais dans la bibliothèque des partenaires.

⚠️ **Supabase, dans tout code qui parle à la base** : `prepare_threshold = None`
est obligatoire avec le pooler (port 6543), y compris dans un script d'un soir.
Et **une connexion par requête HTTP**, jamais une par fonction : une connexion
coûte 1,3 s, contre une microseconde sur SQLite. C'est ce qui donnait l'écran noir.

## Quand un site s'affiche « tout cassé », sans style (2026-08-04)

**Cloudflare a mis une erreur en cache À LA PLACE d'un fichier.** C'est arrivé
à PISTE : la feuille de style répondait `200`, bon type, bonne taille, et son
contenu était `error code: 502`. Nos fichiers portent `Cache-Control: immutable`
pour un an, donc l'erreur était servie pour un an.

```bash
python scripts/purger.py --verifier     # regarde le CORPS des fichiers servis
python scripts/purger.py                # vide le cache des 5 hôtes
python scripts/purger.py piste          # un seul site
```

⚠️ **Un 200 ne prouve rien**, il faut lire le corps. ⚠️ **Comparer l'origine
`*.pages.dev` et le domaine** désigne le cache en trois secondes. ⚠️ Les
fichiers compilés de PISTE portent une **marque de déploiement** dans leur nom
pour qu'une erreur en cache ne survive jamais à une publication : à reprendre
sur les autres sites s'ils subissent la même panne.

## 🔴 REPRENDRE UNE SESSION
**Lire `_memoire/REPRENDRE-ICI.md` en premier.** Il dit où on en est, ce qui bloque,
et par quoi commencer. Mis à jour à chaque fin de session importante.

## Force de vente & partenaires (chantier 2026-07-30/31)
- **Source de vérité des prix et des règles : `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`.**
  En cas de différence avec un autre fichier, c'est lui qui a raison.
- 13 documents + 2 outils HTML + 9 PDF dans `_documents/nebula-agency/vente/`
- **L'escalier** : on entre TOUJOURS par le Catalogue à 50 000 F, jamais par la Vitrine.
  Un commerçant méfiant dit oui à 50 k, pas à 150 k. Puis Vitrine, puis Outil métier.
- **Abonnement : 20 000 F / 6 mois, modifications comprises** (remplace les 15 000 F partout)
- **GRILLE UNIQUE ET DÉFINITIVE (2026-08-02)** : **30 %** sur chaque vente · **40 %** dès que
  ses ventes **+ celles de ses filleuls directs** atteignent **3** dans le mois. Rien au-dessus.
  Le taux s'applique à TOUT le mois et **repart à zéro le 1er** : les 40 % se regagnent
  chaque mois
- **Récurrent : 20 % de chaque abonnement**, soit 4 000 F par client et par semestre,
  **À VIE**, même après le départ du partenaire. Ne compte pas dans le palier. C'est la
  contrepartie de la non-sollicitation de 24 mois (contrat art. 11.2)
- **Sans paiement, le site du client est COUPÉ au 8e jour** (7 jours de courtoisie, puis
  hébergement + sécurité interrompus, données gardées 6 mois · contrat art. 6.2 bis).
  Frais de réactivation 5 000 F, sans commission. Le partenaire relance une semaine avant
  l'échéance : c'est un fait technique qu'on annonce, jamais une menace qu'on brandit
- **Contrat partenaire en version 1.2** (2026-08-02). Un partenaire encore en 1.1 doit
  recevoir un préavis écrit de 30 jours avant toute baisse de barème (art. 6.7)
- ⛔ **AUCUNE COMMISSION DE RÉSEAU, à aucune profondeur.** Un parrain ne touche **rien** sur
  ses filleuls : leurs ventes comptent seulement dans son **seuil de 3**. « Personne ne gagne
  d'argent sur le dos de personne » est littéralement vrai
- ⚠️ **La relance des renouvellements reste critique** : les clients d'un partenaire parti
  n'ont plus personne pour les relancer. C'est l'automatisation n8n qui porte cette collecte
- Le rôle **superviseur** ne commande plus de barème : la grille unique l'a remplacé, il ne
  reste qu'un insigne
- **Rangs renommés le 2026-08-02** (titres de vraie société, insignes inchangés) :
  Partenaire Junior · Conseiller · Conseiller Confirmé · Conseiller Senior · Chef de
  Secteur · Chef Régional · Directeur Commercial · Directeur Associé · Président Fondateur
- **Versement des commissions : 24 à 72h** après réclamation
- **Barème révisable** avec préavis de 30 jours, sur les ventes futures (art. 6.7) ·
  **le client appartient à NEBULA** (art. 7.4) · **indemnités forfaitaires** en cas
  d'encaissement direct ou de démarchage (art. 8.13)
- ⛔ **Aucun tiret cadratin dans les documents** : ça fait IA et ce n'est pas professionnel.
  Deux-points, virgule, point médian `·` dans les titres
- **Reprise de commission** si un encaissement est remboursé (contrat art. 6.7) —
  sauf si le remboursement vient d'une faute de NEBULA : le partenaire garde alors sa commission
- Vague 1 : **Cotonou, 8 places**, objectif 30 ventes / 90 jours
- Rubrique marketing **« LE SAVIEZ-VOUS ? »** : `_documents/nebula-agency/marketing/`

## 🎨 STANDARD OBLIGATOIRE — toute vitrine, tout client, à partir du 2026-08-01
**Avant d'écrire une ligne de CSS : lire `_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`.**

- **Une vitrine n'est pas finie quand elle marche. Elle est finie quand elle impressionne.**
  Le QC vert et la beauté sont **deux** critères de sortie, pas un.
- **La phrase d'abord** : ce qu'est ce métier vu de l'intérieur, en une ligne, avec un
  **objet concret** dedans (« une maison de couture, c'est un *fil* qui va du mètre-ruban
  au vêtement »). Toutes les animations sortent de cet objet. Sans phrase, on décore.
- **Une animation signature DIFFÉRENTE par section, tirée du métier.** Si elle pourrait
  être copiée-collée chez un autre client, elle est à refaire.
- **Les 3 choses qui font 80 % de l'écart, et aucune n'est une animation** : la typo
  display à caractère et à gros corps (choisie **par registre de métier**), le **rythme
  alterné sombre/clair** des fonds, et le **vide** qu'on ose laisser. Jamais `#000`/`#fff`
  en fond : une encre, un papier.
- ⛔ **INTERDIT ABSOLU : une photo produit générée par IA présentée comme le catalogue du
  client.** Aucune exception. Ambiance/texture : autorisées. Sans photos → dessin au trait
  animé en SVG + cartes « photo à venir », et le héros prêt à recevoir la vraie photo.
- **Regarder les captures, section par section, en 390 ET 1440**, avant de dire « fini ».
  Six défauts sont passés au travers de 53 contrôles verts sur la vitrine Hillary.
- **Source / construction / livrable** : on édite `_vitrine_src.html`, `_build.py` génère
  `vitrine.html` (**jamais édité à la main**), `_qc.py` doit être vert avant déploiement.
  Gabarits : `_memoire/procedure-vitrine/templates/`.
- **Perf** : `prefers-reduced-motion` · grain figé et une nappe en moins sur téléphone ·
  **aucune animation infinie sous un `backdrop-filter`** · **jamais de `transform` sur un
  écran contenant un `position:fixed`** · **aucune bibliothèque**.

Référence d'exécution : `clients/10-hillary-m-styl/` (direction « LE FIL »).

## Mémoire générale
- Voir _memoire/cerveau.md pour contexte complet
- Voir _memoire/lecons.md avant de commencer un nouveau projet
- Voir _knowledge/ pour les compétences techniques

## Mémoire vivante — Règles importantes
- Après chaque session de travail : mettre à jour _memoire/conversations/ avec un log
- Quand on apprend une nouvelle technique : l'ajouter dans _memoire/apprentissages/
- Quand on change de méthode de travail : mettre à jour _memoire/evolution/methodes.md
- Cette mémoire sert à la fois dans GitHub ET Obsidian

## RÈGLE AUTOMATIQUE — MÉMOIRE ET DISPATCH
Après CHAQUE modification importante ou grande avancée :
1. Créer ou mettre à jour le fichier `_memoire/conversations/[date]-[sujet].md`
2. Dispatcher les infos aux bons fichiers :
   - Nouveau produit → CONTEXT.md du client concerné
   - Nouvelle technique → _memoire/apprentissages/
   - Décision prise → _memoire/decisions.md
   - Modification vitrine → CONTEXT.md du client
3. Demander à Mongazi : « Voulez-vous que je sauvegarde cette avancée en mémoire ? »
4. Attendre la confirmation puis commit + push

Ne jamais terminer une session importante sans proposer la sauvegarde mémoire.

## Commandes rapides
- "nouveau client [nom]" → créer dossier + CONTEXT.md
- "checklist [client]" → vérifier avant livraison
- "bilan session" → mettre à jour _memoire/decisions.md
