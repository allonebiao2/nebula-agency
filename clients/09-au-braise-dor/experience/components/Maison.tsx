import Link from "next/link";
import { NB_PLATS } from "@/data/carte";
import { MAISON, PRIX_CARTE, RESUME_MAISON, f } from "@/data/maison";
import { LiensRubriques } from "./LiensSite";

/**
 * LE BANDEAU DE LA MAISON, entre l'expérience et la carte.
 *
 * ⚠️ POURQUOI IL EXISTE (2026-09-18, passe SEO) : la page n'avait AUCUN titre
 * de niveau 1 (le premier titre était « SAUCEGOMBO », le nom d'un plat du
 * carrousel), et le mot « restaurant » n'apparaissait nulle part dans le texte
 * visible, pas plus que « Bénin ». Pour Google, c'était une page de plats, pas
 * un restaurant de Cotonou. Ce bandeau porte le H1, la phrase qui dit tout
 * (celle que les IA citent) et les liens vers chaque rubrique.
 */
export default function Maison() {
  const faits = [
    MAISON.ouverture,
    MAISON.wifi,
    `${NB_PLATS} plats, de ${f(PRIX_CARTE[0])} à ${f(PRIX_CARTE[1])}`,
    "Sur place · à emporter · livraison",
    "Traiteur et place des fêtes",
  ];
  return (
    <section
      id="maison"
      className="relative z-10 border-t border-black/[0.06] px-6 pb-16 pt-20 text-[color:var(--encre)]"
      style={{ background: "linear-gradient(180deg, var(--mur) 0%, var(--mur-2) 100%)" }}
    >
      <div className="mx-auto max-w-5xl">
        <p className="mb-4 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]">
          Restaurant · {MAISON.ville}, {MAISON.pays}
        </p>
        <h1 className="police-titre max-w-4xl text-[clamp(2.1rem,5.6vw,4.2rem)] font-extralight leading-[1.02]">
          {MAISON.nom}, la{" "}
          <span className="font-extrabold italic" style={{ color: "#a8542f" }}>
            braise au feu de bois
          </span>{" "}
          à {MAISON.ville}
        </h1>
        <p className="mt-6 max-w-3xl text-[1rem] leading-relaxed text-[color:var(--encre-2)] md:text-[1.06rem]">
          {RESUME_MAISON}
        </p>
        <ul className="mt-7 flex flex-wrap gap-2">
          {faits.map((t) => (
            <li
              key={t}
              className="rounded-full bg-[color:var(--encre)] px-4 py-2 text-[0.8rem] font-medium text-[color:var(--mur)]"
            >
              {t}
            </li>
          ))}
        </ul>
        <div className="mt-12 grid gap-8 md:grid-cols-[1fr_auto] md:items-end">
          <div>
            <h2 className="police-titre mb-4 text-[1.2rem] font-extrabold">La carte, rubrique par rubrique</h2>
            <LiensRubriques clair />
          </div>
          <div className="flex flex-wrap gap-3 md:justify-end">
            <Link
              href="/traiteur-et-place-des-fetes/"
              className="rounded-full border border-[color:var(--encre)] px-5 py-2.5 text-[0.85rem] font-semibold transition hover:bg-[color:var(--encre)] hover:text-[color:var(--mur)]"
            >
              Traiteur et place des fêtes
            </Link>
            <Link
              href="/commander/"
              className="rounded-full border border-[color:var(--encre)] px-5 py-2.5 text-[0.85rem] font-semibold transition hover:bg-[color:var(--encre)] hover:text-[color:var(--mur)]"
            >
              Comment commander
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
