/**
 * La fin de la pub :
 *  11-12 · un point cyan s'allume (« Et là »), puis la commande arrive, déjà écrite, à 00:14 sous la lune ;
 *          « Même à minuit » : l'heure s'allume ;
 *  13    · « J-34 » en géant, quelques étincelles d'or (le compte se fait depuis la date de publication) ;
 *  14    · l'anneau des 48 heures qui se remplit, et « PRÊTE » ;
 *  15    · le numéro de NEBULA (lu dans `tiktok-20-11/donnees.ts`) et « CATALOGUE » tapé, envoyé ;
 *  16    · le noir, puis l'enseigne néon qui s'allume mot à mot sur la voix, et reste allumée ; le numéro en ligne
 *          discrète dessous, jusqu'à la fin.
 */
import React from 'react';
import {random} from 'remotion';
import {C, francs, JOURS_AVANT_NOEL, ligne, NUMERO, plan, PRODUITS, quand} from './donnees';
import {Bulle, Envoyer, Lune} from './Dessins';
import {Enseigne} from './Enseigne';
import {apparitionNumeroFin} from './etat';
import {entreeSortie, lin, MONO, Pose, TEXTE, TYPO, VA_ET_VIENT} from './outils';

/* ─────────────────────────── 11-12 · la commande arrive ─────────────────────────── */

export const Commande: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('commande');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const tArrive = quand(11, 'arrive');
	const tDeja = quand(11, 'deja');
	const t12 = ligne(12).debut;
	const age = t - (tArrive - 0.22);
	const deplie = age < 0 ? 0 : 1 - Math.exp(-age * 8) * Math.cos(age * 13);
	const point = 1 - lin(t, tArrive - 0.25, tArrive);
	const pouls = 1 + 0.22 * Math.sin((t - a) * 9);
	const minuit = lin(t, t12 - 0.05, t12 + 0.3);
	const balaye = lin(t, tDeja - 0.05, tDeja + 0.7, 0, 1, VA_ET_VIENT);
	const robe = PRODUITS.robe;
	const lignes = ['Bonjour, je commande :', `1 × ${robe.nom}, taille M`, `Prix : ${francs(robe.prix)}`, 'Livraison : Akpakpa'];
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			{point > 0 ? (
				<Pose x={960} y={545} style={{opacity: point}}>
					<div style={{width: 30, height: 30, borderRadius: 15, background: C.cyan, transform: `scale(${pouls.toFixed(4)})`, boxShadow: '0 0 30px rgba(34,211,238,0.9), 0 0 90px rgba(34,211,238,0.5)'}} />
				</Pose>
			) : null}
			{age > 0 ? (
				<Pose x={960} y={545} style={{opacity: Math.min(1, age * 6), transform: `scale(${(1.5 * (0.08 + 0.92 * deplie)).toFixed(4)})`}}>
					<div style={{position: 'relative', width: 760, padding: '30px 38px 34px', borderRadius: 34, background: '#16141f', boxShadow: '0 40px 100px rgba(0,0,0,0.6), inset 0 0 0 1.5px rgba(245,243,255,0.08)', fontFamily: TEXTE, color: C.blanc, overflow: 'hidden'}}>
						<div style={{display: 'flex', alignItems: 'center', gap: 14}}>
							<Bulle taille={40} />
							<div style={{fontWeight: 700, fontSize: 34, flex: 1, letterSpacing: '-0.01em'}}>Nouvelle commande</div>
							<div
								style={{
									display: 'flex',
									alignItems: 'center',
									gap: 10,
									fontWeight: 600,
									fontSize: 30,
									color: minuit > 0.5 ? C.cyan : C.gris,
									transform: `scale(${(1 + 0.32 * minuit).toFixed(4)})`,
									transformOrigin: '100% 50%',
									textShadow: minuit > 0.01 ? `0 0 ${(24 * minuit).toFixed(1)}px rgba(34,211,238,0.7)` : undefined,
								}}
							>
								<Lune taille={28} couleur={minuit > 0.5 ? C.cyan : 'rgba(245,243,255,0.6)'} />
								00:14
							</div>
						</div>
						<div style={{marginTop: 22, opacity: 1 - 0.55 * minuit}}>
							{lignes.map((l, i) => (
								<div key={i} style={{fontWeight: i === 0 ? 500 : 600, fontSize: 40, lineHeight: 1.45, color: i === 0 ? C.grisClair : C.blanc}}>
									{l}
								</div>
							))}
						</div>
						{/* « déjà écrite » : une lumière passe sur le message, de haut en bas */}
						{balaye > 0 && balaye < 1 ? (
							<div style={{position: 'absolute', left: 0, right: 0, height: 120, top: -120 + 560 * balaye, background: 'linear-gradient(180deg, rgba(34,211,238,0) 0%, rgba(34,211,238,0.12) 50%, rgba(34,211,238,0) 100%)'}} />
						) : null}
					</div>
				</Pose>
			) : null}
		</div>
	);
};

