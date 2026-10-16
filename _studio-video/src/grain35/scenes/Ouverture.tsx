/**
 * L'OUVERTURE (0 → 8,6 s) : l'accroche, puis l'entrée dans l'institut.
 *
 *  · l'ŒIL de sa marque se dessine en grand, en or (sourcil, eyeliner, ouverture) ;
 *  · « Vous vous occupez de tout le monde… » : les mots d'une journée s'empilent
 *    autour, de plus en plus serrés, jusqu'à saturer l'écran ;
 *  · « Mais qui s'occupe de VOUS ? » : sur « vous », tout se dissout en grains,
 *    il ne reste que « vous » ;
 *  · la caméra PLONGE DANS LA PUPILLE d'or ; l'or remplit l'écran, et l'on
 *    ressort dans l'institut : SA photo, par un cercle qui s'ouvre (l'iris) ;
 *  · « Chez Grain d'Esthétique, vous passez enfin en premier. »
 */
import React from 'react';
import {AbsoluteFill, Easing, Img, staticFile} from 'remotion';
import {C, FARDEAU, HAUTEUR, LARGEUR, VOIX} from '../donnees';
import {FAITS} from '../faits';
import {Fond, Grains} from '../Fond';
import {Logo, PUPILLE} from '../Logo';
import {LOGO} from '../couches';
import {MOTS, REPLIQUES} from '../minutage';
import {ASPIRE, Etiquette, Filet, h, mix, Mots, p} from '../outils';
import {TEXTE} from '../polices';

// L'œil en grand : sa largeur (sourcil compris) fait 780 px, centré.
const [SX0, , SX1] = LOGO.sourcil.boite;
const ECH = 780 / (SX1 - SX0);
const LARG_LOGO = LOGO.largeur * ECH;
const GAUCHE = LARGEUR / 2 - ((SX0 + SX1) / 2) * ECH;
const HAUT = 250 - LOGO.sourcil.boite[1] * ECH;
const PX = GAUCHE + PUPILLE.x * ECH;
const PY = HAUT + PUPILLE.y * ECH;

const instantDuMot = (mot: string, replique: string, defaut: number) =>
	MOTS.find((m) => m.replique === replique && m.mot.toLowerCase().startsWith(mot))?.debut ?? defaut;

export const T_VOUS = instantDuMot('vous', 'quiVous', REPLIQUES.quiVous[1] - 0.25);
export const T_PLONGE = REPLIQUES.quiVous[1] + 0.35;
export const T_INSTITUT = T_PLONGE + 0.62;
export const FIN_OUVERTURE = REPLIQUES.premier[1] + 0.45;

/**
 * Les mots d'une journée, à des places COMPOSÉES (pas tirées au hasard : au tirage,
 * « les clients » tombait sur « les enfants » et « les rendez-vous des autres »
 * sortait de l'écran). Autour de l'œil et du texte, jamais dessus ; alignés à gauche
 * sur le bord gauche, à droite sur le bord droit. Le dernier, « les rendez-vous des
 * autres », est le mot de la fin : centré, en rose.
 */
const PLACES: {x: number; y: number; cote: 'g' | 'd' | 'c'}[] = [
	{x: 84, y: 120, cote: 'g'},
	{x: 996, y: 186, cote: 'd'},
	{x: 84, y: 800, cote: 'g'},
	{x: 996, y: 866, cote: 'd'},
	{x: 110, y: 1310, cote: 'g'},
	{x: 970, y: 1380, cote: 'd'},
	{x: 84, y: 1452, cote: 'g'},
	{x: 996, y: 1522, cote: 'd'},
	{x: 150, y: 1594, cote: 'g'},
	{x: 540, y: 1680, cote: 'c'},
];

const Fardeau: React.FC<{t: number}> = ({t}) => {
	const debut = REPLIQUES.occupe[0] + 0.15;
	const pas = (REPLIQUES.quiVous[0] - debut) / FARDEAU.length;
	return (
		<>
			{FARDEAU.map((mot, i) => {
				const a = debut + i * pas;
				const e = p(t, a, a + 0.35);
				if (e <= 0) return null;
				const dissous = p(t, T_VOUS - 0.05 + h(i, 3) * 0.15, T_VOUS + 0.45, Easing.in(Easing.cubic));
				if (dissous >= 1) return null;
				const {x, y, cote} = PLACES[i];
				const dernier = i === FARDEAU.length - 1;
				// plus il y en a, plus ça serre : les mots tremblent sous la pression
				const pression = p(t, debut, REPLIQUES.quiVous[0]);
				const tremble = Math.sin(t * 31 + i * 7) * 2.5 * pression;
				const dir = cote === 'g' ? -1 : cote === 'd' ? 1 : 0;
				const fuite = dissous * (220 + h(i, 4) * 200);
				const ancre = cote === 'g' ? '0%' : cote === 'd' ? '-100%' : '-50%';
				return (
					<div
						key={mot}
						style={{
							position: 'absolute',
							left: x + dir * fuite + tremble,
							top: y - dissous * 60,
							fontFamily: TEXTE,
							fontWeight: 500,
							fontSize: dernier ? 38 : 30 + h(i, 5) * 10,
							letterSpacing: '0.24em',
							textTransform: 'uppercase',
							whiteSpace: 'nowrap',
							color: dernier ? C.roseClair : C.creme,
							opacity: e * (dernier ? 0.9 : 0.4 + 0.25 * h(i, 6) + 0.2 * pression) * (1 - dissous),
							filter: `blur(${(1 - e) * 8 + dissous * 10}px)`,
							transform: `translateX(${ancre}) translateY(${(1 - e) * 24}px) scale(${1 - dissous * 0.3})`,
						}}
					>
						{mot}
					</div>
				);
			})}
		</>
	);
};

