/**
 * ACTE I et II · l'histoire (0 → la narratrice) : la chambre de Cotonou, Paris, la lettre écrite et scellée,
 * l'envol le long du méridien, 3-2-1, MINUIT, la lettre lue. Chaque plan reçoit `debut` (seconde absolue du film)
 * et lit les phrases de la voix dans `minutage.json` : il suit la voix, jamais l'inverse.
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, staticFile} from 'remotion';
import {C, CIRES, DISTANCE_KM, HABIT, ITALIQUE, L, LETTRE, MINUIT, PLUME, SANS, TITRE} from './donnees';
import {accent, Ciel, Encre, Fumee, Fuite, Gerbe, Pluie, Poussiere, Rayons, titre} from './decor';
import {bruit, DOUX, ENTRE, flamme, mix, p, plein, SORT, T, useT, vie} from './outils';
import {EcranLettre, Telephone} from './telephone';
import {Cachet3D, Enveloppe3D, Etincelles3D, Halo3D, Lumieres, Scene3D} from './trois';

/** Une image d'ambiance de Mongazi (la vitrine), plein cadre, avec son lent mouvement de caméra. */
const Fond: React.FC<{src: string; zoom: [number, number]; k: number; origine?: string; style?: React.CSSProperties}> = ({src, zoom, k, origine = '50% 50%', style}) => (
	<Img
		src={staticFile('malettre-minuit/' + src)}
		style={{...plein, width: '100%', height: '100%', objectFit: 'cover', scale: String(mix(zoom[0], zoom[1], k)), transformOrigin: origine, ...style}}
	/>
);

/** Le téléphone de la photo (l'image « seuil »), en coordonnées du film : son écran, à allumer. */
const ECRAN_PHOTO = [
	[1268, 712],
	[1300, 697],
	[1597, 728],
	[1563, 757],
].map(([x, y]) => [x * (1920 / 1672), y * (1080 / 941)]);
const CENTRE_PHOTO = [1430 * (1920 / 1672), 728 * (1080 / 941)];

