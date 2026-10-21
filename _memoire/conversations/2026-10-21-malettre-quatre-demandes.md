# 2026-10-21 (nuit) · MA LETTRE À… : les quatre demandes de Mongazi, et le verdict de la 0036

Mongazi, après la coupure du PC (arrêt propre demandé par Windows à 16 h 53, sans doute le courant) :
« continue ce que tu faisais », puis « et côté ma lettre ? », puis « oui commence et enchaîne un à un,
invoque tous les skills qui te seront utiles pour tous les réaliser à 100 % chacun ».

## Ce qui tournait : la 0036 (trading, dépôt privé)

- Le calcul « NEBULA calcul 0036 » a repris seul à 19 h 06 et fini à 22 h 28.
- **D-100 calculé : la 0036 (breakout & retest des quarts) NE TIENT PAS.** Aucun des 58 752 réglages
  positif en recherche ; les 10 finalistes de −0,077 à −0,121 R par trade en confirmation, t de −1,65 à
  −3,50 contre le hasard ; aucun FTMO viable (au mieux 21 % de challenges). Consigné dans
  `_cerveau/DECISIONS.md` du dépôt privé (commit `034f97b`, poussé). Enterrement : à la décision de Mongazi.
- Trouvé en passant : ORB et LE PIÈGE n'ont pas tradé le 21 (internet coupé de 14 h 28 à 14 h 42 environ,
  MT5 refusait l'autorisation, code -6). Pas un bug ; leurs 4 essais d'une minute ne couvrent pas une coupure
  de 15 minutes (proposé à Mongazi : réessayer jusqu'à la fin de la fenêtre).

## Demande 1 · la police, et la chasse à tout ce qui « fait IA »

Skills chargés : `impeccable` (fiche `malettre/PRODUCT.md` écrite depuis le dépôt, détecteur, typeset,
critique), `redesign-existing-projects`, `design-taste-frontend`, `high-end-visual-design`.

- **Texte courant : Commissioner, axe « flair » à 100** (la lignée d'Optima, la police des papeteries et
  des cartes gravées), choisie sur une planche de cinq candidates avec les vrais textes, nuit et papier
  (Schibsted actuelle, Commissioner évasée, Proza Libre, Alegreya Sans, Rosario). 47,6 Ko contre 46,8.
- **Les signes « IA » retirés** : le surtitre en capitales espacées au-dessus de CHAQUE section (10 retirés ;
  celui du héros devient « Cotonou, le 21 octobre 2026 », le lieu et la date d'une lettre) ; la formule de
  titre « ligne droite + ligne italique colorée » (gardée dans une seule section, la plume écrit « Elle
  écrit. » À LA MAIN) ; les petits libellés en capitales (cartes, fiche, habillage) passés en italique Caslon ;
  le gris lilas des paragraphes réchauffé (`--gris-nuit` #b0a79c).
- **La typographie française du texte visible** (une passe du build, jamais dans les scripts ni les
  attributs) : apostrophe typographique, espace insécable devant ; : ! ? et dans les guillemets.
  ⚠️ PAS l'espace fine U+202F : Commissioner et le Caslon ne la dessinent pas, elle tombait à presque rien.
  Le contrôle des langues compare désormais l'apostrophe droite et la typographique pareil.
- Le jambage de « papa » sortait de l'écran au téléphone : un pas de marge au prénom du héros.

## Demande 2 · les bruitages, et le casier plus clair

- **Les bruitages** (Web Audio, aucun fichier) : un clic de papier au survol, un clic au toucher, le cachet
  frappé et le papier qui glisse au casier. Jamais avant un geste, muets quand le son du site est coupé
  (`malettre:son`), leçon audio mobile appliquée. **Une seule copie** : le module vit dans `creer.html`
  entre `/*__BRUITS__*/` et `/*__FIN_BRUITS__*/`, la vitrine le LIT au build (sans ses commentaires).
- **Les emblèmes** : 28 dessins au trait (24 × 24) gravés dans le cachet de chaque occasion, la cire de sa
  famille. Une seule source : `EMBLEMES` dans `creer.html`, lu par le build. Une occasion sans emblème prend
  son initiale.
- **Le casier** : une consigne dit ce que fait le choix ; le nom ne se coupe plus (« Encouragement » sortait
  de sa case) ; au téléphone, **une étagère par famille qu'on fait glisser** au lieu d'un mur de 27 cases ;
  au survol la lettre monte, au toucher **elle sort de sa case** et le cachet est frappé, puis on écrit.
- **Le constructeur** (`creer.html`, l'étape « Pour quelle occasion ? ») : les mêmes cachets, le même son,
  la frappe au toucher, les familles en italique.
- ⛔ **TROUVÉ EN LIGNE : LES TIMBRES FANTÔMES.** Inclinés en 3D par GSAP et encore invisibles, les timbres du
  prix prenaient le doigt sur presque toute la page (sonde : 39 positions de défilement au téléphone). Au
  téléphone, toucher une case du casier touchait un timbre, et rien ne se passait. Corrigé
  (`pointer-events:none` sur les décors 3D sans rien à toucher) ; nouveau contrôle sur une grille de points,
  avec son témoin (on rend le doigt aux timbres, la sonde doit les attraper).

## Demande 3 · le verre partout

(skill `ui-ux-pro-max` : flou 10 à 20 px, teinte translucide, liseré, reflet)

- ⛔ La règle du dépôt l'emporte : aucune animation infinie sous un `backdrop-filter`. Les fonds bougent
  derrière la moitié des sections, donc **verre fumé et givré** (teinte, grain de givre figé, liseré, arête
  de lumière) sans flou recalculé ; **le vrai flou** derrière la fenêtre des exemples, où la page dort
  (`html.voile`) pendant qu'elle est ouverte.
- **Le papier reste du papier** (lettres, enveloppes, timbres, billets) ; le verre habille l'interface :
  champs, fiche de la plume, puces, panneau d'habillage, cadre du téléphone, boutons secondaires, aveu,
  texte du faire-part, questions (verre clair sur le papier), consigne, paiement, compteurs.
- Le bouton principal : un **verre liquide plein** (le contraste ne dépend jamais du fond). Les deux bandes
  de bord restent **opaques** (verre teinté plein).

## Demande 4 · la soirée entre potes

- Occasion `potes`, famille « La famille et les amis » : **« Soirée entre potes » · « Un chill privé, sur
  invitation »**, titre « Tu es de la fête », formule « On t'attend, ». Questions neuves : « Tu organises »,
  « Chacun apporte », le ton (drôle, chaleureux, cash, mystérieux, simple). L'aide des consignes demande le
  lieu et l'heure ; **la plume ne les invente jamais** (registre ET savoir-faire). Anglais : « Night with
  friends ». Le nom reste à confirmer par Mongazi.

## Le poids, les contrôles, la publication

- Les ajouts avaient porté le premier écran à **321 Ko** (plafond 320). **La page livrée n'a plus ses commentaires**
  (`alleger()` du build : 23 Ko sur 178, soit 13 %) ; elle pèse 154,7 Ko. La source les garde : lire
  `_accueil_src.html`, jamais `index.html`.
- Deux contrôles corrigés : la nuit des lettres comparait des noms à apostrophe droite contre la page typographiée ;
  le témoin de la barre attendait la couleur du papier sous un bouton devenu verre liquide (il vérifie désormais
  qu'il lit la surface claire du bouton, pas la nuit derrière).
- **Tous verts** : accueil **307** (FR + EN, dont la sonde des fantômes sur page neuve et son témoin, le casier, un
  vrai toucher au téléphone) · constructeur **285** · caisse **379** · langues **52** · faire-part **83**.
- **Publié le 2026-10-21 vers 23 h 30** (Pages `malettre`), `malettre-plume` republiée. Vérifié en ligne : contenu
  identique au disque (seul ajout : le script de détection de robots que Cloudflare injecte lui-même en fin de
  page), **aucun fantôme** au téléphone ni sur ordinateur (avant : 39 et 33 positions de défilement touchées), un
  vrai toucher sur une case mène à `/creer?occasion=mois`, 28 occasions, aucune erreur.
- ⏳ Mongazi : confirmer « Soirée entre potes », écouter les bruitages au téléphone (le mode silencieux de l'iPhone
  coupe le Web Audio), le premier franc.
