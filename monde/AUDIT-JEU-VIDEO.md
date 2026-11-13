# LE MONDE · l'audit d'un expert en animation 3D et en jeu vidéo

> Demandé par Mongazi le 2026-11-12 : « mets-toi dans la peau d'un expert en animation 3D et en
> création de jeu vidéo : qu'est-ce qui peut encore être optimisé et apporté ? » (hors relecture
> Impeccable, qui couvre l'interface). Écrit d'après le code tel qu'il est ce soir-là.
> Chaque point dit **ce qu'on voit aujourd'hui**, **ce que ferait un studio**, son **effet** et son
> **coût** (S = une session, M = deux ou trois, L = une vague entière), et **ce qui dépend de Mongazi**.

---

## 1 · Les personnages : le plus grand écart (c'est là que l'œil décroche)

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| Trois personnages sur quatre sont des capsules | Sènami, Maman Sènami et Hillary en vraie 3D, par la même chaîne qu'Afi (image → TRELLIS.2 → Mixamo) | énorme | M (quota du jour) · 🙋 photos et accord d'Hillary |
| Visage figé : ni clignement, ni regard, ni lèvres | Clignements aléatoires (3 à 6 s), petits mouvements d'yeux (saccades), regard qui croise le visiteur ; lèvres calées sur le texte (visèmes tirés des syllabes, ou Rhubarb sur une vraie voix) | énorme : c'est ce qui rend « vivant » | M (demande un visage riggé : blend shapes) |
| Une seule animation par état, la même pour toutes | Plusieurs variantes par état (3 « parler », 3 « écouter », rire, hausser les épaules), tirées au hasard, décalées dans le temps par personne : jamais deux gestes identiques en même temps | fort | S |
| Elle démarre et s'arrête d'un coup, pivote sur place en glissant | Animations de démarrage, d'arrêt et de demi-tour (Mixamo : *Start Walking*, *Stop Walking*, *Turn 90*), vitesse de pas calée sur le déplacement réel, pieds qui ne glissent pas (IK des pieds) | fort | M |
| La tête seule suit le regard | Chaîne cou + tête + yeux, avec limites et retard naturel ; le buste accompagne au-delà de 40° | moyen | S |
| Les vêtements sont rigides | Mouvement secondaire : jupes, boubou, gele et cheveux sur « os ressorts » (spring bones), ou drapé précalculé dans Blender | fort sur les robes | M |
| Peau : texture générée qui garde l'éclairage de la photo | Peau « délitée » (lumière retirée de la texture), légère diffusion sous la peau, reflet spéculaire juste | fort | M |
| Gestes de métier absents | Hillary qui plie un tissu, déroule son mètre ruban, pique à la machine ; Sènami qui se filme (TikTok) ; Maman qui palpe le wax ; s'asseoir dans les fauteuils | fort (crédibilité du lieu) | M · 🙋 idéal : les vrais gestes d'Hillary filmés |
| Afi : 88 000 sommets, chaque visiteuse coûte autant | Niveaux de détail (LOD) : 30 000 près, 8 000 de loin ; animations compressées | indispensable au téléphone | S (Blender, installé) |

## 2 · La caméra et le ressenti (le « game feel »)

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| On se déplace de point en point | Garder les points (simple pour un enfant) **et** ajouter « toucher le sol pour y aller » sur un maillage de navigation (recast-navigation, MIT) | fort | M |
| Caméra posée, mouvement mécanique | Ressort-amortisseur sur la rotation, micro-balancement « caméra à l'épaule » mesuré sur la référence (0,1 à 0,3 px au repos), inclinaison légère dans les virages | fort (sensation Call of Duty) | S |
| Les conversations sont filmées comme le reste | Mise en scène : léger rapprochement sur celle qui parle, **profondeur de champ** sur son visage (le fond se floute), regard qui va de l'une à l'autre | énorme (sensation de film) | S à M |
| Un long trajet se fait en marchant | Fondu « clignement » au-delà de 6 m (la référence le fait) | moyen | S |
| Aucune vibration | Petite vibration au toucher sur Android (`navigator.vibrate`) | faible, gratuit | S |

