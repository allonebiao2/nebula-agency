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
