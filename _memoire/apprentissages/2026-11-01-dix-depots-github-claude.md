# Les 10 dépôts GitHub gratuits qui changent ce qu'on fait avec Claude

> Vidéo vue en entier le 2026-11-01, à la demande de Mongazi (« regarde, comprends, apprends, applique, garde en mémoire, à 100 % »).
> Fichier : `_partage/connaissance et capacité CLAUDE/10 dépôts GitHub gratuits qui explosent en ce moment.mp4` (12 min 40 s, en français, 85 Mo, hors git).
> Auteur : **Loïc Frissard**, chaîne YouTube **@DigitizFr** (Digitiz). Il est sous Claude Code v2.1.310, Opus 5.5, abonnement Claude Max.
> Méthode : transcription Whisper `large-v3-turbo` (CPU, int8) + 247 images extraites aux changements de plan, toutes lues.
> **Tout a été revérifié sur l'API GitHub le 2026-11-01** : les dix dépôts existent bien à ces adresses.

---

## Le tableau, vérifié

| # | Outil | Dépôt officiel | Étoiles (vidéo → 2026-11-01) | Licence | En une ligne |
|---|---|---|---|---|---|
| 1 | **REA** | `morluto/rea` | 379 929 → 417 281 | MIT | Claude décortique une appli installée, sans son code source |
| 2 | **Plugins officiels** | `anthropics/claude-plugins-official` | 44 405 → 45 647 | Apache-2.0 | Le catalogue de plugins géré par Anthropic |
| 3 | **HyperFrames** | `heygen-com/hyperframes` | 71 615 → 76 855 | Apache-2.0 | Claude écrit du HTML, l'outil rend un vrai MP4 |
| 4 | **VoiceStudio** | `debpalash/VoiceStudio` | 85 306 → 97 409 | AGPL-3.0 | Une alternative à ElevenLabs, entièrement locale |
| 5 | **ComfyUI** (+ son MCP) | `Comfy-Org/ComfyUI` · `Comfy-Org/comfy-mcp` | 142 713 → 144 436 · 318 | GPL-3.0 · AGPL-3.0 ou commerciale | Images et vidéos IA sur sa machine, pilotées par Claude |
| 6 | **gstack** | `garrytan/gstack` | 137 583 → 138 534 | MIT | La configuration de Garry Tan : Claude Code devient une équipe |
| 7 | **OpenCode** | `anomalyco/opencode` | 221 266 → 223 732 | MIT | Le concurrent libre de Claude Code, 75+ fournisseurs de modèles |
| 8 | **Orca** | `stablyai/orca` | 105 128 → 112 125 | MIT | Plusieurs agents côte à côte, chacun sa copie du projet |
| 9 | **Ruflo** (ex-Claude Flow) | `ruvnet/ruflo` | 79 102 → 80 477 | MIT | Une équipe d'agents qui se répartit le travail, mémoire partagée |
| 10 | **Audit de sécurité Cloudflare** | `cloudflare/security-audit-skill` | 45 174 → 55 942 | MIT | Un skill d'audit : des chasseurs de failles et des contradicteurs |

---

## 1. REA · « Reverse Engineer Anything »

