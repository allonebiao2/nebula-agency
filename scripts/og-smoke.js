/**
 * Smoke test apres allegement :
 * - Parse les <script> inline (syntax check)
 * - Verifier que tous les chemins relatifs dans IMG{} pointent vers des fichiers existants
 * - Verifier que le logo path existe
 * - Mesurer la taille finale
 */
const fs = require('fs');
const path = require('path');

const HTML = 'clients/04-luxury-skin-clinic/ina-luxury.html';
const ROOT = 'clients/04-luxury-skin-clinic/';
const src = fs.readFileSync(HTML, 'utf8');

console.log('=== 1. Syntax check JS inline ===');
const scripts = [...src.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let jsOk = true;
scripts.forEach((s, i) => {
  if (!s.trim()) return;
  try { new Function(s); console.log(`  script #${i+1} : OK (${s.length} chars)`); }
  catch (e) { jsOk = false; console.log(`  script #${i+1} : FAIL - ${e.message}`); }
});

console.log('\n=== 2. Verification fichiers references ===');
// Extract IMG object entries
const imgStart = src.indexOf('const IMG={');
let depth = 0, end = -1;
for (let i = imgStart + 'const IMG='.length; i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
}
const imgBody = src.slice(imgStart + 'const IMG={'.length, end);
const entryRe = /"((?:[^"\\]|\\.)*)"\s*:\s*"([^"]+)"/g;
const entries = [...imgBody.matchAll(entryRe)];

let missing = 0, present = 0;
entries.forEach(e => {
  const key = e[1];
  const val = e[2];
  if (val.startsWith('data:')) {
    console.log(`  [BASE64 STILL THERE] ${key}`);
    missing++; return;
  }
  const fullPath = path.join(ROOT, val);
  if (fs.existsSync(fullPath)) {
    present++;
  } else {
    console.log(`  [MISSING FILE] ${key} -> ${val}`);
    missing++;
  }
});
console.log(`Resultats : ${present} OK / ${missing} manquants sur ${entries.length}`);

console.log('\n=== 3. Verification logo path ===');
const logoMatch = src.match(/<img class="wg-logo" src="([^"]+)"/);
if (logoMatch) {
  const logoVal = logoMatch[1];
  if (logoVal.startsWith('data:')) console.log('  Logo encore en base64 !');
  else {
    const full = path.join(ROOT, logoVal);
    console.log(`  Logo path : ${logoVal} -> ${fs.existsSync(full) ? 'OK' : 'MISSING'}`);
  }
}

console.log('\n=== 4. Stats fichier ===');
const newSize = Buffer.byteLength(src, 'utf8');
const bakSize = fs.statSync(HTML + '.bak').size;
console.log(`HTML avant : ${(bakSize/1024).toFixed(1)} KB`);
console.log(`HTML apres : ${(newSize/1024).toFixed(1)} KB`);
console.log(`Gain       : ${((bakSize-newSize)/1024).toFixed(1)} KB (-${(100*(bakSize-newSize)/bakSize).toFixed(1)}%)`);

console.log('\n=== 5. Base64 restants dans le HTML ===');
const remain = [...src.matchAll(/data:image\/(jpeg|jpg|png|webp);base64,/g)];
console.log(`Restant : ${remain.length} (cible : 0)`);

console.log('\n=== 6. loading="lazy" check ===');
const lazyCount = (src.match(/loading="lazy"/g) || []).length;
console.log(`Tags avec loading="lazy" : ${lazyCount}`);

console.log(jsOk && missing === 0 && remain.length === 0 ? '\nSMOKE OK' : '\nSMOKE WARNINGS');
