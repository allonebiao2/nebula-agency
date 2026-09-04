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
