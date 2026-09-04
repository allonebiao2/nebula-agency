# 2026-09-04 — ANGY ART : un seul bouton « DÉCOUVRIR », et il ne quitte plus l'écran

**Demande de Mongazi**, mot pour mot : « concernant la vitrine de angy art je veux
que tout ces point ajouter se voit quand on clique sur un seul bouton, decouvrir,
et qui reste visible partout sur la page, surtout sur mobile ».

**Fait, en ligne, vérifié** : https://angy-art.pages.dev
`?v=20260904a` · **188 contrôles verts** (`python _qc.py`) · **22 verts**
(`python _audit.py`) · fichiers servis **identiques au disque en MD5**.

---

## Ce que c'était, et pourquoi ça ne suffisait pas

Le 2026-08-27, Angélique avait demandé de remplacer le bouton unique du héros par
un **sommaire de six entrées** : sur téléphone, elle veut voir d'un coup d'œil ce
que le site contient, et le burger anonyme ne le lui dit pas.

Le sommaire faisait ce travail **au bas du héros, et nulle part ailleurs**. Passée
la première section, il n'existait plus : il ne restait que le burger, c'est-à-dire
exactement ce dont elle se plaignait. **Ce n'est pas la liste qui manquait, c'est sa
présence.**

## Ce qui est en place

**Un seul contrôle, deux places, jamais deux à l'écran.**

- **Dans le héros** : une pastille crème « DÉCOUVRIR », **dans le flux** (le héros
  est une colonne flex), à la place exacte du sommaire.
- **Dans la barre** : la même, en pilule, à **toutes les largeurs** — elle remplace
  le burger, qui n'avait pas de nom.
- **Le bouton de la barre s'efface tant que celui du héros est à l'écran** et prend
  le relais dès qu'il en sort (`IntersectionObserver`, seuil 0). Mesuré à 390 px :
  le bouton du héros est **sous la ligne de flottaison** à l'arrivée, donc c'est
  celui de la barre que la visiteuse voit tout de suite. Sur ordinateur c'est
  l'inverse. Dans les deux cas : **un, et un seul**.

**Ce qu'il ouvre** : un panneau à droite qui porte **le sommaire d'Angélique,
entier**, avec ses formules : ACCUEIL · L'ARTISTE · **DÉCOUVRIR LES ŒUVRES** · LE
JOURNAL · **DANS UN LIEU** · **CRÉATIONS SUR MESURE** · CONTACT · ÉCRIRE SUR
WHATSAPP.

⚠️ **Les deux listes ont fusionné.** La barre portait des libellés **raccourcis**
(« LA COLLECTION », « SUR MESURE ») parce qu'elle débordait à 1024 px avec les vrais,
et il lui manquait « DANS UN LIEU ». Dans un panneau la contrainte de largeur tombe :
ses formules complètes reviennent, et rien n'est perdu au passage.

## ⚠️ Pourquoi la barre, et pas une pastille flottante

Une pastille flottante en bas d'écran serait plus proche du pouce. Elle est
**interdite** : un instrument flottant ne recouvre jamais du texte (règle née sur
Mon Bénin), et ce site l'a **payé le 2026-08-27**, quand le bouton du son se posait
sur « DÉCOUVRIR LES ŒUVRES » — 11 × 34 px, à 390 px et nulle part ailleurs.

**La barre du haut est la seule chose de ce site qui ait le droit de passer devant
une phrase**, parce que c'est une bande de bord **vraiment opaque** (mesurée par
`_audit.py` depuis le 2026-08-26). Le bouton y va donc, et le couloir réservé au
bouton du son reste réservé.

## ⛔ Trois défauts vus SUR LES CAPTURES, pas dans le code

Le QC était **vert** avant de les trouver. Ils ont été trouvés en regardant
`_vues/dec-*.png` (nouveau script `_vue_decouvrir.py`, six images : héros, panneau
ouvert, barre en cours de page, en 390 et 1440).

1. ⛔ **Le panneau recouvrait le bouton qui venait de l'ouvrir** : plus **aucune
   croix** à l'écran, aux deux largeurs. Le panneau est un **enfant de la barre**,
   donc son `z-index:1` se compte **à l'intérieur** de la barre, et il passait
   devant un frère sans `z-index`. → `position:relative; z-index:2` sur le bouton.
   ⚠️ **Même famille que la leçon Hillary du 2026-08-21** (« il change de parent,
   pas de style ») : un empilement se lit dans son contexte, jamais dans l'absolu.
