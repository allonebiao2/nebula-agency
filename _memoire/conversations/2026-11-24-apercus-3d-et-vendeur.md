# 2026-11-24 (après-midi et soir) · aperçus en 3D, vendeur animé, file des aperçus

Détail privé (numéros, messages envoyés) : `nebula-cap/REPRENDRE-ICI.md` et `nebula-apercus/PLAN-APERCUS-25-11.md`.

## Ce qui a changé dans la façon de vendre
- **Appels à partir de la semaine prochaine** : l'appel fait écrire le client en premier (« écrivez-moi OK sur
  WhatsApp »), donc la limite des nouveaux contacts ne joue plus pour lui. Messages froids : 5 par jour cette semaine,
  8 ensuite, jamais deux fois le même texte. Fiche d'appel : qui, son vrai problème, ce qui fait céder, 2 objections.
- **Le blocage des prospects, c'était le devoir qu'on leur donnait** (« envoyez photos et prix »). Avec « vous n'avez
  rien à envoyer, je prends dans votre catalogue WhatsApp », trois oui en 30 minutes. On va chercher leurs produits
  nous-mêmes (catalogue WhatsApp, fiche Google).
- **Décisions de Mongazi** : 3 aperçus par jour ; un aperçu part dès qu'il est prêt ; prix toujours « 50 000 F »
  avec « -20 % en ce moment, 40 000 F jusqu'au <jour> » (échéance propre à chacun, ~72 h, tenue) ; aperçu sans
  réponse retiré au 7e jour (page « Aperçu terminé ») ; les 34 prospects dormants relancés 3 par jour dès jeudi ;
  rachat du code d'un site sur devis ; le « vendeur qui parle » inclus partout, **option IA +25 000 F** ;
  chaque message de livraison dit « glissez sans vous arrêter jusqu'en bas », « ce n'est pas la version finale,
  tout est modifiable (détourage…) », et que l'assistant vendeur mène à WhatsApp.
- **La file des aperçus** : un par un, on ne coupe jamais un aperçu commencé, un nouveau client va en bas.

## Ce qui a été construit (dépôt privé `nebula-apercus`)
- **Quesiah** (savon noir) : aperçu d'Altaïr repris et corrigé (feuilles devant les produits, mousse, cartes, anneau),
  3D + conseillère qui pose des questions et vend, `conseil.json` séparé pour une IA plus tard.
- **Moteur 3D commun** `_express/_signatures/voyage3d.js` (Three.js r180) + **un monde par client**
  `monde-<slug>.js` : ARIO = l'atelier de gravure de nuit (le laser grave ARIO, ampoules au premier plan, cadeaux
  accrochés sous des faisceaux), Highgameshop = l'arène néon (grille, soleil rétro, socles hexagonaux).
- **Le vendeur dessiné et animé** commun `_express/_signatures/avatar.js` (cligne, parle, 3 humeurs, habillé par
  métier). Mongazi l'exige sur chaque aperçu.
- **ARIO** : atelier « Écrivez. On grave. » avec support (porte-clés, médaillon, plaque), motif (cœur, lauriers,
  étoile, alliances, logo) et texte ; devis en quantité sur chaque fiche ; photos tirées de SA fiche Google.
- **Highgameshop** : produits d'EXEMPLE (photos libres Wikimedia, créditées) en attendant les siens.
- **Musiques par univers** (Pixabay) : synthwave, guitare acoustique chaude, kalimba. Jamais celle par défaut.
- **Max (OVRSZ, vitrine offerte)** : vidéo de référence décortiquée (la tringle où les vêtements pivotent de face),
  cahier `nebula-apercus/max-ovrsz/DECORTIQUE-REFERENCE.md`.

## Leçons
- Un aperçu « base + effets » a été jugé « beaucoup trop basique » : la barre est la 3D immersive au défilement.
- Les photos d'un produit blanc sur fond blanc se détourent mal (le blanc du produit part avec le fond).
- Même débit = même taille de fichier : on prouve une musique servie par son empreinte, pas par sa taille.
- `wrangler` hors interactif exige `CLOUDFLARE_API_TOKEN` : charger `secrets/cloudflare.env`.
