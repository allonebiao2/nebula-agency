/**
 * LE LOGO QUI S'ÉCRIT : SON logo, dans ses vrais contours (`couches.ts`, tiré de son
 * fichier vectoriel), animé couche par couche. Rien n'est redessiné.
 *
 * L'ordre suit le geste d'une esthéticienne qui maquille un œil, puis la signature :
 *   0,00  le SOURCIL, d'un coup de pinceau, le long de sa ligne médiane (squelette) ;
 *   0,30  l'EYELINER file de gauche à droite ;
 *   0,85  l'ŒIL S'OUVRE : la paupière basse descend depuis la ligne des cils, avec
 *         un léger rebond, et un reflet s'allume dans la pupille ;
 *   1,10  le G calligraphié, au pinceau ; puis « rain d'esthétique » monte lettre
 *         à lettre ;
 *   2,35  LE GRAIN tombe : le point rond du « i » de « rain », le grain du nom.
 *         Il s'écrase, rebondit, et lâche une onde et un éclat ;
 *   3,00  « Institut de beauté » se resserre (l'interlettrage se referme) ;
 *   3,80  un reflet de lumière traverse tout le logo.
 * Durée : `DUREE_LOGO` secondes. `oeilSeul` : seulement le sourcil et l'œil (l'accroche).
 */
import React from 'react';
import {Easing} from 'remotion';
import {LOGO} from './couches';
import {CHUTE, GLISSE, mix, p, ressort} from './outils';

export const DUREE_LOGO = 4.7;

/** La pupille, en unités du logo (relevée sur la boîte de l'iris). */
const [IX0, IY0, IX1, IY1] = LOGO.oeil.iris;
export const PUPILLE = {x: (IX0 + IX1) / 2, y: IY0 + (IY1 - IY0) * 0.3, r: (IX1 - IX0) * 0.2};

const [OX0, OY0, OX1, OY1] = LOGO.oeil.boite;
const CILS = LOGO.oeil.cils + 22;

