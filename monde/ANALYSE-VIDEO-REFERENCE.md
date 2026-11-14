# La supérette de référence, mesurée · grammaire pour le salon d'HILLARY M. STYL

> **Ce fichier** : l'analyse complète de la vidéo de référence
> `_partage/immersive  store 3D/ScreenRecording_11-12-2026 00-42-05_1.mp4`
> (101,7 s, 888 × 634, 60 i/s, avec son), faite le 2026-11-12. Elle complète la
> première lecture de `VISION.md` § 2 (« La supérette, seconde par seconde ») et
> **la corrige sur plusieurs points** (§ 0).
>
> **Règle** : on en tire une **grammaire**, jamais une copie. Aucun nom, aucun
> personnage, aucune marque, aucun visuel du jeu ne passe dans le salon. Les
> noms des personnages du jeu n'apparaissent ici que pour décrire la référence.

## En bref

- Ce qui fait la sensation n'est **presque jamais un effet graphique** : c'est
  une caméra à hauteur juste qui marche juste, des personnages qui **parlent en
  faisant quelque chose**, une interface **presque absente**, un fond sonore
  continu sans musique, et un rythme serré (une réplique toutes les 2,5 s).
- Mesures clés : caméra à **≈ 1,50 m** (15 à 20 cm sous les yeux des PNJ),
  champ de vision **≈ 75° en horizontal, ≈ 46° en vertical** (mesuré),
  balancement de marche **à la cadence des pas, 2,1 à 2,3 Hz, ≈ 1° crête à
  crête**, caméra **parfaitement immobile** quand le joueur ne bouge pas.
- Dix procédés donnent l'essentiel de l'immersion pour presque rien (§ 10) ; le
  salon en fait déjà une partie, et **trois réglages actuels vont à l'encontre
  de la référence** (cadence de marche, focale en paysage, dialogue « touchez
  pour continuer »).

---

## 0. Ce que cette analyse corrige dans la première lecture

| Première lecture (`VISION.md`) | Ce que montrent les mesures |
|---|---|
| « La zone de jeu occupe environ les 330 premiers pixels » | **Elle occupe les 490 premiers pixels** (lignes 0 à 489 ; les lignes 490 à 493 sont la barre de progression de la plateforme, le noir commence à 494). Les planches rognées à 330 px **coupaient le tiers bas de l'image** : les sous-titres, la carte de titre de mission et la barre-minuteur des choix n'y figuraient pas. |
| « Le nom flotte au-dessus de lui » | Le nom est **petit, bleu-vert, posé à hauteur du torse ou des mains**, pas au-dessus de la tête. Il n'existe que sur les coéquipiers, jamais sur les civils, et il est absent pendant les 16 premières secondes. |
| « 70-76 s : à la caisse, invite PAYER, tes mains sur le terminal, écran paiement terminé avec QR » | L'invite « PAY » apparaît à **74,6 s** et **attend 15 s** : le joueur ne paie qu'à **89,6 s**. Sa main entre avec **un téléphone** (90,2 s), le terminal affiche « paiement effectué » et un QR à **91,2 s**, la main repart à 91,8 s. Entre les deux, toute la scène de la télévision se joue. |
| (absent) | Une **carte de titre de mission** s'affiche en bas à gauche de **10,3 à 16,0 s**, révélée en « décodage ». |
| (absent) | Deux **fondus au noir** coupent les trajets : **16,6 à 17,4 s** et **73,6 à 74,5 s**. |
| (absent) | Les choix ont un **minuteur** : une barre qui se vide en ≈ 5 s. |
| Transcription Whisper « Ding-ding, one, two… » (37-41 s) | Ce n'est pas une réplique : ce sont des **murmures de voix d'hommes non sous-titrés**, ≈ 10 dB sous les répliques (fondamentale 270 à 330 Hz). Le moteur a inventé des mots sur un brouhaha. |
| Le joueur, un visiteur | Le joueur est **un soldat du pays** (son nom apparaît sous ses propres répliques). **L'étranger, c'est le guide** (un caporal américain) : c'est lui qui pose les questions naïves et qui fait rire. |

---

## 1. Méthode (reproductible, sans navigateur)

1. **Trouver la vraie zone de jeu** en mesurant la luminosité ligne par ligne
   d'une image pleine (Python + PIL) : le noir franc commence à la ligne 494.
2. **Une image par seconde, rognée sur la zone de jeu**, puis planches de 6
   étiquetées en Python (le filtre `drawtext` fait planter ffmpeg sur ce PC) :
   ```bash
   ffmpeg -i ref.mp4 -vf "fps=1,crop=888:490:0:0" -q:v 3 s_%03d.jpg
   ```
3. **Bandes de sous-titres en pleine résolution** (une par seconde, `crop`
   x 290, y 372, 560 × 100, agrandies 1,4 fois) : on lit chaque réplique, son
   locuteur, sa couleur, sa durée à l'écran.
4. **Images serrées (0,1 à 0,4 s) aux moments d'interface** : ouverture, carte
   de titre, deux choix, invite « PAY », paiement, sortie.
