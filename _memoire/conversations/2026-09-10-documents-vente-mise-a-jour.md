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
