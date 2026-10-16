/**
 * LES TROIS TEMPS (sombre) : visage, corps, lèvres. Chaque temps a SA signature,
 * tirée du mot que dit la voix, et l'icône du vocabulaire de sa vitrine :
 *  · « Un visage qui s'illumine. » : une lumière qui S'ÉPANOUIT au centre, l'éclat
 *    (l'icône de sa section Visage) qui scintille ;
 *  · « Un corps qui respire. » : des ondes qui RESPIRENT (elles s'ouvrent et se
 *    referment au rythme d'une mesure), la feuille (sa section Corps) ;
 *  · « Et des lèvres repulpées… » : le contour des lèvres se TRACE en or, puis se
 *    remplit et se repulpe. Sur l'ARRÊT de la musique (un temps de silence), une
 *    seringue se dessine. Sur LA RELANCE, elle éclate en grains d'or, et « sans une
 *    seule piqûre » s'impose. Puis SA vraie fiche Hyaluropen remonte (sa vitrine).
 * Les prix sont ceux de la vitrine (`faits.ts`), jamais retapés.
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, staticFile} from 'remotion';
import {C, VOIX} from '../donnees';
import {FAITS} from '../faits';
import {Fond, Grains} from '../Fond';
import {MOTS, MUSIQUE, REPLIQUES} from '../minutage';
import {Etiquette, h, mix, Mots, p, ressort} from '../outils';
import {TEXTE} from '../polices';

const debutMot = (replique: string, debut: string, defaut: number) =>
	MOTS.find((m) => m.replique === replique && m.mot.toLowerCase().startsWith(debut))?.debut ?? defaut;

/** L'étiquette de prix, comme une pastille de la vitrine. */
const Prix: React.FC<{nom: string; prix: string; e: number}> = ({nom, prix, e}) => (
	<div
		style={{
			display: 'inline-flex',
			alignItems: 'center',
			gap: 18,
			padding: '18px 34px',
			borderRadius: 999,
			border: `1.5px solid rgba(212,175,114,${0.6 * e})`,
			background: `rgba(42,20,32,${0.55 * e})`,
			opacity: e,
			transform: `translateY(${(1 - e) * 22}px)`,
			fontFamily: TEXTE,
			fontSize: 30,
			color: C.creme,
			letterSpacing: '0.04em',
		}}
	>
		<span>{nom}</span>
		<span style={{width: 7, height: 7, background: C.or, transform: 'rotate(45deg)'}} />
		<span style={{color: C.or, fontWeight: 600}}>{prix}</span>
	</div>
);

/** L'éclat à quatre branches de sa section Visage. */
const Eclat: React.FC<{taille: number; e: number; rot: number}> = ({taille, e, rot}) => (
	<svg width={taille} height={taille} viewBox="-50 -50 100 100" style={{transform: `rotate(${rot}deg) scale(${e})`, overflow: 'visible'}}>
		<defs>
			<radialGradient id="eclat-g">
				<stop offset="0%" stopColor="#fffaf0" />
				<stop offset="60%" stopColor="#f0d49a" />
				<stop offset="100%" stopColor="#c99a4e" />
			</radialGradient>
		</defs>
		<path d="M0,-48 C4,-12 12,-4 48,0 C12,4 4,12 0,48 C-4,12 -12,4 -48,0 C-12,-4 -4,-12 0,-48 Z" fill="url(#eclat-g)" />
		<path d="M0,-22 C2,-5 5,-2 22,0 C5,2 2,5 0,22 C-2,5 -5,2 -22,0 C-5,-2 -2,-5 0,-22 Z" fill="#fffaf0" opacity={0.9} transform="rotate(45) translate(34 -34) scale(.42)" />
	</svg>
);

/** La feuille de sa section Corps. */
const Feuille: React.FC<{taille: number; balance: number}> = ({taille, balance}) => (
	<svg width={taille} height={taille} viewBox="-50 -50 100 100" style={{transform: `rotate(${balance}deg)`, overflow: 'visible'}}>
		<path d="M0,44 C-30,20 -34,-18 0,-46 C34,-18 30,20 0,44 Z" fill="none" stroke="#f0d49a" strokeWidth={3.2} />
		<path d="M0,44 L0,-38 M0,10 L-14,-4 M0,-6 L13,-18 M0,24 L12,12" stroke="#f0d49a" strokeWidth={2.4} strokeLinecap="round" fill="none" />
	</svg>
);

