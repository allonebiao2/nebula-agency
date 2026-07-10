// Boussole — sécurité locale : code PIN (verrouillage de l'appli sur l'appareil).
// Le code n'est JAMAIS stocké en clair : on garde seulement une empreinte SHA-256
// salée. C'est une protection d'accès sur l'appareil (pas un chiffrement des données).

const LS_PIN = 'boussole:pin';

async function sha(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
function load() { try { return JSON.parse(localStorage.getItem(LS_PIN)) || null; } catch { return null; } }
function save(o) { try { localStorage.setItem(LS_PIN, JSON.stringify(o)); } catch {} }

export function hasPin() { const o = load(); return !!(o && o.hash); }
export function lockOnOpen() { const o = load(); return !!(o && o.hash && o.lockOpen !== false); }
export function setLockOnOpen(v) { const o = load(); if (o && o.hash) { o.lockOpen = !!v; save(o); } }

export async function setPin(pin) {
  const salt = Math.random().toString(36).slice(2, 12);
  save({ hash: await sha(salt + pin), salt, lockOpen: true });
}
export async function verifyPin(pin) {
  const o = load(); if (!o || !o.hash) return false;
  return (await sha(o.salt + pin)) === o.hash;
}
export function clearPin() { try { localStorage.removeItem(LS_PIN); } catch {} }

// --- Empreintes de PIN génériques (pour les codes des vendeurs, stockés dans l'équipe) ---
export async function makePinRecord(pin) {
  const salt = Math.random().toString(36).slice(2, 12);
  return { hash: await sha(salt + pin), salt };
}
export async function matchesRecord(pin, rec) {
  if (!rec || !rec.hash || !rec.salt) return false;
  return (await sha(rec.salt + pin)) === rec.hash;
}
export async function verifyOwner(pin) { return verifyPin(pin); }
