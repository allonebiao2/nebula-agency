# Leçons — Nebula Agency

> Ce qui a marché, ce qui n'a pas marché, ce qu'on refera ou évitera.
> Une leçon = un constat appuyé par une expérience concrète.

---

## Format

```
## YYYY-MM-DD — Titre court

- **Contexte** : sur quel projet / quelle tâche
- **Ce qui s'est passé** : observation factuelle
- **Leçon** : ce qu'on en retient
- **À appliquer** : comment ça change la pratique future
```

---

## Ce qui marche bien

> À compléter au fil des projets.

## Ce qui a posé problème

> À compléter au fil des projets.

---

## 2026-05-25 — Tester l'audio sur un vrai mobile, pas en émulation desktop

- **Contexte** : Luxury Club 229 — système audio Web Audio API (musique d'ambiance + SFX) testé sur desktop pendant le développement, validé OK. Gloria signale en production que ça ne fonctionne pas sur mobile.
- **Ce qui s'est passé** : Le pattern `ctx.resume()` au premier geste fonctionnait sur Chrome desktop mais pas sur iOS Safari (AudioContext reste en `suspended`). De plus, le gain master à 1.0 était audible sur laptop mais inaudible sur haut-parleur téléphone.
- **Leçon** : **L'émulation mobile dans les DevTools desktop ne reproduit pas le comportement audio réel d'iOS/Android.** Web Audio API a des quirks par plateforme (silent buffer unlock iOS, gain plus élevé pour les haut-parleurs téléphone, mode silencieux iOS qui bloque tout, sample rate mismatch).
- **À appliquer** :
  - Toujours tester l'audio sur un vrai téléphone (idéalement iPhone ET Android) avant de livrer.
  - Sur tout projet incluant Web Audio API : appliquer d'office le pattern silent buffer unlock + DynamicsCompressor + gain mobile boosté. C'est la baseline minimale viable mobile.
  - Documenter pour la cliente que le mode silencieux iOS bloque l'audio (limitation matérielle non-résoluble).
- Voir [[techniques-html#audio-mobile-fixes-spécifiques-ios-android-2026-05-25]] pour le code prêt à réutiliser.

---

## 2026-05-24 — Les images PNG « background removed » alourdissent et dégradent les vitrines

- **Contexte** : Luxury Club 229 — 33 photos produits INA Luxury embarquées en base64. Gloria n'aime pas le rendu : « les fonds blancs ont été très mal enlevés ».
- **Ce qui s'est passé** : Une étape précédente avait converti les JPEG originaux (fonds blancs propres, studio) en PNG transparents avec détourage automatique raté (halos, crops trop serrés). Résultat : `ina-luxury.html` faisait 12 Mo, les produits paraissaient minuscules dans des cartes pleines de vide, avec des artefacts de détourage visibles.
- **Leçon** : Sur une vitrine commerciale, **les fonds blancs studio sont un atout, pas un défaut**. Le détourage automatique (suppression de fond) génère des artefacts qui font perdre le côté pro des photos. Mieux vaut normaliser les images sur un canvas blanc commun (même dimensions) pour la cohérence visuelle.
- **À appliquer** :
  - Garder les JPEG originaux comme source de vérité dans `assets/images/`.
  - Pour normaliser visuellement la grille : pipeline canvas blanc + redimensionnement (script PowerShell GDI+ ou Python Pillow), aucun détourage. Le CSS card-photo passe en fond blanc + aspect ratio 3:4.
  - Si Gloria veut vraiment du PNG transparent, exiger une livraison de fichiers déjà détourés par elle (ou un pro) — pas d'auto-détourage.

## Un outil se teste sur DEUX écrans, sinon on livre des boutons inatteignables (2026-07-25)

- **Ce qui s'est passé** : après 89 vérifications vertes et plusieurs relectures, un **sweep
  automatisé mobile + PC** a révélé que le bouton « Nouvel article » du Catalogue était
  **hors de l'écran** (donc impossible d'ajouter un produit) et que l'Accueil débordait de 15 px.
- **Pourquoi on ne l'avait pas vu** : les captures d'écran étaient prises sur un seul format, et
  le bouton *existait* dans le DOM — les tests fonctionnels passaient donc parfaitement.
- **Leçon** : tester qu'un élément **existe** ne dit rien sur le fait qu'il soit **atteignable**.
  Mesurer les **positions réelles** (`getBoundingClientRect`) sur **chaque** écran et **chaque**
  format avant de crier victoire.
- **Application immédiate** : vaut aussi pour les **vitrines clients** (CTA WhatsApp sticky,
  bandeaux, pop-ups) — même cause, même effet.

---

<!-- Ajouter les nouvelles leçons au-dessus -->

## 2026-08-01 — Trois leçons de la direction artistique (HILLARY M. STYL v3)

**« Ça fait site à 100 $ » ne se répare pas en ajoutant des animations.**
Ça se répare en trouvant **une idée** dont tout découle. Ici : une maison de couture,
c'est un fil qui va du mètre-ruban au vêtement. À partir de là, chaque animation raconte
le métier — la piqûre, le patron à la craie, la coupe aux ciseaux — au lieu de décorer.
Et avant le mouvement viennent trois choses moins spectaculaires qui font 80 % de l'écart :
**la typographie** (un didone de mode à gros corps), **le rythme des fonds** (sombre,
clair, sombre — sans alternance tout se vaut), et **le vide** qu'on ose laisser.

**Un effet qui suppose une seule ligne de titre cassera sur mobile.**
La « coupe » découpait le titre à 50 % de sa hauteur et écartait les deux moitiés :
impeccable sur une ligne, bouillie sur deux. Refait en balayage horizontal, robuste
quel que soit le nombre de lignes. Règle générale : **tout procédé qui dépend d'une
hauteur de bloc connue est un bug qui attend un écran plus étroit.**

**Le `:hover` reste collé après un appui sur téléphone.**
Tout état de survol qui recouvre un contenu doit vivre dans
`@media (hover:hover) and (pointer:fine)`. Sinon la dernière carte touchée garde son
voile noir, et le client croit l'interface cassée.

**Corollaire de méthode :** ces trois défauts, plus trois autres, étaient invisibles à la
lecture du code. Ils se voient **en regardant les captures, écran par écran**. Le QC
automatique protège la logique ; il ne protège pas le goût.

## 2026-07-31 — Quatre leçons du moteur de commande couture (HILLARY M. STYL)

**Modéliser le métier du client, pas la catégorie qui nous vient à l'esprit.**
La v1 demandait « 8 mesures femme » ou « 8 mesures homme ». C'est un raisonnement de
développeur. Un couturier ne raisonne pas comme ça : **le genre du client ne détermine
rien, le vêtement détermine tout.** Une robe droite demande 15 mesures, un pantalon 6.
Avant de coder un formulaire métier, demander au client la liste exacte, par cas.
Et quand elle manque — la robe ovale — **ne pas l'inventer en silence** : proposer,
marquer « à valider » dans le code ET dans l'interface que le client final verra.

**Une promesse de délai s'annonce sur la borne haute, jamais sur la basse.**
Afficher le jour 8 d'un « 8 à 14 jours » fabrique un client déçu le jour 9. On promet 14,
on livre 10, le client est content. Même logique pour l'express : la vitrine dit que
l'atelier confirme, et que si la charge ne le permet pas, le supplément n'est pas dû.
Une vitrine qui ment sur un délai coûte plus cher qu'une vitrine sans délai.

**Un lien de texte est une cible ratée au pouce.**
Le QC a rejeté six éléments à 15, 23 et 41 px de haut : le logo de la barre, les liens de
navigation, le lien du pied. Tous parfaitement cliquables à la souris. `display:inline-flex`
+ `min-height:44px` règle le cas sans changer l'apparence. À vérifier sur **tous** les
`a`, pas seulement sur les boutons.

**Séparer la source du livrable dès qu'une image en base64 entre dans un fichier.**
75 Ko de logo en base64 rendent un HTML illisible et invitent à dupliquer l'image
(une première version pesait 681 Ko pour cette raison). Méthode : `_vitrine_src.html`
avec des marqueurs → `_build.py` qui injecte → `vitrine.html` généré, **jamais édité à la
main**. Plus `_qc.py` à côté, pour que le contrôle soit rejouable par n'importe qui.

## 2026-07-31 — Cinq leçons du chantier force de vente

**`main` bouge pendant qu'on travaille sur une branche.**
Avant de fusionner vers `main`, toujours `git merge origin/main` dans sa branche, puis
vérifier avec `git diff --stat origin/main..HEAD` que rien d'étranger au chantier
n'apparaît. Un merge naïf a failli annuler 2 621 lignes du module Boussole externalisé
entre-temps. Ce genre de dégât ne se voit qu'une semaine plus tard.

**Un seed n'est pas une migration.**
`seed_content()` ne s'exécute que sur une base vide. Modifier le code ne corrige jamais
la production. Il faut une fonction de migration idempotente, avec **un marqueur par
document**, sinon un élément reste en arrière et contredit les autres.

**Un catalogue commercial ne se dérive jamais d'une structure technique.**
`agency_brain()` construisait la liste des offres de NOVA à partir du dictionnaire
`SERVICES`, qui contenait encore la Fiche Google Maps et les Avatar IA, retirés du site
depuis la v9. NOVA récitait donc au public des offres qui n'existaient plus. Les offres
commerciales se figent explicitement là où on les annonce.

**Vérifier les chaînes couplées avant de toucher un prix.**
Sur `nebula_agency_v9.html`, les valeurs de `setTier('...')` doivent correspondre **au
caractère près** aux `<option>` du formulaire de commande. Un script qui compare les deux
ensembles évite une régression silencieuse du tunnel de commande.

**Tester avant de déployer attrape ce que la relecture ne voit pas.**
Trois bugs seraient partis en production : une colonne `a.numero` qui n'existe pas dans
`affiliates` (c'est `momo_number`) et qui aurait fait planter le cron à sa première
exécution six mois plus tard · `void_commissions()` qui annulait le récurrent acquis à
vie · un marqueur de migration manquant. Aucun n'était visible à la lecture du code.

## 2026-08-02 — hébergement, DNS et robots

- **Un déploiement Cloudflare Pages est un instantané complet.** Ce qui manque sur le disque
  disparaît du site. Lire `git status` avant tout `pages deploy .`, et se méfier des ` D `
  non stagés.
- **Déployer `.` publie aussi les notes internes.** Un `_dist` explicite est la seule façon
  de savoir ce qui part en ligne.
- **`REAL` en PostgreSQL fait 4 octets** et arrondit un horodatage Unix. En SQLite il en fait
  8. Toute date migrée doit passer en `double precision`.
- **Un point de contrôle d'hébergeur ne doit jamais dépendre de la base.** Sinon une base
  lente fait déclarer l'application morte et l'hébergeur cesse de lui envoyer des visiteurs.
  Il doit aussi répondre en **HEAD** : un 405 est lu comme une panne.
- **Toujours interroger l'origine avant d'accuser le proxy.** Un 404 sur un domaine relayé
  peut venir de l'origine, pas du relais.
- **525 puis 522 après correction du DNS** = le nom d'hôte manque côté Cloudflare Pages.
- **Cloudflare bloque les robots des IA par défaut** depuis le 1er juillet 2025, et le
  réglage `ai_bots_protection` n'apparaît nulle part dans le tableau de bord.
- **Cloudflare renvoie 403 aux clients d'API sans en-tête de navigateur.**
- **Sur une page à images base64, tout `grep` ment** tant qu'on n'a pas neutralisé les
  données : c'est ainsi qu'on croit à tort qu'une section existe.
- **Ne pas conclure sur une seule mesure** : un timeout curl, une propagation en cours ou un
  308 non suivi fabriquent de faux diagnostics.
- **Une apostrophe française non échappée casse tout un bloc `<script>`.** `text: '… et
  l'alerte.'` ferme la chaîne et rend muettes toutes les lignes qui suivent. `node --check`
  sur le FICHIER ne la voit pas : il faut vérifier **chaque bloc inline séparément**. Le
  remède est aussi le plus juste typographiquement : l'apostrophe courbe.
- **Corriger la mesure avant de corriger le design.** Une sonde de contraste qui lit
  `rgba(255,255,255,.04)` comme du blanc, au lieu de le fondre sur le fond, invente des
  « textes pâles » qui n'existent pas. Composer les fonds translucides, et ignorer les
  textes en dégradé où il n'y a rien à mesurer.
- **Isoler avant d'optimiser.** Retirer une chose à la fois et remesurer désigne le vrai
  coupable : sur les back-offices, les flous d'arrière-plan et 2 animations coûtaient 25
  images sur 60, et les ombres **rien du tout**.
- **Un banc de mesure chargé ment.** La même page mesurait 60 images/s puis 14 selon ce qui
  tournait à côté. Comparer seulement des mesures prises **d'une traite**, et se méfier des
  chiffres absolus.

## 2026-08-03 — Quatre leçons des back-offices sur Postgres

### 1. Ce qui était gratuit sur SQLite coûte 1,3 s sur Supabase

Ouvrir une connexion coûtait une microseconde en local ; le code appelait donc
`db()` librement, y compris dans des fonctions imbriquées. Après la migration,
un écran ouvrait **neuf connexions** et mettait douze secondes : l'écran restait
noir. **Après un changement de base, il ne faut pas relire les requêtes, il faut
compter les CONNEXIONS.**

Le remède qui répare tout d'un coup : **une connexion par requête HTTP**, tenue
dans un `ContextVar` (pas un thread-local : Starlette exécute le synchrone dans
un autre fil, mais il recopie le contexte). Corriger les douze appels un par un
aurait été long et risqué.

### 2. Réparer la performance peut réveiller un bug endormi

Aussitôt la connexion réutilisée : `DuplicatePreparedStatement "_pg3_0"`.
psycopg3 prépare une requête après 5 exécutions ; le pooler Supabase multiplexe
et la requête préparée n'existe plus sur le serveur suivant.
**`prepare_threshold = None` est obligatoire avec le pooler**, y compris dans le
moindre script d'administration.

Le bug était invisible tant qu'on ouvrait une connexion par appel. **Un correctif
de performance change les conditions d'exécution : il faut retester ce qui
marchait, pas seulement ce qu'on répare.**

### 3. Sur un hébergement sans disque, ce qui n'est pas en base n'existe pas

Render efface le disque à chaque déploiement. Trois choses écrivaient dessus sans
qu'on s'en rende compte : les photos de profil, les PDF envoyés depuis le
cockpit, et les PDF publiés automatiquement. Tout était référencé en base et
introuvable à l'ouverture. **Tout ce qui doit survivre va en base, en base64.**

### 4. Vider une table ne suffit pas quand le code la resème

La zone Documents avait **trois** mécanismes qui recréaient les mêmes entrées à
chaque démarrage, dont un qui les réécrivait systématiquement. Supprimer les
lignes n'aurait rien changé : elles seraient revenues au redémarrage suivant.

**Avant de supprimer des données, chercher qui les fabrique.** Et remplacer les
mécanismes concurrents par **un seul**, idempotent, qui sait distinguer ce qu'il
a posé lui-même de ce qu'un humain a ajouté.

### Bonus, sur l'outillage

- Une expression régulière avec `re.S` et `(?:#.*
)*` part en boucle : le `.`
  mange les retours à la ligne. Sur un fichier de 2 500 lignes, ça bloque la
  session. **Découper un fichier se fait par LIGNES, pas par regex gloutonne.**
- Une marche arrière « tant que la ligne est indentée » avale la fonction du
  dessus. Elle a failli supprimer `seed_content()` en silence ; seule une
  assertion posée **avant** l'écriture l'a évité. **Toujours vérifier avant
  d'écrire, jamais après.**
- Un chemin d'exécutable écrit en dur (`/opt/pw-browsers/…`) rend un script
  inutilisable dès qu'on change de machine. **On cherche l'outil, on ne le
  suppose pas.**

## 2026-08-04 — Cloudflare peut mettre une ERREUR en cache pour un an

PISTE est apparu entièrement sans style : texte noir sur blanc, police par
défaut, un aplat noir géant à la place du décor. La feuille de style répondait
pourtant **200, avec le bon type et la bonne taille**. Son contenu, lui, était
`error code: 502`.

Pendant un déploiement, Cloudflare a reçu un 502 passager de l'origine et l'a
mis en cache **à la place du fichier**. Or les fichiers compilés portent
`Cache-Control: immutable, max-age=31536000` — parfaitement correct pour un nom
qui contient une empreinte de contenu, mais fatal ici : l'erreur restait servie
pendant un an.

**Le piège qui empêchait de réparer.** Vite nomme les fichiers d'après leur
CONTENU. Reconstruire à l'identique redonnait exactement les mêmes noms, donc
les mêmes adresses empoisonnées. Le site ne pouvait pas se réparer tout seul,
et redéployer ne changeait rien.

**Ce qu'il faut retenir.**

1. **Un 200 ne prouve rien.** Il faut regarder le CORPS. `curl -sI` disait
   `Content-Type: text/css`, taille correcte, `cf-cache-status: HIT`. Seul
   `curl -s ... | head -c 200` a montré l'erreur.
2. **Comparer l'origine et le domaine.** `piste-uex.pages.dev` servait le bon
   fichier pendant que `piste.nebula-agency.online` servait l'erreur : ça
   désigne le cache en trois secondes.
3. **Le remède permanent** : une marque de déploiement dans le nom des fichiers
   (`index-2608041417-D5MeerQ9.css`). Chaque publication produit des adresses
   neuves, et une erreur en cache ne survit plus à un déploiement. Le coût est
   un chargement de plus pour un visiteur déjà venu.
4. ✅ **Le bouton de secours existe depuis le 2026-08-04** :
   `python scripts/purger.py` vide le cache des cinq hôtes du parc, et
   `--verifier` regarde le CORPS des fichiers servis sans rien purger.
   Il s'appuie sur `CLOUDFLARE_PURGE_TOKEN` dans `secrets/cloudflare-zone.env`.
   ⚠️ Le jeton de zone qui existait avant ne suffisait pas : il sait LIRE la
   zone, pas la purger. Il faut la permission `Zone · Cache Purge · Purge`.
5. ⚠️ **Cloudflare renvoie 403 à un script qui ne se présente pas comme un
   navigateur.** Un contrôle automatique doit envoyer un vrai `User-Agent`,
   sinon il croit le site cassé alors que le visiteur, lui, le voit bien.

Vaut pour **tous les sites du parc** : les douze vitrines sont sur Cloudflare
Pages et peuvent subir exactement la même panne.

### La même panne, une deuxième fois le même jour — et cette fois c'est l'outil de contrôle qui l'a causée

Quelques heures plus tard, PISTE est réapparu sans style. Même symptôme, cause
différente, et bien plus instructive.

**Deux défauts se combinaient.**

1. **Un fichier absent répondait `200` avec du HTML.** Cloudflare Pages sert la
   page d'accueil pour toute adresse inconnue dès qu'il n'y a pas de
   `404.html` : c'est la bascule « application d'une seule page », activée
   toute seule.
2. **`/assets/*` porte `Cache-Control: immutable, max-age=31536000`.** Cette
   règle s'applique à ce qui est SERVI sous ce chemin, pas au fichier qu'on
   croyait y mettre. Le HTML de repli héritait donc d'un an de cache.

**Et le déclencheur, c'est `purger.py --verifier`, lancé dans la seconde qui
suivait le déploiement.** La propagation n'était pas finie, le fichier
n'existait pas encore partout, la vérification a reçu la page de repli, et
Cloudflare l'a écrite dans le cache **à la place du CSS**.

> **Vérifier à travers un cache n'est pas un geste neutre : la réponse obtenue
> est écrite dans le cache. Une vérification trop tôt fabrique la panne qu'elle
> cherche.**

**Les deux remèdes, tous deux posés.**

- **Un `404.html` dans `public/`.** Une adresse inconnue répond enfin un vrai
  404, et un 404 ne se fait pas mettre en cache comme une ressource permanente.
  ⚠️ **À poser sur chaque nouveau site du parc.** PISTE n'avait de toute façon
  aucun besoin de la bascule SPA : ses routes sont toutes après un dièse
  (`#/carnet`, `#/cockpit`), elles ne touchent jamais le serveur.
- **L'ordre de vérification, écrit en tête de `purger.py`** : déployer →
  vérifier **l'URL du déploiement** (`xxxx.piste-uex.pages.dev`, qui ne passe
  par aucun cache) → purger → attendre ~45 s → vérifier le domaine.

`--verifier` lit désormais `cf-cache-status` et tranche tout seul : `HIT` sur
du HTML = le cache tient une mauvaise copie, une purge suffit. `MISS` = c'est
l'origine qui est cassée, purger n'y changera rien.

## 2026-08-04 — Le « 01 » béninois n'est pas un préfixe à retirer

Une candidature arrive avec le numéro `0162178411`. Le bouton WhatsApp du
cockpit ouvre `+229162178411`. WhatsApp répond : **« ce numéro n'est pas sur
WhatsApp »**, devant le candidat.

**La cause.** `waLink()` faisait `replace(/^0+/, '')`. C'est le réflexe correct
dans la plupart des pays, où le zéro de tête est un préfixe national. **Au
Bénin, depuis la réforme ARCEP du 30 novembre 2024, le `01` fait partie du
numéro.** La forme internationale est `229` + le numéro entier, zéro compris.

**Le vrai problème, plus profond.** Deux formes coexistent : 8 chiffres
(l'ancienne) et 10 chiffres avec le `01`. Un compte WhatsApp peut être resté
sur l'ancienne. Et **les gens donnent souvent celle que leur compte ne porte
pas, sans le savoir** : ils ne mentent pas, ils l'ignorent.

**On ne peut donc pas deviner.** Toute interface qui ouvre une conversation
WhatsApp doit proposer **l'autre forme** en second bouton, dans les deux sens.

**Ce qu'il faut retenir.**

1. **Un réflexe universel n'est pas une règle locale.** Retirer le zéro de tête
   est juste presque partout, et faux ici.
2. **Accepter 8 OU 10, refuser 9.** Un numéro à 9 chiffres est une faute de
   frappe. Et le message d'erreur doit dire **combien de chiffres ont été
   tapés**, jamais « numéro invalide ».
3. ⚠️ **Le Mobile Money fait toujours 10 chiffres**, mais on ne le complète
   JAMAIS en silence : on compte, on dit ce qui manque, on laisse corriger.
4. `phone_key()` de `server.py` a le droit de retirer les zéros : elle
   **compare** des numéros, elle n'en compose pas.

Détail complet : mémoire Claude `reference_numeros-benin`.


---

## Une image générée ne devient jamais le catalogue d'un client

*2026-08-05, en illustrant le portfolio d'Angy Art.*

On sait générer des visuels superbes pour 0,14 $ pièce. C'est une tentation nouvelle,
et elle a un bord tranchant.

**Ce qui est autorisé** : l'ambiance, la matière, le lieu, la texture, le geste. Un
atelier, des mains dans le pigment, un mur en fin de journée. Personne ne peut écrire
« je veux acheter celle-là ».

**Ce qui ne l'est jamais** : une pièce présentée comme vendable. Un collectionneur qui
écrit pour acquérir une toile qui n'existe pas, ce n'est pas nous qui répondons, c'est
l'artiste. Et elle perd le client, et sa parole avec.

**Entre les deux, une zone qu'il faut baliser explicitement.** Chez Angy Art, huit
visuels occupent le carrousel en attendant les vraies photos. Ce qui les rend tenables :

1. **Aucun prix, aucune dimension, aucune mention « disponible ».** Un titre et une
   technique décrivent ; un prix engage.
2. **Le `CONTEXT.md` le dit noir sur blanc**, et le commentaire est en tête du tableau
   dans le code, là où quelqu'un le lira forcément.
3. **Le message pour obtenir les vraies photos est déjà écrit** et prêt à envoyer.
   Une préfiguration n'est acceptable que si le chemin pour en sortir est posé.

Le test : *si le client recevait un message d'achat demain, pourrait-il répondre sans
mentir ?* Si non, l'image n'a rien à faire là.

---

## Un rectangle blanc n'est pas une photo détourée, et un contrôle vert ne le sait pas

*2026-08-06, sur la vitrine d'Hillary M. Styl.*

Le héros de la V4 est bâti sur un effet précis : un chiffre géant passe **derrière**
la silhouette, et le nom de la maison la chevauche. Les photos étaient des rectangles
de studio, fond blanc compris. Le chiffre était donc entièrement couvert : l'effet
n'existait pas, et 74 contrôles étaient verts pendant ce temps.

**Ce que le contrôle ne pouvait pas voir**, il faut le lui apprendre. Trois contrôles
ajoutés, et la même famille de défaut ne peut plus revenir :

1. les images concernées **portent un canal alpha réellement transparent** — lu au
   pixel, jamais déduit du nom du fichier ;
2. **aucun fond opaque ni bordure** sur les conteneurs qui les portent ;
3. **prix et délais tiennent sur une seule ligne** — un `Range` DOM qui renvoie
   plusieurs rectangles trahit un retour à la ligne, et « 100 000 » / « F » sur deux
   lignes fait une carte cassée.

### La transparence n'oblige pas au PNG

Demandé en PNG, livré en WebP, et c'est mieux :

| PNG | WebP sans perte | **WebP `quality=94, alpha_quality=100, exact=True`** |
|---|---|---|
| 3 560 Ko | 2 426 Ko | **761 Ko, écart alpha maximum 0** |

Le canal alpha est **bit pour bit celui du PNG**, pour 4,7 fois moins lourd. À
Cotonou, en 4G, ces 2,8 Mo décident si la page s'affiche. Garder les PNG sources
pour pouvoir revenir en arrière, et le dire au client plutôt que de livrer en
silence autre chose que ce qu'il a demandé.

### Un poids annoncé ne prouve rien, seule l'empreinte prouve

`curl -w "%{size_download}"` a annoncé 124 Ko pour un fichier de 194 Ko et fait croire
à un cache empoisonné. Le fichier servi, téléchargé et comparé en **MD5**, était
identique à celui du disque. **Comparer les octets, pas les compteurs.**

### Une page 404 sur chaque site, sans exception

Sans `404.html`, Cloudflare Pages répond `200` avec le HTML d'accueil pour un fichier
absent — et ce `200` hérite du cache `immutable` d'un an. C'est la panne de PISTE du
2026-08-04. `_predeploy.py` l'écrit désormais tout seul. À reprendre sur le parc.

---

## Une courbe qui part à plat se lit comme un bug

*2026-08-06, sur le héros d'Hillary. Mongazi : « ça bugue un peu, surtout sur les
chiffres, ça doit suivre ».*

`cubic-bezier(.45,.02,.2,1)` a l'air d'un beau easing sur le papier. Avec un point
de contrôle à `y = .02`, **il ne se passe presque rien pendant le premier tiers** :
mesuré, la pièce restait immobile **580 ms après le clic**, puis se précipitait.
Personne ne dit « ton easing est mal choisi » : on dit « ça bugue ».

Un ease-out qui bouge dès la première image (`cubic-bezier(.25,1,.5,1)`) règle
tout. **Vérifier le début de la courbe, pas seulement sa fin.**

### Ce qui accompagne un mouvement ne doit pas le porter

Fabriquer un glyphe de 30 rem coûte un calcul de mise en page. Poser une variable
CSS sur `:root` coûte un recalcul de tout le document. Faire ces deux choses
**avant** de changer les classes qui lancent la transition, c'est retarder le
départ de ce qu'on veut voir bouger.

L'ordre qui marche : préparer hors du chemin critique → **lancer le mouvement et
tout ce qui doit être en phase dans la MÊME image** → la couleur et les textes à
l'image suivante.

### Deux horloges pour un seul geste, c'est une horloge de trop

Le chiffre géant roulait 240 ms puis se remplaçait d'un coup, pendant que la pièce
glissait 1,15 s. Deux éléments d'un même geste doivent partager **la durée ET la
courbe**, sinon l'œil voit un raté même sans savoir le nommer.

### Deux minuteurs qui tombent à la même milliseconde, c'est une course

Le verrou de la transition et le retrait de l'ancien chiffre étaient tous deux à
1050 ms. Selon lequel gagnait, un chiffre restait empilé (« 0302 ») quand on
cliquait vite. Règle : **seule l'opération la plus récente fait le ménage**, et
elle le fait complètement (`if (conteneur.lastElementChild !== moi) return;`).

### Un contrôle ne doit pas regarder à un instant fixe

La première version du contrôle échantillonnait à 420 ms et tombait pendant un
défilement automatique qui avait avalé le clic : elle criait au bug sur du code
juste. Elle échantillonne maintenant **tout le mouvement**, et reclique si rien
n'a bougé. Et elle n'exige pas de voir une valeur précise : une courbe rapide
peut passer entre deux images d'un rendu lent sans que rien ne cloche.

### Un aplat de couleur à faible opacité doit se mélanger en oklab

`color-mix(in srgb, <bleu> 22%, transparent)` sur du papier crème donne un **voile
gris sale**. `in oklab` garde la teinte. Quand une couleur doit se *voir* comme
une couleur, ne pas la mélanger en srgb.

---

## Une page dont TOUT est construit par le script ne marche pas pour tout le monde

*2026-08-06, Mongazi : « la page ne marche pas sur mon téléphone ».*

Le héros et le catalogue d'Hillary étaient entièrement injectés par le
JavaScript. Sans lui : une page rose, un chiffre géant, le nom de la maison, et
**aucun vêtement**. Le visiteur ne dit pas « le script n'a pas tourné », il dit
« ça ne marche pas ».

Ça arrive pour de vrai chez nous : **Opera Mini en mode économie** (rendu côté
serveur, script fortement limité), les modes « Lite » d'Android, un réseau qui
coupe pendant le chargement du script.

**Règle : ce qui prouve que le site existe doit être dans le HTML.** Une vraie
photo, un vrai nom, un vrai texte, un vrai numéro de téléphone. Le script
enrichit, il ne fonde pas. Bénéfice en prime : le navigateur découvre l'image en
lisant la page, au lieu d'attendre que le script tourne.

**Contrôle à ajouter partout** : un contexte Playwright avec
`java_script_enabled=False`, et on vérifie qu'il reste une photo et un texte.

### Charger quatre images d'un coup, c'est quatre images lentes

Sur une 4G à 1,6 Mb/s, lancer les quatre mannequins du héros ensemble donne
quatre pièces lentes au lieu d'une rapide. La première part **seule** (avec un
`<link rel="preload" as="image">` dans le `<head>`, parce qu'une image injectée
par le script est invisible au préchargeur du navigateur), les autres suivent
**une par une** quand elle est peinte, et un clic anticipé les réclame.

### ⚠️ Ne jamais mesurer une performance avec sa propre boucle

`page.wait_for_function` de Playwright sonde en `requestAnimationFrame`. Sous
4× de ralentissement processeur, les rAF sont affamés : il a annoncé « première
pièce à 9,3 s » alors que la chronologie réseau montrait l'image **reçue à
2,6 s**. J'ai optimisé pendant une heure d'après un chiffre faux.

Lire les **vraies métriques du navigateur** : `performance.getEntriesByType`
(`navigation`, `resource`) et un `PerformanceObserver` sur
`largest-contentful-paint`. Et ne jamais comparer un `file://` (sans
compression) à une URL en ligne.

### Compresser une image détourée : l'alpha reste sans perte, le RVB non

`quality=84, alpha_quality=100, exact=True` : **écart alpha 0** (bit pour bit,
donc aucun halo au contour) et écart RVB moyen de 3 sur 255, invisible sur une
photo, pour **moitié moins d'octets**. Script réutilisable :
`clients/10-hillary-m-styl/_alleger.py`.

---

## Un contact faux est pire que pas de contact

*2026-08-06, audit de la vitrine d'Hillary.*

Une adresse email inventée, `contact@hillarymstyl.com`, était **affichée sur le
site en ligne** et servait de destination réelle au lien « je n'ai pas WhatsApp »
de la dernière étape du tunnel de commande. Une cliente sans WhatsApp envoyait sa
commande **dans le vide**, et ni elle ni la maison ne pouvaient le savoir.

Le code portait `/* ⚠ À REMPLACER */` depuis le premier jour. **Un avertissement
dans le code n'a jamais empêché un déploiement.**

**La règle** : une coordonnée qu'on n'a pas ne s'invente pas, elle **disparaît**.
Le champ reste vide, la ligne se retire toute seule, et le repli bascule sur un
canal réel (ici un `tel:` vers son vrai numéro). Le jour où le client donne la
vraie valeur, on l'écrit à un seul endroit et tout revient.

**Le contrôle qui va avec** : aucune adresse email affichée sur la page qui ne
soit celle configurée, et le lien de repli doit mener quelque part de réel —
sans jamais recopier « mailto: » dans le contrôle, sinon il empêche la
correction.

### Deux chiffres différents sur la même page, c'est le client qui choisit

Le bloc contact annonçait « 7 à 14 jours · 1 à 3 jours en express » quand chaque
carte du catalogue disait « 14 jours » et « 2 à 5 jours ». Un délai vit à
**plusieurs endroits** : la carte, la fiche, le bloc contact, le badge du héros,
et les valeurs de secours du moteur. Un contrôle doit **comparer les endroits
entre eux**, pas vérifier un chiffre écrit à la main.

### Un sélecteur de type attrape le voisin, et la spécificité ne prévient pas

`.et span{grid-column:2}` frappait aussi le numéro, un `<span class="n">` : le
titre passait dans la colonne de 86 px du numéro et « L'essayage » chevauchait le
« 04 ». `.et .n` (0-2-0) l'emporte pourtant sur `.et span` (0-1-1) — mais
seulement pour ce qu'il **déclare**, et `grid-column` n'y était pas.
Écrire `.et>span:not(.n)`.

### Un fondu de navigation peut rendre le menu invisible

La barre croisait sa couleur de texte (0,4 s) et son fond (0,5 s) : à mi-chemin
les deux valaient le même gris, **1,01:1 mesuré**. Quand deux propriétés
opposées se croisent, les faire **courtes et ensemble** (0,22 s) : la zone
trouble dure 100 ms au lieu d'un demi-tour d'horloge.

### La marque WhatsApp n'est pas faite pour du texte blanc

`#25D366` et `#1EA855` portent du texte **foncé**. En blanc dessus on tombe à
**3,09:1**. Pour un bouton vert à texte blanc : `#128040` (5,0:1).


## 2026-08-10 — Un son généré se MESURE, il ne s'écoute pas de confiance

- **Contexte** : les huit ambiances de Mon Bénin, générées avec WaveSpeed.
- **Ce qui s'est passé** : les huit fichiers pesaient **exactement 64 592
  octets**. C'est normal en MP3 à débit constant et durée égale, mais ça ne
  prouve rien : on aurait pu me renvoyer huit fois le même son. Comparés par
  **MD5 et profil spectral par bandes**, ils étaient bien différents, et leurs
  profils correspondaient aux textes. En revanche leurs **niveaux** avaient un
  **facteur 15** d'écart : le voyage serait passé du quasi-silence au fort.
- **Leçon** : trois contrôles obligatoires sur tout son généré, dans cet ordre :
  **différence réelle** (MD5 + spectre), **raccord de boucle** (moyenne des 40
  premières ms contre les 40 dernières), **niveaux** (`loudnorm=I=-20`).
- **À appliquer** : ne jamais livrer un son généré sans ces trois mesures. Et
  garder les originaux : régénérer coûte de l'argent.

## 2026-08-10 — Un élément fixe finit toujours par recouvrir du contenu

- **Contexte** : l'anneau des kilomètres de Mon Bénin.
- **Ce qui s'est passé** : réserver une marge en bas de section ne suffisait
  pas. Un `position: fixed` est ancré au **viewport**, pas à la section : dès
  qu'une section dépasse la hauteur d'écran, du contenu passe dessous. L'anneau
  s'est posé sur l'avertissement de la Pendjari, sur le curseur de Ganvié, sur
  « Les greniers » et sur le bouton WhatsApp.
- **Leçon** : **un instrument flottant ne recouvre jamais du texte. Seules les
  bandes de bord en ont le droit, et alors elles doivent être vraiment
  opaques.**
- **À appliquer** : décaler l'instrument du côté opposé au contenu, ou le
  transformer en bande de bord au téléphone. Et vérifier l'opacité en
  **photographiant**, jamais en lisant une chaîne CSS : `getComputedStyle` d'un
  dégradé renvoie une forme imprévisible et le contrôle passe pour de mauvaises
  raisons.

## 2026-08-10 — Une police distante casse la promesse de vitesse

- **Contexte** : Mon Bénin chargeait Fraunces depuis Google Fonts.
- **Ce qui s'est passé** : le test s'est **bloqué** dessus, et le réseau a mis
  plus de deux minutes à répondre. Le site promettait « 3 secondes en 3G ».
- **Leçon** : une dépendance à un tiers dans le chemin critique annule la
  promesse de performance, quelle que soit la qualité du reste.
- **À appliquer** : polices servies depuis notre domaine, `font-display: swap`,
  et **un contrôle automatique qui échoue si une requête sort du site**. Le
  dépôt contient déjà Bodoni Moda, Archivo, Manrope, Bricolage Grotesque et
  Plex Mono en woff2 : les reprendre plutôt que d'en charger de nouvelles.

## 2026-08-10 — L'alias d'un déploiement Cloudflare Pages a du retard

- **Contexte** : trois publications successives de Mon Bénin.
- **Ce qui s'est passé** : `dev.<projet>.pages.dev` servait encore l'ancienne
  version quelques secondes après la fin du déploiement, alors que l'URL
  immuable (`<hash>.<projet>.pages.dev`) servait déjà la nouvelle. Ça a fait
  conclure deux fois à une publication ratée, dont un faux 404 sur les sons.
- **Leçon** : après un déploiement, **vérifier sur l'URL immuable**, ou attendre.
  Comparer les deux désigne le problème en trois secondes.
- **À appliquer** : dans tout script de vérification, interroger l'URL immuable
  renvoyée par wrangler, pas seulement l'alias.

## 2026-08-10 — Le disque plein se déguise en panne de réseau

- **Contexte** : l'installation de wrangler puis le démarrage du navigateur de
  test échouaient, avec des délais dépassés.
- **Ce qui s'est passé** : le disque était à **0 octet libre sur 271 Go**.
  L'erreur visible était `ENOSPC` noyée dans des avertissements npm, puis un
  simple délai dépassé au lancement du navigateur.
- **Leçon** : devant une lenteur ou un délai dépassé inexplicable sur cette
  machine, **regarder l'espace disque avant le réseau**.
- **À appliquer** : `df -h /c`. Récupérable sans risque : le cache npm, les
  profils Playwright abandonnés dans `%TEMP%`, les paquets d'une installation
  ratée. ⚠️ **Ne pas vider `%TEMP%` en entier** : Claude Code y écrit ses
  propres fichiers de travail et supprime sa sortie en cours.

## 2026-08-16 — Le voile qui avale les clics après sa fermeture

- **Contexte** : le tiroir du panier d'Hillary se fermait, et pendant un instant
  la fiche ouverte derrière ne répondait plus.
- **Ce qui s'est passé** : le voile portait
  `transition: opacity .35s, visibility .35s`. **`visibility` ne se dégrade pas
  en douceur : elle bascule à la FIN de la transition.** Le voile était donc
  invisible mais toujours là, et il interceptait tout pendant 350 ms.
- **Leçon** : sur tout voile, tiroir ou modale qu'on fait disparaître,
  **`pointer-events` est ce qui décide**, pas `opacity` ni `visibility`.
- **À appliquer** : `pointer-events:none` à l'état fermé, `auto` à l'état
  ouvert. Et le contrôle qui le trouve n'est pas un contrôle de style : c'est un
  clic qui échoue, avec « intercepts pointer events » dans le journal.

## 2026-08-16 — Le défaut le plus cher est invisible depuis le site

- **Contexte** : audit de la vitrine Hillary avant de « rendre tout parfait ».
- **Ce qui s'est passé** : le site n'avait **aucune `og:image`**. Au Bénin, un
  lien se partage sur WhatsApp : la maison apparaissait comme une ligne de texte
  grise, à côté de liens qui montrent une photo. Personne ne pouvait le voir en
  regardant le site, et ça durait depuis la mise en ligne.
- **Leçon** : une vitrine ne se juge pas seulement à l'écran. **Elle se juge
  aussi dans une conversation WhatsApp, dans un résultat Google et dans un
  aperçu de partage.** Ce sont trois surfaces qu'aucune capture ne montre.
- **À appliquer** : à chaque livraison, vérifier `og:image` (**en JPEG**,
  l'aperçu WhatsApp ne lit pas toujours le WebP), `twitter:card`, `robots.txt`,
  `sitemap.xml`, et une page `404`. ⚠️ Vérifier aussi que le script de
  déploiement **copie vraiment** ces fichiers : celui d'Hillary ne copiait que
  les `.webp`, et l'image de partage restait sur le disque.

## 2026-08-16 — Des données structurées qui promettent ce que la page ne montre pas

- **Contexte** : la page déclarait un `FAQPage` à Google.
- **Ce qui s'est passé** : **aucune question n'était visible sur la page.**
  C'est contraire aux règles de Google (le contenu balisé doit être visible), et
  surtout les objections des clientes n'étaient répondues nulle part. Les
  réponses cachées annonçaient même un délai que le catalogue contredisait.
- **Leçon** : un balisage n'est pas une déclaration d'intention. **Ce qu'il
  annonce doit exister à l'écran, mot pour mot.**
- **À appliquer** : quand on balise une FAQ, un produit ou un prix, **le lire
  dans les données du site** au lieu de le recopier, et poser un contrôle qui
  compare le balisage et la page. Chez Hillary, les fiches produit sont
  extraites du catalogue par l'assembleur, et un contrôle compare les questions
  une par une.

## 2026-08-17 — Quand la porte échoue, ce qu'on publie est l'ancienne version

- **Contexte** : le pré-déploiement d'Hillary a signalé un contrôle rouge, et
  le déploiement est parti quand même (des commandes enchaînées par `&&`).
- **Ce qui s'est passé** : `_predeploy.py` s'arrête **avant** de préparer
  `_dist/`. Le dossier contenait donc encore la version précédente, et
  `wrangler` l'a publiée **sans le moindre message d'erreur**. Le site est parti
  avec la nouvelle FAQ mais sans le nouveau héros. Vu en vérifiant en ligne.
- **Leçon** : un contrôle qui échoue ne laisse pas le livrable en l'état, il le
  laisse **périmé**. Et un déploiement réussi ne prouve rien sur ce qui a été
  déployé.
- **À appliquer** : ne jamais enchaîner « contrôle && déploiement » sans lire la
  sortie du contrôle, et **vérifier en ligne un élément que la nouvelle version
  est seule à porter** (ici : le nombre de diapositives du héros).

## 2026-08-17 — Un contrôle qui échoue au hasard accuse le site à tort

- **Contexte** : la suite d'Hillary tombait une fois sur deux sur
  « Page.goto: Timeout », ce qui ressemble à une panne du site.
- **Ce qui s'est passé** : le petit serveur HTTP du contrôle était
  **`socketserver.TCPServer`, mono-tâche**. Le navigateur ouvre plusieurs
  connexions et les garde ouvertes : l'une bloquait toutes les autres. Tant que
  la page ne demandait qu'une poignée de fichiers ça passait ; avec **28
  images**, elle a commencé à ne plus se charger dans le temps imparti.
  ⚠️ J'ai d'abord soupçonné Google Fonts et corrigé à côté : la panne est
  revenue au passage suivant.
- **Leçon** : devant un contrôle intermittent, **regarder d'abord l'instrument**,
  pas le site. Un contrôle qui échoue au hasard est pire qu'un contrôle absent :
  on finit par le croire, ou pire, par ne plus le croire du tout.
- **À appliquer** : `ThreadingTCPServer` (avec `daemon_threads`) dans toute
  suite qui sert un site à un vrai navigateur. Et confirmer une correction
  d'intermittence par **plusieurs passages d'affilée**, jamais un seul.


## 2026-08-18 — Une image dans une conversation n'est pas un fichier, et ça dépend d'OÙ tourne la session

- **Contexte** : Mongazi envoie onze modèles en photo depuis son téléphone et
  demande quatre fois de les mettre en ligne. Il est certain que ça marchait
  avant, « au même endroit ».
- **Ce qui s'est passé** : il avait raison, et la vérification l'a prouvé. Les
  photos des lots précédents sont **sur le disque** alors que git ne les suit
  pas (`_sources/` est ignoré), et le lot du 10 août a livré **les images
  finies sans aucune source** — or l'outil de détourage ne sait lire que des
  fichiers. Donc cette session-là **avait les fichiers**.
  **Une session lancée depuis le téléphone tourne dans le nuage : les pièces
  jointes y arrivent comme de vrais fichiers.** Une session qui tourne sur le PC
  voit l'image sans pouvoir l'écrire nulle part.
- **Leçon** : ne jamais dire « c'est impossible » quand l'utilisateur affirme
  que ça marchait. **Aller chercher la trace** (git, dates, ce qu'un outil exige
  pour fonctionner) : elle dit ce qui s'est réellement passé, et souvent il a
  raison sur le fait, pas sur la cause.
- **À appliquer** : quand des photos manquent, deux voies au lieu d'une :
  refaire la manipulation **depuis le téléphone** (la session du nuage sait
  écrire les fichiers), ou un **lien** que je télécharge. ⚠️ Une session du
  téléphone travaille sur une branche `claude/…` qui ne rejoint jamais `main`
  toute seule.

## 2026-08-18 — Un catalogue peut vivre sans photos, à condition de ne pas mentir

- **Contexte** : onze pièces réelles, prix réels, aucune photo. Mongazi tranche :
  « mets-les déjà sur la vitrine ».
- **Ce qui a été fait** : les fiches sont complètes (nom, description, prix en
  trois monnaies, délai, mesures) et **commandables de bout en bout**. À la
  place de l'image : le monogramme et **« Photo sur WhatsApp »**.
- **Leçon** : entre un placeholder qui s'excuse (« photo à venir », qui dit que
  la maison n'est pas prête) et une absence, il existe une troisième voie :
  **une phrase vraie et actionnable**, qui envoie le client là où il achète.
- **À appliquer** : ⚠️ ces pièces n'entrent **ni au héros ni au carrousel** —
  ces surfaces vivent de la photo. Et ce n'est pas un état final : un drapeau
  (`photoWa`) marque les fiches, et l'outil qui posera les images le retirera.

## 2026-08-19 — Un contrôle faux coûte plus cher qu'un contrôle absent

- **Contexte** : mesure du contraste de la pastille de prix d'Au Braisé d'Or,
  posée sur les photos de plats. La méthode d'Angy Art dit, à juste titre, que
  lire `background-color` est aveugle au-dessus d'une photo : il faut
  photographier et **prendre le décile le plus clair** pour le texte.
- **Ce qui s'est passé** : la mesure annonçait **2,15:1** sur une pastille
  **parfaitement nette**, vérifiée ensuite à l'œil sur une capture agrandie de
  la seule pastille. Corriger l'animation, le serveur, le recadrage : les
  chiffres ne bougeaient pas d'un centième.
- **La cause** : le décile ne marche que si le texte couvre une bonne part de
  la boîte. Les chiffres d'une pastille en couvrent **un dixième** : le seuil du
  décile tombe alors **en plein anticrénelage**, et on mesure du gris de bord.
- **Leçon** : **la couleur du texte est DÉCLARÉE, donc connue et solide ; seul
  le fond dépend de ce qu'il y a dessous. On déclare l'une, on mesure l'autre.**
  Et on neutralise l'animation d'apparition avant de photographier, sinon on
  mesure le contraste d'un fondu.
- **À appliquer** : quand l'instrument et l'œil se contredisent, **on regarde**
  — on agrandit l'élément seul, on le met sous les yeux. Deux autres faux
  rouges de la même soirée : `querySelector('[role=dialog]')` qui mesurait le
  tiroir toujours monté au lieu de la modale, et un recadrage calculé sur des
  boîtes lues **avant** la capture, entre lesquelles les images différées
  avaient déplacé la mise en page.

## 2026-08-19 — On ne corrige pas une donnée contre un résumé

- **Contexte** : le `MENU.md` d'Au Braisé d'Or (transcription des photos du menu
  papier) donnait « pizza pêcheur 4 000 / (à confirmer) », le site affichait
  « 4 000 / 6 000 ». Conclusion apparente : un prix inventé, à retirer — et
  cette pizza est un des 4 plats du héros, le chiffre s'affiche en grand.
- **Ce qui s'est passé** : en recadrant la photo d'origine au bord coupé, **le
  6 est lisible**. Le site avait raison, le résumé était trop prudent. Retirer
  le prix aurait fait perdre la grande taille à la vente.
- **Leçon** : un fichier de transcription n'est pas la source, c'est une
  lecture de la source. **Avant de corriger une donnée, remonter à la photo, au
  scan, au message d'origine.** Le même détour a montré que 4 lignes du
  petit-déjeuner n'étaient jamais arrivées jusqu'au site.
- **À appliquer** : marquer dans le fichier de transcription **ce qui est lu**
  et **ce qui est déduit**, et garder les originaux (`_partage/`) à portée.
  Une carte à laquelle il manque une ligne a l'air d'une carte complète : elle
  ne se vérifie qu'en la comparant à autre chose qu'elle-même.

## 2026-08-19 — Retirer un plat n'est pas supprimer une ligne

- **Contexte** : la propriétaire d'Au Braisé d'Or fait retirer 13 plats de sa
  carte (6 pizzas sur 10, 2 grillades, 2 burgers, 3 cocktails alcoolisés).
- **Ce qui cassait en silence** : (1) la **pizza pêcheur était un des 4 plats
  signature du héros** — le visiteur serait arrivé sur un plein écran vantant
  un plat introuvable trois écrans plus bas ; (2) **deux notes de catégorie
  devenaient fausses** : « servis avec Coca-Cola sauf végétarien, crispy,
  nugget » sans plus de crispy ni de nugget, et « avec ou sans alcool » sans
  plus une goutte d'alcool.
- **Leçon** : un retrait modifie **tout ce que la page raconte**, pas seulement
  la liste. Les données se régénèrent ; les **phrases**, elles, ne sont
  vérifiées par rien.
- **À appliquer** : après un retrait, chercher le nom du plat **partout**
  (héros, carrousel, notes de catégorie, pied de page, affiche imprimée) et
  relire ce que les textes voisins affirment encore. Puis poser **un contrôle
  par élément retiré**, sur le texte rendu de la page : un plat retiré mais
  laissé affiché se commande quand même, et c'est le restaurant qui gère la
  déception du client.
- ⚠️ **SUITE, le soir même** : la note disait « Lapin », la ligne du menu dit
  « lapin **ou mouton** frit ». Retirer la ligne entière a **supprimé un plat
  que la maison vend toujours** — Mongazi l'a corrigé dans l'heure. **Une ligne
  de menu qui contient un « ou » est deux produits** : quand le client n'en
  nomme qu'un, on retire ce qu'il nomme, pas la ligne. Et poser la question
  reste ce qui rattrape le coup : elle était dans ma liste, elle a été lue.

## 2026-08-19 — Quand une information manque, on donne le chemin, pas une valeur

- **Contexte** : la propriétaire ajoute une catégorie « Desserts » (yaourt,
  glace, cocktail) **sans donner un seul prix**.
- **Ce qui a été fait** : convention `p:0` = prix pas encore donné. La carte
  affiche **« Prix sur demande »**, et la fiche remplace le panier par
  **« Demander le prix sur WhatsApp »**, question déjà rédigée.
- ⚠️ **Un article sans prix ne doit jamais entrer au panier** : le total
  mentirait et le message de commande partirait avec un « 0 F ». Un contrôle
  vérifie qu'aucun « 0 F » n'apparaît nulle part.
- **Leçon** : c'est la même famille que « Prix sur demande » chez Weinkeller et
  « Photo sur WhatsApp » chez Hillary. **Ni inventer, ni cacher, ni s'excuser :
  donner au client le chemin pour obtenir ce qui manque.** Cacher la catégorie
  aurait privé la maison d'une vente qu'elle vient de demander.

## 2026-08-19 — La source vaut mieux qu'un résumé, le client vaut mieux que la source

- **Contexte** : une heure passée à recadrer les photos du menu papier pour
  lever deux prix coupés (napolitaine, oriental) et confirmer celui de la
  pêcheur. Le soir même, la propriétaire **retire ces trois pizzas**.
- **Leçon** : remonter à la source reste juste — la même lecture a trouvé 4
  lignes de petit-déjeuner absentes du site, qui, elles, restent. Mais quand
  une question porte sur **ce que le client veut vendre**, et pas sur ce qu'un
  document dit, **il faut la lui poser d'abord**. Aucune lecture, si rigoureuse
  soit-elle, ne devine une décision commerciale.
- **À appliquer** : trier les questions en deux tas avant d'enquêter — celles
  qu'un document peut trancher (on lit), celles que seul le client tranche (on
  demande, et on avance ailleurs pendant ce temps).

## 2026-08-19 — Le même modèle de détourage gagne ici et perd là

- **Contexte** : détourer des plats pour le héros d'Au Braisé d'Or. Deux lots de
  photos, deux verdicts opposés sur planche comparative.
- **Les bols de sauce sur fond gris** : `isnet-general-use` garde le bol entier
  ET la vapeur ; `u2net` ne garde que la viande et jette le bol ;
  `birefnet-general` déchiquette le bol.
- **Les assiettes NOIRES sur fond NOIR** : c'est l'inverse. isnet garde une
  tache de vapeur pleine, une encoche dans l'assiette et un bout d'ardoise ;
  **birefnet découpe la masse du plat proprement**.
- **Leçon** : il n'y a pas de « bon modèle » de détourage, il y a un bon modèle
  **pour ce lot de photos**. Le facteur décisif ici est le contraste entre le
  sujet et le fond, pas la qualité du modèle.
- **À appliquer** : **faire la planche comparative à chaque nouveau lot**, la
  REGARDER sur le fond où l'image sera posée (un halo ne se voit pas sur du
  blanc), et écrire dans l'outil ce qui a perdu et pourquoi — sinon le suivant
  refait les essais. ⚠️ Corollaire déjà payé : « nettoyer » un défaut par
  ouverture morphologique mord dans le sujet. Changer de modèle plutôt que
  réparer un mauvais masque.

## 2026-08-19 — Un prix qui dépend du choix du client n'est pas deux tailles

- **Contexte** : la carte des sauces annonce « 1 500 F à 3 000 F ». Lu comme
  Normal/Grand, ça donnait deux boutons de taille et un total exact au panier.
  Mongazi corrige : « le prix varie en fonction des éléments entre parenthèses ;
  en fonction de ce que le client veut dedans, le prix augmente. »
- **Ce que ça change** : ce n'est pas un choix entre deux prix, c'est une
  **fourchette** dont la valeur exacte se fixe à la commande. Le panier ne peut
  donc pas afficher un total : il affiche **une fourchette**, et le message
  WhatsApp dit « merci de me le confirmer ».
- ⛔ **Et on n'invente pas le prix de chaque ingrédient** pour reconstituer un
  total : la maison n'a donné qu'une borne basse et une borne haute. Mettre un
  chiffre en face de « crabe » serait le fabriquer.
- **Leçon** : avant de modéliser un prix, demander **de quoi il dépend**. Deux
  tailles, une fourchette et un supplément se ressemblent sur le papier et ne
  produisent pas le même panier. Même famille que « `p:0` = prix pas encore
  donné » : quand le total ne peut pas être connu, on le dit, on ne l'invente pas.

## 2026-08-19 — Un damier « transparent » peut être peint dans les pixels

- **Contexte** : le client renvoie ses plats **déjà détourés**. Les fichiers
  arrivent en **RGB sans canal alpha** : le damier gris de son éditeur est
  aplati dans l'image. Vu à l'écran, ça ressemble à de la transparence ; posé
  sur une page, c'est un rectangle à carreaux.
- **Ce qui a coûté quatre tours** : vouloir retirer le damier « proprement » en
  le reconnaissant à ses deux gris — apprendre les gris sur les coins, remplir
  depuis les bords, ponter les pixels de transition, rembourrer avant la
  fermeture, reconstruire la grille. Échec de fond : **sur une des photos les
  gris du damier étaient 77 et 124, et le bord noir de l'assiette a des reflets
  dans cette plage.** Aucun seuil ne les sépare.
- **Ce qui a marché du premier coup** : **rembg sur le fichier à damier.** Un
  modèle de saillance ne se demande pas de quelle couleur est le fond.
- **Leçon** : quand un outil générique existe pour « séparer le sujet du fond »,
  l'essayer AVANT d'écrire un masque sur mesure pour un fond particulier. Le
  sur-mesure ne bat le général que si le général a échoué.
- ⚠️ **Et vérifier le canal alpha à la réception** : `im.mode` et
  `getchannel('A').getextrema()`. Une image « détourée » sans alpha est un
  piège silencieux.
- ⚠️ **Archiver la SOURCE REÇUE, jamais un intermédiaire** : j'avais copié mon
  masque raté dans le dossier d'archive, et l'outil a ensuite travaillé
  dessus — l'assiette avait disparu et le défaut semblait venir de rembg.

## 2026-08-18 — Un contrôle de mise en pause a besoin d'un témoin

- **Contexte** : les pièces à deux photos basculent toutes seules, et doivent
  s'arrêter hors de l'écran. J'écris le contrôle : état, on attend, état, « ils
  doivent être identiques ». Vert du premier coup.
- **Le piège** : ce contrôle serait **vert aussi si le mécanisme était mort**.
  Deux états identiques prouvent l'immobilité, jamais la mise en pause.
- **Leçon générale** : tout contrôle qui vérifie que **quelque chose ne se
  produit pas** doit être précédé d'un contrôle qui prouve que **ça se produit**
  dans les conditions normales. Sans le témoin, on ne teste rien.
- **À appliquer** : partout où on vérifie une absence — pas d'animation en
  mouvement réduit, pas de requête réseau, pas de son, pas de bascule hors
  écran.

## 2026-08-18 — On échantillonne, on ne compare pas deux instantanés

- **Contexte** : « le catalogue tourne » vérifié par un état, 5,2 s d'attente,
  un second état, « ils doivent différer ». Échec apparent, site intact.
- **La cause** : la bascule a une période de **7,2 s**. Deux relevés espacés de
  5,2 s retombent sur la **même phase une fois sur cinq**. Le contrôle échouait
  au hasard de la seconde où il tombait.
- **Leçon générale** : pour observer un phénomène **périodique**, on relève à
  intervalle court sur une fenêtre qui couvre au moins un cycle entier, et on
  compte les états **distincts**. Deux points sur une sinusoïde ne disent rien.
- **Même famille** que le contrôle qui échouait au hasard le 2026-08-17 (serveur
  de test mono-tâche). Un contrôle intermittent finit toujours par être ignoré,
  et c'est là qu'il laisse passer un vrai défaut.

## 2026-08-18 — Un contrôle qui dit « il manque quelque chose » doit dire QUOI

- **Contexte** : « aucune ressource locale manquante » échouait. Rien d'autre.
  Une demi-heure pour découvrir qu'il s'agissait des six `.mp3`, et qu'ils
  étaient bien sur le disque : la page est ouverte en `file://`, où Chromium
  **interdit `fetch()`** par principe.
- **Leçon** : un message d'échec qui ne nomme pas l'objet fautif coûte plus cher
  que le défaut qu'il signale. Il nomme maintenant les fichiers.
- **Et une leçon de méthode** : avant de corriger, j'ai rejoué le même relevé
  sur la version de `main`. Identique. **On ne répare pas ce qu'on n'a pas
  cassé** — et on ne s'attribue pas un défaut antérieur.

## 2026-08-19 — Un masque ne rend pas des pixels qui n'existent pas

- **Contexte** : Mongazi voit le site en ligne : « la sauce krinkrin a été mal
  détourée sur le côté droit, c'est coupé, ça doit être bien circulaire comme
  pour les autres ».
- **Le réflexe qui a coûté du temps** : chercher un meilleur masque. Cercle
  ajusté, octogone tracé à l'œil, contour mesuré sur 360 rayons en suivant le
  liseré brillant du bord de l'assiette — trois tentatives, trois échecs, dont
  un contour en dents de scie franchement pire que le défaut d'origine.
- **La vraie cause** : la photo source était **recadrée trop serré**. Le disque
  d'ardoise sortait du cadre à gauche, à droite et en bas, et l'assiette
  elle-même touchait les bords. Il n'y avait rien à détourer : l'information
  manquait.
- **La solution** : une **autre source**. Le premier envoi de la même sauce,
  sur fond noir, était bien cadré — l'assiette y tient entière avec de la
  marge. Trente secondes de traitement au lieu d'une heure de masquage.
- **Leçon** : devant un sujet coupé, **mesurer d'abord si le sujet touche le
  bord de l'image** (`getbbox()` contre les dimensions). Si oui, aucun
  traitement ne le réparera : il faut une autre source, ou la redemander.
- **À appliquer** : un contrôle à la réception d'une photo destinée à être
  détourée — le sujet touche-t-il un bord ? Si oui, le dire tout de suite,
  avant de commencer.
## 2026-08-20 — Un écart de teinte n'est pas un écart perçu

- **Contexte** : le héros d'Hillary peint son fond avec la couleur de la pièce.
  Pour éviter deux transitions invisibles, je compare les couleurs voisines.
  Première version : la distance entre leurs **angles de teinte**, seuil 28°.
- **Le faux défaut** : la règle accusait `hero-3 → hero-4`, 19° d'écart. Leur
  distance perçue est de **33 ΔE** — un bleu profond et un cyan clair, que
  personne ne confondrait. Je l'avais signalé à Mongazi comme un défaut à
  corriger. C'était faux.
- **La cause** : l'angle de teinte ignore la **clarté** et la **saturation**,
  c'est-à-dire l'essentiel de ce qui distingue deux couleurs à l'œil. Deux
  rouges à 25° peuvent être indiscernables si leur clarté est la même ; un bleu
  et un cyan à 19° sautent aux yeux.
- **Leçon générale** : dès qu'on mesure « est-ce que ces deux couleurs se
  ressemblent ? », on mesure en **L\*a\*b\***, jamais en degrés de teinte. La
  conversion tient en dix lignes et ne dépend d'aucune bibliothèque.
- **Et une leçon plus large** : une mesure commode n'est pas une mesure juste.
  Avant de faire d'un nombre un critère de qualité, vérifier qu'il dit bien ce
  qu'on croit — sur un cas où l'on connaît déjà la réponse.

## 2026-08-20 — La couleur dominante d'une photo de mode, c'est souvent la peau

- **Contexte** : le fond du héros est relevé sur la photo de la pièce (teinte
  dominante des pixels saturés). La robe verte et jaune est ressortie en
  **brun**.
- **La cause** : ce n'était pas un bug. Bras et jambes nus couvraient **23 %**
  de la photo contre **17 %** pour le tissu. La peau gagnait, honnêtement.
- **Le correctif** : parmi les teintes qui occupent au moins 15 % de la pièce,
  prendre **la plus saturée**. Un vêtement est presque toujours plus vif qu'une
  peau. Vérifié sur huit pièces : la verte redevient verte, l'ensemble en jean
  gagne son vrai rouge, les six autres ne bougent pas.
- ⚠️ **Ce qui ne marche pas** : un détecteur de peau par bande de teinte. La
  peau occupe 10-40°, exactement là où vivent les tissus orange et terracotta —
  et Hillary en a. On aurait réparé une pièce en en cassant une autre.

## 2026-08-20 — Vérifier ce qui est gratuit avant de lancer ce qui est cher

- **Contexte** : le script de pose détoure les photos (45 s chacune) puis les
  injecte. Une restructuration avait effacé sept fonctions au passage.
- **Ce qui s'est passé** : il a détouré **douze photos pendant dix minutes**,
  puis est mort sur `NameError` à la seconde d'après, au moment précis où il
  allait enfin écrire quelque chose.
- **Leçon** : le coût d'une bourde ne doit pas dépendre de l'endroit où elle
  explose. Une étape coûteuse commence par vérifier ses préconditions gratuites
  — ici, que les fonctions qu'elle appellera existent.
- **Corollaire, appris le même jour** : un outil qui réécrit du code par
  découpe de texte passe sa sortie à `node --check` **avant** de l'écrire. Deux
  bourdes de découpe (une virgule après un commentaire, puis tout l'en-tête du
  fichier effacé) rendaient le site entièrement muet.

## 2026-08-20 — `npx playwright install` n'installe PAS les navigateurs de Python

- **Contexte** : les navigateurs avaient été supprimés pour libérer le disque.
  Pour republier la vitrine d'Hillary il fallait ses 138 contrôles, donc les
  réinstaller. J'ai lancé `npx playwright install chromium webkit`.
- **Ce qui s'est passé** : 430 Mo téléchargés, installés, et le contrôle
  s'arrête quand même :
  `Executable doesn't exist at ...\chromium_headless_shell-1223\...`
- **La cause** : le paquet **Node** et la bibliothèque **Python** épinglent des
  **numéros de version différents**. `npx` a posé `chromium-1234` et
  `webkit-2336` ; la bibliothèque Python réclame `1223` et `2287`. Ils vivent
  dans le même dossier, portent les mêmes noms à un chiffre près, et **ne se
  remplacent pas**.
- **La bonne commande**, quand le contrôle est écrit en Python :
  `python -m playwright install chromium webkit`.
- ⚠️ **Le coût réel** : 430 Mo pour rien sur une connexion de Cotonou, et le
  disque qui retombe à **0,08 Go libres** pendant que les deux jeux coexistent.
- **Leçon** : la commande d'installation doit venir du **même écosystème que le
  code qui l'utilise**. `npx` pour un `_qc.js`, `python -m` pour un `_qc.py`.

## 2026-08-21 — Un enfant ne passe jamais au-dessus du plafond de son parent

- **Contexte** : le bouton du son recouvrait du texte partout. Je l'ai déplacé
  dans la barre du haut, une bande de bord opaque, où il ne gêne plus rien.
- **Ce qui a cassé** : il devait rester atteignable pendant une commande, en
  flottant au-dessus de la fiche. Je lui ai écrit `z-index:130` contre le
  `z-index:120` de la fiche. Ça n'a pas marché, et c'était normal.
- **La cause** : la barre porte `z-index:50` et crée donc un **contexte
  d'empilement**. À l'intérieur, tous les `z-index` sont relatifs à ce 50. Un
  enfant à 130 vaut 50 vu de l'extérieur. Aucune valeur n'y change quoi que ce
  soit.
- **Le correctif** : changer de **parent**, pas de style. Le bouton sort de la
  barre le temps de la commande (`document.body.appendChild`) et y revient en
  refermant. Déplacer un nœud ne perd pas ses écouteurs.
- **À retenir** : quand un `z-index` « ne marche pas », ce n'est presque jamais
  la valeur. C'est un ancêtre qui a créé un contexte — `z-index`, `transform`,
  `filter`, `opacity < 1`, `backdrop-filter` en créent tous un.

## 2026-08-21 — Un détecteur qui s'exclut lui-même annonce zéro défaut

- **Contexte** : détecteur de texte recouvert. Pour ne pas accuser l'en-tête
  fixe, qui a le droit de passer devant, j'exclus « tout élément fixe au fond
  opaque ».
- **Le piège** : le bouton du son est fixe **et** opaque à 92 %. Il satisfaisait
  ma propre exclusion. Le détecteur l'a rangé parmi les meubles légitimes et a
  annoncé **zéro défaut** alors qu'il en couvrait onze.
- **Le correctif** : une **bande** de bord traverse l'écran (≥ 85 % d'une
  dimension) et touche un bord. Une pastille de 46 px qui flotte n'en est pas
  une, même opaque : c'est un **instrument**, et un instrument ne recouvre
  jamais du texte.
