# Filmer l'écran de Windows avec ffmpeg (2026-11-11)

Appris en construisant NEBULA REC (`scripts/nebula-rec/`), mesuré sur un Core i5-5300U / Intel HD 5500.

## La source : `gfxcapture`, pas `ddagrab`
- `ddagrab` (Duplication du bureau, DXGI) **dessine chaque curseur dans un carré blanc** : main, texte, et
  même la flèche (ffmpeg 9.0.2, build gyan.dev). Défaut visible dans toutes les vidéos.
- `gfxcapture` (Windows.Graphics.Capture, Windows 10 1903 et plus) : c'est Windows qui compose le curseur,
  il est juste. Plus régulier aussi : 240/240 images à 30 i/s et 480/480 à 60, contre 232 et 414.
- Les deux livrent des images D3D11 : `hwdownload,format=bgra`, puis `fps=N` (Windows n'envoie une image que
  si l'écran change), puis `crop=trunc(iw/2)*2:trunc(ih/2)*2,format=nv12` pour l'encodeur.

## Ne pas se filmer soi-même
`SetWindowDisplayAffinity(hwnd, 0x11)` (WDA_EXCLUDEFROMCAPTURE) : la fenêtre disparaît des captures, que ce
soit par `ddagrab` ou par `gfxcapture`. Vérifié au pixel avec une fenêtre magenta et son témoin.
Avec tkinter, la vraie fenêtre est `GetAncestor(winfo_id(), 2)`.

## Le curseur « démarrage » qu'on filme sans le vouloir
Tout lancement de processus affiche quelques secondes la flèche + sablier. Lancer ffmpeg avec
`STARTUPINFO.dwFlags |= 0x80` (STARTF_FORCEOFFFEEDBACK).

## Quick Sync sur une vieille puce Intel (Broadwell)
- `-init_hw_device qsv` échoue (session MFX -9) ; il faut `qsv=hw:hw_any,child_device_type=dxva2`.
- `hwmap=derive_device=qsv` depuis D3D11, `scale_d3d11`, `vpp_qsv` : échouent.
- Ce qui marche : image en mémoire système, puis `-c:v h264_qsv` (session interne). Agrandir en direct
  par le processeur tient la 1080p à 30 i/s, **pas la 4K** (24 i/s) : agrandir après coup.

## Écrire un fichier qui survit à une coupure
`.mkv` avec `-cluster_time_limit 1000 -flush_packets 1`. Sans ça, ffmpeg tué ne laissait que l'en-tête.
Arrêt propre : écrire `q` sur l'entrée de ffmpeg (stdin en tube), pas le tuer.

## Le son
DirectShow : « Mixage stéréo » = son du PC (haut-parleurs seulement, pas un casque Bluetooth) ;
`-audio_buffer_size 50` sinon le son arrive ~0,5 s en retard ; deux sources : `amix=normalize=0`.
