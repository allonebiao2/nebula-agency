# AU BRAISÉ D'OR — client 09

> 📌 **Le résumé qui vivait dans `CLAUDE.md` jusqu'au 2026-09-16 est recopié en fin de fichier**, section « Résumé transféré de `CLAUDE.md` ».

> ## 🔥 EN LIGNE : **https://au-braise-dor.pages.dev**

> ### 🌐 EN LIGNE SUR SON DOMAINE : **https://aubraisedor.com** (2026-09-18)
> ✅ **Fait et vérifié le 2026-09-18** : domaine acheté chez Hostinger par Mongazi, serveurs de noms
> basculés sur Cloudflare (`paul` / `rosemary`), zone créée, deux `CNAME` (apex et `www`) vers
> `au-braise-dor.pages.dev` en mode *proxied*, certificat émis. **Les deux hôtes rendent 200 avec le
> vrai site** (164 879 octets), `/page-inexistante` rend bien **404**.
> ⛔ **LE PIÈGE RENCONTRÉ** : après la création de la zone, le domaine répondait **200 en servant la
> page de parking Hostinger** — Cloudflare avait importé l'enregistrement `A` vers `2.57.91.91` et le
> proxyfiait. **Un 200 ne prouve rien : il faut lire le CORPS.** La bascule n'a marché qu'après avoir
> supprimé cet `A`.
> **L'adresse a été changée aux 6 endroits où elle vivait**, puis reconstruite et redéployée :
> `experience/app/layout.tsx` (canonical + og:url + og:image), `components/DonneesStructurees.tsx`
> (JSON-LD), `public/robots.txt` (ligne `Sitemap:`), `public/sitemap.xml`, `index.html` (l'ancienne
> page unique), et **`_outils/_build_affiche.py` → l'affiche A4 et son QR**, refaits et **décodés
> pour vérification** (`https://aubraisedor.com` + le lien WhatsApp).
> ✅ Le `robots.txt` servi est bien **le nôtre** (les robots d'IA restent accueillis) : Cloudflare n'a
> pas préposé son `robots.txt` géré sur cette zone. À revérifier si Mongazi active un réglage d'IA.
> ⏳ Reste : la fiche Google Business avec cette adresse (voir `GOOGLE-BUSINESS.md`), et l'ancien
> `au-braise-dor.pages.dev` qui continue de répondre (normal, c'est l'origine).

> ### 🪧 L'AFFICHE CARRÉE DES TABLES (2026-09-18)
> Demandée par Mongazi dès le domaine posé : « l'affiche carrée qu'ils pourront coller sur les tables
> et partout dans le restaurant, avec le QR code en grand ». `python _outils/_build_affiche_table.py`
> → `assets/docs/` :
> - **`Affiche_Table_Au_Braise_dOr_20cm.pdf` / `.png`** : le carré maître, 20 × 20 cm à 300 DPI, qui
>   se réduit à 15 ou 10 cm sans rien refaire. **Un seul QR, vers `https://aubraisedor.com`** (43 % de
>   la largeur), l'adresse écrite dessous pour qui ne scanne pas, puis « Scannez · Choisissez ·
>   Envoyez sur WhatsApp ». Le site est **déjà réglé sur « Sur place »** : le client à table n'a rien
>   à changer.
> - **`Planche_A4_6_carres_Au_Braise_dOr.pdf`** : six carrés de **9 cm** sur une feuille A4, traits de
>   coupe, pour l'imprimeur qui n'imprime que de l'A4.
> ⛔ **Aucun numéro imprimé** : le site en porte un (`22956057157`), l'`index.html` un autre, l'enseigne
> un troisième, et une affiche collée sur trente tables ne se corrige pas. Le QR mène au site, le site
> mène à WhatsApp : le jour où le numéro est tranché, les tables ont raison sans être réimprimées.
> ⚠️ **Le QR est décodé à chaque fabrication par DEUX lecteurs** (OpenCV et zbar), à 20 cm, à 9 cm et
> réduit à 600 px ; le script sort en erreur si l'un échoue. Zone de silence de 4 modules, adresse
> écrite à 3 modules du QR, jamais collée à lui.
> ⛔ **Deux défauts vus en REGARDANT, que le décodage ne voyait pas** : la mention NEBULA se posait sur
> « Sur place · À emporter » (un `assert` la garde désormais), et la planche en **9,5 cm** laissait
> **2 mm** de marge en haut et en bas : une imprimante de bureau n'imprime pas à moins de 4-5 mm du
> bord, les carrés extrêmes sortaient rognés (→ 9 cm, 9,5 mm de marge, `assert` ≥ 5 mm).
> ℹ️ Les fichiers partent en ligne au prochain déploiement (`cp -r ../assets/docs out/`), sous
> `/docs/`, comme l'affiche A4.

## ⚠️ LES SEPT PIÈGES DE CE PROJET, tous trouvés à la mesure

1. **Les 48 photos en `background-image` se téléchargeaient d'un coup** :
   4,3 Mo avant même d'arriver au menu. Un navigateur ne sait pas différer un
   fond CSS. → `<img loading="lazy">`.
2. **`gsap.from()` laisse l'élément invisible si on l'interrompt.** Le bouton
   « Commander sur WhatsApp » était à `visibility: hidden` : la carte
   s'affichait complète, sauf le seul bouton qui rapporte de l'argent.
   → `fromTo()` + `clearProps`, partout, sans exception.
3. **Une scène en `fixed` ne se décolle jamais** et reste en travers du
   contenu suivant. → `sticky` dans un parent de N × 100vh.
4. **On n'empile pas des boîtes à la main sur téléphone** : un pourcentage de
   hauteur ne sait rien de la hauteur en pixels du texte. → conteneur en
   `display: contents` sur grand écran, **colonne flex** sur téléphone.
   ⚠️ Et en `width: auto` une boîte dont les enfants sont tous absolus est
   mesurée à **zéro de large** : l'assiette disparaissait.
5. **Un conteneur plein écran avale les clics** des boutons posés avant lui.
   Le bouton du héros s'illuminait au survol et ne faisait rien.
   → `pointer-events-none`.
6. **LENIS TIENT LE DÉFILEMENT DE LA PAGE.** Tout `scrollIntoView` lancé à côté
   se fait interrompre : le saut vers une catégorie s'arrêtait à **7 382 px**
   de sa cible, sans erreur en console. → `components/aller.ts`.
7. **Une vidéo de référence se MESURE image par image** avant d'écrire
   l'animation, elle ne se résume pas de mémoire. Les assiettes **roulent sur
   un arc** (haut droite → bas gauche, presque un quart de tour), elles ne
   montent pas tout droit.

## Ce qui est en ligne

**L'expérience** : 4 plats signature, défilement **automatique** (5,5 s) avec
cinq garde-fous, titre en deux lignes qui se dédouble, carte de verre, prix qui
compte de 0, carrousel Swiper à item surélevé, tiroir des 8 univers ouvert
depuis le héros.
**La carte** : 48 plats **toujours tous affichés** (le filtre cachait 38
plats), chips en ancres avec scroll-spy, fiche taille + accompagnement +
quantité, panier, mode, message WhatsApp rédigé.
**Le pied** : les deux numéros, l'email, le WiFi, les horaires, le traiteur, la
place des fêtes, **RC RB/COT/24 A 102350 · IFU 0202501441177**.

⛔ **NI NOTE, NI CHEF, NI « LIKES » INVENTÉS.** La vidéo de référence en
affichait ; ce restaurant existe. Le carré coloré porte **le prix**, qui est
vrai. Les champs `chef` et `avis` attendent dans `data/dishes.ts` et
s'afficheront tout seuls le jour où le restaurant les donnera.

## Les outils

| Fichier | Ce qu'il fait |
|---|---|
| `_outils/_extraire_carte.js` | relit `index.html` et régénère `experience/data/carte.ts` (8 catégories, 48 plats). **La carte ne se retape jamais à la main** |
| `_outils/_carte_claire.py` | passe la carte et le pied dans la langue du héros |
| `_outils/_catalogue_vente.py` | ancres + scroll-spy + tiroir des catégories |

⚠️ Les trois **s'arrêtent net si un motif a disparu**, pour ne jamais repeindre
à moitié.

## ✅ LA CARTE DES SAUCES, ET TROIS VRAIES PHOTOS — 2026-08-19 (nuit, 2)

La maison envoie **sa feuille de menu des sauces** (`_partage/2026-08-19-menu-sauces.jpeg`)
et **trois photos de plats**. Mongazi : « ce sont de vraies images de plats
béninois que j'ai améliorées avec l'IA, donc on peut les utiliser ».
**La règle du 2026-08-01 ne s'y applique pas** : ce ne sont pas des images
générées. Les originaux restent dans `_partage/`, la vérification reste possible.

### ⚠️ LE PRIX EST UNE FOURCHETTE, PAS DEUX TAILLES
Mongazi : « le prix varie en fonction des éléments entre parenthèses ; en
fonction de ce que le client veut dans les parenthèses, le prix augmente. »
**J'avais d'abord lu « 1 500-3 000 » comme Normal/Grand.** C'était faux, et le
panier aurait annoncé un total que la maison n'aurait pas tenu.

Nouveau modèle dans les données : **`pMax`** (borne haute) et **`garn`** (ce
qu'on peut mettre dedans). Plus **`tailles`**, pour les deux formats du yassa au
poulet, qui ne s'appellent pas « Normal / Grand » mais « Quart / Demi-poulet ».

Dans la page : la carte affiche **« 1 500 à 3 500 F »**, la fiche propose
**« Ce que vous voulez dedans »** (cases à cocher), et **le total du panier est
lui-même une fourchette**. ⛔ **On n'annonce aucun prix par ingrédient** : la
maison n'a donné qu'une fourchette, un chiffre en face de chaque case serait
inventé. Le message WhatsApp porte les choix, la fourchette, et la phrase
« merci de me le confirmer ».

### ⚠️ LA RÈGLE DE PRIX, PRÉCISÉE PAR MONGAZI (nuit, 3)
> « Un client qui veut commander une sauce doit, après avoir choisi la sauce,
> choisir un accompagnement. Les plats varient de 1 500 à 3 000 F en fonction
> des éléments qu'ils veulent à l'intérieur — entre parenthèses. **Quand on met
> tout dedans, c'est le prix le plus cher.** »

Cette dernière phrase change tout : **deux cas sur trois deviennent EXACTS.**

| Ce que le client choisit | Prix affiché | Au panier |
|---|---|---|
| **rien dedans** | **1 500 F** exact | 1 500 F |
| une partie | **1 500 à 3 500 F** | fourchette, la maison confirme |
| **tout dedans** | **3 500 F** exact | 3 500 F |

⛔ **On n'interpole pas entre les deux.** La maison n'a jamais donné le prix
d'un ingrédient pris séparément : deux bornes connues ne font pas un barème.
Le cas « une partie » reste donc une fourchette assumée, et le message WhatsApp
demande la confirmation.

✅ **L'accompagnement est OBLIGATOIRE.** Le bouton reste bloqué sur
« Choisissez un accompagnement » tant qu'il n'y en a pas — une commande sans
accompagnement arrive incomplète en cuisine, et c'est le restaurant qui doit
rappeler le client. Vaut pour les sauces **et les grillades**, les deux
catégories qui proposent des accompagnements. Deux contrôles le vérifient :
bloqué sans, débloqué avec.

### La catégorie passe de 4 à 14 sauces
Les 10 de la feuille (gombo, krinkrin, feuille, arachide, graine, tomate, tête
de mouton, pieds de bœuf, yassa, yassa au poulet) rejoignent les 4 de l'ancien
menu. Les **accompagnements sont remplacés** par la liste de la feuille (15,
de telibo à toubani).

### Le héros : QUE des sauces
Mongazi, en regardant le héros en ligne : « je veux qu'ici ce soient les sauces
qui soient mises en avant, **que les sauces** ». Le poulet bicyclette, le
tilapia et le chawarma JOQ **sortent du héros**. Ils restent à la carte et se
commandent comme avant : ce n'est pas un retrait de plat, c'est un choix de
vitrine — un restaurant béninois montre ses sauces.

⚠️ **Trois, et pas plus** : ce sont les seules sauces dont la maison a envoyé
la photo, et le héros vit de l'image (une ardoise en plein écran ne vend rien).
Moyo Chigan et Sauce poisson frais ont bien un détourage, mais fait à partir
d'une image **générée** de juillet : les mettre là, c'est ouvrir le site sur de
l'IA. Elles y entreront le jour où la maison les photographie.

### Le héros : trois vraies photos en tête
Sauce gombo, Sauce krinkrin, Sauce feuille, puis poulet, tilapia, chawarma.
⚠️ **L'appariement photo ↔ sauce est vérifié, pas deviné** : la feuille porte
trois vignettes imprimées et **la forme de l'assiette concorde** (gombo
octogonale, krinkrin octogonale sur ardoise, feuille hexagonale).

### Les détourages de la maison : `python _outils/_damier.py`
Mongazi renvoie les trois plats **déjà détourés**, mais les fichiers arrivent en
**RGB sans canal alpha** : le damier gris de son éditeur est **peint dans les
pixels**. Il faut donc redétourer, en traitant le damier comme un fond.

⛔ **Quatre tours perdus à vouloir le faire « proprement »** : apprendre les deux
gris sur les coins, remplir depuis les bords, ponter les pixels de transition,
rembourrer pour que l'érosion ne mange pas l'anneau du bord, reconstruire la
grille pour ne retirer que ce qui coïncide avec elle. Échec de fond : **sur le
gombo les deux gris du damier sont 77 et 124, et le bord noir de l'assiette a
des reflets dans cette plage.** Aucun seuil de luminance ne les sépare.
✅ **rembg sort les trois d'un coup, sans une bavure** : un modèle de saillance
ne se demande pas de quelle couleur est le fond, il voit une assiette.
⚠️ Et ici **`isnet` gagne**, alors que birefnet gagnait sur les mêmes plats
photographiés sur fond noir : **le fond change, le gagnant change.**

⚠️ **Piège d'archivage** : j'avais copié dans `_partage/` *mon masque raté* au
lieu des fichiers de Mongazi, et rembg a donc travaillé sur une image déjà
abîmée — assiette perdue. **Ce qu'on archive doit être la source reçue, jamais
un intermédiaire.**

### Le détourage : `python _outils/_photos_sauces.py`
Deux formes par photo : **carré opaque** pour la carte, **détouré RGBA** pour le
héros. Le carré n'est pas un recadrage aveugle — il se centre sur l'assiette
grâce au masque, un recadrage centré coupait le bord sur deux des trois photos.
⚠️ **MODÈLE : `birefnet-general` ICI, `isnet` POUR LES BOLS.** Planche
comparative : sur ces photos — **assiettes noires sur fond noir** — isnet garde
une tache de vapeur pleine au-dessus du krinkrin, une encoche dans l'assiette de
la feuille et un bout d'ardoise ; birefnet découpe la masse du plat proprement.
Sur les bols de `_detoure_plats.py`, c'est **exactement l'inverse**.
→ **Refaire la planche à chaque nouveau lot, ne pas présumer.**

## ✅ LE HÉROS PASSE AUX SAUCES — 2026-08-19 (nuit)

> Mongazi : « c'est un restaurant béninois, donc les plats de la catégorie
> sauce doivent être mis en avant plus que les autres ; dans la héros section
> ce sont ces plats-là qui défileront automatiquement. Les autres aussi bien
> sûr, mais ces plats-là en principal. »

**Le héros passe de 4 à 6 plats, les deux sauces en tête** : Moyo Chigan et
Sauce poisson frais, puis Poulet bicyclette, Tilapia braisé, Pizza Paysanne,
Chawarma JOQ.

### Pourquoi CES deux sauces et pas les quatre
Le menu papier range les sauces en **deux sections** : « Monyo » (les locales)
et « Sauces Européennes ». **Béchamel et Sauce Crème sont les européennes** :
les mettre en avant pour dire « c'est un restaurant béninois » dirait le
contraire de l'argument. Elles restent à la carte, pas au héros.
⚠️ Et leur détourage est raté (voir ci-dessous), ce qui tranche la question.

### Le détourage : `python _outils/_detoure_plats.py`
Le héros pose l'assiette sur un fond crème, donc **toutes les images de
`public/plats/` sont en RGBA**, contrairement à celles de `public/carte/`.
Les sauces n'en avaient pas : elles ont été détourées depuis leur image carrée.
- **Modèle `isnet-general-use`**, choisi sur planche comparative : `u2net` perd
  le bol et ne garde que la viande, `birefnet-general` déchiquette le bol.
  isnet garde le bol entier **et la vapeur**, qui fait tout le charme.
- ⛔ **Ce qui ne marche pas** : sur Béchamel et Crème, isnet garde un bout de
  l'ardoise sous le bol. L'ouverture morphologique qui devait l'enlever **mord
  dans le bol** et laisse une encoche — pire que le mal. Ne pas refaire l'essai.
- La **teinte du prix est relevée sur la photo** (méthode Hillary) : Moyo
  `#B25324` (5,05:1 avec le blanc), Poisson frais `#8A3520` — les deux sauces
  partagent leur dominante tomate, il fallait les distinguer sans mentir.

### ⏳ Ce qui manque pour aller au bout
**Gombo, krinkrin et sauce feuille — les plus béninoises de toutes — n'ont
aucune photo sur le disque.** Les images envoyées par Mongazi sont arrivées
dans la conversation, pas comme fichiers. Le jour où elles atterrissent dans
`_partage/`, elles prennent la tête du héros.
⚠️ **Et il faudra d'abord savoir d'où elles viennent** : fond noir, vapeur,
lumière de studio — elles ont l'allure des 48 images générées de juillet. Si
elles sont générées, la règle du 2026-08-01 les refuse, et ce serait la
première fois qu'on en ajoute une **après** la règle.

## ✅ CORRECTIONS DE LA PROPRIÉTAIRE — 2026-08-19 (soir) · **52 → 42 plats**

Note manuscrite « Correction pour Au Braisé d'Or », photographiée et transmise
par Mongazi. **Les prix en place sont validés** (« la propriétaire n'est pas
contre »). Elle demande des retraits et une catégorie de plus.

### 13 plats retirés
| Catégorie | Retiré | Reste |
|---|---|---|
| **Pizza** | napolitaine · oriental · margherita · pili chaud · à la crème · **pêcheur** | 4 sur 10 |
| **Grillades** | **le lapin seul** · viande de caille — ✅ **le mouton frit reste, même prix** (Mongazi, 19/08 au soir) | 5 sur 6 |
| **Chawarma** | rien (elle l'écrit) | 3 |
| **Hamburger** | crispy poulet · nugget pomme au four | 7 sur 9 |
| **Cocktails** | « on supprime tout sauf les jus de fruit » → mojito, piña colada, JOQ Viagra | 3 sur 6 |

Salades, sauces et petit-déjeuner : rien à changer.

### Une catégorie ajoutée : **Desserts** (yaourt, glace)
⚠️ Le « cocktail » qu'elle listait **en a été sorti le soir même** (Mongazi) :
il faisait doublon avec les 3 cocktails de fruits à 2 500 F, dans deux onglets
et à deux prix.
⏳ **Aucun prix donné.** Mongazi les demandera plus tard : on garde
« Prix sur demande », c'est assumé, pas un oubli. Les trois portent **« Prix sur demande »** et
leur fiche envoie la question sur WhatsApp au lieu d'ajouter au panier.
Convention posée dans les données : **`p:0` = prix pas encore donné**. On
n'invente pas un prix, et on ne cache pas une catégorie qu'elle veut vendre.
⚠️ Un article à 0 ne doit jamais entrer au panier : le total mentirait et le
message WhatsApp partirait avec un « 0 F ». Un contrôle vérifie qu'aucun
« 0 F » n'apparaît nulle part.

### ⚠️ Ce que le retrait a cassé, et qu'il fallait réparer
1. **La pizza pêcheur était un des 4 plats signature du héros.** Un héros ne
   peut pas mettre en avant un plat qu'on ne peut plus commander : le visiteur
   arrive, s'enthousiasme, et ne le trouve nulle part. → **paysanne**, seule
   pizza restante à deux tailles, donc au même rôle sur la carte.
   ⚠️ Elle réutilise l'image générée de l'ancienne pizza, qui ne représente
   aucun plat réel : à revoir avec la décision sur les 48 photos.
2. **Deux notes de catégorie devenaient fausses.** Les hamburgers disaient
   « sauf végétarien, crispy, nugget » alors que crispy et nugget sont partis ;
   les cocktails annonçaient « avec ou sans alcool » alors qu'il n'y a plus
   d'alcool. Réécrites. **Retirer un plat ne suffit pas : il faut relire ce que
   la page dit encore de lui.**
3. Les trois cocktails restants répétaient « Sans alcool. » en fin de
   description, ce que la note de catégorie dit désormais une fois pour toutes.

### ⏳ Les trois questions qui restent (détail en bas de `MENU.md`)
1. **Prix du yaourt et de la glace** — ⏳ Mongazi les demandera plus tard, les
   deux desserts restent en « Prix sur demande » en attendant.
2. **Aileron** : le prix corrigé au surligneur sur le papier.
3. **Le n° WhatsApp.**

✅ **Deux tranchées par Mongazi le soir même** : le mouton frit reste au même
prix (seul le lapin part) — ⚠️ **on avait retiré la ligne entière et donc
supprimé un plat que la maison vend toujours** — et le « cocktail » sort des
desserts.

✅ **Deux questions de la passe précédente sont mortes d'elles-mêmes** : les
2ᵉˢ tailles de la napolitaine et de l'oriental, et le prix de la pêcheur — les
trois pizzas sont retirées.

**QC : 64 contrôles verts**, dont un par plat retiré (il ne doit réapparaître
ni par une régénération ni par un retour en arrière mal ciblé).

## ✅ PASSE CATALOGUE DU 2026-08-19 — la carte relue contre le menu papier

**On est remonté aux 5 photos du menu** (`_partage/photo_*_2026-07-17_*.jpg`),
recadrées et agrandies, plutôt qu'au `MENU.md` qui en était le résumé. Trois
choses en sont sorties.

### 1. Le catalogue ne contenait pas tout le menu — **48 → 52 plats**
Le petit-déjeuner du papier compte **10 lignes**, le site n'en montrait que
**6**. Manquaient : **café chaud serré (500 F)**, **Lipton citron (500 F)**,
**œuf sur plat (1 000 F)** et **café au lait écrémé (1 000 F)**. Quatre choses
que la maison vend, tous les matins, et qu'on ne lui proposait pas.
Ajoutées dans `index.html` (la vérité), carte régénérée par
`node _outils/_extraire_carte.js`.

### 2. Le prix était **illisible sur les 52 cartes**
La pastille de prix n'avait **aucune couleur de texte** : elle héritait de
`--encre` (`#1d1a17`) et posait de l'encre noire sur un fond noir à 65 %.
Contraste mesuré sur les pixels rendus : **1,1:1**. Le minimum lisible est
4,5:1. Autrement dit le seul chiffre que le client cherche n'était pas là.
→ texte en `#f6efe6`, pastille à 70 %, **mesuré entre 13,9:1 et 18:1**, et un
contrôle le garde désormais.

### 3. Un plat sans photo a maintenant une place : **l'ardoise**
⛔ Ni cadre vide, ni « photo à venir » : le premier dit que le site est en
travaux, le second que la maison n'est pas prête. Un restaurant, lui, **écrit à
l'ardoise** ce qu'il n'a pas photographié. La tuile porte le nom du plat, un
filet de braise, et rien d'autre. C'est aussi **le mécanisme qui servira le
jour où les 48 photos IA sortiront** (voir la question ouverte plus bas).

### Ce que la photo a tranché, et ce qu'elle n'a pas tranché
La colonne des 2ᵉˢ tailles est coupée au bord de la photo, mais **le premier
chiffre se lit** en recadrant :

- **confirmés** : à la crème 6 000 · pili chaud 5 000 · paysanne 6 000 ·
  **pêcheur 6 000** (le `MENU.md` le donnait « à confirmer » : il est bon)
- **absents du site alors qu'ils existent** : **napolitaine** et **oriental**
  ont une grande taille, prix coupé, commençant par 5. ⏳
- **pas de 2ᵉ taille** (colonne vide) : épinards, quatre saisons, fruit de mer,
  margherita — le site a raison
- ⚠️ **Aileron : la ligne est corrigée à la main au surligneur** sur le menu
  papier, et c'est illisible sur la photo. Le site affiche 3 000. ⏳

Les quatre questions à poser à la maison sont dans `MENU.md`, en bas.

### Le QC, enfin écrit : `python _outils/_qc.py`
**30 contrôles** (après `npm run build`) : le compte des plats **lu dans les
données** et jamais recopié, les ardoises lisibles, 0 image cassée, 0
`/carte/undefined.webp`, 0 débordement en 390 et 1440, la fiche qui s'ouvre sur
un plat sans photo, et **la lisibilité du prix mesurée par catégorie**.
⚠️ Trois pièges d'instrument sont documentés en tête du fichier : serveur de
test multi-tâches, les **deux** dialogues de la page, et surtout — le décile le
plus clair ne mesure pas un texte qui couvre un dixième de sa boîte, il mesure
son anticrénelage (il annonçait **2,15:1 sur une pastille parfaitement nette**).

### ⛔ LA QUESTION OUVERTE, QUI APPARTIENT À MONGAZI
**Les 48 photos de plats sont des images générées** (z_image, 2026-07-20).
Depuis le 2026-08-01 le cerveau dit : « INTERDIT ABSOLU : une photo produit
générée par IA présentée comme le catalogue du client. » Angy Art a été purgée
le 2026-08-08, Hillary affiche « Photo sur WhatsApp ». **Au Braisé d'Or est le
dernier site où la règle n'est pas appliquée.** Rien n'a été touché ici sans
décision : l'ardoise est prête, la bascule est de retirer `img` des entrées de
`PHOTO` dans `index.html` et de régénérer.

## 🔥 LE HÉROS DES 14 SAUCES (2026-08-26)

*Détail : `_memoire/conversations/2026-08-26-braise-heros-sauces.md`.*

Trois demandes de Mongazi : **toutes** les sauces au héros, **beaucoup plus
vite**, et **on commande depuis là**.

### ⛔ Le défilement était le moteur, et c'est ce qui bloquait tout
La scène était une piste de **N × 100vh** parcourue par le défilement
(ScrollTrigger « scrub » + aimant). À 4 plats : 400vh. **À 14 sauces :
1 400vh**, quatorze écrans avant la carte. Et une cadence rapide aurait fait
**défiler la page toute seule** à toute vitesse.
→ **La scène tient sur UN écran**, l'index est piloté par un tween sur un
nombre. Le mouvement des assiettes (diagonale + rotation + échelle, réglé image
par image sur la vidéo de référence) **n'a pas bougé d'un pixel** : c'est son
moteur qui a changé, pas son dessin.
✅ La crainte du 21/08 (« reboucler ferait REMONTER la page ») **n'existe
plus** : la boucle est franche, sans le tour de respiration.
✅ On tourne **par le chemin le plus court sur l'anneau** : de la 14e à la 1re,
on avance d'un cran.
⚠️ **Lenis reste** : `aller.ts` passe par `window.__lenis` pour sauter aux
catégories (sans lui, un `scrollIntoView` s'arrête en chemin).

### ⚠️ La pause au survol qui aurait tué le carrousel
`onPointerEnter` sur la scène : **la scène fait tout l'écran**, la souris est
toujours dessus, le carrousel ne serait **jamais reparti** sur un ordinateur.
On ne s'arrête que sur la carte de verre et sur la bande des miniatures.

### `DISHES` est lu dans la carte, plus écrit à la main
Quatre sauces étaient recopiées avec leur prix : deux vérités pour le même
plat. `DISHES` = la catégorie **Sauces** de `carte.ts`. Ajouter une sauce à la
carte la fait entrer au héros toute seule, et **le QC la réclame**.
Sans photo → **ardoise ronde** avec le **filet à la couleur de la sauce**
(huit ardoises identiques ressemblent à une panne, huit couleurs à une
collection).
⚠️ **Béchamel et Crème n'auront jamais de découpe** : `_detoure_plats.py` le
documente depuis le 19/08.

### L'optimisation, mesurée
Les 14 découpes pèsent **plus de 2 Mo** : fenêtre glissante d'images (**4 au
premier écran**, le QC refuse au-delà de 5), et au-delà de la fenêtre une
assiette est **rangée une fois** au lieu d'être repositionnée à chaque image.

### Commander depuis le héros : un pont, pas un second moteur
⛔ Recoder « ajouter au panier » dans le héros = un **deuxième moteur de
commande** avec sa propre idée du prix et de l'accompagnement.
✅ `data/commande.ts` : le héros **demande**, la carte **ouvre sa fiche**. Une
fonction, un nom de plat. Fiche du menu, garnitures, **accompagnement
obligatoire**, fourchette, panier, message : un seul de chaque.
⚠️ **La barre du panier recouvrait la scène** (barre du bas + carrousel).
`body.a-panier` remonte la scène, et un contrôle **mesure le chevauchement**.

### La glace se vend à la boule — le modèle ne savait pas
`p` / `p2` / `pMax` ne portaient que **deux** tailles, et la fiche tenait la
taille dans un **booléen**. Le 3e palier de la glace disparaissait : la maison
encaissait 1 500 F au lieu de 2 500. → **`paliers: [libellé, prix][]`**, un
barème à N crans, et la fiche ne connaît plus qu'un **index**.
⚠️ **Le balisage a maintenant QUATRE façons d'avoir un prix** : `pMax` →
`AggregateOffer` · `p2` → 2 offres · `paliers` → N offres · `p: 0` → aucune.

### ⛔ QUATRE DÉFAUTS QUE LE QC VERT NE VOYAIT PAS
Trouvés **sur les captures**, pas par un contrôle. `_outils/_vues_heros.py`
photographie les 14 sauces en 390 et 1440 : les regarder est la seule façon.

1. **`clearProps: "all"` VIDE l'attribut `style`** (il ne retire pas « ce que
   GSAP a posé »). → **le bouton de commande était INVISIBLE** : fond
   transparent, texte crème, sur verre clair, **1,1:1**. ⚠️ Défaut **antérieur
   à cette session** : l'ancien bouton vert avait le même sort **en ligne**.
   Et le corps du titre, calculé par sauce, était effacé : la **2e ligne
   ressortait plus petite que la 1re**. → `clearProps:
   "opacity,visibility,transform"`, et les couleurs fixes dans une **classe**.
2. **L'ardoise ronde sortait de sa boîte de 100 px** en 390 px : `inset-0` fixe
   déjà les deux dimensions, donc **`aspect-ratio` est ignoré**, et la boîte
   n'est carrée que sur grand écran. → conteneur mesuré + `min(100cqw,100cqh)`.
3. **La pile de points se posait sur le texte** sur téléphone (colonne pleine
   largeur) → masquée sous 768 px.
4. **Les deux flèches du carrousel étaient posées SUR des miniatures** :
   `overflow: visible` + 14 slides qui débordent. → `overflow-x: clip` (garder
   la verticale, sinon l'ombre de la miniature active est rognée).

### Deux défauts trouvés en chemin
⛔ La carte de verre listait les accompagnements des **grillades** sous des
**sauces**. Elle les **lit** maintenant dans la carte.
⛔ **LE SITE A DEUX NUMÉROS WHATSAPP** : `index.html` = `2290156057157`,
`experience/data/dishes.ts` (**le fichier servi**) = `22956057157` — **le `01`
a sauté**. Rien n'a été touché (règle : jamais un lien WhatsApp sans
confirmation). À trancher.

## 📍 LA FICHE GOOGLE — dossier complet dans `GOOGLE-BUSINESS.md` (2026-08-27)

**⛔ On ne crée PAS une deuxième fiche.** La maison a déjà une présence sur
Maps et a perdu l'accès au compte (mail + mail de secours). La demande était
d'en recréer une sous « Aux Braisé d'Or Restaurant » : refusé, et pour trois
raisons.

1. ⛔ **« Aux » est une faute** : `au` = à le (singulier), `aux` = à les. Tout
   le reste de la maison écrit « Au » : l'enseigne, le menu papier,
   `aubraisedor@gmail.com`, le site, le balisage. Une fiche dont le nom
   contredit l'enseigne échoue à la **validation vidéo**, qui filme l'enseigne.
2. ⚠️ **« Restaurant » déplacé à la fin devient un mot-clé** = motif n° 1 de
   suspension (30 jours et plus pour contester). En revanche, **si l'enseigne
   peinte dit « RESTAURANT AU BRAISÉ D'OR », ce nom est légitime tel quel** :
   un nom se recopie, il ne se réarrange pas.
3. ⛔ **Une 2ᵉ fiche double le problème** : Google déduplique sur
   adresse + téléphone + activité. Soit il refuse, soit il **fusionne dans la
   fiche inaccessible** (le travail est perdu), soit **une des deux est
   suspendue**. Et même si ça passe : on perd les avis, l'ancienneté et la
   position Maps de l'ancienne, qui reste en ligne et sort devant.

⚡ **Perdre le mail n'est pas perdre la fiche.** Soit elle n'a jamais été
revendiquée (rien à récupérer, on la revendique), soit elle l'est par un compte
injoignable, et **c'est exactement le cas prévu par « Demander l'accès »** : le
propriétaire ne répond jamais, et **ce silence donne la fiche** au bout de
3 à 7 jours.

### ⚡ CE QUE LA CAPTURE DU 2026-08-27 A TRANCHÉ

L'écran « Demander l'accès » dit : **« Le restaurant "AU BRAISÉ D'OR" appartient
à `bl…@gmail.com` »**. Quatre faits :

1. ⛔ **Le propriétaire n'est PAS `aubraisedor@gmail.com`** : Google masque le
   milieu d'une adresse, jamais le début. Le bon compte commence par **`bl`**.
   ⚡ **Deux questions à la propriétaire valent mieux que la demande d'accès**
   (instantané contre 3 à 7 jours) : « ton Gmail qui commence par `bl`, c'est
   lequel ? » et « qui t'a créé ta page Google ? » (cette personne peut ajouter
   NEBULA en deux minutes).
