# Contrat partenaire en version 1.3, et la signature de Mongazi

**2026-09-02** · demande : « mets à jour le contrat pour NEBULA Agency avec les dernières
mises à jour, mets à jour les docs, envoie-moi le doc en PDF et mets ma signature ».

---

## Ce qui a été tranché par Mongazi

| Question | Réponse |
|---|---|
| Les logiciels édités par NEBULA (Boussole, PISTE, LE STANDARD, Digital HSE) entrent-ils au programme ? | **Non.** « C'est juste les deux, vitrine et catalogue, plus QR code. C'est pour les partenaires le contrat » |
| La signature | **Une vraie photo**, envoyée dans la conversation |
| IFU et RCCM | **Toujours en cours d'immatriculation**, mention inchangée |

---

## Le contrat passe de 1.2 à 1.3

**Aucun taux de commission ne bouge.** C'est ce qui rend le passage indolore : l'article 6.7
impose un préavis de 30 jours avant toute **baisse** de barème, et il n'y en a aucune. Un
partenaire en 1.2 ne perd rien.

| Article | Ce qui apparaît |
|---|---|
| **4.4** | Le **périmètre de vente**, écrit noir sur blanc : Catalogue et QR Google dès l'entrée, Vitrine après la 1re vente livrée, Outil sur mesure après 3 ventes et en binôme |
| **4.1 et 6.2 bis** | Les **frais de réactivation chiffrés à 5 000 F**, et « aucun frais si le client règle pendant les 7 jours de courtoisie » |
| **8, point 13** | Ne jamais vendre ni chiffrer une prestation absente du tableau de l'article 4.1 |
| **14.1 à 14.5** | Données personnelles étoffées : minimisation, information de la personne, destruction en fin de contrat **y compris sur le téléphone personnel**, alerte sans délai en cas de fuite, APDP nommée |

✅ **L'Outil sur mesure a été GARDÉ**, et Mongazi l'a confirmé le soir même : « ya juste
outil metier, catalogue digital et vitrine ». Le socle le portait déjà (l'escalier §1.3, la
certification §5.7, le barème §4.5) ; le retirer aurait supprimé une ligne de revenu
partenaire contre la source de vérité.

---

## ⛔ CORRECTION LE SOIR MÊME : aucun logiciel n'est nommé dans le contrat

Mongazi : « **dans le contrat ya rien qui concerne boussole et autre bordel, ya juste outil
metier, catalogue digital et vitrine** ».

L'article 4.5 que j'avais écrit (Boussole, PISTE, LE STANDARD, Digital HSE expressément
exclus) est **entièrement supprimé**, avec l'engagement 13 qui y renvoyait et le passage de
l'annexe qui les listait.

⚠️ **La protection ne disparaît pas pour autant** : l'article 4.4 dit déjà « les offres du
tableau de l'article 4.1, **et elles seules** ». C'est du meilleur droit que d'énumérer des
produits : une liste nominative **oblige à un avenant à chaque nouveau logiciel**, et un
logiciel absent de la liste devient discutable. L'engagement 13 a été recentré sur la même
idée : ne jamais vendre ni chiffrer une prestation absente du tableau des tarifs.

⚠️ **Le socle a été ramené à sa forme d'origine.** Il excluait **Boussole seul**, et c'était
une décision de Mongazi antérieure à cette session. Le tableau à quatre logiciels que j'y
avais ajouté était de ma propre initiative : il est retiré. On ne garde pas dans un document
interne ce qu'on vient de faire sortir du contrat.