5. **Le mouvement de la caméra** par corrélation de phase entre images
   successives (30 i/s, haut de l'image seulement, sous-pixel) : lacet,
   tangage, balancement de marche, immobilité.
6. **Le champ de vision** par la perspective d'une rotation pure : pendant un
   lacet, un point situé à l'angle *a* du centre glisse 1/cos²(*a*) fois plus
   vite qu'au centre. Le rapport bord/centre (1,32 des deux côtés, 186 paires
   d'images retenues sur cinq rotations) donne une focale de ≈ 570 px sur 888.
7. **Le son** : niveaux par seconde, plancher de bruit (10e centile des
   fenêtres de 10 ms), répartition en 5 bandes, largeur stéréo (côtés contre
   centre), pics tonals sur les passages calmes, recherche d'une pulsation
   musicale par autocorrélation.

---

## 2. Le déroulé, seconde par seconde

Les répliques sont traduites (l'original est en anglais ; entre crochets dans
le jeu = traduit du coréen).

| Temps (s) | Ce qu'on voit | Ce qu'on lit / entend | Caméra |
|---|---|---|---|
| 0,0-1,7 | **Bandes noires** (≈ 11 % en haut et en bas, format ≈ 2,35:1). Dos d'un soldat (Cho, lunettes de protection sur le casque). Une femme rousse traverse le premier plan (0,0-0,6). Le flou d'arrière-plan est déjà là. | Caissière [Oh non ! Dehors ! Tous !] · Cho [Pourquoi ? On est vos meilleurs clients !] | quasi fixe |
| 1,2-1,6 | Le sergent (Jae), à droite, lève la main gantée. | Jae [Hé, soldat Park.] « Ils veulent bizuter le nouveau. Prends des médicaments pour l'estomac et peut-être des ramen pour lui. » (à l'écran de 1,0 à 8,0) | |
| 1,7 | **Les bandes disparaissent d'un coup** : le joueur a la main. Le visage de Cho passe flou au premier plan. | | pointe à 35°/s vers Jae |
| 2,2-7,8 | **Jae s'avance à ≈ 0,65 m**, visage plein cadre (son casque = 26 % de la largeur), regard droit dans l'objectif, sourire. **Fond flou** (60 % de détail en moins). À droite, le bras de la caissière pointe la sortie (3 s) ; deux clients près de la caisse regardent les soldats. | | < 11°/s |
| 8,0-8,6 | Jae tourne les talons, flou de bougé. | Park (le joueur) [Oui, chef.] | 40°/s |
| 9,0-12,0 | Jae va s'excuser à la caisse. Le fond redevient net : gondoles pleines, un soldat avec un panier, deux civils qui partent (12 s). | Jae [Désolé, ça ne se reproduira pas.] · Ju Kwon [Oh, zut.] | |
| 10,3-16,0 | **Carte de titre** en bas à gauche : petite ligne « jour présent », grand titre de mission, nom et grade du joueur, écusson pâle derrière. Révélée en décodage (lettres qui se cherchent, 10,3-11,2), tenue 5,7 s. | | |
| 10,2-16,6 | **Le joueur regarde partout par coups secs** : distributeur de billets, comptoir de vitrine où **un couple mange**, **une femme accroupie** devant le rayon du bas, ventilateurs muraux, suspensions, un rayon de tout près (16 s). | Caissière [Cette odeur ne partira pas !] · Cho [Si vous n'étiez pas habillés comme une armée…] · Dunn : « Park, tu viens avec moi, frère. » (14-16) | **220 à 300°/s** par à-coups |
| 16,6-17,4 | **Fondu au noir** (luminance 130 → 53), ellipse : on se retrouve devant les frigos à boissons. | Dunn : « Pas mal, ces réflexes. » (action hors champ) | |
| 17,4-21,9 | Dunn, de dos, fouille le rayon frais, prend un paquet, le retourne. **Aucune réplique pendant 3,5 s.** Son nom apparaît à hauteur de ses mains. | murmure du magasin seul | quasi fixe |
| 22,0-24,9 | Dunn tourne la tête par-dessus l'épaule vers le joueur, **à ≈ 1,4 m**, paquet de poisson séché en main. | Dunn : « Dis, Park, tu peux me dire ce que c'est, ce truc ? » | fixe |
| 24,9-27,5 | **Choix 1**, au centre : haut « Pas de réponse », gauche « Du poisson qui sent la pisse », droite « [Mentir] Oui, des sushis ». **Barre-minuteur**, voile léger, sous-titre effacé. Dunn continue de tripoter le paquet. Choix à gauche à 27,5 s (2,6 s). | | fixe |
| 28,0-38,0 | Dunn rit, regarde le paquet, puis le joueur ; **à 36 s il pointe l'index vers la caméra**, sourire en coin, à ≈ 1,1 m. Jusqu'à **3 lignes** de sous-titres empilées (31-33). | Park : « C'est… du poisson dans de la pisse. » · Dunn : « Arrête. Sérieux ? » · « Vous mangez ça, vous ? » · « Oh, mais le nouveau va peut-être aimer, hein ? » | fixe (26-33 s : immobile) |
| 38,0-42,5 | Dunn tourne, va vers Cho qui tient **un panier violet**. Aucun sous-titre. | **murmures non sous-titrés** | suit à 46°/s |
| 42,5-46,0 | **Dunn met le paquet dans le panier de Cho**, Cho le regarde, Dunn sourit au joueur (45 s). | Dunn : « J'ajoute ça au menu. » | fixe |
| 46,0-51,0 | Dunn **marche devant** vers le coin pharmacie (croix verte) ; on le suit. | Dunn : « On devait prendre autre chose, non ? » | 29°/s, balancement 2,1-2,3 Hz |
| 52,0-54,0 | **Choix 2** : haut « Soins de la peau », gauche « Crème pour ton infection », droite « Médicaments pour l'estomac ». Le joueur prend la **mauvaise** réponse, à 54,0 s (2,0 s). | | fixe |
| 55,0-62,0 | Dunn parle **sans quitter le rayon des yeux**, tend le bras vers l'étagère haute (61), prend un flacon (62). | Park : « Ah. La crème pour ton infection ? » · Dunn : « Non, ça c'est guéri. » · « C'était autre chose… » · « Oh ! Les médicaments pour l'estomac. » | **immobile 12 s (51-63)** |
| 62,0-64,0 | Dunn **se retourne et tend le flacon** vers le joueur. | Park [Ah oui, c'est vrai.] · Dunn : « Je l'ai. » | |
| 64,0-73,6 | Dunn marche devant vers la caisse, **se retourne en marchant** (67-68, ≈ 2,5 m) pour lancer la chute. Au passage : un homme assis mange au comptoir de vitrine, **serpillière et seau jaune**, cartons au sol. | Park : « Ju Kwon va en avoir besoin. » · Dunn : « Tu l'as dit. Le pauvre va rester collé aux toilettes une semaine. » · « J'espère que quelqu'un lui a acheté des couches. » | 10 à 35°/s |
| 73,6-74,5 | **Fondu au noir** (luminance 42). | | |
| 74,5-75,4 | Au comptoir : la caissière désigne le sac et le terminal, puis **croise les bras et fixe le joueur**, tête penchée. **« ⊙ PAY »** apparaît **sur son épaule** (74,6). Le sac vert est déjà sur le comptoir. | silence de 4 s | |
| 75,8-77,9 | On tourne vers les soldats qui attendent ; le terminal affiche « posez votre carte ». | | 29°/s |
| 78,0-82,0 | La caméra **lève les yeux d'environ 35°** vers la télévision : un journal, un portrait, un bandeau (« changement à la tête… la crise militaire s'aggrave »). **Tous les soldats lèvent la tête.** | Dunn : « C'est qui ? Une star de K-pop ? » · Ju Kwon : « Le nouveau Guide suprême de la Corée du Nord. » | tangage +43°/s |
| 82,0-88,0 | La télé passe à la présentatrice. Dunn tend la main vers Ju Kwon (83). **La main de la caissière tend le sac plein par-dessus le comptoir, Cho le prend à deux mains** (84-85) et le serre contre lui (86-88), ramen au sommet. | Dunn : « Sans blague. Il a l'air plus jeune que moi. » · Jae : « Il l'est. » · Cho : « Sa sœur, c'est mon ex. » | immobile |
| 88,0-90,0 | Les soldats se tournent vers la porte. | Jae : « Remballe, Cho, on y va. » · Cho : (rit) « Bien reçu, sergent. » | |
| 89,2-91,8 | **La caméra baisse les yeux** vers le terminal ; **la main du joueur entre avec un téléphone** (90,2), le pose au-dessus (91,2 : « paiement effectué » + QR), repart (91,8). | | tangage -32°/s puis +29°/s |
| 92,0-95,0 | Dunn franchit la porte vitrée ; on le suit. | Cho : « Soldat Ju Kwon… » · Ju Kwon : « Soldat Ju Kwon. » · Cho : « Mange. » · Ju Kwon : « Oh. J'ai pas faim. » | |
| 95,0-97,5 | **Passage de la porte** : la luminance tombe à 22 (95,7-96,2), puis **remonte à 38 en 1,5 s** (l'œil s'habitue). La rue de nuit : néons roses, blancs, jaunes, violets, enseignes de restaurants, **25 à 40 passants**, étals, tabourets en plastique rouges, vapeur. | le fond sonore monte de 10 dB | |
| 97,0-101,7 | L'escouade s'enfonce dans la foule ; noms de Cho et Jae visibles. Coupe nette. | Cho : « Ça ne compte pas, soldat. Parce que tu vas tout manger. Tout de suite. » · Ju Kwon [Tout ?] | balancement 2,1 Hz |

---

## 3. La caméra

### 3.1 Hauteur des yeux : ≈ 1,50 m

Calcul sur l'image de 68 s (Dunn debout face à la caméra, couloir dans l'axe) :
ligne d'horizon à y ≈ 165 (caméra inclinée de 8° vers le bas), pieds de Dunn à
30,8° sous l'horizontale, ses yeux à 4,4° au-dessus. Avec des yeux de PNJ à
1,68 m : **caméra à 1,49 m**. Recoupé sur l'image de 12 s : même ordre.

