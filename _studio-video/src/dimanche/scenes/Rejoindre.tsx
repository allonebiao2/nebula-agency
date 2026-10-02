/**
 * CHAPITRE 6 · REJOINDRE (2:51 → 3:29) et LA CARTE DE FIN
 *
 *  · TU ES ICI      « si tu es dans ce canal, en train de voir cette vidéo » :
 *                   l'épingle tombe, puis « pas encore membre ? ».
 *  · LA FORMATION   la semaine prochaine, MERCREDI et JEUDI entourés au stylo ;
 *                   le BILLET « formation 100 % gratuite » avec son talon
 *                   détachable ; puis le bouton « réserve ta place », qu'on
 *                   presse sur « immédiatement ».
 *  · LE LIVE        l'horloge tourne jusqu'à 21:00, la pastille LIVE bat,
 *                   « majestueux » fait jaillir des étincelles, la discussion
 *                   s'écrit en bulles (sans texte inventé).
 *  · SEPTEMBRE      « une nouvelle dimension » : des ondes, et le mois.
 *  · LA FIN         la vidéo s'arrête en pleine phrase : la carte de fin atterrit.
 *
 * ⚠️ Pas de « lien en bio » : on ne sait pas où l'inscription se fait. Le
 * bouton dit ce qu'il dit, lui : « réserve ta place ».
 */
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, COMMUNAUTE, DEBUT_FIN, d, fi} from '../donnees';
import {Ecrit, Etiquette, Feuille, Surligne, Trait, fenetre, p, ressort} from '../outils';
import {MAIN, TEXTE, TITRE} from '../polices';
import {Horloge, Marque} from './Communaute';

/* ───────────────────────── TU ES ICI ───────────────────────── */

export const TuEsIci: React.FC<{t: number}> = ({t}) => {
	const a = d(677) - 0.1;
	const b = d(711) - 0.3;
	const w = fenetre(t, a, b);
	if (!w.vis) return null;
	const chute = ressort(t, d(683) - 0.1, {damping: 8, stiffness: 180, mass: 0.8});
	const membre = p(t, d(702) - 0.1, d(702) + 0.3);
	return (
		<div
			style={{
				position: 'absolute',
				left: 64,
				right: 140,
				top: 1250,
				height: 250,
				borderRadius: 30,
				background: 'rgba(16,19,26,.82)',
				opacity: Math.min(1, w.e * 2) * (1 - w.s),
				transform: `translateY(${(1 - w.e) * 60 + w.s * 60}px)`,
				display: 'flex',
				alignItems: 'center',
				gap: 34,
				paddingLeft: 50,
				boxShadow: '0 30px 60px -24px rgba(0,0,0,.7)',
			}}
		>
			<svg width={110} height={150} viewBox="0 0 110 150" style={{overflow: 'visible', transform: `translateY(${(1 - chute) * -180}px)`}}>
				<ellipse cx={55} cy={140} rx={30 * chute} ry={8 * chute} fill="rgba(0,0,0,.4)" />
				<path d="M55 132 C28 96 10 74 10 50 A45 45 0 0 1 100 50 C100 74 82 96 55 132 Z" fill={C.surligneur} stroke={C.encre} strokeWidth={5} />
				<circle cx={55} cy={50} r={17} fill={C.encre} />
			</svg>
			<div style={{position: 'relative', height: 170, flex: 1}}>
				<div style={{position: 'absolute', top: 20, opacity: 1 - membre, transform: `translateY(${-membre * 30}px)`}}>
					<Ecrit v={p(t, d(683), d(685))} taille={86} couleur={C.blanc}>
						tu es ici
					</Ecrit>
					<Etiquette taille={24} couleur={C.gris} style={{marginTop: 18}}>
						devant cette vidéo
					</Etiquette>
				</div>
				<div style={{position: 'absolute', top: 30, opacity: membre, transform: `translateY(${(1 - membre) * 30}px)`}}>
					<Etiquette taille={24} couleur={C.gris}>
						pas encore membre de
					</Etiquette>
					<div style={{fontFamily: TITRE, fontWeight: 900, fontSize: 70, color: C.surligneur, lineHeight: 1.05, textTransform: 'uppercase', marginTop: 8}}>
						{COMMUNAUTE} ?
					</div>
				</div>
			</div>
		</div>
	);
};

