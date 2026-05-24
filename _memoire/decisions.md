# Décisions — Nebula Agency

> Journal des décisions structurantes prises sur le projet.
> Chaque décision : date, contexte, choix, raison.

---

## Format

```
## YYYY-MM-DD — Titre court de la décision

- **Contexte** : pourquoi la question s'est posée
- **Décision** : ce qui a été choisi
- **Raison** : pourquoi ce choix
- **Alternatives écartées** : ce qu'on n'a pas pris, et pourquoi
- **Conséquences** : ce que ça implique pour la suite
```

---

## 2026-05-11 — Mise en place de la structure du repo

- **Contexte** : Plusieurs clients en parallèle, besoin d'organisation claire.
- **Décision** : Structure `clients/0X-nom/` + `_memoire/` + `_templates/`.
- **Raison** : Permettre à Claude de retrouver le contexte d'un client en un coup d'œil et capitaliser les apprentissages.
- **Alternatives écartées** : Un repo par client (trop dispersé pour un solo).
- **Conséquences** : Chaque nouveau client suit le même schéma, mémoire transverse centralisée.

---

## 2026-05-14 — Versioning fichiers vitrine : un seul fichier actif

- **Contexte** : Accumulation de fichiers `nebula_agency_vX.html` dans le repo crée de la confusion sur quel fichier est la version active.
- **Décision** : À chaque mise à jour d'un fichier versionné, supprimer l'ancien (`git rm`) avant de créer le nouveau. L'historique git suffit pour retrouver les versions antérieures.
- **Raison** : Repo propre, pas d'ambiguïté sur la version live, clients ne risquent pas d'être servis sur une ancienne version.
- **Alternatives écartées** : Garder tous les vX en parallèle (poubelle qui grossit), branches git par version (overkill pour un solo).
- **Conséquences** : Workflow appliqué aux vitrines `00-nebula-agency/` et `/clients/`. v7 supprimé, v8 devient version active.

---

## 2026-05-14 — Pricing récurrent : setup + 10k FCFA/mois

- **Contexte** : Maintenance, hébergement, modifications répétées des vitrines clients étaient inclus dans un prix one-shot — modèle non soutenable.
- **Décision** : Introduire un abonnement mensuel **10 000 FCFA/mois** en plus du setup pour les services Vitrine Digitale (70k setup) et Catalogue Digital (50k setup). Inclut : hébergement + sécurité + modifications illimitées 24h/24.
- **Raison** : Revenu récurrent prévisible, justifie le support continu, aligné sur la norme SaaS, retient les clients dans l'écosystème NEBULA.
- **Alternatives écartées** : Prix forfaitaire one-shot (épuisant à maintenir), facturation horaire pour chaque modification (friction).
- **Conséquences** : Argumentaire de vente axé sur "24h/24" et "modifications illimitées". Les vitrines déjà livrées (Jocelyne, Cédène, Abakar) restent sur l'ancien modèle ; nouveau modèle pour les prochains clients.

---

## 2026-05-14 — FedaPay devient le provider de paiement standard

- **Contexte** : Besoin d'un moyen de paiement intégré dans les vitrines pour transformer "vitrine de présentation" en "vitrine qui vend".
- **Décision** : Adopter FedaPay comme provider de paiement Mobile Money (Moov, MTN, Wave) + cartes pour toutes les vitrines NEBULA. Compte principal + sous-comptes par client.
- **Raison** : Provider local Afrique de l'Ouest, supporte tous les Mobile Money utilisés au Bénin, dashboard MyFeda, notifications natives, sous-comptes natifs pour facturation par client.
- **Alternatives écartées** : Stripe (pas adapté au Mobile Money local), CinetPay (pas testé), intégration manuelle Moov/MTN (trop de friction).
- **Conséquences** : Clé secrète `sk_live_*` jamais dans le HTML (uniquement `.env` local + n8n côté serveur). Clé publique `pk_live_*` utilisable dans les vitrines. Triple confirmation paiement : WhatsApp + MyFeda + Email.

---

## 2026-05-18 — Numéro WhatsApp : format Bénin 10 chiffres conservé

- **Contexte** : un brief demandait de passer le numéro à `wa.me/22967975626`.
- **Décision** : conserver `2290167975626` (229 + 01 67 97 56 26) sur toutes les pages.
- **Raison** : `22967975626` est l'ancien format béninois à 8 chiffres, abandonné
  depuis le passage du Bénin à la numérotation 10 chiffres (préfixe `01`) en 2023 ;
  il risque de ne plus router vers WhatsApp. Confirmé avec Mongazi.
