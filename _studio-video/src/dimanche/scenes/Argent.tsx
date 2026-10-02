/**
 * CHAPITRE 2 · L'ARGENT (0:28 → 1:24)
 *
 *  · LES VERBES   gagner, économiser, investir, épargner : quatre lignes écrites.
 *  · LE BUDGET    une seule feuille qui vit trois temps :
 *                 1. le SALAIRE : 100 000 F, la tentation des 400 000 (barrée),
 *                    retour aux 100 000 « sous ta main » ;
 *                 2. le PLAN : la barre des 100 000 se découpe, les CHARGES
 *                    partent d'abord dans leur case, il RESTE 30 000 F ;
 *                 3. « si tu gagnes 400 000, tu fais pareil » : même découpe.
 *  · LA VITESSE   l'argent entre et sort à la même vitesse : il disparaît.
 *
 * ⚠️ Il dit « si tes charges sont de 110 000 » puis « il va te rester 30 000 »
 * sur un salaire de 100 000 : le calcul ne tombe pas juste (il voulait sans
 * doute dire 70 000). On n'affiche donc AUCUN montant sur les charges, seulement
 * ce qu'il reste. Les montants affichés sont ceux qu'il prononce, rien d'autre.
 */
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, d, fi} from '../donnees';
import {Chiffre, Ecrit, Etiquette, Feuille, GLISSE, Surligne, Trait, fenetre, montant, p, ressort} from '../outils';
import {TITRE} from '../polices';

const CARTE = {x: 64, y: 1170, l: 876, h: 420};
const bornes = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/* ───────────────────────── LES VERBES ───────────────────────── */

const VERBES: [string, number, string][] = [
	['gagner', 100, 'M40 12 A28 28 0 1 1 39.9 12 M34 26 H48 M34 26 V54 M34 40 H45'],
	['économiser', 107, 'M24 20 H56 M26 20 C16 30 16 62 26 68 H54 C64 62 64 30 54 20 M32 44 H48'],
	['investir', 109, 'M12 66 H68 M18 56 L32 40 L44 48 L64 24 M50 24 H64 V38'],
	['épargner', 121, 'M12 16 H68 V62 H12 Z M30 39 A10 10 0 1 0 50 39 A10 10 0 1 0 30 39 M22 62 V70 M58 62 V70'],
];

export const Verbes: React.FC<{t: number}> = ({t}) => {
	const a = d(87) - 0.1;
	const b = d(122) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	return (
		<Feuille {...CARTE} e={w.e} s={w.s} incline={1}>
			<div style={{position: 'absolute', left: 40, top: 28}}>
				<Ecrit v={p(t, d(89), d(95))} taille={52}>
					Le but de tout le monde
				</Ecrit>
			</div>
			{VERBES.map(([mot, i, icone], n) => {
				const x = 40 + (n % 2) * 410;
				const y = 130 + Math.floor(n / 2) * 140;
				const r = ressort(t, d(i) - 0.08, {damping: 12, stiffness: 220});
				return (
					<div
						key={mot}
						style={{
							position: 'absolute',
							left: x,
							top: y,
							display: 'flex',
							alignItems: 'center',
							gap: 22,
							opacity: Math.min(1, r * 3),
						}}
					>
						<div
							style={{
								width: 104,
								height: 104,
								borderRadius: 52,
								background: C.surligneur,
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
								transform: `scale(${interpolate(r, [0, 1], [0.3, 1])})`,
							}}
						>
							<svg width={70} height={70} viewBox="0 0 80 80">
								<Trait d={icone} v={p(t, d(i), d(i) + 0.5)} couleur={C.stylo} epaisseur={5.5} />
							</svg>
						</div>
						<Ecrit v={p(t, d(i) - 0.05, d(i) + 0.45)} taille={68}>
							{mot}
						</Ecrit>
					</div>
				);
			})}
		</Feuille>
	);
};

/* ───────────────────────── LE BUDGET ───────────────────────── */

const BARRE = {x: 40, y: 172, l: 796, h: 124};
const PART_CHARGES = 0.7;

