# 2026-09-04 — HILLARY M. STYL : ce qu'elle doit savoir avant de couper

**Demande de Mongazi**, transmettant la liste d'Hillary, mot pour mot :

> Les informations dont j'ai besoin… Lieu de résidence · Nom · Prénom · Numéro de
> téléphone · Lieu d'expédition ou de livraison… Ou la cliente passera à l'atelier
> récupérer. De toute façon quand la tenue de la cliente sera prête on lui enverra
> un message ou on l'appellera en direct… De même qu'un message lui sera envoyé
> dès que sa commande est validée.

**Fait, en ligne, vérifié** : https://hillary-m-styl.pages.dev
**192 contrôles verts** (150 avant) · page servie **identique au disque en MD5**
· un fichier absent répond **404**.

---

## L'écart, mesuré avant de toucher au code

Sa liste tenait en cinq lignes. Trois d'entre elles n'étaient pas tenues.

| Ce qu'elle demande | Ce que le site faisait |
|---|---|
| Lieu de résidence | ⛔ **n'existait pas** — seule la ville de *livraison* était demandée, et seulement en expédition |
| Nom | ⚠️ présent mais **facultatif** |
| Prénom | ✅ obligatoire |
| Numéro de téléphone | ⛔ **remplaçable par un email** (`tel ‖ mail`) |
| Lieu d'expédition ou de livraison | ⚠️ pays obligatoire, **ville non**, aucun repère |
| Retrait à l'atelier | ✅ en place |
| Un message à la validation | ⛔ dit nulle part |
| Un message ou un appel quand c'est prêt | ⛔ dit nulle part |

⛔ **Une commande pouvait arriver à l'atelier sans aucun moyen d'appeler la
cliente** — alors que la phrase d'Hillary dit exactement le contraire : « on lui
enverra un message ou on l'appellera en direct ». Et une autre pouvait partir
avec « Côte d'Ivoire » pour toute adresse de livraison.

⚠️ **Une liste de champs n'est pas une liste de champs, c'est une règle métier.**
Chacune de ces cinq lignes décrit un moment de son travail : appeler, livrer,
situer une cliente. Les ajouter sans changer ce qui est *exigé* aurait laissé le
défaut entier.

## Ce qui est en place

**Étape 1 — Comment la recevoir ?**
- la **ville de livraison devient obligatoire** en expédition (le pays seul est
  une zone tarifaire, pas une adresse) ;
- nouveau champ **« Quartier ou point de repère »**, facultatif. ⚠️ **Au Bénin,
  une adresse est un repère, pas une rue.** Facultatif parce que le numéro, lui,
  est obligatoire : l'atelier peut préciser au téléphone, et un champ de plus
  avant le bouton coûte des commandes.

**Étape 2 — Vos coordonnées**
- **quatre obligatoires** : Prénom, Nom, **Numéro de téléphone**, **Lieu de
  résidence**. L'email devient *facultatif* ;
- ⚠️ **le numéro ne peut plus être remplacé par un email.** Ça n'exclut
  personne : qui n'a pas WhatsApp a un téléphone, et c'est celui-là qu'on
  appellera. L'email reste offert **en plus**, jamais **à la place** ;
- ⚠️ **le lieu de résidence n'est pas le lieu de livraison**, et elle demande les
  deux. Ils se confondent souvent, pas toujours (une cliente de Cotonou fait
  livrer sa sœur à Abidjan) : on ne le **suppose** pas, une puce **« J'habite à
  Abidjan »** propose de le recopier en un geste ;
- **les deux messages promis** sont écrits au-dessus du récapitulatif. C'est ce
  qui **justifie** le champ obligatoire, au lieu de le faire deviner.

**Étape 3 — Envoi** : la même promesse, redite là où la cliente quitte le site.

**FAQ** : une septième question, « Comment saurai-je où en est ma commande ? ».

**Le message WhatsApp** porte les cinq informations, **chacune sous son nom** —
plus de `Prénom Nom` collés : Hillary les recopie dans son carnet, et un nom
composé rend le collage indéchiffrable.

```
*LIVRAISON*
Expédition — Côte d'Ivoire, Abidjan
Repère : Cocody, en face du lycée français
Frais : 12 000 F

*CLIENT*
Nom : SOGLO
Prénom : Ama
Téléphone : +229 01 97 00 00 00
Lieu de résidence : Abidjan, Riviera 2
```

## ⛔ Le défaut vu sur une capture, pas dans le code

À l'étape 1, choisir un pays sans remplir la ville laissait **« CONTINUER » gris
et muet**. L'étoile rouge est sur l'étiquette, mais rien ne reliait le bouton
mort au champ qui manque.

C'est exactement ce que la ligne **« Encore : … »** corrige à l'étape 2 — et elle
n'existait qu'à l'étape 2. **Une règle appliquée à un seul endroit n'est pas une
règle.** Même famille que « une correction faite à un endroit n'est pas faite
partout » (carrousel Hillary, 25/08).

