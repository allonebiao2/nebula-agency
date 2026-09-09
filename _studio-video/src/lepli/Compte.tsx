import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, LETTRE, SANS, SERIF} from './donnees';

/**
 * 3 · LE COMPTE · les chiffres qui roulent.
 *
 * Signature du produit : LES CHIFFRES ROULENT, AVEC UNE SORTIE QUI RALENTIT.
 *
 * C'est le détail qui fait qu'une lettre digitale n'est pas une carte de vœux
 * scannée : elle SAIT quelque chose. Le nombre n'est pas décoratif, il est
 * calculé depuis la date que l'acheteur a donnée.
 */
export const Compte: React.FC = () => {
	const frame = useCurrentFrame();

	return (
		<AbsoluteFill
			name="Le compte"
			style={{
				background: `radial-gradient(120% 90% at 50% 40%,${C.nuit2} 0%,${C.nuit} 62%)`,
				alignItems: 'center',
				justifyContent: 'center',
			}}
		>
			<Interactive.Div
				name="Le papier"
				style={{
					width: 920,
					padding: '110px 60px',
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 18,
					boxShadow: '0 60px 140px rgba(0,0,0,.55)',
					textAlign: 'center',
					opacity: interpolate(frame, [0, 12, 74, 90], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
					}),
				}}
			>
				<div style={{height: 1, background: 'rgba(36,29,43,.18)', marginBottom: 64}} />

				<Interactive.Div
					name="Le nombre"
					style={{
						fontFamily: SERIF,
						fontSize: 230,
						lineHeight: 1,
						color: C.cire,
						fontVariantNumeric: 'tabular-nums',
					}}
				>
					{Math.round(
						interpolate(frame, [6, 62], [0, LETTRE.compte], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						}),
					)}
				</Interactive.Div>

				<Interactive.Div
					name="Jours ensemble"
					style={{
						fontFamily: SANS,
						fontSize: 46,
						letterSpacing: '0.28em',
						textTransform: 'uppercase',
						color: C.gris,
						marginTop: 26,
						opacity: interpolate(frame, [30, 52], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{LETTRE.libelleCompte}
				</Interactive.Div>

				<div style={{height: 1, background: 'rgba(36,29,43,.18)', marginTop: 64}} />
			</Interactive.Div>
		</AbsoluteFill>
	);
};
