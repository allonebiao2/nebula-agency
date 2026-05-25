/**
 * Allege une page HTML : extrait les base64 -> fichiers disque, remplace les
 * data:image;base64,... par les chemins relatifs, ajoute loading="lazy" sur
 * les tags <img> dans les templates JS (IMG[...]) ou ceux marques "below the fold".
 *
 * Strategie de mapping :
 *   1. Hash match : si le hash SHA-256 du base64 correspond a un fichier disque,
 *      on utilise ce fichier (bit-pour-bit identique, zero perte).
 *   2. Slug match (uniquement pour entries IMG{} avec une cle nommee) :
 *      utiliser le fichier disque ayant le meme slug.
 *   3. Extraction : si rien ne matche, extraire le base64 vers un fichier dans
 *      assets/images/extracted/.
 *
 * Usage : node scripts/og-allegement.js <chemin/page.html>
 *
 * Backup : copie .bak du HTML avant toute modification (skippe si deja present).
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HTML = process.argv[2];
if (!HTML) { console.error('Usage: node scripts/og-allegement.js <page.html>'); process.exit(1); }
const HTML_DIR = path.dirname(HTML).replace(/\\/g, '/');
const ASSETS_IMAGES = path.join(HTML_DIR, 'assets/images').replace(/\\/g, '/');
const EXTRACT_DIR = path.join(ASSETS_IMAGES, 'extracted').replace(/\\/g, '/');

// --- 1. Backup ---
const BACKUP = HTML + '.bak';
if (!fs.existsSync(BACKUP)) {
  fs.copyFileSync(HTML, BACKUP);
  console.log('Backup ->', BACKUP);
}
let src = fs.readFileSync(HTML, 'utf8');
const originalSize = Buffer.byteLength(src, 'utf8');

// --- 2. Helpers ---
function slugify(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
function walk(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else if (/\.(jpe?g|png|webp)$/i.test(e.name)) out.push(p);
  }
  return out;
}

// --- 3. Index des fichiers disque par hash et par slug ---
const files = walk(ASSETS_IMAGES);
const hashMap = new Map();   // hash -> file path
const slugMap = new Map();   // slug -> file path
for (const f of files) {
  const bin = fs.readFileSync(f);
  const hash = crypto.createHash('sha256').update(bin).digest('hex');
  hashMap.set(hash, f);
  const slug = slugify(path.basename(f).replace(/\.[a-z]+$/i, ''));
  if (!slugMap.has(slug)) slugMap.set(slug, f); // 1er gagne en cas de doublon
}
console.log(`Index disque : ${files.length} fichiers (${hashMap.size} hashes uniques)`);

// --- 4. Pour chaque base64 du HTML, decide du remplacement ---
const b64Regex = /data:image\/(jpeg|jpg|png|webp);base64,([A-Za-z0-9+/=]+)/g;
const replacements = []; // { fullMatch, replacement, info }
const seenB64 = new Map(); // dedup : meme base64 = meme replacement

let m;
while ((m = b64Regex.exec(src)) !== null) {
  const fullB64 = m[0];
  if (seenB64.has(fullB64)) {
    replacements.push({ fullMatch: fullB64, ...seenB64.get(fullB64) });
    continue;
  }

  const type = m[1];
  const b64Data = m[2];
  const bin = Buffer.from(b64Data, 'base64');
  const hash = crypto.createHash('sha256').update(bin).digest('hex');

  let target = null;
  let strategy = '';

  // Stratégie 1 : hash match
  if (hashMap.has(hash)) {
    target = hashMap.get(hash);
    strategy = 'HASH';
  } else {
    // Stratégie 2 : slug match basé sur le contexte JS-key
    const ctx = src.slice(Math.max(0, m.index - 250), m.index);
    const keyMatch = ctx.match(/["']([^"']{3,80})["']\s*:\s*["']$/);
    if (keyMatch) {
      const slug = slugify(keyMatch[1]);
      if (slugMap.has(slug)) {
        target = slugMap.get(slug);
        strategy = 'SLUG(' + keyMatch[1] + ')';
      }
    }
  }

  if (!target) {
    // Stratégie 3 : extraction
    const ctx = src.slice(Math.max(0, m.index - 250), m.index);
    const keyMatch = ctx.match(/["']([^"']{3,80})["']\s*:\s*["']$/);
    const classMatch = ctx.match(/class=["']([^"']{1,60})["'][^"']*src=["']$/);
    const baseName = keyMatch ? slugify(keyMatch[1])
                  : classMatch ? slugify(classMatch[1])
                  : 'img-' + hash.slice(0, 8);
    fs.mkdirSync(EXTRACT_DIR, { recursive: true });
    const ext = (type === 'jpeg' || type === 'jpg') ? '.jpg' : '.' + type;
    const outPath = path.join(EXTRACT_DIR, baseName + ext);
    fs.writeFileSync(outPath, bin);
    target = outPath;
    strategy = 'EXTRACT';
    // ajouter au hashMap pour deduper si plusieurs base64 identiques
    hashMap.set(hash, outPath);
  }

  // Construire le path relatif depuis le HTML
  const relPath = target.replace(/\\/g, '/').replace(HTML_DIR + '/', '');

  const info = { replacement: relPath, strategy, size: bin.length };
  seenB64.set(fullB64, info);
  replacements.push({ fullMatch: fullB64, ...info });

  console.log(`  [${strategy.padEnd(7)}] ${(bin.length/1024).toFixed(1).padStart(7)} KB -> ${relPath}`);
}

// --- 5. Appliquer les remplacements (uniques) ---
// Pour eviter de remplacer plusieurs fois la meme chaine, on remplace une fois par valeur unique.
const uniqueB64 = new Map(); // b64 -> path
replacements.forEach(r => uniqueB64.set(r.fullMatch, r.replacement));
for (const [b64, p] of uniqueB64) {
  // Remplacer toutes les occurences de ce base64 (peut etre dans plusieurs <img>)
  src = src.split(b64).join(p);
}

// --- 6. Ajouter loading="lazy" sur les <img src="${IMG[...]}"> ---
let lazyCount = 0;
src = src.replace(/<img\b([^>]*?)src=(["'`])\$\{IMG\[[^\]]+\]\}\2([^>]*?)>/g, (full, pre, q, post) => {
  if (/\bloading\s*=/.test(full)) return full;
  lazyCount++;
  return `<img loading="lazy"${pre}src=${q}\${IMG[` + full.split('${IMG[')[1];
});
if (lazyCount > 0) console.log(`loading="lazy" ajoute sur ${lazyCount} template(s) IMG[...]`);

// --- 7. Sauvegarde ---
fs.writeFileSync(HTML, src);
const newSize = Buffer.byteLength(src, 'utf8');
console.log('\n=== RESULTAT ' + path.basename(HTML) + ' ===');
console.log(`Avant : ${(originalSize/1024).toFixed(1)} KB`);
console.log(`Apres : ${(newSize/1024).toFixed(1)} KB`);
console.log(`Gain  : ${((originalSize - newSize)/1024).toFixed(1)} KB (-${(100*(originalSize-newSize)/originalSize).toFixed(1)}%)`);

const stats = { HASH: 0, SLUG: 0, EXTRACT: 0 };
replacements.forEach(r => {
  const s = r.strategy.split('(')[0];
  stats[s] = (stats[s] || 0) + 1;
});
console.log(`Stats : HASH=${stats.HASH} SLUG=${stats.SLUG} EXTRACT=${stats.EXTRACT}`);