export const Budget: React.FC<{t: number}> = ({t}) => {
	const a = d(122) - 0.1;
	const b = d(288) - 0.1;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	// le salaire qui roule : 0 → 100 000 → 400 000 → 100 000 → (plan) → 400 000
	let v = interpolate(t, [d(138) - 0.1, d(138) + 0.55], [0, 100000], {...bornes, easing: Easing.out(Easing.cubic)});
	if (t >= d(161) - 0.1) v = interpolate(t, [d(161) - 0.1, d(161) + 0.6], [100000, 400000], {...bornes, easing: Easing.out(Easing.cubic)});
	if (t >= d(171)) v = interpolate(t, [d(171), d(171) + 0.6], [400000, 100000], {...bornes, easing: Easing.out(Easing.cubic)});
	if (t >= d(283) - 0.1) v = interpolate(t, [d(283) - 0.1, d(283) + 0.5], [100000, 400000], {...bornes, easing: Easing.out(Easing.cubic)});

	const plan = p(t, d(197) - 0.1, d(197) + 0.6, GLISSE);
	const barre = p(t, d(200), d(200) + 0.6, Easing.linear);
	const charges = p(t, d(204) - 0.1, d(204) + 0.5);
	const depart = p(t, d(241), d(241) + 0.7, GLISSE);
	const regle = p(t, d(250) + 0.1, d(250) + 0.5, Easing.linear);
	const reste = p(t, d(261), d(261) + 0.4);
	const trente = interpolate(t, [d(267) - 0.1, d(267) + 0.5], [0, 30000], {...bornes, easing: Easing.out(Easing.cubic)});
	const pareil = ressort(t, d(283) - 0.1, {damping: 9, stiffness: 200});
	const barre4 = t >= d(283) - 0.1 ? 1 + 0.035 * Math.sin(Math.min(1, pareil) * Math.PI) : 1;

	const lCharges = BARRE.l * PART_CHARGES;
	const barre400 = p(t, d(170) - 0.05, d(170) + 0.35, Easing.linear); // « va te suffire » : on barre
	const debarre = p(t, d(171), d(171) + 0.3);

	return (
		<Feuille x={64} y={1140} l={876} h={470} e={w.e} s={w.s}>
			{/* TEMPS 1 · le salaire */}
			<div style={{position: 'absolute', left: 40, top: 30, opacity: 1 - plan}}>
				<Ecrit v={p(t, d(133), d(136) + 0.3)} taille={52}>
					mon salaire
				</Ecrit>
			</div>
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 140,
					display: 'flex',
					justifyContent: 'center',
					transformOrigin: '50% 50%',
					transform: `translate(${plan * -262}px, ${plan * -150}px) scale(${1 - plan * 0.6})`,
					opacity: Math.min(1, p(t, d(138) - 0.15, d(138) + 0.1) * 2),
				}}
			>
				<div style={{position: 'relative'}}>
					<div
						style={{
							position: 'absolute',
							left: -10,
							right: -10,
							bottom: 6,
							height: 44,
							background: C.surligneur,
							borderRadius: 8,
							transformOrigin: 'left',
							transform: `scaleX(${p(t, d(176) - 0.05, d(176) + 0.3) * (1 - plan)}) skewX(-8deg)`,
						}}
					/>
					<Chiffre v={v} taille={190} couleur={C.stylo} style={{position: 'relative'}} />
					<svg width={700} height={200} style={{position: 'absolute', left: -40, top: 0, overflow: 'visible'}}>
						<Trait d="M20 110 C200 96 420 122 660 92" v={barre400 * (1 - debarre)} couleur={C.rouge} epaisseur={12} />
					</svg>
				</div>
			</div>
			{t >= d(152) - 0.1 && t < d(161) + 0.2 ? (
				<div
					style={{
						position: 'absolute',
						right: 44,
						top: 356,
						transform: `rotate(${-3 + Math.sin((t - d(152)) * 9) * 1.5}deg)`,
						opacity: 1 - p(t, d(161) - 0.1, d(161) + 0.2),
					}}
				>
					<Ecrit v={p(t, d(152) - 0.1, d(155))} taille={54} couleur={C.rouge}>
						ne suffit pas…
					</Ecrit>
				</div>
			) : null}
			{t >= d(169) && t < d(171) + 0.3 ? (
				<div style={{position: 'absolute', right: 36, top: 36, opacity: 1 - debarre}}>
					<Ecrit v={p(t, d(169), d(169) + 0.3)} taille={170} couleur={C.rouge}>
						?
					</Ecrit>
				</div>
			) : null}
			<div style={{position: 'absolute', left: 0, right: 0, top: 360, display: 'flex', justifyContent: 'center', opacity: 1 - plan}}>
				<Ecrit v={p(t, d(180) - 0.05, fi(182))} taille={56}>
					sous ta main
				</Ecrit>
			</div>

			{/* TEMPS 2 et 3 · le plan */}
			<div style={{position: 'absolute', left: 340, top: 42, opacity: plan * (1 - p(t, d(285) - 0.2, d(285)))}}>
				<Ecrit v={p(t, d(197) + 0.4, d(197) + 1.0)} taille={50}>
					mon plan
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 340, top: 42, opacity: p(t, d(285) - 0.2, d(285))}}>
				<Surligne v={p(t, d(286), d(286) + 0.3)}>
					<Ecrit v={p(t, d(285), d(287))} taille={50}>
						pareil, ×4
					</Ecrit>
				</Surligne>
			</div>
			{plan > 0 ? (
				<div style={{position: 'absolute', left: 0, top: 0, width: 876, height: 470, transformOrigin: `${BARRE.x}px ${BARRE.y}px`, transform: `scaleX(${barre4})`}}>
					<svg width={876} height={470} style={{position: 'absolute', left: 0, top: 0}}>
						<Trait
							d={`M${BARRE.x + 18} ${BARRE.y} H${BARRE.x + BARRE.l - 18} Q${BARRE.x + BARRE.l} ${BARRE.y} ${BARRE.x + BARRE.l} ${BARRE.y + 18} V${BARRE.y + BARRE.h - 18} Q${BARRE.x + BARRE.l} ${BARRE.y + BARRE.h} ${BARRE.x + BARRE.l - 18} ${BARRE.y + BARRE.h} H${BARRE.x + 18} Q${BARRE.x} ${BARRE.y + BARRE.h} ${BARRE.x} ${BARRE.y + BARRE.h - 18} V${BARRE.y + 18} Q${BARRE.x} ${BARRE.y} ${BARRE.x + 18} ${BARRE.y}`}
							v={barre}
							epaisseur={5}
						/>
						{/* la case des charges, en bas : là où elles partent d'abord */}
						<Trait
							d={`M${BARRE.x} 330 V${330 + 110} H${BARRE.x + lCharges} V330`}
							v={p(t, d(238), d(238) + 0.6, Easing.linear)}
							epaisseur={4}
							couleur="rgba(28,43,75,.45)"
						/>
					</svg>
					{/* les charges : elles remplissent 70 %, puis descendent dans leur case */}
					<div
						style={{
							position: 'absolute',
							left: BARRE.x + 6,
							top: interpolate(depart, [0, 1], [BARRE.y + 6, 336]),
							width: (lCharges - 12) * charges,
							height: BARRE.h - 12 - depart * 16,
							borderRadius: 14,
							background: C.stylo,
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							gap: 16,
							overflow: 'hidden',
						}}
					>
						<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 60, color: C.blanc, letterSpacing: '0.04em', opacity: p(t, d(204) + 0.2, d(204) + 0.5)}}>
							CHARGES
						</span>
						{regle > 0 ? (
							<svg width={54} height={54} viewBox="0 0 60 60">
								<Trait d="M10 31 L25 45 L52 10" v={regle} couleur={C.surligneur} epaisseur={9} />
							</svg>
						) : null}
					</div>
					{depart > 0.5 ? (
						<div
							style={{
								position: 'absolute',
								left: BARRE.x + lCharges + 14,
								top: 360,
								// cède la place à « à épargner », qui s'écrit au même endroit
								opacity: p(t, d(241) + 0.4, d(241) + 0.8) * (1 - p(t, d(261) - 0.2, d(261) + 0.2)),
							}}
						>
							<Ecrit v={p(t, d(241) + 0.4, d(246))} taille={40}>
								réglées d'abord
							</Ecrit>
						</div>
					) : null}
					{/* ce qu'il reste */}
					<div
						style={{
							position: 'absolute',
							left: BARRE.x + lCharges + 6,
							top: BARRE.y + 6,
							width: (BARRE.l - lCharges - 12) * reste,
							height: BARRE.h - 12,
							borderRadius: 14,
							background: C.vert,
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							overflow: 'hidden',
						}}
					>
						<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 64, color: C.blanc, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap'}}>
							{montant(trente)}
						</span>
					</div>
					{reste > 0 && t < d(283) - 0.2 ? (
						<div style={{position: 'absolute', left: BARRE.x + lCharges + 8, top: BARRE.y - 44, opacity: reste}}>
							<Etiquette taille={24} couleur={C.vert}>
								il reste
							</Etiquette>
						</div>
					) : null}
					{t >= d(275) - 0.1 ? (
						<div style={{position: 'absolute', left: BARRE.x + lCharges + 10, top: 320, opacity: p(t, d(275) - 0.1, d(275) + 0.2)}}>
							<Surligne v={p(t, d(275), d(275) + 0.35)}>
								<Ecrit v={p(t, d(275) - 0.1, fi(279))} taille={46} couleur={C.stylo}>
									à épargner
								</Ecrit>
							</Surligne>
						</div>
					) : null}
				</div>
			) : null}
		</Feuille>
	);
};

