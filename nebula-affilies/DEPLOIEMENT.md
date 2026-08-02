# Bureau des partenaires — remise en ligne (Render + Supabase)

> Écrit le 2026-08-02, après la disparition de l'application sur Railway.
>
> ## ✅ FAIT LE 2026-08-02 — le bureau est en ligne
>
> **https://partenaires.nebula-agency.online** répond, vérifié 15 fois d'affilée sans un
> seul échec. Portail, espace partenaire, page de recrutement et cockpit à 200.
>
> | | |
> |---|---|
> | Service Render | `srv-d9nni7e7bikc73c9oksg` · https://nebula-affilies.onrender.com |
> | Base | Supabase, schéma `naff`, pooler `aws-0-eu-central-1`, port 6543 |
> | Relais | Pages `nebula-partenaires`, origine repointée vers Render |
> | Clé API Render | `secrets/render.env` |
>
> ⚠️ **L'auto-déploiement ne marche PAS.** Le dépôt est branché par son URL publique, sans
> l'application GitHub, donc GitHub ne prévient jamais Render. Un `git push` ne déploie
> rien. Il faut déclencher à la main :
> ```
> curl -X POST https://api.render.com/v1/services/srv-d9nni7e7bikc73c9oksg/deploys >      -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" -d '{}'
> ```
>
> ⚠️ **Piège rencontré, à connaître :** au début, une requête sur huit repartait avec
> `x-render-routing: no-server`, et ces requêtes **n'apparaissaient même pas dans les
> journaux** de l'application. Deux causes fermées : l'hébergeur sondait `/`, qui rend une
> page complète et dépend de la base ; et une sonde `HEAD /` recevait **405 Method Not
> Allowed**, ce qu'un répartiteur lit comme une panne. D'où **`/healthz`**, qui répond en
> GET comme en HEAD et ne touche ni la base ni le disque. Depuis, 15 essais sur 15.
>
> **✅ Toutes les clés sont posées** (2026-08-02) : `ANTHROPIC_API_KEY` (NOVA répond avec les
> bons prix, vérifié), `RESEND_API_KEY` + `EMAIL_*`, `TELEGRAM_BOT_TOKEN`, `NAFF_CRON_KEY`
> (générée). **Miroir complet dans `secrets/nebula-affilies.env`**, pour tout reposer si le
> service Render est un jour recréé.
>
> **Chaîne « devenir partenaire » vérifiée de bout en bout** : formulaire public →
> `POST /api/candidature` → candidature enregistrée dans Supabase en `pending` →
> notification « recrue » générée pour l'admin. Ligne de test supprimée.
>
> **Reste :** **ressaisir les partenaires** (la base est vide, cf. la section sur les données
> perdues) et **changer le mot de passe Supabase**, qui a transité par une conversation.
>
> À suivre dans l'ordre. Chaque étape se vérifie avant de passer à la suivante.

---

## Pourquoi ce montage

Railway a cessé de servir l'application : l'origine elle-même répondait
`404 Application not found`, et le jeton du dépôt était refusé. Sans carte bancaire,
il fallait un hébergement gratuit qui **garde les données**.

| | |
|---|---|
| **Le code** | **Render**, plan gratuit, sans carte. 750 heures par mois. ⚠️ S'endort après 15 minutes sans visite et met environ une minute à se réveiller. Acceptable pour un back-office, pas pour une vitrine. |
| **Les données** | **Supabase**, gratuit, sans carte, usage commercial autorisé. ⚠️ Le disque de Render est **éphémère** : un fichier SQLite y serait effacé à chaque redémarrage. C'est toute la raison de ce découpage. |
| **Le domaine** | Ne bouge pas. Le relais Cloudflare `nebula-partenaires` existe déjà, on change juste vers où il pointe. Aucun DNS à toucher, le HTTPS continue de marcher. |

⚠️ **Supabase met un projet en pause après 7 jours sans aucune requête**, et le plan gratuit
n'autorise que **2 projets actifs**. Boussole en occupe déjà un : les tables du bureau des
partenaires vivent donc dans **le même projet**, sous le schéma `naff`, pour ne pas
consommer le second.

---

## Ce qui a changé dans le code

Rien dans les 219 requêtes. Une couche de traduction a été ajoutée, `dbx.py` :

| | |
|---|---|
| `?` → `%s` | les paramètres, dans les deux dialectes |
| `cur.lastrowid` | devient `... RETURNING id` puis lecture de la valeur |
| `sqlite3.Row` | devient un dictionnaire, même accès `row["colonne"]` |
| schéma `naff` | posé par `search_path`, donc aucune requête n'est préfixée |

**Sans `DATABASE_URL`, l'application retombe exactement sur SQLite comme avant.** C'est le
repli, et c'est aussi ce qui a permis de vérifier qu'il n'y avait pas de régression.

⚠️ **`_outils` du serveur : ne jamais relancer `init_db()`/`migrate()` sur Postgres.** Les
deux sont désactivées quand `DATABASE_URL` est posée, et c'est voulu : en Postgres, un
`ALTER TABLE` qui échoue **empoisonne toute la transaction**, donc le `try/except` du code
d'origine ferait échouer tous les ALTER suivants au lieu d'un seul.

