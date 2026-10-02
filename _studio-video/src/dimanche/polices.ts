/**
 * Trois voix, une par registre de la feuille :
 *  · TITRE  : Big Shoulders, condensée et massive, pour ce qu'on tamponne ;
 *  · TEXTE  : Archivo, grotesque à caractère, pour les sous-titres et les
 *             étiquettes (pas la Montserrat de CapCut qu'on remplace) ;
 *  · MAIN   : Caveat, l'écriture de celui qui prépare sa semaine au stylo.
 * Chargées depuis Google au rendu (le rendu attend qu'elles soient prêtes).
 */
import {loadFont as archivo} from '@remotion/google-fonts/Archivo';
import {loadFont as bigShoulders} from '@remotion/google-fonts/BigShoulders';
import {loadFont as caveat} from '@remotion/google-fonts/Caveat';

export const TITRE = bigShoulders('normal', {weights: ['700', '800', '900'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const TEXTE = archivo('normal', {weights: ['500', '700', '800', '900'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const MAIN = caveat('normal', {weights: ['600', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;
