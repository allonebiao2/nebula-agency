/*
  PISTE · le contrôle du paiement en ligne.

      node --experimental-strip-types _qc_paiement.mjs

  ⚠️ Le drapeau n'est pas un caprice : ce fichier importe un `.ts`, que Deno lit
  nativement et que Node 22 refuse sans lui (`ERR_UNKNOWN_FILE_EXTENSION`).
  `npm run qc:paiement` le porte deja.

  ⚠️ SANS CLÉ, SANS RÉSEAU, SANS BASE. Tout ce qui décide de l'argent vit dans
  `supabase/functions/_shared/saspay.ts`, en Web standard : ce fichier l'essaie
  sous Node exactement tel qu'il tournera chez Deno. Un garde-fou qu'aucun
  contrôle ne peut atteindre n'est pas un garde-fou, c'est une intention.

  ⚠️ Le serveur d'essai est un `node:http` sur 127.0.0.1 : la création de
  session est donc vraiment exercée, en-tête d'autorisation compris, sans
  jamais appeler SasPay.
*/
import http from 'node:http'
import fs from 'node:fs'

const M = await import('./supabase/functions/_shared/saspay.ts')
const ok = [], ko = []
const dire = (b, q) => (b ? ok : ko).push(q)

/* ═══ 1. lire un statut ═══════════════════════════════════════════════════ */
for (const m of ['paid', 'SUCCESS', 'payment.succeeded', 'Completed', 'PAYÉ', 'approved'])
  dire(M.lireEtat(m) === 'paye', `« ${m} » se lit « payé »`)
for (const m of ['failed', 'CANCELLED', 'expired', 'échec', 'declined'])
  dire(M.lireEtat(m) === 'echoue', `« ${m} » se lit « échoué »`)
for (const m of ['pending', 'PROCESSING', 'en_attente', 'initiated'])
  dire(M.lireEtat(m) === 'attente', `« ${m} » se lit « en attente »`)
dire(M.lireEtat('') === 'inconnu', `un statut vide reste inconnu`)
dire(M.lireEtat('quelque_chose_de_neuf') === 'inconnu', `un statut jamais vu reste inconnu`)

/* ═══ 2. lire une notification ════════════════════════════════════════════ */
const n1 = M.lireNotification({
  event: 'payment.succeeded',
  data: { id: 'evt_77', payment_id: 'pay_42', amount: 10000, currency: 'xof',
          metadata: { reference: 'PISTE-AB2C' } },
})
dire(n1.reference === 'PISTE-AB2C', `la référence PISTE se lit même enfouie dans metadata`)
dire(n1.session === 'pay_42', `l'identifiant du fournisseur se lit à part`)
dire(n1.montant === 10000 && n1.devise === 'XOF' && n1.etat === 'paye', `montant, devise et état se lisent`)

/* ⛔ Le piège qui rendrait toute commande introuvable : prendre l'identifiant
   du fournisseur pour notre code de commande. */
const n2 = M.lireNotification({ id: 'ch_123', status: 'paid', amount: '12 500',
                                order_id: 'PISTE-ZZ99', currency: 'XOF' })
dire(n2.reference === 'PISTE-ZZ99', `« order_id » est notre référence, pas « id »`)
dire(n2.session === 'ch_123', `« id » reste l'identifiant du fournisseur`)
dire(n2.montant === 12500, `un montant écrit « 12 500 » se lit 12500`)

/* ⛔ LE POINT LE PLUS IMPORTANT DU FICHIER : un montant introuvable ne devient
   JAMAIS zéro. Sans ça, une notification mal formée vaudrait « payé 0 F ». */
const n3 = M.lireNotification({ id: 'x', status: 'paid', currency: 'XOF' })
dire(n3.montant === null, `un montant absent rend null, jamais 0`)
dire(M.lireNotification({}).etat === 'inconnu', `un message vide ne dit rien`)

