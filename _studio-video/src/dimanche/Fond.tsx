/**
 * LE FOND · la vidéo préparée, et ce que la caméra aurait dû faire.
 *
 * Un plan fixe de 3 min 29, sans une coupe : on lui donne des POUSSÉES sur le
 * visage aux mots forts, un TREMBLEMENT au seul moment où il décrit le trader
 * qui « saute dessus », et une OMBRE sous chaque grand graphique.
 * L'origine du zoom est son visage (50 % / 15 %), pas le centre de l'image.
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, random, staticFile} from 'remotion';
import {DEBUT_FIN, FPS, OMBRES, POUSSEES, d, fi} from './donnees';
import {p} from './outils';

const poussee = (t: number) =>
	POUSSEES.reduce((max, [a, force]) => {
		if (t < a || t > a + 2.6) return max;
		const monte = p(t, a, a + 0.28);
		const redescend = 1 - p(t, a + 1.5, a + 2.6, Easing.inOut(Easing.cubic));
		return Math.max(max, force * monte * redescend);
	}, 0);

const ombre = (t: number) =>
	OMBRES.reduce((max, [a, b, niveau]) => Math.max(max, niveau * p(t, a, a + 0.3) * (1 - p(t, b, b + 0.4))), 0);

/** « je saute dessus » : l'image tressaute, une demi-seconde, puis se calme. */
const DEBUT_SAUT = d(425);
const FIN_SAUT = fi(427) + 0.25;

export const Fond: React.FC<{t: number; frame: number}> = ({t, frame}) => {
	const z = 1 + poussee(t);
	const k = t >= DEBUT_SAUT && t <= FIN_SAUT ? interpolate(t, [DEBUT_SAUT, FIN_SAUT], [1, 0]) : 0;
	const dx = k * (random(`x${frame}`) - 0.5) * 22;
	const dy = k * (random(`y${frame}`) - 0.5) * 16;
	const rot = k * (random(`r${frame}`) - 0.5) * 1.6;
	const fin = p(t, DEBUT_FIN, DEBUT_FIN + 0.6);

	return (
		<AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#0b0d12'}}>
			<AbsoluteFill
				style={{
					transformOrigin: '50% 15%',
					transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg) scale(${z})`,
					filter: fin > 0 ? `blur(${fin * 18}px)` : undefined,
				}}
			>
				{frame < Math.round(DEBUT_FIN * FPS) + 8 ? (
					<OffthreadVideo src={staticFile('dimanche/image.mp4')} muted style={{width: '100%', height: '100%'}} />
				) : (
					<Img src={staticFile('dimanche/derniere.jpg')} style={{width: '100%', height: '100%'}} />
				)}
			</AbsoluteFill>
			{/* vignette permanente, et le bas (bureau vide) un peu plus sombre pour les feuilles */}
			<AbsoluteFill
				style={{
					background:
						'radial-gradient(120% 80% at 50% 30%, rgba(0,0,0,0) 55%, rgba(0,0,0,.38) 100%), linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(0,0,0,.32) 100%)',
				}}
			/>
			<AbsoluteFill style={{backgroundColor: '#07090d', opacity: Math.max(ombre(t), fin * 0.55)}} />
		</AbsoluteFill>
	);
};
