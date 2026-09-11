# Les documents de vente relus contre la grille unique · 2026-09-10

## Ce que Mongazi a demandé

« Mes documents de NEBULA agency ne sont pas à jour, il faut les mettre à jour. Déjà le
contrat ne contient même pas les dernières modifications, ce n'est pas 30 % 25 % 40 % mais
plutôt 30 % 40 %. Donc il faut faire une mise à jour sur tous les documents s'il y en a. »

## Le contrat, lui, était bon

⚠️ **Le premier réflexe était le mauvais.** `09-CONTRAT-PARTENAIRE.md` est en **version 1.4**,
il porte bien **30 % / 40 %**, il ne contient ni 25 % ni 35 %, et son PDF, relu **dans les
octets et pas dans le nom du fichier**, dit exactement la même chose. Les **12 PDF** de
`vente/pdf/` et les **10** de `docs-partenaires/` sont tous propres. Le moteur du portail
aussi (`RATE_BASE = 0.30`, `RATE_EQUIPE = 0.40`, `SEUIL_EQUIPE = 3`, aucune commission de
réseau), le site v9 aussi, le cerveau de NOVA aussi.

**Ce que Mongazi a sous les yeux n'est donc pas le contrat : c'est un autre document.**

## Ce qui portait vraiment l'ancienne grille

Quatre documents, tous **hors du dossier `vente/`**, donc jamais relus quand la grille a
changé le 2026-08-02 :

| Document | Ce qu'il annonce |
|---|---|
| `NEBULA_Brochure_Partenaire.pdf` | STARTER **25 %** · SILVER **30 %** · GOLD **35 %** · N1 **10 %** · N2 **5 %** |
| `NEBULA_Guide_Lancement_Partenaire.pdf` | la même grille, en version interne |
| `NEBULA_Programme_Partenaires_PREMIUM.pptx` | **25 %** vente directe, **10 %** parrain, **5 %** N2, « plafond total 40 % », abonnement **15 000 F**, sept rangs cosmiques |
| `NEBULA_Programme_Partenaires.pdf` | le même deck exporté, oublié dans `nebula-affilies/assets/` |

⛔ **Le plus cher n'est pas le taux, c'est le réseau.** Une diapositive entière, « Le pouvoir
de l'effet réseau », déroule un arbre Marc → Shad → Paul → Kofi et conclut : « son réseau lui
rapporte 90 000 FCFA de plus, sans effort supplémentaire ». C'est exactement ce que la
décision du 2026-08-02 a supprimé. Montrer cette page à un candidat, c'est lui promettre un
revenu qu'il ne touchera jamais, **et donner au programme l'allure de la pyramide que la
diapositive d'à côté jure qu'il n'est pas**.

⚠️ **Ils ne sont pas réparables.** Les 14 diapositives du `.pptx` sont **des images plein
écran** (une PNG par diapositive, `<a:t>` vide, 13 caractères de texte extraits sur tout le
fichier), et les deux PDF n'ont aucune source dans le dépôt. Corriger un chiffre voudrait dire
refabriquer le document entier. Ils partent donc en quarantaine dans
`_documents/nebula-agency/_obsolete/`, avec un README qui dit ligne par ligne ce qui a changé
et par quoi les remplacer (`01b-ANNONCE-PUBLIQUE`, `02-MANUEL-DU-PARTENAIRE`, le simulateur,
le contrat 1.4). Ils ne sont pas supprimés : ils restent une archive.

⚠️ **`NEBULA_Masterclass_Closing.pptx` a été vérifié et RESTE en place** : il ne parle que de
méthode (« Écoute 70 %, parle 30 % », la carte des objections), ne cite aucun taux de
commission, et ses prix concordent avec le socle. **Ne pas ranger un document parce que son
voisin est périmé.**

## Le simulateur de commissions était cassé, et personne ne pouvait le savoir

`simulateur-commissions.html` faisait :

```js
["25","30","35"].forEach(function(k){ el("t-" + k).classList.remove("on"); });
```

Or la page ne porte plus que `t-30` et `t-40` depuis la grille unique. `el("t-25")` rend
`null`, et **`null.classList` lève une TypeError au milieu de `render()`**, dès le chargement
puis à chaque clic.