- **Ce que c'est** : on prend une application **déjà installée** sur l'ordinateur et on demande à Claude **comment elle fait telle chose**. Il l'analyse **sans le code source**, explique le mécanisme, **montre les preuves** sur lesquelles il s'appuie, et peut **coder une fonction du même genre** pour notre projet.
- **Les 4 étapes (carte de la vidéo)** : une appli installée → votre question (« comment elle fait telle chose ? ») → l'analyse, sans le code source → le mécanisme, les preuves, puis une fonction du même genre.
- **À quoi ça sert** : on voit une fonction qui plaît dans un outil qu'on utilise et on veut la même chose dans son produit, sans savoir comment elle est faite.
- **Exemples publiés sur `rea.tools/showcase`** : comment l'authentificateur Aegis (APK Android) calcule le code à six chiffres qui change toutes les 30 secondes · comment Notion (Electron) garde la mise en forme d'un bloc copié (API exposée, enveloppes IPC, presse-papiers, petit marqueur HTML) · résoudre un vérificateur de drapeau de CTF (DownUnderCTF) · DX-Ball · comment TH04 (PC-98, DOS) vise un anneau de balles. Il circule aussi des copies de Photoshop sur GitHub.
- **Démonstration** : sur une appli « OpenPage.app », REA suit « Enregistrer » dans le code (`window.js`, `editor.js`, `menu.js` vers `save.js` vers `io.js`) : `saveDocument(path)` vérifie que le chemin est valide et le fichier inscriptible, **mais jamais quelle fenêtre appelle**. Le point faible à corriger.
- **Installation** (Node.js et npm) : `npx rea-agents setup`. Elle **détecte les agents** (Claude Code, Codex, Cursor, Gemini CLI, Grok Build…), **montre ce qu'elle va modifier**, demande l'accord, **garde une copie de la configuration**, ajoute le serveur MCP de REA et ses consignes. Redémarrer l'agent ensuite. **Toute l'analyse se fait sur l'ordinateur.**
- **Prompt type** : « Understand how search works in the Notes app, show me the evidence, and build a similar feature for my project. »
- **En ligne de commande** : `npx -y rea-agents@latest analyze-javascript-application /chemin/absolu/vers/app --js` (dossier JavaScript/Electron extrait, ou ASAR).
- **Prérequis** : une appli JavaScript (comme Notion) ne demande **rien d'autre** ; un programme classique demande en plus un logiciel d'analyse : **Ghidra**, gratuit.
- ⚠️ **Beaucoup de copies circulent sous des noms proches.** Le seul dépôt officiel est `github.com/morluto/rea` (site `rea.tools`).

## 2. Le catalogue officiel de plugins d'Anthropic

- **Dépôt** : `anthropics/claude-plugins-official`, « Official, Anthropic-managed directory of high quality Claude Code Plugins », doc `code.claude.com/docs/en/plugins`. Version web : `claude.com/fr-fr/plugins` (« Ajoutez de nouvelles fonctionnalités à Claude »).
- **Dans Claude Code** : la commande `/plugin` (onglets Discover · Installed · Marketplaces · Errors · Stats). Au moment de la vidéo : **3 621 plugins**, dont 3 593 dans l'Anthropic Directory et 72 dans `claude-plugins-official`. Les plus installés : Superpowers (1,1 M), code-review (477,6 K), code-simplifier (371,4 K), playwright (358,1 K), github (345,4 K), vercel (293 K), feature-dev (269,2 K).
- **Les deux qu'il utilise tout le temps** :
  - **frontend-design** : pousse Claude à faire des interfaces qui ont un vrai style au lieu du design générique qu'on reconnaît partout.
  - **skill-creator** : créer ses propres skills **et tester qu'ils marchent**.
- **Les autres cités** :
  - **code-review** : fait relire le code par plusieurs agents spécialisés.
  - **playground** : fabrique une petite page **avec des curseurs** pour régler un design ou un prompt et voir le résultat en direct. Démonstration : une « carte de chapitre YouTube » (`carte-chapitre.html`) avec préréglages (Par défaut, Rouge YouTube, Nuit minimale, Éditorial, Pastel arrondi, Jaune affiche), teinte, saturation, luminosité, opacité, taille du titre, contraste calculé, et **une consigne générée** à recopier.
  - **ralph-loop** : relance Claude **en boucle sur la même tâche** jusqu'à ce qu'elle soit vraiment terminée.
  - **Context7** (autre éditeur, présent dans le catalogue) : donne à Claude **la documentation à jour** des outils de code qu'il utilise.
  - Visibles aussi sur la page web : Superpowers, Code Simplifier, Playwright, GitHub, CLAUDE.md Management, Feature Dev, **Security Guidance** (hook qui avertit des injections de commandes et autres failles), Vercel, Claude Code Setup.
- **Pourquoi commencer là** : gratuits, et c'est Anthropic qui gère le catalogue : **l'endroit le plus sûr pour démarrer**.

## 3. HyperFrames · la vidéo fabriquée comme une page web

