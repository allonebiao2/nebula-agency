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
  ⚠️ **CETTE LIGNE CONTREDIT LA SECTION INFRASTRUCTURE** : le VPS `72.61.103.56`
  **n'appartient plus à Mongazi** (certificat au nom de `api-preprod.normly.fr`).
  Donc, sauf preuve du contraire, **il n'y a plus de n8n utilisable**. Deux
  chantiers s'appuyaient dessus sans le savoir : la relance des renouvellements,
  et « la livraison à l'heure choisie » de LE PLI (celle-là vit désormais dans la
  lettre, elle n'attend plus rien). ⏳ **Mongazi doit dire si un n8n tourne
  ailleurs**, oui ou non ; en attendant, ne rien planifier qui en dépende.
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
  Le studio porte aussi **la démonstration vidéo de LE PLI** (`lepli-demo`,
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
| 04 | Gloria (Ahouangnimon) | **LUXURY CLUB 229** — hub + 3 marques : **INA Luxury** (cosmétiques) · **Luxury Skin Clinic** (institut, Mme Sabrina) · **Cozy** (intime) | **LIVE https://luxuryclub229.com** (Cloudflare Pages `luxury-club-229`) · ⚠️ **déploiement avec `.`** : tout fichier manquant sur le disque disparaît du site · **VAGUE 2026-09-05 — LES 4 DEMANDES DE GLORIA + LA DIRECTION « LA LUMIÈRE »** (détail `_memoire/conversations/2026-09-05-luxury-skin-clinic-gloria-et-la-lumiere.md`) : ⛔ **la consultation gratuite est supprimée** — et c'était un MOTEUR, pas une ligne : les deux questionnaires (`SKIN_FORM`, `HAIR_FORM`), leurs modales et le moteur multi-étapes n'avaient plus de porte d'entrée, un `getElementById` sur un élément disparu **cassait tout le JS** (retirés, **récupérables dans git**, −30 Ko) · **du lundi au samedi, 10h-17h** (9 endroits) ⚠️ **48 boutons de date au lieu de 16** → 12 visibles + « autres dates », et le créneau de **9h tombait avant l'ouverture** · **SOIN VISAGE CLASSIC 15 000 F** ajouté · **Diagnostic Capillaire 5 000 F → CONSULTATION CAPILLAIRE PREMIUM 30 000 F** (⚠️ c'est un **rendez-vous**, pas un formulaire : l'analyse se fait pendant la consultation) · **DA « LA LUMIÈRE »** = *la lumière qu'on approche d'une peau, d'abord pour la lire, ensuite pour la révéler* → **une animation par zone** (la lampe qui passe · le filet · les trois foyers · le défilé · l'examen · le trait qui se trace · les étapes qui s'allument · le créneau qui s'illumine · le halo qui se referme) + **onze croquis, un par soin** (il y en avait quatre) · **19 ambiances générées ~2,66 $** ⛔ aucune ne montre visage/peau/cheveu/main/produit/intérieur · ⏳ **Mongazi veut des images de SOINS** (gestes, massages) : **`_outils/_gen_soins.py` est prêt**, mais **WaveSpeed est à 0,03 $ et Higgsfield à 0 crédit** — recharger, lancer, regarder, `--poser` · ⛔ **AU SURVOL LES BOUTONS PASSAIENT EN OR ET LE TEXTE RESTAIT CRÈME : 3,29:1** (*un aplat d'or porte du texte foncé*) ; défauts antérieurs : « Accueil » 2,72 · « réalisé par » 2,49 · pastille de filtre Cozy **1,59** · nouvelles valeurs `--or-texte:#7d5f18` `--gris-f:#63605a` `--menthe-f:#42695b` `--rose-texte:#9c5468` · **`_outils/_qc.py` MESURE LE CONTRASTE SUR LES PIXELS RENDUS** (136 verts clinique · 29 hub · 32 INA · 32 Cozy) ⚠️ **quatre fois c'est la SONDE qui mentait** (elle lisait la couleur après l'avoir rendue transparente · mesurait sous la bande de bord · mesurait pendant la révélation · accusait une image rognée par `overflow:hidden`) · ⛔ **les pastilles sociales se posaient SUR « ENTRER » et sur les titres** → **bande de bord opaque sur les 4 pages** · ⚠️ **une règle posée AVANT celle qu'elle corrige ne sert à rien** (bande d'image sur le sous-titre des 3 univers) · ⚠️ `.marble::before` **plein écran en `mix-blend-mode` animé en boucle** retiré du hub ET d'INA (dépense mesurée sur Angy Art) · ⛔ `consultation-peau.jpg` est un **avant/après de provenance inconnue** : jamais intégré, ne doit pas l'être · ✅ **EN LIGNE le 2026-09-05** ⚠️ **ON NE DÉPLOIE PLUS AVEC `.` MAIS AVEC `_dist`** (`python _outils/_dist.py` puis `wrangler pages deploy _dist --project-name luxury-club-229 --branch main` ; ⛔ depuis le 2026-09-11 il exclut aussi **le devis tablette à 420 000 F**, posé dans le dossier du site par une branche du 2026-08-29, qui serait parti en ligne) : ⛔ **`CONTEXT.md` (notes internes, prix) et 7,2 Mo de photos SOURCES de Gloria (`assets/_inbox/`) étaient publiquement téléchargeables** — mesuré en 200, référencés nulle part, depuis des mois ; le livrable passe de 36 Mo à **9,9 Mo** · ⛔ **`404.html` ajoutée** : sans elle Pages servait **l'accueil en 200** pour toute adresse inconnue · **`_headers`** = en-têtes de sécurité + cache **d'une heure** sur `/assets/*` ⚠️ **jamais `immutable`** ici (pas de `?v=` sur les images) · ⏳ **une copie périmée survit dans le cache DE PAGES** (pas celui de la zone : ni `purge_everything` ni la purge par URL ne l'atteignent, une clé fraîche rend déjà 404) — expire seule sous 7 jours, revérifier après le **2026-09-12** · 🤖 **PASSE GEO 2026-09-09** (skill `ai-seo`) : **la porte d'abord** — Cloudflare bloque les robots d'IA par défaut, **vérifié en se présentant comme chacun** (GPTBot, ClaudeBot, PerplexityBot, Googlebot : **200**), et le `robots.txt` les nomme · **une FAQ de 8 questions** écrite pour être citée (une question posée comme on la pose, 40-60 mots qui tiennent debout seuls) ⛔ **chaque réponse vient de la page** et ⚠️ **une phrase inventée a été attrapée avant publication** (« l'acompte se déduit du montant » : le site dit qu'il valide le créneau, jamais qu'il se déduit) · ⚠️ **le `FAQPage` est LU dans les questions visibles** et **un contrôle compare les deux côtés** · **`/llms.txt` et `/tarifs.md`** produits par `_outils/_llms.py` **en lisant les pages** (un agent qui compare des prestations lit un fichier, il ne rend pas une page) ⚠️ **à relancer après tout changement de tarif ou de FAQ** · **QC 136 → 147** · ⏳ **ce qui pèse le plus ne se fait pas d'ici** : une marque est citée **6,5× plus via un tiers** que via son domaine (fiche Google, annuaires) ⛔ **aucune statistique inventée** · 🔍 **PASSE SEO 2026-09-05, tout mesuré en ligne** : ⛔ **CLS 0,52 / 0,51 / 0,19** (seuil 0,1) — **mon rai de lumière s'animait en `left`** et pesait 0,49 à lui seul (→ `transform` ; *on anime `transform` et `opacity`, jamais une propriété de mise en page*), la **rangée de filtres de Cozy** était construite en JS (⚠️ **réserver la hauteur ne suffit pas** : une liste FIXE s'écrit dans la page), le **menu + la grille d'INA** poussaient le pied de 600 px → **après : 0,003 · 0,002 · 0,010** ⚠️ **alléger les images RÉVEILLE le décalage** (INA 0,013 → 0,193 juste après) · ⛔ **la page INA pesait 1,5 Mo** : 26 photos en 1179 px (export brut de téléphone, jusqu'à 350 Ko) quand les 25 autres font 28 Ko → `_outils/_alleger.py` **3 287 → 725 Ko**, avant/après indiscernable, **INA 1 508 → 450 Ko** · **balisage LU dans la page** (`_outils/_jsonld.py`) : horaires lundi→samedi + **11 soins en `Offer`** ⛔ aucune note, aucun avis, **aucune adresse inventée** · les **3 pages d'impression étaient indexables** → `noindex` · ⏳ **fiche Google, Search Console et l'ADRESSE EXACTE ne se font pas d'ici** | **0167975626** |
| 05 | Saeir Thiam | **Djambar Team** (⚠️ JAMAIS « groupe » — redondant avec « team » ; dire « la maison » / « les pôles ») — pôle **Saeir Thiam Bijouterie** (or/argent/sur-mesure) + comm./événementiel à venir · Cotonou (Agla Gbodjètin) · hub multi-pages évolutif | **LIVE https://djambarteam.com** (domaine final, Cloudflare Pages) · finition complète 23/06 (motion, hero nuit vidéo, formulaire devis→WhatsApp, conversion, ergonomie mobile) · 24/06 « groupe » retiré partout (→ « la maison »/« Cotonou ») · 24/06 **V18** : 11 animations signatures par section (bijouterie) + pôles différenciés (Comm = studio/égaliseur, Événementiel = scène/projecteurs) · **V19 conversion** (FAQ+FAQPage, process 3 étapes, garantie, barre CTA mobile+tel:) · **V20 héros média** (accueil still chaîne d'or Ken-Burns + bijouterie vidéo joaillerie 376 Ko) `?v=20260625b` · reste : **vrais avis + photos sans watermark + fiche Google Business** | 0197967671 |
| 06 | Samelia FAGBOHOUN | **Miss cakes** — pâtisserie artisanale en ligne (gâteaux sur commande) · Cotonou · page unique vitrine + catalogue commandable | **LIVE https://miss-cakes.pages.dev** (Cloudflare Pages, skill `nebula-site`) · motion spectaculaire (drips glaçage, CTA AA raspberry) + **une animation signature DIFFÉRENTE par section `?v=20260624c`** (hero parallax, engagements ligne dorée, La maison clip+unfold, créations en perspective, galerie scatter, éditorial Ken-Burns, avis slide+étoiles, commander poussière de sucre, contact tampons, CTA confettis) + **boutons Liquid Glass** (verre raspberry/vert/givré, AA) + **police texte Bricolage Grotesque** (ex-Jost/Hanken jugés « trop basiques » ; grotesque à caractère) `?v=20260624f` + **VRAIES images câblées** : hero = **vidéo cinemagraph** (cake) + 3 fonds photo (éditorial/CTA/La maison, Nano Banana Pro) · rose poudré + chocolat + crème · formulaire commande→WhatsApp · affiche A4+QR · reste : vrai logo + photos galerie + vrais avis + **confirmer n° WhatsApp** | 2290167748955 (à confirmer) |
| 07 | Ck | **SPEED SHOPPING × WEINKELLER BY CK** — maison « BY CK » à **2 marques/mondes opposés** (la cliente : « deux mondes carrément différents ») · **Speed Shopping** = achat-pour-autrui France→Bénin + colis 2 sens (Cotonou/Paris, bleu) · **Weinkeller by CK** = cave vins/champagnes/spiritueux (Porto-Novo, noir/rouge/or) | **LIVE https://speed-weinkeller.pages.dev** (Cloudflare Pages, skill `nebula-site`, `?v=20260626b`) · concept **hub à 2 mondes + seuil-éclair** (accueil splash façon « match » : éclair central, 1 bouton/côté, sceau CK) — exigence Mongazi « totalement différent » tenue · **Speed** clair/kinetic (Anton, vol France→Bénin animé, 6 catégories, 3 étapes, FAQ+JSON-LD) · **Weinkeller** sombre/cave (Cinzel+Spectral, silhouettes bouteilles SVG, sélection filtrable placeholder « à valider ») · logo Speed détouré, OG×3, affiche A4+2 QR · **n° : Bénin +229 0197158484 (confirmé Mongazi, MÊME pour les 2 marques) + France +33761666887** · **2e passe 2026-06-26 `?v=20260626c`** : **8 CHAMPAGNES RÉELS** (Ruinart/Moët/Veuve Clicquot/Lanson/Nicolas Feuillatte, photos client détourées fond→transparent `_build_bottles.py`, noms+prix) + **3D/animations** = **coverflow 3D** champagnes au hero (perspective, reflets, halo, auto+drag+fiche live) + cartes photo profondeur 3D + poussière d'or · reste : **autres caves Weinkeller (rouges/spiritueux… noms+prix+photos)** · logo Weinkeller défin. · adresses Maps exactes · **facturiers séparés = outil distinct** · **VAGUE 2026-07-01 (`?v=20260701m`, détail `_memoire/conversations/2026-07-01-speed-weinkeller-evolutions.md`)** : Weinkeller = **vrai logo blason** (loader/nav/favicon/OG) + **3 fiches services animées** (Commande spéciale import FR/DE→BJ · Événementiel · Bar à domicile, animations distinctes) + **bannière provenance FR+DE dans le héros** & **carrousel champagnes en bas** + **8 catégories** (Vins/Champagnes/Whiskys/Tequila/Rhum/Gin/Pastis/Vodka, 6 « bientôt »→état vide commande spéciale) + **architecture = drawer DROIT global** ouvert par **bouton brillant à gauche (auto-masqué quand « Parcourir » visible)** + **recherche de boissons** + **pop-up coffrets à chaque visite** (exit-intent+animation) · Speed = refonte 4 services+N.B.+carrousel bas + **typo compacte mobile** + nav sans « Commander » + barre mobile « Appeler » seul · commun = **bruitage de touché** + perf(golddust idle)+révélations distinctes/zone + cibles ≥44 + retrait « à valider/à confirmer » + **bloc légal en pied** (confidentialité/conditions-usage/mentions par marque) + **affiche A4+QR** régénérée (`assets/docs/Affiche_BY_CK_A4.pdf`) · ⚠️ bumps/sync **via Node/Python UTF-8** (jamais PowerShell Get-Content/WriteAllText = mojibake) · **VAGUE 2026-07-02 (`?v=20260701n`, détail `_memoire/conversations/2026-07-02-speed-weinkeller-whiskys.md`)** : catégorie **Whiskys ACTIVÉE** (10 = 4 single malts Lagavulin/Aberlour/BenRiach + 6 cognacs Hennessy/Martell/Rémy/Camus · sous-filtres **Single Malt/Cognacs**) + **Rhum** (Eminente Reserva) — vraies bouteilles Ck **détourées IA rembg** (`_build_whisky.py` isnet 1100px + `_apply_whisky.py` inject idempotente UTF-8) · 3e carte « Nos caves » Whiskies&cognacs · notice en-stock MAJ · QC Playwright (32 bouteilles, 0 err/0 404, détourage sans halo) déployé+vérifié 200 · **Eminente laissé en Rhum ⏳ att. réponse Ck** · **Martell VS(65k)>VSOP(60k) confirmé garder** (Mongazi) · **VAGUE 2026-07-13 (`?v=20260713a`, détail `_memoire/conversations/2026-07-13-speed-weinkeller-catalogue.md`)** : catalogue **60 fiches** (+28 bouteilles détourées rembg) · **2 nouveaux onglets = Cognacs + Apéritifs & liqueurs** (Cognacs sortis des Whiskys→onglet dédié, Whiskys à plat, Ricard→Apéritifs, **Pastis retiré**) · répartition Champagnes 13/Whiskys 15/Cognacs 6/Tequila 8/Rhum 6/Gin 4/Vodka 1/Apéritifs 7, seul **Vins** reste « bientôt » · **Clase Azul Reposado image corrigée** (re-détour) · 6 sans prix « Prix sur demande » ⏳ att. Ck · `_build_newcave.py`+`_apply_cave.py` idempotents UTF-8, `_dist` allégé 5,9 Mo (sources `gallery`/`Wenkeller` exclues) · déployé Cloudflare + vérifié 200 | +229 0197158484 (les 2 marques, confirmé) |
| 08 | HH Design | **HH DESIGN** — **maison d'ébénisterie / mobilier bois noble** à Cotonou (⚠️ PAS immobilier : erreur de 1er brief corrigée le 2026-07-04 via les planches de marque `_partage/inspiration 1..8.JPG`) · meubles bois massif faits main (étagères, bibliothèques, tables de chevet, tables basses, consoles) · bois mindi/acajou, finitions roasted coffee/naturelle/pearl brushed · « L'élégance du bois » / « Créé pour durer, pensé pour vous » | **LIVE https://hh-design.pages.dev** — **REFONTE TOTALE v2 2026-07-04** (crème sable + bois + or vieilli + espresso, **Cormorant Garamond + Archivo**) : hero bois brut Ken-Burns · manifeste espresso 3 piliers · **collection filtrable des VRAIES pièces** (Ayula/Leon/Cancun/Tabasco/Natura/Console) en cartes « spécimen » → **fiche modale** (specs + WhatsApp pré-rempli « commander/sur-mesure ») · bande ambiance · **matières & finitions** (4 échantillons bois) · sur-mesure 4 étapes · contact form→WhatsApp · **vraies photos extraites des planches** (WebP ~250 Ko) · affiche A4 + 2 QR (site+WhatsApp) refaites · QC impeccable+node+captures OK · ⚠️ v1 immobilière (blanc/or/noir Marcellus) OBSOLÈTE · reste : **confirmer n° WhatsApp** + vrai logo + handle IG + adresse Maps + prix | **+229 01 62 68 67 68** (⚠️ à confirmer · issu des planches HH · remplace l'ancien 0167975626) |
| 09 | Au Braisé d'Or | **Au Braisé d'Or** — restaurant **braisé / grillades au feu de bois** à Cotonou (« De Paris à Cotonou ») · **catalogue digital** + traiteur & place des fêtes | **LIVE https://au-braise-dor.pages.dev** · ⚠️ **l'adresse sert le projet Next.js de `experience/`** depuis le 2026-08-12 (Next 14 + TypeScript + Tailwind + GSAP + Swiper + Lenis, pile maintenue par Mongazi), plus `index.html` · ⚠️ **mais `index.html` reste la vérité des données** : `node _outils/_extraire_carte.js` en tire `experience/data/carte.ts`, qu'on n'édite jamais à la main · **53 plats en 9 rubriques** + un **héros des 14 sauces** où l'on commande (un pont vers la fiche de la carte, pas un second moteur) · ⚠️ **le héros lit le `DECO` de `dishes.ts`, pas le dossier** : une photo livrée n'est affichée qu'une fois déclarée · **cinq façons d'avoir un prix** (`p` · `p2` deux tailles · `pMax` fourchette · `paliers` · `p:0` prix sur demande, jamais au panier) + **`choix`** obligatoire à prix égal (attiéké poisson ou viande) · publier = `npm run build` + `cp -r ../assets/docs out/` + `wrangler pages deploy out --project-name au-braise-dor --branch main` · QC `python _outils/_qc.py` **117 verts** + `_qc_partage.py` **36** · ✅ les photos de plats générées par IA sont **gardées, sujet clos** (Mongazi, 2026-08-20) : héritage de ce client, la règle du 2026-08-01 reste entière ailleurs · ⛔ **LE SITE PORTE DEUX NUMÉROS** : `index.html` `2290156057157`, `dishes.ts` (le fichier servi) `22956057157` sans le `01`, rien touché, à trancher · ⏳ la photo de l'attiéké (Mongazi l'envoie) et sa description, vraie photo de la salle, vrais avis, adresse et Maps, logo, réseaux, « gbata » ou « gbotâ » · **tout le détail : `clients/09-au-braise-dor/CONTEXT.md`** | 0156057157 (à confirmer, vs 43 99 29 29 enseigne · ⚠️ **et `dishes.ts` en utilise un AUTRE, sans le `01`**) |
| 10 | Hillary | **HILLARY M. STYL** — maison de couture (monogramme H.M.S) · prêt-à-porter par tailles **+ sur-mesure** · magenta `#E6007E` + encre, Bodoni Moda + Archivo + Manrope | **LIVE https://hillary-m-styl.pages.dev** · **V4 « LA COUPE »** (magenta = sa signature, une animation signature par section) · ⚠️ **on édite `_v4/*`**, jamais `_vitrine_src.html` ni `vitrine.html` : `python _v4/_assembler.py` monte la source et refuse d'écrire si l'un des 18 identifiants du moteur manque, et les morceaux `garde-*` (modale, toucher, moteur) ne sont jamais régénérés · publier = `python3 _predeploy.py` (assembleur, construction, QC, puis `_dist/`) puis `wrangler pages deploy _dist --project-name hillary-m-styl --branch main` (**wrangler 3 global**, `npx wrangler` ne marche plus sur le PC) ⚠️ **si le QC échoue, `_predeploy.py` s'arrête AVANT `_dist/`** : déployer quand même republie l'ancienne version sans un mot · QC `python _qc.py` **192 verts** · **19 pièces, toutes en sur-mesure, toutes avec leur photo** (face et dos qui basculent, héros de 16 diapositives ordonnées en ΔE L\*a\*b\*) · **panier** : délai = la pièce la plus lente, supplément express propre à chaque pièce, aucun prix stocké · commande : **prénom, nom, téléphone et lieu de résidence obligatoires** + ville de livraison · Mobile Money seul, rien n'est payé sur le site · détourage **`birefnet-general`** (isnet efface l'organza), **un processus par photo** · ⛔ « Ensemble Volants » **retiré le 2026-08-27** : fiche fabriquée par Claude le 2026-08-16, doublon de h10 (**six prix identiques = doublon jusqu'à preuve du contraire**) · ⛔ la branche `claude/github-repo-context-nisd2r` est **périmée** (la fusionner supprimerait 30 790 lignes) · ⏳ les **11 mesures de la robe ovale**, la matière de chaque pièce, le sac beige de l'Ensemble Orange, « PRÊT-À-PORTER » encore au héros, les originaux non sauvegardés (`_sources/` ignoré, dépôt public), **l'adresse** (bloque la fiche Google, dossier `GOOGLE-BUSINESS.md`) · **tout le détail : `clients/10-hillary-m-styl/CONTEXT.md`** | **+229 51 37 47 93** ✅ posé et EN LIGNE (`wa.me/22951374793`, donné 2026-08-01 · ⚠️ tester une fois : le dépôt a 2 formats, sinon `2290151374793`) |
| 11 | Angélique AVOCEVOU | **ANGY ART** — **artiste plasticienne** · Cotonou · œuvres contemporaines en relief sur l'identité, la mémoire et le patrimoine africain (scarifications, symboles, masques, textiles) · portfolio + moteur de demande | **LIVE https://angyart.online** (son nom de domaine depuis le 2026-09-10 · Cloudflare Pages `angy-art`, l'origine `angy-art.pages.dev` répond toujours et le `canonical` la déréférence) · portfolio éditorial noir `#0a0a0a` / crème `#f3efe6`, Playfair Display + Public Sans, **son or `#bd9f64`** (`#7e6d3a` sur fond clair) · **aucune bibliothèque** · **aucune image générée** : photos d'atelier réelles, « MISE EN SITUATION » écrit sur les décors montés · **six œuvres nommées par elle, SANS PRIX depuis le 2026-09-05** ⚠️ un prix vivait à quatre endroits (cartel, message WhatsApp, `Offer` du JSON-LD, phrases) et **`llms.txt` n'en porte aucun**, un contrôle le vérifie · **« Ma sélection »** = une liste sans total, un seul message · **créations sur mesure** : 15 questions, le formulaire rédige un message WhatsApp et ne soumet rien · navigation = barre à 6 entrées + WhatsApp, sommaire du héros, bouton « Découvrir » flottant qui **s'ajoute** · **musique EN LIGNE** : WETHU (*Culture Capital*, a remplacé le lofi le 2026-09-10), `<audio loop>` nu, part au premier contact, coupure mémorisée, marque `VER_SON` à part, crédit au pied, licence **tranchée par Mongazi, sujet clos** · ⚠️ **assets `immutable` un an : bumper `?v=` à chaque modification d'`app.css` ou `app.js`** · ⛔ **ne pas remettre le grain plein écran** (`mix-blend-mode` fixe) · publier = **`python clients/11-angy-art/_publier.py`** (récupère `main`, QC, `_dist`, déploie, **purge le cache de zone**, vérifie ce qui est servi) ; une session distante ne peut pas publier · QC **244 verts** · ⏳ photos des œuvres seules, adresse, vrais avis, tester le numéro, et à trancher : l'obfuscation d'e-mail de Cloudflare (illisible sans JavaScript) et les tranches de budget du formulaire · **tout le détail : `clients/11-angy-art/CONTEXT.md`** | **+229 01 52 00 64 90** (⚠️ à tester une fois : 8 et 10 chiffres coexistent) |

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

