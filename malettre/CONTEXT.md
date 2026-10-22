<!-- HISTOIRE DU NOM -->
# MA LETTRE À… · la lettre digitale (ex-MINUIT, ex-LE PLI)

> Le récit complet du produit. `CLAUDE.md` n'en garde qu'un résumé (règle du
> 2026-09-16 : une ligne de produit y est un résumé, le récit vit ici).
> Le mode d'emploi technique est dans `README.md`, la caisse dans
> `PAIEMENT.md`, les règles de publication et de retrait dans `CONDITIONS.md`.

## Le nom (2026-10-16)

**MA LETTRE À…**. Mongazi : « ma lettre j'aime bien », puis le nom qui se
termine par le prénom de la personne (« Ma lettre à Afi », « Ma lettre à
papa », « Ma lettre à la famille Dossou »). Il remplace **LE PLI** (2026-09-09),
qui avait lui-même remplacé **MINUIT** : « LE PLI c'est un peu bizarre, on doit
comprendre dès qu'on le lit ou qu'on le dit ».
- `lepli/` → **`malettre/`**, schéma `malettre`, fonctions `malettre-*`, clés
  `malettre:*`, marqueur `MALETTRE_DONNEES` (commit `5af692d`).
- ⛔ Les documents datés gardent l'ancien nom (`_plans/`, journaux,
  conversations, leçons) ; la composition vidéo `lepli-demo` aussi, elle sera
  refaite avec la vidéo publicitaire.
- Adresse prévue : **`malettre.nebula-agency.online`** (sous-domaine gratuit).
  `malettre.com` est pris ; `malettre.app`, `.online`, `.bj`, `.ci`
  semblaient libres le 2026-10-16 (le lien `malettre.app/a/afi` se lirait
  « ma lettre à Afi ») : achat à décider par Mongazi.

<!-- FIN HISTOIRE -->

## La page d'accueil (2026-10-16)

`_accueil_src.html` → `python malettre/_build_accueil.py` → `index.html` +
`exemples/*.html` (jamais édités à la main). **La phrase** : *une lettre, c'est
une feuille qui devient une enveloppe scellée, puis qui redevient une feuille
entre les mains de quelqu'un.* **L'objet** : la feuille et son cachet de cire.
- **Le chargement** (demandé par Mongazi) : une lettre nouée d'un ruban de
  satin, le nœud se défait, le rabat se lève, « Ma lettre à toi » paraît,
  « by NEBULA Agency » en dessous. Retiré seul à 3 s, filet à 4,5 s, un toucher
  le passe, absent sans JavaScript.
- **Héros** : « Ma lettre à… » où la plume tape *Afi, papa, Zara, maman,
  Grâce* ; le visiteur tape SON prénom, il part à `creer.html?pour=…`.
- **La scène 3D épinglée** (720 vh, CSS 3D, une seule boucle rAF) : la feuille
  s'écrit, se plie en trois, entre dans l'enveloppe, le cachet tombe et
  s'imprime, dort à 23:57, s'allume à minuit, se brise, la lettre revient.
- **Six exemples** écrits par la vraie plume, personnes inventées et dites
  telles, aucune photo de visage, aucun balisage d'avis ; chacun ouvre la
  VRAIE lettre (`_injecter.poser()`) dans un téléphone.
- **La plume** (fiche qui se coche, lettre qui s'écrit) · **le casier** des
  27 occasions · **le seuil** (une vraie lettre qui s'ouvre 40 s plus tard) ·
  **les timbres** (prix LUS dans `creer.html`, jamais recopiés) · **les
  promesses** · **la fin** (la page blanche qui attend un prénom).
- **Le retrait** : lien WhatsApp au pied, `wa.me/22996740732` (le numéro déjà
  utilisé par `merci.html` et PISTE), comme le prévoit `CONDITIONS.md`.
- Image de partage `og.jpg` (`python malettre/_og.py`, aucune personne).
- **Contrôle** `python malettre/_qc_accueil.py` : **78 verts** (livrable à
  jour, prix égaux au constructeur, prénom transmis, exemples, chargement,
  débordement, CLS, cibles 44 px, contraste sur les pixels avec deux témoins,
  mouvement réduit, sans JavaScript, poids du premier écran). Mesure : la scène
  tient 60 images/s en médiane, processeur ×4.
- **Captures** `python malettre/_voir_accueil.py` → `_vues/accueil/`.
- **Publication prête, pas faite** : `python malettre/_dist.py` (16 fichiers,
  433 Ko, garde anti-fuite) puis `wrangler pages deploy malettre/_dist
  --project-name malettre --branch main` **avec le feu vert de Mongazi**, et
  seulement quand la caisse est branchée (la page vend des lettres payantes).
  ⚠️ La route `/l/<jeton>` arrivera avec la caisse : `_dist` devra la porter.

### Trois défauts trouvés le 2026-10-16, après la coupure du PC

1. ⛔ **Au téléphone, la page était dézoomée** : l'`input` du prénom (Pinyon
   30 px, `size` 20 par défaut) gardait ~440 px de large et poussait la page à
   **597 px**, puis les timbres agrandis avant leur frappe (`scale(1.25)`) à
   414 px. Le contrôle comparait `scrollWidth` à `innerWidth`, qui GRANDIT
   avec le défaut : il passait au vert. Corrigé (`width:0` + `flex:1` sur
   l'input, `overflow-x:clip` sur `#prix`), et le contrôle compare désormais
   à la largeur demandée.
2. ⛔ **En mouvement réduit, billets et timbres restaient invisibles** jusqu'au
   défilement : le repli `.js [data-rv]:not(.vu)` perdait contre leurs règles
   plus spécifiques.
3. ⚠️ **Deux sondes menteuses** : la capture « nœud noué » d'avant la coupure
   montrait un nœud déjà défait (`clock.install()` laisse couler le temps) ;
   la sonde de contraste mesurait le fond une section à côté au téléphone (la
   capture d'élément refait défiler). Témoins ajoutés.

## Décisions du 2026-10-16 au soir (le dossier `_partage/ma lettre`, et la suite)

Mongazi a déposé 11 vidéos, 6 images et un modèle 3D dans `_partage/ma lettre/` pour « tout » :
vitrine, création, rendu, pub. Ce sont surtout des **faire-part de mariage concurrents**
(mayainvite, @convite_sofisticado, invitelytr, un studio Canva, @es_wedding), avec leurs
filigranes et de vrais couples, plus 3 clips IA d'enveloppe d'auteur inconnu.
- **Le dossier sert de RÉFÉRENCES uniquement** : on reproduit leurs idées dans notre code et nos
  images, rien de leur contenu n'est publié ni commité.
- **La voix off** : Mongazi l'enregistre sur ElevenLabs (Alimata) à partir de notre texte. Rien
  n'est généré (WaveSpeed 0,04 $, Higgsfield 0 crédit).
- **L'ouverture spectaculaire (3D, vibration, son) est pour tout le monde**, l'habillage (cire,
  sceau, papier, pluie, phrase à gratter) pour les offres payantes, **sans changer les prix**.
- **Le son** : activé, discret, avec un bouton pour le couper.
- **« Lui répondre sur WhatsApp »** : si l'acheteur coche la case (décochée par défaut), toutes
  les offres. **Aucun avis d'ouverture** : on garde « aucune mesure d'audience ».
- **Le faire-part de mariage** : « des gens peuvent se marier à tout moment ». **Sur demande
  tout de suite** (fait par NEBULA) et **en libre-service ensuite**, **25 000 F**, les invités
  répondent **par WhatsApp aux mariés** (aucun serveur).
- **L'adresse** : `malettre.nebula-agency.online`.
- **La pub** : TikTok, Facebook et Instagram, statuts WhatsApp (deux fois 15 s), YouTube
  Shorts.
- **Le français ET l'anglais sur tout le parcours** (vitrine, constructeur, lettre, plume,
  exemples, pub), **dans chaque vague**.
- **Vendre dès que possible.**
- Le plan en vagues (0 : les deux langues · 1 : le rendu pour tous · 2 : l'habillage payant et
  la réponse · 3 : la vitrine · 4 : le faire-part sur demande · 5 : la pub) est dans
  `~/.claude/plans/dynamic-conjuring-piglet.md`, et repris ici au fil des vagues.

## Vague 0 · les deux langues (faite le 2026-10-16 au soir)

- La lettre, la caisse, la plume, le constructeur, le paiement, le merci et
  l'accueil existent en anglais (`/en/`). Le français reste la source ;
  `i18n/en.txt` est le dictionnaire, `_traduire.py` refuse d'écrire s'il manque
  une phrase. Détail technique : `README.md` § « Les deux langues ».
- Six exemples anglais écrits par la vraie plume anglaise (`exemples.en.json`),
  mêmes personnes inventées ; Ismaël écrit depuis Londres.
- **Trouvé en essayant pour de vrai** : la plume anglaise titrait en français
  (2 lettres sur 6) → système renforcé ET relecture qui refuse (`'langue'`).
- Contrôles : caisse 269, lettre 212, anglais 51, accueil (FR + EN).
- Image de partage anglaise `og-en.jpg`, 404 bilingue, `_dist` à 27 fichiers.

## Vague 1 · le rendu pour tous (2026-10-16, commit `c8cf9f4`)

- L'enveloppe du seuil en **vraie 3D** (dos, carte, poche, rabat à deux faces) : on
  touche le cachet, il casse en deux le long de sa fêlure, le rabat se lève, la carte
  sort, la lettre se déplie (1 150 ms).
- **Vibration** au toucher (jamais en mouvement réduit) et **son** de la cire et du
  papier synthétisés en Web Audio (aucun fichier), discrets, coupables d'un bouton,
  le choix gardé sur l'appareil.
- **Grand compte à rebours** (jours, heures, minutes, secondes) sur le seuil.
- Trouvé : en anglais, le seuil d'une lettre prête disait « Une lettre t'attend. ».

## Vague 2 · l'habillage payant et « Répondre » (2026-10-16, commit `efa8381`)

- **L'habillage, réservé aux offres payantes, sans changer les prix** : 5 cires, 4
  sceaux (initiale, cœur, colombe, couronne), 4 papiers (crème, coton ivoire en relief
  SVG, kraft, nuit), une pluie à l'ouverture (pétales, confettis, étoiles d'or), et
  une **phrase à gratter** sous une pellicule d'or (au doigt, ou « Révéler sans
  gratter »).