export const Ouverture: React.FC<{t: number}> = ({t}) => {
	if (t > FIN_OUVERTURE + 0.5) return null;
	// la plongée : on grossit autour de la pupille, de plus en plus vite
	const plonge = p(t, T_PLONGE, T_INSTITUT, ASPIRE);
	const zoom = mix(1, 70, plonge ** 1.6);
	const flashOr = p(t, T_PLONGE + 0.32, T_INSTITUT - 0.02) * (1 - p(t, T_INSTITUT + 0.05, T_INSTITUT + 0.45));
	// l'iris qui s'ouvre sur la photo
	const iris = p(t, T_INSTITUT - 0.08, T_INSTITUT + 0.55, Easing.out(Easing.cubic));
	const kb = p(t, T_INSTITUT, FIN_OUVERTURE, Easing.linear);
	const sortie = p(t, FIN_OUVERTURE - 0.35, FIN_OUVERTURE + 0.2);
	const texteSort = p(t, T_PLONGE - 0.1, T_PLONGE + 0.25);

	return (
		<AbsoluteFill>
			{/* ---------------- l'accroche */}
			{t < T_INSTITUT + 0.6 ? (
				<AbsoluteFill>
					<Fond t={t} lumiere={{x: PX, y: PY + 250}} />
					<Grains t={t} densite={p(t, 0, 0.8) * (1 - plonge)} />
					<AbsoluteFill style={{transformOrigin: `${PX}px ${PY}px`, transform: `scale(${zoom})`}}>
						<div style={{position: 'absolute', left: GAUCHE, top: HAUT}}>
							<Logo t={t} debut={0} largeur={LARG_LOGO} oeilSeul id="ouv" />
						</div>
					</AbsoluteFill>
					<Fardeau t={t} />
					<div style={{position: 'absolute', left: 70, right: 70, top: 1030, textAlign: 'center', opacity: 1 - texteSort}}>
						<Mots
							t={t}
							texte={VOIX.occupe}
							a={REPLIQUES.occupe[0]}
							b={REPLIQUES.occupe[1]}
							taille={74}
							sortie={REPLIQUES.quiVous[0] - 0.25}
						/>
					</div>
					<div style={{position: 'absolute', left: 60, right: 60, top: 1000, textAlign: 'center', opacity: 1 - texteSort}}>
						<Mots
							t={t}
							texte={VOIX.quiVous}
							a={REPLIQUES.quiVous[0]}
							b={REPLIQUES.quiVous[1]}
							taille={96}
							accent={['vous']}
							interligne={1.04}
						/>
					</div>
					{flashOr > 0 ? (
						<AbsoluteFill
							style={{
								background: `radial-gradient(circle at ${PX}px ${PY}px, #fff4d6 0%, ${C.or} 45%, ${C.orFonce} 100%)`,
								opacity: flashOr,
							}}
						/>
					) : null}
				</AbsoluteFill>
			) : null}

			{/* ---------------- dans l'institut : SA photo, par l'iris qui s'ouvre */}
			{iris > 0 ? (
				<AbsoluteFill style={{clipPath: `circle(${iris * 2300}px at ${PX}px ${PY}px)`, opacity: 1 - sortie}}>
					<AbsoluteFill style={{overflow: 'hidden', backgroundColor: C.encre}}>
						<Img
							src={staticFile('grain35/institut.jpg')}
							style={{
								position: 'absolute',
								height: HAUTEUR,
								width: (HAUTEUR * 900) / 1200,
								left: LARGEUR / 2 - (HAUTEUR * 900) / 1200 / 2 + mix(30, -30, kb),
								top: 0,
								transform: `scale(${mix(1.16, 1.03, kb)})`,
								filter: 'saturate(1.06) contrast(1.04)',
							}}
						/>
						{/* l'étalonnage : une chaleur rose-or, puis le bas qui descend dans l'encre pour le texte */}
						<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(42,20,32,.55) 0%, rgba(42,20,32,0) 22%, rgba(42,20,32,0) 42%, rgba(26,14,20,.78) 68%, rgba(26,14,20,.96) 100%)'}} />
						<AbsoluteFill style={{background: 'radial-gradient(ellipse at 60% 35%, rgba(240,212,154,.14), transparent 60%)', mixBlendMode: 'screen'}} />
					</AbsoluteFill>
					<div style={{position: 'absolute', left: 0, right: 0, top: 1130, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
						<Etiquette texte={`${FAITS.quartier} · ${FAITS.ville}`} taille={32} opacite={p(t, T_INSTITUT + 0.3, T_INSTITUT + 0.9)} />
						<Filet e={p(t, T_INSTITUT + 0.4, T_INSTITUT + 1.2)} largeur={300} />
					</div>
					<div style={{position: 'absolute', left: 70, right: 70, top: 1250, textAlign: 'center'}}>
						<Mots t={t} texte={VOIX.chez} a={REPLIQUES.chez[0]} b={REPLIQUES.chez[1]} taille={62} couleur={C.rosePale} />
					</div>
					<div style={{position: 'absolute', left: 60, right: 60, top: 1350, textAlign: 'center'}}>
						<Mots t={t} texte={VOIX.premier} a={REPLIQUES.premier[0]} b={REPLIQUES.premier[1]} taille={100} accent={['premier']} interligne={1.02} />
					</div>
				</AbsoluteFill>
			) : null}
		</AbsoluteFill>
	);
};
