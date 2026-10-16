/**
 * Les instants partagés par l'image et les bruitages, tous DÉDUITS du minutage
 * (la voix et la musique mesurées) : jamais une seconde recopiée à la main.
 */
import type {Replique} from './donnees';
import {MOTS, MUSIQUE, REPLIQUES} from './minutage';

/** L'instant où la voix commence un mot (par le début du mot, sans la casse). */
export const motDe = (replique: Replique, debut: string, defaut: number) =>
	MOTS.find((m) => m.replique === replique && m.mot.toLowerCase().replace(/^'/, '').startsWith(debut.toLowerCase()))?.debut ?? defaut;

/** Les quatre vagues de grains : [début, durée]. La première finit sur la relance. */
export const V1 = {a: MUSIQUE.relanceAvis - 0.67, d: 0.67};
export const V2 = {a: REPLIQUES.visage[0] - 0.75, d: 0.6};
export const V3 = {a: REPLIQUES.tour[0] - 0.5, d: 0.55};
export const V4 = {a: MUSIQUE.logo - 0.55, d: 0.5};
