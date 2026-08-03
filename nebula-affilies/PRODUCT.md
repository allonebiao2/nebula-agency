# NEBULA Affiliés — fiche produit

> Le bureau virtuel du programme partenaires de NEBULA Agency.
> Deux faces : le **cockpit** de Mongazi, et l'**espace partenaire**.
> Écrit le 2026-08-03, avant la refonte « lisible pour un débutant ».

## Register

**Product.** Le design SERT le produit, il n'est pas le produit. Personne ne vient
ici pour admirer une interface : on vient voir qui a vendu, qui doit être payé, et
combien on a gagné. Toute décision visuelle se juge à « est-ce qu'on trouve
l'information plus vite ? », jamais à « est-ce que c'est beau ? ».

## Qui s'en sert, et dans quelles conditions

**Mongazi (le cockpit).** Fondateur, à Cotonou. Il valide des candidatures, suit
des clients, déclenche des paiements. Souvent sur téléphone, entre deux rendez-vous.
Sa question permanente : *qui dois-je payer, et qui dois-je relancer ?*

**Les partenaires (l'espace partenaire).** Des commerciaux indépendants d'Afrique de
l'Ouest, **débutants pour la plupart**, sans culture des outils de gestion. Beaucoup
n'ont jamais utilisé de tableau de bord. **Presque tous sur un téléphone d'entrée de
gamme, souvent en plein soleil, souvent en 3G.** Leur question permanente :
*combien j'ai gagné, et qu'est-ce que je dois faire maintenant ?*

**Conséquence directe, et non négociable :** si une personne qui n'a jamais utilisé
un tableau de bord ne comprend pas un écran en cinq secondes, l'écran est raté.
Le mot juste bat le mot élégant. « Pipeline » ne veut rien dire ; « Où en sont tes
clients » se comprend sans explication.

## Ce que le produit doit permettre, par ordre

1. **Voir ce qu'on a gagné**, et ce qui reste à encaisser.
2. **Savoir quoi faire maintenant** : une action, pas une liste de chiffres.
3. **Suivre ses clients** de la prise de contact au paiement.
4. **Recruter et suivre son équipe** (côté cockpit : valider, payer).

## Personnalité

**Sérieuse, chaleureuse, directe.** C'est un outil qui parle d'argent réel : il doit
inspirer confiance comme une banque, mais parler comme un collègue. Ni jargon
d'entreprise, ni familiarité forcée. Le tutoiement est déjà en place et il reste :
il correspond à la relation.

## Références retenues (données par Mongazi le 2026-08-03)

**Helios Investments** et **Aura Store**. Ce qui est retenu d'elles, précisément :

| Ce qu'on prend | Pourquoi |
|---|---|
| **Navigation écrite**, texte + icône | L'actuelle est en icônes seules : personne ne devine ce qu'est une icône de coupe ou de sablier |
| **Chiffres avec leur tendance** (+15 % vs période précédente) | Un nombre seul ne dit pas si ça va bien. La flèche, si |
| **Vrais tableaux** avec pastilles de statut et action au bout de la ligne | Les cartes empilées forcent à dérouler ; le tableau se lit en diagonale |
| **Tout au-dessus de la ligne de flottaison**, espacement serré | Sur téléphone, chaque écran de défilement perdu est une information non vue |
| **Recherche en haut** | À dix partenaires on scrute, à cinquante on cherche |

## Anti-références

- **L'état actuel** : navigation en icônes muettes, quatre chiffres qui remplissent
  un écran de téléphone, mots d'initiés (« Pipeline », « RCM », « palier »).
- **Le tableau de bord décoratif** : gros nombre, dégradé, halo, et rien à en faire.
- **Le jargon d'agence.** Si un mot demande une explication, c'est le mot qui est
  faux, pas le lecteur.

## Accessibilité, comme contrainte de conception

Ce ne sont pas des cases à cocher : ce sont les conditions réelles d'usage.

- **Contraste ≥ 4,5:1** pour tout texte courant. Un téléphone au soleil pardonne
  moins qu'un écran de bureau.
- **Cibles tactiles ≥ 44 px.** On travaille au pouce, debout, dans la rue.
- **Deux thèmes, sombre et clair, au choix de la personne** (décision Mongazi,
  2026-08-03). Le clair existe pour le plein jour, pas pour la mode.
- **`prefers-reduced-motion` respecté**, et **mode performance adaptatif** déjà en
  place : les effets d'ambiance se calment sur appareil modeste.
- **Poids et latence comptent** : la 3G est la norme, pas l'exception.

## Principes de conception, propres à ce produit

1. **Nommer les choses comme le lecteur les nomme.** Pas comme le code les nomme.
2. **Un écran, une question.** Si un écran répond à trois questions, il en faut trois.
3. **Le chiffre seul est muet.** Toujours lui donner sa comparaison ou son action.
4. **Le vide se remplit de mots.** Un écran sans données doit dire quoi faire pour
   qu'il y en ait, jamais rester blanc.
5. **Ce qui est rare va au fond.** Les réglages ne méritent pas la même place que
   « qui dois-je payer ».
