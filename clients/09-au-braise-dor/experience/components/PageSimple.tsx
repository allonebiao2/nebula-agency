import Link from "next/link";
import { WHATSAPP } from "@/data/dishes";
import { MAISON, SITE } from "@/data/maison";
import Ld from "./Ld";
import Pied from "./Pied";

/**
 * LE GABARIT DES PAGES DE CONTENU (carte par rubrique, traiteur, commande,
 * contact). Sobre exprès : l'expérience animée reste l'accueil ; ces pages-ci
 * existent pour être LUES, par un client pressé comme par un robot.
 * Le fil d'Ariane visible et son `BreadcrumbList` sont bâtis sur la même liste.
 */
export default function PageSimple({
  ariane,
  children,
}: {
  ariane: { nom: string; href: string }[];
  children: React.ReactNode;
}) {
  const fil = [{ nom: "Accueil", href: "/" }, ...ariane];
  return (
    <div className="min-h-screen bg-[color:var(--mur)] text-[color:var(--encre)]">
      <Ld
        donnees={{
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: fil.map((e, i) => ({
            "@type": "ListItem",
            position: i + 1,
            name: e.nom,
            item: `${SITE}${e.href}`,
          })),
        }}
      />
      {/* ⚠️ Fond OPAQUE en style : `bg-[color:var(--mur)]/95` ne s'applique pas (pas
          d'opacité sur une variable CSS), l'en-tête était transparent et le texte passait
          dessous (vu à 390 px). Collant seulement sur grand écran : en téléphone il tient
          sur trois lignes et mangerait l'écran. */}
      <header
        className="z-30 border-b border-black/[0.07] md:sticky md:top-0"
        style={{ background: "var(--mur)" }}
      >
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-3">
          <Link href="/" className="police-titre text-[1.05rem] font-extrabold tracking-tight">
            {MAISON.nom}
          </Link>
          <nav aria-label="Navigation principale" className="flex flex-wrap items-center gap-x-5 gap-y-1 text-[0.85rem]">
            <Link href="/carte/" className="hover:text-[#a8542f]">La carte</Link>
            <Link href="/traiteur-et-place-des-fetes/" className="hover:text-[#a8542f]">Traiteur</Link>
            <Link href="/commander/" className="hover:text-[#a8542f]">Commander</Link>
            <Link href="/contact/" className="hover:text-[#a8542f]">Contact</Link>
            <a
              href={`https://wa.me/${WHATSAPP}`}
              target="_blank"
              rel="noreferrer"
              className="rounded-full px-4 py-2 font-semibold text-white"
              style={{ background: "#128040" }}
            >
              WhatsApp
            </a>
          </nav>
        </div>
      </header>
      <nav aria-label="Fil d'Ariane" className="mx-auto max-w-5xl px-6 pt-6 text-[0.8rem] text-[color:var(--encre-2)]">
        <ol className="flex flex-wrap gap-1.5">
          {fil.map((e, i) => (
            <li key={e.href} className="flex items-center gap-1.5">
              {i > 0 && <span aria-hidden>›</span>}
              {i < fil.length - 1 ? (
                <Link href={e.href} className="hover:text-[#a8542f]">{e.nom}</Link>
              ) : (
                <span aria-current="page">{e.nom}</span>
              )}
            </li>
          ))}
        </ol>
      </nav>
      <main className="mx-auto max-w-5xl px-6 pb-24 pt-8">{children}</main>
      <Pied />
    </div>
  );
}

export function Surtitre({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]">{children}</p>
  );
}

export function BoutonWhatsApp({ texte, message }: { texte: string; message: string }) {
  return (
    <a
      href={`https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message)}`}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-2 rounded-full px-5 py-3 text-[0.9rem] font-semibold text-white transition hover:brightness-110"
      style={{ background: "#128040" }}
    >
      {texte}
    </a>
  );
}