⚠️ **Leçon** : quand le fondateur dit « c'est juste les deux, c'est pour les partenaires le
contrat », il répond à la question posée (est-ce que ça se vend ?) et **pas à la question
suivante** (faut-il l'écrire ?). Un périmètre positif se suffit à lui-même ; l'exclusion
nominative est une couche que personne n'avait demandée.

---

## Les documents alignés derrière

- **Socle commercial §8** : la section « ce qui n'est PAS dans le programme » gagne une
  phrase de tête (le partenaire vend Catalogue, Vitrine, Outil sur mesure, plus le QR) et
  **garde la seule exclusion posée par Mongazi lui-même, Boussole**. ⚠️ Le tableau à quatre
  logiciels que j'y avais mis a été retiré le soir même, voir la correction plus haut.
- **Manuel §5.2 ter** : « la remise en ligne peut coûter des frais de réactivation » devient
  **5 000 F**, avec la phrase qui compte : ces 5 000 F **ne rapportent rien au partenaire**,
  donc il n'a aucun intérêt à laisser un client tomber.

---

## La signature

⚠️ **Le dépôt `allonebiao2/nebula-agency` est PUBLIC, et `pdf/*.pdf` y est versionné.**
Une signature manuscrite commitée là serait récupérable par n'importe qui, et une signature
qui traîne se colle sur n'importe quel papier. D'où la chaîne :

- l'image détourée vit dans **`secrets/signature-mongazi.png`** (ignoré par git) ;
- le PDF signé sort dans **`pdf/signe/`**, ajouté au `.gitignore` ;
- le PDF **vierge** reste versionné, et les deux se superposent au millimètre (le marqueur
  est un **commentaire HTML**, donc le creux garde la même hauteur dans les deux).

### Le détourage

⛔ **Pas rembg ici.** rembg détoure un **sujet** posé sur un fond. Un trait d'encre sur du
papier n'a pas de silhouette : ce qui le sépare du papier est une **couleur**. Un seuil sur
la teinte bleue (`B - R`) donne un **alpha continu**, donc des traits qui gardent leur délié.

- masque de repérage : `bleu > 30 & luminance < 180` → boîte **426 × 1192 px** dans une photo
  de 4032 × 3024, propre du premier coup ;
- alpha : `teinte × (0.35 + 0.65 × darkness)`, la teinte décide, la darkness sert de garde-fou
  (un reflet bleuté mais **clair** n'est pas de l'encre) ;
- ⚠️ **la feuille n'a jamais été cherchée** : le carrelage est presque aussi clair qu'elle.
  Chercher l'encre directement évite tout le problème.

### ⛔ `_partage/` EST VERSIONNÉ, et la photo y a atterri

Mongazi a redéposé la photo dans **`_partage/signature.JPG`**, pensant bien faire.
⚠️ **`_partage/` n'était pas ignoré par git et 33 de ses fichiers sont déjà suivis** : un
`git add -A` aurait publié sa signature manuscrite sur un dépôt **public**. Vérifié à temps,
elle n'avait jamais été commitée.

La règle posée vise **le nom du fichier, pas le dossier** (`signature.jpg`, `.JPG`, `.png`,
`signature-*`) : une photo envoyée arrive rarement deux fois au même endroit. Contrôlé que la
règle n'attrape aucun fichier légitime déjà suivi (la note
`2026-07-25-boussole-signatures-mastodontes.md` reste versionnée).

⚠️ **Leçon générale** : protéger `secrets/` et le dossier des PDF signés ne suffisait pas.
Le point d'entrée d'un fichier sensible n'est pas là où on le range, c'est **là où on le
dépose**, et sur ce dépôt c'est `_partage/`.

### La photo redéposée était la même

MD5 différents, **pixels identiques à 100 %** (même 4032 × 3024, écart moyen 0,00). C'était
la photo de la veille, seulement réencodée. Aucun PDF à refaire.
⚠️ **Un MD5 différent ne prouve pas une image différente** : c'est l'inverse de la leçon du
06/08 chez Hillary, où des compteurs d'octets identiques cachaient un cache empoisonné. Ici
il fallait comparer **les pixels**, pas les octets.

### Le sens

⚠️ **On ne devine pas le sens d'une signature, on la regarde.** La boîte faisait
426 × 1192 px, donc la feuille avait été photographiée tournée d'un quart de tour. Les deux
rotations possibles ont été **fabriquées et posées sur un damier**, puis comparées à l'œil :
le **quart de tour horaire** est le bon (boucle capitale à gauche, longue envolée finale vers
la droite). L'axe principal mesuré (70,7°) ne suffisait pas à trancher : il dit l'inclinaison,
pas l'endroit.

⛔ **Aucun redressement ajouté.** L'axe principal d'une signature n'est pas sa ligne de base :
il est dominé par la longue envolée finale. Se caler dessus aurait penché l'écriture vers le
bas.

---

## Contrôles passés

- le **HTML brut du bloc de signature traverse python-markdown intact** (5 classes + le
  marqueur survivent, aucun `&lt;div` échappé) ;
- **0 tiret cadratin** dans les trois documents touchés ;
- les articles annoncés dans l'en-tête de version **existent réellement** dans le corps ;
- le bloc a été **photographié avec le CSS et le balisage réels** de la chaîne PDF, pas
  déduit du poids du fichier : signature posée au-dessus du filet, deux cadres alignés.

⚠️ Chaque script d'édition **refuse d'écrire** si un bloc à remplacer est absent ou présent
deux fois. On ne modifie pas un document contractuel à l'aveugle.

---

## Ce qui reste

- les **13 documents de vente** n'ont pas tous été relus : seuls le contrat, le socle et le
  manuel ont été touchés ;
