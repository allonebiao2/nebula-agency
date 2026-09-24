import type { Metadata } from "next";
import Link from "next/link";
import { LiensRubriques } from "@/components/LiensSite";

/* La 404 dit qu'elle est une 404 : « noindex », et AUCUN canonique (elle en
   héritait un, celui de l'accueil, ce qui revenait à se déclarer sa copie). */
export const metadata: Metadata = {
  title: "Page introuvable · Au Braisé d'Or",
  robots: { index: false, follow: true },
};

export default function Introuvable() {
  return (
    <main className="flex min-h-screen items-center bg-[color:var(--mur)] px-6 text-[color:var(--encre)]">
      <div className="mx-auto max-w-2xl">
        <p className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]">Page introuvable</p>
        <h1 className="police-titre text-[clamp(2rem,5vw,3.2rem)] font-extrabold leading-[1.05]">
          Cette page n&apos;est pas à la carte.
        </h1>
        <p className="mt-4 text-[0.98rem] text-[color:var(--encre-2)]">
          Retour à{" "}
          <Link href="/" className="font-semibold text-[#a8542f] underline underline-offset-4">
            l&apos;accueil d&apos;Au Braisé d&apos;Or
          </Link>
          , ou directement à une rubrique :
        </p>
        <div className="mt-6">
          <LiensRubriques />
        </div>
      </div>
    </main>
  );
}
