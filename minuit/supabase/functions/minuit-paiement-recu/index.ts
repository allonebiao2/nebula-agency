import { createClient } from 'jsr:@supabase/supabase-js@2'
import {
  decider, horodatageFrais, lireNotification, referenceParTransaction,
  reglages, verifierSignature,
} from '../_shared/saspay.ts'
import { JETON_FORME, palier } from '../_shared/lettre.ts'

/*
  MINUIT · la notification de paiement (webhook SasPay).

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase functions deploy minuit-paiement-recu --no-verify-jwt
  ⛔ `--no-verify-jwt` n'est pas une négligence : SasPay n'a pas de jeton
     Supabase à présenter. Ce qui protège cette porte n'est pas un JWT, c'est
     la signature vérifiée ci-dessous.

  ⛔ CE QUI FAIT FOI, C'EST CETTE PORTE, PAS LE RETOUR DU NAVIGATEUR. Un client
     ramené sur « merci » n'a rien prouvé : la page de retour se visite à la
     main. Seule une notification signée rend une lettre joignable.

  ⚠️ Toute la mécanique est celle de PISTE, qui tourne depuis le 2026-09-03.
     Ce qui change : ici, l'action est d'OUVRIR la lettre, et elle est
     inoffensive à répéter (poser « vivante » deux fois écrit la même valeur).
*/

/* ⚠️ RÉPONDRE 200 SIGNIFIE « REÇU, JE N'EN VEUX PLUS ». On ne rend 200 que
   lorsque l'événement est écrit au journal. Tout le reste rend une erreur,
   pour que le fournisseur renvoie : un événement perdu est un paiement
   invisible. */
