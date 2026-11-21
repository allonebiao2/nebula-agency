/**
 * PUB ÉCRAN NEBULA · « écran filmé, motion design » (21/11/2026), d'après les deux références décortiquées dans
 * `references/PUB-ECRAN-MOTION.md` (la barre de qualité : B, un seul élément par phrase sur la nuit, un halo qui
 * respire, une seule couleur forte).
 *
 * ⚠️ AUCUN TEMPS N'EST ÉCRIT À LA MAIN. Tout vient de `minutage.json`, écrit par `_outils/caler_voix.py` sur la voix
 *    de Mongazi. Un composant demande « quand commence le mot X de la ligne N » (`quand(11, 'arrive')`), jamais une
 *    seconde : on refait la voix, on relance l'outil, la vidéo suit.
 * ⚠️ Le numéro est LU dans `../tiktok-20-11/donnees.ts` (celui du site public) : jamais écrit ici, le dépôt est public.
 * ⚠️ Les produits sont des DESSINS au trait, avec des prix d'exemple : aucune image générée, aucun produit de client.
 */
import minutageJson from './minutage.json';

export {NUMERO} from '../tiktok-20-11/donnees';

export type Mot = {m: string; a: number; b: number};
export type Ligne = {n: number; texte: string; debut: number; fin: number; mots: Mot[]};
type Minutage = {source: string; voix: string | null; fin_voix: number; duree_voix: number; lignes: Ligne[]};

export const M = minutageJson as unknown as Minutage;

export const FPS = 30;
/** Ce qui reste après le dernier mot, l'enseigne allumée (Mongazi, 21/11 : 1,5 s). */
export const QUEUE = 1.5;
export const DUREE_S = M.fin_voix + QUEUE;
export const DUREE = Math.ceil(DUREE_S * FPS);

export const ECRAN = {l: 1920, h: 1080};
export const TIKTOK = {l: 1080, h: 1920};

/** Remotion additionne les sons sans limiteur : on garde de la réserve. */
export const MIX = 0.85;

export const C = {
	nuit: '#07060D',
	violet: '#9333EA',
	cyan: '#22D3EE',
	blanc: '#F5F3FF',
	orange: '#FF8A1E',
	gris: 'rgba(245,243,255,0.55)',
	grisClair: 'rgba(245,243,255,0.78)',
	carte: '#13111C',
	carteBord: 'rgba(245,243,255,0.09)',
	or: '#FFD27A',
} as const;

export const RVB = {
	violet: [147, 51, 234] as const,
	cyan: [34, 211, 238] as const,
	orange: [255, 138, 30] as const,
	page: [236, 228, 214] as const,
	neonViolet: [172, 82, 255] as const,
	neonCyan: [40, 222, 255] as const,
};

/** Le compte à rebours de Noël se calcule depuis le jour où la pub sort : changer cette date si elle sort plus tard. */
export const DATE_PUBLICATION = '2026-11-21';
export const JOURS_AVANT_NOEL = Math.round(
	(Date.UTC(Number(DATE_PUBLICATION.slice(0, 4)), 11, 25) - Date.parse(`${DATE_PUBLICATION}T00:00:00Z`)) / 86400000,
);

/** Les produits dessinés : des exemples, pas le catalogue d'un client. */
export const PRODUITS = {
	sac: {nom: 'Sac à main', prix: 12500},
	robe: {nom: 'Robe wax', prix: 15000},
	parfum: {nom: 'Parfum', prix: 9000},
	chaussures: {nom: 'Escarpins', prix: 11000},
} as const;
export type Produit = keyof typeof PRODUITS;

export const francs = (p: number) => `${String(p).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')} F`;

/* ─────────────────────────── le minutage ─────────────────────────── */

const normal = (s: string) =>
	s
		.toLowerCase()
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '')
		.replace(/[^a-z0-9]/g, '');

export const ligne = (n: number): Ligne => M.lignes[n - 1];

/** Le mot de la ligne n qui commence par `cle` (sans accents ni ponctuation), à sa n-ième apparition. */
export const motDe = (n: number, cle: string, occurrence = 1): Mot => {
	const l = ligne(n);
	const c = normal(cle);
	let k = 0;
	for (const w of l.mots) {
		if (normal(w.m).startsWith(c)) {
			k += 1;
			if (k === occurrence) return w;
		}
	}
	return {m: cle, a: l.debut, b: l.fin};
};

export const quand = (n: number, cle: string, occurrence = 1) => motDe(n, cle, occurrence).a;

/**
 * Les plans : un élément par phrase. Un plan commence un peu AVANT sa première phrase (`avance`), et s'efface quand
 * le suivant commence. La signature part plus tôt : l'enseigne doit scintiller avant que la voix dise « NEBULA ».
 */
export const PLANS = [
	{id: 'nuit', lignes: [1, 2], avance: 0.15},
	{id: 'statut', lignes: [3, 4, 5], avance: 0.15},
	{id: 'retiens', lignes: [6, 7], avance: 0.15},
	{id: 'boutique', lignes: [8], avance: 0.15},
	{id: 'produits', lignes: [9], avance: 0.15},
	{id: 'appuie', lignes: [10], avance: 0.15},
	{id: 'commande', lignes: [11, 12], avance: 0.15},
	{id: 'noel', lignes: [13], avance: 0.12},
	{id: 'pret', lignes: [14], avance: 0.12},
	{id: 'ecris', lignes: [15], avance: 0.12},
	{id: 'signature', lignes: [16], avance: 0.3},
] as const;
export type PlanId = (typeof PLANS)[number]['id'];

const indice = (id: PlanId) => PLANS.findIndex((p) => p.id === id);
const debutK = (k: number) => ligne(PLANS[k].lignes[0]).debut - PLANS[k].avance;

/** Le début du plan et l'instant où le suivant le remplace. */
export const plan = (id: PlanId) => {
	const k = indice(id);
	return {a: debutK(k), b: k + 1 < PLANS.length ? debutK(k + 1) : DUREE_S};
};

/** Le plan affiché à l'instant t. */
export const planA = (t: number): PlanId => {
	let id: PlanId = PLANS[0].id;
	for (const p of PLANS) if (t >= plan(p.id).a) id = p.id;
	return id;
};
