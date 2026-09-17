# 2026-09-17 (nuit) · NEBULA Trader : figures chartistes (ETE, biseaux) avec RSI et EMA 50

Après le verdict « Sniper Entry », Mongazi : « donc la majorité présente des stratégies qui ne tiennent
pas la route » (oui : 146 tests, 0 survit), puis demande le taux de réussite des **biseaux ascendant et
descendant**, de l'**épaule-tête-épaule et de l'inversé**, puis « et si on ajoute le RSI et la moyenne
mobile 50 EMA ? », puis « essayons, backtestons ».

Rapport généré : **`trading/RECHERCHE-FIGURES.md`**. Code : `trading/recherche/figures.py`.

---

## Ce qui a été répondu avant le test (sources vérifiées)

- **Bulkowski** (actions, sortie au meilleur prix, sans stop ni coûts) : biseau ascendant objectif atteint
  32 %, échec 51 %, dernier des 36 figures baissières ; biseau descendant 62 % / 26 % ; ETE 51 % / 19 %,
  9e sur 36 ; ETE inversé 71 % / 11 %, 13e sur 39.
- **Chang et Osler** (Fed de New York, Economic Journal 1999) : l'ETE sur 6 devises 1973-1994 ne gagne que
  sur le yen et le mark, et moins que de simples moyennes mobiles.
- Estimation annoncée : 35 à 45 % de réussite à 1:2 avec un vrai stop ; RSI et EMA 50 ajouteraient 2 à 5
  points et retireraient la moitié des trades.

## Verdict du test : NON

- **192 versions** (4 figures × aucun / divergence RSI / EMA 50 / les deux × stop proche ou loin × H1, H4,
  D1 × EUR/USD, NAS100), objectif 2 R, coûts Deriv. Registre **312 tests, 0 survit à Holm** (il faudrait
  p < 0,00016). **0 version à plus de 50 % sur au moins 100 trades.**
- Gagnants moyens, toutes versions EUR/USD : ETE 39,1 %, ETE inversé 38,4 %, biseau ascendant 35,0 %,
  biseau descendant 30,7 % (l'estimation de 35-45 % se vérifie).
- Meilleure sans filtre : **ETE EUR/USD H4, 89 trades, 42,7 %, +0,175 R, p 0,12** → 10 000 $ = 11 550 $ en
  21 ans (**+0,7 % par an**). ETE D1 à 59 % mais 22 trades, 4 objectifs atteints.
- **RSI** : +0,0 point de réussite, garde 31 % des trades. **EMA 50** : +2,3 points, +0,025 R, garde 59 %.
- NAS100 : quelques dizaines de figures depuis janvier 2024, rien à conclure.

## Pièges et corrections

- ⚠️ **Deux versions identiques comptées comme deux tests** : dans un biseau ascendant le dernier sommet
  EST le plus haut, donc stop « proche » = stop « loin ». Vu sur les planches, corrigé avant tout tableau
  (proche = extrême des 4 dernières bougies).
- ⚠️ **Cassure pendant la confirmation du dernier pivot** : un signal daté de cette bougie utiliserait un
  pivot confirmé après elle. Règle « pas de trade », contrôle dessiné, prouvé rouge si on la retire.
- ⚠️ **Contrôle aveugle à une fuite qui supprime un pivot** : il tirait ses bougies parmi celles où l'état
  change ; une bougie de trop lue à droite d'un pivot fait DISPARAÎTRE un changement, donc rien à tirer.
  Tirage sur toutes les bougies : la fuite injectée est attrapée.
- Planches regardées : certains ETE « de sommet » se forment après une forte baisse ; certains biseaux
  ascendants ont une ligne haute presque plate. Définitions gardées telles quelles (fixées avant).

## Fichiers

`trading/recherche/figures.py`, `figures_lancer.py`, `figures_rapport.py`, `figures_planches.py`,
`_qc_figures.py` (11 contrôles) · `_qc_banc.py` · `rapport.py` (section 2 bis, noms, variantes) ·
`trading/RECHERCHE-FIGURES.md` · `trading/RECHERCHE-STRATEGIES.md` · `trading/JOURNAL.md` · `CLAUDE.md` ·
`_memoire/lecons.md`. Résultats (ignorés) : `trading/rapports/recherche/figures/`.
