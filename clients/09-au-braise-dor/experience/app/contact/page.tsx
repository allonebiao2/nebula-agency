import type { Metadata } from "next";
import Link from "next/link";
import { WHATSAPP } from "@/data/dishes";
import { MAISON, SITE } from "@/data/maison";
import { LiensRubriques } from "@/components/LiensSite";
import PageSimple, { BoutonWhatsApp, Surtitre } from "@/components/PageSimple";

const TITRE = `Contact et infos pratiques · ${MAISON.nom}, restaurant à Cotonou`;
const DESCRIPTION =
  `Contacter ${MAISON.nom}, restaurant à Cotonou (Bénin) : WhatsApp ${MAISON.whatsapp}, téléphone ` +
  `${MAISON.telephone2}. Ouvert tous les jours, WiFi 24h/24.`;

export const metadata: Metadata = {
  title: TITRE,
  description: DESCRIPTION,
  alternates: { canonical: "/contact/" },
  openGraph: {
    title: TITRE, description: DESCRIPTION, url: `${SITE}/contact/`, siteName: MAISON.nom,
    images: ["/og.jpg"], locale: "fr_FR", type: "website",
  },
};

/**
 * ⛔ Pas d'adresse de rue, pas d'horaires précis, pas de plan : la maison ne
 * les a jamais donnés, et la fiche Google (encore inaccessible) porte une
 * adresse lisible à moitié. Le jour où elle est confirmée, elle entre dans
 * `maison.ts`, puis ici, dans le balisage et sur la fiche Google, À L'IDENTIQUE.
 */
export default function PageContact() {
  const lignes: [string, React.ReactNode][] = [
    ["WhatsApp", <a key="w" href={`https://wa.me/${WHATSAPP}`} className="underline underline-offset-4">{MAISON.whatsapp}</a>],
    ["Téléphone", <a key="t" href={`tel:+229${MAISON.telephone2.replace(/ /g, "")}`} className="underline underline-offset-4">{MAISON.telephone2}</a>],
    ["E-mail", <a key="e" href={`mailto:${MAISON.email}`} className="underline underline-offset-4">{MAISON.email}</a>],
    ["Ville", `${MAISON.ville}, ${MAISON.pays}`],
    ["Ouverture", MAISON.ouverture],
    ["Sur place", MAISON.wifi],
    ["Services", "Sur place, à emporter, livraison, traiteur, place des fêtes"],
  ];
  return (
    <PageSimple ariane={[{ nom: "Contact", href: "/contact/" }]}>
      <Surtitre>{MAISON.nom} · {MAISON.ville}, {MAISON.pays}</Surtitre>
      <h1 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extrabold leading-[1.05]">
        Contact et infos pratiques
      </h1>
      <p className="mt-5 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)]">
        {MAISON.nom} est un restaurant de {MAISON.ville}, ouvert tous les jours. Le plus rapide pour commander,
        réserver une table ou demander un évènement : WhatsApp au {MAISON.whatsapp}.
      </p>
      <dl className="mt-10 divide-y divide-black/[0.07] rounded-2xl border border-black/[0.07] bg-white/70">
        {lignes.map(([k, v]) => (
          <div key={k} className="grid grid-cols-[8.5rem_1fr] gap-4 px-5 py-4 text-[0.95rem]">
            <dt className="font-semibold">{k}</dt>
            <dd className="text-[color:var(--encre-2)]">{v}</dd>
          </div>
        ))}
      </dl>
      <div className="mt-8">
        <BoutonWhatsApp texte="Écrire sur WhatsApp" message={`Bonjour ${MAISON.nom}, `} />
      </div>
      <section className="mt-14">
        <h2 className="police-titre mb-4 text-[1.3rem] font-extrabold">La carte</h2>
        <LiensRubriques />
        <p className="mt-4 text-[0.9rem] text-[color:var(--encre-2)]">
          <Link href="/carte/" className="font-semibold text-[#a8542f] underline underline-offset-4">
            La carte complète et les prix
          </Link>{" "}
          · Mentions : RC {MAISON.rc} · IFU {MAISON.ifu}
        </p>
      </section>
    </PageSimple>
  );
}
