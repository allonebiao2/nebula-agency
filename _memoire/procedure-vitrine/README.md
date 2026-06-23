# 🧠 Branche cerveau — PROCÉDURE VITRINE / CATALOGUE + QR

> Branche créée le **2026-06-22** pendant la construction du site **Djambar Team / Saeir Thiam Bijouterie** (client #05).
> **But** : capturer **minutieusement** la procédure réelle qu'on utilise pour produire un
> **site vitrine + QR code** ou un **catalogue digital + QR code**, afin d'en faire **un SKILL**.

> ✅ **SKILL CONSTRUIT le 2026-06-23** : **`nebula-site`**, installé dans
> `.claude/skills/nebula-site/` (SKILL.md + `templates/` = socle gold standard
> app.css/app.js/_build_assets.py/_build_gallery_v2.py). ⚠️ `.claude/` est **gitignoré**
> (config locale machine) → la **source versionnée = cette branche** ; le texte canonique du
> skill est mirroré ici dans **`SKILL.md`**. **Réinstaller** après un clone/reset : copier
> `_memoire/procedure-vitrine/SKILL.md` → `.claude/skills/nebula-site/SKILL.md` et recopier
> les templates depuis `clients/05-saeir-thiam-bijouterie/` (`assets/app.css`, `assets/app.js`,
> `_build_assets.py`, `_build_gallery_v2.py`). **Test restant** : lancer sur un NOUVEAU formulaire
> (autre client) et comparer au gold standard Djambar Team.

## Objectif final (ce qu'on construit)
Un **skill invocable** auquel je donne **juste le formulaire rempli d'un client** et qui
**sort le produit fini** (site en ligne + affiche PDF + QR), de bout en bout, **sans s'arrêter
tant que tout n'est pas terminé** (run-to-completion autonome ; il ne s'interrompt que pour les
infos que SEUL le client possède).

## Comment lire cette branche
| Fichier | Contenu |
|---|---|
| `PROCEDURE.md` | **Le runbook maître** : toutes les phases, étapes et livrables, dans l'ordre. |
| `QUESTIONS-FORMULAIRE.md` | Le formulaire client + les questions de cadrage à poser + les valeurs par défaut. |
| `SKILLS-ET-OUTILS.md` | **TOUS les skills et outils invoqués** durant la création (versions, commandes). |
| `CONVENTIONS.md` | Les standards techniques/visuels non négociables (règles NEBULA). |
| `EVOLUTION.md` | **Journal vivant** : décisions, apprentissages, ajustements, au fur et à mesure. |
| `SPEC-SKILL.md` | La **spécification du skill** (nom, déclencheur, entrées, comportement, sorties). |
| `SKILL.md` | ✅ **Le skill construit** (copie canonique versionnée de `.claude/skills/nebula-site/SKILL.md`). |

## Règle de tenue (au fur et à mesure)
À chaque avancée sur une vitrine/catalogue **avant** que le skill existe :
1. Si une **nouvelle étape** ou un **nouvel outil** apparaît → l'ajouter dans `PROCEDURE.md` / `SKILLS-ET-OUTILS.md`.
2. Si une **décision** ou un **apprentissage** survient → l'ajouter dans `EVOLUTION.md` (daté).
3. Garder `SPEC-SKILL.md` aligné sur la réalité (c'est lui qu'on transformera en skill).

## Projet de référence (gold standard)
**Djambar Team / Saeir Thiam Bijouterie** — `clients/05-saeir-thiam-bijouterie/`.
C'est la première exécution complète documentée ici ; le skill devra reproduire ce niveau de finition.
