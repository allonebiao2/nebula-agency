# WhatsApp — conformité & passage à l'échelle (checklist opérationnelle)

> Complète les corrections 🔴 B (données) et 🔴 C (opt-in/templates) de
> `_audit/analyse-vendora-produit-2026-06.md`. Ici = ce qui se règle **côté Meta**
> (pas dans le code). À faire dans l'ordre quand on vise les 1ers clients payants → l'échelle.

## Ce qui est DÉJÀ fait dans le code (2026-06-12)
- ✅ Droit à l'effacement client (« supprime mes données ») + anonymisation des commandes.
- ✅ Opt-in marketing capturé (`bia_optin`) + STOP (`bia_optouts`) — base prête pour les diffusions.
- ✅ Page `/confidentialite` : APDP, responsable/sous-traitant (DPA), rétention, droits.
- ✅ Intelligence Vendora (leçons anonymisées) conservée même après départ/effacement client.

## À faire côté Meta (opérationnel) — dans l'ordre

### 1. Business Verification (lève le plafond 250/jour)
- Vérifier l'entreprise NEBULA dans **Meta Business Manager** (documents légaux).
- Sans ça : 250 contacts/24 h max, pas de montée en gamme. Après : 1 000 → 10 000 → illimité (selon qualité).

### 2. Compte officiel / nom d'affichage
- Demander la vérification du **nom d'affichage** WhatsApp (et, à terme, le badge officiel).
- Effet : confiance du client final + signal de qualité.

### 3. Templates de messages (pour le ré-engagement HORS fenêtre 24 h)
- Les réponses dans les 24 h après un message du client = **gratuites** (déjà OK, c'est le flux actuel).
- Pour relancer/diffuser APRÈS 24 h → **templates pré-approuvés** par Meta (catégories : utility / marketing).
- Préparer 4-5 templates types : confirmation de commande, rappel de paiement, nouveauté/promo (marketing), info de livraison (utility).
- Coût : au message livré (marketing payant ; utility moins cher ; service/réponse 24 h gratuit).

### 4. Opt-in (consentement) avant toute diffusion
- Ne JAMAIS envoyer de marketing sans opt-in (déjà capturé par `definir_preference_promos`).
- Afficher la source de l'opt-in (ex : « le client a accepté dans la conversation »).

### 5. Tech Provider + Embedded Signup (= le moat, avant de scaler) — point 🔴 A de l'audit
- S'enrôler comme **Meta Tech Provider** (obligatoire pour les ISV depuis le 30/06/2025).
- Intégrer l'**Embedded Signup** : chaque boutique connecte **SON propre numéro** (~5 min), brandé à son nom, qualité isolée.
- Remplace le « numéro partagé » actuel (OK pour le pilote, plafond de verre à l'échelle).

## Décisions produit liées
- Diffusions à la base clients = **forfait Business/Empire** (à activer quand 1-3 et 5 sont prêts).
- Tant que templates/Embedded Signup pas faits → relances **uniquement dans la fenêtre 24 h** (déjà le cas, `core/followup.py`).
