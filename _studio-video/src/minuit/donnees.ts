/**
 * MINUIT · la démonstration du produit, en vidéo verticale.
 *
 * La phrase qui tient tout, reprise mot pour mot de `minuit/README.md` :
 * une lettre digitale, c'est une ENVELOPPE CACHETÉE qu'on ouvre à l'heure dite.
 * Le sceau, le pli, l'encre qui sèche. Chaque animation de cette vidéo sort de
 * cet objet, et d'aucun autre. Si un mouvement pourrait être collé dans la
 * vidéo d'un autre produit, il est à refaire.
 *
 * ⚠️ Rien n'est inventé ici. Les couleurs sont les jetons de
 * `minuit/lettre.html`, le texte de la lettre est celui de la démonstration du
 * produit (accentué, il ne l'était pas), et les prix sont ceux de
 * `minuit/creer.html`. Ce fichier est le SEUL endroit où ils sont recopiés :
 * si la charte du produit bouge, c'est le seul endroit à corriger.
 */

export const FPS = 30;
export const LARGEUR = 1080;
export const HAUTEUR = 1920;

/**
 * Les jetons de `minuit/lettre.html`.
 * Jamais #000 ni #fff en fond : une encre de nuit, un papier de lettre.
 */
export const C = {
	nuit: '#141019',
	nuit2: '#1d1826',
	papier: '#f4ede0',
	papier2: '#ebe0cd',
	encre: '#241d2b',
	cire: '#8c2f39',
	cireClair: '#b2434e',
	or: '#c9a227',
	orDoux: '#e0c266',
	gris: '#6d6478',
	pli: 'rgba(36,29,43,.12)',
} as const;

/**
 * ⚠️ Aucune police téléchargée, exactement comme dans le produit : la pile est
 * système, choisie et assumée. Iowan Old Style (Apple) et Palatino (Windows)
 * sont de vraies faces de correspondance, plus chaudes que Georgia. Le rendu
 * tourne sous Windows, donc c'est Palatino Linotype qui sort.
 * ⛔ Ne PAS rajouter Google Fonts : la vidéo doit ressembler à la lettre que
 * la destinataire ouvrira, pas à une version embellie pour la publicité.
 */
export const SERIF =
	'"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",Times,serif';
export const SANS =
	'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif';

/**
 * La courbe du produit, `--t: cubic-bezier(.25,1,.5,1)` dans `lettre.html`.
 * Elle est écrite en toutes lettres dans chaque plan, `Easing.bezier(.25,1,.5,1)`,
 * plutôt que rangée dans une constante : c'est la seule forme que le studio
 * sait rendre modifiable à la souris. Si elle change, elle change partout.
 */

/**
 * Le contenu de la lettre montrée. C'est la démonstration du produit, celle
 * des captures de `minuit/_vues/`, remise avec ses accents.
 *
 * Une ligne vide est un saut de paragraphe : elle ne compte pas dans le
 * séchage de l'encre, elle ouvre juste un blanc.
 */
export const LETTRE = {
	pour: 'Zara',
	initiale: 'R',
	occasion: 'Anniversaire',
	titre: 'Joyeux anniversaire',
	lignes: [
		'Je ne sais pas écrire les belles',
		'phrases, alors je vais écrire',
		'les vraies.',
		'',
		'Depuis que tu es là, les journées',
		"ordinaires ont cessé d'être",
		'ordinaires.',
		'',
		'Bon anniversaire. Je nous',
		'souhaite encore beaucoup de',
		'jours comme ceux-là.',
	],
	compte: 902,
	libelleCompte: 'jours ensemble',
	formule: 'Avec tout mon cœur,',
	signature: 'Robert',
} as const;

/**
 * Le rythme, en images. Une lettre ne se lit pas au rythme d'une publicité :
 * chaque plan doit laisser le temps de LIRE. Les durées restent écrites en
 * images plutôt qu'en secondes pour se retrouver telles quelles dans la
 * timeline du studio.
 */
export const DUREES = {
	seuil: 165, // 5,5 s · le cachet respire, puis se brise
	lettre: 255, // 8,5 s · le pli s'ouvre, l'encre sèche ligne après ligne
	compte: 90, // 3,0 s · les chiffres roulent
	signature: 90, // 3,0 s · le trait qui s'écrit
	heure: 180, // 6,0 s · l'heure dite, c'est le produit
	fin: 120, // 4,0 s · la carte, où le cachet se REFERME
} as const;

/**
 * ⛔ PAS DE FONDU ENCHAÎNÉ ENTRE LES PLANS, et ce n'est pas un raccourci.
 *
 * Les six plans posent tous leur contenu sur LE MÊME fond de nuit, et chacun
 * fait entrer et sortir ce contenu lui-même. Une coupe entre deux plans est
 * donc invisible : ce qui change, c'est ce qui est posé dessus, pas le fond.
 *
 * Un fondu enchaîné, lui, superpose les deux plans. Essayé, puis regardé sur
 * l'image 372 : la feuille de la lettre à 50 % et la carte du compte à 50 %
 * donnaient deux rectangles clairs décalés l'un sur l'autre, le « 332 » en
 * train de rouler par-dessus le texte de la lettre. Ça ne ressemble pas à une
 * transition, ça ressemble à une panne.
 *
 * Chaque plan garde donc son propre souffle d'entrée et de sortie, et le peu
 * de nuit qui les sépare est une respiration voulue : c'est le temps qu'on met
 * à descendre le regard le long d'une lettre.
 */

/** Durée totale du montage. Les plans se suivent, rien ne se recouvre. */
export const DUREE_TOTALE =
	DUREES.seuil +
	DUREES.lettre +
	DUREES.compte +
	DUREES.signature +
	DUREES.heure +
	DUREES.fin;