/* ─────────────────────────── 13 · J-34 ─────────────────────────── */

const ETINCELLES = Array.from({length: 11}, (_, i) => ({
	x: 960 + (random(`ex${i}`) - 0.5) * 1150,
	y: 560 + (random(`ey${i}`) - 0.5) * 520,
	t: 1.6 + random(`et${i}`) * 1.2,
	d: random(`ed${i}`) * 0.7,
	f: 2 + random(`ef${i}`) * 3,
}));

const Etoile: React.FC<{taille: number; couleur: string}> = ({taille, couleur}) => (
	<svg width={taille} height={taille} viewBox="-10 -10 20 20">
		<path d="M0 -10 Q1.2 -1.2 10 0 Q1.2 1.2 0 10 Q-1.2 1.2 -10 0 Q-1.2 -1.2 0 -10 Z" fill={couleur} />
	</svg>
);

export const Noel: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('noel');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			{ETINCELLES.map((e, i) => {
				const p = lin(t, a + 0.1 + e.d, a + 0.45 + e.d);
				if (p <= 0) return null;
				const scintille = 0.55 + 0.45 * Math.sin((t - a) * e.f * 2 + i);
				return (
					<Pose key={i} x={e.x} y={e.y - 40 * (t - a)} style={{opacity: p * scintille, filter: `drop-shadow(0 0 8px ${C.or})`}}>
						<Etoile taille={10 + e.t * 9} couleur={C.or} />
					</Pose>
				);
			})}
			<Pose x={960} y={290}>
				<div style={{...TYPO, fontSize: 58, fontWeight: 700, letterSpacing: '0.34em', color: C.grisClair}}>NOËL</div>
			</Pose>
			<Pose x={960} y={600}>
				<div style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 420, letterSpacing: '-0.05em', color: C.blanc, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>
					J-<span style={{color: C.cyan}}>{JOURS_AVANT_NOEL}</span>
				</div>
			</Pose>
		</div>
	);
};

/* ─────────────────────────── 14 · prête en 48 heures ─────────────────────────── */

export const Pret: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('pret');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const t48 = quand(14, '48');
	const p = lin(t, a + 0.35, t48 + 0.2, 0, 1, VA_ET_VIENT);
	const heures = Math.round(48 * p);
	const plein = lin(t, t48 + 0.15, t48 + 0.45);
	const pPrete = lin(t, quand(14, 'prete') - 0.08, quand(14, 'prete') + 0.2);
	const R = 280;
	const tour = 2 * Math.PI * R;
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={960} y={545}>
				<div style={{position: 'relative', width: 2 * R + 60, height: 2 * R + 60}}>
					<svg width={2 * R + 60} height={2 * R + 60} style={{position: 'absolute', inset: 0, filter: `drop-shadow(0 0 ${(14 + 22 * plein).toFixed(1)}px rgba(34,211,238,${(0.45 + 0.4 * plein).toFixed(2)}))`}}>
						<circle cx={R + 30} cy={R + 30} r={R} fill="none" stroke="rgba(245,243,255,0.09)" strokeWidth={26} />
						<circle
							cx={R + 30}
							cy={R + 30}
							r={R}
							fill="none"
							stroke={C.cyan}
							strokeWidth={26}
							strokeLinecap="round"
							strokeDasharray={`${(tour * p).toFixed(2)} ${tour.toFixed(2)}`}
							transform={`rotate(-90 ${R + 30} ${R + 30})`}
							opacity={p > 0.002 ? 1 : 0}
						/>
					</svg>
					<div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
						<div style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 220, letterSpacing: '-0.05em', color: C.blanc, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>
							{heures}
							<span style={{fontSize: 100, fontWeight: 700, marginLeft: 10}}>h</span>
						</div>
						<div style={{fontFamily: TEXTE, fontWeight: 800, fontSize: 46, letterSpacing: '0.3em', color: C.cyan, marginTop: 16, opacity: pPrete, filter: pPrete < 0.99 ? `blur(${((1 - pPrete) * 6).toFixed(2)}px)` : undefined}}>
							PRÊTE
						</div>
					</div>
				</div>
			</Pose>
		</div>
	);
};

