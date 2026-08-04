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

---

## 2026-08-04 — Quatre leçons de la V1 de PISTE (React, animation, argent)

- **Contexte** : construction de `piste/` (vitrine, questionnaire, calculateur,
  paiement, cockpit), 95 contrôles automatiques.

### 1. Le vert ne remplace pas l'œil, et cette fois ça se chiffre

**92 contrôles verts. Trois défauts réels dans l'image.** Les cinq repères du
héros n'étaient jamais visibles, la page glissait latéralement avant qu'on
arrive à la section concernée, et le tampon du barème était tranché net par le
bord de sa carte.

Aucun de ces trois n'est détectable par une assertion écrite à l'avance : il
faut **regarder les captures, section par section, en 390 et en 1440**. C'est la
deuxième fois que cette règle sauve une livraison (la première : six défauts sur
la vitrine Hillary, derrière 53 contrôles verts).

**Leçon : le contrôle automatique prouve que rien n'est cassé, pas que c'est
bien.** Et une fois le défaut vu, on ajoute le contrôle qui l'attrapera la
prochaine fois.

### 2. En SVG, un `transform` CSS n'ajoute rien à l'attribut : il l'efface

Un `<g transform="translate(x y)">` qui porte aussi une classe animée en CSS
perd sa position dès que la règle CSS s'applique. Les cinq repères retombaient
sur le coin haut-gauche du `viewBox`, donc hors cadre.

**Leçon : deux groupes, toujours.** L'extérieur POSE (attribut SVG),
l'intérieur ANIME (transform CSS). Ils ne peuvent pas cohabiter sur un même
élément.

### 3. Un élément animé en 3D pousse toute la page de côté

`perspective(700px) rotateY(-72deg)` sur une carte de 670 px donne une boîte de
**5 000 px de large** tant qu'elle est dans cet état. La page était pannable
latéralement sur téléphone, sans rien de visible pour l'expliquer, avant même
qu'on arrive à la section.

**Leçon : tout élément transformé en 3D vit dans un cadre `overflow-hidden`.**
Et le débordement horizontal se mesure **deux fois** : au chargement, et une
fois la page parcourue. Un même élément est inoffensif dans un état et coupable
dans l'autre.

Corollaire : **une animation signature doit se jouer à l'arrivée, pas au
chargement.** Une `animation` CSS posée sur une classe se joue hors écran, et
l'utilisateur qui descend trouve le geste déjà consommé. Ce sont des
`transition` pilotées par la classe de révélation.

### 4. Un identifiant que le client dicte ne se dérive pas de l'heure

Le code de commande prenait deux caractères dans l'horloge et deux au hasard :
1 024 possibilités par seconde. Le contrôle a sorti **400 codes tirés, 342
distincts**. Dans un cockpit qui fusionne par code, un doublon fait disparaître
une commande, donc un client payé et jamais livré.

**Leçon : tirer au hasard, dimensionner sur le volume réel** (six caractères,
un milliard de combinaisons pour dix commandes par jour), **et rendre la
collision inoffensive** — la fusion exige désormais le code ET l'email. Le
hasard se prend dans `crypto.getRandomValues`, en ne gardant que 5 bits par
octet : 256 n'est pas un multiple de 32, et un modulo naïf ferait sortir les
premières lettres plus souvent.

Deux contrôles statistiques ont dû être recalibrés : **écrits plus serrés que
le hasard ne le permet, ils clignotent** et on finit par ne plus les croire.

### 5. Un numéro de paiement non confirmé ne s'affiche jamais

Le produit était prêt avant les numéros Mobile Money de NEBULA. Plutôt que de
poser un numéro « provisoire », la page dit la vérité — *le numéro vous est
donné sur WhatsApp à l'instant où votre commande arrive* — et un script
`_predeploy.js` **refuse la mise en ligne** tant que le drapeau `aConfirmer`
est levé.

**Leçon : quand une donnée manquante touche à l'argent, on livre le parcours
complet et on bloque la publication, jamais l'inverse.** Un tarif faux se paie
à chaque commande ; un numéro de paiement faux se paie une seule fois, mais
c'est chez un inconnu.
