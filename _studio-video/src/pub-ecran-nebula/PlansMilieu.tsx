/**
 * Le cœur de la pub :
 *  6-7 · le moment fort : le halo s'ouvre en plein écran violet ; « Retiens bien ça », puis la phrase-clé en GÉANT,
 *        deux mots à la fois au rythme de la voix, et « TOUT DE SUITE » en blanc, avec un souffle ;
 *  8   · le téléphone, et dedans le VRAI catalogue d'un client livré (aubraisedor.com) ; sur « faut la mettre », on
 *        entre dans sa vraie photo du haut (la sauce krinkrin, son prix, « Ajouter au panier ») ;
 *  9   · trois produits dessinés sortent du téléphone, leurs prix s'allument, puis ils deviennent un seul lien ;
 *  10  · il choisit la robe, il appuie sur « Commander » (le doigt, l'onde).
 * ⚠️ Taille : chaque élément occupe 55 à 65 % de la hauteur (la version TikTok le montre à moitié de sa taille).
 */
import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, francs, ligne, Mot, plan, Produit, PRODUITS, quand} from './donnees';
import {BarreEtat, Cadenas, Coche, Dessin, Lien} from './Dessins';
import {entreeSortie, ENTREE_DOUCE, lin, motQuiArrive, Pose, TEXTE, TYPO, VA_ET_VIENT} from './outils';
import {ECRAN_TEL, Telephone} from './Telephone';

const normal = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');

/* ─────────────────────────── 6-7 · le moment fort ─────────────────────────── */

/** La phrase-clé coupée en coups de deux mots au plus (on coupe aussi à la virgule), pour la dire en géant. */
const coups = (mots: Mot[]): Mot[][] => {
	const out: Mot[][] = [];
	let courant: Mot[] = [];
	for (const w of mots) {
		courant.push(w);
		if (courant.length === 2 || /[,.:;]$/.test(w.m)) {
			out.push(courant);
			courant = [];
		}
	}
	if (courant.length) out.push(courant);
	return out;
};

const sansPonctuation = (m: string) => m.replace(/[\s ]*[,.:;!?…]+$/, '');

export const Retiens: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('retiens');
	if (t < a - 0.05 || t > b + 0.4) return null;
	const ouvre = lin(t, a, a + 0.5, 0, 1, VA_ET_VIENT);
	// le violet se referme AVANT que le téléphone du plan 8 arrive : deux éléments ne se croisent jamais (vu le 21/11,
	// le cercle qui se refermait passait sur le téléphone pendant 0,25 s)
	const ferme = lin(t, b - 0.25, b + 0.08, 0, 1, VA_ET_VIENT);
	const rayon = 1250 * ouvre * (1 - ferme);

	const l7 = ligne(7).mots;
	const iSuite = l7.findIndex((w, i) => i > 0 && normal(w.m) === 'tout' && normal(l7[i - 1].m) === 'tout');
	const coupe = iSuite > 0 ? iSuite : l7.length - 3;
	const lesCoups = coups(l7.slice(0, coupe));
	const toutDeSuite = l7.slice(coupe);
	const tSuite = toutDeSuite[0].a;

	const sortie6 = lin(t, ligne(7).debut - 0.14, ligne(7).debut + 0.04, 0, 1, ENTREE_DOUCE);
	// le coup affiché : celui dont le premier mot a commencé
	let k = -1;
	lesCoups.forEach((c, i) => {
		if (t >= c[0].a - 0.06) k = i;
	});
	const coup = k >= 0 && t < tSuite - 0.06 ? lesCoups[k] : null;

	return (
		<div style={{position: 'absolute', inset: 0, background: C.violet, clipPath: `circle(${rayon.toFixed(1)}px at 960px 560px)`}}>
			{sortie6 < 1 ? (
				<Pose x={960} y={540} style={{opacity: 1 - sortie6, transform: `translateY(${(-40 * sortie6).toFixed(1)}px)`}}>
					<div style={{display: 'flex', columnGap: '0.22em', fontFamily: TEXTE, fontWeight: 800, fontSize: 220, letterSpacing: '-0.045em', color: C.nuit, whiteSpace: 'nowrap', lineHeight: 1}}>
						{ligne(6).mots.map((w, i) => (
							<span key={i} style={{display: 'inline-block', whiteSpace: 'pre', ...motQuiArrive(t, w.a)}}>
								{w.m}
							</span>
						))}
					</div>
				</Pose>
			) : null}
			{coup ? (
				<Pose x={960} y={545}>
					<div style={{display: 'flex', columnGap: '0.2em', fontFamily: TEXTE, fontWeight: 900, fontSize: 250, letterSpacing: '-0.05em', color: C.nuit, whiteSpace: 'nowrap', lineHeight: 1}}>
						{coup.map((w, i) => {
							const p = lin(t, w.a - 0.06, w.a + 0.14);
							return (
								<span key={`${k}-${i}`} style={{display: 'inline-block', opacity: p, transform: `scale(${(1.16 - 0.16 * p).toFixed(4)})`, filter: p < 0.99 ? `blur(${((1 - p) * 10).toFixed(2)}px)` : undefined}}>
									{sansPonctuation(w.m)}
								</span>
							);
						})}
					</div>
				</Pose>
			) : null}
			{t > tSuite - 0.2 ? (
				<Pose x={960} y={545}>
					<div style={{display: 'flex', columnGap: '0.2em', fontFamily: TEXTE, fontWeight: 900, fontSize: 224, letterSpacing: '-0.045em', color: C.blanc, whiteSpace: 'nowrap', lineHeight: 1, textShadow: '0 10px 60px rgba(40,0,80,0.35)'}}>
						{toutDeSuite.map((w, i) => {
							const p = lin(t, w.a - 0.06, w.a + 0.16);
							return (
								<span key={i} style={{display: 'inline-block', opacity: p, transform: `scale(${(1.18 - 0.18 * p).toFixed(4)})`, filter: p < 0.99 ? `blur(${((1 - p) * 10).toFixed(2)}px)` : undefined}}>
									{sansPonctuation(w.m).toUpperCase()}
								</span>
							);
						})}
					</div>
				</Pose>
			) : null}
		</div>
	);
};

