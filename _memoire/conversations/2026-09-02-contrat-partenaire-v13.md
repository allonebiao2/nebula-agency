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
| **4.5** | Les **logiciels édités par NEBULA sont hors du programme** : pas vendus, pas chiffrés, **aucune commission**. Le partenaire signale et n'engage rien |
| **4.1 et 6.2 bis** | Les **frais de réactivation chiffrés à 5 000 F**, et « aucun frais si le client règle pendant les 7 jours de courtoisie » |
| **8.13** | Treizième engagement : ne jamais présenter ni chiffrer un produit de l'article 4.5 |
| **14.1 à 14.5** | Données personnelles étoffées : minimisation, information de la personne, destruction en fin de contrat **y compris sur le téléphone personnel**, alerte sans délai en cas de fuite, APDP nommée |

⚠️ **L'Outil sur mesure a été GARDÉ** alors que Mongazi n'a cité que trois offres. Raison :
le socle commercial, qui est la source de vérité, le porte explicitement (l'escalier §1.3, la
certification §5.7, le barème §4.5). Le retirer aurait supprimé une ligne de revenu partenaire
contre la source de vérité. Il est donc dans le contrat **avec sa condition d'accès**.
**À confirmer par Mongazi.**

---

## Les documents alignés derrière

- **Socle commercial §8** : la section « ce qui n'est PAS dans le programme » ne parlait que
  de **Boussole**. Elle porte maintenant les **quatre** logiciels dans un tableau, plus un
  §8.2 : le partenaire peut les **citer comme preuves de capacité**, il ne les propose pas.
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

- **confirmer** que l'Outil sur mesure reste dans le périmètre partenaire (voir plus haut) ;
- les **13 documents de vente** n'ont pas tous été relus : seuls le contrat, le socle et le
  manuel ont été alignés. Les guides 03/04/05 ne parlent pas des logiciels édités ;
- IFU et RCCM à porter dès obtention (un avenant d'une ligne).
