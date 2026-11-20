/**
 * 2 · LE CONSEIL (statut de 13 h, 2,3 → 12,9 s).
 * « Avant de commander, ton client veut 3 choses » : la photo, le prix, comment
 * commander. Chacune s'allume sur le téléphone ET se coche dans la liste.
 * Puis le revers (« c'est combien ? »… il va voir ailleurs) et la promesse :
 * « Ton catalogue montre les 3. Même la nuit. »
 *
 * ⚠️ Le téléphone est DESSINÉ : le statut montrait un téléphone généré aux prix
 * illisibles (« 100.00 »), qui fait image d'IA (remarque de Polaris). Ici la carte
 * est nette, en francs, et c'est un exemple : aucun produit de client.
 */
import React from 'react';
import {AbsoluteFill, Easing, interpolate, interpolateColors} from 'remotion';
import {C, DEGRADE, PRIX_EXEMPLE, T} from './donnees';
import {BarreEtat, Bulle, CL, Cadeau, Coche, Combine, Etiquette, ImageVide, lin, Lune, millier, Mots, phrase, ressort, secousse, Telephone, TEXTE_DEGRADE, Toucher} from './outils';
import {MONO, TEXTE, TITRE} from './polices';

/** Le téléphone de la liste : position et taille dans l'image. */
const TEL = {x: 320, y: 280, l: 440, h: 800};
/** L'écran (la coque fait 12 px). */
const EC = {l: TEL.l - 24, h: TEL.h - 24};
/** Le bouton « Commander » dans l'écran : le doigt y tombe. */
const BOUTON = {x: 24, y: 600, l: EC.l - 48, h: 84};

/** L'anneau cyan qui désigne la chose dont on parle. */
const anneau = (t: number, a: number, b: number) => lin(t, a, a + 0.22) * (1 - lin(t, b - 0.3, b));

export const Conseil: React.FC<{t: number}> = ({t}) => {
	if (t < T.conseil - 0.05 || t > T.lecon + 0.4) return null;
	const glisse = lin(t, T.lecon, T.lecon + 0.35, 0, 1, Easing.in(Easing.cubic));
	return (
		<AbsoluteFill style={{transform: `translateY(${(-glisse * 1920).toFixed(1)}px) ${secousse(t, [[T.trois, 16], [T.sinon + 0.7, 9]])}`}}>
			<TroisChoses t={t} />
			<Liste t={t} />
		</AbsoluteFill>
	);
};

/** « Avant de commander, ton client veut 3 choses. » Le 3 arrive de face. */
const TroisChoses: React.FC<{t: number}> = ({t}) => {
	if (t > T.liste + 0.4) return null;
	const sortie = lin(t, T.liste, T.liste + 0.35, 0, 1, Easing.in(Easing.cubic));
	const s3 = ressort(t, T.trois, 190, 11);
	const sc = ressort(t, T.choses, 220, 14);
	return (
		<AbsoluteFill style={{opacity: 1 - sortie, transform: `scale(${(1 + sortie * 0.4).toFixed(3)})`}}>
			<Etiquette t={t} a={T.conseil} texte="CONSEIL N° 1 · LES FÊTES" top={290} />
			<div style={{position: 'absolute', top: 370, left: 80, right: 80}}>
				<Mots t={t} mots={phrase('Avant de commander, ton client veut', T.conseil + 0.1, 0.14)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 84, lineHeight: 1.16, color: C.lumiere}} />
			</div>
			<div style={{position: 'absolute', top: 800, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34}}>
				<span
					style={{
						display: 'inline-block',
						fontFamily: TITRE,
						fontWeight: 800,
						fontSize: 300,
						lineHeight: 1,
						...TEXTE_DEGRADE,
						opacity: Math.min(1, s3 * 2),
						transform: `scale(${(3 - 2 * s3).toFixed(3)}) rotate(${((1 - s3) * -14).toFixed(2)}deg)`,
						filter: 'drop-shadow(0 0 46px rgba(79,111,255,.6))',
					}}
				>
					3
				</span>
				<span
					style={{
						display: 'inline-block',
						fontFamily: TITRE,
						fontWeight: 800,
						fontSize: 84,
						color: C.lumiere,
						opacity: Math.min(1, sc * 1.8),
						transform: `translateX(${((1 - sc) * 120).toFixed(1)}px)`,
					}}
				>
					choses.
				</span>
			</div>
		</AbsoluteFill>
	);
};

