import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, ECRAN, PRENOMS, SERIF, type Langue} from '../donnees';
import {Encre, Enveloppe, mix, p, vie} from '../outils';

/**
 * 1 · L'ACCROCHE · « Ma lettre à… papa. À Afi. À maman. »
 *
 * Signature : LE PRÉNOM QUI SE REMPLIT. « Ma lettre à… » est le nom du produit et
 * il finit par un vide ; la vidéo le remplit, un prénom après l'autre, et sous
 * chaque prénom arrive SA lettre, avec l'habillage réel de son exemple (papa : cire
 * d'or, couronne, kraft · Afi : cire rose, cœur · maman : bordeaux, cœur).
 * Avant le premier prénom, le curseur clignote là où il s'écrira : c'est le champ
 * « Son prénom » du constructeur.
 */
export const Accroche: React.FC<{t: number; d: number; temps: number[]; langue: Langue}> = ({t, d, temps, langue}) => {
	const rang = temps.filter((x) => t >= x).length - 1;
	const sortie = 1 - p(t, d - 0.3, d);
	const curseur = rang < 0 && Math.floor(t * 2.4) % 2 === 0;

	return (
		<AbsoluteFill style={{opacity: sortie}}>
			<div style={{position: 'absolute', top: 360, width: '100%', textAlign: 'center'}}>
				<Encre t={t} a={0.05} duree={0.5} style={{fontFamily: SERIF, fontSize: 118, color: C.papier}}>
					{ECRAN[langue].accroche}
				</Encre>
				<div style={{position: 'relative', height: 200, marginTop: 18}}>
					{PRENOMS.map((n, i) => {
						const a = temps[i];
						const b = temps[i + 1] ?? d + 1;
						/* Le prénom sèche en arrivant, et s'efface juste avant le suivant. */
						const k = Math.min(p(t, a, a + 0.32), 1 - p(t, b - 0.12, b + 0.08));
						if (k <= 0) return null;
						return (
							<div
								key={n.fr}
								style={{
									position: 'absolute',
									inset: 0,
									fontFamily: SERIF,
									fontStyle: 'italic',
									fontSize: 170,
									color: C.orDoux,
									opacity: k,
									filter: `blur(${(1 - k) * 10}px)`,
								}}
							>
								{langue === 'fr' ? n.fr : n.en}.
							</div>
						);
					})}
					<div
						style={{
							position: 'absolute',
							left: '50%',
							top: 30,
							width: 6,
							height: 150,
							background: C.orDoux,
							opacity: curseur && t > 0.4 ? 0.9 : 0,
						}}
					/>
				</div>
			</div>

			{/* Les enveloppes : chacune glisse depuis la droite, la précédente part à gauche. */}
			{PRENOMS.map((n, i) => {
				const a = temps[i];
				const b = temps[i + 1] ?? d + 10;
				const entree = p(t, a - 0.08, a + 0.5);
				const depart = p(t, b - 0.12, b + 0.4);
				if (entree <= 0 || depart >= 1) return null;
				return (
					<div
						key={n.fr}
						style={{
							position: 'absolute',
							left: '50%',
							top: 1010,
							translate: `${mix(mix(70, -50, entree), -170, depart)}% 0%`,
							rotate: `${mix(mix(7, -2 + i * 2, entree), -9, depart)}deg`,
							opacity: Math.min(entree, 1 - depart),
						}}
					>
						<Enveloppe h={n.habillage} largeur={700} t={t} />
					</div>
				);
			})}
			{/* Avant le premier prénom : l'enveloppe encore anonyme, sans cachet. */}
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: 1010,
					translate: '-50% 0%',
					rotate: '-2deg',
					opacity: vie(t, 0.15, 0.5, temps[0] - 0.12, temps[0] + 0.1) * 0.9,
				}}
			>
				<Enveloppe h={PRENOMS[1].habillage} largeur={700} t={t} sansCachet />
			</div>
		</AbsoluteFill>
	);
};
