# Cercle — sécurité familiale consentie

App mobile (Expo / React Native) du produit **Cercle** de NEBULA Agency.
Partage de position **mutuel et consenti** entre membres d'un même cercle familial
(modèle Life360). **Garde-fou absolu : aucun pistage caché d'un adulte.** On ne voit
la position de quelqu'un que si l'on partage un cercle avec lui.

## Stack
- **Expo (React Native + TypeScript)** — pas besoin d'Android SDK local.
- **Supabase** (gratuit) : Auth + Postgres + RLS + Realtime.
- **EAS Build** (cloud, gratuit) : génère l'APK, distribué par WhatsApp (sideload).

## Vagues
1. ✅ Auth (tél + code), créer/rejoindre un cercle, **liste live des positions** (avant-plan).
2. ⏳ Localisation **arrière-plan + notification permanente** (anti-ban) — build EAS.
3. ⏳ Bouton **SOS**.
4. ⏳ **Alerte Disparition communautaire** (aimant viral gratuit).

## Configuration
1. Créer un projet sur https://supabase.com (gratuit).
2. SQL Editor → coller et exécuter `supabase/schema.sql`.
3. Auth → Providers → Email : **désactiver "Confirm email"** (MVP sans SMS, on mappe
   le téléphone vers un email synthétique `<tel>@cercle.app`).
4. `cp .env.example .env` puis remplir `EXPO_PUBLIC_SUPABASE_URL` et
   `EXPO_PUBLIC_SUPABASE_ANON_KEY` (Project Settings → API).

## Lancer en dev
```bash
npm install        # si pas déjà fait
npx expo start     # scanner le QR avec l'app Expo Go (Android)
```

## Notes
- La clé **anon** est publique (sûre côté client) ; la confidentialité repose sur les
  policies **RLS**. Ne JAMAIS embarquer la clé `service_role`.
- L'auth tél→email est un raccourci MVP (zéro coût SMS). À remplacer par un vrai OTP
  WhatsApp avant le lancement large.
