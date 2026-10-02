/**
 * Les gestes communs du film : les courbes, le ressort, le hasard déterministe,
 * les mots qui s'allument, l'étoile, l'onde de choc, la secousse.
 *
 * ⚠️ Tout se calcule à partir du TEMPS ABSOLU `t` (secondes), jamais en CSS
 * `@keyframes` ni `transition` : une animation CSS ne se rend pas image par image.
 * ⚠️ Toute rotation s'écrit avec son unité (`deg`) : React écrit `rotate: 12` en
 * `12px`, donc invalide et ignoré sans un mot.
 * ⚠️ Le hasard est une fonction de l'indice, jamais Math.random() : chaque image
 * est rendue par un onglet différent, et doit tomber juste toute seule.
 */
import React from 'react';
import {Easing, interpolate, spring} from 'remotion';
import {C, DEGRADE, FPS} from './donnees';
import {TITRE} from './polices';

const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Sortie vive, arrivée douce : la courbe de tout ce qui se pose. */
export const DOUX = Easing.bezier(0.22, 1, 0.36, 1);
/** Aller-retour symétrique, pour ce qui glisse d'une place à l'autre. */
export const GLISSE = Easing.bezier(0.65, 0, 0.35, 1);
/** Ce qui est aspiré : lent, puis de plus en plus vite. */
export const ASPIRE = Easing.bezier(0.55, 0, 0.9, 0.35);

/** Progression 0→1 entre les secondes a et b. */
export const p = (t: number, a: number, b: number, e: (x: number) => number = DOUX) =>
	interpolate(t, [a, b], [0, 1], {...bornes, easing: e});

/** Un ressort qui part à la seconde a. */
export const ressort = (t: number, a: number, conf: {damping?: number; stiffness?: number; mass?: number} = {}) =>
	t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping: 14, stiffness: 150, mass: 0.7, ...conf}});

/** Mélange linéaire. */
export const mix = (a: number, b: number, k: number) => a + (b - a) * k;

/** Le hasard d'un indice : toujours le même nombre 0..1 pour (i, k). */
export const h = (i: number, k = 0) => {
	const x = Math.sin(i * 127.1 + k * 311.7 + 74.7) * 43758.5453;
	return x - Math.floor(x);
};

/** Un bruit lisse 1D (0..1), pour les dérives et les tremblements. */
export const bruit = (x: number, graine = 0) => {
	const i = Math.floor(x);
	const f = x - i;
	const u = f * f * (3 - 2 * f);
	return mix(h(i, graine), h(i + 1, graine), u);
};

/** 50000 → « 50 000 ». */
export const montant = (v: number) =>
	Math.round(v)
		.toString()
		.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

/**
 * LA SECOUSSE : un tremblement de caméra qui part à chaque impact et s'éteint en
 * une demi-seconde. Renvoie [dx, dy] en pixels.
 */
export const secousse = (t: number, impacts: number[], force = 16): [number, number] => {
	let dx = 0;
	let dy = 0;
	for (const a of impacts) {
		const u = t - a;
		if (u < 0 || u > 0.6) continue;
		const amp = force * Math.exp(-u * 7);
		dx += (bruit(u * 38, 3) - 0.5) * 2 * amp;
		dy += (bruit(u * 38, 9) - 0.5) * 2 * amp;
	}
	return [dx, dy];
};

/** Le texte en dégradé du wordmark (lumière en haut, violet en bas). */
export const enDegrade = (degrade = DEGRADE): React.CSSProperties => ({
	backgroundImage: degrade,
	WebkitBackgroundClip: 'text',
	backgroundClip: 'text',
	color: 'transparent',
	WebkitTextFillColor: 'transparent',
});

/**
 * LES MOTS QUI S'ALLUMENT : chaque mot monte de 26 px, sort du flou et s'allume
 * à son instant. `instants` donne le départ de chaque mot (secondes) ; sans lui,
 * les mots se répartissent dans [a, b] selon leur longueur (en attendant les
 * instants mesurés sur la voix).
 */