export const Logo: React.FC<{
	t: number;
	debut: number;
	largeur: number;
	oeilSeul?: boolean;
	id?: string;
	style?: React.CSSProperties;
}> = ({t, debut, largeur, oeilSeul = false, id = 'lg', style}) => {
	const u = t - debut;
	if (u < -0.05) return null;
	const W = LOGO.largeur;
	const H = LOGO.hauteur;

	// 1. le sourcil
	const eSourcil = p(u, 0, 0.8, GLISSE);
	// 2-3. l'eyeliner, puis l'ouverture (ressort : la paupière rebondit un peu)
	const eLiner = p(u, 0.3, 1.0, GLISSE);
	const eOuvre = u < 0.85 ? 0.02 : Math.max(0.02, ressort(t, debut + 0.85, {damping: 11, stiffness: 140, mass: 0.6}));
	const reflet = p(u, 1.15, 1.45) * (1 - 0.35 * p(u, 1.45, 2.2));
	// 4. le G et la première ligne
	const eG = p(u, 1.1, 2.0, GLISSE);
	const remplirG = p(u, 1.85, 2.15);
	// 5. le grain
	const T_IMPACT = 2.78;
	const chute = p(u, 2.35, T_IMPACT, CHUTE);
	const apres = u >= T_IMPACT;
	const k = apres ? ressort(t, debut + T_IMPACT, {damping: 7, stiffness: 260, mass: 0.55}) : 0;
	const ecrase = apres ? (1 - k) * 0.38 : 0;
	const [gx, gy] = LOGO.grain.centre;
	const R = LOGO.grain.rayon;
	const dyGrain = apres ? 0 : -1300 * (1 - chute);
	const sy = apres ? 1 - ecrase : 1 + 0.18 * chute;
	const sx = apres ? 1 + ecrase * 0.8 : 1 - 0.1 * chute;
	const onde = (d: number) => p(u, T_IMPACT + d, T_IMPACT + d + 0.85, Easing.out(Easing.cubic));
	const eclat = p(u, T_IMPACT, T_IMPACT + 0.12) * (1 - p(u, T_IMPACT + 0.12, T_IMPACT + 0.7));
	// 6. la deuxième ligne, puis le reflet
	const eLigne2 = (i: number) => p(u, 3.0 + i * 0.022, 3.6 + i * 0.022);
	const balayage = p(u, 3.8, 4.7, GLISSE);
	const xBal = mix(-600, W + 600, balayage);

	const or = `url(#${id}-or)`;
	const lignes2 = LOGO.ligne2;
	const cx2 = (lignes2[0].boite[0] + lignes2[lignes2.length - 1].boite[2]) / 2;

	const pinceau = (e: number, trace: string, ep: number, cle: string) => (
		<mask id={`${id}-${cle}`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
			{e > 0.002 ? (
				<path
					d={trace}
					stroke="white"
					strokeWidth={ep * 2.3}
					fill="none"
					strokeLinecap="round"
					strokeLinejoin="round"
					pathLength={1}
					strokeDasharray="1 1"
					strokeDashoffset={1 - e}
				/>
			) : null}
		</mask>
	);

	const toutLeLogo = (fill: string) => (
		<>
			<path d={LOGO.sourcil.d} fill={fill} fillRule="evenodd" />
			<path d={LOGO.oeil.d} fill={fill} fillRule="evenodd" />
			{oeilSeul ? null : (
				<>
					<path d={LOGO.g.d} fill={fill} fillRule="evenodd" />
					<path d={LOGO.grain.d} fill={fill} fillRule="evenodd" />
					{LOGO.ligne1.map((g, i) => (
						<path key={`a${i}`} d={g.d} fill={fill} fillRule="evenodd" />
					))}
					{LOGO.ligne2.map((g, i) => (
						<path key={`b${i}`} d={g.d} fill={fill} fillRule="evenodd" />
					))}
				</>
			)}
		</>
	);

	return (
		<svg width={largeur} height={(largeur * H) / W} viewBox={`0 0 ${W} ${H}`} style={{overflow: 'visible', ...style}}>
			<defs>
				<linearGradient id={`${id}-or`} x1="0" y1="0" x2="0.25" y2="1">
					<stop offset="0%" stopColor="#fff2cf" />
					<stop offset="30%" stopColor="#f0d49a" />
					<stop offset="60%" stopColor="#d4af72" />
					<stop offset="100%" stopColor="#a8803f" />
				</linearGradient>
				<linearGradient id={`${id}-bal`} gradientUnits="userSpaceOnUse" x1={xBal - 420} y1={0} x2={xBal + 420} y2={260}>
					<stop offset="0%" stopColor="#fffaf0" stopOpacity={0} />
					<stop offset="50%" stopColor="#fffaf0" stopOpacity={0.9} />
					<stop offset="100%" stopColor="#fffaf0" stopOpacity={0} />
				</linearGradient>
				<radialGradient id={`${id}-halo`}>
					<stop offset="0%" stopColor="#fff6dc" stopOpacity={1} />
					<stop offset="35%" stopColor="#f0d49a" stopOpacity={0.55} />
					<stop offset="100%" stopColor="#d4af72" stopOpacity={0} />
				</radialGradient>
				{pinceau(eSourcil, LOGO.sourcil.trace, LOGO.sourcil.epaisseur, 'ms')}
				{oeilSeul ? null : pinceau(eG, LOGO.g.trace, LOGO.g.epaisseur, 'mg')}
				<clipPath id={`${id}-haut`}>
					<rect x={OX0 - 10} y={OY0 - 10} width={(OX1 - OX0 + 20) * eLiner} height={CILS - OY0 + 10} />
				</clipPath>
				<clipPath id={`${id}-bas`}>
					<rect x={OX0 - 10} y={CILS} width={OX1 - OX0 + 20} height={OY1 - CILS + 10} />
				</clipPath>
			</defs>

			{/* 1. le sourcil, au pinceau */}
			<path d={LOGO.sourcil.d} fill={or} fillRule="evenodd" mask={`url(#${id}-ms)`} />

			{/* 2. l'eyeliner (le haut de l'œil), puis 3. l'ouverture (le bas, qui descend) */}
			<path d={LOGO.oeil.d} fill={or} fillRule="evenodd" clipPath={`url(#${id}-haut)`} />
			<g transform={`translate(0 ${CILS}) scale(1 ${eOuvre}) translate(0 ${-CILS})`}>
				<path d={LOGO.oeil.d} fill={or} fillRule="evenodd" clipPath={`url(#${id}-bas)`} />
			</g>
			{reflet > 0.01 ? (
				<>
					<circle cx={PUPILLE.x} cy={PUPILLE.y} r={PUPILLE.r * 3.2} fill={`url(#${id}-halo)`} opacity={0.35 * reflet} />
					<circle cx={PUPILLE.x + PUPILLE.r * 0.38} cy={PUPILLE.y - PUPILLE.r * 0.36} r={PUPILLE.r * 0.3} fill="#fffaf0" opacity={reflet} />
				</>
			) : null}

			{oeilSeul ? null : (
				<>
					{/* 4. le G au pinceau (le remplissage final couvre ce que le squelette n'atteint pas) */}
					<path d={LOGO.g.d} fill={or} fillRule="evenodd" mask={`url(#${id}-mg)`} />
					{remplirG > 0 ? <path d={LOGO.g.d} fill={or} fillRule="evenodd" opacity={remplirG} /> : null}
					{LOGO.ligne1.map((g, i) => {
						const e = ressort(t, debut + 1.6 + i * 0.045, {damping: 16, stiffness: 140, mass: 0.6});
						if (e <= 0.001) return null;
						return (
							<path
								key={i}
								d={g.d}
								fill={or}
								fillRule="evenodd"
								opacity={Math.min(1, e * 1.4)}
								transform={`translate(0 ${(1 - e) * 70})`}
							/>
						);
					})}

					{/* 5. LE GRAIN */}
					{u >= 2.35 ? (
						<>
							{[0, 0.14].map((d, i) => {
								const e = onde(d);
								return e > 0 && e < 1 ? (
									<circle key={i} cx={gx} cy={gy} r={R * (1.1 + 3.4 * e)} fill="none" stroke="#f0d49a" strokeWidth={10 * (1 - e)} opacity={0.9 * (1 - e)} />
								) : null;
							})}
							{eclat > 0.01 ? (
								<>
									<circle cx={gx} cy={gy} r={R * 4.2} fill={`url(#${id}-halo)`} opacity={0.85 * eclat} />
									<path
										d={`M${gx} ${gy - R * 3.4} L${gx + R * 0.22} ${gy} L${gx} ${gy + R * 3.4} L${gx - R * 0.22} ${gy} Z M${gx - R * 3.4} ${gy} L${gx} ${gy - R * 0.22} L${gx + R * 3.4} ${gy} L${gx} ${gy + R * 0.22} Z`}
										fill="#fffaf0"
										opacity={eclat}
										transform={`rotate(${15 * eclat} ${gx} ${gy})`}
									/>
								</>
							) : null}
							<g transform={`translate(${gx} ${gy + dyGrain}) scale(${sx} ${sy}) translate(${-gx} ${-gy})`}>
								<path d={LOGO.grain.d} fill={or} fillRule="evenodd" />
							</g>
						</>
					) : null}

					{/* 6. « Institut de beauté » : l'interlettrage se referme */}
					{lignes2.map((g, i) => {
						const e = eLigne2(i);
						if (e <= 0.001) return null;
						const gc = (g.boite[0] + g.boite[2]) / 2;
						return (
							<path key={i} d={g.d} fill={or} fillRule="evenodd" opacity={e} transform={`translate(${(gc - cx2) * 0.32 * (1 - e)} 0)`} />
						);
					})}
				</>
			)}

			{/* le reflet qui traverse le logo une fois qu'il est complet */}
			{balayage > 0 && balayage < 1 ? <g opacity={0.85}>{toutLeLogo(`url(#${id}-bal)`)}</g> : null}
		</svg>
	);
};
