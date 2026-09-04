# 2026-09-04 — Photographier et mesurer une modale, sans se mentir

> Née sur le tunnel de commande d'Hillary M. Styl, mais valable sur **toute
> modale, tout tiroir, tout panneau** de nos vitrines : le panier d'Hillary, la
> fiche du Braisé d'Or, le panneau d'Angy Art, la modale de devis de Djambar.

---

## 1. La capture : ni `full_page`, ni l'élément

Pour relire un tunnel de commande, deux façons évidentes donnent des images
**fausses sans le moindre signal**.

**`page.screenshot(full_page=True)`** photographie **tout le document**, or une
modale est un `position:fixed` posé au-dessus d'un catalogue qui fait
**28 000 px de haut**. La modale y est un timbre-poste dans une image géante.

**`page.locator(".sheet").screenshot()`** a l'air d'être la bonne réponse, et
c'est pire : la barre du haut et le pied de la modale sont `position:sticky`.
Dans une capture d'élément, ils **se repeignent au bord de la fenêtre** et
**recouvrent tout ce qui suit**. Sur mes deux premières planches, les blocs que
je venais précisément vérifier — les deux promesses et le récapitulatif —
**étaient absents de l'image**, et rien ne le disait.

### Ce qui marche

**Une fenêtre assez haute pour que toute la modale y tienne**, et une capture de
fenêtre ordinaire :

```python
LARGEURS = [("mobile", 390, 2600), ("bureau", 1440, 2000)]
...
await page.screenshot(path=chemin)      # surtout pas full_page
```

⚠️ La largeur reste **réelle** (390 / 1440) : c'est elle qui détermine la mise
en page. Seule la hauteur est forcée, et **le débordement horizontal continue
d'être mesuré par le QC aux vraies hauteurs** — ces planches ne servent pas à
ça, elles servent à **regarder**.

⚠️ Photographier **chaque état**, pas seulement l'état plein : le formulaire
vide, un champ rempli, le bouton grisé. C'est dans l'état intermédiaire que
s'est révélé le vrai défaut du jour (un bouton gris qui ne disait pas pourquoi).

---

## 2. Le contraste : mesurer les pixels rendus, pas la couleur déclarée

Les contrôles de contraste habituels lisent `background-color` **sur l'élément
qui porte le texte**. Dans une modale, cet élément est presque toujours
transparent : la couleur vient d'un ancêtre. Résultat, ils lisent
`rgba(0,0,0,0)` et ne mesurent rien.

**On remonte donc jusqu'au premier ancêtre dont le fond est vraiment opaque** :

```js
let n = el, fond = null;
while (n && n !== document.documentElement) {
  const c = rgb(getComputedStyle(n).backgroundColor);
  if (c.length >= 3 && (c[3] === undefined || c[3] > .95)) { fond = c.slice(0,3); break; }
  n = n.parentElement;
}
```

Puis le seuil se choisit sur la **taille réelle** : 3,0 pour du grand texte
(≥ 24 px, ou ≥ 18,66 px en gras), 4,5 sinon. Le lire dans `getComputedStyle`,
jamais le supposer.

⛔ **Ça ne vaut PAS pour un texte posé sur une photo.** Là il n'y a pas de fond
calculable : on masque le texte, on photographie, on prend le décile le plus
clair (technique Angy Art du 2026-08-08).

### Ce que ça a trouvé

La puce « J'habite à … » au **survol** : `--rose` `#E6007E` sur `--rose-p`
`#FFE9F5` = **3,91:1**. Sous le seuil.

⚠️ **C'était la quatrième fois** que le rose de la marque était posé sur du
texte sur ce même site (étiquette du carrousel, badge, bouton WhatsApp, puce).
**Le rose de marque sert au trait, jamais à la lettre** : le contour garde
`--rose`, le texte prend `--rose-f` `#c9006c` (4,93:1).

À reprendre : **aucune de nos vitrines n'a de contrôle de contraste sur sa
modale**. Hillary en a un depuis aujourd'hui.

---

## 3. Trois pièges de sonde, tous rencontrés le même jour

**`innerText` d'un élément en `display:none` renvoie quand même son contenu.**
Un contrôle qui lit le texte d'une ligne masquée croit la voir affichée. Le
remède n'est pas de ruser dans la sonde : c'est de rendre **texte et visibilité
solidaires** dans le produit — la ligne n'écrit que ce qu'elle montre.

**Une page qui se souvient fausse le parcours suivant.** Le moteur d'Hillary
reporte les coordonnées d'une commande sur la suivante (c'est voulu). Un
contrôle qui enchaîne deux commandes mesure donc des champs **déjà remplis par
la première** et conclut l'inverse de la vérité. Vider explicitement ce qu'on va
mesurer — et en profiter pour vérifier que le souvenir marche.

**Remplir tous les champs d'un coup ne prouve rien.** Pour vérifier que quatre
champs sont obligatoires, on les remplit **un par un** et on constate que le
bouton reste mort à chaque étape, en nommant à chaque fois ce qui manque encore.

---

## 4. Le raccord avec la chaîne de construction

Sur un site monté en deux temps (assembleur → build), **le script de
déploiement doit partir de la source la plus amont**. Celui d'Hillary ne
lançait que le build : éditer un morceau de `_v4/` puis déployer publiait un
livrable bâti sur une source **périmée** — QC vert, déploiement réussi, et le
changement absent du site.

⚠️ Bénéfice de bord : l'assembleur **refuse d'écrire** si l'un des 18
identifiants du moteur de commande manque. Le mettre dans le chemin de
déploiement y ajoute ce garde-fou.

Voir `_memoire/conversations/2026-09-04-hillary-informations-commande.md`.