export const Mots: React.FC<{
	t: number;
	texte: string;
	a: number;
	b?: number;
	instants?: number[];
	taille?: number;
	police?: string;
	graisse?: number;
	couleur?: string;
	degrade?: string;
	style?: React.CSSProperties;
	sortie?: number;
	interligne?: number;
	espacement?: string;
}> = ({t, texte, a, b, instants, taille = 56, police = TITRE, graisse = 800, couleur = C.lavande, degrade, style, sortie, interligne = 1.08, espacement = '-0.01em'}) => {
	const mots = texte.split(' ');
	const total = mots.reduce((s, m) => s + m.length + 2, 0);
	let cumul = 0;
	const departs = instants ?? mots.map((m) => {
		const d = a + ((b ?? a + mots.length * 0.22) - a) * (cumul / total);
		cumul += m.length + 2;
		return d;
	});
	const s = sortie === undefined ? 0 : p(t, sortie, sortie + 0.35, Easing.in(Easing.cubic));
	if (s >= 1) return null;
	return (
		<div style={{fontFamily: police, fontWeight: graisse, fontSize: taille, lineHeight: interligne, letterSpacing: espacement, color: couleur, ...style}}>
			{mots.map((m, k) => {
				const e = ressort(t, departs[k], {damping: 16, stiffness: 170, mass: 0.6});
				const flou = (1 - Math.min(1, e)) * 14;
				return (
					<React.Fragment key={k}>
						<span
							style={{
								display: 'inline-block',
								opacity: Math.min(1, e * 1.4) * (1 - s),
								transform: `translateY(${(1 - e) * 26 - s * 30}px)`,
								filter: flou > 0.4 ? `blur(${flou}px)` : undefined,
								...(degrade ? enDegrade(degrade) : {}),
							}}
						>
							{m}
						</span>
						{k < mots.length - 1 ? ' ' : null}
					</React.Fragment>
				);
			})}
		</div>
	);
};

/**
 * L'ÉTOILE : celle du centre du logo. Quatre longs rayons, quatre courts en
 * diagonale, un cœur blanc et un halo. `eclat` de 0 à 1 (au-delà : éblouissement).
 */
export const Etoile: React.FC<{x: number; y: number; taille: number; eclat?: number; rotation?: number; traine?: number}> = ({
	x,
	y,
	taille,
	eclat = 1,
	rotation = 0,
	traine = 0,
}) => {
	if (taille <= 0.5 || eclat <= 0.01) return null;
	const r = taille;
	const rayon = (long: number, larg: number) => `M0 ${-long} L${larg} 0 L0 ${long} L${-larg} 0 Z`;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, pointerEvents: 'none'}}>
			{/* le halo */}
			<div
				style={{
					position: 'absolute',
					left: -r * 3.2,
					top: -r * 3.2,
					width: r * 6.4,
					height: r * 6.4,
					borderRadius: '50%',
					background: `radial-gradient(circle, rgba(200,225,255,${0.55 * eclat}) 0%, rgba(120,140,255,${0.22 * eclat}) 28%, rgba(107,63,242,${0.08 * eclat}) 55%, transparent 72%)`,
				}}
			/>
			{/* la traînée anamorphique, horizontale, comme un reflet d'objectif */}
			{traine > 0 ? (
				<div
					style={{
						position: 'absolute',
						left: -r * 14 * traine,
						top: -r * 0.18,
						width: r * 28 * traine,
						height: r * 0.36,
						borderRadius: '50%',
						background: `radial-gradient(ellipse at center, rgba(220,240,255,${0.85 * eclat}) 0%, rgba(140,170,255,${0.35 * eclat}) 35%, transparent 70%)`,
					}}
				/>
			) : null}
			<svg
				width={r * 6}
				height={r * 6}
				viewBox={`${-r * 3} ${-r * 3} ${r * 6} ${r * 6}`}
				style={{position: 'absolute', left: -r * 3, top: -r * 3, overflow: 'visible', transform: `rotate(${rotation}deg)`}}
			>
				<defs>
					<radialGradient id="coeur-etoile">
						<stop offset="0%" stopColor="#ffffff" stopOpacity={1} />
						<stop offset="40%" stopColor={C.cyan} stopOpacity={0.9} />
						<stop offset="100%" stopColor={C.bleuClair} stopOpacity={0} />
					</radialGradient>
				</defs>
				<g opacity={Math.min(1, eclat)}>
					<path d={rayon(r * 2.7, r * 0.13)} fill="#f4f8ff" />
					<path d={rayon(r * 2.7, r * 0.13)} fill="#f4f8ff" transform="rotate(90)" />
					<path d={rayon(r * 1.05, r * 0.09)} fill="#dfe9ff" transform="rotate(45)" opacity={0.85} />
					<path d={rayon(r * 1.05, r * 0.09)} fill="#dfe9ff" transform="rotate(-45)" opacity={0.85} />
					<circle r={r * 0.62} fill="url(#coeur-etoile)" />
					<circle r={r * 0.2} fill="#ffffff" />
				</g>
			</svg>
		</div>
	);
};

