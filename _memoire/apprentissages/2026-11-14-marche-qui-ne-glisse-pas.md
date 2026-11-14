# Une marche qui ne glisse pas (three.js + animations Mixamo)

> LE MONDE, 2026-11-14. Mongazi : « la façon de marcher, tout, on doit tout revoir ». Outil de mesure :
> `monde/_outils/mesurer_marche.py`. Code : `monde/socle/habiller.js` (`mesurerMarche`) et `monde/socle/pnj.js` (`MARCHE`).

## Ce qui faisait faux, mesuré

| Défaut | Mesure | Correction |
|---|---|---|
| La cadence de l'animation était posée au jugé (vitesse / 1,2) | la marche d'Afi va en réalité à **0,80 m/s** : le pied posé glissait d'environ **34 cm/s** en permanence | mesurer la vitesse propre de la marche **sur les pieds**, puis `timeScale = vitesse réelle / vitesse propre` |
| Pleine vitesse dès la première image, arrêt net | | accélération 1,6 m/s², freinage 1,3 m/s² calculé sur la distance qui reste (`√(2·a·d)`) |
| Angles secs à chaque point du chemin | | cap limité à 2,4 rad/s en marchant, virage pris à 32 cm du point, droit sur le but dans les 35 derniers cm |
| Animations Mixamo « démarrer » et « s'arrêter » | ce sont **deux autres allures** (le départ finit à 1,3 m/s), leur avancée était retirée : **30 cm/s** de glissement | ne plus les jouer : sa propre marche accélère et freine, la cadence suit la vitesse |
| Le corps suivait le cap avec un lissage exponentiel | jusqu'à 37° de retard dans un virage | en marchant, le corps prend le cap tel quel (déjà adouci par la limite de rotation) |
| Les écartements (ne pas cacher Hillary, distance au visiteur, entre visiteuses) déplaçaient la position sous les pieds | le pied glissait de côté | en marchant : l'écart s'ajoute à la trajectoire, corps et cadence suivent le mouvement RÉEL ; immobile : un **pas de côté** marché, puis elle se retourne |

**Résultat** : patinage du pied posé à vitesse de croisière **9 cm/s en médiane, 12 cm/s au 90e centile**. Le
reste vient du pied qui pivote avec le corps dans les virages (20 à 35 cm/s) : sans IK des pieds, c'est la limite.

## Les pièges de la mesure (trois faux chiffres avant le bon)

1. **La hauteur ne dit pas quel pied est posé** : en pleine foulée, la cheville du pied en l'air rase le sol à la
   même hauteur que celle du pied posé. Le bon critère : dans chaque demi-foulée, le pied posé est **le plus lent**.
2. **Un `mixer.setTime(D)` sur une animation en boucle revient à 0** : la dernière mesure d'une courbe retombe.
   Échantillonner jusqu'à `D − ε`.
3. **Le point de départ du test compte** : faire partir la visiteuse sur la caméra la fait repousser (distance
   minimale au visiteur), et ces images faussent tout le début.

## Ce qui reste possible plus tard

- IK des pieds (le pied posé tenu au sol pendant le pivot du corps) pour les virages.
- Départ et arrêt en animation **avec leur avancée propre** (le corps mené par le bassin de l'animation), à
  condition d'avoir un départ et un arrêt de **la même allure** que la marche.
