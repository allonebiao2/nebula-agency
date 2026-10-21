# 2026-10-21 · MA LETTRE À… : la vitrine en profondeur (GSAP, la nuit des lettres, les fonds)

*Suite de `2026-10-21-malettre-mise-en-ligne.md`. Mongazi : « ajoute encore plus de GSAP et de scroll
animation 3D sur les autres zones… pousser l'effet WOW à 200 % et maximiser les achats ».*

## Ses réponses (questions posées avant de construire)

- La grande zone de profondeur : **une nouvelle section au milieu** (entre la plume et les occasions).
- La musique : **au premier toucher**, bouton pour couper, choix mémorisé.
- Les images de fond : **des mains, jamais de visage**.
- Au téléphone : **une barre « Écrire ma lettre » fixée en bas**.

## Ce qui est fait

- **GSAP 3.13.0 + ScrollTrigger**, téléchargés de npm (licence « no charge », usage commercial compris),
  servis d'ICI (`malettre/vendor/`, `?v=3.13.0`, cache d'un an), **chargés après le premier écran** (au
  premier geste, ou 3,5 s après `load`), jamais en mouvement réduit. Sans eux, rien ne manque : ils
  n'ajoutent que le mouvement. ⚠️ La règle « aucune bibliothèque » du standard vitrine cède ici à la
  demande explicite de Mongazi ; le premier écran reste sous 320 Ko (contrôlé).
- **Une animation de profondeur par zone, tirée de la lettre** : le héros (l'enveloppe plonge vers la
  scène, deux nappes de poussière d'or et de cire) · la plume (la feuille se redresse du bureau, un bec suit
  la ligne qui s'écrit) · **la nuit des lettres** (nouvelle section : la caméra traverse un ciel où flotte une
  enveloppe par occasion RÉELLE du constructeur, 27, chacune à sa profondeur ; à la fin la tienne arrive, au
  prénom tapé, son cachet s'allume, « Écrire la mienne ») · le faire-part (deux volets s'ouvrent sur le
  sceau) · le seuil (le téléphone sort de la nuit, un rai de lumière, les pastilles tombent comme des gouttes
  de cire) · le prix (la feuille de timbres se lève du comptoir) · les promesses (chaque billet tombe de sa
  profondeur et se déplie ; les mots de l'aveu s'allument) · les questions (fiches qui montent du tiroir) ·
  la fin (la page blanche se lève du bureau et prend le prénom) · les exemples (inclinaison sous le pointeur).
  ⛔ Aucun chiffre inventé : les enveloppes du ciel sont les occasions, pas des lettres vendues.
