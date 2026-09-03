# Une expérience historique jouable sur le Bénin · analyse et 15 pistes

> Demandé par Mongazi le 2026-08-14 : « une sorte de jeu pour Cotonou, une
> expérience historique mais en jeu, en simulation ». Objectif déclaré :
> **impressionner le Bénin entier**, décrocher des clients, et se montrer aussi
> à l'extérieur du pays.

---

## PREMIÈRE PARTIE · L'ANALYSE

### 1. Ce que vous avez déjà, et ce qui manque

**MON BÉNIN** (`mon-benin.pages.dev`) fait déjà le voyage : sept minutes, huit
stations, sept cents kilomètres de la Porte du Non-Retour au fleuve Niger. Il
est narratif, linéaire, contemplatif. C'est une réussite, et c'est aussi sa
limite : **on le regarde, on ne le fait pas.**

Le jeu n'est donc pas un doublon, c'est la marche suivante :

| MON BÉNIN | Le jeu |
|---|---|
| je vois | **j'ai fait** |
| une fois | on y revient |
| seul | à plusieurs |
| je comprends | **je me souviens, parce que j'ai décidé** |

On retient ce qu'on a décidé, pas ce qu'on a lu. C'est toute la différence entre
un beau site et une chose dont on parle le lendemain au bureau.

### 2. Qui vous voulez impressionner, et ce qui impressionne chacun

Ce ne sont pas les mêmes personnes, et **rien n'impressionne les cinq à la
fois**. Il faut choisir sa cible en premier, la technique vient après.

| Qui | Ce qui l'impressionne vraiment | Ce qui ne lui fait rien |
|---|---|---|
| Le Béninois avec un téléphone à 30 000 F | que ça s'ouvre vite et que ça marche chez lui | la 3D, les mots anglais |
| Le commerçant que vous voulez pour client | qu'il se reconnaisse, lui, son métier | l'histoire ancienne |
| L'institution (musée, mairie, école) | le sérieux des sources et le hors-ligne | le score et les points |
| L'étranger et la diaspora | la dignité du récit, la version anglaise | l'humour local |
| Le développeur, ici et ailleurs | que ce soit fait **sans moteur de jeu**, et que ce soit fluide | le contenu |

### 3. La contrainte qui décide de tout

Le public que vous visez joue sur un **Android d'entrée de gamme, avec de la
data payée au mégaoctet**. Ce n'est pas un détail de performance, c'est le
cahier des charges :

- **Sous 3 Mo au premier chargement.** Au delà, la moitié du pays ne verra
  jamais votre travail, et ceux qui le verront diront que ça rame.
- **Jouable d'une seule main, en vertical**, dans un taxi, avec du soleil sur
  l'écran.
- **Hors-ligne dès la deuxième visite** (PWA). Dans un musée d'Abomey, il n'y a
  pas de réseau. Dans un taxi non plus.
- **Aucune bibliothèque lourde.** C'est déjà votre méthode sur les vitrines,
  c'est ici un argument de vente : « fluide sur un téléphone à 30 000 F, écrit
  à la main ».

### 4. La direction artistique, et pourquoi elle est déjà trouvée

Règle absolue de la maison, déjà écrite dans MON BÉNIN : **aucune image générée
par IA d'un lieu réel**. Un faux Ganvié est un mensonge sur un pays qui existe.

Un jeu **dessiné** échappe entièrement au problème, et le style est là, sous la
main : **l'appliqué d'Abomey et les bas-reliefs des palais**. Aplats de couleur,
silhouettes découpées, animaux emblèmes, indigo, ocre, blanc, or.

Trois raisons, et aucune n'est esthétique :

1. **C'est honnête.** Un dessin ne prétend pas être une photo.
2. **C'est léger.** Des aplats en SVG pèsent des kilooctets, pas des mégaoctets.
   La contrainte du point 3 est résolue par le style lui même.
3. **C'est reconnaissable entre mille.** Personne d'autre au monde n'a cette
   grammaire graphique. Un étranger qui voit une capture sait que ça vient d'ici.

