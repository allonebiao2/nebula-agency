# 2026-07-31 — HILLARY M. STYL (client 10)

## Demande

Mongazi transmet le **logo** de la marque et un cahier des charges : maison de couture avec
**deux catalogues** (prêt-à-porter par tailles / sur-mesure), **formulaire de prise de
mesures**, **frais d'expédition calculés par pays**, **délais normal vs express**, retrait
en atelier et notification du client quand la tenue est prête.

## Le logo

Buste de mannequin ceint d'un ruban magenta, monogramme **H.M.S** en noir, signature
**HILLARY M. STYL** en magenta, sur fond gris uniforme `#CCCCCC`.

**Traitement :** fond rendu transparent par tolérance de 26 sur les 4 coins (76 % des
pixels), recadrage sur la boîte englobante (1007×557), redimensionnement à 620 px, puis
**conversion WebP** (55 Ko contre 158 Ko en PNG).

## Décisions de conception

1. **Palette tirée du logo** : magenta `#E6007E`, noir `#0A0A0A`, crème. Typo **Archivo**
   pour les titres (géométrique large, comme les lettres du logo) + **Manrope** pour le texte.
2. **Le logo n'est déclaré qu'une seule fois**, en variable CSS `--logo`, utilisé par trois
   éléments en `background`. Première version : 681 Ko parce que le data-URI était inliné
   trois fois. **Après correction : 120 Ko.** Sur la 3G béninoise, ce n'est pas un détail.
3. **Catalogue en 2 colonnes sur mobile.** Première version en 1 colonne : une pièce
   remplissait tout l'écran, parcourir 6 modèles devenait pénible. Deux colonnes, comme
   toutes les boutiques de mode.
4. **Une mesure vide ne bloque pas la commande.** Elle part en « à prendre ensemble » et le
   message indique combien il en manque. Un client qui ne sait pas mesurer son entrejambe
   ne doit pas abandonner son panier.
5. **Accueil personnalisé** : moment de la journée + prénom mémorisé en localStorage à la
   première commande.

## Piège de méthode rencontré

Une capture d'écran en **headless simple** (`--window-size=430`) montrait la page débordant
et les boutons coupés. **C'était un artefact** : headless sans émulation ignore le
`meta viewport` et rend la page à 800 px avant de recadrer à 430. La mesure Playwright avec
vraie émulation mobile a montré `scrollWidth === clientWidth` sur les trois formats.

**Leçon : ne jamais conclure à un bug de mise en page depuis une capture headless non
émulée.** Mesurer `scrollWidth` vs `clientWidth` avec Playwright.

## QC passé

- 0 débordement horizontal sur 390 / 768 / 1440, page et modale ouverte
- 0 erreur JS, 0 requête en échec, 0 image externe
- Toutes les cibles tactiles ≥ 44 px
- Tunnel vérifié : 35 000 + 12 000 + 10 000 = **57 000 F** · retrait atelier gratuit ·
  bascule femme/homme des mesures · bascule automatique en « sur devis »

## ⚠️ Bloquant avant mise en ligne

Sept informations manquent, toutes regroupées dans un bloc **« ZONE À COMPLÉTER »** en tête
du script, et détaillées au §3 du `CONTEXT.md` du client. Les deux plus graves :

1. **Le numéro WhatsApp est un fixe de test.** En l'état, aucune commande n'arrive.
2. **Les frais d'expédition sont des exemples.** Un tarif faux coûte de l'argent à la
   cliente à chaque commande.

Rien n'a été inventé en silence : tout ce qui est provisoire est marqué comme tel dans le
code et dans le CONTEXT.

## Positionnement commercial

Ce projet dépasse le Catalogue Digital à 50 000 F : il embarque un moteur de commande avec
prise de mesures et calcul de frais par pays. À chiffrer avec le **configurateur** du site,
pas au forfait catalogue.
