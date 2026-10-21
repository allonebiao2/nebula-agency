import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, CIRES, ECRAN, HISTOIRE, SANS, SERIF, type Langue} from '../donnees';
import {Cachet, Encre, Enveloppe, mix, p, T} from '../outils';
import {Decompte} from './Decompte';

/**
 * 5 · L'OUVERTURE · « À l'heure dite, la cire s'allume. On brise le cachet, et on lit. »
 *
 * Trois gestes du produit, dans son ordre :
 *   1. `temps[0]` : le compte tombe à zéro, LA CIRE S'ALLUME (`--cire-lumiere`), la
 *      phrase devient « C'est l'heure. » et le bouton paraît ;
 *   2. `temps[1]` : le doigt enfonce « Briser le cachet », la cire cède en trois
 *      éclats à angles vifs (jamais des pastilles arrondies) ;
 *   3. la feuille se DÉPLIE depuis son pli, et l'encre sèche phrase après phrase :
 *      la lettre que la plume a écrite pour Afi, mot pour mot.
 */

const ECLATS = [
	{x: -190, y: 40, r: -58, forme: 'polygon(48% 0%, 100% 34%, 80% 100%, 14% 84%, 0% 28%)'},
	{x: 90, y: 70, r: 46, forme: 'polygon(0% 14%, 84% 0%, 100% 60%, 42% 100%)'},
	{x: -30, y: -160, r: 18, forme: 'polygon(20% 0%, 100% 22%, 74% 94%, 0% 66%)'},
];

