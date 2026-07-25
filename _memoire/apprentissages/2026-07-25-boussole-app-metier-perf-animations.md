# 2026-07-25 — Construire une APP métier (pas une vitrine) : perf, animations, audio, QC

> Tiré des 7 vagues du proto Boussole (`boussole/_proto/app.html`). Techniques **réutilisables
> sur les vitrines clients** et sur les prochains SaaS verticaux NEBULA.

---

## 1. ⚠️ PIÈGE MAJEUR — `transform` + `position: fixed` = bouton hors écran

**Symptôme** : sur l'écran Catalogue, le bouton flottant « + » se retrouvait à `top: 939px`
pour une fenêtre de 844px → **inatteignable**, sur mobile ET PC.

**Cause** : un élément avec un `transform` (même une **matrice identité**) devient le
*containing block* de ses descendants `position: fixed`. Ces derniers ne se réfèrent plus au
viewport mais à l'élément transformé.

Deux sources, souvent combinées :
1. Une animation d'entrée (`@keyframes` qui anime `transform`) **avec `animation-fill-mode: both`** :
   à la fin, Chromium conserve la valeur finale résolue en `matrix(1,0,0,1,0,0)` — techniquement
   « un transform », donc le piège reste actif **après** l'animation.
2. Le simple fait d'animer le conteneur pendant la durée de l'animation.

**Correctifs (les deux ensemble)** :
```css
/* a) fill-mode backwards : aucun transform résiduel à la fin (rendu identique) */
.screen.entrance { animation: pull .45s var(--ease) backwards; }   /* PAS `both` */
```
```html
<!-- b) n'anime JAMAIS l'écran qui contient un position:fixed : anime son CONTENU -->
<div class="screen">
  <div class="entrance"> …titre, listes… </div>
  <button class="fab">+</button>        <!-- reste ancré au viewport -->
</div>
```
**Idem pour** : `filter`, `perspective`, `will-change: transform`, `backdrop-filter` — tous
créent un containing block. À vérifier partout où une vitrine a un **CTA WhatsApp sticky**
dans une section animée au scroll.

## 2. `overflow-x: hidden` sur `body` NE SUFFIT PAS

Un dépassement horizontal persistait (10–15 px) malgré `body { overflow-x: hidden }` :
le débordement **remonte au viewport** via l'élément racine.
```css
html { overflow-x: hidden; }   /* + body : ceinture ET bretelles */
```
Mesure de contrôle : `document.documentElement.scrollWidth - clientWidth` doit valoir **0**
sur chaque écran (test automatisé, cf. §6).

## 3. Perf : couper ce qui tourne hors écran

Trois animations infinies tournaient en permanence dans le tiroir **fermé** (hors écran).
```css
.app:not(.menu-open) .drawer .navbtn--holo,
.app:not(.menu-open) .drawer .navbtn--holo::before { animation-play-state: paused; }
```
Règle : **toute animation infinie doit être mise en pause quand son conteneur est masqué**
(tiroir, modale, onglet inactif). Gain direct sur la batterie des téléphones d'entrée de gamme.

Rappel de la leçon du 2026-07-21 : **jamais de `backdrop-filter` permanent sous des animations
de fond** (recalcul du flou à chaque frame) → verre *simulé* par dégradés opaques, flou réservé
aux surfaces transitoires (tiroir, voiles).

## 4. Animation « plaisir » VS vitesse d'usage : le compromis 1×/session

Une transition spectaculaire à chaque entrée d'écran devient une **taxe** au 20ᵉ passage.
```js
const _fxSeen = {};                 // mémoire de session (pas persistée)
const full = _entryFx && !_fxSeen[nav];
if (full) { _fxSeen[nav] = 1; /* version longue */ }
// sinon : rendu instantané, ou version « éclair » (durées ÷ 2 via une classe .is-fast)
```
Et distinguer **arrivée sur l'écran** (transition permise) de **re-rendu interne**
(suppression, filtre, changement de période) → un flag `_entryFx` posé par le routeur et
**consommé** par le premier bind. Sans ça, chaque clic rejoue la mise en scène.

## 5. Audio Web Audio — cohérence & richesse (aucun fichier)

