# LE MONDE · 14 au 16 novembre 2026 : les personnages en vidéo, le rendu de film, puis le nouveau cap

> La reprise exacte (quoi relancer, la prochaine action, les commandes, la carte du code) est dans
> `monde/REPRENDRE-ICI.md`, section « ÉTAT DU 2026-11-16, 7 h ». Ici : le fil de la conversation, avec les mots de Mongazi.

## Le fil, dans l'ordre

1. **« mon pc s'est dechargé continu la ou tu en etait »** (14 novembre) : le branchement du décor en Gaussian splat (Spark)
   était sur le disque, pas commité. Repris, contrôlé (deux faux rouges du QC réparés), poussé.
2. **« faut qu'on corriges tout les graphisme meme les personnages la facon de marcher tout on doit tout revoir comment
   faire pour qu ece soit ultra realiste ? »** → réponse : la technique d'origine plafonne (« GTA 2001 ») ; on change de
   matière couche par couche (décor en splats, personnages en vidéo en conversation, marche refaite dans le code).
3. **« google flow a un api ? pour que tu puisses utiliser veo 3.1 »**, **« ET NNOBANANA PRO »** → vérifié : Flow n'a pas
   d'API officielle ; sa clé Gemini voit Nano Banana Pro mais le refuse (quota, facturation) et ne voit pas Veo ; WaveSpeed a
   les deux (Nano Banana Pro 0,14 $, Veo 3.1 ≈ 0,40 $/s, Fast 0,15, Lite 0,05) mais le solde est de 0,04 $.
4. **« CE QUE J44AVAIS GENERER NE SUFFIT PAS ? etpour les visage comment se rappproccher le maximum possible ? »** → oui :
   ses vidéos sont photoréalistes, c'est le passage en 3D qui les détruit ; en conversation on montre la vidéo elle-même.
5. **« redonnes les prompts adapter… liste absolument toute… tout ce qui reste a faire »** → `monde/A-FAIRE.md` (qui fait
   quoi) et les consignes vidéo (`personnages/CONSIGNES.md`, « LES PERSONNAGES EN VIDÉO »).
6. **« vas y fait tout »**, **« vague pa vague »**, **« je veu sortir donc je veux que tu puisse trvailler sans t'arreter
   prends toute les decisions »**, **« fais deja tout ce que tu peux faire sans ses point… ramenes toujours a 100% avant de
   passer a un autre »** → travail en autonomie, vague par vague.
7. **La consigne pour Fable** : « Et si je devais mettre fable sur le coup quel prompt ultra optimiser… », « qu'il puisse
   travailler seul… avec ce qui est dispo actuellement », « T'as pas préciser… la qualite que j'imagine je veux que ce
   dantesque, spectaculaire qu'on n'est l'impression que c'est un vrai salon de couture », « ça doit valoir 100000
   dollars » → `monde/PROMPT-FABLE.md`. Puis il l'a **collée dans cette session-ci** : elle fait loi pour la qualité.
   **« Ne platfome pas a gta 2001 monte a gta 2026 »**.
8. **« Elle est d'accord donc t'inquiètes fais ce que tu as à faire »** (Hillary) → trace dans
   `_partage/immersive  store 3D/hillary/ACCORD.md` ; ses vidéos fabriquées gratuitement par Wan 2.2.
9. **« donnes le lien pour voir »** → `http://localhost:8765/lieux/hillary-m-styl/` (téléphone : `http://192.168.100.203:8765/…`).
10. **« fais tout le reste etap par etape »**, **« CONTINU »** → vagues 1, 2, 3 et la première partie de la 6.
11. **« UTILISES UN AGENT QUI VAANALYSER TREG QUI PERMETS UN OPEN ROUTER ? OPEN SOURCE SUR GIT HUB je veux tu analyses en
    rntiereté qu'on l'intege a nos travaux »**, puis **« en quoi il pourrait nous aider dans notre creation de boutique
    virtulle 3D interractive ? »** → agent lancé (coupé trois fois par les limites d'utilisation), rapport complet
    `_knowledge/treg-decortique.md`. **Pour la boutique 3D : presque rien** (de l'image vers vidéo payante, rien en image
    vers 3D ni en monde en splats). Verdict : pas maintenant.
12. **« Comment pouvoir avoir des eproannages 3d ultra realiste comme dans gta 6 et call of duty korea story ? »** →
    répondu : scans d'acteurs, visages à centaines de réglages, capture de mouvement, rendu de console : hors de portée d'un
    téléphone en 3G ; la vidéo en conversation est faite ; pour la marche de loin, trois pistes (3D multi-vues, avatar en
    points animé, MetaHuman dont la licence hors Unreal est contradictoire).
13. 🔴 **LE NOUVEAU CAP** (16 novembre) : **« deja les correctiona a faire les expositions sont ulta flou on ne voit pas tres
    bien les images les expos transformes les robes en 3d lesgens pourront toucher et avoir les details et son images etc..
    finalememnt il y ,aura juste hillary dans le salon et je vexu qu"lle est plus d'animation plus relle que nature et etre
    plus optimiser a la vente de ces produit »**, **« vas y »**, **« continu »** → G1 à G5 (`monde/A-FAIRE.md` § G).
14. Limite de Fable atteinte (jusqu'au 22 novembre) : il passe Claude Code sur **Opus 5.5**. Puis **« METS TOUT EN MEMOIRE A
    LA LETTRE PRES. VAIS METTRE EN MEMOIRE ET FAIT CLEAR »** → cette mémoire.

## Ce qui a été fait (commits sur `main`)

`a4a22cc` liste complète · `4dd7b7f` monde photographique (Spark) · `4ee9453` la marche (34 → 9 cm/s) · `c9f3c02`,
`3f96a89` consigne Fable · `9db7a3b`, `bd141a3` vague 1, les personnages en vidéo (QC 62/62) · `10c3abc`, `0a49568` vague 2,
le rendu et le soleil par la vitrine (66/66) · `5ea69a0` vague 3, les imprimés wax (67/67) · `defc888` vague 6, première
partie, vidéos légères à la demande, et le nouveau cap inscrit (68/68).

## Les décisions prises seul (champ libre donné par Mongazi)

- Hillary **en buste** et **en vidéo en permanence** à son comptoir ; les visiteuses en vidéo seulement en conversation.
- **Ne plus jouer** les animations Mixamo « démarrer », « arrêter », « tourner » (autres allures, double rotation).
- **La façade regarde le sud-ouest (215°)** : Hillary n'a pas de salon physique, l'orientation est libre ; ainsi le soleil
  entre tous les après-midi de l'année.
- **TAMISE 0,34** le soir, exposition du soir 0,92 ; brume 0,012 / 0,018 ; faisceaux deux fois plus doux en qualité haute.
- Les imprimés wax du décor **générés** (matière, jamais le catalogue).
- Les vidéos des personnages **hors de git** (Hillary est réelle, le dépôt est public).

## Les apprentissages

`_memoire/apprentissages/2026-11-14-marche-qui-ne-glisse-pas.md`, `2026-11-14-personnage-video.md`,
`2026-11-15-rendu-film-sans-passe.md`.
