import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './donnees';
import {VERSIONS, type Plan, type VersionId} from './minutage';
import {NUIT} from './outils';
import {Accroche} from './scenes/Accroche';
import {Attente} from './scenes/Attente';
import {Fin} from './scenes/Fin';
import {Occasions} from './scenes/Occasions';
import {Ouverture} from './scenes/Ouverture';
import {PageBlanche} from './scenes/PageBlanche';
import {Plume} from './scenes/Plume';
import {Scellee} from './scenes/Scellee';

/**
 * MA LETTRE À… · le montage d'une version (30 s, ou une coupe de 15 s).
 *
 * Tous les plans posent leur contenu sur LA MÊME nuit, posée une fois ici : une
 * coupe entre deux plans ne change que ce qui est posé dessus, jamais le fond.
 * ⛔ Aucun fondu enchaîné (leçon de `lepli/donnees.ts` : deux feuilles de papier
 * à demi transparentes l'une sur l'autre ressemblent à une panne).
 *
 * Chaque plan reçoit son temps local `t` (secondes), sa durée `d`, et ses instants
 * internes ramenés à son début : caler la voix, c'est changer `minutage.ts`, rien
 * d'autre.
 */
const UnPlan: React.FC<{plan: Plan; version: VersionId}> = ({plan, version}) => {
	const V = VERSIONS[version];
	const t = useCurrentFrame() / FPS;
	const d = plan.fin - plan.debut;
	const temps = (plan.temps ?? []).map((x) => x - plan.debut);
	const langue = V.langue;
	switch (plan.id) {
		case 'accroche':
			return <Accroche t={t} d={d} temps={temps} langue={langue} />;
		case 'scellee':
			return <Scellee t={t} d={d} langue={langue} />;
		case 'pageBlanche':
			return <PageBlanche t={t} d={d} langue={langue} />;
		case 'plume':
			return <Plume t={t} d={d} temps={temps} langue={langue} />;
		case 'attente': {
			/* Minuit tombe sur la cire qui s'allume, dans le plan suivant. */
			const suivant = V.plans.find((x) => x.id === 'ouverture');
			const minuit = (suivant?.temps?.[0] ?? plan.fin + 0.5) - plan.debut;
			return <Attente t={t} d={d} temps={temps} minuit={minuit} langue={langue} />;
		}
		case 'ouverture': {
			const avant = V.plans[V.plans.indexOf(plan) - 1];
			return <Ouverture t={t} d={d} temps={temps} fondu={avant?.id !== 'attente'} langue={langue} />;
		}
		case 'occasions':
			return <Occasions t={t} d={d} temps={temps} langue={langue} />;
		case 'marque':
			return <Fin t={t} fin={V.fin} langue={langue} />;
	}
};

export const Pub: React.FC<{version: VersionId}> = ({version}) => {
	const V = VERSIONS[version];
	return (
		<AbsoluteFill style={{background: NUIT}}>
			{V.plans.map((plan) => (
				<Sequence
					key={plan.id}
					name={plan.id}
					from={Math.round(plan.debut * FPS)}
					durationInFrames={Math.round((plan.fin - plan.debut) * FPS)}
				>
					<UnPlan plan={plan} version={version} />
				</Sequence>
			))}
			{V.voix ? <Audio src={staticFile(V.voix)} /> : null}
		</AbsoluteFill>
	);
};