/* ═══ 3. la signature ═════════════════════════════════════════════════════ */
const CORPS = '{"id":"evt_1","status":"paid","amount":10000}'
const { hex, b64 } = await M.signer(CORPS, 'secret-de-test')
dire(await M.verifierSignature(CORPS, hex, 'secret-de-test'), `une signature hexadécimale passe`)
dire(await M.verifierSignature(CORPS, b64, 'secret-de-test'), `une signature base64 passe`)
dire(await M.verifierSignature(CORPS, 'sha256=' + hex, 'secret-de-test'), `le préfixe « sha256= » est toléré`)
dire(await M.verifierSignature(CORPS, `t=1234,v1=${hex}`, 'secret-de-test'), `la forme « t=…,v1=… » est tolérée`)
dire(!(await M.verifierSignature(CORPS, hex, 'autre-secret')), `un autre secret est refusé`)
dire(!(await M.verifierSignature(CORPS + ' ', hex, 'secret-de-test')), `un corps modifié d'un espace est refusé`)
dire(!(await M.verifierSignature(CORPS, '', 'secret-de-test')), `une signature vide est refusée`)
dire(!(await M.verifierSignature(CORPS, hex, '')), `sans secret, rien ne passe`)
dire(M.memeChaine('abc', 'abc') && !M.memeChaine('abc', 'abd') && !M.memeChaine('ab', 'abc'),
     `la comparaison est à temps constant et gère les longueurs`)

/* ── le schéma réel de SasPay : horodatage + « . » + corps ──────────────────
   Confirmé dans la doc le 2026-09-03. Signer le corps seul refusait TOUT, et
   le symptôme (« signature refusée » sur des messages parfaitement valables)
   pousse droit vers la seule bêtise qui compte : couper la vérification. */
const TS = String(Math.floor(Date.now() / 1000))
const sigTs = (await M.signer(CORPS, 'secret-de-test', TS)).hex
dire(await M.verifierSignature(CORPS, sigTs, 'secret-de-test', TS),
     `la signature couvre l'horodatage ET le corps`)
dire(!(await M.verifierSignature(CORPS, sigTs, 'secret-de-test', String(Number(TS) + 1))),
     `un horodatage d'une seconde à côté ne passe pas : il est bien dans la signature`)
dire(!(await M.verifierSignature(CORPS, hex, 'secret-de-test', TS)),
     `une signature du corps seul est refusée quand un horodatage est annoncé`)

/* ── l'âge, qui est un contrôle à part ───────────────────────────────────── */
const MAINTENANT = 1_800_000_000_000
dire(M.horodatageFrais(String(MAINTENANT / 1000), 300, MAINTENANT), `un horodatage à l'heure passe`)
dire(M.horodatageFrais(String(MAINTENANT / 1000 - 299), 300, MAINTENANT), `299 secondes de retard passent`)
dire(!M.horodatageFrais(String(MAINTENANT / 1000 - 301), 300, MAINTENANT), `301 secondes de retard sont refusées`)
dire(!M.horodatageFrais(String(MAINTENANT / 1000 + 3600), 300, MAINTENANT), `une heure dans le futur est refusée`)
dire(!M.horodatageFrais('', 300, MAINTENANT), `un horodatage absent est un refus, pas un laissez-passer`)
dire(!M.horodatageFrais('bientôt', 300, MAINTENANT), `un horodatage illisible est refusé`)
dire(!M.horodatageFrais('0', 300, MAINTENANT), `zéro est refusé`)

/* ── le nom « reference » appartient aux deux ────────────────────────────────
   La vraie notification `transaction.success` porte `data.reference` =
   « TXN-… », le numéro de SasPay. Le nôtre, quand il revient, est plus bas
   dans `metadata`. La recherche allant en largeur d'abord, sans précaution
   c'est le leur qui gagne, et aucune commande n'est jamais retrouvée. */
const nSas = M.lireNotification({
  event: 'transaction.success',
  data: {
    id: '9c3f2a10-4b7e-4f1a-9d2e-9b6a7c1e4a02',
    reference: 'TXN-2026-000456', status: 'SUCCESS',
    amount: '25000.00', currency: 'XOF',
    metadata: { reference: 'PISTE-AB2C' },
  },
})
dire(nSas.reference === 'PISTE-AB2C', `notre code l'emporte sur la référence du fournisseur`)
dire(nSas.etat === 'paye', `« transaction.success » se lit « payé »`)
dire(nSas.montant === 25000, `un montant en chaîne décimale se lit`)
dire(nSas.devise === 'XOF', `la devise se lit dans l'enveloppe data`)

/* ⚠️ ET SANS metadata — c'est le cas que la doc décrit aujourd'hui : la
   notification ne porte ni metadata ni numéro de session. On ne doit alors
   SURTOUT PAS prendre « TXN-… » pour une commande PISTE. */
