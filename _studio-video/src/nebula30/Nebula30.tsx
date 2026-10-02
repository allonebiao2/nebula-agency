/**
 * NEBULA · LA VIDÉO DE MARQUE (30 s). Voir `donnees.ts` pour la phrase et l'objet.
 *
 * Trois couches qui se relaient : le FILM jusqu'au gel ; le LOGICIEL DE MONTAGE,
 * qui montre ce film dans son moniteur (figé, rembobiné) ; la FIN (l'appel et la
 * signature). Le son : la voix placée, la musique montée et baissée sous la voix
 * (`_outils/nebula30_son.py`), puis les bruitages.
 */
import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {Bruitages} from './Bruitages';
import {C, FPS, MIX, type Registre, T} from './donnees';
import {Film, Fin} from './Film';
import {Montage} from './scenes/Montage';

export const Nebula30: React.FC<{registre: Registre}> = ({registre}) => {
	const t = useCurrentFrame() / FPS;
	return (
		<AbsoluteFill style={{backgroundColor: C.encre}}>
			{t < T.fige ? <Film t={t} registre={registre} /> : null}
			{t >= T.chute ? <Fin t={t} registre={registre} /> : null}
			{t >= T.fige && t <= T.chute + 0.45 ? <Montage t={t} registre={registre} film={(tf) => <Film t={tf} registre={registre} />} /> : null}
			<Audio src={staticFile('nebula30/voix.wav')} volume={MIX} />
			<Audio src={staticFile('nebula30/musique.wav')} volume={MIX} />
			<Bruitages />
		</AbsoluteFill>
	);
};