/* ── 1 · L'ACCROCHE : une chambre noire à Cotonou, un téléphone qui s'allume, 23:59:57, et le temps se fige ── */
export const Accroche: React.FC<{debut: number}> = ({debut}) => {
	const t = useT();
	const allume = p(t, 0.22, 0.6, SORT);
	const gros = p(t, 0.95, 1.3, DOUX);
	const fige = p(t, 2.85, 3.2, ENTRE);
	const [cx, cy] = CENTRE_PHOTO;
	return (
		<AbsoluteFill style={{background: C.nuit3, filter: `grayscale(${fige}) contrast(${1 + fige * 0.2})`}}>
			{/* la chambre, large */}
			<AbsoluteFill style={{opacity: 1 - gros}}>
				<Fond src="seuil.jpg" zoom={[1.0, 1.07]} k={p(t, 0, 1.3, DOUX)} origine={`${cx}px ${cy}px`} style={{filter: `brightness(${0.62 + 0.3 * allume})`}} />
				<svg width={1920} height={1080} style={{...plein, mixBlendMode: 'screen'}}>
					<defs>
						<filter id="flou-ecran">
							<feGaussianBlur stdDeviation={3} />
						</filter>
					</defs>
					<polygon points={ECRAN_PHOTO.map((q) => q.join(',')).join(' ')} fill="#ffe6d8" opacity={allume * 0.9} filter="url(#flou-ecran)" />
				</svg>
				<div style={{...plein, mixBlendMode: 'screen', opacity: allume * 0.75, background: `radial-gradient(ellipse 420px 220px at ${cx}px ${cy - 30}px, rgba(255,205,190,.55) 0%, rgba(255,170,160,.18) 45%, transparent 75%)`}} />
				<div style={{...plein, mixBlendMode: 'screen', opacity: allume * 0.35, background: `radial-gradient(ellipse 900px 520px at ${cx}px 160px, rgba(190,170,255,.18) 0%, transparent 70%)`}} />
			</AbsoluteFill>
			{/* le gros plan : la vraie lettre, scellée, à trois secondes de minuit */}
			<AbsoluteFill style={{opacity: gros}}>
				<Fond src="seuil.jpg" zoom={[1.25, 1.3]} k={p(t, 1, 3.2)} origine={`${cx}px ${cy}px`} style={{filter: 'blur(18px) brightness(.45)'}} />
				<div style={{position: 'absolute', left: 330, top: 158, perspective: 1600}}>
					<div style={{rotate: '0deg', transform: `rotateY(${mix(-24, -14, p(t, 1, 3.2))}deg) rotateX(${mix(10, 6, p(t, 1, 3.2))}deg)`, transformStyle: 'preserve-3d', scale: String(mix(0.9, 1, p(t, 0.95, 3.2, DOUX)))}}>
						<Telephone largeur={420} lueur={0.6}>
							<EcranLettre largeur={420 - 29} t={t} reste={3} heure={0} />
						</Telephone>
					</div>
				</div>
			</AbsoluteFill>
			{/* les mots, sur un voile (la fenêtre derrière est claire) */}
			<div style={{...plein, background: 'radial-gradient(ellipse 760px 420px at 1400px 420px, rgba(8,5,12,.55) 0%, transparent 70%)', opacity: 1 - gros * 0.6}} />
			<div style={{position: 'absolute', left: 1010, top: 330, width: 820}}>
				<div style={{...accent(30, C.grisNuit), opacity: vie(t, 0.3, 0.8, 2.8, 3.1)}}>Cotonou, 23 h 59</div>
				<Encre texte="Dans trois secondes…" debut={L('k1').debut - 0.05} style={{...titre(92), marginTop: 26}} />
				<Encre texte="ma mère va pleurer." debut={L('k2').debut - 0.05} pas={0.08} style={{...accent(84), marginTop: 18}} />
			</div>
			{/* le temps se fige, puis la bande rembobine */}
			<div style={{...plein, opacity: fige * 0.85, background: 'repeating-linear-gradient(90deg, rgba(244,237,224,.06) 0px, transparent 2px, transparent 9px)', mixBlendMode: 'screen'}} />
		</AbsoluteFill>
	);
};

/* ── 2 · PARIS : la table de Koffi, la bougie ; « Paris », et le méridien qui descend ── */
export const Paris: React.FC<{debut: number}> = ({debut}) => {
	const t = useT();
	const entree = p(t, debut, debut + 0.35);
	const f = flamme(t);
	const meridien = p(t, L('k5').debut + 0.1, L('k5').debut + 1.0, SORT);
	return (
		<AbsoluteFill style={{background: C.nuit3, opacity: entree}}>
			<Fond src="heros.jpg" zoom={[1.08, 1.2]} k={p(t, debut, debut + 4.3, DOUX)} origine="80% 30%" style={{filter: `brightness(${0.75 * f}) saturate(1.05)`}} />
			<div style={{...plein, mixBlendMode: 'screen', opacity: 0.55 * f, background: 'radial-gradient(ellipse 380px 300px at 1795px 150px, rgba(255,190,120,.5) 0%, rgba(255,160,90,.12) 50%, transparent 75%)'}} />
			<Poussiere n={34} force={0.7} graine="paris" />
			<div style={{position: 'absolute', left: 140, top: 300, width: 900}}>
				<Encre texte="Elle a 60 ans ce soir." debut={L('k3').debut - 0.05} style={titre(96)} />
				<div style={{...accent(40, C.grisNuit), marginTop: 22, opacity: p(t, L('k4').debut + 0.3, L('k4').debut + 0.9)}}>et lui…</div>
			</div>
			<div style={{position: 'absolute', left: 140, top: 640, opacity: p(t, L('k5').debut, L('k5').debut + 0.4)}}>
				<div style={{...titre(210, C.orDoux), letterSpacing: '0.02em'}}>Paris</div>
				<div style={{fontFamily: SANS, fontSize: 24, letterSpacing: '0.3em', color: C.grisNuit, marginTop: 6}}>48,86° N · 2,35° E</div>
			</div>
			{/* le méridien : Paris et Cotonou sont presque sur la même ligne */}
			<div style={{position: 'absolute', left: 1000, top: 0, width: 2, height: 1080 * meridien, background: `linear-gradient(${C.orDoux}, ${C.or}00)`, boxShadow: `0 0 12px ${C.orDoux}`}} />
		</AbsoluteFill>
	);
};

