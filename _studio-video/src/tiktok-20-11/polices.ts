/**
 * Les polices des statuts du jour, reprises telles quelles :
 *  · TITRE : Syne 800, la display du site, pour ce qui frappe ;
 *  · TEXTE : Inter, pour ce qui se lit (jusqu'à 900 pour les phrases qui claquent) ;
 *  · MONO  : JetBrains Mono, pour l'heure, le minuteur, le prix et le numéro.
 * ⚠️ Syne 800 est très large (0,75 à 1 em par lettre) : ses lignes restent courtes.
 */
import {loadFont as inter} from '@remotion/google-fonts/Inter';
import {loadFont as jetbrains} from '@remotion/google-fonts/JetBrainsMono';
import {loadFont as syne} from '@remotion/google-fonts/Syne';

export const TITRE = syne('normal', {weights: ['800'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const TEXTE = inter('normal', {weights: ['500', '600', '700', '800', '900'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const MONO = jetbrains('normal', {weights: ['500', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;
