/**
 * LES SAUCES DU HÉROS — Au Braisé d'Or, Cotonou.
 *
 * ⚠️ ELLES NE SONT PLUS ÉCRITES ICI, ELLES SONT LUES DANS LA CARTE.
 * Avant le 2026-08-26, quatre sauces étaient recopiées à la main dans ce
 * fichier, avec leur prix. Deux vérités pour le même plat, c'est une faute de
 * prix qui attend son tour : le jour où la maison change le prix du gombo, la
 * carte suit et le héros ment. Désormais, `DISHES` est la catégorie « Sauces »
 * de `carte.ts`, dans son ordre, avec ses prix, ses fourchettes et ses textes.
 * Ajouter une sauce à la carte la fait entrer au héros toute seule.
 *
 * ⚠️ TOUTES LES SAUCES, ET C'EST UN ORDRE (2026-08-26). Mongazi : « je veux
 * que toutes les sauces soient dans le carrousel dans la hero ». Le héros
 * n'en montrait que quatre : les seules dont la maison avait envoyé la photo.
 * Les autres passent donc en ARDOISE — le disque de pierre au nom du plat,
 * le même objet que dans la carte — au lieu de rester invisibles. Une sauce
 * qu'on ne montre pas est une sauce qu'on ne vend pas ; une ardoise, elle,
 * se commande.
 *
 * ⛔ ET C'EST POUR ÇA QU'IL N'Y A NI NOTE, NI CHEF, NI « LIKES ». La vidéo de
 * référence affiche « 4.9 ★ », « Chef Feny » et « 96 likes ». Sur le site d'un
 * restaurant qui existe, ce serait un faux avis, un faux employé et un faux
 * compteur. Le carré coloré porte donc **le prix**, qui est vrai, et qui est de
 * toute façon la première chose qu'un client cherche.
 */

import { CARTE } from "./carte";

export type Dish = {
  id: string;
  /** Le nom EXACT du plat dans `carte.ts` : c'est la clé qui ouvre sa fiche. */
  nom: string;
  /** Ligne 1 du titre : fine, espacée */
  line1: string;
  /** Ligne 2 du titre : très grasse */
  line2: string;
  /** « #1 La sauce du pays » */
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
  /** Le fichier détouré, dans /public/plats. ABSENT tant que la maison n'a pas
   *  donné sa photo : le héros pose alors une ardoise, jamais un cadre vide. */
  img?: string;
  /** La couleur du carré de prix, une par sauce. ⚠️ Le prix est écrit en BLANC
   *  dessus : chaque teinte est vérifiée à 4,5:1 minimum par `_outils/_qc.py`. */
  tint: string;
  /** La teinte de fond, très légère, propre au plat */
  wash: string;
  /** ⏳ à remplir quand le restaurant les donnera. Vides, ils ne s'affichent pas. */
  chef?: string;
  chefRole?: string;
  avis?: { note: number; nombre: number };
};

/**
 * LA DÉCORATION, et rien d'autre : identifiant, accroche, couleurs, photo.
 *
 * ⚠️ AUCUN PRIX ICI, AUCUNE DESCRIPTION. Tout ce qui engage la maison est lu
 * dans `carte.ts`. Ce qui reste est du dessin, et le dessin ne se contredit
 * pas avec la cuisine.
 *
 * ⚠️ LES ACCROCHES SORTENT DES DESCRIPTIONS DE LA MAISON. « Le gbata », « le
 * blokoto », « l'adèmè pilé » sont ses mots, repris de sa carte, pas des
 * formules inventées pour faire joli.
 */
const DECO: Record<
  string,
  { id: string; kicker: string; tint: string; wash: string; img?: string }
