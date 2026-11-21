/**
 * LE FILM 16:9 (1920 x 1080) : la nuit, un seul halo violet qui respire derrière l'élément du moment, et un élément
 * par phrase. Il est joué tel quel (PubEcranNebula169) et sur le moniteur de la pièce (PubEcranNebulaTikTok).
 */
import React from 'react';
import {C, ECRAN} from './donnees';
import {halo, respiration} from './etat';
import {rgba} from './outils';
import {Appuie, Boutique, Produits, Retiens} from './PlansMilieu';
import {Commande, Ecris, Noel, Pret, Signature} from './PlansFin';
import {Nuit, Statut} from './PlansNuit';

/** Le halo : une lumière large et floue, posée un peu SOUS l'élément (elle l'éclaire par en dessous, comme dans B). */
export const Halo: React.FC<{t: number}> = ({t}) => {
	const h = halo(t);
	const r = respiration(t);
	const force = h.force * r.opacite;
	if (force < 0.003) return null;
	const T = h.taille;
	return (
		<div
			style={{
				position: 'absolute',
				left: h.x - T / 2,
				top: h.y + 40 - T / 2,
				width: T,
				height: T,
				borderRadius: '50%',
				background: `radial-gradient(circle, ${rgba(h.c, 0.9)} 0%, ${rgba(h.c, 0.55)} 18%, ${rgba(h.c, 0.26)} 38%, ${rgba(h.c, 0.09)} 56%, ${rgba(h.c, 0)} 71%)`,
				opacity: force,
				transform: `scale(${r.echelle.toFixed(4)})`,
			}}
		/>
	);
};

export const Film: React.FC<{t: number}> = ({t}) => (
	<div style={{position: 'absolute', left: 0, top: 0, width: ECRAN.l, height: ECRAN.h, background: C.nuit, overflow: 'hidden'}}>
		<Halo t={t} />
		<Nuit t={t} />
		<Statut t={t} />
		<Boutique t={t} />
		<Produits t={t} />
		<Appuie t={t} />
		<Commande t={t} />
		<Noel t={t} />
		<Pret t={t} />
		<Ecris t={t} />
		<Signature t={t} />
		<Retiens t={t} />
	</div>
);
