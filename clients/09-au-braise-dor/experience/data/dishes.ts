/**
 * LES QUATRE PLATS SIGNATURE — Au Braisé d'Or, Cotonou.
 *
 * ⚠️ CE SONT DE VRAIS PLATS, AUX VRAIS PRIX. Les noms, les descriptions et les
 * prix sont repris mot pour mot de la carte du restaurant (`../index.html`,
 * tableau `CATS`). Rien n'est inventé ici.
 *
 * ⛔ ET C'EST POUR ÇA QU'IL N'Y A NI NOTE, NI CHEF, NI « LIKES ». La vidéo de
 * référence affiche « 4.9 ★ », « Chef Feny » et « 96 likes ». Sur le site d'un
 * restaurant qui existe, ce serait un faux avis, un faux employé et un faux
 * compteur. Le carré coloré porte donc **le prix**, qui est vrai, et qui est de
 * toute façon la première chose qu'un client cherche.
 * Le jour où le restaurant donne ses vrais avis et le nom de son chef, les
 * champs `chef` et `avis` ci-dessous se remplissent et la carte les affiche.
 */

export type Dish = {
  id: string;
  /** Ligne 1 du titre : fine, espacée */
  line1: string;
  /** Ligne 2 du titre : très grasse */
  line2: string;
  /** « #1 Spécialité maison » */
  kicker: string;
  /** La catégorie de la carte, pour renvoyer au menu complet */
  cat: string;
  /** Prix en francs CFA */
  price: number;
  /** Deuxième taille, quand elle existe */
  price2?: number;
  desc: string;
  /** Le fichier détouré, dans /public/plats */
  img: string;
  /** La couleur du carré de prix, une par plat, comme la référence */
  tint: string;
  /** La teinte de fond, très légère, propre au plat */
  wash: string;
  /** ⏳ à remplir quand le restaurant les donnera. Vides, ils ne s'affichent pas. */
  chef?: string;
  chefRole?: string;
  avis?: { note: number; nombre: number };
};

export const DISHES: Dish[] = [
  {
    id: "poulet",
    line1: "POULET",
    line2: "BICYCLETTE",
    kicker: "#1 Spécialité maison",
    cat: "Grillades",
    price: 3000,
    price2: 6000,
    desc: "Poulet fermier saisi au feu de bois, croustillant et fondant.",
    img: "/plats/poulet.webp",
    tint: "#E8763A",
    wash: "#F6EDE6",
  },
  {
    id: "tilapia",
    line1: "TILAPIA",
    line2: "BRAISÉ",
    kicker: "#2 Le goût fumé",
    cat: "Grillades",
    price: 3000,
    price2: 6000,
    desc: "Le tilapia entier, braisé minute, ce goût fumé signature.",
    img: "/plats/tilapia.webp",
    tint: "#C9A227",
    wash: "#F5F1E4",
  },
  {
    /* ⚠️ C'ÉTAIT LA PIZZA PÊCHEUR JUSQU'AU 2026-08-19. La propriétaire l'a
       retirée de la carte ce jour-là, avec cinq autres pizzas. Un héros ne
       peut pas mettre en avant un plat qu'on ne peut plus commander : le
       visiteur arrive, s'enthousiasme, et ne le trouve nulle part.
       La paysanne prend sa place : c'est la seule pizza restante à deux
       tailles, donc la seule au même rôle sur la carte. */
    id: "pizza",
    line1: "PIZZA",
    line2: "PAYSANNE",
    kicker: "#3 Au four",
    cat: "Pizza",
    price: 4000,
    price2: 6000,
    desc: "Poulet, champignons, tomate, poivron, oignon, fromage, olive.",
    img: "/plats/pizza.webp",
    tint: "#B8574B",
    wash: "#F6E9E6",
  },
  {
    id: "chawarma",
    line1: "CHAWARMA",
    line2: "JOQ",
    kicker: "#4 Notre signature",
    cat: "Chawarma",
    price: 3000,
    desc: "Poulet et viande réunis. Notre signature.",
    img: "/plats/chawarma.webp",
    tint: "#7E8B5A",
    wash: "#EFF1E8",
  },
];

/** Le numéro qui reçoit les commandes. ⚠️ À CONFIRMER : l'enseigne affiche
 *  43 99 29 29, le site a toujours utilisé celui-ci. */
export const WHATSAPP = "22956057157";

export function lienCommande(d: Dish) {
  const t =
    `Bonjour Au Braisé d'Or, je voudrais commander : ${d.line1} ${d.line2}` +
    ` (${d.price.toLocaleString("fr-FR")} F).`;
  return `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(t)}`;
}
