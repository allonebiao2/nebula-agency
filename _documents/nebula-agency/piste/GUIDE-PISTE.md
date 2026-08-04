# PISTE · LA MÉTHODE COMPLÈTE
## Tout faire tourner, sans rien oublier

> Écrit le 4 août 2026, le jour où PISTE est entré en service.
> Ce guide est pour Mongazi. Il dit **les gestes**, **les prix**, **les pièges**
> et **les phrases**. Il ne dit pas comment le produit est codé : ça, c'est
> dans `piste/PRODUCT.md`.

---

# 1 · CE QU'ON VEND, EN UNE PHRASE

**Le client dit qui il cherche, on lui livre un carnet de commerces réels, avec
le message déjà écrit pour chacun.**

Ce n'est pas un fichier Excel. C'est un carnet qu'on ouvre sur son téléphone,
où on appuie sur une fiche, et la conversation WhatsApp démarre avec le bon
message. C'est cette différence-là qui justifie le prix.

**L'adresse : piste.nebula-agency.online**

| | |
|---|---|
| Votre cockpit | `piste.nebula-agency.online/#/cockpit` |
| Le carnet d'un client | `…/#/carnet/<jeton>` |
| Son reçu | `…/#/recu/<jeton>` |

---

# 2 · LES SIX GESTES D'UNE COMMANDE

## Geste 1 · La commande arrive

Elle vous arrive de **trois côtés à la fois**, et c'est voulu :

- sur votre **WhatsApp**, le message commence par `PISTE COMMANDE · 50 fiches · 4 500 F`
- dans votre **boîte mail**, même sujet
- dans la **base**, où elle est enregistrée quoi qu'il arrive

⚠️ **Même si le client ne vous écrit jamais, la commande existe.** C'est
exactement ce qui avait été perdu sur le site de l'agence le 4 août : une
demande partie sur WhatsApp mais nulle part en base.

Collez le message dans votre cockpit pour en garder une copie de travail.

## Geste 2 · Vérifier le paiement

Ouvrez MTN MoMo. **Cherchez le NUMÉRO et le NOM que l'acheteur a déclarés** :
c'est ce qui s'affiche à la réception, pas la référence de commande.

Le numéro de dépôt est le **01 96 74 07 32**, au nom de BIAO Mongazi Yan Karl.

⚠️ **Ce n'est pas votre numéro WhatsApp.** Le site le dit au client en rouge,
mais rappelez-le si vous voyez le moindre doute. Un dépôt envoyé au mauvais
numéro, c'est le geste le plus coûteux qui existe.

Quand l'argent est là, marquez **« payée »** dans le cockpit.

## Geste 3 · Fabriquer le carnet · UN SEUL BOUTON

Dans le cockpit, sur une commande marquée « payée », appuyez sur
**« Fabriquer et envoyer le carnet »**.

Le serveur fait tout, sans vous :
- il choisit les fiches libres, en **alternant** entre les métiers demandés
- il compose le message d'approche de chacune, à partir de ce que le client vend
- il **réserve les fiches 90 jours** pour ce client seul
- il **envoie le lien au client** par email, et à vous aussi

Le mot de passe du cockpit vous est demandé **une seule fois**, puis gardé dans
ce navigateur. Il est dans `secrets/piste.env`.

⚠️ **Un double clic ne livre pas deux fois.** La deuxième fois, le serveur rend
le lien existant. Sinon les fiches seraient réservées deux fois et le client
recevrait deux liens différents.

⚠️ **Si le stock ne suffit pas**, rien n'est fabriqué et le cockpit vous dit
combien de fiches sont réellement libres. La commande ne bouge pas, vous pouvez
réessayer après une nuit de collecte.

### La voie de secours, sur le PC

Si le serveur ne répond pas, ou pour composer un carnet à la main :

```
python piste/_carnet.py --metier restaurant,alimentation --ville cotonou --n 50 \
  --options teste,message --offre "ce qu'il vend, en une phrase" \
  --prenom Adjoa --nom Kponou --email adjoa@exemple.com --tel 22997000000 \
  --ref PISTE-4471 --ecrire
```

Pour voir ce qui est disponible avant de composer :
```
python piste/_carnet.py --voir
```

Elle fait la même chose que le bouton, et écrit en plus une copie dans
`piste/_carnets/PISTE-4471.txt`.

## Geste 4 · Si « numéro testé » est coché, vous appelez

**Chaque numéro, avant l'envoi.** L'outil vous le rappelle mais il ne peut pas
composer à votre place.

Une fiche qui ne répond pas **ne part pas** : vous la remplacez par une autre.
C'est ce que le client a payé 60 F de plus par fiche. Ne cochez jamais cette
option à la légère.

## Geste 5 · Envoyer sur WhatsApp aussi

L'email est parti tout seul. Dans le cockpit, sur une commande payée, le bouton
**« Envoyer sur son WhatsApp »** ouvre sa conversation avec le message déjà
écrit. Il ne reste qu'à coller le lien.

Puis marquez **« livrée »**.

## Geste 6 · Une semaine après, relancer

```
python piste/_carnet.py --relances
```

