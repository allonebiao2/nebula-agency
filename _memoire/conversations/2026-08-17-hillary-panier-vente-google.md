# 2026-08-16/17 · Hillary M. Styl — le panier, ce qui fait vendre, la fiche Google

Trois demandes de Mongazi à la suite : **un panier** (« comme pour madame
Luxury, histoire que les clientes voient ce qu'elles commandent et les prix »),
puis **« fais tout avec ton expertise en vente, marketing et développement web
pour que tout soit parfait »**, puis **« fais la fiche Google Business »**.

---

## 1 · LE PANIER

**Avant**, une cliente qui voulait deux robes envoyait deux messages WhatsApp.
L'atelier recevait deux commandes sans savoir qu'elles allaient ensemble : même
cliente, une seule livraison, un seul règlement.

Le parcours passe d'une seule suite de cinq étapes à **deux parcours** :

| | |
|---|---|
| **La fiche d'une pièce** | mesures ou taille → délai → *Ajouter au panier* |
| **Le tiroir** | photo, mesures renseignées, délai, prix, quantité, modifier, retirer |
| **La commande** | livraison → coordonnées → récapitulatif → un seul message |

### Les calculs, et pourquoi ils sont ainsi

- une ligne = `expPrix` si express sinon `prix`, **fois la quantité** ;
- le total = somme des lignes **+ les frais de livraison une seule fois** ;
- les euros et les dollars = **la somme de SES valeurs**, jamais un taux ;
- le délai = **la borne haute de la pièce la plus lente**, plus l'acheminement.

⚠️ **Le délai d'une commande est celui de sa pièce la plus lente. Tout part
ensemble.** Annoncer la plus rapide fabriquerait une cliente déçue, exactement
comme annoncer la borne basse d'un délai. Quand le panier mélange express et
normal, l'écran le dit et propose deux envois séparés.

⚠️ **Aucun prix n'est stocké dans le panier**, seulement l'identifiant de la
pièce et les choix. Un panier oublié une semaine dans le navigateur ne peut donc
pas ressortir avec un prix périmé.

✅ **Les mesures déjà données se reportent** d'une pièce à l'autre quand le champ
existe dans les deux jeux : on ne remesure pas son tour de taille pour la
deuxième robe.

### Deux défauts trouvés en construisant

1. ⛔ **Le voile du panier avalait les clics 350 ms après sa fermeture.**
   `visibility` ne se dégrade pas en douceur : elle bascule à la **fin** de la
   transition. C'est `pointer-events` qui règle ça, immédiatement.
2. ⛔ **Le bouton du son se posait sur « Retour » et sur « Vider le panier »**
   (il est en `position:fixed` en bas à gauche). Le cacher aurait été plus
   simple, mais **le contrôle qualité l'a refusé** : une règle de la maison veut
   qu'il reste atteignable quand une fiche est ouverte. On lui réserve donc un
   couloir de 78 px dans les deux pieds de page.

---

## 2 · CE QUI FAIT VENDRE, ET QUI MANQUAIT

Audit avant de toucher à quoi que ce soit. **Trois défauts, et aucun ne se
voyait en regardant le site.** C'est ce qui les rendait durables.

### ⛔ Le lien partagé sur WhatsApp n'avait aucune image

Aucune `og:image`. Au Bénin, tout circule par WhatsApp : la maison apparaissait
comme **une ligne de texte grise** dans une conversation, à côté de liens qui,
eux, montrent une photo. C'est le défaut le plus coûteux commercialement qu'un
site puisse avoir, et il est **invisible depuis le site**.

`python _og.py` fabrique `og.jpg` (1200x630, 87 Ko) avec **sa vraie robe de
cérémonie détourée**, son encre, son magenta, son nom en Bodoni.
⚠️ **En JPEG, pas en WebP** : l'aperçu WhatsApp ne lit pas toujours le WebP.
⚠️ `_predeploy.py` ne copiait **que les `.webp`** : il copie maintenant tout ce
que la page réclame, sinon l'image restait sur le disque.

### ⛔ Un `FAQPage` déclaré, aucune question visible

Le JSON-LD annonçait une FAQ à Google alors que la page n'en portait aucune.
C'est contraire aux règles de Google, et surtout : **les six objections d'une
cliente n'étaient répondues nulle part**. Pire, les réponses balisées disaient
**« 7 à 14 jours »** contre « 2 semaines » sur chaque carte : la même
contradiction que celle corrigée le 2026-08-06 ailleurs.

Il y a maintenant une section **« Les questions »** en `<details>` (lisible sans
JavaScript, navigable au clavier), et **un contrôle compare le balisage et la
page question par question**, réponse par réponse. Ils ne peuvent plus diverger
en silence.

### ⛔ Aucun balisage produit, alors que les prix sont réels

Les 8 pièces chiffrées sont balisées `Product` + `Offer` (XOF, `MadeToOrder`,
photo). ⚠️ **Les fiches sont LUES dans `PIECES`** par l'assembleur, jamais
recopiées.

### Et un reliquat

La **meta description** annonçait encore « express en 1 à 3 jours ». C'est le
premier texte que lit Google. Corrigé, et un contrôle interdit désormais à ce
texte de contredire le catalogue.

Plus `robots.txt` et `sitemap.xml`, qui n'existaient pas.

---

## 3 · LA FICHE GOOGLE BUSINESS

⚠️ **Elle ne peut pas être créée depuis ici.** Google exige le **compte Google
de la propriétaire** et une **validation** (vidéo, courrier ou téléphone) que
personne ne peut faire à sa place. Au Bénin c'est très souvent la vidéo.

`clients/10-hillary-m-styl/GOOGLE-BUSINESS.md` contient donc **tout ce qui se
recopie** : nom, catégories, description de **665 caractères comptés** (limite
750), services avec les prix du catalogue, attributs, horaires à valider, zones
desservies, procédure étape par étape, et l'après (lien d'avis → QR, les cinq
premiers avis, une publication par semaine).

