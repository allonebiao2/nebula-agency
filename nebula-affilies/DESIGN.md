# NEBULA Affiliés — charte visuelle

> Comment ça se présente. Le « pourquoi » et le « pour qui » sont dans `PRODUCT.md`.
> Écrit le 2026-08-03 pour la refonte « lisible pour un débutant ».

## Le parti pris

**Un outil de travail, pas une vitrine.** L'ancienne interface empruntait au site
public : verre dépoli partout, halos, orbes animés, dégradés. Sur un tableau de
bord, ce décor coûte deux fois — il ralentit l'appareil, et il noie l'information.

On garde l'identité NEBULA (le violet, le fond nocturne, le logo) et on lui retire
son maquillage. Le verre devient rare et intentionnel : les feuilles qui glissent,
rien d'autre.

## Thèmes

**Deux, au choix de la personne** (décision Mongazi). Sombre par défaut, clair d'un
clic, mémorisé. Le clair n'est pas décoratif : il existe pour le téléphone en plein
soleil à Cotonou.

| Jeton | Sombre | Clair | Rôle |
|---|---|---|---|
| `--bg` | `#0b0b12` | `#f7f7fa` | le fond de la page |
| `--surface` | `#141420` | `#ffffff` | cartes, tableaux, panneaux |
| `--surface-2` | `#1c1c2b` | `#f0f0f5` | **la barre de navigation**, plus dense que le contenu |
| `--ink` | `#eceaf6` | `#16161f` | le texte courant |
| `--ink-2` | `#a5a3bd` | `#55536b` | le texte secondaire, ≥ 4,5:1 dans les deux thèmes |
| `--line` | `rgba(255,255,255,.09)` | `rgba(0,0,0,.10)` | les séparations |
| `--accent` | `#7b5cff` | `#6a45f5` | **actions principales, sélection, état — jamais décor** |
| `--accent-tx` | `#9b86ff` | `#5a35e0` | le violet quand il porte du **texte** (contraste) |
| `--ok` `--warn` `--bad` | `#36f5a0` `#f5b14c` `#ff5c7a` | `#0a8f57` `#a86a00` `#c8253f` | statuts |

⚠️ Les couleurs de statut changent **de valeur** entre les thèmes, pas seulement
d'opacité : un vert clair sur blanc est illisible.

## Typographie

Une seule famille, **Plus Jakarta Sans**, déjà chargée. Pas de police d'affichage
dans une interface de travail : les chiffres restent en **JetBrains Mono**, qui
aligne les colonnes.

Échelle **fixe en rem**, pas fluide : un tableau de bord se lit à la même taille
partout, et un titre qui rétrécit dans une colonne étroite fait moins bien, pas mieux.

| | |
|---|---|
| Titre d'écran | 1,35 rem / 600 |
| Titre de section | 1,05 rem / 600 |
| Texte courant | 0,94 rem / 400 |
| Secondaire, libellés | 0,82 rem / 500 |
| Chiffre de compteur | 1,6 rem mono / 700 |

Rapport de 1,15 entre les pas : il y a beaucoup d'éléments à l'écran, un contraste
trop marqué fait du bruit.

## Navigation

**Écrite.** Icône **et** mot, toujours. C'est le changement le plus important de la
refonte : une icône de coupe ou de sablier ne se devine pas.

- **PC** : colonne de 216 px à gauche, fond `--surface-2`, libellés visibles.
- **Téléphone** : barre en bas, **5 entrées maximum** avec leur mot sous l'icône,
  le reste dans « Plus ». Une barre de 12 icônes muettes qui défile n'est pas une
  navigation, c'est une devinette.

## Composants

**Le tableau plutôt que la pile de cartes.** Une carte par ligne oblige à dérouler ;
un tableau se lit en diagonale. Sur téléphone, le tableau devient une liste de
lignes à deux niveaux (titre + détail), jamais une grille qui déborde.

**Le compteur ne montre jamais un nombre seul.** Toujours accompagné de sa
comparaison (« +3 ce mois ») ou de son action (« 2 à payer → »). Un nombre sans
repère n'apprend rien.

**Les pastilles de statut** portent un mot, pas une couleur seule : un daltonien
doit lire « Payé », pas deviner un vert.

Chaque élément interactif a ses états : repos, survol, focus **visible**, actif,
désactivé, chargement. Squelettes au chargement, pas de tourniquet au milieu du
contenu.

**Les états vides enseignent.** « Aucun client pour l'instant » ne sert à rien ;
« Partage ton lien pour recevoir ton premier client », avec le bouton, oui.

## Mouvement

150 à 250 ms, et seulement pour dire un changement d'état. Pas de mise en scène au
chargement : on arrive ici pour travailler. Le mode performance adaptatif et
`prefers-reduced-motion` restent en place.

## Densité et cibles

Cibles tactiles **≥ 44 px** partout. Sur téléphone, les compteurs vont **par deux**,
jamais un par ligne. Marges intérieures de carte : 13-14 px sur téléphone, 18 px sur
PC.

## Ce qui est banni ici

- Le **verre dépoli décoratif** : réservé aux feuilles qui glissent.
- Les **halos et orbes animés** derrière le contenu.
- Le **dégradé sur du texte**.
- Les **icônes sans mot** dans la navigation.
- Le **jargon** : « Pipeline », « RCM », « palier » n'existent plus à l'écran.
