# Au Braisé d'Or · passe SEO et GEO publiée (2026-09-24)

Écrite le 2026-09-18 (Mongazi : « que la vitrine sorte en premier quand on cherche restaurant,
restaurant Bénin… »), restée non commitée et non publiée. Construite, contrôlée et mise en ligne
le 2026-09-24.

## Ce qui est en ligne sur aubraisedor.com
- **14 pages** : accueil, `/carte/`, **9 rubriques** `/carte/<rubrique>/`, `/traiteur-et-place-des-fetes/`,
  `/commander/`, `/contact/`, plus une **vraie 404** (`noindex`, sans canonique héritée).
- L'accueil a enfin **un H1** (le premier titre était « SAUCEGOMBO », un nom de plat du carrousel).
- `sitemap.xml` généré par `app/sitemap.ts` (l'ancien fichier statique est supprimé), `robots.txt` enrichi.
- `/llms.txt` et `/carte.md` générés depuis les données (routes Next), jamais recopiés.
- Coordonnées rassemblées dans `experience/data/maison.ts` (le JSON-LD les lit, valeur inchangée).
- **IndexNow** : clé publiée (`c2f892be….txt`), les 14 adresses soumises, réponse **202**.

## Contrôles
`_qc_seo.py` **126** (nouveau) · `_qc_pages.py` **88** (nouveau, navigateur 390/1440 : débordement,
H1 au premier écran, erreurs JS) · `_qc_partage.py` **38** · `_qc.py` **117**. Captures 390 regardées.

## Ce qui reste
- ⛔ **Le numéro** : les 171 liens `wa.me` servis sont `22956057157` (sans `01`), le JSON-LD dit
  `+2290156057157`. Rien touché, Mongazi tranche.
- Fiche Google Business, Search Console, adresse exacte : ne se font pas d'ici, et pèsent le plus.
