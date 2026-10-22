/**
 * ACTES III à V · la vente (la narratrice, l'afrobeat) : la marque, l'heure choisie, l'impossible à ouvrir, la
 * plume, l'habillage, puis les moments de la vie (Saint-Valentin, excuses, demande, soirée entre potes), et la fin.
 * Une animation PROPRE à chaque moment, tirée des vidéos de référence de Mongazi ou de ce qu'elles inspirent.
 * Les coupes et les accents tombent sur la musique (`tempsAfro`, `mesuresAfro`).
 */
import React from 'react';
import {AbsoluteFill, Img, random, staticFile} from 'remotion';
import {ADRESSE, C, CIRES, L, LETTRE, M, OCCASIONS, PAPIERS, PLUME, SANS, SCEAUX, TITRE, type Cire, type Papier, type Sceau} from './donnees';
import {accent, Ciel, Encre, Pluie, Poussiere, titre} from './decor';
import {bruit, DOUX, ENTRE, mix, p, plein, RESSORT, SORT, useT, vie} from './outils';
import {EcranLettre, Telephone} from './telephone';
import {Alliances3D, Cachet3D, Enveloppe3D, Halo3D, Lumieres, Scene3D, SolOmbre, texturePapier} from './trois';

/** L'accent du temps fort : 1 sur le temps, puis s'éteint (pour faire respirer l'image avec la musique). */
const battue = (t: number, decroit = 0.16) => {
	let s = 0;
	for (const b of M.tempsAfro) if (t >= b && t - b < 0.8) s = Math.max(s, Math.exp(-(t - b) / decroit));
	return s;
};

const NUIT_FOND = `radial-gradient(110% 90% at 50% 42%, ${C.nuit2} 0%, ${C.nuit3} 72%)`;
const PAPIER_FOND = `radial-gradient(120% 100% at 45% 35%, #fbf6ec 0%, ${C.papier} 45%, ${C.papier2} 100%)`;

/* ── 9 · « Ça, c'est Ma lettre à… » : le cachet de la marque tombe sur le papier, sur le premier temps ── */
export const Marque: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const tombe = p(t, debut - 0.12, debut + 0.06, ENTRE);
	const ecrase = p(t, debut + 0.04, debut + 0.24, SORT);
	const onde = vie(t, debut + 0.04, debut + 0.1, debut + 0.12, debut + 0.7);
	const sortie = p(t, fin - 0.25, fin, ENTRE);
	const pap = React.useMemo(() => texturePapier('coton', 11), []);
	return (
		<AbsoluteFill style={{background: PAPIER_FOND, opacity: 1 - sortie}}>
			<Scene3D camera={[0, 3.4, 1.15]} vise={[0, 0, 0.42]} fov={30} expo={0.9} ciel={0.3}>
				<Lumieres position={[1.8, 3.0, 2.0]} cle={20} contre={2} />
				<mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
					<planeGeometry args={[12, 7]} />
					<meshStandardMaterial map={pap} roughness={0.95} />
				</mesh>
				<group position={[0, mix(1.6, 0, tombe), 0]}>
					<Cachet3D sceau="marque" echelle={0.5} ecrase={0.35 + 0.65 * ecrase} />
				</group>
			</Scene3D>
			<div style={{position: 'absolute', left: '50%', top: 330, width: 620 * (0.6 + onde), height: 620 * (0.6 + onde), translate: '-50% -50%', borderRadius: '50%', border: `2px solid ${CIRES.bordeaux.cire}`, opacity: onde * 0.5}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 740, textAlign: 'center'}}>
				<Encre texte="Ma lettre à…" debut={debut + 0.18} pas={0.12} style={{...titre(150, C.encre), letterSpacing: '-0.015em'}} flou={14} />
			</div>
		</AbsoluteFill>
	);
};

/* ── 10 · « Une lettre scellée… qui s'ouvre à l'heure que TU choisis » : le cadran ── */
const Cadran: React.FC<{heure: number; minute: number; taille: number}> = ({heure, minute, taille: R}) => (
	<svg width={R * 2} height={R * 2} viewBox="-120 -120 240 240">
		<defs>
			<radialGradient id="cadran" cx="40%" cy="35%">
				<stop offset="0" stopColor="#2a2233" />
				<stop offset="1" stopColor="#120e17" />
			</radialGradient>
			<linearGradient id="or" x1="0" y1="0" x2="1" y2="1">
				<stop offset="0" stopColor="#f7e7b0" />
				<stop offset=".5" stopColor="#c9a227" />
				<stop offset="1" stopColor="#8a6a14" />
			</linearGradient>
		</defs>
		<circle r="112" fill="url(#cadran)" stroke="url(#or)" strokeWidth="5" />
		<circle r="100" fill="none" stroke="#c9a22755" strokeWidth="1" />
		{Array.from({length: 60}, (_, i) => {
			const a = (i / 60) * Math.PI * 2, gros = i % 5 === 0;
			return <line key={i} x1={Math.sin(a) * (gros ? 84 : 92)} y1={-Math.cos(a) * (gros ? 84 : 92)} x2={Math.sin(a) * 98} y2={-Math.cos(a) * 98} stroke={gros ? '#e0c266' : '#8f86a0'} strokeWidth={gros ? 3 : 1} strokeLinecap="round" />;
		})}
		<line x1="0" y1="10" x2={Math.sin((heure / 12) * Math.PI * 2) * 52} y2={-Math.cos((heure / 12) * Math.PI * 2) * 52} stroke="url(#or)" strokeWidth="7" strokeLinecap="round" />
		<line x1="0" y1="14" x2={Math.sin((minute / 60) * Math.PI * 2) * 82} y2={-Math.cos((minute / 60) * Math.PI * 2) * 82} stroke="#f4ede0" strokeWidth="4" strokeLinecap="round" />
		<circle r="7" fill="url(#or)" />
	</svg>
);

