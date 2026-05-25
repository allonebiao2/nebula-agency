const fs = require('fs');
const path = require('path');

const HTML = 'clients/04-luxury-skin-clinic/ina-luxury.html';
const BASE = 'clients/04-luxury-skin-clinic/assets/images/ina-luxury';

const src = fs.readFileSync(HTML, 'utf8');

// 1) Find the IMG object opening (line "const IMG=" or "var IMG =")
const imgObjStart = src.search(/(?:const|var|let)\s+IMG\s*=\s*\{/);
console.log('IMG object start char:', imgObjStart);
if (imgObjStart > 0) {
  const before = src.slice(Math.max(0, imgObjStart - 100), imgObjStart + 200);
  console.log('Context around IMG declaration:\n', before.replace(/\s+/g, ' ').slice(0, 350));
}

// 2) Find all <img src=... and tag context
const imgTagRe = /<img\b[^>]*src=("|')([^"']{0,80})/g;
let m;
const tagRefs = [];
while ((m = imgTagRe.exec(src)) !== null && tagRefs.length < 10) {
  tagRefs.push({ pos: m.index, src: m[2] });
}
console.log('\n=== Echantillons <img src=...> ===');
tagRefs.forEach(t => console.log(`  pos ${t.pos} : src="${t.src.slice(0, 60)}..."`));

// 3) Find IMG[...] references in JS (template strings, etc.)
const imgAccessRe = /IMG\[([^\]]+)\]/g;
const accesses = [...src.matchAll(imgAccessRe)].slice(0, 5);
console.log('\n=== Echantillons IMG[...] ===');
accesses.forEach(a => console.log(`  pos ${a.index} : ${a[0]}`));

// 4) Walk existing disk files in ina-luxury/ — produce slug map
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
const files = walk(BASE);
function slugifyFile(filename) {
  return filename.toLowerCase().replace(/\.[a-z]+$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
function slugifyName(name) {
  // Strip diacritics, lowercase, replace non-alnum by -
  return name.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

console.log('\n=== Fichiers disk (slug derive) ===');
files.slice(0, 8).forEach(f => {
  const filename = path.basename(f);
  console.log(`  ${filename.padEnd(45)} -> slug=${slugifyFile(filename)}`);
});

// 5) Test mapping for the identified product keys
const productKeys = [
  'Oxygène Masque', 'Sérum Anagen', 'Acné Control Crème', 'Après-Shampoing Sensicare',
  'Beurre Clarté', 'Bonbon Scrub', 'Busserole Beauty Bar', 'Crème Oxygène',
  'Body Butter Baiser Nocturne'
];

// Build slug->file map
const slugMap = new Map();
files.forEach(f => {
  const slug = slugifyFile(path.basename(f));
  slugMap.set(slug, f);
});

console.log('\n=== Test mapping nom-produit -> fichier (slug match) ===');
productKeys.forEach(k => {
  const slug = slugifyName(k);
  const file = slugMap.get(slug);
  console.log(`  "${k}"\n    slug="${slug}"\n    match=${file ? file.replace(/\\/g, '/').split('assets/')[1] : 'NONE'}`);
});