/** L'ONDE DE CHOC : un anneau de lumière qui s'élargit et s'éteint. */
export const Onde: React.FC<{t: number; a: number; x: number; y: number; rayonMax?: number; duree?: number; couleur?: string}> = ({
	t,
	a,
	x,
	y,
	rayonMax = 1300,
	duree = 0.9,
	couleur = C.cyan,
}) => {
	const u = (t - a) / duree;
	if (u <= 0 || u >= 1) return null;
	const r = rayonMax * Easing.out(Easing.cubic)(u);
	const epaisseur = 2 + 34 * (1 - u) ** 2;
	return (
		<div
			style={{
				position: 'absolute',
				left: x - r,
				top: y - r,
				width: r * 2,
				height: r * 2,
				borderRadius: '50%',
				border: `${epaisseur}px solid ${couleur}`,
				opacity: (1 - u) ** 1.4 * 0.75,
				boxShadow: `0 0 ${40 * (1 - u)}px ${couleur}, inset 0 0 ${40 * (1 - u)}px ${couleur}`,
			}}
		/>
	);
};

/** L'ÉCLAIR : un flash plein cadre qui s'éteint, au moment d'un impact. */
export const Eclair: React.FC<{t: number; a: number; x: number; y: number; duree?: number; force?: number}> = ({t, a, x, y, duree = 0.45, force = 1}) => {
	const u = (t - a) / duree;
	if (u < 0 || u >= 1) return null;
	const o = (1 - u) ** 2 * force;
	return (
		<div
			style={{
				position: 'absolute',
				inset: 0,
				background: `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,${o}) 0%, rgba(190,210,255,${o * 0.8}) 18%, rgba(107,63,242,${o * 0.45}) 45%, rgba(5,4,14,0) 80%)`,
				mixBlendMode: 'screen',
			}}
		/>
	);
};

/** Le petit repère « 01 / 03 » au-dessus des titres de service. */
export const Repere: React.FC<{t: number; a: number; texte: string; sortie?: number; style?: React.CSSProperties}> = ({t, a, texte, sortie, style}) => {
	const e = ressort(t, a, {damping: 20});
	const s = sortie === undefined ? 0 : p(t, sortie, sortie + 0.3);
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: e * (1 - s), ...style}}>
			<div style={{width: 64 * e, height: 2, background: C.cyan, boxShadow: `0 0 12px ${C.cyan}`}} />
			<div style={{fontFamily: 'inherit', letterSpacing: '0.32em', fontSize: 24, color: C.cyan}}>{texte}</div>
		</div>
	);
};
