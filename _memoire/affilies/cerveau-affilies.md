# NEBULA Affiliés — Cerveau du produit

> Bureau virtuel du programme partenaires/affiliés de NEBULA Agency. Back-office 2 faces, base SQLite, design cosmique « Ethereal Glass », cerveau IA NOVA. Tout est interconnecté et en temps réel.

Dernière grosse mise à jour : **2026-07-31** (module Abonnements + alignement commercial).

---

## 1. Accès & URLs

- **App LIVE** : **https://partenaires.nebula-agency.online** (HTTPS valide via **relais Cloudflare Pages gratuit** — voir §5) + secours `https://nebula-affilies-production.up.railway.app`.
- **Admin Mongazi** : `…/cockpit-d59fa50d` (URL secrète, env `NAFF_ADMIN_PATH`) · `allonebiao@gmail.com` / **`dylanfurax`** (env `NAFF_ADMIN_PASS`). Anti-force-brute + portail `/` partenaire-only.
- **Partenaire** : `/` (code + PIN) · **« Code/PIN oublié ? »** → notifie l'admin qui renvoie les accès. Plus de compte DEMO (plateforme démarre vide).
- **Romaric DJANKAKI** = partenaire privilégié **40%** (code `RBNXF`, PIN `0067`, WhatsApp +229 67 21 82 56) ; aucune commission de réseau (grille unique 30/40/50). Taux perso = colonne `direct_rate_override` + endpoint admin `/rate`.
- **Espaces** :
  - `/` portail (connexion partenaire OU admin) — marqué « réservé aux partenaires »
  - `/partenaire` espace partenaire (code + PIN)
  - **Page de connexion admin PRIVÉE** sur une **URL secrète** (`console.html`, `noindex`) définie par l'env **`NAFF_ADMIN_PATH`** (valeur PROD réelle posée sur Railway, **hors git** → voir mémoire locale `.claude` ; défaut code `qg-mongazi-x7q2` inactif en prod). Mot de passe admin = env **`NAFF_ADMIN_PASS`** (renforcé, plus `founder123`). Le portail `/` n'expose PLUS l'admin (partenaire-only).
  - `/admin` console NEBULA (dashboard) — **servie uniquement à une session admin** ; sinon **302 → `/`** (ne révèle jamais l'URL secrète).
  - `/p/<code>` **lien unique** partenaire (client OU recrutement)
  - `/devenir` candidature publique (avec CGU)
  - `/r/<code>` formulaire client direct · `/rejoindre/<code>` recrutement direct (rétrocompat)
- **Comptes démo/test** : partenaire `DEMO` / PIN `1234` · admin `allonebiao@gmail.com` (ou allonebiao2@gmail.com / mongazi@nebula-agency.online) / mot de passe `founder123`.
- Lancer en local : `python -m uvicorn --app-dir nebula-affilies server:app --port 8780` → http://localhost:8780/

---

## 2. Architecture technique

- Dossier `nebula-affilies/` : `server.py` (FastAPI + SQLite, tout dedans) + pages HTML (`index`, `partenaire`, `admin`, `lead`, `rejoindre`, `devenir`, `hub`) + `static/app.js` (moteur « NA » : icônes SVG, son synthétisé Web Audio, animations, NOVA, QR, tour, etc.) + `static/app.css` (design system).
- Même stack que NEXO / Vendora : FastAPI + SQLite, 100 % gratuit, sans carte bancaire.
- **Sécurité** : PIN/mots de passe PBKDF2, sessions cookie signé HMAC (30 j).
- **Cerveau NOVA** : appel direct API Claude (clé `ANTHROPIC_API_KEY` reprise de `boutique-ia/.env` en repli), mémoire en table `brain_msgs`, modèle `claude-sonnet-4-6`.
- **Base de données** (`/data/affilies.db` en prod, volume Railway) — tables :
  - `affiliates` (code, nom, prénom, momo, pin, accent, **photo**, parrain_id, pseudo)
  - `leads` (clients), `history`, `notifs`, `recruits`, `candidatures`
  - `commissions` (registre tracé due→claimed→paid)
  - `documents`, `publications` (bibliothèques admin)
  - `messages`, `chat_reads` (messagerie), `app_settings`, `link_events` (compteur de clics)
- ⚠️ **`db()` = context manager qui FERME la connexion** (`@contextlib.contextmanager`). Avant c'était `return c` → fuite de connexions → `database is locked` sous la charge chat/polling. **NE PAS revenir en arrière.**

---

## 2bis. MODULE ABONNEMENTS (2026-07-31) — le récurrent à vie, tracé

Le programme promet au partenaire **20 % de chaque abonnement client, acquis à vie**, même
après son départ. Cette promesse n'était traçable nulle part : aucune table ne portait de
date d'échéance. Elle l'est désormais.

- **Table `subscriptions`** : `lead_id`, `affiliate_id` (celui qui touche à vie), `offre`,
  `montant` (20 000), `debut`, `echeance`, `statut`, `dernier_rappel`, `relances`.
- **`ensure_subscription(lead)`** — idempotente, appelée quand l'admin marque une vente
  payée. Catalogue et Vitrine uniquement (le QR Review n'a pas d'abonnement).
- **`record_subscription_payment(sid)`** — décale l'échéance de 6 mois **et** crée la
  commission de 20 % dans la table `commissions` avec **`level='abonnement'`**.
- **`subscriptions_due()`** — paliers J-15 / J-3 / J+3 / J+10, **un seul message par
  abonnement et par jour**, plafond de **3 relances** par échéance.
- **`_plus_mois()`** — mois calendaires, gère les fins de mois.

**Endpoints :** `GET /api/admin/subscriptions` · `GET /api/admin/subscriptions/due`
(accepte `?key=NAFF_CRON_KEY` pour n8n) · `POST …/{id}/paid` · `POST …/{id}/rappel`
(accepte aussi la clé cron) · `POST …/{id}/resilier` · `GET /api/partenaire/portefeuille`.

⚠️ **`void_commissions()` ne doit JAMAIS annuler une commission d'abonnement.** Elle a été
corrigée pour ne toucher que `level IN ('direct','n1','n2')`. Dé-marquer le paiement d'une
vente aurait sinon supprimé le récurrent acquis à vie.

⚠️ **Le palier n'est pas affecté** : il se calcule sur les *leads* payés (`_paid_value`,
`_month_paid_count`), pas sur les commissions. Ne pas changer ça.

