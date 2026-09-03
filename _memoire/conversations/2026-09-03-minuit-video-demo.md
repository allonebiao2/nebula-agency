# MINUIT · la vidéo de démonstration

## Date : 2026-09-03
## Sujet principal : monter en Remotion la démonstration de MINUIT, la lettre digitale

---

## Ce qu'on a fait

Une composition `minuit-demo` dans `_studio-video/` : **1080x1920, 30 images
par seconde, 900 images, 30 s exactement**, rendue en `out/minuit-demo.mp4`
(2,9 Mo, H.264, vérifié à l'ffprobe).

**Six plans, six signatures, toutes tirées de l'enveloppe cachetée**, reprises
une par une de `minuit/README.md` :

| # | Plan | Signature | Durée |
|---|---|---|---|
| 1 | Le seuil | le cachet respire, puis se brise en trois éclats de cire | 5,5 s |
| 2 | La lettre | le dépliage, puis l'encre qui sèche ligne après ligne | 8,5 s |
| 3 | Le compte | les chiffres qui roulent, sortie qui ralentit | 3 s |
| 4 | La signature | le trait qui s'écrit (`stroke-dashoffset`) | 3 s |
| 5 | L'heure dite | l'aiguille qui monte à minuit | 6 s |
| 6 | La carte | le cachet qui se referme, la boucle du plan 1 à l'envers | 4 s |

Le plan 5 est le seul dont la signature n'existe pas dans le produit, et c'est
lui qui vend. Il sort quand même du même objet : **le cadran reprend le cercle
et le pointillé DU CACHET**, l'aiguille remplace la cire.

### Le choix de fond : on rejoue le produit, on ne le photographie pas

`minuit/_vues/` contenait déjà de vraies captures (seuil, lettre, constructeur).
Elles n'ont pas été utilisées comme images. **Le produit EST une animation** :
le cachet qui se brise ne tient pas dans une capture, et une démonstration de
MINUIT qui ne montrerait pas ce brisement ne montrerait rien. Tout est donc
reconstruit en React, avec les jetons de couleur, la pile de polices et les
trajectoires d'éclats **lues dans `minuit/lettre.html`**.

⚠️ **Aucune police téléchargée**, comme dans le produit : Palatino Linotype
sous Windows. La vidéo doit ressembler à la lettre que la destinataire ouvrira,
pas à une version embellie pour la publicité.

---

## Ce que j'ai appris

### ⛔ Le délai de démarrage de Chrome n'est PAS celui de `remotion.config.ts`

Premier rendu : `TimeoutError: Timed out after 25000 ms while trying to connect
to the browser`. Or `remotion.config.ts` porte déjà
`setDelayRenderTimeoutInMilliseconds(120000)`, posé exprès pour ce PC.

**Ce sont deux délais différents.** Celui du démarrage du navigateur est
**écrit en dur** dans `node_modules/@remotion/renderer/dist/open-browser.js:104`
(`timeout: 25000`) et aucun réglage ne l'atteint.

**Le remède** : lancer le binaire une fois à la main pour que Defender le
scanne et retienne son verdict. Après ça, tous les rendus passent.

```
node_modules/.remotion/chrome-headless-shell/win64/chrome-headless-shell-win64/chrome-headless-shell.exe
```

⚠️ Le premier lancement télécharge **270 Mo décompressés** (113 Mo de zip), et
sur la connexion de Cotonou ça a pris une quinzaine de minutes.

### ⛔ Une rotation en nombre nu sort en pixels, donc ignorée sans un mot

React 19 a `scale` dans sa table des valeurs sans unité, **pas `rotate` ni
`translate`**. Vérifié en rendant un `<div>` avec `react-dom/server` :

```
<div style="scale:1.045;rotate:12px;translate:5px;opacity:0.5">
```

`scale:1.045` est valide, `rotate:12px` ne l'est pas et le navigateur le jette
**en silence**. Toute rotation s'écrit donc avec son `deg` dans un gabarit de
chaîne. Le piège est qu'une rotation qui ne tourne pas ressemble à une
animation mal réglée, pas à une faute de syntaxe.

### ⛔ Ne jamais fondre en enchaîné deux plans qui montrent du papier

Premier montage : `TransitionSeries` + `fade()` de 0,5 s entre chaque plan.
Regardé sur l'image 372 : la feuille de la lettre à 50 % et la carte du compte
à 50 %, deux rectangles clairs décalés l'un sur l'autre, **le « 332 » en train
de rouler par-dessus le texte de la lettre**. Ça ne ressemble pas à une
transition, ça ressemble à une panne.

**Les six plans partagent le même fond de nuit et font eux-mêmes entrer et
sortir leur contenu : la coupe est donc invisible, et le fondu ne servait qu'à
superposer.** Passé en `Series`, `@remotion/transitions` désinstallé.

⚠️ C'est l'inverse de la règle des séries « oui / non » du même dossier, où la
coupe sèche est le format. Ici la coupe n'est pas un parti pris de rythme,
c'est simplement ce qui ne se voit pas.

### ⚠️ Un palier de sortie tenu à gauche maintient la PREMIÈRE valeur, pas zéro

Les trois éclats de cire allaient de 1 à 0 à partir de l'image du brisement,
avec `extrapolateLeft: 'clamp'`. Avant le brisement, la valeur est donc tenue
à **1** : les trois morceaux de cire étaient posés sur le cachet intact
**depuis la première image**. Il faut un palier de départ à 0, une image avant.

Trouvé en **relisant le code**, pas en le regardant : le défaut était bien
visible à l'image 90, mais je ne l'avais pas encore rendue.

### ⚠️ Trois défauts que seules les CAPTURES ont montrés

- **L'aiguille traversait le « 00:00 »** de part en part, pile entre les deux
  paires de zéros. Le code était juste, la composition non. → l'aiguille
  s'efface au moment où l'heure s'écrit.
- **Les éclats de cire ronds ressemblaient à trois pastilles roses.** Le
  produit s'en sort avec un `border-radius` parce que ses éclats sont
  minuscules et rapides ; à 84 px et traversant l'écran, il faut de vrais
  **polygones à angles vifs**. La cire ne se casse pas en ronds.
- **Le dépliage était mangé par la transition** : la feuille finissait de
  s'ouvrir pendant le fondu, on ne voyait qu'une dalle grise. Décalé de dix
  images.

### ⚠️ Une ligne de texte se recoupe pour la LARGEUR de la vidéo

« phrases, alors je vais écrire les vraies. » faisait 41 caractères, soit
1 041 px estimés pour 800 px de papier. Les lignes de la lettre sont donc
recoupées à la main dans `donnees.ts`, **et il le faut de toute façon parce que
le séchage de l'encre se fait ligne par ligne** : sans lignes explicites, il
n'y a rien à décaler.

---

## Décisions prises

- **On rejoue le produit en React, on ne colle pas ses captures.** Le seuil est
  une animation, une image fixe ne le montre pas.
- **Pas de fondu enchaîné.** `Series`, coupes invisibles sur fond commun.
- **Les couleurs, le texte et le prix sont recopiés UNE SEULE FOIS**, dans
  `src/minuit/donnees.ts`, depuis `minuit/lettre.html` et `minuit/creer.html`.
- **Les durées vivent dans `donnees.ts`, pas en clair dans le montage.** Le
  studio ne sait donc pas les faire glisser à la souris, et c'est assumé : la
  longueur de la composition est calculée sur les mêmes valeurs, une durée
  déplacée d'un seul côté laisserait du noir en fin de vidéo.
- **Chaque plan est aussi une composition** (dossier `minuit-plans` du studio) :
  on règle un plan seul sans rejouer les trente secondes.

---

## ⛔ À NE PAS OUBLIER AVANT DE PUBLIER CETTE VIDÉO

Elle promet **« Elle l'ouvre à minuit pile. Pas avant. »** et affiche
**`nebula-agency.online/minuit`**. Au 2026-09-03, **ni l'un ni l'autre
n'existe** : la livraison à l'heure choisie (n8n) et le serveur en ligne
(Render) sont les deux chantiers ouverts de `minuit/README.md`.

Le choix de garder quand même la promesse est assumé : c'est elle qui donne son
nom au produit, et une démonstration qui l'enlèverait ne démontrerait plus
rien. **La vidéo est prête, la promesse ne l'est pas.** Elle attend que
l'adresse réponde.

⚠️ Le constructeur porte déjà le choix de l'heure (un champ `time` à `00:00`
dans `creer.html`, avec la note « À minuit pile, c'est ce qui fait le
produit »). C'est la **remise** à l'heure dite qui manque, pas le réglage.

