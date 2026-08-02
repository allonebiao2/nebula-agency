# 2026-08-02 — AI SEO du site de l'agence : les robots des IA étaient interdits d'entrée

## La découverte qui domine tout le reste

`www.nebula-agency.online` **répondait 403 aux robots des IA**. Mesuré, pas supposé :

| Visiteur | Réponse |
|---|---|
| GPTBot (ChatGPT) | **403** |
| ClaudeBot | **403** |
| PerplexityBot | **403** |
| Navigateur normal | 200 |

Et le `robots.txt` servi n'était pas le nôtre : il portait la mention
« Cloudflare Managed content » et interdisait GPTBot, ClaudeBot, Google-Extended, CCBot,
Bytespider, Amazonbot, Applebot-Extended et meta-externalagent, avec le signal `ai-train=no`.

**Cause :** depuis le 1er juillet 2025, Cloudflare bloque les robots IA **par défaut** sur
tout nouveau domaine. Personne n'avait rien réglé, c'est arrivé tout seul.

État du parc au moment de l'audit :

| Domaine | Robots IA |
|---|---|
| www.nebula-agency.online | 403 au pare-feu **et** interdits dans robots.txt |
| djambarteam.com | 403 au pare-feu |
| luxuryclub229.com | interdits dans robots.txt |
| graindesthetique.com | interdits dans robots.txt |
| les `*.pages.dev` | ouverts |

