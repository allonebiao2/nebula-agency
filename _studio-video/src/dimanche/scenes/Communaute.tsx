/**
 * CHAPITRE 5 · LA COMMUNAUTÉ (2:21 → 2:51)
 *
 *  · DIMANCHE 21 H   la page du calendrier, l'horloge qui tourne jusqu'à 21:00.
 *  · LES MEMBRES     le nom de la communauté, et un réseau qui se relie ;
 *                    la nouvelle semaine s'allume jour par jour.
 *  · LES OPPORTUNITÉS  un balayage passe sur le graphique ; chaque opportunité
 *                    s'allume quand il la touche.
 *  · VALIDER         quatre paires : deux cochées, deux barrées.
 *  · LES RÉSULTATS   une flèche qui monte, SANS aucun chiffre.
 *  · L'INVITATION    la case « planifier ma semaine », vide : à toi de la cocher.
 */
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, COMMUNAUTE, d, fi} from '../donnees';
import {Bougie, Case, Ecrit, Etiquette, Feuille, Surligne, Trait, fenetre, p, ressort} from '../outils';
import {TITRE} from '../polices';

const CARTE = {x: 64, y: 1170, l: 876, h: 420};

/* ───────────────────────── DIMANCHE 21 H ───────────────────────── */

export const Horloge: React.FC<{t: number; x: number; y: number; r: number; arrivee: number; debut: number; couleur?: string}> = ({
	t,
	x,
	y,
	r,
	arrivee,
	debut,
	couleur = C.stylo,
}) => {
	const k = p(t, debut, arrivee, Easing.inOut(Easing.cubic));
	const heure = interpolate(k, [0, 1], [150, 270 + 360]); // finit sur 9 h, soit 21 h
	const minute = interpolate(k, [0, 1], [0, 360 * 4]);
	return (
		<g transform={`translate(${x} ${y})`}>
			<Trait d={`M0 ${-r} A${r} ${r} 0 1 1 -0.1 ${-r}`} v={p(t, debut - 0.6, debut)} couleur={couleur} epaisseur={7} />
			{Array.from({length: 12}, (_, i) => {
				const ang = (i / 12) * Math.PI * 2;
				const l = i % 3 === 0 ? 22 : 11;
				return (
					<line
						key={i}
						x1={Math.sin(ang) * (r - 14)}
						y1={-Math.cos(ang) * (r - 14)}
						x2={Math.sin(ang) * (r - 14 - l)}
						y2={-Math.cos(ang) * (r - 14 - l)}
						stroke={couleur}
						strokeWidth={i % 3 === 0 ? 6 : 4}
						strokeLinecap="round"
						opacity={p(t, debut - 0.4 + i * 0.02, debut - 0.2 + i * 0.02)}
					/>
				);
			})}
			<line x1={0} y1={0} x2={0} y2={-r * 0.5} stroke={couleur} strokeWidth={11} strokeLinecap="round" transform={`rotate(${heure})`} />
			<line x1={0} y1={0} x2={0} y2={-r * 0.78} stroke={C.rouge} strokeWidth={6} strokeLinecap="round" transform={`rotate(${minute})`} />
			<circle r={11} fill={couleur} />
		</g>
	);
};

