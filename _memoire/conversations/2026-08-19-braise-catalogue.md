# 2026-08-19 — Au Braisé d'Or : le catalogue relu contre le menu papier

> Mongazi : « Je veux qu'on travaille sur le catalogue de Au Braisé d'Or ce soir. »

## Ce qui a été fait

**On est remonté à la source.** Le catalogue avait été construit depuis
`MENU.md`, qui est lui-même le résumé des 5 photos du menu papier du 17 juillet.
Les photos sont dans `_partage/` : elles ont été recadrées et agrandies, page
par page, colonne par colonne. C'est ce détour qui a tout produit.

### 1. Quatre plats manquaient — 48 → 52
Le petit-déjeuner du papier a **10 lignes**, le site en montrait **6**.
Manquaient **café chaud serré (500 F)**, **Lipton citron (500 F)**, **œuf sur
plat (1 000 F)** et **café au lait écrémé (1 000 F)**.

⚠️ Personne ne l'aurait vu depuis le site : une carte à laquelle il manque une
ligne a exactement l'air d'une carte complète. Il faut la comparer à autre chose.

### 2. Le prix était illisible sur les 52 cartes
La pastille de prix n'avait **aucune couleur de texte déclarée**. Elle héritait
donc de `--encre` (`#1d1a17`), sur un fond `rgba(0,0,0,.65)`.
**Contraste mesuré : 1,1:1** là où il en faut 4,5.

C'est la faute la plus chère de la soirée, et la plus discrète : sur les photos
de plats sombres, la pastille se lisait « un peu », assez pour qu'un coup d'œil
ne s'alarme pas. Corrigé en `#f6efe6` sur pastille à 70 % → **13,9:1 à 18:1**.

### 3. L'ardoise, pour un plat sans photo
⛔ Ni cadre vide (« le site est en travaux »), ni « photo à venir » (« la maison
n'est pas prête »). **Un restaurant écrit à l'ardoise ce qu'il n'a pas
photographié**, et personne n'y voit un manque. Tuile sombre, nom du plat dans
la police de titre, filet de braise. C'est aussi le mécanisme prêt pour le jour
où les 48 images générées sortiront.

### 4. Un QC, enfin — `python clients/09-au-braise-dor/_outils/_qc.py`
**30 contrôles.** Le client 09 n'en avait aucun.

## ⚠️ LA LEÇON D'INSTRUMENT, payée trois fois ce soir

**Un contrôle faux coûte plus cher qu'un contrôle absent, parce qu'on le croit.**

1. `document.querySelector('[role=dialog]')` mesurait **le tiroir des univers**,
   monté en permanence et premier dans le DOM, au lieu de la fiche de commande.
   Deux contrôles rouges qui accusaient un site sain.
2. Recadrer une capture d'écran à partir de boîtes lues **avant** la capture :
   entre les deux, les images différées arrivent et la mise en page glisse.
3. **Le plus instructif** : « prendre le décile le plus clair pour le texte »
   (leçon Angy Art) ne marche que si le texte couvre une bonne part de la boîte.
   Les chiffres d'une pastille en couvrent **un dixième** : le décile tombe
   alors en plein anticrénelage. La mesure annonçait **2,15:1 sur une pastille
   parfaitement nette**, vérifiée à l'œil sur une capture agrandie.
   → **La couleur du texte est DÉCLARÉE, donc connue et solide ; seul le fond
   dépend de la photo posée dessous. On déclare l'une, on mesure l'autre.**
   Et on neutralise l'animation d'apparition avant de photographier, sinon on
   mesure le contraste d'un fondu.

C'est en regardant une capture agrandie d'une seule pastille que le doute s'est
levé. **Quand l'instrument et l'œil se contredisent, on regarde.**

## Ce que la photo tranche, et ce qu'elle ne tranche pas

La colonne des 2ᵉˢ tailles est coupée au bord de la photo, mais le premier
chiffre se lit en recadrant :

| | |
|---|---|
| **confirmés** | à la crème 6 000 · pili chaud 5 000 · paysanne 6 000 · **pêcheur 6 000** |
| **manquants au site** | ⏳ **napolitaine** et **oriental** ont une grande taille (prix en 5 …) |
| **pas de 2ᵉ taille** | épinards, quatre saisons, fruit de mer, margherita — le site a raison |
| **illisible** | ⏳ **aileron** : ligne corrigée **à la main au surligneur** sur le papier |

⚠️ Le `MENU.md` donnait « pêcheur 4 000 / (à confirmer) » et le site affichait
6 000 : **j'ai d'abord cru à un prix inventé et j'ai failli le retirer.** La
photo dit que le 6 est bien là. **On ne corrige pas une donnée contre un résumé,
on remonte à la source.**

## ⛔ Ce qui n'a PAS été touché, et pourquoi

**Les 48 photos de plats sont générées par IA** (z_image, 2026-07-20, avant la
règle). Le cerveau dit depuis le 2026-08-01 : « INTERDIT ABSOLU : une photo
produit générée par IA présentée comme le catalogue du client. » Angy Art purgée
le 08-08, Hillary affiche « Photo sur WhatsApp ». **Au Braisé d'Or est le
dernier site où la règle n'est pas appliquée.**

C'est une décision de Mongazi, pas une correction technique : elle a été posée,
pas prise. L'ardoise rend la bascule immédiate le jour où il tranche.

## Fichiers touchés
- `clients/09-au-braise-dor/index.html` — 4 lignes de petit-déj
- `clients/09-au-braise-dor/experience/data/carte.ts` — régénéré (52 plats)
- `clients/09-au-braise-dor/experience/components/Carte.tsx` — ardoise + pastille
- `clients/09-au-braise-dor/experience/components/Categories.tsx` — vignette du tiroir
- `clients/09-au-braise-dor/_outils/_extraire_carte.js` — `img` facultatif
- `clients/09-au-braise-dor/_outils/_qc.py` — **nouveau**, 30 contrôles
- `clients/09-au-braise-dor/MENU.md` · `CONTEXT.md` · `.gitignore`

---

# 2ᵉ temps du 2026-08-19 — la propriétaire corrige la carte

Mongazi envoie **deux photos d'une note manuscrite** : « Correction pour Au
Braisé d'Or ». Les prix en place sont validés (« la propriétaire n'est pas
contre »), mais elle veut des retraits et une catégorie de plus.