- **Alternatives écartées** : appliquer le numéro du brief tel quel (risque de casser
  tout le tunnel de contact client).
- **Conséquences** : règle « lien WhatsApp = confirmation obligatoire » respectée ;
  toujours vérifier le format 10 chiffres pour les futurs clients.

---

## 2026-05-18 — Architecture audio des vitrines (Web Audio API + délégation)

- **Contexte** : l'ancien audio par page ne fonctionnait pas de façon fiable.
- **Décision** : module unifié `LCAudio` (Web Audio API pure, zéro fichier externe) :
  sons générés par oscillateurs, musique d'ambiance jazz générative, déblocage de
  l'`AudioContext` au 1er geste utilisateur, câblage des effets par **délégation
  d'événements** sur `document`.
- **Raison** : zéro CDN (règle NEBULA), un seul bloc réutilisable sur les 4 pages,
  la délégation évite de modifier chaque écouteur existant.
- **Alternatives écartées** : MP3 base64 (lourd), librairie audio externe (CDN interdit),
  brancher l'audio écouteur par écouteur (fragile, verbeux).
- **Conséquences** : pour ajouter un son, étendre l'objet `SFX` ; l'ancien bouton
  audio est masqué en CSS (code inerte conservé pour robustesse).

---

## 2026-05-18 — Catalogue 3 marques : enrichir le menu existant

- **Contexte** : un brief demandait un panneau catalogue latéral montrant
  l'architecture des 3 marques sur `ina-luxury.html`.
- **Décision** : enrichir le menu accordéon **déjà en place** (compteurs de produits +
  sections Luxury Skin Clinic et Cozy en liens sortants) plutôt que créer un 2ᵉ
  panneau slide-over indépendant.
- **Raison** : éviter un refactor risqué du layout ; le menu existant remplit déjà
  le rôle ; pas de redondance avec le bouton « Catalogue » existant.
- **Alternatives écartées** : panneau slide-over séparé (refactor du layout `.layout`).
- **Conséquences** : navigation INA Luxury dans la page, marques Clinic/Cozy en liens
  vers leurs pages.

---

## 2026-05-18 — Intégration FedaPay sur les vitrines : via n8n, pas de SDK client

- **Contexte** : ajouter le paiement direct (Mobile Money / carte) sur les vitrines
  clients, en complément de la commande WhatsApp. Compte FedaPay en cours de
  vérification.
- **Décision** : la vitrine n'intègre **aucun SDK FedaPay ni script CDN**. Flux :
  vitrine → webhook n8n → n8n crée la transaction FedaPay avec `sk_live_*`
  (serveur) → renvoie l'URL de paiement → la vitrine redirige vers la page
  sécurisée FedaPay.
- **Raison** : la clé secrète `sk_live_*` ne doit jamais être côté client
  (règle `CLAUDE.md`) ; éviter une dépendance CDN ; n8n est déjà le backend NEBULA.
- **Alternatives écartées** : `checkout.js` de FedaPay (charge un script CDN +
  expose la logique côté client) ; liens de paiement statiques (montant du panier
  dynamique, incompatible).
