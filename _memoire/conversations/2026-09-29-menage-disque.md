# Ménage du disque et de `_partage/` (2026-09-29)

Mongazi : « vide-moi le dossier partagé, vide le cache et libère de la mémoire dans
nebula-agency, et vérifie sur le PC tout ce qu'on peut supprimer ». Le disque C: était
plein à 96 % (13 Go libres). En fin de session : **138 Go libres**.

## Dans le dépôt

- **`_partage/` est vide** (seul `.gitkeep`, suivi, reste). Les planches d'essai
  (`_planche-*`, régénérables) et le cache `.impeccable/` sont supprimés.
- **Archivé dans `_archives/partage-2026-09-29/`** (17 Mo, ignoré par git, comme le
  vidage du 2026-07-02) : `capture de la methode/` (captures, CSV, résultats 0007 à
  0009), `la methode.pdf`, la vidéo snaptik et une capture d'écran du jour.
  ⚠️ **Ces fichiers de la méthode de trading n'étaient ni sur GitHub ni dans
  `nebula-trader`** au moment du vidage : voir `RESTE-A-FAIRE.md`.
- **Worktree `.claude/worktrees/angy-photos` supprimé** (1,1 Go) avec sa branche
  `worktree-angy-photos`, déjà contenue dans `main`. ⚠️ Il contenait **130 fichiers
  ignorés par git qui n'existaient nulle part ailleurs**, recopiés dans `main` et
  vérifiés octet par octet AVANT la suppression :
  - `clients/10-hillary-m-styl/_sources/` : 26 fichiers (détourages et modèles
    orange, tulle, verte, violette, robe de ville violette, sons bruts) ;
  - `benin-mon-pays/_sources/candidats/` : 81 photos candidates (370 Mo) ;
  - `benin-mon-pays/_sources_sons/` : les 8 ambiances.
- **Caches supprimés** : `_studio-video/node_modules/.cache/webpack` (388 Mo) et
  `clients/09-au-braise-dor/experience/.next` (94 Mo). Ils se refont au prochain
  rendu ou build.
- Rien n'est commité par ce ménage (tout ce qui a bougé est ignoré). Les modifications
  en cours de `_studio-video/` (le montage « dimanche ») sont antérieures et intactes ;
  il lit sa propre copie `public/dimanche/source.mp4`, pas la vidéo archivée.

## Sur le PC (hors dépôt)

- Cache CapCut (24,4 Go) et ses journaux réseau (1 Go), 7 anciennes versions de CapCut
  (~11 Go, la 6.6.1 reste), fichiers temporaires Windows, vieil installeur LM Studio.
- Téléchargements : 141 fichiers, 65 Go (films, films Telegram, installeurs, doublons,
  téléchargements incomplets). `Vidéos\RMI edit` (20,7 Go), confirmé par Mongazi.
- Historique FTMO de MetaTrader (1,9 Go). **Tout Deriv est gardé** (le terminal ouvert,
  `C:\Program Files\MetaTrader 5 Terminal`, est celui de nebula-trader).
- Veille prolongée désactivée par Mongazi (`powercfg /h off`) : `hiberfil.sys` (3,4 Go)
  a disparu.

## Gardé exprès

Tout ce qui touche Claude (application et sa machine virtuelle de 12 Go, installeurs
Claude et Codex, caches de Chrome où tourne l'extension), le modèle Whisper de 1,6 Go
(il sert au montage « dimanche »), Playwright (les QC), `D:\séries2` (Big Bang Theory),
les rushes perso uniques de Téléchargements (`IMG_0125.MOV`, `C0043 2.MP4`, `C0478.MP4`).

## Incident

La mémoire vive (8 Go) était saturée pendant les effacements : l'Explorateur Windows
s'est figé (fond d'écran seul, plus de barre des tâches). Relancé, puis le défilement
du pavé tactile a cessé : le programme Synaptics `SynTPEnh.exe` relancé, tout remarche.

## Ce qui reste

- Les anciennes versions de VS Code (~5,9 Go) : Mongazi dit « plus tard ».
- Déplacer l'archive de la méthode de trading dans `nebula-trader` (dépôt privé).
