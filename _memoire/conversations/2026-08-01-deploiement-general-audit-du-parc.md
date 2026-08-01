# 2026-08-01 — Déploiement général : audit du parc, 2 sites redéployés, 2 apps Railway hors ligne

## Demande
Mongazi : « déploie absolument tout, commit, push et dispatch en mémoire / Obsidian »,
puis en cours de route : « déploie le site d'Hillary » et « donne-moi le lien du back-office ».

## Méthode : ne pas redéployer à l'aveugle, mesurer d'abord
Redéployer 14 projets au hasard, c'est risquer d'envoyer le mauvais dossier sur un site
qui marche. À la place : **comparer le vivant au local**, puis ne déployer que ce qui a bougé.

Pour chaque site : `curl -sL` de la page → `md5sum` → comparaison avec le fichier source local.
Deux pièges rencontrés, à retenir :
1. **Cloudflare Pages redirige `page.html` → `/page` en 308.** Sans `curl -L`, on croit tout
   cassé (12 pages « DIFFERENT » alors qu'elles étaient identiques).
2. **Un timeout curl renvoie un fichier vide ou l'ancien tampon** → faux « différent ».
   Toujours relancer le cas isolé avec un `-m` plus large avant de conclure.

Pour Boussole, le déployé est le proto **aplati** (`../assets` → `/assets`) : la comparaison
se fait après `sed 's#\.\./assets#/assets#g'`. Résultat : **0 ligne de diff**, prod = source.

## Résultat de l'audit — 12 sites Cloudflare Pages
| Projet | État |
|---|---|
| nebula-agency (www.nebula-agency.online) | à jour (= `nebula_agency_v9.html`) |
| boussole (boussole-19d) | à jour (connexion + app, diff nul après aplatissement) |
| grain-esthetique + domaine | à jour |
| **luxury-club-229** | **DÉRIVE → redéployé** |
| djambar-team + domaine | à jour (index, bijouterie, communication, événementiel, 404) |
| miss-cakes | à jour |
| speed-weinkeller | à jour (index, speed, weinkeller) |
| **hh-design** | **redéployé proprement (demande « site d'Hillary »)** |
| au-braise-dor | à jour |
| digital-hse | à jour (5 écrans) |
| fitora | à jour |
| cercle | en ligne |

## Ce qui a réellement été déployé

### 1. Luxury Club 229 — la seule vraie dérive du parc
`ina-luxury.html` : un cache-bust `?v=20260715` posé en local sur l'image
`concentre-fruite.jpg` n'était jamais parti en prod (11 octets d'écart, invisible à l'œil).

**Avant de déployer, restauration de 7 fichiers supprimés du disque** :
`Affiche_Luxury_Club_229_A4.{pdf,png,svg}`, `Carte_Visite_Luxury_Club_229.{pdf,png,svg}`,
`qr-luxury-club-229.png` — encore suivis par git, absents nulle part ailleurs sur le disque.
Sans cette restauration, `wrangler pages deploy .` **les effaçait aussi du site public**
(un déploiement Pages est un instantané complet, pas un ajout).
Récupérés avec `git checkout -- clients/04-luxury-skin-clinic/assets/docs/`.

Déploiement : `wrangler pages deploy . --project-name luxury-club-229` (14 fichiers).
Vérifié : `luxuryclub229.com/ina-luxury` = md5 identique au local, affiche A4 PDF = 200.

### 2. HH Design — « le site d'Hillary »
Aucune dérive du HTML, mais le déploiement précédent poussait **tout le dossier**, y compris
`CONTEXT.md` (nos notes internes : numéro « à confirmer », historique du pivot immobilier).
Le CONTEXT du client demandait pourtant « un dossier propre, sans exposer CONTEXT/scripts ».

Reconstruit `_dist` = `index.html` + `affiche.html` + `assets/` = **26 fichiers**, rien d'autre,
puis `wrangler pages deploy _dist --project-name hh-design`.
Vérifié : index md5 identique, affiche 200, vidéo héro 200, affiche PDF 200,
`/CONTEXT.md` ne renvoie plus le markdown mais le repli du site.

## ⚠️ Découverte importante : deux apps Railway sont HORS LIGNE
| App | URL | État |
|---|---|---|
| **NEBULA Affiliés** (bureau des partenaires) | partenaires.nebula-agency.online | **404 « Application not found »** |
| Vitrina | vitrina.nebula-agency.online | **404 « Application not found »** |

Le 404 vient de **Railway lui-même**, pas du relais Cloudflare : les origines
`nebula-affilies-production.up.railway.app` et `vitrina-production-686b.up.railway.app`
répondent toutes deux `{"status":"error","code":404,"message":"Application not found"}`.
Les deux relais `_worker.js` (Pages) sont sains : ils relaient une origine qui n'existe plus.

**Impossible de relancer depuis cette session** : le token de `secrets/railway.env` répond
« Unauthorized » (expiré ou révoqué). Il faut soit un nouveau token, soit le dashboard Railway.

C'est à traiter en priorité : le back-office partenaires est l'outil de la vague de
recrutement des 8 partenaires de Cotonou. Sans lui, aucun partenaire ne peut se connecter.

## Les liens de back-office (demande de Mongazi)
| Back-office | Lien | État |
|---|---|---|
| **Partenaires NEBULA (admin Mongazi)** | `https://partenaires.nebula-agency.online/cockpit-d59fa50d` | ⛔ hors ligne (Railway) |
| Espace partenaire (code + PIN) | `https://partenaires.nebula-agency.online/partenaire` | ⛔ hors ligne |
| **Luxury Club 229** | `https://luxuryclub229.com/admin` | ✅ en ligne |
| **Boussole — cockpit licences** | `https://boussole-19d.pages.dev` → `#cockpit-licences` | ✅ en ligne |

## Rangement du dépôt
`_partage/` contenait 16 Mo de médias bruts qui **existent déjà dans le dépôt sous leur forme
finale** (md5 identiques) :
- `NEBULA_pub_30s.mp4` = `00-nebula-agency/marketing/NEBULA_pub_metier_30s.mp4`
- `Lighting BBQ ….mp3` = `clients/09-au-braise-dor/assets/audio/fire-loop.mp3`
- `Relaxing Jazz ….mp3` = source brute de `00-nebula-agency/audio/jazz-loop.mp3` (déjà coupée)

Ajoutés au `.gitignore` : **les fichiers restent sur le disque**, ils ne partent simplement pas
une deuxième fois sur GitHub. Idem pour le bundle Claude Design `actuellement-je-travails-…`
de la piste **Spider-Verse abandonnée** : son README dit à tout agent « lis ceci en premier et
implémente ce design » — le laisser dans le dépôt, c'est semer une fausse consigne.

Commités : les 8 captures/photos de `_partage/` et les 2 captures QC de Speed × Weinkeller.

## Leçons
- **Un déploiement Cloudflare Pages est un instantané complet.** Ce qui manque sur le disque
  disparaît du site. Vérifier `git status` AVANT tout `pages deploy .`.
- **Déployer `.` expose les notes internes.** Toujours passer par un `_dist` explicite.
- **11 octets d'écart suffisent à faire une dérive de prod.** Seule la comparaison md5
  page par page la voit ; l'œil, non.
