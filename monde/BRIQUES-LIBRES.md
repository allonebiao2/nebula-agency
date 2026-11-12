# Les briques gratuites et libres, vérifiées

> Vérifié le 2026-11-12 **sur l'API de GitHub** (licence déclarée, étoiles,
> date du dernier travail, archivé ou non), pas de mémoire. Une licence
> « NOASSERTION » veut dire que GitHub n'a pas su la lire : elle est à relire
> dans le fichier du dépôt avant usage.
>
> ⚠️ Pour un modèle d'IA, **le code ET les poids** ont chacun leur licence
> (leçon de LE MONTEUR) : vérifier les deux.

## Ce que la maquette utilise (vague 1)

| Brique | Licence | ★ | Rôle | Pourquoi |
|---|---|---|---|---|
| **three.js** 0.180 | MIT | 118 k | le moteur 3D | déjà sur le disque, déjà utilisé chez nous |
| **qrcode-generator** 1.4.4 | MIT | | le QR du cadran sur ordinateur | 20 Ko, aucun appel réseau (vérifié) |
| **MET Norway** (service public) | CC BY 4.0, usage commercial permis | | la météo réelle de Cotonou | ⚠️ Open-Meteo n'est gratuit qu'en non commercial |

**Écrit à la main plutôt qu'importé**, pour garder la page légère en 3G : la
marche le long d'un graphe (au lieu de `camera-controls`), le moteur de
dialogue (au lieu d'`ink`), les agendas des visiteuses (au lieu de `Yuka`), le
calcul du soleil (formules de Meeus, comme SunCalc). Chacun tient en une
centaine de lignes et fait exactement ce dont le salon a besoin.

## Ce qui viendra, par vague

| Brique | Licence | ★ | Dernier travail | Quand, et pour quoi |
|---|---|---|---|---|
| **pmndrs/postprocessing** | Zlib | 3,0 k | 2026-11 | vague 5 : un rendu plus cinéma que le halo de base |
| **three-mesh-bvh** | MIT | 3,6 k | 2026-11 | vague 2 : toucher précisément un décor dense |
| **three-gpu-pathtracer** | MIT | 2,0 k | 2026-11 | vague 2 : **précalculer la lumière** du salon dans un navigateur, en secours de Blender |
| **recast-navigation-js** | MIT | 0,4 k | 2026-10 | si l'on veut marcher librement (hors des points) : le maillage de navigation |
| **Yuka** | MIT | 1,5 k | 2026-10 | si les agendas des PNJ deviennent riches (objectifs, perception) |
| **ink + inkjs** | MIT | 5,0 k + 0,7 k | 2026-11 | quand les dialogues grossiront : **un langage que Mongazi pourra éditer** |
| **three-geospatial** (takram) | MIT | 1,8 k | 2026-05 | vague 6 : un vrai ciel physique et des nuages volumétriques dehors |
| **glTF-Transform + meshoptimizer** | MIT | 2,1 k + 8,8 k | 2026-10 | vagues 2 à 4 : compresser chaque modèle pour la 3G |
| **blender-mcp** | MIT | 34 k | 2026-11 | vague 2 : Claude pilote Blender (dans Colab, pas sur ce PC) |
| **MPFB2** (MakeHuman pour Blender) | à relire (code GPL, ressources MakeHuman CC0) | 0,7 k | 2026-10 | vague 3 : une base de personnage **réaliste et gratuite**, à habiller avec la planche d'Hillary |
| **Rhubarb Lip Sync** | MIT selon son fichier, à relire | 2,8 k | 2026-06 | vague 3 : **les lèvres d'Hillary bougent sur sa vraie voix** |
| **Chatterbox** (Resemble) | MIT | 27,8 k | 2026-11 | vague 3 : des voix pour les visiteuses (déjà retenu pour NEBULA VOIX) |
| **TRELLIS / TRELLIS.2** (Microsoft) | MIT (code) · **poids à vérifier** | 14 k / 12,8 k | 2026-10 / 07 | vague 4 : photo vers 3D, en local sur Colab, en secours de WaveSpeed |
| **TripoSR** | MIT | 7,4 k | 2026-06 | idem, plus léger |
| **three-vrm** (pixiv) | MIT | 2,3 k | 2026-10 | si un jour on accepte des avatars de visiteurs au format VRM |
| **AI Town** (a16z) | MIT | 10,8 k | 2026-11 | **la référence** pour l'IA plus tard : une ville où des personnages IA vivent, se souviennent et se parlent |
| **Generative Agents** (Stanford) | Apache-2.0 | 22 k | 2024-08 | la recherche derrière AI Town : mémoire, réflexion, planning des personnages |
| **Colyseus** | MIT | 7,5 k | 2026-11 | étage 2 : **voir les autres visiteurs** dans le monde (multijoueur) |
| **MapLibre GL JS** | BSD-3 selon son fichier, à relire | 12 k | 2026-11 | étage 2 : **la carte de Cotonou en 3D** (immeubles d'OpenStreetMap), d'où l'on entre dans chaque lieu |
| **Spark** (World Labs) | MIT | 3,9 k | 2026-10 | plus tard : des décors « photo 3D » (splats) ; ⚠️ leur lumière est figée, donc pas de jour/nuit |

## Ce qu'on écarte, et pourquoi

| Brique | Pourquoi non |
|---|---|
| **chongdashu/unreal-mcp** | ⛔ **aucune licence** déclarée : tous droits réservés. Pour piloter Unreal, la voie est **le MCP officiel d'Epic** (Unreal 5.8 et plus, expérimental) |
| **Hyperfy** (mondes 3D sur le web) | GPL-3.0 : le code envoyé au navigateur nous obligerait à ouvrir le nôtre. **À lire pour les idées**, pas à intégrer |
| **Hubs** (Mozilla, repris par une fondation) | MPL-2.0, viable, mais bâti sur A-Frame et pensé pour la réalité virtuelle : trop lourd pour la 3G |
| **Piper** (voix) | ⛔ archivé ; sa suite est en GPL |
| **GaussianSplats3D** | dernier travail en 2025 ; Spark l'a dépassé |
| **Ready Player Me** | fermé le 31 janvier 2026 |
| **MetaHuman** | création dans Unreal seulement, trop lourd pour un téléphone, licence hors Unreal floue |
