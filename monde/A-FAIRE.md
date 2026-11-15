# LE MONDE · tout ce qui reste, qui fait quoi (2026-11-14)

> Mongazi : « quelles sont les actions que je dois poser et quelles sont celles que tu dois faire toi ?
> liste absolument tout ce qui reste à faire ». La liste complète, à tenir à jour (on coche, on ne
> supprime pas). Les consignes à coller sont dans `lieux/hillary-m-styl/personnages/CONSIGNES.md`,
> section « LES PERSONNAGES EN VIDÉO ».

**La direction (2026-11-14)** : la technique actuelle plafonne (« GTA de 2001 »). On change de matière :
le décor devient un **monde photographique** (Gaussian splat, Spark), les personnages **en conversation
sont ses vidéos** détourées, la 3D ne sert plus qu'à marcher de loin, la marche est refaite dans le code.

## 🙋 MONGAZI

### A · L'essai qui décide tout (maintenant)
- [ ] A1 · Le décor vidé : consigne 5 sur `salon-vue-comptoir-arche.jpg` → `salon\salon-a-vide-16x9.jpg`
- [ ] A2 · Marble, compte gratuit : un monde depuis A1, le regarder dans leur visionneuse, dire « ça vaut » ou non
- [ ] A3 · Si ça vaut : Marble Standard 20 $ (export) ou Pro 35 $/mois (droits commerciaux), carte bancaire : SA décision. Sinon : me laisser chercher une voie gratuite
- [ ] A4 · Les images de départ (consigne 1) : `afi-depart.jpg`, `senami-depart.jpg`, `maman-depart.jpg`
- [ ] A5 · Les vidéos en boucle (consignes 2 et 3) : écouter + parler pour Afi, Sènami, Maman (6 vidéos)
- [ ] A6 · Hillary : 2 ou 3 vraies photos de son visage, `hillary-depart.jpg` (consigne 4), puis écouter, parler, accueillir, conseiller (4 vidéos)
- [x] A7 (parole de Mongazi notée le 2026-11-14 dans `hillary/ACCORD.md` ; une preuve d'Hillary elle-même reste à déposer avant la mise en ligne) · La trace écrite de l'accord d'Hillary (visage, et voix si un jour) dans `hillary\`

### B · Les questions en attente depuis le 13
- [ ] B1 · Le jour clair comme ses images, le soir tamisé : oui ou non
- [ ] B2 · `robe-inconnue` : une création d'Hillary absente du site, ou une image ratée ?
- [ ] B3 · L'ensemble Mira (h2) : son dos est-il ouvert ? (à demander à Hillary)
- [ ] B4 · Les six expressions du visage d'Hillary : plus nécessaires si la vidéo est retenue
- [ ] B5 · Le commercial NEBULA : les 5 questions ouvertes de `COMMERCIAL.md`

### C · Plus tard
- [ ] C1 · Essayer le salon sur son iPhone (même Wi-Fi, adresse dans `REPRENDRE-ICI.md` § 0) et écouter la musique
- [ ] C2 · Un Android d'entrée de gamme pour mesurer (le sien, ou celui d'un proche)
- [ ] C3 · Les 16 planches de robes qui manquent (h1 et h2 sont faites) : `PROMPTS-ROBES-3D.md`
- [ ] C4 · Recharger WaveSpeed (≈ 40 $) pour passer les robes en 3D (solde : 0,04 $)
- [ ] C5 · Hillary : le questionnaire (`QUESTIONNAIRE-HILLARY.md`), son TikTok, sa voix, des vidéos de ses vrais gestes
- [ ] C6 · La vidéo d'une vraie rue de Cotonou à l'iPhone (la rue derrière la vitrine)
- [ ] C7 · Dire quand le salon passe en ligne, et à quelle adresse

## 🤖 CLAUDE

