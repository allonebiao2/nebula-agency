/**
 * LE FOND D'ESPACE : une encre (jamais du noir), trois nuages de nébuleuse qui
 * dérivent, quatre cents étoiles qui scintillent, et le vignetage qui tient le
 * regard au centre. Le fond s'éclaire quand la nébuleuse explose.
 */
import React, {useLayoutEffect, useRef} from 'react';
import {C, CENTRE, HAUTEUR, LARGEUR, T} from './donnees';
import {bruit, h, p} from './outils';

const ETOILES = 420;

const Ciel: React.FC<{t: number}> = ({t}) => {
	const ref = useRef<HTMLCanvasElement>(null);
	useLayoutEffect(() => {
		const ctx = ref.current?.getContext('2d');
		if (!ctx) return;
		ctx.clearRect(0, 0, LARGEUR, HAUTEUR);
		for (let i = 0; i < ETOILES; i++) {
			const x = h(i, 30) * LARGEUR;
			const y = (((h(i, 31) * HAUTEUR - t * (2 + 6 * h(i, 32))) % HAUTEUR) + HAUTEUR) % HAUTEUR;
			const r = 0.4 + 1.5 * h(i, 33) ** 3;
			const scintille = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * (1.2 + 3 * h(i, 34)) + h(i, 35) * 6.3));
			ctx.globalAlpha = Math.min(1, (0.25 + 0.75 * h(i, 36)) * scintille);
			ctx.fillStyle = h(i, 37) < 0.2 ? C.cyan : h(i, 37) < 0.35 ? C.mauve : C.etoile;
			ctx.beginPath();
			ctx.arc(x, y, r, 0, Math.PI * 2);
			ctx.fill();
		}
		ctx.globalAlpha = 1;
	}, [t]);
	return <canvas ref={ref} width={LARGEUR} height={HAUTEUR} style={{position: 'absolute', inset: 0}} />;
};

/** Un nuage de nébuleuse : un grand dégradé qui dérive et respire. */
const Nuage: React.FC<{t: number; x: number; y: number; r: number; couleur: string; graine: number; force: number}> = ({t, x, y, r, couleur, graine, force}) => {
	const dx = (bruit(t * 0.12, graine) - 0.5) * 120;
	const dy = (bruit(t * 0.1, graine + 5) - 0.5) * 120;
	const souffle = 0.85 + 0.3 * bruit(t * 0.25, graine + 9);
	return (
		<div
			style={{
				position: 'absolute',
				left: x - r + dx,
				top: y - r + dy,
				width: r * 2,
				height: r * 2,
				borderRadius: '50%',
				background: `radial-gradient(circle, ${couleur} 0%, transparent 68%)`,
				opacity: force * souffle,
				mixBlendMode: 'screen',
			}}
		/>
	);
};

export const Univers: React.FC<{t: number}> = ({t}) => {
	// avant l'explosion : presque rien ; après : la nébuleuse est là
	const allume = 0.25 + 0.75 * p(t, T.bang - 0.05, T.bang + 1.2);
	return (
		<div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					background: `radial-gradient(circle at ${CENTRE.x}px ${CENTRE.y}px, ${C.nuit2} 0%, ${C.nuit} 38%, ${C.encre} 78%)`,
				}}
			/>
			<Nuage t={t} x={260} y={560} r={720} couleur="rgba(107,63,242,.55)" graine={1} force={0.55 * allume} />
			<Nuage t={t} x={860} y={1180} r={780} couleur="rgba(47,107,255,.5)" graine={2} force={0.5 * allume} />
			<Nuage t={t} x={540} y={880} r={520} couleur="rgba(168,236,255,.28)" graine={3} force={0.45 * allume} />
			<Nuage t={t} x={180} y={1560} r={600} couleur="rgba(182,137,255,.35)" graine={4} force={0.35 * allume} />
			<Ciel t={t} />
			<div
				style={{
					position: 'absolute',
					inset: 0,
					background: 'radial-gradient(ellipse 75% 60% at 50% 46%, transparent 55%, rgba(2,2,8,.72) 100%)',
				}}
			/>
		</div>
	);
};
