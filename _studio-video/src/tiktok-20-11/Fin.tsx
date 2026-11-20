/**
 * 4 · LA FIN (22,3 → 28 s) : l'offre du statut de 17 h (« ton catalogue en lien,
 * prêt en 48 h »), qui s'effondre dans l'étoile du logo ; NEBULA naît de l'étoile,
 * puis « Écris-nous sur WhatsApp » et le numéro, tapé chiffre par chiffre.
 * Le logo est le vrai, en couches détourées (`public/nebula30/logo/`).
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, staticFile} from 'remotion';
import {C, DEGRADE, NUMERO, T} from './donnees';
import {BulleAppel, lin, ressort, TEXTE_DEGRADE, Toucher} from './outils';
import {MONO, TEXTE, TITRE} from './polices';

/** Le logo réduit de moitié, centré : positions lues dans `couches.json` (logo x2 : 856, 496, 1300 x 876). */
const K = 0.5;
const X0 = 540 - (1300 * K) / 2;
const Y0 = 400;
const place = (x: number, y: number, w: number, h: number) => ({left: X0 + (x - 856) * K, top: Y0 + (y - 496) * K, width: w * K, height: h * K});
const MARQUE = place(942, 496, 1214, 608);
const NEBULA = place(862, 1122, 1278, 156);
const TRAIT_G = place(976, 1312, 342, 52);
const AGENCY = place(1344, 1312, 380, 52);
const TRAIT_D = place(1758, 1312, 258, 52);
const ETOILE = {x: X0 + (1596 - 856) * K, y: Y0 + (766 - 496) * K};

const PILULE = {top: 950, h: 116};

export const Fin: React.FC<{t: number}> = ({t}) => (
	<>
		<Offre t={t} />
		<Logo t={t} />
		<Appel t={t} />
	</>
);

/** « Ton catalogue en lien. Prêt en 48 h, dès tes photos reçues. » */
const Offre: React.FC<{t: number}> = ({t}) => {
	if (t < T.offre - 0.05 || t > T.logo + 0.05) return null;
	const s1 = ressort(t, T.offre + 0.05, 200, 14);
	const s2 = ressort(t, T.offre + 0.4, 200, 13);
	const s3 = ressort(t, T.offre + 0.75, 200, 15);
	const aspire = lin(t, T.logo - 0.42, T.logo - 0.04, 0, 1, Easing.in(Easing.cubic));
	return (
		<AbsoluteFill style={{transformOrigin: `${ETOILE.x}px ${ETOILE.y}px`, transform: `scale(${(1 - aspire * 0.9).toFixed(3)})`, opacity: 1 - aspire}}>
			<div style={{position: 'absolute', top: 730, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: Math.min(1, s1 * 1.6), transform: `scale(${(0.6 + 0.4 * s1).toFixed(3)})`}}>
				<div
					style={{
						fontFamily: TEXTE,
						fontWeight: 800,
						fontSize: 52,
						color: C.lumiere,
						padding: '26px 52px',
						borderRadius: 999,
						background: DEGRADE,
						boxShadow: '0 18px 60px rgba(79,111,255,.45)',
						whiteSpace: 'nowrap',
					}}
				>
					Ton catalogue en lien
				</div>
			</div>
			<div
				style={{
					position: 'absolute',
					top: 880,
					left: 0,
					right: 0,
					textAlign: 'center',
					fontFamily: TITRE,
					fontWeight: 800,
					fontSize: 92,
					color: C.lumiere,
					opacity: Math.min(1, s2 * 1.6),
					transform: `translateY(${((1 - s2) * 60).toFixed(1)}px) scale(${(1.3 - 0.3 * s2).toFixed(3)})`,
				}}
			>
				Prêt en <span style={TEXTE_DEGRADE}>48&nbsp;h</span>
			</div>
			<div
				style={{
					position: 'absolute',
					top: 1015,
					left: 0,
					right: 0,
					textAlign: 'center',
					fontFamily: TEXTE,
					fontWeight: 600,
					fontSize: 44,
					color: C.lavande,
					opacity: Math.min(1, s3 * 1.6),
					transform: `translateY(${((1 - s3) * 30).toFixed(1)}px)`,
				}}
			>
				dès tes photos reçues.
			</div>
		</AbsoluteFill>
	);
};

