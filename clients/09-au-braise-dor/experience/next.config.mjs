/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cloudflare Pages sert des fichiers, pas un serveur Node : on exporte.
  output: "export",
  // ⚠️ Corollaire obligatoire : l'optimiseur d'images de Next a besoin d'un
  // serveur. Sans serveur, il faut le désactiver, et c'est donc à nous de
  // livrer des images déjà au bon poids.
  images: { unoptimized: true },
  trailingSlash: true,
};

export default nextConfig;
