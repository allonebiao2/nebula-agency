# HILLARY M. STYL — les images à apporter, niveau par niveau

> **La V4 « LA COUPE » est en ligne et fonctionne sans une seule photo.**
> Chaque emplacement montre un dessin au trait. Ce document dit, pour chaque
> niveau : combien d'images, quel cadrage, et **où exactement** on les pose.
>
> Ordre d'importance : **le carrousel du catalogue d'abord** (c'est lui qui
> déclenche les commandes), puis le héros, puis le lookbook.

---

## Comment on pose une image, dans tous les cas

Tout se règle **en haut de la partie « mouvement »** de `_vitrine_src.html`,
dans deux tableaux. Il suffit de remplir le champ `f` :

```js
var HERO = [
  { f:'robe-01.webp', col:'Sur-mesure', ... },   ← le nom du fichier suffit
];
var COLLECTIONS = [
  { f:'piece-01.webp', l:'Sur-mesure', t:'Robe droite', ... },
];
```

Les fichiers vont dans `assets/images/`. Puis :

```bash
python3 _build.py     # reconstruit vitrine.html
python3 _qc.py        # 74 contrôles, doit finir « TOUT EST VERT »
python3 _predeploy.py # vérifie tout et prépare _dist/
```

**Format de sortie** : WebP qualité 82, **250 Ko par image, 400 Ko maximum**.
À Cotonou le site se charge en 4G ; une photo de 3 Mo, personne ne la voit.

---

## NIVEAU 1 · LE HÉROS — le slider éditorial
**4 photos** · format portrait **4:5** · 1200 px de large minimum
→ `HERO[].f` dans `_vitrine_src.html`

| # | Ce qu'on veut voir | Pourquoi celle-là |
|---|---|---|
| 1 | Une pièce **sur-mesure** portée, en pied | c'est le cœur du métier |
| 2 | Une pièce en **pagne ou wax**, portée en pied | la maison fait tout, il faut le montrer |
| 3 | Une pièce de **prêt-à-porter** | l'autre moitié de l'offre |
| 4 | Une **tenue de cérémonie** | le budget le plus élevé |

### ⚠️ Le point qui décide de tout : le fond
**Fond blanc uni, impérativement.** Un drap blanc lisse tendu contre un mur
suffit. C'est l'uniformité du fond qui permet au grand chiffre « 01 » de passer
**derrière** le mannequin et au nom de la maison de le chevaucher. Avec un fond
chargé, l'effet tombe et il ne reste qu'une photo dans un cadre.

- Mannequin **en pied**, de face, cadré du sol au-dessus de la tête.
- Lumière douce, de côté. **Jamais de flash direct** : il écrase le tissu.
- Les 4 photos **prises au même endroit, avec la même lumière**. Une série,
  pas quatre photos.

---

## NIVEAU 2 · L'ATELIER — trois plans empilés
**3 photos** · format portrait **3:4** · 900 px minimum
→ section « LA MAISON », emplacements `.plan--1/2/3`

| # | Sujet | Légende affichée |
|---|---|---|
| 1 | Un rouleau de tissu, pagne ou wax, vu de près | **Le tissu** |
| 2 | Un patron tracé, une craie, un mètre-ruban | **Le patron** |
| 3 | Un détail de couture ou de broderie, en gros plan | **La finition** |

Fond sombre ou neutre : elles s'affichent sur fond encre. Ce sont des plans
**rapprochés** : on doit voir la matière, pas la pièce entière.

---

## NIVEAU 3 · LE CARROUSEL DES COLLECTIONS — ⭐ LE PLUS IMPORTANT
**6 à 8 photos** · format portrait **4:5** · fond neutre clair
→ `COLLECTIONS[].f`

**C'est le seul écran qui déclenche un achat.** Une photo par pièce phare,
avec son vrai nom, sa vraie matière, son vrai prix.

