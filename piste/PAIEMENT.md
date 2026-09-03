# PISTE · le paiement en ligne (SasPay)

*Écrit le 2026-09-03. Rien n'est branché : le drapeau est fermé, le site
n'affiche aucun bouton « payer », et le Mobile Money à la main marche comme
avant.*

---

## 1. Ce que ça change, et ce que ça ne change pas

Aujourd'hui (décision 27) : le client envoie son virement, une capture d'écran
sur WhatsApp, et **Mongazi rapproche à la main** dans son application MoMo.

Avec SasPay : le client paie depuis la page, et la commande se marque **payée
toute seule**. Le gain n'est pas le bouton, c'est **la notification** : c'est
elle qui supprime le rapprochement manuel.

⛔ **Ce qui ne change pas, volontairement.** La fabrication du carnet reste un
geste de Mongazi, dans le cockpit. Tant que la forme exacte des messages SasPay
n'est pas confirmée, laisser partir de la marchandise sur un message mal
compris serait le seul geste vraiment coûteux. On automatise l'encaissement,
pas encore la livraison.

---

## 2. Où on en est

**✅ Les opérateurs sont confirmés** (Mongazi, 2026-09-03) : le compte encaisse
sur **tous les MTN et tous les Moov Africa**. C'est plus large qu'espéré, et ça
touche directement ce que PISTE peut vendre.

⚠️ **Ce que ça débloque, et qu'il ne faut pas annoncer trop tôt.** Le §9 de
`PRODUCT.md` garde depuis le début une réserve : « le paiement depuis le Togo
et la Côte d'Ivoire vers un compte béninois, non testé ». Le vivier compte
7 817 fiches sur **trois pays**, et l'écran de paiement dit encore « MTN MoMo,
au Bénin ; si vous payez depuis un autre pays, écrivez-nous d'abord ». Si un
client togolais ou ivoirien peut payer seul, c'est le plus gros verrou
commercial de PISTE qui saute. ⛔ **Mais on ne change pas cette phrase avant
d'avoir encaissé pour de vrai depuis Lomé ou Abidjan.** La règle n'a pas
changé : ne rien promettre avant d'avoir envoyé 1 000 F.

**✅ La devise est confirmée** (Mongazi, 2026-09-03) : le compte propose **XOF**,
XAF et d'autres. Le CDF vu sur la première capture n'était donc que la devise
sélectionnée par défaut, pas la seule disponible. Le doute commercial est levé.

**✅ La forme technique de leur API est trouvée** (2026-09-03, depuis le PC) :
adresse, en-tête, noms de champs, schéma de signature. La sonde a ouvert une
vraie session de checkout, **HTTP 201**, avec la clé de `secrets/saspay.env`.
Détail des cinq écarts au §5. Les trois sessions d'essai ont été annulées.

**⏳ Ce qui reste : le vrai encaissement.** Tant que le premier franc n'est pas
arrivé, **`SASPAY_PRET` reste `false`** dans `src/donnees.js`. Deux choses
n'ont pas pu être vérifiées sans payer :

1. **le lien entre la notification et la commande** (§5) — la seule inconnue
   qui empêche encore l'encaissement automatique de fonctionner ;
2. **le secret de signature**, qui est encore un gabarit dans
   `secrets/saspay.env` : il se copie depuis le dashboard SasPay, onglet
   Webhooks, et **ne se réaffiche jamais** après sa création.

⚠️ **Le montant minimum est de 200 XOF**, mesuré. Sans conséquence : PISTE vend
au minimum 10 fiches à 100 F, donc 1 000 F.

⚠️ **Un compte multi-pays n'est pas un compte multi-devises pour PISTE.** Le
verrou reste `XOF`, ce qui couvre exactement les trois marchés du vivier
(Bénin, Togo, Côte d'Ivoire sont tous en franc CFA de l'UEMOA) et refuse tout
le reste. MTN Cameroun encaisse en XAF, MTN Ghana en GHS, MTN Nigeria en NGN :
ces paiements-là seront refusés et journalisés, et c'est le comportement voulu.
PISTE ne vend pas de fiches dans ces pays.

## 3. Où vit chaque morceau

| Fichier | Ce qu'il fait |
|---|---|
| `supabase/paiement.sql` | les deux tables et les quatre portes serveur. **À jouer une fois** dans l'éditeur SQL Supabase. Rejouable |
| `supabase/functions/_shared/saspay.ts` | **tout ce qu'on ne sait pas encore de SasPay**, plus les gardes de la caisse (`decider`) |
| `supabase/functions/piste-paiement/` | ouvre une session de paiement. C'est ici que vit la clé secrète |
| `supabase/functions/piste-paiement-recu/` | reçoit la notification, vérifie, marque « payée » |
| `src/donnees.js` → `SASPAY_PRET` | l'interrupteur. `false` = le site ne montre rien |
| `src/composants/Paiement.jsx` → `EnLigne` | le bouton, au-dessus du Mobile Money à la main |
| `_qc_paiement.mjs` | **89 contrôles, sans clé, sans réseau, sans base** |

