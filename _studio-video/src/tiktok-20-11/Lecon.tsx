/**
 * 3 · LA LEÇON (statut de 17 h, 12,9 → 22,3 s).
 * « Ton catalogue PDF pèse 50 Mo ? » Le PDF tombe comme une pierre ; sur la 3G
 * la barre de téléchargement rampe, le minuteur file, et le client regarde
 * ailleurs. Puis le fond du statut : le rocher (le fichier lourd fait attendre)
 * contre le téléphone léger (le lien fait commander). On plonge dans sa lumière.
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, random, staticFile} from 'remotion';
import {C, T, TEL_FOND} from './donnees';
import {BarreEtat, CL, Etincelle, Etiquette, Horloge, lin, minuteur, Mots, Pdf, phrase, ressort, Rouet, secousse, Telephone, TEXTE_DEGRADE, Toucher} from './outils';
import {MONO, TEXTE, TITRE} from './polices';

const TEL = {x: 320, y: 480, l: 440, h: 780};

export const Lecon: React.FC<{t: number}> = ({t}) => {
	if (t < T.lecon || t > T.lourd + 0.3) return null;
	const entree = lin(t, T.lecon, T.lecon + 0.35, 1, 0, Easing.out(Easing.cubic));
	return (
		<AbsoluteFill style={{transform: `translateY(${(entree * 1920).toFixed(1)}px) ${secousse(t, [[T.mo, 26]])}`}}>
			<CinquanteMo t={t} />
			<Attente t={t} />
		</AbsoluteFill>
	);
};

/** La poussière soulevée quand le PDF touche le sol. */
const POUSSIERE = Array.from({length: 18}, (_, i) => {
	const angle = (200 + random(`pa${i}`) * 140) * (Math.PI / 180);
	const v = 260 + random(`pv${i}`) * 520;
	return {vx: Math.cos(angle) * v, vy: Math.sin(angle) * v * 0.55, r: 6 + random(`pr${i}`) * 12};
});

/** Le haut de la fenêtre d'où sort le PDF (sous le « 50 Mo ? ») et la hauteur de sa chute. */
const BORD = 700;
const CHUTE = 1250 - 380 - BORD + 380;

