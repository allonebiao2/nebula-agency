# 2026-10-14 · recherche trading : sa méthode « CDS + EMA 13/50 » (0030), et l'arrêt du scanner BBLOCK

*Le détail vit dans le dépôt privé `nebula-trader` ; ici, seulement le renvoi.*

## L'arrêt du scanner BBLOCK (D-084)

Mongazi, en ouvrant la session : « bblock on stop ça […] on avait déjà conclu que ça ne servait à rien ». Tâche « NEBULA
BBLOCK alertes » supprimée, processus `pythonw` arrêté (il s'était relancé à 03 h 24), contrôlé. Il recevait bien les
signaux. En regardant avant d'arrêter : **17 passages en échec depuis le 12 octobre** (« Object of type bool is not JSON
serializable ») : le signal partait sur Telegram, puis l'écriture du journal plantait, la figure n'était jamais marquée
envoyée (doublons probables) et `signaux.jsonl` est resté vide. Pas de test en avant, donc. Rien n'est corrigé puisque rien
ne tourne. Le sort du test à l'aveugle D-083 et l'enterrement de la 0029 restent à sa décision.

## Sa méthode 0030 « CDS + EMA 13/50 »

**Demande** : « test la méthode du dossier `_partage/CDS & EMA13 et 50` […] en profondeur comme d'hab, mais mets-toi dans la
peau d'un expert en trading et en programmeur avec 50 ans d'expérience ». Sept captures du 13 octobre (NAS100 Capital.com,
S&P 500 Vantage, M5) avec ses règles écrites dessus : tendance EMA 13 / EMA 50, cassures de structure comptées (CDS 1,
CDS 2, « CDS OK »), annulation au contact de l'EMA 13, entrée à la clôture de la cassure, stop au-dessus de la bougie
d'avant, sortie au contact de l'EMA 13.

**La lecture retrouvée sur ses captures** : minutes Deriv de ses jours extraites de MT5 ; ses lignes orange relevées dans les
pixels. Sa vente du 7 octobre (S&P 06 h 40) retrouvée à la bougie près, entrée 7 809,67 contre ses 7 809,74, stop, ventes 2 et
3, sortie des trois à 08 h 35 à 7 796,92 contre ses 7 796,87. ⚠️ Le S&P Deriv colle à Vantage à 0,1-0,3 point ; le NAS100 de
Capital.com est environ 38 points sous Deriv, ses captures NAS100 ne se reproduisent qu'à peu près.

**Ses réponses aux questions à cliquer** : « tester » partout (contact par clôture ou par mèche, CDS 2 ou 3, trois sorties,
quatre seuils de stop), plus ses deux stops et une ou plusieurs positions : 256 cellules par marché (D-086, déclarée avant).

**Verdict D-086 : NE TIENT PAS.** 0 cellule positive sur 256 en 2013-2021 après frais ; sans frais, médiane −0,027 R ; sa
version exacte ne fait pas mieux que des entrées au hasard dans la même tendance ; 26-32 % de gagnants, pire série 16-34,
objectif 1:2 touché 26-31 % au mieux. Page : https://claude.ai/artifact/M75FtcCWnwhCWGZEbKbFE1. Deux ajustements proposés,
non testés : entrer au repli sur l'EMA 13 après deux CDS, ou ouverture de New York seulement.

**Enterrée le jour même.** Mongazi : « hasard donc on l'enterre ». Fiche 23 au cimetière du dépôt privé (commit `248e4ee`),
23 méthodes enterrées. Les deux ajustements ne seront pas testés.

## La méthode 0031 « la double structure » (Benjamin Deleuze)

**Demande** : une vidéo de 54 min (`_partage/La Seule Stratégie de Trading Rentable pour les Débutants…mp4`) : « analyse-la en
profondeur […] comprendre parfaitement et sans erreur la stratégie et la passer en test », puis « test aussi et surtout sa
méthode telle quelle, sans ajout ». Forex, majeures et mineures, M30 à H4 : une tendance de Dow (structure 1), une
consolidation sous une zone psychologique (structure 2), entrée à la clôture franche au-delà de la zone, du bon côté de l'EMA
100, stop sous le dernier creux, objectif au départ de la tendance, ratio 1:2,5 au moins, 8 h-21 h Paris, jamais en mars.

**Lecture** : parole par les sous-titres automatiques YouTube (Whisper arrêté, le PC tombait à 0,3 Go libre), 200 écrans
immobiles en planches, ses trois trades lus sur ses écrans puis retrouvés dans les minutes Deriv : GBP/CAD et NZD/CAD sur la
même bougie, EUR/GBP pris en pullback le même jour ; rejoués avec sa gestion du stop, les trois à l'objectif comme lui.

**Ses réponses aux questions à cliquer** : « tester les trois » partout (unité, gestion, entrée, distance) : 189 réglages,
plus sa méthode telle quelle et sa gestion du risque sur un compte (D-087, déclarée avant).

**Verdict D-087 : NE TIENT PAS.** Sa méthode telle quelle ne tient sur aucune unité ; en M30, −0,119 R par trade en 2022-2025,
20 % de gagnants, pire série 21. Sur un compte (1 %, 2/4/12 %), 33 années négatives sur 48. Aucun des 10 meilleurs réglages ne
tient en confirmation. Elle fait un peu mieux qu'entrer au hasard, pas assez pour payer l'écart et les swaps. Page :
https://claude.ai/artifact/TgUD1cCxxNVnAfWiheADjT. Commit privé `1cff14d`. **Enterrement : à sa décision.**

## Ce qui a coûté du temps

- La lecture recopiait tout l'historique inversé à chaque bougie de baisse (`-l` recalculé dans la boucle) : un temps au
  carré, le calcul ne finissait pas. Corrigé, une année lue en 0,7 s.
- Le premier fichier MT5 du S&P n'avait que le 14 octobre : la première demande déclenche le téléchargement, la seconde rend
  tout. Vérifier le nombre de minutes par jour avant de conclure.

- 0031 : une occasion en attente bloquait la détection des suivantes ; une cassure refusée fermait l'occasion au lieu
  d'attendre la bougie suivante ; dix zones de gestion serrées au lieu de ses deux ou trois (corrigé : la plus fournie
  d'abord, 3 ATR d'écart, 4 impacts). Les swaps d'aujourd'hui surestiment 2019-2021 : une lecture « sans swaps » est donnée à
  côté.

## Où c'est

`nebula-trader` (commit `e307081`) : `_cerveau/methodes/cds-ema-13-50-sources/ANALYSE.md`, D-086 dans `_cerveau/DECISIONS.md`,
`cerveau/methodes_code/0030_cds_ema.py`, `_0030_grille.py`, `_0030_planche.py`, `_0030_page.py`. Contrôles 72 + 224 verts.
