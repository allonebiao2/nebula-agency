import { createClient } from 'jsr:@supabase/supabase-js@2'
import { decider, lireNotification, reglages, verifierSignature } from '../_shared/saspay.ts'

/*
  PISTE · la notification de paiement (webhook SasPay).

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase functions deploy piste-paiement-recu --no-verify-jwt
  ⛔ `--no-verify-jwt` n'est pas une négligence : SasPay n'a pas de jeton
     Supabase à présenter. Ce qui protège cette porte n'est pas un JWT, c'est
     la signature vérifiée ci-dessous.

  ⛔ CE QUI FAIT FOI, C'EST CETTE PORTE, PAS LE RETOUR DU NAVIGATEUR.
     Un client ramené sur « merci » n'a rien prouvé : la page de retour se
     visite à la main. Seule une notification signée déplace l'état d'une
     commande.

  ⚠️ ELLE NE LIVRE RIEN. Elle marque « payée », et c'est tout. Mongazi ouvre le
     cockpit et fabrique le carnet comme avant. Tant que la forme exacte des
     messages SasPay n'est pas confirmée, laisser partir de la marchandise sur
     un message mal compris serait le seul geste vraiment coûteux.
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
     réordonne les clés et change les espaces : la signature ne correspondrait
     plus jamais, et on finirait par « désactiver la vérification pour que ça
     marche ». */
  const brut = await req.text()

  const obligatoire = (Deno.env.get('SASPAY_SIGNATURE_OBLIGATOIRE') ?? '1') !== '0'
  const entete = req.headers.get(r.enteteSig) || req.headers.get('x-signature')
             || req.headers.get('signature') || ''
  const signe = await verifierSignature(brut, entete, r.secretSig)

  if (!signe && obligatoire) {
    /* Rien n'est écrit : sans cette règle, n'importe qui remplirait le journal
       en tapant l'adresse. */
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

  /* ── retrouver la commande ────────────────────────────────────────────── */
  let reference = /^PISTE-[A-Z0-9]{4}$/.test(n.reference.toUpperCase())
    ? n.reference.toUpperCase()
    : ''
  if (!reference && n.session) {
    const { data } = await db.rpc('piste_paiement_par_session', { p_session: n.session })
    const s = Array.isArray(data) ? data[0] : data
    if (s?.reference) reference = String(s.reference)
  }

  const journal = async (agi: string, code = 200) => {
    const { data, error } = await db.rpc('piste_paiement_journal', {
      p_evenement_id: n.evenementId,
      p_reference: reference || null,
      p_session: n.session || null,
      p_montant: n.montant,
      p_devise: n.devise || null,
      p_etat_lu: n.etat,
      p_agi: signe ? agi : agi + ' · NON SIGNÉ',
      p_brut: corps,
    })
    /* ⚠️ Une écriture ratée ne doit pas rendre 200 : ce serait dire « reçu »
       en n'ayant rien gardé. On rend 500, le fournisseur renvoie. */
    if (error) {
      console.error('saspay journal', error.message)
      return ok({ ok: false, erreur: 'journal' }, 500)
    }
    return ok({ ok: true, nouveau: data === true, agi }, code)
  }

  if (!reference) return journal('sans commande')

  /* ── ce qu'on attend, puis la décision ────────────────────────────────── */
  const { data: lignes, error } = await db.rpc('piste_paiement_attendu', { p_reference: reference })
  if (error) { console.error('saspay attendu', error.message); return ok({ ok: false }, 500) }
  const brutCmd = Array.isArray(lignes) ? lignes[0] : lignes
  const cmd = brutCmd?.existe
    ? { existe: true, etat: String(brutCmd.etat), total: Number(brutCmd.total) || 0 }
    : null

  /* ⛔ Les gardes (devise, montant, déjà payée) vivent dans `_shared/saspay.ts`
     et sont essayées par `node piste/_qc_paiement.mjs`. Les recopier ici ferait
     deux vérités sur ce qui autorise un encaissement. */
  const { payer, agi } = decider(n, cmd, r)
  if (!payer) {
    if (agi.startsWith('refus')) console.error('saspay', reference, agi)
    return journal(agi)
  }

  /* ── agir, PUIS journaliser ───────────────────────────────────────────── */
  /*
    ⚠️ CET ORDRE EST RÉFLÉCHI. Journaliser d'abord, c'est réserver
    l'identifiant de l'événement : si la mise à jour échouait ensuite, le
    renvoi du fournisseur serait pris pour un doublon et le paiement resterait
    invisible pour toujours. Poser « payée » deux fois, à l'inverse, ne coûte
    rien : c'est la même valeur écrite deux fois.

    ⚠️ Ce raisonnement tient tant que l'action est INOFFENSIVE À RÉPÉTER. Le
    jour où cette fonction enverra le carnet elle-même, il faudra l'inverser,
    et réserver en deux temps : poser, agir, confirmer.
  */
  const { data: fait, error: eE } = await db.rpc('piste_etat_commande', {
    p_reference: reference, p_etat: 'payee',
  })
  if (eE || fait !== true) {
    console.error('saspay état', reference, eE?.message)
    return ok({ ok: false, erreur: 'état' }, 500)
  }

  console.log('saspay · payée', reference, cmd?.total, r.devise)
  return journal('payee')
})