Ça vous rend un message écrit **à partir de SES résultats** : « vous avez
marqué 2 rendez-vous et 1 vente ». Vous n'avez qu'à envoyer.

**Ce message n'est pas de la politesse.** C'est la seule façon de savoir si vos
fiches valent quelque chose. Tant qu'aucun client n'a dit « 12 sur 50 m'ont
répondu », votre barème est une hypothèse.

---

# 3 · LES PRIX, ET CE QU'ON PROMET

## Le barème

**Une fiche coûte entre 100 F et 250 F, jamais plus.**

| | |
|---|---|
| **La fiche de base** | **100 F** — nom, métier, ville, quartier, téléphone |
| Le numéro est testé | **+60 F** — la ligne sonne, le compte WhatsApp existe |
| Il n'a rien en ligne | **+40 F** — ni site, ni page qui tourne |
| Le nom du dirigeant | **+30 F** — pour dire son nom au lieu de « bonjour » |
| Le message déjà écrit | **+20 F** — rédigé pour ce commerce, à partir de ce qu'il vend |

Les quatre réunis font exactement 150 F. **250 F est un plafond, pas une
suggestion.**

## Les remises

| 50 fiches | 200 fiches | 500 fiches |
|---|---|---|
| −10 % | −20 % | −30 % |

## Ce qu'on promet, mot pour mot

- **Minimum 10 fiches.** En dessous, on ne vend pas : on prend la demande.
- **Livré sous 24 heures.** Pas « jours ouvrés », pas d'horaire. 24 heures.
- **Exclusivité 90 jours.** Les fiches d'un client ne repartent chez personne
  d'autre pendant trois mois. C'est vérifié dans l'outil, pas promis en l'air.
- **Toute fiche injoignable est remplacée sans frais.** Le client appuie sur un
  bouton dans son carnet, ça vous arrive par email.
- **Le lien du carnet ne périme pas.** Il est à lui, à vie.
- **MTN MoMo seul.** Pas de Moov, pas de Wave, pas de virement.

## Ce qu'on ne promet PAS

- Qu'un commerce va répondre. On vend un contact, pas un client.
- Qu'un numéro sera joignable, **sauf** si l'option « numéro testé » est payée.
- Une facture normalisée. Le reçu est un reçu, c'est écrit dessus.
- Un paiement depuis le Togo ou la Côte d'Ivoire : **jamais testé**. Si un
  client de Lomé ou d'Abidjan veut acheter, écrivez-lui d'abord.

---

# 4 · LES PIÈGES, ET COMMENT NE PAS Y RETOMBER

## Le dépôt GitHub est PUBLIC

`allonebiao2/nebula-agency` est lisible par tout le monde. **La marchandise ne
doit jamais y revenir.** Les fiches et leurs numéros vivent dans Supabase.

Un jour, quelqu'un aura envie de « juste sauvegarder le fichier des prospects »
dans le dépôt. Ce jour-là, PISTE devient gratuit pour qui trouve le dépôt.

## Un site qui s'affiche sans style

Cloudflare peut mettre une **erreur en cache à la place d'un fichier**, pour un
an. C'est arrivé à PISTE le 4 août : la page apparaissait en texte noir sur
blanc, sans police, sans couleur.

```
python scripts/purger.py --verifier    regarde ce qui est vraiment servi
python scripts/purger.py               vide le cache des 5 sites
```

⚠️ **Un code 200 ne prouve rien.** Ce jour-là, tous les en-têtes étaient
parfaits ; seul le contenu du fichier révélait l'erreur.

## Les numéros

- **Bénin** : 10 chiffres depuis le 1er janvier 2025. Un numéro à 8 chiffres
  est un numéro **mort**.
- **Sauf sur WhatsApp** : un compte peut être resté enregistré sur l'ancien
  numéro à 8 chiffres. C'est le cas du vôtre. Le site accepte donc les deux.
- **Le Mobile Money, lui, fait toujours 10 chiffres.** Le site ne complète
  jamais tout seul : il dit ce qui manque et laisse corriger. Compléter en
  silence un numéro de paiement, c'est faire perdre de l'argent à quelqu'un.
- **Côte d'Ivoire** : 10 chiffres depuis le 31 janvier 2021.

## Le numéro de dépôt n'est pas le numéro WhatsApp

Écrit deux fois dans ce guide parce que ça vaut deux fois.

## Le vivier se vide

Chaque vente **retire** ses fiches du stock pendant 90 jours. Sept commandes de
30 fiches, et une catégorie est épuisée. Le moteur recollecte chaque nuit, mais
surveillez :

```
python piste/_moteur.py --voir
python piste/_stock.py          pour que le site affiche le vrai stock
```

⚠️ **Lancez `_stock.py` après chaque grosse collecte**, sinon le site continue
d'annoncer d'anciens chiffres.

---

# 5 · CE QU'ON RÉPOND

## « C'est combien ? »

> À partir de 100 francs la fiche. Vous choisissez ce que vous voulez dedans,
> le prix s'affiche pendant que vous réglez. Le maximum, tout compris, c'est
> 250 francs.

Ne jamais donner un total avant qu'il ait dit ce qu'il cherche.

