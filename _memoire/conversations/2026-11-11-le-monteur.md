# 2026-11-11 · LE MONTEUR, l'agent de montage vidéo

## La demande

Mongazi, à partir d'une capture de la vidéo YouTube « I investigated 8 GitHub repos that print money » qui
présente OpenMontage : « une app, un agent capable de monter n'importe quel type de vidéo lui-même ». Puis son
objectif (/goal), répété deux fois :

> « L'agent IA dans l'app ou le SaaS doit pouvoir monter tout type de vidéo, quels que soient le type ou la demande
> du client ou moi, des montages et des vidéos qui valent toutes minimum 10 000 euros. Et même sans rush, l'agent
> doit pouvoir monter la vidéo en cherchant, en partant de rien, juste à partir d'une demande. »

## La recherche

Quatre dépôts lus dans leur code, une quarantaine relevés : `_knowledge/montage-ia-decortique.md`.
**OpenMontage est en AGPL-3.0** : bon studio interne, interdit au cœur d'un produit en libre-service fermé.
À Mongazi qui demandait s'il suffisait : non (licence, validation humaine à chaque étape, montage de rushes en
« beta »). Il a choisi **l'appli** (option B).

## Ce qui est construit

Un projet **privé**, hors de ce dépôt public : `C:\Users\USER\nebula-montage` (git local). Le dépôt GitHub privé
n'a pas pu être créé automatiquement (refusé par le garde-fou de Claude Code) : **Mongazi le crée**.

- **Avec rushes** : lecture (transcription mot à mot Deepgram, plans, visages, netteté, silences, planches), un
  réalisateur Claude Opus 5.5 qui rend un plan JSON validé et recalé entre les mots, une fabrication ffmpeg exacte à
  l'image et à l'échantillon, un banc de 16 mesures. Essai : une interview NASA de 3 min (domaine public) devenue un
  short vertical de 40,5 s pour 0,18 $, banc 16/16.
- **Sans rush** : un scénariste Claude, une voix off Deepgram Aura-2 (Agathe), une collecte d'images (Pexels et
  Pixabay si une clé existe, sinon FLUX.2 par Cloudflare Workers AI, gratuit), un mouvement de caméra sur chaque
  image, un sound design sobre, chaque licence notée. Essai : une pub TikTok de 30 s pour MA LETTRE À… à partir de
  la seule demande.
