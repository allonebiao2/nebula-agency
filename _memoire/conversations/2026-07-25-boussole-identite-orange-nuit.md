# 2026-07-25 — Boussole : identité visuelle « ORANGE & NUIT » (2 thèmes, animations intactes)

## Demande (avec 4 images de référence)
Interface dans l'esprit des références : **orangé + noir en thème sombre**, **orange + blanc en thème clair**, **ultra soigné et épuré**, **sans changer les animations actuelles**.

## Lecture des références
Cartes très arrondies, **aplats de couleur pleins** (une carte orange, une sombre, une blanche), **boutons pill**, barre de navigation à pastilles avec **onglet actif en aplat orange**, beaucoup d'air, aucune couleur parasite.

## Méthode : tokeniser avant de recolorer
Le fichier contenait **646 hex + 338 rgba en dur** (CSS *et* styles inline générés par le JS). Un simple « changement de couleurs » aurait été ingérable et n'aurait jamais permis un thème clair.
1. **Bloc de tokens** sur `:root` (+ `:root[data-theme="light"]`) : `--fg` / `--sh` en **composantes RVB** (donc réutilisables dans `rgba()`), `--bg --bg2 --ink --ink2 --tx --tx2 --line --acc --acc2 --acc3 --on-acc --good --bad --card-r`.
2. **Remplacement mécanique** : `rgba(255,255,255,x)` → `rgba(var(--fg),x)` (226 occurrences), `rgba(0,0,0,x)` → `rgba(var(--sh),x)`, `color:#fff` → `var(--tx)` (65).
3. **Mapping de palette** : or ambre `#f6a63c` → **orange `#ff8a1e`**, jaunes → `--acc2`, fonds bleutés (`#0B0F19`, `#0C0B10`) → **noir chaud `#0a0a0c`**, surfaces opaques → `--ink`.

## Palette
| | Sombre | Clair |
|---|---|---|
| Fond | `#0a0a0c` (noir chaud, plus aucun bleu) | `#fffdfb` / `#fff6ec` |
| Surfaces | `--ink #17171b` | blanc pur, ombres chaudes |
| Texte | blanc / 62 % | `#17110a` / 62 % |
| Accent | **`#ff8a1e`** + `#ffb020` | **`#f97316`** + `#fb9d3a` |
| Sémantique | vert `#2fd18a`, rouge `#ff4d5e` | vert `#0f9d63`, rouge `#e11d48` |

## Décisions de design
- **VENDRE devient l'aplat orange plein** (l'action reine, comme le bouton principal des références) ; **DÉPENSER** reste une carte sobre — surface blanche dédiée en thème clair, sinon il disparaissait.
- **Onglet actif de la barre = aplat orange** (au lieu d'un halo), sans glow.
- **Arrondis uniformisés** via `--card-r: 22px` (16/18 px → 22).
- **Épure = une seule famille de couleur** : les 6 teintes disparates des tuiles de caisse (violet, rose, vert, cyan…) deviennent **6 nuances d'orange** ; accents d'écran froids (violet/sky/bleu) réchauffés.
- Liseré « doré vivant » et shimmer du titre **calmés** (moins de couleur, plus de contraste).
- Les halos de fond passent en `color-mix` sur l'accent : ils suivent le thème.

## Bascule de thème
Bouton **dans le pied du tiroir** (à côté du son) : lune/soleil + libellé. **Suit `prefers-color-scheme` par défaut**, le choix manuel est mémorisé (`boussole:theme`) et `<meta name="theme-color">` suit.

## Correctifs trouvés au contrôle visuel du thème clair
1. Le `background` du `body` était **déclaré deux fois** (`var(--bg)` puis `#0C0B10` en dur) → le fond restait noir en clair. Une seule déclaration, sur le token.
2. **Barre du bas** restée sombre (dégradé en dur) → `color-mix(var(--ink))`.
3. **Scanlines du titre** visibles comme des rayures sur fond clair → masquées en thème clair.

## QC
Captures des **2 thèmes × 4 écrans** (onboarding, accueil, caisse, bilan) + contrôle du couple fond/texte calculé. **Non-régression des 8 suites (v4→v11) : toutes vertes**, 0 erreur console → **aucune animation n'a été modifiée**, conformément à la demande.

Aperçu republié (même URL) : https://claude.ai/code/artifact/3c6705ae-b701-4337-ae47-c758a643572f

## Règle qui en découle
**Ne jamais recoder une couleur en dur dans Boussole** : tout passe par les tokens, sinon le thème clair casse silencieusement.

Cf [[2026-07-25-boussole-visite-guidee-aide]].
