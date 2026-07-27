# 2026-07-25 — Boussole : VAGUE 2 des transitions — une mise en scène par item du menu

## Demande
« Des animations de transition pour chaque item du menu, **adaptées à leur rôle** » — idées proposées puis **tout validé**, y compris le fil rouge et le remplacement du tiroir 3D du catalogue.

## Le fil rouge : l'icône du menu s'envole
`flyIcon(btn)` : au clic sur une entrée du tiroir, **son icône est clonée**, positionnée en `fixed` à sa place exacte, puis projetée vers le centre de l'écran en grandissant (×4,2) avant de se dissoudre (580 ms). Un seul mécanisme, mais **différent pour chaque item puisque chaque icône diffère** — ça relie enfin le menu à l'écran qu'il ouvre. `pointer-events: none`, auto-nettoyée.

## Les 8 mises en scène
| Écran | Mise en scène | Détail |
|---|---|---|
| **Bilan** | **Électrocardiogramme** | Un tracé ECG orange se dessine (`stroke-dashoffset`) + point lumineux au battement. **Le tracé encode le résultat** : régulier si le score >= 60, irrégulier et saccadé sinon — on comprend avant de lire le chiffre. |
| **Statistiques** | **Constellation** | 7 étoiles s'allument en cascade puis une polyligne les relie. Sons : scan de données + validation analytique. |
| **Mes produits** | **Podium** | Les 3 premières lignes montent à des hauteurs et vitesses différentes, éclat qui balaie la 1re. L'animation **encode le classement**. |
| **Carnet clients** | **Répertoire feuilleté** | 3 pages tournent en 3D depuis la gauche (`rotateY -125°`, origine à gauche) avec froissement. |
| **Factures & devis** | **Tampon** | Un sceau descend, **frappe** (scale 2,6→1, rotation −14°) et l'écran tremble 2 fois + loquet mécanique + vibration. |
| **Mon équipe** | **Badges scannés** | Chaque membre glisse depuis la gauche avec un **trait de scan vert** qui balaie la carte. |
| **Réglages** | **Engrenages** | Deux roues dentées arrivent, s'engrènent, font un quart de tour synchronisé, puis s'écartent. Double « clac ». |
| **Catalogue** | **Étagère** *(remplace le tiroir 3D)* | Les produits tombent et se posent un à un, avec une ligne d'étagère qui apparaît sous chacun. Plus parlant que le tiroir générique. |

## Garde-fous respectés
`transform`/`opacity` uniquement · calques `.fx-layer` **non bloquants** et auto-nettoyés (1,2–2 s) · **1× par session** (`_fxSeen`) puis affichage instantané · `_entryFx` consommé donc **aucun rejeu au re-rendu interne** · tout coupé en `prefers-reduced-motion`.

## Effet de bord corrigé
En supprimant `.drawer3d` du catalogue, la carte d'un produit nouvellement créé se retrouve **hors écran** (top 1111 px) dans le test : l'ouverture de la fiche fonctionne (vérifié à la main), c'est le QC qui devait scroller → `scrollIntoViewIfNeeded` ajouté dans `qc_v5`.

## QC
`qc_v12.js` : **21/21 verts du premier coup** — icône projetée (nom d'animation + décalage calculé + non bloquante + nettoyée), les 8 scènes présentes à la 1re arrivée, **aucun calque résiduel**, **aucun rejeu** à la 2e visite (répertoire, podium, badges), ECG vérifié sur session neuve, et **mouvement réduit = tout coupé mais l'écran s'affiche**.
Non-régression **v4 → v11 : toutes vertes**, 0 erreur console.

Cf [[2026-07-25-boussole-identite-orange-nuit]], [[2026-07-25-boussole-transitions-vague1]].
