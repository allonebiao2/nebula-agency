# Ajouter un plat à la carte d'Au Braisé d'Or, de bout en bout

*(2026-09-15, en ajoutant l'attiéké. À relire avant de toucher à cette carte.)*

## ⚠️ LA CARTE NE S'ÉDITE PAS LÀ OÙ ELLE S'AFFICHE

`experience/data/carte.ts` est **généré**. L'éditer à la main marche jusqu'à la
prochaine régénération, qui efface tout sans un mot. La vérité est le tableau
**`CATS` de `clients/09-au-braise-dor/index.html`** — le vieux site, qui n'est
plus servi mais reste la source.

## La chaîne, dans l'ordre

1. **`index.html`, tableau `CATS`** : ajouter l'objet du plat dans sa rubrique.
2. **`index.html`, table `PHOTO`** : `'nom du plat en minuscules': 'cle-fichier'`
   — ⛔ **seulement si le fichier existe**. Sans entrée, le générateur n'écrit
   aucun `img` et la carte pose **l'ardoise** (le nom sur la pierre). Avec une
   entrée sans fichier, on fabrique un lien mort.
3. **L'image, aux DEUX endroits** : `assets/images/<cle>.webp` **et**
   `experience/public/carte/<cle>.webp`. Écrire une seule des deux laisse une
   carte à moitié illustrée sans que rien ne le signale.
4. **`node _outils/_extraire_carte.js`** — il dit combien de plats et lesquels
   sont sans photo.
5. **`cd experience && npm run build && cp -r ../assets/docs out/`**
6. **`python _outils/_qc.py`** et **`python _outils/_qc_partage.py`**, tous
   verts.
7. **Regarder les captures** : `python _outils/_vues_attieke.py` (ou la vue de
   la rubrique concernée), en **390 ET 1440**.
8. Publier : `wrangler pages deploy out --project-name au-braise-dor --branch main`,
   jeton dans `secrets/cloudflare.env`.

## ⚠️ Un champ neuf se déclare à TROIS endroits

Le générateur écrit **le type ET les données**. Un champ ajouté dans `CATS`
sans être appris au script disparaît en silence à la régénération :

- le gabarit du `type Plat` dans `_extraire_carte.js` (le commentaire qui dit
  **pourquoi** le champ existe part avec) ;
- la sérialisation du plat, dans le même fichier ;
- le composant qui l'affiche, `experience/components/Carte.tsx`.

## Les cinq façons d'avoir un prix, et la sixième qui n'en est pas une

`p` simple · `p2` deuxième taille · `pMax` fourchette · `paliers` barème à N
crans · `p: 0` prix sur demande. Et **`choix`**, qui n'est **pas** un prix :
un choix obligatoire **à prix égal** (poisson ou viande). ⚠️ Le tordre dans
`p2` affiche « 2 000 F / 2 000 F » sur la pastille ; dans `garn`, il devient
facultatif et censé faire monter le prix.

⚠️ **Le balisage JSON-LD suit** : `pMax` → `AggregateOffer`, `p2` → 2 offres,
`paliers` → N offres, `p: 0` → aucune. `choix` n'en change aucune, et c'est
juste : le prix ne bouge pas.

## ⚠️ Ce qu'un plat neuf peut casser sans qu'on y pense

- **Les notes de rubrique sont des phrases, que rien ne vérifie.** Celle des
  Grillades énumère les accompagnements, dont l'attiéké.
- **La rubrique « Sauces » alimente aussi le héros** (`dishes.ts` la lit) : un
  plat ajouté là y entre tout seul et réclame une entrée `DECO`.
- **Un plat sans photo redevient le sujet du contrôle « ardoise »** du QC, ce
  qui déplace le clic de plusieurs contrôles.
