/**
 * Le téléphone de la mère, et ce qu'il montre : LA LETTRE DU PRODUIT (`malettre/lettre.html`), scellée avec son
 * compte à rebours, puis « C'est l'heure. » et le bouton « Briser le cachet ». Rien n'est embelli : ce sont les
 * phrases, les couleurs et l'enveloppe du produit.
 */
import React from 'react';
import {Enveloppe} from '../malettre/outils';
import {C, CIRES, HABIT, ITALIQUE, LETTRE, SANS, TITRE} from './donnees';
import {mix, p, T} from './outils';

const deux = (n: number) => String(Math.max(0, n)).padStart(2, '0');

/** Le compte à rebours du produit : heures, minutes, secondes ; le chiffre des secondes ROULE. */
const Compte: React.FC<{reste: number; taille: number}> = ({reste, taille}) => {
	const s = Math.max(0, Math.ceil(reste - 1e-6));
	const frac = s - Math.max(0, reste);
	const k = reste <= 0 ? 1 : T(Math.min(1, Math.max(0, (frac - 0.8) / 0.2)));
	const roule = k > 0 && reste > 0;
	const suivant = Math.max(0, s - 1);
	/* heures, minutes, secondes : seule la case qui change roule */
	const hms = (x: number) => [Math.floor(x / 3600), Math.floor((x % 3600) / 60), x % 60];
	const [h0, m0, s0] = hms(s), [h1, m1, s1] = hms(roule ? suivant : s);
	const cases: [string, string, number, string][] = [
		[deux(h1), deux(h0), h1 !== h0 ? k : 1, 'h'],
		[deux(m1), deux(m0), m1 !== m0 ? k : 1, 'min'],
		[deux(s1), deux(s0), roule ? k : 1, 's'],
	];
	return (
		<div style={{display: 'flex', gap: taille * 0.3, justifyContent: 'center'}}>
			{cases.map(([v, avant, kk, lib], i) => (
				<div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', width: taille * 1.5}}>
					<div style={{position: 'relative', height: taille * 1.08, width: '100%', overflow: 'hidden', fontFamily: TITRE, fontSize: taille, lineHeight: `${taille * 1.08}px`, color: C.papier, textAlign: 'center'}}>
						<span style={{position: 'absolute', inset: 0, translate: `0 ${-kk * 100}%`, opacity: 1 - kk}}>{avant}</span>
						<span style={{position: 'absolute', inset: 0, translate: `0 ${(1 - kk) * 100}%`, opacity: kk}}>{v}</span>
					</div>
					<i style={{fontStyle: 'normal', fontFamily: SANS, fontSize: taille * 0.26, letterSpacing: '0.2em', textTransform: 'uppercase', color: C.grisNuit}}>{lib}</i>
				</div>
			))}
		</div>
	);
};

/**
 * L'écran de la lettre. `reste` : secondes avant minuit (le compte) ; `heure` 0→1 : minuit est passé
 * (« C'est l'heure. », la cire s'allume, le bouton paraît) ; `presse` 0→1 : le doigt enfonce le bouton.
 */
