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

---

# 2026-08-02 (suite) — Le bureau des partenaires remis en ligne : Render + Supabase

**https://partenaires.nebula-agency.online répond de nouveau**, vérifié 15 fois d'affilée
sans un échec. Portail, espace partenaire, page de recrutement, cockpit : tous à 200.

## Le montage retenu, et pourquoi

Railway avait fait disparaître l'application et exige désormais une carte bancaire, que
Mongazi n'a pas. Le VPS Hostinger, envisagé ensuite, **ne lui appartient plus** : le
certificat de `72.61.103.56` est au nom de `api-preprod.normly.fr`, l'IP a été réattribuée.

D'où : **le code sur Render** (gratuit, sans carte) et **les données sur Supabase**
(gratuit, sans carte, sauvegardes quotidiennes). Ce découpage n'est pas un luxe : le disque
de Render est **éphémère**, un fichier SQLite y serait effacé à chaque redémarrage.

Le domaine n'a pas bougé : le relais Cloudflare `nebula-partenaires` existait déjà, seule
son origine a changé. Aucun DNS touché, le HTTPS a continué de marcher.

## Ce qui a coincé, et ce que ça apprend

**1. L'auto-déploiement ne fonctionne pas.** Le dépôt étant branché par URL publique (sans
l'application GitHub), GitHub ne prévient jamais Render : un `git push` ne déploie rien.
Il faut un `POST /v1/services/{id}/deploys`. Cela a d'abord donné l'illusion d'un correctif
qui ne prenait pas.

**2. Une requête sur huit repartait avec `x-render-routing: no-server`** — et ces requêtes
**n'apparaissaient même pas dans les journaux de l'application**. C'est ce détail qui a
donné la réponse : elles n'atteignaient jamais le code, le routage les jetait avant.
Deux causes, toutes deux fermées :
- l'hébergeur sondait `/`, qui rend une page complète et dépend de la base : une lenteur de
  Supabase suffisait à faire croire que l'application était morte ;
- une sonde `HEAD /` recevait **405 Method Not Allowed**, l'application n'acceptant que
  `GET`. Un répartiteur de charge lit un 405 comme une panne.

→ **`/healthz`**, qui répond en GET **comme en HEAD** et ne touche ni la base ni le disque.
Après quoi : 15 essais sur 15. **Un point de contrôle ne doit jamais dépendre de la base :
sinon une base lente fait déclarer l'application morte, et l'hébergeur cesse de lui envoyer
des visiteurs.**

**3. Le tableau de bord Supabase a déplacé les chaînes de connexion** derrière un bouton
« Connect », et Mongazi avait perdu son mot de passe. Contourné en reconstruisant la chaîne
à partir du seul mot de passe (`_trouve_dsn.py`), la région du pooler étant trouvée en les
essayant une par une : **`eu-central-1`**.

## Vérifié pour de vrai, pas seulement « ça répond »

- Base : schéma `naff`, 16 tables sur 16, **aucune colonne en `REAL`** (Postgres arrondirait
  les horodatages), identité automatique sur les 14 tables à `id`.
- Application lancée contre Supabase **en local d'abord**, puis un vrai
  `POST /api/site-lead` **depuis Render** : demande enregistrée dans Supabase, notification
  créée, `service_raw` extrait, horodatage exact. C'est le chemin qui passe par
  `cur.lastrowid`. Lignes de test supprimées, base à zéro.
- Site de l'agence : les **3 appels** à l'ancienne adresse Railway rebranchés, plus aucune
  occurrence de « railway » dans la page en ligne. NOVA ne renvoie plus une erreur mais un
  repli poli vers WhatsApp, faute de clé Anthropic.

## Ce qui reste

- Poser `ANTHROPIC_API_KEY` (NOVA), `RESEND_API_KEY` (emails d'accès), `NAFF_CRON_KEY`.
- **Ressaisir les partenaires** : les données de production étaient sur le disque Railway,
  sans sauvegarde. Romaric DJANKAKI (`RBNXF`, taux spécial 40 %) en premier.
- **Changer le mot de passe Supabase** : il a transité par la conversation.
- Render endort l'instance après 15 minutes sans visite, réveil en ~1 minute.

## Romaric DJANKAKI restauré — premier partenaire ressaisi

Traité comme une **restauration, pas une création**. L'API `/api/admin/affiliates` génère
un code et un PIN aléatoires ; or Romaric a déjà `RBNXF` sur sa carte de visite et dans ses
liens de parrainage. Lui donner un nouveau code aurait invalidé tout ce qu'il a déjà diffusé.

Méthode : création par l'API (pour que toute la logique métier s'applique), **puis remise de
son code `RBNXF` et de son PIN `0067`**, ce dernier re-haché avec la même fonction `hash_pw`
que le serveur. Taux spécial **40 %** reposé par l'endpoint prévu pour ça.

