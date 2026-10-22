# MA LETTRE À… · la lettre digitale

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure dite.**
> Le sceau, le pli, l'encre qui sèche. Toutes les animations de ce produit sortent
> de cet objet, et d'aucun autre.

<!-- HISTOIRE DU NOM -->
## Le nom : MA LETTRE À… (2026-10-16)

Le produit est né **MINUIT** (2026-09-02), puis s'est appelé **LE PLI**
(2026-09-09), puis **MA LETTRE À…** (2026-10-16), décidé par Mongazi.

- **MINUIT** nommait une heure : il allait à la lettre d'amour, et ne passait
  pas sur une annonce de décès.
- **LE PLI** nommait l'objet et passait les trois registres, mais il fallait
  l'expliquer. Mongazi : « on doit pouvoir comprendre dès qu'on le lit ou
  qu'on le dit ».
- **MA LETTRE À…** se comprend tout de suite, et **se termine par le prénom de
  la personne** : « Ma lettre à Afi », « Ma lettre à papa ». Le seuil et
  l'onglet de chaque lettre le disent. Il tient sur les trois registres
  (l'amour, les fêtes, et plus tard le deuil : « Ma lettre à la famille
  Dossou »).

À l'écran : « Ma lettre à… ». Dans le code : `malettre` (dossier, schéma,
fonctions `malettre-*`, clés `malettre:*`, marqueur `MALETTRE_DONNEES`).
⛔ Les documents datés gardent l'ancien nom (`_plans/2026-08-27-lepli-*`,
journaux, conversations, leçons) : à cette date, le produit s'appelait ainsi.

⚠️ `malettre.com` est déjà pris. `malettre.app`, `.online`, `.bj` et `.ci` ne
répondaient pas le 2026-10-16. Avec `malettre.app`, le lien d'une lettre peut
se lire « ma lettre à Afi » (`malettre.app/a/afi`). En attendant :
`malettre.nebula-agency.online`.
<!-- FIN HISTOIRE -->

Dossier de décision : `_plans/2026-08-27-lepli-dossier.html`
Manuel d'exploitation : `_plans/2026-08-28-lepli-manuel.html`
**L'arrêté (les 12 décisions) : `_plans/2026-09-06-lepli-arrete.html`**
Conditions et retrait : `malettre/CONDITIONS.md`

---

## Ce qui existe, au 2026-10-16

