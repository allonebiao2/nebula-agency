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
