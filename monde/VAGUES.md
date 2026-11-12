# LE MONDE · le registre des vagues

> Mongazi, 2026-11-12 : « fais tout vague par vague et note-les pour ne rien
> oublier de ce qu'on se dit ».
>
> **Règle** : chaque demande de Mongazi entre ici **au moment où il la fait**,
> avec ses mots, sa vague et son état. On ne coche qu'après l'avoir vu marcher
> (contrôle vert ET capture regardée). ✅ fait · 🔨 en cours · ⏳ attend
> quelque chose · 🙋 attend Mongazi ou Hillary · 💤 plus tard.

---

## Vague 0 · Analyser avant de construire ✅ (2026-11-12)

- ✅ « analyses correctement mes propos… d'abord à 100 % avant de commencer » → `VISION.md`
- ✅ « n'oublie pas d'analyser en profondeur et à 100 % chaque élément ainsi que la vidéo » → planches toutes les 2 s + bande son transcrite (`VISION.md` § 2)
- 🔨 « regarde bien la vidéo… utilise un agent qui va l'analyser en profondeur » → agent lancé, rapport attendu dans `ANALYSE-VIDEO-REFERENCE.md`
- ✅ « analyse et recherche du code des repos open source » → `BRIQUES-LIBRES.md` (vérifié sur l'API GitHub)
- ✅ « gardes tout le déroulement d'un côté… pour créer un skill » → `DEROULEMENT.md`
- ✅ « donnes-moi tout ce que tu veux que je t'apporte » → `A-APPORTER.md`

## LE BUT · faire ACHETER 🔨 (Mongazi, 2026-11-12, en fin d'après-midi)

> « je suis allé voir, je vois toujours des Lego, pas des personnages, c'est tout brouillon et
> ils se rentrent dedans. Un des objectifs aussi, surtout, c'est que les gens viennent pour
> acheter : l'expérience doit donner envie au client d'acheter les produits ou services, donc
> ça doit être encore plus pro. On est archi loin du GTA que je t'ai envoyé et de GTA 6. »

Ce que j'ai vu en refaisant le tour dans son Chrome (2026-11-12, 16 h) :
- **les personnages sont des capsules** (le vrai modèle d'Afi existe, il n'est pas encore dans le salon) ;
- **les robes sont des photos collées sur des panneaux** (des silhouettes en carton), pas des vêtements ;
- **les étiquettes s'empilent** : six ou sept bulles à l'écran, dont une posée SUR la robe (« Le comptoir ») ;
- **la rue derrière la vitrine est un dessin** (façades plates, moto en boules) ;
- **les visiteuses ne s'évitent pas entre elles** : `pnj.js` ne contourne que le joueur ;
- **le salon met environ 30 s à s'ouvrir** sur ce PC.

Décisions de Mongazi, le même jour :
- ✅ « oui, télécharge les 7 » (les animations d'Afi sur Mixamo) ;
- **le décor reste en 3D vivante** : « je ne veux pas que ce soit juste des images figées, je veux
  que ça vive » (les panoramas 360° figés sont écartés) ;
- **scanner le vrai lieu = la voie des PROCHAINS clients qui ont un emplacement** : « j'avais pensé
  à filmer… mais Hillary n'en a pas » ;
- 🙋 **il envoie les images faites pour le salon** : elles deviennent le modèle à atteindre (et une
  source de matières), pas un décor plat.

- 🔨 **« même la navigation, et les boutons qui sont trop gros et trop lambda : il faut invoquer
  Impeccable pour rehausser cette qualité, et les polices, etc. C'est trop lambda, ça ressemble à
  un salon de couture et une immersion 3D de 200 dollars ; le but ultime, c'est que ça ressemble à
  une immersion 3D valant 20 000 dollars minimum »** (2026-11-12) → refonte de l'interface
  (navigation, repères, boutons, typographie, bulles de dialogue, fiche, sac, cadran) par le skill
  Impeccable ; **l'étalon : 20 000 $**.

- ✅ **direction de l'interface choisie par Mongazi : « Les enseignes peintes »** (tirage Impeccable,
  `seed:677424d6dda1b16c`) : chaque mot peint à la main comme l'enseigne d'un atelier de Cotonou, au
  niveau d'une maison de couture ; nuancier fermé de 5 pots. Fiche produit : `PRODUCT.md`.
- ✅ **les 7 animations d'Afi téléchargées** (2026-11-12, 17 h 28) : `_partage\immersive  store 3D\personnages\afi\afi-{attendre,marcher,parler,saluer,hocher,reflechir,regarder}.fbx` (8,5 Mo ; seule `attendre` porte le corps ; `marcher` = *Female Walk* sur place)
- 🙋 **« faut lancer Unreal Engine »** (2026-11-12) → le moteur n'est pas installé (installation sur `C:` annulée à 13 h 59) ; lanceur rouvert sur la page Unreal : **choisir `D:\Epic Games`**. ⚠️ ce PC (8 Go, Intel HD 5500) risque de ne pas ouvrir l'éditeur.

Règle qui en sort : **chaque choix se juge à « est-ce que ça donne envie d'acheter ? »**. Le
produit est le héros de chaque plan ; le décor, les personnages et les jeux le servent.

## Vague 1 · La maquette jouable 🔨 (2026-11-12)

- ✅ « un salon de couture 3D ultra immersif… à la 1re personne… moderne, lumineux, au Bénin »
- ✅ « un comptoir au fond, et vers l'entrée plusieurs expositions de ses réalisations » → 5 podiums, 7 pièces, + mur des créations (les 19 du catalogue, lues dans la vitrine)
- ✅ « des PNJ avec qui on peut interagir… des réponses possibles à donner au choix » → 3 visiteuses, réponses en croix
- ✅ « il peut y avoir 3 personnes, donc le 1 et le 2 » → Afi (Paris), Sènami (Cotonou, TikTok), Maman Sènami
- ✅ « les personnages doivent paraître intelligents, se parler entre eux, on voit ce qu'ils se disent, ils ne font pas les mêmes choses » → agendas, 15 conversations, sous-titres nommés
- ✅ « les conversations comme dans Horizon Zero Dawn »
- ✅ « au comptoir Hillary… on pourra lui parler… elle recommande… un article s'affiche comme dans un jeu… panier… c'est tout ?… c'est parfait, valide ta commande ici… un cadran… WhatsApp »
- ✅ « le jour, la nuit passeront là-bas aussi » → heure réelle de Cotonou
- ✅ « s'il pleut au Bénin, il pleut dans cette réalité virtuelle » → météo réelle (MET Norway)
- ✅ « Point & Click 3D… points lumineux au sol ou sur les éléments… le personnage s'y déplace automatiquement… fluide »
- ✅ « on pourra regarder partout… comme dans Street View »
- ✅ « la majorité des gens utilisent des mobiles… avec un pouce… une zone touchable (habits, affiche, clients inconnus, comptoir, sortir, entrée)… le point lumineux avec le nom » → repères au pouce, « Une visiteuse » tant qu'on ne lui a pas parlé
- ✅ « si elle doit organiser des événements… les affiches aux murs… les gens pourront aller regarder, avoir des infos » → mur des événements, lu dans `faits.json` (vide = « Prochainement », rien d'inventé)
- ✅ « un des PNJ peut évoquer… sur son TikTok… une vidéo qui l'a choqué… s'abonner… son TikTok peut s'afficher » → prêt, **caché tant que le compte n'est pas dans `faits.json`** (🙋 le compte)
- ✅ « il faut prendre en compte les tailles : elle fait 1,68 m, les autres prends en compte toi-même » → Hillary 1,68 · Afi 1,71 · Sènami 1,64 · Maman 1,62
- ✅ « quand on parle avec des gens, ce sont leurs corps mêmes qui bougent… pas en mode des images » → portraits retirés, gestes de parole
- ✅ « ils doivent se mouvoir, vraiment fluides et authentiques : poser une question, écouter la réponse, répondre » → gestes selon le ton (question : paumes ouvertes ; écoute : hochements) · la vraie fluidité viendra de la vague 3
- ✅ « le viewer a des réponses prédéfinies, on pourrait être tenté de tout choisir et apprendre tout sur la boutique : qui l'a créée, la cliente, les réalisations, la vision, absolument tout » → réponses explorées cochées ✓, nouvelles ✦, **le carnet** (« 7 sur 12 ») ; histoire, vision, sens du « M. » : 🙋 les mots d'Hillary (questionnaire)
- 🔨 « il doit y avoir des bruits ultra réalistes, ouverture de porte, cherche des repos de bruitage libres » → voir vague 1 bis
- ✅ contrôle automatique : une visite complète jusqu'au message WhatsApp, au franc près (`_qc.py`)
- ✅ **le contrôle donne 48/48** (2026-11-12) : Afi restait plantée à 55 cm du joueur, son chemin passait par sa position et le réflexe d'évitement la repoussait ; corrigé (chemins qui évitent le joueur, arrivée à 1,50 m)
- ✅ « nous, on ne voit pas le bras » → décision : **le visiteur ne voit jamais ses propres bras** (dans la référence, on voit les mains du joueur payer ; pas chez nous)
- 🔨 « il faut être un peu plus proche ; quand on voit quelqu'un au loin et que le point s'affiche, on va vers lui avec l'animation, ensuite il y a des options : parler, etc., et là la discussion commence » → elle s'arrête et se tourne dès qu'on la choisit, on marche jusqu'à 1,30 m, puis **Parler · Saluer · Laisser** ; Hillary : **Parler · Me conseiller / Valider ma commande · Laisser**
- ✅ le rapport de l'agent (`ANALYSE-VIDEO-REFERENCE.md`, 52 procédés mesurés) a corrigé quatre réglages : **champ de vision 75° en horizontal** (au lieu de ~98°), **yeux à 1,55 m**, **un pas tous les 0,68 m avec la tête qui descend à chaque pas** (au lieu de 3,7 pas/s désaccordés), **le dialogue avance seul** (toucher pour aller plus vite) ; et Hillary **accueille les mains sur le comptoir** (les bras croisés, c'est l'impatience)

- ✅ « en attendant, avances » (2026-11-12) → priorités de l'analyse vidéo, sans rien télécharger : **carte de titre** à l'entrée (6 s, heure et météo réelles), **ta réponse reprise sous « Toi »**, **le regard d'Hillary** qui alterne sa tâche et toi, **le sac magenta sur le comptoir** dès la première pièce, **l'accroche** (Afi vient dans les premières secondes)
- ⏳ restent de l'analyse : fondus pour les longs trajets, exposition qui réagit à la porte, têtes qui se tournent ensemble vers l'écran, passants derrière la vitrine, Hillary qui lève et retourne la pièce

## Vague 1 bis · Les vrais sons 🔨

- 🔨 bruitages libres de droits, vérifiés (licence) : porte, pas sur carrelage, tissus, sac, cintres, machine à coudre, rue de Cotonou, pluie sur la tôle
- 🔨 sons **placés dans l'espace** (la porte s'entend du côté de la porte, les pas d'une visiteuse viennent d'où elle marche)
- ✅ **le son de la pièce** (climatiseur), **la machine à coudre de l'atelier** placée dans l'espace, **la rue qui monte d'environ 10 dB et s'éclaircit dehors**
- ✅ 19 bruitages enregistrés, CC0, 116 Ko (Kenney) : porte, pas, tissus, sac, interface → `SONS.md`
- ⏳ pluie sur la tôle, rue de Cotonou, machine à coudre, tonnerre : encore synthétisés ; 🙋 idéal = **un vrai enregistrement de 2 min devant une vitrine à Cotonou** et 30 s de **la vraie machine d'Hillary**

## Vague 2 · Le salon habillé ⏳

- ⏳ « qualité Call of Duty Korea et GTA 6 » → la sensation : lumière précalculée jour et nuit, matières, densité (dit à Mongazi : pas la qualité console dans un téléphone en 3G)
- ⏳ « utilise Blender, télécharge Unreal Engine… je dirai le 1 [navigateur] mais installe quand même Unreal pour la création » → lanceur installé ✅, compte Epic créé par Mongazi ✅, 🙋 **le moteur à installer sur D:** ; ⚠️ ce PC (8 Go, Intel HD 5500) risque de ne pas l'ouvrir
- ⏳ « il faut que tu utilises Unreal Engine pour la construction aussi » → un plan commun (`plan.json`) lu par le navigateur ET par un script Unreal ; script à écrire, testable une fois le moteur installé
- ✅ script écrit : `unreal/construire_lieu.py` (pièce, dôme, podiums, comptoir, étagères, lumières, **une caméra de cinéma par point** pour la bande-annonce TikTok) · ⚠️ pas encore éprouvé
- ⏳ « la construction, niveau fluidité, tu dois normalement la faire aussi avec Unreal Engine » → Unreal construit, éclaire et filme ; la fluidité DANS LE TÉLÉPHONE reste celle du moteur du navigateur (Unreal ne tourne pas dans un navigateur sans un serveur payé par visiteur)
- 🙋 « je vais t'envoyer une réalisation de jeu faite dans Unreal Engine, c'est beau et fluide, avec des mouvements de caméra immersifs et réalistes » → à analyser comme la référence Call of Duty (caméra, fluidité) dès réception
- 🙋 « concernant Epic, c'est fait » → **le moteur n'est pas encore sur le disque** au 2026-11-12 (vérifié : ni `UE_…` sur C ni sur D, un composant d'installation Epic tournait) : finir l'installation sur `D:`
- ⏳ « l'environnement en 3D, les nuages beaux comme la météo » → ciel physique et nuages (three-geospatial)
- 🙋 les 11 vues du salon et la vue par la fenêtre (Nano Banana Pro, `PROMPTS-NANO-BANANA.md` D1 à D11)
- 🙋 ses vrais tissus photographiés à plat (A1), ses outils (A2)

- 🔨 « LE GRAPHISME ET LA QUALITÉ doivent ressembler extrêmement à Call of Duty Korea, GTA 6… c'est un des objectifs principaux » (2026-11-12) → **piste 1 faite** : lumière photographiée (HDR), sol en vrai marbre, plâtre, chêne, velours scannés, plantes, fauteuils, table basse, vases et suspensions scannés (**Poly Haven, CC0**, 5,3 Mo, chargés APRÈS l'ouverture), tons AgX · ⏳ piste 2 : « salon photo 3D » depuis les panoramas P1 à P4 (🙋 à générer) · ⏳ piste 3 : Unreal diffusé en vidéo (démonstration) · ⏳ le plus gros écart restant : **les personnages** (vague 3)
- 🙋 « télécharge Unreal depuis le navigateur », « prends le contrôle du PC » → la prise de contrôle de l'écran n'existe pas dans cette session (il faut l'application Claude pour ordinateur, option Computer use) ; lanceur ouvert sur la page Unreal par lien interne, installation à finir par Mongazi sur D:

## Vague 3 · Les personnages vivants ⏳

- 🙋 « je veux que Hillary soit dedans avec une véritable ressemblance… comme les personnages des jeux » → son accord écrit + 8 à 10 photos + planche
- ✅ les planches des trois visiteuses, **générées le 2026-11-12** (Cloudflare Workers AI, gratuit) : `lieux/hillary-m-styl/personnages/` · Afi brun moyen, Sènami brun clair, Maman Sènami brun très foncé, pose prête à animer · ⚠️ celle de Sènami montre deux fois le dos au lieu du profil droit · ⏳ la 3D attend WaveSpeed. Demande d'origine : (« les PNJ je te laisse gérer, ça doit être des Noires, claires de peau ou noires ») ; carnations déjà posées dans la maquette
- ✅ « le principal c'est Hillary, je veux qu'elle soit reconnaissable » → consignes B1 à B4 refaites : fidélité stricte (pas de peau éclaircie), pose prête à animer, expressions, **ses gestes filmés**
- ⏳ « les prompts tu vas les modifier ? on doit créer les personnages pour que tu les modélises en 3D et les rendes vivants à 100 % » → consignes refaites pour un squelette d'animation + **vidéos de ses vrais gestes** (capture de mouvement)
- ⏳ squelette, animations (Mixamo et capture), lèvres synchronisées sur la voix (Rhubarb), voix (la sienne si elle accepte, sinon Chatterbox)
- 🔨 « je ne veux pas de Lego, je veux de vrais personnages 3D » + **« voie gratuite »** (2026-11-12) → jeton Hugging Face rangé (compte « mongazi », lecture seule) · ✅ **Afi en vraie 3D** (`personnages/afi.glb`, TRELLIS.2, cohérente sous 4 angles, pose prête pour Mixamo ; 1 m et 115 000 triangles : à mettre à 1,71 m et à alléger) · ⏳ Sènami et Maman : **le compte gratuit limite le NOMBRE de calculs par jour** → demain, en 2 calculs par personnage (détourage fait sur le PC) · ✅ `_outils/glb_vers_obj.py` → `afi-mixamo.zip` · 🙋 **Mixamo** : se connecter (compte Adobe), puis squelette et animations
- 💤 « IA plus tard » : Hillary qui répond librement (avec le garde-fou des prix de LE STANDARD)
- 🔨 **« on doit appliquer les âges aussi dorénavant, moi j'ai 28 ans par exemple, Hillary 26 ans, donc jeune encore, pas trop vieux »** (2026-11-12) → **Hillary 26 ans** (fait) · Afi **29** (partie il y a dix ans, à 19 ans) · Sènami **21** (une adulte, pas une adolescente) · Maman Sènami **47** (pas une grand-mère) · posés dans `lieu.js` (`age`), dans la consigne B1 d'Hillary et dans `personnages/CONSIGNES.md` (consignes gardées mot pour mot) · ⚠️ **les premières images ne tenaient pas l'âge** : Maman Sènami faisait 60-65 ans, Sènami 16-17 ; Afi (≈ 30) passe · ⏳ **refaire les images de Sènami et de sa mère AVANT leur 3D** : quota gratuit de Cloudflare épuisé ce jour-là (10 000 « neurones »), remis à zéro à 1 h, heure du Bénin
- 🔨 **Afi a son squelette sur Mixamo** (2026-11-12, après-midi) : modèle envoyé par l'extension Chrome, 9 repères posés, squelette standard (65 os), marche vérifiée dans l'aperçu · `FBXLoader` copié dans `socle/vendor/three/addons/` (r180, avec `fflate` et `NURBSCurve`) · 🙋 **les 7 téléchargements attendent l'accord de Mongazi**

## Vague 4 · Ses robes en 3D sur mannequins ⏳

- ✅ « les robes seront affichées sur les mannequins en 3D, ses vraies réalisations… un super prompt… sans erreur de pixel » → `PROMPTS-ROBES-3D.md`
- 🙋 les 18 planches (une conversation Nano Banana par pièce)
- ⏳ planche → 3D (WaveSpeed, 🙋 recharger ≈ 40 $) → **validation d'Hillary pièce par pièce** ; la fiche garde la vraie photo

## Vague 5 · La finition et la mise en ligne ⏳

- ⏳ caméra de cinéma, niveaux de qualité, poids pour la 3G, relais météo sur Cloudflare, adresse en ligne, contrôles
- ⏳ « chaque salon a son lien pour y accéder »

## Vague 6 · La ville 💤

- 💤 « un monde virtuel où entreprise, propriété, salon de beauté… comme une virtualisation du monde physique… une sorte de Google Maps, mais virtuel, où l'on peut vraiment se mouvoir »
- 💤 « après je créerai pour Grain d'Esthétique pour ma mère » → le 2e lieu, même socle
- 💤 la carte de Cotonou en 3D (OpenStreetMap + MapLibre), chaque lieu à sa vraie place ; 🙋 le quartier de chaque atelier
- 💤 voir les autres visiteurs (multijoueur)

## Vague 7 · Le back-office du lieu 💤 (demandé le 2026-11-12)

> « il faut qu'on fasse une sorte de back-office pour les clients, donc pour
> Hillary aussi, pour qu'elle puisse faire des modifications : changer de
> tenue, afficher certaines choses réelles ; s'il y a un événement, afficher
> l'affiche dans son salon ou à sa porte d'entrée ; changer ses robes, comme
> une vraie boutique ; pour les périodes, des décorations… plein de choses
> auxquelles tu réfléchiras, qu'on améliorera progressivement »

Premières réflexions (à affiner) :
- **une page sur son téléphone**, pas un logiciel : elle se connecte, voit son salon, change, prévisualise, publie ;
- **les expositions** : quelle pièce sur quel podium, la pièce du moment au centre ;
- **les affiches** : elle envoie l'affiche et choisit où la poser (mur, **porte d'entrée**, vitrine) et **jusqu'à quand** ⚠️ une affiche périmée se retire seule (leçon de Grain d'Esthétique : la promo de la fête des Pères restée en ligne) ;
- **les décorations de saison** : des « habits » du salon qu'on active par période (Noël, Nouvel An, Tabaski, fête des mères, Saint-Valentin, Vodun Days, fête de l'indépendance du 1er août…), avec date de début et de fin ;
- **sa tenue au comptoir** : une de ses pièces 3D ;
- **ses nouvelles** : la dernière vidéo TikTok, l'annonce du jour, ses horaires ;
- ⛔ **les prix restent ceux du catalogue** : le back-office modifie la même source que le site, jamais une deuxième vérité ;
- **toute modification est annulable**, et le cockpit NEBULA voit tout (règle « back-office partout »).

