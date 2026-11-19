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
