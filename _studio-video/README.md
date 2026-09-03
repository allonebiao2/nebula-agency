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
src/Root.tsx      les trois compositions, 1080x1920
public/           les plans filmés et la musique (hors dépôt)
```

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
