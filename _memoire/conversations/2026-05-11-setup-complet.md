# Session — Setup Complet Infrastructure NEBULA
## Date : 11 Mai 2026

## Ce qu'on a fait
- Installé Claude Code terminal sur Windows (PowerShell)
- Débloqué PowerShell avec Set-ExecutionPolicy
- Cloné le repo nebula-agency en local sur le PC
- Créé la structure neuronale complète du repo
- Connecté GitHub + Claude Code + Obsidian sur le même dossier
- Premier push de 48 fichiers +1591 lignes sur GitHub main
- Ouvert le vault Obsidian sur nebula-agency

## Ce que j'ai appris
- Claude Code terminal = outil qui lit/modifie fichiers locaux
- CLAUDE.md = mémoire permanente lue à chaque session
- cd = changer de dossier dans le terminal
- git clone = télécharger un repo GitHub sur le PC
- git push = envoyer les modifications sur GitHub
- Fichier .md = texte lisible par humains et IA
- Obsidian = affiche les .md du repo de façon visuelle
- Les liens [[]] dans Obsidian créent la vue graphique
- Main = branche principale du repo
- Obsidian se met à jour automatiquement quand Claude Code modifie un fichier
- Plus de contexte = moins de tokens gaspillés en corrections

## Décisions prises
- Structure neuronale : clients/ _memoire/ _templates/ _knowledge/
- Jamais pusher sans validation de Mongazi
- Images toujours en base64, jamais Google Drive CDN
- Ne jamais modifier liens WhatsApp sans confirmation
- Logger toutes les sessions importantes dans _memoire/conversations/
- Workflow permanent : VS Code → ouvrir nebula-agency → terminal → claude

## Infrastructure mise en place
- GitHub : sauvegarde cloud + historique
- Claude Code : exécution et modifications
- Obsidian : visualisation et navigation
- CLAUDE.md : cerveau permanent
- _memoire/ : intelligence cumulative
- clients/ : un dossier par client avec CONTEXT.md + assets/
- _templates/ : modèles réutilisables
- _knowledge/ : base de connaissance technique

## Commande de lancement permanent
cd C:\Users\USER\nebula-agency && claude

## Prochaines étapes
- Remplir les CONTEXT.md de chaque client
- Ajouter les liens [[]] dans Obsidian pour la vue graphique
- Déplacer nebula_agency_v5_FINAL.html dans 00-nebula-agency/
- Remplir _memoire/cerveau.md avec tout le contexte NEBULA
- Tester le workflow complet sur une vraie modification de vitrine
