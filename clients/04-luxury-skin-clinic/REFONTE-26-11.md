# LUXURY CLUB 229 · le chantier du 26/11 (refonte 3D + ajouts de la cliente)

Rang 1 de la zone travaux (`_memoire/TRAVAUX.md`). Tout ce qui a été demandé est ici, mot pour mot quand c'est utile,
pour qu'aucune session ne reparte de zéro.

## 1. Ce que Mongazi a demandé (26/11, /vague)
« La refonte de Luxury [Skin Clinic], sa vitrine ENTIÈREMENT en 3D, 3D scrolling adapté à sa vitrine, dans un salon de
beauté bien beau, bien lumineux, intégrer tout ça à l'intérieur. De plus elle veut des ajouts. » À enchaîner tout de
suite après les étiquettes d'Au Braisé d'Or (livrées le 26/11).

## 2. Les ajouts de la cliente (26/11, message transmis par Mongazi)
### 2.1 Cozy rejoint INA Luxury
- Transférer **tous** les produits de Cozy dans la rubrique produits d'**INA Luxury**.
- Ajouter dans INA les catégories de Cozy : **Hygiène intime**, **Produits raffermissants**, et toutes les autres
  catégories de Cozy. Tous les produits doivent être accessibles depuis INA Luxury, sans passer par Cozy.

### 2.2 L'espace Cozy devient la rubrique de son NOUVEAU DOMAINE (sa formation : l'harmonisation faciale)
Même principe que Luxury Skin Clinic (les clientes consultent les soins et leurs tarifs). Elle présente : les nouvelles
prestations, les descriptions des protocoles, les indications, les tarifs, les informations pour comprendre chaque
prestation. **Ses 3 flyers** (dans `assets/harmonisation/`) en sont le contenu, et elle veut leurs VISUELS sur le site
(« là, les gens vont comprendre exactement de quelle zone on parle »).

**Flyer 1 · FACIAL BALANCING** (`flyer-facial-balancing.jpg`) : « Le facial balancing est la combinaison de ces différentes
techniques pour rajeunir votre visage et le rendre plus frais et beau. »
- Zone supérieure (front + cerne) : 500 000 FCFA
- Milieu du visage (pommette + nez) : 1 000 000 FCFA
- Zone inférieure (lèvre, mâchoire, joue et menton) : 800 000 FCFA
- **Genesis Face** (tout le visage) : 2 200 000 FCFA

**Flyer 2 · HARMONISATION FACIALE · GENESIS HOLLYWOOD** (`flyer-genesis-hollywood.jpg`) : « Le Genesis Hollywood est une
technique qui va permettre de relifter votre peau et votre visage, d'affiner votre visage et d'adoucir vos traits, et de
traiter tout ce qui est rides dynamiques. » Zones montrées : Frontalis (rides du front), zone glabellaire (rides de la
concentration).
- Frontalis + zone glabellaire (rides du front et entre les sourcils) : 300 000 FCFA
- Rhinoplastie (non chirurgicale) : 600 000 FCFA
- Affiner le bas du visage : 200 000 FCFA
- Visage complet : 1 000 000 FCFA

**Flyer 3 · HARMONISATION FACIALE · GENESIS SOFT** (`flyer-genesis-soft.jpg`) : « Le Genesis Soft est une technique qui va
permettre de modifier le volume et d'améliorer son aspect visuel. La perte de volume est très fréquente dès qu'on
commence à prendre de l'âge. »
- Creux infraorbitaire : 300 000 FCFA
- Sillon nasogénien (ride du sourire) : 600 000 FCFA
- Restructuration labiale (lèvres) : 300 000 FCFA
- Redéfinition de la mâchoire et des joues : 2 100 000 à 2 400 000 FCFA (fourchette)
- Note : « Si vous désirez un volume vraiment plus grand, des frais supplémentaires pourraient être appliqués. »

### 2.3 Ses vocaux (25/11, transcrits)
1. « Ce serait parfait si tu arrives à intégrer [les visuels des flyers] sur le site. Là, les gens vont comprendre
   exactement de quelle zone on parle. Amuse-toi et fais-moi ça comme tu peux. » (occupée, hors du Bénin)
2. « C'est le plus gros travail. Les autres, c'est je dois supprimer certaines choses de INA Lux… et ajouter quelques
   nouveaux soins de visage dans Luxury Skin Clinic. » ⏳ **La liste des suppressions dans INA et des nouveaux soins
   visage n'est pas encore donnée** : ne rien supprimer ni inventer avant.
3. « Tu as pu voir le truc pour les paiements sur le site directement, Mobile Money et tout ? Dis-moi ça va coûter
   combien pour qu'on puisse l'intégrer le plus tôt possible. » ⏳ **Prix à fixer par Mongazi** (techniquement : SasPay,
   déjà branché sur PISTE et MA LETTRE À…, Mobile Money et carte, 61 réseaux, minimum 200 XOF).

