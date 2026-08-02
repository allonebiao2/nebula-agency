# LA RELANCE AUTOMATIQUE DES RENOUVELLEMENTS
## Spécification à construire

> **Pourquoi ce document existe.** Deux décisions, combinées, rendent cette automatisation
> **obligatoire** :
>
> 1. Le partenaire touche **20 % de chaque abonnement, à vie**, même après son départ.
> 2. La relance se fait par **rappel automatique + relance personnelle du partenaire**.
>
> Conséquence : les clients d'un partenaire parti n'ont plus personne pour les relancer.
> C'est l'automatisation qui portera cette collecte, ou personne ne la portera.
>
> **Le levier qui fait payer**, à mettre dans tous les gabarits : sans règlement,
> **le site est coupé** (hébergement et sécurité interrompus, QR code mort). Ce n'est pas
> une menace, c'est un fait technique, et il faut l'annoncer à l'avance, jamais le brandir.
>
> **Version 3.0 · 2026-08-02.** Table `subscriptions`, ouverture automatique à
> l'encaissement, génération de la commission de **20 %**, endpoints n8n et portefeuille :
> en place et testés dans `nebula-affilies/server.py`. Il reste le workflow n8n lui-même.

---

## 1. Le constat de départ (résolu le 2026-07-31)

**Il n'existait aucun suivi des abonnements dans le système.**

Vérification faite dans `nebula-affilies/server.py` : la base contient `affiliates`, `leads`,
`commissions`, `history`, `notifs`, `recruits`, `candidatures`, `documents`, `publications`,
`messages`, `app_settings`, `link_events`. **Aucune table ne porte une date d'échéance
d'abonnement.**

Autrement dit : aujourd'hui, personne ne sait quand un client doit renouveler.
Ce n'est pas un problème d'automatisation, c'est un problème de **données manquantes**.

**On ne peut pas automatiser une relance sur une information qui n'existe nulle part.**
La donnée a donc été construite en premier. ✅ Fait.

---

## 2. Étape 1 · La donnée ✅ IMPLÉMENTÉE

Table `subscriptions` créée dans `nebula-affilies/server.py`, une ligne par client abonné.

| Colonne | Contenu |
|---|---|
| `id` | identifiant |
| `lead_id` | le client (lien vers `leads`) |
| `affiliate_id` | **le partenaire qui l'a apporté** (c'est lui qui touchera les 20 % à vie) |
| `offre` | catalogue · vitrine |
| `montant` | 20 000 |
| `debut` | date de mise en ligne |
| `echeance` | date du prochain renouvellement (début + 6 mois) |
| `statut` | actif · en retard · résilié |
| `dernier_rappel` | date du dernier message envoyé (évite les doublons) |
| `relances` | compteur de rappels envoyés pour l'échéance en cours |

**Règle métier, implémentée dans `record_subscription_payment()` :** quand un abonnement
est encaissé, on décale `echeance` de 6 mois **et on crée la commission de 20 %** pour
`affiliate_id`, dans la table `commissions` avec `level='abonnement'`.

C'est ce lien qui rend la promesse du récurrent à vie réellement tenable : elle est portée
par la donnée, pas par la mémoire de quelqu'un.

**Trois propriétés obtenues gratuitement** en réutilisant la table `commissions` :
- le partenaire réclame et se fait payer par le circuit qu'il connaît déjà, sans aucune
  modification de l'interface ;
- le palier se calculant sur les *leads* payés et non sur les commissions, la règle
  « le récurrent ne compte pas dans le palier » est respectée sans code supplémentaire ;
- `void_commissions()` a été corrigée pour ne jamais annuler une commission d'abonnement :
  elles correspondent à des encaissements distincts et sont acquises à vie.

**Fonctions livrées :** `ensure_subscription()` (idempotente, ouverture à l'encaissement,
catalogue et vitrine uniquement) · `record_subscription_payment()` · `subscriptions_due()`
· `_plus_mois()` (mois calendaires, gère les fins de mois).

**Endpoints livrés :**

| Route | Usage |
|---|---|
| `GET /api/admin/subscriptions` | Liste, jours restants, récurrent semestriel total |
| `GET /api/admin/subscriptions/due` | **Consommé par n8n**, accepte `?key=NAFF_CRON_KEY` |
| `POST /api/admin/subscriptions/{id}/paid` | Encaissement : échéance +6 mois et commission 15 % |
| `POST /api/admin/subscriptions/{id}/rappel` | Marque le rappel envoyé (anti-doublon) |
| `POST /api/admin/subscriptions/{id}/resilier` | Résiliation |
| `GET /api/partenaire/portefeuille` | Le partenaire voit ses abonnements et ses échéances |

