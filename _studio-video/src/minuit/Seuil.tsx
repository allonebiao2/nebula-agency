import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, LETTRE, SANS, SERIF} from './donnees';

/**
 * 1 · LE SEUIL · l'enveloppe fermée, le cachet de cire.
 *
 * Signature du produit : LE CACHET RESPIRE, PUIS SE BRISE en trois éclats.
 *
 * Le seuil EST le produit : il crée l'attente, rend la page privée, et surtout
 * il RÉUNIT un avant et un après, donc il se filme. Une démonstration de MINUIT
 * qui ne montrerait pas ce brisement ne montrerait rien.
 *
 * ⚠️ Le brisement est écrit ici en images (`useCurrentFrame`), pas en
 * `@keyframes` comme dans `lettre.html` : une animation CSS ne se rend pas,
 * elle joue à l'horloge du navigateur et le rendu la photographierait figée.
 */

/** L'image où le cachet cède. Tout le plan se lit par rapport à elle. */
const BRISEMENT = 104;

/**
 * Un éclat de cire, du centre du cachet vers sa fuite. Trajectoires reprises de
 * `lettre.html`.
 *
 * ⚠️ La forme est un POLYGONE, pas un `border-radius`. Le produit s'en sort
 * avec des coins arrondis parce que ses éclats sont minuscules et rapides ;
 * ici ils font 84 px et traversent l'écran, et arrondis ils ressemblaient à
 * trois pastilles roses. La cire se casse en morceaux à angles vifs.
 */
