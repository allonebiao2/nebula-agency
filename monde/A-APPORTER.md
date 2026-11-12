# Ce que Mongazi doit apporter · le salon d'Hillary

> Écrit le 2026-11-12. Classé par vague : ce qui débloque la vague 1 d'abord.
>
> 📌 **Les consignes complètes à générer** (Hillary, ses visiteuses, ses
> portraits de dialogue, le salon, les objets, les vraies photos à prendre) :
> **`PROMPTS-NANO-BANANA.md`**. **Le message à envoyer à Hillary** :
> **`QUESTIONNAIRE-HILLARY.md`**. Cette page-ci n'est que la liste à cocher.
> Coche au fur et à mesure, ou dépose les fichiers dans `_partage/immersive  store 3D/`.

---

## Vague 1 · la maquette jouable (presque rien)

- [x] **Tes réponses aux 4 questions** (moteur, PNJ, visiteurs, mesures) : données le 2026-11-12.
- [ ] **Le TikTok d'Hillary** : son nom exact (`@…`). Et ses autres comptes s'ils
      existent (Instagram, Facebook).
- [ ] **Confirmer que `+229 51 37 47 93` reste le numéro de commande.** Je ne le
      change pas, je vérifie seulement qu'il n'a pas bougé depuis le site.

## Vague 2 · le salon habillé : les images à générer avec Nano Banana Pro

**Comment** : génère-les **dans la même conversation**, en joignant à chaque fois
**sa photo de référence** (`ff6cc3de-….jpg`, les robes sur podiums) et **son
logo** (`clients/10-hillary-m-styl/assets/images/logo.png`), pour que les
images se ressemblent entre elles. Format **16:9, 2K**.

⚠️ Ces images me servent de **plans d'architecte** : je construis la 3D à partir
d'elles. Elles ne seront jamais présentées comme des photos d'un vrai salon, et
**aucune robe générée n'entrera au catalogue** (les robes exposées seront les
siennes). Si une robe apparaît dans l'image, ce n'est pas grave : je ne la
reprends pas.

**Le décor commun à coller au début de chaque consigne :**

> Modern luxury couture boutique in Cotonou, Benin, for the fashion house
> "HILLARY M. STYL" (monogram H.M.S, signature color magenta #E6007E). Bright,
> airy, contemporary West African luxury. Glossy cream floor that reflects,
> curved white ceiling with a continuous warm gold LED cove line, warm recessed
> spotlights, white round podiums of different heights with headless white
> mannequins, light oak wood and brass details, rolls of colorful wax fabric
> displayed like art, a few tropical plants, large windows. Daylight. Realistic
> architectural photography, eye level 1.6 m, 24 mm lens. No people. No real
> brand logos other than H.M.S.

**Les plans à générer :**

| # | Fichier | Ce qu'il faut ajouter à la consigne |
|---|---|---|
| 1 | `salon-01-plan.png` | `Isometric cutaway view from above of the whole boutique: entrance with exhibition podiums at the front, the sales counter against the back wall, an events poster wall on the left, a seating corner with a large vertical screen, a fitting room with a magenta curtain, fabric roll shelves.` **Le plus important : il me donne la disposition.** |
| 2 | `salon-02-entree.png` | `View from the entrance door looking toward the counter at the back.` |
| 3 | `salon-03-comptoir.png` | `Front view of the sales counter: light oak and white lacquer with brass edges, backlit magenta H.M.S logo on the wall behind, shelves of folded wax fabric, a sewing machine, a tape measure, a small tablet.` |
| 4 | `salon-04-expositions.png` | `Close view of three round white podiums with headless white mannequins, warm spotlights from above, reflections on the floor.` (mannequins **sans robe** si possible) |
| 5 | `salon-05-evenements.png` | `A wall dedicated to events: framed posters with small brass lights, a bench in front.` |
| 6 | `salon-06-coin-tiktok.png` | `A cozy seating corner: magenta velvet armchairs, a large vertical screen on the wall, a ring light.` |
| 7 | `salon-07-cabine.png` | `Fitting room with a heavy magenta velvet curtain and a full-length mirror with a gold frame.` |
| 8 | `salon-08-facade-jour.png` | `Exterior facade of the boutique on a street of Cotonou in daylight: glass front, H.M.S sign, palm trees, red laterite dust on the roadside, motorbike taxis passing.` |
| 9 | `salon-09-facade-nuit-pluie.png` | `Same facade at night under heavy tropical rain, warm interior light spilling onto the wet street, reflections.` |

Si une image ne te plaît pas, refais-la : c'est **ton goût** et celui d'Hillary
qui comptent ici, pas le mien. **Montre le n° 1 à Hillary** si possible : c'est
son salon.

## Vague 3 · les personnages

### Hillary
- [ ] **Son accord écrit** pour que son visage soit utilisé (un message WhatsApp
      suffit) : *« J'accepte que mon image serve à créer mon personnage 3D dans
      le salon virtuel HILLARY M. STYL. »*
- [ ] **8 à 10 vraies photos d'elle**, lumière du jour, **sans filtre** :
      visage de face, de trois quarts (gauche et droite), de profil (gauche et
      droite), corps entier de face et de dos. Coiffure comme elle la porte
      d'habitude.
- [ ] **La tenue qu'elle porterait au comptoir** (idéalement **une de ses
      créations** : son personnage devient sa meilleure publicité).
