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

## Règle dure : JAMAIS scraper des emails persos (Gmail) à froid
Décidé 2026-06-10. Techniquement faisable, mais à proscrire :
1. **Réputation** : démarcher des persos non sollicités → plaintes spam → **blacklist du domaine partagé** → casse les emails de TOUTES les boutiques + NEBULA.
2. **Légal** : emailer des particuliers sans consentement = zone rouge (vie privée) ; Gmail punit de toute façon.
3. **Qualité** : un Gmail trouvé sur une page ≠ acheteur qualifié → conversion ~0.
4. **ToS** : scraper Google / les réseaux = contre leurs conditions (ban).

## Vérité B2C vs B2B (cadrage acquisition)
- Boutiques **B2C** (mode, cosméto, bijoux) : clients = particuliers, pas d'email trouvable → **l'email à froid ne colle pas**. Acquisition réelle = **social + comment-to-DM + bouche-à-oreille + statut WhatsApp**. Voir [[canaux]].
- L'email prospection n'a de sens que pour des clients **B2B** (services, événementiel, fournisseurs qui vendent à d'autres entreprises).

## Comment la rendre RÉELLE plus tard (2 options conformes)
1. **Scrape de sites d'entreprises → email PRO public (B2B only)** : à partir d'un site (souvent listé sur OSM/annuaires même sans email tag), crawler la page contact → extraire l'email pro **publié volontairement**. Viser les segments qui ONT des emails (hôtels, écoles, ONG, B2B).
2. **Mode « liste de prospects »** : Vendora trouve les entreprises + nom/téléphone/adresse → donne une **liste à contacter** au commerçant (WhatsApp/appel). **Zéro email à froid**, livrable tout de suite.

Garde-fous (toute option email) : cibles **entreprises** (jamais particuliers), **opt-out**, **warm-up**, volume bas, et **sous-domaine/domaine par client** à l'échelle (ne pas mutualiser la réputation). Voir [[garde-fous]].
