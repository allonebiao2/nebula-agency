# 2026-09-16 · `CLAUDE.md` allégé : de 151 181 à 85 017 caractères

Mongazi montre une capture de Claude Code : « ⚠ CLAUDE.md is over the 150.0k-char
limit (151.3k chars) · /memory to free up context ». Il demande ce que ça veut dire,
puis : « vas-y, mais assure-toi que ça reste cohérent et sans bug, dorénavant ce genre
de problème doit pouvoir être traité directement, mets en mémoire ».

---

## Ce que voulait dire l'avertissement

`CLAUDE.md` est chargé **en entier** au début de chaque session. Au-delà de 150 000
caractères, chaque session démarre avec environ 40 000 tokens de moins pour travailler.
Rien n'était cassé.

## D'où venait le poids (mesuré)

| Bloc | Caractères |
|---|---|
| ligne client 11 · Angy Art | 28 909 |
| ligne client 10 · Hillary | 27 287 |
| ligne client 09 · Au Braisé d'Or | 17 623 |
| **le tableau « Clients actifs » entier** | **88 428** |

Chaque vague de travail ajoutait son récit **au bout de la ligne** du client, au lieu de
la réécrire. Trois lignes faisaient la moitié du fichier.

## Ce qui a été fait

1. **Les trois lignes recopiées intégralement** à la fin de leur `CONTEXT.md`, section
   « 📌 Résumé transféré de `CLAUDE.md` (2026-09-16) », découpées en puces aux `·`
   d'origine sans casser un gras, un code, une parenthèse ou des guillemets (81, 156 et
   138 puces). Un renvoi en tête de chaque `CONTEXT.md` pointe vers la section.
2. **Vérifié sans passer par le script** : en repartant de `CLAUDE.md` tel qu'il est dans
   git, **les 414 morceaux** des trois lignes se retrouvent tous dans les `CONTEXT.md`,
   métier et numéro WhatsApp compris. Les diffs des `CONTEXT.md` ne sont que des ajouts,
   sauf la ligne « En ligne » d'Angy Art.
3. **Trois résumés neufs** dans le tableau (1 861, 2 205 et 2 128 caractères) : adresse,
   état, commande pour publier, pièges qui cassent quelque chose, ce qui attend, renvoi
   au `CONTEXT.md`. Structure du tableau vérifiée : 11 lignes, 5 cellules chacune, gras
   et code équilibrés.
4. **La règle écrite dans `CLAUDE.md`** (section « RÈGLE AUTOMATIQUE — MÉMOIRE ET
   DISPATCH ») : une ligne est un résumé, on la réécrit au lieu de l'allonger, et au-delà
   de 140 000 caractères **on allège sans demander**.
5. **`scripts/poids_claude_md.py`** : le total, le seuil, les blocs les plus lourds, et
   un drapeau sur toute ligne client de plus de 3 000 caractères. Sortie 1 au-dessus de
   140 000.

## ⛔ Ce que la relecture a trouvé

- **La ligne d'Angy Art était EN RETARD sur le dépôt.** Elle se terminait par « reste :
  fusionner, déployer, purger » pour la musique, alors que les commits du 2026-09-10
  (`a7b9afb` à `caa0748`) l'avaient mise en ligne, **remplacé le lofi par WETHU**
  (*Culture Capital*), créé `_publier.py` (publication en une commande) et porté le QC à
  **244**. Le résumé dit l'état réel, et une note datée l'explique dans le `CONTEXT.md`.
  L'en-tête du `CONTEXT.md` annonçait encore `angy-art.pages.dev` : passé à
  `angyart.online`.
- **Hillary** : la typographie du tableau disait « Archivo + Manrope », or la V3 a ajouté
  **Bodoni Moda**. Corrigé.
- ⚠️ **Deux fois le même défaut, de ma main** : pour écrire « 17 623 » j'ai appliqué
  `.replace(",", " ")` **à toute la phrase**, qui a perdu ses propres virgules (dans les
  trois `CONTEXT.md`, puis dans les titres affichés par le nouveau script). Vu à la
  relecture, corrigé : on formate **le nombre**, jamais la phrase.

## Ce qui reste lourd (mesuré après)

LE PLI 11 927 · Force de vente 7 920 · MON BÉNIN 6 712 · **ligne 04 Luxury Club 229
6 284** et **ligne 07 Speed/Weinkeller 4 129** (au-dessus des 3 000 de la règle) ·
NEBULA Trader 6 212. Rien d'urgent : 55 000 caractères de marge avant l'alerte.

## Fichiers touchés

`CLAUDE.md` · `clients/09-au-braise-dor/CONTEXT.md` · `clients/10-hillary-m-styl/CONTEXT.md` ·
`clients/11-angy-art/CONTEXT.md` · `scripts/poids_claude_md.py` (neuf) ·
`_memoire/conversations/2026-09-16-claude-md-allege.md` · `_memoire/journal/2026-09-16-journal.md` ·
`_memoire/lecons.md`
