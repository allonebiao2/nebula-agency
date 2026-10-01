# Recherche trading, 30 septembre et 1er octobre 2026 (renvoi)

Le travail de trading vit dans le dépôt **privé** `allonebiao2/nebula-trader`
(`C:\Users\USER\nebula-trader`). Cette page n'en garde que le fil, sans chiffre ni règle de
méthode : ce dépôt-ci est public.

## Ce qui s'est passé

- **Méthode 0010** (envoyée en captures par Mongazi) : codée, jugée sur plusieurs époques puis
  sur des marchés jamais vus. **Elle ne tient pas.** Un document de résultats avec graphiques a
  été fait (Claude Docs, plus un PDF pour le portable).
- **Méthode 0011** (suivi de tendance, la version « swing ») : **ne tient pas.**
- **Deux méthodes du cimetière exhumées** et retestées en grand : **aucune ne tient** au verdict
  écrit avant. Une piste reste à l'étude.
- **Une démo de cette piste tourne sur un compte DÉMO Deriv**, sans argent réel, par exception
  décidée par Mongazi.
- **Bilan : aucune méthode n'a d'avantage prouvé au 2026-10-01.** Mongazi va envoyer une
  nouvelle méthode.

## À savoir sur le PC

- ⚠️ **Tâche Windows « NEBULA ORB demo »** : du lundi au vendredi à 14 h 00 (heure du Bénin),
  elle lance le programme de démo, qui **ouvre MT5** (environ 1,7 Go de mémoire) et tourne
  jusqu'à environ 21 h 00. Pour l'arrêter : `schtasks /Delete /TN "NEBULA ORB demo" /F`.
- **Mise en veille désactivée** (30 septembre) : les calculs s'arrêtaient à chaque veille.

## Où est le détail

Dans `nebula-trader` : `_cerveau/DECISIONS.md` (D-049 à D-053), les fiches
`_cerveau/methodes/0010-*.md` et `0011-*.md`, et le cimetière `_cerveau/cimetiere/`.
Derniers commits : `00d4cba` → `22ea7eb`.
