# 2026-09-17 · NEBULA Trader : recherche de stratégies et analyse de deux vidéos de scalping

Mongazi demande de chercher en ligne les 5 meilleures stratégies de scalping et d'intraday « à
plus de 80 % de réussite », de les backtester sur toutes nos données, puis de retenir 2 stratégies
PRO et 2 BOOST, avec tableaux et conseils. Ses réponses en cours de route : **R:R d'au moins 1:2,
en BOOST aussi** ; **rapport ET intégration** ; **EUR/USD et NAS100 uniquement** ; puis deux
vidéos de trader à analyser en profondeur et à backtester ; et un objectif : **le million de dollars**.
Il a aussi autorisé la prise de contrôle du PC.

Rapport complet, généré depuis les résultats : **`trading/RECHERCHE-STRATEGIES.md`**.

---

## Verdict : NON, pas avec nos données

**50 tests, 0 survit à la correction de Holm.** Aucune stratégie retenue pour PRO ni BOOST,
**rien d'intégré dans l'agent** (règle du plan : on n'intègre rien de perdant).

- **5 stratégies publiées** (RSI(2) de Connors, Bollinger + RSI(7), IBS, EMA 200 + Stochastique,
  range de séance) : la meilleure est le **range asiatique EUR/USD M15**, +0,087 R sur 358 trades,
  p = 0,15. Plusieurs font moins bien que le **témoin qui entre au hasard**.
- **Aucun 80 %.** Les « 80 % » en ligne sont payants, invérifiables, ou obtenus avec un objectif
  plus petit que le stop. À 1:2 le point mort est à 33 %.

## Les deux vidéos (fichiers dans `_partage/`, NON versionnés)

Transcrites en local avec `faster-whisper` (installé pour l'occasion, modèle `small`), la vidéo
découpée en planches d'images toutes les 10 s. Transcriptions dans
`trading/rapports/recherche/videos/` (ignoré par git : contenu d'auteur).

**MambaFx, « The Only 1-Minute Scalping Strategy »** (US30) : zone de support ou de résistance en
M5 (4 touches), cassure de structure en M1 (plus haut plus haut, plus bas plus haut, cassure),
stop serré, 1:3 à 1:5, 30 min par jour. Annonce 75 à 80 % « avec trois confirmations » sans aucune
statistique, et vend un abonnement à 39,99 $ et une prop firm dans la même vidéo.
→ **version auteur positive sur tous ses échantillons EUR/USD** (M1 +0,35 R, M5 +0,30 R, M15 +0,66 R)
**mais sur 14 à 28 trades** ; le 83 % sur NAS100 M1 porte sur 6 trades (IC 44-97 %).

**Hugo FX, « Meilleure stratégie de scalping M1 2026 »** (DAX, NZD/USD) : CRT H1 (la bougie 2 prend
le bas de la 1 et clôture dedans), nouveau swing low M15 qui n'invalide pas, entrée M1 en
« discount » sous 50 % dans un PD array, stop derrière, cible = autre côté du range.
→ **négative presque partout**, sauf transposée en EUR/USD H1 sur 16 ans (58 trades, +0,127 R,
années bonnes et mauvaises alternées).

Non modélisé, et écrit dans le rapport : passage au point mort, ajouts de positions, lignes de
tendance, FVG et PD arrays (remplacés par un retour sous 50 ou 62 % de l'impulsion).

## Le million

Rendement mensuel à tenir : depuis 10 000 $, **8 % par mois pendant 5 ans** ou 3,9 % pendant 10 ans.
Projection sur la meilleure piste (si elle gardait +0,087 R, non prouvé) : à 1 % de risque,
**0 % de chances** en 10 ans ; à 3 %, 22 % de chances mais **99,9 % de perdre la moitié en chemin**.
Monter le risque ne remplace pas l'avantage.

## ⛔ Bloquant, et c'est à Mongazi

MT5 plafonne à **100 000 bougies par unité de temps** (`MaxBars=100000` dans `common.ini` du
terminal Deriv, dossier `FB9A…`) : **3 mois de M1, 16 mois de M5**. Pour tester les vidéos sur
plusieurs années il faut « Max. barres = Unlimited » et redémarrer MT5. **Le garde de sécurité de
Claude Code a refusé** que je ferme le terminal et modifie sa configuration (application de trading),
malgré l'autorisation orale : c'est un geste de Mongazi, ou une règle de permission à ajouter.

## Défauts trouvés et corrigés en chemin

- ⛔ **`lire_plage` perdait 47 000 barres M5** : une année qui dépasse la limite rend 0 barre →
  on lit aussi les N dernières barres d'un bloc (⚠️ demander EXACTEMENT la limite rend `None`,
  99 000 passe) ; ⚠️ la fusion rangeait les barres dans le désordre (`np.sort(uniques)` trie les
  positions, pas les temps).
- ⛔ **Moteur : 12 nuits de swap par nuit en M5, 4 en M15** (`quand.hour == 0`), inchangé en H1/H4.
- ⛔ **Banc : un trade à +8 879 358 R** : stop plus proche que le spread → plancher = stops level du
  courtier et deux allers-retours de coûts. ⚠️ Premier jet de ma correction du moteur : **fichier
  abîmé** (positions de découpe calculées avant un remplacement qui décalait le texte), restauré
  depuis git puis corrigé à l'outil d'édition.
- **R:R 1:2 imposé** en PRO et BOOST : `config.toml`, videur (`ConfigDangereuse` sous 2), bornes de
  l'interface, 3 contrôles.

## Fichiers

`trading/recherche/` (neuf : `banc.py`, `candidates.py`, `videos.py`, `lancer.py`,
`videos_lancer.py`, `million.py`, `rapport.py`, `_qc_banc.py`) · `trading/RECHERCHE-STRATEGIES.md` ·
`trading/strategies/indicateurs.py` · `trading/backtest/moteur.py` · `trading/noyau/{config,reglages,donnees_mt5}.py` ·
`trading/config.toml` · `trading/outils/qc.py` (176 → 190) · `trading/JOURNAL.md` · `CLAUDE.md` ·
`_memoire/lecons.md`
