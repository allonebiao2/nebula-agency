/**
 * LE PLAN DU DIMANCHE · la vidéo d'un proche, reprise en motion design.
 *
 * Face caméra de 3 min 29 : un formateur en trading explique qu'on ne réussit
 * pas sans planifier sa semaine AVANT qu'elle commence, d'abord avec l'argent
 * d'un salaire, puis au trading ; et il invite à sa communauté.
 *
 * La phrase qui tient tout : planifier, c'est ÉCRIRE SA SEMAINE LE DIMANCHE,
 * puis n'avoir plus qu'à l'exécuter.
 * L'objet : LA FEUILLE DE PLAN DU DIMANCHE. Un papier quadrillé, un stylo, un
 * surligneur. Chaque animation sort de cette feuille : la semaine qu'on range,
 * le budget qu'on découpe, le graphique qu'on annote, la case qu'on coche.
 *
 * ⚠️ Rien n'est inventé. Aucun chiffre de résultat : les courbes sont des
 * SCHÉMAS, sans axe ni valeur. Les seuls montants affichés sont ceux qu'il
 * prononce. Le texte vient de `mots.ts` (Whisper corrigé), jamais recopié.
 *
 * ⚠️ La source (576x1024, sous-titres CapCut incrustés) est préparée par
 * `_outils/dimanche_image.py` et `_outils/dimanche_son.py` dans
 * `public/dimanche/` : hors dépôt, c'est la vidéo d'un particulier.
 */
import {DEBUTS, FINS} from './mots';

export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;

/** Images de la source, et la carte de fin qui la prolonge. */
export const IMAGES_SOURCE = 6286;
export const DUREE_FIN = 105;
export const DUREE_TOTALE = IMAGES_SOURCE + DUREE_FIN;
export const DEBUT_FIN = 209.25;

/** Le début et la fin d'un mot, par son indice Whisper : les scènes s'y calent. */
export const d = (i: number) => DEBUTS[i];
export const fi = (i: number) => FINS[i];

/**
 * Les jetons. Jamais #000 ni #fff : une encre, un papier.
 * Le vert et le rouge sont ceux d'un graphique de bougies, et ne servent qu'à ça.
 */
export const C = {
	encre: '#10131a',
	encre2: '#1b2130',
	papier: '#f4efe4',
	papier2: '#e7dfcc',
	stylo: '#1c2b4b',
	surligneur: '#ffe14d',
	vert: '#18a864',
	vertClair: '#3fd68b',
	rouge: '#e0464b',
	gris: '#7b8190',
	blanc: '#fbf8f1',
	quadrillage: 'rgba(28,43,75,.09)',
} as const;

/**
 * La mise en page, mesurée sur la source agrandie (1080x1920) :
 * visage de 0 à ~440, anciens sous-titres (effacés) de 422 à 647, bureau et
 * tablette vides sous 1250. Les nouveaux sous-titres prennent la place des
 * anciens ; les graphiques vivent en bas. Marge TikTok : rien d'important à
 * droite de 940 ni sous 1660 (boutons et description de l'appli).
 */
export const ZONE = {
	sousTitres: 560,
	basHaut: 1150,
	basBas: 1640,
	gauche: 64,
	droite: 940,
} as const;

/** Les chapitres, affichés en haut à gauche. Le début est celui du premier mot. */
export const CHAPITRES = [
	{nom: 'Planifier', debut: 0},
	{nom: "L'argent", debut: d(87)},
	{nom: 'Le trader', debut: d(324)},
	{nom: 'La méthode', debut: d(435)},
	{nom: 'La communauté', debut: d(566)},
	{nom: 'Rejoindre', debut: d(677)},
] as const;

/**
 * Les poussées de caméra sur le visage : un mot fort, un zoom court.
 * [début en s, force]. La source est en 576 px : on ne dépasse pas ×1,12.
 */
export const POUSSEES: [number, number][] = [
	[0, 0.1],
	[d(62), 0.1],
	[d(82), 0.07],
	[d(168), 0.08],
	[d(323), 0.08],
	[d(348), 0.1],
	[d(564), 0.11],
	[d(726), 0.09],
	[d(781), 0.1],
	[d(799), 0.1],
];

/**
 * Les moments où la vidéo s'assombrit sous un grand graphique.
 * [début, fin, niveau]. Alternance voulue : clair, sombre, clair.
 */
export const OMBRES: [number, number, number][] = [
	[d(59) - 0.1, fi(63) + 0.5, 0.5],
	[d(348) - 0.2, d(386), 0.45],
	[d(435) - 0.2, d(566) - 0.1, 0.42],
	[d(711), d(782) - 0.2, 0.42],
	[d(796) - 0.2, d(826), 0.4],
];

/** Le nom de la communauté, tel que ses propres sous-titres l'écrivent. */
export const COMMUNAUTE = 'Trading pour tous';
