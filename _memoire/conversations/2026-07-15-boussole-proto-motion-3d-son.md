# 2026-07-15 — Boussole proto v2 cyberpunk : motion, HUD Accueil, sound design, 3D

Suite de la refonte **non destructive** dans `boussole/_proto/` (l'app live n'est PAS touchée). Séquence de points validés un par un par Mongazi (via /ui-ux-pro-max). Commit `64e43bc`.

## `_proto/app.html` (shell app)
- **Fond Cyber-Noir** : retrait du dégradé bleu navy → noir de jais `#0B0F19` ; header verre noir (`bg-black/.2` + blur) ; drawer charbon translucide ; voile neutre.
- **Micro-animations d'icônes au survol** (8 sections, couche additive `.navbtn__ic svg`, gated souris, reduced-motion) : respiration/sautillage/rotation/translation/pulsation/étirement/vibration/convergence.
- **Clic « Miles » générique** (pointerdown) : glitch RGB 1px + snap-scale ressort + flash néon de la couleur, ≤ 200 ms ; fermeture du menu repoussée à 220 ms pour qu'on le VOIE (bug initial : fermeture à 130 ms coupait l'anim). ⚠️ signature exclusive Accueil testée puis **annulée** à la demande.
- **Navigation HUD sèche** au clic (translation 10px + micro-zoom, cubic-bezier sans overshoot) ; **Accueil = écran par défaut** ; écrans-scaffold par section.
- **HUD de bienvenue « Smart Greeting Engine »** : Bonjour/Bonsoir + nom (défaut « Miles ») + **phrase variée** (3 catégories × 4, tirage aléatoire à chaque retour Accueil), **effet machine à écrire 50 ms/car** + curseur terminal, scanlines + glow cyan #00F0FF, glitch de réveil ; conteneur prêt-3D (perspective/preserve-3d).
- **Mastodontes VENDRE/DÉPENSER** en 3D : biseau vitré (border dégradé), **double ombre float** (sol sombre + glow coloré émis), **tilt kinetic** qui suit le curseur (rotateX/Y −5..5°, JS pointermove).
- **Profondeur du fond** : grille géométrique en fuite (perspective) + **16 poussières parallaxe** (2 couches, proches plus grosses+rapides).
- **Sound design audio-haptique** (Web Audio synthétisé, 0 fichier) : tick par lettre du typing, glitch/snap au clic, whoosh au routing, + **charge électrique au survol / chime(Vendre)/impact(Dépenser) au clic** des mastodontes ; **bouton Mute persistant** (`boussole:muted`) qui coupe tout. Compresseur maître (anti-saturation), déverrouillage iOS.

## `_proto/connexion.html`
- **Ouverture cinématique** en cascade (fond→logo→titre→formulaire, cubic-bezier .4,0,.2,1) + zoom 98→100 % + **glitch de réveil** du titre.
- **Succès de connexion** → enchaîne vers le vrai dashboard (`app.html`) après le message d'accueil (corrige le spinner infini).

## Reste
Contenu réel des écrans, puis intégration dans l'app live. Détail dans [[project-boussole-refonte]].
