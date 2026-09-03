# 2026-09-03 · PISTE, le paiement en ligne (SasPay)

**Demande de Mongazi** : « j'ai trouvé un moyen de paiement qu'on peut mettre
sur des vitrines en ligne sans forcément avoir de RCCM : `app.saspay.me`. Je
veux commencer déjà à tester avec PISTE. Je vais t'envoyer la clé API aussi. »

---

## Ce qui a bloqué, et qu'il faut savoir avant de relire le code

⛔ **`saspay.me` et `docs.saspay.me` sont injoignables depuis une session dans
le nuage.** Le filtre de sortie répond **403 sur le CONNECT** pour ces deux
domaines. Ni la doc, ni l'API n'ont pu être lues, et **rien de leur API n'est
publié ailleurs** (recherches : aucun dépôt, aucun paquet, aucun article).
Aucune adresse ni aucun nom de champ n'a donc pu être vérifié.

⚠️ Conséquence sur la manière d'écrire : le pari n'est pas « j'ai deviné
juste », c'est **« me tromper ne doit rien coûter »**. Chaque valeur incertaine
est un **réglage d'environnement** : corriger une hypothèse est une commande
(`supabase secrets set`), pas une modification de code ni un déploiement. Et
**rien ne se devine sur l'argent** : un montant introuvable rend `null`, jamais
`0`, et la notification est refusée.

⚠️ **Le premier essai réel dira la vérité tout seul.** Un refus affiche **les
deux chiffres** : un montant cent fois trop grand = SasPay compte en centimes
(`SASPAY_MONTANT_MULTIPLIE=100`). Et `piste.paiement_evenement` garde **le
message entier, même incompris**.

---

## ⛔ LA QUESTION QUI DÉCIDE DE TOUT : LA DEVISE

Sur la capture envoyée par Mongazi, la fenêtre « Créer un lien de paiement »
propose **CDF** — le franc congolais. PISTE vend en **FCFA (XOF)**, à Cotonou.
**10 000 CDF valent environ 2 100 F** : encaisser la mauvaise devise sans s'en
apercevoir, c'est livrer un carnet payé au quart.

D'où un **verrou de devise** dans le code (`SASPAY_DEVISE=XOF`) : ce qui n'est
pas dans la devise attendue n'est **jamais** marqué payé, c'est journalisé et
refusé.

Si SasPay ne règle pas en XOF sur un compte béninois, le chantier s'arrête là,
**et le code reste bon pour FedaPay**, déjà dans le stack de l'agence.

### ✅ Les opérateurs, confirmés le soir même

Mongazi : « ça passe sur MTN Moov. Tous les MTN même et Moov Afrique qui
existe. » Le compte encaisse donc sur **tous les MTN et tous les Moov Africa**.

⚠️ **Ça répond à la question des opérateurs, pas à celle de la devise.** Un
agrégateur peut débiter un portefeuille MTN Bénin et créditer un solde en CDF.
Reste à regarder deux choses : le XOF est-il dans la liste des devises de la
fenêtre « Créer un lien », et dans quelle devise sort l'argent à l'onglet
Retraits.

⚠️ **Ce que la couverture débloque** : le §9 de `PRODUCT.md` garde depuis le
début « le paiement depuis le Togo et la Côte d'Ivoire vers un compte béninois,
non testé », et l'écran de paiement dit encore « MTN MoMo, au Bénin ». Le vivier
fait 7 817 fiches sur **trois pays** : si un Togolais ou un Ivoirien peut payer
seul, c'est le plus gros verrou commercial de PISTE qui saute. ⛔ Rien n'est
annoncé avant un encaissement réel depuis Lomé ou Abidjan.

### ✅ Et la devise, confirmée dans la foulée

Mongazi : « XOF et XAF aussi etc. » Le **CDF de la première capture n'était que
la devise sélectionnée par défaut**, pas la seule disponible. ⚠️ *Une valeur
affichée dans un formulaire n'est pas la liste des valeurs possibles : j'ai
construit un verrou entier sur une capture d'écran, et j'avais raison de le
construire, mais tort de croire que la capture disait tout.*