**Conséquence** : on regarde les personnages debout **très légèrement de bas en
haut** (15 à 20 cm sous leurs yeux). Ils ont de la présence sans écraser.

### 3.2 Champ de vision : ≈ 75° horizontal, ≈ 46° vertical (mesuré)

Méthode § 1.6 : rapport de vitesse bord/centre 1,317 (gauche) et 1,324
(droite), focale 569 à 576 px sur 888, soit **75,3 à 75,9° en horizontal** et
**46,1 à 46,6° en vertical** sur l'image visible (≈ 47° pour un 16:9 entier).
Les bords s'étirent un peu (rayons de 16 s, main tendue de 36 s), sans
déformation gênante.

### 3.3 Balancement de marche

| Passage | Vertical crête à crête | Fréquence verticale | Latéral (écart-type) | Fréquence latérale |
|---|---|---|---|---|
| 64-68,6 s (vers la caisse) | 7 px | **2,31 Hz** | 2,6 px | **1,15 Hz** |
| 96,6-101,4 s (rue) | 11 px | **2,14 Hz** | 2,6 px | **1,07 Hz** |
| 69,5-73,5 s (virage) | 9 px | 1,0 Hz (virage dominant) | 12,6 px | 1,0 Hz |
| 27,6-31,4 s (dialogue, debout) | **0,1 px** | (rien) | 0,1 px | (rien) |
| 54,6-62,4 s (dialogue, debout) | **0,3 px** | (rien) | 0,2 px | (rien) |

- **Un cycle vertical par pas** (2,1 à 2,3 Hz, ≈ 130 pas/min), **un cycle
  latéral par foulée** (demi-cadence, ≈ 1,1 Hz). 10 px sur 490 = **≈ 1° crête à
  crête**.
- Le son des pas a **la même cadence** (périodicité 0,44 à 0,46 s mesurée dans
  le grave pendant la marche).
- **Immobile = immobile** : aucune respiration de caméra, aucun flottement.
  C'est ce qui rend la marche lisible.

### 3.4 Vitesses de rotation

| Situation | Vitesse | Exemples |
|---|---|---|
| Dialogue, écoute | **< 1°/s** (caméra posée) | 26-33 s, 51-63 s, 84-88 s |
| Suivre un guide | **30 à 60°/s**, régulier | 41 s, 46-50 s, 64-70 s |
| Regard guidé vers un objet | tangage **+43°/s** (télé), **-32°/s** (terminal) | 78 s, 89 s |
| Regard libre du joueur | **220 à 300°/s** en coups secs | 10-16 s |

Au total, **38 secondes sur 101** la caméra tourne à moins de 2,5°/s : **le
joueur regarde plus d'un tiers du temps sans rien faire**, et ne s'ennuie pas
parce que quelqu'un agit devant lui.

### 3.5 Profondeur de champ

Utilisée **une seule fois** : pendant l'ouverture, quand Jae est à ≈ 0,65 m
(0 à 8 s). Le détail du fond tombe de 60 % (mesure de contours : 7,5 à 8,4
contre 17 à 25 ailleurs). Dès qu'il s'éloigne (9 s), tout redevient net. Dunn à
1,1 m (34-36 s) ne déclenche aucun flou.

### 3.6 Transitions

- **Bandes de cinéma** de 0 à 1,7 s seulement, retirées d'un coup quand le
  joueur prend la main. Plus jamais ensuite, même pendant les dialogues.
- **Deux fondus au noir** d'environ 0,8 s pour sauter les trajets sans intérêt.
- **Adaptation de l'œil** au passage de la porte (mesuré à 0,1 s près) :
  luminance 108 dedans → 60 face à la porte sombre → 22 dehors (95,7 s) →
  remonte à 38 en 1,5 s.
- **Flou de bougé** sur les rotations rapides (8,2-8,6 s).

---

## 4. La lumière et la matière

### 4.1 Mesures par zone (moyennes sur l'image)

| Zone | Luminance (0-255) | Bleu moins rouge | Saturation | Lecture |
|---|---|---|---|---|
| Entrée et snacks (2-16 s) | 120 à 145 | -15 à -18 | ≈ 17 % | blanc neutre-chaud, très lumineux, peu saturé |
| Rayon pharmacie (50-66 s) | 125 à 139 | **-3 à -5** | ≈ 15 % | plus neutre, presque froid |
| Couloir vers la caisse (68-73 s) | 133 à 151 | **-21 à -25** | ≈ 20 % | le plus chaud |
| Caisse, télé (79-88 s) | 80 à 100 | -7 à -13 | ≈ 21 % | plus sombre (la vitrine noire derrière) |
| Rue de nuit (97-101 s) | **24 à 38** | -6 | **≈ 24 %** | sombre mais plus saturée : la couleur vient des néons |

Chaque zone a **son propre blanc**, sans que l'œil le remarque. L'intérieur est
**lumineux et peu saturé** : la couleur vient des produits, pas de la lumière.

### 4.2 Les sources

- **Plafond** : bandes LED blanches en treillis de losanges, lumière plate,
  presque sans ombre. C'est **la lumière banale d'une supérette**, et c'est
  précisément ce qui fait vrai.
- **Suspensions** à abat-jour sombre au-dessus du comptoir de vitrine (chaudes).
- **Frigos rétroéclairés**, **panneaux de rayon lumineux**, présentoirs
  rétroéclairés derrière la caisse, une enseigne de soda lumineuse.
- **Écrans qui bougent** : télé publicitaire au plafond (2-7 s), télé
  d'information (78-88 s), écran de caisse, terminal de paiement.
- **Dehors** : une dizaine d'enseignes au néon, lampes d'étals, vitrines
  éclairées ; presque pas de lumière d'ambiance.

### 4.3 Le sol

Grands carreaux crème **satinés** : reflets **diffus et flous** des plafonniers
et des rayons, jamais un miroir.

### 4.4 La densité, et ce qui fait « vrai »

- **60 à 80 produits par face de gondole** (≈ 1,2 m), ≈ 40 par porte de frigo,
  une étiquette de prix sous chaque rangée, une pancarte promotionnelle toutes
  les 2 ou 3 rangées, des panneaux de rayon suspendus. **Aucune étagère vide.**
- **Le texte local partout** : affiches, prix, panneaux, bandeau de la télé.
- **Le désordre vrai** : serpillière et seau jaune, cartons au sol, chariot
  chargé de cartons, micro-ondes, machine à café, distributeur de billets,
  caméras de surveillance en dôme, ventilateurs muraux.
- **Les objets à la bonne échelle**, et **personne n'est là pour décorer** :
  chacun fait quelque chose (§ 5.3).

---

## 5. Les personnages (PNJ)

### 5.1 Qui fait quoi

