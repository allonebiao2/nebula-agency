/**
 * Les matières du film en 2D : grain, vignettage, bandes, pluie sur la vitre, poussière d'or, ciel, fumée,
 * rayons, fuite de lumière, gerbe, et les trois pluies du produit (étoiles, pétales, confettis).
 * Tout est déterministe (`random(graine)`), tout avance par le TEMPS : deux rendus donnent les mêmes images.
 */
import React from 'react';
import {random, Solid, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {lightLeak} from '@remotion/effects/light-leak';
import {starburst} from '@remotion/effects/starburst';
import {C, ITALIQUE, TITRE} from './donnees';
import {bruit, mix, p, plein, T, useT} from './outils';

/** Le grain de pellicule : une tuile de bruit décalée toutes les deux images. */
export const Grain: React.FC<{force?: number}> = ({force = 0.06}) => {
	const f = Math.floor(useCurrentFrame() / 2);
	return (
		<div
			style={{
				...plein,
				backgroundImage: `url(${staticFile('malettre-minuit/grain.png')})`,
				backgroundPosition: `${Math.floor(random('gx' + f) * 512)}px ${Math.floor(random('gy' + f) * 512)}px`,
				opacity: force,
				mixBlendMode: 'overlay',
				pointerEvents: 'none',
			}}
		/>
	);
};

export const Vignette: React.FC<{force?: number}> = ({force = 0.75}) => (
	<div style={{...plein, pointerEvents: 'none', background: `radial-gradient(ellipse 75% 70% at 50% 50%, transparent 55%, rgba(5,3,8,${force}) 100%)`}} />
);

/** Les bandes du cinéma (2,39:1). `ouvert` 0→1 les retire : à minuit, l'image s'ouvre en grand. */
export const Bandes: React.FC<{ouvert: number}> = ({ouvert}) => {
	const h = 138 * (1 - ouvert);
	return (
		<>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: h, background: C.nuit3}} />
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: h, background: C.nuit3}} />
		</>
	);
};

/** La pluie sur la vitre de Paris : des perles posées, et des gouttes qui glissent en laissant leur trace. */
export const PluieVitre: React.FC<{force?: number}> = ({force = 1}) => {
	const t = useT();
	const {width, height} = useVideoConfig();
	const perles = Array.from({length: 170}, (_, i) => {
		const r = 2 + random('pr' + i) ** 2 * 9;
		return (
			<div
				key={'p' + i}
				style={{
					position: 'absolute',
					left: random('px' + i) * width,
					top: random('py' + i) * height,
					width: r * 2,
					height: r * 2.2,
					borderRadius: '50%',
					background: 'radial-gradient(circle at 35% 30%, rgba(255,240,220,.85) 0%, rgba(255,240,220,.18) 28%, rgba(20,16,25,.25) 62%, rgba(255,230,200,.35) 92%, transparent 100%)',
					opacity: 0.55 * force,
				}}
			/>
		);
	});
	const coulees = Array.from({length: 16}, (_, i) => {
		const x = random('cx' + i) * width;
		const v = 120 + random('cv' + i) * 260;
		const depart = random('cd' + i) * 4;
		const y = ((t + depart) * v) % (height + 300) - 150;
		const r = 4 + random('cr' + i) * 6;
		return (
			<React.Fragment key={'c' + i}>
				<div style={{position: 'absolute', left: x + r * 0.6, top: y - 220, width: Math.max(1.5, r * 0.35), height: 220, background: 'linear-gradient(to bottom, transparent, rgba(255,235,210,.18))', opacity: force}} />
				<div
					style={{
						position: 'absolute',
						left: x,
						top: y,
						width: r * 1.6,
						height: r * 2.2,
						borderRadius: '50% 50% 50% 50% / 40% 40% 60% 60%',
						background: 'radial-gradient(circle at 35% 35%, rgba(255,245,230,.95) 0%, rgba(255,240,220,.25) 35%, rgba(15,10,20,.35) 70%, rgba(255,220,190,.5) 100%)',
						opacity: 0.8 * force,
					}}
				/>
			</React.Fragment>
		);
	});
	return <div style={{...plein, pointerEvents: 'none'}}>{perles}{coulees}</div>;
};

