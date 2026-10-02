/**
 * 2 · LES TROIS TOURS : un seul téléphone, qui ne quitte jamais sa place.
 *
 *  · VITRINE : la poussière dessine son contour, puis un plan d'architecte trace
 *    un site dans l'écran ; le VRAI site d'Angy Art s'y révèle. « …et vous devenez
 *    une marque » : quatre autres vitrines livrées s'ouvrent en éventail derrière.
 *  · CATALOGUE : le téléphone pivote sur le catalogue d'Au Braisé d'Or ; les vrais
 *    produits (champagnes de Weinkeller, robes d'Hillary) tournent en orbite comme
 *    les anneaux du logo. Un doigt touche « Ajouter au panier » : les commandes
 *    arrivent sur WhatsApp.
 *  · OUTIL : l'écran s'élargit et devient un tableau de bord (voir `Tableau`).
 */
import React from 'react';
import {Easing, Img, interpolate, staticFile} from 'remotion';
import {C, COMMANDES, DEGRADE, FAITS, LARGEUR, ORBITE, PRODUITS, type Registre, SITES, T, TEL, TEXTES, instants, mot, R} from '../donnees';
import {IconeDiscussion} from '../Icones';
import {DOUX, GLISSE, Mots, Repere, mix, montant, p, ressort} from '../outils';
import {MONO, TEXTE, TITRE} from '../polices';
import {Capture, Telephone} from '../Telephone';
import {Tableau} from './Tableau';

const ECRAN_L = TEL.l - 26;
const ECRAN_H = TEL.h - 26;
const TOUCHER = {x: 0.5, y: 0.697}; // « Ajouter au panier », mesuré sur la capture
/** Au-delà, le film est figé : c'est `Montage` qui le montre, dans son moniteur. */
const MAX = T.fige + 0.02;

// ------------------------------------------------------------------ les titres

