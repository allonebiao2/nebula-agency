// Rend des images fixes d'une composition, en UNE ouverture du navigateur :
// `npx remotion still` relance Chrome à chaque image (30 s sur ce PC).
//
//   node _outils/planches.mjs dimanche-plan 1.2 7.2 19.9 …   (secondes)
//
// Les images vont dans out/planches/<composition>/<seconde>.jpg.
//
// ⚠️ CHAQUE `renderStill` RECOPIE LES VIDÉOS DE LA COMPOSITION dans un dossier
// temporaire neuf (`%TEMP%/remotion-v4.0.512-assets*`, 193 Mo pour la vidéo du
// dimanche), et ne l'efface jamais : 45 images de contrôle ont rempli le disque
// le 2026-09-27 et fait tomber le rendu sur ENOSPC. On nettoie en sortant.
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import {mkdirSync, readdirSync, rmSync, statSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const debut = Date.now();

const [, , id, ...secondes] = process.argv;
const ici = path.resolve(import.meta.dirname, '..');
const sortie = path.join(ici, 'out', 'planches', id);
mkdirSync(sortie, {recursive: true});

const serveUrl = await bundle({entryPoint: path.join(ici, 'src/index.ts'), publicDir: path.join(ici, 'public')});
const navigateur = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}});
const composition = await selectComposition({serveUrl, id, puppeteerInstance: navigateur, timeoutInMilliseconds: 120000});

for (const s of secondes) {
	const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(s) * composition.fps));
	const fichier = path.join(sortie, `${String(s).padStart(6, '0')}.jpg`);
	await renderStill({serveUrl, composition, frame, output: fichier, imageFormat: 'jpeg', jpegQuality: 88, puppeteerInstance: navigateur, timeoutInMilliseconds: 120000});
	console.log('·', s, 's →', path.basename(fichier));
}
await navigateur.close({silent: true});

// le ménage : ce que Remotion a laissé dans le dossier temporaire depuis le début
for (const nom of readdirSync(os.tmpdir())) {
	if (!nom.startsWith('remotion-')) continue;
	const chemin = path.join(os.tmpdir(), nom);
	if (statSync(chemin).mtimeMs >= debut - 1000) rmSync(chemin, {recursive: true, force: true});
}
