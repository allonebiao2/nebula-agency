import { createClient } from 'jsr:@supabase/supabase-js@2'
import { ouvrirSession, reglages } from '../_shared/saspay.ts'
import { expireLe, jeton, lireCommande } from '../_shared/lettre.ts'

/*
  MINUIT · déposer une lettre, et ouvrir son paiement.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase functions deploy minuit-commande

  DEUX CHEMINS, UN SEUL DÉPÔT
    Palier offert → la lettre est vivante tout de suite, on rend son adresse.
    Palier payé   → la lettre attend, on rend une adresse de paiement.
    ⛔ Le palier gratuit ne passe pas par la caisse : c'est la décision du
      2026-09-06, et elle vaut ici comme dans le constructeur.

  ⛔ LE PRIX NE VIENT JAMAIS DU NAVIGATEUR. Il est lu dans le barème de
    `_shared/lettre.ts`, à partir du seul identifiant de palier que le client
    envoie. Si le navigateur pouvait annoncer le montant, on paierait 0 F pour
    un Coffret, et ça ne se verrait qu'en comptant la caisse.

  ⛔ ON NE STOCKE JAMAIS SON HTML. On stocke ses données. Une porte publique
    qui accepte du HTML et le sert sur notre domaine est un hébergeur de pages
    arbitraires : gratuit, anonyme, et parfait pour imiter une banque.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

const SITE = Deno.env.get('MINUIT_SITE') || 'https://minuit.nebula-agency.online'

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const repondre = (c: unknown, code = 200) =>
    new Response(JSON.stringify(c), {
      status: code,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })

  let d: any
  try { d = await req.json() } catch { return repondre({ ok: false, erreur: 'corps' }, 400) }

  const lu = lireCommande(d)
  if (!lu.ok) return repondre({ ok: false, erreur: lu.erreur }, 400)
  const { lettre, palier } = lu

  /* Le WhatsApp de l'ACHETEUR : c'est là qu'on lui rend SON lien. On ne
     demande jamais celui de la destinataire, on ne lui écrit pas. */
  const whatsapp = String(d?.whatsapp ?? '').replace(/[^\d+]/g, '').slice(0, 20)
  if (whatsapp.replace(/\D/g, '').length < 8) {
    return repondre({ ok: false, erreur: 'WhatsApp' }, 400)
  }

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
  )

  const j = jeton()
  const offert = palier.prix === 0

  const { error } = await db.rpc('minuit_deposer', {
    p_jeton: j,
    p_palier: palier.id,
    p_prix: palier.prix,
    p_donnees: lettre,
    p_whatsapp: whatsapp,
    /* Offerte : vivante immédiatement. Payée : elle attend son argent. */
    p_etat: offert ? 'vivante' : 'attente',
    p_expire: offert ? expireLe(palier) : null,
  })
  if (error) { console.error('minuit dépôt', error.message); return repondre({ ok: false, erreur: 'dépôt' }, 500) }

  const adresse = `${SITE}/l/${j}`
  if (offert) return repondre({ ok: true, offert: true, adresse })

  /* ── le paiement ─────────────────────────────────────────────────────── */
  const r = reglages()
  if (!r.cle) {
    /* ⚠️ La lettre est DÉPOSÉE, elle n'est pas perdue. Dire « pas encore
       branché » plutôt que rendre une erreur muette : c'est ce message qui
       apprend à Mongazi que le secret n'est pas posé. */
    return repondre({
      ok: false, depose: true, jeton: j,
      erreur: 'SasPay n’est pas encore branché ici.',
    }, 503)
  }

  /* ⛔ L'ADRESSE DE RETOUR EST PROPRE A CETTE COMMANDE, et il faut la poser :
     le reglage par defaut de `_shared/saspay.ts` ramene chez PISTE, parce que
     ce fichier est LA COPIE EXACTE du sien. Sans cette ligne, un acheteur de
     lettre qui vient de payer tomberait sur la page d'un autre produit.
     ⚠️ Le nom par defaut aussi : « Client PISTE » finirait sur un recu MINUIT. */
  const s = await ouvrirSession({
    ...r,
    retour: `${SITE}/merci.html?j=${j}`,
    nomDefaut: 'Client MINUIT',
  }, {
    reference: j,
    montant: palier.prix,
    description: `MINUIT · ${palier.nom}`,
  })
  if (!s.ok) {
    console.error('saspay session', j, s.erreur)
    return repondre({ ok: false, depose: true, jeton: j, erreur: s.erreur }, 502)
  }

  /* On garde le lien AVANT de le rendre : la notification qui arrivera ne
     portera peut-être que l'identifiant de session. Sans ce répertoire, un
     paiement bien réel serait impossible à rattacher à une lettre. */
  const { error: eS } = await db.rpc('minuit_paiement_session', {
    p_session: s.session, p_jeton: j, p_montant: palier.prix,
    p_devise: r.devise, p_url: s.url,
  })
  if (eS) console.error('saspay session non enregistrée', j, eS.message)

  /* ⛔ LA SOMME ET LE NOM DE L'OFFRE VIENNENT D'ICI, pas du navigateur : la
     page de paiement les AFFICHE, elle ne les calcule pas. Un prix recalcule
     dans le navigateur est un prix qu'on peut reecrire dans la console. */
  return repondre({
    ok: true, offert: false, jeton: j, adresse, paiement: s.url,
    palier: palier.nom, prix: palier.prix,
  })
})
