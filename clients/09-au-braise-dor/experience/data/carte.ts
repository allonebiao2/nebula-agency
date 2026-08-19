/**
 * LA CARTE COMPLÈTE — 52 plats, 9 catégories.
 *
 * ⚠️ FICHIER GÉNÉRÉ, NE PAS ÉDITER À LA MAIN.
 * Source : le tableau `CATS` de `../../index.html`, qui reste la vérité.
 * Régénérer :  node _outils/_extraire_carte.js
 */

export type Plat = {
  n: string;
  d?: string;
  /** Prix, ou borne BASSE quand pMax est là. */
  p: number;
  /** Deuxième taille, à son propre prix. Voir aussi tailles. */
  p2?: number;
  /** ⚠️ FOURCHETTE, PAS DEUX TAILLES. Le prix des sauces dépend de ce que le
   *  client met dedans (voir garn) : la maison le confirme à la commande. */
  pMax?: number;
  /** Ce qu'on peut mettre dedans, et qui fait monter le prix. */
  garn?: string[];
  /** Libellés des deux tailles quand ce n'est pas « Normal / Grand ». */
  tailles?: [string, string];
  joq?: boolean;
  /** Absent tant que la maison n'a pas donné sa photo. La carte affiche
   *  alors une tuile au nom du plat, jamais une image d'emprunt. */
  img?: string;
};

export type Cat = {
  id: string;
  label: string;
  tag: string;
  note?: string;
  acc?: "grillades" | "sauces";
  items: Plat[];
};

/** Les accompagnements au choix, repris tels quels du site. */
export const ACC: Record<string, string[]> = {
  grillades: ["Riz", "Attiéké", "Aloco", "Frites", "Pommes sautées", "Pomme vapeur", "Pâte rouge", "Bomiwo", "Akassa", "Igname frit"],
  /* ⚠️ Repris MOT POUR MOT de la feuille de menu de la maison (2026-08-19),
     qui remplace l'ancienne liste. « Tègbô » y est barré et corrigé en
     « telibo » de sa main : c'est telibo. */
  sauces: ["Telibo", "Agbéli", "Couscous", "Atchiéké", "Igname pilée", "Riz au gras", "Frites", "Pâte de maïs", "Akassa", "Riz blanc", "Wassa Wassa", "Foutou banane", "Foutou de manioc", "Aloko", "Toubani"],
};

