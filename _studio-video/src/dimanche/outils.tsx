/**
 * Les gestes de la feuille, réutilisés par toutes les scènes : la feuille qu'on
 * pose, le trait de stylo qui se trace, le surligneur qui passe, le tampon qui
 * tombe, l'écriture qui avance, la case qu'on coche, le compteur qui roule.
 *
 * ⚠️ Tout est calculé à partir du TEMPS ABSOLU `t` (secondes) reçu en prop, et
 * jamais en CSS `@keyframes` : une animation CSS ne se rend pas image par image.
 * ⚠️ Toute rotation s'écrit avec son unité (`deg`) : React écrit `rotate: 12`
 * en `12px`, donc invalide et ignoré sans un mot.
 */
import React from 'react';
import {Easing, interpolate, spring} from 'remotion';
import {C, FPS} from './donnees';
import {MAIN, TEXTE, TITRE} from './polices';

const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Sortie vive, arrivée douce : la courbe de tout ce qui se pose. */
export const DOUX = Easing.bezier(0.22, 1, 0.36, 1);
/** Aller-retour symétrique, pour ce qui glisse d'une place à l'autre. */
export const GLISSE = Easing.bezier(0.65, 0, 0.35, 1);

/** Progression 0→1 entre les secondes a et b. */
export const p = (t: number, a: number, b: number, e: (x: number) => number = DOUX) =>
	interpolate(t, [a, b], [0, 1], {...bornes, easing: e});

/** Un ressort qui part à la seconde a. */
export const ressort = (t: number, a: number, conf: {damping?: number; stiffness?: number; mass?: number} = {}) =>
	t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping: 14, stiffness: 160, mass: 0.7, ...conf}});

/** Entrée (ressort) et sortie (0→1) d'un élément présent de a à b. */
export const fenetre = (t: number, a: number, b: number, sortie = 0.35) => ({
	e: ressort(t, a),
	s: p(t, b, b + sortie, Easing.in(Easing.cubic)),
	vis: t >= a - 0.04 && t <= b + sortie + 0.04,
});

/** 100000 → « 100 000 » (espace insécable), comme il le dit. */
export const montant = (v: number) =>
	Math.round(v)
		.toString()
		.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

/**
 * LA FEUILLE : un papier quadrillé qu'on pose sur la vidéo.
 * Elle arrive d'en bas en se redressant, et repart en glissant.
 */
export const Feuille: React.FC<{
	x: number;
	y: number;
	l: number;
	h: number;
	e: number;
	s?: number;
	incline?: number;
	sombre?: boolean;
	children?: React.ReactNode;
}> = ({x, y, l, h, e, s = 0, incline = -1.2, sombre = false, children}) => {
	const monte = interpolate(e, [0, 1], [140, 0]);
	const tourne = interpolate(e, [0, 1], [incline * 4, incline]);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				width: l,
				height: h,
				borderRadius: 30,
				overflow: 'hidden',
				opacity: Math.min(1, e * 1.6) * (1 - s),
				transform: `translateY(${monte + s * 90}px) rotate(${tourne}deg) scale(${1 - s * 0.04})`,
				background: sombre
					? `linear-gradient(${C.encre2},${C.encre})`
					: `linear-gradient(${C.quadrillage} 1.5px, transparent 1.5px) 0 0/40px 40px,
					   linear-gradient(90deg, ${C.quadrillage} 1.5px, transparent 1.5px) 0 0/40px 40px,
					   linear-gradient(170deg, ${C.papier}, ${C.papier2})`,
				boxShadow: '0 50px 90px -30px rgba(0,0,0,.7), 0 14px 30px -12px rgba(0,0,0,.45)',
			}}
		>
			{children}
		</div>
	);
};

/**
 * LE TRAIT DE STYLO : un chemin SVG qui se trace (pathLength normalisé à 1).
 * À poser dans un <svg> ; `v` va de 0 (rien) à 1 (tracé complet).
 */