/* ── 3 · LA LETTRE S'ÉCRIT : la plume, la bougie ; le titre de la vraie lettre paraît à la main ── */
export const Ecriture: React.FC<{debut: number}> = ({debut}) => {
	const t = useT();
	const f = flamme(t, 'b2');
	const ecrit = p(t, L('k6').debut + 0.2, L('k6').debut + 1.6, (x) => x);
	return (
		<AbsoluteFill style={{background: C.nuit3, opacity: p(t, debut, debut + 0.3)}}>
			<Fond src="plume.jpg" zoom={[1.05, 1.16]} k={p(t, debut, debut + 2.2, DOUX)} origine="62% 72%" style={{filter: `brightness(${0.85 * f})`}} />
			<div style={{...plein, mixBlendMode: 'screen', opacity: 0.4 * f, background: 'radial-gradient(ellipse 300px 260px at 1640px 120px, rgba(255,190,120,.55) 0%, transparent 70%)'}} />
			<div
				style={{
					position: 'absolute',
					left: 120,
					top: 330,
					fontFamily: PLUME,
					fontSize: 112,
					color: C.papier,
					textShadow: '0 4px 30px rgba(0,0,0,.6)',
					clipPath: `inset(0 ${100 - ecrit * 100}% 0 0)`,
				}}
			>
				{LETTRE.titre}
			</div>
			<div style={{position: 'absolute', left: 126, top: 500, ...accent(34, C.grisNuit), opacity: p(t, L('k6').debut + 1.0, L('k6').debut + 1.5)}}>
				pour {LETTRE.pour}, de {LETTRE.de}
			</div>
		</AbsoluteFill>
	);
};

/* ── 4 · LE CACHET : la main presse le sceau dans la cire (la fumée), puis la cire en vrai relief ── */
export const Sceau: React.FC<{debut: number}> = ({debut}) => {
	const t = useT();
	const impact = L('k7').debut + 0.15;
	const choc = Math.max(0, 1 - Math.abs(t - impact) / 0.12);
	const relief = p(t, impact + 0.62, impact + 0.95, DOUX);
	const tour = p(t, impact + 0.6, debut + 2.1, (x) => x);
	return (
		<AbsoluteFill style={{background: C.nuit3, opacity: p(t, debut, debut + 0.2)}}>
			<AbsoluteFill style={{opacity: 1 - relief, translate: `${bruit('sh', t, 9) * choc * 10}px ${bruit('sv', t, 9) * choc * 8}px`}}>
				<Fond src="promesses.jpg" zoom={[1.06, 1.14]} k={p(t, debut, debut + 1.2)} origine="44% 76%" style={{filter: `brightness(${0.9 + choc * 0.25})`}} />
				<Fumee x={760} y={520} debut={debut} force={0.9} />
			</AbsoluteFill>
			<AbsoluteFill style={{opacity: relief, background: `radial-gradient(110% 90% at 50% 45%, ${C.nuit2} 0%, ${C.nuit3} 70%)`}}>
				<Scene3D camera={[mix(0.6, -0.5, tour), mix(2.6, 2.3, tour), mix(2.2, 2.0, tour)]} vise={[0, 0.05, 0]} fov={26} expo={0.85}>
					<Lumieres position={[2.4, 3.2, 1.0]} cle={20} />
					<group rotation={[-Math.PI / 2, 0, 0]}>
						<Enveloppe3D>
							<group rotation={[Math.PI / 2, 0, 0]}>
								<Cachet3D echelle={0.42} ecrase={1} />
							</group>
						</Enveloppe3D>
					</group>
				</Scene3D>
				<Fumee x={1000} y={540} debut={impact + 0.6} force={0.45} />
			</AbsoluteFill>
			<div style={{...plein, background: 'linear-gradient(20deg, rgba(8,5,12,.82) 0%, rgba(8,5,12,.45) 32%, transparent 55%)'}} />
			<div style={{position: 'absolute', left: 140, bottom: 150, width: 1200}}>
				<Encre texte="Scellée jusqu’à" debut={L('k7').debut + 0.05} style={titre(84)} />
				<Encre texte="minuit pile." debut={L('k7').debut + 0.75} pas={0.1} style={{...accent(96), marginTop: 6}} />
			</div>
		</AbsoluteFill>
	);
};

