/**
 * 5 · LA SIGNATURE : « NEBULA Agency. Là où naissent les étoiles. »
 *
 * Tout ce qui a été montré est aspiré dans l'étoile du logo (les grains, dans
 * `Particules`). Sur le premier temps de la musique, elle se rallume : éclair,
 * onde de choc ; la galaxie se révèle depuis l'étoile, ses orbites se tracent,
 * les six VRAIES lettres de NEBULA tombent une à une, AGENCY s'ouvre entre ses
 * deux traits, et un reflet passe sur le mot. Dessous : la phrase, les faits qui
 * convainquent, et de quoi écrire.
 */
import React from 'react';
import {Easing, Img, interpolate, staticFile} from 'remotion';
import {COUCHES} from '../couches';
import {C, DEGRADE_TRAVERS, FAITS, LARGEUR, R, type Registre, T, TEXTES, instants, mot} from '../donnees';
import {IconeDiscussion, IconeGlobe, IconeTelephone} from '../Icones';
import {BAS_LOGO, ETOILE, cadre, enImage} from '../logo';
import {Eclair, Etoile, Mots, Onde, montant, p, ressort} from '../outils';
import {MONO, TEXTE} from '../polices';

const Couche: React.FC<{fichier: string; c: {x: number; y: number; w: number; h: number}; style?: React.CSSProperties}> = ({fichier, c, style}) => (
	<Img src={staticFile(`nebula30/logo/${fichier}`)} style={{position: 'absolute', ...cadre(c), ...style}} />
);

