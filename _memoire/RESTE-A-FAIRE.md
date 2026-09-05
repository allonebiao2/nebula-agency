# Ce qui reste à faire

> **Ce fichier ne contient QUE ce qui n'est pas fait.** Ce que Mongazi a
> demandé est dans `DEMANDES-MONGAZI.md`. Quand une ligne est faite, on la
> retire d'ici et on la marque là-bas.
> Dernière mise à jour : 2026-09-04.

---

## Luxury Club 229 — deux fuites refermées, une copie périmée à surveiller (2026-09-05)

Le site se déployait avec `.`, c'est-à-dire **tout le dossier client**. Mesuré
en ligne ce jour-là, avant correction :

- `https://luxuryclub229.com/CONTEXT.md` → **200** (les notes internes : prix,
  décisions, « à valider »)
- `https://luxuryclub229.com/assets/_inbox/…` → **200** (**7,2 Mo** de photos
  sources brutes de Gloria)

Aucune page ne les référençait. Ils sont **hors du livrable** depuis
`_outils/_dist.py`, et l'URL du déploiement les rend bien en **404**.

⏳ **À revérifier :** sur le domaine, une **copie périmée** subsiste dans la
couche de Cloudflare Pages (`Age` qui grimpe depuis la même origine,
`s-maxage=604800`). Ni `purge_everything` ni la purge par URL ne l'atteignent —
c'est le cache **de Pages**, pas celui de la zone. Toute clé fraîche (une
requête avec `?x=…`) répond déjà **404**. Ça expire seul en **7 jours au
maximum** : revérifier après le 2026-09-12.

```bash
curl -sI https://luxuryclub229.com/CONTEXT.md | head -1     # doit finir en 404
```

⚠️ **À chercher sur les autres sites du parc** : tout site déployé avec `.`
publie ce que le dossier contient. `clients/` en a plusieurs.

## 🔴 CE QUI BLOQUE, ou peut coûter de l'argent

| Quoi | Pourquoi c'est grave | Qui débloque |
|---|---|---|
| **Les 11 mesures de la robe ovale**, jamais validées par l'atelier depuis le 2026-08-06 | Trois des cinq robes d'Hillary en dépendent. Une mesure qui manque, c'est une pièce coupée faux ; une de trop, c'est une cliente qui abandonne le formulaire. Le message est prêt : `clients/10-hillary-m-styl/MESSAGE-MESURES-HILLARY.md` | **Hillary** |
| **Le jeu `haut_pantalon`**, créé le 2026-08-11, encore moins validé | Deux robes l'utilisent. Et « Longueur pantalon » sur une robe se lit mal pour une cliente : à faire reformuler | **Hillary** |
| **Le prix en dollar de la Robe de ville bleue** : 67 $ pour 30 000 F, soit 448 F/$ quand tout le reste du site suit 556 F/$ | Un écart de +24 %. Et 67 est exactement le prix express en euro de la même pièce : ça sent la valeur qui a glissé d'une case à l'autre. **Non corrigé** : ses prix sont les siens | **Mongazi / Hillary** |
| ~~**Le disque de la machine est saturé**~~ · **mesuré 19 Go libres sur 271 Go le 2026-09-04** | Plus bloquant pour l'instant : les navigateurs de test tournent, les déploiements passent. ⚠️ **À regarder avant chaque gros build** : c'est descendu à zéro octet en pleine fusion git le 19/08, et l'image de machine virtuelle de Claude (11,9 Go) grossit | **Mongazi** |

---

## 🔒 LE PARC : 10 SITES SUR 15 N'ONT PAS DE `_headers`

**Mesuré le 2026-09-04, sur les fichiers ET sur les en-têtes réellement servis.**

| A un `_headers` | N'en a pas |
|---|---|
| Djambar Team · Miss cakes · Angy Art · Boussole · PISTE | Grain d'Esthétique · Little Sun Pearls · WECS · Luxury Skin Clinic · Speed×Weinkeller · HH Design · **Au Braisé d'Or** · **Hillary M. Styl** · site NEBULA · **Mon Bénin** |

Vérifié en ligne, ce ne sont pas que des fichiers absents :

```
angy-art.pages.dev         XFO=1 HSTS=1     ← a un _headers
miss-cakes.pages.dev       XFO=1 HSTS=1     ← a un _headers
hillary-m-styl.pages.dev   XFO=0 HSTS=0
au-braise-dor.pages.dev    XFO=0 HSTS=0
mon-benin.pages.dev        XFO=0 HSTS=0
```

**Ce que ça coûte, concrètement :**

1. **Aucune protection contre le détournement en cadre** (`X-Frame-Options`) ni
   **HSTS**. Cloudflare ajoute `X-Content-Type-Options` tout seul, rien d'autre.
2. **Aucun cache sur les images.** Sans `_headers`, Cloudflare Pages sert
   `max-age=0, must-revalidate` sur **tout** : chez Hillary, les **31 images** de
   la page sont revalidées à chaque visite, sur la 3G de Cotonou.

