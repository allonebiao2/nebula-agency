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
