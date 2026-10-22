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

## Où on en est (2026-10-22, vague 1)

**Le théâtre existe et tourne dans la vraie lettre.** Un moteur 3D WebGL écrit pour la lettre, sans bibliothèque
(`rites/moteur.js`), un atelier d'objets partagés (`rites/atelier.js` : la table, l'enveloppe aux couleurs de
l'habillage, le cachet de cire au sceau en relief et ses éclats PLEINS, les pluies en 3D, les sons), le branchement
dans le seuil (`rites/branchement.js`), et quatre ouvertures :

| Rite | Occasion | Ce qui se passe |
|---|---|---|
| `cachet` | toutes les autres, en attendant la leur | la cire s'allume, casse en trois éclats et étincelles, le rabat doublé de damas se lève, la carte sort, la caméra plonge |
| `perles` | Mariage | le collier de perles et de grains d'or se dénoue, les perles roulent sur la table, les quatre rabats s'ouvrent un à un |
| `portes` | Saint-Valentin | le cœur de cire à l'initiale bat deux fois et se fend, les portes brodées s'ouvrent sur une lueur rose et des pétales |
| `bougie` | Anniversaire | « Souffler la bougie » : la flamme (vraie lumière) se couche et meurt, la fumée, le noir, puis les confettis |

- **Les matières viennent de Blender** (Cycles, CPU) : `rites/_matieres_blender.py` rend douze « matcaps » (les cinq
  cires du produit, l'or poli et brossé, l'argent, la perle à la nacre irisée, deux velours, le papier) sous la lumière
  d'une chambre le soir (« interior », Poly Haven, CC0, fournie avec Blender). La lettre lit la lumière dedans : un vrai
  rendu pour le prix d'une texture de 128 px.
- **Construire** : `python malettre/_rites.py` (après toute retouche) écrit `malettre/rites.js` (constructeur) et
  `supabase/functions/_shared/rites.ts` (serveur), avec la même fonction `poserRite(html, id, cire)`. Le moteur minifié
  pèse 26 Ko (environ 9 Ko compressé), un rite 2 à 6 Ko, chaque matière environ 5 Ko.
- **Regarder** : `python malettre/rites/_voir.py <rite>` (une planche à huit instants, le temps est une donnée),
  `python malettre/rites/_lettre_essai.py <rite>` (dans une vraie lettre), `python malettre/rites/_demo.py` (les
  quatre lettres sur http://localhost:8765/).
- **Toujours une lettre qui s'ouvre** : sans WebGL, en mouvement réduit, dans l'aperçu du constructeur ou à la moindre
  erreur, la lettre reprend l'ouverture d'avant (`RITE` vaut `null`). Avant l'heure, la cire dort ; à l'heure, elle
  s'allume. Au repos, 30 images par seconde au plus, rien quand la page est cachée.
- ⏳ **Pas encore branché** : le constructeur (choisir son ouverture), le serveur (`poserRite` dans `malettre-lettre`),
  la caisse (le prix d'une ouverture premium), et les 24 autres occasions.

## Les 28 ouvertures

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

## L'architecture

- Chaque rite vit dans `malettre/rites/<id>.js` (et son CSS dedans) : `{seuil(env), ouvrir(fin), duree, pluie}`.
- Le gabarit (`lettre.html`) porte un marqueur `/*MALETTRE_RITE*/…/*FIN_MALETTRE_RITE*/`. Le constructeur (aperçu) et
  le serveur (lettre envoyée) y posent **le seul rite de l'occasion**. Le gabarit seul reste sous 60 Ko ; chaque
  lettre ne porte que son rite (comme la plume ne reçoit que le savoir-faire de l'occasion).
- ⛔ Le rite vient de NOS fichiers, jamais du navigateur : le serveur choisit par l'identifiant d'occasion, sur une
  liste blanche, comme il choisit le prix. `D.occasion` est le nom affiché : il faut un champ `rite` (l'identifiant).
- Une lettre d'avant ce champ, ou un rite inconnu : l'ouverture d'aujourd'hui.
- Règles de la lettre, inchangées : aucune bibliothèque, aucun appel réseau, `prefers-reduced-motion` (la lettre
  s'ouvre sans mouvement), le son en Web Audio, la vibration, un rite ≤ 6 Ko.

## Les vagues

1. L'infrastructure (marqueur, constructeur, serveur, contrôles) et six rites : Anniversaire, Saint-Valentin, Demande
   en mariage, Mariage, Fête des mères, Soirée entre potes. Montrés à Mongazi.
2. Les vingt-deux autres.
3. Remotion : chaque ouverture filmée en clip court pour la vitrine (le casier des occasions) et les statuts.
