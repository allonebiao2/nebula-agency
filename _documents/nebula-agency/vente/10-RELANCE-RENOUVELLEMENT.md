# LA RELANCE AUTOMATIQUE DES RENOUVELLEMENTS
## Spécification à construire

> **Pourquoi ce document existe.** Vous avez décidé deux choses qui, combinées, rendent
> cette automatisation **obligatoire** :
>
> 1. Le partenaire garde ses commissions sur abonnement **à vie**, même après son départ.
> 2. La relance de renouvellement se fait par **rappel automatique + relance du partenaire**.
>
> Conséquence : les clients d'un partenaire parti n'ont plus personne pour les relancer.
> C'est l'automatisation qui portera cette collecte, ou personne ne la portera.
>
> Version 1.0 · 2026-07-30

---

## 1. Le constat, avant toute chose

**Il n'existe aujourd'hui aucun suivi des abonnements dans le système.**

Vérification faite dans `nebula-affilies/server.py` : la base contient `affiliates`, `leads`,
`commissions`, `history`, `notifs`, `recruits`, `candidatures`, `documents`, `publications`,
`messages`, `app_settings`, `link_events`. **Aucune table ne porte une date d'échéance
d'abonnement.**

Autrement dit : aujourd'hui, personne ne sait quand un client doit renouveler.
Ce n'est pas un problème d'automatisation, c'est un problème de **données manquantes**.

**On ne peut pas automatiser une relance sur une information qui n'existe nulle part.**
Il faut donc construire dans cet ordre : d'abord la donnée, ensuite la relance.

---

## 2. Étape 1 · La donnée (à créer dans l'app partenaires)

Une table `subscriptions`, une ligne par client abonné.

| Colonne | Contenu |
|---|---|
| `id` | identifiant |
| `lead_id` | le client (lien vers `leads`) |
| `affiliate_id` | **le partenaire qui l'a apporté** (c'est lui qui touchera les 25 % à vie) |
| `offre` | catalogue · vitrine |
| `montant` | 20 000 |
| `debut` | date de mise en ligne |
| `echeance` | date du prochain renouvellement (début + 6 mois) |
| `statut` | actif · en retard · résilié |
| `dernier_rappel` | date du dernier message envoyé (évite les doublons) |
| `relances` | compteur de rappels envoyés pour l'échéance en cours |

**Règle métier :** quand un abonnement est encaissé, on fait deux choses d'un coup :
on décale `echeance` de 6 mois, et **on crée automatiquement la commission de 25 %**
pour `affiliate_id`, exactement comme une vente payée génère aujourd'hui sa commission.

C'est ce lien-là qui rend la promesse « récurrent à vie » réellement tenable : elle est
portée par la donnée, pas par la mémoire de quelqu'un.

---

## 3. Étape 2 · Le calendrier de relance

Quatre messages, puis une action humaine. Rien de plus : au-delà, on harcèle.

| Moment | Destinataire | Objet |
|---|---|---|
| **J-15** | Le client | Prévenir, avec un rappel de ce que l'abonnement couvre |
| **J-3** | Le client | Rappeler, plus court |
| **J-3** | **Le partenaire** | L'alerter pour qu'il relance personnellement |
| **J+3** | Le client | Le site est toujours en ligne, mais l'abonnement est en retard |
| **J+10** | **Mongazi** | Alerte : dossier à traiter à la main |

**Après J+10, plus aucun message automatique.** Un client qui n'a pas payé après trois
rappels ne paiera pas au quatrième : il faut un appel humain.

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

À la clé pour vous : 5 000 F de commission sur ce renouvellement.
```

**J+3 · au client**
```
Bonjour [Nom], votre abonnement était dû le [date].
Votre site est toujours en ligne, pas d'inquiétude.

Pour le maintenir et garder vos modifications comprises, il reste 20 000 F à régler.
Je m'occupe de tout dès que c'est fait.
```

**J+10 · à Mongazi**
```
⚠️ ABONNEMENT EN RETARD DE 10 JOURS
Client : [nom] · Partenaire : [prénom] · Échéance : [date] · Montant : 20 000 F
3 rappels envoyés, aucun règlement. À traiter à la main.
```

---

## 5. Étape 3 · Le déclencheur technique

**Un seul workflow n8n, une exécution par jour.**

```
1. Cron  ->  tous les jours à 08h00 (heure de Cotonou)
2. HTTP  ->  GET /api/admin/subscriptions/due
             renvoie les abonnements à J-15, J-3, J+3, J+10
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

- [ ] **Que se passe-t-il si un client ne renouvelle jamais ?** Le site est-il coupé, et
      après combien de temps ? *Ma recommandation : prévenir à J+30, suspendre à J+45,
      conserver les données 6 mois. Couper sans prévenir crée des histoires qui circulent
      vite à Cotonou.*
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
| 2 | Génération automatique de la commission de 25 % à chaque encaissement | 1 séance |
| 3 | Endpoints `/due` et `/rappel` | courte |
| 4 | Workflow n8n avec les 4 gabarits | 1 séance |
| 5 | Onglet « Mon portefeuille » côté partenaire | 1 séance |

**Rien de tout cela n'est urgent avant la première échéance**, soit six mois après la
première vente de la vague 1. Mais **le point 1 est urgent dès la première vente** : sans
la donnée, vous ne saurez pas qui doit quoi, et la promesse du récurrent à vie devient
impossible à tenir.

---

*NEBULA Agency · Cotonou, Bénin · Spécification, pas encore implémentée.*