---

## Étape 1 — la base, dans Supabase

1. Ouvrir le projet Supabase existant (celui de Boussole), **SQL Editor**.
2. Coller tout le contenu de **`schema_pg.sql`** et lancer.
3. Vérifier : `Table Editor` → sélecteur de schéma en haut → **`naff`** → 16 tables.

⚠️ Le fichier traduit `REAL` en **`double precision`**, et ce n'est pas un détail de style :
en PostgreSQL, `REAL` ne fait que 4 octets et **arrondit un horodatage Unix**, ce qui
décalerait toutes les dates de plusieurs minutes.

**Récupérer ensuite la chaîne de connexion** : `Project Settings` → `Database` →
**Connection string** → onglet **URI**, et prendre la version **pooler / Transaction**
(port **6543**). Remplacer `[YOUR-PASSWORD]` par le mot de passe de la base.

> Prendre le pooler, pas la connexion directe : la connexion directe de Supabase est en
> IPv6, et Render sort en IPv4.

---

## Étape 2 — le service, sur Render

1. Créer un compte sur **render.com** (email ou GitHub, aucune carte).
2. **New → Web Service** → connecter le dépôt GitHub `allonebiao2/nebula-agency`.
3. Réglages :

| Champ | Valeur |
|---|---|
| Root Directory | `nebula-affilies` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |
| Region | Frankfurt |

4. Dans **Environment**, poser les variables. Aucune ne va dans le dépôt :

```
DATABASE_URL        = <URI pooler Supabase, port 6543>
NAFF_PG_SCHEMA      = naff
NAFF_ADMIN_PATH     = cockpit-d59fa50d
NAFF_ADMIN_PASS     = <le mot de passe admin>
NAFF_PUBLIC_BASE    = https://partenaires.nebula-agency.online
ANTHROPIC_API_KEY   = <pour NOVA>
RESEND_API_KEY      = <pour les emails d'accès>
EMAIL_FROM_ADDRESS  = contact@nebula-agency.online
TELEGRAM_BOT_TOKEN  = <pour les alertes>
NAFF_CRON_KEY       = <chaîne au choix, pour la relance des abonnements>
```

5. Déployer, puis noter l'adresse donnée par Render, du genre
   `https://nebula-affilies.onrender.com`.

**Contrôle :** cette adresse doit répondre `200`, et `/cockpit-d59fa50d` aussi.

---

## Étape 3 — rebrancher le domaine

Le relais Cloudflare pointe encore vers Railway. Une ligne à changer dans
**`_proxy/_worker.js`**, à la racine du dépôt :

```js
const ORIGIN = "https://nebula-affilies.onrender.com";   // était : ...up.railway.app
```

Puis redéployer le relais :

```bash
npx -y wrangler@3 pages deploy _proxy --project-name nebula-partenaires --branch main
```

**Contrôle :** `https://partenaires.nebula-agency.online/` répond `200`.

---

## Étape 4 — remonter le site de l'agence

Le site public appelle encore l'ancienne adresse Railway, à deux endroits de
`00-nebula-agency/nebula_agency_v9.html` :

- `/api/agency-chat` — c'est **NOVA**, le chat du site. Il est cassé depuis la disparition
  de Railway et répond « Désolé, réessayez dans un instant » à chaque message.
- `/api/site-lead` — l'enregistrement des demandes. ⚠️ **Les formulaires ne sont PAS
  cassés** : ils ouvrent WhatsApp avec le message complet, et l'appel à l'API est enveloppé
  dans un `catch` silencieux. Aucun prospect n'a été perdu, seule la copie en base l'a été.

Remplacer les deux par `https://partenaires.nebula-agency.online`, puis redéployer le site
(voir `00-nebula-agency/CONTEXT.md`).

---

## Ce qui a été perdu, et qu'il faut regarder en face

**Les données de production étaient sur le disque Railway.** Il n'en existe aucune
sauvegarde dans le dépôt. La base locale `affilies.db` date du 22 juin et ne contient que
des comptes de test (`DEMO`, `Test`, `Recrue`).

Donc : **les partenaires enregistrés, leurs clients et leurs commissions sont à ressaisir.**
Romaric DJANKAKI (code `RBNXF`, taux spécial 40 %) est le cas connu à recréer en premier.

**La leçon, à ne pas repayer :** une base qui porte des commissions doit être sauvegardée
ailleurs que là où elle tourne. Une fois Supabase en place, cette sauvegarde existe
d'office (Supabase garde des sauvegardes quotidiennes), ce qui n'était pas le cas d'un
fichier SQLite sur un disque loué.

---

## Vérifier après coup

```bash
curl -sL -o /dev/null -w "%{http_code}\n" https://partenaires.nebula-agency.online/
curl -sL -o /dev/null -w "%{http_code}\n" https://partenaires.nebula-agency.online/devenir
curl -sL -o /dev/null -w "%{http_code}\n" https://www.nebula-agency.online/
```

Puis, dans le cockpit, créer un partenaire de test, lui rattacher un client, marquer le
client payé, et vérifier que les commissions apparaissent. C'est le chemin qui touche le
plus de tables d'un coup.

---

*NEBULA Agency · Cotonou*