/* ── 5 · L'ENVOL : de Paris à Cotonou, le long du même méridien, la lettre file dans la nuit ── */
/* Le vol : la lettre plonge depuis le haut, ralentit, et SE POSE au-dessus de « Cotonou ». Avec une courbe
   symétrique, elle traversait l'écran en 0,3 s et finissait sur le mot (planche du MP4, 2026-10-22). */
const ATTERRIT = Easing.bezier(0.2, 0.55, 0.25, 1);
const UNITE_PX = 540 / (7.5 * Math.tan((15 * Math.PI) / 180)); /* caméra à 7,5, champ de 30° : pixels par unité */
const VOL_HAUT = 2.46; /* au-dessus du cadre */
const VOL_BAS = -0.56; /* le centre de la lettre à 690 px : le mot « Cotonou » reste lisible */
export const Envol: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const k = p(t, debut, fin, (x) => x);
	const vol = p(t, debut + 0.02, fin - 0.12, ATTERRIT);
	const hauteur = mix(VOL_HAUT, VOL_BAS, vol);
	return (
		<AbsoluteFill style={{background: C.nuit3}}>
			<Fond src="nuit.jpg" zoom={[1.22, 1.12]} k={k} origine="50% 20%" style={{translate: `0 ${mix(-60, 40, k)}px`, filter: 'brightness(.9)'}} />
			<Ciel n={160} force={0.8} />
			<div style={{position: 'absolute', left: 959, top: 0, width: 2, height: 1080, background: `linear-gradient(${C.orDoux}cc, ${C.orDoux}55)`, boxShadow: `0 0 16px ${C.orDoux}`}} />
			{/* les mots s'effacent AVANT le fondu vers le téléphone : sinon « Paris » se lisait à travers son écran */}
			<div style={{opacity: 1 - p(t, fin - 0.32, fin - 0.12)}}>
				<div style={{position: 'absolute', left: 1000, top: 168, ...titre(64, C.papier)}}>Paris</div>
				<div style={{position: 'absolute', left: 1000, bottom: 168, ...titre(64, C.orDoux)}}>Cotonou</div>
				<div style={{position: 'absolute', left: 1000, top: 506, fontFamily: SANS, fontSize: 26, letterSpacing: '0.3em', color: C.grisNuit}}>{DISTANCE_KM}</div>
			</div>
			{/* la traîne d'or */}
			<div style={{position: 'absolute', left: 958, top: 0, width: 4, height: Math.max(0, 540 - hauteur * UNITE_PX), background: `linear-gradient(transparent, ${C.orPale})`, filter: 'blur(2px)'}} />
			<Poussiere n={40} force={0.8} graine="envol" />
			<Scene3D camera={[0, 0, 7.5]} fov={30} expo={1.0} style={{filter: `blur(${Math.abs(Math.sin(vol * Math.PI)) * 1.5}px)`}}>
				<Lumieres position={[2.5, 2.5, 4]} cle={40} />
				<group position={[0, hauteur, 0]} rotation={[0.25 + vol * 0.5, -0.5 + vol * 1.0, 0.15 - vol * 0.3]} scale={0.46}>
					<Enveloppe3D>
						<group rotation={[Math.PI / 2, 0, 0]}>
							<Cachet3D echelle={0.3} />
						</group>
					</Enveloppe3D>
				</group>
			</Scene3D>
		</AbsoluteFill>
	);
};