Deux pièges dans le remède lui-même :

⚠️ **« A commencé » n'est pas « a choisi un mode ».** Le premier jet allumait la
ligne dès le clic sur « Expédition », au-dessus de deux champs vides que la
cliente s'apprêtait à remplir : on lui reprochait de ne pas avoir fait ce qu'elle
était en train de faire.

⚠️ **Une ligne cachée qui porte quand même son texte est un piège.** `innerText`
d'un élément en `display:none` renvoie son contenu : le contrôle lisait
« Encore : votre pays… » sur une ligne que **personne ne voit** et accusait le
site. La sonde était fausse. Plutôt que de corriger la seule sonde, texte et
visibilité ont été rendus **solidaires** : la ligne n'écrit que ce qu'elle montre.

## ⛔ Le contraste de la modale n'était mesuré par rien

Ce QC vérifie qu'aucune variable CSS n'est utilisée sans être définie, mais
**aucun contrôle ne lisait une couleur de texte contre son fond dans le tunnel de
commande**. C'est pourtant là que le rose de la marque a déjà été posé sur du
texte **trois fois** (étiquette du carrousel, badge, bouton WhatsApp) — et une
**quatrième** ici : la puce de recopie au survol mesurait **3,91:1**, trouvée à la
main pendant la relecture des captures.

⚠️ **`--rose` ne porte pas de lettres.** Le trait le garde, le texte prend
`--rose-f` (4,93:1). Le contrôle neuf mesure les **pixels rendus** en remontant
jusqu'au premier ancêtre vraiment opaque : puce au repos **et** au survol, les
deux blocs de promesse, l'écran d'envoi. Mesuré : 9,27 · 4,93 · 8,04 · 9,54.

## ⛔ `_predeploy.py` ne lançait pas l'assembleur

Le site se monte en deux temps : `_v4/_assembler.py` recompose
`_vitrine_src.html` depuis les morceaux de `_v4/`, puis `_build.py` en tire
`vitrine.html`. **`_predeploy.py` ne faisait que le second.**

Qui modifiait un morceau de `_v4/` puis lançait ce script déployait un livrable
bâti sur une source **périmée** : tout vert, tout en ligne, et le changement
absent, **sans un mot**. Le défaut était noté dans CLAUDE.md depuis le
2026-08-16 et n'avait jamais été refermé. Il l'est.

⚠️ Bénéfice de bord : l'assembleur **refuse d'écrire** si l'un des 18
identifiants du moteur manque — ce garde-fou entre donc dans le chemin de
déploiement.

## Contrôles : 150 → 192

⚠️ **Un contrôle qui devient faux n'est pas un contrôle qu'on supprime.** Celui
qui disait « email seul (sans WhatsApp) suffit pour valider » protégeait une
vraie décision : ne pas exclure qui n'a pas WhatsApp. Cette décision tient
toujours, mais elle passe désormais par le **téléphone**, qui sert aussi bien à
appeler. Le contrôle a été **retourné**, pas retiré.

⚠️ **La page se souvient, et le contrôle l'ignorait.** `cmd` et `memoire()`
reportent les coordonnées d'une commande sur la suivante — c'est voulu, une
cliente qui repasse commande ne retape pas son numéro. Le contrôle « email seul
ne suffit plus » mesurait donc un numéro **déjà rempli par le parcours
précédent** et concluait l'inverse de la vérité. Il vide maintenant les champs
avant de mesurer, et vérifie au passage que le souvenir fonctionne — ce que
personne ne contrôlait.

⚠️ **On remplit les champs UN PAR UN.** Un contrôle qui remplit les quatre d'un
coup et constate que le bouton s'allume ne prouve pas qu'ils sont tous exigés.

## Nouvel outil : `python _vues_commande.py`

Photographie les **dix écrans** du tunnel en 390 et 1440.

⚠️ **Ni `full_page` ni `.sheet`.** Le premier photographie les 28 000 px du
catalogue qui dort derrière la modale. Le second est pire, parce qu'il a l'air de
marcher : la barre et le pied sont `sticky`, donc ils se repeignent au bord de la
**fenêtre** et cachent tout ce qui suit. Sur les deux premières planches, **les
deux messages promis et le récapitulatif étaient absents de l'image sans que rien
ne le signale** — et c'est précisément ce que j'étais en train de vérifier.
La fenêtre est donc haute (390×2600, 1440×2000) et toute la modale y tient.

## Ce qui reste

Rien de nouveau : les points en attente sont ceux d'avant (les 11 mesures de la
robe ovale à valider par l'atelier, la matière de chaque pièce, le libellé
« Robe de ville », l'adresse pour la fiche Google).

## Fichiers touchés

`_v4/garde-moteur.js` · `_v4/garde-css-modale.css` · `_v4/markup.html` ·
`_v4/_assembler.py` · `_qc.py` · `_predeploy.py` · **nouveau**
`_vues_commande.py` · `_vitrine_src.html` et `vitrine.html` régénérés.
