/**
 * MA LETTRE À… · « Minuit pile, pour maman » (16:9, YouTube) · LES DONNÉES. ON ÉDITE ICI.
 *
 * Le minutage n'est PAS écrit à la main : il vient de `minutage.json`, écrit par
 * `_outils/malettre_minuit_son.py` à partir des voix de Mongazi. Une seule vérité pour l'image et le son :
 * on change une pause, on relance le script du son, et chaque plan suit.
 *
 * ⛔ Rien d'inventé. La lettre est une vraie lettre de la plume (fiche inventée, relue : aucun fait ajouté),
 *    les occasions sont les 28 du constructeur, les couleurs sont les jetons de `malettre/lettre.html`,
 *    le prix d'entrée est celui de La Carte (1 000 F).
 * ⛔ Aucun visage, aucun chiffre de vente, aucun avis. Les images d'ambiance sont celles de la vitrine,
 *    choisies par Mongazi (mains comprises : elles y sont déjà, en ligne).
 */
import {loadFont as caslonDisplay} from '@remotion/google-fonts/LibreCaslonDisplay';
import {loadFont as caslonText} from '@remotion/google-fonts/LibreCaslonText';
import {loadFont as pinyon} from '@remotion/google-fonts/PinyonScript';
import {loadFont as commissioner} from '@remotion/google-fonts/Commissioner';
import minutage from './minutage.json';

export const FPS = 60;
export const LARGEUR = 1920;
export const HAUTEUR = 1080;
export const M = minutage;
export const DUREE = minutage.duree;
export const MINUIT = minutage.minuit;
export const NARRATRICE = minutage.debutNarratrice;
export const MESURES = minutage.mesuresAfro;

/** Une phrase de la voix, par son identifiant (k1…k9 Koffi, a1…a22 Alimata). */
export const L = (id: string) => {
	const l = minutage.lignes.find((x) => x.id === id);
	if (!l) throw new Error('phrase inconnue : ' + id);
	return l;
};

