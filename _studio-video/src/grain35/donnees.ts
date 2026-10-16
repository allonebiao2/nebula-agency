/**
 * GRAIN D'ESTHÉTIQUE · LA PUBLICITÉ DE 35 s (9:16) · les données. ON ÉDITE ICI.
 *
 * Le but est unique : que celle qui regarde ÉCRIVE « RDV » sur WhatsApp.
 *
 * La phrase qui tient tout, reprise de l'affiche de l'institut : un institut comme
 * celui-ci, c'est UN GRAIN DE PEAU QU'ON RÉVÈLE. L'objet : le grain. Il est d'or,
 * il dérive sur les bords de l'image et laisse le centre libre, il balaie une
 * scène pour révéler la suivante (comme un gommage révèle la peau), et c'est LUI
 * qui tombe en dernier sur le logo : le point rond du « i » de « Grain ».
 * Et la marque est un ŒIL : il s'ouvre au début, et la caméra plonge dans sa
 * pupille pour entrer dans l'institut.
 *
 * ⚠️ Rien n'est inventé. Prix, numéro, horaires, maisons partenaires, compteurs et
 * devise sont LUS dans la vitrine (`faits.ts`, écrit par _outils/grain35_faits.py).
 * La seule photo est la sienne. Les avis Google sont recopiés mot pour mot des
 * captures de Mongazi, jamais écrits par nous.
 * ⚠️ La voix ne dit aucun chiffre : prix, numéro et horaires vivent à l'écran.
 */
export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;
export const DUREE = 35 * FPS;

/** Remotion additionne les sons sans limiteur : 2,5 dB de réserve (comme NEBULA). */
export const MIX = 0.75;

/**
 * Les jetons de SA vitrine : rose #C4648A, or #D4AF72, encre #1A0E14. Jamais #000
 * ni #fff : une encre prune, un papier crème. Le vert est celui de WhatsApp et ne
 * sert qu'à WhatsApp.
 */
export const C = {
	encre: '#1a0e14',
	prune: '#2a1420',
	prune2: '#3c1c2c',
	rose: '#c4648a',
	roseClair: '#e7a8c0',
	rosePale: '#f6dfe8',
	or: '#d4af72',
	orClair: '#f3dcab',
	orFonce: '#9c763a',
	creme: '#fbf4ee',
	papier: '#f6ece6',
	gris: '#b9a3ad',
	vertWa: '#25d366',
	vertWaFonce: '#075e54',
	fondWa: '#efe7de',
	bulleWa: '#d9fdd3',
	bleuLu: '#53bdeb',
} as const;

/** L'or du logo : lumière en haut, bronze en bas (comme une feuille d'or posée). */
export const OR_DEGRADE = 'linear-gradient(170deg, #fff2cf 0%, #f0d49a 28%, #d4af72 55%, #a8803f 100%)';

/**
 * Ce que dit la voix, réplique par réplique (les textes animés le reprennent).
 * ⚠️ « rendez-vous » et non « RDV » : ElevenLabs a développé l'abréviation dans la
 * prise (Whisper l'entend « rendez-vous » à 0,99). L'écran dit ce que dit la voix.
 */
export const VOIX = {
	occupe: 'Vous vous occupez de tout le monde…',
	quiVous: "Mais qui s'occupe de vous ?",
	chez: "Chez Grain d'Esthétique,",
	premier: 'vous passez enfin en premier.',
	maisons: 'Des soins signés Sothys Paris et Sultane de Saba.',
	visage: "Un visage qui s'illumine.",
	corps: 'Un corps qui respire.',
	levres: 'Et des lèvres repulpées…',
	piqure: 'sans une seule piqûre.',
	tour: "C'est votre tour :",
	ecrivez: 'écrivez « rendez-vous » sur WhatsApp.',
	nom: "Grain d'Esthétique.",
	devise: 'La beauté est un art de vivre.',
} as const;
export type Replique = keyof typeof VOIX;

/**
 * Ce que porte une journée, pour l'accroche : les mots s'empilent jusqu'à saturer
 * l'écran, puis le grain les balaie et il ne reste que « vous ».
 */
export const FARDEAU = [
	'les enfants',
	'le travail',
	'la maison',
	'la famille',
	'les courses',
	'les factures',
	'les clients',
	'le dîner',
	'les devoirs',
	'les rendez-vous des autres',
] as const;

/**
 * LES AVIS GOOGLE, relevés MOT POUR MOT sur les 7 captures de sa fiche Google que
 * Mongazi a déposées dans _partage le 2026-10-03 (« Capture d'écran 2026-10-03
 * 111020 » à « 111453 »). Tous à 5 étoiles. Seuls changements : des extraits
 * marqués « … », et les accents rétablis (« agreable », « a cotonou »). Jamais un
 * mot ajouté. Le nom : prénom + initiale, comme on cite une cliente.
 * ⚠️ Aucune NOTE MOYENNE n'est affichée : un avis de la fiche est à 4 étoiles
 * (Michelle Ange H.), la moyenne n'est donc peut-être pas 5,0 quoi qu'en dise le
 * « 5★ » de la vitrine. On montre les étoiles de chaque avis cité, rien d'autre.
 */
export const AVIS_PHARE = {texte: 'Les meilleurs à Cotonou !', prenom: 'Neilath P.'};
export const AVIS: {texte: string; prenom: string}[] = [
	{texte: 'Un havre de paix.', prenom: 'Patrick V.'},
	{texte: 'Cette petite pépite… des doigts de fée.', prenom: 'Wijdane'},
	{texte: 'Super accueil ! Un massage relaxant comme j’aime.', prenom: 'Séverine C.'},
	{texte: 'Très bon accueil de Jocelyne et de son équipe.', prenom: 'Caroline P.'},
	{texte: 'Le personnel est au petit soin et attentionné.', prenom: 'Mirella K.'},
	{texte: 'Vraiment impeccable et excellent.', prenom: 'Mercia Z.'},
];
