/**
 * L'état de la lumière, instant par instant, lu par le film ET par la pièce :
 *  · le HALO du film (où il est, sa taille, sa couleur, sa force), qui suit l'élément du moment ;
 *  · la LUMIÈRE que l'écran jette dans la pièce (couleur et force), pour le mur, la table et le reflet ;
 *  · l'allumage de l'ENSEIGNE (le tube scintille puis tient, la lueur suit avec un temps de retard).
 * Tous les instants viennent de `donnees.ts` (donc de `minutage.json`).
 */
import {DUREE_S, FPS, plan, quand, RVB} from './donnees';
import {lin, melange, VA_ET_VIENT} from './outils';

type Halo = {x: number; y: number; taille: number; c: readonly number[]; force: number};

const V = RVB.violet;

/** Les poses du halo : il glisse de l'une à l'autre en 0,6 s, en commençant 0,1 s avant l'instant donné. */
const POSES = (): [number, Halo][] => [
	[plan('nuit').a, {x: 960, y: 520, taille: 1150, c: V, force: 0.95}],
	[plan('statut').a, {x: 960, y: 610, taille: 1000, c: V, force: 0.9}],
	[quand(4, 'il'), {x: 1010, y: 560, taille: 1150, c: V, force: 0.9}],
	[quand(5, 'dors'), {x: 1000, y: 580, taille: 900, c: V, force: 0.45}],
	[quand(5, 'ailleurs') - 0.15, {x: 1300, y: 560, taille: 1000, c: RVB.orange, force: 0.5}],
	[plan('retiens').a, {x: 960, y: 560, taille: 1100, c: V, force: 0.9}],
	[plan('boutique').a, {x: 960, y: 640, taille: 1000, c: V, force: 0.9}],
	[plan('produits').a, {x: 960, y: 620, taille: 1700, c: V, force: 0.9}],
	[quand(9, 'un', 1), {x: 960, y: 600, taille: 1000, c: V, force: 0.95}],
	[plan('appuie').a, {x: 960, y: 640, taille: 1000, c: V, force: 0.9}],
	[plan('commande').a, {x: 960, y: 580, taille: 700, c: V, force: 0.75}],
	[quand(11, 'arrive') - 0.2, {x: 960, y: 600, taille: 1400, c: V, force: 0.95}],
	[plan('noel').a, {x: 960, y: 600, taille: 1150, c: V, force: 0.95}],
	[plan('pret').a, {x: 960, y: 580, taille: 1200, c: V, force: 0.9}],
	[plan('ecris').a, {x: 960, y: 600, taille: 1150, c: V, force: 0.9}],
	[plan('signature').a, {x: 960, y: 560, taille: 1100, c: V, force: 0}],
];

let cache: [number, Halo][] | null = null;

export const halo = (t: number): Halo => {
	cache = cache ?? POSES();
	let etat = cache[0][1];
	for (const [instant, pose] of cache) {
		if (t < instant - 0.1) break;
		const p = lin(t, instant - 0.1, instant + 0.5, 0, 1, VA_ET_VIENT);
		etat = {
			x: etat.x + (pose.x - etat.x) * p,
			y: etat.y + (pose.y - etat.y) * p,
			taille: etat.taille + (pose.taille - etat.taille) * p,
			c: melange(etat.c, pose.c, p),
			force: etat.force + (pose.force - etat.force) * p,
		};
	}
	// le film s'ouvre sur la nuit : le halo est déjà là à la première image (elle sert de vignette), puis il monte
	return {...etat, force: etat.force * (0.5 + 0.5 * lin(t, 0, 0.8))};
};

/** La respiration du halo (la recette) : échelle 0,9 → 1,1 et opacité 0,5 → 0,8 sur 4 s. */
export const respiration = (t: number) => {
	const s = Math.sin((t / 4) * Math.PI * 2);
	return {echelle: 1 + 0.1 * s, opacite: 0.65 + 0.15 * s};
};

/* ─────────────────────────── l'enseigne ─────────────────────────── */