Le doute commercial est levé. Restent le vrai encaissement de 1 000 F et la
forme technique de leur API.

### La sonde, parce que la machine qui peut les joindre n'est pas la mienne

`piste/_saspay_sonde.mjs`, à lancer **depuis le PC de Cotonou** : elle balaie
les adresses et les formes d'en-tête plausibles, **lit les codes de retour**
(401/403 = la porte existe, la clé ne passe pas · 400/422 = adresse et clé
bonnes, c'est le corps · 404 = mauvais chemin) et écrit les
`supabase secrets set` à copier.

⛔ **Deux défauts trouvés en l'éprouvant, et le second était grave.** Le filtre
de sortie du nuage répond **403**, et la sonde a pris ce refus pour la preuve
que la porte existait : elle a désigné `app.saspay.me` gagnant et **tendu des
commandes fondées sur ce rien**. Un pare-feu d'entreprise ou un portail wifi
produiraient le même mirage. Corrigé : on lit le CORPS avant de croire le code
(`allowlist`, `egress`, `proxy`…), et surtout **aucune commande n'est proposée
tant qu'on n'a pas vraiment parlé à l'API** (2xx, ou 400/422 avec un message
d'eux). ⚠️ *Un 401 dit qu'une porte existe, pas que c'est la bonne : figer une
adresse sur cette seule foi, c'est déployer une hypothèse en croyant déployer
un fait.*

### ⛔ Le trou que cette réponse a révélé dans mon propre verrou

Écrit `if (n.devise && n.devise !== r.devise)`, le verrou **laissait passer
toute notification sans champ devise**. Avec un seul opérateur béninois c'était
théorique. Avec tous les MTN et tous les Moov Africa sur le même compte, ça ne
l'est plus : MTN Cameroun encaisse en XAF, MTN Ghana en GHS, MTN Nigeria en
NGN, et **10 000 unités non qualifiées passaient pour 10 000 F**.

Corrigé : **« absent » n'est pas « bon »**, l'absence de devise est un refus.
L'échappatoire existe (`SASPAY_DEVISE_SI_ABSENTE`) mais elle est **vide par
défaut** et ne se pose qu'après avoir LU dans le journal que SasPay omet
vraiment le champ. ⚠️ *J'avais écrit trois lignes plus haut que rien ne se
devine sur l'argent, et je l'avais quand même fait.* QC : 57 → **64 contrôles**.

⚠️ **Le verrou reste `XOF`, et c'est exactement juste** : Bénin, Togo et Côte
d'Ivoire sont tous en franc CFA de l'UEMOA, donc les trois marchés du vivier
sont couverts par une seule devise, et les pays où PISTE ne vend rien sont
refusés.

---

## Ce qui a été construit (rien n'est branché, rien n'est déployé)

| Fichier | Rôle |
|---|---|
| `piste/supabase/paiement.sql` | 2 tables + 4 portes serveur. Rejouable. **S'arrête net** si `piste.commande` n'existe pas, plutôt que de s'installer à moitié |
| `piste/supabase/functions/_shared/saspay.ts` | tout l'inconnu de SasPay **et** les gardes de la caisse (`decider`) |
| `piste/supabase/functions/piste-paiement/` | ouvre une session. **La clé secrète ne vit que là** |
| `piste/supabase/functions/piste-paiement-recu/` | la notification : signature, devise, montant, idempotence |
| `piste/_qc_paiement.mjs` | **57 contrôles verts, sans clé, sans réseau, sans base** |
| `piste/PAIEMENT.md` | le mode d'emploi et les 3 points à vérifier avant d'ouvrir |
| `SASPAY_PRET` dans `donnees.js` | **`false`** : le site n'affiche aucun bouton |

**Le site est inchangé pour un acheteur.** Le Mobile Money à la main marche
comme avant, et il **restera dessous** le jour où le bouton s'ouvrira : un
moyen de paiement neuf se met à côté de celui qui marche, jamais à sa place.

⚠️ **L'encaissement s'automatise, pas la livraison.** La commande se marquera
« payée » toute seule ; le carnet reste fabriqué par Mongazi dans le cockpit.
Laisser partir de la marchandise sur un message mal compris serait le seul
geste vraiment coûteux.

---

## Les règles qui tiennent la caisse (dans `decider()`, essayées par le QC)

- ⛔ **le montant ne vient jamais du navigateur** : le serveur le relit sur la
  commande. Sinon on paie **100 F pour 10 000 F de fiches** ;
- ⛔ **un montant introuvable ne devient jamais zéro** ;
- ⛔ **une commande livrée ne redevient jamais « payée »** ;
- ⛔ **le retour du navigateur ne prouve rien** : une page « merci » se visite à
  la main. Seule la notification signée déplace un état ;
- ⛔ **la signature se calcule sur le corps reçu TEL QUEL**, jamais sur un JSON
  reparsé (`JSON.parse` puis `stringify` réordonne les clés : la signature ne
  correspondrait plus jamais, et on finirait par « désactiver la vérification
  pour que ça marche ») ;
- **agir PUIS journaliser**, et non l'inverse : journaliser d'abord réserverait
  l'identifiant de l'événement, et une mise à jour ratée ferait passer le
  renvoi du fournisseur pour un doublon — le paiement resterait invisible pour
  toujours. ⚠️ Ce raisonnement ne tient **que parce que l'action est
  inoffensive à répéter** : le jour où le carnet partira d'ici, il faudra
  inverser et réserver en deux temps.

---

## ⚠️ Deux défauts trouvés par le contrôle, dans mon propre code

**1. `chercher()` rendait le premier nom trouvé dans LE MESSAGE, pas le premier
de LA LISTE.** Mon commentaire affirmait le contraire. Un message portant `id`
(l'événement) *et* `payment_id` (la session) livrait donc l'identifiant
d'événement là où on voulait celui de la session, et **aucune commande n'aurait
jamais été retrouvée**. Corrigé : on parcourt **nom par nom, dans l'ordre de la
liste**. ⚠️ *La priorité qu'on écrit dans une liste doit être celle qui
s'applique, sinon le commentaire ment.*

**2. Toute signature base64 valable était refusée.** Pour retirer un préfixe
(« sha256=… »), je découpais sur `=` et gardais le dernier morceau. Or **une
signature base64 se TERMINE par `=`** (bourrage) : le morceau gardé était vide.
Corrigé : on ne retire un préfixe que s'il **ressemble** à un préfixe (une
courte étiquette suivie du signe). ⚠️ *Sans ce contrôle, le défaut se serait vu
en production comme « SasPay envoie des signatures invalides », et la réaction
naturelle aurait été de désactiver la vérification.*

---

## Ce qui reste (détail dans `piste/PAIEMENT.md`)

1. **Confirmer XOF + MTN/Moov Bénin** dans le tableau de bord SasPay
2. Poser les secrets, jouer le SQL, déployer les deux fonctions
3. **Encaisser 1 000 F pour de vrai** (même règle que Moov Flooz et Abidjan :
   ne rien promettre avant d'avoir envoyé 1 000 F), lire
   `piste.paiement_evenement`, ajuster les réglages
4. Passer `SASPAY_PRET` à `true`, reconstruire, redéployer
5. Mettre à jour les **décisions 25, 27 et 82** de `PRODUCT.md` — *après* le
   premier encaissement réel, pas avant : on n'inscrit pas une décision qui
   n'a pas été validée

⛔ **La clé API n'est pas encore arrivée, et elle ne doit jamais entrer dans le
dépôt** (il est PUBLIC). Sa place est `supabase secrets set`. Si elle a transité
par une conversation, la faire tourner depuis le tableau de bord SasPay.

**Branche : `claude/saspay-payment-integration-fv2rdt`.** Rien n'est fusionné
dans `main`, rien n'est déployé.
