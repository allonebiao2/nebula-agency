# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Confirmé par Mongazi le 2026-11-12, trois publics à la fois :

- **Les clientes de Cotonou** : femmes d'environ 20 à 45 ans, arrivées par TikTok ou WhatsApp,
  au téléphone, souvent en 3G. Elles viennent découvrir les créations et commander une tenue.
- **La diaspora** : Béninoises de Paris et d'ailleurs, qui commandent à distance (expédition, ou
  retrait pendant un séjour).
- **Les commerçants prospects** : à qui NEBULA vend LE MONDE. Le salon d'Hillary est leur
  démonstration : ils doivent vouloir le leur.

## Product Purpose

LE MONDE fait visiter des commerces en 3D, à la première personne, dans le navigateur du
téléphone ; à terme une ville calquée sur Cotonou, un lieu par commerce, un loyer. Le premier
lieu est le salon de couture d'HILLARY M. STYL.

**Le succès se mesure d'abord à un commerçant qui signe pour son propre lieu** (Mongazi,
2026-11-12). La visite doit donc avoir la tenue d'une immersion valant **20 000 € au moins**
(ses mots, 2026-11-12 : « je veux que ça vaille au moins et minimum 20 000 euros ») et **donner envie d'acheter** : le visiteur finit avec une pièce dans le sac et
envoie sa commande sur WhatsApp.

## Positioning

Une boutique qu'on visite comme un jeu, au téléphone, avec le vrai catalogue du commerçant, de
vraies personnes qui parlent et une commande qui part sur WhatsApp. L'heure et la météo réelles
de Cotonou passent dans le lieu. Référence de sensation donnée par Mongazi : *Call of Duty*,
*GTA 6* (avec la limite dite : un téléphone en 3G n'est pas une console).

## Operating Context

- Mobile d'abord, au pouce ; téléphones d'entrée de gamme, réseau 3G.
- On se déplace par points lumineux et on regarde en glissant le doigt ; on parle aux
  personnages par réponses au choix ; un carnet retient ce qu'on a appris.
- La commande passe par le sac, un cadran de validation, puis un message WhatsApp pré-rempli.
- Hillary n'a **pas de lieu physique** : son salon est imaginé. Les prochains commerçants qui en
  ont un seront scannés (vidéo, puis 3D).

## Capabilities and Constraints

- **Catalogue et prix LUS** dans la vitrine en ligne du commerçant (`_construire.py`), jamais
  recopiés : une seule vérité.
- **Aucune photo de produit inventée par IA** présentée comme le catalogue. Ambiance et matière
  générées : autorisées.
- **Les visiteuses sont des personnages inventés**, jamais présentés comme de vraies clientes ;
  aucun avis, aucun événement, aucune histoire inventés (`faits.json` vide = rien d'affiché).
- **Le visage et la voix d'Hillary** seulement avec son accord écrit.
- **Les âges sont posés** : Hillary 26 ans, Afi 29, Sènami 21, Maman Sènami 47.
- Les tailles : Hillary 1,68 m, Afi 1,71, Sènami 1,64, Maman Sènami 1,62.
- Le visiteur ne voit jamais ses propres bras.
- Le décor reste **en 3D vivante** : pas de panoramas figés (Mongazi, 2026-11-12).
- Technique : Three.js r180 servi depuis le dépôt, JavaScript sans autre bibliothèque, aucune
  étape de construction côté navigateur.

## Brand Commitments

- Le lieu porte l'identité d'HILLARY M. STYL : monogramme **H.M.S**, **magenta `#E6007E`**,
  encre, papier patron crème ; ses polices de vitrine sont Bodoni Moda, Archivo et Manrope.
- Tout en français, sans tiret cadratin dans les textes.
- **L'interface est en verre fumé, plate, petite et discrète** (préférence durable de Mongazi,
  2026-11-12, après avoir rejeté des « enseignes peintes » jugées ringardes) : rien ne doit
  remplir l'écran ; étalon : l'interface de la vidéo Call of Duty qu'il a fournie.
- **Le salon est tamisé** (murs sombres et chauds, une lumière par création) et porte une
  musique feutrée.

## Evidence on Hand

- Les 19 pièces du catalogue, avec photos face et dos, prix, délais, express (vitrine d'Hillary).
- Le logo H.M.S (`lieux/hillary-m-styl/img/`).
- **Absents, à ne pas inventer** : photos et accord d'Hillary, son compte TikTok, ses événements,
  son histoire, son adresse, de vrais avis.

## Product Principles

1. **Chaque choix se juge à « est-ce que ça donne envie d'acheter ? »** : le produit est le
   héros de chaque plan.
2. **Un commerçant qui visite doit vouloir le sien** : la tenue d'ensemble vaut plus que la
   quantité de fonctions.
3. **Le vrai d'abord** : le catalogue, l'heure, la météo et les personnes sont vrais ou
   déclarés inventés.
4. **Le téléphone en 3G est l'appareil de référence**, pas le PC.
