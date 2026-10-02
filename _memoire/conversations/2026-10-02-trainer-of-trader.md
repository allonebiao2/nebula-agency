# Recherche trading, 1er et 2 octobre 2026 (renvoi)

Le travail de trading vit dans le dépôt **privé** `allonebiao2/nebula-trader`
(`C:\Users\USER\nebula-trader`). Cette page n'en garde que le fil, sans chiffre ni règle de
méthode : ce dépôt-ci est public.

## Ce qui s'est passé

- **Méthode 0012** (envoyée en captures par Mongazi) : codée, jugée sur plusieurs époques puis
  sur des marchés jamais vus, avec un indicateur ajouté, puis avec des gabarits tirés de ses
  propres modèles. **Elle ne tient pas.**
- **Test à l'aveugle de l'œil de Mongazi** sur des setups tirés au hasard : son tri **ne fait pas
  mieux que le hasard** sur cette série.
- **« Trainer of Trader »** : une page privée claude.ai (le lien est dans le dépôt privé). On y
  trouve :
  - un backtest en accéléré : Mongazi choisit son capital et sa date de départ ;
  - la décision setup par setup, avec une note de certitude et un commentaire ;
  - ses propres stop et objectif ;
  - quatre gestions de compte : capitalisation, risque fixe, lot fixe, prop firm ;
  - un onglet de résultats ;
  - un calculateur de lot pour le réel.
  Les règles du verdict sont écrites avant qu'il trade.
- **La période scellée reste fermée** : Mongazi a refusé de l'ouvrir pour ce test.
- **Bilan : toujours aucune méthode avec un avantage prouvé au 2026-10-02.**

## À savoir sur le PC

- ⚠️ **La démo « NEBULA ORB demo » n'a pas tradé le 1er octobre** : le bouton **Algo Trading** de
  MT5 était éteint. La configuration de MT5 a été corrigée (une sauvegarde est à côté :
  `common.ini.avant-algo`). **À vérifier par Mongazi : ouvrir MT5 et voir le bouton Algo Trading
  au vert.**
- La tâche Windows tourne toujours du lundi au vendredi à 14 h 00 (heure du Bénin) et ouvre MT5.

## Où est le détail

Dans `nebula-trader` :
- `_cerveau/DECISIONS.md`, D-054 à D-058 ;
- la fiche `_cerveau/methodes/0012-cds-h1-retest.md` ;
- la section « L'état » de son `CLAUDE.md`.

Derniers commits : `f29764b` → `9feb3ae`.