/** La poussière d'or : des bokehs qui flottent, à trois profondeurs. */
export const Poussiere: React.FC<{n?: number; couleur?: string; force?: number; graine?: string}> = ({n = 46, couleur = C.orDoux, force = 1, graine = 'po'}) => {
	const t = useT();
	const {width, height} = useVideoConfig();
	return (
		<div style={{...plein, pointerEvents: 'none'}}>
			{Array.from({length: n}, (_, i) => {
				const z = random(graine + 'z' + i);
				const taille = 4 + z * z * 46;
				const x = (random(graine + 'x' + i) * width + t * (8 + z * 30) + bruit(graine + i, t, 0.15) * 40) % (width + 100) - 50;
				const y = (random(graine + 'y' + i) * height - t * (6 + z * 22) + 4000) % (height + 100) - 50;
				const scint = 0.55 + 0.45 * Math.sin(t * (1 + random(graine + 's' + i) * 2) + i);
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: x,
							top: y,
							width: taille,
							height: taille,
							borderRadius: '50%',
							background: `radial-gradient(circle, ${couleur} 0%, ${couleur}55 40%, transparent 70%)`,
							filter: `blur(${z * 5}px)`,
							opacity: force * scint * (0.25 + z * 0.55),
						}}
					/>
				);
			})}
		</div>
	);
};

/** Un ciel étoilé : des étoiles qui scintillent, chacune à son rythme. */
export const Ciel: React.FC<{n?: number; force?: number; derive?: number}> = ({n = 240, force = 1, derive = 0}) => {
	const t = useT();
	const {width, height} = useVideoConfig();
	return (
		<div style={{...plein, pointerEvents: 'none'}}>
			{Array.from({length: n}, (_, i) => {
				const z = random('ez' + i);
				const s = 1 + z * z * 3;
				const sc = 0.4 + 0.6 * Math.abs(Math.sin(t * (0.6 + random('es' + i) * 2.4) + i * 1.7));
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: (random('ex' + i) * width - derive * (0.3 + z) * t + width * 3) % width,
							top: random('ey' + i) * height * 0.78,
							width: s,
							height: s,
							borderRadius: '50%',
							background: z > 0.85 ? C.orPale : C.papier,
							boxShadow: z > 0.85 ? `0 0 ${s * 4}px ${C.orDoux}` : undefined,
							opacity: force * sc * (0.35 + z * 0.65),
						}}
					/>
				);
			})}
		</div>
	);
};

/** La fumée de la cire : des volutes floues qui montent et se défont. */
export const Fumee: React.FC<{x: number; y: number; force?: number; debut?: number}> = ({x, y, force = 1, debut = 0}) => {
	const t = useT() - debut;
	if (t < 0) return null;
	return (
		<div style={{...plein, pointerEvents: 'none'}}>
			{Array.from({length: 9}, (_, i) => {
				const age = (t * 0.55 + i / 9) % 1;
				const dx = bruit('fx' + i, t, 0.25) * 60 * age;
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: x - 60 + dx,
							top: y - age * 320,
							width: 120 + age * 160,
							height: 160 + age * 120,
							borderRadius: '50%',
							background: 'radial-gradient(ellipse, rgba(235,225,215,.55) 0%, rgba(235,225,215,.12) 45%, transparent 70%)',
							filter: `blur(${10 + age * 18}px)`,
							opacity: force * Math.sin(age * Math.PI) * 0.6 * Math.min(1, t * 2),
							rotate: `${bruit('fr' + i, t, 0.2) * 30}deg`,
						}}
					/>
				);
			})}
		</div>
	);
};