/* ── 6 · COTONOU, 23 h 59 : retour au téléphone ; 3, 2, 1 ; le cœur ── */
export const Retour: React.FC<{debut: number}> = ({debut}) => {
	const t = useT();
	const [cx, cy] = CENTRE_PHOTO;
	const pousse = p(t, debut, MINUIT, DOUX);
	const battement = [MINUIT - 2.88, MINUIT - 1.88, MINUIT - 0.88].reduce((a, b) => a + Math.max(0, 1 - Math.abs(t - b) / 0.18), 0);
	return (
		<AbsoluteFill style={{background: C.nuit3, opacity: p(t, debut, debut + 0.25)}}>
			<Fond src="seuil.jpg" zoom={[1.3, 1.42]} k={pousse} origine={`${cx}px ${cy}px`} style={{filter: `blur(20px) brightness(${0.42 - pousse * 0.18})`}} />
			<div style={{position: 'absolute', left: 220, top: 420, ...accent(40, C.grisNuit)}}>Cotonou, 23 h 59</div>
			<div style={{position: 'absolute', left: '50%', top: 158, translate: '-50% 0', perspective: 1700}}>
				<div style={{transform: `rotateY(${mix(-12, 0, pousse)}deg) rotateX(${mix(6, 0, pousse)}deg)`, scale: String(mix(1, 1.1, pousse) * (1 + battement * 0.012)), transformOrigin: '50% 40%'}}>
					<Telephone largeur={420} lueur={0.5 + pousse * 0.3}>
						<EcranLettre largeur={420 - 29} t={t} reste={MINUIT - t} heure={0} />
					</Telephone>
				</div>
			</div>
			<div style={{...plein, background: `radial-gradient(ellipse 60% 70% at 50% 50%, transparent 40%, rgba(5,3,8,${0.55 + pousse * 0.3}) 100%)`, opacity: 1}} />
		</AbsoluteFill>
	);
};

