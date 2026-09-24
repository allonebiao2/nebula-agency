import type { Metadata } from "next";
import Link from "next/link";
import { NB_PLATS } from "@/data/carte";
import { MAISON, SITE } from "@/data/maison";
import Ld from "@/components/Ld";
import PageSimple, { BoutonWhatsApp, Surtitre } from "@/components/PageSimple";

const TITRE = `Commander à Cotonou : sur place, à emporter, livraison · ${MAISON.nom}`;
const DESCRIPTION =
  `Commander chez ${MAISON.nom} à Cotonou : sur place, à emporter ou en livraison. La carte en ligne ` +
  `rédige le message WhatsApp, avec le total.`;

export const metadata: Metadata = {
  title: TITRE,
  description: DESCRIPTION,
  alternates: { canonical: "/commander/" },
  openGraph: {
    title: TITRE, description: DESCRIPTION, url: `${SITE}/commander/`, siteName: MAISON.nom,
    images: ["/og.jpg"], locale: "fr_FR", type: "website",
  },
};

/** Les étapes, telles que la carte en ligne les fait vraiment (`Carte.tsx`). */
const ETAPES = [
  ["Ouvrir la carte", `Les ${NB_PLATS} plats sont sur la carte en ligne, avec leur photo et leur prix.`],
  ["Ajouter ses plats", "Un appui sur un plat ouvre sa fiche : taille, accompagnement, quantité, puis « Ajouter »."],
  ["Choisir le mode", "Sur place, à emporter ou en livraison, en bas de l'écran, à côté du total."],
  ["Envoyer sur WhatsApp", "La commande part déjà rédigée, avec chaque plat, le mode choisi et le total."],
  ["La maison confirme", `${MAISON.nom} répond sur WhatsApp pour confirmer la commande.`],
] as const;

export default function PageCommander() {
  return (
    <PageSimple ariane={[{ nom: "Commander", href: "/commander/" }]}>
      <Ld
        donnees={{
          "@context": "https://schema.org",
          "@type": "HowTo",
          name: `Commander chez ${MAISON.nom} à Cotonou`,
          step: ETAPES.map(([nom, texte], i) => ({
            "@type": "HowToStep",
            position: i + 1,
            name: nom,
            text: texte,
          })),
        }}
      />
      <Surtitre>{MAISON.nom} · {MAISON.ville}, {MAISON.pays}</Surtitre>
      <h1 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extrabold leading-[1.05]">
        Commander : sur place, à emporter ou en livraison
      </h1>
      <p className="mt-5 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)]">
        Chez {MAISON.nom}, à {MAISON.ville}, on commande en un geste : la carte en ligne rédige le message WhatsApp
        à votre place, avec les plats, le mode et le total. Rien n&apos;est payé sur le site.
      </p>
      <ol className="mt-10 space-y-4">
        {ETAPES.map(([nom, texte], i) => (
          <li key={nom} className="flex gap-4 rounded-2xl border border-black/[0.07] bg-white/70 p-5">
            <span className="police-titre flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--encre)] text-[0.95rem] font-extrabold text-[color:var(--mur)]">
              {i + 1}
            </span>
            <div>
              <h2 className="police-titre text-[1.1rem] font-extrabold">{nom}</h2>
              <p className="mt-1 text-[0.92rem] leading-relaxed text-[color:var(--encre-2)]">{texte}</p>
            </div>
          </li>
        ))}
      </ol>
      <div className="mt-10 flex flex-wrap gap-3">
        <Link
          href="/#carte"
          className="rounded-full bg-[color:var(--encre)] px-5 py-3 text-[0.9rem] font-semibold text-[color:var(--mur)]"
        >
          Ouvrir la carte et commander
        </Link>
        <BoutonWhatsApp texte={`Écrire au ${MAISON.whatsapp}`} message={`Bonjour ${MAISON.nom}, je voudrais passer une commande.`} />
      </div>
    </PageSimple>
  );
}
