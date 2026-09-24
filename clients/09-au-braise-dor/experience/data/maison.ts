/**
 * LES FAITS DE LA MAISON, À UN SEUL ENDROIT.
 *
 * Le bandeau de présentation, la FAQ, les pages de la carte, le balisage
 * JSON-LD, `llms.txt`, `carte.md` et le sitemap lisent TOUS ce fichier (et
 * `carte.ts` pour les plats et les prix). Un fait recopié à la main dans une
 * page finit toujours par contredire un autre : c'est le piège du « prix qui
 * vit à quatre endroits », déjà payé chez Angy Art.
 *
 * ⛔ N'ÉCRIRE ICI QUE CE QUI EST VRAI ET DÉJÀ DIT PAR LA MAISON :
 *   - pas d'adresse de rue (la fiche Google porte « …221, Cotonou », illisible
 *     en entier ; la maison ne l'a jamais confirmée) ;
 *   - pas d'horaires précis (« ouvert tous les jours » n'est pas un horaire) ;
 *   - aucune note, aucun avis, aucun chiffre de clientèle.
 * Le jour où l'adresse, les horaires ou les réseaux arrivent, on les ajoute
 * ICI et tout le site suit.
 */
import { CARTE, NB_PLATS, type Cat, type Plat } from "./carte";

export const SITE = "https://aubraisedor.com";

export const MAISON = {
  nom: "Au Braisé d'Or",
  devise: "De Paris à Cotonou",
  ville: "Cotonou",
  pays: "Bénin",
  whatsapp: "01 56 05 71 57",
  telephone2: "01 94 21 30 02",
  telephoneInternational: "+2290156057157",
  email: "aubraisedor@gmail.com",
  ouverture: "Ouvert tous les jours",
  wifi: "WiFi 24h/24",
  cuisines: "cuisine africaine, européenne et américaine",
  rc: "RB/COT/24 A 102350",
  ifu: "0202501441177",
} as const;

/** Les rubriques de la carte : l'adresse de leur page et ce qu'elles ciblent. */
export const RUBRIQUES: Record<string, { slug: string; titre: string; accroche: string }> = {
  grillades: {
    slug: "grillades",
    titre: "Grillades au feu de bois à Cotonou",
    accroche: "La braise est la spécialité de la maison : poulet, tilapia et aileron grillés au feu de bois.",
  },
  sauces: {
    slug: "sauces",
    titre: "Sauces du pays à Cotonou : gombo, krinkrin, graine",
    accroche: "Les sauces béninoises et d'Afrique de l'Ouest, servies avec l'accompagnement de votre choix.",
  },
  pizza: {
    slug: "pizzas",
    titre: "Pizzas à Cotonou",
    accroche: "Des pizzas au four, sur une base de sauce tomate maison.",
  },
  chawarma: {
    slug: "chawarma",
    titre: "Chawarma à Cotonou",
    accroche: "Le chawarma à la broche, au poulet, à la viande ou en version maison.",
  },
  burger: {
    slug: "burgers",
    titre: "Burgers à Cotonou",
    accroche: "Des hamburgers faits maison, du simple au double, et une version végétarienne.",
  },
  salades: {
    slug: "salades",
    titre: "Salades à Cotonou",
    accroche: "Des salades fraîches, de la salade verte à l'avocat aux crevettes.",
  },
  petitdej: {
    slug: "petit-dejeuner",
    titre: "Petit-déjeuner à Cotonou",
    accroche: "Plateaux, omelettes, cafés et cappuccino pour commencer la journée.",
  },
  cocktails: {
    slug: "cocktails",
    titre: "Cocktails de fruits frais à Cotonou",
    accroche: "Des cocktails maison préparés minute, aux fruits frais et sans alcool.",
  },
  dessert: {
    slug: "desserts",
    titre: "Desserts à Cotonou",
    accroche: "Yaourt et glace à la boule pour finir le repas.",
  },
};

/** Un montant. `insecable` : pour l'affichage, une somme ne se coupe jamais en deux lignes (« 5 000 F »
 *  se cassait en « 5 / 000 / F » dans une colonne étroite, vu à 390 px). Les fichiers texte (llms.txt,
 *  carte.md, descriptions) gardent des espaces simples. */
export const f = (n: number, insecable = false) => {
  const e = insecable ? " " : " ";
  return `${n.toLocaleString("fr-FR").replace(/ | | /g, e)}${e}F`;
};

/** Tous les prix d'un plat (tailles, fourchettes, paliers), sans les « prix sur demande ». */
export function prixDe(p: Plat): number[] {
  return [p.p, p.p2 ?? 0, p.pMax ?? 0, ...(p.paliers ?? []).map(([, v]) => v)].filter((n) => n > 0);
}

export function fourchette(plats: Plat[]): [number, number] {
  const tous = plats.flatMap(prixDe);
  return [Math.min(...tous), Math.max(...tous)];
}

/** Le prix d'un plat en toutes lettres, tel que la carte l'affiche. */
export function prixTexte(p: Plat, insecable = false): string {
  const m = (n: number) => f(n, insecable);
  if (p.p <= 0) return "prix sur demande";
  if (p.pMax) return `de ${m(p.p)} à ${m(p.pMax)} selon la garniture`;
  if (p.paliers) return p.paliers.map(([nom, v]) => `${nom} ${m(v)}`).join(", ");
  if (p.p2) {
    const [a, b] = p.tailles ?? ["Normal", "Grand"];
    return `${a} ${m(p.p)}, ${b} ${m(p.p2)}`;
  }
  return m(p.p);
}

