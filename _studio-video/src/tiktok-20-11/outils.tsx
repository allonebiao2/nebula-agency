/**
 * Les outils du TikTok du 20/11 : le temps, les mots qui tombent, la secousse,
 * l'espace du fond, le téléphone dessiné et ses icônes.
 * ⚠️ Aucune animation CSS ni `transition:` : tout se calcule depuis `t` (secondes),
 * sinon le rendu photographierait l'animation figée ou au hasard.
 * ⚠️ Toute rotation s'écrit avec son `deg` (un `rotate: 12` nu est ignoré sans un mot).
 */
import React, {CSSProperties} from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring} from 'remotion';
import {C, DEGRADE, FPS, HAUTEUR, LARGEUR} from './donnees';
import {MONO, TEXTE} from './polices';

export const CL = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** De `de` à `vers` entre les instants a et b (secondes), bornée. */
export const lin = (t: number, a: number, b: number, de = 0, vers = 1, easing = Easing.out(Easing.cubic)) =>
	interpolate(t, [a, b], [de, vers], {...CL, easing});

/** Un ressort qui part à `debut` : 0 avant, ~1 après (avec un léger rebond). */
export const ressort = (t: number, debut: number, raideur = 180, amorti = 13, masse = 0.9) =>
	t < debut ? 0 : spring({frame: Math.round((t - debut) * FPS), fps: FPS, config: {stiffness: raideur, damping: amorti, mass: masse}});

/** La secousse de l'image après un choc : [instant, force en px]. */
export const secousse = (t: number, coups: [number, number][]) => {
	let x = 0;
	let y = 0;
	let r = 0;
	for (const [a, k] of coups) {
		const d = t - a;
		if (d < 0 || d > 0.42) continue;
		const e = (1 - d / 0.42) ** 2;
		x += Math.sin(d * 95) * k * e;
		y += Math.cos(d * 83) * k * e * 0.8;
		r += Math.sin(d * 61) * k * e * 0.035;
	}
	return `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg)`;
};

/** L'éclair blanc d'un choc : [instant, force]. */
export const eclair = (t: number, coups: [number, number][]) =>
	Math.max(0, ...coups.map(([a, k]) => (t < a ? 0 : Math.max(0, 1 - (t - a) / 0.2) * k)));

/** Le texte en dégradé des statuts (violet → cyan). */
export const TEXTE_DEGRADE: CSSProperties = {
	backgroundImage: DEGRADE,
	WebkitBackgroundClip: 'text',
	backgroundClip: 'text',
	color: 'transparent',
};

export type Mot = {m: string; a: number; style?: CSSProperties};

/** Une phrase découpée en mots qui tombent l'un après l'autre (espace insécable = même mot). */
export const phrase = (texte: string, debut: number, pas = 0.11, style?: CSSProperties): Mot[] =>
	texte.split(' ').map((m, i) => ({m, a: debut + i * pas, style}));

/** Les mots, chacun sur son ressort ; la ligne se coupe d'elle-même entre deux mots. */
export const Mots: React.FC<{t: number; mots: Mot[]; style?: CSSProperties; align?: 'center' | 'flex-start'}> = ({t, mots, style, align = 'center'}) => (
	<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: align, columnGap: '0.38em', ...style}}>
		{mots.map((w, i) => {
			const s = ressort(t, w.a, 230, 14);
			return (
				<span
					key={i}
					style={{
						display: 'inline-block',
						whiteSpace: 'pre',
						opacity: Math.min(1, s * 1.8),
						transform: `translateY(${((1 - s) * 0.45).toFixed(3)}em) scale(${(0.72 + 0.28 * s).toFixed(3)})`,
						...w.style,
					}}
				>
					{w.m}
				</span>
			);
		})}
	</div>
);

/** Le petit sur-titre en capitales espacées, en cyan (celui des statuts). */
export const Etiquette: React.FC<{t: number; a: number; texte: string; top: number}> = ({t, a, texte, top}) => {
	const p = lin(t, a, a + 0.45);
	return (
		<div
			style={{
				position: 'absolute',
				top,
				left: 0,
				right: 0,
				textAlign: 'center',
				fontFamily: TEXTE,
				fontWeight: 700,
				fontSize: 30,
				letterSpacing: '0.32em',
				color: C.cyan,
				opacity: p,
				clipPath: `inset(0 ${((1 - p) * 50).toFixed(2)}% 0 ${((1 - p) * 50).toFixed(2)}%)`,
			}}
		>
			{texte}
		</div>
	);
};

