/**
 * Les icônes du film, dessinées ici (aucune image tierce, aucun emoji).
 * ⚠️ L'icône de discussion n'est PAS le logo de WhatsApp (marque d'un autre) :
 * une bulle et un combiné, dans le vert qui désigne l'application.
 */
import React from 'react';
import {C} from './donnees';

export const IconeDiscussion: React.FC<{taille?: number; fond?: string}> = ({taille = 64, fond = C.vertWa}) => (
	<svg width={taille} height={taille} viewBox="0 0 64 64">
		<circle cx="32" cy="32" r="32" fill={fond} />
		<path d="M32 13.5c-10.5 0-19 8.1-19 18.1 0 3.6 1.1 6.9 3 9.7L13.8 50l9.1-2.3c2.7 1.4 5.8 2.2 9.1 2.2 10.5 0 19-8.1 19-18.1S42.5 13.5 32 13.5z" fill="none" stroke="#fff" strokeWidth="3.4" strokeLinejoin="round" />
		<path
			d="M25.2 24.6c.5-1 .9-1.1 1.4-1.1h1.1c.3 0 .8.1 1.1.8l1.4 3.3c.1.3.1.7-.1 1l-.8 1c-.2.3-.2.5-.1.8.7 1.3 1.6 2.4 2.7 3.3 1 .8 2 1.4 3.2 1.9.3.1.6 0 .8-.2l1.1-1.3c.3-.3.6-.3 1-.2l3.2 1.5c.3.2.6.3.6.7 0 .6-.2 1.9-1 2.6-.8.8-2.3 1.4-3.7 1.2-1.6-.2-3.8-1-6.2-2.9-2.6-2-4.3-4.6-5-6.4-.6-1.6-.6-3.1-.3-4.1z"
			fill="#fff"
		/>
	</svg>
);

export const IconeTelephone: React.FC<{taille?: number; couleur?: string}> = ({taille = 40, couleur = C.gris}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24">
		<path
			d="M6.6 3.5c.4-.4 1-.4 1.4 0l2.3 2.6c.3.4.3.9 0 1.3l-1.2 1.5c-.2.2-.2.6 0 .8 1.2 2 2.9 3.7 4.9 4.9.3.2.6.2.8 0l1.5-1.2c.4-.3.9-.3 1.3 0l2.6 2.3c.4.4.4 1 0 1.4l-1.6 1.6c-.9.9-2.3 1.2-3.5.7-3.9-1.6-7-4.7-8.6-8.6-.5-1.2-.2-2.6.7-3.5z"
			fill="none"
			stroke={couleur}
			strokeWidth="1.7"
			strokeLinejoin="round"
		/>
	</svg>
);

export const IconeGlobe: React.FC<{taille?: number; couleur?: string}> = ({taille = 36, couleur = C.cyan}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth="1.6">
		<circle cx="12" cy="12" r="9" />
		<path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18" />
	</svg>
);

/** Les métiers de l'outil : une assiette, une fleur, un sac, une étoile. */
export const IconeMetier: React.FC<{forme: 'plat' | 'fleur' | 'sac' | 'etoile'; taille?: number; couleur: string}> = ({forme, taille = 30, couleur}) => (
	<svg width={taille} height={taille} viewBox="0 0 24 24" fill="none" stroke={couleur} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
		{forme === 'plat' ? (
			<>
				<circle cx="13" cy="12" r="6.5" />
				<circle cx="13" cy="12" r="3" />
				<path d="M3.5 4v5.5M2 4v3.5c0 1 .7 2 1.5 2S5 8.5 5 7.5V4M3.5 9.5V20" />
			</>
		) : forme === 'fleur' ? (
			<>
				<path d="M12 20c-4-2-6-5.5-6-9 3 0 5 1.5 6 4 1-2.5 3-4 6-4 0 3.5-2 7-6 9z" />
				<path d="M12 15c-1.5-2.5-1.5-6 0-9 1.5 3 1.5 6.5 0 9z" />
			</>
		) : forme === 'sac' ? (
			<>
				<path d="M5 8h14l-1.2 12H6.2z" />
				<path d="M9 8V6.5a3 3 0 0 1 6 0V8" />
			</>
		) : (
			<path d="M12 2.5l2.2 6.6 6.8.2-5.4 4.1 2 6.6L12 16l-5.6 4 2-6.6L3 9.3l6.8-.2z" />
		)}
	</svg>
);