export const PRIX_CARTE = fourchette(CARTE.flatMap((c) => c.items));

export function rubrique(id: string): Cat {
  const c = CARTE.find((x) => x.id === id);
  if (!c) throw new Error(`rubrique inconnue : ${id}`);
  return c;
}

export function chemin(c: Cat): string {
  return `/carte/${RUBRIQUES[c.id].slug}/`;
}

/** La phrase qui dit tout, en 40 à 60 mots : c'est elle que les IA citent. */
export const RESUME_MAISON =
  `${MAISON.nom} est un restaurant de ${MAISON.ville}, au ${MAISON.pays}, dont la spécialité est la braise : ` +
  `grillades au feu de bois, sauces du pays, pizzas, chawarma, burgers, salades, petit-déjeuner et cocktails. ` +
  `La carte compte ${NB_PLATS} plats, de ${f(PRIX_CARTE[0])} à ${f(PRIX_CARTE[1])} CFA. ` +
  `Sur place, à emporter ou en livraison, et la commande part sur WhatsApp.`;

const noms = (id: string) => rubrique(id).items.map((p) => p.n);

/**
 * LA FAQ. Chaque réponse tient debout seule (40 à 60 mots) et ne contient que
 * des faits de ce fichier ou de la carte. Le `FAQPage` du balisage est bâti
 * sur CE tableau : la question visible et la question balisée sont la même
 * chaîne, elles ne peuvent pas diverger.
 */
export function faq(): { q: string; r: string }[] {
  const [gb, gh] = fourchette(rubrique("grillades").items);
  const [pb, ph] = fourchette(rubrique("pizza").items);
  const [sb, sh] = fourchette(rubrique("sauces").items);
  const sauces = noms("sauces").filter((n) => /gombo|krinkrin|feuille|graine|arachide/i.test(n));
  return [
    {
      q: "Où manger du braisé au feu de bois à Cotonou ?",
      r: `${MAISON.nom} est un restaurant de Cotonou dont la spécialité est la braise : ${noms("grillades")
        .filter((n) => !/attiéké|frit/i.test(n)).join(", ").toLowerCase()} grillés au feu de bois, de ${f(gb)} à ${f(gh)}, ` +
        `servis avec l'accompagnement de votre choix (riz, attiéké, aloco, frites, igname frit…).`,
    },
    {
      q: "Combien coûte un repas chez Au Braisé d'Or ?",
      r: `Les ${NB_PLATS} plats de la carte vont de ${f(PRIX_CARTE[0])} à ${f(PRIX_CARTE[1])} CFA. ` +
        `Les grillades coûtent de ${f(gb)} à ${f(gh)}, les pizzas de ${f(pb)} à ${f(ph)}, les sauces du pays ` +
        `de ${f(sb)} à ${f(sh)} selon ce qu'on met dedans. Tous les prix sont affichés sur la carte en ligne.`,
    },
    {
      q: "Quelles sauces béninoises trouve-t-on à la carte ?",
      r: `${sauces.join(", ")}, mais aussi sauce tomate, tête de mouton, pieds de bœuf et Yassa : ` +
        `${rubrique("sauces").items.length} sauces servies avec l'accompagnement de votre choix, ` +
        `dont telibo, agbéli, pâte de maïs, akassa, igname pilée et riz au gras.`,
    },
    {
      q: "Peut-on commander à emporter ou se faire livrer ?",
      r: `Oui. Sur la carte en ligne, on choisit ses plats puis « Sur place », « À emporter » ou « Livraison » : ` +
        `la commande part sur WhatsApp déjà rédigée, avec le total, et la maison répond pour confirmer. ` +
        `On peut aussi écrire directement au ${MAISON.whatsapp}.`,
    },
    {
      q: "Au Braisé d'Or est-il ouvert tous les jours ?",
      r: `Oui, ${MAISON.nom} est ouvert tous les jours et le WiFi est disponible 24h/24. ` +
        `Pour une grande table, un évènement ou une livraison, le plus simple est d'écrire sur WhatsApp au ` +
        `${MAISON.whatsapp} ou d'appeler le ${MAISON.telephone2}.`,
    },
    {
      q: "Proposez-vous un service traiteur à Cotonou ?",
      r: `Oui. ${MAISON.nom} déplace la braise chez vous pour vos réceptions, et reçoit aussi vos ` +
        `évènements dans sa place des fêtes, à Cotonou. La demande se fait sur WhatsApp au ` +
        `${MAISON.whatsapp} ou par téléphone au ${MAISON.telephone2}.`,
    },
    {
      q: "Peut-on organiser un anniversaire ou un mariage au restaurant ?",
      r: `Oui. ${MAISON.nom} dispose d'une place des fêtes à Cotonou : un espace pour les anniversaires, ` +
        `les mariages et les évènements, avec la cuisine de la maison à la carte. ` +
        `Pour réserver, écrivez sur WhatsApp au ${MAISON.whatsapp}.`,
    },
    {
      q: "Quel type de cuisine sert Au Braisé d'Or ?",
      r: `« ${MAISON.devise} » : une ${MAISON.cuisines}. Grillades au feu de bois et sauces du pays côté ` +
        `Afrique, pizzas et salades côté Europe, burgers côté Amérique, plus le chawarma, ` +
        `un petit-déjeuner et des cocktails de fruits frais sans alcool.`,
    },
  ];
}
