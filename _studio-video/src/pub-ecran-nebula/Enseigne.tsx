/**
 * L'enseigne néon NEBULA AGENCY, dessinée comme dans `_outils/avatar_studio.py` (NEBULA violet, AGENCY cyan, Arial
 * Black en tubes au cœur clair), en trois couches préparées par `_outils/pub_ecran_preparer.py` : le verre éteint,
 * le tube allumé, la lueur. Elle sert deux fois : à l'écran (la fin du film) et au mur de la pièce (la version TikTok).
 * Les niveaux viennent de `etat.ts` : chaque mot s'allume sur le mot dit.
 */
import React from 'react';
import {Img, staticFile} from 'remotion';
import {niveauLueur, niveauTube} from './etat';

/** Les mesures des PNG (écrites par le préparateur dans `neon.json`, toile de 2600 x 1500, NEBULA haut de 220 px). */
const TOILE = {l: 2600, h: 1500};
const NEBULA = {x: 651, y: 518, w: 1318, h: 212};
const AGENCY = {x: 822, y: 800, w: 954, h: 150};
const CENTRE = {x: TOILE.l / 2, y: (NEBULA.y + AGENCY.y + AGENCY.h) / 2};

const couche = (nom: string, k: number, opacite: number) =>
	opacite <= 0.001 ? null : (
		<Img
			src={staticFile(`pub-ecran-nebula/${nom}.png`)}
			style={{position: 'absolute', left: 0, top: 0, width: TOILE.l * k, height: TOILE.h * k, opacity: Math.min(1, opacite)}}
		/>
	);

/**
 * `largeur` : la largeur du mot NEBULA à l'image. L'enseigne est centrée sur le point (x, y).
 * `verre` : la visibilité du verre éteint (au mur, on le devine ; à l'écran, il n'y a que la lumière).
 */
export const Enseigne: React.FC<{t: number; x: number; y: number; largeur: number; verre?: number; force?: number}> = ({
	t,
	x,
	y,
	largeur,
	verre = 0,
	force = 1,
}) => {
	const k = largeur / NEBULA.w;
	const tn = niveauTube(t, 'nebula') * force;
	const ta = niveauTube(t, 'agency') * force;
	const ln = niveauLueur(t, 'nebula') * force;
	const la = niveauLueur(t, 'agency') * force;
	return (
		<div style={{position: 'absolute', left: x - CENTRE.x * k, top: y - CENTRE.y * k, width: TOILE.l * k, height: TOILE.h * k, pointerEvents: 'none'}}>
			{couche('neon-eteint', k, verre * (1 - 0.85 * Math.max(tn, ta)))}
			{couche('neon-halo-nebula', k, ln)}
			{couche('neon-halo-agency', k, la)}
			{couche('neon-tube-nebula', k, tn)}
			{couche('neon-tube-agency', k, ta)}
		</div>
	);
};

/** Pour poser la lumière de l'enseigne sur un mur : où sont les deux mots, par rapport au centre. */
export const ENSEIGNE_MOTS = {
	nebula: {dy: (NEBULA.y + NEBULA.h / 2 - CENTRE.y) / NEBULA.w, l: 1, h: NEBULA.h / NEBULA.w},
	agency: {dy: (AGENCY.y + AGENCY.h / 2 - CENTRE.y) / NEBULA.w, l: AGENCY.w / NEBULA.w, h: AGENCY.h / NEBULA.w},
};
