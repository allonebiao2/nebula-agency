# 2026-07-25 — Boussole proto : signatures Vendre/Dépenser (accueil) + audit animations

## Demande
Analyser Boussole (erreurs / animations à améliorer) et donner aux 2 mastodontes de l'accueil une **animation propre à chacun, dans l'univers Boussole, avec l'effet de données qui va avec**.

## Signatures implémentées
- **VENDRE (émeraude)** : à l'effleurement et au toucher, **pluie de pièces d'or** (dégradé or, marquées « F », chute+rotation+rebond cubic-bezier 1.35) DANS le verre du bouton + **étiquette de VRAIE donnée** « +prix » (tiré au hasard du catalogue réel) qui **monte** en vert lumineux. Icône panier qui « pèse » toutes les ~4 s (idle).
- **DÉPENSER (rouge)** : **billets rouges** (médaillon central) qui **glissent vers le bas** en tournant + étiquette « −montant » (tirée des vraies dernières sorties) qui **descend** en rouge. Icône flèche qui « plonge » (idle décalé de celui du panier).
- **Au clic** : `is-fired` → **onde circulaire** de la couleur du bouton (scale 0.4→9) + brightness, **navigation retardée de 300 ms** (garde anti double-tir `data-firing`) pour voir la signature avant d'arriver à la caisse/dépenses. Vibration 15 ms.
- Particules éphémères uniquement (spawn à l'événement, fx vidé à 1,3 s, throttle survol 900 ms) ; les 2 seules anims infinies sont les micro-vies d'icônes (transform léger). `overflow:hidden` sur le bouton, reduced-motion coupe tout.
- `mastoData(sell)` = le pont « données » : prix réels du catalogue / montants réels des dépenses → le commerçant voit SON argent vivre sur les boutons.

## Audit réalisé (état + points à suivre)
- **Aucune erreur console/JS** sur les 4 suites QC (v4 45 + v5 19 + v6 14 + v7 11 = 89 checks verts).
- Points relevés (non bloquants, pour une passe future) :
  1. `countUpNums` : parsing suffixe fragile (fonctionne pour « F »/« % », à durcir si autres formats).
  2. Transitions de lieux rejouées à CHAQUE entrée d'écran (choix assumé) — si lassitude : jouer 1×/session sauf coffre.
  3. Anims infinies sur navbtn du tiroir (holo) : à borner si le tiroir s'agrandit (et c'est ce qui rend les clics Playwright « unstable » → toujours force:true dans les QC).
  4. `titleShine` rejoue aux re-rendus internes d'écran (mineur).
  5. PIN hash djb2 = dissuasif, pas cryptographique (proto ok, à remplacer par WebCrypto en prod).

## QC
`qc_v7.js` : **11/11 verts** (fx présents, 5 pièces, étiquette = vrai prix du catalogue vérifié dans le state, 5 billets, étiquette = vraie sortie, onde + accueil pendant l'onde puis coffre de la caisse, anims idle nommées). Non-régression `qc_v6` : tout vert.

Cf [[2026-07-25-boussole-transitions-vague1]].