- **Les fonds d'ambiance** : `python malettre/_fonds.py` lit `_partage/ma lettre/fonds/<zone>-paysage|portrait.*`,
  écrit `malettre/fonds/<zone>-l.webp` et `-p.webp` en VISANT UN POIDS (le héros au plus bas), découpe une
  forme manquante sur une ancre (la plume : sa main est à droite), retourne le faire-part (ses alliances côté
  carton). Le build ne pose un emplacement QUE si l'image existe ; elle ne se télécharge qu'à l'approche
  (`.pret`), et celle du héros **quand le rideau du chargement se lève** (sinon le premier écran passait de
  282 à 341 Ko). Le voile de chaque zone garde le contraste (mesuré sur les pixels). Six zones sur sept
  ont leur image (Mongazi, 2026-10-21) ; **il manque les promesses** (la cire qu'on presse).
- **La musique** : le bouton n'existe que si `malettre/son/musique.mp3` est sur le disque ; Web Audio
  (l'iPhone ne laisse pas baisser `audio.volume`), départ au premier geste (la molette ne compte pas),
  baisse quand une lettre d'exemple joue ses sons, se tait quand l'onglet est caché. ⏳ **Le MP3 attendu**
  (style proposé : piano nocturne + cordes feutrées + kora en filigrane, sans voix ni batterie, 60-75 bpm).
- **La barre d'achat** au téléphone : bande de bord opaque, paraît après le héros, s'efface devant le
  formulaire de la fin, la modale, et « Écrire la mienne ».

## Ce que les contrôles ont attrapé (et ce que les captures ont attrapé)

- La **sonde de contraste mentait deux fois** : elle mesurait un bouton CACHÉ (son parent à opacité 0) et
  photographiait une feuille encore en mouvement (l'inertie de GSAP après le saut de `scrollIntoView`). Elle
  lit désormais l'opacité VUE (produit des parents, rien si caché) et laisse chaque mouvement arriver
  (`ScrollTrigger` : chaque inertie poussée à sa fin) avant de photographier.
- **Le premier écran** à 341 Ko à cause du fond du héros : il attend le rideau.
- Sur capture seulement : le ciel vide au tout début (rien n'était peint avant que la caméra bouge) ;
  la tienne trop petite ; la barre d'achat sur « Écrire la mienne » (et une deuxième fois après la
  première correction : l'inertie de GSAP finit APRÈS le dernier défilement, la boucle ne le voyait pas) ;
  la page blanche de la fin qui chevauchait le formulaire.
- Les traductions anglaises des phrases neuves étaient oubliées et **le build ne l'a pas dit** : `_traduire`
  ne refuse que les phrases françaises introuvables, pas les phrases NEUVES sans traduction. C'est
  `_qc_langues.py` qui protège ce cas.

## Les quatre demandes mises en attente

Voir `malettre/CONTEXT.md` § « À APPLIQUER, UNE PAR UNE » : la police du texte courant et la chasse à ce
qui fait IA (sans toucher aux animations), des bruitages et une zone de choix de l'occasion plus claire,
du verre partout, l'occasion « fête privée entre potes ».

## Le logo

Prompt donné à Mongazi : **le cachet aux trois points de suspension** (« Ma lettre à… ») plutôt qu'un
monogramme « M » (il en existe des milliers). Variantes : sur la nuit, en un trait d'or, icône, cachet brisé.
Son essai (le cachet BRISÉ, `_partage/Sceau de cire rouge brisé.png`) : neuf lobes, l'anneau d'or, mais la
fissure coupait le point du milieu, **on lisait quatre points**. Redessiné en vectoriel par
**`python malettre/_logo.py`** (graine fixe) : `logo/cachet.svg` (la marque), `logo/cachet-brise.svg` (la
fissure passe ENTRE le 2e et le 3e point), `logo/favicon.svg` (points crème, sans or : lisible à 16 px).
Le build en fait l'icône d'onglet et le cachet de la barre (en image dans la page, aucune requête).
⏳ Le nom « Ma lettre à… » posé à côté (en tracés, pour un fichier qui voyage) et l'image de partage `og.jpg`.

## La musique

Mongazi : « piano jazz rainy night » d'**Alex Morgan** (Pixabay), 3 min, mixé fort (-10,1 LUFS, 5,7 Mo).
**`python malettre/_son.py "<mp3>" "<auteur>"`** : volume égalisé (-16 LUFS, crête -1,5 dB), fondu
d'entrée 2 s et de sortie 4 s (la boucle respire au lieu de couper : un MP3 bouclé laisse un trou au
raccord), 96 kb/s, **2,1 Mo**, RE-MESURÉ après (-16,7 LUFS). Crédit au pied (« Musique : Alex Morgan, sur
Pixabay. »). ⛔ **Le MP3 n'est PAS dans le dépôt** (public ; la licence Pixabay interdit de redistribuer le
fichier seul) : `.gitignore`. Il part avec le site ; publier depuis un autre poste ferait disparaître le
bouton (sans casser la page).

## Les images qui vivent comme une vidéo

Mongazi : « dans la landing page ça doit être animé comme une vidéo, sans rien changer à l'animation
présente ». Il a choisi LES DEUX : tout de suite, ses images vivent en CSS (un lent travelling sur
chacune ; la flamme qui vacille au héros et à la plume ; deux rideaux de pluie sur la vitre du seuil ;
l'eau qui ondule sous l'horizon de la nuit ; la fumée de la cire des promesses ; le cachet tendu de la
fin qui respire ; la lumière du jour sur le lin du faire-part), transform et opacité seulement, **en pause
hors de l'écran**. Ensuite, ses vraies vidéos (prompts image-vers-vidéo donnés, une par zone, caméra fixe,
5-8 s, `_partage/ma lettre/videos/<zone>-paysage|portrait.mp4`) remplaceront ces mouvements : à alléger
(~1 Mo), boucle muette, chargées à l'approche, l'image gardée sur une connexion lente.
