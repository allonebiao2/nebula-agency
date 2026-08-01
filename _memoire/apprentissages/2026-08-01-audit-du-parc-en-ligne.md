# 2026-08-01 — Auditer tout le parc en ligne avant de redéployer

## Le problème

« Déploie tout » sur 14 projets Cloudflare Pages, c'est 14 occasions d'envoyer le mauvais
dossier sur un site qui marchait. Chaque projet a sa source à lui : ici la racine du dossier
client, là un `_dist`, ailleurs un proto aplati. Un `deploy` au mauvais endroit casse la prod.

**La bonne réponse : mesurer d'abord, déployer seulement ce qui a bougé.**

## La méthode

```bash
check(){  # $1 = URL publique, $2 = fichier source local
  code=$(curl -sL -o /tmp/x.html -w "%{http_code}" -m 90 "$1")
  a=$(md5sum /tmp/x.html | cut -c1-10); b=$(md5sum "$2" | cut -c1-10)
  [ "$a" = "$b" ] && st="IDENTIQUE" || st="DIFFERENT (live $(wc -c < /tmp/x.html) / local $(wc -c < "$2"))"
  printf "%-58s %s  %s\n" "$1" "$code" "$st"
}
check "https://djambar-team.pages.dev/bijouterie" clients/05-saeir-thiam-bijouterie/bijouterie.html
```

Le md5 voit ce que l'œil ne voit pas : la seule dérive trouvée sur tout le parc était
un `?v=20260715` de cache-bust manquant — **11 octets** sur un fichier de 314 Ko.

## Les trois pièges qui fabriquent de faux « DIFFERENT »

1. **Le 308 de Cloudflare Pages.** Pages redirige `page.html` → `/page`. Sans `curl -L`,
   on télécharge 0 octet et on croit que 12 pages sont cassées. **Toujours `-sL`.**
2. **Le timeout curl.** Un `-m` trop court laisse `/tmp/x.html` vide ou rempli du tour
   précédent. Un « DIFFERENT » isolé au milieu d'« IDENTIQUE » se relance **toujours**
   à la main avec un `-m 90` avant d'être cru.
3. **Le déployé n'est pas toujours la source.** Boussole déploie le proto **aplati**
   (`../assets` → `/assets`). Comparer après normalisation :
   `sed 's#\.\./assets#/assets#g' boussole/_proto/app.html` → diff de 0 ligne.

## Deux règles de déploiement apprises le même jour

**Un déploiement Pages est un instantané complet, pas un ajout.** Ce qui manque sur le
disque disparaît du site. Sur Luxury Club 229, 7 fichiers (affiche A4, carte de visite, QR)
avaient été effacés du disque tout en restant suivis par git : un `deploy .` les effaçait
aussi de la prod. Récupérés par `git checkout -- <dossier>` **avant** de déployer.
→ **Lire `git status` avant tout `pages deploy .`**, et se méfier des ` D ` non stagés.

**Déployer `.` publie aussi les notes internes.** HH Design servait son `CONTEXT.md`
(numéro « à confirmer », historique du pivot). Un `_dist` explicite, construit fichier par
fichier, est la seule façon de savoir ce qui part en ligne. Contrôle après coup : demander
l'URL du fichier interne et vérifier qu'elle ne renvoie plus son contenu.

## Distinguer une panne de relais d'une panne d'origine

`partenaires.nebula-agency.online` renvoyait 404. Réflexe : accuser le relais Cloudflare.
En interrogeant **l'origine en direct** (`nebula-affilies-production.up.railway.app`), même
404 avec le corps `{"status":"error","code":404,"message":"Application not found"}` :
c'est la signature de **Railway**, pas de Cloudflare. Le relais était sain, l'application
n'existait plus. **Toujours tester l'origine avant de toucher au proxy.**