/* ───────────────────────── LA FORMATION ───────────────────────── */

const JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

export const Formation: React.FC<{t: number}> = ({t}) => {
	const a = d(711) - 0.2;
	const b = d(782) - 0.25;
	const cal = fenetre(t, a, b);
	const bil = fenetre(t, d(723) - 0.15, b);
	if (!cal.vis) return null;

	const listes = p(t, d(768) - 0.2, d(768) + 0.1);
	const bouton = ressort(t, d(768), {damping: 11, stiffness: 200});
	const presse = p(t, d(781) - 0.05, d(781) + 0.12) * (1 - p(t, d(781) + 0.12, d(781) + 0.4));
	const onde = p(t, d(781), d(781) + 0.7, Easing.out(Easing.cubic));
	const pouls = t >= d(768) + 0.4 ? 1 + 0.03 * Math.sin((t - d(768)) * 6) : 1;

	return (
		<>
			{/* la semaine prochaine, deux jours entourés */}
			<Feuille x={64} y={730} l={876} h={260} e={cal.e} s={cal.s} incline={-1}>
				<div style={{position: 'absolute', left: 40, top: 22}}>
					<Ecrit v={p(t, d(716), fi(719))} taille={48}>
						la semaine prochaine
					</Ecrit>
				</div>
				{JOURS.map((j, n) => (
					<div
						key={j}
						style={{
							position: 'absolute',
							left: 40 + n * 116,
							top: 104,
							width: 104,
							height: 110,
							borderRadius: 14,
							border: `3px solid ${C.stylo}`,
							background: n === 2 || n === 3 ? C.surligneur : 'rgba(255,255,255,.35)',
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							fontFamily: TITRE,
							fontWeight: 800,
							fontSize: 40,
							color: C.stylo,
							textTransform: 'uppercase',
							opacity: p(t, a + 0.2 + n * 0.04, a + 0.5 + n * 0.04),
						}}
					>
						{j}
					</div>
				))}
				<svg width={876} height={260} style={{position: 'absolute', left: 0, top: 0}}>
					<Trait d="M320 100 C250 104 262 226 330 224 C398 222 410 104 338 96" v={p(t, d(712) - 0.1, d(712) + 0.45, Easing.linear)} couleur={C.rouge} epaisseur={6} />
					<Trait d="M436 100 C366 104 378 226 446 224 C514 222 526 104 454 96" v={p(t, d(715) - 0.1, d(715) + 0.45, Easing.linear)} couleur={C.rouge} epaisseur={6} />
				</svg>
			</Feuille>

			{/* le billet */}
			{bil.vis ? (
				<Feuille x={64} y={1030} l={876} h={570} e={bil.e} s={bil.s} incline={1.2}>
					<div style={{position: 'absolute', left: 40, top: 36, fontFamily: TITRE, fontWeight: 900, fontSize: 132, lineHeight: 0.9, color: C.stylo}}>
						FORMATION
					</div>
					<div style={{position: 'absolute', left: 36, top: 168}}>
						<Surligne v={p(t, d(726) - 0.05, d(726) + 0.3)}>
							<span
								style={{
									fontFamily: TITRE,
									fontWeight: 900,
									fontSize: 96,
									lineHeight: 1,
									color: C.stylo,
									opacity: p(t, d(724) - 0.1, d(724) + 0.15),
								}}
							>
								100 % GRATUITE
							</span>
						</Surligne>
					</div>
					{/* ce qu'on y apprend, puis le bouton qui prend la place */}
					<div style={{position: 'absolute', left: 40, top: 312, opacity: 1 - listes}}>
						{[
							['apprendre à trader', d(733) - 0.2],
							['les bons comportements', d(741) - 0.2],
							['en faire un business', d(752) - 0.2],
							['en vivre, épanoui', d(758) - 0.2],
						].map(([texte, quand], n) => (
							<div key={n} style={{display: 'flex', alignItems: 'center', gap: 16, height: 58}}>
								<svg width={38} height={38} viewBox="0 0 60 60">
									<Trait d="M10 31 L25 45 L52 10" v={p(t, quand as number, (quand as number) + 0.3, Easing.linear)} couleur={C.vert} epaisseur={9} />
								</svg>
								<Ecrit v={p(t, quand as number, (quand as number) + 0.8)} taille={48}>
									{texte as string}
								</Ecrit>
							</div>
						))}
					</div>
					{t >= d(768) ? (
						<div
							style={{
								position: 'absolute',
								left: 40,
								top: 350,
								width: 600,
								height: 140,
								borderRadius: 70,
								background: C.encre,
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
								opacity: Math.min(1, bouton * 2),
								transform: `scale(${interpolate(bouton, [0, 1], [0.7, 1]) * pouls * (1 - presse * 0.07)})`,
								boxShadow: `0 ${18 - presse * 12}px 36px -14px rgba(0,0,0,.55)`,
							}}
						>
							<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 66, color: C.surligneur, letterSpacing: '0.03em'}}>RÉSERVE TA PLACE</span>
							{onde > 0 && onde < 1 ? (
								<div
									style={{
										position: 'absolute',
										left: '50%',
										top: '50%',
										width: 140,
										height: 140,
										borderRadius: 70,
										border: `6px solid ${C.surligneur}`,
										transform: `translate(-50%,-50%) scale(${1 + onde * 4})`,
										opacity: 1 - onde,
									}}
								/>
							) : null}
						</div>
					) : null}
					{/* le talon, détachable */}
					<svg width={876} height={570} style={{position: 'absolute', left: 0, top: 0}}>
						<line x1={690} x2={690} y1={30} y2={540} stroke="rgba(28,43,75,.4)" strokeWidth={4} strokeDasharray="4 14" strokeLinecap="round" />
						<circle cx={690} cy={0} r={26} fill="#0b0d12" />
						<circle cx={690} cy={570} r={26} fill="#0b0d12" />
					</svg>
					<div
						style={{
							position: 'absolute',
							left: 690,
							width: 186,
							top: 0,
							bottom: 0,
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
						}}
					>
						<div style={{transform: 'rotate(-90deg)', whiteSpace: 'nowrap', fontFamily: TITRE, fontWeight: 900, fontSize: 64, color: C.rouge, letterSpacing: '0.04em'}}>
							MER · JEU
						</div>
					</div>
				</Feuille>
			) : null}
		</>
	);
};

