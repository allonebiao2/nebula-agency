# MON BÉNIN · ce que tu dois m'apporter

> Écrit le 2026-08-11, à ta demande. Tout ce qui suit est du **contenu que je
> ne peux pas fabriquer honnêtement à ta place**. Le reste (code, dessin,
> textes, sons, mise en ligne) est déjà fait ou je le fais seul.

**Où en est le site :** https://dev.mon-benin.pages.dev · 8 lieux, 8 vraies
photos sous licence, 8 ambiances sonores, 107 contrôles verts, logo posé.

---

## La règle qui commande tout le reste

**Un Béninois voit une erreur sur son pays en deux secondes, et le charme
tombe.** C'est pour ça que je ne remplis aucun trou tout seul : une fausse
photo de Ganvié, une histoire inventée ou une date approximative détruisent en
une seconde ce que le reste du site construit en sept minutes.

---

## 0. BÉNINNÉO · le photographe, et ce qu'il faut de lui

**Décidé le 2026-08-11 :** les photos viendront de **Béninnéo**, et son
Instagram est mis **en valeur**, pas relégué en petit en bas de page. Trois
endroits, et c'est le premier qui compte :

1. **Sur chaque photo du voyage** : « Photographie · Béninnéo », dans la ligne
   qui porte déjà la légende. C'est le seul crédit que la plupart des visiteurs
   verront, parce que peu de gens vont jusqu'au pied de page.
2. **Un bloc à son nom dans le pied**, avec un vrai bouton vers son Instagram,
   au-dessus de la liste des licences.
3. **Dans le partage** : quand une de ses photos porte l'aperçu, son nom suit.

### ⚠️ Deux choses avant de poser une seule image

- **Créditer n'est pas être autorisé.** Le crédit dit d'où vient la photo, il
  ne donne aucun droit de la publier. Il me faut **son accord écrit**, une
  phrase suffit : « j'accepte que mes photos soient publiées sur le site Mon
  Bénin, avec mon nom et mon Instagram ». Message par message, c'est valable.
  Sans ça, le site publie l'œuvre de quelqu'un sans son autorisation, et c'est
  exactement le reproche qu'on ferait à un concurrent.
- **Son identifiant Instagram exact, copié depuis l'application.** Je ne le
  devine pas et je ne l'écris pas de mémoire : un lien qui tombe sur le mauvais
  compte est pire que pas de lien. (C'est la faute de l'adresse email inventée
  chez Hillary, on ne la repaie pas.)

### ⚠️ Et une limite technique qu'il vaut mieux connaître tout de suite

**Instagram ne rend jamais une image au-delà de 1 080 px de large**, et il la
recompresse. Sur ce site, une photo occupe **tout l'écran** : 1 080 px passent
sur un téléphone, et se voient sur un ordinateur.

**Donc : demande-lui les fichiers d'origine**, ceux de son appareil ou de sa
galerie, pas les images téléchargées depuis sa page. C'est la même démarche,
et ça change tout à l'affichage. Si on n'a que les versions Instagram, on les
utilise, mais en cadre plus petit, pas en plein écran.

Je mesure chaque fichier reçu, un par un :

```bash
python benin-mon-pays/_entrer_photos.py _partage
```

Il dit, pour chaque image : portrait ou paysage, taille réelle, si elle est
passée par une messagerie (le poids par pixel le trahit), et **ses coordonnées
GPS quand elle en porte**. Une photo géolocalisée se pose toute seule à sa
latitude sur la route, et le kilomètre se calcule au lieu de se deviner.

## 0 bis. CE QUE JE FAIS DE CHAQUE IMAGE QUE TU M'ENVOIES

**Demande de Mongazi : « pour chaque image, fais des recherches et parle de ce
que je t'envoie pour enrichir l'histoire, mettre la culture et le pays en
avant. »** La méthode, à chaque photo :

