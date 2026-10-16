/**
 * LES PREUVES : ce que la vidéo ne peut pas montrer (on n'a qu'une photo), elle le
 * fait DIRE par d'autres.
 *
 *  · `Maisons` (sombre) : « Des soins signés Sothys Paris et Sultane de Saba. »
 *    Les deux noms en très grand, chacun au moment où la voix le prononce, avec un
 *    reflet d'or qui passe dessus. Les noms sont écrits en lettres : leurs logos
 *    sont leurs marques, pas les nôtres.
 *  · `Avis` (clair, sur la relance de la musique) : SES vrais avis Google, mot pour
 *    mot. « Les meilleurs à Cotonou ! » en phare, ses 5 étoiles qui s'allument,
 *    puis un fil d'avis qui défile, comme sur la fiche.
 */
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {AVIS, AVIS_PHARE, C} from '../donnees';
import {Fond, Grains} from '../Fond';
import {MOTS, MUSIQUE, REPLIQUES} from '../minutage';
import {enOr, Etiquette, Filet, Mots, p, ressort} from '../outils';
import {ACCENT, TEXTE, TITRE} from '../polices';

const mot = (debutDe: string, defaut: number) =>
	MOTS.find((m) => m.replique === 'maisons' && m.mot.startsWith(debutDe))?.debut ?? defaut;

/** Un reflet qui traverse un texte (le texte doit être en `enOr`). */
const refletOr = (e: number): React.CSSProperties => ({
	...enOr(
		`linear-gradient(105deg, #a8803f 0%, #d4af72 ${mix100(e) - 18}%, #fff6dc ${mix100(e)}%, #d4af72 ${mix100(e) + 18}%, #a8803f 100%)`,
	),
});
const mix100 = (e: number) => -30 + e * 160;

export const Maisons: React.FC<{t: number}> = ({t}) => {
	const [a, b] = REPLIQUES.maisons;
	const tS = mot('Sothys', a + 0.8) - 0.08;
	const tU = mot('Sultane', a + 1.8) - 0.08;
	const eS = ressort(t, tS, {damping: 15, stiffness: 110, mass: 0.8});
	const eU = ressort(t, tU, {damping: 15, stiffness: 110, mass: 0.8});
	return (
		<AbsoluteFill>
			<Fond t={t} lumiere={{x: 540, y: 880}} />
			<Grains t={t} densite={0.9} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 360, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22}}>
				<Etiquette texte="Nos maisons partenaires" taille={28} opacite={p(t, a - 0.2, a + 0.4)} />
				<Filet e={p(t, a, a + 0.8)} largeur={320} />
			</div>
			<div style={{position: 'absolute', left: 60, right: 60, top: 500, textAlign: 'center'}}>
				<Mots t={t} texte="Des soins signés" a={a} b={tS - 0.05} taille={66} couleur={C.rosePale} />
			</div>
			{/* Sothys */}
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 640,
					textAlign: 'center',
					opacity: Math.min(1, eS * 1.4),
					transform: `translateY(${(1 - eS) * 50}px) scale(${0.92 + 0.08 * eS})`,
					filter: eS < 0.95 ? `blur(${(1 - eS) * 10}px)` : undefined,
				}}
			>
				<div style={{fontFamily: TITRE, fontSize: 190, lineHeight: 1, ...refletOr(p(t, tS + 0.2, tS + 1.3))}}>Sothys</div>
				<div style={{fontFamily: TEXTE, fontSize: 34, letterSpacing: '0.62em', color: C.or, marginTop: 10, paddingLeft: '0.62em'}}>PARIS</div>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 980, display: 'flex', justifyContent: 'center', opacity: p(t, tU - 0.4, tU)}}>
				<div style={{fontFamily: ACCENT, fontStyle: 'italic', fontSize: 64, color: C.roseClair}}>&</div>
			</div>
			{/* Sultane de Saba */}
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 1080,
					textAlign: 'center',
					opacity: Math.min(1, eU * 1.4),
					transform: `translateY(${(1 - eU) * 50}px) scale(${0.92 + 0.08 * eU})`,
					filter: eU < 0.95 ? `blur(${(1 - eU) * 10}px)` : undefined,
				}}
			>
				<div style={{fontFamily: ACCENT, fontStyle: 'italic', fontSize: 150, lineHeight: 1, paddingRight: 12, ...refletOr(p(t, tU + 0.2, tU + 1.3))}}>Sultane de Saba</div>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 1420, textAlign: 'center', opacity: p(t, tU + 0.5, tU + 1.1)}}>
				<Etiquette texte="Exclusivement" taille={24} couleur={C.gris} />
			</div>
		</AbsoluteFill>
	);
};

