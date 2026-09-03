# 2026-08-27 · Les cinq vidéos TikTok : analyse du micro-site émotionnel

Mongazi a envoyé 5 vidéos TikTok (SnapTik) en demandant une analyse de fond du
projet, de sa rentabilisation et de la réalité africaine. Aucune ligne de code
écrite : c'est un dossier de décision.

**Dossier complet : `_plans/2026-08-27-minuit-dossier.html`**
(publié aussi en artifact : https://claude.ai/code/artifact/08cd98d7-d4d5-4d3b-a017-a006c584f04f)

---

## Méthode

`ffmpeg` installé dans la session (absent au départ), 118 images extraites des 5
fichiers, lues en planches de contact. Pied de page de V3 recadré en pleine
résolution pour identifier le concurrent. Prix des concurrents relevés en
ligne, jamais estimés. Actifs NEBULA vérifiés dans le dépôt.

## Ce que sont les 5 vidéos

Une seule catégorie de produit, cinq positionnements.

| Réf | Durée | Accroche | Forme | Mécanique |
|---|---|---|---|---|
| V1 | 23,1 s | « No rizz but I'd always make handmade (digital) gifts for you » | Album souvenir verrouillé | Clavier PIN « Welcome, jan » → satin rouge, étoiles léopard, polaroïds, boule à facettes, lettre manuscrite, chat, « LOVE » |
| V2 | 45,3 s | « POV: You surprised your girl with this cute website » | Page à 4 onglets | « Enter the secret code » → « Welcome my love, enjoy your stay » → Love Letter / Music / Notes / Gallery. **Barre d'adresse : `C:\Users\jam\lovetemplate.html`** = un seul fichier HTML local |
| V3 | 23,8 s | « Pov : Mon copain me surprend avec cette invitation » | **Invitation + confirmation**, produit **« Dis Oui »** (FR) | Enveloppe à cachet, « TOUCHE LA LETTRE » → « Ça te dit un date avec moi ? » avec **bouton Non qui fuit** et raillerie changeante → dîner croisière, Pont de Bir-Hakeim 75015 Paris, **créneau 20h/21h**, mot facultatif → « Vendredi 31 juillet à 21:00 », **Ajouter à mon calendrier**, pied **« CRÉER LA MIENNE SUR DIS OUI »** |
| V4 | 26,8 s | « instead of a normal text you send her this card on her birthday » | Carte pensée téléphone | Enveloppe bordeaux, **cachet de cire doré**, ouverture, flash, carte crème « Happy Birthday », lettre ligne à ligne (« Dear Zara… Forever yours, Robert »), **polaroïd du couple** |
| V5 | 9,8 s | « Valentine Letter · HTML · CSS · JS » | **Contenu de développeur** | Fenêtre pixel Win95, 3 panneaux de code, « Press & release to shoot Cupid's arrow », YES/NO avec **NO qui s'enfuit**, confettis |

⚠️ **Les 5 bandes son sont de la musique seule, sans voix off** (32 à 65 kb/s) :
pas de visage, pas de voix, pas de barrière de langue. Un opérateur seul tient
le format.

## Les 5 lois de la catégorie

1. **Le seuil EST le produit.** Les 5 ont une barrière (PIN, code, cachet,
   flèche). Elle crée l'attente, rend privé, et surtout **rend filmable** en
   créant un avant/après. Une page sans seuil n'est pas un contenu partageable.
2. **L'objet vendu est la vidéo, pas la page.** On ne vend pas un site, on vend
   **une raison de publier**. Chaque acheteur est un distributeur.
3. **Aucune ancre de prix.** La destinataire ne peut pas chiffrer le cadeau.
   Valeur perçue haute, coût marginal nul, aucun comparatif.
4. **Le « Non » qui s'enfuit** (2 vidéos sur 5) : il force l'interaction et
   provoque le rire, l'émotion qui fait partager.
5. **Un calendrier, pas un achat unique** (anniversaire mensuel, Saint-Valentin,
   demande, excuse, distance).

## Marché réel (prix relevés, non estimés)

| Acteur | Marché | Prix | Modèle |
|---|---|---|---|
| Gabarits Canva | Philippines | ≈ 1,20 $ | fichier |
| YourLovePage | International | 9,99 $ | achat unique à vie |
| LovesPage | Brésil | R$ 69,90 (≈12 $) | à vie, 7 moments |
| LovePage, Love-Builder | International | libre-service | constructeur |
| **Dis Oui** (V3) | France | gratuit + pied viral | freemium |
| Prestation Fiverr | International | **50 à 200 $** (site mariage + RSVP : 120 $) | fait pour vous |

⛔ **Aucun avantage technique n'existe dans cette catégorie** (V2 tient dans un
fichier). Le seul terrain défendable : marque, distribution, vitesse du
catalogue, spécificité locale.

## ⚡ LA DÉCOUVERTE : la tuyauterie existe déjà dans le dépôt

C'est le point qui change tout le calcul. Le coût d'entrée n'est pas un
développement, c'est un assemblage.

