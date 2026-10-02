/**
 * L'OUTIL DIGITAL : un tableau de bord qui s'assemble module par module, puis
 * CHANGE DE PEAU au rythme des métiers (restaurant, institut, boutique), avant de
 * se poser sur « VOTRE MÉTIER » : un squelette qui scintille, l'outil qui reste à
 * construire pour vous.
 *
 * ⚠️ Les chiffres sont un EXEMPLE (pastille DÉMO), jamais un résultat promis.
 */
import React from 'react';
import {Img, interpolate, staticFile} from 'remotion';
import {C, type Registre, T, TEXTES, mot} from '../donnees';
import {IconeMetier} from '../Icones';
import {DOUX, montant, p, ressort} from '../outils';
import {MONO, TEXTE} from '../polices';

type Peau = {
	nom: string;
	icone: 'plat' | 'fleur' | 'sac' | 'etoile';
	accent: string;
	kpis: [string, number, string][];
	liste: [string, string][];
	parts: [string, number][];
	courbe: number[];
	squelette?: boolean;
};

const PEAUX: Peau[] = [
	{
		nom: 'RESTAURANT',
		icone: 'plat',
		accent: '#ff9a3c',
		kpis: [['Commandes du jour', 48, ''], ['Plats servis', 126, ''], ['Caisse du jour', 186500, ' F']],
		liste: [['Poulet braisé', '32'], ['Attiéké poisson', '21'], ['Jus de bissap', '18']],
		parts: [['Sur place', 0.5], ['À emporter', 0.3], ['Livraison', 0.2]],
		courbe: [0.35, 0.5, 0.42, 0.62, 0.58, 0.8, 0.72],
	},
	{
		nom: 'INSTITUT DE BEAUTÉ',
		icone: 'fleur',
		accent: '#ff77c8',
		kpis: [['Rendez-vous', 14, ''], ['Soins réalisés', 37, ''], ['Caisse du jour', 245000, ' F']],
		liste: [['Soin visage', '10 h 30'], ['Manucure', '11 h 15'], ['Massage', '14 h 00']],
		parts: [['Visage', 0.45], ['Corps', 0.35], ['Mains', 0.2]],
		courbe: [0.4, 0.38, 0.55, 0.5, 0.7, 0.66, 0.85],
	},
	{
		nom: 'BOUTIQUE',
		icone: 'sac',
		accent: '#4fd1ff',
		kpis: [['Ventes', 63, ''], ['Articles en stock', 412, ''], ['Caisse du jour', 318000, ' F']],
		liste: [['Robe Sirène', '4 en stock'], ['Sac en cuir', '2 en stock'], ['Parfum', '9 en stock']],
		parts: [['Robes', 0.4], ['Sacs', 0.35], ['Parfums', 0.25]],
		courbe: [0.3, 0.45, 0.6, 0.52, 0.68, 0.75, 0.9],
	},
	{
		nom: 'VOTRE MÉTIER',
		icone: 'etoile',
		accent: C.cyan,
		kpis: [['', 0, ''], ['', 0, ''], ['', 0, '']],
		liste: [['', ''], ['', ''], ['', '']],
		parts: [['', 0.4], ['', 0.35], ['', 0.25]],
		courbe: [0.42, 0.48, 0.55, 0.6, 0.66, 0.72, 0.8],
		squelette: true,
	},
];

/** Les changements de peau : au mot « pensé », puis deux fois, puis sur « votre ». */
const bascules = () => {
	const a = T.peaux;
	const b = mot('outil', 5);
	return [a, a + (b - a) / 2, b];
};

const Module: React.FC<{t: number; a: number; style: React.CSSProperties; children: React.ReactNode}> = ({t, a, style, children}) => {
	const e = ressort(t, a, {damping: 15, stiffness: 210, mass: 0.6});
	return (
		<div
			style={{
				position: 'absolute',
				borderRadius: 26,
				background: 'linear-gradient(160deg, rgba(40,38,92,.72), rgba(16,15,44,.82))',
				boxShadow: 'inset 0 0 0 1.5px rgba(170,180,255,.16), 0 18px 40px -20px rgba(0,0,0,.8)',
				opacity: Math.min(1, e * 1.6),
				transform: `scale(${0.84 + 0.16 * e}) translateY(${(1 - e) * 30}px)`,
				overflow: 'hidden',
				...style,
			}}
		>
			{children}
		</div>
	);
};

