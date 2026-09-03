# 2026-09-03 · SasPay : l'API est trouvée, la clé fonctionne

*Suite de `2026-09-03-piste-saspay.md`, écrit le même jour depuis le nuage.*

## Le point de départ : deux moitiés qui ne s'étaient jamais rencontrées

Mongazi : « vérifie en mémoire j'ai mis le code secret api pour saspay dans le
dossier secret ». C'était vrai, et ce n'était pas le sujet.

`secrets/saspay.env` existait bien, écrit à 17:42, trois lignes, les bons noms.
Mais **« saspay » n'apparaissait nulle part ailleurs sur le disque** : tout le
code du paiement dormait sur `origin/claude/saspay-payment-integration-fv2rdt`,
quatre commits, 1 629 lignes, jamais fusionnés. Une session du téléphone avait
écrit le paiement, le PC avait reçu la clé, et personne n'avait mis les deux
ensemble.

⚠️ **C'est exactement le piège n°1 du dépôt**, et il s'est présenté d'une
manière nouvelle : la question portait sur un fichier, pas sur une branche.
Vérifier « est-ce que le fichier est là » aurait répondu oui et fermé le sujet.
Ce qui a ouvert le vrai problème, c'est **`git log --all -S "saspay"`** : la
recherche dans le répertoire de travail ne rendait rien, l'historique de
**toutes** les branches rendait quatre commits.

## Ce que le PC pouvait faire et que le nuage ne pouvait pas

Le code avait été écrit **à l'aveugle** : `docs.saspay.me` répondait 403 à la
machine du nuage, et rien de leur API n'est publié ailleurs. D'où sa forme,
volontairement défensive : chaque valeur incertaine était un réglage.

⛔ **Depuis le PC de Cotonou, `docs.saspay.me` répond 200.** Le 403 était un
filtre de sortie, pas une absence. La documentation est un site Mintlify, donc
elle publie `/llms-full.txt` (84 Ko) et son OpenAPI (102 Ko). Tout était là.

⚠️ **La leçon n'est pas « le PC est meilleur »**, c'est qu'un refus réseau
appartient à la machine qui l'a reçu, pas au service. Le premier réflexe utile
a été de refaire l'essai depuis l'autre machine.

## Le pari du « tout est réglable » : payé à moitié

Adresse, en-tête, préfixe : corrigés par des réglages, sans toucher au code.
C'était le pari, il tient.

Mais **cinq choses ont demandé du code, parce que ce sont des formes et pas des
valeurs** :

| Supposé | Vrai |
|---|---|
| `POST /v1/checkout/sessions` | `POST /api/v1/checkout-sessions/` |
| `amount` est un nombre | une **chaîne décimale** `"5000.00"` |
| `success_url` + `cancel_url` | `return_url` seule, succès uniquement |
| le client est optionnel | `customer_email` **et** `customer_name` requis |
| la signature couvre le corps | elle couvre `horodatage + "." + corps` |

⚠️ **Un réglage rattrape une valeur, jamais une forme.** C'est la limite de la
méthode, et elle mérite d'être connue avant d'écrire le prochain connecteur à
l'aveugle.

## Le piège que rien n'aurait rattrapé

⛔ **La notification ne dit pas quelle commande elle paie.**
`transaction.success` porte l'identifiant de la transaction, la référence de
SasPay (« TXN-2026-000456 »), les montants, le réseau. **Ni `metadata`, ni le
numéro de session, ni la description.**

Pire : **son champ s'appelle `reference`, comme le nôtre.** La lecture des
messages cherche en largeur d'abord, donc `data.reference` (2 niveaux)
l'emportait sur `data.metadata.reference` (3 niveaux) : le numéro de SasPay
remplaçait le nôtre **sans un mot**. Le code portait déjà un commentaire
avertissant de cette famille de bug, écrit deux semaines plus tôt, et la
collision est arrivée quand même — un nom partagé ne se devine pas, il se
mesure sur un vrai message.

Ce qui rattrape le lien : **la session de checkout garde `metadata` et
`description`** (relu sur trois sessions réelles) et son champ `transaction`
se remplit quand elle est payée. D'où `referenceParTransaction()`.

⏳ **Ce maillon reste le seul non prouvé** : vérifier que `transaction` se
remplit demande un paiement réel. Son échec ne fait rien d'autre qu'écrire
« sans commande » au journal. On ne livre pas sur une supposition.

## La preuve

La sonde, corrigée, a **ouvert une vraie session de checkout : HTTP 201**, avec
la clé de `secrets/saspay.env`.

- `Authorization: Bearer` ✅ (les trois autres formes rendent 401)
- ⚠️ **Le montant minimum est de 200 XOF** : le premier essai à 100 F a été
  refusé, et c'est le message d'erreur qui l'a appris. Sans conséquence
  commerciale, PISTE vend au minimum 1 000 F.
- Deux écarts entre la doc et la réalité : la réponse est enveloppée dans
  `{success, data:{…}}` (l'exemple montre l'objet nu) et l'adresse de paiement
  est sur **`checkout.saspay.me`**, pas `pay.saspay.me`. **La doc est un
  indice, la réponse est la preuve.**
- Les trois sessions d'essai ont été **annulées**.

## Deux manques trouvés en chemin

1. ⛔ **Le contrôle d'âge du webhook n'existait pas.** Une signature ne périme
   jamais : sans borne, un message légitime intercepté se rejoue indéfiniment
   et paie la même commande autant de fois qu'on veut. Cinq minutes, et
   l'horodatage étant *dans* la signature, on ne peut pas le rajeunir.
2. ⚠️ **Le QC ne démarrait pas sur le PC** : il importe un `.ts`, que Deno lit
   nativement et que Node 22 refuse (`ERR_UNKNOWN_FILE_EXTENSION`). La commande
   documentée ne pouvait pas marcher ici, là où le nuage la lançait sans y
   penser. Même famille que les trois pannes d'instrument du 2026-08-19.

## État

**QC 64 → 89 contrôles, tous verts.** Tout est dans `main` et poussé.

⏳ Il reste **deux choses avant le premier franc** : le **secret de signature**
(encore un gabarit dans `secrets/saspay.env`, à copier depuis le dashboard
SasPay onglet Webhooks — ⚠️ **il ne se réaffiche jamais**), et le **paiement
réel de 200 F** qui prouvera le dernier maillon. `SASPAY_PRET` reste `false`.