- **Leçon générale** : une exclusion écrite pour épargner un cas légitime doit
  être **serrée sur ce cas**. Trop large, elle épargne le coupable — et un
  contrôle qui dit « rien à signaler » est pire que pas de contrôle.

## 2026-08-21 — La bonne définition d'un chevauchement

- Ce qui est un défaut : **du texte dans le flux** recouvert par un élément
  positionné.
- Ce qui n'en est pas : un texte **posé exprès** sur une photo — le chiffre
  géant d'un héros, une légende, un badge, un « Commander » au survol. Ils sont
  en `position:absolute` : c'est la signature de l'intention.
- Sans cette distinction, un premier jet annonçait **105 défauts** sur la
  vitrine Hillary, presque tous voulus. Avec elle : **14**, tous réels.
- **À retenir** : avant de compter des défauts, écrire ce qui en est un. Un
  détecteur qui ne sait pas distinguer l'intention de l'accident noie le vrai
  défaut dans le bruit, et on cesse de le lire.

## 2026-08-21 — Un garde-fou qui protège d'un cas déjà couvert devient une panne

- **Contexte** : la scène des plats du Braisé avance toute seule. Une règle
  écrite plus tôt l'arrêtait **définitivement** au dernier plat, pour ne pas
  faire remonter la page en travers de quelqu'un qui descend vers le menu.