- **Conséquences** : intégration réelle bloquée jusqu'à la vérification du compte
  (sous-compte client + workflow n8n + test d'un paiement réel). Préparation
  documentée dans `clients/04-luxury-skin-clinic/CONTEXT.md`.

---

## 2026-05-19 — Corrections critiques v3 (logo, audio mobile, stock, réseaux)

- **Contexte** : série de corrections critiques sur Luxury Club 229 (logo de
  chargement, audio mobile bloqué, doublons réseaux, stock capillaires).
- **Décisions** :
  - Splash screen sur les 4 pages : logo Luxury Group + bouton « Entrer dans
    l'univers » qui débloque l'audio (geste explicite obligatoire sur mobile),
    flag `sessionStorage`. Le splash ne se ferme plus automatiquement.
  - Emblèmes du hub (I/L/C) → texte stylisé CSS par marque (les dossiers
    `assets/images/logo/<marque>/` sont vides).
  - Capillaires : prix fixés, 6 produits mis en rupture de stock (badge rouge +
    bouton « M'avertir du retour » WhatsApp).
  - Une seule barre réseaux : la barre animée `lc-social` ; l'ancienne barre
    statique du hub est supprimée.
- **Raison** : sur mobile l'audio exige un geste utilisateur explicite ; éviter
  les doublons d'UI ; refléter l'état réel du stock.
- **Conséquences** : audio à tester sur un vrai téléphone. Qualité des images
  produits non récupérable (originaux compressés le 18/05) sans re-fourniture.

---

## 2026-05-19 — Audit conversion : panier + questionnaires multi-étapes

- **Contexte** : le site n'a pas d'inscription ; audit des vrais parcours de
  conversion (panier→WhatsApp, questionnaires clinique, modal règlement).
- **Décisions** :
  - Panier : vignette photo produit, boutons quantité agrandis (tactile mobile),
    bouton « Vider le panier », ligne zone de livraison dans le message WhatsApp.
  - Questionnaires clinique : refonte en **multi-étapes** (1 section/écran,
    barre de progression, Précédent/Suivant), validation **inline**, radios
    requis vérifiés, sauvegarde des réponses en `localStorage`.
  - Règlement clinique : déjà affiché 1×/session — inchangé.
- **Raison** : un questionnaire de 25 champs en une seule page provoque l'abandon ;
  le multi-étapes réduit la friction sans rien supprimer.
- **Alternatives écartées** : supprimer des questions (décision de contenu qui
  revient à Gloria, pas un choix technique).
- **Conséquences** : la réduction du nombre de questions reste à valider avec
  Gloria si elle souhaite un questionnaire plus court.

---

## 2026-05-19 — Navigation automatique + logos + fix empilement catalogue

- **Contexte** : navigation jugée trop lente (bouton « Entrer » obligatoire,
  texte d'accueil lent) ; logos à intégrer ; panneau catalogue invisible sur mobile.
- **Décisions** :
  - Suppression du bouton « Entrer dans l'univers » : l'entrée dans chaque
    compartiment est **automatique** à la fin du texte d'accueil (un clic le saute).
    Le son se débloque désormais au premier tap réel sur la page.
  - Nouveau logo Luxury Club 229 (« LC » or sur noir, contient déjà le nom)
    affiché en plein sur l'accueil et les welcome-gates ; logos Cozy et Clinique
    dans les emblèmes du hub ; INA Luxury reste en logo CSS (aucune image fournie).
  - Particules en `z-index:-1` et `.layout` sans `z-index` : corrige le bug où le
    panneau catalogue (menu `position:fixed`) restait sous le scrim sur mobile.
- **Raison** : un client part si l'entrée prend trop de temps ; un panneau
  catalogue invisible sur mobile = fonctionnalité cassée.
- **Conséquences** : l'audio mobile démarre à la 1ʳᵉ interaction réelle (plus
  d'écran dédié au déblocage du son) — compromis vitesse assumé.

---

## 2026-05-19 — Catalogue global omniprésent

- **Contexte** : le catalogue n'existait que sur `ina-luxury` ; besoin d'y accéder
  depuis n'importe quelle page.
- **Décision** : composant « Catalogue global » autonome (bouton fixe bas-gauche
  + panneau coulissant + scrim) montrant l'architecture des 3 marques, injecté
  sur `index`, `cozy` et `luxury-skin-clinic`. `ina-luxury` garde son panneau
  latéral intégré (filtrage en direct) — pas de double catalogue.
- **Raison** : navigation cohérente et omniprésente sans casser la fonctionnalité
  de filtrage propre à `ina-luxury`.
- **Conséquences** : les éléments du panneau global sont des liens vers les pages
  marques (pas de filtrage en direct hors `ina-luxury`).

---

## 2026-05-20 — Enrichissement contenu fiches : champ `det` unifié

- **Contexte** : les fiches produits / services affichaient une description
  courte (`d`) et un INCI brut, sans hiérarchie ni progression dans le contenu
  de l'accordéon. Le client (Gloria) a fourni un dossier complet de descriptions
  longues structurées pour les 30+ produits et 11 services.
- **Décision** : ajouter un champ optionnel `det` (string HTML) à chaque
  produit / service. Quand `det` est présent, le rendu de l'accordéon
  « En savoir plus » l'utilise prioritairement ; sinon fallback sur l'ancienne
  construction (`plus + use + warn` pour `ina-luxury`, `plus` pour `cozy`).
  Pour le clinic, le `det` est injecté en tête du contenu de l'accordéon
  « Le protocole en détail », avant le protocole structuré et le post-soin.
- **Raison** : un champ optionnel n'impose pas d'enrichir toutes les fiches en
  une seule passe (idéal pour livrer par vagues), garde les fiches non
  enrichies fonctionnelles, et concentre la richesse éditoriale au même
  endroit que les actifs déjà existants. Classes CSS partagées (`det-h`,
  `det-p`, `det-ul`, `det-phase`, `det-warn`) → cohérence visuelle.
- **Alternatives écartées** : remplacer entièrement le champ `d` par un objet
  riche (casserait les cartes et la liste catalogue) ; créer un fichier
  externe par fiche (incompatible avec la règle « tout en HTML pur sans CDN »).
- **Conséquences** : 43 fiches enrichies sur 54 (24/35 INA Luxury, 8/8 Cozy,
  11/11 Clinic). Les 11 fiches restantes (Beauty Bars sans photo et capillaires
  en rupture) gardent l'ancien rendu jusqu'au retour du stock / des photos.

---

## 2026-05-20 — Cozy : refonte catégories Hygiène intime / SELFCARE / Raffermissants

- **Contexte** : architecture Cozy initiale (Hygiène intime, Soin du corps,
  Bien-être) jugée peu lisible par Gloria. Mauvaise classification du Gel
  Nettoyant Intime mélangé à l'Huile Intime (qui est en fait un produit SELFCARE
  sensoriel, pas un produit d'hygiène).
- **Décision** :
  - `intime` (Hygiène intime) : 1 seul produit — Gel Nettoyant Intime.
  - `selfcare` (SELFCARE) : 4 produits — Huile Intime, Crème Corps Parfumée,
    Crème Mains, Baume Pailleté.
  - `raffermissant` (Produits raffermissants) : 2 produits — Maca Cream,
    Le Boost Fermeté.
  - Synchronisé dans les ARCH catalogue des 4 pages (cozy, ina-luxury,
    luxury-skin-clinic, index).
- **Raison** : « Hygiène intime » au sens strict = soin lavant intime. Les autres
  produits sont du soin-plaisir (selfcare). La fermeté mérite sa propre catégorie
  parce que c'est l'argument commercial premium de Cozy.
- **Conséquences** : Huile Éclat Suprême, initialement classée Cozy, transférée
  à INA Luxury Corps/Huile (elle n'appartenait pas à la gamme Cozy).

---

## 2026-05-20 — INA Luxury Enfant : fusion Crème Hydratante + Crème Apaisante

- **Contexte** : sous-catégories enfant initialement séparées en
  « Crème Hydratante » et « Crème Apaisante ». Or Crème Douceur d'Aloe ET
  Crème Dermo-Apaisante sont chacune **à la fois** hydratantes et apaisantes —
  la distinction n'apporte rien à l'utilisateur.
- **Décision** : fusionner en une seule sous-catégorie `creme` (label « Crème »).
  Les 2 produits s'affichent ensemble dans cette catégorie unique.
- **Raison** : un menu plus court (3 sous-catégories au lieu de 4) est plus
  lisible. La granularité fine est de toute façon expliquée dans la description
  de chaque produit.
- **Conséquences** : ARCH catalogue synchronisé dans les 4 pages + docs
  internes (`CONTEXT.md`, `gloria-infos.md`).

---

## 2026-05-20 — Services Clinic : champ `by` pour surcharger le praticien

- **Contexte** : tous les soins Luxury Skin Clinic affichaient « Réalisé par
  Mme Sabrina — Diplômée » en bas de carte. Le Luxury Massage n'est pas réalisé
  par Mme Sabrina mais par l'esthéticienne.
- **Décision** : ajouter un champ optionnel `by` sur les services. Le rendu
  utilise `s.by` s'il existe, sinon fallback sur « Mme Sabrina — Diplômée ».
- **Raison** : pattern propre et extensible (massothérapeute, coiffeur, etc.)
  sans casser les 10 soins par défaut.
- **Conséquences** : Luxury Massage seul soin avec override pour l'instant
  (`by:"l'esthéticienne"`). Réutilisable pour futurs soins.

---

## 2026-05-20 — Audio mobile : démarrage au 1er geste (et pas au 1er click)

- **Contexte** : sur mobile, la musique d'ambiance ne démarrait qu'au premier
  `click`. Un utilisateur qui scrollait ou tappait sans relâcher n'entendait
  jamais rien. Plainte directe de Mongazi : « On n'étend absolument rien sur
  la version mobile ».
- **Décision** : refonte du hook de déblocage `_kick()` qui écoute désormais
  `touchstart`, `touchend`, `pointerdown`, `click`, `keydown`, `scroll`. Au
  premier événement quel qu'il soit, il fait ensure + resume + musicStart +
  marque le bouton mute en playing. Volumes mobile augmentés
  (master 0.9 → 1.0, musique 0.16 → 0.24, ramp 4 s → 2.2 s).
- **Raison** : iOS Safari bloque l'autoplay sans interaction utilisateur,
  c'est une règle système non contournable. La meilleure réponse possible est
  donc de **rendre le déblocage le plus sensible possible** au moindre geste,
  pas d'essayer de le bypasser.
- **Alternatives écartées** : bouton « Activer le son » dédié au splash
  (lent, friction supplémentaire, déjà supprimé en session précédente) ;
  Howler/Tone.js (interdit par règle NEBULA « pas de CDN »).
- **Conséquences** : appliqué aux 4 pages. Test mobile recommandé sur un
  vrai téléphone pour vérifier que le mode silencieux iOS n'empêche pas
  Web Audio (rien à faire côté code dans ce cas).

---

## 2026-05-20 — Cosmétique : descriptions EXACTES + photos uniformes

- **Contexte** : Gloria a indiqué (via Mongazi) qu'en cosmétique, la précision
  des termes est critique pour la conformité réglementaire et la promesse au
  client. Les descriptions doivent être **exactement** celles qu'elle a fournies,
  pas reformulées. En parallèle, certaines photos étaient rognées par
  `object-fit:cover` — il fallait que **tout** le produit soit visible.
- **Décision** :
  - **Descriptions** : conserver le texte source mot pour mot, avec les listes
    à puces préservées (jamais convertir une liste à puces en phrase
    combinée pour les produits cosmétiques). Sections dans l'ordre exact du
    brief : Description produit → Résultats attendus → Caractéristiques produit
    → Conseils d'utilisation → Actifs clés.
  - **Photos** : `object-fit:contain` + `padding:8px` + fond dégradé thématique
    sur `.card-photo` (noir/anthracite pour ina-luxury, rose pâle pour cozy).
    `aspect-ratio:4/3` conservé pour garder la même hauteur partout. Grille
    et disposition générale strictement inchangées.
- **Raison** : la cosmétique a un vocabulaire réglementé (« aide à »,
  « visiblement », pas de promesses thérapeutiques). Reformuler =
  risque de mal traduire. Photos rognées = client ne voit pas le packaging
  complet, frein à l'achat.
- **Alternatives écartées** : laisser cover et redimensionner les sources
  (lourd et non scalable) ; convertir tous les sources en format 4:3 normalisé
  (perte de qualité, impossible sans accès aux originaux non compressés).
- **Conséquences** : les 36 fiches enrichies pré-restauration (vagues 1-9)
  ont du texte reformulé. Si Gloria veut la même fidélité absolue dessus,
  elle doit re-poster les textes source un par un.

---

## 2026-05-20 — INA Luxury : détourage fonds blancs (produits sur fond noir luxe)

- **Contexte** : Gloria voulait que les produits INA Luxury fondent dans le
  fond noir doré de la marque. Or 33 des 34 images base64 étaient en JPEG
  avec fond blanc → impossible à effacer en CSS seul (aucun `mix-blend-mode`
  ne supprime un fond blanc d'un JPEG sur un fond noir).
- **Décision** : détourage automatique des fonds blancs via script Python
  Pillow (`_detoure.py` — script transient, supprimé après exécution).
  Pour chaque image : flood-fill depuis les 4 coins avec seuil de tolérance
  pour ne supprimer QUE le fond connecté (pas les zones blanches internes
  au produit). Léger feathering Gaussien (0.6px) pour adoucir les bords.
  Conversion JPEG → PNG avec alpha transparent. 31 images traitées, 3 skip
  (déjà sans fond blanc, conservées telles quelles).
- **Raison** : seul moyen propre d'avoir des produits réellement détourés
  sur fond noir. Les alternatives CSS (mix-blend-mode multiply/screen/lighten
  + fond noir) sont toutes mathématiquement inadaptées à ce cas. Demander
  à Gloria de re-fournir des PNG transparents = friction inutile alors
  qu'on a déjà ses images de bonne qualité.
- **Alternatives écartées** :
  - `mix-blend-mode: multiply` sur fond noir → tout devient noir (le multiply
    avec 0 = 0)
  - `mix-blend-mode: screen` ou `lighten` → le blanc reste blanc, n'efface
    rien (visible sur fond noir)
  - Demander à Gloria des PNG transparents → friction supplémentaire
- **Conséquences** :
  - Poids du fichier ina-luxury.html passe de ~3 Mo à ~9 Mo (PNG transparent
    > JPEG compressé).
  - CSS `.card-photo` : background gradient radial noir profond + pseudo
    `::after` vignette + filter `drop-shadow` noir + halo or léger.
  - Si chargement mobile devient trop lent, re-optimiser via pngquant
    (palette 256 couleurs) ou re-réduire les dimensions de 900 px à 700 px.
  - Pour les futurs ajouts d'images : refournir détourées en PNG si possible,
    sinon relancer le script de détourage automatique.

---

## 2026-05-21 — Restauration massive des textes EXACTS (briefs Gloria)

- **Contexte** : Gloria, exigeante sur la précision réglementaire du vocabulaire
  cosmétique, a re-posté en clair les briefs sources de quasiment toutes les
  fiches. Les versions paraphrasées des vagues 1-9 ne lui convenaient pas.
- **Décision** : restaurer **mot pour mot** le texte source dans le champ `det`
  de chaque fiche, en respectant strictement :
  - les sections dans l'ordre exact du brief (Description → Résultats par
    phases → Caractéristiques → Conseils → Avertissements / Actifs clés) ;
  - les listes à puces telles quelles (jamais converties en phrases) ;
  - les emojis de titres de section du brief (✨ 💎 🌿 🧖🏽‍♀️ 📅 🧴 🌫️…) ;
  - les listes ordonnées `<ol class="det-ul">` pour les étapes numérotées
    (protocoles de soin, questionnaires).
- **Raison** : en cosmétique, la formulation est réglementée (« aide à »,
  « contribue à », « visiblement » — jamais de promesse thérapeutique).
  Reparaphraser = risque de mal traduire une allégation. Le texte de Gloria
  fait foi.
- **Conséquences** :
  - 50/54 fiches en texte EXACT (INA Luxury 32/36, Cozy 7/7, Clinic 11/11).
  - Règlement intérieur clinique étendu de 6 à 7 sections (modal `reglScrim`).
  - Restent 4 fiches sans brief : Crème Lait de Chèvre + 6 capillaires en
    rupture (à restaurer dès réception des briefs).
  - **Process pour la suite** : toute nouvelle fiche ou correction de fiche
    cosmétique doit partir du texte source fourni par Gloria, jamais d'une
    reformulation. Voir [[feedback_contenu-manquant]].

---

## 2026-05-25 — Audio mobile : silent buffer unlock + compresseur + gain boosté

- **Contexte** : Gloria signale que la musique et les bruitages ne fonctionnent pas / ne s'entendent pas sur mobile (iOS Safari + Android). La logique `ctx.resume()` au premier geste suffisait sur desktop mais pas sur iOS où l'AudioContext reste en `suspended`.
- **Décision** : Patch en 4 points sur LCAudio (les 4 pages Luxury Club 229) :
  1. **Silent buffer unlock** : jouer un buffer audio d'1 sample silencieux pendant `ensure()` — pattern canonique recommandé par Apple pour débloquer iOS Safari.
  2. **DynamicsCompressor** entre master et destination (`threshold=-10`, `ratio=8`) pour gérer le clipping quand on boost le gain.
  3. **Master gain mobile** : `1.0` → `1.45` (+45 %). Le compresseur absorbe les pics.
  4. **Détection mobile élargie** : `matchMedia('(max-width:760px)')` ∨ `matchMedia('(pointer:coarse)')` pour couvrir tablettes + phones en paysage.
- **Raison** : Les 3 changements sont nécessaires conjointement. Le silent buffer débloque iOS sans demander de permission. Le compresseur permet de monter le gain sans saturation. La détection élargie évite de rater des cas mobile en landscape.
- **Alternatives écartées** :
  - HTMLAudioElement + MediaStream pour bypasser le mode silencieux iOS → demanderait la permission Microphone, hors scope pour une vitrine commerciale.
  - Howler.js → externe au repo, viole la règle « zéro CDN » de NEBULA.
  - User-agent sniffing → fragile et déprécié.
- **Conséquences** :
  - Audio fonctionnel sur Chrome Android, Safari iOS (hors mode silencieux), Firefox mobile.
  - Limitation iOS mode silencieux documentée dans `apprentissages/techniques-html.md` — à mentionner aux clientes pour les tests.
  - Pattern réutilisable pour les futurs projets NEBULA → archivé comme technique standard.

---

<!-- Ajouter les nouvelles décisions au-dessus -->
