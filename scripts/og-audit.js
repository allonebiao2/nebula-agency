/**
 * Audit base64 d'une page HTML (compte, poids, structure, slug-mapping).
 * Usage : node scripts/og-audit.js <chemin/page.html>
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HTML = process.argv[2];
if (!HTML) { console.error('Usage: node scripts/og-audit.js <page.html>'); process.exit(1); }
const HTML_DIR = path.dirname(HTML);
const ASSETS_IMAGES = path.join(HTML_DIR, 'assets/images');

const src = fs.readFileSync(HTML, 'utf8');

// 1) Base64 detail
const b64Regex = /data:image\/(jpeg|jpg|png|webp|svg\+xml);base64,([A-Za-z0-9+/=]+)/g;
const matches = [...src.matchAll(b64Regex)];
console.log(`=== ${path.basename(HTML)} ===`);
console.log(`Taille HTML : ${(Buffer.byteLength(src,'utf8')/1024).toFixed(1)} KB`);
console.log(`Base64 imgs : ${matches.length}`);

let totalB64 = 0;
matches.forEach(m => totalB64 += m[2].length);
console.log(`Poids cumule b64 : ${(totalB64/1024).toFixed(1)} KB texte, ${(totalB64*0.75/1024).toFixed(1)} KB binaire`);

// 2) Detect structure: IMG object? wg-logo? inline?
const hasIMG = /\b(?:const|var|let)\s+IMG\s*=\s*\{/.test(src);
const hasWgLogo = /<img class="wg-logo" src="data:image/.test(src);
console.log(`Structure : IMG object = ${hasIMG ? 'OUI' : 'non'} | wg-logo = ${hasWgLogo ? 'OUI' : 'non'}`);

// 3) For each base64, try to identify context (key in JSON or alt attr)
function findKey(pos) {
  const ctx = src.slice(Math.max(0, pos - 250), pos);
  // JS key style "Nom":"data:..."
  const k1 = ctx.match(/["']([^"']{3,80})["']\s*:\s*["']$/);
  if (k1) return { type: 'js-key', value: k1[1] };
  // alt= just before src=
  const k2 = ctx.match(/alt=["']([^"']{1,80})["'][^"']*src=["']$/);
  if (k2) return { type: 'alt', value: k2[1] };
  // class wg-logo
  if (/class="wg-logo"/.test(ctx)) return { type: 'class', value: 'wg-logo' };
  // class hero-logo etc.
  const k4 = ctx.match(/class=["']([^"']*logo[^"']*)["'][^"']*src=["']$/);
  if (k4) return { type: 'class', value: k4[1] };
  return { type: '?', value: ctx.slice(-80).replace(/\s+/g, ' ') };
}

console.log('\n--- Detail base64 ---');
matches.forEach((m, i) => {
  const bin = Buffer.from(m[2], 'base64');
  const hash = crypto.createHash('sha256').update(bin).digest('hex').slice(0, 12);
  const k = findKey(m.index);
  const sz = (bin.length / 1024).toFixed(1);
  console.log(`  #${String(i+1).padStart(2)} ${m[1].padEnd(8)} ${sz.padStart(7)} KB  hash=${hash}  [${k.type}] ${k.value}`);
});

// 4) Slug match
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
const files = walk(ASSETS_IMAGES);
const slugMap = new Map();
files.forEach(f => slugMap.set(slugify(path.basename(f).replace(/\.[a-z]+$/i, '')), f));

console.log('\n--- Mapping disk ---');
let matched = 0, missing = 0;
matches.forEach((m, i) => {
  const k = findKey(m.index);
  if (k.type === '?') { return; } // unidentifiable
  const slug = slugify(k.value);
  const file = slugMap.get(slug);
  if (file) {
    matched++;
    const rel = file.replace(/\\/g, '/').split(HTML_DIR.replace(/\\/g, '/') + '/')[1] || file;
    console.log(`  #${String(i+1).padStart(2)} OK -> ${rel}`);
  } else {
    missing++;
    console.log(`  #${String(i+1).padStart(2)} MISS (slug="${slug}")`);
  }
});
console.log(`\nMatched: ${matched} / Missing: ${missing} / Unidentifiable: ${matches.length - matched - missing}`);
