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

---

## CE QUI FAIT VENDRE, ET QUI MANQUAIT (2026-08-16)

Trois défauts trouvés en auditant la vitrine. **Aucun ne se voyait en regardant
le site** : c'est ce qui les rendait durables.

### 1 · ⛔ Le lien partagé sur WhatsApp n'avait aucune image

Le site n'avait **aucune `og:image`**. Au Bénin, tout circule par WhatsApp : la
maison apparaissait comme une ligne de texte grise dans une conversation, à côté
de liens qui, eux, montrent une photo. C'est le défaut le plus coûteux
commercialement qu'un site puisse avoir.

`python _og.py` fabrique `assets/images/og.jpg` (1200x630, 87 Ko) : **sa vraie
robe de cérémonie détourée**, son encre, son magenta, son nom en Bodoni.
⚠️ **En JPEG, pas en WebP** : l'aperçu WhatsApp ne lit pas toujours le WebP.
⚠️ `_predeploy.py` ne copiait que les `.webp` : il copie maintenant **tout ce que
la page réclame**, sinon l'image restait sur le disque.

### 2 · ⛔ Un `FAQPage` déclaré, aucune question visible

Le JSON-LD annonçait une FAQ à Google alors que **la page n'en portait aucune**.
C'est contraire aux règles de Google (le contenu balisé doit être visible), et
surtout : les six objections que se pose une cliente n'étaient répondues nulle
part. Pire, les réponses balisées annonçaient **« 7 à 14 jours »** contre
« 2 semaines » sur chaque carte : la même contradiction que celle corrigée le
2026-08-06 ailleurs sur le site.

Il y a maintenant une **section « Les questions »** (`#questions`, en `<details>`,
donc lisible sans JavaScript et au clavier), et le JSON-LD dit **exactement** la
même chose. ⚠️ **Un contrôle automatique compare les deux** : question par
question, et vérifie que chaque réponse balisée est visible sur la page. Ils ne
peuvent plus diverger en silence.

### 3 · ⛔ Aucun balisage produit, alors que les prix sont réels

Les 8 pièces chiffrées sont maintenant balisées en `Product` + `Offer`
(prix, `XOF`, `MadeToOrder`, photo). ⚠️ **Les fiches sont LUES dans `PIECES`**
par l'assembleur, jamais recopiées : un prix écrit à deux endroits finit
toujours par diverger. Un contrôle vérifie que chaque fiche porte le prix du
catalogue.

### Et le reste

`robots.txt` et `sitemap.xml` sont écrits par `_predeploy.py`, comme le
`404.html`. Vérifié en ligne : `200` sur les trois, `404` sur une page
inexistante, `image/jpeg` sur l'image de partage.

**Le contrôle qualité passe de 84 à 120 contrôles** (le panier, puis cette
couche commerciale).

---

## LE HÉROS COMPLÉTÉ ET UNE SIGNATURE PAR SECTION (2026-08-17)

Mongazi : « complète le héros en mettant juste les meilleures, dans le même
style que ceux déjà présents » et « ajoute des animations différentes pour
chaque autre section ».

### Le héros montrait 4 pièces sur 8

Les quatre pièces reçues le 2026-08-10 (violette, Naja orange, verte, tulle)
n'étaient **jamais passées au héros ni au carrousel**. Corrigé :

- **héros : 4 → 7** (violette, Naja, verte ajoutées). La robe **à tulle est
  restée au seul carrousel** : son violet doublait celui de la robe de
  cérémonie violette, et deux nappes identiques qui se suivent ne se voient pas.
- **carrousel : 4 → 8** (les huit vraies pièces).
- ⚠️ Les nouvelles diapositives pointent sur **`piece-*.webp`**, pas sur un
  `hero-*.webp` : c'est la **même photo détourée**, en 950 px de haut. La
  réencoder en WebP une seconde fois ne ferait que la dégrader.
- Leur **teinte** est relevée sur le tissu comme pour les autres
  (`_v4/_couleurs.json`) : violette `#6b3065`, Naja `#925437`, verte `#7e6730`.
  ⚠️ Le seuil de saturation à 0,35 écartait le **fond sauge** de la robe verte :
  il ne restait que ses rubans ocre et sa nappe tombait sur celle de l'orange.
  À 0,22 on garde les tissus sourds, qui sont aussi des couleurs.
