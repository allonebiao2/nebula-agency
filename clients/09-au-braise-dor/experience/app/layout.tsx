import type { Metadata, Viewport } from "next";
import { Montserrat, Inter } from "next/font/google";
import "./globals.css";

/**
 * Les deux polices demandées au brief : Montserrat pour les titres (300 pour la
 * ligne fine, 800 pour la ligne grasse) et Inter pour le texte courant.
 * ⚠️ Servies par `next/font` : elles sont téléchargées à la construction et
 * hébergées avec le site. Aucune requête ne part chez Google au chargement,
 * ce qui compte quand le visiteur est en 3G à Cotonou.
 */
const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["200", "300", "500", "800", "900"],
  variable: "--f-display",
  display: "swap",
});
const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--f-texte",
  display: "swap",
});

const SITE = "https://au-braise-dor.pages.dev";
const TITRE = "Au Braisé d'Or · Grillades au feu de bois · Cotonou";
const RESUME =
  "Au Braisé d'Or, la maison de la braise à Cotonou : grillades au feu de bois, sauces du pays, pizzas, chawarma, salades et cocktails. Commande en un geste sur WhatsApp.";

/**
 * ⚠️ `openGraph` N'EST PAS UN ORNEMENT. Au Bénin tout circule par WhatsApp :
 * sans image de partage, un lien envoyé dans une conversation n'est qu'une
 * ligne de texte grise, à côté de liens qui montrent une photo. C'est le
 * défaut le plus coûteux d'une vitrine, et il est invisible quand on la
 * regarde. L'image est en JPEG : l'aperçu WhatsApp ne lit pas toujours le WebP.
 */
export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: TITRE,
  description: RESUME,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "fr_FR",
    url: SITE,
    siteName: "Au Braisé d'Or",
    title: TITRE,
    description: RESUME,
    images: [
      {
        url: "/og.jpg",
        width: 1200,
        height: 630,
        alt: "Au Braisé d'Or · grillades au feu de bois à Cotonou",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: TITRE,
    description: RESUME,
    images: ["/og.jpg"],
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#EDE9E3",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${montserrat.variable} ${inter.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
