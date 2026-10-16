# 2026-10-16 · MA LETTRE À… : le nom, la page d'accueil, et la reprise après la coupure

Suite de `2026-10-16-lepli-plume.md` (la plume et les 27 occasions, le matin).

## 1 · Le nom

Mongazi : « LE PLI c'est un peu bizarre, on doit pouvoir comprendre dès qu'on le
lit ou qu'on le dit ». Tableau des candidats (LETTRE SCELLÉE recommandée, MA
LETTRE, L'ENVELOPPE, OUVRE-MOI, LETTRE À L'HEURE). Mongazi : « ma lettre j'aime
bien », puis, sur le nom lui-même, **MA LETTRE À…** : le seul qui se
personnalise tout seul (« Ma lettre à Afi », « Ma lettre à papa », « Ma lettre à
la famille Dossou » pour un deuil). « Donc on retient ça. »
- Aucune application ne s'appelle exactement « Ma Lettre » (Lettre.app et Lettrs
  sont les plus proches). `malettre.com` est pris ; `.app`, `.online`, `.bj`,
  `.ci` ne répondaient pas.
- Renommage `lepli/` → `malettre/` le jour même (commit `5af692d`) : schéma,
  fonctions `malettre-*`, clés `malettre:*`, `MALETTRE_DONNEES`, textes.
- Au passage, **le Coffret ne promet plus « la livraison WhatsApp à l'heure
  choisie »** (rien ne la faisait, et c'est contraire à « on n'écrit jamais à
  la personne qui reçoit »), prix inchangé, et il **contient** ses 20 photos :
  le formulaire plafonnait à 3 pour tout le monde alors que le serveur en
  gardait 20.
- Correctif des élisions de la plume (« je ne te en veux ») dans `plume.ts`.

## 2 · La page d'accueil

Demande de Mongazi : la page où viennent les clients, présentation + exemples
de lettres d'Africains inventés, « totalement différente » des vitrines déjà
faites, « nouvelle génération ». La vidéo de référence promise : « oublie la
vidéo de référence finalement ». Puis : « la zone de chargement dès qu'on lance
le lien du site doit être une lettre avec un nœud qui se déplie, avec by NEBULA
Agency marqué un peu plus bas ».

Construite sur la phrase *une lettre, c'est une feuille qui devient une
enveloppe scellée, puis qui redevient une feuille entre les mains de
quelqu'un* : chargement lettre nouée, héros où l'on tape le prénom, scène 3D
épinglée (pli, enveloppe, cachet, 23:57, minuit, bris), six exemples écrits par
la vraie plume (Kofi à Afi, Afi à papa, Robert à Zara, Aminata à maman, Sèna à
Grâce, Ismaël à Fatou), la plume, le casier des 27 occasions, le seuil en vrai,
les timbres, les promesses, la page blanche. Aucune bibliothèque.

## 3 · La coupure

Le PC s'est éteint à 15 h 54, pendant la vérification du chargement. Reprise :
« continue où tu en étais et veille à ce que rien ne soit cassé ou manquant ».
- Contrôles du produit relancés : **212** et **231** verts, rien de cassé.
- La dernière capture (« nœud noué ») montrait un nœud déjà défait :
  `clock.install()` de Playwright **laisse couler le temps**. Rejouée en
  figeant les transitions (`getAnimations()`, `pause()`, `currentTime`) : le
  nœud est là, la séquence est juste.
- Manquants trouvés et faits : le **contrôle de la page** (prévu au plan,
  jamais écrit), l'**image de partage** (annoncée par la page, absente du
  disque), le **lien de retrait** (le pied promettait le retrait sans moyen de
  nous joindre : `wa.me/22996740732`, le numéro de `merci.html`), la **vague 3**
  (`_dist.py`, `404.html`, `_headers`, `robots.txt`).

## 4 · Ce que le contrôle a trouvé

1. ⛔ **Au téléphone, la page était dézoomée** : l'`input` du prénom (Pinyon
   30 px, `size` 20 par défaut) poussait la page à **597 px**, puis les timbres
   agrandis avant leur frappe à 414 px. Visible sur une capture d'avant la
   coupure (le champ coupé à droite), et **invisible au contrôle** qui comparait
   `scrollWidth` à `innerWidth`, lequel grandit avec le défaut. Corrigé, et le
   contrôle compare à la largeur demandée.
2. ⛔ **En mouvement réduit**, billets et timbres restaient invisibles jusqu'au
   défilement (repli moins spécifique que leurs règles).
3. ⚠️ **La sonde de contraste mentait au téléphone** : la capture d'élément
   refaisait défiler la page, le fond était mesuré une section à côté. Capture
   de l'écran puis découpe, et **deux témoins** (gris sur gris doit échouer,
   le papier du bouton de la barre doit être lu).
4. La marque de la barre faisait 35 px de haut (cible sous 44 px).

Résultat : **78 contrôles verts** (`_qc_accueil.py`), 60 images/s en médiane
dans la scène avec un processeur ×4. Planches 390 et 1440 regardées.

## 5 · Rien n'est en ligne

La page vend des lettres payantes et la caisse n'est pas branchée : la mise en
ligne attend le feu vert de Mongazi. `_dist.py` est prêt.

## 6 · Ensuite

La vidéo publicitaire (Mongazi : « une fois fini on va passer à la vidéo
publicitaire, tu me poseras des questions »).

## Fichiers touchés

- `malettre/_accueil_src.html`, `index.html`, `exemples/*.html`, `exemples.json`,
  `favicon.svg`, `og.jpg` (neufs ou générés)
- `malettre/_build_accueil.py`, `_voir_accueil.py`, `_qc_accueil.py`, `_og.py`,
  `_dist.py` (neufs)
- `malettre/README.md`, `malettre/CONTEXT.md` (neuf, bloc de `CLAUDE.md`
  recopié intégralement)
- `malettre/supabase/functions/_shared/plume.ts`, `malettre/_qc_caisse.mjs`
  (élisions)
- `CLAUDE.md` (bloc réécrit en résumé : 91 489 → 81 300 caractères)
- `_memoire/decisions.md`, `_memoire/lecons.md`, `_memoire/REPRENDRE-ICI.md`,
  `_memoire/journal/2026-10-16-journal.md`,
  `_memoire/apprentissages/2026-10-16-qc-telephone-dezoom.md`
