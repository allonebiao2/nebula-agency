# Tarifs & forfaits

Modèle : **frais d'installation + abonnement mensuel** (Mobile Money). Détails de prix = dans le code / page de vente (source de vérité `config.py` + `boutique.html` onglet Forfait).

## Logique « Composez votre vendeur »
- 3 forfaits (Démarrage / Business·Croissance / Empire) — voir libellés dans `config.PLAN_LABELS`.
- Chaque forfait = socle + un **nombre de modules** au choix (plafonds : 2 / 5 / illimité — `MODULE_LIMIT` dans `capabilities.py`).
- Super-pouvoirs = Empire.
- Capacités « Bientôt » (Messenger/IG, email, prospection) affichées mais non activables → voir [[capacites]].

## Principe de promesse
Garder les prix, **aligner les promesses sur le livrable réel** (page de vente honnête : Messenger/IG + email + prospection = « bientôt »). Essai gratuit = offre Démarrage uniquement.

Lié : [[capacites]], [[garde-fous]].
