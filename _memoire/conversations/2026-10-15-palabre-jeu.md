# 2026-10-14 / 15 · PALABRE, le jeu de cartes de la francophonie

## Le fil de la demande
1. « Tu es un expert en création de jeu vidéo… un jeu que tout utilisateur de TikTok apprécierait, addictif, en temps
   réel, joueur contre joueur, chacun sur son téléphone… où les gens pourront même mettre de l'argent » : cinq idées
   proposées (Awalé éclair, Le graphique, La guerre des lives, Quartiers, Le clash).
2. « Non, pas que TikTok, tout le monde… les références francophones, africaines, françaises… des cartes à jouer où on
   peut miser, de belles animations style Yu-Gi-Oh, des références et stickers drôles » : le concept PALABRE.
3. « Ultra simple, même un enfant… miser avec des gens partout dans le monde, jouer seul, jouer avec qui on veut,
   évoluer… ce truc qui pousse à dégainer son téléphone pour régler un conflit » : le triangle Costaud, Malin,
   Tchatcheur (le pierre-feuille-ciseaux du téléphone), l'enjeu et le verdict, le Tour, la Coupe des pays.
4. « Viral sur TikTok, hyper drôle en soirée, multijoueur, Yu-Gi-Oh et Clash Royale… les mèmes francophones, le for sure
   de Macron, 8 morts 6 blessés… » : premières recherches, la règle « la phrase, pas le visage », la soirée.
5. « Créer un dossier, Obsidian aussi à part : NEBULA AGENCY GAME, puis construire le jeu… graphisme parfait…
   cherche bien sur TikTok : Gabon, Côte d'Ivoire, Congo, France… » : fait.

## Ce qui est livré
- Dossier et coffre `C:\Users\USER\NEBULA AGENCY GAME` (git local, commit `9b52ff9`).
- Le jeu en ligne : https://palabre-4cn.pages.dev. Contrôles : 462 sur le moteur, 22 dans le navigateur contre le site
  en ligne (solo, duel à deux téléphones avec revanche, soirée à trois), 0 erreur.
- La recherche des mèmes par pays (six recherches puis un rapport), dans le coffre.

## Décisions et limites
- Pas de mise d'argent réel : les cauris sont un score. Au Bénin, loi n° 2002-28 et monopole de la LNB (presse) ;
  juriste obligatoire avant toute mise.
- Dessins vectoriels faits main : WaveSpeed à 0,04 $, Higgsfield à 0 crédit.
- Temps réel sur Supabase Realtime (projet partagé) : le jeton Cloudflare ne permet pas les Workers.
- Le mème « 8 morts, 6 blessés… ma libellule » : trouvé (particulier filmé à Meaux, 2020), laissé hors du jeu.
- Le coffre n'a pas pu être enregistré dans Obsidian depuis la ligne de commande : à ajouter une fois à la main.

Détail : `NEBULA AGENCY GAME/00 Accueil/REPRENDRE-ICI.md` et `04 Journal/2026-10-15.md`.