/* ── 7 · MINUIT : la cire s'embrase, la lumière jaillit, on plonge, le cachet éclate, la carte sort ── */
export const Minuit: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const m = MINUIT;
	const heure = p(t, m, m + 0.35, SORT);
	const plonge = p(t, m + 0.45, m + 0.95, ENTRE);
	const blanc = vie(t, m + 0.78, m + 0.92, m + 0.95, m + 1.25);
	const presse = vie(t, m + 0.82, m + 0.88, m + 0.92, m + 1.0);
	const eclat = p(t, m + 1.0, m + 1.9, (x) => x);
	const ouvre = p(t, m + 1.55, m + 2.35, DOUX);
	const sort = p(t, m + 2.05, m + 3.05, DOUX);
	const versLettre = p(t, fin - 0.35, fin, ENTRE);
	const camY = mix(0.1, 0.9, sort), camZ = mix(5.2, 4.2, sort);
	return (
		<AbsoluteFill style={{background: C.nuit3}}>
			{/* le téléphone s'embrase, puis on plonge dedans */}
			<AbsoluteFill style={{opacity: 1 - p(t, m + 0.9, m + 1.0)}}>
				<Fond src="seuil.jpg" zoom={[1.42, 1.5]} k={heure} origine={`${CENTRE_PHOTO[0]}px ${CENTRE_PHOTO[1]}px`} style={{filter: `blur(20px) brightness(${0.24 + heure * 0.35})`}} />
				<Gerbe force={heure * (1 - plonge) * 0.95} tour={t * 12} origine={[0.5, 0.5]} />
				<Rayons x="50%" y="50%" force={heure * 0.8} tour={t * 20} />
				<div style={{position: 'absolute', left: '50%', top: 158, translate: '-50% 0', scale: String(mix(1.1, 8, plonge)), transformOrigin: '50% 40%', filter: `blur(${plonge * 14}px)`}}>
					<Telephone largeur={420} lueur={0.8 + heure}>
						<EcranLettre largeur={420 - 29} t={t} reste={0} heure={heure} />
					</Telephone>
				</div>
				<div style={{...plein, background: `repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,240,210,.0) 0deg, rgba(255,240,210,.22) 1deg, rgba(255,240,210,0) 3deg)`, opacity: plonge * 0.9, mixBlendMode: 'screen', filter: 'blur(3px)'}} />
			</AbsoluteFill>
			{/* teinte 20 : ambre et corail, la couleur de la cire. ⚠️ 335 rendait du VERT-JAUNE (74°) : la matrice du shader
			    est écrite en colonnes, la rotation tourne à l'envers de l'intuition (mesuré le 2026-10-22, voir `Fuite`). */}
			<Fuite progres={p(t, m - 0.05, m + 1.4, (x) => x)} graine={3} teinte={20} force={0.75} />
			{/* le monde de la lettre, en 3D */}
			<AbsoluteFill style={{opacity: p(t, m + 0.9, m + 1.02) * (1 - versLettre), background: `radial-gradient(100% 90% at 50% 45%, #2a2030 0%, ${C.nuit3} 72%)`}}>
				<Poussiere n={50} force={0.9} graine="minuit" />
				<Scene3D camera={[0, camY, camZ]} vise={[0, mix(0, 0.85, sort), 0]} fov={28} expo={1.0}>
					{/* l'ombre s'efface pendant que les éclats volent (sinon : des taches grises), et revient pour le rabat */}
					<Lumieres position={[2.2, 2.6, 3.6]} cle={36} ombre={1 - vie(t, m + 1.08, m + 1.4, m + 1.9, m + 2.2)} />
					<group rotation={[-0.1, 0, 0]}>
						<Enveloppe3D ouvre={ouvre} sort={sort}>
							{eclat < 1 && (
								<group rotation={[Math.PI / 2, 0, 0]}>
									<Cachet3D echelle={0.33} lueur={eclat > 0 ? Math.max(0, 0.3 - eclat * 1.5) : 1} eclat={eclat > 0 ? Math.max(0.001, eclat) : 0} />
								</group>
							)}
						</Enveloppe3D>
					</group>
					<Halo3D position={[0, -0.3, 0.3]} taille={2.4} couleur={CIRES[HABIT.cire].lumiere} force={(1 - eclat) * 0.85} />
					<Halo3D position={[0, -0.3, 0.4]} taille={5 * eclat + 0.5} couleur="#ffe2b0" force={vie(t, m + 1.0, m + 1.08, m + 1.15, m + 1.7)} />
					<Etincelles3D t={t - (m + 1.0)} origine={[0, -0.3, 0.3]} n={90} />
				</Scene3D>
				<div style={{position: 'absolute', left: '50%', top: '57%', width: 240 * (1 + presse * 0.4), height: 240 * (1 + presse * 0.4), translate: '-50% -50%', borderRadius: '50%', border: `3px solid rgba(255,230,200,${presse * 0.8})`}} />
				<Pluie type="etoiles" debut={m + 1.05} echelle={3.6} graine="etoiles-minuit" />
			</AbsoluteFill>
			<div style={{...plein, background: '#fff6e8', opacity: blanc * 0.9, mixBlendMode: 'screen'}} />
		</AbsoluteFill>
	);
};