export const Heure: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a3 = L('a3').debut;
	/* trois heures choisies, posées sur les temps : minuit, 7 h 30, 20 h */
	const arrets = [
		{t: a3 + 0.2, h: 0, m: 0, lib: 'minuit'},
		{t: a3 + 0.82, h: 7, m: 30, lib: '7 h 30, son réveil'},
		{t: a3 + 1.45, h: 20, m: 0, lib: '20 h, le dîner'},
	];
	let cumul = 0, hh = 11.2, lib = '';
	for (let i = 0; i < arrets.length; i++) {
		const a = arrets[i];
		const k = p(t, a.t - 0.42, a.t, SORT);
		const avant = i === 0 ? 11.2 : arrets[i - 1].h + arrets[i - 1].m / 60 + (i === 1 ? 12 : 0);
		const cible = a.h + a.m / 60 + 12 * (i + 1);
		if (t >= a.t - 0.42) {
			cumul = mix(avant + 12 * i, cible, k);
			if (k > 0.6) lib = a.lib;
		}
		hh = cumul || hh;
	}
	const heure = hh % 12, minute = (hh % 1) * 60;
	const env = p(t, debut, debut + 0.45, SORT);
	return (
		<AbsoluteFill style={{background: NUIT_FOND, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<Poussiere n={30} force={0.7} graine="heure" />
			<div style={{position: 'absolute', left: 120, top: 150, width: 820}}>
				<Encre texte="Une lettre scellée…" debut={L('a2').debut - 0.05} style={titre(92)} />
				<Encre texte="qui s’ouvre à l’heure" debut={a3 - 0.05} pas={0.07} style={{...titre(92), marginTop: 18}} />
				<Encre texte="que TU choisis." debut={a3 + 0.5} pas={0.09} style={{...accent(104), marginTop: 4}} />
			</div>
			<div style={{position: 'absolute', left: 1080, top: 120, scale: String(mix(0.85, 1, env) * (1 + battue(t) * 0.02)), opacity: env}}>
				<Cadran heure={heure} minute={minute} taille={330} />
				<div style={{textAlign: 'center', marginTop: 14, ...accent(46), minHeight: 60}}>{lib}</div>
			</div>
		</AbsoluteFill>
	);
};

/* ── 11 · « Et avant l'heure ? Impossible de l'ouvrir. Même en insistant. » : on tapote, le cachet refuse ── */
export const Insiste: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const taps = [0, 0.17, 0.34].map((d) => L('a5').debut + 1.2 + d);
	const verrou = L('a5').debut + 1.82;
	const secoue = taps.reduce((a, b) => a + (t >= b ? Math.exp(-(t - b) / 0.12) * Math.sin((t - b) * 60) : 0), 0) + (t >= verrou ? Math.exp(-(t - verrou) / 0.2) * Math.sin((t - verrou) * 45) * 1.6 : 0);
	const reste = 4 * 3600 + 12 * 60 + 30 - (t - debut);
	return (
		<AbsoluteFill style={{background: NUIT_FOND, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<div style={{position: 'absolute', left: 120, top: 190, width: 900}}>
				<Encre texte="Et avant l’heure ?" debut={L('a4').debut - 0.05} style={titre(100)} />
				<Encre texte="Impossible de l’ouvrir." debut={L('a5').debut - 0.05} style={{...titre(80, C.papier), marginTop: 40}} />
				<Encre texte="Même en insistant." debut={L('a5').debut + 1.15} pas={0.1} style={{...accent(84), marginTop: 10}} />
			</div>
			<div style={{position: 'absolute', left: 1160, top: 40, perspective: 1600}}>
				<div style={{transform: 'rotateY(-10deg) rotateX(4deg)', translate: `${secoue * 10}px 0`, rotate: `${secoue * 1.2}deg`}}>
					<Telephone largeur={470} lueur={0.4}>
						<EcranLettre largeur={470 - 32} t={t} reste={reste} heure={0} />
					</Telephone>
				</div>
			</div>
			{taps.map((b, i) => {
				const k = p(t, b, b + 0.45, SORT);
				return t >= b ? <div key={i} style={{position: 'absolute', left: 1395, top: 530, width: 60 + k * 160, height: 60 + k * 160, translate: '-50% -50%', borderRadius: '50%', border: `3px solid rgba(244,237,224,${0.7 * (1 - k)})`}} /> : null;
			})}
			<div style={{position: 'absolute', left: 1395, top: 760, translate: '-50% 0', display: 'flex', alignItems: 'center', gap: 14, opacity: p(t, verrou, verrou + 0.2), scale: String(mix(0.6, 1, p(t, verrou, verrou + 0.35, RESSORT)))}}>
				<svg width={40} height={46} viewBox="0 0 24 28">
					<rect x="3" y="12" width="18" height="14" rx="3" fill={C.orDoux} />
					<path d="M7 12V8a5 5 0 0 1 10 0v4" fill="none" stroke={C.orDoux} strokeWidth="2.6" />
				</svg>
				<span style={{fontFamily: SANS, fontWeight: 700, fontSize: 30, color: C.papier}}>Pas avant l’heure.</span>
			</div>
		</AbsoluteFill>
	);
};

/* ── 12 · « Tu l'écris… ou la plume l'écrit avec toi, à partir de tes souvenirs » : la fiche, puis l'écriture ── */
const PUCES = ['Ma mère', 'Émouvant', 'Sa force', 'Sa patience', 'Une longue vie'];
const Plume: React.FC<{taille: number}> = ({taille}) => (
	<svg width={taille} height={taille} viewBox="0 0 64 64">
		<defs>
			<linearGradient id="plume-or" x1="0" y1="0" x2="1" y2="1">
				<stop offset="0" stopColor="#f7e7b0" />
				<stop offset="1" stopColor="#a87f1c" />
			</linearGradient>
		</defs>
		<path d="M56 6C34 8 18 22 12 46l-4 12 6-6c8-2 18-8 26-18 6-8 12-18 16-28z" fill="url(#plume-or)" />
		<path d="M54 9 14 52" stroke="#6d4a0e" strokeWidth="1.6" />
	</svg>
);

export const PlumeScene: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a7 = L('a7').debut;
	const tape = 'Maman, tu me réveillais à 5 h…';
	const n = Math.floor(p(t, debut + 0.05, debut + 0.75, (x) => x) * tape.length);
	const ecrit = p(t, a7 + 1.25, fin - 0.15, (x) => x);
	/* la vraie lettre, coupée en lignes courtes : chacune s'écrit à son tour */
	const lignes = [LETTRE.titre, 'Tu me réveillais à 5 h', 'pour réviser le bac, avec un bol', 'de bouillie chaude, et tu ne te', 'plaignais jamais.'];
	const nL = lignes.length;
	return (
		<AbsoluteFill style={{background: PAPIER_FOND, opacity: 1 - p(t, fin - 0.2, fin)}}>
			{/* tu l'écris */}
			<div style={{position: 'absolute', left: 110, top: 120, width: 760}}>
				<div style={{...titre(78, C.encre)}}>Tu l’écris…</div>
				<div style={{marginTop: 34, padding: '26px 30px', borderRadius: 18, background: '#fffaf1', boxShadow: '0 20px 50px rgba(60,40,20,.15), inset 0 0 0 1.5px rgba(36,29,43,.08)', fontFamily: SANS, fontSize: 34, color: C.encre, minHeight: 48}}>
					{tape.slice(0, n)}
					<span style={{opacity: Math.floor(t * 3) % 2 ? 1 : 0.15, color: CIRES.bordeaux.cire}}>|</span>
				</div>
			</div>
			{/* ou la plume l'écrit avec toi */}
			<div style={{position: 'absolute', left: 110, top: 470, width: 800, opacity: p(t, a7 - 0.1, a7 + 0.3)}}>
				<div style={{...accent(64, CIRES.bordeaux.cire)}}>ou la plume, avec toi</div>
				<div style={{display: 'flex', flexWrap: 'wrap', gap: 14, marginTop: 26}}>
					{PUCES.map((x, i) => {
						const k = p(t, a7 + 0.15 + i * 0.18, a7 + 0.4 + i * 0.18, RESSORT);
						return (
							<span key={x} style={{padding: '12px 24px', borderRadius: 999, fontFamily: SANS, fontWeight: 500, fontSize: 28, background: k > 0.5 ? CIRES.bordeaux.cire : '#efe5d4', color: k > 0.5 ? C.papier : C.encre, scale: String(mix(0.92, 1, k)), boxShadow: k > 0.5 ? '0 10px 24px rgba(140,47,57,.3)' : 'none'}}>
								{x}
							</span>
						);
					})}
				</div>
				<div style={{position: 'relative', marginTop: 30, paddingLeft: 70, ...accent(30, C.gris), lineHeight: 1.45, opacity: p(t, a7 + 1.05, a7 + 1.35)}}>
					<span style={{position: 'absolute', left: 0, top: -26, fontFamily: TITRE, fontSize: 120, lineHeight: 1, color: C.or}}>«</span>
					Elle me réveillait à 5 h pour réviser le bac, avec un bol de bouillie chaude.
				</div>
			</div>
			{/* la lettre qui s'écrit, la plume au bout de la ligne */}
			<div style={{position: 'absolute', left: 1010, top: 150, width: 800, height: 780, borderRadius: 12, background: '#fffaf2', boxShadow: '0 40px 90px rgba(60,40,20,.22)', padding: '60px 56px', boxSizing: 'border-box', rotate: '1.5deg'}}>
				{lignes.map((ligne, i) => {
					const k = p(ecrit * nL, i, i + 1, (x) => x);
					return (
						<div key={i} style={{position: 'relative', fontFamily: i ? PLUME : TITRE, fontSize: i ? 54 : 52, lineHeight: 1.3, color: C.encre, marginTop: i === 1 ? 26 : 0, whiteSpace: 'nowrap', clipPath: `inset(0 ${100 - k * 100}% 0 0)`}}>
							{ligne}
						</div>
					);
				})}
				{(() => {
					const i = Math.min(nL - 1, Math.floor(ecrit * nL));
					const k = ecrit * nL - i;
					return (
						<div style={{position: 'absolute', left: 50 + k * 600, top: 30 + (i ? 96 + (i - 1) * 70 : 0), opacity: ecrit > 0 && ecrit < 1 ? 1 : 0}}>
							<Plume taille={80} />
						</div>
					);
				})()}
			</div>
		</AbsoluteFill>
	);
};

/* ── 13 · « La cire, le sceau, le papier, ta photo… et une pluie d'étoiles à l'ouverture » ── */
const CIRES_ORDRE: Cire[] = ['bordeaux', 'or', 'nuit', 'sapin', 'rose'];
const SCEAUX_ORDRE: Sceau[] = ['coeur', 'colombe', 'couronne', 'initiale'];
const PAPIERS_ORDRE: Papier[] = ['creme', 'kraft', 'nuit', 'coton'];
const tirage = <X,>(liste: X[], t: number, debut: number, fige: X) => {
	if (t < debut) return liste[0];
	const k = Math.floor((t - debut) / 0.11);
	return k >= liste.length ? fige : liste[k];
};

export const Habit: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a8 = L('a8').debut, a9 = L('a9').debut;
	const tc = a8, ts = a8 + 0.55, tp = a8 + 1.15, tf = a8 + 1.85;
	const cire = tirage(CIRES_ORDRE, t, tc, 'or' as Cire);
	const sceau = tirage(SCEAUX_ORDRE, t, ts, 'couronne' as Sceau);
	const papier = tirage(PAPIERS_ORDRE, t, tp, 'nuit' as Papier);
	const photo = p(t, tf, tf + 0.5, SORT);
	const ouvre = p(t, a9 - 0.1, a9 + 0.5, SORT);
	const mot = t < ts ? 'La cire' : t < tp ? 'le sceau' : t < tf ? 'le papier' : t < a9 ? 'ta photo' : 'une pluie d’étoiles';
	const changeA = [tc, ts, tp, tf, a9].reduce((a, b) => (t >= b ? b : a), tc);
	const pop = p(t, changeA, changeA + 0.3, RESSORT);
	return (
		<AbsoluteFill style={{background: NUIT_FOND, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<Poussiere n={36} force={0.8} graine="habit" />
			<div style={{position: 'absolute', left: 120, top: 330, width: 700}}>
				<div style={{...titre(118), scale: String(mix(0.92, 1, pop)), transformOrigin: 'left center', opacity: mix(0.4, 1, pop)}}>{mot}</div>
				<div style={{display: 'flex', gap: 16, marginTop: 38, height: 56, alignItems: 'center'}}>
					{t < ts &&
						CIRES_ORDRE.map((c) => (
							<span key={c} style={{width: 46, height: 46, borderRadius: '50%', background: `radial-gradient(circle at 34% 30%, ${CIRES[c].clair}, ${CIRES[c].cire} 62%, ${CIRES[c].fonce})`, outline: c === cire ? `3px solid ${C.orDoux}` : 'none', outlineOffset: 4}} />
						))}
					{t >= ts && t < tp &&
						SCEAUX_ORDRE.map((s) => (
							<span key={s} style={{width: 52, height: 52, borderRadius: '50%', display: 'grid', placeItems: 'center', background: '#2a2233', color: C.papier, fontFamily: TITRE, fontSize: 26, outline: s === sceau ? `3px solid ${C.orDoux}` : 'none', outlineOffset: 4}}>
								{s === 'initiale' ? 'K' : (
									<svg viewBox="0 0 24 24" width={28} height={28} style={{fill: 'none', stroke: 'currentColor', strokeWidth: 1.6, strokeLinejoin: 'round'}}>
										{SCEAUX[s as keyof typeof SCEAUX].map((d) => (
											<path key={d} d={d} />
										))}
									</svg>
								)}
							</span>
						))}
					{t >= tp && t < tf &&
						PAPIERS_ORDRE.map((x) => (
							<span key={x} style={{width: 74, height: 50, borderRadius: 6, background: `linear-gradient(160deg, ${PAPIERS[x].papier}, ${PAPIERS[x].papier2})`, outline: x === papier ? `3px solid ${C.orDoux}` : 'none', outlineOffset: 4}} />
						))}
				</div>
			</div>
			<Scene3D camera={[0, 0.25, 5.2]} vise={[0.9, 0.1, 0]} fov={30} expo={1.0}>
				<Lumieres position={[2.6, 2.8, 3.6]} cle={36} />
				<group position={[1.75, 0, 0]} rotation={[-0.15, -0.28 + Math.sin(t * 0.8) * 0.06, 0]}>
					<Enveloppe3D papier={papier} cire={cire} ouvre={ouvre} sort={ouvre * 0.4}>
						<group rotation={[Math.PI / 2, 0, 0]}>
							<Cachet3D cire={cire} sceau={sceau} initiale="K" echelle={0.33} lueur={ouvre} />
						</group>
					</Enveloppe3D>
				</group>
				<Halo3D position={[1.75, 0.6, 0.4]} taille={3} couleur="#ffe2b0" force={vie(t, a9 + 0.4, a9 + 0.55, a9 + 0.7, a9 + 1.6) * 0.8} />
				<SolOmbre y={-1.05} force={0.3} />
			</Scene3D>
			{/* la photo glisse dans l'enveloppe */}
			<div style={{position: 'absolute', left: 1240, top: mix(-420, 300, photo), rotate: `${mix(-18, -4, photo)}deg`, opacity: t < tf ? 0 : 1 - p(t, a9 - 0.2, a9 + 0.1), padding: '14px 14px 44px', background: '#fbf7ef', boxShadow: '0 30px 60px rgba(0,0,0,.5)'}}>
				<Img src={staticFile('malettre-minuit/nuit.jpg')} style={{width: 300, height: 200, objectFit: 'cover', display: 'block'}} />
			</div>
			<Pluie type="etoiles" debut={a9 + 0.5} echelle={3.4} graine="habit-e" />
			<Pluie type="petales" debut={a9 + 0.68} echelle={3.4} graine="habit-p" />
			<Pluie type="confettis" debut={a9 + 0.86} echelle={3.4} graine="habit-c" />
		</AbsoluteFill>
	);
};

/* ── 14 · « Pour la Saint-Valentin… à minuit pile, avant tout le monde » : la lettre arrive la première ── */
const Bulle: React.FC<{titre: string; texte: string; icone: React.ReactNode; y: number; opacite: number; eclat?: number}> = ({titre: tt, texte, icone, y, opacite, eclat = 0}) => (
	<div
		style={{
			position: 'absolute',
			left: 22,
			right: 22,
			top: y,
			padding: '18px 20px',
			borderRadius: 26,
			background: 'rgba(244,237,224,.12)',
			boxShadow: `0 10px 30px rgba(0,0,0,.3), inset 0 0 0 1px rgba(244,237,224,.12), 0 0 ${40 * eclat}px rgba(234,169,187,${0.6 * eclat})`,
			display: 'flex',
			gap: 16,
			alignItems: 'center',
			opacity: opacite,
		}}
	>
		<div style={{width: 54, height: 54, borderRadius: 14, display: 'grid', placeItems: 'center', background: '#2a2233', flex: 'none'}}>{icone}</div>
		<div style={{minWidth: 0}}>
			<div style={{fontFamily: SANS, fontWeight: 700, fontSize: 22, color: C.papier}}>{tt}</div>
			<div style={{fontFamily: SANS, fontSize: 21, color: '#d9d0c4', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{texte}</div>
		</div>
	</div>
);

export const Valentin: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const minuit = L('a11').debut;
	const passe = t >= minuit;
	const nous = p(t, minuit + 0.02, minuit + 0.3, RESSORT);
	const autres = [
		{qui: 'Awa', mot: 'Joyeuse Saint-Valentin !'},
		{qui: 'Groupe Famille', mot: 'Bonne fête des amoureux à tous'},
		{qui: 'Serge', mot: 'Bonne Saint-Val’ ma belle'},
	];
	const rose = CIRES.rose;
	return (
		<AbsoluteFill style={{background: `radial-gradient(110% 90% at 60% 40%, #3a1f2c 0%, ${C.nuit3} 72%)`, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<div style={{position: 'absolute', left: 120, top: 200, width: 800}}>
				<Encre texte="Pour la Saint-Valentin…" debut={L('a10').debut - 0.05} style={titre(92)} />
				<Encre texte="à minuit pile," debut={minuit - 0.05} pas={0.08} style={{...accent(96, rose.lumiere), marginTop: 16}} />
				<Encre texte="avant tout le monde." debut={L('a12').debut - 0.05} style={{...titre(80), marginTop: 10}} />
			</div>
			<div style={{position: 'absolute', left: 1180, top: 40}}>
				<Telephone largeur={470} lueur={0.3 + nous * 0.5}>
					<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #2a1d30 0%, #120d17 100%)'}}>
						<div style={{position: 'absolute', top: 92, width: '100%', textAlign: 'center', fontFamily: SANS, fontSize: 22, color: '#d9d0c4'}}>{passe ? 'dimanche 14 février' : 'samedi 13 février'}</div>
						<div style={{position: 'absolute', top: 120, width: '100%', textAlign: 'center', fontFamily: SANS, fontWeight: 500, fontSize: 112, color: C.papier, letterSpacing: '-0.02em'}}>{passe ? '00:00' : '23:59'}</div>
						<Bulle
							titre="Ma lettre à…"
							texte={LETTRE.attend}
							y={mix(330, 300, nous)}
							opacite={nous}
							eclat={nous}
							icone={<span style={{width: 34, height: 34, borderRadius: '50%', background: `radial-gradient(circle at 34% 30%, ${rose.clair}, ${rose.cire} 62%, ${rose.fonce})`}} />}
						/>
						{autres.map((a, i) => {
							const k = p(t, L('a12').debut + i * 0.16, L('a12').debut + 0.3 + i * 0.16, SORT);
							return <Bulle key={a.qui} titre={a.qui} texte={a.mot} y={mix(780, 420 + i * 112, k)} opacite={k} icone={<span style={{fontFamily: SANS, fontWeight: 700, fontSize: 22, color: C.grisNuit}}>{a.qui[0]}</span>} />;
						})}
					</div>
				</Telephone>
			</div>
			<Pluie type="petales" debut={minuit + 0.05} echelle={3.2} graine="valentin" />
		</AbsoluteFill>
	);
};

/* ── 15 · « Pour t'excuser… sans qu'on te raccroche au nez » : l'appel coupé, puis la lettre ── */
export const Pardon: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const coupe = L('a14').fin - 0.65;
	const raccroche = t >= coupe;
	const secoue = raccroche ? Math.exp(-(t - coupe) / 0.15) * Math.sin((t - coupe) * 50) : 0;
	const lettre = p(t, coupe + 0.25, coupe + 0.8, SORT);
	const duree = Math.max(0, Math.floor(t - debut));
	return (
		<AbsoluteFill style={{background: `radial-gradient(110% 90% at 60% 40%, #1d2233 0%, ${C.nuit3} 72%)`, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<div style={{position: 'absolute', left: 120, top: 220, width: 820}}>
				<Encre texte="Pour t’excuser…" debut={L('a13').debut - 0.05} style={titre(96)} />
				<Encre texte="sans qu’on te raccroche au nez." debut={L('a14').debut - 0.05} pas={0.07} style={{...accent(78), marginTop: 18}} />
			</div>
			<div style={{position: 'absolute', left: 1180, top: 40, translate: `${secoue * 14}px 0`, opacity: 1 - lettre * 0.65, filter: `blur(${lettre * 6}px)`}}>
				<Telephone largeur={470}>
					<div style={{position: 'absolute', inset: 0, background: raccroche ? 'linear-gradient(180deg, #3a1218 0%, #120d17 100%)' : 'linear-gradient(180deg, #1c2a24 0%, #0d1310 100%)'}}>
						<div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center'}}>
							<div style={{width: 130, height: 130, margin: '0 auto', borderRadius: '50%', background: '#2a2233', display: 'grid', placeItems: 'center', fontFamily: TITRE, fontSize: 64, color: C.papier}}>B</div>
							<div style={{fontFamily: SANS, fontWeight: 500, fontSize: 44, color: C.papier, marginTop: 24}}>Bébé</div>
							<div style={{fontFamily: SANS, fontSize: 26, color: raccroche ? '#ff8a8a' : '#a8d5bf', marginTop: 10}}>{raccroche ? 'Appel terminé' : `Appel en cours · 00:0${Math.min(9, duree)}`}</div>
						</div>
						<div style={{position: 'absolute', bottom: 120, left: '50%', translate: '-50% 0', width: 96, height: 96, borderRadius: '50%', background: '#d64545', display: 'grid', placeItems: 'center', scale: String(raccroche ? 0.9 : 1)}}>
							<svg width={46} height={46} viewBox="0 0 24 24" style={{rotate: '135deg'}}>
								<path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z" fill="#fff" />
							</svg>
						</div>
					</div>
				</Telephone>
			</div>
			{/* la lettre, elle, ne raccroche pas */}
			<div style={{position: 'absolute', left: 1120, top: mix(1100, 330, lettre), rotate: `${mix(8, -3, lettre)}deg`, width: 620, height: 400, borderRadius: 10, background: `linear-gradient(160deg, ${PAPIERS.nuit.papier}, ${PAPIERS.nuit.papier2})`, boxShadow: '0 40px 100px rgba(0,0,0,.6)', display: 'grid', placeItems: 'center'}}>
				<div style={{textAlign: 'center'}}>
					<div style={{width: 92, height: 92, margin: '0 auto', borderRadius: '50%', background: `radial-gradient(circle at 34% 30%, ${CIRES.nuit.clair}, ${CIRES.nuit.cire} 62%, ${CIRES.nuit.fonce})`, boxShadow: '0 8px 20px rgba(0,0,0,.5)'}} />
					<div style={{...titre(92, C.papier), marginTop: 24}}>Pardon.</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};

/* ── 16 · « Pour une demande… quand la voix tremble » : les alliances ; la question tremble, puis se pose ── */
export const Demande: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a16 = L('a16').debut;
	const tremble = t >= a16 - 0.1 ? Math.max(0, 1 - (t - (a16 - 0.1)) / 1.0) : 0;
	const dx = bruit('tr', t, 9) * 7 * tremble, dy = bruit('ty', t, 11) * 5 * tremble;
	const coeur = [0, 0.42, 0.79, 1.11].reduce((a, d) => a + Math.max(0, 1 - Math.abs(t - (a16 - 0.1 + d)) / 0.12), 0);
	return (
		<AbsoluteFill style={{background: `radial-gradient(100% 90% at 50% 40%, #4a1820 0%, #1a070b 75%)`, opacity: 1 - p(t, fin - 0.2, fin)}}>
			<Poussiere n={40} couleur="#ffd9a0" force={0.9} graine="demande" />
			<Scene3D camera={[0, 0.35, 4.2]} vise={[0, 0.3, 0]} fov={30} expo={1.1} ciel={0.6}>
				<Lumieres position={[2.4, 3, 3]} cle={30} cleCouleur="#ffe2b8" />
				<Alliances3D tour={t * 0.9} position={[-1.05, -0.35, 0]} echelle={0.72} />
			</Scene3D>
			<div style={{position: 'absolute', left: 120, top: 110}}>
				<Encre texte="Pour une demande…" debut={L('a15').debut - 0.05} style={titre(86)} />
				<Encre texte="quand la voix tremble." debut={a16 - 0.05} pas={0.08} style={{...accent(74, '#f0c6cf'), marginTop: 10}} />
			</div>
			<div style={{position: 'absolute', left: 980, top: 470, width: 780, padding: '50px 40px', boxSizing: 'border-box', borderRadius: 12, background: `linear-gradient(160deg, #fbf7ef, ${C.papier2})`, boxShadow: `0 40px 100px rgba(0,0,0,.55), 0 0 ${60 * coeur}px rgba(234,169,187,${0.45 * coeur})`, textAlign: 'center', opacity: p(t, debut + 0.1, debut + 0.4), rotate: '-1.5deg'}}>
				<div style={{fontFamily: SANS, fontSize: 22, fontWeight: 700, letterSpacing: '0.3em', textTransform: 'uppercase', color: CIRES.bordeaux.cire}}>Demande en mariage</div>
				<div style={{...titre(84, C.encre), marginTop: 18, translate: `${dx}px ${dy}px`}}>Veux-tu m’épouser ?</div>
			</div>
		</AbsoluteFill>
	);
};

/* ── 17 · « Ou la soirée entre potes : l'heure, le lieu… et qui ramène les boissons » ── */
export const Potes: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a17 = L('a17'), a18 = L('a18');
	const coche = (x: number) => p(t, x, x + 0.25, RESSORT);
	const tHeure = a17.debut + 1.05, tLieu = a17.debut + 1.6;
	const tampon = p(t, a18.debut + 0.75, a18.debut + 0.95, ENTRE);
	const items = [
		{lib: 'L’heure', val: 'samedi, 21 h', k: coche(tHeure)},
		{lib: 'Le lieu', val: 'chez Romuald', k: coche(tLieu)},
		{lib: 'Qui ramène les boissons', val: '…', k: p(t, a18.debut, a18.debut + 0.3, SORT)},
	];
	const kraft = PAPIERS.kraft;
	return (
		<AbsoluteFill style={{background: NUIT_FOND, opacity: 1 - p(t, fin - 0.2, fin)}}>
			{/* les autres occasions passent, au loin : il y en a 28 */}
			{[0, 1].map((rang) => (
				<div key={rang} style={{position: 'absolute', top: rang ? 1000 : 40, left: 0, whiteSpace: 'nowrap', fontFamily: TITRE, fontSize: 40, color: C.grisNuit, opacity: 0.35, translate: `${(rang ? -1 : 1) * ((t - debut) * 70) - (rang ? 1400 : 200)}px 0`}}>
					{(rang ? [...OCCASIONS].reverse() : OCCASIONS).join('   ·   ')}
				</div>
			))}
			<div style={{position: 'absolute', left: 120, top: 210, width: 760}}>
				<Encre texte="Ou la soirée entre potes :" debut={a17.debut - 0.05} style={titre(84)} />
				<Encre texte="l’heure, le lieu…" debut={a17.debut + 1.0} pas={0.12} style={{...accent(84), marginTop: 12}} />
				<Encre texte="et qui ramène les boissons." debut={a18.debut - 0.05} pas={0.07} style={{...titre(70), marginTop: 18}} />
			</div>
			<div style={{position: 'absolute', left: 1000, top: 170, width: 800, padding: '54px 56px', boxSizing: 'border-box', borderRadius: 10, background: `linear-gradient(160deg, ${kraft.papier}, ${kraft.papier2})`, boxShadow: '0 40px 100px rgba(0,0,0,.55)', rotate: '1.8deg', opacity: p(t, debut, debut + 0.35)}}>
				<div style={{fontFamily: SANS, fontSize: 22, fontWeight: 700, letterSpacing: '0.3em', textTransform: 'uppercase', color: '#6d4a2a'}}>Soirée entre potes</div>
				<div style={{...titre(70, C.encre), marginTop: 12}}>On remet ça samedi</div>
				<div style={{marginTop: 34, display: 'grid', gap: 22}}>
					{items.map((it) => (
						<div key={it.lib} style={{display: 'flex', alignItems: 'center', gap: 20, opacity: mix(0.35, 1, it.k)}}>
							<span style={{width: 40, height: 40, borderRadius: 10, border: `3px solid ${C.encre}`, display: 'grid', placeItems: 'center', fontFamily: SANS, fontWeight: 700, fontSize: 28, color: CIRES.bordeaux.cire}}>{it.lib.startsWith('Qui') ? '?' : it.k > 0.5 ? '✓' : ''}</span>
							<span style={{fontFamily: SANS, fontSize: 32, color: C.encre}}>
								<b style={{fontWeight: 700}}>{it.lib} :</b> {it.val}
							</span>
						</div>
					))}
				</div>
				<div style={{position: 'absolute', right: 70, bottom: 40, rotate: `${mix(-30, -12, tampon)}deg`, scale: String(mix(2.4, 1, tampon)), opacity: tampon, padding: '6px 26px', border: `5px solid ${CIRES.bordeaux.cire}`, borderRadius: 12, fontFamily: TITRE, fontSize: 92, color: CIRES.bordeaux.cire}}>Toi.</div>
			</div>
			<Pluie type="confettis" debut={a18.debut + 0.1} echelle={3.2} graine="potes" />
		</AbsoluteFill>
	);
};

/* ── 18 · LA FIN : « Ma lettre à… Dès mille francs. Tape un prénom : ta lettre commence. » ── */
export const Fin: React.FC<{debut: number; fin: number}> = ({debut, fin}) => {
	const t = useT();
	const a19 = L('a19'), a20 = L('a20'), a21 = L('a21'), a22 = L('a22');
	const frappe = a21.fin - 0.1;
	const prenom = 'maman'.slice(0, Math.max(0, Math.min(5, Math.floor((t - frappe) / 0.16) + 1)) * (t >= frappe ? 1 : 0));
	const cachet = p(t, a19.debut - 0.1, a19.debut + 0.15, ENTRE);
	const brille = p(t, a20.debut + 0.1, a20.debut + 0.9, (x) => x);
	return (
		<AbsoluteFill style={{background: NUIT_FOND}}>
			<Img src={staticFile('malettre-minuit/nuit.jpg')} style={{...plein, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.45, scale: String(mix(1.1, 1.18, p(t, debut, fin)))}} />
			<Ciel n={180} force={0.7} />
			{/* les lettres montent dans la nuit, comme des lanternes */}
			{Array.from({length: 26}, (_, i) => {
				/* dispersées au hasard sur les côtés : la colonne du milieu reste à la marque */
				const z = random('lz' + i);
				const cote = i % 2 ? 1 : -1;
				const x = 960 + cote * (500 + random('lx' + i) * 430) - 50;
				const y = 1150 - ((t - debut) * (40 + z * 70) + random('ly' + i) * 1100);
				const c = [CIRES.bordeaux, CIRES.or, CIRES.rose, CIRES.sapin, CIRES.nuit][i % 5];
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y, width: 60 + z * 70, height: (60 + z * 70) * 0.62, borderRadius: 4, background: `linear-gradient(160deg, ${C.papier}, ${C.papier2})`, opacity: 0.25 + z * 0.45, filter: `blur(${(1 - z) * 3}px)`, boxShadow: `0 0 ${30 + z * 30}px rgba(255,214,160,${0.25 + z * 0.3})`}}>
						<div style={{position: 'absolute', left: '50%', top: '50%', width: '26%', aspectRatio: '1', translate: '-50% -50%', borderRadius: '50%', background: c.cire}} />
					</div>
				);
			})}
			<div style={{position: 'absolute', left: 0, right: 0, top: 150, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
				<Img src={staticFile('malettre-minuit/logo-cachet.svg')} style={{width: 190, height: 190, scale: String(mix(2.6, 1, cachet)), opacity: cachet, filter: 'drop-shadow(0 18px 30px rgba(0,0,0,.5))'}} />
				<Encre texte="Ma lettre à…" debut={a19.debut + 0.05} pas={0.1} style={{...titre(150), marginTop: 20}} flou={14} />
				<div style={{position: 'relative', marginTop: 10, overflow: 'hidden', padding: '4px 20px'}}>
					<Encre texte="Dès 1 000 F" debut={a20.debut - 0.05} pas={0.12} style={{...accent(84)}} />
					<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(100deg, transparent 30%, rgba(255,250,230,.75) 50%, transparent 70%)', translate: `${mix(-120, 120, brille)}% 0`, mixBlendMode: 'overlay'}} />
				</div>
				{/* le vrai champ de la vitrine : on tape un prénom */}
				<div style={{marginTop: 40, display: 'flex', alignItems: 'center', gap: 18, padding: '16px 18px 16px 34px', borderRadius: 999, background: 'rgba(244,237,224,.1)', boxShadow: 'inset 0 0 0 1.5px rgba(244,237,224,.22)', opacity: p(t, a21.debut - 0.1, a21.debut + 0.25), scale: String(mix(0.94, 1, p(t, a21.debut - 0.1, a21.debut + 0.4, SORT)))}}>
					<span style={{fontFamily: TITRE, fontSize: 52, color: C.papier}}>Ma lettre à</span>
					<span style={{minWidth: 210, fontFamily: TITRE, fontSize: 52, color: C.orDoux, borderBottom: `2px solid ${C.orDoux}88`}}>
						{prenom}
						<span style={{opacity: Math.floor(t * 3) % 2 ? 1 : 0}}>|</span>
					</span>
					<span style={{padding: '18px 34px', borderRadius: 999, background: `linear-gradient(180deg, #fbf4e6, ${C.papier} 55%, #e6d8bf)`, color: C.encre, fontFamily: SANS, fontWeight: 700, fontSize: 30, boxShadow: `0 0 ${40 * p(t, a22.debut, a22.debut + 0.3)}px rgba(255,214,160,.6)`}}>Écrire ma lettre</span>
				</div>
				<div style={{marginTop: 46, fontFamily: SANS, fontWeight: 500, fontSize: 40, letterSpacing: '0.02em', color: C.papier, opacity: p(t, a22.debut + 0.2, a22.debut + 0.6)}}>{ADRESSE}</div>
				<div style={{marginTop: 14, fontFamily: SANS, fontSize: 24, letterSpacing: '0.24em', textTransform: 'uppercase', color: C.grisNuit, opacity: p(t, a22.debut + 0.5, a22.debut + 0.9)}}>by NEBULA Agency</div>
			</div>
		</AbsoluteFill>
	);
};
