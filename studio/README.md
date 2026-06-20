# NEBULA Studio Quotidien

Agent créatif qui produit **chaque jour 2 contenus publiables totalement
différents** (script + vidéo verticale de marque) et les livre **sur Telegram
avant 13h**. Marques : NEBULA Agency, Vendora, AXIO IA. Marché : Afrique de
l'Ouest francophone.

## Comment ça marche
```
brain.py   → choisit un format/marque/angle JAMAIS récent (ledger.jsonl) et fait
             écrire à Claude (Opus) un concept complet (accroche, script, légende,
             hashtags, CTA, storyboard).
render.py  → transforme le storyboard en vidéo 1080×1920 de marque (motion design
             « Ethereal Glass »). mp4 (ffmpeg) ou webm. Gratuit, illimité.
heygen.py  → option premium : avatar parlant (STUDIO_VIDEO=heygen, crédits HeyGen).
deliver.py → envoie sur Telegram (vidéo + affiche + script).
run_daily.py → orchestre tout (2 posts/jour par défaut).
```
Le **registre `ledger.jsonl`** est la mémoire anti-répétition : il est relu à
chaque post et commité par l'automatisation, donc le studio ne se répète jamais.

## Lancer à la main
```bash
cd studio
export PYTHONIOENCODING=utf-8           # (Windows : set PYTHONIOENCODING=utf-8)
python run_daily.py                     # 2 posts : génère + vidéo + Telegram
python run_daily.py --no-send           # test sans envoi
python run_daily.py --no-video          # script seul
python run_daily.py --count=3           # 3 posts
```
Sorties dans `studio/out/<date>/post-N/` : `concept.json`, `script.md`,
`caption.txt`, `video.mp4`, `poster.png`.

## Automatisation (déjà en place)
`.github/workflows/studio-quotidien.yml` — cron `0 7 * * *` (07:00 UTC = **08:00
Cotonou**, avant 13h) + bouton « Run workflow ». Il génère, livre, et commit le
registre.

### Secrets GitHub requis (Settings → Secrets and variables → Actions)
| Secret | Rôle |
|---|---|
| `ANTHROPIC_API_KEY` | cerveau créatif (Claude) |
| `TELEGRAM_BOT_TOKEN` | bot de livraison |
| `TELEGRAM_CHAT_ID` | chat de Mongazi |
| `HEYGEN_API_KEY` | (optionnel) moteur avatar |

## Réglages (variables d'env)
- `STUDIO_COUNT` : nombre de posts/jour (défaut **2**).
- `STUDIO_VIDEO` : `kinetic` (défaut, gratuit) ou `heygen` (avatar, crédits).
- `STUDIO_MODEL` : modèle Claude (défaut `claude-opus-4-8`).

En local, les clés sont lues depuis l'environnement puis, à défaut, depuis les
`.env` voisins (`boutique-ia/.env`, `nebula-prospector/.env`, `secrets/heygen.env`).
Aucun secret n'est committé.
