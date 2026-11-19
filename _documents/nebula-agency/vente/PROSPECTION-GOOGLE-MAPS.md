# Prospection Google Maps · trouver les commerces qui ont le plus besoin de nous

Ouvert le 2026-11-18, pour le sprint des fêtes (objectif : 100 000 F CFA encaissés avant le dimanche 22 novembre,
avec de **nouveaux** clients). La méthode reste valable après.

⛔ **Aucune coordonnée dans ce fichier ni dans ce dépôt** : il est PUBLIC. Les fiches (nom, numéro, statut) vivent
dans Supabase, table privée `piste.prospection`, comme la marchandise de PISTE.

## 1. Où chercher

Google Maps, **Cotonou d'abord**, puis Abomey-Calavi. On vise les métiers qui vendent des **produits** (donc un
catalogue a un sens) et qui vendent **plus en décembre** :

pâtisserie · boutique de vêtements · chaussures et sacs · cosmétiques · parfumerie · bijouterie · traiteur ·
décoration événementielle · caviste · jouets · fleuriste.

**La source qui marche : la liste locale de Google**, `google.com/search?q=<métier>+Cotonou&udm=local&hl=fr`
(`&start=20` pour la page suivante). Chaque carte porte le nom, la note, les avis, **le numéro** et le bouton
« Site Web ». Google Maps, lui, exige d'ouvrir chaque fiche pour lire le numéro et gèle ce PC (18/11).
Pour viser plus haut que le Catalogue : hôtels, salles de fêtes, agences, grandes boutiques (Vitrine 150 000 F).

## 2. La note de besoin (sur 10)

| Signal lu sur la fiche Google | Points |
|---|---|
| Pas de site web | +3 |
| Vend des produits (un catalogue a un sens) | +2 |
| Actif : 10 avis ou plus | +2 |
| Bonne note (4,3 ou plus) : il soigne son image | +1 |
| Numéro mobile, donc joignable sur WhatsApp | +1 |
| Métier des fêtes | +1 |
| A déjà un site ou une boutique en ligne | **écarté** |
| Chaîne, franchise, grande enseigne | **écarté** |

On contacte d'abord les plus hautes notes. La colonne `raison` dit en une ligne **pourquoi lui** : c'est elle qui
rend le message personnel.

## 3. Le message (validé ; feu vert général de Mongazi depuis le 18/11 pour écrire et répondre)

**Premier message, sans lien** (un lien envoyé à un inconnu fait signaler le numéro). Version 2, depuis le
18/11 vers 16 h (Mongazi : « choquer et intriguer, parler moins, de la manière la plus humaine possible ») :

> Bonjour, c'est Mongazi 🙂
> [Nom] : [4,8] sur Google avec [29] avis, vos clients vous aiment.
> Mais un client qui vous trouve à 23 h ne voit ni vos [plats] ni vos prix. Il commande chez qui, à votre avis ?

