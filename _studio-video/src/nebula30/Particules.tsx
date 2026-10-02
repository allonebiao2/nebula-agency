/**
 * LA POUSSIÈRE D'ÉTOILES : le fil du film. 2 800 grains, toujours les mêmes, qui
 * passent d'une forme à l'autre :
 *
 *   explosion → galaxie (l'ovale du logo) → contour du téléphone → ciel
 *   → orbite autour du catalogue → ciel → implosion dans l'étoile du logo
 *   → la galaxie du logo, dessinée grain par grain, puis éteinte.
 *
 * Chaque grain a une position CALCULÉE à partir de t (aucune simulation) : une
 * image se rend seule, dans n'importe quel ordre. La vitesse se lit en comparant
 * t et t − 1/60 s, et devient une traînée : c'est le flou de mouvement.
 */
import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {CENTRE, GALAXIE, HAUTEUR, LARGEUR, ORBITE, T, TEL} from './donnees';
import {COUCHES, POINTS_MARQUE} from './couches';
import {ETOILE, enImage} from './logo';
import {Easing} from 'remotion';
import {ASPIRE, DOUX, GLISSE, h, p} from './outils';

const N = 2800;
const TAU = Math.PI * 2;
const COULEURS = ['#e4f8ff', '#9ad6ff', '#62a8ff', '#7f63f5', '#b689ff', '#ffffff'];

type Etat = [number, number, number, number]; // x, y, taille, opacité

const melange = (a: Etat, b: Etat, k: number): Etat =>
	k <= 0 ? a : k >= 1 ? b : [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, a[3] + (b[3] - a[3]) * k];

const incline = (cx: number, cy: number, ex: number, ey: number, degres: number): [number, number] => {
	const r = (degres * Math.PI) / 180;
	return [cx + ex * Math.cos(r) - ey * Math.sin(r), cy + ex * Math.sin(r) + ey * Math.cos(r)];
};

/** L'explosion : chaque grain part dans sa direction, freiné par le vide. */
const explosion = (i: number, t: number): Etat => {
	const u = Math.max(0, t - T.bang);
	const a = h(i, 7) * TAU;
	const v = 0.16 + 1.5 * h(i, 8) ** 2;
	const d = 1150 * v * (1 - Math.exp(-u * 2.8));
	return [CENTRE.x + Math.cos(a) * d, CENTRE.y + Math.sin(a) * d * 0.92, 1.4 + 2.4 * h(i, 6), 1];
};

/** La galaxie : trois bras en spirale et un anneau, qui tournent (plus vite au centre). */
const galaxie = (i: number, t: number): Etat => {
	const anneau = h(i, 2) < 0.24;
	const rho = anneau ? 1 + (h(i, 3) - 0.5) * 0.1 : 0.06 + 0.94 * Math.sqrt(h(i, 1));
	const theta = anneau ? h(i, 4) * TAU : ((i % 3) * TAU) / 3 + rho * 4.6 + (h(i, 5) - 0.5) * 0.7;
	const omega = anneau ? 0.22 : 0.5 / (0.22 + rho);
	const ang = theta + omega * (t - T.bang);
	const [x, y] = incline(CENTRE.x, CENTRE.y, GALAXIE.a * rho * Math.cos(ang), GALAXIE.b * rho * Math.sin(ang), GALAXIE.inclinaison);
	const devant = (Math.sin(ang) + 1) / 2;
	const taille = (anneau ? 1.7 : 2.8 * (1.15 - rho)) * (0.7 + 0.6 * h(i, 6)) * (0.8 + 0.4 * devant);
	const alpha = (anneau ? 0.6 : 0.95 - 0.5 * rho) * (0.6 + 0.4 * devant);
	return [x, y, taille, alpha];
};

/** Le contour du téléphone : un rectangle très arrondi (une « squircle »). */
const contourTel = (i: number): Etat => {
	const a = h(i, 9) * TAU;
	const c = Math.cos(a);
	const s = Math.sin(a);
	const n = 0.18; // plus c'est petit, plus les coins sont carrés
	const x = TEL.x + (TEL.l / 2 + 12) * Math.sign(c) * Math.abs(c) ** n + (h(i, 21) - 0.5) * 6;
	const y = TEL.y + (TEL.h / 2 + 12) * Math.sign(s) * Math.abs(s) ** n + (h(i, 22) - 0.5) * 6;
	return [x, y, 1.3 + 1.6 * h(i, 6), 0.95];
};

