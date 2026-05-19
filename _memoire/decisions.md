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

<!-- Ajouter les nouvelles décisions au-dessus -->