- Le serveur retire l'habillage d'une lettre gratuite comme il fixe le prix ; trois
  copies des listes (serveur, constructeur, gabarit), comparées par un contrôle.
- **« Répondre à Kofi sur WhatsApp »** si l'acheteur coche la case (décochée par
  défaut) ; l'indicatif part à part, le serveur compose le numéro (le `01` gardé).

## Vague 3 · la vitrine (2026-10-16)

- **« Ouvre-la toi-même »** (le seuil) : la vraie lettre s'ouvre dans **10 s** (au
  lieu de 40), puis **trois rangées de pastilles** (cire, papier, pluie) la rhabillent
  en direct ; rhabillée, elle s'ouvre tout de suite et cache « Tu peux cacher une
  phrase ici. » sous l'or à gratter. Le téléphone et ses pastilles forment **un bloc**
  qui tient dans l'écran (390 × 844 et 1440 × 900) : on touche, la lettre change juste
  au-dessus du doigt. Le sceau reste au constructeur (une 4e rangée ne tenait plus).
  Pastilles LUES dans `HABILLAGE` de `creer.html` (noms anglais dans `en/creer.html`).
- **Les six exemples habillés**, chacun autrement (`habillage` dans `exemples.json` et
  `exemples.en.json`), deux avec une phrase à gratter (Afi : « Ton billet de retour
  est déjà payé. », Grâce : « Ta calculatrice est toujours chez moi. »). Le cachet de
  chaque carte prend la cire de sa lettre (tons LUS dans `lettre.html`).
- **La prochaine grande date**, calculée au chargement sur les occasions datées
  (`jour`) : « Prochaine grande date : Noël, dans 70 jours. Écris-la maintenant, elle
  attendra. » Jamais une fausse rareté.
- **Le faire-part de mariage, sur demande** : un bloc nuit dans les occasions (lien
  « Faire-part » dans la barre), un carton d'exemple (Kossi & Afiwa, couple inventé et
  dit tel), **25 000 F lus dans `faire-part/offre.json`** (seule source du prix et du
  numéro), bouton vers le WhatsApp de NEBULA avec un message prêt.
- **Une FAQ de 8 questions** (section « Les questions », entre les promesses et la
  fin) : chaque réponse tient debout seule, ne dit que ce que la page dit ; la réponse
  du prix est **écrite depuis le catalogue** et le build **vérifie** avant de l'écrire
  que chaque offre payante dure un an, sans signature, avec l'habillage. Le `FAQPage`
  du `<head>` est **lu dans les questions visibles**. « Une autre question ? Écris-nous
  sur WhatsApp ».
- **`llms.txt`** (FR + EN), fabriqué par le build : offres et prix du catalogue, plume,
  faire-part, les 8 questions et leurs réponses, les pages. Dans `_dist` (28 fichiers).