### 5. La ligne rouge, et elle n'est pas négociable

Trois sujets ne se gamifient pas n'importe comment : **la traite négrière, le
vodun, les rois**.

- **Aucun score, aucun chronomètre, aucune vie sur la mémoire de la traite.** Un
  compteur de points sur la Route des Esclaves, et vous ne réparez plus votre
  réputation. Ce sujet se traite en marche, en silence, en noms.
- **Le vodun n'est pas un décor de jeu vidéo.** On explique un système, on ne
  fait pas parler un esprit. Rien sur le Fâ, les Zangbéto ou les Egungun sans
  l'accord de dépositaires nommés.
- **Aucune affirmation historique sans source.** La crédibilité que vous
  cherchez se perd sur une seule date fausse, et un professeur d'histoire la
  trouvera en trois minutes. Chaque écran porte sa source, visible.

Dit autrement : **la retenue est votre meilleur effet spécial.** C'est elle qui
fait la différence entre « le développeur béninois qui a fait ça » et « celui
qui a fait un jeu sur l'esclavage ».

### 6. La règle de l'artisan

**Un jeu fini bat quinze démos.** Quinze idées ouvertes et abandonnées, c'est le
contraire de l'effet recherché : ça dit qu'on ne finit pas. Deux jeux terminés,
polis, rapides, et le pays vous croit.

Ces quinze pistes sont un **catalogue de choix**, pas un programme.

### 7. Comment ça ramène vraiment des clients

Un jeu ne se vend pas. **Il fait la démonstration d'une capacité que vous
vendez.** Chaque idée ci dessous porte donc une ligne « ce que ça prouve », et
c'est celle qui compte pour le business :

- une boucle temps réel fluide → applications métier réactives ;
- du multijoueur synchronisé → formation, événement d'entreprise ;
- du hors-ligne complet → outils de terrain, là où le réseau tombe ;
- de la géolocalisation → logistique, livraison, tourisme ;
- un moteur de règles chiffré → **c'est littéralement Boussole**.

Et en pied de chaque jeu, une seule ligne, sobre : *fait à Cotonou par NEBULA
Agency*, avec le lien. Pas de bannière, pas de publicité. La sobriété fait
sérieux.

---

## DEUXIÈME PARTIE · LES QUINZE IDÉES

Cinq familles de trois. Chaque famille sert un objectif différent : la
crédibilité, le partage, l'utilité, le terrain, la démonstration technique.

---

## FAMILLE 1 · LA MÉMOIRE
*Objectif : la crédibilité et la presse. Ce sont les pièces qu'une institution
peut soutenir sans se compromettre.*

### 1. LE TRÉSOR REVENU

**En une phrase.** Vingt six œuvres sont rentrées à Abomey le 10 novembre 2021,
cent vingt neuf ans après le pillage du palais : le joueur les rapatrie une à
une et reconstitue la salle.

**Rôle.** La pièce de crédibilité. C'est le sujet béninois le plus suivi à
l'international, et il est **entièrement documenté**, donc sans risque
d'invention.

**Comment ça se joue.** On ne marque pas de points, on **retrouve**. Chaque
objet arrive avec trois indices (la matière, la fonction, le roi), on le replace
dans la salle, et son histoire s'ouvre : qui l'a fait, à quoi il servait,
comment il est parti en 1892, où il est aujourd'hui. Le geste final est le plus
fort du projet : **une place reste vide**, celle du kataklè, le tabouret encore
absent. Tant qu'il n'est pas rentré, le jeu ne peut pas être terminé.

**Ce que ça apporte.** Une salle de musée dans la poche de n'importe quel
écolier du pays, et une histoire que la presse étrangère raconte déjà : la place
vide se photographie et se partage.

**Ce que ça prouve.** Rigueur documentaire, performance, lecture audio pour ceux
qui lisent mal. Et le sens du détail : un vide qui attend vaut mieux qu'un
badge.

