/**
 * TIKTOK DU 20/11/2026 · « les deux conseils du jour » (28 s, 1080 x 1920, 30 i/s).
 * Le montage : l'espace en fond, les quatre temps posés par-dessus, l'éclair
 * des chocs, le vignettage, et les bruitages. Toutes les scènes lisent `t`.
 * Rendu : `npm run rendu:tiktok1120` (UN onglet).
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Accroche} from './Accroche';
import {Bruitages} from './Bruitages';
import {Conseil} from './Conseil';
import {FPS, T} from './donnees';
import {Fin} from './Fin';
import {Lecon, LourdLeger} from './Lecon';
import {eclair, Espace} from './outils';

export const Tiktok2011: React.FC = () => {
	const t = useCurrentFrame() / FPS;
	const blanc = eclair(t, [
		[T.parti, 0.35],
		[T.trois, 0.3],
		[T.mo, 0.45],
		[T.lourd, 0.7],
		[T.offre - 0.05, 0.9],
		[T.logo, 0.4],
	]);
	return (
		<AbsoluteFill style={{background: '#060713', overflow: 'hidden'}}>
			<Espace t={t} />
			<Accroche t={t} />
			<Conseil t={t} />
			<Lecon t={t} />
			<LourdLeger t={t} />
			<Fin t={t} />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(3,3,10,.55) 100%)', pointerEvents: 'none'}} />
			{blanc > 0 ? <AbsoluteFill style={{background: '#eef0ff', opacity: blanc, pointerEvents: 'none'}} /> : null}
			<Bruitages />
		</AbsoluteFill>
	);
};
