# 2026-08-14 · Le studio vidéo NEBULA (Remotion) — installation, licence, rangement

Mongazi a lancé `npm i --save-exact remotion@4.0.512 @remotion/cli@4.0.512`, puis
a demandé de « faire ce qu'il faut pour chaque situation » sur les deux réserves
soulevées : la **licence** et **l'endroit** où l'installation atterrissait.

---

## 1. Ce qui a été installé

`remotion` et `@remotion/cli` **4.0.512**, avec `@remotion/renderer`,
`@remotion/bundler`, `@remotion/player`, le compositeur Windows
(`compositor-win32-x64-msvc`, ffmpeg inclus), `react` / `react-dom` 19.2.8 et
`zod` 4.4.3 en dépendances. 245 paquets, 8 minutes.

Ajouté ensuite en dépendances de développement : `typescript` 7.0.2,
`@types/react` 19.2.18, `@types/react-dom` 19.2.4.

## 2. La licence, vérifiée et non supposée

Lue **dans `node_modules/remotion/LICENSE.md`**, donc la licence de la version
réellement installée, et recoupée avec la FAQ officielle
(`remotion.dev/docs/license/faq`, `remotion.pro/faq` y redirige).

- Gratuit pour : un particulier, **une société à but lucratif de 3 employés au
  plus**, une association, ou quelqu'un qui évalue l'outil.
- **L'usage commercial est autorisé** sous licence gratuite : *« Any commercial
  use case is allowed as long as you are not selling Remotion as a product
  itself. »* La FAQ traite explicitement le cas de l'agence : *« If your agency
  has 3 or fewer personnel, the Free License covers this work; if it has 4 or
  more, your agency needs a Company License. »*
- ⚠️ **Le piège pour NEBULA** : si le **client** devient propriétaire du projet
  Remotion, la FAQ **additionne les effectifs des deux sociétés** et la licence
  est à la charge de celui qui détient la propriété intellectuelle. Conclusion
  de travail : **on livre le MP4, jamais le projet**.
- ⚠️ **La licence change en 5.0** (télémétrie obligatoire pour le modèle
  « Automators »). Le `--save-exact` de Mongazi nous protège : rien ne bouge tant
  qu'on ne fait pas `npm update`, et on relit la licence avant de monter.
- Interdit dans tous les cas : revendre, relouer ou sous-licencier un dérivé de
  Remotion. Vendre une vidéo faite avec Remotion, oui ; vendre Remotion habillé
  en produit NEBULA, non.

**Aujourd'hui, NEBULA est éligible à la licence gratuite.** À revoir le jour où
l'agence emploie une quatrième personne (les partenaires commerciaux ne sont pas
des salariés).

## 3. Le rangement

L'installation avait créé un `package.json` **à la racine du dépôt**, qui n'en
avait pas : la racine devenait un projet Node. Tout a été déplacé dans
**`_studio-video/`** (`package.json`, `package-lock.json`, `node_modules`
déplacés, pas réinstallés).

Effet de bord constaté : le `npm i` initial a **vidé `node_modules/@puppeteer`**
qui traînait à la racine (npm élague ce qui n'est pas dans le `package.json`).
Sans conséquence, la génération d'affiches passe par SVG → sharp → PDF, pas par
puppeteer.

## 4. Ce que contient `_studio-video/`

Un projet Remotion qui rend **les trois séries « oui / non »** de
`_documents/nebula-agency/marketing/TIKTOK-OUI-NON.md`, en 1080x1920 à 30 i/s :

| Composition | Contenu | Durée |
|---|---|---|
| `oui-non-1-prix` | 9 questions | 25,5 s |
| `oui-non-2-besoin` | 8 questions | 23 s |
| `oui-non-3-logiciel` | 8 questions | 23 s |

- Rythme repris du document : question **1,5 s**, réponse **1 s**, carte finale
  **3 s**, **coupe sèche** (aucune transition, c'est le format).
- **Les cartes ne sont pas redessinées** : les PNG de `_cartes.py` sont importés
  tels quels. Une question change → `python _cartes.py`, jamais de retouche.
- **Les plans filmés n'existent pas encore.** Chaque question porte un champ
  `plan: null` ; tant qu'il est nul, la réponse s'affiche en grosses lettres sur
  fond noir et **la vidéo se rend quand même**. Les fichiers se posent dans
  `public/visages/` (hors dépôt : le dépôt est public et ces fichiers sont
  lourds).
- `out/` et `public/` sont ignorés par git, sauf `public/LISEZ-MOI.md`.

Commandes : `npm run studio`, `npm run rendu`, `npm run verifier`.

## 5. Contrôles

- `npm run verifier` (`tsc`) : **0 erreur**.
- **Rendu réel de `oui-non-3-logiciel` : sorti.** `ffprobe` (celui livré avec
  Remotion) : H.264, **1080x1920**, **30 i/s**, **690 images**, **23,06 s**,
  1,45 Mo, plus une piste audio muette. 690 = 8 x 75 + 90, exactement la durée
  calculée.
- Trois images regardées, pas seulement des chiffres verts : la carte de la
  question 1, la réponse à 2 s (**OUI**, conforme au script 3) et la carte
  finale à 21 s.

### ⚠️ Le rendu échoue avec les réglages par défaut

Deux échecs avant le bon, et la cause n'est pas le code :

1. `Timed out after 25000 ms while trying to connect to the browser`, avec un
   journal Chrome **vide**. C'était le tout premier lancement, juste après le
   téléchargement des 113 Mo de Chrome : Defender scannait. Relancer suffit.
2. `Timed out after 30000ms while setting up the headless browser`. Même cause,
   étape suivante.

Remède posé dans `remotion.config.ts`, à **garder** :
`Config.setDelayRenderTimeoutInMilliseconds(120000)` et
`Config.setChromiumOpenGlRenderer('angle')`. La page, elle, se charge en 4 s une
fois le navigateur debout : ce n'était pas la performance du montage.

⚠️ Diagnostic utile : lancer `chrome-headless-shell.exe --version` puis
interroger `http://127.0.0.1:PORT/json/version` prouve en dix secondes que le
navigateur n'est pas en cause. Et `ffmpeg` sans `-nostdin` **reste bloqué** dans
un terminal non interactif.

## 6. Un défaut vu sur la carte finale

`z-fin.png` coupe « NEBULA Agency · Cotonou » en deux lignes, et le point médian
se retrouve **en tête de la deuxième ligne** : « NEBULA Agency » / « · Cotonou ».
Ça vient de `_cartes.py` (retour à la ligne par mots), pas du montage. À
corriger dans le générateur de cartes, pas dans l'image.

---

## Ce qui reste

- Tourner les plans « oui » et « non » (six de chaque d'un coup, comme le dit le
  document), les poser dans `public/visages/`, renseigner `plan:` dans
  `src/scripts.ts`.
- Choisir la musique, et vérifier les droits : un son ajouté **depuis
  l'application TikTok** est couvert par leur catalogue, un fichier collé au
  montage ne l'est pas.
- La vague 2 des scripts (`TIKTOK-OUI-NON-2.md`, registre sérieux) n'a pas
  encore ses cartes ni sa composition.
