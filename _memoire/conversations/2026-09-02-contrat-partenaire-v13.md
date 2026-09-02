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