| Personnage (rôle) | Présent | Gestes | Regard | Distance quand il parle |
|---|---|---|---|---|
| Le sergent, Jae (donne la mission) | 0-16, 79-101 | se penche, lève la main, sourit, tourne les talons pour s'excuser | **droit dans l'objectif** pendant la consigne, ailleurs ensuite | **0,6 à 0,7 m** (intimidation pour rire) |
| Le caporal étranger, Dunn (le guide) | 14-101 | fouille, retourne un paquet, **pointe le joueur**, met dans le panier, **attrape en hauteur**, **tend le flacon**, marche devant, **se retourne en marchant** | **sur l'objet en parlant, sur le joueur aux questions et aux chutes** (22-24, 33-37, 63, 67-68) | **1,1 à 1,4 m** ; 2 à 2,5 m en marchant |
| Le soldat qui porte (Cho) | 0-16, 41-46, 78-101 | tient le panier, **reçoit le sac à deux mains**, rit | vers les autres | 1,5 à 2,5 m |
| La recrue bizutée (Ju Kwon) | 11-13, 78-101 | lève la tête vers la télé, répond, subit la blague | télé, puis les autres | ≈ 2 m |
| La caissière | 0-16 (voix, bras), 74-92 | pointe la sortie, désigne le sac, **croise les bras et fixe le joueur**, **tend le sac** | **sur le joueur** : elle attend qu'il paie | ≈ 1,5 m (derrière le comptoir) |

Répartition des 40 répliques : le guide 16, le porteur 7, le sergent 5, la
recrue 5, **le joueur 5**, la caissière 2. **Le joueur parle peu (12 %)** ; le
guide porte la scène (40 %).

### 5.2 Les interactions physiques

- **Mettre dans le panier que tient l'autre** (42,5-46 s) : l'article passe de
  main en main.
- **Tendre le sac par-dessus le comptoir** (84-85 s) : l'achat devient un objet
  qu'on porte, et il sort avec eux.
- **Pointer le joueur du doigt** (36 s) : le joueur est inclus dans la blague.
- **Tendre la main vers un camarade** (83 s), **rire ensemble** (85-90 s).
- **Lever la tête ensemble** vers la télé (79-82 s) : une réaction collective.

### 5.3 La vie de fond

Une douzaine de personnes dans le magasin au départ, **chacune avec une tâche
différente** : un couple qui mange au comptoir de vitrine (encore là à 68-70 s),
une femme accroupie devant le rayon du bas, deux hommes qui observent puis
sortent, une femme rousse qui traverse, deux à quatre soldats (panier, entre les
gondoles). Dehors, 25 à 40 passants, des vendeurs, des gens assis sur des
tabourets. **Personne ne regarde le joueur sans raison.**

### 5.4 Ce qui fait vivant

1. **Parler en faisant** : le guide ne s'arrête jamais pour parler.
2. **Regarder aux temps forts** seulement (la question, la chute).
3. **Le corps comme invite** : la caissière croise les bras, et c'est elle qui
   dit « paie », sans un mot.
4. **Le guide se retourne pour lancer sa chute**, puis repart.
5. **Ils parlent entre eux en fond**, sans sous-titres.

---

## 6. L'interface

### 6.1 L'inventaire complet

| Élément | Où | Taille | Couleur, typographie | Quand |
|---|---|---|---|---|
| **Sous-titres** | bloc **aligné à gauche, qui commence à 36 % de la largeur**, entre 81 et 90 % de la hauteur | ligne ≈ 2 % de la hauteur | texte gris clair sur **une boîte noire translucide par ligne** ; nom à gauche dans sa propre boîte : **bleu-vert** pour l'équipe et le joueur, **jaune pâle** pour les civils ; police **condensée** sans empattement | ≈ 80 % du temps |
| **Nom flottant** | **sur le torse** du coéquipier | ≈ 2 % de la hauteur | bleu-vert, liseré sombre | dès 19 s, sur l'équipe seulement |
| **Croix de choix** | **centre de l'écran** | croix ronde ≈ 25 px, textes ≈ 2 % | blanc ; l'option choisie passe en **bleu-vert** | 24,9-27,5 et 52,0-54,0 |
| **Barre-minuteur** | sous la croix | **48 % de la largeur** | blanc ; la partie consommée reste en trait sombre | avec la croix |
| **Invite « PAY »** | **accrochée à l'épaule de la caissière** | **≈ 3 % de la largeur** | icône de bouton + 3 lettres, blanc | dès 74,6, attend |
| **Carte de titre** | bas gauche | titre ≈ 4,5 % de la hauteur | blanc, condensé gras ; écusson pâle bleu-vert derrière | 10,3-16,0 |
| Le triangle ▶ en bas à droite | (0-1,6 et 95-101,7) | | | appartient probablement à la plateforme vidéo |

**Ce qui ne s'affiche jamais** : pas de réticule, pas de mini-carte, pas de
boussole, pas d'objectif écrit, pas de compteur, pas de flèche au sol, pas
d'arme. **Le corps du joueur n'apparaît qu'une fois**, au geste qui compte : la
main qui tend le téléphone pour payer (90,2-91,8 s).

### 6.2 Les sous-titres en détail

- **Trois lignes au plus**. La nouvelle entre en bas, la plus ancienne **pâlit
  (≈ 40 %) puis part** (13,6 s, 64 s).
- **Les répliques du joueur y passent aussi, sous son nom** : ce qu'on a choisi
  devient une phrase dite.
- **Entre crochets** : traduit d'une autre langue. La langue du lieu existe
  sans exclure le joueur.
- **Effacés pendant un choix**, pour qu'on ne lise qu'une chose.
- Une réplique reste de 2 à 7 s selon sa longueur.

### 6.3 La croix de choix en détail

| | Choix 1 | Choix 2 |
|---|---|---|
| Apparition | 24,9 s, juste après une **question directe** du guide | 52,0 s, après « on devait prendre autre chose, non ? » |
| Options | haut « Pas de réponse » · gauche (la vérité, crue) · droite « [Mentir] Oui, des sushis » · **bas vide** | haut « Soins de la peau » · gauche « Crème pour ton infection » · droite « Médicaments pour l'estomac » |
| Longueur des options | **2 à 5 mots** | 2 à 4 mots |
| Barre | 425 px → se vide par les deux bouts à **≈ 90 px/s** : fenêtre **≈ 4,7 s** | **≈ 79 px/s** : fenêtre **≈ 5,4 s** |
| Réponse du joueur | 2,6 s | 2,0 s |
| Après | l'option passe en bleu-vert, les autres pâlissent, tout disparaît en 0,4 s | idem |
| Effet | **ne change pas l'histoire**, change la réplique (et le rire) | la mauvaise réponse **retarde d'une blague**, puis la bonne arrive quand même |

Pendant le choix, un **voile très léger** couvre l'image (saturation -5 %, trame
fine) : la scène reste lisible et **le guide continue de bouger**. Aucun
bruitage d'interface marquant n'a été mesuré à l'apparition ni à la validation.

### 6.4 L'invite « PAY »

Minuscule, **posée sur la personne qui attend** (elle suit son épaule), elle
**n'insiste pas** : elle reste 15 s pendant que le monde continue (la télé, les
blagues). C'est la caissière, bras croisés, qui fait la pression.

---

## 7. Le son