const ITEMS = [
	{n: '1', texte: 'La photo.', a: T.photo},
	{n: '2', texte: 'Le prix.', a: T.prix},
	{n: '3', texte: 'Comment commander.', a: T.commander},
];

/** Le téléphone, la liste qui se coche, puis le revers et la nuit. */
const Liste: React.FC<{t: number}> = ({t}) => {
	if (t < T.liste + 0.05) return null;
	const monte = ressort(t, T.liste + 0.1, 120, 16);
	const voile = lin(t, T.sinon, T.sinon + 0.25) * (1 - lin(t, T.nuit - 0.15, T.nuit + 0.2));
	const nuit = lin(t, T.nuit, T.nuit + 0.45, 0, 1, Easing.inOut(Easing.cubic));
	const listeSort = lin(t, T.nuit - 0.1, T.nuit + 0.3, 0, 1, Easing.in(Easing.cubic));
	const tete = ressort(t, T.liste + 0.2, 200, 16);
	return (
		<AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					top: 180,
					left: 0,
					right: 0,
					textAlign: 'center',
					fontFamily: TEXTE,
					fontWeight: 700,
					fontSize: 44,
					color: C.lavande,
					opacity: Math.min(1, tete * 1.6) * (1 - voile) * (1 - listeSort),
					transform: `translateY(${((1 - tete) * -40).toFixed(1)}px)`,
				}}
			>
				Avant de commander, il veut :
			</div>

			<div style={{position: 'absolute', left: TEL.x, top: TEL.y, perspective: 1600}}>
				<div
					style={{
						transform: `translateY(${((1 - monte) * 1000).toFixed(1)}px) rotateY(${(Math.sin(t * 0.9) * 8).toFixed(2)}deg) rotateX(4deg) scale(${(1 - voile * 0.06).toFixed(3)})`,
						opacity: 1 - voile * 0.85,
					}}
				>
					<Telephone l={TEL.l} h={TEL.h} ecran={interpolateColors(nuit, [0, 1], [C.papier, C.nuit])} lueur={1 + nuit * 0.6}>
						<EcranCatalogue t={t} nuit={nuit} />
					</Telephone>
				</div>
			</div>

			<div style={{position: 'absolute', top: 1130, left: 110, opacity: (1 - voile * 0.88) * (1 - listeSort), transform: `translateY(${(listeSort * 240).toFixed(1)}px)`}}>
				{ITEMS.map((it, i) => {
					const s = ressort(t, it.a + 0.15, 200, 15);
					const actif = t < (ITEMS[i + 1]?.a ?? T.sinon);
					return (
						<div
							key={it.n}
							style={{
								display: 'flex',
								alignItems: 'center',
								gap: 26,
								height: 115,
								opacity: Math.min(1, s * 1.7),
								transform: `translateX(${((1 - s) * -160).toFixed(1)}px)`,
							}}
						>
							<div
								style={{
									width: 84,
									height: 84,
									borderRadius: '50%',
									background: DEGRADE,
									display: 'flex',
									alignItems: 'center',
									justifyContent: 'center',
									fontFamily: TEXTE,
									fontWeight: 900,
									fontSize: 44,
									color: C.lumiere,
									boxShadow: actif ? '0 0 34px rgba(34,211,238,.55)' : 'none',
								}}
							>
								{it.n}
							</div>
							<span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 58, color: actif ? C.lumiere : C.pervenche}}>{it.texte}</span>
							<Coche p={lin(t, it.a + 0.45, it.a + 0.75)} taille={58} couleur={C.cyan} />
						</div>
					);
				})}
			</div>

			<Sinon t={t} />
			<MemeLaNuit t={t} />
		</AbsoluteFill>
	);
};

