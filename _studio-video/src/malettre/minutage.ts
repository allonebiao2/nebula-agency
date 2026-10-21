/**
 * MA LETTRE À… · le minutage des six versions (secondes, temps du film).
 *
 * ⏳ PROVISOIRE, écrit à la main d'après le tableau de `VOIX.md` : la voix n'est
 * pas encore enregistrée. Quand les six MP3 seront posés dans
 * `_partage/ma lettre/voix/`, on cale l'image sur la voix (et pas l'inverse) :
 * chaque plan commence sur la phrase qui le porte, et les `temps` (les instants
 * internes : un prénom, une occasion, la cire qui s'allume) tombent sur leur mot.
 * `voix` passe alors du `null` au fichier de `public/malettre/`.
 *
 * Un plan ne connaît que son début et sa fin : il étire ses gestes sur la durée
 * qu'on lui donne, donc caler la voix ne demande de toucher à aucune scène.
 */
import type {Langue} from './donnees';

export type PlanId =
	| 'accroche'
	| 'scellee'
	| 'pageBlanche'
	| 'plume'
	| 'attente'
	| 'ouverture'
	| 'occasions'
	| 'marque';

export type Plan = {id: PlanId; debut: number; fin: number; temps?: number[]};

export type Version = {
	langue: Langue;
	duree: number;
	/** `public/malettre/<fichier>` une fois la voix posée, sinon null. */
	voix: string | null;
	/** La fin de la coupe B dit le prix de la plume ; les autres disent « gratuite ». */
	fin: 'gratuite' | 'plume';
	plans: Plan[];
};

const TRENTE = (langue: Langue): Version => ({
	langue,
	duree: 30,
	voix: null,
	fin: 'gratuite',
	plans: [
		/* « Ma lettre à… papa. À Afi. À maman. » : un instant par prénom. */
		{id: 'accroche', debut: 0, fin: 3.4, temps: [1.0, 1.9, 2.7]},
		{id: 'scellee', debut: 3.4, fin: 7.2},
		/* « Tu l'écris avec tes mots. » puis « Ou la plume… » */
		{id: 'plume', debut: 7.2, fin: 12.2, temps: [9.0]},
		/* « Tu envoies le lien. » puis « Le cachet attend… » */
		{id: 'attente', debut: 12.2, fin: 17.2, temps: [14.0]},
		/* « À l'heure dite, la cire s'allume. » puis « On brise le cachet… » */
		{id: 'ouverture', debut: 17.2, fin: 23.2, temps: [17.8, 19.6]},
		/* « Un anniversaire, une demande, un pardon, une fête. » */
		{id: 'occasions', debut: 23.2, fin: 27.2, temps: [23.5, 24.4, 25.3, 26.1]},
		{id: 'marque', debut: 27.2, fin: 30},
	],
});

const LETTRE15 = (langue: Langue): Version => ({
	langue,
	duree: 15,
	voix: null,
	fin: 'gratuite',
	plans: [
		{id: 'accroche', debut: 0, fin: 3.4, temps: [1.0, 1.9, 2.7]},
		{id: 'scellee', debut: 3.4, fin: 7.2},
		/* Cinq secondes pour s'ouvrir ET se lire : le brisement vient tôt. */
		{id: 'ouverture', debut: 7.2, fin: 12.2, temps: [7.5, 8.6]},
		{id: 'marque', debut: 12.2, fin: 15},
	],
});

const PLUME15 = (langue: Langue): Version => ({
	langue,
	duree: 15,
	voix: null,
	fin: 'plume',
	plans: [
		{id: 'pageBlanche', debut: 0, fin: 2.4},
		/* Pas de « moi » ici : la coupe B entre directement par la plume. */
		{id: 'plume', debut: 2.4, fin: 8.4},
		{id: 'scellee', debut: 8.4, fin: 12.2},
		{id: 'marque', debut: 12.2, fin: 15},
	],
});

/** Les six versions, sous le nom de leur MP3 dans `VOIX.md`. */
export const VERSIONS = {
	'fr-30': TRENTE('fr'),
	'en-30': TRENTE('en'),
	'fr-15-lettre': LETTRE15('fr'),
	'fr-15-plume': PLUME15('fr'),
	'en-15-letter': LETTRE15('en'),
	'en-15-quill': PLUME15('en'),
} as const satisfies Record<string, Version>;

export type VersionId = keyof typeof VERSIONS;
