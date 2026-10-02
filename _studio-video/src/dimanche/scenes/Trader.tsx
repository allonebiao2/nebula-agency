/**
 * CHAPITRE 3 · LE TRADER (1:24 → 1:51)
 *
 *  · LA QUESTION   « pourquoi je te raconte ça, en tant que trader ? »
 *  · LA BASCULE    « C'est pareil pour le trader » : LA CHARNIÈRE DE LA VIDÉO.
 *                  La barre du budget (charges 70 %, reste 30 %) se découpe en
 *                  tranches, et chaque tranche devient une bougie : le salaire
 *                  devient le marché. Puis la semaine se pose sur le graphique,
 *                  et la loupe passe sur « les paires ».
 *  · L'IMPROVISATION  l'écran en direct, pas le papier : le curseur saute d'une
 *                  bougie à l'autre, « je saute dessus », et la croix rouge.
 *
 * ⚠️ Les paires ne sont pas nommées (« PAIRE 1 ») : il n'en nomme aucune, et un
 * nom réel coché ressemblerait à un signal d'achat.
 */
import React from 'react';
import {Easing, interpolate, interpolateColors, random} from 'remotion';
import {C, d, fi} from '../donnees';
import {Bougie, Ecrit, Etiquette, Feuille, GLISSE, Surligne, Tampon, Trait, fenetre, p, ressort} from '../outils';
import {TITRE} from '../polices';

/* ───────────────────────── LA QUESTION ───────────────────────── */

export const Question: React.FC<{t: number}> = ({t}) => {
	const a = d(324) - 0.05;
	const b = d(348) - 0.35;
	const w = fenetre(t, a, b, 0.25);
	if (!w.vis) return null;
	return (
		<Feuille x={64} y={1170} l={876} h={420} e={w.e} s={w.s}>
			<div style={{position: 'absolute', left: 40, top: 60}}>
				<Ecrit v={p(t, d(329), d(332) + 0.3)} taille={70}>
					en tant que trader,
				</Ecrit>
				<div style={{height: 20}} />
				<Ecrit v={p(t, d(333), d(343))} taille={70}>
					pourquoi ça ?
				</Ecrit>
			</div>
			<svg width={876} height={420} style={{position: 'absolute', left: 0, top: 0}}>
				<Trait
					d="M660 130 C660 70 780 60 790 125 C798 175 725 180 722 240 L722 262"
					v={p(t, d(333), d(343) + 0.4)}
					couleur={C.rouge}
					epaisseur={16}
				/>
				<circle cx={722} cy={322} r={p(t, d(345), d(345) + 0.2) * 13} fill={C.rouge} />
			</svg>
		</Feuille>
	);
};

/* ───────────────────────── LA BASCULE ───────────────────────── */

const N = 14;
const PAS = 796 / N;
const OUV = [630, 600, 575, 590, 540, 520, 545, 490, 470, 500, 440, 420, 445, 390];
const CLO = [600, 575, 590, 540, 520, 545, 490, 470, 500, 440, 420, 445, 390, 360];
const BARRE_Y = 330;
const BARRE_H = 120;

