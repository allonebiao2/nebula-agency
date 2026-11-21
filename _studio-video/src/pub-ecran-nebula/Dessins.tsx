/**
 * Les dessins au trait de la pub écran : quatre produits d'EXEMPLE (robe, sac, parfum, escarpins) et les petites
 * icônes. Aucune image générée : ce sont des traits SVG, et les prix affichés sont des exemples.
 * ⛔ Pas le logo de WhatsApp : la bulle et l'icône de discussion sont génériques.
 */
import React from 'react';
import {Produit} from './donnees';

type Trait = {couleur?: string; epaisseur?: number; taille?: number};

const svg = (taille: number, ratio = 1.2) => ({width: taille, height: taille * ratio, viewBox: '0 0 200 240'});

/** La robe en wax : un bustier, une jupe évasée, et les ronds du pagne. */
const Robe: React.FC<Trait> = ({couleur = '#F5F3FF', epaisseur = 3.2, taille = 200}) => (
	<svg {...svg(taille)} fill="none" stroke={couleur} strokeWidth={epaisseur} strokeLinecap="round" strokeLinejoin="round">
		<path d="M80 24 L86 58 M120 24 L114 58" />
		<path d="M86 58 Q100 68 114 58 L119 104 Q100 110 81 104 Z" />
		<path d="M81 104 Q66 160 44 214 Q100 230 156 214 Q134 160 119 104" />
		<path d="M83 116 Q100 121 117 116" opacity={0.7} />
		<circle cx={100} cy={160} r={11} opacity={0.75} />
		<circle cx={100} cy={160} r={4} opacity={0.75} />
		<circle cx={74} cy={196} r={8} opacity={0.6} />
		<circle cx={126} cy={196} r={8} opacity={0.6} />
		<path d="M70 150 Q78 142 86 150 M114 150 Q122 142 130 150" opacity={0.55} />
	</svg>
);

/** Le sac à main : le corps, l'anse, le rabat et son fermoir. */
const Sac: React.FC<Trait> = ({couleur = '#F5F3FF', epaisseur = 3.2, taille = 200}) => (
	<svg {...svg(taille)} fill="none" stroke={couleur} strokeWidth={epaisseur} strokeLinecap="round" strokeLinejoin="round">
		<path d="M70 104 Q70 54 100 54 Q130 54 130 104" />
		<path d="M48 104 L152 104 L164 204 Q165 214 154 214 L46 214 Q35 214 36 204 Z" />
		<path d="M48 104 L100 140 L152 104" opacity={0.8} />
		<circle cx={100} cy={142} r={7} />
		<path d="M60 186 L140 186" opacity={0.4} />
	</svg>
);

/** Le parfum : le flacon, le col, le bouchon et l'étiquette. */
const Parfum: React.FC<Trait> = ({couleur = '#F5F3FF', epaisseur = 3.2, taille = 200}) => (
	<svg {...svg(taille)} fill="none" stroke={couleur} strokeWidth={epaisseur} strokeLinecap="round" strokeLinejoin="round">
		<rect x={80} y={34} width={40} height={36} rx={8} />
		<path d="M90 70 L90 92 M110 70 L110 92" />
		<rect x={52} y={92} width={96} height={124} rx={18} />
		<rect x={72} y={132} width={56} height={44} rx={6} opacity={0.75} />
		<path d="M84 150 L116 150 M90 160 L110 160" opacity={0.6} />
		<path d="M60 110 Q66 102 74 100" opacity={0.5} />
	</svg>
);

/** L'escarpin : la semelle, l'empeigne et le talon. */
const Chaussures: React.FC<Trait> = ({couleur = '#F5F3FF', epaisseur = 3.2, taille = 200}) => (
	<svg {...svg(taille)} fill="none" stroke={couleur} strokeWidth={epaisseur} strokeLinecap="round" strokeLinejoin="round">
		<path d="M30 176 Q34 160 56 158 Q84 154 104 138 Q126 118 146 116 Q170 114 172 140 L172 168" />
		<path d="M30 176 Q60 182 96 176 Q130 170 150 168 L172 168" />
		<path d="M150 168 L158 212 L168 212 L172 168" />
		<path d="M104 138 Q116 150 132 148" opacity={0.6} />
	</svg>
);

export const DESSINS: Record<Produit, React.FC<Trait>> = {robe: Robe, sac: Sac, parfum: Parfum, chaussures: Chaussures};