| Passage | Niveau moyen | Plancher (bruit de fond) | Ce qu'on entend |
|---|---|---|---|
| Ouverture 0-8 s | -22 à -27 dBFS | -27 à -34 | voix fortes, brouhaha de soldats |
| Intérieur calme (12-13, 18-21, 25-27, 52-54) | -30 à -35 | **-36 à -40** | **un fond tonal continu** : bourdon grave ≈ 48 Hz et ≈ 97 Hz, **sifflement fixe ≈ 544 Hz** (frigos, néons), en **stéréo large** (côtés à -2 à -10 dB du centre) |
| Répliques | -22 à -27 | | voix **au centre**, presque mono (côtés à -18 à -28 dB), **8 à 12 dB au-dessus du fond** |
| 37-42 s | -30 à -40 | | **murmures d'hommes non sous-titrés** |
| Marche | | | pas **à peine audibles**, cadence 0,44-0,46 s |
| Rue 97-101 s | -22 | **-26** | foule continue, **10 à 12 dB plus fort** que dedans ; le sifflement de 544 Hz a disparu |

- **Aucune musique** : pas de mélodie, aucune pulsation (autocorrélation
  inférieure à 0,27, sans période stable). Le silence habité suffit.
- **La porte est un filtre** : dehors, le fond change de nature et de niveau.

---

## 8. Le rythme

- **40 répliques en 101 s : une toutes les 2,5 s.** Sous-titres à l'écran 80 %
  du temps. **Plus long silence : ≈ 4,5 s** (38-42,5 s, comblé par les
  murmures).
- **Un choix toutes les ≈ 27 s** (24,9 s, puis 52,0 s), toujours après une
  question directe.
- **Quelque chose de visible arrive toutes les 3 à 6 s** (un geste, un objet,
  une réplique, un regard).
- **Le joueur reste immobile 38 % du temps**, jusqu'à 12 s d'affilée (51-63 s).

| Acte | Temps | Part | Ce qu'il fait |
|---|---|---|---|
| Accroche | 0-1,7 s | 2 % | on arrive **au milieu d'une dispute**, avec un rire |
| Mission | 1,7-9 s | 7 % | quelqu'un, tout près, **confie une course** |
| Découverte libre | 9-16,6 s | 7 % | carte de titre, regards en tous sens, la vie du lieu |
| Le guide | 17,4-73,6 s | **55 %** | deux rayons, deux choix, quatre blagues, un objet montré |
| La caisse | 74,5-92 s | 17 % | l'attente, la télé, le sac tendu, puis le paiement |
| La sortie | 92-101,7 s | 9 % | la porte, l'œil qui s'habitue, la ville, une dernière blague |

**Le paiement n'est pas la fin** : la scène continue 10 s après, et finit sur
une chute, dans la rue.

---

## 9. Chaque procédé, transposé chez Hillary

Légende téléphone : **oui** = coût négligeable sur un Android d'entrée de gamme
(Tecno, Infinix, itel, puce Mali-G52 ou PowerVR, 2 à 3 Go) en 3G dans un
navigateur ; **à adapter** = faisable sous une forme allégée ; **non** = trop
cher pour ce que ça rapporte. Colonne « Salon » : ce que fait le code actuel
(`monde/socle/`, `monde/lieux/hillary-m-styl/`).

### La caméra

