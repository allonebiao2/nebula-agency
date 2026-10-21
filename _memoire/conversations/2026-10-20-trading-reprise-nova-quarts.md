# 2026-10-20 et 21 · trading : les démos se relèvent seules, NOVA répond toujours, LE TRIO, la 0034 jugée, la méthode des quarts (0036)

*Le détail vit dans le dépôt privé `nebula-trader` (D-096 à D-100, leçon 15) ; ici, le récit et les renvois.*

## Le point de départ

Le PC s'était éteint le 17/10 pendant le calcul de la 0034, et la limite hebdomadaire de Claude était atteinte. Mongazi
valide les planches des deux méthodes QQE (0034 « QQE MOD scalping », 0035 « SuperTrend + QQE pullback ») et demande,
avant le test : que la démo et NOVA « fonctionnent quoi qu'il arrive, même sans toi, dès que le PC est allumé et connecté ».

## NOVA ne recevait plus rien depuis le 14/10

- NOVA (trading) et le robot du Bureau des partenaires sont le **même** robot Telegram (@Nova_de_nebula_bot). Les annonces
  partaient du PC (ça marchait) ; les messages de Mongazi passaient par le webhook du Bureau sur Render, qui avait **perdu
  `NAFF_TG_SECRET`** et répondait 403 à tout (sans doute un remplacement global des variables le 14/10).
- Réparé : le webhook arrive désormais sur **NOVA (Cloudflare, `nebula-carnet.pages.dev/api/nova`)**, qui remet le reste
  au Bureau ; secret reposé sur Render (une seule clé, jamais le PUT global) ; replis Claude (modèle de secours, puis
  réponse sans IA lue dans le journal) ; **garde GitHub toutes les 15 min** (`garde-nova.yml`) qui repose la porte
  (essayé en la détournant exprès). Les deux messages en attente ont été livrés et NOVA y a répondu.
- NOVA voit maintenant **les positions ouvertes de MT5** (déposées chaque heure) : elle avait dit « aucune position »
  devant une vente ORB à +5 R.

## Les démos se relèvent seules

- La vente ORB du 16/10 était restée ouverte quatre jours (la règle la soldait à **+7,89 R** à 15 h 59) ; soldée le 20/10
  à **+4,81 R** (+387 $), après un refus de MT5 : **un commentaire d'ordre avec des parenthèses** (« Invalid comment »).
  Filtre durci (lettres, chiffres, espace, tiret, point, 25 caractères) et contrôlé sur tous les motifs.
- Tâche **« NEBULA reprise »** (ouverture de session + toutes les 30 min) : attend internet, relance MT5, solde les
  positions oubliées, suit celle du jour jusqu'à sa règle. Tâches rattrapées (`StartWhenAvailable`), connexion MT5 qui
  insiste et relance le terminal (démo seulement), carnet qui attend internet. QC de l'agent **243 verts**.
- Coupure de courant le 20/10 au soir : le PC a tenu sur batterie (14 %), la box est tombée ; la reprise a attendu
  internet et tout resynchronisé à 18 h 32. Rien de cassé.
- ⚠️ Mes outils (Bash, PowerShell) ne joignent pas MT5 : passer par une tâche planifiée (`NEBULA sonde`).

## LE TRIO (D-099) et ses chiffres

- Mongazi nomme les trois pistes en démo (VWAP or + LE PIÈGE + ORB 5 min, 0,75 % chacune) : **LE TRIO**.
- Rejoué 2013-2025, frais Deriv : 4 141 trades, **26,9 % de gagnants à 1:3,26** (seuil 23,5 %, marge +3,5 points),
  +0,15 R par trade, +4,1 R par mois, 12 années positives sur 13, pire baisse −57 R, pire série 29 pertes.
- FTMO : 10 000 $ à 0,75 % ≈ **+192 $ par mois** (1er challenge réussi 54 %, médiane 2,1 mois) ; 100 000 $ ≈ +1 970 $.
  Une part vient de la règle de FTMO (+54 $ sur 10 000 $ sans avantage). Compte personnel : 100 $ impossible (lots
  minimaux), 1 000 $ sans l'or, 10 000 $ ≈ +305 $ par mois mais −43 % au pire. Avis : démo, puis essai gratuit, puis 10 k.