| Brique | État |
|---|---|
| **Le gabarit de la lettre** (`lettre.html`) | ✅ construit, **212 contrôles verts** (`_qc.py`) |
| **Le constructeur** (`creer.html`) | ✅ construit |
| **La sauvegarde du formulaire** | ✅ à chaque frappe, restaurée au retour |
| **L'heure d'ouverture** | ✅ **dans la lettre**, depuis le 2026-09-06 |
| **Les conditions et le retrait** | ✅ écrits, `CONDITIONS.md` |
| **L'encaissement** | ✅ **écrit et contrôlé** (SasPay), ⏳ pas encore branché |
| **L'adresse en ligne** | ✅ **écrite et contrôlée**, ⏳ pas encore déployée |
| **La vidéo de démonstration** | ✅ construite le 2026-09-03, publiable dès que l'adresse existe |
| **Les occasions** | ✅ **27**, rangées en quatre familles, depuis le 2026-10-16 · ⛔ pas de deuil |
| **La plume** (l'agent qui écrit la lettre) | ✅ écrite, contrôlée, **essayée en vrai sur le modèle** · ⏳ pas déployée |
| **La page d'accueil** (`index.html`) | ✅ construite le 2026-10-16, **78 contrôles verts** (`_qc_accueil.py`) · ⏳ pas en ligne |
| **La publication** (`_dist.py`) | ✅ prête (16 fichiers, `404`, `_headers`, `robots.txt`) · ⛔ rien de déployé |

Le manuel disait : *« un gabarit irréprochable, la sauvegarde du formulaire, la
livraison à l'heure choisie, dans cet ordre »*. **Les trois sont faits.**

### La page d'accueil (2026-10-16)

**La phrase** : une lettre, c'est une feuille qui devient une enveloppe scellée,
puis qui redevient une feuille entre les mains de quelqu'un. Le récit et la liste
des sections : `CONTEXT.md`.

```bash
python malettre/_build_accueil.py     # index.html + exemples/*.html + llms.txt (GÉNÉRÉS)
python malettre/_qc_accueil.py        # 235 contrôles (FR + EN), tous verts avant publication
python malettre/_voir_accueil.py      # captures 390 et 1440 dans _vues/accueil, à REGARDER
python malettre/_og.py                # og.jpg (1200 × 630, réseau requis pour les polices)
python malettre/_dist.py              # _dist/ : seulement ce qui doit être en ligne
```

- ⛔ **On édite `_accueil_src.html`, `exemples.json` ou le catalogue de
  `creer.html`**, jamais `index.html` ni `exemples/*.html`.
- ⛔ **Aucun prix, aucune occasion n'est écrit dans la source** : le build les
  lit dans `creer.html`, et le contrôle les relit dans le NAVIGATEUR (pas avec
  la regex du build, sinon il vérifierait le build par lui-même).
- ⛔ **Les exemples sont de vraies lettres** bâties par `_injecter.poser()` ;
  leurs personnes sont inventées et la lettre le dit (« Exemple · »).
- ⚠️ **Au téléphone, un élément trop large ne déborde pas : il DÉZOOME la
  page**, et `innerWidth` grandit avec lui. Le contrôle compare donc à la
  largeur demandée (390), jamais à `innerWidth`. Deux coupables trouvés le
  2026-10-16 : l'`input` du prénom (largeur naturelle ~440 px) et les timbres
  agrandis avant leur frappe.
- ⚠️ **La sonde de contraste a deux témoins** (un gris sur gris doit échouer, le
  fond papier du bouton de la barre doit être lu) : au téléphone, une capture
  d'élément refait défiler la page et mesurait le fond une section à côté.
- ⚠️ **Pour voir le chargement, figer ses transitions** (`getAnimations()`,
  `pause()`, `currentTime`), pas `clock.install()` qui laisse couler le temps.

**Ce que la vitrine vend depuis la vague 3** (détail : `CONTEXT.md`) :

- **« Ouvre-la toi-même »** : la vraie lettre (le vrai gabarit, en `srcdoc`) s'ouvre
  dans 10 s, puis des **pastilles** cire / papier / pluie la rhabillent ; rhabillée,
  elle s'ouvre tout de suite, avec une phrase à gratter. Les pastilles sont LUES dans
  `HABILLAGE` (`creer.html`), écrites en HTML par le build (aucun CLS).
- **Les exemples sont habillés** : `habillage` (et parfois `gratter`) dans
  `exemples.json` / `exemples.en.json` ; le build refuse une valeur absente des listes.
- **La prochaine grande date** : calculée dans la page sur les occasions qui ont un
  `jour` (Saint-Valentin, Noël, Nouvel an). ⚠️ Ses clés (`a`, `j0`, `j1`, `jn`, `go`)
  sont neutres exprès : `avant` et `dans` passaient pour du français dans le script
  anglais.
- **Le faire-part sur demande** : prix et numéro dans **`faire-part/offre.json`**, et
  nulle part ailleurs (bloc, FAQ, `llms.txt` le lisent).
- **La FAQ** : 8 `<details class="q">`. Le `FAQPage` est LU dans ces questions par le
  build, et le contrôle compare les deux côtés dans le navigateur. La réponse du prix
  est écrite par `faq_prix()` depuis le catalogue, qui **refuse d'écrire** si une
  offre payante ne dure plus un an, garde la signature ou perd l'habillage.
- **`llms.txt`** : fabriqué par le build depuis la page et le catalogue, publié par
  `_dist`. ⚠️ À relancer après tout changement de prix ou de FAQ (le build le fait).

### Les deux langues (2026-10-16)

Décision de Mongazi : le français ET l'anglais sur tout le parcours (vitrine,
constructeur, lettre, plume, exemples, pub). **Le français est la source.**

