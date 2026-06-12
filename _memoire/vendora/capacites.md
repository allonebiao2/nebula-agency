# Capacités (skills) de l'agent

« Composez votre vendeur » : le commerçant coche ce que son agent sait faire.
**Source de vérité = `boutique-ia/core/capabilities.py`** (gating réel partout).

3 couches : 🟢 socle (toujours actif) · 🔵 modules (à la carte, plafond par forfait) · 🟣 super-pouvoirs (Empire).

## Actifs (live, marchent sur WhatsApp)
- Socle : vend sur WhatsApp 24h/24, conseille, alerte le patron, **vocal**.
- Modules : photos produits, paiement à la livraison, négociation encadrée, relances auto, prise de RDV.
- Premium : apprentissage perso, images de marque (Pillow), coach commercial, réseaux sociaux (rédige + planifie ; publication 1-clic manuelle).

## Mode SUPPORT — 2e métier de l'agent (2026-06-12, LIVRÉ + déployé)
En plus de VENDRE, l'agent peut faire du **SUPPORT CLIENT**. Réglage `agent_role` (`vendeur` | `support`) par boutique, choisi **à l'inscription** ou dans l'onglet **« Mode Support »** du back-office. Même produit, 2 visages (un agent fait UN métier à la fois).
- **Base de connaissances** : FAQ collée + import **PDF** (pypdf) + **lecture auto du site** (URL → crawl) ; l'agent répond UNIQUEMENT à partir de ça (grounded), sinon il escalade (ticket + notif patron).
- **Canaux** : WhatsApp + **widget « Discuter avec nous »** sur le site (1 ligne `<script src=…/widget.js?code=…>`, bouton lumineux aux couleurs de la marque).
- **Rapport** : questions récurrentes + corrections suggérées + résumé des visiteurs (le widget logge chaque visiteur).
- **Cible** : SaaS, sites, services, formateurs, écoles, organisateurs d'événements (pilote : Abakar / WE ACT).
- **Gating** : support de base (WhatsApp + FAQ + escalade) dans TOUS les forfaits ; premium (widget, PDF, lecture site, rapport) = **Business/Empire** (`_support_premium_ok` dans `server.py`).
- **Code** : `core/support_agent.py`, `core/site_reader.py`, `core/support_report.py` · tables `bia_knowledge` + `bia_support_tickets` · le cerveau du bot de support (`_VENDORA_FACTS` dans `core/support.py`) connaît maintenant ce mode et sait le proposer.

## Nouveautés 2026-06-12 (LIVRÉ + déployé)
- **Conformité APDP** : droit à l'effacement client (`effacer_mes_donnees`), opt-in promos (`definir_preference_promos`/`bia_optin`), `/confidentialite` (DPA). On garde TOUJOURS l'intelligence anonymisée de Vendora même si le client part. Voir [[garde-fous]].
- **Paiement en chat (semi-auto MoMo)** : rapprochement montant vs total + anti-réutilisation de référence (notif + onglet Validation).
- **Messages interactifs WhatsApp** : `proposer_boutons` → boutons (≤3) / liste (4-10) sur Cloud API, repli texte ailleurs.
- **Analytics revenu** : section « Mes chiffres » (CA mois/sem/jour, panier moyen, conversion, top par CA, clients fidèles).
- **Robustesse** : pause IA / reprise humaine (réponse manuelle back-office), anti-spam (plafond/24h), alerting « agent down », export des données. Sécurité : RLS activé sur toutes les tables `bia_*`.
- **Appels** : l'agent gère les messages ; pour un appel → numéro du commerçant. **Super-vendeur** : analyse le client + pousse vers l'objectif. Voir [[vente]], [[canaux]].

## Masqués de l'UI — on ne montre QUE le concret (décidé 2026-06-10)
Marqués `"soon": True` dans `capabilities.py` → **retirés** de « Composez votre vendeur », de la page de vente et des forfaits (filtrés dans `capabilities_context` ; exclus activation/auto-assignation/gating). Plus de badge « Bientôt » affiché. Flag conservé pour le futur :
- **Messenger + Instagram** (`multicanal`) → dépend de l'App Review Meta. Voir [[canaux]].
- **Acquisition réseaux / comment-to-DM** → App Review + setup page.
- **Email pro + réponses auto** → boîte email par boutique, dormante.
- **Prospection** → sourcing OSM sans emails. Voir [[prospection]].

**Principe** (honnêteté) : on n'affiche « actif » que ce qui marche vraiment ; le reste = « Bientôt ». Quand une capacité devient réelle → retirer `soon` dans `capabilities.py` (+ allumer le flux).

Lié : [[tarifs]], [[garde-fous]].