2. ⛔ **« DEMANDER UNE VISITE » était coupé en deux** par le bord du panneau
   (« DEM… ») : elle se retire tant que le panneau est ouvert, et elle est de toute
   façon à un doigt dans le panneau, sous CONTACT.
3. ⚠️ **Le premier lien portait un cadre de focus au simple toucher** : le focus
   allait sur `ACCUEIL`. Il va maintenant **sur le panneau** (`tabindex="-1"`), qui
   n'a pas à désigner une entrée ; pour qui tabule, le premier lien vient au coup
   suivant.

## Ce qui a été tenu au passage

- **Sans JavaScript**, le bouton **se retire** (il n'ouvrirait rien), le panneau
  redevient la **rangée de liens** de la barre — qui se replie sur plusieurs lignes
  à 390 px — et **la barre cesse de flotter** (`position:static`) : son fond n'arrive
  qu'au défilement, par le script, et une bande translucide devant du texte est
  précisément ce que la maison s'interdit. Trois contrôles le vérifient.
- **Au clavier** : le reste de la page devient **inerte** pendant que le panneau est
  ouvert (sinon la tabulation sort vers des liens qu'on ne voit pas — leçon Hillary
  du 2026-08-25), Échap referme, et **le focus revient sur le bouton qui a ouvert**.
- **Le voile** est en `pointer-events:none` quand il est fermé, dans le même état
  que son opacité — jamais une `visibility` qui bascule à la fin de la transition
  (chez Hillary, le voile avalait les clics **350 ms après sa fermeture**).
- **Le panneau est centré par des marges automatiques, pas par
  `justify-content:center`** : le résultat est le même tant que ça tient, mais quand
  ça déborde une marge automatique retombe à zéro, là où `center` **coupe le début**
  d'un conteneur qui défile et le rend inatteignable.

## Les contrôles : 150 → 188

Trente-huit contrôles neufs, dont **trente aux trois largeurs** :

- **il y a TOUJOURS un bouton visible**, et **JAMAIS deux** — en haut, au milieu, en
  bas de page. ⚠️ **Les deux moitiés sont nécessaires** : le premier contrôle seul
  laisserait passer deux boutons affichés ensemble, le second seul laisserait passer
  une page qui n'en a plus aucun.
- les **deux boutons portent le même nom** (lu dans la page, pas recopié) ;
- le panneau **s'ouvre depuis le bas de page** — là où le sommaire n'existait plus ;
- **les 8 points se voient TOUS** : mesuré en boîtes réellement dans la fenêtre, et
  refus d'un panneau qu'il faudrait faire défiler pour lire ;
- la page derrière est **inerte**, Échap referme, **le focus revient au bouton** ;
- **sans JS** : les 8 entrées restent atteignables, le bouton se retire, la barre ne
  flotte pas.

⚠️ **Le contrôle du couloir du bouton du son a suivi** : il visait `.hero-plan a`,
qui n'existe plus. Un contrôle qui décrit un élément disparu ne protège plus rien et
fait croire qu'il veille (même remarque que le 2026-08-27). Il vise `.hero-dec`.

## Fichiers touchés

`clients/11-angy-art/index.html` · `assets/app.css` · `assets/app.js` · `_qc.py`
· **nouveau** `_vue_decouvrir.py` · captures dans `_vues/dec-*.png`.

`?v=` **bumpé sur la feuille et le script seulement** (`20260826a` → `20260904a`) :
les images n'ont pas changé, et leur marque de version sert à forcer un
rechargement qui n'a pas lieu d'être.

## Publication

```bash
python clients/11-angy-art/_qc.py          # 188 verts
python clients/11-angy-art/_dist.py        # 37 fichiers, 4,67 Mo
wrangler pages deploy clients/11-angy-art/_dist --project-name=angy-art --branch=main
```

Vérifié en ligne avec un vrai `User-Agent` : `app.css` et `app.js` **identiques au
disque en MD5**, `index.html` porte les deux boutons et le nouveau `?v=`, plus
**aucune trace de `hero-plan`**, un fichier absent répond **404**.

---

# Second temps du 2026-09-04 — la barre redevient visible, le bouton flottant s'ajoute

**Demande de Mongazi**, après avoir vu la version du matin en ligne : « il y avait
directement tout qui était visible, remets ça ».

`?v=20260904b` · **209 contrôles verts** · déployé et vérifié.

## Ce qui était faux dans la version du matin

Le bouton unique avait **remplacé** les liens de la barre par un panneau à ouvrir.
La demande d'Angélique (« voir d'un coup d'œil ce que le site contient ») venait de
son usage **téléphone**, et la réponse l'avait appliquée **à toutes les largeurs** :
sur ordinateur, où la place ne manque pas, on avait retiré une navigation qu'on VOIT
pour la remplacer par une navigation qu'on OUVRE. Un geste de plus pour tout le monde,
pour résoudre un problème qui n'existait que sur petit écran.

⚠️ **Une contrainte de téléphone ne se généralise pas à l'ordinateur.** C'est la même
famille que « la barre portait des libellés raccourcis faute de place à 1024 px » :
la place disponible fait partie du problème, pas seulement le libellé.

## Ce qui est en place

- **la barre retrouve ses 6 entrées + WhatsApp**, le burger reste sur téléphone ;
- **le sommaire du héros revient** (6 entrées, dans le flux) ;
- **le bouton flottant s'AJOUTE au lieu de remplacer** : il ouvre le même panneau,
  à toutes les largeurs. Trois portes, trois habitudes, un seul mécanisme — ouvrir
  l'une referme l'autre, et chacune gèle ce qui n'est pas elle (sinon une tabulation
  sort du panneau vers des liens qu'on ne voit pas) ;
- ⚠️ **les deux instruments flottants partagent UN couloir réservé, pas deux**
  (règle née sur Mon Bénin, payée le 27/08 avec le bouton du son posé sur
  « DÉCOUVRIR LES ŒUVRES ») ;
- **sans JS** le bouton flottant se retire au lieu de ne rien faire, et la barre
  cesse de flotter.

## ⛔ La leçon de contrôle : un recouvrement se CALCULE, il ne s'échantillonne pas

Premier jet du contrôle « le bouton flottant ne vole aucun clic » : faire défiler la
page par paliers de 400 px et comparer les boîtes à chaque palier. Il a trouvé trois
cibles, on les a réservées, **il est passé au vert — et il en restait une** :
« ÉQUIPER UN LIEU », **54 px de recouvrement à 390 px**.

Elle ne tombait simplement sur aucun palier. La fenêtre de défilement où elle croise
le bouton fait **102 px** ; un pas de 400 la manque **quatre fois sur cinq**.

**Un contrôle qui dépend de l'endroit où l'on regarde n'est pas un contrôle.**

Le remède : le bouton est **fixe**, la cible **défile**. On résout donc l'intervalle
de défilement où les deux se croisent, et on le compare à ce que la page permet.
Exact, instantané, et sans faire bouger la page. ⚠️ On écarte ce qui ne défile pas
(un ancêtre en `position:fixed` ne passera jamais sous le bouton).

Même famille que les leçons du 20/08 (les pastilles mesurées pendant leur transition)
et du 18/08 (« on échantillonne au lieu de comparer deux instantanés ») : ici c'est
l'inverse qui vaut, **quand la géométrie est calculable, on la calcule**.

## ⚠️ Le `?v=` n'avait pas été bumpé

La feuille et le script avaient changé de 307 et 107 lignes, et gardaient
`?v=20260904a` — la marque **déjà servie le matin avec l'ancien contenu**. Nos assets
portent `immutable` pour un an : tous ceux qui avaient ouvert le site dans la matinée,
**Mongazi le premier**, auraient gardé l'ancienne version. Bumpé en `20260904b`.

C'est le défaut du 2026-08-08 à l'identique (« Mongazi voyait encore l'ancienne image
alors que le serveur envoyait la vraie ») : **le cache du navigateur ne se voit pas
depuis le serveur**, et un QC vert ne le dit pas non plus.

## Fichiers touchés

`clients/11-angy-art/index.html` · `assets/app.css` · `assets/app.js` · `_qc.py`
· `_audit.py` · `_vue_decouvrir.py`.