- **`vitrina/`** : `creer.html` + `server.py` + `cfproxy/_worker.js`. La cliente
  crée, commande, paie en Mobile Money manuel, notification Telegram,
  back-office, validation, mise en ligne. Packs 15/25/45 000 F. **C'est déjà
  exactement le parcours voulu, soit ~70 % du travail.**
- **`_studio-video/`** (Remotion 4.0.512, 1080×1920, 30 i/s) : **l'avantage
  déloyal.** Les concurrents filment leur écran à la main (V1, V2 = production
  médiocre). On *rend* une vidéo de démonstration par gabarit, au pixel, en série.
- **FedaPay** (pk_live/sk_live) : encaissement Mobile Money automatique, condition
  de survie d'un ticket à 2 000 F.
- **n8n + Twilio WhatsApp** : la **livraison programmée à minuit**, que personne
  dans les 5 vidéos ne propose.
- **Cloudflare Pages** : coût marginal d'une page de plus = 0.
- **`DIRECTION-ARTISTIQUE.md`** : une animation signature par section = exactement
  la discipline que cette catégorie récompense.
- **Le carnet clients** = des revendeurs (Djambar bijouterie, Miss cakes,
  Weinkeller, Grain d'Esthétique, Hillary couture). Un bijoutier qui vend une
  bague offre la page avec un QR.
- **PISTE** (7 817 fiches) = la liste de prospection B2B événementiel.
- **Réseau partenaires** (30 %, 40 % à 3 ventes, contrat v1.2).

⚠️ **La ressource rare n'est pas l'argent, c'est l'attention de Mongazi**, déjà
prise par Boussole, PISTE et les clients. C'est le vrai arbitrage.

## Réalité africaine

- 10,6 M utilisateurs mobiles actifs au Bénin (T3 2025), MTN 4,51 M / Moov 2,59 M.
- Mobile Money : MTN ≈ 55 % des transactions, Moov ≈ 35 %. **Deux réseaux, pas un.**
- ✅ **Depuis juillet 2026, un seul numéro suffit pour MTN MoMo, Moov Money et
  Celtiis Cash** (interopérabilité) : c'est le déverrouillage principal de
  l'encaissement.
- **Diaspora : plus de 2 M de Béninois** (France, USA, Canada, CEDEAO),
  ≈ 300 Md FCFA/an de transferts. **Ils paient en euros.** Segment le plus
  rentable, et V3 prouve que la version française premium marche déjà en France.
- ⚠️ **WhatsApp avant TikTok** : la vraie surface virale ouest-africaine est le
  statut WhatsApp et les listes de diffusion. Il n'y a pas de « lien en bio »,
  le lien doit voyager **dans** le message.
- ⚠️ **La méfiance au paiement est rationnelle** : parcours WhatsApp d'abord,
  aperçu avant paiement, preuve sociale.
- **Les occasions qui paient vraiment** : mariage (25 à 75 000 F, 200-500 invités
  = 200-500 diffusions par vente, et compter les invités pour le traiteur est une
  douleur réelle), naissance/baptême (10-25 000), **deuil/funérailles**
  (15-50 000, poids social énorme, aujourd'hui servi par des programmes imprimés
  et des images WhatsApp, **personne ne le sert avec dignité**), Saint-Valentin
  (2-10 000, volume fort ticket faible), 31 décembre et fêtes des mères/pères.

## La thèse : un moteur, trois marchés

> **Le romantique est le marketing. L'événement est le chiffre d'affaires.
> Le B2B est la retraite.**

| Marché | Rôle | Ticket |
|---|---|---|
| A · Romantique impulsion | marketing, volume, boucle virale | 0 à 10 000 F |
| B · Événement familial | **chiffre d'affaires** | 25 000 à 75 000 F |
| C · B2B marque blanche | **récurrence** | 15 000 F/mois |

Un seul moteur (page scellée + médias + confirmation + encaissement MoMo), trois
habillages. C'est la méthode « socle réutilisable décliné par secteur » déjà en
vigueur.

⚠️ Et : **une page offerte à 0 F est le meilleur aimant possible pour le
Catalogue à 50 000 F.** Même à l'équilibre, ce produit se justifie.

## Grilles de prix proposées

**B2C Bénin** : Gratuit (pied de page NEBULA, 7 j, 1 photo) · **Le Mot 2 000 F**
· **La Lettre 5 000 F** (palier de référence) · **Le Coffret 10 000 F** (livraison
WhatsApp à minuit + bande-annonce rendue) · **Sur Mesure 25 000 F**.

**Diaspora** : 5 € / 15 € / 29 €. ⚠️ **Ne jamais afficher les deux monnaies sur
la même page** : une page en euros, une en francs, deux adresses.

**Événement/B2B** : faire-part + confirmation 25 000 F · pack mariage 75 000 F ·
**commission 3 à 5 % sur les contributions collectées** (⚠️ via FedaPay
**directement vers le compte du couple**, jamais de détention de fonds) ·
marque blanche 15 000 F/mois · gabarits 9 à 19 $ à l'international.

**Marge brute > 90 %**, coûts fixes ≈ 0. Seuil de rentabilité immédiat.

**Scénarios à 12 mois** : prudent 60 000 F/mois (revenu d'appoint) · **réaliste
500 à 600 000 F/mois** à 6-9 mois · bon ≈ 1 000 000 F/mois (la diaspora et le
B2B font la différence, pas le volume romantique). ⚠️ Un mois de Saint-Valentin
peut faire 2 à 4× un mois ordinaire : **il se prépare en janvier**.

## Ordre d'exécution (6 phases)

1. **J1-5** : un gabarit irréprochable + le seuil + **le pied de page viral** +
   palier gratuit, en réutilisant `vitrina/`.
2. **J6-12** : **FedaPay automatique** + livraison WhatsApp à minuit (n8n).
   Sans cette phase les petits tickets sont déficitaires.
3. **J13-20** : chaîne vidéo Remotion + tournage façon V4, publication quotidienne.
4. **S4-6** : ligne événement (faire-part + confirmation + calendrier) à 25 000 F.
5. **S7-10** : diaspora en euros + démarchage marque blanche via PISTE.
6. **S11** : décision.

## Risques et garde-fous

- 🔴 **Détournement contre une personne** (vraies photos, prénom, et dans V3 une
  **adresse et une heure de rendez-vous** sur une URL publique). Aucune des 5
  vidéos ne traite ce risque. → adresse non devinable, code obligatoire,
  expiration, pas d'indexation, retrait sous 24 h, CGU. **Avant la première
  vente.**
- 🔴 **Droits musicaux** : héberger un MP3 est une contrefaçon (V2 affiche des
  morceaux réels) → lecteur externe ou lien, jamais de fichier hébergé.
- Copie du produit : certaine, ne pas la combattre, la devancer.
- Saisonnalité : portefeuille d'occasions + abonnement B2B.

**⛔ À ne jamais faire** : aucune photo générée du couple (règle du 2026-08-01,
ici doublement juste) · ne jamais détenir l'argent des cadeaux de mariage · pas
d'abonnement logiciel ni d'application avant le premier chiffre d'affaires · pas
de refonte de `vitrina/` · **aucune validation manuelle sous 10 000 F** · le
deuil ne se décore pas (sobriété totale, aucun emoji).

## Verdict

À faire, mais **pas** sous la forme des vidéos. Trois choses au premier jour :
le **palier gratuit avec son pied de page viral**, **un seul gabarit
irréprochable**, et la **livraison WhatsApp à minuit** (la seule idée du dossier
qu'aucun concurrent observé ne propose, et qui mérite de donner son nom au
produit : **« Minuit »**, proposition et non décision).

**Critères d'arrêt écrits d'avance** : après 8 semaines de publication
quotidienne et 200 pages gratuites créées, si la conversion payante reste sous
3 % et qu'aucun revendeur n'a signé, la ligne romantique est un loisir. On garde
le palier gratuit comme aimant pour le Catalogue et les heures repartent vers
Boussole et PISTE.

---

## État

- Aucun code produit, aucun déploiement. **Dossier de décision uniquement.**
- Branche `claude/video-project-analysis-monetization-18oh7b`, **rien fusionné
  dans `main`** : en attente de validation de Mongazi.

---

## Suite du 2026-08-28 — le manuel opérationnel

Mongazi : « Comment on vendra ça ? Je veux les étapes de la mise en ligne
jusqu'à comment le client fait, et les divers événements. »

**Manuel : `_plans/2026-08-28-minuit-manuel.html`**
(artifact : https://claude.ai/code/artifact/3cd64652-a154-4004-bedd-5abea81346de)

Huit parties : ouvrir la boutique (8 étapes, 3 déjà faites) · le flux d'une
vente avec schéma des 3 acteurs · le parcours client écran par écran · le
catalogue des 10 occasions · le calendrier de l'année au Bénin · 4 scripts de
vente mot pour mot · les cas tordus · l'état réel des briques.

### ⛔ Deux défauts trouvés dans le code en écrivant la procédure

1. **La référence de transaction était marquée « (optionnel) »** dans
   `creer.html` alors que c'est TOUT le mécanisme de vérification décidé par
   Mongazi. Corrigé : champ exigé côté client avec explication (« le SMS te
   donne ce code »), et le serveur **crie** `*AUCUNE RÉFÉRENCE FOURNIE*` dans
   l'alerte si une commande arrive sans (on accepte quand même : une vente par
   un partenaire ou en main propre n'en a pas).

2. ⚠️ **LE TROU DE L'ÉCRAN 4, PAS ENCORE BOUCHÉ** : pour payer, le client
   **quitte la page** (appli Mobile Money ou code USSD). S'il revient et que le
   navigateur a vidé l'onglet, **il a tout perdu** : son mot, ses photos, 15 min
   de travail. Il ne recommencera pas, et on ne saura jamais que la vente a
   existé. Remède = sauvegarder le formulaire dans le navigateur à chaque frappe
   et le restaurer au retour. **À faire avant d'ouvrir.**

### Le flux réel (tiré du code, pas d'une intention)

Client remplit et voit son aperçu → il paie hors du site → il colle la réf →
alerte WhatsApp+Telegram avec réf, doublon et lien signé → **Mongazi vérifie le
SMS puis valide (seul arrêt humain, ~2 min)** → page en ligne + client prévenu
automatiquement. Son temps réel par vente : environ deux minutes.

### Ce qui reste (par ordre)

1. **Le gabarit émotionnel** (le vrai travail : `creer.html` fabrique
   aujourd'hui des vitrines de commerce, pas des pages cadeau)
2. **La sauvegarde du formulaire pendant le paiement** (quelques lignes)
3. **La livraison à l'heure choisie** (la fonction qui donne son nom au produit)
4. Déploiement Render + sous-domaine, variables WhatsApp, numéro MoMo dédié
5. La commande à blanc avec un vrai paiement de 100 F avant d'ouvrir

⚠️ **Sur le deuil** : vrai besoin, mais une seule maladresse de ton abîme la
marque pour longtemps. Faire relire par quelqu'un qui vient d'enterrer un
proche avant de vendre cette ligne.

---

## Suite du 2026-08-28 — le réveil de Render, réglé sans payer un franc

Mongazi a envoyé une capture : `partenaires.nebula-agency.online` affichait
« APPLICATION LOADING » pendant 26 s. Consigne : « je ne veux rien payer, mais
arrange-moi la situation ».

### Les faits vérifiés

- Render endort un service gratuit après **15 min** sans trafic, réveil **~1 min**.
- ⚠️ **Les 750 h gratuites sont PAR ESPACE DE TRAVAIL, pas par service.** Un
  service éveillé 24h/24 = **720 h**, soit presque tout le quota. **Deux
  services = 1 440 h : les DEUX sont suspendus.** Réveiller trop est pire que
  ne rien faire.
- ⛔ **Un proxy inverse NE RÈGLE PAS un réveil** : si Cloudflare interroge
  Render, la requête attend quand même. C'était le piège du réflexe.

### Le vrai danger, qui n'était pas celui de la capture

Dans l'architecture d'origine, c'est le serveur Python qui sert **la page
cadeau** (`/v/{slug}`). Donc la destinataire tape le lien à minuit et tombe sur
« APPLICATION LOADING » pendant une minute. **Ce n'est pas un site lent, c'est
le cadeau détruit** : tout le produit tient dans ce moment d'ouverture.

### La solution : séparer selon QUI attend

- **Ce que le client et la destinataire touchent** → Cloudflare KV, servi
  depuis le bord, **aucun réveil, jamais**, gratuit (1 000 écritures et
  100 000 lectures par jour, une vente = une écriture).
- **Le back-office et la validation** → Render a le droit de dormir : le seul
  qui attend, c'est Mongazi, et il prend déjà 2 min pour lire son SMS.

### Ce qui a été écrit

- **`.github/workflows/reveil.yml`** : ping toutes les 10 min de **06h à 23h**
  Cotonou (`*/10 5-21 * * *` UTC, le Bénin est à UTC+1 sans heure d'été).
  **510 h/mois sur 750, marge de 240 h.** Le calcul est écrit dans le fichier
  avec l'avertissement de le refaire avant d'ajouter une URL. Liste d'URLs dans
  la variable de dépôt `URLS_A_REVEILLER` ; absente, le workflow ne fait rien.
  ⚠️ **Ce n'est pas une garantie** : GitHub peut retarder un déclenchement
  programmé de plusieurs minutes. Le réveil devient rare, pas impossible.
- **`vitrina/publier.py`** : pose le HTML validé dans Cloudflare KV
  (`publier`), et **`retirer`** pour le retrait sous 24 h. ⚠️ **Supprimer en
  base NE SUFFIT PAS** : tant que la page est dans KV, le bord la sert.
- **`vitrina/cfproxy/_worker.js` réécrit** : `/v/{slug}` servi depuis KV **sans
  jamais toucher l'origine** ; l'aperçu non validé retombe sur l'origine (c'est
  acceptable, l'acheteur vient de POSTer donc elle est réveillée) ; le reste est
  relayé. `noindex` posé (une page cadeau porte un prénom et des photos).
  ⛔ **L'ancienne version pointait encore vers Railway**
  (`vitrina-production-686b.up.railway.app`), abandonné le 2026-08-01 : elle
  relayait vers un service mort et rien ne le signalait. L'origine se pose
  désormais en variable `ORIGINE`.
- **`server.py`** : `/sante` (point de réveil sans base ni rendu), publication
  au bord à la validation, retrait du bord à la suppression. ⚠️ **L'alerte DIT
  si la page n'a pas pu être publiée sur Cloudflare** (« servie par Render,
  environ une minute d'attente ») au lieu de le taire.

### Contrôles

`vitrina/_qc.py` **36 verts** (dont : la page est posée sur Cloudflare à la
validation, la suppression retire du bord, et **Cloudflare absent ne casse rien
mais l'alerte le dit**). Nouveau `vitrina/cfproxy/_qc_worker.mjs` **15 verts**
en Node (dont : **aucun appel à l'origine** pour une page livrée, un slug tordu
n'interroge pas KV, et sans `ORIGINE` un message clair au lieu d'une page
blanche).

### À poser côté Cloudflare et GitHub

Variables `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID`, `CF_API_TOKEN` (permission
Workers KV Storage · Edit) ; sur le projet Pages, la variable `ORIGINE` et la
liaison KV nommée `PAGES` ; dans le dépôt, la variable `URLS_A_REVEILLER`.

---

## Suite du 2026-08-28 — LA LETTRE EXISTE

Mongazi : « lance le projet de lettre maintenant, le back-office après, je veux
que ce soit visuellement et textuellement comme ceux dans les vidéos ».

**`vitrina/lettre/gabarit.html`** · QC `python3 _qc.py` = **35 contrôles verts**

### La phrase, dont tout découle
*Une lettre, c'est du papier qu'on a plié, scellé, et qu'on ouvre en tremblant.*
Papier, cire, encre, pli. Aucune animation ne vient d'ailleurs.

### Le parcours, repris du vocabulaire des vidéos
Enveloppe bordeaux + **cachet de cire doré** (V4) → « Touche le cachet » (V3)
→ le cachet **se fend en deux**, le rabat s'ouvre, le papier glisse → **code
secret au clavier** (V1, V2) → « Bienvenue mon amour » en manuscrite (V2)
→ la lettre dont **chaque ligne monte comme si on l'écrivait** → mes mots
(papiers pliés qui se déplient) → polaroïds qui tombent de travers → notre
musique (sillon du disque) → **le « Non » qui s'enfuit** (V3, V5) → pied viral
« Créer la mienne sur Minuit ».

### ⛔ Défauts trouvés et corrigés

- **`--or-clair:#d3ae६8` contenait un chiffre DEVANAGARI** au lieu d'un 6. La
  couleur était invalide, donc le dégradé du cachet était invalide, donc **le
  cachet de cire ne s'affichait pas du tout** et le prénom était illisible. Une
  seule frappe tuait les deux éléments les plus importants du premier écran.
- ⛔ **LE « NON » SE POSAIT SUR LE « OUI »** et le rendait incliquable : le gag
  tuait la page, on ne pouvait plus répondre. Il calcule maintenant une zone
  interdite autour du Oui, et se colle dans le coin opposé si la place manque.
  Contrôle dédié : après **15 fuites**, le Oui reste cliquable.
- ⛔ **Les légendes des polaroïds étaient coupées en plein mot** (« Notre
  premi… ») : trouvé **sur une capture, pas dans le code**. Une légende tronquée
  sur la photo d'un cadeau est pire que pas de légende. Elles passent à la ligne.
- Cibles tactiles du sommaire à 31 px → **44 px**.

### ⚠️ Leçons de mesure

- **`document.fonts.check()` MENT** : il rendait `true` alors que
  `document.fonts.size` valait **0** et que la requête Google Fonts avait
  échoué. On mesure **la largeur réelle d'un glyphe** (168 px en script contre
  108 px en monospace), jamais l'API.
- **La police manuscrite est EMBARQUÉE en base64** (Petit Formal Script, OFL,
  réduite aux caractères français : 23,7 Ko). Une lettre ouverte à minuit sur
  une connexion lente ne peut pas attendre deux allers-retours vers un serveur
  de polices : c'est elle qui porte toute l'émotion. EB Garamond reste au CDN
  avec Georgia en repli, qui ne coûte rien à la lettre.
- **Un faux positif de MON contrôle** : `text-transform:uppercase` rend « TA
  PHOTO ICI », et je cherchais « Ta photo ici ». On lit ce qui est RENDU.

### Règles tenues
⛔ **Aucune photo inventée** : sans photo, le cadre affiche « Ta photo ici » et
n'émet aucune `<img>`. ⛔ Aucune bibliothèque. `noindex` posé (une page cadeau
porte un prénom et des photos). `prefers-reduced-motion` respecté.

### Reste
Le **back-office** (le formulaire qui écrit le bloc `LETTRE`), demandé pour
après.

---

## Suite du 2026-08-28 — LE BACK-OFFICE, UNE QUESTION PAR ÉCRAN

**`vitrina/lettre/creer.html`** · QC `python3 _qc_creer.py` = **50 contrôles verts**
(il remplit vraiment les onze étapes dans un navigateur et vérifie la lettre produite)

Essais en ligne : lettre https://claude.ai/code/artifact/f1db259e-8281-44f1-a74a-1abdc6482ce6
(code **0410**) · formulaire https://claude.ai/code/artifact/5a4c085d-2418-4420-902c-f9e90146bda2

### Onze étapes
occasion (5 choix qui pré-remplissent le ton) · pour qui/de qui · la lettre ·
la signature · mes mots · nos photos · notre musique · la question · le code
secret · **l'aperçu (la vraie lettre dans un cadre)** · le paiement.

### ⚡ LE TROU DE L'ÉCRAN 4 EST BOUCHÉ
Tout est sauvegardé dans le navigateur **à chaque frappe** (`minuit:brouillon:v1`),
et le brouillon n'est oublié **qu'après** l'envoi. Le client qui part payer en
Mobile Money et revient **repart là où il s'était arrêté**, et on le lui dit
(« On a retrouvé ta lettre »). Contrôlé en ouvrant un second onglet du même
contexte.

### ⚠️ UNE SEULE VÉRITÉ POUR LE GABARIT
`creer.html` ne recopie pas la lettre : il va chercher `gabarit.html` et
remplace le bloc entre **`MINUIT:DEBUT_CONTENU`** et **`MINUIT:FIN_CONTENU`**.
Le jour où le gabarit change, toutes les lettres suivantes en profitent.

### ⛔ TROIS DÉFAUTS RÉELS TROUVÉS

1. ⛔ **LE `<link>` GOOGLE FONTS BLOQUAIT L'EXÉCUTION DU SCRIPT.** Mesuré :
   **12 640 ms** avant que le prénom s'affiche quand le CDN ne répond pas.
   Pendant ce temps la lettre montrait **« toi » et « M »** (les valeurs écrites
   en dur dans le gabarit) au lieu du prénom et de l'initiale : le produit
   ratant son seul moment, sur le premier écran. → `media="print"` puis bascule
   `this.media='all'` : **73 ms**, CDN totalement coupé. Contrôle dédié qui
   coupe `fonts.googleapis.com` et exige moins de 2 500 ms.
2. ⛔ **`maxlength="4"` sur le code coupait AVANT le filtre** : taper ou coller
   « abc1234 » laissait « abc1 », puis le filtre retirait les lettres et le code
   devenait **« 1 »**. Le maxlength est retiré, le filtre plafonne déjà.
3. ⛔ **`</script>` dans le gabarit embarqué** fermait la balise du shim de la
   version d'essai (« Invalid or unexpected token »). Il faut échapper les
   `</` en `<\/` pour embarquer du HTML dans du JavaScript.

### ⚠️ QUATRE FAUX ROUGES DE MES PROPRES CONTRÔLES
- « ÉTAPE 1 SUR 11 » en majuscules (`text-transform`) contre « sur 11 » cherché
  en minuscules. **Troisième fois** dans cette session : on lit ce qui est
  RENDU, jamais la casse de la source.
- « const LETTRE » cherché dans `creer.html` : il l'ÉCRIT, c'est normal. Le
  contrôle est devenu structurel (`.enveloppe{` et `#seuil{` absents).
- « TOUCHE LE CACHET » : présent dans le texte d'aide **du formulaire**.
- Lire l'iframe de l'aperçu **avant que son script ait tourné** renvoie les
  valeurs d'exemple. → fonction `attendre_iframe()` qui attend le signal.
  ⚠️ C'est en corrigeant ce faux rouge qu'on a trouvé le défaut n°1 : le
  produit était vraiment lent, pas seulement mal mesuré.

### Photos
Réduites **dans le navigateur** (1000 px, JPEG 82 %) avant d'entrer dans la
page, plafond 3,2 Mo avec avertissement : la lettre part entière dans KV, une
photo brute de téléphone la rendrait impossible à ouvrir sur une connexion
béninoise. ⛔ Sans photo, aucune `<img>` n'est émise et le cadre le dit.

### Reste
Déploiement (Render + Cloudflare KV + les variables), et la **livraison à
l'heure choisie**.

---

## ⛔ 2026-09-02 — LE MÊME TRAVAIL A ÉTÉ FAIT DEUX FOIS (encore)

Pendant que cette session construisait `vitrina/lettre/`, une autre a poussé
**`minuit/`** directement dans `main` (commit `cfa8576`), à partir du même
dossier et du même manuel. Deuxième occurrence après celle du 2026-08-27.
⚠️ `git fetch` au DÉBUT ne suffit pas quand une session du téléphone pousse
dans `main` PENDANT le travail.

### Les deux versions, mesurées

| | `minuit/` (dans `main`) | `vitrina/lettre/` (branche) |
|---|---|---|
| Lettre | **22 233 o** | 62 060 o |
| Polices | **aucun téléchargement**, pile système (Iowan Old Style, Palatino) | Petit Formal Script en base64 + EB Garamond au CDN |
| Appels réseau de la lettre | **zéro** | 1 (feuille de style) |
| Architecture | chercher `lettre.html` + remplacer le bloc | identique |
| Sauvegarde formulaire | oui | oui |
| Écrans du formulaire | 6 (ceux du manuel) | **11** |
| Contrôles | 78 | 35 + 50 |
| README | oui | non |

### ✅ VERDICT : on garde `minuit/`
Sur le point qui décide, **elle est meilleure** : 22 Ko et zéro appel réseau.
Ma réponse (embarquer la police en base64) était le bon instinct, la leur va
plus loin et plus juste : **ne télécharger aucune police**, prendre de vraies
faces de correspondance déjà sur l'appareil. Le défaut du `<link>` bloquant que
j'ai trouvé et mesuré (**12 640 ms**) **n'existe pas chez elle** : sa conception
l'évite. Les deux sessions ont convergé sur la même architecture, ce qui est
bon signe pour le dessin.

### ⛔ MAIS LE BUG DU `maxlength` Y ÉTAIT AUSSI, ET IL EST CORRIGÉ
`minuit/creer.html` avait `<input id="f-code" maxlength="4">` avec un filtre
`replace(/\D/g,"")`. Prouvé en navigateur : coller « abc1234 » laissait
« abc1 », le filtre retirait les lettres, **le code tombait à « 1 »**.
→ `maxlength` retiré, le filtre plafonne lui-même (`.slice(0,4)`). Vérifié :
« abc1234 » → « 1234 », et « 12345678 » → « 1234 ».

### À porter de `vitrina/lettre/` vers `minuit/`, puis jeter le doublon
1. **Les 11 étapes au lieu de 6** : Mongazi a demandé « un à un étape par
   étape ». Le manuel décrivait 6 écrans côté client, sa demande en veut plus.
2. **Le contrôle du CDN de polices** (coupe `fonts.googleapis.com`, exige
   moins de 2 500 ms) : assurance bon marché si quelqu'un rajoute un jour un
   `<link>` de police.
3. **`attendre_iframe()`** : lire l'aperçu avant que son script ait tourné rend
   les valeurs d'exemple et fait accuser le produit à tort.

⏳ **Mongazi tranche** : fusionner puis supprimer `vitrina/lettre/`, ou l'inverse.

---

## SESSION 2026-09-03 — « c'est raté c'est basique » : l'enveloppe n'avait qu'un seul plan

Mongazi envoie une capture de l'ouverture sur son iPhone : *« Regardes comment
la lettre s'ouvre, c'est raté c'est basique, utilises remontions [Remotion] pour
améliorer et augmenter la qualité du rendu et rendre les animation plus propre
et mieux disigner »*.

### ⛔ REMOTION EST LE MAUVAIS OUTIL POUR LA LETTRE, et il faut le dire
Remotion **fabrique de la vidéo**. La lettre est **interactive** : elle porte le
prénom de la destinataire, elle attend un code, elle réagit au toucher. Avec
Remotion il faudrait **un rendu par vente** : une vidéo par prénom, par code,
par photo. Le produit s'effondre sur son économie.

⚠️ **Ce n'est pas un refus de l'outil, c'est un déplacement** : Remotion reste
le bon outil pour **les vidéos de démonstration TikTok** (c'est même exactement
ce que `_studio-video/` fait déjà). Ce qu'il y avait à emprunter à Remotion,
c'est **sa discipline** : une vidéo se juge image par image. Donc au lieu de
l'installer, **j'ai mesuré la vraie page image par image**.

### LE DÉFAUT ÉTAIT STRUCTUREL, PAS COSMÉTIQUE
« Basique » ne se répare pas en ajoutant des courbes. **Une enveloppe a un DOS,
une POCHE et un RABAT.** La version d'avant n'avait **qu'un seul plan** : le
papier ne pouvait donc pas sortir « de dedans », il **glissait par-dessus**, et
ça se voit tout de suite.

Quatre plans désormais : `.dos` · `.papier` · `.devant` (poche opaque) ·
`.rabat`. Le papier part de l'intérieur, **attend que le rabat ait franchi les
90 degrés**, puis monte et devient la carte. Mesuré au `requestAnimationFrame`
**côté page**, pas supposé :

```
cire tombée        644 ms      papier sorti     877 ms
rabat à 90°        344 ms      amorce lisible  1227 ms
rabat grand ouvert 544 ms      code visible    2127 ms
papier commence    527 ms      ÉCRAN VIDE :    JAMAIS
```

### ⛔ `preserve-3d` REMPLACE LE z-index PAR UN TRI DE PROFONDEUR 3D
Le défaut le plus intéressant : **des bandes rouges en travers du papier**.
Trouvé en lisant les pixels de la colonne centrale (3 zones crème alternant
avec du rouge), pas dans le code.

La cause n'était pas un z-index mal posé. `transform-style: preserve-3d`
**annule l'ordre des z-index** et le remplace par un tri de profondeur : les
plans qui **s'intersectent** sont découpés l'un par l'autre, et le rendu est
rayé. Mon `rotateX(4deg)` sur le papier le faisait traverser le plan de la
poche. → rotateX retiré, papier en `translateZ(-2px)`. Vérifié aux pixels :
**1 seule zone crème**.

⚠️ **Règle à retenir** : dans un contexte `preserve-3d`, deux plans qui doivent
se recouvrir doivent être **séparés en Z**, pas en z-index.

### Les autres défauts, tous trouvés en mesurant
| Défaut | Comment il a été trouvé | Correction |
|---|---|---|
| Le rabat coupait le papier d'une bande rouge à 1 000 ms | capture | il passe derrière à **520 ms**, posé par le script : visible **pendant** sa rotation, derrière **après** |
| Le V de la poche laissait deux triangles découverts | mesuré à x=25% : rabat 0-31%, poche 44-100%, **trou de 13%** | le V est **dessiné** sur un rectangle opaque, plus découpé |
| La cire ne tombait que de 54 px, posée comme deux pétales | capture | 172 et 186 px, rotation ±74 et 81° |
| Le prénom se retrouvait **derrière le rabat** | capture | il s'efface en montant, 380 ms |
| 1 200 ms d'écran vide | mesure | fondu croisé, « écran vide : jamais » |
| Le papier sortait à 282 ms, **avant** l'ouverture du rabat | mesure | retard de 0,5 s sur le papier |

### ⚠️ ET J'AI REFAIT L'ERREUR QUE SON PROPRE CLAUDE.md DOCUMENTE
*« Ne jamais mesurer une animation d'ouverture avec des `wait_for_timeout`
empilés autour de captures »* (leçon Angy Art du 08/08). Je l'ai refaite. Une
capture coûte des centaines de ms, donc l'horloge dérive et le diagnostic est
faux. → **un chargement de page = une capture**, et c'est la **page** qui compte
le temps en `requestAnimationFrame`.

⚠️ **Cinq de mes sondes ont menti avant de dire vrai**, dont une qui vaut d'être
gardée : mon lecteur de matrice CSS avec `/-?[\d.e+-]+/g` **attrapait le « 3 »
de `matrix3d`**, décalait tous les indices, et le rabat semblait bloqué à
-0,0° alors qu'il était à **-172°**. *Vérifier sa sonde avant d'accuser le
produit* — troisième fois dans ce dépôt.

### GARDE-FOU NEUF : AUCUN CARACTÈRE SOSIE D'UN AUTRE ALPHABET
Le défaut le plus cher de ce fichier tenait en **une frappe** :
`--or-clair:#d3ae६8` portait un **chiffre devanagari** au lieu d'un 6. Couleur
invalide → `radial-gradient` invalide → **le cachet de cire ne s'affichait pas
du tout** et **le prénom de la destinataire était illisible**. Les deux éléments
les plus importants du premier écran, tués par un caractère que rien ne
signalait, dans un fichier par ailleurs vert.

Le QC lit maintenant tout le fichier et refuse cyrillique, grec, devanagari,
pleine-largeur, arabe, mathématique. Il a trouvé **un « е » cyrillique de plus**
dans un commentaire (`basculе`), corrigé.

⚠️ **Pourquoi ce contrôle-là plutôt qu'une relecture** : un sosie est
**invisible à l'œil par construction**. C'est précisément le genre de défaut
qu'une machine doit chercher, et un humain jamais.

### ⛔ ET UN 7e DÉFAUT, TROUVÉ EN REGARDANT LA CAPTURE DE 1 300 ms
L'amorce (« Bienvenue mon amour, prends ton temps. ») finissait **à 0,2 px du
bord de la poche**. Elle n'était pas coupée — donc aucun contrôle de
débordement ne pouvait la voir — mais elle n'avait **aucune respiration**, et la
moindre variation de métrique de police l'aurait fait passer dessous.

La cause : `align-items:center` centrait le texte sur **toute** la hauteur du
papier, alors que **le papier ne sort qu'à 62 %** (le reste est dans la poche).
Un texte centré sur 100 % d'une boîte visible à 62 % tombe forcément en bas.

⚠️ **Et à 768 px c'était pire** : l'amorce était en `clamp(15px,3.9vw,19px)`,
donc elle **grandissait avec l'écran** alors que l'enveloppe est **plafonnée à
338 px**. À 19 px la phrase passait à **3 lignes** et **traversait le pli du
papier** — ça se lit comme un texte barré. Une taille qui suit le viewport dans
un conteneur à largeur fixe est un bug, pas une adaptation.

Corrigé : alignement en haut (`padding-top:7%`), police plafonnée à **16 px**,
pli descendu de 38 % à **47 %** pour rester sous la phrase **et** dans la partie
visible. Mesuré à 360, 390, 768 et 1440 : **2 lignes partout, 43 à 52 px de
respiration, aucun croisement du pli, pli toujours visible**.

**3 contrôles neufs** (l'amorce respire · elle ne traverse pas le pli · le pli
reste visible) : le défaut avait traversé **36 contrôles verts**.

### ⏳ CE QUI RESTE
1. **La planche des 8 images n'a pas pu être assemblée ici** : ni PIL, ni
   ffmpeg, ni ImageMagick dans ce conteneur, et l'installation a été refusée.
   Les 8 captures existent (390 px, un chargement chacune, horodatage vrai) —
   **à regarder sur le PC**, c'est la règle de la maison (*« Regarder les
   captures, section par section, en 390 ET 1440, avant de dire fini »*).
2. **Mongazi tranche le doublon** `minuit/` vs `vitrina/lettre/` (recommandé :
   garder `minuit/`, 22 Ko, zéro appel réseau).
3. **La livraison à l'heure choisie** (n8n) : la fonction qui donne son nom au
   produit, toujours pas construite.