/** Des rayons de lumière qui tournent lentement depuis un point (la lumière de minuit). */
export const Rayons: React.FC<{x: string; y: string; force: number; couleur?: string; tour?: number}> = ({x, y, force, couleur = C.orDoux, tour = 0}) => (
	<div
		style={{
			...plein,
			pointerEvents: 'none',
			mixBlendMode: 'screen',
			opacity: force,
			background: `repeating-conic-gradient(from ${tour}deg at ${x} ${y}, ${couleur}33 0deg, transparent 4deg, transparent 9deg, ${couleur}22 12deg, transparent 16deg)`,
			maskImage: `radial-gradient(circle at ${x} ${y}, black 0%, rgba(0,0,0,.5) 30%, transparent 70%)`,
			WebkitMaskImage: `radial-gradient(circle at ${x} ${y}, black 0%, rgba(0,0,0,.5) 30%, transparent 70%)`,
			filter: 'blur(6px)',
		}}
	/>
);

/**
 * La fuite de lumière (`lightLeak`), posée en écran sur l'image. Sa base est jaune et orange.
 * ⚠️ `teinte` (hueShift) tourne à l'ENVERS de l'intuition : la matrice du shader est en colonnes. Mesuré :
 * 20 → ambre 34° et corail 10° (la cire) ; 335 → vert-jaune 74° (vu sur la planche du MP4, 2026-10-22).
 */
export const Fuite: React.FC<{progres: number; graine?: number; teinte?: number; force?: number}> = ({progres, graine = 0, teinte = 0, force = 1}) => {
	const {width, height} = useVideoConfig();
	if (progres <= 0 || progres >= 1) return null;
	return (
		<div style={{...plein, mixBlendMode: 'screen', opacity: force, pointerEvents: 'none'}}>
			<Solid width={width} height={height} color="black" effects={[lightLeak({seed: graine, hueShift: teinte, progress: progres})]} />
		</div>
	);
};

/** La gerbe de minuit (`starburst`) : des rayons d'or qui jaillissent du cachet. */
export const Gerbe: React.FC<{force: number; tour: number; origine?: [number, number]}> = ({force, tour, origine = [0.5, 0.5]}) => {
	const {width, height} = useVideoConfig();
	if (force <= 0.001) return null;
	const [ox, oy] = origine;
	const masque = `radial-gradient(circle at ${ox * 100}% ${oy * 100}%, black 0%, rgba(0,0,0,.55) 22%, transparent 62%)`;
	return (
		<div style={{...plein, mixBlendMode: 'screen', opacity: force, pointerEvents: 'none', maskImage: masque, WebkitMaskImage: masque}}>
			<Solid width={width} height={height} color="black" effects={[starburst({rays: 36, colors: ['#e0c266', '#140f05'], rotation: tour, smoothness: 0.6, origin: origine})]} />
		</div>
	);
};

/* ── Les trois pluies du produit (`pleuvoir()` de lettre.html), rejouées par le temps ── */
const ETOILE = (r: number) => {
	const pts: string[] = [];
	for (let i = 0; i < 8; i++) {
		const a = (i * Math.PI) / 4;
		const rr = i % 2 ? r * 0.38 : r;
		pts.push(`${(Math.cos(a) * rr).toFixed(2)},${(Math.sin(a) * rr).toFixed(2)}`);
	}
	return pts.join(' ');
};
const COULEURS_PLUIE = {
	petales: ['#b2434e', '#d88aa0', '#f0c6cf', '#8c2f39'],
	confettis: ['#c9a227', '#b2434e', '#4f8a6f', '#e0c266', '#f4ede0'],
	etoiles: ['#e0c266', '#c9a227', '#f7e7b0'],
};

