/**
 * LA PIÈCE (version TikTok 9:16) : le film 16:9 joue sur un moniteur fin, dans une pièce sombre. Sa lumière déborde
 * sur le mur et sur une table noire brillante, qui le reflète (la référence A). L'enseigne NEBULA AGENCY en néon est
 * accrochée au mur, au-dessus. La caméra pousse doucement tout du long ; à la ligne 16 elle monte vers l'enseigne,
 * qui s'allume en plein sur « NEBULA Agency ». En haut, l'accroche ; sous l'écran, les sous-titres mot à mot.
 * ⚠️ Si le décor fait faux sur la planche : SIMPLIFIER (plus de nuit, moins d'objets), jamais ajouter.
 */
import React from 'react';
import {AbsoluteFill, random, staticFile, useCurrentFrame} from 'remotion';
import {C, ECRAN, FPS, plan} from './donnees';
import {Enseigne, ENSEIGNE_MOTS} from './Enseigne';
import {lumiereEcran, niveauLueur} from './etat';
import {Film} from './Film';
import {lin, rgba, TEXTE, VA_ET_VIENT} from './outils';
import {LigneNumero} from './PlansFin';
import {SousTitres} from './SousTitres';

/* La géométrie de la pièce, en pixels de l'image 1080 x 1920. */
const ECRAN_L = 980;
const ECRAN_H = (ECRAN_L * 9) / 16;
const ECRAN_X = (1080 - ECRAN_L) / 2;
const ECRAN_Y = 682;
const BORD = 11;
const MENTON = 12;
const CONTACT_Y = 1322;           // le pied du moniteur touche la table
const TABLE_Y = 1288;             // le fond de la table, contre le mur
const RACCOURCI = 0.62;           // le reflet sur une table vue de biais est écrasé
const ENSEIGNE = {x: 540, y: 420, largeur: 560};
const SOUS_TITRES_Y = 1446;
const ORIGINE = {x: 540, y: 958}; // le point autour duquel la caméra pousse

const ECHELLE_FILM = ECRAN_L / ECRAN.l;

/** La caméra : une poussée lente (1 → 1,05), une respiration de la main, puis la montée vers l'enseigne. */
const camera = (t: number) => {
	const sig = plan('signature').a;
	const pousse = lin(t, 0, sig, 0, 1, (x) => x);
	const monte = lin(t, sig - 0.05, sig + 1.6, 0, 1, VA_ET_VIENT);
	const s0 = 1 + 0.06 * pousse;
	const sF = 1.28;
	const tyF = 660 - ORIGINE.y + (ORIGINE.y - ENSEIGNE.y) * sF; // l'enseigne finit vers y = 660
	const s = s0 + (sF - s0) * monte;
	const ty = tyF * monte;
	const main = 1 - 0.6 * monte;
	const dx = (Math.sin(t * 0.53) * 2.2 + Math.sin(t * 1.31 + 1) * 0.8) * main;
	const dy = (Math.sin(t * 0.41 + 2) * 1.6 + Math.sin(t * 1.07) * 0.6) * main;
	const r = Math.sin(t * 0.37 + 0.5) * 0.12 * main;
	return {s, ty, dx, dy, r, monte};
};

/** Où tombe un point de la pièce à l'image, une fois la caméra passée. */
const aLImage = (y: number, cam: ReturnType<typeof camera>) => ORIGINE.y + (y - ORIGINE.y) * cam.s + cam.ty + cam.dy;

