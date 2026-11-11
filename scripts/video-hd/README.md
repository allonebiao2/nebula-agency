# VIDÉO HD · 4K et 60 images par seconde, avec l'IA, gratuitement

Outil personnel de Mongazi (2026-11-11). Il prend une vidéo et la rend :
- **plus grande** (jusqu'en 4K), grâce à **Real-ESRGAN** qui redessine les détails ;
- **plus fluide** (30 ou 60 images par seconde), grâce à **RIFE 4.25** qui fabrique les
  images manquantes entre deux vraies images.

Le son d'origine est gardé. Une vidéo verticale de téléphone reste verticale (2160 x 3840 en 4K).

## Le lancer : Google Colab, gratuit

Le PC de Cotonou n'a pas de carte graphique capable de faire tourner ces IA (Intel HD 5500,
sans Vulkan ni NVIDIA) : sur son processeur, une minute de vidéo prendrait des jours. Google
Colab prête gratuitement une carte NVIDIA T4, avec un compte Gmail et sans carte bancaire.

**Ouvrir le carnet directement :**
https://colab.research.google.com/github/allonebiao2/nebula-agency/blob/main/scripts/video-hd/Video_HD.ipynb

**Par Google Drive, sur téléphone comme sur ordinateur (le choix par défaut) :**
1. mettre la vidéo dans le dossier **Video-HD** de Google Drive (appli Drive → + → Importer) ;
2. ouvrir le lien ci-dessus, **Exécution → Tout exécuter** (sous ⋮ sur téléphone), autoriser le Drive ;
3. le résultat arrive dans **Drive → Video-HD → resultats**.

Sur ordinateur, on peut aussi envoyer la vidéo directement (réglage « Je l'envoie depuis cet
appareil ») : le bouton Parcourir apparaît, le résultat se télécharge. ⚠️ Sur téléphone, ce
chemin-là marche mal (l'envoi et surtout le téléchargement), d'où Drive par défaut.

Commencer par cocher **ESSAI_10_SECONDES** pour voir la qualité et le temps annoncé.

⚠️ Garder l'onglet ouvert. ⚠️ La carte est prêtée, pas garantie : aux heures chargées elle
peut manquer, et Google limite le temps d'utilisation gratuit par jour.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `video_hd.py` | **le moteur**, la seule vérité. Marche aussi en ligne de commande sur n'importe quel PC |
| `_carnet.py` | fabrique `Video_HD.ipynb` en y recopiant le moteur |
| `Video_HD.ipynb` | le carnet Colab. ⛔ **Jamais édité à la main** : on modifie `video_hd.py` puis `python _carnet.py` |

```bash
python video_hd.py ma_video.mp4                   # 4K, 60 images/s
python video_hd.py ma_video.mp4 --ips 30 --essai 10
python video_hd.py ma_video.mp4 --style anime     # dessin animé
python video_hd.py ma_video.mp4 --style max       # plus fin, beaucoup plus lent
```

## Comment il travaille

1. `ffprobe` lit la vidéo : taille, rotation du téléphone, cadence, son, HDR.
2. `ffmpeg` la décode image par image (cadence rendue régulière, HDR ramené en couleurs normales).
3. Chaque image passe dans Real-ESRGAN (x4 ou x2), puis est ramenée à la taille exacte.
4. Entre deux images agrandies, RIFE fabrique celles qui manquent pour atteindre 30 ou 60.
   **Pas d'image fabriquée à travers un changement de plan** : elle mélangerait deux scènes.
5. `ffmpeg` réencode au fil de l'eau (NVENC sur la carte, x264 sinon) et recolle le son.

Rien n'est entassé sur le disque : une minute en 4K60 ferait 90 Go d'images brutes.

## Les IA et leurs licences

| IA | Source | Licence | Poids |
|---|---|---|---|
| Real-ESRGAN | github.com/xinntao/Real-ESRGAN | BSD-3-Clause | publications GitHub du projet |
| RIFE 4.25 | github.com/hzwer/Practical-RIFE | MIT | `flownet_v4.25.pkl` publié par github.com/HolyWu/vs-rife (MIT) |

Les architectures sont recopiées dans `video_hd.py` (basicsr et vs-rife) pour ne dépendre
d'aucun paquet : `basicsr` casse avec les versions récentes de torchvision.

⚠️ L'agrandissement **invente** des détails plausibles, il ne retrouve pas ceux que la caméra
n'a pas captés. Sur un visage flou, le résultat est net mais peut ne pas ressembler tout à
fait à la personne.
