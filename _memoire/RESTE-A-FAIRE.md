# Ce qui reste à faire

> **Ce fichier ne contient QUE ce qui n'est pas fait.** Ce que Mongazi a
> demandé est dans `DEMANDES-MONGAZI.md`. Quand une ligne est faite, on la
> retire d'ici et on la marque là-bas.
> Dernière mise à jour : 2026-08-11.

---

## 🔴 CE QUI BLOQUE, ou peut coûter de l'argent

| Quoi | Pourquoi c'est grave | Qui débloque |
|---|---|---|
| **Les 11 mesures de la robe ovale**, jamais validées par l'atelier depuis le 2026-08-06 | Trois des cinq robes d'Hillary en dépendent. Une mesure qui manque, c'est une pièce coupée faux ; une de trop, c'est une cliente qui abandonne le formulaire. Le message est prêt : `clients/10-hillary-m-styl/MESSAGE-MESURES-HILLARY.md` | **Hillary** |
| **Le jeu `haut_pantalon`**, créé le 2026-08-11, encore moins validé | Deux robes l'utilisent. Et « Longueur pantalon » sur une robe se lit mal pour une cliente : à faire reformuler | **Hillary** |
| **Le prix en dollar de la Robe de ville bleue** : 67 $ pour 30 000 F, soit 448 F/$ quand tout le reste du site suit 556 F/$ | Un écart de +24 %. Et 67 est exactement le prix express en euro de la même pièce : ça sent la valeur qui a glissé d'une case à l'autre. **Non corrigé** : ses prix sont les siens | **Mongazi / Hillary** |
| **Le disque de la machine est saturé** : 459 Mo libres sur 271 Go | Bloque l'installation des outils, le démarrage du navigateur de test, et les déploiements. Nettoyé trois fois dans la session, il se remplit à nouveau | **Mongazi** |

---

## 🌍 MON BÉNIN — https://dev.mon-benin.pages.dev

### La suite du voyage
- [ ] **Les 3 lieux qui manquent** sur les 11 décidés, avec leur verbe :
      **Porto-Novo « retourner »** (l'église baroque brésilienne devenue
      mosquée : c'est l'histoire des affranchis revenus du Brésil, et c'est
      la station la plus forte pour la cible diaspora), **Grand-Popo
      « mêler »** (à la Bouche du Roi, le Mono rencontre la mer),
      **Dassa « compter »** (les 41 collines).
- [ ] **La version anglaise complète.** Décidée « dès la sortie », pas faite.
      La cible est la diaspora, largement anglophone. Avec `hreflang` et
      l'aperçu de partage qui suit la langue.
- [ ] **Les voix des habitants.** 30 à 40 secondes par lieu, enregistrées au
      téléphone. C'est ce qui rend le site non copiable : n'importe qui peut
      acheter une image de drone, personne d'autre n'a la voix du pêcheur de
      Ganvié.
- [ ] **De vrais enregistrements de son**, pour remplacer les ambiances
      générées. ⚠️ Un son fabriqué présenté comme « le bruit de Ganvié » est
      le même mensonge qu'une photo générée du lieu. C'est écrit dans le pied
      de page en attendant.
- [ ] **Plus de photos**, et des photos en **portrait** : le site est en
      plein écran vertical, et 90 % des photos de tourisme sont en paysage.

### L'annuaire d'entreprises
- [ ] **La note due à Mongazi** avant qu'il tranche : ce que perdrait PISTE
      (100 F la fiche, exclusivité 90 jours, 7 817 fiches) contre ce que
      gagnerait l'annuaire. Il a répondu « à creuser, je veux comprendre
      d'abord ».
- [ ] **L'annuaire lui-même**, en objet SÉPARÉ, même identité visuelle.
      ⚠️ Un parcours linéaire de 11 lieux ne porte pas 5 000 fiches.
- [ ] **Les haltes d'artisans** : Angélique, Hillary, HH Design, Au Braisé
      d'Or, Saeir Thiam. ⚠️ **Il faut leur accord écrit**, Mongazi le demande.

### La sortie
- [ ] **Le vrai domaine**, quand Mongazi l'achètera. ⚠️ Il faudra **rouvrir
      les robots IA dessus** (`PUT /zones/{zone}/bot_management`) : Cloudflare
      les bloque par défaut, et sans ça ChatGPT et Perplexity ne pourront
      jamais citer le site. Pour une cible diaspora qui cherche « où voir la
      Porte du Non-Retour », ce n'est pas un détail.
- [ ] **Cap sur les Vodun Days de janvier**, à Ouidah : le moment de l'année
      où le monde regarde le Bénin.

---

## 👗 HILLARY M. STYL — https://hillary-m-styl.pages.dev

- [ ] Les **mesures** (voir en haut, c'est le blocage n° 1).
- [ ] **Les vrais noms** des trois robes qui portent encore un descripteur de
      couleur (bleue, verte, à tulle), si elle en a.
- [ ] **La photo de face de la Robe de ville bleue** : sa photo principale est
      une vue de DOS. Antérieur, mais ça se voit maintenant que les autres
      pièces ont une face.
- [ ] **Les frais et délais de livraison par pays** : le site affiche « à
      confirmer » pour les pays sans tarif, ce qui est honnête mais empêche
      d'annoncer un total.
- [ ] **La matière de chaque pièce**, le jeu « haut + jupe » de Mira, et le
      libellé exact de chaque modèle.
- [ ] **De vrais avis** de clientes.
- [ ] **Tester le lien WhatsApp** `wa.me/22951374793` en envoyant un vrai
      message. ⚠️ Au Bénin les formes à 8 et 10 chiffres coexistent : si ça
      ne s'ouvre pas, la bonne forme est `2290151374793`.
- [ ] Les **8 autres sons** du plan, si les 6 posés donnent envie.

---

## 🎨 ANGY ART — https://angy-art.pages.dev

- [ ] **Les photos des œuvres seules** : fond neutre, avec titre, technique et
      dimensions. Elles iront dans un tableau **séparé** des mises en
      situation, jamais mélangées.
- [ ] **Son adresse d'atelier**, si elle veut la publier.
- [ ] **De vrais avis.**
- [ ] **Tester son numéro WhatsApp** : +229 01 52 00 64 90.

---

## 🧰 LE PARC

- [ ] **La marque de déploiement** sur les autres sites : la protection
      anti-cache-empoisonné de PISTE, demandée par Mongazi le 2026-08-04.
- [ ] **Fusionner `worktree-angy-photos` dans `main`.** La branche porte ANGY
      ART, tout MON BÉNIN et toute la vague HILLARY.

---

## ⚠️ Ce qu'il ne faut pas oublier en reprenant

- **Le disque se remplit.** Vérifier `df -h /c` avant de s'étonner d'une
  lenteur ou d'un délai dépassé : ça se déguise en panne de réseau.
- **Les navigateurs Playwright ont été supprimés** à la demande de Mongazi.
  Seul `chromium-headless-shell` est réinstallé, et c'est suffisant. Si un QC
  refuse de démarrer : `python -m playwright install chromium-headless-shell`.
- **L'alias `dev` d'un déploiement Cloudflare a quelques secondes de retard**
  sur l'URL immuable. Vérifier sur l'URL immuable, ou attendre.
- **Un agent non navigateur reçoit 403** sur `*.pages.dev` : filtrage de bots.
  Vérifier avec un vrai `User-Agent`.