### D · Tout de suite, sans rien attendre
- [x] D1 · Le contrôle qui cale : ✅ 2026-11-14, QC **58/58**. Deux faux rouges : (1) le QC touchait la bulle au moment où la fiche s'ouvre par-dessus → `toucher_dialogue()` n'attend plus 60 s ; (2) le test du fondu lisait l'opacité depuis une page occupée → il lit l'opacité RÉELLE du voile au moment du saut. Et un vrai gain : le saut attend `transitionend` (l'écran noir), filet 700 ms (`socle/deplacement.js`)
- [x] D2 · Le monde photographique : ✅ 2026-11-14, essayé avec le monde d'exemple (500 000 points, `?monde=../../_cuisson/essai-monde.spz`) : chargé, décor modélisé retiré, personnages et pièces par-dessus, 0 erreur ; commité
- [x] D3 · La marche : ✅ 2026-11-14, QC **59/59** (un contrôle neuf). Patinage du pied posé **~34 → 9 cm/s** (médiane, 12 au 90e centile ; mesuré par `_outils/mesurer_marche.py`). Vitesse propre mesurée sur les pieds, accélération et freinage, virages en courbe, corps sans retard, écarts intégrés à la trajectoire, **pas de côté** marché au lieu de glisser. Décision : `demarrer`/`arreter` et `tourner-gauche/droite` ne sont PAS joués (autres allures, double rotation) : détail `_memoire/apprentissages/2026-11-14-marche-qui-ne-glisse-pas.md`. Reste pour plus tard : IK des pieds dans les virages
- [x] D4 · Les personnages en vidéo : ✅ 2026-11-15, QC **62/62**. Hillary (en buste, en vidéo permanente à son comptoir : écouter 23 s, parler, saluer), Afi, Sènami, Maman (parler + écouter). Regardé au téléphone jour et nuit, à l'ordinateur de jour. Vidéos hors dépôt. Détail : `_memoire/apprentissages/2026-11-14-personnage-video.md`. Reste possible : de vraies vidéos « écouter » pour Afi et Maman, « conseiller » pour Hillary (quota ZeroGPU), une version plus nette pour l'ordinateur
- [ ] D5 · Vidéo → mouvement 3D : 🔎 **piste trouvée le 2026-11-14 : NVIDIA GEM-X** (code Apache 2.0, poids sous « NVIDIA Open Model License », la fiche du modèle le dit prêt pour un usage commercial ; corps SOMA-X annoncé Apache 2.0 ; mouvement complet du corps depuis une seule vidéo). ⚠️ À faire avant de s'en servir : lire le texte entier de la licence NVIDIA, et il faut une carte NVIDIA (ce PC n'en a pas : Colab ou un Space Hugging Face), puis recibler son squelette SOMA sur celui de Mixamo (Blender). Écartés : FrankMocap et tout ce qui passe par SMPL (corps sous licence non commerciale). Sources : github.com/NVlabs/gem-x, huggingface.co/nvidia/GEM-X
- [ ] D6 · Voie gratuite pour le décor en splats : ⛔ **vérifié le 2026-11-14 à la source** : **Apple SHARP = poids sous licence « apple-amlr », recherche seulement** (le Space ZeroGPU qui l'enrobe est MIT, pas le modèle) ; **NVIDIA Lyra 2.0 = poids sous licence « Internal Scientific Research and Development », recherche seulement** (le code est Apache 2.0, les articles qui disent « Apache, commercial » se trompent). ✅ **Reste : NVIDIA Lyra 1.0, poids sous « NVIDIA Open Model License », prêt pour un usage commercial** (fiche huggingface.co/nvidia/Lyra), mais très lourd (Cosmos) : à éprouver. Notes d'origine : des articles) : **NVIDIA Lyra 2.0** (une image → un monde 3D navigable, annoncé Apache 2.0), **Apple SHARP** (une image → des splats en moins d'une seconde, annoncé MIT ; vérifier les POIDS). TripoSplat, Idol et TRELLIS 2 font des OBJETS, pas des pièces. Toutes demandent une carte NVIDIA : Space Hugging Face (clé `secrets/huggingface.env`) ou Colab. ⛔ Partir d'une vue vidée de ses robes générées

- [ ] D7 · **De VRAIES vidéos « écouter » pour Afi et Maman, sans payer** : Wan 2.2 « première et dernière image » sur ZeroGPU (Space `multimodalart/wan-2-2-first-last-frame` ; poids annoncés Apache 2.0, À VÉRIFIER sur la fiche officielle Wan-AI). Donner la 1re image de sa vidéo « parler » (bras le long du corps) en première ET en dernière image : une boucle parfaite où elle écoute. Quota ZeroGPU : épuisé à 2 h le 2026-11-14, retour vers 16 h 20. En attendant : le passage calme de « parler » (`--calme`).

- [x] D8 · **Vague 2, le rendu** : ✅ 2026-11-15, QC **66/66**. Étalonnage de film dans le tone mapping (toutes qualités), vignettage, faisceaux visibles et poussière, brume de profondeur, soir plus tamisé, **le soleil qui entre par la vitrine** (façade au sud-ouest). 53 i/s immobile, 44 en marchant au téléphone. ⛔ Notes : lumière 7 à 7,5, étalonnage 7,5 à 8, « waouh » 6,5 à 7 : le seuil de 8 n'est pas atteint partout, ce sont les matières (vague 3) et le décor (vague 4) qui retiennent. Détail : `_memoire/apprentissages/2026-11-15-rendu-film-sans-passe.md`

### E · Dès que ses fichiers arrivent
- [ ] E1 · Le monde Marble : le caler sur le salon (`?calage`), mesurer poids et images/s au téléphone, retirer le décor modélisé du dedans, poser par-dessus le vrai logo et ses pièces
- [ ] E2 · Ses vidéos : détourer, boucler, brancher Afi, Sènami, Maman
- [x] E3 · Hillary au comptoir : ✅ en vidéo (2026-11-15) ; ⏳ Mongazi confirme la ressemblance
- [ ] E4 · Maman en 3D pour la marche de loin (quota TRELLIS, `en_3d.py … --faces 100000`)
- [ ] E5 · Les robes : planche → 3D → validation d'Hillary pièce par pièce ; la fiche garde la vraie photo

### F · La 3G et la finition
- [ ] F1 · Compression (meshopt + KTX2), personnages allégés, chargement par étapes (`REPRENDRE-ICI.md` § 4)
- [ ] F2 · Mesurer au téléphone (`_outils/mesurer.py`) : cible 30 images/s, premier écran léger
- [ ] F3 · La rue derrière la vitrine (R10), la brume légère dans les faisceaux (R11), un rendu sans crénelage (R12)
- [ ] F4 · L'interface : une main animée la première fois, les animations des panneaux (fiche, sac, cadran)
- [ ] F5 · Le test à l'aveugle « photo ou 3D ? » (R13, à faire faire par Mongazi), puis retirer le bandeau « MAQUETTE » (R15)
- [ ] F6 · La mise en ligne : `_dist`, adresse, contrôles, vérifier ce qui est servi
- [ ] F7 · La mémoire à chaque étape : `REPRENDRE-ICI.md`, `VAGUES.md`, `_memoire/EN-INSTANCE.md`, journal

⚠️ Si le monde photographique est retenu, la lumière cuite, le plafond (R5) et le sol qui reflète (R6) du
dedans deviennent sans objet : la lumière est dans l'image.

## 💤 Plus loin (registre `VAGUES.md`)
- Le commercial NEBULA dans chaque boutique (`COMMERCIAL.md`)
- Un teaser vidéo par boutique (`TEASERS.md`)
- Le 2e lieu : Grain d'Esthétique
- La ville : Cotonou en 3D, chaque lieu à sa place, voir les autres visiteurs
- Le back-office d'Hillary (affiches, décorations de saison, sa tenue, ses expositions)
- Le loyer
- Le futur skill tiré de `DEROULEMENT.md`
