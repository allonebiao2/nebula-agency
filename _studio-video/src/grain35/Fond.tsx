/**
 * L'OBJET DE LA PUB : LE GRAIN.
 *  · `Fond`     : l'encre prune (ou le papier crème), avec une lumière qui respire ;
 *  · `Grains`   : le grain d'or qui dérive, DENSE SUR LES BORDS ET LIBRE AU CENTRE
 *                 (le dessin de son affiche : le regard se pose là où le grain s'efface) ;
 *  · `Balayage` : la vague de grains qui traverse l'écran et révèle la scène suivante,
 *                 comme un gommage révèle la peau. C'est la seule transition du film.
 */
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, HAUTEUR, LARGEUR} from './donnees';
import {bruit, GLISSE, h, p} from './outils';

export const Fond: React.FC<{clair?: boolean; lumiere?: {x: number; y: number}; t: number}> = ({clair = false, lumiere = {x: 540, y: 760}, t}) => {
	const souffle = 0.85 + 0.15 * Math.sin(t * 1.1);
	return (
		<AbsoluteFill
			style={{
				background: clair
					? `radial-gradient(ellipse 85% 60% at ${lumiere.x}px ${lumiere.y}px, #fffaf6 0%, ${C.papier} 55%, #ecd9cf 100%)`
					: `radial-gradient(ellipse 90% 62% at ${lumiere.x}px ${lumiere.y}px, rgba(120,46,78,${0.55 * souffle}) 0%, ${C.prune2} 30%, ${C.prune} 58%, ${C.encre} 100%)`,
			}}
		/>
	);
};

/**
 * Le grain d'or qui dérive. `n` grains tirés au hasard (déterministe), repoussés
 * hors d'un ovale central ; chacun scintille à son rythme. `densite` 0..1 pour
 * les faire apparaître ou disparaître, `attire` 0..1 pour les aspirer vers un point.
 */
export const Grains: React.FC<{
	t: number;
	n?: number;
	densite?: number;
	attire?: number;
	cible?: {x: number; y: number};
	couleur?: string;
	clair?: boolean;
}> = ({t, n = 130, densite = 1, attire = 0, cible = {x: 540, y: 760}, couleur = C.or, clair = false}) => {
	if (densite <= 0.01) return null;
	const grains = [];
	for (let i = 0; i < n; i++) {
		// une position repoussée vers les bords : rayon tiré au-delà de 0,42
		const ang = h(i, 1) * Math.PI * 2;
		const r = 0.42 + 0.75 * Math.sqrt(h(i, 2));
		let x = LARGEUR / 2 + Math.cos(ang) * r * LARGEUR * 0.62;
		let y = HAUTEUR * 0.47 + Math.sin(ang) * r * HAUTEUR * 0.5;
		x += (bruit(t * 0.25 + i, 3) - 0.5) * 70;
		y += (bruit(t * 0.22 + i, 5) - 0.5) * 70 - t * (6 + h(i, 4) * 14);
		y = ((y % (HAUTEUR + 80)) + HAUTEUR + 80) % (HAUTEUR + 80) - 40;
		if (attire > 0) {
			const k = Math.min(1, attire * (0.7 + 0.6 * h(i, 9)));
			x += (cible.x - x) * k;
			y += (cible.y - y) * k;
		}
		const taille = 2 + h(i, 6) ** 2.2 * 9;
		const scint = 0.45 + 0.55 * Math.max(0, Math.sin(t * (1.5 + h(i, 7) * 3) + i));
		const alpha = densite * scint * (clair ? 0.55 : 0.85) * (1 - attire * 0.3);
		grains.push(
			<div
				key={i}
				style={{
					position: 'absolute',
					left: x - taille / 2,
					top: y - taille / 2,
					width: taille,
					height: taille,
					borderRadius: '50%',
					background: `radial-gradient(circle at 35% 30%, #fff6dc 0%, ${couleur} 45%, ${C.orFonce} 100%)`,
					opacity: alpha,
					boxShadow: taille > 6 && !clair ? `0 0 ${taille * 1.6}px rgba(240,212,154,${0.35 * alpha})` : undefined,
				}}
			/>,
		);
	}
	return <AbsoluteFill style={{pointerEvents: 'none'}}>{grains}</AbsoluteFill>;
};

/**
 * LA VAGUE DE GRAINS : entre `a` et `a + duree`, un front diagonal descend du coin
 * haut-gauche au coin bas-droite. Derrière le front, la scène `apres` ; devant,
 * la scène `avant` ; SUR le front, une bande dense de grains d'or. Renvoie la
 * progression pour que l'appelant sache quoi monter.
 */
export const Balayage: React.FC<{t: number; a: number; duree?: number; avant: React.ReactNode; apres: React.ReactNode}> = ({t, a, duree = 0.75, avant, apres}) => {
	const e = p(t, a, a + duree, GLISSE);
	if (e <= 0) return <>{avant}</>;
	if (e >= 1) return <>{apres}</>;
	// le front : une droite perpendiculaire à la diagonale, qui parcourt de -400 à 2600 px
	const D = Math.hypot(LARGEUR, HAUTEUR);
	const pos = -250 + e * (D + 500);
	const angle = Math.atan2(HAUTEUR, LARGEUR);
	const ux = Math.cos(angle);
	const uy = Math.sin(angle);
	// le polygone « déjà balayé » (en deçà du front) en coordonnées écran
	const pts: [number, number][] = [];
	const coin = (x: number, y: number) => x * ux + y * uy;
	const coins: [number, number][] = [
		[0, 0],
		[LARGEUR, 0],
		[LARGEUR, HAUTEUR],
		[0, HAUTEUR],
	];
	for (let k = 0; k < 4; k++) {
		const [x1, y1] = coins[k];
		const [x2, y2] = coins[(k + 1) % 4];
		const d1 = coin(x1, y1) - pos;
		const d2 = coin(x2, y2) - pos;
		if (d1 <= 0) pts.push([x1, y1]);
		if (d1 * d2 < 0) {
			const s = d1 / (d1 - d2);
			pts.push([x1 + (x2 - x1) * s, y1 + (y2 - y1) * s]);
		}
	}
	const poly = pts.length ? `polygon(${pts.map(([x, y]) => `${x}px ${y}px`).join(',')})` : 'polygon(0 0)';
	const grains = [];
	for (let i = 0; i < 170; i++) {
		const le = (h(i, 11) - 0.5) * (D + 200);
		const prof = -(Math.abs((h(i, 12) - 0.5) * 2) ** 1.6) * 140 + (h(i, 13) - 0.5) * 40;
		const x = (pos + prof) * ux - le * uy;
		const y = (pos + prof) * uy + le * ux;
		if (x < -30 || x > LARGEUR + 30 || y < -30 || y > HAUTEUR + 30) continue;
		const taille = 3 + h(i, 14) ** 2 * 14;
		grains.push(
			<div
				key={i}
				style={{
					position: 'absolute',
					left: x - taille / 2,
					top: y - taille / 2,
					width: taille,
					height: taille,
					borderRadius: '50%',
					background: `radial-gradient(circle at 35% 30%, #fff6dc 0%, ${C.or} 50%, ${C.orFonce} 100%)`,
					boxShadow: `0 0 ${taille * 2}px rgba(240,212,154,.5)`,
				}}
			/>,
		);
	}
	return (
		<AbsoluteFill>
			{avant}
			<AbsoluteFill style={{clipPath: poly}}>{apres}</AbsoluteFill>
			<AbsoluteFill style={{pointerEvents: 'none'}}>{grains}</AbsoluteFill>
		</AbsoluteFill>
	);
};