/** Les étoiles du fond : fixes d'un rendu à l'autre (`random` à graine), elles scintillent et dérivent. */
const ETOILES = Array.from({length: 90}, (_, i) => ({
	x: random(`ex${i}`) * LARGEUR,
	y: random(`ey${i}`) * HAUTEUR,
	r: 1 + random(`er${i}`) * 2.6,
	v: 6 + random(`ev${i}`) * 22,
	f: 0.6 + random(`ef${i}`) * 2.2,
	p: random(`ep${i}`) * 6.28,
}));

export const Espace: React.FC<{t: number}> = ({t}) => (
	<AbsoluteFill style={{background: C.encre}}>
		<AbsoluteFill
			style={{
				background: [
					`radial-gradient(circle at ${(28 + 7 * Math.sin(t * 0.4)).toFixed(2)}% ${(26 + 5 * Math.cos(t * 0.3)).toFixed(2)}%, rgba(147,51,234,.36), transparent 46%)`,
					`radial-gradient(circle at ${(76 + 6 * Math.cos(t * 0.33)).toFixed(2)}% ${(60 + 6 * Math.sin(t * 0.27)).toFixed(2)}%, rgba(79,111,255,.30), transparent 50%)`,
					`radial-gradient(circle at ${(50 + 9 * Math.sin(t * 0.21)).toFixed(2)}% 96%, rgba(34,211,238,.16), transparent 45%)`,
				].join(', '),
			}}
		/>
		{ETOILES.map((e, i) => (
			<div
				key={i}
				style={{
					position: 'absolute',
					left: e.x,
					top: (e.y + t * e.v) % HAUTEUR,
					width: e.r,
					height: e.r,
					borderRadius: '50%',
					background: C.lumiere,
					opacity: 0.25 + 0.65 * Math.abs(Math.sin(t * e.f + e.p)),
					boxShadow: e.r > 2.6 ? `0 0 ${e.r * 3}px rgba(201,210,255,.8)` : undefined,
				}}
			/>
		))}
	</AbsoluteFill>
);

/** Le téléphone, dessiné (jamais une image générée) : une coque, un îlot, un écran. */
export const Telephone: React.FC<{l: number; h: number; ecran: string; lueur?: number; children: React.ReactNode}> = ({l, h, ecran, lueur = 1, children}) => (
	<div
		style={{
			width: l,
			height: h,
			borderRadius: l * 0.15,
			padding: 12,
			boxSizing: 'border-box',
			background: 'linear-gradient(145deg, #4a5078, #15172e 38%, #0c0d1f 62%, #3a4170)',
			boxShadow: `0 40px 120px rgba(79,111,255,${(0.38 * lueur).toFixed(3)}), 0 0 0 2px rgba(201,210,255,.16), inset 0 0 0 2px rgba(255,255,255,.08)`,
		}}
	>
		<div style={{position: 'relative', width: '100%', height: '100%', borderRadius: l * 0.12, overflow: 'hidden', background: ecran}}>
			{children}
			<div style={{position: 'absolute', top: 12, left: '50%', width: 116, height: 32, marginLeft: -58, borderRadius: 16, background: '#05060f'}} />
		</div>
	</div>
);

/** La barre d'état du téléphone : l'heure à gauche, le réseau à droite. */
export const BarreEtat: React.FC<{heure: string; encre: string; reseau?: string; barres?: number; clignote?: number}> = ({heure, encre, reseau, barres = 4, clignote = 1}) => (
	<div style={{position: 'absolute', top: 16, left: 30, right: 30, height: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: encre}}>
		<span style={{fontFamily: MONO, fontWeight: 700, fontSize: 21}}>{heure}</span>
		<span style={{display: 'flex', alignItems: 'flex-end', gap: 4}}>
			{reseau ? <span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 19, marginRight: 6}}>{reseau}</span> : null}
			{[8, 12, 16, 20].map((hh, i) => (
				<span key={i} style={{width: 5, height: hh, borderRadius: 2, background: encre, opacity: i < barres ? (i === 0 ? clignote : 1) : 0.22}} />
			))}
		</span>
	</div>
);

