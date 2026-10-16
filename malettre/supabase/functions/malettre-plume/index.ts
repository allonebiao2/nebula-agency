import Anthropic from 'npm:@anthropic-ai/sdk@0.135.0'
import { createClient } from 'jsr:@supabase/supabase-js@2'
import { LIMITES, empreinte, lireFiche, lireReponse, requete } from '../_shared/plume.ts'

/*
  MA LETTRE À… · la plume. Elle reçoit une fiche, elle rend une lettre.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase secrets set ANTHROPIC_API_KEY=…
      supabase functions deploy malettre-plume

  ⛔ TOUT CE QUI DÉCIDE VIT DANS `_shared/plume.ts` (ce qu'on accepte, ce qu'on
    demande, ce qu'on refuse de rendre), essayé sous Node sans clé ni réseau.
    Ce fichier n'est que la plomberie : la porte, le compteur, l'appel.

  ⛔ LA FICHE N'EST ÉCRITE NULLE PART. Le compteur ne garde qu'une empreinte
    d'adresse et l'identifiant du brouillon, pendant deux jours.

  ⚠️ LA PLUME EST GRATUITE À ESSAYER, PAYANTE À L'ENVOI. L'acheteur doit lire
    SA lettre avant de payer : c'est là que la vente se fait. Les 500 F
    s'ajoutent à la commande (`_shared/lettre.ts`, `PLUME`), pas ici. D'où le
    compteur : trois versions par brouillon, douze par adresse et par jour.
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
  try { d = await req.json() } catch { return repondre({ ok: false, erreur: 'corps' }, 400) }

  const lu = lireFiche(d)
  if (!lu.ok) return repondre({ ok: false, erreur: lu.erreur }, 400)
  const fiche = lu.fiche

  /* ⚠️ « Pas encore branchée » plutôt qu'une erreur muette : c'est ce message
     qui apprend à Mongazi que le secret n'est pas posé, et à l'acheteur qu'il
     peut écrire sa lettre lui-même en attendant. */
  const cle = Deno.env.get('ANTHROPIC_API_KEY')
  if (!cle) return repondre({ ok: false, erreur: 'pas-branchee' }, 503)

  /* ── le compteur ─────────────────────────────────────────────────────── */
  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
  )
  const ip = (req.headers.get('x-forwarded-for') ?? '').split(',')[0].trim() || 'inconnue'
  const { data: version, error: eC } = await db.rpc('malettre_plume_permis', {
    p_ip: await empreinte(ip),
    p_brouillon: fiche.brouillon,
    p_max_ip: LIMITES.ip,
    p_max_brouillon: LIMITES.brouillon,
  })
  /* ⛔ Un compteur en panne ne doit pas ouvrir un robinet gratuit : sans
     compteur, pas de plume. */
  if (eC) { console.error('plume compteur', eC.message); return repondre({ ok: false, erreur: 'compteur' }, 500) }
  if (typeof version !== 'number' || version < 0) return repondre({ ok: false, erreur: 'limite' }, 429)

  /* ── l'appel ─────────────────────────────────────────────────────────── */
  const client = new Anthropic({ apiKey: cle })
  let m: any
  try {
    m = await client.beta.messages.create(requete(fiche) as any)
  } catch (e) {
    /* Les erreurs de l'API (débordement, panne passagère) ne disent rien de
       la lettre : l'acheteur réessaie, sa fiche est gardée chez lui. */
    if (e instanceof Anthropic.RateLimitError) return repondre({ ok: false, erreur: 'occupee' }, 503)
    if (e instanceof Anthropic.APIError) {
      console.error('plume api', e.status, e.message)
      return repondre({ ok: false, erreur: 'occupee' }, 502)
    }
    console.error('plume réseau', String(e))
    return repondre({ ok: false, erreur: 'occupee' }, 502)
  }

  const r = lireReponse(m)
  if (!r.ok) return repondre({ ok: false, refus: r.refus, version }, 200)

  return repondre({
    ok: true, titre: r.titre, lettre: r.lettre, formule: r.formule,
    version, restantes: Math.max(0, LIMITES.brouillon - version),
  })
})
