# SPEC DU FUTUR SKILL — « vitrine-express » (nom provisoire)

> À **construire à la fin** de la vitrine Mr THIAM (quand validée), à partir de cette branche cerveau.
> Cible : **donner le formulaire rempli → recevoir le produit fini**, sans s'arrêter en cours de route.

## 1. Identité
- **Nom** (provisoire) : `vitrine-express` (alt : `forme-to-vitrine`, `vitrine-nebula`). À ne pas confondre avec le **projet Vitrina** (générateur SaaS) ni `studio-quotidien`.
- **Emplacement** : `.claude/skills/vitrine-express/SKILL.md` (+ assets bundlés : `_build_assets.py` template, snippets `app.css`/`app.js`).
- **Déclencheurs** (description SKILL.md) : « formulaire client », « nouvelle vitrine », « catalogue digital », « créer le site de <client> », collage d'une fiche `NOUVELLE COMMANDE — NEBULA AGENCY ».

## 2. Entrée
- **Le formulaire client rempli** (collé tel quel) + éventuel **brief additionnel** (texte/vocal).
- Optionnel : chemin d'un dossier d'assets déjà reçus (logo/photos), pré-autorisations (ex : « commit+push OK », « sous-domaine = X »).

## 3. Comportement — RUN-TO-COMPLETION (exigence clé)
> **« Il ne s'arrête pas tant que tout n'est pas fini. »**

- Exécute **PHASE 0 → 9** de `PROCEDURE.md` **d'affilée**, sans rendre la main entre les phases.
- **Donnée manquante (côté client)** → ne bloque PAS : pose un **placeholder pro « à valider »** (texte, visuel SVG/libre de droits, avis-exemples, wordmark) et **continue**. Tient une liste « À REMPLACER ».
- **Boucle d'auto-vérification** : à la fin, déroule la **checklist de pré-livraison** (§5). Tant qu'un item échoue → **corriger et re-vérifier**. Ne se déclare « fini » que lorsque **tous** les items passent **et** que le site est **déployé et accessible (200)**.
- **Autonomie décisionnelle** : tranche lui-même via les **défauts** de `QUESTIONS-FORMULAIRE.md` (architecture déduite du brief, style depuis design-system + palette client, démarrage immédiat). 
- **Points d'arrêt autorisés (rares)** :
  - actions **sortantes/irréversibles** non pré-autorisées (**push git**, **domaine custom/DNS**) → exécute le reste, **livre**, puis **demande** ces dernières actions ;
  - ambiguïté **bloquante** réelle non résolvable par défaut → **1 question** groupée, puis reprend.
- Le **déploiement `*.pages.dev`** (réversible) fait partie du run normal (pas un point d'arrêt).

## 4. Sortie (produit fini)
1. Site **multi-pages déployé** en HTTPS (`*.pages.dev`) — lien live.
2. **Affiche PDF A4** (`assets/docs/Affiche_<Marque>_A4.pdf`) avec **QR** WhatsApp + Maps.
3. Assets générés (logos détourés, favicons, OG sociales, galerie optimisée, QR).
4. **Mémoire à jour** : `CONTEXT.md`, table `CLAUDE.md`, conversation, journal, entrée `EVOLUTION.md`.
5. **Rapport final** : lien live + chemin PDF + **liste « À REMPLACER »** (assets/infos client) + étapes futures (domaine).

## 5. Checklist de pré-livraison (la boucle doit toutes les valider)
- [ ] Toutes les pages + assets répondent **200** (local et live).
- [ ] **0 débordement horizontal** (mesuré `--dump-dom`, mobile inclus).
- [ ] Liens **WhatsApp** pré-remplis OK ; numéro **confirmé** (sinon marqué « à confirmer »).
- [ ] **Google Maps + itinéraire** présents (si option/adresse connue).
- [ ] **Galerie** filtrable + lightbox fonctionnelles ; images optimisées + lazy-load.
- [ ] **Logo** intégré (nav/footer/favicon/OG) ; placeholders restants signalés.
- [ ] **Réseaux sociaux** : liens réels ou emplacements présents.
- [ ] Affiche **PDF A4** générée, sans débordement, QR stables.
- [ ] Hook **`impeccable`** traité (défauts corrigés, faux positifs classés).
- [ ] Accessibilité de base (contraste, focus, alt, labels) ; `prefers-reduced-motion`.
- [ ] **Audio baseline mobile** intégré (OFF par défaut).
- [ ] Cache-bust `?v=` à jour.
- [ ] Mémoire écrite + commit (push selon autorisation).

## 6. Orchestration interne (briques — voir `SKILLS-ET-OUTILS.md`)
`/ui-ux-pro-max` (design system) → Write socle+pages → `impeccable` (auto) → `_build_assets.py` (Pillow) → `segno` (QR) → `http.server` + **Edge headless** (QA + mesure + PDF) → `wrangler` (deploy) → `git` + mémoire.

## 7. Garde-fous (hérités des CONVENTIONS)
- Secrets jamais affichés/commités ; **stage git sélectif** ; **avertir des risques** sortants ; **vérifier avant d'affirmer** ; **réponses courtes** ; contenu manquant = version pro « à valider ».

## 8. Étapes pour créer le skill (à la fin du projet Mr THIAM)
1. Figer `PROCEDURE.md` + `CONVENTIONS.md` (stables après 1-2 vitrines de plus).
2. Convertir `PROCEDURE.md` en `SKILL.md` (instructions exécutables) + bundler `_build_assets.py` (template paramétrable) et des snippets `app.css`/`app.js` de base.
3. Rédiger la **description** SKILL.md avec les déclencheurs (§1).
4. Tester sur un **nouveau formulaire** (autre client) → comparer au gold standard Djambar Team.
5. Itérer via `EVOLUTION.md`.
