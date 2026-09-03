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

---

# Deuxième partie de la journée · les photos, le héros, et une seule adresse

## 4. Le héros ne montrait aucune photo

Mongazi, photo de son écran à l'appui : « dans le héros je ne vois toujours pas
d'image ». **C'était exact, et ce n'était pas un cache : le portail n'a jamais
porté de photo.** Il montrait l'atlas dessiné sur un aplat de couleur ; les huit
vraies photos ne vivaient que dans les sections, plus bas dans la page. Il
regardait l'écran où il n'y en avait pas.

La photo passe désormais **sous la nappe**, qui devient un voile teinté de la
couleur du lieu : la photo se voit, l'identité de couleur reste, le titre de
96 px garde son contraste. Elle suit le tour automatique et traverse l'iris.

- **`_photos_portail.py`** fabrique des `-po.webp` à 1 000 px. Le portail les
  montre sous un voile, un motif et un titre : il n'a aucun besoin de 1 400 px,
  et **depuis qu'il tourne tout seul, chaque kilo-octet est payé huit fois.**
- ⚠️ **On vise un POIDS, pas une qualité.** À qualité fixe, la Porte fait 15 Ko
  et la Pendjari 169 : une savane, c'est des dizaines de milliers de feuilles,
  la compression n'a rien à mordre. Le script baisse la qualité jusqu'au
  plafond de 92 Ko, puis **réduit la taille** quand la qualité ne suffit plus
  (la Pendjari finit à 740 px, 89 Ko). Le premier écran reste sous 320 Ko.
- ⚠️ **Premier réglage trop sombre, corrigé après avoir REGARDÉ la capture.**
  Le voile initial laissait **16,96:1** de contraste et une photo qu'on
  devinait à peine. Le contraste était excellent et l'image invisible.
  **Regarder vaut mieux que lire un chiffre.**

## 5. Le portail avance tout seul

« Toute animation ou mouvement doit se faire sans attendre forcément une
intervention humaine. » Un tour toutes les 6,2 s, avec quatre garde-fous :
`prefers-reduced-motion`, portail hors écran, onglet en arrière-plan, et **un
vrai geste repousse le tour de 12 s** (on ne vole pas la main du visiteur).

⚠️ **Le tour automatique ne télécharge AUCUNE ambiance.** Sinon les huit sons
partent en une minute, 380 Ko que personne n'a demandés sur une page de 231.
Le tour automatique est un regard, pas une visite.

## 6. Un contrôle qui mentait une fois sur deux

Quatre contrôles du portail exigeaient « le premier lieu ». Depuis le tour
automatique, ils échouaient **selon l'heure à laquelle ils tombaient**. Un
contrôle qui crie au loup finit par ne plus être lu. Ils vérifient désormais la
seule chose qui doit rester vraie : que le nom, la région, le kilomètre, le
lien **et la photo** désignent TOUS LE MÊME lieu.

Et le **contraste est mesuré sur les huit lieux**, plus sur un seul : le fond du
titre change complètement d'un lieu à l'autre (la Porte est un crépuscule, le
toit de Ouidah est en plein soleil). Mesuré : **6,19 à 11,95:1**.

## 7. « La page ne passe pas »

**`mon-benin.pages.dev` répondait 404.** Le site n'avait jamais été publié sur
la branche de production : seul `dev.mon-benin.pages.dev` servait. C'est
l'adresse la plus courte, celle qu'on tape de mémoire.

Puis Mongazi a tranché : « **il est censé y en avoir une seule, pourquoi
deux ?** ». Il a raison, et le problème était pire que deux liens : **la page
n'avait ni `canonical` ni `og:url`**. Rien ne disait à Google, à WhatsApp ni à
quelqu'un qui copie le lien laquelle des deux était le site.

→ Les **9 déploiements de `dev` sont supprimés** (l'alias répond 404), la page
porte un `canonical` vers `https://mon-benin.pages.dev/`, et le CONTEXT dit de
ne plus jamais fabriquer une deuxième adresse en ligne pour essayer : le QC et
un serveur local sont là pour ça.

⚠️ **Leçon déjà apprise sur Angy Art, repayée aujourd'hui** : ma première
mesure du rideau annonçait **5,8 s** avant le bouton d'entrée. Faux. Les
captures et les `evaluate` empilés dans la boucle **ajoutaient eux-mêmes le
retard qu'ils prétendaient mesurer**. Le vrai chiffre, lu dans la Navigation
Timing de la page : DOMContentLoaded à **1,2 s**, bouton à **2,2 s**.

## 8. Les images de Béninéo, et pourquoi elles ne sont pas en ligne

Mongazi en a envoyé sept dans la conversation. **Elles n'existent nulle part
sur le disque** : vérifié dans `_partage/`, Téléchargements, Bureau, Images,
Documents, et par une recherche de tout fichier image modifié aujourd'hui.
Zéro. Une image qu'on regarde dans une conversation n'est pas un fichier.

J'ai aussi ouvert son Drive : le document **« Mon bénin apport »** (créé le
2026-08-11 à 14 h 13) contient **les quatre textes et aucune image** (export
`.docx` : pas de `word/media/`).

**→ La marche à suivre proposée : ajouter les photos DANS ce document.** Une
image posée dans un Google Doc y est vraiment, et l'export `.docx` la rend à sa
taille d'origine. Mongazi n'a pas à toucher au PC.

## 9. Béninéo n'est pas un photographe, c'est une agence

Trouvé sur `benineo.com` : **agence de tourisme 100 % béninoise**, circuits
culturels et mémoriels, conciergerie, coffrets cadeaux **EbunBox**, boutique de
souvenirs. Signature : « Le monde commence au Bénin ».

- **Instagram : `@mybenineo`** ✅ confirmé sur leur propre site (le blocage
  saute) · Facebook `/mybenineo` · TikTok `@mybenineo` · LinkedIn `/benineo`
- WhatsApp : **+33 6 46 39 66 46** (numéro français)

**Ça change la conversation à avoir avec eux.** Ils vendent exactement ce que
Mon Bénin donne envie d'acheter : eux ont les images, les circuits et
l'audience, Mongazi a la vitrine qui fait rêver du pays. C'est un **échange**,
pas une faveur, et ça vaut mieux qu'un crédit en pied de page : c'est la
**première halte naturelle** du site.

⚠️ **Rien de Béninéo n'est publié**, et c'est volontaire : les huit photos en
ligne sont celles de Wikimedia. Créditer Béninéo pour des images qui ne sont
pas les siennes serait faux. Il faut **son accord écrit** avant toute mise en
ligne.

## L'état à la fin de la journée

**116 contrôles verts, 0 échec.** Une seule adresse : **https://mon-benin.pages.dev**.