## 3 · La lumière et le rendu

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| Aucune ombre portée nulle part | Une ombre douce sous les personnages (ombre de contact, ou un seul projecteur qui projette), les objets posés par la lumière cuite | fort | S à M |
| Lumière en temps réel seulement | **Lumière cuite dans Blender** (rebonds, ombres douces, occlusion), sondes de lumière pour que les personnages « baignent » dans la même lumière que le décor | énorme | L (Blender installé, décor déjà exporté) |
| Les faisceaux éclairent sans se voir | Une légère brume dans les cônes des projecteurs et dans les rayons des vitrines (volumétrie discrète) : c'est la signature « luxe » | fort | M |
| Le marbre reflète par un miroir plat | Reflets plus justes (sonde cubique cuite une fois, rugosité variable) | moyen | S |
| Tissus et robes en matière simple | Matière **tissu** (reflet de velours/satin, « sheen »), verre avec transmission, laiton avec vernis | fort sur les produits | S |
| Exposition fixe | Adaptation de l'œil en passant dehors ↔ dedans, étalonnage par heure du jour | moyen | S |

## 4 · Les produits : ce qui fait vendre

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| **Les robes sont des photos sur des panneaux** | **Les robes en 3D sur les mannequins**, avec leur matière qui bouge un peu ; la fiche garde la vraie photo | énorme : c'est le moment « wow » ET la vente | L · 🙋 les 18 planches (`PROMPTS-ROBES-3D.md`), puis validation d'Hillary pièce par pièce |
| On ouvre une fiche | Mode « examiner » : la robe se détache, tourne au doigt, gros plan sur le tissu, puis la fiche | fort | M |
| Rien ne met en scène l'arrivée d'une pièce | Chorégraphie de lumière : au premier regard sur une robe, son projecteur monte doucement | fort, peu cher | S |
| Pas de souvenir à partager | **Mode photo** : une belle image de la robe dans le salon, à envoyer sur WhatsApp ou TikTok (avec le lien du salon) | fort (bouche-à-oreille) | M |

## 5 · Le décor et la vie du lieu

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| La rue est dessinée (façades plates, moto en boules) | Une **vraie rue** capturée (vidéo iPhone → Gaussian splat) ; à défaut, façades photographiées, zémidjans et passants animés derrière la vitrine | énorme dehors | M · 🙋 la vidéo d'une rue de Cotonou |
| Salon propre et un peu vide | Densité : cintres, rouleaux entamés, échantillons, magazines, un ruban par terre, une tasse sur le comptoir ; de petites imperfections (le réalisme vient de l'imperfection) | fort | M |
| Les bâtiments d'en face sont des aplats | « Intérieurs simulés » derrière leurs fenêtres (une image de pièce en parallaxe), lumières qui s'allument le soir | moyen | S |

## 6 · Le son

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| Pas, tissus et porte : bruitages libres, placés dans l'espace | Pas différents selon le sol (marbre, tapis), froissement de tissu calé sur les gestes (événements d'animation), réverbération de la pièce | moyen | S |
| Personne n'a de voix | Voix d'Hillary (la sienne si elle accepte, sinon une voix clonée avec accord), voix des visiteuses, lèvres synchronisées | énorme | M · 🙋 accord et enregistrements |

## 7 · La performance au téléphone en 3G (la condition de tout le reste)

| Aujourd'hui | Ce que ferait un studio | Effet | Coût |
|---|---|---|---|
| Environ 30 s d'ouverture sur ce PC ; modèles et textures bruts | Chaîne d'assets : glTF + meshopt (géométrie), textures KTX2/Basis (mémoire graphique divisée par 4 à 6), niveaux de détail, chargement par étapes : la rue tout de suite, l'intérieur ensuite | indispensable | M |
| Beaucoup d'objets séparés | Fusion de la géométrie fixe, instanciation des objets répétés (rouleaux de wax, cintres) : moins d'appels de dessin | fort | S |
| Quelques calculs recréés à chaque image | Zéro allocation par image (repères, points de passage) : moins de saccades | moyen | S |
| Aucune mesure fiable au téléphone | Compteur d'images et temps GPU sur un vrai Android d'entrée de gamme ; cible 30 i/s au téléphone, 60 à l'ordinateur | indispensable | S · 🙋 un Android d'entrée de gamme |

## 8 · Le jeu : le moment « wow » et la boucle qui fait acheter

