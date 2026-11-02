import { createClient } from 'jsr:@supabase/supabase-js@2'
import { ouvrirSession, reglages } from '../_shared/saspay.ts'
import { lireOffre, nouvelleReference } from '../_shared/offres.ts'

/*
  LA BOBINE · ouvrir le paiement d'un abonnement Pro.
  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      cd labobine && npx -y supabase@2 functions deploy labobine-commande --project-ref xukduhqqfzogisoimhyo --use-api
  ⛔ Il faut être connecté : la commande est rattachée au compte qui paie, lu dans le jeton, jamais dans le corps.
  ⛔ Le prix est lu dans `_shared/offres.ts`, jamais envoyé par le navigateur.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}
const SITE = Deno.env.get('LABOBINE_SITE') || 'https://labobine.pages.dev'

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })
  const repondre = (c: unknown, code = 200) =>
    new Response(JSON.stringify(c), { status: code, headers: { ...CORS, 'Content-Type': 'application/json' } })
  if (req.method !== 'POST') return repondre({ ok: false, erreur: 'méthode' }, 405)

  const db = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)
  const jeton = (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '')
  const { data: qui, error: errQui } = await db.auth.getUser(jeton)
  if (errQui || !qui?.user) return repondre({ ok: false, erreur: 'connexion requise' }, 401)

  let d: any
  try { d = await req.json() } catch { return repondre({ ok: false, erreur: 'corps' }, 400) }
  const offre = lireOffre(d?.offre)
  if (!offre) return repondre({ ok: false, erreur: 'offre inconnue' }, 400)

  const reference = nouvelleReference()
  const { error } = await db.rpc('labobine_commande_creer', {
    p_utilisateur: qui.user.id, p_reference: reference, p_offre: offre.id, p_total: offre.total,
  })
  if (error) { console.error('labobine commande', error.message); return repondre({ ok: false, erreur: 'commande' }, 500) }

  const r = reglages()
  if (!r.cle) return repondre({ ok: false, erreur: 'Le paiement n’est pas encore branché.' }, 503)
  /* ⛔ Le retour et le nom sont propres à LA BOBINE : par défaut, `saspay.ts` (copie exacte de celui de PISTE)
     ramènerait le client chez PISTE et écrirait « Client PISTE » sur son reçu. */
  const s = await ouvrirSession({
    ...r,
    retour: `${SITE}/#merci`,
    annule: `${SITE}/#paiement-annule`,
    nomDefaut: 'Client LA BOBINE',
  }, {
    reference,
    montant: offre.total,
    description: offre.nom,
    client: { email: qui.user.email || undefined },
  })
  if (!s.ok) { console.error('labobine session', s.erreur); return repondre({ ok: false, erreur: 'Le paiement n’a pas pu s’ouvrir.' }, 502) }
  await db.rpc('labobine_commande_session', { p_reference: reference, p_session: s.session })
  return repondre({ ok: true, reference, url: s.url })
})
