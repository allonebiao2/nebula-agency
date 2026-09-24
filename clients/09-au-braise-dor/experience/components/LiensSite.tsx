import Link from "next/link";
import { CARTE } from "@/data/carte";
import { RUBRIQUES, chemin } from "@/data/maison";

/**
 * LES LIENS INTERNES. Une page qu'aucun lien n'atteint n'existe pas pour
 * Google : chaque rubrique et chaque service est relié depuis l'accueil, depuis
 * le pied de page et depuis les autres pages. L'ancre dit ce qu'on trouve
 * derrière (« Grillades »), jamais « cliquez ici ».
 */
export function LiensRubriques({ clair = false }: { clair?: boolean }) {
  return (
    <ul className="flex flex-wrap gap-2">
      {CARTE.map((c) => (
        <li key={c.id}>
          <Link
            href={chemin(c)}
            className={
              "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-[0.85rem] font-medium transition " +
              (clair
                ? "border-black/[0.1] bg-white/60 hover:border-[#a8542f] hover:text-[#a8542f]"
                : "border-black/[0.1] hover:border-[#a8542f] hover:text-[#a8542f]")
            }
          >
            {c.label}
            <span className="text-[0.72rem] text-[color:var(--encre-2)]">{c.items.length}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export const SERVICES = [
  { href: "/carte/", texte: "La carte complète et les prix" },
  { href: "/traiteur-et-place-des-fetes/", texte: "Traiteur et place des fêtes" },
  { href: "/commander/", texte: "Commander : sur place, à emporter, livraison" },
  { href: "/contact/", texte: "Contact et infos pratiques" },
];

export function LiensServices() {
  return (
    <ul className="space-y-1.5 text-[0.88rem]">
      {SERVICES.map((s) => (
        <li key={s.href}>
          <Link href={s.href} className="underline decoration-black/20 underline-offset-4 hover:text-[#a8542f]">
            {s.texte}
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function titreRubrique(id: string) {
  return RUBRIQUES[id]?.titre ?? id;
}
