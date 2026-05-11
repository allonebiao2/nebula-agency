# Session — Mise en place de Claude Code + structure mémoire NEBULA

- **Date** : 2026-05-11
- **Durée approx.** : ~1 session
- **Outil principal** : Claude Code (Opus 4.7) sur Windows
- **Repo** : `nebula-agency`
- **Contexte global** : Initialisation complète de la mémoire projet NEBULA pour que Claude Code puisse reprendre le contexte à chaque session.

---

## 1. Contexte

Mongazi voulait passer d'un usage ponctuel de l'IA (recopier le contexte à chaque fois) à un système où :
- Claude Code retrouve seul l'identité de l'agence, des clients, des règles.
- Les apprentissages sont **capitalisés** (techniques HTML, n8n, prompts, business).
- La structure du repo est **standardisée** pour tous les futurs clients.

## 2. Ce qui a été fait

1. Création de la structure initiale du repo `nebula-agency/` :
   - `00-nebula-agency/` (agence elle-même)
   - `clients/01-grain-esthetique/`, `02-little-sun-pearls/`, `03-wecs/` avec `CONTEXT.md` + `assets/`
   - `_memoire/` (decisions, leçons, stack)
   - `_templates/` (NOUVEAU-CLIENT, CONTEXT-template)
2. Première version du `CLAUDE.md`, puis remplacement par le contenu officiel défini par Mongazi.
3. Ajout des sous-dossiers `assets/images/`, `assets/videos/`, `assets/docs/` pour chaque client.
4. Extension de `_memoire/` avec : `cerveau.md`, `clients-historique.md`, `prompts-efficaces.md`, `vocabulaire-metier.md`.
5. Création de `_templates/checklist-livraison.md`.
6. Création de `_knowledge/` avec : `n8n-workflows.md`, `whatsapp-business.md`, `seo-afrique.md`, `design-system.md`.
7. Mise à jour finale du `CLAUDE.md` (ajout marques AXIO IA + KARABA Finance, infra VPS, GitHub, modèle Groq).
8. Ajout des dossiers `_memoire/evolution/`, `_memoire/apprentissages/`, `_memoire/conversations/` avec leurs fichiers de base.
9. Sauvegarde en mémoire persistante Claude :
   - `user_profile.md` (identité Mongazi + 3 marques + infra)
   - `feedback_nebula_rules.md` (règles absolues NEBULA)

## 3. Décisions

- Adopter la structure de mémoire en 3 axes : `_memoire/` (long-terme NEBULA), `_knowledge/` (compétences techniques), `_templates/` (modèles répliqués pour chaque client).
- HTML existant `nebula_agency_v5_FINAL (1).html` non touché ni déplacé, en attendant validation explicite.
- Pas de création de fichiers `.html` à cette étape (vitrine.html par client, vitrine-base.html template) — seuls les `.md` sont mis en place.

→ À répercuter dans `_memoire/decisions.md`.

## 4. Livrables

- Fichiers créés (extraits) :
  - `CLAUDE.md` (version officielle finale)
  - `_memoire/cerveau.md`, `clients-historique.md`, `prompts-efficaces.md`, `vocabulaire-metier.md`
  - `_memoire/evolution/methodes.md`, `ameliorations.md`, `versions.md`
  - `_memoire/apprentissages/depuis-claude.md`, `techniques-html.md`, `techniques-n8n.md`, `techniques-ia.md`, `business.md`
  - `_memoire/conversations/README.md`, `template-session.md`, ce log
  - `_templates/checklist-livraison.md`
  - `_knowledge/n8n-workflows.md`, `whatsapp-business.md`, `seo-afrique.md`, `design-system.md`
- Commits : aucun (Mongazi commit lui-même après validation)
- Déploiements : aucun
- Prompts capitalisés : aucun (à faire dans `_memoire/prompts-efficaces.md`)

## 5. À faire ensuite

- [ ] Vérifier / ajuster le contenu des fichiers nouvellement créés
- [ ] Mongazi : faire un premier commit propre une fois validé
- [ ] Décider du sort de `nebula_agency_v5_FINAL (1).html` (renommer en `00-nebula-agency/vitrine.html` ?)
- [ ] Compléter les `CONTEXT.md` des 3 clients avec les vraies infos (Jocelyne / Cédène / Abakar, numéros WhatsApp, etc.)
- [ ] Documenter SOFIA en détail dans `_memoire/vocabulaire-metier.md` + `_knowledge/`
- [ ] Commencer à remplir `_memoire/prompts-efficaces.md` avec 2-3 prompts qui marchent déjà

## 6. À retenir

- Un `CLAUDE.md` court à la racine + des fichiers spécialisés lus à la demande = bonne séparation
- Les règles absolues (base64, WhatsApp, validation avant push) sont aussi en mémoire persistante Claude → suivies même hors de ce repo
- Les `.gitkeep` permettent de versionner les dossiers vides ; les retirer dès que de vrais fichiers entrent

→ À répercuter dans `_memoire/lecons.md` si jugé suffisamment durable.

## 7. Notes brutes

- Le fichier existant `nebula_agency_v5_FINAL (1).html` reste à la racine, intact.
- Les anciens `clients/0X/assets/.gitkeep` sont devenus redondants depuis l'ajout de `images/videos/docs/` — à supprimer plus tard si Mongazi veut nettoyer.
