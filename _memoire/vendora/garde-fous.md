# Garde-fous & gouvernance

Principe (validé) : **l'agent propose/agit dans ses garde-fous, Mongazi valide oui/non, le FINANCIER reste à Mongazi.** Toute nouveauté autonome = **OFF par défaut** + toggle cockpit.

## Règles
- Nouveautés autonomes OFF par défaut (économie tokens, pas encore de clients).
- Avertir AVANT d'agir des risques plateforme/technique, avec le pourquoi + proposer la voie conforme.
- Honnêteté : n'afficher « actif » que ce qui marche vraiment (sinon « Bientôt »). Voir [[capacites]].
- Conformité : jamais de cold DM WhatsApp (ban) ; email avec opt-out + warm-up ; comment-to-DM = réponse privée à un commentaire (consentement), jamais de cold DM.

## Contrôles cockpit (admin, Mongazi)
- Boutons ON/OFF des capacités/actions autonomes de Vendora (existant, à étendre).
- 🔜 Panneau pour **ajuster modèle + effort par tâche/niveau** (voir [[modeles]], [[evolution]]).
- Validation des paiements, prospection auto, recrutement, relances.

## Conformité données (APDP / Code du numérique Bénin) — livré 2026-06-12
- **Distinction clé** : données PERSONNELLES du client (effaçables) ≠ **intelligence de Vendora** (gardée).
- **Droit à l'effacement** : le client peut écrire « supprime mes données » → outil `effacer_mes_donnees` (cerveau vendeur) → `delete_customer_data()` supprime messages/notes/ardoise/session, **anonymise** les commandes (gardées pour la compta), prévient le commerçant.
- **ON N'EFFACE JAMAIS les données d'apprentissage de Vendora** : leçons anonymisées (`bia_lessons`), A/B (`bia_experiments`), coûts (`bia_usage`), intelligence collective → conservées **pour toujours**, même si le client part. Elles n'identifient personne → conforme + nourrit l'auto-amélioration. (Décision Mongazi 2026-06-12.)
- **Pas de purge auto** des conversations (`purge_old_messages` = utilitaire manuel) → on garde la donnée pour s'améliorer.
- **Consentement marketing (opt-in)** : `definir_preference_promos` + table `bia_optin` ; jamais de promo non sollicitée ; STOP = `bia_optouts`. Base prête pour les diffusions (templates) — voir [[canaux]].
- Responsable de traitement = le **commerçant** ; Vendora = **sous-traitant** (annexe DPA dans `/confidentialite`).
- Docs : `_audit/analyse-vendora-produit-2026-06.md`, migration `db/migrations/2026-06-12-conformite-apdp.sql`.

## Vérification avant d'affirmer
Jamais d'info plateforme/prix non vérifiée. Marquer ✅ vérifié vs ⚠️ à vérifier ; sourcer ou tester. Confiance totale exigée.
