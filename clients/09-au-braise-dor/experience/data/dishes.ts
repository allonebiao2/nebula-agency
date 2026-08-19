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
  /* ⚠️ LES SAUCES OUVRENT LE HÉROS, ET C'EST VOULU (2026-08-19).
     Mongazi : « c'est un restaurant béninois, donc les plats de la catégorie
     sauce doivent être mis en avant plus que les autres ; les autres aussi
     bien sûr, mais ces plats-là en principal. »
     Les deux qui ouvrent sont les sauces LOCALES du menu (section « Monyo »).
     La Béchamel et la Sauce Crème restent à la carte mais pas ici : le menu
     papier les range sous « Sauces Européennes », elles ne servent pas
     l'argument. Le gombo, le krinkrin et la sauce feuille — les plus
     béninoises de toutes — n'ont pas encore de photo : le jour où leurs
     fichiers arrivent, elles prennent la tête. */
  {
    id: "moyo",
    line1: "MOYO",
    line2: "CHIGAN",
    kicker: "#1 La sauce du pays",
    cat: "Sauces",
    price: 3000,
    desc: "Sauce tomate, piment vert, oignon, moutarde, poisson ou aileron.",
    img: "/plats/sc-moyo.webp",
    /* teinte relevée sur la photo elle-même, comme chez Hillary : la couleur
       du héros suit la matière. 5,05:1 avec le blanc du prix. */
    tint: "#B25324",
    wash: "#F7EBE4",
  },
  {
    id: "poisson-frais",
    line1: "SAUCE",
    line2: "POISSON FRAIS",
    kicker: "#2 Au poisson frais",
    cat: "Sauces",
    price: 3000,
    desc: "Sauce tomate et crin-crin au choix.",
    img: "/plats/sc-poisson.webp",
    /* la même famille de tomate, en plus profond : les deux sauces partagent
       leur couleur dominante, il fallait les distinguer sans mentir. */
    tint: "#8A3520",
    wash: "#F6E8E2",
  },
  {
    id: "poulet",
    line1: "POULET",
    line2: "BICYCLETTE",
    kicker: "#3 Spécialité maison",
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
    kicker: "#4 Le goût fumé",
    cat: "Grillades",
    price: 3000,
    price2: 6000,
    desc: "Le tilapia entier, braisé minute, ce goût fumé signature.",
    img: "/plats/tilapia.webp",
    tint: "#C9A227",
    wash: "#F5F1E4",
  },
  {
    /* ⚠️ C'ÉTAIT LA PIZZA PÊCHEUR JUSQU'AU 2026-08-19, retirée de la carte par
       la propriétaire. Un héros ne met pas en avant un plat qu'on ne peut plus
       commander. La paysanne est la seule pizza restante à deux tailles. */
    id: "pizza",
    line1: "PIZZA",
    line2: "PAYSANNE",
    kicker: "#5 Au four",
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
    kicker: "#6 Notre signature",
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
