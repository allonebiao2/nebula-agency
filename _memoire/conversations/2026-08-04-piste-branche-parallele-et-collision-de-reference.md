# PISTE — une branche parallèle, et une collision de référence dans le produit en ligne

## Date : 2026-08-04
## Sujet principal : deux sessions ont construit PISTE le même jour, sans se voir

---

## Ce qui s'est passé, et c'est la vraie leçon

Une session distante (`claude/continuation-xu5ma7`) a repris `piste/` à l'état
du commit `396ed4f` : la fiche produit, la direction artistique, les données du
3 août et le barème étaient là, mais **`index.html` appelait `src/main.jsx` qui
n'existait pas**, et `donnees.js` ne compilait plus.

Elle a donc construit la V1 : vitrine, questionnaire, calculateur, paiement,
cockpit, page d'origine des données, 95 contrôles, garde-barrière de mise en
ligne.

**Pendant ce temps, `main` avait avancé de 20 commits sur exactement le même
produit** — et beaucoup plus loin : générateur, carnet client, moteur de
collecte nocturne, Supabase, 7 817 fiches, 88 décisions, 130 contrôles, et
**le site est en ligne** (`piste.nebula-agency.online`).

> **`main` bouge pendant qu'on travaille.** C'était déjà le piège n° 1 du dépôt.
> Cette fois il n'a pas coûté un merge malheureux, il a coûté **une journée de
> travail refaite en double**. Le `git fetch origin` ne se fait pas seulement
> avant de fusionner : il se fait **avant de commencer**, et sur le dossier
> qu'on s'apprête à ouvrir.

La branche parallèle est conservée pour mémoire au commit `445c8f6`.
⛔ **Elle ne doit JAMAIS être fusionnée dans `main` :** elle supprimerait le
générateur, le carnet, le moteur de collecte et Supabase. Le seul contenu qui
mérite de remonter est décrit ci-dessous.

---

## ⚠️ Ce que la branche parallèle a trouvé, et qui concerne le produit EN LIGNE

Les quatre défauts trouvés en route ont été confrontés au code de `main`.

| Défaut | Dans `main` ? |
|---|---|
| En SVG, un `transform` CSS efface l'attribut : les repères retombent hors cadre | ✅ **déjà corrigé** (`ddb0ce2`), trouvé indépendamment |
| Un hook après un retour anticipé (React #310) | ✅ sans objet : le loquet est un composant séparé |
| Une carte en `rotateY(-72deg)` sous perspective pousse la page de côté | ⚠️ **présent, mais bref** : `.porte` est une `animation` jouée au chargement, la boîte géante n'existe que 0,85 s |
| **Une référence de commande trop courte** | 🔴 **PRÉSENT, ET IL COÛTE UN CLIENT** |

### 🔴 `nouvelleReference()` : 4 caractères, et le cockpit refuse les doublons

```js
// piste/src/donnees.js, sur main
const A = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'   // 32 caractères
for (let i = 0; i < 4; i++) s += A[...]         // 32^4 = 1 048 576
```

À la capacité annoncée (**décision 37 : 5 à 10 commandes par jour**), soit
3 650 commandes sur un an, le calcul des anniversaires donne **≈ 6 collisions
attendues par an**. Sur trois mois : ≈ 0,4, donc c'est déjà jouable dès le
premier trimestre.

Et voici pourquoi ça ne passe pas inaperçu, ça se paie :

```js
// piste/src/composants/Cockpit.jsx, ranger()
if (commandes.some((c) => c.ref === o.ref)) {
  setErreur(`La commande ${o.ref} est déjà dans la liste.`)
  return                       // ← la commande n'est jamais rangée
}
```

**Un vrai client, avec un vrai paiement, dont la référence tire la même
combinaison qu'une commande déjà rangée, est refusé comme un doublon.** Mongazi
lit « déjà dans la liste », croit avoir collé deux fois, et passe à la suite.
Le client a payé et ne recevra jamais son carnet.

**Le correctif tient en un caractère** : `i < 6` au lieu de `i < 4` porte le
compte à **1,07 milliard** de combinaisons, soit une collision tous les
plusieurs siècles au rythme prévu. Une référence à six caractères se dicte
aussi bien au téléphone qu'une à quatre.

**Et la ceinture en plus des bretelles** : que le cockpit ne compare pas
seulement la référence. Deux commandes ne sont le même papier que si la
référence **et** l'email correspondent ; sinon ce sont deux clients, et les
deux doivent apparaître.

✅ **Bonne nouvelle sur le rayon d'action** : le carnet du client est ouvert par
un **jeton distinct** (`piste_carnet`, RPC Supabase), pas par la référence. Une
collision ne fait donc **pas** lire le carnet d'un client à un autre. Le dégât
s'arrête à la prise de commande.

---

## Les leçons vraiment neuves

1. **Avant d'ouvrir un dossier, `git fetch origin` et regarder si quelqu'un y
   travaille.** Le coût de l'oubli n'est pas un conflit : c'est une journée
   refaite.
2. **Un identifiant que l'humain dicte se dimensionne sur le volume annoncé**,
   pas sur l'intuition. 4 caractères « ça suffit largement » se traduit en
   6 collisions par an à 10 commandes par jour. Le calcul prend trente
   secondes.
3. **Un test statistique écrit plus serré que le hasard ne le permet
   clignote**, et on finit par ne plus le croire. Deux contrôles ont dû être
   recalibrés (répartition des caractères, absence de collision) parce qu'ils
   échouaient sur du hasard parfaitement sain.
4. **Une animation signature doit se jouer à l'arrivée, pas au chargement.** Une
   `animation` CSS posée sur une classe se joue hors écran ; celui qui descend
   trouve le geste déjà consommé.

## Prochaine étape

- **Décider** : appliquer le correctif de la référence (un caractère + la
  comparaison sur l'email) sur une branche partie de `main`, et le déployer.
- La branche `claude/continuation-xu5ma7` reste un dossier mort à consulter,
  jamais à fusionner.
