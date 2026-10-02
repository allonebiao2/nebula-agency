// Rend une longue composition PAR MORCEAUX, puis les recolle avec le son.
//
//   node _outils/rendu_morceaux.mjs dimanche-plan
//   node _outils/rendu_morceaux.mjs nebula-30s 150 1   (morceaux de 150 images, UN onglet)
//
// Pourquoi : le 2026-09-27, le rendu d'un seul tenant du plan du dimanche
// (6 391 images) a vu Chrome tomber à l'image 2 562, faute de mémoire (8 Go,
// 1,6 libres), et tout était perdu. Ici chaque morceau ouvre un navigateur neuf
// et le referme, le cache des images de la vidéo de fond est bridé, et un
// morceau fini est gardé : relancer la commande reprend là où elle s'était
// arrêtée.
//
// Le son est rendu à part, d'un seul tenant (sans capture d'écran, c'est léger),
// puis posé sur les morceaux recollés sans réencodage de l'image.
//
// ⚠️ Chaque rendu recopie les vidéos de la composition dans
// `%TEMP%/remotion-v4.0.512-assets*` (~200 Mo) et ne l'efface jamais : on
// nettoie après chaque morceau (voir planches.mjs). ⚠️ SEULEMENT les
// `-assets*` : le paquet webpack (`remotion-webpack-bundle-*`) sert encore au
// morceau suivant, et l'effacer a tué le premier essai après un morceau.
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import {existsSync, mkdirSync, readdirSync, renameSync, rmSync, statSync, writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const [, , id, taille = '640', onglets = '2'] = process.argv;
const ici = path.resolve(import.meta.dirname, '..');
const dossier = path.join(ici, 'out', 'morceaux', id);
const final = path.join(ici, 'out', `${id}.mp4`);
const FFMPEG = path.join(ici, 'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe');
mkdirSync(dossier, {recursive: true});

const heure = () => new Date().toTimeString().slice(0, 8);
const dire = (...m) => console.log(heure(), ...m);

const menage = (depuis) => {
	for (const nom of readdirSync(os.tmpdir())) {
		if (!nom.startsWith('remotion-v') || !nom.includes('-assets')) continue;
		const chemin = path.join(os.tmpdir(), nom);
		try {
			if (statSync(chemin).mtimeMs >= depuis - 1000) rmSync(chemin, {recursive: true, force: true});
		} catch {}
	}
};

const COMMUN = {
	imageFormat: 'jpeg',
	jpegQuality: 88,
	chromiumOptions: {gl: 'angle'},
	timeoutInMilliseconds: 120000,
	// Le compositeur garde en mémoire les images décodées de la vidéo de fond
	// (1080x1920) : sans plafond, il grossit jusqu'à faire tomber Chrome.
	offthreadVideoCacheSizeInBytes: 256 * 1024 * 1024,
	overwrite: true,
};

dire('Préparation du paquet…');
const serveUrl = await bundle({entryPoint: path.join(ici, 'src/index.ts'), publicDir: path.join(ici, 'public')});
const composition = await selectComposition({serveUrl, id, chromiumOptions: {gl: 'angle'}, timeoutInMilliseconds: 120000});
const total = composition.durationInFrames;
const pas = Number(taille);
const bornes = [];
for (let a = 0; a < total; a += pas) bornes.push([a, Math.min(total - 1, a + pas - 1)]);
dire(`${id} : ${total} images, ${bornes.length} morceaux de ${pas}`);

const nomMorceau = (k) => path.join(dossier, `${String(k).padStart(2, '0')}.mp4`);

for (const [k, [a, b]] of bornes.entries()) {
	const sortie = nomMorceau(k);
	if (existsSync(sortie)) {
		dire(`morceau ${k + 1}/${bornes.length} déjà fait`);
		continue;
	}
	// Un seul onglet quand la mémoire manque (le 2026-10-02, Claude Code a arrêté le rendu à deux
	// onglets de la vidéo NEBULA : le PC n'avait plus que quelques centaines de Mo libres).
	for (const concurrency of onglets === '1' ? [1] : [2, 1]) {
		const debut = Date.now();
		const provisoire = sortie.replace(/\.mp4$/, '.part.mp4');
		try {
			dire(`morceau ${k + 1}/${bornes.length} (images ${a}-${b}), ${concurrency} onglet(s)`);
			let dernier = -1;
			await renderMedia({
				...COMMUN,
				serveUrl,
				composition,
				codec: 'h264',
				muted: true,
				frameRange: [a, b],
				concurrency,
				outputLocation: provisoire,
				onProgress: ({progress}) => {
					const pc = Math.floor(progress * 10);
					if (pc !== dernier) {
						dernier = pc;
						dire(`   ${pc * 10} %`);
					}
				},
			});
			renameSync(provisoire, sortie);
			dire(`   fait en ${Math.round((Date.now() - debut) / 1000)} s`);
			menage(debut);
			break;
		} catch (e) {
			menage(debut);
			rmSync(provisoire, {force: true});
			dire(`   ÉCHEC : ${String(e?.message ?? e).split('\n')[0]}`);
			if (concurrency === 1) throw e;
		}
	}
}

// Le son, d'un seul tenant.
const son = path.join(dossier, 'son.wav');
if (!existsSync(son)) {
	const debut = Date.now();
	dire('Le son…');
	await renderMedia({...COMMUN, serveUrl, composition, codec: 'wav', concurrency: 2, outputLocation: son + '.part.wav'});
	renameSync(son + '.part.wav', son);
	menage(debut);
}

// On recolle l'image sans la réencoder, et on pose le son (AAC, comme Remotion).
const liste = path.join(dossier, 'liste.txt');
writeFileSync(liste, bornes.map((_, k) => `file '${nomMorceau(k).replace(/\\/g, '/')}'`).join('\n') + '\n');
dire('Assemblage…');
execFileSync(
	FFMPEG,
	['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', liste, '-i', son, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', final],
	{stdio: 'inherit'},
);
rmSync(serveUrl, {recursive: true, force: true});
dire(`Terminé : ${final}`);