export const Dessin: React.FC<Trait & {produit: Produit}> = ({produit, ...trait}) => {
	const D = DESSINS[produit];
	return <D {...trait} />;
};

/* ─────────────────────────── les icônes ─────────────────────────── */

type Icone = {taille?: number; couleur?: string};

export const Oeil: React.FC<Icone> = ({taille = 22, couleur = '#F5F3FF'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
		<path d="M2 12 Q12 3 22 12 Q12 21 2 12 Z" />
		<circle cx={12} cy={12} r={3.2} />
	</svg>
);

/** Une ou deux coches, grises : envoyé, puis remis, jamais lu. */
export const Coches: React.FC<Icone & {deux: number}> = ({taille = 26, couleur = 'rgba(245,243,255,0.5)', deux}) => (
	<svg width={taille * 1.35} height={taille} viewBox="0 0 32 24" fill="none" stroke={couleur} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round">
		<path d="M3 13 L8.5 18.5 L19 6" />
		<path d="M12 18.5 L13.5 18.5 L24 6" opacity={deux} />
	</svg>
);

export const Lune: React.FC<Icone> = ({taille = 24, couleur = '#F5F3FF'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill={couleur}>
		<path d="M15.5 2.5 A9.5 9.5 0 1 0 21.5 15 A7.6 7.6 0 1 1 15.5 2.5 Z" />
	</svg>
);

/** La bulle de discussion générique (pas le logo d'une application). */
export const Bulle: React.FC<Icone> = ({taille = 28, couleur = '#22D3EE'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
		<path d="M4 5.5 Q4 4 5.5 4 L18.5 4 Q20 4 20 5.5 L20 14.5 Q20 16 18.5 16 L10 16 L6 20 L6 16 L5.5 16 Q4 16 4 14.5 Z" />
		<path d="M8.5 9 L15.5 9 M8.5 12 L13 12" />
	</svg>
);

export const Lien: React.FC<Icone> = ({taille = 34, couleur = '#07060D'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round">
		<path d="M10 14 L14 10" />
		<path d="M8.5 11.5 L6.6 13.4 A3.4 3.4 0 0 0 11.4 18.2 L13.3 16.3" />
		<path d="M15.5 12.5 L17.4 10.6 A3.4 3.4 0 0 0 12.6 5.8 L10.7 7.7" />
	</svg>
);

export const Envoyer: React.FC<Icone> = ({taille = 36, couleur = '#07060D'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round">
		<path d="M4 12 L20 4.5 L15 20 L11.5 13 Z" />
		<path d="M11.5 13 L20 4.5" />
	</svg>
);

export const Coche: React.FC<Icone> = ({taille = 22, couleur = '#07060D'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round">
		<path d="M5 12.5 L10 17.5 L19 7" />
	</svg>
);

export const Cadenas: React.FC<Icone> = ({taille = 14, couleur = '#5b5750'}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth={2.4} strokeLinecap="round">
		<rect x={5} y={11} width={14} height={10} rx={2} />
		<path d="M8 11 V8 A4 4 0 0 1 16 8 V11" />
	</svg>
);

/** La barre d'état d'un téléphone : l'heure, le réseau, la batterie. */
export const BarreEtat: React.FC<{heure: string; couleur: string; police: string}> = ({heure, couleur, police}) => (
	<div style={{position: 'absolute', top: 15, left: 26, right: 22, display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: couleur, fontFamily: police, fontWeight: 600, fontSize: 15}}>
		<span>{heure}</span>
		<div style={{display: 'flex', gap: 6, alignItems: 'center'}}>
			<svg width={18} height={12} viewBox="0 0 18 12" fill={couleur}>
				<rect x={0} y={8} width={3} height={4} rx={1} />
				<rect x={5} y={5} width={3} height={7} rx={1} />
				<rect x={10} y={2.5} width={3} height={9.5} rx={1} />
				<rect x={15} y={0} width={3} height={12} rx={1} opacity={0.4} />
			</svg>
			<svg width={26} height={12} viewBox="0 0 26 12" fill="none" stroke={couleur} strokeWidth={1.2}>
				<rect x={0.6} y={0.6} width={22} height={10.8} rx={3} opacity={0.5} />
				<rect x={2.5} y={2.5} width={14} height={7} rx={1.5} fill={couleur} stroke="none" />
				<path d="M24.5 4 V8" strokeLinecap="round" opacity={0.5} />
			</svg>
		</div>
	</div>
);
