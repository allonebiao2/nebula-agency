# SKILLS & OUTILS INVOQUÉS (création Djambar Team — référence)

> Inventaire **exhaustif** de tout ce qui a été invoqué/utilisé pendant la création actuelle.
> Le futur skill devra orchestrer ces mêmes briques. Versions constatées le 2026-06-22.

## A. Skills (Claude Code)
| Skill | Rôle | Comment invoqué |
|---|---|---|
| **`ui-ux-pro-max`** | Design intelligence (67 styles, 96 palettes, 57 paires de polices, stacks). Génère un **design system grounded**. | Installé via npm `uipro-cli` (v2.2.3) → `.claude/skills/ui-ux-pro-max/`. Usage : `python .claude/skills/ui-ux-pro-max/scripts/search.py "<requête>" --design-system -p "<Marque>" -f markdown` (+ `--domain style/typography/color/landing`, `--stack html-tailwind`). |
| **`impeccable`** | QA design **automatique** (hook PostToolUse à chaque écriture HTML/CSS). Détecte em-dash overuse, single-font, overused-font, gradient-text, etc. | Tourne tout seul. Audit manuel : `/impeccable audit`. Ignorer une règle (avec confirmation user) : `/impeccable hooks ignore-value … --shared`. |

> ⚠️ **Faux positifs récurrents à connaître** :
> - `single-font` : déclenché car le **CSS est partagé** (`app.css`) et le hook scanne 1 fichier HTML à la fois ; la paire Cormorant+Jost est pourtant bien active. → **classer faux positif**, ne pas inliner les polices.
> - `overused-font` (Montserrat) : **vrai** signal de goût → on est passés à **Jost**.

## B. Outils Python
| Outil | Version | Rôle | Note |
|---|---|---|---|
| **Pillow** (`PIL`) | 12.2.0 | Pipeline images : détourage logo (bbox alpha), crops, resize+compression JPEG progressive, favicon/apple-touch, **images OG sociales** (ImageDraw + polices système Georgia/Arial). | Script `_build_assets.py` (ré-exécutable). |
| **segno** | 1.6.6 | Génération **QR codes** (WhatsApp + Maps), couleur navy, PNG. | `pip install segno`. Pur Python, sans dépendance. |
| **http.server** | (stdlib) | Aperçu local : `python -m http.server <PORT> --directory <client>` → **lien localhost** (règle : on envoie le lien, pas des captures, au client). | — |

## C. Outils système / CLI
| Outil | Rôle | Commande clé |
|---|---|---|
| **Microsoft Edge (headless)** | **Captures** QA (desktop/mobile) + **rendu PDF** A4 + `--dump-dom` (mesure overflow). | `--headless --disable-gpu --no-sandbox --user-data-dir=… --virtual-time-budget=N --screenshot=… ` / `--no-pdf-header-footer --print-to-pdf=…`. Chemin : `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`. |
| **wrangler** (via `npx`) | Déploiement **Cloudflare Pages**. | `npx --yes wrangler@latest pages project create <p> --production-branch=main` puis `… pages deploy _dist --project-name=<p> --branch=main --commit-dirty=true`. Token : `secrets/cloudflare.env` (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`) — chargé via `set -a; source …; set +a`, jamais affiché. v4.103.0. |
| **npm / npx** | npm 10.9.2, node v22.14.0. Installer le skill / lancer wrangler. | `npm install -g uipro-cli`. |
| **git** | Versioning. **Stage sélectif** (pas de `git add -A`), commit `Co-Authored-By`, push selon validation. | `git add <chemins>` ; `git commit -m …` ; `git push origin main`. |

## D. Outils internes Claude Code (harness)
- **AskUserQuestion** : cadrage (≤4 questions, reco en 1er).
- **Write / Edit / Read / Glob / Grep** : fichiers (préférer aux commandes shell).
- **Bash (git-bash POSIX)** + **PowerShell (Win)** : selon la syntaxe. ⚠️ ne jamais éditer `.py`/`.html` via `Set-Content` (mojibake).
- **WebFetch** : vérifier une source (ex : page d'install d'un plugin) avant d'agir.

## E. Environnement
- OS Windows 10 ; repo `C:\Users\USER\nebula-agency` ; déploiement **Cloudflare Pages** (vitrines) ; DNS souvent **Hostinger**.
- Secrets dans `secrets/*.env` (jamais commités, jamais affichés). `.claude/`, `.wrangler/`, `*.env` **gitignorés**.

## F. Ordre d'invocation observé (Djambar Team)
1. `npm install -g uipro-cli` → `uipro init --ai claude` (installe le skill `ui-ux-pro-max`).
2. `/ui-ux-pro-max` → `search.py --design-system` (design system).
3. Write `app.css` / `app.js` / pages → **hook `impeccable`** à chaque écriture.
4. `_build_assets.py` (Pillow) : logo + favicons + OG + galerie.
5. `pip install segno` → QR.
6. `http.server` + **Edge headless** (captures + mesure overflow `--dump-dom`).
7. Edge `--print-to-pdf` (affiche A4).
8. `npx wrangler pages deploy` (Cloudflare Pages).
9. `git` (commit/push) + mise à jour mémoire.