const Moniteur: React.FC<{t: number; voile: number; lueur: number}> = ({t, voile, lueur}) => (
	<>
		{/* le pied : le cou derrière l'écran, la base posée sur la table */}
		<div style={{position: 'absolute', left: 540 - 38, top: ECRAN_Y + ECRAN_H + BORD + MENTON - 10, width: 76, height: CONTACT_Y - (ECRAN_Y + ECRAN_H + BORD + MENTON) + 2, background: 'linear-gradient(90deg, #08080a 0%, #1b1a21 50%, #08080a 100%)'}} />
		<div style={{position: 'absolute', left: 540 - 175, top: CONTACT_Y - 14, width: 350, height: 26, borderRadius: '50%', background: 'linear-gradient(180deg, #2a2931 0%, #121116 45%, #060608 100%)', boxShadow: '0 10px 18px rgba(0,0,0,0.7)'}} />
		{/* le corps, fin, et l'écran */}
		<div
			style={{
				position: 'absolute',
				left: ECRAN_X - BORD,
				top: ECRAN_Y - BORD,
				width: ECRAN_L + 2 * BORD,
				height: ECRAN_H + 2 * BORD + MENTON,
				borderRadius: 9,
				background: 'linear-gradient(180deg, #121117 0%, #0b0a0e 100%)',
				boxShadow: 'inset 0 0 0 1px rgba(245,243,255,0.08), 0 0 0 1px rgba(0,0,0,0.7)',
			}}
		/>
		<div style={{position: 'absolute', left: ECRAN_X, top: ECRAN_Y, width: ECRAN_L, height: ECRAN_H, overflow: 'hidden', background: C.nuit}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: ECRAN.l, height: ECRAN.h, transform: `scale(${ECHELLE_FILM})`, transformOrigin: '0 0'}}>
				<Film t={t} />
			</div>
			{/* à la fin, l'écran s'éteint quand l'enseigne du mur s'allume : il ne reste qu'elle (son verre en garde un reflet) */}
			{voile > 0.001 ? <div style={{position: 'absolute', inset: 0, background: '#050407', opacity: voile}} /> : null}
			{voile > 0.001 ? <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(172,82,255,0.10) 0%, rgba(40,222,255,0.04) 35%, rgba(0,0,0,0) 70%)', opacity: voile * lueur}} /> : null}
			{/* le verre de l'écran : un reflet en biais, à peine */}
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(118deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0) 38%, rgba(255,255,255,0) 72%, rgba(255,255,255,0.025) 100%)'}} />
		</div>
	</>
);

/** Le reflet de l'écran dans la table : retourné, écrasé, flou, et qui s'éteint en s'éloignant. */
const Reflet: React.FC<{t: number; opacity: number}> = ({t, opacity}) => {
	const haut = CONTACT_Y + (CONTACT_Y - (ECRAN_Y + ECRAN_H + BORD + MENTON)) * RACCOURCI;
	const h = ECRAN_H * RACCOURCI;
	if (opacity < 0.001) return null;
	return (
		<div
			style={{
				position: 'absolute',
				left: ECRAN_X,
				top: haut,
				width: ECRAN_L,
				height: h,
				overflow: 'hidden',
				filter: 'blur(10px)',
				opacity,
				WebkitMaskImage: 'linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.07) 28%, rgba(0,0,0,0) 55%)',
				maskImage: 'linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.07) 28%, rgba(0,0,0,0) 55%)',
			}}
		>
			<div style={{position: 'absolute', left: 0, top: 0, width: ECRAN.l, height: ECRAN.h, transformOrigin: '0 0', transform: `translateY(${h}px) scale(${ECHELLE_FILM}, ${-h / ECRAN.h})`}}>
				<Film t={t} />
			</div>
		</div>
	);
};

