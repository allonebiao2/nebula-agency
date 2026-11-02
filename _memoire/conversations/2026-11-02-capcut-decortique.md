# 2026-11-02 · CapCut décortiqué

## La demande

Mongazi : « ce que moi je me vois créer actuellement c'est CapCut et n8n, on va commencer par CapCut ». Il
demande d'invoquer REA, de prendre le contrôle du PC, de chercher CapCut et de le décortiquer de A à Z, version PC
et mobile.

## Ce qui a été fait

1. CapCut localisé : `%LOCALAPPDATA%\CapCut\Apps\6.6.1.2640` (17 juillet 2025, 1,7 Go, Qt 6 + CEF + Lynx).
2. REA `inspect_desktop_application` sur le dossier : **zéro candidat** (il ne connaît pas Qt). Ses outils de
   pilotage d'interface (`observe_native_ui`, `capture_native_ui_scenario`) ne visent que les applications Mac.
3. Lecture des DLL (architecture) et du fichier `Resources/po/fr-FR.po` (13 143 libellés, regroupés par préfixe
   d'identifiant en 194 modules).
4. Croisement avec capcut.com, l'App Store, Wikipédia, l'aide CapCut, et un blog 2026 (marqué « tiers »).
5. Page publiée, fiche `_knowledge/capcut-decortique.md`.

## Décisions et limites

- **CapCut pas lancé** : la démo ORB tournait (MT5 ouvert, 1,4 Go libre). Une visite de l'interface en direct
  est possible **après 21 h**, ou un week-end, et plutôt sur une version à jour (la 6.6.1 a 15 mois de retard).
- **Aucun code décompilé** : interdit par les conditions d'utilisation de CapCut. On lit ce qui est livré en clair.
- Recommandation : ne pas refaire CapCut en généraliste ; viser la vidéo tirée du catalogue réel d'un commerçant.

## Suite

n8n, le second outil que Mongazi veut créer.

## Suite : le payant, puis LA BOBINE

- Mongazi demande tout le payant de CapCut : relevé dans les 473 libellés « argent », confirmé par l'aide
  officielle (le verrou est à l'export).
- Mongazi : « crée exactement CapCut avec toutes les options payantes, on va renommer ». Réponse : les familles de
  fonctions et le modèle payant, oui ; le code, les écrans, les effets et les ressources de CapCut, non (contrefaçon).
  Par vagues. Décisions de Mongazi : **version web** (PC + téléphone), nom **LA BOBINE**.
- Vague 1 construite et testée (33 verts). Publication refusée par le garde-fou, en attente de Mongazi.
- Suite : vague 2 (montage avancé), puis n8n.
