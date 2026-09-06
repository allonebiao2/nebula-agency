# 2026-09-06 · MINUIT : finaliser l'idée de la lettre digitale

**La demande de Mongazi, en entier** : « Finalise-moi l'idée de la lettre
digitale. »

Le dossier du 27 août disait quoi vendre et pourquoi. Le manuel du 28 disait ce
qui se passe le mardi matin. Le gabarit et le constructeur existaient depuis le
2 septembre, la vidéo depuis le 3. Il restait **douze questions ouvertes**, dont
une qui portait le nom du produit.

Livrables : **`_plans/2026-09-06-minuit-arrete.html`** (les 12 décisions),
**`minuit/CONDITIONS.md`** (ce qu'on promet, et le retrait), et le code qui tient
la première d'entre elles.

---

## 1 · Ce qui a changé en dix jours, et que le dossier ne pouvait pas savoir

Un dossier vieux de dix jours n'est pas faux, il est daté. Trois faits ont bougé
dans le dépôt depuis le 27 août, et chacun retire ou remplace une brique du plan.

**SasPay est en ligne depuis le 3 septembre.** PISTE encaisse par Mobile Money
et par carte, 61 réseaux vérifiés au Bénin, au Togo et en Côte d'Ivoire, minimum
200 F, **et le carnet part tout seul dès qu'un paiement est confirmé**. Le
dossier supposait FedaPay et une vérification à la main : ce n'est plus la
meilleure option disponible, c'est la moins bonne.

**⛔ n8n tournait sur un VPS qui n'appartient plus à Mongazi.** Le dossier ET le
manuel confient tous les deux « la livraison à l'heure choisie » à n8n. Or la
ligne de stack dit « n8n self-hosted (Hostinger VPS 72.61.103.56) » et la section
infrastructure dit, depuis des semaines, que **cette machine n'est plus la
sienne**. Les deux informations vivent dans le même fichier, à cinq cents lignes
d'écart, sans jamais se rencontrer. **La fonction la plus vendeuse du produit
reposait sur un serveur perdu.**

**La vidéo promettait une chose qui n'existait pas.** « Elle l'ouvre à minuit
pile. Pas avant. » Rien, nulle part, ne tenait cette heure le 3 septembre.

---

## 2 · ⛔ Le défaut principal : la fonction qui donne son nom au produit n'existait nulle part

Le constructeur demandait la date et l'heure (`quand`, `quandH`), les gardait
dans son état, les sauvegardait avec le brouillon, et l'écran final annonçait :

> « Elle la recevra le 14 février à 00:00. »

Ces deux valeurs **n'entraient dans aucune lettre livrée**, et aucune machine ne
les lisait ailleurs. Le produit portait le nom d'une fonction écrite à aucun
endroit.

⚠️ **Aucun des 82 contrôles ne pouvait le voir.** On ne mesure pas l'absence
d'une chose dont personne n'a écrit qu'elle devait exister. Même famille que la
photo livrée et jamais affichée chez Au Braisé d'Or le 27/08 : le QC ne voit que
ce qu'on lui a appris à regarder.

### La décision : l'heure vit DANS la lettre

Au lieu de chercher une autre machine à envoyer, on met l'heure dans l'objet.
**Avant l'heure choisie, le cachet ne se brise pas.**

- **Avant l'heure** : la cire dort (éteinte, immobile), il n'y a **aucun bouton à
  pousser**, et la page **dit** quand elle s'ouvre : « Elle s'ouvre dimanche
  7 septembre à minuit », avec un compte à rebours en dessous.
- **À l'heure** : la cire s'allume, le bouton paraît, **sans rechargement**, et
  la ligne d'attente devient « C'est l'heure. »
- **Ça ne dépend de rien** : ni serveur, ni réseau, ni compte tiers. La lettre
  s'ouvre dans un taxi, hors connexion, et l'heure tient quand même.
- **Ça tient même si l'acheteur envoie son lien trois jours trop tôt**, ce
  qu'aucune machine à envoyer n'aurait rattrapé.

### Ce que ça supprime, d'un seul coup

| Ce qui disparaît | Pourquoi il était là |
|---|---|
| **n8n** | La machine à livrer. Elle n'existe plus. |
| **Le modèle WhatsApp approuvé par Meta** | Nécessaire seulement pour écrire hors de la fenêtre de 24 h. On n'écrit plus à personne. |
| **Le coût d'un envoi** | Un message par lettre, à un ticket de 2 000 F. |
| **Le risque le plus grave du produit** | Une machine qui écrit à une personne qui n'a jamais donné son numéro **est** l'outil de harcèlement qu'on refuse d'être. |

⛔ **NEBULA n'écrit jamais à la destinataire.** C'est une décision de conception,
pas une limite technique. Le lien voyage par l'acheteur : nous fabriquons
l'objet, pas le geste.

### Les trois choix fins, et pourquoi

**Le garde-fou est dans `ouvrir()`, pas sur le bouton.** Le code secret appelle
`ouvrir()` directement ; tout chemin futur y passera aussi. Un verrou posé sur
l'interface n'est pas un verrou.

**L'heure est une heure de CALENDRIER, sans fuseau** (`2027-02-14T00:00`).
Minuit, c'est minuit **sur le téléphone de celle qui lit**. Un instant absolu
ferait s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou, et
le cadeau arriverait pendant le dîner. C'est aussi la seule règle qui ne demande
aucune plomberie de fuseau, donc la seule qui ne cassera jamais. La date est lue
à la main par une expression régulière plutôt que confiée à `new Date()`, dont
les navigateurs n'ont pas toujours traité « …T00:00 » comme une heure locale.

⛔ **On ne promet JAMAIS le secret.** Le texte d'une lettre est écrit dans la
page : qui sait lire un code source peut le lire avant l'heure, et qui avance
l'horloge de son téléphone aussi. **Le cachet tient l'heure, c'est tout**, et
c'est déjà ce qu'aucun concurrent observé ne vend. Une lettre est un cadeau
emballé, pas un coffre-fort ; un emballage qu'on peut déchirer reste un
emballage, il tient parce qu'on a envie qu'il tienne.

---

## 3 · Deux défauts de caisse, trouvés en relisant le code en face du document

### ⛔ Deux échelles de prix, et l'une des deux mentait

Chaque occasion portait un prix affiché « dès 10 000 F ». Chaque palier portait
le vrai prix. **Rien ne reliait les deux** : on choisissait « Demande en mariage ·
dès 10 000 F », puis le palier gratuit, et on partait avec la lettre **sans payer
un franc**.

Le manuel fixe les prix par occasion, le constructeur par palier : les deux
avaient raison dans leur fichier. L'écran des paliers disait déjà la vérité
(« la lettre est déjà écrite, elle ne change pas selon le prix »).

**Décision : le palier fixe le prix, l'occasion décide du ton.** Le champ `prix`
a été **retiré** des occasions, pas seulement caché : la structure impose la
règle. La ligne événement (faire-part, deuil) garde ses prix propres, parce que
là, la page fait vraiment davantage.

### ⛔ La lettre offerte passait par la caisse

```js
aller(p.prix === 0 ? "e-paiement" : "e-paiement");
```

Les deux branches sont identiques : quelqu'un avait vu le problème, écrit le
test, et jamais écrit la destination. Le palier gratuit, **celui qui porte toute
la boucle virale** et qui doit être le plus fluide du site, affichait « Envoie
exactement cette somme, au franc près » au-dessus d'un numéro Mobile Money, pour
zéro franc, et réclamait une référence de SMS.

**Décision : un seul écran, qui change de nature.** Offert, il demande seulement
où envoyer le lien. Payé, la caisse revient. Le WhatsApp est demandé dans les
deux cas, donc on ne dédouble pas le parcours.

### ⛔ Le seuil n'était mesuré par rien

Le contrôle de contraste ne regardait que le corps de la lettre. Or **une lettre
programmée ne montre que son seuil**, parfois pendant des heures, et c'est là que
vit le compte à rebours.

Le même gris `#6d6478` tient **4,8:1** sur le papier de la lettre et tombe à
**3,09:1** sur la nuit du seuil, mesuré sur les pixels rendus. C'est l'inverse
exact de l'or d'Angy Art (qui avait besoin d'une variante **foncée** pour le
crème) : ici il fallait une variante **claire** pour la nuit.

→ `--gris-nuit: #8f86a0`, et quatre contrôles qui mesurent les quatre textes du
seuil. **Sonde vérifiée** : avec l'ancien gris elle rend 3,09 et passe au rouge.

---

## 4 · Les douze décisions

Détail et raisons dans `_plans/2026-09-06-minuit-arrete.html`.

| № | Décision | État |
|---|---|---|
| 01 | **MINUIT** est le nom, arrêté | arrêté |
| 02 | L'heure vit **dans la lettre** | ✅ fait |
| 03 | **NEBULA n'écrit jamais** à la destinataire | arrêté |
| 04 | Heure de **calendrier**, téléphone de qui reçoit | ✅ fait |
| 05 | **SasPay**, comme PISTE. La référence collée disparaît | arrêté |
| 06 | **Cloudflare Pages + Supabase**, jamais Render | arrêté |
| 07 | Le **palier** fixe le prix, l'occasion le ton | ✅ fait |
| 08 | Quatre paliers, **un seul règlement en francs** | arrêté |
| 09 | Le paquet détournement : **`CONDITIONS.md`** | ✅ écrit |
| 10 | **Trois lignes** : lettre, faire-part, deuil | arrêté |
| 11 | Le faire-part vise **novembre**, pas février | arrêté |
| 12 | On tranche le **1er décembre 2026** | arrêté |

### Pourquoi pas Render, alors que le manuel le prévoyait

`vitrina/server.py` range les commandes dans un **fichier SQLite posé à côté du
code**. Sur Render, le disque est effacé à chaque déploiement : c'est exactement
ce qui avait fait disparaître les deux PDF des partenaires. **Un déploiement, et
les lettres payées n'existent plus.** Supabase porte déjà PISTE, le bureau des
partenaires et Boussole ; MINUIT y est un schéma de plus, pas une facture de
plus. ⚠️ Contrepartie à écrire noir sur blanc : ce projet Supabase unique
porterait alors **quatre** produits, et s'il est mis en pause, les quatre
tombent ensemble.

### Pourquoi novembre et pas février

Le calendrier du manuel le dit sans le dire : novembre et décembre sont le
meilleur chiffre d'affaires de l'année, **à ticket élevé** (saison des mariages,
retour de la diaspora, faire-part à 25 000 F). Février est un pic de **volume à
petit ticket**. Viser la Saint-Valentin d'abord, c'est travailler cinq mois pour
le mois qui rapporte le moins.

---

## 5 · `CONDITIONS.md` : le paquet qui conditionne la première vente

Le dossier classait le détournement en risque **critique** et notait qu'aucune
des cinq références observées ne le traite. C'est écrit, c'est court, et il n'y
a plus rien à inventer le jour où quelqu'un appelle.

- **L'adresse ne se devine pas** : un jeton tiré au hasard, jamais un numéro qui
  se suit.
- **Aucune indexation** : la balise est dans le gabarit, l'en-tête `X-Robots-Tag`
  devra l'être côté serveur (une balise dans la page ne couvre pas une réponse
  qui n'est pas de l'HTML).