⚠️ **Les deux réglages vont ensemble, et dans les deux sens** : poser
`immutable` sur `/assets/*` fait gagner le cache **et rend obligatoire le bump du
`?v=` à chaque modification d'un asset** — sans quoi le client reste un an sur
l'ancienne version (Angy Art, 08/08 et 04/09). Ajouter un `_headers` à un site
qui ne versionne pas ses images **crée** le piège du cache périmé.

⛔ **Rien n'a été corrigé** : ce serait un déploiement vers dix sites clients en
ligne. **Mongazi tranche.** L'ordre le plus utile s'il dit oui : les trois qui
prennent des commandes (**Hillary**, **Au Braisé d'Or**, Speed×Weinkeller), en
posant `?v=` sur les assets **avant** `immutable`.

Le gabarit à recopier : `clients/11-angy-art/_headers`.

---

## 🌍 MON BÉNIN — https://mon-benin.pages.dev

> **La liste complète de ce que Mongazi doit apporter, avec les formats exacts
> et les interdits : `benin-mon-pays/CE-QUE-TU-DOIS-APPORTER.md`** (2026-08-11).
> Ordre conseillé : les deux photos de la Porte, puis une voix sur ce même
> lieu, puis l'accord écrit des cinq artisans.
>
> ⛔ **LE BLOCAGE N° 1 : les photos de Béninéo ne sont sur AUCUN disque.**
> Sept images envoyées le 2026-08-11 dans la conversation. Vérifié : `_partage/`,
> Téléchargements, Bureau, Images, Documents, et le Drive. Le document
> **« Mon bénin apport »** ne contient que les quatre textes.
> **Marche à suivre : ajouter les photos DANS ce même Google Doc**, une image
> posée dans un Doc s'extrait à sa taille d'origine. Mongazi ne touche pas au PC.
>
> ⚠️ **BÉNINÉO EST UNE AGENCE DE TOURISME**, pas une page de photos : circuits
> culturels et mémoriels, conciergerie, coffrets EbunBox, boutique. Instagram
> **@mybenineo** (confirmé sur `benineo.com`), WhatsApp **+33 6 46 39 66 46**.
> **C'est un partenaire, pas un fournisseur à qui l'on demande une faveur** :
> ils vendent ce que Mon Bénin donne envie d'acheter. Première halte naturelle.
> ⛔ **Rien de Béninéo n'est publié** tant qu'on n'a pas son **accord écrit**.
>
> ✅ **Le logo est fait** (2026-08-11) : le pays au drapeau, la ligne des
> 700 km, le point d'or au km 0. Voir `benin-mon-pays/CONTEXT.md` §10 bis.

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
      ⚠️ Les 8 photos actuelles sont vraies mais **empruntées** (CC BY et
      CC BY-SA) : le crédit de l'auteur est obligatoire, il est affiché en bas
      de page, et n'importe qui peut se servir des mêmes images. **Ce ne sont
      pas nos images.** Deux par lieu, l'arrivée large et le détail serré.

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

## 🔥 AU BRAISÉ D'OR — https://au-braise-dor.pages.dev

> ⚠️ **DEPUIS LE 2026-08-12 LE SITE N'EST PLUS `index.html`** : l'adresse sert
> le projet **Next.js de `clients/09-au-braise-dor/experience/`**. Publier =
> `npm run build` puis `cp -r ../assets/docs out/` puis
> `wrangler pages deploy out --project-name au-braise-dor --branch main`.
> Les sept pièges du projet sont documentés dans son `CONTEXT.md`.

- [ ] **La vraie photo de la salle.** Le fond de l'expérience est un mur
      neutre, pas leur restaurant. ⚠️ La vidéo `hero.mp4` montre **le gril**,
      pas la salle : elle a été essayée puis retirée à la demande de Mongazi.
- [ ] **Confirmer le numéro WhatsApp** : `01 56 05 71 57` est câblé dans le
      site, l'enseigne affiche `43 99 29 29`. Un numéro faux, c'est une
      commande qui n'arrive jamais.
- [ ] **Les vrais avis et le nom du chef.** Les champs `chef` et `avis`
      existent dans `experience/data/dishes.ts` et s'afficheront tout seuls.
      ⛔ Rien d'inventé en attendant : la vidéo de référence affichait
      « 4.9 ★ » et « 96 likes », ce restaurant existe.
- [ ] L'**adresse exacte** et la carte, le **vrai logo**, les **réseaux**.
- [ ] ⏳ **La version « braise »** (vidéo du gril en fond, scène sombre) dort en
      **32062e3**. La reprendre est un `git revert`, pas une reconstruction.

---

## 🧰 LE PARC

- [ ] **La marque de déploiement** sur les autres sites : la protection
      anti-cache-empoisonné de PISTE, demandée par Mongazi le 2026-08-04.
- [x] ~~Fusionner `worktree-angy-photos` dans `main`~~ ✅ **fait le
      2026-08-11**, et refait à chaque commit depuis. `main` porte ANGY ART,
      tout MON BÉNIN et toute la vague HILLARY.

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