- **Un bus d'écho commun** branché une seule fois dans le graphe donne à *tous* les sons une
  signature « produit premium », sans toucher chaque fonction :
  ```js
  const dly = ctx.createDelay(0.4); dly.delayTime.value = 0.125;
  const fb = ctx.createGain(); fb.gain.value = 0.22;
  const damp = ctx.createBiquadFilter(); damp.type = 'lowpass'; damp.frequency.value = 2600;
  master.connect(dly); dly.connect(damp); damp.connect(fb); fb.connect(dly);
  damp.connect(wet); wet.connect(compressor);   // wet ~0.13 desktop / 0.09 mobile
  ```
- **Cloche crédible** = plusieurs partiels **légèrement détunés** (±0,4 %) avec des durées
  décroissantes (880 / 1318,5 / 1760 / 2637 Hz), pas un simple bip.
- **Bruit qui meurt naturellement** : façonner le buffer à la génération
  `d[i] = (rand*2-1) * Math.pow(1 - i/len, 2)` → « poussière d'or » plutôt que « pshhh ».
- **Chaleur d'un clic** : sinus fondamental + octave `triangle` détunée à 30 % de gain.
- Sons courts (< 500 ms), volumes 0,03–0,2, compresseur en sortie, mobile boosté ×1,8.

## 6. QC Playwright — le sweep qui trouve ce que l'œil rate

Un **balayage automatisé multi-viewport** a trouvé 2 bugs invisibles en review manuelle
(bouton hors écran, débordement de 15 px). Patron réutilisable :
```js
for (const vp of [{w:390,h:844}, {w:1280,h:800}]) {      // mobile ET PC
  for (const ecran of TOUS_LES_ECRANS) {
    await aller(ecran);
    // 1. débordement horizontal
    scrollWidth - clientWidth === 0
    // 2. chaque bouton flottant est DANS le viewport
    rect.right <= innerWidth && rect.bottom <= innerHeight && rect.left >= 0
    // 3. chaque feuille/modale est cadrée ET son bouton d'action visible
    left >= 0 && right <= vp.w && bottom <= vp.h && await isVisible('[data-valider]')
  }
}
```
Pièges rencontrés :
- Servir les modules ES avec le **bon MIME** (`text/javascript`) sinon la page ne démarre pas.
- Les éléments avec animation infinie sont « unstable » → `click(sel, { force: true })`.
- Ne jamais cibler une ligne par son **index** dans une liste triée : passer par `data-id`.
- Garder les suites **cumulatives** (`qc_v4` … `qc_v9`) et toutes les rejouer : c'est ce qui a
  prouvé qu'aucune correction ne cassait les vagues précédentes (113 vérifications).

## 7. Moteur de phrases qui ne se répète jamais

Pour un texte d'accueil qui doit donner envie de revenir (conseils, avis, leçons) :
```js
// pool = phrases CALCULÉES sur les vraies données (poids fort) + contenu statique (poids faible)
let pool = tousLesTextes().filter((g) => !hist.includes(g.id));
if (!pool.length) hist = hist.slice(-4);        // reset doux : on garde juste les 4 derniers
// tirage pondéré, puis on mémorise l'id servi (persisté avec les données)
```
Clé du ressenti « il me connaît » : **la majorité des phrases sont générées à partir des
chiffres réels** (hier vs avant-hier, dettes, ruptures, marge) — pas une liste figée.

## 8. Divers réutilisables

- **Confirmation douce à 2 touches** sur un bouton destructif (s'arme 3 s puis se désarme) +
  **toast « Annuler »** qui restaure vraiment l'état (stock, dettes, position dans la liste).
- **Charte des couleurs d'action** : primaire = or, destructif = rouge, encaissement = vert.
  Un « Enregistrer » rouge à côté d'un « Supprimer » rouge = suppression accidentelle garantie.
- **Feuilles (bottom sheets) sur PC** : passer en **carte centrée** (`min(560px, 100vw-48px)`,
  `left:50%` + `translate(-50%)`) au-delà de 1024 px — une barre pleine largeur sur un 27" est
  illisible.
- **Découpage robuste d'un nombre affiché** (pour animer un compteur) :
  `/^([^\d]*)([\d\s  ]+)(.*)$/` → préfixe / chiffres (avec espaces de milliers) / suffixe.
- **Hachage de code PIN** : versionner l'algo (`v2` en préfixe) et garder une fonction
  `pinOk(code, hash)` qui accepte **l'ancien et le nouveau** → les codes déjà posés continuent
  de fonctionner après migration.