export const Trait: React.FC<{
	d: string;
	v: number;
	couleur?: string;
	epaisseur?: number;
	remplissage?: string;
	pointille?: boolean;
}> = ({d, v, couleur = C.stylo, epaisseur = 6, remplissage = 'none', pointille = false}) =>
	v <= 0 ? null : (
		<path
			d={d}
			pathLength={1}
			fill={remplissage}
			stroke={couleur}
			strokeWidth={epaisseur}
			strokeLinecap="round"
			strokeLinejoin="round"
			strokeDasharray={pointille ? undefined : 1}
			strokeDashoffset={pointille ? undefined : 1 - v}
			opacity={pointille ? v : 1}
		/>
	);

/**
 * L'ÉCRITURE À LA MAIN : le texte se découvre de gauche à droite, comme une
 * ligne qu'on écrit. `v` de 0 à 1.
 */
export const Ecrit: React.FC<{
	v: number;
	taille?: number;
	couleur?: string;
	style?: React.CSSProperties;
	children: React.ReactNode;
}> = ({v, taille = 60, couleur = C.stylo, style, children}) => (
	<div
		style={{
			fontFamily: MAIN,
			fontWeight: 700,
			fontSize: taille,
			lineHeight: 1,
			color: couleur,
			whiteSpace: 'nowrap',
			// Caveat déborde de sa chasse (le « d » final) : on découpe une boîte élargie
			paddingRight: '0.3em',
			marginRight: '-0.3em',
			clipPath: `inset(-20% ${(1 - v) * 100}% -20% -0.2em)`,
			...style,
		}}
	>
		{children}
	</div>
);

/**
 * LE SURLIGNEUR : une bande jaune qui passe derrière un mot, de gauche à droite,
 * légèrement penchée comme un vrai coup de feutre.
 */
export const Surligne: React.FC<{v: number; couleur?: string; style?: React.CSSProperties; children: React.ReactNode}> = ({
	v,
	couleur = C.surligneur,
	style,
	children,
}) => (
	<span style={{position: 'relative', display: 'inline-block', ...style}}>
		<span
			style={{
				position: 'absolute',
				left: '-4%',
				right: '-4%',
				top: '18%',
				bottom: '8%',
				background: couleur,
				borderRadius: 6,
				transformOrigin: 'left center',
				transform: `scaleX(${v}) skewX(-8deg) rotate(-1deg)`,
			}}
		/>
		<span style={{position: 'relative'}}>{children}</span>
	</span>
);

/**
 * LE TAMPON : il tombe de haut (×2,4), s'écrase, rebondit à peine.
 * Le bord est rendu irrégulier par un filtre de turbulence, comme une encre
 * qui a bu le papier.
 */
export const Tampon: React.FC<{
	t: number;
	a: number;
	couleur?: string;
	taille?: number;
	incline?: number;
	fond?: string;
	style?: React.CSSProperties;
	children: React.ReactNode;
}> = ({t, a, couleur = C.rouge, taille = 150, incline = -7, fond = 'transparent', style, children}) => {
	if (t < a) return null;
	const r = ressort(t, a, {damping: 11, stiffness: 260, mass: 0.6});
	const echelle = interpolate(r, [0, 1], [2.4, 1]);
	return (
		<div
			style={{
				display: 'inline-block',
				transform: `rotate(${incline}deg) scale(${echelle})`,
				opacity: Math.min(1, r * 3),
				...style,
			}}
		>
			<svg width="0" height="0" style={{position: 'absolute'}}>
				<filter id="encre-bue">
					<feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves={2} seed={7} />
					<feDisplacementMap in="SourceGraphic" scale={5} />
				</filter>
			</svg>
			<div
				style={{
					filter: 'url(#encre-bue)',
					border: `${Math.round(taille / 16)}px solid ${couleur}`,
					borderRadius: taille / 8,
					padding: `${taille * 0.02}px ${taille * 0.16}px ${taille * 0.04}px`,
					fontFamily: TITRE,
					fontWeight: 900,
					fontSize: taille,
					lineHeight: 1,
					letterSpacing: '0.02em',
					textTransform: 'uppercase',
					color: couleur,
					background: fond,
					whiteSpace: 'nowrap',
				}}
			>
				{children}
			</div>
		</div>
	);
};

