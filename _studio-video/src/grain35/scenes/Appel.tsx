/**
 * L'APPEL (clair) : « C'est votre tour : écrivez rendez-vous sur WhatsApp. »
 *
 * On MONTRE le geste, pour qu'il paraisse aussi facile qu'il l'est : sa vitrine sur
 * un téléphone, un doigt touche « Prendre rendez-vous », WhatsApp s'ouvre sur
 * Grain d'Esthétique, « Rendez-vous » se tape AU RYTHME OÙ LA VOIX LE DIT, et le
 * message part (✓✓ qui passent au bleu). Dessous, en grand : son numéro et ses
 * horaires, lus dans la vitrine. Aucune réponse de l'institut n'est inventée : la
 * conversation s'arrête au message envoyé.
 */
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {C, VOIX} from '../donnees';
import {FAITS} from '../faits';
import {Fond, Grains} from '../Fond';
import {MOTS, REPLIQUES} from '../minutage';
import {Mots, p, ressort} from '../outils';
import {TEXTE} from '../polices';

const TEL = {l: 500, h: 1000, x: 290, y: 470, r: 64};
const ECRAN = {l: TEL.l - 24, h: TEL.h - 24};
const ECH = ECRAN.l / 1170; // la capture fait 1170 px de large (390 x3)
const BOUTON = {x: 585 * ECH, y: 1974 * ECH}; // « Prendre rendez-vous », relevé sur la capture

const motVoix = (debut: string, defaut: number) =>
	MOTS.find((m) => m.replique === 'ecrivez' && m.mot.toLowerCase().startsWith(debut))?.debut ?? defaut;

const Coche: React.FC<{bleu: boolean}> = ({bleu}) => (
	<svg width={30} height={18} viewBox="0 0 30 18">
		<path d="M1 9 L6 14 L16 3 M10 14 L12 16 L23 3" fill="none" stroke={bleu ? C.bleuLu : '#8696a0'} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" />
	</svg>
);