const Etoiles: React.FC<{t: number; a: number; taille: number; pas?: number}> = ({t, a, taille, pas = 0.1}) => (
	<div style={{display: 'flex', gap: taille * 0.18, justifyContent: 'center'}}>
		{[0, 1, 2, 3, 4].map((i) => {
			const e = ressort(t, a + i * pas, {damping: 9, stiffness: 220, mass: 0.5});
			return (
				<svg key={i} width={taille} height={taille} viewBox="-50 -50 100 100" style={{transform: `scale(${e}) rotate(${(1 - e) * -40}deg)`, opacity: Math.min(1, e * 2)}}>
					<defs>
						<linearGradient id={`et${i}`} x1="0" y1="0" x2="0" y2="1">
							<stop offset="0%" stopColor="#f6dfa8" />
							<stop offset="100%" stopColor="#b88a3e" />
						</linearGradient>
					</defs>
					<path d="M0,-46 L13,-15 L46,-14 L20,7 L29,40 L0,21 L-29,40 L-20,7 L-46,-14 L-13,-15 Z" fill={`url(#et${i})`} />
				</svg>
			);
		})}
	</div>
);

/** Une carte d'avis, comme sur la fiche : les étoiles, le texte, le prénom. */
const Carte: React.FC<{texte: string; prenom: string}> = ({texte, prenom}) => (
	<div
		style={{
			width: 820,
			padding: '30px 40px 28px',
			borderRadius: 30,
			background: '#fffaf6',
			boxShadow: '0 18px 50px -22px rgba(122,46,78,.45), 0 0 0 1px rgba(196,100,138,.12)',
			display: 'flex',
			flexDirection: 'column',
			gap: 14,
		}}
	>
		<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
			<div style={{display: 'flex', gap: 6}}>
				{[0, 1, 2, 3, 4].map((i) => (
					<svg key={i} width={26} height={26} viewBox="-50 -50 100 100">
						<path d="M0,-46 L13,-15 L46,-14 L20,7 L29,40 L0,21 L-29,40 L-20,7 L-46,-14 L-13,-15 Z" fill="#d9a441" />
					</svg>
				))}
			</div>
			<div style={{fontFamily: TEXTE, fontSize: 22, letterSpacing: '0.12em', color: C.gris, textTransform: 'uppercase'}}>Avis Google</div>
		</div>
		<div style={{fontFamily: TITRE, fontSize: 44, lineHeight: 1.15, color: C.encre}}>« {texte} »</div>
		<div style={{fontFamily: TEXTE, fontSize: 26, fontWeight: 500, color: C.rose}}>{prenom}</div>
	</div>
);

export const Avis: React.FC<{t: number}> = ({t}) => {
	const a = MUSIQUE.relanceAvis;
	const ePhare = ressort(t, a + 0.05, {damping: 16, stiffness: 120, mass: 0.7});
	// le fil : il entre par le bas et monte à vitesse constante
	const debutFil = a + 0.55;
	const vitesse = 250; // px/s : les 6 avis passent en 3,3 s
	const montee = Math.max(0, t - debutFil) * vitesse;
	const pas = 250;
	return (
		<AbsoluteFill>
			<Fond t={t} clair lumiere={{x: 540, y: 520}} />
			<Grains t={t} densite={0.6} clair />
			<div style={{position: 'absolute', left: 0, right: 0, top: 210, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
				<Etiquette texte="Elles l’écrivent sur Google" taille={28} couleur={C.rose} opacite={p(t, a - 0.3, a + 0.3)} />
				<Filet e={p(t, a - 0.1, a + 0.7)} largeur={320} couleur={C.rose} />
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 330}}>
				<Etoiles t={t} a={a} taille={70} />
			</div>
			<div
				style={{
					position: 'absolute',
					left: 50,
					right: 50,
					top: 440,
					textAlign: 'center',
					fontFamily: TITRE,
					fontSize: 122,
					lineHeight: 1.0,
					color: C.encre,
					opacity: Math.min(1, ePhare * 1.3),
					transform: `translateY(${(1 - ePhare) * 40}px)`,
				}}
			>
				« Les meilleurs à <span style={{fontFamily: ACCENT, fontStyle: 'italic', color: C.rose, fontSize: '1.08em'}}>Cotonou</span> ! »
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 735, textAlign: 'center', fontFamily: TEXTE, fontSize: 30, fontWeight: 500, color: C.rose, opacity: p(t, a + 0.4, a + 0.8)}}>
				{AVIS_PHARE.prenom}
			</div>
			{/* le fil d'avis, avec un fondu en haut et en bas */}
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 830,
					height: 830,
					overflow: 'hidden',
					WebkitMaskImage: 'linear-gradient(180deg, transparent 0%, #000 14%, #000 82%, transparent 100%)',
					maskImage: 'linear-gradient(180deg, transparent 0%, #000 14%, #000 82%, transparent 100%)',
				}}
			>
				{AVIS.map((av, i) => {
					const y = 130 + i * pas - montee;
					if (y < -320 || y > 900) return null;
					return (
						<div key={i} style={{position: 'absolute', left: 130, top: y}}>
							<Carte texte={av.texte} prenom={av.prenom} />
						</div>
					);
				})}
			</div>
		</AbsoluteFill>
	);
};
