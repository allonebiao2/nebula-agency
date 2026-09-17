# 2026-09-17 (soir) · NEBULA Trader : la vidéo « Sniper Entry », apprise puis backtestée

Mongazi dépose dans `_partage/` la vidéo « My Secret 1 Minute Scalping Strategy (Sniper Entry) »
(Mulham Trading, 26 min) : « analyse-la en profondeur, regarde-la, apprends parfaitement la stratégie,
backtest le plus proprement possible, en prenant tout en compte, même les news et les meilleures heures,
avec un capital de 10 000 $ ». En cours de route : « sur 10 000 dollars je veux savoir combien de
bénéfice, les stats, pourcentages ».

Rapport généré : **`trading/RECHERCHE-SNIPER.md`**. Fiche de la méthode : **`trading/recherche/METHODE-SNIPER.md`**.

---

## Verdict : NON

| | EUR/USD 2019-2026 | NAS100 2024-2026 |
|---|---|---|
| Trades | 2 941 | 1 070 |
| Gagnants / objectif 3 R atteint | 23,8 % / 21,1 % | 24,7 % / 22,1 % |
| Espérance (coûts Deriv) | **-0,113 R** | **-0,075 R** |
| Espérance SANS aucun coût | -0,020 R (p 0,74) | +0,015 R (p 0,39) |
| P(5 pertes d'affilée sur 100) | 100 % | 100 % |
| 10 000 $ à 1 %, règles de la vidéo | **273 $** | 4 015 $ |
| 10 000 $ à 1 %, NEBULA PRO | 7 970 $ (arrêt total 2022-05-13) | 9 557 $ |

Chaque année perd sur EUR/USD. Filtre des annonces, meilleures heures (choisies sur 80 %, contrôle sur
20 %), 64 variantes en walk-forward : tout négatif. Registre 124 → 146 tests, **0 survit à Holm**.
Rien intégré à l'agent.

## Comment la méthode a été apprise

- Transcription faster-whisper (`small`), puis **la vidéo regardée** : une image toutes les 5 s en
  planches, pleine résolution sur chaque exemple.
- **L'image a tranché ce que le son ne disait pas** : « 50 minute » = M15 ; EMA 200 entourée ;
  graphique **EUR/USD M15 Tickmill en heure de New York** ; la bougie qui balaie doit être de la couleur
  OPPOSÉE au trade ; rectangle = clôture → mèche.
- **Les 4 exemples retrouvés au dixième de pip dans les bougies Deriv** (serveur en UTC) : le 31/10/2025
  01:15 UTC, plus haut 1,15775, clôture 1,15766, exactement. Le graphique était en heure de New York
  (heure d'été cette semaine-là), pas en « UTC-5 » comme l'affichait l'horloge.

## Fidélité, et le seul réglage choisi sur les exemples

- Pivots de structure M15 de 5 bougies : **aucun** exemple détecté (un repli inverse la tendance). À 12
  (≈ pivots H1 de 3) : exemples 1, 2, 3 détectés à la minute, et gagnants comme à l'écran. Choisi AVANT
  tout résultat.
- Exemple 4 non détecté : clôture Deriv 0,3 pip au-dessus des sommets égaux. Règle gardée telle quelle.
- La même semaine, les mêmes règles ont pris 17 trades ; hors des 3 montrés, 11 perdants sur 14.

## Défauts et pièges trouvés en chemin

- ⛔ **Le jeu Hugging Face « Forex Factory 2007-2025 »** annonce ses heures avec un décalage (+03:30)
  mais **40 à 50 % des annonces fortes USD/EUR sont à 00:00** : le NFP 2019-2025 y est à minuit.
  Remplacé par les pages hebdomadaires Forex Factory (horodatage Unix) : NFP et IPC à 08:30 NY dans
  100 % des cas, FOMC à 14:00 (deux exceptions : réunions d'urgence de mars 2020).
- ⛔ **Deriv ne sert aucun tick passé** (0 tick pour la veille comme pour 2019) : ni contre-vérification
  sur ticks, ni profil de spread mesuré sur 28 jours. Profil par minute tiré du champ `spread` des bougies
  2025-2026, recalé sur la médiane des ticks du jour.
- ⚠️ **Premier profil en UTC : faux l'hiver.** Le rollover est à 17:00 New York (21:00 UTC l'été, 22:00
  l'hiver) : profil refait en heure de New York (jusqu'à 100 points à 17:01).
- ⚠️ **Contrôle « données coupées à la minute d'entrée » rouge sur le code SAIN** : un trade n'est
  enregistré qu'à sa sortie, et la position ouverte sur la dernière bougie ne sortait jamais. Corrigé
  (6 minutes plates ajoutées).
- ⚠️ **Mutation équivalente** : un pivot « confirmé » avec la bougie suivante ne peut jamais être balayé
  par elle, donc le résultat ne change pas et aucun contrôle ne rougit. Les vraies fautes (stop au bid,
  EMA lue 4 bougies dans le futur, déclenchement sur la minute suivante) font toutes rougir.
- ⚠️ Heredoc Python sous Git Bash : les accents des chaînes à remplacer sont abîmés, le remplacement ne
  trouve rien. Écrire le script avec l'outil Write (déjà noté en mémoire, redécouvert).

## Fichiers

`trading/recherche/` : `sniper.py`, `annonces.py`, `spread_horaire.py`, `compte.py`, `sniper_lancer.py`,
`sniper_rapport.py`, `sniper_planches.py`, `_qc_sniper.py` (20 contrôles), `METHODE-SNIPER.md` ·
`banc.py` (dispatch `simuler_banc`, motif « avant annonce ») · `_qc_banc.py` · `rapport.py` ·
`trading/RECHERCHE-SNIPER.md` · `trading/RECHERCHE-STRATEGIES.md` · `trading/JOURNAL.md` · `CLAUDE.md` ·
`_memoire/lecons.md` · `_memoire/decisions.md`. Données (ignorées) : `trading/donnees/annonces/ff/`
(402 semaines), `trading/donnees/*_spread_minute.json`, `trading/rapports/recherche/sniper/`.