- **Le raisonnement était juste, la conclusion trop large.** Le cas redouté
  était déjà couvert **deux fois** : rien ne bouge quand la scène n'est pas à
  l'écran, et un geste repousse tout de 12 s. Il ne restait donc que le
  visiteur **immobile, qui regarde** — et pour lui une scène figée n'est pas
  une protection, c'est une panne. Au bout de 22 s, le site avait l'air mort.
- **Leçon** : avant d'ajouter un garde-fou, énumérer qui reste concerné une
  fois les autres garde-fous appliqués. Si la réponse est « personne qu'on
  voulait protéger », le garde-fou ne protège plus rien : il casse.
- **Corollaire** : une boucle qui se referme doit **respirer**. Le dernier
  élément se laisse regarder un tour de plus avant le retour, sinon le retour
  ressemble à un bug.

## 2026-08-21 — La cadence d'un carrousel doit compter avec les autres mécanismes

- **Contexte** : le carrousel d'Hillary devait avancer tout seul. Chaque pièce
  photographiée des deux côtés se retourne 3,6 s après son arrivée.
- **Le piège évité** : une cadence ordinaire (4 s) aurait fait passer à la
  pièce suivante **avant** que le dos ait eu le temps de se montrer. On aurait
  posé un mécanisme par-dessus l'autre et perdu le second, sans que rien ne le
  signale.