- **Les timbres disent ce que chaque offre débloque** (« + l'habillage au choix »), et
  le texte du prix dit que l'ouverture est la même pour tous.
- ⛔ **La barre d'action en bas au téléphone n'est PAS faite, exprès** : la barre du
  haut porte déjà « Écrire ma lettre » en permanence, et le plan la voulait « masquée
  quand un autre bouton d'écriture est visible » : elle ne se serait jamais montrée.
  Un deuxième fixe aurait mangé 60 px d'un écran de 844 pour rien.
- Trouvé en route : le surtitre du faire-part héritait du **bordeaux des sections
  claires sur le fond nuit du bloc** (2,3:1, attrapé par la sonde sur les pixels) ·
  le cachet « K & A » en **grille** empilait K, & et A (trois cases) · l'esperluette du
  script se lisait comme un trait (→ italique Caslon) · le bouton du faire-part était
  sombre sur sombre · le contrôle des langues prenait les clés `avant` et `dans` du
  script anglais pour du français (→ clés neutres) · le contrôle de caisse virait au
  rouge sans `PYTHONIOENCODING` (console cp1252) : il le pose lui-même désormais.
- Contrôles : accueil **235** (FR + EN), lettre 269, caisse 301, anglais 52.

## Vague 4 · le faire-part sur demande (2026-10-16 → 17)

- **Le gabarit** `faire-part/gabarit.html` reprend le moteur de la lettre : l'enveloppe
  3D, le cachet d'or **aux initiales du couple** qui se brise, le son, la vibration, la
  pluie de pétales. Puis le carton (familles, noms qui s'écrivent, date, heure, ville),
  **le compte jusqu'au jour J à l'heure du LIEU** (date + heure + fuseau : un mariage a
  lieu à une heure de Cotonou, pas à celle du téléphone), le mot des mariés, **le
  programme sur un fil d'or** avec « Voir sur la carte » (Google Maps), la tenue et ses
  couleurs, les photos (données, jamais des liens), et **la réponse** : prénom, nombre
  de personnes, « Je serai là » / « Je ne pourrai pas venir » vers **le WhatsApp des
  mariés**, message prêt. Le jour J : « C'est aujourd'hui ! » ; 36 h après : « Merci
  d'avoir été là », réponses fermées. FR et EN. 37 Ko sans photo.
- **Le générateur** `_faire_part.py` : valide toute la fiche (refuse et liste les
  fautes : numéro, date passée, lien de carte qui n'est pas Google Maps, photo absente),
  tire un **jeton de 16 caractères** gardé d'une version à l'autre, réduit les photos à
  1 200 px, écrit l'**empreinte** du jeton dans `faire-part/publies.txt`.
- ⛔ **Les vrais couples hors de git** (`faire-part/_couples/`, ignoré) : le dépôt est
  public et le jeton EST l'adresse. ⛔ **`_dist.py` refuse** si une page publiée manque
  sur le disque (un déploiement d'ailleurs l'effacerait).
- **L'exemple** (Kossi & Afiwa, couple inventé et dit tel, samedi 12 décembre 2026) :
  `faire-part/exemple.html` et `exemple-en.html`, ouverts depuis la vitrine par
  « Ouvrir l'exemple » (fenêtre téléphone), publiés par `_dist` (`/faire-part/exemple`).
  Ses réponses ne partent nulle part, elles expliquent.
- Contrôles : `_qc_faire_part.py` **83** (générateur, témoins de refus, `</script>` et
  U+2028, jeton et empreinte, garde de `_dist`, photo réduite ; dans le navigateur
  aucune requête réseau, ouverture, compte, cartes, réponses, jour J et lendemain,
  contraste sur les pixels avec témoin, langues, mouvement réduit) · accueil **239**.
- Trouvé en route : « Une invitation de » sans nom au seuil · l'heure qui se coupait
  (« 10 / H ») · la sonde du seuil lisait « KOSSI » (`innerText` applique le
  `text-transform`, deuxième fois le même jour) · le générateur effaçait les marqueurs
  de données (gardés désormais, la page se relit et se refabrique).

## 🟢 EN LIGNE DEPUIS LE 2026-10-21 · https://malettre.nebula-agency.online

Feu vert de Mongazi le 2026-10-21 (« tu as le feu vert pour mettre en ligne »). Tout le détail du
branchement est dans `PAIEMENT.md` § 4 ; le récit dans `_memoire/conversations/2026-10-21-malettre-mise-en-ligne.md`.

- **Base** (schéma `malettre`, 4 tables, RLS) · **4 fonctions** (commande et plume vérifiées par la clé
  publique, paiement-reçu et lettre sans vérification du jeton) · **webhook SasPay avec SON secret**
  (`MALETTRE_SECRET_WEBHOOK`) · **la plume** (clé Anthropic du Bureau) · **site** Pages `malettre` + domaine.
- ⛔ **Piège trouvé à la mise en ligne** : Supabase sert tout HTML en `text/plain` avec
  `default-src 'none'; sandbox` ; la lettre s'affichait en code source. Corrigé dans le relais (autorisé par
  Mongazi), et la caisse imite désormais la vraie réponse de Supabase (**379** contrôles).
- **Essayé en ligne, puis effacé** : lettre offerte créée, ouverte, retirée · commande à 5 000 F jusqu'à
  SasPay puis annulée · webhook signé / faux / vieux · une lettre de la plume.
- ⏳ **Le premier franc réel** (Mongazi) : le plus petit est l'offre gratuite + la plume, **500 F**. Puis
  lire `malettre.paiement_evenement` : c'est le seul essai qui prouve le dernier maillon.
- **Publier une modification** : `python malettre/_dist.py` puis `wrangler pages deploy malettre/_dist
  --project-name malettre --branch main` ; une fonction : `npx -y supabase@2 functions deploy <nom>
  --project-ref xukduhqqfzogisoimhyo --use-api` (et `python malettre/_gabarit_ts.py` avant `malettre-lettre`
  si `lettre.html` a bougé).

## La vitrine en profondeur (2026-10-21, « effet WOW à 200 % »)

- **GSAP 3.13.0 + ScrollTrigger**, servis d'ici (`vendor/`, `?v=3.13.0`), chargés **après le premier écran**,
  jamais en mouvement réduit ; sans eux rien ne manque. Une animation de profondeur par zone, tirée de la
  lettre (détail : `_memoire/conversations/2026-10-21-malettre-vitrine-profondeur.md` et l'en-tête de
  `_accueil_src.html`).
- **La nuit des lettres** (`#nuit-lettres`, entre la plume et les occasions) : une enveloppe par occasion
  RÉELLE (le build les lit dans `creer.html`), la caméra les traverse, la tienne arrive au prénom tapé.
- **Les fonds** : `python malettre/_fonds.py` (sources `_partage/ma lettre/fonds/<zone>-paysage|portrait.*`)
  puis `_build_accueil.py`. Une zone n'a d'emplacement que si son image existe ; chargement à l'approche ;
  celui du héros attend le rideau ET la fin du chargement (premier écran < 320 Ko). Les **sept zones** ont
  leur image (Mongazi, 2026-10-21). Elles **vivent en CSS** (travelling, flamme, pluie, eau, fumée, cachet,
  lumière), en pause hors de l'écran, ⏳ en attendant ses vraies vidéos (`_partage/ma lettre/videos/`).
- **La musique** : `python malettre/_son.py "<mp3>" "<auteur>"` puis rebuild ; le bouton paraît seul, le
  crédit va au pied. Morceau : Alex Morgan (Pixabay), égalisé à -16 LUFS, 2,1 Mo. ⛔ **Le MP3 n'est pas dans
  le dépôt** (public, licence Pixabay) : il ne vit que sur ce PC et sur le site.
- **Le logo** : `python malettre/_logo.py` → `logo/cachet.svg`, `cachet-brise.svg`, `favicon.svg` (le cachet
  aux trois points ; la fissure passe ENTRE deux points). Onglet et cachet de la barre. ⏳ Le nom à côté, `og.jpg`.
- **La barre d'achat** au téléphone (bande de bord opaque).
- Contrôles : accueil (nouveaux : GSAP d'ici et hors du premier écran, nuit, volets, barre d'achat, fonds),
  la sonde de contraste lit l'opacité VUE et laisse l'inertie finir.

## ✅ LES QUATRE DEMANDES DE MONGAZI, FAITES (2026-10-21, la nuit)

*« oui commence et enchaîne un à un, invoque tous les skills qui te seront utiles pour tous les réaliser à 100 % »*.
Récit complet : `_memoire/conversations/2026-10-21-malettre-quatre-demandes.md`. Skills : `impeccable` (sa fiche
`malettre/PRODUCT.md`), `redesign-existing-projects`, `design-taste-frontend`, `high-end-visual-design`, `ui-ux-pro-max`.

1. **La police et tout ce qui « fait IA »** : texte courant en **Commissioner, axe « flair » à 100** (la lignée
   d'Optima, choisie sur planche contre Proza Libre, Alegreya Sans, Rosario) ; **plus aucun surtitre en capitales
   espacées** (celui du héros devient « Cotonou, le … », la date du jour) ; la formule « ligne droite + ligne italique
   colorée » gardée dans UNE section, et la plume dit « Elle écrit. » à la main ; petits libellés en italique Caslon ;
   gris réchauffé ; **typographie française du texte visible par le build** (apostrophe ’, espace insécable devant
   ; : ! ? et dans « »). ⚠️ Pas l'espace fine U+202F : ces polices ne la dessinent pas. Animations intactes.
2. **Les bruitages et le casier** : clic de papier au survol, clic au toucher, cachet frappé et papier qui glisse au
   casier (Web Audio, aucun fichier, jamais avant un geste, muets si le son est coupé). **Le module vit dans
   `creer.html` (`/*__BRUITS__*/`), la vitrine le lit au build.** 28 **emblèmes** gravés dans les cachets
   (`EMBLEMES` de `creer.html`, seule source). Le casier : une consigne explicite, des noms qui ne se coupent plus,
   **une étagère qu'on fait glisser par famille au téléphone**, la lettre qui sort de sa case au toucher. L'étape
   « Pour quelle occasion ? » du constructeur a les mêmes cachets, le même son, la même frappe.
   ⛔ **Trouvé en ligne : les timbres fantômes** (décor 3D invisible qui prenait le doigt sur presque toute la page :
   au téléphone, toucher une case ne faisait rien). Corrigé, et contrôlé sur une page NEUVE, avec témoin.
3. **Le verre partout** : verre FUMÉ et GIVRÉ sur la nuit (aucun flou recalculé : les fonds bougent derrière, règle
   du dépôt), verre clair sur le papier (questions, consigne, paiement), **bouton principal en verre liquide plein**,
   bandes de bord en verre teinté **plein**, **vrai flou** derrière la fenêtre des exemples (la page dort,
   `html.voile`). Le papier reste du papier (lettres, enveloppes, timbres, billets).
4. **La soirée entre potes** : occasion `potes` (famille « La famille et les amis ») : **« Soirée entre potes » ·
   « Un chill privé, sur invitation »**, titre « Tu es de la fête », formule « On t'attend, » ; questions « Tu
   organises », « Chacun apporte », un ton à elle (dont « Mystérieux ») ; l'aide des consignes demande le lieu et
   l'heure. **La plume ne les invente jamais** (registre + savoir-faire, essayé au banc : avec lieu et heure, elle
   les reprend ; sans, « les détails arrivent en message »). Anglais : « Night with friends ». `malettre-plume`
   republiée. ✅ **Nom confirmé par Mongazi le 2026-10-21.**

**La page livrée n'a plus ses commentaires** (`alleger()` du build) : ils pesaient 23 Ko sur 178, et le premier écran
dépassait ses 320 Ko (321). La source les garde tous. ⚠️ **Pour comprendre un morceau de la vitrine, lire
`_accueil_src.html`, jamais `index.html`.** Contrôles de la nuit : accueil, langues, constructeur, caisse, faire-part
(chiffres dans le récit de la nuit).

## 🎵 LA MUSIQUE AU PREMIER CONTACT (2026-10-22)

Mongazi : « la musique doit se déclencher au simple toucher ; même moi, sur une vitrine, je défile d'un seul
geste ». ⛔ **Aucun navigateur de téléphone ne laisse jouer un son pendant un défilement** (règle de Chrome et de
Safari, incontournable). D'où **la lettre du chargement qui ATTEND le premier contact** : tant qu'elle est là,
la page ne défile pas (`touch-action:none`, `html.rideau`), donc le premier geste, même un glissement, est un
vrai toucher : il ouvre la lettre ET lance la musique (volume 0,15), avec un bruit de papier. « Touche l'écran
pour l'ouvrir » (« Clique pour l'ouvrir » sur ordinateur) paraît à 2,4 s ; la molette l'ouvre (sans le son) ;
**filet : elle s'ouvre seule à 12 s**. Mouvement réduit : aucune attente, elle part à 0,25 s.
⚠️ **Les contrôles ordinaires ne voient pas le son** (Playwright lance Chromium sans la règle de lecture, et ses
`evaluate` comptent comme un geste) : `_qc_accueil.py` § « la musique au premier contact » remet la règle, touche
par le protocole et lit sans geste, avec un témoin. Voir `_memoire/lecons.md` (2026-10-22).

## ⏳ LES PRIX, REVUS EN PROFONDEUR (2026-10-22) : PROPOSITION, EN ATTENTE DE MONGAZI

Demande : « réfléchis en profondeur et revois le prix, à la hausse ou à la baisse ». Skills : `pricing-strategy`,
`marketing-psychology`. Rien n'est changé dans la caisse tant que Mongazi n'a pas dit oui.

- **Le constat** : aucune lettre, aucun paiement en base au 2026-10-21. Le goulot est la venue des visiteurs, pas le
  prix : baisser n'apporte personne. 2 000 F (environ 3 €) est déjà un prix d'impulsion.
- **Le défaut de la grille** : La Lettre (5 000 F) = Le Mot (2 000 F) + un code secret. +3 000 F pour quatre
  chiffres : le palier conseillé (présélectionné) ne se défend pas. Et la plume à +500 F sur tout casse les totaux
  ronds (5 500, 10 500 F) dans un pays qui paie en billets de 5 000 et 10 000.
- **La proposition** : Offert 0 F et Le Mot 2 000 F inchangés ; **La Lettre 5 000 F, plume incluse, 10 photos,
  code secret** (« notre conseil ») ; **Le Coffret 10 000 F, plume incluse, 20 photos** ; la plume reste à 500 F
  avec Offert et Le Mot (c'est le premier franc) ; **le faire-part passe de 25 000 à 35 000 F** (le marché d'un
  sur-mesure) ; **l'équivalent en euros affiché** pour la diaspora (décidé à l'arrêté 08, jamais fait).