export const Bascule: React.FC<{t: number}> = ({t}) => {
	const a = d(348) - 0.2;
	const b = d(386) - 0.25;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const debutMorph = d(348) + 0.35;
	const ecarte = p(t, a + 0.1, debutMorph);
	const ligne = p(t, debutMorph + 1.1, debutMorph + 2.2, Easing.linear);
	const semaine = p(t, d(362) - 0.1, d(362) + 0.8);
	const loupe = p(t, d(372), d(385) - 0.2, GLISSE);
	const pointsClo = CLO.map((c, i) => [40 + (i + 0.5) * PAS, c] as const);
	const chemin = pointsClo.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join(' ');
	// la loupe suit la ligne des clôtures
	const lx = interpolate(loupe, [0, 1], [pointsClo[0][0], pointsClo[N - 1][0]]);
	const k = Math.min(N - 2, Math.floor((lx - pointsClo[0][0]) / PAS));
	const ly = interpolate(lx, [pointsClo[k][0], pointsClo[k + 1][0]], [pointsClo[k][1], pointsClo[k + 1][1]]);

	return (
		<Feuille x={64} y={730} l={876} h={880} e={w.e} s={w.s} incline={-0.8}>
			<div style={{position: 'absolute', left: 40, top: 34, display: 'flex', alignItems: 'baseline', gap: 22}}>
				<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 120, lineHeight: 1, color: C.stylo, opacity: p(t, d(348), d(348) + 0.2)}}>
					C'EST
				</span>
				<Surligne v={p(t, d(350), d(350) + 0.3)}>
					<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 120, lineHeight: 1, color: C.stylo, opacity: p(t, d(349), d(349) + 0.2)}}>
						PAREIL
					</span>
				</Surligne>
			</div>
			<div style={{position: 'absolute', left: 44, top: 176}}>
				<Ecrit v={p(t, d(351), fi(353))} taille={56}>
					pour le trader
				</Ecrit>
			</div>
			{t >= d(369) - 0.1 ? (
				<div style={{position: 'absolute', right: 50, top: 170, transform: 'rotate(-4deg)'}}>
					<Ecrit v={p(t, d(369) - 0.1, fi(370))} taille={66} couleur={C.rouge}>
						comment ?
					</Ecrit>
				</div>
			) : null}

			<svg width={876} height={880} style={{position: 'absolute', left: 0, top: 0}}>
				{/* la semaine posée sur le graphique */}
				{[1, 2, 3, 4].map((c) => (
					<line
						key={c}
						x1={40 + c * (796 / 5)}
						x2={40 + c * (796 / 5)}
						y1={290}
						y2={interpolate(semaine, [0, 1], [290, 690])}
						stroke="rgba(28,43,75,.35)"
						strokeWidth={3}
						strokeDasharray="10 12"
					/>
				))}
				{/* chaque tranche de la barre devient une bougie */}
				{OUV.map((o, i) => {
					const c = CLO[i];
					const m = p(t, debutMorph + i * 0.045, debutMorph + 0.75 + i * 0.045, GLISSE);
					const cx = 40 + (i + 0.5) * PAS;
					const trancheX = 40 + i * PAS + ecarte * 2;
					const trancheL = PAS - ecarte * 4;
					const dansCharges = cx < 40 + 796 * 0.7;
					const couleur = interpolateColors(m, [0, 1], [dansCharges ? C.stylo : C.vert, c < o ? C.vert : C.rouge]);
					const y0 = Math.min(o, c);
					const h = Math.max(8, Math.abs(o - c));
					return (
						<g key={i}>
							<line
								x1={cx}
								x2={cx}
								y1={y0 - 26}
								y2={y0 + h + 26}
								stroke={c < o ? C.vert : C.rouge}
								strokeWidth={4}
								strokeLinecap="round"
								opacity={p(m, 0.75, 1, Easing.linear)}
							/>
							<rect
								x={interpolate(m, [0, 1], [trancheX, cx - 15])}
								y={interpolate(m, [0, 1], [BARRE_Y, y0])}
								width={interpolate(m, [0, 1], [trancheL, 30])}
								height={interpolate(m, [0, 1], [BARRE_H, h])}
								rx={interpolate(m, [0, 1], [i === 0 || i === N - 1 ? 14 : 3, 4])}
								fill={couleur}
								opacity={Math.min(1, p(t, a, a + 0.25) * 1.2)}
							/>
						</g>
					);
				})}
				<Trait d={chemin} v={ligne} couleur={C.stylo} epaisseur={4} />
				{/* la loupe : analyser les paires */}
				{loupe > 0 && loupe < 1 ? (
					<g transform={`translate(${lx} ${ly})`} opacity={Math.min(1, loupe * 8, (1 - loupe) * 8)}>
						<circle r={64} fill="rgba(255,225,77,.22)" stroke={C.stylo} strokeWidth={8} />
						<line x1={46} y1={46} x2={96} y2={96} stroke={C.stylo} strokeWidth={14} strokeLinecap="round" />
					</g>
				) : null}
			</svg>
			{['Lun', 'Mar', 'Mer', 'Jeu', 'Ven'].map((j, n) => (
				<div
					key={j}
					style={{
						position: 'absolute',
						left: 40 + n * (796 / 5),
						width: 796 / 5,
						top: 262,
						textAlign: 'center',
						opacity: p(t, d(362) + n * 0.08, d(362) + 0.3 + n * 0.08),
					}}
				>
					<Etiquette taille={24} couleur={C.gris}>
						{j}
					</Etiquette>
				</div>
			))}
			<div style={{position: 'absolute', left: 40, right: 40, top: 730, display: 'flex', gap: 22}}>
				{[0, 1, 2].map((n) => {
					const r = ressort(t, d(374) + n * 0.22, {damping: 12, stiffness: 230});
					const choisi = p(t, d(380) + n * 0.1, d(380) + 0.3 + n * 0.1);
					return (
						<div
							key={n}
							style={{
								flex: 1,
								height: 92,
								borderRadius: 46,
								border: `4px solid ${C.stylo}`,
								background: interpolateColors(choisi, [0, 1], ['rgba(255,255,255,.4)', C.surligneur]),
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
								opacity: Math.min(1, r * 2),
								transform: `translateY(${(1 - r) * 40}px) scale(${interpolate(r, [0, 1], [0.8, 1])})`,
							}}
						>
							<Etiquette taille={32}>Paire {n + 1}</Etiquette>
						</div>
					);
				})}
			</div>
		</Feuille>
	);
};

/* ───────────────────────── L'IMPROVISATION ───────────────────────── */

/** Une marche au hasard, figée par la graine : le marché qui défile en direct. */
const DIRECT = (() => {
	let prix = 200;
	return Array.from({length: 120}, (_, k) => {
		const o = prix;
		const c = o + (random(`c${k}`) - 0.5) * 60;
		prix = Math.max(110, Math.min(300, c));
		const hi = Math.min(o, c) - 8 - random(`h${k}`) * 24;
		const lo = Math.max(o, c) + 8 + random(`l${k}`) * 24;
		return {o, c: prix, hi, lo};
	});
})();

