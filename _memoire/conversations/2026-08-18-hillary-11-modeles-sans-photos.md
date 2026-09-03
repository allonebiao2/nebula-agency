# 2026-08-18 · Hillary — les 11 modèles posés sans leurs photos

## Ce qui s'est passé

Hillary a envoyé **onze modèles** entre le 16 et le 18 août : prix, prix
express, délais, type de mesures, tout est donné. **Aucune photo n'est jamais
arrivée sur le disque** : elles ont été montrées dans la conversation, depuis le
téléphone de Mongazi.

Mongazi a demandé quatre fois de suite de les mettre en ligne. À la quatrième :
« mets-les déjà sur la vitrine ». C'est sa maison, sa décision, exécutée.

## Ce qui est en ligne

**Le catalogue passe de 9 à 20 cartes.** Les onze nouvelles portent tout sauf
l'image : nom, description, **prix dans les trois monnaies qu'elle donne**,
délai, type de mesures. La commande fonctionne de bout en bout (mesures, délai,
panier, message WhatsApp avec le bon total).

⚠️ **Le libellé est `Photo sur WhatsApp`, pas « photo à venir ».** La différence
n'est pas cosmétique : « à venir » dit à la cliente que la maison n'est pas
prête, « sur WhatsApp » est **vrai, actionnable**, et l'envoie là où elle
commande de toute façon. Drapeau `photoWa:true` dans `PIECES`.

⚠️ **Ni héros ni carrousel** : ces deux surfaces vivent de la photo, un
monogramme en pleine page ne montre rien. Héros à 7 pièces, carrousel à 8.

## Vérifié sur téléphone, en ligne

| | iPhone 13 (WebKit réel) | Android Pixel 5 | 360 px |
|---|---|---|---|
| Cartes | 20 | 20 | 20 |
| Sans photo affichées | 12/12 | 12/12 | 12/12 |
| Débordement | 0 px | 0 px | 0 px |
| Au toucher | fiche ouverte, 11 mesures | idem | idem |
| Erreurs JS / réseau | 0 / 0 | 0 / 0 | 0 / 0 |

(les 12 = les 11 nouvelles + « Création libre », qui n'a jamais eu de photo)

## ⛔ POURQUOI LES PHOTOS N'ARRIVENT PAS, ET CE QUE ÇA APPREND

Mongazi : « mais c'est ici que je t'envoyais les images de base et tu arrivais à
les mettre ». **Il avait raison, et la vérification l'a montré :**

- les quatre photos du 6 août (`IMG_1604`…`IMG_1614.png`) sont **sur le disque**,
  et **git ne les suit pas** (`clients/*/_sources/` est ignoré) : elles ont donc
  été **déposées directement sur ce PC** ;
- le lot du 10 août a livré **les huit images finies et aucune source**. Or
  `_detourer.py` ne sait lire que des fichiers : cette session-là **avait donc
  les fichiers**, ailleurs qu'ici.

**L'explication qui colle : une session lancée depuis le téléphone tourne dans
le nuage, et là les pièces jointes arrivent comme de vrais fichiers.** Une
session qui tourne sur le PC voit l'image dans la conversation sans pouvoir
l'écrire nulle part.

C'est la même leçon que MON BÉNIN, et elle a coûté une journée : **une image
regardée dans une conversation n'est pas un fichier**, et ce qui change tout,
c'est **où tourne la session**.

## L'outil qui attend

`_nouveaux_modeles.py` porte les onze modèles (prix, délais, express, mesures,
noms, indices de reconnaissance). Sans argument il dit ce qui manque et crée les
dossiers de dépôt ; avec `--poser` il détoure, pose en WebP, relève la teinte du
tissu et injecte. **Il refuse de travailler tant qu'une seule photo manque.**

## Restent en suspens

1. Les fichiers photo des onze modèles.
2. Les **11 mesures de la robe ovale**, toujours pas validées.
3. Deux pièces à faire préciser : la **Robe Émeraude** (robe d'une pièce ou
   deux-pièces ?) et l'**Ensemble Orange** (jupe ou pantalon ?).
4. La **Robe Sirène** : la vue de face porte un cœur collé, il faut l'originale.
5. La question que la **Robe d'été** tranche peut-être toute seule : le même
   modèle y est montré dans deux tissus, donc le tissu est probablement au choix.