```bash
python malettre/_build_accueil.py     # lance _traduire.py, puis l'accueil FR et EN
python malettre/_qc_langues.py        # 52 contrôles : aucun mot français dans l'anglais
python malettre/_voir_accueil.py en   # captures de la page anglaise (_vues/accueil-en)
python malettre/_og.py                # og.jpg et og-en.jpg
```

- **La lettre** porte un champ `langue` (`fr` ou `en`, liste fermée côté
  serveur : tout le reste est du français). Le gabarit a son petit
  dictionnaire `L` ; **seuls les mots du gabarit changent, jamais ceux de
  l'acheteur.** En anglais le seuil dit « My letter to Afi » ; la marque reste
  « Ma lettre à… ». Les heures se disent sur douze (« at 6:30 pm »).
- **Les pages anglaises** (`en/*.html`) sont FABRIQUÉES par `_traduire.py` à
  partir de `i18n/en.txt`. Format **sans échappement** (une ligne `FR:`, une
  ligne `EN:`). ⛔ Il refuse d'écrire si une phrase française est introuvable :
  **une phrase changée en français doit l'être aussi dans `i18n/en.txt`**.
- **La plume anglaise** a son propre système (`SYSTEME_EN`), mis en cache à
  part. ⛔ Elle a titré deux lettres sur six en français le jour de son
  écriture (« Merci pour chaque matin ») : la relecture refuse désormais un
  titre ou une formule anglaise contenant du français (`refus: 'langue'`).
  ⛔ L'élision française ne s'applique qu'au français (« tell m'about »).
- **Les offres** ont leur nom anglais côté serveur (`en` dans `PALIERS` :
  Free, The Note, The Letter, The Keepsake), comparé à `en/creer.html` par un
  contrôle. La caisse renvoie l'acheteur anglais vers `/en/merci.html`.
- **Un brouillon par langue** (`malettre:brouillon:en`) : repris en anglais, un
  brouillon français garderait des réponses qu'aucune puce anglaise ne coche.
- ⚠️ **Pièges du jour** : `innerText` applique le `text-transform` (« DAYS
  TOGETHER ») ; `document.fonts.ready` répondait avant le chargement des
  polices (une image de partage est sortie sans un mot) ; le sélecteur de
  langue a fait passer « Write my letter » sur deux lignes au téléphone.

### Le faire-part de mariage, sur demande (vague 4, 2026-10-16)

NEBULA le fait pour le couple, **35 000 F** (25 000 F jusqu'au 2026-10-22) payés hors de la caisse (prix et
numéro : `faire-part/offre.json`, seule source). Le couple écrit depuis le bouton
de la vitrine ; on remplit sa fiche ; la page part à une adresse impossible à
deviner. Les invités répondent sur **le WhatsApp des mariés**, jamais celui de
NEBULA.

```bash
python malettre/_faire_part.py                      # les deux exemples (Kossi & Afiwa, FR et EN)
python malettre/_faire_part.py malettre/faire-part/_couples/sena-grace.json   # un vrai couple
python malettre/_qc_faire_part.py                   # 83 contrôles
python malettre/_dist.py                            # publie les exemples ET les pages des couples
```

**Pour un vrai couple** :
1. Leur demander (un seul message WhatsApp) : vos deux prénoms · les familles
   (facultatif) · la date · pour chaque moment de la journée l'heure, ce que c'est
   et le lieu · la ville · la tenue et ses couleurs · un mot pour vos invités
   (facultatif) · jusqu'à 12 photos · le numéro WhatsApp où recevoir les réponses ·
   la date limite pour répondre.
2. Copier `faire-part/exemple.json` en `faire-part/_couples/<prenoms>.json`, retirer
   `_lire` et `exemple`, remplir. Le fuseau : `+01:00` au Bénin, `+00:00` au Togo et
   en Côte d'Ivoire. Le numéro : indicatif compris, chiffres seuls (le `01` béninois
   GARDÉ : `2290197…`). Les photos : des chemins relatifs à la fiche.
3. Fabriquer : le générateur valide tout (il refuse et liste les fautes), tire le
   **jeton** à la première fois et l'écrit dans la fiche (l'adresse ne change plus
   ensuite), embarque les photos en données (1 200 px), et note l'**empreinte**
   du jeton dans `faire-part/publies.txt`.