⚠️ **Ces fichiers sont la source.** Comme `piste-cockpit`, ils tournent chez
Supabase mais ils vivent ici. Ce qui n'est écrit que dans l'éditeur Supabase
n'est relu par personne et disparaît avec le projet.

---

## 4. Brancher, le jour venu

```bash
# 0. trouver l'adresse et l'en-tête (depuis le PC de Cotonou, pas le nuage)
node _saspay_sonde.mjs
#    → elle balaie les adresses plausibles, lit les codes de retour, et
#      n'écrit les `supabase secrets set` QUE si elle a vraiment parlé à SasPay.
#    ⚠️ Un 401 dit qu'une porte existe, pas que c'est la bonne : elle refuse
#      alors de tendre une commande, et renvoie à l'onglet « Développeur ».

# 1. la base (éditeur SQL Supabase, une seule fois)
#    → contenu de supabase/paiement.sql

# 2. les secrets — ⛔ JAMAIS dans le dépôt, il est PUBLIC
supabase secrets set SASPAY_CLE_SECRETE=...        # la clé secrète SasPay
supabase secrets set SASPAY_SECRET_WEBHOOK=...     # le secret de signature
supabase secrets set SASPAY_DEVISE=XOF
#    Les autres réglages ont désormais le bon défaut dans le code : rien à
#    poser, sauf si SasPay change quelque chose (table du §5).

# 3. les fonctions
supabase functions deploy piste-paiement
supabase functions deploy piste-paiement-recu --no-verify-jwt

# 4. dans le tableau de bord SasPay, onglet « Webhooks », déclarer :
#    https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/piste-paiement-recu

# 5. le contrôle, avant tout
node --experimental-strip-types _qc_paiement.mjs   # ou : npm run qc:paiement
```

### ⛔ « Clé API invalide » sur une clé valable : regarder les fins de ligne

Arrivé le 2026-09-03. Le fichier `secrets/saspay.env` avait été réécrit par un
outil Windows, donc en **CRLF**. Le lecteur de la sonde coupait sur `'
'`, le
`'
'` restait collé en fin de ligne, et comme « . » ne traverse pas un retour
chariot en JavaScript, le `$` de sa regex ne s'accrochait plus à rien :
**aucune ligne lue**, `Bearer undefined` envoyé, et SasPay répondant « Clé API
invalide » sur six routes d'affilée.

⚠️ **Le message d'erreur accusait la clé, le coupable était un octet
invisible.** Ce qui a tranché en trois secondes : la même clé, extraite par
`sed` et envoyée par `curl`, répondait **200**. Quand un outil échoue et qu'un
autre réussit sur la même donnée, le défaut est dans l'outil.

Le lecteur coupe désormais sur `/
?
/`. ⚠️ Et la règle de la maison sur les
écritures de fichiers (Node/Python en UTF-8, jamais PowerShell) vaut aussi
pour les **fins de ligne**, pas seulement pour les accents.

### ✅ 2026-09-03 · la base est installée, et elle a corrigé deux erreurs

`paiement.sql` est **joué** sur le projet PISTE : 2 tables (RLS activée) et 4
fonctions, vérifiées en lisant une vraie commande. Le garde-fou du bloc 0 a
servi deux fois, exactement comme prévu.

⛔ **La table s'appelle `piste.commandes`, au pluriel.** Le fichier disait
`piste.commande` et s'est arrêté net plutôt que de s'installer à moitié.

⛔ **Et surtout : la base et l'application ne parlent pas la même langue.** La
contrainte de `piste.commandes` n'accepte que
`attente / paye / livre / expire / annule`. Le webhook écrivait **`payee`**, que
la base **refuse** (mesuré en transaction annulée). Conséquence si personne ne
l'avait vu : **le client paie, SasPay confirme, et la commande reste « en
attente »** — le défaut n'apparaissant qu'au premier paiement réussi, c'est-à-dire
au pire moment possible.

⚠️ Le même écart cassait le garde « déjà payée » : il ne comparait qu'à `payee`
et `livree`, donc il **ne se serait jamais déclenché**, et une notification
rejouée aurait re-marqué payée une commande déjà payée. Il accepte désormais
les deux orthographes.

⚠️ **Ce n'est pas propre au paiement** : `piste-cockpit/index.ts` et
`Cockpit.jsx` emploient partout `payee` / `livree` / `annulee`, et la table
n'en accepte aucun. **À vérifier sur le cockpit déployé** — hors du périmètre
de cette vague, mais si le bouton « Marquer payé » n'a jamais fonctionné,
c'est là que ça se joue.