- **Repères** (recherches du 2026-10-22) : invitations digitales en Côte d'Ivoire, Carte Event de 7 500 à 30 000 F
  en libre-service, monmariage.net 35 000 F (promo 25 000) ; faire-part imprimé 500 à 800 F l'unité, 50 au moins ;
  bouquet de roses environ 10 000 F, 15 000 à 20 000 F autour du 14 février (Sénégal) ; pages d'amour en libre-service
  à l'étranger 9,99 à 12 $ (dossier du 27/08) ; frais Mobile Money marchand réels 2,3 à 3,5 % (estimations), ceux de
  SasPay toujours inconnus.
- **Ce qu'on ne fait pas** : aucun « le plus choisi » (aucune vente), aucune fausse urgence, aucun prix en 4 990 F
  (le franc se compte en billets ronds), aucun prix par occasion (arrêté 07), aucune durée « à vie » (la lettre expire,
  `CONDITIONS.md`).
- **Ce qu'on mesure ensuite** (après 30 à 50 lettres payées) : la part de chaque palier ; si La Lettre reste sous 25 %,
  on revoit son contenu ; si plus de la moitié des Le Mot prennent la plume, on essaie la plume à 1 000 F.

## Reprendre ici (2026-10-21, avant la mise en ligne)

Le point de reprise du 2026-10-17 (sept étapes) est **fait**, sauf ce qui attend Mongazi :

