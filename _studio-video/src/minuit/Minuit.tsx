import React from 'react';
import {Series} from 'remotion';
import {Compte} from './Compte';
import {DUREES} from './donnees';
import {Fin} from './Fin';
import {Heure} from './Heure';
import {Lettre} from './Lettre';
import {Seuil} from './Seuil';
import {Signature} from './Signature';

/**
 * MINUIT · le montage.
 *
 * Six plans, six signatures, toutes tirées de l'enveloppe cachetée :
 *   1 · le cachet respire, puis se brise
 *   2 · la feuille se déplie, puis l'encre sèche ligne après ligne
 *   3 · les chiffres roulent
 *   4 · le trait de la signature s'écrit
 *   5 · l'aiguille monte à minuit
 *   6 · le cachet se referme
 *
 * ⛔ Aucun fondu enchaîné, et la raison est écrite dans `donnees.ts` : les six
 * plans partagent le même fond de nuit et font eux-mêmes entrer et sortir leur
 * contenu, donc la coupe est invisible. Superposer deux feuilles de papier à
 * demi transparentes, en revanche, se voit tout de suite.
 *
 * ⚠️ Les durées viennent de `donnees.ts` au lieu d'être écrites ici en clair.
 * Le studio ne sait donc pas les faire glisser à la souris, et c'est assumé :
 * la longueur de la composition est calculée à partir des mêmes valeurs, une
 * durée déplacée ici seulement laisserait du noir en fin de vidéo.
 */
export const Minuit: React.FC = () => (
	<Series>
		<Series.Sequence durationInFrames={DUREES.seuil} name="1 · Le seuil">
			<Seuil />
		</Series.Sequence>
		<Series.Sequence durationInFrames={DUREES.lettre} name="2 · La lettre">
			<Lettre />
		</Series.Sequence>
		<Series.Sequence durationInFrames={DUREES.compte} name="3 · Le compte">
			<Compte />
		</Series.Sequence>
		<Series.Sequence durationInFrames={DUREES.signature} name="4 · La signature">
			<Signature />
		</Series.Sequence>
		<Series.Sequence durationInFrames={DUREES.heure} name="5 · L'heure dite">
			<Heure />
		</Series.Sequence>
		<Series.Sequence durationInFrames={DUREES.fin} name="6 · La carte">
			<Fin />
		</Series.Sequence>
	</Series>
);