1. **J'identifie ce qu'elle montre**, précisément : le lieu, l'objet, le geste.
   Si je ne suis pas sûr, **je te le demande** au lieu de deviner.
2. **Je cherche**, et je ne garde que ce qui est **public et vérifiable** : une
   date, un chiffre, un nom, une décision. Chaque fait du site l'est déjà.
3. **J'écris le texte du lieu** : pas une légende de carte postale, ce qui
   fait que cet endroit existe. Ganvié n'est pas « un joli village sur
   pilotis », c'est un village bâti sur l'eau **parce que l'eau était la seule
   chose qui sauvait des razzias**. C'est ça, mettre la culture en avant.
4. **Si une source manque ou si deux sources divergent, je l'écris dans le
   texte.** ⛔ Aucune histoire inventée, jamais. Un Béninois voit une erreur
   sur son pays en deux secondes, et le charme tombe.
5. **Je te donne mes sources**, pour que tu puisses trancher quand un ancien
   ou un guide dit autre chose que l'encyclopédie. Sur ce pays, c'est souvent
   l'ancien qui a raison.

## 1. LES PHOTOS · c'est le premier levier, très loin devant

**Ce qu'il y a aujourd'hui :** 8 photos vraies, mais **empruntées** (Wikimedia
Commons, CC BY et CC BY-SA). Elles sont belles et légales, et elles ont trois
défauts : le crédit de l'auteur est **obligatoire** et il est affiché en bas de
page, elles sont **en paysage** alors que le site est un plein écran vertical,
et **tout le monde peut les utiliser**. Ce ne sont pas nos images.

### Ce qu'il me faut, par lieu : DEUX photos

| | Ce que c'est | Pourquoi |
|---|---|---|
| **A · l'arrivée** | très large, on voit le lieu entier | c'est le plein écran, le premier choc |
| **B · le détail** | serré sur une main, une matière, un geste | c'est ce qui fait qu'on y croit |

### Le format, sans négociation

- **En portrait**, jamais en paysage. 9:16 ou 4:5. Le site est vertical.
- **Au moins 2 000 px** sur le grand côté. En dessous, ça bave en plein écran.
- **Le fichier d'origine**, pas la version WhatsApp (WhatsApp divise le poids
  par 10 et ça se voit en grand).
- **Le matin avant 9 h ou après 16 h.** À midi le soleil écrase tout.
- **Aucun filtre, aucun logo, aucune date incrustée.**

### Ce qui est interdit et ne passera pas

- ⛔ **Une personne reconnaissable sans son accord écrit.** Un simple message
  WhatsApp « j'accepte que ma photo soit publiée sur le site Mon Bénin » suffit,
  mais il le faut.
- ⛔ **Jamais un enfant**, même avec l'accord des parents.
- ⛔ **Aucune photo prise ailleurs qu'au Bénin.** La moitié des images
  étiquetées « Bénin » sur Internet sont ghanéennes ou togolaises.

### Les 8 lieux, dans l'ordre du voyage

1. **La Porte du Non-Retour**, plage d'Ouidah · km 0
2. **Ouidah**, le temple des Pythons, la Route des Esclaves, la forêt sacrée
3. **Cotonou**, le marché Dantokpa
4. **Ganvié**, le lac Nokoué, les pilotis, une pirogue
5. **Abomey**, les bas-reliefs, les palais
6. **Koutammakou / Boukoumbé**, une Tata Somba
7. **La Pendjari**, un baobab, la savane
8. **Malanville**, le fleuve Niger, les pirogues

**Si tu ne peux en faire qu'un seul :** la Porte du Non-Retour. C'est le
premier écran, celui qui décide si on reste.

---

## 2. LES VOIX · ce qui manquerait encore à un site parfait

Les trois vidéos que tu m'as envoyées comme références sont sublimes et
**froides** : aucune n'a de voix humaine. C'est exactement là que ce site peut
les dépasser, et c'est la seule chose que je ne peux pas fabriquer.

