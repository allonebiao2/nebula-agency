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