Vérifié : il se connecte avec `RBNXF`/`0067`, son espace se charge avec ses statistiques à
zéro, et ses trois liens publics répondent 200.

⚠️ **Piège rencontré** : Cloudflare renvoie **403** à un client d'API sans en-tête de
navigateur. Un `urllib` Python nu ne peut pas se connecter au back-office ; il faut poser un
`User-Agent` de navigateur. À savoir pour tout script qui pilotera l'application.

⚠️ **Son numéro est à confirmer** : posé en `22967218256`, l'ancien format béninois à
8 chiffres. Depuis le 30/11/2024, l'ARCEP impose `+229 01 XX XX XX XX`. **Un numéro Mobile
Money faux, c'est une commission qui n'arrive jamais.**

---

## Boussole passe en « ORANGE & NUIT » — transplantation, pas fusion

**En production : https://boussole-19d.pages.dev** · essai conservé sur
`orange.boussole-19d.pages.dev`

L'identité vivait sur une branche jamais fusionnée (`protocole-boussole-memoire-9xy3j4`).
La fusion a été **tentée puis annulée**, et c'est le bon réflexe : elle butait sur un seul
conflit, mais le conflit disait tout.

```
main       : <script src="../assets/js/proto-app.js">   ← les 238 Ko sortis du fichier
la branche : les 238 Ko réécrits À L'INTÉRIEUR du fichier
```

La branche avait travaillé **avant** l'externalisation. Fusionner aurait remis tout le code
en ligne et **annulé le mode performance adaptatif**, donc la fluidité sur les appareils
modestes. Les deux lignées étaient complémentaires, pas concurrentes :

| main depuis le 25/07 | la branche depuis le 25/07 |
|---|---|
| module externalisé, boot non-bloquant, mode performance adaptatif | Orange & Nuit, visite guidée, aide par écran, pilotage (point mort, trésorerie, score de santé) |

### La méthode : mesurer ce que chacun a touché

- **CSS** : main n'avait changé que **1 412 octets** (le bloc `.perf-lite`), la branche
  **27 860**. → le CSS se transplante en bloc, en recollant `.perf-lite` derrière.
- **JS** : la branche avait remplacé **58 couleurs générées par le JavaScript** par des
  jetons ; le module de main n'en avait aucun. Sans ce second volet, on aurait eu une
  interface orange avec des **graphiques restés en ambre et en cyan**.

Les règles de remplacement n'ont pas été devinées : elles ont été **déduites** en comparant
le JS de la branche à celui d'avant (`difflib` + extraction des couleurs), ce qui a donné
12 règles sûres (`#f6a63c → var(--acc)`, `#34d399 → var(--good)`, `#4cc9ff → var(--acc2)`…).
**82 couleurs** converties dans le module, **0 ancienne couleur restante**.

`boussole/_outils/_orange_nuit.py`, idempotent, fait les deux volets et refuse d'écrire si le
module externalisé ou le mode performance a disparu.

### Deux bugs corrigés au passage

La branche définissait `--bad2: var(--bad2);` (thème sombre) et `--bad: var(--bad);`
(thème clair) : **des jetons qui se référencent eux-mêmes ne produisent rien**. Le rouge des
alertes n'aurait pas fonctionné. Remplacés par `#ff8a96` et `#e11d48`, cohérents avec le
couple `good`/`good2` de chaque thème.

### Découverte : deux fichiers de production n'étaient nulle part dans le dépôt

