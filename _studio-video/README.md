# NEBULA · le studio vidéo

Le montage des vidéos de l'agence, écrit en code plutôt qu'à la souris. Une
vidéo est un programme : on change une question, on relance, la vidéo est
refaite à l'identique. Aucun projet CapCut à retrouver, aucun export à refaire à
la main.

Outil : **Remotion 4.0.512** (React + rendu H.264).

---

## Ce qu'il y a dedans aujourd'hui

Les trois séries « oui / non » de
`_documents/nebula-agency/marketing/TIKTOK-OUI-NON.md`, en 1080x1920, 30 images
par seconde :

| Composition | Contenu | Durée |
|---|---|---|
| `oui-non-1-prix` | Script 1 · le prix, 9 questions | 25,5 s |
| `oui-non-2-besoin` | Script 2 · « je n'ai pas besoin de site », 8 questions | 23 s |
| `oui-non-3-logiciel` | Script 3 · le logiciel métier, 8 questions | 23 s |

Et la démonstration d'un produit de la maison :

| Composition | Contenu | Durée |
|---|---|---|
| `minuit-demo` | **MINUIT · la lettre digitale**, six plans | 30 s |
| `minuit-plans/` | Les six plans, chacun réglable seul | |

Le rythme est celui du document : la question tient **1,5 s**, la réponse
**1 s**, la carte finale **3 s**, et la coupe est **sèche** (aucune transition,
c'est le format qui le veut).

Les cartes ne sont pas redessinées ici : ce sont les PNG écrits par
`_documents/nebula-agency/marketing/_cartes.py`, importés tels quels. Une
question change → on regénère la carte avec `python _cartes.py`, jamais à la
main.

## Ce qui manque encore

- **Les plans filmés.** Le visage qui fait oui ou non n'est pas tourné. En
  attendant, la réponse s'affiche en grosses lettres sur fond noir et la vidéo
  se rend quand même. Voir `public/LISEZ-MOI.md` pour la brancher.
- **La musique.** Même dossier, mêmes explications, et l'avertissement qui va
  avec sur les droits.

---

## Les commandes

```bash
cd _studio-video

npm run studio          # l'aperçu dans le navigateur, on scrube à la souris
npm run rendu           # les trois vidéos dans out/
npm run rendu:prix      # une seule
npm run verifier        # contrôle TypeScript, sans rien rendre
```

Le premier rendu télécharge un Chrome sans interface (une centaine de Mo). Les
suivants ne le retéléchargent pas.

`out/` n'est pas versionné : une vidéo se refabrique, elle n'a rien à faire dans
un dépôt public.

## Les fichiers

```
src/scripts.ts    les questions, les réponses, le rythme  ← c'est ici qu'on édite
src/OuiNon.tsx    le montage : question, coupe, réponse
src/Root.tsx      toutes les compositions, 1080x1920
public/           les plans filmés et la musique (hors dépôt)

src/minuit/donnees.ts   MINUIT : couleurs, texte de la lettre, rythme  ← on édite ICI
src/minuit/Minuit.tsx   le montage des six plans
src/minuit/*.tsx        un fichier par plan
```

---

## MINUIT · la démonstration du produit

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure
> dite.** Toutes les animations sortent de cet objet, et d'aucun autre.

Six plans, six signatures, reprises une par une de `minuit/README.md` :

| # | Plan | Signature | Durée |
|---|---|---|---|
| 1 | Le seuil | le cachet **respire, puis se brise** en trois éclats de cire | 5,5 s |
| 2 | La lettre | **le dépliage**, puis **l'encre qui sèche** ligne après ligne | 8,5 s |
| 3 | Le compte | **les chiffres qui roulent**, avec une sortie qui ralentit | 3 s |
| 4 | La signature | **le trait qui s'écrit** (`stroke-dashoffset`) | 3 s |
| 5 | L'heure dite | **l'aiguille qui monte à minuit** | 6 s |
| 6 | La carte | **le cachet qui se referme** : la boucle du plan 1, à l'envers | 4 s |

Le plan 5 est le seul dont la signature n'existe pas dans le produit, et c'est
lui qui vend : l'heure choisie est ce qui donne son nom à MINUIT. Elle sort
quand même du même objet, le cadran reprenant le cercle et le pointillé **du
cachet**.

### Ce qui n'est pas inventé

Rien. Les couleurs sont les jetons de `minuit/lettre.html`, le texte de la
lettre est celui de la démonstration du produit (accentué, il ne l'était pas
dans les captures), le prix est celui de `minuit/creer.html`. Tout est recopié
**une seule fois**, dans `src/minuit/donnees.ts`.

⚠️ **Aucune police téléchargée**, comme dans le produit : la pile est système,
Palatino Linotype sous Windows. La vidéo doit ressembler à la lettre que la
destinataire ouvrira, pas à une version embellie pour la publicité.
⛔ Ne pas rajouter Google Fonts ici.

### ⛔ Avant de publier cette vidéo

Elle promet **« Elle l'ouvre à minuit pile. Pas avant. »** et affiche
`nebula-agency.online/minuit`. Au 2026-09-03, ni l'un ni l'autre n'existe :
la livraison à l'heure choisie (n8n) et le serveur en ligne sont les deux
chantiers ouverts de `minuit/README.md`. La vidéo est prête, **la promesse ne
l'est pas** : elle attend que l'adresse réponde.

### ⛔ Pas de fondu enchaîné, et ce n'est pas un raccourci

Les six plans posent leur contenu sur **le même fond de nuit**, et chacun fait
entrer et sortir ce contenu lui-même. Une coupe entre deux plans est donc
invisible : ce qui change, c'est ce qui est posé dessus, pas le fond.

Un fondu enchaîné, lui, superpose les deux plans. Essayé, puis **regardé** sur
l'image 372 : la feuille de la lettre à 50 % et la carte du compte à 50 %
donnaient deux rectangles clairs décalés l'un sur l'autre, le « 332 » roulant
par-dessus le texte de la lettre. Ça ne ressemble pas à une transition, ça
ressemble à une panne. `@remotion/transitions` a été désinstallé.

### ⚠️ Ce que CSS ne sait pas faire ici

`lettre.html` anime son cachet en `@keyframes`. **Une animation CSS ne se rend
pas** : elle joue à l'horloge du navigateur, et le rendu la photographierait
figée ou au hasard. Tout est donc réécrit en `useCurrentFrame()` et
`interpolate()`. Même chose pour un `transition:` : il n'existe pas ici.

⚠️ **`rotate: 12` en nombre nu sort en `rotate:12px`, donc invalide et ignoré
sans un mot** (React n'a `scale` dans sa table des valeurs sans unité, pas
`rotate`). Toute rotation s'écrit `` `${...}deg` ``.

---

## ⚠️ La licence Remotion, vérifiée le 2026-08-14

Lue dans `node_modules/remotion/LICENSE.md`, la licence de la version installée,
et dans la FAQ officielle. Ce n'est pas du logiciel libre au sens habituel.

**NEBULA est éligible à la licence gratuite**, à trois conditions qui sont
remplies aujourd'hui :

1. **Trois personnes au plus.** Le texte : *« a for-profit organization with up
   to 3 employees »*. Les partenaires commerciaux ne sont pas des salariés, mais
   le jour où l'agence emploie quatre personnes, la licence entreprise devient
   obligatoire.
2. **L'usage commercial est autorisé**, y compris les vidéos vendues à un
   client : *« Any commercial use case is allowed as long as you are not selling
   Remotion as a product itself »*. La FAQ le dit pour les agences : *« If your
   agency has 3 or fewer personnel, the Free License covers this work. »*
3. **On livre des fichiers vidéo, pas le projet Remotion.** Si le client devient
   propriétaire du projet, la FAQ additionne les effectifs des deux sociétés et
   c'est **au client** de payer la licence. Un client de plus de trois salariés
   ferait donc basculer l'affaire : on lui remet le MP4, pas le code.

Ce qui reste interdit dans tous les cas : revendre, relouer ou sous-licencier
une version dérivée de Remotion. Vendre une vidéo faite avec Remotion, oui ;
vendre Remotion habillé en produit NEBULA, non.

**La version est figée à 4.0.512, et ce n'est pas un détail.** La licence
**change en 5.0** (télémétrie obligatoire avec clé de licence pour le modèle
« Automators »). Ne pas faire `npm update` sans relire la licence de la version
visée : c'est exactement pour ça que l'installation a été faite avec
`--save-exact`.
