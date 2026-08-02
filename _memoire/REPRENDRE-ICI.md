# REPRENDRE ICI
## Point de reprise pour une session terminal · dernière mise à jour 2026-08-01

> **À lire en premier** quand on ouvre une session sur ce dépôt.
> Ce fichier dit où on en est, ce qui bloque, et par quoi commencer.
> Il est mis à jour à chaque fin de session importante.

---

## 0. 🚨 URGENT — le bureau des partenaires est HORS LIGNE (constaté le 2026-08-01)

`https://partenaires.nebula-agency.online` renvoie **`404 Application not found`**, et ce 404
vient de **Railway**, pas du relais Cloudflare : l'origine
`nebula-affilies-production.up.railway.app` répond la même chose en direct.
Même panne pour **Vitrina** (`vitrina-production-686b.up.railway.app`).
Les deux relais `_worker.js` sont sains, ils pointent vers des applications qui n'existent plus.

**Le token de `secrets/railway.env` est refusé (« Unauthorized »)** → rien ne peut être relancé
en ligne de commande. Il faut un token neuf, ou passer par le dashboard Railway.

Pourquoi c'est prioritaire : c'est l'outil de la vague de recrutement des 8 partenaires de
Cotonou. Tant qu'il est éteint, aucun partenaire ne peut se connecter ni réclamer sa commission.

**Les liens de back-office**, pour mémoire :

| Back-office | Lien | État |
|---|---|---|
| Partenaires — admin Mongazi | `https://partenaires.nebula-agency.online/cockpit-d59fa50d` | ⛔ hors ligne |
| Partenaires — espace partenaire | `https://partenaires.nebula-agency.online/partenaire` | ⛔ hors ligne |
| Luxury Club 229 | `https://luxuryclub229.com/admin` | ✅ en ligne |
| Boussole — cockpit licences | `https://boussole-19d.pages.dev` → `#cockpit-licences` | ✅ en ligne |

**Le reste du parc va bien.** Audit complet du 2026-08-01 : les 12 sites Cloudflare Pages
répondent 200 et servent exactement la source locale. Détail et méthode dans
`_memoire/conversations/2026-08-01-deploiement-general-audit-du-parc.md`.

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
| `01-AVIS-DE-RECRUTEMENT.md` | ⛔ **INTERNE.** Le dossier de recrutement complet : grille de sélection /20, script d'entretien, plan de diffusion. **Ne jamais l'envoyer à un candidat** — il connaîtrait les réponses attendues |
| `01b-ANNONCE-PUBLIQUE.md` | ✅ **PUBLIC.** L'annonce seule, à envoyer librement à qui veut devenir partenaire |
| `PROMPT-AFFICHE-RECRUTEMENT.md` | Prompt de l'affiche A4 + variantes 9:16 et 1:1. ⚠️ **le QR ne se génère pas par IA** : le vrai est dans `vente/assets/` |
| `02-MANUEL-DU-PARTENAIRE.md` | Le métier : prospection, **méthode de vente en 7 temps**, relance, brief |
| `03/04/05-GUIDE-*.md` | Un guide par service, anatomie en 12 chapitres |
| `06-ARSENAL-SCRIPTS.md` | Tous les messages prêts à copier |
| `07-MISE-EN-LIGNE.md` | Procédure de publication et état des actions |
| `08-DIAGNOSTIC-DIGITAL.md` | La consultation pro : 40 questions + grille des automatisations |
| `09-CONTRAT-PARTENAIRE.md` | Contrat d'apporteur d'affaires en 16 articles |
| `10-RELANCE-RENOUVELLEMENT.md` | Spécification de la relance des abonnements |
| `11-MESSAGES-GROUPE-PARTENAIRES.md` | **Quoi envoyer aux partenaires actifs** : 3 PDF sur 9, 5 messages prêts à copier, et ce qu'on ne diffuse pas |
| `simulateur-commissions.html` | Le partenaire calcule ses gains du mois |
| `fiche-diagnostic.html` | Fiche remplie chez le client → rapport WhatsApp |
| `pdf/` | Les 9 documents en PDF, régénérables via `_build_pdf.py` |
| `marketing/PROMPTS-POSTS-LE-SAVIEZ-VOUS.md` | Prompt-maître Nano Banana Pro + **15 posts** : 8 en rythme de croisière (mardi/vendredi, un mois) + **7 en campagne intensive, un par jour pendant une semaine** (§3bis) |
| `marketing/PROMPTS-POSTS-OCCASIONS.md` | Posts de fête (1er août, nouvel an…). ⚠️ **ordre des images inversé** : 1 = référence, 2 = logo |

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
| Commission | **30 %** par vente · **40 %** dès que ses ventes + celles de ses filleuls atteignent **3** dans le mois. Repart à zéro le 1er |
| **Récurrent** | **20 % de chaque abonnement, tous les 6 mois, À VIE** (4 000 F/client/semestre), même après son départ. Ne compte pas dans le palier |
| Parrainage | **Aucune commission, à aucune profondeur** (2026-08-02). Les ventes des filleuls directs comptent avec les siennes pour le palier des 40 %, à partir de sa 1re vente |
| Versement | **24 à 72h** après réclamation |
| Vague 1 | Cotonou, **AUCUN QUOTA DE PLACES** *(décision 2026-08-01, remplace les 8 places)*, candidatures 21 jours, objectif 30 ventes / 90 jours |
| **Le filtre** | L'**entretien**, obligatoire — c'est le seul qui reste. **Le vrai plafond n'est plus le nombre de partenaires mais la capacité à livrer en 5 à 7 jours** : le jour où ce délai glisse, on ralentit le recrutement |
| **Guides** | **Les 5 guides sont remis dès l'entrée** (2026-08-01). Ce qui reste échelonné, c'est le **droit de conclure seul** : Vitrine après la 1ʳᵉ vente livrée, Outil métier après 3 ventes + binôme. Avant, le partenaire passe la main et **garde 100 % de sa commission** |

