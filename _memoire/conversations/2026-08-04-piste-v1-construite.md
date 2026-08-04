# PISTE — la V1 est construite et marche de bout en bout

## Date : 2026-08-04
## Sujet principal : `piste/` passe d'une fiche produit à un produit qui tourne

---

## Où on en était en ouvrant

La session précédente avait posé **la fiche produit (46 décisions)**, la
**direction artistique** (`index.css`), les **vraies données du 3 août**
(`donnees.js`), le **barème** (`prix.js`) et quatre briques d'interface.

Il manquait le produit : `index.html` appelait `src/main.jsx`, **qui n'existait
pas**. Et `donnees.js` ne se compilait même plus — un bloc de commentaire fermé
deux fois, trois lignes de texte à nu au milieu du fichier.

## Ce qu'on a fait

**Le produit, en entier.** Les six points du périmètre V1, plus deux que la
vente rendait obligatoires :

| | |
|---|---|
| `src/main.jsx` · `App.jsx` | le point d'entrée, le routage par ancre, l'entête et le pied |
| `composants/Vitrine.jsx` | 10 sections, **un geste différent par section**, tous tirés de la phrase du métier |
| `composants/Questionnaire.jsx` | les 6 questions + les coordonnées, le prix détaillé toujours à l'écran, le stock réel qui plafonne le curseur |
| `composants/Paiement.jsx` | le code, le montant, le compte à rebours des 24 h, le message WhatsApp déjà écrit |
| `composants/Cockpit.jsx` | coller le message reçu, marquer payé, marquer livré, sortir le CSV |
| `composants/Origine.jsx` | d'où vient la donnée (décision 43) et le retrait des commerces |
| `src/etat.js` | le code de commande, la composition **et la relecture** du message, le rangement, les routes |
| `_qc.js` | **95 contrôles** : le calcul, l'aller-retour du message, l'écran en 390/768/1440, le parcours joué en entier |
| `_predeploy.js` | le garde-barrière : il s'arrête au premier problème |
| `README.md` | la marche à suivre, les pièges, ce qui reste |

**La décision qui compte le plus, et elle est technique.** En V1 il n'y a pas de
serveur. La commande voyage donc par **WhatsApp**, et le message est le format
d'échange : écrit pour un humain d'abord, mais relisible par le cockpit parce
que c'est PISTE qui l'a composé. `composerMessage()` et `lireMessage()` vont
ensemble, et un contrôle vérifie l'aller-retour. Sans lui, Mongazi ressaisit
ses commandes à la main.

## Ce que j'ai appris

1. **En SVG, un `transform` CSS n'ajoute rien à l'attribut `transform` : il
   l'efface.** Les cinq repères du héros retombaient tous sur le coin du
   viewBox, donc hors cadre, donc invisibles. **Le geste signature du héros ne
   s'est jamais affiché, et 92 contrôles verts n'y ont rien vu.** Il a fallu
   regarder l'image. Correctif : deux groupes, l'extérieur pose, l'intérieur
   anime.
2. **Un hook posé après un retour anticipé** (le `useMemo` du cockpit, après le
   loquet) change le nombre de hooks entre deux rendus : React #310, et toute
   l'application disparaît. Le contrôle ne le voyait qu'à travers un délai
   d'attente épuisé 30 secondes plus tard, sans dire pourquoi.
3. **Une carte animée en 3D pousse la page de côté.** `rotateY(-72deg)` sous
   perspective donne une boîte de ~5 000 px de large tant que la porte est
   fermée : la page glissait latéralement avant même qu'on arrive à la section.
   Elle vit maintenant dans un cadre `overflow-hidden`, ce qui est d'ailleurs
   plus juste — une porte s'ouvre dans son encadrement.
4. **Une animation signature doit se jouer à l'ARRIVÉE, pas au chargement.** La
   porte était une `animation` : elle se jouait tout en bas de l'écran, et
   celui qui descendait la trouvait déjà ouverte. Le geste était dépensé sans
   que personne le voie.
5. **Un code de commande ne se dérive pas de l'heure.** Première version : deux
   caractères d'horloge + deux au hasard, soit 1 024 possibilités par seconde.
   Le contrôle a sorti *400 codes tirés, 342 distincts*. Un doublon, c'est une
   commande qui en écrase une autre dans le cockpit, donc un client jamais
   livré. Six caractères tirés au hasard, **et** une fusion qui exige le code
   ET l'email.
6. **Un contrôle statistique doit être calibré sur le volume réel**, sinon il
   clignote. Deux contrôles ont été refaits parce qu'ils étaient plus serrés
   que le hasard ne le permet.

## Décisions prises

- **Aucun numéro Mobile Money n'est affiché tant qu'il n'est pas confirmé.** La
  page dit la vérité, qui est aussi la solution : *« le numéro vous est donné
  sur WhatsApp, à l'instant où votre commande arrive »*. Le parcours marche
  entier, et `_predeploy.js` refuse la mise en ligne. Un numéro de paiement faux
  n'est pas un défaut d'affichage : c'est l'argent d'un client qui part chez un
  inconnu.
- **Le cockpit dit à l'écran qu'il range dans ce navigateur-ci.** Un outil qui
  laisse croire qu'il sauvegarde ailleurs finit par perdre les données de
  quelqu'un — c'est exactement ce que Railway a fait le 2026-08-01.
- **Le loquet du cockpit est annoncé comme un loquet, pas comme une serrure.**
  Il n'y a pas de serveur : il n'y a rien à voler ailleurs.
- **Tirets cadratins retirés de tout le texte vu par le client** (15), et
  espaces insécables posées avant les « ? » des titres.

## À appliquer dans NEBULA

- **La règle « regarder les captures » a encore payé, et lourdement.** Trois
  défauts réels (repères invisibles, page qui glisse de côté, tampon tranché)
  sont passés au travers de 92 contrôles verts. Le vert et l'œil sont deux
  critères, pas un.
- **Le couple `_qc.js` + `_predeploy.js` est le bon patron**, repris du client
  10 : le premier dit si c'est bon, le second refuse de publier si ça ne l'est
  pas. À reprendre sur tout produit qui encaisse de l'argent.
- Deux pièges méritent leur place dans `_memoire/lecons.md` : le `transform`
  CSS qui efface l'attribut SVG, et la boîte géante d'un élément en 3D.

## Prochaine étape

1. **Obtenir les deux numéros Mobile Money** (10 chiffres, préfixe `01`) et le
   nom du titulaire. C'est le seul blocage.
2. `node _predeploy.js` puis déployer sur Cloudflare Pages, projet `piste`,
   brancher `piste.nebula-agency.online`, autoriser les robots des IA.
3. **Le moteur de collecte** (décision 41) : sans lui, sept commandes de
   30 fiches vident le stock, puisque l'exclusivité de 90 jours retire chaque
   fiche vendue.
4. Poser SPF, DKIM et DMARC sur `piste@nebula-agency.online`.
