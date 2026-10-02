/**
 * 3 · LA RÉVÉLATION : « Et même… cette vidéo. La vôtre est la prochaine. »
 *
 * L'image se FIGE au moment où la musique allait tomber. « Et même… » ; puis la
 * caméra RECULE : le film n'était qu'un écran dans un logiciel de montage, avec
 * ses rushes (les vrais sites), ses effets, sa timeline, la VRAIE onde de cette
 * voix et de cette musique. La tête de lecture REMBOBINE (le film défile à
 * l'envers dans le moniteur), puis file vers un clip vide : VOTRE VIDÉO.
 * Sur la chute de la musique, on plonge dans ce clip : c'est l'appel.
 */
import React from 'react';
import {Easing, Img, interpolate, staticFile} from 'remotion';
import {C, HAUTEUR, LARGEUR, NOMS_SITES, R, type Registre, SITES, T, TEXTES, instants} from '../donnees';
import {ONDE_MUSIQUE, ONDE_VOIX} from '../minutage';
import {GLISSE, Mots, p, ressort} from '../outils';
import {MONO, TEXTE, TITRE} from '../polices';

export const MONITEUR = {x: 324, y: 236, k: 0.4};
const TL = {x0: 150, l: 890, haut: 1222, piste: 52, ecart: 8, duree: 36};
const xTemps = (s: number) => TL.x0 + (s / TL.duree) * TL.l;
const FANTOME = {a: 30.4, b: 35.6};

