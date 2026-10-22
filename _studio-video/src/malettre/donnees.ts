/**
 * MA LETTRE À… · LA PUBLICITÉ (30 s, et deux coupes de 15 s) · les données. ON ÉDITE ICI.
 *
 * La phrase qui tient tout, celle du produit : une lettre digitale, c'est une
 * ENVELOPPE CACHETÉE qu'on ouvre à l'heure dite. Chaque plan sort de cet objet :
 * le prénom qui s'écrit sur l'enveloppe, la cire qui dort, la cire qui s'allume,
 * le cachet qui se brise, la feuille qui se déplie.
 *
 * ⚠️ Rien n'est inventé.
 *   · Les couleurs sont les jetons de `malettre/lettre.html`, habillages compris
 *     (cire, sceau, papier) : les enveloppes de la pub portent l'habillage RÉEL
 *     de chaque lettre d'exemple.
 *   · Les lettres montrées sont les lettres d'exemple de `malettre/exemples.json`
 *     et `exemples.en.json`, écrites par la vraie plume le 2026-10-16 à partir de
 *     leurs fiches, puis relues. Les personnes sont inventées, et la vitrine le dit.
 *   · Les occasions portent leur nom exact dans le constructeur.
 * ⛔ Aucun chiffre inventé (pas de « 10 000 lettres »), aucun avis, aucun visage.
 * ⛔ La voix ne dit aucun prix sauf « cinq cents francs de plus » (coupe B), et
 *    c'est une phrase relue : la plume S'AJOUTE à l'offre, jamais « 500 F » seul.
 *
 * Les textes de la voix vivent dans `VOIX.md` (ce que Mongazi enregistre) ; ceux
 * qui s'écrivent à l'écran vivent ici. Ce sont les mêmes phrases, raccourcies pour
 * qu'on les lise sans le son : la moitié des statuts se regardent muets.
 */

export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;

/** L'adresse prévue (`malettre/CONTEXT.md`). ⛔ On ne publie pas la vidéo avant qu'elle réponde. */
export const ADRESSE = 'malettre.nebula-agency.online';

/** Les jetons de `malettre/lettre.html`. Jamais #000 ni #fff : une nuit, un papier. */
export const C = {
	nuit: '#141019',
	nuit2: '#1d1826',
	papier: '#f4ede0',
	papier2: '#ebe0cd',
	carteHaut: '#fbf7ef',
	encre: '#241d2b',
	or: '#c9a227',
	orDoux: '#e0c266',
	gris: '#5d5468',
	grisNuit: '#8f86a0',
	pli: 'rgba(36,29,43,.12)',
	/** Le vert de WhatsApp, et pour WhatsApp seulement. */
	whatsapp: '#25d366',
	bulle: '#1f2c26',
} as const;

/** Les cires de `lettre.html` (`.cire-or`, `.cire-rose`…). Bordeaux est la cire de base. */
export const CIRES = {
	bordeaux: {cire: '#8c2f39', clair: '#b2434e', fonce: '#6d1f27', lumiere: '#e08a93'},
	or: {cire: '#b8892b', clair: '#e0b85a', fonce: '#7a5a14', lumiere: '#e0c266'},
	nuit: {cire: '#2b2433', clair: '#4a3f56', fonce: '#141019', lumiere: '#c4b9d4'},
	sapin: {cire: '#2f5d4a', clair: '#4f8a6f', fonce: '#1b3a2d', lumiere: '#8cc9ab'},
	rose: {cire: '#b25a72', clair: '#d88aa0', fonce: '#7e3a4e', lumiere: '#eaa9bb'},
} as const;
export type Cire = keyof typeof CIRES;

/** Les papiers de l'enveloppe. Crème et coton ont la même teinte (le coton ajoute un grain). */
export const PAPIERS = {
	creme: {papier: C.papier, papier2: C.papier2, encre: C.encre},
	coton: {papier: C.papier, papier2: C.papier2, encre: C.encre},
	kraft: {papier: '#e6d3b3', papier2: '#d6bf98', encre: C.encre},
	nuit: {papier: '#2a2333', papier2: '#211b29', encre: C.papier},
} as const;
export type Papier = keyof typeof PAPIERS;

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

/** Un habillage, tel qu'il est écrit dans `exemples.json`. `initiale` = le sceau à l'initiale. */
export type Habillage = {cire: Cire; sceau: keyof typeof SCEAUX | 'initiale'; papier: Papier; initiale: string};

/**
 * ⚠️ Aucune police téléchargée, exactement comme dans le produit (même décision
 * que la démonstration `lepli-demo`) : la vidéo doit ressembler à la lettre que
 * l'on ouvrira, pas à une version embellie pour la publicité.
 */
export const SERIF =
	'"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",Times,serif';
export const SANS =
	'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif';

export type Langue = 'fr' | 'en';

/**
 * Les trois prénoms de l'accroche, et l'habillage RÉEL de leur lettre d'exemple
 * (`exemples.json` : papa, afi, maman).
 */
