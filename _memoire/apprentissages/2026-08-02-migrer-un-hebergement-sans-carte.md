# 2026-08-02 — Déplacer une application quand on n'a pas de carte bancaire

## Le problème

Railway a fait disparaître l'application du bureau des partenaires et exige désormais une
carte. Le VPS Hostinger de secours **n'appartenait plus** à Mongazi : le certificat de
`72.61.103.56` était au nom de `api-preprod.normly.fr`, l'IP avait été réattribuée.
**Toujours vérifier à qui appartient une machine avant d'y toucher.**

## Ce qui existe vraiment en gratuit sans carte

| | Vérifié le 2026-08-02 |
|---|---|
| **Render** | gratuit, sans carte, 750 h/mois. ⚠️ **pas de disque persistant**, et son Postgres gratuit **expire au bout de 30 jours**. S'endort après 15 min, réveil ~1 min |
| **Supabase** | gratuit, sans carte, usage commercial autorisé, 500 Mo. ⚠️ pause après **7 jours** sans requête, **2 projets actifs** maximum |

**D'où la règle : séparer le calcul des données.** Le code sur Render, la base sur Supabase.
Un fichier SQLite sur Render serait effacé à chaque redémarrage.

Pour rester sous la limite des 2 projets, les tables du nouveau service vont dans le projet
existant, sous un **schéma dédié** (`naff`), posé par `search_path`. Aucune requête n'a
besoin d'être préfixée, et le schéma n'est **pas exposé à l'API REST** : les données ne sont
atteignables par aucune clé publique.

## Porter SQLite vers PostgreSQL sans réécrire les requêtes

219 requêtes réécrites à la main sur une base qui porte des commissions, c'est 219 occasions
de casser quelque chose en silence. À la place, une **couche de traduction** (`dbx.py`) :

| | |
|---|---|
| `?` → `%s` | sûr ici : un seul `%` dans tout le SQL, et il est dans un paramètre |
| `cur.lastrowid` | → `... RETURNING id`, sauf sur les tables sans colonne `id` et sur les `ON CONFLICT` |
| `sqlite3.Row` | → dictionnaire : même accès `row["colonne"]` |

**Sans `DATABASE_URL`, on retombe sur SQLite.** C'est le repli, et surtout le moyen de
prouver l'absence de régression avant de basculer.

**À vérifier avant d'écrire une telle couche** (tout était favorable ici) : pas d'`INSERT OR`,
pas d'`executemany`, pas de fonction de date SQLite, `ON CONFLICT DO UPDATE` déjà en syntaxe
Postgres, et les `sqlite3.Row` seulement en annotations de type.

## Les quatre pièges qui ont coûté du temps

1. **`REAL` en PostgreSQL fait 4 octets** et arrondit un horodatage Unix ; en SQLite il en
   fait 8. Toute date migrée doit passer en **`double precision`**.
2. **`init_db()`/`migrate()` doivent être désactivées sur Postgres** : un `ALTER` qui échoue
   **empoisonne toute la transaction**, donc un `try/except` par colonne fait échouer tous
   les ALTER suivants au lieu d'un seul.
3. **L'auto-déploiement ne marche pas** quand le dépôt est branché par URL publique : GitHub
   ne prévient jamais l'hébergeur. Un `git push` ne déploie rien.
4. **`x-render-routing: no-server`** sur une application pourtant vivante : l'hébergeur
   sondait `/`, qui dépend de la base, et une sonde `HEAD /` recevait **405**.
   → **un point de contrôle ne doit jamais dépendre de la base, et doit répondre en HEAD.**

## Le domaine ne bouge pas

Le relais Cloudflare Pages existant absorbe le changement d'hébergeur : une ligne `ORIGIN`
dans `_worker.js`, un redéploiement, et c'est tout. Aucun DNS touché, le HTTPS continue.

## Ce que cette panne a coûté

**Les données de production.** Elles étaient sur le disque loué, sans sauvegarde. Une base
qui porte des commissions doit être sauvegardée **ailleurs que là où elle tourne**. Avec
Supabase, cette sauvegarde existe d'office.
