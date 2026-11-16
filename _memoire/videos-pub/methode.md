# PUBS VIDÉO IA · la méthode

> Écrire, générer, remettre, monter, publier. Version du 2026-11-16, tirée de « L'AUTRE ».

## 1. Écrire une pub décalée (la grammaire des pubs asiatiques)

1. **Commencer au milieu du drame**, avec un enjeu énorme : jalousie, départ, aveu, accusation. La première image se
   comprend **sans le son** : sur TikTok, elle a une seconde.
2. **Des répliques à deux sens.** Chaque phrase marche pour la fausse histoire (l'amant) ET pour la vraie (le
   catalogue). Le spectateur se trompe tout seul ; à la chute, il revoit pour relire. C'est ça qui fait les vues.
3. **Un registre trop grand pour l'objet** : un mélodrame joué avec tout le sérieux du monde, pour un catalogue. Aucun
   clin d'œil avant la chute : les personnages ne savent pas qu'ils sont drôles.
4. **Une bascule qu'on voit** : un changement de lumière, de musique ou de cadre fait passer du drame au banal (le néon
   de « L'AUTRE »). Une musique qui se coupe net vaut une blague.
5. **Un chœur** : des témoins qui réagissent à la place du public (les voisins à la fenêtre). L'appel à l'action est
   **joué par un personnage** (« Envoie-moi le lien ! »), pas plaqué.
6. **Une fin en boucle** : la dernière réplique rappelle la première (« Dors. »).
7. **Des indices cachés** pour ceux qui revoient (les piles de pagnes dans la chambre).
8. **Le produit n'arrive qu'à la fin**, et il est vrai.
9. **Briser le 4e mur** (Mongazi, 2026-11-16) : un personnage se tourne vers le spectateur et lui parle. Au milieu,
   pour relancer l'attention (« Toi aussi, tu crois que c'est un homme ? ») ; à la fin, pour l'appel (« Et toi ? Ta
   boutique, elle dort quand tu dors ? »). Sur TikTok, on tutoie.

### Le français (consigne de Mongazi, 2026-11-16)

« Ici au Bénin, quand le français est trop soutenu, ils ne comprennent pas. » Donc le français de la rue, pas celui de
l'école :
- des phrases de 3 à 8 mots, une idée par phrase, des mots de tous les jours ;
- la tournure parlée : « Il a quoi de plus que moi ? », pas « Qu'est-ce qu'il a, que je n'ai pas ? » ;
- un mot technique s'explique par une image : Afi ne dit pas « catalogue digital », elle dit « ma boutique dans le
  téléphone » ; le nom de l'offre vit sur la carte de fin ;
- le test : quelqu'un qui n'est pas allé loin à l'école comprend-il l'idée du premier coup ?

Et aussi : on rit de la situation, jamais d'un peuple ; pas de religion, pas de deuil, aucun chef d'État ; une réplique
tient dans un clip de 8 s, donc 15 mots au plus.

## 2. Générer dans Google Flow (la part de Mongazi)

### La chaîne

1. **Les références** (Nano Banana Pro), faites une fois : d'abord une **image de style** (R0), jointe ensuite à TOUT ;
   puis une fiche par personnage (trois angles et six expressions, 16:9) et une image du décor vide (9:16).
2. **L'image de chaque plan** (Nano Banana Pro, 9:16), références jointes. On garde la meilleure.
3. **L'animation** (Veo 3.1, mode **Frames to Video**) : l'image du plan en première image, 8 s, **2 à 3 prises en
   Fast**, la meilleure refaite en Quality si elle le mérite.
4. **Un changement de lumière ou un geste précis** : première ET dernière image. La dernière se fait **en modifiant** la
   première dans Nano Banana Pro (même cadre), jamais en la refaisant.

### Écrire un prompt Veo 3.1 (guide officiel de Google)

- L'ordre : **cadrage, sujet, action, décor, style**.
- La réplique entre guillemets, après la voix :
  `Koffi says, in a deep, raspy male voice, speaking French with a West African accent from Benin: "Afi... C'est qui ?"`