**Taille.** Moyenne (deux à trois semaines). **Risque.** Les droits sur les
photographies des œuvres. Solution : dessins au trait originaux, ou accord écrit
du musée.

### 2. 1892, LE CHOIX DU ROI

**En une phrase.** Vous siégez au conseil de Béhanzin, et chaque tour vous
présente une décision réelle, avec ce qu'on en savait à ce moment là.

**Rôle.** Comprendre au lieu de juger. Faire sentir l'étau, pas refaire
l'histoire.

**Comment ça se joue.** Un jeu de cartes de décision, quatre ressources
(hommes, poudre, alliances, récoltes) et le temps qui avance. Chaque carte porte
sa source en bas. À la fin, votre partie se compare à ce qui s'est réellement
passé, et le jeu explique pourquoi l'issue fut celle là.

**Ce que ça apporte.** L'histoire vécue de l'intérieur, sans héroïsation
ridicule ni humiliation. C'est le format qui manque cruellement à l'école.

**Ce que ça prouve.** Un moteur de règles avec conséquences chiffrées et
sauvegarde : exactement ce qu'on vend en logiciel métier.

**Taille.** Moyenne. **Risque.** ⚠️ L'issue est une défaite. Le jeu doit
l'expliquer (artillerie, guerre longue, isolement diplomatique) sans la
réécrire. **Validation par un historien obligatoire avant publication.**

### 3. LA ROUTE, À PIED

**En une phrase.** Ce n'est pas un jeu, c'est une marche : les trois kilomètres
et demi de la Route des Esclaves, au rythme du doigt.

**Rôle.** La pièce morale du projet. C'est elle qui rend tout le reste
défendable.

**Comment ça se joue.** On avance, on ne peut pas accélérer. Aucun score, aucun
chronomètre, aucune vie. À chaque halte, on ne passe qu'une fois le texte lu.
Voix, silence, noms. La fin est la mer, et on n'a rien gagné.

**Ce que ça apporte.** De la dignité, et un public immense : la diaspora
afro américaine, brésilienne, caribéenne, pour qui Ouidah est un lieu
d'origine.

**Ce que ça prouve.** La retenue, qui est la chose la plus difficile à obtenir
d'un développeur. Techniquement : défilement contrôlé, audio, hors-ligne.

**Taille.** Petite à moyenne. **Risque.** Le rater par excès d'effets. Règle de
travail : **si ça brille, on retire.** ⚠️ Les noms des lieux et des arbres se
vérifient auprès du musée d'Ouidah avant toute mise en ligne.

---

## FAMILLE 2 · LA FIERTÉ QUI SE PARTAGE
*Objectif : le bruit. Ce sont les pièces qui circulent sur WhatsApp sans qu'on
paie personne.*

### 4. ZEM RUSH

**En une phrase.** Vous êtes zémidjan à Cotonou : un client, une adresse, la
pluie, et le carrefour qui ne passe pas.

**Rôle.** La viralité pure. C'est celui que tout le monde envoie à un ami.

**Comment ça se joue.** Arcade à un doigt, vue de dessus, dessin à plat. Des
courses qui s'enchaînent, l'essence, la pluie qui change la conduite, les
embouteillages aux heures connues de tous. Le score se partage en image, et le
classement se fait **par quartier**.

**Ce que ça apporte.** La ville se reconnaît, et un métier que tout le monde
utilise est traité avec sérieux au lieu d'être un décor.

**Ce que ça prouve.** Une boucle de jeu fluide à soixante images par seconde en
JavaScript pur, sur un téléphone bon marché, **sans moteur de jeu**. C'est la
pièce qui fait dire aux développeurs : « c'est fait avec quoi ? ».

**Taille.** Petite (une à deux semaines). **Meilleur rapport effort sur bruit de
toute la liste.** **Risque.** ⚠️ Faire du zémidjan un gag. Le respect du métier
décide si c'est un succès ou une moquerie.

### 5. L'ATELIER D'APPLIQUÉ

**En une phrase.** Composez votre tenture royale avec les symboles du Danhomè,
et repartez avec l'image.