1. ✅ **Le code secret n'appartient qu'à La Lettre et au Coffret** : droit `code` dans les deux
   `PALIERS` (`creer.html`, `_shared/lettre.ts`), comparés par la caisse (section 20). Commit `beed2ed`.
2. ✅ **« Retirer cette lettre »** dans le pied de `lettre.html` : visible seulement sur une lettre
   servie à `/l/<jeton>` (22 signes du bon alphabet), deux temps (Oui / Non), `POST …/retrait`, puis la
   page du serveur ; repli WhatsApp `22996740732`. Contrôlé par `_qc.py` (« Retirer cette lettre »).
   ⚠️ **La lettre pèse 61 372 octets pour un seuil de 61 440 : il reste 68 octets.** Le moindre
   ajout à `lettre.html` passe par une économie ailleurs (les textes anglais du retrait vivent déjà
   dans un objet `RX` compact pour cette raison).
3. ✅ **Le relais `/l/*`** : `malettre/_relais.js`, copié en `_dist/_worker.js` par `_dist.py`.
   `/l/<jeton>`, `/retrait`, `/etat` vont à `malettre-lettre`, le reste aux fichiers ; il pose
   lui-même les en-têtes de sécurité (en mode avancé, `_headers` ne s'applique plus). Caisse section 21.
4. ✅ **Le ménage** : `malettre/_menage.py` + `.github/workflows/malettre-menage.yml`, chaque nuit
   03 h 30 UTC, secret `MALETTRE_DATABASE_URL` ou `PISTE_DATABASE_URL`. Avant le branchement, il le
   dit et sort sans erreur (essayé).
5. ✅ **`PAIEMENT.md`** : relais, ménage, règle du code, étape 6 (publier), nombres du jour.
6. ✅ **Les critères d'arrêt** sont recopiés ci-dessous, avec le conflit de calendrier à trancher.
7. 🟡 **La pub (vague 5)** : **les images sont faites**, la voix non. Six compositions
   `malettre-*` dans `_studio-video/` (30 s FR/EN, 2 × 15 s par langue), le vrai constructeur
   photographié par `_outils/malettre_captures.py`, planches regardées en FR et EN. Il manque **les six
   MP3** de Mongazi (`_studio-video/src/malettre/VOIX.md`) ; ensuite caler `minutage.ts` sur la voix
   et rendre à UN onglet. Détail : `_studio-video/README.md`.

**Contrôles au 2026-10-21, tous verts** : `_qc.py` **285** · caisse **373** · accueil **239** ·
langues **52** · faire-part **83**.

**La suite, dans l'ordre** : les MP3 → caler et rendre la pub · le feu vert de Mongazi → brancher
la caisse et la plume (`PAIEMENT.md`) → publier `_dist` (le relais part avec) → vérifier qu'une
adresse `/l/<jeton>` inconnue rend « Cette lettre n'existe pas ».

## La plume : ses savoir-faire et ses retouches (2026-10-21)

Mongazi : « donne-lui tous les outils et les skills qu'il faut pour satisfaire n'importe quel client
à 100 %, à tout moment ». La plume avait ses RÈGLES (ce qu'il ne faut pas faire) ; elle a reçu le
MÉTIER (comment on fait bien) :

- **Un savoir-faire par occasion** (`supabase/functions/_shared/savoirs.ts`, 27 occasions) : comment
  la lettre s'ouvre, ce qui la porte, comment elle finit, où elle se rate (la vraie excuse en quatre
  temps, la demande en mariage qui finit sur la question seule, la rupture claire dès le premier
  paragraphe…). Comme une compétence qu'on charge quand on en a besoin, **seul celui de l'occasion
  part avec la fiche** (`<savoir-faire>` dans le message) : le système, lui, reste figé et en cache.
- **Le métier commun, dans le système FR et EN** : à qui on écrit (**vouvoiement au pluriel** pour
  les mariés, les parents, une équipe, un groupe d'amis ; vouvoiement d'un patron et des
  beaux-parents ; une lettre « pour plus tard » parle à l'enfant devenu grand), la première phrase
  qui entre dans le vrai, le souvenir raconté sans enjoliver, la dernière phrase qui porte la lettre,
  le titre tiré du cœur de la lettre, la formule accordée au lien, la fiche maigre (court et juste),
  la bénédiction en une phrase, l'humour qui ne se moque jamais de la personne, plus de clichés.
- **Les retouches** (constructeur FR et EN) : « Plus courte », « Plus longue », « Plus tendre »,
  « Plus drôle », « Plus simple », « Plus solennelle », ou une demande écrite (140 signes). La plume
  repart de la lettre **telle qu'elle est dans les champs**, corrections à la main comprises
  (`<lettre-actuelle>` + `<retouche>`). Une retouche sans lettre est refusée (`retouche`), une
  retouche inconnue est ignorée, rien de ce que l'acheteur écrit ne ferme un bloc.
- **Cinq versions par lettre, retouches comprises** (trois avant) : ⚠️ à confirmer par Mongazi.
- **Le banc d'essai** `_banc_plume.mjs` : 15 fiches inventées (occasions et pièges : plusieurs
  destinataires, un patron, une fiche maigre, une consigne humiliante, le deuil glissé dans
  « Autre », l'anglais) + une retouche ; contrôles codés (longueur, prénom, vouvoiement, question
  finale, bénédiction, titre, formule) et relecture par un juge (fidélité, souvenir, consignes, ton,
  naturel, langue, chute). ⛔ **Appels payants, environ 32** (1 à 2 $) : rien ne part sans `--oui`.
  Résultat dans `_vues/` (ignoré par git). **Lancé deux fois le 2026-10-21** (« finalise ça maintenant ») :
  - **1er passage** : il a trouvé **un vrai bug de production** : l'élision codée (`elider`) utilisait ``,
    qui en JavaScript ne connaît que l'ASCII ; « notre amitié s'arrête ici » sortait « s'arrêt'ici »,
    « même avec » « mêm'avec ». Corrigé (frontière Unicode), contrôlé sur six phrases. Les six exemples
    publiés étaient intacts (relus avant publication). Aussi : la plume ajoutait des détails à la
    scène (47 « faits inventés » relevés par le juge), la retouche « Plus courte » raccourcissait d'un
    cinquième, il manquait l'espace avant « : ».
  - **Corrections** : ce qu'on a le droit d'ajouter (ce que l'acheteur ressent aujourd'hui) et ce
    qu'on n'a pas le droit d'ajouter (scène, geste, parole, objet, qualité non choisie) écrits dans les
    deux systèmes ; genre de l'acheteur jamais supposé ; « Plus courte » = au moins un tiers en moins ;
    « Bonne fête de Tabaski », « Joyeux Noël »… dits en toutes lettres ; typographie française (espace
    avant « : ; ! ? »), ⚠️ **sans casser la sonde des liens** : « https:// » devenait « https :// » et un
    lien passait, attrapé par la caisse le jour même (`(?!//)` + sonde tolérante).
  - **2e passage** (moyennes du juge sur 15 lettres, 1er → 2e) : fidélité 3,33 → **3,67**, consignes
    3,6 → **4,0**, langue 3,67 → **4,07**, chute 2,47 → **3,13**, souvenir 4,27, ton 3,93, naturel 3,0 ;
    faits inventés 47 → **34** ; la retouche passe de 140 à 64 mots. Le juge est sévère exprès (il
    compte « jour après jour » comme inventé).
  - ⏳ **Reste faible** : les souvenirs comiques s'enrichissent encore (« je tenais le sac », « la
    vendeuse ») et le « naturel » plafonne à 3 ; le registre « Avec nos expressions d'ici » est
    très prudent. À reprendre avec un troisième passage, de préférence une fois la plume en ligne et
    les premières vraies fiches lues.