export const CARTE: Cat[] = [
  {
    id: "grillades",
    label: "Grillades",
    tag: "La braise",
    note: "Accompagnements au choix : riz, attiéké, aloco, frites, pommes sautées ou vapeur, pâte rouge, Bomiwo, Akassa, igname frit.",
    acc: "grillades",
    items: [
      { n: "Poulet bicyclette", d: "Poulet fermier saisi au feu de bois, croustillant et fondant.", p: 3000, p2: 6000, img: "/carte/poulet.webp" },
      { n: "Tilapia braisé", d: "Le tilapia entier, braisé minute, ce goût fumé signature.", p: 3000, p2: 6000, img: "/carte/tilapia.webp" },
      { n: "Poulet chair", d: "Poulet chair grillé sur la braise.", p: 2500, p2: 5000, img: "/carte/g-poulet-chair.webp" },
      { n: "Aileron", d: "Aileron mariné et grillé.", p: 3000, img: "/carte/g-aileron.webp" },
      { n: "Mouton frit", d: "Viande frite dorée, tendre à cœur.", p: 3000, img: "/carte/g-lapin-mouton.webp" },
    ],
  },
  {
    id: "pizza",
    label: "Pizza",
    tag: "Au four",
    note: "Base sauce tomate maison. Deux tailles pour certaines pizzas.",
    items: [
      { n: "Paysanne", d: "Poulet, champignons, tomate, poivron, oignon, fromage, olive.", p: 4000, p2: 6000, img: "/carte/p-paysanne.webp" },
      { n: "Quatre saisons", d: "Jambon, crevette, viande, oignon, tomate, poivrons, olives, maïs.", p: 3500, img: "/carte/p-quatre-saisons.webp" },
      { n: "Fruit de mer", d: "Poisson, crevettes, oignon, tomate, fromage.", p: 3500, img: "/carte/p-fruit-mer.webp" },
      { n: "Aux épinards", d: "Thon, oignon, épinards, fromage.", p: 3000, img: "/carte/p-epinards.webp" },
    ],
  },
  {
    id: "chawarma",
    label: "Chawarma",
    tag: "À la broche",
    items: [
      { n: "Chawarma JOQ", d: "Poulet et viande réunis. Notre signature.", p: 3000, joq: true, img: "/carte/chawarma.webp" },
      { n: "Chawarma au poulet", d: "Poulet mariné, sauce maison.", p: 2500, img: "/carte/c-poulet.webp" },
      { n: "Chawarma à la viande", d: "Boulettes de viande, généreux.", p: 1500, img: "/carte/c-viande.webp" },
    ],
  },
  {
    id: "burger",
    label: "Hamburger",
    tag: "Fait maison",
    note: "Servis avec Coca-Cola, sauf le végétarien.",
    items: [
      { n: "Chicken burger", d: "Burger poulet, frites, Coca-Cola.", p: 4000, img: "/carte/b-chicken.webp" },
      { n: "Double burger", d: "Double steak, frites, Coca-Cola.", p: 3500, img: "/carte/b-double.webp" },
      { n: "Burger végétarien", d: "Pain burger, nuggets de pomme de terre, fromage.", p: 3500, img: "/carte/b-vegetarien.webp" },
      { n: "Cheese burger", d: "Cheese, viande, frites, Coca-Cola.", p: 3000, img: "/carte/b-cheese.webp" },
      { n: "Royal burger", d: "Burger, frites, Coca-Cola.", p: 3000, img: "/carte/b-royal.webp" },
      { n: "King burger", d: "Burger, œuf, Coca-Cola.", p: 2500, img: "/carte/b-king.webp" },
      { n: "Hamburger simple", d: "Le simple, Coca-Cola inclus.", p: 2500, img: "/carte/b-simple.webp" },
    ],
  },
  {
    id: "salades",
    label: "Salades",
    tag: "Fraîcheur",
    items: [
      { n: "Salade JOQ", d: "Laitue, pomme de terre, œuf, carotte, jambon, viande, crevette, maïs, avocat. Notre signature.", p: 4000, joq: true, img: "/carte/salade.webp" },
      { n: "Salade composée", d: "Laitue, concombre, carotte, oignon, pomme de terre, betterave, maïs, viande, œuf.", p: 3000, img: "/carte/s-composee.webp" },
      { n: "Salade d'avocats aux crevettes", d: "Laitue, avocat, oignon, tomate, crevettes, sauce Marie-rose.", p: 3000, img: "/carte/s-avocat-crevettes.webp" },
      { n: "Salade verte", d: "Laitue, tomate, oignon, olive noire.", p: 1000, img: "/carte/s-verte.webp" },
    ],
  },
  {
    id: "sauces",
    label: "Sauces",
    tag: "Local",
    note: "Toutes les sauces sont servies avec l'accompagnement de votre choix. Le prix dépend de ce que vous mettez dedans.",
    acc: "sauces",
    items: [
      { n: "Sauce gombo", d: "Le gombo de la maison. Vous choisissez ce qu'il y a dedans.", p: 1500, pMax: 3500, garn: ["Crabe", "Kpanmom", "Poisson"], img: "/carte/sc-gombo.webp" },
      { n: "Sauce krinkrin", d: "Adèmè pilé, servi bien vert.", p: 1500, pMax: 3000, garn: ["Crevette", "Kpanmom"], img: "/carte/sc-krinkrin.webp" },
      { n: "Sauce feuille", d: "Gbêkê mijoté.", p: 1500, pMax: 3000, garn: ["Poisson", "Crevette"], img: "/carte/sc-feuille.webp" },
      { n: "Sauce arachide", d: "La pâte d'arachide, longuement mijotée.", p: 1500, pMax: 3000, garn: ["Viande de mouton", "Poisson"] },
      { n: "Sauce graine", d: "La graine de palme, pressée à la maison.", p: 1500, pMax: 3000 },
      { n: "Sauce tomate", d: "Tomate fraîche, mijotée.", p: 1500, pMax: 3000 },
      { n: "Sauce tête de mouton", d: "Le gbata, pour ceux qui savent.", p: 1500, pMax: 3000 },
      { n: "Sauce pieds de bœuf", d: "Le blokoto, fondant.", p: 1500, pMax: 3000 },
      { n: "Sauce Yassa", d: "À l'oignon et au citron.", p: 1500, pMax: 3000, garn: ["Poisson", "Viande"] },
      { n: "Sauce Yassa au poulet", d: "Le yassa, avec du poulet.", p: 2500, p2: 3500, tailles: ["Quart de poulet", "Demi-poulet"] },
      { n: "Sauce Béchamel", d: "Champignon, haricot vert, oignon vert, au choix steak, poisson ou poulet à l'ail.", p: 5000, img: "/carte/sc-bechamel.webp" },
      { n: "Sauce Crème", d: "Filet de poisson à la crème aux champignons.", p: 5000, img: "/carte/sc-creme.webp" },
      { n: "Moyo Chigan", d: "Sauce tomate, piment vert, oignon, moutarde, poisson ou aileron.", p: 3000, img: "/carte/sc-moyo.webp" },
      { n: "Sauce poisson frais", d: "Sauce tomate et crin-crin au choix.", p: 3000, img: "/carte/sc-poisson.webp" },
    ],
  },
  {
    id: "petitdej",
    label: "Petit-déj",
    tag: "Le matin",
    items: [
      { n: "Plateau Mignon JOQ", d: "Chocolat chaud, beurre, croissant, œuf à la coque, jus de fruit, yaourt.", p: 4000, joq: true, img: "/carte/pd-mignon.webp" },
      { n: "Plateau complet", d: "Café ou thé, lait, beurre ou confiture, pain ou croissant, omelette, jus.", p: 3500, img: "/carte/pd-complet.webp" },
      { n: "Cappuccino", d: "Café crémeux.", p: 1500, img: "/carte/pd-cappuccino.webp" },
      { n: "Omelette aux légumes", d: "Œufs et légumes frais.", p: 1000, img: "/carte/pd-omelette-legumes.webp" },
      { n: "Omelette nature", d: "La simple et bonne.", p: 1000, img: "/carte/pd-omelette-nature.webp" },
      { n: "Œuf sur plat", d: "Œufs au plat.", p: 1000 },
      { n: "Café au lait", d: "Peak, chaud ou froid.", p: 1000, img: "/carte/pd-cafe-lait.webp" },
      { n: "Café au lait écrémé", d: "Chaud ou froid, au lait écrémé.", p: 1000 },
      { n: "Café chaud serré", d: "Le serré, bien chaud.", p: 500 },
      { n: "Lipton citron", d: "Thé Lipton au citron.", p: 500 },
    ],
  },
  {
    id: "cocktails",
    label: "Cocktails",
    tag: "Spécial maison",
    note: "Préparés minute, aux fruits frais. Sans alcool.",
    items: [
      { n: "Babariba", d: "Papaye, banane, pomme, lait, sirop de fraise.", p: 2500, img: "/carte/k-babariba.webp" },
      { n: "Paparazi", d: "Jus de citron, banane, orange, sirop de framboise.", p: 2500, img: "/carte/k-paparazi.webp" },
      { n: "Cocktail de fruit naturel", d: "Papaye, mangue, banane, lait, miel.", p: 2500, img: "/carte/k-fruit-naturel.webp" },
    ],
  },
  {
    id: "dessert",
    label: "Desserts",
    tag: "Pour finir",
    items: [
      { n: "Yaourt", p: 0 },
      { n: "Glace", p: 0 },
    ],
  },
];

export const NB_PLATS = CARTE.reduce((n, c) => n + c.items.length, 0);