---

## 3. CE QUI BLOQUE — à faire par Mongazi

**Aucun de ces points ne peut être fait depuis une session distante.**
*3.1 et 3.3 sont faits. Restent 3.2, 3.4, 3.5, plus les 8 informations du client 10 (§3bis).*

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

### 3.3 ~~Compléter le numéro IFU~~ ✅ RÉGLÉ le 2026-08-01
Décision de Mongazi : l'IFU viendra plus tard. Le contrat porte désormais
**« IFU et RCCM en cours d'immatriculation — les numéros seront communiqués au Partenaire
dès leur obtention »**. C'est exact, et le contrat est **signable en l'état**.
Le jour où les numéros arrivent : un avenant d'une ligne suffit.

### 3.4 Téléverser les 9 PDF dans l'espace partenaire
`/admin` → Documentation → Ajouter. Catégories et descriptions : `07-MISE-EN-LIGNE.md` §1 et §3.
⚠️ Le socle `00` et l'avis `01` **ne se publient pas** : documents internes.

### 3.5 L'image de référence des posts
Jamais reçue malgré plusieurs demandes. Sans elle, le bloc `STYLE INHERITANCE` du
prompt-maître reste générique.

---

## 3bis. Client 10 · HILLARY M. STYL — ⚠️ EN LIGNE, MAIS EN ANCIENNE VERSION

**https://hillary-m-styl.pages.dev est en ligne depuis le 2026-08-01 19h27** (autre session,
projet Cloudflare `hillary-m-styl`), **avec la V2 — sans la direction artistique « LE FIL ».**

## 🚀 POUR DÉPLOYER LA V3 : lire `clients/10-hillary-m-styl/DEPLOIEMENT.md`

**⚠️ LE PIÈGE : la V3 n'est PAS sur `main`.** Elle est sur la branche
`claude/github-repo-context-nisd2r`. Déployer depuis `main` republie l'ancienne version —
le site ne bouge pas, et on croit à un échec alors que tout a marché.

Le test en une commande : `grep -c "Bodoni Moda" clients/10-hillary-m-styl/vitrine.html`
→ **0 = mauvaise version, ne pas déployer.**

```bash
git fetch origin && git checkout claude/github-repo-context-nisd2r && git pull
cd clients/10-hillary-m-styl && python3 _predeploy.py
npx -y wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main
```

**`_predeploy.py` s'arrête au premier problème** : mauvaise version, construction ratée,
QC rouge, placeholder resté dans la page. Le site est vivant — on ne déploie pas « pour voir ».

Les apports de l'autre session sont **conservés** dans la source V3 : vrai numéro WhatsApp,
« retrait sur rendez-vous · le point de retrait vous est donné sur WhatsApp », carte
« Confection » au lieu d'« Horaires », valeurs en dur dans le HTML. ⚠️ **`_outils/_apply_infos.py`
est OBSOLÈTE** (il patchait le livrable, ce qui écraserait la V3) et **`og:url`/`canonical`
restent à reposer dans `_vitrine_src.html`**. Détail au §6ter de son CONTEXT.md.

## 3bis. Client 10 · HILLARY M. STYL (v2 le 2026-07-31, **v3 « LE FIL » le 2026-08-01**)

Vitrine couture avec **moteur de commande**. La v2 a refait le cœur de l'outil :
**les mesures dépendent du type de vêtement, pas du genre du client.**

| Type de vêtement | Mesures |
|---|---|
| Robe coupée à la taille | 9 |
| Robe droite | 15 |
| Robe ovale | 11 ⚠️ **à faire valider par l'atelier** |
| Pantalon | 6 |
| Chemise ou haut | 8 |