/* ─────────────────────────── 8 · le vrai catalogue dans le téléphone ─────────────────────────── */

/**
 * La capture de https://aubraisedor.com (390 px de large, x2) : 780 x 6800.
 * ⛔ POLARIS, 21/11 : plus bas que le premier écran, la grille des plats (poulet bicyclette, tilapia, poulet chair,
 *    aileron…) est faite des photos GÉNÉRÉES de juillet. Une pub ne les montre jamais, pas même un instant : on ne
 *    défile pas, on entre dans la VRAIE photo du haut (la sauce krinkrin, 1 500 F, « Ajouter au panier »), et l'image
 *    est coupée au-dessus de la barre du bas (`coupe`), donc aucune photo de la grille ne peut paraître.
 * ⚠️ Le carrousel des sauces montre les trois vraies photos envoyées par la maison (gombo, krinkrin, feuille) ; la
 *    quatrième, coupée au bord droit, n'en est pas : elle est recouverte du fond de la page (`vignetteCachee`).
 * Mongazi a l'accord d'Au Braisé d'Or pour paraître dans la pub (21/11).
 */
const CAPTURE = {l: 780, coupe: 1530, fond: 'rgb(226,221,215)', vignetteCachee: {x: 668, y: 1328, l: 112, h: 176}};

export const Boutique: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('boutique');
	const es = entreeSortie(t, a + 0.1, b); // il attend que le violet du plan d'avant soit refermé
	if (!es.visible) return null;
	const echelle = ECRAN_TEL.l / CAPTURE.l;
	const haut = 84;
	// « faut la mettre » : on entre dans l'écran, jusqu'à la vraie photo, son prix et « Ajouter au panier »
	const tFaut = quand(8, 'faut');
	const entre = lin(t, tFaut - 0.6, b - 0.05, 0, 1, VA_ET_VIENT);
	const chute = lin(t, b - 0.15, b + 0.3, 0, 1, ENTREE_DOUCE);
	const v = CAPTURE.vignetteCachee;
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={960} y={545 + 110 * chute} style={{transform: `scale(${(1.2 + 0.72 * entre).toFixed(4)})`, transformOrigin: '50% 56%'}}>
				<Telephone fond={CAPTURE.fond}>
					<div style={{position: 'absolute', left: 0, top: haut, width: ECRAN_TEL.l, height: ECRAN_TEL.h - haut, overflow: 'hidden', background: CAPTURE.fond}}>
						<div style={{position: 'absolute', left: 0, top: 0, width: ECRAN_TEL.l, height: CAPTURE.coupe * echelle, overflow: 'hidden'}}>
							<Img src={staticFile('pub-ecran-nebula/braise-tel-long.jpg')} style={{position: 'absolute', left: 0, top: 0, width: ECRAN_TEL.l}} />
							<div style={{position: 'absolute', left: v.x * echelle, top: v.y * echelle, width: v.l * echelle, height: v.h * echelle, background: `linear-gradient(90deg, rgba(226,221,215,0) 0px, ${CAPTURE.fond} 7px)`}} />
						</div>
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: haut, background: '#f3eee5'}}>
						<BarreEtat heure="00:13" couleur="#1f1b16" police={TEXTE} />
						<div style={{position: 'absolute', left: 14, right: 14, top: 44, height: 32, borderRadius: 16, background: '#e4ddd1', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontFamily: TEXTE, fontWeight: 600, fontSize: 15, color: '#3b352c'}}>
							<Cadenas taille={13} couleur="#5b5346" />
							aubraisedor.com
						</div>
					</div>
				</Telephone>
			</Pose>
		</div>
	);
};

