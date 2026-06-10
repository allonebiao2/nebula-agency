# Apprentissage & intelligence

Vendora apprend pour vendre mieux. Tout est **premium/Empire** et la plupart **dormant** tant que peu de boutiques.

## Briques (code)
- **Leçons de vente** (`core/learning.py`) : analyse les conversations (Sonnet) → extrait des leçons concrètes (accroches qui marchent, objections, etc.), réinjectées dans le prompt du vendeur.
- **Intelligence collective** : benchmark anonymisé entre boutiques d'un même secteur. Dormant tant que < 3 boutiques/secteur.
- **Auto-amélioration** : l'agent tire des leçons globales et ajuste.
- **Auto-expérimentation (A/B)** (`core/experiment.py`) : teste des variantes d'accroche/réponse et garde ce qui convertit.
- **Cerveau CEO / stratège** (`core/strategist.py`) : propose des décisions (prix, modèle, rétention…), Mongazi valide, exécution. Raisonne avec **Opus**. OFF par défaut (coûteux).
- **Coach commercial** (`core/coach.py`) : conseils chiffrés par boutique, hebdo.

## Règle
Apprentissage = within garde-fous, propose → Mongazi valide. Voir [[garde-fous]], [[modeles]].
