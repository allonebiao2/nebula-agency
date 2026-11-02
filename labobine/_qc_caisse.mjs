// LA BOBINE · contrôle de la caisse, sans clé, sans réseau, sans base.
//   node --experimental-strip-types labobine/_qc_caisse.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { lireOffre, nouvelleReference, REFERENCE_FORME, OFFRES } from './supabase/functions/_shared/offres.ts';
import { decider } from './supabase/functions/_shared/saspay.ts';

const ICI = dirname(fileURLToPath(import.meta.url));
const lire = (...p) => readFileSync(join(ICI, ...p), 'utf8');
const sansCR = (s) => s.replace(/\r/g, '');
let verts = 0; const rouges = [];
const ok = (c, m) => { if (c) { verts += 1; console.log(`  ✔ ${m}`); } else { rouges.push(m); console.log(`  ✘ ${m}`); } };

console.log('Barème');
ok(lireOffre('pro-mois')?.total === 1500 && lireOffre('pro-mois').jours === 31 && lireOffre('pro-mois').credits === 100, 'Pro 1 mois : 1 500 F, 31 jours, 100 crédits');
ok(lireOffre('pro-an')?.total === 12000 && lireOffre('pro-an').jours === 366 && lireOffre('pro-an').credits === 1200, 'Pro 1 an : 12 000 F, 366 jours, 1 200 crédits');
ok(['__proto__', 'constructor', 'toString', 'pro', '', null, 1500, { offre: 'pro-mois' }].every((x) => lireOffre(x) === null), "rien d'autre n'est une offre (__proto__, constructor, un nombre, un objet)");
ok(Object.values(OFFRES).every((o) => o.total >= 200), 'chaque prix dépasse le minimum SasPay de 200 F');

console.log('Références');
const refs = Array.from({ length: 2000 }, nouvelleReference);
ok(refs.every((r) => REFERENCE_FORME.test(r)), 'les références ont la forme LB-XXXXXXXXXX');
ok(new Set(refs).size === refs.length, '2 000 références tirées, aucune en double');
const sql = lire('supabase', 'labobine.sql');
ok(sql.includes("check (reference ~ '^LB-[A-Z0-9]{10}$')"), 'la base impose la même forme de référence');

console.log('Décisions du webhook');
const r = { devise: 'XOF', multiple: 1, deviseSiAbsente: '' };
const cmd = { existe: true, etat: 'attente', total: 1500 };
const n = (x) => ({ etat: 'paye', montant: 1500, devise: 'XOF', reference: 'LB-ABCDEFGHJK', session: '', evenementId: 'e1', ...x });
ok(decider(n({}), cmd, r).payer === true, 'paiement juste : la commande est payée');
ok(decider(n({ montant: 1000 }), cmd, r).payer === false, 'montant inférieur : refusé');
ok(decider(n({ devise: 'NGN' }), cmd, r).payer === false, 'devise étrangère (nairas) : refusée');
ok(decider(n({ devise: '' }), cmd, r).payer === false, 'devise absente : refusée');
ok(decider(n({}), { ...cmd, etat: 'payee' }, r).payer === false, 'notification rejouée sur une commande payée : rien');
ok(decider(n({ etat: 'echec' }), cmd, r).payer === false, 'paiement échoué : rien');
ok(decider(n({}), null, r).payer === false, 'commande inconnue : rien');

console.log('Le module SasPay partagé');
const notre = sansCR(lire('supabase', 'functions', '_shared', 'saspay.ts'));
ok(notre === sansCR(lire('..', 'malettre', 'supabase', 'functions', '_shared', 'saspay.ts')), 'saspay.ts identique à celui de MA LETTRE À…');
ok(notre === sansCR(lire('..', 'piste', 'supabase', 'functions', '_shared', 'saspay.ts')), 'saspay.ts identique à celui de PISTE');

console.log('Les fonctions serveur');
const commande = lire('supabase', 'functions', 'labobine-commande', 'index.ts');
const webhook = lire('supabase', 'functions', 'labobine-paiement-recu', 'index.ts');
ok(commande.includes('lireOffre(d?.offre)') && !/d\??\.(total|montant|prix)/.test(commande), 'la commande lit le prix dans le barème, jamais dans le corps');
ok(commande.includes('db.auth.getUser(jeton)') && commande.includes("'connexion requise' }, 401"), 'la commande exige un compte connecté');
ok(commande.includes('/#merci') && commande.includes("nomDefaut: 'Client LA BOBINE'"), 'retour et reçu propres à LA BOBINE (pas ceux de PISTE)');
ok(webhook.includes("Deno.env.get('LABOBINE_SECRET_WEBHOOK')") && !webhook.includes("get('SASPAY_SECRET_WEBHOOK')") && !webhook.includes('MALETTRE_SECRET'), 'le webhook a son propre secret, sans repli sur un autre');
ok(webhook.includes('horodatageFrais(') && webhook.includes('verifierSignature('), 'le webhook vérifie la signature ET l’âge');
ok(!webhook.includes('SASPAY_SIGNATURE_OBLIGATOIRE'), 'aucun réglage ne permet de couper la vérification');
ok(webhook.indexOf('labobine_payer') > webhook.indexOf('decider('), 'on ne paie qu’après la décision');

console.log('La base');
const tables = [...sql.matchAll(/create table if not exists labobine\.(\w+)/g)].map((m) => m[1]);
ok(tables.length === 6 && tables.every((t) => sql.includes(`alter table labobine.${t}`) && new RegExp(`alter table labobine\\.${t}\\s+enable row level security`).test(sql)), `les ${tables.length} tables ont la sécurité par ligne`);
const fonctions = [...sql.matchAll(/create or replace function (public\.labobine_\w+)\(/g)].map((m) => m[1]);
const blocs = sql.split('create or replace function').slice(1);
ok(blocs.length === fonctions.length && blocs.every((b) => b.includes("security definer set search_path = ''")), `les ${fonctions.length} fonctions ont un search_path vide`);
ok(!/to anon/i.test(sql), 'rien n’est accordé aux visiteurs anonymes');
const versClient = sql.split('to authenticated;')[0].split('grant execute on function').pop();
ok(!/commande|journal|payer|paiement/.test(versClient), 'aucune fonction de la caisse n’est ouverte au navigateur');
ok(/labobine_payer\(text, integer, integer\)\s+to service_role/.test(sql), 'payer est réservé au serveur');

console.log('Le navigateur');
const compte = lire('js', 'compte.js');
const offre = lire('js', 'offre.js');
ok(/export const OUVERT = (false|true) \|\| \(typeof window/.test(compte), "l'interrupteur des comptes est un simple booléen écrit dans le code (il n'ouvre aucun droit)");
ok(compte.includes('sb_publishable_') && !compte.includes('service_role') && !compte.includes('sb_secret_'), 'seule la clé publique est dans la page');
ok(offre.includes('estPro = () => proActif()') && !offre.includes('localStorage'), 'Pro ne se lit que dans les droits rendus par le serveur');

console.log(`\n${verts} verts, ${rouges.length} rouges`);
process.exit(rouges.length ? 1 : 0);