/* ───────────────────────── LA VITESSE ───────────────────────── */

const VITESSE_PIECE = 300;
const INTERVALLE = 0.42;

export const Vitesse: React.FC<{t: number}> = ({t}) => {
	const a = d(288) - 0.05;
	const b = d(324) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const debut = d(297);
	const cx = 438;
	const entreeFin = cx - 90;
	const sortieDebut = cx + 90;
	const disparait = p(t, d(323) - 0.1, d(323) + 0.4);
	const pieces: React.ReactNode[] = [];
	for (let k = 0; k < 14; k++) {
		const tk = debut + k * INTERVALLE;
		const age = t - tk;
		if (age < 0) continue;
		// une pièce entre de la gauche jusqu'à la main…
		const xe = 40 + age * VITESSE_PIECE;
		if (xe < entreeFin) {
			pieces.push(<Piece key={`e${k}`} x={xe} y={250} o={Math.min(1, age * 5)} />);
		}
		// …et, au même rythme, une autre sort à droite et s'évapore
		const xs = sortieDebut + age * VITESSE_PIECE;
		if (xs < 860) {
			const o = (1 - (xs - sortieDebut) / 330) * (1 - disparait * 0.8);
			pieces.push(<Piece key={`s${k}`} x={xs} y={250} o={Math.max(0, o)} echelle={1 - (xs - sortieDebut) / 700} />);
		}
	}

	return (
		<Feuille {...CARTE} e={w.e} s={w.s} incline={1}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 26, display: 'flex', justifyContent: 'center'}}>
				<Surligne v={p(t, d(301) + 0.2, d(302) + 0.2)}>
					<Ecrit v={p(t, d(300), d(302))} taille={60}>
						même vitesse
					</Ecrit>
				</Surligne>
			</div>
			<svg width={CARTE.l} height={CARTE.h} style={{position: 'absolute', left: 0, top: 0}}>
				<Trait d={`M40 250 H${entreeFin - 20}`} v={p(t, a + 0.3, a + 0.8)} couleur="rgba(24,168,100,.35)" epaisseur={6} />
				<Trait d={`M${sortieDebut + 20} 250 H840`} v={p(t, a + 0.3, a + 0.8)} couleur="rgba(224,70,75,.35)" epaisseur={6} />
				<Trait d={`M${entreeFin - 40} 232 L${entreeFin - 20} 250 L${entreeFin - 40} 268`} v={p(t, a + 0.6, a + 0.9)} couleur={C.vert} epaisseur={6} />
				<Trait d="M810 232 L830 250 L810 268" v={p(t, a + 0.6, a + 0.9)} couleur={C.rouge} epaisseur={6} />
				{/* la main : une poche ouverte */}
				<Trait
					d={`M${cx - 80} 200 H${cx + 80} V300 Q${cx + 80} 318 ${cx + 62} 318 H${cx - 62} Q${cx - 80} 318 ${cx - 80} 300 Z M${cx - 80} 232 H${cx + 80}`}
					v={p(t, a + 0.2, a + 0.9)}
					epaisseur={6}
				/>
			</svg>
			{pieces}
			<div style={{position: 'absolute', left: cx - 70, top: 330, width: 140, textAlign: 'center'}}>
				<Ecrit v={p(t, a + 0.5, a + 1)} taille={40} style={{display: 'inline-block'}}>
					ta main
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 44, top: 300}}>
				<Ecrit v={p(t, d(307), d(309))} taille={48} couleur={C.vert}>
					entre
				</Ecrit>
			</div>
			<div style={{position: 'absolute', right: 44, top: 300}}>
				<Ecrit v={p(t, d(320), d(323))} taille={48} couleur={C.rouge}>
					disparaît
				</Ecrit>
			</div>
		</Feuille>
	);
};

const Piece: React.FC<{x: number; y: number; o: number; echelle?: number}> = ({x, y, o, echelle = 1}) => (
	<div
		style={{
			position: 'absolute',
			left: x - 26,
			top: y - 26,
			width: 52,
			height: 52,
			borderRadius: 26,
			background: C.surligneur,
			border: `4px solid ${C.stylo}`,
			opacity: o,
			transform: `scale(${echelle})`,
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center',
			fontFamily: TITRE,
			fontWeight: 900,
			fontSize: 30,
			color: C.stylo,
		}}
	>
		F
	</div>
);
