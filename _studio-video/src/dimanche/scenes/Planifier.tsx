/**
 * CHAPITRE 1 · PLANIFIER (0:00 → 0:28)
 *
 *  · L'ÉCHO        « Je ne le répéterai jamais assez » : la phrase se répète.
 *  · LA SEMAINE    « avant le début de ta semaine » : le DIMANCHE quitte la fin
 *                  de la semaine et passe DEVANT le lundi. Puis la semaine
 *                  devient la première ligne du mois.
 *  · LES PROFILS   étudiant, fonctionnaire, entrepreneur, trader : un badge par mot.
 *  · LE TAMPON     « tu ne vas JAMAIS réussir » s'écrase sur les quatre.
 *  · L'AVANCE      deux traits de course ; celui qui part le dimanche garde
 *                  « une longueur d'avance ».
 */
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, d, fi} from '../donnees';
import {Ecrit, Etiquette, Feuille, GLISSE, Surligne, Tampon, Trait, fenetre, p, ressort} from '../outils';
import {TEXTE, TITRE} from '../polices';

const CARTE = {x: 64, y: 1170, l: 876, h: 420};

/* ───────────────────────── L'ÉCHO ───────────────────────── */

export const Echo: React.FC<{t: number}> = ({t}) => {
	const fin = d(6) - 0.2;
	if (t > fin + 0.5) return null;
	const s = p(t, fin, fin + 0.4, Easing.in(Easing.cubic));
	const petit = p(t, 0.02, 0.45);
	const j = ressort(t, d(4) - 0.05, {damping: 12, stiffness: 220});
	const a = ressort(t, d(5) - 0.05, {damping: 12, stiffness: 220});

	const bloc = (couleurJ: string, couleurA: string, contour: boolean) => (
		<div style={{fontFamily: TITRE, fontWeight: 900, fontSize: 230, lineHeight: 0.86, textAlign: 'center', letterSpacing: '0.01em'}}>
			{[
				['JAMAIS', couleurJ, j],
				['ASSEZ', couleurA, a],
			].map(([mot, couleur, r]) => (
				<div
					key={mot as string}
					style={{
						color: contour ? 'transparent' : (couleur as string),
						WebkitTextStroke: contour ? `3px ${C.surligneur}` : undefined,
						transform: `translateY(${interpolate(r as number, [0, 1], [60, 0])}px)`,
						opacity: Math.min(1, (r as number) * 2),
					}}
				>
					{mot as string}
				</div>
			))}
		</div>
	);

	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: 1110, opacity: 1 - s, transform: `scale(${1 - s * 0.06})`}}>
			<div
				style={{
					fontFamily: TEXTE,
					fontWeight: 800,
					fontSize: 46,
					color: C.blanc,
					textAlign: 'center',
					letterSpacing: '0.08em',
					textTransform: 'uppercase',
					opacity: petit,
					transform: `translateY(${(1 - petit) * 20}px)`,
					textShadow: '0 3px 16px rgba(0,0,0,.6)',
				}}
			>
				Je ne le répéterai
			</div>
			<div style={{position: 'relative', marginTop: 10}}>
				{/* les échos : deux copies au trait qui montent et s'effacent, la phrase qu'on répète */}
				{[1, 2].map((n) => {
					const e = p(t, d(5) + 0.1 + n * 0.16, d(5) + 0.9 + n * 0.16);
					return (
						<div
							key={n}
							style={{
								position: 'absolute',
								inset: 0,
								transform: `translateY(${-e * 70 * n}px) scale(${1 + e * 0.04 * n})`,
								opacity: e > 0 ? (1 - e) * 0.9 : 0,
							}}
						>
							{bloc(C.blanc, C.surligneur, true)}
						</div>
					);
				})}
				<div style={{position: 'relative', textShadow: '0 10px 40px rgba(0,0,0,.5)'}}>{bloc(C.blanc, C.surligneur, false)}</div>
			</div>
		</div>
	);
};

