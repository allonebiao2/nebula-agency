# MON BÉNIN · l'expérience

> **Nom tranché par Mongazi le 2026-08-10 : « Mon Bénin »**, avec **« sept cents
> kilomètres »** en signature. Le dossier garde son ancien nom `benin-mon-pays/`.
>
> ## 🌍 EN LIGNE (dev) : **https://dev.mon-benin.pages.dev**
> Projet Cloudflare Pages `mon-benin`, branche `dev`, production `main` (vide).
> Publier : `python benin-mon-pays/_dist.py` puis déployer `_dist` sur `dev`.
> ⚠️ Un agent non navigateur reçoit **403** sur `*.pages.dev` (filtrage de bots
> Cloudflare). Vérifier avec un vrai `User-Agent`, et **rouvrir les robots IA sur
> le vrai domaine** quand il sera acheté (`PUT /zones/{zone}/bot_management`).
> **Vrai domaine : plus tard**, Mongazi l'achètera.

Produit **interne NEBULA**, pas une vitrine client. Il ne vit pas dans
`clients/`.

---

## 1. Ce que c'est, en une phrase

**Ce n'est pas un site sur le Bénin. C'est un voyage au Bénin qui dure sept
minutes**, de la Porte du Non-Retour jusqu'au fleuve Niger, sur environ
700 kilomètres.

## 2. Pourquoi ce n'est pas un catalogue

Tous les sites de tourisme sont des grilles de cartes. Pour le Bénin c'est pire
qu'inefficace : la force du pays n'est pas visuelle, elle est **narrative**.
Ganvié n'est pas un joli village sur pilotis, c'est un village bâti sur l'eau
**parce que l'eau était la seule chose qui sauvait des razzias**. Une grille de
photos écrase exactement ça.

La référence envoyée par Mongazi (vidéo 1, « GLOBETROTTER ») **est** un site de
destinations, et elle a un bouton **« HASARD »** : la preuve, écrite dans son
interface, que c'est un catalogue. On a pris son savoir-faire et refusé sa
structure. **Ici les lieux sont dans l'ordre de la route, et l'ordre est le
sens.** Le jour où l'on peut tirer au sort, on a perdu.

## 3. L'idée de structure

Le Bénin s'étend sur **environ 700 km** de l'Atlantique au fleuve Niger. C'est
un pays en couloir. Donc **le défilement est la route**, et l'anneau du coin est
**gradué en kilomètres**, pas décoratif.

Et le voyage **part de la Porte du Non-Retour, sur le sable, et remonte** la
Route des Esclaves vers l'intérieur : le visiteur refait le chemin à l'envers.

✅ **Tranché le 2026-08-10 : on part de la Porte.** Mongazi a choisi d'ouvrir
sur la mémoire. Tout reste écrit pour qu'un réordonnancement soit une simple
permutation des `<section class="st">`.

## 4. Les huit stations

