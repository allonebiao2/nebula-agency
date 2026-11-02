# LA BOBINE · installer les comptes et la caisse (vague 4)

Le code est prêt et contrôlé (`node --experimental-strip-types labobine/_qc_caisse.mjs`, 31 verts). L'interface des
comptes est **cachée** (`OUVERT = false` dans `js/compte.js`) tant que les six étapes ci-dessous ne sont pas faites.
Elles touchent la production : chacune se fait avec l'accord de Mongazi, une par une.

| # | Étape | Qui | Où |
|---|---|---|---|
| 1 | Créer la base : exécuter `labobine/supabase/labobine.sql` | Claude (avec accord) ou Mongazi | éditeur SQL du projet `xukduhqqfzogisoimhyo` |
| 2 | Déployer les deux fonctions | Claude (avec accord) | `cd labobine && npx -y supabase@2 functions deploy labobine-commande --project-ref xukduhqqfzogisoimhyo --use-api` puis `… labobine-paiement-recu … --no-verify-jwt` |
| 3 | Déclarer le webhook dans SasPay, **copier son secret** | Mongazi | tableau de bord SasPay → Webhooks → `https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/labobine-paiement-recu`, événements `transaction.success/failed/cancelled/created` |
| 4 | Poser les secrets `LABOBINE_SECRET_WEBHOOK` (celui de l'étape 3) et `LABOBINE_SITE=https://labobine.pages.dev` | Claude (avec accord) | `npx -y supabase@2 secrets set … --project-ref xukduhqqfzogisoimhyo` · le secret va aussi dans `secrets/saspay.env` |
| 5 | Autoriser l'adresse de retour de connexion | Mongazi | Supabase → Authentication → URL Configuration → Redirect URLs → ajouter `https://labobine.pages.dev/**` (et le domaine final plus tard) |
| 6 | Ouvrir l'interface : `OUVERT = true`, QC, publication, **un vrai paiement de 1 500 F** | Claude, puis Mongazi paie | `js/compte.js` |

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
- ⚠️ **E-mail de connexion** : le modèle par défaut de Supabase n'envoie qu'un lien. Pour afficher aussi le code à
  6 chiffres, ajouter `{{ .Token }}` au modèle « Magic Link » (Authentication → Email Templates). Ce modèle est
  partagé avec Boussole : ajouter le code ne casse pas le lien.
- Pas d'essai gratuit : leçon de MA LETTRE À… (un essai se contourne en changeant d'adresse ou de navigateur).
  Le parrainage récompense seulement un **paiement**.
- Le nuage garde le **montage** (2 Mo et 200 projets au plus par compte), jamais les vidéos. Sur un autre appareil,
  les médias se rebranchent par leur nom quand on les réimporte.