## 3. Le plan (dans cet ordre)
**Les références (26/11)** : FIRST PAGE 3D (le parcours de clinique, pour la STRUCTURE) + Vibrant Wellness (la zone
qui s'allume sur un buste, pour l'EFFET), détail Facework (la fiche de soin). Décorticage et prompt complet :
`C:/Users/USER/nebula-apercus/_socle/references/FIRSTPAGE-VIBRANT-clinique-PROMPT.md` (hors dépôt, registre des
références). ⏳ **À faire valider par Mongazi avant la construction (B).** Décidé dans le prompt :
- la clinique est un voyage en 10 stations, de la porte au bureau des rendez-vous ;
- l'harmonisation faciale est une page à part (`harmonisation-faciale.html`, l'ex-Cozy) : le « cabinet privé »
  encre et or, où l'on touche les zones sur **SES visuels de flyers** ;
- le buste de Poly Haven est écarté (un Romain au visage sévère) ;
- tout le décor est fait en code, sans GLB lourd.

- [x] A1 · Cozy → INA (26/11), par `python _outils/_cozy_vers_ina.py`, idempotent :
  - les 7 produits sont LUS dans `cozy.html` et entrent dans une 6e famille « Intime & bien-être », avec ses 3
    catégories sous leurs libellés exacts (Hygiène intime 1, Selfcare 4, Produits raffermissants 2) ;
  - **INA passe de 49 à 56 produits**, et le script refuse d'écrire si un nom manque ou se double ;
  - les besoins de Cozy (libellés en clair) sont devenus des clés de `CONCERNS`, avec ses mots ;
  - `important` est devenu `warn` ;
  - la variante (« Fraise Sucrée ») s'affiche en or clair `#c9a84c` sur la carte noire (l'or foncé ne se lisait pas).
  - Vérifié dans le navigateur : la famille, les 7 cartes, les photos, les badges, la variante.
  - ⚠️ Le QC (`_qc.py --page ina-luxury.html`) n'a pas pu tourner le 26/11 : le PC manquait de mémoire et la page
    ne chargeait pas en 30 s. À relancer seul, sans Chrome ouvert.
  - Reste : `cozy.html` ne doit plus rien vendre (A2).