**Ce qu'il me faut :** par lieu, **30 à 45 secondes** de quelqu'un qui est
d'ici et qui raconte.

- Pas une description du lieu. **Un souvenir précis.** Pas « Ganvié est un
  village sur pilotis », mais « mon grand-père m'a appris à ramer ici, j'avais
  six ans, l'eau était plus haute ».
- **En français** pour la première version. Si la personne préfère le fon, le
  yoruba ou le bariba, c'est encore mieux : on met le sous-titre.
- **Enregistré au téléphone**, dans une pièce fermée, sans ventilateur, sans
  télévision. La qualité du téléphone suffit largement, le bruit de fond non.
- **Envoie le fichier**, pas un vocal WhatsApp réécouté et réenvoyé.
- Il me faut **le prénom, le lieu et l'accord de publication** de chaque
  personne.

---

## 3. LES 3 LIEUX QUE TU AS DÉCIDÉS ET QUI NE SONT PAS ENCORE CONSTRUITS

Tu as tranché 11 lieux le 2026-08-10. Le site en porte 8. Les trois autres :
**Porto-Novo** (« retourner »), **Grand-Popo** (« mêler »), **Dassa**
(« compter »).

Le bouton disait « Les onze lieux » alors qu'il y en a huit : **je l'ai corrigé
aujourd'hui**, et un contrôle vérifie désormais que le mot et le nombre
concordent.

**Pour chacun des trois, il me faut quatre choses :**

1. **Le fait que seul quelqu'un d'ici connaît.** Une phrase. C'est ce qui fait
   la section. Pour Ganvié c'était : le village est sur l'eau **parce que
   l'eau était la seule chose qui sauvait des razzias**.
2. **Une date ou un chiffre vérifiable** (une fondation, une hauteur, un
   nombre). Je vérifie derrière, mais il me faut le point de départ.
3. **Ce qu'on y fait avec les mains**, pour l'animation. Le verbe est déjà
   choisi, il me faut le geste réel.
4. **Les deux photos** (§1).

---

## 4. L'ANGLAIS

Tu as décidé **bilingue FR/EN dès la sortie**, et la cible est la diaspora
afro-descendante, largement anglophone. **La traduction, je la fais.** Ce qu'il
me faut de toi, c'est ta décision sur deux points :

- **Le nom reste-t-il « Mon Bénin » en anglais ?** Mon avis : oui. « My Benin »
  affaiblit, « Mon Bénin » sonne comme un nom propre et garde le pays français
  d'Afrique de l'Ouest dans le titre.
- **Les noms de lieux ne se traduisent pas** (« La Porte du Non-Retour » reste,
  avec « The Door of No Return » entre parenthèses la première fois). Confirme.

---

## 5. LES HALTES · les commerces sur la route

C'est la couche qui transforme l'objet éditorial en produit. Elle est
**conçue, pas ouverte**, et c'est volontaire : une plateforme avec deux salons
dedans a l'air morte.

