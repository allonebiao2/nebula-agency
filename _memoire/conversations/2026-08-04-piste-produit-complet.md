# 2026-08-04 · PISTE, de l'idée au produit en ligne

> Session terminal, Cotonou. Un produit entier construit, mis en ligne et
> corrigé dans la journée. **88 décisions** verrouillées, écrites dans
> `piste/PRODUCT.md`, qui reste la source de vérité.

---

## Ce qu'est PISTE

**Le client dit qui il cherche, PISTE lui livre un carnet de prospects réels,
avec le message déjà écrit pour chacun.**

En ligne : **https://piste.nebula-agency.online** · cockpit `…/#/cockpit` ·
carnet client `…/#/carnet/<jeton>` · reçu `…/#/recu/<jeton>`

Ce n'est pas un fichier, c'est un carnet de travail : on ouvre au téléphone, on
appuie, WhatsApp s'ouvre sur la bonne conversation avec le bon message.

## Le point de départ

Mongazi cherchait des restaurants et des salons de couture à démarcher au Bénin
et au Togo. J'ai relevé **187 commerces à la main en une heure** dans un
annuaire professionnel public. PISTE, c'est cette heure automatisée et vendue.

---

## Les cinq briques

| Brique | Où | État |
|---|---|---|
| **Le générateur** | la page d'accueil | tout se règle sur un panneau, prix en direct, 3 vraies fiches |
| **Le carnet du client** | `#/carnet/<jeton>` | ses fiches, numéros complets, un bouton WhatsApp par ligne |
| **Le moteur de collecte** | GitHub Actions, chaque nuit | 187 → **7 817 fiches** en une journée |
| **Le reçu** | `#/recu/<jeton>` | imprimable, le navigateur fait le PDF |
| **Le cockpit** | `#/cockpit` | les commandes, et la marche à suivre en 6 gestes |

## Le barème

**Une fiche coûte entre 100 F et 250 F, jamais plus.** Base 100 F, et quatre
suppléments qui valent exactement 150 F réunis : numéro testé +60, pas de site
+40, nom du dirigeant +30, message écrit +20. **La règle est vérifiée dans le
code**, pas seulement écrite en commentaire.

Remises : 50 fiches −10 % · 200 −20 % · 500 −30 %. Minimum 10 fiches.
Exclusivité **90 jours**. Livraison **24 h**. **MTN MoMo seul.**

---

## Les décisions qui structurent tout

**Le numéro de téléphone est le cœur de la valeur.** Une fiche n'entre dans le
vivier vendable que si elle a un numéro valide au bon format, un nom lisible,
un métier et une localité. Le reste va dans un vivier « à visiter », séparé.

**Plusieurs métiers à la fois.** Un grossiste en boissons veut les restaurants
ET les alimentations. L'obliger à commander deux fois, c'est lui facturer deux
fois le minimum pour rien.

**On ne vend jamais ce qui n'existe pas.** Le stock s'affiche à côté de chaque
ville, le curseur ne le dépasse pas, et une combinaison sous le minimum bascule
en « prévenez-moi » au lieu de bloquer.

**L'apprentissage part du seul signal qui existe** : les marques du carnet
(Écrit / Rendez-vous / Vendu / Non), qui remontent désormais — **et on le dit au
client en toutes lettres**. Des règles écrites à la main d'abord ; un modèle
seulement quand il y aura de quoi l'entraîner. Un modèle entraîné sur rien
aurait l'air savant et serait faux.

---

## Vibe Prospecting : testé, pas supposé

Il connaît 6 779 entreprises au Bénin et au Togo, mais ce sont des sociétés
**inscrites sur LinkedIn** : banques, cabinets de recrutement, agences de
communication. Une recherche « restaurant, maquis, couture, tailleur,
pâtisserie » y rend 61 résultats, **dont pas un seul restaurant ni un seul
atelier de couture**. Et aucune fiche d'entreprise ne porte de numéro.