- Le compteur de secours du markup passe à `01 — 07` (c'est celui que voit
  quelqu'un sans JavaScript).

### Cinq sections partageaient la même révélation

La règle de la maison est **une signature différente par section**, et cinq
blocs partageaient le même `translateY(24px)` + fondu. Chacun a maintenant la
sienne, tirée d'un geste de couture :

| Section | La signature |
|---|---|
| 01 la maison | **l'ourlet qu'on déroule** : les piliers se découvrent de gauche à droite (`clip-path`) |
| 02 les collections | **le portant** : le bloc glisse comme un cintre poussé sur la tringle, avec un balancement très court |
| 03 le catalogue | **les patrons qu'on épingle** : chaque carte pivote autour de son coin haut-gauche jusqu'à son inclinaison |
| 04 les questions | **le fil qui se dénoue** : un fil descend le long de la liste, les questions se posent l'une après l'autre |
| 05 le contact | **la couture qui se ferme** : les quatre accès se rapprochent par paires, le point se pique au milieu |

⚠️ **`#grille` et `.faq-l` ont été ajoutés à la liste balayée** dans
`motion.js` : sans ça, ils n'auraient jamais reçu la classe `vu` et leur
animation n'aurait jamais joué.

⚠️ **`section{overflow-x:clip}` a été ajouté** en même temps. Deux de ces
animations viennent du côté : une révélation qui part de la droite **pousse la
page tant qu'elle n'a pas joué**, et personne ne le voit en regardant l'écran.
C'est exactement le défaut de 6 px trouvé sur le site de l'agence.

### ⚠️ Un piège de déploiement, vérifié à mes dépens

**Quand le contrôle qualité échoue, `_predeploy.py` s'arrête AVANT de préparer
`_dist/`.** Déployer juste après publie donc **la version précédente**, sans
aucun message d'erreur. C'est arrivé ici : le site est parti avec la FAQ mais
sans le nouveau héros. Vérifié en ligne, redéployé, revérifié.

⚠️ Et un contrôle **échoue par intermittence** (une fois sur deux environ) :
il est passé vert deux fois de suite juste après. À identifier : un contrôle qui
échoue au hasard est pire qu'un contrôle absent.

---

## LES 11 MODÈLES POSÉS SANS LEURS PHOTOS (2026-08-18)

Mongazi, après avoir compris que les photos n'arriveraient pas tout de suite :
« mets-les déjà sur la vitrine ». Décision assumée, exécutée.

**Le catalogue passe de 9 à 20 cartes.** Les 11 nouvelles portent tout sauf
l'image : nom, description, **prix en trois monnaies**, délai, type de mesures,
et la commande fonctionne de bout en bout (mesures, délai, panier, WhatsApp).

⚠️ **Le libellé est `Photo sur WhatsApp`, pas « photo à venir ».** La différence
n'est pas cosmétique : « à venir » dit à la cliente que la maison n'est pas
prête, « sur WhatsApp » est **vrai et actionnable**, et ça l'envoie là où elle
commande de toute façon. Le drapeau est `photoWa:true` dans `PIECES`.

⚠️ **Elles n'entrent ni au héros ni au carrousel.** Un monogramme en pleine page
ne montre rien : ces deux surfaces vivent de la photo. Le héros reste à 7, le
carrousel à 8.

⚠️ **Ce n'est pas l'état final et il ne faut pas s'y habituer.** Onze cartes sans
photo à la suite, ça se voit. `python _nouveaux_modeles.py --poser` posera les
images et retirera le drapeau dès que les fichiers seront là.

Contrôlé : **121 contrôles verts**, 0 erreur JS, la fiche d'une pièce sans photo
s'ouvre et demande bien ses 11 mesures. Déployé et vérifié en ligne.

---

## LES PIÈCES ENVOYÉES EN DOUBLE BASCULENT TOUTES SEULES (2026-08-18)

Mongazi : « Je t'enverrai certains en double pour un seul, et d'autres seuls.
Ceux en double, assure-toi qu'il **switch automatiquement quand on regarde**. »
Puis : « Dans la hero tu n'y mets en plus que les nouvelles, **dans le style de
ceux déjà présents**, histoire que ça reste cohérent. »

### La bascule

Une pièce qui a deux photos les montre l'une après l'autre, **au catalogue et
au carrousel**. `img2` (catalogue) et `f2` (carrousel) portent la vue de dos.

- **hors de l'écran, rien ne tourne** (`IntersectionObserver` → `duoVus`) ;
- **onglet caché ou fiche ouverte : tout se fige**, et l'échéance est
  **repoussée** — sans ce report, toutes les cartes rattrapent leur retard d'un
  coup au retour et basculent ensemble ;
- **décalage d'une carte à l'autre** : synchrones, elles clignoteraient
  ensemble comme une panne ;
- première bascule à **1,6 s** (elle apprend qu'il y a un dos), puis **3,6 s** ;
- au carrousel, **seule la carte active** respire ; le minuteur repart à chaque
  changement, donc une pièce qui arrive se montre toujours **de face d'abord**.

⛔ **Jamais de bascule vers une image pas encore arrivée.** La seconde vue est
en `lazy` : sur une 4G lente on révélerait **du vide pendant 3,6 s**. On attend
que `.complete` soit vrai. Un contrôle coupe le réseau sur les `-dos.webp` et
vérifie que la carte reste sur sa face.

⛔ **Le héros ne prend QUE la face.** Son glissement (pièce + chiffre géant,
même durée, même courbe) a été réglé au millième le 2026-08-06 : une seconde
vue qui s'y fondrait entrerait en concurrence avec lui.

`prefers-reduced-motion` : rien ne tourne, les pastilles disparaissent, le dos
reste dans la fiche de commande (figure « Le dos », inchangée).

Pastilles : l'active est **plus large**, pas seulement rose — un état qui ne
tient qu'à la couleur ne se lit pas pour tout le monde. 4,5:1 et 3,4:1 mesurés.

### Le héros prend les nouvelles

Plus de liste de trois élues. **Toute pièce qui a sa photo entre au héros**,
écrite comme ses voisines (`f` `c` `col` `mat` en apostrophes, `t` `d` en
guillemets, `mat:'Fait main · 2 semaines'` si la pièce est faite main).

⚠️ **La règle des nappes du 2026-08-17 est passée dans le code.** Le héros
peint le fond avec la teinte de la pièce : deux teintes voisines à la suite,
c'est une transition qui n'existe pas. `poser_heros()` choisit l'**ordre** des
ajouts (écart minimum 28°, **boucle comprise** : la dernière précède la
première). On ne perd plus la pièce — au lieu de l'exclure, **on la déplace**.
⛔ Aucune entrée déjà présente n'est touchée.

⏳ **À TRANCHER PAR MONGAZI** : 2 voisinages de même nappe existent **parmi les
7 diapositives déjà en place**, antérieurs à la règle —
`hero-3 #275eb7 → hero-4 #0e85b7` (**19°**) et
`piece-violette #6b3065 → piece-orange #925437` (**23°**). Deux transitions
presque invisibles. Un échange de place les réglerait.

### ⛔ Trois bugs qui auraient fait perdre les photos

Dans `_nouveaux_modeles.py`, ils se seraient déclenchés le jour de l'arrivée :

1. **`injecter()` sautait les onze fiches** : elles sont au catalogue depuis le
   2026-08-18 avec `photoWa:true`, le script voyait `id:"h10"` présent et
   passait. Les photos auraient été détourées, posées… et **jamais raccrochées
   à une fiche**. Rien ne l'aurait signalé. → `fiche_existante()`.
2. **`motion.js` n'était jamais réécrit** : carrousel et héros calculés puis
   **jetés**. Une pièce serait entrée au catalogue et nulle part ailleurs.
3. **Chaînes JS bâties en `'%s'`** : la première apostrophe cassait le site.
   → `js()` / `jsq()`, qui gardent le style du fichier sans risque.

Et la légende du carrousel se coupait **au milieu d'un mot** (« jupe longu »),
en grand sous la pièce. → `court()` coupe sur un mot.

### La règle du « tout ou rien » est inversée, et c'est voulu

Le script refusait de poser tant qu'une photo manquait. C'était juste quand les
onze pièces n'étaient nulle part. **Elles sont en ligne** avec « Photo sur
WhatsApp » : chaque photo posée est désormais un gain net. Attendre la dernière,
c'est laisser dix pièces sans image pour une onzième.

### Quand les photos arrivent

```
1. _partage/
2. _sources/modele-<clé>/  — UNE photo, ou DEUX (nommer le dos `dos.jpg`)
3. python _nouveaux_modeles.py --poser      (pose ce qui est prêt)
4. python _v4/_assembler.py && python _build.py && python _qc.py
5. REGARDER les captures
```

### Contrôles : 121 → 138

Onze neufs + une note. Ils mesurent l'**opacité réellement calculée**, pas le
CSS déclaré : fichiers présents, **face et dos non identiques (MD5)**, 2 images
et 2 pastilles, largeur de la pastille active, témoin « sous les yeux ça
tourne », pause hors écran, pause fiche ouverte, carrousel (seule l'active),
mouvement réduit, seconde vue coupée au réseau.

⚠️ **Trois leçons de contrôle**, valables partout :
1. **un contrôle de mise en pause a besoin d'un témoin** — « rien ne bascule
   hors de l'écran » passerait tout seul si le mécanisme était **mort** ;
2. **on échantillonne, on ne compare pas deux instantanés** — la bascule a une
   période de 7,2 s, deux relevés à 5,2 s d'écart retombent sur la même phase
   **une fois sur cinq** (même famille que le contrôle qui échouait au hasard) ;
3. un contrôle qui dit « il manque quelque chose » **nomme ce qui manque**.

⚠️ **Faux positif corrigé, antérieur au chantier** : « aucune ressource locale
manquante » échouait sur les 6 `.mp3`. Ils sont sur le disque — la boucle ouvre
la page en `file://`, où Chromium **interdit `fetch()`** (CORS), et l'échec
n'arrivait qu'**après** le clic, donc au hasard de la vitesse de la machine.
Les sons ont leur propre contrôle `sons()`, sur un vrai serveur HTTP.
Vérifié identique sur `main` avant de toucher à quoi que ce soit.

---

## NEUF MODÈLES REÇOIVENT LEURS VRAIES PHOTOS (2026-08-20)

Détail : `_memoire/conversations/2026-08-20-hillary-photos-recues.md`

**9 des 11 fiches** ont leur image. Il reste **Robe d'été** et **Ensemble
Volants**, qui gardent « Photo sur WhatsApp ». **Quatre pièces basculent
face/dos toutes seules** (organza, nœud, lacée, jean).

Les **9 prix et 9 types de mesures** donnés par Mongazi correspondent au
centime à ce qu'Hillary avait donné le 16/08. Vérifié avant de poser.

⛔ **Deux photos écartées** : la face de la Robe Sirène porte un **emoji ❤️
collé sur la poitrine** (on garde le profil) ; l'ancienne capture d'écran de la
Robe d'été reste écartée.

### ⛔ Le détourage : birefnet, pas isnet

`isnet-general-use` rendait le train d'organza blanc **en gris sale** sur la
face et l'**effaçait entièrement** sur le dos — il ne restait qu'un disque
rouge flottant. Les tissus translucides sont ce que ce modèle ne sait pas voir.
**`birefnet-general`** les garde intacts (~45 s par photo, 890 Mo).

⚠️ **Un processus par photo** : birefnet se faisait **tuer sur la deuxième
image** (code 137) avec 15 Go libres. onnxruntime ne rend pas ce qu'il a pris
entre deux inférences.

### ⛔ La couleur du héros suivait la peau

La robe verte ressortait en **brun**. Bras et jambes nus couvraient **23 %** de
la photo contre **17 %** pour le tissu. `teinte()` garde désormais les teintes
qui occupent **au moins 15 %** de la pièce et prend **la plus saturée** : un
vêtement est presque toujours plus vif qu'une peau.
⚠️ Un détecteur de peau par bande de teinte **ne marche pas** : la peau occupe
10-40°, là où vivent les tissus orange — et Hillary en a un.

### ⚠️ Un faux défaut signalé à tort, puis corrigé

La règle des nappes voisines comparait des **angles de teinte** (seuil 28°) et
accusait `hero-3 → hero-4`. **C'était faux** : leur distance perçue est de
**33 ΔE**, un bleu profond et un cyan clair. L'angle ignore la clarté et la
saturation. **La règle mesure maintenant en L\*a\*b\*, seuil ΔE 18.**
Résultat : **16 diapositives au héros, aucune transition invisible**.
⚠️ Avec l'ancienne mesure, **aucun ordre parfait n'existait** (6 pièces chaudes
contre 3 séparateurs) : la mauvaise mesure fabriquait un problème insoluble.

### ⛔ Trois bourdes de découpe, et deux garde-fous

L'outil réécrit `motion.js` et `garde-moteur.js` par découpe de texte :
une **virgule après un commentaire** (« `*/,` »), **tout l'en-tête du fichier
effacé** (bannière, `(function () {`, `'use strict'` — site entièrement muet),
et **sept fonctions effacées** par une restructuration, découvertes après
**dix minutes de détourage**.
→ la sortie passe par **`node --check` avant** d'être écrite, et `main()`
**vérifie ses fonctions avant** de lancer ce qui est coûteux.

### ⏳ Ce qui attend une réponse

1. les **2 photos** manquantes ;
2. le **sac beige** tenu devant l'Ensemble Orange — laissé ou retiré ?
3. le **dos de l'organza** a une teinte **crème** (fond jaune du studio vu à
   travers le tissu transparent) — neutraliser ou garder ?
4. ⚠️ **les originaux ne sont pas sauvegardés** : `clients/*/_sources/` est
   ignoré (ligne 76) et le dépôt est **public** ;
5. le **nommage** : « Robe de ville » coiffe même un tailleur veste + pantalon,
   donc lu comme un modèle de message ;
6. ⚠️ **défaut antérieur** : le héros affiche **« PRÊT-À-PORTER »** alors que
   les 20 pièces sont toutes en sur-mesure, onglet masqué car vide.

## ✅ 2026-08-20 · LES PHOTOS SONT EN LIGNE (le constat qui suit est résolu)

Vérifié depuis le PC, sur le site servi :

| | |
|---|---|
| `piece-soleil.webp` · `piece-organza.webp` · `piece-organza-dos.webp` · `piece-sirene.webp` · `piece-orange-uni.webp` | **404** |
| la page servie contre `vitrine.html` du disque | **deux fichiers différents** (MD5) |

**Un `git push` ne déploie rien.** Le travail du téléphone (8 modèles
photographiés, la Robe Soleil, la bascule face/dos, l'écart des nappes en
L\*a\*b\*) est bien dans `main` : il n'est pas chez la cliente.

Pour publier : `python _v4/_assembler.py` puis `python _build.py` (faits, la
page fait 286 261 octets et porte les 4 nouvelles pièces), puis
`python _predeploy.py`, **qui lance les 138 contrôles et refuse un déploiement
douteux**.

⚠️ **Ce qui bloque aujourd'hui** : les navigateurs Playwright ont été supprimés
le matin même pour libérer le disque, et le QC ne peut pas tourner sans eux.
`npx playwright install chromium webkit` = **430 Mo** (267 Chromium + 166
WebKit, qui sert au test iPhone réel). Le téléchargement est en cours et très
lent sur cette connexion.

⛔ **Ne jamais déployer en sautant le QC** : quand il échoue, `_predeploy.py`
s'arrête **avant** de préparer `_dist/`, et déployer juste après **republie la
version précédente sans un mot**.

### Il reste 3 pièces sans photo

`h8` Robe de ville à tulle · `h19` Robe d... · `h20` Ensemble Volants.
Elles affichent « Photo sur WhatsApp », ce qui est le bon comportement.

### ✅ Publié le 2026-08-20, et vérifié

`_v4/_assembler.py` → `_build.py` → `_predeploy.py` → `wrangler pages deploy`.
La page servie est **identique octet pour octet** au fichier construit (MD5), et
les cinq nouvelles images répondent 200 : Soleil, Organza (face et dos), Sirène,
Orange uni. **Il ne reste que 2 cartes en « Photo sur WhatsApp »** (25 images
distinctes en ligne).

⚠️ **`npx wrangler` ne marche plus sur ce poste** depuis le nettoyage du disque
(le paquet vivait dans un `node_modules` supprimé, et le cache npm a été vidé).
Wrangler 3 est maintenant **installé globalement** : la commande est
`wrangler pages deploy _dist --project-name hillary-m-styl --branch main`.

### ⚠️ Un contrôle tombait sur un site sain

`OK 137 / FAIL 1` : « l'état de la pastille ne tient pas qu'à la couleur »,
largeurs mesurées 9,18 et 10,31 px. Le style dit pourtant 5 px et 15 px.

**La largeur est animée.** Pendant le croisement des deux vues, les deux
pastilles passent toutes les deux par ~9 px et l'écart tombe à 1. Le contrôle
mesurait **un instant**, et cet instant arrivait juste après les 5 secondes
d'échantillonnage du contrôle précédent : il tombait donc pile dans la
transition. Mesuré au repos : **9,7 px d'écart, constant sur 8 secondes**.

Le contrôle **échantillonne maintenant six fois sur une seconde et garde le
meilleur écart**. Il reste strict : si le style regressait à la seule couleur,
aucun échantillon n'atteindrait le seuil. **138 contrôles verts.**

⚠️ Même famille que les deux pièges déjà écrits ici : on échantillonne, on ne
compare pas deux instantanés.

---

## PLUS AUCUN TEXTE SOUS UNE IMAGE NI SOUS UN INSTRUMENT (2026-08-21)

Mongazi, capture d'iPhone à l'appui : « y'a du texte qui rentre dans les
images, et ce n'est pas que là ». Un détecteur écrit pour l'occasion a trouvé
**quatorze endroits**, à trois largeurs. **14 → 0.**

### Le carrousel : titre et description posés SUR la robe

Sous 1180 px, `.cars-t` redevenait `position:relative` — donc dans le flux —
mais restait **dans `.cars`**, une boîte de hauteur fixe dont la piste
(`.cars-p`) est en `position:absolute` et couvre tout. **65 % du texte
recouvert à 390 px.** → `.cars` devient une colonne, la hauteur passe sur la
piste, le texte occupe sa propre ligne au-dessus.

### Le bouton du son mangeait le premier mot de tout ce qui passait

En `position:fixed` en bas à gauche : « 04 » du processus, « Conçu par » dans
le pied, « Saison 2026 », le « On » d'un titre. **Onze endroits.** Règle de la
maison : un instrument flottant ne recouvre jamais du texte, seules les bandes
de bord en ont le droit.

→ **il rejoint la barre du haut**, bande de bord opaque, et y devient un bouton
comme la loupe et le panier. ⚠️ `.nav-d` était **entièrement masqué sous
880 px** : on masque désormais ses autres enfants, pas le conteneur.

⚠️ **ET IL CHANGE DE PARENT, PAS SEULEMENT DE STYLE.** La barre porte
`z-index:50` et crée un **contexte d'empilement** : de l'intérieur, un
`z-index:130` vaut 50 et le bouton ne peut PAS passer au-dessus de la fiche
(z-index 120). Or la maison exige qu'on puisse couper le son en donnant ses
mesures. `parDessus()` le **sort de la barre** le temps de la commande et l'y
remet en refermant — le contrôle existant a vu l'échec immédiatement.

### Le contrôle, et ce qu'il refuse de compter

`chevauchements()` tourne aux 3 largeurs, en défilant toute la page :
- **défaut** : du texte **dans le flux** recouvert par un élément positionné ;
- **pas un défaut** : un texte posé exprès sur une photo (chiffre géant du
  héros, légende, badge, « Commander ») — il est `absolute`, c'est la signature
  de l'intention. Sans cette distinction, un premier jet annonçait **105**
  défauts, presque tous voulus ;
- **pas un défaut** : une **bande de bord** opaque qui traverse l'écran et
  touche un bord. ⚠️ Une pastille de 46 px qui flotte n'en est pas une, même
  opaque — sans ce resserrement, le détecteur **s'excluait lui-même** et
  annonçait zéro.

**138 → 141 contrôles, tous verts.**

---

## LE CARROUSEL AVANCE TOUT SEUL (2026-08-21)

Mongazi : « il faut que les éléments défilent tout seuls ». Le héros tournait
déjà (5 s) ; le carrousel des collections, lui, ne bougeait qu'au clic.

⚠️ **LA DURÉE SUIT LA PIÈCE, elle n'est pas fixe.** Une pièce photographiée des
deux côtés montre sa face 3,6 s, se retourne, puis laisse voir son dos avant
qu'on passe à la suivante : **7,4 s**. Une pièce à une seule vue : **5,5 s**.
Une cadence ordinaire de 4 s aurait fait passer au suivant **avant** que le dos
ait eu le temps de se montrer — on aurait posé un mécanisme par-dessus l'autre
et perdu le second, sans que rien ne le signale.

Il s'arrête au survol, onglet caché, et **hors de l'écran** (on n'anime pas ce
que personne ne regarde). Un geste le relance. Rien sous mouvement réduit.
Mesuré : 4 positions en 22 s sans y toucher, puis figé dès qu'il sort du champ.


---

## 2026-08-27 — « Ensemble Volants » retiré : la fiche n'a jamais existé

**Catalogue : 20 → 19 cartes, et toutes ont leur photo.** Plus une seule
« Photo sur WhatsApp ».

Mongazi a renvoyé la même photo une deuxième fois, avec les mêmes mots : « ce
n'est pas une robe volante mais robe de ville », 40 000 / 55 000, mesures d'une
robe ovale. Trois preuves concordantes :

1. Les **six prix** de `h20` étaient identiques à ceux de `h10 Robe de ville
   organza`, au franc et au centime près.
2. La seule photo jamais associée à `h20` est, **au pixel près** (empreinte
   `c2c3d9d2389a4c57`), le **dos de `h10`** déjà en ligne. Mesurée le 25 **et**
   le 27, même résultat.
3. La description de `h10` disait déjà ce que montre la photo : « dos lacé au
   ruban et jupon d'organza sous un wax rouge ».

⛔ **C'est moi qui l'avais fabriquée**, le 16/08, en décrivant deux fois la même
robe depuis une photo montrée en conversation. Voir `_memoire/lecons.md` :
*une description inventée coûte plus cher qu'une case vide*.

Le mécanisme `photoWa` **reste en place** — ce n'est pas du code mort, c'est
une place qui attend le prochain modèle arrivé avant son image.

⏳ **Il reste à publier.** Le site en ligne date d'avant le 26 août : il montre
encore la Robe d'été sans photo, alors qu'elle en a une depuis. Depuis le PC :

```bash
cd clients/10-hillary-m-styl && python3 _predeploy.py
npx -y wrangler@3 pages deploy _dist --project-name hillary-m-styl --branch main
```

---

## 2026-09-04 — CE QU'HILLARY DOIT SAVOIR AVANT DE COUPER

**Sa demande, mot pour mot** :

> Les informations dont j'ai besoin… Lieu de résidence · Nom · Prénom · Numéro
> de téléphone · Lieu d'expédition ou de livraison… Ou la cliente passera à
> l'atelier récupérer. De toute façon quand la tenue de la cliente sera prête on
> lui enverra un message ou on l'appellera en direct… De même qu'un message lui
> sera envoyé dès que sa commande est validée.

### L'écart mesuré avant de toucher au code

| Ce qu'elle demande | Ce que le site faisait |
|---|---|
| Lieu de résidence | ⛔ **n'existait pas** — seule la ville de *livraison* était demandée, et seulement en expédition |
| Nom | ⚠️ présent mais **facultatif** |
| Prénom | ✅ obligatoire |
| Numéro de téléphone | ⛔ **remplaçable par un email** (`tel ‖ mail`) |
| Lieu d'expédition ou de livraison | ⚠️ pays obligatoire, **ville non**, aucun repère |
| Retrait à l'atelier | ✅ en place |
| Un message à la validation | ⛔ dit nulle part |
| Un message ou un appel quand c'est prêt | ⛔ dit nulle part |

⛔ **Une commande pouvait donc arriver à l'atelier sans aucun moyen d'appeler la
cliente**, alors qu'Hillary annonce précisément qu'elle appellera. Et une autre
pouvait partir avec « Côte d'Ivoire » pour toute adresse de livraison.

### Ce qui est en place

**Étape 1 — Comment la recevoir ?**
- la **ville de livraison devient obligatoire** en expédition (le pays seul est
  une zone tarifaire, pas une adresse) ;
- nouveau champ **« Quartier ou point de repère »**, facultatif. ⚠️ **Au Bénin,
  une adresse est un repère, pas une rue** : demander « votre adresse » ne donne
  rien d'exploitable. Facultatif parce que le numéro, lui, est obligatoire :
  l'atelier peut toujours préciser au téléphone, et un champ de plus avant le
  bouton coûte des commandes.

**Étape 2 — Vos coordonnées**
- **quatre champs obligatoires** : Prénom, Nom, **Numéro de téléphone**, **Lieu
  de résidence**. L'email passe en *facultatif*, et la note reste libre ;
- ⚠️ **le numéro ne peut plus être remplacé par un email.** Ça n'exclut personne :
  qui n'a pas WhatsApp a un téléphone, et c'est précisément celui-là qu'on
  appellera. L'email reste offert **en plus**, jamais **à la place** ;
- ⚠️ **le lieu de résidence n'est pas le lieu de livraison**, et Hillary demande
  les deux. Le plus souvent ils se confondent, mais pas toujours (une cliente de
  Cotonou fait livrer sa sœur à Abidjan) : on ne le **suppose** pas, une puce
  **« J'habite à Abidjan »** propose de le recopier en un geste ;
- **les deux messages promis** sont écrits au-dessus du récapitulatif :
  « Vous serez prévenue deux fois. Un message dès que votre commande est validée,
  puis un message ou un appel dès que votre tenue est prête. C'est ce numéro que
  l'atelier utilisera. » C'est ce qui **justifie** le champ obligatoire.

**Étape 3 — Envoi** : la même promesse, redite là où la cliente quitte le site.

**La FAQ** porte une septième question, « Comment saurai-je où en est ma
commande ? ». ⚠️ Elle va dans **deux fichiers au même rang** (`markup.html` et le
`JSON_LD` de `_assembler.py`) : le balisage FAQPage est comparé **à la lettre et
dans l'ordre** aux questions visibles.

**Le message WhatsApp** porte les cinq informations, **chacune sous son nom** :

```
*CLIENT*
Nom : SOGLO
Prénom : Ama
Téléphone : +229 01 97 00 00 00
Lieu de résidence : Abidjan, Riviera 2
```

⚠️ Plus de `Prénom Nom` collés : Hillary recopie ces lignes dans son carnet, et
un nom composé rend le collage indéchiffrable. Le bloc `*LIVRAISON*` porte le
pays, la ville et le repère, ou « Retrait à l'atelier — gratuit ».

### ⛔ Le défaut vu sur une capture, pas dans le code

À l'étape 1, choisir un pays sans remplir la ville laissait **« CONTINUER » gris
et muet**. L'étoile rouge est sur l'étiquette, mais rien ne reliait le bouton
mort au champ qui manque.

C'est exactement ce que la ligne **« Encore : … »** corrige à l'étape 2 — et elle
n'y était qu'à l'étape 2. **Une règle appliquée à un seul endroit n'est pas une
règle** : la ligne est devenue commune aux deux étapes.

⚠️ **« A commencé » n'est pas « a choisi un mode ».** Le premier jet allumait la
ligne dès le clic sur « Expédition », c'est-à-dire au-dessus de deux champs
encore vides que la cliente s'apprêtait à remplir : on lui reprochait de ne pas
avoir fait ce qu'elle était en train de faire.

⚠️ **La ligne n'écrit que ce qu'elle montre.** `innerText` d'un élément en
`display:none` renvoie quand même son contenu : le contrôle lisait un message que
personne ne voit et accusait le site. La sonde était fausse — mais plutôt que de
corriger la seule sonde, texte et visibilité ont été rendus solidaires.

### ⛔ Le contraste de la modale n'était mesuré par rien

Ce QC vérifie qu'aucune variable CSS n'est utilisée sans être définie, mais
**aucun contrôle ne lisait une couleur de texte contre son fond dans le tunnel**.
C'est pourtant là que le rose de la marque a déjà été posé sur du texte **trois
fois** (étiquette du carrousel, badge, bouton WhatsApp) — et une **quatrième**
ici : la puce de recopie au survol mesurait **3,91:1**, trouvée à la main.

⚠️ **Le rose `--rose` ne porte pas de lettres.** Le trait le garde, le texte prend
`--rose-f` (4,93:1). Le contrôle mesure désormais les **pixels rendus** en
remontant jusqu'au premier ancêtre vraiment opaque, pour la puce (repos **et**
survol), les deux blocs de promesse et l'écran d'envoi.

### ⛔ `_predeploy.py` ne lançait pas l'assembleur

Le site se monte en deux temps : `_v4/_assembler.py` recompose
`_vitrine_src.html`, puis `_build.py` en tire `vitrine.html`. **`_predeploy.py` ne
faisait que le second.** Qui modifiait un morceau de `_v4/` puis lançait ce
script déployait un livrable bâti sur une source **périmée** : tout vert, tout en
ligne, et le changement absent, sans un mot. Le défaut était noté dans CLAUDE.md
depuis le 2026-08-16 et n'avait jamais été refermé. Il l'est.

### Contrôles : 150 → 192

Dont un par champ obligatoire **rempli un à un** (un contrôle qui remplit tout
d'un coup ne prouve rien), la ligne « encore » aux deux étapes, la puce de
recopie et son absence en retrait, les cinq lignes du message, le repère, les
deux promesses et leur contraste.

⚠️ **Un contrôle qui devient faux n'est pas un contrôle qu'on supprime.** Celui
qui disait « email seul suffit pour valider » protégeait une vraie décision : ne
pas exclure qui n'a pas WhatsApp. Cette décision tient toujours, mais elle passe
désormais par le **téléphone**, qui sert aussi bien à appeler. Le contrôle a été
**retourné**, pas retiré.

⚠️ **La page se souvient.** `cmd` et `memoire()` reportent les coordonnées d'une
commande sur la suivante — c'est voulu. Le contrôle « email seul ne suffit plus »
mesurait un numéro **déjà rempli par le parcours précédent** et concluait
l'inverse de la vérité. Il vide maintenant les champs avant de mesurer, et
vérifie au passage que le souvenir fonctionne, ce que personne ne contrôlait.

### Nouvel outil

`python _vues_commande.py` photographie les **dix écrans** du tunnel en 390 et
1440. ⚠️ **Ni `full_page` ni `.sheet`** : le premier photographie les 28 000 px du
catalogue qui dort derrière la modale, et le second est trompeur parce que la
barre et le pied sont `sticky` — ils se repeignent au bord de la fenêtre et
**cachent tout ce qui suit**. Sur les deux premières planches, les deux messages
promis et le récapitulatif étaient **absents de l'image sans que rien ne le
signale**. La fenêtre est donc haute, et toute la modale y tient.