/* ───────────────────────── LE LIVE ───────────────────────── */

export const Live: React.FC<{t: number}> = ({t}) => {
	const marqueA = d(782) - 0.1;
	const marqueB = d(796) - 0.3;
	const a = d(796) - 0.25;
	const b = d(826) - 0.25;
	const m = fenetre(t, marqueA, marqueB, 0.25);
	const w = fenetre(t, a, b);
	if (!m.vis && !w.vis) return null;

	const titre = ressort(t, d(799) + 0.3, {damping: 12, stiffness: 190});
	const etincelles = p(t, d(803) - 0.05, d(803) + 0.9, Easing.out(Easing.cubic));

	return (
		<>
			{m.vis ? (
				<Feuille x={64} y={1200} l={876} h={340} e={m.e} s={m.s} sombre>
					<div style={{position: 'absolute', left: 44, top: 36}}>
						<Ecrit v={p(t, d(783), d(788))} taille={46} couleur={C.surligneur}>
							tous les membres de
						</Ecrit>
					</div>
					<div style={{position: 'absolute', left: 44, top: 110}}>
						<Marque t={t} a={d(789) - 0.15} taille={92} />
					</div>
				</Feuille>
			) : null}
			{w.vis ? (
				<Feuille x={64} y={740} l={876} h={860} e={w.e} s={w.s} sombre incline={-0.8}>
					<svg width={876} height={860} style={{position: 'absolute', left: 0, top: 0}}>
						<Horloge t={t} x={438} y={250} r={180} debut={d(796) + 0.1} arrivee={d(799) + 0.45} couleur={C.blanc} />
						{/* « majestueux » : les étincelles */}
						{etincelles > 0 && etincelles < 1
							? Array.from({length: 10}, (_, i) => {
									const ang = (i / 10) * Math.PI * 2 + 0.3;
									const rr = 250 + etincelles * 170;
									const x = 438 + Math.cos(ang) * rr;
									const y = 560 + Math.sin(ang) * rr * 0.55;
									const s = (1 - etincelles) * 22;
									return (
										<path
											key={i}
											d={`M${x} ${y - s} L${x + s * 0.28} ${y - s * 0.28} L${x + s} ${y} L${x + s * 0.28} ${y + s * 0.28} L${x} ${y + s} L${x - s * 0.28} ${y + s * 0.28} L${x - s} ${y} L${x - s * 0.28} ${y - s * 0.28} Z`}
											fill={C.surligneur}
										/>
									);
								})
							: null}
					</svg>
					<div style={{position: 'absolute', left: 0, right: 0, top: 470, display: 'flex', justifyContent: 'center', opacity: p(t, d(802) - 0.1, d(802) + 0.2)}}>
						<div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '12px 30px', borderRadius: 40, background: C.rouge}}>
							<div style={{width: 20, height: 20, borderRadius: 10, background: C.blanc, opacity: 0.4 + 0.6 * Math.abs(Math.sin(t * 3.2))}} />
							<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 48, color: C.blanc, letterSpacing: '0.12em'}}>LIVE</span>
						</div>
					</div>
					<div
						style={{
							position: 'absolute',
							left: 0,
							right: 0,
							top: 560,
							textAlign: 'center',
							fontFamily: TITRE,
							fontWeight: 900,
							fontSize: 124,
							lineHeight: 1,
							color: C.blanc,
							opacity: Math.min(1, titre * 2),
							transform: `scale(${interpolate(titre, [0, 1], [0.7, 1])})`,
						}}
					>
						CE SOIR · <span style={{color: C.surligneur}}>21 H</span>
					</div>
					{/* « on va discuter de beaucoup de choses » : des bulles, sans rien y faire dire */}
					<div style={{position: 'absolute', left: 60, right: 60, top: 720, display: 'flex', justifyContent: 'center', gap: 26}}>
						{[0, 1, 2].map((n) => {
							const r = ressort(t, d(810) - 0.1 + n * 0.3, {damping: 11, stiffness: 220});
							return (
								<div
									key={n}
									style={{
										width: 150,
										height: 78,
										borderRadius: 26,
										borderBottomLeftRadius: n % 2 ? 26 : 6,
										borderBottomRightRadius: n % 2 ? 6 : 26,
										background: n === 1 ? C.surligneur : 'rgba(251,248,241,.14)',
										display: 'flex',
										alignItems: 'center',
										justifyContent: 'center',
										gap: 10,
										opacity: Math.min(1, r * 2),
										transform: `translateY(${(1 - r) * 30}px) scale(${interpolate(r, [0, 1], [0.6, 1])})`,
									}}
								>
									{[0, 1, 2].map((k) => (
										<div
											key={k}
											style={{
												width: 12,
												height: 12,
												borderRadius: 6,
												background: n === 1 ? C.encre : C.blanc,
												transform: `translateY(${-6 * Math.max(0, Math.sin(t * 7 - k * 0.8 - n))}px)`,
											}}
										/>
									))}
								</div>
							);
						})}
					</div>
				</Feuille>
			) : null}
		</>
	);
};