Un contrôle du QC lit désormais le fichier du webhook et refuse tout état que
la contrainte n'accepte pas.

### Où vit la clé, et où elle ne vit pas

| Endroit | Quoi |
|---|---|
| `supabase secrets set` | **la vraie place.** C'est de là que la fonction la lit |
| `secrets/saspay.env`, sur le PC de Cotonou | la copie de sauvegarde. `secrets/` est ignoré par git (`.gitignore` ligne 24) |
| `.env.example` | la **forme** des variables, sans aucune valeur. C'est le seul des trois qui est versionné |

⛔ **Jamais dans le dépôt, jamais dans une vitrine, jamais dans un paquet
JavaScript.** Le dépôt est public et le site est statique.

⚠️ **Une clé qui a transité par une conversation, un courriel ou une capture
d'écran est à considérer comme connue de tiers : on la fait tourner.** Chez
SasPay comme ailleurs, révoquer et régénérer coûte une minute ; un encaissement
détourné coûte le chiffre d'affaires.

⛔ `--no-verify-jwt` n'est pas une négligence : SasPay n'a pas de jeton Supabase
à présenter. Ce qui protège cette porte, c'est **la signature**.

---

## 5. Se tromper ne doit rien coûter

Le jour où ce code a été écrit, `saspay.me` et `docs.saspay.me` étaient
**injoignables** depuis la machine qui l'écrivait (le filtre de sortie répond
403 sur ces deux domaines), et rien de leur API n'est publié ailleurs. Aucune
adresse, aucun nom de champ n'a donc pu être vérifié.

D'où la façon dont c'est écrit : **chaque valeur incertaine est un réglage**.
Corriger une hypothèse, c'est une commande, pas une modification de code.

### ✅ 2026-09-03, depuis le PC de Cotonou : ce n'est plus une hypothèse

`docs.saspay.me` répond **200 depuis le PC** — le 403 était un filtre du nuage,
pas une absence. La doc publie son OpenAPI (`/api-reference/openapi.json`) et
un `llms-full.txt`. Puis la sonde a **vraiment ouvert une session** avec la
clé du dossier `secrets/` : **HTTP 201**.

⚠️ **Le pari du « tout est réglable » a payé, mais pas partout.** Adresse,
en-tête et préfixe se sont corrigés par des réglages. Cinq choses ont demandé
du code, parce qu'elles ne sont pas des valeurs mais des **formes** :

| Ce qu'on supposait | Ce qui est vrai |
|---|---|
| `POST /v1/checkout/sessions` | **`POST /api/v1/checkout-sessions/`** — le `/api` et la barre finale |
| `amount` est un nombre | **une chaîne décimale** : `"5000.00"` |
| `success_url` + `cancel_url` | **`return_url` seule**, et seulement sur succès |
| le client est optionnel | **`customer_email` et `customer_name` sont REQUIS** |
| la signature couvre le corps | elle couvre **`horodatage + "." + corps`** |

⛔ **Et une chose qu'aucun réglage n'aurait rattrapée : la notification ne dit
pas quelle commande elle paie.** `transaction.success` porte l'identifiant de
la transaction, la référence de SasPay (« TXN-… »), les montants et le réseau.
**Ni `metadata`, ni le numéro de session, ni la description.** Pire, son champ
s'appelle `reference` comme le nôtre : la recherche allant en largeur d'abord,
le numéro de SasPay écrasait le nôtre sans un mot.

Ce qui rattrape le lien : **la session de checkout garde `metadata` et
`description`** (relu sur trois sessions réelles) et son champ `transaction` se
remplit quand elle est payée. `referenceParTransaction()` repart donc de
l'identifiant de transaction pour retrouver la session, donc la commande.

⏳ **Ce point reste le seul non prouvé** : que `transaction` se remplisse
vraiment demande un paiement réel. En attendant, l'échec de cette route ne
fait rien d'autre qu'écrire « sans commande » au journal. **On ne livre pas sur
une supposition.**

⚠️ Deux écarts entre la doc et la réalité, relevés au passage : la réponse est
enveloppée dans `{success, data:{…}}` (l'exemple de la doc montre l'objet nu),
et l'adresse de paiement est sur **`checkout.saspay.me`**, pas `pay.saspay.me`.
Les deux sont sans conséquence ici — on lit les champs par leur nom, à
n'importe quelle profondeur — mais c'est le rappel que **la doc est un indice,
la réponse est la preuve**.

