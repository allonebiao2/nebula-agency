# CLIENT 10 — HILLARY M. STYL

> **Maison de couture · prêt-à-porter & sur-mesure**
> Vitrine avec catalogue commandable et prise de mesures en ligne.
> Créé le 2026-07-31 · moteur de mesures refait (v2) · direction artistique « LE FIL » (v3, 2026-08-01)
> · **V4 « LA COUPE » en ligne, avec ses 4 vraies créations (2026-08-05/06)**.

---

## 1. Identité

| | |
|---|---|
| **Marque** | HILLARY M. STYL (monogramme **H.M.S**) |
| **Métier** | Couture : prêt-à-porter (par tailles) et sur-mesure (aux mesures du client) |
| **Cible** | Femmes et hommes, cérémonies et quotidien |
| **Logo** | Buste de mannequin ceint d'un ruban magenta + monogramme H.M.S |
| **Palette** | Magenta `#E6007E` · encre `#0B0A0C` · papier de patron `#F4F1EC` · rose pâle `#FFE9F5` |
| **Typographie** | **Bodoni Moda** (titres — le didone des magazines de mode) + Archivo (libellés) + Manrope (texte) |

---

## 2. Les fichiers, et lequel on modifie

| Fichier | Rôle |
|---|---|
| **`_vitrine_src.html`** | **La source. C'est celui-ci qu'on édite.** ≈70 Ko, lisible, avec des marqueurs `__LOGO_B64__` et `__FAVICON_B64__` à la place des images |
| `_build.py` | Injecte les images en base64 et écrit `vitrine.html` |
| `_qc.py` | La suite de contrôle qualité, **79 contrôles**, à passer avant tout déploiement (le nombre monte à chaque défaut corrigé) |
| `vitrine.html` | **Le livrable, généré. Ne jamais l'éditer à la main** : la prochaine construction écraserait la modification |

```bash
cd clients/10-hillary-m-styl
python3 _build.py     # source -> vitrine.html (174 Ko)
python3 _qc.py        # doit afficher « TOUT EST VERT »
```

Pourquoi ce détour : le logo pèse 75 Ko une fois en base64. Éditer directement le
livrable revient à travailler dans un fichier où le code utile est noyé — et à risquer
de dupliquer le logo, ce qui avait fait grimper une première version à 681 Ko.

---

## 3. Ce qui a été livré

**Un seul fichier de 174 Ko**, aucune dépendance externe hormis les polices Google.
Logo et favicon en base64, le logo déclaré **une seule fois** en variable CSS `--logo`.