⚠️ **Le symptôme trompe** : ce qui est écrit **avant** la ligne fautive s'affichait
normalement (le gain, le nombre de ventes, le chiffre, le badge). Ce qui vient **après** ne
s'exécutait jamais : **le palier ne s'allumait plus, et le message « il te manque 2 ventes
pour passer à 40 % » n'apparaissait plus** — c'est-à-dire précisément les deux choses pour
lesquelles le simulateur existe. Un outil à moitié mort a l'air vivant.

Vérifié en rejouant le script dans node avec un faux DOM bâti sur les identifiants réellement
présents dans la page : 0 vente → aucun palier ; 1 vitrine → BRONZE, 30 %, 45 000 F, « il te
manque 2 ventes » ; 3 vitrines → ARGENT, 40 %, 180 000 F, « tu es au taux maximum ». Et
l'ancienne version, relancée dans le même harnais, **casse au chargement** : le défaut est
prouvé, pas supposé.

Une phrase du même âge disait aussi deux fois la même chose : « dès **3** au total, tout ton
mois passe à 40 %. Et dès que tu fais **4** au total, tout ton mois passe à 40 % » : le
vestige du palier intermédiaire supprimé.

## Le kit partenaire vendait ce que le contrat interdit

`_kits/kit-nebula.html` (et son PDF, présent en deux exemplaires) proposait la **Fiche Google
Maps à 20 000 F** et l'**Avatar IA à 30 000 / 100 000 F par mois**. Or l'article **4.4** du
contrat dit : « les offres du tableau de l'article 4.1, **et elles seules** », et ni l'une ni
l'autre n'y figure. Le kit poussait aussi à **entrer par la Vitrine** (« tu entres souvent par
la vitrine ») quand la règle de la maison est l'escalier : **on entre toujours par le
Catalogue à 50 000 F**. Et il annonçait l'abonnement à **15 000 F**.

⚠️ **Ce n'était pas une ligne à changer, c'était un fil dans tout le document** : la Fiche
Google Maps servait d'argument dans six endroits, dont un script de dialogue complet et une
technique de combo. Elle est remplacée partout par le **QR Code Avis Google (30 000 F)**, qui
est au contrat et sert le même besoin.

⛔ **Une statistique inventée est partie avec** : « 8 personnes sur 10 cherchent un resto sur
Google avant d'y aller ». Aucune source, et la maison n'invente pas de chiffres.

Le tableau des six offres est refait sur le tableau 4.1 (Catalogue, QR avis, Vitrine, Outil,
Abonnement, Réactivation), chaque carte disant **quand** le partenaire a le droit de la
vendre. Le PDF est régénéré depuis le HTML au Chrome headless : **14 pages avant, 14 pages
après**, balisage revérifié (0 erreur), et la page regardée en capture avant de conclure.

## Les autres écarts trouvés en chemin

- **`00-SOCLE-COMMERCIAL.md` §13 « Reste à répercuter »** : les trois points étaient **faits**
  et jamais cochés. Vérifiés un par un dans les fichiers : le site v9 affiche 20 000 F aux six
  endroits, `agency_brain()` aussi, et `seed_docs` **n'existe plus** (remplacé par
  `DOCS_PARTENAIRES` + `DOCS_RETIRES`). ⚠️ **Une liste de choses à faire qu'on ne coche pas
  devient une liste de choses qui ont l'air non faites** : elle appelle à refaire du travail
  déjà livré.
- **`CLAUDE.md`** annonçait le contrat en **1.3** alors qu'il est en **1.4** depuis le
  2026-09-03 (cosignature de Romaric DJANKAKI, trois signatures pour deux parties).
- **`server.py`** portait un commentaire « tout le monde est sur **30/40/50** » : un troisième
  palier qui n'a **jamais existé** dans le code, qui n'a que `RATE_BASE` et `RATE_EQUIPE`.
- **`INDEX.md`** annonçait « les 9 documents » pour 12 PDF, décrivait les commissions avec le
  mot « réseau », et donnait le socle en « v2 » alors qu'il est en 2.1.
- **`00-nebula-agency/CONTEXT.md`** portait encore la grille tarifaire à **15 000 F / 6 mois**,
  alors que le site qu'il documente affiche 20 000 F depuis des semaines.
- **`presentation-couts-roi.html`** : même 15 000 F.

## Ce qui reste à trancher par Mongazi

