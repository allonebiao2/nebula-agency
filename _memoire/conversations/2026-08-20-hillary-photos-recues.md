# HILLARY M. STYL — neuf modèles reçoivent leurs vraies photos

**Date :** 2026-08-20 · **Branche :** `claude/hillary-style-auto-switch-9ij9wz`
**Site :** https://hillary-m-styl.pages.dev — ⚠️ **rien n'est encore déployé.**

Mongazi a envoyé les photos, par lots, depuis le téléphone. Elles sont arrivées
comme de vrais fichiers dans la session du nuage — ce que la note du 2026-08-18
avait prévu.

---

## Ce qui est posé : 9 des 11 fiches

| pièce | vues | prix | mesures |
|---|---|---|---|
| Robe de ville organza | face + **dos** | 40 000 | robe ovale |
| Ensemble Nœud | face + **dos** | 25 000 | haut + pantalon |
| Robe Lacée | face + **dos** | 35 000 | robe ovale |
| Tailleur Cœurs | face | 50 000 | haut + pantalon |
| Ensemble Jean | face + **dos** | 35 000 | haut + jupe |
| Robe Sirène | face (profil) | 40 000 | robe droite |
| Robe Émeraude | face | 25 000 | haut + jupe |
| Ensemble Orange | face | 35 000 | haut + pantalon |
| Robe Soleil | face | 25 000 | robe ovale |

⏳ **Il reste 2 pièces** : Robe d'été et Ensemble Volants. Elles gardent
« Photo sur WhatsApp », qui reste vrai et actionnable.

**Quatre pièces basculent face/dos toutes seules**, au catalogue et au
carrousel — le mécanisme du 2026-08-18 sert enfin à quelque chose.

## Rien n'a été déduit

Les **9 prix et les 9 types de mesures** que Mongazi a écrits correspondent
**au centime et au mot** à ce qu'Hillary avait donné le 2026-08-16. Vérifié
ligne à ligne avant de poser quoi que ce soit. Une fiche qui part sur WhatsApp
avec un prix engage la maison.

## Deux photos écartées, et pourquoi

- ⛔ la vue de face de la **Robe Sirène** porte un **emoji ❤️ collé sur la
  poitrine**. Ce n'est pas une photo de produit. On garde le profil, propre.
- ⛔ l'ancienne capture d'écran de la **Robe d'été** reste écartée.

---

## ⛔ LE DÉTOURAGE EFFAÇAIT L'ORGANZA

`isnet-general-use` rendait le train blanc de la robe à jupon **en gris sale**
sur la face, et l'**effaçait entièrement** sur le dos : il ne restait qu'un
disque rouge flottant, sans jambes ni jupon. Les tissus translucides (organza,
tulle, mousseline) sont exactement ce que ce modèle ne sait pas voir.

**`birefnet-general` les garde intacts.** Plus lent (~45 s par photo contre
~10 s), 890 Mo de modèle. C'est le prix d'une pièce qui ressemble à ce
qu'Hillary a cousu.

⚠️ **Un processus par photo.** birefnet enchaînait la première image sans
broncher puis se faisait **tuer sur la deuxième** (code 137), sur une machine
où 15 Go étaient libres. Ce n'est pas la machine : onnxruntime ne rend pas ce
qu'il a pris entre deux inférences.

## ⛔ LA COULEUR DU HÉROS SUIVAIT LA PEAU, PAS LE TISSU

La robe verte et jaune ressortait en **brun `#9e6033`**. Ce n'était pas un bug
de calcul : bras et jambes nus couvraient **23 %** de la photo contre **17 %**
pour le tissu, et la peau gagnait. Le héros aurait peint son fond couleur peau
sous une robe verte.

**Correctif** : parmi les teintes qui occupent au moins 15 % de la pièce,
prendre **la plus saturée**. Un vêtement est presque toujours plus vif qu'une
peau. La verte redevient verte (`#136b16`), l'ensemble en jean gagne son vrai
rouge, les six autres ne bougent pas ou à peine.

