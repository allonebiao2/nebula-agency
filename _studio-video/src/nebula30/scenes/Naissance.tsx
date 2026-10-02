/**
 * 1 · LA PROMESSE, PUIS L'EXPLOSION.
 *
 * Une étoile respire seule dans le noir, au rythme de deux battements. « Regardez
 * bien. » s'allume dessous, lettre par lettre, puis est ASPIRÉ dans l'étoile, qui
 * explose sur le premier temps de la musique : la nébuleuse naît (les grains sont
 * dans `Particules`). En haut : « Tout ce que vous allez voir… ». En bas, les
 * VRAIES lettres du logo tombent une à une : NEBULA le crée pour votre business.
 */
import React from 'react';
import {Img, interpolate, staticFile} from 'remotion';
import {COUCHES} from '../couches';
import {C, CENTRE, DEGRADE, LARGEUR, type Registre, T, TEXTES, instants, mot} from '../donnees';
import {ASPIRE, Eclair, Etoile, Mots, Onde, p, ressort} from '../outils';
import {TEXTE, TITRE} from '../polices';

const BATTEMENTS = [0.05, 1.0];
const LARGEUR_NEBULA = 470;

/** « REGARDEZ / BIEN. » : deux lignes, chaque lettre s'allume à son mot, puis tout est aspiré. */
const Regardez: React.FC<{t: number; texte: string}> = ({t, texte}) => {
	const [d0, d1] = instants('regardez');
	const aspire = p(t, T.bang - 0.5, T.bang - 0.02, ASPIRE);
	if (aspire >= 1) return null;
	const haut = 1130;
	const lignes = texte.split(' ');
	const espacement = interpolate(t, [d0, d1 + 0.6], [0.1, 0.03], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<div
			style={{
				position: 'absolute',
				left: 0,
				width: LARGEUR,
				top: haut,
				textAlign: 'center',
				fontFamily: TITRE,
				fontWeight: 800,
				fontSize: 96,
				lineHeight: 1.04,
				color: C.lavande,
				textTransform: 'uppercase',
				transformOrigin: `${CENTRE.x}px ${CENTRE.y - haut}px`,
				transform: `scale(${1 - 0.97 * aspire})`,
				opacity: 1 - aspire ** 3,
				textShadow: '0 0 30px rgba(168,236,255,.45), 0 0 80px rgba(107,63,242,.5)',
			}}
		>
			{lignes.map((ligne, l) => (
				<div key={l} style={{whiteSpace: 'nowrap', letterSpacing: `${espacement}em`}}>
					{[...ligne].map((c, k) => {
						const depart = (l === 0 ? d0 : d1) + k * 0.034;
						const e = ressort(t, depart, {damping: 18, stiffness: 140});
						return (
							<span
								key={k}
								style={{
									display: 'inline-block',
									opacity: Math.min(1, e * 1.5),
									transform: `translateY(${(1 - e) * 34}px)`,
									filter: e < 0.97 ? `blur(${(1 - e) * 16}px)` : undefined,
								}}
							>
								{c}
							</span>
						);
					})}
				</div>
			))}
		</div>
	);
};

/** NEBULA en VRAIES lettres du logo, qui tombent une à une avec un éclat. */
const LettresNebula: React.FC<{t: number; a: number; largeur: number; x: number; y: number; sortie: number}> = ({t, a, largeur, x, y, sortie}) => {
	const k = largeur / COUCHES.nebula.w;
	const s = p(t, sortie, sortie + 0.35);
	return (
		<div style={{position: 'absolute', left: x, top: y, width: largeur, height: COUCHES.nebula.h * k, opacity: 1 - s, transform: `translateY(${-40 * s}px)`}}>
			{COUCHES.lettres.map((L, i) => {
				const e = ressort(t, a + i * 0.055, {damping: 13, stiffness: 190, mass: 0.6});
				const eclat = Math.max(0, 1 - (t - (a + i * 0.055)) * 3) * (t > a + i * 0.055 ? 1 : 0);
				return (
					<Img
						key={i}
						src={staticFile(`nebula30/logo/${L.fichier}`)}
						style={{
							position: 'absolute',
							left: (L.x - COUCHES.nebula.x) * k,
							top: (L.y - COUCHES.nebula.y) * k,
							width: L.w * k,
							height: L.h * k,
							opacity: Math.min(1, e * 1.4),
							transform: `translateY(${(1 - e) * -46}px) scale(${1.35 - 0.35 * e})`,
							filter: `brightness(${1 + eclat * 1.6})`,
						}}
					/>
				);
			})}
		</div>
	);
};

