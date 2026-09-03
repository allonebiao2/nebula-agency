import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, SANS, SERIF} from './donnees';

/**
 * 6 · LA CARTE · le cachet se REFERME.
 *
 * Le plan d'ouverture brisait la cire ; celui-ci la reforme. C'est la même
 * signature jouée à l'envers, et c'est ce qui ferme la boucle : la vidéo finit
 * sur une enveloppe cachetée, donc sur une lettre qui n'a pas encore été
 * écrite. C'est exactement l'état où l'on veut laisser celui qui regarde.
 *
 * ⚠️ Les prix sont ceux de `minuit/creer.html` (2 000 F l'occasion la plus
 * demandée). Ils sont recopiés dans `donnees.ts`, nulle part ailleurs.
 */

/** Un éclat de cire qui REVIENT vers le centre et disparaît en se soudant. */
const EclatQuiRevient: React.FC<{depuisX: number; depuisY: number; rotation: number}> = ({
	depuisX,
	depuisY,
	rotation,
}) => {
	const frame = useCurrentFrame();

	return (
		<div
			style={{
				position: 'absolute',
				left: '50%',
				top: '50%',
				width: 84,
				height: 84,
				background: `radial-gradient(circle at 40% 34%,${C.cireClair},${C.cire} 70%)`,
				borderRadius: '46% 54% 38% 62%',
				opacity: interpolate(frame, [0, 8, 20, 27], [0, 1, 1, 0], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
				}),
				translate: `${interpolate(frame, [0, 27], [depuisX, -50], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}% ${interpolate(frame, [0, 27], [depuisY, -50], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}%`,
				rotate: `${interpolate(frame, [0, 27], [rotation, 0], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}deg`,
			}}
		/>
	);
};

export const Fin: React.FC = () => {
	const frame = useCurrentFrame();

	return (
		<AbsoluteFill
			name="La carte"
			style={{
				background: `radial-gradient(120% 90% at 50% 42%,${C.nuit2} 0%,${C.nuit} 62%)`,
				flexDirection: 'column',
				alignItems: 'center',
				justifyContent: 'center',
				gap: 46,
			}}
		>
			<Interactive.Div
				name="Le cachet refermé"
				style={{
					position: 'relative',
					width: 210,
					height: 210,
					opacity: interpolate(frame, [0, 6, 108, 120], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
					}),
				}}
			>
				<EclatQuiRevient depuisX={-190} depuisY={40} rotation={-58} />
				<EclatQuiRevient depuisX={90} depuisY={70} rotation={46} />
				<EclatQuiRevient depuisX={-30} depuisY={-160} rotation={18} />

				<Interactive.Div
					name="Le sceau"
					style={{
						position: 'absolute',
						inset: 0,
						borderRadius: '50%',
						display: 'grid',
						placeItems: 'center',
						background: `radial-gradient(circle at 34% 30%,${C.cireClair},${C.cire} 62%,#6d1f27 100%)`,
						boxShadow: '0 20px 50px rgba(0,0,0,.5),0 2px 0 rgba(255,255,255,.28) inset',
						color: C.papier,
						fontFamily: SERIF,
						fontSize: 70,
						opacity: interpolate(frame, [22, 34], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
						scale: interpolate(frame, [22, 40], [0.82, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						}),
					}}
				>
					<div
						style={{
							position: 'absolute',
							inset: 13,
							borderRadius: '50%',
							border: '2px dashed rgba(244,237,224,.42)',
						}}
					/>
					M
				</Interactive.Div>
			</Interactive.Div>

			<Interactive.Div
				name="MINUIT"
				style={{
					fontFamily: SANS,
					fontSize: 104,
					fontWeight: 800,
					letterSpacing: '0.22em',
					color: C.papier,
					marginLeft: '0.22em',
					opacity: interpolate(frame, [34, 54, 108, 120], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				MINUIT
			</Interactive.Div>

			<Interactive.Div
				name="La promesse"
				style={{
					fontFamily: SANS,
					fontSize: 46,
					lineHeight: 1.5,
					color: C.gris,
					textAlign: 'center',
					maxWidth: 820,
					opacity: interpolate(frame, [48, 68, 108, 120], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				Une lettre, une enveloppe, un cachet.
				<br />
				En cinq minutes.
			</Interactive.Div>

			<Interactive.Div
				name="Le prix"
				style={{
					fontFamily: SANS,
					fontSize: 56,
					fontWeight: 700,
					color: C.orDoux,
					marginTop: 18,
					opacity: interpolate(frame, [62, 82, 108, 120], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				dès 2 000 F
			</Interactive.Div>

			<Interactive.Div
				name="L'adresse"
				style={{
					fontFamily: SANS,
					fontSize: 40,
					letterSpacing: '0.06em',
					color: C.gris,
					opacity: interpolate(frame, [74, 94, 108, 120], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				nebula-agency.online/minuit
			</Interactive.Div>
		</AbsoluteFill>
	);
};