/* ───────────────────────── LA SEMAINE ───────────────────────── */

const JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const CASE_L = 104;
const ECART = 12;

export const Semaine: React.FC<{t: number}> = ({t}) => {
	const a = d(6) - 0.15;
	const b = d(42) - 0.25;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const leve = p(t, d(12), d(12) + 0.35);
	const passe = p(t, d(14) + 0.05, d(14) + 1.0, GLISSE);
	const mois = p(t, d(24), d(24) + 0.8, GLISSE);
	const hCase = interpolate(mois, [0, 1], [170, 50]);
	const haut = 118;

	return (
		<Feuille {...CARTE} e={w.e} s={w.s}>
			<div style={{position: 'absolute', left: 40, top: 30, width: 500, height: 70}}>
				<div style={{position: 'absolute', opacity: 1 - mois}}>
					<Ecrit v={p(t, a + 0.25, a + 0.9)} taille={62}>
						Ma semaine
					</Ecrit>
				</div>
				<div style={{position: 'absolute', opacity: mois}}>
					<Ecrit v={p(t, d(24) + 0.3, d(24) + 0.9)} taille={62}>
						Mon mois
					</Ecrit>
				</div>
			</div>
			<div style={{position: 'absolute', right: 40, top: 40, opacity: p(t, d(12), d(12) + 0.4)}}>
				<Etiquette taille={24} couleur={C.gris}>
					quelques heures, avant
				</Etiquette>
			</div>

			{/* la première ligne : les sept jours, le dimanche qui passe devant */}
			{JOURS.map((j, i) => {
				const dim = i === 6;
				const place = dim ? interpolate(passe, [0, 1], [6, 0]) : i + passe;
				const arc = dim ? -110 * Math.sin(Math.PI * passe) - 26 * leve * (1 - passe) : 0;
				const e = ressort(t, a + 0.3 + i * 0.05, {damping: 15});
				return (
					<div
						key={j}
						style={{
							position: 'absolute',
							left: 40 + place * (CASE_L + ECART),
							top: haut,
							width: CASE_L,
							height: hCase,
							borderRadius: 14,
							border: `3px solid ${C.stylo}`,
							background: dim && leve > 0 ? C.surligneur : 'rgba(255,255,255,.35)',
							transform: `translateY(${arc + (1 - e) * 40}px) rotate(${dim ? -4 * Math.sin(Math.PI * passe) : 0}deg)`,
							opacity: Math.min(1, e * 2),
							zIndex: dim ? 2 : 1,
							boxShadow: dim ? `0 ${12 * leve}px ${24 * leve}px -8px rgba(0,0,0,.35)` : undefined,
							display: 'flex',
							flexDirection: 'column',
							alignItems: 'center',
							paddingTop: interpolate(mois, [0, 1], [16, 6]),
						}}
					>
						<div style={{fontFamily: TITRE, fontWeight: 800, fontSize: interpolate(mois, [0, 1], [40, 30]), color: C.stylo, textTransform: 'uppercase'}}>
							{j}
						</div>
						{dim ? (
							<div style={{marginTop: 16, opacity: (1 - mois) * p(t, d(14) + 0.7, d(14) + 1.1)}}>
								<Ecrit v={p(t, d(14) + 0.75, d(14) + 1.3)} taille={36}>
									le plan
								</Ecrit>
							</div>
						) : null}
					</div>
				);
			})}

			{/* le mois : trois lignes de plus, en dessous */}
			{[1, 2, 3].map((r) =>
				JOURS.map((j, i) => {
					const e = p(t, d(24) + 0.5 + r * 0.12 + i * 0.03, d(24) + 0.9 + r * 0.12 + i * 0.03);
					if (e <= 0) return null;
					return (
						<div
							key={`${r}-${j}`}
							style={{
								position: 'absolute',
								left: 40 + i * (CASE_L + ECART),
								top: haut + r * (50 + 12),
								width: CASE_L,
								height: 50,
								borderRadius: 12,
								border: `3px solid ${C.stylo}`,
								opacity: e * (i === 0 ? 1 : 0.55),
								background: i === 0 ? C.surligneur : 'rgba(255,255,255,.3)',
								transform: `translateY(${(1 - e) * -20}px)`,
							}}
						/>
					);
				}),
			)}
		</Feuille>
	);
};

