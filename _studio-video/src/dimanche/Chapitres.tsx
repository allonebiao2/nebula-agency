/**
 * LE REPÈRE · en haut à gauche, sur le mur (le visage est au centre).
 * Six onglets comme ceux d'un agenda : celui du chapitre en cours se remplit
 * au fil du discours ; au changement, le nom glisse vers le haut et le suivant
 * monte, comme une page qu'on tourne. Il retient sur 3 min 30.
 */
import React from 'react';
import {interpolate} from 'remotion';
import {C, CHAPITRES, DEBUT_FIN} from './donnees';
import {p, ressort} from './outils';
import {TEXTE, TITRE} from './polices';

export const Chapitres: React.FC<{t: number}> = ({t}) => {
	if (t < 0.8 || t > DEBUT_FIN) return null;
	const n = CHAPITRES.reduce((acc, c, i) => (t >= c.debut ? i : acc), 0);
	const apparition = p(t, 0.8, 1.4);

	return (
		<div
			style={{
				position: 'absolute',
				left: 36,
				top: 214,
				opacity: apparition,
				transform: `translateX(${(1 - apparition) * -30}px)`,
				padding: '14px 18px 16px',
				borderRadius: 20,
				background: 'rgba(12,15,21,.62)',
				boxShadow: '0 12px 30px -10px rgba(0,0,0,.5)',
			}}
		>
			<div style={{position: 'relative', height: 40, width: 322, overflow: 'hidden'}}>
				{CHAPITRES.map((c, i) => {
					if (Math.abs(i - n) > 1) return null;
					const r = ressort(t, c.debut, {damping: 18, stiffness: 180});
					const suiv = CHAPITRES[i + 1];
					const part = suiv ? ressort(t, suiv.debut, {damping: 18, stiffness: 180}) : 0;
					const y = interpolate(r, [0, 1], [44, 0]) - part * 44;
					if (t < c.debut - 0.05 || part >= 0.999) return null;
					return (
						<div
							key={c.nom}
							style={{
								position: 'absolute',
								left: 0,
								top: 0,
								display: 'flex',
								alignItems: 'baseline',
								gap: 14,
								transform: `translateY(${y}px)`,
								whiteSpace: 'nowrap',
							}}
						>
							<span style={{fontFamily: TITRE, fontWeight: 900, fontSize: 36, color: C.surligneur, lineHeight: 1}}>
								{String(i + 1).padStart(2, '0')}
							</span>
							<span
								style={{
									fontFamily: TEXTE,
									fontWeight: 800,
									fontSize: 22,
									letterSpacing: '0.1em',
									textTransform: 'uppercase',
									color: C.blanc,
								}}
							>
								{c.nom}
							</span>
						</div>
					);
				})}
			</div>
			<div style={{display: 'flex', gap: 8, marginTop: 12}}>
				{CHAPITRES.map((c, i) => {
					const fin = CHAPITRES[i + 1]?.debut ?? DEBUT_FIN;
					const plein = interpolate(t, [c.debut, fin], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
					return (
						<div key={c.nom} style={{width: 47, height: 6, borderRadius: 3, background: 'rgba(251,248,241,.22)', overflow: 'hidden'}}>
							<div style={{width: `${plein * 100}%`, height: '100%', background: i === n ? C.surligneur : C.blanc}} />
						</div>
					);
				})}
			</div>
		</div>
	);
};