| # | Lieu | km | Verbe | Motif dessiné |
|---|---|---|---|---|
| 0 | **La Porte** (plage d'Ouidah) | 0 | **tenir** | l'arche + la mer |
| 1 | **Ouidah** | 6 | **remonter** | la route + la forêt sacrée |
| 2 | **Cotonou** | 7 | **choisir** | les étals de Dantokpa |
| 3 | **Ganvié** (lac Nokoué) | 18 | **pagayer** | les pilotis + la pirogue |
| 4 | **Abomey** | 98 | **frotter** | la grille des bas-reliefs |
| 5 | **Koutammakou** (Boukoumbé) | 430 | **descendre** | la coupe d'une Tata Somba |
| 6 | **La Pendjari** | 538 | **attendre** | les courbes de niveau |
| 7 | **Le Fleuve** (Malanville) | 617 | **arriver** | les bandes du Niger |

**Un verbe DIFFÉRENT par lieu.** C'est la règle. Partout ailleurs il n'y en a
qu'un, « faire défiler ». Si une interaction pourrait être copiée-collée sur un
autre lieu, elle est à refaire.

⚠️ **Les kilomètres sont des latitudes converties**, pas des distances
routières : la route réelle Cotonou→Malanville fait environ 730 km, ce qui
casserait l'échelle de 700. C'est écrit dans le pied de page et sur le panneau
des huit lieux. **Ne jamais les remplacer par des distances de route** sans
refaire l'échelle entière.

Conséquence assumée et utilisée : **les quatre premiers lieux tiennent dans les
vingt premiers kilomètres.** Le sud est dense, le pays est long. La section
« LE SAUT » dit exactement ça, et c'est vrai.

## 5. Ce qui vient des trois vidéos

| Emprunt | Source | Ce que ça devient ici |
|---|---|---|
| Rideau d'ouverture | V1 | deux panneaux s'écartent, le compteur monte **de 0 à 700 km** |
| Cercles concentriques | V1 | **l'anneau gradué**, un instrument, pas un ornement |
| Poussée verticale vers une page claire | V1 | la **halte** |
| Le panneau qui EST la transition | V2 | le **cartel** qui balaye, **côté alterné** |
| Titre fantôme puis solide | V2 | repris tel quel |
| Fond qui morphe sombre ↔ clair | V3 | le pays **s'éclaircit vers le nord** |
| Parallaxe par mot | V3 | une seule phrase par section (« LE SAUT ») |

**Refusé du prompt d'origine** : GSAP, ScrollTrigger, SplitText, Draggable,
InertiaPlugin, Lenis (150 à 250 Ko avant la première image) · les 300vh de
défilement artificiel · le bouton « HASARD » · le `backdrop-filter` **sous** une
rotation infinie (leçon Boussole) · l'or `#D4AF37` sur le crème, **mesuré à
1,86:1, illisible**.

**Ce qu'aucune des trois vidéos n'a** : du son, une voix, un être humain qui
parle. Elles sont sublimes et froides. C'est là que se joue la différence, et
c'est ce qui reste à faire.

## 6. Décisions techniques qui ne se devinent pas

- **Zéro bibliothèque.** Défilement lissé, iris, glissé avec inertie, découpage
  par mot : tout écrit à la main.
- **Zéro requête vers un tiers.** Il y avait une police Google : elle est
  **retirée**. Bodoni Moda est servi depuis `assets/fonts/` (repris de Hillary,
  100 Ko, `font-display: swap`, jamais bloquant). Un contrôle vérifie qu'aucune
  requête ne sort.
- **Le défilement lissé n'est branché QU'À LA MOLETTE.** Au doigt on laisse le
  navigateur : reprendre l'inertie tactile, c'est casser le site.
- **`--terre` n'est réécrite qu'au CHANGEMENT de station**, jamais à chaque
  image : une variable sur `:root` recalcule tout le document (leçon Hillary).
- **Le compte du rideau tourne au minuteur**, pas sur `requestAnimationFrame`
  (leçon Angy Art).
- **Huit ambiances générées avec WaveSpeed**, une par lieu (Mirelo SFX 1.6,
  `ambience: true`, 8 s, 0,64 $ au total). La nappe synthétisée qui se déformait
  avec la latitude est **remplacée** : chaque lieu a désormais SON son.
  ⚠️ **Le modèle choisi est le seul qui boucle SANS COUTURE.** Une ambiance qui
  claque toutes les huit secondes est pire que pas d'ambiance : le raccord est
  mesuré (début contre fin sur 40 ms, écart 7,9 %).
  ⚠️ **Niveaux normalisés à -20 LUFS** : bruts, l'écart entre le Koutammakou
  (vent sec, 49 % de silence) et la Pendjari (cicadas) était d'un **facteur 15**.
  Après normalisation : 1,9. Les originaux sont gardés dans `_sources_sons/`,
  une régénération coûte de l'argent.
  ⚠️ **Jamais chargées d'avance** : 380 Ko de son sur une page de 231 Ko. Seul
  le lieu où l'on se trouve télécharge son ambiance (48 Ko), et seulement si le
  son est allumé. Un contrôle vérifie qu'aucun son ne part avant le geste
  d'entrée. Rien ne sonne avant un geste, silence d'amorçage iOS + compresseur.
  Scripts : `_sons.py` (génération) et `_sons_finir.py` (normalisation).
- **Aucun emprisonnement** : on entre au bouton (avec le son) **ou** en
  défilant (sans). Le verbe « tenir » de la Porte **ne bloque pas** le
  défilement : la gravité vient du texte, pas de la privation de liberté.
- **L'anneau se range du côté opposé au cartel** à chaque station. Sans ça il se
  posait sur l'avertissement de la Pendjari.
- **Au téléphone l'anneau devient une réglette de bord opaque** : un disque de
  84 px se posait sur le curseur de Ganvié, sur « Les greniers » et sur le
  bouton WhatsApp.

### La règle des éléments fixes
> **Un instrument flottant ne recouvre jamais du texte. Seules les bandes de
> bord (barre du haut, réglette du bas) en ont le droit, et alors elles doivent
> être vraiment opaques.**

Le QC applique cette règle littéralement, et il **photographie la barre** au
lieu de lire une chaîne CSS.

## 7. Les images

⛔ **Aucune image générée par IA d'un lieu réel.** Un faux Ganvié présenté comme
Ganvié est un mensonge sur un pays réel. ⛔ Aucune photo « d'Afrique » qui ne
soit pas le Bénin : la moitié des images étiquetées « Bénin » en ligne sont
ghanéennes ou togolaises. ⛔ Aucune personne identifiable sans accord écrit,
**jamais un enfant**.

En attendant les vraies photos, **le site est un atlas dessiné** : chaque lieu a
un relevé géométrique en SVG qui se trace à l'arrivée. Ce n'est pas un
bouche-trou, c'est fini en l'état. Les photos viendront **dans** les aplats de
couleur.

**Ce qu'il faut demander** : deux photos par lieu, **en portrait** (90 % des
photos de tourisme sont en paysage et se recadrent mal en plein écran vertical),
une très large pour l'arrivée et une serrée sur un détail humain.

