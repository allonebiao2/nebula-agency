/**
 * 1 · L'ACCROCHE (0 → 2,3 s) : un client écrit « C'est combien ? », l'heure file,
 * personne ne répond… « Ton client est parti. » Tout se joue avant 2 s.
 */
import React from 'react';
import {AbsoluteFill, Easing, interpolate} from 'remotion';
import {C, T} from './donnees';
import {Bulle, CL, Horloge, lin, ressort, secousse} from './outils';
import {MONO, TEXTE, TITRE} from './polices';

export const Accroche: React.FC<{t: number}> = ({t}) => {
	if (t > T.conseil + 0.05) return null;
	const sortie = lin(t, T.conseil - 0.18, T.conseil, 0, 1, Easing.in(Easing.cubic));
	const chute = lin(t, T.parti - 0.04, T.parti + 0.42, 0, 1, Easing.in(Easing.quad));
	const sb = ressort(t, T.bulle, 260, 15);
	const sa = ressort(t, T.attente, 200, 16);

	// 21:04 → 22:51 en 0,7 s : l'heure file, personne ne répond
	const minutes = 21 * 60 + 4 + Math.round(interpolate(t, [T.attente, T.parti], [0, 107], CL));
	const heure = `${Math.floor(minutes / 60)}:${String(minutes % 60).padStart(2, '0')}`;

	const slam = t >= T.parti ? lin(t, T.parti, T.parti + 0.13, 0, 1, Easing.out(Easing.quad)) : 0;

	return (
		<AbsoluteFill style={{opacity: 1 - sortie, transform: `${secousse(t, [[T.parti, 22]])} scale(${(1 + sortie * 0.25).toFixed(3)})`}}>
			<div
				style={{
					position: 'absolute',
					top: 560,
					left: 0,
					right: 0,
					textAlign: 'center',
					fontFamily: TEXTE,
					fontWeight: 600,
					fontSize: 42,
					color: C.lavande,
					opacity: Math.min(1, sb * 1.6) * (1 - chute),
				}}
			>
				Un client t’écrit :
			</div>

			<div
				style={{
					position: 'absolute',
					top: 650,
					left: 0,
					right: 0,
					display: 'flex',
					justifyContent: 'center',
					opacity: Math.min(1, sb * 1.6) * (1 - chute),
					transform: `translateY(${(chute * 340).toFixed(1)}px) rotate(${(chute * 9).toFixed(2)}deg) scale(${(0.5 + 0.5 * sb).toFixed(3)})`,
				}}
			>
				<Bulle texte="C’est combien ?" heure="21:04" taille={66} />
			</div>

			<div
				style={{
					position: 'absolute',
					top: 860,
					left: 0,
					right: 0,
					display: 'flex',
					justifyContent: 'center',
					alignItems: 'center',
					gap: 18,
					opacity: Math.min(1, sa * 1.6) * (1 - chute),
					transform: `translateY(${((1 - sa) * 30 + chute * 260).toFixed(1)}px)`,
				}}
			>
				<Horloge t={t} taille={54} couleur={C.pervenche} />
				<span style={{fontFamily: MONO, fontWeight: 700, fontSize: 50, color: C.lumiere}}>{heure}</span>
				<span style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 38, color: C.gris}}>pas de réponse…</span>
			</div>

			{slam > 0 ? (
				<div
					style={{
						position: 'absolute',
						top: 690,
						left: 0,
						right: 0,
						textAlign: 'center',
						fontFamily: TITRE,
						fontWeight: 800,
						fontSize: 116,
						lineHeight: 1.04,
						color: C.lumiere,
						opacity: slam,
						transform: `scale(${(1.9 - 0.9 * slam).toFixed(3)})`,
						textShadow: '0 10px 60px rgba(6,7,19,.8)',
					}}
				>
					Ton client
					<br />
					<span style={{color: C.rouge}}>est parti.</span>
				</div>
			) : null}
		</AbsoluteFill>
	);
};