- [ ] Puis, avec ses photos jointes, génère sa **planche de personnage** :
      > Character turnaround sheet of the woman in the reference photos, exact
      > same face and body type: front view, three-quarter view, side view,
      > back view, full body, neutral A-pose with arms slightly away from the
      > body, wearing [sa tenue]. Plain light grey background, soft even
      > lighting, no shadows, realistic proportions, high detail, video game
      > character concept sheet.

      ⚠️ La pose bras écartés et la lumière plate sont **obligatoires** : c'est
      ce qui permet de la transformer en 3D puis de l'animer.
- [ ] **Facultatif, mais ça change tout** : **sa vraie voix**. Une note vocale
      d'une minute où elle lit un texte que je lui écrirai, et son accord pour
      la voix aussi. Sans elle, je prends une voix générée.
- [ ] **Sa façon de parler** : comment elle accueille une cliente, les mots
      qu'elle répète, les expressions béninoises qu'elle emploie (en fon, en
      goun, en français d'ici). **Je n'invente aucune expression locale.**

### Les trois visiteuses (décidées le 2026-11-12)
La Béninoise de Paris · la jeune de Cotonou fan du TikTok d'Hillary · sa mère.
Ce sont des **personnages inventés** : leur planche se génère **sans photo de
quelqu'un de réel**, avec la même consigne de pose et de lumière que pour
Hillary, en remplaçant le début par leur description.
- [ ] **Leurs prénoms** : je propose *Sènami* (la fille) et *Afi* (la
      Parisienne) ; la mère se fait appeler *Maman* par sa fille. À toi de
      valider ou de changer : ce sont des prénoms d'ici, je ne veux pas en
      choisir un qui sonne faux.
- [ ] **Leurs tenues** : elles peuvent porter **des pièces d'Hillary** (le
      salon devient un défilé discret), ou des tenues neutres. À trancher.

## Le contenu vrai (pour que les PNJ ne mentent jamais)

- [ ] **Sa dernière vidéo TikTok marquante** : le lien, et ce qui s'y passe en
      une phrase. C'est elle que le visiteur évoquera.
- [ ] **Ses événements à venir** (défilé, vente privée, nouvelle collection) :
      titre, date, lieu, et l'affiche si elle existe. S'il n'y en a pas, le mur
      dira « Prochainement ».
- [ ] **Le quartier de l'atelier** (au moins le quartier : Fidjrossè, Haie
      Vive, Akpakpa…). Il décide **la rue qu'on voit par la vitrine**, et plus
      tard **sa place sur la carte de Cotonou**. L'adresse exacte bloque aussi sa
      fiche Google depuis août.
- [ ] **Ses horaires** : le salon peut dire « fermé » la nuit, ou rester ouvert
      parce qu'il est virtuel (à toi de décider).
- [ ] **Les 5 questions qu'on lui pose le plus** : ce seront les premières
      répliques d'Hillary.

## L'argent

- [ ] **Recharger WaveSpeed : prévoir 40 $** pour tout le premier lieu
      (aujourd'hui : 0,04 $). Estimation, à ± 50 % :

      | Poste | Calcul | Total |
      |---|---|---|
      | Hillary en 3D | modèle 0,36 $ × 3 essais + squelette 0,30 $ × 2 + 6 animations à 0,42 $ | ≈ 4 $ |
      | Trois visiteuses | idem × 3 | ≈ 12 $ |
      | 19 pièces sur mannequin | 0,36 $ × 2 essais × 19 | ≈ 14 $ |
      | Objets du décor qu'aucune bibliothèque gratuite n'a | | ≈ 3 $ |
      | Images que je génère moi-même (textures, affiches) | 0,14 $ × 20 | ≈ 3 $ |

      Je te donnerai le **réel** à la fin de chaque vague.
- [ ] Rien d'autre à payer : hébergement gratuit (Cloudflare Pages), météo
      gratuite (MET Norway), moteur gratuit (Three.js), Blender gratuit dans
      Colab.

## Unreal Engine (ta demande : l'installer quand même pour la création)

Le **lanceur Epic est installé** (`C:\Program Files\Epic Games\Launcher`). Le
moteur, lui, ne s'installe qu'avec **ton compte Epic** :
- [ ] ouvrir « Epic Games Launcher », te connecter ;
- [ ] onglet **Unreal Engine → Bibliothèque → « + »**, choisir la dernière
      version ;
- [ ] ⚠️ **l'installer sur `D:`** (60 Go libres ; `C:` n'en a que 38) ;
- [ ] ⚠️ dans **Options**, décocher tout ce qui n'est pas Windows (Android,
      iOS, Linux, symboles de débogage) : c'est ce qui fait passer
      l'installation de plus de 100 Go à quelques dizaines ;
- [ ] me dire quand c'est fini : je lance l'éditeur une fois et je te dis
      **franchement** s'il tient sur ce PC.

⚠️ Prévois le volume de téléchargement (plusieurs dizaines de Go) sur ta
connexion. Rien du salon ne dépend d'Unreal : la vague 1 avance sans lui.

## Une question sur ton dossier
- [ ] La capture `IMG_9666.PNG` montre les chapitres « Repo 3 à 6 » d'une
      vidéo « /motion-graphics » que je n'ai pas retrouvée. **Si elle compte,
      envoie-moi son lien** et je l'analyse comme les autres.

## Pour tester

- [ ] **Un téléphone Android d'entrée de gamme** (Tecno, Infinix, itel : ce
      qu'ont les clientes d'Hillary). Le tien, celui d'un proche, peu importe,
      pourvu qu'on puisse l'ouvrir à chaque vague.
