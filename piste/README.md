# PISTE by NEBULA — la V1

> Vendre des prospects d'entreprise vérifiés, prêts à être contactés, en
> Afrique de l'Ouest francophone.
> **Ce que c'est, en une phrase :** le client dit qui il cherche, PISTE lui
> livre un carnet de prospects réels, avec le message déjà écrit pour chacun.

Les 46 décisions produit sont dans **`PRODUCT.md`**. En cas de désaccord entre
ce fichier et le code, c'est `PRODUCT.md` qui a raison.

---

## En une minute

```bash
cd piste
npm install
npm run dev        # http://localhost:5173
npm run build      # -> dist/
npm run qc         # 95 contrôles, doit finir sur « TOUT EST VERT »
node _predeploy.js # le garde-barrière : il REFUSE tant que quelque chose cloche
```

---

## ⛔ Ce qui bloque la mise en ligne aujourd'hui

**Les numéros Mobile Money qui reçoivent l'argent ne sont pas confirmés.**

Ils vivent dans `src/donnees.js`, dans le bloc `MOMO`, avec `aConfirmer: true`.
Tant que ce drapeau est levé :

- **la page de paiement n'affiche aucun numéro.** Elle dit la vérité, qui est
  aussi la solution : *« le numéro vous est donné sur WhatsApp, à l'instant où
  votre commande arrive »*. Le parcours marche de bout en bout, personne n'est
  bloqué ;
- **`node _predeploy.js` refuse de préparer un déploiement.**

Pour lever le blocage, il faut de Mongazi : les deux numéros (MTN MoMo et Moov
Flooz), **10 chiffres commençant par `01`** — l'ARCEP l'impose depuis le
30/11/2024, un numéro à 8 chiffres ne recevra rien — et le **nom du titulaire
tel qu'il s'affiche à la réception**, pour que le client vérifie qu'il paie la
bonne personne. On les écrit, on passe `aConfirmer` à `false`, c'est tout.

> Un numéro de paiement faux n'est pas un défaut d'affichage : c'est l'argent
> d'un client qui part chez un inconnu, et ça ne se rattrape pas le lendemain.

---

## Comment la commande voyage, en V1

Il n'y a **pas de serveur** : le site est un paquet statique sur Cloudflare
Pages. La commande passe donc par le canal que tout le monde sait déjà ouvrir.

```
  le client compose         ->  WhatsApp de NEBULA
  Mongazi colle le message  ->  son cockpit  ->  encaisse -> payé -> livré
```

Le message WhatsApp est **le format d'échange**. Il est écrit pour être lu par
un humain d'abord (aucun bloc technique dedans), et le cockpit sait le relire
parce que c'est PISTE qui l'a composé. `composerMessage()` et `lireMessage()`
dans `src/etat.js` **vont ensemble** : toucher à l'un sans l'autre casse le
cockpit, et le contrôle qualité le dit tout de suite.

Le cockpit range les commandes **dans le navigateur de Mongazi**, sur son
appareil. C'est écrit à l'écran, en clair : un outil qui laisse croire qu'il
sauvegarde ailleurs finit par perdre les données de quelqu'un. Le bouton CSV
est la seule sauvegarde tant que la base n'existe pas.

---

## Les fichiers

| Fichier | Ce qu'il porte |
|---|---|
| `PRODUCT.md` | Les 46 décisions. **La source de vérité.** |
| `src/donnees.js` | Les vraies données du 3 août, l'inventaire, le bloc `MOMO`. ⚠️ **Rien d'inventé n'entre ici.** |
| `src/prix.js` | Le barème. Rend le calcul **ligne par ligne**, jamais un total seul |
| `src/etat.js` | Le code de commande, le message WhatsApp et sa relecture, le rangement, les routes |
| `src/index.css` | La direction artistique et les 8 gestes |
| `src/composants/` | `Vitrine` · `Questionnaire` · `Paiement` · `Cockpit` · `Origine` + les briques |
| `_qc.js` | Les 95 contrôles |
| `_predeploy.js` | Le garde-barrière de la mise en ligne |
| `_captures.mjs` · `_tranches.mjs` | Les captures qu'on **regarde** avant de dire « fini » |

---

## La direction artistique

**La phrase :** *une piste, c'est une trace qu'on relève sur le terrain et
qu'on suit jusqu'à la porte du commerçant.*

Tous les gestes en sortent, **un par section, et jamais deux fois le même** :

| Section | Le geste |
|---|---|
| Héros | la trace se dessine, les repères se plantent dessus |
| Ruban | ce qui a été relevé, qui défile |
| La preuve | le semis : 187 points, un par commerce, comptables à l'œil |
| Le carnet | la fiche qu'on relève du sol, ligne à ligne |
| Les 3 étapes | la trace verticale et ses repères |
| Le barème | le tampon qu'on pose sur le tarif |
| La garantie | la porte qui s'ouvre |
| Le questionnaire | le jalon qu'on plante à chaque question franchie |

Couleur de la piste en latérite. Jamais `#000` ni `#fff` en fond : une encre,
un papier. Police Bricolage Grotesque, servie depuis le paquet — **aucune
requête vers l'extérieur**, la page se charge entière hors ligne.

---

## Les pièges déjà payés, à ne pas repayer

1. **En SVG, un `transform` CSS n'ajoute rien à l'attribut `transform` : il
   l'efface.** Les cinq repères du héros retombaient sur le coin du viewBox,
   donc hors cadre, donc invisibles. Il faut **deux groupes** : l'extérieur
   pose, l'intérieur anime. *92 contrôles verts n'y ont rien vu — il a fallu
   regarder l'image.*
2. **Un `useMemo` après un retour anticipé** (le loquet du cockpit) change le
   nombre de hooks entre deux rendus : React #310, et toute l'application
   disparaît.
3. **Une carte animée en 3D pousse la page de côté.** `rotateY(-72deg)` sous
   perspective donne une boîte de 5 000 px de large tant que la porte est
   fermée. Elle vit dans un cadre `overflow-hidden`.
4. **La barre de prix est en `position: fixed`** : jamais à l'intérieur d'un
   élément animé par `transform`, sinon elle défile avec la page.
5. **Le code de commande est tiré au hasard, pas dérivé de l'heure.** Une
   première version donnait 1 024 possibilités par seconde : 400 codes tirés,
   342 distincts. Un doublon, c'est une commande qui en écrase une autre.
6. **`fcfa()` sépare les milliers par une espace fine insécable.** Pour
   comparer un montant affiché à un montant calculé, normaliser les espaces.
7. **Aucun tiret cadratin dans le texte vu par le client** (règle NEBULA) :
   deux-points, virgule, point médian.

---

## Ce qui reste

- **Le moteur de collecte** (décision 41), sur GitHub Actions, chaque nuit.
  Sans lui : sept commandes de 30 fiches et le stock est vide, parce que
  l'exclusivité de 90 jours retire du stock chaque fiche vendue.
- **Abidjan** : aucune source ivoirienne relevée. La ville est affichée
  « bientôt » et n'est pas commandable. À ouvrir seulement après avoir relevé
  pour de vrai.
- **Le paiement depuis le Togo et la Côte d'Ivoire** vers un compte béninois :
  non testé. Ne rien promettre avant d'avoir envoyé 1 000 F pour de vrai.
- **`piste@nebula-agency.online`** : SPF, DKIM et DMARC à poser, sinon les
  emails de livraison tombent en indésirable.
- Le sous-domaine `piste.nebula-agency.online` à brancher sur le projet
  Cloudflare Pages, et les robots des IA à autoriser dessus (`ai_bots_protection`,
  voir `CLAUDE.md`).
