/**
 * Les deux premiers plans : la nuit qui fait perdre des clients, puis le statut, la question et le client qui part.
 *  1-2 · « Chaque nuit, tu perds des clients et tu ne le sais même pas » : l'horloge 00:12 dans le halo, la phrase
 *        s'écrit avec la voix, puis « clients » s'efface lettre par lettre, sans bruit.
 *  3-5 · le téléphone : ton statut (la robe dessinée et son prix), une vue de plus ; la bulle « C'est combien ? »
 *        arrive, deux coches grises ; « Tu dors » : l'écran s'éteint ; la bulle s'en va, « ailleurs. » en orange.
 * ⚠️ Taille : la version TikTok montre ce film à moitié de sa taille. Chaque élément occupe 55 à 65 % de la hauteur,
 *    et un texte qui compte fait au moins 50 px ici.
 */
import React from 'react';
import {C, francs, ligne, plan, PRODUITS, quand} from './donnees';
import {BarreEtat, Coches, Dessin, Oeil} from './Dessins';
import {entreeSortie, ENTREE_DOUCE, lin, Pose, TEXTE, TYPO, VA_ET_VIENT} from './outils';
import {Telephone} from './Telephone';

const normal = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');

/* ─────────────────────────── 1-2 · la nuit ─────────────────────────── */

export const Nuit: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('nuit');
	// la première image montre déjà l'horloge : elle sert de vignette, et TikTok la montre avant même le son
	const es = entreeSortie(t, Math.min(a, 0) - 0.5, b);
	if (!es.visible) return null;
	const deuxPoints = 0.28 + 0.72 * Math.min(1, Math.max(0, (Math.sin(t * Math.PI * 2) + 0.35) * 2.2));
	const efface = ligne(2).debut + 0.25;
	const lueur = '0 0 26px rgba(147,51,234,0.95), 0 0 80px rgba(147,51,234,0.55), 0 0 160px rgba(147,51,234,0.35)';
	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={960} y={390}>
				<div style={{fontFamily: TEXTE, fontWeight: 300, fontSize: 340, letterSpacing: '-0.035em', color: C.blanc, textShadow: lueur, fontVariantNumeric: 'tabular-nums', lineHeight: 1}}>
					00<span style={{opacity: deuxPoints}}>:</span>12
				</div>
			</Pose>
			<Pose x={960} y={760}>
				<div style={{display: 'flex', columnGap: '0.27em', ...TYPO, fontSize: 94, letterSpacing: '-0.02em', whiteSpace: 'nowrap'}}>
					{ligne(1).mots.map((w, i) => {
						const p = lin(t, w.a - 0.08, w.a + 0.2);
						const style = {display: 'inline-block', whiteSpace: 'pre' as const, opacity: p, filter: p < 0.99 ? `blur(${(6 * (1 - p)).toFixed(2)}px)` : undefined};
						if (normal(w.m) !== 'clients') return <span key={i} style={style}>{w.m}</span>;
						// « clients » : les lettres partent une à une, de la dernière à la première
						const lettres = [...w.m];
						return (
							<span key={i} style={{...style, color: C.cyan}}>
								{lettres.map((l, k) => {
									const debut = efface + (lettres.length - 1 - k) * 0.12;
									const q = lin(t, debut, debut + 0.32, 0, 1, ENTREE_DOUCE);
									return (
										<span key={k} style={{display: 'inline-block', opacity: 1 - q, filter: q > 0.01 ? `blur(${(q * 8).toFixed(2)}px)` : undefined, transform: `translateY(${(-q * 0.28).toFixed(3)}em)`}}>
											{l}
										</span>
									);
								})}
							</span>
						);
					})}
				</div>
			</Pose>
		</div>
	);
};

/* ─────────────────────────── 3-5 · le statut, la question, le client parti ─────────────────────────── */

/** Ton statut, vu par toi : la robe dessinée, son prix en grand (comme on l'écrit sur un statut), le compteur de vues. */
const EcranStatut: React.FC<{t: number; vu: number}> = ({t, vu}) => {
	const t3 = ligne(3).debut;
	const remplissage = lin(t, t3 - 0.2, t3 + 5.5, 0, 1, (x) => x);
	const robe = PRODUITS.robe;
	const allume = vu > 0.5;
	return (
		<div style={{position: 'absolute', inset: 0, fontFamily: TEXTE, color: C.blanc}}>
			<BarreEtat heure="00:12" couleur="rgba(245,243,255,0.92)" police={TEXTE} />
			{/* les trois statuts du jour, le premier qui défile */}
			<div style={{position: 'absolute', top: 50, left: 14, right: 14, display: 'flex', gap: 4}}>
				{[0, 1, 2].map((k) => (
					<div key={k} style={{flex: 1, height: 4, borderRadius: 2, background: 'rgba(245,243,255,0.25)', overflow: 'hidden'}}>
						<div style={{width: `${k === 0 ? remplissage * 100 : 0}%`, height: '100%', background: C.blanc}} />
					</div>
				))}
			</div>
			<div style={{position: 'absolute', top: 66, left: 16, display: 'flex', alignItems: 'center', gap: 10}}>
				<div style={{width: 40, height: 40, borderRadius: 20, background: 'linear-gradient(140deg, #3a2a63, #1b1730)', boxShadow: 'inset 0 0 0 1.5px rgba(245,243,255,0.25)'}} />
				<div>
					<div style={{fontWeight: 700, fontSize: 19}}>Mon statut</div>
					<div style={{fontWeight: 500, fontSize: 14, color: C.gris}}>Aujourd'hui, 00:10</div>
				</div>
			</div>
			<div
				style={{
					position: 'absolute',
					top: 120,
					left: 12,
					right: 12,
					height: 392,
					borderRadius: 22,
					background: 'radial-gradient(circle at 50% 36%, #2e2250 0%, #17131f 74%)',
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					justifyContent: 'center',
				}}
			>
				<Dessin produit="robe" taille={176} epaisseur={3.6} />
				<div style={{fontWeight: 600, fontSize: 24, marginTop: 6}}>{robe.nom}</div>
				<div style={{fontWeight: 800, fontSize: 46, letterSpacing: '-0.02em', lineHeight: 1.05}}>{francs(robe.prix)}</div>
			</div>
			{/* le compteur des vues : 0, puis 1 sur « voit » */}
			<div style={{position: 'absolute', bottom: 22, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '8px 20px', borderRadius: 24, background: allume ? 'rgba(34,211,238,0.14)' : 'rgba(245,243,255,0.07)'}}>
					<Oeil taille={32} couleur={allume ? C.cyan : 'rgba(245,243,255,0.7)'} />
					<span style={{fontWeight: 800, fontSize: 34, color: allume ? C.cyan : 'rgba(245,243,255,0.7)', display: 'inline-block', transform: `scale(${(1 + 0.4 * Math.sin(Math.PI * Math.min(1, Math.max(0, vu)))).toFixed(3)})`}}>
						{allume ? '1' : '0'}
					</span>
				</div>
			</div>
		</div>
	);
};