### Les sections
1. **Héros** avec accueil personnalisé (bonjour / bon après-midi / bonsoir, et le prénom
   du visiteur s'il est déjà venu) et deux portes d'entrée : prêt-à-porter ou sur-mesure
2. **La maison** — quatre piliers : mesures par vêtement, retrait ou expédition,
   normal ou express, prévenu deux fois
3. **Catalogue à deux onglets** — prêt-à-porter et sur-mesure. **Le prix ET le délai de
   confection sont affichés sur chaque carte.** Deux colonnes sur mobile
4. **Comment ça se passe** — quatre étapes, dont la **double notification** (à la
   confirmation de la commande, puis quand la tenue est prête)
5. **À propos** — le métier de la maison
6. **L'atelier** — adresse, horaires, email, WhatsApp, retrait gratuit, règlement Momo

### Le tunnel de commande (le cœur du projet)

Une fiche s'ouvre au clic sur une pièce, avec quatre étapes puis l'envoi.

| Étape | Prêt-à-porter | Sur-mesure |
|---|---|---|
| **1** | Choix de la taille (XS → XXL) | **Formulaire de mesures propre au vêtement** (voir §4) |
| **2** | Retrait atelier (gratuit) ou expédition — **les frais s'affichent par pays** | idem |
| **3** | Délai **normal** ou **express (1 à 3 jours)** → **la date précise de disponibilité s'affiche** | idem |
| **4** | Coordonnées : WhatsApp **ou** email | idem |

Un **récapitulatif chiffré** se met à jour en direct (pièce + livraison + délai = total),
puis la commande part sur WhatsApp en message structuré, avec toutes les mesures.

---

## 4. Le moteur de mesures — ce qui a changé en v2

**Les mesures dépendent du type de vêtement, pas du genre du client.**
C'était l'erreur de la v1, qui demandait 8 mesures « femme » ou « homme ».
Une robe droite en demande 15, un pantalon 6.

| Type de vêtement | Mesures | Détail |
|---|---|---|
| **Robe coupée à la taille** | **9** | Épaules · Carrure devant · Poitrine · Tour de taille · Longueur taille · Longueur robe courte · Longueur robe longue · Tour de manche · Longueur manche |
| **Robe droite** | **15** | les 9 ci-dessus **+** Tour du sous-sein · Tour de ceinture · Tour de hanche · Longueur sous-sein · Longueur ceinture · Longueur genou |
| **Robe ovale** | **11** ⚠️ | **Liste proposée, à valider par l'atelier** (voir §6, point 7) |
| **Pantalon** | **6** | Tour de taille · Tour de bassins · Tour de cuisse · Tour de genoux · Longueur genou · Longueur pantalon |
| **Chemise ou haut** | **8** | Épaules · Carrure devant · Carrure dos · Tour de poitrine · Tour de taille · Longueur habit · Tour de manche · Longueur manche |

Les champs sont **regroupés** (Le haut · Les longueurs · Les manches) pour qu'on ne se
perde pas dans quinze cases identiques.

**Le message d'aide demandé, affiché au-dessus des mesures, mot pour mot :**
> « Vous pouvez prendre les mesures vous-même ou inviter quelqu'un à le faire pour vous
> ou vous aider. »

**Une mesure laissée vide n'est pas bloquante.** Elle part en « à prendre ensemble » et
le message indique combien il en manque. Il faut la moitié des mesures pour avancer :
un client qui ne sait pas mesurer son entrejambe ne doit pas abandonner sa commande,
mais un formulaire vide n'est pas une commande.

La pièce **« Création libre »** laisse le client choisir lui-même le type de vêtement,
et bascule alors sur le bon formulaire.

---

## 5. La date de disponibilité

Dès que le client a choisi son délai, la date exacte s'affiche en vert :

> **CHEZ VOUS AU PLUS TARD LE**
> vendredi 7 août
> *Confection incluse, plus 4 jours d'acheminement vers Côte d'Ivoire.*

Le libellé change selon le mode : « Prête à retirer au plus tard le » en cas de retrait.

**Le calcul est volontairement pessimiste.** La date est annoncée sur la **borne haute**
du délai, acheminement du pays compris. Promettre le jour 8 d'un « 8 à 14 jours »
fabrique un client déçu le jour 9. On promet 14, on livre 10, la cliente est contente.

| | Confection | Acheminement | Annoncé |
|---|---|---|---|
| Normal | borne haute de la pièce | jours du pays | somme des deux |
| Express | **1 à 3 jours** → 3 | jours du pays | somme des deux |

Le délai express affiche un avertissement honnête : il est confirmé par l'atelier à la
validation, et **si la charge du moment ne le permet pas, le supplément n'est pas dû**.

---

## 6. ⚠️ À CONFIRMER AVANT MISE EN LIGNE

**Rien de tout cela n'a été inventé : les valeurs en place sont des exemples clairement
marqués dans `_vitrine_src.html`, en haut du `<script>`, dans un bloc « ZONE À COMPLÉTER ».**

| # | Information | Pourquoi ça compte |
|---|---|---|
| 1 | ~~Numéro WhatsApp~~ ✅ **FOURNI le 2026-08-01 : +229 51 37 47 93** → `WHATSAPP = "22951374793"`. ⚠️ **Reste à tester en envoyant un vrai message sur le lien** avant diffusion (voir §6bis) | — |
| 2 | **Email de repli** (`EMAIL`) | Le client sans WhatsApp passe par là. Adresse d'exemple pour l'instant |
| 3 | **Frais d'expédition et jours d'acheminement par pays** (`PAYS`) | Valeurs provisoires. Un tarif faux coûte de l'argent à la cliente **à chaque commande**, et un acheminement faux fausse la date annoncée |
| 4 | **Délais de confection** (`DELAIS` et `jmin`/`jmax` de chaque pièce) | Normal 7-14 jours, express 1-3 : à valider avec l'atelier |
| 5 | ~~**Le catalogue** (`PIECES`)~~ ✅ **RÉGLÉ le 2026-08-06** : ses **4 vraies créations** (Robe de cérémonie, ensemble Mira, ensemble JOSY, Robe de ville) avec ses prix en FCFA/€/$, ses délais et **un supplément express propre à chaque pièce**. Détail : `_sources/hillary/PIECES-RECUES.md` |
| 6 | **Adresse, horaires de l'atelier** (`ATELIER`) | Affichent « à confirmer » |
| 7 | **Les mesures de la robe ovale** (`MESURES.robe_ovale`) | **Jamais fournies.** 11 mesures proposées par déduction, signalées en jaune dans l'interface : « Liste de mesures en cours de validation par l'atelier » |
| 8 | **Prix du supplément express** | 10 000 F par défaut |

### 6bis. ⚠️ Le format du numéro, à vérifier une fois

Mongazi a donné **+229 51 37 47 93**, soit 8 chiffres — le même format que son propre
numéro (`+229 96 74 07 32` → `wa.me/22996740732`, en production et fonctionnel).
Le lien posé est donc **`wa.me/22951374793`**, transcription littérale.

**Mais le dépôt contient les deux conventions** : les autres clients sont enregistrés en
10 chiffres avec le préfixe `01` (`wa.me/2290197085576`, `wa.me/2290167748955`), suite au
renumérotage béninois. **Rien n'a été deviné : le numéro est repris tel qu'il a été donné.**

**Le test, une fois, avant toute diffusion :** ouvrir `wa.me/22951374793` et envoyer un
vrai message. Si la conversation ne s'ouvre pas sur le bon contact, la variante à essayer
est **`2290151374793`** (préfixe `01`), et il suffit alors de changer `WHATSAPP` puis de
relancer `python3 _build.py`.

---

**Conseil photo à transmettre à la cliente :** dehors le matin ou en fin d'après-midi, à
l'ombre, sur un fond uni, la pièce portée ou sur mannequin. Format portrait (les cartes
sont en 3:4). C'est ce qui fera la différence entre un catalogue correct et un beau catalogue.

