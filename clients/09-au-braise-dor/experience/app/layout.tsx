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

export const metadata: Metadata = {
  title: "Au Braisé d'Or · Grillades au feu de bois · Cotonou",
  description:
    "Au Braisé d'Or, la maison de la braise à Cotonou : grillades au feu de bois, pizzas, chawarma, salades et cocktails. Commande en un geste sur WhatsApp.",
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