2. ✅ **La fiche a 4 avis** : la démonstration en une ligne de pourquoi on ne
   recrée pas. Ils ne se transfèrent pas.
3. ✅ **La fiche porte déjà une adresse** (« …221, Cotonou, Bénin ») : le
   blocage de l'adresse tombe tout seul. À lire en entier et à faire confirmer,
   point posé **sur la porte**.
4. ⚠️ **Un 3ᵉ nom en circulation** : la fiche dit « AU BRAISÉ D'OR », le dossier
   dit « Restaurant Au Braisé d'Or », le site dit « Au Braisé d'Or ». La photo
   de l'enseigne tranche.

**Le formulaire** : ➜ **Propriétaire / Possession, JAMAIS « Gestion »** (en
gestionnaire la fiche reste à `bl…`, révocable, et seule la demande de
*propriété* ouvre le « pas de réponse sous 3 jours → tu revendiques ») · nom de
contact = **la propriétaire du restaurant** · téléphone = **celui de la fiche ou
de l'enseigne**, jamais un numéro perso · ⛔ **jamais deux demandes depuis deux
comptes** (ça ressemble à un abus). Compte demandeur : **celui de la maison de
préférence** (aucun transfert ensuite, et dossier bien plus solide si ça finit
en appel manuel) ; à défaut celui de Mongazi, **avec transfert de la propriété
principale ensuite**.

