# NEBULA Affiliés — Cerveau du produit

> Bureau virtuel du programme partenaires/affiliés de NEBULA Agency. Back-office 2 faces, base SQLite, design cosmique « Ethereal Glass », cerveau IA NOVA. Tout est interconnecté et en temps réel.

Dernière grosse mise à jour : **2026-06-17**.

---

## 1. Accès & URLs

- **App LIVE** : https://nebula-affilies-production.up.railway.app
- **Domaine custom** : `partenaires.nebula-agency.online` → ⏳ **SSL bloqué** (voir §7).
- **Espaces** :
  - `/` portail (connexion partenaire OU admin) — marqué « réservé aux partenaires »
  - `/partenaire` espace partenaire (code + PIN)
  - `/admin` console NEBULA (Mongazi)
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

## 3. Système de gains (3 couches) — à valider par Mongazi

1. **RANKING cosmique** (prestige, ventes CUMULÉES) : Météore 1-5 / Comète 6-15 / Planète 16-35 / Étoile 36-65 / Supernova 66-110 / Nébuleuse 111-150 / **Galaxie 151+** (statut spécial). Icônes SVG pro.
2. **PALIERS mensuels** (= commission DIRECTE, remis à zéro chaque mois) : STARTER 1-4 = 25 % / SILVER 5-9 = 30 % / GOLD 10+ = 35 %.
3. **PROFONDEURS réseau** (fixes) : N1 = 10 % (recrues directes), N2 = 5 % (recrues des recrues).

« Une vente » = un lead **payé**. Commission générée **automatiquement** quand l'admin marque le paiement.

---

## 4. Inventaire des fonctionnalités (toutes LIVE)

- **Back-office 2 faces** : statuts client (attente / en cours / terminé / annulé), paiement gris↔vert fluo, notifs in-app.
- **Commissions automatisées** : vente payée → 3 commissions auto (direct + N1 + N2) → chacun alerté → **Réclamer** (partenaire) → admin voit le MoMo → **Marquer payé** (groupé) → notifié. Registre 100 % tracé. **RCM poussé** = bilan à vie (`earnings_of`).
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

## 8. Liens mémoire

Brain lié à la mémoire auto `project-nebula-affilies` (la plus à jour, détail technique par vague) et à [[reference-railway-cli]] (API/CLI Railway), [[project-boutique-ia]] (Vendora, dont le domaine custom a été retiré pour libérer le slot), [[reference-domaines]].