Ce qui la rend juste : le compliment est **précis** (sa vraie note), et le fait qui dérange est **vrai et
vérifiable** (sa fiche Google n'a pas de site). L'offre n'arrive qu'après sa réponse. `scripts/prospection.py`
l'écrit tout seul pour chaque fiche. *(La version 1, plus longue et qui vendait d'entrée, a obtenu 3 vraies
réponses sur 18 envois le 18/11 ; elle est dans l'historique git.)*

**S'il dit oui** : l'exemple qui ressemble à son métier, puis le prix.

| Son métier | L'exemple à montrer |
|---|---|
| mode, couture | https://hillary-m-styl.pages.dev |
| cosmétiques, beauté | https://luxuryclub229.com |
| boissons, caviste | https://speed-weinkeller.pages.dev |
| bijoux | https://djambarteam.com/bijouterie |
| restaurant, traiteur, pâtisserie | https://aubraisedor.com |

> Pour vous, c'est 50 000 F, et c'est prêt en une semaine au plus dès que j'ai vos photos et vos prix.
> Ensuite, 20 000 F tous les six mois pour l'hébergement, et vos changements de prix sont compris.

**Quand il est intéressé** : il remplit la fiche **https://www.nebula-agency.online/#order** ; elle arrive sur le
WhatsApp de NEBULA (« NOUVELLE COMMANDE »). Ensuite : encore des questions, et ce qui complète sa commande (produits
au-delà de 20, QR Code Google Review, vidéo des fêtes, Vitrine s'il a besoin de crédibilité).

**Les relances : qui, quand, comment** (`python scripts/prospection.py relances - <fichier hors dépôt>` sort la liste
du jour avec les messages ; après chaque envoi, `fait <id>` note la relance et pose la suivante) :

| Où il en est | Relance 1 | Ensuite | Le message |
|---|---|---|---|
| **Aucune réponse** | J+2 | 1 seule relance. Sans réponse 3 jours après : on clôt | « Si je vous montre ce que ça donnerait avec vos [produits], sans que vous payiez quoi que ce soit, ça vous intéresse ? Un oui ou un non me suffit. » |
| **Seulement son message automatique** | J+2 (le jour même si Mongazi le signale) | Dernier message 3 jours après, puis on clôt | L'exemple de son métier + « Je vous prépare un essai gratuit ? » |
| **Il a parlé, puis plus rien** | J+1 | Dernier message 2 jours après | **Sur mesure**, à partir de ce qu'il a dit |
| **Intéressé** | J+1 | J+3, puis J+6, puis appel de Mongazi | **Sur mesure, et toujours du neuf** : son aperçu, une réponse, une proposition. Jamais « avez-vous vu mon message ? » |

**Les heures** (toujours entre 9 h et 16 h) : pâtisserie 9 h-11 h · traiteur 9 h 30-11 h, avant le service de midi ·
boutiques, bijouterie, parfumerie 10 h 30-12 h 30, après l'ouverture · pas de relance le dimanche.

**Chaque personne contactée est enregistrée** dans les contacts WhatsApp (« Prospect + nom »), et chaque discussion
de prospect est **ouverte et relue**, pas seulement regardée dans la liste.

## 4. Les règles qui protègent le numéro et la maison

- **La fenêtre des nouveaux prospects : de 9 h à 16 h** (Mongazi, 19/11). Les réponses aux conversations en cours
  continuent ensuite, jamais la nuit : ce qui est prêt à minuit part à 7 h 45. **Aucun client n'attend sans
  annonce** : chaque demande dit ce qui suit et quand.
- **Le rythme est décidé par Mongazi** : 30 par jour le 18/11 à 15 h, puis **40 par jour** à 16 h 20 (« on doit
  atteindre l'objectif »), en connaissant le risque : au-delà d'une quinzaine, WhatsApp peut bannir le numéro si des
  gens le signalent, et c'est le numéro de travail de NEBULA. D'où : chaque message personnalisé, envois espacés.
- **Des relances comptées** (le tableau du § 3). Un « non », ou le silence après la dernière relance : statut
  `ne_plus_contacter`, pour toujours.
- **Les prix sont ceux du socle** (`00-SOCLE-COMMERCIAL.md`) : Catalogue 50 000 F, abonnement 20 000 F tous les
  six mois. Aucune remise sans Mongazi. **Paiement** : Mongazi a dit le 18/11 « en deux tranches » (une partie pour
  démarrer, le reste à la validation sans correction, puis la mise en ligne), alors que le socle dit « paiement
  intégral, pas d'acompte » : ⏳ à trancher par lui, et la répartition à fixer. Le QR code sur une affiche carrée
  est compris, la carte de visite à imprimer aussi si le client la veut ; le nom de domaine (30 000 F) se propose
  après la livraison.
- **On ne promet que ce qu'on sait livrer** : « une semaine au plus » (le socle dit 5 à 7 jours), compté à partir
  des photos et des prix, pas de la signature. Le « 48 h » des premiers messages du 18/11 n'est plus dit.
- **Plus de 20 produits** : 15 000 F par lot de 10 en plus (socle §1.2), annoncé avant le paiement, jamais après.
- **On ne réécrit jamais à une fiche vendue en exclusivité par PISTE** (90 jours).

## 5. Les statuts d'une fiche

`a_contacter` → `contacte` → `repondu` → `interesse` → `paye`, ou `refus` / `ne_plus_contacter`.
Le tableau de suivi (chaque fiche, sa relance, son historique) : `python scripts/prospection.py suivi <fichier.md>`,
**écrit hors du dépôt** car il porte les numéros.

## 6. Les situations, et quoi répondre (toutes vécues le 18/11)

| Ce qu'il répond | Ce qu'on fait |
|---|---|
| « oui », « ok », « je veux voir » | L'exemple de son métier, le prix en deux lignes, puis « On le fait pour les fêtes ? » |
| « ok » juste après le prix | On le traite comme un oui, **et on explique tout** : ce qu'il reçoit, le prix, l'abonnement, le délai, le paiement Mobile Money. Puis « Une question avant qu'on démarre ? » |
| « d'accord, c'est noté » | On creuse : l'ambiance voulue, ses produits phares, ses clients. Et on relance les photos |
| « Si je comprends, vous faites ça 50 000 ? » | Oui, simplement, puis ce qu'il reçoit pour ce prix, puis une question sur son commerce |
| « J'ai déjà un catalogue » | Demander où il est. Un PDF lourd est l'argument (le client télécharge avant de voir un seul produit) : proposer un **aperçu avec ses propres produits**, sans engagement |
| « Je reviendrai plus tard » | Remercier, proposer une relance datée (« je vous fais signe la semaine prochaine ? »), noter la date |
| « Pour le moment on attend » | « Pas de souci, je reste disponible. » Statut `refus`, aucune relance avant la date notée |
| Une **note vocale** | La télécharger (menu du message) et la transcrire : `python scripts/transcrire.py`. Si le fond coince, **alerter Mongazi** (« BESOIN DE TOI »). Jamais répondre à l'aveugle |
| « J'ai déjà payé quelqu'un qui n'a rien fait » | Empathie d'abord, puis l'**aperçu avec ses vrais produits**, et le paiement seulement s'il lui plaît |
| Il tente un **appel vidéo** ou vocal | C'est le plus chaud : **alerter Mongazi** pour qu'il rappelle ; en attendant, exemple et prix par écrit |
| Il a un catalogue WhatsApp Business (`wa.me/c/…`) | Le saluer, puis le vrai manque : il ne se voit que si on a déjà son numéro, pas sur Google où cherchent les nouveaux clients |
| Message automatique (« Merci d'avoir contacté… ») | **On répond quand même, une fois** (Mongazi, 18/11 : il les compte comme des réponses) : une phrase écrite sur SON message (« vous proposez votre catalogue WhatsApp… », « vous dites de passer en boutique… »), puis « je vous montre un exemple ? ». S'il ne renvoie encore que de l'automatique : relance unique à J+2 |
| L'assistant IA de Meta (« je vous ai connecté à notre équipe ») | Envoyer l'exemple quand même : l'équipe le lira |
| Il répond au 1er message sans avoir vu l'exemple | Renvoyer le lien en une ligne, et proposer l'aperçu avec ses photos |
| « Non » | Remercier, statut `ne_plus_contacter`, plus jamais |