/** Un titre de service sur deux lignes, chaque ligne à son mot. */
const TitreService: React.FC<{t: number; numero: string; lignes: [string, number][]; a: number; sortie: number}> = ({t, numero, lignes, a, sortie}) => {
	const s = p(t, sortie, sortie + 0.32, Easing.in(Easing.cubic));
	if (t < a - 0.1 || s >= 1) return null;
	return (
		<div style={{position: 'absolute', left: 0, width: LARGEUR, top: 236, textAlign: 'center', opacity: 1 - s, transform: `translateY(${-50 * s}px)`}}>
			<Repere t={t} a={a} texte={numero} style={{justifyContent: 'center', fontFamily: MONO}} />
			{lignes.map(([texte, depart], k) => {
				const e = ressort(t, depart, {damping: 15, stiffness: 160});
				return (
					<div
						key={k}
						style={{
							fontFamily: TITRE,
							fontWeight: 800,
							fontSize: 96,
							lineHeight: 1.02,
							whiteSpace: 'nowrap',
							letterSpacing: '-0.015em',
							marginTop: k ? 0 : 18,
							opacity: Math.min(1, e * 1.5),
							transform: `translateY(${(1 - e) * 60}px)`,
							filter: e < 0.97 ? `blur(${(1 - e) * 18}px)` : undefined,
							...(k
								? {backgroundImage: DEGRADE, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', WebkitTextFillColor: 'transparent'}
								: {color: C.lavande}),
						}}
					>
						{texte}
					</div>
				);
			})}
		</div>
	);
};

/** La seconde moitié d'une réplique : une petite ligne, puis le grand mot en lumière. */
const Chute: React.FC<{t: number; petit: string; grand: string; instantsPetit: number[]; instantsGrand: number[]; sortie: number; eclatA?: number}> = ({
	t,
	petit,
	grand,
	instantsPetit,
	instantsGrand,
	sortie,
	eclatA,
}) => {
	if (t < instantsPetit[0] - 0.1) return null;
	const balaye = eclatA === undefined ? 0 : p(t, eclatA, eclatA + 0.7, GLISSE);
	return (
		<div style={{position: 'absolute', left: 40, width: LARGEUR - 80, top: 250, textAlign: 'center'}}>
			<Mots t={t} texte={petit} a={0} instants={instantsPetit} police={TEXTE} graisse={500} taille={52} sortie={sortie} />
			<div style={{position: 'relative', display: 'inline-block', marginTop: 4}}>
				<Mots t={t} texte={grand} a={0} instants={instantsGrand} taille={98} degrade={DEGRADE} sortie={sortie} espacement="-0.02em" interligne={1.0} />
				{balaye > 0 && balaye < 1 && t < sortie ? (
					<div
						style={{
							position: 'absolute',
							inset: '-10px -30px',
							background: `linear-gradient(100deg, transparent ${balaye * 130 - 40}%, rgba(255,255,255,.75) ${balaye * 130 - 22}%, transparent ${balaye * 130 - 4}%)`,
							mixBlendMode: 'overlay',
						}}
					/>
				) : null}
			</div>
		</div>
	);
};

// ------------------------------------------------------- l'écran de la vitrine

/** Le plan d'architecte : la grille, puis les blocs d'un site qui se tracent. */
const Plan: React.FC<{t: number}> = ({t}) => {
	const v = (a: number, b: number) => p(t, a, b, Easing.inOut(Easing.cubic));
	const a = T.vitrine + 0.15;
	const blocs: [string, number, number][] = [
		[`M28 70 H${ECRAN_L - 28}`, a, a + 0.3],
		[`M28 100 h150 v40 h-150 Z`, a + 0.1, a + 0.4],
		[`M${ECRAN_L - 120} 108 h90 M${ECRAN_L - 120} 122 h90 M${ECRAN_L - 120} 136 h90`, a + 0.15, a + 0.4],
		[`M28 180 H${ECRAN_L - 28} V520 H28 Z`, a + 0.2, a + 0.65],
		[`M28 180 L${ECRAN_L - 28} 520 M${ECRAN_L - 28} 180 L28 520`, a + 0.4, a + 0.8],
		[`M28 570 h330 M28 615 h260 M28 660 h300`, a + 0.55, a + 0.95],
		[`M28 720 h${ECRAN_L - 56} M28 750 h${ECRAN_L - 90} M28 780 h${ECRAN_L - 70}`, a + 0.7, a + 1.05],
		[`M28 840 h230 a28 28 0 0 1 0 56 h-230 a28 28 0 0 1 0 -56 Z`, a + 0.8, a + 1.15],
	];
	const quadrillage = v(T.vitrine, T.vitrine + 0.4);
	return (
		<div style={{position: 'absolute', inset: 0, background: `radial-gradient(circle at 50% 30%, #13204a, ${C.encre})`}}>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					opacity: quadrillage * 0.5,
					background: `linear-gradient(rgba(168,236,255,.14) 1px, transparent 1px) 0 0/28px 28px, linear-gradient(90deg, rgba(168,236,255,.14) 1px, transparent 1px) 0 0/28px 28px`,
				}}
			/>
			<svg width={ECRAN_L} height={ECRAN_H} style={{position: 'absolute', inset: 0, filter: `drop-shadow(0 0 6px ${C.cyan})`}}>
				{blocs.map(([d, de, a2], k) => (
					<path key={k} d={d} pathLength={1} fill="none" stroke={C.cyan} strokeWidth={2.4} strokeDasharray={1} strokeDashoffset={1 - v(de, a2)} strokeLinecap="round" />
				))}
			</svg>
		</div>
	);
};

