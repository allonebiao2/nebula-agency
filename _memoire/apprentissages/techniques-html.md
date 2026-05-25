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

## Audio mobile — fixes spécifiques iOS & Android (2026-05-25)

**Problème** : sur mobile, la musique et les bruitages ne fonctionnent pas
ou ne s'entendent pas. Symptômes : son muet sur iOS Safari, son trop faible
sur Android.

**Causes & solutions**

### 1. iOS Safari : silent buffer unlock (canonique Apple)
L'AudioContext reste en `suspended` sur iOS même après le geste. La résolution
asynchrone de `ctx.resume()` fait que les premiers oscillateurs sont muets.
Le pattern Apple : jouer un buffer audio d'1 sample silencieux **pendant** le
geste pour forcer le déblocage.

```js
try{
  var b=ctx.createBuffer(1,1,22050),s=ctx.createBufferSource();
  s.buffer=b;s.connect(ctx.destination);s.start(0);
}catch(e){}
```

### 2. Master gain boosté + DynamicsCompressor pour éviter le clipping
Les haut-parleurs mobile sont plus faibles que ceux d'un laptop. Monter le
gain master à 1.45 sur mobile (vs .9 desktop). Ajouter un compresseur entre
master et destination pour empêcher la saturation.

```js
var comp=ctx.createDynamicsCompressor();
comp.threshold.value=-10;comp.knee.value=4;comp.ratio.value=8;
comp.attack.value=.005;comp.release.value=.12;
comp.connect(ctx.destination);
master=ctx.createGain();
master.gain.value=IS_MOBILE?1.45:.9;
master.connect(comp);
```

### 3. Détection mobile élargie
`matchMedia('(max-width:760px)')` rate les tablettes et phones en paysage.
Combiner avec `(pointer:coarse)` pour couvrir tout le tactile :

```js
var IS_MOBILE=matchMedia('(max-width:760px)').matches
           ||matchMedia('(pointer:coarse)').matches;
```

### 4. Resume Promise géré
`ctx.resume()` retourne une Promise (iOS). L'ignorer = warnings console + erreurs
silencieuses. Catch-er sans bloquer :

```js
function resume(){
  if(!ctx)return;
  if(ctx.state==='suspended'){
    try{var p=ctx.resume();if(p&&p.catch)p.catch(function(){});}catch(e){}
  }
}
```

### Limitation matérielle iOS — non résoluble
Quand l'iPhone est en **mode silencieux** (interrupteur côté), Web Audio
reste muet quelle que soit la config. Workaround possible via `<audio>` +
MediaStream mais demande la permission Microphone → hors scope pour une
vitrine commerciale. Mentionner à la cliente que le test doit se faire avec
le téléphone NON silencieux.

**Notes** : volume effectif des SFX sur mobile après patch (master 1.45) :
tap .12 · hover .14 · whatsapp .29 · addCart .32 · brandClick .43 · musique .35.

### Update v2 (2026-05-25 PM) — itération après retour cliente
La v1 ci-dessus ne suffisait pas dans la vraie vie. 4 fixes additionnels :

1. **Low-pass adapté mobile** : `lp.frequency.value = IS_MOBILE ? 2800 : 950`
   — les haut-parleurs téléphone sont tinny, couper à 950 Hz rend la musique
   inaudible (le contenu reste dans les basses que le HP ne reproduit pas).
   Sur mobile, lever la coupure à 2800 Hz garde la couleur jazz mais laisse
   passer la clarté.

2. **Compresseur en mode limiter, pas crusher** :
   `threshold:-4, ratio:3, knee:6` (au lieu de `-10, 8, 4`). Le réglage v1
   écrasait justement les pics qu'on cherchait à booster. Nouveau : laisse
   passer les volumes naturels, attrape seulement les crêtes.

3. **iOS unlock avec oscillateur silencieux** en plus du silent buffer :
   ```js
   var uo=ctx.createOscillator(),ug=ctx.createGain();
   ug.gain.value=0;uo.connect(ug);ug.connect(ctx.destination);
   uo.start(0);uo.stop(ctx.currentTime+.002);
   ```
   Certaines versions iOS Safari ont besoin d'un vrai oscillateur joué (même à
   gain 0) pour débloquer totalement la chaîne audio.

