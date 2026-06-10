# Capacités (skills) de l'agent

« Composez votre vendeur » : le commerçant coche ce que son agent sait faire.
**Source de vérité = `boutique-ia/core/capabilities.py`** (gating réel partout).

3 couches : 🟢 socle (toujours actif) · 🔵 modules (à la carte, plafond par forfait) · 🟣 super-pouvoirs (Empire).

## Actifs (live, marchent sur WhatsApp)
- Socle : vend sur WhatsApp 24h/24, conseille, alerte le patron, **vocal**.
- Modules : photos produits, paiement à la livraison, négociation encadrée, relances auto, prise de RDV.
- Premium : apprentissage perso, images de marque (Pillow), coach commercial, réseaux sociaux (rédige + planifie ; publication 1-clic manuelle).

## Masqués de l'UI — on ne montre QUE le concret (décidé 2026-06-10)
Marqués `"soon": True` dans `capabilities.py` → **retirés** de « Composez votre vendeur », de la page de vente et des forfaits (filtrés dans `capabilities_context` ; exclus activation/auto-assignation/gating). Plus de badge « Bientôt » affiché. Flag conservé pour le futur :
- **Messenger + Instagram** (`multicanal`) → dépend de l'App Review Meta. Voir [[canaux]].
- **Acquisition réseaux / comment-to-DM** → App Review + setup page.
- **Email pro + réponses auto** → boîte email par boutique, dormante.
- **Prospection** → sourcing OSM sans emails. Voir [[prospection]].

**Principe** (honnêteté) : on n'affiche « actif » que ce qui marche vraiment ; le reste = « Bientôt ». Quand une capacité devient réelle → retirer `soon` dans `capabilities.py` (+ allumer le flux).

Lié : [[tarifs]], [[garde-fous]].