export const PRENOMS: {fr: string; en: string; habillage: Habillage}[] = [
	{fr: 'papa', en: 'Dad', habillage: {cire: 'or', sceau: 'couronne', papier: 'kraft', initiale: 'A'}},
	{fr: 'Afi', en: 'Afi', habillage: {cire: 'rose', sceau: 'coeur', papier: 'coton', initiale: 'K'}},
	{fr: 'maman', en: 'Mum', habillage: {cire: 'bordeaux', sceau: 'coeur', papier: 'coton', initiale: 'A'}},
];

/**
 * LA lettre qu'on suit d'un bout à l'autre : celle de Kofi à Afi, Saint-Valentin,
 * qui s'ouvre le 14 février à 00:00. C'est la seule des six à porter une heure
 * d'ouverture, et minuit est exactement ce que la voix promet.
 * Le texte est le premier paragraphe écrit par la plume, mot pour mot.
 */
export const HISTOIRE = {
	habillage: {cire: 'rose', sceau: 'coeur', papier: 'coton', initiale: 'K'} as Habillage,
	fr: {
		pour: 'Afi',
		de: 'Kofi',
		occasion: 'Saint-Valentin',
		titre: 'Pour toi, ma douce',
		/* La phrase exacte du produit : `L.ouvre` + `libQuand()`, « minuit se dit ». */
		ouvre: ["Elle s'ouvre ", 'dimanche 14 février à minuit', '.'],
		attend: "Une lettre t'attend.",
		heure: "C'est l'heure.",
		formule: "Je t'embrasse très fort,",
		paragraphe:
			"Ma douce, je commence par le bord de mer à Lomé, notre premier rendez-vous. L'orage est arrivé sans prévenir, on a couru se cacher sous la paillote d'un vendeur de coco. Moi, je ne regardais plus le ciel. Je te regardais rire sous la pluie.",
	},
	en: {
		pour: 'Afi',
		de: 'Kofi',
		occasion: "Valentine's Day",
		titre: 'Counting the days, my sweet',
		ouvre: ['It opens ', 'Sunday 14 February at midnight', '.'],
		attend: 'A letter is waiting for you.',
		heure: "It's time.",
		formule: 'Yours always,',
		/* La lettre anglaise n'est pas une traduction : la plume anglaise l'a écrite. */
		paragraphe:
			"Happy Valentine's Day, my sweet. I think of our first date by the sea in Lomé. The storm came out of nowhere, and we ran to hide under a coconut seller's straw hut. I remember laughing while the rain drummed on the straw, and thinking: I want more days like this one.",
	},
};

/**
 * Les quatre occasions de la fin, avec leur nom EXACT dans le constructeur
 * (`creer.html`, `en/creer.html`) et un habillage par enveloppe.
 */
export const OCCASIONS: {fr: string; en: string; habillage: Habillage}[] = [
	{fr: 'Anniversaire', en: 'Birthday', habillage: {cire: 'or', sceau: 'initiale', papier: 'creme', initiale: 'A'}},
	{fr: 'Demande en mariage', en: 'Marriage proposal', habillage: {cire: 'bordeaux', sceau: 'coeur', papier: 'coton', initiale: 'S'}},
	{fr: 'Excuse', en: 'Apology', habillage: {cire: 'nuit', sceau: 'initiale', papier: 'nuit', initiale: 'R'}},
	{fr: 'Tabaski', en: 'Tabaski', habillage: {cire: 'sapin', sceau: 'colombe', papier: 'creme', initiale: 'I'}},
];

/** Ce qui s'écrit à l'écran, par plan. Les mêmes phrases que la voix, en plus court. */
export const ECRAN = {
	fr: {
		accroche: 'Ma lettre à…',
		marque: 'Ma lettre à…',
		scellee: ['Scellée', "jusqu'à l'heure que tu choisis."],
		plume: ['Tes mots.', 'Ou la plume, à partir de tes souvenirs.'],
		pageBlanche: 'Tu ne sais pas quoi écrire ?',
		attente: ['Tu envoies le lien.', 'Le cachet attend.'],
		lienApercu: 'Une lettre t’attend.',
		heureDite: "À l'heure dite, la cire s'allume.",
		briser: 'Briser le cachet',
		prix: 'Dès 1 000 F',
		plumePrix: 'La plume : 500 F de plus',
		par: 'by NEBULA Agency',
		souvenir: 'Un souvenir que vous seuls connaissez',
	},
	en: {
		/* L'accroche se dit dans la langue de celui qui regarde ; la marque, jamais traduite. */
		accroche: 'My letter to…',
		marque: 'Ma lettre à…',
		scellee: ['Sealed', 'until the moment you choose.'],
		plume: ['Your words.', 'Or the Quill, from your memories.'],
		pageBlanche: "Don't know what to write?",
		attente: ['Send the link.', 'The seal waits.'],
		lienApercu: 'A letter is waiting for you.',
		heureDite: 'At the chosen hour, the wax lights up.',
		briser: 'Break the seal',
		prix: 'From 1,000 F',
		plumePrix: 'The Quill: 500 F extra',
		par: 'by NEBULA Agency',
		souvenir: 'A memory only the two of you share',
	},
} as const;