**À poser sur Railway : `NAFF_CRON_KEY`.** Sans elle, n8n ne peut pas lire les échéances.
Spécification du workflow : `_documents/nebula-agency/vente/10-RELANCE-RENOUVELLEMENT.md`.

## 2ter. Documents de démarrage : migration automatique

`seed_content()` ne s'exécute que si la table `documents` est **vide** : modifier le code ne
corrige jamais la production. Les 5 guides seedés poussaient la Vitrine en premier, contre
la stratégie de l'escalier.

**`refresh_seeded_docs()`** (appelée au démarrage, après `seed_content()`) supprime les deux
fiches produit renommées, réécrit les trois autres **si et seulement si** leur corps porte
encore un marqueur de l'ancienne version, et **ne touche jamais un document ajouté à la
main**. Idempotente. La liste vit dans la constante module `_SEED_DOCS`.

⚠️ **Il faut un marqueur par document conservé**, sinon un guide reste en arrière et
contredit les autres. C'est arrivé avec « Répondre aux objections ».

## 3. Système de gains (3 couches) — à valider par Mongazi

1. **RANKING cosmique** (prestige, ventes CUMULÉES) : Conseiller 1-5 / Conseiller Confirmé 6-15 / Conseiller Senior 16-35 / Étoile 36-65 / Chef Régional 66-110 / Directeur Commercial 111-150 / **Directeur Associé 151+** (statut spécial). Icônes SVG pro.
2. **PALIERS mensuels** (= commission, remis à zéro le 1er) : **BRONZE 30 %** par défaut / **ARGENT 40 %** dès que ses ventes + celles de ses filleuls directs atteignent **3**. Rien au-dessus. Le taux s'applique à TOUT le mois.
3. **AUCUNE COMMISSION DE RÉSEAU** (2026-08-02) : `DEPTH_N1 = DEPTH_N2 = 0.0`, conservés à zéro pour que l'historique déjà en base continue de s'afficher. Un parrain ne touche rien sur ses filleuls ; **leurs ventes du mois s'ajoutent aux siennes dans `palier_for` pour atteindre la marche des 40 %**. Grille unique 30 / 40 / 50.

