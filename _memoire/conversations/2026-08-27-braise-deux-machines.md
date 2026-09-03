# Au Braisé d'Or — deux machines ont fait le même travail, et personne n'a affiché le résultat

*2026-08-27. Client 09. La session devait « commiter et pousser ce qui traîne ».
Elle a trouvé le même travail fait deux fois, et un héros qui posait des
ardoises sur des photos déjà livrées.*

---

## Ce qu'on croyait faire, et ce qu'il y avait vraiment

Le PC de Cotonou avait, **non commité**, tout le travail des six dernières
sauces : les images posées, deux outils neufs (`_damier_vers_alpha.py`,
`_poser_sauces.py`), `carte.ts`, `dishes.ts`, `index.html`, un correctif du QC.

`git fetch` a montré autre chose : **`origin/main` portait déjà les mêmes six
sauces**, poussées la veille en **7 commits** (`fb93ec7` → `aeba870`) par une
session lancée depuis le téléphone. Mêmes photos sources — au bit près, git les
a reconnues comme de simples renommages `2026-08-26-*` → `2026-08-27-*`.

**Deux machines ont refait le même travail, avec deux chaînes d'outils
différentes, sans jamais se voir.**

---

## ⛔ POURQUOI PERSONNE N'A RIEN VU : `rapatrier.py` NE REGARDAIT PAS `main`

Le script de début de session, celui qui existe précisément pour ça, avait une
ligne qui disait :

```python
if not b or b.endswith("/HEAD") or b == "origin/main":
    continue
```

Il inventoriait **les branches `claude/…`** et **excluait `origin/main`**.
Or **une session lancée depuis le téléphone pousse DIRECTEMENT dans `main`.**
Le script répondait donc « ✅ Rien ne traîne : tout est déjà dans `main` »
pendant que `main` distant avait sept commits d'avance.

⚠️ **« Rien ne traîne sur les branches » ne veut pas dire « je suis à jour ».**

**Corrigé** : `main_en_retard()` s'exécute **avant** l'inventaire des branches,
liste les commits manquants et refuse de dire que tout va bien. Une branche
oubliée coûte une fusion ; **un `main` en retard coûte le travail refait deux
fois**.

---

## Ce qu'on garde, et pourquoi ce n'est pas le travail local

Les deux chaînes marchent. **Celle de `main` est plus mûre**, et elle avait
déjà tranché ce que la locale venait de réinventer :

| | version locale (écartée) | version `main` (gardée) |
|---|---|---|
| découpe | damier reconnu aux gris + propagation depuis les bords | **`rembg`/`isnet-general-use`** |
| cadrage | carré sur la boîte du sujet, marge fixe 1,16 | **gel par photo**, décidé à l'œil |
| QC | ouvre le 1er plat venu | **sépare l'ardoise de l'accompagnement**, ouvre une SAUCE |

⛔ **Et le local avait réinventé une approche déjà mesurée et rejetée.** C'est
écrit dans `_damier.py`, sur `main`, depuis le 19/08 : *« on apprend les gris
sur les coins, on remplit depuis les bords… quatre tours, et un échec de fond :
sur le gombo, les deux gris du damier sont 77 et 124, et le bord noir de
l'assiette a des reflets dans cette plage. Aucun seuil de luminance ne les
sépare. »*

⛔ **Le QC local sortait à 89 verts / 5 rouges.** Son correctif gardait deux
assertions sans rapport accrochées au même clic : l'**ardoise** (un cas
particulier qui peut disparaître) et l'**accompagnement obligatoire** (une
règle métier valable pour tout plat). La version de `main` les sépare et ouvre
une sauce, catégorie qui exige toujours un accompagnement. **Mesuré ici après
câblage du héros et ajout du contrôle des orphelines : 93 verts, 0 rouges.**

**Le commit local `70e3d8b` est donc écarté**, pas perdu : il reste dans le
reflog, et les deux scripts sont archivés hors dépôt. Le garder aurait posé un
piège réel — `_poser_sauces.py` aurait **réécrit en silence** les cadrages que
`_photos_sauces.py` gèle exprès, ce que ce fichier documente noir sur blanc.

---

## ⛔ MAIS LES DEUX AVAIENT RAISON SUR UN POINT, ET `main` AVAIT TORT

Les six découpes de sauce étaient dans `main` : fichiers propres, pesés,
poussés, en 200. **Et le héros posait quand même son ardoise.**

Parce que le héros ne lit pas le dossier, il lit le `DECO` de `dishes.ts` :

```ts
img: d?.img,     // d = DECO[nom]  →  absent = ardoise
```

