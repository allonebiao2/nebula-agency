# Ce que Mongazi crée de son côté · consignes prêtes à coller

> Écrit le 2026-11-12. Le but : que le salon ne ressemble à **aucun autre**, parce
> qu'il est fait de **ses** choses à elle. Trois sortes d'éléments, du plus
> personnel au moins personnel :
> 1. **les vrais** (photos à prendre chez Hillary) : rien ne les remplace ;
> 2. **les générés à partir d'elle** (Nano Banana Pro avec ses photos jointes) ;
> 3. **les générés tout court** (décor, ambiance).
>
> Dépose tout dans `_partage/immersive  store 3D/hillary/` avec les noms
> indiqués. Format **PNG, 2K**, sauf mention contraire.

---

## Les règles qui valent pour toutes les images

- **Joindre à chaque génération** : sa photo de référence (les robes sur
  podiums, `ff6cc3de-….jpg`) et son logo (`clients/10-hillary-m-styl/assets/images/logo.png`).
  Générer **dans la même conversation**, pour que tout se ressemble.
- ⛔ **Aucune robe générée ne sera vendue.** Les robes exposées dans le salon
  seront les siennes, reconstruites depuis ses vraies photos. Si une image
  générée montre une robe, je ne la reprends pas.
- ⛔ **Aucun autre logo de marque réelle** dans les images (pas de Coca, pas de
  MTN, pas de logo de téléphone).
- Si une image ne plaît pas, on la refait : c'est **le goût d'Hillary** qui
  décide. Montre-lui au moins le plan (A1) et son personnage (B1).

---

## A · LES VRAIS : à photographier chez Hillary (le plus important)

Au téléphone, **lumière du jour**, sans filtre, sans flash.

| # | Fichier | Ce qu'il faut | Ce que j'en fais |
|---|---|---|---|
| A1 | `vrai-tissus-01.jpg` à `-20.jpg` | **ses vrais tissus**, chaque wax **posé à plat**, photographié **du dessus**, en entier si possible (un mètre au moins) | les rouleaux, les présentoirs, les coussins du salon portent **ses** motifs |
| A2 | `vrai-outils-*.jpg` | sa machine à coudre, ses ciseaux, son mètre ruban, sa boîte d'épingles, son carnet de mesures | modélisés à l'identique sur le comptoir |
| A3 | `vrai-etiquette.jpg` | l'étiquette cousue dans ses vêtements, si elle en a | posée sur les fiches des pièces |
| A4 | `vrai-sac.jpg` | son sac ou son emballage de livraison, si elle en a | le sac que tu reçois au comptoir quand tu commandes |
| A5 | `vrai-atelier-*.jpg` | son atelier tel qu'il est (même modeste) | des clins d'œil : un objet, un tableau, une plante qui sont vraiment chez elle |
| A6 | `vrai-pieces-*.jpg` | **ses nouvelles créations** non encore au catalogue | elles entrent au site ET au salon |
| A7 | `voix-hillary.m4a` | **sa voix** : une note vocale où elle lit le texte de la section F | ses répliques, avec son accord |

---

## B · HILLARY, À PARTIR DE SES PHOTOS (avec son accord écrit) · LA PRIORITÉ

> Mongazi, 2026-11-12 : « le principal c'est Hillary, je veux qu'elle soit
> reconnaissable ». Elle mesure **1,68 m**.
>
> Ces images ne sont **jamais affichées** dans le salon : elles servent à
> fabriquer son personnage 3D (B1, B2), puis à animer son visage (B3). Son
> corps bougera pour de vrai grâce à **ses propres gestes filmés** (B4).

**Joindre à CHAQUE génération de cette section** : 8 à 10 vraies photos
d'elle, lumière du jour, sans filtre (visage de face, trois quarts gauche et
droite, profil gauche et droite, en pied de face et de dos). Plus il y a de
photos, plus elle sera reconnaissable.

