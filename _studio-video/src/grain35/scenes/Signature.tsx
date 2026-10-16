/**
 * LA SIGNATURE (sombre, 28,5 → 35 s) : SON logo s'écrit en entier (`Logo.tsx`).
 * Le grain du « i » tombe sur un premier temps de la musique (MUSIQUE.grain), les
 * grains d'or du fond sont aspirés vers lui au moment où il touche, puis
 * repartent. La devise (SA phrase), puis ce qu'il faut pour écrire : le numéro
 * WhatsApp, le quartier, les horaires, l'adresse du site. Tout est lu dans la vitrine.
 */
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, VOIX} from '../donnees';
import {FAITS} from '../faits';
import {Fond, Grains} from '../Fond';
import {DUREE_LOGO, Logo} from '../Logo';
import {LOGO} from '../couches';
import {MUSIQUE, REPLIQUES} from '../minutage';
import {Etiquette, Mots, p, ressort} from '../outils';
import {ACCENT, TEXTE} from '../polices';

const LARG = 900;
const ECH = LARG / LOGO.largeur;
const HAUT = 470;
const GRAIN = {x: 540 - LARG / 2 + LOGO.grain.centre[0] * ECH, y: HAUT + LOGO.grain.centre[1] * ECH};

export const Signature: React.FC<{t: number}> = ({t}) => {
	const debut = MUSIQUE.logo;
	const impact = MUSIQUE.grain;
	// les grains du fond : aspirés vers le grain au moment de l'impact, puis relâchés
	const attire = p(t, impact - 0.35, impact) * (1 - p(t, impact + 0.05, impact + 1.2));
	const [da, db] = REPLIQUES.devise;
	const eContact = ressort(t, debut + DUREE_LOGO - 0.6, {damping: 16, stiffness: 110, mass: 0.8});
	return (
		<AbsoluteFill>
			<Fond t={t} lumiere={{x: 540, y: 760}} />
			<Grains t={t} densite={p(t, debut - 0.4, debut + 0.4)} attire={attire} cible={GRAIN} />
			<div style={{position: 'absolute', left: 540 - LARG / 2, top: HAUT}}>
				<Logo t={t} debut={debut} largeur={LARG} id="sig" />
			</div>
			<div style={{position: 'absolute', left: 60, right: 60, top: 1170, textAlign: 'center'}}>
				<Mots
					t={t}
					texte={VOIX.devise}
					a={da}
					b={db}
					taille={76}
					police={ACCENT}
					couleur={C.orClair}
					style={{fontStyle: 'italic'}}
				/>
			</div>
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 1360,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					gap: 22,
					opacity: Math.min(1, eContact * 1.3),
					transform: `translateY(${(1 - eContact) * 40}px)`,
				}}
			>
				<div style={{display: 'flex', alignItems: 'center', gap: 18, padding: '18px 40px', borderRadius: 999, border: `1.5px solid ${C.or}`, background: 'rgba(212,175,114,.08)'}}>
					<div style={{width: 16, height: 16, borderRadius: '50%', background: C.vertWa, boxShadow: `0 0 14px ${C.vertWa}`}} />
					<div style={{fontFamily: TEXTE, fontSize: 46, fontWeight: 600, color: C.creme, letterSpacing: '0.05em'}}>{FAITS.telephone}</div>
					<div style={{fontFamily: TEXTE, fontSize: 24, color: C.or, letterSpacing: '0.2em', textTransform: 'uppercase'}}>WhatsApp</div>
				</div>
				<Etiquette texte={`${FAITS.quartier} · ${FAITS.ville} · ${FAITS.horaires}`} taille={24} couleur={C.rosePale} />
				<div style={{fontFamily: TEXTE, fontSize: 26, color: C.gris, letterSpacing: '0.12em'}}>{FAITS.site}</div>
			</div>
		</AbsoluteFill>
	);
};