4. Ouvrir la page (`faire-part/_couples/sortie/<jeton>.html`), la faire valider au
   couple, encaisser, publier (feu vert de Mongazi), envoyer l'adresse
   `https://malettre.nebula-agency.online/f/<jeton>`.

- ⛔ **Les fiches et les pages des couples ne vont JAMAIS dans git** (dépôt public :
  noms, lieux, numéros ; et le jeton EST l'adresse). `faire-part/_couples/` est
  ignoré. ⚠️ **Le sauvegarder ailleurs** : si ce disque meurt, les fiches meurent.
- ⛔ **`_dist.py` refuse de construire si une page publiée manque sur ce disque**
  (il compare les empreintes de `publies.txt`) : un déploiement Pages est un
  instantané complet, publier depuis un autre poste effacerait les faire-part en
  ligne. Publier depuis le poste qui porte `faire-part/_couples/`.
- ⚠️ **Le compte vise l'heure du LIEU** (date, heure, fuseau), pas celle du
  téléphone comme la lettre : un mariage a lieu à une heure de Cotonou.
- Le jour J, le compte laisse place à « C'est aujourd'hui ! » ; 36 h après, à « Merci
  d'avoir été là », et les réponses se ferment.
- ⚠️ **L'exemple est daté du samedi 12 décembre 2026** : passé ce jour, le
  générateur le refuse et le contrôle rougit. Changer la date dans les deux fiches
  d'exemple.

### La vidéo de démonstration

`_studio-video/`, composition **`lepli-demo`** : 1080x1920, 30 s.
`cd _studio-video && npm run rendu:lepli`.

Les **six signatures ci-dessous sont rejouées en React**, pas photographiées :
une capture ne montre pas un cachet qui se brise. Les couleurs, le texte de la
lettre et le prix y sont lus depuis **ce dossier**, recopiés une seule fois
dans `_studio-video/src/lepli/donnees.ts`.

⚠️ Elle promet « Elle l'ouvre à minuit pile. Pas avant. » **Cette phrase est
vraie depuis le 2026-09-06** : la lettre tient l'heure.
<!-- HISTOIRE DU NOM -->
⛔ **Elle porte encore l'ancien nom** (LE PLI, `lepli.nebula-agency.online`) :
elle est à refaire avec la vidéo publicitaire, sous le nom MA LETTRE À….
<!-- FIN HISTOIRE -->

---

## Les fichiers

| Fichier | Ce que c'est |
|---|---|
| `lettre.html` | **Le produit.** Une lettre, autonome, sans aucun appel réseau |
| `creer.html` | Le constructeur : occasion, **la plume ou l'acheteur**, la fiche, aperçu vivant, commande |
| `paiement.html` | **La page de paiement** : la somme, et **le lien** (bouton + en clair) |
| `merci.html` | **La page de retour**, celle que SasPay rappelle. ⛔ Elle ne prouve rien |
| `_injecter.py` | **Le seul endroit** où l'on écrit des données dans le gabarit |
| `_qc.py` | **203 contrôles**. Vert obligatoire avant toute mise en ligne |
| `_qc_caisse.mjs` | **213 contrôles** sur la caisse et la plume, sans clé ni réseau |
| `supabase/` | La base et les **quatre** fonctions de bord. Voir `PAIEMENT.md` |
| `_gabarit_ts.py` | Recopie `lettre.html` dans un module pour les fonctions |
| `PAIEMENT.md` | Où vit chaque morceau, et comment brancher le jour venu |
| `CONDITIONS.md` | Ce qu'on promet, et le retrait sous 24 h. À lire avant de vendre |
| `_voir.py` | Fabrique les captures à REGARDER (390 et 1440) |

```bash
python malettre/_qc.py                                   # les 203 contrôles
node --experimental-strip-types malettre/_qc_caisse.mjs  # les 213 de la caisse et de la plume
python malettre/_gabarit_ts.py                           # après toute retouche de lettre.html
python malettre/_voir.py                                 # les captures
cd malettre && python -m http.server                     # pour ouvrir creer.html
```

---

## Les six animations, une par section

Toutes tirées de l'objet « enveloppe cachetée », aucune n'est décorative.

| Section | Signature |
|---|---|
| 1 · Le seuil | **Le cachet dort, s'allume à l'heure dite, puis se brise** en trois éclats de cire |
| 2 · Le pli | **Le dépliage** : la feuille s'ouvre, ses deux plis s'effacent |
| 3 · La lettre | **L'encre qui sèche** : flou vers net, ligne après ligne |
| 4 · Les photos | **Le polaroïd qui se développe**, du blanc vers l'image |
| 5 · Le compte | **Les chiffres qui roulent**, avec une sortie qui ralentit |
| 6 · La signature | **Le trait qui s'écrit** (`stroke-dashoffset`) |

---

## Les décisions, et pourquoi

**Le seuil EST le produit.** Les cinq références du dossier ont toutes une
barrière. Elle crée l'attente, rend la page privée, et surtout **rend filmable**
en créant un avant/après. Une lettre livrée garde donc toujours son cachet : un
contrôle vérifie que le drapeau d'aperçu ne part jamais dans la commande.

**Aucune police téléchargée.** La pile est système, choisie : Iowan Old Style
(Apple) et Palatino (Windows) sont de vraies faces de correspondance, plus
chaudes que Georgia, et déjà sur la machine. Une lettre doit s'ouvrir dans un
taxi ; on ne fait pas attendre un cadeau derrière un fichier de police.
⛔ Ne pas rajouter Google Fonts.

**Les photos sont des données, jamais des liens.** Une photo distante ferait
dépendre la lettre d'un serveur, et **fuiterait l'heure d'ouverture** vers un
tiers. Le gabarit refuse toute source qui ne commence pas par `data:`.

**`noindex`.** Une lettre est privée. Elle n'a rien à faire dans un moteur.

**Le pied viral n'existe qu'à La Carte**, l'offre d'entrée à 1 000 F qui a remplacé l'offre
gratuite le 2026-10-22. C'est la boucle de croissance : chaque destinataire est un acheteur
possible. Les autres offres le retirent.

---

## ✒️ La plume, et pourquoi elle existe (2026-10-16)

Le vrai frein d'une lettre n'est pas le prix, c'est **la page blanche** : on
ouvre le constructeur, on regarde la case vide, on repart. La plume écrit la
lettre **à la place** de l'acheteur, qui la **relit, la corrige et la signe**.
Ce sont ses mots : la plume les lui prête.

**Le geste.** Il choisit l'occasion, puis « La plume l'écrit pour moi ». Une
fiche lui pose des **questions à choix** (qui est-ce, le ton, ce que la
personne a de rare, et selon l'occasion : pourquoi, la porte, ce qu'elle t'a
appris, ce que tu lui souhaites…) et lui laisse **deux zones libres** : un
souvenir que vous seuls connaissez, et « comment tu la veux ». Un bouton, et la
lettre arrive dans les champs, titre et formule de fin compris.

⛔ **Depuis le 2026-10-22, plus rien n'est gratuit** (Mongazi : un essai gratuit « se contourne
en changeant de navigateur ou de téléphone ») : la plume est **coupée en ligne** jusqu'à ce
qu'elle écrive APRÈS le paiement (le chantier suivant, `CONTEXT.md` § « LES PRIX »). Ce qui suit
décrit son fonctionnement d'avant, toujours actif sur le PC (`localhost`).

