# ZONE TRAVAUX · ce qui est à fabriquer, en vagues

> ⚙️ Page CONSTRUITE par `python scripts/travaux.py` à partir de `_memoire/travaux.json` : ne pas l'éditer à la main.
> Mongazi ajoute des travaux avec **`/vague <client> : <travail> ; …`** et change leur place avec
> **`/rang <travail> <position>`** (exemple : `/rang djibom 2`).

Créée le 2026-11-25 à la demande de Mongazi : « crée cette zone, et elle doit fonctionner en vagues ». On y met **ce
qu'on fabrique pour un client** : aperçu, catalogue, vitrine, étiquette, affiche, vidéo. Ce qui attend une décision
va dans `EN-INSTANCE.md`, les messages à envoyer dans NEBULA Suivi. Le détail privé d'un aperçu (numéros compris) est
dans `nebula-apercus/PLAN-APERCUS-25-11.md`.

## Les règles des vagues
1. **Une vague à la fois.** On lance ensemble ses travaux, puis on les finit, on les vérifie (QC, Polaris ou un
   regard sur les captures) et on les livre **avant** d'ouvrir la vague suivante.
2. **3 travaux au plus par vague** : les rangs 1 à 3 forment la vague 1, les rangs 4 à 6 la vague 2, et ainsi de
   suite. On reste à 3 parce que le PC a 8 Go et qu'on fait 3 aperçus par jour.
3. **Ordre d'arrivée** : un nouveau travail va au bout de la file. **Mongazi change l'ordre avec `/rang`.**
4. **Une promesse en retard passe en tête.**
5. **⛔ Rien n'est bloqué** (Mongazi, 25/11 : « ne bloque rien »). S'il manque des photos, une décision ou une mesure,
   on avance avec ce qu'on a : produits d'exemple marqués comme tels, « photo à venir », une taille standard
   proposée. On livre, et on complète dès que l'information arrive.
6. **Un travail livré** descend dans « Livrés », avec son lien et sa date.


## 🔨 Vague 1 · EN COURS

| Rang | Travail | Client | Ce qu'il faut | Échéance |
|---|---|---|---|---|
| 1 | Aperçu 3D, meubles en « prix sur demande » | Nouva Meubles | 5 meubles pris sur ses pages (ou 5 captures de son catalogue WhatsApp par Mongazi) | ⚠️ en retard (promis « sous 24 h » le 24/11) |
| 2 | Aperçu 3D, un seul catalogue pour ses 3 pubs (montres connectées, tablettes, ventilateurs solaires) | Dayday's Fancy Accessories | ses produits, que Mongazi me transfère (sinon : ses pages Facebook) | ven. 27/11 après-midi |
| 3 | Aperçu 3D, prêt-à-porter, baskets, montres | ABD SHOP CHIC | 5 modèles pris sur sa page Facebook | ven. 27/11 après-midi |

## 🔜 Vague 2

| Rang | Travail | Client | Ce qu'il faut | Échéance |
|---|---|---|---|---|
| 4 | Aperçu 3D, PC | Yaz computer | 5 PC pris sur sa page Facebook | ven. 27/11 fin de journée |
| 5 | Aperçu 3D, ensembles montre | BIMF Store | ses photos si elles arrivent ; sinon ensembles d'EXEMPLE marqués comme tels, remplacés ensuite | sous 48 h après son oui |
| 6 | Étiquettes de jus en format RECTANGULAIRE | Au Braisé d'Or (Maman Djibom) | format RECTANGLE (pas carré). Ses dimensions si elle les donne, sinon 9 × 6 cm à l'horizontale, ajustable. Partir de `clients/09-au-braise-dor/_outils/_etiquettes_carre.py`, sans « Préparé le … Au frais » |  |

## 🔜 Vague 3

| Rang | Travail | Client | Ce qu'il faut | Échéance |
|---|---|---|---|---|
| 7 | Remplacer les pièces d'exemple de la vitrine par ses vraies pièces | Max · OVRSZ | ses pièces sur cintre, noms, prix, tailles ; en attendant, améliorer ce qu'on peut |  |

## ✅ Livrés
| Date | Client | Travail | Lien |
|---|---|---|---|
| 25/11 | Max · OVRSZ | Vitrine 3D offerte (pièces d'exemple) | https://ovrsz.pages.dev |
| 25/11 | Semelle Dafrik | Aperçu 3D | https://semelle-dafrik.pages.dev |
| 24/11 | Highgameshop | Aperçu 3D (produits d'exemple) | https://highgameshop.pages.dev |
| 24/11 | ARIO Cadeaux | Démo 3D | https://ario-cadeaux.pages.dev |
| 24/11 | Quesiah (Benin Beni) | Aperçu 3D | https://quesiah.pages.dev |
| 24/11 | Au Braisé d'Or | Étiquettes de jus carrées 6,5 × 6,5 cm et ovales | `clients/09-au-braise-dor/imprimer/` |