/** « Ton catalogue PDF pèse 50 Mo ? » et le PDF qui tombe. */
const CinquanteMo: React.FC<{t: number}> = ({t}) => {
	if (t > T.reseau + 0.4) return null;
	const sortie = lin(t, T.reseau - 0.05, T.reseau + 0.3, 0, 1, Easing.in(Easing.cubic));
	const mo = Math.round(interpolate(t, [T.chute, T.mo], [0, 50], {...CL, easing: Easing.in(Easing.quad)}));
	const montreMo = t >= T.chute;
	const slam = t >= T.mo ? Math.max(0, 1 - (t - T.mo) / 0.16) : 0;
	const sMo = ressort(t, T.chute, 220, 14);

	// la chute : gravité jusqu'au sol, puis l'écrasement qui rebondit
	// il sort de SOUS le « 50 Mo ? » (la fenêtre commence à BORD) : il ne passe jamais derrière le titre
	const y = t < T.mo ? interpolate(t, [T.chute, T.mo], [-CHUTE, 0], {...CL, easing: Easing.in(Easing.quad)}) : 0;
	const ecrase = t >= T.mo ? Math.exp(-(t - T.mo) * 9) * Math.cos((t - T.mo) * 30) : 0;
	const sol = 1250;
	const d = t - T.mo;

	return (
		<AbsoluteFill style={{opacity: 1 - sortie}}>
			{/* l'ombre au sol grandit à mesure que le PDF approche */}
			{montreMo ? (
				<div
					style={{
						position: 'absolute',
						top: sol - 10,
						left: 540 - 180,
						width: 360,
						height: 40,
						borderRadius: '50%',
						background: 'radial-gradient(ellipse, rgba(0,0,0,.65), transparent 70%)',
						opacity: interpolate(y, [-CHUTE, 0], [0.1, 1], CL) * (1 - sortie),
						transform: `scaleX(${interpolate(y, [-CHUTE, 0], [0.4, 1.1], CL).toFixed(3)})`,
					}}
				/>
			) : null}

			{montreMo ? (
				<div style={{position: 'absolute', top: BORD, left: 0, right: 0, bottom: 0, overflow: 'hidden'}}>
				<div
					style={{
						position: 'absolute',
						left: 540 - 150,
						top: sol - 380 - BORD,
						width: 300,
						height: 380,
						transformOrigin: '50% 100%',
						transform: `translateY(${y.toFixed(1)}px) scale(${(1 + 0.12 * ecrase - sortie * 0.6).toFixed(3)}, ${(1 - 0.18 * ecrase - sortie * 0.6).toFixed(3)}) rotate(${(t < T.mo ? -6 + (y / -CHUTE) * -10 : -6 * Math.exp(-d * 6)).toFixed(2)}deg)`,
						filter: 'drop-shadow(0 30px 40px rgba(0,0,0,.5))',
					}}
				>
					<Pdf taille={300} />
				</div>
				</div>
			) : null}

			{d > 0 && d < 0.8
				? POUSSIERE.map((p, i) => (
						<div
							key={i}
							style={{
								position: 'absolute',
								left: 540 + p.vx * d - p.r,
								top: sol + p.vy * d + 380 * d * d - p.r,
								width: p.r * 2,
								height: p.r * 2,
								borderRadius: '50%',
								background: 'rgba(201,210,255,.55)',
								opacity: Math.max(0, 1 - d / 0.8),
							}}
						/>
					))
				: null}

			{/* le texte passe DEVANT le PDF qui tombe : le titre reste lisible pendant la chute */}
			<Etiquette t={t} a={T.lecon + 0.1} texte="CONSEIL N° 2 · TES VENTES" top={230} />
			<div style={{position: 'absolute', top: 300, left: 60, right: 60, transform: `translateY(${(-sortie * 300).toFixed(1)}px)`}}>
				<Mots t={t} mots={phrase('Ton catalogue PDF pèse', T.lecon + 0.25, 0.13)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 80, lineHeight: 1.08, color: C.lumiere}} />
			</div>
			{montreMo ? (
				<div
					style={{
						position: 'absolute',
						top: 540,
						left: 0,
						right: 0,
						textAlign: 'center',
						fontFamily: TITRE,
						fontWeight: 800,
						fontSize: 140,
						lineHeight: 1,
						opacity: Math.min(1, sMo * 1.8),
						transform: `translateY(${(-sortie * 300).toFixed(1)}px) scale(${(1 + slam * 0.35).toFixed(3)})`,
						filter: 'drop-shadow(0 0 40px rgba(147,51,234,.55))',
					}}
				>
					<span style={TEXTE_DEGRADE}>{mo}&nbsp;Mo&nbsp;?</span>
				</div>
			) : null}
		</AbsoluteFill>
	);
};