export const Naissance: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	if (t > T.vitrine + 0.4) return null;
	const x = TEXTES[registre];
	const avant = t < T.bang;
	const battement = BATTEMENTS.reduce((s, a) => s + (t > a ? Math.exp(-(t - a) * 6) * 0.45 : 0), 0);
	const aspire = p(t, T.bang - 0.5, T.bang, ASPIRE);
	const taille = avant
		? (19 + 3 * Math.sin(t * 2.6)) * (1 + battement) * (1 - 0.65 * aspire)
		: interpolate(t, [T.bang, T.bang + 0.45, T.versTel, T.vitrine], [58, 30, 24, 0], {extrapolateRight: 'clamp'});
	const eclat = avant ? 0.9 + 0.7 * aspire : 1.25;
	const sortie = T.versTel - 0.15;
	const ny = 1185;
	return (
		<>
			<Etoile x={CENTRE.x} y={CENTRE.y} taille={taille} eclat={eclat} rotation={t * 9} traine={avant ? 0.25 + 0.5 * aspire : interpolate(t, [T.bang, T.bang + 0.8], [1.4, 0.35], {extrapolateRight: 'clamp'})} />
			<Onde t={t} a={T.bang} x={CENTRE.x} y={CENTRE.y} rayonMax={1500} duree={1.0} />
			<Onde t={t} a={T.bang + 0.1} x={CENTRE.x} y={CENTRE.y} rayonMax={900} duree={0.8} couleur={C.mauve} />
			<Eclair t={t} a={T.bang} x={CENTRE.x} y={CENTRE.y} duree={0.55} />

			<Regardez t={t} texte={x.regardez} />

			<Mots
				t={t}
				texte={x.toutCe}
				a={0}
				instants={instants('toutCe')}
				police={TEXTE}
				graisse={500}
				taille={56}
				couleur={C.lavande}
				sortie={sortie}
				style={{position: 'absolute', left: 60, width: LARGEUR - 120, top: 300, textAlign: 'center', textShadow: '0 0 24px rgba(107,63,242,.6)'}}
			/>

			{/* « NEBULA le crée » : le wordmark et les deux mots, centrés ensemble */}
			<div style={{position: 'absolute', left: 0, width: LARGEUR, top: ny, display: 'flex', justifyContent: 'center', alignItems: 'flex-end', gap: 26}}>
				<div style={{position: 'relative', width: LARGEUR_NEBULA, height: (COUCHES.nebula.h * LARGEUR_NEBULA) / COUCHES.nebula.w}}>
					<LettresNebula t={t} a={mot('nebulaCree', 0) - 0.04} largeur={LARGEUR_NEBULA} x={0} y={0} sortie={sortie} />
				</div>
				<Mots t={t} texte={x.cree} a={0} instants={instants('nebulaCree').slice(1, 3)} taille={64} sortie={sortie} style={{whiteSpace: 'nowrap', marginBottom: -12}} />
			</div>
			<Mots
				t={t}
				texte={x.pour}
				a={0}
				instants={instants('nebulaCree').slice(3)}
				taille={66}
				degrade={DEGRADE}
				sortie={sortie}
				style={{position: 'absolute', left: 60, width: LARGEUR - 120, top: ny + 100, textAlign: 'center', whiteSpace: 'nowrap'}}
			/>
		</>
	);
};