/** La bulle d'un message reçu sur WhatsApp, en mode sombre. */
export const Bulle: React.FC<{texte: string; heure: string; taille?: number}> = ({texte, heure, taille = 62}) => (
	<div
		style={{
			position: 'relative',
			background: C.bulle,
			color: C.bulleTexte,
			fontFamily: TEXTE,
			fontWeight: 600,
			fontSize: taille,
			padding: `${taille * 0.38}px ${taille * 0.55}px ${taille * 0.42}px`,
			borderRadius: taille * 0.42,
			borderTopLeftRadius: 8,
			boxShadow: '0 24px 70px rgba(0,0,0,.45)',
			whiteSpace: 'nowrap',
		}}
	>
		<svg width={28} height={28} viewBox="0 0 28 28" style={{position: 'absolute', left: -20, top: 0}}>
			<path d="M28 0 H6 Q0 0 4 5 L28 28 Z" fill={C.bulle} />
		</svg>
		{texte}
		<span style={{fontFamily: MONO, fontWeight: 500, fontSize: taille * 0.36, color: C.bulleHeure, marginLeft: taille * 0.4}}>{heure}</span>
	</div>
);

/** Le doigt qui touche : un point qui appuie, puis une onde. */
export const Toucher: React.FC<{t: number; a: number; x: number; y: number; couleur?: string}> = ({t, a, x, y, couleur = C.lumiere}) => {
	if (t < a - 0.25 || t > a + 0.7) return null;
	const approche = lin(t, a - 0.25, a);
	const appui = t < a ? 1 : 1 - 0.25 * Math.max(0, 1 - (t - a) / 0.15);
	const onde = lin(t, a, a + 0.55, 0, 1, Easing.out(Easing.quad));
	const depart = lin(t, a + 0.3, a + 0.6);
	return (
		<>
			<div
				style={{
					position: 'absolute',
					left: x - 38,
					top: y - 38,
					width: 76,
					height: 76,
					borderRadius: '50%',
					background: 'rgba(244,245,255,.38)',
					border: '3px solid rgba(244,245,255,.85)',
					opacity: approche * (1 - depart),
					transform: `scale(${(appui * (1.3 - 0.3 * approche)).toFixed(3)})`,
				}}
			/>
			{t >= a ? (
				<div
					style={{
						position: 'absolute',
						left: x - 40 - onde * 120,
						top: y - 40 - onde * 120,
						width: 80 + onde * 240,
						height: 80 + onde * 240,
						borderRadius: '50%',
						border: `4px solid ${couleur}`,
						opacity: 0.9 * (1 - onde),
					}}
				/>
			) : null}
		</>
	);
};

/** Une étincelle à quatre branches. */
export const Etincelle: React.FC<{x: number; y: number; taille: number; opacite: number; couleur?: string; angle?: number}> = ({x, y, taille, opacite, couleur = C.lumiere, angle = 0}) => (
	<svg
		width={taille}
		height={taille}
		viewBox="-10 -10 20 20"
		style={{position: 'absolute', left: x - taille / 2, top: y - taille / 2, opacity: opacite, transform: `rotate(${angle.toFixed(2)}deg)`, filter: `drop-shadow(0 0 ${taille / 4}px ${couleur})`}}
	>
		<path d="M0 -10 L2.4 -2.4 L10 0 L2.4 2.4 L0 10 L-2.4 2.4 L-10 0 L-2.4 -2.4 Z" fill={couleur} />
	</svg>
);

/** Le cadeau qui se dessine trait par trait (p de 0 à 1), puis se remplit. */
export const Cadeau: React.FC<{p: number; remplissage: number; taille: number}> = ({p, remplissage, taille}) => {
	const trait = (k: number) => ({
		pathLength: 1,
		strokeDasharray: '1 1',
		strokeDashoffset: 1 - Math.max(0, Math.min(1, p * 1.6 - k * 0.15)),
	});
	return (
		<svg width={taille} height={taille} viewBox="0 0 200 200" fill="none" strokeLinecap="round" strokeLinejoin="round">
			<path d="M42 92 H158 V178 H42 Z" stroke={C.lumiere} strokeWidth={7} fill={`rgba(244,245,255,${(0.16 * remplissage).toFixed(3)})`} {...trait(0)} />
			<path d="M30 66 H170 V92 H30 Z" stroke={C.lumiere} strokeWidth={7} fill={`rgba(244,245,255,${(0.28 * remplissage).toFixed(3)})`} {...trait(1)} />
			<path d="M100 66 V178" stroke={C.or} strokeWidth={10} {...trait(2)} />
			<path d="M100 64 C82 30 50 38 64 58 C72 68 90 67 100 64" stroke={C.or} strokeWidth={8} {...trait(3)} />
			<path d="M100 64 C118 30 150 38 136 58 C128 68 110 67 100 64" stroke={C.or} strokeWidth={8} {...trait(3.4)} />
		</svg>
	);
};

