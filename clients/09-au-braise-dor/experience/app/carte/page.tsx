import type { Metadata } from "next";
import Link from "next/link";
import { CARTE, NB_PLATS } from "@/data/carte";
import { MAISON, PRIX_CARTE, RUBRIQUES, SITE, chemin, fourchette, f, prixTexte } from "@/data/maison";
import PageSimple, { Surtitre } from "@/components/PageSimple";

const TITRE = `Carte et prix du restaurant ${MAISON.nom} à Cotonou · ${NB_PLATS} plats`;
const DESCRIPTION =
  `La carte d'${MAISON.nom}, restaurant à Cotonou (Bénin) : ${NB_PLATS} plats de ${f(PRIX_CARTE[0])} à ` +
  `${f(PRIX_CARTE[1])} CFA. Grillades au feu de bois, sauces du pays, pizzas, chawarma, burgers.`;

export const metadata: Metadata = {
  title: TITRE,
  description: DESCRIPTION,
  alternates: { canonical: "/carte/" },
  openGraph: {
    title: TITRE, description: DESCRIPTION, url: `${SITE}/carte/`, siteName: MAISON.nom,
    images: ["/og.jpg"], locale: "fr_FR", type: "website",
  },
};

/**
 * LA CARTE EN TEXTE, tout entière sur une page : ce que cherche celui qui tape
 * « menu restaurant Cotonou » ou « prix braisé Cotonou ». La carte animée de
 * l'accueil reste celle où l'on commande ; celle-ci est celle qu'on LIT.
 */
export default function PageCarte() {
  return (
    <PageSimple ariane={[{ nom: "La carte", href: "/carte/" }]}>
      <Surtitre>{MAISON.nom} · {MAISON.ville}, {MAISON.pays}</Surtitre>
      <h1 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extrabold leading-[1.05]">
        La carte d&apos;{MAISON.nom} et ses prix
      </h1>
      <p className="mt-5 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)]">
        {NB_PLATS} plats en {CARTE.length} rubriques, de {f(PRIX_CARTE[0])} à {f(PRIX_CARTE[1])} CFA, au restaurant{" "}
        {MAISON.nom} à {MAISON.ville}. Les prix sont ceux de la maison, en francs CFA.{" "}
        <Link href="/#carte" className="font-semibold text-[#a8542f] underline underline-offset-4">
          Commander depuis la carte en ligne
        </Link>
        .
      </p>
      <div className="mt-12 space-y-14">
        {CARTE.map((c) => {
          const [bas, haut] = fourchette(c.items);
          return (
            <section key={c.id} id={c.id}>
              <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2 border-b border-black/[0.1] pb-2">
                <h2 className="police-titre text-[1.6rem] font-extrabold">
                  <Link href={chemin(c)} className="hover:text-[#a8542f]">
                    {c.label}
                  </Link>
                </h2>
                <p className="text-[0.85rem] text-[color:var(--encre-2)]">
                  {c.items.length} plats · {f(bas)} à {f(haut)}
                </p>
              </div>
              <p className="mb-4 text-[0.92rem] text-[color:var(--encre-2)]">{RUBRIQUES[c.id].accroche}</p>
              <ul className="divide-y divide-black/[0.06]">
                {c.items.map((p) => (
                  <li key={p.n} className="flex items-start justify-between gap-4 py-3">
                    <div className="min-w-0">
                      <p className="font-semibold">{p.n}</p>
                      {p.d && <p className="text-[0.86rem] text-[color:var(--encre-2)]">{p.d}</p>}
                    </div>
                    <p className="w-[38%] shrink-0 text-right text-[0.88rem] font-semibold text-[#a8542f] sm:w-[30%]">
                      {prixTexte(p, true)}
                    </p>
                  </li>
                ))}
              </ul>
              <Link
                href={chemin(c)}
                className="mt-3 inline-block text-[0.85rem] font-semibold text-[#a8542f] underline underline-offset-4"
              >
                {RUBRIQUES[c.id].titre}
              </Link>
            </section>
          );
        })}
      </div>
    </PageSimple>
  );
}
