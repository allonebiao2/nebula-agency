/**
 * L'IMAGE DU FILM, pour un instant t : le fond d'espace et la poussière (dans la
 * caméra, qui pousse et tremble), puis les scènes. `Film` couvre tout ce qui
 * précède le gel ; c'est aussi lui que le moniteur du logiciel de montage montre,
 * figé puis rembobiné. `Fin` couvre l'appel et la signature.
 */
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, CENTRE, type Registre, T} from './donnees';
import {ETOILE} from './logo';
import {p, secousse} from './outils';
import {Particules} from './Particules';
import {Appel} from './scenes/Appel';
import {Naissance} from './scenes/Naissance';
import {Signature} from './scenes/Signature';
import {Tours} from './scenes/Tours';
import {Univers} from './Univers';

export const Film: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	// la caméra pousse dans la galaxie, et revient avant que la poussière dessine le téléphone
	const zoom = 1 + 0.08 * p(t, T.bang + 0.4, T.versTel - 0.45) * (1 - p(t, T.versTel - 0.45, T.versTel + 0.1));
	const [dx, dy] = secousse(t, [T.bang], 18);
	return (
		<AbsoluteFill style={{backgroundColor: C.encre, overflow: 'hidden'}}>
			<div style={{position: 'absolute', inset: 0, transformOrigin: `${CENTRE.x}px ${CENTRE.y}px`, transform: `translate(${dx}px, ${dy}px) scale(${zoom})`}}>
				<Univers t={t} />
				<Particules t={t} />
			</div>
			<div style={{position: 'absolute', inset: 0, transform: `translate(${dx}px, ${dy}px)`}}>
				<Naissance t={t} registre={registre} />
			</div>
			<Tours t={t} registre={registre} />
		</AbsoluteFill>
	);
};

export const Fin: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	const [dx, dy] = secousse(t, [T.hit], 22);
	const pousse = 1 + 0.03 * p(t, T.hit, 30);
	return (
		<AbsoluteFill style={{backgroundColor: C.encre, overflow: 'hidden'}}>
			<div style={{position: 'absolute', inset: 0, transformOrigin: `${ETOILE.x}px ${ETOILE.y}px`, transform: `translate(${dx}px, ${dy}px) scale(${pousse})`}}>
				<Univers t={t} />
				<Particules t={t} />
			</div>
			<Appel t={t} registre={registre} />
			<div style={{position: 'absolute', inset: 0, transformOrigin: `${ETOILE.x}px ${ETOILE.y}px`, transform: `translate(${dx}px, ${dy}px) scale(${pousse})`}}>
				<Signature t={t} registre={registre} />
			</div>
		</AbsoluteFill>
	);
};