/** Sur la 3G : la barre qui rampe, le minuteur qui file, puis il regarde ailleurs. */
const Attente: React.FC<{t: number}> = ({t}) => {
	if (t < T.reseau - 0.05) return null;
	const entree = ressort(t, T.reseau + 0.05, 140, 16);
	const depart = lin(t, T.ailleurs + 0.25, T.ailleurs + 0.75, 0, 1, Easing.in(Easing.cubic));
	const texte1 = 1 - lin(t, T.ailleurs - 0.1, T.ailleurs + 0.1);
	const attente = interpolate(t, [T.reseau, T.lourd], [0, 252], CL); // 0:00 → 4:12 en accéléré
	const pct = 1 + Math.floor(interpolate(t, [T.reseau, T.lourd], [0, 3.4], CL));
	return (
		<AbsoluteFill>
			<div style={{position: 'absolute', top: 240, left: 70, right: 70, opacity: texte1, transform: `translateY(${((1 - texte1) * -60).toFixed(1)}px)`}}>
				<Mots
					t={t}
					mots={[
						...phrase('Sur la 3G, ton client attend', T.reseau + 0.05, 0.1),
						...phrase('de longues minutes…', T.reseau + 0.85, 0.12, {color: C.cyan}),
					]}
					style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 64, lineHeight: 1.15, color: C.lumiere}}
				/>
			</div>
			{t >= T.ailleurs ? (
				<div style={{position: 'absolute', top: 240, left: 60, right: 60}}>
					<Mots t={t} mots={phrase('Pendant ce temps,', T.ailleurs + 0.02, 0.1)} style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 64, color: C.lumiere}} />
					<Mots t={t} mots={phrase('il regarde ailleurs.', T.ailleurs + 0.35, 0.11)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 92, lineHeight: 1.06, color: C.cyan, marginTop: 14}} />
				</div>
			) : null}

			<div style={{position: 'absolute', left: TEL.x, top: TEL.y, perspective: 1600}}>
				<div
					style={{
						transform: `translateX(${((1 - entree) * 900 - depart * 1100).toFixed(1)}px) rotateY(${((1 - entree) * -30 + depart * 25).toFixed(2)}deg) rotate(${(depart * -16).toFixed(2)}deg)`,
						opacity: 1 - depart * 0.6,
					}}
				>
					<Telephone l={TEL.l} h={TEL.h} ecran={C.nuit} lueur={0.6}>
						<BarreEtat heure="21:04" encre={C.lumiere} reseau="3G" barres={1} clignote={0.35 + 0.65 * Math.abs(Math.sin(t * 5))} />
						<div style={{position: 'absolute', top: 210, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22}}>
							<div style={{display: 'flex', alignItems: 'center', gap: 18, background: 'rgba(201,210,255,.08)', borderRadius: 20, padding: '18px 22px'}}>
								<Pdf taille={56} />
								<div>
									<div style={{fontFamily: TEXTE, fontWeight: 700, fontSize: 25, color: C.lumiere}}>catalogue.pdf</div>
									<div style={{fontFamily: MONO, fontWeight: 500, fontSize: 21, color: C.gris, marginTop: 4}}>50 Mo · PDF</div>
								</div>
							</div>
							<Rouet t={t} taille={74} couleur={C.cyan} />
							<div style={{width: 320, height: 14, borderRadius: 7, background: 'rgba(201,210,255,.14)', overflow: 'hidden'}}>
								<div style={{width: `${pct}%`, height: '100%', borderRadius: 7, background: C.cyan}} />
							</div>
							<div style={{fontFamily: TEXTE, fontWeight: 600, fontSize: 25, color: C.gris}}>
								Téléchargement… <span style={{fontFamily: MONO, fontWeight: 700, color: C.lumiere}}>{pct} %</span>
							</div>
						</div>
					</Telephone>
				</div>
			</div>

			<div
				style={{
					position: 'absolute',
					top: 1300,
					left: 0,
					right: 0,
					display: 'flex',
					justifyContent: 'center',
					alignItems: 'center',
					gap: 20,
					opacity: Math.min(1, entree * 1.5),
				}}
			>
				<Horloge t={t} taille={70} couleur={C.pervenche} />
				<span style={{fontFamily: MONO, fontWeight: 700, fontSize: 104, color: C.lumiere}}>{minuteur(attente)}</span>
			</div>
		</AbsoluteFill>
	);
};

/** Les étincelles qui montent du téléphone léger. */
const ETINCELLES = Array.from({length: 16}, (_, i) => ({
	dx: (random(`sx${i}`) - 0.5) * 260,
	v: 120 + random(`sv${i}`) * 220,
	d: random(`sd${i}`) * 1.2,
	taille: 18 + random(`st${i}`) * 26,
}));