« Une vente » = un lead **payé**. Commission générée **automatiquement** quand l'admin marque le paiement.

---

## 4. Inventaire des fonctionnalités (toutes LIVE)

- **Back-office 2 faces** : statuts client (attente / en cours / terminé / annulé), paiement gris↔vert fluo, notifs in-app.
- **Commissions automatisées** : vente payée → 1 commission auto (le vendeur, et lui seul) → chacun alerté → **Réclamer** (partenaire) → admin voit le MoMo → **Marquer payé** (groupé) → notifié. Registre 100 % tracé. **RCM poussé** = bilan à vie (`earnings_of`).
- **Parrainage / réseau** : arbre N1→N2 visualisé côté partenaire ET admin (forêt complète).
- **Candidatures** : publiques (`/devenir`, avec **CGU obligatoires** horodatées + IP) + parrainées → l'admin valide dans l'onglet *Recrues* → crée le partenaire (code+PIN).
- **Documentation** : notes / PDF / liens par catégorie ; l'admin gère (upload), les partenaires lisent/téléchargent ; MAJ instantanée. Contenu pro seedé (5 guides).
- **Publication** : posts / visuels / vidéos / scripts par plateforme ; copier / télécharger / partager. Contenu seedé (4 scripts/posts).
- **Bureaux virtuels** :
  - **Classement public** : chacun voit rang/RCM/ventes/perf de tous (**clients privés**).
  - **Messagerie** : salon d'équipe + DM 1-à-1 (partenaires ↔ NEBULA), photos, badges, polling.
  - **Photos de profil** : chacun (et NEBULA) ; visibles partout.
  - **Temps réel** : polling `/api/signals` (12 s) → badges qui se remplissent + **son quand ça bouge** (voir notifs typées ci-dessous).