/** L'allumage d'un néon, image par image : [durée en images, niveau]. Le dernier pas tient (durée 0). */
const MOTIFS = {
	nebula: [[2, 0.95], [3, 0], [1, 0.55], [4, 0.04], [2, 1], [2, 0.12], [0, 1]],
	agency: [[1, 0.85], [4, 0], [2, 1], [3, 0.08], [1, 0.7], [2, 0], [0, 1]],
} as const;
export type MotNeon = keyof typeof MOTIFS;

/** Le tube de chaque mot s'allume SUR le mot dit (« NEBULA », puis « Agency »), un souffle avant lui. */
export const allumageNeon = (mot: MotNeon) => (mot === 'nebula' ? quand(16, 'nebula') - 0.22 : quand(16, 'agency') - 0.16);

export const niveauTube = (t: number, mot: MotNeon) => {
	const t0 = allumageNeon(mot);
	if (t < t0) return 0;
	let f = (t - t0) * FPS;
	for (const [d, v] of MOTIFS[mot]) {
		if (d === 0 || f < d) return v;
		f -= d;
	}
	return 1;
};

/** La lueur suit le tube avec du retard (le gaz chauffe) : moyenne des 0,4 s passées, et une montée lente. */
export const niveauLueur = (t: number, mot: MotNeon) => {
	const t0 = allumageNeon(mot);
	if (t < t0) return 0;
	let s = 0;
	const n = 10;
	for (let k = 0; k < n; k++) s += niveauTube(t - k * 0.04, mot);
	const chauffe = lin(t, t0, t0 + 0.9);
	const souffle = 1 + 0.025 * Math.sin(t * 7.3) * chauffe;
	return (s / n) * (0.5 + 0.5 * chauffe) * souffle;
};

/**
 * Le numéro sous l'enseigne (Polaris et le directeur, 21/11 : il ne restait que 1,7 s à l'écran). Une ligne discrète,
 * comme la ligne finale de la référence B : elle arrive quand AGENCY tient sa lumière, et reste jusqu'à la fin.
 */
export const apparitionNumeroFin = () => allumageNeon('agency') + 0.45;

/** Les instants où un tube passe de l'ombre à la lumière (un claquement de néon chacun). */
export const claquements = (mot: MotNeon): number[] => {
	const t0 = allumageNeon(mot);
	const out: number[] = [];
	let f = 0;
	let avant = 0;
	for (const [d, v] of MOTIFS[mot]) {
		if (v > 0.5 && avant <= 0.5) out.push(t0 + f / FPS);
		avant = v;
		f += d;
	}
	return out;
};

/* ─────────────────────────── la lumière de l'écran dans la pièce ─────────────────────────── */

/**
 * Ce que l'écran jette sur le mur et la table : le halo du moment, le violet plein du grand moment, la page claire du
 * catalogue, puis le néon. C'est cette lumière qui fait croire à l'écran filmé.
 */
export const lumiereEcran = (t: number): {c: readonly number[]; force: number} => {
	const h = halo(t);
	const r = respiration(t);
	let c: readonly number[] = h.c;
	let force = h.force * r.opacite * 0.75;

	const ret = plan('retiens');
	const plein = lin(t, ret.a, ret.a + 0.5, 0, 1, VA_ET_VIENT) * (1 - lin(t, ret.b - 0.25, ret.b + 0.08, 0, 1, VA_ET_VIENT));
	if (plein > 0) {
		c = melange(c, RVB.violet, plein);
		force = force + (1.25 - force) * plein;
	}

	const bou = plan('boutique');
	const page = lin(t, bou.a + 0.1, bou.a + 0.5) * (1 - lin(t, bou.b - 0.1, bou.b + 0.3));
	if (page > 0) {
		c = melange(c, RVB.page, page * 0.7);
		force = force + (0.9 - force) * page * 0.6;
	}

	const neon = Math.max(niveauLueur(t, 'nebula'), 0.7 * niveauLueur(t, 'agency'));
	if (neon > 0) {
		c = melange(RVB.neonViolet, RVB.neonCyan, 0.35 * lin(t, allumageNeon('agency'), allumageNeon('agency') + 0.6));
		force = Math.max(force, 0.55 * neon);
	}
	return {c, force: force * (1 - lin(t, DUREE_S - 0.6, DUREE_S, 0, 0.35))};
};
