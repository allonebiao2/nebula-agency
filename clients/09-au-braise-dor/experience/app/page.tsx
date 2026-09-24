import type { Metadata } from "next";
import Experience from "@/components/Experience";
import Carte from "@/components/Carte";
import Pied from "@/components/Pied";
import DonneesStructurees from "@/components/DonneesStructurees";
import Maison from "@/components/Maison";
import Questions from "@/components/Questions";

export const metadata: Metadata = { alternates: { canonical: "/" } };

/**
 * L'expérience passe AU-DESSUS de la carte : les quatre plats signature
 * d'abord, puis les 48 plats commandables. Décision de Mongazi : le
 * restaurant garde sa carte complète ET gagne la vitrine.
 */
export default function Page() {
  return (
    <main>
      <DonneesStructurees />
      <Experience />
      <Maison />
      <Carte />
      <Questions />
      <Pied />
    </main>
  );
}
