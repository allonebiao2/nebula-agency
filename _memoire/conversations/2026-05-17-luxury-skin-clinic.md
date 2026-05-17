# Session — Récap complet vitrine Luxury Skin Clinic (cliente 04 · Gloria)

## Date : 17 Mai 2026
## Sujet principal : Bilan de tout ce qui a été construit pour la cliente 04 depuis le début

---

## 1. Contexte

Nouvelle cliente NEBULA : **Ahouangnimon Gloria**, Cotonou (Bénin).
Secteur cosmétique / institut de beauté. WhatsApp : `0167975626` ⚠️ INTOUCHABLE.

Particularité du projet : ce n'est pas une vitrine simple mais un **projet
multi-marques** réunissant 3 marques distinctes de Gloria sous un même site,
articulées autour d'une page d'accueil centrale (hub).

Cette session fait le point sur l'ensemble du travail accumulé sur ce client
(création du dossier, framework des 4 pages, intégration des premiers vrais
produits) et consigne l'état d'avancement.

---

## 2. Structure créée

### Dossier client
`clients/04-luxury-skin-clinic/`
- `index.html` — page d'accueil / hub (anciennement `hub.html`, renommé pour Netlify)
- `ina-luxury.html` — catalogue marque INA LUXURY
- `luxury-skin-clinic.html` — soins & prestations de l'institut
- `cozy.html` — catalogue marque COZY
- `CONTEXT.md` — brief, contraintes, état d'avancement, décisions
- `assets/docs/gloria-infos.md` — collecte des infos brutes envoyées par la cliente
- `assets/images/` — arborescence préparée par marque et catégorie
  (logo/, ina-luxury/{visage,corps,capillaires}, luxury-skin-clinic/{soins,prestations},
  cozy/, galerie/, hub/)
- `assets/videos/presentation/`

### Direction artistique commune aux 4 pages
- Palette : Blanc • Or • Noir (`--noir #0c0b09`, `--or #c9a24b`, `--creme #faf6ec`)
- Typo : Cormorant Garamond (titres) + Jost (corps) — Google Fonts
- Fond marbre noir animé (SVG feTurbulence), particules dorées en canvas
- Curseur doré personnalisé avec traînée
- Technique : HTML pur, CSS inline, zéro framework — règle NEBULA

---

## 3. Architecture des 3 marques

Le site est pensé comme un **hub + 3 univers** :

### `index.html` — le hub
- Loader animé → phrase d'accueil écrite lettre par lettre (typewriter)
- 3 cards marques flottantes (lévitation douce)
- Au clic : son cristal (Web Audio API) + zoom cinématique + rideau de transition
- Musique d'ambiance spa générée en Web Audio API (bouton mute)
- Footer : liens Instagram / TikTok (encore en `#`), localisation Cotonou

### 1. INA LUXURY — `ina-luxury.html` (cosmétiques & capillaires)
- Catalogue à navigation hiérarchique : Famille → Sous-catégorie → Préoccupation
- 3 familles : Visage / Corps / Capillaires
- Menu accordéon latéral + fil d'Ariane cliquable + bouton retour niveau par niveau
- Filtres « par préoccupation » (chips) : taches, acné, hydratation, anti-âge,
  éclat, sensibilité, cheveux secs, pousse — chacun ouvre un panneau conseils
- Cards produits avec badge Bestseller animé, tilt 3D, lien WhatsApp pré-rempli

### 2. LUXURY SKIN CLINIC — `luxury-skin-clinic.html` (institut)
- Page soins & prestations (pas un catalogue produits)
- Onglets par type : Visage / Corps / Rituels signature + filtres préoccupation
- Section vidéo de présentation (embed YouTube — VIDEO_ID encore placeholder)
- Section avant/après + témoignages clientes
- CTA WhatsApp « Réserver maintenant »

### 3. COZY — `cozy.html` (hygiène intime & bien-être)
- Catalogue par catégorie : Hygiène intime / Zones sensibles / Fraîcheur /
  Soins du corps doux