**Correction de Mongazi, et elle est juste** : ce sont quand même de vraies
structures. PISTE vend donc **deux viviers** — les commerces (notre moteur) et
les structures (Vibe Prospecting), pour deux acheteurs différents. Le second
n'est pas encore construit.

---

## Six vraies pannes, corrigées

### 1. Le dépôt public exposait la marchandise
`allonebiao2/nebula-agency` répond 200 sur l'API GitHub. Les fiches et leurs
numéros y étaient lisibles gratuitement. **Le dépôt garde les outils, la base
garde les données.**

### 2. Le masque qui ne masquait rien
Les numéros d'aperçu étaient masqués **à l'affichage** : le numéro complet
partait quand même dans le paquet JavaScript. Ils sont désormais **coupés à la
source**.

### 3. Les prospects du site de l'agence étaient perdus
Angélique AVOCEVOU, 4 août 09h47 : sa demande est partie sur le WhatsApp de
Mongazi mais n'est **jamais** arrivée en base. Le code faisait `fetch(...)` sans
l'attendre puis `window.open(wa.me)` : sur téléphone, ouvrir WhatsApp annule la
requête. Et l'appel était dans un `catch` vide, donc l'échec était **silencieux**.
Remède : `navigator.sendBeacon`. Vérifié dans un vrai navigateur.

### 4. Cloudflare a mis une erreur en cache pour un an
PISTE est apparu entièrement sans style. La feuille de style répondait **200,
bon type, bonne taille**, et son contenu était `error code: 502`. Vite nommant
les fichiers d'après leur contenu, reconstruire redonnait les mêmes adresses
empoisonnées : **le site ne pouvait pas se réparer tout seul**.
Remède : une **marque de déploiement** dans le nom des fichiers. Détail complet
dans `_memoire/lecons.md`.

### 5. Une révélation qui cachait ce qu'elle révélait
Les repères 3D partaient d'`opacity: 0` avec une animation d'entrée qui ne s'est
jamais déclenchée : **invisibles pour toujours, sans rien pour le signaler**.
C'est la règle de la charte, réapprise à la dure.

### 6. Le site ne vendait que 3 métiers sur 9
Le moteur en avait ramené neuf. Personne ne pouvait acheter les six autres. Les
métiers du site **découlent maintenant du moteur**.

---

## Ce qui reste

- **Le deuxième vivier** (les structures, via Vibe Prospecting) : décidé, pas construit
- **La marque de déploiement sur les autres sites** du parc ⏳ *demandé par Mongazi, à faire plus tard*
- **Le paiement depuis le Togo et la Côte d'Ivoire** vers un compte béninois : jamais testé
- **Les stratégies de vente** de PISTE : jamais abordées
- ⚠️ **Le jeton de purge Cloudflare a transité par la conversation**, à changer

## Liens

- `piste/PRODUCT.md` — les 88 décisions, source de vérité
- [[2026-08-03-backoffices-refonte-et-documents]]
- `_memoire/lecons.md` — la panne Cloudflare, les leçons Postgres
- `scripts/purger.py` — le bouton de secours du cache

---

## Rallonge du soir · le code du cockpit, et la panne de cache qui revient

### Un secret qu'on ne peut pas taper n'est pas un secret, c'est un blocage

Mongazi a voulu fabriquer un carnet et s'est heurté à une demande de mot de
passe. Il a cru à un code Google, a tenté `2915`, et s'est fait refuser.

Le mot de passe était **24 caractères au hasard**. Juste en théorie. Sur un
téléphone, entre deux rendez-vous, inutilisable. Et le message ne disait ni ce
que c'était, ni où le trouver.

**Mongazi a choisi son code : `19984`.** C'est le bon choix, et la sécurité se
déplace : elle ne vient plus de la longueur du code mais de **ce qui arrive à
celui qui le devine mal**.

