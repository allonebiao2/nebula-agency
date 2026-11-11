# L'agent de montage vidéo, décortiqué (relevé du 2026-11-11)

> Base de travail pour le projet de Mongazi du 2026-11-11 : « une app, un agent capable de monter n'importe quel
> type de vidéo lui-même. Les clients déposent leurs rushes, décrivent comment ils veulent la vidéo, et obtiennent
> une vidéo déjà montée, prête pour YouTube, TikTok, etc. » Puis : « plusieurs vidéos pour des particuliers, payées
> chaque mois, absolument tout type de vidéo : publicitaire, virale pour TikTok ». Exigence : des montages qui
> « valent 10 000 euros minimum ».
>
> Point de départ : une capture de la vidéo YouTube « I investigated 8 GitHub repos that print money »
> (`_partage/depot github .png`), qui présente **OpenMontage** comme un « pack de vidéos pub » à vendre
> 500 $ d'installation + 1 000 $ par mois à des boutiques Shopify (quatre pubs courtes par mois).

## Comment le relevé a été fait

- **Quatre dépôts téléchargés et lus dans leur code** (pas seulement leur README) : OpenMontage, video-use,
  openfilm, open-edit. Clones dans le dossier temporaire de la session, rien n'est entré dans ce dépôt.
- **Étoiles, licence et dernière activité** relevées par l'API publique de GitHub le 2026-11-11, pour une
  quarantaine de dépôts. Les chiffres bougent vite : ce sont des photographies du jour.
- La liste classée `sasateguh/awesome-ai-video-for-creators` (CC0, mise à jour chaque semaine) a servi de carte :
  près de 200 outils en 7 familles.
- **REA n'a pas servi, et c'est voulu** : son propre mode d'emploi dit que pour un dépôt dont on a **tout le code
  source**, on lit le code ; REA sert aux logiciels fermés. Il servira si on veut observer un concurrent fermé
  en ligne (Opus Clip, Submagic, CapCut web) : regarder ses fonctions, jamais recopier son code.
- Skills croisés : `video` (carte des approches), `video-shotcraft` (règles d'une vidéo premium, Apache-2.0,
  installé ici).

## La découverte qui décide de tout : la licence

Pour **vendre un service par abonnement**, la licence du code compte plus que ses étoiles.

