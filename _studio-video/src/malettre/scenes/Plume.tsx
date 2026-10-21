import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {CAPTURES} from '../captures';
import {C, ECRAN, type Langue} from '../donnees';
import {Encre, grand, mix, p} from '../outils';

/**
 * 3 · LA PLUME · « Tu l'écris avec tes mots. Ou la plume l'écrit avec toi, à partir
 * de tes souvenirs. »
 *
 * Le VRAI constructeur, photographié par `_outils/malettre_captures.py` : la fiche
 * de la lettre d'Afi, ses puces cochées une à une (la fiche défile jusqu'à la puce
 * que le doigt touche), puis la lettre que la plume a réellement écrite à partir
 * de cette fiche. Rien n'est redessiné : ce sont les pixels du produit.
 *
 * `temps[0]` est l'instant où la voix dit « la plume ». Avant, l'écran « Je l'écris
 * moi-même » ; sans `temps` (la coupe B), on entre directement par la plume.
 */

/** Le téléphone : 390 px CSS rendus à cette largeur. */
const ECRAN_L = 660;
const ECHELLE = ECRAN_L / 390;
const ECRAN_H = 844 * ECHELLE;
/* Le téléphone sort par le bas du cadre : il monte, il ne flotte pas. */
const HAUT = 540;

const Doigt: React.FC<{x: number; y: number; k: number}> = ({x, y, k}) =>
	k <= 0 || k >= 1 ? null : (
		<div
			style={{
				position: 'absolute',
				left: x * ECHELLE,
				top: y * ECHELLE,
				width: 64,
				height: 64,
				marginLeft: -32,
				marginTop: -32,
				borderRadius: '50%',
				background: 'rgba(244,237,224,.55)',
				boxShadow: '0 0 0 3px rgba(244,237,224,.35)',
				scale: String(mix(1.25, 0.8, Math.min(1, k * 2.4))),
				opacity: k < 0.5 ? 1 : 1 - (k - 0.5) * 2,
			}}
		/>
	);

export const Plume: React.FC<{t: number; d: number; temps: number[]; langue: Langue}> = ({t, d, temps, langue}) => {
	const E = ECRAN[langue];
	const M = CAPTURES[langue];
	const dossier = `malettre/${langue}`;
	const sortie = 1 - p(t, d - 0.3, d);

	/* Les trois temps du plan : moi (facultatif) · la fiche · la lettre écrite. */
	const tPlume = temps[0] ?? 0;
	const tLettre = d - 1.35;
	const puces = M.puces;
	const pas = Math.max(0.16, (tLettre - 0.35 - (tPlume + 0.55)) / Math.max(1, puces.length));
	const instantPuce = (k: number) => tPlume + 0.55 + k * pas;
	const cochees = puces.filter((_, k) => t >= instantPuce(k) + 0.06).length;

	/* La fiche défile pour garder la puce qu'on coche au tiers haut de l'écran. */
	const hautVisible = ECRAN_H / ECHELLE - M.entete;
	const cible = (k: number) => Math.max(0, Math.min(M.fiche.h - hautVisible, (puces[Math.min(k, puces.length - 1)]?.y ?? 0) - hautVisible * 0.38));
	let defile = cible(0);
	for (let k = 1; k < puces.length; k++) {
		defile = mix(defile, cible(k), p(t, instantPuce(k) - 0.22, instantPuce(k)));
	}
	defile = mix(defile, Math.max(0, M.fiche.h - hautVisible), p(t, instantPuce(puces.length - 1) + 0.1, tLettre - 0.1));

	/* L'écran « moi » reste le temps que le doigt touche « la plume ». */
	const avant = t < tPlume + 0.4;
	/* La fiche est plus étroite que la page : elle garde sa marge réelle. */
	const marge = ((390 - M.fiche.l) / 2) * ECHELLE;
	const aMoi = tPlume > 0.8;
	const montreLettre = p(t, tLettre, tLettre + 0.45);

	return (
		<AbsoluteFill style={{opacity: sortie}}>
			<div style={{position: 'absolute', top: 250, width: '100%', height: 240}}>
				{aMoi ? (
					<Encre t={t} a={0.05} style={{...grand, position: 'absolute', width: '100%', opacity: 1 - p(t, tPlume - 0.2, tPlume)}}>
						{E.plume[0]}
					</Encre>
				) : null}
				<Encre t={t} a={tPlume} style={{...grand, fontSize: 76, position: 'absolute', width: '100%', padding: '0 70px', boxSizing: 'border-box'}}>
					{E.plume[1]}
				</Encre>
			</div>

			{/* Le téléphone : un cadre neutre, sans marque, et les pixels du constructeur. */}
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: HAUT,
					width: ECRAN_L,
					height: ECRAN_H,
					translate: `-50% ${mix(60, 0, p(t, 0, 0.45))}px`,
					opacity: p(t, 0, 0.3),
					borderRadius: 54,
					overflow: 'hidden',
					background: C.nuit,
					boxShadow: '0 0 0 14px #0c0a10,0 0 0 16px rgba(143,134,160,.35),0 60px 140px rgba(0,0,0,.6)',
				}}
			>
				{avant ? (
					<>
						<Img src={staticFile(`${dossier}/moi.jpg`)} style={{width: '100%', display: 'block'}} />
						{aMoi ? <Doigt x={M.doigt.moi.x} y={M.doigt.moi.y} k={p(t, 0.5, 1.1)} /> : null}
						<Doigt x={M.doigt.plume.x} y={M.doigt.plume.y} k={p(t, tPlume - 0.05, tPlume + 0.45)} />
					</>
				) : (
					<>
						<div style={{position: 'absolute', left: marge, width: M.fiche.l * ECHELLE, top: M.entete * ECHELLE + 16, translate: `0 ${-defile * ECHELLE}px`}}>
							<Img src={staticFile(`${dossier}/fiche-${cochees}.jpg`)} style={{width: '100%', display: 'block'}} />
							{puces.map((pu, k) => (
								<Doigt key={k} x={pu.x} y={pu.y} k={p(t, instantPuce(k) - 0.05, instantPuce(k) + 0.35)} />
							))}
						</div>
						{/* La lettre que la plume a écrite à partir de cette fiche (photographiée
						    sans l'en-tête collant, qui se repose par-dessus). */}
						<Img
							src={staticFile(`${dossier}/lettre.jpg`)}
							style={{position: 'absolute', left: 0, top: M.entete * ECHELLE, width: '100%', opacity: montreLettre, translate: `0 ${mix(40, 0, montreLettre)}px`}}
						/>
						<Img src={staticFile(`${dossier}/entete.jpg`)} style={{position: 'absolute', top: 0, left: 0, width: '100%'}} />
					</>
				)}
			</div>
		</AbsoluteFill>
	);
};