**Mongazi a validé le 26/11** (« continue et finalise ») en précisant : **les TROIS univers restent, et chacun a sa
propre expérience 3D immersive et interactive** (une visite de salon, l'exposition des produits).

- [x] A2 · `harmonisation-faciale.html` (26/11), l'ex-Cozy :
  - **les données** : un bloc JSON `harmo-donnees` dans la page, seule source des 3 techniques et des 12 tarifs
    (textes et prix de ses flyers mot pour mot, la fourchette 2 100 000 à 2 400 000 F gardée en `pMin`/`pMax`, jamais
    aplatie). `python _outils/_harmo.py` en tire le tableau visible (lisible sans JavaScript) et le JSON-LD (12 `Offer`) ;
  - **la consultation** : un dialogue avec « J'ai lu et compris » obligatoire, puis WhatsApp pré-rempli au numéro de la
    maison ;
  - **le site entier suit** (`python _outils/_cozy_vers_harmo.py`, idempotent) :
    - le hub : la carte, les balises et les filtres d'avis ;
    - le menu « Catalogue » des trois pages ;
    - la recherche commune : Cozy ne s'y charge plus ;
    - le sitemap ;
    - `cozy.html` devient une redirection vers `ina-luxury.html#intime-bien-etre`, doublée dans `_redirects`. La
      page d'origine reste récupérable dans git (commit `a72f21e`).
  - Images faites avec SES flyers (`_outils/_images_harmo.py`) : `hub-harmonisation.webp`, `og-harmonisation.jpg`.
- [x] A3 · `_llms.py` lit aussi l'harmonisation : `llms.txt` et `tarifs.md` portent les 12 tarifs.
- [x] B · **LES TROIS UNIVERS EN 3D** (26/11), socle commun `assets/js/salon3d/` :
  - **le moteur** (three r180 en local, aucune autre bibliothèque) : rendu natif jusqu'à 3x, plancher 2x, ombres puis
    netteté baissées seulement si l'appareil peine, rendu suspendu hors écran et quand rien ne bouge ;
  - **les matières** (terrazzo, marbre, chêne, plâtre, plaques de laiton gravées) sont dessinées en code ;
  - **le son** : bruitages Web Audio ; aucune seconde musique là où la maison a déjà la sienne (bouton `#lcMute`) ;
  - **les trois mondes** :
    - **la clinique** (`#visite`) : 14 stations, de la porte en verre à l'accueil (comptoir en demi-lune, lattes de
      chêne, enseigne LS rétroéclairée), le couloir des 5 soins visage qu'on longe (une porte et une plaque de
      laiton par soin, prix LUS dans `SERVICES`), la cabine (la lampe descend, la vapeur, les 8 étapes du Classic
      qui s'allument), le corps, les cheveux, le VIP, l'étagère INA (les vraies photos LUES dans la page INA), la
      porte dorée du cabinet privé et le carnet de rendez-vous. « Réserver » appelle `startBooking`, avec son
      règlement et sa case.
    - **INA Luxury** (`#boutique`) : une galerie d'arches d'or en tunnel, une vitrine par famille (6), et dans chacune
      un carrousel 3D des vraies photos (meilleures ventes d'abord). Toucher un produit ouvre sa carte dans le
      catalogue ; le comptoir du fond mène au panier et à la consultation.
    - **le cabinet privé** : ses trois flyers dans des cadres dorés. On touche une zone : elle s'allume SUR SON
      VISUEL, la caméra s'approche, et la fiche donne la zone et le tarif. Un profil au fil d'or se trace à l'entrée.
  - `python _outils/_salon3d_poser.py --version <v>` pose la visite dans la clinique et dans INA, avec une passerelle
    vers leurs moteurs. **Bumper la version à chaque modification du socle.**
  - ⚠️ **PIÈGES qui ont mordu** :
    - une apostrophe écrite dans une chaîne JavaScript (« d'INA ») a cassé tout le script de la clinique →
      `python _outils/_syntaxe.py` compile chaque script de chaque page ;
    - une règle CSS posée AVANT celle qu'elle corrige ne sert à rien (encore) ;
    - les pages donnent une marge à toutes leurs sections ;
    - l'en-tête collant décale la scène : `--s3d-haut` et `--s3d-bas` la calent entre les barres ;
    - le biseau de `boiteArrondie` épaissit les plateaux de 3 cm ;
    - Chrome refuse les modules JavaScript en `file://` : le QC sert maintenant les pages en HTTP ;
    - un rendu 3D continu, en logiciel, empêchait le QC de finir : on ne redessine en continu que là où quelque
      chose bouge.
- [x] C · **EN LIGNE le 26/11** (déploiement `d9ae0bd1`, 178 fichiers, 10,7 Mo), vérifié sur luxuryclub229.com en
      LISANT le corps des fichiers, adresses nues comprises.
  - **QC vert partout, une largeur par passage** (le PC n'en supporte qu'une à la fois) :
    - clinique : 90 + 90 contrôles ;
    - INA : 18 + 18 ;
    - harmonisation : 18 + 18 ;
    - hub : 15 + 14.
  - Après le QC, seuls les cadrages des caméras au téléphone et la matière des pages du carnet ont changé ; deux
    planches en ont été tirées et regardées.
  - Commandes :
    - `python _outils/_qc.py --page <page> --largeur 390|1440` ;
    - `python _outils/_vues_3d.py [--largeur 1440]` : la planche des stations, à REGARDER, dans `_vues/` ;
    - `python _outils/_syntaxe.py`.
  - Rappels :
    - **`_dist.py` n'envoie plus aucune note `.md`**, sauf `tarifs.md` ;
    - ⚠️ **les modules 3D sont mis en cache une heure**, sans `?v=` dans leurs imports : une correction met jusqu'à
      une heure à se voir. Bumper `--version` dans `_salon3d_poser.py` ne rafraîchit que les fichiers de démarrage.

## 3 bis. Le 26/11 au matin : ses retours, et le site mis en MAINTENANCE
- ⛔ **luxuryclub229.com EN MAINTENANCE** (Mongazi : « je ne veux pas qu'elle voie les modifications là-bas »).
  - Toutes les adresses répondent 503 (`_maintenance/_worker.js`).
  - **Verrou** : `_dist.py` refuse la production tant que `MAINTENANCE.md` existe.
  - L'aperçu : https://apercu.luxury-club-229.pages.dev (`_dist.py --apercu`, puis `--branch apercu`).
  - Tout est dans `MAINTENANCE.md`.
- **Le Menu** (ses vocaux : « à côté de l'accueil, l'icône de menu, Menu » ; « catalogue, les gens ne comprennent
  pas » ; « une petite notification : Retrouvez ici notre menu »), dans `assets/js/menu.js` et `_outils/_menu_poser.py` :
  - un bouton « ☰ Menu » à côté d'« Accueil » sur les 4 pages ;
  - le tiroir de la barre du bas renommé « Menu », avec en tête « Sur cette page » (les étapes de la visite 3D en un
    toucher, les rayons d'INA, les raccourcis) ;
  - « Catalogue » et « Tout le catalogue » sont devenus « Menu » ;
  - la bulle « Retrouvez ici notre menu », une fois par page et par visite.
- **« Nos résultats »** (`_outils/_nos_resultats.py`) :
  - la galerie photo du hub devient « Nos résultats · Nos patientes » ;
  - la zone des avis écrits est retirée (elle était vide), et le bouton flottant devient « Nos résultats » ;
  - un témoignage peut être une PAIRE `{avant, apres}`, avec un comparateur à faire glisser ;
  - sans photo, la section mène à son Instagram.
  - ⏳ **SES PHOTOS AVANT / APRÈS** (elle les envoie) : à poser dans `TESTIMONIALS` (index.html), fichiers dans
    `assets/images/temoignages/`.
- **Les soins** (`_outils/_soins_2611.py`, ses textes mot pour mot) :
  - ajoutés : Cosmelan Peel 950 000 F, Melan 2 Peel 999 000 F, Perfect Derma Peel 200 000 F ;
  - retirés : le Luxury Massage et le Soin Complet VIP ;
  - renommé : « Soin Activateur de Pousse » devient « Mésothérapie ANAGEN » ;
  - la FAQ suit (« de 15 000 à 999 000 FCFA ») ; le JSON-LD, `llms.txt` et `tarifs.md` sont régénérés : 12 soins.
  - 3D : les 8 soins visage se partagent les deux murs du couloir, et l'étape VIP n'existe plus.
- **Les produits INA sur fond noir** (sa remarque sur l'étagère : « plus esthétique ») :
  - `_outils/_detourer_ina.py` (rembg/isnet) a détouré les 56 produits, contrôlés sur magenta ; la Crème au Lait
    de Chèvre est écartée (sa photo coupe le pot) ;
  - ils sont posés sur les tablettes de la clinique et debout sur les socles de la boutique, toujours de face.
- QC vert (une largeur à la fois) : clinique 90 + 90, INA 18 + 18, harmonisation 18 + 18, hub 15 + 14.
  - La sonde des recouvrements est corrigée : un tiroir fermé, hors de l'écran, ne recouvre rien.

- **INA, 22 produits retirés** (liste de Mme Sabrina, 26/11), par `_outils/_ina_retirer_2611.py` :
  - **56 → 34 produits**, photos et détourages compris ;
  - routines : Éclat / Pigmentation et Boosters n'ont plus de produit, donc disparaissent ; Acné ne garde que
    l'Acné Control Crème. ⏳ **à faire revoir par Sabrina** ;
  - 7 sous-catégories vidées : les masques visage, le gel lavant enfant, 4 rubriques capillaires, l'exfoliant lèvres ;
  - les descriptions des familles Visage, Capillaires et Soin Lèvres sont ajustées ;
  - le bloc INA du menu du hub et de la clinique est désormais RÉGÉNÉRÉ depuis les données (il était recopié, et
    en retard) ;
  - le Lip Kit nomme encore le Lactic Lip Scrub dans son rituel : c'est le contenu du coffret, laissé tel quel.
- **Mésothérapie amincissante**, 4e technique du cabinet (son flyer, oublié de la grille), par
  `_outils/_harmo_meso_2611.py` :
  - zones : double menton, joues, combo ;
  - prix à la SÉANCE + **forfait 4 séances** (ancien prix barré), dans une case neuve `forfait` ;
  - 4 cadres sur l'arc 3D ;
  - tableau, JSON-LD (une offre de plus par forfait), `llms.txt`, `tarifs.md`, menus, hub et image de partage
    (4 flyers) suivent.
- QC vert sur les 4 pages, aux deux largeurs. Aperçu `be619b9b`. La production reste en maintenance.
- **Le verre dépoli** (Mongazi : « ajoute du glassmorphism ») :
  - les fiches de la visite, les étiquettes, les pastilles, le bouton son et les enseignes des portes ;
  - un voile, un flou de 22 px, un reflet en haut et un liseré : crème pour la clinique, fumé et or pour INA et le
    cabinet ; voile plus dense au téléphone ;
  - sans `backdrop-filter`, le voile redevient plein ;
  - les points ne pulsent plus que trois fois (rien d'infini sous un verre).
- **L'hôtesse qui vient saluer** (« comme les autres »), par `assets/js/invite.js` et `_outils/_invite_poser.py` :
  - un portrait DESSINÉ par le dessinateur commun des aperçus (`_outils/avatar.mjs`) : peau ouest-africaine,
    tunique menthe, foulard d'or ;
  - elle vient à la fin de la visite 3D, ou au plus tard à 18 s, une fois par visite, jamais par-dessus la porte,
    l'accueil, le menu ou une réservation ;
  - « Oui » mène à l'aide de chaque univers : un conseil sur WhatsApp (clinique), « Faire ma consultation » (INA),
    la demande de consultation (harmonisation) ;
  - le QC la tient à l'écart de sa mesure (message passager) ; elle se vérifie en photographies.
- **LE MENU MÈNE AU SITE NORMAL** (vocal de la cliente, 26/11 : « la nouvelle interface, c'est une sorte d'accueil
  pour chaque espace ; quand ils ne se retrouvent pas, ils cliquent sur Menu et ça les amène dans un espace normal ») :
  - le menu ne liste plus les étapes 3D. Il liste, au téléphone comme au PC : à INA les familles et leurs
    catégories (le catalogue classique) ; à la clinique les soins par famille (leur carte dans la liste) ; à
    l'harmonisation les techniques (la liste écrite) ;
  - au-delà de 2,5 écrans il SAUTE au lieu de glisser (on ne traverse pas toute la 3D), et il s'arrête sous les
    barres collantes (`scroll-margin-top`) ;
  - la 3D se met en pause tant que le menu est ouvert ;
  - ⚠️ **défaut d'INA trouvé et corrigé** : chaque rayon touché remontait la page à 0, donc DANS la boutique 3D posée
    au-dessus ; il remonte maintenant au début du catalogue.
- **L'harmonisation en liste écrite** : la section des techniques n'a plus de flyers (ils restent dans le cabinet 3D).
- **LA MUSIQUE DE SPA** (Mongazi : « un son apaisant, relaxant, qui donne l'impression d'être dans un spa », choisie
  sur Pixabay dans Chrome), par `_outils/_musique_poser.py` :
  - la piste : « Spa » de leberch (Pixabay, 4:56) → `assets/audio/luxury-spa.mp3`, -12,3 LUFS, 96 kb/s, fondus de
    boucle ;
  - ⚠️ elle est **Content ID Registered**, comme les 12 pistes de spa vérifiées : sans effet sur un site, mais une
    vidéo du site publiée sur YouTube ou Facebook peut être réclamée ;
  - elle REMPLACE l'ambiance synthétisée (musicStart/musicStop de la maison la jouent ; le bouton de la barre du bas
    la commande) et l'ancienne piste de l'harmonisation, retirée.
- **LES BRUITAGES** (« au toucher, au mouvement, tout ») :
  - une goutte d'eau au toucher dans la scène ;
  - un souffle d'air qui suit la vitesse de la caméra ;
  - un bol chantant à chaque étape ;
  - une note de verre au survol d'un objet qu'on peut toucher ;
  - un souffle à l'ouverture du menu ;
  - tout se tait avec le son.
- QC vert sur les 4 pages, aux deux largeurs. Aperçu publié ; la production reste en maintenance.
- ✅ **LA MUSIQUE** (Mongazi, /vague du 26/11), livrée le 26/11 (ci-dessus) : remplacer l'ambiance actuelle par une musique de relaxation, **une fois
  toutes les modifications finies**. Zone travaux, rang 7. L'ambiance actuelle est synthétisée en Web Audio
  (bouton `#lcMute`, sur le hub, la clinique et INA) ; la page d'harmonisation joue `assets/audio/luxury-ambiance.mp3`.
  Il faut REMPLACER (jamais deux musiques à la fois), avec une seule piste pour les 4 pages, à -12 LUFS, et proposer 2
  ou 3 pistes à Mongazi avant de poser.

## 3 ter. Le 26/11 au soir : la 4K et la fluidité
Deux demandes de Mongazi : « la vitrine en 4K » et « le plus fluide possible ». Tout est dans
`assets/js/salon3d/moteur.js` ; `window.S3D` dit dans la console ce que le moteur rend vraiment (définition, images
par seconde, carte graphique, temps de compilation).
- **La définition** : jamais sous 2x, même sur un écran de PC ordinaire, donc un écran 1920 est rendu en 3840 px.
  Le plafond est le natif de l'écran (jusqu'à 3x) ET un budget de 3840 × 2160 pixels.
- **Une carte graphique faible** (Intel HD/UHD intégrée, Mali, PowerVR, petit Adreno : la plupart des portables et
  des téléphones de Cotonou) démarre à la netteté native, avec l'anticrénelage. Mesuré ici : une Intel HD 5500 tient
  40 images/s en 2x quand la caméra bouge. Une carte forte démarre en 4K.
- **La fluidité d'abord** : 60 images/s visées, sans plafond (un écran 120 Hz en reçoit 120). Sous 55, on coupe la
  poussière et les rais, puis on descend vers 2x, puis jusqu'au natif, jamais en dessous. Une définition baissée ne
  remonte pas sur un écran 60 Hz (chaque aller-retour est un à-coup).
- **Les ombres sont figées** : aucun objet qui en porte ne bouge, donc elles se calculent au départ et à chaque
  étape, jamais à chaque image. ⚠️ **Couper les ombres recompilait toutes les matières et gelait la 3D** : la qualité
  basse les garde.
- **Plus de gel au démarrage** : les matières se compilent en parallèle (`compileAsync`), les textures partent vers
  la carte graphique une par image, et chaque photo est décodée hors du fil principal (`ImageBitmapLoader`, sauf
  Safari).
- **Les matières** posées d'un seul tenant sont dessinées en double définition sur grand rendu (un sol qui se répète
  6 à 14 fois, non : doubler ses 16 millions de pixels gelait le démarrage 2,5 s).
- **Les produits d'INA en 2x sur grand rendu** : `_outils/_agrandir_detoures.py` (Real-ESRGAN x4plus sur le
  processeur, qui affine la vraie photo sans rien inventer ; la transparence suit en Lanczos). Le moteur ne demande
  que les produits de `2x/liste.json` ; le téléphone garde les originaux.
  - ⚠️ Le PC a tué l'agrandisseur en pleine écriture : `bonbon-scrub.webp` faisait 0 octet et figurait dans la liste.
    Il écrit maintenant à côté puis renomme, et un fichier vide ne compte plus.
  - Environ 2 à 3 minutes par produit sur ce PC, 33 produits : il se relance et reprend où il s'est arrêté.
- **Le verre dépoli allégé** : flou 22 → 16 px (12 px au téléphone). Une étiquette cachée passe en `visibility:hidden`,
  pour que son flou ne se calcule plus.
- **La page** (bloc `<!--FLUIDE-->` en fin des 4 pages) : l'égaliseur du bouton son anime `transform` au lieu de
  `height`, et les pulsations (`box-shadow`, 34 boutons sur INA) battent trois fois puis s'arrêtent.
- **Le cache** : les modules 3D s'importent entre eux sans `?v=`. Ils sont donc en `no-cache` dans `_headers` (un
  fichier inchangé répond 304), et le `?v=` du démarrage et de la feuille passe à `20261126u`.
  ⚠️ `_salon3d_poser.py` a pour version par défaut `20261126a` : toujours lui passer `--version`.
- QC vert sur les 4 pages aux deux largeurs : clinique 90 + 90, INA 18 + 18, harmonisation 18 + 18, hub 15 + 14.
- ⛔ **`assets/docs/gloria-infos.md` partait en ligne** (la fiche de collecte de la cliente, depuis mai), comme le README
  des témoignages : `_dist.py` n'excluait les `.md` qu'à la racine. Il les exclut maintenant à tout niveau (seul
  `tarifs.md` part) et le vérifie. ⚠️ Les anciens déploiements de Pages la servent encore par leur adresse à numéro
  (`<numéro>.luxury-club-229.pages.dev`) : rien de secret dedans (le catalogue et les prix du site), mais les supprimer
  est une décision de Mongazi.
- Aperçu publié le 26/11 au soir : `09125167` (https://apercu.luxury-club-229.pages.dev), vérifié en lisant le corps
  des fichiers servis. La production reste en maintenance (503).

## 3 quater. « Le travail doit valoir 10 000 $ » (Mongazi, 26/11 au soir) : par vagues
Méthode : tout photographier d'abord, au téléphone et au PC, chaque étape des visites et chaque écran des pages
(script d'audit, planches réduites), juger comme un client exigeant, puis corriger par vagues de trois au plus.

### Vague 1 · ce qui gênait le visiteur (faite)
- ⛔ **L'hôtesse recouvrait la visite** : à 18 s elle se posait sur la fiche de chaque soin (au téléphone, un quart de
  l'écran, de l'étape 1 à l'étape 10). Elle ne vient plus jamais pendant la visite : seulement quand la visite est
  derrière le visiteur, ou après 18 s passées hors d'elle (`assets/js/invite.js`).
- **Les étiquettes des points** étaient coupées au bord (« Le protoco… »). Elles se posent maintenant là où il y a
  de la place : à droite du point, à gauche s'il déborde, sinon sous le point. Les points de l'étape sont des
  obstacles : à l'accueil, « Sur rendez-vous » ne se pose plus sur « Lundi au samedi » (`moteur.js`, en deux passes).
- **Au téléphone, les fiches d'INA et du cabinet cachaient les produits** : les sous-catégories et les zones tiennent
  sur une ligne qu'on fait glisser, la description sur deux lignes, et la caméra d'INA s'approche et vise plus bas.
  Les produits sont grands, au-dessus de la fiche.
- **INA : une bande de texte coupé sous l'en-tête** : la sous-navigation était collée à 60 px sous un en-tête de 80.
  Elle se cale sur l'en-tête MESURÉ, et la visite passe par-dessus elle (« Menu » est déjà dans l'en-tête) : la 3D
  gagne 50 px (`<!--ENTETE-->` en fin de `ina-luxury.html`).
- Le cabinet : la dernière étape se numérotait « 04 » après « 04 / 04 » ; elle suit maintenant le nombre de techniques.
- QC vert : clinique 90 + 90, INA 18 + 18, harmonisation 18 + 18, hub 14 + 15.

### Vague 2 · les 8 soins du visage (faite)
Avant : huit fois le même couloir, un grand panneau de bois vide et une plaque de prix illisible.
- **Un caisson lumineux par soin**, à côté de sa porte (`caisson()` dans `matieres.js`) : rétroéclairé, double filet
  d'or, SON croquis (le même que sa carte dans la page), son nom, son prix, sa durée. Cadre d'or satiné (le laiton
  poli reflétait le décor et virait au brun-noir), halo sur le mur.
- Les croquis et les polices sont chargés AVANT d'être dessinés dans la toile, sinon on obtient une police de secours
  et un caisson sans dessin. La passerelle `window.LC_CLINIC` transmet `art` et `artFamille` (et
  `_salon3d_poser.py` aussi).
- **Trois croquis neufs** : Cosmelan (les taches qui pâlissent), Melan 2 (deux temps, deux gouttes) et Perfect Derma
  (les couches de la peau, la plus haute qui se renouvelle). Ils retombaient sur le croquis générique « visage », dans
  la page comme dans la 3D.
- Caméras : au PC, de biais et proche (le caisson en grand à droite, la fiche à gauche) ; au téléphone, droit devant
  et visé plus bas (le caisson dans le haut de l'écran, au-dessus de la fiche). Le point « Le protocole » passe sous
  le caisson (près de la porte, il tombait derrière la fiche).
- ⚠️ **`node --check` ne voit pas une variable déclarée deux fois dans un module** (`halo`) : la visite ne démarrait
  plus, sans aucune erreur visible dans le QC. Vérifier avec `node --input-type=module --check < fichier.js`.
- QC clinique vert : 90 + 90.

### Vague 3 · la lumière (faite, première passe)
Vu en grand au PC, trois matières faisaient bon marché : un plafond de béton gris taché (un tiers de l'écran), des murs
marbrés de taches, un terrazzo aux éclats trop contrastés. Et une lumière plate.
- **Plafond blanc chaud et lisse** ; **murs à la chaux** (`platre()` prend un réglage `taches`, 1 = d'origine) ;
  **terrazzo fin** (éclats proches du fond, 1 700 au lieu de 2 600).
- **Le vignettage** : les bords de l'image s'assombrissent à peine (`.s3d-scene::after`, `--s3d-vignette`, plus fort sur
  les fonds sombres d'INA et du cabinet). Un dégradé FIXE, sans mélange ni flou, que la carte graphique compose sans
  rien recalculer. Les points et les fiches passent au-dessus (`z-index:2`).
- QC vert : clinique 90 + 90, INA 18 + 18, harmonisation 18 + 18.
- ⏳ **Ce qui irait plus loin** (à mesurer sur un vrai téléphone avant) : un éclairage précalculé, des reflets au sol,
  une profondeur de champ. Chacun coûte des images par seconde sur les cartes graphiques faibles de Cotonou.

### Vague 4 · la boutique INA : détourages et étalage (Mongazi, photos de son écran : « de mauvais détourages, très mauvais »)
Ce que montraient ses photos : un « rectangle de bruit » (le Lip Kit), un pot sur fond blanc carré, des produits
géants qui se chevauchaient, passaient par la tranche en tournant, et des blancs brûlés en rectangles vides.
- **Les détourages** (`_outils/_detours_affiner.py`, à lancer après `_detourer_ina.py`) : repartir de la PHOTO
  D'ORIGINE, garder le produit (pas les débris), BOUCHER LES TROUS (un flacon est plein), rendre l'intérieur opaque,
  rogner le bord d'un pixel et le recolorer avec la couleur du produit (fini le liseré blanc sur le noir).
  - ⛔ **Le Lip Kit était troué à 18 %** : ses lèvres blanches et roses avaient été prises pour du fond, et la 3D
    montrait le noir à travers. Bouché avec ses vraies couleurs.
  - **Une boîte est convexe** (`CONVEXE`, Lip Kit) : là où l'imprimé clair touche le fond blanc de la photo, aucun
    modèle ne les sépare ; la silhouette est complétée par son enveloppe convexe, limitée à la hauteur de la boîte
    (le ruban n'est pas touché).
  - Contrôlés un par un sur magenta ET sur noir. Les 32 autres n'avaient pas de trou.
- **L'étalage** (`monde-ina.js`) : fini le carrousel de douze produits de 90 cm. Deux gradins (une marche de marbre
  filetée d'or) : les grands flacons derrière, les pots et les petits devant ; une hauteur selon le type (pots et
  boîtes bas, sérums moyens, flacons hauts) ; un espacement calculé, sans chevauchement ; une ombre de contact sous
  chacun ; une teinte chaude (les blancs ne brûlent plus). Jusqu'à trois produits : une rangée, sur la marche, plus
  grande. Rien ne tourne : la 3D se repose quand rien ne bouge.
- Seuls les produits DÉTOURÉS montent sur l'étalage : la Crème au Lait de Chèvre (photo coupée) reste au catalogue.
- Les détourages portent un `?v=` (manifeste, `boot-ina.js`, l'étagère de la clinique) : le cache d'une heure aurait
  montré l'ancien Lip Kit. Les agrandis 2x faits sur les anciens détourages sont supprimés et refaits.
- QC vert : INA 18 + 18, clinique 90 + 90.

### Vague 5 · les sons, le menu, le volume (27/11, Mongazi : « enlève ce bruitage générique bizarre », « des sons ultra relaxants », « le menu moins généré par IA, beaucoup plus profond », « plus de profondeur au niveau des produits, avec du volume »)
- **Les sons** : tous les bruitages synthétisés sont retirés (la sirène du menu, le bip carré des filtres, l'accord
  électronique du panier, le « vent » qui suivait le défilement). Dix vrais enregistrements de spa, trouvés sur
  Pixabay depuis Chrome (Cloudflare refuse les accès automatiques ; le fichier se télécharge ensuite du CDN), choisis à
  la MESURE (graves, sans aigus durs, bruit de fond bas) : bol tibétain, goutte d'eau, carillon à vent, harpe en
  glissando, note de kalimba, cloche de méditation, eau qu'on verse, deux notes douces. Coupés, fondus, mis au même
  volume (`assets/audio/sfx/`, 240 Ko). Un seul lecteur pour les quatre pages (`assets/js/sons.js`, `LCSons.jouer`),
  posé par `_outils/_sons_poser.py` (qui remplace aussi les `var SFX` des pages). Le bol ne sonne qu'une fois toutes
  les 1,5 s (en défilant vite, ils s'empilaient).
- **Le menu** (`assets/js/menu.js`, réécrit) : le tiroir de texte devient LA CARTE, plein écran. Un grand titre
  éditorial par univers ; INA : chaque famille en carte avec SES vrais produits détourés en éventail, qui débordent de
  la carte ; la clinique : une carte de spa (croquis, nom, durée, points de conduite, prix) ; le cabinet : ses flyers
  inclinés ; les quatre univers (monogrammes dessinés, vrai pot INA, flyer) et WhatsApp ; l'entrée en perspective,
  bloc après bloc ; le monogramme LC en filigrane, qui remonte moins vite. ⛔ Aucune image générée par IA dans le menu
  (les « ambiances » de l'accueil le sont : écartées). Le prix ne se coupe plus en deux lignes (espaces insécables).
- **Le volume des produits** (`monde-ina.js`, `volume()`) : flacons, tubes et pots sont des cylindres où la photo
  s'enroule (u = ½ + ½ sin θ : vue de face, c'est exactement la photo), une lumière posée dans les couleurs des
  sommets (bords à l'ombre, reflet vertical comme sur du verre). La DEMI-face avant seulement : un dos qui reprenait la
  découpe faisait un goulot en double, vu de biais. Les « Beauty Bar » et le Lip Kit (des boîtes photographiées de
  trois quarts) gardent leur photo sur une plaque d'épaisseur. Les produits ne se tournent plus qu'aux deux tiers vers
  le visiteur : on voit leur rondeur quand la caméra bouge.
- Le fondu de la musique pouvait calculer un volume négatif (une exception dans la page) : borné.
- QC vert sur les 4 pages, aux deux largeurs.

### Vague 6 · toutes les étapes à portée de doigt au téléphone (27/11, Mongazi, capture de son iPhone : « que le client puisse avoir accès à tous les points directement, comme sur PC, sinon il risque de se perdre et perdre du temps »)
- Au PC, une colonne de pastilles au bord mène à chaque étape ; au téléphone elle recouvrait la fiche et avait été
  CACHÉE : il fallait tout faire défiler. Ce sont maintenant les mêmes pastilles en **bandeau** en haut de la scène
  (numéro + nom de l'étape, on le fait glisser, un toucher y mène), l'étape en cours dorée et centrée (le moteur fait
  défiler le bandeau seul, jamais la page). Sans flou (une scène qui bouge le ferait recalculer à chaque image).
- **Un seul numéro par étape** : le bandeau, le caisson et la fiche disaient 04, 02 et 03 pour le même soin. Tout prend
  le numéro de l'étape (00 = l'entrée).
- La caméra du téléphone recule un peu devant les caissons : le bandeau ne mord plus leur haut.
- ⛔ **L'hôtesse restait affichée quand on remontait dans la visite** (sa capture : elle couvrait l'étape 12). Elle
  s'efface dès que la visite remplit de nouveau l'écran.
- ⏳ Au cabinet, le bouton « Son » passe sous le bandeau, sur le haut du flyer : à revoir.
- QC vert : clinique 90 + 90, INA 18 + 18, harmonisation 18 + 18.

### Vague 7 · une ambiance réelle par niveau, qui part comme sur la vitrine NEBULA (27/11, Mongazi : « enlève cette musique générique IA pour un son relaxant, le son artificiel basique est toujours présent », puis « 4 sons ultra relaxants, un pour chaque niveau, qui se déclenchent comme sur la vitrine de NEBULA »)
- Vérifié dans le navigateur : les anciennes notes de synthèse (`Audio`, `Ambiance`, `#audio-btn`) ne jouaient plus ;
  ce qu'on entendait partout, c'était la piste « Spa » du 26/11, une nappe de synthèse. Elle est RETIRÉE.
- Quatre ENREGISTREMENTS réels (Pixabay), choisis à la mesure (niveau stable, graves, peu d'aigus), mis en boucle sans
  couture (la fin se fond dans le début) et à -15 LUFS, posés par `_outils/_musique_poser.py` (réécrit) :
  accueil = ruisseau de forêt et oiseaux · clinique = bols de cristal + fontaine zen · boutique INA = fontaine en bois +
  bols himalayens · cabinet = bols de méditation frappés.
- ⛔ **Le démarrage ratait au téléphone** : au premier geste, si c'était un défilement ou un premier toucher (refusés
  par l'iPhone), le code abandonnait et la musique ne venait jamais. Comme sur la vitrine NEBULA, on réessaie
  maintenant à chaque geste jusqu'à ce qu'elle joue (pages ET `son.js` du cabinet), jamais si le visiteur l'a coupée.
  Testé : défilement → muette, toucher → la bonne ambiance sur les quatre pages.
- QC vert sur les 4 pages, aux deux largeurs.

## 4. Les règles du site qui restent vraies (voir `CONTEXT.md`)
Publier par `_dist` · contraste mesuré sur les pixels rendus · aucun visage ni soin inventé dans une image GÉNÉRÉE par
nous (les flyers sont ses supports à elle : leurs visuels sont les siens, demandés par elle) · `llms.txt` à relancer après
tout changement de tarif · horaires lundi-samedi 10h-17h · numéro de la maison inchangé.