- Trois planches, un gagnant médian 2024-2025 par stratégie (`trading/rapports/recherche/trio/planches/`).
- ⚠️ L'ORB est la pièce fragile (77 % des trades, marge +2,5 points ; une réplication publique le trouve nul après frais).

## La recherche de méthodes (session et liquidité)

Une méthode publiée perd en moyenne 58 % de son rendement après publication (McLean et Pontiff). Écartées : dernière
demi-heure, dérive de nuit (disparue depuis 2021), dérive avant la Fed (disparue après 2015), VWAP « Holy Grail » (mort à
un centime de glissement). Retenues : **le reflux de la nuit** (Della Corte et Kosowski), **la zone de bruit sur le
Nasdaq** (morte sur le S&P 500 après publication), **les fixings du dollar** (les frais mangent la fenêtre courte),
**les chasses aux nombres ronds** (Osler) : cette dernière a donné la 0036.

## La 0034 jugée (D-096) : ne tient pas

Aucun des 864 réglages positif en recherche ; les 10 meilleurs de −0,019 à −0,022 R en confirmation, t ≤ 1,36 contre
le hasard ; FTMO non viable. ⚠️ **Le juge commun s'est figé** : il chargeait 10,7 Go sur un PC de 8 Go ; il lit
désormais un marché à la fois. La 0035 était en calcul au moment d'écrire. Les critères sont désormais **rentable et
viable + conditions FTMO + comparaison au top 1 du classement FTMO** (+30 %, lu le 20/10) : D-098.

## La 0036 : breakout & retest des quarts (D-100)

- Sa méthode (texte + `_partage/Quater theory brekout&retest/ex 1.png`) : cassure d'un quart (25 pips), retest,
  confirmation, stop au quart d'avant, objectif au quart suivant. **Son exemple USD/CAD du 19/10 retrouvé** (vente 1.4100
  à 04 h 05 New York, objectif à 07 h 27), grâce à une marge d'1 pip (écart FXCM / Deriv).
- Ses demandes, toutes dans la grille : cassure 2/5/10 pips et corps ; avec ou sans retest, ordre limite (sur le quart,
  poussé de 2 ou 5 pips) ; **l'entrée recule de la commission** pour que le stop fasse exactement −1 R et l'objectif +1 R
  (sa version : confirmation puis limite ajustée) ; stop entier ou à 0,5 ; 1:1, 1:1,5, 1:2 ; durée de l'ordre 30 min, 2 h,
  coupure ; annonces avec ou sans filtre ; niveaux 25, 50 ou adaptés ; séances ; M5 et M15 ; break-even ; vendredi ou
  week-end ; et au niveau du compte FTMO : 1, 3 ou illimité positions, 2, 4 ou illimité trades par jour.
- **58 752 réglages par paire**, moteur en deux étages compilé (≈ 13 min par paire), juge qui lit une paire à la fois,
  « la crème de la crème » choisie sur la recherche puis jugée une seule fois. Lancement automatique après la 0035.
- ⚠️ La fermeture forcée de chaque soir à 16 h 55 (héritée du banc commun) est retirée : pas dans sa méthode.

## Ce qui attend Mongazi

- Le verdict de la 0035, puis celui de la 0036 (l'après-midi du 21/10), avec les familles, la combinaison qui tient le
  mieux et sa fiche.
- Enterrer ou non la 0034 (sa décision).
- Vérifier une fois le bouton Algo Trading ; verrouiller le PC (Windows + L) plutôt que se déconnecter ; activer
  l'ouverture de session automatique si un mot de passe est demandé au démarrage.

## Leçons

- **Tout en français, messages ET descriptions d'actions** : je suis reparti en anglais plusieurs fois dans la nuit ;
  Mongazi l'a signalé trois fois (mémoire `feedback_tout-en-francais`).
- Une démo doit se relever seule (leçon 15 du cerveau) ; un commentaire MT5 sans accent peut encore être refusé ; un juge
  qui charge tout en mémoire se fige sans erreur ; un réglage de banc (la fermeture du soir) n'est pas une règle de méthode.