### ⛔ LE COMPTE `bl…` EST PERDU (tranché par Mongazi le 2026-08-27)

« Elle ne se rappelle plus, c'est perdu, considère ça comme ça. » **On n'y
revient plus.** ⚡ Et c'est le cas où « Demander l'accès » marche le mieux : la
procédure repose sur le **silence du propriétaire pendant 3 jours**, et ce
silence est désormais **certain**.

Chemin unique : **J+0** créer le compte de la maison *(⛔ pas celui de Mongazi)*
avec **secours mail + secours téléphone le jour même, notés sur papier**,
trancher le numéro, envoyer la demande en **Propriétaire** · **J+3** l'option de
revendiquer apparaît · **J+7** « Faire appel » avec enseigne + RC + IFU +
document officiel *(c'est le chemin le plus probable)*.
⛔ Pendant l'attente : aucune fiche créée, aucune 2ᵉ demande, aucune
modification de la fiche existante.
⚡ **L'attente n'est pas du temps mort** : c'est le créneau pour réunir adresse,
horaires, numéro et les six photos. **Le chemin critique n'est pas Google, ce
sont les informations manquantes.**

### ⛔ Les quatre blocages, tous antérieurs à la fiche

- **QUATRE numéros en circulation**, et ⚡ **une explication** : le Bénin est
  passé de 8 à 10 chiffres fin 2020 (préfixe `01`). Donc `43 99 29 29` de
  l'enseigne = `01 43 99 29 29` en ancien format, et surtout
  ⛔ **`22956057157` de `dishes.ts` = `01 56 05 71 57` AMPUTÉ de son `01`** :
  c'est l'**ancienne forme** du numéro du site, et c'est **elle qui reçoit
  toutes les commandes**. → tester `wa.me/22956057157` contre
  `wa.me/2290156057157` et `wa.me/2290143992929`. **30 secondes.**
- **L'adresse** : ⚠️ un restaurant où l'on s'assoit **ne peut pas** être en
  « zone de service » comme Hillary. Adresse physique publique obligatoire,
  point posé **sur la porte**.
- **Les horaires** : « ouvert tous les jours » n'en est pas un. ⚠️ Le filtre
  **« Ouvert »** de Maps est l'un des plus utilisés : sans horaires, la maison
  est invisible à l'heure où l'on cherche où manger.
- **Le nom exact de l'enseigne** : le dossier dit « Restaurant Au Braisé d'Or »,
  le site dit « Au Braisé d'Or ». **Deux noms différents pour Google.** Une
  photo de l'enseigne tranche, et le site s'aligne dessus.

### Ce que le dossier contient, prêt à recopier
Nom · catégorie principale *(⚡ le champ le plus lourd de la fiche)* ·
**catégories secondaires Traiteur et Salle de réception, deux activités déjà
vendues que personne ne cherche chez elle** · description **714 caractères
mesurés** (limite 750) · attributs *(⛔ pas d'alcool : la propriétaire a retiré
les 3 cocktails alcoolisés le 19/08)* · **le menu 52 plats / 9 rubriques** dans
le module natif · les photos · la validation vidéo · avis, Q&R, posts ·
**SEO local + GEO**.

⚠️ **Les 48 photos générées restent sur le site (tranché, non rediscuté) mais
ne montent PAS sur la fiche** : autre surface, autre règle, et un client qui
commande d'après une image trop belle laisse un avis à une étoile.

⚠️ **GEO : le site est déjà bien parti** (robots IA autorisés, balisage
`Restaurant` + `Menu` avec les 52 prix, **export statique donc le texte est
dans le HTML servi** — la plupart des robots d'IA n'exécutent pas le JS). Ce
qui manque : la fiche elle-même, la **corroboration** par 3-4 sources au même
NAP, et ⚠️ **un vrai domaine** (`au-braise-dor.pages.dev` n'a aucune autorité
propre et a l'air provisoire) : c'est le geste au meilleur rapport
effort/résultat.

### ⚠️ La leçon, pour tous les clients
À la création de tout compte Google client, **le même jour** : adresse de
secours + numéro de secours renseignés, notés sur papier, **et NEBULA ajoutée
comme gestionnaire**. Ce dernier point aurait suffi ici : la fiche serait
ouverte.

## ⏳ Ce qui reste

- ✅ **FAIT le 2026-08-26 : les quatorze sauces ont leur photo.** Plus une
  seule ardoise, ni dans les sauces ni ailleurs — **les 52 plats du menu ont
  la leur**. Détail : `_memoire/conversations/2026-08-26-braise-les-sauces.md`.
  ⚠️ Au passage, une photo portait le nom d'un autre plat depuis le 19/08 :
  celle dite « sauce graine » était **la sauce arachide** (crémeuse et beige
  quand la graine est rouge d'huile de palme, et servie dans un **bol rond à
  bord cuivré** quand tout le reste est dans l'assiette octogonale noire).
  Réattribuée, sources renommées avec.
- **La vraie photo de la salle.** Le fond est un mur neutre, pas leur
  restaurant. ⚠️ La vidéo `hero.mp4` montre **le gril**, pas la salle.
- **Confirmer le numéro WhatsApp** : `01 56 05 71 57` est câblé, l'enseigne
  affiche `43 99 29 29`.
- Les **vrais avis** et le **nom du chef**.
- L'adresse exacte et la carte, le vrai logo, les réseaux.
- ⏳ **La version « braise »** (vidéo du gril en fond, scène sombre) est dans
  l'historique en **32062e3** : la reprendre est un `git revert`, pas une
  reconstruction. Elle a prouvé qu'inverser toute la scène ne demande de
  réécrire que **cinq jetons de couleur**.

---

## Identité
- Client : **Au Braisé d'Or**
- Secteur : Restaurant (braisé / grillades)
- Livrable : **Catalogue digital** (menu commandable) — 1er catalogue-resto NEBULA
- Marché : Cotonou, Bénin (à confirmer)
- Statut : **LIVE https://au-braise-dor.pages.dev** (Cloudflare Pages, projet `au-braise-dor`, déployé 2026-07-20)

## Décisions
- Architecture : **CATALOGUE DIGITAL** (grille de plats + prix + commande WhatsApp pré-remplie) — validé par Mongazi 2026-07-17
- Direction visuelle : à valider (reco : **braise premium** noir profond + or/braise + bois)
- Périmètre services : à préciser (sur place / à emporter / livraison)

## À DEMANDER au client (WhatsApp, en parallèle du build)
- [ ] **n° WhatsApp Business** (commandes) — à CONFIRMER avant câblage
- [ ] **Menu réel** : plats + prix, par catégorie
- [ ] **Photos** plats + lieu (5-10)
- [ ] **Logo** (si existe)
- [ ] **Adresse exacte** + quartier/ville (Google Maps)
- [ ] **Horaires** d'ouverture
- [ ] **Réseaux** (Instagram / Facebook)
- [ ] Positionnement/ambiance (premium vs populaire)

## ✅ GÉNÉRATION HIGGSFIELD EXÉCUTÉE (2026-07-19, vagues A/B/C)
- **MCP débloqué** : le vrai serveur MCP Higgsfield est connecté (`/mcp` → « Connected »), génération OK via `mcp__higgsfield__*` (le CLI/skills restent bloqués). Détail : [[reference_higgsfield]].
- **Vague A — 7 images (nano_banana_pro, ~14 cr)** : 6 plats photoréalistes (Tilapia braisé, Poulet bicyclette, Pizza feu de bois, Chawarma, Salade JOQ, Cocktail Piña Colada) + 1 image héro (mains gantées noires retournant poisson/brochettes sur flammes, 16:9 2k). Optimisées WebP ≤1100px (43-130 Ko) dans `assets/images/`. Câblées dans la **galerie « La braise en spectacle »** (bento 6 colonnes PC qui tessellise, cartes 2 col tablette / 1 col mobile — bug cascade CSS corrigé : media queries APRÈS les règles de base). Sous-titre honnête « Visuels d'illustration, bientôt remplacés par les photos de la maison ».
- **Vague B — vidéo héro (Kling 3.0 Turbo, 7,5 cr)** : les flammes bougent, mains gantées retournent le poisson, étincelles. 5 s (durée courte optimisée vente, demande Mongazi). Compressée ffmpeg (imageio-ffmpeg) : `hero.mp4` boucle 1,07 Mo + `hero-scrub.mp4` keyframes denses 2,3 Mo. **Câblage** : scroll-scrub sur PC (les images AVANCENT au défilement) + **poster Ken-Burns sur mobile (aucun téléchargement vidéo = data light)** + `prefers-reduced-motion` = poster statique.
- **Vague C — univers braise (1 texture z_image 0,15 cr + CSS/JS gratuit)** : lit de braises `coals.webp` en filigrane sous la **barre d'onglets** ; **halo de braise qui suit le curseur** (PC) ; **boutons chauffés** (balayage d'ember au survol + respiration d'ember sur le CTA or) ; **cadres chauffés** (liseré d'ember sur les cartes plats au survol) ; **onglet actif** = braise vivante qui palpite. Tout respecte `prefers-reduced-motion`.
- **Crédits** : ~21,5 utilisés (test 2 + 7 images ~12 + héro 2k + vidéo 7,5 + texture 0,15), **~76,5 restants** sur les 100 (budget ~50 respecté).
- **QA Playwright** : PC (héro vidéo scrub, galerie bento, onglets braise, halo curseur) + mobile/tablette (poster Ken-Burns, galerie 1/2 col) → 0 erreur console, tout 200. **PAS déployé** (attente accord Mongazi).
- ⚠️ Bump `?v=` de app.css/app.js **inexistants ici** : CSS/JS sont **inline dans index.html** (pas de fichiers externes) → recharge simple.

## ✅ REFONTE + 48 PHOTOS DE PLATS + DÉPLOIEMENT (2026-07-20)
Retours Mongazi après la session Higgsfield → refonte (skill `ui-ux-pro-max` invoqué) :
- **Vidéo héro** : le scroll-scrub « décomposition image par image » a été tenté (scène épinglée 210vh + `requestVideoFrameCallback`) mais **ne passait pas au défilement** chez Mongazi → **abandonné**. Remis en **vidéo d'intro douce qui démarre TOUTE SEULE** à l'entrée (`hero.mp4` boucle muette, autoplay, pause hors-écran via IntersectionObserver, `prefers-reduced-motion` = poster). `hero-scrub.mp4` n'est plus référencé.
- **Photos DANS les cartes** (plus de galerie séparée) : chaque plat a un **cadre image** en haut de sa carte + **prix en pastille verre** ; **carte entière cliquable → fiche de commande qui montre la photo en grand**. La section galerie « La braise en spectacle » a été **supprimée** (markup + CSS).
- **FAB WhatsApp** flottant brillant (bas-droite, anneau pulsant) **retiré** (il restait « Commander » header + héros + fiche).
- **Glassmorphism « verre fumé braise »** : tokens verre (highlight or, hairline), backdrop-filter sur barre d'onglets / feuilles / pastilles de prix, feuille de commande frostée.
- **48 plats = 48 vraies photos générées** (fini les placeholders) : map JS `PHOTO` (nom du plat en minuscules → slug WebP). Chaque fiche de commande affiche aussi la photo.

### Modèle image choisi = **z_image** (pas nano_banana_pro)
- A/B testé **nano_banana_pro (2 cr) vs Recraft V4.1 (1,25 cr) vs z_image (0,15 cr)** sur poulet/pizza/cocktail/burger, **images téléchargées et regardées**. Verdict : **z_image = photoréaliste, 2048², rendu au moins aussi bon** que les autres pour des plats sur ardoise sombre → retenu (nano à 2 cr aurait coûté 84 cr pour 42, hors budget).
- **42 nouvelles images z_image** (1:1) style « braise premium » (charbon + ember + halo doré + fumée), + 4 réutilisées des tests A/B (poulet chair, napolitaine, mojito, cheeseburger). Prompt commun = sujet + « Dark moody charcoal background, warm ember glow, golden rim light, wisps of smoke, appetizing, professional restaurant menu photography, no text/watermark/hands/cutlery ».
- Pipeline : `scratchpad/fetch_dishes.py` télécharge le `_min.webp` de chaque job (via `show_generations`) → réencode **WebP 900px q80** (~72 Ko/pièce, **3 Mo les 42**) dans `assets/images/<slug>.webp`. Slugs = `g-*` grillades, `p-*` pizzas, `c-*` chawarmas, `b-*` burgers, `s-*` salades, `sc-*` sauces, `pd-*` petit-déj, `k-*` cocktails.
- ⚠️ **z_image sujet au rate-limit (429)** si trop d'appels en parallèle → générer par lots de ~6-11.
- **Coût total session** : ~10,2 crédits (dont ~4 en tests A/B). **Solde 66,15 / 100.**
- **QC** : 48/48 plats mappés, 48/48 fichiers présents, 0 lien mort, JS parse OK, tous assets 200 en local ET en prod.
- **Déploiement** : `wrangler pages deploy` d'un dist propre (index.html + assets/images + `assets/videos/hero.mp4` seul ; `assets/raw/` 30 Mo et `hero-scrub.mp4` exclus). 53 fichiers, 5,4 Mo. Projet Cloudflare **`au-braise-dor`** créé + **LIVE https://au-braise-dor.pages.dev** (vérifié 200).

## PLAN GÉNÉRATION HIGGSFIELD (validé — HISTORIQUE, désormais exécuté ci-dessus)
- **Accès** : MCP Higgsfield ajouté à Claude Code (`https://mcp.higgsfield.ai/mcp`, scope user, authentifié via /mcp le 2026-07-19). ⚠️ Le CLI/skills sont BLOQUÉS sur le plan trial (`only_mcp_usage_on_trial_is_available`) → **générer uniquement via les outils MCP** (voir [[reference_higgsfield]]). Budget validé Mongazi = **~50 crédits / 100**, rendu **photoréaliste**.
- **1. Vidéo héro « qui avance au défilement »** : plan cinématique **grillade qui flambe + mains du cuisinier en GANTS NOIRS** qui retourne poisson/brochettes, braises, fumée → image (Nano Banana Pro 16:9 2k, ~2cr) puis animée en vidéo (Kling 3.0 Turbo, ~7,5cr). Câblage = scroll-scrub PC + repli boucle/Ken-Burns mobile.
- **2. Section « ultra puissante »** qui pousse à commander (feu + accroche haute énergie + CTA magnétique).
- **3. 6 visuels de plats photoréalistes** (Tilapia braisé, Poulet bicyclette, Pizza, Chawarma, Salade JOQ, Cocktail) — Nano Banana Pro ~2cr each (~12cr) — marqués « à remplacer » par vraies photos.
- **4. Textures UI boutons** (braise/charbon, or, flamme) via Soul Cinematic 0,12cr — quasi gratuit.
- Après génération : download → optimiser (WebP/JPEG) → câbler dans index.html → QA → rapport (pas de deploy sans accord).

## À FAIRE AUSSI (déjà demandé par Mongazi, en attente de génération/photos)
- Panier + options (taille/accompagnement/qté) + mode Sur place/Emporter/Livraison + message WhatsApp structuré = **DÉJÀ construit** dans index.html (moteur de commande V1).
- Barre de catégories sticky **corrigée** (overflow clip + scroll-spy).
- Ambiance sonore (feu de fond + survol/clic + son commander + boot façon Nintendo DS) = **déjà en place**.

## À REMPLACER / RESTE (placeholders posés pendant le build)
- Photos plats = **48 visuels IA générés** (à remplacer un jour par les vraies photos de la maison si souhaité, mais déjà propres et vendeurs).
- Photo **du lieu** (bloc « La maison » a encore un placeholder) · adresse exacte + carte Google Maps · horaires (badge ouvert/fermé) · logo officiel · réseaux IG/FB · 2ᵉ prix pizzas/grillades · vrais avis · **confirmer n° WhatsApp** (01 56 05 71 57 câblé, vs 43 99 29 29 enseigne).
- ✅ **Affiche A4 + 2 QR** produite (2026-07-20) : `assets/docs/Affiche_Au_Braise_dOr_A4.pdf` (print) + `.jpg` (partage WhatsApp). Design braise (héro flammes + trio tilapia/pizza/mojito), **QR site + QR WhatsApp décodés/vérifiés** (pyzbar). Générateur = `_outils/_build_affiche.py` (Python PIL + qrcode, sans navigateur).
- Reconfirmer direction couleur (braise sombre vs enseigne bleu/blanc/or).

## Infos enseigne (reçues 2026-07-17)
- Nom complet : **Restaurant Au Braisé d'Or**
- Slogan : **« De Paris à Cotonou »**
- Cuisine : **Africaine · Européenne · Américaine** (explique le menu très large)
- Services additionnels : **Service traiteur** + **Place des fêtes** (événementiel)
- Contact : **(+229) 43 99 29 29** (à CONFIRMER = numéro WhatsApp ?) · **aubraisedor@gmail.com** · WiFi 24h/24
- Légal (pied de page / mentions) : RC **RB/COT/24 A 102350** · IFU **0202501441177**
- ⚠️ Couleurs de l'ENSEIGNE = **bleu + blanc + jaune/or** (le menu papier, lui, était orange). Direction actuelle du site = **braise sombre** (choix Mongazi) → à reconfirmer vu l'enseigne.

## Journal
- 2026-07-17 — Création du dossier. Mongazi introduit la cliente (nom seul), puis précise : elle veut un **catalogue digital**. Architecture verrouillée = catalogue.
- 2026-07-17 (13h) — Menu reçu (5 photos → `MENU.md`) + enseigne. Choix validés : catalogue · **braise premium sombre** · son braise. **V1 construite** (`index.html` : dark braise, 3D glass, son braise, tout le menu rendu, commande WhatsApp par plat). Puis enseigne reçue (bleu/blanc/or + slogan + traiteur/place des fêtes + contacts) → questions de recadrage. QA V1 : rendu premium OK, à corriger = kicker hero qui clippe en mobile étroit.
- 2026-07-19 — **Génération Higgsfield exécutée (MCP débloqué)** : héro vidéo braise (scroll-scrub PC / Ken-Burns mobile), galerie de 6 plats + ambiance (bento responsive, bug cascade CSS corrigé), univers braise sur boutons/cadres/curseur/onglets (+ texture lit de braises). QA Playwright PC+mobile OK, 0 erreur. Sources IA lourdes dans `assets/raw/` (gitignoré) ; livrables WebP/MP4 dans `assets/images` + `assets/videos`. **Non déployé** (attente accord).
- 2026-07-20 (3) — **Son remplacé** : le client détestait le son synthétique (Web Audio braise/grésillement). **Retiré tout le moteur Web Audio** (ambiance + bruitages survol/clic/boot) → remplacé par une **boucle mp3 « feu de bois »** (`assets/audio/fire-loop.mp3`, source `_partage/Fat Es BBQ 1 minute of relaxing fire sound..mp3`) qui **démarre au 1er contact** (pointerdown/touchstart/keydown, façon NEBULA Agency) avec fondu ; le bouton haut-parleur du header (#sound) coupe/relance, état en `localStorage`. Redéployé. ✅ testé Playwright (fire-loop.mp3 joué au 1er clic).
- 2026-07-20 (2) — **Polish post-mise en ligne** : (1) **crépitement/ronflement de fond retiré** (`startAmbient` no-op, on garde les retours survol/clic) ; (2) **menu 2 plats par ligne + cartes compactes sur mobile** (`.menu .grid → 1fr 1fr`, description masquée mobile — reste dans la fiche) pour parcourir vite ; (3) **toutes les mentions de brouillon retirées du site public** (« à valider / à confirmer / à préciser / aperçu / exemple / dev-tag ») → carte Maps placeholder remplacée par **vrai lien Google Maps** (recherche par nom+ville), adresse/horaires nettoyés, tags d'avis retirés, watermark « Aperçu NEBULA » supprimé. Nouvelle règle en mémoire : [[feedback_no-placeholder-on-deploy]]. Redéployé + vérifié live.
- 2026-07-20 — **Refonte (skill ui-ux-pro-max) + 48 photos de plats + 1ER DÉPLOIEMENT** (détail section « REFONTE… » ci-dessus). Scroll-scrub héro abandonné (ne passait pas) → intro douce autoplay ; galerie fusionnée dans les cartes (photo + prix + clic→fiche) ; FAB WhatsApp retiré ; verre fumé ; **z_image** retenu après A/B (0,15 cr) pour générer **42 photos** (+4 réutilisées) = 48 plats photographiés. Solde crédits 66,15/100. **LIVE https://au-braise-dor.pages.dev.** Reste : affiche A4+QR, photo du lieu, n° WhatsApp, adresse/Maps, horaires, logo, réseaux, avis.

## 2026-08-19 · les corrections de la propriétaire sont EN LIGNE

Les modifications arrivées par la session téléphone (13 plats retirés, la carte
des sauces, les héros détourés, les deux prix exacts) ont été **construites,
contrôlées et publiées** depuis le PC de Cotonou.

- déploiement : `https://cfc82be6.au-braise-dor.pages.dev` → https://au-braise-dor.pages.dev
- vérifié **dans le corps de la page servie**, pas sur un code 200 :
  « Monyo » 0 fois · gombo 9 · krinkrin 5 · 52 plats · Napolitaine / Mojito /
  Crispy poulet / JOQ Viagra absents · « Mouton frit » toujours là (2 fois)
- les 3 photos de sauces répondent 200 en `image/webp`, l'affiche A4 aussi
- un fichier absent répond bien **404** (et non 200, cf. la panne PISTE)

### ⚠️ Le contrôle qualité ne démarrait pas sur ce PC

`_outils/_qc.py` a été écrit sur la machine du nuage. Trois défauts d'instrument,
corrigés ici, aucun ne venait du site :

1. il **codait en dur** `/opt/pw-browsers/chromium-1194/...` : ce chemin n'existe
   que sur la machine du nuage. Il n'est plus imposé que s'il existe.
2. il lisait `#cat-petitdej` après un **délai fixe de 1,5 s** : sur un poste
   chargé la rubrique n'était pas encore montée et tout s'arrêtait sur un `null`.
   Il **attend** l'élément.
3. la console Windows écrit en **cp1252** : un « ≥ » dans un libellé faisait
   planter la suite **après** l'avoir réussie. Sortie forcée en UTF-8.

**78 contrôles verts, 0 rouge** (mobile 390 + bureau 1440 + lisibilité des prix).

## 2026-08-20 · Les photos générées par IA sont gardées

**Décision de Mongazi : « les photos IA de Braisé d'Or on les garde, oublie
ça ».** Les 48 photos de plats (z_image, 20/07, antérieures à la règle du
2026-08-01) restent en ligne. Le sujet est **clos** : il sort du reste-à-faire.

⚠️ Ce n'est pas une exception à la règle, c'est un héritage assumé. Aucun
**nouveau** visuel généré n'entre dans ce catalogue ni dans un autre.

### Reste à obtenir de la maison

- le prix du **yaourt** et de la **glace** (affichés « Prix sur demande »)
- la correction manuscrite au surligneur sur **l'aileron**
- **confirmer le n° WhatsApp** : 0156057157 câblé, contre 43 99 29 29 sur l'enseigne
- la **vraie photo de la salle**, les vrais avis, l'adresse, le logo

⚠️ `next@14.2.15` porte une vulnérabilité connue signalée par npm.

## 2026-08-20 · ce qui ne se voyait pas : partage, robots, données structurées

La vitrine avait tout ce qui se regarde et **rien de ce qui ne se voit pas**.
Trois manques, tous invisibles depuis le site, tous corrigés sans rien demander
à la maison.

### 1 · Aucune image de partage

Le lien envoyé sur WhatsApp n'était qu'une **ligne de texte grise**. Au Bénin
tout circule par WhatsApp : c'est le défaut le plus cher qu'une vitrine puisse
avoir. `python _outils/_og.py` fabrique `og.jpg` (1200x630, 93 Ko, **JPEG** —
l'aperçu WhatsApp ne lit pas toujours le WebP) : la braise, le nom, et **une
vraie photo de la maison**, la sauce gombo détourée. Aucun texte inventé.

⚠️ **L'instrument mesurait le texte au lieu du fond.** Le contraste du titre
tombait à 1,1:1 parce que les pixels les plus clairs de la zone étaient **les
lettres elles-mêmes**. On relève le fond **avant** d'écrire dessus : 10,8:1.

### 2 · Ni robots.txt, ni sitemap.xml

Écrits. Les robots des IA (GPTBot, ClaudeBot, PerplexityBot) sont explicitement
autorisés : ils citent la maison.

### 3 · Aucune donnée structurée

Un prix réel ne s'affichait dans aucun résultat Google. La page porte
maintenant un `Restaurant` complet, **lu dans `CARTE`, jamais recopié** :
`hasMenu` avec ses 9 rubriques et ses 52 plats, les vrais numéros, l'e-mail.

⛔ **Ce qu'on n'a PAS déclaré** : aucune note ni avis (personne n'en a donné),
aucune adresse de rue (la maison ne l'a jamais donnée : la ville et le pays
suffisent, une adresse inventée est pire que pas d'adresse), aucun horaire
(« ouvert tous les jours » n'est pas un horaire).

⚠️ **UN PLAT A TROIS FAÇONS D'AVOIR UN PRIX**, et les confondre ment :
`pMax` est une **fourchette** (les sauces, selon ce qu'on met dedans) →
`AggregateOffer` ; `p2` est une **deuxième taille** → deux offres ; `p: 0` veut
dire **prix pas encore donné** → aucune offre. Le premier jet ne lisait que
`p` et annonçait « jusqu'à **5 000 F** » alors que la carte monte à **6 000 F**.

### Le contrôle

`python _outils/_qc_partage.py` = **35 contrôles, sans aucun navigateur** (il
lit le fichier servi). Il compare le balisage à la carte plat par plat, refuse
une offre à 0 F, vérifie que les 9 fourchettes portent leur borne haute et que
les 13 plats retirés ne reviennent pas par le balisage.

⚠️ Il a fallu deux corrections d'instrument : une expression régulière « du nom
jusqu'au prix » attrapait le prix du plat **suivant** quand un plat tient sur
plusieurs lignes (les sauces), et `toLocaleString("fr-FR")` sépare les milliers
par une **espace fine insécable** (U+202F) qu'aucune comparaison de texte ne
voit venir.

⚠️ **La suite Playwright (76 contrôles) n'a PAS tourné** : les navigateurs ont
été supprimés le même jour pour libérer le disque. Les changements sont
entièrement dans l'en-tête du document, sans effet sur la mise en page. Pour la
relancer : `npx playwright install chromium` (267 Mo).

---

## LA SCÈNE NE MEURT PLUS AU DERNIER PLAT (2026-08-21)

Mongazi : « il faut que les éléments défilent tout seuls ». Tout était déjà
automatique ici — sauf que `if (iRef.current >= N - 1) return;` arrêtait la
rotation **définitivement** au quatrième plat. Au bout de 22 s, la scène était
morte et le site avait l'air en panne.

**La crainte d'origine était juste, la conclusion trop large.** ⚠️ `aller()`
fait défiler **LA PAGE** : revenir au premier plat la fait **remonter**, en
travers de quelqu'un qui descend vers le menu. Mais ce cas est **déjà couvert
deux fois** — rien ne bouge quand la scène n'est pas à l'écran (garde-fou 2),
et un geste repousse tout de 12 s (garde-fou 5). Ne restait que le visiteur
**immobile, qui regarde** : pour lui, une scène figée n'est pas une protection.

Elle reboucle donc, ⚠️ **avec un tour de plus sur le dernier plat** avant de
remonter : une boucle qui se referme sans respirer ressemble à un bug.
Mesuré sur l'export statique : **0 → 1 → 2 → 3 → 0** en 30 s, sans y toucher.
Build 182 kB, QC **76 verts, 0 rouges**.

---

## ⛔ SIX PHOTOS LIVRÉES, AFFICHÉES NULLE PART (2026-08-27)

*Détail complet : `_memoire/conversations/2026-08-27-braise-deux-machines.md`.*

Les six découpes de sauce (arachide, tomate, tête de mouton, pieds de bœuf,
yassa, yassa au poulet) étaient dans `main` depuis la veille : fichiers
propres, pesés, poussés, en 200. **Et le héros posait quand même son ardoise
sur les six**, en plein premier écran.

Parce que le héros ne lit pas le dossier `/plats`, il lit le `DECO` de
`dishes.ts` :

```ts
img: d?.img,     // d = DECO[nom]  →  absent = ardoise
```

et **aucun des sept commits qui ont posé les images n'a touché `dishes.ts`**.

⚠️ **RIEN NE POUVAIT LE SIGNALER.** Le contrôle « 0 image cassée » ne voit que
les images **demandées**. Une image qu'on ne réclame jamais ne peut pas être
cassée : elle est parfaite et invisible. **Un fichier livré n'est pas un
fichier affiché.**

**Posé le 27/08** : les six `img:` du `DECO` · les six correspondances de la
page de repli `index.html` · les images de carte manquantes dans
`assets/images/` (elle en réclamait déjà trois qui n'existaient pas).

**Nouveau contrôle** : *aucune découpe inutilisée dans `/plats`*. Il lit les
**deux** côtés dans les fichiers, sans recopier aucune liste : le jour où une
sauce arrive, il la réclame tout seul.

### Le héros, après

| | avant | après |
|---|---|---|
| plats illustrés | 46 / 52 | **52 / 52** |
| sauces montrées au héros | 6 | **12** |
| ardoises rondes au héros | 8 | **2** |

Les deux qui restent sont **Béchamel** et **Crème** : elles n'auront **jamais**
de découpe (plat noir sur fond noir, noté depuis le 19/08). Leur ardoise ronde
au filet de la couleur de la sauce est le rendu définitif, pas un pis-aller.

### ⚠️ ET LE MÊME TRAVAIL A ÉTÉ FAIT DEUX FOIS

Le PC de Cotonou avait, non commité, une chaîne complète pour ces six sauces
(deux outils, images, correctif du QC) — pendant que `origin/main` portait déjà
le même travail, poussé depuis le téléphone en 7 commits (`fb93ec7` →
`aeba870`), à partir des **mêmes photos sources au bit près**.

La version de `main` est gardée : elle est plus mûre (rembg/isnet contre une
reconstruction d'alpha depuis le damier — **approche déjà mesurée et rejetée**
dans `_damier.py` : *« les deux gris du damier sont 77 et 124, et le bord noir
de l'assiette a des reflets dans cette plage »*), et son correctif du QC sépare
l'**ardoise** de l'**accompagnement obligatoire** au lieu de laisser les deux
accrochés au même clic. Le commit local `70e3d8b` est **écarté**, pas perdu.

⚠️ **Le garder aurait posé un piège** : `_poser_sauces.py` aurait réécrit en
silence les cadrages que `_photos_sauces.py` gèle exprès, photo par photo.

**Cause racine, corrigée dans `scripts/rapatrier.py`** : le script de début de
session **excluait `origin/main`** de son inventaire et ne surveillait que les
branches `claude/…`. Une session du téléphone pousse **directement dans
`main`** : il répondait « ✅ Rien ne traîne » avec sept commits de retard.

### ⏳ VU EN REGARDANT LES 12 DÉCOUPES : LA VAPEUR DE `sc-moyo` ET `sc-poisson`

Les douze découpes ont été posées côte à côte sur le crème du site
(`#ede9e3`) et regardées. Onze sont propres : assiette entière, aucun halo,
aucun escalier dans le bord. **Deux ne le sont pas.**

Sur **`sc-moyo`** et **`sc-poisson`**, le **panache de vapeur** est sorti du
masque en **forme pleine, gris foncé et opaque** : au-dessus du plat flotte
une silhouette qui ressemble à une **anse ou un crochet**, pas à de la vapeur.
Sur fond blanc ça passe ; sur le crème du héros, c'est une tache.

⚠️ **Ce n'est pas un défaut du 27/08** : ces deux découpes sont en ligne depuis
le 26/08, elles n'ont pas été retouchées aujourd'hui. Personne ne l'avait vu
parce qu'on regarde les images **une par une** — c'est en les mettant **toutes
les douze ensemble** que les deux intruses sautent aux yeux.

**Le remède est déjà écrit dans `_damier.py`** : c'est la « rustine
anti-vapeur », dont la note dit qu'elle ne servait plus sur la krinkrin
(9 lignes étroites, largeur croissante = le coin de l'octogone). Sur ces deux
plats-là, il y a bien un panache. ⚠️ **Refaire la planche comparative des
modèles pour ces deux photos** avant de choisir : `isnet` gagne sur damier,
`birefnet` sur fond noir, et **le fond change le gagnant**.

---

# 2026-09-15 — L'ATTIÉKÉ ENTRE À LA CARTE (52 → 53 plats)

Demandé par Mongazi. Détail complet :
`_memoire/conversations/2026-09-15-braise-attieke.md`.

**Attiéké · 2 000 F · rubrique Grillades · au poisson ou à la viande.**

⚠️ **Il n'existait que comme ACCOMPAGNEMENT** (« Attiéké » chez les grillades,
« Atchiéké » chez les sauces), jamais comme plat. Ni prix ni photo dans la
maison : les deux ont été demandés avant d'écrire une ligne.

## Deux champs neufs dans le modèle

- **`choix: { libelle, options }`** — un choix **obligatoire, à prix égal**.
  ⚠️ Ce n'est ni une taille (`p2` : le prix ne bouge pas), ni une garniture
  (`garn` : facultative et fait monter le prix), ni un barème (`paliers`). Le
  tordre dans `p2` aurait affiché « 2 000 F / 2 000 F » sur la pastille.
  Sans réponse, le bouton reste gris : « Poisson ou viande ? ».
- **`sansAcc: true`** — ⚠️ **l'attiéké EST un des dix accompagnements de la
  rubrique Grillades** : sans ce drapeau, sa fiche proposait « Attiéké » comme
  accompagnement de l'attiéké.

Le choix voyage jusqu'au bout : clé de ligne du panier, message WhatsApp
(« 1 × Attiéké (Poisson) »), et **il partage la parenthèse de la taille** —
« (Grand, Poisson) », jamais « (Grand) (Poisson) ».

## ⛔ Le piège du 26/08 s'est refermé à l'envers

Le QC accrochait l'ardoise ET l'accompagnement obligatoire **au même clic**.
L'attiéké redevenant le seul plat sans photo, ce clic tombait sur lui — et
comme il ne demande pas d'accompagnement, **ce contrôle-là se serait éteint
sans un mot, tout vert**. → **une règle, une fiche** : trois clics
indépendants, et les plats à choix sont **lus dans `carte.ts`**.

## ⛔ `button.flex-1` attrapait aussi les boutons de taille

Défaut **antérieur** de la sonde : sur « Sauce Yassa au poulet », seule sauce
à deux tailles, le QC cliquait « Quart de poulet · 2 500 F » au lieu de
« Ajouter ». Le héros montrant une sauce au hasard, **ça ne ratait qu'une fois
sur quatorze**. → prise explicite **`data-ajouter`**, plus deux autres pour
les contrôles : **`data-plat`** sur chaque carte, **`data-choix`** sur le bloc.

## L'image

⛔ **Aucune image générée.** WaveSpeed était à **0,03 $** (il en faut 0,14) et
Higgsfield à **0 crédit**, mesurés — et Mongazi a tranché pour **une vraie
photo**, qu'il envoie. En attendant, **l'ardoise** : le nom du plat sur la
pierre, le mécanisme du 19/08. Poser la photo = une entrée dans `PHOTO` de
`index.html`, le fichier dans `assets/images/` **et**
`experience/public/carte/`, puis `node _outils/_extraire_carte.js`.

**QC 102 → 117 verts** · `_qc_partage` 36 verts, 53 plats balisés ·
nouveau `_outils/_vues_attieke.py` (6 captures, 390 et 1440).

⏳ **À confirmer** : la photo · la description (écrite par moi) · quel poisson
et quelle viande · la rubrique (Grillades, faute d'une meilleure).

---

## 📌 Résumé transféré de `CLAUDE.md` (2026-09-16)

> Cette ligne vivait dans le tableau « Clients actifs » de `CLAUDE.md`, où elle pesait **17 623 caractères**. `CLAUDE.md` est chargé à chaque session et avait dépassé la limite de 150 000 caractères de Claude Code : le détail vit désormais ici, et `CLAUDE.md` n'en garde qu'un résumé qui renvoie à ce fichier.
> Le texte est recopié **sans un mot changé**, découpé en puces aux séparateurs `·` d'origine. C'est un **historique** : chaque puce porte sa date, et quand deux puces se contredisent, la plus récente fait foi.

**Métier** : **Au Braisé d'Or** — restaurant **braisé / grillades au feu de bois** à Cotonou (« De Paris à Cotonou ») · **catalogue digital** + traiteur & place des fêtes

**WhatsApp** : 0156057157 (à confirmer, vs 43 99 29 29 enseigne · ⚠️ **et `dishes.ts` en utilise un AUTRE, sans le `01`**)

**État, dans l'ordre où il a été écrit :**

- **LIVE https://au-braise-dor.pages.dev**
- ⚠️ **DEPUIS LE 2026-08-12 LE SITE N'EST PLUS `index.html`** : l'adresse sert le projet **Next.js de `clients/09-au-braise-dor/experience/`** (Next 14 + TypeScript + Tailwind + **GSAP/ScrollTrigger/CustomEase + Swiper + Lenis**, pile demandée par Mongazi ; j'avais recommandé le natif, il a maintenu ; **179 kB de JS** au premier chargement). `index.html` reste dans le dépôt, un retour arrière est un déploiement
- **expérience à 4 plats signature** (défilement **automatique** 5,5 s, assiettes détourées qui **ROULENT sur un arc**, titre en deux lignes qui se dédouble, carte de verre, prix qui compte de 0, carrousel Swiper, **tiroir des 8 univers** ouvert depuis le héros) **puis les 48 plats commandables** (toujours tous affichés : le filtre en cachait 38 ; chips en ancres + scroll-spy ; fiche taille/accompagnement/quantité ; panier ; message WhatsApp rédigé)
- ⛔ **NI NOTE, NI CHEF, NI LIKES INVENTÉS** (la référence en affichait ; le carré coloré porte **le prix**, qui est vrai)
- ⚠️ **7 pièges documentés** : `background-image` non différable (4,3 Mo avant le menu), **`gsap.from()` laisse l'élément invisible si on l'interrompt**, `fixed` qui ne se décolle jamais, pourcentages de hauteur sur téléphone, `width:auto` = boîte de zéro, **conteneur plein écran qui avale les clics**, et **LENIS QUI INTERROMPT TOUT `scrollIntoView`** (saut arrêté à 7 382 px de sa cible)
- ⚠️ **une vidéo de référence se MESURE image par image**
- publier = `npm run build` + `cp -r ../assets/docs out/` + `wrangler pages deploy out`
- ✅ affiche A4 + 2 QR faite
- **VAGUE 2026-08-26 — LES 52 PLATS ONT LEUR PHOTO** (plus une seule ardoise) : 9 assiettes posées ou refaites
- ⚠️ **les fichiers reçus sont TOUJOURS opaques** (celui qui montre un damier est un JPEG, damier peint dans les pixels ; le `.png` est la photo fond noir)
- **planche comparative refaite à chaque lot, isnet gagne 6 fois sur 6 sur damier** — mais la refaire a évité de poser **une viande sans assiette** sur la tête de mouton (écart 26 points)
- ⛔ **`_photos_sauces.py` mourait en CODE 137 à la 2e photo** (fuite onnxruntime, comme chez Hillary) → **une photo, un processus**
- ⚠️ **le réparer a réveillé 2 cartes qu'il n'atteignait plus et les a écrasées** → drapeau de **gel**, et ⚠️ **le gel suit le FICHIER, pas le slug**
- ⛔ **une photo portait le nom d'un autre plat depuis le 19/08** : la « graine » était **l'arachide** (beige et crémeuse vs rouge palme, bol cuivré vs assiette octogonale) → réattribuée, sources renommées
- ⛔ **le contrôle du bouton du héros mentait déjà sur `main`** : il photographiait l'opacité au milieu d'une animation permanente (mesuré : **max 1,00, pleine opacité 71 % du temps**) → il échantillonne
- ⛔ **le QC PLANTAIT sur un `null.click()`** le jour où le dernier plat a eu sa photo, et **2 contrôles sans rapport étaient sur le même clic** : l'ardoise (cas particulier) et **l'accompagnement obligatoire** (règle métier) → séparés, le second reste vert
- **`reboucher()`** neuf : cavités + **fentes ligne par ligne** (jamais colonne, on souderait la vapeur), **seuil 8 % mesuré sur les 10 assiettes**
- **QC 92 verts / 0 rouge**
- ⏳ **« gbata » ou « gbotâ »** à trancher
- reste : **vraie photo de la salle**, confirmer n° WhatsApp, vrais avis, adresse/Maps, logo, réseaux
- **VAGUE CATALOGUE 2026-08-19** (détail `_memoire/conversations/2026-08-19-braise-catalogue.md`) : carte relue **contre les 5 photos du menu papier**, pas contre `MENU.md` qui n'en est que le résumé → **48 → 52 plats** (les 4 lignes de petit-déj que la maison vend et que le site ne proposait pas : café chaud serré 500, Lipton citron 500, œuf sur plat 1 000, café au lait écrémé 1 000)
- ⛔ **le PRIX était illisible sur les 52 cartes** : la pastille n'avait aucune couleur de texte et posait `--encre #1d1a17` sur `rgba(0,0,0,.65)`, **1,1:1 mesuré** → `#f6efe6` sur 70 %, **13,9:1 à 18:1**
- **l'ARDOISE** = un plat sans photo porte son nom écrit (⛔ ni cadre vide ni « photo à venir »), et c'est **le mécanisme prêt pour le jour où les 48 images générées sortiront**
- **`python _outils/_qc.py` = 30 contrôles** (le client 09 n'en avait aucun)
- ⚠️ **pêcheur 6 000 est BON** : `MENU.md` disait « à confirmer », le 6 est lisible en recadrant la photo — **on ne corrige pas une donnée contre un résumé**
- ⏳ **napolitaine et oriental ont une 2e taille ABSENTE du site** (prix coupé, commence par 5) et **l'aileron porte une correction manuscrite au surligneur** illisible
- ✅ **LES 48 PHOTOS GÉNÉRÉES PAR IA SONT GARDÉES** (z_image, 20/07, avant la règle) — **tranché par Mongazi le 2026-08-20 : « on les garde, oublie ça »**. Héritage assumé, **pas une exception** : la règle du 2026-08-01 reste absolue et aucun nouveau visuel généré n'entre dans un catalogue. ⛔ Sujet clos, ne plus le remonter
- **CORRECTIONS DE LA PROPRIÉTAIRE le même soir (note manuscrite)** : prix validés, **13 plats RETIRÉS et la catégorie Desserts ajoutée → 52 → 42 plats** (pizza : napolitaine/oriental/margherita/pili chaud/à la crème/**pêcheur** = 6 sur 10 · grillades : lapin ou mouton frit + viande de caille · burgers : crispy + nugget · cocktails : « tout sauf les jus de fruit » = les 3 alcoolisés)
- ⚠️ **RETIRER UN PLAT N'EST PAS SUPPRIMER UNE LIGNE** : la **pizza pêcheur était un des 4 plats signature du HÉROS** (→ remplacée par la paysanne) et **2 notes de catégorie devenaient fausses** (« sauf crispy, nugget » sans crispy ni nugget, « avec ou sans alcool » sans alcool) — les données se régénèrent, **les phrases ne sont vérifiées par rien**
- **Desserts (yaourt/glace/cocktail) SANS PRIX** → convention **`p:0` = prix pas encore donné**, la carte affiche « Prix sur demande » et la fiche remplace le panier par « Demander le prix sur WhatsApp » (⚠️ **un article à 0 n'entre JAMAIS au panier** : le total mentirait)
- **QC = 62 contrôles**, dont **un par plat retiré** et « aucun prix à 0 F »
- ✅ **Mongazi tranche le soir même** : ⚠️ **le MOUTON FRIT RESTE à 3 000 F** — la note disait « Lapin », la ligne du menu dit « lapin **ou mouton** frit », et retirer la ligne entière avait **supprimé un plat que la maison vend** (→ **une ligne de menu avec un « ou » est deux produits**)
- le « cocktail » **sort des desserts** (doublon avec les 3 cocktails de fruits à 2 500 F) → desserts = **yaourt + glace**, prix demandés plus tard, « Prix sur demande » assumé
- ⏳ 3 questions restantes en bas de `MENU.md` (prix yaourt/glace · aileron · n° WhatsApp)
- **VAGUE SAUCES + MISE EN LIGNE 2026-08-19** : catégorie **Sauces (14)** ajoutée avec ses fourchettes de prix et **4 vraies photos de la maison** (gombo, krinkrin, graine, feuille — les 4 sont AU HÉROS, qui ne montre plus que les sauces, détourées par la maison)
- ⚠️ **la krinkrin n'était pas mal détourée, elle était RECADRÉE TROP SERRÉ à la source** : mesurer si le sujet touche le bord avant de chercher un masque, sinon redemander la photo, « tout dedans » = le prix le plus cher
- **carte à 9 rubriques / 52 plats**
- ✅ **PUBLIÉ ET VÉRIFIÉ DANS LE CORPS DE LA PAGE SERVIE** (« Monyo » 0 fois, Napolitaine/Mojito/Crispy/JOQ absents, « Mouton frit » présent, photos 200, fichier absent → **404**)
- ⚠️ **`_outils/_qc.py` ne démarrait pas sur le PC** : chemin de navigateur codé en dur pour la machine du nuage, attente fixe de 1,5 s au lieu d'attendre l'élément, et console Windows **cp1252** qui plantait sur un « ≥ » **après** avoir réussi le contrôle → **78 contrôles verts** 
- **VAGUE PARTAGE + SEO 2026-08-20** : la vitrine avait tout ce qui se regarde et **rien de ce qui ne se voit pas** → **`og.jpg` en JPEG** (braise + **vraie** photo de la maison, `_outils/_og.py`), `robots.txt` (robots IA autorisés), `sitemap.xml`, et un **`Restaurant` + `Menu` LU dans `CARTE`** (9 rubriques, 52 plats, vrais numéros)
- ⛔ **ni note, ni avis, ni adresse de rue, ni horaire inventés**
- ⚠️ **UN PLAT A TROIS FAÇONS D'AVOIR UN PRIX** : `pMax` = fourchette (sauces) → `AggregateOffer`, `p2` = 2e taille → 2 offres, `p:0` = pas de prix → aucune offre ; le 1er jet ne lisait que `p` et annonçait **« jusqu'à 5 000 F » quand la carte monte à 6 000**
- ⚠️ **l'instrument mesurait le TEXTE au lieu du FOND** (contraste du titre à 1,1:1 sur une image parfaitement lisible : relever le fond AVANT d'écrire dessus → 10,8:1)
- **`_outils/_qc_partage.py` = 35 contrôles SANS navigateur** (les navigateurs Playwright ont été supprimés pour le disque : `npx playwright install chromium`, 267 Mo, pour relancer les 76)· détail `clients/09-au-braise-dor/CONTEXT.md` et `_memoire/conversations/2026-08-12-braise-experience-next.md`
- **2026-08-21 — LA SCÈNE NE MEURT PLUS AU DERNIER PLAT** : `if (iRef.current >= N-1) return;` arrêtait la rotation DÉFINITIVEMENT, le site avait l'air mort au bout de 22 s ; elle reboucle désormais, ⚠️ avec **un tour de plus sur le dernier plat** avant de remonter (une boucle qui se referme sans respirer ressemble à un bug)
- la crainte d'origine (⚠️ `aller()` fait défiler LA PAGE, donc reboucler la fait REMONTER) était **déjà couverte deux fois** : rien ne bouge hors écran, et un geste repousse de 12 s
- **VAGUE 2026-08-26 — LES 6 DERNIÈRES PHOTOS, LA GLACE À LA BOULE, ET LE HÉROS QUI DEVIENT LE COMPTOIR** (détail `_memoire/conversations/2026-08-26-braise-heros-sauces.md`) : **6 images générées et posées** (œuf sur plat, café au lait écrémé, café serré, Lipton citron, yaourt, glace ; `_outils/_gen_plats.py`, nano-banana-pro, 0,84 $) sur **ordre explicite de Mongazi** — ⚠️ **exception nommée sur CE client** (produits de commodité, héritage déjà assumé), **la règle du 2026-08-01 reste entière ailleurs**
- **prix reçus** : yaourt **600 F**, glace **1 000 / 1 500 / 2 500 F** ⛔ **le modèle ne portait que DEUX tailles** (`p`/`p2`, et la fiche tenait la taille dans un **booléen**) → le 3e palier disparaissait et la maison encaissait 1 500 au lieu de 2 500 → **`paliers: [libellé, prix][]`**, la fiche ne connaît plus qu'un **index** ; ⚠️ **le balisage a maintenant QUATRE façons d'avoir un prix** (`pMax`→AggregateOffer · `p2`→2 offres · `paliers`→N offres · `p:0`→aucune)
- **HÉROS : les 14 sauces, il avance seul toutes les 2,8 s (était 5,5), on y commande** ⛔ **le DÉFILEMENT était le moteur** (piste de N×100vh) : à 14 sauces ça faisait **1 400vh**, quatorze écrans avant la carte, et « plus vite » aurait fait **défiler la page toute seule** → **la scène tient sur UN écran**, l'index est un tween sur un nombre, **le mouvement des assiettes n'a pas bougé d'un pixel** ✅ la crainte du 21/08 (« reboucler fait REMONTER ») **n'existe plus**, boucle franche, chemin le plus court sur l'anneau
- ⚠️ **Lenis reste** (`aller.ts` en dépend)
- ⚠️ **la pause au survol aurait tué le carrousel** : `onPointerEnter` sur une scène qui fait TOUT L'ÉCRAN = il ne repart jamais sur un PC → on ne s'arrête que sur la carte de verre et la bande des miniatures
- **`DISHES` est LU dans `carte.ts`** (4 sauces y étaient recopiées avec leur prix = deux vérités), sans photo → **ardoise ronde au filet de la couleur de la sauce** ; ⚠️ **Béchamel et Crème n'auront jamais de découpe** (documenté depuis le 19/08)
- **optimisation mesurée** : 14 découpes = 2 Mo → fenêtre glissante (**4 images au 1er écran**), et hors fenêtre une assiette est **rangée une fois** au lieu d'être repositionnée à chaque image
- **commander depuis le héros = un PONT, pas un 2e moteur** (`data/commande.ts` : le héros demande, la carte ouvre SA fiche → accompagnement obligatoire, fourchette, panier, message : un seul de chaque)
- ⚠️ **la barre du panier recouvrait la scène** → `body.a-panier` + **`--barre-h` MESURÉE** (les rem écrites à la main laissaient 8 px de recouvrement à 390 px)
- ⛔ **la carte de verre listait les accompagnements des GRILLADES sous des SAUCES** → lue dans la carte
- ⛔ **LE SITE A DEUX NUMÉROS WHATSAPP** : `index.html` `2290156057157` vs `dishes.ts` (**le fichier servi**) `22956057157`, **le `01` a sauté** — rien touché, à trancher
- ⛔ **4 DÉFAUTS QUE LE QC VERT NE VOYAIT PAS**, trouvés **sur les captures** (`_outils/_vues_heros.py` photographie les 14 sauces en 390 et 1440) : **`clearProps: "all"` VIDE l'attribut `style`** — le **bouton de commande était INVISIBLE** (fond transparent, texte crème sur verre clair, **1,1:1**), ⚠️ **défaut ANTÉRIEUR, l'ancien bouton vert avait le même sort EN LIGNE**, et le corps du titre calculé par sauce était effacé (**la 2e ligne ressortait plus petite que la 1re**) → `clearProps: "opacity,visibility,transform"` + couleurs fixes dans une **classe**
- **l'ardoise ronde sortait de sa boîte de 100 px** à 390 (`inset-0` fixe déjà les 2 dimensions donc **`aspect-ratio` est ignoré**) → conteneur mesuré + `min(100cqw,100cqh)`
- **la pile de points se posait sur le texte** sur téléphone → masquée sous 768 px
- **les 2 flèches du carrousel étaient posées SUR des miniatures** → `overflow-x: clip` (garder la verticale, sinon l'ombre est rognée)
- **QC 64 → 102 contrôles** (+ `_qc_partage` 35 → 36) ⚠️ **2 pannes d'instrument, aucune du site** : le contrôle de débordement mesurait le **X d'une animation GSAP** (GSAP ignore `prefers-reduced-motion`) et accusait « KRINKRIN dépasse de 36 px » → `scrollWidth - clientWidth`, insensible aux transformations ; et le contrôle « ça avance seul » a un **TÉMOIN** avant celui de la pause
- **2026-08-27 — SIX PHOTOS LIVRÉES, AFFICHÉES NULLE PART** (détail `_memoire/conversations/2026-08-27-braise-deux-machines.md`) : les six découpes de sauce étaient dans `main` depuis la veille, propres, pesées, en 200 — **et le héros posait quand même son ardoise sur les six**, en plein premier écran ⚠️ **le héros ne lit pas le dossier, il lit le `DECO` de `dishes.ts`** (`img: d?.img`, absent = ardoise) et aucun des 7 commits qui ont posé les images ne l'a touché ⛔ **RIEN NE POUVAIT LE SIGNALER** : le contrôle « 0 image cassée » ne voit que les images **demandées**, et une image qu'on ne réclame jamais ne peut pas être cassée — **un fichier livré n'est pas un fichier affiché**
- posé : les 6 `img:` du `DECO`, les 6 correspondances de `index.html`, les images de carte manquantes dans `assets/images/`
- **nouveau contrôle** « aucune découpe inutilisée dans /plats » (il lit les DEUX côtés dans les fichiers)
- **héros 6 → 12 sauces montrées, 8 → 2 ardoises** (Béchamel et Crème n'en auront jamais)
- ⚠️ **LE MÊME TRAVAIL A ÉTÉ FAIT DEUX FOIS** : le PC avait une chaîne complète non commitée pendant que `main` portait déjà le même travail, mêmes sources au bit près — la version de `main` est gardée (rembg/isnet contre une reconstruction d'alpha **déjà mesurée et rejetée** dans `_damier.py`), le commit local `70e3d8b` **écarté** (le garder aurait réécrit en silence les cadrages gelés exprès)
- **2026-09-15 — L'ATTIÉKÉ ENTRE À LA CARTE, 52 → 53 plats** (détail `_memoire/conversations/2026-09-15-braise-attieke.md`) : **Attiéké 2 000 F dans Grillades, au poisson ou à la viande** ⚠️ **il n'existait que comme ACCOMPAGNEMENT** (deux fois : « Attiéké » chez les grillades, « Atchiéké » chez les sauces), ni prix ni photo dans la maison — **les deux ont été demandés avant d'écrire une ligne**
- ⚠️ **UN CHOIX OBLIGATOIRE À PRIX ÉGAL N'EST NI UNE TAILLE, NI UNE GARNITURE, NI UN BARÈME** : le modèle avait quatre façons d'avoir un prix et une façon de choisir (`garn`, facultative et qui fait MONTER le prix), poisson/viande n'entre dans aucune (le tordre dans `p2` affichait **« 2 000 F / 2 000 F »** sur la pastille) → champ **`choix`**, et sans réponse le bouton reste gris « Poisson ou viande ? »
- ⚠️ **UN PLAT QUI EST DÉJÀ UN ACCOMPAGNEMENT N'EN REDEMANDE PAS UN** : la fiche proposait « Attiéké » comme accompagnement de l'attiéké → **`sansAcc`**
- le choix voyage jusqu'au **message WhatsApp** (« 1 × Attiéké (Poisson) ») et **partage la parenthèse de la taille**
- ⛔ **LE PIÈGE DU 26/08 S'EST REFERMÉ À L'ENVERS** : le QC accrochait l'ardoise ET l'accompagnement obligatoire **au même clic**, l'attiéké redevenant le seul plat sans photo ce clic tombait sur lui, et **le contrôle de l'accompagnement se serait éteint sans un mot, tout vert** → **une règle, une fiche** (l'ardoise · **toujours une sauce** pour l'accompagnement · les plats à choix **lus dans `carte.ts`**)
- ⛔ **`button.flex-1` ATTRAPAIT AUSSI LES BOUTONS DE TAILLE** : sur « Sauce Yassa au poulet », **seule sauce à deux tailles**, le QC cliquait « Quart de poulet · 2 500 F » au lieu de « Ajouter » — défaut **antérieur** qui ne ratait **qu'une fois sur quatorze** (le héros montre une sauce au hasard) → prises explicites **`data-ajouter`**, **`data-plat`**, **`data-choix`**
- ⚠️ **ma propre sonde a cassé l'instrument** (variable `attendu` écrasée : le 2e passage mourait sur un `%d`) et ⛔ **un `dire(… or True, "")` écrit de ma main** retiré
- ⚠️ **défaut vu sur la CAPTURE, QC vert** : le « ? » tombait seul sur sa ligne → **espace fine insécable**, que le français demande de toute façon
- ⛔ **AUCUNE IMAGE GÉNÉRÉE** : WaveSpeed mesuré à **0,03 $** (il en faut 0,14) et Higgsfield à **0 crédit**, et **Mongazi a tranché pour une vraie photo** qu'il envoie → **l'ardoise** en attendant (poser la photo = une entrée dans `PHOTO` de `index.html`, le fichier aux **deux** endroits, puis `node _outils/_extraire_carte.js`)
- **QC 102 → 117 verts**, `_qc_partage` 36
- ⏳ **à confirmer** : la photo
- la description (écrite par moi)
- quel poisson, quelle viande
- la rubrique
