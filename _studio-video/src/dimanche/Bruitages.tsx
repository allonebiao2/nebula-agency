/**
 * LES BRUITAGES · un son par geste de la feuille, calé sur les mêmes mots que
 * l'animation qu'il accompagne (jamais une seconde recopiée à la main).
 * Discrets : la voix est à −14 LUFS, ils passent dessous (volume 0,12 à 0,35).
 */
import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
import {DEBUT_FIN, FPS, d} from './donnees';

type Son = 'pop' | 'whoosh' | 'tampon' | 'coche' | 'stylo' | 'clic' | 'tic' | 'montee' | 'ding';
const DUREE: Record<Son, number> = {pop: 0.12, whoosh: 0.42, tampon: 0.3, coche: 0.09, stylo: 0.5, clic: 0.06, tic: 0.04, montee: 0.9, ding: 0.9};
const VOLUME: Record<Son, number> = {pop: 0.22, whoosh: 0.16, tampon: 0.38, coche: 0.2, stylo: 0.1, clic: 0.18, tic: 0.12, montee: 0.2, ding: 0.16};

const s = (quand: number, son: Son, force = 1): [number, Son, number] => [quand, son, force];

/** Les tics d'une horloge qui tourne, de a à b. */
const tics = (a: number, b: number, n: number) => Array.from({length: n}, (_, k) => s(a + ((b - a) * k) / (n - 1), 'tic'));

/** Le curseur qui clique au hasard, toutes les 0,5 s, jusqu'au saut. */
const clics = (() => {
	const a = d(386) - 0.1;
	const fin = d(425) - 0.05;
	const out: [number, Son, number][] = [];
	for (let q = a + 0.16; q < fin; q += 0.5) out.push(s(q, 'clic', 0.55));
	return out;
})();

/** Le balayage des opportunités : un pop quand il touche chacune. */
const opportunites = [3.5, 7.5, 12.5].map((k) => s(d(605) + (k / 14) * (d(620) - d(605)), 'pop', 0.9));