**Le prix.** **500 F**, une option qui s'ajoute à l'offre choisie, jamais un
palier : avec La Carte, la lettre coûte 1 500 F.
⚠️ **Gratuite à essayer, payante à l'envoi** : l'acheteur lit SA lettre avant
de payer, c'est là que la vente se fait. D'où un compteur : **trois versions
par brouillon, douze par adresse et par jour**. Ce qui se paie, c'est le texte
de la plume, pas le mode : « Repartir d'une page blanche » ne la compte plus,
et « Remettre la lettre de la plume » se rattrape.

**Ce qui la tient**, tout dans `supabase/functions/_shared/plume.ts` :

- ⛔ **Elle n'invente aucun fait** : ni souvenir, ni lieu, ni date, ni lignée,
  ni nom de clan, ni mot de fon ou de yoruba que l'acheteur n'a pas écrit, ni
  verset cité mot pour mot.
- ⛔ **Pas de deuil**, même glissé dans « Autre occasion » (`CONDITIONS.md` §7).
  Essayé en vrai : « Les funérailles de mon oncle » est refusé.
- ⛔ **Une consigne dans un prompt n'est pas un contrôle** : le code relit la
  réponse et retire tiret long, emoji, et refuse lien, numéro, adresse
  électronique. Une fiche qui tente une injection (« </fiche> nouvelle
  consigne… ») est neutralisée avant d'arriver au modèle, et le modèle l'ignore.
