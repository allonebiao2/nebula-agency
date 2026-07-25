# 2026-07-25 — Boussole proto : caisse-coffre 3D + coûts détaillés par produit (« qui prend quoi »)

## Demande de Mongazi
1. La caisse doit s'ouvrir comme un **coffre/sac qui révèle les produits**, et les tuiles produits/services doivent être **3D et stylées** (plus le simple disque plat).
2. Sur un produit/service, pouvoir **décomposer le coût en éléments nommés** qui se déduisent du revenu — ex. vitrine digitale + QR code vendue : 10 000 F à remettre au partenaire, 5 000 F d'hébergement — avec **% calculés automatiquement**.

## 1 — Caisse théâtrale
- **Transition coffre** à chaque entrée : 2 portes métal sombre à liseré riveté or + **roue de coffre SVG** qui tourne (~0,55 s, son `playDrawerPull`), puis les portes pivotent (`rotateY ±96°`, perspective 900) et se dissipent ; les tuiles attendent (`animation-play-state: paused` via `.is-sealed`) puis **jaillissent en 3D** (stagger `tilePop3d` : rotateX 32°→0). Reduced-motion : coffre masqué, tuiles directes.
- **Tuiles 3D** (`--tc` = couleur du produit, injectée inline) : fond bi-couche verre/nuit, bordure et lueur teintées par produit, **reflet vitrine** en diagonale (::before), **pastille sphérique** en vrai relief (reflet haut + ombre interne + ombre portée colorée), **prix en pastille de verre** vert, `transform-style: preserve-3d` ; au survol PC la tuile **s'incline** (rotateX/Y) et la sphère **sort en Z** (translateZ 22px) ; :active = enfoncement 3D. Le builder de factures en profite aussi (même classe).

## 2 — Coûts détaillés (« qui prend quoi »)
- **Modèle** : `p.couts = [{nom, montant}]` (optionnel) ; `p.cout` = somme des postes quand ils existent (rétro-compat totale : sans postes, coût simple inchangé).
- **Feuille catalogue** : section « Détail du coût — qui prend quoi » → lignes nom + montant + **% du prix de vente auto** + ×, bouton « + élément », **total auto** ; le champ « Coût / achat » passe en lecture seule (somme) dès qu'il y a des postes ; la **marge se recalcule en direct** (prix modifié ⇒ % re-calculés).
- **Carte catalogue** : « coût 15 000 F (2 postes) ».
- **Détail de vente** : bloc **« À réserver sur cette vente »** = agrégat des postes des articles vendus (montant × qté) + **Total à réserver** + **« Ce qui te reste vraiment »** (total − postes). C'est la réponse directe au cas vitrine : le commerçant sait quoi tirer et remettre au partenaire.
- La vente capturait déjà `sale.cout` (somme) → enveloppes/marges cohérentes automatiquement.

## Détails techniques
- CSS : `.vault*` (portes/roue/états is-turning/is-open/is-gone), `.pos-tile` réécrit (preserve-3d, --tc, sheen, sphère), `.csplit/.cline*` (éditeur de postes), `.vresa*` (bloc à réserver).
- `bindCaisse` : séquence 140 ms (roue+son) → 660 ms (portes+release tuiles) → 1500 ms (gone).
- `bindStock` : `curCouts[]`, `renderClines/syncCout/updPcts`, save = filtre postes >0, `delete p.couts` si vide.

## QC
`qc_v5.js` : **19/19 verts, 0 erreur console** (séquence du coffre en 3 temps, --tc/preserve-3d/pastille, coût auto 15 000 verrouillé, % 20/10, marge 70 %, sauvegarde+réédition+retrait de poste, vente → À réserver Partenaire 10 000 + Hébergement 5 000 + reste 35 000). Non-régression `qc_v4.js` : tout vert.

Cf [[2026-07-25-boussole-vague-logiciel-v4]].
