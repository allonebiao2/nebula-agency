/**
 * LES BRUITAGES · un son par geste, calé sur les instants de `donnees.ts`
 * (jamais une seconde recopiée à la main). Pas de voix, pas de musique :
 * une nappe d'espace en fond, et les bruitages synthétisés de NEBULA
 * (`public/nebula30/sfx/`, `_outils/nebula30_bruitages.py`, aucun fichier tiers).
 * Mongazi peut poser un son de TikTok par-dessus dans l'application.
 */
import React from 'react';
import {Audio, interpolate, Sequence, staticFile} from 'remotion';
import {DUREE, FPS, MIX, NUMERO, T} from './donnees';

type Son =
	| 'aspiration' | 'battement' | 'carte' | 'commande' | 'declic' | 'donnee' | 'envoi' | 'etincelle' | 'final' | 'impact'
	| 'implosion' | 'module' | 'pose' | 'scintille' | 'souffle' | 'trace' | 'whoosh' | 'touche1' | 'touche2' | 'touche3' | 'touche4';

/** Durées mesurées des fichiers (secondes). */
const LONGUEUR: Record<Son, number> = {
	aspiration: 1.4, battement: 2.1, carte: 0.16, commande: 1.65, declic: 0.42, donnee: 0.07, envoi: 1.0, etincelle: 3.6,
	final: 8.6, impact: 6.4, implosion: 1.25, module: 0.14, pose: 0.62, scintille: 3.6, souffle: 2.3, trace: 1.6, whoosh: 1.55,
	touche1: 0.06, touche2: 0.06, touche3: 0.06, touche4: 0.06,
};

const s = (quand: number, son: Son, volume: number): [number, Son, number] => [quand, son, volume];
const serie = (de: number, a: number, pas: number, son: Son, volume: number) => {
	const out: [number, Son, number][] = [];
	for (let q = de; q < a; q += pas) out.push(s(q, son, volume));
	return out;
};
const touches = (['touche1', 'touche2', 'touche3', 'touche4'] as const);

export const SONS: [number, Son, number][] = [
	// 1 · l'accroche
	s(T.bulle, 'pose', 0.55), s(T.bulle + 0.02, 'carte', 0.3),
	...serie(T.attente, T.parti - 0.04, 0.1, 'donnee', 0.22),
	s(T.parti, 'impact', 0.55),
	// 2 · le conseil
	s(T.conseil - 0.1, 'whoosh', 0.3),
	s(T.trois - 0.02, 'pose', 0.5), s(T.trois, 'etincelle', 0.3), s(T.choses, 'carte', 0.25),
	s(T.liste - 0.05, 'whoosh', 0.4),
	s(T.photo, 'trace', 0.35), s(T.photo + 0.15, 'pose', 0.3), s(T.photo + 0.45, 'declic', 0.4), s(T.photo + 0.85, 'scintille', 0.18),
	...serie(T.prix, T.prix + 0.42, 0.06, 'donnee', 0.15), s(T.prix + 0.15, 'pose', 0.3), s(T.prix + 0.45, 'declic', 0.4),
	s(T.commander, 'module', 0.3), s(T.commander + 0.15, 'pose', 0.3), s(T.commander + 0.45, 'declic', 0.4),
	s(T.tap, 'touche1', 0.55), s(T.tap + 0.02, 'commande', 0.35),
	s(T.sinon, 'souffle', 0.3), s(T.sinon + 0.25, 'pose', 0.45), s(T.sinon + 0.7, 'impact', 0.3),
	s(T.nuit, 'scintille', 0.35), s(T.nuit + 0.15, 'pose', 0.35), s(T.nuit + 0.5, 'etincelle', 0.25),
	// 3 · la leçon
	s(T.lecon - 0.05, 'whoosh', 0.5),
	s(T.chute - 0.3, 'aspiration', 0.35),
	...serie(T.chute, T.mo - 0.03, 0.05, 'donnee', 0.14),
	s(T.mo, 'impact', 0.7),
	s(T.reseau, 'whoosh', 0.4), s(T.reseau + 0.2, 'battement', 0.4), s(T.reseau + 1.4, 'battement', 0.35),
	...serie(T.reseau + 0.3, T.lourd - 0.1, 0.25, 'carte', 0.16),
	s(T.ailleurs + 0.25, 'whoosh', 0.4),
	s(T.lourd, 'declic', 0.3), s(T.lourd + 0.25, 'impact', 0.6),
	s(T.leger, 'etincelle', 0.45), s(T.leger + 0.05, 'scintille', 0.3), s(T.leger + 0.55, 'touche2', 0.5), s(T.leger + 0.57, 'commande', 0.35),
	s(T.plongee, 'aspiration', 0.4), s(T.offre - 0.08, 'whoosh', 0.35),
	// 4 · la fin
	s(T.offre + 0.05, 'pose', 0.45), s(T.offre + 0.4, 'module', 0.3), s(T.offre + 0.75, 'carte', 0.25),
	s(T.logo - 0.4, 'implosion', 0.5), s(T.logo, 'final', 0.6), s(T.logo + 0.1, 'scintille', 0.3),
	s(T.whatsapp, 'pose', 0.45),
	...Array.from({length: NUMERO.length}, (_, k) => s(T.whatsapp + 0.3 + k * 0.045, touches[k % 4], 0.14)),
	s(T.tapWa, 'touche3', 0.5), s(T.tapWa + 0.02, 'envoi', 0.4),
];

/** Tout s'éteint sur la dernière demi-seconde. */
const extinction = (image: number) => interpolate(image, [DUREE - 15, DUREE - 1], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const Bruitages: React.FC = () => (
	<>
		<Audio
			src={staticFile('nebula30/sfx/nappe.wav')}
			loop
			loopVolumeCurveBehavior="extend"
			volume={(f) => 0.3 * MIX * interpolate(f, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) * extinction(f)}
		/>
		{SONS.map(([quand, son, volume], n) => {
			const de = Math.max(0, Math.round(quand * FPS));
			const duree = Math.min(Math.ceil(LONGUEUR[son] * FPS) + 2, DUREE - de);
			if (duree <= 0) return null;
			return (
				<Sequence key={n} from={de} durationInFrames={duree} layout="none" name={son}>
					<Audio src={staticFile(`nebula30/sfx/${son}.wav`)} volume={(f) => volume * MIX * extinction(de + f)} />
				</Sequence>
			);
		})}
	</>
);
