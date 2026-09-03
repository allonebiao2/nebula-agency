# Message à envoyer à Hillary — les mesures de la robe ovale

> **Pourquoi c'est le point le plus urgent du dossier.**
> Ses **quatre pièces** (Robe de cérémonie, Ensemble Mira, Ensemble JOSY, Robe
> de ville) sont **toutes en robe ovale**. Aujourd'hui le site demande à la
> cliente **11 mesures déduites par nous**, pas validées par l'atelier. Si une
> mesure manque, la pièce est coupée faux ; si une mesure est en trop, la
> cliente se décourage devant le formulaire. C'est le seul endroit du site qui
> peut coûter de l'argent à Hillary.
>
> En attendant, le site affiche honnêtement à la cliente : « Liste de mesures
> en cours de validation par l'atelier. Nous vous rappellerons pour confirmer
> ou compléter ces mesures. » Ça protège la commande, mais ça ne remplace pas
> sa réponse.

---

## Le message, à copier tel quel

Bonjour Hillary,

Pour votre site, j'ai besoin de votre validation sur **un seul point** : les
mesures à demander pour une **robe ovale**. Vos quatre pièces sont dans cette
coupe, donc c'est ce qui décide de tout.

Voici la liste que j'ai mise pour le moment. **Répondez juste par le numéro** :
dites-moi ce qu'on **garde**, ce qu'on **enlève**, et ce qui **manque**.

**Le haut**
1. Épaules
2. Carrure devant
3. Poitrine
4. Tour du sous-sein
5. Tour de taille
6. Tour de hanche

**Les longueurs**
7. Longueur taille
8. Longueur robe courte
9. Longueur robe longue

**Les manches**
10. Tour de manche
11. Longueur manche

Trois questions en plus, très rapides :

- Est-ce qu'il faut demander **les deux longueurs** (courte et longue), ou
  seulement celle qui correspond au modèle choisi ?
- Y a-t-il une mesure que vous prenez **toujours** et qui n'est pas dans la
  liste ? (longueur dos, tour de bras, hauteur de poitrine, tour d'encolure…)
- Si une cliente ne connaît qu'**une partie** de ses mesures, laquelle vous
  suffit pour commencer, et lesquelles peuvent attendre le rendez-vous ?

Merci beaucoup, c'est le dernier point qui bloque.

---

## Ce qu'on fait de sa réponse

| Elle répond | On fait |
|---|---|
| La liste est bonne | On retire le bandeau « en cours de validation ». Une ligne dans `garde-moteur.js` : `aValider: true` → supprimé. |
| Il faut enlever des mesures | On retire les lignes correspondantes de `MESURES.robe_ovale`. |
| Il en manque | On ajoute, en respectant les trois groupes (`Le haut`, `Les longueurs`, `Les manches`). |
| Certaines sont facultatives | Le moteur sait déjà faire : une mesure vide part en « à prendre ensemble », et la moitié suffit pour avancer. |

⚠️ **On édite `_v4/garde-moteur.js`, jamais `vitrine.html`.** Puis
`python _v4/_assembler.py`, puis `python _build.py`, puis `python _qc.py`.
L'assembleur **refuse d'écrire** si l'un des 18 identifiants du moteur manque.

---

## Les autres questions en attente, si l'occasion se présente

Ce sont les **8 informations** du bloc « ZONE À COMPLÉTER ». Aucune ne bloque
autant que les mesures, mais elles se posent bien dans le même message :

1. **Les frais de livraison par pays** — le site affiche « à confirmer » pour
   les pays sans tarif, ce qui est honnête mais empêche d'annoncer un total.
2. **Le délai d'acheminement par pays**, pour calculer la date de disponibilité.
3. **L'adresse et les horaires de l'atelier** — aujourd'hui le site dit
   « Retrait sur rendez-vous, le point de retrait vous est donné sur WhatsApp ».
   C'est très bien si elle préfère ne pas publier son adresse.
4. **La matière de chacune des quatre pièces** (wax, bazin, satin…).
5. **Le jeu « haut + jupe » de l'ensemble Mira** : est-ce vendu séparément ?
6. **Le libellé « Robe de ville »** : c'est le nom que nous avons donné, pas
   forcément le sien.
7. **De vrais avis** de clientes.
8. **Tester le lien WhatsApp** : `wa.me/22951374793`. ⚠️ Au Bénin les formes à
   8 et 10 chiffres coexistent et les gens donnent souvent la mauvaise sans le
   savoir. Si le lien ne s'ouvre pas, la forme correcte est `2290151374793`.
