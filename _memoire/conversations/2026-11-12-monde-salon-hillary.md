# 2026-11-12 · LE MONDE : le salon 3D d'Hillary, analysé avant construction

## La demande
Mongazi veut un salon de couture 3D « ultra immersif » dans l'univers d'HILLARY M. STYL : moderne, lumineux, béninois ;
comptoir au fond (Hillary, ressemblante, qui conseille et vend), expositions de ses réalisations en 3D vers l'entrée,
visiteurs PNJ qui se parlent et posent des questions à choix (style *Horizon Zero Dawn*), mur d'événements, son TikTok,
panier, « c'est tout ? », « valide ta commande ici », cadran, WhatsApp. Jour, nuit et pluie synchronisés sur
Cotonou. Qualité visée : *Call of Duty* (supérette coréenne de MW4) et *GTA 6*. Déplacement point & click par
points lumineux, regard libre façon Street View. Premier lieu d'un **monde virtuel calqué sur Cotonou** (chaque
commerce a son lien ; Grain d'Esthétique ensuite ; un loyer plus tard). Garder tout le déroulement pour un skill.
Consigne : **analyser à 100 % avant de commencer**, puis dire tout ce qu'il doit apporter.

## Ce qui a été analysé
- La vision d'Hillary (`ff6cc3de-….jpg`) : podiums ronds blancs, mannequins blancs sans tête, plafond courbe à ligne
  dorée, sol crème qui reflète. Ses mannequins règlent aussi la question des femmes réelles qui portent ses pièces.
- La vidéo *Call of Duty* : une image toutes les 2 s + transcription. Procédés retenus : course confiée dès l'entrée,
  nom flottant, choix en croix (avec « mentir »), PNJ qui agissent ensemble, PNJ guide, article montré, écran mural
  commenté, invite « PAYER » posée sur place, écran de paiement avec QR, sac visible, sortie vers la rue.
- Les vidéos de Brendan Jowett : Claude pilote Unreal et Blender par script ; la version « 100 heures » = 54 agents,
  25,8 milliards de tokens, environ 14 000 $ d'API, 19 jours ; lui-même avoue les zones bâclées.
- Le PC : i5-5300U 2 cœurs, 8 Go (1,8 libre), Intel HD 5500, 38 Go libres sur C, 60 sur D.
- WaveSpeed : chaîne 3D complète (photo vers 3D 0,20 à 0,36 $, squelette 0,30 $, animation 0,42 $) ; solde 0,04 $.
  Higgsfield : 0 crédit.
- Faits vérifiés en ligne : Ready Player Me fermé le 31/01/2026 ; Open-Meteo gratuit seulement en non commercial
  (donc MET Norway) ; Epic recommande 32 Go et 8 Go de mémoire graphique ; couverture 3D de Google sur Cotonou non confirmée.

## Ce qui a été dit à Mongazi
- La qualité *Call of Duty* dans un téléphone en 3G : non ; la sensation (lumière précalculée jour et nuit, densité,
  sons, caméra, interface) : oui.
- Unreal : inutilisable sur ce PC, et sans sortie navigateur hors *Pixel Streaming* (un serveur GPU par visiteur).
- Les PNJ sont des visiteurs, **pas de fausses clientes satisfaites** ; tout ce qu'ils disent est vrai (catalogue LU
  dans `PIECES`, vidéo TikTok réelle, événements réels).
- Les pièces en 3D sur mannequins, **validées une à une par Hillary**, la fiche montre la vraie photo.
- Hillary en 3D : avec **son accord écrit**, et validée par elle.

## Décisions de Mongazi
Moteur navigateur (Three.js), **Unreal installé quand même pour la création** · PNJ écrits d'abord, IA plus tard ·
**trois visiteuses** (lu comme : la Parisienne, la jeune de Cotonou fan de TikTok, sa mère ; à confirmer) · mesures au
choix du client.

## Fait
- `monde/VISION.md`, `monde/A-APPORTER.md`, `monde/DEROULEMENT.md`.
- Lanceur Epic installé (`winget`), le moteur attend la connexion Epic de Mongazi (sur `D:`).

## La suite
Vague 1, la maquette jouable (ne demande que ses réponses, déjà données) : au feu vert de Mongazi.

## La suite : la maquette jouable (même journée)

Feu vert de Mongazi (« continue où tu en étais »). Construit dans `monde/` :
- un **socle** réutilisable (moteur, ciel réel de Cotonou, déplacement « point & click » + regard Street View,
  repères au pouce, options près d'une personne, personnages animés, PNJ à agenda, dialogue en croix, carnet,
  boutique jusqu'à WhatsApp, sons placés dans l'espace) et le **lieu d'Hillary** construit depuis `plan.json` ;
- le catalogue **lu** dans la vitrine par le lecteur de LE STANDARD (19 fiches, 12 pays, 6 jeux de mesures) ;
- `_qc.py` joue une visite complète, du trottoir au message WhatsApp contrôlé au franc près.

Demandes ajoutées en cours de route, toutes dans **`monde/VAGUES.md`** avec ses mots : mobile d'abord et repères au
pouce · tailles (Hillary 1,68 m) · les corps parlent, pas des images · question, écoute, réponse · tout choisir
apprend tout (le carnet) · sons réalistes libres · tout noter vague par vague · le visiteur ne voit pas ses bras ·
s'approcher, puis des options, puis la discussion · un back-office pour qu'Hillary change son salon (vague 7) ·
Unreal pour la construction · « les PNJ je te laisse gérer, des Noires claires ou foncées de peau » · Hillary
reconnaissable (consignes refaites, ses gestes filmés).

Un agent a analysé la vidéo de référence (`monde/ANALYSE-VIDEO-REFERENCE.md`, 52 procédés mesurés) : quatre
réglages corrigés (champ de vision, hauteur des yeux, cadence des pas, dialogue qui avance seul).

Trouvé en route : sur le site EN LIGNE d'Hillary, l'Ensemble Jean et la Robe Émeraude affichent « Type de vêtement
introuvable » aux mesures (jeu `haut_jupe` inexistant). Rien corrigé sans Hillary.

Unreal : lanceur installé, compte Epic créé par Mongazi, **moteur pas encore sur le disque** au soir.

## Le soir : le graphisme et les vrais personnages

- Mongazi : « le graphisme et la qualité doivent ressembler extrêmement à Call of Duty Korea, GTA 6, c'est un des objectifs principaux » → dit franchement : la qualité console dans un téléphone en 3G n'existe pas ; trois pistes (matières et lumière réelles dans le navigateur, faite ; « salon photo 3D » depuis des panoramas, à venir ; Unreal diffusé en vidéo, pour une démonstration).
- « Je ne veux pas de Lego, je veux de vrais personnages 3D » + « voie gratuite » → Afi en vraie 3D (TRELLIS.2, Hugging Face) ; Mixamo pour l'animer (il s'y est connecté) ; Mesh2Motion en alternative sans compte.
- « Prends le contrôle du PC », « télécharge Unreal » → pas de contrôle d'écran dans le terminal ; Unreal installé par lui sur `C:`, coincé faute de place.
- « Mets tout en mémoire… pour se retrouver au poil près » → `monde/REPRENDRE-ICI.md`.