4. **Chime immédiat au clic « Entrer »** : appel `LCAudio.play('chordOk')`
   AVANT `musicStart()` dans la fonction `enter()` du welcome-gate. L'utilisateur
   entend un accord doré dès le geste — confirme immédiatement que l'audio
   fonctionne (sinon il attend 1 s avant le premier accord de musique et
   pense que c'est cassé).

5. **Music gain target ↑** : `IS_MOBILE ? .38 : .12` (vs `.24 : .10` v1) sur
   ramp de 1 s (au lieu de 2.2 s). Le master 1.8 + LP 2800 Hz + ramp rapide
   donnent une musique audible quasi immédiate sur mobile.

**Leçon** : tester sur vrai mobile AVANT la livraison cliente, pas après.
Voir [[lecons.md#2026-05-25]].

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

## Allègement d'une vitrine HTML lourde — extraire base64 → fichiers + lazy

**Problème** : Une vitrine NEBULA accumule des images base64 inline et finit
par peser 1+ MB. Sur 3G/4G en Afrique de l'Ouest, ça donne 10-15 s de chargement
et un bounce rate énorme. Mais on ne veut pas casser la règle "100% autonome"
(pas de Google Drive / CDN externe).

**Solution** : Extraire les base64 vers `assets/images/...` (chemins relatifs,
servis par Netlify donc 100% autonomes) + `loading="lazy"` sur les `<img>`
en grille. Stratégie de mapping **hash-first** pour ne jamais re-encoder :

1. **HASH match** (SHA-256 binaire) : si le base64 == un fichier disque
   existant → on lie. Bit-pour-bit identique, **zéro perte qualité**.
2. **SLUG match** : pour les objets JS `IMG{"Nom Produit": "data:..."}`,
   matcher le slug du nom avec un nom de fichier disque.
3. **EXTRACT** : si rien ne matche, écrire `assets/images/extracted/<slug>.<ext>`
   en décodant le base64 (zéro re-encodage = qualité identique au base64).

**Scripts versionnés dans `/scripts/`** (réutilisables sur tout client) :
- `og-audit.js <page.html>` : inventaire base64 (nombre, poids, mapping potentiel)
- `og-allegement.js <page.html>` : applique la transformation (backup .bak auto)
- `og-smoke.js <page.html>` : vérifie syntaxe JS + existence fichiers + 0 base64 restant

**Pattern de remplacement IMG{}**
```js
// AVANT
const IMG={
  "Sérum Anagen":"data:image/jpeg;base64,/9j/4AAQ...(40 KB de texte b64)..."
};
// APRES
const IMG={
  "Sérum Anagen":"assets/images/ina-luxury/capillaires/serum/serum-anagen.jpg"
};
```

**Pattern lazy sur template JS**
```js
// AVANT
return `<img src="${IMG[p.n]}" alt="${p.n}">`;
// APRES
return `<img loading="lazy" src="${IMG[p.n]}" alt="${p.n}">`;
```

**Résultat mesuré** (hub Luxury Club 229, 4 pages) :
- index.html : 508 KB → 57 KB (-89%)
- luxury-skin-clinic.html : 405 KB → 152 KB (-62%)
- cozy.html : 432 KB → 108 KB (-75%)
- ina-luxury.html : 1200 KB → 230 KB (-81%)
- **Total : 2547 KB → 548 KB (-78%)**, chargement 3G : 27 s → 6 s

**Pièges**
- Les `<img class="wg-logo">` (logos hero) : **NE PAS** ajouter `loading="lazy"`,
  ils sont above-the-fold. Le script ne lazifie que les templates JS `${IMG[...]}`.
- Si le base64 est dédupliqué (même logo répété 2× dans la page), le script
  utilise une `Map seenB64` pour ne le hasher qu'une fois.
- Le fallback EXTRACT crée `assets/images/extracted/` — penser à déplacer les
  fichiers vers le bon dossier sémantique par la suite (`corps/`, `visage/`...).

---

## Images Open Graph générées sans API (HTML → PNG via Edge headless)

**Problème** : Les liens partagés sur WhatsApp/Facebook/Instagram nécessitent
`<meta property="og:image">` avec une URL absolue d'image 1200×630. Sans API
payante (Midjourney/Ideogram), comment générer des OG brand-cohérentes ?

**Solution** : HTML + CSS local → PNG via Edge headless → JPG optimisé.
Brand-perfect, gratuit, reproductible, < 50 KB par image.

**Pipeline**
1. Créer un fichier HTML par OG (1200×630), charte exacte du client, polices
   Google Fonts, gradients dorés CSS.
2. Lancer Edge headless :
   ```powershell
   & "msedge.exe" --headless --disable-gpu --hide-scrollbars `
     --window-size=1200,630 --screenshot="og-luxury.png" `
     "file:///C:/path/to/og-luxury.html"
   ```
3. Convertir PNG → JPG qualité 88 avec `System.Drawing.Bitmap` (PowerShell natif Windows) :
   ```powershell
   Add-Type -AssemblyName System.Drawing
   $jpegEncoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() `
     | ? { $_.MimeType -eq 'image/jpeg' }
   $encParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
   $encParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
     [System.Drawing.Imaging.Encoder]::Quality, [long]88)
   $img = [System.Drawing.Image]::FromFile('og-luxury.png')
   $bmp = New-Object System.Drawing.Bitmap $img.Width, $img.Height, `
     ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
   $g = [System.Drawing.Graphics]::FromImage($bmp)
   $g.Clear([System.Drawing.Color]::White)
   $g.DrawImage($img, 0, 0)
   $bmp.Save('og-luxury.jpg', $jpegEncoder, $encParams)
   ```
4. Garder les HTML sources dans `assets/og-source/` (versionnés Git) pour
   pouvoir régénérer plus tard si on change un slogan/couleur.

**Meta tags HTML à ajouter sur la page**
```html
<meta property="og:image" content="https://domaine.netlify.app/assets/images/og-page.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Titre descriptif">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://domaine.netlify.app/assets/images/og-page.jpg">
```

**Test de validation après deploy** : https://developers.facebook.com/tools/debug/
→ coller l'URL, cliquer "Scrape Again" (Facebook cache agressif).

**Résultat** (Luxury Club 229) : 4 OG images générées, 35-46 KB chacune,
charte respectée (Cormorant Garamond, gradients dorés, cadre coins).

---

## Audit complet d'une vitrine en fin de session — checklist

**Quand** : avant livraison client OU si la vitrine est en prod depuis > 1 mois.

**Catégories à vérifier**
1. **Liens WhatsApp** : format `wa.me/<numero>?text=...`, encodage URI, numéro correct
2. **JS** : null-checks sur `getElementById`, try/catch autour de localStorage/AudioContext
3. **Cart WhatsApp** (si présent) : validation ville si livraison, confirmation avant "Vider le panier"
4. **Meta sociales** : `og:image`, `og:url`, `canonical`, `twitter:card`
5. **Poids HTML** : si > 300 KB, candidat à l'allègement base64 → fichiers
6. **Lazy loading** sur les images en grille / panier
7. **Audio mobile** : silent buffer iOS + compresseur + master gain 1.8 (voir
   feedback_audio-mobile)
8. **Focus visible** au clavier (`:focus-visible` global)

**Bonnes pratiques découvertes**
- Toujours **vérifier les trouvailles d'un agent Explore manuellement** —
  taux de faux positifs ~50 % sur l'audit Luxury Club 229.
- Pour tout fix > 3 fichiers : faire un script Node générique dans `/scripts/`
  plutôt que des sed-replace manuels.
- Backup auto `.bak` avant toute transformation script-driven.

---

## Autres techniques à documenter

- Variables CSS pour palette client
- Carousel sans librairie (CSS scroll-snap)
- Skeleton screens pendant le lazy-load