**Action qui reste à Mongazi**, impossible en ligne de commande (le jeton Cloudflare du
dépôt n'a que les droits Pages, pas les droits zone) : dashboard Cloudflare → chaque
domaine → **Sécurité → Bots** → désactiver « AI Scrapers and Crawlers » et
« Manage robots.txt ».

**Tant que ce n'est pas fait, le `robots.txt` que nous déployons n'est pas servi** :
Cloudflare impose le sien. Vérifié après déploiement, le fichier public reste celui de
Cloudflare (2 699 octets, 2 blocs « Cloudflare Managed »).

## Correction d'une erreur d'audit

J'avais annoncé « une section FAQ existe, mais sans balisage ». **C'était faux** : mes
occurrences de « faq » venaient des images en base64, pas du texte. Il n'y avait aucune
FAQ. Leçon : sur une page qui embarque des base64, **neutraliser les données avant de
compter** (`re.sub(r'data:[^"\')]{200,}', '[DATA]', h)`), sinon tout `grep` ment.

## Ce qui a été livré

### Quatre fichiers, dans `00-nebula-agency/public/`
| Fichier | Rôle |
|---|---|
| `robots.txt` | autorise explicitement GPTBot, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot… et refuse CCBot et Bytespider (entraînement pur, sans retour) |
| `llms.txt` | la fiche d'identité de l'agence pour les IA : offres, prix, faits vérifiables, réalisations |
| `pricing.md` | les tarifs en markdown, lisibles par une machine sans rendu ni JavaScript |
| `sitemap.xml` | 4 URL |

Avant : ces trois adresses renvoyaient **200 avec la page d'accueil**. Un robot qui
demandait le plan du site recevait du HTML, ce qui est pire qu'une absence franche.

### Sur la page d'accueil (`_outils/_ai_seo.py`, idempotent, UTF-8)
1. **`<meta keywords>` retirée** : le bourrage de mots-clés fait **perdre 10 %** de
   visibilité IA (étude GEO, Princeton, KDD 2024).
2. **Descriptions corrigées** : elles vendaient encore les « avatars IA », service retiré
   du site en v9. Remplacées par les prix, qui sont l'actif réel.
3. **JSON-LD refait en `@graph`** : `Organization`+`ProfessionalService`, `OfferCatalog`
   avec les **5 offres et leurs vrais prix**, `WebSite`, `FAQPage`. Avant : un seul nœud
   `ProfessionalService` avec une adresse.
4. **Une vraie section FAQ**, 10 questions, visible pour l'humain et balisée pour la
   machine. Chaque réponse tient debout **sortie de son contexte**, condition pour être
   extraite telle quelle.
5. **Date de mise à jour affichée** dans le pied de page.

Poids : 411 → 423 Ko.

### Une page pensée pour être citée
`prix-site-web-benin.html` → **https://www.nebula-agency.online/prix-site-web-benin**

Réponse directe dès la première phrase, tableau des prix, ce qui coûte après la livraison,
cinq questions à poser avant de comparer deux devis, FAQ, `Article`+`BreadcrumbList`+`FAQPage`.
16 Ko.

**Ancrage vérifié** : le plancher de 55 000 F est rapproché du **SMIG béninois de
52 000 FCFA**, en vigueur depuis le 1er janvier 2023 (revalorisation de 30 % depuis
40 000 F). Vérifié en ligne avant d'écrire, pas cité de mémoire.

## Pourquoi cette page-là

La question « combien coûte un site web au Bénin » est posée aux IA, et **presque personne
ne publie ses prix** sur ce marché. NEBULA les affiche. C'est le seul endroit où l'agence
peut être la meilleure réponse disponible plutôt qu'une réponse parmi d'autres.
Les chiffres sourcés augmentent les citations de 37 à 40 %, et jusqu'à 115 % pour un site
encore peu établi.

## Remarque d'honnêteté, notée telle quelle

À Cotonou, les clients arrivent aujourd'hui par WhatsApp et le bouche-à-oreille, pas par
ChatGPT. Ce chantier prépare l'année qui vient. Mais rester bloqué ne rapporte rien, et le
déblocage tient en quelques clics.

## Note de design

Le hook `impeccable` a signalé une barre bleue à gauche du chapeau : retirée, c'était un
tic visuel inventé pour l'occasion. Inter, Syne et le dégradé du logotype ont été gardés :
ce sont ceux du site de l'agence, en changer aurait donné une page étrangère au reste.


---

## RÉSOLU le 2026-08-02 — où était vraiment l'interrupteur

Le blocage ne se voyait **ni dans les règles WAF ni dans les réglages de zone** : comparés
un à un entre un domaine bloqué et un domaine ouvert, les rulesets étaient identiques et
les 56 réglages de zone identiques aussi. C'est ce qui a fait perdre du temps dans le
dashboard : il n'y a rien à voir à ces deux endroits.

**L'interrupteur vit dans l'API Bot Management**, et il s'appelle `ai_bots_protection` :

```
GET  /zones/{zone}/bot_management     → ai_bots_protection = block
PUT  /zones/{zone}/bot_management     {"ai_bots_protection":"disabled"}
```

Valeurs possibles : `block`, `only_on_ad_pages`, `disabled`. C'est le même objet qui porte
`is_robots_txt_managed`, celui que Mongazi avait déjà désactivé dans le dashboard.

État trouvé sur le parc : `nebula-agency.online` et `djambarteam.com` étaient à **`block`**,
`luxuryclub229.com` à `only_on_ad_pages`, `graindesthetique.com` déjà à `disabled`.
Les deux premiers ont été passés à `disabled` par l'API.

⚠️ **Le jeton doit porter le droit `Zone · Bot Management`.** Avec seulement *Zone Settings*
et *Zone WAF*, l'endpoint répond « Authentication error » : on ne peut même pas **lire** le
réglage, donc on cherche à l'aveugle.

**Vérification finale, les quatre domaines, cinq robots :**

| Domaine | GPTBot | ClaudeBot | Perplexity | OAI-Search | Google-Ext |
|---|:--:|:--:|:--:|:--:|:--:|
| www.nebula-agency.online | 200 | 200 | 200 | 200 | 200 |
| djambarteam.com | 200 | 200 | 200 | 200 | 200 |
| luxuryclub229.com | 200 | 200 | 200 | 200 | 200 |
| graindesthetique.com | 200 | 200 | 200 | 200 | 200 |

Le premier contrôle après l'écriture donnait encore un 403 sur GPTBot : c'était de la
**propagation**, résolu en une poignée de secondes. Ne pas conclure sur une seule mesure.

## Découvert au passage : l'apex du site agence est cassé en HTTPS

`https://nebula-agency.online` (sans `www`) renvoie **525**, pour tout le monde, robots
comme navigateurs. `https://www.nebula-agency.online` répond 200, et `http://` sans `www`
répond 200 aussi. Les trois autres apex du parc (`djambarteam.com`, `luxuryclub229.com`,
`graindesthetique.com`) répondent 200.

### ✅ CORRIGÉ le 2026-08-02

**La cause, une fois le DNS lisible :**

```
nebula-agency.online   A  2.57.91.91   proxifié
```

Ce n'était pas l'ancien site : `2.57.91.91` servait **la page de parking de Hostinger**
(« Parked Domain name on Hostinger DNS system », 33 Ko), reste de l'hébergement d'avant la
migration. Et cet hôte **ne répond pas du tout en HTTPS** (handshake impossible), d'où le 525
puisque le mode SSL de la zone est `full`. Autrement dit : qui tapait l'adresse sans `www`
voyait une erreur en HTTPS, et une page Hostinger en HTTP. Sur le domaine principal de
l'agence.

Pour comparaison, `djambarteam.com` avait déjà le bon montage : apex **et** `www` en CNAME
vers le projet Pages.

**La correction, en deux temps — le premier seul ne suffit pas :**

1. **DNS** : le `A` remplacé par `CNAME nebula-agency.online → nebula-agency.pages.dev`,
   proxifié (aplatissement d'apex assuré par Cloudflare).
   → le 525 devient **522**. Progrès, mais toujours cassé.
2. **Pages** : l'apex n'était **pas déclaré comme domaine du projet** (`/pages/projects/
   nebula-agency/domains` ne contenait que `www.nebula-agency.online`). Un CNAME proxifié
   vers `*.pages.dev` ne suffit pas : Pages doit connaître le nom d'hôte, sinon il ne sait
   pas quel projet servir.
   `POST /accounts/{acc}/pages/projects/nebula-agency/domains {"name":"nebula-agency.online"}`
   → **200 immédiat**.

**Leçon à garder : 525 puis 522 après correction du DNS = le nom d'hôte manque côté Pages.**
Deux réglages, deux endroits, deux jetons différents (Zone·DNS pour l'un, Pages pour l'autre).

Vérifié sur l'apex : page servie identique au `www` (434 Ko, bon titre),
`/prix-site-web-benin`, `/llms.txt`, `/pricing.md`, `/sitemap.xml`, `/robots.txt` tous à 200,
et GPTBot, ClaudeBot, PerplexityBot à 200.

⚠️ **Piège de mesure rencontré** : deux requêtes sur la même URL donnent deux md5 différents.
Ce n'est pas une divergence apex/www, c'est le **script de mesure injecté par Cloudflare**,
avec un jeton unique par requête. Comparer des md5 de pages proxifiées ne prouve rien :
comparer la taille et le titre.