`sw.js` (**kill-switch** qui désinstalle l'ancien service worker et vide ses caches) et
`_headers` n'existaient **que dans le déploiement**. Un redéploiement les aurait effacés, et
des visiteurs seraient restés coincés sur une version périmée. Récupérés depuis la
production, rangés dans `boussole/_deploy/`, et `boussole/_outils/_build_dist.py` les inclut
désormais. Ce script aplatit le proto (`connexion.html` → `index.html`, `../assets/` →
`/assets/`) et **refuse de publier** si le module externalisé, le mode performance, la
palette ou le thème clair manquent.

### Vérifié

md5 du fichier servi **identique** au fichier local. Palette orange, thème clair, mode
performance, module externalisé : tous présents dans la page réellement servie. Module :
0 ancienne couleur, 64 jetons.

⚠️ Piège de mesure : un premier `curl` avait renvoyé un fichier corrompu et fait croire que
la palette manquait en prod. **Retélécharger avant de conclure** — deuxième fois de la
journée que ce réflexe évite un faux diagnostic.

### Pas repris de la branche

L'**écran de pilotage** (point mort, trésorerie, score de santé, rapport mensuel), la
**visite guidée animée** et l'**aide par écran**. Ce sont des fonctions, pas des couleurs :
un chantier à part, à décider séparément.

---

## Les back-offices : une erreur bloquante, l'accessibilité, la fluidité

Demande de Mongazi : « améliore le rendu, le visuel des back-offices, le mien et celui des
partenaires, corrige toutes les erreurs et rends ça fluide. »

**Méthode : mesurer d'abord.** `nebula-affilies/_outils/_audit_ui.py` se connecte pour de
vrai (cockpit **et** espace partenaire, avec le compte de Romaric), sur 3 formats, et relève
ce que l'œil ne voit pas : erreurs JavaScript, requêtes en échec, débordements mesurés,
cibles sous 44 px, contrastes, animations en boucle sous un flou.

### 1. Une erreur JavaScript qui cassait la moitié du cockpit

```js
text: 'Tous les clients du réseau. … et l'alerte.'
                                        ↑ la chaîne se ferme ici
```

Une **apostrophe française non échappée** dans une chaîne à guillemets simples. Elle cassait
**tout le bloc `<script>` d'`admin.html`**, donc une partie du cockpit ne s'exécutait pas.
Corrigée par une apostrophe **typographique** : le bug disparaît et la typographie est juste.

⚠️ `node --check` sur le **fichier** ne l'attrape pas : il faut vérifier **chaque bloc inline
séparément**. C'est ce qui l'a trouvée.

### 2. Accessibilité, sur mesure

- `--faint` donnait **3,69** de contraste sur les libellés de statistiques, là où il en faut
  4,5. Passé à `#8a8aa6` → **5,68**, en restant plus discret que `--muted` (7,19) : la
  hiérarchie visuelle tient.
- **Cibles tactiles** sous 44 px : boutons ronds (42, et 40 en mobile), croix des
  notifications (34), croix du guide (32), petits boutons (38 de haut). Toutes à 44.
- Champs à **16 px en mobile** : en dessous, Safari iOS zoome tout seul et la page part de
  travers.
- **Focus clavier** rendu visible, il ne l'était pas sur fond sombre.
- `prefers-reduced-motion` respecté.

### 3. Fluidité : isoler avant de trancher

Mesure d'une traite, sur un écran de téléphone, en défilant :

| | images/s |
|---|---|
| tel quel | **35** |
| sans les flous d'arrière-plan | 53 |
| sans les animations infinies | 56 |
| sans les ombres | 35 (**aucun effet**) |
| sans flous NI animations | **60** (le plafond) |

Les **14 flous d'arrière-plan** et les **2 animations d'ambiance** coûtent 25 images sur 60.
Les ombres ne coûtent rien : on n'y a pas touché.

D'où un **mode adaptatif** (`initPerfMode` + `.perf-lite`), le patron déjà éprouvé sur
Boussole : personne n'est dégradé d'office. Sur appareil modeste (≤ 4 cœurs ou ≤ 4 Go), ou
si la fluidité mesurée tombe sous 45, on calme les effets **d'ambiance**. Jamais les
interactions, jamais les transitions au toucher : ce sont elles qui donnent la sensation de
réactivité, et elles ne coûtent rien.

⚠️ **Le gain exact sur les téléphones réels n'est pas certifiable depuis cette machine** : la
référence variait de 14 à 60 images/s selon la charge. Ce qui est solide, c'est l'isolation
des deux coupables, faite d'une traite à charge égale.

### ⚠️ Le piège que j'ai failli payer

Ma **première sonde de contraste était fausse** : elle lisait `rgba(255,255,255,.04)` comme
du blanc au lieu de le **fondre sur le noir**, et signalait 13 « textes pâles » inexistants,
dont des textes en dégradé mesurés à 1,03. J'allais corriger un design qui n'avait rien.

**Corriger la MESURE avant de corriger le design.** La sonde compose désormais les fonds
translucides jusqu'à un fond opaque, et ignore les textes en dégradé, où il n'y a rien à
mesurer.

### Résultat

**9 combinaisons** (3 formats × 3 pages) au vert, **deux passages de suite**, 0 erreur
JavaScript, 0 requête en échec. Vérifié en ligne, connecté : le cockpit ne produit aucune
erreur, `--faint` vaut bien `#8a8aa6`, et le mode calme s'active tout seul sur un appareil
modeste.

---

## Boussole : le PILOTAGE et la VISITE GUIDÉE, portés sans perdre la performance

**En production : https://boussole-19d.pages.dev** · module 232 → **297 Ko**

Ce que ça change pour un commerçant : l'application répondait bien à « combien j'ai fait ? »,
jamais à « **est-ce que je vais tenir ?** ».

| | |
|---|---|
| **Point mort** | charges fixes ÷ taux de marge réel → CA minimum vital, objectif quotidien de survie, et le jour du mois où il a été franchi |
| **Trésorerie** | encaissé réel, **vendu à crédit** (dans le bénéfice mais pas dans la caisse), argent dehors, **autonomie en jours de charges** |
| **Score de santé /100** | rentabilité, trésorerie, crédits, stock, suivi — avec la composante qui pénalise le plus, dite en clair |
| **Rythme** | panier moyen, jours forts, heures de pointe, comparaison de périodes |
| **Mes produits** | classement par **bénéfice réellement apporté**, pas par chiffre d'affaires · règle 20/80 · dormants · rotation |
| **Projection, rapport** | atterrissage fin de mois, récurrent, fiabilité, **rapport mensuel imprimable + WhatsApp** |
| **Visite guidée** | rejouable, aide par écran, et « **⚡ À FAIRE MAINTENANT** » |

### La méthode, et le piège qu'elle a évité

Ces apports avaient été écrits quand tout le JavaScript vivait dans `app.html` ; `main` l'a
depuis externalisé et y a ajouté le mode performance. **Fusionner la branche aurait tout
remis en ligne.**

`boussole/_outils/_porte_pilotage.py` fait donc une **vraie fusion à trois voies, séparément
sur chaque fichier** : style et structure d'un côté, code de l'autre.

Deux gestes ont fait tomber les conflits :
1. **Viser la pointe de la branche** plutôt qu'un commit intermédiaire : sa palette est déjà
   celle transplantée dans `main`, donc `app.html` fusionne **proprement** (52 conflits → 0).
2. **Normaliser les couleurs de l'apport** sur la convention en place avant de fusionner :
   les deux lignées avaient recoloré le même code différemment, ce qui fabriquait des
   conflits qui n'en étaient pas.

Restaient 13 conflits, arbitrés par des **règles nommées**, le script disant ce qu'il a
décidé pour chacun.

⚠️ **La règle qui compte est sémantique** : *si un côté appelle une fonction du pilotage,
c'est le nouveau code.* Ma première règle comptait les lignes, et elle était **fausse** :
un conflit aurait fait **disparaître tout l'affichage du score de santé**, silencieusement,
parce que le nouveau bloc « ressemblait » à une modification plutôt qu'à un ajout. Compter
des lignes ne dit pas ce qu'un morceau de code **fait**.

**Non repris volontairement** : la vague 2 des transitions, qui remplace le tiroir 3D. Autre
chantier, non demandé, et le script le dit explicitement quand il conserve l'existant.

### Vérifié en navigateur

0 erreur JavaScript. « Mes produits » et « Aide » apparaissent dans le menu. Et l'application
annonce d'elle-même, sur les données de démo :

> « TON COMMERCE EST À **50/100** — FRAGILE, MAIS RATTRAPABLE. CE QUI TE PÉNALISE LE PLUS :
> TA CAISSE NE TIENT QUE 0 JOUR DE CHARGES. »

Avec, juste en dessous, « ⚡ À FAIRE MAINTENANT · Réapprovisionne Pain doré — 1 produit est
en rupture : chaque heure sans stock est une vente perdue. » La visite guidée se lance à la
première visite.
