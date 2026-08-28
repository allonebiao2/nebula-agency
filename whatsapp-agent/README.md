# LE STANDARD — l'agent WhatsApp des clients NEBULA

> Celui qui décroche. Un client écrit sur le WhatsApp d'une maison, l'agent
> répond avec **la vraie carte de cette maison**, prend la commande, et passe la
> main à un humain dès qu'il ne sait pas.

---

## Pourquoi ce kit existe

Les onze vitrines NEBULA se terminent toutes par le même bouton : « écrire sur
WhatsApp ». Le client appuie, écrit… et **quelqu'un doit répondre à la main**,
le soir, pendant le service, en cuisine. C'est le seul endroit de toute la
chaîne qui ne soit pas automatisé, et c'est celui où les ventes se perdent.

Ce kit répond à leur place. Pas avec un catalogue recopié : **avec le fichier
que le site sert déjà**.

```
Le client écrit  →  webhook  →  LE STANDARD  →  Claude  →  GARDE-FOU  →  réponse
                                     ↑                          ↓
                          la carte du site (carte.ts)    un prix inventé
                          la conversation de CE client   ne part jamais
```

### Ce qui le distingue d'un robot de démonstration

**1. Le catalogue n'est jamais recopié.** Il est lu dans le fichier qui fait
autorité sur le site : `carte.ts` chez Au Braisé d'Or, `PIECES` chez Hillary.
La maison change un prix sur son site, l'agent change avec lui, le jour même.
Recopier un prix ici, ce serait fabriquer une deuxième vérité — et une deuxième
vérité est une faute de prix qui attend son tour.

**2. Un prix inventé ne peut pas sortir.** Le prompt dit à Claude de ne rien
inventer. Ça ne suffit pas : une consigne n'est pas un contrôle. Avant tout
envoi, **le code relit la réponse**, en extrait chaque montant et le vérifie
contre la carte. Un montant que la maison ne porte pas fait **avorter l'envoi**,
et un humain est réveillé.

```
Le modèle allait écrire : « Le tilapia braisé est à 4 500 F. »
    ⛔ 4500 F annoncé pour « Tilapia braisé » — la carte dit 3 000 / 6 000
Le client reçoit : « Je préfère vous confirmer ce point exactement… »
Le patron reçoit : le message bloqué, en entier, et le motif.
```

**3. Il sait qu'il ne sait pas.** Réservation, traiteur, réclamation, mesures
d'une cliente, adresse exacte : chaque maison liste dans sa fiche ce qui part
**toujours** à un humain, et ce qu'elle n'a **pas encore tranché** — que l'agent
n'inventera donc sous aucun prétexte.

---

## Essayer maintenant, sans compte WhatsApp

```bash
pip install -r whatsapp-agent/requirements.txt
python whatsapp-agent/simuler.py braise-dor          # avec le vrai modèle
python whatsapp-agent/simuler.py braise-dor --faux   # sans clé, pour voir la mécanique
```

Le simulateur monte **exactement** la chaîne de production — même carte, même
mémoire, même garde-fou — dans un terminal. Tapez `/carte` pour voir ce que
l'agent a vraiment lu. Essayez de le piéger sur un prix.

```bash
python whatsapp-agent/_qc.py     # 146 contrôles, sans clé et sans réseau
```

---

## Mettre un client en ligne

### 1. Chez Meta (une fois par client, ~30 min)

1. **Meta Business Manager** → l'entreprise du client → vérification d'entreprise.
   Sans elle : 250 contacts / 24 h maximum.
2. **WhatsApp Business Platform** → ajouter le numéro **du client** (pas le vôtre).
3. Relever le **Phone Number ID**, générer un **jeton permanent**, copier
   l'**App Secret**.
4. Webhook → URL `https://…/webhook/<id-de-la-maison>`, champ `messages`,
   avec le mot de passe de vérification que vous avez choisi.

### 2. Les variables

Copier `.env.example`, remplir. **`WA_META_SECRET` n'est pas facultatif** : sans
lui, le webhook refuse tout — un webhook public sans signature vérifiée, c'est
un inconnu qui fait parler l'agent d'un client et dépense ses jetons.

### 3. Démarrer

```bash
python whatsapp-agent/serveur.py --port 8020 --racine .
```

Le serveur **refuse de démarrer une maison incomplète** et dit ce qui manque.
Un agent sans numéro à prévenir n'est pas un agent, c'est un répondeur : le jour
où il ne sait pas, la conversation meurt en silence.

---

## Ajouter un client

Deux fichiers, jamais plus.

