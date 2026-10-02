/**
 * 4 · L'APPEL : « Écrivez-nous sur WhatsApp. »
 *
 * On a plongé dans le clip vide : c'est une conversation avec NEBULA Agency. Le
 * message s'écrit tout seul, part, est lu ; NEBULA écrit déjà. Dessous, en grand,
 * les deux numéros : WhatsApp et appel (ce ne sont pas les mêmes).
 * Puis tout est aspiré dans l'étoile du logo.
 */
import React from 'react';
import {Easing, Img, staticFile} from 'remotion';
import {C, FAITS, LARGEUR, type Registre, T, TEXTES, instants} from '../donnees';
import {IconeDiscussion, IconeTelephone} from '../Icones';
import {ETOILE} from '../logo';
import {Mots, p, ressort} from '../outils';
import {MONO, TEXTE} from '../polices';

const CARTE = {x: 90, y: 440, l: 900, h: 540};

export const ecriture = () => {
	const debut = T.chute + 0.5;
	return {debut, fin: debut + 0.95, envoi: debut + 1.05, lu: debut + 1.45, ecrit: debut + 1.7};
};

export const Appel: React.FC<{t: number; registre: Registre}> = ({t, registre}) => {
	if (t < T.chute + 0.1 || t > T.hit + 0.1) return null;
	const x = TEXTES[registre];
	const e = ressort(t, T.chute + 0.12, {damping: 16, stiffness: 120});
	const aspire = p(t, T.implosion, T.hit - 0.05, Easing.in(Easing.cubic));
	const {debut, fin, envoi, lu, ecrit} = ecriture();
	const message = x.message;
	const lettres = Math.round(message.length * p(t, debut, fin, Easing.linear));
	const parti = ressort(t, envoi, {damping: 14, stiffness: 200});
	const cx = LARGEUR / 2;
	const cy = CARTE.y + CARTE.h / 2;
	return (
		<div
			style={{
				position: 'absolute',
				inset: 0,
				transformOrigin: `${ETOILE.x}px ${ETOILE.y}px`,
				transform: `scale(${1 - 0.85 * aspire})`,
				opacity: 1 - aspire,
			}}
		>
			{(() => {
				const [premier, ...reste] = x.ecrivez.split(' ');
				const quand = instants('ecrivez');
				const style: React.CSSProperties = {position: 'absolute', left: 0, width: LARGEUR, textAlign: 'center', whiteSpace: 'nowrap', textShadow: '0 0 30px rgba(107,63,242,.6)'};
				return (
					<>
						<Mots t={t} texte={premier} a={0} instants={quand.slice(0, 1)} taille={76} style={{...style, top: 250}} />
						<Mots t={t} texte={reste.join(' ')} a={0} instants={quand.slice(1)} taille={76} style={{...style, top: 336}} />
					</>
				);
			})()}

			{/* la conversation */}
			<div
				style={{
					position: 'absolute',
					left: CARTE.x,
					top: CARTE.y,
					width: CARTE.l,
					height: CARTE.h,
					borderRadius: 40,
					overflow: 'hidden',
					background: '#0b141a',
					boxShadow: '0 40px 120px -30px rgba(0,0,0,.95), inset 0 0 0 1.5px rgba(190,200,255,.18), 0 0 80px rgba(37,211,102,.12)',
					transformOrigin: `${cx - CARTE.x}px ${cy - CARTE.y}px`,
					transform: `scale(${0.85 + 0.15 * e})`,
					opacity: Math.min(1, e * 1.5),
				}}
			>
				<div style={{height: 116, display: 'flex', alignItems: 'center', gap: 20, padding: '0 30px', background: '#1f2c34'}}>
					<div style={{width: 74, height: 74, borderRadius: 37, background: C.encre, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `inset 0 0 0 2px ${C.violet}`}}>
						<Img src={staticFile('nebula30/logo/marque.png')} style={{width: 62, height: 31, objectFit: 'contain'}} />
					</div>
					<div>
						<div style={{fontFamily: TEXTE, fontWeight: 700, fontSize: 32, color: '#e9edef'}}>NEBULA Agency</div>
						<div style={{fontFamily: TEXTE, fontSize: 22, color: t > ecrit ? C.vertWa : '#8696a0'}}>{t > ecrit ? 'écrit…' : 'en ligne'}</div>
					</div>
				</div>
				<div
					style={{
						position: 'absolute',
						inset: '116px 0 0 0',
						background: 'radial-gradient(circle at 20% 20%, rgba(255,255,255,.025) 2px, transparent 3px) 0 0/46px 46px, #0b141a',
					}}
				>
					{/* la bulle envoyée, en haut à droite */}
					{parti > 0.01 ? (
						<div
							style={{
								position: 'absolute',
								right: 30,
								top: 46,
								maxWidth: 720,
								padding: '20px 26px 14px',
								borderRadius: 26,
								borderTopRightRadius: 6,
								background: '#005c4b',
								fontFamily: TEXTE,
								fontWeight: 500,
								fontSize: 36,
								lineHeight: 1.25,
								color: '#e9edef',
								opacity: Math.min(1, parti * 1.5),
								transformOrigin: '100% 100%',
								transform: `translateY(${(1 - parti) * 160}px) scale(${0.8 + 0.2 * parti})`,
							}}
						>
							{message}
							<div style={{display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 8, marginTop: 6, fontSize: 20, color: '#8fb3aa'}}>
								maintenant
								<svg width={30} height={18} viewBox="0 0 30 18">
									<path d="M2 10 L7 15 L17 3 M12 15 L14 15 L27 3" fill="none" stroke={t > lu ? C.bleuLu : '#8fb3aa'} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" />
								</svg>
							</div>
						</div>
					) : null}
					{/* le champ de saisie : le message s'y écrit, avec son curseur, puis part */}
					<div
						style={{
							position: 'absolute',
							left: 24,
							right: 24,
							bottom: 24,
							height: 84,
							borderRadius: 42,
							background: '#1f2c34',
							display: 'flex',
							alignItems: 'center',
							padding: '0 30px',
							fontFamily: TEXTE,
							fontSize: 30,
							whiteSpace: 'nowrap',
							overflow: 'hidden',
							color: lettres > 0 && t < envoi ? '#e9edef' : '#8696a0',
						}}
					>
						{lettres > 0 && t < envoi ? message.slice(0, lettres) : 'Message'}
						{t > debut - 0.2 && t < envoi && Math.floor(t * 4) % 2 === 0 ? <span style={{color: C.vertWa, marginLeft: 2}}>|</span> : null}
					</div>
				</div>
			</div>

			{/* les deux numéros */}
			{[
				{a: envoi - 0.15, icone: <IconeDiscussion taille={78} />, libelle: 'WhatsApp', numero: FAITS.whatsapp, taille: 58, couleur: C.etoile, y: 1040},
				{a: envoi + 0.05, icone: <IconeTelephone taille={52} couleur={C.cyan} />, libelle: 'Appel', numero: FAITS.appel, taille: 42, couleur: C.lavande, y: 1160},
			].map((ligne) => {
				const r = ressort(t, ligne.a, {damping: 15, stiffness: 150});
				return (
					<div
						key={ligne.libelle}
						style={{
							position: 'absolute',
							left: 0,
							width: LARGEUR,
							top: ligne.y,
							display: 'flex',
							justifyContent: 'center',
							alignItems: 'center',
							gap: 22,
							opacity: Math.min(1, r * 1.5),
							transform: `translateY(${(1 - r) * 40}px)`,
						}}
					>
						{ligne.icone}
						<div style={{fontFamily: TEXTE, fontWeight: 500, fontSize: 28, color: C.gris}}>{ligne.libelle}</div>
						<div style={{fontFamily: MONO, fontWeight: 700, fontSize: ligne.taille, color: ligne.couleur, letterSpacing: '0.02em', textShadow: '0 0 24px rgba(98,168,255,.35)'}}>{ligne.numero}</div>
					</div>
				);
			})}
		</div>
	);
};