| # | Procédé (référence) | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P1 | Yeux à ≈ 1,50 m, 15-20 cm sous ceux des PNJ (§ 3.1) | caméra à **1,52 m** : on lève à peine les yeux vers Afi (1,71 m), Hillary (1,68 m), et on est à hauteur de Maman Sènami (1,62 m) | **oui**, un nombre | `hauteur = 1.62` : on domine Maman Sènami |
| P2 | ≈ 75° horizontal, ≈ 46° vertical (§ 3.2) | en paysage, **48 à 50° vertical** (≈ 76 à 80° horizontal en 16:9). En portrait, impossible de tenir 75° en horizontal sans déformer : garder ≈ 80° vertical et **tourner la caméra vers celui qui parle** | **oui** | 66° vertical en paysage, soit **≈ 98° horizontal** en 16:9 : trop large, personnages petits, bords étirés |
| P3 | Balancement : un cycle vertical par pas (2,1-2,3 Hz, ≈ 1°), un latéral par foulée, pas sonores à la même cadence (§ 3.3) | même loi. Pas de **0,66 m** à 1,45 m/s (2,2 pas/s), vertical sur 0,66 m, latéral sur 1,32 m, `son.pas()` à chaque sommet | **oui**, 10 lignes | vertical sur 0,78 m (1,86 Hz) **mais un pas sonore tous les 0,39 m (3,7 pas/s)** : les deux ne concordent pas, on « trottine » ; aucun latéral |
| P4 | Vitesse de croisière constante, départ et arrêt courts | accélérer en 0,3 s, croiser, freiner en 0,4 s | **oui** | courbe en cosinus sur tout le trajet : la vitesse varie sans cesse (pointe ≈ 2,3 m/s), la cadence aussi |
| P5 | Immobile = immobile (§ 3.3) | garder | **oui** | déjà le cas |
| P6 | Regard guidé à 30-60°/s vers ce qui compte (la télé, le terminal) | la caméra lève les yeux vers l'écran TikTok quand Sènami dit « regarde ! », baisse les yeux vers la tablette du comptoir au moment de commander | **oui** | `tournerVers` existe ; vitesse fixée par le lissage (constante 0,18 s), plus brusque |
| P7 | Pendant une conversation à plusieurs, la caméra **ne saute pas** d'un locuteur à l'autre | ne tourner vers le locuteur **que s'il sort du centre de l'écran** | **oui** | tourne vers la tête **à chaque réplique** |
| P8 | Profondeur de champ à l'accroche seulement, PNJ à ≈ 0,65 m (§ 3.5) | Afi s'approche à 0,9 m pour la course ; fond flou | **à adapter** : un vrai flou coûte deux passes plein écran (trop pour une Mali-G52). Au niveau haut seulement, pendant 6 s ; ailleurs, **vignette sombre et fond assombri de 20 %**, même travail de focalisation | rien |
| P9 | Bandes de cinéma à l'accroche seulement, retirées d'un coup (§ 3.6) | bandes pendant l'ouverture des portes et la première réplique, puis retirées | **oui** (CSS) | bandes à **chaque** dialogue : la référence ne le fait pas |
| P10 | Fondus au noir de ≈ 0,8 s pour sauter les trajets | quand on demande « aller au comptoir » de loin, ou pour une ellipse (« Hillary prend tes mesures » → fondu → « c'est noté ») | **oui** (une div noire) ; réduit aussi le mal des transports | rien |
| P11 | L'œil qui s'habitue en passant la porte (§ 3.6) | en sortant sur le trottoir : exposition -35 % puis remontée en 1,5 s ; en entrant : surexposé puis normal | **oui** (`toneMappingExposure`) | l'exposition suit le jour et la pluie, pas la porte |
| P12 | Flou de bougé sur les rotations rapides | ne pas le faire | **non** : passe plein écran, et le regard au doigt est lent de toute façon | rien (bien) |

### La lumière et la matière

| # | Procédé | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P13 | La lumière **banale et juste** du lieu, chaque zone son blanc (§ 4.1) | galerie : spots chauds et ligne dorée (sa photo) ; **atelier plus froid** (lumière de travail) ; **comptoir plus chaud** ; près de la porte, la lumière du dehors (jour blanc, nuit orangée des lampadaires) | **oui** si la lumière est **précalculée** (plan de `VISION.md` § 3) ; **non** pour des dizaines de vraies lumières | spots et flaques de lumière, ligne dorée, jour et nuit |
| P14 | Écrans et objets lumineux qui bougent | écran TikTok (fait) + **la tablette du comptoir qui affiche le sac** + enseigne lumineuse H.M.S + téléphone d'une visiteuse allumé | **oui** (matériaux sans éclairage, textures dessinées) | écran TikTok, oui |
| P15 | Sol satiné, reflets flous (§ 4.3) | garder le sol crème ; reflet **flou** plutôt que miroir | **à adapter** : carte d'environnement en bas et moyen, vrai reflet en haut seulement | exactement ça |
| P16 | Densité : aucune étagère vide, une étiquette par rangée (§ 4.4) | rouleaux de wax empilés, bobines par couleur, portant de pièces en attente de retouche avec étiquettes à la main (« retouche · mardi »), sacs magenta pliés, carnet de commandes, mètre ruban | **à adapter** : géométries fusionnées, instances, un atlas de textures, objets lointains en plans texturés ; viser **moins de 100 appels de dessin** | wax, mannequins, machine, mètre ruban : à densifier |
| P17 | Le désordre vrai (seau, cartons, chariot) | chutes de tissu sous la table de coupe, ventilateur sur pied, multiprise, tasse, épingles, une housse sur une chaise | **oui** (peu d'objets, gros effet) | presque rien |
| P18 | Le texte du lieu partout | affichettes en français : « Essayage », « Sur-mesure », prix **tirés des données**, jamais inventés | **oui** (textures dessinées) | affiches d'événements, oui |
| P19 | Intérieur lumineux mais peu saturé, la couleur vient des produits | murs crème, la couleur vient **des robes et du wax** | **oui** | conforme |

### Les PNJ

| # | Procédé | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P20 | Distances : 0,65 m (accroche), 1,1-1,5 m (conversation), 2-2,5 m (en marchant) | Afi à **0,9-1 m** pour confier sa course (elle est pressée), puis 1,2 m | **oui** | abordage à 1,25 m : bien |
| P21 | Regard sur l'objet en parlant, sur le joueur aux questions et aux chutes | Hillary regarde le tissu en parlant, **lève les yeux sur la question** (« Tu la veux pour quand ? ») et sur la chute | **oui** (une cible de regard) | Hillary **fixe le joueur en permanence** dès 5,5 m : c'est ce qui rend un personnage inquiétant |
| P22 | Parler en faisant | Hillary plie, épingle, coupe pendant qu'elle parle ; Maman Sènami tâte un wax en racontant | **à adapter** : gestes procéduraux simples sur personnages légers | gestes de parole génériques, activités des visiteuses : bonne base |
| P23 | Présenter l'objet : le lever à hauteur du visage, le tendre | Hillary décroche une pièce, **la lève, la retourne : on voit le dos** (les photos de dos existent pour 9 pièces) | **à adapter** : un plan texturé accroché à sa main | la fiche s'ouvre ; la pièce ne bouge pas |
| P24 | Le guide marche devant et **se retourne pour lancer sa chute** | Sènami t'emmène voir « la robe de la vidéo » au coin TikTok, se retourne à mi-chemin : « Attends, tu vas voir ! » | **oui** | non trouvé dans le code |
| P25 | Un objet passe de main en main (panier, sac) | Hillary **pose le sac magenta sur le comptoir, le remplit à chaque pièce ajoutée, et le tend** quand la commande part | **à adapter** : attacher et détacher un objet, sans cinématique inverse | le sac est une icône d'interface et un message |
| P26 | Le corps comme invite (bras croisés de la caissière) | Hillary **attend avec chaleur** (mains jointes, sourire) quand le sac est plein ; les bras croisés, seulement pour une blague | **oui** | Hillary prend **au hasard la pose « bras croisés »** quand le joueur est proche : dans la référence, c'est le signe de l'impatience |
| P27 | Réaction collective (tous lèvent la tête vers la télé) | quand l'écran TikTok change de vidéo, Sènami et sa mère tournent la tête ensemble, une réplique tombe | **oui** (`regarder()` existe) | partiel : la réplique existe dans les dialogues de Sènami |
| P28 | Vie de fond : chacun sa tâche, personne ne fixe le joueur | dedans, **4 à 5 personnages 3D au plus** (Hillary, les trois visiteuses, une apprentie à la machine) ; dehors, des passants en silhouettes derrière la vitrine | **à adapter** : 13 personnages 3D, **non** ; des silhouettes animées en 2D derrière la vitre, oui | agenda des visiteuses, déjà riche |
| P29 | L'étranger pose les questions naïves (§ 0) | **Afi la Parisienne est ce personnage** : elle demande les délais, l'envoi vers Paris, le sur-mesure, c'est-à-dire **la foire aux questions de la maison**, et l'humour est sur elle (« Il fait chaud… j'avais oublié ! »), jamais sur Cotonou | **oui** | la course d'Afi existe et va dans ce sens |

### L'interface

| # | Procédé | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P30 | Dialogue **qui coule** : pas de boîte, les répliques avancent seules, le joueur n'agit qu'aux choix | pour les conversations d'ambiance et les visiteuses ; **garder la boîte seulement pour la commande** (fiche, cadran), où il faut lire | **oui** | dialogue en boîte, texte tapé, **toucher pour continuer**, déplacement bloqué : c'est un roman graphique, pas la référence |
| P31 | Sous-titres : boîte par ligne, nom coloré par rôle, 3 lignes, l'ancienne pâlit (§ 6.2) | une couleur par personne (déjà) ; **le joueur sous « Toi »** | **oui** ; en portrait, garder au moins 15 px | 3 lignes, noms colorés : conforme |
| P32 | La réponse choisie **devient une réplique** sous-titrée | « Toi : Elle peut être prête avant samedi ? » | **oui** | non |
| P33 | Croix au centre, 3 options de **2 à 5 mots**, « Pas de réponse » en haut, une option pour rire (« [Mentir] ») | « [Bluffer] Bien sûr, je couds aussi » ; jamais sur une décision d'achat | **oui** ; en portrait, la croix **dans le tiers bas**, à portée de pouce, cibles de 44 px | croix présente, sans « Pas de réponse » ; en téléphone, empilée en colonne |
| P34 | Minuteur de ≈ 5 s, la barre se vide par les deux bouts | **6 à 8 s** (on lit plus lentement au téléphone), **seulement pour les répliques légères** ; à zéro, « Pas de réponse » ; **jamais** pour une commande | **oui** (CSS) | rien |
| P35 | Pendant le choix : sous-titre effacé, voile léger, la scène continue de bouger | l'interlocutrice hoche la tête et attend (déjà) ; voile **sans flou d'arrière-plan animé** | **oui** | elle écoute : bien |
| P36 | Nom petit, sur le torse, sur les « siens » seulement | nom à hauteur d'épaule, petit ; « Une visiteuse » tant qu'on ne la connaît pas (déjà) | **oui** | au-dessus de la tête, quand elle parle ou au survol : acceptable |
| P37 | Invite minuscule, posée sur la chose, qui attend sans insister (§ 6.4) | garder l'invite **ancrée sur le comptoir** (un bouton qui bouge se vise mal au pouce) ; elle attend | **oui** ; 44 px au moins | **déjà conforme et mieux pensé pour le doigt** |
| P38 | Carte de titre bas gauche, 6 s, révélée en décodage | « AUJOURD'HUI · 16 h 40 · pluie sur Cotonou / LE SALON / HILLARY M. STYL », monogramme H.M.S pâle derrière, **heure et météo réelles** (déjà calculées pour le haut de l'écran) | **oui** (CSS) | rien |
| P39 | Rien d'autre à l'écran : ni réticule, ni carte, ni objectif écrit | objectif d'Afi affiché **4 s puis replié** ; étiquettes des points au sol seulement pour les 2 plus proches | **oui** | objectif persistant, étiquettes de tous les points visibles, logo et météo en haut |
| P40 | Le corps du joueur n'apparaît qu'au geste qui compte | au moment d'envoyer la commande, **une main tenant un téléphone** entre par le bas pendant 1,2 s (bulle verte **générique**, aucun logo d'application), puis WhatsApp s'ouvre | **à adapter** : une image 2D d'environ 30 Ko, pas une main 3D | rien |

### Le son

| # | Procédé | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P41 | Aucune musique, un fond tonal continu en stéréo large (§ 7) | **le ton de la pièce** : souffle de climatiseur ou ventilateur (bruit filtré + bourdon grave), **machine à coudre lointaine** par rafales rares, ciseaux | **oui** (Web Audio synthétisé, 0 Ko) | rue derrière la vitre et pluie : pas de ton intérieur |
| P42 | Voix au centre, 8 à 12 dB au-dessus du fond | le fond intérieur à ≈ -36 dB, les voix à ≈ -25 dB | **oui** | pas de voix |
| P43 | Murmures non sous-titrés | conversations lointaines des visiteuses : **un murmure synthétisé** (bruit passé dans 2 ou 3 formants qui bougent), sous-titres seulement à moins de 9,5 m (déjà) | **oui** | silence au-delà de 9,5 m |
| P44 | Pas à peine audibles, à la cadence du balancement | même cadence que P3, plus bas | **oui** | 3,7 pas/s |
| P45 | La porte est un filtre : dehors +10 dB, plus clair | sur le trottoir : rumeur **+10 dB**, filtre ouvert jusqu'à ≈ 5 kHz, klaxons de zems, pluie sur la tôle ; dedans, près de la porte : à mi-chemin | **oui** | rumeur filtrée à 420 Hz, fixe |
| P46 | Des voix | **à adapter** : 40 répliques de 3 s en Opus 24 kbit/s ≈ 360 Ko, chargées après le premier écran ; ou des **grommelots** synthétisés (0 Ko) ; ⛔ jamais une voix imitée sans accord écrit | **à adapter** | rien |

### Le rythme

| # | Procédé | Chez Hillary | Téléphone | Salon aujourd'hui |
|---|---|---|---|---|
| P47 | Accroche **au milieu d'une scène**, réplique à 0 s | en entrant, Sènami filme sa mère : « Maman, souris, c'est pour TikTok ! » · Maman Sènami : « Range ce téléphone ! » (aucun fait inventé) | **oui** | « Bienvenue ! » d'Hillary à 2,6 s |
| P48 | Course confiée **avant 10 s** | Afi vient dans les 10 premières secondes (texte déjà écrit) | **oui** | Afi n'aborde qu'après 14 s **et** un premier déplacement |
| P49 | Une réplique toutes les 2,5 s, un choix toutes les ≈ 27 s, quelque chose toutes les 3-6 s | **une première visite écrite de 90 s** au rythme dense, puis le mode libre (agenda des visiteuses) | **oui** | conversations toutes les 14 à 30 s : bien pour le mode libre, trop lâche pour la première minute |
| P50 | Le joueur regarde 38 % du temps (12 s d'affilée) | la présentation d'une pièce par Hillary = **une petite scène de 10 s** sans rien toucher | **oui** | la fiche s'ouvre tout de suite |
| P51 | L'écran annonce un événement du monde, les PNJ le commentent | l'écran passe les **vrais** rendez-vous de la maison (données), les visiteuses réagissent | **oui** | les affiches d'événements existent |
| P52 | Le paiement n'est pas la fin : 10 s de plus, une chute, la rue | après l'envoi : Hillary tend le sac, Afi lance une dernière phrase, la porte s'ouvre sur la rue (l'étage 2, plus tard) | **oui** pour la scène ; **non** pour une rue 3D complète aujourd'hui (étage 2) | « Merci ! Je te réponds sur WhatsApp. » puis rien |

---

## 10. Les 10 priorités : le plus d'immersion pour le moins de coût

Classées par rapport immersion / coût. Coûts estimés en lignes de code dans le
socle actuel, **sans un octet de plus à télécharger** sauf mention.

1. **Marcher juste** (P3, P4, P44). Un pas de 0,66 m, 2,2 pas par seconde, un
   cycle vertical par pas (≈ 1°), un balancement latéral par foulée, le son du
   pas au sommet du cycle, une vitesse de croisière constante.
   *Coût : ≈ 20 lignes (`deplacement.js`, `son.js`). Manque aujourd'hui : la
   cadence sonore (3,7 pas/s) contredit le balancement (1,86 Hz).*
2. **La bonne focale et la bonne hauteur** (P1, P2). Paysage : 48 à 50° en
   vertical ; caméra à 1,52 m.
   *Coût : 2 lignes. Manque : 98° en horizontal aujourd'hui en 16:9, et on
   domine les visiteuses.*
3. **Le dialogue qui coule** (P30, P32, P33, P34, P35). Plus de boîte ni de
   « toucher pour continuer » dans les conversations d'ambiance ; la croix au
   centre (tiers bas en portrait), des réponses de 2 à 5 mots, « Pas de
   réponse », un minuteur doux de 6 à 8 s pour les répliques légères, la
   réponse choisie reprise en sous-titre sous « Toi ».
   *Coût : CSS + ≈ 60 lignes dans `dialogue.js`. Manque : partiel (la croix
   existe).*
4. **L'accroche et la course en 10 s** (P9, P47, P48). Bandes pendant
   l'ouverture seulement, une scène déjà en cours à l'entrée, Afi à 1 m avant
   la dixième seconde.
   *Coût : réordonner l'existant. Manque : partiel.*
5. **Le son de la pièce et la porte-filtre** (P41, P43, P45). Climatiseur,
   machine à coudre lointaine, murmures non sous-titrés ; dehors +10 dB et
   filtre ouvert.
   *Coût : ≈ 40 lignes Web Audio, 0 Ko. Manque : oui.*
6. **Parler en faisant, regarder aux temps forts** (P21, P22, P26, P7).
   Calendrier de regard d'Hillary, et retirer ses bras croisés au hasard près
   du joueur ; la caméra ne saute plus d'un locuteur à l'autre.
   *Coût : ≈ 30 lignes. Manque : partiel.*
7. **L'objet qui passe de main en main** (P23, P25). Hillary lève la pièce et
   la retourne (les photos de dos existent) ; le sac magenta se remplit sur le
   comptoir et elle le tend.
   *Coût : un plan texturé accroché à une main, un objet sac. Manque : oui.*
8. **Fondus et œil qui s'habitue** (P10, P11). 0,8 s au noir pour les longs
   trajets automatiques ; exposition qui réagit 1,5 s au passage de la porte.
   *Coût : une div et un réglage. Manque : oui.*
9. **La carte de titre** (P38). Six secondes, bas gauche, heure et météo
   réelles de Cotonou, monogramme H.M.S.
   *Coût : CSS. Manque : oui.*
10. **Réactions collectives et vie hors champ** (P27, P28, P24). Les têtes qui
    se tournent ensemble vers l'écran TikTok, Sènami qui guide et se retourne,
    des passants en silhouettes derrière la vitrine.
    *Coût : `regarder()` existe ; silhouettes 2D ≈ 50 à 100 Ko. Manque : oui.*

**À ne pas faire maintenant** (trop cher pour ce que ça rapporte sur le
téléphone visé) : vrai flou de profondeur hors niveau haut (P8), flou de bougé
(P12), plus de 5 personnages 3D (P28), la rue de nuit complète (étage 2),
l'éclairage dynamique multiple (P13), viser 60 i/s (la référence tourne à 60 ;
le salon doit tenir **30** sur une Mali-G52), des voix enregistrées tant que les
textes bougent encore (P46).

