# 2026-11-25/26 · Luxury Club 229 : les trois univers en 3D, Cozy dans INA, l'harmonisation faciale

Rang 1 de la zone travaux. Détail complet et pièges : `clients/04-luxury-skin-clinic/REFONTE-26-11.md`.

## ⛔ DERNIER ÉTAT (26/11 matin) : le site est EN MAINTENANCE
- Mongazi : « je ne veux pas qu'elle voie les modifications là-bas, coupe la visibilité, il faut que ça affiche en
  maintenance ».
  - luxuryclub229.com répond 503 partout (`_maintenance/_worker.js`, déploiement `15f909bb`).
  - Verrou dans `_dist.py` (`MAINTENANCE.md`).
  - Aperçu : https://apercu.luxury-club-229.pages.dev (`bb091e4b`, noindex).
- Fait ensuite (ses retours) :
  - le Menu en haut et la bulle « Retrouvez ici notre menu » ;
  - « Catalogue » renommé « Menu » ;
  - « Nos résultats » à la place des avis ;
  - Cosmelan, Melan 2 et Perfect Derma ajoutés ;
  - Massage et VIP retirés, Mésothérapie ANAGEN ;
  - produits INA détourés sur fond noir.
- QC vert sur les 4 pages, aux deux largeurs.
- ⏳ **Ses photos avant / après** (elle les envoie). ⏳ **La décision de rouvrir le site** (Mongazi).

## Ce que Mongazi a demandé
- 25/11 : « commence le travail de Sabrina Luxury, expose ton plan, recherche des vitrines ou catalogues digitaux avec
  du 3D scrolling ou de la 3D immersive et interactive, un salon de beauté, décortique-les et utilise-les comme
  référence, ça doit être submersif et immersif plus que pour Semelle d'Afrik ».
- 26/11 : « continue et finalise […] une sorte de visite dans un salon de beauté avec l'exposition des produits […] ça
  doit rester dans trois univers, donc respecter les trois univers et leur porter chacun l'expérience 3D immersive
  interactive adaptée à chacun d'eux ».

## Les références (neuves, inscrites au registre)
`nebula-apercus/_socle/references/FIRSTPAGE-VIBRANT-clinique-PROMPT.md`.
- **FIRST PAGE 3D** (firstpage3d.com) : le parcours de clinique, pour la STRUCTURE.
  - Ce qu'on prend : les étapes numérotées, les points posés dans la scène, les pastilles sur le bord, la carte
    d'action de fin.
  - Mesuré : leur visite est une vidéo de 30 s que le défilement fait avancer ; on ne la reprend pas, règle du 19/11.
- **Vibrant Wellness** (Noomo) : on touche une zone, la caméra s'approche, la zone s'allume. C'est l'EFFET.
- **Facework** (Framer) : la fiche de soin.

## Ce qui est fait (branche `worktree-braise-etiquettes-rectangle`)
- **Cozy entre dans INA** : 7 produits, famille « Intime & bien-être », INA passe de 49 à 56 produits.
- **`harmonisation-faciale.html`** remplace Cozy, dans le hub, les menus, la recherche et le sitemap ; `cozy.html`
  redirige vers INA. Ses 3 flyers, 12 tarifs mot pour mot, la consultation avec « J'ai lu et compris ».
- **Les trois univers en 3D** (`assets/js/salon3d/`) :
  - la clinique, un salon en plein jour de 14 stations ;
  - INA, une galerie d'arches d'or, une vitrine et un carrousel des vraies photos par famille ;
  - le cabinet privé, où la zone touchée s'allume sur SON flyer.
- `llms.txt`, `tarifs.md` et le JSON-LD de l'harmonisation sont LUS dans les pages.

## ✅ EN LIGNE le 26/11 (après le « vas-y » de Mongazi)
- **QC vert, une largeur à la fois** :
  - clinique : 90 + 90 contrôles ;
  - INA : 18 + 18 ;
  - harmonisation : 18 + 18 ;
  - hub : 15 + 14.
