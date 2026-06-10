# Comment l'agent vend

Code : `core/brain.py` (cerveau du vendeur). Modèle = Sonnet (voir [[modeles]]).

## Principe
- Prompt système construit depuis la **fiche boutique** (produits, prix, livraison, paiement, ton, règles) + les **leçons** apprises ([[apprentissage]]) + les **capacités actives** ([[capacites]]).
- Réponses WhatsApp courtes (max ~500 tokens), ton réglé par le commerçant.
- Fiche mise en **cache** (cache_control) → réutilisée à chaque tour, coût réduit.

## Outils (tools) — selon capacités
- `enregistrer_commande` → notifie le patron + confirme + instructions paiement (Mobile Money / livraison).
- `alerter_le_patron` → escalade lead chaud / réclamation.
- `montrer_produit` → envoie photo (si capacité `photos`).
- `enregistrer_rendezvous` → si capacité `rdv`.

## Multi-canal (même cerveau)
Le même `_agent_handle` sert WhatsApp / Messenger / IG / email (canal-agnostique). Voir [[canaux]].

## Back-office commerçant
Le commerçant règle tout dans son espace (`web/templates/boutique.html`), réorganisé **WhatsApp-first** + super-guide pas-à-pas (2026-06). Chaque réglage est appliqué tout de suite.
