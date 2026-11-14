# LE MONDE · la consigne à donner à Fable (2026-11-14)

> Mongazi : « si je devais mettre Fable sur le coup, quel prompt ultra optimisé… », puis « qu'il puisse travailler
> seul, tout faire avec ce qui est dispo actuellement, sans mon intervention ». À coller tel quel au début d'une session.

```
Tu reprends LE MONDE, le salon 3D d'HILLARY M. STYL (dépôt nebula-agency, dossier monde/). Objectif : que chaque capture du salon, au téléphone comme à l'ordinateur, puisse passer pour une image de Call of Duty ou de GTA 6, sans rien casser de ce qui marche (visite, conseil, commande WhatsApp). Je ne suis pas là : ne me pose AUCUNE question, ne m'attends jamais, décide seul et écris chaque décision avec sa raison. Tu travailles UNIQUEMENT avec ce qui est disponible aujourd'hui, listé plus bas.

LA QUALITÉ QUE JE VEUX (elle passe avant tout le reste)
La barre : un travail qui vaut 100 000 dollars. Fais le maximum de ce que tu peux, jamais « assez bien » : tant qu'une capture peut être meilleure, elle n'est pas finie, et tant qu'il reste une amélioration que tu peux faire seul, tu continues.
Dantesque, spectaculaire, et surtout VRAI. Quelqu'un qui voit une capture doit croire que c'est la photo d'un vrai salon de couture à Cotonou, pas un jeu. Le test : trois captures montrées à quelqu'un qui ne sait pas, il doit hésiter entre « photo » et « 3D ».
Un vrai salon de couture, c'est :
- la lumière : le jour qui entre par la vitrine et se pose en flaques chaudes sur un sol poli qui reflète tout ; le soir, des spots qui découpent les robes dans la pénombre, la poussière qui danse dans les faisceaux ;
- les matières : le wax qui a du grain et des plis, le satin qui brille, le velours qui boit la lumière, le bois veiné, le laiton patiné, le verre et ses reflets ;
- la vie : des rouleaux entamés, des chutes de tissu au sol, un mètre ruban, des épingles, une tasse, des croquis, des cintres de travers. Le réel vient de l'imperfection, jamais d'un décor trop propre ;
- la profondeur : un premier plan, un milieu, un fond, et la rue qui vit derrière la vitrine ;
- les gens : des visages photographiques, des corps qui pèsent sur leurs pieds, des regards qui se croisent ;
- l'échelle : du volume, de la hauteur, une entrée qui coupe le souffle quand les portes s'ouvrent.
Spectaculaire veut dire que chaque zone a son moment, comme un plan de film : l'arrivée, la robe vedette sous sa lumière, le comptoir d'Hillary.
L'ambiance à atteindre : mes vues du salon dans « _partage/immersive  store 3D/salon/ » et ma photo de vision « _partage/immersive  store 3D/ff6cc3de-70c6-4fd8-a801-e694e3bbaa7d.jpg ». On vise la qualité d'image des grands jeux récents, sans rien leur emprunter.

AVANT DE COMMENCER
1. git fetch puis python scripts/rapatrier.py. Lis dans cet ordre : monde/REPRENDRE-ICI.md (section « ÉTAT DU 2026-11-14 »), monde/A-FAIRE.md, monde/REALISME.md, monde/VAGUES.md, monde/lieux/hillary-m-styl/personnages/CONSIGNES.md, _memoire/apprentissages/2026-11-14-marche-qui-ne-glisse-pas.md.
2. Lance python monde/_servir.py --sans-construire en fond, puis python monde/_qc.py : note le score de départ.
3. Captures « avant » : téléphone 390 et ordinateur 1440 (?qualite=haute), de jour (?heure=14) et de nuit (?heure=21). Regarde-les toi-même, à côté de mes vues du salon.

LA DIRECTION EST TRANCHÉE
La technique d'origine (boîtes, textures dessinées, personnages TRELLIS animés par Mixamo) plafonne à « GTA 2001 ». On ne la polit plus : on remplace chaque couche par de la matière photographique. Décor : un monde en Gaussian splat (socle/monde-photo.js, Spark, ?monde=). Personnages en conversation : leurs vidéos détourées (socle/perso-video.js, préparées par _outils/perso_video.py). Personnages qui marchent : la 3D, marche calée sur les pieds (_outils/mesurer_marche.py).

CE QUI EST DISPONIBLE (et rien d'autre)
- Mes vidéos (7,93 s, 720x1280, fond gris) dans « _partage/immersive  store 3D/personnages/<prénom>/videos/ » : afi-parler, afi-marcher, senami-parler, senami-ecouter, senami-marcher, senami-tourner, maman-parler, maman-marcher, maman-tourner.
- Mes images : les 4 personnages en pose A, 8 vues du salon (salon/), les planches des robes h1 et h2 (robes/).
- Les outils du dépôt : perso_video.py (détourage rembg, stabilisation, boucle, H.264 couleur et opacité côte à côte, option --reprendre), mesurer_marche.py, mesurer.py, en_3d.py (TRELLIS sur Hugging Face ZeroGPU, quota quotidien, clé secrets/huggingface.env), scripts/image_cf.py (images Cloudflare Workers AI, gratuites, pour l'ambiance seulement), Blender en D:\Blender\blender.exe (cuisson : _outils/cuire.py), les modèles rembg isnet-general-use et birefnet-general.
- PAS d'argent : WaveSpeed à 0,04 $, Higgsfield à 0 crédit, Marble sans export. Ne t'en sers pas.

LES VAGUES, DANS CET ORDRE (chacune à 100 % avant la suivante)
1. Les personnages-vidéo : Afi (parler), Sènami (parler et écouter), Maman (parler). Afi et Maman n'ont pas de vidéo « écouter » : choisis le meilleur repli et écris pourquoi. Planche 3D contre vidéo, au téléphone et à l'ordinateur, de jour et de nuit.
2. Le rendu de niveau AAA sur le salon actuel : étalonnage filmique (AgX ou ACES, LUT chaude), exposition douce, poussière et brume légère dans les faisceaux, occlusion, reflets du sol, ombres de contact, anticrénelage, grain et vignettage discrets. Un niveau par qualité (basse, moyenne, haute).
3. La vie et les matières : plus d'objets de métier, plus d'imperfections, des matières vraies (wax, satin, velours, bois, laiton, verre), un moment de mise en scène par zone.
4. Le décor photographique SANS PAYER : essaie une voie gratuite « une image → une scène en splats » (par exemple Apple SHARP, NVIDIA Lyra 2, ou mieux si tu trouves) sur un Space Hugging Face, depuis une vue du salon d'abord vidée de ses robes générées. Licence vérifiée pour le code ET pour les poids. Si aucune voie ne tient, écris-le et garde le décor modélisé.
5. Maman en 3D (en_3d.py, quand le quota TRELLIS revient), pour la marche de loin.
6. La 3G : compression (meshopt, KTX2), chargement par étapes, mesure au téléphone.
7. L'interface : une main animée la première fois, les animations des panneaux (fiche, sac, cadran).
Puis les autres points de monde/A-FAIRE.md que tu peux faire seul.

LA MÉTHODE
- Pour chaque vague : captures avant, travail, captures après, aux 4 mêmes réglages. Note chaque capture sur 7 critères, sur 10 : (1) lumière motivée, ombres de contact, rebonds ; (2) matières : aucune surface unie, rugosité, reflets justes ; (3) profondeur : premier plan, fond, flou ; (4) personnes : visage photographique, pieds au sol, regard vivant ; (5) étalonnage : noirs denses, hautes lumières douces ; (6) plus rien qui ressemble à une maquette ; (7) l'effet « waouh » : la capture coupe le souffle et pourrait passer pour une photo d'un vrai salon. Une vague n'est finie que si chaque critère qu'elle touche atteint 8, et le critère 7 au moins 8 sur toutes les captures.
- Mesure, ne suppose pas : images par seconde, poids chargé, patinage des pieds. Aucune régression acceptée.
- Un quota épuisé ou un service injoignable : note l'heure de reprise dans A-FAIRE.md, passe à la vague suivante, reviens-y ensuite.
- Une approche échoue deux fois de la même façon : changes-en et écris pourquoi.

LES INTERDITS
- Jamais une robe générée par IA présentée comme le catalogue d'Hillary : ses pièces viennent de son catalogue, lu à la source, jamais recopié.
- Aucun visage d'une personne réelle sans accord écrit.
- Aucune copie d'un jeu existant (images, modèles, musique, interface) : on vise son niveau, pas son apparence.
- Aucun code ni poids sans licence commerciale vérifiée.
- Aucun achat, aucune mise en ligne, aucun compte créé.
- Premier écran sous 320 Ko, tout le lourd après, en fondu ; 30 images/s au téléphone.
- Ce PC a 8 Go et une carte Intel HD 5500 : UN SEUL travail lourd à la fois (un navigateur Playwright, OU un détourage, OU Blender), sinon Claude Code les coupe faute de mémoire.

À LA FIN DE CHAQUE VAGUE
QC vert (python monde/_qc.py, avec un contrôle neuf pour ce que tu as construit), captures regardées, A-FAIRE.md coché avec les chiffres, REPRENDRE-ICI.md et VAGUES.md à jour, ce que tu as appris dans _memoire/apprentissages/, commit puis push sur main.

TON RAPPORT FINAL
Un tableau avant/après des 7 critères pour les 4 captures, les images, les images/s, et la liste exacte de ce qui reste, avec pour chaque point qui doit le faire.
```

## Pourquoi elle est écrite ainsi

- **La direction est imposée** : sans elle, un modèle repart polir les boîtes et les textures dessinées, ce qui ne
  dépassera jamais « GTA 2001 ».
- **Des critères notés sur des captures** : « ressembler à GTA 6 » ne se vérifie pas, sept critères notés sur 10 si.
- **La qualité est décrite avec des choses qu'on voit** (Mongazi : « dantesque, spectaculaire, qu'on ait l'impression que
  c'est un vrai salon de couture ») : la lumière, les matières, la vie, la profondeur, les gens, l'échelle, et un test.
- **Les interdits viennent du dépôt** (`CLAUDE.md`, `A-FAIRE.md`) : le catalogue jamais généré, les licences
  vérifiées, la 3G, la mémoire du PC.
- **« Ne me pose aucune question »** plus **« écris-le dans A-FAIRE.md et passe à la suite »** : la session ne se
  bloque jamais sur ce qui t'attend.