⚠️ **Ce qui ne marche pas** : un détecteur de peau par bande de teinte. La peau
occupe 10-40°, exactement là où vivent les tissus orange et terracotta — et
Hillary en a un.

## ⚠️ UN FAUX DÉFAUT QUE J'AI SIGNALÉ À TORT

La règle qui évite deux nappes voisines identiques au héros comparait des
**angles de teinte**, seuil 28°. Elle accusait `hero-3 → hero-4` (19° d'écart)
et je l'ai rapporté à Mongazi comme un défaut à corriger.

**C'était faux.** Leur distance perçue est de **33 ΔE** : un bleu profond et un
cyan clair, que personne ne confondrait. L'angle de teinte ignore la clarté et
la saturation, c'est-à-dire l'essentiel.

**La règle mesure désormais en L\*a\*b\***, seuil **ΔE 18**. Résultat : le héros
porte **16 diapositives** et **aucune transition invisible**. Les deux plus
serrées sont à ΔE 19,9 et 21,7 — visibles.

⚠️ Le calcul exhaustif montre qu'avec la mesure d'angle, **aucun ordre parfait
n'existait** : la collection compte 6 pièces chaudes contre 3 séparateurs. La
mauvaise mesure fabriquait un problème insoluble qui n'existait pas.

## ⛔ TROIS BOURDES DE DÉCOUPE, ET LES GARDE-FOUS

L'outil réécrit `motion.js` et `garde-moteur.js` par découpe de texte.

1. une **virgule posée après un commentaire** (« `*/,` ») — le bloc `hero-4`
   traîne dix lignes de commentaire derrière lui ;
2. **tout l'en-tête du fichier effacé** : la bannière, `(function () {`, le
   `'use strict'`. Le fichier ne se fermait plus, **le site entier devenait
   muet** ;
3. une restructuration avait **effacé sept fonctions** au passage. Le script a
   détouré **douze photos pendant dix minutes** avant de mourir sur un
   `NameError`, à la seconde où il allait écrire.

**Deux garde-fous** : la sortie passe par **`node --check` avant** d'être
écrite, et `main()` **vérifie ses fonctions avant** de lancer quoi que ce soit
de coûteux. Le coût d'une bourde ne doit pas dépendre de l'endroit où elle
explose.

---

## Contrôles

**138 verts.** Captures regardées en 390 et 1440, plus une planche des douze
découpes sur fond sombre — un détourage raté ne se voit jamais sur du blanc.

## ⏳ CE QUI ATTEND MONGAZI

1. **2 photos manquantes** : Robe d'été, Ensemble Volants.
2. **Le sac beige** tenu devant l'Ensemble Orange : on le laisse ou on le
   retire ? Une cliente peut le croire compris.
3. **Le dos de l'organza** a une teinte **crème** sur les bords : le fond jaune
   du studio vu à travers un tissu transparent. C'est ce que montre la photo.
   Neutraliser ou garder ?
4. ⚠️ **Ses photos originales ne sont pas sauvegardées.** `clients/*/_sources/`
   est ignoré par git (ligne 76), et le dépôt est **public**. Les détourées sont
   commitées, le site ne perd rien — mais refaire un détourage plus tard
   demandera de les redemander.
5. **Le nommage.** Mongazi écrit « Robe de ville » en tête de chaque fiche, y
   compris pour un **tailleur veste + pantalon** dont il précise « mesures d'un
   haut et un pantalon ». Lu comme son modèle de message, pas comme le nom de
   chaque pièce. Les noms qui distinguent ont été gardés.
6. ⚠️ **Défaut antérieur** : le héros affiche l'étiquette **« PRÊT-À-PORTER »**
   alors que les 20 pièces sont toutes en sur-mesure, et l'onglet correspondant
   est masqué parce qu'il est vide.
