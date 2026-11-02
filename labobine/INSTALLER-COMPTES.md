# LA BOBINE · installer les comptes et la caisse (vague 4)

Le code est prêt et contrôlé (`node --experimental-strip-types labobine/_qc_caisse.mjs`, 31 verts). L'interface des
comptes est **cachée** (`OUVERT = false` dans `js/compte.js`) tant que les six étapes ci-dessous ne sont pas faites.
Elles touchent la production : chacune se fait avec l'accord de Mongazi, une par une.

| # | Étape | État (2026-11-02) |
|---|---|---|
| 1 | Créer la base : `labobine/supabase/labobine.sql` | ✅ fait par Claude : 6 tables RLS, 13 fonctions `search_path=''`, schéma invisible pour `anon` et `authenticated`, `labobine_payer` introuvable depuis le navigateur |
| 2 | Déployer `labobine-commande` et `labobine-paiement-recu` (`--no-verify-jwt`) | ✅ fait : sans compte → 401 « connexion requise », sans signature → 401 « horodatage » |
| 3 | Mongazi déclare le webhook dans SasPay → `https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/labobine-paiement-recu` (`transaction.success/failed/cancelled/created`) et colle le secret après `LABOBINE_SECRET_WEBHOOK=` dans `secrets/saspay.env` (la ligne attend) | ⏳ Mongazi |
| 4 | Secrets des fonctions : `LABOBINE_SITE=https://labobine.pages.dev` ✅ posé · `LABOBINE_SECRET_WEBHOOK` ⏳ (`npx -y supabase@2 secrets set … --project-ref xukduhqqfzogisoimhyo`) | ⏳ après l'étape 3 |
| 5 | **Connexion par e-mail** (configuration Auth du projet partagé) : ajouter `https://labobine.pages.dev/**` et `https://labobine.nebula-agency.online/**` aux Redirect URLs **en gardant celle de Boussole** ; **brancher un SMTP** (Resend, domaine `nebula-agency.online` vérifié en DKIM + SPF, clé d'ENVOI seule) ; modèles « Magic Link » et « Confirm signup » en français avec `{{ .Token }}` | ⏳ refusé au garde-fou de Claude Code (ressource partagée) : accord explicite de Mongazi. Script prêt : `python -I labobine/_installer_connexion.py` |
| 6 | Ouvrir l'interface : `OUVERT = true`, adapter les deux contrôles, QC, publication, **un vrai paiement de 1 500 F** | ⏳ après 3, 4 et 5 |

⛔ **Sans SMTP, personne ne peut se connecter** : le SMTP intégré de Supabase n'écrit qu'aux membres de l'équipe du
projet, **2 e-mails par heure**. C'est vrai aussi pour l'inscription à Boussole (`signUp` + confirmation), qui n'a
jamais pu fonctionner pour un vrai client.
⚠️ **Les confirmations d'e-mail sont activées** : un nouveau client qui demande un lien reçoit le modèle
« Confirm signup », pas « Magic Link ». Le code doit donc être dans les deux. Il fait **8 chiffres** (réglage du projet).
⚠️ Boussole se connecte par **mot de passe** : changer le modèle « Magic Link » ne la touche pas ; le modèle
« Confirm signup » si (même texte pour les deux, sans nom de produit).

## Ce qui protège l'argent

- Le prix est lu dans `supabase/functions/_shared/offres.ts`, jamais envoyé par le navigateur.
- Le webhook a **son propre secret** et vérifie la signature **et** l'âge (5 minutes) ; un message rejoué sur une
  commande payée ne paie rien deux fois ; un montant ou une devise qui ne correspond pas est refusé et journalisé.
- La commande passe « payee » une seule fois, et c'est ce passage qui ouvre Pro, verse les crédits et récompense le
  parrain (`public.labobine_payer`, un seul bloc).
- Les tables sont dans le schéma `labobine`, **non exposé**, verrouillées ligne par ligne ; le navigateur ne passe
  que par les fonctions `labobine_*` qui ne rendent que ce qui appartient à la personne connectée.

## Ce qu'il faut savoir

- ⚠️ **Le filigrane est retiré dans le navigateur** : un développeur qui modifie le code de sa page peut contourner
  le verrou d'export, comme chez tout éditeur qui exporte sur l'appareil. Ce qui ne se contourne pas : les crédits et
  l'IA côté serveur (voix de synthèse, vidéo générée), facturés par le serveur.
- Pas d'essai gratuit : leçon de MA LETTRE À… (un essai se contourne en changeant d'adresse ou de navigateur).
  Le parrainage récompense seulement un **paiement**.
- Le nuage garde le **montage** (2 Mo et 200 projets au plus par compte), jamais les vidéos. Sur un autre appareil,
  les médias se rebranchent par leur nom quand on les réimporte.
