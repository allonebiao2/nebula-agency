# CONTEXT — Grain d'Esthétique

## Identité
- **Nom** : Grain d'Esthétique — Institut de Beauté
- **Fondatrice** : Jocelyne Aguiar (mère de Mongazi)
- **Secteur** : Esthétique / soins (femmes & hommes — Espace Hommes dédié)
- **Lieu** : Cotonou, Haie-Vive (Lot N 18) — Bénin
- **Produits pros** : Sothys Paris · Sultane de Saba
- **WhatsApp / Tél** : `2290197085576` (01 97 08 55 76) — aussi 01 99 23 71 23 / 01 90 92 68 31
- **Horaires** : Mar–Sam 09h–19h (Lun & Dim fermé) · Sur rendez-vous
- **Réseaux** : avis Google 5★

## Vitrine (en ligne)
- **URL** : https://grain-esthetique-cotonou.netlify.app (Netlify)
- **Source dans le repo** : `grain-esthetique-LIVE.html` (récupérée du live le 2026-06-12 ; ~787 Ko, **images en base64**).
- Mono-fichier HTML/CSS/JS, mobile-first (colonne ~500px), fonts **Cormorant Garamond + Jost**, palette **rose #C4648A / or #D4AF72**, lecteur de musique d'ambiance.
- **Réservation = WhatsApp** : chaque soin a un lien `wa.me/2290197085576?text=…réserver…`. ⚠️ **Ne jamais changer ce numéro/redirection.**

## Promotion Fête des Pères (16–30 juin 2026) — TERMINÉE (retirée du site le 2026-07-02)
> Promo expirée → pastille hero + pop-up auto + flyer base64 **retirés** (validé par Mongazi).
> Le pop-up/mécanique de conversion pourra être réactivé pour une future offre (voir `_edit_promo.py`).
Flyer source : `_partage/flyer fete des pere chez grain desthetique.JPG`. Offres (archive) :
- Soin du visage : ~~30 000~~ → **25 000 F**
- Hydrafacial : ~~60 000~~ → **45 000 F**
- Soin visage + Pédicure & Manucure : ~~45 000~~ → **40 000 F**
- Massage relaxant : ~~15 000~~ → **12 000 F**

## Améliorations livrées (2026-06-12)
Couche **additive** (images, couleurs et liens WhatsApp **inchangés**) :
- **Promo à l'entrée** : badge doré animé dans le hero + **affiche en modale** (ouverture auto 1×/visite) + **boutons RDV** par offre → WhatsApp de base avec message prédéfini.
- **Animations** : révélation au défilement (réutilise `.rv`), zoom doux du hero + fondu du titre, micro-interactions (survol soins, cartes qui se soulèvent, icônes vivantes), focus accessibles, respect « mouvement réduit ».
- **Onglets premium** : nav en verre dépoli + soulignement animé dégradé rose→or, centrés sur PC.
- ❌ Écarté (jugé « moche » par Mongazi) : encadrer la colonne PC avec fond dégradé → revenu au blanc d'origine.