---

## 11. Où en est le salon par rapport à la référence

### Ce qu'il fait déjà comme elle (ou mieux)

- Sous-titres nommés et colorés, trois lignes au plus.
- Réponses en croix (haut, gauche, droite, bas), l'interlocutrice qui écoute
  et hoche la tête pendant qu'on choisit.
- Une visiteuse qui **vient d'elle-même** confier une course (Afi).
- Invite d'action **ancrée sur le comptoir**, plus facile au pouce que celle
  de la référence.
- Visiteuses qui vivent selon un **agenda** et se parlent entre elles,
  sous-titres à moins de 9,5 m.
- Écran TikTok qui défile, affiches d'événements tirées des données.
- Son synthétisé sans fichier, jour, nuit et pluie de Cotonou.
- Trois niveaux de qualité choisis tout seuls, qui descendent si l'appareil
  peine.
- Immobilité totale quand on ne bouge pas.

### Ce qu'il ne fait pas encore

1. Une marche à la bonne cadence (pas et balancement qui concordent, balancement
   latéral).
2. La focale de la référence en paysage, et la hauteur des yeux sous celle des
   personnages.
3. Le dialogue sans boîte qui avance seul ; la réponse choisie dite à voix
   haute en sous-titre ; « Pas de réponse » ; le minuteur.
