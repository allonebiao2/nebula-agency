# 2026-11-11 · NEBULA REC, notre enregistreur d'écran (et ScreenRec supprimé)

## Ce que Mongazi a demandé
1. « screen record je veux aussi qu'on crée le nôtre » : enregistrer l'écran du PC **en 1080p et même en 4K**,
   un **logiciel PC simple**, « utilise ce qu'il faut ». Regarder avec REA comment ScreenRec fonctionne.
2. Une fois fini : **supprimer ScreenRec**, puis « mets tout à jour, commit and push, tout sur GitHub ».
3. En cours de route : « supprime toutes les vidéos faites avec screen record ».

## Ce que REA a montré de ScreenRec (tables d'import seulement, aucun code repris)
Qt 6 (QML + un Chromium complet, 142 Mo, pour le compte et le cloud), **FFmpeg 6** (avcodec, avformat,
avfilter, avdevice), `dxgi.dll` (lecture de l'écran), Opus, **RNNoise + WebRTC audio** (micro nettoyé),
`RegisterHotKey` (raccourci global), Sentry (rapports de plantage), onnxruntime (IA, chargée à la demande).
420 Mo installés. Notre version garde le principe : ffmpeg + capture Windows + puce vidéo + raccourci.

## Ce qui a été construit : `scripts/nebula-rec/`
- `moteur.py` (tout le travail vidéo), `nebula_rec.pyw` (fenêtre tkinter), `icone.py` (icône en Python pur),
  `installer.py` (copie dans `%LOCALAPPDATA%\Programs\NEBULA REC` + raccourcis Bureau et menu Démarrer),
  `_qc.py` (**49 contrôles verts**, dont de vraies captures), `README.md`.
- **Installé** sur le PC (raccourci « NEBULA REC » sur le Bureau). Vidéos dans `Vidéos\NEBULA REC`.
- Raccourcis : **Ctrl + Alt + R** démarrer / arrêter, **Ctrl + Alt + P** pause. La fenêtre est **exclue de la
  capture** (`SetWindowDisplayAffinity`, vérifié au pixel).
- Son : « Mixage stéréo » (son du PC, actif sur ce Realtek) + micro au choix, mélangés.
- Morceaux `.mkv` écrits **chaque seconde** : un PC coupé net ne perd qu'une seconde, la session est
  proposée à la récupération au lancement suivant (testé en tuant ffmpeg).

## Mesures sur ce PC (Intel HD 5500, écran 1366 x 768, 8 s)
| Essai | Résultat |
|---|---|
| `ddagrab` 30 i/s natif | 232 / 240 |
| `ddagrab` 60 i/s natif | 414 / 480 |
| 1080p agrandi en direct | 235 / 240 |
| **4K agrandie en direct** | **197 / 240 (24 i/s) : saccade** |
| **`gfxcapture` 30 i/s** | **240 / 240** |
| **`gfxcapture` 60 i/s** | **480 / 480** |

D'où : **on filme à la taille de l'écran, la 1080p ou la 4K se fait après l'arrêt** (« finition », lanczos,
barre de progression, annulable). ⚠️ Écran 1366 x 768 : la 4K est **agrandie, pas plus détaillée** (dit
dans le logiciel). Avec un vrai écran 4K, capture native.

## Les pièges rencontrés
- ⛔ **`ddagrab` dessine CHAQUE curseur dans un carré blanc** (main, texte, flèche : planche comparée,
  curseur imposé par un carré gris sous la souris). `gfxcapture` (Windows.Graphics.Capture) laisse
  Windows dessiner le curseur : juste. `ddagrab` ne sert plus qu'en secours (Windows < 1903).
- ⚠️ **Lancer ffmpeg affiche le curseur « démarrage » (flèche + sablier)**, filmé au début de chaque vidéo :
  `STARTF_FORCEOFFFEEDBACK` (0x80) dans `STARTUPINFO`.
- Quick Sync sur Broadwell : `hwmap=derive_device=qsv` depuis D3D11 échoue, `scale_d3d11` et `vpp_qsv`
  aussi ; la QSV ne s'ouvre qu'en `child_device_type=dxva2`. Solution retenue : image téléchargée en
  mémoire (`hwdownload`), codage QSV depuis la mémoire système.
- Un `.mkv` tué n'avait **rien** sur le disque (ffmpeg garde 5 s de blocs) : `-cluster_time_limit 1000
  -flush_packets 1`.
- Premier lancement : **75 s de préparation** (mémoire saturée, test de la puce). Un appui sur Enregistrer
  pendant ce temps était ignoré : il démarre maintenant dès que c'est prêt. Lancements suivants : ~10 s.
- `Windows.Graphics.Capture` sur Windows 10 peut afficher un cadre jaune : **mesuré absent** ici.
- Tests de bout en bout pendant que Mongazi utilisait le PC : les essais de forme de curseur ont été
  arrêtés dès qu'ils devenaient gênants (curseur changé une seconde, jamais déplacé).

## ScreenRec supprimé
- **Ses enregistrements étaient cachés** dans `AppData\Local\StreamingVideoProvider\screenrec\Records`
  (4 vidéos du 2026-08-08 + miniatures) : mis à l'abri AVANT la désinstallation, puis, à la demande de
  Mongazi, **envoyés à la Corbeille** (12 fichiers, récupérables tant qu'elle n'est pas vidée).
- Désinstalleur NSIS silencieux (`/S`), puis restes supprimés : dossier du logiciel, 127 Mo dans
  `AppData\Local\StreamingVideoProvider` (dont une ancienne copie de 2025), `AppData\Roaming`, entrée de
  démarrage, clé `HKCU\Software\StreamingVideoProvider`.

## Ce qui reste
- ⏳ Mongazi doit l'essayer lui-même (raccourci sur le Bureau) et dire ce qui manque.
- Idées pour une suite : zone ou fenêtre seule, webcam en incrustation, son d'un casque Bluetooth (boucle
  WASAPI au lieu de « Mixage stéréo »), micro nettoyé (RNNoise, comme ScreenRec).
- Icecream Screen Recorder est toujours installé (démarrage coupé) : non demandé.
