# 2026-11-04 et 05 · NEBULA VOIX : des agents vocaux qui appellent au Bénin

## La demande
Mongazi veut des agents vocaux IA, avec de vraies voix, qui appellent entreprises et particuliers 24 h sur 24 pour amener
des clients qui prennent rendez-vous et achètent. NEBULA vend ensuite ce service. Le cap : « devenir l'agence n°1 des
appels au Bénin ». Bénin d'abord, puis l'Afrique ; étape par étape ; tout en gratuit pour commencer. Il a donné à Claude
le contrôle du PC et des recherches pour ce chantier.

## Ce qui a été fait
- **Étape 1, recherche approfondie** : 7 recherches, puis un rapport. Fichiers : `_documents/nebula-agency/voix/Agents vocaux appels au Benin.*` (Markdown, Word, PDF, HTML). Ce qu'on en retient :
  - **La loi** : consentement préalable prouvé pour tout appel automatisé à une personne physique (art. 245, 332). Seuls les numéros « impersonnels » de sociétés y échappent. Autorisation de l'APDP pour tout transfert de la voix à l'étranger (art. 391). SIM box : 3 à 5 ans de prison (art. 248).
  - **Le coût** : il est dans la téléphonie. 0,48 à 0,65 $/min vers un mobile béninois depuis l'étranger (plancher ARCEP de 90 FCFA), contre environ 0,01 $/min par WhatsApp Calling.
  - **Les dépôts** : Dograh (BSD-2) couvre environ 75 % de l'objectif.
  - **Le marché** : 60 à 150 FCFA par minute (Kolonell, octobre 2026).
- **Étape 2, la grille** : `_documents/nebula-agency/voix/Grille des fonctions NEBULA VOIX.*`. 85 fonctions, dont 39 indispensables au pilote. Couverture du pilote : Dograh environ 59 %, LiveKit environ 58 %.
- **Étape 3, Dograh décortiqué** : `nebula-voix/docs/etape3-dograh.md`. Le fork Pipecat reste maintenable (+7 765 / -495).
- **Le prototype Awa** (`nebula-voix/coeur/`), sur la carte réelle d'Au Braisé d'Or :
  - testé par écrit : prix lus avec l'outil, prix proposé par le client refusé, rendez-vous au +229 01, opposition notée ;
  - essayé à la voix par Mongazi : « c'est pas mal ».
- **Clés branchées**, toutes depuis son presse-papier, sans affichage : Deepgram (200 $ offerts), LiveKit Cloud (`wss://mes-voix-vdtw1id3.livekit.cloud`), Cloudflare Workers AI. Les clés Claude API existantes ont du crédit.
- **Images gratuites** : l'outil `scripts/image_cf.py` (Workers AI). Le quota de 10 000 neurones par jour a été épuisé en quatre images.
- **Le skill Impeccable** est mis à jour en v4.8.0. Son moteur binaire est ignoré par git.

## Les objectifs ajoutés par Mongazi
- **Une vendeuse naturelle et ultra intelligente, entièrement réglable depuis une console** : consignes, modèle, voix clonée, options, connaissances. Elle répond hors script, ramène la conversation au but, rit, écoute. Un banc d'essai de clients simulés vérifie chaque réglage.
- **Passer de 25 % à 100 %, voire 200 %, de la rétro-ingénierie utile**. Vague 2a : QuickVoice, VoiceBlender, LiveKit Agents, Smart Turn, Jambonz, Kyutai Unmute, Fonoster, Rapida en lecture seule. Vague 2b : Chatterbox, et les consoles observées sur nos comptes d'essai.
- **Le cadrage ChatGPT** (reçu en partie) a apporté quatre ajouts : un parcours d'apprentissage, un compteur de coût par appel, zéro dépendance, et un tableau pays par pays pour l'international.
- **STELLA**, son « Jarvis » en 3D, est la dernière vague. Mémoire : `project_obsidian-maison`.

## Leçons
- Twilio ne se « rétro-ingénière » pas : on y paie l'accès aux réseaux. Le vrai levier est une ligne SIP chez MTN, Moov ou Celtiis, ou WhatsApp Calling chez Meta.
- Le modèle de VoiceStudio (OmniVoice) est sous CC-BY-NC : bon pour STELLA, interdit au produit. Pour le produit : Chatterbox (MIT).
- Les WAV en flux de Deepgram ont un en-tête faux : il faut les réécrire avant de les lire.
- LiveKit : les modules se chargent au démarrage, jamais dans l'appel (« Plugins must be registered on the main thread »).
- Notre `agent.py` masquait le paquet `agent` de LE STANDARD : le fichier a été renommé `standardiste.py`.
- Le PC de 8 Go sature : il a fallu fermer Chrome, Discord, Copilot et Edge pour les essais locaux.

## Ce qui reste
- Relancer la vague 2a, coupée par la limite d'usage.
- L'essai d'Awa dans le playground.
- La création du dépôt GitHub privé.
- La suite du texte ChatGPT.
- Le choix entre Agathe et Hector.
- La console de réglage et le banc d'essai.
- Le test de clonage avec Chatterbox (Kaggle).
- La demande de ligne SIP aux opérateurs.
- Le dossier APDP.
