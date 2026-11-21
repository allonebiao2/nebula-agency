/**
 * Les sous-titres mot à mot de la version TikTok, sous l'écran : blancs, gras, le mot dit en cyan, 2 à 4 mots par
 * ligne. Le texte est celui que Mongazi a DIT (`script.json`), calé par `minutage.json` : Deepgram entend
 * « Nebulla » et « prêt », l'écran écrit « NEBULA » et « prête ».
 */
import React from 'react';
import {C, M, Mot} from './donnees';
import {lin, TEXTE} from './outils';

type Bloc = {mots: Mot[]; a: number; b: number};

const FIN_DE_GROUPE = /[,.:;!?…»]$/;

/** Une ligne coupée en groupes : d'abord à la ponctuation, puis en morceaux de 4 mots au plus, équilibrés. */
const decouper = (mots: Mot[]): Mot[][] => {
	const groupes: Mot[][] = [];
	let courant: Mot[] = [];
	for (const w of mots) {
		courant.push(w);
		if (FIN_DE_GROUPE.test(w.m.trim())) {
			groupes.push(courant);
			courant = [];
		}
	}
	if (courant.length) groupes.push(courant);
	// un mot seul rejoint son voisin si l'ensemble tient en 4 mots
	const fusion: Mot[][] = [];
	for (const g of groupes) {
		const avant = fusion[fusion.length - 1];
		if (avant && (g.length === 1 || avant.length === 1) && avant.length + g.length <= 4) avant.push(...g);
		else fusion.push([...g]);
	}
	// au-delà de 4 mots, des morceaux égaux ; le surplus va aux DERNIERS (« juste en / un seul lien »)
	const out: Mot[][] = [];
	for (const g of fusion) {
		const n = Math.ceil(g.length / 4);
		const base = Math.floor(g.length / n);
		const surplus = g.length % n;
		let k = 0;
		for (let i = 0; i < n; i++) {
			const taille = base + (i >= n - surplus ? 1 : 0);
			out.push(g.slice(k, k + taille));
			k += taille;
		}
	}
	return out;
};

const BLOCS: Bloc[] = (() => {
	const blocs: Bloc[] = [];
	for (const l of M.lignes) for (const mots of decouper(l.mots)) blocs.push({mots, a: mots[0].a, b: mots[mots.length - 1].b});
	return blocs;
})();

/** Ce qui s'affiche : la ponctuation de fin de groupe (point, virgule, deux-points) tombe ; « ? », « … » et « » » restent. */
const propre = (m: string, dernier: boolean) => (dernier ? m.replace(/[\s ]*[.,:;]+$/, '') : m);

export const SousTitres: React.FC<{t: number; y: number; largeur: number}> = ({t, y, largeur}) => {
	let k = -1;
	for (let i = 0; i < BLOCS.length; i++) if (t >= BLOCS[i].a - 0.06) k = i;
	if (k < 0) return null;
	const bloc = BLOCS[k];
	const suivant = BLOCS[k + 1];
	// dans un long silence, le groupe s'en va 0,6 s après son dernier mot
	const fin = suivant ? Math.min(suivant.a - 0.06, bloc.b + 0.6) : bloc.b + 1.2;
	if (t > fin + 0.12) return null;
	const entre = lin(t, bloc.a - 0.06, bloc.a + 0.06);
	const sort = lin(t, fin, fin + 0.12);
	let enCours = 0;
	bloc.mots.forEach((w, i) => {
		if (t >= w.a - 0.02) enCours = i;
	});
	return (
		<div
			style={{
				position: 'absolute',
				left: (1080 - largeur) / 2,
				width: largeur,
				top: y,
				display: 'flex',
				flexWrap: 'wrap',
				justifyContent: 'center',
				columnGap: '0.26em',
				fontFamily: TEXTE,
				fontWeight: 800,
				fontSize: 58,
				lineHeight: 1.12,
				letterSpacing: '-0.01em',
				color: C.blanc,
				textShadow: '0 3px 0 rgba(0,0,0,0.55), 0 0 22px rgba(0,0,0,0.85), 0 0 4px rgba(0,0,0,0.9)',
				opacity: entre * (1 - sort),
				transform: `translateY(-50%) scale(${(0.94 + 0.06 * entre).toFixed(4)})`,
			}}
		>
			{bloc.mots.map((w, i) => (
				<span key={i} style={{display: 'inline-block', whiteSpace: 'pre', color: i === enCours ? C.cyan : C.blanc}}>
					{propre(w.m, i === bloc.mots.length - 1)}
				</span>
			))}
		</div>
	);
};

/** Pour le contrôle : les groupes tels qu'ils s'affichent. */
export const GROUPES = BLOCS.map((b) => b.mots.map((w, i) => propre(w.m, i === b.mots.length - 1)).join(' '));