- **Le correctif** : la durée **suit la pièce**. Deux vues → 7,4 s (face, dos,
  puis on avance). Une seule vue → 5,5 s.
- **Leçon** : avant de choisir un intervalle, lister ce qui se passe déjà dans
  cet intervalle. Un nombre rond choisi seul écrase souvent quelque chose.

## 2026-08-21 — `hidden` ne cache rien quand un `display` est déclaré

- **Contexte** : un formulaire en trois étapes, chaque étape `hidden` sauf une,
  deux champs conditionnels `hidden` eux aussi.
- **Ce qui s'est passé** : tout était visible. Les trois étapes empilées, les
  champs conditionnels ouverts, un bouton caché qui débordait de la modale.
- **La cause** : l'attribut `hidden` ne vaut qu'un `display:none` de la
  **feuille par défaut du navigateur**. Dès qu'on écrit `.ch{display:grid}` ou
  `.pill{display:inline-flex}`, on l'écrase — une règle d'auteur passe toujours
  devant la feuille par défaut, quelle que soit sa spécificité.
- **Le correctif** : un sélecteur d'attribut, qui est une règle d'auteur lui
  aussi et gagne par spécificité : `.ch[hidden]{display:none}`. Pas besoin
  d'`!important`.
- **À retenir** : dès qu'une classe déclare un `display`, prévoir sa variante
  `[hidden]` dans la foulée. C'est le même geste, deux lignes plus bas.

