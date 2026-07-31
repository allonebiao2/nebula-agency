# REPRENDRE ICI
## Point de reprise pour une session terminal · dernière mise à jour 2026-07-31

> **À lire en premier** quand on ouvre une session sur ce dépôt.
> Ce fichier dit où on en est, ce qui bloque, et par quoi commencer.
> Il est mis à jour à chaque fin de session importante.

---

## 1. Le chantier en cours : la force de vente NEBULA

**Objectif de Mongazi :** il se juge « piètre vendeur » et veut recruter des partenaires
commissionnés capables de vendre parfaitement les **3 services phares**, avec des guides
qui leur apprennent tout.

**État : le chantier documentaire est TERMINÉ.** 13 documents + 2 outils HTML + 9 PDF,
dans `_documents/nebula-agency/vente/`.

| Fichier | Ce que c'est |
|---|---|
| `00-SOCLE-COMMERCIAL.md` | **La source de vérité.** 32 décisions, prix, commissions, règles, 12 interdits. En cas de doute sur un chiffre, c'est lui qui fait foi |
| `01-AVIS-DE-RECRUTEMENT.md` | Annonce, affiche, grille de sélection /20, script d'entretien |
| `02-MANUEL-DU-PARTENAIRE.md` | Le métier : prospection, **méthode de vente en 7 temps**, relance, brief |
| `03/04/05-GUIDE-*.md` | Un guide par service, anatomie en 12 chapitres |
| `06-ARSENAL-SCRIPTS.md` | Tous les messages prêts à copier |
| `07-MISE-EN-LIGNE.md` | Procédure de publication et état des actions |
| `08-DIAGNOSTIC-DIGITAL.md` | La consultation pro : 40 questions + grille des automatisations |
| `09-CONTRAT-PARTENAIRE.md` | Contrat d'apporteur d'affaires en 16 articles |
| `10-RELANCE-RENOUVELLEMENT.md` | Spécification de la relance des abonnements |
| `simulateur-commissions.html` | Le partenaire calcule ses gains du mois |
| `fiche-diagnostic.html` | Fiche remplie chez le client → rapport WhatsApp |
| `pdf/` | Les 9 documents en PDF, régénérables via `_build_pdf.py` |
| `marketing/PROMPTS-POSTS-LE-SAVIEZ-VOUS.md` | Prompt-maître Nano Banana Pro + 8 posts |

---

## 2. Les chiffres à connaître par cœur

*Si un chiffre diffère ailleurs dans le dépôt, `00-SOCLE-COMMERCIAL.md` a raison.*

| | |
|---|---|
| Catalogue Digital | **50 000 F**, jusqu'à 20 produits, +15 000 F par lot de 10 |
| Vitrine Digitale | **150 000 F**, une page, +30 000 F par page, domaine offert 1 an puis 16 000 F/an |
| Outil sur mesure | **55 000 à 500 000 F**, prix issu du configurateur du site |
| QR Google Review | **30 000 F** |
| **Abonnement** | **20 000 F tous les 6 mois, modifications comprises** (ex-15 000 F) |
| Paiement | Catalogue intégral · Vitrine et Outil **70 % / 30 %** |
| Commission | 25 % (1-4 ventes/mois) · 30 % (5-9) · 35 % (10+) |
| **Récurrent** | **25 % de chaque abonnement, ACQUIS À VIE**, ne compte pas dans le palier |
| Réseau | N1 10 %, N2 5 %, à partir de la 1re vente du partenaire |
| Versement | **24 à 72h** après réclamation |
| Vague 1 | Cotonou, 8 places, candidatures 21 jours, objectif 30 ventes / 90 jours |

---

## 3. CE QUI BLOQUE — à faire par Mongazi

**Aucun de ces points ne peut être fait depuis une session distante.**
*3.1 est fait. Restent 3.2 à 3.5, plus les 7 informations du client 10 (§3bis).*

### 3.1 Déployer le site sur Cloudflare ✅ FAIT le 2026-07-31 (session terminal Claude Code)
Déployé : **www.nebula-agency.online affiche maintenant 20 000 F / 6 mois**. Les 4 « 15 000 » restants = poids du configurateur (`data-price="15000"`), légitimes. Vérifié live (domaine + `nebula-agency.pages.dev` = 4× « 15 000 » / 19× « 20 000 », `cf-cache-status: DYNAMIC`). Procédure ci-dessous conservée pour référence.

```bash
git pull origin main
mkdir -p _tmp_pages && cp 00-nebula-agency/nebula_agency_v9.html _tmp_pages/index.html
cp -r 00-nebula-agency/affiliation 00-nebula-agency/audio _tmp_pages/ 2>/dev/null
npx -y wrangler@3 pages deploy _tmp_pages --project-name nebula-agency --branch main
```
Identifiants dans `secrets/cloudflare.env`.
**Contrôle :** plus aucune occurrence de « 15 000 F » sur la page Tarifs.

### 3.2 Poser `NAFF_CRON_KEY` sur Railway
Une chaîne secrète au choix. Sans elle, n8n ne pourra pas lire les échéances
d'abonnement. Une minute de travail, et ça débloque toute la relance automatique.

