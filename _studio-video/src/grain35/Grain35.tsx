/**
 * GRAIN D'ESTHÉTIQUE · LA PUBLICITÉ DE 35 s (9:16). Voir `donnees.ts` pour la
 * phrase et l'objet (le grain), et `minutage.ts` pour les instants (la voix et la
 * musique, mesurées par `_outils/grain35_son.py`).
 *
 * Le rythme des fonds alterne sombre et clair (la règle de la maison) :
 *   ouverture (sombre, puis SA photo) · maisons (sombre) · AVIS (clair) ·
 *   visage, corps, lèvres (sombre) · APPEL (clair) · signature (sombre).
 * Entre deux scènes, une seule transition : LA VAGUE DE GRAINS (`Balayage`).
 * La première vague finit pile sur la relance de la musique (les avis entrent
 * avec la basse).
 */
import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {C, FPS, MIX} from './donnees';
import {Balayage} from './Fond';
import {Bruitages} from './Bruitages';
import {V1, V2, V3, V4} from './instants';
import {SON} from './minutage';
import {Appel} from './scenes/Appel';
import {FIN_OUVERTURE, Ouverture} from './scenes/Ouverture';
import {Avis, Maisons} from './scenes/Preuves';
import {Signature} from './scenes/Signature';
import {TroisTemps} from './scenes/TroisTemps';

const Film: React.FC<{t: number}> = ({t}) => {
	if (t < FIN_OUVERTURE - 0.5) return <Ouverture t={t} />;
	if (t < V1.a)
		return (
			<>
				<Maisons t={t} />
				<Ouverture t={t} />
			</>
		);
	if (t < V1.a + V1.d) return <Balayage t={t} a={V1.a} duree={V1.d} avant={<Maisons t={t} />} apres={<Avis t={t} />} />;
	if (t < V2.a) return <Avis t={t} />;
	if (t < V2.a + V2.d) return <Balayage t={t} a={V2.a} duree={V2.d} avant={<Avis t={t} />} apres={<TroisTemps t={t} />} />;
	if (t < V3.a) return <TroisTemps t={t} />;
	if (t < V3.a + V3.d) return <Balayage t={t} a={V3.a} duree={V3.d} avant={<TroisTemps t={t} />} apres={<Appel t={t} />} />;
	if (t < V4.a) return <Appel t={t} />;
	if (t < V4.a + V4.d) return <Balayage t={t} a={V4.a} duree={V4.d} avant={<Appel t={t} />} apres={<Signature t={t} />} />;
	return <Signature t={t} />;
};

export const Grain35: React.FC = () => {
	const t = useCurrentFrame() / FPS;
	return (
		<AbsoluteFill style={{backgroundColor: C.encre}}>
			<Film t={t} />
			{SON.voix ? <Audio src={staticFile('grain35/voix.wav')} volume={MIX} /> : null}
			{SON.musique ? <Audio src={staticFile('grain35/musique.wav')} volume={MIX} /> : null}
			<Bruitages />
		</AbsoluteFill>
	);
};