- IFU et RCCM à porter dès obtention (un avenant d'une ligne) ;
- la date reste `[date]` sur l'exemplaire signé : elle se remplit quand le partenaire
  contresigne.

---

## Deuxième passe, le soir : le contrat n'arrivait pas jusqu'aux partenaires

⛔ **La bibliothèque du cockpit servait encore le contrat du 3 août.** Le 1.3 était dans le
dépôt depuis le matin, mais `nebula-affilies/assets/docs-partenaires/09-CONTRAT-PARTENAIRE.pdf`
n'avait pas bougé : ni l'article 4.4, ni l'APDP, pas même une version en couverture. Un
partenaire qui téléchargeait « son contrat » depuis son espace signait **l'ancien**.

⚠️ **Écrire le document ne le publie pas.** Trois copies vivent dans ce dépôt et elles ne
bougent pas ensemble : le Markdown, le PDF de `vente/pdf/`, et **celui de la bibliothèque**,
qui est le seul que le partenaire voit. La version de `DOCS_PARTENAIRES` a été passée au
2026-09-02 : sans ce changement, `publier_documents()` ne rejoue rien et la base garde
l'ancien fichier même si l'octet a changé sur le disque.

## Le socle et le manuel dataient d'avant leur propre texte

Tous deux avaient été modifiés le matin **en gardant leur ligne « Version · 2026-07-30 »**.
Le socle passe en **2.1**, le manuel en **1.1**.

⚠️ Ce n'est pas cosmétique : le socle est la **source de vérité des prix**, et l'**article 15
du contrat en fait une pièce contractuelle**. Un document contractuel daté plus vieux que son
propre contenu se fait écarter comme périmé par celui qui le compare au contrat.

## ⛔ La couverture lisait la date de MODIFICATION du fichier

`VERSION = date.fromtimestamp(getmtime(src))`. Un `git clone` remet cette date au jour du
clone : le contrat aurait annoncé **la date du clone en couverture** et « Version 1.3 ·
2026-09-02 » dans son texte. **Deux dates qui se contredisent sur une pièce contractuelle.**

La version se lit maintenant **dans le document**, qui la porte déjà ; le mtime n'est plus
qu'un secours pour les deux fichiers qui n'ont pas de ligne de version.

⚠️ **C'est le mtime qui masquait le problème du socle** : il affichait la date d'aujourd'hui,
donc la couverture semblait juste. Corriger la lecture a rendu l'incohérence visible.

## La page des signatures partait seule

Le bloc tenait **à 7 mm près** en bas de la page 10 : les deux cadres passaient à la page
suivante, **orphelins de leur titre**, sous un tiers de page blanc. On ne joue pas au
millimètre avec ça, le texte du contrat bougera encore : la page des signatures **commence
désormais à neuf**, titre et cadres ensemble. Nombre de pages inchangé (12), et vierge et
signé se superposent toujours à **0,00 pt** (mesuré sur quatre repères de la page).

## `_signature.py` : la méthode était en mémoire, le code avait disparu

Le détourage n'avait **jamais été commité**. Réécrit d'après la note du matin, et vérifié de
bout en bout sur une fausse photo fabriquée pour l'occasion (encre bleue sur papier clair
posé sur un carrelage clair, feuille tournée d'un quart de tour) : boîte trouvée
**463 × 1350**, très proche des 426 × 1192 de la vraie, alpha continu, quart de tour horaire
correct. **Planche sur damier regardée**, pas seulement des chiffres lus.

⛔ **Mon propre `--voir` écrivait la planche à la racine du dépôt**, où rien ne l'ignorait :
la signature aurait été poussée sur un dépôt **public** au premier `git add -A`. C'est
exactement la leçon de ce matin sur `_partage/`, refaite par moi douze heures plus tard.
La planche sort maintenant dans `pdf/signe/`, déjà ignoré.
⚠️ **Une leçon écrite ne protège pas le code écrit après elle.** Le garde-fou utile n'est pas
la note, c'est le contrôle : `git status` a été relu avant le commit, et c'est lui qui a vu.

## ⛔ La photo de la signature est perdue, et c'est structurel

Le conteneur a été réinitialisé (≈15e fois de la session). La photo vivait dans les deux
seuls endroits qui la protègent : `secrets/` et `_partage/signature.JPG`, **tous deux ignorés
par git**. Ignoré par git veut dire **absent du clone qui reconstruit la machine**.

⚠️ **Ce qui protège la signature du dépôt public est exactement ce qui la fait disparaître à
chaque réinitialisation.** Il n'y a pas de réglage à changer : c'est le prix du dépôt public,
et il est juste. La conséquence pratique est qu'une session dans le nuage ne peut produire
l'exemplaire signé **que dans la séance où Mongazi envoie la photo**. Sur son PC, `secrets/`
survit, et l'exemplaire signé se refait quand il veut.

Le PDF **vierge** en 1.3, lui, est versionné : il est livré, à jour, et c'est sur lui que la
signature se posera sans rien déplacer.

---

# 2026-09-03 · la 1.4, et la signature qui a failli passer pour un fantôme

## Trois signatures, deux parties

Mongazi : *« il doit signé aussi car lui il se charges de gérer tout les partenaires »*.
**Romaric DJANKAKI**, son second, cosigne désormais le contrat qu'il fait appliquer.

⚠️ **Trois cadres alignés se lisent comme trois parties.** Les deux cadres NEBULA sont donc
groupés sous un seul intitulé, le cadre du Partenaire ouvre le sien, et le cadre seul garde
**la largeur d'un cadre du haut** (sinon il s'étale sur toute la page et déséquilibre).