4. Une accroche au milieu d'une scène et la course avant 10 s.
5. Un fond sonore intérieur (climatiseur, machine à coudre), des murmures
   lointains, la porte qui change le son.
6. Un regard qui alterne entre la tâche et le joueur ; Hillary qui croise les
   bras au hasard devant le client (à retirer).
7. Un objet montré (pièce levée, retournée) et un sac physique qu'on tend.
8. Les fondus, l'exposition qui réagit à la porte.
9. La carte de titre.
10. Les réactions collectives, un guide qui marche devant et se retourne, la vie
    derrière la vitrine.
11. Les bandes de cinéma réservées à l'accroche (aujourd'hui à chaque
    dialogue), et une interface plus discrète (objectif persistant, étiquettes
    de tous les points).
12. Le geste final du joueur (la main au téléphone) et les 10 secondes après
    la commande.

---

## 12. Garde-fous

- **Rien du jeu** : ni nom, ni personnage, ni marque, ni typographie
  identifiable, ni la carte de titre telle quelle. On reprend des **lois**
  (hauteur, cadence, distances, durées), pas des **dessins**.
- **Aucun fait inventé** dans une réplique : délais, prix, pays desservis,
  événements, tout vient des données de la maison (règle déjà écrite dans
  `textes.js`).
- **Aucune voix imitée**, aucune voix réelle sans accord écrit.
- **L'humour porte sur la Parisienne, jamais sur Cotonou** ni sur une
  personne réelle.
- **Pas de minuteur sur une décision d'argent** : la référence presse pour
  rire, jamais pour faire acheter.
- **Pas d'animation infinie sous un flou d'arrière-plan** (règle du dépôt) :
  le voile des choix est une couleur, pas un `backdrop-filter`.

---

## 12. L'audit du 2026-11-14 : ce qui est pris, ce qui reste (« REA ce qui est possible de prendre et d'ajouter à 100 % »)

> Demande de Mongazi du 2026-11-14. REA a refusé la vidéo (« unsupported binary format » : il démonte des
> programmes, pas des films) ; l'audit est fait **contre le code**, procédé par procédé. La colonne
> « Salon aujourd'hui » du § 9 date du 12 novembre : elle est périmée, c'est ce tableau qui fait foi.

**Déjà dans le salon (vérifié dans le code)** : P2 focale 75° horizontal (`moteur.js`) · P3 et P44 un pas tous
les 0,68 m, tête et son au même instant, roulis par foulée (`deplacement.js`) · P5 immobile = immobile · P8 vrai
flou en qualité haute (vague 3) · P15 sol qui reflète à toutes les qualités (R6) · P16 et P17 la densité et le
désordre vrai (R9, ce jour) · P19 · P20 · P21 et P26 Hillary alterne regard et tâche, accueille sans croiser les
bras · P29 Afi la Parisienne · P30 les répliques avancent seules · P31 · P32 « Toi » · P33 la croix · P35 elle
écoute pendant qu'on choisit · P37 · P38 la carte de titre · P39 objectif replié à 6 s, un seul nom à la fois ·
P41 climatiseur et machine à coudre · P45 la porte-filtre (+10 dB dehors, filtre à 1 600 Hz) · P48 Afi vient
dans les premières secondes · P51 affiches tirées des données (« Prochainement » tant que `faits.json` est vide).

**Ce qui reste, en vagues (une à la fois, chacune regardée et contrôlée)** :

| Vague | Procédés | Ce qu'on construit |
|---|---|---|
| A · la caméra | P1, P4, P7, P9, P10, P11 | yeux à 1,52 m ; vitesse de croisière constante (départ 0,3 s, arrêt 0,4 s) ; la caméra ne saute plus d'une oratrice à l'autre tant qu'elle est dans le cadre ; bandes de cinéma à la seule accroche ; fondu au noir de 0,8 s sur les longs trajets ; l'œil qui s'habitue en passant la porte |
| B · le dialogue | P33, P34 | « Pas de réponse » en haut de la croix pour les répliques légères, un minuteur doux de 7 s qui se vide par les deux bouts (jamais pour une commande) |
| C · le son | P43 | les murmures des conversations lointaines (bruit passé dans des formants qui bougent), 0 Ko |
| D · la vie | P14, P17, P18, P27, P28, P47 | la tablette du comptoir allumée, le ventilateur sur pied qui tourne, les affichettes « Essayage » et « Sur-mesure », les têtes qui se tournent ensemble, des passants en silhouettes derrière la vitrine, l'accroche au milieu d'une scène (Sènami filme sa mère) |
| E · l'objet et le geste | P23, P25, P40, P50, P52 | le sac magenta qui se remplit sur le comptoir à chaque pièce, Hillary qui présente la pièce (face puis dos), la main au téléphone avant WhatsApp, les dix secondes après la commande |

**Pas maintenant** : P12 flou de bougé (non, § 10) · P13 un blanc par zone (il faut recuire la lumière : avec la
prochaine cuisson) · P22 « parler en faisant » et P24 le guide qui se retourne (attendent Hillary et Maman en
3D) · P42 et P46 des voix (⛔ jamais une voix imitée sans accord écrit ; textes encore mouvants) · P49 la première
visite écrite de 90 s (après les vagues A à E, elle les assemble).