## 2026-08-21 — Un enfant de grille a `min-width:auto`, pas zéro

- **Contexte** : des champs à `width:100%` dans une grille, qui débordaient de
  leur modale sur téléphone.
- **La cause** : ce n'était pas le champ qui débordait, c'était **la piste qui
  avait grandi**. Un enfant de grille (comme de flex) a `min-width:auto` : la
  piste s'élargit jusqu'à la largeur **intrinsèque** de son contenu — ici un
  long texte d'invite dans un `textarea`. `width:100%` de 800 px reste 800 px.
- **Le correctif** : `grid-template-columns:minmax(0,1fr)` sur le conteneur, ou
  `min-width:0` sur les enfants.
- **À retenir** : quand un enfant à `width:100%` déborde, ce n'est jamais lui
  qu'il faut regarder. C'est son parent qui a cédé.

## 2026-08-21 — Un contrôle qui a besoin du réseau doit le dire

- **Contexte** : deux contrôles rouges sur une vitrine parfaite. L'un ouvrait
  **vraiment** `wa.me` pour vérifier qu'un message part ; l'autre attendait que
  Google Fonts réponde.
- **Le vrai sujet** : le premier prétendait vérifier **le message**, il
  vérifiait surtout la connexion. On intercepte `window.open` et on lit l'URL :
  le contrôle teste enfin ce qu'il annonce, et il devient déterministe.