export const Ouverture: React.FC<{t: number; d: number; temps: number[]; fondu: boolean; langue: Langue}> = ({t, d, temps, fondu, langue}) => {
	const E = ECRAN[langue];
	const L = HISTOIRE[langue];
	const h = HISTOIRE.habillage;
	const cire = CIRES[h.cire];
	const [tHeure, tBrise] = [temps[0] ?? 0.5, temps[1] ?? 2.2];
	const sortie = 1 - p(t, d - 0.3, d);
	/* Après « l'attente », l'enveloppe continue au pixel près ; après « scellée »
	   (coupe de 15 s), elle revient en fondu depuis la nuit. */
	const entree = fondu ? p(t, 0, 0.3) : 1;

	const allume = p(t, tHeure, tHeure + 0.5);
	const presse = t < tBrise ? mix(1, 0.955, p(t, tBrise - 0.25, tBrise)) : mix(0.955, 1, p(t, tBrise, tBrise + 0.3));
	const brise = p(t, tBrise, tBrise + 0.15);
	const envPart = p(t, tBrise + 0.2, tBrise + 0.6);
	const deplie = p(t, tBrise + 0.45, tBrise + 1.15);
	const encre = tBrise + 1.0;
	/* L'encre sèche phrase après phrase ; le pas s'adapte à ce qui reste du plan. */
	const phrases = L.paragraphe.match(/[^.!?]+[.!?]+\s*/g) ?? [L.paragraphe];
	const pas = Math.min(0.55, Math.max(0.2, (d - 0.7 - (encre + 0.7)) / phrases.length));

	return (
		<AbsoluteFill style={{opacity: sortie * entree}}>
			{/* Avant le brisement : l'enveloppe du plan précédent, au même endroit. */}
			<div style={{position: 'absolute', top: 300, width: '100%', opacity: 1 - envPart}}>
				<Encre t={t} a={tHeure} style={{fontFamily: SERIF, fontSize: 92, color: C.papier, textAlign: 'center', padding: '0 60px'}}>
					{E.heureDite}
				</Encre>
			</div>
			<div style={{position: 'absolute', left: '50%', top: 820, translate: `-50% ${envPart * 120}px`, opacity: 1 - envPart}}>
				<Enveloppe h={h} largeur={780} t={t} sansCachet>
					<div style={{position: 'absolute', left: '50%', top: '52%', translate: '-50% -50%', opacity: 1 - brise}}>
						<Cachet h={h} taille={195} t={t} lumiere={allume * (0.75 + 0.25 * Math.sin(t * 5))} />
					</div>
					{ECLATS.map((e) => {
						const k = p(t, tBrise, tBrise + 0.85);
						return (
							<div
								key={e.forme}
								style={{
									position: 'absolute',
									left: '50%',
									top: '52%',
									width: 84,
									height: 84,
									background: `radial-gradient(circle at 40% 34%,${cire.clair},${cire.cire} 70%)`,
									clipPath: e.forme,
									opacity: t < tBrise ? 0 : 1 - k,
									translate: `${mix(-50, e.x, k)}% ${mix(-50, e.y, k)}%`,
									rotate: `${e.r * k}deg`,
								}}
							/>
						);
					})}
				</Enveloppe>
			</div>
			<div style={{position: 'absolute', top: 1340, width: '100%', opacity: 1 - envPart}}>
				<div style={{fontFamily: SANS, fontSize: 40, color: C.grisNuit, textAlign: 'center', height: 56}}>
					{t < tHeure ? (
						<>
							{L.ouvre[0]}
							<b style={{color: C.papier, fontWeight: 600}}>{L.ouvre[1]}</b>
							{L.ouvre[2]}
						</>
					) : (
						<span style={{color: C.papier}}>{L.heure}</span>
					)}
				</div>
				<div style={{position: 'relative', height: 190, marginTop: 34}}>
					<Decompte reste={tHeure - t} style={{position: 'absolute', inset: 0, opacity: 1 - p(t, tHeure + 0.1, tHeure + 0.4)}} />
					<div
						style={{
							position: 'absolute',
							left: '50%',
							top: 30,
							translate: '-50% 0',
							padding: '34px 80px',
							borderRadius: 999,
							background: C.papier,
							color: C.encre,
							fontFamily: SANS,
							fontWeight: 700,
							fontSize: 46,
							whiteSpace: 'nowrap',
							boxShadow: '0 24px 60px rgba(0,0,0,.4)',
							opacity: p(t, tHeure + 0.25, tHeure + 0.6),
							scale: String(presse),
						}}
					>
						{E.briser}
					</div>
				</div>
			</div>

			{/* La feuille : elle s'ouvre depuis son pli central, puis l'encre sèche. */}
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: 300,
					width: 920,
					translate: '-50% 0',
					padding: '64px 64px 70px',
					boxSizing: 'border-box',
					background: `linear-gradient(168deg,${C.papier} 0%,${C.papier2} 100%)`,
					borderRadius: 18,
					boxShadow: '0 60px 140px rgba(0,0,0,.55)',
					transformOrigin: '50% 30%',
					scale: `1 ${mix(0.04, 1, deplie)}`,
					opacity: p(t, tBrise + 0.4, tBrise + 0.55),
				}}
			>
				<Encre t={t} a={encre} style={{fontFamily: SANS, fontSize: 36, fontWeight: 700, letterSpacing: '0.26em', textTransform: 'uppercase', color: cire.cire, textAlign: 'center'}}>
					{L.occasion}
				</Encre>
				<Encre t={t} a={encre + 0.2} style={{fontFamily: SERIF, fontSize: 76, lineHeight: 1.16, color: C.encre, textAlign: 'center', marginTop: 20}}>
					{L.titre}
				</Encre>
				<div style={{width: 132, height: 5, margin: '28px auto 44px', background: C.or, borderRadius: 3, scale: `${T(p(t, encre + 0.35, encre + 0.8))} 1`}} />
				<div style={{fontFamily: SERIF, fontSize: 44, lineHeight: 1.6, color: C.encre}}>
					{phrases.map((ph, i) => {
						const a = encre + 0.7 + i * pas;
						const k = p(t, a, a + 0.5);
						return (
							<span key={i} style={{opacity: k, filter: `blur(${(1 - k) * 8}px)`}}>
								{ph}
							</span>
						);
					})}
				</div>
				<Encre t={t} a={encre + 0.7 + phrases.length * pas} style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 44, color: C.gris, textAlign: 'right', marginTop: 36}}>
					{L.formule}
					<br />
					<span style={{fontStyle: 'normal', color: C.encre}}>{L.de}</span>
				</Encre>
			</div>
		</AbsoluteFill>
	);
};
