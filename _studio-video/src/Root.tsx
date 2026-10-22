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
import {DUREE as GRAIN35_DUREE, FPS as GRAIN35_FPS, HAUTEUR as GRAIN35_H, LARGEUR as GRAIN35_L} from './grain35/donnees';
import {Grain35} from './grain35/Grain35';
import {FPS as MALETTRE_FPS, HAUTEUR as MALETTRE_H, LARGEUR as MALETTRE_L} from './malettre/donnees';
import {VERSIONS as MALETTRE_VERSIONS, type VersionId as MalettreVersion} from './malettre/minutage';
import {Pub as MalettrePub} from './malettre/Pub';
import {MinuitFilm} from './malettre-minuit/Minuit';
import {DUREE as MINUIT_DUREE, FPS as MINUIT_FPS, HAUTEUR as MINUIT_H, LARGEUR as MINUIT_L} from './malettre-minuit/donnees';

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

		{/* La publicité de Grain d'Esthétique, l'institut de Jocelyne : 35 s, le grain qui révèle. */}
		<Composition
			id="grain-35s"
			component={Grain35}
			durationInFrames={GRAIN35_DUREE}
			fps={GRAIN35_FPS}
			width={GRAIN35_L}
			height={GRAIN35_H}
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

		{/* MA LETTRE À… · « Minuit pile, pour maman » : 16:9 pour YouTube, 60 i/s, posé sur les voix de Mongazi. */}
		<Composition id="malettre-minuit" component={MinuitFilm} durationInFrames={Math.round(MINUIT_DUREE * MINUIT_FPS)} fps={MINUIT_FPS} width={MINUIT_L} height={MINUIT_H} />

		{/* MA LETTRE À… · la pub : 30 s et deux coupes de 15 s, en français et en
		    anglais. Une composition par MP3 de `src/malettre/VOIX.md`. */}
		<Folder name="malettre-pub">
			{(Object.keys(MALETTRE_VERSIONS) as MalettreVersion[]).map((id) => (
				<Composition
					key={id}
					id={`malettre-${id}`}
					component={MalettrePub}
					defaultProps={{version: id}}
					durationInFrames={Math.round(MALETTRE_VERSIONS[id].duree * MALETTRE_FPS)}
					fps={MALETTRE_FPS}
					width={MALETTRE_L}
					height={MALETTRE_H}
				/>
			))}
		</Folder>
	</>
);
