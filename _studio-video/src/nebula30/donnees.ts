/**
 * NEBULA · LA VIDÉO DE MARQUE (30 s, 9:16) · les données. ON ÉDITE ICI.
 *
 * La phrase qui tient tout : une nébuleuse, c'est de la POUSSIÈRE QUI DEVIENT
 * DES ÉTOILES. L'objet : la poussière d'étoiles. Chaque plan en sort : elle
 * explose, tourne en galaxie, dessine un téléphone, tourne en orbite autour d'un
 * catalogue, puis revient s'effondrer dans l'étoile du logo.
 *
 * Le film est un TOUR DE MAGIE en trois temps :
 *   1. la promesse : « Regardez bien. Tout ce que vous allez voir… » ;
 *   2. les trois tours : la vitrine, le catalogue, l'outil ;
 *   3. la révélation : « Et même… cette vidéo. » On recule, et l'on découvre
 *      qu'on était dans un logiciel de montage. « La vôtre est la prochaine. »
 *
 * ⚠️ Rien n'est inventé. Les sites sont les vrais, photographiés en ligne
 * (`_outils/nebula30_captures.py`) ; les produits et leurs prix sont ceux des
 * catalogues livrés (Weinkeller by CK, Hillary M. Styl, Au Braisé d'Or). Le
 * tableau de bord de l'outil porte la mention DÉMO : ses chiffres sont un
 * exemple, jamais un résultat.
 * ⚠️ La voix ne dit aucun chiffre : prix, délai et numéros vivent à l'écran.
 * Un prix change → on refait l'image, pas la voix.
 */
import {MOTS, MUSIQUE, REPLIQUES} from './minutage';

export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;
export const DUREE = 30 * FPS;

/**
 * La marge du mélange : Remotion additionne les sons sans limiteur. On garde 2,5 dB
 * de réserve pour que la somme ne sature jamais ; `_outils/nebula30_master.py` pose
 * ensuite le niveau final (−14 LUFS) et le limiteur, sur le son rendu.
 */
export const MIX = 0.75;

/**
 * Les jetons, lus sur le logo (galaxie et wordmark). Jamais #000 ni #fff : une
 * encre d'espace, une lumière d'étoile. Le vert est celui de WhatsApp et ne sert
 * qu'à WhatsApp.
 */
export const C = {
	encre: '#05040e',
	nuit: '#0b0a22',
	nuit2: '#16123e',
	indigo: '#1e1872',
	bleu: '#2f6bff',
	bleuClair: '#62a8ff',
	cyan: '#a8ecff',
	violet: '#6b3ff2',
	mauve: '#b689ff',
	lavande: '#efeaff',
	etoile: '#f7f5ff',
	gris: '#9d98c9',
	grisFonce: '#5d5a86',
	vertWa: '#25d366',
	bleuLu: '#53bdeb',
	verre: 'rgba(160,170,255,.07)',
	bord: 'rgba(190,200,255,.18)',
} as const;

/** Le dégradé du wordmark NEBULA, mesuré : cyan clair en haut, violet en bas. */
export const DEGRADE = 'linear-gradient(180deg, #d6f6ff 0%, #8fd0ff 30%, #5b8cf0 62%, #6a4ff0 100%)';
export const DEGRADE_TRAVERS = 'linear-gradient(100deg, #a8ecff 0%, #62a8ff 40%, #8a5cff 75%, #b689ff 100%)';

export type Registre = 'vous' | 'tu';

/**
 * Ce que la voix dit, et que l'écran écrit. Deux registres : on vouvoie partout,
 * sauf sur TikTok où l'on tutoie (règle de la marque).
 */
export const TEXTES = {
	vous: {
		regardez: 'Regardez bien.',
		toutCe: 'Tout ce que vous allez voir…',
		cree: 'le crée',
		pour: 'pour votre business.',
		devenez: 'et vous devenez',
		marque: 'une marque.',
		commandes: 'et les commandes arrivent sur WhatsApp.',
		pensePour: 'pensé pour',
		metier: 'VOTRE MÉTIER.',
		etMeme: 'Et même…',
		cetteVideo: 'cette vidéo.',
		votre: 'La vôtre est la prochaine.',
		votreClip: 'VOTRE VIDÉO',
		ecrivez: 'Écrivez-nous sur WhatsApp.',
		message: 'Bonjour NEBULA, je veux la mienne !',
		etoiles: 'Là où naissent les étoiles.',
	},
	tu: {
		regardez: 'Regarde bien.',
		toutCe: 'Tout ce que tu vas voir…',
		cree: 'le crée',
		pour: 'pour ton business.',
		devenez: 'et tu deviens',
		marque: 'une marque.',
		commandes: 'et les commandes arrivent sur WhatsApp.',
		pensePour: 'pensé pour',
		metier: 'TON MÉTIER.',
		etMeme: 'Et même…',
		cetteVideo: 'cette vidéo.',
		votre: 'La tienne est la prochaine.',
		votreClip: 'TA VIDÉO',
		ecrivez: 'Écris-nous sur WhatsApp.',
		message: 'Salut NEBULA, je veux la mienne !',
		etoiles: 'Là où naissent les étoiles.',
	},
} as const;

/**
 * LES RÉPLIQUES de la voix off : [début, fin] en secondes DU FILM, et les instants
 * musicaux (120 BPM). Rien n'est recopié ici : `_outils/nebula30_son.py` les MESURE
 * sur la prise et les écrit dans `minutage.ts`.
 */
export const R = REPLIQUES;
export type Replique = keyof typeof REPLIQUES;

