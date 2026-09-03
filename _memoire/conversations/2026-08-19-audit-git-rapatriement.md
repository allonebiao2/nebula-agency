# 2026-08-19 · Audit git : trois chantiers dormaient hors de `main`

Mongazi : « REGARDES LES COMMIT LES PUSH ETC il faut tout commit et push ».
L'audit a trouvé bien plus que mes propres commits.

## Ce qui dormait

**18 branches `claude/…` sur le dépôt distant.** Trois portaient du travail
récent et fusionnable, jamais arrivé dans `main` :

| Branche | Ce qu'elle portait | Sort |
|---|---|---|
| `claude/hillary-style-auto-switch-9ij9wz` | **la bascule face/dos** des pièces photographiées des deux côtés, le héros qui prend TOUTES les nouvelles pièces en espaçant les teintes, et **trois bugs de `_nouveaux_modeles.py`** qui auraient fait détourer les photos sans jamais les raccrocher aux fiches. QC 121 → **138** | ✅ fusionnée et **déployée** |
| `claude/catalogue-braised-gold-ve5jwi` | 12 commits sur Au Braisé d'Or : carte relue contre le menu papier (52 → 42 plats), catégorie Sauces, vraies photos, prix exacts | ✅ fusionnée (une autre session l'avait aussi poussée dans `main` entre-temps) |
| `claude/nebula-carousel-post-5cp35d` | 4 911 lignes, **que des ajouts** : carrousels TikTok, statuts WhatsApp, et un **prospectus A5 imprimable pour Grain d'Esthétique** (PDF + recto/verso) | ✅ fusionnée |

## Ce qui dort encore, et qu'il faut trancher

Quatorze branches, de mai à août. Aucune n'est perdue, aucune ne se fusionne
en bloc : plusieurs sont très en retard sur `main` et ressusciteraient des
fichiers morts.

- **⛔ `claude/github-repo-context-nisd2r`** — 12 commits utiles (affiche
  « NOUS RECRUTONS », message de changement de barème) mais **la fusionner
  supprimerait 30 790 lignes de `main`**. À **cueillir commit par commit**,
  jamais à fusionner.
- `claude/le-greffier` · `claude/continuation-xu5ma7` · `claude/rare-paid-tools-ideas-w81ihh` ·
  `claude/nebula-quote-generator-kmr4i6` (tous du 2026-08-05) : produits et
  documents de vente, à relire avant de décider.
- `claude/nebula-agency-pricing-grid-4wnr2z` (12/08) : l'affiche des forfaits.
- `claude/protocole-boussole-memoire-9xy3j4` (27/07) : vague 2 des transitions Boussole.
- `claude/repo-discussion-analysis-g8qubx` (04/07) : HH Design en 3D immersive.
- Les branches vidéo et social de mai et juin : à archiver ou à cueillir.

## ⛔ LE DISQUE ÉTAIT PLEIN, ET ÇA S'EST VU COMME UNE PANNE DE GIT

Au milieu de la fusion : `unable to write file`, `index.lock write error`.
**0 octet libre sur 270 Go.** C'est la panne du 2026-08-10 qui revient.

Le cache npm pesait **1,8 Go** : `npm cache clean --force` a rendu 1,5 Go et la
fusion est passée. ⚠️ La fusion avortée avait laissé des fichiers à moitié
écrits qui bloquaient la reprise ; ils étaient **tous présents dans la branche**
(vérifié un par un avant de les effacer), donc `git clean` sur ces chemins était
sans risque.

## Deux fichiers se conflictent à chaque fois

`CLAUDE.md` et `_memoire/lecons.md` : deux sessions y écrivent en parallèle.
**La résolution est toujours la même : garder les deux apports.** Ici, la ligne
du client 09 vient de la session Braisé, celle du client 10 vient d'ici, et les
onze leçons (3 + 8) ont toutes été conservées.

## L'état à la fin

`main` porte tout. Hillary redéployée et **vérifiée au MD5** : ce qui est en
ligne est exactement ce qui est sur le disque, 281 947 octets, 138 contrôles.