---

## 6ter. ✅ EN LIGNE — la V4, à jour

**✅ https://hillary-m-styl.pages.dev** — Cloudflare Pages, projet `hillary-m-styl`.
**Ce qui est en ligne est la V4 « LA COUPE »**, avec ses quatre vraies créations
(dernier déploiement : 2026-08-06).

*Historique : la V2 sans direction artistique est restée en ligne du 1er au 2 août ;
la V3 « LE FIL » l'a remplacée le 2 août ; la V4 s'est posée dessus le 5-6 août.
Les avertissements « la V3 doit remplacer l'ancienne » que vous croiseriez encore
plus bas dans ce fichier sont périmés.*

### Ce que l'autre session a apporté, et qui est conservé ici

| Apport | Où il vit maintenant |
|---|---|
| Le vrai numéro WhatsApp `22951374793` | dans `_vitrine_src.html` |
| « Retrait sur rendez-vous · le point de retrait vous est donné sur WhatsApp » | idem — **remplace « adresse à confirmer »** |
| La carte « Horaires » devenue **« Confection »** avec les délais | idem |
| Ces valeurs **écrites en dur dans le HTML**, pas seulement injectées par le JS | idem — sinon le visiteur voit « — » le temps du script |
| Affiche A4 + 2 QR (site et WhatsApp pré-rempli) | `assets/docs/` — **toujours valables**, l'adresse n'a pas changé |
| `og:url` + `canonical` | ✅ **présents dans `_vitrine_src.html`** depuis la V3 |

### ⚠️ Un piège pour la prochaine session

**`_outils/_apply_infos.py` est OBSOLÈTE.** Il patchait `vitrine.html` directement, ce qui
est incompatible avec la chaîne `_v4/ → _assembler.py → _vitrine_src.html → _build.py →
vitrine.html`. Les vraies valeurs sont désormais **dans la source**. Ne pas le relancer :
il écraserait le travail.

### Le redéploiement

⚠️ **Passer par `_predeploy.py`** : il vérifie la version, construit, lance le contrôle
qualité, refuse s'il reste un texte d'attente sur la page publique, copie les images,
**écrit la page 404** et prépare `_dist/`.

```bash
cd clients/10-hillary-m-styl
python _v4/_assembler.py && python _build.py     # si on a touché à _v4/
python _predeploy.py                             # tout est vérifié ici
npx -y wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main
```
Identifiants dans `secrets/cloudflare.env`. Contrôle : la page doit afficher Bodoni Moda
et le rideau d'ouverture.

---

## 7. Les limites honnêtes du statique

Deux demandes ne peuvent pas être tenues par un fichier HTML seul. Elles sont
**préparées** dans la vitrine, mais elles demandent la couche automatisation :

