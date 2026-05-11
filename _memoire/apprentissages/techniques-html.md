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

## Autres techniques à documenter

- Variables CSS pour palette client
- Carousel sans librairie (CSS scroll-snap)
- Lazy-load des images base64 lourdes (technique alternative)
- Open Graph pour partage WhatsApp
- Optimisation Lighthouse mobile sur vitrine 100% inline
