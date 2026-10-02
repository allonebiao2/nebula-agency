import React from 'react';
import {Composition, Folder} from 'remotion';
import {OuiNon} from './OuiNon';
import {dureeDeLaSerie, FPS, SERIES} from './scripts';
import {Dimanche} from './dimanche/Dimanche';
import {DUREE_TOTALE as DIMANCHE_DUREE, FPS as DIMANCHE_FPS, HAUTEUR as DIMANCHE_H, LARGEUR as DIMANCHE_L} from './dimanche/donnees';
import {Compte} from './lepli/Compte';
import {DUREE_TOTALE, DUREES, HAUTEUR as LEPLI_H, LARGEUR as LEPLI_L} from './lepli/donnees';
import {Fin} from './lepli/Fin';
import {Heure} from './lepli/Heure';
import {Lettre} from './lepli/Lettre';
import {LePli} from './lepli/LePli';
import {Seuil} from './lepli/Seuil';
import {Signature} from './lepli/Signature';
import {DUREE as NEBULA30_DUREE, FPS as NEBULA30_FPS, HAUTEUR as NEBULA30_H, LARGEUR as NEBULA30_L} from './nebula30/donnees';
import {Nebula30} from './nebula30/Nebula30';

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

		{/* La vidéo d'un proche reprise en motion design : sa source reste hors dépôt. */}
		<Composition
			id="dimanche-plan"
			component={Dimanche}
			durationInFrames={DIMANCHE_DUREE}
			fps={DIMANCHE_FPS}
			width={DIMANCHE_L}
			height={DIMANCHE_H}
		/>

		{/* La vidéo de marque NEBULA, 30 s : le tour de magie. La version TikTok
		    (« tu ») attend sa propre voix off : elle n'est pas déclarée tant qu'elle manque. */}
		<Composition
			id="nebula-30s"
			component={Nebula30}
			durationInFrames={NEBULA30_DUREE}
			fps={NEBULA30_FPS}
			width={NEBULA30_L}
			height={NEBULA30_H}
			defaultProps={{registre: 'vous' as const}}
		/>

		<Composition
			id="lepli-demo"
			component={LePli}
			durationInFrames={DUREE_TOTALE}
			fps={FPS}
			width={LEPLI_L}
			height={LEPLI_H}
		/>

		{/* Chaque plan est aussi une composition : on le règle seul, sans rejouer
		    les 25 secondes, et un double-clic sur la timeline y saute. */}
		<Folder name="lepli-plans">
			<Composition
				id="lepli-1-seuil"
				component={Seuil}
				durationInFrames={DUREES.seuil}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
			<Composition
				id="lepli-2-lettre"
				component={Lettre}
				durationInFrames={DUREES.lettre}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
			<Composition
				id="lepli-3-compte"
				component={Compte}
				durationInFrames={DUREES.compte}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
			<Composition
				id="lepli-4-signature"
				component={Signature}
				durationInFrames={DUREES.signature}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
			<Composition
				id="lepli-5-heure"
				component={Heure}
				durationInFrames={DUREES.heure}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
			<Composition
				id="lepli-6-fin"
				component={Fin}
				durationInFrames={DUREES.fin}
				fps={FPS}
				width={LEPLI_L}
				height={LEPLI_H}
			/>
		</Folder>
	</>
);