/* ───────────────────────── LES PROFILS ───────────────────────── */

const ICONES: Record<string, string> = {
	Étudiant: 'M8 30 L40 16 L72 30 L40 44 Z M22 36 V52 C22 60 58 60 58 52 V36 M72 30 V50',
	Fonctionnaire: 'M10 30 L40 13 L70 30 Z M17 34 V60 M31 34 V60 M49 34 V60 M63 34 V60 M9 65 H71',
	Entrepreneur: 'M12 28 H68 V64 H12 Z M30 28 V19 H50 V28 M12 44 H68 M36 44 V50 H44 V44',
	Trader: 'M22 12 V66 M16 26 H28 V52 H16 Z M42 8 V52 M36 16 H48 V38 H36 Z M62 22 V66 M56 32 H68 V56 H56 Z',
};
const PROFILS: [string, number][] = [
	['Étudiant', 45],
	['Fonctionnaire', 49],
	['Entrepreneur', 53],
	['Trader', 58],
];

export const Profils: React.FC<{t: number}> = ({t}) => {
	const b = fi(63) + 0.2;
	if (t < d(42) || t > b + 0.4) return null;
	const ecrase = p(t, d(62), d(62) + 0.2);
	const s = p(t, b, b + 0.35);
	return (
		<>
			{PROFILS.map(([nom, i], n) => {
				const r = ressort(t, d(i) - 0.08, {damping: 11, stiffness: 240, mass: 0.6});
				const x = 64 + (n % 2) * 446;
				const y = 1190 + Math.floor(n / 2) * 190;
				return (
					<div
						key={nom}
						style={{
							position: 'absolute',
							left: x,
							top: y,
							width: 430,
							height: 160,
							borderRadius: 26,
							background: 'rgba(16,19,26,.78)',
							border: `2px solid rgba(251,248,241,.16)`,
							display: 'flex',
							alignItems: 'center',
							gap: 22,
							paddingLeft: 30,
							opacity: Math.min(1, r * 2) * (1 - ecrase * 0.88) * (1 - s),
							transform: `translateY(${(1 - r) * 60 + ecrase * 70}px) scale(${interpolate(r, [0, 1], [0.7, 1]) - ecrase * 0.06}) rotate(${ecrase * (n % 2 ? 3 : -3)}deg)`,
							boxShadow: '0 20px 40px -18px rgba(0,0,0,.6)',
						}}
					>
						<svg width={80} height={80} viewBox="0 0 80 80">
							<Trait d={ICONES[nom]} v={p(t, d(i), d(i) + 0.5)} couleur={C.surligneur} epaisseur={5} />
						</svg>
						<div style={{fontFamily: TITRE, fontWeight: 800, fontSize: 58, color: C.blanc, textTransform: 'uppercase', letterSpacing: '0.02em'}}>
							{nom}
						</div>
					</div>
				);
			})}
		</>
	);
};

/* ───────────────────────── LE TAMPON « JAMAIS » ───────────────────────── */