## « Comment je sais que c'est vrai ? »

> Vous voyez trois vraies fiches avant de payer, avec le nom, le quartier et le
> numéro. Les quatre derniers chiffres sont masqués, le reste est là. Prenez
> deux minutes, je vous montre.

**C'est votre meilleur argument. Montrez le générateur, ne le décrivez pas.**

## « Et si personne ne répond ? »

> Une fiche injoignable est remplacée sans frais, il y a un bouton dans le
> carnet. Et si vous prenez l'option « numéro testé », j'appelle chaque numéro
> avant de vous l'envoyer : celui qui ne répond pas ne part pas.

## « C'est légal ? »

> Ce sont des commerces, pas des particuliers. Nom, métier, adresse, téléphone
> publié : ce sont des informations qu'ils ont eux-mêmes rendues publiques pour
> qu'on les appelle. Un commerce qui demande à sortir de la base en sort, et ne
> revient dans aucune livraison.

## « Je peux avoir une facture ? »

> Vous recevez un reçu avec votre carnet, imprimable. Si votre comptabilité
> exige une facture normalisée, dites-le moi maintenant plutôt qu'au moment de
> votre déclaration.

## « C'est cher pour une liste »

> Ce n'est pas une liste. Vous ouvrez le carnet sur votre téléphone, vous
> appuyez sur un commerce, WhatsApp s'ouvre avec le message déjà écrit pour
> lui. Vous ne recopiez rien, vous ne réfléchissez pas à quoi dire. Une liste,
> ça se fait à la main en une soirée. Ça, non.

## « Je vais réfléchir »

> Bien sûr. Juste pour savoir : c'est le montant, le moment, ou vous voulez
> voir à quoi ressemble une fiche d'abord ?

**Ne partez jamais sans savoir laquelle des trois.**

---

# 6 · TROUVER LES DIX PREMIERS ACHETEURS

## Qui c'est

**Celui qui vend AUX commerçants.** Grossiste en boissons, assureur,
fournisseur de matériel, banque, agence de communication, imprimeur.

⚠️ **Pas un commerçant.** Un restaurant cherche des particuliers qui viennent
manger : votre vivier ne contient que des commerces, vous lui vendriez la
mauvaise chose.

## La méthode : WhatsApp d'abord

**Un statut par jour, pendant deux semaines.** Court, tenable entre deux
rendez-vous, et assez long pour savoir si ça mord. Au bout de deux semaines
vous saurez : soit des gens écrivent, soit il faut changer de porte.

Trois choses à publier, en rotation :

**1. La démonstration de 30 secondes.** Filmez votre écran : vous choisissez un
métier, une ville, le prix s'affiche, trois vraies fiches apparaissent.
Personne ne résume PISTE mieux que PISTE en action. Passe aussi sur TikTok et
Instagram.

**2. Le chiffre brut.**
> 7 817 commerces du Bénin, du Togo et de Côte d'Ivoire, avec leur numéro
> WhatsApp. Restaurants, couture, quincaillerie, garages, écoles, pharmacies.
> Vous choisissez, vous recevez le carnet sous 24 h.
> piste.nebula-agency.online

**3. Le problème raconté.**
> Vos clients existent déjà.
> Ils sont juste introuvables.
>
> Vous passez vos journées à chercher qui démarcher. Pendant ce temps, 7 817
> commerces attendent qu'on leur parle, avec leur numéro WhatsApp.
> piste.nebula-agency.online

## Ce qui convertit vraiment

**Le générateur, montré en direct, sur votre téléphone.** Deux minutes. Il
choisit son métier, il voit le prix monter, il voit trois vraies fiches.

Ne racontez pas PISTE. Ouvrez-le.

## Ce qu'il ne faut pas faire

- **Ne pas baisser le prix pour la première vente.** Un prix cassé se sait, et
  le client suivant le demandera aussi.
- **Ne pas promettre de résultat.** Vous vendez des contacts, pas des clients.
  Un seul client déçu par une promesse fait plus de mal que dix ventes ratées.
- **Ne pas publier dans un groupe où vous n'avez jamais parlé.** On vous
  sortira, et vous perdrez le groupe pour de bon.

## Comment savoir si ça marche

Au bout de deux semaines, comptez **les conversations, pas les vues**. Trois
personnes qui écrivent valent mieux que mille vues.

Si personne n'écrit, ce n'est pas le produit : c'est la porte. On en essaiera
une autre.

---

# 7 · LA DÉCISION QUI RESTE À PRENDRE

**PISTE est à vous seul pour l'instant** : vos partenaires NEBULA ne le vendent
pas et ne touchent rien dessus.

C'est cohérent tant que vous cherchez vos premiers acheteurs vous-même. Mais
vous avez huit personnes qui démarchent déjà des commerçants tous les jours,
avec un contrat signé. Le jour où PISTE aura fait ses premières ventes et où
vous saurez ce qu'il rapporte vraiment, **c'est la porte la plus courte vers le
volume.**

Gardez-la en tête. Ne l'ouvrez pas avant d'avoir vendu vous-même : on ne
demande pas à quelqu'un de vendre ce qu'on n'a jamais vendu.
