# FORMULAIRE CLIENT & QUESTIONS DE CADRAGE

## 1. Le formulaire (entrée du skill)
Le formulaire `nebula-agency.online` fournit (exemple Saeir Thiam) :
- **Contact** : Nom, WhatsApp, Marque, Secteur, Ville
- **Projet** : Service demandé (souvent « Plusieurs services / besoin de conseils » → à clarifier), Couleurs, Logo (oui/à envoyer WA), Délai
- **Options cochées** : Boutons WhatsApp · Galerie photos · Musique d'ambiance · Affiche PDF A4 · Google Maps · Section avis
- **Description** : activité + slogan

> Le skill **parse** ces champs et en déduit un maximum **sans** reposer de questions inutiles.
> Un brief additionnel (vocal/texte) peut **redéfinir l'ampleur** (ex : groupe multi-pôles).

## 2. Ce que SEUL le client peut fournir (à demander sur WhatsApp, en parallèle)
- Logo (idéalement 2 versions : claire/sombre, fond transparent)
- Photos produits/réalisations (par catégorie)
- **Adresse exacte + lien Google Maps**
- Avis clients réels + horaires
- Réseaux sociaux (Instagram / TikTok / Facebook…)
- **Confirmer le n° WhatsApp** avant câblage (règle absolue)
- Musique d'ambiance (piste libre de droits) — sinon pad synthétisé par défaut

## 3. Questions de cadrage au décideur (Mongazi) — AskUserQuestion
**Max 3-4 questions, recommandation en 1ʳᵉ position.** Modèles validés sur Djambar Team :

| Thème | Question | Options (déf. = 1ʳᵉ) |
|---|---|---|
| **Architecture** | Comment structurer le site ? | **Hub multi-pages (Recommandé)** / Page unique à ancres / Catalogue produits |
| **Périmètre** | Que faire des pôles/secteurs futurs ? | **Pages « Bientôt » élégantes (Recommandé)** / Juste mentionnés / Pages complètes maintenant |
| **Direction visuelle** | Quel style ? (dans la palette client) | **Luxe éditorial + verre léger (Recommandé)** / Effets intenses / Minimaliste |
| **Démarrage** | Démarrer maintenant ou attendre les assets ? | **Maintenant, placeholders pro (Recommandé)** / Attendre les vrais assets |
| **Mise en ligne** | Sous-domaine ? (si pas de domaine final) | proposer `marque.nebula-agency.online` ; sinon `*.pages.dev` provisoire |
| **Sauvegarde** | Commit + push ? | Oui commit+push / Oui commit seul / Pas encore |

## 4. Valeurs par défaut (si le client ne précise pas)
- **Service flou** → proposer le conseil (Vitrine vs Catalogue) et trancher avec le décideur.
- **Couleurs absentes** → palette grounded via `/ui-ux-pro-max`, cohérente avec le secteur.
- **Pas de logo** → wordmark typographique provisoire « à remplacer ».
- **Pas de photos** → motifs SVG / visuels libres de droits « à valider », remplacés ensuite.
- **Avis absents** → 3 exemples **marqués « à valider »** (jamais inventer de faux clients réels nommés sans le dire).
- **Délai « urgent »** → démarrage immédiat, placeholders pro, itération.

## 5. Détection d'ampleur (important)
Avant de coder, vérifier si le brief implique :
- une **marque ombrelle / groupe** (→ hub multi-pages, nom du groupe en tête) ;
- une **évolutivité** demandée (→ socle partagé, pages « Bientôt ») ;
- une **stratégie d'audience** (réseaux/événementiel qui ramènent au site).