**Variable d'environnement à poser sur Railway :** `NAFF_CRON_KEY`, une chaîne secrète
que n8n passera en `?key=` pour lire les échéances sans session admin.

---

## 3. Étape 2 · Le calendrier de relance

Quatre messages, puis une action humaine. Rien de plus : au-delà, on harcèle.

| Moment | Destinataire | Objet |
|---|---|---|
| **J-15** | Le client | Prévenir, avec un rappel de ce que l'abonnement couvre |
| **J-3** | Le client | Rappeler, plus court |
| **J-3** | **Le partenaire** | L'alerter pour qu'il relance personnellement |
| **J+3** | Le client | Le site est en ligne, mais l'échéance est passée. On annonce la date de coupure |
| **J+7** | Le client | **Dernier avis : le site est coupé demain** |
| **J+8** | (automatique) | **SUSPENSION AUTOMATIQUE** du site, et alerte à Mongazi et au partenaire |
| **M+6** | Le client | Dernier avertissement avant suppression des données |

**Après J+8, plus aucun message automatique au client.** Un client suspendu qui veut revenir
appelle : c'est le moment de la reprise humaine, pas du message.

### Pourquoi 8 jours, et pas 45

C'est le réglage qui rapporte le plus, et ce n'est pas le plus dur :

1. **Une échéance qu'on n'applique pas est une échéance qui n'existe pas.** Un client coupé
   au 45e jour apprend que la date est décorative, et il attendra encore plus longtemps au
   semestre suivant. Le retard devient l'habitude de tout le parc.
2. **Sept jours de courtoisie suffisent** pour un virement Mobile Money, un déplacement ou
   une absence. Au-delà, ce n'est plus un délai, c'est un crédit gratuit que NEBULA accorde.
3. **Le levier est à son maximum juste après l'échéance**, tant que le site tourne encore et
   que le commerçant a le QR affiché dans sa boutique. Il s'effondre après : un client coupé
   depuis six semaines a déjà pris l'habitude de vivre sans.
4. **Six mois de conservation des données** ne coûtent presque rien et gardent récupérable un
   client qui vaut 20 000 F par semestre. Supprimer vite ne fait économiser rien du tout.

### 💰 Les frais de réactivation, à valider

**Proposition : 5 000 F pour remettre un site coupé en ligne**, en plus du semestre dû.

C'est ce qui transforme le retard en recette au lieu d'en faire une perte sèche, et surtout
c'est ce qui rend le paiement à l'heure **strictement moins cher** que le retard. Deux règles
qui le rendent acceptable :

- **Aucun frais si le client règle pendant les 7 jours de courtoisie.** Le délai devient une
  faveur qu'on peut perdre, pas un droit acquis.
- **Ces frais ne portent aucune commission partenaire** : ils couvrent la remise en ligne,
  ils ne sont pas un abonnement.

⚠️ **C'est un tarif nouveau, à votre validation.** Le risque existe : un petit commerçant en
retard de huit jours à qui on réclame 5 000 F de plus peut renoncer, et vous perdez alors
20 000 F par semestre plus les 4 000 F du partenaire. Si vous préférez la sécurité, mettez
la suspension en place sans les frais et ajoutez-les au deuxième semestre.

---

## 4. Les messages, mot pour mot

**J-15 · au client**
```
Bonjour [Nom] 🙂
Votre abonnement NEBULA pour [nom du commerce] arrive à échéance le [date].

20 000 F pour les 6 prochains mois : votre site reste en ligne, protégé, et
vos modifications restent comprises (textes, prix, photos, produits).

Vous voulez qu'on en profite pour mettre quelque chose à jour ?
```

**J-3 · au client**
```
Bonjour [Nom], petit rappel : votre abonnement arrive à échéance le [date].
20 000 F pour 6 mois, modifications comprises.
Je vous envoie les infos de paiement ?
```

**J-3 · au partenaire**
```
[Prénom], l'abonnement de [nom du commerce] arrive à échéance le [date].

Un appel de votre part vaut mieux que dix messages automatiques.
Et c'est le meilleur moment pour lui parler de la suite : une vitrine, une page
de plus, un outil de suivi.

À la clé pour vous : 4 000 F de commission sur ce renouvellement, et vous les toucherez
encore au suivant, et à celui d'après.
```

**J+3 · au client**
```
Bonjour [Nom], votre abonnement était dû le [date].
Votre site est toujours en ligne, pas d'inquiétude.

Je vous préviens simplement à l'avance : sans règlement, il sera coupé
le [date + 8 jours] : l'hébergement et la sécurité s'arrêtent, et votre
QR code ne mènera plus à rien.

20 000 F pour 6 mois, vos modifications comprises. Je m'occupe de tout
dès que c'est réglé.
```

