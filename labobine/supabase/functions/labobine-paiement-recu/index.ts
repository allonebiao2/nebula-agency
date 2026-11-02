import { createClient } from 'jsr:@supabase/supabase-js@2'
import {
  decider, horodatageFrais, lireNotification, referenceParTransaction, reglages, verifierSignature,
} from '../_shared/saspay.ts'
import { lireOffre, REFERENCE_FORME } from '../_shared/offres.ts'

/*
  LA BOBINE · la notification de paiement (webhook SasPay).
  ⚠️ CE FICHIER EST LA SOURCE.
      cd labobine && npx -y supabase@2 functions deploy labobine-paiement-recu --project-ref xukduhqqfzogisoimhyo --use-api --no-verify-jwt
  ⛔ `--no-verify-jwt` : SasPay n'a pas de jeton Supabase. Ce qui protège cette porte, c'est la signature ET l'âge.
  ⛔ Ce webhook a SON secret (`LABOBINE_SECRET_WEBHOOK`) : SasPay signe chaque point de réception avec le sien.
     Pas de repli sur celui de PISTE ou de MA LETTRE À… : un secret absent refuse, il ne devine pas.
  ⛔ Ce qui fait foi, c'est cette porte, pas le retour du navigateur sur « #merci ».
  ⚠️ Répondre 200 veut dire « reçu, je n'en veux plus » : on ne le fait qu'une fois l'événement écrit au journal.
*/

const ok = (c: unknown, code = 200) =>
  new Response(JSON.stringify(c), { status: code, headers: { 'Content-Type': 'application/json' } })

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return ok({ ok: false, erreur: 'méthode' }, 405)
  const r = { ...reglages(), secretSig: Deno.env.get('LABOBINE_SECRET_WEBHOOK') ?? '' }
  const brut = await req.text() // ⛔ le corps brut, jamais reparsé : la signature porte sur lui
  const entete = req.headers.get(r.enteteSig) || req.headers.get('x-signature') || req.headers.get('signature') || ''
  const horodatage = req.headers.get(r.enteteTs) || req.headers.get('x-timestamp') || ''
  if (!horodatageFrais(horodatage, r.toleranceSig)) {
    console.error('labobine webhook · horodatage refusé', horodatage.slice(0, 24))
    return ok({ ok: false, erreur: 'horodatage' }, 401)
  }
  if (!(await verifierSignature(brut, entete, r.secretSig, horodatage))) {
    console.error('labobine webhook · signature refusée', entete.slice(0, 24))
    return ok({ ok: false, erreur: 'signature' }, 401)
  }

  let corps: unknown = null
  try { corps = JSON.parse(brut) } catch { corps = { _texte: brut } }
  const n = lireNotification(corps)
  const db = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)

  // retrouver la commande : notre référence, sinon la session, sinon la transaction (la notification ne porte
  // parfois ni l'une ni l'autre, mesuré chez PISTE le 2026-09-03)
  let reference = REFERENCE_FORME.test(n.reference) ? n.reference : ''
  if (!reference && n.session) {
    const { data } = await db.rpc('labobine_paiement_par_session', { p_session: n.session })
    const s = Array.isArray(data) ? data[0] : data
    if (s?.reference) reference = String(s.reference)
  }
  if (!reference && n.session) {
    const trouve = await referenceParTransaction(r, n.session)
    if (REFERENCE_FORME.test(trouve)) reference = trouve
  }

  const journal = async (agi: string) => {
    const { data, error } = await db.rpc('labobine_paiement_journal', {
      p_evenement_id: n.evenementId, p_reference: reference || null, p_session: n.session || null,
      p_montant: n.montant, p_devise: n.devise || null, p_etat_lu: n.etat, p_agi: agi, p_brut: corps,
    })
    if (error) { console.error('labobine journal', error.message); return ok({ ok: false, erreur: 'journal' }, 500) }
    return ok({ ok: true, nouveau: data === true, agi })
  }

  if (!reference) return journal('commande introuvable')
  const { data: lue } = await db.rpc('labobine_commande_lire', { p_reference: reference })
  const cmd = Array.isArray(lue) ? lue[0] : lue
  const decision = decider(n, cmd ? { existe: true, etat: String(cmd.etat), total: Number(cmd.total) } : null, r)
  if (!decision.payer) return journal(decision.agi)

  const offre = lireOffre(cmd.offre)
  if (!offre) return journal(`refus · offre ${cmd.offre} inconnue du barème`)
  const { data: paye, error } = await db.rpc('labobine_payer', { p_reference: reference, p_jours: offre.jours, p_credits: offre.credits })
  if (error) { console.error('labobine payer', error.message); return ok({ ok: false, erreur: 'payer' }, 500) }
  return journal(paye ? `payee · ${offre.id}` : 'déjà payée')
})
