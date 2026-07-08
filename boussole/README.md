# Boussole — gestion financière du commerçant

Outil NEBULA pour **tout type de commerçant** (nourriture, produits importés, immobilier…).
Objectif : comparer précisément ce qu'on **dépense** à ce qu'on **gagne**, voir sa rentabilité,
et répartir chaque vente en **3 enveloppes**.

## Comment ça marche
1. **Configuration** (une fois) : activité + produits + TOUS leurs coûts + charges fixes mensuelles.
2. **Ventes** (au quotidien) : un clic « +1 vente » (ou saisie détaillée). Rien d'autre à faire.
3. **Bilan** : bénéfices calculés automatiquement, graphe d'évolution, **bilan trimestriel** exportable.

### Les 3 enveloppes (par mois)
| Enveloppe | Contient | Sert à |
|---|---|---|
| **Relance production** | le coût de revient des ventes | racheter la matière / le stock |
| **Charges fixes** | la marge, jusqu'à couvrir les charges du mois | payer électricité, internet… |
| **Bénéfice net** | la marge restante | mettre de côté |

Deux modèles de coûts supportés : **Transformation** (matières + emballage + main-d'œuvre)
et **Achat-revente** (prix d'achat + transport + stockage). Devise : **FCFA**.

## Stack
- **Front** : HTML/CSS/JS pur, responsive **mobile + PC**, PWA installable, **offline-first**.
- **Cloud** : **Supabase** (Postgres + Auth e-mail + Row-Level Security + synchro temps réel).
- **Hébergement** : Cloudflare Pages (dossier `boussole/`).
- Aucune dépendance de build (npm). Supabase est vendorisé dans `assets/js/vendor/`.

### Deux modes
- **Sans compte = Mode local** : données dans le navigateur (localStorage), privé à l'appareil, marche hors-ligne.
- **Avec compte = Cloud** : synchronisé mobile ↔ PC. Se configure via `assets/js/config.js`.

## Mise en route du cloud (5 étapes)
1. Créer un projet gratuit sur [supabase.com](https://supabase.com) (aucune carte bancaire).
2. **SQL Editor** → coller le contenu de `schema.sql` → **Run**.
3. **Project Settings → API** : copier `Project URL` et la clé `anon public`.
4. Les coller dans `assets/js/config.js` (`SUPABASE_URL`, `SUPABASE_ANON_KEY`).
5. (Auth → Providers → Email est activé par défaut. Pour un test rapide, désactiver
   « Confirm email » dans Auth → Sign In / Providers si on ne veut pas confirmer par mail.)

## Déploiement
- Cloudflare Pages → nouveau projet → dossier racine `boussole/` (site statique, pas de build).
- Après **chaque** modif d'asset : bumper `APP_VERSION` dans `assets/js/config.js`,
  le `?v=` dans `index.html`, et `V` dans `sw.js` (cache-busting du service worker).

## Sauvegarde
Réglages → **Exporter** produit un fichier JSON ; **Importer** le restaure.
Recommandé en Mode local (les données vivent sur l'appareil).
