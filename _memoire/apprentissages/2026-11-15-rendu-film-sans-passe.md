# Un rendu « de film » sans passe d'image : étalonnage, faisceaux, soleil par la vitrine

> LE MONDE, vague 2, 2026-11-15. Mongazi : « ne plafonne pas à GTA 2001, monte à GTA 2026 », « dantesque, spectaculaire,
> un vrai salon de couture ». Contrainte : un téléphone en 3G, et son PC (Intel HD 5500) qui tourne en qualité
> « moyenne », donc SANS aucune passe d'image. Code : `monde/socle/moteur.js` (LOOK), `socle/faisceaux.js`,
> `socle/soleil-vitrine.js`, `socle/ciel.js` (`capFacade`). Captures : `_outils/captures/voir_salon.py` (GL=gpu, EXTRA),
> `voir_soleil.py`. QC : § 13 et § 14 de `monde/_qc.py` (66/66).

## Ce qui a été fait, et ce que ça coûte

| Quoi | Comment | Coût |
|---|---|---|
| **Étalonnage de film pour TOUTES les qualités** | l'AgX de three.js recopié dans `CustomToneMapping`, avec un « look » (pente, puissance, saturation : ASC CDL) posé dans le domaine encodé d'AgX, là où Blender pose les siens. `THREE.ShaderChunk.tonemapping_pars_fragment` remplacé au chargement | quelques opérations par pixel, zéro passe |
| **Vignettage** | un `div` en dégradé radial par-dessus le canevas (« moyenne », « basse ») ; la passe d'étalonnage de la « haute » ne garde que vignettage et grain | une couche du navigateur, sans `mix-blend-mode` |
| **Faisceaux visibles + poussière** | un cône additif par projecteur (épaisseur traversée, bruit lent) et des points qui dérivent ; aucun en « basse » | 4 cônes + 4 nuages de 36 points en « moyenne » |
| **Brume de profondeur** | `FogExp2` 0,012 le jour, 0,018 le soir (6 % à 20 m) | nul |
| **Soir plus tamisé** | lampes à 34 % (avant 45 %), exposition du soir 0,92 | nul |
| **Le soleil par la vitrine** | chaque ouverture de la façade PROJETÉE sur le sol le long du vrai soleil (un quadrilatère par ouverture) : la flaque est exacte, s'allonge quand le soleil descend, glisse avec l'heure ; ombre des montants ; coupée aux murs | 3 quadrilatères |

Mesuré (Playwright sur ce PC, format téléphone, « moyenne ») : **53 i/s immobile, 44 en marchant** (avant : 60 et 40).

## Les pièges, dans l'ordre où ils ont mordu

1. **`let` lu avant sa ligne = page morte.** Le module du lieu `await` des chargements pendant que des images sont déjà
   rendues : une fonction appelée à chaque image lisait `nuitCuite`, déclaré 800 lignes plus bas → « Cannot access
   before initialization » à CHAQUE image, et `window.__monde` jamais défini. Déclarer la variable avant son premier
   usage dans une fonction de rendu.
2. **`long` est un mot réservé de GLSL** (comme `half`, `input`, `output`, `sample`, `filter`…) : le shader ne compile pas,
   et three.js l'écrit dans la console, pas dans une exception.
3. **L'étalonnage a deux réglages qui dérapent vite** : à pente [1,03 ; 1 ; 0,955] les murs crème viraient au PÊCHE ;
   à puissance 1,16 les personnages du soir devenaient NOIRS. Retenu : [1,018 ; 1 ; 0,975], 1,11, saturation 1,12.
4. **Un faisceau additif voile ce qu'il éclaire.** À l'ordinateur (« haute » : 7 projecteurs + halo), un voile blanc
   couvrait la robe du premier plan : l'inverse du but. Trois corrections : le cône s'efface à moins de 1,2 m de son
   axe (de près on est dedans, on ne le voit pas), il est dense à la source et DISSOUS avant la pièce (tiers bas), et
   sa force est divisée par deux là où un halo l'amplifie.
