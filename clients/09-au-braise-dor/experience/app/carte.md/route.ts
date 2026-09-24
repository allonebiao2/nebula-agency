import { ACC, CARTE, NB_PLATS } from "@/data/carte";
import { MAISON, PRIX_CARTE, SITE, f, prixTexte } from "@/data/maison";

/* `/carte.md` : la carte et ses prix en Markdown, pour un agent qui compare
   des restaurants sans rendre de page. Lu dans `carte.ts`, jamais recopié. */
export const dynamic = "force-static";

export function GET() {
  const l: string[] = [
    `# La carte d'${MAISON.nom} · ${MAISON.ville}, ${MAISON.pays}`, "",
    `${NB_PLATS} plats, de ${f(PRIX_CARTE[0])} à ${f(PRIX_CARTE[1])} CFA. Prix en francs CFA (XOF).`,
    `Commande : ${SITE}/ (carte en ligne, message WhatsApp déjà rédigé) ou WhatsApp ${MAISON.whatsapp}.`, "",
  ];
  for (const c of CARTE) {
    l.push(`## ${c.label}`, "");
    if (c.note) l.push(c.note, "");
    for (const p of c.items) l.push(`- **${p.n}** : ${prixTexte(p)}${p.d ? `. ${p.d}` : ""}`);
    if (c.acc) l.push("", `Accompagnements au choix : ${ACC[c.acc].join(", ")}.`);
    l.push("");
  }
  return new Response(l.join("\n"), { headers: { "Content-Type": "text/markdown; charset=utf-8" } });
}