export const TITRE = caslonDisplay('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const ITALIQUE = caslonText('italic', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const PLUME = pinyon('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const SANS = commissioner('normal', {weights: ['400', '500', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;

/** Les jetons de `malettre/lettre.html`. Jamais #000 ni #fff : une nuit, un papier. */
export const C = {
	nuit: '#141019',
	nuit2: '#1d1826',
	nuit3: '#0b0910',
	papier: '#f4ede0',
	papier2: '#ebe0cd',
	encre: '#241d2b',
	or: '#c9a227',
	orDoux: '#e0c266',
	orPale: '#f7e7b0',
	gris: '#5d5468',
	grisNuit: '#8f86a0',
	bougie: '#ffb36b',
} as const;

export const CIRES = {
	bordeaux: {cire: '#8c2f39', clair: '#b2434e', fonce: '#6d1f27', lumiere: '#e08a93'},
	or: {cire: '#b8892b', clair: '#e0b85a', fonce: '#7a5a14', lumiere: '#e0c266'},
	nuit: {cire: '#2b2433', clair: '#4a3f56', fonce: '#141019', lumiere: '#c4b9d4'},
	sapin: {cire: '#2f5d4a', clair: '#4f8a6f', fonce: '#1b3a2d', lumiere: '#8cc9ab'},
	rose: {cire: '#b25a72', clair: '#d88aa0', fonce: '#7e3a4e', lumiere: '#eaa9bb'},
} as const;
export type Cire = keyof typeof CIRES;

/** Les dessins du sceau, recopiés trait pour trait de `lettre.html` (viewBox 0 0 24 24). */
export const SCEAUX = {
	coeur: ['M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z'],
	colombe: [
		'M3.5 13.5c2.2.4 4.3-.2 6-1.8 1.6-1.6 2.3-3.9 4.4-4.8 1.6-.7 3.4-.4 4.6.6l-2.1.8c.5 1.9 0 3.9-1.5 5.4-1.9 1.9-4.7 2.7-7.3 2.4-1.5-.2-2.9-.8-4.1-1.7z',
		'M9.8 11.5C8.3 9.4 8 6.9 9.1 4.6c1.6 1.6 2.4 3.7 2.4 5.8',
		'M3.5 13.5 2 16.5l3-1.2',
	],
	couronne: ['M4 17 3 8l5 4 4-6 4 6 5-4-1 9z', 'M5 20h14'],
} as const;
export type Sceau = keyof typeof SCEAUX | 'initiale' | 'marque';

/** Les papiers de l'enveloppe (`lettre.html`). */
export const PAPIERS = {
	creme: {papier: '#f4ede0', papier2: '#ebe0cd'},
	coton: {papier: '#f7f1e6', papier2: '#ece3d3'},
	kraft: {papier: '#e6d3b3', papier2: '#d6bf98'},
	nuit: {papier: '#2a2333', papier2: '#211b29'},
} as const;
export type Papier = keyof typeof PAPIERS;

/** La lettre du film : Koffi, à Paris, pour les 60 ans de sa mère à Cotonou. Habillage de La Lettre. */
export const HABIT = {cire: 'bordeaux' as Cire, sceau: 'coeur' as Sceau, papier: 'creme' as Papier, initiale: 'K'};

/**
 * LA LETTRE, mot pour mot, telle que la vraie plume l'a écrite le 2026-10-22 (relue : rien d'ajouté).
 * Fiche : anniversaire, Maman, de Koffi, émouvant et chaleureux, sa force et sa patience, la santé, une longue vie,
 * la joie, courte ; souvenir « elle me réveillait à 5 h pour réviser le bac, avec un bol de bouillie chaude » ;
 * consigne « elle fête ses 60 ans, je vis à Paris, la lettre s'ouvre à minuit pile ».
 */
export const LETTRE = {
	occasion: 'Anniversaire',
	pour: 'Maman',
	de: 'Koffi',
	titre: 'Un bol de bouillie à 5 heures',
	paragraphes: [
		'Tu me réveillais à 5 h pour réviser le bac, avec un bol de bouillie chaude, et tu ne te plaignais jamais. J’y pense encore, et ça me serre le cœur de la plus belle façon.',
		'Ta force et ta patience m’ont porté bien plus loin que ces matins-là. Je suis à Paris, je ne serai pas à Cotonou pour tes 60 ans, mais je voulais être le premier à te le souhaiter, dès minuit. Je te souhaite la santé, une longue vie, et de la joie à chaque réveil.',
	],
	formule: 'Je t’embrasse très fort,',
	/** La phrase qui s'allume quand Koffi se tait (le cœur de la lettre). */
	phare: 'je voulais être le premier à te le souhaiter, dès minuit.',
	/** Ce que lit la voix de Koffi : la première phrase. */
	lue: 'Tu me réveillais à 5 h pour réviser le bac, avec un bol de bouillie chaude, et tu ne te plaignais jamais.',
	/** La phrase exacte du produit (`L.ouvre` + `libQuand()`). Le 15 novembre 2026 est un dimanche. */
	ouvre: ['Elle s’ouvre ', 'dimanche 15 novembre à minuit', '.'],
	attend: 'Une lettre t’attend.',
	heure: 'C’est l’heure.',
	briser: 'Briser le cachet',
};

/** Les 28 occasions du constructeur (`creer.html`), dans leur ordre. Le ciel du film les fait passer. */
export const OCCASIONS = [
	'Demande de couple', 'Mois de rencontre', 'Saint-Valentin', 'Anniversaire de couple', 'Demande en mariage',
	'Excuse', 'Rupture', 'Anniversaire', 'Fête des mères', 'Fête des pères', 'Naissance', 'Mariage', 'Amitié',
	'Soirée entre potes', 'Rupture d’amitié', 'Noël', 'Nouvel an', 'Tabaski', 'Fin du Ramadan', 'Pâques',
	'Réussite', 'Encouragement', 'Bon rétablissement', 'Nouveau travail', 'Départ à la retraite', 'Merci',
	'Une invitation', 'Autre occasion',
];

export const ADRESSE = 'malettre.nebula-agency.online';

/** Paris (48,86° N) → Cotonou (6,37° N), presque le même méridien : 42,5° de latitude, soit 4 720 km à vol d'oiseau. */
export const DISTANCE_KM = '4 720 km';
