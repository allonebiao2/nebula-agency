# LE MONDE · le mini-objectif « réalisme », et ce qu'il faut pour l'atteindre à 100 %

> **Mongazi, 2026-11-13** : « le salon doit être virtuel mais le plus réaliste possible, garde en
> mémoire, tu vas me dire ce qu'il faut pour que ce mini-objectif soit atteint à 100 % ».
>
> **Virtuel** : Hillary n'a pas de salon physique (« Hillary n'en a pas », 2026-11-12). On ne scanne
> donc pas un lieu réel : on **invente** un salon, mais il doit **passer pour une photo**.
> **L'étalon** : sa photo de vision, `_partage\immersive  store 3D\ff6cc3de-70c6-4fd8-a801-e694e3bbaa7d.jpg`
> (des robes **portées par des mannequins**, des podiums ronds crème, un sol brillant qui reflète les
> robes, un plafond à spots encastrés, une ligne lumineuse qui court sur une courbe).

## La limite, dite franchement

Un téléphone en 3G ne calcule pas la lumière de *GTA 6* en direct. **La voie des jeux mobiles** :
calculer le réalisme **une fois, à l'avance** (dans Blender, avec Cycles, la nuit), et laisser le
téléphone **afficher** une lumière déjà calculée. C'est ce qui donne le plus de réalisme pour le moins
de calcul. Le reste (personnages, reflets mobiles, jour et nuit réels) reste en direct, en plus léger.

## Ce qui empêche aujourd'hui de croire à une photo (vu sur les captures du 2026-11-13)

1. **Les robes sont des photos collées sur des panneaux** : c'est le plus gros écart avec l'étalon,
   et c'est le produit.
2. **Le plafond** : une grande surface noire et un anneau blanc qui occupent la moitié de l'écran du
   téléphone ; ni spots encastrés crédibles, ni moulure, ni ligne lumineuse comme sur l'étalon.
3. **La lumière** est calculée en direct, sans rebonds : pas de lumière qui « remplit » les coins, des
   ombres rares, des surfaces qui paraissent posées et non éclairées.
4. **Trois personnages sur quatre** sont des silhouettes de maquette.
5. **La rue derrière la vitrine** est un dessin (façades plates, moto en boules).
6. **Le salon est trop propre et trop vide** : le réalisme vient de l'imperfection et de la densité.
7. Le bandeau « MAQUETTE · PERSONNAGES ET DÉCOR PROVISOIRES » (à retirer seulement à la fin).

## La grille : le réalisme est à 100 % quand TOUT est vrai

Chaque ligne se vérifie **sur des captures regardées**, au téléphone (390) et à l'ordinateur (1440,
qualité haute), de jour (`?heure=14`) et de nuit (`?heure=21`).

| # | Critère | Comment on le prouve |
|---|---|---|
| R1 | **Lumière cuite** : rebonds, ombres douces et occlusion précalculés dans Blender Cycles sur tout le décor fixe ; le direct (jour et nuit réels) reste dynamique | captures avant/après côte à côte |
| R2 | **Ombres de contact** sous chaque objet posé et sous chaque personnage | aucun objet qui « flotte » sur les captures |
| R3 | **Aucune surface en couleur unie** sur un grand plan : chaque matière a sa couleur, son relief (normale) et sa rugosité ; tissus avec reflet de velours ou de satin, laiton verni, verre qui transmet | liste des matériaux relue dans le code |
| R4 | **Aucun objet de maquette** visible (boîte, sphère, capsule nue) : mobilier et objets scannés (Poly Haven, CC0) ou modélisés avec chanfreins | inventaire des objets de la scène |
| R5 | **Le plafond de l'étalon** : spots encastrés qui éclairent vraiment, ligne lumineuse sur la courbe, plafond clair ou brun chaud qui ne fait plus « trou noir » | capture du téléphone : le plafond n'occupe plus la moitié de l'écran en noir |
| R6 | **Le sol qui reflète** les robes et les podiums comme sur l'étalon (reflet précalculé + rugosité variable) | capture d'un podium et de son reflet |
| R7 | **Les robes en 3D sur des mannequins**, avec leur tombé, leur matière et une légère vie ; la fiche garde la vraie photo | 🙋 dépend des planches et de la validation d'Hillary |
| R8 | **Les quatre personnages en vraie 3D**, ombre au sol, peau sans l'éclairage de la photo d'origine | 🙋 dépend de Sènami et Maman (Mongazi) et d'Hillary (photos + accord) |
| R9 | **Densité et imperfections** : au moins quinze objets de vie (cintres, rouleaux entamés, échantillons, mètre ruban, magazines, tasse, ruban au sol, carnet de croquis…) | inventaire + captures |
| R10 | **La rue** derrière la vitrine : une vraie image de rue de Cotonou en profondeur (plusieurs plans qui bougent l'un par rapport à l'autre), plus aucun dessin plat | capture dehors et depuis l'intérieur |
| R11 | **L'atmosphère** : une brume très légère dans les faisceaux des projecteurs | capture de nuit |
| R12 | **Le rendu propre** : pas de crénelage, pas de scintillement, étalonnage chaud cohérent, halo maîtrisé | captures zoomées |
| R13 | **Le test à l'aveugle** : trois personnes regardent trois captures et répondent « photo ou 3D ? » ; au moins une hésite sur chaque capture | 🙋 Mongazi le fait faire |
| R14 | **Ça tourne** : 30 images/s au téléphone (le réalisme ne doit pas tuer la 3G ; c'est la vague 4 de l'audit) | `monde/_outils/mesurer.py` (à écrire) |
| R15 | Le bandeau « MAQUETTE » retiré | quand R1 à R14 sont vrais |