- **Pour le second**, la dépendance est irréductible : il se **saute en le
  disant** quand aucune police ne répond, et reste strict dès qu'il y a du
  réseau. Les contrôles voisins, qui lisent la police *demandée*, ne dépendent
  de rien et restent durs.
- **Leçon** : un contrôle qui rougit pour une raison extérieure au produit
  apprend à ignorer le rouge. Soit on le rend indépendant, soit il annonce
  lui-même qu'il ne peut pas juger.

## 2026-08-21 — Un défilement lissé maison doit CÉDER aux autres

- **Contexte** : le moteur de défilement d'Angy Art (l'équivalent maison de
  Lenis) ne relisait sa cible que `if (!anime)`, c'est-à-dire **seulement à
  l'arrêt**. Pendant qu'il glissait, il réécrivait `scrollY` à chaque image et
  écrasait tout déplacement venu d'ailleurs.
- **Qui en souffre** : la recherche du navigateur, un lecteur d'écran, la
  touche Fin, le passage au clavier sur un bouton hors écran, un
  `scrollIntoView` d'outil de contrôle. Le saut est annulé **sans un mot**.
  Mesuré : un saut à 200 px ramené à **5 992 px**.
- ⚠️ **Le correctif naïf est pire que le défaut.** Adopter *tout* écart casse
  le glissement : une image perdue laisse la page **sur le chemin** du moteur,
  et l'adopter arrête net le défilement au milieu — une régression visible par
  tout le monde, pour réparer un cas étroit.
- **Le bon critère, c'est OÙ** : entre `courant` et `cible` (à 12 px près),
  c'est nous ; ailleurs, c'est quelqu'un d'autre, et c'est lui qui a raison.

  ```js
  var bas = Math.min(courant, cible) - 12, haut = Math.max(courant, cible) + 12;
  if (y < bas || y > haut) { cible = borne(y); courant = y; }
  ```
- **À retenir** : c'est la **troisième** apparition de cette famille (Lenis sur
  Au Braisé d'Or, saut arrêté à 7 382 px de sa cible). Tout défilement lissé,
  bibliothèque ou maison, prend la main sur `scrollY` : il doit prévoir
  explicitement ce qui se passe quand un autre y écrit aussi.

## 2026-08-21 — Une liste recopiée finit toujours par mentir sur ce qu'elle décrit

Quatre contrôles, le même jour, sur la même vitrine, pour la même raison :

| Ce qui était recopié | Ce que ça a coûté |
|---|---|
| trois ancres de menu | le menu a changé → `null.click()`, le contrôle **plantait** au lieu de tester |
| les étiquettes de sections | le contrôle a **accusé le site** d'avoir perdu des textes qu'il avait seulement renommés |
| les sélecteurs de sections des captures | les **deux sections neuves n'ont jamais été photographiées**, et personne ne l'a vu |

- **Le pire des trois est le troisième** : les deux autres crient. Une liste de
  captures, elle, **ne se plaint pas de ce qu'elle ne montre pas**. Elle a
  produit huit images vertes pendant que deux sections entières n'étaient
  jamais regardées.
- **À retenir** : un contrôle **lit** ce qu'il décrit (`document.querySelectorAll`),
  il ne le recopie pas. Ce qu'on garde écrit en dur, ce sont les choses qui ne
  doivent **jamais** changer : les phrases du client, pas le vocabulaire du menu.

## 2026-08-21 — Attendre n'est pas se placer

- **Contexte** : un contrôle de contraste coupait le lissage, appelait
  `scrollIntoView`, attendait 500 ms, puis mesurait. Il passait tout seul et
  échouait **juste après les captures** — qui laissent le moteur en pleine
  course.
- **Le diagnostic à ne pas rater** : le contrôle criait au *défaut de
  contraste* alors que l'élément **n'était pas à l'écran**. Un contrôle qui se
  trompe de coupable envoie chercher une heure au mauvais endroit.
- **Le correctif** : `placer()` — on se place, **puis on vérifie qu'on y est**,
  et on recommence jusqu'à six fois. Si on n'y arrive pas, on le dit **avec le
  chiffre** (« impossible d'amener `.visite-sm` à l'écran : haut −1 240 px »).
- **À retenir** : face à un moteur qui réécrit `scrollY`, **aucune durée
  d'attente n'est une preuve**. Il faut regarder où on a atterri. Même famille
  que « ne jamais mesurer une animation d'ouverture avec des `wait_for_timeout`
  empilés » (2026-08-08).

## 2026-08-21 — Quand on tranche à la place du client, la raison s'écrit à côté

- **Contexte** : six questions posées au client, aucune réponse, et l'ordre de
  « faire ce qui est meilleur pour le moment ».
- **Le piège** : une décision prise à la place de quelqu'un ressemble, trois
  semaines plus tard, à un oubli. La prochaine session ne peut plus savoir si
  « les six œuvres » est un choix assumé ou une liste qu'on a mal recopiée.
- **La règle** : la raison s'écrit **dans le code, à côté de la décision**, pas
  seulement dans un journal. Le commentaire dit ce qu'on a mesuré (« 31 px de
  marge à 1024 px »), ce qu'on a refusé (« annoncer disponible sur les six
  serait une affirmation qu'on ne peut pas tenir ») et ce que coûterait le
  retour en arrière (« un attribut à poser, pas une refonte »).
- **Le principe qui a guidé les six** : entre deux inconnues, choisir celle qui
  **n'affirme rien**. On ne sait pas quelles cinq œuvres composent la
  collection → on montre les six et on n'annonce aucun nombre. On ne connaît
  pas le statut des pièces → on n'en invente aucun et on invite à demander.
  Cacher ou affirmer coûte cher ; se taire proprement ne coûte rien.

## 2026-08-21 — Une session à distance ne peut pas publier, et doit le dire tôt

- **Contexte** : tout était prêt à mettre en ligne — contrôles verts, `_dist`
  composé, 36 fichiers. Aucun jeton Cloudflare dans le conteneur.
- **La cause, et c'est la bonne règle** : `secrets/` est ignoré par git parce
  que le dépôt est **public**. Un conteneur cloné à neuf n'a donc jamais les
  clés, et aucune variable d'environnement ne les remplace.
- **À retenir** : une session à distance **écrit, contrôle et pousse** ; elle
  **ne déploie pas**. Le dire dès qu'on sait, pas à la fin — sinon on laisse
  croire qu'un travail est en ligne alors qu'il attend une commande sur le PC.
  C'est le pendant de « un `git push` ne déploie rien tout seul ».

## 2026-08-22 — Une animation qui avance PAR IMAGE punit les machines lentes

- **Contexte** : sur la vitrine d'Angy Art, cliquer « accueil » depuis le bas de
  la page ramenait bien en haut sur téléphone et sur tablette, mais laissait la
  page à **284 px** sur ordinateur (puis 467 px à l'essai suivant : la valeur
  changeait à chaque fois).
- **La fausse piste** : une position qui varie fait penser à une course entre
  deux mécanismes, ou à une force extérieure qui interrompt le glissement. Le
  code contenait justement une logique d'adoption des sauts venus d'ailleurs.
- **La vraie cause** : la boucle interpolait **d'un cran fixe par image** :
  ```js
  courant += (cible - courant) * 0.095;
  ```
  À 60 images par seconde, le trajet de 10 318 px est fini en 1,1 s. À 30
  images par seconde, il en faut **plus du double**. Le glissement n'était pas
  cassé : **il n'était pas fini**. Et la page d'ordinateur, plus chargée en
  effets, tombe justement sous les 60.
- **Le correctif** : interpoler **au temps écoulé**, pas à l'image.
  ```js
  var dt = Math.min(64, ts - dernier);
  var k  = 1 - Math.pow(1 - 0.095, dt / 16.7);
  courant += (cible - courant) * k;
  ```
  Le `Math.min(64, …)` évite qu'un gel d'une seconde produise un saut brutal.
