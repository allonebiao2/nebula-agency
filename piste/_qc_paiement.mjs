/*
  PISTE · le contrôle du paiement en ligne.

      node _qc_paiement.mjs

  ⚠️ SANS CLÉ, SANS RÉSEAU, SANS BASE. Tout ce qui décide de l'argent vit dans
  `supabase/functions/_shared/saspay.ts`, en Web standard : ce fichier l'essaie
  sous Node exactement tel qu'il tournera chez Deno. Un garde-fou qu'aucun
  contrôle ne peut atteindre n'est pas un garde-fou, c'est une intention.

  ⚠️ Le serveur d'essai est un `node:http` sur 127.0.0.1 : la création de
  session est donc vraiment exercée, en-tête d'autorisation compris, sans
  jamais appeler SasPay.
*/
import http from 'node:http'

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

/* ═══ 4. la décision ══════════════════════════════════════════════════════ */
const R = { ...M.reglages(), devise: 'XOF', multiple: 1 }
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
dire(vu?.corps?.amount === 10000 && vu?.corps?.currency === 'XOF', `le montant et la devise partent tels quels`)
dire(vu?.corps?.reference === 'PISTE-AB2C' && vu?.corps?.metadata?.reference === 'PISTE-AB2C',
     `notre référence part à deux endroits, pour maximiser les chances qu'elle revienne`)

/* ⚠️ Avec SASPAY_MONTANT_MULTIPLIE, c'est le corps envoyé qui change aussi. */
process.env.SASPAY_MONTANT_MULTIPLIE = '100'
await M.ouvrirSession(M.reglages(), { reference: 'PISTE-AB2C', montant: 10000, description: 'essai' })
dire(vu?.corps?.amount === 1000000, `en centimes, la demande part aussi en centimes`)
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
