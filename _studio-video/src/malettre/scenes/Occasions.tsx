import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, OCCASIONS, SANS, type Langue} from '../donnees';
import {Cachet, Enveloppe, mix, p} from '../outils';

/**
 * 6 · LES OCCASIONS · « Un anniversaire, une demande, un pardon, une fête. »
 *
 * Signature : QUATRE CACHETS PRESSÉS, un par mot de la voix. Chaque enveloppe porte
 * un habillage différent du produit (or, bordeaux, nuit, sapin) et, dessous, le nom
 * EXACT de l'occasion dans le constructeur. La plus récente est au premier plan,
 * les autres reculent d'un pas : c'est une pile de lettres, pas une grille de cases.
 */
const PLACES = [
	{x: 290, y: 600, r: -4},
	{x: 790, y: 650, r: 3},
	{x: 290, y: 1130, r: 2},
	{x: 790, y: 1180, r: -3},
];

export const Occasions: React.FC<{t: number; d: number; temps: number[]; langue: Langue}> = ({t, d, temps, langue}) => {
	const sortie = 1 - p(t, d - 0.3, d);
	const dernier = temps.filter((x) => t >= x).length - 1;

	return (
		<AbsoluteFill style={{opacity: sortie}}>
			{OCCASIONS.map((o, i) => {
				const a = temps[i] ?? i;
				const k = p(t, a - 0.1, a + 0.35);
				const presse = p(t, a + 0.05, a + 0.4);
				const ecrase = t < a + 0.4 ? mix(1.3, 1, presse) : 1 + 0.1 * Math.max(0, 1 - (t - a - 0.4) / 0.2);
				const recule = i < dernier ? 0.94 : 1;
				const pl = PLACES[i];
				return (
					<div
						key={o.fr}
						style={{
							position: 'absolute',
							left: pl.x,
							top: pl.y,
							translate: `-50% ${mix(70, 0, k)}px`,
							rotate: `${pl.r}deg`,
							opacity: k,
							/* Reculer, c'est s'assombrir un peu : jamais de transparence, qui
							   rendrait le papier gris sur la nuit. */
							filter: i < dernier ? 'brightness(.8)' : undefined,
							scale: String(recule),
							display: 'flex',
							flexDirection: 'column',
							alignItems: 'center',
							gap: 30,
						}}
					>
						<Enveloppe h={o.habillage} largeur={470} t={t} sansCachet>
							<div style={{position: 'absolute', left: '50%', top: '52%', translate: '-50% -50%', opacity: presse > 0 ? 1 : 0}}>
								<Cachet h={o.habillage} taille={120} t={t} style={{scale: `${ecrase} ${2 - ecrase}`}} />
							</div>
						</Enveloppe>
						<div style={{fontFamily: SANS, fontSize: 32, fontWeight: 600, letterSpacing: '0.2em', textTransform: 'uppercase', color: C.orDoux, whiteSpace: 'nowrap'}}>
							{langue === 'fr' ? o.fr : o.en}
						</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};
