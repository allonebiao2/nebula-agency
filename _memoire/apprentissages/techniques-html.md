# Techniques HTML / CSS découvertes

> Techniques concrètes qui marchent pour les vitrines NEBULA (HTML pur + CSS inline + base64).
> Une technique = un problème résolu, avec un bout de code prêt à réutiliser.

---

## Format

```
## Titre — quand l'utiliser

**Problème** : ...
**Solution** :
```html
<!-- exemple de code -->
```
**Notes** : pièges, perfs, compat mobile
```

---

## Images en base64

**Problème** : Les images en lien externe (Google Drive, Imgur, etc.) cassent ou ralentissent. NEBULA exige du 100% autonome.

**Solution** : Encoder chaque image en base64 et l'inliner directement.

```html
<img src="data:image/webp;base64,UklGRiI..." alt="..." />
```

**Notes**
- Toujours compresser AVANT d'encoder (WebP idéal)
- Au-delà de ~200 ko par image, vérifier que le poids total reste raisonnable
- Compatible 100% navigateurs

---

## CTA WhatsApp sticky mobile

**Problème** : Le visiteur mobile veut écrire en 1 tap, sans scroller.

**Solution** : Bouton flottant fixe en bas à droite.

```html
<a class="wa-fab" href="https://wa.me/229XXXXXXXX?text=Bonjour" target="_blank" rel="noopener" aria-label="Discuter sur WhatsApp">💬</a>

<style>
.wa-fab {
  position: fixed; right: 16px; bottom: 16px;
  width: 56px; height: 56px; border-radius: 50%;
  background: #25D366; color: #fff;
  display: flex; align-items: center; justify-content: center;
  text-decoration: none; font-size: 28px;
  box-shadow: 0 6px 18px rgba(0,0,0,.18);
  z-index: 999;
}
</style>
```

**Notes** : Vérifier qu'il ne masque pas un élément critique (formulaire, footer).

---

## Audio Web Audio API — effets + ambiance (zéro fichier externe)

**Problème** : mettre du son sur une vitrine sans MP3 ni CDN (règle NEBULA).
**Solution** : générer tous les sons par oscillateurs Web Audio API.

- `AudioContext` créé une fois ; **toujours** appeler `ctx.resume()` au 1er geste
  utilisateur (`click`/`touchstart`/`keydown`) sinon le navigateur bloque le son.
- Un son = oscillateur + gain avec enveloppe (`exponentialRampToValueAtTime`).
- Glissando (swoosh) : `frequency.exponentialRampToValueAtTime`.
- Musique d'ambiance : notes aléatoires d'une gamme en boucle `setTimeout`, dans un
  `BiquadFilter` lowpass, gain global ~12 % avec fondu d'entrée.
- Câbler les effets par **délégation d'événements** sur `document` (`closest()`),
  pas listener par listener → un seul bloc réutilisable sur toutes les pages.

```js
const ctx=new (window.AudioContext||window.webkitAudioContext)();
function tone(freq,dur,type,vol){
  const t=ctx.currentTime,o=ctx.createOscillator(),g=ctx.createGain();
  o.type=type;o.frequency.value=freq;o.connect(g);g.connect(ctx.destination);
  g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.0001,t+dur);
  o.start(t);o.stop(t+dur+.03);
}
['click','touchstart','keydown'].forEach(ev=>
  document.addEventListener(ev,function u(){ctx.resume();
    document.removeEventListener(ev,u);},{once:true}));
```

**Notes** : implémenté en module `LCAudio` sur les 4 pages de Luxury Club 229.

---

## Dispatch d'images en base64 via script Python

**Problème** : intégrer beaucoup d'images dans des vitrines 100 % inline sans CDN.
**Solution** : script Python + Pillow.

- Redimensionne (~640 px), compresse (JPEG q≈78), encode en base64.
- **Injecte dans le HTML via des tokens** : le HTML contient `const IMG=__TOKEN__;`,
  le script remplace le token par un objet JSON `{ "Nom produit": "data:image/...;base64,..." }`.
- La carte produit lit `IMG[p.n]` → `<img>` si présent, sinon placeholder dégradé.
- Stocker la version **compressée** dans `assets/images/` (repo léger).

**Notes** : 41 images dispatchées ainsi sur Luxury Club 229. Vérifier après coup :
JSON parseable, 0 produit sans image, 0 image orpheline. Supprimer le script après usage.

---

## Autres techniques à documenter

- Variables CSS pour palette client
- Carousel sans librairie (CSS scroll-snap)
- Lazy-load des images base64 lourdes (technique alternative)
- Open Graph pour partage WhatsApp
- Optimisation Lighthouse mobile sur vitrine 100% inline