export const Dimanche21h: React.FC<{t: number}> = ({t}) => {
	const a = d(566) - 0.1;
	const b = d(578) - 0.25;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const heure = ressort(t, d(573) + 0.25, {damping: 12});
	return (
		<Feuille {...CARTE} e={w.e} s={w.s}>
			<div
				style={{
					position: 'absolute',
					left: 40,
					top: 40,
					width: 350,
					height: 330,
					borderRadius: 20,
					background: C.blanc,
					boxShadow: '0 10px 24px -12px rgba(0,0,0,.4)',
					overflow: 'hidden',
					transform: `rotate(-2deg) translateY(${(1 - ressort(t, d(569) - 0.1)) * 30}px)`,
					opacity: p(t, d(569) - 0.1, d(569) + 0.2),
				}}
			>
				<div style={{height: 84, background: C.rouge, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					<Etiquette taille={26} couleur={C.blanc}>
						Aujourd'hui
					</Etiquette>
				</div>
				<div style={{fontFamily: TITRE, fontWeight: 900, fontSize: 72, color: C.stylo, textAlign: 'center', marginTop: 74, letterSpacing: '0.01em'}}>
					DIMANCHE
				</div>
			</div>
			<svg width={CARTE.l} height={CARTE.h} style={{position: 'absolute', left: 0, top: 0}}>
				<Horloge t={t} x={640} y={180} r={140} debut={d(572) - 0.1} arrivee={d(574) + 0.3} />
			</svg>
			<div
				style={{
					position: 'absolute',
					left: 500,
					width: 280,
					top: 334,
					textAlign: 'center',
					fontFamily: TITRE,
					fontWeight: 900,
					fontSize: 64,
					lineHeight: 1,
					color: C.stylo,
					opacity: Math.min(1, heure * 2),
					transform: `scale(${interpolate(heure, [0, 1], [0.6, 1])})`,
				}}
			>
				21 H
			</div>
		</Feuille>
	);
};

/* ───────────────────────── LES MEMBRES ───────────────────────── */

const NOEUDS: [number, number][] = [
	[600, 70], [700, 110], [800, 60], [640, 190], [760, 200], [840, 150], [580, 290], [690, 290], [810, 280],
];
const LIENS: [number, number][] = [[0, 1], [1, 2], [0, 3], [1, 3], [1, 4], [2, 5], [4, 5], [3, 6], [3, 7], [4, 7], [4, 8], [5, 8], [6, 7], [7, 8]];

/** Le nom de la communauté, sur la plaque sombre. Réutilisé plus loin. */
export const Marque: React.FC<{t: number; a: number; taille?: number}> = ({t, a, taille = 100}) => (
	<div style={{fontFamily: TITRE, fontWeight: 900, fontSize: taille, lineHeight: 0.92, color: C.blanc, textTransform: 'uppercase'}}>
		{COMMUNAUTE.split(' ').reduce<string[][]>((l, m, i) => (i === 0 ? [[m]] : i === 1 ? [...l, [m]] : [l[0], [...l[1], m]]), []).map((ligne, n) => {
			const r = ressort(t, a + n * 0.12, {damping: 13, stiffness: 200});
			return (
				<div key={n} style={{opacity: Math.min(1, r * 2), transform: `translateY(${(1 - r) * 40}px)`}}>
					{ligne.join(' ')}
				</div>
			);
		})}
	</div>
);

export const Membres: React.FC<{t: number}> = ({t}) => {
	const a = d(578) - 0.25;
	const b = d(597) - 0.25;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const reseau = p(t, d(578), d(586) + 0.4, Easing.linear);
	return (
		<Feuille x={64} y={1160} l={876} h={440} e={w.e} s={w.s} sombre incline={1}>
			<div style={{position: 'absolute', left: 40, top: 36}}>
				<Ecrit v={p(t, d(580), d(583) + 0.3)} taille={46} couleur={C.surligneur}>
					ma communauté
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 40, top: 104}}>
				<Marque t={t} a={d(584) - 0.1} taille={96} />
			</div>
			<svg width={876} height={440} style={{position: 'absolute', left: 0, top: 0}}>
				{LIENS.map(([i, j], n) => (
					<Trait
						key={n}
						d={`M${NOEUDS[i][0]} ${NOEUDS[i][1]} L${NOEUDS[j][0]} ${NOEUDS[j][1]}`}
						v={p(reseau, n / LIENS.length, Math.min(1, n / LIENS.length + 0.2), Easing.linear)}
						couleur="rgba(251,248,241,.35)"
						epaisseur={3}
					/>
				))}
				{NOEUDS.map(([x, y], n) => (
					<circle key={n} cx={x} cy={y} r={14 * ressort(t, d(578) + n * 0.12, {damping: 10})} fill={n % 3 === 0 ? C.surligneur : C.blanc} />
				))}
			</svg>
			{/* la nouvelle semaine, qui s'allume jour par jour */}
			<div style={{position: 'absolute', left: 40, right: 40, top: 336, display: 'flex', gap: 10}}>
				{['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((j, n) => {
					const allume = p(t, d(593) + n * 0.12, d(593) + 0.2 + n * 0.12);
					return (
						<div
							key={n}
							style={{
								flex: 1,
								height: 62,
								borderRadius: 12,
								border: '2px solid rgba(251,248,241,.3)',
								background: interpolate(allume, [0, 1], [0, 1]) > 0.5 ? C.surligneur : 'rgba(251,248,241,.06)',
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
								fontFamily: TITRE,
								fontWeight: 800,
								fontSize: 34,
								color: allume > 0.5 ? C.encre : 'rgba(251,248,241,.6)',
								opacity: p(t, d(588), d(590)),
							}}
						>
							{j}
						</div>
					);
				})}
			</div>
		</Feuille>
	);
};

