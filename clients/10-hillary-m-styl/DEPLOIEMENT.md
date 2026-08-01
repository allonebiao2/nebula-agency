# HILLARY M. STYL — LE DÉPLOIEMENT

> **À lire par Claude Code dans le terminal de Mongazi, avant tout déploiement.**
> Dernière mise à jour : 2026-08-01.

---

## ⚠️ LE PIÈGE, EN UNE PHRASE

**La V3 « LE FIL » n'est PAS sur `main`.** Elle vit sur la branche
`claude/github-repo-context-nisd2r`.

Si vous déployez depuis `main`, vous **redéployez l'ancienne version** — celle qui est
déjà en ligne, sans direction artistique. Le site n'aura pas bougé, et on croira que
le déploiement a échoué alors qu'il aura parfaitement fonctionné.

**Comment le vérifier en une commande, sans réfléchir :**

```bash
grep -c "Bodoni Moda" clients/10-hillary-m-styl/vitrine.html
```

| Résultat | Signification |
|---|---|
| **0** | ⛔ vous êtes sur l'ancienne version. **Ne déployez pas.** |
| **≥ 1** | ✅ c'est la V3 |

---

## LA PROCÉDURE, EN TROIS COMMANDES

```bash
# 1. se placer sur la branche qui porte la V3
git fetch origin && git checkout claude/github-repo-context-nisd2r && git pull

# 2. construire, contrôler, préparer  (il s'arrête au premier problème)
cd clients/10-hillary-m-styl && python3 _predeploy.py

# 3. publier  (la commande exacte est réaffichée par l'étape 2)
npx -y wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main
```

Identifiants Cloudflare : `secrets/cloudflare.env` (gitignoré, présent en local seulement).

---

## CE QUE FAIT `_predeploy.py`, ET POURQUOI

Le site est **déjà en ligne et utilisé**. Un déploiement raté ne casse pas un brouillon :
il casse la vitrine d'une cliente. Le script s'arrête donc au premier problème.

| # | Vérification | Ce qu'elle évite |
|---|---|---|
| 1 | La source contient bien `Bodoni Moda`, `croquis`, `data-tap` | Déployer l'ancienne version sans s'en rendre compte |
| 2 | `_build.py` réussit | Publier un fichier à moitié construit |
| 3 | `_qc.py` — **71 contrôles, tous verts** | Publier un débordement, une erreur JS, un bouton inatteignable |
| 4 | Aucun `22900000000`, aucun « à confirmer », aucun « À COMPLÉTER » | Qu'une cliente lise un placeholder sur un site public |
| 5 | `_dist/index.html` préparé | Se tromper de dossier à publier |

**Les trois « à confirmer » tolérés** concernent tous le même cas : le pays « Autre »,
dont les frais d'expédition sont réellement à confirmer au cas par cas. Ce n'est pas un
oubli, c'est une réponse honnête. Ils sont listés en tête du script.

---

## APRÈS LE DÉPLOIEMENT — les trois choses à regarder

Ouvrez **https://hillary-m-styl.pages.dev** sur un téléphone :

1. **Le rideau s'ouvre** au chargement — un fil descend, le monogramme paraît, deux pans
   s'écartent. S'il n'y a pas de rideau, c'est l'ancienne version.
2. **Les titres sont en Bodoni** — un serif fin, à déliés très contrastés. Si les titres
   sont en sans-serif, c'est l'ancienne version.
3. **Appuyez sur une carte du catalogue** — elle s'enfonce, une lueur naît sous le doigt,
   la lumière balaie le tissu.

Et **envoyez une vraie commande de test** jusqu'à WhatsApp, une fois.

---

## ÉTAT DU CONTENU — ce qui est vrai, ce qui est un exemple

| | |
|---|---|
| ✅ **Numéro WhatsApp** | `+229 51 37 47 93` → `wa.me/22951374793`. ⚠️ **à tester une fois** : le dépôt utilise deux formats, si ça n'ouvre pas le bon contact essayer `2290151374793` (§6bis du CONTEXT) |
| ✅ **Retrait** | « Retrait sur rendez-vous · le point de retrait vous est donné sur WhatsApp » — vrai, rien d'inventé |
| ✅ **Délais de confection** | 7 à 14 jours · 1 à 3 en express |
| ⚠️ **LE CATALOGUE** | **12 pièces d'EXEMPLE, avec des prix d'EXEMPLE.** C'est le point le plus important : une cliente peut commander une « Robe Amazone » qui n'existe pas |
| ⚠️ **Frais d'expédition par pays** | Valeurs provisoires. Un tarif faux coûte de l'argent à Hillary **à chaque commande** |
| ⚠️ **Mesures de la robe ovale** | Jamais fournies. 11 mesures proposées, signalées en jaune dans l'interface |
| ⚠️ **Email de repli** | Adresse d'exemple |

**Le catalogue d'exemple est déjà en ligne depuis le 2026-08-01** (déployé par une autre
session). Le redéployer en V3 ne l'aggrave pas — mais **c'est la première chose à obtenir
d'Hillary.**

---

## SI VOUS VOULEZ QUE `main` PORTE LA V3

Rien ne l'empêche techniquement, mais c'est une décision de Mongazi. Le jour venu :

```bash
git checkout main && git pull
git merge claude/github-repo-context-nisd2r      # vérifier les conflits
git diff --stat origin/main..HEAD                # rien d'étranger au chantier ?
git push origin main
```

⚠️ **`main` bouge pendant qu'on travaille** (piège n° 1 du dépôt). Toujours fusionner
`origin/main` dans la branche AVANT de fusionner vers `main`, et vérifier qu'aucun autre
chantier n'apparaît dans le diff.

---

## LES FICHIERS, ET LEQUEL ON MODIFIE

| Fichier | Rôle |
|---|---|
| **`_vitrine_src.html`** | **La source. C'est celui-ci qu'on édite.** |
| `_build.py` | Injecte logo et favicon en base64 → `vitrine.html` |
| `_qc.py` | 71 contrôles, à passer avant tout déploiement |
| `_predeploy.py` | Enchaîne tout et prépare `_dist/` |
| `_apercu.py` | Variante autonome (polices embarquées) pour montrer le site hors ligne |
| `vitrine.html` | **Le livrable, généré. Jamais édité à la main.** |
| `_dist/index.html` | Ce qui part sur Cloudflare. Regénéré à chaque fois |

⚠️ **`_outils/_apply_infos.py` est OBSOLÈTE** : il patchait le livrable directement, ce qui
écraserait la V3. Ne pas le relancer.

---

*NEBULA Agency · Cotonou*
