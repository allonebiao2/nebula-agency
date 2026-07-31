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

## La force de vente (depuis le 2026-07-30)

NEBULA ne vend plus seule : un **programme de partenaires commissionnés** est outillé de
bout en bout. Le partenaire **vend et rapporte le brief**, NEBULA produit tout.

- **L'escalier** : Catalogue 50 000 F (porte d'entrée) → Vitrine 150 000 F (crédibilité)
  → Outil métier 55 000 à 500 000 F (contrôle). On ne saute jamais une marche.
- **Le Diagnostic Digital**, offert avec sa valeur affichée (25 000 F), est la porte
  d'entrée de l'Outil métier. Le partenaire collecte avec une fiche, Mongazi restitue.
- **Le récurrent** (25 % de chaque abonnement, à vie) est ce qui retient un bon vendeur.
  Il est tracé par la table `subscriptions` de l'app partenaires.
- Tout est consigné dans `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`.

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
| **Reprendre une session** | **`_memoire/REPRENDRE-ICI.md`** |
| Règles & vue d'ensemble | `CLAUDE.md` |
| **Prix, commissions, règles de vente** | **`_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`** |
| Guides de vente des partenaires | `_documents/nebula-agency/vente/` |
| Prompts des posts informatifs | `_documents/nebula-agency/marketing/` |
| Décisions structurantes | `_memoire/decisions.md` |
| Leçons apprises | `_memoire/lecons.md` |
| Stack technique | `_memoire/stack.md` |
| Historique clients | `_memoire/clients-historique.md` |
| Prompts efficaces | `_memoire/prompts-efficaces.md` |
| Vocabulaire | `_memoire/vocabulaire-metier.md` |
| Templates projet | `_templates/` |
| Connaissances spécialisées | `_knowledge/` |