**Rôle.** Faire fabriquer la publicité par les joueurs eux mêmes : chacun repart
avec une affiche à poster.

**Comment ça se joue.** Un fond (indigo, ocre, blanc), des symboles à poser, un
titre. Chaque symbole affiche **sa signification vérifiée** quand on le
sélectionne : on apprend en composant. Export en carré et en format story.

**Ce que ça apporte.** Un savoir-faire textile réel, expliqué au lieu d'être
décoratif, et une porte ouverte vers les ateliers d'Abomey : un bouton
« commander une vraie tenture » qui envoie vers un artisan. **Ce bouton là est
une vitrine NEBULA en puissance.**

**Ce que ça prouve.** Un éditeur graphique dans le navigateur, export d'image,
zéro serveur, zéro coût de fonctionnement.

**Taille.** Petite. **Risque.** ⚠️ Attribuer un symbole au mauvais roi.
Validation obligatoire auprès d'un atelier ou du musée.

### 6. LE NOM DES CHOSES

**En une phrase.** Cent mots du quotidien en fon, yoruba, goun, bariba et dendi,
dits par de vraies voix.

**Rôle.** L'utilité de tous les jours, et la diaspora qui veut transmettre à ses
enfants.

**Comment ça se joue.** Séries de deux minutes, par famille de mots : le marché,
la famille, la route, la politesse. On écoute, on reconnaît, on répète. La
progression se garde sur le téléphone.

**Ce que ça apporte.** Des langues nationales traitées comme des langues, pas
comme du folklore. Un outil pour les parents, les ONG, les nouveaux arrivants.

**Ce que ça prouve.** L'audio, le hors-ligne, l'accessibilité. Et il y a un vrai
produit derrière : une méthode de langue se vend.

**Taille.** Moyenne, surtout du travail d'enregistrement. **Risque.** ⚠️ Des
voix synthétiques tueraient le projet. Il faut de vrais locuteurs, bien
enregistrés.

---

## FAMILLE 3 · L'UTILE
*Objectif : l'école, l'argent, le civisme. Ce sont les pièces qui ouvrent des
portes institutionnelles et commerciales.*

### 7. DANTOKPA, LE VRAI MÉTIER

**En une phrase.** Vous tenez un étal : vous achetez, vous négociez, vous vendez,
et à la fin de la semaine vous découvrez ce que vous avez **vraiment** gagné.

**Rôle.** Le pont commercial. C'est la démonstration jouable de **Boussole**.

**Comment ça se joue.** Des journées qui s'enchaînent, des prix qui bougent, des
clients qui marchandent, un crédit qu'on accorde ou pas, la tontine, la pluie,
la marchandise qui s'abîme. Le dimanche, le calcul honnête : coût de revient,
marge réelle, ce qui reste.

**Ce que ça apporte.** De l'éducation financière à grande échelle, dans la
langue du commerce béninois. Beaucoup de joueurs découvriront qu'ils perdent de
l'argent sur un produit qu'ils croyaient rentable.

**Ce que ça prouve.** Le moteur de Boussole, en dix minutes, sans rendez-vous de
démonstration. Un commerçant qui a joué comprend le produit.

**Taille.** Moyenne. **Risque.** ⚠️ Moraliser. Le jeu montre les chiffres, il ne
fait pas la leçon. **C'est l'idée qui ramène des clients le plus directement.**

### 8. LA CLASSE QUI RÉPOND

**En une phrase.** Le professeur ouvre une partie, quarante élèves rejoignent
avec un code, tout le monde répond en même temps.

**Rôle.** Entrer dans les écoles. Un directeur qui voit ça vous rappelle.

**Comment ça se joue.** Questions d'histoire et de géographie du Bénin,
chronomètre, classement de la classe, et une banque de questions que le
professeur peut compléter lui même.

**Ce que ça apporte.** Un outil pédagogique gratuit et local, là où les écoles
n'ont ni budget ni matériel.

