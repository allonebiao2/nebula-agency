/**
 * MA LETTRE À… · « Minuit pile, pour maman » · 16:9, YouTube, 1920×1080 à 60 i/s.
 *
 * L'histoire (Koffi, le piano), MINUIT (le wow, sans voix), la lettre, puis la vente (Alimata, l'afrobeat) : la
 * marque, l'heure choisie, l'impossible à ouvrir, la plume, l'habillage, la Saint-Valentin, les excuses, la
 * demande, la soirée entre potes, la fin. Chaque plan est posé sur la voix (`minutage.json`, écrit par
 * `_outils/malettre_minuit_son.py`) ; le son est le master de ce script (−14 LUFS, −1 dBTP).
 *
 * Les bandes du cinéma tiennent toute l'histoire, et s'ouvrent à minuit : l'image s'agrandit au moment où la
 * lettre s'ouvre.
 */
import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, DUREE, L, MINUIT, NARRATRICE} from './donnees';
import {Bandes, Grain, Vignette} from './decor';
import {Decalage, p, SORT} from './outils';
import {Accroche, Ecriture, Envol, Lettre, Minuit as MinuitScene, Paris, Retour, Sceau} from './histoire';
import {Demande, Fin, Habit, Heure, Insiste, Marque, Pardon, PlumeScene, Potes, Valentin} from './produit';

type Plan = {nom: string; debut: number; fin: number; rendu: (debut: number, fin: number) => React.ReactNode};

const PLANS: Plan[] = [
	{nom: 'Accroche', debut: 0, fin: 3.3, rendu: (d) => <Accroche debut={d} />},
	{nom: 'Paris', debut: 3.15, fin: 7.3, rendu: (d) => <Paris debut={d} />},
	{nom: 'Écriture', debut: 7.15, fin: 9.35, rendu: (d) => <Ecriture debut={d} />},
	{nom: 'Sceau', debut: 9.2, fin: L('k7').fin + 0.05, rendu: (d) => <Sceau debut={d} />},
	{nom: 'Envol', debut: L('k7').fin, fin: 11.95, rendu: (d, f) => <Envol debut={d} fin={f} />},
	{nom: 'Retour', debut: 11.75, fin: MINUIT, rendu: (d) => <Retour debut={d} />},
	{nom: 'Minuit', debut: MINUIT, fin: L('k8').debut + 0.05, rendu: (d, f) => <MinuitScene debut={d} fin={f} />},
	{nom: 'Lettre', debut: L('k8').debut - 0.08, fin: NARRATRICE + 0.05, rendu: (d, f) => <Lettre debut={d} fin={f} />},
	{nom: 'Marque', debut: NARRATRICE - 0.02, fin: L('a2').debut, rendu: (d, f) => <Marque debut={d} fin={f} />},
	{nom: 'Heure', debut: L('a2').debut - 0.05, fin: L('a4').debut, rendu: (d, f) => <Heure debut={d} fin={f} />},
	{nom: 'Insiste', debut: L('a4').debut - 0.05, fin: L('a6').debut, rendu: (d, f) => <Insiste debut={d} fin={f} />},
	{nom: 'Plume', debut: L('a6').debut - 0.05, fin: L('a8').debut, rendu: (d, f) => <PlumeScene debut={d} fin={f} />},
	{nom: 'Habit', debut: L('a8').debut - 0.05, fin: L('a10').debut, rendu: (d, f) => <Habit debut={d} fin={f} />},
	{nom: 'Valentin', debut: L('a10').debut - 0.05, fin: L('a13').debut, rendu: (d, f) => <Valentin debut={d} fin={f} />},
	{nom: 'Pardon', debut: L('a13').debut - 0.05, fin: L('a15').debut, rendu: (d, f) => <Pardon debut={d} fin={f} />},
	{nom: 'Demande', debut: L('a15').debut - 0.05, fin: L('a17').debut, rendu: (d, f) => <Demande debut={d} fin={f} />},
	{nom: 'Potes', debut: L('a17').debut - 0.05, fin: L('a19').debut - 0.1, rendu: (d, f) => <Potes debut={d} fin={f} />},
	{nom: 'Fin', debut: L('a19').debut - 0.2, fin: DUREE, rendu: (d, f) => <Fin debut={d} fin={f} />},
];

export const MinuitFilm: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = f / fps;
	const ouvert = p(t, MINUIT + 0.05, MINUIT + 0.5, SORT);
	return (
		<AbsoluteFill style={{background: C.nuit3}}>
			{PLANS.map((pl) => (
				<Sequence key={pl.nom} name={pl.nom} from={Math.round(pl.debut * fps)} durationInFrames={Math.max(1, Math.round((pl.fin - pl.debut) * fps))}>
					<Decalage.Provider value={pl.debut}>{pl.rendu(pl.debut, pl.fin)}</Decalage.Provider>
				</Sequence>
			))}
			<Vignette force={0.55} />
			<Grain force={0.055} />
			<Bandes ouvert={ouvert} />
			<Audio src={staticFile('malettre-minuit/mix.wav')} />
		</AbsoluteFill>
	);
};