/** L'écran : une carte d'exemple. La photo, le prix et le bouton s'allument l'un après l'autre. */
const EcranCatalogue: React.FC<{t: number; nuit: number}> = ({t, nuit}) => {
	const encre = interpolateColors(nuit, [0, 1], [C.encreEcran, C.lumiere]);
	const trait = interpolateColors(nuit, [0, 1], [C.papierTrait, '#2a2c52']);
	const dessin = lin(t, T.photo, T.photo + 0.9, 0, 1, Easing.inOut(Easing.cubic));
	const remplie = lin(t, T.photo + 0.05, T.photo + 0.4);
	const reflet = lin(t, T.photo + 0.8, T.photo + 1.35, 0, 1, Easing.inOut(Easing.quad));
	const prix = interpolate(t, [T.prix, T.prix + 0.42], [0, PRIX_EXEMPLE], {...CL, easing: Easing.out(Easing.cubic)});
	const prixS = ressort(t, T.prix, 260, 14);
	const vert = lin(t, T.commander, T.commander + 0.25);
	const appui = t >= T.tap && t < T.tap + 0.18 ? 0.95 : 1;
	return (
		<>
			<BarreEtat heure={nuit > 0.5 ? '02:14' : '21:04'} encre={encre} />
			{nuit > 0.02 ? (
				<div style={{position: 'absolute', top: 54, right: 26, opacity: nuit, transform: `rotate(${((1 - nuit) * -40).toFixed(2)}deg)`}}>
					<Lune taille={46} />
				</div>
			) : null}
			<div style={{position: 'absolute', top: 64, left: 26, fontFamily: TEXTE, fontWeight: 800, fontSize: 28, color: encre}}>Catalogue des fêtes</div>

			{/* la photo */}
			<div
				style={{
					position: 'absolute',
					top: 114,
					left: 24,
					width: EC.l - 48,
					height: 330,
					borderRadius: 24,
					overflow: 'hidden',
					background: t < T.photo ? trait : 'radial-gradient(circle at 30% 25%, #b06bff, #5b3fd6 48%, #1e1a5c 100%)',
					border: t < T.photo ? `3px dashed ${C.gris}` : 'none',
					boxSizing: 'border-box',
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					boxShadow: `0 0 0 ${(5 * anneau(t, T.photo, T.prix)).toFixed(2)}px ${C.cyan}, 0 0 ${(50 * anneau(t, T.photo, T.prix)).toFixed(1)}px rgba(34,211,238,.7)`,
				}}
			>
				{t < T.photo ? <ImageVide taille={110} couleur={C.gris} /> : <Cadeau p={dessin} remplissage={remplie} taille={230} />}
				{t >= T.photo ? (
					<div
						style={{
							position: 'absolute',
							top: -60,
							bottom: -60,
							width: 90,
							left: `${(-30 + reflet * 160).toFixed(1)}%`,
							background: 'linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent)',
							transform: 'rotate(18deg)',
							opacity: reflet > 0 && reflet < 1 ? 1 : 0,
						}}
					/>
				) : null}
			</div>

			<div style={{position: 'absolute', top: 462, left: 26, fontFamily: TEXTE, fontWeight: 700, fontSize: 30, color: encre}}>Coffret cadeau</div>

			{/* le prix */}
			<div
				style={{
					position: 'absolute',
					top: 512,
					left: 24,
					height: 58,
					minWidth: 170,
					padding: '0 12px',
					borderRadius: 14,
					display: 'flex',
					alignItems: 'center',
					background: t < T.prix ? trait : 'transparent',
					boxShadow: `0 0 0 ${(4 * anneau(t, T.prix, T.commander)).toFixed(2)}px ${C.cyan}, 0 0 ${(40 * anneau(t, T.prix, T.commander)).toFixed(1)}px rgba(34,211,238,.7)`,
				}}
			>
				{t >= T.prix ? (
					<span
						style={{
							fontFamily: MONO,
							fontWeight: 700,
							fontSize: 42,
							color: interpolateColors(nuit, [0, 1], [C.prix, '#9fb0ff']),
							display: 'inline-block',
							transform: `scale(${(0.7 + 0.3 * prixS).toFixed(3)})`,
							transformOrigin: 'left center',
						}}
					>
						{millier(Math.round(prix / 100) * 100)} F
					</span>
				) : null}
			</div>

			{/* le bouton */}
			<div
				style={{
					position: 'absolute',
					top: BOUTON.y,
					left: BOUTON.x,
					width: BOUTON.l,
					height: BOUTON.h,
					borderRadius: BOUTON.h / 2,
					background: interpolateColors(vert, [0, 1], [trait, C.vertFonce]),
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					gap: 12,
					transform: `scale(${appui})`,
					boxShadow: `0 0 0 ${(4 * anneau(t, T.commander, T.sinon)).toFixed(2)}px ${C.cyan}, 0 0 ${(40 * anneau(t, T.commander, T.sinon)).toFixed(1)}px rgba(34,211,238,.7)`,
				}}
			>
				<div style={{opacity: vert, display: 'flex', alignItems: 'center', gap: 12}}>
					<Combine taille={34} couleur="#ffffff" />
					<span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 32, color: '#ffffff'}}>Commander</span>
				</div>
			</div>
			<Toucher t={t} a={T.tap} x={BOUTON.x + BOUTON.l * 0.62} y={BOUTON.y + BOUTON.h / 2} couleur={C.vertWa} />

			{/* les autres articles, devinés en bas */}
			<div style={{position: 'absolute', top: 708, left: 24, right: 24, display: 'flex', gap: 14}}>
				{[0, 1, 2].map((k) => (
					<div key={k} style={{flex: 1, height: 70, borderRadius: 16, background: t < T.photo ? trait : `linear-gradient(135deg, ${['#7b4dff', '#4f6fff', '#2bb7d9'][k]}, #1e1a5c)`, opacity: 0.9}} />
				))}
			</div>
		</>
	);
};