- **Dépôt** : `heygen-com/hyperframes`, par **HeyGen** (la société des avatars), site `hyperframes.dev`, « Write HTML. Render video. Built for agents. » Licence **Apache-2.0**. Node.js **22 ou plus**.
- **Le principe** : Claude écrit le HTML (titres, captures, animations) → HyperFrames fait le rendu **image par image** → un vrai fichier MP4. Rendu **déterministe**.
- **Son usage à lui** : il monte **toutes ses vidéos** avec : titres, cartes de chapitre, captures qui défilent. Il donne sa vidéo **face caméra**, dit à peu près où mettre un titre, une capture ou un chiffre, et la vidéo sort habillée. Au début, plusieurs allers-retours ; à force, Claude **apprend sa façon de monter**. « Plus besoin de passer par un monteur », qualité « presque aussi bien, voire mieux ». Conseil : commencer par une petite intro ou la présentation de son produit.
- **Installation pour Claude Code** : `claude plugin marketplace add heygen-com/hyperframes` puis `claude plugin install hyperframes@hyperframes`. Ou `npx hyperframes skills update` (installe exactement le jeu de base). Application de bureau **HyperFrames Studio** (macOS, Windows, Linux).
- **Les skills** : `/hyperframes:hyperframes` (à lire en premier : le contrat et les références), `-cli` (créer, vérifier, prévisualiser, rendre en local ou dans le nuage), `-registry` (**environ 450 blocs prêts** : transitions, habillages…), `figma` (amener une maquette Figma), `media-use` (musique, bruitages, images, icônes, logos, voix), **`remotion-to-hyperframes`** (convertir un code vidéo Remotion existant et le vérifier image par image).
- **Prompt de démonstration** : « `/hyperframes:hyperframes` Fais une intro de produit de 10 secondes pour Studio Lumen : le titre apparaît en fondu, la vidéo lumen.mp4 en fond, et une musique douce. Rends le MP4 dans ce dossier. »

## 4. VoiceStudio · ElevenLabs en local

- **Dépôt** : `debpalash/VoiceStudio`, licence **AGPL-3.0**. « Open-source, fully-local ElevenLabs alternative : voice cloning, voice design, video dubbing, dictation, transcription & audiobook creation in 646 languages. »
- **Ce qu'il fait** : on lui donne un enregistrement de sa voix (**5 à 15 secondes de parole propre**), il **la clone** et lit n'importe quel texte avec ; il **double une vidéo dans une autre langue** ; dictée, transcription, livres audio ; **créer une voix en la décrivant** (genre, âge, hauteur, style, accent). Rien ne part sur un serveur.
- **Ce qui le rend intéressant** : son **serveur MCP**. Claude Code le pilote : « fais la voix off de ce tutoriel » → la voix est générée sur la machine.
- **Poids réel** : son catalogue de modèles affiche « 4 des 8 modèles recommandés pour Windows x64 + CUDA installés, **16,88 Go restants** ». Pensé pour une carte graphique NVIDIA.

## 5. ComfyUI · images et vidéos IA sur sa machine

- **Dépôts** : `Comfy-Org/ComfyUI` (GPL-3.0, 140 000+ étoiles, `comfy.org`) et **`Comfy-Org/comfy-mcp`** (« Drive your own ComfyUI from Claude Code, Claude Desktop, Cursor or any MCP-speaking agent », AGPL-3.0 **ou licence commerciale**). Il existe aussi **Comfy Cloud MCP** (version hébergée).
- **Le problème** : l'interface en blocs reliés entre eux, intimidante au début. **Depuis l'été**, Comfy a son serveur MCP : Claude Code pilote ComfyUI.
- **Ce que Claude sait faire** : décrire l'image à partir d'un workflow tout prêt, lancer la génération, récupérer le résultat ; **modifier un workflow, en faire des variantes, vérifier qu'il tient avant un long rendu** ; démarrer ou arrêter ComfyUI ; **lire ses erreurs quand une génération plante** pour corriger.
- **Démonstration** : « Make me a picture of a tree using Z-Image Turbo » (gabarit `image_z_image_turbo`), puis quatre arbres de biomes avec Krea 2, puis l'un d'eux transformé en vidéo.
- **Limites (carte « Tout dépend de votre machine »)** : un Mac récent fait beaucoup mieux · la vidéo demande plus de mémoire · Comfy Cloud est payant · Nano Banana depuis ComfyUI est payant.

## 6. gstack · la configuration du patron de Y Combinator