export const SONS: [number, Son, number][] = [
	// 1 · planifier
	s(0, 'whoosh'), s(d(4), 'pop'), s(d(5), 'pop'),
	s(d(6) - 0.15, 'whoosh'), s(d(14) + 0.05, 'whoosh', 0.7), s(d(24), 'whoosh', 0.6),
	s(d(45) - 0.08, 'pop'), s(d(49) - 0.08, 'pop'), s(d(53) - 0.08, 'pop'), s(d(58) - 0.08, 'pop'),
	s(d(62) - 0.04, 'tampon', 1.2),
	s(d(64) - 0.1, 'whoosh'), s(d(82) + 0.1, 'stylo'),
	// 2 · l'argent
	s(d(87) - 0.1, 'whoosh'), s(d(100) - 0.08, 'pop'), s(d(107) - 0.08, 'pop'), s(d(109) - 0.08, 'pop'), s(d(121) - 0.08, 'pop'),
	s(d(122) - 0.1, 'whoosh'), s(d(138) - 0.1, 'pop'), s(d(161) - 0.1, 'whoosh', 0.6), s(d(170) - 0.05, 'stylo', 1.2),
	s(d(176) - 0.05, 'stylo'), s(d(197) - 0.1, 'whoosh', 0.7), s(d(200), 'stylo'), s(d(204) - 0.1, 'pop'),
	s(d(241), 'whoosh', 0.7), s(d(250) + 0.1, 'coche'), s(d(261), 'pop'), s(d(275), 'stylo'), s(d(283) - 0.1, 'whoosh', 0.7),
	s(d(288) - 0.05, 'whoosh'), s(d(323) - 0.1, 'whoosh', 0.8),
	// 3 · le trader
	s(d(324) - 0.05, 'whoosh'), s(d(333), 'stylo'),
	s(d(348) - 0.9, 'montee'), s(d(348) + 0.35, 'whoosh'), s(d(362) - 0.1, 'stylo'), s(d(369) - 0.1, 'stylo'), s(d(372), 'whoosh', 0.6),
	s(d(374), 'pop'), s(d(374) + 0.22, 'pop'), s(d(374) + 0.44, 'pop'),
	s(d(386) - 0.1, 'whoosh'), ...clics, s(d(409) - 0.05, 'tampon'), s(d(425) - 0.05, 'clic', 1.4), s(d(428), 'stylo', 1.2),
	// 4 · la méthode
	s(d(435) - 0.15, 'whoosh'), s(d(438) - 0.05, 'tampon', 0.6), s(d(442), 'stylo', 0.7), s(d(465), 'stylo'), s(d(468), 'stylo'),
	s(d(473), 'stylo'), s(d(480) - 0.1, 'stylo', 0.7), s(d(486) - 0.1, 'stylo', 0.7),
	s(d(501), 'coche', 1.2), s(d(502), 'coche', 1.2), s(d(503), 'coche', 1.2), s(d(509) - 0.05, 'tampon', 1.1),
	s(d(511) - 0.1, 'whoosh'), s(d(522), 'stylo', 0.8), s(d(529), 'stylo', 0.8), s(d(553) - 0.1, 'stylo'), s(d(559) - 0.1, 'stylo'),
	s(d(564) - 0.1, 'tampon', 0.8),
	// 5 · la communauté
	s(d(566) - 0.1, 'whoosh'), ...tics(d(572) - 0.1, d(574) + 0.3, 9), s(d(573) + 0.25, 'pop'),
	s(d(578) - 0.25, 'whoosh'), s(d(584) - 0.1, 'pop'),
	s(d(597) - 0.2, 'whoosh'), ...opportunites,
	s(d(623) - 0.2, 'whoosh'), s(d(624), 'coche'), s(d(624) + 0.2, 'coche'), s(d(626), 'stylo'), s(d(626) + 0.2, 'stylo'),
	s(d(636) - 0.2, 'whoosh'), s(d(643), 'stylo'), s(d(656) - 0.1, 'whoosh'), s(d(670), 'stylo', 1.1),
	// 6 · rejoindre
	s(d(677) - 0.1, 'whoosh'), s(d(683) + 0.1, 'pop', 1.2),
	s(d(711) - 0.2, 'whoosh'), s(d(712) - 0.1, 'stylo'), s(d(715) - 0.1, 'stylo'), s(d(723) - 0.15, 'whoosh'), s(d(726), 'ding'),
	s(d(733) - 0.2, 'coche'), s(d(741) - 0.2, 'coche'), s(d(752) - 0.2, 'coche'), s(d(758) - 0.2, 'coche'),
	s(d(768), 'pop', 1.2), s(d(781), 'clic', 1.4), s(d(781) + 0.05, 'ding'),
	s(d(782) - 0.1, 'whoosh'), s(d(796) - 0.25, 'whoosh'), ...tics(d(796) + 0.1, d(799) + 0.45, 10), s(d(802) - 0.1, 'pop'),
	s(d(803) - 0.05, 'ding', 1.2), s(d(810) - 0.1, 'pop', 0.7), s(d(810) + 0.2, 'pop', 0.7), s(d(810) + 0.5, 'pop', 0.7),
	s(d(826) - 0.3, 'whoosh'), s(d(831) - 0.15, 'montee', 0.7),
	s(DEBUT_FIN, 'whoosh'), s(DEBUT_FIN + 1.0, 'stylo'),
];

export const Bruitages: React.FC = () => (
	<>
		{SONS.map(([quand, son, force], n) => (
			<Sequence key={n} from={Math.max(0, Math.round(quand * FPS))} durationInFrames={Math.ceil(DUREE[son] * FPS) + 2} layout="none" name={`${son}`}>
				<Audio src={staticFile(`dimanche/sfx/${son}.wav`)} volume={Math.min(1, VOLUME[son] * force)} />
			</Sequence>
		))}
	</>
);