## 13 plats retirés, une catégorie ajoutée — **52 → 42**

| Catégorie | Retiré | Reste |
|---|---|---|
| Pizza | napolitaine · oriental · margherita · pili chaud · à la crème · **pêcheur** | 4 sur 10 |
| Grillades | lapin ou mouton frit · viande de caille | 4 sur 6 |
| Chawarma | rien (elle l'écrit) | 3 |
| Hamburger | crispy poulet · nugget pomme au four | 7 sur 9 |
| Cocktails | « tout sauf les jus de fruit » → mojito, piña colada, JOQ Viagra | 3 sur 6 |

**Ajouté : Desserts** — yaourt, glace, cocktail, **sans aucun prix**.

## ⚠️ LA LEÇON DU SOIR : retirer un plat ne suffit pas

Un retrait n'est pas une suppression de ligne, c'est une modification de tout
ce que la page raconte. Trois choses cassaient en silence :

1. **La pizza pêcheur était un des 4 plats signature du héros.** Le visiteur
   serait arrivé sur un plein écran vantant un plat introuvable dans la carte,
   trois écrans plus bas. → remplacée par la paysanne, seule pizza restante à
   deux tailles, donc au même rôle.
2. **Deux notes de catégorie devenaient des mensonges** : les hamburgers
   annonçaient « sauf végétarien, crispy, nugget » sans plus de crispy ni de
   nugget, et les cocktails « avec ou sans alcool » sans plus une goutte
   d'alcool. Aucun outil ne l'aurait signalé : ce sont des phrases, pas des
   données.
3. Les trois cocktails restants répétaient « Sans alcool. » que la note de
   catégorie dit maintenant une fois pour toutes.

**À appliquer** : après un retrait, chercher le nom du plat partout — héros,
carrousel, notes de catégorie, pied de page, affiche — puis relire ce que les
textes voisins affirment encore. Le QC compte désormais **un contrôle par plat
retiré**, sur le texte rendu de la page.

## Les prix qu'on n'a pas

Elle n'a donné **aucun prix pour les trois desserts**. Convention posée :
**`p:0` = prix pas encore donné**. La carte affiche **« Prix sur demande »**,
la fiche remplace le panier par **« Demander le prix sur WhatsApp »** avec la
question déjà rédigée.

⚠️ **Un article à 0 ne doit jamais entrer au panier** : le total mentirait et
le message partirait avec un « 0 F ». Un contrôle vérifie qu'aucun « 0 F »
n'apparaît nulle part sur la page. C'est le même principe que Weinkeller
(« Prix sur demande » sur 6 bouteilles) et qu'Hillary (« Photo sur WhatsApp ») :
**quand une information manque, on donne au client le chemin pour l'obtenir,
on ne bricole pas une valeur.**

## Deux de mes questions sont mortes d'elles-mêmes

Les 2ᵉˢ tailles de la napolitaine et de l'oriental, et le prix de la pêcheur
que j'avais failli retirer : **les trois pizzas sont retirées de la carte**.
Une heure de lecture de photos pour des plats qui n'existent plus.
⚠️ Ce n'est pas du temps perdu — la même lecture a trouvé les 4 lignes de
petit-déjeuner manquantes, qui, elles, restent. Mais **la leçon est de demander
au client AVANT de déduire** : la source vaut mieux qu'un résumé, et le client
vaut mieux que la source.

## Les cinq questions ouvertes
1. **Prix du yaourt, de la glace et du cocktail.**
2. **« Cocktail » en dessert = le cocktail de fruits à 2 500 F, ou autre chose ?**
   Le mot est dans deux onglets à deux prix.
3. **« Lapin » : le mouton frit part aussi ?** La ligne est « lapin **ou
   mouton** frit », elle n'a écrit que « lapin ». Toute la ligne est partie.
4. **Aileron** : le prix corrigé au surligneur.
5. **Le n° WhatsApp.**

## État
✅ Construit (`npm run build`) · ✅ **64 contrôles verts**
⛔ **NON DÉPLOYÉ** — Cloudflare Pages attend l'accord de Mongazi.
