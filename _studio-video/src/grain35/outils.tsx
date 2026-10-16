/**
 * Les gestes communs de la pub : les courbes, le ressort, le hasard déterministe,
 * les mots qui se posent.
 *
 * ⚠️ Tout se calcule à partir du TEMPS ABSOLU `t` (secondes), jamais en CSS
 * `@keyframes` ni `transition` : une animation CSS ne se rend pas image par image.
 * ⚠️ Toute rotation s'écrit avec son unité (`deg`) : React écrit `rotate: 12` en
 * `12px`, donc invalide et ignoré sans un mot.
 * ⚠️ Le hasard est une fonction de l'indice, jamais Math.random() : le rendu se
 * fait par morceaux, et chaque image doit tomber juste toute seule.
 */
import React from 'react';
import {Easing, interpolate, spring} from 'remotion';
import {C, FPS, OR_DEGRADE} from './donnees';
import {ACCENT, TEXTE, TITRE} from './polices';

const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Sortie vive, arrivée douce : la courbe de tout ce qui se pose. */
export const DOUX = Easing.bezier(0.22, 1, 0.36, 1);
/** Aller-retour symétrique : ce qui glisse d'une place à l'autre. */
export const GLISSE = Easing.bezier(0.65, 0, 0.35, 1);
/** Ce qui est aspiré : lent, puis de plus en plus vite. */
export const ASPIRE = Easing.bezier(0.55, 0, 0.9, 0.35);
/** La chute d'un grain : la pesanteur. */
export const CHUTE = Easing.bezier(0.5, 0, 0.95, 0.6);

/** Progression 0→1 entre les secondes a et b. */
export const p = (t: number, a: number, b: number, e: (x: number) => number = DOUX) =>
	interpolate(t, [a, b], [0, 1], {...bornes, easing: e});

/** Un ressort qui part à la seconde a. */
export const ressort = (t: number, a: number, conf: {damping?: number; stiffness?: number; mass?: number} = {}) =>
	t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping: 14, stiffness: 150, mass: 0.7, ...conf}});

export const mix = (a: number, b: number, k: number) => a + (b - a) * k;

/** Le hasard d'un indice : toujours le même nombre 0..1 pour (i, k). */
export const h = (i: number, k = 0) => {
	const x = Math.sin(i * 127.1 + k * 311.7 + 74.7) * 43758.5453;
	return x - Math.floor(x);
};

/** Un bruit lisse 1D (0..1), pour les dérives. */
export const bruit = (x: number, graine = 0) => {
	const i = Math.floor(x);
	const f = x - i;
	const u = f * f * (3 - 2 * f);
	return mix(h(i, graine), h(i + 1, graine), u);
};

/** Fenêtre de présence : 0 avant a, monte, tient, redescend après b. */
export const fenetre = (t: number, a: number, b: number, entree = 0.35, sortie = 0.35) =>
	Math.min(p(t, a, a + entree), 1 - p(t, b - sortie, b, Easing.in(Easing.cubic)));

/** Le texte en or (feuille d'or : lumière en haut, bronze en bas). */
export const enOr = (degrade = OR_DEGRADE): React.CSSProperties => ({
	backgroundImage: degrade,
	WebkitBackgroundClip: 'text',
	backgroundClip: 'text',
	color: 'transparent',
	WebkitTextFillColor: 'transparent',
});

/**
 * LES MOTS QUI SE POSENT : chaque mot monte de 22 px, sort du flou et s'allume à
 * son instant, réparti dans [a, b] selon sa longueur (la voix le dit à peu près
 * ainsi ; le minutage mesuré resserre ensuite a et b sur la vraie prise).
 * `accent` : les mots en Instrument Serif italique, en or (ex. « premier »).
 */
export const Mots: React.FC<{
	t: number;
	texte: string;
	a: number;
	b: number;
	taille?: number;
	police?: string;
	graisse?: number;
	couleur?: string;
	accent?: string[];
	couleurAccent?: string;
	sortie?: number;
	interligne?: number;
	espacement?: string;
	style?: React.CSSProperties;
}> = ({t, texte, a, b, taille = 72, police = TITRE, graisse = 400, couleur = C.creme, accent = [], couleurAccent, sortie, interligne = 1.12, espacement = '0', style}) => {
	const mots = texte.split(' ');
	const total = mots.reduce((s, m) => s + m.length + 2, 0);
	let cumul = 0;
	const departs = mots.map((m) => {
		const d = a + (b - a) * 0.92 * (cumul / total);
		cumul += m.length + 2;
		return d;
	});
	const s = sortie === undefined ? 0 : p(t, sortie, sortie + 0.4, Easing.in(Easing.cubic));
	if (s >= 1 || t < a - 0.05) return null;
	const nu = (m: string) => m.replace(/[.,…?:«»!]/g, '').toLowerCase();
	return (
		<div style={{fontFamily: police, fontWeight: graisse, fontSize: taille, lineHeight: interligne, letterSpacing: espacement, color: couleur, ...style}}>
			{mots.map((m, k) => {
				const e = ressort(t, departs[k], {damping: 18, stiffness: 120, mass: 0.7});
				const flou = (1 - Math.min(1, e)) * 12;
				const estAccent = accent.includes(nu(m));
				return (
					<React.Fragment key={k}>
						<span
							style={{
								display: 'inline-block',
								opacity: Math.min(1, e * 1.3) * (1 - s),
								transform: `translateY(${(1 - e) * 22 - s * 26}px)`,
								filter: flou > 0.4 ? `blur(${flou}px)` : undefined,
								fontFamily: estAccent ? ACCENT : undefined,
								fontStyle: estAccent ? 'italic' : undefined,
								fontSize: estAccent ? '1.08em' : undefined,
								...(estAccent ? (couleurAccent ? {color: couleurAccent} : enOr()) : {}),
								paddingRight: estAccent ? '0.06em' : undefined,
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

/** L'étiquette espacée en capitales de la vitrine (« NOTRE VISION », « COTONOU · BÉNIN »). */
export const Etiquette: React.FC<{texte: string; opacite?: number; couleur?: string; taille?: number; style?: React.CSSProperties}> = ({
	texte,
	opacite = 1,
	couleur = C.or,
	taille = 26,
	style,
}) => (
	<div
		style={{
			fontFamily: TEXTE,
			fontWeight: 400,
			fontSize: taille,
			letterSpacing: '0.42em',
			textTransform: 'uppercase',
			color: couleur,
			opacity: opacite,
			...style,
		}}
	>
		{texte}
	</div>
);

/** Le filet doré au losange central de la vitrine (— ◆ —), qui se déploie. */
export const Filet: React.FC<{e: number; largeur?: number; couleur?: string}> = ({e, largeur = 260, couleur = C.or}) => (
	<div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, opacity: Math.min(1, e * 2)}}>
		<div style={{height: 1.5, width: (largeur / 2) * e, background: `linear-gradient(90deg, transparent, ${couleur})`}} />
		<div style={{width: 11, height: 11, background: couleur, transform: `rotate(45deg) scale(${e})`}} />
		<div style={{height: 1.5, width: (largeur / 2) * e, background: `linear-gradient(90deg, ${couleur}, transparent)`}} />
	</div>
);
