import React from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame} from 'remotion';
import {C, LETTRE, SANS, SERIF} from './donnees';

/**
 * 2 · LE PLI, PUIS L'ENCRE · la lettre elle-même.
 *
 * Deux signatures du produit dans le même plan, parce qu'elles ne se séparent
 * pas à l'œil : LE DÉPLIAGE (la feuille s'ouvre, ses deux plis s'effacent),
 * puis L'ENCRE QUI SÈCHE (flou vers net, ligne après ligne).
 *
 * ⚠️ Le séchage part du HAUT et descend, au rythme d'une lecture. C'est ce
 * qui fait qu'on lit la lettre au lieu de la survoler : la vidéo impose le
 * tempo que la destinataire aura de toute façon.
 */

/** Première image du séchage de l'encre, une fois la feuille dépliée. */
const ENCRE = 34;

/** Le décalage d'une ligne à la suivante. Plus court, ça bégaie ; plus long, ça traîne. */
const PAS = 8;

/** Le flou de départ, en pixels : de l'encre fraîche qui n'a pas encore pris. */
const FLOU = 9;

export const Lettre: React.FC = () => {
	const frame = useCurrentFrame();

	/* Les lignes vides sont des blancs de paragraphe : elles n'ont pas d'encre
	   à sécher, donc elles ne comptent pas dans le décalage. */
	let rang = 0;

	return (
		<AbsoluteFill
			name="La lettre"
			style={{
				background: `radial-gradient(120% 90% at 50% 40%,${C.nuit2} 0%,${C.nuit} 62%)`,
				alignItems: 'center',
				justifyContent: 'center',
			}}
		>
			<Interactive.Div
				name="La feuille"
				style={{
					position: 'relative',
					width: 920,
					height: 1240,
					padding: '64px 60px',
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 18,
					boxShadow: '0 60px 140px rgba(0,0,0,.55)',
					textAlign: 'center',
					/* Le dépliage : la feuille s'ouvre depuis son pli central. */
					scale: `1 ${interpolate(frame, [4, 30], [0.04, 1], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
						easing: Easing.bezier(0.25, 1, 0.5, 1),
					})}`,
					opacity: interpolate(frame, [0, 10, 238, 255], [0, 1, 1, 0], {
						extrapolateLeft: 'clamp',
						extrapolateRight: 'clamp',
					}),
				}}
			>
				{/* Les deux plis, qui s'effacent une fois la feuille à plat. */}
				<div
					style={{
						position: 'absolute',
						left: 0,
						right: 0,
						top: '33.3%',
						height: 2,
						background: C.pli,
						opacity: interpolate(frame, [26, 52], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				/>
				<div
					style={{
						position: 'absolute',
						left: 0,
						right: 0,
						top: '66.6%',
						height: 2,
						background: C.pli,
						opacity: interpolate(frame, [26, 52], [1, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				/>

				<Interactive.Div
					name="Occasion"
					style={{
						fontFamily: SANS,
						fontSize: 44,
						fontWeight: 700,
						letterSpacing: '0.26em',
						textTransform: 'uppercase',
						color: C.cire,
						filter: `blur(${interpolate(frame, [ENCRE, ENCRE + 20], [FLOU, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						})}px)`,
						opacity: interpolate(frame, [ENCRE, ENCRE + 20], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{LETTRE.occasion}
				</Interactive.Div>

				<Interactive.Div
					name="Titre de la lettre"
					style={{
						fontFamily: SERIF,
						fontSize: 84,
						lineHeight: 1.18,
						color: C.encre,
						marginTop: 26,
						filter: `blur(${interpolate(frame, [ENCRE + 8, ENCRE + 28], [FLOU, 0], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						})}px)`,
						opacity: interpolate(frame, [ENCRE + 8, ENCRE + 28], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{LETTRE.titre}
				</Interactive.Div>

				<Interactive.Div
					name="Filet doré"
					style={{
						width: 132,
						height: 5,
						margin: '30px auto 54px',
						background: C.or,
						borderRadius: 3,
						/* Le filet ne sèche pas, il se TIRE : c'est un trait de plume. */
						scale: `${interpolate(frame, [ENCRE + 20, ENCRE + 38], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.bezier(0.25, 1, 0.5, 1),
						})} 1`,
					}}
				/>

				<div style={{textAlign: 'left'}}>
					{LETTRE.lignes.map((ligne, i) => {
						if (ligne === '') {
							return <div key={i} style={{height: 40}} />;
						}
						const depart = ENCRE + 28 + rang * PAS;
						rang += 1;

						return (
							<div
								key={i}
								style={{
									fontFamily: SERIF,
									fontSize: 50,
									lineHeight: 1.62,
									color: C.encre,
									filter: `blur(${interpolate(frame, [depart, depart + 20], [FLOU, 0], {
										extrapolateLeft: 'clamp',
										extrapolateRight: 'clamp',
									})}px)`,
									opacity: interpolate(frame, [depart, depart + 20], [0, 1], {
										extrapolateLeft: 'clamp',
										extrapolateRight: 'clamp',
									}),
								}}
							>
								{ligne}
							</div>
						);
					})}
				</div>
			</Interactive.Div>
		</AbsoluteFill>
	);
};
