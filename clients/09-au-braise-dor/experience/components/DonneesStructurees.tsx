import { CARTE } from "@/data/carte";
import { WHATSAPP } from "@/data/dishes";

/**
 * LES DONNÉES STRUCTURÉES.
 *
 * Sans elles, un prix réel ne s'affiche jamais dans un résultat Google et la
 * maison n'existe pas comme restaurant, seulement comme page.
 *
 * ⚠️ TOUT EST LU DANS `CARTE`, RIEN N'EST RECOPIÉ. Une carte qui change met à
 *    jour le balisage toute seule. Recopier, c'est promettre à Google un prix
 *    que la page ne pratique plus.
 *
 * ⛔ ON N'ANNONCE QUE CE QUI EST VRAI ET VISIBLE :
 *    - aucune note, aucun avis, aucun `aggregateRating` (personne n'en a donné) ;
 *    - aucune adresse de rue (la maison ne l'a jamais donnée) : la ville et le
 *      pays suffisent, une adresse inventée est pire que pas d'adresse ;
 *    - aucun horaire précis (« ouvert tous les jours » n'est pas un horaire) ;
 *    - un plat sans prix (`p: 0`) n'a PAS d'offre : il est « prix sur demande »
 *      sur la page, il doit l'être ici aussi.
 */
export default function DonneesStructurees() {
  const site = "https://au-braise-dor.pages.dev";

  /**
   * ⚠️ TROIS FAÇONS D'AVOIR UN PRIX, et les confondre ment au client :
   *   - `pMax` est une FOURCHETTE (les sauces : le prix dépend de ce qu'on met
   *     dedans) → une offre groupée, de la borne basse à la borne haute ;
   *   - `p2` est une DEUXIÈME TAILLE, à son propre prix → deux offres ;
   *   - `p: 0` veut dire « prix pas encore donné » → aucune offre.
   * Le premier jet ne lisait que `p` : le site annonçait « jusqu'à 5 000 F »
   * alors que la carte monte à 6 000 F. Un balisage qui sous-estime est un
   * client qui découvre le vrai prix à table.
   */
  const tous = CARTE.flatMap((c) =>
    c.items.flatMap((p) => [p.p, p.p2 ?? 0, p.pMax ?? 0]),
  ).filter((n) => n > 0);
  const bas = Math.min(...tous);
  const haut = Math.max(...tous);

  const offre = (p: (typeof CARTE)[number]["items"][number]) => {
    if (p.p <= 0) return {};
    if (p.pMax) {
      return {
        offers: {
          "@type": "AggregateOffer",
          lowPrice: String(p.p),
          highPrice: String(p.pMax),
          priceCurrency: "XOF",
          offerCount: 1,
        },
      };
    }
    const tailles = p.tailles ?? ["Normal", "Grand"];
    const liste = [
      { "@type": "Offer", price: String(p.p), priceCurrency: "XOF",
        availability: "https://schema.org/InStock",
        ...(p.p2 ? { name: tailles[0] } : {}) },
      ...(p.p2
        ? [{ "@type": "Offer", price: String(p.p2), priceCurrency: "XOF",
             availability: "https://schema.org/InStock", name: tailles[1] }]
        : []),
    ];
    return { offers: liste.length === 1 ? liste[0] : liste };
  };

  const donnees = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "@id": `${site}/#restaurant`,
    name: "Au Braisé d'Or",
    slogan: "De Paris à Cotonou",
    description:
      "Grillades au feu de bois, sauces du pays, pizzas, chawarma, salades et cocktails. Sur place, à emporter, traiteur et réceptions.",
    url: site,
    image: `${site}/og.jpg`,
    telephone: "+2290156057157",
    email: "aubraisedor@gmail.com",
    address: {
      "@type": "PostalAddress",
      addressLocality: "Cotonou",
      addressCountry: "BJ",
    },
    servesCuisine: ["Africaine", "Européenne", "Américaine", "Grillades"],
    priceRange: `${bas.toLocaleString("fr-FR")} - ${haut.toLocaleString("fr-FR")} XOF`,
    currenciesAccepted: "XOF",
    amenityFeature: [
      { "@type": "LocationFeatureSpecification", name: "WiFi 24h/24", value: true },
      { "@type": "LocationFeatureSpecification", name: "Place des fêtes", value: true },
      { "@type": "LocationFeatureSpecification", name: "Traiteur", value: true },
    ],
    potentialAction: {
      "@type": "OrderAction",
      target: `https://wa.me/${WHATSAPP}`,
      deliveryMethod: "http://purl.org/goodrelations/v1#DeliveryModeOwnFleet",
    },
    hasMenu: {
      "@type": "Menu",
      name: "La carte d'Au Braisé d'Or",
      inLanguage: "fr",
      hasMenuSection: CARTE.map((c) => ({
        "@type": "MenuSection",
        name: c.label,
        description: c.tag,
        hasMenuItem: c.items.map((p) => ({
          "@type": "MenuItem",
          name: p.n,
          ...(p.d ? { description: p.d } : {}),
          ...(p.img ? { image: `${site}${p.img}` } : {}),
          ...offre(p),
        })),
      })),
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(donnees) }}
    />
  );
}