> = {
  "Sauce gombo":         { id: "gombo",    kicker: "La sauce du pays",   tint: "#8C6A1F", wash: "#F5EFDF", img: "/plats/sc-gombo.webp" },
  "Sauce krinkrin":      { id: "krinkrin", kicker: "L'adèmè pilé",       tint: "#4F5B32", wash: "#EEF0E5", img: "/plats/sc-krinkrin.webp" },
  "Sauce feuille":       { id: "feuille",  kicker: "Le gbêkê",           tint: "#3E5136", wash: "#EAEFE7", img: "/plats/sc-feuille.webp" },
  "Sauce arachide":      { id: "arachide", kicker: "La pâte d'arachide", tint: "#7A4A22", wash: "#F3EAE0", img: "/plats/sc-arachide.webp" },
  "Sauce graine":        { id: "graine",   kicker: "La graine de palme", tint: "#9E5F20", wash: "#F5E9DC", img: "/plats/sc-graine.webp" },
  "Sauce tomate":        { id: "tomate",   kicker: "Tomate fraîche",     tint: "#A3301F", wash: "#F7E7E2", img: "/plats/sc-tomate.webp" },
  "Sauce tête de mouton":{ id: "gbata",    kicker: "Le gbata",           tint: "#6B4230", wash: "#F1E8E1", img: "/plats/sc-tete-mouton.webp" },
  "Sauce pieds de bœuf": { id: "blokoto",  kicker: "Le blokoto",         tint: "#5C4433", wash: "#F0EAE3", img: "/plats/sc-pieds-boeuf.webp" },
  "Sauce Yassa":         { id: "yassa",    kicker: "Oignon et citron",   tint: "#8A6A12", wash: "#F6F0DC", img: "/plats/sc-yassa.webp" },
  "Sauce Yassa au poulet":{ id: "yassapoulet", kicker: "Le yassa au poulet", tint: "#8F5A16", wash: "#F6ECDC", img: "/plats/sc-yassa-poulet.webp" },
  "Sauce Béchamel":      { id: "bechamel", kicker: "Champignon, ail",    tint: "#6E6353", wash: "#F2EFE8" },
  "Sauce Crème":         { id: "creme",    kicker: "Filet à la crème",   tint: "#4F6266", wash: "#E9EFF0" },
  "Moyo Chigan":         { id: "moyo",     kicker: "Piment vert, moutarde", tint: "#A8452A", wash: "#F7E9E3", img: "/plats/sc-moyo.webp" },
  "Sauce poisson frais": { id: "poisson",  kicker: "Tomate et crin-crin", tint: "#2F5A63", wash: "#E6EFF1", img: "/plats/sc-poisson.webp" },
};

/**
 * LE TITRE EN DEUX LIGNES, découpé sans y penser.
 *
 * ⚠️ ON NE COUPE PAS AU MILIEU D'UN MOT, ET ON NE LAISSE PAS UNE LIGNE 2 À
 * QUATRE MOTS. « SAUCE TÊTE DE MOUTON » en une seule ligne très grasse déborde
 * de la colonne du titre, qui ne fait que 366 px sur un écran de 1440.
 * Règle : ce qui suit « Sauce » tient sur la deuxième ligne s'il fait deux mots
 * au plus ; au-delà, le premier mot remonte sur la ligne fine.
 */
function couper(nom: string): [string, string] {
  const mots = nom.split(" ");
  if (mots.length === 1) return ["LA", mots[0].toUpperCase()];
  const tete = mots[0].toUpperCase();
  const reste = mots.slice(1);
  if (reste.length <= 2) return [tete, reste.join(" ").toUpperCase()];
  return [
    (tete + " " + reste[0]).toUpperCase(),
    reste.slice(1).join(" ").toUpperCase(),
  ];
}

/** La palette de secours, si la maison ajoute une sauce sans lui donner sa
 *  teinte. ⚠️ Toutes sont vérifiées à 4,5:1 avec du blanc, comme les autres. */
const SECOURS = ["#8C6A1F", "#4F5B32", "#9E5F20", "#3E5136", "#A8452A"];

const SAUCES = CARTE.find((c) => c.id === "sauces");

export const DISHES: Dish[] = (SAUCES?.items ?? []).map((p, k) => {
  const d = DECO[p.n];
  const [line1, line2] = couper(p.n);
  return {
    id: d?.id ?? `sauce-${k}`,
    nom: p.n,
    line1,
    line2,
    /* ⚠️ Le numéro se calcule, il ne se recopie pas : à quatorze sauces, un
       « #4 » écrit à la main sur la cinquième ne se remarque jamais. */
    kicker: `#${k + 1} ${d?.kicker ?? SAUCES?.label ?? "Nos sauces"}`,
    cat: SAUCES?.label ?? "Sauces",
    price: p.p,
    price2: p.p2,
    priceMax: p.pMax,
    desc: p.d ?? "",
    img: d?.img,
    tint: d?.tint ?? SECOURS[k % SECOURS.length],
    wash: d?.wash ?? "#F3EFE6",
  };
});

/** Le numéro qui reçoit les commandes. ⚠️ À CONFIRMER : l'enseigne affiche
 *  43 99 29 29, le site a toujours utilisé celui-ci. */
export const WHATSAPP = "22956057157";

export function lienCommande(d: Dish) {
  const t =
    `Bonjour Au Braisé d'Or, je voudrais commander : ${d.line1} ${d.line2}` +
    ` (${d.price.toLocaleString("fr-FR")} F).`;
  return `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(t)}`;
}
