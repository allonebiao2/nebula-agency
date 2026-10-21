# 2026-10-21 · MA LETTRE À… est en ligne

*Suite de `2026-10-21-malettre-reprise-et-pub.md`. Mongazi : « tu as le feu vert pour mettre en ligne ».*

**https://malettre.nebula-agency.online**

## Ce qui a été branché, dans l'ordre

1. **Les contrôles d'abord**, un à la fois (le calcul de trading 0036 occupait la mémoire) : `_qc.py` 285 ·
   caisse 373 · accueil 239 · langues 52 · faire-part 83.
2. **La base** : `malettre/supabase/lettres.sql` exécuté par `DATABASE_URL` (pooler, `prepare_threshold=None`).
   4 tables sous RLS sans politique, 10 fonctions exécutables par le seul `service_role`. Rien d'autre touché.
3. **Le webhook SasPay** : créé par Mongazi dans le tableau de bord (SasPay n'autorise ni la création ni la
   modification de webhook par l'API, seulement la lecture). LIVE, 4 événements `transaction.*`.
   ⛔ **Il a SON secret** (SasPay signe chaque point de réception avec le sien) : rangé dans
   `secrets/saspay.env` en `MALETTRE_SECRET_WEBHOOK`, lu par `malettre-paiement-recu` **sans repli** sur celui
   de PISTE (un secret absent doit refuser, pas deviner). `_shared/saspay.ts` reste la copie exacte de PISTE.
   Un contrôle de la caisse le garde.
4. **Le jeton Supabase du PC était mort** (« Invalid access token ») : Mongazi en a créé un. Le secret du
   webhook et le jeton ont transité par **le presse-papiers**, lus et rangés sans jamais apparaître dans la
   conversation (`ranger_secret.py`, fin de ligne du fichier respectée : la leçon du CRLF de PISTE).
5. **Les secrets Supabase** : `MALETTRE_SITE`, `MALETTRE_SECRET_WEBHOOK`, `ANTHROPIC_API_KEY` (celle du Bureau,
   comme le banc d'essai). ⚠️ Poser des secrets fait monter d'un cran la version de **toutes** les fonctions du
   projet, PISTE compris, sans toucher leur code (leur date de modification ne bouge pas). Ce n'est pas un
   redéploiement ; PISTE a répondu normalement juste après.
6. **Les 4 fonctions**, sans CLI installée : `npx -y supabase@2 functions deploy … --use-api`. La clé
   `sb_publishable_…` **passe** la vérification du jeton (mesuré : la fonction répond « palier inconnu », pas la
   porte) : commande et plume restent vérifiées.
7. **Le site** : projet Pages `malettre` créé, domaine déclaré par l'API, CNAME `malettre` → `malettre.pages.dev`
   posé avec le jeton de zone. Certificat actif en quelques minutes. `robots.txt` servi sans ajout de
   Cloudflare, GPTBot / ClaudeBot / PerplexityBot en 200.

## ⛔ Le piège de la mise en ligne : Supabase sert tout HTML en texte

Mesuré sur la fonction déployée : **`Content-Type: text/plain` et `Content-Security-Policy: default-src 'none';
sandbox`**, plus un cookie de `supabase.co`. C'est la défense de Supabase contre les pages d'hameçonnage hébergées
sur ses adresses. Le relais recopiait tout : **la lettre se serait affichée en code source, scripts bloqués.**

- **Aucun contrôle ne pouvait le voir** : la fausse fonction de la caisse répondait en `text/html`. Elle imite
  désormais la vraie réponse (type, `sandbox`, cookie, en-têtes internes), et quatre contrôles la gardent.
- **La correction** : le relais ne garde que les en-têtes choisis (`cache-control`, `x-robots-tag`,
  `referrer-policy`, `x-content-type-options`) et rend leur type aux pages. Elle retire une protection : le
  garde-fou de Claude Code l'a bloquée, la question a été posée à Mongazi, **il l'a autorisée**. Elle est juste
  ici parce que seules passent les pages bâties par NOTRE fonction sur NOTRE gabarit, le texte de l'acheteur
  neutralisé par `_injecter` (c'est ce que Supabase permet avec un domaine personnalisé payant).
- Caisse : **379** contrôles verts.

## Essayé en ligne, puis effacé

- Lettre offerte créée → ouverte par le domaine (HTML, sans `sandbox`, sans cookie, `noindex`) → **photographiée
  au téléphone** (enveloppe, cachet, puis la lettre et « Retirer cette lettre », aucune erreur) → retirée en vrai
  (« C'est retiré », puis 410 « Cette lettre n'existe plus »).
- Commande « La Lettre » : session SasPay à **5 000 XOF**, retour sur `merci.html?j=<jeton>`, référence = jeton ;
  la lettre répond 425 « pas encore prête » ; session **annulée** (l'annulation ne crée aucune transaction, donc
  aucune notification).
- Webhook éprouvé à la main comme SasPay le signe : valable 200 et journalisé, signature fausse 401, horodatage
  vieux de 2 h 401.
- La plume : une vraie lettre (« Le piment renversé à Fidjrossè »), version 1 sur 5.
- Les lignes d'essai (2 lettres, 1 session, 1 événement, 1 entrée de la plume) sont **effacées** : la base démarre à zéro.

## Ce qui attend Mongazi

- ⏳ **Le premier franc réel** : le plus petit est l'offre gratuite + la plume, **500 F**. C'est le seul essai qui
  prouve le dernier maillon (une notification SasPay réelle, signée par SasPay, qui ouvre une lettre).
- La commission SasPay · qui relit le deuil · `malettre.app` · les six MP3 de la pub · les critères d'arrêt
  (1er décembre, ou huit semaines après la mise en ligne : 16 décembre).

## Leçons

- **Une fausse dépendance doit répondre comme la vraie, pas comme on croit qu'elle répond.** La fausse fonction
  du relais renvoyait ce que notre code envoie (`text/html`), pas ce que Supabase rend. Le seul essai qui l'a vu
  est la requête réelle, en lisant **tous** les en-têtes.
- **Un secret de webhook appartient à un point de réception, pas à un compte** : deux webhooks sur un même compte
  SasPay = deux secrets, et les secrets Supabase valent pour tout le projet.
