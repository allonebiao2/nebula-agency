/**
 * TIKTOK DU 20/11/2026 · les deux posts du jour en vidéo (28 s, 9:16). ON ÉDITE ICI.
 *
 * Décision de Mongazi : le TikTok de ce soir, ce sont les deux statuts du jour,
 * animés, SANS sa voix. Le texte à l'écran porte tout, les bruitages le rythme.
 *   1. l'accroche (0 → 2,3 s) : « C'est combien ? », pas de réponse, il est parti ;
 *   2. le conseil (statut de 13 h) : la photo, le prix, comment commander ;
 *   3. la leçon (statut de 17 h) : le PDF de 50 Mo contre le lien léger ;
 *   4. la fin : NEBULA, « Écris-nous sur WhatsApp ».
 *
 * ⚠️ TikTok tutoie (règle de la marque) : les statuts disent « votre client »,
 * la vidéo dit « ton client ».
 * ⚠️ Le téléphone du statut de 13 h (prix illisibles « 100.00 », image générée)
 * n'est PAS repris : il est redessiné ici, net, avec un exemple en francs. La
 * carte montrée est un dessin d'exemple, jamais le catalogue d'un client.
 * ⚠️ Le seul fond généré repris est celui du statut de 17 h (le rocher et le
 * téléphone), une ambiance déjà publiée, posé dans `public/tiktok-20-11/` (hors dépôt).
 * ⚠️ Rien de privé ici : le numéro est celui du site public de NEBULA.
 */
export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;
export const DUREE_S = 28;
export const DUREE = DUREE_S * FPS;

/** Remotion additionne les sons sans limiteur : on garde de la réserve. */
export const MIX = 0.8;

/** Les jetons des statuts (`nebula-apercus/statuts/composer.py`) : encre d'espace, cyan, dégradé violet → cyan. */
export const C = {
	encre: '#060713',
	nuit: '#0f1027',
	violet: '#9333ea',
	bleu: '#4f6fff',
	cyan: '#22d3ee',
	lavande: '#c9d2ff',
	pervenche: '#9aa6ff',
	lumiere: '#f4f5ff',
	gris: '#8e93b8',
	rouge: '#ff5c7a',
	vertWa: '#25d366',
	vertFonce: '#128c4a',
	bulle: '#202c33',
	bulleTexte: '#e9edef',
	bulleHeure: '#8696a0',
	papier: '#f4f5ff',
	papierTrait: '#dfe1ef',
	encreEcran: '#14163a',
	prix: '#3b4fe0',
	or: '#ffd27a',
} as const;

export const DEGRADE = `linear-gradient(100deg, ${C.violet}, ${C.bleu} 60%, ${C.cyan})`;

/** Le numéro du site public nebula-agency.online (wa.me/22996740732). */
export const NUMERO = '01 96 74 07 32';

/** Le prix de la carte d'exemple : un dessin, pas le produit d'un client. */
export const PRIX_EXEMPLE = 15000;

/** Les instants, en secondes. Chaque animation et chaque bruitage lit CES valeurs. */
export const T = {
	// 1 · l'accroche
	bulle: 0.08,
	attente: 0.45,
	parti: 1.15,
	// 2 · le conseil
	conseil: 2.3,
	trois: 3.5,
	choses: 3.75,
	liste: 4.6,
	photo: 5.05,
	prix: 6.55,
	commander: 8.05,
	tap: 8.45,
	sinon: 9.45,
	nuit: 11.5,
	// 3 · la leçon
	lecon: 12.9,
	chute: 13.7,
	mo: 14.15,
	reseau: 15.3,
	ailleurs: 17.7,
	lourd: 18.9,
	leger: 20.5,
	plongee: 21.9,
	// 4 · la fin
	offre: 22.3,
	logo: 23.7,
	whatsapp: 25.0,
	tapWa: 26.0,
} as const;

/** Le centre du téléphone dans le fond « lourd / léger » (image 1088 x 1920, recadrée à 1080). */
export const TEL_FOND = {x: 824, y: 925};