export const Signature: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	if (t < T.implosion) return null;
	const hit = T.hit;
	const avant = t < hit;
	// l'étoile : elle grossit pendant l'aspiration, éclate au premier temps, puis se pose
	const montee = p(t, T.implosion, hit, Easing.in(Easing.quad));
	const taille = avant ? 6 + 30 * montee : interpolate(t, [hit, hit + 0.35, hit + 1.6], [70, 30, 17], {extrapolateRight: 'clamp'});
	const scintille = t > 28.6 ? Math.exp(-((t - 29.0) ** 2) * 30) * 1.2 : 0;
	// la galaxie se révèle en cercle depuis l'étoile
	const m = cadre(COUCHES.marque);
	const revele = p(t, hit + 0.05, hit + 1.0, Easing.out(Easing.cubic));
	const rayon = revele * 900;
	const masque = `radial-gradient(circle at ${ETOILE.x - m.left}px ${ETOILE.y - m.top}px, #000 ${rayon}px, transparent ${rayon + 90}px)`;
	// les orbites tracées par-dessus, le temps que la galaxie apparaisse
	const orbite = p(t, hit, hit + 0.8, Easing.inOut(Easing.cubic));
	const orbiteSort = p(t, hit + 0.9, hit + 1.5);
	const [ox, oy] = enImage(COUCHES.marque.x + COUCHES.marque.w / 2, COUCHES.marque.y + COUCHES.marque.h * 0.52);
	// AGENCY et ses traits
	const traits = p(t, hit + 0.75, hit + 1.25, Easing.out(Easing.cubic));
	const agency = ressort(t, hit + 0.85, {damping: 20, stiffness: 120});
	// le reflet sur NEBULA
	const reflet = p(t, hit + 1.4, hit + 2.1, Easing.inOut(Easing.quad));
	const n = cadre(COUCHES.nebula);
	const contacts = ressort(t, T.contacts, {damping: 17, stiffness: 120});
	const faits = ressort(t, R.etoiles[1] - 0.6, {damping: 17});
	const services = ressort(t, hit + 1.8, {damping: 18});
	return (
		<>
			<Onde t={t} a={hit} x={ETOILE.x} y={ETOILE.y} rayonMax={1500} duree={1.1} />
			<Onde t={t} a={hit + 0.12} x={ETOILE.x} y={ETOILE.y} rayonMax={950} duree={0.9} couleur={C.mauve} />

			{/* la galaxie */}
			<Couche
				fichier="marque.png"
				c={COUCHES.marque}
				style={{opacity: revele > 0 ? 1 : 0, WebkitMaskImage: masque, maskImage: masque, filter: `brightness(${1 + 0.8 * (1 - revele)})`}}
			/>
			{orbite > 0 && orbiteSort < 1 ? (
				<svg width={LARGEUR} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: 1 - orbiteSort}}>
					{[
						[0.53, 0.3, -10, C.cyan],
						[0.47, 0.22, -14, C.mauve],
						[0.39, 0.15, -11, C.etoile],
					].map(([rx, ry, rot, couleur], i) => (
						<ellipse
							key={i}
							cx={ox}
							cy={oy}
							rx={(rx as number) * m.width}
							ry={(ry as number) * m.width}
							transform={`rotate(${rot} ${ox} ${oy})`}
							fill="none"
							stroke={couleur as string}
							strokeWidth={3.5 - i}
							pathLength={1}
							strokeDasharray={1}
							strokeDashoffset={1 - orbite}
							style={{filter: `drop-shadow(0 0 10px ${couleur})`}}
						/>
					))}
				</svg>
			) : null}

			{/* NEBULA, lettre par lettre */}
			{COUCHES.lettres.map((L, i) => {
				const a = mot('nebulaAgency', 0) + 0.02 + i * 0.06;
				const e = ressort(t, a, {damping: 12, stiffness: 180, mass: 0.6});
				const eclat = t > a ? Math.max(0, 1 - (t - a) * 2.6) : 0;
				return (
					<Couche
						key={i}
						fichier={L.fichier}
						c={L}
						style={{opacity: Math.min(1, e * 1.4), transform: `translateY(${(1 - e) * -60}px) scale(${1.4 - 0.4 * e})`, filter: `brightness(${1 + 1.8 * eclat})`}}
					/>
				);
			})}
			{reflet > 0 && reflet < 1 ? (
				<div
					style={{
						position: 'absolute',
						...n,
						WebkitMaskImage: `url(${staticFile('nebula30/logo/nebula.png')})`,
						maskImage: `url(${staticFile('nebula30/logo/nebula.png')})`,
						WebkitMaskSize: '100% 100%',
						maskSize: '100% 100%',
						background: `linear-gradient(105deg, transparent ${reflet * 140 - 40}%, rgba(255,255,255,.95) ${reflet * 140 - 25}%, transparent ${reflet * 140 - 10}%)`,
					}}
				/>
			) : null}

			{/* AGENCY entre ses deux traits */}
			<Couche fichier="trait-g.png" c={COUCHES['trait-g']} style={{transformOrigin: 'right center', transform: `scaleX(${traits})`, opacity: traits}} />
			<Couche fichier="trait-d.png" c={COUCHES['trait-d']} style={{transformOrigin: 'left center', transform: `scaleX(${traits})`, opacity: traits}} />
			<Couche fichier="agency.png" c={COUCHES.agency} style={{opacity: Math.min(1, agency * 1.3), transform: `scaleX(${1.25 - 0.25 * agency})`, filter: agency < 0.98 ? `blur(${(1 - agency) * 8}px)` : undefined}} />

			<Etoile x={ETOILE.x} y={ETOILE.y} taille={taille * (1 + scintille)} eclat={avant ? 0.6 + montee : 1.3 + scintille} rotation={t * 12} traine={avant ? montee : interpolate(t, [hit, hit + 1.0], [1.6, 0.3], {extrapolateRight: 'clamp'}) + scintille} />
			<Eclair t={t} a={hit} x={ETOILE.x} y={ETOILE.y} duree={0.6} />

			{/* en haut : ce que NEBULA fabrique */}
			<div style={{position: 'absolute', left: 0, width: LARGEUR, top: 300, textAlign: 'center', fontFamily: MONO, fontWeight: 500, fontSize: 25, letterSpacing: '0.26em', color: C.cyan, opacity: services, transform: `translateY(${(1 - services) * -20}px)`}}>
				{FAITS.services.join(' · ').toUpperCase()}
			</div>

			{/* la phrase */}
			<Mots
				t={t}
				texte={TEXTES[registre].etoiles}
				a={0}
				instants={instants('etoiles')}
				police={TEXTE}
				graisse={300}
				taille={54}
				couleur={C.lavande}
				espacement="0.01em"
				style={{position: 'absolute', left: 0, width: LARGEUR, top: BAS_LOGO + 40, textAlign: 'center', textShadow: '0 0 30px rgba(107,63,242,.7)'}}
			/>

			{/* les faits qui convainquent */}
			<div style={{position: 'absolute', left: 0, width: LARGEUR, top: BAS_LOGO + 128, textAlign: 'center', fontFamily: MONO, fontWeight: 500, fontSize: 30, color: C.cyan, opacity: faits, transform: `translateY(${(1 - faits) * 20}px)`}}>
				Dès {montant(FAITS.prixEntree)} F · {FAITS.delai} · {FAITS.ville}
			</div>

			{/* de quoi écrire */}
			<div style={{position: 'absolute', left: 0, width: LARGEUR, top: BAS_LOGO + 196, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, opacity: contacts, transform: `translateY(${(1 - contacts) * 30}px)`}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 18}}>
					<IconeDiscussion taille={66} />
					<span style={{fontFamily: MONO, fontWeight: 700, fontSize: 54, color: C.etoile}}>{FAITS.whatsapp}</span>
				</div>
				<div style={{display: 'flex', alignItems: 'center', gap: 14}}>
					<IconeTelephone taille={42} couleur={C.gris} />
					<span style={{fontFamily: MONO, fontWeight: 500, fontSize: 36, color: C.lavande}}>Appel {FAITS.appel}</span>
				</div>
				<div style={{display: 'flex', alignItems: 'center', gap: 12}}>
					<IconeGlobe taille={38} />
					<span style={{fontFamily: TEXTE, fontWeight: 600, fontSize: 38, backgroundImage: DEGRADE_TRAVERS, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', WebkitTextFillColor: 'transparent'}}>
						{FAITS.site}
					</span>
				</div>
			</div>
		</>
	);
};

