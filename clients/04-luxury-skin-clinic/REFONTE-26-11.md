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
- ⏳ **LA MUSIQUE** (Mongazi, /vague du 26/11) : remplacer l'ambiance actuelle par une musique de relaxation, **une fois
  toutes les modifications finies**. Zone travaux, rang 7. L'ambiance actuelle est synthétisée en Web Audio
  (bouton `#lcMute`, sur le hub, la clinique et INA) ; la page d'harmonisation joue `assets/audio/luxury-ambiance.mp3`.
  Il faut REMPLACER (jamais deux musiques à la fois), avec une seule piste pour les 4 pages, à -12 LUFS, et proposer 2
  ou 3 pistes à Mongazi avant de poser.

## 4. Les règles du site qui restent vraies (voir `CONTEXT.md`)
Publier par `_dist` · contraste mesuré sur les pixels rendus · aucun visage ni soin inventé dans une image GÉNÉRÉE par
nous (les flyers sont ses supports à elle : leurs visuels sont les siens, demandés par elle) · `llms.txt` à relancer après
tout changement de tarif · horaires lundi-samedi 10h-17h · numéro de la maison inchangé.