- **Ça expire** : 7 jours offert, 1 an payé.
- **Aucune mesure d'audience** sur une lettre.
- **Le retrait sous 24 h**, sur simple demande de la personne visée : sans
  discuter, sans prévenir l'acheteur, sans rembourser, sans demander de preuve.
  ⚠️ **Le pouvoir de retirer appartient à qui détient le lien**, ce qui est
  exactement l'ensemble des gens concernés : personne d'autre ne peut l'avoir
  sans qu'un des deux le lui ait donné.
- **Le deuil n'ouvre pas** tant que la page n'a pas été relue par quelqu'un qui
  vient d'enterrer un proche. Ce n'est pas une précaution de style, c'est la
  condition d'ouverture.

---

## 6 · Le contrôle

**QC 82 → 115 contrôles verts**, deux passages d'affilée.

17 pour le verrou d'heure, 4 pour le contraste du seuil, 3 structurels sur
l'échelle de prix, 9 pour la caisse et l'heure livrée.

⚠️ **Chaque verrou a son TÉMOIN** : une heure déjà passée, un palier payé. Sans
lui, un verrou resté fermé pour toujours passerait tous les contrôles du verrou
avec les honneurs, et un écran de caisse toujours nu passerait les quatre
contrôles du palier gratuit.

⚠️ **Un compte à rebours ne se mesure pas avec deux instantanés** : il change une
fois par seconde, deux lectures tombent dans la même. On échantillonne quatre
fois et on exige seulement que deux valeurs diffèrent. Même famille que les
pastilles animées d'Hillary (20/08).