- ⚠️ **Qui payait vraiment** : le moteur maison ne tourne que sur pointeur fin,
  donc le contrôle ne pouvait le voir que sur ordinateur. Mais **tout ce qui est
  écrit ainsi ailleurs** (compteurs, révélations, glissements) ralentit sur les
  téléphones bas de gamme de Cotonou, qui sont nos vrais visiteurs.
- **À appliquer** : chercher `* 0.0` et `+=` dans les boucles `requestAnimationFrame`
  du parc. Une interpolation sans `dt` est un défaut qui ne se voit que sur les
  machines qu'on n'a pas sous la main.

## 2026-08-25 — Un défilement lissé maison doit céder aux autres (3e fois)

Troisième apparition, sur le troisième site : Au Braisé d'Or (Lenis, saut
arrêté à 7 382 px), Angy Art (200 → 5 992 px), Hillary M. Styl (200 → 5 996 px).
La leçon du 2026-08-21 est confirmée, et elle se généralise :

- **Tout moteur qui écrit dans `scrollY` doit prévoir ce qui arrive quand un
  autre y écrit aussi.** Bibliothèque ou maison, c'est la même dette.
- Le critère est **où**, pas **combien** : entre `courant` et `cible` c'est le
  moteur, ailleurs c'est quelqu'un d'autre, et c'est lui qui a raison.
- **À faire sur tout nouveau site qui lisse son défilement**, sans attendre que
  quelqu'un s'en plaigne : les victimes (recherche du navigateur, lecteur
  d'écran, touche Fin, focus clavier) ne laissent pas de trace.

## 2026-08-25 — `role="dialog"` sur un `<div>` n'apporte que l'étiquette

- **Contexte** : la fiche de commande de Hillary, un `<div role="dialog"
  aria-modal="true">`. Tout le monde la croyait accessible parce qu'elle
  portait les bons attributs.
- **Ce qu'un vrai `<dialog>` fait et qu'un div ne fait PAS** : la couche
  supérieure, le piège à focus, la mise à l'écart du reste de la page. Mesuré :
  le focus restait sur `<body>`, **une seule** tabulation sortait vers le
  catalogue caché, rien n'était `inert`, et en refermant le focus retombait sur
  `<body>`.
- **Ce que ça coûtait** : cette fiche **est** le bon de commande. Quelqu'un au
  clavier ou au lecteur d'écran ne pouvait pas commander.
- **Les quatre gestes** : donner le focus à l'ouverture, l'enfermer, rendre le
  fond `inert` **et** `aria-hidden` (pour qui ignore `inert`), le rendre en
  refermant.
- ⚠️ **`focus({preventScroll:true})`** : donner le focus fait défiler la page,
  et un moteur de défilement maison se bat avec.
- ⚠️ **Une exception voulue doit être écrite à côté du contrôle**, sinon elle
  ressemble à un défaut : ici le bouton du son est dans la boucle des
  tabulations parce que la maison exige qu'on puisse couper le son en donnant
  ses mesures.

## 2026-08-25 — Une correction faite à un endroit n'est pas faite partout

- **Contexte** : le 2026-08-06, la courbe du héros a été réparée (elle partait
  à plat, la pièce restait figée ~580 ms après le clic). Deux mois plus tard,
  **le second carrousel du même site portait encore la courbe fautive**.
- **À retenir** : quand on répare un défaut de sensation, chercher tout de
  suite **qui d'autre porte le même code**. `grep` sur la valeur (ici
  `cubic-bezier(.4,0,.2,1)`) coûte dix secondes.
- Même famille que la leçon du défilement ci-dessus, à l'échelle d'un fichier
  au lieu d'un dépôt.

## 2026-08-25 — Vérifier sa sonde avant d'accuser le produit

Quatre « défauts » d'affilée pendant un audit, tous dus à la sonde :

| Ce que la sonde disait | Ce que c'était vraiment |
|---|---|
| `NaN` dans le message WhatsApp | j'avais injecté un panier au mauvais format (`{id,q,exp}` au lieu de `{id,qte,express}`) |
| « la fiche ne s'ouvre pas » | le rideau d'ouverture dure **4 800 ms**, j'attendais 4 200 |
| « la fiche ne s'ouvre pas » (bis) | ce n'est pas un `<dialog>` mais un `div#ov.on` |
| « le focus sort de la fiche » | c'était le bouton du son, qui y est **par décision** |
| « le fond reste inerte après fermeture » | le tiroir du panier porte `aria-hidden="true"` **par construction** |

- **La règle** : avant d'annoncer un défaut, se demander *« et si c'était ma
  mesure ? »*. Un audit qui crie au loup cinq fois n'est plus lu.
- **Le signe qui ne trompe pas** : la suite de contrôle officielle passe au
  vert sur le même chemin. Quand elle et la sonde divergent, c'est presque
  toujours la sonde.

## 2026-08-26 — `clearProps: "all"` VIDE l'attribut `style`

- **Ce que tout le monde croit** : il retire ce que GSAP a posé.
  **Ce qu'il fait** : il vide l'attribut `style` de l'élément, y compris ce
  que le composant y avait écrit lui-même.
- **Ce que ça a coûté, sur Au Braisé d'Or** : le bouton « Ajouter au panier »
  du héros portait sa couleur en style en ligne. Après l'animation :
  `background-color: rgba(0,0,0,0)`, texte crème, sur une carte de verre
  claire. **1,1:1 mesuré, invisible.** ⚠️ Et le défaut était **antérieur** :
  l'ancien bouton vert « Commander sur WhatsApp » avait le même sort, **en
  ligne**, depuis le 12/08. C'est la **deuxième fois** que GSAP fait
  disparaître le seul bouton qui rapporte de l'argent sur cette carte.
- Deuxième dégât le même jour : le corps du titre, calculé par plat (donc en
  ligne), était effacé — la **deuxième ligne**, la très grasse, la signature du
  héros, ressortait **plus petite que la première**.
- **La règle** : `clearProps: "opacity,visibility,transform"`, jamais
  `"all"`. Et ce qui est fixe et décoratif (une couleur de bouton) va dans
  une **classe**, qu'aucun `clearProps` ne peut atteindre.
- ⚠️ **Aucun des deux ne fait d'erreur en console, et les deux passaient un QC
  vert à 90 contrôles.** Ils ont été vus **sur des captures**, en regardant les
  quatorze sauces une par une. *Une vitrine n'est pas finie quand elle marche.*

## 2026-08-26 — Un instrument qui mesure une animation accuse un site sain

Trois contrôles ont accusé un site parfaitement juste, le même jour :

| Ce que le contrôle disait | Ce que c'était |
|---|---|
| « KRINKRIN dépasse de 36 px » | il lisait le `x` d'un `fromTo({x:50})` en cours. ⚠️ **GSAP ignore `prefers-reduced-motion`**, seul votre code le lit → `scrollWidth - clientWidth`, insensible aux transformations |
| « l'ardoise déborde de 170 px » | il comparait à la boîte **commune**, alors que les 14 assiettes sont **déplacées** par GSAP : il avait attrapé la voisine, garée hors champ → comparer l'enfant à **son propre conteneur**, qui subit la même transformation |
| « la pile de points est visible » | `display: none` laisse les éléments dans le DOM → tester aussi que la boîte a une taille |

- **La règle** : mesurer une **mise en page**, jamais un instant d'animation.
  Et quand plusieurs copies d'un élément coexistent, viser **la relation** (un
  enfant contre son parent), pas une position absolue.

## 2026-08-26 — Réparer un script qui échouait tôt réveille tout ce qu'il ne faisait plus

- **Contexte** : `_photos_sauces.py` mourait en **code 137 (tué faute de
  mémoire)** à la deuxième photo — une seule session rembg pour tout le lot,
  la fuite d'onnxruntime déjà vue chez Hillary. Réparé en donnant **un
  processus par photo**.
- **Ce qui a suivi, et que je n'attendais pas** : le script, enfin capable
  d'aller au bout, a atteint deux fichiers qu'il ne touchait plus depuis des
  semaines — et les a **écrasés**. Sur l'un, le carré automatique coupait tout
  le bord du bol : il ne restait qu'une texture jaune sans vaisselle.
- **La règle** : après avoir réparé un script qui s'arrêtait en chemin,
  **regarder ce qu'il touche pour la première fois depuis longtemps**. Un
  `git status` suffit, et il faut le lire ligne par ligne au lieu de committer.
- **Le correctif durable** : un drapeau qui **gèle** les sorties déjà bonnes,
  avec la raison écrite à côté. Sans ça, la prochaine exécution refait le même
  dégât en silence.
- ⚠️ **Le gel suit le FICHIER, pas le nom.** Quand la photo gelée a été
  réattribuée à un autre plat, le drapeau devait partir avec elle.

## 2026-08-26 — Un contrôle qui perd son sujet doit le dire, pas planter

- **Contexte** : le jour où le dernier plat a reçu sa photo, la suite de
  contrôle d'Au Braisé d'Or s'est **arrêtée en plein milieu** sur un
  `null.click()`. Elle cherchait « un plat sans image » pour ouvrir sa fiche.
  Il n'y en avait plus aucun.
- **Le vrai danger n'était pas le plantage** : c'est que **deux contrôles sans
  rapport étaient accrochés au même clic**. L'ardoise est un cas particulier
  qui peut disparaître ; l'**accompagnement obligatoire** est une règle métier
  permanente, et une commande qui part sans lui arrive incomplète en cuisine.
  En laissant les deux ensemble, la seconde serait morte avec la première,
  sans un mot.
- **Ce qu'on fait** : on sépare. Le contrôle spécifique **annonce** qu'il n'a
  plus de sujet ; le contrôle général se donne une autre cible (ici une sauce,
  catégorie qui exige toujours un accompagnement) et reste vert.
- **À retenir** : quand un succès du produit rend un contrôle sans objet,
  vérifier **ce qui voyageait avec lui**. C'est là que se perdent les contrôles
  qui comptaient.

## 2026-08-26 — Une assiette n'a ni trou ni fente, mais le seuil se mesure

- **Contexte** : sur une sauce, le masque avait taillé un **couloir vertical**
  dans le rebord du plat — 158 lignes percées, 52 px au pire. Invisible sur
  blanc, très visible sur le crème du héros.
- **Deux passes, deux raisons** : les **cavités** (transparent qu'on ne peut
  pas atteindre depuis le bord de l'image) et les **fentes** (un couloir qui
  débouche, et qui échappe donc à la première passe). Un remplissage de cavités
  seul n'a **rien trouvé**.
- ⚠️ **Ligne par ligne, jamais colonne par colonne** : en colonnes, l'espace
  entre le panache de vapeur et l'assiette serait « pris entre deux morceaux »
  lui aussi, et on souderait la vapeur au plat.
- ⚠️ **Le seuil ne se devine pas, il se mesure sur tout le parc.** Les dix
  assiettes ont été mesurées d'abord : six sans aucune fente, une à 0,4 %, la
  fautive à 5,8 % — **et deux à 12,7 % et 18,2 %**, dont la « fente » est
  l'espace entre la vapeur et le bol. Un seuil à 8 % ferme les vraies et laisse
  les fausses.
- ⚠️ **J'ai failli écrire que ces deux-là étaient « des plats à deux bols ».**
  Il a suffi de les REGARDER pour voir que non. Une explication plausible qu'on
  n'a pas vérifiée est une erreur qui attend son tour dans un commentaire.

## 2026-08-27 — Un fichier livré n'est pas un fichier affiché

- **Contexte** : Au Braisé d'Or. Six découpes de sauce étaient dans `main`,
  propres, pesées, poussées, en 200. **Et le héros posait quand même son
  ardoise** sur les six, en plein premier écran.
- **Ce qui s'est passé** : le héros ne lit pas le dossier `/plats`, il lit le
  `DECO` de `dishes.ts` (`img: d?.img` — absent = ardoise). Les sept commits
  qui ont posé les images n'ont jamais touché `dishes.ts`.
- ⚠️ **Rien ne pouvait le signaler.** Le contrôle « 0 image cassée » ne voit
  que les images **demandées** ; une image qu'on ne réclame jamais ne peut pas
  être cassée. Elle est parfaite, et invisible. Le manque est silencieux par
  construction : il n'y a ni erreur, ni 404, ni ligne rouge.
- **Leçon** : vérifier qu'un asset existe, pèse, répond 200 et n'est pas cassé
  ne prouve **rien**. Il faut vérifier qu'il est **demandé**.
- **À appliquer** : un contrôle qui lit **les deux côtés dans les fichiers** —
  ce qui est sur le disque contre ce que le code référence — et qui nomme les
  orphelins. Posé sur le client 09 (« aucune découpe inutilisée dans /plats »).
  **À reprendre partout où des médias sont posés à la main** : Hillary
  (`piece-*.webp`), Angy Art (`oeuvre-*`), Weinkeller (les bouteilles).

## 2026-08-27 — `git fetch` se fait AVANT de travailler, pas avant de pousser

- **Contexte** : le PC de Cotonou a refait de zéro les six photos de sauces
  d'Au Braisé d'Or — images, deux outils neufs, correctif du QC — alors que le
  travail dormait dans `origin/main` depuis la veille, poussé en 7 commits par
  une session lancée depuis le téléphone. **Mêmes photos sources, au bit près.**
- **Pourquoi personne n'a rien vu** : `scripts/rapatrier.py`, le script de
  début de session qui existe précisément pour ça, **excluait `origin/main`**
  de son inventaire (`if b == "origin/main": continue`). Il ne surveillait que
  les branches `claude/…`. Or une session du téléphone pousse **directement
  dans `main`**. Le script répondait « ✅ Rien ne traîne ».