/**
 * La pluie d'ouverture, avec LES PARAMÈTRES DU PRODUIT : 46 étoiles (70 pétales ou confettis), une chute de 1,6 à
 * 4 px par image à 60 i/s sur un téléphone de 390 px, un balancement, une rotation, 2,6 s, un fondu après 2 s.
 * `echelle` agrandit le tout pour un écran de 1920 px.
 */
export const Pluie: React.FC<{type: keyof typeof COULEURS_PLUIE; debut: number; echelle?: number; graine?: string}> = ({type, debut, echelle = 4.9, graine = 'pl'}) => {
	const t = useT() - debut;
	const {width, height} = useVideoConfig();
	if (t < 0 || t > 2.7) return null;
	const age = t * 1000;
	const n = type === 'etoiles' ? 46 : 70;
	const W = width / echelle, H = height / echelle;
	const alpha = age > 2000 ? Math.max(0, 1 - (age - 2000) / 600) : 1;
	const pas = age / 16.7;
	const coul = COULEURS_PLUIE[type];
	return (
		<svg width={width} height={height} viewBox={`0 0 ${W} ${H}`} style={{...plein, opacity: alpha, pointerEvents: 'none', overflow: 'visible'}}>
			{Array.from({length: n}, (_, i) => {
				const x0 = random(graine + 'x' + i) * W;
				const y0 = -20 - random(graine + 'y' + i) * H * 0.6;
				const v = 1.6 + random(graine + 'v' + i) * 2.4;
				const d = (random(graine + 'd' + i) - 0.5) * 1.2;
				const r0 = random(graine + 'r' + i) * 6.28;
				const vr = (random(graine + 'w' + i) - 0.5) * 0.12;
				const taille = 4 + random(graine + 't' + i) * 6;
				const o = random(graine + 'o' + i) * 6.28;
				const y = y0 + v * pas;
				const x = x0 + d * pas + 0.6 * (420 / 16.7) * (Math.cos(o) - Math.cos(o + age / 420));
				const rot = ((r0 + vr * pas) * 180) / Math.PI;
				const c = coul[i % coul.length];
				return (
					<g key={i} transform={`translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rot.toFixed(1)})`}>
						{type === 'etoiles' ? (
							<polygon points={ETOILE(taille * 0.8)} fill={c} />
						) : type === 'petales' ? (
							<ellipse rx={taille} ry={taille * 0.55} fill={c} />
						) : (
							<rect x={-taille / 2} y={-taille / 4} width={taille} height={taille / 2} fill={c} />
						)}
					</g>
				);
			})}
		</svg>
	);
};

/** L'encre qui sèche, mot à mot : floue puis nette (la signature du produit pour tout texte qui paraît). */
export const Encre: React.FC<{texte: string; debut: number; pas?: number; style?: React.CSSProperties; flou?: number}> = ({texte, debut, pas = 0.06, style, flou = 10}) => {
	const t = useT();
	const mots = texte.split(' ');
	return (
		<div style={style}>
			{mots.map((m, i) => {
				const k = p(t, debut + i * pas, debut + i * pas + 0.45, T);
				return (
					<span key={i} style={{display: 'inline-block', opacity: k, filter: `blur(${(1 - k) * flou}px)`, translate: `0 ${(1 - k) * 10}px`, whiteSpace: 'pre'}}>
						{m}
						{i < mots.length - 1 ? ' ' : ''}
					</span>
				);
			})}
		</div>
	);
};

/** Une ligne de titre du film (Libre Caslon Display), avec son italique d'accent. */
export const titre = (taille: number, couleur: string = C.papier): React.CSSProperties => ({
	fontFamily: TITRE,
	fontSize: taille,
	lineHeight: 1.04,
	color: couleur,
	letterSpacing: '-0.01em',
});
export const accent = (taille: number, couleur: string = C.orDoux): React.CSSProperties => ({
	fontFamily: ITALIQUE,
	fontStyle: 'italic',
	fontSize: taille,
	color: couleur,
});

export const fondu = (t: number, a: number, b: number) => mix(0, 1, p(t, a, b));
