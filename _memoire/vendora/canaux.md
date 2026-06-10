# Canaux

## WhatsApp — LE canal autonome (live ✅)
- API **WhatsApp Cloud** (Meta), token Système permanent, numéro partagé `+229 62046155` (routing par code `vendora:CODE` / session / nom de boutique).
- L'agent reçoit + répond tout seul, 24h/24. Testé en vrai. Gratuit (conv. service entrantes).
- ⚠️ On ne branche JAMAIS le numéro via les boutons « WhatsApp Business » grand public (FB/IG) → conflit avec l'API Cloud.

## Messenger + Instagram — codé mais « Bientôt » ⏳
- Code prêt : `core/messenger_meta.py` (inbound DM + comment-to-DM). Dormant tant que `MESSENGER_PAGE_TOKEN` absent.
- **Blocage** : pour répondre au PUBLIC, l'app doit être en **mode Live + App Review de `pages_messaging`** (vérifié). Sinon → seulement les admins/testeurs de l'app.
- Page FB **Vendora** + IG pro **@vendora_bj** créés (2026-06). Reste : lien IG↔Page (propagation), token, webhook, App Review.
- Stratégie : FB/IG = **aimant/contenu** qui ramène vers WhatsApp (où l'agent ferme). Auto-post sur notre propre page = OK sans review ; réponse auto au public = App Review.

## Email
- Sortant via **Resend** (domaine vérifié `nebula-agency.online`, SPF/DKIM). Entrant via catch-all → libellé Vendora.
- Boîte par boutique = alias `code@nebula-agency.online` (réponses dans le back-office). Dormante jusqu'à 1ère boutique active.

Lié : [[prospection]], [[capacites]], [[garde-fous]].