export const Jamais: React.FC<{t: number}> = ({t}) => {
	const a = d(59) - 0.05;
	const b = fi(63) + 0.2;
	if (t < a || t > b + 0.45) return null;
	const s = p(t, b, b + 0.4, Easing.in(Easing.cubic));
	const haut = p(t, a, a + 0.3);
	const bas = ressort(t, d(63) - 0.05, {damping: 13});
	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: 1150, textAlign: 'center', opacity: 1 - s}}>
			<div
				style={{
					fontFamily: TEXTE,
					fontWeight: 800,
					fontSize: 58,
					color: C.blanc,
					textTransform: 'uppercase',
					letterSpacing: '0.1em',
					opacity: haut,
					transform: `translateY(${(1 - haut) * 20}px)`,
					textShadow: '0 4px 20px rgba(0,0,0,.7)',
				}}
			>
				Tu ne vas
			</div>
			<div style={{height: 250, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
				<Tampon t={t} a={d(62) - 0.04} taille={200} fond="rgba(244,239,228,.94)" incline={-6}>
					Jamais
				</Tampon>
			</div>
			<div
				style={{
					fontFamily: TITRE,
					fontWeight: 900,
					fontSize: 130,
					lineHeight: 1,
					color: C.blanc,
					textTransform: 'uppercase',
					opacity: Math.min(1, bas * 2),
					transform: `translateY(${(1 - bas) * 40}px)`,
					textShadow: '0 8px 30px rgba(0,0,0,.6)',
				}}
			>
				réussir
			</div>
		</div>
	);
};

/* ───────────────────────── L'AVANCE ───────────────────────── */

export const Avance: React.FC<{t: number}> = ({t}) => {
	const a = d(64) - 0.1;
	const b = d(87) - 0.15;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const X0 = 250;
	const vitesse = 118;
	const arret = d(82) + 0.1;
	const tt = Math.min(t, arret);
	const lui = Math.max(0, Math.min(560, (tt - d(69)) * vitesse));
	const toi = Math.max(0, Math.min(560, (tt - d(76)) * vitesse));
	const cote = p(t, d(82), d(82) + 0.5);

	const couloir = (y: number, long: number, couleur: string, depart: number) => (
		<>
			<Trait d={`M${X0} ${y} L${X0 + 560} ${y}`} v={p(t, a + 0.3, a + 0.8)} couleur="rgba(28,43,75,.18)" epaisseur={4} />
			{long > 0 ? <Trait d={`M${X0} ${y} L${X0 + long} ${y}`} v={1} couleur={couleur} epaisseur={10} /> : null}
			<circle cx={X0 + long} cy={y} r={t >= depart ? 17 : 0} fill={couleur} stroke={C.papier} strokeWidth={5} />
		</>
	);

	return (
		<Feuille {...CARTE} e={w.e} s={w.s}>
			<div style={{position: 'absolute', left: 40, top: 28}}>
				<Ecrit v={p(t, a + 0.2, a + 0.9)} taille={54}>
					La semaine qui démarre
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 40, top: 150, opacity: p(t, d(64), d(64) + 0.4)}}>
				<Ecrit v={p(t, d(64), d(66) + 0.2)} taille={44} couleur={C.vert}>
					a planifié
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 40, top: 270, opacity: p(t, d(76), d(76) + 0.3)}}>
				<Ecrit v={p(t, d(76), d(79))} taille={44}>
					toi
				</Ecrit>
			</div>
			<svg width={CARTE.l} height={CARTE.h} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				{couloir(175, lui, C.vert, d(69))}
				{couloir(295, toi, C.stylo, d(76))}
				{/* la cote : l'écart entre les deux, mesuré comme sur un plan */}
				{cote > 0 ? (
					<g opacity={cote}>
						<Trait d={`M${X0 + toi} 340 L${X0 + toi} 360 L${X0 + lui} 360 L${X0 + lui} 340`} v={cote} couleur={C.rouge} epaisseur={5} />
					</g>
				) : null}
			</svg>
			{cote > 0 ? (
				<div style={{position: 'absolute', right: Math.max(24, CARTE.l - (X0 + lui) - 10), top: 362, opacity: cote}}>
					<Surligne v={p(t, d(82) + 0.2, d(82) + 0.6)}>
						<Ecrit v={p(t, d(82) + 0.1, d(84) + 0.2)} taille={42} couleur={C.stylo}>
							une longueur d'avance
						</Ecrit>
					</Surligne>
				</div>
			) : null}
		</Feuille>
	);
};
