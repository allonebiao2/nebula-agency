# 2026-09-18 · NEBULA Trader : le test d'un an retourne LE REFLUX

## Contexte
Le PC a planté vers 11 h 20 (Windows, erreur d'alimentation 0xA0) juste après la fabrication des PDF
de la méthode LE REFLUX. À la reprise, Mongazi : « fais un test et continue de prendre des notes à
chaque trade », puis « fais le test sur 1 an avec un capital de 10 dollars sur chacun et prends les
notes pour le deep learning », puis « le minimum même avec 0,1 c'est combien ? sinon il faudra
augmenter le risque et adapter le plan ».

## Ce qui a été trouvé avant même le test
- `live/scalpeur.py` n'appelait pas `execution.autorisation` : avec `--reel`, il aurait envoyé des
  ordres sur n'importe quel compte branché, réel compris.
- Il n'écrivait aucun trade dans le journal : le carnet `SUIVI.md` serait resté vide.
- Il jugeait le filtre au moment de poser l'ordre, alors que la recherche le juge à la minute qui
  précède le remplissage.
- Il lisait 6 000 minutes : mesuré, une caractéristique s'écarte alors de 3,7 % (20 000 : 2e-6).
- Le seuil du modèle posé sur le disque est calibré sur l'apprentissage lui-même.
- Le plafond de levier x30 de BOOST interdit le scalping M1 à 6 % (levier médian x29 / x73).

## Le test
`recherche/rejeu.py` + `live/moteur_scalp.py` (moteur partagé avec l'agent), filtres trimestriels
sans regard vers l'avenir, prix Deriv, vrais lots, échelle 6-4-3. Résultats et détail :
`trading/REJEU-1AN.md`. NAS100 −0,103 R (30,8 %), EUR/USD −0,370 R (25,4 %). À 10 $ : 0 trade sous
x30 ; sans plafond, 2 et 10 trades, tous perdants. Variantes causales : toutes négatives.

## La cause
`banc._simuler_ordres` n'est pas causal (ordre de pose, réentrée dans la barre de sortie). Moteur
validé contre lui : `_qc_moteur.py` (208 divergences sur 208 expliquées).

## Décisions / suite
- Avertissement en tête de METHODE-LE-REFLUX, BACKTEST-LONG, PLAN-DE-RISQUE, RECHERCHE-SCALPING ;
  PDF régénérés (plus REJEU-1AN.pdf).
- Ni démo ni réel avant une version causale positive sur une période neuve.
- Suite proposée : filtre réappris sur les trades du moteur causal ; banc rendu causal ; registre rejoué.
- Réponse à la question du capital : minimum ~40 $ (NAS100) et ~6 à 12 $ (EUR/USD) sans plafond de
  levier, ~80 $ et ~39 $ sous x30 ; mais augmenter le risque d'une méthode perdante ne fait que
  vider le compte plus vite.

## Fichiers
`trading/live/moteur_scalp.py` (neuf) · `trading/live/scalpeur.py` (réécrit) · `trading/live/execution.py`
(`ouvrir_niveaux`) · `trading/recherche/rejeu.py`, `rejeu_variantes.py`, `_qc_moteur.py`, `_qc_parite.py`
(neufs) · `trading/recherche/caracteristiques.py` (`construire_aux_barres`) · `trading/REJEU-1AN.md` ·
avertissements dans 4 documents · `trading/outils/pdf_methode.py` · `trading/documents/*.pdf` ·
`trading/JOURNAL.md` · `CLAUDE.md` · `_memoire/lecons.md`.
