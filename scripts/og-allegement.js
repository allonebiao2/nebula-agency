/**
 * Allege ina-luxury.html :
 * 1) Logo PNG -> path relatif vers assets/images/logos/logo-luxury-club-229.png
 * 2) IMG{} object : pour chaque produit, base64 -> chemin relatif assets/images/ina-luxury/...
 * 3) Pour Body Butter Baiser Nocturne (orphelin), extraire son base64 vers le disque
 * 4) Ajouter loading="lazy" aux <img src="${IMG[...]}"> du template
 *
 * BACKUP : copie .bak du HTML avant toute modification.
 */
const fs = require('fs');
const path = require('path');

const HTML = 'clients/04-luxury-skin-clinic/ina-luxury.html';
const BASE_DIR = 'clients/04-luxury-skin-clinic/assets/images/ina-luxury';
const LOGO_PATH = 'assets/images/logos/logo-luxury-club-229.png';
const BODY_BUTTER_TARGET = 'corps/creme-corps/body-butter-baiser-nocturne.jpg';

// --- 1. Backup ---
const BACKUP = HTML + '.bak';
if (!fs.existsSync(BACKUP)) {
  fs.copyFileSync(HTML, BACKUP);
  console.log('Backup ->', BACKUP);
} else {
  console.log('Backup deja present, on continue.');
}

let src = fs.readFileSync(HTML, 'utf8');
const originalSize = Buffer.byteLength(src, 'utf8');

// --- 2. Build slug -> file map ---
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
const files = walk(BASE_DIR);
const slugMap = new Map();
files.forEach(f => slugMap.set(slugify(path.basename(f).replace(/\.[a-z]+$/i, '')), f));

// --- 3. Replace wg-logo PNG base64 ---
const logoTagRe = /<img class="wg-logo" src="data:image\/png;base64,[^"]+"/;
const logoMatch = src.match(logoTagRe);
if (logoMatch) {
  src = src.replace(logoTagRe, `<img class="wg-logo" src="${LOGO_PATH}"`);
  console.log('Logo PNG -> path relatif OK');
} else {
  console.log('!! Logo wg-logo non trouve');
}

// --- 4. Build new IMG object content ---
// First, identify all entries in IMG{}: parse start..end with brace counting
const imgStart = src.indexOf('const IMG={');
if (imgStart < 0) throw new Error('IMG object introuvable');
let depth = 0, end = -1;
for (let i = imgStart + 'const IMG='.length; i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
}
if (end < 0) throw new Error('Fin de IMG{} introuvable');

const imgBody = src.slice(imgStart + 'const IMG={'.length, end);
// Extract entries: "key": "data:image/...;base64,xxxx",
const entryRe = /"((?:[^"\\]|\\.)*)"\s*:\s*"(data:image\/(jpeg|jpg|png|webp);base64,[A-Za-z0-9+/=]+)"\s*,?/g;
const entries = [...imgBody.matchAll(entryRe)];
console.log('Entrees IMG : ', entries.length);

// --- 5. For each entry, compute new value (path relatif) ---
const RESULTS = [];
const newPairs = [];
for (const e of entries) {
  const key = e[1];
  const slug = slugify(key);
  let target = slugMap.get(slug);

  if (!target) {
    // Fallback : chercher dans assets/images/ tout entier (peut etre dans cozy/ par ex.)
    const wider = walk('clients/04-luxury-skin-clinic/assets/images');
    target = wider.find(f => slugify(path.basename(f).replace(/\.[a-z]+$/i, '')) === slug);
    if (target) {
      console.log(`Match large -> ${target}`);
    }
  }

  if (!target) {
    // Vrai orphelin : extraire le base64 vers ina-luxury/corps/* ou un dossier raisonnable
    const b64 = e[2].split(';base64,')[1];
    const bin = Buffer.from(b64, 'base64');
    // Heuristique de placement : "huile" -> corps/huile-corps/, "body butter" -> corps/creme-corps/
    let subfolder = 'corps/creme-corps';
    if (/huile/i.test(key)) subfolder = 'corps/huile-corps';
    else if (/serum|s.rum/i.test(key)) subfolder = 'visage/serums';
    else if (/cr.me/i.test(key)) subfolder = 'visage/cremes';
    const outPath = path.join(BASE_DIR, subfolder, slug + '.jpg');
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, bin);
    target = outPath;
    console.log(`Extracted base64 -> ${outPath} (${(bin.length/1024).toFixed(1)} KB)`);
  }

  const relPath = target.replace(/\\/g, '/').split('clients/04-luxury-skin-clinic/')[1];
  // JSON-safe key (re-stringify to handle accents/escapes)
  newPairs.push(`${JSON.stringify(key)}:${JSON.stringify(relPath)}`);
  RESULTS.push({ key, status: 'OK', target: relPath });
}

// --- 6. Replace IMG body in src ---
const newImgBody = '\n  ' + newPairs.join(',\n  ') + '\n';
const newImgObj = 'const IMG={' + newImgBody + '}';
src = src.slice(0, imgStart) + newImgObj + src.slice(end + 1);
console.log('IMG object remplace.');

// --- 7. Add loading="lazy" to <img src="${IMG[...]}"> (only those tags) ---
// Match <img ...src="${IMG[anything]}"... > and inject loading="lazy" if not present
const lazyAdded = [];
src = src.replace(/<img\b([^>]*?)src=(["'`])\$\{IMG\[[^\]]+\]\}\2([^>]*?)>/g, (full, pre, q, post) => {
  if (/\bloading\s*=/.test(full)) return full; // already has loading attr
  lazyAdded.push(full.slice(0, 80) + '...');
  // Insert loading="lazy" right after <img
  return `<img loading="lazy"${pre}src=${q}\${IMG[` + full.split('${IMG[')[1];
});
console.log(`loading="lazy" ajoute sur ${lazyAdded.length} tag(s)`);

// --- 8. Write file ---
fs.writeFileSync(HTML, src);
const newSize = Buffer.byteLength(src, 'utf8');
console.log('\n=== RESULTAT ===');
console.log('Avant : ', (originalSize/1024).toFixed(1), 'KB');
console.log('Apres : ', (newSize/1024).toFixed(1), 'KB');
console.log('Gain  : ', ((originalSize - newSize)/1024).toFixed(1), 'KB',
            `(-${(100*(originalSize-newSize)/originalSize).toFixed(1)}%)`);
console.log('\n=== Detail mapping ===');
const ok = RESULTS.filter(r => r.status === 'OK').length;
const ko = RESULTS.filter(r => r.status !== 'OK').length;
console.log(`OK : ${ok} / Non matches : ${ko}`);
if (ko > 0) {
  console.log('Non matches detail :');
  RESULTS.filter(r => r.status !== 'OK').forEach(r => console.log(`  - "${r.key}" (slug=${r.slug})`));
}