et **aucun des 7 commits n'a touché `dishes.ts`**. Six images livrées,
affichées nulle part, sur **le premier écran du site**.

⚠️ **RIEN NE POUVAIT LE SIGNALER.** Le contrôle « 0 image cassée » ne voit que
les images **demandées**. Une image qu'on ne réclame jamais ne peut pas être
cassée : elle est parfaite et invisible. **Un fichier livré n'est pas un
fichier affiché.**

C'est la seule chose que le travail local avait et que `main` n'avait pas.
C'est ce qui a été repris : les six `img:` du `DECO`, les six correspondances
de `index.html`, et les images de carte manquantes dans `assets/images/`
(la page de repli en réclamait déjà trois qui n'existaient pas).

**Nouveau contrôle, pour que ça ne se reproduise pas** :

> *aucune découpe inutilisée dans `/plats`*

Il lit les **deux** côtés dans les fichiers, sans recopier aucune liste : le
jour où une sauce arrive, il la réclame tout seul.

---

## État de la carte, après cette vague

| | avant | après |
|---|---|---|
| plats illustrés | 46 / 52 | **52 / 52** |
| sauces montrées au héros | 6 | **12** |
| ardoises rondes au héros | 8 | **2** |

Les deux qui restent sont **Béchamel** et **Crème** : elles n'auront **jamais**
de découpe (plat noir sur fond noir, noté depuis le 19/08). Leur ardoise ronde
au filet de la couleur de la sauce est le rendu définitif, pas un pis-aller.

---

## Les trois leçons

1. **`git fetch` se fait AVANT de travailler, pas avant de pousser.** Le
   cerveau dit déjà de récupérer `main` avant de fusionner ; ce qui manquait,
   c'est de le faire **au premier geste de la session**. Le script le dit
   maintenant tout seul.
2. **Un fichier livré n'est pas un fichier affiché.** Vérifier qu'une image
   existe, pèse, répond 200 et n'est pas cassée ne prouve **rien** : il faut
   vérifier qu'elle est **demandée**. Le manque est silencieux par nature.
3. **Quand deux versions du même travail existent, on ne fusionne pas : on
   compare et on tranche.** Ce qui départage, ce sont les mesures déjà écrites
   dans les fichiers (« 77 et 124 », « 23,4 % contre 49,6 »), pas l'ordre
   d'arrivée ni l'attachement à son propre code.

---

## Ce qui reste ouvert sur ce client

- ⛔ **LE SITE A TOUJOURS DEUX NUMÉROS WHATSAPP** : `index.html` porte
  `2290156057157`, `dishes.ts` (**le fichier réellement servi**) porte
  `22956057157` — **le `01` a sauté**. Rien n'est touché, à trancher.
- ⏳ aileron : correction manuscrite au surligneur, toujours illisible.
- ⏳ napolitaine et oriental : une 2e taille absente du site.
- ⏳ vraie photo de la salle, vrais avis, adresse/Maps, logo, réseaux.

### ⏳ VU EN REGARDANT LES 12 DÉCOUPES : LA VAPEUR DE `sc-moyo` ET `sc-poisson`

Les douze découpes ont été posées côte à côte sur le crème du site
(`#ede9e3`) et regardées. Onze sont propres : assiette entière, aucun halo,
aucun escalier dans le bord. **Deux ne le sont pas.**

Sur **`sc-moyo`** et **`sc-poisson`**, le **panache de vapeur** est sorti du
masque en **forme pleine, gris foncé et opaque** : au-dessus du plat flotte
une silhouette qui ressemble à une **anse ou un crochet**, pas à de la vapeur.
Sur fond blanc ça passe ; sur le crème du héros, c'est une tache.

⚠️ **Ce n'est pas un défaut du 27/08** : ces deux découpes sont en ligne depuis
le 26/08, elles n'ont pas été retouchées aujourd'hui. Personne ne l'avait vu
parce qu'on regarde les images **une par une** — c'est en les mettant **toutes
les douze ensemble** que les deux intruses sautent aux yeux.

**Le remède est déjà écrit dans `_damier.py`** : c'est la « rustine
anti-vapeur », dont la note dit qu'elle ne servait plus sur la krinkrin
(9 lignes étroites, largeur croissante = le coin de l'octogone). Sur ces deux
plats-là, il y a bien un panache. ⚠️ **Refaire la planche comparative des
modèles pour ces deux photos** avant de choisir : `isnet` gagne sur damier,
`birefnet` sur fond noir, et **le fond change le gagnant**.
