import type { MetadataRoute } from "next";
import { CARTE } from "@/data/carte";
import { SITE, chemin } from "@/data/maison";

/* Le sitemap est BÂTI sur la carte : une rubrique ajoutée y entre toute seule.
   Il remplace `public/sitemap.xml`, qui ne connaissait que l'accueil. */
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const maj = new Date();
  const page = (p: string, priority: number, changeFrequency: "weekly" | "monthly") => ({
    url: `${SITE}${p}`, lastModified: maj, changeFrequency, priority,
  });
  return [
    page("/", 1.0, "weekly"),
    page("/carte/", 0.9, "weekly"),
    ...CARTE.map((c) => page(chemin(c), 0.8, "weekly")),
    page("/traiteur-et-place-des-fetes/", 0.7, "monthly"),
    page("/commander/", 0.6, "monthly"),
    page("/contact/", 0.6, "monthly"),
  ];
}