⚠️ **Le dégel se mesure sous les yeux** : une lettre programmée à trois secondes,
et on vérifie que le bouton paraît seul, **que la page ne s'est pas rechargée**
(un témoin posé sur `window` avant), et que la cire a changé de filtre.

Les captures ont été **regardées** (`python minuit/_voir.py`, planches
`verrou-390` et `verrou-1440`), et c'est là qu'on a vu que « dans 5 h 11 » se lit
comme une heure de la journée, pas comme une durée → « dans 5 h 11 min ».

---

## 7 · ⏳ Ce qui reste, et qui n'appartient qu'à Mongazi

| Ce qu'il faut | Pourquoi ça bloque |
|---|---|
| **Le compte qui encaisse** | Le constructeur affiche un numéro Mobile Money au nom de « NEBULA Agency ». Avec SasPay il disparaît, mais le compte qui reçoit doit exister. |
| **Le sous-domaine** | Une lettre voyage dans un message : l'adresse est la première chose qu'on voit du produit. `minuit.nebula-agency.online`, **une seule**. |
| **Un n8n ailleurs, oui ou non** | Ça ne change plus rien pour MINUIT, mais ça rouvre les relances de renouvellements, qui en dépendaient aussi sans le savoir. |
| **La commission SasPay** | Sur un ticket à 2 000 F, le taux décide de la marge. Écrit nulle part dans le dépôt. |
| **Qui relit le deuil** | La ligne la plus rentable de la partie événement, et la seule où une maladresse de ton abîme la marque pour longtemps. |
| **Le premier franc** | Comme pour PISTE : le seul essai qui prouve le dernier maillon. Une boutique qui n'a jamais encaissé n'est pas ouverte, elle est en préparation. |