## Vague 8 · L'économie du monde 💤

- 💤 « dans le futur, pour y rester, il faudra payer une sorte de loyer »

---

## Ce qui attend Mongazi ou Hillary (le résumé)

| Quoi | Pour quelle vague | Où c'est expliqué |
|---|---|---|
| installer le moteur Unreal sur `D:` | 2 | `A-APPORTER.md` |
| le compte TikTok d'Hillary et sa dernière vidéo | 1 | `QUESTIONNAIRE-HILLARY.md` |
| le questionnaire (ses mots, son histoire, sa vision, le « M. ») | 1 et 3 | `QUESTIONNAIRE-HILLARY.md` |
| ses photos + son accord écrit (visage, voix) | 3 | `PROMPTS-NANO-BANANA.md` B |
| les vidéos de ses vrais gestes | 3 | `PROMPTS-NANO-BANANA.md` B4 |
| ~~les planches des trois visiteuses~~ : **je m'en charge** (Mongazi : « les PNJ je te laisse gérer ») | 3 | `PROMPTS-NANO-BANANA.md` C |
| les 11 vues du salon | 2 | `PROMPTS-NANO-BANANA.md` D |
| les 18 planches de ses robes | 4 | `PROMPTS-ROBES-3D.md` |
| recharger WaveSpeed (≈ 40 $) | 3 et 4 | `A-APPORTER.md` |
| un téléphone Android d'entrée de gamme pour tester | toutes | `A-APPORTER.md` |

## Ce que j'ai trouvé en route (hors salon)

- ⛔ **Sur le site en ligne d'Hillary**, commander l'**Ensemble Jean** ou la **Robe Émeraude** affiche « Type de vêtement introuvable » à l'étape des mesures : leur jeu de mesures `haut_jupe` n'existe pas. 🙋 Il faut qu'Hillary dise quelles mesures elle prend pour une jupe ; rien n'est corrigé sans elle.
