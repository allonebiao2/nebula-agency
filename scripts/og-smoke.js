/**
 * Smoke test post-allegement.
 * Usage : node scripts/og-smoke.js <chemin/page.html>
 */
const fs = require('fs');
const path = require('path');

const HTML = process.argv[2];
if (!HTML) { console.error('Usage: node scripts/og-smoke.js <page.html>'); process.exit(1); }
const ROOT = path.dirname(HTML).replace(/\\/g, '/') + '/';
const src = fs.readFileSync(HTML, 'utf8');

console.log(`=== Smoke ${path.basename(HTML)} ===`);

// 1) JS parse
console.log('\n[1] Syntax JS inline');
const scripts = [...src.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let jsOk = true;
scripts.forEach((s, i) => {
  if (!s.trim()) return;
  try { new Function(s); console.log(`  script #${i+1}: OK (${s.length} chars)`); }
  catch (e) { jsOk = false; console.log(`  script #${i+1}: FAIL - ${e.message}`); }
});

// 2) <img src="..."> et IMG{} references existent ?
console.log('\n[2] References fichiers');
// Tous les src="..." qui ne sont pas data:
const imgSrcs = [...src.matchAll(/src=["']([^"'$][^"']*)["']/g)].map(m => m[1])
  .filter(s => !s.startsWith('http') && !s.startsWith('data:') && !s.startsWith('#') && !s.includes('${'));
const imgUniq = [...new Set(imgSrcs)];
let missing = 0;
imgUniq.forEach(s => {
  const fullPath = path.join(ROOT, s);
  if (!fs.existsSync(fullPath)) {
    console.log(`  MISSING: ${s}`);
    missing++;
  }
});
console.log(`  ${imgUniq.length - missing} OK / ${missing} missing sur ${imgUniq.length} src= referencees`);

// 3) IMG{} entries
console.log('\n[3] IMG{} entries (si present)');
const imgStart = src.indexOf('const IMG={');
let imgEntries = 0, imgMissing = 0;
if (imgStart >= 0) {
  let depth = 0, end = -1;
  for (let i = imgStart + 'const IMG='.length; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
  }
  const body = src.slice(imgStart + 'const IMG={'.length, end);
  const entries = [...body.matchAll(/"((?:[^"\\]|\\.)*)"\s*:\s*"([^"]+)"/g)];
  imgEntries = entries.length;
  entries.forEach(e => {
    if (e[2].startsWith('data:')) { console.log(`  BASE64 STILL: ${e[1]}`); imgMissing++; return; }
    if (!fs.existsSync(path.join(ROOT, e[2]))) {
      console.log(`  MISSING: ${e[1]} -> ${e[2]}`);
      imgMissing++;
    }
  });
  console.log(`  ${imgEntries - imgMissing} OK / ${imgMissing} ko sur ${imgEntries} entrees`);
} else {
  console.log('  (pas d\'objet IMG{})');
}

// 4) Base64 restants
console.log('\n[4] Base64 restants');
const remain = [...src.matchAll(/data:image\/(jpeg|jpg|png|webp);base64,/g)];
console.log(`  ${remain.length} (cible: 0)`);

// 5) Stats taille
console.log('\n[5] Stats taille');
const newSize = Buffer.byteLength(src, 'utf8');
console.log(`  HTML actuel : ${(newSize/1024).toFixed(1)} KB`);
if (fs.existsSync(HTML + '.bak')) {
  const bakSize = fs.statSync(HTML + '.bak').size;
  console.log(`  Backup .bak : ${(bakSize/1024).toFixed(1)} KB`);
  console.log(`  Gain        : ${((bakSize-newSize)/1024).toFixed(1)} KB (-${(100*(bakSize-newSize)/bakSize).toFixed(1)}%)`);
}

// 6) loading lazy
const lazyCount = (src.match(/loading="lazy"/g) || []).length;
console.log(`\n[6] loading="lazy" tags : ${lazyCount}`);

const allOk = jsOk && missing === 0 && imgMissing === 0 && remain.length === 0;
console.log(allOk ? '\nSMOKE OK' : '\nSMOKE WARNINGS - revoir les MISSING / BASE64 STILL');
process.exit(allOk ? 0 : 1);
