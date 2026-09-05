# 2026-09-05 — Angy Art : les prix s'en vont, une sélection arrive

> Client 11 · ANGY ART (Angélique Avocevou) · https://angy-art.pages.dev
> Deux demandes de Mongazi, transmises d'Angélique : **retirer les prix**, et
> **ajouter un panier**.

---

## 1. Les prix : quatre endroits, dont trois qu'on ne voit pas

« Enlever les prix » n'est pas enlever six lignes. Un prix vivait à **quatre**
endroits sur cette page :

| Où | Visible ? | Ce qui a été fait |
|---|---|---|
| la ligne `PRIX` du cartel de chaque œuvre | oui | les **6 lignes** retirées |
| le message WhatsApp pré-écrit du bouton « acquérir » | **non** — il part chez elle | **5 messages** débarrassés du montant |
| le balisage `Offer` du JSON-LD | **non** — il part chez Google, et **s'affiche dans les résultats de recherche** | **5 offres** retirées |
| deux phrases qui **annonçaient** que les prix sont donnés | oui | reformulées |

En oublier un, c'est afficher un prix qu'elle ne veut plus montrer — et le
plus dangereux est celui du balisage, qui continue à vivre dans Google
longtemps après qu'on a nettoyé la page.

### ⛔ Ce qui reste, et pourquoi

Le menu déroulant **« budget »** du formulaire de création sur mesure garde ses
cinq tranches en FCFA. **Ce n'est pas un prix d'Angélique** : c'est la question
qu'elle pose au client, et elle vient de son brief en quinze questions du
2026-08-21. Le retirer casserait son formulaire. **À elle de trancher.**

### ⚠️ Le contrôle n'a pas été supprimé, il a été RETOURNÉ

`_qc.py` exigeait « chaque œuvre annonce son prix, ou qu'il est sur demande ».
Il vérifie désormais **qu'aucune n'en affiche** — et un second contrôle a été
ajouté pour le message WhatsApp, parce que c'est l'endroit qu'on oublie.

---

## 2. Le « panier » d'une artiste qui n'affiche plus ses prix

⚠️ **Un panier sans prix ne peut pas additionner.** Les deux demandes arrivent
ensemble et se contredisent à moitié : il n'y a plus de total à afficher, donc
plus de panier au sens du commerce.

Ce que le mécanisme fait vraiment ici : **rassembler plusieurs œuvres et
n'écrire qu'un seul message**. Jusqu'ici, une visiteuse intéressée par trois
pièces devait envoyer trois messages. C'est le service rendu par le panier
d'Hillary, moins l'addition. Il s'appelle donc **« Ma sélection »**.
*(Si Mongazi préfère le mot « panier », c'est un libellé à changer, pas un
mécanisme à refaire.)*

### Où se pose le rappel, et pourquoi pas ailleurs

- ⛔ **pas dans la barre du haut** : mesuré le 2026-08-21, à 1024 px elle ne
  garde que **31 px de marge** de chaque côté. Un bouton de plus la fait déborder.
- ⛔ **pas en pastille flottante** : interdit sur ce site depuis Mon Bénin, et
  payé ici le 2026-08-27 (le bouton du son se posait sur « DÉCOUVRIR LES ŒUVRES »).
- ✅ **une bande de bord**, vraiment opaque, qui **n'apparaît que si la
  sélection n'est pas vide** — la seule chose qui ait le droit de passer devant
  une phrase sur ce site. `body` reçoit sa hauteur en marge basse, et **les deux
  instruments du couloir de droite montent d'autant** (la solution d'Hillary du
  2026-08-16).

⚠️ **La hauteur de la bande est MESURÉE**, pas écrite à la main : à 390 px elle
passe sur deux lignes, et une valeur en dur laisse toujours quelques pixels de
recouvrement. Le contrôle le vérifie (68 px réservés pour 68 px mesurés).

### Ce que la sélection ne fait pas

- elle **ne recopie aucune œuvre** : titre, dimensions et image sont **lus dans
  la fiche**. Le jour où Angélique change un texte, la sélection suit.
- elle **écarte ce qui n'existe plus** : une œuvre retirée de la page ne
  ressort pas d'une sélection oubliée dans le navigateur.
- **sans JavaScript**, la bande et les boutons n'existent pas, et chaque œuvre
  garde son lien WhatsApp direct — qui suffisait déjà.
- la modale est un `<dialog>` natif : `showModal()` donne le piège au clavier,
  Échap et l'inertie de la page derrière **sans une ligne de plus** (la leçon
  Hillary du 2026-08-25, où l'on ne pouvait pas commander au clavier).

---

## 3. Ce qu'une capture a montré et que le code ne disait pas

⛔ **La flèche du bouton « ÉCRIRE À ANGÉLIQUE » sortait en triangle plein
noir.** `.pill` n'avait jamais porté d'icône sur ce site : sans règle, un
`<path>` sans `fill="none"` se remplit. Vu sur la capture, invisible dans le
code. → `.pill svg{fill:none;stroke:currentColor}`.

---

## 4. Contrôles et mise en ligne

- **`_qc.py` : 209 → 220 contrôles, tous verts.** Onze nouveaux pour la
  sélection : la bande absente à vide, le compte, l'opacité réelle, la marge
  réservée **comparée à la hauteur mesurée**, la persistance, la survie au
  rechargement, l'ouverture de la modale, l'entrée du clavier, Échap, et le
  retour à zéro.
- ⚠️ **`?v=` bumpé en `20260905a`** : les assets de ce site portent
  `immutable` un an et **le cache de bordure d'un `*.pages.dev` ne se purge
  pas**. Sans le bump, personne n'aurait vu le changement.
- ✅ **Déployé et vérifié en ligne** : 6 boutons d'ajout, aucun prix dans le
  texte de la page, la bande paraît à l'ajout, la modale liste.

---

## 5. Ce qui reste

- ⏳ **Le mot « panier »** : dire à Mongazi que le bouton s'appelle
  « Ma sélection », et lui laisser le choix.
- ⏳ **Les tranches de budget** du formulaire sur mesure : à confirmer avec
  Angélique.
- ⏳ Sans prix affichés, **le balisage n'annonce plus rien de commercial** : si
  elle veut apparaître dans les recherches d'achat d'art, il faudra une autre
  voie (un `Offer` sans prix n'existe pas utilement).