- ⏳ **`00-nebula-agency/affiliation/programme-affilies.html`** : une génération **encore
  antérieure**. Vitrine à **100 000 F négociable jusqu'à 75 000 F**, Catalogue à **40 000 F
  livré en 14 à 21 jours**, commissions en **montants fixes** (30 000 F, 12 000 F), versement
  **sous 7 jours** au lieu de 24 à 72 h, et un numéro de paiement qui n'est pas celui du
  contrat. **Rien n'y est juste.** Elle n'est pas déployée (le site est un seul `index.html`)
  mais elle a été maintenue en août pour les liens du portfolio, donc elle n'est pas
  abandonnée. La refaire contre le socle, ou la ranger : c'est une décision, pas une
  correction.
- ⏳ **Deux CONTEXT client portent l'abonnement à 15 000 F** : `06-miss-cakes` et
  `07-speed-weinkeller-ck`. ⚠️ **Ce n'est pas forcément une erreur** : ces clients ont pu
  souscrire avant le passage à 20 000 F. Un tarif déjà accepté ne se réécrit pas depuis un
  dépôt. Seul Mongazi sait ce qu'ils paient.

## Ce qu'il faut retenir

⚠️ **La grille change dans `vente/`, les documents périmés vivent ailleurs.** Le 2026-08-02, la
grille unique a été répercutée avec soin sur les 13 documents du dossier de vente, le contrat,
le portail et le site. Les quatre qui sont restés faux étaient **à la racine de
`_documents/nebula-agency/`**, hors du chemin de la relecture. Le jour où un chiffre change,
la question n'est pas « quels documents de vente », c'est **« quels documents, où qu'ils
soient »**.

⚠️ **Un document en images ne se corrige pas, il se refabrique.** Un `.pptx` dont les
diapositives sont des PNG n'a pas de chiffre à changer : il a un chiffre **peint**. Rien ne
peut le signaler, aucune recherche de texte ne le trouve, et il survit à toutes les vagues de
correction. **Ce qui n'a pas de source ne se maintient pas.**

⚠️ **Relire les octets, pas les noms.** « Le contrat n'est pas à jour » a été démenti en
extrayant le texte du PDF, pas en regardant sa date ni son nom de fichier. Et c'est cette
même lecture qui a trouvé le vrai coupable trois dossiers plus loin.

---

# Second temps · 2026-09-11 · l'ancienne grille était aussi écrite EN FRANCS

Mongazi : « Donne-moi les documents du coup. Améliorer, modifier. »

En régénérant les PDF (le socle avait été modifié la veille sans que son PDF soit
refait), la relecture de `01b-ANNONCE-PUBLIQUE.md` a fait tomber **six défauts de plus**,
et l'un d'eux ouvrait une famille entière.

## ⛔ Le défaut de fond : 25 % survivait en francs

Le 2026-08-02, la grille est passée à 30 % / 40 % et **tous les pourcentages** ont été
corrigés. Mais trois montants étaient écrits **en francs** :

| Où | Ce qui était écrit | Ce que c'est | Ce que ça devrait être |
|---|---|---|---|
| `07-MISE-EN-LIGNE.md` | « 1 catalogue = **12 500 F** » | 25 % de 50 000 | **15 000 F** |
| `07-MISE-EN-LIGNE.md` | « 1 vitrine = **37 500 F** » | 25 % de 150 000 | **45 000 F** |
| `03-GUIDE-CATALOGUE.md` | « QR Google Review 30 000 F → **7 500 F** » | 25 % de 30 000 | **9 000 F** |

⚠️ **Aucune recherche de « 25 % » ne pouvait les trouver.** Ils ont survécu cinq semaines
à toutes les relectures. Le pire des trois vivait **sous un titre « palier 30 % »**, dans
le guide que le partenaire lit pour vendre le Catalogue, et la même ligne annonçait
l'Outil à 200 000 F pour **50 000 F** de commission (25 %) au lieu de 60 000. Le tableau
« sur un seul client » totalisait **107 500 F** quand la vraie somme fait **129 000 F** :
⚠️ **il ne tombait même pas juste sur ses propres lignes** (15 000 + 7 500 + 45 000 +
50 000 = 117 500). Un partenaire perdait 21 500 F sur un client, sur le papier.

⚠️ **Et `07-MISE-EN-LIGNE.md` affirmait que ces montants avaient été « recalculés à la
main sur 7 cas de figure, tous conformes au socle commercial ».** Une vérification écrite
n'est pas une vérification faite.

## ⛔ Le mois type valait 150 000 F au lieu de 200 000 F, dans TROIS documents

