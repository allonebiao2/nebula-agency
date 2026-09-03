import { createClient } from 'jsr:@supabase/supabase-js@2'

/*
  PISTE · fabriquer et envoyer un carnet, tout seul.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit dans le
  dépôt : piste/supabase/functions/piste-livrer/index.ts

  CE QU'ELLE FAIT, DANS L'ORDRE
    1. lit la commande payée
    2. choisit les fiches libres, en alternant entre les métiers demandés
    3. compose le message d'approche pour chacune
    4. pose le carnet et réserve les fiches 90 jours
    5. envoie le lien au client ET à Mongazi

  ⚠️ « NUMÉRO VÉRIFIÉ » N'EST PLUS UN APPEL TÉLÉPHONIQUE (2026-08-04).
  L'option promettait « chaque numéro est composé avant l'envoi ». Seul le
  pouce de Mongazi pouvait tenir ça, un numéro à la fois : dix commandes de
  cinquante fiches font cinq cents appels. Ses mots : « je ne me vois pas
  lancer les appels moi-même ».
  Quand l'option est payée, on demande donc au serveur des fiches VÉRIFIÉES :
  numéro dans une tranche réellement attribuée par le régulateur, fiche revue
  à sa source depuis moins de deux mois, jamais signalée injoignable.
  ⚠️ Aucune de ces trois vérifications ne prouve qu'on décrochera, et l'e-mail
  ne doit JAMAIS le laisser croire.

  ⚠️ UN MOT DE PASSE EST EXIGÉ, et les essais sont comptés : au-delà de 10
  échecs en 15 minutes, tout est refusé pendant 15 minutes.

  ⚠️ ELLE REFUSE DE RELIVRER. Une référence déjà livrée rend son lien existant
  au lieu d'en créer un second.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

const SITE = 'https://piste.nebula-agency.online'

const fcfa = (v: number) =>
  String(Math.round(v || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' F'

const SINGULIER: Record<string, string> = {
  couture: 'atelier de couture', restaurant: 'restaurant', patisserie: 'pâtisserie',
  beaute: 'salon de beauté', alimentation: "commerce d'alimentation",
  quincaillerie: 'quincaillerie', auto: 'garage', maison: 'magasin de décoration',
  sante: 'cabinet', ecole: 'établissement', informatique: 'commerce informatique',
  imprimerie: 'imprimerie', hotel: 'hôtel', immobilier: 'agence immobilière',
  transport: 'société de transport', services: 'société de services',
  artisan: 'artisan', commerce: 'commerce',
}

function messagePour(f: any, offre: string) {
  const lieu = [f.quartier, f.localite].filter(Boolean).join(', ')
  const p = (offre || '').trim().replace(/[.\s]+$/, '')
  return [
    'Bonjour,',
    `Je vous écris au sujet de ${f.nom}, votre ${SINGULIER[f.metier] || 'commerce'} à ${lieu}.`,
    p ? `${p.charAt(0).toUpperCase()}${p.slice(1)}.`
      : 'Je vous écris au sujet de ce que je propose aux commerces comme le vôtre.',
    'Est-ce que je peux vous en dire deux mots ? Ça prend deux minutes.',
  ].join('\n\n')
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

  const ref = String(d?.reference || '').trim()
  const motdepasse = String(d?.motdepasse || '')
  if (!ref) return repondre({ ok: false, erreur: 'reference' }, 400)

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  /* ══ LA PORTE INTERNE ══════════════════════════════════════════════════════
     Quand un paiement en ligne est confirmé, `piste-paiement-recu` livre le
     carnet tout seul, à trois heures du matin s'il le faut. Il passe par ICI,
     et non par une copie du code : la sélection des fiches, la pose du carnet
     et les courriels sont écrits une fois, à un seul endroit.

     ⛔ ELLE NE DESSERRE QUE DEUX CHOSES, et pour de vraies raisons :
       · le mot de passe du cockpit — un serveur n'en a pas, il présente un
         secret que seul lui connaît ;
       · le verrou anti-force-brute — il protège le cockpit de Mongazi. Le
         laisser bloquer une livraison, c'est qu'un inconnu tapant des mots de
         passe au hasard empêcherait un client qui a PAYÉ de recevoir sa
         marchandise.
     ⚠️ Tout le reste est rigoureusement identique : commande introuvable,
     commande déjà livrée, fiches insuffisantes. Une porte interne n'est pas
     une porte dérobée. */
  const jetonInterne = String(d?.interne || '')
  const attendu = Deno.env.get('PISTE_JETON_INTERNE') || ''
  const interne = attendu.length >= 16 && jetonInterne === attendu

  /* ⚠️ LES RÉGLAGES SE LISENT DANS TOUS LES CAS. Ils ne portent pas que le mot
     de passe : la clé d'envoi des courriels et les adresses sont dedans, et
     c'est tout en bas qu'on s'en sert. Les enfermer dans le contrôle du mot de
     passe, c'était une livraison automatique qui pose le carnet et n'envoie
     rien à personne. */
  const { data: reglages } = await db.rpc('piste_reglages')
  const r: Record<string, string> = {}
  for (const x of reglages || []) r[x.cle] = x.valeur

  if (!interne) {
    const { data: verrouille } = await db.rpc('piste_verrouille')
    if (verrouille === true) {
      return repondre({
        ok: false,
        erreur: 'Trop d’essais. Le cockpit est bloqué 15 minutes, puis il rouvre tout seul.',
        verrouille: true,
      }, 429)
    }

    if (!r['motdepasse_cockpit'] || motdepasse !== r['motdepasse_cockpit']) {
      await db.rpc('piste_tentative', { p_reussi: false })
      return repondre({ ok: false, erreur: 'mot de passe' }, 401)
    }
    await db.rpc('piste_tentative', { p_reussi: true })
  }

  /* 1. la commande */
  const { data: lignes } = await db.rpc('piste_commande', { p_reference: ref })
  const cde = Array.isArray(lignes) ? lignes[0] : lignes
  if (!cde) return repondre({ ok: false, erreur: 'commande introuvable' }, 404)
  if (cde.jeton) {
    return repondre({ ok: true, deja: true, lien: `${SITE}/#/carnet/${cde.jeton}` })
  }

  const cmd = cde.commande || {}
  const client = cde.client || {}
  const metiers: string[] = cmd.metiers?.length ? cmd.metiers : [cmd.metier].filter(Boolean)
  const n = Number(cmd.n || 0)
  if (!metiers.length || !cmd.ville || n < 1) {
    return repondre({ ok: false, erreur: 'commande incomplète' }, 400)
  }

  /* 2. les fiches libres.
     Si le client a payé « numéro vérifié », on n'accepte QUE des fiches
     vérifiées : mieux vaut refuser la commande que livrer une promesse creuse. */
  const options: string[] = cmd.options || []
  const exigeVerifiees = options.includes('teste')

  const { data: brutes, error: eF } = await db.rpc('piste_fiches_libres', {
    p_metiers: metiers, p_ville: cmd.ville, p_n: n, p_verifiees: exigeVerifiees,
  })
  if (eF) return repondre({ ok: false, erreur: eF.message }, 500)
  const fiches: any[] = brutes || []
  if (fiches.length < n) {
    return repondre({
      ok: false,
      erreur: exigeVerifiees
        ? `seulement ${fiches.length} fiches VÉRIFIÉES libres sur ${n} demandées`
        : `seulement ${fiches.length} fiches libres sur ${n} demandées`,
      libres: fiches.length,
      verifiees: exigeVerifiees,
    }, 409)
  }

  /* 3. le message, quand il est payé */
  for (const f of fiches) {
    if (options.includes('message') && !f.fixe) f.message = messagePour(f, cmd.offre || '')
    if (options.includes('sansSite')) f.sansSite = true
    if (exigeVerifiees) f.verifie = true
  }

  /* 4. poser le carnet */
  const jeton = [...crypto.getRandomValues(new Uint8Array(24))]
    .map((b) => 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'[b % 62])
    .join('')

  const { data: pose } = await db.rpc('piste_poser_carnet', {
    p_jeton: jeton, p_reference: ref, p_client: client, p_commande: cmd, p_fiches: fiches,
  })
  if (pose !== true) return repondre({ ok: false, erreur: 'déjà livrée' }, 409)

  const lien = `${SITE}/#/carnet/${jeton}`
  const fixes = fiches.filter((f) => f.fixe).length

  /* 5. les courriels */
  let courriels = 0
  const envoyer = async (a: string, sujet: string, texte: string) => {
    if (!r['resend_key'] || !a || !a.includes('@')) return
    const rep = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${r['resend_key']}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: r['email_expediteur'] || 'PISTE <piste@nebula-agency.online>',
        to: [a], subject: sujet, text: texte,
      }),
    })
    if (rep.ok) courriels++
  }

  try {
    await envoyer(client.email, `Votre carnet PISTE est prêt · ${ref}`, [
      `Bonjour ${client.prenom || ''},`.trim(), '',
      `Votre carnet est prêt : ${n} fiches${cmd.metierNom ? ' · ' + cmd.metierNom : ''}${cmd.villeNom ? ' · ' + cmd.villeNom : ''}.`,
      '', 'Il s’ouvre ici, et ce lien est à vous :', lien, '',
      'COMMENT S’EN SERVIR, EN TROIS LIGNES',
      '  1. Ouvrez le lien sur votre téléphone.',
      '  2. Appuyez sur « Écrire sur WhatsApp » : la conversation s’ouvre, le',
      '     message est déjà dedans.',
      fixes ? `     ${fixes} de ces numéros sont des lignes fixes : on les appelle.` : '',
      '  3. Ouvrez la fiche et dites ce qui s’est passé : j’ai écrit, il veut me',
      '     voir, j’ai vendu, ou pas intéressé. Votre avancement se garde, même',
      '     si vous fermez.', '',
      exigeVerifiees
        ? 'VOS FICHES SONT VÉRIFIÉES : chaque numéro appartient à une tranche\nréellement attribuée par le régulateur, la fiche a été revue à sa source\nrécemment, et aucun client ne l’a signalée injoignable.'
        : '',
      'Un numéro ne répond plus ? Appuyez sur « Ce numéro ne répond plus ? » dans',
      'le carnet : la fiche est remplacée sans frais, et la remplaçante apparaît',
      'dans ce même lien.', '',
      'Ces fiches sont à vous seul pendant 90 jours.',
      'Ce lien vous arrive par email ET sur votre WhatsApp. Il ne périme pas.',
      '', 'NEBULA Agency · Cotonou',
    ].filter(Boolean).join('\n'))

    await envoyer(r['email_admin'] || '', `PISTE LIVRÉ · ${n} fiches · ${ref}`, [
      `Carnet ${ref} livré à ${[client.prenom, client.nom].filter(Boolean).join(' ') || 'un client'}.`,
      '',
      `Commande   ${n} fiches · ${cmd.metierNom || metiers.join(', ')} · ${cmd.villeNom || cmd.ville}`,
      `Encaissé   ${fcfa(cmd.total)}`,
      `Client     ${client.email || 'pas d email'} · +${client.whatsapp || client.tel || '?'}`,
      `Dont fixes ${fixes}`,
      '', 'Le lien du carnet :', lien, '',
      exigeVerifiees
        ? '✅ « NUMÉRO VÉRIFIÉ » EST PAYÉ, ET LE SERVEUR L’A DÉJÀ FAIT.\n   Seules des fiches vérifiées sont parties : tranche attribuée, revue\n   récemment, jamais signalée injoignable. VOUS N’AVEZ AUCUN APPEL À PASSER.'
        : '',
      '', 'Ces fiches sont réservées à ce client pendant 90 jours.',
      'Dans une semaine : python piste/_carnet.py --relances',
    ].filter(Boolean).join('\n'))
  } catch { /* un courriel raté ne défait pas un carnet déjà posé */ }

  return repondre({ ok: true, lien, fiches: fiches.length, fixes, verifiees: exigeVerifiees, courriels })
})