⚠️ **Un troisième nom au bas d'un contrat se lit comme un troisième engagé.** La cosignature
est donc qualifiée dans l'identification des parties : elle **engage NEBULA, pas Romaric à
titre personnel**. Sans cette phrase, on créait une obligation solidaire sans le vouloir.
⏳ **À confirmer par Mongazi** : le titre « responsable du réseau partenaires » est ma
reformulation de ce qu'il a décrit, et cette phrase de non-engagement personnel est un choix
juridique, pas une évidence. S'il veut Romaric engagé, c'est une autre clause.

La chaîne PDF accepte maintenant **deux emplacements de signature, chacun facultatif** :
l'absence de la signature de l'un n'empêche jamais de produire l'exemplaire portant celle de
l'autre. Le cadre vide se signe à la main sur l'imprimé.

## ⛔ Le masque était parfait, l'alpha était faux

La 2e photo sortait à **0,3 % de pixels opaques**. J'ai d'abord soupçonné le repérage. Faux :
la planche des masques, regardée, montrait un détourage **impeccable**.

C'est la **rampe d'alpha** qui était fausse. Elle était fixe (60 niveaux au-dessus du seuil),
calibrée sur la 1re photo dont l'encre montait à **B-R = 90**. Cette photo-ci, prise dans une
pièce plus sombre, **plafonne à 42** : `t = (42-30)/60 = 0,20`. Une signature à 20 %
d'opacité. La rampe se cale désormais sur le **85e centile de la teinte trouvée dans la photo
traitée** : 0,3 % → **2,7 %** d'opaques.

⚠️ **Une constante mesurée sur un échantillon devient un réglage, pas une loi.** Le seuil de
détection (B-R > 30) a très bien tenu d'une photo à l'autre ; c'est la NORMALISATION qui ne
pouvait pas tenir, parce qu'elle encodait la luminosité d'une pièce.

## ⛔ La rotation par défaut se trompait une fois sur deux

La 1re photo arrivait couchée et demandait un quart de tour horaire. **La 2e sortait déjà
droite d'`exif_transpose`**, et ce même quart de tour la remettait sur le flanc. La rotation
n'a donc plus de valeur par défaut : on regarde la planche, on passe `--rot`. Le script
prévient quand la boîte est plus haute que large.

Mesures de la 2e photo, pour mémoire : boîte **1241 × 475**, **aucune rotation**, encre
médiane R 50 / G 49 / B 93, luminance 54, papier à 205.

Un reflet bleuté du carrelage étirait aussi la boîte de **1241 à 1911 px** : on ne garde que
la **plus grosse tache** d'encre.

## ⛔ La photo est reperdue, et c'est la deuxième fois dans la journée

Le conteneur s'est réinitialisé **deux fois pendant ce seul échange**, dont une au milieu du
détourage. `/root/.claude/uploads/` revient à un instantané du 20 août : la photo envoyée
il y a quelques minutes n'y est plus.

⚠️ **Méthode adoptée : commiter après CHAQUE étape**, pas en fin de tâche. Les corrections de
`_signature.py` ont été perdues une fois parce qu'elles attendaient un commit groupé.
⚠️ **`git merge --ff-only` a échoué en silence** sur une branche divergente, et j'ai cru
travailler sur `main` à jour alors que j'étais 4 commits en arrière. Vérifier
`git log origin/main`, pas seulement le code de retour.

**Conclusion pratique, à dire à Mongazi plutôt qu'à redécouvrir** : l'exemplaire signé se
fabrique **sur son PC**, où `secrets/` survit. Une session dans le nuage ne peut le faire que
dans la minute où la photo arrive, et rien ne garantit qu'elle y sera encore.
