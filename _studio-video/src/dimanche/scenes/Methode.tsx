/**
 * CHAPITRE 4 · LA MÉTHODE (1:51 → 2:21) · la grande feuille, vidéo assombrie.
 *
 *  · LE PLAN DU WEEK-END   le graphique qu'on annote au stylo : la paire qu'on
 *                          entoure, la zone où l'on trade (verte), celle où l'on
 *                          ne trade pas (hachurée rouge), puis ce que je dois
 *                          faire / ne dois pas faire.
 *  · EXÉCUTER              « voici, voici, voici » : une coche par « voici », et
 *                          le tampon EXÉCUTER. Dans la semaine, on ne décide plus.
 *  · LA LOI UNIVERSELLE    deux courbes SCHÉMATIQUES (aucun axe, aucune valeur) :
 *                          l'improvisation en dents de scie, le plan régulier.
 *                          « perdre moins = gagner plus ».
 */
import React from 'react';
import {Easing} from 'remotion';
import {C, d, fi} from '../donnees';
import {Case, Ecrit, Etiquette, Feuille, Surligne, Tampon, Trait, fenetre, p, ressort} from '../outils';
import {TITRE} from '../polices';

const GRANDE = {x: 64, y: 720, l: 876, h: 880};

/* ───────────────────────── LE PLAN DU WEEK-END ───────────────────────── */

const OUV = [450, 420, 380, 330, 280, 250, 290, 340, 400, 450, 470, 430, 370, 310, 260, 240];
const CLO = [420, 380, 330, 280, 250, 290, 340, 400, 450, 470, 430, 370, 310, 260, 240, 280];
const PAS = 796 / OUV.length;