/**
 * Le départ du k-ième mot d'une réplique, lu sur la voix. Whisper coupe
 * « Écrivez-nous » en deux jetons : un jeton qui commence par « - » se recolle
 * au précédent, pour que les mots comptés soient ceux du texte affiché.
 */
export const motsDe = (replique: Replique) => {
	const mots: {mot: string; debut: number; fin: number}[] = [];
	for (const m of MOTS) {
		if (m.replique !== replique) continue;
		if (m.mot.startsWith('-') && mots.length) {
			mots[mots.length - 1].mot += m.mot;
			mots[mots.length - 1].fin = m.fin;
		} else mots.push({mot: m.mot, debut: m.debut, fin: m.fin});
	}
	return mots;
};
export const instants = (replique: Replique) => motsDe(replique).map((m) => m.debut);
export const mot = (replique: Replique, k: number) => {
	const ms = motsDe(replique);
	return ms[Math.min(k, ms.length - 1)].debut;
};

/** Les instants du film, tirés de la voix et de la musique (jamais écrits en dur ailleurs). */
export const T = {
	bang: MUSIQUE.bang,
	versTel: R.vitrine[0] - 0.45,
	vitrine: R.vitrine[0] - 0.2,
	revele: R.marque[0] - 0.2,
	eventail: R.marque[0],
	catalogue: R.catalogue[0] - 0.3,
	tap: R.commandes[0],
	outil: R.outil[0] - 0.35,
	peaux: mot('outil', 3),
	fige: MUSIQUE.fige,
	recul: R.etMeme[1] + 0.05,
	rembobine: R.cetteVideo[0],
	votre: R.votre[0] - 0.15,
	chute: MUSIQUE.chute,
	implosion: MUSIQUE.hit - 0.8,
	hit: MUSIQUE.hit,
	contacts: R.etoiles[1] - 0.3,
} as const;

/** Les vrais sites (photographiés par `_outils/nebula30_captures.py`). */
export const SITES = {
	vitrine: 'angy-art',
	eventail: ['hillary', 'djambar', 'luxury-club', 'hh-design'],
	catalogue: 'braise-dor',
	tous: ['angy-art', 'braise-dor', 'hillary', 'weinkeller', 'djambar', 'luxury-club', 'grain', 'miss-cakes', 'hh-design'],
} as const;

export const NOMS_SITES: Record<string, string> = {
	'angy-art': 'Angy Art',
	'braise-dor': "Au Braisé d'Or",
	hillary: 'Hillary M. Styl',
	weinkeller: 'Weinkeller by CK',
	djambar: 'Djambar Team',
	'luxury-club': 'Luxury Club 229',
	grain: "Grain d'Esthétique",
	'miss-cakes': 'Miss cakes',
	'hh-design': 'HH Design',
};

/** Les produits en orbite autour du catalogue : vrais articles, vrais prix (FCFA). */
export const PRODUITS = [
	{img: 'vin-ruinart-blanc-de-blancs.webp', nom: 'Ruinart Blanc de Blancs', prix: 80000},
	{img: 'hms-piece-ceremonie.webp', nom: 'Robe de cérémonie', prix: 100000},
	{img: 'vin-moet-ice.webp', nom: 'Moët Ice Impérial', prix: 55000},
	{img: 'hms-piece-sirene.webp', nom: 'Robe Sirène', prix: 40000},
	{img: 'vin-dom-perignon-2015.webp', nom: 'Dom Pérignon 2015', prix: 220000},
	{img: 'hms-piece-josy.webp', nom: 'Ensemble JOSY', prix: 65000},
	{img: 'vin-veuve-clicquot.webp', nom: 'Veuve Clicquot Brut', prix: 60000},
	{img: 'hms-piece-coeurs.webp', nom: 'Tailleur Cœurs', prix: 50000},
] as const;

/** Les commandes qui arrivent : un article réel de trois catalogues livrés. */
export const COMMANDES = [
	{maison: 'Weinkeller by CK', article: 'Ruinart Blanc de Blancs', prix: 80000, img: 'vin-ruinart-blanc-de-blancs.webp'},
	{maison: 'Hillary M. Styl', article: 'Robe de cérémonie', prix: 100000, img: 'hms-piece-ceremonie.webp'},
	{maison: "Au Braisé d'Or", article: 'Poulet bicyclette', prix: 3000, img: null},
] as const;

/** Ce que l'écran affiche, et que la voix ne dit pas. */
export const FAITS = {
	prixEntree: 50000,
	delai: 'En ligne en 5 à 7 jours',
	whatsapp: '+229 96 74 07 32',
	appel: '+229 01 96 74 07 32',
	site: 'nebula-agency.online',
	services: ['Vitrines', 'Catalogues', 'Outils', 'Vidéos'],
	ville: 'Cotonou',
} as const;

/**
 * La pose du logo final dans l'image (le logo agrandi x2 est réduit de K) :
 * tout le bloc tient au-dessus des 480 px du bas, que TikTok recouvre.
 */
export const LOGO = {k: 0.6, haut: 455} as const;

/** Le cœur de la galaxie (et l'étoile du début) : là où tout naît. */
export const CENTRE = {x: 540, y: 880} as const;

/** La galaxie de l'explosion : l'ovale incliné du logo. */
export const GALAXIE = {a: 450, b: 170, inclinaison: -13} as const;

/** Le téléphone des trois tours : il ne change pas de place de la vitrine à l'outil. */
export const TEL = {x: 540, y: 1080, l: 500, h: 1030, r: 76} as const;

/** L'orbite des produits autour du catalogue, inclinée comme les anneaux du logo. */
export const ORBITE = {x: 540, y: 1235, a: 500, b: 190, inclinaison: -8} as const;
