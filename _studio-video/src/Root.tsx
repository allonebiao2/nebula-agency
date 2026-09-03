import React from 'react';
import {Composition, Folder} from 'remotion';
import {OuiNon} from './OuiNon';
import {dureeDeLaSerie, FPS, SERIES} from './scripts';
import {Compte} from './minuit/Compte';
import {DUREE_TOTALE, DUREES, HAUTEUR as MINUIT_H, LARGEUR as MINUIT_L} from './minuit/donnees';
import {Fin} from './minuit/Fin';
import {Heure} from './minuit/Heure';
import {Lettre} from './minuit/Lettre';
import {Minuit} from './minuit/Minuit';
import {Seuil} from './minuit/Seuil';
import {Signature} from './minuit/Signature';

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

		<Composition
			id="minuit-demo"
			component={Minuit}
			durationInFrames={DUREE_TOTALE}
			fps={FPS}
			width={MINUIT_L}
			height={MINUIT_H}
		/>

		{/* Chaque plan est aussi une composition : on le règle seul, sans rejouer
		    les 25 secondes, et un double-clic sur la timeline y saute. */}
		<Folder name="minuit-plans">
			<Composition
				id="minuit-1-seuil"
				component={Seuil}
				durationInFrames={DUREES.seuil}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
			<Composition
				id="minuit-2-lettre"
				component={Lettre}
				durationInFrames={DUREES.lettre}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
			<Composition
				id="minuit-3-compte"
				component={Compte}
				durationInFrames={DUREES.compte}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
			<Composition
				id="minuit-4-signature"
				component={Signature}
				durationInFrames={DUREES.signature}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
			<Composition
				id="minuit-5-heure"
				component={Heure}
				durationInFrames={DUREES.heure}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
			<Composition
				id="minuit-6-fin"
				component={Fin}
				durationInFrames={DUREES.fin}
				fps={FPS}
				width={MINUIT_L}
				height={MINUIT_H}
			/>
		</Folder>
	</>
);