/** Le temps montré par le moniteur (et la tête de lecture) à l'instant t. */
export const tempsMoniteur = (t: number) => {
	if (t < T.rembobine) return T.fige;
	const recule = p(t, T.rembobine, T.rembobine + 0.95, GLISSE);
	if (t < T.votre + 0.15) return T.fige * (1 - recule);
	// la tête file vers le clip vide : le film défile en accéléré, puis le vide
	return interpolate(t, [T.votre + 0.15, T.votre + 0.8], [0, FANTOME.a + 0.6], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
};

const code = (s: number) => {
	const sec = Math.floor(s);
	const img = Math.floor((s - sec) * 30);
	return `00:00:${String(sec).padStart(2, '0')}:${String(img).padStart(2, '0')}`;
};

const PLANS: [string, number, number][] = [
	['Ouverture', 0, T.bang],
	['Nébuleuse', T.bang, T.versTel],
	['Vitrine', T.versTel, T.catalogue],
	['Catalogue', T.catalogue, T.outil],
	['Outil', T.outil, T.fige],
	['Révélation', T.fige, T.chute],
	['Appel', T.chute, T.implosion],
	['Signature', T.implosion, 30],
];
const CLES = [T.bang, T.versTel, T.catalogue, T.outil, T.implosion, T.hit];

const Piste: React.FC<{y: number; nom: string; children?: React.ReactNode}> = ({y, nom, children}) => (
	<>
		<div style={{position: 'absolute', left: 30, top: y + 16, width: 112, fontFamily: MONO, fontSize: 15, letterSpacing: '0.1em', color: C.gris}}>{nom}</div>
		<div style={{position: 'absolute', left: TL.x0, top: y, width: TL.l, height: TL.piste, borderRadius: 8, background: 'rgba(160,170,255,.045)'}} />
		{children}
	</>
);

const Onde: React.FC<{y: number; valeurs: number[]; couleur: string}> = ({y, valeurs, couleur}) => (
	<svg style={{position: 'absolute', left: 0, top: y, overflow: 'visible'}} width={LARGEUR} height={TL.piste}>
		{valeurs.map((v, i) => {
			const x = xTemps(i * 0.1);
			const hh = Math.max(1, v * (TL.piste - 12));
			return <rect key={i} x={x} y={TL.piste / 2 - hh / 2} width={2.6} height={hh} rx={1.3} fill={couleur} opacity={0.85} />;
		})}
	</svg>
);

export const Montage: React.FC<{t: number; registre: Registre; film: (t: number) => React.ReactNode}> = ({t, registre, film}) => {
	if (t < T.fige || t > T.chute + 0.45) return null;
	const x = TEXTES[registre];
	const recul = p(t, T.recul, T.recul + 0.6, GLISSE);
	const plonge = p(t, T.chute - 0.02, T.chute + 0.4, Easing.in(Easing.cubic));
	const tf = tempsMoniteur(t);
	const k = interpolate(recul, [0, 1], [1, MONITEUR.k]);
	const fige = t < T.recul + 0.1;
	const tete = Math.min(tf, FANTOME.a + 0.6);
	const fantome = ressort(t, T.votre, {damping: 14, stiffness: 140});
	const dansLeVide = tf > FANTOME.a;
	// la plongée : tout le logiciel grossit autour du moniteur
	const cx = MONITEUR.x + (LARGEUR * MONITEUR.k) / 2;
	const cy = MONITEUR.y + (HAUTEUR * MONITEUR.k) / 2;
	const zoom = 1 + 1.5 * plonge;
	return (
		<div style={{position: 'absolute', inset: 0, background: C.encre, transformOrigin: `${cx}px ${cy}px`, transform: `scale(${zoom})`, opacity: 1 - p(t, T.chute + 0.2, T.chute + 0.42)}}>
			{/* le logiciel de montage, qui apparaît en reculant */}
			<div style={{position: 'absolute', inset: 0, opacity: recul}}>
				<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 35%, #161337, #07061a 70%)'}} />
				{/* la barre du haut */}
				<div style={{position: 'absolute', left: 24, right: 24, top: 150, height: 64, display: 'flex', alignItems: 'center', gap: 16, transform: `translateY(${(1 - recul) * -40}px)`}}>
					<Img src={staticFile('nebula30/logo/marque.png')} style={{width: 64, height: 32, objectFit: 'contain'}} />
					<div style={{fontFamily: TEXTE, fontWeight: 700, fontSize: 25, color: C.lavande}}>NEBULA Studio</div>
					<div style={{flex: 1, textAlign: 'center', fontFamily: MONO, fontSize: 19, color: C.gris}}>cette-video.mp4</div>
					<div style={{fontFamily: MONO, fontSize: 16, color: C.grisFonce}}>1080 × 1920 · 30 i/s</div>
				</div>
				{/* les rushes : les vrais sites */}
				<div style={{position: 'absolute', left: 24, top: MONITEUR.y, width: 280, transform: `translateX(${(1 - recul) * -70}px)`}}>
					<div style={{fontFamily: MONO, fontSize: 15, letterSpacing: '0.24em', color: C.cyan, marginBottom: 14}}>RUSHES</div>
					<div style={{display: 'flex', flexWrap: 'wrap', gap: 12}}>
						{SITES.tous.map((site, i) => (
							<div key={site} style={{width: 128, opacity: ressort(t, T.recul + 0.25 + i * 0.03)}}>
								<Img src={staticFile(`nebula30/sites/${site}-pc.jpg`)} style={{width: 128, height: 80, objectFit: 'cover', borderRadius: 8, boxShadow: 'inset 0 0 0 1px rgba(190,200,255,.2)'}} />
								<div style={{fontFamily: MONO, fontSize: 11.5, color: C.gris, marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden'}}>{NOMS_SITES[site]}</div>
							</div>
						))}
					</div>
				</div>
				{/* les effets */}
				<div style={{position: 'absolute', left: 786, top: MONITEUR.y, width: 270, transform: `translateX(${(1 - recul) * 70}px)`}}>
					<div style={{fontFamily: MONO, fontSize: 15, letterSpacing: '0.24em', color: C.cyan, marginBottom: 14}}>EFFETS</div>
					{['Poussière d’étoiles', 'Orbites', 'Étoile', 'Lumière', 'Profondeur 3D', 'Secousse', 'Ralenti'].map((nom, i) => {
						const on = ressort(t, T.recul + 0.3 + i * 0.05);
						return (
							<div key={nom} style={{display: 'flex', alignItems: 'center', gap: 12, height: 50, borderBottom: '1px solid rgba(170,180,255,.08)'}}>
								<svg width={14} height={14} viewBox="0 0 14 14">
									<path d="M7 1 L13 7 L7 13 L1 7 Z" fill={C.mauve} />
								</svg>
								<div style={{flex: 1, fontFamily: TEXTE, fontSize: 19, color: C.lavande}}>{nom}</div>
								<div style={{width: 44, height: 24, borderRadius: 12, background: `rgba(168,236,255,${0.15 + 0.6 * on})`, position: 'relative'}}>
									<div style={{position: 'absolute', top: 3, left: 3 + 20 * on, width: 18, height: 18, borderRadius: 9, background: C.etoile}} />
								</div>
							</div>
						);
					})}
				</div>

				{/* la timeline */}
				<div style={{position: 'absolute', inset: 0, transform: `translateY(${(1 - recul) * 90}px)`}}>
					<div style={{position: 'absolute', left: 24, right: 24, top: TL.haut - 52, height: 1, background: 'rgba(170,180,255,.12)'}} />
					{Array.from({length: TL.duree + 1}, (_, s) => (
						<React.Fragment key={s}>
							<div style={{position: 'absolute', left: xTemps(s), top: TL.haut - 30, width: 1.5, height: s % 5 ? 8 : 16, background: C.grisFonce}} />
							{s % 5 === 0 ? <div style={{position: 'absolute', left: xTemps(s) - 30, width: 60, top: TL.haut - 50, textAlign: 'center', fontFamily: MONO, fontSize: 13, color: C.gris}}>{`00:${String(s).padStart(2, '0')}`}</div> : null}
						</React.Fragment>
					))}
					<Piste y={TL.haut} nom="TEXTES">
						{Object.values(R).map(([a, b], i) => (
							<div key={i} style={{position: 'absolute', left: xTemps(a), width: xTemps(b) - xTemps(a), top: TL.haut + 14, height: 24, borderRadius: 6, background: 'rgba(182,137,255,.55)'}} />
						))}
					</Piste>
					<Piste y={TL.haut + 60} nom="POUSSIÈRE">
						<div style={{position: 'absolute', left: xTemps(T.bang), width: xTemps(30) - xTemps(T.bang), top: TL.haut + 60 + 10, height: 32, borderRadius: 8, background: 'linear-gradient(90deg, rgba(98,168,255,.35), rgba(107,63,242,.35))'}} />
						{CLES.map((s, i) => (
							<svg key={i} width={18} height={18} viewBox="0 0 18 18" style={{position: 'absolute', left: xTemps(s) - 9, top: TL.haut + 60 + 17}}>
								<path d="M9 1 L17 9 L9 17 L1 9 Z" fill={C.etoile} />
							</svg>
						))}
					</Piste>
					<Piste y={TL.haut + 120} nom="PLANS">
						{PLANS.map(([nom, a, b], i) => (
							<div
								key={nom}
								style={{
									position: 'absolute',
									left: xTemps(a) + 1,
									width: xTemps(b) - xTemps(a) - 2,
									top: TL.haut + 120 + 4,
									height: 44,
									borderRadius: 8,
									background: `linear-gradient(180deg, ${['#3b5bdb', '#5a3fd6', '#2f6bff', '#6b3ff2', '#4c6ef5', '#7048e8', '#2f9e7a', '#845ef7'][i]}, rgba(10,10,30,.6))`,
									boxShadow: 'inset 0 0 0 1px rgba(255,255,255,.18)',
									fontFamily: TEXTE,
									fontWeight: 600,
									fontSize: 13,
									color: C.etoile,
									padding: '6px 6px',
									overflow: 'hidden',
									whiteSpace: 'nowrap',
								}}
							>
								{nom}
							</div>
						))}
						{/* le clip vide : VOTRE VIDÉO */}
						{fantome > 0.01 ? (
							<div
								style={{
									position: 'absolute',
									left: xTemps(FANTOME.a),
									width: xTemps(FANTOME.b) - xTemps(FANTOME.a),
									top: TL.haut + 120 + 4,
									height: 44,
									borderRadius: 8,
									border: `2.5px dashed ${C.cyan}`,
									boxShadow: `0 0 ${18 + 14 * Math.sin(t * 9)}px rgba(168,236,255,.7)`,
									background: 'rgba(168,236,255,.1)',
									opacity: Math.min(1, fantome * 1.4),
									transform: `scale(${0.7 + 0.3 * fantome})`,
									display: 'flex',
									alignItems: 'center',
									justifyContent: 'center',
									gap: 6,
									fontFamily: MONO,
									fontWeight: 700,
									fontSize: 13,
									color: C.cyan,
									whiteSpace: 'nowrap',
								}}
							>
								+ {x.votreClip}
							</div>
						) : null}
					</Piste>
					<Piste y={TL.haut + 180} nom="VOIX">
						<Onde y={TL.haut + 180} valeurs={ONDE_VOIX} couleur={C.cyan} />
					</Piste>
					<Piste y={TL.haut + 240} nom="MUSIQUE">
						<Onde y={TL.haut + 240} valeurs={ONDE_MUSIQUE} couleur={C.mauve} />
					</Piste>
					{/* la tête de lecture */}
					<div style={{position: 'absolute', left: xTemps(tete) - 1.5, top: TL.haut - 40, width: 3, height: 340, background: C.etoile, boxShadow: `0 0 14px ${C.cyan}`}} />
					<div
						style={{
							position: 'absolute',
							left: xTemps(tete) - 74,
							top: TL.haut - 86,
							width: 148,
							textAlign: 'center',
							padding: '5px 0',
							borderRadius: 8,
							background: C.etoile,
							fontFamily: MONO,
							fontWeight: 700,
							fontSize: 17,
							color: C.encre,
						}}
					>
						{code(Math.min(tf, 35.99))}
					</div>
				</div>
			</div>

			{/* le film lui-même : plein écran et figé, puis dans le moniteur */}
			<div
				style={{
					position: 'absolute',
					left: MONITEUR.x * recul,
					top: MONITEUR.y * recul,
					width: LARGEUR,
					height: HAUTEUR,
					transformOrigin: '0 0',
					transform: `scale(${k})`,
					borderRadius: 34 * recul / k,
					overflow: 'hidden',
					boxShadow: recul > 0 ? `0 0 0 ${3 / k}px rgba(190,200,255,.35), 0 40px 120px rgba(0,0,0,.8)` : undefined,
					filter: fige ? `saturate(${1 - 0.5 * p(t, T.fige, T.fige + 0.3)}) brightness(${1 - 0.35 * p(t, T.fige, T.fige + 0.3)})` : undefined,
				}}
			>
				{dansLeVide ? (
					<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 45%, #1d1850, #06051a 70%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 50}}>
						<div style={{width: 230, height: 230, borderRadius: 115, border: `8px dashed ${C.cyan}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TEXTE, fontWeight: 300, fontSize: 170, color: C.cyan, transform: `rotate(${t * 40}deg)`}}>
							<span style={{transform: `rotate(${-t * 40}deg)`, marginTop: -16}}>+</span>
						</div>
						<div style={{fontFamily: TITRE, fontWeight: 800, fontSize: 130, color: C.lavande, letterSpacing: '-0.01em'}}>{x.votreClip}</div>
					</div>
				) : (
					film(tf)
				)}
			</div>

			{/* le bandeau PAUSE pendant que tout est figé */}
			{t < T.recul + 0.3 ? (
				<div style={{position: 'absolute', left: 60, top: 250, display: 'flex', alignItems: 'center', gap: 14, opacity: p(t, T.fige + 0.05, T.fige + 0.25) * (1 - p(t, T.recul, T.recul + 0.3)), fontFamily: MONO, fontWeight: 700, fontSize: 26, letterSpacing: '0.2em', color: C.etoile}}>
					<div style={{display: 'flex', gap: 7}}>
						<div style={{width: 10, height: 34, background: C.etoile}} />
						<div style={{width: 10, height: 34, background: C.etoile}} />
					</div>
					PAUSE
				</div>
			) : null}

			{/* « Et même… » sur l'image figée */}
			{t < T.recul + 0.3 ? (
				<div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse 70% 30% at 50% 50%, rgba(5,4,14,${0.75 * p(t, R.etMeme[0] - 0.2, R.etMeme[0] + 0.1)}), transparent 75%)`}}>
					<Mots t={t} texte={x.etMeme} a={0} instants={instants('etMeme')} taille={150} sortie={T.recul - 0.05} style={{position: 'absolute', left: 0, width: LARGEUR, top: 870, textAlign: 'center', textShadow: '0 0 40px rgba(107,63,242,.8)'}} />
				</div>
			) : null}

			{/* « cette vidéo. » puis « La vôtre est la prochaine. » sous le moniteur */}
			<Mots t={t} texte={x.cetteVideo} a={0} instants={instants('cetteVideo')} taille={74} sortie={R.votre[0] - 0.25} style={{position: 'absolute', left: 0, width: LARGEUR, top: 1026, textAlign: 'center', whiteSpace: 'nowrap'}} />
			<Mots t={t} texte={x.votre} a={0} instants={instants('votre')} taille={54} couleur={C.cyan} style={{position: 'absolute', left: 0, width: LARGEUR, top: 1040, textAlign: 'center', whiteSpace: 'nowrap'}} />
		</div>
	);
};