## L'avancement, critère par critère

- ✅ **R1 · la lumière cuite (2026-11-13, FAITE)** : la chaîne marche de bout en bout.
  `exporter_decor.py` (toute la scène, clés stables, lampes orientées, lampes de cuisson) →
  `cuire.py` (Blender sans fenêtre : dépliage commun, occlusion + lumière des 25 lampes, lissage, export) →
  `appliquerCuisson()` (géométrie recousue, `aoMap` + `lightMap`, lampes en direct coupées sur les surfaces
  cuites du dedans, force qui suit l'allumage des projecteurs et la nuit). Les dix pièges rencontrés :
  `_memoire/apprentissages/2026-11-13-cuisson-lumiere-blender-threejs.md`. Essais en 1024 px : la version
  cuite est plus juste que la version en direct (dégradés, ombres sous les tables, ombre des panneaux sur
  le podium). **Reste** : cuisson finale en 2048 px, comparaison jour et nuit, téléphone, regard dans Chrome,
  poids (WebP), QC, puis « est-ce que ça suffit ? ».
  **Livré** : cuisson 2048 px (occlusion 128 échantillons, lumière des 25 lampes 256 échantillons, lissage 3),
  cartes en WebP (204 + 156 Ko au lieu de 4 Mo), force réglée à l'œil **dans Chrome** à 0,8 (le podium ne
  brûle plus), les **reflets des lampes gardés en direct** sur le marbre (seule la part diffuse est cuite),
  regardé de nuit et de jour, à l'ordinateur et au téléphone, avec et sans cuisson : la version cuite est
  plus juste partout (vraies flaques de lumière aux bords doux, ombres des panneaux sur le podium, ombres
  de la table dans les flaques, dégradés sur les étagères). QC **53/53** (un contrôle neuf : la lumière
  cuite est posée). **Ce qui n'en fait pas partie, dit franchement** : le dehors ne reçoit que l'occlusion
  (sa lumière reste en direct, R10 s'en occupera), les personnages n'ont pas encore d'ombre au sol (R2),
  la géométrie cuite pèse 1,6 Mo non compressée (R14). Refaire une cuisson : `cuire.py` puis
  `cuisson_finir.py` (en-tête de `cuire.py`).
- ✅ **R2 · les ombres de contact (2026-11-13)** : les objets posés ont la leur par la cuisson (R1) ; chaque
  personnage a une **ombre de contact** en direct (`ombreContact` dans `socle/matieres.js` : une ombre serrée
  et foncée au cœur d'une ombre large et douce ; avant, une seule tache pâle, ils flottaient), et un
  personnage habillé a en plus **une ombre sous chaque pied**, qui suit le pas et pâlit quand le pied se lève,
  l'ombre large suivant le bassin (`socle/habiller.js`). ⚠️ `renderOrder 2` : en qualité haute le sol est
  translucide, une ombre dessinée avant lui disparaissait. Regardé au téléphone et à l'ordinateur
  (`monde/_outils/captures/voir_ombres.py`). QC 53/53.
- 🔨 **R6 · le sol qui reflète, au téléphone aussi (2026-11-13, après-midi)** : en qualité haute, le `Reflector`
  d'avant ; en moyenne et basse, **le miroir par photo à 360° prise depuis L'ŒIL REFLÉTÉ sous le sol**
  (`poserRefletSol` dans `lieu.js`) : un sol plat reflète exactement ce que voit l'œil reflété en (x, −y, z),
  donc chaque point du sol lit la photo dans la direction « œil reflété → ce point ». Juste et net tant que le
  visiteur reste au même endroit ; **refaite quand il s'arrête ailleurs** (une face par image, aucun hoquet)
  et quand la lumière change. ⛔ **Le plan prévu le matin ne marchait pas** (une photo au centre projetée sur
  les murs, parallaxe en boîte) : un podium AU MILIEU de la pièce n'est pas sur les murs, et le centre de la
  pièce tombait dans les panneaux du podium central. Réglages : `?reflet-force=` (2,4) et `?reflet-irr=` (0,8),
  `?sans-reflet` pour comparer. Vu au téléphone : le podium et sa lumière se reflètent sous lui.
- Comparer à tout moment : `?sans-cuisson` (tout) ou `?sans-lumiere-cuite` (garder l'occlusion).

## Ce que JE fais (sans attendre personne) : R1 à R6, R9 à R12, R14

Dans l'ordre de ce qui rapporte le plus :
1. **La lumière cuite** (R1, R2, R6) : `monde/_outils/cuire.py` pour Blender
   (`D:\Blender\blender.exe -b -P monde/_outils/cuire.py`), à partir du décor déjà exporté
   (`python monde/_outils/exporter_decor.py` → `monde/_cuisson/salon-decor.glb`) ; cartes de lumière
   rechargées dans three.js (`material.lightMap`, UV2, retrouvées par le nom `decor-N`) ; une sonde de
   lumière pour que les personnages baignent dans la même lumière.
2. **Le plafond de l'étalon** (R5) et **le sol qui reflète** (R6).
3. **Les matières et les objets** (R3, R4) : remplacer tout ce qui est encore en primitive ou en
   couleur unie (Poly Haven CC0, `monde/_outils/polyhaven.py`).
4. **La densité** (R9).
5. **La rue** (R10) : une image de rue de Cotonou en plusieurs plans. ⚠️ La règle NEBULA autorise une
   **image générée pour un lieu ou une ambiance** (jamais pour le catalogue) : je peux la générer
   (Cloudflare, gratuit ; ou WaveSpeed `nano-banana-pro`, 0,14 $ l'image, solde actuel 0,04 $).
   Une vraie photo de rue prise par Mongazi serait meilleure.
6. **L'atmosphère et le rendu** (R11, R12).
7. **La mesure au téléphone** (R14), en même temps que la vague 4 : les cartes de lumière ajoutent
   du poids, donc la compression (KTX2) vient avec.

## Ce qu'il faut de MONGAZI pour atteindre 100 %

| Quoi | Pour quel critère | Sans ça |
|---|---|---|
| **Les planches des robes** (`PROMPTS-ROBES-3D.md`, 18 pièces), puis **la validation d'Hillary pièce par pièce** | R7 | les robes restent des photos sur panneaux : le réalisme plafonne, et c'est le produit |
| **Sènami et Maman Sènami en 3D** (il les génère, `personnages/CONSIGNES.md`) | R8 | silhouettes de maquette |
| **Les photos d'Hillary et son accord écrit** | R8 | Hillary reste une silhouette |
| **Laisser le PC allumé une nuit** quand je lance la cuisson (Blender, sur le processeur de ce PC) | R1 | pas de lumière cuite |
| **Les images faites pour le salon** qu'il avait annoncées le 2026-11-12 (« je vais t'envoyer d'ici là les images faites pour le salon ») : **jamais arrivées**. À défaut, l'étalon reste la photo de vision d'Hillary | toutes | je vise la photo de vision |
| Une **vraie photo de rue de Cotonou** (facultatif, sinon je la génère) | R10 | image générée |
| **Le test à l'aveugle** auprès de trois personnes | R13 | pas de preuve extérieure |
| **L'essai sur son téléphone** | R14 | mesure faite sur ce PC seulement |
| Recharger WaveSpeed (≈ 40 $, facultatif) | R7, R10 | voie gratuite, plus lente et moins fine |

## La méthode, fixée par Mongazi (2026-11-13)

> « je t'envoie les assets tout à l'heure ; en attendant, concentre-toi sur ce que tu peux faire toi.
> Atteins 100 % de chacun en te demandant à chaque fois si ça suffit, regarde ce que tu fais avec Chrome
> et améliore jusqu'à ce que ce soit parfait et à 200 % pour chacun des points, et fais ça un à la fois,
> et termine toujours un avant d'enchaîner l'autre. »

- **Un critère à la fois**, dans l'ordre de « Ce que JE fais » : on ne commence pas le suivant tant que
  le courant n'est pas à 200 %.
- **Regarder dans Chrome** (l'extension Claude pour Chrome, `/chrome`), au téléphone et à l'ordinateur,
  pas seulement des captures Playwright ; à chaque tour se demander « est-ce que ça suffit ? » et
  améliorer tant que la réponse est non.
- Les apports de Mongazi (« les assets ») arrivent plus tard : R7 et R8 attendent.

## L'ordre proposé (à confirmer par Mongazi)

La prochaine vague prévue était la **4 (la 3G)**. Je propose de traiter **le réalisme d'abord, en
commençant par la lumière cuite** (vague 5 de l'audit), et d'y fondre la compression 3G : la lumière
cuite, c'est précisément ce qui donne du réalisme **sans** charger le téléphone.
