# CONTEXT — Djambar Team (pôle Saeir Thiam Bijouterie)

> Client #05 · Fiche reçue le **2026-06-22** via le formulaire de `nebula-agency.online`.
> Commande **acceptée**. Statut : **EN LIGNE (provisoire)** — https://djambar-team.pages.dev · assets réels intégrés, affiche PDF générée.

## 🌐 Mise en ligne
- **LIVE provisoire** : **https://djambar-team.pages.dev** (Cloudflare Pages, projet `djambar-team`, branche `main`, HTTPS auto).
- Déploiement via `npx wrangler pages deploy` (token `secrets/cloudflare.env`). Dossier déployé = build propre (HTML + `assets/app.*` + `assets/images/{logos,og,favicon,gallery}`), **sans** les photos sources lourdes.
- ⚠️ **Domaine final = `djambarteam.com`** (Mr THIAM va l'acheter) → quand prêt : mapper le domaine custom sur le projet Pages + régénérer l'affiche avec un QR « site ». En attendant, le QR de l'affiche pointe vers **WhatsApp + Google Maps** (stables).
- Re-déployer après modif : rebuild du dossier propre puis `wrangler pages deploy`.

## ⭐ Architecture de marque (vision du client, à respecter absolument)
- **Djambar Team = structure MÈRE** (marque ombrelle). Le site porte ce nom dès le départ.
- La **bijouterie est la locomotive** actuelle (priorité opérationnelle), mais ne chapeaute pas le groupe.
- Pôles à venir : **Communication** (plus tard) + **Événementiel & Showbiz** (≥ 2 events en tête, guest stars).
- Le site doit rester **modulaire / évolutif** : ajouter un pôle = ajouter une page, sans refonte lourde.
- **Levier d'audience** : la visibilité des artistes (événementiel) doit ramener le trafic vers le site → découverte de toute l'offre. Communication différenciée par secteur.

## Identité
- **Groupe** : **DJAMBAR TEAM** (marque mère)
- **Pôle bijouterie** : **SAEIR THIAM BIJOUTERIE** (nom de l'enseigne physique — à conserver) · tagline **« Le Bijoutier »**
- **Contact** : Saeir THIAM
- **Secteur** : Bijoux & accessoires (or, argent, sur-mesure) + (à venir : communication, événementiel)
- **Ville** : Cotonou — Bénin
- **WhatsApp** : `2290197967671` → **CONFIRMÉ par le client** (ne change pas) · `https://wa.me/2290197967671`

## Adresse / Google Maps ✅
- **Agla Gbodjètin**, à proximité du **CEG DE L'ENTENTE**, Cotonou.
- Itinéraire : depuis la **PHARMACIE ARCHANGE**, prendre le nouveau goudron vers Akogbato, puis la **5ᵉ von à droite** et encore la **1ʳᵉ von à droite**. Boutique à droite, enseigne **SAEIR THIAM**.
- Lien court : `https://maps.app.goo.gl/CWuoF2epYVKeAQs57`
- Place Google : **SAEIR THIAM BIJOUTERIE** — cid `0x102357cccd8885c1:0x43fda23d25e44dcc`.

## Réseaux sociaux ✅ (câblés footers + affiche)
- **Instagram** : https://www.instagram.com/djambarteam_bijoucomevent (handle = bijou + com + event → confirme les 3 pôles)
- **TikTok** : https://www.tiktok.com/@saeirthiam
- **Facebook** : https://www.facebook.com/share/18koUwZtUH/

## Activité (texte fourni par le client)
> Création • Réparation • Vente de bijoux
> Or • Argent • Bijoux personnalisés
> **L'élégance dans chaque détail.**

## Assets reçus ✅
- **Logo** (`assets/images/Logo/`) : `1000000104.png` = **noir** (arbre stylisé + porte + « DJAMBAR TEAM »), `1000000103.png` = **blanc** (fonds sombres). 1181×1181, transparent, ~60 Ko. **Même logo pour tous les pôles.**
- **Photos bijoux** (`assets/images/`) : 3 catégories — **Colliers** (~16), **Bracelet** (~24), **Bague D'alliance en Or et Argent** (~33).
  - ⚠️ Les photos portent **déjà le branding** : watermark « Saeir Thiam · Le Bijoutier » + n° WhatsApp + logo Djambar Team → **on garde** (identité du client), on ne fait que redimensionner/compresser pour le web (`assets/images/gallery/`).

## Direction artistique (appliquée)
- **Palette imposée** : **Bleu nuit + Blanc**, accents **or/argent** (rappel du métier).
- **Style** : luxe éditorial, verre dépoli léger (perf mobile/4G). Typo **Cormorant** (titres) + **Jost** (texte — choisi pour plus de caractère vs Montserrat, jugé trop répandu).
- Design system généré via le skill **UI/UX Pro Max** (palette/typo grounded), reco rose/or écrasée par la palette client.

## Architecture du site (construite)
Hub multi-pages dans `clients/05-saeir-thiam-bijouterie/` :
- **`index.html`** — accueil **groupe Djambar Team** (hero ombrelle, les 3 pôles, valeurs, CTA).
- **`bijouterie.html`** — pôle **Saeir Thiam Bijouterie** complet : savoir-faire (Création/Réparation/Vente), matières (Or/Argent/Sur-mesure), **galerie filtrable + lightbox**, avis, **Google Maps + itinéraire**, devis WhatsApp.
- **`communication.html`** + **`evenementiel.html`** — pages « Bientôt » élégantes (teasers, opt-in « me prévenir »).
- **`assets/app.css` + `assets/app.js`** — design system + comportements **partagés** (cache-bust `?v=`). Ajouter un pôle = dupliquer 1 page légère.
- **Images** : chemins relatifs `assets/images/...` (PAS base64 — choix assumé pour un hub multi-pages déployé sur Cloudflare Pages : plus léger, cacheable, lazy-load).

## Options demandées (formulaire) — état
- [x] Boutons WhatsApp (pré-remplis par contexte de page)
- [x] Galerie photos (lightbox + filtre par catégorie)
- [x] Musique d'ambiance (lecteur flottant, baseline audio mobile, OFF par défaut)
- [x] **Affiche PDF A4** (`assets/docs/Affiche_Saeir_Thiam_Djambar_A4.pdf` — générée via `affiche.html` + Edge ; 2 QR : WhatsApp + Maps)
- [x] Google Maps (adresse + itinéraire intégrés)
- [x] Section avis (⚠️ 3 exemples « à valider » — remplacer par de vrais avis)

## Passe « Check-list 2 — IA vs pro » (V5, 2026-06-23) ✅
- **#6 SEO technique** : JSON-LD **JewelryStore** (adresse, horaires, tél, makesOffer, sameAs réseaux, hasMap) sur bijouterie + **Organization** (subOrganization JewelryStore) sur accueil ; **robots.txt** + **sitemap.xml** (4 URLs). JSON-LD validés (parse strict).
- **#3 Copywriting + #9 Conversion** : **barre de confiance** (4 piliers VRAIS : fait main à Cotonou, or & argent, sur-mesure & gravure, devis gratuit) + ligne de **réassurance** sous le CTA final (devis gratuit · sans engagement · réponse rapide · visite en boutique). **Aucun faux chiffre ni fausse urgence** (honnêteté). Avis = toujours exemples « à valider » (vrais avis = livrable client).
- **#4 Vitesse** : 1er écran ~180 Ko + polices, TTFB ~0,6 s (CDN Cloudflare), polices non-bloquantes, images lazy. Rapide (pas de Lighthouse formel).
- **#10 Analytics** : **Cloudflare Web Analytics** = bon choix (gratuit, sans CB, sans cookie) MAIS le token API de déploiement n'a pas le scope Analytics → **activation = 1 clic dashboard par Mongazi** (Cloudflare → Web Analytics → Add site `djambar-team.pages.dev`, ou Pages > projet > Metrics > Enable). Non fait côté code (pas de script bidon).
- **#1/2/5/7** déjà ✅. **#8** : robots/sitemap = déploiement + propre ; domaine final + test WhatsApp réel = côté Mongazi/client.
Cache `?v=20260622h`. LIVE + redeploy Pages OK.

## Passe « Check-list 10 000 $ » (V4, 2026-06-22) ✅
Corrections demandées par Mongazi (check-list 1, 8 points) sur le thème sombre :
- **05 Imagerie** : art-direction `_build_gallery_v2.py` (ré-exécutable) → curatage des meilleures sources + **grade unifié vers le nuit** + **vignette** (focus bijou, noie fonds parasites) + crops carrés. Hero Chadé regradé. ⚠️ watermarks client (n° + logo) **conservés** = décision anti-vol de Mr THIAM ; vrai cran « 10k » = reshoot fond noir / retrait watermark (à lui de décider).
- **06 Motion** : suppression du fade-up générique → **séquence d'entrée chorégraphiée du hero** (stagger au chargement) + reveals **dé-gatés** (`.js` sur `<html>` ; sans JS = visible, conforme règle impeccable).
- **07 Mobile** : vraies décisions (marquee redimensionné, hero `background-position:62%` garde le pendentif, légendes galerie visibles au tap car pas de hover tactile).
- **08 Invisible** : **contraste AA vérifié par calcul** (min 7.25, tout ≥4.5) ; **polices non-bloquantes** (preload+swap, noscript) ; **preload du hero** ; **canonical + og:url** ; `theme-color` #050d1f. HTML prod ~0,65 s.
- 02/03/04 (typo/couleur/hiérarchie) déjà ✅, renforcés.
Cache-bust `?v=20260622g`. LIVE + redeploy Pages OK.
⚠️ RESTE pour atteindre vraiment 10k (cf. mon audit honnête) : photos sans watermark, **vrais avis**, **domaine final**, **analytics**, schema SEO, test WhatsApp réel.

## Refonte visuelle V3 — THÈME SOMBRE LUXE (inspiration immersive, 2026-06-22) ✅
Mongazi voulait **le mood** de l'inspiration (`_partage/inspiration.jpg`), pas que la structure → bascule en **thème sombre immersif** : fond bleu nuit profond (`--bg #050d1f`) partout, texte blanc, accents or, cartes en verre sombre, **hero avec photo produit dramatique en fond** (collier Chadé sur velours bleu → `hero-bijou.jpg`), bande **« GET SOCIAL »** (6 vignettes → Instagram). Interprétation « bleu/blanc » de Mr THIAM en version sombre (bleu = base, blanc = texte). PAS de faux discount/compte à rebours (malhonnête pour un vrai bijoutier) : on garde le traitement visuel, pas la fausse promo.
⚠️ Bug attrapé en QA visuelle : token `--gold-deep` était `#B8924` (hex invalide) → corrigé `#A8842F` (cassait le dégradé des boutons or). Leçon : toujours QA visuelle après réécriture CSS.

## Refonte visuelle V2 (composants éditoriaux, 2026-06-22) ✅
Inspiration fournie par Mongazi (`_partage/inspiration.jpg`, « The Ancient Coin Collector ») — **transposée** sans trahir la charte (on RESTE bleu nuit/blanc/or, PAS le sépia de la réf). Skill `frontend-design` appliqué.
- **Section « Collections »** : 3 grandes cartes-image éditoriales (Colliers / Bracelets / Bagues & Alliances) avec libellé en surimpression + liseré or au survol → **cliquables = filtre** de la galerie (scroll auto).
- **Galerie masonry** : hauteurs naturelles (fini les carrés plats), **spans calculés en JS** (`grid-auto-rows` + `getBoundingClientRect`), **hover pro** (zoom image, liseré or, légende qui monte), **apparition échelonnée** au scroll.
- **Bandeau défilant (marquee)** éditorial : Création · Réparation · Or · Argent… (losange or, `overflow:hidden` → 0 débordement, pause au survol, off si reduced-motion). Présent aussi sur l'accueil.
- **Bandeau éditorial avec IMAGE BRACELET EN FOND** (`assets/images/bg-bracelet.jpg` = chaîne torsadée traitée Pillow : recadrage large, voile bleu nuit, flou léger) + voile dégradé navy → « Chaque pièce raconte une histoire » + CTA. `background-attachment:fixed` (parallax) desktop.
- QA : DOM vérifié (images chargées, spans OK), **over=0** mobile (390px), tout 200 en prod. Cache-bust `?v=20260622e`. ⚠️ captures headless ne peignent pas les images `decoding=async` (artefact, OK en vrai navigateur).

## Horaires ✅ (intégrés — page bijouterie + footer accueil)
- Lundi – Vendredi : **9h30 – 20h00** · Samedi : **9h30 – 19h00** · Dimanche : **Fermé**
- Affichés avec **surlignage automatique du jour courant** (JS `data-day` / `getDay()`).

## Reste à récupérer / faire
- [ ] **Avis clients réels** (remplacer les exemples)
- [ ] Noms officiels + contenu des pôles Communication / Événementiel (quand prêts) + les 2 events en tête
- [ ] Musique : piste libre de droits du client (sinon pad d'ambiance synthétisé par défaut)
- [ ] Validation finale de Mr THIAM (textes « à valider »)
- [ ] **Domaine final `djambarteam.com`** : mapper sur le projet Pages quand acheté + régénérer l'affiche (QR site)

## État d'avancement
- [x] Fiche reçue + commande acceptée + back-office (lead id=4, En cours)
- [x] Vision groupe captée + architecture validée (hub multi-pages)
- [x] Design system + socle CSS/JS partagés
- [x] 4 pages construites (accueil groupe + bijouterie + 2 pôles « Bientôt »)
- [x] Assets réels reçus (logo 2 versions + photos 3 catégories) + adresse/Maps
- [x] Intégration logo + photos + Maps + renommage pôle « Saeir Thiam Bijouterie »
- [x] Police Jost (ajustement design)
- [x] Affiche PDF A4 (2 QR : WhatsApp + Maps)
- [x] **Mis en ligne (provisoire)** : https://djambar-team.pages.dev
- [ ] Avis réels + horaires
- [ ] Validé par le client
- [ ] Domaine final `djambarteam.com` (quand acheté)

## Décisions importantes
- **Marque** : site = **Djambar Team** (groupe) ; pôle bijoux = **Saeir Thiam Bijouterie** (enseigne) ; tagline **« Le Bijoutier »**.
- **WhatsApp confirmé** `2290197967671` → câblé.
- **Images en relatif** (pas base64) pour ce hub multi-pages (perf + évolutivité).
- Watermarks des photos **conservés** (branding client).

## Procédure → futur skill
- Ce projet est le **gold standard** documenté dans la branche cerveau **`_memoire/procedure-vitrine/`** (procédure end-to-end vitrine/catalogue+QR, pour créer un skill autonome « formulaire → produit fini »).

## Liens
- Back-office (lead site) : https://partenaires.nebula-agency.online (clients « site », En cours)
- Procédure / futur skill : `_memoire/procedure-vitrine/`
- Google Maps : https://maps.app.goo.gl/CWuoF2epYVKeAQs57
- Assets : `assets/` (`images/` dont `Logo/`, `Colliers/`, `Bracelet/`, `Bague D'alliance en Or et Argent/`, `gallery/`)
- Site : `index.html` · `bijouterie.html` · `communication.html` · `evenementiel.html`