/** L'écran de la vitrine : le plan, puis le vrai site révélé par une ligne de lumière. */
const EcranVitrine: React.FC<{t: number}> = ({t}) => {
	const revele = p(t, T.revele, T.revele + 0.5, Easing.inOut(Easing.quad));
	const defile = interpolate(t, [T.revele + 0.6, T.catalogue], [0, 560], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
	return (
		<>
			{revele < 1 ? <Plan t={t} /> : null}
			<div style={{position: 'absolute', inset: 0, clipPath: `inset(0 0 ${(1 - revele) * 100}% 0)`}}>
				<Capture site={SITES.vitrine} long defile={defile} />
			</div>
			{revele > 0 && revele < 1 ? (
				<div
					style={{
						position: 'absolute',
						left: 0,
						right: 0,
						top: `${revele * 100}%`,
						height: 4,
						marginTop: -2,
						background: '#fff',
						boxShadow: `0 0 24px 8px ${C.cyan}, 0 0 60px 20px rgba(98,168,255,.6)`,
					}}
				/>
			) : null}
		</>
	);
};

/** L'écran du catalogue : le vrai catalogue d'Au Braisé d'Or, et le doigt qui commande. */
const EcranCatalogue: React.FC<{t: number}> = ({t}) => {
	const appui = t - T.tap;
	const x = TOUCHER.x * ECRAN_L;
	const y = TOUCHER.y * ECRAN_L * (2532 / 1170);
	return (
		<>
			<Capture site={SITES.catalogue} />
			{appui > -0.25 && appui < 0.9 ? (
				<>
					<div
						style={{
							position: 'absolute',
							left: x - 34,
							top: y - 34,
							width: 68,
							height: 68,
							borderRadius: 34,
							background: 'rgba(255,255,255,.55)',
							border: '3px solid #fff',
							opacity: appui < 0 ? p(t, T.tap - 0.25, T.tap) : 1 - p(t, T.tap + 0.25, T.tap + 0.5),
							transform: `scale(${appui < 0 ? 1.3 - 0.3 * p(t, T.tap - 0.25, T.tap) : 0.85})`,
						}}
					/>
					{appui > 0 ? (
						<div
							style={{
								position: 'absolute',
								left: x - 160 * DOUX(Math.min(1, appui / 0.6)),
								top: y - 160 * DOUX(Math.min(1, appui / 0.6)),
								width: 320 * DOUX(Math.min(1, appui / 0.6)),
								height: 320 * DOUX(Math.min(1, appui / 0.6)),
								borderRadius: '50%',
								border: `4px solid ${C.vertWa}`,
								opacity: 1 - Math.min(1, appui / 0.6),
							}}
						/>
					) : null}
				</>
			) : null}
		</>
	);
};

// ----------------------------------------------------------- l'éventail des vitrines

const EVENTAIL = [
	{dx: 300, echelle: 0.74, rot: -24, retard: 0},
	{dx: -300, echelle: 0.74, rot: 24, retard: 0.07},
	{dx: 520, echelle: 0.6, rot: -32, retard: 0.14},
	{dx: -520, echelle: 0.6, rot: 32, retard: 0.21},
];

const Eventail: React.FC<{t: number}> = ({t}) => {
	if (t < T.eventail - 0.05 || t > T.catalogue + 0.1) return null;
	const ferme = p(t, T.catalogue - 0.4, T.catalogue - 0.05, Easing.in(Easing.cubic));
	return (
		<>
			{SITES.eventail.map((site, k) => {
				const pose = EVENTAIL[k];
				const e = ressort(t, T.eventail + pose.retard, {damping: 16, stiffness: 120}) * (1 - ferme);
				const x = TEL.x + pose.dx * e;
				return (
					<React.Fragment key={site}>
						<Telephone
							l={TEL.l}
							h={TEL.h}
							r={TEL.r}
							rotY={pose.rot * e}
							echelle={pose.echelle}
							lueur={0.4}
							style={{left: x - TEL.l / 2, top: TEL.y - TEL.h / 2, opacity: Math.min(1, e * 1.4) * 0.92}}
						>
							<Capture site={site} />
							<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, transparent 50%, rgba(5,4,14,.45))'}} />
						</Telephone>
					</React.Fragment>
				);
			})}
		</>
	);
};

