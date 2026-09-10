# ANGY ART · le site prend son nom de domaine

**2026-09-10** · `angy-art.pages.dev` → **https://angyart.online/**

---

## Ce qui était vrai en arrivant

Mongazi demande où en est la connexion du domaine. Mesuré, pas supposé :

- `angyart.online` **était acheté**, sa zone **active** dans notre compte
  Cloudflare, et ses NS **déjà délégués** (`paul` / `rosemary.ns.cloudflare.com`).
- Et pourtant il servait **la page de parking Hostinger** : un `A` vers
  `2.57.91.91`, proxifié, plus un `CNAME` `www` vers la racine.
- Le projet Pages `angy-art` portait **`domains: ['angy-art.pages.dev']`** :
  aucun domaine personnalisé.
- `_domaine.py` était écrit et commité depuis la veille (`eb850ee`), et il
  **refusait de s'exécuter**, exactement comme prévu : il ne réécrit rien tant
  que le domaine ne sert pas le site, parce qu'un `canonical` mort déréférence
  la page qui marchait.

⚠️ **Le blocage n'était donc ni le registrar ni le DNS, mais les deux moitiés
d'un même branchement** : le nom déclaré dans le projet Pages, et
l'enregistrement DNS qui pointe vers lui. **Poser l'un sans l'autre ne donne
rien** : le nom seul reste en « Verifying » pour toujours, l'enregistrement
seul tombe sur une erreur, parce que Pages ne sert un hôte que s'il le connaît.

## Ce qui a été fait

Mongazi dans le tableau de bord (aucun de nos trois jetons n'a `Zone · DNS`,
vérifié : les trois sont refusés en lecture des enregistrements **et** des
réglages de zone) :

1. projet Pages → *Custom domains* → `angyart.online` et `www.angyart.online`
2. la ligne `A` de la racine passée en `CNAME` vers `angy-art.pages.dev`

Puis d'ici, en une commande : **30 occurrences dans 9 fichiers**, dont les
`@id` du JSON-LD, le pied **imprimé** de l'affiche, et `qr-site.png` refait
**puis décodé**. Carte de visite et affiche réimprimées. `llms.txt` régénéré
depuis la page. **224 contrôles verts.** Déployé.

## Vérifié en ligne, sur le domaine

`canonical`, `og:url` et `og:image` portent la nouvelle adresse · `app.js`,
`app.css`, `llms.txt` et `sitemap.xml` **servis identiques au disque en MD5** ·
un fichier absent rend **404** · les quatre robots (GPTBot, ClaudeBot,
PerplexityBot, Googlebot) reçoivent **200**.

---

## Trois pièges qui n'existaient pas sur `*.pages.dev`

Et la raison est la même pour les trois : **un `*.pages.dev` n'est pas une
zone.** Passer sur son nom de domaine, ce n'est pas changer d'adresse, c'est
passer sous un jeu de réglages qui n'existait pas.

### 1. Le cache de zone servait encore l'ancien HTML

Après un déploiement réussi, la page servie portait toujours l'ancien
`canonical`. `sitemap.xml` et `llms.txt` étaient à jour, `index.html` et
`robots.txt` non : ceux-là, je les avais demandés **avant** le déploiement, en
diagnostiquant. Mes propres requêtes avaient rempli le cache.

`purge_everything` sur la zone a suffi. ⚠️ **Un 200 ne prouvait rien**, c'est
le corps qui le disait. Même famille que la panne PISTE du 2026-08-04.

### 2. Cloudflare préposé son `robots.txt` au nôtre, et il nous contredit

Le fichier servi commence par un bloc **« Cloudflare Managed content »** qui
pose `Content-Signal: ai-train=no` puis **interdit** ClaudeBot, GPTBot,
Google-Extended, CCBot, Bytespider, Amazonbot, Applebot-Extended et
meta-externalagent. Le nôtre suit derrière, qui les accueille nommément.

⛔ **Le fichier se contredit sur les mêmes agents**, et le bloc qui refuse est
le premier. C'est exactement le travail GEO de la veille (2026-09-09) défait
par un réglage de zone, sur un site dont l'enjeu est justement d'être cité.

⚠️ **Le vérifier fait partie de la mise en service d'un domaine**, au même
titre que le blocage des robots d'IA par Cloudflare (déjà connu, et re-mesuré
ici : les quatre passent, **c'est le fichier qui ment, pas la porte**).
À désactiver dans **AI Crawl Control**.

### 3. L'obfuscation d'e-mail réécrit sa page

Le seul écart entre la page servie et le disque : Cloudflare a remplacé
`mailto:angyavocevou@gmail.com` par un lien `/cdn-cgi/l/email-protection` et
injecté un script de décodage. Un humain avec JavaScript ne voit rien ; **sans
JavaScript l'adresse est illisible, donc pour un robot aussi**. Le site a un
contrôle « sans JS » précisément parce que ça compte ici.

⚠️ C'est un arbitrage, pas un défaut : protection contre les moissonneurs
d'adresses contre lisibilité. **À trancher par Mongazi.**

---

## Ce qui reste

- ✅ **`www` réglé** : son `CNAME` visait `angyart.online`, donc le proxy
  tournait en rond (522). Repointé sur `angy-art.pages.dev`, il répond 200 et
  son `canonical` renvoie à la racine. ⚠️ Le champ s'appelle **Content** dans
  l'écran d'édition de Cloudflare, pas « Target ».
- ✅ **AI Crawl Control** : `robots.txt` géré **désactivé**. Le fichier servi
  ne porte plus que le nôtre (14 lignes) et les 4 robots restent en 200.
- ⏳ **L'obfuscation d'e-mail** : la garder ou non.
- ✅ **SPF et DMARC posés le 2026-09-10**, et vérifiés depuis un résolveur
  public : `angyart.online` rend `v=spf1 -all`, `_dmarc.angyart.online` rend
  `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s`, **aucun MX**. Personne
  n'envoie de courrier depuis ce domaine : un SPF vide et un DMARC en refus
  empêchent qu'on écrive « au nom d'Angy Art », et son adresse reste un Gmail.
  ⚠️ Le jour où elle voudrait écrire **depuis** `@angyart.online`, ces deux
  enregistrements feraient rejeter son message : c'est à défaire ce jour-là.
  ⚠️ **Le nom de l'enregistrement n'est pas son contenu** : la chaîne
  `v=DMARC1; …` collée dans le champ **Name** fabrique un sous-domaine qui
  s'appelle comme la politique, et Cloudflare répond « angyart.online has a
  record with content » sans dire que c'est le champ qui est faux. Name =
  `_dmarc` (ou `@` pour le SPF), Content = la politique.
- ✅ **La carte de visite est imprimable**, ce qu'elle n'était pas hier : son
  QR menait à une adresse qu'on abandonnait.