export const PlanWeekend: React.FC<{t: number}> = ({t}) => {
	const a = d(435) - 0.15;
	const b = d(511) - 0.15;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const entoure = p(t, d(465), d(465) + 0.6, Easing.linear);
	const vert = p(t, d(468), d(468) + 0.6, Easing.linear);
	const rouge = p(t, d(473), d(473) + 0.6, Easing.linear);
	const voici = [d(501), d(502), d(503)];

	return (
		<Feuille {...GRANDE} e={w.e} s={w.s} incline={-0.8}>
			<div style={{position: 'absolute', left: 40, top: 34}}>
				<Ecrit v={p(t, a + 0.25, d(440))} taille={58}>
					Mon plan du week-end
				</Ecrit>
			</div>
			<div style={{position: 'absolute', right: 34, top: 26}}>
				<Tampon t={t} a={d(438) - 0.05} taille={50} couleur={C.stylo} incline={7}>
					Week-end
				</Tampon>
			</div>

			<svg width={GRANDE.l} height={GRANDE.h} style={{position: 'absolute', left: 0, top: 0}}>
				<defs>
					<pattern id="hachures" width={18} height={18} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
						<line x1={0} y1={0} x2={0} y2={18} stroke={C.rouge} strokeWidth={5} opacity={0.5} />
					</pattern>
				</defs>
				{/* où je ne trade pas : le milieu, là où ça hésite */}
				{rouge > 0 ? (
					<g>
						<rect x={40} y={318} width={796 * rouge} height={70} fill="url(#hachures)" />
						<Trait d="M40 318 H836 M40 388 H836" v={rouge} couleur={C.rouge} epaisseur={4} />
					</g>
				) : null}
				{/* où je trade : le bas de la fourchette */}
				{vert > 0 ? (
					<g>
						<rect x={440} y={432} width={396 * vert} height={62} rx={8} fill="rgba(24,168,100,.18)" />
						<Trait d="M448 432 H828 Q836 432 836 440 V486 Q836 494 828 494 H448 Q440 494 440 486 V440 Q440 432 448 432" v={vert} couleur={C.vert} epaisseur={5} />
					</g>
				) : null}
				{OUV.map((o, i) => (
					<g key={i}>
						<line
							x1={40 + (i + 0.5) * PAS}
							x2={40 + (i + 0.5) * PAS}
							y1={Math.min(o, CLO[i]) - 20}
							y2={Math.max(o, CLO[i]) + 20}
							stroke={C.stylo}
							strokeWidth={4}
							opacity={p(t, d(442) + i * 0.06, d(442) + 0.3 + i * 0.06)}
						/>
						<rect
							x={40 + (i + 0.5) * PAS - 13}
							y={Math.min(o, CLO[i])}
							width={26}
							height={Math.abs(o - CLO[i])}
							rx={3}
							fill={CLO[i] < o ? C.vert : C.rouge}
							stroke={C.stylo}
							strokeWidth={3}
							opacity={p(t, d(442) + i * 0.06, d(442) + 0.3 + i * 0.06)}
						/>
					</g>
				))}
				{/* « cette paire-là » : on l'entoure */}
				<Trait d="M40 170 C40 128 250 124 262 164 C272 204 60 212 44 176" v={entoure} couleur={C.rouge} epaisseur={5} />
			</svg>
			<div
				style={{
					position: 'absolute',
					left: 60,
					top: 146,
					padding: '6px 22px',
					borderRadius: 30,
					border: `3px solid ${C.stylo}`,
					background: 'rgba(255,255,255,.6)',
					opacity: p(t, d(443), d(443) + 0.3),
				}}
			>
				<Etiquette taille={26}>Paire 1</Etiquette>
			</div>
			{rouge > 0.3 ? (
				<div style={{position: 'absolute', left: 60, top: 334, display: 'flex', alignItems: 'center', gap: 10, opacity: p(rouge, 0.3, 1)}}>
					<Etiquette taille={28} couleur={C.rouge} style={{background: C.papier, padding: '4px 12px', borderRadius: 8}}>
						× Pas ici
					</Etiquette>
				</div>
			) : null}
			{vert > 0.3 ? (
				<div style={{position: 'absolute', left: 460, top: 446, display: 'flex', alignItems: 'center', gap: 12, opacity: p(vert, 0.3, 1)}}>
					<Etiquette taille={28} couleur={C.vert} style={{background: C.papier, padding: '4px 12px', borderRadius: 8}}>
						Je trade ici
					</Etiquette>
					{t >= voici[2] ? (
						<svg width={36} height={36} viewBox="0 0 60 60">
							<Trait d="M10 31 L25 45 L52 10" v={p(t, voici[2], voici[2] + 0.25, Easing.linear)} couleur={C.vert} epaisseur={9} />
						</svg>
					) : null}
				</div>
			) : null}

			{/* ce que je dois faire / ne dois pas faire : cochés à chaque « voici » */}
			{[
				['ce que je dois faire', d(480), voici[0]],
				['ce que je ne dois pas faire', d(486), voici[1]],
			].map(([texte, quand, coche], n) => {
				const e = p(t, (quand as number) - 0.1, (quand as number) + 0.3);
				return (
					<div key={n} style={{position: 'absolute', left: 44, top: 574 + n * 104, display: 'flex', alignItems: 'center', gap: 24, opacity: e}}>
						<Case v={p(t, (quand as number) - 0.1, (quand as number) + 0.35, Easing.linear)} coche={p(t, coche as number, (coche as number) + 0.3, Easing.linear)} taille={66} />
						<Ecrit v={p(t, quand as number, (quand as number) + 1.0)} taille={56}>
							{texte as string}
						</Ecrit>
					</div>
				);
			})}
			<div style={{position: 'absolute', right: 40, bottom: 34}}>
				<Tampon t={t} a={d(509) - 0.05} taille={92} couleur={C.vert} incline={-7}>
					Exécuter
				</Tampon>
			</div>
		</Feuille>
	);
};

/* ───────────────────────── LA LOI UNIVERSELLE ───────────────────────── */

/** Catmull-Rom → Bézier : une courbe qui passe par les points, sans cassure. */
const lisse = (pts: [number, number][]) =>
	pts
		.map(([x, y], i) => {
			if (i === 0) return `M${x} ${y}`;
			const p0 = pts[i - 2] ?? pts[i - 1];
			const p1 = pts[i - 1];
			const p3 = pts[i + 1] ?? [x, y];
			const c1 = [p1[0] + (x - p0[0]) / 6, p1[1] + (y - p0[1]) / 6];
			const c2 = [x - (p3[0] - p1[0]) / 6, y - (p3[1] - p1[1]) / 6];
			return `C${c1[0]} ${c1[1]} ${c2[0]} ${c2[1]} ${x} ${y}`;
		})
		.join(' ');

