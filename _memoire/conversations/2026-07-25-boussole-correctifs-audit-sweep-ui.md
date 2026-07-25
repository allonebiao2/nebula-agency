# 2026-07-25 — Boussole proto : correctifs d'audit (perf/vitesse) + sweep UI mobile & PC

## Demande
Appliquer les améliorations pour **chaque point de l'audit**, surtout **perfs et vitesse d'utilisation**, et vérifier **boutons qui débordent / mal placés** et **onglets-feuilles mal cadrés ou inaccessibles**, sur **PC et mobile**.

## Correctifs des 5 points d'audit
1. **Transitions 1×/session** (`_fxSeen`) : ticket, portefeuille, flèche, calibration jouent en plein format à la 1re visite de la session ; ensuite l'écran s'affiche **instantanément**. La caisse garde son rituel mais passe en **MODE ÉCLAIR** (`.vault.is-fast`, 60/320/760 ms au lieu de 140/660/1500) — le plaisir reste, l'attente disparaît.
2. **Animations du tiroir en pause quand il est fermé** : `.app:not(.menu-open) .drawer .navbtn--holo{,::before,svg} { animation-play-state: paused }` — 3 animations infinies tournaient en permanence hors écran.
3. **Shimmer du titre à l'entrée seulement** : `#view.vw-enter .screen__title` (classe posée par `showSection`, retirée à 2,1 s) — plus de rejeu à chaque re-rendu interne.
4. **`countUpNums` durci** : découpage par regex `^([^\d]*)([\d\s\u00A0\u202F]+)(.*)$` (préfixe/chiffres/suffixe) au lieu du parsing fragile par `search`.
5. **PIN v2** : `pinHash` FNV-1a double passe salée (préfixe `v2`) + **`pinOk()` rétro-compatible** (les codes posés avec l'ancien hash continuent de marcher — vérifié en QC).

## Bugs UI trouvés par le sweep (et corrigés)
- 🔴 **FAB « Nouvel article » HORS de l'écran sur le Catalogue** (mesuré `top: 939` pour une hauteur de 844) : `.screen.drawer3d` gardait un **transform résiduel** (fill-mode `both` → matrice identité), ce qui faisait de l'écran le **containing block** des éléments `position: fixed`. Double correction : (a) `both` → **`backwards`** sur `.screen.cine/.hud/.drawer3d` (aucun transform résiduel, rendu identique) ; (b) l'animation `drawerPull` est déplacée sur un **conteneur interne `.drawer3d`**, plus jamais sur `.screen` — le FAB ne dépend plus de l'animation, même pendant les 450 ms.
- 🔴 **Débordement horizontal de 10-15 px sur l'Accueil** : seul `body` avait `overflow-x: hidden`, le dépassement remontait au viewport → **`html { overflow-x: hidden }`**. Mesure : 15 px → **0 px**.
- 🟠 **Feuilles pleine largeur sur PC** : `@media (min-width: 1024px)` → carte **centrée de 560 px max**, arrondie, à 22 px du bas (au lieu d'une barre collée sur toute la largeur de l'écran).
- 🟠 **« Enregistrer » et « Supprimer » du même rouge** (risque de clic destructif par erreur) : `.sheet__add` passe en **or ambre** (action primaire = identité Boussole), le rouge reste réservé au destructif.

## QC
`qc_v9.js` — sweep **12 écrans × 2 viewports (390 et 1280)** : débordement, position du FAB, 4 feuilles (vente, période stats, changement de caisse, objectifs) cadrées + boutons atteignables, pastille d'alertes dans son onglet, + les 5 correctifs de perf. **24/24 verts, 0 erreur JS.**
Non-régression totale : v8, v7, v6, v5, v4 **tous verts** (113 vérifications cumulées).

Cf [[2026-07-25-boussole-salutations-v2-sons]].