// ------------------------------------------------------------ l'orbite des produits

const CARTE = {l: 176, h: 240};

const etatCarte = (t: number, k: number) => {
	const entre = ressort(t, T.catalogue + 0.3 + k * 0.05, {damping: 18, stiffness: 90});
	const sort = p(t, T.outil - 0.55, T.outil - 0.05, Easing.in(Easing.cubic));
	const rayon = entre * (1 - sort);
	const ang = (k * Math.PI * 2) / PRODUITS.length + 0.55 * (t - T.catalogue) + Math.PI / 2;
	const r = (ORBITE.inclinaison * Math.PI) / 180;
	const ex = ORBITE.a * rayon * Math.cos(ang);
	const ey = ORBITE.b * rayon * Math.sin(ang);
	const devant = (Math.sin(ang) + 1) / 2;
	return {
		x: ORBITE.x + ex * Math.cos(r) - ey * Math.sin(r),
		y: ORBITE.y + ex * Math.sin(r) + ey * Math.cos(r),
		devant,
		echelle: (0.56 + 0.44 * devant) * (0.3 + 0.7 * rayon),
		opacite: Math.min(1, rayon * 2) * (0.5 + 0.5 * devant),
	};
};

const CarteProduit: React.FC<{t: number; k: number}> = ({t, k}) => {
	const produit = PRODUITS[k];
	const e = etatCarte(t, k);
	if (e.opacite <= 0.01) return null;
	return (
		<div
			style={{
				position: 'absolute',
				left: e.x - CARTE.l / 2,
				top: e.y - CARTE.h / 2,
				width: CARTE.l,
				height: CARTE.h,
				borderRadius: 22,
				background: 'linear-gradient(165deg, rgba(56,52,120,.78), rgba(14,13,40,.9))',
				boxShadow: `inset 0 0 0 1.5px rgba(190,200,255,.25), 0 20px 40px -18px rgba(0,0,0,.9), 0 0 ${30 * e.devant}px rgba(98,168,255,${0.35 * e.devant})`,
				transform: `scale(${e.echelle})`,
				opacity: e.opacite,
				overflow: 'hidden',
			}}
		>
			<Img src={staticFile(`nebula30/produits/${produit.img}`)} style={{position: 'absolute', left: 10, right: 10, top: 10, height: 150, width: CARTE.l - 20, objectFit: 'contain'}} />
			<div style={{position: 'absolute', left: 12, right: 12, top: 166, fontFamily: TEXTE, fontWeight: 600, fontSize: 15, lineHeight: 1.15, color: C.lavande, textAlign: 'center'}}>
				{produit.nom}
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 14, fontFamily: MONO, fontWeight: 700, fontSize: 19, color: C.cyan, textAlign: 'center'}}>
				{montant(produit.prix)} F
			</div>
		</div>
	);
};

/** Les cartes de l'arrière-plan d'abord, celles de devant après le téléphone. */
const Orbite: React.FC<{t: number; plan: 'derriere' | 'devant'}> = ({t, plan}) => {
	if (t < T.catalogue + 0.2 || t > T.outil) return null;
	return (
		<>
			{PRODUITS.map((_, k) => {
				const devant = etatCarte(t, k).devant > 0.5;
				return devant === (plan === 'devant') ? <CarteProduit key={k} t={t} k={k} /> : null;
			})}
		</>
	);
};

// ------------------------------------------------------------ les commandes qui arrivent

/** Les trois commandes arrivent pendant « …arrivent sur WhatsApp », et repartent avant l'outil. */
export const instantsCommandes = () => [0, 1, 2].map((k) => T.tap + 0.25 + k * 0.33);

