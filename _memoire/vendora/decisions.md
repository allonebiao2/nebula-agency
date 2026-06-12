# Décisions produit (datées)

## 2026-06-12
- **Vendora Support = 2e pilier** : l'agent peut faire du SUPPORT, pas que vendre. Mode `agent_role` (vendeur|support), base de connaissances (FAQ + PDF + lecture auto du site), canaux WhatsApp + **widget site** « Discuter avec nous », escalade → ticket + notif patron, rapport (récurrents + corrections + visiteurs). Choix à l'inscription + onglet back-office. **LIVRÉ + déployé.** Voir [[capacites]].
- **Packaging support** : base (WhatsApp + FAQ + escalade) dans TOUS les forfaits ; premium (widget / PDF / lecture site / rapport) réservé **Business/Empire** (protéger la marge — le support peut faire un GROS volume). Ce n'est PAS une offre séparée : même produit, 2 visages, un métier à la fois.
- **Cerveau mis à jour** : `_VENDORA_FACTS` (`core/support.py`) sait désormais expliquer/proposer le mode support → les agents qui parlent de Vendora l'intègrent.

## 2026-06-10
- **Modèles** : réponses client + rédaction = **Sonnet** ; Opus réservé au lourd créatif. Posé dans `config.py` + variable Railway `CLAUDE_MODEL` (staged). Voir [[modeles]].
- **Back-office client réorganisé WhatsApp-first** : bloc « Votre agent WhatsApp » en haut (lien + numéro + stats), onglets réordonnés, Réseaux repoussé, **super-guide pas-à-pas** (étape « à faire maintenant » en surbrillance). `boutique.html` + `server.py`.
- **Skills honnêtes** : Messenger/IG, comment-to-DM, email pro, **prospection** passés en **« Bientôt »** (badge, non activables) dans `capabilities.py`. Raison prospection = OSM sans emails (vérifié : Cotonou beauté 0 / mode 1 / resto 4-60). Voir [[capacites]], [[prospection]].
- **Concret only (soir)** : les capacités « bientôt » RETIRÉES de l'UI (page de vente + back-office), pas juste badgées ; prospection masquée ; filtre dans `capabilities_context`. On ne montre que ce qui marche aujourd'hui.
- **Cerveau Vendora** créé ici (`_memoire/vendora/`), dans le dossier NEBULA (Obsidian + GitHub).
- Page Facebook **Vendora** + Instagram pro **@vendora_bj** créés (visuels générés `_partage/vendora-fb/`).

## Antérieur (repères)
- WhatsApp prod réel validé (Cloud API, numéro partagé). Voir [[canaux]].
- Positionnement « vos employés IA sur WhatsApp ». Priorité = 1ers clients payants en direct.
