import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

/*
  Tout est compilé dans le bundle : aucune requête vers un CDN au chargement.

  ⚠️ POURQUOI LES FICHIERS PORTENT UNE MARQUE DE DÉPLOIEMENT
  Le 2026-08-04, le site est apparu ENTIÈREMENT SANS STYLE : texte noir sur
  blanc, police par défaut. La feuille de style répondait pourtant 200, avec le
  bon type et la bonne taille. Son contenu, lui, était « error code: 502 ».

  Ce qui s'était passé : pendant un déploiement, Cloudflare a reçu un 502
  passager de l'origine et l'a mis en cache À LA PLACE du fichier. Or nos
  fichiers portent `Cache-Control: immutable, max-age=31536000` : parfaitement
  correct pour un nom qui contient une empreinte de contenu, mais fatal ici,
  car l'erreur restait servie pendant un an.

  Et comme Vite nomme les fichiers d'après leur CONTENU, reconstruire à
  l'identique redonnait exactement les mêmes noms, donc les mêmes adresses
  empoisonnées. Le site ne pouvait pas se réparer tout seul.

  D'où cette marque de déploiement dans le nom : chaque publication produit des
  adresses neuves, et une erreur mise en cache ne survit plus à un déploiement.
  Le coût est un seul chargement de plus pour un visiteur déjà venu. C'est
  infiniment moins cher qu'un site casse qu'on ne peut pas reparer.
*/
const MARQUE = new Date()
  .toISOString()
  .replace(/[-:T]/g, '')
  .slice(2, 12) /* AAMMJJHHmm */

export default defineConfig({
  base: '/',
  plugins: [react(), tailwindcss()],
  build: {
    outDir: 'dist',
    assetsInlineLimit: 4096,
    target: 'es2020',
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name]-${MARQUE}-[hash].js`,
        chunkFileNames: `assets/[name]-${MARQUE}-[hash].js`,
        assetFileNames: `assets/[name]-${MARQUE}-[hash][extname]`,
      },
    },
  },
})