export const Appel: React.FC<{t: number}> = ({t}) => {
	const [ta] = REPLIQUES.tour;
	const [ea, eb] = REPLIQUES.ecrivez;
	const tRdv = motVoix('rendez', ea + 0.4);
	const tWa = motVoix('whatsapp', eb - 0.4);
	const entree = ressort(t, ta - 0.3, {damping: 17, stiffness: 110, mass: 0.8});
	const tap = ta + 0.75;
	const versWa = p(t, tap + 0.15, tap + 0.55);
	// la frappe : « Rendez-vous » s'écrit pendant que la voix le dit
	const texte = 'Rendez-vous';
	const nFrappe = Math.round(texte.length * p(t, tRdv - 0.05, tRdv + 0.45));
	const envoi = Math.min(tWa + 0.1, tRdv + 0.6);
	const bulle = ressort(t, envoi, {damping: 13, stiffness: 180, mass: 0.6});
	const bleu = t > envoi + 0.4;
	const eNumero = ressort(t, ea + 0.3, {damping: 15, stiffness: 120, mass: 0.7});

	return (
		<AbsoluteFill>
			<Fond t={t} clair lumiere={{x: 540, y: 900}} />
			<Grains t={t} densite={0.5} clair />
			<div style={{position: 'absolute', left: 60, right: 60, top: 150, textAlign: 'center'}}>
				<Mots t={t} texte={VOIX.tour} a={ta} b={REPLIQUES.tour[1]} taille={84} couleur={C.encre} />
			</div>
			<div style={{position: 'absolute', left: 50, right: 50, top: 250, textAlign: 'center'}}>
				<Mots t={t} texte={VOIX.ecrivez} a={ea} b={eb} taille={60} couleur={C.encre} accent={['rendez-vous']} couleurAccent={C.rose} interligne={1.1} />
			</div>

			{/* le téléphone */}
			<div
				style={{
					position: 'absolute',
					left: TEL.x,
					top: TEL.y,
					width: TEL.l,
					height: TEL.h,
					borderRadius: TEL.r,
					background: 'linear-gradient(150deg, #4a2a38 0%, #1d0f16 30%, #2c1822 60%, #120a0f 100%)',
					boxShadow: '0 60px 120px -30px rgba(90,30,55,.55), inset 0 0 0 2px rgba(240,212,154,.35)',
					opacity: Math.min(1, entree * 1.3),
					transform: `translateY(${(1 - entree) * 160}px) rotate(${(1 - entree) * 4}deg)`,
				}}
			>
				<div style={{position: 'absolute', left: 12, top: 12, width: ECRAN.l, height: ECRAN.h, borderRadius: TEL.r - 12, overflow: 'hidden', background: '#fff'}}>
					{/* 1. sa vitrine */}
					<div style={{position: 'absolute', inset: 0, transform: `translateX(${-versWa * 40}%)`, opacity: 1 - versWa * 0.6}}>
						<Img src={staticFile('grain35/vitrine/accueil.jpg')} style={{position: 'absolute', left: 0, top: 0, width: ECRAN.l}} />
						{/* le doigt qui touche « Prendre rendez-vous » */}
						{t > tap - 0.3 && versWa < 1 ? (
							<>
								<div
									style={{
										position: 'absolute',
										left: BOUTON.x - 40,
										top: BOUTON.y - 40,
										width: 80,
										height: 80,
										borderRadius: '50%',
										background: 'rgba(255,255,255,.55)',
										border: '3px solid rgba(255,255,255,.9)',
										transform: `scale(${t < tap ? 1.3 - 0.3 * p(t, tap - 0.3, tap) : 1 + 1.6 * p(t, tap, tap + 0.35)})`,
										opacity: t < tap ? p(t, tap - 0.3, tap - 0.1) : 1 - p(t, tap, tap + 0.35),
									}}
								/>
							</>
						) : null}
					</div>
					{/* 2. WhatsApp */}
					{versWa > 0 ? (
						<div style={{position: 'absolute', inset: 0, transform: `translateX(${(1 - versWa) * 100}%)`, background: C.fondWa}}>
							<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 150, background: C.vertWaFonce, display: 'flex', alignItems: 'flex-end', padding: '0 22px 20px', gap: 16}}>
								<div style={{fontFamily: TEXTE, color: '#fff', fontSize: 34, lineHeight: 1}}>‹</div>
								<div style={{width: 66, height: 66, borderRadius: '50%', background: C.creme, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
									<Img src={staticFile('grain35/logo.png')} style={{width: 58}} />
								</div>
								<div style={{fontFamily: TEXTE, color: '#fff', fontSize: 30, fontWeight: 600, paddingBottom: 12}}>{FAITS.nom}</div>
							</div>
							{bulle > 0.001 ? (
								<div
									style={{
										position: 'absolute',
										right: 22,
										bottom: 140,
										padding: '16px 20px 12px 24px',
										borderRadius: '22px 22px 6px 22px',
										background: C.bulleWa,
										boxShadow: '0 2px 2px rgba(0,0,0,.08)',
										transformOrigin: '100% 100%',
										transform: `scale(${bulle})`,
										display: 'flex',
										alignItems: 'flex-end',
										gap: 12,
									}}
								>
									<div style={{fontFamily: TEXTE, fontSize: 34, color: '#111b21'}}>{texte}</div>
									<div style={{display: 'flex', alignItems: 'center', gap: 6, fontFamily: TEXTE, fontSize: 18, color: '#667781'}}>
										<span>09:41</span>
										<Coche bleu={bleu} />
									</div>
								</div>
							) : null}
							{/* la barre de saisie */}
							<div style={{position: 'absolute', left: 16, right: 16, bottom: 34, height: 78, display: 'flex', gap: 12, alignItems: 'center'}}>
								<div style={{flex: 1, height: 78, borderRadius: 40, background: '#fff', display: 'flex', alignItems: 'center', padding: '0 28px', fontFamily: TEXTE, fontSize: 32, color: '#111b21'}}>
									{t < envoi ? texte.slice(0, nFrappe) : ''}
									{t < envoi && nFrappe < texte.length && Math.floor(t * 3) % 2 === 0 ? <span style={{color: C.vertWa}}>|</span> : null}
									{nFrappe === 0 || t >= envoi ? <span style={{color: '#8696a0'}}>Message</span> : null}
								</div>
								<div style={{width: 78, height: 78, borderRadius: '50%', background: C.vertWa, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${t > envoi - 0.1 && t < envoi + 0.15 ? 0.88 : 1})`}}>
									<svg width={34} height={34} viewBox="0 0 24 24">
										<path d="M3 20 L21 12 L3 4 L3 10 L15 12 L3 14 Z" fill="#fff" />
									</svg>
								</div>
							</div>
						</div>
					) : null}
				</div>
			</div>

			{/* son numéro, ses horaires */}
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 1505,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					gap: 18,
					opacity: Math.min(1, eNumero * 1.3),
					transform: `translateY(${(1 - eNumero) * 40}px)`,
				}}
			>
				<div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '20px 44px', borderRadius: 999, background: C.vertWa, boxShadow: '0 20px 40px -16px rgba(37,211,102,.6)'}}>
					<svg width={46} height={46} viewBox="0 0 32 32">
						<path d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3z" fill="#fff" />
						<path d="M11.6 9.6c-.3-.7-.6-.7-.9-.7h-.8c-.3 0-.7.1-1 .5-.4.4-1.3 1.3-1.3 3.1s1.3 3.6 1.5 3.9c.2.2 2.6 4.1 6.4 5.6 3.2 1.2 3.8 1 4.5.9.7-.1 2.2-.9 2.5-1.8.3-.9.3-1.6.2-1.8-.1-.2-.3-.3-.7-.5l-2.4-1.2c-.3-.1-.6-.2-.8.2l-1.1 1.4c-.2.2-.4.3-.8.1-.4-.2-1.6-.6-3-1.9-1.1-1-1.9-2.2-2.1-2.6-.2-.4 0-.6.2-.8l.6-.7c.2-.2.3-.4.4-.7.1-.3 0-.5 0-.7l-1.4-2.3z" fill={C.vertWa} />
					</svg>
					<div style={{fontFamily: TEXTE, fontSize: 52, fontWeight: 600, color: '#fff', letterSpacing: '0.04em'}}>{FAITS.telephone}</div>
				</div>
				<div style={{fontFamily: TEXTE, fontSize: 28, color: C.encre, letterSpacing: '0.06em'}}>
					{FAITS.horaires} · {FAITS.surRendezVous}
				</div>
			</div>
		</AbsoluteFill>
	);
};
