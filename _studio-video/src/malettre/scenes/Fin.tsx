import React from 'react';
import {AbsoluteFill} from 'remotion';
import {ADRESSE, C, CIRES, ECRAN, SANS, SERIF, type Langue} from '../donnees';
import {Encre, mix, p} from '../outils';

/**
 * 7 · LA MARQUE · « Ma lettre à… Gratuite pour commencer. » (ou, coupe B, « La plume,
 * cinq cents francs de plus. »)
 *
 * Signature : LE CACHET SE REFORME. Les trois éclats du plan d'ouverture reviennent
 * au centre et se soudent en un cachet, celui de la marque (cire bordeaux et « M »,
 * le favicon du produit). La vidéo finit sur une lettre fermée, donc sur une lettre
 * qui n'a pas encore été écrite : c'est l'état où l'on veut laisser celui qui regarde.
 *
 * ⛔ L'adresse est la seule chose qu'on doit pouvoir recopier : elle reste au-dessus
 * de la bande basse où TikTok et Reels posent leurs boutons.
 */
const RETOURS = [
	{x: -420, y: 120, r: -58},
	{x: 300, y: 260, r: 46},
	{x: -60, y: -420, r: 18},
];

export const Fin: React.FC<{t: number; fin: 'prix' | 'plume'; langue: Langue}> = ({t, fin, langue}) => {
	const E = ECRAN[langue];
	const c = CIRES.bordeaux;
	const soude = p(t, 0.05, 0.6);
	const cachet = p(t, 0.5, 0.7);

	return (
		<AbsoluteFill style={{opacity: p(t, 0, 0.15)}}>
			<div style={{position: 'absolute', left: '50%', top: 560, width: 250, height: 250, translate: '-50% 0'}}>
				{RETOURS.map((e, i) => (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: '50%',
							top: '50%',
							width: 96,
							height: 96,
							background: `radial-gradient(circle at 40% 34%,${c.clair},${c.cire} 70%)`,
							clipPath: 'polygon(48% 0%, 100% 34%, 80% 100%, 14% 84%, 0% 28%)',
							translate: `${mix(e.x, -50, soude)}% ${mix(e.y, -50, soude)}%`,
							rotate: `${mix(e.r, 0, soude)}deg`,
							opacity: Math.min(p(t, 0, 0.1), 1 - cachet),
						}}
					/>
				))}
				<div
					style={{
						position: 'absolute',
						inset: 0,
						borderRadius: '50%',
						display: 'grid',
						placeItems: 'center',
						background: `radial-gradient(circle at 34% 30%,${c.clair},${c.cire} 62%,${c.fonce} 100%)`,
						boxShadow: '0 24px 60px rgba(0,0,0,.5),0 2px 0 rgba(255,255,255,.28) inset',
						fontFamily: SERIF,
						fontSize: 118,
						color: '#f0d6cf',
						opacity: cachet,
						scale: String(mix(0.86, 1, cachet) * (1 + 0.03 * Math.sin((t / 3.4) * Math.PI * 2))),
					}}
				>
					M
				</div>
			</div>

			<Encre t={t} a={0.55} style={{position: 'absolute', top: 880, width: '100%', fontFamily: SERIF, fontSize: 132, color: C.papier, textAlign: 'center'}}>
				{E.marque}
			</Encre>
			<Encre t={t} a={0.85} style={{position: 'absolute', top: 1070, width: '100%', fontFamily: SANS, fontSize: 52, fontWeight: 600, color: C.orDoux, textAlign: 'center'}}>
				{fin === 'plume' ? E.plumePrix : E.prix}
			</Encre>
			<Encre t={t} a={1.05} style={{position: 'absolute', top: 1250, width: '100%', fontFamily: SANS, fontSize: 46, color: C.papier, textAlign: 'center', letterSpacing: '0.01em'}}>
				{ADRESSE}
			</Encre>
			<Encre t={t} a={1.2} style={{position: 'absolute', top: 1330, width: '100%', fontFamily: SANS, fontSize: 32, color: C.grisNuit, textAlign: 'center', letterSpacing: '0.14em'}}>
				{E.par}
			</Encre>
		</AbsoluteFill>
	);
};
