/**
 * PUB ÉCRAN NEBULA · les deux compositions.
 *  · PubEcranNebula169    : le film 16:9 (1920 x 1080, 30 i/s), tel quel ;
 *  · PubEcranNebulaTikTok : le même film sur un moniteur, dans la pièce sombre (1080 x 1920).
 * Rendu à UN onglet, l'un après l'autre (8 Go sur ce PC) : voir `README.md` de ce dossier.
 * `musique: false` (props) : le son de la version Facebook, sans la musique.
 */
import React from 'react';
import {AbsoluteFill, random, staticFile, useCurrentFrame} from 'remotion';
import {C, FPS} from './donnees';
import {Film} from './Film';
import {Piece} from './Piece';
import {Son} from './Son';

export type PropsPub = {musique: boolean};

export const PubEcranNebula169Film: React.FC<PropsPub> = ({musique}) => {
	const frame = useCurrentFrame();
	const t = frame / FPS;
	return (
		<AbsoluteFill style={{background: C.nuit, overflow: 'hidden'}}>
			<Film t={t} />
			{/* un grain très léger : il casse les marches d'escalier du halo, que la compression creuse */}
			<AbsoluteFill
				style={{
					backgroundImage: `url(${staticFile('pub-ecran-nebula/grain.png')})`,
					backgroundPosition: `${Math.floor(random(`gx${frame}`) * 384)}px ${Math.floor(random(`gy${frame}`) * 384)}px`,
					opacity: 0.35,
				}}
			/>
			<Son musique={musique} />
		</AbsoluteFill>
	);
};

export const PubEcranNebulaTikTokPiece: React.FC<PropsPub> = ({musique}) => (
	<AbsoluteFill style={{background: '#040307'}}>
		<Piece />
		<Son musique={musique} />
	</AbsoluteFill>
);
