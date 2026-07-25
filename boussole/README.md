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


---

# Proto v4 « verre de nuit » — l'app en cours de construction

> Le développement actif se fait dans **`_proto/app.html`** (+ `_proto/connexion.html`).
> L'app de la racine (ci-dessus) est la version en production, **pas encore migrée**.
> Preview : https://proto.boussole-19d.pages.dev/_proto/connexion

## Ce que le proto sait faire en plus

### Démarrage
- **Onboarding 4 pas** : prénom → nom du commerce + activité → objectif du jour → **« mes vraies données » (zéro) ou « explorer la démo »**.
- Plus **aucune donnée d'exemple imposée** : le mode démo est explicite (chip « Mode démo ») et se quitte depuis Réglages.

### Écran Réglages
Identité du commerce (nom, tél., adresse, **IFU / RCCM** → repris sur les factures), **code patron**, webhook IA, **export / import JSON**, effacement, état du cloud.

### Métier
| Fonction | Détail |
|---|---|
| **Caisse** | tuiles produits 3D, entrée « coffre qui s'ouvre », panier, 3 modes de paiement |
| **Vente à crédit** | oblige à choisir un client → **la dette s'inscrit automatiquement** sur sa fiche (et se solde / s'ajuste si la vente est modifiée ou supprimée) |
| **Coût de revient** | capturé à chaque vente ; **décomposable en postes nommés** (ex. vitrine + QR : Partenaire 10 000 F, Hébergement 5 000 F) avec **% du prix calculés tout seuls** |
| **« À réserver »** | le détail d'une vente affiche qui prend quoi, le total à réserver et **ce qui te reste vraiment** |
| **Les 3 enveloppes** | affichées dans le Bilan, calculées sur le mois (relance production / charges / bénéfice net) |
| **Ventes & dépenses** | modification complète, suppression **annulable**, recherche live, pagination |
| **Objectifs** | objectifs jour/semaine/mois + projets d'achat modifiables et supprimables |
| **Équipe** | « qui tient la caisse » (avatar du header), **chaque vente est signée du vendeur**, codes **hachés**, **verrous par rôle** (un vendeur ne voit ni bilan ni bénéfice) |
| **Factures / devis** | à l'identité du commerce (IFU/RC), statut cliquable brouillon → envoyé → payé |

### L'IA Boussole
- **Alertes proactives** (pastille rouge sur l'onglet) : ruptures, objectif en retard, dettes qui traînent, charges non couvertes, séries réussies.
- **Chat** : questions libres avec réponses chiffrées **calculées en local** (marche hors-ligne) ; webhook n8n/Claude **optionnel** (Réglages) pour les questions ouvertes.
- **Salutation d'accueil** : 3 voix (avis honnêtes sur les vrais chiffres / leçons d'argent / questions qui font réfléchir), **sans jamais se répéter** (historique `SM.greetHist`).

### Sensations
- **Une transition par lieu** : coffre (caisse), ticket qui s'imprime (ventes), portefeuille (dépenses), flèche dans la cible (objectifs), aiguille qui se calibre (Boussole).
- **15 animations de touché** différentes selon le type d'élément + signatures des boutons Vendre (pièces d'or + vrai prix) et Dépenser (billets + vraie sortie).
- **Confettis** au franchissement de l'objectif du jour (1×/jour) et **flamme de série** sur l'accueil.
- **Son 100 % synthétisé** (aucun fichier) : carillon doré à l'encaissement, tintement de pièce, arpège de validation, bus d'écho commun.
- ⚡ Les transitions jouent **en plein format une fois par session**, puis l'app va droit au but (le coffre passe en mode éclair).

## Synchronisation cloud du proto
L'état complet suit le compte (mobile ↔ PC) via la table **`boussole_proto_etat`** (jsonb + RLS).
**À faire une fois** : exécuter `_proto/etat.sql` dans Supabase → SQL Editor. Sans ça, l'app reste en mode local (statut affiché dans Réglages).

## Règles de développement du proto
1. Éditer via **script Python/Node en UTF-8** (jamais PowerShell : mojibake).
2. `node --check` du module inline après chaque vague.
3. Lancer **toutes** les suites QC Playwright (`qc_v4` → `qc_v9`) : elles doivent être vertes.
4. Ne jamais poser de `transform` sur un écran qui contient un `position: fixed` (le bouton flottant sortirait de l'écran) — animer un conteneur interne.
5. Pas d'animation infinie sous un `backdrop-filter` (latence).
