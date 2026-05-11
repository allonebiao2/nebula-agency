# Nouveau client — Checklist de démarrage

> À copier et suivre à chaque nouveau projet.

---

## 1. Création du dossier

- [ ] Choisir un numéro d'ordre : `0X` (suite à l'ordre chronologique)
- [ ] Créer le dossier `clients/0X-nom-client/` (slug en kebab-case, sans accent)
- [ ] Y créer :
  - [ ] `vitrine.html` (à partir de `_templates/vitrine-base.html`)
  - [ ] `CONTEXT.md` (à partir de `_templates/CONTEXT-template.md`)
  - [ ] `assets/` (vide au départ)

## 2. Brief client

- [ ] Remplir `CONTEXT.md` :
  - [ ] Identité du client + secteur + cible
  - [ ] Brief : besoin exprimé, objectifs, pages attendues
  - [ ] Ton et univers visuel
  - [ ] Contenu fourni vs à produire
  - [ ] Deadline et budget
- [ ] Valider le brief avec le client par écrit

## 3. Direction artistique

- [ ] Choisir palette (3-5 couleurs max)
- [ ] Choisir typographie (1 titre + 1 corps)
- [ ] Sélectionner ou demander les visuels
- [ ] Documenter ces choix dans `CONTEXT.md` → "Décisions importantes"

## 4. Intégration

- [ ] Structure HTML sémantique
- [ ] CSS : variables pour la palette
- [ ] Mobile-first
- [ ] Vérifier accessibilité de base (contrastes, alt sur images)

## 5. Recette

- [ ] Test responsive (mobile / tablette / desktop)
- [ ] Test navigateurs (Chrome, Firefox, Safari)
- [ ] Lighthouse > 90 mobile
- [ ] Relecture des textes
- [ ] Validation client

## 6. Livraison

- [ ] Mettre en ligne (hébergement défini avec client)
- [ ] Transmettre accès / fichiers
- [ ] Mettre à jour la table dans `README.md` ("En cours" → "Livré")
- [ ] Capitaliser dans `_memoire/lecons.md` si utile

---

## Modèle de nommage

- Dossier : `clients/0X-nom-client/`
- HTML : toujours `vitrine.html`
- Images : `assets/nom-descriptif.webp` (kebab-case)