// Le contour des lèvres (dessiné ici : c'est une icône, pas une photo de cliente).
const LEVRE_HAUT = 'M-200,0 C-150,-26 -95,-82 -40,-70 C-18,-66 -8,-46 0,-44 C8,-46 18,-66 40,-70 C95,-82 150,-26 200,0';
const LEVRE_BAS = 'M-200,0 C-130,58 -70,96 0,96 C70,96 130,58 200,0';
const LIGNE = 'M-188,2 C-110,18 -50,8 0,14 C50,8 110,18 188,2';
const SERINGUE = 'M-140,-6 L60,-6 L60,6 L-140,6 Z M60,-14 L76,-14 L76,14 L60,14 Z M76,-2 L170,-2 L170,2 L76,2 Z M-140,-20 L-140,20 M-160,-12 L-160,12 M-160,0 L-140,0';

export const TroisTemps: React.FC<{t: number}> = ({t}) => {
	const [va, vb] = REPLIQUES.visage;
	const [ca, cb] = REPLIQUES.corps;
	const [la] = REPLIQUES.levres;
	const [pa] = REPLIQUES.piqure;
	const ARRET = MUSIQUE.arret;
	const RELANCE = MUSIQUE.relance;

	// visage : la lumière s'épanouit à « s'illumine »
	const tIllu = debutMot('visage', "'illumine", vb - 0.5) - 0.1;
	const eVisage = p(t, va - 0.2, va + 0.4) * (1 - p(t, ca - 0.45, ca - 0.1));
	const eclot = p(t, tIllu - 0.2, tIllu + 0.9, Easing.out(Easing.cubic));
	// corps : la respiration (une mesure à 90 BPM)
	const eCorps = p(t, ca - 0.3, ca + 0.3) * (1 - p(t, la - 0.4, la - 0.05));
	const souffle = 0.5 + 0.5 * Math.sin(((t - ca) / 2.667) * Math.PI * 2 - Math.PI / 2);
	// lèvres
	const eLevres = p(t, la - 0.3, la + 0.2); // jusqu'au bout : c'est la vague qui l'emporte
	const trace = p(t, la - 0.1, la + 1.0, Easing.inOut(Easing.cubic));
	const tRep = debutMot('levres', 'repulp', la + 0.6);
	const repulpe = ressort(t, tRep + 0.05, {damping: 8, stiffness: 120, mass: 0.7});
	const seringue = p(t, ARRET - 0.25, ARRET + 0.15) * (t < RELANCE ? 1 : 0);
	const eclate = p(t, RELANCE, RELANCE + 1.1, Easing.out(Easing.quad));
	const flash = 0.6 * p(t, RELANCE - 0.02, RELANCE + 0.04) * (1 - p(t, RELANCE + 0.04, RELANCE + 0.28));
	const suspense = p(t, ARRET - 0.1, ARRET + 0.2) * (1 - p(t, RELANCE, RELANCE + 0.15));
	const coup = t >= RELANCE ? Math.exp(-(t - RELANCE) * 9) : 0;
	const fiche = ressort(t, pa + 0.4, {damping: 16, stiffness: 100, mass: 0.8});

	return (
		<AbsoluteFill>
			<Fond t={t} lumiere={{x: 540, y: 720}} />
			<Grains t={t} densite={0.85 - 0.5 * suspense} />

			{/* ---------- VISAGE */}
			{eVisage > 0 ? (
				<AbsoluteFill style={{opacity: eVisage}}>
					<div
						style={{
							position: 'absolute',
							left: 540 - 700,
							top: 700 - 700,
							width: 1400,
							height: 1400,
							borderRadius: '50%',
							background: 'radial-gradient(circle, rgba(255,246,220,.9) 0%, rgba(240,212,154,.45) 18%, rgba(212,175,114,.16) 40%, transparent 66%)',
							transform: `scale(${mix(0.15, 1.05, eclot)})`,
							opacity: 0.25 + 0.75 * eclot,
						}}
					/>
					<div style={{position: 'absolute', left: 540 - 130, top: 700 - 130}}>
						<Eclat taille={260} e={ressort(t, va, {damping: 10, stiffness: 120})} rot={(t - va) * 18} />
					</div>
					<div style={{position: 'absolute', left: 60, right: 60, top: 1080, textAlign: 'center'}}>
						<Mots t={t} texte={VOIX.visage} a={va} b={vb} taille={104} accent={["s'illumine"]} interligne={1.02} />
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, top: 1420, textAlign: 'center'}}>
						<Prix nom={FAITS.soins.visage.nom} prix={FAITS.soins.visage.prix} e={p(t, va + 0.55, va + 1.0)} />
					</div>
				</AbsoluteFill>
			) : null}

			{/* ---------- CORPS */}
			{eCorps > 0 ? (
				<AbsoluteFill style={{opacity: eCorps}}>
					{[0, 1, 2, 3, 4, 5].map((i) => {
						const r = 120 + i * 95 + souffle * (26 + i * 10);
						return (
							<div
								key={i}
								style={{
									position: 'absolute',
									left: 540 - r * 1.15,
									top: 700 - r * 0.8,
									width: r * 2.3,
									height: r * 1.6,
									borderRadius: '50%',
									border: `${2 - i * 0.2}px solid rgba(240,212,154,${0.55 - i * 0.08})`,
									opacity: p(t, ca + i * 0.08, ca + 0.5 + i * 0.08),
								}}
							/>
						);
					})}
					<div style={{position: 'absolute', left: 540 - 85, top: 700 - 85}}>
						<Feuille taille={170} balance={Math.sin((t - ca) * 2.3) * 6} />
					</div>
					<div style={{position: 'absolute', left: 60, right: 60, top: 1080, textAlign: 'center'}}>
						<Mots t={t} texte={VOIX.corps} a={ca + 0.45} b={cb} taille={104} accent={['respire']} interligne={1.02} />
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, top: 1420, textAlign: 'center'}}>
						<Prix nom={FAITS.soins.corps.nom} prix={FAITS.soins.corps.prix} e={p(t, ca + 0.7, ca + 1.15)} />
					</div>
				</AbsoluteFill>
			) : null}

			{/* ---------- LÈVRES, puis SANS UNE SEULE PIQÛRE */}
			{eLevres > 0 ? (
				<AbsoluteFill style={{opacity: eLevres, transform: `scale(${1 + 0.025 * coup})`}}>
					<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
						<defs>
							<linearGradient id="levres-or" x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stopColor="#f6dfa8" />
								<stop offset="100%" stopColor="#b8873c" />
							</linearGradient>
							<linearGradient id="levres-rose" x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stopColor="#e7a8c0" />
								<stop offset="100%" stopColor="#9c3f66" />
							</linearGradient>
						</defs>
						<g transform={`translate(540 ${t < RELANCE ? 560 : mix(560, 470, p(t, RELANCE, RELANCE + 0.5))}) scale(${1.25} ${1.25 * (1 + 0.14 * Math.min(1.2, repulpe))})`}>
							<path d={`${LEVRE_HAUT} ${LEVRE_BAS.replace('M-200,0', 'L-200,0')}`} fill="url(#levres-rose)" opacity={0.85 * p(t, tRep, tRep + 0.5)} />
							{[LEVRE_HAUT, LEVRE_BAS, LIGNE].map((d, i) => (
								<path
									key={i}
									d={d}
									fill="none"
									stroke="url(#levres-or)"
									strokeWidth={i === 2 ? 3.5 : 5}
									strokeLinecap="round"
									pathLength={1}
									strokeDasharray="1 1"
									strokeDashoffset={1 - trace}
									opacity={trace > 0.001 ? 1 : 0}
								/>
							))}
						</g>
						{/* la seringue, sur l'arrêt ; elle éclate sur la relance */}
						{seringue > 0 ? (
							<g transform={`translate(${540 + Math.sin(t * 40) * 1.5} 860) rotate(-18)`} opacity={seringue}>
								<path d={SERINGUE} fill="none" stroke={C.creme} strokeWidth={4} strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - seringue} />
							</g>
						) : null}
					</svg>
					{eclate > 0 && eclate < 1
						? Array.from({length: 90}, (_, i) => {
								// les grains partent de la silhouette de la seringue
								const u = h(i, 21) * 310 - 160;
								const x0 = 540 + u * Math.cos((-18 * Math.PI) / 180);
								const y0 = 860 + u * Math.sin((-18 * Math.PI) / 180);
								const ang = h(i, 22) * Math.PI * 2;
								const v = 260 + h(i, 23) * 900;
								const x = x0 + Math.cos(ang) * v * eclate;
								const y = y0 + Math.sin(ang) * v * eclate + 380 * eclate * eclate;
								const taille = 4 + h(i, 24) ** 2 * 16;
								return (
									<div
										key={i}
										style={{
											position: 'absolute',
											left: x - taille / 2,
											top: y - taille / 2,
											width: taille,
											height: taille,
											borderRadius: '50%',
											background: 'radial-gradient(circle at 35% 30%, #fff6dc, #d4af72 55%, #9c763a)',
											boxShadow: `0 0 ${taille * 2}px rgba(240,212,154,.6)`,
											opacity: 1 - eclate ** 2,
										}}
									/>
								);
							})
						: null}
					{/* « Et des lèvres repulpées… » puis « sans une seule piqûre. » */}
					<div style={{position: 'absolute', left: 60, right: 60, top: 1040, textAlign: 'center', opacity: 1 - p(t, RELANCE - 0.15, RELANCE + 0.05)}}>
						<Mots t={t} texte={VOIX.levres} a={la} b={REPLIQUES.levres[1]} taille={96} accent={['repulpées']} interligne={1.04} />
					</div>
					{t >= RELANCE - 0.02 ? (
						<div
							style={{
								position: 'absolute',
								left: 40,
								right: 40,
								top: 760,
								textAlign: 'center',
								transform: `scale(${1 + 0.12 * coup})`,
							}}
						>
							<Mots t={t} texte={VOIX.piqure} a={RELANCE} b={REPLIQUES.piqure[1]} taille={150} accent={['piqûre']} interligne={0.98} />
						</div>
					) : null}
					{/* SA fiche Hyaluropen, telle qu'elle est sur la vitrine */}
					{fiche > 0.001 ? (
						<div
							style={{
								position: 'absolute',
								left: 540 - 330,
								top: 1230,
								width: 660,
								height: 420,
								borderRadius: 26,
								overflow: 'hidden',
								boxShadow: '0 30px 80px -20px rgba(0,0,0,.7), 0 0 0 1.5px rgba(212,175,114,.55), 0 0 60px rgba(212,175,114,.18)',
								opacity: Math.min(1, fiche * 1.4),
								transform: `translateY(${(1 - fiche) * 120}px)`,
							}}
						>
							<Img
								src={staticFile('grain35/vitrine/avances.jpg')}
								style={{position: 'absolute', width: 1170 * (660 / 1025), left: -72 * (660 / 1025), top: -1487 * (660 / 1025)}}
							/>
						</div>
					) : null}
					{fiche > 0.001 ? (
						<div style={{position: 'absolute', left: 0, right: 0, top: 1680, textAlign: 'center', opacity: fiche}}>
							<Etiquette texte={`${FAITS.hyaluropen.nom} · ${FAITS.hyaluropen.details[0].split(' · ')[0]}`} taille={24} />
						</div>
					) : null}
					{/* l'arrêt : le noir se resserre autour, la musique retient son souffle */}
					<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 30%, rgba(10,4,8,.75) 100%)', opacity: suspense}} />
					{flash > 0 ? <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 42%, #fffaf0 0%, rgba(240,212,154,.7) 22%, transparent 55%)', opacity: flash}} /> : null}
				</AbsoluteFill>
			) : null}
		</AbsoluteFill>
	);
};