/* ───────────────────────── LES OPPORTUNITÉS ───────────────────────── */

const MARCHE = [
	[300, 260], [260, 230], [230, 270], [270, 320], [320, 340], [340, 300], [300, 250], [250, 210], [210, 240], [240, 290], [290, 330], [330, 310], [310, 260], [260, 220],
];
const OPPORTUNITES = [3.5, 7.5, 12.5];

export const Opportunites: React.FC<{t: number}> = ({t}) => {
	const a = d(597) - 0.2;
	const b = d(623) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const pas = 796 / MARCHE.length;
	const balayage = p(t, d(605), d(620), Easing.linear);
	const xb = 40 + balayage * 796;
	return (
		<Feuille {...CARTE} e={w.e} s={w.s} incline={-1}>
			<div style={{position: 'absolute', left: 40, top: 28}}>
				<Ecrit v={p(t, d(608), fi(611))} taille={54}>
					chercher les opportunités
				</Ecrit>
			</div>
			<svg width={CARTE.l} height={CARTE.h} style={{position: 'absolute', left: 0, top: 0}}>
				{MARCHE.map(([o, c], i) => (
					<Bougie key={i} x={40 + (i + 0.5) * pas} haut={Math.min(o, c) - 18} bas={Math.max(o, c) + 18} o={o} c={c} v={p(t, a + 0.3 + i * 0.04, a + 0.6 + i * 0.04)} pale={40 + (i + 0.5) * pas > xb + 6} />
				))}
				{balayage > 0 && balayage < 1 ? (
					<>
						<rect x={xb - 60} y={120} width={60} height={270} fill="url(#trainee)" />
						<line x1={xb} x2={xb} y1={120} y2={390} stroke={C.surligneur} strokeWidth={5} />
					</>
				) : null}
				<defs>
					<linearGradient id="trainee" x1="0" x2="1">
						<stop offset="0" stopColor={C.surligneur} stopOpacity={0} />
						<stop offset="1" stopColor={C.surligneur} stopOpacity={0.35} />
					</linearGradient>
				</defs>
				{OPPORTUNITES.map((k, n) => {
					const x = 40 + k * pas;
					const quand = d(605) + ((x - 40) / 796) * (d(620) - d(605));
					const r = ressort(t, quand, {damping: 9, stiffness: 200});
					const onde = p(t, quand, quand + 0.8, Easing.linear);
					const [o, c] = MARCHE[Math.floor(k)];
					const y = Math.max(o, c) + 30;
					return (
						<g key={n}>
							{onde > 0 && onde < 1 ? <circle cx={x} cy={y} r={20 + onde * 50} fill="none" stroke={C.stylo} strokeWidth={4} opacity={1 - onde} /> : null}
							<circle cx={x} cy={y} r={22 * r} fill={C.surligneur} stroke={C.stylo} strokeWidth={5} />
						</g>
					);
				})}
			</svg>
		</Feuille>
	);
};

/* ───────────────────────── VALIDER ───────────────────────── */

