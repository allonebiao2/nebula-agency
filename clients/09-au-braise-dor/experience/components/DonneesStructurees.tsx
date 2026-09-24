import { CARTE } from "@/data/carte";
import { WHATSAPP } from "@/data/dishes";
import { MAISON, RESUME_MAISON, faq } from "@/data/maison";
import Ld from "./Ld";

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
  const site = "https://aubraisedor.com";

  /**
   * ⚠️ TROIS FAÇONS D'AVOIR UN PRIX, et les confondre ment au client :
   *   - `pMax` est une FOURCHETTE (les sauces : le prix dépend de ce qu'on met
   *     dedans) → une offre groupée, de la borne basse à la borne haute ;
   *   - `p2` est une DEUXIÈME TAILLE, à son propre prix → deux offres ;
   *   - `paliers` est un BARÈME à N crans (la glace, à la boule) → N offres,
   *     chacune à son prix exact et à son libellé ;
   *   - `p: 0` veut dire « prix pas encore donné » → aucune offre.
   * Le premier jet ne lisait que `p` : le site annonçait « jusqu'à 5 000 F »
   * alors que la carte monte à 6 000 F. Un balisage qui sous-estime est un
   * client qui découvre le vrai prix à table.
   */
  const tous = CARTE.flatMap((c) =>
    c.items.flatMap((p) => [
      p.p,
      p.p2 ?? 0,
      p.pMax ?? 0,
      ...(p.paliers ?? []).map(([, v]) => v),
    ]),
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
    if (p.paliers) {
      return {
        offers: p.paliers.map(([nom, valeur]) => ({
          "@type": "Offer",
          price: String(valeur),
          priceCurrency: "XOF",
          availability: "https://schema.org/InStock",
          name: nom,
        })),
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

  /* ⚠️ UN SEUL GRAPHE (2026-09-18) : le restaurant, le site et la FAQ se
     désignent par leur `@id`. Le `FAQPage` est bâti sur `faq()`, le MÊME
     tableau que les questions affichées : la question balisée est la question
     visible, au caractère près. */
  const restaurant = {
    "@type": "Restaurant",
    "@id": `${site}/#restaurant`,
    name: MAISON.nom,
    /* Les noms sous lesquels on le trouve déjà : l'enseigne, et la fiche Google
       (« AU BRAISÉ D'OR »). Ils aident Google à reconnaître UN établissement. */
    alternateName: ["Restaurant Au Braisé d'Or", "AU BRAISÉ D'OR", "Au Braisé d'Or Cotonou"],
    slogan: MAISON.devise,
    description: RESUME_MAISON,
    url: `${site}/`,
    image: `${site}/og.jpg`,
    logo: `${site}/og.jpg`,
    telephone: MAISON.telephoneInternational,
    email: MAISON.email,
    address: {
      "@type": "PostalAddress",
      addressLocality: MAISON.ville,
      addressRegion: "Littoral",
      addressCountry: "BJ",
    },
    areaServed: { "@type": "City", name: MAISON.ville },
    servesCuisine: [
      "Grillades", "Cuisine béninoise", "Cuisine africaine", "Cuisine européenne",
      "Cuisine américaine", "Pizza", "Chawarma", "Burgers",
    ],
    priceRange: `${bas.toLocaleString("fr-FR")} - ${haut.toLocaleString("fr-FR")} XOF`,
    currenciesAccepted: "XOF",
    amenityFeature: [
      { "@type": "LocationFeatureSpecification", name: "WiFi 24h/24", value: true },
      { "@type": "LocationFeatureSpecification", name: "Place des fêtes", value: true },
      { "@type": "LocationFeatureSpecification", name: "Traiteur", value: true },
    ],
    makesOffer: [
      { name: "Traiteur", url: `${site}/traiteur-et-place-des-fetes/` },
      { name: "Place des fêtes", url: `${site}/traiteur-et-place-des-fetes/` },
      { name: "Livraison à Cotonou", url: `${site}/commander/` },
      { name: "Vente à emporter", url: `${site}/commander/` },
    ].map((o) => ({ "@type": "Offer", itemOffered: { "@type": "Service", name: o.name, url: o.url } })),
    potentialAction: {
      "@type": "OrderAction",
      target: `https://wa.me/${WHATSAPP}`,
      deliveryMethod: "http://purl.org/goodrelations/v1#DeliveryModeOwnFleet",
    },
    hasMenu: {
      "@type": "Menu",
      name: `La carte d'${MAISON.nom}`,
      url: `${site}/carte/`,
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

  const donnees = {
    "@context": "https://schema.org",
    "@graph": [
      restaurant,
      {
        "@type": "WebSite",
        "@id": `${site}/#site`,
        url: `${site}/`,
        name: MAISON.nom,
        inLanguage: "fr",
        publisher: { "@id": `${site}/#restaurant` },
      },
      {
        "@type": "FAQPage",
        "@id": `${site}/#questions`,
        mainEntity: faq().map(({ q, r }) => ({
          "@type": "Question",
          name: q,
          acceptedAnswer: { "@type": "Answer", text: r },
        })),
      },
    ],
  };

  return <Ld donnees={donnees} />;
}
