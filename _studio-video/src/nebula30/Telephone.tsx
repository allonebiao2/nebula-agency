/**
 * LE TÉLÉPHONE : un cadre de titane sombre, un écran, l'îlot de la caméra et un
 * reflet de verre. Il porte les VRAIS sites, photographiés en ligne.
 * La 3D se règle par `rotY` / `rotX` (degrés) ; la perspective est dans le cadre.
 */
import React from 'react';
import {Img, staticFile} from 'remotion';
import {C} from './donnees';

export const Telephone: React.FC<{
	l: number;
	h: number;
	r: number;
	rotY?: number;
	rotX?: number;
	echelle?: number;
	lueur?: number;
	corps?: number;
	style?: React.CSSProperties;
	children?: React.ReactNode;
}> = ({l, h, r, rotY = 0, rotX = 0, echelle = 1, lueur = 0.6, corps = 1, style, children}) => {
	const bord = 13 * corps;
	return (
		<div
			style={{
				position: 'absolute',
				width: l,
				height: h,
				transform: `perspective(2600px) rotateY(${rotY}deg) rotateX(${rotX}deg) scale(${echelle})`,
				...style,
			}}
		>
			<div
				style={{
					position: 'absolute',
					inset: -70,
					borderRadius: r + 70,
					background: `radial-gradient(ellipse at center, rgba(98,168,255,${0.32 * lueur}) 0%, rgba(107,63,242,${0.16 * lueur}) 45%, transparent 72%)`,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					borderRadius: r,
					opacity: corps,
					background: 'linear-gradient(145deg, #555b7e 0%, #1b1c33 20%, #2c2f4c 52%, #101122 80%, #3d4262 100%)',
					boxShadow: '0 50px 100px -24px rgba(0,0,0,.85), inset 0 0 0 1.5px rgba(205,215,255,.28), inset 0 0 0 5px rgba(10,10,22,.9)',
				}}
			/>
			<div style={{position: 'absolute', inset: bord, borderRadius: Math.max(8, r - bord + 2), overflow: 'hidden', background: C.encre}}>
				{children}
				{corps > 0.05 ? (
					<div
						style={{
							position: 'absolute',
							top: 15,
							left: '50%',
							width: 116,
							height: 34,
							marginLeft: -58,
							borderRadius: 20,
							background: '#030308',
							opacity: corps,
						}}
					/>
				) : null}
				<div
					style={{
						position: 'absolute',
						inset: 0,
						background: 'linear-gradient(115deg, rgba(255,255,255,.15) 0%, rgba(255,255,255,0) 30%, rgba(255,255,255,0) 72%, rgba(255,255,255,.05) 100%)',
						opacity: corps,
					}}
				/>
			</div>
		</div>
	);
};

/** La capture d'un vrai site dans l'écran ; `defile` = pixels déjà défilés. */
export const Capture: React.FC<{site: string; long?: boolean; defile?: number; style?: React.CSSProperties}> = ({site, long = false, defile = 0, style}) => (
	<Img
		src={staticFile(`nebula30/sites/${site}-${long ? 'tel-long' : 'tel'}.jpg`)}
		style={{position: 'absolute', left: 0, top: 0, width: '100%', display: 'block', transform: `translateY(${-defile}px)`, ...style}}
	/>
);