- **Le relecteur** : un second appel, neuf, qui note la vidéo sur 8 critères (accroche, histoire, rythme, image,
  artefacts d'IA, texte, son, exactitude), rend un plan corrigé et les images à refaire ; deux corrections au plus.

## Ce que le banc a attrapé

- Une cadence de 29,83 i/s au lieu de 30 : le son d'un segment commençait en retard, le collage décalait la suite.
  Corrigé : chaque segment a un nombre exact d'images et d'échantillons (`aresample=async=1:first_pts=0`).
- Le relecteur attrapera ce que le banc ne mesure pas : une image générée de tasse à deux anses en est l'exemple.

## Le premier film sans rush (même jour, relancé à la demande de Mongazi)

La pub TikTok de 30 s pour MA LETTRE À… est allée au bout : banc **16/16**, relecteur **6,0/10** au premier tour, avec
des défauts justes (adresse hors cadre, sous-titres sur un visage, fausse interface, autre femme dans la boucle, prix
trop petit). Au second tour, **le crédit de l'API Anthropic était épuisé**. Corrigé dans le moteur, sans appel payant :

- **Le script fait foi** : Deepgram avait entendu 15 mots faux dans la voix de synthèse (« un cachet d'or » pour
  « dort », « Salut. » pour « Puis il s'allume… »). Les sous-titres reprennent le texte du script, posé à l'heure
  qu'a entendue Deepgram.
- **Un texte se mesure** avec sa police avant d'être posé (libass : taille 96 = corps de 63 px, mesuré au pixel).
  L'adresse se coupe « malettre. » / « nebula-agency.online », jamais après un tiret ; une adresse dictée s'écrit
  comme une adresse ; un sous-titre qui répète le texte affiché est retiré ; le prix est plus grand.
- **Les sous-titres évitent les visages** détectés, et gardent la même place pendant tout un plan.
- **La même personne revient avec la même image** (`reprend_scene`) : un générateur ne la refait jamais à l'identique.
- **Un appel payé ne se perd plus** : la relecture est gardée hors du dossier de rendu, et une panne d'API livre
  quand même la vidéo et son rapport.

## Sans Claude, et OpenMontage (même soir)

- Mongazi : « sans le Claude d'Anthropic ça ne peut pas fonctionner ? » La lecture, la fabrication, le son, le banc et
  un montage simple (`--sans-ia`) tournent sans modèle. Le scénariste, le réalisateur et le relecteur en ont besoin.
  Comparé : Claude (0,50 à 1 $ par vidéo, carte bancaire), Gemini (gratuit sous quota, sans carte, voit les images),
  Groq (gratuit, ne voit pas bien les images).
- « OpenMontage est-il plus apte ? » Non : il n'a **aucun orchestrateur en code**, l'assistant de code conduit chaque
  étape. Il dépend donc **plus** de Claude que nous, demande l'accord humain à chaque étape, et ne se vend pas (AGPL).
  Il est plus large aujourd'hui (animation, avatars, 60 fournisseurs) : utilisable en studio interne.
- Mongazi : « branche Gemini en secours ». Fait (`monteur/ia.py`, commit `4167a61`). Claude d'abord ; Gemini prend
  le relais si Claude est indisponible (crédit, clé, quota, réseau, panne), jamais pour contourner un refus. Google
  a une nouvelle API (`/v1beta/interactions`) et dit `generateContent` « legacy mais entièrement prise en charge » :
  c'est elle qu'on utilise. Le modèle est choisi à l'exécution dans la liste de la clé (les noms changent :
  `gemini-4-carbon`, `gemini-3.6-flash`…). Aucun appel réel encore : il faut la clé.
- « Pourra-t-on atteindre l'étendue d'OpenMontage ? » Oui : elle vient de services branchés. Animation (HyperFrames),
  démo d'écran (NEBULA REC), vidéo générée (Wan, Kling par WaveSpeed), avatar (InfiniteTalk, HeyGen), voix et musique.
  La vraie limite est le budget de génération.

## Le verdict de Mongazi, et la réponse franche

- Mongazi : « ça ne vaut pas un travail de 500 dollars même, tu jugerais ça combien ? » Réponse : **50 à 150 €**,
  le niveau d'une vidéo « sans visage » Fiverr ou InVideo. Sept raisons :
  1. un diaporama d'images fixes ;
  2. le produit n'apparaît jamais ;
  3. aucun personnage suivi ;
  4. une voix synthétique ;
  5. un son générique ;
  6. du texte posé ;
  7. un concept plat.
- Huit travaux, par ordre d'impact :
  1. une vraie vidéo à chaque scène ;
  2. une seule héroïne ;
  3. le vrai produit ;
  4. une vraie voix ;
  5. un son pensé pour l'histoire ;
  6. un habillage animé ;
  7. une étape de concept et de story-board ;
  8. un relecteur à 8,5/10 minimum.
- Dit franchement : avec les travaux 1 à 6, une pub vaut **500 à 1 500 €**. **10 000 €**, c'est un tournage ou un
  studio de création : atteignable en offre premium avec un humain qui dirige, pas en automatique pour chaque demande.
- « Ma présence demandera quoi concrètement ? » En premium seulement, trois validations depuis le téléphone :
  le concept parmi 3 (5 min), le story-board de 8 à 12 vignettes (10 min, avant toute génération chère), puis la
  version finale (5 à 10 min, deux retours au plus). 20 à 30 minutes par vidéo. L'offre standard tourne sans lui.

## La recherche sur GitHub pour les autres vagues

56 dépôts relevés par l'API GitHub, 51 modèles par l'API Hugging Face, licences floues lues. Tableau complet dans
`_knowledge/montage-ia-decortique.md` (« Les briques pour passer d'un diaporama à une vraie pub »).

- Retenus (code et poids libres) :
  - vidéo : Wan 2.2 ;
  - personnage : Qwen-Image-Edit, FLUX.2 klein, Phantom ;
  - voix française : Chatterbox V3, Kyutai TTS en_fr, CosyVoice 3 ;
  - son : ACE-Step, Beat This!, ThinkSound ;
  - habillage : HyperFrames ;
  - concept : ViMax ;
  - relecteur : VBench, TalkNet ;
  - avatar : InfiniteTalk ;
  - restauration : SeedVR2.
- Écartés :
  - ⛔ InfiniteYou et MMAudio (poids non commerciaux), DOVER (S-Lab), MovieAgent (aucune licence) ;
  - ⚠️ PuLID et InstantID (insightface), LTX-2, HunyuanVideo, Stable Audio Open ;
  - ⚠️ Kokoro : une seule voix française.
- Libre ne veut pas dire gratuit à faire tourner : Wan 2.2 5B veut une carte de 24 Go, le PC n'en a pas.

## Le calcul gratuit hors du PC

- Kaggle : environ 30 h de GPU par semaine, sans carte mais avec vérification par téléphone. ⛔ Ses conditions disent
  usage interne, personnel, **non commercial**.
- Colab : prévu pour l'usage interactif.
- Lightning AI : 5 crédits sans carte.
- Cloudflare Workers AI : 10 000 neurones par jour, usage commercial permis.
- **GitHub Actions** : processeurs, 2 000 min par mois en privé, usage commercial permis.
- Décidé :
  - les GPU gratuits servent à la **recherche** (essayer Wan 2.2) ;
  - les **rendus** iront sur GitHub Actions ;
  - le calcul pour les **clients** sera payant, dans le prix de l'abonnement.
- Mongazi a créé le dépôt privé `nebula-montage` (23 h 48) ; le code est poussé (`923134a`), vérifié privé (404).

## La clé Gemini (2026-11-12, 0 h 20)

Mongazi l'a créée et copiée. Rangée depuis le presse-papier dans `secrets/gemini.env` (`GEMINI_API_KEY=`), jamais
affichée, ignorée par git. ⚠️ **Nouveau format de clé Google : `AQ.` suivi de 50 caractères, avec des points**
(l'ancien commençait par `AIza`) : un contrôle de forme trop strict l'avait d'abord refusée. Premier vrai appel
réussi : réponse JSON conforme au schéma. `gemini-4-carbon` et `gemini-4-argon` ne sont pas ouverts à une clé
gratuite ; le secours est passé seul sur `gemini-3.8-flash`.

## Ce qui attend Mongazi

1. ✅ Clé Gemini rangée et éprouvée. Le crédit Anthropic reste à recharger pour retrouver Claude.
2. ✅ Dépôt GitHub **privé** `nebula-montage` créé par Mongazi, code poussé.
3. Répondre au relecteur : « 1 000 F » en francs CFA ? que couvrent les « 7 jours » ? de vraies captures de MA LETTRE À… ?
   le logo et la typographie officiels ?
4. En option, sa voix sur le texte de la pub (environ 30 s).
5. Dire oui ou non à l'installation de `gh` (rendus sur GitHub Actions).
6. Plus tard : une clé **Pexels**, le nom du produit, un vrai rush de client.

La suite exacte : `C:/Users/USER/nebula-montage/REPRENDRE-ICI.md`.