/* ─────────────────────────── 9 · les produits, leurs prix, un seul lien ─────────────────────────── */

const Carte: React.FC<{produit: Produit; prixAllume: number; largeur?: number; selection?: number; hauteur?: number}> = ({
	produit,
	prixAllume,
	largeur = 300,
	selection = 0,
	hauteur = 400,
}) => {
	const p = PRODUITS[produit];
	const k = largeur / 300;
	return (
		<div
			style={{
				width: largeur,
				height: hauteur * k,
				borderRadius: 30 * k,
				background: C.carte,
				boxShadow: `0 30px 80px rgba(0,0,0,0.5), inset 0 0 0 ${(1.5 + 1.5 * selection).toFixed(2)}px ${selection > 0.01 ? `rgba(34,211,238,${(0.09 + 0.91 * selection).toFixed(3)})` : C.carteBord}`,
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'center',
				paddingTop: 30 * k,
				fontFamily: TEXTE,
				color: C.blanc,
				position: 'relative',
			}}
		>
			<Dessin produit={produit} taille={150 * k} epaisseur={3.4} />
			<div style={{fontWeight: 600, fontSize: 30 * k, marginTop: 14 * k, letterSpacing: '-0.01em'}}>{p.nom}</div>
			<div style={{fontWeight: 800, fontSize: 36 * k, marginTop: 4 * k, letterSpacing: '-0.02em', color: prixAllume > 0.5 ? C.cyan : 'rgba(245,243,255,0.45)', transform: `scale(${(1 + 0.12 * Math.sin(Math.PI * prixAllume)).toFixed(4)})`}}>
				{francs(p.prix)}
			</div>
		</div>
	);
};

const RANG: Produit[] = ['sac', 'robe', 'parfum'];

