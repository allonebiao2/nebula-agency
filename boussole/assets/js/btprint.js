// Boussole — impression sur imprimante thermique Bluetooth (58 mm, ESC/POS).
// HONNÊTETÉ : le Bluetooth direct du navigateur (Web Bluetooth) marche sur
// Android (Chrome/Edge) et sur ordinateur (Chrome/Edge), en HTTPS. Il NE marche
// PAS sur iPhone/iPad (Apple ne l'autorise pas) : dans ce cas on garde
// l'impression via le navigateur. On ne promet donc rien qu'on ne tienne.

const LS_PRINTER = 'boussole:printer';

// Services BLE courants des mini-imprimantes thermiques (ESC/POS).
const SERVICE_UUIDS = [
  0x18f0,                                         // imprimantes type « MTP » / génériques
  0xff00, 0xffe0, 0xffb0, 0x1811, 0xff10,
  '49535343-fe7d-4ae5-8fa9-9fafd205e455',         // module BLE ISSC/Microchip (très répandu)
  '0000ff00-0000-1000-8000-00805f9b34fb',
];

let device = null, characteristic = null;

export function supported() {
  return typeof navigator !== 'undefined' && !!navigator.bluetooth;
}
export function savedName() {
  try { return localStorage.getItem(LS_PRINTER) || ''; } catch { return ''; }
}
export function isConnected() {
  return !!(characteristic && device && device.gatt && device.gatt.connected);
}

async function findWritable(server) {
  const services = await server.getPrimaryServices();
  for (const s of services) {
    let chars = [];
    try { chars = await s.getCharacteristics(); } catch { continue; }
    for (const c of chars) {
      if (c.properties && (c.properties.write || c.properties.writeWithoutResponse)) return c;
    }
  }
  throw new Error('Aucune sortie d’impression trouvée sur cet appareil.');
}

// Ouvre le sélecteur d'appareils, se connecte, mémorise le nom.
export async function connect() {
  if (!supported()) throw new Error('Bluetooth non disponible sur cet appareil.');
  device = await navigator.bluetooth.requestDevice({
    acceptAllDevices: true,
    optionalServices: SERVICE_UUIDS,
  });
  device.addEventListener('gattserverdisconnected', () => { characteristic = null; });
  const server = await device.gatt.connect();
  characteristic = await findWritable(server);
  try { localStorage.setItem(LS_PRINTER, device.name || 'Imprimante'); } catch {}
  return device.name || 'Imprimante';
}

async function ensure() {
  if (isConnected()) return;
  if (device && device.gatt) {
    const server = await device.gatt.connect();
    characteristic = await findWritable(server);
    return;
  }
  await connect();
}

// Écrit les octets par petits paquets (limite BLE).
async function writeBytes(bytes) {
  const CHUNK = 180;
  for (let i = 0; i < bytes.length; i += CHUNK) {
    const slice = bytes.slice(i, i + CHUNK);
    if (characteristic.writeValueWithoutResponse) await characteristic.writeValueWithoutResponse(slice);
    else await characteristic.writeValue(slice);
    await new Promise((r) => setTimeout(r, 24));
  }
}

export function forget() {
  try { if (device && device.gatt && device.gatt.connected) device.gatt.disconnect(); } catch {}
  device = null; characteristic = null;
  try { localStorage.removeItem(LS_PRINTER); } catch {}
}

// ---------- Génération ESC/POS ----------
const enc = new TextEncoder();
// Les imprimantes bon marché rendent mal les accents : on retire les diacritiques.
function ascii(s) { return String(s == null ? '' : s).normalize('NFD').replace(/[̀-ͯ]/g, ''); }

function pushText(arr, s) { enc.encode(ascii(s)).forEach((b) => arr.push(b)); }
function line(arr, s = '') { pushText(arr, s); arr.push(0x0a); }

const ESC = 0x1b, GS = 0x1d;
function bytesReceipt({ commerce = 'Boussole', date, lignes = [], total = 0, mode = '', vendeur = '', devise = 'F', footer = '' }) {
  const a = [];
  a.push(ESC, 0x40);                       // init
  a.push(ESC, 0x61, 0x01);                 // centrer
  a.push(ESC, 0x21, 0x30);                 // double hauteur+largeur
  line(a, commerce);
  a.push(ESC, 0x21, 0x00);                 // normal
  if (date) line(a, date);
  line(a, '--------------------------------');
  a.push(ESC, 0x61, 0x00);                 // gauche
  lignes.forEach((l) => {
    const nom = ascii(l.nom).slice(0, 32);
    const montant = `${Number(l.qte) || 0} x ${fmt(l.prix_unitaire, devise)}`;
    line(a, nom);
    line(a, pad(montant, fmt((l.qte || 0) * (l.prix_unitaire || 0), devise), 32));
  });
  line(a, '--------------------------------');
  a.push(ESC, 0x21, 0x20);                 // double largeur
  line(a, pad('TOTAL', fmt(total, devise), 16));
  a.push(ESC, 0x21, 0x00);
  if (mode) line(a, `Paye en ${ascii(mode)}`);
  if (vendeur) line(a, `Vendeur : ${ascii(vendeur)}`);
  a.push(ESC, 0x61, 0x01);
  line(a); line(a, footer || 'Merci !'); line(a);
  a.push(0x0a, 0x0a, 0x0a);
  a.push(GS, 0x56, 0x42, 0x00);            // coupe partielle
  return new Uint8Array(a);
}
function fmt(n, devise) { return `${Math.round(Number(n) || 0).toLocaleString('fr-FR')} ${devise}`.trim(); }
function pad(left, right, width) {
  left = String(left); right = String(right);
  const space = Math.max(1, width - left.length - right.length);
  return left + ' '.repeat(space) + right;
}

export async function printReceipt(data) {
  await ensure();
  await writeBytes(bytesReceipt(data));
}
export async function printTest(commerce, devise) {
  await ensure();
  await writeBytes(bytesReceipt({
    commerce: commerce || 'Boussole', date: new Date().toLocaleString('fr-FR'),
    lignes: [{ nom: 'Article de test', qte: 1, prix_unitaire: 1000 }],
    total: 1000, mode: 'Especes', devise: devise || 'F', footer: 'Impression OK !',
  }));
}
