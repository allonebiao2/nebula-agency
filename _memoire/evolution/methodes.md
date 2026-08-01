# Méthodes — comment NEBULA travaille

> Comment l'agence travaille **aujourd'hui**, et comment cette manière de faire évolue.
> Quand une méthode change durablement, la mettre à jour ici (et logger le pourquoi dans `_memoire/decisions.md`).

---

## Méthode actuelle (v1 — 2026-05)

### Prise de brief
- Canal principal : **WhatsApp**
- Reformuler le besoin par écrit dans `CONTEXT.md` avant de coder
- Valider la reformulation avec le client avant toute production

### Production d'une vitrine
1. Copier `_templates/CONTEXT-template.md` dans le dossier client
2. Collecter les assets dans `assets/images/`, `assets/videos/`, `assets/docs/`
3. Encoder les images en **base64** (jamais de lien externe)
   - **Photos produits** : normaliser sur canvas blanc 600×800 (3:4) JPEG q78
     pour une grille visuellement cohérente — voir `lecons.md` 2026-05-24.
   - Pas de détourage automatique : les fonds blancs studio sont un atout.
4. Construire `vitrine.html` : HTML pur + CSS inline + JS vanilla si nécessaire
5. Tester sur mobile réel **iPhone ET Android** (pas seulement émulation desktop) :
   - Audio (musique + SFX) — voir `lecons.md` 2026-05-25
   - Touch targets ≥ 44px
   - Performance sur réseau 4G africain
6. Dérouler `_templates/checklist-livraison.md`
7. Envoyer preview au client (URL Netlify staging ou capture)
8. **Aucun push sans validation explicite de Mongazi**

### Automatisation IA
- n8n self-hosted (Hostinger VPS `72.61.103.56`)
- Conventions de nommage et structure : voir `_knowledge/n8n-workflows.md`
- LLM : Groq (vitesse) en premier, fallback Claude (qualité) si besoin

### Versioning
- Git local pour chaque modification
- Diff montré à Mongazi avant chaque commit
- Push GitHub `allonebiao2` uniquement après validation
- **Un seul fichier versionné actif à la fois** (depuis 2026-05-14)
  - À chaque mise à jour d'un `nebula_agency_vX.html` (ou autre fichier versionné), supprimer l'ancien via `git rm` avant de créer le nouveau
  - L'historique git garde la trace des versions précédentes — pas besoin d'accumuler les fichiers
  - Voir `_memoire/decisions.md` (2026-05-14) pour le détail

### Paiement intégré dans les vitrines (depuis 2026-05-14)
- **FedaPay** comme provider standard (Mobile Money Moov, MTN, Wave + cartes)
- Clés API stockées **uniquement dans `.env` local** (jamais commitées)
- Clé publique `pk_live_*` : côté client (HTML/JS de la vitrine)
- Clé secrète `sk_live_*` : côté serveur uniquement (n8n, webhooks)
- Sous-comptes clients via "+ Ajouter un compte" dans le dashboard FedaPay
- Notifications paiement triple : WhatsApp (bouton confirmation) + MyFeda (app) + Email natif

### Propagation d'impact : info de site → supports dérivés (depuis 2026-07-13)
- Toute **mise à jour d'info sur un site** (lien/URL, domaine, téléphone, prix, nom de marque, adresse) doit être **répercutée partout où l'info est présente**, y compris les **supports dérivés** : affiches, cartes de visite, QR (PDF/PNG), kits imprimés, images OG.
- Un **changement de lien/domaine** (ex. migration Netlify vers domaine final) déclenche d'office la **revue de tous les QR/liens** imprimés et en ligne.
- Si la propagation n'est pas appliquée d'office : **lister les endroits concernés et DEMANDER à Mongazi « je mets aussi à jour ici et là ? »**, puis attendre sa confirmation (oui/non). Ne jamais laisser un support avec une info périmée en silence.
- Déclencheur : la bascule Luxury Skin Clinic vers `luxuryclub229.com` (12/07) a laissé le QR de la carte + de l'affiche pointer vers l'ancien Netlify jusqu'à ce que Mongazi le signale (2026-07-13).

---

### QC par suites cumulatives + sweep multi-viewport (depuis 2026-07-25, produits logiciels)

Pour un **outil** (pas une vitrine), la relecture de code et les captures ne suffisent plus.
Méthode appliquée sur Boussole, à reprendre pour les prochains SaaS verticaux :

1. **Une suite QC Playwright par vague** (`qc_v4` = données/métier, `qc_v5` = caisse/coûts,
   `qc_v6` = transitions, `qc_v7` = accueil, `qc_v8` = textes/sons, `qc_v9` = sweep UI).
2. **On ne remplace jamais une suite : on l'ajoute.** À chaque nouvelle vague, **toutes** les
   suites précédentes sont rejouées → la non-régression est prouvée, pas supposée.
3. **Sweep d'interface obligatoire** : chaque écran × **mobile 390 px** ET **PC 1280 px** →
   débordement horizontal nul, boutons flottants dans le viewport, feuilles cadrées avec
   leur bouton d'action visible.
4. **Zéro erreur console** est un critère de sortie, au même titre que les assertions.
5. `node --check` du module inline après chaque édition (le fichier est un mono-HTML).
6. Rien n'est déployé tant qu'une seule suite est rouge.

Bilan de la journée du 2026-07-25 : **113 vérifications** cumulées, 2 bugs bloquants trouvés
par le sweep que personne n'avait vus à l'œil.

## 2026-08-01 — La beauté devient un critère de sortie, au même titre que le QC

Jusqu'ici, « fini » voulait dire : toutes les vérifications passent. Depuis le 2026-08-01,
**« fini » veut dire deux choses à la fois** — les vérifications passent **et** le résultat
impressionne. Une vitrine techniquement irréprochable peut être jugée « à 100 $ », et
c'est arrivé.

Ce qui change concrètement dans la façon de travailler :

1. **On écrit la phrase avant le CSS.** Une ligne qui dit ce qu'est le métier vu de
   l'intérieur, avec un objet concret dedans. Elle décide de la typo, du rythme des fonds
   et de toutes les animations. C'est la nouvelle PHASE 1.0 de la procédure vitrine.
2. **On regarde les captures, section par section.** Le QC automatique ne remplace pas
   l'œil : six défauts réels sont passés au travers de 53 contrôles verts. La QA visuelle
   n'est plus un bonus, c'est une étape obligatoire avant de dire « fini ».
3. **On sépare la source du livrable** dès qu'une image en base64 entre dans un fichier :
   `_vitrine_src.html` → `_build.py` → `vitrine.html` généré. Gabarits partagés.
4. **Le QC hérite des leçons de perf.** La règle « aucune animation infinie sous un
   `backdrop-filter` » n'est plus une consigne qu'on peut oublier : c'est un test.

Manuel : `_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`.

## Choses qu'on essaie / qu'on teste

> _vide pour le moment._
> Quand une nouvelle méthode est testée, la noter ici avec **date de début** et **critère de réussite**.

---

## Méthodes abandonnées (et pourquoi)

> _vide pour le moment._
> Quand une méthode est retirée, la déplacer ici avec **date d'arrêt** et **raison**.