5. **Le soleil ne « recouvre » pas le sol, il l'ÉCLAIRCIT.** En additif, la flaque était un aplat blanc sans matière.
   Mélange `DstColor, One` : sol × (1 + soleil) : le grain, les joints et les ombres de contact restent. Et quand le
   soleil entre, l'exposition du reste de la pièce baisse de 10 % (un appareil photo se règle sur le soleil).
6. **L'azimut de Meeus part du SUD, vers l'ouest** (azimut de boussole = azimut + 180). J'avais cru la façade au nord :
   elle regardait le sud. Écrit maintenant dans `capFacade` (degrés de boussole, 180 par défaut).
7. **L'orientation d'un lieu inventé est un choix de mise en scène.** Façade au sud-ouest (215°) : le soleil entre
   tous les après-midi de l'année (plein sud : jamais de mai à juillet à Cotonou, 6° N).
8. **L'ombre d'un montant se dissout avec la distance** (pénombre du soleil : 9 mm par mètre) : nette au pied du
   vitrage, effacée au bout. Uniforme, elle faisait des lignes roses sur une flaque jaunie par l'écrêtage.
9. **Une capture en « haute », le soir, dépasse 30 s sur ce PC** : `screenshot(timeout=120000)`, et une capture ratée
   ne doit pas tuer la série.

## Les notes (sur 10), honnêtes

| Critère | téléphone jour | téléphone soir | ordinateur jour | ordinateur soir |
|---|---|---|---|---|
| 1 · lumière | 5 → 7 | 4 → 7,5 | 6 → 7 | 6 → 7,5 |
| 3 · profondeur | 5 → 6,5 | 5 → 6,5 | 5,5 → 6,5 | 5,5 → 7 |
| 5 · étalonnage | 4 → 7,5 | 4 → 8 | 5,5 → 7,5 | 6 → 8 |
| 7 · « waouh » | 4 → 6,5 | 4 → 7 | 5 → 6,5 | 5,5 → 7 |

⛔ **Le seuil de 8 n'est PAS atteint partout.** Le rendu a donné ce qu'il pouvait sur un décor en boîtes : ce qui retient
la note, ce sont les MATIÈRES (surfaces unies : vague 3) et le décor lui-même (monde photographique : vague 4).


## Vague 3 (le même jour) : de vrais imprimés à la place de motifs dessinés

- **Les tissus wax du décor étaient DESSINÉS par le code** (cercles, feuilles, losanges) : c'est ce qui se voyait le
  plus. Huit imprimés originaux générés gratuitement (FLUX.1 schnell, Apache 2.0, `scripts/image_cf.py`), 384 px en
  WebP, 344 Ko en tout, posés APRÈS le premier écran dans le canevas de chaque texture (`chargerWaxPhotos`).
- ⛔ **Redessiner un canevas et prévenir la texture d'ORIGINE ne suffit pas quand les matières portent des COPIES**
  (`texture.clone()` pour une répétition propre) : three.js ne renvoie une texture à la carte graphique que si SA
  version change, et l'original n'est porté par aucune matière. Les rouleaux gardaient leur dessin, sans erreur.
  Prévenir chaque copie (`needsUpdate`).
- **Un imprimé fin se délave de loin** : en mosaïque 2 × 2 les motifs devenaient une bouillie pastel, et les trois
  imprimés à fond clair pâlissaient les étagères. Motif en entier dans le canevas + répétition EN MIROIR (raccord sans
  couture), fonds colorés, +18 % de couleur.
- **Regarder le code avant d'ajouter** : le sol, les murs, le chêne et le velours portaient déjà des matières scannées
  (Poly Haven, posées par `embellir()`). Mes reliefs calculés par-dessus ne changeaient presque rien, et le laiton
  « patiné » à 0,9 de contraste paraissait SALI en gros plan (ramené à 0,3).
- Le filtre de Cloudflare a refusé un des huit prompts pour « contenu NSFW » (un faux positif sur des losanges
  bruns) : reformuler, ne pas insister.
