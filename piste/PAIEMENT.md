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

**⏳ Ce qui reste : le vrai encaissement de 1 000 F**, et la forme technique de
leur API (adresse, noms de champs), que la sonde ci-dessous va chercher. Tant
que le premier franc n'est pas arrivé, **`SASPAY_PRET` reste `false`** dans
`src/donnees.js`.

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
| `_qc_paiement.mjs` | **57 contrôles, sans clé, sans réseau, sans base** |

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

# 3. les fonctions
supabase functions deploy piste-paiement
supabase functions deploy piste-paiement-recu --no-verify-jwt

# 4. dans le tableau de bord SasPay, onglet « Webhooks », déclarer :
#    https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/piste-paiement-recu

# 5. le contrôle, avant tout
node _qc_paiement.mjs
```

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

| Réglage | Défaut supposé | À corriger si… |
|---|---|---|
| `SASPAY_BASE` | `https://api.saspay.me` | la doc donne une autre adresse |
| `SASPAY_CHEMIN_SESSION` | `/v1/checkout/sessions` | le chemin diffère |
| `SASPAY_ENTETE_CLE` | `Authorization` | la clé se présente autrement |
| `SASPAY_PREFIXE_CLE` | `Bearer ` | pas de préfixe → poser une chaîne vide |
| `SASPAY_ENTETE_SIGNATURE` | `x-saspay-signature` | l'en-tête porte un autre nom |
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