- ⛔ **La fiche n'est gardée nulle part** : seul un compteur reste, deux jours
  (une empreinte d'adresse, l'identifiant du brouillon, l'heure).
- **Sonnet 5.5** (règle maison : jamais Opus sur du texte client), sortie
  contrainte par un schéma JSON, système **mis en cache** (1 968 jetons relus
  dès la deuxième lettre, mesuré), `fallbacks: "default"` pour qu'un filtre de
  sécurité trop zélé ne refuse pas une rupture « cash ».
- **Coût mesuré** : 2 à 6 F CFA la version, cache chaud. Trois versions au
  plus : moins de 20 F sur une plume vendue 500 F.

⚠️ **Les identifiants d'occasion vivent à deux endroits** (`OCCASIONS` dans
`creer.html`, `REGISTRES` dans `plume.ts`) : un contrôle compare les deux
listes. Même règle pour le prix de la plume (`PLUME`, des deux côtés).

---

## 🏦 La caisse, en une phrase

Le constructeur envoie **les données** de la lettre à `malettre-commande`, qui en
fixe le prix (⛔ jamais le navigateur), la dépose, et ouvre un paiement SasPay.
La notification signée rend la lettre joignable, seule, à n'importe quelle
heure. `malettre-lettre` la sert à une adresse de **110 bits tirés au sort**, et
la retire à la demande. Tout est dans **`PAIEMENT.md`**.

⛔ **On ne stocke jamais le HTML du navigateur** : une porte publique qui
accepte du HTML et le sert sur notre domaine est un hébergeur de pages
arbitraires, gratuit et anonyme. La lettre est **rebâtie** à partir du gabarit.

---

## 🕛 Le verrou d'heure, et pourquoi il vit DANS la lettre

C'est la fonction qui donne son nom au produit, et **aucun concurrent observé ne
la propose**. Le dossier et le manuel la confiaient tous les deux à n8n. Or n8n
était auto-hébergé sur le VPS Hostinger `72.61.103.56`, et **cette machine
n'appartient plus à Mongazi**. La fonction reposait sur un serveur perdu.

Elle vit donc **dans la lettre**, et c'est mieux :

- elle **ne dépend de rien** : ni serveur, ni réseau, ni compte tiers ;
- elle tient **même si l'acheteur envoie son lien trois jours trop tôt**, ce
  qu'aucune machine à envoyer n'aurait rattrapé ;
- elle retire d'un coup **trois dépendances** : le modèle WhatsApp à faire
  approuver par Meta pour sortir de la fenêtre de 24 h, le coût d'un envoi, et
  le risque le plus grave du produit, celui d'écrire à quelqu'un qui n'a jamais
  donné son numéro.

**Ce qu'on promet, et rien de plus :** le cachet ne se brise pas avant l'heure.
⛔ **On ne promet JAMAIS le secret** : le texte est dans la page, qui sait lire
un code source peut le lire avant l'heure. Une lettre est un cadeau emballé, pas
un coffre-fort. Voir `CONDITIONS.md` §1.

**L'heure est une heure de CALENDRIER, sans fuseau** (`2027-02-14T00:00`) :
minuit, c'est minuit sur le téléphone de celle qui lit. Un instant absolu ferait
s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou.

⚠️ **Le garde-fou est dans `ouvrir()`, pas sur le bouton** : le code secret
appelle `ouvrir()` directement, et tout chemin futur y passera aussi.

⚠️ **L'aperçu du constructeur ignore le verrou** : l'acheteur doit voir SES mots
pendant qu'il les tape, c'est là que la vente se fait. Le drapeau d'aperçu ne
part jamais dans la commande, et un contrôle le vérifie.