- Contrôles : caisse **373** (46 nouveaux : couverture des savoir-faire, un seul envoyé, retouches,
  bornes, pièges, boutons égaux des deux côtés) ; `_qc.py` : les boutons de retouche essayés dans le
  vrai constructeur (la lettre des champs part, la demande écrite part avec Entrée, la limite les range).

## Les critères d'arrêt (recopiés le 2026-10-21, étape 6 du point de reprise)

**Ils sont écrits**, et depuis le début : dossier de décision du 27/08/2026
(`_plans/2026-08-27-minuit-dossier.html`, § « Critères d'arrêt, écrits d'avance »),
confirmés par la décision 12 de l'arrêté du 06/09 (`_memoire/decisions.md` :
« le 1er décembre 2026, critères du dossier inchangés »). Le texte, mot pour mot :

> Après huit semaines de publication quotidienne et 200 pages gratuites créées : si la
> conversion payante reste sous 3 % et qu'aucun revendeur n'a signé, la ligne romantique
> est un loisir. Dans ce cas, on ne s'entête pas : on garde le palier gratuit comme aimant
> pour le Catalogue à 50 000 F, et les heures repartent vers Boussole et PISTE.

⚠️ **Ils ne tiennent plus dans le calendrier, et c'est à Mongazi de trancher** (rien n'est
changé ici) : ils demandent **huit semaines de publication et 200 lettres gratuites**, or
**rien n'est en ligne** au 2026-10-21 et le 1er décembre est dans **six semaines**. Les
deux lectures possibles :
- **garder la date** du 1er décembre : la mesure portera sur ce qui aura tourné d'ici là,
  donc sur moins de huit semaines ;
- **garder les critères** : la date devient « huit semaines après la mise en ligne ».

Deux mots du texte ont vieilli sans changer la règle : « revendeur » (l'abonnement des
professionnels du dossier n'a pas été construit) et « publication quotidienne » (la vague 5,
les vidéos, n'est pas encore faite).

## Ce qui attend Mongazi

- ✅ ~~Le feu vert, la caisse, la plume~~ : **en ligne le 2026-10-21**. Le compte qui encaisse est celui
  de PISTE (par défaut). ⏳ **Le premier franc réel** (500 F : l'offre gratuite + la plume), puis lire
  le journal ; et la **commission SasPay**, toujours écrite nulle part.
- **Acheter `malettre.app`** (ou non).
- **Faire lire les six exemples** à deux ou trois personnes.
- **Filmer 10 secondes de vraie matière** (une main qui ferme une enveloppe,
  un cachet qu'on brise) : sert la page ET la vidéo publicitaire.
- Les 5 réponses déjà en attente (bloc archivé ci-dessous).
- **La vidéo publicitaire** (vague 5) : **les images sont faites** (2026-10-21) ;
  **les six MP3 ElevenLabs sont à déposer** dans `_partage/ma lettre/voix/` (textes dans
  `_studio-video/src/malettre/VOIX.md`).
- **Trancher les critères d'arrêt** : garder la date du 1er décembre, ou « huit semaines
  après la mise en ligne » (section ci-dessus). La mise en ligne étant le 21 octobre, la
  seconde lecture tombe le **16 décembre 2026**.
- **Le faire-part sur demande peut se vendre AVANT la caisse** (il passe par WhatsApp) :
  tout est prêt (README § « Le faire-part de mariage, sur demande »). **Le site est en ligne
  depuis le 2026-10-21** ; il lui faut **le compte** où le couple paie les 25 000 F, et
  une **sauvegarde** de `faire-part/_couples/` hors de ce disque. ⚠️ La date de l'exemple (12 décembre 2026) sera à changer après ce jour.

---

<!-- HISTOIRE DU NOM -->
## Archive : le bloc de `CLAUDE.md` au 2026-10-16, recopié intégralement

### LE PLI — la lettre digitale  *(produit interne, 2026-09-02 · **idée arrêtée le 2026-09-06**)*
- **Ce que c'est** : « une lettre digitale, c'est **une enveloppe cachetée qu'on
  ouvre à l'heure dite** ». L'acheteur écrit son mot, choisit l'heure, paie ;
  il envoie le lien lui-même, elle brise le cachet à l'heure dite, et lit.
  Dossier de décision : `_plans/2026-08-27-lepli-dossier.html` · manuel
  d'exploitation : `_plans/2026-08-28-lepli-manuel.html` · **arrêté (les 12
  décisions) : `_plans/2026-09-06-lepli-arrete.html`** · conditions et retrait :
  **`lepli/CONDITIONS.md`** · code : **`lepli/`**.
- **La thèse** : *le romantique est le marketing, l'événement est le chiffre
  d'affaires, le B2B est la retraite.* Un seul moteur, trois habillages.
- ✅ **LE NOM EST TRANCHÉ LE 2026-09-09 : LE PLI.** Mongazi : « je préfère le
  pli ». **Une seule enseigne**, et ⛔ **MINUIT disparaît comme marque** — le
  mot « minuit » ne survit que là où c'est le mot français (« elle s'ouvre à
  minuit pile »), jamais comme enseigne : garder les deux ferait deux vérités.
  ⚠️ **Le défaut qui a tué MINUIT, mesuré sur les trois registres** : il nommait
  une HEURE, donc il allait à la lettre d'amour, passait sur un faire-part de
  mariage, et ⛔ **ne passait pas sur une annonce de décès** (« MINUIT · Famille
  Dossou »), la ligne à 15 000-50 000 F. Des quatre finalistes (MINUIT · LE PLI ·
  LE CACHET · MISSIVE), **seul LE PLI passe les trois, parce qu'il nomme l'OBJET
  et pas l'occasion** (« un pli », c'est littéralement une lettre qu'on fait
  parvenir). ⚠️ **Le sous-domaine étant tranché** (`lepli.nebula-agency.online`),
  aucun domaine n'était à acheter : la disponibilité n'a contraint personne.
  **Renommé le jour même**, avant la première vente : `minuit/` → **`lepli/`**,
  schéma `minuit` → **`lepli`**, `minuit-*` → **`lepli-*`**, `MINUIT_DONNEES` →
  **`LEPLI_DONNEES`**, `minuit:brouillon` → **`lepli:brouillon`**, la vidéo et
  ses compositions, et l'enseigne partout. **333 remplacements, 28 fichiers**,
  QC **145 + 118 toujours verts**. ⚠️ **Un renommage mécanique abîme les textes
  qui COMPARENT les deux noms** : la note de la veille est ressortie en « LE PLI
  nomme une HEURE » et « les finalistes LE PLI · LE PLI » — relire les endroits
  où l'ancien nom était cité comme objet d'analyse, pas comme enseigne.
  ⛔ **Les documents datés gardent l'ancien nom** (`_plans/2026-08-27-minuit-*`,
  `_plans/2026-09-06-minuit-arrete.html`, les journaux, les conversations, les
  leçons) : à cette date le produit s'appelait MINUIT. L'arrêté porte un bandeau
  qui renvoie ici.
