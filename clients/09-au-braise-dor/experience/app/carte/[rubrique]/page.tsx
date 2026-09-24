import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ACC, CARTE } from "@/data/carte";
import { MAISON, RUBRIQUES, SITE, chemin, fourchette, f, prixTexte } from "@/data/maison";
import Ld from "@/components/Ld";
import PageSimple, { BoutonWhatsApp, Surtitre } from "@/components/PageSimple";

/**
 * UNE PAGE PAR RUBRIQUE DE LA CARTE (« Grillades au feu de bois à Cotonou »,
 * « Sauces du pays à Cotonou »…). Une seule page ne peut pas répondre à la
 * fois à « braisé Cotonou », « pizza Cotonou » et « chawarma Cotonou » : chaque
 * recherche mérite une page qui ne parle que d'elle, avec les vrais plats et
 * les vrais prix, lus dans `carte.ts`.
 */
const parSlug = (slug: string) => CARTE.find((c) => RUBRIQUES[c.id]?.slug === slug);

export function generateStaticParams() {
  return CARTE.map((c) => ({ rubrique: RUBRIQUES[c.id].slug }));
}

export function generateMetadata({ params }: { params: { rubrique: string } }): Metadata {
  const c = parSlug(params.rubrique);
  if (!c) return {};
  const r = RUBRIQUES[c.id];
  const [bas, haut] = fourchette(c.items);
  const titre = `${r.titre} | ${MAISON.nom}`;
  const description = `${r.accroche} De ${f(bas)} à ${f(haut)} CFA, chez ${MAISON.nom}, restaurant à Cotonou.`;
  return {
    title: titre,
    description,
    alternates: { canonical: chemin(c) },
    openGraph: {
      title: titre, description, url: `${SITE}${chemin(c)}`, siteName: MAISON.nom,
      images: ["/og.jpg"], locale: "fr_FR", type: "website",
    },
  };
}

export default function PageRubrique({ params }: { params: { rubrique: string } }) {
  const c = parSlug(params.rubrique);
  if (!c) notFound();
  const r = RUBRIQUES[c.id];
  const [bas, haut] = fourchette(c.items);
  const autres = CARTE.filter((x) => x.id !== c.id);
  return (
    <PageSimple ariane={[{ nom: "La carte", href: "/carte/" }, { nom: c.label, href: chemin(c) }]}>
      <Ld
        donnees={{
          "@context": "https://schema.org",
          "@type": "MenuSection",
          name: `${c.label} · ${MAISON.nom}`,
          description: r.accroche,
          url: `${SITE}${chemin(c)}`,
          isPartOf: { "@id": `${SITE}/#restaurant` },
          hasMenuItem: c.items.map((p) => ({
            "@type": "MenuItem",
            name: p.n,
            ...(p.d ? { description: p.d } : {}),
            ...(p.img ? { image: `${SITE}${p.img}` } : {}),
            ...(p.p > 0 ? { offers: { "@type": "Offer", price: String(p.p), priceCurrency: "XOF" } } : {}),
          })),
        }}
      />
      <Surtitre>{MAISON.nom} · {MAISON.ville}, {MAISON.pays}</Surtitre>
      <h1 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extrabold leading-[1.05]">{r.titre}</h1>
      <p className="mt-5 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)]">
        {r.accroche} {c.items.length} {c.label.toLowerCase()} à la carte, de {f(bas)} à {f(haut)} CFA
        {c.note ? `. ${c.note}` : "."}
      </p>

      <ul className="mt-10 grid gap-5 sm:grid-cols-2">
        {c.items.map((p) => (
          <li key={p.n} className="overflow-hidden rounded-2xl border border-black/[0.07] bg-white/70">
            {p.img && (
              <div className="relative aspect-[5/3] bg-[#e7e0d8]">
                <Image
                  src={p.img}
                  alt={`${p.n}, ${MAISON.nom} à Cotonou`}
                  fill
                  loading="lazy"
                  sizes="(max-width: 640px) 90vw, 460px"
                  className="object-cover"
                />
              </div>
            )}
            <div className="p-5">
              {/* ⚠️ Le prix passe SOUS le nom sur téléphone : forcé à côté, « Normal 3 000 F,
                  Grand 6 000 F » débordait de la carte et se faisait couper (vu à 390 px). */}
              <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
                <h2 className="police-titre text-[1.15rem] font-extrabold">{p.n}</h2>
                <p className="text-[0.9rem] font-semibold text-[#a8542f] sm:max-w-[55%] sm:text-right">{prixTexte(p, true)}</p>
              </div>
              {p.d && <p className="mt-2 text-[0.9rem] leading-relaxed text-[color:var(--encre-2)]">{p.d}</p>}
              {p.choix && (
                <p className="mt-2 text-[0.85rem] text-[color:var(--encre-2)]">
                  {p.choix.libelle} : {p.choix.options.join(" ou ")}.
                </p>
              )}
              {p.p > 0 && (
                <div className="mt-4">
                  <BoutonWhatsApp
                    texte="Commander sur WhatsApp"
                    message={`Bonjour ${MAISON.nom}, je voudrais commander : ${p.n} (${prixTexte(p)}).`}
                  />
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>

      {c.acc && (
        <section className="mt-12">
          <h2 className="police-titre mb-3 text-[1.3rem] font-extrabold">Les accompagnements au choix</h2>
          <p className="text-[0.95rem] leading-relaxed text-[color:var(--encre-2)]">{ACC[c.acc].join(", ")}.</p>
        </section>
      )}

      <section className="mt-14 rounded-2xl bg-[color:var(--encre)] p-7 text-[color:var(--mur)]">
        <h2 className="police-titre text-[1.4rem] font-extrabold">Commander plusieurs plats d&apos;un coup</h2>
        <p className="mt-2 max-w-2xl text-[0.92rem] leading-relaxed opacity-85">
          Sur la carte complète, on ajoute ses plats, on choisit sur place, à emporter ou en livraison, et la
          commande part sur WhatsApp déjà rédigée, avec le total.
        </p>
        <Link
          href="/#carte"
          className="mt-5 inline-block rounded-full bg-[color:var(--mur)] px-5 py-3 text-[0.9rem] font-semibold text-[color:var(--encre)]"
        >
          Ouvrir la carte et commander
        </Link>
      </section>

      <section className="mt-14">
        <h2 className="police-titre mb-4 text-[1.3rem] font-extrabold">Les autres rubriques de la carte</h2>
        <ul className="flex flex-wrap gap-2">
          {autres.map((x) => (
            <li key={x.id}>
              <Link
                href={chemin(x)}
                className="inline-block rounded-full border border-black/[0.1] px-4 py-2 text-[0.85rem] hover:border-[#a8542f] hover:text-[#a8542f]"
              >
                {RUBRIQUES[x.id].titre.split(" à Cotonou")[0]}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </PageSimple>
  );
}