/** Le ciel : une poussière lente, à peine visible, qui dérive vers le haut. */
const ciel = (i: number, t: number): Etat => {
	const x = h(i, 10) * LARGEUR + Math.sin(t * 0.2 + h(i, 11) * 6) * 12;
	const y = (((h(i, 12) * HAUTEUR - t * (6 + 10 * h(i, 13))) % HAUTEUR) + HAUTEUR) % HAUTEUR;
	return [x, y, 0.8 + 1.5 * h(i, 14), 0.14 + 0.3 * h(i, 15)];
};

/** L'orbite du catalogue : la même ellipse que les fiches produits, ouverte depuis le téléphone. */
const orbite = (i: number, t: number, ouverture = 1): Etat => {
	const ang = h(i, 16) * TAU + 0.55 * (t - T.catalogue);
	const rho = (1 + (h(i, 17) - 0.5) * 0.14) * ouverture;
	const [x, y] = incline(ORBITE.x, ORBITE.y, ORBITE.a * rho * Math.cos(ang), ORBITE.b * rho * Math.sin(ang), ORBITE.inclinaison);
	const devant = (Math.sin(ang) + 1) / 2;
	return [x, y, (1.1 + 1.7 * h(i, 6)) * (0.6 + 0.6 * devant), 0.3 + 0.55 * devant];
};

/** Un grain de la galaxie du logo. */
const pointLogo = (i: number): Etat => {
	const q = POINTS_MARQUE[i % POINTS_MARQUE.length];
	const m = COUCHES.marque;
	const [x, y] = enImage(m.x + q[0] * m.w, m.y + q[1] * m.h);
	return [x, y, 1.5 + 1.5 * h(i, 6), 0.95];
};

/** L'état d'un grain à l'instant t, ou null s'il n'existe pas encore. */
const etat = (i: number, t: number): Etat | null => {
	if (t < T.bang) return null;
	const retard = h(i, 18);
	if (t < T.versTel) {
		const k = p(t, T.bang + 0.3 + retard * 0.5, T.bang + 1.7 + retard * 0.6, GLISSE);
		return melange(explosion(i, t), galaxie(i, t), k);
	}
	if (t < T.catalogue) {
		const k = p(t, T.versTel + retard * 0.3, T.versTel + 0.55 + retard * 0.3, GLISSE);
		const versCiel = p(t, T.revele - 0.1 + retard * 0.4, T.revele + 0.9 + retard * 0.4, GLISSE);
		return melange(melange(galaxie(i, t), contourTel(i), k), ciel(i, t), versCiel);
	}
	if (t < T.outil) {
		if (h(i, 19) < 0.45) {
			// ces grains-là s'éteignent dans le ciel, et l'orbite s'ouvre depuis le téléphone :
			// aucun grain ne traverse l'écran (c'était une toile d'araignée de traînées)
			const ouvre = p(t, T.catalogue + 0.2 + retard * 0.3, T.catalogue + 1.0 + retard * 0.3) * (1 - p(t, T.outil - 0.55, T.outil - 0.05, Easing.in(Easing.cubic)));
			const c = ciel(i, t);
			if (ouvre <= 0.001) return [c[0], c[1], c[2], c[3] * (1 - p(t, T.catalogue - 0.2, T.catalogue + 0.3))];
			const o = orbite(i, t, ouvre);
			return [o[0], o[1], o[2], o[3] * Math.min(1, ouvre * 1.5)];
		}
		return ciel(i, t);
	}
	if (t < T.implosion) return ciel(i, t);
	if (t < T.hit) {
		const k = p(t, T.implosion + retard * 0.35, T.hit, ASPIRE);
		return melange(ciel(i, t), [ETOILE.x + (h(i, 26) - 0.5) * 10, ETOILE.y + (h(i, 27) - 0.5) * 6, 0.9, 0.55], k);
	}
	// l'étoile se rallume : les grains jaillissent, puis dessinent la galaxie du logo
	const u = t - T.hit;
	const a = h(i, 7) * TAU;
	const d = 520 * (0.2 + h(i, 8)) * (1 - Math.exp(-u * 5));
	const jaillit: Etat = [ETOILE.x + Math.cos(a) * d, ETOILE.y + Math.sin(a) * d * 0.7, 1.6 + 2 * h(i, 6), 1];
	const pose = melange(jaillit, pointLogo(i), p(t, T.hit + 0.12 + retard * 0.25, T.hit + 1.15 + retard * 0.35, DOUX));
	const eteint = 1 - p(t, T.hit + 1.5 + retard * 0.5, T.hit + 2.5 + retard * 0.6);
	// quelques grains restent, et scintillent autour du logo
	if (h(i, 20) < 0.05) {
		const scint = 0.5 + 0.5 * Math.sin(t * (2 + 3 * h(i, 23)) + h(i, 24) * 6);
		return [pose[0] + Math.sin(t * 0.5 + i) * 14, pose[1] - u * 6, pose[2] * 1.2, Math.max(pose[3] * eteint, 0.65 * scint)];
	}
	return [pose[0], pose[1], pose[2], pose[3] * eteint];
};

