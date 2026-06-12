# Vendora Support — Spécification v1

> Le 2ᵉ pilier de Vendora : un **agent de support client IA** pour tout business ayant un site / SaaS / vitrine. Même moteur que le vendeur, cerveau différent : **le vendeur conclut une vente ; le support explique, dépanne, escalade — et fait remonter ce qu'il faut corriger.**
> Cas pilote : **Abakar (WE ACT)**. Spéc générique (valable pour tout client).
> NEBULA · juin 2026 · ⚠️ estimations de temps à confirmer.

---

## 1. Objectif

Permettre à un client (business) de brancher un agent qui **répond à ses utilisateurs 24h/24, sur son site ET sur WhatsApp**, à partir de SA base de connaissances (FAQ, docs, PDF, infos libres). L'agent :
- répond avec exactitude (jamais inventer),
- **escalade quand il ne sait pas ou face à une plainte** (et notifie le patron du problème précis + le contact de la personne),
- **rend des comptes** (rapport périodique),
- et — le vrai différenciateur — **repère les problèmes récurrents et propose au business les corrections à faire** pour que ça ne se reproduise plus.

---

## 2. Principe directeur (3 règles non négociables)

1. **Grounded** — l'agent répond UNIQUEMENT depuis la base de connaissances du client. Aucune invention. (Réutilise la discipline anti-hallucination déjà en place dans Vendora.)
2. **Escalade-si-doute** — hors de sa base, ou plainte/mécontentement → il ne devine pas : il rassure (« je vérifie avec l'équipe »), **notifie le patron** avec le problème exact + le contact, et trace le ticket.
3. **Boucle d'amélioration** — chaque conversation nourrit un cerveau qui identifie les questions/plaintes récurrentes et **génère des recommandations de correction** au business (FAQ à compléter, étape à clarifier, bug à régler).

---

## 3. Périmètre v1 (lean) — ce qui est DEDANS / DEHORS

**DANS la v1 :**
- Choix du **rôle d'agent** : `vendeur` (actuel) ou `support` (nouveau).
- **Base de connaissances** : champs FAQ + texte libre + « apprends à l'agent » + **upload PDF** (extraction texte) + coller le contenu d'un lien. *(Crawl auto du site = phase 2.)*
- **Moteur Support** : persona dédiée, grounded, escalade-si-doute.
- **2 canaux** : **WhatsApp** (réutilisé) + **widget de chat embarquable sur le site** (minimal).
- **Escalade & notification** au patron (WhatsApp/email/cockpit) avec contact + problème précis.
- **Rapport hebdomadaire** au client : nb de questions traitées, % résolu sans humain, escalades, **top problèmes récurrents + corrections suggérées** (généré par IA).
- **Multi-tenant** : chaque client = sa base + son agent isolés (déjà le cas).

**DEHORS (phases suivantes) :**
- Phase 2 : crawl automatique du site/liens ; **RAG** (recherche dans une grosse base) ; canaux Messenger/Instagram/email pour le support ; suggestions d'auto-amélioration de la FAQ validées en 1 clic.
- Phase 3 : scoring de satisfaction, clustering avancé des tickets, intégrations (Zendesk/Notion…), multi-agents par équipe.

---

## 4. Les 3 acteurs & leurs parcours

- **L'utilisateur final** (client du business) : pose ses questions sur le site (widget) ou WhatsApp → réponse immédiate ; si l'agent ne sait pas → « l'équipe te revient » + il est mis en relation.
- **Le client / patron du business** (ex. Abakar) : configure sa base de connaissances, choisit le ton, reçoit les escalades en temps réel, lit son rapport hebdo, **corrige l'agent en langage naturel** depuis le back-office.
- **NEBULA / Mongazi (admin)** : pilote la plateforme, les modèles, la facturation, le support de 2ᵉ niveau (déjà le cockpit existant).

---

## 5. Spécification fonctionnelle

### A. Type d'agent
- Nouveau réglage par client : **`agent_role` = `vendeur` | `support`** (défaut `vendeur` → aucune régression).
- À l'inscription / dans le back-office, le client choisit « Mon agent VEND » ou « Mon agent fait du SUPPORT ».
- Le routage des messages entrants (WhatsApp, widget) lit ce rôle → dirige vers le moteur vendeur OU le moteur support.

### B. Base de connaissances (le cœur du nouveau travail)
Onglet back-office **« Base de connaissances »** :
- **FAQ / Infos** : grand champ texte (questions-réponses, procédures, politiques, horaires…).
- **À propos / contexte** : description du produit/service, ce qu'il fait, pour qui.
- **Apprends à l'agent** : zone en langage naturel (« quand on te demande X, réponds Y », « ne promets jamais Z »).
- **Documents PDF** : upload → le serveur **extrait le texte** (pypdf) → stocké en « morceaux » (chunks) de connaissance.
- **Liens** : le client colle l'URL **et le contenu clé** (v1) ; crawl auto = phase 2.
- **Mode test** : une fenêtre « teste ton agent » avant la mise en ligne (réutilise le chat de démo existant).

Utilisation par l'agent (v1) : la base est **injectée dans le prompt système** du support (avec **prompt caching** → coût quasi nul sur les messages répétés). Plafond de taille ; au-delà → troncature/filtre par mots-clés en v1, **RAG en phase 2**.

### C. Le moteur Support (persona + comportement + outils)
- **Persona** : patient, pédagogue, clair, dans le ton de la marque, multilingue (FR + locales), **n'invente jamais**, va droit au but, rassure.
- **Comportement** :
  - Répond depuis la base.
  - Si hors-base / pas sûr → **escalade** (outil) + message d'attente honnête.
  - Si plainte / mécontentement / même problème répété malgré explication → **escalade prioritaire** + note « problème spécifique ».
- **Outils de l'agent** (réutilisent le schéma `alerter_le_patron` / `signaler_probleme` existant) :
  - `escalader(probleme, contact, gravité)` → notifie le patron + crée un ticket.
  - `prendre_contact(nom, contact, sujet)` → quand il faut un rappel humain.
  - *(optionnel v1)* `noter_pour_correction(sujet)` → marque un point pour le rapport (sinon déduit automatiquement à l'analyse).

### D. Canaux v1
- **WhatsApp** : réutilise l'infra Meta/Twilio. Si `agent_role=support` → moteur support.
- **Widget site** (« sur la plateforme ») : un petit script `widget.js?code=CLIENT` que le client colle sur son site → bulle de chat → poste vers `/api/support/chat` (réutilise le pattern `/api/chat` déjà existant). Minimal : bulle + fil + envoi, aux couleurs de la marque.

### E. Escalade & notifications
- Notif au patron en **temps réel** (WhatsApp + email + cockpit) : *« [Utilisateur 229…] rencontre : “impossible de payer mon abonnement”. L'agent n'a pas pu résoudre. »*
- Tous les tickets escaladés listés dans le back-office (statut : ouvert / traité).
- Réutilise `notify.py` + le schéma support existant.

### F. Boucle d'apprentissage + rapport (le différenciateur)
- Un job hebdomadaire par client (réutilise/étend `learning.py`) lit les conversations support et produit :
  - **Statistiques** : nb questions traitées, % résolu sans humain, nb escalades, temps de réponse.
  - **Top sujets / questions récurrentes** (regroupement par fréquence).
  - **Plaintes récurrentes**.
  - **Corrections suggérées au business** (générées par le modèle « writer ») : *« 14 personnes ont demandé comment réinitialiser leur mot de passe → ajoute cette réponse à ta FAQ »* / *« le bug X revient 9 fois → à corriger »* / *« clarifie l'étape 3 de l'inscription »*.
- Livré au client par **message hebdo (WhatsApp/email)** + visible dans le cockpit.

### G. Back-office client (nouveaux éléments)
- Sélecteur **rôle d'agent**.
- Onglet **Base de connaissances** (champs + upload PDF + apprends-à-l'agent + mode test).
- Onglet **Tickets / Escalades** (liste, statut).
- Onglet **Rapport** (stats + sujets + corrections suggérées).
- Bouton **« Code du widget »** (à copier-coller sur le site).

### H. Reporting / cockpit admin (NEBULA)
- Vue globale des clients « support » : volume, escalades, coût IA (réutilise l'onglet **Coûts** F3 déjà livré).

---

## 6. Spécification technique (mapping au code existant)

**Réutilisé (déjà dans `boutique-ia/`) :**
- Moteur conversationnel + prompt caching + `model_config` + `usage.track` (coûts) → base du moteur support.
- `core/support.py` (support in-app aux commerçants) = **excellent template** à généraliser (persona support + `PROBLEM_TOOL` + réinjection des problèmes récents « known_issues »).
- Canaux : `core/whatsapp_meta.py`, `messenger_meta.py`, `inbox.py`.
- Escalade/notif : `notify.py` + schéma `alerter_le_patron`.
- Multi-tenant (`bia_merchants`), back-office (`web/templates/boutique.html`), cockpit (`admin.html`), gating (`core/capabilities.py`), apprentissage (`core/learning.py`).
- Endpoint chat HTTP : pattern `/api/chat` (démo) → base du `/api/support/chat`.

**Nouveau à construire :**
- **DB** :
  - `bia_merchants.agent_role text default 'vendeur'`
  - `bia_merchants.kb_text text` (FAQ/infos), `kb_instructions text` (apprends-à-l'agent)
  - table `bia_knowledge(id uuid, merchant_id uuid, kind text[faq|pdf|link|text], title text, content text, created_at)` (chunks, surtout PDF)
  - table `bia_support_tickets(id, merchant_id, user_contact, channel, summary, status[open|done], created_at)`
- **`core/support_agent.py`** : `build_support_prompt(merchant, kb)` + `reply(...)` (calqué sur `brain.reply`, tools = escalader/prendre_contact, grounded).
- **Ingestion PDF** : extraction texte (pypdf) à l'upload → `bia_knowledge`.
- **Widget** : `web/static/widget.js` + route `/api/support/chat` (scopée par code client) + `/widget` (snippet à copier).
- **Routage entrant** : dans le webhook WhatsApp, si `agent_role=='support'` → `support_agent.reply`.
- **Back-office** : onglets Base de connaissances / Tickets / Rapport + sélecteur rôle + upload PDF + bouton widget.
- **Rapport & récurrents** : `core/support_report.py` (étend `learning.py`) → analyse hebdo + corrections suggérées (modèle writer) + envoi.
- **Migration** Supabase pour les colonnes/tables ci-dessus.

---

## 7. Ordre de construction (sprint v1)

| # | Lot | Dépend de | Estimation |
|---|---|---|---|
| 1 | DB (agent_role, kb_text, bia_knowledge, bia_support_tickets) + migration | — | 0,5 j |
| 2 | `support_agent.py` (persona + grounded + outils escalade) | 1 | 1 j |
| 3 | Back-office : sélecteur rôle + onglet Base de connaissances (texte + apprends) + mode test | 1,2 | 1 j |
| 4 | Routage WhatsApp → moteur support + escalade/notif patron + onglet Tickets | 2 | 0,5 j |
| 5 | Upload PDF + extraction → base | 1,3 | 0,5 j |
| 6 | Widget site (`widget.js` + `/api/support/chat` + snippet) | 2 | 1–1,5 j |
| 7 | Rapport hebdo + détection récurrents + corrections suggérées | 2,4 | 1 j |
| **Total v1** | | | **≈ 5–6 jours** |

**Phases suivantes :** crawl site + RAG (gros volume) · canaux Messenger/IG/email support · auto-suggestions FAQ en 1 clic · scoring satisfaction.

---

## 8. Tarification & packaging (recommandation)

- **« Vendora Support »** = ligne de produit distincte (ou capacité activable). Le client choisit « Vendre » ou « Servir » (ou les deux plus tard).
- Métrique de valeur = **volume de conversations/tickets traités** (pas le nb de produits). Paliers selon le volume.
- Argumentaire ROI : *« combien d'heures par semaine tu passes à répondre aux mêmes questions ? L'agent te les rend, 24/7, et te dit en plus quoi corriger. »*
- À valider par Mongazi (financier).

---

## 9. Garde-fous & risques

- **Exactitude = réputation** (un mauvais conseil nuit au business) → grounded + escalade-si-doute + **mode test obligatoire avant mise en ligne**.
- **Qualité de la base** : garbage in/out → la zone « apprends à l'agent » + le rapport « corrections suggérées » améliorent la base dans le temps.
- **Scope** : NE PAS tout construire ; v1 minimale, on étend après le pilote.
- **Limite de contexte** (grosse base) : v1 injecte la base (caching) ; **RAG en phase 2** dès que ça grossit.
- **Confidentialité** : la base d'un client n'est jamais visible par un autre (isolation multi-tenant déjà en place).

---

## 10. Cas pilote — Abakar (WE ACT)

1. On crée son espace, `agent_role = support`.
2. Il colle sa FAQ + les infos de WE ACT + uploade ses PDF (guides/CGU).
3. On branche son WhatsApp (là où il reçoit ses questions) + on lui donne le snippet widget pour son site.
4. Mode test → on vérifie les vraies questions qu'il reçoit le plus.
5. Mise en ligne → il reçoit les escalades + le 1ᵉʳ rapport hebdo.
6. **Critère de succès** : % de questions résolues sans lui + le rapport lui fait gagner du temps ET améliorer WE ACT. S'il valide → on déroule les phases 2/3 et on vend « Vendora Support » à d'autres SaaS/services.

---

*Spéc à exécuter en vagues testées (cf. méthode habituelle). Rien n'est déployé/commité sans validation de Mongazi.*