**Et l'euro** : le dossier prévoyait une page en euros pour la diaspora. La carte
existe chez SasPay, **l'euro n'est pas vérifié**. En attendant : prix affiché en
euros, **débité en francs**, et la page le dit. Un prix affiché dans une monnaie
et prélevé dans une autre sans le dire fabrique une réclamation.

---

## 8 · SECOND TEMPS — la caisse et l'adresse

Étape 2 de l'arrêté, écrite dans la foulée. **Rien n'est déployé** (il manque
six réponses de Mongazi), mais tout ce qui décide est écrit et essayé.
Marche à suivre complète : **`minuit/PAIEMENT.md`**.

### Ce qui est posé

- **`supabase/lettres.sql`** : le schéma `minuit`, les sessions de paiement, le
  journal des notifications, et **huit portes que seul le `service_role` peut
  pousser**. Même forme que PISTE, qui encaisse depuis le 2026-09-03.
- **Trois fonctions de bord** : `minuit-commande` (déposer + ouvrir le
  paiement), `minuit-paiement-recu` (le webhook signé, qui **ouvre la lettre**),
  `minuit-lettre` (servir, et **retirer**).
- **`_shared/lettre.ts`** : tout ce qui décide, en Web standard, donc essayable
  sous Node **sans clé, sans réseau et sans base**. 118 contrôles.
- **Le constructeur parle enfin à la caisse.** Il posait sa commande sur
  `window.MINUIT_COMMANDE` et elle n'allait nulle part : c'était une
  démonstration.

### ⛔ Les deux règles qui ont décidé de tout le reste

**On ne stocke jamais le HTML du navigateur.** Une porte publique qui accepte
du HTML et le sert sur notre domaine est **un hébergeur de pages arbitraires** :
gratuit, anonyme, et parfait pour une page qui imite une banque. On stocke les
**données**, et la lettre est **rebâtie** à partir du gabarit à chaque lecture.
Conséquence heureuse : une correction dans `lettre.html` profite à toutes les
lettres déjà vendues.

