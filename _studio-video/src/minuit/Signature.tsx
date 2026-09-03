import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, LETTRE, SANS, SERIF} from './donnees';

/**
 * 4 · LA SIGNATURE · le trait qui s'écrit.
 *
 * Signature du produit : LE TRAIT S'ÉCRIT (`stroke-dashoffset`), il n'apparaît
 * pas. C'est le dernier geste de celui qui écrit, et le seul endroit de la
 * lettre où l'on voit une main.
 *
 * ⚠️ Le tracé porte `pathLength={1}` : le trait se mesure alors en fraction,
 * de 1 (rien d'écrit) à 0 (fini), sans avoir à connaître sa longueur réelle en
 * pixels. Changer la courbe du trait ne casse donc pas l'animation.
 */
export const Signature: React.FC = () => {
	const frame = useCurrentFrame();

	return (
		<AbsoluteFill
			name="La signature"
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
					padding: '110px 60px 130px',
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 18,
					boxShadow: '0 60px 140px rgba(0,0,0,.55)',
					textAlign: 'right',
					opacity: interpolate(frame, [0, 12, 74, 90], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
					}),
				}}
			>
				<Interactive.Div
					name="Formule de politesse"
					style={{
						fontFamily: SANS,
						fontSize: 46,
						color: C.gris,
						opacity: interpolate(frame, [4, 24], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{LETTRE.formule}
				</Interactive.Div>

				<Interactive.Div
					name="Le nom"
					style={{
						fontFamily: SERIF,
						fontStyle: 'italic',
						fontSize: 104,
						lineHeight: 1.2,
						color: C.encre,
						marginTop: 18,
						opacity: interpolate(frame, [18, 38], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{LETTRE.signature}
				</Interactive.Div>

				<svg
					viewBox="0 0 300 26"
					style={{width: 400, height: 35, marginTop: 6, display: 'inline-block'}}
				>
					<Interactive.Path
						name="Le trait"
						d="M6 18 C 58 4, 104 24, 158 12 S 246 3, 294 14"
						fill="none"
						stroke={C.or}
						strokeWidth={5}
						strokeLinecap="round"
						pathLength={1}
						strokeDasharray={1}
						strokeDashoffset={interpolate(frame, [34, 68], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						})}
					/>
				</svg>
			</Interactive.Div>
		</AbsoluteFill>
	);
};