| Licence | Ce qu'elle permet pour NEBULA |
|---|---|
| **MIT, Apache-2.0, BSD, Unlicense** | Prendre, modifier, vendre en service. Garder la mention du copyright. Apache : garder le fichier `NOTICE` |
| **GPL-3.0** | Utilisable **sur nos serveurs** (rien n'est distribué). Interdit de l'embarquer dans une appli qu'on donne aux clients sans publier tout notre code |
| **AGPL-3.0** | Comme la GPL, **plus** : si on le modifie et que des clients s'en servent **par Internet**, on doit leur offrir **tout notre code source**. Incompatible avec un produit en libre-service fermé |

⛔ **OpenMontage est en AGPL-3.0, sans exception ajoutée** (vérifié dans son `LICENSE`).
⛔ **Ultralytics YOLO (le suivi d'objets le plus utilisé) est aussi en AGPL** : plusieurs « clippers » MIT
s'appuient dessus sans le dire (openshorts, auto-vertical-reframe). Pour le recadrage, utiliser **MediaPipe**
(Apache-2.0).
⚠️ Je ne suis pas juriste : avant d'encaisser, faire relire ce point.

**Ce qui reste permis avec OpenMontage** : s'en servir **en interne** comme studio. Si c'est NEBULA qui le fait
tourner et que le client reçoit seulement la vidéo finie, le client n'interagit pas avec le logiciel, et la vidéo
produite n'est pas couverte par la licence. C'est exactement le modèle « agence » de la vidéo YouTube. Lire ses
pipelines pour apprendre est libre : une idée ne se protège pas, son texte oui. **On ne recopie aucun de ses
fichiers** (code, skills Markdown, manifestes YAML) dans notre produit.

**Deux autres pièges de licence** :
- **Remotion** : gratuit tant que NEBULA a **3 employés au plus**, et sa licence interdit de « vendre, louer ou
  sous-licencier votre propre dérivé de Remotion ». Pour un produit où les clients fabriquent leurs vidéos, prendre
  **HyperFrames** (Apache-2.0, de HeyGen, 82 700 étoiles, ses skills sont déjà installés ici). Remotion reste bon
  pour nos productions internes (`_studio-video/`).
- **Claude** : un produit vendu à des clients passe par **l'API** (Claude Agent SDK, clé API facturée à l'usage),
  pas par un abonnement Claude Code. Anthropic n'autorise pas un produit tiers à faire tourner ses clients sur un
  compte claude.ai. Or OpenMontage, video-use et reelmimic sont faits pour tourner **dans** Claude Code.

## Les quatre dépôts lus dans leur code

### OpenMontage · 79 640 étoiles · AGPL-3.0 · le plus complet, le moins réutilisable

- Dépôt déplacé : `OpenMontageInc/OpenMontage` (l'ancienne adresse `calesthio/OpenMontage` redirige). 164 Mo,
  660 fichiers Python, 1 106 fichiers Markdown.
- **Pas d'orchestrateur en code** : « ton assistant de code EST l'orchestrateur ». L'agent lit un manifeste YAML
  (`pipeline_defs/`), puis la skill de chaque étape (`skills/pipelines/<pipeline>/<étape>-director.md`), appelle
  des outils Python, se relit, enregistre un point de reprise JSON, demande l'accord humain.
- **13 pipelines**, dont 6 marqués « production » (explainer animé, animation, avatar, cinématique, hybride,
  démo d'écran) et 7 « beta ». ⚠️ **Celui qui monte des rushes de client, `talking-head`, est en beta**, avec un
  budget par défaut de 0,50 $.
- Chaque pipeline suit la même chaîne : recherche, proposition, script, plan des scènes, assets, montage,
  composition. Avec `human_approval_default: true` à chaque étape : il est fait pour qu'un humain valide.
- Outils : une centaine, rangés par famille (analyse, audio, avatar, capture, enhancement, graphics, video,
  subtitle). Plus de 60 fournisseurs branchés (Kling, Veo, Seedance, Runway, ElevenLabs, Suno, Pexels…), choisis
  par un **score sur 7 critères** journalisé.
- Ce qu'il fait de mieux, **à reprendre en idée** : le plafond de dépense et l'accord au-delà de 0,50 $ par
  action, le contrôle « anti-diaporama » avant rendu, la relecture après rendu (ffprobe, images extraites,
  niveaux audio), le tableau « Backlot » qui montre la production avancer, le départ depuis **une vidéo de
  référence** (« fais-moi la même chose sur mon sujet »).

### video-use · 30 910 étoiles · MIT · la meilleure méthode pour monter des rushes

- `browser-use/video-use`. **2 500 lignes en tout** : 6 scripts Python (transcription, résumé des prises,
  planche de lecture, étalonnage, rendu) + un `SKILL.md` de 342 lignes.
- **L'idée centrale, à reprendre** : l'IA ne regarde pas la vidéo, elle la **lit**. Une transcription mot à mot
  de toutes les prises tient en 12 Ko de texte ; des planches (bande d'images + forme d'onde + mots) ne sont
  fabriquées qu'aux moments de doute. « 30 000 images × 1 500 tokens = 45 millions de tokens de bruit » contre
  « 12 Ko et quelques PNG ».
- Chaîne : transcrire, résumer, raisonner, **liste de coupes (EDL)**, rendre, se relire (3 reprises au plus).
- **Ses 12 règles dures**, toutes à garder : sous-titres posés en dernier ; extraire chaque segment puis coller
  sans réencoder ; fondu audio de 30 ms à chaque coupe (sinon un « pop ») ; ne jamais couper dans un mot ; marge
  de 30 à 200 ms à chaque coupe ; transcription mot à mot uniquement ; transcription gardée en cache ; plan validé
  avant de toucher au montage ; tout ce qui sort dans `edit/`.
- Dépend d'ElevenLabs Scribe pour la transcription : **remplaçable par Deepgram Nova-3** (clé déjà dans
  `secrets/deepgram.env`, horodatage mot par mot) ou par faster-whisper (MIT) en local.

### OpenFilm · 5 777 étoiles · MIT, mais nom et logo protégés · le format montable

- Un film est un dossier avec un **`film.html`** : des pistes (`<section>`) de clips (`<video>`, `<audio>`,
  `<iframe>` d'une page animée). Chaque page dessine n'importe quel instant avec une fonction `frame(t)`.
- Livré avec **Studio**, un vrai éditeur dans le navigateur (déplacer, recadrer, couper sur la timeline, export
  vers Premiere, Final Cut, DaVinci Resolve).
- **L'idée à reprendre** : la vidéo livrée reste **modifiable**. L'agent monte, le client retouche à la main.
- ⚠️ `TRADEMARK.md` : le code est libre, mais un produit ou un service ne peut pas s'appeler « OpenFilm ».

### open-edit (VEED) · 1 797 étoiles · Apache-2.0 · un entonnoir vers VEED

- Outil en ligne de commande : transcrire (WhisperX en local, ou VEED payant), générer un présentateur IA,
  détourer, synchroniser les lèvres. La plupart des fonctions demandent un compte VEED et ses crédits.
- Utile pour son **convertisseur de transcriptions** (accepte tous les formats Whisper) et sa règle « devis
  d'abord, dépense ensuite » : la génération payante se fait en deux commandes, la seconde dépense exactement ce
  qui a été approuvé.

## Les autres dépôts, par besoin

Relevés le 2026-11-11 (étoiles · licence · dernière activité).

### Monter des rushes à partir d'une consigne

| Dépôt | Étoiles | Licence | Ce qu'on en tire |
|---|---|---|---|
| FireRedTeam/FireRed-OpenStoryline | 3 667 | Apache-2.0 | agent de montage par conversation, **avec interface web**, serveur MCP d'outils. ⚠️ ses polices et musiques par défaut ne sont pas libres pour un usage commercial |
| kajisho5/ffmpeg-skill | 5 077 | MIT | 42 outils FFmpeg avec un contrat lisible par machine et un serveur MCP |
| WyattBlue/auto-editor | 5 849 | Unlicense | coupe les silences et les temps morts, en une commande |
| riecodes/free247editor | 176 | MIT | même idée que video-use, plus petit |
| poseljacob/agentic-video-editor | 509 | MIT | rushes + brief vers une pub, plusieurs agents (Gemini) |
| HKUDS/VideoAgent | 2 043 | MIT | recherche universitaire (EMNLP), compréhension et remontage |
| palmier-io/palmier-pro | 14 731 | GPL-3.0 | éditeur macOS fait pour l'IA. Serveur seulement |

### Une vidéo longue vers des shorts (podcast, live, interview)

| Dépôt | Étoiles | Licence | Note |
|---|---|---|---|
| mutonby/openshorts | 7 701 | MIT | moments forts, recadrage visage, sous-titres, publication. ⚠️ le dossier `cloud/` interdit la revente en service, et il utilise YOLOv8 (AGPL) |
| Anil-matcha/AI-Youtube-Shorts-Generator | 5 957 | MIT | alternative libre à Opus Clip |
| modelscope/FunClip | 6 541 | MIT | découpe assistée par LLM, interface Gradio |

### Des vidéos en série sans tournage (pub, faceless, viral)

| Dépôt | Étoiles | Licence | Note |
|---|---|---|---|
| harry0703/MoneyPrinterTurbo | 142 486 | MIT | un sujet donne un short : script, images d'archive, voix, sous-titres, musique |
| edenfunf/reelmimic | 1 916 | MIT | montre une vidéo qu'on aime, il en fait une nouvelle **dans le même style**. 2D uniquement, 1 à 3,5 h par vidéo, tourne sur le compte Claude Code |
| Vincentwei1021/video-shotcraft | 18 718 | Apache-2.0 | 157 recettes de plans, règles esthétiques, sound design. **Déjà installé ici**. ⚠️ 6 bruitages sans origine retrouvée |
| lemomo-ai/lemo-opuscar | 14 824 | MIT | 66 styles de film en code |
| darkzOGx/youtube-automation-agent | 5 145 | MIT | fait tourner une chaîne YouTube de bout en bout |

### Les briques (toutes réutilisables)

| Besoin | Brique | Licence |
|---|---|---|
| Transcription mot à mot | faster-whisper · WhisperX · Deepgram Nova-3 (clé déjà là) | MIT · BSD-2 · service |
| Changements de plan | PySceneDetect | BSD-3 |
| Visages, recadrage 9:16 | MediaPipe | Apache-2.0 |
| Motion design, titres, sous-titres animés | HyperFrames | Apache-2.0 |
| Voix | Chatterbox (clonage) · Kokoro · ElevenLabs, Deepgram Aura (services) | MIT · Apache-2.0 |
| Musique générée | ACE-Step | Apache-2.0 |
| Plans générés par IA | Wan 2.2 (local, GPU) · WaveSpeed (Kling, Seedance, Veo : compte déjà ouvert) | Apache-2.0 · service |
| Synchronisation des lèvres | LatentSync | Apache-2.0 |
| Traduction et doublage | VideoLingo | Apache-2.0 |
| Agrandir en 4K, fluidifier à 60 i/s | **VIDÉO HD**, notre outil (`scripts/video-hd/`) : Real-ESRGAN + RIFE | BSD-3 · MIT |
| Éditeur où le client retouche | **LA BOBINE**, le nôtre (`labobine/`) · OpenCut (MIT, 98 112 étoiles) en référence | à nous · MIT |

⚠️ Les **poids** d'un modèle ont parfois une licence différente du code : LTX-Video est en Apache pour le code,
mais ses modèles sont gratuits seulement sous 10 millions de dollars de chiffre d'affaires. Vérifier à chaque fois.

## Ce qui fait une vidéo « à 10 000 euros »

Aucun dépôt ne promet ça. Ce qui s'en approche, relevé dans les règles de video-shotcraft (tirées de retours
réels) et dans les contrôles d'OpenMontage et de video-use :

1. **L'accroche** des 1 à 3 premières secondes, et une seule idée par plan. Une technique d'animation n'est la
   vedette qu'**une fois** dans tout le film ; un plan ou un slogan répété se supprime.
2. **Le rythme, plutôt lent que rapide** : tous les retours de video-shotcraft disaient « ralentis », jamais
   « trop lent ». Le logo final reste au moins 1 s ; une animation de groupe finit sur 0,5 s d'immobilité.
3. **La musique calée sur le temps** : tempo et temps forts mesurés (librosa) avant le découpage ; coupes à
   3 images près ; au plus 3 chocs qui secouent tout l'écran par film.
4. **Le son fait la moitié du travail** : un bruit réel pour chaque geste à l'écran, des bruitages de cinéma
   (montée, impact, scintillement), jamais de sons de jeu vidéo ; volume final à -14 LUFS ; fondus de 30 ms.
5. **L'image** : un étalonnage cohérent sur tous les plans, les couleurs et les polices **du client** (pas une
   « peau de pub » plaquée), aucun reflet décoratif distribué partout.
6. **Les sous-titres lisibles** : au moins 5 % de la hauteur de l'image, posés en dernier.
7. **La relecture par un autre** : video-shotcraft impose qu'un agent **neuf**, qui n'a pas fabriqué la vidéo,
   la juge image par image avant que le client la voie. « Le premier contrôle n'est jamais confié au client. »
8. **Un humain qui valide le plan** pour l'offre haut de gamme. La limite reste la matière : des rushes flous ou
   mal éclairés plafonnent le résultat, quel que soit l'agent.

## Ce que ça veut dire pour NEBULA

### Deux façons de vendre, à ne pas confondre

| | A. L'agence augmentée | B. Le produit en libre-service |
|---|---|---|
| Qui fait tourner l'agent | NEBULA, sur Claude Code | les serveurs NEBULA, par l'API Claude |
| Le client | envoie ses rushes (WhatsApp, Drive), reçoit la vidéo | dépose, décrit, paie et télécharge seul |
| OpenMontage | **utilisable** en interne | ⛔ AGPL : à réécrire avec nos briques |
| Mise en route | immédiate | plusieurs vagues : serveur, stockage, caisse |
| Ce que dit la vidéo YouTube | c'est ce modèle-là (500 $ + 1 000 $/mois, 4 pubs) | |

### L'architecture proposée pour B (rien n'est construit)

1. **Le dépôt** : rushes + un brief guidé (but, plateforme, durée, ton, une vidéo de référence, logo et couleurs).
2. **La lecture** : transcription mot à mot, plans, visages, silences, énergie du son, qualité de l'image, tempo
   de la musique. Tout devient du texte et des planches (méthode video-use).
3. **La réalisation** : Claude par l'API écrit le plan (EDL en JSON) en suivant **nos propres** skills de
   réalisateur, écrites par nous.
4. **La fabrication** : FFmpeg (coupes, étalonnage, sous-titres), MediaPipe (9:16), HyperFrames (titres,
   animations), WaveSpeed si un plan manque, voix et musique sous licence.
5. **Le contrôle** : relecture du rendu, puis un relecteur neuf, puis un humain pour le haut de gamme.
6. **La livraison** : 16:9, 9:16, 1:1, miniature, titre et description, et **un projet modifiable** (idée
   d'OpenFilm), naturellement dans **LA BOBINE**, qui a déjà sa timeline, ses comptes et sa caisse en attente.

### Les points durs, à trancher avant de coder

- **Où ça tourne** : ce PC n'a ni carte graphique ni mémoire pour un service (8 Go, une tâche lourde à la fois).
  Le montage FFmpeg tourne sur processeur ; la génération IA passe par un service. Un serveur vidéo demande
  souvent une carte bancaire (voir mémoire `feedback_pas-de-cb`).
- **Où dorment les rushes** : des vidéos de clients pèsent des gigaoctets. Le stockage est le vrai coût.
- **Les droits** : musique sous licence commerciale (un son tendance de TikTok ne va pas dans une pub), visages
  des clients = données personnelles (APDP).
- **Le coût par vidéo** (API Claude, transcription, génération) : à mesurer sur un premier essai réel, pas à
  deviner.