**Le prix ne vient jamais du navigateur.** Le constructeur est un paquet
statique : ce qu'il annonce se réécrit dans la console en trois secondes. Le
barème de `_shared/lettre.ts` est le seul qui engage la caisse, et un contrôle
**lit les deux côtés** et refuse la moindre différence. Même règle pour le pied
viral (sinon il se retire d'un clic) et pour le code secret.

### L'écran de la référence disparaît

Avec le numéro Mobile Money et le choix du réseau. C'était **le moment le plus
fragile de toute la chaîne**, et la validation à la main rendait le palier à
2 000 F déficitaire, ce que le manuel interdit lui-même. L'écran dit maintenant
la somme, « Mobile Money ou carte, sur la page de notre encaisseur », et le
bouton annonce **« Payer 5 000 F »**.

### ⛔ Trois fois le même piège, dans la même journée

**U+2028 écrit EN CLAIR dans les expressions régulières qui doivent le
neutraliser** : dans `lettre.ts`, puis dans le contrôle qui essaie `lettre.ts`.
Le README documente ce piège depuis le 2026-09-02, où il s'était déjà produit
deux fois.

⚠️ **Un fichier qui documente son propre piège doit être vérifié comme s'il le
contenait**, parce que c'est souvent le cas. Les deux fois, c'est le
**chargement du module** qui l'a dit, immédiatement : écrire un garde-fou sans
l'exécuter une fois, c'est écrire une intention.

### ⚠️ Deux sondes qui mentaient, encore

- L'une lisait la **ligne d'import** au lieu de l'appel (« une lettre offerte
  n'ouvre aucun paiement » accusait un code sain, parce que le mot
  `ouvrirSession` figure en haut du fichier).
- L'autre interrogeait **`pg.url` en boucle** pour attendre une navigation :
  le contexte d'exécution est détruit pendant qu'elle a lieu, et la sonde
  tombe sur « Execution context was destroyed » ou conclut trop tôt que rien
  n'a bougé. Playwright a un guetteur pour ça (`wait_for_url`), et lui survit
  au changement de page.
- ⛔ Et **`localStorage` appartient à l'ORIGINE** : lu depuis la page de
  paiement, il rend le rangement d'un autre site. Le contrôle « son brouillon
  l'attend » revient d'abord sur le constructeur.

### Un défaut de conception attrapé par un contrôle

`jeton()` tirait au sort dans une boucle **non bornée** : une source de hasard
qui ne rendrait que des octets rejetés l'aurait fait tourner pour toujours, et
**un serveur qui tourne pour toujours ne dit rien, il ne répond plus**. La
boucle est bornée, et lève une erreur nommée. C'est le contrôle qui l'a
trouvé, en lui donnant exactement ce hasard-là.

### ⚠️ Trois contrôles RETOURNÉS, pas supprimés

« Sans référence, la commande ne part pas » disait quelque chose de vrai sur le
produit, et c'est ce quelque chose qui a changé : il dit maintenant « il n'y a
plus de référence à coller ». Idem pour « la commande porte le HTML complet de
la lettre », devenu **« ⛔ la commande ne porte AUCUN HTML »**.

### Un troisième sérialiseur, donc une troisième vérité

`_injecter.py` (Python), `creer.html` (navigateur) et `_shared/lettre.ts`
(Deno) écrivent tous les trois des données dans le gabarit. Python écrivait
`"a": 1` là où les deux autres écrivent `"a":1` : **même règle, trois octets
différents**. Séparateurs compacts partout, et le contrôle passe la même
batterie hostile aux deux implémentations en exigeant **le même octet**.

**Contrôles : 115 → 127 (la lettre) + 118 (la caisse).**

---

## 9 · Les fichiers touchés

| Fichier | Ce qui a changé |
|---|---|
| `minuit/lettre.html` | Le verrou d'heure, `--gris-nuit`, la signature du seuil étendue |
| `minuit/creer.html` | L'heure part avec la lettre, une seule échelle de prix, la caisse qui change de nature |
| `minuit/_qc.py` | 82 → **115 contrôles** |
| `minuit/_voir.py` | Une planche de plus : le seuil verrouillé |
| `minuit/CONDITIONS.md` | **Neuf** |
| `_plans/2026-09-06-minuit-arrete.html` | **Neuf** : les 12 décisions |
| `minuit/README.md`, `CLAUDE.md` | L'état réel, et la contradiction n8n signalée |
| `minuit/supabase/` | **Neuf** : la base et les trois fonctions de bord |
| `minuit/_qc_caisse.mjs` | **Neuf** : 118 contrôles, sans clé ni réseau |
| `minuit/_gabarit_ts.py` | **Neuf** : le gabarit voyage avec le code |
| `minuit/PAIEMENT.md` | **Neuf** : où vit chaque morceau, et comment brancher |
| `minuit/_injecter.py` | Séparateurs compacts : trois sérialiseurs, un seul octet |
