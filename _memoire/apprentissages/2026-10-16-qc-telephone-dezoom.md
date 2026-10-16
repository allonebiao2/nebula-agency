# Contrôler une page au téléphone : trois pièges de Playwright (2026-10-16)

Trouvés sur la page d'accueil de MA LETTRE À… (`malettre/_qc_accueil.py`).

## 1 · Au téléphone, un débordement ne déborde pas : il dézoome

En émulation `is_mobile`, un élément plus large que l'écran **élargit la
fenêtre de mise en page** : le navigateur dézoome toute la page pour le faire
tenir. `innerWidth` passe de 390 à 597, et `scrollWidth <= innerWidth` reste
**vrai**. Un contrôle de débordement écrit ainsi ne peut rien voir.

```js
// juste : comparer à la largeur DEMANDÉE
Math.max(document.documentElement.scrollWidth, innerWidth) <= 390
```

Les deux coupables du jour :
- un `<input>` sans largeur garde sa largeur naturelle (`size` 20 par défaut,
  soit ~440 px en police manuscrite de 30 px), même avec `flex:1;min-width:0` :
  son parent flex prend cette largeur comme minimum. Remède : `width:0;
  flex:1 1 0` sur l'input, `min-width:0` sur le parent.
- un état caché qui **agrandit** (`scale(1.25)` avant une révélation) compte
  dans le débordement tant qu'il n'est pas révélé. Remède : couper la section
  sur son bord (`overflow-x:clip`, repli `hidden`).

## 2 · La capture d'élément ment au téléphone

`locator.screenshot()` refait défiler la page avant de photographier. Pour une
sonde de contraste, le fond a été mesuré **une section à côté** (titre sur
papier mesuré sur la nuit). Et `page.screenshot(clip=…)` prend des
coordonnées de document, pas d'écran. Ce qui marche : `scrollIntoView`, relire
le rectangle, `page.screenshot()` de l'écran entier, découper en Python, et
jeter la mesure si `scrollY` a bougé entre-temps.

**Toujours un témoin** : un gris sur gris injecté doit échouer, un fond connu
doit être lu. Sans eux, la sonde a menti trois fois avant d'être vue.

## 3 · `clock.install()` ne fige pas le temps

Après `page.clock.install()`, le temps **continue de couler** tant qu'on n'a
pas appelé `pause_at`. Une capture « avant l'animation » montrait l'animation
finie. Pour photographier une suite de transitions CSS instant par instant :

```js
el.classList.add('etat-suivant');
document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; });
```

Chaque transition devient une animation qu'on place à `t` millisecondes, délai
compris : aucune course contre la montre.

## 4 · Un repli de mouvement réduit perd contre une règle plus précise

```css
.js .billet[data-rv]:not(.vu){opacity:0}            /* plus spécifique */
@media(prefers-reduced-motion:reduce){
  .js [data-rv]:not(.vu){opacity:1}                 /* perd */
}
```

Le repli doit nommer **chaque** sélecteur qui cache quelque chose. Contrôle :
en `reduced_motion="reduce"`, compter les éléments d'opacité < 1 sans défiler.