- **Dépôt** : `garrytan/gstack` (MIT), de **Garry Tan**, patron de Y Combinator (l'incubateur d'Airbnb et de Stripe). « Use Garry Tan's exact Claude Code setup : 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA. » Sa présentation dit « One install. 28 slash commands. Claude becomes your entire team. »
- **Ce qu'il revendique** : 3 services et 40+ fonctionnalités mis en ligne en 60 jours, **à temps partiel**.
- **Les rôles** : un **CEO** qui challenge l'idée et le périmètre · un **designer** qui repère les interfaces trop génériques (et construit des systèmes de design et des variantes) · un **relecteur** (staff engineer) qui cherche les bugs avant la production · un **testeur QA** qui ouvre le site dans un vrai navigateur et clique partout · un **responsable sécurité** (OWASP + STRIDE) · un **ingénieur de mise en production**.
- **Son usage quotidien** : surtout **la navigation** (`/browse`, « fast headless browser for QA testing and site dogfooding ») : quand Claude doit lire une page web ou vérifier un site, il passe par gstack.
- **Par où commencer (ne pas tout utiliser au début)** :
  1. **`/office-hours`** : on décrit son projet, il pose **les questions qu'on poserait chez Y Combinator** (deux modes). Démonstration : « J'ai une idée d'appli : les artisans font leurs devis depuis leur téléphone, en les dictant à voix haute. »
  2. **`/qa`** : fait tester le site (`/qa http://127.0.0.1:8765 en mode Quick`). Rapport avec captures avant/après dans `.gstack/qa-reports/`, défauts numérotés (ISSUE-003…), conseil de relancer en mode Standard.
  3. **`/review`** : relire le code avant de publier.

## 7. OpenCode · l'autre catégorie

- **Dépôt** : `anomalyco/opencode` (MIT), `opencode.ai`. « The open source coding agent. »
- **Son avantage** : **75+ fournisseurs de modèles** (via AI SDK et Models.dev), des modèles bien moins chers que Claude, certains **gratuits** (Big Pickle, DeepSeek V4.1 Flash, GLM-5.3-Flash, Nemotron…), d'autres en local.
- ⛔ **Écrit noir sur blanc dans sa documentation** : « There are plugins that allow you to use your Claude Pro/Max models with OpenCode. **Anthropic explicitly prohibits this.** » Pour Claude dans OpenCode : **une clé API, payée à l'usage**. À l'inverse, ChatGPT Plus, GitHub Copilot et GitLab Duo se branchent sans rien configurer.
- **Son avis** : utile pour tester d'autres modèles ou ne pas dépendre d'un seul éditeur ; **tant qu'on a l'abonnement Claude Code, ça reste le plus simple**.

## 8. Orca · plusieurs agents côte à côte

- **Dépôt** : `stablyai/orca` (MIT), `onorca.dev`, soutenu par Y Combinator. « Run Claude Code, Codex, and any other coding agent in parallel, each in its own worktree. » macOS, Intel, **Windows**, Linux.
- **Pour qui** : quand on maîtrise bien Claude Code et qu'on veut **lancer plusieurs tâches en même temps**. **C'est nous qui donnons une tâche à chaque agent.**
- **Ce qu'il fait** : Claude Code, Codex, OpenCode (et Gemini, Cursor, Cline, Kiro…) en même temps, **chacun sur sa propre copie du projet** (worktree git), donc ils ne se marchent pas dessus ; tout dans une fenêtre (terminaux, diffs, navigateur) ; **application mobile** pour voir les agents et leur répondre ; prévient quand un agent a fini ou a besoin de nous ; on peut **annoter ses modifications**.
- ⚠️ **Le piège : le quota.** Quatre agents, ça consomme quatre fois plus vite. Orca affiche la consommation Claude et Codex et **le moment où les limites reviennent à zéro**. Utile surtout pour **les gros chantiers**.

## 9. Ruflo (ex-Claude Flow) · l'essaim d'agents

