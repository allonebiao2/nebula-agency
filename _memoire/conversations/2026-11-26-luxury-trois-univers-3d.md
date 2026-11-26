# 2026-11-25/26 · Luxury Club 229 : les trois univers en 3D, Cozy dans INA, l'harmonisation faciale

Rang 1 de la zone travaux. Détail complet et pièges : `clients/04-luxury-skin-clinic/REFONTE-26-11.md`.

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