const nNu = M.lireNotification({
  event: 'transaction.success',
  data: { id: 'abc', reference: 'TXN-2026-000456', status: 'SUCCESS', amount: '25000.00', currency: 'XOF' },
})
dire(!/^PISTE-/.test(nNu.reference), `sans metadata, la référence SasPay ne se déguise pas en commande PISTE`)

/* ── le vocabulaire des etats ────────────────────────────────────────────────
   Mesure sur la base le 2026-09-03 : piste.commandes n'accepte que
   attente / paye / livre / expire / annule. Le reste de l'application dit
   « payee » et « livree ». Un controle qui LIT le fichier, parce que la valeur
   ecrite est une constante dans le code du webhook et que rien d'autre ne la
   verifie avant le premier paiement reussi. */
const ETATS_BASE = ['attente', 'paye', 'livre', 'expire', 'annule']
const recu = fs.readFileSync(new URL('./supabase/functions/piste-paiement-recu/index.ts', import.meta.url), 'utf8')
const ecrits = [...recu.matchAll(/p_etat:\s*'([a-z]+)'/g)].map((m) => m[1])
dire(ecrits.length > 0, `le webhook ecrit bien un etat de commande`)
dire(ecrits.every((e) => ETATS_BASE.includes(e)),
     `tout etat ecrit par le webhook est accepte par la contrainte de la base (vu : ${ecrits.join(', ')})`)

/* Et le garde « deja payee » doit reconnaitre l'orthographe DE LA BASE, sinon
   il ne se declenche jamais et une notification rejouee repaie la commande. */
const Rdeja = { ...M.reglages(), devise: 'XOF', multiple: 1, deviseSiAbsente: '' }
const nDeja = { evenementId: 'e', reference: 'PISTE-AB2C', session: 's', montant: 10000, devise: 'XOF', etat: 'paye' }
for (const etat of ['paye', 'payee', 'livre', 'livree']) {
  dire(M.decider(nDeja, { existe: true, etat, total: 10000 }, Rdeja).payer === false,
       `une commande deja « ${etat} » n'est pas repayee`)
}
dire(M.decider(nDeja, { existe: true, etat: 'attente', total: 10000 }, Rdeja).payer === true,
     `une commande « attente » est bien encaissee`)

/* ── retrouver la commande par la transaction ────────────────────────────────
   C'est le maillon qui manquait : la notification ne nomme aucune commande.
   La session de checkout, elle, a gardé notre `metadata`. */
const srvL = http.createServer((q, r) => {
  r.writeHead(200, { 'Content-Type': 'application/json' })
  r.end(JSON.stringify({ success: true, data: { results: [
    { id: 'sess-1', transaction: 'autre-txn', metadata: { reference: 'PISTE-XXXX' }, description: 'PISTE-XXXX · x' },
    { id: 'sess-2', transaction: 'txn-42', metadata: { reference: 'PISTE-AB2C' }, description: 'PISTE-AB2C · essai' },
    { id: 'sess-3', transaction: null, metadata: { reference: 'PISTE-ZZZZ' }, description: 'PISTE-ZZZZ · y' },
  ] } }))
})
await new Promise((r) => srvL.listen(0, '127.0.0.1', r))
const rL = { ...M.reglages(), cle: 'sk_test_faux', base: `http://127.0.0.1:${srvL.address().port}`,
             chemin: '/api/v1/checkout-sessions/', entete: 'Authorization', prefixe: 'Bearer ' }
dire(await M.referenceParTransaction(rL, 'txn-42') === 'PISTE-AB2C',
     `la commande se retrouve par l'identifiant de transaction`)
dire(await M.referenceParTransaction(rL, 'txn-inconnue') === '',
     `une transaction inconnue ne rend rien, jamais la première de la liste`)
dire(await M.referenceParTransaction(rL, '') === '', `sans identifiant, aucun appel`)
dire(await M.referenceParTransaction({ ...rL, cle: '' }, 'txn-42') === '', `sans clé, aucun appel`)
srvL.close()