const ok = (c: unknown, code = 200) =>
  new Response(JSON.stringify(c), { status: code, headers: { 'Content-Type': 'application/json' } })

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return ok({ ok: false, erreur: 'méthode' }, 405)

  const r = reglages()

  /* ⛔ LE CORPS BRUT, JAMAIS REPARSÉ. `JSON.parse` puis `JSON.stringify`
     réordonne les clés : la signature ne correspondrait plus jamais, et on
     finirait par « désactiver la vérification pour que ça marche ». */
  const brut = await req.text()

  const obligatoire = (Deno.env.get('SASPAY_SIGNATURE_OBLIGATOIRE') ?? '1') !== '0'
  const entete = req.headers.get(r.enteteSig) || req.headers.get('x-signature')
             || req.headers.get('signature') || ''
  const horodatage = req.headers.get(r.enteteTs) || req.headers.get('x-timestamp') || ''

  /* ⛔ DEUX CONTRÔLES, PAS UN. Une signature ne périme jamais : sans la borne
     d'âge, un message légitime intercepté se rejoue indéfiniment. */
  if (!horodatageFrais(horodatage, r.toleranceSig) && obligatoire) {
    console.error('saspay webhook · horodatage refusé', horodatage.slice(0, 24))
    return ok({ ok: false, erreur: 'horodatage' }, 401)
  }

  const signe = await verifierSignature(brut, entete, r.secretSig, horodatage)
  if (!signe && obligatoire) {
    console.error('saspay webhook · signature refusée', entete.slice(0, 24))
    return ok({ ok: false, erreur: 'signature' }, 401)
  }

  let corps: unknown = null
  try { corps = JSON.parse(brut) } catch { corps = { _texte: brut } }

  const n = lireNotification(corps)
  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
  )

  /* ── retrouver la lettre ─────────────────────────────────────────────── */
  /* Notre référence EST le jeton de la lettre. */
  let jeton = JETON_FORME.test(n.reference) ? n.reference : ''
  if (!jeton && n.session) {
    const { data } = await db.rpc('minuit_paiement_par_session', { p_session: n.session })
    const s = Array.isArray(data) ? data[0] : data
    if (s?.jeton) jeton = String(s.jeton)
  }
  /* ⛔ DERNIER RECOURS, ET IL EST NÉCESSAIRE : mesuré chez PISTE le
     2026-09-03, la notification de SasPay ne porte NI notre référence NI le
     numéro de session. On repart de l'identifiant de transaction et on
     retrouve la session de checkout, qui a gardé notre `metadata`. */
  if (!jeton && n.session) {
    const trouve = await referenceParTransaction(r, n.session)
    if (JETON_FORME.test(trouve)) jeton = trouve
  }

  const journal = async (agi: string, code = 200) => {
    const { data, error } = await db.rpc('minuit_paiement_journal', {
      p_evenement_id: n.evenementId,
      p_jeton: jeton || null,
      p_session: n.session || null,
      p_montant: n.montant,
      p_devise: n.devise || null,
      p_etat_lu: n.etat,
      p_agi: signe ? agi : agi + ' · NON SIGNÉ',
      p_brut: corps,
    })
    /* ⚠️ Une écriture ratée ne doit pas rendre 200 : ce serait dire « reçu »
       en n'ayant rien gardé. On rend 500, le fournisseur renvoie. */
    if (error) { console.error('saspay journal', error.message); return ok({ ok: false, erreur: 'journal' }, 500) }
    return ok({ ok: true, nouveau: data === true, agi }, code)
  }

  if (!jeton) return journal('sans lettre')

  /* ── ce qu'on attend, puis la décision ───────────────────────────────── */
  const { data: lignes, error } = await db.rpc('minuit_paiement_attendu', { p_jeton: jeton })
  if (error) { console.error('saspay attendu', error.message); return ok({ ok: false }, 500) }
  const b = Array.isArray(lignes) ? lignes[0] : lignes
  const cmd = b?.existe
    ? { existe: true, etat: String(b.etat), total: Number(b.total) || 0 }
    : null

  /* ⛔ Les gardes (devise, montant, déjà payée) vivent dans `_shared/saspay.ts`
     et sont essayées par `node minuit/_qc_caisse.mjs`. Les recopier ici ferait
     deux vérités sur ce qui autorise un encaissement.
     ⚠️ `decider` refuse un état hors « attente / recue » : notre lettre payée
     porte « vivante », donc un renvoi est refusé comme doublon, ce qui est
     exactement ce qu'on veut. */
  const { payer, agi } = decider(n, cmd, r)
  if (!payer) {
    if (agi.startsWith('refus')) console.error('saspay', jeton, agi)
    return journal(agi)
  }

  /* ── agir, PUIS journaliser ──────────────────────────────────────────── */
  /* ⚠️ CET ORDRE EST RÉFLÉCHI. Journaliser d'abord, c'est réserver
     l'identifiant de l'événement : si la mise à jour échouait ensuite, le
     renvoi serait pris pour un doublon et le paiement resterait invisible pour
     toujours. Ouvrir la lettre deux fois écrit la même valeur. */
  /* ⚠️ La durée de vie vient du PALIER lu en base, jamais d'une valeur par
     défaut : les trois paliers payés vivent un an aujourd'hui, et un « 365 »
     écrit ici deviendrait faux en silence le jour où l'un d'eux change. */
  const p = palier(b?.palier)
  if (!p) { console.error('saspay palier inconnu', jeton, b?.palier); return ok({ ok: false, erreur: 'palier' }, 500) }
  const { data: fait, error: eO } = await db.rpc('minuit_ouvrir', {
    p_jeton: jeton, p_jours: p.jours,
  })
  if (eO) { console.error('saspay ouverture', jeton, eO.message); return ok({ ok: false, erreur: 'ouverture' }, 500) }

  /* ⚠️ `false` ici n'est PAS une panne : c'est une lettre RETIRÉE. Le retrait
     passe avant le confort de l'acheteur, remboursement compris (voir
     CONDITIONS.md §3). L'argent est encaissé, la lettre ne s'ouvre pas, et le
     journal le dit. */
  if (fait !== true) {
    console.error('saspay · payée mais retirée', jeton)
    return journal('payee · lettre retirée, non ouverte')
  }

  console.log('minuit · payée et ouverte', jeton, cmd?.total, r.devise)
  return journal('payee · ouverte')
})