**Ce que ça prouve.** Le temps réel synchronisé. C'est la démonstration la plus
spectaculaire pour un non-technicien : **tout le monde voit la même chose au
même instant.**

**Taille.** Moyenne à grande. **Risque.** Le serveur temps réel a un coût, à
dimensionner avant de promettre. La même mécanique se revend en formation
d'entreprise.

### 9. LE BUDGET DE MA COMMUNE

**En une phrase.** Cent unités à répartir entre école, eau, route, santé, marché
et sécurité, puis une année passe et vous voyez ce que ça donne.

**Rôle.** Le civisme, et un positionnement vers les mairies et les ONG.

**Comment ça se joue.** Des curseurs, une année simulée, des indicateurs qui
bougent, des événements (saison des pluies, épidémie, marché qui brûle). À la
fin, la comparaison avec un vrai budget communal ⚠️ *si des données publiques
existent, à vérifier avant de le promettre*.

**Ce que ça apporte.** Comprendre pourquoi tout n'est pas possible en même
temps. Un débat public un peu mieux informé.

**Ce que ça prouve.** Modélisation, tableaux de bord, visualisation de données :
exactement ce que financent les ONG et les bailleurs.

**Taille.** Moyenne. **Risque.** ⚠️ Le terrain politique. Montrer des
arbitrages, jamais des partis ni des personnes.

---

## FAMILLE 4 · LE TERRAIN
*Objectif : les lieux réels, le tourisme, et des partenaires qui paient.*

### 10. LA CHASSE AU TRÉSOR DE COTONOU

**En une phrase.** Le jeu se joue dehors : des étapes réelles dans la ville, une
énigme à chacune.

**Rôle.** Faire sortir les gens, et vendre des étapes à des commerces.

**Comment ça se joue.** Six à dix stations (l'Amazone, Dantokpa, le port, la
cathédrale, un musée), une énigme par lieu, une photo à prendre, un badge.
Classement hebdomadaire.

**Ce que ça apporte.** De l'animation urbaine, du tourisme intérieur, et un
modèle économique clair : hôtels, restaurants, sponsors paient pour être une
étape.

**Ce que ça prouve.** Géolocalisation, QR, hors-ligne, et un back-office pour
créer un parcours : **un produit vendable à chaque ville du pays**, puis
ailleurs.

**Taille.** Moyenne. **Risque.** Les autorisations. Commencer par les lieux
publics, ajouter les privés avec accord.

### 11. LE MUSÉE QUI PARLE

**En une phrase.** Un audioguide qu'on joue au lieu de l'écouter, pour Abomey et
Ouidah, et qui fonctionne **sans réseau**.

**Rôle.** Le dossier institutionnel. C'est celui qu'on dépose sur la table d'un
musée ou de l'agence du tourisme.

**Comment ça se joue.** On entre dans une salle, on cherche un détail sur un
bas-relief, on répond, l'histoire s'ouvre. Français, anglais, fon.

**Ce que ça apporte.** Une visite dont un enfant se souvient, et pour le musée
des statistiques de fréquentation qu'il n'a pas aujourd'hui.

**Ce que ça prouve.** Le hors-ligne complet, le multilingue, l'audio. Argument
imparable : **ça marche dans le musée, où il n'y a pas de réseau.**

**Taille.** Moyenne. **Risque.** Sans accord, ça reste un prototype. Mais le
prototype suffit à décrocher le rendez-vous : c'est même sa fonction.

### 12. GANVIÉ, L'EAU ET LE POISSON

**En une phrase.** Vous tenez un foyer sur le lac Nokoué : pêcher, réparer,
vendre, et ne pas vider le lac.

**Rôle.** L'écologie par le système, sans discours.

**Comment ça se joue.** Les saisons, les acadja, la jacinthe d'eau, le prix du
poisson, l'école des enfants à payer. Si on pêche tout, la partie devient
invivable : **la leçon est dans les règles, pas dans un message.**

**Ce que ça apporte.** Comprendre un mode de vie unique au monde, et la pression
réelle qui pèse sur le lac.

