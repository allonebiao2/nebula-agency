import React from 'react';
import {Composition} from 'remotion';
import {OuiNon} from './OuiNon';
import {dureeDeLaSerie, FPS, SERIES} from './scripts';

/** TikTok : vertical plein cadre, 1080x1920. */
const LARGEUR = 1080;
const HAUTEUR = 1920;

export const Racine: React.FC = () => (
	<>
		{SERIES.map((serie) => (
			<Composition
				key={serie.id}
				id={serie.id}
				component={OuiNon}
				durationInFrames={dureeDeLaSerie(serie)}
				fps={FPS}
				width={LARGEUR}
				height={HAUTEUR}
				defaultProps={{serie}}
			/>
		))}
	</>
);
