# Le personnage-vidéo : une vidéo générée, détourée, posée dans une scène three.js

> LE MONDE, 2026-11-14. Mongazi : « comment faire pour que ce soit ultra réaliste ? », « les visages, le maximum
> possible ». Code : `monde/socle/perso-video.js` ; préparation : `monde/_outils/perso_video.py` ; regard :
> `monde/_outils/captures/voir_perso_video.py` (3D contre vidéo, téléphone et ordinateur, `--nuit`).

## L'idée

Ses vidéos image → vidéo sont photoréalistes ; c'est le passage en 3D qui les détruisait (TRELLIS ne donne qu'une
centaine de pixels de texture au visage ; Mixamo, un mouvement générique). Là où l'on voit un visage de près (la
conversation : elle fait face au visiteur, caméra cadrée, fond flou), on montre **la vidéo elle-même** sur un plan
tourné vers la caméra ; le modèle 3D reste là, invisible, et continue de donner la tête (cadrage, étiquette) et
les ombres des pieds. Hors conversation (elle marche, de loin), c'est la 3D.

## Les choix techniques, et pourquoi

- **La transparence lisible PARTOUT** : couleur à gauche, opacité à droite, dans UNE vidéo H.264 (`yuv420p`,
  profil High, niveau 4.0, `+faststart`). Le WebM VP9 transparent ne passe pas sur iPhone (Mongazi en a un) ; le
  HEVC transparent ne passe que sur Apple. Le shader lit les deux moitiés.
- **Le détourage** : rembg `isnet-general-use` (178 Mo) suffit sur un fond gris uni : cheveux crépus, mains,
  pieds nets. Environ **4 s par image** sur ce PC (180 images = 12 à 15 min) : un seul détourage à la fois.
- **Lissé dans le temps** : médiane sur 3 images. Un bord qui scintille trahit le montage plus qu'un bord flou.
- **Le gris du fond retiré des bords** : couleur vraie = (pixel − (1 − α)·fond) / α, le fond estimé sur les bords
  de chaque image. Aucun halo, même le soir.
- **Le cadre stabilisé** : les générateurs zooment doucement (2 % en 7 s sur `afi-parler`). On mesure la tête et
  les pieds sur le masque, on lisse sur 9 images, et chaque image est ramenée à la taille et à la place de la
  première. Sans ça, la personne grandit pendant qu'elle parle.
- **Les fins de vidéo** : un générateur finit souvent par un fondu vers un autre plan (dernière image de
  `afi-parler`, coupure à 7,6 s dans `senami-parler`). On cherche la coupure par l'écart moyen entre images
  (au-dessus de 6 sur 255 à 8 i/s) et on s'arrête avant.
- **La boucle** : aller-retour quand la fin ne rejoint pas le début (15 s au lieu de 7,6, sans saut).
- **« Écouter » quand il n'existe pas de vidéo où elle écoute** : `--calme 3` cherche le passage de 3 s où le
  VISAGE bouge le moins (écart moyen entre images, dans le haut de la silhouette), rejoué à 0,85. Afi : −32 % de
  mouvement. Mieux qu'une image figée (morte) ou que « parler » (elle parlerait en écoutant).
- **La couleur** : la vidéo est en sRVB ; la texture est déclarée SANS espace de couleur et décodée dans le
  shader (`sRGBTransferEOTF`), sinon un navigateur la décode et l'autre non.
- **La lumière du lieu** : le soir, plus bas et plus chaud (le manteau rejoint la teinte du sol, mesuré sur les
  pixels), et la lumière qui tombe d'en haut (la tête et les épaules plus éclairées que les jambes, comme sous un
  spot). De jour, presque neutre.
- **La bascule** : ≈ 0,3 s, pendant que la caméra se cadre ; la 3D se cache dès que la vidéo couvre (0,6), sinon
  on voit deux personnes l'une dans l'autre.
- **Le poids** : 960 px de haut (540 de large par moitié), CRF 24 : **1,3 Mo** pour « parler » (15 s en
  aller-retour), **0,4 Mo** pour « écouter ». Chargés APRÈS le premier écran.

## Ce qu'on a vu

Planche `monde/_vues/video-contre-3d.jpg` (jour) et `-nuit.jpg` : la 3D d'Afi a un visage de cire sombre et des
mains en griffes ; la vidéo est une vraie femme qui sourit, au manteau qui tombe juste, posée dans le salon. Le
zoom du visage, le soir, ne montre aucun bord gris.

## Ce qui reste possible

- Une version 1280 px pour l'ordinateur (la source fait 1280 : aucun agrandissement), la 960 restant au téléphone.
- Des vidéos tournées pour la boucle (première image = dernière, consigne dans `personnages/CONSIGNES.md`).
- Le personnage-vidéo qui marche : impossible tant qu'il ne marche que vers la caméra ; la 3D garde la marche.