/** Le revers : s'il doit demander « c'est combien ? » et attendre, il va voir ailleurs. */
const Sinon: React.FC<{t: number}> = ({t}) => {
	if (t < T.sinon || t > T.nuit + 0.3) return null;
	const sortie = lin(t, T.nuit - 0.15, T.nuit + 0.15);
	const sb = ressort(t, T.sinon + 0.25, 260, 15);
	return (
		<AbsoluteFill style={{opacity: 1 - sortie}}>
			<div style={{position: 'absolute', top: 470, left: 60, right: 60}}>
				<Mots t={t} mots={phrase('S’il doit demander', T.sinon + 0.05, 0.08)} style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 58, color: C.lumiere}} />
			</div>
			<div style={{position: 'absolute', top: 580, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: Math.min(1, sb * 1.6), transform: `scale(${(0.5 + 0.5 * sb).toFixed(3)})`}}>
				<Bulle texte="C’est combien ?" heure="21:04" taille={56} />
			</div>
			<div style={{position: 'absolute', top: 770, left: 60, right: 60}}>
				<Mots t={t} mots={phrase('et attendre…', T.sinon + 0.5, 0.1)} style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 58, color: C.lumiere}} />
			</div>
			<div style={{position: 'absolute', top: 880, left: 60, right: 60}}>
				<Mots t={t} mots={phrase('il va voir ailleurs.', T.sinon + 0.7, 0.08)} style={{fontFamily: TITRE, fontWeight: 800, fontSize: 96, lineHeight: 1.06, color: C.cyan}} />
			</div>
		</AbsoluteFill>
	);
};

/** La promesse : ton catalogue montre les 3, même la nuit. */
const MemeLaNuit: React.FC<{t: number}> = ({t}) => {
	if (t < T.nuit) return null;
	const sp = ressort(t, T.nuit + 0.15, 200, 14);
	const sn = ressort(t, T.nuit + 0.5, 200, 14);
	return (
		<>
			<div style={{position: 'absolute', top: 1140, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: Math.min(1, sp * 1.6), transform: `scale(${(0.6 + 0.4 * sp).toFixed(3)})`}}>
				<div
					style={{
						fontFamily: TEXTE,
						fontWeight: 800,
						fontSize: 44,
						color: C.lumiere,
						padding: '26px 48px',
						borderRadius: 999,
						background: DEGRADE,
						boxShadow: '0 18px 60px rgba(79,111,255,.45)',
						whiteSpace: 'nowrap',
					}}
				>
					Ton catalogue montre les 3.
				</div>
			</div>
			<div
				style={{
					position: 'absolute',
					top: 1290,
					left: 0,
					right: 0,
					display: 'flex',
					justifyContent: 'center',
					alignItems: 'center',
					gap: 24,
					opacity: Math.min(1, sn * 1.6),
					transform: `translateY(${((1 - sn) * 50).toFixed(1)}px)`,
				}}
			>
				<Lune taille={80} />
				<span style={{fontFamily: TITRE, fontWeight: 800, fontSize: 76, color: C.lumiere}}>Même la nuit.</span>
			</div>
		</>
	);
};