/** LA CASE : un carré dessiné, puis la coche tracée au stylo. */
export const Case: React.FC<{v: number; coche: number; taille?: number; couleur?: string; croix?: boolean}> = ({
	v,
	coche,
	taille = 60,
	couleur = C.stylo,
	croix = false,
}) => (
	<svg width={taille} height={taille} viewBox="0 0 60 60" style={{overflow: 'visible'}}>
		<Trait d="M8 10 L52 8 L53 52 L9 53 Z" v={v} couleur={couleur} epaisseur={4.5} />
		{croix ? (
			<>
				<Trait d="M14 14 L46 47" v={p(coche, 0, 0.5, Easing.linear)} couleur={C.rouge} epaisseur={7} />
				<Trait d="M46 13 L15 47" v={p(coche, 0.5, 1, Easing.linear)} couleur={C.rouge} epaisseur={7} />
			</>
		) : (
			<Trait d="M13 31 L26 44 L54 4" v={coche} couleur={C.vert} epaisseur={8} />
		)}
	</svg>
);

/** Une étiquette de texte sur la feuille (capitales espacées). */
export const Etiquette: React.FC<{taille?: number; couleur?: string; style?: React.CSSProperties; children: React.ReactNode}> = ({
	taille = 30,
	couleur = C.stylo,
	style,
	children,
}) => (
	<div
		style={{
			fontFamily: TEXTE,
			fontWeight: 800,
			fontSize: taille,
			letterSpacing: '0.12em',
			textTransform: 'uppercase',
			color: couleur,
			whiteSpace: 'nowrap',
			...style,
		}}
	>
		{children}
	</div>
);

/** Un grand chiffre, chasse fixe pour qu'il ne danse pas en roulant. */
export const Chiffre: React.FC<{v: number; taille?: number; couleur?: string; suffixe?: string; style?: React.CSSProperties}> = ({
	v,
	taille = 160,
	couleur = C.stylo,
	suffixe = ' F',
	style,
}) => (
	<div
		style={{
			fontFamily: TITRE,
			fontWeight: 900,
			fontSize: taille,
			lineHeight: 0.9,
			color: couleur,
			fontVariantNumeric: 'tabular-nums',
			whiteSpace: 'nowrap',
			...style,
		}}
	>
		{montant(v)}
		<span style={{fontSize: taille * 0.55}}>{suffixe}</span>
	</div>
);

/** Une bougie de graphique. x, haut/bas de la mèche, ouverture/clôture (en px SVG). */
export const Bougie: React.FC<{x: number; haut: number; bas: number; o: number; c: number; l?: number; v?: number; pale?: boolean}> = ({
	x,
	haut,
	bas,
	o,
	c,
	l = 26,
	v = 1,
	pale = false,
}) => {
	const monte = c < o;
	const couleur = monte ? C.vert : C.rouge;
	const y0 = Math.min(o, c);
	const hCorps = Math.max(6, Math.abs(o - c));
	const k = Math.max(0, Math.min(1, v));
	const milieu = (y0 + y0 + hCorps) / 2;
	return (
		<g opacity={pale ? 0.35 : 1} transform={`translate(0 ${milieu * (1 - k)}) scale(1 ${k || 0.001})`}>
			<line x1={x} x2={x} y1={haut} y2={bas} stroke={couleur} strokeWidth={4} strokeLinecap="round" />
			<rect x={x - l / 2} y={y0} width={l} height={hCorps} rx={4} fill={couleur} />
		</g>
	);
};