---

## Ce qui reste

- La **signature 4 du produit** (le polaroïd qui se développe) n'a pas de plan :
  la lettre montrée n'a pas de photo. À ajouter le jour où une vraie lettre
  d'exemple en portera une.
- Aucune **bande son**. Le dossier `public/` du studio est hors dépôt et la
  note sur les droits y est déjà. ⛔ Jamais de MP3 hébergé, c'est de la
  contrefaçon, et c'est écrit aussi dans `minuit/README.md`.

---

## Les fichiers

```
_studio-video/src/minuit/donnees.ts    couleurs, texte de la lettre, durées  ← on édite ICI
_studio-video/src/minuit/Minuit.tsx    le montage des six plans
_studio-video/src/minuit/Seuil.tsx     1 · le cachet qui se brise
_studio-video/src/minuit/Lettre.tsx    2 · le pli, puis l'encre
_studio-video/src/minuit/Compte.tsx    3 · les chiffres qui roulent
_studio-video/src/minuit/Signature.tsx 4 · le trait qui s'écrit
_studio-video/src/minuit/Heure.tsx     5 · l'aiguille qui monte à minuit
_studio-video/src/minuit/Fin.tsx       6 · le cachet qui se referme
```

```bash
cd _studio-video
npm run studio          # l'aperçu, on scrube à la souris
npm run rendu:minuit    # out/minuit-demo.mp4
npm run verifier        # tsc, sans rien rendre
```
