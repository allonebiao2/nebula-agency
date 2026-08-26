/**
 * LES DEUX SEULES FAÇONS D'ÉCRIRE UN PRIX SUR CE SITE.
 *
 * ⚠️ ELLES VIVENT ICI PARCE QU'ELLES SERVENT PARTOUT : la carte, la fiche de
 * commande, le panier, le héros. Recopiées dans chaque fichier, elles finissent
 * par diverger — et deux façons d'écrire un prix sur la même page, c'est un
 * client qui compare et qui doute.
 */

/** « 1 500 » avec une espace insécable : un prix ne se coupe jamais en deux. */
export const fmt = (n: number) => n.toLocaleString("fr-FR").replace(/ | /g, " ");

/** « 1 500 F » ou « 1 500 à 3 500 F » — jamais un chiffre qu'on ne tient pas. */
export const prix = (bas: number, haut?: number) =>
  haut && haut !== bas ? `${fmt(bas)} à ${fmt(haut)} F` : `${fmt(bas)} F`;