⚠️ **Le piège à surveiller** : les générateurs d'images ont tendance à
**éclaircir les peaux noires**, affiner les visages et les silhouettes. Les
consignes l'interdisent en toutes lettres ; si ça arrive quand même, refaire.

### B1 · `hillary-planche.png` · son corps entier, prêt à animer

```
Character turnaround sheet of the woman in the attached photos. The attached photos are the ONLY identity reference: preserve her exact face (face shape, eyes, eyebrows, nose, lips, jawline, hairline), her exact skin tone and her exact body type. No beautification, no skin lightening, no slimming, no makeup change, no age change. She is 1.68 m tall.
She wears [SA TENUE DE COMPTOIR, idéalement une de ses créations, décrite précisément].
Four views side by side, same scale, same height, aligned on the same ground line: front, left side (90°), back, right side (90°), plus a three-quarter front view.
Pose for 3D rigging: A-pose, arms straight and held 45° away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Hair kept off the shoulders if possible. Clothing must not merge with the body at the armpits or between the legs. No bag, no phone, nothing in the hands.
Plain light grey background (#D9D9D9), soft even studio lighting, no cast shadows, no rim light, orthographic-like camera, no perspective distortion, sharp focus, high resolution, photorealistic, AAA video game character reference sheet.
```

### B2 · `hillary-visage-planche.png` · son visage, en gros plan

```
Head turnaround of the woman in the attached photos, exact same face, exact same skin tone, no beautification, no skin lightening. Five views in a row, same size and alignment: front, three-quarter left, left profile, three-quarter right, right profile. Neutral expression, mouth closed, eyes open looking straight ahead, hair exactly as in the photos. Plain light grey background (#D9D9D9), soft even lighting, no shadows, ultra detailed skin texture, photorealistic, high resolution.
```

### B3 · `hillary-expressions.png` · ses expressions (pour animer son visage, jamais affichées)

```
Expression sheet of the woman in the attached photos, exact same face and skin tone, no beautification, no skin lightening. Same front-facing framing for all, head and shoulders, plain light grey background (#D9D9D9), soft even lighting. Nine expressions in a 3 x 3 grid: neutral, warm smile, big laugh, listening attentively, surprised, thinking, asking a question (eyebrows slightly raised), speaking with mouth open on "A", speaking with mouth rounded on "O". Photorealistic, high resolution, no text.
```

### B4 · `hillary-gestes-*.mp4` · SES VRAIS GESTES, filmés (le plus précieux)

C'est ce qui la rendra **vivante et reconnaissable dans sa façon de bouger**.
Une IA de capture de mouvement transforme chaque vidéo en animation pour son
personnage 3D : ce seront **ses** gestes, pas ceux d'une bibliothèque.

**Comment filmer** : téléphone **posé** (pas tenu), à hauteur de taille, à
3 mètres ; **elle entière dans le cadre, des pieds à la tête** ; lumière du
jour ; fond simple ; une vidéo par geste, **5 à 10 secondes**, en commençant et
en finissant immobile, les bras le long du corps.

