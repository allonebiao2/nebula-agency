# 2026-07-15 — Speed×Weinkeller by CK : panier façon Luxury + coffret cadeau + retrait des WhatsApp directs

## Contexte
Modifications urgentes demandées par Ck sur le monde **Weinkeller** (la cave). Déployé en prod (`speed-weinkeller.pages.dev`, `?v=20260715d`). Stack vanilla HTML/CSS/JS partagé (`assets/app.css` + `assets/app.js`), copie de déploiement `_dist/` (gitignorée), bumps via Python UTF-8.

## Ce qui a été fait (dans l'ordre)
1. **Menu « Nos boissons »** ajouté (nav Weinkeller → `#caves`).
2. **Message permanent** sur le bouton doré « Catégories » (`.cave-launcher`) : bulle « Cliquez ici pour voir toutes nos boissons » qui **reste affichée** tant que le bouton est visible, se masque quand on est dans la cave (`#selection` à l'écran), **réapparaît** dès qu'on quitte les boissons (IntersectionObserver sur `#selection`, pas sur le bouton « Parcourir »).
3. **Catalogue compact** : `.bottles` en **2 colonnes forcées** sur mobile (`@media max-width:560px → repeat(2,1fr)`), visuels 184→118 px (photos 240→140), polices/paddings réduits → ~4 bouteilles visibles par écran. Desktop = 6 colonnes.
4. **Panier façon Luxury Club 229** (modèle repris de `ina-luxury.html`) :
   - bouton **« Ajouter au panier »** sous chaque bouteille (remplace « Commander ») ; libellé « Ajouté · N ».
   - **barre panier** en bas-gauche (compteur + total live), **modale « Mon panier »** : quantités −/+, suppression, total estimé live.
   - **formulaire** : Prénom, Nom, WhatsApp, n° alternatif · **Réception** = Livraison (Ville/Quartier/Repères/Créneau) ou Retrait en cave · Note.
   - **validation** des champs obligatoires (surligne + toast), puis **message WhatsApp structuré** (articles + total + coordonnées + livraison + réf) vers +229 0197158484.
   - persistance panier (`wk_coffret`) + coordonnées (`wk_customer`) en localStorage.
5. **Mode coffret cadeau** : « Composer mon coffret » (bulle cadeau) **active un mode cadeau suivi** (coche la case, descend au catalogue). Case « C'est un coffret cadeau » dans le panier + Occasion + Petit mot/dédicace → **message WhatsApp spécial cadeau** (« je souhaite offrir un COFFRET CADEAU 🎁 », bloc Occasion/Petit mot, mention emballage/petit mot à ses frais).
6. **Retrait de TOUS les WhatsApp directs** (exigence Ck « je n'ai jamais voulu de ça ») : 60 boutons « Commander » par bouteille + lien carrousel (« Commander cette bouteille » → « Voir dans la cave » = scroll catalogue) + **FAB WhatsApp flottant**. Le FAB audio est conservé. Désormais toute commande passe **uniquement par le panier**.

## Vérifications
QC en **vrai Chrome piloté (puppeteer-core)** : panier 620 000 F, +1→840 000 F live, validation OK (envoi bloqué si champs vides), messages WhatsApp normal ET cadeau corrects, mode Retrait masque la livraison, 0 erreur console. **Speed non impacté** (0 `.bottle`/`.b-add` chez lui même si app.js/css partagés).

## Pièges / leçons
- **Cache-bust** : bug « rien ne se passe au clic Composer » = j'avais ajouté le code panier **sans changer le `?v=`** → le navigateur rejouait l'ancien `app.js` en cache. Toujours bumper `?v=` après changement de contenu (`20260714a→…→20260715d`).
- **openDrawer verrouille le scroll** (`overflow:hidden`) : ouvrir le tiroir catégories après « Composer » annulait le scroll vers le catalogue → retiré, on scrolle direct sur `#selection`.
- **Éditer un gros bloc JS avec caractères spéciaux** (`━ × ≈ •`) via l'outil Edit échoue → passer par Write d'un fichier propre + splice Python (ancre ASCII `(function panier() {` … `    })();`).
- QC headless/virtual-time **fausse le scroll programmatique et l'IntersectionObserver** → valider ces comportements en **puppeteer réel** (vrai viewport), pas en `--dump-dom` virtual-time.

## Reste / à valider par Ck
- Prix « fourchette » comptés en borne basse (estimation, « ≈ ») ; « prix sur demande » hors total chiffré → prix final confirmé sur WhatsApp.
- 6 fiches sans prix ⏳ + autres caves Weinkeller (rouges/spiritueux) déjà en cours ailleurs.

Déployé Cloudflare + vérifié 200 en prod. Commit `5ea3f83`.


## Correctif produit 2026-07-15 (`?v=20260715e`, commit `e7fa1a9`)
**Veuve Clicquot La Grande Dame 2012** séparé en **2 fiches distinctes** (au lieu d'une seule à prix combiné « 180 000 - 190 000 » qui faussait le calcul du panier — estimation « ≈ » — et embrouillait la cliente) :
- **La Grande Dame 2012 (sans étui)** = 180 000 FCFA
- **La Grande Dame 2012 (avec étui)** = 190 000 FCFA
Carrousel nettoyé (« dès 180 000 FCFA » au lieu de la fourchette). Compteur cave **dynamique → 61 références**. QC puppeteer réel : 2 lignes distinctes, **total exact 370 000 F sans « ≈ »**, 0 erreur. Déployé + vérifié en prod. ⚠️ variantes de prix (avec/sans option) = **toujours une fiche par prix**, jamais une fourchette (sinon panier faux + confusion client).