const IMPROVISE: [number, number][] = [
	[60, 360], [120, 300], [170, 410], [230, 330], [290, 450], [350, 380], [410, 490],
	[470, 420], [530, 520], [590, 460], [650, 540], [710, 490], [770, 560], [816, 540],
];
const PLANIFIE: [number, number][] = [[60, 360], [160, 340], [260, 352], [360, 312], [460, 322], [560, 282], [660, 292], [760, 246], [816, 232]];

export const Loi: React.FC<{t: number}> = ({t}) => {
	const a = d(511) - 0.1;
	const b = d(566) - 0.2;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;

	const cheminImpro = IMPROVISE.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join(' ');
	const titre = p(t, d(564) - 0.1, d(564) + 0.5);

	return (
		<Feuille {...GRANDE} e={w.e} s={w.s} incline={0.8}>
			<div style={{position: 'absolute', left: 40, top: 34}}>
				<Ecrit v={p(t, d(511), fi(516))} taille={58}>
					À la fin de la semaine…
				</Ecrit>
			</div>
			<svg width={GRANDE.l} height={GRANDE.h} style={{position: 'absolute', left: 0, top: 0}}>
				<line x1={40} x2={836} y1={360} y2={360} stroke="rgba(28,43,75,.35)" strokeWidth={3} strokeDasharray="10 12" opacity={p(t, a + 0.3, a + 0.6)} />
				<Trait d={cheminImpro} v={p(t, d(522), d(529) + 0.2, Easing.linear)} couleur={C.rouge} epaisseur={7} />
				<Trait d={lisse(PLANIFIE)} v={p(t, d(529), d(537), Easing.linear)} couleur={C.vert} epaisseur={9} />
			</svg>
			<div style={{position: 'absolute', left: 560, top: 572}}>
				<Ecrit v={p(t, d(538), d(545))} taille={48} couleur={C.rouge}>
					en improvisant
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 560, top: 170}}>
				<Ecrit v={p(t, d(533), d(537))} taille={48} couleur={C.vert}>
					avec un plan
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 44, top: 650, display: 'flex', alignItems: 'center', gap: 22}}>
				<Ecrit v={p(t, d(553) - 0.1, fi(554))} taille={60}>
					perdre moins
				</Ecrit>
				{t >= d(559) - 0.2 ? (
					<Surligne v={p(t, d(559), d(559) + 0.3)}>
						<Ecrit v={p(t, d(559) - 0.2, fi(560))} taille={60}>
							= gagner plus
						</Ecrit>
					</Surligne>
				) : null}
			</div>
			{/* le titre gravé, entre deux filets */}
			<div style={{position: 'absolute', left: 40, right: 40, top: 748, textAlign: 'center', opacity: Math.min(1, titre * 3)}}>
				<div style={{height: 4, background: C.stylo, transformOrigin: 'center', transform: `scaleX(${titre})`}} />
				<div style={{display: 'flex', justifyContent: 'center', margin: '8px 0'}}>
					{'LOI UNIVERSELLE'.split('').map((l, i) => {
						const r = ressort(t, d(564) - 0.1 + i * 0.025, {damping: 14, stiffness: 260});
						return (
							<span
								key={i}
								style={{
									fontFamily: TITRE,
									fontWeight: 900,
									fontSize: 92,
									lineHeight: 1,
									color: C.stylo,
									whiteSpace: 'pre',
									display: 'inline-block',
									opacity: Math.min(1, r * 2),
									transform: `translateY(${(1 - r) * 30}px)`,
								}}
							>
								{l}
							</span>
						);
					})}
				</div>
				<div style={{height: 4, background: C.stylo, transformOrigin: 'center', transform: `scaleX(${titre})`}} />
			</div>
		</Feuille>
	);
};
