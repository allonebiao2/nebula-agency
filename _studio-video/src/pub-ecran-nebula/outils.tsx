/**
 * Les outils de la pub écran : le temps, l'entrée et la sortie « à la B », les mots qui arrivent avec la voix.
 * ⚠️ Aucune animation CSS ni `transition:` : tout se calcule depuis `t` (secondes), sinon le rendu photographie
 *    l'animation figée ou au hasard.
 * ⚠️ Toute rotation s'écrit avec son `deg` (un `rotate: 12` nu est ignoré sans un mot).
 */
import React, {CSSProperties} from 'react';
import {Easing, interpolate} from 'remotion';
import {loadFont as inter} from '@remotion/google-fonts/Inter';
import {loadFont as jetbrains} from '@remotion/google-fonts/JetBrainsMono';
import {C} from './donnees';

/** Inter, la sans-serif de la recette (600 pour le texte, 800 pour le grand moment) ; JetBrains Mono pour le numéro. */
export const TEXTE = inter('normal', {weights: ['300', '500', '600', '700', '800', '900'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const MONO = jetbrains('normal', {weights: ['500', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;

export const CL = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const SORTIE_DOUCE = Easing.out(Easing.cubic);
export const ENTREE_DOUCE = Easing.in(Easing.cubic);
export const VA_ET_VIENT = Easing.inOut(Easing.cubic);

/** De `de` à `vers` entre les instants a et b (secondes), bornée. */
export const lin = (t: number, a: number, b: number, de = 0, vers = 1, easing = SORTIE_DOUCE) =>
	interpolate(t, [a, b], [de, vers], {...CL, easing});

export const melange = (a: readonly number[], b: readonly number[], p: number) => a.map((v, i) => v + (b[i] - v) * p);
export const rgba = (c: readonly number[], a: number) => `rgba(${c.map((v) => Math.round(v)).join(',')},${a.toFixed(3)})`;

/**
 * L'entrée et la sortie de la référence B : l'élément entre en 0,4 s (fondu, échelle 0,96 → 1, flou de 8 px → net)
 * et sort en 0,3 s quand la phrase suivante commence. Pas de balayage, pas de rotation.
 */
export const entreeSortie = (t: number, debut: number, fin: number): {visible: boolean; style: CSSProperties; p: number} => {
	// la sortie finit quand l'entrée suivante commence : deux éléments ne sont jamais à l'écran ensemble
	const e = lin(t, debut + 0.04, debut + 0.44);
	const s = lin(t, fin - 0.2, fin + 0.04, 0, 1, ENTREE_DOUCE);
	const p = e * (1 - s);
	const flou = 8 * (1 - e) + 6 * s;
	return {
		visible: t >= debut && t <= fin + 0.06,
		p,
		style: {
			opacity: p,
			transform: `scale(${(0.96 + 0.04 * e + 0.02 * s).toFixed(4)})`,
			filter: flou > 0.05 ? `blur(${flou.toFixed(2)}px)` : undefined,
		},
	};
};

/** Un mot qui arrive avec la voix : flou → net, en 0,25 s, au moment où il est dit. */
export const motQuiArrive = (t: number, a: number): CSSProperties => {
	const p = lin(t, a - 0.08, a + 0.2);
	return {
		opacity: p,
		filter: p < 0.99 ? `blur(${((1 - p) * 6).toFixed(2)}px)` : undefined,
		transform: `translateY(${((1 - p) * 0.12).toFixed(3)}em)`,
	};
};

export type MotAffiche = {m: string; a: number; style?: CSSProperties};

/** Une phrase qui s'écrit au rythme de la voix : la place de chaque mot est prise dès le début (aucun saut). */
export const Phrase: React.FC<{t: number; mots: MotAffiche[]; style?: CSSProperties}> = ({t, mots, style}) => (
	<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', columnGap: '0.27em', ...style}}>
		{mots.map((w, i) => (
			<span key={i} style={{display: 'inline-block', whiteSpace: 'pre', ...motQuiArrive(t, w.a), ...w.style}}>
				{w.m}
			</span>
		))}
	</div>
);

/** Le texte de la recette : blanc, Inter 600, interlettrage -1 %. */
export const TYPO: CSSProperties = {fontFamily: TEXTE, fontWeight: 600, letterSpacing: '-0.01em', color: C.blanc};

/** Un objet posé au centre d'un point (x, y) de l'image. */
export const Pose: React.FC<{x: number; y: number; style?: CSSProperties; children: React.ReactNode}> = ({x, y, style, children}) => (
	<div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
		<div style={{flex: 'none', ...style}}>{children}</div>
	</div>
);
