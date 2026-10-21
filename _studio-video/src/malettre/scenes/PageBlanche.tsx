import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, ECRAN, type Langue} from '../donnees';
import {Encre, grand, mix, p} from '../outils';

/**
 * 0 · LA PAGE BLANCHE (coupe B) · « Tu ne sais pas quoi écrire ? »
 *
 * Le vrai frein d'une lettre n'est pas le prix, c'est la page blanche (commentaire
 * de `creer.html`). Signature : une feuille vide où le curseur clignote, et rien ne
 * vient. Le plan suivant, la plume, y répond.
 */
export const PageBlanche: React.FC<{t: number; d: number; langue: Langue}> = ({t, d, langue}) => {
	const sortie = 1 - p(t, d - 0.25, d);
	const feuille = p(t, 0.1, 0.55);
	const curseur = Math.floor(t * 2.2) % 2 === 0;

	return (
		<AbsoluteFill style={{opacity: sortie}}>
			<Encre t={t} a={0.25} style={{...grand, position: 'absolute', top: 280, width: '100%', padding: '0 80px', boxSizing: 'border-box'}}>
				{ECRAN[langue].pageBlanche}
			</Encre>
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: 640,
					width: 760,
					height: 920,
					translate: `-50% ${mix(60, 0, feuille)}px`,
					opacity: feuille,
					rotate: '-1.5deg',
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 18,
					boxShadow: '0 60px 140px rgba(0,0,0,.55)',
				}}
			>
				<div style={{position: 'absolute', left: 90, top: 120, width: 5, height: 70, background: C.encre, opacity: curseur ? 0.85 : 0}} />
			</div>
		</AbsoluteFill>
	);
};