## Animations signatures par section (2026-07-02, 2e passe)
- **Une animation différente par section, adaptée à son thème** (au scroll, via `.rv`), + **micro-animation d'icône** :
  - À Propos → **Éclosion** (bloom fondu+flou) · icône fleur qui s'ouvre
  - Visage → **Radiance** (soins qui s'allument, brightness) · étoile qui scintille
  - Corps → **Respiration** (montée lente/douce) · feuille qui se balance
  - Épilation → **Glisse** (translation latérale, façon cire) · goutte qui tombe
  - Mains & Pieds → **Vernis** (révélation gauche→droite, clip-path) · icône qui scintille
  - Soins Avancés → **Élévation** premium (cartes + halo doré) · gemme qui brille
  - Espace Hommes → **Assurance** (montée nette) · **nœud papillon doré** (remplace l'emoji 🎩 résiduel)
- Correctifs : `.hommes-body` reçoit `id="hommessoins"` + ajouté au tableau `ids` du révélateur (ses soins s'animent enfin).
- `prefers-reduced-motion` : tout apparaît sans animation. Script : `_edit_anim.py`.
- QC Playwright : **7/7 animations de contenu distinctes** + **6 icônes distinctes**, nœud papillon OK, Hommes révélé, 0 emoji résiduel, JS OK (le révélateur exécute le nouveau hook).

## Améliorations livrées (2026-07-02) — passe « au max »
Couche **additive** (images, couleurs, **numéro/liens WhatsApp inchangés** — 91 liens Réserver vérifiés) :
- **Promo Fête des Pères expirée retirée** (pastille + pop-up + flyer base64 → −391 Ko ; fichier 787→417 Ko).
- **Tous les emojis → icônes SVG line-art** rose/or (6 sections, horaires, contact ×3, footer ×3, note musique).
  Fini les emojis d'UI (anti-pattern) ; `★` de « 5★ » passé en doré.
- **SEO/social** : meta description, Open Graph + Twitter Card, theme-color, canonical, geo, **JSON-LD BeautySalon**
  (horaires, tel, adresse), favicon SVG de marque, **image de partage `assets/images/og-grain.jpg`** (1200×630, générée du hero).
- **Accessibilité** : nav `<div onclick>` → **7 `<button>`** (clavier), bouton musique = `<button>` + `aria-pressed`,
  alt manquant corrigé, reset CSS boutons (rendu identique).
- **Conversion** : **CTA « Prendre rendez-vous »** (WhatsApp) dans le hero + **bouton WhatsApp flottant** rose/or,
  **badges maisons partenaires** (Sothys Paris · Sultane de Saba), `rel="noopener"` sur les 91 liens.
- Scripts reproductibles : `_edit_promo.py`, `_edit_icons.py`, `_edit_a11y.py`, `_edit_polish.py`, `_build_og.py`.
- QC navigateur (Playwright) desktop+mobile : **0 erreur, 0 404, 11/11 images OK, 93 liens WhatsApp (0 mauvais numéro)**, focus clavier OK.

## Déploiement — MIGRÉ SUR CLOUDFLARE PAGES + DOMAINE (2026-07-02)
- ✅ **LIVE CONFIRMÉ : https://graindesthetique.com** (+ `www`) — 200, **SSL actif**, redirect http→https (301). Site amélioré servi.
- ✅ **Affiche CARRÉE 1:1** (pour coller à l'institut) : `assets/docs/Affiche_Grain_Carre.png` (3240×3240) + `.pdf` —
  QR vers `graindesthetique.com` **vérifié scannable** (pyzbar), design rose/or Cormorant. Scripts : `_build_affiche.py` + `_render_affiche.py`.
  (Statut « custom domain » de l'API Pages restait « pending » alors que le site répondait déjà 200 — l'API retarde, le site marche.)
- ✅ **Domaine acheté par Mongazi : `graindesthetique.com`** (registrar **Hostinger**).
- ✅ **Site amélioré déployé sur Cloudflare Pages** — projet **`grain-esthetique`** → https://grain-esthetique.pages.dev (LIVE, vérifié 200).
  Déploiement = `wrangler pages deploy _dist` (`_dist` = `index.html` [= grain-esthetique-LIVE.html] + `assets/images/og-grain.jpg`).
- ✅ **Meta pointées vers le domaine** : canonical/og/twitter/JSON-LD = `https://graindesthetique.com` (6 remplacements).
- **Domaine branché** : zone `graindesthetique.com` ajoutée à Cloudflare (NS `paul`+`rosemary.ns.cloudflare.com`, changés chez Hostinger).
  Custom domains `graindesthetique.com` + `www` attachés au projet Pages (via API). DNS : **A `2.57.91.91` supprimé** →
  **CNAME `@` → `grain-esthetique.pages.dev` (proxied)**, `www → graindesthetique.com`. ⏳ activation/SSL en cours au 2026-07-02.
- ⚠️ Token `cloudflare.env` = **Pages-only** (ne gère pas le DNS) → les changements DNS/zone = **action Mongazi dans le dashboard**.
- **Ancienne version Netlify** (`grain-esthetique-cotonou.netlify.app`) = OBSOLÈTE → à débrancher une fois le domaine live.

## ✅ NOUVELLE AFFICHE CARRÉE 1:1 POUR L'INSTITUT (2026-09-02)

**`.svg` vectoriel** (voir plus bas) · **`.pdf`** (imprimeur) · **`.png` 4320×4320**
(net jusqu'à **36 × 36 cm à 300 dpi**) · **`.jpg` 1600 px, 204 Ko** (WhatsApp).
Outils : `_outils/_build_affiche_institut.py` puis `_outils/_render_affiche_institut.py`.
⚠️ L'ancienne `Affiche_Grain_Carre.*` est **conservée**, rien n'a été écrasé.

### La phrase, avant le dessin
Un institut comme celui-ci, c'est **un grain de peau qu'on révèle** : le nom le
dit déjà. L'objet concret est donc **le grain**, dense sur les bords et effacé
au centre là où le regard se pose. Et **sa marque est un œil** : il tient le
haut de l'affiche, et on le retrouve **au centre du QR**.

### ⚡ SON LOGO EST ENFIN VECTORIEL (tâche ouverte depuis le 2026-08-15)
`_outils/_vectoriser_logo.py` → `assets/images/logo-grain-esthetique.svg` (95 Ko,
55 contours) + `logo-grain-marque.svg` (l'œil seul). ⚠️ **Ce n'est pas un
redessin** : on trace les contours de SON fichier, c'est son logo au pixel près,
seulement rendu extensible. Le seul PNG existant fait **224 × 162** : agrandi
sur une affiche imprimée il est flou, et un logo flou sur un mur d'institut dit
le contraire de ce que la maison vend (comparaison regardée côte à côte).
⚠️ **On agrandit ×8 au Lanczos AVANT de seuiller** : tracer à 224 px donne des
marches d'escalier que rien ne rattrape ensuite · `RETR_CCOMP` pour garder les
**trous** (sans lui la pupille et le compteur des lettres se remplissent) ·
courbes de Bézier par les milieux, sinon le polygone se voit à l'agrandissement.

### Ce que l'ancienne affiche n'avait pas
**son logo** (le nom était simplement retapé) · **ce que la maison fait** (les 6
familles de soins) · **les maisons partenaires**, qui disent « haut de gamme »
sans l'écrire · **les horaires** (une affiche murale sans horaires oblige à
demander) · et son QR mangeait **un tiers** de l'affiche.

### ⛔ Rien n'est inventé
Numéro, quartier, ville et horaires sont **lus dans le JSON-LD du site**, jamais
recopiés : recopier fabrique une deuxième vérité, et le jour où les horaires
changent c'est la cliente qui trouve porte close. L'accroche **« La beauté est
un art de vivre »** est **sa phrase**, publiée sur sa page À Propos. Aucun prix,
aucune note, aucun avis, aucun slogan fabriqué.
⚠️ **`Lot N 18` n'est PAS sur l'affiche** : il figure dans ce CONTEXT.md mais pas
sur le site. L'y mettre donnerait deux adresses différentes pour une même maison.
⚠️ Les icônes reprennent **le vocabulaire du site** section par section (éclat =
Radiance · feuille = Respiration · goutte = Glisse · vernis · gemme · **nœud
papillon** pour l'Espace Hommes). Une affiche qui parle une autre langue que le
site n'est pas la même maison.

### ⚠️ Le rendu REFUSE d'écrire — 11 contrôles
Fontes réellement chargées (sinon Cormorant retombe en serif générique et **ça ne
se voit pas sur une petite capture**) · aucun débordement du carré ni du cadre
doré · **le QR relu dans l'image FINALE rendue**, œil de la marque compris ·
14 textes obligatoires · apostrophes typographiques · **contrastes mesurés sur
les pixels rendus** (le fond est un dégradé : lire `background-color` ne dit rien).

⚠️ **Les fontes sont embarquées en base64.** Une affiche qui part chez
l'imprimeur ne peut pas dépendre du réseau. Le HTML intermédiaire pèse 1,6 Mo,
il est **gitignoré** et se régénère en une commande.

### ⛔ Trois défauts que le QC vert ne voyait pas, trouvés sur les captures
1. la grille des 6 soins était **étalée sur 916 px** : les icônes flottaient loin
   de leur mot, le bloc n'était pas composé → largeur bornée à 600 px ;
2. le **nœud papillon se lisait « ∞ »** → deux ailes trapézoïdales + un vrai nœud ;
3. **l'adresse du site touchait la ligne de contact** → on libère 26 px, et
   `margin-top:auto` du pied en fait l'air qui manquait.
⚠️ Et deux rouges du 1er jet étaient réels : **ça débordait de 139 px**, et la
ville était à **4,1:1** (mauve trop clair sur le rose du haut → `#6F5462`, 6,3:1).

### ⚡ ET EN **VRAI SVG** (2026-09-02) : `assets/docs/Affiche_Grain_Institut.svg`
267 Ko. ⛔ **Pas un PNG emballé** : logo, six icônes, cadre, filets, **textes en
tracés** et **QR module par module**, tout est vectoriel. Aucune référence
externe, aucune fonte requise. Outils : `_outils/_build_affiche_svg.py` +
`_outils/_polices_svg.py`.

⚠️ **Pourquoi les textes sont vectorisés et pas en `<text>`** : un `<text>` avec
sa fonte en base64 s'affiche dans un navigateur, mais Illustrator et une bonne
part des serveurs d'impression l'ignorent, retombent sur une fonte par défaut,
et **ça se découvre une fois les exemplaires imprimés**. Un imprimeur demande
d'ailleurs toujours « les textes vectorisés ».

⚠️ **La mise en page n'est pas recopiée**, elle est **relevée dans le navigateur**
sur le HTML déjà contrôlé. La retaper aurait créé une 2ᵉ mise en page qui dérive
dès la première retouche : le PNG et le SVG ne seraient plus la même affiche.

⚡ **Le QR est passé en vectoriel DANS LE HTML aussi.** Il était en PNG affiché à
194 px alors que l'image en faisait 770 : un module tombait sur 5,54 px, le
navigateur arrondissait, et **les modules sortaient inégaux (5 ou 6 px au
hasard)**. Un seul QR pour le PNG, le PDF et le SVG.

### ⛔ CINQ PIÈGES, TOUS TROUVÉS À LA MESURE
1. ⛔ **HarfBuzz ne lit pas le woff2.** `tt.save()` réécrit du woff2 (fontTools
   conserve le format), la face se construisait quand même et **chaque
   caractère renvoyait le glyphe 0** : l'affiche se remplissait de cases
   « NO GLYPH ». → `tt.flavor = None` avant de sauver.
   ⚠️ **Et ma vérification de couverture ne le voyait pas** : elle lisait la
   table `cmap` avec fontTools, qui répondait « tout est là ». **Une couverture
   vérifiée sur une bibliothèque ne dit rien de ce que produit l'autre** : on
   contrôle désormais le **résultat de la composition** (`.notdef` = rouge).
2. ⛔ **Google sert des fontes VARIABLES.** Dessiner les glyphes donne
   l'instance par défaut, soit le **Light (300)** pour Cormorant, pas le
   Regular affiché : lettres plus maigres ET plus étroites, donc un décalage
   **qui s'accumule le long de la ligne**. → on fige la graisse avant tout.
3. ⛔ **`radial-gradient` CSS fait des ELLIPSES** (`105% 68%`) et **arrête sa
   couleur à 58 %**, pas à 100 %. Mon `<radialGradient>` était un cercle avec
   l'arrêt au bord. → `gradientTransform` + les vrais décalages d'arrêt.
4. ⛔ **L'ordre des calques** : le fond blanc de l'œil était dessiné **avant**
   le QR, donc recouvert par lui. Trouvé **sur la carte d'écart**, pas par un
   contrôle : c'était le seul point encore lumineux.
5. ⚠️ **CSS compte l'interlettrage du DERNIER caractère** dans la largeur : un
   texte centré très espacé est en fait décalé d'un demi-espacement. On ancre
   donc sur le **bord gauche mesuré** plutôt que de recentrer « correctement » :
   **trois fichiers, une seule affiche.**

### ⚠️ Le contrôle de superposition, et comment il a fallu le corriger
Le SVG est re-rendu et **superposé au PNG**. Écart mesuré : **7,28 → 1,05**.
Trois corrections de l'instrument, pas du produit :
- il s'accusait lui-même d'être « non autonome » à cause de son propre
  `xmlns="http://…"` puis du texte de son `<desc>` ;
- il jugeait sur l'écart **brut** : un glyphe en tracé n'est pas anticrénelé
  comme le même glyphe rendu par le moteur de texte. → verdict après un léger flou ;
- ⚠️ **le grain est une texture procédurale** à 13 % d'alpha : deux documents ne
  la rasterisent jamais pareil. → **on l'éteint des deux côtés** (et on vérifie
  qu'il existe). Le plancher restant (~1,0) vient des ~600 arêtes du QR et des
  55 contours du logo : au-delà de **1,5**, c'est qu'un élément a vraiment bougé.

### ⏳ Variante à faire quand on aura le lien
Une 2ᵉ affiche avec **QR vers les avis Google** (`g.page/r/…`) : posée à
l'accueil, elle vaut plus qu'un QR vers le site pour une cliente qui vient de
sortir de soin. C'est le produit « QR Code Google Review » de NEBULA (30 000 F).
**Le lien n'existe que depuis sa fiche Google**, à récupérer auprès d'elle.

## Prospectus « Fête de l'Igname » (2026-08-15)
Prospectus **A5 recto-verso** (148 × 210 mm), dans l'univers de l'institut : rose `#C4648A`,
or `#D4AF72`, encre `#1A0E14`, Cormorant Garamond + Jost, équerres dorées, filet à la gemme.

- **Recto** : logo, « À l'occasion de la **Fête de l'Igname** » en or dégradé entre deux
  feuilles d'igname au trait, l'accroche « **La fête se prépare la veille.** », les 4 offres
  avec prix barrés, la période, et le rappel WhatsApp.
- **Verso** : les 6 familles de soins, les maisons partenaires, l'adresse et les horaires,
  le QR vers `graindesthetique.com`, le pied signé NEBULA.
- **Fichiers** : `assets/docs/Prospectus_Igname_A5.pdf` (à donner à l'imprimeur) +
  `..._recto.png` / `..._verso.png` (384 dpi, pour WhatsApp et les réseaux).
- **Outils** : `_outils/_build_prospectus_igname.py` (fontes, logo et QR **embarqués en
  base64** : le fichier ne dépend d'aucun réseau) puis `_outils/_render_prospectus_igname.py`.

**Le rendu refuse d'écrire** si une page déborde de l'A5, s'il manque un texte obligatoire,
s'il reste une apostrophe droite, ou si le QR relu **dans l'image finale** ne pointe pas sur
le bon domaine. Au premier essai le bas du recto était coupé de 44 mm : c'est exactement ce
qui part chez l'imprimeur et se découvre une fois les exemplaires payés.

⚠️ **À CONFIRMER PAR JOCELYNE AVANT IMPRESSION** (bloc « ZONE À CONFIRMER » en haut du script) :
- les **dates** (`Du 15 au 31 août 2026` est une proposition) ;
- les **quatre montants**, repris tels quels de la promo Fête des Pères qu'elle avait validée.

⚠️ Le logo n'existait qu'en base64 dans la vitrine. Extrait dans
`assets/images/logo-grain-esthetique.png` (320 × 239) et `-detoure.png` (224 × 162). C'est la
plus grande version qui existe : agrandie ×4 au Lanczos pour l'impression, elle tient à 28 mm.
Une **version vectorielle** reste à faire si on veut l'imprimer en grand.

## À faire / décisions
- [ ] Confirmer `https://graindesthetique.com` en ligne + SSL actif (custom domain « active »), puis débrancher/supprimer l'ancien Netlify.
- [ ] Optionnel : vraies photos supplémentaires, vrais avis Google, mini-vidéo institut.
- [ ] **Prospectus Igname** : faire confirmer dates + montants par Jocelyne, puis imprimer.
- [x] ✅ **Logo en vectoriel FAIT le 2026-09-02** : `assets/images/logo-grain-esthetique.svg` (+ `logo-grain-marque.svg`), tracé de son PNG par `_outils/_vectoriser_logo.py`.

## Liens
- Vitrine source : `grain-esthetique-LIVE.html`
- Assets : `assets/`
