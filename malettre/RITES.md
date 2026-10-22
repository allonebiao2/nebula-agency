# MA LETTRE À… · une ouverture propre à chaque occasion (les « rites »)

> Mongazi (2026-10-22) : « de base chaque événement doit avoir son animation spéciale et les animations que je vois
> actuellement ne sont pas si impressionnantes. Je veux que tu utilises les animations des vidéos que je t'ai envoyées
> dans le dossier ma lettre, UTILISE-LES TOUTES ET EN PLUS INSPIRE-TOI D'elles pour créer d'autres animations. »
> Puis : « exceptionnelles, d'une qualité et d'une fluidité magistrales et éblouissantes ».

## La règle

Une lettre digitale, c'est une enveloppe cachetée qu'on ouvre à l'heure dite. **Chaque occasion a SON fermoir**
(l'objet qui tient la lettre fermée) **et SON geste** (ce qu'on fait pour l'ouvrir). Le fermoir sort de l'occasion,
jamais d'un catalogue d'effets : si une ouverture pourrait servir à une autre occasion sans rien changer, elle est à
refaire. Les deuils de couple et d'amitié restent sobres : la sobriété y est la forme du respect.

## Où on en est (2026-10-22, soir · vague 2)

**18 ouvertures, 9 mécaniques, chacune des 28 occasions en a au moins trois.** Rien n'est déployé. Le catalogue vit dans
**`rites/carte.json`** (seule source) : des OUVERTURES (une mécanique + un thème) et, pour chaque occasion, ses
ouvertures dans l'ordre (la première est la sienne, incluse dans toutes les offres).

| Mécanique | Le geste | Ce qu'on voit | Ouvertures (thèmes) |
|---|---|---|---|
| `cachet` | toucher | la cire s'allume, casse en trois éclats, le rabat se lève, la carte sort | cachet |
| `perles` | toucher | le collier se dénoue, les perles roulent, les quatre rabats s'ouvrent | perles |
| `portes` | toucher | le cœur de cire se fend, le petit cabinet brodé s'ouvre | portes-brodees |
| `bougie` | « souffler » | la flamme se couche, le noir, la fête | bougie |
| `battants` | toucher, puis écarter du doigt | deux battants plein écran s'ouvrent VERS SOI sur la vraie lettre | portes-dentelle, portes-velours, moucharabieh, portes-deco |
| `rideau` | les trois coups | le rideau s'ouvre à l'italienne, la salle applaudit | rideau-theatre, rideau-soie, rideau-minuit |
| `feu` | toucher le ciel | les fusées vont au doigt, le bouquet final écrit le prénom | feu-fete, feu-or, feu-coeur |
| `lanterne` | garder le doigt dessus | elle s'allume, s'envole, des dizaines d'autres montent | lanterne, lanterne-lune |
| `pli` | un toucher par rabat | la lettre pliée se déplie, le papier devient la lettre | pli, pli-noyer |

- **Après chaque ouverture, la lettre S'ÉCRIT** (`rites/ecriture.js`) : titre, texte à la plume, photos, jours,
  signature, puis la pluie en final. Un toucher accélère, deux écrivent tout.
- **Les ouvertures plein écran** (`plein: true`) sont une FENÊTRE : la scène est transparente là où elle ne dessine
  rien, et passe devant la page au moment où la lettre apparaît.
- **Chaque geste a son repli automatique** (personne n'est bloqué devant une porte fermée), et sa phrase d'aide.
- **Sobriété** : excuse, rupture et brouille n'ont ni feu ni rideau (la lettre pliée, la lanterne, le cachet).
- **Le choix et la caisse sont branchés (pas déployés)** : dans le constructeur, un bloc « L'ouverture » propose les
  ouvertures de l'occasion (la sienne d'abord, « Incluse » ; une « grande » d'ailleurs, « + 1 000 F »), et « Voir » la
  joue sur une lettre d'EXEMPLE (le prénom, l'habillage, pas les mots de l'acheteur). Le constructeur lit un catalogue
  léger (`ouvertures.js`, 6 Ko) ; le moteur entier (`rites.js`) ne se charge qu'au premier « Voir ». À la caisse,
  `lireOuverture(occ, id)` (dans `_shared/lettre.ts`) refuse une ouverture qui n'est pas celle de l'occasion (on garde la
  sienne), compte +1 000 F pour une « grande » d'ailleurs, et range `rite` et `motif` dans la lettre ; `malettre-lettre`
  la sert avec `poserRite` ; le reçu nomme une ouverture payée. Contrôles : caisse 418, langues 52, lettre 284, vitrine et faire-part à relancer (le système les a arrêtés faute de mémoire ; avant la reconstruction de l'accueil : 320 sur 322 et 82 sur 83, leurs échecs venant de l'accueil périmé).

### Le retour de Mongazi, et le prix

- Vague 1 : « plus spectaculaire », « pixelisé », « Sega au lieu de PS5 » → le moteur « cinéma » (rendu hors écran
  sur-échantillonné, FXAA, halo, profondeur de champ, papier qui se courbe, 60 images par seconde).
- Puis : « j'aime mieux » ; au moins 3 à 5 par événement ; l'écran entier comme une porte ; le texte qui s'écrit ;
  « faire durer », « ultra interactif ». Choix : **« Les deux »** (plusieurs au choix, chacune qui dure).
- **Le prix, tranché** : l'ouverture de son occasion est incluse dans TOUTES les offres (même La Carte) ; en choisir une
  autre : les simples incluses (`grande: false`), les « grandes » à +1 000 F. Le prix se calcule au serveur.

## L'architecture

- `rites/moteur.js` (le théâtre WebGL 1, aucune bibliothèque), `atelier.js` (objets et sons partagés), `ecriture.js`
  (la lettre qui s'écrit), `branchement.js` (la pose dans le seuil, le mode plein écran, le doigt, le repli) : le
  COMMUN, présent dans chaque lettre (48,9 Ko minifié, plafond 52 000). Chaque mécanique dans `rites/<mecanique>.js`
  (plafond 24 000), avec ses sons propres.
- Le gabarit (`lettre.html`) porte le marqueur `/*MALETTRE_RITE*/null/*FIN_MALETTRE_RITE*/`. **`poserRite(html, id,
  cire, occasion)`** (le même dans `rites.js` pour le constructeur et `_shared/rites.ts` pour le serveur) y pose le
  commun, la mécanique, ses matières et `THEME` (le thème de l'ouverture + l'emblème de l'occasion, lu dans
  `creer.html`). ⛔ L'ouverture vient de NOS fichiers ; inconnue, c'est « cachet ». Le serveur devra vérifier qu'elle
  appartient à l'occasion.
- Construire : `python malettre/_rites.py`. Regarder : `rites/_voir.py <ouverture>` (planche), `_demo.py` (de vraies
  lettres sur http://localhost:8765/), `_geste_essai.py <ouverture>` (le geste vérifié), `_ecriture_essai.py`.
- Règles de la lettre, inchangées : aucun appel réseau, mouvement réduit (la lettre de toujours), Web Audio, vibration ;
  sans WebGL ou à la moindre erreur, l'ouverture d'avant, puis l'écriture.

## Les 28 ouvertures (le plan d'origine, toujours la source d'inspiration)

| Occasion | Le fermoir | Le geste, ce qu'on voit | Tiré de |
|---|---|---|---|
| Demande de couple | un ticket à gratter | on gratte : « Tu veux sortir avec moi ? » apparaît sous l'argent | 0e910abc (gratter la date) |
| Mois de rencontre | un éphéméride | les pages tournent de 1 au nombre de jours, la dernière s'arrache | inventé |
| Saint-Valentin | deux portes brodées, tenues par un cœur de cire | le cœur se fend, les portes pivotent en 3D, les pétales | 3964bcf0 (portes et sceau d'or) |
| Anniversaire de couple | le monogramme | le rabat part avec le sceau, les deux initiales se gravent en or, un cercle et la durée en arc | 4c46da1e, 3a06fe10 (dentelle) |
| Demande en mariage | l'écrin | le couvercle s'ouvre lentement, la bague prend un seul éclat, la question s'écrit | inventé (sobriété maximale) |
| Excuse | le pli et la colombe | la feuille pliée en huit se déplie pli par pli ; la colombe du sceau s'envole | c83bac02 (colombe) |
| Rupture | rien de plus que la cire | la cire se décolle, sans éclat ni pluie | sobriété |
| Anniversaire | une bougie sur le sceau | on souffle (on touche) : la flamme se couche, la fumée monte, les confettis | inventé |
| Fête des mères | l'enveloppe gaufrée de fleurs | les rabats festonnés s'ouvrent haut et bas, une fleur éclot | 0d136ce0 |
| Fête des pères | le nœud de cravate | le nœud glisse et se défait | inventé (son emblème) |
| Naissance | le ruban | le nœud se défait, un mobile d'étoiles tourne, une boîte à musique | inventé |
| Mariage | le collier de perles | le sceau casse, les perles glissent et tombent, les quatre rabats s'ouvrent | 971ee54d |
| Amitié | le carnet de souvenirs | polaroïds, timbres, billets posés sur l'enveloppe glissent de côté | 8ab65a27 (collage) |
| Soirée entre potes | le billet d'entrée | on déchire le talon le long des pointillés, les confettis | 8ab65a27 (billet) |
| Rupture d'amitié | le lien | les deux maillons se séparent doucement | sobriété (son emblème) |
| Noël | le paquet | le nœud se défait, le ruban glisse, le papier s'ouvre, la neige | inventé |
| Nouvel an | le compte | 3, 2, 1 en grand, puis le feu d'artifice d'or | 3a06fe10 (compte) |
| Tabaski | le moucharabieh | deux panneaux d'étoiles géométriques, éclairés par derrière, s'écartent | 6bc34816 (portes) |
| Fin du Ramadan | le croissant et la lanterne | la lune se lève, la lanterne s'allume, « Aïd Moubarak » s'écrit en lumière | d69edd61 (calligraphie) |
| Pâques | l'œuf | la coquille se fêle en zigzag et s'ouvre, la lumière sort | inventé |
| Réussite | le diplôme roulé | le ruban glisse, le rouleau se déroule, les toques volent | inventé |
| Encouragement | la montagne | un chemin se trace jusqu'au drapeau du sommet, qui flotte | son emblème |
| Bon rétablissement | la pousse | une tige sort du sceau, deux feuilles se déplient, lumière du matin | son emblème |
| Nouveau travail | la serrure | la clé tourne (clic, clac), l'enveloppe s'ouvre comme une porte | inventé |
| Départ à la retraite | le réveil | il sonne et tremble ; on le touche, il se tait, s'endort ; le soleil se lève | a5b8b505 (la frise) |
| Merci | le bouquet | la ficelle se dénoue, les fleurs s'ouvrent en éventail | inventé |
| Une invitation | la télé rétro | elle s'allume, la neige, puis « Ça te dit ? » | 8ab65a27 (télé) |
| Autre occasion | le cachet | le cachet casse en trois, le rabat se lève, la carte sort (l'ouverture d'aujourd'hui) | c83bac02 |

## Les vagues

1. ✅ Le théâtre, quatre ouvertures, le moteur « cinéma ».
2. ✅ La lettre qui s'écrit, les portes plein écran, le rideau, le feu d'artifice, les lanternes, la lettre pliée :
   18 ouvertures, trois au moins par occasion.
3. ✅ Le choix dans le constructeur (et son prix), le serveur, la caisse, les contrôles. Reste : la publication, avec
   le feu vert de Mongazi (les fonctions `malettre-commande` et `malettre-lettre`, puis le site).
4. D'autres mécaniques du plan d'origine (le ticket à gratter, l'écrin, le ruban du cadeau, l'œuf, le monogramme…).
5. Remotion : chaque ouverture filmée en clip court pour la vitrine et les statuts.