/* ⚠️ Et si le serveur répond mal : on rend '' , on ne devine pas. */
const srvM = http.createServer((q, r) => { r.writeHead(500); r.end('boum') })
await new Promise((r) => srvM.listen(0, '127.0.0.1', r))
dire(await M.referenceParTransaction({ ...rL, base: `http://127.0.0.1:${srvM.address().port}` }, 'txn-42') === '',
     `une erreur du fournisseur ne fabrique pas de commande`)
srvM.close()

/* ═══ 4. la décision ══════════════════════════════════════════════════════ */
const R = { ...M.reglages(), devise: 'XOF', multiple: 1, deviseSiAbsente: '' }
const CMD = { existe: true, etat: 'attente', total: 10000 }
const notif = (x = {}) => ({ evenementId: 'e', reference: 'PISTE-AB2C', session: 's',
                             montant: 10000, devise: 'XOF', etat: 'paye', ...x })

dire(M.decider(notif(), CMD, R).payer === true, `bon montant, bonne devise, état payé : on encaisse`)
dire(M.decider(notif({ etat: 'attente' }), CMD, R).payer === false, `« en attente » ne marque rien`)
dire(M.decider(notif({ etat: 'echoue' }), CMD, R).payer === false, `un échec ne marque rien`)
dire(M.decider(notif(), null, R).payer === false, `une commande inconnue ne marque rien`)

/* ⛔ LA DEVISE. Le tableau de bord SasPay proposait « CDF » : 10 000 CDF valent
   environ 2 100 F. Encaisser sans regarder la devise, c'est livrer au quart. */
const dCDF = M.decider(notif({ devise: 'CDF' }), CMD, R)
dire(dCDF.payer === false && /CDF/.test(dCDF.agi), `10 000 CDF ne paient pas une commande en XOF`)

/* ⛔ « ABSENT » N'EST PAS « BON ». Le compte accepte tous les MTN et tous les
   Moov Africa (Mongazi, 2026-09-03) : sans devise annoncée, 10 000 unités
   peuvent être des nairas. */
const dSans = M.decider(notif({ devise: '' }), CMD, R)
dire(dSans.payer === false && /absente/.test(dSans.agi), `une notification sans devise est refusée`)
dire(M.decider(notif({ devise: '' }), CMD, { ...R, deviseSiAbsente: 'XOF' }).payer === true,
     `elle passe seulement si SASPAY_DEVISE_SI_ABSENTE le dit explicitement`)
dire(M.decider(notif({ devise: '' }), CMD, { ...R, deviseSiAbsente: 'XAF' }).payer === false,
     `et ce réglage ne desserre rien : XAF supposé reste refusé face à XOF`)
for (const d of ['NGN', 'GHS', 'XAF', 'CDF'])
  dire(M.decider(notif({ devise: d }), CMD, R).payer === false, `${d} ne paie pas une commande en XOF`)

/* ⛔ LE MONTANT. */
dire(M.decider(notif({ montant: 5000 }), CMD, R).payer === false, `la moitié du montant ne paie pas`)
dire(M.decider(notif({ montant: 100 }), CMD, R).payer === false, `100 F ne paient pas 10 000 F`)
dire(M.decider(notif({ montant: null }), CMD, R).payer === false, `un montant illisible ne paie pas`)
dire(M.decider(notif({ montant: 10000.4 }), CMD, R).payer === true, `un arrondi sous le franc passe`)
const dTrop = M.decider(notif({ montant: 1000000 }), CMD, R)
dire(dTrop.payer === false && /1000000/.test(dTrop.agi) && /10000/.test(dTrop.agi),
     `un montant cent fois trop grand est refusé ET affiche les deux chiffres`)
/* ⚠️ C'est ce refus-là qui dira, au premier essai réel, si SasPay compte en
   centimes : il suffira alors de poser SASPAY_MONTANT_MULTIPLIE=100. */
dire(M.decider(notif({ montant: 1000000 }), CMD, { ...R, multiple: 100 }).payer === true,
     `avec SASPAY_MONTANT_MULTIPLIE=100, les centimes se convertissent`)

/* ⛔ Ne jamais faire reculer une commande déjà livrée. */
dire(M.decider(notif(), { ...CMD, etat: 'livree' }, R).payer === false, `une commande livrée ne redevient pas « payée »`)
dire(M.decider(notif(), { ...CMD, etat: 'payee' }, R).payer === false, `une commande déjà payée ne rejoue rien`)