/** Le fond du statut de 17 h : le rocher contre le téléphone, puis la plongée dans sa lumière. */
export const LourdLeger: React.FC<{t: number}> = ({t}) => {
	if (t < T.lourd || t > T.offre + 0.1) return null;
	const apparait = lin(t, T.lourd, T.lourd + 0.12);
	const kb = interpolate(t, [T.lourd, T.offre], [1.12, 1.0], CL);
	const plongee = lin(t, T.plongee, T.offre, 0, 1, Easing.in(Easing.cubic));
	const chuteY = t < T.lourd + 0.25 ? interpolate(t, [T.lourd, T.lourd + 0.25], [-60, 0], {...CL, easing: Easing.in(Easing.quad)}) : 0;
	const leger = lin(t, T.leger, T.leger + 0.5);
	const textes = 1 - lin(t, T.plongee - 0.1, T.plongee + 0.2);
	const pouls = 0.75 + 0.25 * Math.sin((t - T.leger) * 7);
	return (
		<AbsoluteFill style={{opacity: apparait, transform: secousse(t, [[T.lourd + 0.25, 22]])}}>
			<AbsoluteFill
				style={{
					transformOrigin: `${TEL_FOND.x}px ${TEL_FOND.y}px`,
					transform: `translateY(${chuteY.toFixed(1)}px) scale(${(kb * (1 + plongee * 2.6)).toFixed(4)})`,
				}}
			>
				<Img src={staticFile('tiktok-20-11/lourd-leger.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
				{/* le rocher s'assombrit quand le lien gagne */}
				<div style={{position: 'absolute', left: 0, top: 0, width: 640, height: '100%', background: 'linear-gradient(90deg, rgba(6,7,19,.55), rgba(6,7,19,0))', opacity: leger}} />
				<div
					style={{
						position: 'absolute',
						left: TEL_FOND.x - 330,
						top: TEL_FOND.y - 330,
						width: 660,
						height: 660,
						borderRadius: '50%',
						background: 'radial-gradient(circle, rgba(255,190,110,.6), rgba(147,51,234,.25) 45%, transparent 70%)',
						opacity: leger * pouls,
						mixBlendMode: 'screen',
					}}
				/>
				{t >= T.leger
					? ETINCELLES.map((e, i) => {
							const d = (t - T.leger - e.d) % 1.4;
							if (t - T.leger < e.d) return null;
							return (
								<Etincelle
									key={i}
									x={TEL_FOND.x + e.dx}
									y={TEL_FOND.y + 120 - e.v * d}
									taille={e.taille}
									opacite={Math.max(0, 1 - d / 1.4) * leger}
									couleur={i % 3 === 0 ? C.or : C.lumiere}
									angle={d * 90}
								/>
							);
						})
					: null}
				<Toucher t={t} a={T.leger + 0.55} x={TEL_FOND.x} y={TEL_FOND.y + 40} couleur={C.or} />
			</AbsoluteFill>

			{/* les voiles qui portent le texte */}
			<AbsoluteFill style={{background: 'linear-gradient(rgba(6,7,19,.94) 0%, rgba(6,7,19,.75) 16%, rgba(6,7,19,0) 30%, rgba(6,7,19,0) 56%, rgba(6,7,19,.88) 70%, rgba(6,7,19,.97) 100%)', opacity: textes}} />

			<div style={{position: 'absolute', top: 240, left: 60, right: 60, opacity: textes}}>
				<Mots t={t} mots={phrase('Un fichier lourd', T.lourd + 0.3, 0.12)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 70, lineHeight: 1.1, color: C.lumiere}} />
				<Mots t={t} mots={phrase('fait attendre.', T.lourd + 0.65, 0.12)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 70, lineHeight: 1.1, color: C.gris}} />
			</div>
			<div style={{position: 'absolute', top: 1360, left: 60, right: 60, opacity: textes, textShadow: '0 4px 30px rgba(6,7,19,.9)'}}>
				<Mots t={t} mots={phrase('Un lien léger', T.leger, 0.12)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 70, lineHeight: 1.1, color: C.cyan}} />
				<Mots t={t} mots={phrase('fait commander.', T.leger + 0.35, 0.12)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 70, lineHeight: 1.1, color: C.cyan}} />
			</div>
		</AbsoluteFill>
	);
};