/** NEBULA naît de l'étoile : la galaxie se déploie, le nom se dévoile, AGENCY se pose. */
const Logo: React.FC<{t: number}> = ({t}) => {
	if (t < T.logo - 0.3) return null;
	const sm = ressort(t, T.logo, 150, 12);
	const nom = lin(t, T.logo + 0.25, T.logo + 0.8, 0, 1, Easing.inOut(Easing.cubic));
	const agence = lin(t, T.logo + 0.6, T.logo + 1.0);
	const eclat = t < T.logo ? lin(t, T.logo - 0.3, T.logo) : Math.max(0, 1 - (t - T.logo) / 0.7);
	const flotte = Math.sin((t - T.logo) * 1.6) * 5;
	return (
		<AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					left: ETOILE.x - 450,
					top: ETOILE.y - 450,
					width: 900,
					height: 900,
					borderRadius: '50%',
					background: 'radial-gradient(circle, rgba(255,255,255,.95), rgba(168,236,255,.45) 18%, rgba(147,51,234,.18) 40%, transparent 65%)',
					opacity: eclat,
					transform: `scale(${(0.3 + 0.9 * (1 - eclat)).toFixed(3)})`,
				}}
			/>
			<Img
				src={staticFile('nebula30/logo/marque.png')}
				style={{
					position: 'absolute',
					...MARQUE,
					opacity: Math.min(1, sm * 2),
					transformOrigin: `${ETOILE.x - MARQUE.left}px ${ETOILE.y - MARQUE.top}px`,
					transform: `translateY(${flotte.toFixed(2)}px) scale(${(0.15 + 0.85 * sm).toFixed(3)}) rotate(${((1 - sm) * -14).toFixed(2)}deg)`,
				}}
			/>
			<Img src={staticFile('nebula30/logo/nebula.png')} style={{position: 'absolute', ...NEBULA, clipPath: `inset(0 ${((1 - nom) * 100).toFixed(2)}% 0 0)`}} />
			<Img src={staticFile('nebula30/logo/trait-g.png')} style={{position: 'absolute', ...TRAIT_G, opacity: agence, transformOrigin: '100% 50%', transform: `scaleX(${agence.toFixed(3)})`}} />
			<Img src={staticFile('nebula30/logo/agency.png')} style={{position: 'absolute', ...AGENCY, opacity: agence}} />
			<Img src={staticFile('nebula30/logo/trait-d.png')} style={{position: 'absolute', ...TRAIT_D, opacity: agence, transformOrigin: '0% 50%', transform: `scaleX(${agence.toFixed(3)})`}} />
		</AbsoluteFill>
	);
};

/** « Écris-nous sur WhatsApp », le numéro tapé, et le doigt qui appuie. */
const Appel: React.FC<{t: number}> = ({t}) => {
	if (t < T.whatsapp) return null;
	const sp = ressort(t, T.whatsapp, 200, 13);
	const tapes = Math.max(0, Math.min(NUMERO.length, Math.floor((t - T.whatsapp - 0.3) / 0.045) + 1));
	const curseur = tapes < NUMERO.length || Math.floor(t * 2.5) % 2 === 0;
	const rappel = lin(t, T.whatsapp + 1.1, T.whatsapp + 1.5);
	const halo = t > T.tapWa ? ((t - T.tapWa) % 1.1) / 1.1 : -1;
	return (
		<AbsoluteFill>
			<div style={{position: 'absolute', top: PILULE.top, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
				<div style={{position: 'relative', opacity: Math.min(1, sp * 1.6), transform: `scale(${(0.5 + 0.5 * sp).toFixed(3)})`}}>
					{halo >= 0 ? (
						<div
							style={{
								position: 'absolute',
								inset: -6 - halo * 40,
								borderRadius: 999,
								border: `4px solid ${C.vertWa}`,
								opacity: 0.8 * (1 - halo),
							}}
						/>
					) : null}
					<div
						style={{
							display: 'flex',
							alignItems: 'center',
							gap: 20,
							height: PILULE.h,
							padding: '0 52px 0 40px',
							borderRadius: 999,
							background: `linear-gradient(100deg, ${C.vertWa}, ${C.vertFonce})`,
							boxShadow: '0 20px 70px rgba(37,211,102,.4)',
							transform: `scale(${t >= T.tapWa && t < T.tapWa + 0.16 ? 0.95 : 1})`,
						}}
					>
						<BulleAppel taille={66} couleur="#ffffff" />
						<span style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 48, color: '#ffffff', whiteSpace: 'nowrap', textShadow: '0 2px 10px rgba(0,60,25,.35)'}}>Écris-nous sur WhatsApp</span>
					</div>
				</div>
			</div>
			<Toucher t={t} a={T.tapWa} x={720} y={PILULE.top + PILULE.h / 2} couleur={C.vertWa} />

			<div style={{position: 'absolute', top: 1110, left: 0, right: 0, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 62, color: C.lumiere, whiteSpace: 'pre'}}>
				{NUMERO.slice(0, tapes)}
				<span style={{opacity: t >= T.whatsapp + 0.3 && curseur ? 1 : 0, color: C.cyan}}>|</span>
			</div>

			<div
				style={{
					position: 'absolute',
					top: 1220,
					left: 0,
					right: 0,
					textAlign: 'center',
					fontFamily: TEXTE,
					fontWeight: 600,
					fontSize: 38,
					color: C.lavande,
					opacity: rappel,
					transform: `translateY(${((1 - rappel) * 20).toFixed(1)}px)`,
				}}
			>
				Ton catalogue en lien, prêt en 48 h.
			</div>
		</AbsoluteFill>
	);
};