- **Fait le 2026-09-02** : **le gabarit** (`lettre.html`) et **le constructeur**
  (`creer.html`), **78 contrôles verts** (`python lepli/_qc.py`).
- 🕛 **FAIT LE 2026-09-06 — LA LETTRE TIENT L'HEURE ELLE-MÊME** (détail
  `_memoire/conversations/2026-09-06-lepli-finalisation.md`) : ⛔ **la fonction
  qui donne son nom au produit n'existait NULLE PART** — l'heure était demandée à
  l'acheteur, promise sur l'écran final (« elle la recevra le 14 février à
  00:00 ») et n'entrait dans aucune lettre ; ⚠️ **aucun contrôle ne pouvait le
  voir** (on ne mesure pas l'absence d'une chose dont personne n'a écrit qu'elle
  devait exister, même famille que la photo livrée et jamais affichée chez Au
  Braisé d'Or) · ⛔ **n8n, à qui le dossier ET le manuel confiaient la livraison,
  tournait sur le VPS Hostinger `72.61.103.56` qui n'appartient plus à
  Mongazi** : la fonction reposait sur une machine perdue → **elle vit dans la
  LETTRE**, qui ne dépend de rien et tient même si l'acheteur envoie son lien
  trois jours trop tôt · **avant l'heure le cachet dort** (cire éteinte, aucun
  bouton), la page **DIT** quand elle s'ouvre et compte à rebours, **à l'heure
  la cire s'allume** et le bouton paraît **sans rechargement** · ⚠️ **le
  garde-fou est dans `ouvrir()`, pas sur le bouton** (le code secret appelle
  `ouvrir()` directement) · ⚠️ **heure de CALENDRIER, sans fuseau** : minuit,
  c'est minuit **sur le téléphone de celle qui lit** (un instant absolu ferait
  s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou) ·
  ⛔ **on ne promet JAMAIS le secret** (le texte est dans la page) : le cachet
  tient l'heure, c'est tout, et c'est déjà ce que personne d'autre ne vend ·
  ⛔ **NEBULA n'écrit jamais à la destinataire** → plus besoin du modèle Meta
  hors fenêtre de 24 h, et le risque de harcèlement disparaît par conception ·
  **2 défauts de caisse** : ⛔ **deux échelles de prix** (les occasions
  portaient un « dès 10 000 F » appliqué nulle part → on prenait « Demande en
  mariage · dès 10 000 F » au palier gratuit et on payait **0 F** ; l'occasion
  décide du TON, le palier décide du PRIX) et ⛔ **le palier gratuit passait par
  la caisse** (`aller(p.prix === 0 ? "e-paiement" : "e-paiement")`, deux branches
  identiques = intention écrite puis perdue : une lettre offerte affichait
  « Envoie exactement cette somme, au franc près » au-dessus d'un numéro Mobile
  Money) · ⛔ **le seuil n'était mesuré par rien** alors qu'une lettre programmée
  ne montre que lui pendant des heures : le même gris tient 4,8:1 sur le papier
  et **3,09:1 sur la nuit**, mesuré → `--gris-nuit` · **QC 82 → 115**, avec un
  **TÉMOIN** à chaque verrou (heure passée, palier payé) sans quoi un verrou
  resté fermé pour toujours passerait avec les honneurs.
