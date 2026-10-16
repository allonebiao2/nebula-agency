/**
 * LES BRUITAGES · un son par geste, calé sur le même instant que l'animation qu'il
 * accompagne (déduit du minutage, jamais une seconde recopiée). Ce sont ceux de la
 * vidéo NEBULA, SYNTHÉTISÉS par `_outils/nebula30_bruitages.py` : aucun fichier
 * tiers, aucun droit à gérer, recopiés dans public/grain35/sfx/.
 * Discrets : la voix et la musique passent devant. Le mastering final (−14 LUFS)
 * se fait sur le son rendu, comme pour NEBULA.
 */
import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
import {FPS, MIX} from './donnees';
import {motDe, V1, V2, V3, V4} from './instants';
import {DUREE_LOGO} from './Logo';
import {MUSIQUE, REPLIQUES} from './minutage';
import {T_INSTITUT, T_PLONGE, T_VOUS} from './scenes/Ouverture';

type Son = 'whoosh' | 'scintille' | 'etincelle' | 'pose' | 'carte' | 'envoi' | 'souffle' | 'trace' | 'declic' | 'touche1' | 'touche2' | 'touche3' | 'touche4';

const DUREE: Record<Son, number> = {
	whoosh: 1.55, scintille: 3.6, etincelle: 3.6, pose: 0.62, carte: 0.16, envoi: 1.0, souffle: 2.3, trace: 1.6, declic: 0.42,
	touche1: 0.06, touche2: 0.06, touche3: 0.06, touche4: 0.06,
};

const s = (quand: number, son: Son, volume: number): [number, Son, number] => [quand, son, volume];

const tRdv = motDe('ecrivez', 'rendez', REPLIQUES.ecrivez[0] + 0.4);
const envoi = Math.min(motDe('ecrivez', 'whatsapp', REPLIQUES.ecrivez[1] - 0.4) + 0.1, tRdv + 0.6);
const frappe = Array.from({length: 11}, (_, k) => s(tRdv - 0.05 + k * 0.045, (['touche1', 'touche2', 'touche3', 'touche4'] as const)[k % 4], 0.12));

export const SONS: [number, Son, number][] = [
	// l'accroche : l'œil se dessine, les mots se dissolvent, la plongée dans la pupille
	s(0.02, 'trace', 0.22), s(0.85, 'pose', 0.18),
	s(T_VOUS - 0.05, 'scintille', 0.28),
	s(T_PLONGE, 'souffle', 0.38), s(T_INSTITUT - 0.05, 'etincelle', 0.26),
	// les maisons
	s(motDe('maisons', 'sothys', 9.4) - 0.08, 'pose', 0.2), s(motDe('maisons', 'sultane', 10.4) - 0.08, 'pose', 0.2),
	// les avis (la vague finit sur la relance)
	s(V1.a, 'whoosh', 0.3), s(MUSIQUE.relanceAvis + 0.05, 'scintille', 0.18),
	...[0, 1, 2, 3, 4].map((k) => s(MUSIQUE.relanceAvis + 0.05 + k * 0.1, 'carte', 0.07)),
	// les trois temps
	s(V2.a, 'whoosh', 0.26), s(motDe('visage', 'illumine', 17) - 0.1, 'etincelle', 0.24),
	s(REPLIQUES.levres[0] - 0.1, 'trace', 0.2),
	s(MUSIQUE.arret, 'declic', 0.22),
	s(MUSIQUE.relance, 'scintille', 0.42), s(MUSIQUE.relance + 0.02, 'etincelle', 0.24),
	s(REPLIQUES.piqure[0] + 0.4, 'pose', 0.16),
	// l'appel : le doigt, WhatsApp, la frappe, l'envoi
	s(V3.a, 'whoosh', 0.28), s(REPLIQUES.tour[0] + 0.75, 'declic', 0.26), s(REPLIQUES.tour[0] + 0.9, 'whoosh', 0.1),
	...frappe, s(envoi, 'envoi', 0.3),
	// la signature : le sourcil, le G, LE GRAIN
	s(V4.a, 'whoosh', 0.26), s(MUSIQUE.logo, 'trace', 0.2), s(MUSIQUE.logo + 1.1, 'trace', 0.16),
	s(MUSIQUE.grain, 'etincelle', 0.42), s(MUSIQUE.grain + 0.02, 'scintille', 0.26),
	s(MUSIQUE.logo + DUREE_LOGO - 0.6, 'pose', 0.14),
];

export const Bruitages: React.FC = () => (
	<>
		{SONS.map(([quand, son, volume], i) => (
			<Sequence key={i} from={Math.max(0, Math.round(quand * FPS))} durationInFrames={Math.ceil(DUREE[son] * FPS) + 2} layout="none">
				<Audio src={staticFile(`grain35/sfx/${son}.wav`)} volume={volume * MIX} />
			</Sequence>
		))}
	</>
);
