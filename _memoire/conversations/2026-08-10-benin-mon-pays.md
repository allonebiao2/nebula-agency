# 2026-08-09/10 · BÉNIN MON PAYS, l'expérience du pays

## Ce que Mongazi a demandé

Une page qui met le Bénin en valeur « comme personne ne l'avait fait avant » :
faire découvrir le pays aux Béninois eux-mêmes, donner envie à ceux qui n'y sont
jamais venus, montrer sa capacité à construire des expériences hors du commun, et
se faire repérer par des institutions ou des entreprises. Plus tard, des
commerces viendront dessus, avec l'histoire de leur fondateur.

Il a envoyé **trois vidéos de référence** et un prompt écrit pour une maison de
couture, en demandant de l'adapter au projet.

## Ce qui a été décidé

### La phrase
**« Ce n'est pas un site sur le Bénin. C'est un voyage au Bénin qui dure sept
minutes. »**

### Le refus qui définit le projet
La vidéo 1 est **« GLOBETROTTER »**, un vrai site de destinations (Highlands,
Sahara, Dolomites, Maldives). Elle a un bouton **« HASARD »** qui téléporte au
sort : la preuve, écrite dans son interface, que c'est un catalogue. On a pris
son savoir-faire et **refusé sa structure**. Ici l'ordre des lieux est le sens.

### La structure
Le Bénin s'étend sur environ 700 km de l'Atlantique au Niger : un pays en
couloir. Donc **le défilement est la route**. Le voyage part de la **Porte du
Non-Retour, sur le sable**, et **remonte la Route des Esclaves à l'envers**.

Huit stations, **un verbe différent pour chacune** : tenir · remonter · choisir ·
pagayer · frotter · descendre · attendre · arriver.

### Ce qui vient des vidéos
- **V1** : le rideau, les cercles concentriques (devenus **un anneau gradué en
  kilomètres**, un instrument et non un ornement), la poussée verticale vers une
  page claire, le collage.
- **V2** (« Bon Mode ») : **le panneau qui EST la transition**, côté alterné, et
  le titre fantôme qui se solidifie. C'est la meilleure idée des trois.
- **V3** : le fond qui morphe sombre ↔ clair (ici : **le pays s'éclaircit vers le
  nord**), la parallaxe par mot, le flou.

### Ce qui a été refusé du prompt
GSAP, ScrollTrigger, SplitText, Draggable, InertiaPlugin, Lenis (150 à 250 Ko
avant la première image) · les 300vh de défilement artificiel · le bouton
« HASARD » · le `backdrop-filter` sous une rotation infinie · **l'or `#D4AF37`
sur le crème, mesuré à 1,86:1, illisible** (le même piège que l'or d'Angélique).

## Ce qui a été appris

### La police distante était une faute
La page chargeait Fraunces chez Google. Le test s'est **bloqué** dessus, et le
réseau met plus de deux minutes à répondre ici. C'était contraire à la promesse
« 3 secondes en 3G » que je m'étais fixée. **Bodoni Moda est désormais servi
depuis `assets/fonts/`**, repris du dossier Hillary : 100 Ko, `font-display:
swap`, aucune requête vers un tiers, et un contrôle le vérifie.

### Un élément fixe finit toujours par recouvrir du contenu
Réserver une marge en bas d'une section **ne suffit pas** : un `position: fixed`
est ancré au viewport, pas à la section. La règle retenue :

> **Un instrument flottant ne recouvre jamais du texte. Seules les bandes de bord
> en ont le droit, et alors elles doivent être vraiment opaques.**

Deux remèdes : l'anneau **se range du côté opposé au cartel** à chaque station
(sinon il se posait sur l'avertissement de la Pendjari), et **au téléphone il
devient une réglette de bord opaque** (un disque de 84 px se posait sur le
curseur de Ganvié, sur « Les greniers » et sur le bouton WhatsApp).

### Un compteur qui contredit son étiquette
La jauge interpolait en continu : elle affichait **3** en face de « km 0 » et
**166** en face de « km 98 ». Corrigé : quand une station occupe le milieu de
l'écran, la jauge affiche **son** kilomètre exact, et n'interpole que dans les
intervalles.

### Vérifier en photographiant, pas en lisant le CSS
Le contrôle d'opacité de la barre lisait `getComputedStyle(...,'::before')` et
échouait pour une mauvaise raison. Refait : on **photographie** la barre pendant
qu'un motif clair défile dessous, et on regarde la luminance la plus claire.
Même principe que le contraste mesuré sur les pixels rendus.

### Trois signalements de mise en page, tous justes
`padding-left`, `width` et surtout le curseur suiveur qui écrivait `top/left`
**à chaque image** plus quatre propriétés de mise en page animées. Tout est passé
en `transform` et `opacity`.

## L'état

- `benin-mon-pays/` : `index.html`, `assets/app.css`, `assets/app.js`,
  `assets/fonts/`, `assets/images/`, `_qc.py`, `_voir.py`, `_images.py`,
  `CONTEXT.md`
- **63 contrôles verts, 0 échec.** Zéro erreur JS, zéro réponse ≥ 400, **zéro
  requête vers un tiers**, aucun débordement en 390 / 768 / 1440.
- **PAS DÉPLOYÉ, volontairement** : le nom n'est pas tranché et le point de
  départ (ouvrir ou non sur l'esclavage) est une décision de Mongazi.

## Ce qui attend une réponse

Le **nom** (Bénin mon pays · MON BÉNIN · SEPT CENTS · REMONTER) et les **10
questions** posées le 2026-08-09, dont les trois qui décident de la structure :
le point de départ, les **photos** (deux par lieu, **en portrait**), et les
**voix** — sans lesquelles le projet reste beau et froid, comme les trois
références.
