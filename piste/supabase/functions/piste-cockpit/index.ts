import { createClient } from 'jsr:@supabase/supabase-js@2'

/*
  PISTE · la porte du cockpit : lire les commandes, changer un état, lire le
  tableau de bord.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
  Jusqu'au 2026-08-04 les fonctions de bord n'existaient nulle part dans le
  dépôt : personne ne pouvait les relire, et un incident chez Supabase les
  aurait perdues. Après toute modification :
      supabase functions deploy piste-cockpit
  ou, sans la CLI, redéployer ce même contenu depuis l'éditeur Supabase.

  POURQUOI ELLE EXISTE
    Le cockpit ne lisait que le navigateur de Mongazi. Une commande passée
    depuis le téléphone d'un client existait en base, déclenchait deux
    courriels, et n'apparaissait JAMAIS dans le cockpit tant qu'il ne recollait
    pas le message WhatsApp à la main. Ce n'était pas une liste, c'était un
    carnet personnel. Le jour où cette porte a été ouverte, 24 commandes
    dormaient en base sans avoir jamais été vues.

  ⚠️ DEUX VOCABULAIRES, UN SEUL SENS. La base écrit « attente » à la création,
  le cockpit dit « recue » (à encaisser). Sans traduction ICI, les commandes
  arrivaient dans un onglet qui n'existe pas, donc restaient invisibles.

  ⚠️ LE CODE DU COCKPIT EST EXIGÉ, et les essais sont comptés : au-delà de 10
  échecs en 15 minutes, tout est refusé pendant 15 minutes. Le code est court
  (5 chiffres, choisi par Mongazi pour être tapable sur un téléphone) : ce qui
  protège n'est pas sa longueur, c'est ce compteur.

  ⚠️ ELLE NE REND JAMAIS DE FICHES. Les numéros du vivier sont la marchandise :
  ils ne sortent que par un carnet livré, jamais par une liste de commandes.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

/* base → cockpit */
const ETAT_LU: Record<string, string> = {
  attente: 'recue',
  recue: 'recue',
  payee: 'payee',
  livree: 'livree',
  annulee: 'annulee',
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
    return repondre({ ok: false, erreur: 'corps' }, 400)
  }

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  /* la garde, avant tout le reste */
  const { data: verrouille } = await db.rpc('piste_verrouille')
  if (verrouille === true) {
    return repondre(
      {
        ok: false,
        erreur: 'Trop d’essais. Le cockpit est bloqué 15 minutes, puis il rouvre tout seul.',
        verrouille: true,
      },
      429
    )
  }

  const { data: reglages } = await db.rpc('piste_reglages')
  const r: Record<string, string> = {}
  for (const x of reglages || []) r[x.cle] = x.valeur

  const motdepasse = String(d?.motdepasse || '')
  if (!r['motdepasse_cockpit'] || motdepasse !== r['motdepasse_cockpit']) {
    await db.rpc('piste_tentative', { p_reussi: false })
    return repondre({ ok: false, erreur: 'mot de passe' }, 401)
  }
  await db.rpc('piste_tentative', { p_reussi: true })

  /* ── marquer un état ──────────────────────────────────────────────────── */
  if (d?.action === 'etat') {
    const ref = String(d?.reference || '').trim()
    const etat = String(d?.etat || '').trim()
    if (!ref || !['recue', 'payee', 'livree', 'annulee'].includes(etat)) {
      return repondre({ ok: false, erreur: 'état inconnu' }, 400)
    }
    const { data: fait } = await db.rpc('piste_etat_commande', {
      p_reference: ref,
      p_etat: etat,
    })
    return repondre({ ok: fait === true })
  }

  /* ── le tableau de bord ───────────────────────────────────────────────── */
  if (d?.action === 'tableau') {
    const { data: t, error: eT } = await db.rpc('piste_tableau', {
      p_jours: Number(d?.jours) || 30,
    })
    if (eT) return repondre({ ok: false, erreur: eT.message }, 500)
    return repondre({ ok: true, tableau: t })
  }

  /* ── lister les commandes ─────────────────────────────────────────────── */
  const { data: lignes, error } = await db.rpc('piste_commandes_recentes', {
    p_jours: Number(d?.jours) || 60,
  })
  if (error) return repondre({ ok: false, erreur: error.message }, 500)

  /*
    On rend la forme que le cockpit manipule déjà. Traduire ici plutôt que dans
    le site évite d'avoir deux vérités sur ce qu'est une commande.
  */
  const commandes = (lignes || []).map((x: any) => {
    const cl = x.client || {}
    const cm = x.commande || {}
    return {
      ref: x.reference,
      date: x.cree_le,
      metier: cm.metier || (cm.metiers || [])[0] || '',
      metiers: cm.metiers || [],
      ville: cm.ville || '',
      quartier: cm.quartier || '',
      n: Number(cm.n) || 0,
      options: Array.isArray(cm.options) ? cm.options : [],
      offre: cm.offre || '',
      prenom: cl.prenom || '',
      nom: cl.nom || '',
      email: cl.email || '',
      wa: cl.whatsapp || cl.wa || '',
      momoNumero: cl.momo || '',
      momoOperateur: cl.operateur || '',
      unitaire: Number(cm.unitaire) || 0,
      total: Number(cm.total) || 0,
      etat: ETAT_LU[x.etat] || 'recue',
      lienCarnet: x.jeton ? `https://piste.nebula-agency.online/#/carnet/${x.jeton}` : undefined,
      duServeur: true,
    }
  })

  return repondre({ ok: true, commandes })
})