Le reste : prix **et** délai sur chaque carte · délai express **1 à 3 jours** · **la date
précise de disponibilité s'affiche** dès les options validées, calculée sur la borne haute
du délai + l'acheminement du pays · WhatsApp **ou** email · Mobile Money annoncé comme seul
moyen de règlement · section À propos · double notification expliquée.

**La v3 a refait toute l'enveloppe** sur une direction artistique — « LE FIL », le fil qui
va du mètre-ruban au vêtement — **sans toucher au moteur de commande**. Bodoni Moda pour
les titres, une animation signature par section (la piqûre, le patron à la craie, le fil
qui relie, le drapé, la coupe aux ciseaux), le croquis de la robe qui se dessine au héros,
l'aiguille en guise de curseur. Détail complet au §8 du CONTEXT.md du client.

**⚠️ On édite `_vitrine_src.html`, jamais `vitrine.html`** (généré, 174 Ko dont 75 de logo) :

```bash
cd clients/10-hillary-m-styl
python3 _build.py     # source -> vitrine.html
python3 _qc.py        # 71 contrôles, doit être « TOUT EST VERT »
```

✅ **Le numéro WhatsApp est arrivé le 2026-08-01 : +229 51 37 47 93** → `wa.me/22951374793`,
câblé et vérifié dans la page. ⚠️ **Reste à l'essayer une fois avec un vrai message** : le
dépôt utilise deux formats (8 chiffres comme celui de Mongazi, ou 10 avec le préfixe `01`
comme les autres clients). Si ça n'ouvre pas le bon contact, essayer `2290151374793`.
Détail au §6bis du CONTEXT.md.

⚠️ **Ne pas mettre en ligne avant d'avoir les 7 informations restantes du §6.**
Les deux plus graves : les frais d'expédition et les jours d'acheminement sont des
exemples (un tarif faux coûte de l'argent à chaque commande, un acheminement faux fausse
la date promise) · **les mesures de la robe ovale n'ont jamais été fournies** et sont une
proposition, signalée comme telle dans l'interface.

## 3ter. 🎨 NOUVEAU STANDARD — toute vitrine, à partir du 2026-08-01

**`_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md` — à lire avant d'écrire une ligne
de CSS, sur chaque client.**

Né d'une phrase de Mongazi devant une vitrine pourtant irréprochable : « je vois un site
à 100 $ ». En résumé : **une vitrine n'est pas finie quand elle marche, elle est finie
quand elle impressionne** · on écrit **la phrase du métier** avant le CSS, et toutes les
animations en sortent · **une signature différente par section** · la typo, le rythme
sombre/clair et le vide font 80 % de l'écart · **jamais de photo produit générée par IA** ·
**regarder les captures section par section** (six défauts sont passés au travers de 53
contrôles verts).

Branché dans `SKILL.md` (nebula-site), `PROCEDURE.md` (PHASE 1 et 6), `CONVENTIONS.md`,
`CLAUDE.md`. Gabarits `_build.py` / `_qc.py` dans `_memoire/procedure-vitrine/templates/`.
✅ **EN LIGNE depuis le 2026-08-01 : https://hillary-m-styl.pages.dev**
Mongazi a donné le vrai numéro (**+229 51 37 47 93**) : il est posé, les commandes arrivent.
Plus aucun « à confirmer » sur la page publique. Affiche A4 + 2 QR (site et WhatsApp
pré-rempli) dans `assets/docs/`, les deux QR relus et validés par décodage.

⚠️ **Ce qui reste à obtenir d'Hillary — et pourquoi ça coûte de l'argent :**
les **frais d'expédition** par pays sont encore des exemples (un tarif faux se paie à
chaque commande), ainsi que les **délais**, les **pièces et leurs prix**, et **l'adresse
de l'atelier**. **Aucune photo n'a été fournie** : les cartes affichent un visuel de
substitution. Conseil photo à transmettre : dehors le matin ou en fin d'après-midi, à
l'ombre, fond uni, format portrait.

## 4. Ce qui tourne déjà en production

**Déployé automatiquement au push sur `main` (Railway) :**
- **NOVA** annonce les bons prix. Elle citait encore la Fiche Google Maps et les Avatar IA,
  retirés du site en v9, parce que son catalogue était dérivé du dictionnaire `SERVICES`.
- **`refresh_seeded_docs()`** corrige au démarrage les 5 guides déjà en base qui poussaient
  la Vitrine en premier. Idempotente, ne touche pas les documents ajoutés à la main.
- **Module Abonnements** : table `subscriptions`, ouverture automatique à l'encaissement,
  commission de 20 % au renouvellement, 6 endpoints, portefeuille partenaire.

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