**J+7 · au client (le dernier avis)**
```
Bonjour [Nom], je ne veux pas que ça vous surprenne : sans règlement,
votre site sera coupé demain [date].

Vos données sont conservées, rien n'est perdu, et je le remets en ligne
dès réception. 20 000 F.
```

**J+8 · à Mongazi et au partenaire**
```
⛔ SITE SUSPENDU · 8 jours de retard
Client : [nom] · Partenaire : [prénom] · Échéance : [date] · Montant : 20 000 F
4 rappels envoyés, aucun règlement. Site coupé, données conservées 6 mois.
Un appel humain est la seule chose qui le récupère maintenant.
```

**M+6 · au client (dernier avertissement)**
```
Bonjour [Nom], votre site est hors ligne depuis six mois.
Ses données seront supprimées le [date] et il ne sera plus récupérable.

S'il vous reste un doute, dites-le moi avant : une fois supprimé,
tout est à refaire.
```

---

## 5. Étape 3 · Le déclencheur technique

**Un seul workflow n8n, une exécution par jour.**

```
1. Cron  ->  tous les jours à 08h00 (heure de Cotonou)
2. HTTP  ->  GET /api/admin/subscriptions/due
             renvoie les abonnements à J-15, J-3, J+3, J+7, J+8, M+6
3. Switch ->  aiguillage selon le palier d'échéance
4. Twilio WhatsApp -> message au client (gabarits du §4)
5. HTTP  ->  POST /api/admin/subscriptions/{id}/rappel
             met à jour dernier_rappel et incrémente relances
6. Pour J-3 : notification interne au partenaire (notify(kind="info"))
7. Pour J+10 : alerte Telegram à Mongazi (le bot @Nova_de_nebula_bot existe déjà)
8. Error Trigger -> notification WhatsApp à Mongazi
```

**Ce qui existe déjà et qu'on réutilise :** n8n auto-hébergé sur le VPS Hostinger,
Twilio pour WhatsApp, le système `notify()` de l'app partenaires, le bot Telegram.
**Ce qui manque :** uniquement la table `subscriptions` et les deux endpoints.

**Conventions à respecter** (voir `_knowledge/n8n-workflows.md`) : nommer le workflow
`nebula-affilies-renouvellements`, un **Error Trigger** obligatoire, sticky note explicative
en tête, identifiants dans les Credentials n8n et jamais en dur.

---

## 6. Les garde-fous

1. **Un seul message par client et par jour**, quoi qu'il arrive. `dernier_rappel` sert
   exactement à ça.
2. **Jamais plus de 3 rappels** pour une même échéance.
3. **Jamais de relance à un client résilié.**
4. **Vérifier le numéro** avant d'envoyer : un rappel qui part sur un mauvais numéro donne
   l'impression que NEBULA écrit à n'importe qui.
5. **Un client qui a payé sort immédiatement de la file**, même si le message du jour est
   déjà programmé.

---

## 7. Ce qu'il reste à décider

- [x] **Que se passe-t-il si un client ne renouvelle jamais ? TRANCHÉ le 2026-08-02.**
      **Courtoisie de 7 jours, suspension à J+8, données conservées 6 mois.** Le préavis
      n'est pas une politesse, c'est une protection : couper sans prévenir crée des
      histoires qui circulent vite à Cotonou. Voir §3 pour le raisonnement.
- [ ] **Un client peut-il payer 12 mois d'avance** (40 000 F) ? *Recommandation : oui, avec
      un mois offert. Vous encaissez d'avance et vous supprimez une relance sur deux.*
- [ ] **Le partenaire voit-il les échéances de ses clients** dans son espace ?
      *Recommandation : oui, un onglet « Mon portefeuille » avec les dates. C'est ce qui
      transforme le récurrent en habitude de travail plutôt qu'en rente passive.*

---

## 8. Ordre de construction

| # | Quoi | Effort |
|---|---|---|
| 1 | Table `subscriptions` + création automatique à la mise en ligne d'un client | 1 séance |
| 2 | Génération automatique de la commission de 20 % à chaque encaissement | fait |
| 3 | Endpoints `/due` et `/rappel` | courte |
| 4 | Workflow n8n avec les 4 gabarits | 1 séance |
| 5 | Onglet « Mon portefeuille » côté partenaire : ses 20 %, et quand relancer | 1 séance |

**Rien de tout cela n'est urgent avant la première échéance**, soit six mois après la
première vente de la vague 1. Mais **le point 1 est urgent dès la première vente** : sans
la donnée, vous ne saurez pas quel client doit renouveler, et le récurrent de NEBULA devient
impossible à tenir.

---

*NEBULA Agency · Cotonou, Bénin · Spécification, pas encore implémentée.*