/** L'image absente : un cadre et une montagne en gris (avant que la photo n'arrive). */
export const ImageVide: React.FC<{taille: number; couleur: string}> = ({taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 100 100" fill="none" stroke={couleur} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round">
		<rect x={10} y={18} width={80} height={64} rx={10} />
		<circle cx={34} cy={40} r={8} />
		<path d="M14 76 L42 52 L60 66 L72 56 L88 72" />
	</svg>
);

/** Le combiné de téléphone (pictogramme « call » de Material Icons, licence Apache 2.0). */
export const Combine: React.FC<{taille: number; couleur: string}> = ({taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24">
		<path
			fill={couleur}
			d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"
		/>
	</svg>
);

/** Une bulle de discussion qui porte le combiné : dessinée ici, ce n'est pas le logo de WhatsApp. */
export const BulleAppel: React.FC<{taille: number; couleur: string}> = ({taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 48 48" fill="none">
		<path d="M24 4 C13 4 4.5 12.4 4.5 23 c0 3.6 1 7 2.8 9.9 L5 43 l10.4-2.6 c2.6 1.4 5.5 2.1 8.6 2.1 11 0 19.5-8.4 19.5-19 S35 4 24 4 Z" stroke={couleur} strokeWidth={3.4} strokeLinejoin="round" />
		<g transform="translate(13 12.5) scale(0.92)">
			<path
				fill={couleur}
				d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"
			/>
		</g>
	</svg>
);

/** Le croissant de lune. */
export const Lune: React.FC<{taille: number}> = ({taille}) => (
	<svg width={taille} height={taille} viewBox="0 0 100 100" style={{filter: 'drop-shadow(0 0 18px rgba(255,210,122,.75))'}}>
		<path d="M62 8 A44 44 0 1 0 92 70 A36 36 0 1 1 62 8 Z" fill={C.or} />
	</svg>
);

/** Le document PDF, lourd : une feuille, son coin plié, son bandeau rouge. */
export const Pdf: React.FC<{taille: number}> = ({taille}) => (
	<svg width={taille} height={(taille * 380) / 300} viewBox="0 0 300 380">
		<path d="M20 10 H210 L280 80 V370 H20 Z" fill="#e9ebfa" />
		<path d="M210 10 V80 H280 Z" fill="#c3c7e3" />
		{[110, 142, 174].map((y, i) => (
			<rect key={y} x={52} y={y} width={[180, 150, 196][i]} height={13} rx={6.5} fill="#c9cde6" />
		))}
		<rect x={0} y={206} width={232} height={92} rx={14} fill="#e5484d" />
		<text x={116} y={272} textAnchor="middle" fontFamily={TEXTE} fontWeight={900} fontSize={66} fill="#fff">
			PDF
		</text>
		{[322, 346].map((y, i) => (
			<rect key={y} x={52} y={y} width={[196, 120][i]} height={12} rx={6} fill="#c9cde6" />
		))}
	</svg>
);

/** L'horloge dont les aiguilles filent. */
export const Horloge: React.FC<{t: number; taille: number; couleur: string}> = ({t, taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 40 40" fill="none" stroke={couleur} strokeWidth={3.2} strokeLinecap="round">
		<circle cx={20} cy={20} r={17} />
		<line x1={20} y1={20} x2={20} y2={9} transform={`rotate(${((t * 1440) % 360).toFixed(1)} 20 20)`} />
		<line x1={20} y1={20} x2={28} y2={20} transform={`rotate(${((t * 120) % 360).toFixed(1)} 20 20)`} />
	</svg>
);

/** Le cercle de chargement qui tourne sans fin. */
export const Rouet: React.FC<{t: number; taille: number; couleur: string}> = ({t, taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 40 40" fill="none" style={{transform: `rotate(${((t * 400) % 360).toFixed(1)}deg)`}}>
		<circle cx={20} cy={20} r={16} stroke="rgba(201,210,255,.18)" strokeWidth={4} />
		<path d="M20 4 A16 16 0 0 1 36 20" stroke={couleur} strokeWidth={4} strokeLinecap="round" />
	</svg>
);

/** La coche qui se trace. */
export const Coche: React.FC<{p: number; taille: number; couleur: string}> = ({p, taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 40 40" fill="none">
		<path d="M8 21 L17 30 L33 11" stroke={couleur} strokeWidth={5.5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
	</svg>
);

/** Un nombre écrit à la française : 15 000. */
export const millier = (n: number) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

/** Un minuteur m:ss. */
export const minuteur = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