/* ───────────────────────── SEPTEMBRE ───────────────────────── */

export const Septembre: React.FC<{t: number}> = ({t}) => {
	const a = d(826) - 0.3;
	const b = DEBUT_FIN - 0.1;
	const w = fenetre(t, a, b, 0.4);
	if (!w.vis) return null;
	return (
		<Feuille x={64} y={1180} l={876} h={380} e={w.e} s={w.s} sombre>
			<svg width={876} height={380} style={{position: 'absolute', left: 0, top: 0}}>
				{[0, 1, 2, 3].map((n) => {
					const k = ((t - d(826) - n * 0.45) % 1.8) / 1.8;
					if (t < d(826) + n * 0.45) return null;
					return <circle key={n} cx={438} cy={230} r={40 + k * 420} fill="none" stroke={C.surligneur} strokeWidth={4} opacity={(1 - k) * 0.6} />;
				})}
			</svg>
			<div style={{position: 'absolute', left: 0, right: 0, top: 44, textAlign: 'center'}}>
				<Ecrit v={p(t, d(825), fi(827))} taille={52} couleur={C.surligneur} style={{display: 'inline-block'}}>
					une nouvelle dimension
				</Ecrit>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 150, display: 'flex', justifyContent: 'center'}}>
				{'SEPTEMBRE'.split('').map((l, i) => {
					const r = ressort(t, d(831) - 0.15 + i * 0.04, {damping: 13, stiffness: 240});
					return (
						<span
							key={i}
							style={{
								fontFamily: TITRE,
								fontWeight: 900,
								fontSize: 170,
								lineHeight: 1,
								color: C.blanc,
								display: 'inline-block',
								opacity: Math.min(1, r * 2),
								transform: `translateY(${(1 - r) * 50}px) scale(${interpolate(r, [0, 1], [1.3, 1])})`,
							}}
						>
							{l}
						</span>
					);
				})}
			</div>
		</Feuille>
	);
};

