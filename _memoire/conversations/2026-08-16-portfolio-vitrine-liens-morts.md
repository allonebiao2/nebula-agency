# 2026-08-16 · Le portfolio de la vitrine agence montrait un site mort

Mongazi : « je viens de constater sur la vitrine nebula les liens dans le portfolio ne
sont pas à jour, pourtant j'ai notifié en mémoire que toute nouvelle adaptation de lien
doit se faire aussi au niveau du portfolio ».

Il a raison, et la mémoire lui donnait raison : `feedback_propagation-impact` existait
depuis juin, et son **exemple 2 du 2026-07-13 citait déjà ce client précis** (bascule
Luxury Skin Clinic → `luxuryclub229.com`). La règle était écrite, **la liste des surfaces
ne l'était pas**. C'est ça qui manquait.

---

## Ce qui était en ligne, et faux

| Ce qu'on montrait | État réel |
|---|---|
| `luxuryskinclinic.netlify.app/ina-luxury.html` | **404, site entièrement disparu**, racine comprise |
| `grain-esthetique-cotonou.netlify.app` | vivant mais **périmé** : le client est sur `graindesthetique.com` depuis juillet |
| `speed-weinkeller.pages.dev/weinkeller.html` | 200 mais **redirige** vers `/weinkeller` |
| Hillary, ANGY ART, Au Braisé d'Or, Miss cakes, HH Design | **absents du portfolio**, alors que livrés et en ligne |

Et le pire n'était pas le portfolio : **la page partenaires donnait 11 fois l'adresse
morte** dans des messages prêts à envoyer (« un exemple de ce qu'on fait : … »). Chaque
partenaire qui copiait ce message envoyait un 404 à un prospect.

Détail qui pique : **`llms.txt` était à jour**, lui. Le fichier lu par les IA connaissait
les nouveaux clients ; la page lue par les humains, non.

## Ce qui a été fait

- Portfolio : **4 cartes → 9**, dans l'ordre Hillary · ANGY ART · Djambar · Au Braisé
  d'Or · Miss cakes · HH Design · Weinkeller · Luxury Club 229 · Grain d'Esthétique.
  La carte morte est remplacée par `luxuryclub229.com`, **le même client à sa nouvelle
  adresse** (INA Luxury et Skin Clinic y sont deux des trois univers) : ce n'est pas une
  suppression, c'est une mise à jour.
- Page partenaires : les 11 occurrences remplacées par `hillary-m-styl.pages.dev`.
- `llms.txt` complété avec ANGY ART, **dans `public/` (la source) ET dans `_dist/`**.
- Vignettes recapturées à 1280x820 (le ratio exact de la carte, 880/564), réduites à
  720 px, WebP q62 : 12 à 29 Ko de base64 pièce. Fichier 423 → 497 Ko.
- Déployé sur Cloudflare Pages, puis vérifié **en ligne** : les 9 liens répondent 200
  sans redirection, plus aucune occurrence de `luxuryskinclinic`, 9 vignettes chargées,
  0 erreur JS.

## Ce qu'il faut retenir pour ne pas recommencer

⚠️ **Livrer un site client n'est pas fini tant qu'il n'est pas dans le portfolio.**
La liste des surfaces qui parlent des clients est désormais écrite noir sur blanc dans
`feedback_propagation-impact` :

1. `00-nebula-agency/nebula_agency_v9.html` (le portfolio) + la copie `_dist/index.html`
2. `00-nebula-agency/affiliation/programme-affilies.html` (les scripts de vente)
3. `00-nebula-agency/public/llms.txt` (le fichier lu par les IA) + sa copie `_dist/`
4. Les supports imprimés du client (`assets/docs/` : affiche, carte, QR)

⚠️ **`_dist/` n'est pas généré par un script, c'est une copie à la main.** Une source
modifiée et non recopiée ne part jamais en ligne. Et l'inverse est vrai : j'ai d'abord
corrigé `_dist/llms.txt` seul, ce qui aurait été perdu à la prochaine copie depuis
`public/`.

⚠️ **Une vignette en base64 n'est pas différée par `loading="lazy"`** : elle est dans le
HTML, donc payée au premier chargement, même si le visiteur ne descend jamais jusqu'au
portfolio. Le remède, le jour où le poids gênera, est de sortir les vignettes en fichiers
`.webp` dans `assets/`.

## Restes constatés, pas traités

- **Débordement horizontal de 6 px à 390 px** sur la vitrine : mesuré aussi sur la version
  d'avant, donc antérieur à cette correction. À corriger.
- **Des tirets cadratins dans les scripts de vente** de la page partenaires, alors que la
  règle de la maison les interdit. Ce sont ses textes commerciaux : à réécrire avec lui.
- `nebula_agency_v8.html` garde les vieux liens : c'est la version de secours, on n'y
  touche pas.
