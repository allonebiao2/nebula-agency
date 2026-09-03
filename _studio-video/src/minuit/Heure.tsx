import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, SANS, SERIF} from './donnees';

/**
 * 5 · L'HEURE DITE · le cadran qui monte à minuit.
 *
 * C'est le plan qui vend. Tout le reste (le cachet, le pli, l'encre) existe
 * ailleurs sous une forme ou une autre ; l'heure choisie, non. C'est elle qui
 * donne son nom au produit.
 *
 * La signature est neuve mais sort du même objet : le cadran reprend le cercle
 * et le pointillé DU CACHET, et l'aiguille remplace la cire. Rien n'est
 * emprunté à un autre métier.
 *
 * ⚠️ L'aiguille et l'arc partagent la MÊME courbe et la MÊME durée : deux
 * horloges pour un seul geste, c'est ce qui fait dire « ça bugue ».
 */
export const Heure: React.FC = () => {
	const frame = useCurrentFrame();

	return (
		<AbsoluteFill
			name="L'heure dite"
			style={{
				background: `radial-gradient(120% 90% at 50% 40%,${C.nuit2} 0%,${C.nuit} 62%)`,
				flexDirection: 'column',
				alignItems: 'center',
				justifyContent: 'center',
				gap: 76,
			}}
		>
			<Interactive.Div
				name="Le cadran"
				style={{
					position: 'relative',
					width: 460,
					height: 460,
					opacity: interpolate(frame, [0, 14, 160, 180], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
					}),
					scale: interpolate(frame, [0, 18], [0.9, 1], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				<svg viewBox="0 0 100 100" style={{position: 'absolute', inset: 0, rotate: '-90deg'}}>
					{/* Le pointillé du cachet, repris tel quel : c'est le même objet. */}
					<circle cx="50" cy="50" r="46" fill="none" stroke="rgba(109,100,120,.38)" strokeWidth="0.7" strokeDasharray="2 3" />
					<Interactive.Circle
						name="L'arc qui se remplit"
						cx="50"
						cy="50"
						r="46"
						fill="none"
						stroke={C.or}
						strokeWidth="2.4"
						strokeLinecap="round"
						pathLength={1}
						strokeDasharray={1}
						strokeDashoffset={interpolate(frame, [8, 72], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						})}
					/>
				</svg>

				<Interactive.Div
					name="L'aiguille"
					style={{
						position: 'absolute',
						left: '50%',
						bottom: '50%',
						width: 5,
						height: 150,
						marginLeft: -2.5,
						background: C.orDoux,
						borderRadius: 3,
						transformOrigin: '50% 100%',
						/* Elle s'efface au moment ou l'heure s'ecrit. Sans ca elle
						   traverse le « 00:00 » de part en part : mesure sur l'image
						   600, le trait passait pile entre les deux paires de zeros. */
						opacity: interpolate(frame, [68, 82], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
						rotate: `${interpolate(frame, [8, 72], [0, 360], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						})}deg`,
					}}
				/>

				<Interactive.Div
					name="Minuit"
					style={{
						position: 'absolute',
						inset: 0,
						display: 'grid',
						placeItems: 'center',
						fontFamily: SERIF,
						fontSize: 92,
						color: C.papier,
						letterSpacing: '0.04em',
						opacity: interpolate(frame, [68, 88], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					00:00
				</Interactive.Div>
			</Interactive.Div>

			<Interactive.Div
				name="Tu choisis l'heure"
				style={{
					fontFamily: SERIF,
					fontSize: 88,
					color: C.papier,
					textAlign: 'center',
					opacity: interpolate(frame, [76, 96, 158, 180], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
					translate: `0px ${interpolate(frame, [76, 96], [22, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					})}px`,
				}}
			>
				Tu choisis l'heure.
			</Interactive.Div>

			<Interactive.Div
				name="Pas avant"
				style={{
					fontFamily: SANS,
					fontSize: 46,
					color: C.gris,
					textAlign: 'center',
					marginTop: -44,
					opacity: interpolate(frame, [92, 112, 158, 180], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				Elle l'ouvre à minuit pile. Pas avant.
			</Interactive.Div>
		</AbsoluteFill>
	);
};
