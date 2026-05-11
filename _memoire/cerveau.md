# Cerveau — Tout ce que Claude doit savoir

> Mémoire long-terme du projet NEBULA Agency.
> Lu en complément du `CLAUDE.md` à la racine.

---

## Le fondateur

- **Mongazi**, basé à **Cotonou, Bénin**
- Solo founder de **NEBULA Agency**
- Communication : français, ton direct, sans détour
- Vise une agence rentable, ancrée localement, projetée à l'échelle de l'Afrique de l'Ouest francophone (WAOF)

## Le positionnement NEBULA

- Vitrines digitales modernes **+ couche d'automatisation IA**
- Cible : artisans, PME, indépendants francophones d'Afrique de l'Ouest
- Différenciation : qualité agence à prix accessible + IA appliquée (SOFIA, chatbots WhatsApp, automatisations n8n)

## Workflow standard

1. Brief client (souvent via WhatsApp)
2. Création du dossier `clients/0X-nom/` à partir des templates
3. Récolte des assets dans `assets/images/`, `assets/videos/`, `assets/docs/`
4. Construction de `vitrine.html` (HTML pur, CSS inline, images base64)
5. Validation client (souvent capture d'écran via WhatsApp)
6. Déploiement (Netlify principalement)
7. Mise à jour de `_memoire/clients-historique.md` + `_memoire/decisions.md` si besoin

## Contraintes techniques majeures

- **Images en base64 uniquement** — pas de CDN tiers (les liens Google Drive cassent)
- **HTML autonome** → un seul fichier, déploiement trivial, zéro dépendance build
- **Optimiser pour réseau africain** : 3G/4G instable, Android entrée/milieu de gamme
- **WhatsApp = canal de contact principal** — les liens `wa.me/...` sont sacrés

## Règles inviolables (rappel CLAUDE.md)

1. Base64 pour les images, toujours
2. Liens WhatsApp ne se modifient JAMAIS sans confirmation explicite de Mongazi
3. Diff / aperçu obligatoire avant tout commit
4. Pas de `git push` sans validation explicite
5. Un client = un dossier dans `clients/`

## Navigation interne

| Besoin | Fichier |
|---|---|
| Règles & vue d'ensemble | `CLAUDE.md` |
| Décisions structurantes | `_memoire/decisions.md` |
| Leçons apprises | `_memoire/lecons.md` |
| Stack technique | `_memoire/stack.md` |
| Historique clients | `_memoire/clients-historique.md` |
| Prompts efficaces | `_memoire/prompts-efficaces.md` |
| Vocabulaire | `_memoire/vocabulaire-metier.md` |
| Templates projet | `_templates/` |
| Connaissances spécialisées | `_knowledge/` |