const Notifications: React.FC<{t: number}> = ({t}) => {
	const [premiere] = instantsCommandes();
	if (t < premiere - 0.05 || t > T.outil + 0.2) return null;
	return (
		<>
			{COMMANDES.map((c, k) => {
				const a = instantsCommandes()[k];
				const e = ressort(t, a, {damping: 13, stiffness: 170, mass: 0.7});
				const part = p(t, T.outil - 0.2 + k * 0.05, T.outil + 0.1 + k * 0.05, Easing.in(Easing.cubic));
				if (t < a - 0.02) return null;
				return (
					<div
						key={k}
						style={{
							position: 'absolute',
							left: 70,
							width: LARGEUR - 140,
							top: 336 + k * 140,
							height: 124,
							borderRadius: 32,
							background: 'linear-gradient(180deg, rgba(34,32,70,.94), rgba(18,17,44,.94))',
							boxShadow: '0 24px 60px -20px rgba(0,0,0,.95), inset 0 0 0 1.5px rgba(190,200,255,.2)',
							display: 'flex',
							alignItems: 'center',
							gap: 20,
							padding: '0 22px',
							opacity: Math.min(1, e * 1.5) * (1 - part),
							transform: `translateY(${(1 - e) * -180 - part * 260}px) scale(${0.92 + 0.08 * e})`,
						}}
					>
						<IconeDiscussion taille={66} />
						<div style={{flex: 1, minWidth: 0}}>
							<div style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 19, color: C.gris}}>WhatsApp · maintenant</div>
							<div style={{fontFamily: TEXTE, fontWeight: 700, fontSize: 25, color: C.lavande, marginTop: 2, whiteSpace: 'nowrap'}}>Nouvelle commande · {c.maison}</div>
							<div style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 23, color: C.cyan, marginTop: 2, whiteSpace: 'nowrap'}}>
								{c.article} · <span style={{fontFamily: MONO, fontWeight: 700}}>{montant(c.prix)} F</span>
							</div>
						</div>
						{c.img ? <Img src={staticFile(`nebula30/produits/${c.img}`)} style={{width: 64, height: 96, objectFit: 'contain'}} /> : null}
					</div>
				);
			})}
		</>
	);
};

/** La pastille « dès 50 000 F », dont le chiffre monte comme un compteur. */
const Prix: React.FC<{t: number; a: number; sortie: number}> = ({t, a, sortie}) => {
	const e = ressort(t, a, {damping: 14, stiffness: 160});
	const s = p(t, sortie, sortie + 0.3);
	if (t < a || s >= 1) return null;
	const roule = p(t, a, a + 0.8, Easing.out(Easing.cubic));
	return (
		<div style={{position: 'absolute', left: 0, width: LARGEUR, top: 478, display: 'flex', justifyContent: 'center', opacity: Math.min(1, e * 1.4) * (1 - s)}}>
			<div
				style={{
					display: 'flex',
					alignItems: 'baseline',
					gap: 14,
					padding: '8px 30px',
					borderRadius: 60,
					border: `2px solid ${C.cyan}`,
					background: 'rgba(12,11,34,.82)',
					boxShadow: `0 0 34px rgba(168,236,255,.35)`,
					transform: `scale(${0.8 + 0.2 * e})`,
				}}
			>
				<span style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 30, color: C.lavande}}>dès</span>
				<span style={{fontFamily: MONO, fontWeight: 700, fontSize: 48, color: C.cyan}}>{montant(FAITS.prixEntree * roule)} F</span>
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ le téléphone

