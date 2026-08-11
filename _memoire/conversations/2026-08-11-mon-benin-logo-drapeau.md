# 2026-08-11 · MON BÉNIN, le logo au drapeau et la liste du contenu

**En ligne : https://dev.mon-benin.pages.dev** · dossier `benin-mon-pays/`

## Ce que Mongazi a demandé

> « le logo que je veux doit être aux couleurs du drapeau du pays et en forme
> du Bénin ; ensuite dis-moi tout ce que je dois t'apporter en contenu.
> actuellement finalise ça »

Deux choses, faites toutes les deux.

## 1. Le logo : le pays rempli du drapeau

L'ancienne marque était **le méridien gradué** (un cercle, une ligne qui le
traverse, un point d'or). Elle est retirée.

La nouvelle est **le contour du Bénin rempli du drapeau**, traversé par **la
ligne des sept cents kilomètres** qui monte de la Porte du Non-Retour au fleuve
Niger, avec le **point d'or du kilomètre zéro** sur la côte et **sept
graduations**, une par centaine de kilomètres.

**Ce que la ligne apporte, et sans quoi ce logo serait celui de n'importe quel
site béninois :** un pays au drapeau, tout seul, est un cliché qu'on voit sur
mille autocollants. La ligne est l'instrument du site, elle relie deux lieux
réels, et elle dit le sujet (un voyage) en plus du pays.

### Ce qui ne se devine pas

- **Le contour vient de Natural Earth 50 m, DOMAINE PUBLIC** (146 points,
  `_contour.py`, simplifiés au dessin par Douglas-Peucker). Ce choix n'est pas
  neutre : geoBoundaries, l'autre source évidente, est en **CC BY**, donc
  attribution obligatoire. **Un logo se recopie partout, il ne peut pas traîner
  une obligation de crédit derrière lui.**
- **Les trois couleurs sont lues sur le fichier officiel** de Wikimedia
  Commons, pas choisies à vue : `#008751` `#fcd116` `#e8112d`, et la bande
  verte fait **40 %** de la largeur (360 sur 900). Un drapeau approximatif sur
  un logo de pays se voit en deux secondes.
- **Fait vérifié sur les coordonnées** : tirée droite de la Porte du Non-Retour
  à Malanville, la ligne **tient entièrement à l'intérieur du pays**. Aucune
  verticale ne le fait (à la latitude 11,5 le méridien de la Porte est déjà
  sorti) : c'est la diagonale du voyage réel qui marche.
- **La ligne est prolongée de 16 % au-delà de Malanville et c'est la découpe du
  pays qui l'arrête.** Sans ça elle s'interrompait au milieu du jaune et avait
  l'air inachevée. Le fleuve **est** la frontière, la ligne doit y finir.
- **Les longitudes sont multipliées par cos(latitude moyenne).** Sans ça le
  pays est trop large de 1,4 % : invisible sur une carte, visible sur un logo
  qu'on compare au vrai contour.
- **« MON BÉNIN » reste monochrome.** Trois couleurs dans la marque et trois
  dans le mot, ça fait une enseigne. C'est aussi ce qui permet de poser le logo
  sur l'encre comme sur le papier sans le refaire.

### ⚠️ LE PIÈGE DU JOUR : un filtre CSS qui retournait les couleurs

`.barre-lo` portait **`filter: invert(1) brightness(1.6)`**, parfaitement
légitime du temps où la marque était monochrome : la barre posait la version
claire sur l'encre. **Sur un drapeau, `invert(1)` rend le vert MAGENTA.**

Rien ne l'aurait annoncé : le fichier est juste, la page répond 200, et c'est
le navigateur qui fabrique la faute à l'affichage.

Remède : la petite marque est **remplie, sans contour ni ligne** (à 26 px un
trait de plus est une rayure), donc lisible telle quelle sur les deux fonds, et
**le filtre est parti**. Un contrôle lit maintenant le `filter` calculé.

### Les autres décisions de dessin

- Le grand verrouillage garde un **fin contour** (crème sur l'encre, encre sur
  le papier) : à 1 200 px, un aplat sans arête a l'air mou.
- **Un seul favicon désormais.** Celui qui vivait dans `assets/images/` était
  orphelin depuis que `index.html` pointe vers le dossier du logo. Deux
  favicons dans un dépôt, c'est celui que personne ne regarde qui finit par
  partir en ligne.
- **L'image de partage porte la marque** : la vignette WhatsApp est la première
  impression au Bénin (leçon Angy Art).
- **cairosvg est inutilisable sur ce poste** (`libcairo-2.dll` absente) : les
  PNG sont rendus par **Playwright**, déjà là pour le contrôle qualité, avec le
  moteur qui servira le site. `_logo_png.py`.

## 2. Un défaut trouvé en chemin : le bouton mentait

Le bouton de la barre annonçait **« Les onze lieux »** alors que le site en
porte **huit**. Les onze sont une décision du 2026-08-10, pas une construction.

C'est **la même famille que la jauge qui contredisait son étiquette** (elle
affichait 3 en face de « km 0 »). Corrigé en « Les huit lieux », et **un
contrôle vérifie désormais que le mot et le nombre concordent** : il repassera
au rouge le jour où les trois lieux arriveront, ce qui est exactement le but.

## 3. La liste du contenu

**`benin-mon-pays/CE-QUE-TU-DOIS-APPORTER.md`.** Photos (deux par lieu, **en
portrait**, format, heures de prise de vue, interdits), voix (30 à 45 s, un
souvenir précis et non une description), les 3 lieux manquants (4 choses par
lieu), l'anglais (je traduis, 2 décisions à trancher), l'accord écrit des cinq
artisans, le domaine, les sons réels, **ce dont je n'ai PAS besoin**, et deux
messages prêts à copier (le photographe, les artisans).

**Le point le plus important, et il n'était écrit nulle part :** les 8 photos
actuelles sont vraies mais **empruntées** (CC BY / CC BY-SA). Le crédit est
obligatoire, il est affiché en bas de page, elles sont en paysage alors que le
site est vertical, et n'importe qui peut utiliser les mêmes. **Ce ne sont pas
nos images.**

## L'état

**107 contrôles verts, 0 échec** (91 avant). Les 16 nouveaux : les bornes du
contour mesurées en degrés (si quelqu'un remplace le fichier par un autre pays,
rien ne le signale à l'écran), les trois couleurs présentes dans les cinq
fichiers du logo, aucun texte non tracé, aucun filtre qui retourne les
couleurs, les deux images du logo réellement chargées, et la concordance du
libellé avec le nombre de lieux.

Déployé et **vérifié en comparant les octets** (MD5 de l'image servie contre
celle du disque), jamais un compteur de taille.

## Fichiers

`benin-mon-pays/_contour.py` (nouveau) · `_logo.py` (réécrit) ·
`_logo_png.py` (nouveau) · `_images.py` · `_qc.py` · `_dist.py` ·
`assets/app.css` · `index.html` · `assets/images/logo/*` (10 fichiers) ·
`assets/images/og.png` · `CONTEXT.md` · `CE-QUE-TU-DOIS-APPORTER.md` (nouveau)