**1. Un lecteur** — `lecteurs/<client>.py` — qui rend un `Catalogue` à partir du
fichier que son site sert déjà. Les deux existants tiennent en 60 lignes ;
`lecteurs/js_litteral.py` lit un littéral JS/TS **sans jamais exécuter de code**.

**2. Une fiche** — `maisons/<client>.yaml` — le ton, les horaires, la livraison,
le paiement, ce qui part toujours à un humain, ce que la maison n'a pas tranché.
**Aucun prix** : un prix dans une fiche est une deuxième vérité, et le QC le
refuse.

---

## Ce que ça coûte

Sur `claude-sonnet-5` (2 $ / M en entrée, 10 $ / M en sortie), la carte d'Au
Braisé d'Or fait un socle d'environ **1 800 jetons**, posé dans un bloc mis en
cache.

| Une conversation de 10 messages | Entrée | Coût |
|---|---|---|
| cache chaud (messages rapprochés) | ~5 800 jetons | **≈ 16 F CFA** |
| cache froid (cache expiré à chaque tour) | ~19 800 jetons | **≈ 33 F CFA** |

*Hypothèses : ~200 jetons par message entrant, ~150 en sortie, 607 F CFA pour
1 $. Le compte de jetons du socle est estimé (caractères ÷ 4) : à confirmer avec
`messages.count_tokens` le jour où une clé est en place.*

Côté Meta, une conversation **de service** — le client écrit, on répond dans les
24 h — est gratuite jusqu'à 1 000 par mois.

---

## Ce qu'il faut savoir avant de vendre

**La fenêtre de 24 heures.** WhatsApp n'autorise un message libre que dans les
24 h suivant le dernier message de la personne. Répondre à un client est donc
toujours permis. **Prévenir le patron ne l'est pas toujours** : s'il n'a rien
écrit à son propre agent depuis la veille, l'alerte ne part pas. Le kit le
journalise fort et garde l'escalade en base — mais **une relance automatique
demandera un modèle pré-approuvé par Meta**, ce qui n'est pas encore fait.

**Ce que le garde-fou ne fait pas.** Il vérifie qu'un montant existe et qu'il
correspond à l'article nommé dans la même phrase. Un montant **tout seul**
(« ça vous fera 4 500 F ») n'est vérifiable que comme addition possible de la
carte — et c'est faible : mesuré sur Au Braisé d'Or, **90 % des montants ronds**
sont atteignables en six articles ou moins. Chez Hillary, dont les prix sont
gros et espacés, c'est 2 %. C'est pour ça que le prompt exige de **nommer
l'article qu'on chiffre**, et c'est pour ça que le contrôle par attachement
existe.

**Ce qui n'est pas fait.** Les vocaux (le client envoie un audio → passé à un
humain, pas transcrit), les images, les relances hors fenêtre, le paiement.

---

## Décisions qui attendent Mongazi

1. **⛔ Le numéro d'Au Braisé d'Or.** Le dépôt en porte **deux différents** :
   `index.html` dit `2290156057157`, `dishes.ts` — le fichier réellement servi —
   dit `22956057157`, sans le `01`. L'enseigne affiche `43 99 29 29`. La fiche
   est **vide exprès** : choisir ici, ce serait envoyer les commandes d'un
   restaurant sur un numéro deviné.
2. **Le numéro qui reçoit les alertes**, pour chaque maison.
3. **Par quel client commencer.** Au Braisé d'Or a le plus à gagner (52 plats,
   commandes le soir) ; Hillary a le catalogue le plus propre.
4. **Meta ou Twilio** pour le premier essai. Twilio en une heure sur un numéro
   partagé pour montrer que ça marche ; Meta pour livrer.

---

## Les fichiers

| | |
|---|---|
| `agent/catalogue.py` | ce que la maison vend · **les cinq façons d'avoir un prix** |
| `agent/garde_prix.py` | **le garde-fou** · attachement, fourchettes, sommes |
| `agent/cerveau.py` | le prompt, les outils, la boucle Claude |
| `agent/memoire.py` | l'historique, la fenêtre de 24 h, la main humaine |
| `agent/service.py` | un message entre, une réponse sort, la maison est prévenue |
| `agent/maison.py` | la fiche d'un client, et ce qui l'empêche de démarrer |
| `lecteurs/` | un lecteur par client + le lecteur de littéraux JS/TS |
| `canaux/` | Meta Cloud API · Twilio · console |
| `serveur.py` | le webhook (bibliothèque standard, en threads) |
| `simuler.py` | parler à l'agent dans un terminal |
| `_qc.py` | **146 contrôles**, sans clé et sans réseau |