/* ─────────────────────────── 15 · écris-moi CATALOGUE ─────────────────────────── */

export const MOT_CLE = 'CATALOGUE';

export const tapeCatalogue = () => {
	const debut = quand(15, 'catalogue') - 0.32;
	return Array.from(MOT_CLE, (_, k) => debut + k * 0.055);
};

export const Ecris: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('ecris');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const lettres = tapeCatalogue();
	const tapees = lettres.filter((x) => t >= x).length;
	const tEnvoi = quand(15, 'whatsapp');
	const enfonce = Math.sin(Math.PI * lin(t, tEnvoi - 0.02, tEnvoi + 0.2, 0, 1, (x) => x));
	const onde = lin(t, tEnvoi, tEnvoi + 0.5, 0, 1, (x) => 1 - Math.pow(1 - x, 2));
	const curseur = tapees < MOT_CLE.length || Math.sin(t * Math.PI * 3.2) > 0 ? 1 : 0;
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={960} y={350} style={{transform: 'scale(1.3)'}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 22}}>
					<Bulle taille={64} />
					<div style={{fontFamily: MONO, fontWeight: 700, fontSize: 76, letterSpacing: '0.02em', color: C.blanc}}>{NUMERO}</div>
				</div>
			</Pose>
			<Pose x={960} y={660} style={{transform: 'scale(1.3)'}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 22}}>
					<div style={{width: 680, height: 116, borderRadius: 58, background: '#15131f', boxShadow: 'inset 0 0 0 1.5px rgba(245,243,255,0.12), 0 30px 80px rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', paddingLeft: 46, fontFamily: TEXTE, fontWeight: 700, fontSize: 52, letterSpacing: '0.1em', color: C.blanc}}>
						{MOT_CLE.slice(0, tapees)}
						<span style={{display: 'inline-block', width: 4, height: 58, marginLeft: 6, background: C.cyan, opacity: curseur}} />
					</div>
					<div style={{position: 'relative', width: 116, height: 116}}>
						{onde > 0 && onde < 1 ? (
							<div style={{position: 'absolute', left: 58 - 58 - 90 * onde, top: 58 - 58 - 90 * onde, width: 116 + 180 * onde, height: 116 + 180 * onde, borderRadius: '50%', border: `3px solid rgba(34,211,238,${(0.7 * (1 - onde)).toFixed(3)})`}} />
						) : null}
						<div style={{position: 'absolute', inset: 0, borderRadius: 58, background: C.cyan, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${(1 - 0.08 * enfonce).toFixed(4)})`, boxShadow: '0 0 40px rgba(34,211,238,0.45)'}}>
							<Envoyer taille={52} />
						</div>
					</div>
				</div>
			</Pose>
		</div>
	);
};

/* ─────────────────────────── 16 · l'enseigne ─────────────────────────── */

/** La ligne discrète du numéro, sous une enseigne : l'icône de discussion générique et le numéro du site. */
export const LigneNumero: React.FC<{t: number; taille: number}> = ({t, taille}) => {
	const a = apparitionNumeroFin();
	const p = lin(t, a, a + 0.45);
	if (p <= 0) return null;
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: taille * 0.42, opacity: p, filter: p < 0.99 ? `blur(${((1 - p) * 6).toFixed(2)}px)` : undefined, transform: `translateY(${((1 - p) * 0.3 * taille).toFixed(2)}px)`}}>
			<Bulle taille={taille * 0.95} />
			<div style={{fontFamily: MONO, fontWeight: 700, fontSize: taille, letterSpacing: '0.04em', color: 'rgba(245,243,255,0.86)', whiteSpace: 'nowrap'}}>{NUMERO}</div>
		</div>
	);
};

export const Signature: React.FC<{t: number}> = ({t}) => {
	const {a} = plan('signature');
	if (t < a) return null;
	return (
		<>
			<Enseigne t={t} x={960} y={520} largeur={1060} />
			<Pose x={960} y={800}>
				<LigneNumero t={t} taille={48} />
			</Pose>
		</>
	);
};
