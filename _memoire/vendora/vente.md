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

## Super-vendeur (renfort 2026-06-12)
Les agents ne se contentent pas de répondre : ce sont des **SUPER-VENDEURS**. Inscrit dans le prompt (`core/brain.py`, section « Tu es un SUPER-VENDEUR ») :
- **ANALYSER chaque client** avant de répondre : besoin réel, budget probable, niveau d'envie, freins (prix/confiance/livraison), pressé ou hésitant → adapter l'approche à CE client.
- **POUSSER vers l'objectif** : conclure la vente (ou l'objectif visé : commande, RDV, paiement), guider étape par étape jusqu'à l'achat — avec finesse, jamais lourdement.

## Appels (voir [[canaux]])
L'agent gère les **messages**, pas la voix : pour un appel, il oriente le client vers le **numéro du commerçant**, puis continue la vente par message.

## Multi-canal (même cerveau)
Le même `_agent_handle` sert WhatsApp / Messenger / IG / email (canal-agnostique). Voir [[canaux]].

## Back-office commerçant
Le commerçant règle tout dans son espace (`web/templates/boutique.html`), réorganisé **WhatsApp-first** + super-guide pas-à-pas (2026-06). Chaque réglage est appliqué tout de suite.