- Filtres « par besoin » : fraîcheur, apaisant, éclat, hydratation, douceur
- Ton volontairement doux et délicat, panneau conseils par besoin

---

## 4. Produits intégrés

### Contenu de démonstration (framework v1)
Les 3 catalogues ont d'abord été remplis de produits/soins **de démonstration**
(noms plausibles, prix indicatifs) pour valider le framework :
- INA LUXURY : ~30 produits démo (sérums, crèmes, gommages, packs, routines)
- LUXURY SKIN CLINIC : ~14 soins démo + rituels signature
- COZY : ~10 produits démo

### Premiers VRAIS produits intégrés (INA LUXURY · Visage)
Une sous-catégorie **« Nettoyants visage »** a été ajoutée et reçoit les premiers
produits réels de Gloria, avec fiche détaillée complète (formats, prix réels,
actifs, résultats, liste INCI d'ingrédients) :
- **Busserole Beauty Bar** — savon soin illuminateur, 250g · 8 000 FCFA
- **Kojic Beauty Bar** — savon éclaircissant, 150g · 5 500 F / 300g · 10 000 F

Ces 2 produits introduisent un nouveau modèle de card enrichie : sélecteur de
formats, accordéons produit (description, actifs, résultats, ingrédients INCI).

Photos reçues mais **pas encore encodées en base64 ni intégrées** :
`assets/images/ina-luxury/visage/` — NETTOYANT ICE, GEL LAVANT SKIN,
NETTOYANT OXYGÈNE, Nettoyant aux plantes.

---

## 5. État actuel du projet

| Élément | État |
|---|---|
| Dossier + arborescence assets | ✅ Fait |
| Framework des 4 pages (HTML/CSS/JS) | ✅ Fait |
| Direction artistique | ✅ Fait |
| Hub + animations (son, zoom, rideau) | ✅ Fait |
| Contenu démo des 3 catalogues | ✅ Fait |
| Premiers vrais produits (Busserole, Kojic) | ✅ Intégrés |
| Photos produits en base64 | ❌ À faire (4 photos reçues, non encodées) |
| Logos réels des 3 marques | ❌ À recevoir (monogrammes dorés en attendant) |
| Liens Instagram / TikTok | ❌ Encore en `#` |
| VIDEO_ID vidéo de présentation | ❌ Placeholder |
| Reste du contenu réel (textes, prix, listes) | ❌ À recevoir de Gloria |
| Brief validé / responsive testé / livré | ❌ Pas encore |

**Budget** : 100 000 FCFA setup + 10 000 FCFA/mois.
**Hébergement** : Netlify (d'où le renommage `hub.html` → `index.html`).

---

## 6. Décisions prises

- Projet structuré en **4 pages HTML distinctes** (hub + 3 marques) plutôt qu'une
  seule page longue.
- Framework v1 construit avec **contenu de démonstration** d'abord, à remplacer
  progressivement par le contenu réel de la cliente.
- Sons (cristal + ambiance spa) générés via **Web Audio API** : zéro fichier
  audio externe à héberger.
- `hub.html` renommé `index.html` pour servir de page d'accueil Netlify.
- Card produit enrichie (formats + accordéons actifs/résultats/INCI) introduite
  avec les premiers vrais produits — deviendra le standard INA LUXURY.

---

## 7. À faire ensuite

1. Encoder en base64 les 4 photos de nettoyants déjà reçues et les intégrer.
2. Réclamer à Gloria : logos des 3 marques, liens Instagram/TikTok, vidéo de
   présentation, et le reste des listes produits avec prix réels.
3. Remplacer progressivement le contenu démo par le contenu validé.
4. Tester le responsive sur appareils réels.
5. Faire valider le brief par Gloria avant la livraison.

---

## 8. À retenir

- Un projet « multi-marques » se gère bien en hub + pages-univers séparées :
  chaque marque garde son ton tout en partageant la direction artistique.
- Construire le framework avec du contenu démo permet de valider la structure
  sans bloquer sur l'attente des assets clients.
- Penser dès le départ au renommage `index.html` pour Netlify.