export const Statut: React.FC<{t: number}> = ({t}) => {
	const {a, b} = plan('statut');
	const es = entreeSortie(t, a, b);
	if (!es.visible) return null;
	const t4 = ligne(4).debut;
	const tCombien = quand(4, 'combien');
	const tDors = quand(5, 'dors');
	const tPart = quand(5, 'il');
	const tAilleurs = quand(5, 'ailleurs');

	const decale = lin(t, t4 - 0.1, t4 + 0.5, 0, 1, VA_ET_VIENT);
	const xTel = 960 - 270 * decale;
	const vu = lin(t, quand(3, 'voit') - 0.05, quand(3, 'voit') + 0.25);
	const eteint = lin(t, tDors + 0.05, tDors + 0.4, 0, 1, VA_ET_VIENT);
	const telOpacite = 1 - 0.8 * lin(t, tAilleurs - 0.2, tAilleurs + 0.4);

	// la bulle : un « pop » (ressort amorti), puis elle file à droite quand le client s'en va
	const age = t - (t4 + 0.02);
	const pop = age < 0 ? 0 : 1 - Math.exp(-age * 9) * Math.cos(age * 16);
	const part = lin(t, tPart, tPart + 0.55, 0, 1, ENTREE_DOUCE);
	const bulleVisible = age >= 0 && part < 1;
	const robe = PRODUITS.robe;

	const pAilleurs = lin(t, tAilleurs - 0.08, tAilleurs + 0.3);

	return (
		<div style={{position: 'absolute', inset: 0, ...es.style}}>
			<Pose x={xTel} y={545} style={{opacity: telOpacite, transform: `scale(${(1.14 - 0.08 * decale).toFixed(4)})`}}>
				<Telephone eteint={eteint}>
					<EcranStatut t={t} vu={vu} />
				</Telephone>
			</Pose>
			{bulleVisible ? (
				<Pose
					x={1255 + 760 * part}
					y={520}
					style={{
						opacity: Math.min(1, age * 8) * (1 - part),
						transform: `scale(${(0.55 + 0.45 * pop).toFixed(4)})`,
						transformOrigin: '0% 100%',
						filter: part > 0.01 ? `blur(${(part * 10).toFixed(2)}px)` : undefined,
					}}
				>
					<div
						style={{
							width: 680,
							padding: '26px 32px 20px',
							borderRadius: '38px 10px 38px 38px',
							background: '#1d1a28',
							boxShadow: '0 30px 90px rgba(0,0,0,0.55), inset 0 0 0 1px rgba(245,243,255,0.07)',
							fontFamily: TEXTE,
							color: C.blanc,
						}}
					>
						<div style={{display: 'flex', alignItems: 'center', gap: 16, padding: '12px 16px', borderRadius: 16, background: 'rgba(245,243,255,0.05)', borderLeft: `5px solid ${C.cyan}`}}>
							<Dessin produit="robe" taille={56} epaisseur={7} />
							<div>
								<div style={{fontWeight: 700, fontSize: 28, color: C.cyan}}>Statut</div>
								<div style={{fontWeight: 500, fontSize: 27, color: C.gris}}>
									{robe.nom} · {francs(robe.prix)}
								</div>
							</div>
						</div>
						<div style={{fontWeight: 700, fontSize: 80, letterSpacing: '-0.025em', marginTop: 16, lineHeight: 1.1}}>C'est combien ?</div>
						<div style={{display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 10, marginTop: 6, fontWeight: 500, fontSize: 28, color: C.gris}}>
							00:12 <Coches taille={30} deux={lin(t, tCombien - 0.05, tCombien + 0.1)} />
						</div>
					</div>
				</Pose>
			) : null}
			{pAilleurs > 0 ? (
				<Pose x={1300} y={540}>
					<div
						style={{
							...TYPO,
							fontSize: 190,
							letterSpacing: '-0.03em',
							color: C.orange,
							opacity: pAilleurs,
							filter: pAilleurs < 0.99 ? `blur(${((1 - pAilleurs) * 8).toFixed(2)}px)` : undefined,
							transform: `scale(${(0.96 + 0.04 * pAilleurs).toFixed(4)})`,
							textShadow: '0 0 40px rgba(255,138,30,0.45), 0 0 120px rgba(255,138,30,0.25)',
						}}
					>
						ailleurs.
					</div>
				</Pose>
			) : null}
		</div>
	);
};
