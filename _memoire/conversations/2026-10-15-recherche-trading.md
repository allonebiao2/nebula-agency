# 2026-10-15 · recherche trading : « l'OPR de 15 h 30 » (0032, OlinVest), enterrée ; sa cousine « au marché » et FTMO

*Le détail vit dans le dépôt privé `nebula-trader` (commit `cff432c`) ; ici, seulement le renvoi.*

## La demande

Une vidéo déposée dans `_partage/` : « Trader l'OPR tous les jours à 15h30 (ridiculement simple et prouvé) » (OlinVest,
20 min 51, YouTube `KImPoa7QTzQ`). Mongazi : « regardes la, lis la et comprends la profondément et totalement […] pas à moitié
mais à 100 pourcent et de passer au test complet ».

## La lecture

- **La parole** : sous-titres automatiques français de YouTube (`yt-dlp`), pas de Whisper (1,5 Go libres sur le PC, et
  l'arrêt brutal du 2026-10-08 pendant une transcription). **Les images** : 488 gardées sur 1 251, toutes regardées.
- **La méthode** : boîte = haut et bas de la bougie 15 min de 9 h 30 New York (15 h 30 Paris) ; une bougie de 5 min clôt
  dehors ; si elle a pris les deux bords, la suivante doit rester dehors ; entrée au RETOUR sur la boîte, stop sous le gap ou
  la base, objectif 1:3, environ 90 minutes.
- **Ses exemples retrouvés à la minute** : EUR/USD 02/04/2026 (objectif 10 h 36), or 16/04 (ordre servi 11 h 09 contre 11 h 08
  chez lui, objectif 12 h 33 comme lui), or 13/04 (la bougie qui prend les deux bords écartée). ⚠️ Pour reproduire l'or du
  16/04 il a fallu **laisser l'ordre posé même quand le prix touche l'objectif avant lui** : le banc du dépôt l'annulait.
- Questions à cliquer : « tester les trois » partout (4 entrées, 3 stops, 3 fenêtres, 2 sorties, 3 filtres, 3 façons de
  compter les trades), objectifs « 3R, variante et 2R », marchés « les siens + 2 juges ». Planches 1 et 2 validées.

## Le verdict (D-090)

- **Sa méthode telle quelle ne tient pas** : −0,053 R sur 4 755 trades en 2022-2025, 28 % de gagnants, sous le sens opposé ;
  en recherche, 16 réglages positifs sur 1 782 contre 644 pour le miroir. **Le retour sur la boîte sélectionne les cassures
  qui échouent** (l'entrée au retour : 15 réglages positifs contre 1 035 pour le miroir).
- **Sa cousine « au marché »** (entrée dès la clôture de 5 min dehors, stop au bord opposé, un trade par jour, sortie 16 h)
  confirme sur 2022-2025 : +0,055 R sur 4 530 trades, t 3,54 contre le miroir, deux moitiés positives. **Mais c'est une
  époque** : négative avant 2022 sur le S&P 500 (chaque année 2013-2020), le Dow et l'EUR/USD ; +0,012 R sur 2014-2025.
- Page : https://claude.ai/artifact/QbCNZrqb9SLsfKpVn4yJf4

## La décision de Mongazi, puis FTMO (D-091)

« enterre et on garde la cousine » : fiche 25 du cimetière, la cousine dans `PISTES.md`, sans démo. Puis : « je veux ton avis
sur la cousine, laisse-moi mes objectifs […] est-ce que ça peut réussir FTMO ? ». 10 000 parcours de 24 mois, 2-Step
100 000 $, cinq marchés : à 0,5 % par trade, 54 % des challenges réussis et +1 749 $ par mois sur l'époque 2022-2025, 33 % et
+689 $ sur 2014-2025 ; avantage retiré, encore +419 $ (la règle de FTMO paie une part). ⛔ Jamais 1 % : le pire jour vaut
−5,5 R sur cinq marchés, au-delà de la perte du jour de 5 %.

## Ce qu'on en garde

- Un ordre limite qui attend le retour sur un niveau cassé est servi quand la cassure échoue.
- Un juge écrit d'avance peut confirmer une époque : relire l'historique entier, année par année, avant d'y croire.

## L'après-midi : « la méthode ADR » (0033, SA méthode, le daily cycle)

- **Ses captures** (`_partage/ADR method/` : 4 exemples, un schéma, 2 captures TDI) : l'Asie (18 h-2 h New York) cassée, la
  bande ADR traversée, le haut (bas) de la veille pris, **le sommet forme deux jambes** (le M / W de Steve Mauro, BTMM),
  imbalance du retournement, entrée au retour, stop au-dessus de l'imbalance, objectif le bas de l'Asie. Avec le **TDI** :
  divergence entre les deux jambes, la ligne verte sort de la bande et rentre en croisant la rouge à la 1re jambe, le
  croisement vert-jaune au moment de l'imbalance.
- **Son indicateur ADR retrouvé** : ouverture de 17 h New York ± ½ ADR(7) et ± ½ ADR(14) (au centième près sur sa capture).
- **Ses exemples retrouvés par le code** (minutes Deriv d'octobre extraites du MT5 démo, en lecture seule, compte démo
  vérifié), dont son trade TDI du GBP/USD 14/10 (ordre 1,31657 contre ses 1,31664). **Planches 1 à 9 validées** (« c'est le
  setup ça »).
- **D-092** (18 144 puis 36 288 réglages par paire, 7 majeures, recherche 2019 → mi-2022, confirmation → sept. 2025, autre
  époque 2012-2018) et **D-093** (le TDI, 3 888 réglages par paire), déclarées avant tout calcul. Contrôles verts après un vrai
  défaut corrigé (le filtre des journées lisait la fin du jour).
- **Calcul** lancé à 17 h 44, détaché, garde-éveil, reprise possible ; D-092 finie à 21 h 51, puis la vague TDI.
- **Ses deux questions du soir**, mesurées sur la recherche et déclarées comme regard : les trades coupés à 16 h 59 New York
  (30 à 43 %) sont en gain à la coupe, mais **gardés la nuit ils rapportent moins** pour chaque objectif (jusqu'au
  lendemain, au jeudi soir, ou sans limite) ; **les deux sens** : ventes −0,065 R, achats −0,273 R. D'où le conseil de ne
  pas lancer la version « nuit » aux règles FTMO (D-094).
- **Verdict de D-092 : rien ne confirme.** Aucun des 36 288 réglages n'est positif en moyenne sur les 7 paires en
  recherche ; 4 cellules (2 réglages distincts) passent le filtre, et retombent à −0,03 et −0,015 R en confirmation. Sa
  méthode telle quelle : −0,064 R sur 2 114 trades (2022-2025), −0,104 R sur 4 907 trades (2012-2018). Le sens opposé gagne
  en recherche (24 523 réglages positifs) mais pas en confirmation.
- **Verdict de D-093 (le TDI) : rien ne confirme.** 36 réglages passent le filtre de la recherche, les 5 finalistes perdent
  en confirmation (−0,065 à −0,031 R) et sur 2012-2018 ; sa méthode TDI : −0,167 R sur 251 trades. La moins mauvaise lecture
  du TDI est la divergence avec le croisement vert-jaune, sans sortir du rouge.
- Page : https://claude.ai/artifact/SRoQci5F8HcCXB9t2BwBj3 (commit privé `1097a1f`). Le calcul ventes/achats sur 2022-2025 a
  été coupé par Claude Code faute de mémoire (Chrome ouvert) : non relancé.
- ⏳ **À sa décision** : le sort de la méthode, la version nuit (D-094), l'envers.

## Ce qu'on en garde (soir)

- Une coupe de fin de journée qui « laisse des trades en gain » ne dit pas qu'il faut les garder : mesurer ce qu'ils
  deviennent. Ici, gardés, ils finissent surtout au stop.