**Ce qu'il me faut de toi :** l'**accord écrit** des cinq artisans déjà clients
(Angélique, Hillary, HH Design, Au Braisé d'Or, Saeir Thiam). Rien ne part en
ligne sans. Message prêt à envoyer au §9.

**Et par halte, quatre choses, toujours les mêmes :**

1. **Le geste** : 10 secondes de mains qui travaillent, sans parole, en
   portrait.
2. **La voix** : 30 à 40 secondes, la personne raconte pourquoi elle fait ça.
3. **La matière** : 2 ou 3 photos serrées (le bois, le tissu, la braise, l'or).
4. **La porte** : son numéro WhatsApp, confirmé, testé une fois.

⚠️ **On ne vend pas la place sur la carte.** Un commerce apparaît à sa
**latitude réelle**, et la position ne s'achète pas. Ce qui se paie, c'est la
profondeur (le geste, la voix, la matière). C'est ce qui permet à un salon de
coiffure de cohabiter avec la Porte du Non-Retour sans que ce soit obscène.

---

## 6. LE DOMAINE

Le site vit sur `dev.mon-benin.pages.dev`. Tu as dit « le vrai domaine plus
tard ». Quand tu veux le prendre, il me faut **ton choix entre `mon-benin.com`
et un `.bj`**, et l'achat (je ne paie pas à ta place). Le jour où il est posé,
je dois **rouvrir les robots des IA dessus** : Cloudflare les bloque par
défaut, et le réglage n'existe nulle part dans le tableau de bord.

---

## 7. LES SONS RÉELS · plus tard, mais je le note

Les 8 ambiances sont **générées** (WaveSpeed), et le pied de page le dit noir
sur blanc : ce sont des matières, pas des enregistrements des lieux. Une
ambiance fabriquée présentée comme « le bruit de Ganvié » serait le même
mensonge qu'une fausse photo.

Le jour où quelqu'un y va : **60 secondes de son par lieu**, téléphone posé,
personne ne parle, personne ne bouge. Ça remplace la matière générée et ça
change tout.

---

## 8. CE DONT JE N'AI **PAS** BESOIN

Pour que tu ne perdes pas de temps :

- ❌ **Les textes** : ils sont écrits, vérifiés et sourcés. Tu les relis, tu ne
  les écris pas.
- ❌ **Les dessins, les cartes, les icônes, le logo** : tout est dessiné en
  interne, rien ne vient d'ailleurs.
- ❌ **Les traductions.**
- ❌ **Un cahier des charges.** Les 13 décisions du 2026-08-10 suffisent.
- ❌ **Des images trouvées sur Internet.** Sans licence vérifiée fichier par
  fichier, elles ne rentrent pas.

---

## 9. DEUX MESSAGES PRÊTS À COPIER

### Pour celui ou celle qui prend les photos

> Bonjour, je prépare un site qui fait découvrir le Bénin, lieu par lieu.
> J'ai besoin de photos de [LIEU]. Deux photos : une très large où on voit tout
> le lieu, et une serrée sur un détail, des mains, une matière, un objet.
> **En portrait** (comme une story), pas en paysage. Le matin avant 9 h ou
> après 16 h, jamais en plein midi. Envoie-moi **le fichier d'origine**, pas la
> version compressée. Pas de filtre, pas de logo, pas de date sur l'image.
> Et si une personne est reconnaissable, il me faut son accord écrit, même par
> message. Jamais d'enfant.

### Pour les cinq artisans (l'accord des haltes)

> Bonjour [PRÉNOM], je construis un site qui fait voyager à travers le Bénin,
> de la Porte du Non-Retour jusqu'au fleuve Niger. Je voudrais y présenter
> votre atelier, à l'endroit exact où il se trouve sur la route. Ce serait une
> courte séquence : vos mains qui travaillent, votre voix qui raconte, deux ou
> trois photos de la matière, et un bouton qui ouvre WhatsApp chez vous.
> C'est gratuit et vous pouvez demander le retrait quand vous voulez.
> Répondez-moi simplement « j'accepte » si vous êtes d'accord, j'ai besoin de
> l'écrit avant de commencer.

---

## L'ordre dans lequel je te conseille de t'y prendre

1. **Les deux photos de la Porte du Non-Retour.** Un seul lieu, le premier
   écran. Ça change le site plus que tout le reste.
2. **Une voix, une seule**, sur ce même lieu. Pour voir l'effet avant de
   lancer les huit.
3. **L'accord écrit des cinq artisans.** C'est du message, pas du déplacement,
   et ça débloque la couche qui rapporte.
4. Le reste des photos, lieu par lieu, sans se presser.

**Le cap :** les **Vodun Days de janvier**, à Ouidah. C'est la fenêtre où le
monde regarde le Bénin, et c'est là que ce site doit être complet.
