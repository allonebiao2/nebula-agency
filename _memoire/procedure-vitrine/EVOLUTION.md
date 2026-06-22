# JOURNAL D'ÉVOLUTION — procédure vitrine/catalogue

> Log **vivant**. Ajouter une entrée datée à chaque décision, apprentissage ou ajustement de méthode,
> jusqu'à ce que le skill soit créé (puis continuer à le faire évoluer).

---

## 2026-06-22 — Exécution de référence : Djambar Team / Saeir Thiam Bijouterie (#05)

### Contexte
Première exécution complète, end-to-end, qui sert de **gold standard** pour le futur skill.

### Décisions & apprentissages
- **Analyse du brief > formulaire** : la fiche disait « bijouterie » mais le brief révélait un **GROUPE Djambar Team** (la bijouterie est la locomotive). → architecture **hub multi-pages évolutif**, nom du **groupe** en tête, pôle = **Saeir Thiam Bijouterie**. **Leçon** : toujours analyser l'ampleur avant de coder.
- **`/ui-ux-pro-max` à écraser** : il proposait rose/or + liquid glass ; on a imposé **bleu nuit/blanc** (client) + verre **léger** (perf 4G). On a **gardé** sa reco typo de base puis ajusté.
- **Police** : Montserrat signalé « sur-utilisé » par `impeccable` → remplacé par **Jost** (plus de caractère, pairing luxe avec Cormorant). **Leçon** : écouter `overused-font`, classer `single-font` en faux positif (CSS partagé).
- **Images relatives, pas base64** : choix assumé pour un hub multi-pages (perf + évolutivité). La règle base64 vaut pour le mono-fichier.
- **Pipeline Pillow** (`_build_assets.py`) : détourage logo → marque arbre seule pour la nav + favicon + OG sociales ; 24 photos optimisées (3 catégories) ; watermarks client **conservés**.
- **QA mesurée** : capture Edge + page diag `--dump-dom` → **`over=0`** (0 débordement mobile). Le « cut » perçu sur les captures était un artefact de downscale d'aperçu, **pas** un bug réel. **Leçon** : mesurer, ne pas deviner.
- **Affiche PDF** : QR vers **WhatsApp + Maps** (stables), **pas** l'URL provisoire (le client prendra `djambarteam.com`). **Leçon** : sur l'imprimé, jamais d'URL périssable.
- **Déploiement** : `wrangler pages deploy` → **`*.pages.dev` live immédiat** sans DNS. Domaine custom = étape ultérieure (DNS). **Leçon** : livrer une URL live tout de suite, mapper le domaine après.
- **Réseaux sociaux** reçus après coup → câblés dans les 4 footers + ligne « Suivez-nous » de l'affiche → **redeploy**. **Leçon** : prévoir des emplacements réseaux dès le départ (placeholders), faciles à remplir.

### Outils nouveaux ajoutés à la boîte
- `segno` (QR), `uipro-cli`/`ui-ux-pro-max` (design system), Edge `--dump-dom` (mesure overflow).

### État
Site **LIVE** : https://djambar-team.pages.dev · Affiche PDF générée · poussé sur `main`.
Reste (client) : avis réels + horaires ; domaine `djambarteam.com` (mapping ultérieur).

### À intégrer dans le skill (issu de cette run)
- Étape « **détection d'ampleur** » (groupe vs simple vitrine) en PHASE 0.
- Bloc **réseaux sociaux** présent par défaut (placeholders) sur toutes les pages + affiche.
- Choix QR **stable** par défaut (WhatsApp+Maps), QR site ajouté quand domaine final connu.
- Garder le **pipeline d'assets** générique (logos/OG/galerie/QR) paramétrable par dossier.

---

<!-- Prochaines entrées : ajouter ici au fil des vitrines suivantes, avant la création du skill. -->
