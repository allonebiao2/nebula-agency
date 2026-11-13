# Les scripts de capture du salon (recopiés du dossier temporaire le 2026-11-13)

Tous supposent le serveur lancé (`python monde/_servir.py --sans-construire`, port 8765) et écrivent
dans `monde/_vues/`. **Un seul à la fois** : ce PC a 8 Go, deux navigateurs Playwright le saturent.

| Script | Ce qu'il fait | Commande |
|---|---|---|
| `filmer_intro.py` | filme l'ouverture cinéma (rue, travelling, portes, projecteurs) ; argument = l'heure | `python monde/_outils/captures/filmer_intro.py` (nuit) · `... filmer_intro.py 14` (jour) |
| `filmer_dialogue.py` | conversation avec Hillary puis avec Afi, **par le vrai parcours** (toucher Afi, options, « Parler »), ordinateur en qualité haute et téléphone → `{ordi,tel}-scene-{hillary,afi}.png` | `python monde/_outils/captures/filmer_dialogue.py` |
| `sonde_cadre.py` | mesure la caméra (position, tangage, champ) et projette les os de la tête d'Afi à l'écran pendant une conversation, journalise chaque `tournerVers` et `cadrer` → `sonde-cadre.png` | `python monde/_outils/captures/sonde_cadre.py` |
| `voir_dehors.py` | l'arrivée dehors (avant « Entrer ») au téléphone, puis le rendu cinéma à l'ordinateur | `python monde/_outils/captures/voir_dehors.py` |
| `preuves_revue.py` | les preuves demandées par la revue Impeccable (intérieur, réplique d'ambiance, étiquette au bord droit) | `python monde/_outils/captures/preuves_revue.py` |

Autres outils recopiés :
- `monde/_outils/generer_visiteuses.py` : prend les DEUX premiers blocs de code de
  `personnages/CONSIGNES.md` (Sènami, puis Maman Sènami), fait deux images de chacune par
  `scripts/image_cf.py` (Cloudflare, `flux-2-dev`, 1024 px) → `<dossier>/senami-1.jpg`, `senami-2.jpg`,
  `maman-1.jpg`, `maman-2.jpg`. À lancer depuis la racine du dépôt :
  `python monde/_outils/generer_visiteuses.py <dossier de sortie>`. ⚠️ Regarder l'âge sur chaque image.
- `monde/_outils/design_sidecar.py` : régénère le fichier compagnon d'Impeccable depuis `DESIGN.md` :
  `python monde/_outils/design_sidecar.py monde/DESIGN.md monde/.impeccable/design.json`.
