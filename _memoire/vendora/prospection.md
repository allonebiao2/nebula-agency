# Prospection — statut : « Bientôt » ⏳

## Comment c'est codé (`core/prospecting.py`)
1. **Sourcing** : OpenStreetMap (API Overpass), entreprises par catégorie + ville, **seulement celles avec email public**.
2. **Rédaction** : Claude (Sonnet, `writer_model`) — email perso + règles anti-spam + lien de désinscription.
3. **Envoi** : EMAIL via Resend, depuis l'alias boutique `code@nebula-agency.online`. Réponses → back-office.
4. Tourne côté serveur (warm-up, X/jour). Jamais de WhatsApp à froid (ban). Jamais de numéros perso.

## Pourquoi « Bientôt » (vérifié 2026-06-10)
Les commerces ouest-africains ne mettent presque jamais leur email sur OSM :
- Cotonou **beauté : 0** email · **mode : 1** · **restaurant : 4/60** (~7%).
- En plus, les endpoints Overpass sont instables (403/504).
→ Le cœur de cible (beauté/mode/bijoux) n'est pas atteignable. La promesse ne tient pas → **Bientôt** (`soon` dans `capabilities.py`).

## Comment la rendre RÉELLE plus tard
1. **Meilleur sourcing** : prendre le **site web** (souvent présent sur OSM même sans email) → en extraire l'email ; viser les segments qui ONT des emails (hôtels, écoles, ONG, B2B).
2. **Mode « liste de prospects »** : trouver nom + **téléphone** + adresse (présents sur OSM) → donner une liste à contacter (appel/visite). Pas d'email requis, livrable tout de suite.

⚠️ À l'échelle : sortir du domaine partagé → **sous-domaine/domaine par client** (sinon un spammeur abîme la réputation de tous). Voir [[canaux]], [[garde-fous]].
