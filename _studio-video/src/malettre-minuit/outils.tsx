/**
 * Les gestes communs du film. Tout se calcule à partir du temps (secondes), jamais en CSS `transition` ni
 * `@keyframes` : une animation CSS ne se rend pas image par image.
 * ⚠️ Toute rotation s'écrit avec son `deg` (`rotate: 12` sort en `12px`, invalide et ignoré).
 */
import React from 'react';
import {Easing, interpolate, random, useCurrentFrame, useVideoConfig} from 'remotion';

const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Les courbes. `T` = la courbe du produit (`--t` de lettre.html), `SORT` = une sortie franche, `RESSORT` = un léger dépassement. */
export const T = Easing.bezier(0.25, 1, 0.5, 1);
export const DOUX = Easing.bezier(0.45, 0, 0.2, 1);
export const SORT = Easing.bezier(0.16, 1, 0.3, 1);
export const ENTRE = Easing.bezier(0.6, 0, 0.9, 0.4);
export const RESSORT = Easing.bezier(0.34, 1.56, 0.64, 1);

/**
 * LE TEMPS DU FILM, en secondes, même à l'intérieur d'un plan. Chaque plan déclare sa seconde de départ
 * (`Decalage`) : les textes, les pluies et la fumée reçoivent des secondes du FILM (celles de la voix), et
 * `useCurrentFrame()` compte depuis le début du plan. Sans ce décalage, tout arrivait en retard de la durée
 * écoulée avant le plan (constaté sur les planches du 2026-10-22 : « Elle a 60 ans ce soir » 3 s trop tard).
 */
export const Decalage = React.createContext(0);
export const useT = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return f / fps + React.useContext(Decalage);
};

/** Progression 0→1 entre a et b. */
export const p = (t: number, a: number, b: number, e: (x: number) => number = T) =>
	interpolate(t, [a, b], [0, 1], {...bornes, easing: e});

/** Monte entre a et b, redescend entre c et d. */
export const vie = (t: number, a: number, b: number, c: number, d: number, e: (x: number) => number = T) =>
	Math.min(p(t, a, b, e), 1 - p(t, c, d, e));

export const mix = (a: number, b: number, k: number) => a + (b - a) * k;

/** Un bruit doux et déterministe (somme de sinus à phases tirées) : -1..1. */
export const bruit = (graine: string, t: number, vitesse = 1) => {
	let s = 0;
	for (let i = 0; i < 3; i++) {
		const f = (0.6 + random(graine + 'f' + i) * 1.4) * vitesse * (i + 1);
		s += Math.sin(t * f * Math.PI * 2 + random(graine + 'p' + i) * 6.283) / (i + 1);
	}
	return s / 1.83;
};

/** La lueur d'une bougie : un battement irrégulier autour de 1. */
export const flamme = (t: number, graine = 'bougie') => 1 + 0.07 * bruit(graine, t, 1.7) + 0.035 * bruit(graine + 'v', t, 7.3);

/** Un dégradé radial : la lumière, partout la même recette. */
export const halo = (couleur: string, force = 1, etendue = 60) =>
	`radial-gradient(circle at 50% 50%, ${couleur} 0%, ${couleur}${Math.round(force * 0x55)
		.toString(16)
		.padStart(2, '0')} ${etendue * 0.35}%, transparent ${etendue}%)`;

/** Un calque plein écran, positionné en absolu. */
export const plein: React.CSSProperties = {position: 'absolute', inset: 0};
