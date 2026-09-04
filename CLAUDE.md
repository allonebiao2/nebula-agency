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
- **Montage vidéo : Remotion 4.0.512**, dans **`_studio-video/`** (jamais à la
  racine du dépôt). Une vidéo est un programme : on change une question, on
  relance, la vidéo est refaite à l'identique. Les trois séries TikTok
  « oui / non » y sont montées à partir des cartes de `_cartes.py`.
  ⚠️ **Licence** : gratuite tant que NEBULA emploie **3 personnes au plus**,
  usage commercial compris, **mais on livre le MP4, jamais le projet** (si le
  client détient la propriété intellectuelle, les effectifs des deux sociétés
  s'additionnent et la licence lui incombe). ⚠️ **La licence change en 5.0** :
  la version est figée, ne pas faire `npm update` sans la relire.
  ⚠️ Sur ce PC, garder `setDelayRenderTimeoutInMilliseconds(120000)` dans
  `remotion.config.ts` : à 30 s le rendu meurt avant que Chrome ait démarré.
  ⛔ **Ce réglage ne couvre PAS le démarrage du navigateur**, qui a son propre
  délai de 25 s **écrit en dur** dans `@remotion/renderer/dist/open-browser.js`
  et qu'aucune configuration n'atteint. Au premier rendu après une
  réinstallation, lancer une fois
  `node_modules/.remotion/chrome-headless-shell/win64/chrome-headless-shell-win64/chrome-headless-shell.exe`
  à la main : Defender scanne les 270 Mo, retient son verdict, et tous les
  rendus suivants passent. ⚠️ **`rotate: 12` en nombre nu sort en `rotate:12px`,
  donc invalide et ignoré sans un mot** (React n'a que `scale` dans sa table
  des valeurs sans unité) : toute rotation s'écrit avec son `deg`.
  Le studio porte aussi **la démonstration vidéo de MINUIT** (`minuit-demo`,
  30 s, six plans). Détail : `_studio-video/README.md`.
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
| 09 | Au Braisé d'Or | **Au Braisé d'Or** — restaurant **braisé / grillades au feu de bois** à Cotonou (« De Paris à Cotonou ») · **catalogue digital** + traiteur & place des fêtes | **LIVE https://au-braise-dor.pages.dev** · ⚠️ **DEPUIS LE 2026-08-12 LE SITE N'EST PLUS `index.html`** : l'adresse sert le projet **Next.js de `clients/09-au-braise-dor/experience/`** (Next 14 + TypeScript + Tailwind + **GSAP/ScrollTrigger/CustomEase + Swiper + Lenis**, pile demandée par Mongazi ; j'avais recommandé le natif, il a maintenu ; **179 kB de JS** au premier chargement). `index.html` reste dans le dépôt, un retour arrière est un déploiement · **expérience à 4 plats signature** (défilement **automatique** 5,5 s, assiettes détourées qui **ROULENT sur un arc**, titre en deux lignes qui se dédouble, carte de verre, prix qui compte de 0, carrousel Swiper, **tiroir des 8 univers** ouvert depuis le héros) **puis les 48 plats commandables** (toujours tous affichés : le filtre en cachait 38 ; chips en ancres + scroll-spy ; fiche taille/accompagnement/quantité ; panier ; message WhatsApp rédigé) · ⛔ **NI NOTE, NI CHEF, NI LIKES INVENTÉS** (la référence en affichait ; le carré coloré porte **le prix**, qui est vrai) · ⚠️ **7 pièges documentés** : `background-image` non différable (4,3 Mo avant le menu), **`gsap.from()` laisse l'élément invisible si on l'interrompt**, `fixed` qui ne se décolle jamais, pourcentages de hauteur sur téléphone, `width:auto` = boîte de zéro, **conteneur plein écran qui avale les clics**, et **LENIS QUI INTERROMPT TOUT `scrollIntoView`** (saut arrêté à 7 382 px de sa cible) · ⚠️ **une vidéo de référence se MESURE image par image** · publier = `npm run build` + `cp -r ../assets/docs out/` + `wrangler pages deploy out` · ✅ affiche A4 + 2 QR faite · **VAGUE 2026-08-26 — LES 52 PLATS ONT LEUR PHOTO** (plus une seule ardoise) : 9 assiettes posées ou refaites · ⚠️ **les fichiers reçus sont TOUJOURS opaques** (celui qui montre un damier est un JPEG, damier peint dans les pixels ; le `.png` est la photo fond noir) · **planche comparative refaite à chaque lot, isnet gagne 6 fois sur 6 sur damier** — mais la refaire a évité de poser **une viande sans assiette** sur la tête de mouton (écart 26 points) · ⛔ **`_photos_sauces.py` mourait en CODE 137 à la 2e photo** (fuite onnxruntime, comme chez Hillary) → **une photo, un processus** · ⚠️ **le réparer a réveillé 2 cartes qu'il n'atteignait plus et les a écrasées** → drapeau de **gel**, et ⚠️ **le gel suit le FICHIER, pas le slug** · ⛔ **une photo portait le nom d'un autre plat depuis le 19/08** : la « graine » était **l'arachide** (beige et crémeuse vs rouge palme, bol cuivré vs assiette octogonale) → réattribuée, sources renommées · ⛔ **le contrôle du bouton du héros mentait déjà sur `main`** : il photographiait l'opacité au milieu d'une animation permanente (mesuré : **max 1,00, pleine opacité 71 % du temps**) → il échantillonne · ⛔ **le QC PLANTAIT sur un `null.click()`** le jour où le dernier plat a eu sa photo, et **2 contrôles sans rapport étaient sur le même clic** : l'ardoise (cas particulier) et **l'accompagnement obligatoire** (règle métier) → séparés, le second reste vert · **`reboucher()`** neuf : cavités + **fentes ligne par ligne** (jamais colonne, on souderait la vapeur), **seuil 8 % mesuré sur les 10 assiettes** · **QC 92 verts / 0 rouge** · ⏳ **« gbata » ou « gbotâ »** à trancher · reste : **vraie photo de la salle**, confirmer n° WhatsApp, vrais avis, adresse/Maps, logo, réseaux · **VAGUE CATALOGUE 2026-08-19** (détail `_memoire/conversations/2026-08-19-braise-catalogue.md`) : carte relue **contre les 5 photos du menu papier**, pas contre `MENU.md` qui n'en est que le résumé → **48 → 52 plats** (les 4 lignes de petit-déj que la maison vend et que le site ne proposait pas : café chaud serré 500, Lipton citron 500, œuf sur plat 1 000, café au lait écrémé 1 000) · ⛔ **le PRIX était illisible sur les 52 cartes** : la pastille n'avait aucune couleur de texte et posait `--encre #1d1a17` sur `rgba(0,0,0,.65)`, **1,1:1 mesuré** → `#f6efe6` sur 70 %, **13,9:1 à 18:1** · **l'ARDOISE** = un plat sans photo porte son nom écrit (⛔ ni cadre vide ni « photo à venir »), et c'est **le mécanisme prêt pour le jour où les 48 images générées sortiront** · **`python _outils/_qc.py` = 30 contrôles** (le client 09 n'en avait aucun) · ⚠️ **pêcheur 6 000 est BON** : `MENU.md` disait « à confirmer », le 6 est lisible en recadrant la photo — **on ne corrige pas une donnée contre un résumé** · ⏳ **napolitaine et oriental ont une 2e taille ABSENTE du site** (prix coupé, commence par 5) et **l'aileron porte une correction manuscrite au surligneur** illisible · ✅ **LES 48 PHOTOS GÉNÉRÉES PAR IA SONT GARDÉES** (z_image, 20/07, avant la règle) — **tranché par Mongazi le 2026-08-20 : « on les garde, oublie ça »**. Héritage assumé, **pas une exception** : la règle du 2026-08-01 reste absolue et aucun nouveau visuel généré n'entre dans un catalogue. ⛔ Sujet clos, ne plus le remonter · **CORRECTIONS DE LA PROPRIÉTAIRE le même soir (note manuscrite)** : prix validés, **13 plats RETIRÉS et la catégorie Desserts ajoutée → 52 → 42 plats** (pizza : napolitaine/oriental/margherita/pili chaud/à la crème/**pêcheur** = 6 sur 10 · grillades : lapin ou mouton frit + viande de caille · burgers : crispy + nugget · cocktails : « tout sauf les jus de fruit » = les 3 alcoolisés) · ⚠️ **RETIRER UN PLAT N'EST PAS SUPPRIMER UNE LIGNE** : la **pizza pêcheur était un des 4 plats signature du HÉROS** (→ remplacée par la paysanne) et **2 notes de catégorie devenaient fausses** (« sauf crispy, nugget » sans crispy ni nugget, « avec ou sans alcool » sans alcool) — les données se régénèrent, **les phrases ne sont vérifiées par rien** · **Desserts (yaourt/glace/cocktail) SANS PRIX** → convention **`p:0` = prix pas encore donné**, la carte affiche « Prix sur demande » et la fiche remplace le panier par « Demander le prix sur WhatsApp » (⚠️ **un article à 0 n'entre JAMAIS au panier** : le total mentirait) · **QC = 62 contrôles**, dont **un par plat retiré** et « aucun prix à 0 F » · ✅ **Mongazi tranche le soir même** : ⚠️ **le MOUTON FRIT RESTE à 3 000 F** — la note disait « Lapin », la ligne du menu dit « lapin **ou mouton** frit », et retirer la ligne entière avait **supprimé un plat que la maison vend** (→ **une ligne de menu avec un « ou » est deux produits**) · le « cocktail » **sort des desserts** (doublon avec les 3 cocktails de fruits à 2 500 F) → desserts = **yaourt + glace**, prix demandés plus tard, « Prix sur demande » assumé · ⏳ 3 questions restantes en bas de `MENU.md` (prix yaourt/glace · aileron · n° WhatsApp) · **VAGUE SAUCES + MISE EN LIGNE 2026-08-19** : catégorie **Sauces (14)** ajoutée avec ses fourchettes de prix et **4 vraies photos de la maison** (gombo, krinkrin, graine, feuille — les 4 sont AU HÉROS, qui ne montre plus que les sauces, détourées par la maison) · ⚠️ **la krinkrin n'était pas mal détourée, elle était RECADRÉE TROP SERRÉ à la source** : mesurer si le sujet touche le bord avant de chercher un masque, sinon redemander la photo, « tout dedans » = le prix le plus cher · **carte à 9 rubriques / 52 plats** · ✅ **PUBLIÉ ET VÉRIFIÉ DANS LE CORPS DE LA PAGE SERVIE** (« Monyo » 0 fois, Napolitaine/Mojito/Crispy/JOQ absents, « Mouton frit » présent, photos 200, fichier absent → **404**) · ⚠️ **`_outils/_qc.py` ne démarrait pas sur le PC** : chemin de navigateur codé en dur pour la machine du nuage, attente fixe de 1,5 s au lieu d'attendre l'élément, et console Windows **cp1252** qui plantait sur un « ≥ » **après** avoir réussi le contrôle → **78 contrôles verts**  · **VAGUE PARTAGE + SEO 2026-08-20** : la vitrine avait tout ce qui se regarde et **rien de ce qui ne se voit pas** → **`og.jpg` en JPEG** (braise + **vraie** photo de la maison, `_outils/_og.py`), `robots.txt` (robots IA autorisés), `sitemap.xml`, et un **`Restaurant` + `Menu` LU dans `CARTE`** (9 rubriques, 52 plats, vrais numéros) · ⛔ **ni note, ni avis, ni adresse de rue, ni horaire inventés** · ⚠️ **UN PLAT A TROIS FAÇONS D'AVOIR UN PRIX** : `pMax` = fourchette (sauces) → `AggregateOffer`, `p2` = 2e taille → 2 offres, `p:0` = pas de prix → aucune offre ; le 1er jet ne lisait que `p` et annonçait **« jusqu'à 5 000 F » quand la carte monte à 6 000** · ⚠️ **l'instrument mesurait le TEXTE au lieu du FOND** (contraste du titre à 1,1:1 sur une image parfaitement lisible : relever le fond AVANT d'écrire dessus → 10,8:1) · **`_outils/_qc_partage.py` = 35 contrôles SANS navigateur** (les navigateurs Playwright ont été supprimés pour le disque : `npx playwright install chromium`, 267 Mo, pour relancer les 76)· détail `clients/09-au-braise-dor/CONTEXT.md` et `_memoire/conversations/2026-08-12-braise-experience-next.md` · **2026-08-21 — LA SCÈNE NE MEURT PLUS AU DERNIER PLAT** : `if (iRef.current >= N-1) return;` arrêtait la rotation DÉFINITIVEMENT, le site avait l'air mort au bout de 22 s ; elle reboucle désormais, ⚠️ avec **un tour de plus sur le dernier plat** avant de remonter (une boucle qui se referme sans respirer ressemble à un bug) · la crainte d'origine (⚠️ `aller()` fait défiler LA PAGE, donc reboucler la fait REMONTER) était **déjà couverte deux fois** : rien ne bouge hors écran, et un geste repousse de 12 s · **VAGUE 2026-08-26 — LES 6 DERNIÈRES PHOTOS, LA GLACE À LA BOULE, ET LE HÉROS QUI DEVIENT LE COMPTOIR** (détail `_memoire/conversations/2026-08-26-braise-heros-sauces.md`) : **6 images générées et posées** (œuf sur plat, café au lait écrémé, café serré, Lipton citron, yaourt, glace ; `_outils/_gen_plats.py`, nano-banana-pro, 0,84 $) sur **ordre explicite de Mongazi** — ⚠️ **exception nommée sur CE client** (produits de commodité, héritage déjà assumé), **la règle du 2026-08-01 reste entière ailleurs** · **prix reçus** : yaourt **600 F**, glace **1 000 / 1 500 / 2 500 F** ⛔ **le modèle ne portait que DEUX tailles** (`p`/`p2`, et la fiche tenait la taille dans un **booléen**) → le 3e palier disparaissait et la maison encaissait 1 500 au lieu de 2 500 → **`paliers: [libellé, prix][]`**, la fiche ne connaît plus qu'un **index** ; ⚠️ **le balisage a maintenant QUATRE façons d'avoir un prix** (`pMax`→AggregateOffer · `p2`→2 offres · `paliers`→N offres · `p:0`→aucune) · **HÉROS : les 14 sauces, il avance seul toutes les 2,8 s (était 5,5), on y commande** ⛔ **le DÉFILEMENT était le moteur** (piste de N×100vh) : à 14 sauces ça faisait **1 400vh**, quatorze écrans avant la carte, et « plus vite » aurait fait **défiler la page toute seule** → **la scène tient sur UN écran**, l'index est un tween sur un nombre, **le mouvement des assiettes n'a pas bougé d'un pixel** ✅ la crainte du 21/08 (« reboucler fait REMONTER ») **n'existe plus**, boucle franche, chemin le plus court sur l'anneau · ⚠️ **Lenis reste** (`aller.ts` en dépend) · ⚠️ **la pause au survol aurait tué le carrousel** : `onPointerEnter` sur une scène qui fait TOUT L'ÉCRAN = il ne repart jamais sur un PC → on ne s'arrête que sur la carte de verre et la bande des miniatures · **`DISHES` est LU dans `carte.ts`** (4 sauces y étaient recopiées avec leur prix = deux vérités), sans photo → **ardoise ronde au filet de la couleur de la sauce** ; ⚠️ **Béchamel et Crème n'auront jamais de découpe** (documenté depuis le 19/08) · **optimisation mesurée** : 14 découpes = 2 Mo → fenêtre glissante (**4 images au 1er écran**), et hors fenêtre une assiette est **rangée une fois** au lieu d'être repositionnée à chaque image · **commander depuis le héros = un PONT, pas un 2e moteur** (`data/commande.ts` : le héros demande, la carte ouvre SA fiche → accompagnement obligatoire, fourchette, panier, message : un seul de chaque) · ⚠️ **la barre du panier recouvrait la scène** → `body.a-panier` + **`--barre-h` MESURÉE** (les rem écrites à la main laissaient 8 px de recouvrement à 390 px) · ⛔ **la carte de verre listait les accompagnements des GRILLADES sous des SAUCES** → lue dans la carte · ⛔ **LE SITE A DEUX NUMÉROS WHATSAPP** : `index.html` `2290156057157` vs `dishes.ts` (**le fichier servi**) `22956057157`, **le `01` a sauté** — rien touché, à trancher · ⛔ **4 DÉFAUTS QUE LE QC VERT NE VOYAIT PAS**, trouvés **sur les captures** (`_outils/_vues_heros.py` photographie les 14 sauces en 390 et 1440) : **`clearProps: "all"` VIDE l'attribut `style`** — le **bouton de commande était INVISIBLE** (fond transparent, texte crème sur verre clair, **1,1:1**), ⚠️ **défaut ANTÉRIEUR, l'ancien bouton vert avait le même sort EN LIGNE**, et le corps du titre calculé par sauce était effacé (**la 2e ligne ressortait plus petite que la 1re**) → `clearProps: "opacity,visibility,transform"` + couleurs fixes dans une **classe** · **l'ardoise ronde sortait de sa boîte de 100 px** à 390 (`inset-0` fixe déjà les 2 dimensions donc **`aspect-ratio` est ignoré**) → conteneur mesuré + `min(100cqw,100cqh)` · **la pile de points se posait sur le texte** sur téléphone → masquée sous 768 px · **les 2 flèches du carrousel étaient posées SUR des miniatures** → `overflow-x: clip` (garder la verticale, sinon l'ombre est rognée) · **QC 64 → 102 contrôles** (+ `_qc_partage` 35 → 36) ⚠️ **2 pannes d'instrument, aucune du site** : le contrôle de débordement mesurait le **X d'une animation GSAP** (GSAP ignore `prefers-reduced-motion`) et accusait « KRINKRIN dépasse de 36 px » → `scrollWidth - clientWidth`, insensible aux transformations ; et le contrôle « ça avance seul » a un **TÉMOIN** avant celui de la pause · **2026-08-27 — SIX PHOTOS LIVRÉES, AFFICHÉES NULLE PART** (détail `_memoire/conversations/2026-08-27-braise-deux-machines.md`) : les six découpes de sauce étaient dans `main` depuis la veille, propres, pesées, en 200 — **et le héros posait quand même son ardoise sur les six**, en plein premier écran ⚠️ **le héros ne lit pas le dossier, il lit le `DECO` de `dishes.ts`** (`img: d?.img`, absent = ardoise) et aucun des 7 commits qui ont posé les images ne l'a touché ⛔ **RIEN NE POUVAIT LE SIGNALER** : le contrôle « 0 image cassée » ne voit que les images **demandées**, et une image qu'on ne réclame jamais ne peut pas être cassée — **un fichier livré n'est pas un fichier affiché** · posé : les 6 `img:` du `DECO`, les 6 correspondances de `index.html`, les images de carte manquantes dans `assets/images/` · **nouveau contrôle** « aucune découpe inutilisée dans /plats » (il lit les DEUX côtés dans les fichiers) · **héros 6 → 12 sauces montrées, 8 → 2 ardoises** (Béchamel et Crème n'en auront jamais) · ⚠️ **LE MÊME TRAVAIL A ÉTÉ FAIT DEUX FOIS** : le PC avait une chaîne complète non commitée pendant que `main` portait déjà le même travail, mêmes sources au bit près — la version de `main` est gardée (rembg/isnet contre une reconstruction d'alpha **déjà mesurée et rejetée** dans `_damier.py`), le commit local `70e3d8b` **écarté** (le garder aurait réécrit en silence les cadrages gelés exprès) | 0156057157 (à confirmer, vs 43 99 29 29 enseigne · ⚠️ **et `dishes.ts` en utilise un AUTRE, sans le `01`**) |
| 10 | Hillary | **HILLARY M. STYL** — maison de couture (monogramme H.M.S) · prêt-à-porter par tailles **+ sur-mesure** · magenta `#E6007E` + noir, Archivo + Manrope | **EN LIGNE : https://hillary-m-styl.pages.dev** ✅ **la V4 « LA COUPE » EST en ligne ET sur `main`** (déployée le 2026-08-06 · image servie comparée en MD5 au fichier du disque : identique, transparence comprise) · vitrine + moteur de commande livrée 2026-07-31, refaite en V2 le même jour · ⚠️ **on édite `_vitrine_src.html`, jamais `vitrine.html`** (généré par `python3 _build.py`, 177 Ko ; QC = `python _qc.py`, **91 contrôles** ; ⚠️ **la V4 se monte depuis `_v4/` : `python _v4/_assembler.py` d'abord**, il refuse d'écrire si l'un des 18 identifiants du moteur manque) · **🚀 DÉPLOIEMENT depuis `main` : `clients/10-hillary-m-styl/DEPLOIEMENT.md`** ; `python3 _predeploy.py` vérifie tout et refuse un déploiement douteux · ⛔ **la branche `claude/github-repo-context-nisd2r` est PÉRIMÉE : la fusionner supprimerait 30 790 lignes de `main`** (tout PISTE, `purger.py`, `rapatrier.py`) · **V2 = les mesures dépendent du TYPE DE VÊTEMENT, pas du genre** : robe coupée à la taille **9**, robe droite **15**, robe ovale **11 ⚠️ à valider par l'atelier**, pantalon **6**, chemise/haut **8** (champs regroupés haut/longueurs/manches ; une mesure vide part en « à prendre ensemble », la moitié suffit pour avancer ; pièce « Création libre » = le client choisit le vêtement) · **prix ET délai sur chaque carte**, catalogue 2 colonnes mobile · **express 1 à 3 jours** / normal 7-14 · **date précise de disponibilité affichée** dès les options validées, calculée sur la **borne haute** du délai + acheminement du pays (promettre la borne basse fabrique un client déçu) · **WhatsApp OU email** (un des deux suffit) · **Mobile Money seul moyen de règlement**, aucun paiement sur le site · À propos · double notification expliquée · message d'aide mesures mot pour mot · QC : 0 débordement 390/768/1440 page+modale, 0 erreur JS, cibles ≥44px, 0 image externe · ⚠️ **8 informations à confirmer avant mise en ligne** (bloc « ZONE À COMPLÉTER » en haut du script, §6 du CONTEXT.md) frais+acheminement par pays, **mesures robe ovale jamais fournies** · paiement Momo réel = FedaPay + notifications auto = n8n/Twilio, hors périmètre du statique · **V3 « LE FIL » 2026-08-01** = direction artistique complète, moteur inchangé : **Bodoni Moda** (didone mode) + Archivo + Manrope, fond encre `#0B0A0C` / papier `#F4F1EC` / magenta, rythme sombre-clair alterné · **une animation signature par section, toutes tirées du métier** (rideau d'ouverture au fil · héros titre-craie + **croquis de robe qui se dessine** + mètre-ruban gradué · 01 la piqûre · 02 le patron à la craie · 03 le fil qui relie · 04 le drapé + chiffres comptés · 05 la coupe aux ciseaux · modale = carnet + date tamponnée) · permanent : grain, fil de progression, **aiguille-curseur aimantée**, ruban défilant · ⚠️ **pas de photos IA pour le catalogue** (promesse fausse) — héros prêt à recevoir une vraie photo · perf : `prefers-reduced-motion`, grain figé + 1 nappe retirée sur mobile, **contrôle auto « aucune animation infinie sous backdrop-filter »** · **🚀 V4 « LA COUPE » CONSTRUITE ET EN LIGNE le 2026-08-06** (spec `BRIEF-V4.md`, fusion de 3 références) : loader qui se fend · **héros slider éditorial** avec **numéro géant DERRIÈRE la silhouette** et le nom qui la chevauche (⚠️ ne marche QUE sur fond blanc uni) · **4 badges flottants** · coverflow des collections · **lookbook à compteur fixe + mosaïque en parallaxe** · processus qui se remplit · **74 contrôles verts**, moteur de commande INTACT · ⛔ **ZÉRO bibliothèque** là où le brief demandait Next.js/GSAP/ScrollTrigger/SplitText/Lenis/Swiper · ✅ pagne tranché : « elle fait tout, la maison mère » → le wax est une **matière et une collection, pas l'identité** ; **magenta = sa signature** ; « Collection Kente » abandonné (ghanéen) · ⚠️ **chaque accent wax n'est lisible que sur UN seul fond** (ocre 2,2:1 sur papier ⛔, indigo 1,26:1 et vert 1,77:1 sur noir ⛔) · ⚠️ **on édite `_v4/*` puis `python _v4/_assembler.py`**, jamais `_vitrine_src.html` à la main ; les 4 morceaux `garde-*` (modale, toucher, **moteur**) ne sont JAMAIS régénérés · ✅ **SES 4 VRAIES PIÈCES REÇUES ET POSÉES le 2026-08-06** (Robe de cérémonie 100k · Ensemble Mira 50k · Ensemble JOSY 65k · Robe de ville 30k, toutes en sur-mesure robe ovale) : elles occupent le **catalogue, le carrousel ET le héros** (détourées au rembg) · les 12 pièces d'EXEMPLE ont disparu · ✨ **la couleur du héros suit le tissu** (teinte dominante relevée sur chaque photo → `--piece` sur `:root`, ⚠️ ne jamais la redéclarer sur `.hero`) · ⚠️ **le supplément express est PROPRE À CHAQUE PIÈCE** (+40k sur 100k, +15k sur 30k) : le moteur appliquait 10k à tout le monde et Hillary absorbait l'écart · délai express aussi par pièce (JOSY 2-5 j, autres 2-4 j) · onglet vide masqué (ses 4 pièces sont toutes en sur-mesure) · prix affichés en **FCFA + € + $** tels qu'elle les donne, jamais recalculés · **9 images d'ambiance régénérées d'après SES tissus** (atelier + lookbook) · ⏳ reste à confirmer : **les 11 mesures de la robe ovale** (les 4 pièces en dépendent), la matière de chaque pièce, le jeu « haut + jupe » de Mira, le libellé « Robe de ville » · détail `_sources/hillary/PIECES-RECUES.md`  · **PASSE DU 2026-08-06** : **une seule photo par pièce**, détourée, partagée par le héros, le carrousel ET les cartes (`piece-*.webp` ; les `coll-*.webp` en double sont supprimés) — sans détourage le chiffre géant du héros était entièrement couvert et chaque pièce tenait dans une boîte blanche · transparence livrée en **WebP `quality=94, alpha_quality=100, exact=True`** = alpha **bit pour bit celui du PNG** pour 761 Ko au lieu de 3 560 Ko (sources PNG dans `_sources/detoure/`) · « 14 à 14 jours » → `libDelai()` n'annonce qu'un chiffre quand les bornes se rejoignent · prix et délais **insécables** (« 100 000 » / « F » se cassait sur téléphone) · **`404.html` écrite par `_predeploy.py`** — sans elle un fichier absent répond **200** et ce 200 se met en cache **un an** (panne PISTE) · **84 contrôles** : alpha réellement transparent lu au pixel, aucun cadre, aucune coupure de ligne, chiffre du héros synchrone · ⚠️ `curl -w "%{size_download}"` a annoncé un poids faux et fait croire à un cache empoisonné : **comparer les octets (MD5), pas les compteurs** · **MOUVEMENT DU HÉROS RÉPARÉ (2026-08-06)** — Mongazi : « ça bugue un peu, surtout sur les chiffres, ça doit suivre » : ⚠️ **`cubic-bezier(.45,.02,.2,1)` partait À PLAT**, la pièce restait immobile **580 ms mesurées** après le clic puis se précipitait → `cubic-bezier(.25,1,.5,1)` sur 1 s · le chiffre géant porte **la même durée ET la même courbe** que la pièce (2 chiffres qui se croisent dans le sens du mouvement) · ⚠️ **le travail lourd ne doit pas précéder le mouvement** (un glyphe de 30 rem = un calcul de mise en page ; `--piece` sur `:root` = un recalcul de tout le document) : `preparerNum()` prépare hors du chemin critique, `aller()` déclenche tout dans **la même image**, couleur et textes à l'image suivante · ⚠️ **verrou et retrait tombaient tous deux à 1050 ms** = une course qui empilait « 0302 » au clic rapide → seule la transition la plus récente fait le ménage · nappe en **`color-mix(in oklab)`** (en srgb un bleu à 22 % sur crème = gris sale) · pied du « 2 » de Bodoni fondu au `mask-image` · héros **jamais en `loading="lazy"`** + `decode()` en fond · ombres coupées pendant le mouvement (`.hsc.bouge`) · mesuré téléphone 4× ralenti : **17 ms au repos, 21 ms en glissant** — ce n'était pas la performance, c'était la courbe · **AUDIT COMPLET 2026-08-06** (9 défauts corrigés) : ⛔ **adresse email INVENTÉE en ligne** (`contact@hillarymstyl.com`) qui servait de vrai `mailto:` au repli « je n'ai pas WhatsApp » — les commandes partaient dans le vide ; `EMAIL` est **vide**, la ligne se retire seule et le repli devient un **`tel:`** vers son vrai numéro · ⛔ le bloc contact annonçait **« 7 à 14 j · 1 à 3 j express »** contre « 2 semaines · 2 à 5 j » sur chaque carte (corrigé partout + badge du héros + valeurs de secours) · ⛔ `.et span{grid-column:2}` frappait aussi le numéro (un `<span>`) : titres dans la colonne de 86 px et **« L'essayage » chevauchait le « 04 »** → `.et>span:not(.n)` ; ⚠️ la spécificité ne prévient pas, `grid-column` n'était déclaré que là · ⛔ **le bouton « Écrire sur WhatsApp » avait `href="#"`** (posé par le script) : sans JS on ne pouvait pas joindre la maison → liens WhatsApp **écrits en dur** · **3 contrastes réparés** : bouton WhatsApp **3,09→5,0** (`#128040` ; le vert de la marque porte du texte FONCÉ), étiquette carrousel 4,13→5,2 (`--rose-f #c9006c`, ⚠️ `--rose` intact = sa signature), badge 4,21→5,9 (`--terre #a8452a`) · **textes d'attente retirés** (« Photo à venir »→« Votre modèle », 6 légendes lookbook) · **menu illisible pendant son fondu** (texte 0,4 s / fond 0,5 s se croisaient au même gris, **1,01:1 mesuré**) → les deux à 0,22 s · lien téléphone porté à 44 px · ✅ vérifié bon : CLS **0,025**, WebKit réel, 0 erreur JS, 0 réponse ≥400, 0 débordement · **PANIER + VENTE 2026-08-16/17** : **un panier** (plusieurs pièces, une seule commande, un seul message) — ligne = `expPrix` si express × quantité, frais de livraison **une seule fois**, ⚠️ **délai = la borne haute de la pièce la PLUS LENTE** (tout part ensemble ; le mélange express/normal est annoncé), **aucun prix stocké dans le panier** (relu dans `PIECES`, sinon un panier oublié ressort à un prix périmé), mesures reportées d'une pièce à l'autre · ⚠️ le voile du tiroir **avalait les clics 350 ms après sa fermeture** (`visibility` bascule à la FIN de la transition → `pointer-events`) · le bouton du son a **son couloir de 78 px** dans les pieds de page (le QC refuse qu'on le cache) · **AUDIT VENTE** : ⛔ **aucune `og:image`** (un lien WhatsApp n'était qu'une ligne grise : le défaut le plus cher, et invisible depuis le site) → `python _og.py` fabrique `og.jpg` **en JPEG** + `google-logo.jpg` 720² + `google-couverture.jpg` 1024×576 · ⛔ **`FAQPage` déclaré sans aucune question visible** → section « Les questions » en `<details>`, et **un contrôle compare le balisage et la page** · **8 fiches `Product`/`Offer` LUES dans `PIECES`** par l'assembleur · `robots.txt` + `sitemap.xml` · meta description qui disait encore « 1 à 3 jours » corrigée + contrôle · ⚠️ `_predeploy.py` ne copiait **que les `.webp`** et **ne lance PAS l'assembleur** · **121 contrôles** · **FICHE GOOGLE : dossier complet dans `GOOGLE-BUSINESS.md`** (nom SANS mot-clé = motif n°1 de suspension, description 665 car., catégories, services, procédure) — ⛔ **impossible à créer d'ici** (son compte Google + validation vidéo) et **bloquée par l'adresse**, qu'elle n'a jamais donnée · **9 modèles reçus le 2026-08-16** notés dans `_sources/hillary/` (prix, délais, mesures) ⚠️ **leurs photos ne sont pas des fichiers**, rien ne se pose tant qu'elles ne sont pas dans `_partage/` · **2026-08-18** : sur ordre de Mongazi, **les 11 modèles sont AU CATALOGUE SANS leurs photos** (9 → **20 cartes**) — nom, description, prix en 3 monnaies, délai, mesures, **commande complète** ; à la place de l'image, le monogramme et **« Photo sur WhatsApp »** (drapeau `photoWa:true`, ⚠️ **jamais « photo à venir »** : ça dit que la maison n'est pas prête) · ⚠️ **ni héros ni carrousel** tant qu'il n'y a pas d'image · vérifié EN LIGNE sur **iPhone (WebKit réel), Android et 360 px** : 12/12 affichées, 0 débordement, 0 erreur, la fiche s'ouvre au toucher · ⛔ **pourquoi les photos n'arrivent pas** : une session lancée DEPUIS LE TÉLÉPHONE tourne dans le nuage et y reçoit de vrais fichiers, une session sur le PC voit l'image sans pouvoir l'écrire (prouvé : `_sources/` ignoré par git + le lot du 10/08 livré sans sources) · `_nouveaux_modeles.py` porte les 11 fiches et **refuse de poser tant qu'une photo manque** · **2026-08-17** : **héros 4 → 7 pièces** et **carrousel 4 → 8** (les 4 reçues le 10/08 n'y étaient jamais passées ; la robe à tulle reste au seul carrousel, son violet doublait) · **une signature par section** (l'ourlet, le portant, les patrons épinglés, le fil qui se dénoue, la couture qui se ferme) + `section{overflow-x:clip}` · ⚠️ **quand le QC échoue, `_predeploy.py` s'arrête AVANT de préparer `_dist/` : déployer juste après republie la version précédente sans un mot** · ⚠️ le QC échouait 1 fois sur 2 sur « Page.goto: Timeout » = **serveur de test mono-tâche** (`TCPServer` → `ThreadingTCPServer`), pas un défaut du site · **2026-08-18 — LES PIÈCES ENVOYÉES EN DOUBLE BASCULENT TOUTES SEULES** (détail `_memoire/conversations/2026-08-18-hillary-deux-vues.md`) : une pièce à deux photos montre **face puis dos**, au catalogue (`img2`) ET au carrousel (`f2`), ⚠️ **hors de l'écran rien ne tourne**, onglet caché ou fiche ouverte **tout se fige ET l'échéance est repoussée** (sans ce report, toutes les cartes rattrapent leur retard d'un coup au retour), **décalage d'une carte à l'autre** (synchrones elles clignoteraient comme une panne), 1re bascule à 1,6 s puis 3,6 s · ⛔ **jamais de bascule vers une image pas encore chargée** (la 2e vue est en `lazy` : sur une 4G on révélerait du VIDE 3,6 s) · ⛔ **le héros ne prend QUE la face** (son glissement réglé au millième le 06/08 ne partage pas la place) · pastille active **plus large**, pas seulement rose · **le héros prend désormais TOUTES les nouvelles** (fini la liste de 3 élues), écrites au format exact des anciennes, et **`poser_heros()` choisit l'ORDRE** pour que deux nappes de même teinte ne se suivent jamais (**écart ≥ 28°, boucle comprise**) — la règle du 17/08 passe dans le code, et **on déplace la pièce au lieu de l'exclure** · ⏳ **2 voisinages de même nappe subsistent PARMI LES 7 DÉJÀ EN PLACE** (`hero-3→hero-4` 19°, `violette→orange` 23°) : intouchés sur ordre de Mongazi, **à trancher** · ⛔ **3 bugs qui auraient fait perdre les photos** dans `_nouveaux_modeles.py` : `injecter()` **sautait les 11 fiches** déjà au catalogue (photos détourées, posées… et jamais raccrochées, sans un mot), **`motion.js` n'était JAMAIS réécrit** (carrousel et héros calculés puis jetés), et les chaînes JS bâties en `'%s'` (1re apostrophe = site cassé) · la légende du carrousel coupait **au milieu d'un mot** · ⚠️ **la règle du tout ou rien est INVERSÉE** : les 11 fiches étant en ligne avec « Photo sur WhatsApp », chaque photo posée est un gain net — attendre la dernière laisse 10 pièces sans image · **QC 121 → 138** (face et dos comparés en **MD5** : deux fois la même photo donne une bascule invisible ; opacité **réellement calculée** ; **témoin** « sous les yeux ça tourne » ; pause hors écran / fiche ouverte ; mouvement réduit ; **2e vue coupée au réseau**) · ⚠️ **3 leçons de contrôle** : un contrôle de PAUSE a besoin d'un TÉMOIN (sinon il passe aussi quand le mécanisme est mort), on **échantillonne** au lieu de comparer 2 instantanés (période 7,2 s = échec au hasard 1 fois sur 5, même famille que le contrôle du 17/08), et un contrôle **nomme** ce qui manque · ⚠️ **faux positif antérieur corrigé** : les 6 `.mp3` échouaient car la boucle ouvre la page en `file://` où Chromium **interdit `fetch()`** — vérifié identique sur `main` · ⏳ **les photos ne sont pas encore arrivées** : `python _nouveaux_modeles.py` dit ce qui manque, `--poser` pose ce qui est prêt · ✅ **PUBLIÉ ET VÉRIFIÉ LE 2026-08-20** : les photos du téléphone (8 modèles, **Robe Soleil**, organza face+dos, sirène, orange uni) sont **en ligne** — page servie **identique au disque (MD5)**, 25 images distinctes, **2 cartes seulement en « Photo sur WhatsApp »** (h8 tulle, h19, h20 Volants) · **héros 16 diapositives**, écart des nappes mesuré en **L\*a\*b\* (ΔE 18)** et non plus en angle de teinte (l'angle ignore clarté et saturation, et fabriquait un problème insoluble) · ⚠️ **un contrôle échouait sur un site sain** : la largeur des pastilles est ANIMÉE, il mesurait un instant qui tombait dans la transition (9,18 vs 10,31 px quand l'écart au repos est de **9,7 px constant**) → il échantillonne 6 fois et garde le meilleur écart · ⚠️ **`npx wrangler` ne marche plus ici** (paquet supprimé avec les `node_modules`, cache npm vidé) → **wrangler 3 installé globalement** · ⚠️ **`npx playwright install` ≠ `python -m playwright install`** : Node épingle 1234, Python veut 1223, **430 Mo téléchargés pour rien** · **2026-08-20 — 9 DES 11 MODÈLES ONT LEURS VRAIES PHOTOS** (détail `_memoire/conversations/2026-08-20-hillary-photos-recues.md`) : restent Robe d'été et Ensemble Volants · **4 pièces basculent face/dos** · **9 prix et 9 types de mesures vérifiés au centime** contre ce qu'Hillary avait donné le 16/08 · ⛔ **2 photos écartées** (la face de la Sirène porte un **emoji ❤️ collé sur la poitrine**) · ⛔ **DÉTOURAGE = `birefnet-general`, PLUS `isnet`** : isnet rendait le train d'organza **gris sale** sur la face et l'**effaçait entièrement** sur le dos (il ne restait qu'un disque rouge flottant) — les tissus translucides sont ce qu'il ne sait pas voir · ⚠️ **un processus par photo** (birefnet se faisait TUER sur la 2e image, code 137, avec 15 Go libres : onnxruntime ne rend pas ce qu'il prend) · ⛔ **la couleur du héros suivait LA PEAU** (bras et jambes nus = 23 % de la photo contre 17 % pour le tissu, la robe verte sortait en BRUN) → on prend **la teinte la plus SATURÉE parmi celles qui occupent ≥ 15 %** ; ⚠️ un détecteur de peau par bande de teinte casserait les tissus orange · ⚠️ **FAUX DÉFAUT SIGNALÉ PUIS CORRIGÉ** : la règle des nappes comparait des ANGLES de teinte et accusait `hero-3→hero-4` (19°) alors que leur écart perçu est de **33 ΔE** — **on mesure en L\*a\*b\*, seuil ΔE 18**, jamais en degrés ; avec l'ancienne mesure aucun ordre parfait n'existait (6 pièces chaudes contre 3 séparateurs) · **héros 7 → 16 diapositives, aucune transition invisible** · ⛔ **3 bourdes de découpe** (virgule après un commentaire « `*/,` » · **tout l'en-tête du fichier effacé** = site muet · **7 fonctions effacées** découvertes après 10 min de détourage) → **`node --check` AVANT d'écrire** + `main()` vérifie ses fonctions avant de lancer ce qui est coûteux · ⏳ **à trancher** : le **sac beige** de l'Ensemble Orange, la teinte **crème** du dos de l'organza (fond jaune vu à travers), et ⚠️ **les originaux ne sont PAS sauvegardés** (`clients/*/_sources/` ignoré, dépôt PUBLIC) · ⚠️ le héros affiche encore **« PRÊT-À-PORTER »** alors que les 20 pièces sont toutes en sur-mesure · **2026-08-21 — PLUS AUCUN TEXTE SOUS UNE IMAGE NI SOUS UN INSTRUMENT** (14 chevauchements trouvés par un détecteur, → 0, aux 3 largeurs) : ⛔ **carrousel** — sous 1180 px `.cars-t` repassait dans le flux mais restait DANS `.cars`, boîte de hauteur fixe dont la piste est `absolute` et couvre tout (**65 % du texte recouvert à 390 px**) → `.cars` devient une colonne, la hauteur passe sur `.cars-p` · ⛔ **le bouton du son mangeait le premier mot** de tout texte passant en bas à gauche (11 endroits) → **il rejoint la barre du haut** (bande de bord opaque) ; ⚠️ `.nav-d` était **entièrement masqué sous 880 px**, on masque ses autres enfants pas le conteneur · ⚠️ **IL CHANGE DE PARENT, PAS DE STYLE** : la barre porte `z-index:50` donc crée un **contexte d'empilement** — de l'intérieur un `z-index:130` VAUT 50 et ne passe pas au-dessus de la fiche (120) ; `parDessus()` le sort de la barre pendant la commande et l'y remet · **contrôle `chevauchements()` aux 3 largeurs** : défaut = texte **dans le flux** recouvert par un élément positionné ; PAS un défaut = texte posé exprès (chiffre géant, légende, badge, « Commander ») car `absolute` — sans cette distinction un 1er jet annonçait **105** défauts ; PAS un défaut = **bande de bord** opaque traversant l'écran, ⚠️ mais une pastille de 46 px n'en est pas une (sans ce resserrement **le détecteur s'excluait lui-même et annonçait zéro**) · **138 → 141 contrôles** · **2026-08-21 — LE CARROUSEL AVANCE TOUT SEUL** (le héros tournait déjà, lui non) : ⚠️ **la durée SUIT LA PIÈCE** — deux vues → **7,4 s** (face, dos, puis on avance), une seule vue → **5,5 s** ; une cadence ordinaire de 4 s aurait fait passer au suivant AVANT que le dos ait eu le temps de se montrer, écrasant un mécanisme par l'autre · s'arrête au survol, onglet caché et **hors de l'écran**, un geste le relance, rien sous mouvement réduit · **VAGUE 2026-08-25** : **Robe d'été posée** (détourée birefnet, vérifiée sur damier, prix vérifiés au franc près) → **19 cartes sur 20 ont leur photo** · ⛔ **la 2e photo envoyée ce jour-là ÉTAIT DÉJÀ EN LIGNE** — au MD5 près le dos de `h10 Robe de ville organza`, qui porte déjà exactement ces six prix → **`h20 Ensemble Volants` est EN DOUTE** (mêmes prix que h10, jamais de photo propre : peut-être un doublon fabriqué le 16/08) ; rien n'est supprimé, la note est à côté de la fiche, ⏳ **seule Hillary peut trancher** · **CARROUSELS PLUS FLUIDES** : ⛔ le héros **jetait les clics** (`occupe` 1 050 ms, sortie silencieuse) → le dernier geste est **retenu** et joué à l'arrivée (mesuré : 2 clics = 2 pas) · ⛔ le 2e carrousel n'avait **JAMAIS reçu la correction du 06/08** (`cubic-bezier(.4,0,.2,1)` part à plat) → même ease-out quart qu'au héros ; **une correction faite à un endroit n'est pas faite partout** · cadences héros 1 s→**.72 s** / 5 s→**4,2 s**, cartes .8 s→**.6 s** / 5,5 s→**4,4 s** (**6,8 s** à deux vues : 3 600 ms sont dus à la face) · ⚠️ **le chiffre géant et la pièce changent de durée ENSEMBLE** · **AUDIT PROFOND** : catalogue, prix, panier, liens et message WhatsApp **sains** (5 suppléments express propres à chaque pièce, délai = la pièce la plus lente, **aucun prix par défaut**) mais ⛔ **AU CLAVIER ON NE POUVAIT PAS COMMANDER** — `role="dialog"` sur un `<div>` n'apporte QUE l'étiquette : focus resté sur `<body>`, **UNE SEULE** tabulation en sortait vers le catalogue caché, rien d'`inert` (un lecteur d'écran lisait les 20 cartes du fond), focus perdu en refermant → les 4 gestes posés sur la fiche ET le tiroir ; ⚠️ **le bouton du son reste dans la boucle** (la maison exige qu'on coupe le son en donnant ses mesures) et **`focus({preventScroll:true})`** partout · ⛔ **le défilement lissé écrasait tout le monde, 3e site** (saut à 200 px ramené à 5 996) : correctif identique à Angy · **QC 141 → 150** · ⚠️ **4 fausses pistes dues à mes sondes** (panier au mauvais format, rideau de 4 800 ms, ce n'est pas un `<dialog>`, le bouton du son) : vérifier sa sonde avant d'accuser le produit · **VAGUE 2026-08-27** : ⛔ **« Ensemble Volants » RETIRÉ — la fiche n'a jamais existé.** C'est **moi** qui l'avais fabriquée le 16/08 en décrivant deux fois la même robe depuis une photo montrée en conversation. Trois preuves : les **six prix identiques** à `h10 Robe de ville organza` (au franc et au centime près), la seule photo jamais associée = **au pixel près** (`c2c3d9d2389a4c57`) le **dos de h10** déjà en ligne (mesurée le 25 ET le 27), et la description de h10 qui disait déjà ce que montre la photo · ⚠️ **une description inventée coûte plus cher qu'une case vide** : un vêtement que la maison ne coud pas a occupé une carte **onze jours**, commandable · ⚠️ **garde-fou qui manquait** : comparer les prix d'une fiche neuve à ceux des existantes — **six valeurs qui se répètent = doublon jusqu'à preuve du contraire** · **CATALOGUE 20 → 19 CARTES, TOUTES AVEC LEUR PHOTO**, plus une seule « Photo sur WhatsApp » · le mécanisme `photoWa` reste en place (une place qui attend, pas du code mort) · **150 contrôles verts** · ⏳ **RESTE À PUBLIER** : le site en ligne date d'avant le 26/08 et montre encore la Robe d'été sans photo, alors qu'elle en a une depuis — `python3 _predeploy.py` puis `wrangler pages deploy _dist`, depuis le PC · **rien n'est déployé**, publier depuis le PC | **+229 51 37 47 93** ✅ posé et EN LIGNE (`wa.me/22951374793`, donné 2026-08-01 · ⚠️ tester une fois : le dépôt a 2 formats, sinon `2290151374793`) |
| 11 | Angélique AVOCEVOU | **ANGY ART** — **artiste plasticienne** · Cotonou · œuvres contemporaines en relief sur l'identité, la mémoire et le patrimoine africain (scarifications, symboles, masques, textiles) · portfolio + moteur de demande | **LIVE https://angy-art.pages.dev** (Cloudflare Pages `angy-art`, déployé 2026-08-05) · direction **éditoriale noir `#0a0a0a` / crème `#f3efe6`** demandée par Mongazi (réf. « Selva Toscana ») : **Playfair Display + Public Sans**, italiques dorés, curseur suiveur, défilement lourd, **carrousel coverflow**, modale de demande → WhatsApp rédigé · ✅ **VRAI LOGO POSÉ** (glyphe or détouré : nav, pied, modale, favicon, OG, affiche) + son accroche officielle **« Inspiré d'en haut, enraciné ici. »** · **l'or du site est SON or `#bd9f64`** (relevé sur le logo, 7,8:1 sur noir) ; ⚠️ sur le crème il tombe à 2,2:1 → `#7e6d3a` pour tout ce qui est sur clair · **ZÉRO bibliothèque** là où le brief demandait Next.js/GSAP/Lenis/Swiper, tout réécrit en natif · citation signée **d'Angélique**, jamais d'un critique inventé · **VAGUE 2026-08-08 `?v=20260808a` — LE SITE NE CONTIENT PLUS UNE SEULE IMAGE GÉNÉRÉE** (détail `_memoire/conversations/2026-08-08-angy-art-vraies-photos.md`) : les **13 visuels IA sont SUPPRIMÉS** (dont les 8 fausses œuvres du carrousel) avec `_gen_images.py`/`_pose_images.py`, remplacés par **15 vraies photos** envoyées par Mongazi · **7 photos d'atelier 100 % réelles** (elle pose l'enduit, mélange le pigment, trace le trait, peint une toile de 2 m) + **8 mises en situation** ⚠️ **les MASQUES sont bien les siens, les INTÉRIEURS sont des rendus** (preuve : le terracotta de `situ-1` est celui qu'elle peint sur `temps-3`) → le mot **« MISE EN SITUATION »** est le cartel, la vue en grand ET le texte alternatif ; ⛔ **aucun prix, aucune dimension, aucun titre d'œuvre inventé** · **7 sections** : nouvelles **« La main, en quatre temps »** (l'enduit → le pigment → le trait → l'échelle, remplace l'ancien plein écran ATELIER) et **« Pour un lieu »** (hôtels/restaurants/halls) · **signature du héros tirée de son geste** : la photo se révèle sans couleur puis le pigment monte (2 calques du même fichier, **seule l'opacité s'anime**, animer un `filter` faisait tressauter le héros sur téléphone) · **og.png porte une vraie photo** (la vignette WhatsApp = la 1re impression au Bénin) · affiche A4 régénérée (photo 76→106 mm, elle traînait encore l'image IA) · **106 contrôles** (67 avant) dont **3 familles neuves** : arrivée par le menu, chevauchement des boîtes, et surtout **contraste mesuré sur les PIXELS RENDUS** (on masque le texte, on photographie, on prend le décile le plus clair) — ⚠️ le contrôle de contraste habituel lit `background-color`, **transparent au-dessus d'une photo, donc aveugle** · ⛔ **3 défauts antérieurs corrigés** : cliquer le menu posait l'étiquette **à 6 px sous la barre fixe** (le défilement est écrit à la main, `scroll-margin-top` n'est PAS appliqué tout seul → le lire et le retrancher ; 6→90 px), le texte de « Pour un lieu » se posait **sur un masque orange vif**, et à 768 px « DÉCOUVRIR L'ATELIER » **barrait** « PIÈCES · UNIQUES » · ⚠️ **le cache de bordure garde les vieilles images un an et on ne peut PAS le purger sur un `*.pages.dev`** (`cf-cache-status: HIT` alors que l'alias du déploiement renvoie 404) · nouveaux scripts `_photos.py` `_affiche.py` `_dist.py` · **2e temps du 2026-08-08 `?v=20260808c`** : ⛔ **Mongazi voyait encore l'ancienne image IA alors que le serveur envoyait la vraie (MD5 identique au disque)** = son propre navigateur, nos images portant `immutable` un an → **toute URL d'image porte désormais `?v=`** (y compris `og:image` et les chemins construits par `app.js`, constante `VER`) + contrôle dédié · **le HÉROS porte une ŒUVRE** (duo terracotta, arche passée en carré) : choisi parmi 5 cadrages serrés regardés côte à côte, **le seul sur fond sombre** — les 4 autres posent leur masque sur un mur beige qui devient un rectangle lumineux sur page noire · **navigation alignée sur la référence Selva Toscana** (vidéo envoyée par Mongazi, relue image par image) : le site avait déjà défilement lissé/curseur/coverflow/rythme/typo, il manquait **le rideau d'ouverture** (panneau crème, filet doré, compteur 00→100 en 1 s, puis retrait) et **le volet de section** (chaque section masquée par la couleur OPPOSÉE, qui se retire quand elle entre → la suivante semble glisser par-dessus ; ⚠️ `scaleY` sur un **pseudo-élément**, jamais sur la section, sinon la barre fixe casse) · ⚠️ **le compte du rideau tourne au minuteur, pas sur rAF** · ⚠️ **ne jamais mesurer une animation d'ouverture avec des `wait_for_timeout` empilés autour de captures** (une capture coûte des centaines de ms : deux diagnostics ont conclu à tort) → faire mesurer la PAGE · QC attend 3 400 ms · **109 contrôles** · **VAGUE ŒUVRES 2026-08-22 `?v=20260822a`** : ⛔ le travail du téléphone (ses **6 œuvres nommées et chiffrées**, son vocabulaire, la collection **ÉNERGIES**, les créations personnalisées) dormait dans `main` **sans être publié** — 6 images en **404**, page servie de 20 953 o contre 59 976 aujourd'hui (⚠️ une session en conteneur **n'a pas les jetons Cloudflare**, `secrets/` est ignoré par git : c'est le PC qui publie) · ✅ en ligne et vérifié (6 fichiers 200, prix 100k/200k/350k/500k FCFA, `app.js` servi **identique au disque en MD5**) · ⚠️ **VRAI DÉFAUT TROUVÉ** : le défilement maison avançait **d'un cran fixe PAR IMAGE** (`courant += (cible-courant)*.095`) → à 30 images/s le trajet dure **deux fois plus longtemps**, « accueil » laissait la page à **284 px** du haut sur ordinateur ; il interpole désormais **AU TEMPS** (`k = 1-(1-.095)^(dt/16.7)`) — **c'est le téléphone bas de gamme qui payait**, et le moteur ne tournant que sur pointeur fin, aucun contrôle mobile ne l'aurait vu · ⚠️ **2 pannes de contrôle, aucune du site** : serveur de test **mono-tâche** (`Page.goto: Timeout`, même panne qu'Hillary) et une **attente fixe de 1 700 ms** là où il fallait attendre que la page se pose · **150 contrôles verts** · · reste : **photos des œuvres seules** (fond neutre + titre + dimensions, dans un tableau `OEUVRES` SÉPARÉ de `SITUATIONS`), adresse, vrais avis, **tester le n° WhatsApp** · détail `clients/11-angy-art/CONTEXT.md` + `DESIGN.md` · **2026-08-21 — LES CRÉATIONS PERSONNALISÉES** (brief d'Angélique, détail dans son `CONTEXT.md`) : section `#personnalise` + **15 questions en TROIS TEMPS** · ⚠️ **la distinction Collections / Créations personnalisées est exigée par le brief** — deux blocs, dite en toutes lettres, **aucun prix** (œuvre sur commande, pas produit décoratif) · signature **« l'entaille qui se creuse »** (2 traits sur le même chemin, arête +1px, creux −1px tracé 160 ms après) · ⚠️ **le formulaire ne SOUMET rien** : site statique, il RÉDIGE le brief et ouvre WhatsApp ; la **question 11 (téléversement) devient une phrase** (pas de serveur = un bouton « Parcourir » serait un mensonge) ; **le nom et la date sont dans le message** faute de base · ⛔ **3 défauts vus sur les CAPTURES, pas dans le code** : `.pill--plein` est crème sur noir donc **invisible sur une section claire** (le site n'avait aucun bouton pour fond crème → `.pill--encre` 15,2:1) · **`hidden` ne cache rien quand un `display` est déclaré** (3 étapes empilées, champs conditionnels ouverts) · **un enfant de grille a `min-width:auto`** donc la piste s'élargit au contenu intrinsèque et les champs débordaient · ⚠️ la largeur d'une modale se déclare sur `[open]`, un `max-width` seul ne sert à rien · **QC 106 → 121, tous verts**, dont **2 contrôles qui MENTAIENT** (l'un ouvrait vraiment `wa.me` = il testait le réseau, pas le message ; l'autre attendait Google Fonts) · ⏳ à trancher : le brief écrit **« ANGYART »**, le site **« Angy Art »** ; et le bouton du son est encore flottant comme l'était celui d'Hillary · **2026-08-21 — SES SIX ŒUVRES ENTRENT** (le manque le plus ancien du site) : **Bonheur éternel** 1m20×80 *prix sur demande* · **L'Équilibre des Âmes** et **Alliance Solaire** 75×65 à 250 000 F · **Âmes Sœurs** 120 000 F · **Force Silencieuse** 110 000 F · **Aura** 100 000 F — titres, techniques, palettes, dimensions, prix et textes **d'elle, mot pour mot** · ⚠️ **`situ-1/2/3` du carrousel ÉTAIENT déjà ces œuvres**, mais anonymes et sans prix : elles ont enfin leur identité · ⚠️ **ses textes sont écrits EN DUR dans la page, pas dans le script** (sans JS et pour les moteurs, c'est ce qui fait la valeur du site) + **6 fiches `VisualArtwork`** avec leur `Offer` · ⚠️ **« MISE EN SITUATION » sur 3 photos** (les masques sont d'elle, les niches de marbre sont des rendus) · signature **« le cartel qui s'écrit »** · ⚠️ **boîte commune mais vraie proportion** : recadrer en carré alignerait les cartes et MENTIRAIT sur une pièce d'1m20 · 663 Ko différés · **QC 121 → 129** · **VAGUE 2026-08-21 — SON VOCABULAIRE** (récapitulatif d'Angélique) : menu **L'ARTISTE / LA COLLECTION / SUR MESURE / LE JOURNAL / CONTACT** et étiquettes de sections alignées dessus · héros → **« DÉCOUVRIR LES ŒUVRES »** (`#oeuvres`) et **second appel en bas de page** vers le sur-mesure · la section porte le **nom de la collection AVANT son titre** (`COLLECTION ÉNERGIES`), titre = sa phrase telle quelle « Donner une forme à ce qui ne se voit pas. » · ⚠️ **`ACCUEIL` du menu non ajouté** (le logo tient le rôle, 6 entrées cassent à 390 px) — à lui dire · ⛔ **LE DÉFILEMENT LISSÉ ÉCRASAIT TOUT LE MONDE** : le moteur maison ne relisait sa cible que `if (!anime)`, donc pendant qu'il glissait il annulait recherche du navigateur, lecteur d'écran, touche Fin, tout `scrollIntoView` (mesuré : un saut à 200 px ramené à **5 992 px**) — 3e apparition de la famille après Lenis sur Au Braisé d'Or · ⚠️ **le correctif naïf est pire que le défaut** (adopter tout écart arrête le glissement net sur une image perdue) → **on regarde OÙ** : entre `courant` et `cible` c'est nous, ailleurs c'est quelqu'un d'autre · ⚠️ **4 contrôles qui RECOPIAIENT au lieu de LIRE** : 3 ancres de menu (→ `null.click()`, le contrôle plantait), les étiquettes en dur (→ il accusait le site d'avoir perdu des textes seulement renommés), **les 8 sélecteurs de `SECTIONS`** (→ **les 2 sections neuves n'ont JAMAIS été photographiées et personne ne l'a vu** : une liste de captures ne se plaint pas de ce qu'elle ne montre pas), et l'attente de 500 ms avant mesure (→ `placer()` : on se place PUIS on vérifie qu'on y est, sinon on le dit avec le chiffre) · **le contrôle du moteur a un TÉMOIN** (on prouve d'abord que ça glisse, sinon un moteur mort passerait) · **QC 129 → 146** · **6 QUESTIONS TRANCHÉES le 2026-08-21** sur ordre de Mongazi (« fais appliquer ce qui est meilleur, elle observera et me dira ») : **`ACCUEIL` ajouté au menu** (mesuré avant : 31 px de marge à 1024 px, 101 à 309 px au-delà, 7 entrées dans le tiroir) · **les SIX œuvres restent et AUCUN NOMBRE n'est annoncé** (elle en décrit 5, en a envoyé 6 : en cacher une = perte sèche, se tromper de laquelle = pire ; le jour où elle dit laquelle est à part, c'est un attribut, pas une refonte) · **son texte d'intro de collection tient sa place** (il n'assemble que ses mots, remplaçable en une ligne) · ⚠️ **AUCUN statut vendue/disponible inventé** → une phrase vraie dans les deux cas, posée AVANT la grille : « un mot suffit pour savoir si elle est encore disponible » · **« Angy Art » en deux mots** (logo, barre, pied, OG, JSON-LD, affiche le portent déjà) · L'ARTISTE garde son texte de démarche · ⚠️ le sur-mesure reste **court dans la barre** (sa formule complète déborde à 1024 px) · ⚠️ **une entrée « ACCUEIL » testée depuis le haut ne prouve rien** (arriver à 0 en partant de 0) → le contrôle part du BAS, 12 082 → 0 px · **QC 146 → 149** · ✅ **DÉPLOYÉ ET VÉRIFIÉ LE 2026-09-02 depuis le PC** (tout ce qui dormait dans `main` est en ligne : les 4 corrections d'Angélique, le bouton devenu sommaire, la vague fluidité) — **150 contrôles verts**, `index.html`/`app.js`/`app.css` servis **identiques au disque en MD5**, **34 fichiers sur 37 en 200** et les 3 autres sont corrects (`_headers` en 404 = fichier de configuration, jamais public ; `index.html` et `404.html` en 308 vers leurs adresses propres), un fichier absent répond **404** · publier = `python clients/11-angy-art/_dist.py` puis `wrangler pages deploy clients/11-angy-art/_dist --project-name=angy-art --branch=main` (⚠️ **`wrangler` global, pas `npx`**, et le jeton vient de `secrets/cloudflare.env` : une session en conteneur ne peut pas publier) · **VAGUE FLUIDITÉ 2026-08-26 `?v=20260826a`** (détail `_memoire/conversations/2026-08-26-angy-art-fluidite.md`) : le site était **vert à 150 contrôles ET tournait à 15 images/s** sur processeur ×6, avec une tâche de **1 557 ms** — *un QC vert dit que rien n'est cassé, pas que ça glisse* → **60 i/s, 0 à 1 tâche longue**, téléphone p95 **16,8 ms** · ⛔ **NE PAS REMETTRE LE GRAIN PLEIN ÉCRAN** : `body::after` en `fixed` + **`mix-blend-mode:overlay`** coûtait **⅓ à ¾ du budget d'une image** et valait **0,90/255** à l'œil (agrandi 3×, indiscernable) ; ⚠️ **ce n'est pas l'image de bruit qui coûte, c'est le MÉLANGE** (retirer `background-image` ne change rien, passer à `normal` rapporte autant que tout supprimer) et ⚠️ **aucun remède de compositing ne le sauve** (`will-change`/`translateZ(0)`/`contain:strict`/`isolation`, 4 essais × 3 mesures, tous inchangés) · **on lit tout PUIS on écrit tout** dans les 2 balayages du défilement (`classList.add` au milieu d'une boucle de `getBoundingClientRect` = un recalcul de mise en page **par élément**, jusqu'à 100 par image) · **`marque.png` 199 Ko pour un rendu de 57×44 px**, demandé 2e à 2 298 ms sur 3G → **`marque.webp` 9,7 Ko** pour les pages (⚠️ le PNG **reste** : affiche A4, OG, favicons) · **`og.png` 566 Ko PNG → `og.jpg` 96 Ko** (règle de la maison) · **la barre du haut était à 92 %** et on lisait au travers → une bande de bord doit être **vraiment opaque** (0/255 mesuré) · **chemin critique 3G : 244 Ko** avant le héros · nouveaux instruments `_fluidite.py` `_attribuer.py` `_audit.py` (**22 contrôles**) · ⚠️ **5 de mes sondes ont menti avant de dire vrai** : mesurer le poids sur **localhost** (le seuil de `loading="lazy"` grandit avec la vitesse — j'ai failli réécrire le carrousel pour rien), **`*` n'atteint pas les pseudo-éléments**, un bouton de modale mal visé rendant 2 contrôles vides, les 44 px appliqués à un **lien dans une phrase**, et une barre jugée translucide alors que **la police finissait de charger** · **VAGUE 2026-08-27** (4 corrections d'Angélique) : ⚠️ le bouton du héros n'est pas supprimé mais **transformé en SOMMAIRE** de 6 entrées — elle regarde **sur téléphone**, où le burger ne lui suffit pas · ⚠️ **dans le flux**, pas en absolu (l'ancien se posait SUR la ligne des métriques à 768 px) · ⛔ **le bouton du son se posait dessus** : 11 × 34 px sur « DÉCOUVRIR LES ŒUVRES », **à 390 px et nulle part ailleurs** — pile la pastille qu'elle a nommée, pile sa largeur → couloir réservé + contrôle · ordre : **la collection AVANT le journal**, « Dans un lieu » après, étiquettes renumérotées 01→05 (elles allaient 01,02,03,04,**06**) · ⚠️ **réordonner = découper en tranches qui se touchent**, jamais recoller des morceaux choisis (longueur identique au caractère près ; la 1re version perdait les commentaires d'en-tête, le garde-fou a refusé d'écrire) · ⚠️ **MESURER AVANT D'APPLIQUER UNE RÈGLE DE STYLE DU CLIENT** : elle dit « le texte est plus grand que les titres », pris au pied de la lettre ça vise les `h2` — **faux**, ils font déjà 80 px contre 14-19. Le vrai coupable : l'**étiquette** à 10,5 px sous une phrase à 80 px, **7,5×**, et c'était le SEUL endroit du site → le nom prend la taille d'affichage · ⚠️ **à spécificité égale la dernière règle gagne** (ma requête média était placée avant celle qu'elle corrige, elle ne servait à rien) · **QC 146 → 149** · ✅ **ÉNERGIES au pluriel** tranché par Mongazi (« non ça va ») · **VAGUE 2026-09-04 `?v=20260904a` — UN SEUL BOUTON « DÉCOUVRIR », VISIBLE PARTOUT** (détail `_memoire/conversations/2026-09-04-angy-art-bouton-decouvrir.md`) : le sommaire du 27/08 faisait son travail **au bas du héros et nulle part ailleurs** — passée la première section il ne restait que le burger, exactement ce dont Angélique se plaignait (**ce n'est pas la liste qui manquait, c'est sa présence**) · **un seul contrôle, deux places, jamais deux à l'écran** : pastille dans le héros (**dans le flux**) + pilule dans la barre **à toutes les largeurs** (elle remplace le burger, qui n'avait pas de nom), celle de la barre **s'efface tant que celle du héros est à l'écran** et **par défaut elle est VISIBLE** (observateur mort = un bouton, jamais zéro) ; mesuré : à **390 px le bouton du héros est sous la ligne de flottaison**, donc c'est celui de la barre qu'on voit d'abord · **le panneau porte SON sommaire entier** (ACCUEIL · L'ARTISTE · DÉCOUVRIR LES ŒUVRES · LE JOURNAL · DANS UN LIEU · CRÉATIONS SUR MESURE · CONTACT · WHATSAPP) — ⚠️ **les deux listes ont fusionné** : la barre portait des libellés **raccourcis** faute de place à 1024 px et n'avait pas « DANS UN LIEU » · ⚠️ **pas de pastille flottante** (interdit depuis Mon Bénin, payé ici le 27/08 avec le bouton du son sur « DÉCOUVRIR LES ŒUVRES ») : **la barre est la seule chose de ce site qui ait le droit de passer devant une phrase**, parce qu'elle est vraiment opaque · ⛔ **3 défauts vus SUR LES CAPTURES, QC vert** (`_vue_decouvrir.py`) : **le panneau recouvrait le bouton qui l'avait ouvert** — plus aucune croix, car **un enfant de la barre compte son `z-index` à l'intérieur de la barre** (même famille que « il change de parent, pas de style », Hillary 21/08) · **« DEMANDER UNE VISITE » coupé en deux** par le bord du panneau · **cadre de focus sur le 1er lien au simple toucher** (le focus va au panneau, `tabindex="-1"`) · **sans JS** le bouton **se retire**, le panneau redevient la rangée repliée et **la barre cesse de flotter** (`position:static`) · **au clavier** le reste de la page est **inerte**, Échap referme, le focus revient au bouton · ⚠️ **panneau centré par marges automatiques, pas `justify-content:center`** (qui **coupe le début** d'un conteneur qui défile) · **QC 150 → 188** ⚠️ **« toujours un » et « jamais deux » sont DEUX contrôles** (l'un seul laisse passer deux boutons, l'autre seul une page sans aucun) et **« se voit » se mesure** (8 boîtes réellement dans la fenêtre, panneau à défiler refusé) · ✅ **déployé et vérifié** (app.css/app.js **identiques au disque en MD5**, plus aucune trace de `hero-plan`, 404 sur un fichier absent) · **SECOND TEMPS LE MÊME JOUR `?v=20260904b`** — Mongazi après avoir vu le résultat : « il y avait directement tout qui était visible, remets ça » : le bouton unique avait **remplacé** les liens de la barre, or ⚠️ **une contrainte de téléphone ne se généralise pas à l'ordinateur** (la demande d'Angélique venait de son usage mobile ; l'appliquer partout retirait, là où la place ne manque pas, une navigation qu'on VOIT pour une qu'on OUVRE) → **la barre garde ses 6 entrées + WhatsApp**, le burger reste sur téléphone, **le sommaire du héros revient**, et **le bouton flottant s'AJOUTE au lieu de remplacer** (trois portes, un seul mécanisme, ouvrir l'une referme l'autre, chacune gèle ce qui n'est pas elle) · ⚠️ **les deux instruments flottants partagent UN couloir réservé, pas deux** · ⛔ **UN RECOUVREMENT SE CALCULE, IL NE S'ÉCHANTILLONNE PAS** : le 1er jet balayait par paliers de 400 px, il est passé **au vert** en laissant une vraie collision (« ÉQUIPER UN LIEU », **54 px à 390 px**, fenêtre de croisement de **102 px** = manquée 4 fois sur 5) → on résout l'intervalle de défilement où le fixe croise la cible, en écartant ce qui ne défile pas · ⚠️ **le `?v=` n'avait pas été bumpé** alors que feuille et script avaient changé de 307 et 107 lignes : nos assets étant `immutable` un an, tous ceux qui avaient ouvert le site le matin, **Mongazi le premier**, seraient restés sur l'ancienne version (défaut du 2026-08-08 à l'identique) · **QC 188 → 209 verts**, déployé et servi identique au disque en MD5 | **+229 01 52 00 64 90** (⚠️ à tester une fois : 8 et 10 chiffres coexistent) |

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
- **LE PAIEMENT EN LIGNE (SasPay) EST OUVERT** (2026-09-03) : le site encaisse
  par Mobile Money ou carte, **et livre le carnet tout seul** — `piste-paiement-recu`
  appelle `piste-livrer` dès qu'un paiement est confirmé, à trois heures du matin
  comme à midi. ⚠️ **Il l'appelle, il ne le recopie pas.** La **porte interne**
  (`PISTE_JETON_INTERNE`) ne desserre que le mot de passe du cockpit et le verrou
  anti-force-brute (sinon un inconnu tapant des mots de passe empêcherait un client
  qui a **payé** d'être livré) ; **une porte interne n'est pas une porte dérobée**.
  ⛔ **Un échec de livraison ne fait jamais échouer l'encaissement.**
  ⚠️ **Un moyen de paiement n'est pas un bouton, c'est une hypothèse dans tout
  l'entonnoir** : le numéro Mobile Money était obligatoire pour tout le monde, la
  route `#/merci` où SasPay ramène le client **n'existait pas**, et les étapes
  disaient « envoyez une capture » au-dessus d'un bouton Payer.
  ⚠️ **Lien de paiement ≠ session de checkout** : le lien est réutilisable à
  montant fixe, la session est à usage unique au montant de la commande — seule
  la seconde relie un paiement à une commande. La page « Liens de paiement » du
  tableau de bord reste vide, c'est normal.
  ✅ **Vérifié sur les 61 réseaux** : Bénin (MTN/Moov/Celtiis), Togo (Mixx/Moov/
  Togocel, **pas de MTN**), Côte d'Ivoire (MTN/Moov/Orange/Wave/Djamo), tous en XOF.
  ⚠️ Minimum **200 XOF**. ⚠️ **Les listes de leur API sont paginées et le `limit`
  est ignoré** : 61 réseaux annoncés, 20 rendus — vérifier `count` et `next` avant
  de conclure.
  ⛔ **LE PREMIER PAIEMENT RÉEL N'A PAS EU LIEU** : c'est le seul essai qui prouve
  le dernier maillon, celui qui relie une notification à une commande.
  ⛔ **L'ANCIEN CHEMIN EST SUPPRIMÉ** (dépôt à la main + redirection WhatsApp) :
  il n'y a plus qu'un seul moyen de payer. ⚠️ **La redirection WhatsApp faisait
  sortir le client du tunnel juste avant qu'il paie** ; WhatsApp reste comme
  moyen de nous joindre, pas comme étape. ⚠️ **Le filet n'est plus le client qui
  envoie sa capture, c'est Mongazi qui regarde le tableau de bord et le
  journal** — dit avant de le faire.
  Détail : `piste/PAIEMENT.md` et `_memoire/conversations/2026-09-03-piste-paiement-en-ligne.md`.
- **Source de vérité : `piste/PRODUCT.md`**, 88 décisions.

### MON BÉNIN — l'expérience du pays  *(objet éditorial, pas un SaaS)*
- **Ce que c'est** : « pas un site sur le Bénin, **un voyage au Bénin qui dure
  sept minutes** ». 8 stations dans l'ordre réel de la latitude, de la **Porte
  du Non-Retour (km 0)** au **fleuve Niger (km 617)**, sur une échelle de 700 km.
  Le défilement est la route, l'anneau du coin est **gradué en kilomètres**.
- **La règle qui fait tout** : **un verbe d'interaction DIFFÉRENT par lieu**
  (tenir, remonter, choisir, pagayer, frotter, descendre, attendre, arriver).
  Si une interaction pourrait être copiée-collée ailleurs, elle est à refaire.
- **Le refus fondateur** : la référence de Mongazi (« GLOBETROTTER ») a un bouton
  **« HASARD »**, donc c'est un catalogue. Ici **l'ordre des lieux EST le sens**,
  et rien ne se tire au sort.
- **Où** : `benin-mon-pays/` · `python benin-mon-pays/_qc.py` (**107 contrôles**),
  `_voir.py` (planches 390 + 1440, à REGARDER), `_logo.py` + `_logo_png.py`,
  `_images.py`.
- **LA MARQUE (2026-08-11, demandée par Mongazi) : le CONTOUR DU BÉNIN rempli
  du DRAPEAU**, traversé par la ligne des 700 km, point d'or au km 0, sept
  graduations. Le méridien gradué d'avant est retiré. ⚠️ Contour **Natural
  Earth 50 m, domaine public** (geoBoundaries est en CC BY : un logo se recopie
  partout, il ne peut pas traîner un crédit) · couleurs **lues sur le fichier
  officiel** (`#008751` `#fcd116` `#e8112d`, bande verte à **40 %**) · la ligne
  est **prolongée et arrêtée par la découpe du pays**, sinon elle s'interrompt
  au milieu du jaune · ⚠️ **PIÈGE : `filter: invert(1)` dans la barre rendait
  le vert MAGENTA** (légitime tant que la marque était monochrome) → la petite
  marque est **remplie, sans contour ni ligne**, et un contrôle lit le `filter`
  calculé · **un seul favicon** désormais · l'**image de partage porte la
  marque** · PNG rendus par **Playwright** (cairosvg inutilisable ici).
- **CE QUE MONGAZI DOIT APPORTER : `benin-mon-pays/CE-QUE-TU-DOIS-APPORTER.md`**
  (2026-08-11). ⚠️ **Les 8 photos en ligne sont vraies mais EMPRUNTÉES**
  (CC BY / CC BY-SA, crédit obligatoire, en paysage) : ce ne sont pas nos
  images. Ordre conseillé : les 2 photos de la Porte, une voix sur ce lieu,
  puis l'accord écrit des 5 artisans.
- ⚠️ **Le bouton annonçait « Les onze lieux » pour 8 sections** (les 11 sont
  décidés, pas construits) : corrigé le 2026-08-11, et **un contrôle vérifie
  que le mot et le nombre concordent**. Même famille que la jauge qui
  contredisait son étiquette.
- **LIVE : https://mon-benin.pages.dev — UNE SEULE ADRESSE** · projet
  Cloudflare Pages `mon-benin`, **branche `main` uniquement** · publier =
  `python benin-mon-pays/_dist.py` puis déployer `_dist` sur `main`
  · ⚠️ **le site a longtemps répondu à DEUX adresses** (`dev.` et la
  production, qui elle rendait 404) **et n'en nommait aucune** : ni `canonical`
  ni `og:url`. Mongazi : « il est censé y en avoir une seule ». Les 9
  déploiements `dev` sont supprimés. **Pour essayer, le QC et un serveur local,
  jamais une deuxième adresse en ligne**
  · **le portail avance TOUT SEUL** (6,2 s) avec 4 garde-fous, et **ne
  télécharge aucune ambiance** en tournant (380 Ko non demandés)
  · **le héros porte la PHOTO du lieu** (`-po.webp`, `_photos_portail.py`, qui
  **vise un poids** et non une qualité), et le contraste du titre est mesuré
  **sur les huit lieux**, pas sur un seul
  · ⚠️ **BÉNINÉO = agence de tourisme** (`@mybenineo`), partenaire possible et
  première halte naturelle ; **ses photos ne sont sur aucun disque** et **rien
  d'elle n'est publié sans accord écrit**
  · **premier écran sous 320 Ko**, donc les 3 s en 3G sont tenues par
  construction · ⚠️ un agent non navigateur reçoit **403** sur `*.pages.dev`
  (filtrage de bots) : vérifier avec un vrai `User-Agent`.
- **13 décisions prises par Mongazi le 2026-08-10** : nom **MON BÉNIN** +
  « sept cents kilomètres » · **départ à la Porte** · cible **diaspora
  afro-descendante** · **bilingue FR/EN dès la sortie** · **11 lieux** (les 8 +
  Porto-Novo « retourner », Grand-Popo « mêler », Dassa « compter ») · photos
  **sous licence à chercher** · **sons générés (WaveSpeed)** · voix **plus tard**
  · haltes **oui, Mongazi demande l'accord des 5 artisans** · annuaire **en objet
  SÉPARÉ, même identité** · **cap sur les Vodun Days de janvier**.
- ✅ **WaveSpeed FAIT de l'audio** (vérifié 2026-08-10) : 342 modèles audio sur
  979. Le bon pour une ambiance est **`mirelo-ai/sfx-1.6/text-to-audio` avec
  `ambience: true`**, le SEUL qui boucle sans couture, à **0,01 $ la seconde**.
  Les 8 ambiances de Mon Bénin ont coûté **0,64 $**. (Moins cher :
  `sonilo/v1/text-to-sfx` à 0,002 $/s, mais aucune garantie de boucle.)
- ⚠️ **Le son généré est une MATIÈRE, pas un document.** Une ambiance fabriquée
  présentée comme « le bruit de Ganvié » est le même mensonge qu'une photo
  générée du lieu. C'est **écrit dans le pied de page** de Mon Bénin, et un
  contrôle le vérifie. À remplacer par de vrais enregistrements.
- ⚠️ **Toujours mesurer un son généré, jamais l'écouter de confiance** : 8
  fichiers de taille identique (débit constant) peuvent être 8 fois le même.
  Comparer les MD5 **et** le profil spectral. Vérifier le **raccord de boucle**
  (début contre fin) et **normaliser les niveaux** : bruts, l'écart entre deux
  ambiances atteignait un facteur 15.
- ⚠️ **L'annuaire d'entreprises (« un Google My Business béninois, ultra stylé »)
  est un SECOND objet**, pas une couche du voyage : un parcours linéaire de 11
  lieux ne porte pas 5 000 fiches. **Note due à Mongazi** : ce que perdrait PISTE
  (100 F la fiche, exclusivité 90 j) contre ce que gagnerait l'annuaire.
- ⚠️ **Les km sont des latitudes converties**, pas des distances routières
  (Cotonou→Malanville fait ~730 km par la route et casserait l'échelle).
- ⛔ **Aucune image générée d'un lieu réel.** En attendant les photos, le site est
  un **atlas dessiné** (relevés SVG qui se tracent), fini en l'état.
- **Couche « haltes » conçue mais PAS ouverte** : l'unité est « quelqu'un qui
  fabrique quelque chose, dans un endroit », donc une coiffeuse et un parc
  national sont le même objet ; un commerce apparaît à sa **latitude réelle** et
  **la position ne s'achète pas**. Les 5 artisans déjà clients sont les premières
  haltes naturelles, **mais il faut leur accord écrit**.
- **Règle des éléments fixes, née ici** : un **instrument flottant ne recouvre
  jamais du texte** ; seules les **bandes de bord** en ont le droit, et elles
  doivent être **vraiment opaques** (vérifié en photographiant, pas en lisant le
  CSS). Réserver une marge ne suffit pas : un `fixed` est ancré au viewport.
- Détail complet : `benin-mon-pays/CONTEXT.md`

### MINUIT — la lettre digitale  *(produit interne, 2026-09-02)*
- **Ce que c'est** : « une lettre digitale, c'est **une enveloppe cachetée qu'on
  ouvre à l'heure dite** ». L'acheteur écrit son mot, choisit l'heure, paie en
  Mobile Money ; la destinataire reçoit un lien, brise le cachet, et lit.
  Dossier de décision : `_plans/2026-08-27-minuit-dossier.html` · manuel
  d'exploitation : `_plans/2026-08-28-minuit-manuel.html` · code : **`minuit/`**.
- **La thèse** : *le romantique est le marketing, l'événement est le chiffre
  d'affaires, le B2B est la retraite.* Un seul moteur, trois habillages.
- **Fait le 2026-09-02** : **le gabarit** (`lettre.html`) et **le constructeur**
  (`creer.html`), **78 contrôles verts** (`python minuit/_qc.py`), quatre
  passages d'affilée. ⏳ Restent **la livraison à l'heure choisie** (n8n, la
  fonction qui donne son nom au produit et qu'aucun concurrent ne propose) et
  **le serveur en ligne** (Render).
- **Fait le 2026-09-03** : **la vidéo de démonstration**, composition
  `minuit-demo` dans `_studio-video/` (1080x1920, 30 s, `npm run rendu:minuit`).
  Six plans, **les six signatures du produit rejouées en React** et non
  photographiées : une capture ne montre pas un cachet qui se brise. ⛔ **Ne pas
  la publier en l'état** : elle promet « Elle l'ouvre à minuit pile. Pas
  avant. » et affiche `nebula-agency.online/minuit`, or **ni la remise à
  l'heure dite ni le serveur n'existent** au 2026-09-03. La vidéo est prête,
  la promesse ne l'est pas. ⛔ **Jamais de fondu enchaîné entre deux plans qui
  montrent du papier** : mesuré, deux feuilles à 50 % l'une sur l'autre
  ressemblent à une panne, pas à une transition (les plans partagent le même
  fond de nuit, donc la coupe est déjà invisible).
  Détail : `_memoire/conversations/2026-09-03-minuit-video-demo.md`.
- ⛔ **`</script>` écrit par un acheteur TUE la page** : les données atterrissent
  dans un bloc `<script>`, et **`json.dumps` ne protège pas de ça**. Toute
  sérialisation passe par **`minuit/_injecter.py`**, seul endroit, qui neutralise
  `</`, `<!--` et U+2028/U+2029. ⚠️ **Le commentaire qui documentait ce piège le
  contenait en clair** et fermait lui-même le bloc ; ⚠️ **la fonction qui
  neutralise U+2028 les portait en clair dans ses regex**. → **`node --check` sur
  le script en ligne avant d'écrire**, et se méfier d'un fichier qui documente
  son propre piège.
- ⛔ **Le seuil EST le produit** : une lettre livrée garde toujours son cachet.
  L'aperçu du constructeur s'ouvre (l'acheteur doit voir SES mots, c'est là que
  la vente se fait), mais **le drapeau d'aperçu ne part jamais dans la commande**,
  et un contrôle le vérifie.
- ⚠️ **Aucune police téléchargée, aucun appel réseau, `noindex`** : une lettre
  s'ouvre dans un taxi et n'a rien à faire dans un moteur. **Les photos sont des
  données (`data:`), jamais des liens** : un lien distant ferait dépendre la
  lettre d'un serveur et **fuiterait l'heure d'ouverture** vers un tiers.
- ⛔ **La sauvegarde du formulaire n'est pas un confort** : pour payer, l'acheteur
  QUITTE la page. Sans restauration au retour il perd son quart d'heure, ne
  recommence pas, et **on ne sait même pas que la vente a existé**.
- ⏳ **Avant la première vente** : le risque de détournement (adresse non
  devinable, expiration, retrait sous 24 h, CGU) — aucune des 5 références du
  dossier ne le traite. ⛔ **Jamais de MP3 hébergé** (contrefaçon). ⚠️ **Le deuil
  ne se décore pas** : sobriété totale, aucun emoji, relecture par quelqu'un qui
  vient d'enterrer un proche avant de le vendre.

### LE STANDARD — l'agent WhatsApp des clients  *(produit interne, 2026-08-28)*
- **Ce que c'est** : celui qui décroche. Un client écrit sur le WhatsApp d'une
  maison, l'agent répond avec **la carte réelle de cette maison**, prend la
  commande, prévient le patron, et **passe la main dès qu'il ne sait pas**. Les
  onze vitrines finissent toutes sur « écrire sur WhatsApp » : c'était le seul
  maillon que personne n'avait automatisé.
- **Où** : `whatsapp-agent/` · `python whatsapp-agent/simuler.py braise-dor`
  (terminal, sans compte WhatsApp) · `python whatsapp-agent/_qc.py`
  (**146 contrôles**, sans clé et sans réseau) · `serveur.py` = le webhook.
- ⚠️ **Ce n'est PAS Vendora.** `boutique-ia/` est le SaaS des commerçants qui
  s'inscrivent ; LE STANDARD sert les **clients NEBULA qui existent déjà**, dont
  le catalogue vit dans leur propre dossier.
- **LA RÈGLE FONDATRICE : le catalogue n'est jamais recopié, il est LU** dans le
  fichier qui fait autorité sur le site (`carte.ts` chez Au Braisé d'Or, `PIECES`
  chez Hillary), par un lecteur de littéraux JS/TS qui **n'exécute aucun code**.
  La maison change un prix sur son site, l'agent change le jour même. ⚠️ Preuve
  arrivée toute seule le jour de l'écriture : `main` a retiré une pièce
  d'Hillary, l'agent est passé de **20 à 19 sans une ligne modifiée**, QC vert.
- ⛔ **LE GARDE-FOU DES PRIX, et c'est lui qui rend le kit livrable** : une
  consigne dans un prompt n'est pas un contrôle. Le code **relit chaque réponse
  avant l'envoi** et bloque tout montant que la carte ne porte pas. ⚠️ Le montant
  est **ATTACHÉ au plat nommé dans la même phrase** — mesuré, vérifier un total
  nu ne vaut rien chez un restaurateur (**90 %** des montants ronds sont une
  addition possible de la carte, contre **2 %** chez Hillary). D'où la règle
  « nomme l'article que tu chiffres » dans le prompt. Blocage = le client reçoit
  une phrase honnête, le patron reçoit **le message bloqué en entier**.
- **Les cinq façons d'avoir un prix** sont toutes portées (simple · deux tailles
  · fourchette · barème à N crans · prix sur demande) : la carte du Braisé d'Or
  les utilise toutes, et les aplatir faisait encaisser 1 000 F une glace à 2 500.
- **Stack** : Python, **aucune dépendance hors `anthropic` et PyYAML** (HTTP,
  webhooks, signatures, base : bibliothèque standard) · SQLite par numéro ·
  **`claude-sonnet-5`** (règle maison : jamais Opus sur du texte client) · socle
  mis en cache, l'heure posée **après** la coupure · trois canaux (Meta Cloud
  API, Twilio, console).
- **Ajouter un client = deux fichiers** : un `lecteurs/<client>.py` (~60 lignes)
  et une fiche `maisons/<client>.yaml`. ⚠️ **Aucun prix dans une fiche** — le QC
  le refuse : un prix recopié est une deuxième vérité.
- ⚠️ **La fenêtre de 24 h** : répondre à un client est toujours permis,
  **prévenir le patron ne l'est pas toujours**. Hors fenêtre il faut un modèle
  pré-approuvé par Meta — pas fait. L'escalade est journalisée et gardée en base.
- ⛔ **RESTE À FAIRE, et ça bloque la mise en ligne** : **le numéro d'Au Braisé
  d'Or** (le dépôt en porte deux, l'enseigne un troisième — fiche **vide
  exprès**, le serveur refuse de démarrer et dit ce qui manque) · le numéro qui
  reçoit les alertes par maison · **le premier appel réel au modèle** (le
  conteneur d'écriture n'avait pas de clé) · vocaux et images (passés à un
  humain, pas transcrits).
- **Coût** : une conversation de dix messages ≈ **16 F CFA** cache chaud,
  **33 F** cache froid. Conversation de service Meta gratuite jusqu'à 1 000/mois.
- Détail : `whatsapp-agent/README.md` et
  `_memoire/conversations/2026-08-28-standard-whatsapp.md`

## Infrastructure — où tourne quoi (2026-08-02)

| Ce qui tourne | Où | Notes |
|---|---|---|
| Les 12 vitrines et outils | **Cloudflare Pages** | un déploiement est un **instantané complet** : ce qui manque sur le disque disparaît du site |
| **Bureau des partenaires** | **Render** (`srv-d9nni7e7bikc73c9oksg`) + **Supabase** (schéma `naff`) | Railway a fait disparaître l'app le 2026-08-01, données de prod perdues |
| Le domaine des partenaires | relais Cloudflare Pages `nebula-partenaires` | change d'origine sans toucher au DNS |

⚠️ **UN SEUL PROJET SUPABASE PORTE TROIS PRODUITS** (vérifié 2026-09-03) : la référence
`xukduhqqfzogisoimhyo`, région `eu-central-1`, **affichée sous le nom `boussole`** dans le
tableau de bord. Elle contient le schéma **`piste`** (10 tables), le schéma **`naff`** du
bureau des partenaires (16 tables) et **`public.boussole_proto_etat`**. Le nom du projet ne
dit donc pas ce qu'il contient. ⛔ **Si ce projet est mis en pause, les trois tombent
ensemble** — et les deux autres projets du compte (`cercle`, `allonebiao2@gmail.com's
Project`) sont déjà en pause, donc ça arrive. ⚠️ Un **jeton d'accès** Supabase est lié au
**compte**, pas à un projet : `supabase.com/dashboard/account/tokens`.

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

Il dit **d'abord si `main` local est en retard sur `origin/main`**, puis liste ce qui traîne
sur les autres branches, dit si la fusion passerait sans conflit, et signale celles qui
touchent du sensible (contrat, socle commercial, `server.py`, `_worker.js`, `secrets/`, ce
fichier). Avec `--fusionner`, il rapatrie.

⛔ **`git fetch` se fait AVANT de travailler, pas avant de pousser.** Le 2026-08-27, le PC de
Cotonou a refait de zéro les six photos de sauces d'Au Braisé d'Or — images, deux outils
neufs, correctif du QC — alors que le travail dormait dans `main` depuis la veille, poussé
en 7 commits depuis le téléphone, **à partir des mêmes photos sources au bit près**. Le
script excluait `origin/main` de son inventaire et répondait « ✅ Rien ne traîne ».
⚠️ **Une session du téléphone pousse DIRECTEMENT dans `main`** : « rien ne traîne sur les
branches » ne veut pas dire « je suis à jour ». Une branche oubliée coûte une fusion, un
`main` en retard coûte le travail refait deux fois.

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
- **Contrat partenaire en version 1.3** (2026-09-02). Un partenaire encore en 1.1 doit
  recevoir un préavis écrit de 30 jours avant toute baisse de barème (art. 6.7). ⚠️ **La 1.3
  ne baisse aucun taux** : le préavis n'a pas lieu de jouer entre la 1.2 et la 1.3
- ⛔ **Le contrat partenaire ne parle que de TROIS offres** : **Catalogue Digital**,
  **Vitrine**, **Outil métier**, plus le QR Code Google Review. L'article 4.4 dit « les
  offres du tableau de l'article 4.1, **et elles seules** », et l'Outil s'ouvre après
  **3 ventes et en binôme**. ⚠️ **Aucun logiciel édité par NEBULA n'est nommé dans le
  contrat** (Mongazi, 2026-09-02 : « dans le contrat ya rien qui concerne boussole et autre
  bordel ») : le « et elles seules » suffit, et nommer les produits obligerait à un avenant
  à chaque nouveau logiciel. Le socle §8 garde la seule exclusion que Mongazi avait posée
  lui-même, Boussole
- **Frais de réactivation : 5 000 F**, chiffrés au contrat (art. 4.1 et 6.2 bis). **Aucun
  frais si le client règle pendant les 7 jours de courtoisie.** Ils ne rapportent rien au
  partenaire : c'est ce qui lui ôte tout intérêt à laisser un client tomber
- ⚠️ **LA SIGNATURE DE MONGAZI NE VA JAMAIS SUR GITHUB.** Le dépôt est public et
  `pdf/*.pdf` y est versionné. L'image détourée vit dans **`secrets/signature-mongazi.png`**
  et le PDF signé dans **`pdf/signe/`**, tous deux ignorés par git. Le PDF **vierge** reste
  versionné, et les deux se superposent au millimètre (le marqueur est un commentaire HTML,
  donc le creux garde la même hauteur). Fabrication :
  `python _documents/nebula-agency/vente/_build_pdf.py`
- ⛔ **Détourer une signature ne se fait PAS au rembg** : rembg cherche une silhouette, or
  un trait d'encre sur du papier se sépare par sa **couleur**. Seuil sur la teinte bleue
  (`B - R`) = alpha continu, les traits gardent leur délié. ⚠️ **On ne cherche pas la
  feuille** (le carrelage est aussi clair qu'elle), on cherche l'encre. ⚠️ **Le sens se
  REGARDE** : les deux rotations se fabriquent, se posent sur un damier et se comparent à
  l'œil ; l'axe principal est dominé par l'envolée finale et ne dit pas la ligne de base
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
