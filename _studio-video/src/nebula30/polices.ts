/**
 * Les trois voix du site nebula-agency.online, reprises telles quelles :
 *  · TITRE : Syne, la display à caractère du site (v9), pour ce qui s'annonce ;
 *  · TEXTE : Inter, pour ce qui se lit ;
 *  · MONO  : JetBrains Mono, pour les chiffres, les prix, les codes temporels.
 * Chargées depuis Google au rendu (le rendu attend qu'elles soient prêtes).
 */
import {loadFont as inter} from '@remotion/google-fonts/Inter';
import {loadFont as jetbrains} from '@remotion/google-fonts/JetBrainsMono';
import {loadFont as syne} from '@remotion/google-fonts/Syne';

export const TITRE = syne('normal', {weights: ['700', '800'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const TEXTE = inter('normal', {weights: ['300', '400', '500', '600', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const MONO = jetbrains('normal', {weights: ['400', '500', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;
