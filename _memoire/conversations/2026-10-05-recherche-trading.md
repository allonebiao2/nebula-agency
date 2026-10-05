# Recherche trading, 5 et 6 octobre 2026 (renvoi)

Le travail de trading vit dans le dépôt **privé** `allonebiao2/nebula-trader`
(`C:\Users\USER\nebula-trader`). Cette page n'en garde que le fil, sans chiffre ni règle de
méthode : ce dépôt-ci est public.

## Ce qui s'est passé

- **La recherche reprend** après la pause du 2 octobre, sur une source envoyée par Mongazi : une
  vidéo YouTube de Benjamin Deleuze (« 100 stratégies testées, 5 retenues ») et ses indicateurs
  TradingView, rangés dans `_partage/`.
- La vidéo a été **transcrite et lue écran par écran**. Les règles exactes viennent des indicateurs,
  pas de l'oral, qui les contredit par endroits.
- **Méthode 0014** (décisions D-060 à D-063 dans le dépôt privé, toutes figées avant calcul) :
  - notre code **retrouve ses chiffres** sur sa période ;
  - sur les années qu'il n'a pas vues, **aucune des cinq ne tient** au verdict écrit d'avance ;
  - **une seule piste ressort, sur l'or**, juste sous le seuil : c'est le meilleur résultat de toute la
    recherche à ce jour. Les autres unités de temps et les autres marchés ne la confirment pas.
- **L'or entre au périmètre de recherche** (décision de Mongazi).
- **FTMO a été étudié** (règles officielles relevées sur ftmo.com) et la piste simulée sous leurs
  règles. Conseil donné : la démo d'abord, puis un petit challenge, avec un risque modéré.

## À savoir sur le PC

- ⚠️ **Une 2e tâche Windows tourne** : « NEBULA VWAP demo », **chaque heure à la minute 1**, sur compte
  DÉMO. Elle partage le compte MT5 de la démo ORB et referme MT5 seulement si elle l'a ouvert.
  Pour l'arrêter : `schtasks /Delete /TN "NEBULA VWAP demo" /F`.
- Pour faire de la mémoire pendant les calculs, deux onglets Chrome et Discord ont été fermés le 5 octobre.
- Gros fichiers laissés dans `_partage/` **sans les committer** : la vidéo (123 Mo) et son audio.

## Où lire la suite

Dans le dépôt privé : `CLAUDE.md` (l'état), `_cerveau/DECISIONS.md` (D-060 à D-063),
`_cerveau/methodes/benjamin-deleuze-sources/ANALYSE.md`, `_cerveau/DEMO.md`.