/* ───────────────────────── LA CARTE DE FIN ───────────────────────── */

export const CarteDeFin: React.FC<{t: number}> = ({t}) => {
	const a = DEBUT_FIN;
	if (t < a) return null;
	const l = (n: number) => ressort(t, a + 0.25 + n * 0.22, {damping: 14, stiffness: 170});
	const ligne = (n: number, enfant: React.ReactNode, style?: React.CSSProperties) => (
		<div style={{opacity: Math.min(1, l(n) * 2), transform: `translateY(${(1 - l(n)) * 40}px)`, ...style}}>{enfant}</div>
	);
	return (
		<div style={{position: 'absolute', left: 64, right: 64, top: 640, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26, textAlign: 'center'}}>
			{ligne(0, <Etiquette taille={32} couleur={C.surligneur}>{COMMUNAUTE}</Etiquette>)}
			{ligne(
				1,
				<div style={{fontFamily: MAIN, fontWeight: 700, fontSize: 128, lineHeight: 1, color: C.blanc}}>Planifie ta semaine.</div>,
			)}
			{ligne(
				2,
				<Surligne v={p(t, a + 1.0, a + 1.35)}>
					<span style={{fontFamily: MAIN, fontWeight: 700, fontSize: 128, lineHeight: 1, color: t >= a + 1.2 ? C.encre : C.blanc}}>Exécute ton plan.</span>
				</Surligne>,
			)}
			{ligne(
				3,
				<div style={{display: 'flex', flexDirection: 'column', gap: 18, marginTop: 40, alignItems: 'center'}}>
					<div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '16px 34px', borderRadius: 40, background: C.rouge}}>
						<div style={{width: 18, height: 18, borderRadius: 9, background: C.blanc, opacity: 0.4 + 0.6 * Math.abs(Math.sin(t * 3.2))}} />
						<span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 34, color: C.blanc, letterSpacing: '0.1em', textTransform: 'uppercase'}}>
							Live ce soir · 21 h
						</span>
					</div>
					<div style={{padding: '16px 34px', borderRadius: 40, background: C.surligneur}}>
						<span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 34, color: C.encre, letterSpacing: '0.1em', textTransform: 'uppercase'}}>
							Formation 100 % gratuite
						</span>
					</div>
				</div>,
			)}
		</div>
	);
};
