/**
 * Les trois séries « oui / non » de NEBULA, telles qu'elles sont écrites dans
 * `_documents/nebula-agency/marketing/TIKTOK-OUI-NON.md`.
 *
 * Les cartes ne sont PAS redessinées ici : ce sont les PNG 1080x1920 écrits par
 * `_cartes.py`, importés tels quels. La carte `01` est la question 1, dans
 * l'ordre du document. Si une question change, on regénère la carte avec
 * `python _cartes.py`, on ne retouche pas l'image à la main.
 */

import s1_01 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-01.png';
import s1_02 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-02.png';
import s1_03 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-03.png';
import s1_04 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-04.png';
import s1_05 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-05.png';
import s1_06 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-06.png';
import s1_07 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-07.png';
import s1_08 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-08.png';
import s1_09 from '../../_documents/nebula-agency/marketing/tiktok/s1-prix-09.png';

import s2_01 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-01.png';
import s2_02 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-02.png';
import s2_03 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-03.png';
import s2_04 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-04.png';
import s2_05 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-05.png';
import s2_06 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-06.png';
import s2_07 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-07.png';
import s2_08 from '../../_documents/nebula-agency/marketing/tiktok/s2-besoin-08.png';

import s3_01 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-01.png';
import s3_02 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-02.png';
import s3_03 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-03.png';
import s3_04 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-04.png';
import s3_05 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-05.png';
import s3_06 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-06.png';
import s3_07 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-07.png';
import s3_08 from '../../_documents/nebula-agency/marketing/tiktok/s3-logiciel-08.png';

import fin from '../../_documents/nebula-agency/marketing/tiktok/z-fin.png';

export const CARTE_FIN = fin;

export type Reponse = 'OUI' | 'NON';

export type Question = {
	/** Le PNG de la question, 1080x1920. */
	carte: string;
	reponse: Reponse;
	/**
	 * Le plan filmé qui porte la réponse, relatif à `public/`
	 * (exemple : `visages/non-3.mp4`). Tant qu'il vaut `null`, la réponse
	 * s'affiche en carte texte et la vidéo se rend quand même.
	 */
	plan: string | null;
};

export type Serie = {
	/** Sert d'identifiant de composition ET de nom de fichier rendu. */
	id: string;
	titre: string;
	questions: Question[];
};

/**
 * Le rythme, repris du document : la question tient 1,2 à 1,8 s, le visage 0,8
 * à 1,2 s, et le visage doit rester PLUS COURT que la question. On prend le
 * milieu de chaque fourchette. Coupe sèche : aucune transition, c'est le format.
 */
export const FPS = 30;
export const IMAGES_QUESTION = 45; // 1,5 s
export const IMAGES_REPONSE = 30; // 1,0 s
export const IMAGES_FIN = 90; // 3,0 s sur la carte NEBULA

export const SERIES: Serie[] = [
	{
		id: 'oui-non-1-prix',
		titre: 'Script 1 · le prix',
		questions: [
			{carte: s1_01, reponse: 'NON', plan: null},
			{carte: s1_02, reponse: 'NON', plan: null},
			{carte: s1_03, reponse: 'NON', plan: null},
			{carte: s1_04, reponse: 'OUI', plan: null},
			{carte: s1_05, reponse: 'NON', plan: null},
			{carte: s1_06, reponse: 'OUI', plan: null},
			{carte: s1_07, reponse: 'OUI', plan: null},
			{carte: s1_08, reponse: 'OUI', plan: null},
			{carte: s1_09, reponse: 'OUI', plan: null},
		],
	},
	{
		id: 'oui-non-2-besoin',
		titre: 'Script 2 · « je n\'ai pas besoin de site »',
		questions: [
			{carte: s2_01, reponse: 'NON', plan: null},
			{carte: s2_02, reponse: 'NON', plan: null},
			{carte: s2_03, reponse: 'NON', plan: null},
			{carte: s2_04, reponse: 'OUI', plan: null},
			{carte: s2_05, reponse: 'OUI', plan: null},
			{carte: s2_06, reponse: 'OUI', plan: null},
			{carte: s2_07, reponse: 'OUI', plan: null},
			{carte: s2_08, reponse: 'OUI', plan: null},
		],
	},
	{
		id: 'oui-non-3-logiciel',
		titre: 'Script 3 · le logiciel métier',
		questions: [
			{carte: s3_01, reponse: 'OUI', plan: null},
			{carte: s3_02, reponse: 'NON', plan: null},
			{carte: s3_03, reponse: 'OUI', plan: null},
			{carte: s3_04, reponse: 'NON', plan: null},
			{carte: s3_05, reponse: 'OUI', plan: null},
			{carte: s3_06, reponse: 'NON', plan: null},
			{carte: s3_07, reponse: 'OUI', plan: null},
			{carte: s3_08, reponse: 'NON', plan: null},
		],
	},
];

/** Durée totale d'une série, carte de fin comprise. */
export const dureeDeLaSerie = (serie: Serie): number =>
	serie.questions.length * (IMAGES_QUESTION + IMAGES_REPONSE) + IMAGES_FIN;
