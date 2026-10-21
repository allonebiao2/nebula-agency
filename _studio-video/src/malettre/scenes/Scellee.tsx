import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, ECRAN, HISTOIRE, SANS, type Langue} from '../donnees';
import {Cachet, Encre, Enveloppe, grand, mix, p} from '../outils';

/**
 * 2 · SCELLÉE · « Une lettre qui reste scellée jusqu'à l'heure que tu choisis. »
 *
 * Signature : LA CIRE QU'ON PRESSE. Le cachet tombe sur le rabat, s'écrase un peu
 * (la cire est molle), puis se pose et respire. Le mot « Scellée » sèche au même
 * instant : c'est le geste qui le dit. Sous l'enveloppe, la phrase EXACTE que la
 * lettre affiche quand elle est encore fermée.
 */
export const Scellee: React.FC<{t: number; d: number; langue: Langue}> = ({t, d, langue}) => {
	const E = ECRAN[langue];
	const L = HISTOIRE[langue];
	const sortie = 1 - p(t, d - 0.3, d);
	const pose = 0.55;
	const chute = p(t, 0.2, pose);
	/* L'écrasement : la cire s'étale de 12 % puis revient. */
	const ecrase = t < pose ? 1.25 - 0.25 * chute : 1 + 0.12 * Math.max(0, 1 - (t - pose) / 0.22) * Math.sin(Math.min(1, (t - pose) / 0.22) * Math.PI);

	return (
		<AbsoluteFill style={{opacity: sortie}}>
			<div style={{position: 'absolute', top: 300, width: '100%'}}>
				<Encre t={t} a={pose} duree={0.45} style={{...grand, fontSize: 132}}>
					{E.scellee[0]}
				</Encre>
				<Encre t={t} a={pose + 0.25} style={{...grand, fontSize: 64, color: C.grisNuit, marginTop: 14}}>
					{E.scellee[1]}
				</Encre>
			</div>

			<div style={{position: 'absolute', left: '50%', top: 820, translate: '-50% 0%', opacity: p(t, 0, 0.3)}}>
				<Enveloppe h={HISTOIRE.habillage} largeur={780} t={t} sansCachet>
					<div style={{position: 'absolute', left: '50%', top: '52%', translate: `-50% ${mix(-260, -50, chute)}%`, opacity: p(t, 0.15, 0.3)}}>
						<Cachet h={HISTOIRE.habillage} taille={195} t={t} style={{scale: `${ecrase} ${2 - ecrase}`}} />
					</div>
				</Enveloppe>
			</div>

			<Encre t={t} a={pose + 0.6} style={{position: 'absolute', top: 1380, width: '100%', fontFamily: SANS, fontSize: 44, color: C.grisNuit, textAlign: 'center'}}>
				{L.ouvre[0]}
				<b style={{color: C.papier, fontWeight: 600}}>{L.ouvre[1]}</b>
				{L.ouvre[2]}
			</Encre>
		</AbsoluteFill>
	);
};