- **Dépôt** : `ruvnet/ruflo` (MIT), appelé **Claude Flow** en début d'année. « The original agent harness… multi-player swarms… adaptive memory, self-learning, federation, vector RAG. »
- **La différence avec Orca** : ici on lance **une équipe** depuis Claude Code (un agent chef, puis codeur, testeur, architecte, sécurité) et **ils se répartissent le travail entre eux**, avec **une mémoire partagée** et une console pour suivre.
- **Installation en plugin** : `/plugin marketplace add ruvnet/ruflo`, puis `/plugin install ruflo-core@ruflo` (+ `ruflo-swarm`, `ruflo-autopilot`, `ruflo-federation`, 32 plugins en tout). ⚠️ Ce chemin « léger » n'ajoute que des commandes : le serveur MCP n'est **pas** enregistré, donc `memory_store`, `swarm_init`, `agent_spawn` ne marchent pas. Chemin complet : `npx ruflo@latest init wizard` ou `npm install -g ruflo@latest`.
- ⚠️ **Le plus ambitieux, et celui qui divise** : des testeurs ont trouvé **des fonctions qui ne marchent pas comme annoncé**, et sa propre documentation prévient que **ses extensions ont les mêmes droits que votre compte**. Conseil : **d'abord sur un petit projet de test**.

## 10. L'audit de sécurité de Cloudflare · à lancer avant toute mise en ligne