- **Notifications typées + sonores stylées** (2026-06-17 soir) : colonne `notifs.kind` (`client|vente|recrue|commission|paiement|statut|info`) posée à chaque `notify(kind=)` ; `/api/signals` renvoie `notif_top` (id+kind+text) → le front joue **une tonalité Web Audio distincte par type** via `sound.notif(kind)` (dispatcher dans `static/app.js` : client=arpège montant, vente=triade, recrue=« bienvenue », commission/paiement=cash, statut=blip, message=pop). Fenêtre de notif enrichie (compteur « X non lues · Y total », **pastille couleur par type** `.ndot`, **badge qui pulse**, **cloche qui sonne** `ringBell()`). Admin + partenaire.
- **Renvoyer / réinitialiser le PIN** (2026-06-17 soir) : `POST /api/admin/affiliates/{id}/reset-pin` régénère un PIN (l'ancien haché est irrécupérable) et notifie le partenaire ; bouton **« Renvoyer accès »** par partenaire dans `/admin`. Indispensable : sans ça un partenaire qui perd son PIN était bloqué.
- **Kit de bienvenue 1-tap** (2026-06-17 soir) : `renderAccessKit()` + `welcomeMessage()` (admin) → carte commune (création / validation candidature / renvoi d'accès) avec **espace `/partenaire` + Code + PIN + lien `/p/CODE`** et boutons **« Envoyer sur WhatsApp »** (wa.me pré-rempli, **sans destinataire forcé** — numéros Bénin ambigus) + « Copier le kit ».
- **Didacticiel** : guide pas-à-pas par zone (auto au 1er login + bouton « ? »).
- **Logo NEBULA partout** : favicon, dock, hub, pages publiques, filigrane de fond, avatar Salon NEBULA. Assets `static/nebula-mark.png` / `nebula-logo.png` / `favicon.png` / `og-image.png` (générés par PIL depuis `_partage/logo nebula agency.JPG`).
- **Lien unique « hub »** `/p/<code>` : logo + photo + nom du partenaire → 2 chemins (client / devenir partenaire). 1 seul QR. Deep-link `?go=client|partenaire`.
- **Aperçu pro au partage (Open Graph)** : coller le lien sur WhatsApp/FB affiche une carte (logo + titre + description). Helper `served_page()` injecte l'URL absolue via `x-forwarded-host`.
- **Compteur de clics** : `link_events` + `/api/track` (beacon, anti-scraper) → 3 stats dans « Mon lien » (ouvertures / intéressés site / intéressés partenaire).
- **Carte de visite** : canvas client-side (logo + photo + nom + rang + QR + lien) → télécharger / partager en statut WhatsApp. QR same-origin via `/api/qr`.

---

## 5. Déploiement (IMPORTANT)

- **App (Railway)** : service `nebula-affilies`, projet `impartial-achievement` (`3d1f7f58-…`), env prod (`0c5b8ec2-…`), svc id `2b02f708-…`. Build = **Dockerfile à la RACINE** du repo (cible `nebula-affilies/`) + `.dockerignore`.
  - `railway up` (upload local) **timeout** (réseau Bénin) → inutilisable.
  - **Déployer** : `RAILWAY_API_TOKEN=$(grep -oE '[0-9a-fA-F-]{36}' secrets/railway.env|head -1) railway redeploy --from-source -y -s nebula-affilies`. (Le `git push` auto-déploie aussi.)
  - Vérifier : `railway deployment list -s nebula-affilies` (SUCCESS) + `curl …/api/config` = 200.
- **Site agence (Cloudflare Pages)** : `cp 00-nebula-agency/nebula_agency_v8.html _tmp_pages/index.html` puis `npx -y wrangler@3 pages deploy _tmp_pages --project-name nebula-agency --branch main` (creds dans `secrets/cloudflare.env`). Garder les sous-dossiers `_tmp_pages/affiliation/` + `audio/`.
- **API Railway directe** (lecture cert/domaine, suppression domaine) : voir [[reference-railway-cli]] dans la mémoire auto (endpoint GraphQL + User-Agent navigateur sinon Cloudflare 1010).

### Gotchas
- Uploads admin/photo = `fetch` + **FormData** (PAS `NA.api` qui force JSON). `python-multipart` est dans requirements.
- Tester un upload en `curl` sous Windows : utiliser un **chemin relatif** (`-F 'file=@p.png'`), le curl natif ne résout pas `/tmp/...`.
- Valider la syntaxe : `python -m py_compile server.py` + extraire le `<script>` inline et `node --check`.
- Pas de Pillow en runtime (canvas navigateur pour la carte ; PIL sert seulement hors-ligne pour générer les assets logo/og committés).

---

## 6. PowerPoints & supports

- 2 PPT premium dans `Downloads/` + `_partage/` : **NEBULA_Programme_Partenaires_PREMIUM** (14 sl.) + **NEBULA_Masterclass_Closing** (13 sl.). Atelier reproductible `_tmp_deck/` (HTML → Chrome headless `?shot=N` → PNG 2560×1440 → python-pptx).

---

## 7. ⏳ EN ATTENTE / À FAIRE

- **SSL `partenaires.nebula-agency.online`** : le plan gratuit Railway n'autorise **qu'1 domaine custom** (avait été pris par `vendora.nebula-agency.online`, supprimé). Domaine recréé → **nouvelle cible CNAME** : `7tdyf6js.up.railway.app`. **ACTION MONGAZI** : chez **Hostinger**, mettre le CNAME `partenaires` → `7tdyf6js.up.railway.app`. Ensuite Railway émet le cert, puis rebasculer le lien « Connexion partenaires » du site (Cloudflare) de l'URL railway.app vers `https://partenaires.nebula-agency.online/`.
- **À valider par Mongazi** : grille RCM / taux de commission / seuils de paliers / seuils de rang.
- **Idées en réserve** (proposées, non faites) : aucune en attente — photo hub / compteur clics / carte de visite ont été livrés. Pistes futures possibles : pseudo personnalisé dans l'URL, QR brandé (logo au centre), analytics admin du réseau.

---

## 9. Vague 2026-06-20/21 — Cockpit, alertes, NOVA (toutes LIVE)

- **Arborescence = org-chart pyramide + poste de pilotage des paiements (admin)** : apex NEBULA (logo), connecteurs, insigne de rang, métriques d'équipe, zoom/pan/recherche/replier. **Tout cliquable** : badge or « dû/à payer » (pulsant si réclamé) sur qui doit recevoir (qu'il réclame ou non) ; clic → fiche `openAffiliate` (parrain/grand-parrain N1/N2, commissions + **Marquer payé**, clients + **Valider paiement**, filleuls) ; **notifs cliquables** → centrent+ouvrent la personne (`notifs.ref_aff`). Back : `/api/admin/affiliate/{id}/detail` + `/api/admin/network` enrichi (owed/clients/parrain). **Classement** ouvre aussi cette fiche + « Lui écrire ».
- **Pyramide d'équipe côté PARTENAIRE** : sa branche (lui→N1→N2), clic filleul = fiche **lecture seule** (confidentialité : jamais clients/gains privés des autres). `network_of` renvoie `rank`.
- **Vue « Rangs »** (onglet admin) : échelle Directeur Associé→Recrue, qui est à quel rang, cliquable.
- **Email d'accès automatique** (validation candidature/recrue) via **Resend** : `send_access_email`/`access_email_html`, colonnes `affiliates.email`/`recruits.email`, champ email au formulaire de recrutement, bouton admin « Envoyer ses accès par email » (`/api/admin/affiliates/{id}/email-access`). **Expéditeur = `contact@nebula-agency.online`** (seul domaine vérifié Resend). Vars Railway : `RESEND_API_KEY`,`EMAIL_FROM_ADDRESS`,`EMAIL_FROM_NAME`,`EMAIL_REPLY_TO`.
- **Carte de visite pro à imprimer** : `makeCard()` → paysage 2100×1200 (~600 DPI, 8,9×5,1 cm), logo + photo + nom/rang + QR blanc scannable + lien, polices marque.
- **Alertes renforcées** : (son) carillon fort `sfx.alert` + **vibration** (`navigator.vibrate`) à chaque notif ; (Telegram) bot **@Nova_de_nebula_bot** (webhook repris de Vendora), le partenaire relie son Telegram (Profil → Alertes Telegram → deep-link `?start=<tg_token>`), `notify()` envoie aussi en Telegram (thread). **Anti-bruit** : seulement `client|vente|commission|paiement|recrue`, opt-in (`tg_chat`), jamais en boucle. Webhook `/api/telegram/webhook` (secret `NAFF_TG_SECRET`), vars `TELEGRAM_BOT_TOKEN`,`NAFF_TG_BOT_USERNAME`. ⚠️ un seul webhook par bot → si Vendora redémarre, lui rebrancher le sien.
- **NOVA partout** : dashboard partenaire = NOVA seul (retiré « Discuter avec NEBULA Agency ») ; assistant public (app.js) + widget du site agence rebrandés **NOVA**.
- **Versions assets** : `app.css/app.js?v=20260621b` (partenaire/admin/hub). Bug de révélation `.rv` corrigé (moteur auto MutationObserver dans app.js).
- ⚠️ **Piège PowerShell** : ne jamais éditer un .py/.html via `Get-Content -Raw | Set-Content -Encoding utf8` (double-encodage UTF-8 → mojibake + BOM). Toujours l'outil Edit.

## 8. Liens mémoire

Brain lié à la mémoire auto `project-nebula-affilies` (la plus à jour, détail technique par vague) et à [[reference-railway-cli]] (API/CLI Railway), [[project-boutique-ia]] (Vendora, dont le domaine custom a été retiré pour libérer le slot), [[reference-domaines]].
