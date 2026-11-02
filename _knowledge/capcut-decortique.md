# CapCut, décortiqué (relevé du 2026-11-02)

> Base de travail pour le projet de Mongazi : créer « son » CapCut (puis son n8n).
> Page complète : https://claude.ai/artifact/59158HSvUGLjYgySzEmstY · source : `_knowledge/capcut-decortique.html`.

## Comment le relevé a été fait

- CapCut est installé sur le PC de Cotonou : `%LOCALAPPDATA%\CapCut\Apps\6.6.1.2640`, **version 6.6.1 du
  17 juillet 2025** (1,7 Go). Les versions actuelles : **9.3.0 sur Mac** (19 août 2026), **19.9.0 sur iPhone**,
  19.1.0 sur Android (Wikipédia, App Store).
- **REA ne sert à rien ici** : `inspect_desktop_application` ne reconnaît que .NET, Unity, Unreal, Godot,
  GameMaker et Electron ; CapCut est en **Qt**, il rend zéro candidat. Et `observe_native_ui` /
  `capture_native_ui_scenario` (piloter l'interface) ne marchent que sur **Mac** (cibles Mach-O).
- Le relevé vient donc des **noms des DLL** et du fichier **`Resources/po/fr-FR.po`**, livré en clair :
  **13 143 libellés**, regroupés par le préfixe de leur identifiant (`pc_voice`, `pc_charts`, `pc_overdub`…)
  en 194 modules. Lecteur : un analyseur `.po` ligne par ligne (une regex passée par le shell Git Bash a perdu
  ses barres obliques).
- ⛔ **Aucun code décompilé** : les conditions d'utilisation de CapCut l'interdisent. S'inspirer des fonctions
  est libre ; recopier code, modèles ou ressources ne l'est pas.
- CapCut **n'a pas été lancé** : un lundi à 14 h 37, la démo ORB tournait avec MT5 et il restait 1,4 Go libre.

## Sous le capot (noms des modules)

| Couche | Ce qu'on voit |
|---|---|
| Interface | Qt 6 + QML, **Lynx** (cadre d'interface de ByteDance), Chromium embarqué (CEF) pour les panneaux web |
| Moteur | `VECreator.dll` **350 Mo**, `cccreator.dll` 146 Mo, `videoeditor.dll` 49 Mo |
| Codecs | FFmpeg 7 (`avcodec-61`), AV1 (`SvtAv1Enc`, `dav1d`), **codecs maison** `ByteVC1`/`ByteVC2`, HEIF, JPEG XL, RAW |
| IA locale | **trois moteurs** : NVIDIA TensorRT (`nvinfer_lean`), Intel OpenVINO + NPU, Qualcomm QNN ; `lens.dll` 84 Mo (amélioration d'image), `speechsdk`, `rnnoise`, `Tracking` |
| Ressources | effets, filtres, polices, modèles **téléchargés à la demande** (`GeckoSDK`, `EffectPlatform`) |
| Traçabilité | **C2PA** (`tt_c2pa_sdk`), filigrane IA, anti-fraude (`metasecml`) |

Leçon : l'interface est légère, ce qui pèse c'est le moteur d'effets et l'IA embarquée.

## Les fonctions (version PC 6.6.1, sauf mention)

- **Projets et médias** : brouillons, dossiers, corbeille, import par QR depuis le téléphone (Pro), recherche dans
  les rushes par objet / phrase / personne, rangement auto par date, lieu, visage, enregistrement d'écran.
- **Timeline** : multipiste, calque libre (pas sur mobile), clips combinés et sous-projets, **multicam 4 ou 9
  caméras**, marquage auto du rythme, repères, dispositions et raccourcis personnalisables.
- **Vitesse et mouvement** : 0,1x à 100x, courbes, ralenti par flux optique, flou de mouvement, stabilisation,
  images clés partout, suivi (objet, visage, main, corps, caméra), **recadrage auto 16:9 → 9:16**.
- **Image** : masques, fond vert, fusion, détourage, **arrière-plan IA**, gomme IA, agrandissement du cadre par IA,
  super-résolution 2K/4K, rééclairage, retouche visage, corps, cheveux.
- **Couleur** : roues, courbes, HSL, LUT .cube/.3dl, correction et **assortiment auto**, tons de peau, Rec. 709 /
  2020 / HDR HLG et PQ.
- **Texte** : légendes auto (~100 langues), bilingues, mots-clés en évidence, émojis IA, **suppression des tics de
  langage**, paroles, export SRT, **graphiques animés**, rédacteur IA, script vers vidéo.
- **Son** : musique filtrée « usage commercial », **vérification des droits d'auteur**, synthèse vocale à émotions,
  **clonage de voix en 5 s**, isolation de la voix, séparation des instruments, **LUFS (TikTok −12, YouTube −14)**,
  musique IA, bruitages IA.
- **IA de montage** : vidéo longue → courtes (< 60 s, 60-90 s, 90 s-3 min), montage brut auto, AutoCut, assistant.
  EditPilot (montage par consigne, sept. 2026) : *tiers, non vérifié*.
- **IA générative** : avatars (dont avatar à ta ressemblance tiré d'une vidéo de 2,5 à 10 min), synchro labiale,
  doublage avec ta voix, photo qui parle, **mannequin IA** (vêtements portés), image → vidéo. Officiel 2026 :
  Seedance 2.5, Seedream 5.0, Nano Banana Pro, Gemini Omni, Video Studio, AI Design.
- **Effets et créateurs** : les utilisateurs publient effets, stickers et modèles, et peuvent les vendre.
- **Export** : jusqu'à 8K, 10 bits, HDR, H.264 / HEVC / AV1 / **ProRes 4444 alpha** ; publication directe TikTok
  et YouTube.
- **Nuage et marque** : espaces d'équipe, partage pour relecture avec commentaires, kit de marque (50 couleurs).

## PC, mobile, web (seulement ce qui a une source)

Calque libre : PC seul (lu) · AutoCut : PC + mobile, pas web (aide officielle) · modèles : surtout mobile
(officiel) · crédits IA : PC + web, pas mobile (tiers) · export : PC 8K/ProRes, mobile 4K 60 HDR (lu + App Store)
· prix différents selon l'appareil, voulu (aide officielle).

## Tout ce qui est payant (relevé du 2026-11-02, 473 libellés « argent » de la version 6.6.1)

**Le verrou est à l'export, pas à l'outil** : en gratuit on pose un élément Pro et on le voit dans l'aperçu ;
à l'export il faut payer, retirer l'élément ou accepter le filigrane (lu sur le PC + aide officielle
`capcut.com/help/why-prompted-to-purchase-capcut-pro`).

- **Export** : sans filigrane = Pro · projet contenant un élément Pro = Pro · 4K et 60 i/s = Pro (sur mobile,
  1080p et plus sur les vidéos longues) · « export illimité » = avantage Pro.
- **Ressources Pro** : modèles (dont script vers vidéo, certains achetables à l'unité), effets, filtres,
  transitions, stickers, textes, styles, polices et musiques premium. Musique « commerciale » gratuite mais filtrée.
- **Outils avec écran de paiement dédié dans la 6.6.1** : légendes automatiques, suppression d'arrière-plan,
  réduction du bruit, isolation de la voix, amélioration de la qualité, suppression des tics de langage. Aussi
  Pro : kit de marque, import par QR, partage pour relecture externe, stockage en ligne (0 en gratuit depuis
  août 2024 ; 100 Go dans la 6.6.1, 1 To aujourd'hui), suivi de mouvement (officiel). Super-résolution : compteur
  gratuit puis Pro.
- **IA en crédits, en plus de l'abonnement** : avatars (au temps d'apparition), voix clonée (aux caractères),
  remplacement de voix (à la seconde), doublage (par usage, 1re fois offerte), traduction vidéo (à la seconde),
  synchro labiale, agrandissement du cadre, images et vidéos générées, effets / stickers / textes IA, effets
  sonores et musique IA. Rédacteur IA et « vidéo longue en courtes » : compteur quotidien ou mensuel puis Pro.
- **Règles des crédits** : Pro 1 200/mois remis à zéro · Standard un quota plus petit · achetés valables 2 ans ·
  les plus proches de l'expiration partent d'abord · échec = rendus, arrêt en cours = perdus · anciennes
  « utilisations Pro » converties en crédits · sur ordinateur, on paie sur le web ou le téléphone.
- **Leviers** : essai 7 jours (carte, renouvellement auto), 3 jours à la 1re connexion, 30 jours sur offres ·
  parrainage 7 jours chacun par ami, jusqu'à 70 jours, sans carte · 1 à 6 mois avec les PC ASUS · concours
  hashtag et partage TikTok · Go offerts pour activer la sauvegarde · « plus de 80 fonctionnalités Premium ».

## Argent

Gratuit · Standard 9,99 $/mois (App Store) · Pro 19,99 $/mois, **179,99 $/an sur le web** et 89,99 $/an sur
l'App Store, 1 200 crédits/mois · Équipes dès 24,99 $/mois (officiel) · Ultra 79 $ (tiers). ⚠️ Une page officielle
de septembre 2026 appelle « Standard » la version gratuite : les noms de formules ne sont pas stables.

**Pour LA BOBINE (vague 4)** : même verrou à l'export (filigrane), IA en crédits parce que chaque usage nous coûte,
paiement Mobile Money, parrainage.

## Pour NEBULA

Refaire CapCut en entier n'a pas de sens (moteur de 350 Mo, IA multi-matériel, bibliothèque sous licence, TikTok
maison sœur). **Le trou** : partir du catalogue réel d'un commerçant (photos et prix lus à la source, méthode du
STANDARD) et sortir la vidéo TikTok en un geste, voix et sous-titres d'ici, léger pour la 3G, payé en Mobile
Money. Outils déjà là : Remotion, WaveSpeed, FFmpeg, HyperFrames.

## Sources

capcut.com/tools/desktop-video-editor · App Store id1500855883 · capcut.com/tools/capcut-apk-latest-version-android-download
· capcut.com/help/auto-cut-in-capcut · capcut.com/help/different-price-for-capcut-mobile-and-desktop ·
en.wikipedia.org/wiki/CapCut · pixflow.net/blog/capcut-2026-update (tiers).
