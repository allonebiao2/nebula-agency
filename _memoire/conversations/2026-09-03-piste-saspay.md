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
