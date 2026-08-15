# 2026-08-15 · Prospectus « Fête de l'Igname » pour Grain d'Esthétique

## La commande

« Créer un prospectus dans son univers pour la fête de l'igname ici à Cotonou. »
Pas un prompt cette fois : **l'objet fini**.

## Ce qui a été livré

Un **A5 recto-verso** (148 × 210 mm), PDF pour l'imprimeur + deux PNG à 384 dpi pour
WhatsApp et les réseaux. Outils dans `clients/01-grain-esthetique/_outils/` :
`_build_prospectus_igname.py` puis `_render_prospectus_igname.py`.

## L'idée

**« La fête se prépare la veille. »**

C'est la seule phrase du prospectus qui fait le lien entre un institut de beauté et une fête
traditionnelle, et elle est vraie : on se retrouve, on s'habille, on se photographie. On ne
vend pas la fête, on vend la veille de la fête.

Le pont visuel est **l'or** : la fête de l'igname est une fête de récolte, dorée, et l'or
`#D4AF72` est déjà une couleur de la maison. Rien d'autre n'a été emprunté au registre
traditionnel, sauf **deux feuilles d'igname au trait**, dans le même style line-art que les
icônes de la vitrine. Un institut haut de gamme n'a pas à se déguiser pour parler d'une fête.

## Ce qui a failli partir à l'imprimeur

**Au premier rendu, le bas du recto était coupé : 44 mm de contenu hors page**, et 16 mm au
verso. Sur un écran on ne le voit pas, on voit une belle affiche. Sur 500 exemplaires payés,
on le voit tout de suite.

D'où le principe posé dans `_render_prospectus_igname.py` : **il n'écrit rien tant que tout
n'est pas vert.**

| Contrôle | Ce qu'il attrape |
|---|---|
| hauteur du contenu vs 210 mm, **et moins de 3 mm de marge = échec** | le bas coupé |
| largeur du contenu vs la zone utile | un titre qui déborde |
| présence des textes obligatoires | un numéro ou un domaine disparu |
| aucune apostrophe droite `'` | le `l'Igname` moche à côté du `l'esthétique` du logo |
| **le QR relu dans l'image finale** (OpenCV) | un QR juste à la fabrication et illisible au rendu |

Le QR a été relu depuis le PNG final : il rend bien `https://graindesthetique.com`.

## Deux détails techniques qui resservent

1. **Tout est embarqué en base64** : les 10 coupes de fontes (101 Ko), le logo, le QR. Un
   fichier d'impression ne doit dépendre d'aucun réseau, ni le jour où on le rouvre.
2. **Playwright installé par pip ne trouve pas le Chromium préinstallé** : il cherche un
   numéro de build qu'il n'a pas. On le pointe avec `executable_path` sur
   `/opt/pw-browsers/chromium-*/chrome-linux/chrome` au lieu de retélécharger.
3. Le logo n'existe qu'en **224 px de large**. Agrandi ×4 au Lanczos avec raidissement du
   canal alpha, il tient à 28 mm. Au-delà, il faudra le vectoriser.

## Ce qui reste à confirmer, et pourquoi ça compte

Le bloc **ZONE À CONFIRMER** en haut du script porte les deux seules choses que je ne
pouvais pas savoir :

- les **dates** (`Du 15 au 31 août 2026` est une proposition) ;
- les **quatre montants**, repris tels quels de la promo Fête des Pères que Jocelyne avait
  validée. Ce sont ses vrais prix, mais elle n'a jamais dit qu'ils s'appliquaient à cette
  occasion.

Changer l'un ou l'autre, c'est deux lignes en haut du script et une relance.