const Eclat: React.FC<{versX: number; versY: number; rotation: number; forme: string}> = ({
	versX,
	versY,
	rotation,
	forme,
}) => {
	const frame = useCurrentFrame();

	return (
		<div
			style={{
				position: 'absolute',
				left: '50%',
				top: '52%',
				width: 84,
				height: 84,
				background: `radial-gradient(circle at 40% 34%,${C.cireClair},${C.cire} 70%)`,
				clipPath: forme,
				zIndex: 4,
				/* ⚠️ Le premier palier vaut 0 : sans lui, `extrapolateLeft: 'clamp'`
				   tient l'éclat à pleine opacité DEPUIS LA PREMIÈRE IMAGE, et les
				   trois morceaux de cire se posent sur le cachet intact. */
				opacity: interpolate(
					frame,
					[BRISEMENT - 1, BRISEMENT, BRISEMENT + 26],
					[0, 1, 0],
					{extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
				),
				translate: `${interpolate(frame, [BRISEMENT, BRISEMENT + 26], [-50, versX], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}% ${interpolate(frame, [BRISEMENT, BRISEMENT + 26], [-50, versY], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}%`,
				rotate: `${interpolate(frame, [BRISEMENT, BRISEMENT + 26], [0, rotation], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.bezier(0.25, 1, 0.5, 1),
				})}deg`,
			}}
		/>
	);
};

export const Seuil: React.FC = () => {
	const frame = useCurrentFrame();

	return (
		<AbsoluteFill
			name="Le seuil"
			style={{
				background: `radial-gradient(120% 90% at 50% 40%,${C.nuit2} 0%,${C.nuit} 62%)`,
				flexDirection: 'column',
				alignItems: 'center',
				justifyContent: 'center',
				gap: 62,
			}}
		>
			<Interactive.Div
				name="Pour qui"
				style={{
					fontFamily: SANS,
					fontSize: 44,
					letterSpacing: '0.24em',
					textTransform: 'uppercase',
					color: C.gris,
					opacity: interpolate(frame, [6, 26, 140, 160], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
					translate: `0px ${interpolate(frame, [6, 26], [24, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					})}px`,
				}}
			>
				Pour <span style={{color: C.orDoux, fontWeight: 600}}>{LETTRE.pour}</span>
			</Interactive.Div>

			<Interactive.Div
				name="Enveloppe"
				style={{
					position: 'relative',
					width: 760,
					height: 469,
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 14,
					boxShadow: `0 60px 140px rgba(0,0,0,.55),0 4px 0 rgba(255,255,255,.35) inset`,
					opacity: interpolate(frame, [12, 40, 140, 162], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
					scale: interpolate(frame, [12, 40], [0.92, 1], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
					translate: `0px ${interpolate(frame, [12, 40], [40, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					})}px`,
				}}
			>
				{/* Le rabat est DESSINÉ, pas bricolé en carré tourné à 45° : c'est la
				    leçon de `lettre.html`, un triangle pivoté rendait deux coins
				    sombres en bas au lieu d'un V venu du haut. */}
				<svg
					viewBox="0 0 162 100"
					preserveAspectRatio="none"
					style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}
				>
					<path d="M0 0 L81 52 L162 0 Z" fill="rgba(36,29,43,.055)" />
					<path d="M0 0 L81 52 L162 0" fill="none" stroke="rgba(36,29,43,.16)" strokeWidth="0.5" />
					<path d="M0 100 L81 52" fill="none" stroke="rgba(36,29,43,.10)" strokeWidth="0.5" />
					<path d="M162 100 L81 52" fill="none" stroke="rgba(36,29,43,.10)" strokeWidth="0.5" />
				</svg>

				<Eclat versX={-190} versY={40} rotation={-58} forme="polygon(48% 0%, 100% 34%, 80% 100%, 14% 84%, 0% 28%)" />
				<Eclat versX={90} versY={70} rotation={46} forme="polygon(0% 14%, 84% 0%, 100% 60%, 42% 100%)" />
				<Eclat versX={-30} versY={-160} rotation={18} forme="polygon(20% 0%, 100% 22%, 74% 94%, 0% 66%)" />

				<Interactive.Div
					name="Cachet de cire"
					style={{
						position: 'absolute',
						left: '50%',
						top: '52%',
						width: 190,
						height: 190,
						borderRadius: '50%',
						display: 'grid',
						placeItems: 'center',
						zIndex: 3,
						background: `radial-gradient(circle at 34% 30%,${C.cireClair},${C.cire} 62%,#6d1f27 100%)`,
						boxShadow: '0 18px 44px rgba(0,0,0,.45),0 2px 0 rgba(255,255,255,.28) inset',
						color: C.papier,
						fontFamily: SERIF,
						fontSize: 62,
						letterSpacing: '0.06em',
						/* Il respire : 3,4 s par souffle, comme dans le produit. */
						opacity: interpolate(frame, [BRISEMENT, BRISEMENT + 5], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
						translate: '-50% -50%',
						scale: 1 + 0.045 * Math.sin((frame / 102) * Math.PI * 2),
					}}
				>
					<div
						style={{
							position: 'absolute',
							inset: 12,
							borderRadius: '50%',
							border: '2px dashed rgba(244,237,224,.42)',
						}}
					/>
					{LETTRE.initiale}
				</Interactive.Div>
			</Interactive.Div>

			<Interactive.Div
				name="Une lettre t'attend"
				style={{
					fontFamily: SANS,
					fontSize: 46,
					color: C.gris,
					letterSpacing: '0.05em',
					opacity: interpolate(frame, [34, 54, 134, 152], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				Une lettre t'attend.
			</Interactive.Div>

			<Interactive.Div
				name="Briser le cachet"
				style={{
					fontFamily: SANS,
					padding: '34px 76px',
					borderRadius: 999,
					background: C.papier,
					color: C.encre,
					fontWeight: 700,
					fontSize: 46,
					boxShadow: '0 24px 60px rgba(0,0,0,.4)',
					opacity: interpolate(frame, [42, 64, 128, 146], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
					/* On l'enfonce juste avant que la cire cède : c'est le geste de la
					   destinataire, et c'est lui qui rend le brisement lisible. */
					scale: interpolate(frame, [96, BRISEMENT, BRISEMENT + 10], [1, 0.955, 1], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					}),
				}}
			>
				Briser le cachet
			</Interactive.Div>
		</AbsoluteFill>
	);
};