export const EcranLettre: React.FC<{largeur: number; t: number; reste: number; heure: number; presse?: number}> = ({largeur: S, t, reste, heure, presse = 0}) => {
	const c = CIRES[HABIT.cire];
	return (
		<div
			style={{
				position: 'absolute',
				inset: 0,
				background: `radial-gradient(120% 80% at 50% 38%, ${C.nuit2} 0%, ${C.nuit} 70%)`,
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'center',
				paddingTop: S * 0.2,
				boxSizing: 'border-box',
			}}
		>
			<div style={{fontFamily: SANS, fontSize: S * 0.04, letterSpacing: '0.04em', color: C.grisNuit}}>Ma lettre à {LETTRE.pour}</div>
			<div style={{position: 'relative', height: S * 0.13, width: '100%', marginTop: S * 0.05}}>
				<div style={{position: 'absolute', inset: 0, textAlign: 'center', fontFamily: TITRE, fontSize: S * 0.085, color: C.papier, opacity: 1 - heure}}>{LETTRE.attend}</div>
				<div style={{position: 'absolute', inset: 0, textAlign: 'center', fontFamily: TITRE, fontSize: S * 0.095, color: C.papier, opacity: heure, filter: `blur(${(1 - heure) * 8}px)`}}>
					{LETTRE.heure}
				</div>
			</div>
			<div style={{marginTop: S * 0.07, position: 'relative'}}>
				<div style={{position: 'absolute', left: '50%', top: '52%', width: S * 1.2, height: S * 1.2, translate: '-50% -50%', borderRadius: '50%', background: `radial-gradient(circle, ${c.lumiere}aa 0%, ${c.lumiere}33 25%, transparent 60%)`, opacity: heure}} />
				<Enveloppe h={{cire: HABIT.cire, sceau: HABIT.sceau === 'initiale' || HABIT.sceau === 'marque' ? 'coeur' : HABIT.sceau, papier: 'creme', initiale: HABIT.initiale}} largeur={S * 0.78} t={t} lumiere={heure * (0.8 + 0.2 * Math.sin(t * 6))} />
			</div>
			<div style={{marginTop: S * 0.08, fontFamily: SANS, fontSize: S * 0.038, color: C.grisNuit, textAlign: 'center', padding: `0 ${S * 0.08}px`, opacity: 1 - heure}}>
				{LETTRE.ouvre[0]}
				<b style={{color: C.papier, fontWeight: 600}}>{LETTRE.ouvre[1]}</b>
				{LETTRE.ouvre[2]}
			</div>
			<div style={{position: 'relative', width: '100%', height: S * 0.32, marginTop: S * 0.04}}>
				<div style={{position: 'absolute', inset: 0, opacity: 1 - p(heure, 0, 0.4)}}>
					<Compte reste={reste} taille={S * 0.12} />
				</div>
				<div
					style={{
						position: 'absolute',
						left: '50%',
						top: S * 0.02,
						translate: '-50% 0',
						padding: `${S * 0.045}px ${S * 0.11}px`,
						borderRadius: 999,
						background: `linear-gradient(180deg, #fbf4e6 0%, ${C.papier} 55%, #e6d8bf 100%)`,
						boxShadow: `0 ${S * 0.03}px ${S * 0.08}px rgba(0,0,0,.45), 0 0 ${S * 0.1 * heure}px ${c.lumiere}55, inset 0 2px 0 rgba(255,255,255,.7)`,
						color: C.encre,
						fontFamily: SANS,
						fontWeight: 700,
						fontSize: S * 0.05,
						whiteSpace: 'nowrap',
						opacity: p(heure, 0.35, 0.8),
						scale: String(mix(1, 0.94, presse)),
					}}
				>
					{LETTRE.briser}
				</div>
			</div>
		</div>
	);
};

/** Le téléphone : un cadre de titane sombre, l'îlot, le verre qui accroche la lumière. */
export const Telephone: React.FC<{largeur: number; lueur?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({largeur: W, lueur = 0, children, style}) => {
	const H = W * 2.06;
	const bord = W * 0.034;
	return (
		<div
			style={{
				position: 'relative',
				width: W,
				height: H,
				borderRadius: W * 0.15,
				background: 'linear-gradient(145deg, #4a4350 0%, #1d1922 38%, #0e0c12 70%, #3a3340 100%)',
				boxShadow: `0 ${W * 0.08}px ${W * 0.25}px rgba(0,0,0,.6), inset 0 0 0 1.5px rgba(255,255,255,.12), 0 0 ${W * 0.5 * lueur}px ${W * 0.06 * lueur}px rgba(255,214,190,${0.35 * lueur})`,
				...style,
			}}
		>
			<div style={{position: 'absolute', inset: bord, borderRadius: W * 0.12, overflow: 'hidden', background: C.nuit}}>
				{children}
				{/* l'îlot */}
				<div style={{position: 'absolute', left: '50%', top: W * 0.035, width: W * 0.3, height: W * 0.085, translate: '-50% 0', borderRadius: 999, background: '#050407'}} />
				{/* le verre */}
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(118deg, transparent 38%, rgba(255,255,255,.07) 47%, transparent 56%)', pointerEvents: 'none'}} />
			</div>
		</div>
	);
};

export const legende: React.CSSProperties = {fontFamily: ITALIQUE, fontStyle: 'italic', color: C.grisNuit};
