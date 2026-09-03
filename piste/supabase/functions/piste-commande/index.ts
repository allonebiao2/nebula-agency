import { createClient } from 'jsr:@supabase/supabase-js@2'

/*
  PISTE · une commande arrive.

  CE QUE FAIT CETTE FONCTION, ET POURQUOI ELLE EXISTE
  Le site est statique : il ne peut pas envoyer d'email sans exposer la clé.
  Cette fonction tourne côté serveur, lit la clé DANS LA BASE, et envoie deux
  courriels :

    · à Mongazi   : la commande complète, pour qu'il la voie AUSSI dans sa
                    boîte mail et pas seulement sur son WhatsApp ;
    · au client   : la confirmation, avec ce qu'il doit payer et à qui.

  ⚠️ ELLE NE BLOQUE JAMAIS LA COMMANDE. Si l'email échoue, la commande est
  quand même enregistrée : perdre un courriel est ennuyeux, perdre une commande
  est inacceptable. C'est exactement ce qui est arrivé au site de l'agence le
  4 août, et on ne le refait pas.

  ⚠️ TOUT PASSE PAR DES FONCTIONS DE `public`. PostgREST n'expose que ce
  schéma : lire `piste.commandes` en direct répond 406, silencieusement. La
  première version de cette fonction ne le savait pas et n'écrivait rien.
*/

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

const fcfa = (v: number) =>
  String(Math.round(v || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' F'

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const repondre = (corps: unknown, code = 200) =>
    new Response(JSON.stringify(corps), {
      status: code,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })

  let d: any
  try {
    d = await req.json()
  } catch {
    return repondre({ ok: false, erreur: 'corps illisible' }, 400)
  }

  const ref = String(d?.reference || '').trim()
  const client = d?.client || {}
  const cmd = d?.commande || {}
  if (ref.length < 6 || ref.length > 24) return repondre({ ok: false, erreur: 'reference' }, 400)

  const db = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  /* 1. LA COMMANDE D'ABORD. Elle passe avant tout le reste. */
  let enregistree = false
  let detail = ''
  try {
    const { data, error } = await db.rpc('piste_commander', {
      p_reference: ref,
      p_client: client,
      p_commande: cmd,
    })
    enregistree = data === true && !error
    if (error) detail = error.message
  } catch (e) {
    detail = String(e)
  }

  /* 2. Les courriels ensuite, et leur échec ne remonte pas au client. */
  let courriels = 0
  try {
    const { data: reglages } = await db.rpc('piste_reglages')
    const r: Record<string, string> = {}
    for (const x of reglages || []) r[x.cle] = x.valeur
    const clef = r['resend_key']

    if (clef) {
      const nom = [client.prenom, client.nom].filter(Boolean).join(' ') || 'un acheteur'
      const quoi = `${cmd.n || '?'} fiches${cmd.metierNom ? ' · ' + cmd.metierNom : ''}${
        cmd.villeNom ? ' · ' + cmd.villeNom : ''
      }`
      const total = fcfa(cmd.total)

      const envoyer = async (a: string, sujet: string, texte: string) => {
        const rep = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: { Authorization: `Bearer ${clef}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from: r['email_expediteur'] || 'PISTE <piste@nebula-agency.online>',
            to: [a],
            subject: sujet,
            text: texte,
          }),
        })
        if (rep.ok) courriels++
      }

      /* à Mongazi : le sujet dit tout, sans ouvrir le message */
      if (r['email_admin']) {
        await envoyer(
          r['email_admin'],
          `PISTE COMMANDE · ${cmd.n || '?'} fiches · ${total} · ${ref}`,
          [
            `${nom} vient de commander.`,
            '',
            `Référence   ${ref}`,
            `Commande    ${quoi}`,
            `À payer     ${total}`,
            '',
            'QUI',
            `Nom         ${nom}`,
            `Email       ${client.email || 'non donné'}`,
            `WhatsApp    +${client.whatsapp || client.tel || 'non donné'}`,
            `Paiera de   +229 ${client.momo || 'non donné'}`,
            '',
            cmd.offre ? `CE QU'IL VEND\n${cmd.offre}\n` : '',
            "C'est ce NUMÉRO et ce NOM qui s'afficheront à la réception MTN.",
            '',
            'La commande est déjà en base : elle ne se perdra pas.',
          ].filter(Boolean).join('\n')
        )
      }

      /* au client : ce qu'il doit faire maintenant */
      if (client.email && String(client.email).includes('@')) {
        await envoyer(
          client.email,
          `Votre commande PISTE · ${ref}`,
          [
            `Bonjour ${client.prenom || ''},`.trim(),
            '',
            `Votre commande est enregistrée : ${quoi}.`,
            `Montant à régler : ${total}`,
            `Référence : ${ref}`,
            '',
            'CE QUI SE PASSE MAINTENANT',
            '1. Vous recevez le numéro de dépôt Mobile Money dans la conversation',
            '   WhatsApp. Ce numéro n’est pas celui sur lequel vous nous écrivez.',
            '2. Vous envoyez le montant exact, depuis le numéro que vous avez déclaré.',
            '3. Vous recevez votre carnet sous 24 heures, ici et sur WhatsApp.',
            '',
            'Surveillez votre boîte mail ET votre WhatsApp : le lien de votre carnet',
            'arrive par les deux.',
            '',
            `Une question ? Écrivez-nous au +${r['whatsapp_nebula'] || '22996740732'}.`,
            '',
            'NEBULA Agency · Cotonou',
          ].join('\n')
        )
      }
    }
  } catch {
    /* un courriel raté ne fait pas échouer une commande */
  }

  return repondre({ ok: true, enregistree, courriels, detail })
})