### 3.3 Compléter le numéro IFU
Dans `09-CONTRAT-PARTENAIRE.md`, en-tête, champ `[à compléter]`.
Le RCCM est écrit « en cours d'immatriculation », à remplacer le jour venu.

### 3.4 Téléverser les 9 PDF dans l'espace partenaire
`/admin` → Documentation → Ajouter. Catégories et descriptions : `07-MISE-EN-LIGNE.md` §1 et §3.
⚠️ Le socle `00` et l'avis `01` **ne se publient pas** : documents internes.

### 3.5 L'image de référence des posts
Jamais reçue malgré plusieurs demandes. Sans elle, le bloc `STYLE INHERITANCE` du
prompt-maître reste générique.

---

## 3bis. Client 10 · HILLARY M. STYL (livré 2026-07-31)

Vitrine couture avec **moteur de commande** : catalogue prêt-à-porter (tailles) et
sur-mesure (8 mesures femme/homme), frais d'expédition par pays, délai normal ou express,
récapitulatif chiffré, envoi WhatsApp structuré.
`clients/10-hillary-m-styl/vitrine.html` · détail et QC dans son `CONTEXT.md`.

⚠️ **Ne pas mettre en ligne avant d'avoir les 7 informations du §3 de son CONTEXT.md.**
Le numéro WhatsApp est un fixe de test (`22900000000`) : en l'état, **aucune commande
n'arriverait**. Les frais d'expédition sont des exemples : un tarif faux coûte de l'argent
à la cliente à chaque commande.

## 4. Ce qui tourne déjà en production

**Déployé automatiquement au push sur `main` (Railway) :**
- **NOVA** annonce les bons prix. Elle citait encore la Fiche Google Maps et les Avatar IA,
  retirés du site en v9, parce que son catalogue était dérivé du dictionnaire `SERVICES`.
- **`refresh_seeded_docs()`** corrige au démarrage les 5 guides déjà en base qui poussaient
  la Vitrine en premier. Idempotente, ne touche pas les documents ajoutés à la main.
- **Module Abonnements** : table `subscriptions`, ouverture automatique à l'encaissement,
  commission de 25 % au renouvellement, 6 endpoints, portefeuille partenaire.

---

## 5. Le prochain vrai chantier technique

**Le workflow n8n de relance des renouvellements.**
Tout le back-end est prêt et testé. Il ne reste que le workflow.

Spécification complète, messages mot pour mot et garde-fous :
`_documents/nebula-agency/vente/10-RELANCE-RENOUVELLEMENT.md` §3 à §6.

En résumé : un cron quotidien à 08h00 → `GET /api/admin/subscriptions/due?key=NAFF_CRON_KEY`
→ Switch sur les 4 paliers (J-15, J-3, J+3, J+10) → Twilio WhatsApp →
`POST /api/admin/subscriptions/{id}/rappel`. Nommer `nebula-affilies-renouvellements`,
Error Trigger obligatoire.

**Pourquoi ça compte :** le récurrent étant acquis à vie, les clients d'un partenaire parti
n'ont plus personne pour les relancer. C'est l'automatisation qui portera cette collecte,
ou personne ne la portera.

---

## 6. Les pièges de ce dépôt, appris à la dure

1. **`main` bouge pendant qu'on travaille.** Toujours `git merge origin/main` dans sa
   branche AVANT de fusionner vers `main`. Un merge naïf a failli annuler 2 621 lignes du
   module Boussole. Vérifier avec `git diff --stat origin/main..HEAD` que rien d'étranger
   au chantier n'apparaît.
2. **`seed_content()` ne s'exécute que sur une base vide.** Modifier le code ne corrige
   jamais la production : il faut une migration (voir `refresh_seeded_docs()`).
3. **Un catalogue commercial ne se dérive jamais d'une structure technique.** `SERVICES`
   contenait des offres mortes, et NOVA les récitait au public.
4. **`node --check` ment sur les blocs `application/ld+json`.** Comparer avec la version
   d'avant avant de crier à la régression.
5. **`markdown` + `nl2br` casse les phrases** des documents écrits en lignes de 80 colonnes.
6. **Les identifiants ne sont pas dans les sessions distantes** (`secrets/` est gitignoré),
   et la politique réseau bloque `nebula-agency.online`. Tout déploiement se fait en local.

---

## 7. Comment continuer en une phrase

> « Lis `_memoire/REPRENDRE-ICI.md`, puis `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`.
> Le site est déployé. Il reste §3.2 (`NAFF_CRON_KEY` sur Railway, une minute) et les
> 7 informations du client HILLARY M. STYL au §3bis avant de pouvoir le mettre en ligne. »

**Détail complet de tout le chantier :**
`_memoire/conversations/2026-07-30-recrutement-et-guides-de-vente.md` (5 vagues)
`_memoire/journal/2026-07-30-journal.md`
`_memoire/apprentissages/2026-07-30-pdf-et-audit-code.md`