- Les bruits : `SFX: …` · l'ambiance : `Ambient noise: …`
- Le minutage dans un clip : `[00:00-00:02] …` puis `[00:02-00:06] …`
- Toujours finir par : `Audio: only the dialogue and the room sounds, no music. No subtitles, no captions, no on-screen text.`
- Les prompts en anglais (le modèle les suit mieux), les répliques en français.

### Les pièges de Veo, et la parade

| Piège | Parade |
|---|---|
| La voix change d'un plan à l'autre | la même description de voix, mot pour mot, dans chaque prompt ; 2 à 3 prises, garder celles qui se ressemblent ; sinon ElevenLabs « Voice Changer » (voix vers voix) avec une voix fixe : le rythme reste celui de Veo, les lèvres restent calées |
| Un accent de France au lieu d'ici | tester UN plan avant les autres ; le Voice Changer change le timbre, pas vraiment l'accent ; au pire, doubler avec de vraies voix |
| Veo rajoute des mots pour remplir 8 s | finir la consigne par « then stays silent » ; couper au montage |
| Des sous-titres incrustés | la phrase « No subtitles » ; sinon regénérer, jamais recadrer |
| L'écran du téléphone (interface illisible, qui trahit l'IA) | toujours dos à la caméra ; un vrai écran s'incruste au montage |
| La mauvaise personne parle | une seule personne parle par plan (champ, contrechamp), et le prompt le dit : « Only Afi speaks in this shot » |
| Des mains qui se passent un objet | le plan le plus risqué : 3 à 4 prises |
| La pièce change d'un plan à l'autre | joindre l'image du décor à chaque image de plan |

## 3. Ce que Mongazi me remet, et le montage (ma part)

**La remise** : un dossier `_partage/<pub>/`, une prise par plan **nommée par son numéro** (`P01.mp4`, `P02.mp4`…, une
autre prise : `P05-b.mp4`), téléchargée en **1080p** depuis Flow, son de Veo compris. Jamais un export WhatsApp (il
compresse). Je les range dans `_studio-video/public/` (hors dépôt).

**Le montage**, en code dans `_studio-video/` (Remotion 4.0.512), une composition par pub. « Ultra dynamique »,
concrètement :
- **Sous-titres qui claquent** mot par mot, gros, blancs cernés de noir, dans le tiers haut (jamais dans les 480 px du
  bas ni les 240 px de droite : l'interface de TikTok s'y pose).
- **Arrêts sur image avec étiquette**, la marque des pubs thaïes : « KOFFI · livreur depuis 3 h 16 ».
- **Des dessins** en SVG posés sur l'image : cœur qui se fissure, gouttes de sueur, points d'interrogation, traits de
  vitesse façon manga, cercle rouge sur l'indice, onomatopées de bande dessinée.
- **Zooms secs** sur les réactions, transitions en coup de fouet, léger ralenti sur le moment tragique.
- **Bruitages** synthétisés (comme ceux de la vidéo de marque) : fouet, tambour, ding, cymbale.
- **La musique** : une pour le drame, coupée net à la bascule ; une autre pour la carte. Pixabay, lien de la page gardé
  (preuve de licence).
- **La carte de fin** aux couleurs de NEBULA (le logo en couches de la vidéo de marque).
- **Le son** : voix nettoyées et égalisées, −14 LUFS, crête à −1 dBTP.
- **Les livrables** : `out/<Pub>-9x16.mp4`, plus la version courte et le 16:9 si commandés. Rendu à un seul onglet, par
  morceaux si c'est long (le PC a 8 Go).

## 4. Publier

- Une légende courte qui ne dévoile rien, et « Regarde jusqu'à la fin ».
- **Un commentaire épinglé qui prolonge l'histoire** (« Pour la tantie qui veut le lien : … »).
- La version courte (30 s) pour les statuts WhatsApp.
- L'étiquette IA de la plateforme : voir [`cerveau.md`](cerveau.md), règle 5.

## Sources (vérifiées le 2026-11-16)

- Guide officiel des prompts Veo 3.1 : https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Le 9:16 natif (janvier 2026) : https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/
- Le filigrane selon l'abonnement : https://labs.google/fx/en-gb/tools/flow/faq
