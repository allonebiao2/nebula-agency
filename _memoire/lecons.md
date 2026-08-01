# Leçons — Nebula Agency

> Ce qui a marché, ce qui n'a pas marché, ce qu'on refera ou évitera.
> Une leçon = un constat appuyé par une expérience concrète.

---

## Format

```
## YYYY-MM-DD — Titre court

- **Contexte** : sur quel projet / quelle tâche
- **Ce qui s'est passé** : observation factuelle
- **Leçon** : ce qu'on en retient
- **À appliquer** : comment ça change la pratique future
```

---

## Ce qui marche bien

> À compléter au fil des projets.

## Ce qui a posé problème

> À compléter au fil des projets.

---

## 2026-05-25 — Tester l'audio sur un vrai mobile, pas en émulation desktop

- **Contexte** : Luxury Club 229 — système audio Web Audio API (musique d'ambiance + SFX) testé sur desktop pendant le développement, validé OK. Gloria signale en production que ça ne fonctionne pas sur mobile.
- **Ce qui s'est passé** : Le pattern `ctx.resume()` au premier geste fonctionnait sur Chrome desktop mais pas sur iOS Safari (AudioContext reste en `suspended`). De plus, le gain master à 1.0 était audible sur laptop mais inaudible sur haut-parleur téléphone.
- **Leçon** : **L'émulation mobile dans les DevTools desktop ne reproduit pas le comportement audio réel d'iOS/Android.** Web Audio API a des quirks par plateforme (silent buffer unlock iOS, gain plus élevé pour les haut-parleurs téléphone, mode silencieux iOS qui bloque tout, sample rate mismatch).
- **À appliquer** :
  - Toujours tester l'audio sur un vrai téléphone (idéalement iPhone ET Android) avant de livrer.
  - Sur tout projet incluant Web Audio API : appliquer d'office le pattern silent buffer unlock + DynamicsCompressor + gain mobile boosté. C'est la baseline minimale viable mobile.
  - Documenter pour la cliente que le mode silencieux iOS bloque l'audio (limitation matérielle non-résoluble).
- Voir [[techniques-html#audio-mobile-fixes-spécifiques-ios-android-2026-05-25]] pour le code prêt à réutiliser.

---

## 2026-05-24 — Les images PNG « background removed » alourdissent et dégradent les vitrines

- **Contexte** : Luxury Club 229 — 33 photos produits INA Luxury embarquées en base64. Gloria n'aime pas le rendu : « les fonds blancs ont été très mal enlevés ».
- **Ce qui s'est passé** : Une étape précédente avait converti les JPEG originaux (fonds blancs propres, studio) en PNG transparents avec détourage automatique raté (halos, crops trop serrés). Résultat : `ina-luxury.html` faisait 12 Mo, les produits paraissaient minuscules dans des cartes pleines de vide, avec des artefacts de détourage visibles.
- **Leçon** : Sur une vitrine commerciale, **les fonds blancs studio sont un atout, pas un défaut**. Le détourage automatique (suppression de fond) génère des artefacts qui font perdre le côté pro des photos. Mieux vaut normaliser les images sur un canvas blanc commun (même dimensions) pour la cohérence visuelle.
- **À appliquer** :
  - Garder les JPEG originaux comme source de vérité dans `assets/images/`.
  - Pour normaliser visuellement la grille : pipeline canvas blanc + redimensionnement (script PowerShell GDI+ ou Python Pillow), aucun détourage. Le CSS card-photo passe en fond blanc + aspect ratio 3:4.
  - Si Gloria veut vraiment du PNG transparent, exiger une livraison de fichiers déjà détourés par elle (ou un pro) — pas d'auto-détourage.

## Un outil se teste sur DEUX écrans, sinon on livre des boutons inatteignables (2026-07-25)

- **Ce qui s'est passé** : après 89 vérifications vertes et plusieurs relectures, un **sweep
  automatisé mobile + PC** a révélé que le bouton « Nouvel article » du Catalogue était
  **hors de l'écran** (donc impossible d'ajouter un produit) et que l'Accueil débordait de 15 px.
- **Pourquoi on ne l'avait pas vu** : les captures d'écran étaient prises sur un seul format, et
  le bouton *existait* dans le DOM — les tests fonctionnels passaient donc parfaitement.
- **Leçon** : tester qu'un élément **existe** ne dit rien sur le fait qu'il soit **atteignable**.
  Mesurer les **positions réelles** (`getBoundingClientRect`) sur **chaque** écran et **chaque**
  format avant de crier victoire.
- **Application immédiate** : vaut aussi pour les **vitrines clients** (CTA WhatsApp sticky,
  bandeaux, pop-ups) — même cause, même effet.

---

<!-- Ajouter les nouvelles leçons au-dessus -->

## 2026-08-01 — Trois leçons de la direction artistique (HILLARY M. STYL v3)

**« Ça fait site à 100 $ » ne se répare pas en ajoutant des animations.**
Ça se répare en trouvant **une idée** dont tout découle. Ici : une maison de couture,
c'est un fil qui va du mètre-ruban au vêtement. À partir de là, chaque animation raconte
le métier — la piqûre, le patron à la craie, la coupe aux ciseaux — au lieu de décorer.
Et avant le mouvement viennent trois choses moins spectaculaires qui font 80 % de l'écart :
**la typographie** (un didone de mode à gros corps), **le rythme des fonds** (sombre,
clair, sombre — sans alternance tout se vaut), et **le vide** qu'on ose laisser.

**Un effet qui suppose une seule ligne de titre cassera sur mobile.**
La « coupe » découpait le titre à 50 % de sa hauteur et écartait les deux moitiés :
impeccable sur une ligne, bouillie sur deux. Refait en balayage horizontal, robuste
quel que soit le nombre de lignes. Règle générale : **tout procédé qui dépend d'une
hauteur de bloc connue est un bug qui attend un écran plus étroit.**

**Le `:hover` reste collé après un appui sur téléphone.**
Tout état de survol qui recouvre un contenu doit vivre dans
`@media (hover:hover) and (pointer:fine)`. Sinon la dernière carte touchée garde son
voile noir, et le client croit l'interface cassée.

**Corollaire de méthode :** ces trois défauts, plus trois autres, étaient invisibles à la
lecture du code. Ils se voient **en regardant les captures, écran par écran**. Le QC
automatique protège la logique ; il ne protège pas le goût.

## 2026-07-31 — Quatre leçons du moteur de commande couture (HILLARY M. STYL)

**Modéliser le métier du client, pas la catégorie qui nous vient à l'esprit.**
La v1 demandait « 8 mesures femme » ou « 8 mesures homme ». C'est un raisonnement de
développeur. Un couturier ne raisonne pas comme ça : **le genre du client ne détermine
rien, le vêtement détermine tout.** Une robe droite demande 15 mesures, un pantalon 6.
Avant de coder un formulaire métier, demander au client la liste exacte, par cas.
Et quand elle manque — la robe ovale — **ne pas l'inventer en silence** : proposer,
marquer « à valider » dans le code ET dans l'interface que le client final verra.

**Une promesse de délai s'annonce sur la borne haute, jamais sur la basse.**
Afficher le jour 8 d'un « 8 à 14 jours » fabrique un client déçu le jour 9. On promet 14,
on livre 10, le client est content. Même logique pour l'express : la vitrine dit que
l'atelier confirme, et que si la charge ne le permet pas, le supplément n'est pas dû.
Une vitrine qui ment sur un délai coûte plus cher qu'une vitrine sans délai.

**Un lien de texte est une cible ratée au pouce.**
Le QC a rejeté six éléments à 15, 23 et 41 px de haut : le logo de la barre, les liens de
navigation, le lien du pied. Tous parfaitement cliquables à la souris. `display:inline-flex`
+ `min-height:44px` règle le cas sans changer l'apparence. À vérifier sur **tous** les
`a`, pas seulement sur les boutons.

**Séparer la source du livrable dès qu'une image en base64 entre dans un fichier.**
75 Ko de logo en base64 rendent un HTML illisible et invitent à dupliquer l'image
(une première version pesait 681 Ko pour cette raison). Méthode : `_vitrine_src.html`
avec des marqueurs → `_build.py` qui injecte → `vitrine.html` généré, **jamais édité à la
main**. Plus `_qc.py` à côté, pour que le contrôle soit rejouable par n'importe qui.

## 2026-07-31 — Cinq leçons du chantier force de vente

**`main` bouge pendant qu'on travaille sur une branche.**
Avant de fusionner vers `main`, toujours `git merge origin/main` dans sa branche, puis
vérifier avec `git diff --stat origin/main..HEAD` que rien d'étranger au chantier
n'apparaît. Un merge naïf a failli annuler 2 621 lignes du module Boussole externalisé
entre-temps. Ce genre de dégât ne se voit qu'une semaine plus tard.

**Un seed n'est pas une migration.**
`seed_content()` ne s'exécute que sur une base vide. Modifier le code ne corrige jamais
la production. Il faut une fonction de migration idempotente, avec **un marqueur par
document**, sinon un élément reste en arrière et contredit les autres.

**Un catalogue commercial ne se dérive jamais d'une structure technique.**
`agency_brain()` construisait la liste des offres de NOVA à partir du dictionnaire
`SERVICES`, qui contenait encore la Fiche Google Maps et les Avatar IA, retirés du site
depuis la v9. NOVA récitait donc au public des offres qui n'existaient plus. Les offres
commerciales se figent explicitement là où on les annonce.

**Vérifier les chaînes couplées avant de toucher un prix.**
Sur `nebula_agency_v9.html`, les valeurs de `setTier('...')` doivent correspondre **au
caractère près** aux `<option>` du formulaire de commande. Un script qui compare les deux
ensembles évite une régression silencieuse du tunnel de commande.

**Tester avant de déployer attrape ce que la relecture ne voit pas.**
Trois bugs seraient partis en production : une colonne `a.numero` qui n'existe pas dans
`affiliates` (c'est `momo_number`) et qui aurait fait planter le cron à sa première
exécution six mois plus tard · `void_commissions()` qui annulait le récurrent acquis à
vie · un marqueur de migration manquant. Aucun n'était visible à la lecture du code.
