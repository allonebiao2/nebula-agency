import { createClient } from 'jsr:@supabase/supabase-js@2'

/*
  PISTE · un client signale une fiche injoignable.

  POURQUOI ÇA MÉRITE UN COURRIEL
  Le signalement n'est pas une réclamation à subir, c'est le seul moment où un
  client vous dit que la donnée vieillit. Le voir tout de suite permet deux
  choses : remplacer la fiche avant qu'il se plaigne, et savoir QUELLE source
  se gâte. Sans courriel, ça dort dans une table que personne ne regarde.

  ⚠️ Comme partout ici, un courriel raté ne fait jamais échouer le
  signalement : la marque est posée d'abord, l'alerte part ensuite.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const repondre = (c: unknown, code = 200) =>
    new Response(JSON.stringify(c), {
      status: code,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })

  let d: any
  try {
    d = await req.json()
  } catch {
    return repondre({ ok: false }, 400)
  }

  const jeton = String(d?.jeton || '').trim()
  const fiche = String(d?.fiche || '').trim()
  if (jeton.length < 8 || !fiche) return repondre({ ok: false }, 400)

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  /* 1. la marque d'abord, elle passe avant l'alerte */
  let posee = false
  try {
    const { data } = await db.rpc('piste_marquer', {
      p_jeton: jeton,
      p_fiche: fiche,
      p_marque: 'injoignable',
    })
    posee = data === true
  } catch {
    posee = false
  }

  /* 2. l'alerte ensuite */
  let alerte = false
  try {
    const { data: reglages } = await db.rpc('piste_reglages')
    const r: Record<string, string> = {}
    for (const x of reglages || []) r[x.cle] = x.valeur
    const { data: carnet } = await db.rpc('piste_carnet', { p_jeton: jeton })
    const k = Array.isArray(carnet) ? carnet[0] : carnet
    const cl = k?.client || {}
    const nom = [cl.prenom, cl.nom].filter(Boolean).join(' ') || 'un client'

    if (r['resend_key'] && r['email_admin']) {
      const rep = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${r['resend_key']}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: r['email_expediteur'] || 'PISTE <piste@nebula-agency.online>',
          to: [r['email_admin']],
          subject: `PISTE INJOIGNABLE · ${fiche} · ${k?.reference || jeton.slice(0, 8)}`,
          text: [
            `${nom} signale une fiche injoignable.`,
            '',
            `Carnet   ${k?.reference || '?'}`,
            `Fiche    ${fiche}`,
            `Client   ${cl.email || 'pas d email'} · +${cl.tel || cl.whatsapp || '?'}`,
            '',
            'Elle est remplacée sans frais : c’est ce qui a été promis.',
            'Refaites un carnet complémentaire, ou envoyez-lui une fiche de rechange.',
            '',
            'Chaque signalement vous dit AUSSI quelle source vieillit mal.',
          ].join('\n'),
        }),
      })
      alerte = rep.ok
    }
  } catch {
    /* une alerte ratée ne fait pas échouer un signalement */
  }

  return repondre({ ok: true, posee, alerte })
})