⚠️ **Chaque verrou a son TÉMOIN dans le QC** (une heure passée, un palier payé) :
sans lui, un verrou resté fermé pour toujours passerait tous les contrôles avec
les honneurs.

---

## ⛔ Les trois pièges, tous rencontrés le jour de l'écriture

### 1 · « </script> » dans le mot d'un acheteur tue la page

Les données atterrissent **dans un bloc `<script>`**. Un acheteur qui écrit la
balise fermante ferme le bloc, et la page entière meurt : plus de titre, plus de
lettre, plus de seuil.

⚠️ **`json.dumps` ne protège pas de ça** : c'est une chaîne JSON parfaitement
valide, et le navigateur cherche la balise fermante **avant** de lire le JSON.

D'où `_injecter.py`, **seul endroit** où l'on sérialise. Il neutralise `</`,
`<!--` et les séparateurs de ligne U+2028 / U+2029.

### 2 · Le commentaire qui explique le piège contenait le piège

Le commentaire de `creer.html` qui documentait ce danger était écrit **avec la
balise littérale**. Il fermait donc lui-même le bloc, et tout le script du
constructeur était mort. Le QC l'a vu ; l'œil, non.

### 3 · Le garde-fou contenait le défaut qu'il devait empêcher

La fonction qui neutralise U+2028 / U+2029 les portait **en clair** dans ses
expressions régulières. Or ce sont des fins de ligne pour JavaScript : elles
cassaient la syntaxe du fichier.

> **La règle qui en sort :** `node --check` sur le script en ligne avant d'écrire.
> Un fichier qui contient sa propre documentation d'un piège doit être vérifié
> **comme s'il contenait le piège**, parce que c'est souvent le cas.

⚠️ **Cinquième fois le 2026-10-16**, dans `plume.ts` (trois expressions) et
dans `_qc_caisse.mjs` : les échappements **tapés** `\u2028`, `\u2014` sont
arrivés dans les fichiers **en caractères réels**, et la syntaxe du contrôle
cassait. Trouvé par `node --check`, comme prévu. Même la phrase qui raconte le piège l’a reproduit en s’écrivant.
Désormais ils se
**fabriquent** par programme (une barre oblique, `chr(92)`, puis le code), et
un contrôle vérifie que `plume.ts` ne contient aucun des caractères qu'il retire.

---

## ⚠️ Les contrôles qui ont menti avant de dire vrai

Des sondes ont accusé un produit sain, ou blanchi un produit cassé. À relire avant d'ajouter un contrôle.

- **`inner_text` renvoie le texte RENDU.** `.pour` et le libellé du compte sont
  en `text-transform: uppercase` : la sonde lisait « ZARA » et « JOURS ENSEMBLE »
  et concluait à une erreur. On lit `text_content` quand c'est le contenu qui
  compte.
- **Chercher un mot au lieu du marqueur.** « MALETTRE_DONNEES » figure aussi dans
  le commentaire d'en-tête du gabarit, qui doit rester. Le bon test porte sur
  `/*MALETTRE_DONNEES*/`.
- **Une attente fixe est un pari.** La chaîne de l'aperçu fait 260 ms
  d'anti-rebond, plus le chargement de l'iframe, plus 620 ms d'ouverture :
  800 ms donnait **1 passage vert sur 3**. `attendre()` attend l'ÉTAT.
- **Un serveur de test mono-tâche** se bloque dès la seconde requête et fait
  échouer sur un « Timeout » sans rapport. `ThreadingHTTPServer`, toujours.
- **Deux instantanés ne mesurent pas un compte à rebours.** Il change une fois
  par seconde : deux lectures peuvent tomber dans la même. On échantillonne.
- **Lire l'attribut au lieu de ce qui est peint** (2026-10-16). Le contrôle
  du bandeau « on a retrouvé ta lettre » lisait `hidden` ; or
  `.repris{display:flex}` l'emportait sur lui, et le bandeau était **peint pour
  tout le monde, dès la première visite**. Même chose pour le « + » des photos
  (`display:grid`), qui ne partait jamais à trois photos. Trouvé en
  **regardant une capture**, pas par un contrôle. Désormais
  `[hidden]{display:none!important}` dans le constructeur, et le contrôle
  demande `is_visible`, avec un témoin à la première visite.