- 🏦 **LA CAISSE ET L'ADRESSE SONT ÉCRITES ET CONTRÔLÉES le 2026-09-06**
  (marche à suivre : **`lepli/PAIEMENT.md`**) — ⏳ **rien n'est déployé**, il
  manque 5 réponses de Mongazi (le sous-domaine est tranché le 2026-09-09) : **schéma Supabase `lepli`** + **3 fonctions
  de bord** (déposer+payer · la notification signée qui **ouvre la lettre** ·
  servir+**retirer**), sur la forme éprouvée de PISTE · **`_shared/lettre.ts`
  porte TOUT ce qui décide**, en Web standard, donc essayable **sans clé, sans
  réseau et sans base** (`node --experimental-strip-types lepli/_qc_caisse.mjs`,
  **118 contrôles**) · **le constructeur parle enfin à la caisse** (il posait sa
  commande sur `window.LEPLI_COMMANDE` et elle n'allait nulle part) ·
  ⛔ **ON NE STOCKE JAMAIS LE HTML DU NAVIGATEUR** : une porte publique qui
  accepte du HTML et le sert sur notre domaine est un **hébergeur de pages
  arbitraires**, gratuit et anonyme — on stocke les **données**, la lettre est
  **rebâtie** depuis le gabarit (`_gabarit_ts.py` l'y recopie, un contrôle
  compare) · ⛔ **le prix ne vient jamais du navigateur**, ni le pied viral, ni
  le code secret : un contrôle **lit les deux barèmes** et refuse la moindre
  différence · ⛔ **l'écran « colle la référence de ton SMS » DISPARAÎT**, avec
  le numéro Mobile Money et le choix du réseau (c'était le moment le plus
  fragile de la chaîne) · ⛔ **le brouillon ne s'efface qu'après une réponse
  heureuse** · ⛔ **le retrait passe avant tout** (état, date, remboursement) ·
  ⚠️ **U+2028 EN CLAIR dans les regex qui doivent le neutraliser, 3e et 4e fois**
  (dans `lettre.ts`, puis dans le contrôle qui l'essaie) : **un fichier qui
  documente son propre piège doit être vérifié comme s'il le contenait** ·
  ⚠️ **2 sondes menteuses** (l'une lisait la ligne d'**import** au lieu de
  l'appel ; l'autre interrogeait `pg.url` **en boucle pendant une navigation**,
  or le contexte d'exécution est détruit → `wait_for_url`) et ⛔ **`localStorage`
  appartient à l'ORIGINE** (lu depuis la page de paiement, il rend le rangement
  d'un autre site) · ⚠️ **3 contrôles RETOURNÉS**, pas supprimés · ⚠️ **un
  3e sérialiseur = une 3e vérité** : Python écrivait `"a": 1` là où les deux
  autres écrivent `"a":1` → séparateurs compacts partout, et le contrôle exige
  **le même octet** des deux implémentations · **QC 115 → 127 + 118**
- ✒️ **LA PLUME ET 27 OCCASIONS (2026-10-16)** : l'agent écrit la lettre à la
  place de l'acheteur, qui la relit et la signe (option **500 F** qui s'ajoute à
  l'offre, **gratuite à essayer**, 3 versions par brouillon), à partir d'une
  **fiche** : questions à choix propres à l'occasion + un souvenir + « comment tu
  la veux ». **27 occasions en 4 familles** (ruptures de couple et d'amitié, fêtes
  des pères, Noël, Tabaski…), ⛔ **pas de deuil**. Sonnet 5.5, fiche gardée nulle
  part, réponse relue par le code. Essayée en vrai : injection ignorée, deuil
  déguisé refusé, 2 à 6 F la version. ⛔ **Le constructeur n'envoyait pas la clé
  publique Supabase** : 401 garanti au lancement, corrigé. QC **203 + 213**.
  ⚠️ **Le Coffret promet encore « la livraison WhatsApp à l'heure choisie »**,
  contraire à « NEBULA n'écrit jamais à la destinataire » : à trancher. Détail :
  `_memoire/conversations/2026-10-16-lepli-plume.md`.
- ⏳ **CE QUI RESTE** : **brancher** la caisse (5 commandes, `PAIEMENT.md`) et la
  plume (`ANTHROPIC_API_KEY` + `lepli-plume`) ·
  ⛔ **PAS de Render avec le SQLite de `vitrina/`** : le disque de Render
  s'efface à chaque déploiement (c'est ce qui avait fait disparaître les 2 PDF
  des partenaires) — un déploiement, et les lettres payées n'existent plus ·
  le **ménage des lettres expirées** (`lepli_menage()` existe, rien ne
  l'appelle) · le **lien « retirer cette lettre »** dans le pied (la porte
  existe, le bouton non) ·
  **le faire-part pour NOVEMBRE** (saison des mariages + retour de la diaspora,
  ticket 25 000 F), pas pour février (volume, petit ticket) · **critères
  d'arrêt au 1er décembre 2026**, écrits d'avance.
- ⏳ **Les 5 réponses qui n'appartiennent qu'à Mongazi** (le sous-domaine est
  tranché depuis le 2026-09-09 : `lepli.nebula-agency.online`) : le compte qui encaisse ·
  **un n8n tourne-t-il ailleurs, oui ou non** · la commission
  SasPay (elle décide de la marge d'un ticket à 2 000 F, écrite nulle part) ·
  qui relit le deuil · **le premier franc encaissé pour de vrai**.
- **Fait le 2026-09-03** : **la vidéo de démonstration**, composition
  `lepli-demo` dans `_studio-video/` (1080x1920, 30 s, `npm run rendu:lepli`).
  Six plans, **les six signatures du produit rejouées en React** et non
  photographiées : une capture ne montre pas un cachet qui se brise. ⛔ **Ne pas
  la publier en l'état** : elle promet « Elle l'ouvre à minuit pile. Pas
  avant. » et affiche `lepli.nebula-agency.online`, or **ni la remise à
  l'heure dite ni le serveur n'existent** au 2026-09-03. ✅ **Depuis le
  2026-09-06 la promesse est tenue** (la lettre porte le verrou) : il ne reste
  que l'adresse affichée, qui doit exister avant publication.
  ⛔ **Jamais de fondu enchaîné entre deux plans qui
  montrent du papier** : mesuré, deux feuilles à 50 % l'une sur l'autre
  ressemblent à une panne, pas à une transition (les plans partagent le même
  fond de nuit, donc la coupe est déjà invisible).
  Détail : `_memoire/conversations/2026-09-03-lepli-video-demo.md`.
- ⛔ **`</script>` écrit par un acheteur TUE la page** : les données atterrissent
  dans un bloc `<script>`, et **`json.dumps` ne protège pas de ça**. Toute
  sérialisation passe par **`lepli/_injecter.py`**, seul endroit, qui neutralise
  `</`, `<!--` et U+2028/U+2029. ⚠️ **Le commentaire qui documentait ce piège le
  contenait en clair** et fermait lui-même le bloc ; ⚠️ **la fonction qui
  neutralise U+2028 les portait en clair dans ses regex**. → **`node --check` sur
  le script en ligne avant d'écrire**, et se méfier d'un fichier qui documente
  son propre piège.
- ⛔ **Le seuil EST le produit** : une lettre livrée garde toujours son cachet.
  L'aperçu du constructeur s'ouvre (l'acheteur doit voir SES mots, c'est là que
  la vente se fait), mais **le drapeau d'aperçu ne part jamais dans la commande**,
  et un contrôle le vérifie.
- ⚠️ **Aucune police téléchargée, aucun appel réseau, `noindex`** : une lettre
  s'ouvre dans un taxi et n'a rien à faire dans un moteur. **Les photos sont des
  données (`data:`), jamais des liens** : un lien distant ferait dépendre la
  lettre d'un serveur et **fuiterait l'heure d'ouverture** vers un tiers.
- ⛔ **La sauvegarde du formulaire n'est pas un confort** : pour payer, l'acheteur
  QUITTE la page. Sans restauration au retour il perd son quart d'heure, ne
  recommence pas, et **on ne sait même pas que la vente a existé**.
- ✅ **AVANT LA PREMIÈRE VENTE : `lepli/CONDITIONS.md` est écrit** (le dossier
  classait ce risque en *critique* et notait qu'aucune des 5 références ne le
  traite) — adresse impossible à deviner, `X-Robots-Tag` en plus de la balise,
  expiration (7 jours offert / 1 an payé), aucune mesure d'audience, et
  **retrait sous 24 h à la demande de la personne visée, sans discuter, sans
  prévenir l'acheteur, sans rembourser** : ⚠️ **le pouvoir de retirer appartient
  à qui détient le lien**, ce qui est exactement l'ensemble des gens concernés.
  ⛔ **Jamais de MP3 hébergé** (contrefaçon). ⚠️ **Le deuil ne se décore pas** :
  sobriété totale, aucun emoji, relecture par quelqu'un qui vient d'enterrer un
  proche **avant** de le vendre, et c'est la condition d'ouverture de la ligne.
<!-- FIN HISTOIRE -->