- Les planches 390 et 1440 ont été regardées. Les caméras du téléphone ont été inclinées pour que le sujet passe
  au-dessus de la fiche.
- Déploiement `d9ae0bd1`. Vérifié en lisant le corps des fichiers sur luxuryclub229.com, adresses nues comprises.
- Le QC sert maintenant les pages en HTTP, une largeur par passage (`--largeur`), et libère la scène WebGL avant
  les mesures de contraste : sans cela, le PC le tuait (code 137).

## Ce qui n'était pas fait avant la mise en ligne (historique)
- ⏳ **Le QC complet de la clinique et d'INA** : arrêté deux fois par Claude Code faute de mémoire sur le PC (8 Go).
  - Le QC de l'harmonisation a tourné : 32 verts, 4 rouges, tous corrigés depuis.
  - Les captures ont été regardées au PC, en 1440. **Le téléphone (390) n'a pas été regardé.**
- ⏳ **Rien n'est déployé** : la règle est un QC vert d'abord.
- ⏳ L'assistant qui vient saluer (`invite.js`) n'est pas posé.
- ⏳ D'elle : les suppressions dans INA, les nouveaux soins visage, le prix du paiement Mobile Money.

## Le soir du 26/11 : la 4K et la fluidité (session de reprise)
- Deux demandes de Mongazi : « la vitrine en 4K » et « le plus fluide possible ». Le travail était sur le disque,
  pas validé : repris, contrôlé, validé (commit `dfc551c`). Détail : `REFONTE-26-11.md` § 3 ter.
- Le moteur : jamais sous 2x, budget 3840 × 2160 ; une carte graphique faible démarre au natif ; 60 i/s visés ; les
  ombres figées (les couper gelait la 3D en recompilant toutes les matières) ; compilation en parallèle et textures
  envoyées une par image, donc plus de gel au démarrage ; `window.S3D` dit ce qui est rendu.
- ⚠️ **L'agrandisseur des produits (Real-ESRGAN) avait été tué en pleine écriture** : un `bonbon-scrub.webp` de
  0 octet figurait dans la liste que lit le moteur. Il écrit maintenant à côté puis renomme.
- Les modules 3D s'importent entre eux sans `?v=` : ils passent en `no-cache` dans `_headers` (304 s'ils n'ont pas
  changé). Le `?v=` du démarrage passe à `20261126u`.
- `main` fusionné dans la branche (conflit sur la liste des travaux, les deux côtés gardés).
- La ligne du client 04 dans `CLAUDE.md` est résumée (6 455 → environ 2 000 caractères), l'ancienne est archivée
  telle quelle à la fin du `CONTEXT.md`.

## Le soir du 26/11, suite : « le travail doit valoir 10 000 $ », par vagues
- Méthode : tout photographier d'abord (chaque étape des visites, chaque écran, téléphone ET PC), juger, puis trois
  vagues. Détail : `REFONTE-26-11.md` § 3 quater.
- **Vague 1** (`11dd017`) : l'hôtesse ne recouvre plus la visite ; étiquettes des points sans coupure ni collision ;
  fiches compactes et produits plus grands au téléphone ; sous-navigation d'INA calée sur l'en-tête mesuré.
- **Vague 2** (`f2a4b3c`) : un caisson lumineux par soin du visage (croquis, nom, prix, durée) au lieu de huit fois le
  même panneau de bois ; trois croquis neufs (Cosmelan, Melan 2, Perfect Derma).
- **Vague 3** (`0aee101`) : plafond blanc chaud au lieu du béton gris taché, murs à la chaux, terrazzo fin, vignettage.
- ⚠️ `node --check` ne voit pas une variable déclarée deux fois dans un module : `node --input-type=module --check`.
- Aperçu `a23ccbcc`, poussé dans `main`. La production reste en maintenance.
