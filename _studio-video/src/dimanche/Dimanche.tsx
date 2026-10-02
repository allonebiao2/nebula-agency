/**
 * LE PLAN DU DIMANCHE · le montage. Voir `donnees.ts` pour la phrase et l'objet.
 *
 * Les couches, de bas en haut : la vidéo (poussées, tremblement, ombres) · les
 * feuilles de chaque chapitre · les sous-titres mot à mot · le repère des
 * chapitres · la carte de fin. Le son : la voix nettoyée, puis les bruitages.
 *
 * Toutes les scènes lisent le temps absolu `t` ; chacune sait seule quand elle
 * entre et sort (elle se cale sur des mots, par leur indice Whisper).
 */
import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {Bruitages} from './Bruitages';
import {Chapitres} from './Chapitres';
import {DEBUT_FIN, FPS, d, fi} from './donnees';
import {Fond} from './Fond';
import {Budget, Verbes, Vitesse} from './scenes/Argent';
import {Dimanche21h, Invitation, Membres, Opportunites, Resultats, Valider} from './scenes/Communaute';
import {Loi, PlanWeekend} from './scenes/Methode';
import {Avance, Echo, Jamais, Profils, Semaine} from './scenes/Planifier';
import {CarteDeFin, Formation, Live, Septembre, TuEsIci} from './scenes/Rejoindre';
import {Bascule, Improviser, Question} from './scenes/Trader';
import {SousTitres} from './SousTitres';

/** Là où le graphique dit déjà la phrase en grand, les sous-titres se taisent. */
const MASQUES: [number, number][] = [
	[0, d(6) - 0.2],
	[d(59) - 0.05, fi(63) + 0.35],
	[d(564) - 0.1, d(566) - 0.1],
	[DEBUT_FIN, 999],
];

export const Dimanche: React.FC = () => {
	const frame = useCurrentFrame();
	const t = frame / FPS;
	return (
		<AbsoluteFill style={{backgroundColor: '#0b0d12'}}>
			<Fond t={t} frame={frame} />

			<Echo t={t} />
			<Semaine t={t} />
			<Profils t={t} />
			<Jamais t={t} />
			<Avance t={t} />

			<Verbes t={t} />
			<Budget t={t} />
			<Vitesse t={t} />

			<Question t={t} />
			<Bascule t={t} />
			<Improviser t={t} />

			<PlanWeekend t={t} />
			<Loi t={t} />

			<Dimanche21h t={t} />
			<Membres t={t} />
			<Opportunites t={t} />
			<Valider t={t} />
			<Resultats t={t} />
			<Invitation t={t} />

			<TuEsIci t={t} />
			<Formation t={t} />
			<Live t={t} />
			<Septembre t={t} />

			<SousTitres t={t} masques={MASQUES} />
			<Chapitres t={t} />
			<CarteDeFin t={t} />

			<Audio src={staticFile('dimanche/voix.wav')} />
			<Bruitages />
		</AbsoluteFill>
	);
};