- table `piste.tentatives` + `public.piste_verrouille()` / `piste_tentative()`
- **10 échecs en 15 minutes** et tout est refusé 15 minutes, **même le bon code**
- se tromper trois fois ne gêne jamais ; essayer mille codes est arrêté au dixième
- **le verrou n'efface jamais le code enregistré** : un compteur qui mord ne doit
  pas faire oublier un code pourtant bon

Vérifié en ligne : mauvais code → 401 · dixième essai → 429 · le bon code
pendant le verrou → refusé aussi · compteur vidé après le test.

Décisions **89 et 90** ajoutées à `piste/PRODUCT.md`.

### La panne de cache est revenue, et c'est notre outil de contrôle qui l'a causée

Même symptôme que l'après-midi (site sans style), cause différente.

**Deux défauts se combinaient.** Un fichier absent répondait **200 avec du
HTML** (Cloudflare Pages sert la page d'accueil pour toute adresse inconnue
quand il n'y a pas de `404.html`), et `/assets/*` porte `immutable` un an. Le
HTML de repli héritait donc d'un an de cache, à la place du CSS.

**Le déclencheur : `purger.py --verifier`, lancé dans la seconde suivant le
déploiement.** La propagation n'était pas finie ; la vérification a reçu la
page de repli, et Cloudflare l'a écrite dans le cache.

> **Vérifier à travers un cache n'est pas un geste neutre : la réponse obtenue
> est écrite dans le cache. Une vérification trop tôt fabrique la panne qu'elle
> cherche.**

Deux remèdes posés :

- **`piste/public/404.html`** : une adresse inconnue répond enfin un vrai 404,
  qui ne se met pas en cache comme une ressource permanente. ⚠️ **À poser sur
  chaque site du parc** — ajouté à la PHASE 8 de `procedure-vitrine/PROCEDURE.md`.
- **L'ordre de vérification** écrit en tête de `purger.py` : origine d'abord
  (aucun cache devant), domaine en dernier, 45 s d'attente entre les deux.
  `--verifier` lit maintenant `cf-cache-status` et dit si c'est le cache ou
  l'origine.

État final vérifié en ligne : CSS `text/css`, JS `application/javascript`,
fichier absent `404`, nouveau message du cockpit servi, 130 contrôles verts.

---

## Le cockpit ne lisait pas le serveur · tonalité et notifications

### Le trou, découvert en voulant ajouter une sonnerie

Mongazi a demandé une tonalité quand une commande arrive. En cherchant où la
brancher, on découvre que **le cockpit ne lisait que le navigateur de
Mongazi**. Une commande passée depuis le téléphone d'un client existait en
base, déclenchait deux courriels, et **n'apparaissait jamais** tant qu'il ne
recollait pas le message WhatsApp à la main.

C'est exactement la panne du site de l'agence (Angélique, le matin même), une
étape plus loin : la donnée était bien enregistrée, mais **personne n'allait
jamais la chercher**.

> **Le jour où la porte a été ouverte : 24 commandes dormaient en base sans
> avoir jamais été vues.**

La décision 64 de `PRODUCT.md` disait « les commandes vivent dans Supabase ».
C'était vrai pour l'écriture, faux pour la lecture. **Une décision écrite n'est
pas une décision appliquée.**

### Ce qui est posé

- `public.piste_commandes_recentes()` et `piste_etat_commande()`, accordées au
  seul `service_role`, traversées par la fonction de bord **`piste-cockpit`**
  (code du cockpit exigé, même compteur d'essais)
- **la veille** : le cockpit interroge le serveur toutes les 30 s et fusionne
- **la tonalité** (`src/son.js`) : trois notes qui montent, deux fois, entièrement
  synthétisées. Aucun fichier audio : un mp3, c'est un chargement de plus, un
  404 possible, et une seconde de retard au moment où on a besoin d'être prévenu
- **la notification système**, pour être prévenu même quand PISTE est derrière
  une autre fenêtre
- **l'état payé/livré remonte en base** : sans ça, une commande marquée payée
  sur le PC réapparaît « à encaisser » sur le téléphone, et on encaisse deux fois

### Deux vocabulaires pour la même chose = une commande invisible

La base écrivait `attente`, le cockpit dit `recue`. Sans traduction, les
commandes atterrissaient dans un onglet qui n'existe pas. On traduit **à la
porte**, une seule fois, plutôt que d'entretenir deux vérités.

### Le son : trois précautions, toutes déjà connues, toutes nécessaires

1. **Aucun navigateur ne joue avant un geste.** Le contexte s'ouvre au premier
   toucher. ⚠️ Sur PC la molette ne compte pas, sur mobile un toucher compte :
   d'où le bouton **« Tester la tonalité »**, qui permet de le PROUVER au lieu
   de l'espérer.
2. **Le tampon silencieux iOS**, sans quoi un iPhone reste muet pour toujours
   alors que le code paraît parfait.
3. **Gain plus fort sur mobile + compresseur** : un niveau réglé à l'oreille
   sur un PC est inaudible dans la rue à Cotonou.

**Et il ne sonne pas au premier chargement.** Une alarme qui hurle à chaque
ouverture, on l'éteint le deuxième jour, et elle ne sert plus jamais.

### Le contrôle (`_qc_cockpit.mjs`, 19 verts)

Il ne regarde pas un bouton : il **compte les oscillateurs réellement
démarrés** et vérifie que le contexte audio est passé à `running`. Un son qui
ne se prouve pas est un son dont on découvre l'absence le jour où une commande
arrive.

**Une erreur de contrôle corrigée en route** : chercher « un numéro » dans la
page pour détecter une fuite était faux — le cockpit **affiche exprès** le
numéro Mobile Money du client, pour rapprocher les paiements. Le contrôle lit
maintenant la **réponse réseau** et vérifie qu'elle ne transporte aucune fiche.

**149 contrôles verts au total** (91 général + 39 générateur + 19 cockpit).

### Commande de test posée

`PISTE-T522` · Test NEBULA · 10 fiches restaurant Cotonou · 1 200 F ·
deux courriels partis vers `allonebiao@gmail.com`.

---

## La fiche, les quatre mots, et le cockpit devenu poste de pilotage

### « Écrit · Rendez-vous · Vendu · Non » : personne ne comprenait

Mongazi : « **et tout ceci doit être expliqué rapidement et simplement pour le
client car moi-même je ne comprends rien** ».

Quatre mots posés sans phrase autour, dans une page qu'on ouvre debout dans la
rue. **Si celui qui vend le produit ne comprend pas, aucun client ne
comprendra.**

Ils disent maintenant ce qui **s'est passé**, à la première personne :
« J'ai écrit » · « Il veut me voir » · « J'ai vendu » · « Pas intéressé »,
chacun avec sa phrase d'explication. Plus un mode d'emploi en trois gestes en
haut du carnet.

### La fiche : belle avant l'achat, plate après

Le client voyait une carte en relief dans l'aperçu du générateur, et recevait
une **liste plate** une fois payé. C'était à l'envers : ce qu'on livre doit se
tenir mieux que ce qu'on montre.

La fiche est devenue un document numéroté qu'on ouvre : bandeau sombre,
initiales, trame de sécurité, et un **dos qui bascule en 3D** autour de son
bord haut, comme une fiche cartonnée qu'on retourne. Le dos porte un relevé
façon facture et **le message qui partira**, en clair, avant d'envoyer.

⚠️ **Une rotation n'anime pas la hauteur.** Sans `grid-template-rows` de `0fr`
à `1fr`, tout ce qui est en dessous saute d'un coup pendant que le dos tourne
joliment dans le vide. Il faut les deux.

**Ouvrir WhatsApp marque « J'ai écrit »**, mais seulement si rien n'est encore
marqué. Sans ça, le seul signal d'apprentissage de PISTE dépendait d'un second
geste que personne ne fait dans la rue.

### Le cockpit : PISTE ne comptait RIEN

Mongazi voulait « des courbes, combien de personnes viennent, combien
achètent ». Il n'y avait aucune mesure. Nouvelle table `piste.visites`, porte
d'écriture ouverte au site, et `piste_tableau()` qui rend tout en un appel :
courbes 30 jours, entonnoir, argent, métiers et villes les plus cherchés,
retours des clients, état du vivier.

⚠️ **Aucune IP, aucun cookie, aucun identifiant qui survive à l'onglet.** Et on
écrit « visites », jamais « personnes » : promettre des personnes serait faux.

Direction **salle de contrôle** : le cockpit passe en sombre (ce qui donne au
passage le rythme sombre/clair que la charte demande), police **Orbitron** pour
les chiffres, compteurs qui montent, jauges, courbes SVG **sans une seule
bibliothèque**, équerres d'angle.

### ⚠️ Le tableau affichait « 1300 % vont jusqu'au bout »

Les commandes existent depuis des jours, le comptage des visites depuis une
heure. Diviser l'un par l'autre donne un chiffre absurde.

> **Un écran qui affiche 1300 % ne sert plus à rien : on cesse de le croire, y
> compris quand il a raison.**

Remède : un **second entonnoir restreint à la période entièrement mesurée**, un
**seuil de dix** en dessous duquel aucun taux ne s'affiche, et une phrase qui
dit depuis quand on compte. **Un blanc honnête vaut mieux qu'un pourcentage
faux.**

### Trois pièges techniques, tous documentés dans le code

1. **Remapper les jetons de couleur en bloc** a produit des boutons orange
   **parfaitement vides** : `creme` sert de fond de carte ET de texte clair sur
   les boutons. On ne remappe en jeton que ce qui n'a qu'un seul rôle.
2. **`linear-gradient(90deg, var(--x), var(--x)55)` est invalide.** Coller une
   transparence hexadécimale derrière une variable CSS fait jeter le dégradé
   **entier**, sans erreur, et les jauges restent vides.
3. **Deux vocabulaires pour la même chose** (`attente` en base, `recue` au
   cockpit) faisaient atterrir les commandes dans un onglet inexistant.

### Trois contrôles étaient FAUX, corrigés plutôt que contournés

- ils **codaient des chiffres en dur** (« les 30 fiches ») alors qu'on teste un
  carnet de 24
- ils mesuraient des cibles **à travers une rotation de 86°**, qui écrase la
  boîte : 120 défauts inventés
- ils prenaient le **WhatsApp de l'acheteur** pour une fuite du vivier. Un
  numéro seul ne dit pas d'où il vient ; ce qui trahit une fiche, c'est le
  **nom du champ** qui la transporte

**169 contrôles verts** (91 + 39 + 19 + 20).

### Au passage

- **`_vue.mjs`** : regarder une page section par section. ⚠️ Git Bash **avale**
  un argument qui commence par `#`, et aller de `/` à `/#/route` ne recharge
  rien : deux façons de capturer l'accueil en croyant capturer autre chose.
- Les **fonctions de bord vivent enfin dans le dépôt** (`piste/supabase/functions/`).
  Elles n'existaient nulle part : un incident chez Supabase les aurait perdues.

---

## « Je ne me vois pas lancer les appels moi-même »

### La promesse que le vendeur ne pouvait pas tenir

Le site disait, mot pour mot : « **Chaque numéro est composé avant l'envoi.** »
Le supplément coûtait 60 F la fiche, le plus cher des quatre. Et le seul moyen
de le tenir était que Mongazi compose lui-même, un numéro à la fois. **Dix
commandes de cinquante fiches font cinq cents appels.**

> **Une promesse que le vendeur ne peut pas tenir n'est pas une option, c'est
> une dette.**

Trois voies étaient possibles (un carnet de contacts WhatsApp importé en bloc,
changer la promesse, ou retirer l'option). **Mongazi a choisi de changer la
promesse et de la rendre vraie** : zéro geste de sa part, pour toujours.

### Ce que « vérifié » veut dire maintenant

Trois contrôles que la machine fait seule :

1. **Le numéro appartient à une tranche réellement attribuée par le
   régulateur.** Hors de ces tranches, la ligne ne peut pas exister.
   Sources vérifiées le 2026-08-04, pas supposées :
   - **Bénin** : ARCEP, réforme du 30/11/2024, 10 chiffres, préfixe `01`.
     MTN `0142 0146 0150-0154 0156-0157 0159 0161-0162 0166-0167 0169
     0190-0191 0196-0197` · Moov `0145 0155 0158 0160 0163-0165 0168 0194-0195
     0198-0199` · Celtiis `0120-0124 0128-0129 0140-0144 0147-0149 0192-0193`.
     ⚠️ Tout le bloc `012x` est accepté : les fixes historiques y vivent, et la
     source ne parlait que des mobiles. Mieux vaut garder un douteux que jeter
     un vrai fixe.
   - **Togo** : 8 chiffres, mobiles en `7x` et `9x`, fixes en `2x`.
   - **Côte d'Ivoire** : 10 chiffres depuis le 31/01/2021. Moov `01`/`21`,
     MTN `05`/`25`, Orange `07`/`27`.
2. **La fiche a été revue à sa source depuis moins de deux mois.**
3. **Aucun client ne l'a signalée injoignable** : le signal le plus fort, parce
   qu'un vrai humain a vraiment essayé.

Plus la garantie qui existait déjà et qui est ce que l'acheteur veut vraiment :
si ça ne répond pas, on remplace, gratuitement.

⚠️ **Aucune des trois ne prouve qu'on décrochera**, et rien dans le produit ne
doit le laisser croire. L'ancienne promesse survivait à **trois endroits**
(`prix.js`, la marche à suivre du cockpit, la page « d'où viennent les fiches »)
et dans l'e-mail de livraison qui demandait d'appeler chaque numéro.

**Chiffre honnête** : 7 809 fiches sur 7 817 passent déjà, parce que tout le
vivier a été relevé le même jour. Le tri prendra de la valeur avec le temps.

⏳ **Plus tard** : un vrai test réseau (requête opérateur, ~3 F par numéro
contre 60 F facturés) devient possible dès qu'un moyen de paiement
international existe. Mongazi : « garder ça en tête, on verra ».

### Le thème clair, par défaut

Mongazi travaille souvent dehors : **un écran sombre au soleil de Cotonou ne se
lit pas**. Le cockpit s'ouvre en clair, le sombre est à un bouton, le choix
reste dans l'appareil.

⚠️ **Deux palettes, pas une.** Un cyan néon lisible sur du noir devient
illisible sur du papier. Chaque couleur a sa version claire et sa version
sombre, et le contrôle vérifie le contraste **dans les deux**.

### Quatre vrais défauts trouvés en chemin

1. **L'onglet actif écrivait en sombre sur brique sombre, à 3,03:1.** Une
   correction faite pour le thème sombre s'appliquait aussi au clair.
2. **Une variable de Node référencée DANS le navigateur.** Le code passé à
   `page.evaluate` est sérialisé : il n'y voit rien de Node. Une capture
   montrait l'accueil en croyant montrer le cockpit ; un contrôle plantait.
   **Toujours passer la valeur en argument.** Rencontré deux fois en une heure.
3. **Le contrôle de contraste disait qu'un texte était illisible sans dire
   OÙ.** Il rend maintenant la couleur, le fond et la classe. *Un défaut qu'on
   ne peut pas localiser est un défaut qu'on ne corrige pas.*
4. **Trois contrôles ont accusé le calcul des prix alors que le prix était
   juste** : ils cliquaient sur un libellé écrit en dur, devenu obsolète. Ils
   le **lisent** désormais dans le module. C'est la troisième fois que ce piège
   se referme sur ce dépôt.

**175 contrôles verts** (91 + 39 + 25 + 20), zéro rouge.