⛔ **Le nom doit être « Hillary M. Styl » et rien d'autre.** Ajouter des
mots-clés au nom est le motif n° 1 de **suspension** de fiche.

⛔ **Ce qui bloque : l'adresse.** Le site n'en affiche aucune, exprès (une
adresse inventée était restée en ligne). Google en demande une **même pour une
fiche « zone de service »**, où elle reste privée. Recommandation : zone de
service (Cotonou, Abomey-Calavi, Porto-Novo, Sèmè-Podji, Ouidah).

Les images sont prêtes : `_og.py` fabrique aussi **`google-logo.jpg` (720x720)**
et **`google-couverture.jpg` (1024x576)** à partir de son vrai logo et de sa
vraie robe.

⚠️ **La cohérence décide du classement local** : nom, ville et téléphone doivent
être identiques au caractère près entre la fiche et le site. Les données
structurées du site portent maintenant l'image, le logo et la fourchette de prix.

---

## Les neuf modèles reçus le 2026-08-16

Prix, délais, suppléments express et type de mesures : **tout est noté** dans
`_sources/hillary/PIECES-RECUES.md`, et les questions à lui poser dans
`QUESTIONS-A-POSER.md`.

⚠️ **Les photos ne sont pas des fichiers** : montrées dans la conversation,
jamais déposées sur le disque. Rien ne peut être détouré ni posé sur le site
tant qu'elles ne sont pas dans `_partage/`.

Mongazi a tranché : **on garde mes noms provisoires**, elle corrigera ce qui ne
lui va pas. Les neuf portent le même nom (« Robe de ville »), trois demandent
des **mesures combinées** (haut + pantalon, haut + jupe).

---

## L'état, en chiffres

| | |
|---|---|
| Contrôles qualité | **84 → 121** |
| Poids de la page | 240 Ko |
| Commits | panier · modèles · vente et marketing · fiche Google |
| Vérifié en ligne | tiroir, sous-total, date, `og.jpg`, robots, sitemap, 404 |

## Ce qui reste

1. **Les 11 mesures de la robe ovale** — toujours pas validées, tout en dépend.
2. **Les fichiers photo** des neuf modèles, dans `_partage/`.
3. **L'adresse**, les **horaires**, **trois photos d'atelier** et **son compte
   Google** pour la fiche.
4. De **vrais avis** : une fiche à zéro avis ne sort pas dans les résultats
   locaux, et on n'en invente aucun.

---

## 4 · LE HÉROS COMPLÉTÉ, ET UNE SIGNATURE PAR SECTION

Mongazi : « complète le héros en mettant juste les meilleures, dans le même
style » et « ajoute des animations différentes pour chaque autre section ».

### Le héros montrait 4 pièces sur 8

Les quatre reçues le 2026-08-10 n'y étaient **jamais passées**, ni au carrousel.

- **héros 4 → 7** : violette, Naja orange, verte. **La robe à tulle reste au
  seul carrousel** : son violet doublait celui de la violette, et deux nappes
  identiques qui se suivent ne se voient pas.
- **carrousel 4 → 8**.
- ⚠️ Les nouvelles diapositives pointent sur `piece-*.webp`, **la même photo
  détourée** : la réencoder en WebP une seconde fois ne ferait que la dégrader.
- ⚠️ La teinte de chaque pièce est relevée sur le tissu. **Le seuil de
  saturation à 0,35 écartait le fond sauge de la robe verte** : il ne restait
  que ses rubans ocre et sa nappe tombait sur celle de l'orange. À 0,22 on garde
  les tissus sourds, qui sont aussi des couleurs.

### Cinq sections partageaient la même révélation

Chacune a maintenant la sienne, tirée d'un geste de couture : **l'ourlet qu'on
déroule** (la maison) · **le portant** (les collections) · **les patrons qu'on
épingle** (le catalogue) · **le fil qui se dénoue** (les questions) · **la
couture qui se ferme** (le contact).

⚠️ `#grille` et `.faq-l` ont dû être **ajoutés à la liste balayée** : sans ça,
ils ne reçoivent jamais la classe `vu` et l'animation ne joue jamais.
⚠️ `section{overflow-x:clip}` posé en même temps : deux de ces animations
viennent du côté et poussaient la page, exactement comme les 6 px du site de
l'agence.

## 5 · DEUX PIÈGES, PAYÉS COMPTANT

1. ⛔ **Le premier déploiement a publié l'ancienne version.** Quand le contrôle
   échoue, `_predeploy.py` s'arrête **avant** de préparer `_dist/`, et déployer
   juste après republie le précédent **sans aucun message**. Vu en vérifiant en
   ligne (4 diapositives au lieu de 7), redéployé, revérifié.
2. ⛔ **La suite échouait une fois sur deux**, sur « Page.goto: Timeout ».
   Le coupable n'était pas le site : le serveur de test était
   **`TCPServer`, mono-tâche**. Le navigateur garde ses connexions ouvertes,
   l'une bloquait les autres, et la page (28 images désormais) ne se chargeait
   plus à temps. ⚠️ J'ai d'abord accusé Google Fonts et corrigé à côté.
   Passé en `ThreadingTCPServer` : **quatre passages verts d'affilée**.

L'en-tête du fichier annonçait encore « 53 contrôles » : il en annonce 121.
