import { createClient } from 'jsr:@supabase/supabase-js@2'
import { ouvrirSession, reglages } from '../_shared/saspay.ts'

/*
  PISTE · ouvrir un paiement en ligne pour une commande déjà déposée.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase functions deploy piste-paiement

  POURQUOI ELLE EXISTE
    Le site est un paquet statique servi par Cloudflare Pages. Une clé secrète
    posée dedans se lit dans le JavaScript en trois secondes, et le dépôt est
    PUBLIC. La clé SasPay ne peut donc vivre que côté serveur : ici, en secret
    Supabase (`supabase secrets set SASPAY_CLE_SECRETE=…`).

  ⛔ LE MONTANT NE VIENT JAMAIS DU NAVIGATEUR. Il est relu en base, sur la
    commande, à partir de la seule chose que le client envoie : sa référence.
    Si le navigateur pouvait annoncer le montant, on paierait 100 F pour
    10 000 F de fiches, et ça ne se verrait qu'au moment de compter la caisse.

  ⚠️ CETTE PORTE EST PUBLIQUE, et c'est voulu : celui qui l'appelle ne peut que
    FABRIQUER UNE FACTURE À PAYER. Elle ne rend ni nom, ni téléphone, ni email,
    ni fiche : juste une adresse de paiement. Le pire qu'un curieux puisse en
    tirer est de payer la commande d'un autre.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

/* On n'ouvre un paiement que pour une commande qui attend encore son argent.
   Rouvrir une commande livrée, c'est encaisser deux fois. */
const OUVRABLE = ['attente', 'recue']

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const repondre = (c: unknown, code = 200) =>
    new Response(JSON.stringify(c), {
      status: code,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })

  let d: any
  try { d = await req.json() } catch { return repondre({ ok: false, erreur: 'corps' }, 400) }

  const reference = String(d?.reference || '').trim().toUpperCase()
  if (!/^PISTE-[A-Z0-9]{4}$/.test(reference)) {
    return repondre({ ok: false, erreur: 'référence' }, 400)
  }

  const r = reglages()
  if (!r.cle) {
    /* Dire « pas encore branché » plutôt que rendre une erreur muette : c'est
       ce message qui apprend à Mongazi que le secret n'est pas posé. */
    return repondre({ ok: false, erreur: 'SasPay n’est pas encore branché ici.' }, 503)
  }

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
  )

  const { data: lignes, error } = await db.rpc('piste_paiement_attendu', { p_reference: reference })
  if (error) return repondre({ ok: false, erreur: error.message }, 500)
  const cmd = Array.isArray(lignes) ? lignes[0] : lignes
  if (!cmd?.existe) return repondre({ ok: false, erreur: 'commande inconnue' }, 404)

  const total = Number(cmd.total) || 0
  if (total <= 0) return repondre({ ok: false, erreur: 'montant nul' }, 409)
  if (!OUVRABLE.includes(String(cmd.etat))) {
    return repondre({ ok: false, erreur: 'commande déjà traitée', etat: cmd.etat }, 409)
  }

  const s = await ouvrirSession(r, {
    reference,
    montant: total,
    description: `PISTE · commande ${reference}`,
  })
  if (!s.ok) {
    console.error('saspay session', reference, s.erreur)
    return repondre({ ok: false, erreur: s.erreur }, 502)
  }

  /* On garde le lien AVANT de le rendre. La notification qui arrivera ne
     portera peut-être que l'identifiant de session : sans ce répertoire, un
     paiement bien réel serait impossible à rattacher à une commande. */
  const { error: eS } = await db.rpc('piste_paiement_session', {
    p_session: s.session,
    p_reference: reference,
    p_montant: total,
    p_devise: r.devise,
    p_url: s.url,
  })
  if (eS) console.error('saspay session non enregistrée', reference, eS.message)

  return repondre({ ok: true, url: s.url })
})