/* ── 8 · LA LETTRE : l'encre sèche ; la phrase que Koffi lit est au point ; puis la phrase qui fait pleurer s'allume ── */
export const Lettre: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const entree = p(t, debut, debut + 0.5, SORT);
	const sortie = p(t, fin - 0.45, fin, ENTRE);
	const lue = L('k9');
	const phare = p(t, lue.fin - 0.7, lue.fin + 0.1, SORT);
	const mots = (texte: string, depart: number, pas: number, mise: (i: number) => React.CSSProperties = () => ({})) =>
		texte.split(' ').map((w, i) => {
			const k = p(t, depart + i * pas, depart + i * pas + 0.35);
			return (
				<span key={i} style={{display: 'inline-block', whiteSpace: 'pre', opacity: k, filter: `blur(${(1 - k) * 6}px)`, ...mise(i)}}>
					{w + ' '}
				</span>
			);
		});
	const [p1, p2] = LETTRE.paragraphes;
	const [avant1, apres1] = [LETTRE.lue, p1.slice(LETTRE.lue.length).trim()];
	const i2 = p2.indexOf(LETTRE.phare);
	const avant2 = p2.slice(0, i2).trim(), apres2 = p2.slice(i2 + LETTRE.phare.length).trim();
	const net = (k: number) => ({filter: `blur(${k * 2.6}px)`, opacity: 1 - k * 0.45});
	const flouLue = 1 - p(t, lue.debut - 0.2, lue.debut + 0.3);
	const flouPhare = 1 - phare;
	return (
		<AbsoluteFill style={{background: `radial-gradient(90% 80% at 50% 40%, #2c2132 0%, ${C.nuit3} 75%)`}}>
			<Poussiere n={40} force={0.8} graine="lettre" />
			<div style={{position: 'absolute', left: '50%', top: 40, translate: '-50% 0', perspective: 2200, scale: String(mix(1, 0.6, sortie)), opacity: entree * (1 - sortie), filter: `blur(${sortie * 10}px)`}}>
				<div
					style={{
						width: 1180,
						padding: '56px 84px 50px',
						boxSizing: 'border-box',
						background: `linear-gradient(168deg, #f8f1e4 0%, ${C.papier} 45%, ${C.papier2} 100%)`,
						borderRadius: 10,
						boxShadow: '0 60px 140px rgba(0,0,0,.6), inset 0 0 120px rgba(160,120,70,.12)',
						transform: `rotateX(${mix(18, 4, entree)}deg) translateY(${mix(80, 0, entree)}px)`,
						color: C.encre,
					}}
				>
					<div style={{fontFamily: SANS, fontSize: 22, fontWeight: 700, letterSpacing: '0.3em', textTransform: 'uppercase', color: CIRES[HABIT.cire].cire, textAlign: 'center', opacity: p(t, debut + 0.15, debut + 0.5)}}>{LETTRE.occasion}</div>
					<div style={{fontFamily: TITRE, fontSize: 64, textAlign: 'center', marginTop: 10}}>{mots(LETTRE.titre, debut + 0.25, 0.06)}</div>
					<div style={{width: 120, height: 4, margin: '22px auto 30px', background: C.or, borderRadius: 2, scale: `${p(t, debut + 0.6, debut + 1.0)} 1`}} />
					<div style={{fontFamily: ITALIQUE, fontSize: 33, lineHeight: 1.55}}>
						<span style={{...net(flouLue * 0.6 + phare * 0.9)}}>{mots(avant1, debut + 0.7, 0.03, () => ({}))}</span>
						<span style={{...net(Math.min(1, 0.35 + phare))}}>{mots(apres1, debut + 1.2, 0.03)}</span>
					</div>
					<div style={{fontFamily: ITALIQUE, fontSize: 33, lineHeight: 1.55, marginTop: 18}}>
						<span style={{...net(0.55 + phare * 0.45)}}>{mots(avant2, debut + 1.5, 0.025)}</span>{' '}
						<span style={{position: 'relative', isolation: 'isolate', ...net(Math.max(0, flouPhare * 0.55)), color: phare > 0.5 ? '#6d4a0e' : C.encre}}>
							<span style={{position: 'absolute', left: -6, right: -6, top: '58%', height: '0.55em', translate: '0 -50%', background: `linear-gradient(90deg, ${C.orDoux}88, ${C.orPale}aa)`, borderRadius: 4, scale: `${phare} 1`, transformOrigin: 'left', zIndex: -1}} />
							{mots(LETTRE.phare, debut + 2.1, 0.03)}
						</span>{' '}
						<span style={{...net(0.55 + phare * 0.45)}}>{mots(apres2, debut + 2.4, 0.025)}</span>
					</div>
					<div style={{textAlign: 'right', marginTop: 26, ...net(0.4 + phare * 0.5)}}>
						<div style={{fontFamily: ITALIQUE, fontStyle: 'italic', fontSize: 30, color: C.gris, opacity: p(t, debut + 2.7, debut + 3.0)}}>{LETTRE.formule}</div>
						<div style={{fontFamily: PLUME, fontSize: 64, color: C.encre, opacity: p(t, debut + 2.9, debut + 3.3), marginTop: -4}}>{LETTRE.de}</div>
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
