import React from 'react';
import {C, SANS, SERIF} from '../donnees';
import {T} from '../outils';

/**
 * Le compte à rebours DU PRODUIT (`#decompte` de `lettre.html`) : heures, minutes,
 * secondes, chacune avec son libellé en petites capitales. Les jours sont cachés
 * quand ils valent zéro (`.decompte span.zero{display:none}`), donc ici aussi.
 *
 * Le chiffre des secondes ROULE : l'ancien monte et s'efface pendant que le
 * nouveau arrive d'en bas, dans le dernier cinquième de chaque seconde.
 */
const deux = (n: number) => String(Math.max(0, n)).padStart(2, '0');

const Case: React.FC<{valeur: string; avant: string; k: number; libelle: string}> = ({valeur, avant, k, libelle}) => (
	<span style={{display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 150}}>
		<span style={{position: 'relative', height: 112, width: 150, overflow: 'hidden', fontFamily: SERIF, fontSize: 104, lineHeight: '112px', color: C.papier, textAlign: 'center'}}>
			<span style={{position: 'absolute', inset: 0, translate: `0 ${-k * 100}%`, opacity: 1 - k}}>{avant}</span>
			<span style={{position: 'absolute', inset: 0, translate: `0 ${(1 - k) * 100}%`, opacity: k}}>{valeur}</span>
		</span>
		<i style={{fontStyle: 'normal', fontFamily: SANS, fontSize: 28, letterSpacing: '0.2em', textTransform: 'uppercase', color: C.grisNuit, marginTop: 8}}>{libelle}</i>
	</span>
);

export const Decompte: React.FC<{reste: number; style?: React.CSSProperties}> = ({reste, style}) => {
	const s = Math.max(0, Math.ceil(reste - 1e-6));
	const frac = s - Math.max(0, reste);
	/* Le roulement occupe les 0,2 dernières secondes avant chaque changement. */
	const k = reste <= 0 ? 1 : T(Math.min(1, Math.max(0, (frac - 0.8) / 0.2)));
	const suivant = Math.max(0, s - 1);
	const roule = k > 0 && reste > 0;
	return (
		<div style={{display: 'flex', gap: 28, justifyContent: 'center', ...style}}>
			<Case valeur={deux(0)} avant={deux(0)} k={1} libelle="h" />
			<Case valeur={deux(0)} avant={deux(0)} k={1} libelle="min" />
			<Case valeur={deux(roule ? suivant : s)} avant={deux(s)} k={roule ? k : 1} libelle="s" />
		</div>
	);
};