/** Un grain lumineux : un dégradé radial pré-dessiné, par couleur. */
const fabriquerSprites = () =>
	COULEURS.map((couleur) => {
		const c = document.createElement('canvas');
		c.width = 48;
		c.height = 48;
		const g = c.getContext('2d')!;
		const d = g.createRadialGradient(24, 24, 0, 24, 24, 24);
		d.addColorStop(0, '#ffffff');
		d.addColorStop(0.18, couleur);
		d.addColorStop(0.5, couleur + '55');
		d.addColorStop(1, couleur + '00');
		g.fillStyle = d;
		g.fillRect(0, 0, 48, 48);
		return c;
	});

export const Particules: React.FC<{t: number; opacite?: number}> = ({t, opacite = 1}) => {
	const ref = useRef<HTMLCanvasElement>(null);
	const sprites = useMemo(fabriquerSprites, []);
	useLayoutEffect(() => {
		const ctx = ref.current?.getContext('2d');
		if (!ctx) return;
		ctx.clearRect(0, 0, LARGEUR, HAUTEUR);
		if (opacite <= 0) return;
		ctx.globalCompositeOperation = 'lighter';
		ctx.lineCap = 'round';
		const avant = t - 1 / 60;
		for (let i = 0; i < N; i++) {
			const e = etat(i, t);
			if (!e || e[3] <= 0.01) continue;
			const [x, y, taille, alpha] = e;
			if (x < -40 || x > LARGEUR + 40 || y < -40 || y > HAUTEUR + 40) continue;
			const c = Math.floor(h(i, 25) * COULEURS.length);
			const e0 = etat(i, avant);
			if (e0) {
				const vitesse = Math.hypot(x - e0[0], y - e0[1]);
				if (vitesse > 3) {
					// la traînée : deux images et demie de mouvement, plafonnée à 70 px, c'est le flou
					const longueur = Math.min(2.5, 70 / vitesse);
					ctx.globalAlpha = Math.min(1, alpha * opacite * 0.55);
					ctx.strokeStyle = COULEURS[c];
					ctx.lineWidth = Math.max(0.8, taille * 0.9);
					ctx.beginPath();
					ctx.moveTo(x - (x - e0[0]) * longueur, y - (y - e0[1]) * longueur);
					ctx.lineTo(x, y);
					ctx.stroke();
				}
			}
			const r = taille * 3.2;
			ctx.globalAlpha = Math.min(1, alpha * opacite);
			ctx.drawImage(sprites[c], x - r, y - r, r * 2, r * 2);
		}
		ctx.globalAlpha = 1;
		ctx.globalCompositeOperation = 'source-over';
	}, [t, opacite, sprites]);
	return <canvas ref={ref} width={LARGEUR} height={HAUTEUR} style={{position: 'absolute', inset: 0}} />;
};
