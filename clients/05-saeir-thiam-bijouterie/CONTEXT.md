# CONTEXT — Djambar Team (pôle Saeir Thiam Bijouterie)

> Client #05 · Fiche reçue le **2026-06-22** via le formulaire de `nebula-agency.online`.
> Commande **acceptée**. Statut : **EN LIGNE sur domaine final** — https://djambarteam.com · assets réels intégrés, affiche PDF générée.

## 🌐 Mise en ligne
- **LIVE (domaine final)** : **https://djambarteam.com** (+ `www`) — Cloudflare Pages, projet `djambar-team`, HTTPS auto valide. URL d'origine technique : `djambar-team.pages.dev`.
- **DNS = Cloudflare** (2026-06-23) : domaine acheté chez **Hostinger**, nameservers déplacés vers Cloudflare (`paul`/`rosemary.ns.cloudflare.com`). Zone Cloudflare = 2 CNAME **proxied** (`@` et `www` → `djambar-team.pages.dev`). Custom domains Pages = `djambarteam.com` + `www` (status active). Pas d'email sur le domaine (rien à préserver à la bascule).
- Toutes les URLs internes/canonical/og:url/JSON-LD/sitemap/robots migrées **`pages.dev` → `https://djambarteam.com`** (V13).
- ⚠️ Le **token `secrets/cloudflare.env` est « Pages » uniquement** : il déploie Pages MAIS ne peut PAS créer de zone ni éditer le DNS (fait à la main par Mongazi au dashboard). 
- Déploiement via `npx wrangler pages deploy` (build propre : HTML + `assets/app.*` + `assets/images/{logos,og,favicon,gallery}` + `assets/videos/thiam.MP4`, **sans** les photos sources lourdes).
- ▶️ **Reste optionnel** : (a) redirection **www → apex** (301, via Cloudflare Redirect Rule — actuellement www sert le site en direct, canonical pointe sur l'apex = OK SEO) ; (b) **régénérer l'affiche PDF** avec un QR « site » → `https://djambarteam.com` (le QR actuel pointe WhatsApp + Maps).

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
- **THÈME ACTUEL = CLAIR LUXE** (V6, 2026-06-23, demandé par Mongazi) : blanc dominant + bleu très clair (sections alternées) + nuance or douce ; bleu nuit & or réservés aux **accents** et aux **sections sombres ponctuelles** (CTA, hero photo flouté, pages « Bientôt », footer). **Halo lumineux** doré/bleu qui suit le curseur (desktop, off mobile/reduced-motion). ⚠️ Avant V6 le site était **SOMBRE** (V3) ; bascule complète sombre→clair faite + QA.
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

## Passe « Fonds média : flou allégé + colliers + vidéo sur pages Bientôt » (V14, 2026-06-23) ✅
Mongazi : flou des images de fond **plus léger** (voir un peu l'image) ; **images de colliers en fond** sur d'autres pages ; **vidéo `thiam.MP4` en fond** sur une page « Bientôt » (flou **très léger**).
- **Flous allégés** : hero-bg base 16→**9px** ; hero nuit bijouterie 14→**8px** (brightness .66→.74, opacity .42→.52) ; bandeau éditorial 14→**8px** ; vidéo CTA 5→**4px**. On voit nettement mieux les pièces.
- **Fonds collier ajoutés** : **accueil** (hero, `colliers/g7` ghosté sous le voile clair, subtil) + **événementiel** (soon-hero, `colliers/g1`, bien visible sur le fond sombre).
- **Vidéo de fond** : **communication** (soon-hero) = `thiam.MP4` en fond, **flou 4px** (« très léger »), poster `colliers/g3`. Nouveau système réutilisable `.soon-media` (img|video) + `.soon-media-veil` (voile navy lisibilité) ; JS bg-vidéo généralisé (`video.cta-media, video.soon-media` : pause hors-écran + reduced-motion).
- **Contraste AA** (calcul, pire cas zone claire du collier sous voile) : texte blanc **4,93** (image) / **4,78** (vidéo) ≥ 4,5 ✓ ; cas typique ~9,5.
- **QA** : rendus communication + événementiel (texte lisible, texture visible) ; index = changement le plus sûr (collier sous le voile blanc, z-index ::before>bg). Cache **`?v=20260623j`**. Déployé + prod vérifiée (4 pages 200, vidéo/images servies, CSS flous allégés + JS généralisé). Socle synchronisé dans le skill `nebula-site`.

## Passe « Domaine final djambarteam.com EN LIGNE » (V13, 2026-06-23) ✅
- **Domaine raccordé** : Hostinger (registrar) → nameservers Cloudflare → zone Cloudflare (2 CNAME proxied `@`+`www` → `djambar-team.pages.dev`) → custom domains Pages active. **HTTPS valide** vérifié (200 sur les 4 pages + 404 + sitemap + vidéo, via résolution forcée sur l'IP Cloudflare pour contourner le cache DNS local).
- **Migration URLs** : 26 occurrences `djambar-team.pages.dev` → `https://djambarteam.com` (canonical, og:url, JSON-LD, sitemap.xml, robots.txt). JSON-LD re-validés. Redeploy Pages OK.
- Setup fait **étape par étape** avec Mongazi (dashboard Cloudflare + Hostinger) car le token est Pages-only. Email : aucun sur le domaine → bascule sans risque.
- ▶️ Optionnel restant : redirection www→apex (301) + régénérer l'affiche avec QR site.

## Passe « Conversion : descriptions d'images + commander partout » (V12, 2026-06-23) ✅
Mongazi : une description à chaque image (et plus sur certaines), pousser le visiteur à commander, sur toute la plateforme.
- **24 légendes de galerie distinctes** (étaient 3 génériques répétées) — type + attribut d'artisanat (sur-mesure/gravé/maille/prénom…), **honnêtes** (pas de matière/karat inventé, « sertie » retiré).
- **Lightbox = point de commande** : bouton **« Commander ce modèle »** qui pré-remplit WhatsApp avec la description de la pièce ouverte (`je suis intéressé(e) par ce modèle : [légende]`). Browsing → commande en 1 tap. Sous-ligne « Réalisable sur-mesure, à votre taille et à votre prénom ».
- **3 cartes Collections** : sous-titre vendeur (Colliers/Bracelets/Bagues) + CTA « Voir & commander » (au lieu de « Découvrir »).
- **Nudge galerie** : « Une pièce vous plaît ? Ouvrez-la, puis commandez-la — ou faites créer la vôtre. »
- **Éthique** (rappel honnêteté) : persuasion par le désir + chemins de commande clairs, **PAS de dark pattern** (0 faux compte à rebours / faux stock / fausse urgence) — adapté à une joaillerie de luxe.
- **QA** : génération du lien « Commander ce modèle » **testée** (URL wa.me décodée = bonne légende) ; 24/24 légendes distinctes ; JS/CSS OK. Cache **`?v=20260623i`**. Déployé + prod vérifiée (24 caps, lb-order, 3 sublines, builder JS, 4 pages 200).

## Passe « Formulaire de devis → WhatsApp pré-rempli » (V11, 2026-06-23) ✅
Mongazi : un formulaire de commande côté THIAM (nom/prénom/numéro/indication, « 1ʳᵉ fois en bijouterie ? », zones à choix multiples) qui redirige vers WhatsApp.
- **Architecture** : 100% **client-side**, fidèle au modèle du site (tout passe par WhatsApp, pas de backend). Le formulaire **assemble les réponses en un message** et ouvre `wa.me/2290197967671?text=…` pré-rempli (l'utilisateur n'a qu'à appuyer « envoyer »).
- **Champs (analyse de la demande + ajouts)** : **Vous** = prénom*, nom*, numéro WhatsApp*, quartier/indication, « première fois en bijouterie ? » (Oui/Non). **Projet** = type de service* (Création/Réparation/Reproduction), type de bijou* (Chaîne/Pendentif/Boucles/Bague/Alliance/Bracelet/Autre), **matière** (Or/Argent/à conseiller — ajout), **modèle de référence** (boutique / propre modèle / à définir), **taille de bague** (ajout, **affichée uniquement si Bague/Alliance** sélectionné — JS), **description du motif**, **gravure** (ajout), **occasion/échéance** (ajout). (*) = requis.
- **UX** : zones à **choix multiples en pills tactiles** (radio stylés), validation douce (champs requis surlignés + scroll vers l'erreur), section warm + carte blanche, **pas de faux budget** (prix = discussion WhatsApp, honnêteté). Astuce « envoyez une photo dans WhatsApp » pour le modèle.
- **Les 2 CTA « commander »** (nav + bandeau sur-mesure) pointent désormais vers **`#devis`** (le formulaire) au lieu d'un WhatsApp générique → parcours qualifié.
- **Accents** : message WhatsApp en **français correct** (UTF-8 encodé, vérifié transmis OK).
- **QA** : génération du message **testée bout-en-bout** (harnais : autofill → submit → URL `wa.me` décodée = champs corrects, taille de bague apparue car Bague, optionnels vides omis) ; layout desktop+mobile rendu (carte, pills, sections) ; **overflow mobile mesuré = `scrollW==vw`, 0 débordement** (le « coupé » des captures = artefact canvas headless < viewport, pas un vrai bug) ; bouton submit passé en `white-space:normal` + label court « Envoyer sur WhatsApp » (marge de sécurité petits écrans). JS `node --check` OK. Cache **`?v=20260623h`** (5 pages). **Déployé + prod vérifiée** (form live, champ conditionnel, builder JS, CTAs→#devis, 4 pages 200).

## Passe « Vidéo de fond dans le volet commander » (V10, 2026-06-23) ✅
Mongazi : « dans le volet commander, la vidéo `assets/videos/thiam.MP4` en fond, avec un flou gaussien très léger (on aperçoit quand même la scène) ».
- **Cible** = le **volet de conversion** en bas de la page Bijouterie (la `.cta` « Offrez-vous une pièce unique / Demander un devis » = le panneau où l'on commande).
- **Implémentation** : `<video class="cta-media" autoplay muted loop playsinline preload="metadata" poster=hero-bijou.jpg>` en fond de la `.cta` (classe `.cta-video`), **flou gaussien léger** `filter:blur(5px) brightness(.6)` + `transform:scale(1.12)` (couvre le bleed du flou), **voile navy** `.cta-veil` (≈0,5) pour garder le texte blanc lisible. **Scopé** à `.cta-video` (les autres `.cta` du site — accueil, pôles — ne sont **pas** touchées). `isolation:isolate` pour un stacking propre (vidéo+voile z0, contenu z1).
- **Perf/UX** : vidéo **1,77 Mo** (légère, sous la limite 25 Mo Pages) ; `preload=metadata` (ne télécharge pas tant qu'on n'a pas scrollé) ; **pause hors-écran** + **pause `prefers-reduced-motion`** (poster figé) via JS (IntersectionObserver) ; `playsinline`+`muted` = autoplay mobile OK ; **poster** = repli image si autoplay bloqué / 4G lente.
- **QA** : poster flou rendu (desktop+mobile) = scène perceptible + texte lisible ✓ ; JS `node --check` OK ; CSS scopé (0 fuite vers les autres CTA). Cache **`?v=20260623g`** (5 pages). **Déployé** (vidéo incluse au staging) ; prod vérifiée : `thiam.MP4` servi (`video/mp4`, immutable), CTA câblée, 4 pages 200.

## Passe « Hero NUIT à faisceaux lumineux — page Bijouterie » (V9, 2026-06-23) ✅
Mongazi a fourni un **composant React « Beams Background »** (`motion/react` + canvas, style shadcn) et demandé « ceci, animé, sur la page d'accueil de l'onglet bijouterie ».
- **Décision honnête** : le site est **HTML/CSS/JS vanilla statique** (Cloudflare Pages), **PAS** React/shadcn/Tailwind/TS. Installer ce toolchain casserait le modèle de déploiement → **refusé**. Livré **le même effet en natif** (le site avait déjà un port vanilla des « beams » sur le hero accueil → réutilisé/enrichi).
- **Direction validée via AskUserQuestion** : **Hero NUIT dramatique** (vs hero clair + faisceaux doux). Choix = nuit.
- **Implémentation** : hero Bijouterie en **bleu nuit profond** (`.hero-night`), **photo bijou en fond de nuit** (opacity .42 + brightness .66), **faisceaux canvas plus nombreux & lumineux** (`night` : 30 desktop / 16 mobile, or & azur, lightness ↑, **`mix-blend-mode:screen`** = ajoute de la lumière sur le sombre), **aura dorée qui « respire »** (port du breathing overlay du composant React, CSS pur), texte blanc/champagne. **Le reste du site reste clair** (art-direction par section, conforme au register brand).
- **Nav** : `body.dark-hero` (réutilise le pattern des pages « Bientôt ») → nav blanche lisible au sommet, repasse sombre au scroll vers le contenu clair. `theme-color` du hero = `#0B1E45`.
- **Contraste AA (calcul)** sur le hero nuit : tout ≥ 10,2 (blanc 17,5 ; or/lead 10–12). ✅
- **Perf/robustesse** : faisceaux GPU (transform/opacity, blend), pausés hors-écran/onglet caché (IntersectionObserver déjà en place), **`prefers-reduced-motion`** → 1 frame statique + aura figée. Mobile plafonné à 16 faisceaux.
- **QA** : JS `node --check` OK ; rendu statique (JS off) desktop+mobile = hero nuit net + transition vers le contenu clair OK ; **faisceaux animés capturés** via harnais « rAF plafonné » (sinon la boucle infinie fait timeout les captures headless ; soft-render = sous-représente, le vrai navigateur/GPU est plus vif). Cache **`?v=20260623f`** (les 5 pages). **Déployé + prod vérifiée** (hero-night servi, screen blend, JS night, 4 pages 200).
- ⚠️ Intensité réglée « luxe » (mesurée) ; **calibrable** (op/aura/nombre de faisceaux) selon le ressenti de Mongazi en vrai sur son téléphone.

## Passe « Motion & fluidité MAX + infra pro » (V8, 2026-06-23) ✅
Mongazi : « au maximum, plus d'animation et de fluidité, mobile surtout mais aussi PC ». Skill **frontend-design + impeccable/animate**. Tout en **transform/opacity/filter** (GPU), pensé pour le **mobile 4G/low-end de Cotonou**, `prefers-reduced-motion` respecté partout.
- **Transitions de page natives** (cross-document **View Transitions**, `@view-transition{navigation:auto}`) → fondu fluide entre toutes les pages du hub (mobile + PC), coût quasi nul, ignoré si non supporté.
- **Parallax + barre de progression** en **scroll-driven CSS** (`animation-timeline:scroll()/view()`, hors main-thread, marche au tactile) : sparkles/grille/contenu du hero en profondeur, bandeau éditorial qui dérive, filet or de progression de lecture (repli rAF passif si non supporté).
- **Reveals différenciés** (fini le fade-up uniforme = le tell IA) : panneau credo qui glisse de la droite + stagger interne de ses lignes, collections en scale, easing **expo/quint**. Easing global des reveals affiné.
- **Micro-interactions** : boutons à **balayage doré** (sheen) + appui, soulignement de nav qui se dessine, **CTA aimantés** + **tilt 3D** des cartes (desktop fin uniquement, rAF gardé).
- **Mobile d'abord** : **états `:active`/tactiles** partout (pas de hover sur mobile → feedback au toucher), **menu mobile en entrée échelonnée**, ancres avec `scroll-margin` (plus de saut sous la nav).
- **Robustesse reveal** : filet de sécurité au `load` → révèle ce qui est déjà au-dessus du viewport si l'IntersectionObserver ne se déclenche pas (headless/onglet caché/crawler) → **jamais de section blanche**.
- **🐛 BUG PRÉ-EXISTANT CORRIGÉ (propagation)** : le voile blanc `.hero::before` (fait pour le hero clair à photo) **délavait les heros sombres `soon-hero`** → texte blanc quasi illisible sur **communication + événementiel LIVE** (raté à la bascule clair V6). Corrigé à la source (`.hero.soon-hero::before` = halo bleu doux au lieu du voile blanc + grille adaptée au fond sombre). Les 2 pages « Bientôt » + le **404** sont enfin nets.
- **Infra pro (B7)** : **page 404 de marque** (Cloudflare sert `/404.html`, vrai statut 404 vérifié) + **`_headers`** (HSTS, X-Frame-Options SAMEORIGIN, X-Content-Type-Options, Referrer-Policy, Permissions-Policy + **cache immuable** `/assets/*`). Pas de CSP stricte (casserait les handlers inline légitimes — onload fonts, `classList.add('js')`).
- **B8 musique** : laissée telle quelle (pad synthé, OFF par défaut, demandée au formulaire) — vraie piste = livrable client.
- **QA** : JS `node --check` OK ; exécution runtime vérifiée via `--dump-dom` (scroll-progress + halo injectés, **0 erreur**) ; rendus headless desktop+mobile (home/404/soon) ; **déployé** ; prod revérifiée : v=`e`, 5 en-têtes sécurité actifs, `/assets` immutable, 404 = statut 404 page de marque, View Transitions servies. Cache **`?v=20260623e`**.

## Passe « Check-list 2 — IA vs pro : anti-tells structurels » (V7, 2026-06-23) ✅
Skill **frontend-design + impeccable** appliqués « au maximum ». Cible = les derniers signaux *« fait par une IA »* (les points #1 design original / #3 copy de la check-list 2), sans trahir l'identité clair-luxe validée.
- **Fin de l'eyebrow systématique** (LE tell n°1 des deux référentiels : un mini-libellé majuscule tracké au-dessus de *chaque* section). Réduit de **4/9/3/3 → 2/3/2/2** kickers par page : conservé seulement comme **device délibéré** sur 2 moments signatures (hero + bandeau « Notre signature » + CTA de clôture), supprimé partout où il répétait juste le titre. Nouveau système d'en-tête éditorial : le **titre serif porte la section**, complété par une **`.deck`** (phrase de présentation, ajoutée sélectivement — pas en réflexe uniforme) et un filet or optionnel `.rule`.
- **Suppression de la grille de 4 cartes identiques** (ban explicite) « Exigence/Vision/Proximité/Prestige » de l'accueil → remplacée par un **panneau éditorial `.creed`** (surface navy unique, 4 lignes icône+titre+texte séparées par filets, raccord à l'accent de marque) + **copy spécifique** (fini les one-liners génériques type « le détail à chaque étape »).
- **Copy enrichie** : decks concrets (atelier à Cotonou, matières choisies avec le client, itinéraire), lien IG cliquable, avis = note d'exemple plus claire (honnêteté maintenue, 0 faux avis/chiffre).
- **Contraste AA revérifié** (calcul) sur les nouveaux tokens : deck `--muted` 7,6 (blanc)/7,1 (soft) ; creed texte 9,0–9,5 ; lien IG 6,8. Tous ≥ 4,5. ✅
- **Cache unifié `?v=20260623d`** (les 4 pages étaient désynchronisées : index en `c`, les autres en `b`).
- **QA visuelle** : rendus Edge headless (JS off = contenu visible par PE) desktop + mobile → panneau creed + en-têtes vérifiés, 0 débordement. **Déployé Cloudflare Pages** (staging propre 4,0 Mo) ; prod revérifiée : `/` + `/bijouterie` = **200**, v=`d` servie, clean URLs 200-direct, 0 `href .html`, TTFB 0,5–0,7 s. ✅

## Passe « ABSOLUE — Check-list 2 max perf » (V6, 2026-06-23) ✅
Mongazi : « fais l'absolue correction avec ton maximum de performance sur la check-list 2 ». Exécutée sur le **thème CLAIR** (choix confirmé : finir la bascule clair entamée). Corrections appliquées + **vérifiées en prod** :
- **Bascule clair finalisée + bugs corrigés** : la nav gardait du texte/logo **blanc** (hérité du hero sombre) → **illisible sur le nouveau hero clair**. Refonte de la logique nav : par défaut texte+logo **sombres** (hero clair = accueil/bijouterie) ; classe **`body.dark-hero`** pour les pages à hero sombre (communication/événementiel) → nav blanche au sommet, repasse sombre au scroll. Logo hero accueil = `logo-full-dark.png` (était white, invisible). Kickers hero en `--gold-ink` (lisible sur blanc).
- **#6 SEO+** : ajout **WebSite** (accueil) + **BreadcrumbList** (bijouterie/communication/événementiel). Tous les JSON-LD re-validés (parse strict OK).
- **Clean URLs (Cloudflare Pages)** : la plateforme force `/page.html`→308→`/page`. Migration **complète** de tous les liens internes + `canonical` + `og:url` + JSON-LD + `sitemap.xml` en **clean URLs** (`/bijouterie`…). Vérifié en prod : chaque clean URL = **200 direct** (plus de hop 308), 0 `href .html` dans le HTML servi.
- **#9 Conversion** : barre de **réassurance** ajoutée aussi sous le CTA de l'accueil (devis gratuits · sans engagement · réponse rapide).
- **#4 Perf (mesurée en prod, compressé CDN)** : 1er écran **accueil ~79 Ko**, **bijouterie ~115 Ko** ; TTFB ~0,44–0,64 s. Galerie : `aspect-ratio:1/1` + `width/height` sur les 24 tuiles → **0 CLS**. `fetchpriority=high` sur le logo hero accueil.
- **A11y** : **skip-link** « Aller au contenu » sur les 4 pages (cible `#contenu` sur le hero).
- **Contraste AA recalculé** (thème clair) : tous les textes ≥ 4,5 (min 4,84 = or sur fond crème) ; titres 16,3 ; liens 7,4. ✅
- **#10 Analytics** : inchangé (Cloudflare Web Analytics = 1 clic dashboard côté Mongazi, token déploiement sans scope RUM).
Cache **`?v=20260623b`** (css+js). Staging propre (3,88 Mo, sans photos sources) → **2 redeploys Cloudflare Pages** ; prod re-vérifiée (clean URLs 200, JSON-LD, perf, captures live OK).

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
