import Experience from "@/components/Experience";
import Carte from "@/components/Carte";
import Pied from "@/components/Pied";
import DonneesStructurees from "@/components/DonneesStructurees";

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
      <Carte />
      <Pied />
    </main>
  );
}
