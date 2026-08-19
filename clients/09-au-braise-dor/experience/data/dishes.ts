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
  /** Borne haute, quand le prix dépend de ce qu'on met dedans (les sauces). */
  priceMax?: number;
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
  /* ⚠️ QUE DES SAUCES, ET C'EST UN ORDRE (2026-08-19, nuit).
     Mongazi d'abord : « les plats de la catégorie sauce doivent être mis en
     avant plus que les autres ; les autres aussi bien sûr, mais ces plats-là
     en principal. » Puis, en regardant le héros : « je veux qu'ici ce soient
     les sauces qui soient mises en avant, QUE les sauces. »
     Le poulet bicyclette, le tilapia et le chawarma JOQ sortent donc du héros.
     Ils restent à la carte, où ils se commandent comme avant : ce n'est pas
     un retrait de plat, c'est un choix de vitrine — un restaurant béninois
     montre ses sauces.

     ⚠️ CES TROIS-LÀ ET PAS D'AUTRES : ce sont les seules sauces dont la maison
     a envoyé la photo. Les onze autres n'en ont pas, et le héros vit de
     l'image — une ardoise en plein écran ne vend rien. Moyo Chigan et Sauce
     poisson frais ont bien un détourage, mais fait à partir d'une image
     GÉNÉRÉE de juillet : les mettre ici, c'est ouvrir le site sur de l'IA. */
  {
    id: "gombo",
    line1: "SAUCE",
    line2: "GOMBO",
    kicker: "#1 La sauce du pays",
    cat: "Sauces",
    price: 1500,
    priceMax: 3500,
    desc: "Le gombo de la maison, avec crabe, kpanmom et poisson au choix.",
    img: "/plats/sc-gombo.webp",
    tint: "#8C6A1F",
    wash: "#F5EFDF",
  },
  {
    id: "krinkrin",
    line1: "SAUCE",
    line2: "KRINKRIN",
    kicker: "#2 L'adèmè pilé",
    cat: "Sauces",
    price: 1500,
    priceMax: 3000,
    desc: "Adèmè pilé, crevette et kpanmom au choix.",
    img: "/plats/sc-krinkrin.webp",
    tint: "#4F5B32",
    wash: "#EEF0E5",
  },
  {
    id: "feuille",
    line1: "SAUCE",
    line2: "FEUILLE",
    kicker: "#3 Le gbêkê",
    cat: "Sauces",
    price: 1500,
    priceMax: 3000,
    desc: "Gbêkê mijoté, poisson et crevette au choix.",
    img: "/plats/sc-feuille.webp",
    tint: "#3E5136",
    wash: "#EAEFE7",
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
