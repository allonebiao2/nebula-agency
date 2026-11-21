/**
 * LE SON : la voix de Mongazi au premier plan (-16 LUFS, `caler_voix.py`), la musique douce dessous (-28 LUFS, baissée
 * encore un peu quand il parle), et un petit bruitage par geste, synthétisé (`_outils/pub_ecran_preparer.py`) :
 * pop pour la bulle, clic pour le doigt, carillon doux pour la commande, souffle pour le grand texte, bourdonnement
 * pour le néon. Chaque bruitage est calé sur un mot de `minutage.json`, jamais sur une seconde écrite à la main.
 */
import React from 'react';
import {Audio, interpolate, Sequence, staticFile} from 'remotion';
import {DUREE, DUREE_S, FPS, ligne, M, MIX, plan, quand} from './donnees';
import {allumageNeon, claquements} from './etat';
import {tapeCatalogue} from './PlansFin';

type Son = 'pop' | 'clic' | 'carillon' | 'souffle' | 'glisse' | 'tic' | 'eclat' | 'neon-allume';
const LONGUEUR: Record<Son, number> = {pop: 0.16, clic: 0.09, carillon: 1.9, souffle: 1.3, glisse: 0.55, tic: 0.04, eclat: 1.4, 'neon-allume': 0.16};

const normal = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');

const evenements = (): [number, Son, number][] => {
	const l7 = ligne(7).mots;
	const iSuite = l7.findIndex((w, i) => i > 0 && normal(w.m) === 'tout' && normal(l7[i - 1].m) === 'tout');
	const tSuite = iSuite > 0 ? l7[iSuite].a : ligne(7).fin - 0.6;
	return [
		// 3-5 · une vue de plus, la bulle, la deuxième coche, la bulle qui s'en va
		[quand(3, 'voit'), 'tic', 0.4],
		[ligne(4).debut + 0.02, 'pop', 0.4], // Polaris, 21/11 : à 0,6 il couvrait le « il » de « il t'écrit »
		[quand(4, 'combien'), 'tic', 0.2],
		[quand(5, 'il'), 'glisse', 0.45],
		// 6-7 · le violet qui s'ouvre, puis « TOUT DE SUITE »
		[plan('retiens').a, 'souffle', 0.32],
		[tSuite - 0.08, 'souffle', 0.25], // Polaris : à 0,55 il était aussi fort que le mot « suite »
		// 9 · les trois produits, leurs prix, le lien qui brille
		...[0, 1, 2].map((k): [number, Son, number] => [ligne(9).debut - 0.1 + k * 0.13, 'tic', 0.25]),
		...[0, 1, 2].map((k): [number, Son, number] => [quand(9, 'prix') + k * 0.1, 'tic', 0.16]),
		[quand(9, 'lien') - 0.05, 'eclat', 0.32],
		// 10 · le doigt sur « Commander »
		[quand(10, 'appuie'), 'clic', 0.75],
		// 11 · la commande arrive
		[quand(11, 'arrive'), 'carillon', 0.25], // Polaris : à 0,5 il passait 5 à 8 dB au-dessus de « sur »
		// 13-14 · les étincelles de Noël, l'anneau plein
		[plan('noel').a + 0.12, 'eclat', 0.26],
		[quand(14, '48') + 0.18, 'eclat', 0.22],
		// 15 · CATALOGUE tapé, puis envoyé
		...tapeCatalogue().map((x): [number, Son, number] => [x, 'tic', 0.1]),
		[quand(15, 'whatsapp'), 'clic', 0.55],
		// 16 · chaque fois que le tube prend la lumière, un claquement de néon
		...claquements('nebula').map((x, i): [number, Son, number] => [x, 'neon-allume', 0.42 * 0.8 ** i]),
		...claquements('agency').map((x, i): [number, Son, number] => [x, 'neon-allume', 0.34 * 0.8 ** i]),
	];
};

const SONS = evenements();

/** Mongazi parle-t-il à l'instant t ? (pour baisser la musique sous sa voix) */
const parle = (t: number) => M.lignes.some((l) => t >= l.debut - 0.12 && t <= l.fin + 0.2);
const baisse = (t: number) => {
	let s = 0;
	for (let k = -3; k <= 3; k++) s += parle(t + k * 0.06) ? 1 : 0;
	return 1 - 0.22 * (s / 7);
};

const fondu = (f: number, de: number, a: number) => interpolate(f, [de, a], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/**
 * `musique={false}` : la version Facebook, sans la musique (son Content ID n'est pas vérifié, et Facebook peut couper
 * tout le son d'une vidéo dont la musique est déposée). La voix et les bruitages ne bougent pas.
 */
export const Son: React.FC<{musique?: boolean}> = ({musique = true}) => {
	const tNeon = allumageNeon('nebula');
	const deNeon = Math.round(tNeon * FPS);
	return (
		<>
			{M.voix ? <Audio src={staticFile(M.voix)} volume={MIX} /> : null}
{musique ? (
			<Audio
				src={staticFile('pub-ecran-nebula/musique.wav')}
				volume={(f) => {
					const t = f / FPS;
					return MIX * fondu(f, 0, 1.2 * FPS) * (1 - fondu(f, (DUREE_S - 1.8) * FPS, DUREE - 1)) * baisse(t);
				}}
			/>
			) : null}
			<Sequence from={deNeon} durationInFrames={DUREE - deNeon} layout="none" name="néon">
				{/* ⚠️ « extend » : sans lui, le compte des images repart à zéro à chaque tour de boucle (3 s) et le fondu
				    d'entrée rejoue, le bourdonnement s'éteint et revient au milieu de la signature */}
				<Audio
					src={staticFile('pub-ecran-nebula/sfx/neon-bourdon.wav')}
					loop
					loopVolumeCurveBehavior="extend"
					volume={(f) => MIX * 0.13 * fondu(f, 0, 0.9 * FPS) * (1 - fondu(f + deNeon, DUREE - 1.2 * FPS, DUREE - 1))}
				/>
			</Sequence>
			{SONS.map(([quandT, son, volume], n) => {
				const de = Math.max(0, Math.round(quandT * FPS));
				const duree = Math.min(Math.ceil(LONGUEUR[son] * FPS) + 2, DUREE - de);
				if (duree <= 0) return null;
				return (
					<Sequence key={n} from={de} durationInFrames={duree} layout="none" name={son}>
						<Audio src={staticFile(`pub-ecran-nebula/sfx/${son}.wav`)} volume={volume * MIX} />
					</Sequence>
				);
			})}
		</>
	);
};