- Fond uni **clair** (blanc ou gris très clair), le même pour toutes.
- La pièce **entière** dans le cadre, portée ou sur cintre.
- Bien éclairée, sans ombre dure.
- **La même distance et le même cadrage pour toutes les six** : c'est ce qui
  donne l'effet de défilé quand on fait glisser.

### Et avec chaque photo, ces cinq informations
```
Nom · Matière · Prix · Délai (jours) · Prêt-à-porter ou sur-mesure
```

⚠️ **Les 12 pièces actuellement dans le catalogue sont des EXEMPLES.** Une
cliente peut commander aujourd'hui une « Robe Amazone » qui n'existe pas.
C'est le point le plus urgent du dossier, avant même les photos du héros.

---

## NIVEAU 4 · LE LOOKBOOK — la mosaïque
**6 photos** (jusqu'à 12 si elle en a) · formats **variés**, c'est voulu
→ emplacements `.lk--1` à `.lk--6`

| # | Format | Sujet |
|---|---|---|
| 1 | 4:5 portrait | une silhouette complète |
| 2 | 1:1 carré | un détail de tissu, très près |
| 3 | 3:4 portrait | un portrait, ou une pièce portée de dos |
| 4 | 4:5 portrait | une autre silhouette |
| 5 | 5:4 paysage | l'atelier, ou une table de travail |
| 6 | 3:4 portrait | un détail : un bouton, un ourlet, une broderie |

Elles s'affichent **en noir et blanc** et reprennent leurs couleurs au survol.
Prendre les photos **en couleur** : c'est le site qui les décolore.

Ce sont des photos **éditoriales**, pas des photos de catalogue : on cherche
l'ambiance, le mouvement, la lumière. Elles peuvent être moins « propres ».

---

## NIVEAU 5 · LE CATALOGUE COMMANDABLE
**1 photo par pièce** · format **4:5** · fond neutre
→ champ `img` de chaque entrée de `PIECES` (moteur de commande)

Aujourd'hui chaque carte affiche le monogramme et « Photo à venir ». Ce sont
les mêmes photos qu'au niveau 3 : une pièce photographiée sert aux deux.

---

## 🎬 LES VIDÉOS — non demandées, mais ce qui ferait l'écart

| Où | Durée | Quoi |
|---|---|---|
| **Fond de héros** | 6 à 10 s, en boucle, **muette** | un tissu qui tombe au ralenti, ou une main qui pique à la machine. Remplace la première diapositive. |
| **Entre deux sections** | 8 à 12 s | ciseaux qui coupent, épingles, la craie sur le tissu. |
| **Une pièce portée** | 15 à 20 s | une cliente qui tourne dans une tenue finie. **Le meilleur argument qui existe** : c'est ce qu'aucune photo ne montre, le tombé. |

⚠️ **Toute vidéo tournée au téléphone est en HEVC** et ne se lit ni dans Chrome
ni dans Firefox. Il faut la transcoder en H.264 :

```bash
ffmpeg -i entree.mov -c:v libx264 -pix_fmt yuv420p -an \
  -vf "scale='min(1080,iw)':-2,fps=30" -crf 30 -movflags +faststart sortie.mp4
```

Viser **moins de 500 Ko** par boucle.

---

## Récapitulatif — ce qu'on demande à Hillary, en une fois

| Niveau | Nombre | Fond | Format |
|---|---|---|---|
| ⭐ Carrousel / catalogue | **6 à 8** | uni clair | 4:5 |
| Héros | **4** | **blanc uni impératif** | 4:5, en pied |
| Lookbook | **6 à 12** | libre | variés |
| Atelier | **3** | sombre ou neutre | 3:4, gros plan |
| Vidéos | 1 à 3 | libre | H.264, < 500 Ko |

**Plus, pour chaque pièce du catalogue** : nom, matière, prix, délai, et si
c'est du prêt-à-porter ou du sur-mesure.

---

*NEBULA Agency · Cotonou · document écrit le 2026-08-06, à jour de la V4.*
