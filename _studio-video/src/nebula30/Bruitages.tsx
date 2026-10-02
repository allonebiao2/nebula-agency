/**
 * LES BRUITAGES · un son par geste, calé sur les mêmes instants que l'animation
 * qu'il accompagne (jamais une seconde recopiée à la main).
 * Pendant que la voix parle, ils restent discrets : elle doit passer devant tout.
 */
import React from 'react';
import {Audio, Sequence, interpolate, staticFile} from 'remotion';
import {FPS, MIX, T, mot} from './donnees';
import {ecriture} from './scenes/Appel';
import {instantsCommandes} from './scenes/Tours';

type Son =
	| 'battement' | 'aspiration' | 'impact' | 'scintille' | 'whoosh' | 'souffle' | 'trace' | 'pose' | 'carte' | 'commande'
	| 'module' | 'donnee' | 'montee' | 'rembobine' | 'declic' | 'etincelle' | 'envoi' | 'implosion' | 'final'
	| 'touche1' | 'touche2' | 'touche3' | 'touche4';

const DUREE: Record<Son, number> = {
	battement: 2.1, aspiration: 1.4, impact: 6.4, scintille: 3.6, whoosh: 1.55, souffle: 2.3, trace: 1.6, pose: 0.62, carte: 0.16,
	commande: 1.65, module: 0.14, donnee: 0.07, montee: 2.7, rembobine: 1.6, declic: 0.42, etincelle: 3.6, envoi: 1.0, implosion: 1.25,
	final: 8.6, touche1: 0.06, touche2: 0.06, touche3: 0.06, touche4: 0.06,
};

const s = (quand: number, son: Son, volume: number): [number, Son, number] => [quand, son, volume];

const frappe = (() => {
	const {debut, fin} = ecriture();
	const out: [number, Son, number][] = [];
	let k = 0;
	for (let q = debut; q < fin; q += 0.07, k++) out.push(s(q, (['touche1', 'touche2', 'touche3', 'touche4'] as const)[k % 4], 0.16));
	return out;
})();

export const SONS: [number, Son, number][] = [
	// la promesse
	s(0.05, 'battement', 0.6), s(1.0, 'battement', 0.5), s(T.bang - 1.4, 'aspiration', 0.45),
	// l'explosion
	s(T.bang, 'impact', 0.8), s(T.bang + 0.12, 'scintille', 0.32), s(T.bang + 1.2, 'souffle', 0.28),
	s(mot('nebulaCree', 0), 'etincelle', 0.22),
	// la vitrine
	s(T.versTel - 0.05, 'whoosh', 0.38), s(T.vitrine + 0.15, 'trace', 0.3), s(T.revele, 'pose', 0.35), s(T.revele + 0.1, 'etincelle', 0.2),
	s(T.eventail, 'souffle', 0.3), s(mot('marque', 4) + 0.15, 'etincelle', 0.22),
	// le catalogue
	s(T.catalogue - 0.1, 'whoosh', 0.42),
	...[0, 1, 2, 3].map((k) => s(T.catalogue + 0.35 + k * 0.12, 'carte', 0.22)),
	...[0, 1, 2, 3, 4, 5].map((k) => s(mot('catalogue', 2) + 0.25 + k * 0.12, 'donnee', 0.1)),
	s(T.tap, 'pose', 0.38),
	...instantsCommandes().map((q) => s(q, 'commande', 0.3)),
	// l'outil
	s(T.outil - 0.45, 'whoosh', 0.36),
	...[0, 0.12, 0.22, 0.32, 0.42, 0.56, 0.68].map((d) => s(T.outil + 0.3 + d, 'module', 0.26)),
	s(T.peaux, 'whoosh', 0.22), s(T.peaux + (mot('outil', 5) - T.peaux) / 2, 'whoosh', 0.22), s(mot('outil', 5), 'whoosh', 0.24),
	s(T.fige - 1.7, 'montee', 0.4),
	// la révélation
	s(T.fige, 'declic', 0.45), s(T.recul, 'souffle', 0.42), s(T.recul + 0.5, 'declic', 0.28),
	s(T.rembobine, 'rembobine', 0.48), s(T.rembobine + 0.95, 'declic', 0.32),
	s(T.votre, 'etincelle', 0.42), s(T.votre + 0.15, 'whoosh', 0.28),
	s(T.chute - 0.12, 'whoosh', 0.42),
	// l'appel
	...frappe, s(ecriture().envoi, 'envoi', 0.36),
	// la signature
	s(T.hit - 1.25, 'implosion', 0.55), s(T.hit, 'final', 0.8), s(T.hit + 0.1, 'scintille', 0.3),
	s(T.hit + 1.4, 'etincelle', 0.26), s(T.contacts, 'pose', 0.22), s(28.95, 'etincelle', 0.32),
];

/** Le fond de l'espace : sous la promesse, et pendant que la musique se tait. */
const Nappe: React.FC<{de: number; a: number; volume: number}> = ({de, a, volume}) => (
	<Sequence from={Math.round(de * FPS)} durationInFrames={Math.round((a - de) * FPS)} layout="none" name="nappe">
		<Audio
			src={staticFile('nebula30/sfx/nappe.wav')}
			volume={(f) => volume * MIX * interpolate(f, [0, 12, (a - de) * FPS - 12, (a - de) * FPS], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
		/>
	</Sequence>
);

export const Bruitages: React.FC = () => (
	<>
		<Nappe de={0} a={T.bang + 0.3} volume={0.35} />
		<Nappe de={T.fige} a={T.chute + 0.2} volume={0.32} />
		{SONS.map(([quand, son, volume], n) => (
			<Sequence key={n} from={Math.max(0, Math.round(quand * FPS))} durationInFrames={Math.ceil(DUREE[son] * FPS) + 2} layout="none" name={son}>
				<Audio src={staticFile(`nebula30/sfx/${son}.wav`)} volume={volume * MIX} />
			</Sequence>
		))}
	</>
);