/* ═══ 5. ouvrir une session, contre un faux SasPay ════════════════════════ */
let vu = null
const srv = http.createServer((q, r) => {
  let c = ''
  q.on('data', (d) => (c += d))
  q.on('end', () => {
    vu = { chemin: q.url, entetes: q.headers, corps: JSON.parse(c || '{}') }
    r.writeHead(200, { 'Content-Type': 'application/json' })
    r.end(JSON.stringify({ data: { id: 'sess_9', checkout_url: 'https://pay.exemple/xyz' } }))
  })
})
await new Promise((r) => srv.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${srv.address().port}`

process.env.SASPAY_CLE_SECRETE = 'sk_test_faux'
process.env.SASPAY_BASE = base
process.env.SASPAY_DEVISE = 'XOF'
const r5 = M.reglages()
const s5 = await M.ouvrirSession(r5, { reference: 'PISTE-AB2C', montant: 10000, description: 'essai' })

dire(s5.ok === true, `une session s'ouvre`)
dire(s5.url === 'https://pay.exemple/xyz', `l'adresse de paiement se lit dans la réponse`)
dire(s5.session === 'sess_9', `l'identifiant de session se lit dans la réponse`)
dire(String(vu?.entetes?.authorization || '').startsWith('Bearer sk_test_faux'), `la clé part dans l'en-tête, pas dans le corps`)
dire(!JSON.stringify(vu?.corps || {}).includes('sk_test_faux'), `la clé n'est jamais dans le corps`)
dire(vu?.corps?.amount === '10000.00' && vu?.corps?.currency === 'XOF',
     `le montant part en chaîne décimale, la devise telle quelle`)
dire(typeof vu?.corps?.amount === 'string', `le montant n'est JAMAIS un nombre nu (SasPay déclare une chaîne)`)
dire(vu?.corps?.metadata?.reference === 'PISTE-AB2C' && String(vu?.corps?.description || '').startsWith('PISTE-AB2C'),
     `notre référence part dans metadata ET dans la description`)
dire(vu?.corps?.customer_email && vu?.corps?.customer_name,
     `les deux champs client requis sont toujours remplis`)
dire(vu?.corps?.return_url && !('cancel_url' in (vu?.corps || {})),
     `une seule adresse de retour : cancel_url n'existe pas chez eux`)

/* ⛔ Mesuré sur le vrai compte : sous 200 XOF, SasPay refuse. On refuse avant
   lui, pour que le message soit lisible. */
const sMini = await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 100, description: 'essai' })
dire(sMini.ok === false && /minimum/i.test(sMini.erreur), `un montant sous 200 F est refusé chez nous, avec le chiffre`)
dire((await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 200, description: 'essai' })).ok === true,
     `200 F exactement passe`)

/* ⚠️ Avec SASPAY_MONTANT_MULTIPLIE, c'est le corps envoyé qui change aussi. */
process.env.SASPAY_MONTANT_MULTIPLIE = '100'
await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 10000, description: 'essai' })
dire(vu?.corps?.amount === '1000000.00', `en centimes, la demande part aussi en centimes`)
delete process.env.SASPAY_MONTANT_MULTIPLIE

/* Une erreur du fournisseur doit REMONTER son corps : c'est lui qui dira quel
   champ manque, et c'est comme ça que les hypothèses se corrigent en une fois. */
const srv2 = http.createServer((q, r) => {
  r.writeHead(422, { 'Content-Type': 'application/json' })
  r.end(JSON.stringify({ message: 'currency not supported' }))
})
await new Promise((r) => srv2.listen(0, '127.0.0.1', r))
process.env.SASPAY_BASE = `http://127.0.0.1:${srv2.address().port}`
const s6 = await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 10000, description: 'x' })
dire(s6.ok === false && /currency not supported/.test(s6.erreur), `une erreur SasPay remonte son message en clair`)

process.env.SASPAY_CLE_SECRETE = ''
dire((await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 1, description: 'x' })).ok === false,
     `sans clé, aucune session n'est ouverte`)

srv.close(); srv2.close()

/* ═══ le verdict ══════════════════════════════════════════════════════════ */
console.log(`\n  ${ok.length} verts, ${ko.length} rouges\n`)
for (const q of ko) console.log(`  ROUGE  ${q}`)
if (!ko.length) for (const q of ok) console.log(`  ok   ${q}`)
process.exit(ko.length ? 1 : 0)
