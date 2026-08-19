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

## État
✅ Construit (`npm run build`, 181 kB) · ✅ **30 contrôles verts**
⛔ **NON DÉPLOYÉ** — Cloudflare Pages attend l'accord de Mongazi.
