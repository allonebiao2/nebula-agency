import type { Metadata } from "next";
import Link from "next/link";
import { MAISON, SITE } from "@/data/maison";
import { LiensRubriques } from "@/components/LiensSite";
import PageSimple, { BoutonWhatsApp, Surtitre } from "@/components/PageSimple";

const TITRE = `Traiteur et place des fêtes à Cotonou · ${MAISON.nom}`;
const DESCRIPTION =
  `Traiteur et place des fêtes à Cotonou : ${MAISON.nom} déplace la braise chez vous et reçoit vos ` +
  `anniversaires, mariages et évènements. WhatsApp ${MAISON.whatsapp}.`;

export const metadata: Metadata = {
  title: TITRE,
  description: DESCRIPTION,
  alternates: { canonical: "/traiteur-et-place-des-fetes/" },
  openGraph: {
    title: TITRE, description: DESCRIPTION, url: `${SITE}/traiteur-et-place-des-fetes/`, siteName: MAISON.nom,
    images: ["/og.jpg"], locale: "fr_FR", type: "website",
  },
};

/**
 * ⛔ Rien d'inventé : la maison dit « on déplace la braise chez vous, et on
 * reçoit vos évènements dans notre place des fêtes » et « un espace pour vos
 * anniversaires, mariages et évènements, avec la cuisine de la maison à la
 * carte ». Pas de capacité, pas de tarif de location, pas de menu traiteur :
 * personne ne les a donnés. Le jour où ils arrivent, ils vont dans `maison.ts`.
 */
export default function PageTraiteur() {
  return (
    <PageSimple ariane={[{ nom: "Traiteur et place des fêtes", href: "/traiteur-et-place-des-fetes/" }]}>
      <Surtitre>{MAISON.nom} · {MAISON.ville}, {MAISON.pays}</Surtitre>
      <h1 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extrabold leading-[1.05]">
        Traiteur et place des fêtes à {MAISON.ville}
      </h1>
      <p className="mt-5 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)]">
        {MAISON.nom} ne sert pas seulement à table. Le restaurant déplace la braise chez vous pour vos réceptions,
        et reçoit vos évènements dans sa place des fêtes, à {MAISON.ville}, avec la cuisine de la maison.
      </p>

      <div className="mt-10 grid gap-5 md:grid-cols-2">
        <section className="rounded-2xl border border-black/[0.07] bg-white/70 p-6">
          <h2 className="police-titre text-[1.35rem] font-extrabold">Le service traiteur</h2>
          <p className="mt-3 text-[0.95rem] leading-relaxed text-[color:var(--encre-2)]">
            On déplace la braise chez vous : les grillades au feu de bois et la cuisine de la maison viennent à
            votre réception. Dites-nous la date, le lieu et le nombre d&apos;invités sur WhatsApp, la maison vous
            répond.
          </p>
        </section>
        <section className="rounded-2xl border border-black/[0.07] bg-white/70 p-6">
          <h2 className="police-titre text-[1.35rem] font-extrabold">La place des fêtes</h2>
          <p className="mt-3 text-[0.95rem] leading-relaxed text-[color:var(--encre-2)]">
            Un espace pour vos anniversaires, mariages et évènements, avec la cuisine de la maison à la carte.
            Pour connaître les disponibilités, écrivez sur WhatsApp ou appelez le {MAISON.telephone2}.
          </p>
        </section>
      </div>

      <div className="mt-10">
        <BoutonWhatsApp
          texte="Demander pour un évènement"
          message={`Bonjour ${MAISON.nom}, je voudrais des informations pour un évènement (traiteur ou place des fêtes). Date : . Nombre d'invités : .`}
        />
      </div>

      <section className="mt-14">
        <h2 className="police-titre mb-4 text-[1.3rem] font-extrabold">La cuisine de la maison, rubrique par rubrique</h2>
        <LiensRubriques />
        <p className="mt-4 text-[0.9rem] text-[color:var(--encre-2)]">
          Voir aussi{" "}
          <Link href="/carte/" className="font-semibold text-[#a8542f] underline underline-offset-4">
            la carte complète et les prix
          </Link>
          .
        </p>
      </section>
    </PageSimple>
  );
}