export const Valider: React.FC<{t: number}> = ({t}) => {
	const a = d(623) - 0.2;
	const b = d(636) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	return (
		<Feuille {...CARTE} e={w.e} s={w.s} incline={1}>
			{[0, 1, 2, 3].map((n) => {
				const ok = n % 2 === 0;
				const quand = ok ? d(624) + (n / 2) * 0.2 : d(626) + ((n - 1) / 2) * 0.2;
				const e = p(t, a + 0.3 + n * 0.08, a + 0.6 + n * 0.08);
				const barre = ok ? 0 : p(t, quand + 0.2, quand + 0.5);
				return (
					<div
						key={n}
						style={{
							position: 'absolute',
							left: 40 + (n % 2) * 410,
							top: 50 + Math.floor(n / 2) * 120,
							display: 'flex',
							alignItems: 'center',
							gap: 20,
							opacity: e * (1 - barre * 0.45),
						}}
					>
						<Case v={e} coche={p(t, quand, quand + 0.3, Easing.linear)} croix={!ok} taille={72} />
						<div style={{position: 'relative'}}>
							<Etiquette taille={40}>Paire {n + 1}</Etiquette>
							<div style={{position: 'absolute', left: -6, right: -6, top: '52%', height: 5, background: C.rouge, transformOrigin: 'left', transform: `scaleX(${barre})`}} />
						</div>
					</div>
				);
			})}
			<div style={{position: 'absolute', right: 40, bottom: 40}}>
				<Surligne v={p(t, d(635) - 0.1, d(635) + 0.3)}>
					<Ecrit v={p(t, d(633), fi(635))} taille={56}>
						notre stratégie
					</Ecrit>
				</Surligne>
			</div>
			<div style={{position: 'absolute', left: 40, bottom: 44, opacity: p(t, d(624), d(624) + 0.3)}}>
				<Etiquette taille={24} couleur={C.gris}>
					valider · écarter
				</Etiquette>
			</div>
		</Feuille>
	);
};

/* ───────────────────────── LES RÉSULTATS ───────────────────────── */

export const Resultats: React.FC<{t: number}> = ({t}) => {
	const a = d(636) - 0.2;
	const b = d(656) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const fleche = p(t, d(643), d(652), Easing.inOut(Easing.cubic));
	return (
		<Feuille {...CARTE} e={w.e} s={w.s}>
			<svg width={CARTE.l} height={CARTE.h} style={{position: 'absolute', left: 0, top: 0}}>
				<Trait d="M60 370 L230 300 L330 330 L490 220 L590 250 L790 110" v={fleche} couleur={C.vert} epaisseur={14} />
				<Trait d="M720 102 L792 108 L780 178" v={p(t, d(652) - 0.1, d(652) + 0.3, Easing.linear)} couleur={C.vert} epaisseur={14} />
			</svg>
			<div style={{position: 'absolute', left: 40, top: 30}}>
				<Ecrit v={p(t, d(650), d(655))} taille={54}>
					des résultats
				</Ecrit>
				<div style={{height: 10}} />
				<Surligne v={p(t, d(654), d(655) + 0.2)}>
					<Ecrit v={p(t, d(653), fi(655))} taille={54}>
						plus intéressants
					</Ecrit>
				</Surligne>
			</div>
		</Feuille>
	);
};

/* ───────────────────────── L'INVITATION ───────────────────────── */

export const Invitation: React.FC<{t: number}> = ({t}) => {
	const a = d(656) - 0.1;
	const b = d(677) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const pouls = 1 + 0.06 * Math.max(0, Math.sin((t - d(662)) * 5)) * p(t, d(662), d(662) + 0.3);
	return (
		<Feuille {...CARTE} e={w.e} s={w.s} incline={-1}>
			<div style={{position: 'absolute', left: 40, top: 34}}>
				<Ecrit v={p(t, a + 0.3, a + 1.0)} taille={46} couleur={C.gris}>
					à faire ce dimanche :
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 40, top: 130, display: 'flex', alignItems: 'center', gap: 30}}>
				<div style={{transform: `scale(${pouls})`}}>
					<Case v={p(t, d(660), d(660) + 0.4, Easing.linear)} coche={0} taille={110} />
				</div>
				<div>
					<Ecrit v={p(t, d(661), d(666))} taille={80}>
						planifier ma semaine
					</Ecrit>
					<svg width={620} height={30} style={{display: 'block', marginTop: 4}}>
						<Trait d="M4 10 C200 4 420 14 612 6" v={p(t, d(670), d(670) + 0.4, Easing.linear)} couleur={C.rouge} epaisseur={6} />
						<Trait d="M40 24 C220 18 420 28 580 20" v={p(t, d(670) + 0.3, d(670) + 0.7, Easing.linear)} couleur={C.rouge} epaisseur={5} />
					</svg>
				</div>
			</div>
			<div style={{position: 'absolute', right: 40, bottom: 40}}>
				<Surligne v={p(t, d(672), d(672) + 0.3)}>
					<Ecrit v={p(t, d(671), d(674))} taille={54}>
						à toi de cocher
					</Ecrit>
				</Surligne>
			</div>
		</Feuille>
	);
};
