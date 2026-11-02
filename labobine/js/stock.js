// LA BOBINE · le stockage local. Projets et médias restent dans le navigateur de l'utilisateur (IndexedDB) :
// rien ne part sur un serveur, et un projet se rouvre hors connexion.

const NOM = 'labobine';
const VERSION = 1;
let base = null;

function ouvrir() {
  if (base) return base;
  base = new Promise((ok, ko) => {
    const r = indexedDB.open(NOM, VERSION);
    r.onupgradeneeded = () => {
      const db = r.result;
      if (!db.objectStoreNames.contains('projets')) db.createObjectStore('projets', { keyPath: 'id' });
      if (!db.objectStoreNames.contains('medias')) db.createObjectStore('medias', { keyPath: 'id' });
    };
    r.onsuccess = () => ok(r.result);
    r.onerror = () => ko(r.error);
    r.onblocked = () => ko(new Error('Base bloquée par un autre onglet de LA BOBINE.'));
  });
  return base;
}

async function req(magasin, mode, action) {
  const db = await ouvrir();
  return new Promise((ok, ko) => {
    const tx = db.transaction(magasin, mode);
    const r = action(tx.objectStore(magasin));
    tx.oncomplete = () => ok(r && 'result' in r ? r.result : undefined);
    tx.onerror = () => ko(tx.error);
    tx.onabort = () => ko(tx.error || new Error('Transaction annulée'));
  });
}

export const lireProjets = async () => ((await req('projets', 'readonly', (s) => s.getAll())) || [])
  .sort((a, b) => b.modifieLe - a.modifieLe);
export const lireProjet = (id) => req('projets', 'readonly', (s) => s.get(id));
export const ecrireProjet = (p) => req('projets', 'readwrite', (s) => s.put(p));
export const effacerProjet = (id) => req('projets', 'readwrite', (s) => s.delete(id));

export const lireMedia = (id) => req('medias', 'readonly', (s) => s.get(id));
export const ecrireMedia = (m) => req('medias', 'readwrite', (s) => s.put(m));
export const effacerMedia = (id) => req('medias', 'readwrite', (s) => s.delete(id));
export const lireTousMedias = async () => (await req('medias', 'readonly', (s) => s.getAll())) || [];

/** Efface les médias qu'aucun projet n'utilise plus. */
export async function ramasserMedias() {
  const projets = await lireProjets();
  const utilises = new Set();
  for (const p of projets) {
    for (const id of p.medias || []) utilises.add(id);
    for (const t of p.pistes) for (const c of t.clips) for (const id of [c.media, c.lut && c.lut.media, c.inverse && c.inverse.media]) if (id) utilises.add(id);
  }
  const medias = await req('medias', 'readonly', (s) => s.getAllKeys());
  for (const id of medias || []) if (!utilises.has(id)) await effacerMedia(id);
}

export async function demanderPersistance() {
  try { if (navigator.storage && navigator.storage.persist) await navigator.storage.persist(); } catch { /* facultatif */ }
}

export async function espaceUtilise() {
  try {
    if (!navigator.storage || !navigator.storage.estimate) return null;
    const e = await navigator.storage.estimate();
    return { utilise: e.usage || 0, quota: e.quota || 0 };
  } catch { return null; }
}