export const Improviser: React.FC<{t: number}> = ({t}) => {
	const a = d(386) - 0.1;
	const b = d(435) - 0.25;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const defile = (t - a) * 70;
	const saute = d(425) - 0.05;
	// le curseur : il saute d'un point à l'autre toutes les 0,5 s, sans plan
	const pas = 0.5;
	const n = Math.floor((t - a) / pas);
	const cible = (m: number) => ({x: 120 + random(`cx${m}`) * 620, y: 110 + random(`cy${m}`) * 230});
	const avant = cible(n - 1);
	const apres = cible(n);
	const mouv = p(t, a + n * pas, a + n * pas + 0.16, Easing.out(Easing.cubic));
	let cur = {x: interpolate(mouv, [0, 1], [avant.x, apres.x]), y: interpolate(mouv, [0, 1], [avant.y, apres.y])};
	const achat = {x: 660, y: 190};
	if (t >= saute) cur = {x: interpolate(p(t, saute, saute + 0.2), [0, 1], [cur.x, achat.x]), y: interpolate(p(t, saute, saute + 0.2), [0, 1], [cur.y, achat.y])};
	const clic = (t - (a + n * pas) - 0.16) / 0.3;
	const non = p(t, d(428), d(428) + 0.4, Easing.linear);

	return (
		<Feuille x={64} y={1150} l={876} h={460} e={w.e} s={w.s} incline={0.8} sombre>
			<div style={{position: 'absolute', left: 30, top: 24, display: 'flex', alignItems: 'center', gap: 14}}>
				<div style={{width: 18, height: 18, borderRadius: 9, background: C.rouge, opacity: 0.5 + 0.5 * Math.abs(Math.sin(t * 4))}} />
				<Etiquette taille={22} couleur={C.blanc}>
					En direct
				</Etiquette>
			</div>
			<div style={{position: 'absolute', right: 30, top: 24}}>
				<Etiquette taille={22} couleur={C.gris}>
					sans plan
				</Etiquette>
			</div>
			<svg width={876} height={460} style={{position: 'absolute', left: 0, top: 0}}>
				<rect x={20} y={70} width={836} height={300} rx={16} fill="rgba(255,255,255,.03)" />
				{DIRECT.map((k, i) => {
					const x = 40 + i * 40 - defile;
					if (x < 36 || x > 840) return null;
					return <Bougie key={i} x={x} haut={k.hi} bas={k.lo} o={k.o} c={k.c} l={22} />;
				})}
				{/* le trade pris sur un coup de tête */}
				{t >= saute + 0.15 ? (
					<g opacity={p(t, saute + 0.15, saute + 0.3)}>
						<path d={`M${achat.x - 22} ${achat.y + 40} L${achat.x} ${achat.y + 4} L${achat.x + 22} ${achat.y + 40} Z`} fill={C.vertClair} />
						<line x1={20} x2={856} y1={achat.y + 22} y2={achat.y + 22} stroke={C.vertClair} strokeWidth={2} strokeDasharray="8 8" />
					</g>
				) : null}
				{non > 0 ? (
					<>
						<Trait d={`M${achat.x - 90} ${achat.y - 70} L${achat.x + 90} ${achat.y + 110}`} v={p(non, 0, 0.5, Easing.linear)} couleur={C.rouge} epaisseur={18} />
						<Trait d={`M${achat.x + 90} ${achat.y - 70} L${achat.x - 90} ${achat.y + 110}`} v={p(non, 0.5, 1, Easing.linear)} couleur={C.rouge} epaisseur={18} />
					</>
				) : null}
				{/* le clic, et le curseur */}
				{clic > 0 && clic < 1 && t < saute ? (
					<circle cx={cur.x} cy={cur.y} r={10 + clic * 34} fill="none" stroke={C.surligneur} strokeWidth={4} opacity={1 - clic} />
				) : null}
				<path
					d="M0 0 L0 38 L10 29 L17 45 L24 42 L17 26 L30 26 Z"
					transform={`translate(${cur.x} ${cur.y})`}
					fill={C.blanc}
					stroke={C.encre}
					strokeWidth={3}
					strokeLinejoin="round"
				/>
			</svg>
			<div
				style={{
					position: 'absolute',
					right: 30,
					bottom: 26,
					padding: '14px 34px',
					borderRadius: 40,
					background: t >= saute && t < saute + 0.9 ? C.vertClair : 'rgba(24,168,100,.35)',
					transform: `scale(${t >= saute && t < saute + 0.25 ? 0.93 : 1})`,
				}}
			>
				<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 44, color: C.blanc, letterSpacing: '0.06em'}}>ACHAT</span>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 330, display: 'flex', justifyContent: 'flex-start', paddingLeft: 40}}>
				<Tampon t={t} a={d(409) - 0.05} taille={84} incline={-5} fond="rgba(16,19,26,.9)">
					Improviser
				</Tampon>
			</div>
		</Feuille>
	);
};
