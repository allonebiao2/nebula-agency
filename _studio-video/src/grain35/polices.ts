/**
 * Trois voix, choisies le 2026-10-03 sur spécimen (Mongazi : « une police ultra pro,
 * différente de ce qu'on pourrait voir habituellement ») :
 *  · TITRE  : Gloock, un serif très contrasté et rare, au ton de couverture de mode ;
 *  · ACCENT : Instrument Serif en ITALIQUE, en or, pour les mots qui comptent
 *             (« vous », « en premier », « piqûre ») : le fin contre le massif ;
 *  · TEXTE  : Instrument Sans, pour les étiquettes espacées, les prix, le numéro.
 * Écartées sur le spécimen : Ballet (illisible en petit), Italiana (son italique
 * est un faux italique, penché par le navigateur), Cormorant et Jost (ceux de la
 * vitrine : justement ce qu'on voit partout).
 * Chargées depuis Google au rendu (le rendu attend qu'elles soient prêtes).
 */
import {loadFont as gloock} from '@remotion/google-fonts/Gloock';
import {loadFont as instrumentSans} from '@remotion/google-fonts/InstrumentSans';
import {loadFont as instrumentSerif} from '@remotion/google-fonts/InstrumentSerif';

export const TITRE = gloock('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const ACCENT = instrumentSerif('italic', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
instrumentSerif('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']});
export const TEXTE = instrumentSans('normal', {weights: ['400', '500', '600'], subsets: ['latin', 'latin-ext']}).fontFamily;
