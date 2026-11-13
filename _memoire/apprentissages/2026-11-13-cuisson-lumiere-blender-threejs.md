# Cuire la lumière d'une scène three.js dans Blender, et la rendre à la page (2026-11-13)

> Né sur LE MONDE (salon d'Hillary), critère R1 de `monde/REALISME.md`. La chaîne :
> `monde/_outils/exporter_decor.py` (la page exporte son décor) → `monde/_outils/cuire.py` (Blender sans
> fenêtre : dépliage, cuisson Cycles, export) → `appliquerCuisson()` dans `lieux/hillary-m-styl/lieu.js`.

## Le principe

Un téléphone ne calcule pas les ombres douces ni les rebonds. On les calcule **une fois** dans Blender
(Cycles), sur une 2e coordonnée de texture (`uv1`), et la page les **affiche** : `aoMap` (occlusion) et
`lightMap` (lumière des lampes), toutes deux sur `texture.channel = 1`. Le soleil et le ciel restent en
direct (le jour et la nuit réels jouent encore).

## Les pièges, dans l'ordre où ils ont mordu

1. **L'occlusion seule ne se voit presque pas sous des projecteurs.** Dans three.js, `aoMap` n'assombrit
   que la lumière INDIRECTE (ciel, environnement, carte de lumière). Un salon tamisé éclairé par ses
   lampes ne change presque pas. Il faut cuire **la lumière des lampes** et couper leur calcul en direct sur
   les surfaces cuites.
2. **Couper les lampes en direct sur une matière** : dans three.js r180, `lights_fragment_begin` enchaîne
   les boucles des lampes ponctuelles et des projecteurs juste avant celle du soleil. On coupe de
   `#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )` à `#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )`
   dans `onBeforeCompile`, avec une `customProgramCacheKey` à part. Une matière partagée avec le dehors ou
   avec un objet non cuit est **clonée** pour le dedans.
3. **Un nom stable pour chaque maillage**, le même à chaque chargement ET à chaque qualité : signature de
   l'objet de premier niveau (forme, position au centimètre, orientation) + chemin. ⚠️ La forme se fige au
   premier calcul (une fois la géométrie cuite posée, le nombre de sommets change : 113 maillages sur 211
   seulement). ⚠️ **Blender tronque les noms à 63 caractères** : la clé voyage en empreinte FNV-1a.
   ⚠️ On exporte TOUJOURS avec `?sans-cuisson` (sinon on exporte les formes déjà recousues).
4. **Une matière par face** (meubles à lattes) : la forme revenue de Blender perd son découpage par
   matière, et three.js ne dessine RIEN d'un maillage à plusieurs matières sans groupes (deux meubles
   avaient disparu). Chaque groupe part en morceau séparé, la page recolle (`mergeGeometries(…, true)`).
5. **Un projecteur three.js vise sa CIBLE, glTF ne connaît que l'orientation du nœud** : sans `lookAt`, les
   7 projecteurs éclairaient le mur du fond dans Blender. Exporter une lampe neuve, orientée, cible en
   enfant à (0, 0, −1).
6. **Les unités : facteur 683.** L'import glTF de Blender convertit les candelas en watts (× 4π / 683), mais
   **ni l'émission des matières ni le ciel**. Une lueur de 0,047 au plafond (là pour qu'il ne vire pas au
   brun) devenait une lampe géante qui aplatissait la pièce ; un ciel « presque noir » (0,004) pesait autant
   que toutes les lampes et teintait tout de lavande. Règle : seuls les objets marqués `emetteur` émettent,
   à leur force ÷ 683 ; le ciel de la cuisson est noir. Avec ça, **la calibration physique tombe juste** :
   « diffuse sans couleur » de Blender = E/π, donc `lightMapIntensity` = échelle × π × 683.
7. **Cuire 206 objets un par un relance Cycles 206 fois** (7 min 30 pour un essai) : cuire une COPIE
   FUSIONNÉE en une passe (54 s), originaux masqués au rendu pour ne pas s'ombrer eux-mêmes.
8. **Changer l'espace colorimétrique d'une image Blender après y avoir écrit la régénère** : carte toute
   noire. Une image 8 bits est déjà en sRGB.
9. **Les lampes « peintes »** (flaques au sol, disques lumineux en `MeshBasicMaterial`) n'éclairent rien
   dans Blender : leur donner de vraies lampes **pour la cuisson seulement** (elles ne coûtent rien au
   téléphone) et masquer les flaques peintes. Un cône trop large fond les flaques en un éclairage plat.
10. **Le bruit** : `sample_clamp_indirect` contre les lucioles, puis un lissage qui ne déborde pas d'un îlot
    (convolution normalisée par le masque des îlots, en numpy dans Blender).

## Mesurer, pas croire

`monde/_outils/captures/regler_cuisson.py` photographie une
seule page pour plusieurs `__monde.cuisson.facteur` et mesure la luminance de zones fixes contre la
version `?sans-cuisson`. Les rapports chiffrés ont désigné chaque défaut avant l'œil.
