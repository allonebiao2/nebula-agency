/**
 * Les gestes communs de la pub : la courbe du produit, l'encre qui sèche, la cire.
 *
 * ⚠️ Tout se calcule à partir du temps `t` du plan (secondes), jamais en CSS
 * `@keyframes` ni `transition` : une animation CSS ne se rend pas image par image.
 * ⚠️ Toute rotation s'écrit avec son `deg` : `rotate: 12` sort en `12px`, invalide
 * et ignoré sans un mot (piège noté dans CLAUDE.md).
 */
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, CIRES, PAPIERS, SANS, SCEAUX, SERIF, type Habillage} from './donnees';

const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** La courbe du produit, `--t: cubic-bezier(.25,1,.5,1)` dans `lettre.html`. */
export const T = Easing.bezier(0.25, 1, 0.5, 1);

/** Progression 0→1 entre les secondes a et b. */
export const p = (t: number, a: number, b: number, e: (x: number) => number = T) =>
	interpolate(t, [a, b], [0, 1], {...bornes, easing: e});

/** Monte entre a et b, redescend entre c et d. */
export const vie = (t: number, a: number, b: number, c: number, d: number) =>
	Math.min(p(t, a, b), 1 - p(t, c, d));

export const mix = (a: number, b: number, k: number) => a + (b - a) * k;

/** Le fond de tous les plans : la même nuit, donc une coupe entre deux plans ne se voit pas. */
export const NUIT = `radial-gradient(120% 90% at 50% 40%,${C.nuit2} 0%,${C.nuit} 62%)`;

/**
 * L'ENCRE QUI SÈCHE : la signature du produit pour tout texte qui apparaît. Floue
 * puis nette, comme de l'encre fraîche qui prend. Jamais un fondu nu.
 */
export const Encre: React.FC<{
	t: number;
	a: number;
	duree?: number;
	style?: React.CSSProperties;
	children: React.ReactNode;
}> = ({t, a, duree = 0.6, style, children}) => {
	const k = p(t, a, a + duree);
	return <div style={{...style, opacity: k * (style?.opacity === undefined ? 1 : Number(style.opacity)), filter: `blur(${(1 - k) * 9}px)`}}>{children}</div>;
};

/**
 * LE CACHET DE CIRE, avec l'habillage réel d'une lettre. Il respire (3,4 s par
 * souffle, comme dans le produit) ; `lumiere` 0→1 l'allume à l'heure dite.
 */
export const Cachet: React.FC<{
	h: Habillage;
	taille: number;
	t: number;
	lumiere?: number;
	style?: React.CSSProperties;
}> = ({h, taille, t, lumiere = 0, style}) => {
	const c = CIRES[h.cire];
	const souffle = 1 + 0.04 * Math.sin((t / 3.4) * Math.PI * 2);
	return (
		<div
			style={{
				width: taille,
				height: taille,
				borderRadius: '50%',
				display: 'grid',
				placeItems: 'center',
				position: 'relative',
				background: `radial-gradient(circle at 34% 30%,${c.clair},${c.cire} 62%,${c.fonce} 100%)`,
				boxShadow: `0 ${taille * 0.09}px ${taille * 0.23}px rgba(0,0,0,.45),0 2px 0 rgba(255,255,255,.28) inset,0 0 ${taille * 0.7 * lumiere}px ${taille * 0.12 * lumiere}px ${c.lumiere}`,
				color: C.papier,
				fontFamily: SERIF,
				fontSize: taille * 0.33,
				scale: String(souffle),
				...style,
			}}
		>
			<div style={{position: 'absolute', inset: taille * 0.065, borderRadius: '50%', border: `${Math.max(1.5, taille * 0.011)}px dashed rgba(244,237,224,.42)`}} />
			{h.sceau === 'initiale' ? (
				h.initiale
			) : (
				<svg viewBox="0 0 24 24" style={{width: '46%', height: '46%', fill: 'none', stroke: 'currentColor', strokeWidth: 1.5, strokeLinejoin: 'round', strokeLinecap: 'round'}}>
					{SCEAUX[h.sceau].map((d) => (
						<path key={d} d={d} />
					))}
				</svg>
			)}
		</div>
	);
};

/**
 * L'ENVELOPPE, dessinée comme dans `lettre.html` : un rabat en V venu du haut,
 * jamais un carré tourné à 45°. Le papier vient de l'habillage.
 */
export const Enveloppe: React.FC<{
	h: Habillage;
	largeur: number;
	t: number;
	lumiere?: number;
	sansCachet?: boolean;
	style?: React.CSSProperties;
	children?: React.ReactNode;
}> = ({h, largeur, t, lumiere = 0, sansCachet, style, children}) => {
	const pa = PAPIERS[h.papier];
	const hauteur = largeur * 0.617;
	const trait = h.papier === 'nuit' ? '244,237,224' : '36,29,43';
	return (
		<div
			style={{
				position: 'relative',
				width: largeur,
				height: hauteur,
				background: `linear-gradient(168deg,${pa.papier} 0%,${pa.papier2} 100%)`,
				borderRadius: largeur * 0.018,
				boxShadow: `0 ${largeur * 0.07}px ${largeur * 0.18}px rgba(0,0,0,.55),0 3px 0 rgba(255,255,255,.3) inset`,
				...style,
			}}
		>
			<svg viewBox="0 0 162 100" preserveAspectRatio="none" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
				<path d="M0 0 L81 52 L162 0 Z" fill={`rgba(${trait},.055)`} />
				<path d="M0 0 L81 52 L162 0" fill="none" stroke={`rgba(${trait},.16)`} strokeWidth="0.5" />
				<path d="M0 100 L81 52" fill="none" stroke={`rgba(${trait},.10)`} strokeWidth="0.5" />
				<path d="M162 100 L81 52" fill="none" stroke={`rgba(${trait},.10)`} strokeWidth="0.5" />
			</svg>
			{sansCachet ? null : (
				<Cachet h={h} taille={largeur * 0.25} t={t} lumiere={lumiere} style={{position: 'absolute', left: '50%', top: '52%', translate: '-50% -50%'}} />
			)}
			{children}
		</div>
	);
};

/** La petite marque du produit : le point de cire et « Ma lettre à… », comme l'en-tête de `creer.html`. */
export const Marque: React.FC<{taille: number; style?: React.CSSProperties}> = ({taille, style}) => (
	<div style={{display: 'flex', alignItems: 'center', gap: taille * 0.42, fontFamily: SERIF, fontSize: taille, color: C.papier, ...style}}>
		<span
			style={{
				width: taille * 0.62,
				height: taille * 0.62,
				borderRadius: '50%',
				background: `radial-gradient(circle at 34% 30%,${CIRES.bordeaux.clair},${CIRES.bordeaux.cire} 62%,${CIRES.bordeaux.fonce} 100%)`,
				boxShadow: '0 4px 12px rgba(0,0,0,.4)',
			}}
		/>
		Ma lettre à…
	</div>
);

/** Le texte d'appui sous un plan : sans empattement, gris de nuit, lisible muet. */
export const appui: React.CSSProperties = {fontFamily: SANS, fontSize: 46, color: C.grisNuit, letterSpacing: '0.02em', textAlign: 'center'};
/** Le grand texte d'un plan : l'empattement du produit, papier sur nuit. */
export const grand: React.CSSProperties = {fontFamily: SERIF, fontSize: 92, lineHeight: 1.12, color: C.papier, textAlign: 'center'};