- **Une ouverture cinéma de 8 secondes** : la caméra avance lentement de la rue vers l'enseigne, la musique monte, la porte s'ouvre, les projecteurs s'allument un à un sur les robes. Coût S, effet énorme sur la première impression (et sur le commerçant qui regarde).
- **Une boucle claire** : découvrir → apprendre (le carnet) → choisir (Hillary conseille) → acheter (sac, commande). Chaque étape a sa petite récompense visuelle et sonore.
- **Le visiteur qui revient** : Hillary le reconnaît (« Re-bonjour ! »), et lui montre les nouveautés.
- **Les saisons et les événements** pilotés par le back-office (vague 7).

---

## Avancement

- ✅ **Vague 1 · l'ouverture cinéma (2026-11-13)** : travelling de la rue au trottoir (7,5 s, il attend
  que le salon soit chargé), immeuble au-dessus de la boutique avec fenêtres aux rideaux éclairés le soir,
  ciel jour et nuit avec la lueur de la ville, façade anthracite, enseigne en lettres lumineuses (le logo
  détouré dans la page), filet de lumière sous le linteau, portes vitrées qui coulissent, musique qui
  monte, projecteurs qui s'allument un à un, Afi qui attend 5 s puis s'arrête à 1,60 m, carte de titre
  au-dessus des sous-titres, point de porte masqué quand on la franchit. QC 52/52, filmé de nuit et de jour.
- 🟡 **Vague 2 · des personnages qui vivent (2026-11-13, partielle, `b271315`)** : Afi a 13 animations
  (variantes de parole et d'attente tirées au hasard, démarrage et arrêt joués une fois, pieds qui
  piétinent quand elle pivote, regard cou + tête, gestes qui changent seuls). **Reste** : Sènami et sa
  mère en 3D (Mongazi les génère lui-même, consignes dans `personnages/CONSIGNES.md`), Hillary (ses
  photos et son accord). ⛔ Pas de clignement sur un modèle TRELLIS (pas de visage riggé). Non faits :
  IK des pieds, os ressorts, peau délitée, gestes de métier ; l'allègement d'Afi passe à la vague 4.
- ✅ **Vague 3 · la mise en scène des conversations (2026-11-13, `f7d60aa`)** : cadrage de la taille à la
  tête selon la distance ET la largeur d'écran, profondeur de champ (`BokehPass`, qualité haute, éteinte
  hors dialogue, flou plafonné pour ne pas baver sur l'oratrice), **caméra qui suit la tête à chaque
  image** (viser une seule fois laissait parfois la tête coupée), souffle de caméra au repos, oratrice
  à 1,30 m, les autres visiteuses écartées de la ligne de regard, lumière de face douce (2,4) portée par
  la caméra. QC 52/52, filmé au téléphone et à l'ordinateur par le vrai parcours.
- ✅ **Vague 5 · la lumière cuite dans Blender (2026-11-13, avancée par Mongazi avant la 4)** : occlusion +
  lumière des 25 lampes cuites en 2048 px, appliquées au décor du dedans, reflets gardés en direct. C'est le
  critère R1 de `REALISME.md`, qui porte désormais la suite (le mini-objectif « le plus réaliste possible »).
- ⏭️ **Vague 4 · la chaîne d'assets pour la 3G : LA PROCHAINE.** Le plan pas à pas est dans
  `REPRENDRE-ICI.md`, section 4 (mesurer d'abord, puis Afi allégée, meshopt, KTX2, fusion, instanciation,
  zéro allocation, chargement par étapes, mesurer après).

## L'ordre conseillé (effet sur la vente et le « wow », à coût maîtrisé)

1. **L'ouverture cinéma et la chorégraphie de lumière** (S) : le premier « wow », sans rien attendre de personne.
2. **Des personnages qui vivent** (M) : variantes de gestes, clignements et regard, démarrages et arrêts, plus de glissement ; puis Sènami et sa mère en 3D.
3. **La mise en scène des conversations** (S) : rapprochement et profondeur de champ sur celle qui parle.
4. **La chaîne d'assets pour la 3G** (M) : sans elle, rien de tout cela ne tourne chez une cliente de Cotonou.
5. **La lumière cuite dans Blender et les ombres douces** (L).
6. **Les robes en 3D et le mode « examiner »** (L) : dès que Mongazi a les planches.
7. **La vraie rue et la voix d'Hillary** : dès que Mongazi a la vidéo et l'accord.
