/**
 * LES SOUS-TITRES · mot à mot, à la place exacte des anciens (effacés).
 *
 * Signature : LE SURLIGNEUR. Le mot prononcé s'allume en jaune ; un mot-clé
 * reçoit en plus un coup de feutre derrière lui, qui reste jusqu'à la page
 * suivante, comme sur une feuille qu'on relit.
 *
 * Une page = 3 mots au plus, 20 signes au plus, et on coupe à chaque
 * ponctuation et à chaque souffle (> 0,35 s). Il parle d'une traite : ces
 * coupes sont la respiration que le montage n'a pas.
 */
import React from 'react';
import {interpolate} from 'remotion';
import {C, ZONE} from './donnees';
import {MOTS, type Mot} from './mots';
import {p, ressort} from './outils';
import {TEXTE} from './polices';

type Page = {mots: Mot[]; debut: number; fin: number};

const PAGES: Page[] = (() => {
	const pages: Page[] = [];
	let cour: Mot[] = [];
	const ferme = () => {
		if (cour.length) pages.push({mots: cour, debut: cour[0].s, fin: cour[cour.length - 1].e});
		cour = [];
	};
	MOTS.forEach((m, n) => {
		const prec = MOTS[n - 1];
		const signes = cour.reduce((a, x) => a + x.t.length + 1, 0) + m.t.length;
		if (cour.length && (cour.length >= 3 || signes > 20 || (prec && m.s - prec.e > 0.35))) ferme();
		cour.push(m);
		if (/[.,?!;:]$/.test(m.t)) ferme();
	});
	ferme();
	// une page reste affichée jusqu'à la suivante, sans déborder d'un long silence
	pages.forEach((pg, n) => {
		const suiv = pages[n + 1];
		pg.fin = suiv ? Math.min(suiv.debut, pg.fin + 0.7) : pg.fin + 0.7;
	});
	return pages;
})();

/** `masques` : les fenêtres où un graphique porte déjà la phrase, on n'écrit pas deux fois. */
export const SousTitres: React.FC<{t: number; masques: [number, number][]}> = ({t, masques}) => {
	if (masques.some(([a, b]) => t >= a && t < b)) return null;
	const pg = PAGES.find((x) => t >= x.debut - 0.06 && t < x.fin);
	if (!pg) return null;

	const r = ressort(t, pg.debut - 0.06, {damping: 16, stiffness: 320, mass: 0.5});
	return (
		<div
			style={{
				position: 'absolute',
				left: 40,
				right: 40,
				top: ZONE.sousTitres,
				transform: `translateY(-50%) translateY(${interpolate(r, [0, 1], [26, 0])}px) scale(${interpolate(r, [0, 1], [0.9, 1])})`,
				opacity: Math.min(1, r * 2),
				display: 'flex',
				justifyContent: 'center',
			}}
		>
			{/* halo sombre : lisibilité, et il couvre le peu de flou laissé par l'effacement */}
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: '50%',
					width: 900,
					height: 210,
					transform: 'translate(-50%,-50%)',
					background: 'radial-gradient(closest-side, rgba(10,12,18,.62), rgba(10,12,18,0))',
				}}
			/>
			<div
				style={{
					position: 'relative',
					display: 'flex',
					flexWrap: 'wrap',
					justifyContent: 'center',
					columnGap: 20,
					rowGap: 4,
					maxWidth: 940,
					fontFamily: TEXTE,
					fontWeight: 800,
					fontSize: 74,
					lineHeight: 1.12,
					letterSpacing: '-0.01em',
				}}
			>
				{pg.mots.map((m) => {
					const actif = t >= m.s - 0.03 && t < m.e + 0.05;
					const dit = t >= m.s - 0.03;
					const coup = m.k ? p(t, m.s - 0.03, m.s + 0.16) : 0;
					const saut = actif ? ressort(t, m.s - 0.03, {damping: 12, stiffness: 400, mass: 0.4}) : 0;
					return (
						<span
							key={m.i}
							style={{
								position: 'relative',
								display: 'inline-block',
								transform: `translateY(${-6 * saut}px) scale(${1 + 0.07 * saut})`,
							}}
						>
							{m.k ? (
								<span
									style={{
										position: 'absolute',
										left: -10,
										right: -10,
										top: '14%',
										bottom: '6%',
										background: C.surligneur,
										borderRadius: 8,
										transformOrigin: 'left center',
										transform: `scaleX(${coup}) skewX(-8deg) rotate(-1.5deg)`,
									}}
								/>
							) : null}
							<span
								style={{
									position: 'relative',
									color: m.k && coup > 0.5 ? C.encre : actif ? C.surligneur : C.blanc,
									opacity: dit || actif ? 1 : 0.92,
									textShadow: m.k && coup > 0.5 ? 'none' : '0 3px 0 rgba(0,0,0,.55), 0 6px 22px rgba(0,0,0,.55)',
								}}
							>
								{m.t}
							</span>
						</span>
					);
				})}
			</div>
		</div>
	);
};
