import { CARTE, NB_PLATS } from "@/data/carte";
import { MAISON, PRIX_CARTE, RESUME_MAISON, RUBRIQUES, SITE, chemin, f, faq, fourchette } from "@/data/maison";

/* `/llms.txt` : ce qu'une IA doit savoir de la maison, en texte brut, sans
   rendre la page. TOUT est lu dans `maison.ts` et `carte.ts` : un prix changé
   sur la carte change ici au prochain déploiement, jamais recopié à la main. */
export const dynamic = "force-static";

export function GET() {
  const l: string[] = [];
  l.push(`# ${MAISON.nom}`, "", `> ${RESUME_MAISON}`, "");
  l.push("## L'essentiel", "");
  l.push(`- Restaurant à ${MAISON.ville}, ${MAISON.pays}. « ${MAISON.devise} » : ${MAISON.cuisines}.`);
  l.push(`- Spécialité : grillades au feu de bois (la braise).`);
  l.push(`- ${NB_PLATS} plats de ${f(PRIX_CARTE[0])} à ${f(PRIX_CARTE[1])} CFA.`);
  l.push(`- ${MAISON.ouverture}. ${MAISON.wifi}.`);
  l.push(`- Sur place, à emporter, livraison. Traiteur et place des fêtes (anniversaires, mariages, évènements).`);
  l.push(`- Commande : WhatsApp ${MAISON.whatsapp} · téléphone ${MAISON.telephone2} · ${MAISON.email}`);
  l.push("", "## Pages", "");
  l.push(`- [Accueil et carte à commander](${SITE}/)`);
  l.push(`- [La carte complète et les prix](${SITE}/carte/) · en texte brut : [carte.md](${SITE}/carte.md)`);
  for (const c of CARTE) {
    const [b, h] = fourchette(c.items);
    l.push(`- [${RUBRIQUES[c.id].titre}](${SITE}${chemin(c)}) : ${c.items.length} plats, ${f(b)} à ${f(h)}`);
  }
  l.push(`- [Traiteur et place des fêtes](${SITE}/traiteur-et-place-des-fetes/)`);
  l.push(`- [Commander : sur place, à emporter, livraison](${SITE}/commander/)`);
  l.push(`- [Contact et infos pratiques](${SITE}/contact/)`);
  l.push("", "## Questions fréquentes", "");
  for (const { q, r } of faq()) l.push(`### ${q}`, "", r, "");
  return new Response(l.join("\n") + "\n", { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