### LE PLI — la lettre digitale  *(produit interne, 2026-09-02 · **idée arrêtée le 2026-09-06**)*
- **Ce que c'est** : « une lettre digitale, c'est **une enveloppe cachetée qu'on
  ouvre à l'heure dite** ». L'acheteur écrit son mot, choisit l'heure, paie ;
  il envoie le lien lui-même, elle brise le cachet à l'heure dite, et lit.
  Dossier de décision : `_plans/2026-08-27-lepli-dossier.html` · manuel
  d'exploitation : `_plans/2026-08-28-lepli-manuel.html` · **arrêté (les 12
  décisions) : `_plans/2026-09-06-lepli-arrete.html`** · conditions et retrait :
  **`lepli/CONDITIONS.md`** · code : **`lepli/`**.
- **La thèse** : *le romantique est le marketing, l'événement est le chiffre
  d'affaires, le B2B est la retraite.* Un seul moteur, trois habillages.
- ✅ **LE NOM EST TRANCHÉ LE 2026-09-09 : LE PLI.** Mongazi : « je préfère le
  pli ». **Une seule enseigne**, et ⛔ **MINUIT disparaît comme marque** — le
  mot « minuit » ne survit que là où c'est le mot français (« elle s'ouvre à
  minuit pile »), jamais comme enseigne : garder les deux ferait deux vérités.
  ⚠️ **Le défaut qui a tué MINUIT, mesuré sur les trois registres** : il nommait
  une HEURE, donc il allait à la lettre d'amour, passait sur un faire-part de
  mariage, et ⛔ **ne passait pas sur une annonce de décès** (« MINUIT · Famille
  Dossou »), la ligne à 15 000-50 000 F. Des quatre finalistes (MINUIT · LE PLI ·
  LE CACHET · MISSIVE), **seul LE PLI passe les trois, parce qu'il nomme l'OBJET
  et pas l'occasion** (« un pli », c'est littéralement une lettre qu'on fait
  parvenir). ⚠️ **Le sous-domaine étant tranché** (`lepli.nebula-agency.online`),
  aucun domaine n'était à acheter : la disponibilité n'a contraint personne.
  **Renommé le jour même**, avant la première vente : `minuit/` → **`lepli/`**,
  schéma `minuit` → **`lepli`**, `minuit-*` → **`lepli-*`**, `MINUIT_DONNEES` →
  **`LEPLI_DONNEES`**, `minuit:brouillon` → **`lepli:brouillon`**, la vidéo et
  ses compositions, et l'enseigne partout. **333 remplacements, 28 fichiers**,
  QC **145 + 118 toujours verts**. ⚠️ **Un renommage mécanique abîme les textes
  qui COMPARENT les deux noms** : la note de la veille est ressortie en « LE PLI
  nomme une HEURE » et « les finalistes LE PLI · LE PLI » — relire les endroits
  où l'ancien nom était cité comme objet d'analyse, pas comme enseigne.
  ⛔ **Les documents datés gardent l'ancien nom** (`_plans/2026-08-27-minuit-*`,
  `_plans/2026-09-06-minuit-arrete.html`, les journaux, les conversations, les
  leçons) : à cette date le produit s'appelait MINUIT. L'arrêté porte un bandeau
  qui renvoie ici.
