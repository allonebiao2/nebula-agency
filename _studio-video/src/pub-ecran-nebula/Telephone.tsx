/**
 * Le téléphone du film, dessiné : un corps sombre, un liseré de lumière, l'îlot de la caméra, et l'écran.
 * Ce qu'il montre lui est donné (`children`) ; `eteint` (0 → 1) fait tomber l'écran au noir, comme un vrai écran
 * qui se met en veille (il garde un reflet de verre).
 */
import React, {CSSProperties} from 'react';

export const TEL = {l: 300, h: 624, bord: 9, rayon: 50};
export const ECRAN_TEL = {l: TEL.l - 2 * TEL.bord, h: TEL.h - 2 * TEL.bord};

export const Telephone: React.FC<{eteint?: number; style?: CSSProperties; fond?: string; children?: React.ReactNode}> = ({
	eteint = 0,
	style,
	fond = '#0d0c13',
	children,
}) => (
	<div
		style={{
			position: 'relative',
			width: TEL.l,
			height: TEL.h,
			borderRadius: TEL.rayon,
			background: 'linear-gradient(150deg, #24222c 0%, #121117 38%, #0b0a0f 100%)',
			boxShadow: '0 40px 90px rgba(0,0,0,0.65), inset 0 0 0 1.5px rgba(245,243,255,0.13)',
			...style,
		}}
	>
		<div
			style={{
				position: 'absolute',
				left: TEL.bord,
				top: TEL.bord,
				width: ECRAN_TEL.l,
				height: ECRAN_TEL.h,
				borderRadius: TEL.rayon - TEL.bord,
				overflow: 'hidden',
				background: fond,
			}}
		>
			{children}
			{eteint > 0 ? <div style={{position: 'absolute', inset: 0, background: '#050408', opacity: eteint}} /> : null}
			{/* le verre : un reflet en biais, toujours là, plus visible quand l'écran dort */}
			<div
				style={{
					position: 'absolute',
					inset: 0,
					background: 'linear-gradient(125deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0) 34%, rgba(255,255,255,0) 70%, rgba(255,255,255,0.03) 100%)',
					opacity: 0.6 + 0.4 * eteint,
				}}
			/>
		</div>
		{/* l'îlot de la caméra */}
		<div style={{position: 'absolute', top: TEL.bord + 12, left: (TEL.l - 84) / 2, width: 84, height: 24, borderRadius: 12, background: '#050407'}} />
	</div>
);