- **Dépôt** : `cloudflare/security-audit-skill` (MIT). La méthode qui a servi de base à **leur propre outil de recherche de failles**, rendue gratuite. Article : « Build your own vulnerability harness », blog Cloudflare, 18 juin 2026 (Dan Jones, Alexandra Godoi, Grant Bourzikas), suite de « Project Glasswing ».
- **La vidéo le résume en 4 étapes** : cartographie de l'application → les **chasseurs** cherchent les failles, chacun de son côté → les **contradicteurs** tentent de prouver qu'elles **n'existent pas** → le rapport : **confirmé · à vérifier · écarté**.
- **Le README dit 6 phases** : reconnaissance (`architecture.md`, `coverage-ledger.json`) · chasse guidée par la couverture · validation de chaque candidat par un vérificateur neuf qui essaie de le réfuter · sortie structurée (`findings.json` validé contre `report-schema.json`) · vérification indépendante des enregistrements · rapport neutre (`REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md`).
- **Ce qu'il regarde au-delà des failles classiques** : connexion des utilisateurs, **dépendances installées**, **configuration de l'hébergement**, et les failles propres aux applis qui utilisent l'IA, comme **l'injection de prompt**. Fichiers de chasse dédiés : web et authentification, côté client, chaîne d'approvisionnement, nuage et déploiement, RPC et webhooks, épuisement des ressources, isolation des données, IA et LLM…
- **Relancé plus tard**, il **repart de ce qui a été fait** et se concentre sur ce qui n'a pas été vérifié.
- **Installation** : `npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit` (ajouter `--global` pour tout le compte). Usage : « security audit this codebase ». Sortie par défaut : `~/security-audit-skill/<dépôt>/run-<N>`, **hors du dépôt**.
- **Prérequis** : un agent qui sait lancer des sous-agents en parallèle, Node.js pour les deux validateurs (sans dépendance), et **un bac à sable imposé par le système** pour tout ce qui exécuterait le code de la cible (réseau coupé, environnement nettoyé, limites de ressources).
- **Son essai** : **15 agents, 27 minutes, 8 failles sur 8 retrouvées** (une cible de test). Démonstration : 4 agents de reconnaissance en parallèle (produit et pile · rôles et contrôles · surfaces et puits · visibilité d'exécution), puis 2 chasseurs (routes HTTP, 7 unités ; assistant IA, 3 unités), rapport de 102 lignes.
- ⚠️ **Gourmand** : il lance beaucoup d'agents en même temps. Mais « c'est le genre de vérification qu'on ne fait jamais soi-même », surtout en vibe coding, et surtout si le projet est public.

---

## Ce que la vidéo apprend au-delà des outils

1. ⛔ **Une extension a les droits de notre compte.** Ruflo le dit pour lui, mais c'est vrai de **tout** plugin, skill ou serveur MCP. Chez nous, le dossier `secrets/` (Cloudflare, Supabase, Render, WaveSpeed, FedaPay…) est lisible par tout ce qu'on installe. **On lit un plugin avant de l'installer**, comme on lit un fichier avant de le publier.
2. ⚠️ **Les copies aux noms proches** (REA) : avant tout `npx` ou `/plugin marketplace add`, vérifier **le propriétaire du dépôt**, pas seulement son nom.
3. ⛔ **Un abonnement Claude Pro ou Max ne s'utilise pas dans un outil tiers** : c'est une clé API, payée à l'usage.
4. ⚠️ **N agents = quota divisé par N.** Orca, Ruflo et l'audit Cloudflare consomment vite. Sur ce PC s'ajoute la mémoire : une tâche lourde à la fois.
5. **Commencer petit** : `/office-hours` avant les 28 commandes de gstack, un projet de test avant Ruflo, une intro de 10 secondes avant de migrer un studio vidéo.
6. **Un audit qui a des contradicteurs** est le même principe que notre règle « vérifier avant d'affirmer » : chaque faille trouvée passe à un agent dont le seul travail est de prouver qu'elle n'existe pas.

## La vidéo elle-même est une leçon de montage (faite avec HyperFrames)

Utile pour `_studio-video/` et les vidéos de NEBULA :
- face caméra plein cadre, qui devient une **vignette en bas à droite** (bord cyan arrondi) dès qu'on montre un écran ;
- chaque écran est posé dans une **fenêtre** avec une **barre d'adresse étiquetée** (« github.com/morluto/rea · Quick start », « VoiceStudio · clonage et doublage ») sur un fond nuit violet à grille rétro ;
- des **cartes qui apparaissent une par une** sur le face caméra **flouté et assombri** (« REA en 4 étapes », « L'audit en 4 étapes », la dernière carte en cyan) ;
- des **listes à pastilles** ✓ vert, ! orange, ✗ rouge (« Tout dépend de votre machine », « Claude dans OpenCode ») ;
- une **pastille compteur d'étoiles** (« ★ 382 846 étoiles sur GitHub ») ;
- le **texte à lire surligné en jaune ou encadré en rouge** dans les pages ;
- une **grille récapitulative** des 10 à la fin, puis une **pilule verte d'appel au commentaire**.

## État chez nous (2026-11-01)

- **Déjà installé** : `frontend-design@claude-plugins-official`. Déjà disponibles autrement : `skill-creator` (skills Anthropic), `code-review` (intégré).
- **Pas installés** : playground, ralph-loop, Context7, Security Guidance, code-simplifier, HyperFrames, l'audit Cloudflare, gstack, REA, Orca, Ruflo.
- Le connecteur claude.ai **« HyperFrames by HeyGen »** est présent mais pas authentifié.
- Node.js v22.14.0 : assez pour HyperFrames (22 minimum).

## Ce qui sert à NEBULA, et dans quel ordre

1. **L'audit de sécurité Cloudflare**, **le plus utile** : le dépôt est public, **PISTE** et **MA LETTRE À…** encaissent de l'argent (webhooks SasPay, Supabase, livraison automatique) et n'ont jamais eu d'audit. Lancer en **lecture du source seulement** (pas de bac à sable imposé sur ce PC), un produit à la fois, en commençant par PISTE.
2. **HyperFrames**, à **essayer** sur une vidéo courte : licence **Apache 2.0**, alors que Remotion est gratuit seulement jusqu'à 3 employés, interdit de livrer le projet au client et change de licence en 5.0 (voir `[[reference_remotion-licence]]`). **Ne pas migrer** le studio existant avant d'avoir comparé.
3. **Plugins officiels** : **Context7** (documentation à jour de Next.js, GSAP, Remotion, Supabase) et **playground** (Mongazi règle lui-même un design aux curseurs au lieu de le décrire).
4. **gstack**, peut-être seulement **`/office-hours`**, pour éprouver une idée de produit vertical. Ses `/qa` et `/review` doublonnent nos QC Playwright.
5. **Pas sur ce PC** : VoiceStudio et ComfyUI (carte graphique NVIDIA et ~17 Go de modèles, disque déjà juste ; on a WaveSpeed et ElevenLabs), Orca et Ruflo (mémoire, quota, et pour Ruflo, les droits du compte), OpenCode (on a l'abonnement Claude Code), REA (aucun besoin aujourd'hui ; si un jour, uniquement sur des applis qu'on a le droit d'analyser).
