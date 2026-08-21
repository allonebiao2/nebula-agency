# 2026-08-21 — Angy Art : son vocabulaire, sa collection, et le moteur de défilement

## Ce que Mongazi a demandé

Un récapitulatif détaillé de la vision d'Angélique : la structure du menu, la
collection **ÉNERGIES**, les prix affichés, deux boutons d'appel.

> Le menu doit comporter les sections suivantes : **ACCUEIL, L'ARTISTE,
> COLLECTION, CRÉATIONS SUR MESURE, JOURNAL, CONTACT**
> La première est la collection **ÉNERGIES** (composée de 5 œuvres)
> Un bouton pour « **Découvrir les œuvres** » menant directement à la collection
> Un bouton en bas de page pour les « **Créations sur mesure** »

## Ce qui a été fait

### 1. Ses mots, pas les nôtres

Le menu devient `L'ARTISTE · LA COLLECTION · SUR MESURE · LE JOURNAL ·
CONTACT`, et les étiquettes des sections s'alignent dessus (`01 L'ARTISTE`,
`02 LE JOURNAL`, `04 LA COLLECTION`, `06 CRÉATIONS SUR MESURE`). Le contenu
n'a pas bougé : il a changé de nom, parce que c'est le sien.

⚠️ `ACCUEIL` n'est pas ajouté au menu : le logo tient déjà ce rôle, et six
entrées se cassent à 390 px. **À lui dire.**

### 2. Les deux boutons

- Le héros mène désormais aux **œuvres** (`DÉCOUVRIR LES ŒUVRES` → `#oeuvres`),
  plus à l'atelier. On découvre d'abord ce qu'elle vend.
- Un **second appel en bas de page** mène au sur-mesure. On découvre, puis on
  agit. Mesuré sur la photo : 7,5 à 10:1 selon la largeur.

### 3. La collection ÉNERGIES

La section porte le **nom de la collection avant son titre** : on sait dans
quoi on entre avant de voir les pièces. Le titre est sa phrase telle quelle :
*« Donner une forme à ce qui ne se voit pas. »*

⏳ **Deux manques, marqués en commentaire dans le HTML :**

1. **Son texte d'introduction.** Le nôtre est *provisoire* et n'assemble que
   les mots de son récapitulatif. Une ligne à remplacer.
2. ⚠️ **Elle annonce CINQ œuvres. Elle en a envoyé SIX.** Laquelle n'en fait
   pas partie ?

## Le défaut trouvé au passage : le défilement lissé écrasait tout le monde

Le QC échouait **uniquement en mode captures**. Diagnostic : les captures
laissent le moteur de défilement en pleine course, et le contrôle suivant se
faisait ramener en arrière.

Le moteur maison (`app.js`, l'équivalent de Lenis) ne relisait sa cible que
`if (!anime)` — **seulement à l'arrêt**. Pendant qu'il glissait, il réécrivait
`scrollY` à chaque image et annulait tout déplacement venu d'ailleurs : la
recherche du navigateur, un lecteur d'écran, la touche Fin, le passage au
clavier sur un bouton hors écran.

C'est la **troisième apparition** de cette famille (Lenis sur Au Braisé d'Or,
saut arrêté à 7 382 px de sa cible).

⚠️ **Le correctif naïf est pire que le défaut.** Adopter *tout* écart casse le
glissement : une image perdue laisse la page **sur le chemin** du moteur, et
l'adopter arrête net le défilement au milieu.

Le bon critère, c'est **où** :

```js
var bas = Math.min(courant, cible) - 12, haut = Math.max(courant, cible) + 12;
if (y < bas || y > haut) { cible = borne(y); courant = y; }
```

**Mesuré** : sans le correctif, un saut à 200 px est ramené à **5 992 px** ;
avec, la page reste à 200. L'épreuve a été faite en remettant l'ancien code.

## Quatre mesures qui mentaient parce qu'elles recopiaient

| Ce qui était recopié | Ce que ça a coûté |
|---|---|
| trois ancres de menu, dont `#portfolio` | le menu a changé → `null.click()`, le contrôle **plantait** au lieu de tester |
| les étiquettes `LA DÉMARCHE` / `L'ATELIER` / `DANS UN LIEU` | le contrôle a **accusé le site** d'avoir perdu des textes seulement renommés |
| les huit sélecteurs de `SECTIONS` | les **deux sections neuves n'ont jamais été photographiées**, et personne ne l'a vu |
| l'attente de 500 ms avant de mesurer un contraste | l'élément n'était pas à l'écran, et le contrôle criait au **défaut de contraste** |

Le pire est le troisième : les deux autres crient. Une liste de captures, elle,
**ne se plaint pas de ce qu'elle ne montre pas**. Huit images vertes pendant
que deux sections entières n'étaient jamais regardées.

Le quatrième est devenu `placer()` : on se place, **puis on vérifie qu'on y
est**, et si on n'y arrive pas on le dit **avec le chiffre**.

Ce qui reste écrit en dur, ce sont **ses phrases à elle** — celles-là ne
doivent jamais disparaître, quel que soit le vocabulaire du menu.

## Le contrôle du moteur a un témoin

« Le défilement lissé laisse passer les autres » prouve **d'abord que ça
glisse** (3 000 → 4 352 px), puis saute ailleurs. Sans le témoin, un moteur
mort passerait le contrôle : une page qui ne glisse pas ne ramène évidemment
rien. Même leçon que le contrôle de pause de Hillary, le 2026-08-18.

Contexte **PC uniquement** : le moteur n'existe que sur pointeur fin.

## Chiffres

- **129 → 146 contrôles**, tous verts, captures comprises.
- **10 sections photographiées** au lieu de 8.
- Captures regardées en **390 et 1440**, section par section.

## Fichiers touchés

- `clients/11-angy-art/index.html`
- `clients/11-angy-art/assets/app.css`
- `clients/11-angy-art/assets/app.js`
- `clients/11-angy-art/_qc.py`
- `clients/11-angy-art/CONTEXT.md`
- `_memoire/lecons.md`
- `CLAUDE.md`

## État

**Poussé sur `main`** (`8c959f9`, `081fcbe`) et sur
`claude/hillary-style-auto-switch-9ij9wz`. **Rien n'est déployé** — ni Angy, ni
Hillary, ni Au Braisé d'Or.

## Ce qu'il faut demander à Mongazi

1. ⚠️ **Quelles CINQ œuvres composent ÉNERGIES ?** (elle en a envoyé six)
2. **Son texte d'introduction de collection** (le nôtre est provisoire)
3. **« ANGYART » ou « Angy Art » ?** — demandé deux fois, sans réponse
4. Le **texte de la page L'ARTISTE**
5. Le **statut** de chaque pièce : vendue ou disponible
6. `ACCUEIL` dans le menu : le logo tient le rôle, faut-il le libellé ?