| Demande | Où on en est |
|---|---|
| **Paiement Mobile Money** | La vitrine dit clairement « règlement par Mobile Money, le numéro vous sera communiqué à la confirmation ». Aucun paiement ne transite par le site. Un vrai encaissement en ligne passe par **FedaPay** (clé publique côté client, clé secrète côté n8n) |
| **Notification automatique du client** | Les deux messages (confirmation, puis « c'est prêt ») sont aujourd'hui envoyés à la main. L'automatisation, c'est **n8n + Twilio WhatsApp**, avec la commande enregistrée en base |

C'est exactement l'escalier NEBULA : la vitrine d'abord, l'outil ensuite.

---

---

## 8. La direction artistique — « LE FIL »

**Le problème de la v2 :** elle était correcte, pas mémorable. Une vitrine à 100 000 €
n'a pas *plus d'animations* — elle a **une idée**, et tout en découle.

**L'idée :** une maison de couture, c'est un fil qui va du mètre-ruban au vêtement fini.
Le site est ce fil qu'on tire. Chaque section a **sa propre animation signature**, et
toutes sont tirées du métier — jamais un effet décoratif posé par-dessus.

| | Section | La signature | Ce qu'elle raconte |
|---|---|---|---|
| — | **Ouverture** | Le fil descend, le monogramme apparaît, deux pans de tissu s'écartent | On entre dans l'atelier |
| — | **Héros** | Titre à la craie ligne par ligne · **le croquis de la robe se dessine** (grand écran) · mètre-ruban gradué en bas · nappes de lumière qui respirent | Le dessin avant le vêtement |
| 01 | **La maison** | **La piqûre** : un point de couture se coud d'un pilier à l'autre au défilement, l'aiguille suit | La couture qui avance |
| 02 | **Catalogue** | **Le patron à la craie** : un contour pointillé se trace autour de chaque pièce, en cascade | La coupe avant la couture |
| 03 | **La méthode** | **Le fil qui relie** les quatre étapes, la perle progresse avec le défilement | De la commande à l'essayage |
| 04 | **À propos** | **Le drapé** : le texte se dévoile par plis successifs · les chiffres se comptent | Le tissu qui tombe |
| 05 | **L'atelier** | **La coupe** : une ligne de coupe pointillée traverse, **les ciseaux la suivent**, le titre se révèle derrière | Les ciseaux entrent en jeu |
| — | **Modale** | Le carnet se lève, les champs de mesure se posent un à un, **la date se tamponne** | Le carnet de l'atelier |

**Le détail permanent :** grain de toile sur toute la page · fil de progression magenta en
haut · **l'aiguille** en guise de curseur sur ordinateur, aimantée par les boutons ·
ruban défilant · barre transparente sur le héros qui se pose sur fond papier ensuite.

**Ce qui a été refusé :** des photos générées pour le catalogue. Un client qui commande
« Robe Amazone » sur une photo d'IA d'une robe que l'atelier ne fait pas, c'est une
promesse fausse. Les cartes portent un visuel de substitution marqué « photo à venir »,
et le héros est **construit pour recevoir une vraie photo** le jour où elle existe.

**Trois garde-fous techniques :**
- `prefers-reduced-motion` respecté : tout s'arrête pour qui en a besoin
- sur téléphone, le grain ne s'anime plus et la troisième nappe de lumière est retirée —
  la texture reste, le coût en images par seconde disparaît
- **aucune animation infinie sous un `backdrop-filter`** (leçon Boussole) : un contrôle
  automatique le vérifie à chaque passage de QC

## 8bis. Le toucher et la vie du catalogue (V3.1 — 2026-08-01)

Demandé par Mongazi : de meilleures réactions au toucher, une animation par section
**et par étape**, le catalogue « manque de vie », tout le reste conservé.

### Le toucher — partout, en une seule écoute déléguée
| | |
|---|---|
| **L'enfoncement** | tout ce qui se touche s'enfonce (`scale(.972)`), avec un ressort |
| **L'onde** | une lueur magenta naît **au point exact touché** et se dilate. Claire sur les fonds magenta, magenta sur les fonds clairs |
| **La vibration** | `navigator.vibrate(9)` — **Android uniquement**, iOS ne l'expose pas dans Safari. Seulement sur un **choix** (option, taille, carte, valider), **jamais au défilement** : une vibration à chaque geste fait désinstaller une application |

⚠️ **Une seule écoute `pointerdown` déléguée sur `document`.** Les cartes et les options
sont recréées à chaque rendu : un écouteur par élément fuirait à chaque changement d'onglet.

### 02 · Le catalogue — les échantillons qu'on pose
C'était la section la plus importante commercialement et la plus sage. Elle a maintenant :
- **les cartes se posent de travers** (±1,6°) et se redressent, comme des coupons de tissu
  qu'on aligne sur la table — 6 inclinaisons différentes en rotation
- **au doigt : la lumière balaie le tissu** et **la craie se retrace** autour de la pièce
- **au changement d'onglet, la table se vide** avant qu'on repose. Avant, c'était un
  remplacement instantané — c'est précisément ce qui faisait « sage »

⚠️ Le balayage lumineux **ne tourne pas en boucle** : il se déclenche au toucher. Une
animation infinie sur douze cartes coûte cher sur un téléphone d'entrée de gamme.

### Le tunnel — une animation par étape
| Étape | La signature |
|---|---|
| 1 · mesures | **le carnet qui s'ouvre** — les champs pivotent depuis leur bord haut |
| 1 · tailles | **les étiquettes qu'on pose**, en cascade |
| 2 · livraison | **la carte qui se déplie**, depuis le bord gauche |
| 3 · délai | **le sablier** — le choix se remplit de haut en bas |
| 4 · coordonnées | **l'étiquette qu'on coud** — les champs entrent en piquant |

### Trois pièges rencontrés, et leur correction
1. **Le pivot 3D des champs passait au-dessus du pied de la modale** et bloquait le bouton
   « Continuer ». Un `transform` 3D crée son propre plan d'empilement : `.sh-ft` a reçu
   `z-index:6`, `.sh-bd` `z-index:1`.
2. **Le QC mesurait pendant les animations** : un champ en cours de pivot fait 39 px de haut
   au lieu de 52. On attend 900 ms avant de mesurer les cibles tactiles.
3. **`wait_until="networkidle"` ne se stabilise jamais** quand la feuille Google Fonts pend —
   et une feuille externe qui pend bloque `DOMContentLoaded`. Le QC **coupe les polices
   externes** (`ctx.route('**fonts.g*/**', abort)`) : il teste la page, pas le CDN.

---

## 9. Vérifications passées — `python _qc.py`, tous les contrôles verts

- **Aucun débordement horizontal** sur 390 px, 768 px et 1440 px, page et modale ouverte
- **Toutes les cibles tactiles ≥ 44 px** (y compris le logo de la barre et les liens du pied)
- **Aucune erreur JavaScript**, aucune ressource locale manquante
- **Aucune image externe** : logo et favicon en base64, zéro dépendance qui puisse casser
- Nombre de mesures vérifié pour les 5 types : **9 / 15 / 11 / 6 / 8**, sans identifiant en double
- Tunnel prêt-à-porter : robe 35 000 + Côte d'Ivoire 12 000 + express 10 000 = **57 000 F** ✅
  date annoncée à **J+7** (3 jours express + 4 d'acheminement) ✅
- Tunnel sur-mesure : pantalon, retrait atelier, délai normal → **30 000 F**, date à J+10,
  libellé « prête à retirer » ✅, **4 mesures sur 6 suffisent** pour avancer ✅,
  les 2 manquantes apparaissent en « à prendre ensemble » dans le message ✅
- **Email seul** (sans WhatsApp) accepté à l'étape 4 ✅
- Pièce sans prix : total « sur devis » de bout en bout ✅
- Robe ovale : l'avertissement de validation s'affiche ✅
- **Le rideau d'ouverture se retire du DOM** : il ne bloque aucun clic ✅
- Les **5 signatures de section** se déclenchent bien au défilement ✅
- **Aucune animation infinie sous un `backdrop-filter`** ✅

---

## 10. Reste à faire

- [ ] Récupérer les 8 informations du §6 — **le numéro WhatsApp d'abord**
- [ ] Faire valider les mesures de la **robe ovale** par l'atelier
- [ ] Intégrer les vraies pièces, prix et photos
- [ ] Générer le **QR code** et l'affiche A4
- [ ] Déployer sur Cloudflare Pages (projet `hillary-m-styl`)
- [ ] Fiche Google Business et avis clients
- [ ] **Tester `wa.me/22951374793`** en envoyant un vrai message (voir §6bis — deux formats possibles)

---

## 11. Offre NEBULA correspondante

Ce projet dépasse le **Catalogue Digital** simple : il embarque un moteur de commande avec
prise de mesures par type de vêtement, calcul de frais par pays et date de disponibilité.
Il se situe entre le Catalogue à 50 000 F et l'**Outil Digital sur mesure**. À chiffrer
avec le configurateur du site (`www.nebula-agency.online`) plutôt qu'au forfait catalogue.

Références de méthode : `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md` (prix et
règles) et `_documents/nebula-agency/vente/05-GUIDE-OUTIL-METIER.md` (cadrage).

---

*NEBULA Agency · Cotonou*


---

## 7. V3 « LE FIL » — déployée le 2026-08-02

La vitrine mise en ligne le 1er août a été remplacée par la **V3**, bâtie sur le standard
« 100 000 € » (`_memoire/procedure-vitrine/DIRECTION-ARTISTIQUE.md`, dont ce dossier est la
**référence d'exécution**).

Ce qui la distingue, et ce qu'il faut voir sur un téléphone pour savoir qu'on est bien
dessus : le **rideau qui s'ouvre** au chargement (un fil descend, deux pans s'écartent), les
**titres en Bodoni Moda** (serif fin à déliés très contrastés), et les **cartes qui
s'enfoncent** sous le doigt avec une lueur.

⚠️ **La source est `_vitrine_src.html`. `vitrine.html` est GÉNÉRÉ, ne jamais l'éditer à la
main.** Chaîne : `_build.py` (injecte logo et favicon en base64) → `_qc.py` →
`_predeploy.py` (enchaîne tout et prépare `_dist/`).

⚠️ `_outils/_apply_infos.py` est **OBSOLÈTE** : il patchait le livrable directement, ce qui
écraserait la V3.

**Déploiement :** `python _predeploy.py` puis
`npx wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main`.
Contrôle en une commande : `grep -c "Bodoni Moda" vitrine.html` doit valoir au moins 1.

---

## 11. V4 « LA COUPE » — ses vraies créations, détourées (2026-08-05/06)

### La chaîne de construction a changé

La V4 se monte à partir de **huit morceaux** dans `_v4/`, et non plus en éditant
le HTML à la main :

```bash
python _v4/_assembler.py    # _v4/*  ->  _vitrine_src.html
python _build.py            # images en base64 -> vitrine.html
python _qc.py               # 79 contrôles, « TOUT EST VERT » obligatoire
python _predeploy.py        # vérifie tout et prépare _dist/ (+ la page 404)
```

⚠️ **`_v4/garde-moteur.js`, `garde-modale.html`, `garde-css-*.css` ne sont JAMAIS
régénérés** : ils portent le moteur de commande, qui marche. L'assembleur **refuse
d'écrire** si l'un des 18 identifiants dont le moteur a besoin manque du balisage.
C'est ce qui permet de refondre l'apparence sans casser les commandes.

### Ses quatre pièces réelles

| Pièce | Prix | Express | Supplément | Mesures |
|---|---|---|---|---|
| Robe de cérémonie | 100 000 F · 150 € · 180 $ | 140 000 F, 2 à 4 j | **+40 000** | robe ovale |
| L'ensemble Mira | 50 000 F · 75 € · 90 $ | 75 000 F, 2 à 4 j | **+25 000** | robe ovale |
| Ensemble JOSY | 65 000 F · 100 € · 117 $ | 85 000 F, 2 à 5 j | **+20 000** | robe ovale |
| Robe de ville | 30 000 F · 45 € · 67 $ | 45 000 F, 2 à 4 j | **+15 000** | robe ovale |

⚠️ **Le supplément express est propre à chaque pièce.** Le moteur appliquait
10 000 F à tout le monde : une cliente voyait 110 000 F au lieu de 140 000 F, et
c'est Hillary qui absorbait l'écart. Corrigé par `supExpress(p)`.

⚠️ **Ses prix en trois monnaies ne sont pas des conversions** et ne sont pas
cohérents entre eux (30 000 F = 45 € mais 67 $). Ce sont **ses** prix : on les
affiche tels quels, on ne les recalcule jamais.

⚠️ Ses quatre pièces sont toutes en **sur-mesure**. L'onglet « prêt-à-porter » est
donc vide, et il **se masque tout seul** (`compteCat`, `premiereCatPleine`) : sans
ça, le catalogue s'ouvrait sur un onglet vide.

### Les images

**Tout ce qui montre un vêtement est une VRAIE photo d'Hillary**, détourée :
héros, carrousel et cartes du catalogue partagent les fichiers
`piece-{ceremonie,mira,josy,ville}.webp` (une seule photo par pièce, pas de
doublon). Les images générées ne servent plus qu'à l'ambiance — l'atelier et le
lookbook — et elles sont construites **d'après ses quatre tissus**.

Détourage : `rembg` / `isnet-general-use` **sans `alpha_matting`** (1,9 Go de RAM
et ça tombe), puis seuil alpha, érosion, flou léger et décontamination des bords.
Sortie **WebP `quality=94, alpha_quality=100, exact=True`** : alpha **bit pour bit
celui du PNG**, pour 761 Ko au lieu de 3 560 Ko. Sources PNG dans
`_sources/detoure/`.

### La couleur du héros suit le tissu

La teinte dominante de chaque pièce est relevée sur sa photo (histogramme de
teintes sur les pixels saturés, pas une moyenne — bleu + rouge donnait du violet)
et pilote la nappe de fond, le trait sous le titre et le chiffre géant.

⚠️ **`--piece` vit sur `:root`. Ne jamais la redéclarer sur `.hero`** : une
déclaration locale l'emporte, et le script n'a plus aucun effet.

### Ce que le contrôle qualité surveille maintenant, en plus

- les images du héros et du catalogue **portent un alpha réellement transparent**,
  lu au pixel ;
- **aucun fond opaque ni bordure** autour des pièces ;
- **prix et délais tiennent sur une seule ligne** aux trois largeurs ;
- **une page `404.html`** est écrite à chaque préparation de déploiement : sans
  elle, un fichier absent répond 200 et ce 200 se met en cache un an.


---

## VAGUE DU 2026-08-10 — quatre modèles reçus, et un problème de nom

### ⚠️ « Robe de ville » est sa CATÉGORIE, pas un nom de pièce

Mongazi a envoyé quatre modèles en paires (face et dos). **Les quatre portent le
même nom : « Robe de ville ».** Avec celle déjà en ligne, cela fait **cinq**.

Le problème est concret : **la commande WhatsApp qu'Hillary reçoit contient le
nom de la pièce.** Cinq pièces homonymes, et elle ne peut pas savoir laquelle
coudre.

**Noms PROVISOIRES posés**, factuels, tirés de ce que montre la photo :

| id | Nom provisoire | Prix | Express | Mesures |
|---|---|---|---|---|
| h4 | Robe de ville **bleue** | 30 000 F · 45 € · ⚠️67 $ | 45 000 F | robe ovale |
| h5 | Robe de ville **violette** | 40 000 F · 60 € · 72 $ | 55 000 F · 82 € · 100 $ | **haut + pantalon** |
| h6 | Robe de ville **orange** | 35 000 F · 52 € · 63 $ | 45 000 F · 67 € · 81 $ | robe ovale |
| h7 | Robe de ville **verte** | 35 000 F · 52 € · 63 $ | 45 000 F · 67 € · 81 $ | robe ovale |
| h8 | Robe de ville **à tulle** | 35 000 F · 52 € · 63 $ | 45 000 F · 67 € · 81 $ | **haut + pantalon** |

⚠️ **h4 a été RENOMMÉE** de « Robe de ville » à « Robe de ville bleue ». C'était
déjà un nom que **nous** avions donné, signalé comme à confirmer depuis le
2026-08-06. À côté de « Robe de ville verte », le nom nu devenait illisible.

⚠️ **Deux pièces sont violettes** : le seul descripteur de couleur ne suffisait
plus, d'où « à tulle » pour la seconde, son détail le plus visible.

⏳ **À obtenir d'Hillary : ses vrais noms.** Une ligne chacune, et on remplace.

### Le prix en dollar de la robe bleue est douteux

Tous les prix du site suivent **667 F par euro** et **556 F par dollar**, y
compris les quatre reçus le 2026-08-10, qui le confirment.

**Sauf h4 : 30 000 F affichés 67 $**, soit 448 F par dollar, un écart de +24 %.
Et **67 est exactement le prix express en euro de cette même pièce**. La valeur
a probablement glissé d'une case à l'autre le 2026-08-06.

Au taux du site, ce serait **54 $**. ⛔ **Non corrigé** : ses prix sont les
siens, on ne les recalcule jamais. À trancher avec elle.

### Un jeu de mesures neuf : `haut_pantalon`

Hillary demande mot pour mot « **ceux d'un pantalon et un haut** » pour deux des
robes (le buste ajusté monté sur une jupe ample). C'est donc l'**union exacte**
des deux jeux existants, **sans rien réinterpréter**, moins le tour de taille
qui figurait dans les deux : **13 mesures**.

⚠️ Marqué `aValider: true`, comme la robe ovale.
⚠️ **« Longueur pantalon » sur une robe se lit mal** pour une cliente : à faire
reformuler par l'atelier.

### La seconde photo sert à quelque chose

Chaque nouvelle pièce a deux vues. La seconde (`img2`) s'affiche **dans la fiche
de commande, à l'étape des mesures** : c'est là que la cliente a besoin de voir
comment la pièce est bâtie derrière (un laçage, un dos nu, un volant). Elle est
contenue à 78 px de large : une photo pleine largeur pousserait le formulaire
hors de l'écran.

### Ce que le traitement des photos a appris

⚠️ **Le repérage automatique face / dos s'est trompé sur deux paires sur
quatre.** L'heuristique comptait les pixels de peau dans le tiers supérieur :
une vue de dos épaules nues en contient autant qu'un visage. **Remède : monter
une planche des sources et REGARDER**, ce qui a pris trente secondes.

⚠️ **On calibre en HAUTEUR, jamais en largeur.** À 1 100 px de large, la robe
verte faisait 2 475 px de haut pour **689 Ko**. Les quatre pièces déjà en ligne
font toutes **950 px de haut** pour 94 Ko de moyenne : c'est le standard.
Les nouvelles font 84 à 195 Ko. Et **on n'agrandit jamais** au-delà de la source.

### Observation sur une pièce ancienne

**La photo principale de la robe bleue (h4) est une vue de DOS.** C'est
antérieur à cette vague, mais ça saute aux yeux maintenant que les autres
pièces ont une face. À vérifier avec Hillary : a-t-elle une photo de face ?

### Les scripts

- `_detourer.py` — détoure les paires avec rembg/isnet, recadre en hauteur,
  livre en WebP `quality=94, alpha_quality=100, exact=True`, et **mesure la
  proportion de matière** pour repérer un détourage raté.
- Sources dans `_sources/modele-*/face|dos`, PNG maîtres dans
  `_sources/detoure/`. Le tout est **hors Git** (`clients/*/_sources/`).


---

## LES SONS D'ATELIER — 2026-08-11

**Direction : « atelier réel »**, choisie par Mongazi. On entend l'acier, le
tissu, la machine. Hillary vend du fait-main : un son trop poli dirait le
contraire.

**Six sons, pas quatorze.** Ceux qui portent le sens. Un site où chaque geste
sonne devient fatigant en deux minutes, et on peut toujours en ajouter, jamais
retirer une habitude.

| Son | Ce que c'est | Quand |
|---|---|---|
| `ouvrir` | deux lames de ciseaux qui s'écartent | le rideau se fend |
| `fiche` | le tissu qu'on soulève | on ouvre une pièce |
| `mesure` | le claquement du mètre-ruban | on entre une mesure |
| `etape` | trois points de machine à coudre | on passe à l'étape suivante |
| `couper` | le coup de ciseaux dans le tissu | on valide la commande |
| `envoyer` | le fil qu'on noue | la commande part sur WhatsApp |

Générés avec **WaveSpeed** (`mirelo-ai/sfx-1.6`, `ambience: false`), **0,06 $**
au total, **18,6 Ko** pour les six. Scripts : `_sons.py` puis `_sons_finir.py`.

### Cinq pièges rencontrés, tous mesurés

1. **`loudnorm` ne marche pas sous quelques secondes.** La mesure EBU R128 a
   besoin de matière : sur un extrait de 70 ms elle ne rend RIEN. Cinq sons sur
   six sont sortis muets. On normalise **au pic**, ce qui marche à toute durée.
2. **⛔ `-ss` APRÈS `-i` laisse le graphe de filtres sur la timeline du fichier
   entier.** `afade=t=out:st=0.27` éteignait le son à 270 ms du début du
   source, alors que le coup de ciseaux était à 680 ms : trois sons sortaient
   parfaitement muets, **avec un poids normal**. Placé avant `-i`, la coupe
   tombe sur la trame MP3 la plus proche et l'attaque se décale.
   **Remède : couper sur les ÉCHANTILLONS, en Python.** Plus aucune
   approximation.
3. **Le MP3 a un délai d'encodage d'environ 30 ms** : un extrait de 70 ms est
   presque entièrement mangé. Durée minimale de 300 ms, obtenue en prolongeant
   **la queue**, jamais le début (la latence au clic doit rester nulle).
4. **On ne coupe pas au premier bruit.** Les fichiers générés contiennent
   souvent un blip discret, un silence, puis le vrai son. On part du **pic** et
   on remonte, en tolérant les micro-creux.
5. **`fetch` est bloqué depuis une page ouverte en `file://`.** Le QC voyait
   zéro son et accusait le site à tort : le contrôle se fait désormais **en
   HTTP**, comme la page tourne vraiment.

### Ce qui est vérifié, et comment

Aucun son n'est ni écouté ni jugé de confiance. On mesure : **pic et RMS**
(audible ou muet), **facteur de crête** (une attaque nette est au-dessus de 6 ;
les six sont entre 10 et 19), **position de l'attaque** (0 à 10 %, sauf la
machine à coudre à 30 %, ce qui est correct : c'est son quatrième point qui est
le plus fort), et **profil spectral** deux à deux pour qu'aucun son ne soit le
jumeau d'un autre.

### Les garde-fous

- **Rien ne sonne avant un geste.** Conséquence assumée : à la toute première
  visite, le rideau est muet. Aucun navigateur n'autorise autre chose.
- **Silence d'amorçage iOS**, sinon la sortie ne s'ouvre jamais.
- **Compresseur**, et **gain relevé de 60 % sur téléphone**.
- **Volume à 0,30** : un son d'interface se sent plus qu'il ne s'écoute.
- **Verrou de 60 ms par son** : sur un clic rapide, dix déclenchements empilés
  font une bouillie.
- **Bouton de coupure en bas à gauche, en z-index 130**, donc **au-dessus de la
  fiche** : en dessous, il devenait inatteignable dès qu'une fiche s'ouvrait et
  le son ne pouvait plus être coupé pendant la commande. Le choix est retenu.

⚠️ **`_predeploy.py` ne copiait pas les sons.** La page les aurait demandés,
Cloudflare aurait répondu 404, et le site serait parti muet sans que rien ne le
signale. Corrigé, et le script **refuse maintenant de publier** si un son
référencé manque.

---

## LE PANIER (2026-08-16)

Demandé par Mongazi : « un panier comme pour madame Luxury, histoire que les
clientes voient ce qu'elles commandent et les prix ».

**Avant**, une cliente qui voulait deux robes envoyait deux messages WhatsApp.
L'atelier recevait deux commandes sans savoir qu'elles allaient ensemble : même
cliente, une seule livraison, un seul règlement.

**Le parcours, maintenant** : on ouvre une pièce, on donne ses mesures, on
choisit son délai, elle tombe dans le panier. Le tiroir montre chaque ligne
(photo, mesures renseignées, délai, prix), on peut changer la quantité,
**modifier** une ligne ou la retirer. Puis une seule commande : livraison,
coordonnées, récapitulatif, un seul message WhatsApp.

### Les calculs, et pourquoi ils sont ainsi

| Ce qui est calculé | La règle |
|---|---|
| Prix d'une ligne | `expPrix` si express, sinon `prix`, **fois la quantité** |
| Sous-total | la somme des lignes |
| Total | sous-total **+ frais de livraison une seule fois** |
| € et $ | la somme de SES valeurs, jamais un taux de change |
| Délai | **la borne haute de la pièce la plus lente**, plus l'acheminement |

⚠️ **Le délai d'une commande est celui de sa pièce la plus lente.** Tout part
ensemble. Annoncer la plus rapide fabriquerait une cliente déçue. Quand le
panier mélange une pièce express et une pièce normale, l'écran le dit et propose
deux envois séparés.

⚠️ **Aucun prix n'est stocké dans le panier**, seulement l'identifiant de la
pièce et les choix. Un panier oublié une semaine dans le navigateur ne peut donc
pas ressortir avec un prix périmé.

✅ **Les mesures déjà données se reportent** d'une pièce à l'autre quand le
champ existe dans les deux jeux : une cliente ne remesure pas son tour de taille
pour la deuxième robe.

### Deux défauts trouvés en construisant, et corrigés

- ⛔ **Le voile du panier avalait les clics pendant 350 ms après sa fermeture.**
  `visibility` ne se dégrade pas en douceur, elle bascule à la FIN de la
  transition. C'est `pointer-events` qui règle ça, immédiatement.
- ⛔ **Le bouton du son se posait sur « Retour » et sur « Vider le panier »**
  (il est en `position:fixed` en bas à gauche). Le cacher aurait été plus
  simple, mais **une règle de la maison veut qu'il reste atteignable** quand une
  fiche est ouverte : le contrôle qualité l'a refusé. On lui réserve donc un
  couloir de 78 px dans les deux pieds de page.

### Ce qu'il faut savoir pour y toucher

- Tout est dans `_v4/garde-moteur.js` (le panier, les deux parcours, le
  message), le balisage du tiroir dans `_v4/garde-modale.html`, ses styles à la
  fin de `_v4/garde-css-modale.css`, le bouton dans `_v4/markup.html`.
- ⚠️ **`_predeploy.py` ne lance PAS l'assembleur.** Après une modification de
  `_v4/*`, il faut `python _v4/_assembler.py` d'abord, sinon on contrôle et on
  publie l'ancienne version.
- Les animations par étape sont écrites dans la feuille de style par numéro
  (`[data-e="1"]`…). Les deux parcours gardent le sens d'origine :
  **1 mesures · 2 livraison · 3 délai · 4 coordonnées · 5 envoi**.
- Contrôle qualité : **108 contrôles**, dont ceux du panier (somme des lignes,
  délai de la pièce la plus lente, quantité, retrait d'une ligne, survie au
  rechargement).