**Ce que ça prouve.** Une simulation à boucles de rétroaction, équilibrée. Le
genre de moteur qu'achète un projet agricole ou halieutique.

**Taille.** Moyenne à grande. **Risque.** ⚠️ L'exactitude. Il faut parler à des
pêcheurs de Ganvié, pas lire trois articles.

---

## FAMILLE 5 · LA DÉMONSTRATION
*Objectif : faire dire « qui a fait ça ? ». Ce sont les pièces qui vous
distinguent d'un intégrateur de modèles.*

### 13. LE FÂ, MACHINE À PENSER

**En une phrase.** Seize signes, deux cent cinquante six combinaisons : le Fâ
présenté pour ce qu'il est, un système de savoir structuré.

**Rôle.** Montrer une intelligence africaine sans folklore. C'est l'idée qui
impressionne les intellectuels, ici et dehors.

**Comment ça se joue.** On découvre la combinatoire, on explore l'arbre des
signes, on lit les récits qui s'y rattachent, et on voit le pont avec le binaire
que les élèves apprennent en informatique. ⚠️ **Aucune divination simulée,
aucune prédiction** : on explique une structure, on ne joue pas au bokonon.

**Ce que ça apporte.** De la fierté intellectuelle, et un pont inattendu entre
un savoir ancien et le métier que vous exercez.

**Ce que ça prouve.** Visualisation, arborescence, design de l'information : le
haut du panier en matière de savoir-faire web.

**Taille.** Moyenne. **Risque.** ⚠️ **Le plus sensible de la liste.** À ne faire
qu'avec des dépositaires nommés et leur accord écrit. Sinon, ne pas le faire du
tout.

### 14. COTONOU, LA VILLE QUI GRANDIT

**En une phrase.** Un curseur de 1960 à aujourd'hui, et la ville se déploie sous
le doigt.

**Rôle.** La pièce d'orfèvrerie, celle que partagent les architectes, les
urbanistes et la presse.

**Comment ça se joue.** Peu de jeu, beaucoup de révélation : les quartiers, le
port, la lagune, les ponts, la population. On pose un point n'importe où et on
voit ce qu'il y avait avant.

**Ce que ça apporte.** La mémoire d'une ville qui a explosé en soixante ans, et
un outil pour les écoles et les urbanistes.

**Ce que ça prouve.** De la donnée géographique, de la cartographie fluide sur
téléphone, sans bibliothèque lourde.

**Taille.** Grande. **Risque.** ⚠️ **Les données.** Sans sources cartographiques
fiables, on invente, et tout s'effondre. À vérifier **avant** de promettre quoi
que ce soit.

### 15. LE GRAND MATCH DES ROYAUMES

**En une phrase.** Ce n'est pas une application, c'est un rendez-vous : un soir
par semaine, à vingt heures, tout le pays joue en même temps.

**Rôle.** L'effet de masse. C'est la pièce qui vous rend visible en une soirée.

**Comment ça se joue.** Vingt questions, vingt minutes, un thème par semaine.
Chacun sur son téléphone, un classement national, par ville et par école.

**Ce que ça apporte.** Un rendez-vous national autour de la culture du pays, et
un objet sponsorisable par un opérateur télécom ou une banque.

**Ce que ça prouve.** La montée en charge : dix mille personnes en même temps.
C'est la vraie difficulté d'ingénieur de toute la liste. Si ça tient, plus
personne ne doute de vous.

**Taille.** Grande. **Risque.** ⚠️ **Le plus risqué.** Une soirée qui plante
devant dix mille personnes fait plus de mal que dix réussites ne font de bien. À
lancer par paliers : une école, puis dix, puis une ville, et seulement après le
pays.

---

## TROISIÈME PARTIE · CE QUE JE FERAIS

### L'ordre que je recommande

1. **ZEM RUSH** en premier. Petit, fini en une à deux semaines, drôle,
   partageable, et il installe le socle technique et graphique de tous les
   autres. On ne commence pas par le monument, on commence par ce qui se termine.
