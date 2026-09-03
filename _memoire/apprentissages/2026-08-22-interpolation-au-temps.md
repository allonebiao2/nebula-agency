# Interpoler au TEMPS, jamais à l'image

*Trouvé le 2026-08-22 sur la vitrine d'Angy Art, en publiant.*

## Le symptôme

Cliquer « accueil » depuis le bas d'une page de 10 318 px ramenait bien en haut
sur téléphone et sur tablette, mais laissait la page à **284 px** sur
ordinateur. La valeur changeait à chaque essai : 467 px la fois d'avant.

## La fausse piste

Une position qui varie fait penser à une **course entre deux mécanismes**, ou à
une force extérieure qui interrompt le glissement. Le code contenait justement
une logique d'adoption des sauts venus d'ailleurs, écrite la veille : le
suspect idéal, et il était innocent.

## La cause

La boucle avançait **d'un cran fixe par image** :

```js
function boucle() {
  courant += (cible - courant) * 0.095;
  if (Math.abs(cible - courant) < 0.5) { courant = cible; anime = false; }
  window.scrollTo(0, courant);
  if (anime) requestAnimationFrame(boucle);
}
```

À 60 images par seconde, il reste `0,905^n` de la distance après `n` images :
le trajet est fini en **1,1 s**. À 30 images par seconde, il faut **plus du
double**. Le glissement n'était pas cassé : **il n'était pas fini** quand le
contrôle mesurait.

## Le correctif

```js
var dernier = 0;
function boucle(ts) {
  var dt = dernier ? Math.min(64, ts - dernier) : 16.7;
  dernier = ts;
  var k = 1 - Math.pow(1 - 0.095, dt / 16.7);   /* le même 0,095, au temps */
  courant += (cible - courant) * k;
  if (Math.abs(cible - courant) < 0.5) { courant = cible; anime = false; }
  window.scrollTo(0, courant);
  if (anime) requestAnimationFrame(boucle);
}
function lancer() { if (!anime) { anime = true; dernier = 0; requestAnimationFrame(boucle); } }
```

- `Math.pow(1 - k, dt / 16.7)` conserve **exactement la même courbe** à 60 Hz :
  on ne change pas le rendu, on le rend indépendant de la cadence.
- `Math.min(64, …)` : après un gel d'une seconde (onglet en arrière-plan, garbage
  collection), sans plafond la page **saute** d'un coup.
- `dernier = 0` à chaque lancement, sinon le premier `dt` vaut l'âge du dernier
  glissement.

## Pourquoi c'est vicieux

⚠️ **Le défaut se cache sur la machine qui le teste.** Ici le moteur maison ne
tourne que sur `(hover:hover) and (pointer:fine)` : aucun contrôle mobile ne
pouvait le voir. Or ce sont **les machines lentes** qui le subissent, c'est-à-dire
les téléphones bas de gamme de Cotonou, c'est-à-dire nos visiteurs.

## À appliquer sur le parc

```bash
git grep -n "requestAnimationFrame" -- '*.js' | cut -d: -f1 | sort -u
git grep -n "+= *(\|\* *0\.0" -- '*.js' | grep -v node_modules
```

Toute boucle `requestAnimationFrame` qui n'utilise pas `dt` est un candidat :
glissements, compteurs qui montent, révélations, curseurs suiveurs.
Voir aussi `_memoire/lecons.md` (2026-08-22) et la leçon jumelle sur les
mouvements qui « buguent » : une courbe qui part à plat, du travail lourd avant
le mouvement, deux horloges pour un geste.