| Fichier | Ce qu'elle fait |
|---|---|
| `hillary-gestes-01-accueil.mp4` | elle accueille quelqu'un qui entre (sourire, geste de la main) |
| `-02-explique.mp4` | elle explique une robe en la montrant de la main |
| `-03-question.mp4` | elle pose une question (« c'est pour quelle occasion ? ») |
| `-04-ecoute.mp4` | elle écoute quelqu'un, hoche la tête |
| `-05-rire.mp4` | elle rit franchement |
| `-06-reflechit.mp4` | elle réfléchit, la main au menton |
| `-07-montre.mp4` | elle désigne quelque chose au loin |
| `-08-bras-croises.mp4` | elle attend derrière son comptoir, bras croisés |
| `-09-au-revoir.mp4` | elle dit au revoir de la main |
| `-10-marche.mp4` | elle marche tranquillement sur 4 ou 5 pas, aller et retour |

Avec le son, si elle accepte que sa voix serve aussi (section F).

---

## C · LES TROIS VISITEUSES · je m'en charge

> Mongazi, 2026-11-12 : « les PNJ je te laisse gérer, ça doit être des Noires,
> claires de peau ou noires ».

Je les génère moi-même (Cloudflare Workers AI, gratuit ; WaveSpeed en
secours), avec les mêmes règles de pose que B1. Ce sont des **personnages
inventés** : aucune photo d'une personne réelle n'est utilisée.

| Visiteuse | Taille | Carnation | Allure |
|---|---|---|---|
| **Afi**, la Béninoise de Paris, la trentaine | 1,71 m | brun moyen, chaud | cheveux courts naturels, trench crème, tenue noire, créoles dorées, cabas en cuir |
| **Sènami**, 20 ans, fan du TikTok d'Hillary | 1,64 m | brun clair | tresses longues relevées, crop top en wax, jean, baskets blanches, téléphone à coque magenta |
| **Maman Sènami**, la cinquantaine | 1,62 m | brun très foncé | boubou en wax et gele assorti, bracelets dorés, sandales, petit sac à main |

## D · LE SALON (le décor)

**À coller au début de chaque consigne de cette section :**

> Modern luxury couture boutique in Cotonou, Benin, for the fashion house
> "HILLARY M. STYL" (monogram H.M.S, signature color magenta #E6007E, ink
> #0B0A0C, pattern-paper cream #F4F1EC). Bright, airy, contemporary West
> African luxury. Glossy cream floor that reflects, curved white ceiling with a
> continuous warm gold LED cove line, warm recessed spotlights, white round
> podiums of different heights with headless white mannequins, light oak wood
> and brushed brass details, rolls of colorful wax fabric displayed like art,
> a few tropical plants, large windows. Daylight. Realistic architectural
> photography, eye level 1.6 m, 24 mm lens. No people. No brand logos other
> than H.M.S.

| # | Fichier | Ce qu'il faut ajouter |
|---|---|---|
| D1 | `salon-01-plan.png` | `Isometric cutaway view from above of the whole boutique, about 14 m wide and 10 m deep: entrance with glass doors on the front, five exhibition podiums near the entrance, the sales counter against the back wall, an events poster wall on the left, a seating corner with a large vertical screen on the right, a fitting room with a magenta curtain at the back right, fabric roll shelves.` **Le plus important.** |
| D2 | `salon-02-entree.png` | `View from the entrance door looking toward the counter at the back.` |
| D3 | `salon-03-comptoir.png` | `Front view of the sales counter: light oak and white lacquer with brushed brass edges, backlit magenta H.M.S logo on the wall behind, shelves of folded wax fabric, a sewing machine, a magenta tape measure, a small tablet.` |
| D4 | `salon-04-expositions.png` | `Close view of three round white podiums with headless white mannequins without clothes, warm spotlights from above, reflections on the floor.` |
| D5 | `salon-05-evenements.png` | `A wall dedicated to events: three framed posters lit by small brass picture lights, a long upholstered bench in front.` |
| D6 | `salon-06-coin-tiktok.png` | `A cozy corner: two magenta velvet armchairs, a large vertical screen on the wall, a ring light on a stand.` |
| D7 | `salon-07-cabine.png` | `Fitting room with a heavy magenta velvet curtain and a full-length mirror with a thin brass frame.` |
| D8 | `salon-08-facade-jour.png` | `Exterior facade of the boutique on a paved street of Cotonou in daylight: glass front, H.M.S sign, palm trees, red laterite dust on the roadside, yellow-shirted motorbike taxis passing, small neighboring shops.` |
| D9 | `salon-09-facade-nuit-pluie.png` | `Same facade at night under heavy tropical rain, warm interior light spilling onto the wet street, reflections, a motorbike taxi with a passenger under a plastic sheet.` |
| D10 | `salon-10-vue-fenetre.png` | `View THROUGH the boutique's large window from inside, looking at the street of Cotonou: the street only, the window frame at the edges, daylight.` (ce que voit le visiteur dehors) |
| D11 | `salon-11-vue-fenetre-nuit.png` | même chose **la nuit** |

---


### D bis · LES PANORAMAS À 360° (les plus utiles pour la 3D)

Une image qui fait **tout le tour**, prise depuis un point : les outils qui fabriquent un
lieu 3D à partir d'images (World Labs Marble, Tripo) en tirent le meilleur, et je peux
aussi m'en servir directement comme environnement lumineux. **Format 2:1**, le plus grand
possible. Coller d'abord le décor commun (ci-dessus), puis :

| # | Fichier | Ce qu'il faut ajouter |
|---|---|---|
| P1 | `pano-01-centre.png` | `360-degree equirectangular panorama, 2:1 aspect ratio, taken from the center of the boutique at eye level 1.55 m, seamless left and right edges: the glass entrance and street on one side, the counter with the backlit H.M.S logo on the opposite side, the podiums, the events wall, the seating corner and the fitting room around. No people. No distortion artifacts.` |
| P2 | `pano-02-comptoir.png` | `Same, taken standing in front of the sales counter, 2 meters from it.` |
| P3 | `pano-03-rue-jour.png` | `360-degree equirectangular panorama, 2:1, taken on the sidewalk in front of the boutique on a street of Cotonou, Benin, in daylight: the boutique glass facade with its H.M.S sign on one side, the street with motorbike taxis (yellow shirts), small shops with hand-painted signs, palm trees, red laterite dust, power lines, black water tanks on flat roofs. No real brand logos. Seamless edges.` |
| P4 | `pano-04-rue-nuit-pluie.png` | `Same street panorama at night under tropical rain, wet reflective ground, warm shop lights, street lamps.` |

## E · LES OBJETS DE LA MAISON

Ce qui reste quand on ne peut pas photographier le vrai (section A).

| # | Fichier | Consigne |
|---|---|---|
| E1 | `objet-sac.png` | `A luxury shopping bag in magenta #E6007E with a cream H.M.S monogram and cream rope handles, product photography on a plain white background, three-quarter view.` |
| E2 | `objet-enseigne.png` | `A backlit sign of the H.M.S monogram in brushed brass on a cream wall, glowing warm, front view, plain background.` |
| E3 | `objet-carte.png` | `A business card for HILLARY M. STYL, cream paper, magenta monogram H.M.S, elegant Bodoni typography, front view on a plain background.` (sans numéro inventé : je pose le vrai) |
| E4 | `objet-housse.png` | `A garment bag in cream canvas with a small magenta H.M.S monogram, hanging, plain background.` |

---

## F · LE TEXTE QUE HILLARY LIT (pour sa voix, si elle accepte)

Une note vocale, **posée, souriante, sans se presser** :

> « Bonjour, et bienvenue chez HILLARY M. STYL. Prends ton temps, regarde
> tout, touche les tissus. Ici, chaque pièce est cousue à tes mesures. Tu veux
> que je te conseille ? Pour une cérémonie, pour tous les jours, ou tu as déjà
> ton idée ? … C'est noté. C'est tout pour toi ? … Parfait. Valide ta commande
> ici, et on se retrouve sur WhatsApp. »

Plus **ses façons de dire à elle** (section 2 du questionnaire) : je les
découpe en répliques.

---

## G · CE QUE JE GÉNÈRE MOI-MÊME (pour info, rien à faire)

Les textures neutres (bois, laiton, sol, plâtre), le ciel, la pluie, les
sons d'ambiance (Web Audio, aucun fichier), les reconstructions 3D (une fois
WaveSpeed rechargé).
