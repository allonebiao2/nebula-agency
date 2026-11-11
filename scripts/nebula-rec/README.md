# NEBULA REC · enregistreur d'écran

Un logiciel PC simple pour filmer l'écran, avec le son du PC et le micro, en **taille réelle, 1080p ou 4K**,
à **30 ou 60 images par seconde**. Gratuit, sans compte, sans filigrane, sans rien envoyer sur Internet.

## Installer

```bash
winget install Gyan.FFmpeg                 # une seule fois, si ffmpeg n'est pas déjà là
python scripts/nebula-rec/installer.py     # pose « NEBULA REC » sur le Bureau et dans le menu Démarrer
```

Relancer `installer.py` après toute modification du code : le logiciel installé est une **copie**
(`%LOCALAPPDATA%\Programs\NEBULA REC`), pour qu'une opération git ne le casse pas pendant qu'il tourne.
Désinstaller : `python scripts/nebula-rec/installer.py --retirer` (les vidéos ne sont jamais touchées).

## S'en servir

1. Ouvrir **NEBULA REC**, choisir la qualité, les images par seconde, le son.
2. **Enregistrer**, ou **Ctrl + Alt + R** de n'importe où. **Ctrl + Alt + P** met en pause.
3. **Ctrl + Alt + R** encore : la vidéo est rangée dans `Vidéos\NEBULA REC`, nommée
   `Écran 2026-11-11 à 14h32 (4K).mp4`.

La fenêtre de NEBULA REC **n'apparaît pas dans la vidéo** (Windows l'exclut de la capture).

## Comment il marche

| Étape | Outil | Pourquoi |
|---|---|---|
| Lire l'écran | `gfxcapture` de ffmpeg (Windows.Graphics.Capture) | c'est Windows qui dessine le curseur, donc il est juste |
| Coder la vidéo | la puce vidéo (Intel Quick Sync ici, NVIDIA ou AMD ailleurs), sinon le processeur | le PC reste fluide pendant l'enregistrement |
| Le son | DirectShow : « Mixage stéréo » pour le son du PC, le micro pour la voix | inclus dans Windows |
| Écrire | morceaux `.mkv`, un bloc par seconde | une coupure de courant ne perd qu'une seconde |
| Finir | recollage en `.mp4`, puis agrandissement en 1080p ou 4K (lanczos) | voir ci-dessous |

**Pourquoi la 4K est faite après l'arrêt.** Mesuré le 2026-11-11 sur le PC de Cotonou (Intel HD 5500, écran
1366 x 768) : agrandie en direct, la 4K ne tient que 24 images par seconde sur 30 et la vidéo saccade. On filme
donc à la taille de l'écran, et l'agrandissement se fait à l'arrêt (barre de progression, annulable).
⚠️ **Agrandir n'ajoute pas de détails** : un écran 1366 x 768 filmé « en 4K » donne une vidéo plus grande, pas
plus fine. Avec un vrai écran 4K, la capture est en 4K native.

**Pourquoi pas `ddagrab`** (la Duplication du bureau, l'autre source de ffmpeg) : sur ce PC il dessinait
**chaque curseur dans un carré blanc** (main, texte, et même la flèche). Il ne reste qu'en secours sur un
Windows antérieur à 1903.

| Mesuré sur ce PC (8 s) | `ddagrab` | `gfxcapture` |
|---|---|---|
| 30 images/s | 232 / 240 | 240 / 240 |
| 60 images/s | 414 / 480 | 480 / 480 |
| curseur | carré blanc | juste |

**Robustesse.** Si le logiciel ou le PC s'arrête pendant un enregistrement, la session est retrouvée au
lancement suivant et proposée à la récupération. Si ffmpeg s'arrête seul (écran verrouillé, micro débranché),
ce qui a été filmé est gardé.

## Limites connues

- Le **son du PC** passe par « Mixage stéréo » : c'est le son des haut-parleurs du PC, **pas celui d'un casque
  Bluetooth**. S'il n'apparaît pas : Paramètres du son → Panneau de configuration Son → Enregistrement →
  clic droit → Afficher les périphériques désactivés → activer « Mixage stéréo ».
- Plein écran seulement (pas encore de zone ni de fenêtre seule), pas de webcam en incrustation.

## Fichiers

| Fichier | Rôle |
|---|---|
| `nebula_rec.pyw` | la fenêtre (tkinter), les raccourcis clavier, la récupération |
| `moteur.py` | tout le travail vidéo (ffmpeg), testable sans fenêtre |
| `icone.py` | l'icône, dessinée en Python pur |
| `installer.py` | installation, mise à jour, désinstallation |
| `_qc.py` | contrôles : `python scripts/nebula-rec/_qc.py` (sans filmer), `--reel` (vraies captures, ~3 min) |

Aucune dépendance hors Python 3 et un ffmpeg récent (9.0 sur ce PC ; les vieilles versions n'ont pas
`gfxcapture` et le logiciel retombe alors sur `ddagrab`).
