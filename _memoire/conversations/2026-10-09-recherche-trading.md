# 2026-10-08/09 · recherche trading : la méthode de Tori Trades (0026 et 0026b)

*Le détail vit dans le dépôt privé `nebula-trader` ; ici, seulement le renvoi.*

## Ce que Mongazi a demandé

Le 2026-10-08 au soir : « je t'ai envoyé dans le dossier partage les vidéos de Tori Trades, c'est la même stratégie, c'est
sa méthode, analyse en profondeur… et on passe à la simulation ». Puis trois autres vidéos dans la nuit, et : « garder en
mémoire… je t'enverrai d'autres vidéos, que tu emmagasines un max d'infos sur sa méthode » ; « appliquer à 100 % ce
qu'elle dit… que tu ne te trompes absolument pas lors des tests ».

## Comment les vidéos ont été lues

Six vidéos (A à F, environ 2 h 15 en tout). Aucune n'a de sous-titres dans le MP4 : les **sous-titres publiés sur YouTube**
ont été récupérés (`youtube-transcript-api`, durées identiques aux fichiers), donc **pas de Whisper** (arrêt brutal du PC
le 2026-10-08). 2 300 images clés regardées, plus la checklist FX Replay de sa méthode. Tout ce qu'elle dit, avec la
source et la minute : **`nebula-trader/_cerveau/methodes/tori-trades-sources/CARNET-METHODE.md`**, un carnet vivant à
enrichir à chaque nouvelle vidéo.

## Sa méthode en bref

Tracer les lignes que le prix n'a jamais traversées, du mensuel à l'unité d'entrée (chaque ligne repart du point B de la
précédente) : c'est exactement **l'enveloppe convexe** des plus bas et des plus hauts. Une clôture casse une ligne
(« ligne d'action ») : on entre dans le sens de la cassure ; le stop va derrière **la ligne opposée** (« ligne de
sécurité »), qui part du point extrême de l'écran, puis monte sur des lignes plus raides quand le prix avance. En 2026
elle trade **le pétrole seul, en 1 h** (avant : 4 h ; or, platine, Dow).

## Les décisions de Mongazi

- Entrées M3, M5, M15 (« intrascalping »), puis toutes les unités (4 h à M3) ; marchés : or, Dow, Nasdaq, S&P 500, puis
  le pétrole et le platine (chez Deriv, Dukascopy refusant les téléchargements) ; toutes les sorties et entrées testées.
- **« Il faut que le prix soit connecté à la trendline 3 fois »** : une touche est un vrai contact (0,05 ATR) ; il l'a
  maintenue même quand le trade d'or de Tori n'en avait que 2 nets dans nos données.
- Sa remarque sur la ligne de sécurité (« le stop serait derrière la ligne verte du bas ») a fait trouver un défaut :
  le stop montait sur un creux formé avant l'entrée. Corrigé. Il a conclu : « tu avais raison » (elle trace bien des
  lignes plus raides quand le prix prend de l'avance).
- « On ne trade que les breakouts » : les trois entrées (clôture, retest, double confirmation) sont des cassures, gardées.

## Les résultats

- **0026 (D-077)**, M3/M5/M15, ligne de sécurité fixe : **ne tient pas** (meilleur +0,08 R, t 0,6). Page :
  https://claude.ai/artifact/9hxiFMGck3xYhZXj2gBw3g
- **0026b (D-078)**, version complète, 360 réglages × 6 marchés : **ne tient pas**. Recherche : 10 réglages positifs sur
  110, **55 pour le miroir** (le trade à l'envers de la cassure) ; confirmation : meilleur +0,12 R (t 1,4) ; sa façon à
  elle (1 h) −0,15 R ; 42-48 % de gagnants, 1:2 touché 6-13 %. Page : https://claude.ai/artifact/15ie9NVnvG3mtJKWxFbeE6
- Son trade d'or du 20/05/2025 est retrouvé à l'heure près (entrée 3 235,75 contre 3 237,3) ; son trade du pétrole de mai
  2026 seulement à peu près (le CFD Deriv n'est pas son contrat).
- Le portage de Deriv sur le pétrole (0,19 à 0,20 $ par baril et par nuit) tue le swing.

## L'envers de ses cassures (D-079)

Mongazi : « tester l'envers de ses cassures ». Les 5 meilleurs miroirs de la recherche, figés avant de regarder, jugés sur la
confirmation : **aucun ne confirme** (−0,26 à +0,24 R, 20 à 30 % de gagnants, t ≤ 0,77). Le scellé EUR/USD 2003-2011 n'a pas
été ouvert (la règle exigeait les deux juges, le verdict était acquis). Ajouté à la page 0026b.

## Ce que le code a appris (dans `nebula-trader`)

Contrôles qui ont arrêté la chaîne et fait corriger avant tout chiffre : un contact compté sur un sommet non confirmé, un
rejeu qui oubliait le portage. Un jour férié américain se traverse comme un week-end. Commit `f45c909`.

## Ce qui reste

Le sort de la méthode (enterrer ou garder) : à la décision de Mongazi ; l'envers est jugé (ne confirme pas). L'audit du banc commun (bid/ask) et les correctifs 0025 non commités restent en attente.
