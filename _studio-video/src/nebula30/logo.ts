/**
 * Où tombe le logo dans l'image. Les couches (`couches.ts`) sont en pixels du
 * logo agrandi x2 ; on les réduit de LOGO.k et on centre le bloc en largeur.
 * Les particules, l'implosion et la signature lisent TOUTES ces mêmes positions.
 */
import {COUCHES} from './couches';
import {LARGEUR, LOGO} from './donnees';

const X0 = LARGEUR / 2 - (COUCHES.logo.w * LOGO.k) / 2;
const Y0 = LOGO.haut;

/** Un point du logo x2 → un point de l'image. */
export const enImage = (x: number, y: number): [number, number] => [X0 + (x - COUCHES.logo.x) * LOGO.k, Y0 + (y - COUCHES.logo.y) * LOGO.k];

/** Le cadre d'une couche dans l'image. */
export const cadre = (c: {x: number; y: number; w: number; h: number}) => {
	const [x, y] = enImage(c.x, c.y);
	return {left: x, top: y, width: c.w * LOGO.k, height: c.h * LOGO.k};
};

/** L'étoile du logo, dans l'image : là où tout s'effondre puis renaît. */
export const ETOILE = (() => {
	const [x, y] = enImage(COUCHES.etoile.x, COUCHES.etoile.y);
	return {x, y};
})();

/** Le bas du bloc logo (wordmark + AGENCY) : la signature se pose dessous. */
export const BAS_LOGO = enImage(0, COUCHES.logo.y + COUCHES.logo.h)[1];