const Accroche: React.FC = () => (
	<div style={{position: 'absolute', top: 206, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
		<div style={{padding: '14px 26px 16px', borderRadius: 16, background: '#000', fontFamily: `${TEXTE}, 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji'`, fontWeight: 700, fontSize: 50, letterSpacing: '-0.01em', color: '#fff', lineHeight: 1.1}}>
			Tu vends sur WhatsApp ? 😳
		</div>
	</div>
);

export const Piece: React.FC = () => {
	const frame = useCurrentFrame();
	const t = frame / FPS;
	const cam = camera(t);
	const l = lumiereEcran(t);
	const ln = niveauLueur(t, 'nebula');
	const la = niveauLueur(t, 'agency');
	const sig = plan('signature').a;
	const voile = lin(t, sig - 0.05, sig + 0.25, 0, 1, VA_ET_VIENT);
	const lumiere = 1 - voile;
	const centreEcran = ECRAN_Y + ECRAN_H / 2;
	// les sous-titres suivent la montée : sous l'écran, puis entre l'enseigne et le haut du moniteur
	const basEnseigne = ENSEIGNE.y + (ENSEIGNE_MOTS.agency.dy + ENSEIGNE_MOTS.agency.h / 2) * ENSEIGNE.largeur;
	// à la fin : l'enseigne, le numéro juste dessous, puis les sous-titres entre le numéro et le haut du moniteur
	const yNumero = aLImage(basEnseigne + 30, cam);
	const yST = SOUS_TITRES_Y + ((yNumero + 22 + aLImage(ECRAN_Y - BORD, cam)) / 2 - SOUS_TITRES_Y) * cam.monte;
	const gx = Math.floor(random(`gx${frame}`) * 384);
	const gy = Math.floor(random(`gy${frame}`) * 384);
	return (
		<AbsoluteFill style={{background: '#040307', overflow: 'hidden'}}>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					transformOrigin: `${ORIGINE.x}px ${ORIGINE.y}px`,
					transform: `translate(${cam.dx.toFixed(2)}px, ${(cam.ty + cam.dy).toFixed(2)}px) scale(${cam.s.toFixed(5)}) rotate(${cam.r.toFixed(4)}deg)`,
				}}
			>
				{/* le mur, plus grand que l'image : la caméra bouge */}
				<div style={{position: 'absolute', left: -300, top: -900, width: 1680, height: TABLE_Y + 900, background: 'radial-gradient(ellipse 70% 55% at 50% 72%, #100e16 0%, #09080d 55%, #050408 100%)'}} />
				{/* la lumière de l'écran sur le mur */}
				<div style={{position: 'absolute', left: 540 - 900, top: centreEcran - 760, width: 1800, height: 1520, borderRadius: '50%', background: `radial-gradient(ellipse closest-side, ${rgba(l.c, 0.5 * l.force * lumiere)} 0%, ${rgba(l.c, 0.22 * l.force * lumiere)} 38%, ${rgba(l.c, 0.06 * l.force * lumiere)} 70%, ${rgba(l.c, 0)} 100%)`}} />
				{/* la lumière de l'enseigne sur le mur, quand elle s'allume */}
				{ln > 0.001 ? (
					<div style={{position: 'absolute', left: ENSEIGNE.x - 620, top: ENSEIGNE.y + ENSEIGNE_MOTS.nebula.dy * ENSEIGNE.largeur - 330, width: 1240, height: 660, borderRadius: '50%', background: `radial-gradient(ellipse closest-side, rgba(172,82,255,${(0.34 * ln).toFixed(3)}) 0%, rgba(172,82,255,${(0.12 * ln).toFixed(3)}) 45%, rgba(172,82,255,0) 100%)`}} />
				) : null}
				{la > 0.001 ? (
					<div style={{position: 'absolute', left: ENSEIGNE.x - 480, top: ENSEIGNE.y + ENSEIGNE_MOTS.agency.dy * ENSEIGNE.largeur - 230, width: 960, height: 460, borderRadius: '50%', background: `radial-gradient(ellipse closest-side, rgba(40,222,255,${(0.24 * la).toFixed(3)}) 0%, rgba(40,222,255,${(0.08 * la).toFixed(3)}) 45%, rgba(40,222,255,0) 100%)`}} />
				) : null}
				<Enseigne t={t} x={ENSEIGNE.x} y={ENSEIGNE.y} largeur={ENSEIGNE.largeur} verre={0.5} />
				{/* la table : noire, brillante ; son fond prend la lumière */}
				<div style={{position: 'absolute', left: -300, top: TABLE_Y, width: 1680, height: 1400, background: 'linear-gradient(180deg, #0c0b10 0%, #060509 10%, #030205 100%)'}} />
				<div style={{position: 'absolute', left: -300, top: TABLE_Y - 1, width: 1680, height: 2, background: rgba(l.c, 0.18 * l.force + 0.05)}} />
				<div style={{position: 'absolute', left: 540 - 700, top: CONTACT_Y - 120, width: 1400, height: 420, borderRadius: '50%', background: `radial-gradient(ellipse closest-side, ${rgba(l.c, 0.3 * l.force * lumiere)} 0%, ${rgba(l.c, 0.1 * l.force * lumiere)} 50%, ${rgba(l.c, 0)} 100%)`}} />
				<Reflet t={t} opacity={1 - voile} />
				<Moniteur t={t} voile={voile} lueur={ln} />
			</div>
			{/* le vignettage de l'objectif, puis le grain de l'image filmée */}
			<AbsoluteFill style={{background: 'radial-gradient(ellipse 80% 62% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)'}} />
			<AbsoluteFill style={{backgroundImage: `url(${staticFile('pub-ecran-nebula/grain.png')})`, backgroundPosition: `${gx}px ${gy}px`, opacity: 0.7}} />
			<Accroche />
			<div style={{position: 'absolute', left: 540 - 560, top: yST - 150, width: 1120, height: 300, borderRadius: '50%', background: 'radial-gradient(ellipse closest-side, rgba(3,2,6,0.62) 0%, rgba(3,2,6,0.35) 55%, rgba(3,2,6,0) 100%)'}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: yNumero, height: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
				<LigneNumero t={t} taille={36} />
			</div>
			<SousTitres t={t} y={yST} largeur={840} />
		</AbsoluteFill>
	);
};