export const Produits: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('produits');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const t9 = ligne(9).debut;
	const tPrix = quand(9, 'prix');
	const tUn = quand(9, 'un');
	const tLien = quand(9, 'lien');
	const pilule = lin(t, tUn + 0.05, tUn + 0.45);
	const eclat = lin(t, tLien - 0.05, tLien + 0.75, 0, 1, VA_ET_VIENT);
	return (
		<div style={{position: 'absolute', inset: 0, opacity: es.style.opacity}}>
			{RANG.map((produit, k) => {
				const sort = lin(t, t9 - 0.1 + k * 0.13, t9 + 0.45 + k * 0.13, 0, 1, (x) => 1 - Math.pow(1 - x, 3));
				const rentre = lin(t, tUn - 0.12 + (2 - k) * 0.05, tUn + 0.3 + (2 - k) * 0.05, 0, 1, ENTREE_DOUCE);
				const x = 960 + (420 + 540 * k - 960) * sort * (1 - rentre);
				const y = 680 + (545 - 680) * sort + 20 * rentre;
				const s = (0.45 + 0.55 * sort) * (1 - 0.75 * rentre);
				const prix = lin(t, tPrix - 0.05 + k * 0.1, tPrix + 0.2 + k * 0.1);
				if (sort <= 0) return null;
				return (
					<Pose key={produit} x={x} y={y} style={{opacity: Math.min(1, sort * 1.6) * (1 - rentre), transform: `scale(${s.toFixed(4)})`, filter: sort < 0.98 || rentre > 0.02 ? `blur(${((1 - sort) * 8 + rentre * 6).toFixed(2)}px)` : undefined}}>
						<Carte produit={produit} prixAllume={prix} largeur={480} hauteur={360} />
					</Pose>
				);
			})}
			{pilule > 0 ? (
				<Pose x={960} y={545} style={{opacity: pilule, transform: `scale(${(1.55 * (0.92 + 0.08 * pilule)).toFixed(4)})`, filter: pilule < 0.99 ? `blur(${((1 - pilule) * 8).toFixed(2)}px)` : undefined}}>
					<div style={{position: 'relative', display: 'flex', alignItems: 'center', gap: 26, padding: '22px 46px 22px 22px', borderRadius: 80, background: '#15131f', boxShadow: '0 30px 90px rgba(0,0,0,0.55), inset 0 0 0 1.5px rgba(34,211,238,0.45)', overflow: 'hidden'}}>
						<div style={{width: 92, height: 92, borderRadius: 46, background: C.cyan, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
							<Lien taille={48} />
						</div>
						<div style={{...TYPO, fontSize: 60, textDecoration: 'underline', textDecorationColor: C.cyan, textDecorationThickness: 4, textUnderlineOffset: 12}}>ta boutique</div>
						{eclat > 0 && eclat < 1 ? (
							<div
								style={{
									position: 'absolute',
									top: -20,
									bottom: -20,
									width: 160,
									left: -200 + 900 * eclat,
									background: 'linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.28) 50%, rgba(255,255,255,0) 100%)',
									transform: 'skewX(-18deg)',
								}}
							/>
						) : null}
					</div>
				</Pose>
			) : null}
		</div>
	);
};

/* ─────────────────────────── 10 · il choisit, il appuie ─────────────────────────── */

export const Appuie: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('appuie');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const tChoisit = quand(10, 'choisit');
	const tAppuie = quand(10, 'appuie');
	const sel = lin(t, tChoisit - 0.05, tChoisit + 0.25);
	const doigt = lin(t, tAppuie - 0.2, tAppuie - 0.02);
	const enfonce = Math.sin(Math.PI * lin(t, tAppuie - 0.02, tAppuie + 0.2, 0, 1, (x) => x));
	const onde = lin(t, tAppuie, tAppuie + 0.55, 0, 1, (x) => 1 - Math.pow(1 - x, 2));
	const leve = lin(t, tAppuie + 0.25, tAppuie + 0.5);
	const L = 480;
	const bouton = {cote: 0.1 * L, bas: 0.09 * L, h: 0.21 * L};
	const rond = bouton.h * 1.05;
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={960} y={545} style={{transform: `translateY(${(-12 * sel).toFixed(2)}px) scale(${(1 + 0.02 * sel).toFixed(4)})`}}>
				<div style={{position: 'relative'}}>
					<Carte produit="robe" prixAllume={1} largeur={L} selection={sel} hauteur={440} />
					{/* le bouton, au pied de la carte */}
					<div style={{position: 'absolute', left: bouton.cote, right: bouton.cote, bottom: bouton.bas, height: bouton.h, borderRadius: bouton.h / 2, background: C.cyan, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TEXTE, fontWeight: 800, fontSize: 0.1 * L, color: C.nuit, transform: `scale(${(1 - 0.05 * enfonce).toFixed(4)})`}}>
						Commander
					</div>
					{/* la coche de la sélection */}
					<div style={{position: 'absolute', top: -22, right: -22, width: 68, height: 68, borderRadius: 34, background: C.cyan, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: sel, transform: `scale(${(0.4 + 0.6 * sel).toFixed(4)})`, boxShadow: '0 8px 24px rgba(34,211,238,0.35)'}}>
						<Coche taille={36} />
					</div>
					{/* le doigt : le rond clair d'un toucher, puis l'onde */}
					<div style={{position: 'absolute', left: L / 2 - rond / 2, bottom: bouton.bas + bouton.h / 2 - rond / 2, width: rond, height: rond}}>
						{onde > 0 && onde < 1 ? (
							<div style={{position: 'absolute', left: rond / 2 - 30 - 200 * onde, top: rond / 2 - 30 - 200 * onde, width: 60 + 400 * onde, height: 60 + 400 * onde, borderRadius: '50%', border: `4px solid rgba(245,243,255,${(0.7 * (1 - onde)).toFixed(3)})`}} />
						) : null}
						<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: 'rgba(245,243,255,0.55)', boxShadow: '0 0 30px rgba(245,243,255,0.35)', opacity: doigt * (1 - leve), transform: `scale(${(1.35 - 0.35 * doigt - 0.12 * enfonce).toFixed(4)})`}} />
					</div>
				</div>
			</Pose>
		</div>
	);
};
