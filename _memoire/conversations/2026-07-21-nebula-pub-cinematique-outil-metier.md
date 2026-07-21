# 2026-07-21 — Pub cinématique NEBULA « Ton outil métier » (Higgsfield + montage ffmpeg)

Mongazi veut une **pub cinématique NEBULA** (TikTok / Insta Reels / statut WhatsApp) réalisée **avec Higgsfield**. Après recadrage : NE PAS parler « vitrines », mais **la conception d'outils digitaux sur-mesure par secteur** (logiciel métier / vertical SaaS), adaptés aux **réalités africaines** (secteurs pas encore digitalisés, travail à la main → devrait se faire en ligne). Créer le besoin + valeur + urgence, **voix off + son**.

## Décisions (questions validées)
- **Scénario « Le Cahier »** (le registre à la main = symbole du business non digitalisé en Afrique).
- **30 s, tout vidéo** (~35 cr) — pas 60s (statut WhatsApp = 30 s max).
- **Voix off + sound-design, SANS musique** (option B) — car ⚠️ **Higgsfield ne génère PAS de musique** (seed_audio = TTS uniquement). CTA final = **contacter NEBULA sur WhatsApp +229 96 74 07 32** (pas d'offre inventée).

## Script voix off (FR, voix « Orion » seed_audio, grave)
« On est en 2026, et ton business tourne encore sur un cahier. Tu comptes à la main, tu perds du temps… et parfois, de l'argent. Ici, on fait encore à la main ce qui devrait se faire en un clic. Et si tu avais ton outil ? Pensé pour ton métier, et pour tes réalités : Mobile Money, WhatsApp, même hors connexion. Tes ventes, ton stock, tes finances : automatisés. Sois le premier de ton secteur. NEBULA conçoit ton outil. Écris-nous. »
(38,7 s brut → **accéléré à ~30 s via ffmpeg `atempo=1.29`** pour tenir 30 s.)

## Storyboard 30 s (6 plans × 5 s, 9:16)
1. Cahier + calculatrice, mains la nuit — « Ton business tourne encore sur un cahier. »
2. Fiches papier en désordre — « À la main : du temps et de l'argent perdus. »
3. Marché ouest-africain — « Ce qui se fait à la main… devrait se faire en un clic. »
4. Dashboard cosmique sur smartphone — « TON outil. Pensé pour ton métier. »
5. Data/chiffres qui s'auto-remplissent — « Ventes · Stock · Finances = automatisés. »
6. Carte de fin nébuleuse — NEBULA · AGENCY · « Ton outil. Pensé pour ton secteur. » · **CTA vert « Écris-nous sur WhatsApp +229 96 74 07 32 »**.

## Pipeline (RÉUTILISABLE) — comment produire une pub 9:16 avec Higgsfield
1. **6 images de départ** z_image 9:16 (0,15 cr pièce) → valider le look en **contact sheet** AVANT d'animer (économise les crédits).
2. **Animer les plans-clés** en vidéo : `kling3_0_turbo` image→vidéo (start_image = job_id de l'image), 5 s, ~7,5 cr. ⚠️ Kling turbo renvoie souvent une **`preset_recommendation` (ex : « IN THE DARK »)** au lieu de lancer → **relancer avec `declined_preset_id`**. Ici : 4 plans animés + 2 en **Ken-Burns** (zoompan ffmpeg) pour tenir le budget.
3. **Voix off** : `generate_audio` model **`seed_audio`** (TTS ByteDance), `voice_type:preset` + `voice_id` (via `list_voices` — ~40 voix ; « Orion » = ed69c516… masculin grave). Gère le **français**. ⚠️ **Pas de musique possible** (aucun modèle music/SFX standalone).
4. **SFX faits maison** (numpy → wav) : whoosh (bruit filtré balayé), impact (thump grave + clic), riser (montée). Higgsfield ne les fait pas.
5. **Montage ffmpeg** (imageio-ffmpeg) : par plan = scale cover 1080×1920 + overlay **PNG sous-titre** (⚠️ **`-loop 1` sur l'input PNG** sinon l'overlay ne dure qu'1 frame !) avec fade ; concat des 6 plans ; audio = VO `atempo` + SFX placés (`adelay`+`amix`) ; mux final. Carte de fin = PNG (PIL : nébuleuse + wordmark Impact + CTA vert WhatsApp) en Ken-Burns.
6. Vérifier : durée = 30,00 s, frames extraites (contact sheet), flux audio présent.

## Livrable
- **`00-nebula-agency/marketing/NEBULA_pub_metier_30s.mp4`** (30 s, 9:16, 11,9 Mo, VO+SFX+sous-titres+CTA). Copie de partage dans `_partage/NEBULA_pub_30s.mp4` (Mongazi nettoie `_partage` après).
- Crédits Higgsfield : ~32 utilisés (6 z_image + 4 Kling + 1 VO) ; solde ~10.

## ⚠️ À valider par Mongazi (je ne peux pas ENTENDRE le rendu)
- La **voix off** (accent/prononciation FR de « Orion ») — sinon régénérer avec une autre voix.
- Le **mix son** (voix vs whooshs).
- Options : ajouter une **vraie musique** (déposer un morceau libre de droits dans `_partage/` → remixer), passer en 60 s, refaire un plan.

Cf [[reference_higgsfield]] (génération), [[reference_print-generation]] (même esprit « produire sans navigateur »).