- **Fait le 2026-09-02** : **le gabarit** (`lettre.html`) et **le constructeur**
  (`creer.html`), **78 contrôles verts** (`python lepli/_qc.py`).
- 🕛 **FAIT LE 2026-09-06 — LA LETTRE TIENT L'HEURE ELLE-MÊME** (détail
  `_memoire/conversations/2026-09-06-lepli-finalisation.md`) : ⛔ **la fonction
  qui donne son nom au produit n'existait NULLE PART** — l'heure était demandée à
  l'acheteur, promise sur l'écran final (« elle la recevra le 14 février à
  00:00 ») et n'entrait dans aucune lettre ; ⚠️ **aucun contrôle ne pouvait le
  voir** (on ne mesure pas l'absence d'une chose dont personne n'a écrit qu'elle
  devait exister, même famille que la photo livrée et jamais affichée chez Au
  Braisé d'Or) · ⛔ **n8n, à qui le dossier ET le manuel confiaient la livraison,
  tournait sur le VPS Hostinger `72.61.103.56` qui n'appartient plus à
  Mongazi** : la fonction reposait sur une machine perdue → **elle vit dans la
  LETTRE**, qui ne dépend de rien et tient même si l'acheteur envoie son lien
  trois jours trop tôt · **avant l'heure le cachet dort** (cire éteinte, aucun
  bouton), la page **DIT** quand elle s'ouvre et compte à rebours, **à l'heure
  la cire s'allume** et le bouton paraît **sans rechargement** · ⚠️ **le
  garde-fou est dans `ouvrir()`, pas sur le bouton** (le code secret appelle
  `ouvrir()` directement) · ⚠️ **heure de CALENDRIER, sans fuseau** : minuit,
  c'est minuit **sur le téléphone de celle qui lit** (un instant absolu ferait
  s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou) ·
  ⛔ **on ne promet JAMAIS le secret** (le texte est dans la page) : le cachet
  tient l'heure, c'est tout, et c'est déjà ce que personne d'autre ne vend ·
  ⛔ **NEBULA n'écrit jamais à la destinataire** → plus besoin du modèle Meta
  hors fenêtre de 24 h, et le risque de harcèlement disparaît par conception ·
  **2 défauts de caisse** : ⛔ **deux échelles de prix** (les occasions
  portaient un « dès 10 000 F » appliqué nulle part → on prenait « Demande en
  mariage · dès 10 000 F » au palier gratuit et on payait **0 F** ; l'occasion
  décide du TON, le palier décide du PRIX) et ⛔ **le palier gratuit passait par
  la caisse** (`aller(p.prix === 0 ? "e-paiement" : "e-paiement")`, deux branches
  identiques = intention écrite puis perdue : une lettre offerte affichait
  « Envoie exactement cette somme, au franc près » au-dessus d'un numéro Mobile
  Money) · ⛔ **le seuil n'était mesuré par rien** alors qu'une lettre programmée
  ne montre que lui pendant des heures : le même gris tient 4,8:1 sur le papier
  et **3,09:1 sur la nuit**, mesuré → `--gris-nuit` · **QC 82 → 115**, avec un
  **TÉMOIN** à chaque verrou (heure passée, palier payé) sans quoi un verrou
  resté fermé pour toujours passerait avec les honneurs.
