# HILLARY M. STYL — LE DÉPLOIEMENT

> **À lire par Claude Code dans le terminal de Mongazi, avant tout déploiement.**
> Dernière mise à jour : 2026-08-06.

---

## L'ÉTAT, EN UNE PHRASE

**La V3 « LE FIL » est sur `main` et elle est EN LIGNE.** Vérifié le 2026-08-06 :
`vitrine.html` de `main` et la page servie par https://hillary-m-styl.pages.dev sont
**identiques octet pour octet** (181 256 caractères, même empreinte `3d769e1c`).

**Le contrôle en une commande, avant de toucher à quoi que ce soit :**

```bash
grep -c "Bodoni Moda" clients/10-hillary-m-styl/vitrine.html
```

| Résultat | Signification |
|---|---|
| **≥ 1** | ✅ c'est bien la V3 |
| **0** | ⛔ vous êtes sur une vieille version. **Ne déployez pas**, cherchez pourquoi. |

### ⛔ La branche `claude/github-repo-context-nisd2r` est PÉRIMÉE

Elle portait la V3 avant qu'elle n'arrive sur `main`. Depuis, `main` a beaucoup avancé :
**la fusionner supprimerait 30 790 lignes**, dont tout PISTE, `scripts/purger.py` et
`scripts/rapatrier.py`. Ne la fusionnez pas. Ne déployez pas depuis elle.

---

## LA PROCÉDURE, EN TROIS COMMANDES

```bash
# 1. partir de main, à jour
git checkout main && git fetch origin && git merge origin/main

# 2. construire, contrôler, préparer  (il s'arrête au premier problème)
cd clients/10-hillary-m-styl && python3 _predeploy.py

# 3. publier  (la commande exacte est réaffichée par l'étape 2)
npx -y wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main
```

⚠️ **Ne vérifiez pas le site dans les secondes qui suivent** : le bord de Cloudflare peut
servir l'ancienne version un instant, et on croit à un échec. Attendre ~30 s, puis lire
le **corps** du fichier servi, pas seulement le code 200.

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

**Le catalogue d'exemple est en ligne depuis le 2026-08-01.** C'est le point le plus
urgent du dossier : **une cliente peut commander aujourd'hui une « Robe Amazone » qui
n'existe pas.** Obtenir les vraies pièces et les vrais prix passe avant tout le reste.

---

## L'HISTOIRE, POUR QUE PERSONNE NE LA REJOUE

La V3 a été construite sur une branche `claude/…` et est restée trois jours sans arriver
sur `main`, pendant que le site en ligne servait encore la V2. Ce document décrivait alors
un piège réel : « déployer depuis `main` republie l'ancienne version ».

**C'est réglé.** La V3 est sur `main`, en ligne, et la branche d'origine est devenue
dangereuse. Ce qui reste vrai, et qui l'est pour tout le dépôt :

- **`main` bouge pendant qu'on travaille.** Toujours `git fetch origin && git merge
  origin/main` AVANT de fusionner vers `main`.
- **Une branche `claude/…` n'arrive jamais dans `main` toute seule.**
  `python scripts/rapatrier.py` liste ce qui traîne, dit si la fusion passerait, et
  signale ce qui touche du sensible.

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