« Un mois à 6 ventes (4 Catalogues + 2 Vitrines) → **150 000 F de commission** » :
6 ventes dépassent le seuil de 3, donc le mois entier est à 40 %, donc **200 000 F**.
Le socle l'a juste (§4.5). `01`, `01b` et `01c` l'avaient faux. ⚠️ **`01` se contredisait
lui-même** : 200 000 F à la ligne 30, 150 000 F à la ligne 102. Et `07` décrivait un
partenaire « à 4 ventes qui voit ce que la 5e lui rapporte » : **le seuil est 3**, il
serait déjà à 40 %. La mécanique de l'ancien escalier à trois paliers, racontée en
toutes lettres.

**Ces documents sous-vendaient le programme de 50 000 F par mois type.**

## Les autres corrections

- `06-ARSENAL-SCRIPTS` : « Je gagne entre 15 000 et **75 000 F** par vente » → **60 000 F**
  (75 000 n'est aucun taux de la grille ; 60 000 = une Vitrine à 40 %, et l'Outil n'est
  pas vendable avant 3 ventes).
- **Un paragraphe entier disait deux fois la même chose** dans les trois avis de
  recrutement, avec une phrase recopiée mot pour mot (« Personne ne gagne d'argent sur le
  dos de personne ici »).
- « Candidatures ouvertes **jusqu'au 21 jours après la publication** » : phrase cassée, et
  une date qui ne veut rien dire sur un texte partagé pendant des mois.
- « Au Braisé d'Or · **48 plats** » : ⚠️ **le site en sert 52** (`index.html`, la source
  déclarée, et `carte.ts` concordent) **et `CLAUDE.md` en annonce 42**. Trois chiffres pour
  une carte. Un nombre qu'on ne peut pas prouver ne va pas dans un document public → « toute
  sa carte commandable en ligne ». ⏳ **L'écart 42 / 52 reste à trancher chez le client 09.**
- « Luxury Skin Clinic » → **Luxury Club 229** (c'est la maison ; la clinique n'en est qu'un
  pôle), et **Angy Art** ajoutée aux références.

## `_verifier_montants.py` · le contrôle qui manquait

Il relit **chaque montant en francs** des documents de vente et le recalcule contre la
grille. Branché sur `_build_pdf.py` : **un montant faux empêche désormais de fabriquer les
PDF**, il ne se contente pas de s'afficher.

⚠️ **Le premier jet est sorti VERT sur la ligne même pour laquelle il avait été écrit.**
Il ne signalait un montant que si le mot « commission », « palier » ou « vous gagnez » se
trouvait à moins de 240 caractères. Or la ligne fautive disait « montants recalculés à la
main… (1 catalogue = 12 500 F) » : pas un seul de ces mots. **Un filtre de vocabulaire est
une supposition sur la façon d'écrire, et un contrôle qui suppose ne lit plus.** Le filtre
est retiré ; les exceptions sont **nommées une par une** dans `PAS_UNE_COMMISSION`, avec
leur raison (les 5 000 F de réactivation valent par hasard 10 % de 50 000 ; les 25 000 F
du diagnostic valent par hasard 5 % de 500 000 ; les 10 000 F du gain rétroactif sont
justes). ⚠️ **Un contrôle qui crie au loup dix fois n'est plus relancé par personne**, et
c'est comme ça qu'un vrai défaut passe.

**Témoin fait** : les trois défauts d'origine réintroduits → **rouge, code 1** ; retirés →
**vert, code 0**.

## Publication

Les **12 PDF refaits**, les **10 partenaires synchronisés**, et ⚠️ **`03`, `06` et `01b`
ont leur version bumpée dans `DOCS_PARTENAIRES`** : sans ça `publier_documents()` compare
la date, la trouve identique, et **ne republie rien, sans un mot** — les partenaires
seraient restés sur les PDF à 25 %. Les sept autres gardent leur date : même contenu.

## Ce qu'il faut retenir

⚠️ **Un taux corrigé n'est pas une grille corrigée.** Chercher le pourcentage ne trouve que
la moitié du travail : le reste vit en francs, en exemples, en totaux, et dans la mécanique
racontée (« à 4 ventes, la 5e… »). La seule vérification qui tient est **arithmétique** :
recalculer chaque montant à partir du prix et du taux.

⚠️ **Une vérification écrite dans un document n'est pas une vérification faite.**
`07-MISE-EN-LIGNE` affirmait noir sur blanc que ses montants étaient « conformes au socle ».
Ils étaient à 25 %. La phrase a survécu à la correction de la grille parce que personne ne
relit une phrase qui dit que c'est déjà vérifié.