- **Leçon** : « rien ne traîne sur les branches » ne veut pas dire « je suis à
  jour ». Une branche oubliée coûte une fusion ; **un `main` en retard coûte le
  travail refait deux fois**.
- **À appliquer** : `main_en_retard()` tourne désormais **avant** l'inventaire
  des branches et refuse de dire que tout va bien.

## 2026-08-27 — Deux versions du même travail : on compare, on ne fusionne pas

- **Contexte** : deux chaînes d'outils, écrites le même jour par deux machines,
  produisaient les mêmes six images de sauces.
- **Ce qui départage** : les **mesures déjà écrites dans les fichiers**. La
  version locale reconstruisait l'alpha en reconnaissant le damier et en se
  propageant depuis les bords — approche que l'autre session avait déjà
  **essayée, mesurée et rejetée** : *« sur le gombo, les deux gris du damier
  sont 77 et 124, et le bord noir de l'assiette a des reflets dans cette plage.
  Aucun seuil de luminance ne les sépare. »* Elle était écrite en tête de
  `_damier.py`, dans `main`, depuis huit jours.
- ⚠️ **Garder les deux aurait été le pire choix** : le script local aurait
  **réécrit en silence** les cadrages que l'autre gèle exprès, photo par photo.
  Deux outils qui écrivent le même fichier finissent toujours par s'écraser.
- **À appliquer** : lire ce que l'autre version a écrit **avant** de défendre
  la sienne, et ne garder de la sienne que ce que l'autre n'a pas — ici, le
  câblage du héros, que personne n'avait fait.

## 2026-08-27 — Une description inventée coûte plus cher qu'une case vide

- **Ce que j'ai fait** : le 16 août, Hillary a montré ses modèles **en
  conversation**, sans envoyer de fichiers. J'ai noté leurs prix et leurs
  délais — exacts — et j'ai **rédigé une description pour chacun d'après ce que
  je croyais voir**. L'un d'eux est devenu « Ensemble Volants : haut court noué
  devant, manches à trois volants étagés, pantalon très évasé en jean ».
- **Ce que c'était vraiment** : la **robe de ville organza**, déjà au
  catalogue, décrite deux fois. Un vêtement que la maison ne coud pas a occupé
  une carte pendant **onze jours**, avec « Photo sur WhatsApp », et un client
  aurait pu le commander.
- **Ce qui l'a révélé, et qu'il fallait regarder plus tôt** : les **six prix
  étaient identiques** à ceux d'une fiche existante, au franc et au centime
  près. Deux vêtements différents qui coûtent exactement pareil en normal, en
  express, en francs, en euros et en dollars, ça n'arrive pas.
- ⚠️ **La règle** : on peut noter un prix entendu, un délai entendu, un nom
  entendu. **On ne rédige pas la description d'un vêtement qu'on n'a pas vu en
  fichier.** Une fiche sans description attend ; une fiche mal décrite ment, et
  elle ment avec l'autorité du catalogue.
- ⚠️ **Le garde-fou qui manquait** : à la création d'une fiche, comparer ses
  prix à ceux des fiches existantes. Un jeu de six valeurs qui se répète est un
  doublon jusqu'à preuve du contraire.
- **Ce qui a permis de trancher** : l'**empreinte au pixel** de la photo,
  mesurée les deux fois où elle est arrivée (25 et 27 août) — identique au dos
  d'une pièce déjà en ligne. Mesurer une image au lieu de la reconnaître à
  l'œil, c'est ce qui transforme un soupçon en preuve.

## 2026-08-28 — Une consigne dans un prompt n'est pas un contrôle

- **Le cas** : l'agent WhatsApp doit ne jamais inventer un prix. Le prompt le dit
  en majuscules, trois fois, avec la raison. Ça ne suffit pas : un modèle qui
  parle argent finit par arrondir, et il le fait avec le même aplomb que quand
  il a raison.
- ⚠️ **La règle** : tout ce qui coûte de l'argent au client se vérifie **en
  code, après la génération, avant l'envoi**. Le prompt oriente, il ne garantit
  pas. Un garde-fou qui relit la réponse et bloque l'envoi est la seule chose
  qui transforme une démonstration en produit livrable.
- **Ce que ça change en pratique** : quand le garde-fou bloque, le client reçoit
  une phrase honnête (« je préfère vous confirmer ce point exactement ») et le
  patron reçoit **le message que l'agent allait envoyer, en entier**. On ne perd
  pas la vente, on la passe à un humain.

## 2026-08-28 — Un contrôle de prix doit ATTACHER le montant à l'article

- **Le premier jet** vérifiait qu'un montant était atteignable en additionnant
  des articles de la carte. Il acceptait « le tilapia braisé est à 4 500 F »,
  parce que 4 500 = 3 000 + 1 500 : une addition possible, pour un prix faux.
- ⛔ **Mesuré, et c'est le chiffre qui a tout décidé** : sur la carte d'Au
  Braisé d'Or, **90 % des montants ronds** entre 100 et 18 000 F sont
  atteignables en six articles ou moins. Chez Hillary, dont les prix sont gros
  et espacés, **2 %**. Un contrôle qui accepte 90 % des valeurs ne contrôle rien
  — et il paraissait excellent tant qu'on ne le mesurait que chez Hillary.
- ⚠️ **La correction** : chaque montant est **attaché au nom d'article le plus
  proche dans sa phrase**, et vérifié contre CET article. Un total n'est admis
  que s'il combine **au moins deux** articles nommés — sinon « le cappuccino est
  à 600 F » passerait, 600 F étant le prix du yaourt cité juste après.
- ⚠️ **Les mots qui reconnaissent un article sont CALCULÉS depuis les données** :
  un mot ne désigne un plat que s'il n'appartient qu'à lui dans toute la carte
  (« tilapia », « gombo » oui ; « sauce », « poulet » non). Le jour où la maison
  ajoute un second plat au tilapia, le mot cesse tout seul d'être distinctif.

## 2026-08-28 — Un nombre qui SUIT un nom n'est pas une quantité

- « Trois yaourts, ça fait 1 800 F » est vrai (3 × 600). Pour l'accepter, le
  garde-fou lit la quantité écrite devant le nom.
- ⛔ **Le piège** : « la glace **4 boules** est à 3 000 F ». Le 4 compte des
  boules, pas des glaces. Lu comme une quantité, il valide 3 × 1 000 = 3 000 F
  pour un barème qui s'arrête à 2 500 F — exactement l'erreur d'encaissement
  que les paliers avaient été créés pour empêcher le 26 août.
- ⚠️ **La règle** : une quantité se lit **avant** le nom, dans les quelques
  caractères qui le précèdent. Un nombre placé après compte autre chose.

## 2026-08-28 — Un chemin de sortie oublié ne se voit que si un contrôle l'emprunte

- **Le défaut** : le service ne prévenait la maison que lorsqu'il y avait une
  **escalade**. Une commande confirmée était donc enregistrée, récapitulée au
  client… et **personne au restaurant ne l'apprenait**. Un client serait venu
  chercher un plat que personne n'avait mis sur le feu.
- **Comment il est sorti** : un contrôle qui disait « la maison reçoit la
  commande », écrit parce que la liste des contrôles suivait les chemins et non
  le code. Aucune relecture ne l'avait vu — les deux branches (`escalades`,
  `commandes`) sont voisines de trois lignes et l'une avait l'air de couvrir
  l'autre.
- ⚠️ **La règle** : lister les SORTIES d'un service (répondre, prévenir,
  enregistrer, se taire) et écrire un contrôle par sortie, avant de lire le
  code. Un contrôle par fonction rate ce qu'un contrôle par chemin trouve.

## 2026-08-28 — Lire le fichier qui fait autorité, la preuve est venue le jour même

- Le kit WhatsApp ne recopie aucun catalogue : il **lit** `carte.ts` et le
  tableau `PIECES` de la vitrine d'Hillary.
- **La démonstration, non provoquée** : pendant la session, `main` a avancé de
  deux commits, dont un qui **retirait « Ensemble Volants »** du fichier
  d'Hillary. Après la fusion, l'agent est passé de 20 à 19 pièces **sans une
  ligne modifiée**, et les 146 contrôles sont restés verts.
- ⚠️ **Pourquoi les contrôles ont tenu** : aucun ne dit « 20 pièces ». Ils
  **lisent les deux côtés** (le fichier et le catalogue) et les comparent. Un
  contrôle qui recopie un chiffre de la donnée devient faux le jour où la donnée
  change — c'est-à-dire précisément le jour où il devrait servir.

## 2026-08-28 — `git merge-tree` imprime le CONTENU : on lit son code de sortie

- **Le défaut** : `scripts/rapatrier.py` jugeait qu'une branche était en conflit
  en cherchant « CONFLICT » ou « <<<<<<< » dans la sortie de la forme ancienne
  de `git merge-tree`. Or cette forme **imprime le contenu fusionné des
  fichiers**. Toute branche portant ces mots quelque part était accusée.
- **Le cas réel** : la branche du Standard WhatsApp sortait `[conflits]` à cause
  d'un `ON CONFLICT(...) DO UPDATE` — l'**upsert SQLite** de `memoire.py` —
  alors que `main` en était l'**ancêtre direct** : la fusion était une simple
  avance rapide.
- ⚠️ **Le défaut vise précisément ce qu'il ne faut pas rater** : les seules
  branches qu'il accuse à tort sont celles qui parlent de git ou de SQLite,
  c'est-à-dire de l'outillage. Une branche saine écartée par le script chargé de
  ne rien perdre, c'est le pire endroit où mettre un faux positif.
- **Ce qui l'a borné** : avoir comparé l'ancien et le nouveau verdict **sur les
  21 branches** avant de corriger. Une seule était mal jugée. Mesurer l'ampleur
  d'un défaut avant de le réparer évite d'en faire un drame ou de le sous-estimer.
- ⚠️ **La règle** : quand un outil rend un **code de sortie**, on lit le code de
  sortie. `git merge-tree --write-tree` (git ≥ 2.38) rend 0 pour propre et 1 pour
  conflit : c'est un verdict. Chercher un mot dans un texte, c'est une lecture,
  et une lecture se trompe. Sur un git trop ancien, le script dit désormais
  « indécidable » au lieu d'inventer un verdict.

## 2026-08-29 — Un contrôle dans le mauvais contexte ne mesure pas ce qu'il croit

- **Contexte** : le QC d'Hillary refusait le déploiement sur un seul rouge —
  *« témoin muet : la page n'a pas glissé (3003 → 3000) »*. Le contrôle est
  celui du **défilement lissé** (est-ce qu'un saut extérieur, recherche du
  navigateur ou lecteur d'écran, survit au glissement).
- ⚠️ **Le site allait très bien.** Mesuré à côté, en contexte PC : la page
  passe de **3 000 à 4 032 px en 120 ms**, document de 12 369 px, moteur
  présent, `pointer:fine` vrai. Rien de cassé.
- ⛔ **Le contrôle tournait dans le contexte du TOUCHER** : `390 × 844`,
  `is_mobile`, `has_touch` — alors que son propre commentaire disait *« le
  moteur n'existe que sur pointeur fin : ici, en contexte PC »*. Deux
  conséquences, toutes deux silencieuses :
  1. le moteur maison ne s'allume que sur `pointer:fine`, **il n'était pas là** ;
  2. `mouse.move(700, 400)` vise x = 700 sur une page large de **390** : la
     molette tombait **hors de l'écran**.
- **Ce qui a sauvé la mise** : le **témoin**, ajouté le 25/08 pour une tout
  autre raison (« sans lui, il passerait aussi le jour où le moteur serait
  mort »). Il n'a pas dit « le site est cassé », il a dit **« je ne prouve
  rien »**. C'est exactement son travail, et c'est la différence entre un
  contrôle rouge et un contrôle inutile.
- **Leçon** : un contrôle hérite du contexte où il est **écrit**, pas de celui
  qu'il **décrit**. Tant qu'il est vert, personne ne vérifie qu'il regarde au
  bon endroit — et il peut être vert pour la mauvaise raison pendant des
  semaines.
- **À appliquer** : quand un contrôle dépend d'une condition d'environnement
  (pointeur fin, mouvement réduit, largeur), **il la vérifie et le dit** :
  `ok(fin, "le contrôle tourne bien sur pointeur fin")` est posé juste avant.
  Et un contrôle déplacé prend **son propre contexte**, il n'emprunte pas
  celui du bloc voisin.

## 2026-08-29 — Une date de déploiement ne prouve rien, les octets servis oui

- **Contexte** : vérifier le parc entier revenait à comparer, pour chaque
  site, la date du dernier déploiement Cloudflare à celle du dernier commit
  touchant son dossier. **Sept sites sur quinze ressortaient « en retard ».**
- **Faux dans les deux sens** : un commit peut ne toucher que le `CONTEXT.md`
  ou un outil, et un déploiement du même jour peut être antérieur au commit.
  Sur PISTE, la date disait « en retard » ; le site sert `plexmono` et ne sert
  plus `orbitron` : **il était à jour**.
- **Ce qui tranche** : télécharger la page et comparer son **corps** au fichier
  du dépôt. Un seul site était réellement en retard.
- ⚠️ **Cloudflare INJECTE une ligne dans le HTML servi** (Web Analytics,
  `challenge-platform`) sur les domaines qui ont l'analytique : la comparaison
  au MD5 échoue alors que les pages sont identiques. Retirer ces lignes avant
  de comparer — et **dire combien on en a retiré**, sinon on masque une vraie
  différence sous prétexte de nettoyage.
- **À appliquer** : `_outils/_verif_parc.py` (à poser dans les scripts) compare
  chaque site à sa source, pas à sa date.
