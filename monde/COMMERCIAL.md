# LE COMMERCIAL NEBULA · le vendeur de chaque boutique (demandé par Mongazi le 2026-11-13)

> **Ses mots, tels quels** : « après, dans chaque boutique ou structure, pour commencer ça sera déjà
> Hillary, y'aura un commercial habillé en gris et marqué avec le logo NEBULA Agency, qui lui est là pour,
> quand le client est un peu longtemps dans la boutique, approcher, et il demande toujours : "Vous auriez
> quelques minutes que je vous parle ?" ; et le client peut choisir entre oui et non. Quand c'est oui, il doit
> être un expert ultra-puissant en vente : son but, c'est de pousser à la vente au maximum, mais sans
> encombrer. Pour le moment il n'a pas encore d'intelligence artificielle, mais plus tard il en aura. Mais
> quand on va le créer, il pourra poser des questions prédéfinies avec des réponses adaptées à ce que le
> client choisira comme réponses : tout un ou plusieurs workflows conversationnels autour de la structure,
> intégrés en lui. »
>
> **Statut : 💤 à construire « après »** (pas commencé). Il ne passe pas devant le mini-objectif réalisme en
> cours (`REALISME.md`) sans que Mongazi le demande.

## Ce que j'en comprends (à valider par Mongazi)

- **Un personnage de plus dans CHAQUE lieu** (le socle, pas seulement Hillary) : un vendeur **habillé en
  gris**, **marqué du logo NEBULA Agency**. Il est clairement un vendeur, pas un client : la règle « PNJ
  visiteuses, jamais de fausses clientes » reste entière.
- **Il approche quand le client s'attarde** (« un peu longtemps dans la boutique ») ; jamais pendant un
  dialogue, une fiche, un cadran ou une commande (les règles de l'abordage d'Afi : on ne coupe jamais la
  parole, et pas dans les 3 s qui suivent une conversation).
- **Toujours la même entrée** : « Vous auriez quelques minutes pour que je vous parle ? » → **Oui** / **Non**.
  - **Non** : il s'efface poliment et **n'insiste pas** (« sans encombrer »).
  - **Oui** : un **parcours de vente** : des questions prédéfinies, et des réponses adaptées au choix du
    client ; **un ou plusieurs parcours par structure**, rangés dans le lieu (comme les dialogues
    d'aujourd'hui, `donnees.js` + `socle/dialogue.js`, qui savent déjà faire des arbres à choix).
- **Le but** : « pousser à la vente au maximum, sans encombrer » : poser les bonnes questions (pour quelle
  occasion, quand, quel budget, quelle silhouette), mener à la pièce qui convient, à la fiche, au sac, à la
  commande.
- **Plus tard, une IA** : le même personnage, branché sur l'agent (LE STANDARD / Claude). ⛔ Avec le
  **garde-fou des prix** de LE STANDARD : un montant que le catalogue ne porte pas ne sort jamais.
  ⛔ Le catalogue est **lu**, jamais recopié, dans le parcours comme dans l'IA.

## Les questions ouvertes (à poser à Mongazi le moment venu)

1. Son **prénom**, son **âge**, son allure (le gris : costume, chemise, polo ?).
2. **Quand** il approche : au bout de combien de temps, ou après combien de pièces regardées ?
3. Après un **Non** : il ne revient plus jamais pendant la visite, ou une seule fois plus tard ?
4. **Ce qu'il vend** : les pièces de la boutique seulement, ou aussi **NEBULA** à un visiteur commerçant
   (« vous avez un commerce ? on peut faire la même chose pour vous ») ? Le succès principal du projet est
   « un commerçant qui signe ».
5. Le **logo** : un générateur d'images ne reproduit pas un logo fidèlement ; le logo NEBULA sera posé
   ensuite sur le vêtement 3D (une décalcomanie), à partir du vrai fichier.

## Ce qu'il faudra

- son image et son modèle 3D (Mongazi les génère, consigne à écrire dans `personnages/CONSIGNES.md`, sur le
  modèle des visiteuses), puis Mixamo et `habiller()` comme Afi ;
- un module du socle (`socle/commercial.js`) : le déclencheur, l'approche, le Oui/Non ;
- les parcours de vente de chaque lieu (des nœuds de dialogue, avec leurs choix) ;
- plus tard, le branchement sur l'agent IA.
