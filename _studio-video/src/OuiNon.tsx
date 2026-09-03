import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {
	CARTE_FIN,
	IMAGES_FIN,
	IMAGES_QUESTION,
	IMAGES_REPONSE,
	type Reponse,
	type Serie,
} from './scripts';

/**
 * Le montage « oui / non ».
 *
 * Une question, une coupe sèche, la réponse. Aucune transition, aucun fondu :
 * c'est le format qui l'exige, la surprise vient du rythme, pas des effets.
 */

const NOIR = '#070708';
const BLANC = '#ffffff';

/** La même graisse que les cartes de `_cartes.py` (Segoe UI Black / Arial Black). */
const GRASSE = '"Segoe UI Black", "Arial Black", Impact, system-ui, sans-serif';

const PleinEcran: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill
		style={{
			backgroundColor: NOIR,
			alignItems: 'center',
			justifyContent: 'center',
		}}
	>
		{children}
	</AbsoluteFill>
);

/**
 * La réponse en toutes lettres, quand le plan filmé n'est pas encore tourné.
 * Ce n'est pas la version finale voulue par le document (c'est un visage qui
 * répond), mais elle rend une vidéo regardable dès aujourd'hui.
 */
const ReponseEcrite: React.FC<{reponse: Reponse}> = ({reponse}) => (
	<PleinEcran>
		<span
			style={{
				fontFamily: GRASSE,
				fontSize: 300,
				lineHeight: 1,
				letterSpacing: -8,
				color: BLANC,
			}}
		>
			{reponse}
		</span>
	</PleinEcran>
);

const Plan: React.FC<{fichier: string}> = ({fichier}) => (
	<PleinEcran>
		<OffthreadVideo
			src={staticFile(fichier)}
			muted
			style={{width: '100%', height: '100%', objectFit: 'cover'}}
		/>
	</PleinEcran>
);

export const OuiNon: React.FC<{serie: Serie}> = ({serie}) => {
	let debut = 0;

	return (
		<AbsoluteFill style={{backgroundColor: NOIR}}>
			{serie.questions.map((q, i) => {
				const question = debut;
				const reponse = debut + IMAGES_QUESTION;
				debut = reponse + IMAGES_REPONSE;

				return (
					<React.Fragment key={i}>
						<Sequence from={question} durationInFrames={IMAGES_QUESTION}>
							<PleinEcran>
								<Img src={q.carte} style={{width: '100%', height: '100%'}} />
							</PleinEcran>
						</Sequence>
						<Sequence from={reponse} durationInFrames={IMAGES_REPONSE}>
							{q.plan ? (
								<Plan fichier={q.plan} />
							) : (
								<ReponseEcrite reponse={q.reponse} />
							)}
						</Sequence>
					</React.Fragment>
				);
			})}

			<Sequence from={debut} durationInFrames={IMAGES_FIN}>
				<PleinEcran>
					<Img src={CARTE_FIN} style={{width: '100%', height: '100%'}} />
				</PleinEcran>
			</Sequence>
		</AbsoluteFill>
	);
};