export const Tours: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	if (t < T.versTel + 0.3 || t > MAX) return null;
	const x = TEXTES[registre];
	const apparait = p(t, T.versTel + 0.62, T.versTel + 0.95);
	// la bascule vitrine → catalogue : un quart de tour, on change d'écran, un quart de tour
	const b1 = p(t, T.catalogue - 0.08, T.catalogue + 0.2, Easing.in(Easing.cubic));
	const b2 = p(t, T.catalogue + 0.2, T.catalogue + 0.55, DOUX);
	const bascule = t < T.catalogue + 0.2 ? 90 * b1 : -90 * (1 - b2);
	const ouvert = p(t, T.eventail, T.eventail + 0.6) * (1 - p(t, T.catalogue - 0.4, T.catalogue - 0.1));
	const morph = p(t, T.outil - 0.05, T.outil + 0.5, GLISSE);
	const l = mix(TEL.l, 940, morph);
	const hauteur = mix(TEL.h, 1060, morph);
	const rotY = -11 * ouvert + bascule + Math.sin(t * 0.9) * 3 * (1 - morph);
	const rotX = Math.sin(t * 0.7 + 1) * 2 * (1 - morph);
	const ecran = t < T.catalogue + 0.2 ? 'vitrine' : t < T.outil + 0.15 ? 'catalogue' : 'outil';
	// la montée avant que tout se fige
	const tension = p(t, T.fige - 1.6, T.fige, Easing.in(Easing.quad));
	return (
		<>
			<Eventail t={t} />
			<Orbite t={t} plan="derriere" />
			<Telephone
				l={l}
				h={hauteur}
				r={mix(TEL.r, 46, morph)}
				rotY={rotY}
				rotX={rotX}
				echelle={(0.94 + 0.06 * apparait) * (1 + 0.04 * tension)}
				lueur={0.7 + 0.6 * tension}
				corps={1 - morph}
				style={{left: TEL.x - l / 2, top: TEL.y - hauteur / 2, opacity: apparait}}
			>
				{ecran === 'vitrine' ? <EcranVitrine t={t} /> : null}
				{ecran === 'catalogue' ? <EcranCatalogue t={t} /> : null}
				{ecran === 'outil' ? (
					<div style={{position: 'absolute', inset: 0, opacity: p(t, T.outil + 0.15, T.outil + 0.45)}}>
						<Tableau t={t} l={l - 26 * (1 - morph)} h={hauteur - 26 * (1 - morph)} registre={registre} />
					</div>
				) : null}
			</Telephone>
			<Orbite t={t} plan="devant" />
			<Notifications t={t} />

			{/* VITRINE DIGITALE, puis « et vous devenez UNE MARQUE. » */}
			<TitreService t={t} numero="01 / 03" a={R.vitrine[0]} lignes={[['VITRINE', mot('vitrine', 1)], ['DIGITALE', mot('vitrine', 2)]]} sortie={T.eventail - 0.1} />
			<Chute t={t} petit={x.devenez} grand={x.marque} instantsPetit={instants('marque').slice(0, 3)} instantsGrand={instants('marque').slice(3)} sortie={T.catalogue - 0.3} eclatA={mot('marque', 4) + 0.15} />

			{/* CATALOGUE DIGITAL · dès 50 000 F, puis les commandes */}
			<TitreService t={t} numero="02 / 03" a={R.catalogue[0]} lignes={[['CATALOGUE', mot('catalogue', 1)], ['DIGITAL', mot('catalogue', 2)]]} sortie={T.tap - 0.1} />
			<Prix t={t} a={mot('catalogue', 2) + 0.25} sortie={T.tap - 0.1} />
			<Mots
				t={t}
				texte={x.commandes}
				a={0}
				instants={instants('commandes')}
				police={TEXTE}
				graisse={600}
				taille={41}
				sortie={T.outil - 0.3}
				style={{position: 'absolute', left: 40, width: LARGEUR - 80, top: 252, textAlign: 'center', whiteSpace: 'nowrap', textShadow: '0 0 30px rgba(5,4,14,.9)'}}
			/>

			{/* OUTIL DIGITAL, puis « pensé pour VOTRE MÉTIER. » */}
			<TitreService t={t} numero="03 / 03" a={R.outil[0]} lignes={[['OUTIL', mot('outil', 1)], ['DIGITAL', mot('outil', 2)]]} sortie={T.peaux - 0.1} />
			<Chute t={t} petit={x.pensePour} grand={x.metier} instantsPetit={instants('outil').slice(3, 5)} instantsGrand={instants('outil').slice(5)} sortie={MAX} eclatA={mot('outil', 6) + 0.15} />
		</>
	);
};