- 🏦 **LA CAISSE ET L'ADRESSE SONT ÉCRITES ET CONTRÔLÉES le 2026-09-06**
  (marche à suivre : **`lepli/PAIEMENT.md`**) — ⏳ **rien n'est déployé**, il
  manque 5 réponses de Mongazi (le sous-domaine est tranché le 2026-09-09) : **schéma Supabase `lepli`** + **3 fonctions
  de bord** (déposer+payer · la notification signée qui **ouvre la lettre** ·
  servir+**retirer**), sur la forme éprouvée de PISTE · **`_shared/lettre.ts`
  porte TOUT ce qui décide**, en Web standard, donc essayable **sans clé, sans
  réseau et sans base** (`node --experimental-strip-types lepli/_qc_caisse.mjs`,
  **118 contrôles**) · **le constructeur parle enfin à la caisse** (il posait sa
  commande sur `window.LEPLI_COMMANDE` et elle n'allait nulle part) ·
  ⛔ **ON NE STOCKE JAMAIS LE HTML DU NAVIGATEUR** : une porte publique qui
  accepte du HTML et le sert sur notre domaine est un **hébergeur de pages
  arbitraires**, gratuit et anonyme — on stocke les **données**, la lettre est
  **rebâtie** depuis le gabarit (`_gabarit_ts.py` l'y recopie, un contrôle
  compare) · ⛔ **le prix ne vient jamais du navigateur**, ni le pied viral, ni
  le code secret : un contrôle **lit les deux barèmes** et refuse la moindre
  différence · ⛔ **l'écran « colle la référence de ton SMS » DISPARAÎT**, avec
  le numéro Mobile Money et le choix du réseau (c'était le moment le plus
  fragile de la chaîne) · ⛔ **le brouillon ne s'efface qu'après une réponse
  heureuse** · ⛔ **le retrait passe avant tout** (état, date, remboursement) ·
  ⚠️ **U+2028 EN CLAIR dans les regex qui doivent le neutraliser, 3e et 4e fois**
  (dans `lettre.ts`, puis dans le contrôle qui l'essaie) : **un fichier qui
  documente son propre piège doit être vérifié comme s'il le contenait** ·
  ⚠️ **2 sondes menteuses** (l'une lisait la ligne d'**import** au lieu de
  l'appel ; l'autre interrogeait `pg.url` **en boucle pendant une navigation**,
  or le contexte d'exécution est détruit → `wait_for_url`) et ⛔ **`localStorage`
  appartient à l'ORIGINE** (lu depuis la page de paiement, il rend le rangement
  d'un autre site) · ⚠️ **3 contrôles RETOURNÉS**, pas supprimés · ⚠️ **un
  3e sérialiseur = une 3e vérité** : Python écrivait `"a": 1` là où les deux
  autres écrivent `"a":1` → séparateurs compacts partout, et le contrôle exige
  **le même octet** des deux implémentations · **QC 115 → 127 + 118**
- ⏳ **CE QUI RESTE** : **brancher** la caisse (5 commandes, `PAIEMENT.md`) ·
  ⛔ **PAS de Render avec le SQLite de `vitrina/`** : le disque de Render
  s'efface à chaque déploiement (c'est ce qui avait fait disparaître les 2 PDF
  des partenaires) — un déploiement, et les lettres payées n'existent plus ·
  le **ménage des lettres expirées** (`lepli_menage()` existe, rien ne
  l'appelle) · le **lien « retirer cette lettre »** dans le pied (la porte
  existe, le bouton non) ·
  **le faire-part pour NOVEMBRE** (saison des mariages + retour de la diaspora,
  ticket 25 000 F), pas pour février (volume, petit ticket) · **critères
  d'arrêt au 1er décembre 2026**, écrits d'avance.
- ⏳ **Les 5 réponses qui n'appartiennent qu'à Mongazi** (le sous-domaine est
  tranché depuis le 2026-09-09 : `lepli.nebula-agency.online`) : le compte qui encaisse ·
  **un n8n tourne-t-il ailleurs, oui ou non** · la commission
  SasPay (elle décide de la marge d'un ticket à 2 000 F, écrite nulle part) ·
  qui relit le deuil · **le premier franc encaissé pour de vrai**.
- **Fait le 2026-09-03** : **la vidéo de démonstration**, composition
  `lepli-demo` dans `_studio-video/` (1080x1920, 30 s, `npm run rendu:lepli`).
  Six plans, **les six signatures du produit rejouées en React** et non
  photographiées : une capture ne montre pas un cachet qui se brise. ⛔ **Ne pas
  la publier en l'état** : elle promet « Elle l'ouvre à minuit pile. Pas
  avant. » et affiche `lepli.nebula-agency.online`, or **ni la remise à
  l'heure dite ni le serveur n'existent** au 2026-09-03. ✅ **Depuis le
  2026-09-06 la promesse est tenue** (la lettre porte le verrou) : il ne reste
  que l'adresse affichée, qui doit exister avant publication.
  ⛔ **Jamais de fondu enchaîné entre deux plans qui
  montrent du papier** : mesuré, deux feuilles à 50 % l'une sur l'autre
  ressemblent à une panne, pas à une transition (les plans partagent le même
  fond de nuit, donc la coupe est déjà invisible).
  Détail : `_memoire/conversations/2026-09-03-lepli-video-demo.md`.
- ⛔ **`</script>` écrit par un acheteur TUE la page** : les données atterrissent
  dans un bloc `<script>`, et **`json.dumps` ne protège pas de ça**. Toute
  sérialisation passe par **`lepli/_injecter.py`**, seul endroit, qui neutralise
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
- ✅ **AVANT LA PREMIÈRE VENTE : `lepli/CONDITIONS.md` est écrit** (le dossier
  classait ce risque en *critique* et notait qu'aucune des 5 références ne le
  traite) — adresse impossible à deviner, `X-Robots-Tag` en plus de la balise,
  expiration (7 jours offert / 1 an payé), aucune mesure d'audience, et
  **retrait sous 24 h à la demande de la personne visée, sans discuter, sans
  prévenir l'acheteur, sans rembourser** : ⚠️ **le pouvoir de retirer appartient
  à qui détient le lien**, ce qui est exactement l'ensemble des gens concernés.
  ⛔ **Jamais de MP3 hébergé** (contrefaçon). ⚠️ **Le deuil ne se décore pas** :
  sobriété totale, aucun emoji, relecture par quelqu'un qui vient d'enterrer un
  proche **avant** de le vendre, et c'est la condition d'ouverture de la ligne.

### LE STANDARD — l'agent WhatsApp des clients  *(produit interne, 2026-08-28)*
- **Ce que c'est** : celui qui décroche. Un client écrit sur le WhatsApp d'une
  maison, l'agent répond avec **la carte réelle de cette maison**, prend la
  commande, prévient le patron, et **passe la main dès qu'il ne sait pas**. Les
  onze vitrines finissent toutes sur « écrire sur WhatsApp » : c'était le seul
  maillon que personne n'avait automatisé.
- **Où** : `whatsapp-agent/` · `python whatsapp-agent/demonstration.py` (le voir
  travailler, garde-fou compris) · `simuler.py <maison>` (lui parler) ·
  **`installer.py`** (l'assistant : deux numéros, un jeton, et c'est branché) ·
  `_qc.py` (**171 contrôles**, sans clé et sans réseau) · `serveur.py` = le webhook.
- **QUATRE CANAUX, et le choix compte** : ⚡ **Whapi.cloud** branche le WhatsApp
  ORDINAIRE du client en scannant un QR code — ni vérification d'entreprise, ni
  Phone Number ID : c'est le chemin qui met un commerçant de Cotonou en ligne le
  jour même. ⚠️ **Ce n'est PAS l'API officielle** : abonnement mensuel par numéro
  et **WhatsApp peut suspendre un numéro qui automatise par ce chemin** (un
  restaurant qui perd son numéro perd son carnet d'adresses) → pilote oui,
  définitif non. ⚠️ **Whapi ne signe pas ses appels** : poser `WA_WHAPI_SECRET`
  et le recopier dans les « custom headers » (`X-Nebula-Secret`), sinon
  l'adresse du webhook suffit à faire parler l'agent d'un client — le serveur le
  crie au démarrage. · **Meta Cloud API** = l'officiel, à livrer. · **Twilio** =
  le bac à sable. · **console** = les essais.
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

### NEBULA TRADER · agent de trading EUR/USD + NAS100  *(produit interne, 2026-09-16)*
- 🔴 **REPRENDRE ICI : `trading/JOURNAL.md`, section « POINT D'ARRÊT EXACT ».** Au
  2026-09-17 : vagues 1 à 4 **livrées**, EUR/USD + NAS100 en observation, QC 209 verts.
  🔬 **Recherche de stratégies faite** (`trading/RECHERCHE-STRATEGIES.md`, banc `trading/recherche/`) :
  5 stratégies publiées + 3 vidéos, sur M1 à H4 et jusqu'à 21 ans (MT5 passé en « Unlimited »),
  **146 tests, 0 survit à la correction**, aucun où plus de 50 % des trades atteignent 2 R, rien
  intégré. **R:R 1:2 imposé en PRO et BOOST.** ⚠️ Export MT5 « Unlimited » = bougies factices
  depuis 1971 en M15/H1 : filtrées à la lecture.
  🎯 **3e vidéo « Sniper Entry » (2026-09-17 soir, `trading/RECHERCHE-SNIPER.md`)** : méthode apprise
  et ses exemples retrouvés au dixième de pip, backtest M1 bid/ask + annonces Forex Factory + 10 000 $ :
  EUR/USD **-0,113 R** (2 941 trades, 23,8 %), NAS100 **-0,075 R**, **nulle même sans coûts** ;
  10 000 $ à 1 % → **273 $**. ⛔ **Deriv ne sert aucun tick passé** · ⛔ le jeu Hugging Face
  « Forex Factory » perd l'heure de 40-50 % des annonces (`recherche/annonces.py` lit les pages).
- **Trois objectifs, dans cet ordre** : **être rentable** · **s'améliorer tout seul** ·
  **être vendable** (installable chez n'importe qui, vendu en ligne). ⚠️ **Le 3 découle du
  1** : un robot se vend sur un historique réel vérifié, jamais sur un backtest.
- **Où** : `trading/` · **`trading/CAHIER-DES-CHARGES.md`** (v2, la référence) ·
  `trading/JOURNAL.md` (avancement) · `trading/DOCTRINE.md` · `trading/README.md`.
  **Lancer** : `python -m trading.app` (agent + interface sur http://127.0.0.1:8765/) ·
  **QC** : `python -m trading.outils.qc` (**209 verts**) · **produit** :
  `python -m trading.empaquetage.construire` (zip 44 Mo, `NEBULA Trader.exe`, sans Python).
- ✅ **FAIT le 2026-09-16** : pont MT5 ouvert (compte démo Deriv `6305888`, identifiants
  explicites) · historique MT5 **par année** (34 876 H4 depuis 2005) · profil de coûts
  mesuré (spread médian **3 points** sur 147 161 ticks) · **walk-forward** 4 ans → 1 an ·
  **agent live** (`live/agent.py`, seul fil qui parle à MT5) en **observation** · journal
  SQLite des décisions ET des refus · calendrier économique (indisponible = abstention) ·
  **interface 8 pages** (FastAPI local, jeton de session, HTML sans bibliothèque) ·
  conversation (Claude `claude-sonnet-5` avec outils, ou répondeur local) · réglages validés
  par le videur · coffre **DPAPI** · **licences Ed25519** hors ligne (clé privée dans
  `secrets/nebula-trader-licence.pem`, jamais publiée ; `python -m trading.outils.licence`).
- ⛔ **LES SIX VARIANTES PERDENT** (walk-forward, coûts réels, **règles réellement appliquées**,
  recalculé le 2026-09-17) : EUR/USD cassure week-end gardé **372 trades, −0,045 R, 10 000 →
  8 074** · fermeture du vendredi **−0,021 R** · retour à la moyenne −0,059 / −0,077 R · NAS100
  cassure **−0,095 R** (49 trades) · retour −0,218 R. ⛔ **Le « +0,040 R sur 436 trades » cité
  jusqu'au 16/09 était FAUX** : mesuré avant la règle R:R 1:2 (prouvé : seul ce réglage le
  ramène). **Ne pas passer en réel, ne pas vendre de performance.**
- **Capital pour tous, jamais au-delà du risque** : **compte cent** détecté (10 $ prennent les
  mêmes 71 trades que 10 000 $) · **lot minimum toléré** jusqu'à 2 % · **attente** d'un stop plus
  court. Sur compte standard, rien ne passe sous 250 $ (stop médian 527 points).
- 📐 **CAHIER DES CHARGES DE MONGAZI passé au Monte Carlo** (le 16/09, sur les 436 trades faux) :
  arrêt −10 % à 1 % touché **99 %** du temps · 5 pertes d'affilée sur 100 trades **97 %** ·
  3 %/mois exige **1,30 R/trade** · 30 jours de paper = **2 trades** en H4 · levier x5 et 10 %
  de risque incompatibles (**x21,7** médian). **Décisions de Mongazi** : **BOOST jusqu'à 10 %
  par trade** (recalculé le 17/09 : **55 %** de chances de perdre la moitié en un an,
  affiché au moment du choix, BOOST réel verrouillé derrière la porte PRO de 60 jours de son
  propre cahier) · **seuils de drawdown calibrés au Monte Carlo** · **marchés : EUR/USD et
  NAS100 uniquement**. Détail et intégration par vagues : `trading/CAHIER-DES-CHARGES.md`.
- ✅ **Livré la nuit du 2026-09-16** : profils **PRO** (1 %, plafond 2 %) et **BOOST** (≤ 10 %,
  disjoncteurs en escalier, paliers `[10, 5, 3, 2, 1,5, 1]` à chaque ×2, poche épargne à +50 %) ·
  levier effectif plafonné **en réduisant la taille** · arrêt total **calibré au Monte Carlo**
  (PRO 1 % → 26 % au 17/09) · santé **CUSUM** (remplace « 5 pertes d'affilée », qui sonne 97 % du
  temps) · **porte démo** (30 jours ET 30 trades, soit ~1 an en H4) · porte BOOST réel
  (60 jours de PRO réel) · chien de garde · page Évolution.
- ⚠️ **NAS100 chez Deriv** : symbole **« US Tech 100 »**, historique **depuis 2024-01-22
  seulement**, spread **fixe de 70 points**, lot minimum 0,1 → **3 372 $ minimum à 1 %**
  (EUR/USD : 440 $). ⛔ **Un plafond en points n'appartient qu'à un instrument** : les 20 points
  de l'EUR/USD refusaient 92,8 % des bougies du NAS100 (plafonds par instrument, en prix,
  `[execution.par_instrument]`). ⛔ **Chaque rapport porte l'empreinte des règles**
  (`empreinte_regles`) : l'interface et l'agent disent quand il ne décrit plus l'agent.
- **Décidé** : H4, risque PRO **1 %** (plafond **2 %** écrit dans le code), **positions gardées
  le week-end** (la fermeture du vendredi tue la tendance : 197 sorties forcées, coûts = 344 %
  du brut ; 2 gaps en 15 ans), code agnostique du courtier, **tout ordre part avec son stop
  chez le courtier et la position est RELUE** (sans stop, elle est fermée).
- ⚠️ **LE COÛT EN R décide de l'unité de temps** : 0,02 R en H4 contre 0,19 R en M5.
- ⛔ **PIÈGES MT5 MESURÉS** : `[Experts] Api=1` **coupe** l'API Python (case « désactiver ») ·
  MT5 **éteint le Trading Algo à chaque changement de compte** · `SYMBOL_FILLING_FOK/IOC`
  n'existent pas dans le paquet Python (drapeaux 1 et 2) · une plage de 20 ans d'un coup =
  `Call failed`, **lire par année** · le terminal télécharge l'historique de TOUS les symboles de
  l'Observation du marché (bases 1,2 Go, disque à 4,4 Go) · le champ `spread` d'une bougie n'est
  pas le spread payé.
- ⛔ **DÉFAUTS DU MOTEUR TROUVÉS ET CORRIGÉS** : disjoncteur de série noire verrouillé pour
  toujours (le matin) · **verrous datés à l'ouverture de la barre du signal** (entrée à 00 h
  acceptée pendant « Asie ») · **fermeture du vendredi jamais déclenchée en H4** (la dernière
  barre ouvre à 20 h 00, avant le seuil de 20 h 30 : on compare la FIN de la barre).
- 🔐 **Dépôt PUBLIC** : identifiants dans `secrets/` ou dans le coffre DPAPI de l'application ·
  `.gitignore` refuse `*.env` et `secrets*` (un `notepad secrets\mt5.env` sous Git Bash avait créé
  `secretsmt5.env` à la racine avec le mot de passe) · la construction du paquet **refuse** un
  secret, cherché par nom ET par contenu · ⛔ un jeton collé en clair le 2026-09-16 est à révoquer.
- ⛔ **Interdits par conception** : martingale, grille, moyenne à la baisse, stop élargi,
  apprentissage en direct. Aucun rendement promis nulle part.
- Détail : `_memoire/conversations/2026-09-16-nebula-trader.md`

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

⚠️ **10 SITES SUR 15 N'ONT PAS DE `_headers`** (mesuré le 2026-09-04, fichiers **et**
en-têtes servis) : ni `X-Frame-Options`, ni HSTS, et **aucun cache sur les assets** —
Cloudflare Pages sert alors `max-age=0, must-revalidate` sur tout, donc les 31 images
d'Hillary sont revalidées à chaque visite sur la 3G de Cotonou. En ont un : Djambar, Miss
cakes, Angy Art, Boussole, PISTE. ⚠️ **Les deux réglages vont ensemble** : poser
`immutable` sur `/assets/*` gagne le cache **et rend obligatoire le bump du `?v=`** à
chaque modification d'un asset — l'ajouter à un site qui ne versionne pas ses images
**crée** le piège du cache périmé. ⛔ Rien n'est corrigé, **Mongazi tranche** : c'est un
déploiement vers dix sites clients. ✅ **Luxury Club 229 en a un depuis le 2026-09-05** :
en-têtes de sécurité + cache d'**une heure** sur `/assets/*` — **pas `immutable`**, parce que ce site
ne versionne pas ses images. Gabarit : `clients/11-angy-art/_headers`, détail dans
`_memoire/RESTE-A-FAIRE.md`.

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

⛔ **UN BUMP NE PUBLIE RIEN TANT QUE RENDER N'EST PAS REDÉPLOYÉ** (et Render ne se
redéploie pas au push). Mesuré le 2026-09-11 : la base portait encore les dix PDF
du 3 août alors que trois sessions de septembre avaient bumpé manuel, contrat et
guides, et le commit du contrat 1.5 avait remplacé son PDF **sans** bumper sa date.
Publier = bump + push + `POST /v1/services/srv-d9nni7e7bikc73c9oksg/deploys`, puis
**relire `naff.documents`** (colonne `filename` = la version) : c'est la base qui
prouve, pas le code. En une commande : **`python scripts/verif_documents.py`**
(version et MD5 de chaque document en base contre le dépôt, sortie 1 si l'un est
en retard). Pour décider d'un bump, comparer le **texte** des deux PDF, pas leurs
octets : `_memoire/apprentissages/2026-09-11-prouver-une-publication.md`.

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
- **Contrat partenaire en version 1.5** (2026-09-11) : **NEBULA transmet au partenaire des
  contacts à appeler** (art. 3.5). ⚠️ **Obligation de MOYENS, écrite comme telle** : aucune
  quantité, aucune fréquence, aucune qualité promise, et un mois sans contact transmis
  **n'est pas un manquement** ; chercher ses propres prospects reste la mission du
  partenaire (art. 3.1). **La commission ne bouge pas** (art. 3.6, taux plein, NEBULA ne
  prélève rien). Un contact transmis est **à ce partenaire 60 jours** et à personne d'autre
  (art. 7.6) ; **un contact qui refuse n'est retransmis à personne** (art. 7.7). Ces listes
  sont des **données personnelles qui restent celles de NEBULA** : jamais communiquées, pas
  même à un filleul, jamais versées dans une application tierce, détruites à la fin du
  contrat, détournement = **faute grave** (art. 14.6). ⛔ **CÔTÉ NEBULA, LA RÈGLE QUI NE SE
  VOIT PAS : une fiche sous exclusivité PISTE (90 jours, payée) NE SE TRANSMET PAS** à un
  partenaire — ce serait reprendre d'une main ce que l'autre a vendu, et le client de PISTE
  ne s'en apercevrait qu'en apprenant qu'on a déjà appelé son prospect. Écarter avant
  d'envoyer. **La 1.5 n'enlève rien** : le préavis de l'art. 6.7 ne joue pas, un partenaire
  en 1.4 signe la 1.5 sans formalité
- **Version 1.4** (2026-09-03) : cosigné pour NEBULA par **Romaric DJANKAKI**, responsable du
  réseau partenaires, soit **trois signatures pour deux parties**. Un partenaire encore en 1.1 doit recevoir un préavis écrit de 30 jours
  avant toute baisse de barème (art. 6.7). ⚠️ **Aucun taux ne baisse de la 1.2 à la 1.4** : le
  préavis n'a pas lieu de jouer. ⚠️ **La signature de Romaric est FACULTATIVE** dans
  `_build_pdf.py` : son cadre reste vide tant que le fichier n'est pas là, et l'absence de
  l'une n'empêche jamais de produire l'exemplaire de l'autre
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
- ⛔ **QUATRE DOCUMENTS À L'ANCIENNE GRILLE SONT EN QUARANTAINE** dans
  `_documents/nebula-agency/_obsolete/` (2026-09-10) : brochure partenaire, guide de lancement,
  deck de 14 diapositives et son export PDF. Ils annoncent **STARTER 25 % · SILVER 30 % ·
  GOLD 35 %**, une **commission de réseau de 10 % (N1) et 5 % (N2)**, un abonnement à
  **15 000 F** et les **sept rangs cosmiques**. Une diapositive entière (« Le pouvoir de l'effet
  réseau ») promet « 90 000 F de plus sans effort supplémentaire ». ⛔ **Ne jamais les envoyer**,
  ils promettent un revenu qui n'existe pas et donnent au programme l'allure d'une pyramide.
  ⚠️ **Ils ne sont pas réparables** : leurs diapositives sont des images, sans source dans le
  dépôt. Les remplaçants à jour sont `01b-ANNONCE-PUBLIQUE`, `02-MANUEL-DU-PARTENAIRE` et le
  simulateur. Détail : `_obsolete/README.md`
- ⚠️ **Le partenaire ne vend QUE les offres du tableau 4.1** : Catalogue, QR Code Google Review,
  Vitrine, Outil sur mesure. **Fiche Google Maps et Avatar IA n'en sont pas** et traînaient
  encore dans le kit partenaire (retirées le 2026-09-10) et dans `SERVICES` du portail
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

### `CLAUDE.md` reste sous la limite de Claude Code (2026-09-16)
`CLAUDE.md` est chargé **en entier** au début de chaque session. Au-delà de **150 000
caractères**, Claude Code affiche « CLAUDE.md is over the 150.0k-char limit » et chaque session
démarre avec environ 40 000 tokens de moins. Le 2026-09-16 il en faisait 151 181, dont **73 819
dans trois lignes clients** (Angy Art, Hillary, Au Braisé d'Or) : chaque vague y avait ajouté son récit.
- **Ici, une ligne client ou un produit est un RÉSUMÉ** (2 000 caractères environ, 3 000 au plus) :
  l'adresse en ligne, l'état, la commande pour publier, les pièges qui cassent quelque chose, ce
  qui attend, et un renvoi au `CONTEXT.md`. **Le récit d'une vague va dans le `CONTEXT.md` et dans
  `_memoire/conversations/`**, jamais dans le tableau.
- ⚠️ **Mettre à jour une ligne, c'est la réécrire, pas l'allonger.**
- **Mesurer** : `python scripts/poids_claude_md.py` (il nomme les blocs les plus lourds, sortie 1
  au-dessus de 140 000).
- ⚡ **Au-delà de 140 000, ou dès que l'avertissement s'affiche, on allège SANS DEMANDER**
  (Mongazi, 2026-09-16) : recopier le bloc **intégralement** dans le `CONTEXT.md` concerné,
  **vérifier que chaque morceau d'origine s'y retrouve**, puis seulement le remplacer par un
  résumé. ⚠️ **Relire le résumé contre le dépôt** : la ligne d'Angy Art était en retard sur ses
  propres commits (musique donnée « à déployer », alors qu'elle était en ligne depuis six jours).

## Commandes rapides
- "nouveau client [nom]" → créer dossier + CONTEXT.md
- "checklist [client]" → vérifier avant livraison
- "bilan session" → mettre à jour _memoire/decisions.md