| Réglage | Défaut supposé | À corriger si… |
|---|---|---|
| `SASPAY_BASE` | `https://api.saspay.me` | ✅ confirmé |
| `SASPAY_CHEMIN_SESSION` | `/api/v1/checkout-sessions/` | ✅ confirmé (le `/api` et la barre finale manquaient) |
| `SASPAY_ENTETE_CLE` | `Authorization` | ✅ confirmé |
| `SASPAY_PREFIXE_CLE` | `Bearer ` | ✅ confirmé (sans lui : 401) |
| `SASPAY_ENTETE_SIGNATURE` | `x-webhook-signature` | ✅ confirmé |
| `SASPAY_ENTETE_HORODATAGE` | `x-webhook-timestamp` | ✅ confirmé |
| `SASPAY_TOLERANCE_SIGNATURE` | `300` | 5 minutes, recommandation SasPay |
| `SASPAY_MONTANT_MINIMUM` | `200` | ✅ mesuré : 100 F est refusé |
| `SASPAY_EMAIL_DEFAUT` / `SASPAY_NOM_DEFAUT` | valeurs NEBULA | requis par SasPay, le client les corrige sur leur page |
| `SASPAY_DEVISE` | `XOF` | ⛔ ne jamais mettre autre chose sans avoir relu le §2 |
| `SASPAY_DEVISE_SI_ABSENTE` | *(vide)* | ⛔ vide = une notification sans devise est **refusée**. N'y poser `XOF` qu'après avoir LU dans le journal que SasPay omet vraiment le champ |
| `SASPAY_MONTANT_MULTIPLIE` | `1` | SasPay compte en centimes → `100` |
| `SASPAY_RETOUR` / `SASPAY_ANNULE` | pages du site | — |
| `SASPAY_SIGNATURE_OBLIGATOIRE` | `1` | voir ci-dessous |

**La seule chose qui demandera vraiment la doc**, c'est le corps envoyé pour
créer une session : quinze lignes, dans `ouvrirSession`. Tout le reste (lecture
de la réponse, lecture des notifications) est écrit pour accepter plusieurs
formes et **refuser plutôt que de deviner**.

### Ce que le premier essai réel va nous apprendre tout seul

Un refus n'est pas une panne : il **affiche les deux chiffres**. Un montant cent
fois trop grand dans le journal, et on sait que SasPay compte en centimes. Une
devise refusée, et on sait que le compte est en CDF. La table
`piste.paiement_evenement` garde **le message entier**, même incompris : c'est
elle qui donnera la vraie forme des notifications.

```sql
select recu_le, reference, montant, devise, etat_lu, agi, brut
  from piste.paiement_evenement order by id desc limit 20;
```

### ⚠️ `SASPAY_SIGNATURE_OBLIGATOIRE=0`

Si le schéma de signature supposé est faux, **toutes** les notifications seront
refusées. Le poser à `0` les accepte quand même, et le journal marque alors
« NON SIGNÉ ».

⛔ **Uniquement le temps de trouver le bon schéma, jamais en exploitation :**
tant qu'il vaut `0`, n'importe qui connaissant l'adresse peut déclarer une
commande payée.

---

## 6. Les règles qui tiennent la caisse

Elles sont dans `decider()`, à un seul endroit, et **essayées par
`_qc_paiement.mjs`** :

- ⛔ **le montant ne vient jamais du navigateur** : le serveur le relit sur la
  commande. Sinon on paierait 100 F pour 10 000 F de fiches ;
- ⛔ **un montant introuvable ne devient jamais zéro** : on refuse ;
- ⛔ **la devise est un verrou** : ce qui n'est pas en XOF n'est pas encaissé ;
- ⛔ **une commande livrée ne redevient jamais « payée »** ;
- ⛔ **le retour du navigateur ne prouve rien** : une page « merci » se visite à
  la main. Seule la notification signée déplace un état ;
- ⛔ **la signature se calcule sur le corps reçu tel quel**, jamais sur un JSON
  reparsé, et se compare **à temps constant** ;
- **l'idempotence** : un renvoi ne rejoue rien.

---

## 7. Ce qu'il reste à faire

- [ ] Confirmer **XOF + MTN/Moov Bénin** dans le tableau de bord SasPay
- [ ] Poser les secrets, jouer le SQL, déployer les deux fonctions
- [ ] **Encaisser 1 000 F pour de vrai**, lire `piste.paiement_evenement`,
      ajuster les réglages
- [ ] Passer `SASPAY_PRET` à `true`, reconstruire, redéployer
- [ ] Mettre à jour les décisions **25, 27 et 82** de `PRODUCT.md` — *après* le
      premier encaissement réel, pas avant
- [ ] Plus tard seulement : la livraison automatique du carnet sur paiement
      confirmé (⚠️ elle demandera d'inverser l'ordre « agir puis journaliser »,
      c'est écrit dans la fonction)
