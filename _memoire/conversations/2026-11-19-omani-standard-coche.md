# 2026-11-19 (soir) · Omani : les couches nommées, la pleine définition, la musique au glissé, les lueurs, le panier

## Le déclencheur
Omani (Omani Pâtisserie, prospect chaud) a regardé son aperçu 3D (https://omani-benin.pages.dev) à 18 h 58 : il aime,
mais « il n'y a pas la description de l'intérieur comme l'autre » (son catalogue PDF écrit le nom de chaque couche à
côté d'elle). Réunion avec son équipe de communication le soir même avant de revenir.

## Ce qui a été fait (aperçu hors dépôt : `C:\Users\USER\nebula-apercus\omani\`)
- **Les couches nommées à leur place** : `etiquettes.py` lit dans le PDF chaque étiquette (police Bebas, 24 à 27 pt),
  sa position et son côté ; 21 gâteaux sur 21. Dans la scène, chaque nom suit sa couche : point d'or, trait, pastille.
  Le gâteau reste éclaté plus longtemps pour qu'on lise.
- **Pleine définition** : couches réexportées sans réduction (WebP q90, `OMANI_HD=1 python construire.py`), rendu à
  `min(dpr, 3)` + antialias + anisotropie max, repli automatique si lent ; film d'ouverture en 1080 (5,1 Mo au lieu de 1,5).
- **Musique au premier glissé** : mesuré dans Chromium avec le vrai réglage d'autoplay (glissé CDP) : un glissé laissé au
  navigateur est refusé (`NotAllowedError`) ; pris à la main (`preventDefault` sur `touchstart`, défilement par le code,
  élan au lâcher), son lâcher débloque le son. Safari iPhone pas encore vérifié sur un vrai appareil.
- **Lueurs et profondeur** : faisceau, flaque dorée, bokehs devant et derrière en parallaxe, poussière ronde, flou de
  premier plan, éclat au montage, caméra qui s'avance.
- **Commande multiple** : `panier.js` (quantités, minimum 6 parts, date, prénom, total, un seul message WhatsApp).
  Numéro WhatsApp inchangé.

## La décision de Mongazi
Tout cela est **coché d'office** sur toutes les prochaines réalisations : `_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`
§ 0 ter. Les modules sont dans `nebula-apercus/_socle/`.

## Fichiers touchés
- dépôt : `_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md` (§ 0 ter ajouté), ce journal
- hors dépôt : `nebula-apercus/omani/{etiquettes.py, construire.py, site/app.js, site/index.html, site/son.js,
  site/sequence.js, site/panier.js, site/film/ouverture/*}`, `nebula-apercus/_socle/{son.js, sequence.js, panier.js}`

## Ensuite, ADEMAR (vers 20 h)
- Son offre de 12 h 45 (35 000 F en deux fois) et le vocal de 12 h 47 étaient encore NON LUS à 19 h 46 (coches grises) :
  rien ce soir (service du dîner), relance courte demain 9 h 30-10 h, une seule question facile.
- ⛔ J'avais rédigé « je passe moi-même au restaurant prendre vos plats en photo » : Mongazi ne se déplace pas. Règle
  ajoutée à `prospection/VENDEUR.md` § 6 et à la mémoire : aucune visite promise sans lui en parler.
- Son aperçu reçoit le standard coché d'office (panier de plusieurs plats sans prix, musique au 1er glissé, braises de
  profondeur par-dessus le film du téléphone, film 1080 refait depuis `recadre.mp4`). **Testé, pas publié** : le
  déploiement attend son accord.
- Omani republié avec deux corrections du panier (intitulé de date, boutons d'une fiche cachée rendus inertes).

## La nuit : le son partout, les rappels, ADEMAR v2, la Maison des bijoux v2
- **Le son** : sur iPhone la musique était inaudible (fichier à -20 LUFS joué à 0,26, soit -32 LUFS). Recette d'Angy Art
  reprise (lancée au doigt posé), musiques normalisées à -12 LUFS, volume 0,66, bruitages rangés avec la musique
  (`navigator.audioSession.type = "playback"`). Les 4 aperçus corrigés, et `nebula-apercus/_socle/verifier_son.py`
  arrête désormais toute publication dont le son n'est pas au standard. Mongazi : « le son marche sur mon iPhone ».
- **Les rappels** : 38 messages du 20/11 dans « À envoyer » de NEBULA Suivi, tâche Windows « NEBULA rappels envois »
  (toutes les 20 min, alerte qui insiste). Son iPhone est abonné, l'essai est arrivé.
- **ADEMAR v2 « La cour de la cuisine »** EN LIGNE : vraie 3D au téléphone (fini la vidéo en boucle), on descend sur
  les toits de Cotonou, on longe 7 foyers de côté, on remonte. Mongazi : « j'aime bien comment t'as fait, c'est beau ».
- **Flow pour la 3D ?** Réponse donnée : possible (Veo fait les mouvements de caméra, joués au doigt), mais Veo
  invente (plats, bijoux), pèse lourd (50 Mo pour 10 plans) et manque de précision ; le MÉLANGE est retenu : Flow pour
  l'entrée (aucun produit), 3D codée pour les produits.
- **Maison des bijoux v2 « La galerie des écrins »** : galerie 3D écrite (rideau de velours, lustre, 5 vitrines de
  verre et laiton, dessins des familles en fil d'or qui se tracent, écrin final) ; entrée Flow à générer (prompts :
  `nebula-apercus/bijoux/PROMPTS-FLOW.md`, aussi dans le Journal du suivi). Corrections de la dernière passe NON
  vérifiées : le PC était saturé (Chrome avec Flow, 1 Go libre), rien n'est publié.
- **Règle ajoutée** : jamais promettre un déplacement de Mongazi sans lui demander (`prospection/VENDEUR.md` § 6).