2. **DANTOKPA, LE VRAI MÉTIER** ensuite. C'est celui qui ramène des clients, et
   il réutilise le moteur de règles que vous avez déjà pensé pour Boussole.
3. **LE TRÉSOR REVENU** comme pièce maîtresse, monté pendant que les deux autres
   tournent, parce qu'il demande des accords et de la vérification. C'est lui qui
   vous met dans la presse, et la place vide du kataklè est le geste dont on
   parlera.

### Un socle, pas quinze projets

Les trois partagent la même coquille : même direction artistique (l'appliqué),
même chargement, même pied de page, même hébergement, même méthode de contrôle.
C'est votre logique d'usine à produits, appliquée aux jeux. **Le deuxième jeu
doit coûter la moitié du premier, le troisième le quart.**

### Où ça vit

Sous **MON BÉNIN**, à une adresse unique, pas sur une marque nouvelle. Vous avez
déjà une porte d'entrée sur le pays : une seule marque forte vaut mieux que deux
marques tièdes, et le voyage envoie vers les jeux, les jeux renvoient vers le
voyage.

### Comment le pays l'apprend

Vous avez déjà l'outil : le format TikTok « oui / non », et le studio vidéo pour
le monter. Une série de questions sur le jeu, une carte par question, et le lien
en bio. Ajoutez trois cercles : les écoles (un professeur convaincu vaut
quarante familles), la presse culturelle (le sujet du trésor est déjà suivi), la
diaspora (une version anglaise change tout).

---

## CE DONT J'AI BESOIN DE VOUS

1. **Un choix, un seul, pour commencer.** Ma recommandation : Zem Rush.
2. **Est-ce que ça vit sous MON BÉNIN** ou sous une marque à part ?
3. **Avez-vous un contact** dans un musée, une école, une mairie, la Fondation
   Zinsou ? Un seul contact réel change complètement l'ordre des priorités.

---

## SOURCES ET POINTS À VÉRIFIER

**Vérifié le 2026-08-14 :**

- **26 œuvres** des trésors royaux d'Abomey restituées par la France, acte de
  transfert signé le 9 novembre 2021, cérémonie du 10 novembre 2021 ; pillage du
  palais d'Abomey en **1892** par les troupes du général Dodds. Un 27e objet, le
  **kataklè**, restait à rentrer (état de la question fin 2024).
  Sources : [Élysée](https://www.elysee.fr/emmanuel-macron/2021/10/27/ceremonie-organisee-pour-la-restitution-de-26-oeuvres-des-tresors-royaux-dabomey-a-la-republique-du-benin) ·
  [Quai Branly](https://m.quaibranly.fr/en/collections/living-collections/news/restitution-of-26-works-to-the-republic-of-benin) ·
  [Ambassade de France au Bénin](https://bj.ambafrance.org/-Restitution-des-biens-culturels-) ·
  [AllAfrica, kataklè](https://fr.allafrica.com/stories/202411080427.html)
- **Statue de l'Amazone**, Cotonou : **30 m**, environ 150 tonnes, bronze,
  inaugurée le **30 juillet 2022**, esplanade des Amazones.
  Sources : [Monument Amazone, Wikipédia](https://fr.wikipedia.org/wiki/Monument_Amazone) ·
  [Jeune Afrique](https://www.jeuneafrique.com/1367556/culture/benin-lamazone-bio-guera-et-lobelisque-aux-devoues-trois-monuments-pour-se-reapproprier-lhistoire/)

**⚠️ À vérifier avant toute mise en ligne** (ne rien publier sur ces points sans
source) : la longueur exacte et les stations de la Route des Esclaves à Ouidah
(le CONTEXT de MON BÉNIN retient environ 3,5 km) · la signification et
l'attribution de chaque symbole royal · les noms et l'état d'avancement des
musées en construction · les chiffres de population de Ganvié et de Cotonou ·
l'existence de données budgétaires communales publiques · les données
cartographiques historiques de Cotonou.