/** Une barre grise qui scintille : la place d'une donnée qui reste à écrire. */
const Squelette: React.FC<{t: number; l: number | string; h: number; style?: React.CSSProperties}> = ({t, l, h, style}) => (
	<div
		style={{
			width: l,
			height: h,
			borderRadius: h / 2,
			background: `linear-gradient(90deg, rgba(168,236,255,.08) 0%, rgba(168,236,255,.32) ${((t * 70) % 140) - 20}%, rgba(168,236,255,.08) ${((t * 70) % 140) + 20}%)`,
			...style,
		}}
	/>
);

export const Tableau: React.FC<{t: number; l: number; h: number; registre: Registre}> = ({t, l, h, registre}) => {
	const debut = T.outil + 0.3;
	const [b1, b2, b3] = bascules();
	const indice = t < b1 ? 0 : t < b2 ? 1 : t < b3 ? 2 : 3;
	const peau = PEAUX[indice];
	const depuis = [debut, b1, b2, b3][indice];
	const nom = indice === 3 ? TEXTES[registre].metier.replace('.', '') : peau.nom;
	const vu = p(t, depuis, depuis + 0.22);
	const pad = 34;
	const largeur = l - 2 * pad;
	const tuile = (largeur - 2 * 18) / 3;
	// le balayage lumineux de chaque changement de peau
	const balaye = indice > 0 ? p(t, depuis - 0.02, depuis + 0.3) : 1;
	const precedente = PEAUX[Math.max(0, indice - 1)];
	const courbe = peau.courbe.map((v, i) => (indice > 0 ? interpolate(vu, [0, 1], [precedente.courbe[i], v]) : v));
	const trace = p(t, debut + 0.45, debut + 1.3);
	const pointsCourbe = courbe.map((v, i) => [24 + (i * (largeur - 48)) / 6, 250 - v * 200]);
	const chemin = pointsCourbe.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
	return (
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 30% 0%, rgba(98,168,255,.18), transparent 55%), linear-gradient(180deg, #121034, #0a0920)'}}>
			{/* l'en-tête */}
			<Module t={t} a={debut} style={{left: pad, top: pad, width: largeur, height: 96, display: 'flex', alignItems: 'center', gap: 18, padding: '0 26px'}}>
				<Img src={staticFile('nebula30/logo/marque.png')} style={{width: 74, height: 37, objectFit: 'contain'}} />
				<div style={{fontFamily: TEXTE, fontWeight: 700, fontSize: 32, color: C.lavande}}>Tableau de bord</div>
				<div style={{flex: 1}} />
				<div
					style={{
						display: 'flex',
						alignItems: 'center',
						gap: 10,
						padding: '10px 20px',
						borderRadius: 40,
						border: `2px solid ${peau.accent}`,
						boxShadow: `0 0 ${indice === 3 ? 30 : 14}px ${peau.accent}66`,
						fontFamily: MONO,
						fontWeight: 700,
						fontSize: 21,
						letterSpacing: '0.08em',
						color: peau.accent,
						transform: `scale(${0.9 + 0.1 * vu})`,
					}}
				>
					<IconeMetier forme={peau.icone} couleur={peau.accent} taille={26} />
					{nom}
				</div>
				<div style={{fontFamily: MONO, fontSize: 15, color: C.gris, border: `1.5px solid ${C.grisFonce}`, borderRadius: 8, padding: '4px 8px', letterSpacing: '0.12em'}}>DÉMO</div>
			</Module>

			{/* les trois chiffres */}
			{peau.kpis.map(([libelle, valeur, unite], k) => {
				const a = debut + 0.12 + k * 0.1;
				const roule = p(t, Math.max(a + 0.1, depuis), Math.max(a + 0.1, depuis) + (indice ? 0.3 : 0.7));
				const avant = indice > 0 ? precedente.kpis[k][1] : 0;
				return (
					<Module key={k} t={t} a={a} style={{left: pad + k * (tuile + 18), top: pad + 116, width: tuile, height: 176, padding: 24}}>
						{peau.squelette ? (
							<>
								<Squelette t={t + k * 0.3} l="70%" h={16} />
								<Squelette t={t + k * 0.3 + 0.2} l="55%" h={44} style={{marginTop: 30}} />
							</>
						) : (
							<>
								<div style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 21, color: C.gris, opacity: vu}}>{libelle}</div>
								<div style={{fontFamily: MONO, fontWeight: 700, fontSize: valeur > 99999 ? 40 : 52, color: C.lavande, marginTop: 22, whiteSpace: 'nowrap'}}>
									{montant(interpolate(roule, [0, 1], [avant, valeur]))}
									<span style={{fontSize: 26, color: peau.accent}}>{unite}</span>
								</div>
							</>
						)}
						<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 5, background: peau.accent, opacity: 0.85}} />
					</Module>
				);
			})}

			{/* la courbe */}
			<Module t={t} a={debut + 0.42} style={{left: pad, top: pad + 312, width: largeur, height: 320}}>
				<div style={{position: 'absolute', left: 26, top: 22, fontFamily: TEXTE, fontWeight: 600, fontSize: 22, color: C.lavande}}>Activité · 7 jours</div>
				<svg width={largeur} height={320} style={{position: 'absolute', left: 0, top: 30}}>
					<defs>
						<linearGradient id="sous-courbe" x1="0" y1="0" x2="0" y2="1">
							<stop offset="0%" stopColor={peau.accent} stopOpacity={0.45} />
							<stop offset="100%" stopColor={peau.accent} stopOpacity={0} />
						</linearGradient>
					</defs>
					{[0, 1, 2, 3].map((k) => (
						<line key={k} x1={24} x2={largeur - 24} y1={60 + k * 62} y2={60 + k * 62} stroke="rgba(170,180,255,.09)" strokeWidth={1.5} />
					))}
					<path d={`${chemin} L${largeur - 24} 262 L24 262 Z`} fill="url(#sous-courbe)" opacity={trace} />
					<path
						d={chemin}
						fill="none"
						stroke={peau.accent}
						strokeWidth={5}
						strokeLinejoin="round"
						strokeLinecap="round"
						pathLength={1}
						strokeDasharray={peau.squelette ? '0.02 0.015' : 1}
						strokeDashoffset={peau.squelette ? -t * 0.08 : 1 - trace}
						style={{filter: `drop-shadow(0 0 8px ${peau.accent})`}}
					/>
					{pointsCourbe.map(([x, y], i) => (trace > i / 6 ? <circle key={i} cx={x} cy={y} r={6} fill={C.encre} stroke={peau.accent} strokeWidth={3} /> : null))}
				</svg>
			</Module>

			{/* la répartition */}
			<Module t={t} a={debut + 0.56} style={{left: pad, top: pad + 652, width: 330, height: h - pad * 2 - 652}}>
				<svg width={330} height={300} viewBox="0 0 330 300" style={{position: 'absolute', left: 0, top: 10}}>
					{(() => {
						let cumul = 0;
						const tour = p(t, debut + 0.6, debut + 1.4);
						return peau.parts.map(([, part], k) => {
							const r = 92;
							const circ = 2 * Math.PI * r;
							const longueur = part * circ * tour;
							const el = (
								<circle
									key={k}
									cx={165}
									cy={150}
									r={r}
									fill="none"
									stroke={peau.squelette ? `rgba(168,236,255,${0.18 + 0.12 * k})` : [peau.accent, C.violet, C.bleuClair][k]}
									strokeWidth={34}
									strokeDasharray={`${Math.max(0, longueur - 6)} ${circ}`}
									strokeDashoffset={-cumul * circ * tour}
									transform="rotate(-90 165 150)"
								/>
							);
							cumul += part;
							return el;
						});
					})()}
				</svg>
			</Module>

			{/* la liste */}
			<Module t={t} a={debut + 0.68} style={{left: pad + 348, top: pad + 652, width: largeur - 348, height: h - pad * 2 - 652, padding: '26px 28px'}}>
				{peau.liste.map(([gauche, droite], k) => (
					<div key={k} style={{display: 'flex', alignItems: 'center', gap: 16, height: 80, borderBottom: k < 2 ? '1.5px solid rgba(170,180,255,.1)' : undefined, opacity: vu}}>
						<div style={{width: 14, height: 14, borderRadius: 7, background: [peau.accent, C.violet, C.bleuClair][k], boxShadow: `0 0 10px ${peau.accent}`}} />
						{peau.squelette ? (
							<Squelette t={t + k * 0.25} l={220 - k * 30} h={18} />
						) : (
							<>
								<div style={{fontFamily: TEXTE, fontWeight: 600, fontSize: 25, color: C.lavande, flex: 1}}>{gauche}</div>
								<div style={{fontFamily: MONO, fontWeight: 500, fontSize: 22, color: peau.accent}}>{droite}</div>
							</>
						)}
					</div>
				))}
			</Module>

			{/* le balayage de lumière d'un changement de peau */}
			{balaye > 0 && balaye < 1 ? (
				<div
					style={{
						position: 'absolute',
						top: 0,
						bottom: 0,
						left: `${-30 + 130 * DOUX(balaye)}%`,
						width: '22%',
						background: `linear-gradient(90deg, transparent, ${peau.accent}55, rgba(255,255,255,.35), ${peau.accent}55, transparent)`,
						mixBlendMode: 'screen',
					}}
				/>
			) : null}
		</div>
	);
};
