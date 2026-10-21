import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, ECRAN, ADRESSE, HISTOIRE, SANS, type Langue} from '../donnees';
import {Encre, Enveloppe, grand, mix, p} from '../outils';
import {Decompte} from './Decompte';

/**
 * 4 · L'ATTENTE · « Tu envoies le lien. Le cachet attend : minuit, un anniversaire,
 * le grand jour. »
 *
 * D'abord le lien, nu, dans une bulle de conversation : une lettre n'a pas d'image
 * de partage (`lettre.html` n'en porte aucune, exprès), donc on ne lui en invente
 * pas. Puis l'enveloppe, à l'endroit exact où elle était scellée, avec la phrase et
 * le compte à rebours DU PRODUIT : il ne reste que quelques secondes avant minuit.
 *
 * `minuit` : l'instant (temps du plan) où le compte tombe à zéro. Il tombe dans le
 * plan suivant ; ici on ne voit que les dernières secondes qui s'égrènent.
 */

/** Un jeton au bon alphabet (22 signes de `[23456789bcdfghjkmnpqrstvwxyz]`), qui n'ouvre rien. */
const JETON = 'k7mq2dx9hbt4wr6pzn3fgc';

export const Attente: React.FC<{t: number; d: number; temps: number[]; minuit: number; langue: Langue}> = ({t, d, temps, minuit, langue}) => {
	const E = ECRAN[langue];
	const L = HISTOIRE[langue];
	const tCachet = temps[0] ?? d / 2;
	const sortie = 1 - p(t, d - 0.25, d);
	const bulle = p(t, 0.1, 0.55);
	const bulleSort = p(t, tCachet - 0.3, tCachet + 0.1);
	const env = p(t, tCachet - 0.1, tCachet + 0.4);

	return (
		<AbsoluteFill>
			{/* ⚠️ Seul le texte s'efface en fin de plan : l'enveloppe et le compte
			    continuent, au pixel près, dans le plan de l'ouverture. */}
			<div style={{position: 'absolute', top: 300, width: '100%', height: 260, opacity: sortie}}>
				<Encre t={t} a={0.05} style={{...grand, position: 'absolute', width: '100%', opacity: 1 - bulleSort}}>
					{E.attente[0]}
				</Encre>
				<Encre t={t} a={tCachet} style={{...grand, position: 'absolute', width: '100%'}}>
					{E.attente[1]}
				</Encre>
			</div>

			{/* La bulle : le lien seul, envoyé par l'acheteur lui-même. */}
			<div
				style={{
					position: 'absolute',
					right: 110,
					top: 820,
					maxWidth: 760,
					padding: '30px 36px 22px',
					borderRadius: '34px 34px 8px 34px',
					background: '#144d37',
					boxShadow: '0 30px 70px rgba(0,0,0,.45)',
					fontFamily: SANS,
					opacity: bulle * (1 - bulleSort),
					translate: `0 ${mix(80, 0, bulle) - 120 * bulleSort}px`,
					scale: String(mix(0.94, 1, bulle)),
				}}
			>
				<div style={{fontSize: 40, lineHeight: 1.32, color: '#8fd7ff', textDecoration: 'underline', wordBreak: 'break-all'}}>
					https://{ADRESSE}/l/{JETON}
				</div>
				<div style={{fontSize: 28, color: 'rgba(233,237,239,.6)', textAlign: 'right', marginTop: 10}}>
					23:41 <span style={{color: '#53bdeb', letterSpacing: '-0.2em'}}>✓✓</span>
				</div>
			</div>

			{/* L'enveloppe qui dort, à la place exacte du plan « scellée ». */}
			<div style={{position: 'absolute', left: '50%', top: 820, translate: '-50% 0%', opacity: env}}>
				<Enveloppe h={HISTOIRE.habillage} largeur={780} t={t} />
			</div>
			<div style={{position: 'absolute', top: 1340, width: '100%', opacity: env}}>
				<div style={{fontFamily: SANS, fontSize: 40, color: C.grisNuit, textAlign: 'center'}}>
					{L.ouvre[0]}
					<b style={{color: C.papier, fontWeight: 600}}>{L.ouvre[1]}</b>
					{L.ouvre[2]}
				</div>
				<Decompte reste={minuit - t} style={{marginTop: 34}} />
			</div>
		</AbsoluteFill>
	);
};