- **Un témoin qui contient le mot cherché.** Pour vérifier qu'un « registre »
  envoyé par le navigateur est ignoré, la sonde cherchait « menace » dans le
  message : la consigne de la rupture dit « ni menace ». Le témoin doit être un
  mot qu'aucune consigne ne contient.
- **Un chemin nu dans `import()` sous Windows** est lu comme une adresse au
  protocole « c: ». `_qc_caisse.mjs`, écrit dans un conteneur Linux, ne
  tournait pas sur le PC de Cotonou ; et `core.autocrlf` rend les fichiers en
  CRLF, donc deux fichiers identiques dans git se déclaraient différents.
  `pathToFileURL`, et les fins de ligne ramenées à LF avant toute comparaison.

---

## ⛔ Les trois défauts trouvés le 2026-09-06, tous invisibles au QC vert

1. **L'heure n'existait nulle part.** Elle était demandée à l'acheteur, promise
   sur l'écran final (« elle la recevra le 14 février à 00:00 ») et n'entrait
   dans aucune lettre. ⚠️ **Aucun contrôle ne pouvait le voir** : on ne mesure
   pas l'absence d'une chose dont personne n'a écrit qu'elle devait exister.
2. **Deux échelles de prix.** Les occasions portaient un « dès 10 000 F »
   appliqué nulle part : on prenait « Demande en mariage · dès 10 000 F » au
   palier gratuit, et on partait à 0 F. **L'occasion décide du ton, le palier
   décide du prix.**
3. **Le palier gratuit passait par la caisse.** `aller(p.prix === 0 ?
   "e-paiement" : "e-paiement")` : deux branches identiques, donc l'intention
   avait été écrite puis perdue. Une lettre offerte affichait « Envoie
   exactement cette somme, au franc près » au-dessus d'un numéro Mobile Money.

Et un quatrième, de contraste : **le seuil n'était mesuré par rien**, alors
qu'une lettre programmée ne montre que lui, parfois pendant des heures. Le même
gris tient 4,8:1 sur le papier et tombe à **3,09:1** sur la nuit du seuil,
mesuré. → `--gris-nuit`, et quatre contrôles qui le mesurent.

---

## ⏳ Ce qui reste

Les douze décisions sont prises : `_plans/2026-09-06-lepli-arrete.html`.

0. **Brancher la plume** en même temps que la caisse : une clé et une
   fonction de plus, `PAIEMENT.md` §4.
1. **Brancher la caisse.** Elle est écrite, contrôlée, et pas déployée : la
   marche à suivre tient en cinq commandes dans **`PAIEMENT.md`**. ⛔ Pas de
   Render avec le SQLite de `vitrina/` : son disque s'efface à chaque
   déploiement, c'est ce qui avait fait disparaître les deux PDF des
   partenaires. Un déploiement, et les lettres payées n'existent plus.
2. **Le ménage des lettres expirées** : `malettre_menage()` existe, rien ne
   l'appelle encore. Une tâche quotidienne suffit.
3. **Le lien « retirer cette lettre »** dans le pied de la lettre : la porte
   existe, le bouton non. Le retrait passe par WhatsApp en attendant.
4. **Le faire-part avec confirmation**, pour **novembre** (saison des mariages
   et retour de la diaspora), pas pour février.
5. ⛔ **Ne jamais héberger un MP3** : c'est de la contrefaçon. Lien externe, ou rien.
6. Le deuil, **après** relecture par quelqu'un qui vient d'enterrer un proche.

### Les cinq réponses qui n'appartiennent qu'à Mongazi

Le compte qui encaisse · un n8n ailleurs, oui ou non · la commission SasPay ·
qui relit le deuil · le premier franc encaissé pour de vrai.

L'adresse : `malettre.nebula-agency.online` depuis le renommage du 2026-10-16
(`_memoire/decisions.md`), en attendant que Mongazi achète, ou non,
`malettre.app`.