## 8. La couche « haltes » (les commerces), pas encore ouverte

L'unité du projet n'est pas le lieu, c'est **quelqu'un qui fabrique quelque
chose, dans un endroit**. Le pêcheur de Ganvié, le maçon batammariba et la
coiffeuse de Ganhi sont **le même objet**. C'est ce qui permettra à un salon de
coiffure de cohabiter avec la Porte du Non-Retour sans que ce soit obscène.

Règles arrêtées d'avance :
1. **Un commerce apparaît à sa latitude réelle**, sur la route. Pas d'onglet,
   pas d'annuaire, **la position ne s'achète pas**.
2. **On ne vend pas la place, on vend la profondeur.** Être sur la carte reste
   gratuit ; ce qui se paie est la halte (le geste filmé, la voix, la matière).
3. **Aucune histoire inventée.**
4. Format d'une halte, toujours les mêmes quatre temps : **le geste** (10 s de
   mains qui travaillent, sans parole) · **la voix** (30 à 40 s) · **la matière**
   (2 ou 3 photos serrées) · **la porte** (un bouton WhatsApp).

⚠️ **Les cinq artisans déjà clients de NEBULA sont les premières haltes
naturelles** (Angélique, Hillary, HH Design, Au Braisé d'Or, Saeir Thiam),
**mais il faut leur accord écrit**. Rien ne part en ligne sans.

⚠️ **Ne pas ouvrir cette couche maintenant** : une plateforme avec deux salons
dedans a l'air morte, et une carte que personne n'a admirée ne se vend pas.

## 9. Exactitude

Chaque date du site est publique et vérifiable : Porte élevée en **1995** ·
Route des Esclaves **~3,5 km** · douze rois d'Abomey de **1625 à 1900** · palais
UNESCO **1985** · **26 œuvres** restituées en **novembre 2021** · Vodun Days
depuis **janvier 2024** · Koutammakou UNESCO **2004** (Togo), versant béninois
**2023** · Pendjari confiée à **African Parks depuis 2017** · statue de
l'Amazone **2022**.

⚠️ **Un Béninois voit une erreur sur son pays en deux secondes, et le charme
tombe.** Si une source manque ou diverge, on le dit dans le texte.

⚠️ **L'avertissement sécurité du nord est obligatoire** et reste dans la
section Pendjari. Le dire augmente la crédibilité, il ne la réduit pas.

## 10. Le contrôle qualité

```bash
python benin-mon-pays/_qc.py      # 63 contrôles, tous verts au 2026-08-10
python benin-mon-pays/_voir.py    # planches contact 390 + 1440, à REGARDER
python benin-mon-pays/_images.py  # favicon + image de partage
```

Ce que le QC voit et que l'œil oublie : le compteur qui **contredit
l'étiquette** (il affichait 3 sur « km 0 » et 166 sur « km 98 »), un fixe qui se
pose sur du texte, le **contraste mesuré sur les pixels rendus** (lire
`background-color` est aveugle au-dessus d'un motif), une section atteinte **par
le menu** qui ne se révèle pas, les cibles sous 44 px, et le débordement
horizontal en 390 / 768 / 1440.

## 11. Si le nom change, ces 6 endroits

1. `index.html` → `<title>`, `og:site_name`, `og:title`, le JSON-LD `name`
2. `index.html` → `.rideau-t` et `.seuil-t`
3. `index.html` → `.barre-m` et `.pied-t`
4. `_images.py` → le texte de l'image de partage, puis **regénérer**
5. `benin-mon-pays/CONTEXT.md` → cette fiche
6. `CLAUDE.md` → la ligne du produit

## 12. Ce qui reste

- [ ] **Le nom** (4 options sur la table)
- [ ] **Les 10 questions** posées le 2026-08-09, sans réponse
- [ ] Les **photos**, deux par lieu, en portrait
- [ ] Les **voix** : sans elles, le projet reste beau et froid
- [ ] Le déploiement (**volontairement pas fait** : le nom et le point de départ
      ne sont pas tranchés)
- [ ] Anglais en 2e vague (la diaspora visée est largement anglophone)
- [ ] Fenêtre calendaire : **les Vodun Days de janvier**, à Ouidah
